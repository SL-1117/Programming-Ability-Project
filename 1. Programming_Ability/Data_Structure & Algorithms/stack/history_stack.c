#include "history_stack.h"
#include <stdio.h>
#include <string.h>


int push(Stack *stack, BattleAction action)
{
    if (stack == NULL || stack->top < -1 ||
        stack->top >= HISTORY_CAPACITY - 1)
        return 1;

    stack->data[++stack->top] = action;

    return 0;
}


int pop(Stack *stack, BattleAction *last_action)
{
    if (stack == NULL || last_action == NULL || stack->top < 0)
        return 0;

    *last_action = stack->data[stack->top--];
    
    return 1;
}


void Init_stack(Stack *stack)
{
    if (stack != NULL)
        stack->top = -1;
}