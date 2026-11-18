```c
//
// Lab9-2: Bresenham Ellipse Drawing
//
// EVB : Nu-LB-NUC140
// MCU : NUC140VE3CN
//

#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include "NUC100Series.h"
#include "MCU_init.h"
#include "SYS_init.h"
#include "LCD.h"
#include "Scankey.h"

#define XC 64
#define YC 32

#define A 10
#define B 30

#define MAX_POINTS 64

typedef struct {
    int x;
    int y;
} Point;

static Point points[MAX_POINTS];
static int point_count = 0;

static int drawn[4] = {0};

// Round floating-point coordinates to the nearest integer
static int round_int(double value)
{
    if (value >= 0)
        return (int)(value + 0.5);
    else
        return (int)(value - 0.5);
}

// Bresenham Line Algorithm
// draw_Pixel() is the only drawing function used.
static void draw_line(int x0, int y0, int x1, int y1)
{
    int dx = abs(x1 - x0);
    int dy = abs(y1 - y0);

    int sx = (x0 < x1) ? 1 : -1;
    int sy = (y0 < y1) ? 1 : -1;

    int err = dx - dy;
    int e2;

    while (1)
    {
        draw_Pixel(x0, y0, FG_COLOR, BG_COLOR);

        if (x0 == x1 && y0 == y1)
            break;

        e2 = 2 * err;

        if (e2 > -dy)
        {
            err -= dy;
            x0 += sx;
        }

        if (e2 < dx)
        {
            err += dx;
            y0 += sy;
        }
    }
}

// Midpoint Ellipse Algorithm
// Generate points from the top of the ellipse
// to the right side of the ellipse.
static void build_ellipse_points(void)
{
    int x = 0;
    int y = B;

    double a2 = A * A;
    double b2 = B * B;

    double dx = 0;
    double dy = 2 * a2 * y;

    double d1 = b2 - a2 * B + 0.25 * a2;
    double d2;

    point_count = 0;

    // Region 1
    while (dx < dy)
    {
        points[point_count].x = x;
        points[point_count].y = y;
        point_count++;

        if (d1 < 0)
        {
            x++;
            dx += 2 * b2;
            d1 += dx + b2;
        }
        else
        {
            x++;
            y--;

            dx += 2 * b2;
            dy -= 2 * a2;

            d1 += dx - dy + b2;
        }
    }

    // Region 2
    d2 = b2 * (x + 0.5) * (x + 0.5)
       + a2 * (y - 1) * (y - 1)
       - a2 * b2;

    while (y >= 0)
    {
        points[point_count].x = x;
        points[point_count].y = y;
        point_count++;

        if (d2 > 0)
        {
            y--;
            dy -= 2 * a2;
            d2 += a2 - dy;
        }
        else
        {
            x++;
            y--;

            dx += 2 * b2;
            dy -= 2 * a2;

            d2 += dx - dy + a2;
        }
    }
}

// Rotate a point and convert it to LCD coordinates
static void transform_point(int x, int y, int angle,
                            int *screen_x, int *screen_y)
{
    double rad = angle * 3.14159265358979323846 / 180.0;

    double cos_t = cos(rad);
    double sin_t = sin(rad);

    double rx = x * cos_t - y * sin_t;
    double ry = x * sin_t + y * cos_t;

    *screen_x = XC + round_int(rx);
    *screen_y = YC + round_int(ry);
}

// Draw the ellipse using four quadrants.
// The generated first-quadrant points are mirrored.
static void draw_ellipse(int angle)
{
    int i;
    int sx, sy;
    int x1, y1, x2, y2;

    int sign_x, sign_y;

    for (sign_x = -1; sign_x <= 1; sign_x += 2)
    {
        for (sign_y = -1; sign_y <= 1; sign_y += 2)
        {
            for (i = 0; i < point_count - 1; i++)
            {
                // First point
                sx = sign_x * points[i].x;
                sy = sign_y * points[i].y;

                transform_point(sx, sy, angle, &x1, &y1);

                // Next point
                sx = sign_x * points[i + 1].x;
                sy = sign_y * points[i + 1].y;

                transform_point(sx, sy, angle, &x2, &y2);

                // Connect adjacent points
                draw_line(x1, y1, x2, y2);
            }
        }
    }
}

int32_t main(void)
{
    int key;
    int pressed_Key = 0;

    SYS_Init();
    init_LCD();
    clear_LCD();

    OpenKeyPad();

    // Generate the original ellipse points only once
    build_ellipse_points();

    while (1)
    {
        key = ScanKey();

        // Execute operation when the key is released
        if (pressed_Key != 0 && key == 0)
        {
            switch (pressed_Key)
            {
                case 1:
                    if (!drawn[1])
                    {
                        draw_ellipse(0);
                        drawn[1] = 1;
                    }
                    break;

                case 2:
                    if (!drawn[2])
                    {
                        draw_ellipse(60);
                        drawn[2] = 1;
                    }
                    break;

                case 3:
                    if (!drawn[3])
                    {
                        draw_ellipse(-60);
                        drawn[3] = 1;
                    }
                    break;

                case 9:
                    clear_LCD();

                    drawn[1] = 0;
                    drawn[2] = 0;
                    drawn[3] = 0;
                    break;

                default:
                    break;
            }

            pressed_Key = 0;
        }
        else
        {
            pressed_Key = key;
        }

        CLK_SysTickDelay(5000);
    }
}
