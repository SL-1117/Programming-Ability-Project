```c
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#include "NUC100Series.h"
#include "GPIO.h"
#include "SYS.h"
#include "Seven_Segment.h"

/* =====================================================
   1. Seven-segment definitions

   Active-low:
   0 = ON
   1 = OFF

   Hardware mapping:
   PE0 = C, PE1 = DP, PE2 = F, PE3 = A
   PE4 = B, PE5 = D, PE6 = E, PE7 = G
   ===================================================== */

#define S_C  (1U << 0)
#define S_DP (1U << 1)
#define S_F  (1U << 2)
#define S_A  (1U << 3)
#define S_B  (1U << 4)
#define S_D  (1U << 5)
#define S_E  (1U << 6)
#define S_G  (1U << 7)

/* Numbers: 0xFF & ~segment mask */

#define N_0 (0xFF & ~(S_A | S_B | S_C | S_D | S_E | S_F))
#define N_1 (0xFF & ~(S_B | S_C))
#define N_2 (0xFF & ~(S_A | S_B | S_D | S_E | S_G))
#define N_3 (0xFF & ~(S_A | S_B | S_C | S_D | S_G))
#define N_4 (0xFF & ~(S_B | S_C | S_F | S_G))
#define N_5 (0xFF & ~(S_A | S_C | S_D | S_F | S_G))
#define N_6 (0xFF & ~(S_A | S_C | S_D | S_E | S_F | S_G))
#define N_7 (0xFF & ~(S_A | S_B | S_C))
#define N_8 (0xFF & ~(S_A | S_B | S_C | S_D | S_E | S_F | S_G))
#define N_9 (0xFF & ~(S_A | S_B | S_C | S_D | S_F | S_G))

static const uint8_t digitPattern[10] = {
    N_0, N_1, N_2, N_3, N_4,
    N_5, N_6, N_7, N_8, N_9
};

/* =====================================================
   2. Global state
   ===================================================== */

volatile uint8_t locked = 0;

/* Current displayed number: 00 to 99 */
static uint8_t number = 0;

/* 0 = stopped, 1 = count up, -1 = count down */
static int8_t countMode = 0;

/* Key 3 alternates: zero, then random */
static uint8_t key3RandomNext = 0;

/* Display blink state */
static uint8_t displayVisible = 1;

/* Millisecond counters */
static uint16_t countTimer = 0;
static uint16_t blinkTimer = 0;
static uint16_t randomSeed = 0;

/* Key release detection */
static uint8_t previousKey = 0;

/* =====================================================
   3. Seven-segment display
   ===================================================== */

static void ShowCustomDigit(uint8_t position, uint8_t pattern)
{
    CloseSevenSegment();

    PE->DOUT = pattern;

    switch (position) {
        case 0: PC4 = 1; break;
        case 1: PC5 = 1; break;
        case 2: PC6 = 1; break;
        case 3: PC7 = 1; break;
        default: break;
    }
}

/*
   Display the two-digit number in the leftmost
   two positions. The remaining two positions stay off.
*/
static void RefreshDisplay(void)
{
    uint8_t tens;
    uint8_t ones;

    tens = number / 10;
    ones = number % 10;

    if (locked && !displayVisible) {
        CloseSevenSegment();
        return;
    }

    /* Leftmost digit: tens */
    ShowCustomDigit(1, digitPattern[tens]);
    CLK_SysTickDelay(1000);

    /* Second digit: ones */
    ShowCustomDigit(0, digitPattern[ones]);
    CLK_SysTickDelay(1000);

    /* Keep the other two positions off */
    CloseSevenSegment();
}

/* =====================================================
   4. Direct GPIO keypad scanning

   Based on the supplied Scankey.c wiring.
   Does not call OpenKeyPad() or ScanKey().
   ===================================================== */

static void InitKeypadGPIO(void)
{
    GPIO_SetMode(PA, BIT0, GPIO_PMD_QUASI);
    GPIO_SetMode(PA, BIT1, GPIO_PMD_QUASI);
    GPIO_SetMode(PA, BIT2, GPIO_PMD_QUASI);
    GPIO_SetMode(PA, BIT3, GPIO_PMD_QUASI);
    GPIO_SetMode(PA, BIT4, GPIO_PMD_QUASI);
    GPIO_SetMode(PA, BIT5, GPIO_PMD_QUASI);

    PA0 = 1;
    PA1 = 1;
    PA2 = 1;
    PA3 = 1;
    PA4 = 1;
    PA5 = 1;
}

/*
   Return key number 1-9, or 0 if no key is pressed.
*/
static uint8_t ReadKeypadGPIO(void)
{
    uint8_t key = 0;

    /* Column 1 */
    PA0 = 1;
    PA1 = 1;
    PA2 = 0;

    if (PA3 == 0) key = 1;
    else if (PA4 == 0) key = 4;
    else if (PA5 == 0) key = 7;

    if (key != 0) goto done;

    /* Column 2 */
    PA0 = 1;
    PA1 = 0;
    PA2 = 1;

    if (PA3 == 0) key = 2;
    else if (PA4 == 0) key = 5;
    else if (PA5 == 0) key = 8;

    if (key != 0) goto done;

    /* Column 3 */
    PA0 = 0;
    PA1 = 1;
    PA2 = 1;

    if (PA3 == 0) key = 3;
    else if (PA4 == 0) key = 6;
    else if (PA5 == 0) key = 9;

done:
    PA0 = 1;
    PA1 = 1;
    PA2 = 1;

    return key;
}

/* =====================================================
   5. Key actions
   ===================================================== */

static void ProcessKey(uint8_t key)
{
    if (locked)
        return;

    switch (key) {
        case 1:
            /* Start continuous counting up */
            countMode = 1;
            countTimer = 0;
            break;

        case 2:
            /* Start continuous counting down */
            countMode = -1;
            countTimer = 0;
            break;

        case 3:
            /* First press: 00; next press: random number */
            countMode = 0;
            countTimer = 0;

            if (key3RandomNext == 0) {
                number = 0;
                key3RandomNext = 1;
            } else {
                number = (uint8_t)(rand() % 100);
                key3RandomNext = 0;
            }
            break;

        default:
            break;
    }
}

/* =====================================================
   6. INT1 interrupt

   Assumption: INT1 is connected to PB.15.
   Confirm this against your board and course example.
   ===================================================== */

void EINT1_IRQHandler(void)
{
    if (GPIO_GET_INT_FLAG(PB, BIT15)) {
        GPIO_CLR_INT_FLAG(PB, BIT15);
        locked = !locked;
    }
}

static void InitINT1(void)
{
    GPIO_SetMode(PB, BIT15, GPIO_PMD_INPUT);

    GPIO_EnableInt(PB, 15, GPIO_INT_FALLING);
    NVIC_EnableIRQ(EINT1_IRQn);
}

/* =====================================================
   7. Main
   ===================================================== */

int main(void)
{
    uint8_t key;
    uint8_t keyReleased;

    SYS_Init();

    OpenSevenSegment();
    CloseSevenSegment();

    InitKeypadGPIO();
    InitINT1();

    /* Random initial number */
    srand(1234);
    number = (uint8_t)(rand() % 100);

    while (1) {

        /*
           Refresh both digits continuously.
           Each digit is displayed for approximately 1 ms.
        */
        RefreshDisplay();

        /*
           Approximately 2 ms elapsed per display refresh.
           The timers below are software timing estimates.
        */
        randomSeed++;
        countTimer += 2;
        blinkTimer += 2;

        /* Auto count every 250 ms */
        if (!locked && countMode != 0 && countTimer >= 250) {
            countTimer = 0;

            if (countMode > 0) {
                number = (number + 1) % 100;
            } else {
                if (number == 0)
                    number = 99;
                else
                    number--;
            }
        }

        /* Toggle display visibility every 500 ms when locked */
        if (locked && blinkTimer >= 500) {
            blinkTimer = 0;
            displayVisible = !displayVisible;
        }

        if (!locked) {
            key = ReadKeypadGPIO();

            /*
               Execute once when a key is released.
               Ignore repeated scans while it remains pressed.
            */
            keyReleased = (previousKey != 0 && key == 0);

            if (keyReleased) {
                ProcessKey(previousKey);
            }

            previousKey = key;
        } else {
            /*
               Clear the key state while locked, so a key
               held during locking cannot trigger afterward.
            */
            previousKey = 0;
        }

        /* Change seed over time for subsequent random values */
        srand(randomSeed + 1234);
    }
}