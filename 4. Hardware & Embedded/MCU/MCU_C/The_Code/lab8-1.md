```c
//
// LCD_Graph_Pingpong: 圓球在兩根擋板間彈跳
//
// EVB : Nu-LB-NUC140
// MCU : NUC140VE3CN
//
// 按鍵: 4=左  6=右  1=左上  3=右上  7=左下  9=右下  5=S(暫停/繼續)
//
#include <stdio.h>
#include <math.h>
#include "NUC100Series.h"
#include "MCU_init.h"
#include "SYS_init.h"
#include "LCD.h"
#include "Draw2D.h"
#include "Seven_Segment.h"
#include "Scankey.h"

#define PIXEL_ON  1
#define PIXEL_OFF 0
#define X0        64
#define Y0        32
#define R_BAR_X   (LCD_Xmax - 1)   
#define L_BAR_X   0
#define BAR_HALF  7
#define Buzzer    PB11

static void Buzz(void)            
{
    Buzzer = 0;
    CLK_SysTickDelay(50000);      
    Buzzer = 1;
}

static void draw_all(int x, int y, int r, uint16_t fg, uint16_t bg)
{
    int y1 = y - BAR_HALF, y2 = y + BAR_HALF;
    if (y1 < 0) y1 = 0;                          // 避免負值 (unsigned 溢位)
    if (y2 > LCD_Ymax - 1) y2 = LCD_Ymax - 1;
    draw_Circle(x, y, r, fg, bg);
    draw_Line(L_BAR_X, y1, L_BAR_X, y2, fg, bg);
    draw_Line(R_BAR_X, y1, R_BAR_X, y2, fg, bg);
}

int32_t main(void)
{
    int key, pressed_key = 0;
    int dirX = 0, dirY = 0;        // 目前(或暫停前)的方向
    int moving = 0;                // 0=暫停  1=移動中
    int x = X0, y = Y0;
    int r = 3, mov = 3;
    int hit;

    SYS_Init();
    init_LCD();
    clear_LCD();
    OpenKeyPad();

    GPIO_SetMode(PB, BIT11, GPIO_MODE_OUTPUT);   
    Buzzer = 1;                                  

    draw_all(x, y, r, FG_COLOR, BG_COLOR);       // 初始畫面

    while (1) {
        // ---- 按鍵：放開時才執行 ----
        key = ScanKey();
        if (key != 0) {
            pressed_key = key;
        } else if (pressed_key != 0) {
            if (pressed_key == 5) {                       // S 鍵
                if (moving) moving = 0;                   // 暫停
                else if (dirX != 0 || dirY != 0) moving = 1; // 依原方向繼續
            } else if (!moving) {                         
                int nx = 0, ny = 0, valid = 1;
                switch (pressed_key) {
                    case 1: nx = -1; ny = -1; break;
                    case 3: nx =  1; ny = -1; break;
                    case 4: nx = -1; ny =  0; break;
                    case 6: nx =  1; ny =  0; break;
                    case 7: nx = -1; ny =  1; break;
                    case 9: nx =  1; ny =  1; break;
                    default: valid = 0; break;
                }
                if (valid) { dirX = nx; dirY = ny; moving = 1; }
            }
            pressed_key = 0;
        }

        // ---- 移動與反彈 ----
        if (moving) {
            draw_all(x, y, r, BG_COLOR, BG_COLOR);        // 擦除舊畫面

            x += dirX * mov;
            y += dirY * mov;

            hit = 0;
            if (x - r <= L_BAR_X)        { x = L_BAR_X + r;        dirX = -dirX; hit = 1; }
            else if (x + r >= R_BAR_X)   { x = R_BAR_X - r;        dirX = -dirX; hit = 1; }
            if (y - r <= 0)              { y = r;                  dirY = -dirY; hit = 1; }
            else if (y + r >= LCD_Ymax-1){ y = LCD_Ymax - 1 - r;   dirY = -dirY; hit = 1; }

            draw_all(x, y, r, FG_COLOR, BG_COLOR);        // 畫新畫面
            if (hit) Buzz();
        }

        CLK_SysTickDelay(50000);   // 移動速度，可調整
    }
}