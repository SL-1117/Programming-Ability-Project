#include "action_queue.h"
#include <stdio.h>
#include <stdlib.h>


void queue_init(Queue *queue)
{
    queue->size = 0;
    queue->front = 0;
}


int queue_offer(Queue *queue, BattleAction action)
{
    if (queue->size >= ACTION_CAPACITY)
        return 0;

    int rear = (queue->front + queue->size) % ACTION_CAPACITY;

    queue->data[rear] = action;
    queue->size++;

    return 1;
}


int queue_poll(Queue *queue, BattleAction *last_action)
{
    if (queue->size <= 0)
        return 0;

    *last_action = queue->data[queue->front];

    queue->front = (queue->front + 1) % ACTION_CAPACITY;
    queue->size--;
    
    return 1;
}


void queue_display(Queue *queue);
void queue_isEmpty(Queue *queue);
int queue_size(Queue *queue);
