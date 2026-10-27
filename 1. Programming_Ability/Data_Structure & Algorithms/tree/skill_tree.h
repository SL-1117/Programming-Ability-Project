#ifndef TREE_H
#define TREE_H

#define MAX_CHILDREN 3

typedef enum
{
    LOCKED = 0,
    UNLOCKED = 1
} STATE;

typedef struct Skill Skill;

struct Skill
{
    char name[40];
    int id;
    int state;
    Skill *children[MAX_CHILDREN];
    int child_count;
};

Skill *create_skill(const char *name, int id);
int add_skill(Skill *parent, Skill *child);
int unlock_skill(Skill *prerequisite, Skill *unlock_skill);

#endif