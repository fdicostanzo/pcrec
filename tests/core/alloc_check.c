/* tests/core/alloc_check.c — [REVW.U] THE ALLOCATION-FAILURE INJECTOR'S
 * CHECK DRIVER (lens 5's R1, judged LOCAL — see tests/core/alloc_inject.h).
 *
 * THE PROPERTY UNDER AUDIT (src/core/CLAUDE.md's own rule): *"pcrec is a
 * LIBRARY, and aborting kills the CALLER's process."*
 *
 *   For every N in 1..K (K measured per witness, below), a build in
 *   which the Nth malloc/calloc/realloc/strdup call returns NULL must
 *   answer pcrec_compile() with a DIAGNOSED error (rc == -1, a non-empty
 *   message) — never abort(), never a signal, never success.
 *
 * WHY ANSWER-LEVEL COVERAGE CANNOT SEE IT. The closest existing section,
 * tests/resource/run_resource_tests.sh section 2, is blind for reasons
 * enumerated in lens 8's F6 and this file does not repeat: it is skipped
 * on darwin, its verdict arm accepts a BUDGET refusal as if it were an
 * allocation failure, and even repaired an `RLIMIT_AS` ceiling fails
 * whichever allocation happens to cross the line — nothing steers it to
 * a CHOSEN site. This file's counter is a steering wheel; a limit is a
 * wall.
 *
 * THIS FILE DOES NOT LINK THE INJECTED HEADER. `tests/core/
 * alloc_inject.h` is `-include`d into the SEPARATE `build-alloc/` tree
 * this file's own driver script compiles — never into this TU — so the
 * four `pcrec_inject_*` functions DEFINED here call the REAL libc
 * allocators, and this file's own bookkeeping (the pipe, `waitpid`,
 * `memset`) is never redirected.
 *
 * ISOLATION IS BY `fork()`, ONE CHILD PER TRIAL. `abort()`/SIGABRT/
 * SIGSEGV are exactly the outcomes under audit, so the sweep cannot run
 * in-process — a single crashing trial would take the whole sweep and
 * every later N with it. Each child gets a fresh `call_n = 0` right
 * after `fork()`, so the counter always starts at the SAME point a
 * direct `pcrec_compile()` call would.
 *
 * WITNESSES, AND WHY A FIXED SET RATHER THAN AN EXHAUSTIVE SWEEP OF EVERY
 * COMPILE PATH IN THE TREE. `K` (allocations per compile) is unbounded
 * in principle; the tier budget (R0.4: one gcc invocation and one
 * process spawn per SUBJECT, no per-case `pcrec`/`gcc` call) forbids
 * driving this through a corpus. This is therefore a deliberate,
 * NAMED exception (R1's own residual): a fixed small K, measured per
 * witness by a "never fail" profiling run rather than guessed, over a
 * fixed witness set —
 *
 *   W1  a plain DFA compile                       ("[a-z]+")
 *   W2  the VM CURSOR RUNG — F1's own reaching sequence
 *       (lens 8: "reached by any VM-engine pattern with a deterministic
 *       repeat over a class sequence")                 ("[a-z]{2,10}")
 *   W3  module `unicode-props` under `-e utf8`          ("\\p{L}")
 *   W4  the [ART-SIZE] SIZE-TERM LADDER — seven internal attempts, the
 *       one mechanism K60 names that W1-W3 structurally cannot reach
 *       ([K60MEAS]; see the witness table at the bottom of this file)
 *   W5  the FORCE LOOP's arm: `pcrec_emit_facts` on "(?:a?){700}" with the
 *       failing allocation INSIDE a forced fact derivation — its own
 *       property (rc 0 + one `decline:force-failed` row), its own driver
 *       `w5_run()`; see the [W5] block above `main`
 *   W6  the COMPOUND WALK: nested part compiles whose heap results the
 *       arena owns ("^abc|x+$"; [K155], its row's comment)
 *   W7  [ARENA-SCOPES] THE ARENA WINDOW, over each of W1-W4 and W6: a second
 *       counter (`arena_n`) of ARENA allocations made inside a WINDOW, each
 *       a trial point failed through the arena's real failure path. An
 *       arena allocation that fits its block takes no malloc, so W1-W6's
 *       malloc counter cannot fail it where it matters (how K163 and the
 *       `uprops_produce` strand hid). The windows: a scope is open on the
 *       allocating arena (`pcrec_arena_open_p`), or a HAND-KEPT arena is
 *       live (Ctx-bound, not its Ctx's own `&cx->arena`, not a scope's
 *       child, holding a block). The hook is the test link's alone:
 *       `-Wl,--wrap=pcrec_arena_alloc,--wrap=pcrec_arena_free` (both links:
 *       tests/core/run_alloc_tests.sh and tests/resource/run_resource_tests.sh);
 *       nothing under src/ is edited. Its control (the SEEN gate,
 *       docs/design/arena_scopes.md "Tests and sabotage") is the planted
 *       witness `W7 control`, a hand-kept arena stranded on purpose, which
 *       every trial must read as STRANDED.
 *       THE STRIDE (lane arenabuild2, ruling R-1): every point in the
 *       hand-kept window is a trial; a point in the scope window ONLY is a
 *       trial every W7_SCOPE_STRIDE-th (4) of them, the first included.
 *       Measured at R-1: W7/W3 runs 535 trials (9 hand-kept + 526 of 2,102
 *       scope-window points), against 2,111 unstrided at F1.
 *       THE MEMO EXCLUSION (a recorded design deviation, ruling R-1): the
 *       DFA memo arena is not hand-kept. Its premise, that compile_driver
 *       frees it on EVERY arrival, refusals included, is BOUND here: every
 *       child of every witness (malloc and arena trials, the profiling pass)
 *       exits 6, a FAIL, if a memo arena still holds a block when the
 *       compile returns (sabotage S3603 drops one of those frees).
 *
 * [K60FIX] (2026-09-18, lane k60fix, docs/dev/decisions.md D109): W4's own
 * mechanism (the [ART-SIZE] ladder catch absorbing a genuine pcrec_ctx_nomem) is
 * FIXED at the recovery point — W4 is expected to PASS (0 absorptions,
 * single-shot and sustained both) on any tree carrying the fix, and a W4
 * FAIL here is a real regression. W1 and W3's absorptions were a SEPARATE
 * mechanism (emit_state_legend's silent degradation, src/gen/emit_dfa.c —
 * see tests/core/CLAUDE.md's own [K60FIX] note) that this fix could not
 * reach by construction.
 *
 * [D105] (2026-09-18, lane d105, same day): that separate mechanism is
 * fixed too — the legend's raw allocations are DELETED, not rerouted — so
 * W1 and W3 read 0 absorptions as well and **every witness in this file is
 * expected to PASS**. K60 is closed in both its classes; any FAIL here is
 * now a real regression, whichever witness it names.
 *
 * [D110] (2026-09-18, lane allocpins, Frank's ruling) THE POPULATION
 * EXPECTATION IS A FLOOR NOW, NOT AN EQUALITY PIN. [REVW.2]'s wave 2
 * slices A+C moved W4's population 158 -> 162 by two byte-neutral,
 * size-neutral refactors — the measured evidence that an equality pin
 * re-pins on ordinary allocation-shape churn no caller can observe, not
 * only on the K35 hazard (a population falling toward empty) it exists to
 * catch. Each witness's `min_total` is now HALF its measured population at
 * ruling time, so a legitimate refactor's incidental movement has wide
 * margin and a real collapse still trips it. `expect_absorbed_*` is
 * UNCHANGED — still exact, in both directions, since both K60 classes are
 * closed and any absorption anywhere is a regression. See the `Witness`
 * struct's own comment and `docs/dev/decisions.md` D110.
 *
 * — not a `--source` target (composing a real `.rxt` definitions file
 * inside a pure C driver adds machinery this check does not need to
 * demonstrate the property again through a fourth, structurally
 * identical path: `pcrec_compile_defs` shares `compile_driver` with
 * `pcrec_compile` end to end, so the discipline IS the same code for
 * both).
 *
 * VERDICT PER TRIAL, via the child's exit status:
 *   0    diagnosed failure (rc == -1, err.msg non-empty)   -- PASS
 *   2    pcrec_compile SUCCEEDED despite the forced failure -- FAIL
 *   3    rc == -1 but err.msg was EMPTY (a failure with no diagnostic)
 *                                                            -- FAIL
 *   WIFSIGNALED  abort()/SIGSEGV/etc                        -- FAIL,
 *        reported by signal number (SIGABRT=6 is the K7 shape verbatim)
 *
 * ============================================================= [K60MEAS]
 * THREE MODES, AND THE DEFAULT IS UNCHANGED (lane k60meas, 2026-09-18,
 * docs/dev/k60_measurement.md). `make test`'s own caller
 * (tests/resource/run_resource_tests.sh section 2b) runs this binary with
 * NO ARGUMENTS and greps its output, so the argument-free behaviour and
 * every verdict string it prints are exactly what they were.
 *
 *   (no args)      SINGLE-SHOT: fail exactly the Nth allocation, let every
 *                  later one succeed. What K60 was found with.
 *   --sustained    SUSTAINED: fail the Nth allocation AND EVERY ALLOCATION
 *                  AFTER IT. The decisive experiment. Single-shot cannot
 *                  tell "the compile degraded gracefully under memory
 *                  pressure" from "the next allocation happened to
 *                  succeed", because in single-shot mode it always does.
 *                  Under sustained failure there is no later allocation to
 *                  get lucky with, so an absorption that SURVIVES is a real
 *                  fallback path and an absorption that COLLAPSES into a
 *                  refusal was luck.
 *   --both         both sweeps, plus the per-witness comparison table.
 *
 *   --sites        (modifier) print one line per NON-PASSING trial naming
 *                  the `file:line` of the allocation that was forced to
 *                  fail — the injector's own `__FILE__`/`__LINE__`
 *                  pass-through (tests/core/alloc_inject.h). This is what
 *                  turns "15 of 72 were absorbed" into "these 15 sites
 *                  were absorbed", which is the only form a mechanism can
 *                  be attributed from.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <unistd.h>
#include <malloc.h>
#include <sys/wait.h>

/* core/internal.h (not just pcrec.h): pcrec_enabled_set_spec, the W3
 * witness's feature-gate installer, has no public entry. */
#include "core/internal.h"

/* ==== the injector's own state — REAL allocators, this TU is never
 * compiled with alloc_inject.h ==== */
static long long call_n = 0;
static long long fail_at = 0;   /* 0 = never fail (the profiling pass) */
/* [K60MEAS] SUSTAINED: fail `fail_at` and everything after it. */
static int sustained = 0;
/* [K60MEAS] the FIRST forced failure's own call site, reported to the
 * parent over the trial pipe. First, not last: in sustained mode every
 * later allocation fails too, and the site that matters is the one the
 * compile first had to cope with. */
static char fail_site[96];
/* [K155] THE LIVE HEAP of the injected tree: every block its malloc/calloc/
 * realloc/strdup handed out, less every one its free gave back, counted in
 * `malloc_usable_size` (the same block measured on both sides). A compile
 * that returns -1 must leave it where it started: a nonzero balance is a
 * block stranded by the refusal's longjmp. */
static long long live_bytes = 0;

/* [W5] THE ALLOCATION-SITE TRACE, off except in W5's three profiling passes:
 * every call's `__FILE__`/`__LINE__` in order, so two runs of the same
 * pattern can be diffed by the SITES of their allocations. `call_n` is the
 * 1-based index into it. */
#define TRACE_CAP 4096
static int trace_on = 0;
static const char *tr_file[TRACE_CAP];
static int tr_line[TRACE_CAP];

static int inject_should_fail(const char *file, int line)
{
    if (trace_on && call_n >= 1 && call_n <= TRACE_CAP) {
        tr_file[call_n - 1] = file;
        tr_line[call_n - 1] = line;
    }
    if (!fail_at) return 0;
    if (call_n < fail_at) return 0;
    if (!sustained && call_n != fail_at) return 0;
    if (!fail_site[0]) {
        const char *base = strrchr(file, '/');
        snprintf(fail_site, sizeof fail_site, "%s:%d", base ? base + 1 : file, line);
    }
    return 1;
}

/* [K155] THE LIVE BLOCKS' OWN ALLOCATION SITES, in a small open-addressed
 * table (pointer -> the `file:line` that allocated it): what --sites prints
 * for each stranded trial. (The filed-stranding table that excused named
 * places, with its allocation-stack recording, is deleted: its last row,
 * K155's `target_headers_render`, closed at [ARENA-SCOPES] F3, and a table
 * no row can reach is a check of nothing, learnings.md section 3.) */
#define LIVE_CAP 65536
static int show_sites = 0;   /* --sites */
typedef struct { void *p; const char *file; int line; } LiveEnt;
static LiveEnt live_tab[LIVE_CAP];
static size_t live_slot(void *p)
{
    size_t h = ((size_t)p >> 4) * 2654435761u % LIVE_CAP;
    while (live_tab[h].p && live_tab[h].p != p) h = (h + 1) % LIVE_CAP;
    return h;
}
static void live_note(void *p, const char *file, int line)
{
    if (!p) return;
    size_t h = live_slot(p);
    live_tab[h].p = p; live_tab[h].file = file; live_tab[h].line = line;
}

/* [K155] is `p` a block this injector counted (review r96 CHECK-6)? A
 * block libc returned on its own (`realpath(.., NULL)`, a FILE's buffer)
 * was never added, so its free must not lower the balance: subtracting it
 * could cancel a real stranded block of the same size. */
static int live_tracked(void *p)
{
    return p && live_tab[live_slot(p)].p == p;
}
static void live_forget(void *p)
{
    if (!p) return;
    size_t h = live_slot(p);
    if (!live_tab[h].p) return;
    /* backward-shift delete keeps every probe chain whole */
    live_tab[h].p = NULL;
    for (size_t j = (h + 1) % LIVE_CAP; live_tab[j].p; j = (j + 1) % LIVE_CAP) {
        LiveEnt e = live_tab[j];
        live_tab[j].p = NULL;
        live_tab[live_slot(e.p)] = e;
    }
}

/* [K155] counts a block the real allocator returned into the live heap */
static void *live_add_at(void *p, const char *file, int line)
{
    if (p) live_bytes += (long long)malloc_usable_size(p);
    live_note(p, file, line);
    return p;
}
#define live_add(p) live_add_at((p), file, line)

/* [ARENA-SCOPES] W7 THE ARENA WINDOW (see the header): the arena-trial
 * counter, the trial to fail, and the live HAND-KEPT arenas. */
static long long arena_n = 0;
static long long arena_fail_at = 0;   /* 0 = never fail */
static int arena_mode = 0;            /* this sweep's trial points are W7's */
#define HK_CAP 64
static const Arena *hk[HK_CAP];
static int hk_n = 0;
/* R-1: a point in the scope window only is a trial every W7_SCOPE_STRIDE-th
 * time (the first included). Why 4: F1's unstrided W7 ran 2,112 trials in
 * 58 s against the design's budget of 2,000; the scope window's points all
 * fail inside the same few minimize tables, so every 4th still reaches each
 * table, and the hand-kept window (the strands W7 exists to find) is kept
 * whole. */
#define W7_SCOPE_STRIDE 4
static long long scope_pt_n = 0;
/* R-1: the live DFA memo arenas (a block taken, not yet freed). */
static const Arena *mm[HK_CAP];
static int mm_n = 0;

static void hk_forget(const Arena *a)
{
    for (int i = 0; i < hk_n; i++)
        if (hk[i] == a) { hk[i] = hk[--hk_n]; break; }
    for (int i = 0; i < mm_n; i++)
        if (mm[i] == a) { mm[i] = mm[--mm_n]; break; }
}

/* The Ctx's DFA memo arena (`cx->dfa_memo`, S7). */
static int is_memo(const Arena *a)
{
    return a->cx && a->cx->dfa_memo && a == &a->cx->dfa_memo->arena;
}

/* A HAND-KEPT arena: Ctx-bound, not its Ctx's own `&cx->arena`, not a
 * scope's child (the registry frees those), and not the Ctx's DFA memo
 * (`cx->dfa_memo`, S7: compile_driver frees it by hand on EVERY arrival, the
 * handler's included, so it cannot strand; its window would span the whole
 * compile and multiply W7's population for trials that cannot fail). */
static int hand_kept(const Arena *a)
{
    return a->cx && a != &a->cx->arena && !a->child && !is_memo(a);
}

void *__real_pcrec_arena_alloc(Arena *a, size_t sz);
void __real_pcrec_arena_free(Arena *a);

/* Every arena allocation from outside arena.c lands here (the test link's
 * --wrap): inside a window it is a W7 trial point, failed on the chosen
 * trial through the real failure path; a hand-kept arena's first block
 * opens the hand-kept window. */
void *__wrap_pcrec_arena_alloc(Arena *a, size_t sz)
{
    if (hk_n > 0 || (pcrec_arena_open_p(a) && scope_pt_n++ % W7_SCOPE_STRIDE == 0)) {
        arena_n++;
        if (arena_fail_at && arena_n == arena_fail_at) {
            if (!fail_site[0])
                snprintf(fail_site, sizeof fail_site, "arena window trial %lld", arena_n);
            if (a->cx) pcrec_ctx_nomem(a->cx);
            abort();
        }
    }
    ABlock *h0 = a->head;
    void *p = __real_pcrec_arena_alloc(a, sz);
    if (!h0 && a->head && hand_kept(a) && hk_n < HK_CAP)
        hk[hk_n++] = a;
    if (!h0 && a->head && is_memo(a) && mm_n < HK_CAP)
        mm[mm_n++] = a;
    return p;
}

/* A hand-kept arena's release closes its window; a memo's leaves the list. */
void __wrap_pcrec_arena_free(Arena *a)
{
    hk_forget(a);
    __real_pcrec_arena_free(a);
}

void *pcrec_inject_malloc_at(size_t sz, const char *file, int line)
{
    call_n++;
    if (inject_should_fail(file, line)) return NULL;
    return live_add(malloc(sz));
}
void *pcrec_inject_calloc_at(size_t n, size_t sz, const char *file, int line)
{
    call_n++;
    if (inject_should_fail(file, line)) return NULL;
    return live_add(calloc(n, sz));
}
void *pcrec_inject_realloc_at(void *p, size_t sz, const char *file, int line)
{
    call_n++;
    if (inject_should_fail(file, line)) return NULL;
    int tracked = live_tracked(p);
    long long old = tracked ? (long long)malloc_usable_size(p) : 0;
    live_forget(p);   /* before the call: `p` is not read after it */
    void *np = realloc(p, sz);
    if (!np) { if (tracked) live_note(p, file, line); return NULL; }   /* `p` still live */
    live_bytes -= old;
    return live_add(np);
}
char *pcrec_inject_strdup_at(const char *s, const char *file, int line)
{
    call_n++;
    if (inject_should_fail(file, line)) return NULL;
    return live_add(strdup(s));
}
void pcrec_inject_free_at(void *p, const char *file, int line)
{
    (void)file; (void)line;
    if (live_tracked(p)) live_bytes -= (long long)malloc_usable_size(p);
    live_forget(p);
    free(p);
}

static int pass_n, fail_n;
static void ok(const char *fmt, ...)
{
    va_list ap; va_start(ap, fmt);
    printf("PASS: "); vprintf(fmt, ap); printf("\n");
    va_end(ap);
    pass_n++;
}
static void bad(const char *fmt, ...)
{
    va_list ap; va_start(ap, fmt);
    fprintf(stderr, "FAIL: "); vfprintf(stderr, fmt, ap); fprintf(stderr, "\n");
    va_end(ap);
    fail_n++;
}

typedef struct {
    const char *name;
    const char *pattern;
    int encoding;      /* PCREC_ENC_* */
    int enable_unicode_props;
    int force_engine;  /* 0 = auto (pcrec_default_options' default); else PCREC_ENGINE_* */
    /* [D105] TWO KINDS OF EXPECTATION, for two different reasons —
     * "no absorption" on its own is a claim a check can satisfy by not
     * reaching the compile at all (K35 — count the population, fail on an
     * empty one).
     *
     * [D110] (2026-09-18, lane allocpins, Frank's ruling) `min_total` IS A
     * FLOOR, not an equality pin. D105's own two-day life measured the
     * hazard the OTHER way first: [REVW.2]'s wave 2 slices A+C moved W4's
     * population 158 -> 162 by two BYTE-NEUTRAL, SIZE-NEUTRAL refactors
     * (pcrec_sb_fragf's fragment retirement changing the arena-call SHAPE, not
     * the compile's observable behaviour) — an equality pin re-pins on
     * every such refactor whether or not anything a caller can see moved,
     * which is a tax on the whole tree's future allocation-shape churn, not
     * evidence of anything. K35's actual hazard is a population that FALLS
     * — to zero (the witness stopped reaching the compile) or partway (some
     * of what it swept quietly stopped being swept) — never one that RISES
     * or holds; a check that also fires on a rise is asserting a property
     * ("this witness's shape never changes") nobody needs and every
     * legitimate refactor violates. So the floor is set at HALF the
     * measured population at the time of this ruling — low enough that an
     * ordinary refactor's incidental movement (four allocations out of 162,
     * measured) does not approach it, high enough that an empty or
     * near-empty population (the actual hazard) still trips it. See D110
     * for the ruling and the measured brittleness it answers.
     *
     * `expect_absorbed_*` STAYS EXACT, in both directions, because both
     * classes of K60 are now CLOSED (D105 + D109): any absorption at all is
     * a regression, and a witness that stops absorbing what it used to
     * (there is nothing left to stop absorbing — every row already pins
     * zero) would mean the check itself lost reach, not that a defect
     * moved. `absorbed_why` is NULL on every row today; the field and the
     * ratchet stay in case a NEW defect is filed and pinned the same way. */
    long long   min_total;
    long long   expect_absorbed_single;
    long long   expect_absorbed_sustained;
    const char *absorbed_why;   /* NULL iff both expectations are zero */
    /* [ARENA-SCOPES] a PLANTED witness runs this instead of pcrec_compile
     * (the W7 control); it returns the compile-shaped rc and fills `err` */
    int (*run)(pcrec_error *err);
    /* W7: every trial must read STRANDED (the control that can fail) */
    int expect_all_stranded;
} Witness;

/* [K60MEAS] what a child hands back: the profiling total (mode 0 only) and
 * the forced failure's own call site. One fixed-size record, one write,
 * one read — a pipe protocol a reader can check by eye. */
typedef struct {
    long long total;
    long long leaked;   /* [K155] the live heap's balance after the compile */
    char      site[96];
} ChildReport;

/* One CHILD attempt: N == 0 means "never fail" (the profiling pass);
 * N > 0 forces the Nth allocation to return NULL (and, under `sustained`,
 * every allocation after it). */
static void child_attempt(const Witness *w, long long n, int sust, int fd)
{
    fail_at = arena_mode ? 0 : n;
    arena_fail_at = arena_mode ? n : 0;
    arena_n = 0;
    hk_n = 0;
    scope_pt_n = 0;
    mm_n = 0;
    sustained = sust;
    call_n = 0;
    live_bytes = 0;
    memset(live_tab, 0, sizeof live_tab);   /* nothing inherited from the parent */
    fail_site[0] = 0;

    pcrec_options opt;
    pcrec_default_options(&opt);
    /* [REL-1.11]: pcrec_compile() resolves gating from opt.features per
     * call now, not from src/parse/enabled.c's process-global -- this
     * witness's own module request rides that field directly instead of
     * a separate pcrec_enabled_set_spec() call the compile would no
     * longer see. */
    if (w->enable_unicode_props) opt.features = "unicode-props";
    opt.encoding = w->encoding;
    if (w->force_engine) opt.engine = w->force_engine;

    pcrec_output out; memset(&out, 0, sizeof out);
    pcrec_error err; memset(&err, 0, sizeof err);
    int rc = w->run ? w->run(&err) : pcrec_compile(w->pattern, &opt, &out, &err);
    long long total = arena_mode ? arena_n : call_n;
    /* [K155] the caller's output goes back before the balance is read: on
     * either answer the compile must leave the live heap where it found it */
    if (rc == 0 && !w->run) pcrec_output_free(&out);

    ChildReport rep;
    memset(&rep, 0, sizeof rep);
    rep.total = total;
    rep.leaked = live_bytes;
    memcpy(rep.site, fail_site, sizeof rep.site);

    if (live_bytes && show_sites)
        for (size_t h = 0; h < LIVE_CAP; h++)
            if (live_tab[h].p)
                printf("  LIVE %s N=%lld block %zu bytes from %s:%d\n", w->name, n,
                       malloc_usable_size(live_tab[h].p), live_tab[h].file,
                       live_tab[h].line);
    if (fd >= 0) { ssize_t wr = write(fd, &rep, sizeof rep); (void)wr; }
    fflush(stdout);
    if (n == 0) {
        /* profiling pass: the total is the report; the compile must succeed
         * and give back every block, the memo's included */
        _exit(rc == 0 && live_bytes == 0 && !mm_n ? 0 : 1);
    }
    /* R-1: the memo exclusion's premise, on every arrival */
    if (mm_n) _exit(6);

    if (rc == 0)
        _exit(2);   /* forced failure at N was not on the path taken -- success is fine, but flag it for the caller to note */
    if (!err.msg[0]) _exit(3);
    /* [K155] diagnosed, but a block was stranded (4) */
    _exit(!live_bytes ? 0 : 4);
}

/* Measure K: the total allocation count over a run where nothing fails.
 * Returns -1 on any anomaly (the profiling compile itself must succeed). */
static long long profile(const Witness *w)
{
    int pipefd[2];
    if (pipe(pipefd) != 0) return -1;
    fflush(stdout);   /* a child must not inherit (and re-print) the parent's buffer */
    fflush(stderr);
    pid_t pid = fork();
    if (pid < 0) { close(pipefd[0]); close(pipefd[1]); return -1; }
    if (pid == 0) {
        close(pipefd[0]);
        child_attempt(w, 0, 0, pipefd[1]);
        _exit(127);   /* unreachable */
    }
    close(pipefd[1]);
    ChildReport rep;
    memset(&rep, 0, sizeof rep);
    ssize_t r = read(pipefd[0], &rep, sizeof rep);
    close(pipefd[0]);
    int status;
    waitpid(pid, &status, 0);
    if (r != (ssize_t)sizeof rep) return -1;
    if (!(WIFEXITED(status) && WEXITSTATUS(status) == 0)) return -1;
    return rep.total;
}

/* One trial at a chosen N. Returns the child's classification:
 *   0 = diagnosed cleanly, 2 = succeeded anyway, 3 = failed silently,
 *   100+signum = killed by a signal, -1 = wait() anomaly.
 * `site_out` (optional) receives the forced allocation's own file:line. */
static int trial(const Witness *w, long long n, int sust,
                 char *site_out, size_t site_cap, long long *leaked_out)
{
    int pipefd[2];
    if (pipe(pipefd) != 0) return -1;
    fflush(stdout);   /* a child must not inherit (and re-print) the parent's buffer */
    fflush(stderr);
    pid_t pid = fork();
    if (pid < 0) { close(pipefd[0]); close(pipefd[1]); return -1; }
    if (pid == 0) {
        close(pipefd[0]);
        child_attempt(w, n, sust, pipefd[1]);
        _exit(127);   /* unreachable */
    }
    close(pipefd[1]);
    ChildReport rep;
    memset(&rep, 0, sizeof rep);
    ssize_t r = read(pipefd[0], &rep, sizeof rep);
    close(pipefd[0]);
    if (leaked_out) *leaked_out = r == (ssize_t)sizeof rep ? rep.leaked : 0;
    if (site_out && site_cap) {
        /* A child killed by a signal never wrote its report — say so rather
         * than leaving the caller a stale or empty string. */
        snprintf(site_out, site_cap, "%s",
                 r == (ssize_t)sizeof rep && rep.site[0] ? rep.site : "(no report)");
    }
    int status;
    waitpid(pid, &status, 0);
    if (WIFEXITED(status)) return WEXITSTATUS(status);
    if (WIFSIGNALED(status)) return 100 + WTERMSIG(status);
    return -1;
}

/* [K60MEAS] one sweep's tally, so the two modes can be compared rather
 * than merely printed one after the other. */
typedef struct {
    long long total, n_succeeded, n_silent, n_signalled, n_anomaly;
    long long n_memo, first_memo_n;   /* R-1: a DFA memo arena live at return */
    long long first_succeeded_n, first_silent_n, first_signal_n, first_signal_code;
    /* [K155] diagnosed refusals that stranded heap: how many, the first N,
     * its byte balance and the forced allocation's site */
    long long n_leaked, first_leaked_n, first_leaked_bytes;
    char      first_leaked_site[96];
} Tally;


/* Returns 0 if the profiling pass failed (nothing was swept). */
static int sweep_mode(const Witness *w, int sust, Tally *t)
{
    memset(t, 0, sizeof *t);
    t->first_succeeded_n = t->first_silent_n = t->first_signal_n = -1;
    t->first_leaked_n = -1;
    t->first_signal_code = -1;

    long long total = profile(w);
    if (total <= 0) {
        bad("%s: profiling pass did not succeed cleanly (K=%lld; a failed compile, or one that left heap live after pcrec_output_free) -- cannot sweep", w->name, total);
        return 0;
    }
    t->total = total;

    /* Full histogram, not just the first miss: "succeeded anyway" and
     * "killed by a signal" are DIFFERENT findings (K7's abort() class vs.
     * a masked-retry class) and a reader must be able to tell which
     * population is which without re-running the sweep by hand. */
    for (long long n = 1; n <= total; n++) {
        char site[96];
        long long leaked = 0;
        int code = trial(w, n, sust, site, sizeof site, &leaked);
        if (code != 0 && show_sites)
            printf("  SITE %s mode=%s N=%lld code=%d at %s%s\n",
                   w->name, sust ? "sustained" : "single", n, code, site,
                   code == 4 ? " (stranded heap)" : "");
        if (code == 0) continue;
        if (code == 4) {
            if (t->first_leaked_n < 0) {
                t->first_leaked_n = n;
                t->first_leaked_bytes = leaked;
                snprintf(t->first_leaked_site, sizeof t->first_leaked_site, "%s", site);
            }
            t->n_leaked++;
            continue;
        }
        if (code == 2) { t->n_succeeded++; if (t->first_succeeded_n < 0) t->first_succeeded_n = n; }
        else if (code == 3) { t->n_silent++; if (t->first_silent_n < 0) t->first_silent_n = n; }
        else if (code == 6) { t->n_memo++; if (!t->first_memo_n) t->first_memo_n = n; }
        else if (code >= 100) { t->n_signalled++; if (t->first_signal_n < 0) { t->first_signal_n = n; t->first_signal_code = code - 100; } }
        else t->n_anomaly++;
    }
    return 1;
}

/* The verdict lines. UNCHANGED WORDING in single-shot mode — section 2b of
 * tests/resource/run_resource_tests.sh greps 'KILLED THE PROCESS BY SIGNAL'
 * out of this output, and `make alloc`'s own driver counts '^PASS'/'^FAIL'
 * lines. The sustained mode's lines carry a ` [sustained]` tag so the two
 * sweeps are never confused in one log. */
static void report(const Witness *w, const Tally *t, int sust)
{
    const char *tag = sust ? " [sustained]" : "";
    long long want = sust ? w->expect_absorbed_sustained : w->expect_absorbed_single;
    /* [K155] an absorption count EQUAL to a stated pin is the witness's
     * documented fallback (absorbed_why), not a finding; any other count is
     * (above the pin: a new absorption; below: the stale-pin line). */
    int pinned = want > 0 && w->absorbed_why && t->n_succeeded == want;
    long long bad_n = (pinned ? 0 : t->n_succeeded) + t->n_silent + t->n_signalled
                    + t->n_anomaly + t->n_leaked + t->n_memo;
    /* [ARENA-SCOPES] the W7 control: a planted strand every trial must SEE */
    if (w->expect_all_stranded) {
        if (t->total >= w->min_total && t->n_leaked == t->total)
            ok("%s%s: all %lld trial(s) read STRANDED (the planted hand-kept arena): the window SEES a stranded arena",
               w->name, tag, t->total);
        else
            bad("%s%s: the planted strand was NOT seen: %lld trial(s), %lld read stranded (floor %lld): "
                "the hand-kept window or the stranded-heap property is blind",
                w->name, tag, t->total, t->n_leaked, w->min_total);
        return;
    }
    /* [D110] THE POPULATION FLOOR, checked before any verdict: a witness
     * that stopped reaching the compile, or whose allocation shape
     * collapsed, reports "every forced failure was diagnosed" over a
     * population that is no longer the one this check was written to sweep
     * (K35). It is a FLOOR, not an equality pin — set at half the measured
     * population, below which is exactly the hazard (an empty or shrunken
     * sweep) and above which is ordinary refactor churn this check has no
     * opinion about. See the [D110] comment on `min_total`'s own field. */
    if (t->total < w->min_total)
        bad("%s%s: the swept POPULATION fell BELOW its floor -- %lld forced allocations, floor %lld. "
            "Either this witness stopped reaching what it was written to sweep (K35 -- lower the "
            "floor only if that is wrong) or a real collapse in the compile's allocation shape needs "
            "investigating before any floor is touched",
            w->name, tag, t->total, w->min_total);
    /* [D105] THE ABSORPTION PIN, in both directions. `n_succeeded` is
     * reported below on its own terms too; this is the comparison against
     * what a FILED defect accounts for. */
    if (t->n_succeeded < want)
        bad("%s%s: %lld of %lld forced allocations were absorbed, and the pin says %lld -- "
            "the filed defect moved or was FIXED and this pin is stale. Re-pin it in the "
            "same change (%s)",
            w->name, tag, t->n_succeeded, t->total, want,
            w->absorbed_why ? w->absorbed_why : "no filed defect is recorded for this witness");
    if (pinned)
        printf("NOTE: %s%s: %lld of %lld forced allocations succeeded through the pinned "
               "fallback (%s)\n", w->name, tag, t->n_succeeded, t->total, w->absorbed_why);
    if (bad_n == 0) {
        ok("%s%s: every one of %lld forced allocation failures was diagnosed (rc == -1, non-empty message), never abort/signal/success, no new stranded heap",
           w->name, tag, t->total);
        return;
    }
    if (t->n_signalled) {
        bad("%s%s: %lld of %lld forced allocations KILLED THE PROCESS BY SIGNAL (K7's abort() class) -- first at N=%lld, signal %lld",
            w->name, tag, t->n_signalled, t->total, t->first_signal_n, t->first_signal_code);
    }
    if (t->n_succeeded && !pinned) {
        /* The wording of the first sentence is UNCHANGED (it is what the K60
         * measurement quotes); what follows it says whether this count is the
         * standing filed defect or something new. */
        bad("%s%s: %lld of %lld forced allocations were SUCCEEDED THROUGH anyway -- first at N=%lld (pcrec_compile returned 0 despite the Nth allocation call returning NULL)%s%s",
            w->name, tag, t->n_succeeded, t->total, t->first_succeeded_n,
            t->n_succeeded == want && w->absorbed_why ? " -- the pinned count of " : "",
            t->n_succeeded == want && w->absorbed_why ? w->absorbed_why : "");
    }
    if (t->n_silent) {
        bad("%s%s: %lld of %lld forced allocations were diagnosed with an EMPTY message -- first at N=%lld (rc == -1, err.msg[0] == 0)",
            w->name, tag, t->n_silent, t->total, t->first_silent_n);
    }
    if (t->n_memo)
        bad("%s%s: %lld of %lld forced allocations returned with a DFA memo arena still holding a block (first N=%lld): "
            "compile_driver did not free cx->dfa_memo on that arrival, the premise of W7's memo exclusion (R-1)",
            w->name, tag, t->n_memo, t->total, t->first_memo_n);
    if (t->n_anomaly) {
        bad("%s%s: %lld of %lld forced allocations produced a wait() anomaly", w->name, tag, t->n_anomaly, t->total);
    }
    if (t->n_leaked) {
        /* [K155] the rule this reads: a builder live across a refusal is
         * arena-backed (src/core/CLAUDE.md); a heap one strands its block
         * on the longjmp. Rerun with --sites for every N's forced site. */
        bad("%s%s: %lld of %lld forced allocations were diagnosed but STRANDED HEAP -- first at N=%lld, "
            "%lld bytes still live after pcrec_compile returned -1 (forced failure at %s): a heap "
            "block was live across the refusal's longjmp",
            w->name, tag, t->n_leaked, t->total, t->first_leaked_n, t->first_leaked_bytes,
            t->first_leaked_site);
    }
}

/* ======================================================================
 * [W5] THE FORCE LOOP'S ARM — `pcrec --emit-facts`, an allocation failure
 * INSIDE a forced fact derivation (docs/design/dec_fallback.md §4.2, B0
 * deliverable 10; critB1 MAJOR-3).
 *
 * THE PROPERTY. src/core/compile.c's recovery point tests `pf.forcing`
 * FIRST, ahead of the K60 nomem arm: a failure inside a FORCED ask (one only
 * the listing made, after the artifact and every stamp exist) becomes
 * `decline:force-failed` on that one fact and the loop resumes, so
 * `pcrec_emit_facts` still answers (non-NULL text) with exactly that row. W1-
 * W4 cannot reach the arm — they drive pcrec_compile(), which never forces —
 * and no corpus compile does either, so before W5 the arm had no witness.
 *
 * WHERE THE FAILING ALLOCATION MUST LAND, AND HOW THIS FILE KNOWS IT DID.
 * Forced derivations allocate only through the arena (src/facts/kset.c's
 * `pcrec_kset_walk`, four arena allocations of ~13n bytes), and the arena
 * only reaches malloc when its current block has no room — so whether a
 * given pattern's force loop allocates AT ALL is a property of the pattern,
 * found by probing (the witness pattern below), not of the fact. The loop's
 * allocations are located WITHOUT reading the output under test, by
 * DIFFING THE SITE TRACES of two profiling passes of the same pattern:
 *   (hook-less)  pcrec_compile_driver, facts_hook == NULL: the force loop is
 *                skipped (compile.c `if (facts_hook) pcrec_facts_force_all`);
 *   (hooked)     the same call with a no-op recording hook: the force loop
 *                runs, and the hook's entry gives the allocation count there.
 * The two traces (file:line of every allocation, in order) are identical up
 * to the first allocation of the force loop; that index d is the loop's
 * first call and `hooked_at - hookless_K` is its length L (the render-prefix
 * allocations after the loop are in both traces, which is why the two total
 * counts alone cannot place the loop). Trials N in [d, d+L) are IN the loop;
 * the control shares nothing with the listing text, and a THIRD pass
 * (pcrec_emit_facts itself) is cross-checked to reproduce the hooked trace
 * through the loop, so the numbering the trials use is the one measured.
 *
 *   in-loop trials   (N in [d, d+L))   must return text carrying EXACTLY ONE
 *                    `decline:force-failed` row. Anything else is a FAIL: NULL
 *                    (the arm did not absorb, or sits below the nomem arm —
 *                    design §4.4 S-F0), text without the row, a signal.
 *   margin before    (the 6 calls before d: the compile's own last
 *                    allocations) must be DIAGNOSED (NULL + message): W1-W4's
 *                    own contract, so a regression that moves the arm's
 *                    reach upstream reads here.
 *   after the loop   (render prefix + the listing's own row rendering):
 *                    NOT asserted — see the NOTE the witness prints: today
 *                    some of these abort (detached StrBufs in
 *                    src/dump/facts_dump.c have no error channel,
 *                    sb.c's `abort()`); the witness reports the count and
 *                    asserts only that none of them can show a force-failed
 *                    row (a failure there is not a forced ask).
 *   FLOOR (K35)      the loop must contain at least W5_MIN_INLOOP calls. L is
 *                    1 for the chosen pattern (measured), so the floor is
 *                    the measured value, not half: below 1 there is nothing
 *                    left to assert. The floor applies to the population
 *                    actually asserted: if NO candidate reaches, the witness
 *                    FAILS here, loudly, rather than passing over an empty
 *                    population.
 *
 * WHICH PATTERN. Whether `(?:a?){N}`'s forced loop opens an arena block
 * depends on where N's arena usage falls against a block boundary, which
 * every change to the compiler's arena traffic shifts (kit unit M6 moved it:
 * {700} went from L=1 to L=0 while {600},{750} reached and {650},{690},{710},
 * {800} did not -- docs/dev/lanes/w5fix_report.md). A constant picked once is
 * therefore a coin that comes up again at the next shift ([MECH-REACH]). So
 * the witness MEASURES: w5_pick tries w5_counts in order, profiles each with
 * the hook-less/hooked pair above, and takes the first with L >= W5_MIN_INLOOP;
 * only when none reaches does it fail. The chosen pattern is printed.
 * Single-shot only: SUSTAINED mode would also fail the listing's own
 * rendering allocations after the loop, which is a different (unasserted)
 * population.
 * ====================================================================== */

#define W5_MARGIN     6
#define W5_MIN_INLOOP 1
#define W5_MIN_TOTAL  100   /* about half of the measured 190 ({600}; 220 at {700} before M6) */
/* The witness pattern is `(?:a?){N}` for the first N in this list whose forced
 * derivation allocates (see "WHICH PATTERN" above); w5_pattern is set by
 * w5_run. */
static const int w5_counts[] = { 700, 600, 750, 500, 900, 1000, 400, 1200, 300, 1500 };
static char w5_pattern_buf[32];
static const char *w5_pattern = "(?:a?){700}";

typedef struct { long long n; const char *f[TRACE_CAP]; int l[TRACE_CAP]; } Trace;
static Trace tr_hookless, tr_hooked, tr_emit;
static long long hooked_at = -1;

static void w5_hook(Ctx *cx, const char *artifact, size_t len, void *ud)
{
    (void)cx; (void)artifact; (void)len; (void)ud;
    hooked_at = call_n;
}

static void w5_save(Trace *t)
{
    t->n = call_n < TRACE_CAP ? call_n : TRACE_CAP;
    memcpy(t->f, tr_file, (size_t)t->n * sizeof t->f[0]);
    memcpy(t->l, tr_line, (size_t)t->n * sizeof t->l[0]);
}

static int w5_same(const Trace *a, const Trace *b, long long i)
{
    return a->l[i] == b->l[i] && !strcmp(a->f[i], b->f[i]);
}

/* mode 0 = hook-less driver, 1 = hooked driver, 2 = pcrec_emit_facts.
 * In-process (a profiling pass never fails, so there is nothing to
 * isolate). Returns the total allocation count, or -1 on any anomaly. */
static long long w5_profile(int mode, Trace *t)
{
    pcrec_options o;
    pcrec_default_options(&o);
    o.header_name = NULL;
    pcrec_error err; memset(&err, 0, sizeof err);
    fail_at = 0; sustained = 0; call_n = 0; trace_on = 1; hooked_at = -1;
    int ok_run;
    if (mode == 2) {
        char *txt = pcrec_emit_facts(w5_pattern, &o, NULL, NULL, 0, &err);
        ok_run = txt != NULL;
        free(txt);
    } else {
        pcrec_output out; memset(&out, 0, sizeof out);
        ok_run = pcrec_compile_driver(w5_pattern, &o, &out, &err, NULL, NULL, NULL,
                                      mode == 1 ? w5_hook : NULL, NULL, NULL) == 0;
        if (ok_run) pcrec_output_free(&out);
    }
    trace_on = 0;
    long long total = call_n;
    if (!ok_run || total <= 0 || total > TRACE_CAP) return -1;
    w5_save(t);
    return total;
}

/* One trial: the Nth allocation of a real pcrec_emit_facts fails.
 * Child verdicts: 20 = text with exactly one force-failed row,
 * 21 = text without it, 22 = NULL + message, 23 = NULL, no message. */
static int w5_trial(long long n, char *site_out, size_t site_cap)
{
    int pipefd[2];
    if (pipe(pipefd) != 0) return -1;
    fflush(stdout);   /* a child must not inherit (and re-print) the parent's buffer */
    fflush(stderr);
    pid_t pid = fork();
    if (pid < 0) { close(pipefd[0]); close(pipefd[1]); return -1; }
    if (pid == 0) {
        close(pipefd[0]);
        fail_at = n; sustained = 0; call_n = 0; fail_site[0] = 0; trace_on = 0;
        pcrec_options o; pcrec_default_options(&o);
        pcrec_error err; memset(&err, 0, sizeof err);
        char *txt = pcrec_emit_facts(w5_pattern, &o, NULL, NULL, 0, &err);
        int code;
        if (txt) {
            int rows = 0;
            for (const char *p = txt; (p = strstr(p, "decline:force-failed")); p++) rows++;
            code = rows == 1 ? 20 : 21;
        } else {
            code = err.msg[0] ? 22 : 23;
        }
        ChildReport rep; memset(&rep, 0, sizeof rep);
        rep.total = code;
        memcpy(rep.site, fail_site, sizeof rep.site);
        ssize_t wr = write(pipefd[1], &rep, sizeof rep); (void)wr;
        _exit(0);
    }
    close(pipefd[1]);
    ChildReport rep; memset(&rep, 0, sizeof rep);
    ssize_t r = read(pipefd[0], &rep, sizeof rep);
    close(pipefd[0]);
    int status;
    waitpid(pid, &status, 0);
    if (site_out && site_cap)
        snprintf(site_out, site_cap, "%s", r == (ssize_t)sizeof rep && rep.site[0] ? rep.site : "(no report)");
    if (WIFSIGNALED(status)) return 100 + WTERMSIG(status);
    if (r != (ssize_t)sizeof rep || !WIFEXITED(status)) return -1;
    return (int)rep.total;
}

static void w5_run(void)
{
    const char *nm = "W5 (force loop, --emit-facts)";
    long long k_less = 0, k_hook = 0, hooked_n = 0, k_emit = 0, L = 0;
    int tried = 0;
    for (size_t c = 0; c < sizeof w5_counts / sizeof w5_counts[0]; c++) {
        snprintf(w5_pattern_buf, sizeof w5_pattern_buf, "(?:a?){%d}", w5_counts[c]);
        w5_pattern = w5_pattern_buf;
        k_less = w5_profile(0, &tr_hookless);
        k_hook = w5_profile(1, &tr_hooked);
        hooked_n = hooked_at;
        tried++;
        L = k_less > 0 && k_hook > 0 && hooked_n > 0 ? hooked_n - k_less : 0;
        if (L >= W5_MIN_INLOOP) break;
        printf("NOTE: %s: candidate '%s' does not reach the arm (loop allocates %lld time(s)); trying the next\n",
               nm, w5_pattern, L);
    }
    k_emit = w5_profile(2, &tr_emit);
    if (k_less <= 0 || k_hook <= 0 || k_emit <= 0 || hooked_n <= 0) {
        bad("%s: a profiling pass did not succeed cleanly (hookless K=%lld, hooked K=%lld, emit K=%lld, hook entry %lld) -- cannot place the loop",
            nm, k_less, k_hook, k_emit, hooked_n);
        return;
    }
    /* d: 1-based index of the first call where the hooked trace leaves the
     * hook-less one. L: the loop's length. */
    long long d = 1;
    while (d <= tr_hookless.n && d <= tr_hooked.n && w5_same(&tr_hookless, &tr_hooked, d - 1)) d++;
    if (L < W5_MIN_INLOOP) {
        bad("%s: none of the %d candidate patterns (last '%s') makes the force loop allocate (floor %d) -- this witness stopped reaching the arm (K35): extend w5_counts or find a pattern whose forced derivation opens an arena block",
            nm, tried, w5_pattern, W5_MIN_INLOOP);
        return;
    }
    printf("NOTE: %s: using pattern '%s' (candidate %d of %d; loop length L=%lld)\n",
           nm, w5_pattern, tried, (int)(sizeof w5_counts / sizeof w5_counts[0]), L);
    /* The numbering cross-check: the emit_facts pass reproduces the hooked
     * trace through the loop (same pre-loop allocations, same loop). */
    for (long long i = 0; i < d - 1 + L && i < tr_emit.n; i++)
        if (!w5_same(&tr_emit, &tr_hooked, i)) {
            bad("%s: pcrec_emit_facts's allocation trace diverges from the hooked driver's at call %lld -- the loop's numbering cannot be trusted", nm, i + 1);
            return;
        }
    if (k_emit < W5_MIN_TOTAL)
        bad("%s: the swept POPULATION fell BELOW its floor -- %lld allocations, floor %d (K35)", nm, k_emit, W5_MIN_TOTAL);

    long long lo = d > W5_MARGIN ? d - W5_MARGIN : 1;
    long long n_in = 0, in_bad = 0, margin_bad = 0, post_total = 0, post_sig = 0,
              post_diag = 0, post_other = 0, post_forcefail = 0;
    for (long long n = lo; n <= k_emit; n++) {
        char site[96];
        int code = w5_trial(n, site, sizeof site);
        int in = n >= d && n < d + L;
        if (in) {
            n_in++;
            if (code != 20) {
                in_bad++;
                bad("%s: N=%lld is IN the force loop (failing site %s) and the listing %s -- expected rc 0 with exactly one `decline:force-failed` row (code %d)",
                    nm, n, site,
                    code == 22 ? "was REFUSED (NULL + message: the forcing arm did not absorb, or sits below the nomem arm)"
                  : code == 23 ? "failed with an EMPTY message"
                  : code == 21 ? "answered WITHOUT a force-failed row"
                  : code >= 100 ? "KILLED THE PROCESS BY SIGNAL" : "had a wait() anomaly",
                    code);
            } else if (show_sites) {
                printf("  SITE %s N=%lld in-loop at %s -> force-failed row\n", nm, n, site);
            }
        } else if (n < d) {
            if (code != 22) {
                margin_bad++;
                bad("%s: N=%lld (pre-loop margin, site %s) was not DIAGNOSED (code %d; 22 = NULL + message)", nm, n, site, code);
            }
        } else {
            post_total++;
            if (code >= 100) post_sig++;
            else if (code == 22) post_diag++;
            else if (code == 20) post_forcefail++;
            else post_other++;
        }
    }
    if (post_forcefail)
        bad("%s: %lld post-loop trial(s) showed a force-failed row -- a failure outside the loop must never be reported as a forced ask's", nm, post_forcefail);
    if (!in_bad && !margin_bad && !post_forcefail && n_in >= W5_MIN_INLOOP)
        ok("%s: of %lld in-loop forced allocation failure(s) (calls %lld..%lld of %lld, pattern '%s'), every one answered rc 0 with exactly one `decline:force-failed` row; %lld pre-loop margin trials diagnosed",
           nm, n_in, d, d + L - 1, k_emit, w5_pattern, (long long)(d - lo));
    /* Reported, not asserted (the property above): the listing's own row
     * rendering, after the loop. */
    printf("NOTE: %s: the %lld post-loop (render-prefix + listing-rendering) trials: %lld diagnosed, %lld killed by a signal, %lld other -- not asserted by W5\n",
           nm, post_total, post_diag, post_sig, post_other);
}

/* [ARENA-SCOPES] THE W7 CONTROL (the SEEN gate's (i)): a hand-kept arena
 * (Ctx-bound, not the Ctx's own) takes a block, then an arena allocation W7
 * fails while it is live; the longjmp skips its free, exactly
 * `uprops_produce`'s shape. Every trial must read STRANDED: a window or a
 * stranded-heap property that cannot see this cannot see the real one. */
static Ctx w7_cx;
static Arena w7_tmp;
static int w7_plant(pcrec_error *err)
{
    memset(&w7_cx, 0, sizeof w7_cx);
    memset(&w7_tmp, 0, sizeof w7_tmp);
    w7_cx.err = err;
    w7_cx.arena.cx = &w7_cx;
    if (setjmp(w7_cx.jb)) {
        pcrec_arena_free(&w7_cx.arena);   /* the teardown: w7_tmp is not its */
        return -1;
    }
    w7_tmp.cx = &w7_cx;
    (void)pcrec_arena_alloc(&w7_tmp, 16);       /* the hand-kept block */
    (void)pcrec_arena_alloc(&w7_cx.arena, 16);  /* a W7 trial point */
    pcrec_arena_free(&w7_tmp);
    pcrec_arena_free(&w7_cx.arena);
    return 0;
}

/* W7's compile rows: a malloc witness whose compile has a NONEMPTY window.
 * Measured at F1: W1, W2, W4 and W6 have none (their minimize merges
 * nothing and they hold no hand-kept arena), so they have no row (a row of
 * population 0 is a gate that passes by emptiness, K35); W3 has its
 * windows in minimize's scope and `uprops_produce`'s (F6: a scope on the attempt
 * arena, so the class constructor's allocations are scope-window points). `min_total`
 * is half the population measured after F6 (528, from `ALLOC_ARGS=--w7-only make alloc`, lane f2f6; 535 at R-1,
 * lane arenabuild2, when the hand-kept `uprops_produce` window was in it; D110). */
#define W7_ROWS \
    { "W7/W3 (unicode-props/utf8)", "\\p{L}", PCREC_ENC_UTF8, 1, 0, 264, 0, 0, NULL, NULL, 0 }, \


int main(int argc, char **argv)
{
    int do_single = 1, do_sustained = 0, w7_only = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--sustained")) { do_single = 0; do_sustained = 1; }
        else if (!strcmp(argv[i], "--both")) { do_single = 1; do_sustained = 1; }
        else if (!strcmp(argv[i], "--sites")) { show_sites = 1; }
        else if (!strcmp(argv[i], "--w7-only")) { w7_only = 1; }   /* measuring W7 alone */
        else {
            fprintf(stderr, "usage: %s [--sustained|--both] [--sites] [--w7-only]\n", argv[0]);
            return 2;
        }
    }

    /* every statement after the witness loops that judges the WHOLE run (the
     * K60 table, W5) is gated by this one
     * predicate: --w7-only runs one witness and cannot judge the whole run
     * (r105 CHECKS-5). */
    const int whole_run = !w7_only;

    static const Witness witnesses[] = {
        /* [D105] W1 and W3 are the LEGEND-CLASS witnesses: every one of
         * their absorptions (15 and 25, docs/dev/k60_measurement.md §2.2)
         * was `emit_state_legend`'s own silent degradation, and the
         * restructuring deleted the path. Both pin ZERO absorbed, so a
         * legend-class absorption — or any other absorption reaching these
         * two — is RED. The totals fell by exactly the deleted allocations:
         * 5 per emitted legend, W1 emitting three machines' worth
         * (72 - 15 = 57) and W3 five across its two attempts
         * (328 - 25 = 303).
         *
         * [D110] `min_total` IS A FLOOR: 28 (half of 57, measured
         * 2026-09-18). See the struct comment for the ruling. */
        { "W1 (DFA)",              "[a-z]+",     PCREC_ENC_BYTE, 0, 0,
          28, 0, 0, NULL, NULL, 0 },
        /* W2 forces --engine=vm: [a-z]{2,10} is capture-free and AUTO
         * selection routes it to the DFA by default (measured -- see
         * docs/dev/lanes/waveu_report.md), which never reaches
         * vm_cursor_rep/scr_test at all. Forcing the engine is what
         * makes this witness actually exercise F1's own reaching
         * sequence rather than a different one.
         *
         * [D110] `min_total` floor: 5 (half of 11). */
        { "W2 (VM cursor rung)",   "[a-z]{2,10}", PCREC_ENC_BYTE, 0, PCREC_ENGINE_VM,
          5, 0, 0, NULL, NULL, 0 },
        /* [D110] `min_total` floor: 151 (half of 303). */
        { "W3 (unicode-props/utf8)", "\\p{L}",   PCREC_ENC_UTF8, 1, 0,
          151, 0, 0, NULL, NULL, 0 },
        /* [K60MEAS] W4 — THE SIZE-TERM LADDER, added because K60 names the
         * ladder's blanket "this K is out" catch as a mechanism and NONE of
         * W1-W3 enters the ladder at all (W1/W3 are DFA-engine artifacts,
         * which the ladder's own `fit.chosen == ENGM_VM` conjunct excludes;
         * W2 is too small to reach the `emit_code` threshold). A mechanism
         * with no witness is a mechanism nobody is measuring.
         *
         * Found by sweeping the shipped corpus with the attempt-counting
         * probe (docs/dev/k60_measurement.md §3) rather than constructed:
         * this is a real corpus pattern, and it runs SEVEN internal attempts
         * (the default, all five ladder rungs, and the final re-emission). */
        /* [D105/K60FIX] W4 is the LADDER class and it is GREEN now: its
         * 108 absorptions were the `[ART-SIZE]` ladder's blanket catch
         * discarding a genuine `pcrec_ctx_nomem`-routed OOM as "this K is out",
         * fixed at the recovery point by lane k60fix (D109). This row
         * pinned 108 while that fix was in flight; the pin going stale-low
         * the moment it landed is the ratchet working as designed, and
         * zero is what it re-pins to. Every witness in this table now pins
         * zero absorbed, so `absorbed_why` is NULL on all four and any
         * absorption anywhere is a regression.
         *
         * [REVW.2] 2026-09-18 (manager, at the w2b merge): POPULATION MOVED
         * 158 -> 162 by two byte-neutral, size-neutral refactors (wave 2
         * slices A+C) that moved nothing observable — the measurement that
         * produced [D110]'s ruling, below.
         *
         * [D110] (2026-09-18, lane allocpins, Frank's ruling) `min_total`
         * BECOMES A FLOOR, 81 (half of the then-current 162): the 158 -> 162
         * shift above is exactly the ordinary refactor churn a floor is
         * built to absorb without re-pinning, and the actual hazard (K35)
         * is a population falling toward zero, which 81 still catches with
         * wide margin. `expect_absorbed_*` stays exact at 0 -- see the
         * struct comment. */
        { "W4 (size-term ladder)",
          "((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}",
          PCREC_ENC_BYTE, 0, 0,
          81, 0, 0, NULL, NULL, 0 },
        /* [K155] W6 — THE COMPOUND WALK (review r96 GENFORM-1/CHECK-5): a
         * floor arm beside an end-pinned arm admits the `split` compound
         * row, so nested part compiles run and hand their heap `c_src` to
         * the arena (an arena hold, `pcrec_arena_hold`, compound.c). W1-W5 never run the
         * walk. Measured 2026-11-24: BASE (before K155's fix) strands a
         * part's c_src on 10 diagnosed refusals; with the fix 0 new.
         *
         * THE ABSORPTION PIN IS BY DESIGN, not a filed defect: a part that
         * refuses ends the compound row and the compile falls back to the
         * plain artifact (compound.c: "Nothing here refuses the compile"),
         * so single-shot failures inside a part's compile succeed (1010 of
         * 1045 at [ARENA-SCOPES] F1, re-pinned UP from 982 of 1008: each part
         * compile's registry records are new heap calls, absorbed by the same
         * fallback; lane arenabuild2's R-3 array read 984 of 1011 and was
         * reverted, lane arenabuild3's R-5); under sustained failure the fallback fails too (0). The
         * pin is exact (D110); allocation-shape churn on the compound path
         * re-pins it. `min_total` floor: 504 (half of 1008, kept). */
        { "W6 (compound split)",   "^abc|x+$",   PCREC_ENC_BYTE, 0, 0,
          504, 1010, 0,
          "the compound row's by-design fallback: a refused part compile "
          "leaves the plain artifact (compound.c)", NULL, 0 },
    };
    const size_t nw = sizeof witnesses / sizeof witnesses[0];

    Tally single[8], sust[8];
    int have_single[8] = { 0 }, have_sust[8] = { 0 };

    for (size_t i = 0; i < nw && !w7_only; i++) {
        if (do_single) {
            have_single[i] = sweep_mode(&witnesses[i], 0, &single[i]);
            if (have_single[i]) report(&witnesses[i], &single[i], 0);
        }
        if (do_sustained) {
            have_sust[i] = sweep_mode(&witnesses[i], 1, &sust[i]);
            if (have_sust[i]) report(&witnesses[i], &sust[i], 1);
        }
    }

    /* [ARENA-SCOPES] W7, single-shot: the control first, then the arena
     * window over each compile witness. Each row's own floor and pin. */
    {
        static const Witness w7[] = {
            { "W7 control (planted hand-kept strand)", "", PCREC_ENC_BYTE, 0, 0,
              1, 0, 0, NULL, w7_plant, 1 },
            W7_ROWS
        };
        arena_mode = 1;
        for (size_t i = 0; i < sizeof w7 / sizeof w7[0]; i++) {
            Tally t;
            if (sweep_mode(&w7[i], 0, &t)) report(&w7[i], &t, 0);
        }
        arena_mode = 0;
    }

    if (whole_run && do_single && do_sustained) {
        /* [K60MEAS] THE DECISIVE COMPARISON, printed as data rather than
         * asserted: an absorption count that SURVIVES sustained failure is a
         * fallback path that genuinely does not need the memory; one that
         * COLLAPSES was single-shot luck. */
        printf("\n== [K60] absorption under single-shot vs sustained failure ==\n");
        printf("%-28s %8s %14s %14s\n", "witness", "K", "single", "sustained");
        for (size_t i = 0; i < nw; i++) {
            if (!have_single[i] || !have_sust[i]) continue;
            char a[32], b[32];
            snprintf(a, sizeof a, "%lld (%.1f%%)", single[i].n_succeeded,
                     100.0 * (double)single[i].n_succeeded / (double)single[i].total);
            snprintf(b, sizeof b, "%lld (%.1f%%)", sust[i].n_succeeded,
                     100.0 * (double)sust[i].n_succeeded / (double)sust[i].total);
            printf("%-28s %8lld %14s %14s\n", witnesses[i].name, single[i].total, a, b);
        }
    }

    /* [W5] single-shot only, see its comment block. */
    if (whole_run && do_single) w5_run();

    printf("\nchecks passed: %d\n", pass_n);
    printf("checks failed: %d\n", fail_n);
    return fail_n ? 1 : 0;
}
