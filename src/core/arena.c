#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

#define ABLOCK_MIN (64 * 1024)

/* ---- the registry ([ARENA-SCOPES], docs/design/arena_scopes.md) ----
 *
 * One LIFO STACK per Arena of ENTRY records, each a resource of one KIND from
 * the table below, released by that kind's function. The stack is ONE heap
 * array (`rec`, `n` used of `cap`, oldest first), grown by doubling, popped
 * on close and freed by `pcrec_arena_free`: no per-record allocation (ruling
 * R-3 of lane arenabuild2, a design deviation: per-record calloc/free moved
 * the 8 MiB growth rung). A SCOPE is a MARK record in the stack; closing it
 * pops and releases every entry above it, newest first. Entries pushed while
 * no scope is open are the HOLDS (`pcrec_arena_hold`), the stack's bottom.
 * `pcrec_arena_free` releases the whole stack before the blocks, so every
 * teardown releases whatever a longjmp left open.
 *
 * The array moves when it grows, so nothing outside this file holds a record
 * address: a handle (a Scope, an ArenaHold) names its record by POSITION
 * (index + 1; 0 is "none") and generation stamp, and an entry's storage (a
 * heap block, a StrBuf, a child Arena) is a heap object of its own that the
 * record points to, so a pointer the client holds survives every growth.
 * No function in this file calls `pcrec_arena_alloc` (the test link wraps
 * it, and a call from inside this file would bypass the wrap). */

/* An entry's kind: the size of the heap object its storage is (0: the
 * storage is the client's own block, or none), and its release, which never
 * allocates and never refuses (it runs inside a teardown) and takes NULL (a
 * record pushed before its object exists). A new row is a design change,
 * reviewed, never a local addition. */
struct LKind {
    size_t size;
    void (*release)(void *storage);
};

/* A record: its kind, its storage, and for a MARK or a hold its stamp; a
 * MARK also keeps the mark it hides (`prev_open`, a position, 0 = none). */
struct LEnt {
    const struct LKind *kind;
    void    *p;
    uint64_t gen;
    size_t   prev_open;
};

static void release_none(void *storage) { (void)storage; }
static void release_heap(void *storage) { free(storage); }
static void release_strbuf(void *storage)
{
    if (storage) pcrec_sb_free(storage);
    free(storage);
}
static void release_arena(void *storage)
{
    if (storage) pcrec_arena_free(storage);
    free(storage);
}

/* THE KIND TABLE (design "API", the kind table) */
static const struct LKind kind_mark   = { 0,              release_none };
static const struct LKind kind_heap   = { 0,              release_heap };
static const struct LKind kind_strbuf = { sizeof(StrBuf), release_strbuf };
static const struct LKind kind_arena  = { sizeof(Arena),  release_arena };

/* The record at position `h` (index + 1). Valid until the next push. */
static LEnt *rec_at(const Arena *a, size_t h) { return &a->rec[h - 1]; }

/* The one error-channel read for a refusal or nomem made through an Arena's
 * or a StrBuf's `.cx` (D-7). Returns `cx`; NULL (a detached arena) is legal. */
Ctx *pcrec_err_chan(Ctx *cx)
{
    return cx;
}

/* An internal-error refusal from the registry: diagnosed through the
 * arena's compile when it has one, an abort on a detached arena. */
__attribute__((noreturn)) static void reg_fail(const Arena *a, const char *why)
{
    if (a && a->cx)
        pcrec_ctx_fail(pcrec_err_chan(a->cx), 0, "internal error: arena registry: %s", why);
    abort();
}

/* A nomem from the registry: through the arena's compile, else an abort. */
__attribute__((noreturn)) static void reg_nomem(const Arena *a)
{
    if (a->cx) pcrec_ctx_nomem(pcrec_err_chan(a->cx));
    abort();
}

/* Pushes a zeroed record of `kind` (storage NULL) and returns its position:
 * the one step of a registration that can fail (the array's growth), taken
 * while there is nothing yet to lose. The first growth takes 16 records:
 * minimize, the one client at F1, peaks at 9 (its mark and 8 tables), so one
 * allocation serves an attempt (derived from that count, not measured). */
static size_t rec_take(Arena *a, const struct LKind *kind)
{
    if (a->n == a->cap) {
        size_t cap = a->cap ? a->cap * 2 : 16;
        LEnt *r = cap > SIZE_MAX / sizeof *r ? NULL : realloc(a->rec, cap * sizeof *r);
        if (!r) reg_nomem(a);
        a->rec = r;
        a->cap = cap;
    }
    a->rec[a->n] = (LEnt){ .kind = kind };
    return ++a->n;
}

/* Gives the record at `h` its kind's heap object (zeroed): the record is
 * already pushed holding NULL, so a failure here strands nothing. */
static void *rec_obj(Arena *a, size_t h)
{
    void *o = calloc(1, rec_at(a, h)->kind->size);
    if (!o) reg_nomem(a);
    rec_at(a, h)->p = o;
    return o;
}

/* Pops and releases records, newest first, until `n` remain. */
static void release_above(Arena *a, size_t n)
{
    while (a->n > n) {
        LEnt *e = &a->rec[--a->n];
        e->kind->release(e->p);
    }
}

/* L1: `s` names the innermost open scope of its arena, with that scope's
 * stamp. `a->open` is tested first, and only the LIVE mark is read. */
static void scope_check(const Scope *s)
{
    Arena *a = s->a;
    if (!a) abort();
    if (!(a->open && a->open == s->mark && rec_at(a, a->open)->gen == s->gen))
        reg_fail(a, "a scope handle that is not the innermost open scope");
}

Scope pcrec_scope_open(Arena *a)
{
    if (a->child) reg_fail(a, "a scope opened on a scope's child arena");
    size_t m = rec_take(a, &kind_mark);
    LEnt *e = rec_at(a, m);
    e->prev_open = a->open;
    e->gen = ++a->gen;
    a->open = m;
    return (Scope){ a, m, e->gen };
}

void pcrec_scope_close(Scope *s)
{
    scope_check(s);
    Arena *a = s->a;
    size_t prev = rec_at(a, s->mark)->prev_open;
    release_above(a, s->mark - 1);
    a->open = prev;
    if (a->n != s->mark - 1)
        reg_fail(a, "a scope's close did not release down to its mark");
}

/* Pushes a HEAP entry for scope `s` and gives it `n` bytes (never fewer than
 * one): the record is pushed holding NULL before the block exists, so a
 * failure of the block strands nothing. */
void *pcrec_scope_malloc(Scope *s, size_t n)
{
    scope_check(s);
    Arena *a = s->a;
    size_t h = rec_take(a, &kind_heap);
    void *p = malloc(n ? n : 1);
    if (!p) reg_nomem(a);
    rec_at(a, h)->p = p;
    return p;
}

void *pcrec_scope_calloc(Scope *s, size_t n, size_t sz)
{
    if (sz && n > SIZE_MAX / sz) {
        scope_check(s);
        reg_nomem(s->a);
    }
    void *p = pcrec_scope_malloc(s, n * sz);
    memset(p, 0, n * sz);
    return p;
}

/* L6: only the innermost scope's own HEAP entries are candidates (the
 * search stops at its mark, and above the innermost mark there is no
 * other mark); the entries above the one released close up over it. */
void pcrec_scope_free(Scope *s, void *p)
{
    scope_check(s);
    Arena *a = s->a;
    for (size_t h = a->n; h > s->mark; h--) {
        LEnt *e = rec_at(a, h);
        if (e->kind != &kind_heap || e->p != p) continue;
        LEnt dead = *e;
        memmove(e, e + 1, (a->n - h) * sizeof *e);
        a->n--;
        dead.kind->release(dead.p);
        return;
    }
    reg_fail(a, "pcrec_scope_free of a block the innermost scope does not own");
}

StrBuf *pcrec_scope_sb(Scope *s)
{
    scope_check(s);
    Arena *a = s->a;
    StrBuf *sb = rec_obj(a, rec_take(a, &kind_strbuf));
    sb->cx = a->cx;
    return sb;
}

Arena *pcrec_scope_arena(Scope *s)
{
    scope_check(s);
    Arena *a = s->a;
    Arena *c = rec_obj(a, rec_take(a, &kind_arena));
    c->cx = a->cx;
    c->child = true;
    return c;
}

void pcrec_scope_unwind(Arena *a)
{
    while (a->open) {
        Scope s = { a, a->open, rec_at(a, a->open)->gen };
        pcrec_scope_close(&s);
    }
}

void pcrec_scope_check_closed(Arena *a)
{
    if (a->open) reg_fail(a, "a scope left open at the end of a successful attempt");
}

bool pcrec_arena_open_p(const Arena *a)
{
    return a->open != 0;
}

ArenaHold pcrec_arena_hold(Arena *a)
{
    if (a->open) reg_fail(a, "pcrec_arena_hold while a scope is open");
    size_t h = rec_take(a, &kind_heap);
    LEnt *e = rec_at(a, h);
    e->gen = ++a->gen;
    return (ArenaHold){ a, h, e->gen };
}

void pcrec_hold_set(ArenaHold *h, void *p)
{
    Arena *a = h->a;
    if (!a) abort();
    if (!(h->rec && h->rec <= a->n && rec_at(a, h->rec)->kind == &kind_heap &&
          rec_at(a, h->rec)->gen == h->gen && !rec_at(a, h->rec)->p))
        reg_fail(a, "a hold handle that names no empty hold of its arena");
    rec_at(a, h->rec)->p = p;
}

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
            if (a->cx) pcrec_ctx_nomem(pcrec_err_chan(a->cx));
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

/* Releases the arena's whole registry (open scopes, their entries and the
 * holds, newest first) and frees its array, then frees every block, and
 * resets it to empty but for `cx` and `child`; the arena's one teardown,
 * called on both the success path and every longjmp'd refusal. */
void pcrec_arena_free(Arena *a)
{
    release_above(a, 0);
    free(a->rec);
    a->rec = NULL;
    a->n = a->cap = 0;
    a->open = 0;
    a->gen = 0;
    ABlock *b = a->head;
    while (b) {
        ABlock *next = b->next;
        free(b);
        b = next;
    }
    a->head = NULL;
}
