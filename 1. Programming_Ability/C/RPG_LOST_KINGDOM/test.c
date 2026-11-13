#include <stdio.h>
#include <string.h>

int main() {

    char groceries[][9] = {"Apple", 
                           "Banana", 
                           "Pineapple",
                           "Ferari", 
                           "Honda", 
                           "Tesla",
                           "Running", 
                           "Raining", 
                           "Crying"};

    printf("%c", groceries[3][5]);

    return 0;
}