#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

#define ABLOCK_MIN (64 * 1024)

void *arena_alloc(Arena *a, size_t sz)
{
    sz = (sz + 15) & ~(size_t)15;
    ABlock *b = a->head;
    if (!b || b->cap - b->used < sz) {
        size_t cap = sz > ABLOCK_MIN ? sz : ABLOCK_MIN;
        b = malloc(sizeof(ABlock) + cap);
        if (!b) abort();
        b->next = a->head;
        b->used = 0;
        b->cap = cap;
        a->head = b;
    }
    void *p = b->mem + b->used;
    b->used += sz;
    memset(p, 0, sz);
    return p;
}

void arena_free(Arena *a)
{
    ABlock *b = a->head;
    while (b) {
        ABlock *next = b->next;
        free(b);
        b = next;
    }
    a->head = NULL;
}
