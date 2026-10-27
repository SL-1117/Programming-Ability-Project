# Programming-Ability-Project

2026/10/27 Tuesday

# note
Working on controlling MCU 7segment by each pin.

***means completed
**means almost
*means a little

### quest.h quest.c main.c
quest.h:
#ifndef STACK_H
#define STACK_H

// functions

#endif

quest.c

# Quest Manager ***
Linked list
Accept, complete, remove quests


# Skill Manager ***
Tree
Prerequisites and unlocking


# World Manager
Graph
Rooms, exits, pathfinding


# Combat Manager ***
Heap + Queue
Initiative and pending actions


# Item Database
Hash table
Find items by ID


# Battle History ***
Stack
Undo previous actions

# Heap & Priority_queue ***
Queue / Circular queue
Line up in a convenience store

# The roadmap of Data Structure(but dis is not for today tho.)
```c
                           DATA STRUCTURES
                                  │
          ┌───────────────────────┼────────────────────────┐
          │                       │                        │
          ▼                       ▼                        ▼
       LINEAR                HIERARCHICAL              NETWORK
          │                       │                        │
    ┌─────┼─────┐           ┌─────┼─────┐                  │
    │     │     │           │     │     │                  │
    ▼     ▼     ▼           ▼     ▼     ▼                  ▼
  Array  List  Stack       Tree   Heap  Trie              Graph
    │     │     │
    │     │     └── Queue
    │     │          │
    │     │          ├── Circular Queue
    │     │          └── Priority Queue
    │     │
    │     ├── Singly Linked List
    │     ├── Doubly Linked List
    │     └── Circular Linked List
    │
    └── Dynamic Array
```


# Main
```c
#include <stdio.h>
#include <stdbool.h>
#include <ctype.h>

guess = toupper(guess);
guess = tolower(guess);

scanf(" %s", name);
printf("%3d", name;)

for (int i = 0; i < 10; i++)
{
    if (i == 5)
    {
        break;
    }

    printf("%d", i);
}

for (int i = 0; i < 10; i++)
{
    if (i == 5)
    {
        continue;
    }

    printf("%d", i);
}

int numbers[5] = {0};
int numbers[5] = {1, 2, 3, 4, 5};

char guess = '\0';
char characters[] = {'A', 'B', 'C', 'D', 'E'}; 
char characters2[] = "HelloWorld";

char keypad[][3] = {{'1', '2', '3'},
                    {'4', '5', '6'},
                    {'7', '8', '9'},
                    {'*', '0', '#'}};
char fruits[][3] = {"Apple", 
                    "Banana",
                    "Coconut"};

fruits[0][0] = 'e';
fruits[0][4] = 'A';

fruits[1][0] = 'a';
fruits[1][5] = 'B';

fruits[2][0] = 't';
fruits[2][6] = 'C';

// when we enter 10 at the first scanf, we press "enter" 
// so the program is actually received 10\n
scanf("%d", &num);
scanf(" %c", &choice);

bool age18Check(int age)
{
    if (age >= 18) return true;
    else return false;
}

bool age18Check2(int age)
{
    return age >= 18;
}

char AttackCheck(void) 
{
    int hp = 10;

    do {
        printf("Attack!\n");
        hp -= 1;
        Sleep(1000);
    } while (hp > 0);
}

int main(void) 
{
    bool islocked = true;

    char name[20] = "";
    char operator = '\0';

    float weight = 0.0f;
    float height = 0.0f;
    float rnum = 10.00;

    double num1 = 0.0;
    double num2 = 21.34;
    double result = 0.0;

    int age = 3;

    printf("Enter ur name: \n");
    fgets(name, sizeof(name), stdin);
    name[strlen(name) - 1] = '\0';

    printf("ur name is %s\n", name);
    printf("ur age is %.2lf\n", age);

    if (islocked == true)
    {
        if (age18Check2(18))
        {
            printf("You are already 18.\n");
        }

        else 
        {
            printf("You are not 18 yet.\n");
        }

        printf("You ara locked.\n");
    }

    else if (islocked == false)
    {
        printf("You are not a locked.\n");
    }

    printf("num1's value is %lf\n", num1);
    printf("num2's value is %.2f\n", num2);

    AttackCheck();

    getchar();
}

int main(void)
{
    int num = 0;
    bool online = true;
    int age = 18;
    int number = 100;

    int minutes = 2;
    int hours = 17;
    char *meridium = (hours <= 12) ? "AM" : "PM";

    printf("%s\n", (num == 0) ? "Yes" : "No");
    printf("%s\n", (online == true) ? "The player is online." : "The player is not online.");
    printf("%s\n", (age >= 18) ? "Adult" : "Children");
    printf("%s\n", (number % 2 == 0) ? "Odd" : "Even");
    printf("%02d:%02d %s", hours, minutes, meridium);

    getchar();
}

#include <stdio.h>
#include <stdlib.h>

typedef struct 
{
    char *name;
    char *race;
    int hp;
    int mp;
    int atk;
    int def;
    int level;
}Mob;

void plusPlayerGold(int *gold);

int main(void) 
{   
    int Gold = 1000;
    int *gold  = &Gold;

    *gold++;
    (*gold)++;

    Mob mobs[] = {{"Charlie", "Wolf", 100, 100, 10, 10, 1},
                  {"Hokkins", "Slime", 50, 50, 1, 1, 1},
                  {"Steve", "Orc", 200, 200, 100, 100, 50}};

    int size = sizeof(mobs) / sizeof(mobs[0]);              

    for (int i = 0; i < size; i++)
    {
        printf("Name: %-7s\nRace: %-7s\nHP: %-7d\nMP: %-7d\nATK: %-7d\nDEF: %-7d\nLevel: %-7d\n\n",
            mobs[i].name, mobs[i].race, mobs[i].hp, mobs[i].mp, mobs[i].atk, mobs[i].def, mobs[i].level);
    }


    printf("%d\n", Gold);

    printf("%d\n", &Gold);
    printf("%d\n", gold);

    getchar();
}

void plusPlayerGold(int *gold)
{
    (*gold)++;
}
```


