```c
/*
 * Lab7-2: Language selection + text rotation
 * EVB: Nu-LB-NUC140
 * MCU: NUC140VE3CN
 *
 * Key 1: Select Chinese
 * Key 2: Select Japanese
 * INT1 : Confirm language
 * Key 4: Rotate counter-clockwise
 * Key 5: Pause
 * Key 6: Rotate clockwise
 *
 * Rotation: 90 degrees every second
 */

#include <stdio.h>
#include <stdint.h>

#include "NUC100Series.h"
#include "MCU_init.h"
#include "SYS_init.h"
#include "LCD.h"
#include "Scankey.h"
#include "Seven_Segment.h"

/* =========================================================
   16 x 16 bitmap data
   Keep the original bitmap data from your program here.
   ========================================================= */

/* Chinese glyphs */
const unsigned char ZH_0[32] = {
    0x40,0xE0,0xF8,0xFE,0x07,0x60,0x7C,0x1F,
    0x1F,0xF8,0xF8,0x18,0x18,0x78,0x78,0x00,
    0x00,0x00,0xFF,0xFF,0x00,0x18,0x1F,0x0F,
    0xC1,0xFF,0xFF,0x00,0x03,0x1F,0x1C,0x00
};

const unsigned char ZH_1[32] = {
    0x08,0xF8,0xFF,0x1F,0x98,0xFE,0x7C,0xC9,
    0xC3,0xC3,0xF3,0xFB,0xDF,0xCF,0xC3,0x80,
    0x00,0x61,0x3B,0x3F,0x1F,0x1F,0x38,0x00,
    0x60,0x60,0x7F,0x7F,0x00,0x00,0x00,0x00
};

const unsigned char ZH_2[32] = {
    0x00,0x30,0x30,0xFF,0xFE,0x30,0x30,0xFF,
    0xFF,0x30,0x30,0xFF,0xFF,0x30,0x30,0x00,
    0x00,0x00,0x00,0x7F,0x7F,0x60,0x60,0x67,
    0x67,0x66,0x66,0x67,0x67,0x60,0x60,0x00
};

const unsigned char ZH_3[32] = {
    0x00,0x00,0x7F,0x7F,0xED,0xED,0xED,0x7F,
    0x7F,0xED,0xED,0xED,0x7F,0x7F,0x00,0x00,
    0x00,0x06,0x27,0x73,0x3B,0x1F,0x0E,0x00,
    0x00,0x3C,0x7F,0x7F,0x03,0x07,0x06,0x00
};

/* Japanese glyphs */
const unsigned char JA_0[32] = {
    0x00,0x00,0x00,0x00,0xF0,0xF8,0x38,0x00,
    0x00,0x08,0x7C,0xF8,0xE0,0x00,0x00,0x00,
    0x00,0x10,0x3C,0x1F,0x0F,0x01,0x00,0x00,
    0x00,0x00,0x00,0x03,0x1F,0x3F,0x18,0x00
};

const unsigned char JA_1[32] = {
    0x00,0x00,0xFC,0xFC,0x0C,0x0C,0x0C,0x0C,
    0x0C,0x0C,0x0C,0x0C,0xFC,0xFC,0x00,0x00,
    0x00,0x00,0x3F,0x3F,0x18,0x18,0x18,0x18,
    0x18,0x18,0x18,0x18,0x3F,0x3F,0x00,0x00
};

const unsigned char JA_2[32] = {
    0x00,0x60,0x60,0x60,0x60,0x60,0x60,0x60,
    0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
};

const unsigned char JA_3[32] = {
    0x00,0x00,0x7E,0x7E,0x06,0x06,0x06,0x06,
    0x06,0x06,0x86,0xF6,0xFE,0x3E,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x30,0x38,0x38,
    0x1C,0x1E,0x0F,0x07,0x01,0x00,0x00,0x00
};

const unsigned char JA_4[32] = {
    0x00,0x60,0x60,0x60,0x60,0x60,0x60,0x60,
    0x60,0x60,0x60,0x60,0x60,0x60,0x60,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
};

const unsigned char JA_5[32] = {
    0x00,0x00,0x00,0x00,0xFE,0xFE,0x00,0x00,
    0xFE,0xFE,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x10,0x3C,0x1F,0x0F,0x01,0x00,0x00,
    0x1F,0x3F,0x1C,0x1C,0x0E,0x07,0x03,0x00
};

const unsigned char JA_6[32] = {
    0x00,0x00,0x00,0x00,0xFC,0xFC,0xFC,0xC0,
    0xC0,0x80,0x8C,0x18,0x06,0x0C,0x00,0x00,
    0x00,0x00,0x00,0x00,0x7F,0x7F,0x7F,0x01,
    0x01,0x01,0x03,0x03,0x03,0x00,0x00,0x00
};

static const unsigned char *ZH_TEXT[4] = {
    ZH_0, ZH_1, ZH_2, ZH_3
};

static const unsigned char *JA_TEXT[7] = {
    JA_0, JA_1, JA_2, JA_3, JA_4, JA_5, JA_6
};

static unsigned char FrameBuf[LCD_Xmax * (LCD_Ymax / 8)];

/* =========================================================
   Program state
   ========================================================= */

static volatile uint32_t ticks100ms = 0;
static volatile uint8_t confirmReq = 0;

static uint8_t langSel = 0;
static uint8_t langConf = 0;

static int8_t rotDir = 0;   /* +1 = CCW, -1 = CW, 0 = stopped */
static uint8_t angle = 0;   /* 0, 1, 2, 3 = 0, 90, 180, 270 */

/* =========================================================
   TIMER0 interrupt
   ========================================================= */

void TMR0_IRQHandler(void)
{
    TIMER0->TISR = TIMER_TISR_TIF_Msk;
    ticks100ms++;
}

static void Init_Timer0(void)
{
    SYS_UnlockReg();

    CLK->APBCLK |= CLK_APBCLK_TMR0_EN_Msk;

    CLK->CLKSEL1 =
        (CLK->CLKSEL1 & ~CLK_CLKSEL1_TMR0_S_Msk)
        | CLK_CLKSEL1_TMR0_S_HXT;

    SYS_LockReg();

    /*
     * HXT = 12 MHz
     * Prescaler = 11, so timer clock = 12 MHz / 12 = 1 MHz
     * Compare = 100000, approximately 100 ms
     *
     * Bit 27 selects periodic mode for this timer configuration.
     */
    TIMER0->TCMPR = 100000;

    TIMER0->TCSR = TIMER_TCSR_IE_Msk
                 | (1UL << 27)
                 | 11UL
                 | TIMER_TCSR_CEN_Msk;

    NVIC_EnableIRQ(TMR0_IRQn);
}

/* =========================================================
   INT1 configuration
   ========================================================= */

static void Init_EINT1(void)
{
    GPIO_SetMode(PB, BIT15, GPIO_PMD_INPUT);

    GPIO_EnableEINT1(PB, 15, GPIO_INT_RISING);

    NVIC_EnableIRQ(EINT1_IRQn);

    GPIO_SET_DEBOUNCE_TIME(GPIO_DBCLKSRC_LIRC, GPIO_DBCLKSEL_64);
    GPIO_ENABLE_DEBOUNCE(PB, BIT15);
}

void EINT1_IRQHandler(void)
{
    GPIO_CLR_INT_FLAG(PB, BIT15);
    confirmReq = 1;
}

/* =========================================================
   Render rotated text into the LCD framebuffer
   ========================================================= */

static void render_text(const unsigned char **text, int n, int ang)
{
    int g, i, j, k;
    int W = n * 16;
    int rx, ry, ax, ay, sx, sy;
    unsigned char b;

    for (i = 0; i < LCD_Xmax * (LCD_Ymax / 8); i++)
        FrameBuf[i] = 0;

    for (g = 0; g < n; g++) {
        for (j = 0; j < 2; j++) {
            for (i = 0; i < 16; i++) {
                b = text[g][i + j * 16];

                for (k = 0; k < 8; k++) {
                    if (!(b & (1U << k)))
                        continue;

                    rx = 2 * (g * 16 + i) + 1 - W;
                    ry = 2 * (j * 8 + k) + 1 - 16;

                    switch (ang & 3) {
                        case 0:
                            ax = rx;
                            ay = ry;
                            break;

                        case 1:
                            ax = ry;
                            ay = -rx;
                            break;

                        case 2:
                            ax = -rx;
                            ay = -ry;
                            break;

                        default:
                            ax = -ry;
                            ay = rx;
                            break;
                    }

                    sx = 64 + (ax - 1) / 2;
                    sy = 32 + (ay - 1) / 2;

                    if (sx >= 0 && sx < LCD_Xmax &&
                        sy >= 0 && sy < LCD_Ymax) {
                        FrameBuf[sx + (sy >> 3) * LCD_Xmax]
                            |= (1U << (sy & 7));
                    }
                }
            }
        }
    }
}

/* =========================================================
   LCD display functions
   ========================================================= */

static void show_text(void)
{
    if (langConf == 1)
        render_text(ZH_TEXT, 4, angle);
    else
        render_text(JA_TEXT, 7, angle);

    draw_LCD(FrameBuf);
}

static void show_prompt(void)
{
    clear_LCD();
    printS(4, 24, "Select Language");
}

/* =========================================================
   Wait for keypad release
   ========================================================= */

static void wait_release(void)
{
    CLK_SysTickDelay(20000);

    while (ScanKey() != 0) {
        /* Wait until key is released */
    }

    CLK_SysTickDelay(20000);
}

/* =========================================================
   Main
   ========================================================= */

int main(void)
{
    uint8_t key;
    uint32_t tStart = 0;

    SYS_Init();

    init_LCD();
    clear_LCD();

    OpenKeyPad();
    OpenSevenSegment();
    CloseSevenSegment();

    Init_EINT1();
    Init_Timer0();

    show_prompt();

    while (1) {
        /* ---------- Keypad ---------- */

        key = ScanKey();

        if (key != 0) {
            wait_release();

            switch (key) {
                case 1:
                    langSel = 1;

                    CloseSevenSegment();
                    ShowSevenSegment(0, 1);
                    break;

                case 2:
                    langSel = 2;

                    CloseSevenSegment();
                    ShowSevenSegment(0, 2);
                    break;

                case 4:
                    if (langConf != 0) {
                        rotDir = +1;
                        tStart = ticks100ms;
                    }
                    break;

                case 5:
                    if (langConf != 0)
                        rotDir = 0;
                    break;

                case 6:
                    if (langConf != 0) {
                        rotDir = -1;
                        tStart = ticks100ms;
                    }
                    break;

                default:
                    break;
            }
        }

        /* ---------- INT1 confirmation ---------- */

        if (confirmReq) {
            confirmReq = 0;

            if (langSel != 0) {
                langConf = langSel;

                angle = 0;
                rotDir = 0;

                show_text();
            }
        }

        /* ---------- Rotate every second ---------- */

        if (langConf != 0 &&
            rotDir != 0 &&
            (uint32_t)(ticks100ms - tStart) >= 10) {

            tStart += 10;

            if (rotDir > 0)
                angle = (angle + 1) & 3;
            else
                angle = (angle + 3) & 3;

            show_text();
        }
    }
}