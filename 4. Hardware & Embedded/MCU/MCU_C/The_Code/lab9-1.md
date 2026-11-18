```c
//
// Lab9-1: Bresenham Circle Drawing
//
// EVB : Nu-LB-NUC140
// MCU : NUC140VE3CN
//

#include <stdio.h>
#include <stdint.h>
#include "NUC100Series.h"
#include "MCU_init.h"
#include "SYS_init.h"
#include "LCD.h"
#include "Scankey.h"
#include "Seven_Segment.h"

#define XC 64
#define YC 32

// Draw or erase eight symmetric points
static void plot_circle_points(int xc, int yc, int x, int y,
                               uint16_t color)
{
    draw_Pixel(xc + x, yc + y, color, BG_COLOR);
    draw_Pixel(xc - x, yc + y, color, BG_COLOR);
    draw_Pixel(xc + x, yc - y, color, BG_COLOR);
    draw_Pixel(xc - x, yc - y, color, BG_COLOR);

    draw_Pixel(xc + y, yc + x, color, BG_COLOR);
    draw_Pixel(xc - y, yc + x, color, BG_COLOR);
    draw_Pixel(xc + y, yc - x, color, BG_COLOR);
    draw_Pixel(xc - y, yc - x, color, BG_COLOR);
}

// Bresenham Circle Algorithm
static void draw_bresenham_circle(int xc, int yc, int radius,
                                  uint16_t color)
{
    int x = 0;
    int y = radius;
    int p = 3 - 2 * radius;

    while (x <= y)
    {
        plot_circle_points(xc, yc, x, y, color);

        if (p < 0)
        {
            p = p + 4 * x + 6;
        }
        else
        {
            p = p + 4 * (x - y) + 10;
            y--;
        }

        x++;
    }
}

int32_t main(void)
{
    int key;
    int pressed_Key = 0;

    int radius = 0;
    int previous_radius = 0;
    int has_circle = 0;

    SYS_Init();
    init_LCD();
    clear_LCD();

    OpenKeyPad();
    OpenSevenSegment();

    while (1)
    {
        key = ScanKey();

        // Execute only when the key is released
        if (pressed_Key != 0 && key == 0)
        {
            if (pressed_Key >= 1 && pressed_Key <= 9)
            {
                radius = pressed_Key;

                // Erase the previous circle
                if (has_circle)
                {
                    draw_bresenham_circle(
                        XC, YC, previous_radius, BG_COLOR
                    );
                }

                // Draw the new circle
                draw_bresenham_circle(
                    XC, YC, radius, FG_COLOR
                );

                previous_radius = radius;
                has_circle = 1;
            }

            pressed_Key = 0;
        }
        else
        {
            pressed_Key = key;
        }

        // Display current radius on the rightmost digit
        if (has_circle)
        {
            ShowSevenSegment(0, radius);
        }

        CLK_SysTickDelay(5000);
    }
}
