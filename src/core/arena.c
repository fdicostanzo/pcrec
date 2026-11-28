#include <stddef.h>
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

#define ABLOCK_MIN (64 * 1024)

/* ---- the registry ([ARENA-SCOPES], docs/design/arena_scopes.md) ----
 *
 * One LIFO list per Arena (`top`, newest first) of ENTRY records, each a
 * resource of one KIND from the table below, released by that kind's
 * function. A SCOPE is a MARK record in the list; closing it releases every
 * entry above it, newest first. Entries pushed while no scope is open are
 * the HOLDS (`pcrec_arena_hold`), the list's bottom. `pcrec_arena_free`
 * releases the whole list before the blocks, so every teardown releases
 * whatever a longjmp left open. Records are heap (one `calloc` each, sized by
 * kind, freed at release): never from the arena's own blocks, and no
 * function in this file calls `pcrec_arena_alloc` (the test link wraps it,
 * and a call from inside this file would bypass the wrap). */

/* An entry's kind: its payload size and its release, which never allocates
 * and never refuses (it runs inside a teardown). A new row is a design
 * change, reviewed, never a local addition. */
struct LKind {
    size_t size;
    void (*release)(void *storage);
};

struct LEnt {
    LEnt *next;
    const struct LKind *kind;
    _Alignas(max_align_t) unsigned char payload[];
};

/* A MARK's payload: the mark it hides (`prev_open`), its stamp, and the
 * record under it when it was pushed (the close's stop and post-condition). */
typedef struct {
    LEnt    *prev_open;
    uint64_t gen;
    LEnt    *below;
} MarkPay;

static void release_none(void *storage) { (void)storage; }
static void release_heap(void *storage) { free(*(void **)storage); }
static void release_strbuf(void *storage) { pcrec_sb_free(storage); }
static void release_arena(void *storage) { pcrec_arena_free(storage); }

/* THE KIND TABLE (design "API", the kind table) */
static const struct LKind kind_mark   = { sizeof(MarkPay), release_none };
static const struct LKind kind_heap   = { sizeof(void *),  release_heap };
static const struct LKind kind_strbuf = { sizeof(StrBuf),  release_strbuf };
static const struct LKind kind_arena  = { sizeof(Arena),   release_arena };

static MarkPay *mark_pay(LEnt *m) { return (MarkPay *)(void *)m->payload; }

/* The one error-channel read for a refusal or nomem made through an Arena's
 * or a StrBuf's `.cx` in arena.c and sb.c, called unconditionally by every
 * allocating entry that holds a channel (D-7, internal.h). Returns `cx` and
 * counts one use, lent or not (counted, never failed): the lender reads the
 * uses made while `cx` was LENT (a nested part compile runs under it,
 * [K163]) as the difference from its snapshot, so the hot path is one add
 * and no flag read. NULL (a detached arena) is legal and counts nothing.
 * vm_stmt.c's and enc.c's `sb->cx` refusals read the Ctx directly. */
Ctx *pcrec_err_chan(Ctx *cx)
{
    if (cx) cx->chan_uses++;
    return cx;
}

/* [K163] THE LENT PAIR (D-7, D-4's order): compound.c `walk_part` lends its
 * Ctx around a part compile and refuses at its own point on a nonzero count,
 * after both of its holds are stored, so the refusal strands nothing. */
void pcrec_ctx_lend(Ctx *cx)
{
    cx->lent = true;
    cx->lent_base = cx->chan_uses;
}

unsigned pcrec_ctx_unlend(Ctx *cx)
{
    uint64_t n = cx->chan_uses - cx->lent_base;
    cx->lent = false;
    return n > UINT_MAX ? UINT_MAX : (unsigned)n;
}

bool pcrec_ctx_lent_p(const Ctx *cx)
{
    return cx && cx->lent;
}

/* An internal-error refusal from the registry: diagnosed through the
 * arena's compile when it has one, an abort on a detached arena. */
__attribute__((noreturn)) static void reg_fail(const Arena *a, const char *why)
{
    if (a && a->cx)
        pcrec_ctx_fail(pcrec_err_chan(a->cx), 0, "internal error: arena registry: %s", why);
    abort();
}

/* An out-of-memory refusal: diagnosed through the arena's compile when it
 * has one, an abort on a detached arena. Out of line and cold so the
 * allocation paths keep no channel live across their malloc (lane f4flag:
 * `pcrec_arena_alloc` had held `a->cx` in a saved register for this;
 * `noipa`, not `noinline`: IPA-SRA would pass `a->cx` in and undo it). */
__attribute__((noreturn, cold, noipa)) static void arena_nomem(const Arena *a)
{
    if (a->cx) pcrec_ctx_nomem(pcrec_err_chan(a->cx));
    abort();
}

/* A fresh zeroed record of `kind`, not yet linked: the one step of a
 * registration that can fail, taken while there is nothing yet to lose. */
static LEnt *rec_take(Arena *a, const struct LKind *kind)
{
    (void)pcrec_err_chan(a->cx);   /* D-7: a use, counted while lent */
    LEnt *e = calloc(1, offsetof(LEnt, payload) + kind->size);
    if (!e) {
        arena_nomem(a);
    }
    e->kind = kind;
    return e;
}

/* Links `e` on top of the registry. */
static void rec_push(Arena *a, LEnt *e)
{
    e->next = a->top;
    a->top = e;
}

/* Releases one unlinked record: its kind's resource, then the record. */
static void rec_release(LEnt *e)
{
    e->kind->release(e->payload);
    free(e);
}

/* L1: `s` names the innermost open scope of its arena, with that scope's
 * stamp. `a->open` is tested first, and only the LIVE mark is read: a
 * closed handle's `mark` may be freed memory. */
static void scope_check(const Scope *s)
{
    Arena *a = s->a;
    if (!a) abort();
    if (!(a->open && a->open == s->mark && mark_pay(a->open)->gen == s->gen))
        reg_fail(a, "a scope handle that is not the innermost open scope");
}

Scope pcrec_scope_open(Arena *a)
{
    if (a->child) reg_fail(a, "a scope opened on a scope's child arena");
    LEnt *m = rec_take(a, &kind_mark);
    MarkPay *mp = mark_pay(m);
    mp->prev_open = a->open;
    mp->gen = ++a->gen;
    mp->below = a->top;
    rec_push(a, m);
    a->open = m;
    return (Scope){ a, m, mp->gen };
}

/* Releases records from the top down to and including `mark`. */
static void release_to_mark(Arena *a, LEnt *mark)
{
    for (;;) {
        LEnt *e = a->top;
        bool last = e == mark;
        a->top = e->next;
        rec_release(e);
        if (last) break;
    }
}

void pcrec_scope_close(Scope *s)
{
    scope_check(s);
    Arena *a = s->a;
    LEnt *below = mark_pay(s->mark)->below, *prev = mark_pay(s->mark)->prev_open;
    release_to_mark(a, s->mark);
    a->open = prev;
    if (a->top != below)
        reg_fail(a, "a scope's close did not release down to its mark");
}

/* Pushes a HEAP entry for scope `s` and gives it `n` bytes (never fewer than
 * one): the record is linked holding NULL before the block exists, so a
 * failure of the block strands nothing. */
void *pcrec_scope_malloc(Scope *s, size_t n)
{
    scope_check(s);
    Arena *a = s->a;
    LEnt *e = rec_take(a, &kind_heap);
    rec_push(a, e);
    void *p = malloc(n ? n : 1);
    if (!p) {
        arena_nomem(a);
    }
    *(void **)(void *)e->payload = p;
    return p;
}

void *pcrec_scope_calloc(Scope *s, size_t n, size_t sz)
{
    if (sz && n > SIZE_MAX / sz) {
        scope_check(s);
        arena_nomem(s->a);
    }
    void *p = pcrec_scope_malloc(s, n * sz);
    memset(p, 0, n * sz);
    return p;
}

void pcrec_scope_free(Scope *s, void *p)
{
    scope_check(s);
    Arena *a = s->a;
    LEnt *prev = NULL;
    for (LEnt *e = a->top; e != s->mark; prev = e, e = e->next) {
        if (e->kind != &kind_heap || *(void **)(void *)e->payload != p) continue;
        if (prev) prev->next = e->next;
        else a->top = e->next;
        rec_release(e);
        return;
    }
    reg_fail(a, "pcrec_scope_free of a block the innermost scope does not own");
}

StrBuf *pcrec_scope_sb(Scope *s)
{
    scope_check(s);
    Arena *a = s->a;
    LEnt *e = rec_take(a, &kind_strbuf);
    rec_push(a, e);
    StrBuf *sb = (StrBuf *)(void *)e->payload;
    sb->cx = a->cx;
    return sb;
}

Arena *pcrec_scope_arena(Scope *s)
{
    scope_check(s);
    Arena *a = s->a;
    LEnt *e = rec_take(a, &kind_arena);
    rec_push(a, e);
    Arena *c = (Arena *)(void *)e->payload;
    c->cx = a->cx;
    c->child = true;
    return c;
}

void pcrec_scope_unwind(Arena *a)
{
    while (a->open) {
        Scope s = { a, a->open, mark_pay(a->open)->gen };
        pcrec_scope_close(&s);
    }
}

void pcrec_scope_check_closed(Arena *a)
{
    if (a->open) reg_fail(a, "a scope left open at the end of a successful attempt");
}

bool pcrec_arena_open_p(const Arena *a)
{
    return a->open != NULL;
}

void **pcrec_arena_hold(Arena *a)
{
    if (a->open) reg_fail(a, "pcrec_arena_hold while a scope is open");
    LEnt *e = rec_take(a, &kind_heap);
    rec_push(a, e);
    return (void **)(void *)e->payload;
}

/* Allocates `sz` bytes (rounded up to 16) from the arena's current block,
 * opening a new BLOCK via malloc when the current one has no room; the
 * returned memory is zeroed. On malloc failure this diagnoses through
 * pcrec_ctx_nomem when the arena has a Ctx, then aborts -- a detached arena
 * (no Ctx) has no error channel to diagnose through. */
void *pcrec_arena_alloc(Arena *a, size_t sz)
{
    (void)pcrec_err_chan(a->cx);   /* D-7: a use, counted while lent, block or not */
    sz = (sz + 15) & ~(size_t)15;
    ABlock *b = a->head;
    if (!b || b->cap - b->used < sz) {
        size_t cap = sz > ABLOCK_MIN ? sz : ABLOCK_MIN;
        b = malloc(sizeof(ABlock) + cap);
        /* [M4.7b/K7] A library must not kill its caller. The arena belongs to
         * a Ctx, so a failure here is an ordinary diagnosed refusal: the
         * longjmp lands in compile_driver, which frees this arena wholesale
         * along with the Job's heap arrays (the arena's Ctx is the running
         * one: a use through a lent Ctx is counted above and refused by its
         * lender, [K163]). Nothing allocated so far leaks and
         * nothing half-built is ever read again. */
        if (!b) {
            arena_nomem(a);
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

/* Releases the arena's whole registry (open scopes, their entries and the
 * holds, newest first), then frees every block, and resets it to empty but
 * for `cx` and `child`; the arena's one teardown, called on both the success
 * path and every longjmp'd refusal. */
void pcrec_arena_free(Arena *a)
{
    while (a->top) {
        LEnt *e = a->top;
        a->top = e->next;
        rec_release(e);
    }
    a->open = NULL;
    a->gen = 0;
    ABlock *b = a->head;
    while (b) {
        ABlock *next = b->next;
        free(b);
        b = next;
    }
    a->head = NULL;
}
