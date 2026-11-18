//
// LCD_Graph_Pingpong: draw a circle bouncing around between two bars on LCD
//
// EVB : Nu-LB-NUC140
// MCU : NUC140VE3CN
//
#include <stdio.h>
#include <math.h>
#include "NUC100Series.h"
#include "MCU_init.h"
#include "SYS_init.h"
#include "LCD.h"
#include "Draw2D.h"
#include "Scankey.h"

#define PIXEL_ON  1
#define PIXEL_OFF 0
#define X0 15       // Circle initial X 
#define Y0 10       // Circle initial Y
#define R_BAR_X LCD_Xmax-1 // Right-Bar X-position
#define L_BAR_X 0          // Left-Bar  X-position


void Buzz(void)
{
	PB11 = 0;
	CLK_SysTickDelay(20000);
	PB11 = 1;
}


int32_t main (void)
{
	int dirX, dirY;
	int movX, movY;
	uint16_t r;
	uint16_t x, y;
	uint16_t fgColor, bgColor;
	int key, pressed_Key = 0;
	int moving = 0;
	
	SYS_Init();
	init_LCD();  
	clear_LCD();
	OpenKeyPad();

	GPIO_SetMode(PB, BIT11, GPIO_MDOE_OUTPUT);
	PB = 1;
	
	x = 64;    // circle center x
	y = 32;    // circle center y
	r = 3;    // circle radius
	movX = 3;  // x movement
	movY = 3;  // y movement
	dirX = 1;  // x direction
	dirY = 1;  // y direction
	
	bgColor = BG_COLOR;
	while(1) {
		
		key = Scankey();
		
		if (pressed_Key != 0 && key == 0)
		{
			if (pressed_Key != 5)
			{
				switch(pressed_Key) {
				case 1: dirX = -1; dirY = -1; break;
				case 3: dirX = 1; dirY = -1; break;
				case 4: dirX = -1; dirY = 0; break;
				case 6: dirX = 1; dirY = 0; break;
				case 7: dirX = -1; dirY = 1; break;
				case 9: dirX = 1; dirY = 1; break;
				default:
					break;
				}
			}
			
			if (pressed_Key == 5)
			{
				moving = !moving;
			}

		} else {
			pressed_Key = key;
		}

		if (moving)
		{
			fgColor = FG_COLOR;
			draw_Circle(x, y, r, fgColor, bgColor); // draw a circle
			draw_Line(L_BAR_X,y-7, L_BAR_X,y+7, fgColor, bgColor); // draw left  line			
			draw_Line(R_BAR_X,y-7, R_BAR_X,y+7, fgColor, bgColor); // draw right line

			CLK_SysTickDelay(50000); // adjustable delay for vision
					
			fgColor = BG_COLOR;
			draw_Circle(x, y, r, fgColor, bgColor); // erase a circle
			draw_Line(L_BAR_X,y-7,L_BAR_X,y+7, fgColor, bgColor); // draw left  line				
			draw_Line(R_BAR_X,y-7,R_BAR_X,y+7, fgColor, bgColor); // draw right line
									
			// boundary check for changing direction
			if      ((x-r) < L_BAR_X) { dirX=1; Buzz();  }
			else if ((x+r) > R_BAR_X) { dirX=-1; Buzz(); }
			else if ((y-r) < 0)       { dirY=1;  Buzz(); }
			else if ((y+r) > LCD_Ymax){ dirY=-1; Buzz(); }
					
			x = x + dirX * movX; // change x of circle center
			y = y + dirY * movY; // change y of circle center							
		}
	}
}
