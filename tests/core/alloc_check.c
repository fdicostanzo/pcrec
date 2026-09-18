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
 * WITNESSES, AND WHY FOUR RATHER THAN AN EXHAUSTIVE SWEEP OF EVERY
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

static int inject_should_fail(const char *file, int line)
{
    if (!fail_at) return 0;
    if (call_n < fail_at) return 0;
    if (!sustained && call_n != fail_at) return 0;
    if (!fail_site[0]) {
        const char *base = strrchr(file, '/');
        snprintf(fail_site, sizeof fail_site, "%s:%d", base ? base + 1 : file, line);
    }
    return 1;
}

void *pcrec_inject_malloc_at(size_t sz, const char *file, int line)
{
    call_n++;
    if (inject_should_fail(file, line)) return NULL;
    return malloc(sz);
}
void *pcrec_inject_calloc_at(size_t n, size_t sz, const char *file, int line)
{
    call_n++;
    if (inject_should_fail(file, line)) return NULL;
    return calloc(n, sz);
}
void *pcrec_inject_realloc_at(void *p, size_t sz, const char *file, int line)
{
    call_n++;
    if (inject_should_fail(file, line)) return NULL;
    return realloc(p, sz);
}
char *pcrec_inject_strdup_at(const char *s, const char *file, int line)
{
    call_n++;
    if (inject_should_fail(file, line)) return NULL;
    return strdup(s);
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
} Witness;

/* [K60MEAS] what a child hands back: the profiling total (mode 0 only) and
 * the forced failure's own call site. One fixed-size record, one write,
 * one read — a pipe protocol a reader can check by eye. */
typedef struct {
    long long total;
    char      site[96];
} ChildReport;

/* One CHILD attempt: N == 0 means "never fail" (the profiling pass);
 * N > 0 forces the Nth allocation to return NULL (and, under `sustained`,
 * every allocation after it). */
static void child_attempt(const Witness *w, long long n, int sust, int fd)
{
    if (w->enable_unicode_props) {
        char featerr[256];
        pcrec_enabled_set_spec("unicode-props", featerr, sizeof featerr);
    }
    fail_at = n;
    sustained = sust;
    call_n = 0;
    fail_site[0] = 0;

    pcrec_options opt;
    pcrec_default_options(&opt);
    opt.encoding = w->encoding;
    if (w->force_engine) opt.engine = w->force_engine;

    pcrec_output out; memset(&out, 0, sizeof out);
    pcrec_error err; memset(&err, 0, sizeof err);
    int rc = pcrec_compile(w->pattern, &opt, &out, &err);

    ChildReport rep;
    memset(&rep, 0, sizeof rep);
    rep.total = call_n;
    memcpy(rep.site, fail_site, sizeof rep.site);
    if (fd >= 0) { ssize_t wr = write(fd, &rep, sizeof rep); (void)wr; }

    if (n == 0) {
        /* profiling pass: the total is the report; the compile must succeed */
        if (rc == 0) pcrec_output_free(&out);
        _exit(rc == 0 ? 0 : 1);
    }

    if (rc == 0) {
        pcrec_output_free(&out);
        _exit(2);   /* forced failure at N was not on the path taken -- success is fine, but flag it for the caller to note */
    }
    _exit(err.msg[0] ? 0 : 3);
}

/* Measure K: the total allocation count over a run where nothing fails.
 * Returns -1 on any anomaly (the profiling compile itself must succeed). */
static long long profile(const Witness *w)
{
    int pipefd[2];
    if (pipe(pipefd) != 0) return -1;
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
                 char *site_out, size_t site_cap)
{
    int pipefd[2];
    if (pipe(pipefd) != 0) return -1;
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
    long long first_succeeded_n, first_silent_n, first_signal_n, first_signal_code;
} Tally;

static int show_sites = 0;

/* Returns 0 if the profiling pass failed (nothing was swept). */
static int sweep_mode(const Witness *w, int sust, Tally *t)
{
    memset(t, 0, sizeof *t);
    t->first_succeeded_n = t->first_silent_n = t->first_signal_n = -1;
    t->first_signal_code = -1;

    long long total = profile(w);
    if (total <= 0) {
        bad("%s: profiling pass did not succeed cleanly (K=%lld) -- cannot sweep", w->name, total);
        return 0;
    }
    t->total = total;

    /* Full histogram, not just the first miss: "succeeded anyway" and
     * "killed by a signal" are DIFFERENT findings (K7's abort() class vs.
     * a masked-retry class) and a reader must be able to tell which
     * population is which without re-running the sweep by hand. */
    for (long long n = 1; n <= total; n++) {
        char site[96];
        int code = trial(w, n, sust, site, sizeof site);
        if (code != 0 && show_sites)
            printf("  SITE %s mode=%s N=%lld code=%d at %s\n",
                   w->name, sust ? "sustained" : "single", n, code, site);
        if (code == 0) continue;
        if (code == 2) { t->n_succeeded++; if (t->first_succeeded_n < 0) t->first_succeeded_n = n; }
        else if (code == 3) { t->n_silent++; if (t->first_silent_n < 0) t->first_silent_n = n; }
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
    long long bad_n = t->n_succeeded + t->n_silent + t->n_signalled + t->n_anomaly;
    if (bad_n == 0) {
        ok("%s%s: every one of %lld forced allocation failures was diagnosed (rc == -1, non-empty message), never abort/signal/success",
           w->name, tag, t->total);
        return;
    }
    if (t->n_signalled) {
        bad("%s%s: %lld of %lld forced allocations KILLED THE PROCESS BY SIGNAL (K7's abort() class) -- first at N=%lld, signal %lld",
            w->name, tag, t->n_signalled, t->total, t->first_signal_n, t->first_signal_code);
    }
    if (t->n_succeeded) {
        bad("%s%s: %lld of %lld forced allocations were SUCCEEDED THROUGH anyway -- first at N=%lld (pcrec_compile returned 0 despite the Nth allocation call returning NULL)",
            w->name, tag, t->n_succeeded, t->total, t->first_succeeded_n);
    }
    if (t->n_silent) {
        bad("%s%s: %lld of %lld forced allocations were diagnosed with an EMPTY message -- first at N=%lld (rc == -1, err.msg[0] == 0)",
            w->name, tag, t->n_silent, t->total, t->first_silent_n);
    }
    if (t->n_anomaly) {
        bad("%s%s: %lld of %lld forced allocations produced a wait() anomaly", w->name, tag, t->n_anomaly, t->total);
    }
}

int main(int argc, char **argv)
{
    int do_single = 1, do_sustained = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--sustained")) { do_single = 0; do_sustained = 1; }
        else if (!strcmp(argv[i], "--both")) { do_single = 1; do_sustained = 1; }
        else if (!strcmp(argv[i], "--sites")) { show_sites = 1; }
        else {
            fprintf(stderr, "usage: %s [--sustained|--both] [--sites]\n", argv[0]);
            return 2;
        }
    }

    static const Witness witnesses[] = {
        { "W1 (DFA)",              "[a-z]+",     PCREC_ENC_BYTE, 0, 0 },
        /* W2 forces --engine=vm: [a-z]{2,10} is capture-free and AUTO
         * selection routes it to the DFA by default (measured -- see
         * docs/dev/lanes/waveu_report.md), which never reaches
         * vm_cursor_rep/scr_test at all. Forcing the engine is what
         * makes this witness actually exercise F1's own reaching
         * sequence rather than a different one. */
        { "W2 (VM cursor rung)",   "[a-z]{2,10}", PCREC_ENC_BYTE, 0, PCREC_ENGINE_VM },
        { "W3 (unicode-props/utf8)", "\\p{L}",   PCREC_ENC_UTF8, 1, 0 },
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
        { "W4 (size-term ladder)",
          "((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}",
          PCREC_ENC_BYTE, 0, 0 },
    };
    const size_t nw = sizeof witnesses / sizeof witnesses[0];

    Tally single[8], sust[8];
    int have_single[8] = { 0 }, have_sust[8] = { 0 };

    for (size_t i = 0; i < nw; i++) {
        if (do_single) {
            have_single[i] = sweep_mode(&witnesses[i], 0, &single[i]);
            if (have_single[i]) report(&witnesses[i], &single[i], 0);
        }
        if (do_sustained) {
            have_sust[i] = sweep_mode(&witnesses[i], 1, &sust[i]);
            if (have_sust[i]) report(&witnesses[i], &sust[i], 1);
        }
    }

    if (do_single && do_sustained) {
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

    printf("\nchecks passed: %d\n", pass_n);
    printf("checks failed: %d\n", fail_n);
    return fail_n ? 1 : 0;
}
