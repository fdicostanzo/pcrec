/* tests/core/scope_check.c — [ARENA-SCOPES] F1: the registry's LIFO rules on a
 * DETACHED arena (cx NULL), below any compile (docs/design/arena_scopes.md D-2,
 * "THE DRILLS"; Discipline rows L1, L5, L6, L7).
 *
 * A refusal on a detached arena ABORTS, so every refusing step runs in its OWN
 * forked child, which must die by SIGABRT; the parent keeps the state from
 * before the step (fork copies it), so the drill continues past refusing steps
 * exactly as the design's tables read. A step that must NOT refuse runs in the
 * parent and its registry is checked through the handles and `a.n`/`a.open`.
 *
 * Records live in ONE array and handles name them by POSITION (lane
 * arenabuild2, ruling R-3), so a reopen at the same depth ALWAYS reuses the
 * closed mark's position: the real stale handle names the live mark, and the
 * stamp compare is the only thing that can refuse it (sabotage S3597, the
 * stamp compare dropped, must turn this drill into a FAIL). Step 6 also
 * FORGES the handle (the live position, the old stamp), as the design asks.
 * `growth` checks that handles and storage pointers survive the array's
 * growth. */
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

#include "core/internal.h"

static int pass_n, fail_n;

static void ok(const char *what) { printf("PASS: %s\n", what); pass_n++; }
static void bad(const char *what) { fprintf(stderr, "FAIL: %s\n", what); fail_n++; }
static void expect(int cond, const char *what) { if (cond) ok(what); else bad(what); }

/* Runs `step` in a forked child: true iff the child died by SIGABRT (the
 * detached arena's refusal). */
#define REFUSES(what, step) do {                                              \
        fflush(stdout); fflush(stderr);                                       \
        pid_t pid_ = fork();                                                  \
        if (pid_ == 0) { step; _exit(0); }                                    \
        int st_ = 0;                                                          \
        waitpid(pid_, &st_, 0);                                               \
        expect(WIFSIGNALED(st_) && WTERMSIG(st_) == SIGABRT, what);          \
    } while (0)

static void stale_handle_drill(void)
{
    Arena a = { 0 };
    Scope s1 = pcrec_scope_open(&a);                       /* step 1 */
    void *p = pcrec_scope_malloc(&s1, 8);                  /* step 2 */
    expect(p && a.open == s1.mark && s1.gen == 1 && a.n == 2, "stale drill 1-2: S1 open at g1, e(p) registered");
    pcrec_scope_close(&s1);                                /* step 3 */
    expect(!a.n && !a.open && a.gen == 1, "stale drill 3: close(S1) empties the registry, gen stays 1");
    Scope s2 = pcrec_scope_open(&a);                       /* step 4 */
    void *q = pcrec_scope_malloc(&s2, 8);                  /* step 5 */
    expect(q && s2.gen == 2 && a.open == s2.mark, "stale drill 4-5: S2 open at g2, e(q) registered");
    /* step 6, forged: the LIVE mark's address with S1's old stamp */
    Scope forged = { &a, s2.mark, s1.gen };
    REFUSES("stale drill 6 (forged handle: live mark address, old stamp): close REFUSED",
            pcrec_scope_close(&forged));
    REFUSES("stale drill 6 (forged handle): a registering call REFUSED",
            pcrec_scope_malloc(&forged, 8));
    expect(s1.mark == s2.mark, "stale drill 4: the reopen reuses the closed mark's position (the reuse precondition)");
    REFUSES("stale drill 6 (the real stale handle, same position): close REFUSED", pcrec_scope_close(&s1));
    expect(a.open == s2.mark && a.n == s2.mark + 1, "stale drill 6: e(q) still S2's after the refusals");
    pcrec_scope_close(&s2);
    expect(!a.n && !a.open, "stale drill: close(S2) releases e(q) and m2");
    pcrec_arena_free(&a);
}

static void free_the_mark_drill(void)
{
    Arena a = { 0 };
    Scope s1 = pcrec_scope_open(&a);                       /* step 1 */
    void *p1 = pcrec_scope_malloc(&s1, 8);
    Scope s2 = pcrec_scope_open(&a);                       /* step 2 */
    void *p2 = pcrec_scope_malloc(&s2, 8);
    expect(a.open == s2.mark, "free-the-mark 1-2: S2 innermost");
    REFUSES("free-the-mark 3: scope_free(&S1, p1) while S2 is innermost REFUSED", pcrec_scope_free(&s1, p1));
    REFUSES("free-the-mark 3b: scope_malloc(&S1) while S2 is innermost REFUSED", pcrec_scope_malloc(&s1, 8));
    REFUSES("free-the-mark 3b: scope_sb(&S1) while S2 is innermost REFUSED", pcrec_scope_sb(&s1));
    REFUSES("free-the-mark 3b: scope_arena(&S1) while S2 is innermost REFUSED", pcrec_scope_arena(&s1));
    REFUSES("free-the-mark 3b: scope_calloc(&S1) while S2 is innermost REFUSED", pcrec_scope_calloc(&s1, 1, 8));
    REFUSES("free-the-mark 3b: close(&S1) while S2 is innermost REFUSED", pcrec_scope_close(&s1));
    {
        Arena b = { 0 };
        Scope z = { &b, 0, 0 };
        REFUSES("free-the-mark 3c: a zero handle with no scope open REFUSED", pcrec_scope_malloc(&z, 8));
    }
    REFUSES("free-the-mark 4: scope_free(&S2, p1) (S1's entry, below S2's mark) REFUSED", pcrec_scope_free(&s2, p1));
    size_t m2 = s2.mark;
    pcrec_scope_free(&s2, p2);                             /* step 5 */
    expect(a.n == m2, "free-the-mark 5: scope_free(&S2, p2) unlinks e(p2); m2 is the top");
    pcrec_scope_close(&s2);                                /* step 6 */
    expect(a.open == s1.mark && a.n == s1.mark + 1, "free-the-mark 6: close(S2) frees m2 only; S1 innermost, e(p1) on top");
    pcrec_scope_close(&s1);                                /* step 7 */
    expect(!a.n && !a.open, "free-the-mark 7: close(S1) frees e(p1) and m1");
    pcrec_arena_free(&a);
}

static void hold_rule(void)
{
    Arena a = { 0 };
    ArenaHold h = pcrec_arena_hold(&a);
    expect(h.a == &a && h.rec == 1 && h.gen && a.n == 1, "L7: a hold with no scope open is a stamped bottom record");
    ArenaHold forged = { &a, h.rec, h.gen + 1 };
    REFUSES("hold: pcrec_hold_set through a handle with a wrong stamp REFUSED", pcrec_hold_set(&forged, NULL));
    ArenaHold none = { &a, 0, 0 };
    REFUSES("hold: pcrec_hold_set through a zero handle REFUSED", pcrec_hold_set(&none, NULL));
    pcrec_hold_set(&h, malloc(16));
    REFUSES("hold: a second pcrec_hold_set (it would strand the first) REFUSED", pcrec_hold_set(&h, NULL));
    Scope s = pcrec_scope_open(&a);
    REFUSES("L7: pcrec_arena_hold while a scope is open REFUSED", pcrec_arena_hold(&a));
    pcrec_scope_close(&s);
    expect(a.n == 1 && !a.open, "L7: the hold survives the scope's close");
    pcrec_arena_free(&a);
    expect(!a.n && !a.rec && !a.head, "teardown: pcrec_arena_free releases the hold");
}

static void child_rule(void)
{
    Arena a = { 0 };
    Scope s = pcrec_scope_open(&a);
    Arena *c = pcrec_scope_arena(&s);
    expect(c && c->child && !c->head, "ARENA entry: a child, no block until first use");
    (void)pcrec_arena_alloc(c, 32);
    StrBuf *sb = pcrec_scope_sb(&s);
    pcrec_sb_puts(sb, "text");
    expect(sb->p && !sb->ar, "STRBUF entry: a heap StrBuf");
    REFUSES("L5: pcrec_scope_open on a child arena REFUSED", pcrec_scope_open(c));
    pcrec_scope_close(&s);
    expect(!a.n && !a.open, "close releases the child arena and the StrBuf");
    pcrec_arena_free(&a);
}

/* D-6: `pcrec_sb_adopt` moves HEAP storage only; arena storage handed to
 * `free` is refused (sabotage S3601 drops the check). */
static void adopt_rule(void)
{
    Arena a = { 0 };
    StrBuf ar = pcrec_sb_scratch(&a);
    pcrec_sb_puts(&ar, "arena");
    StrBuf h = { 0 };
    pcrec_sb_puts(&h, "heap");
    REFUSES("D-6: pcrec_sb_adopt of arena storage (src) REFUSED", pcrec_sb_adopt(&h, &ar));
    REFUSES("D-6: pcrec_sb_adopt into arena storage (dst) REFUSED", pcrec_sb_adopt(&ar, &h));
    StrBuf d = { 0 };
    pcrec_sb_puts(&d, "old");
    pcrec_sb_adopt(&d, &h);
    expect(d.len == 4 && !memcmp(d.p, "heap", 4) && !h.p && !h.len && !h.cap,
           "D-6: pcrec_sb_adopt moves heap storage and empties the source");
    pcrec_sb_free(&d);
    pcrec_arena_free(&a);
}

static void teardown_unwind(void)
{
    Arena a = { 0 };
    ArenaHold h = pcrec_arena_hold(&a);
    pcrec_hold_set(&h, malloc(8));
    Scope s1 = pcrec_scope_open(&a);
    (void)pcrec_scope_malloc(&s1, 64);
    Scope s2 = pcrec_scope_open(&a);
    (void)pcrec_scope_sb(&s2);
    (void)s2;
    pcrec_scope_unwind(&a);
    expect(!a.open && a.n == 1, "unwind: every open scope closed, the hold kept");
    REFUSES("L2: check_closed with a scope open REFUSED",
            ({ Scope t_ = pcrec_scope_open(&a); (void)t_; pcrec_scope_check_closed(&a); }));
    pcrec_scope_check_closed(&a);
    ok("L2: check_closed with no scope open passes");
    Scope s3 = pcrec_scope_open(&a);
    (void)pcrec_scope_malloc(&s3, 8);
    pcrec_arena_free(&a);   /* the longjmp shape: teardown with a scope open */
    expect(!a.n && !a.rec && !a.open && !a.gen, "teardown: pcrec_arena_free releases open scopes, entries and holds");
}

/* R-3: the registry is one array that MOVES when it grows. A hold taken
 * first, a scope opened under many entries, a StrBuf and a child arena taken
 * before the growth: every handle still checks, every storage pointer is
 * still the client's, and the close pops back to the mark. */
static void growth(void)
{
    Arena a = { 0 };
    ArenaHold h = pcrec_arena_hold(&a);
    Scope s1 = pcrec_scope_open(&a);
    StrBuf *sb = pcrec_scope_sb(&s1);
    pcrec_sb_puts(sb, "before");
    Arena *c = pcrec_scope_arena(&s1);
    (void)pcrec_arena_alloc(c, 16);
    size_t cap0 = a.cap;
    for (int i = 0; i < 100; i++) (void)pcrec_scope_malloc(&s1, 8);
    Scope s2 = pcrec_scope_open(&a);
    for (int i = 0; i < 100; i++) (void)pcrec_scope_malloc(&s2, 8);
    expect(a.cap > cap0 && a.n == 205, "growth: the array grew past its first capacity");
    pcrec_sb_puts(sb, " after");
    expect(sb->len == 12 && !memcmp(sb->p, "before after", 12) && c->head,
           "growth: a StrBuf and a child arena taken before the growth are still the client's");
    REFUSES("growth: the outer handle is still not innermost", pcrec_scope_malloc(&s1, 8));
    pcrec_scope_close(&s2);
    expect(a.open == s1.mark && a.n == 104, "growth: close(S2) pops back to its mark");
    pcrec_scope_close(&s1);
    pcrec_hold_set(&h, malloc(4));
    expect(a.n == 1 && !a.open, "growth: close(S1) pops back to the hold, whose handle still sets");
    pcrec_arena_free(&a);
}

int main(void)
{
    stale_handle_drill();
    free_the_mark_drill();
    hold_rule();
    child_rule();
    adopt_rule();
    teardown_unwind();
    growth();
    printf("\nchecks passed: %d\nchecks failed: %d\n", pass_n, fail_n);
    return fail_n ? 1 : 0;
}
