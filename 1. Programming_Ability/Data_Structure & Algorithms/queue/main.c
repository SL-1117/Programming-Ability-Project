#include "action_queue.h"
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    BattleAction a1 = {"Alice", "Juice", 35};
    BattleAction a2 = {"Liwei", "Tissue", 25};
    BattleAction a3 = {"Steve", "Black tea", 100};

    Queue *queue = malloc(sizeof(Queue));
    if (queue == NULL)
    {
        fprintf(stderr, "Error: memory allocation failed.");
        return 1;
    }

    queue_init(queue);

    queue_offer(queue, a1);
    queue_offer(queue, a2);
    queue_offer(queue, a3);

    BattleAction action;

    for (int i = 0; i < 2; i++)
    {
        queue_poll(queue, &action);
    }

    while (queue_poll(queue, &action))
    {
        printf("%s bought %s ($%d) in a convenience store!\n",
                action.buyer, action.item, action.price);
    }

    free(queue);

    return 0;
}