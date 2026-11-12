#include <stdio.h>
#include <string.h>

int main() {

    char name[30] = "Shiro Leaf";
    char name2[30] = "Hello";



    snprintf(name, sizeof(name), "%s", name2 ? name2 : "Unnamed");

    printf("%s", name);

    return 0;
}