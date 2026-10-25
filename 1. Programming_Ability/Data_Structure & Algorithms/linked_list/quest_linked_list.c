#include "quest_linked_list.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

Quest *add_quest(Quest *head, int id, char name[])
{
    Quest *new_quest = malloc(sizeof(*new_quest));
    
    if (new_quest == NULL)
    {
        printf("Memory allocated failed.");
        return head;
    } 

    snprintf(new_quest->name, sizeof new_quest->name, "%s", name);
    new_quest->id = id;
    new_quest->state = ACTIVE;
    new_quest->next = head;

    return new_quest;
}

int complete_quest(Quest *head, int id)
{
    while (head != NULL)
    {
        if (head->id == id)
        {
            head->state = COMPLETED;
            return 1;
        }  

        head = head->next;
    }

    printf("Invalid ID.");

    return 0;
}

void display_quest(const Quest *head)
{
    while (head != NULL)
    {
        printf("Quest name:  %s\n"
               "Quest id:    %d\n"
               "Quest state: %s\n",
            head->name, head->id, head->state ? "completed" : "active");

        head = head->next;
    }
}

void free_quest(Quest *head)
{
    while (head != NULL)
    {
        Quest *temp = head->next;
        free(head);
        head = temp;
    }
}