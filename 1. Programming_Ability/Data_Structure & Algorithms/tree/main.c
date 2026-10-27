#include "skill_tree.h"
#include <stdio.h>

int main(void)
{
    Skill *root = create_skill("Swordmanship", 0);
    Skill *heavy = create_skill("Heavy Slash", 1);
    Skill *quick = create_skill("Quick Strike", 2);
    Skill *basic = create_skill("Basic Attack", 3);

    if (root == NULL || heavy == NULL || quick == NULL || basic == NULL)
        return 1;

    add_skill(root, heavy);
    add_skill(root, quick);
    add_skill(root, basic);

    unlock_skill(NULL, root);
    unlock_skill(root, heavy);

    printf("root state: %d\n", root->state);
    printf("heavy state: %d\n", heavy->state);
    printf("basic state: %d\n", basic->state);

    return 0;
}