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
 * WITNESSES, AND WHY THREE RATHER THAN AN EXHAUSTIVE SWEEP OF EVERY
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

void *pcrec_inject_malloc(size_t sz)
{
    call_n++;
    if (fail_at && call_n == fail_at) return NULL;
    return malloc(sz);
}
void *pcrec_inject_calloc(size_t n, size_t sz)
{
    call_n++;
    if (fail_at && call_n == fail_at) return NULL;
    return calloc(n, sz);
}
void *pcrec_inject_realloc(void *p, size_t sz)
{
    call_n++;
    if (fail_at && call_n == fail_at) return NULL;
    return realloc(p, sz);
}
char *pcrec_inject_strdup(const char *s)
{
    call_n++;
    if (fail_at && call_n == fail_at) return NULL;
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

/* One CHILD attempt: N == 0 means "never fail" (the profiling pass);
 * N > 0 forces the Nth allocation to return NULL. */
static void child_attempt(const Witness *w, long long n, int fd)
{
    if (w->enable_unicode_props) {
        char featerr[256];
        pcrec_enabled_set_spec("unicode-props", featerr, sizeof featerr);
    }
    fail_at = n;
    call_n = 0;

    pcrec_options opt;
    pcrec_default_options(&opt);
    opt.encoding = w->encoding;
    if (w->force_engine) opt.engine = w->force_engine;

    pcrec_output out; memset(&out, 0, sizeof out);
    pcrec_error err; memset(&err, 0, sizeof err);
    int rc = pcrec_compile(w->pattern, &opt, &out, &err);

    if (n == 0) {
        /* profiling pass: report the total call count over the pipe */
        long long total = call_n;
        ssize_t wr = write(fd, &total, sizeof total);
        (void)wr;
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
        child_attempt(w, 0, pipefd[1]);
        _exit(127);   /* unreachable */
    }
    close(pipefd[1]);
    long long total = -1;
    ssize_t r = read(pipefd[0], &total, sizeof total);
    close(pipefd[0]);
    int status;
    waitpid(pid, &status, 0);
    if (r != (ssize_t)sizeof total) return -1;
    if (!(WIFEXITED(status) && WEXITSTATUS(status) == 0)) return -1;
    return total;
}

/* One trial at a chosen N. Returns the child's classification:
 *   0 = diagnosed cleanly, 2 = succeeded anyway, 3 = failed silently,
 *   100+signum = killed by a signal, -1 = wait() anomaly. */
static int trial(const Witness *w, long long n)
{
    pid_t pid = fork();
    if (pid < 0) return -1;
    if (pid == 0) {
        child_attempt(w, n, -1);
        _exit(127);   /* unreachable */
    }
    int status;
    waitpid(pid, &status, 0);
    if (WIFEXITED(status)) return WEXITSTATUS(status);
    if (WIFSIGNALED(status)) return 100 + WTERMSIG(status);
    return -1;
}

static void sweep(const Witness *w)
{
    long long total = profile(w);
    if (total <= 0) {
        bad("%s: profiling pass did not succeed cleanly (K=%lld) -- cannot sweep", w->name, total);
        return;
    }

    /* Full histogram, not just the first miss: "succeeded anyway" and
     * "killed by a signal" are DIFFERENT findings (K7's abort() class vs.
     * a masked-retry class) and a reader must be able to tell which
     * population is which without re-running the sweep by hand. */
    long long n_succeeded = 0, n_silent = 0, n_signalled = 0, n_anomaly = 0;
    long long first_signal_n = -1, first_signal_code = -1;
    long long first_succeeded_n = -1;
    long long first_silent_n = -1;
    for (long long n = 1; n <= total; n++) {
        int code = trial(w, n);
        if (code == 0) continue;
        if (code == 2) { n_succeeded++; if (first_succeeded_n < 0) first_succeeded_n = n; }
        else if (code == 3) { n_silent++; if (first_silent_n < 0) first_silent_n = n; }
        else if (code >= 100) { n_signalled++; if (first_signal_n < 0) { first_signal_n = n; first_signal_code = code - 100; } }
        else n_anomaly++;
    }
    long long bad_n = n_succeeded + n_silent + n_signalled + n_anomaly;
    if (bad_n == 0) {
        ok("%s: every one of %lld forced allocation failures was diagnosed (rc == -1, non-empty message), never abort/signal/success", w->name, total);
        return;
    }
    if (n_signalled) {
        bad("%s: %lld of %lld forced allocations KILLED THE PROCESS BY SIGNAL (K7's abort() class) -- first at N=%lld, signal %lld",
            w->name, n_signalled, total, first_signal_n, first_signal_code);
    }
    if (n_succeeded) {
        bad("%s: %lld of %lld forced allocations were SUCCEEDED THROUGH anyway -- first at N=%lld (pcrec_compile returned 0 despite the Nth allocation call returning NULL)",
            w->name, n_succeeded, total, first_succeeded_n);
    }
    if (n_silent) {
        bad("%s: %lld of %lld forced allocations were diagnosed with an EMPTY message -- first at N=%lld (rc == -1, err.msg[0] == 0)",
            w->name, n_silent, total, first_silent_n);
    }
    if (n_anomaly) {
        bad("%s: %lld of %lld forced allocations produced a wait() anomaly", w->name, n_anomaly, total);
    }
}

int main(void)
{
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
    };
    for (size_t i = 0; i < sizeof witnesses / sizeof witnesses[0]; i++)
        sweep(&witnesses[i]);

    printf("\nchecks passed: %d\n", pass_n);
    printf("checks failed: %d\n", fail_n);
    return fail_n ? 1 : 0;
}
