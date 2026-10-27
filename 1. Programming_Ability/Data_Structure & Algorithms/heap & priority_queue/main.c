#include "priority_queue.h"
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    Combatant a = {
        "Garou", 1, 7
    };
    Combatant b = {
        "Ryouma", 2, 2
    };
    Combatant c = {
        "Nichola", 3, 99
    };

    MAX_Heap *h = malloc(sizeof(MAX_Heap));
    if (h == NULL)
    {
        fprintf(stderr, "Error: memory allocation failed.");
        return 1;
    }

    h->size = 0;

    insert(h, a);
    insert(h, b);
    insert(h, c);

    Combatant temp;

    while (queue_remove(h, &temp))
    {
        printf("%s's id is %d.\n", 
                temp.name, temp.id);
    }

    free(h);

    return 0;
}