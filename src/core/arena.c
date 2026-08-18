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
        /* [M4.7b/K7] A library must not kill its caller. The arena belongs to
         * a Ctx, so a failure here is an ordinary diagnosed refusal: the
         * longjmp lands in compile_driver, which frees this arena wholesale
         * along with the Job's heap arrays. Nothing allocated so far leaks and
         * nothing half-built is ever read again. */
        if (!b) {
            if (a->cx) ctx_nomem(a->cx);
            abort();
        }
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
