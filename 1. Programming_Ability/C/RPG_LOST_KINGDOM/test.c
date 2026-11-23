
#include <stdio.h>
#include <stdint.h>

#include "NUC100Series.h"
#include "MCU_init.h"
#include "SYS_init.h"
#include "LCD.h"
#include "Draw2D.h"
#include "Scankey.h"
#include "Seven_Segment.h"

// LCD dimensions
#define LCD_WIDTH   128
#define LCD_HEIGHT  64

// Square dimensions
#define SQUARE_SIZE 8

// Movement intervals (ms)
#define SPEED_1     200
#define SPEED_2     100
#define SPEED_3     40

// Background color
#define BLACK       0x0000

// RGB LED pins (active low)
#define RED_PIN     (1 << 12)
#define GREEN_PIN   (1 << 13)
#define BLUE_PIN    (1 << 14)
#define RGB_MASK    (RED_PIN | GREEN_PIN | BLUE_PIN)

// Square position
int16_t x = (LCD_WIDTH - SQUARE_SIZE) / 2;
int16_t y = (LCD_HEIGHT - SQUARE_SIZE) / 2;

// Movement direction
int8_t dx = 1;
int8_t dy = 1;

// Program state
uint8_t running = 0;
uint8_t speed = 1;

// ADC initialization
void InitADC(void)
{
    // Configure GPA7 as ADC7
    GPIOA->OFFD |= (1 << 7);
    SYS->GPAMFP.ADC7_SS21_AD6 = 1;

    // Enable ADC clock
    CLK->CLKSEL1.ADC_S = 2;
    CLK->CLKDIV.ADC_N = 1;
    CLK->APBCLK.ADC_EN = 1;

    // Enable ADC module
    ADC->ADCR.ADEN = 1;

    // Single-end input, single conversion mode
    ADC->ADCR.DIFFEN = 0;
    ADC->ADCR.ADMD = 0;

    // Select ADC channel 7
    ADC->ADCHER.CHEN = 0x80;
}

// Read VR1
uint16_t ReadADC(void)
{
    ADC->ADSR.ADF = 1;

    // Start conversion
    ADC->ADCR.ADST = 1;

    // Wait for conversion
    while (ADC->ADSR.ADF == 0);

    return ADC->ADDR[7].RSLT;
}

// Determine movement speed
uint8_t GetSpeed(uint16_t adcValue)
{
    if (adcValue < 1365)
        return 1;
    else if (adcValue < 2730)
        return 2;
    else
        return 3;
}

// Set RGB LED color
void SetRGB(uint8_t speed)
{
    GPIOA->DOUT |= RGB_MASK;

    if (speed == 1)
        GPIOA->DOUT &= ~BLUE_PIN;
    else if (speed == 2)
        GPIOA->DOUT &= ~GREEN_PIN;
    else
        GPIOA->DOUT &= ~RED_PIN;
}

// Update Seven Segment
void UpdateSevenSegment(uint8_t speed)
{
    ShowSevenSegment(0, speed);
}

// Draw square
void DrawSquare(int16_t x, int16_t y, uint16_t color)
{
    fill_Rectangle(
        x, y,
        x + SQUARE_SIZE - 1,
        y + SQUARE_SIZE - 1,
        color, BLACK
    );
}

// Move square
void MoveSquare(void)
{
    // Erase previous square
    DrawSquare(x, y, BLACK);

    // Update position
    x += dx;
    y += dy;

    // Horizontal boundary collision
    if (x <= 0)
    {
        x = 0;
        dx = 1;
    }
    else if (x >= LCD_WIDTH - SQUARE_SIZE)
    {
        x = LCD_WIDTH - SQUARE_SIZE;
        dx = -1;
    }

    // Vertical boundary collision
    if (y <= 0)
    {
        y = 0;
        dy = 1;
    }
    else if (y >= LCD_HEIGHT - SQUARE_SIZE)
    {
        y = LCD_HEIGHT - SQUARE_SIZE;
        dy = -1;
    }

    // Draw new square
    DrawSquare(x, y, FG_COLOR);
}

// Initialize RGB LED
void InitRGB(void)
{
    GPIOA->PMD &= ~(3 << 24);
    GPIOA->PMD &= ~(3 << 26);
    GPIOA->PMD &= ~(3 << 28);

    GPIOA->PMD |= (1 << 24);
    GPIOA->PMD |= (1 << 26);
    GPIOA->PMD |= (1 << 28);

    GPIOA->DOUT |= RGB_MASK;
}

// Main
int main(void)
{
    uint16_t adcValue;
    uint8_t key;
    uint8_t previousKey = 0;

    uint16_t moveCounter = 0;
    uint16_t moveInterval;

    SYS_Init();

    init_LCD();
    clear_LCD();

    OpenKeyPad();
    OpenSevenSegment();

    InitADC();
    InitRGB();

    // Initial square
    DrawSquare(x, y, FG_COLOR);

    while (1)
    {
        // Scan keypad
        key = ScanKey();

        // Center key (S) toggles movement
        if (key == 5 && previousKey != 5)
        {
            running = !running;
        }

        previousKey = key;

        // Read potentiometer
        adcValue = ReadADC();

        // Determine speed
        speed = GetSpeed(adcValue);

        // Update output devices
        SetRGB(speed);
        UpdateSevenSegment(speed);

        // Movement interval
        if (speed == 1)
            moveInterval = SPEED_1;
        else if (speed == 2)
            moveInterval = SPEED_2;
        else
            moveInterval = SPEED_3;

        if (running)
        {
            moveCounter += 10;

            if (moveCounter >= moveInterval)
            {
                moveCounter = 0;
                MoveSquare();
            }
        }
        else
        {
            moveCounter = 0;
        }

        CLK_SysTickDelay(10000);  // 10 ms
    }
}
