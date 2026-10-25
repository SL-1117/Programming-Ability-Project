#ifndef QUEUE_H
#define QUEUE_H

#define ACTION_CAPACITY 100

typedef struct {
    char buyer[20];
    char item[30];
    int price;
} BattleAction;

typedef struct {
    BattleAction data[ACTION_CAPACITY];
    int front;
    int size;
} Queue;

void queue_init(Queue *queue);
int queue_offer(Queue *queue, BattleAction action);
int queue_poll(Queue *queue, BattleAction *action);
void queue_display(Queue *queue);
void queue_isEmpty(Queue *queue);
int queue_size(Queue *queue);
void queue_free(Queue *queue);

#endif