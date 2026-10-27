#include "priority_queue.h"
#include <stdio.h>


void swap(Combatant *a, Combatant *b)
{
    Combatant temp = *a;
    *a = *b;
    *b = temp;
}


int insert(MAX_Heap *h, Combatant combatant)
{
    if (h->size >= MAX_COMBATANTS)
        return 0;

    int rear = h->size;
    h->data[rear] = combatant;
    h->size++;

    while (rear > 0)
    {
        int parent = (rear - 1) / 2;

        if (h->data[parent].initiative >= h->data[rear].initiative)
            break;

        swap(&h->data[parent], &h->data[rear]);

        rear = parent;
    }

    return 1;
}


int queue_remove(MAX_Heap *h, Combatant *removed_combatant)
{
    // Check if there is no element in the heap
    if (h->size == 0)
        return 0;

    // Store the element that we r gonna remove and remove it
    *removed_combatant = h->data[0];
    h->size--;

    // Check is there any element to replace the data[0]
    // if denied, it means there is only 1 element in this heap
    if (h->size == 0)
        return 1;

    // Move the last element to the top of the heap
    h->data[0] = h->data[h->size];

    // Start swaping one side of the tree
    int parent = 0;

    while (1)
    {
        // Define the children and the parent's index
        int left = (parent * 2) + 1;
        int right = (parent * 2) + 2;
        int largest = parent;

        // Check if the parent has the left or right child
        // if there is no child, we js go straight up to the third if logic
        if (left < h->size && h->data[left].initiative > h->data[largest].initiative)
            largest = left;

        if (right < h->size && h->data[right].initiative > h->data[largest].initiative)
            largest = right;

        if (parent == largest)
            break;

        swap(&h->data[largest], &h->data[parent]);

        /* The index of the largest has to become 
             the parent for next loop that we r gonna check */
        parent = largest;
    }

    return 1;
}