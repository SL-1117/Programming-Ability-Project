#ifndef PRIORITY_QUEUE_H
#define PRIORITY_QUEUE_H

#define MAX_COMBATANTS 40

typedef struct 
{
    char name[30];
    int id;
    int initiative;
} Combatant;

typedef struct
{
    Combatant data[MAX_COMBATANTS];
    int size;
} MAX_Heap;

int insert(MAX_Heap *h, Combatant combatant);
int queue_remove(MAX_Heap *h, Combatant *removed_combatant);


#endif