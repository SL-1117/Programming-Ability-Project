#include "skill_tree.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

Skill *create_skill(const char *name, int id)
{
    Skill *s = malloc(sizeof(*s));
    if (s == NULL) return NULL;

    s->id = id;
    snprintf(s->name, sizeof(s->name), "%s", name ? name : "Unnamed");
    s->state = LOCKED;
    s->child_count = 0;

    for (int i = 0; i < MAX_CHILDREN; i++)
    {
        s->children[i] = NULL;
    }

    return s;
}

int add_skill(Skill *parent, Skill *child)
{
    if (parent == NULL || child == NULL)
        return 0;

    if (parent->child_count >= MAX_CHILDREN)
        return 0;

    parent->children[parent->child_count] = child;
    parent->child_count++;

    return 1;
}

int unlock_skill(Skill *prerequisite, Skill *unlock_skill)
{
    if (unlock_skill == NULL)
        return 0;

    if (prerequisite != NULL && prerequisite->state == LOCKED)
        return 0;

    unlock_skill->state = UNLOCKED;

    return 1;
}