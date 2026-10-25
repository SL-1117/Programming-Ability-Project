#include "history_stack.h"
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int player_hp = 10;
    int potion_restore = 70;
    
    Stack *stack = malloc(sizeof(Stack));
    if (stack == NULL)
        return 0;

    Init_stack(stack);

    BattleAction action1 = {
        .name = "Drink Potion",
        .old_value = 30,
        .new_value = 30 + potion_restore
    };

    if (push(stack, action1) != 0)
    {
        fprintf(stderr, "Failed to push action onto history stack.\n");
        return 1;
    }

    BattleAction action2 = {
        .name = "Got hit by duragon",
        .old_value = 100,
        .new_value = 10
    };
    
    BattleAction action3 = {
        .name = "Soaked into a devine foundation",
        .old_value = 10,
        .new_value = 3000
    };

    push(stack, action2);
    push(stack, action3);

    BattleAction action;

    while (pop(stack, &action))
    {
        printf("\n[Action]: %s\n"
               "[Player_hp]: %d\n",
                action.name, action.new_value);
    }

    free(stack);
    
    return 0;
}
