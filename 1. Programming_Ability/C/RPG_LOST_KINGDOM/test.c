#include <stdio.h>
#include <string.h>

int main() {
    int arr[][9] = {{100, 100, 100,
                      99, 99, 99,
                      88, 88, 88},
                      {77, 77, 77,
                       66, 66, 66,
                       55, 55, 55}};
    
    int rows = sizeof(arr) / sizeof(arr[0]);
    int columes = sizeof(arr[0]) / sizeof(arr[0][0]);

    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < columes; j++)
        {
            printf("%d ", arr[i][j]);
        }
        printf("\n");
    }
}