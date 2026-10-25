#ifndef STACK_H
#define STACK_H

#define HISTORY_CAPACITY 100

typedef struct {
    char name[100];
    int old_value;
    int new_value;
} BattleAction;

typedef struct {
    BattleAction data[HISTORY_CAPACITY];
    int top;
} Stack;

void Init_stack(Stack *stack);
int push(Stack *stack, BattleAction action);
int pop(Stack *stack, BattleAction *last_action);

#endif