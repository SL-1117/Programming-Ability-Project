```c
#include <stdio.h>
#include <stdlib.h>
#include "NUC100Series.h"
#include "MCU_init.h"
#include "SYS_init.h"
#include "Seven_Segment.h"
#include "Scankey.h"


/* Segment -> PE bit (G E D B A F DOT C = PE7 ... PE0) */
#define S_A    BIT3
#define S_B    BIT4
#define S_C    BIT0
#define S_D    BIT5
#define S_E    BIT6
#define S_F    BIT2
#define S_G    BIT7
#define S_DOT  BIT1

/* Segments are active low, so invert the "ON" segments */
#define SEG(x)  ((uint8_t)(~(x)))

#define CH_1   SEG(S_B | S_C)
#define CH_2   SEG(S_A | S_B | S_D | S_E | S_G)
#define CH_3   SEG(S_A | S_B | S_C | S_D | S_G)
#define CH_4   SEG(S_B | S_C | S_F | S_G)
#define CH_5   SEG(S_A | S_C | S_D | S_F | S_G)
#define CH_6   SEG(S_A | S_C | S_D | S_E | S_F | S_G)
#define CH_7   SEG(S_A | S_B | S_C)

#define CH_i   SEG(S_C)                              /* small i: lower-right only */
#define CH_E   SEG(S_A | S_D | S_E | S_F | S_G)
#define CH_C   SEG(S_A | S_D | S_E | S_F)
#define CH_S   SEG(S_A | S_C | S_D | S_F | S_G)
#define CH_d   SEG(S_B | S_C | S_D | S_E | S_G)      /* small d */

/* Digit i (0 = leftmost) -> PC pin.
   If the text shows reversed on the board, change to (7 - (i)). */
#define DIG_PIN(i)  (4 + (i))

#define TEXT_LEN  12


const uint8_t text[TEXT_LEN] = {
    CH_i, CH_E, CH_C, CH_S, CH_d,
    CH_1, CH_2, CH_3, CH_4, CH_5, CH_6, CH_7      // replace with your ID
};

volatile uint8_t start = 0;       // index of the character on the leftmost digit
volatile uint8_t led_pos = 0;     // 0~3 = PC12~PC15

volatile uint8_t pressed_key = 0;


void Update_LED(void)
{
    /* LEDs are active low: 0 = on */
    PC->DOUT |= 0xF000;                         // all LEDs off
    PC->DOUT &= ~(1 << (12 + led_pos));         // only one LED on
}


void Init_LED(void)
{
    GPIO_SetMode(PC, BIT12, GPIO_MODE_QUASI);
    GPIO_SetMode(PC, BIT13, GPIO_MODE_QUASI);
    GPIO_SetMode(PC, BIT14, GPIO_MODE_QUASI);
    GPIO_SetMode(PC, BIT15, GPIO_MODE_QUASI);

    Update_LED();                               // only PC12 on
}


void Init_key(void)
{
    GPIO_SetMode(PA, BIT0, GPIO_MODE_QUASI);
    GPIO_SetMode(PA, BIT1, GPIO_MODE_QUASI);
    GPIO_SetMode(PA, BIT2, GPIO_MODE_QUASI);

    GPIO_SetMode(PA, BIT3, GPIO_MODE_QUASI);
    GPIO_SetMode(PA, BIT4, GPIO_MODE_QUASI);
    GPIO_SetMode(PA, BIT5, GPIO_MODE_QUASI);

    PA0 = 1;
    PA1 = 1;
    PA2 = 1;

    /* PA3 low forever, PA4/PA5 high forever */
    PA3 = 0;
    PA4 = 1;
    PA5 = 1;

    GPIO_EnableInt(PA, 0, GPIO_INT_BOTH_EDGE);
    GPIO_EnableInt(PA, 1, GPIO_INT_BOTH_EDGE);
    GPIO_EnableInt(PA, 2, GPIO_INT_BOTH_EDGE);

    NVIC_EnableIRQ(GPAB_IRQn);

    GPIO_SET_DEBOUNCE_TIME(GPIO_DBCLKSRC_LIRC, GPIO_DBCLKSEL_64);
    GPIO_ENABLE_DEBOUNCE(PA, BIT0 | BIT1 | BIT2);
}


int GetKey(void)
{
    if (PA0 == 0) return 1;
    if (PA1 == 0) return 2;
    if (PA2 == 0) return 3;
    return 0;
}


void GPAB_IRQHandler(void)
{
    int key;

    if (PA->ISRC & BIT0) PA->ISRC = BIT0;
    if (PA->ISRC & BIT1) PA->ISRC = BIT1;
    if (PA->ISRC & BIT2) PA->ISRC = BIT2;

    key = GetKey();

    /* Key pressed: remember it */
    if (key != 0)
    {
        pressed_key = key;
    }

    /* Key released: execute the action */
    else if (pressed_key != 0)
    {
        if (pressed_key == 3)
        {
            /* Text moves left, LED moves right */
            start = (start + 1) % TEXT_LEN;
            led_pos = (led_pos + 1) % 4;
            Update_LED();
        }
        else if (pressed_key == 1)
        {
            /* Text moves right, LED moves left */
            start = (start + TEXT_LEN - 1) % TEXT_LEN;
            led_pos = (led_pos + 3) % 4;
            Update_LED();
        }

        pressed_key = 0;
    }
}


int32_t main(void)
{
    uint8_t s;
    uint8_t i;

    SYS_Init();

    Init_key();
    Init_LED();

    OpenSevenSegment();

    while (1)
    {
        s = start;      // snapshot so all 4 digits use the same start

        for (i = 0; i < 4; i++)
        {
            CloseSevenSegment();                        // 1. all digits off
            PE->DOUT = text[(s + i) % TEXT_LEN];        // 2. segment pattern
            PC->DOUT |= (1 << DIG_PIN(i));              // 3. enable digit i
        }
    }
}
