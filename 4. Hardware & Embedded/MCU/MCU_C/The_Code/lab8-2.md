```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "NUC100Series.h"
#include "MCU_init.h"
#include "SYS_init.h"
#include "LCD.h"
#include "Scankey.h"
#include "Seven_Segment.h"

#define LCD_COLS   16
#define LCD_ROWS   4
#define LOG_MAX    50
#define LED_PASSES 250          // one refresh pass is about 2 ms, so 250 passes is about 0.5 s (tune on the board)

// RGB LED (active low); swap these three lines if the colors are in the wrong order
#define LED_R      PA14
#define LED_G      PA13
#define LED_B      PA12

typedef enum { IDLE, GUESSING, RESULT } State;

static char logbuf[LOG_MAX][LCD_COLS + 1];
static int  logCnt = 0;
static int  logTop = 0;

static int      seg_num   = 0;              // 0 = all off
static volatile uint8_t int1_flag = 0;
static uint8_t  led_on = 0, led_phase = 0;
static uint16_t led_cnt = 0;
static uint32_t passes = 0;                 // free-running counter, used as random seed

/* ---------- INT1 (PB15) ---------- */
void EINT1_IRQHandler(void)
{
    GPIO_CLR_INT_FLAG(PB, BIT15);
    int1_flag = 1;
}

static void Init_INT1(void)
{
    SYS->GPB_MFP |= SYS_GPB_MFP_PB15_INT1;
    GPIO_SetMode(PB, BIT15, GPIO_MODE_INPUT);
    GPIO_EnableEINT1(PB, 15, GPIO_INT_RISING);   // fires on release
    GPIO_SET_DEBOUNCE_TIME(GPIO_DBCLKSRC_HCLK, GPIO_DBCLKSEL_32768);
    GPIO_ENABLE_DEBOUNCE(PB, BIT15);
    NVIC_EnableIRQ(EINT1_IRQn);
}

static void Init_LED(void)
{
    GPIO_SetMode(PA, BIT12 | BIT13 | BIT14, GPIO_MODE_OUTPUT);
    LED_R = LED_G = LED_B = 1;
}

/* ---------- Seven-segment + LED: one pass, about 2 ms ---------- */
static void seg_refresh(void)
{
    passes++;

    if (seg_num == 0) {
        CloseSevenSegment();
        CLK_SysTickDelay(2000);
    } else {
        ShowSevenSegment(0, seg_num % 10);           // ones digit
        CLK_SysTickDelay(1000);
        CloseSevenSegment();
        if (seg_num >= 10) {
            ShowSevenSegment(1, seg_num / 10);       // tens digit
            CLK_SysTickDelay(1000);
            CloseSevenSegment();
        } else {
            CLK_SysTickDelay(1000);
        }
    }

    if (led_on) {                                    // red -> green -> blue, 0.5 s each
        if (++led_cnt >= LED_PASSES) { led_cnt = 0; led_phase = (led_phase + 1) % 3; }
        LED_R = (led_phase != 0);
        LED_G = (led_phase != 1);
        LED_B = (led_phase != 2);
    } else {
        LED_R = LED_G = LED_B = 1;
    }
}

/* ---------- LCD log ---------- */
static char *line_new(void)
{
    char *l;
    if (logCnt == LOG_MAX) {
        memmove(logbuf[0], logbuf[1], (LOG_MAX - 1) * (LCD_COLS + 1));
        logCnt--;
    }
    l = logbuf[logCnt++];
    memset(l, ' ', LCD_COLS);
    l[LCD_COLS] = '\0';
    return l;
}

static void log_center(const char *s)
{
    int n = strlen(s);
    char *l = line_new();
    memcpy(l + (LCD_COLS - n) / 2, s, n);
}

static void log_lr(const char *left, const char *right)
{
    int n = strlen(right);
    char *l = line_new();
    memcpy(l, left, strlen(left));
    memcpy(l + LCD_COLS - n, right, n);
}

static void render(void)        // refresh the seven-segment display after every row so it does not flicker
{
    int r, idx;
    for (r = 0; r < LCD_ROWS; r++) {
        idx = logTop + r;
        if (idx < logCnt) printS(0, r * 16, logbuf[idx]);
        else              printS(0, r * 16, "                ");
        seg_refresh();
    }
}

static int  max_top(void)    { return (logCnt > LCD_ROWS) ? logCnt - LCD_ROWS : 0; }
static void log_follow(void) { logTop = max_top(); render(); }

static int new_secret(void)
{
    srand(passes * 2654435761u ^ SysTick->VAL);
    return (rand() % 9 + 1) * 10 + (rand() % 9 + 1);
}

/* ---------- main ---------- */
int main(void)
{
    State   state = IDLE;
    uint8_t key, last = 0, k;
    int     inVal = 0, inCnt = 0;
    int     secret = 11, lo = 0, hi = 99, x;
    char    buf[LCD_COLS + 1], rng[LCD_COLS + 1];

    SYS_Init();
    init_LCD();
    clear_LCD();
    OpenKeyPad();
    OpenSevenSegment();
    CloseSevenSegment();
    Init_LED();
    Init_INT1();

    log_center("Ultimate Guess");
    log_follow();

    while (1)
    {
        seg_refresh();                               // refreshed on every loop pass

        key = ScanKey();
        if (key != 0) {
            last = key;
        } else if (last != 0) {                      // act on key release
            k = last;
            last = 0;

            switch (state) {
            case IDLE:
            case GUESSING:
                if (inCnt < 2) {
                    inVal = inVal * 10 + k;
                    inCnt++;
                    seg_num = inVal;
                    if (state == IDLE) {
                        secret = new_secret();
                        state = GUESSING;
                    }
                }
                break;
            case RESULT:
                if (k == 2 && logTop > 0)               { logTop--; render(); }
                else if (k == 8 && logTop < max_top())  { logTop++; render(); }
                break;
            default: break;
            }
        }

        if (int1_flag) {
            int1_flag = 0;

            if (state == RESULT) {                   // press again: clear the log and start a new game
                led_on = 0;
                logCnt = 0;
                lo = 0; hi = 99;
                inVal = inCnt = 0;
                seg_num = 0;
                state = IDLE;
                log_center("Ultimate Guess");
                log_follow();
            }
            else if (inCnt > 0) {
                x = inVal;
                inVal = inCnt = 0;
                seg_num = 0;

                if (x < lo || x > hi) {
                    log_center("OUT OF RANGE");
                }
                else if (x == secret) {
                    log_center("CONGRATS!!!");
                    sprintf(buf, "The code is %d", secret);
                    log_center(buf);
                    led_phase = 0; led_cnt = 0; led_on = 1;
                    state = RESULT;
                }
                else if (x > secret) {
                    hi = x - 1;
                    sprintf(rng, "%d--%d", hi, lo);
                    log_lr("LOWER!!!", rng);
                }
                else {
                    lo = x + 1;
                    sprintf(rng, "%d--%d", hi, lo);
                    log_lr("HIGHER!!!", rng);
                }
                log_follow();
            }
        }
    }
}