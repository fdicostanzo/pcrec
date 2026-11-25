#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

#define ABLOCK_MIN (64 * 1024)

/* Allocates `sz` bytes (rounded up to 16) from the arena's current block,
 * opening a new BLOCK via malloc when the current one has no room; the
 * returned memory is zeroed. On malloc failure this diagnoses through
 * pcrec_ctx_nomem when the arena has a Ctx, then aborts -- a detached arena
 * (no Ctx) has no error channel to diagnose through. */
void *pcrec_arena_alloc(Arena *a, size_t sz)
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
            if (a->cx) pcrec_ctx_nomem(a->cx);
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

/* [K155] The ownership record, from the arena itself: allocated before the
 * heap block it will hold exists (see internal.h). */
AOwn *pcrec_arena_own_slot(Arena *a)
{
    return pcrec_arena_alloc(a, sizeof(AOwn));
}

/* [K155] Links `heap` (may be NULL) into `slot`: the arena frees it. No
 * allocation, so nothing can refuse between a callee returning the block
 * and the arena owning it. */
void pcrec_arena_own(Arena *a, AOwn *slot, void *heap)
{
    slot->p = heap;
    slot->next = a->owned;
    a->owned = slot;
}

/* Frees every block the arena holds (its owned heap blocks first: their
 * records live in the blocks) and resets it to empty; the arena's one
 * teardown, called on both the success path and every longjmp'd refusal. */
void pcrec_arena_free(Arena *a)
{
    for (AOwn *o = a->owned; o; o = o->next) free(o->p);
    a->owned = NULL;
    ABlock *b = a->head;
    while (b) {
        ABlock *next = b->next;
        free(b);
        b = next;
    }
    a->head = NULL;
}
