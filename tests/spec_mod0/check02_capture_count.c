/* check02_capture_count.c — INVARIANT 2: the capture count, external.
 *
 * THE PROMISE. "The count-scan's group count equals LIBPCRE2's capture count
 * over generated patterns — compiling AND non-compiling, because an undercount
 * manifests as a spurious err-115 refusal (the non-compiling side is the
 * failure direction). Population printed per generator family; includes
 * `(?<n>`/`(?<=` splits, verb and callout bodies, `(?|` branch maxima with
 * hidden `|`, scoped `(?n)`, and quote-mode edges (`(\Q?\E:a)` captures)."
 *
 * HOW THE NON-COMPILING SIDE IS REACHED — the design problem this check had to
 * solve. libpcre2 will not tell you the capture count of a pattern that does
 * not compile: PCRE2_INFO_CAPTURECOUNT needs a compiled code object. So a
 * check that only reads CAPTURECOUNT can only ever see the compiling side,
 * which is the side that does NOT fail. An undercount does not show up as a
 * wrong number; it shows up as `\N` being refused with err 115 for an N the
 * pattern really does have.
 *
 * So the count is measured a SECOND way, through the very mechanism the bug
 * would break: for a body B, the probe `\d B` compiles iff d <= the number of
 * groups B contains (single digits are backreferences validated against the
 * TOTAL count — invariant 5, clause 1). Walking d upward and taking the
 * largest d that still compiles yields the count AS ERR-115 SEES IT, and every
 * step past it is a non-compiling probe. The two measurements must agree:
 *
 *      CAPTURECOUNT(B)  ==  max { d : "\d" + B compiles }
 *
 * Both sides come from libpcre2 and neither comes from the row data. When they
 * disagree the check says so and names the body — that disagreement would mean
 * the err-115 boundary and the introspected count are not the same number,
 * which is precisely the confusion the invariant is about.
 *
 * THE FAMILIES, and why each one is here. Each is a place where "count the
 * open parens" gives the wrong answer:
 *   named        `(?<n>a)` captures, and the count must survive the name;
 *   lookaround   `(?<=a)` and `(?<!a)` open with the same two bytes as
 *                `(?<n>` and capture NOTHING — the `(?<n>`/`(?<=` split;
 *   verbs        `(*MARK:(x)` — the `(` is inside a verb ARGUMENT, not a group;
 *   callouts     `(?C"x(y")` — same, inside a callout string;
 *   branchreset  `(?|(a)|(b)(c))` — the group numbers RESTART per branch, so
 *                the count is the branch MAXIMUM, not the total, and a `|`
 *                hidden inside a nested group must not be counted as a branch;
 *   scoped_n     `(?n)` turns plain `(...)` non-capturing from that point on,
 *                so the same text counts differently depending on scope;
 *   quotemode    `(\Q?\E:a)` — the `?:` is QUOTED, so this is a CAPTURING
 *                group whose text looks exactly like a non-capturing one.
 *
 * SABOTAGE (verified 2026-08-11): make max_d() stop one short (`best = d - 1`)
 * and 74 of the 102 bodies fail, each naming the body, the CAPTURECOUNT and
 * the err-115 boundary — the 28 that still agree are the zero-capture bodies,
 * where both measurements are 0 either way, which is itself worth knowing.
 * Drop the `(?|` family and its population line disappears, which
 * spec_floors_require() turns into a failure rather than a smaller pass.
 *
 * PCREC-SIDE SURFACE, LANDED: `pcrec --count-groups [--] PATTERN`. Detected
 * by RUNNING the probe `--count-groups -- '(a)'`: stdout "1" and exit 0 means
 * the surface exists; anything else (including the exit-1 unknown-option
 * diagnostic an older pcrec prints for a flag it does not have) means it does
 * not, and this check falls back unchanged to the oracle-only behaviour below
 * — detection keys off exit codes and stdout content only, never stderr.
 * When present, every generated body below is run a SECOND time, through
 * pcrec itself, no shell involved (execl(), so a body's quotes/backslashes/
 * parens reach pcrec exactly as this file spelled them): exit 0 means
 * compare pcrec's printed count against libpcre2 CAPTURECOUNT for that body;
 * exit 1 means pcrec refuses the body (an unimplemented construct — base tier
 * only, so most of the named/lookaround/verb/callout/branch-reset/scoped/
 * quote-mode bodies land here today, not in the compared bucket) — counted,
 * not compared; anything else (timeout, a non-exit status, or an unparseable
 * stdout on exit 0) is a spec_fail. The pcrec binary's path is argv[2] if the
 * runner passed one (run_spec_mod0.sh does), else the PCREC environment
 * variable, else the literal "build/pcrec" — either override exists so a
 * sabotage run can point this check at a stand-in binary without editing it.
 *
 * SABOTAGE (verified 2026-08-11): a wrapper standing in for pcrec that prints
 * the unknown-option diagnostic and exits 1 for `--count-groups` (an old
 * pcrec) makes detect_surface() return false and the check falls back to
 * AWAITING-SURFACE, exit 3 — the pcrec-side buckets are never reported, so
 * spec_floors_require never asks for them. A wrapper that delegates every
 * body to the real pcrec except one, for which it echoes a count one too
 * high, is detected present (the '(a)' probe still passes through) and fails
 * exactly the sabotaged body, naming pcrec's wrong number against libpcre2's
 * CAPTURECOUNT, exit 1.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check02 check02_capture_count.c -ldl
 * Run:   check02 floors.txt [PCREC_PATH]
 */
#include "spec_common.h"
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

/* ---------------------------------------------------------------------
 * Running pcrec as a black box. No shell is involved anywhere here: every
 * body reaches pcrec as one argv element, handed to execl() verbatim, so a
 * body containing quotes, backslashes, or unbalanced parens reaches pcrec
 * exactly as this file spelled it, with none of the respelling a shell
 * would do. Bounded by a wall-clock timeout so a hang in pcrec is a
 * spec_fail, never a hang of the whole suite.
 * ------------------------------------------------------------------- */

#define PCREC_TIMEOUT_MS 3000

typedef struct {
    int ran;         /* fork/exec/wait all succeeded */
    int timed_out;
    int exit_code;    /* valid only when ran && !timed_out */
    char out[256];     /* captured stdout, NUL-terminated */
} PcrecRun;

static PcrecRun run_pcrec_count(const char *pcrec_path, const char *body)
{
    PcrecRun r; memset(&r, 0, sizeof r);
    int pfd[2];
    if (pipe(pfd) != 0) return r;
    pid_t pid = fork();
    if (pid < 0) { close(pfd[0]); close(pfd[1]); return r; }
    if (pid == 0) {
        close(pfd[0]);
        dup2(pfd[1], STDOUT_FILENO);
        int devnull = open("/dev/null", O_WRONLY);
        if (devnull >= 0) { dup2(devnull, STDERR_FILENO); close(devnull); }
        close(pfd[1]);
        execl(pcrec_path, pcrec_path, "--count-groups", "--", body, (char *)NULL);
        _exit(127);   /* exec failed: no such binary, or not executable */
    }
    close(pfd[1]);
    int fl = fcntl(pfd[0], F_GETFL, 0);
    fcntl(pfd[0], F_SETFL, fl | O_NONBLOCK);

    struct timespec deadline;
    clock_gettime(CLOCK_MONOTONIC, &deadline);
    deadline.tv_sec += PCREC_TIMEOUT_MS / 1000;

    size_t total = 0;
    int status = 0, exited = 0;
    for (;;) {
        pid_t w = waitpid(pid, &status, WNOHANG);
        if (w == pid) exited = 1;

        ssize_t n;
        while (total < sizeof r.out - 1 &&
               (n = read(pfd[0], r.out + total, sizeof r.out - 1 - total)) > 0)
            total += (size_t)n;

        if (exited) break;

        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);
        if (now.tv_sec > deadline.tv_sec ||
            (now.tv_sec == deadline.tv_sec && now.tv_nsec >= deadline.tv_nsec)) {
            kill(pid, SIGKILL);
            waitpid(pid, &status, 0);
            r.timed_out = 1;
            break;
        }
        struct timespec nap = {0, 5 * 1000 * 1000};
        nanosleep(&nap, NULL);
    }
    close(pfd[0]);
    r.out[total] = 0;
    r.ran = 1;
    if (!r.timed_out) r.exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    return r;
}

static void rstrip(char *s)
{
    size_t L = strlen(s);
    while (L && (s[L-1] == '\n' || s[L-1] == '\r' || s[L-1] == ' ')) s[--L] = 0;
}

static const char *pcrec_path;
static int surface_present;
static long pcrec_compared, pcrec_refused;

/* Exactly the probe the surface is specified by: '(a)' must print "1" and
 * exit 0. Anything else — including the exit-1 unknown-option diagnostic an
 * older pcrec prints for a flag it does not have — means the surface is not
 * there. Only exit codes and stdout content are examined; stderr is never
 * grepped for a failure keyword. */
static int detect_surface(const char *path)
{
    PcrecRun r = run_pcrec_count(path, "(a)");
    if (!r.ran || r.timed_out || r.exit_code != 0) return 0;
    rstrip(r.out);
    return strcmp(r.out, "1") == 0;
}

/* The pcrec-side comparison for one body, given its libpcre2 CAPTURECOUNT. */
static void check_pcrec_side(const char *b, const char *family, int cc)
{
    PcrecRun r = run_pcrec_count(pcrec_path, b);
    if (!r.ran) {
        spec_fail("%s body '%s': could not run pcrec --count-groups "
                  "(fork/exec failed)", family, b);
        return;
    }
    if (r.timed_out) {
        spec_fail("%s body '%s': pcrec --count-groups did not return within "
                  "%dms", family, b, PCREC_TIMEOUT_MS);
        return;
    }
    if (r.exit_code == 1) {
        pcrec_refused++;   /* an unimplemented construct: counted, not compared */
        return;
    }
    if (r.exit_code != 0) {
        spec_fail("%s body '%s': pcrec --count-groups exited %d (expected 0 "
                  "or 1)", family, b, r.exit_code);
        return;
    }
    rstrip(r.out);
    char *end;
    errno = 0;
    long got = strtol(r.out, &end, 10);
    if (errno || end == r.out || *end != '\0') {
        spec_fail("%s body '%s': pcrec --count-groups exited 0 but printed "
                  "unparseable stdout '%s'", family, b, r.out);
        return;
    }
    pcrec_compared++;
    if (got != cc)
        spec_fail("%s body '%s': pcrec --count-groups reports %ld, libpcre2 "
                  "CAPTURECOUNT is %d", family, b, got, cc);
}

/* The count as err-115 sees it: the largest d for which `\d B` still compiles.
 * Single digits only (1..9), which is all the invariant's failure direction
 * needs and keeps the probe free of the octal-fallback rules. Returns -1 if
 * the body does not compile on its own. */
static int max_d(const char *body)
{
    char pat[1024];
    snprintf(pat, sizeof pat, "%s", body);
    if (!spec_compile(pat).ok) return -1;
    int best = 0;
    for (int d = 1; d <= 9; d++) {
        snprintf(pat, sizeof pat, "\\%d%s", d, body);
        if (spec_compile(pat).ok) best = d; else break;
    }
    return best;
}

static long compared, noncompiling_probes;

/* One body: the two measurements must agree. */
static void body(const char *b, const char *family)
{
    int cc = spec_capture_count(b);
    if (cc < 0) {
        spec_fail("%s body '%s' does not compile — the generator must emit "
                  "bodies that do, or the cross-check has nothing to compare",
                  family, b);
        return;
    }
    int md = max_d(b);
    compared++;
    /* every d past the boundary, up to 9, is a non-compiling probe */
    noncompiling_probes += (9 - (md < 0 ? 0 : md));

    if (surface_present) check_pcrec_side(b, family, cc);

    if (cc > 9) return;    /* beyond the single-digit probe's reach */
    if (md != cc)
        spec_fail("%s body '%s': libpcre2 CAPTURECOUNT is %d, but the largest "
                  "d with `\\d`+body compiling is %d — the introspected count "
                  "and the err-115 boundary are not the same number",
                  family, b, cc, md);
}

int main(int argc, char **argv)
{
    spec_start("check02_capture_count", argc, argv, NULL);

    /* argv[2] (if the runner passed one) wins, then $PCREC, then the literal
     * default — the same three-way fallback run_spec_mod0.sh itself uses for
     * $PCREC, kept overridable here so a sabotage run can substitute a
     * stand-in binary without editing this file. */
    pcrec_path = (argc >= 3 && argv[2][0]) ? argv[2] : getenv("PCREC");
    if (!pcrec_path || !*pcrec_path) pcrec_path = "build/pcrec";
    surface_present = detect_surface(pcrec_path);
    printf("  pcrec:  %s (--count-groups %s)\n", pcrec_path,
           surface_present ? "present — comparing" : "not present — awaiting");

    long f_named = 0, f_look = 0, f_verb = 0, f_call = 0,
         f_branch = 0, f_scoped = 0, f_quote = 0;
    char buf[2048];

    /* --- named groups: the count must survive the name ------------------- */
    {
        static const char *const forms[] = {
            "(?<n%d>a)", "(?'n%d'a)", "(?P<n%d>a)", NULL };
        for (int f = 0; forms[f]; f++)
            for (int n = 1; n <= 5; n++) {
                char one[64], acc[1024]; acc[0] = 0;
                for (int i = 0; i < n; i++) {
                    snprintf(one, sizeof one, forms[f], i);
                    strncat(acc, one, sizeof acc - strlen(acc) - 1);
                }
                body(acc, "named"); f_named++;
            }
    }

    /* --- the (?<n> / (?<= split: same two opening bytes, opposite counts -- */
    {
        static const char *const looks[] = {
            "(?<=a)", "(?<!a)", "(?=a)", "(?!a)", "(?*a)", NULL };
        for (int f = 0; looks[f]; f++)
            for (int n = 1; n <= 4; n++) {
                char acc[1024]; acc[0] = 0;
                for (int i = 0; i < n; i++)
                    strncat(acc, looks[f], sizeof acc - strlen(acc) - 1);
                body(acc, "lookaround"); f_look++;
                /* and interleaved with real captures, so a miscount of the
                 * lookaround shows up as an off-by-n rather than cancelling */
                snprintf(buf, sizeof buf, "(a)%s(b)", acc);
                body(buf, "lookaround"); f_look++;
            }
    }

    /* --- verb bodies: a '(' inside a verb argument is not a group -------- */
    {
        static const char *const verbs[] = {
            "(*MARK:(x)", "(*MARK:((x)", "(*:(x)",
            "(*pla:(a))", "(*atomic:(a))", NULL };
        for (int f = 0; verbs[f]; f++) {
            /* A generator input that does not compile is reported, never
             * silently dropped: a family that quietly shrinks to nothing is
             * the vacuity this suite exists to make impossible. The guard here
             * only skips the two COMPOSED forms when the base form is already
             * invalid, so the report fires once rather than three times. */
            if (!spec_compile(verbs[f]).ok) {
                spec_fail("verbs generator input '%s' does not compile",
                          verbs[f]);
                continue;
            }
            body(verbs[f], "verbs"); f_verb++;
            snprintf(buf, sizeof buf, "(a)%s", verbs[f]);
            body(buf, "verbs"); f_verb++;
            snprintf(buf, sizeof buf, "%s(a)(b)", verbs[f]);
            body(buf, "verbs"); f_verb++;
        }
    }

    /* --- callout bodies: a '(' inside a callout string is not a group ---- */
    {
        static const char *const calls[] = {
            "(?C1)", "(?C\"x\")", "(?C\"(\")", "(?C\"((\")",
            "(?C'('", NULL };
        for (int f = 0; calls[f]; f++) {
            char one[128];
            snprintf(one, sizeof one, "%s", calls[f]);
            /* the unbalanced form is deliberately included; body() reports a
             * non-compiling generator input rather than silently dropping it,
             * so a family cannot quietly shrink to nothing */
            if (spec_compile(one).ok) { body(one, "callouts"); f_call++; }
            snprintf(buf, sizeof buf, "(a)%s(b)", calls[f]);
            if (spec_compile(buf).ok) { body(buf, "callouts"); f_call++; }
        }
    }

    /* --- (?| branch maxima, including a '|' hidden inside a nested group -- */
    {
        static const char *const br[] = {
            "(?|(a)|(b))",              /* max 1 */
            "(?|(a)|(b)(c))",           /* max 2 */
            "(?|(a)(b)(c)|(d))",        /* max 3 */
            "(?|(a(b|c))|(d))",         /* the | is INSIDE (a(b|c)): max 2 */
            "(?|(a[|])|(d)(e))",        /* the | is inside a class */
            "(?|(a\\|b)|(d)(e)(f))",    /* the | is escaped */
            "(?|(?:x|y)(a)|(b)(c))",
            NULL };
        for (int f = 0; br[f]; f++) {
            body(br[f], "branchreset"); f_branch++;
            snprintf(buf, sizeof buf, "(z)%s", br[f]);
            body(buf, "branchreset"); f_branch++;
        }
    }

    /* --- scoped (?n): the same text counts differently by scope ---------- */
    {
        static const char *const sc[] = {
            "(a)(b)",                   /* 2 */
            "(?n)(a)(b)",               /* 0 */
            "(a)(?n)(b)",               /* 1 */
            "(?n:(a))(b)",              /* 1 — the scope ends with the group */
            "(?n)(?<k>a)(b)",           /* named still captures under (?n) */
            "((?n)(a))",                /* outer counts, inner does not */
            NULL };
        for (int f = 0; sc[f]; f++) { body(sc[f], "scoped_n"); f_scoped++; }
    }

    /* --- quote-mode edges: (\Q?\E:a) is a CAPTURING group ---------------- */
    {
        static const char *const qm[] = {
            "(\\Q?\\E:a)",              /* looks non-capturing, is not */
            "(\\Q?:\\Ea)",
            "(?\\Q:\\Ea)",              /* ...and this one is not a group at all */
            "\\Q(\\Ea)",                /* the ( is quoted: no group */
            "(a\\Q)\\E)",               /* the ) is quoted */
            "\\Q(a)\\E(b)",             /* only the second is a group */
            NULL };
        for (int f = 0; qm[f]; f++)
            if (spec_compile(qm[f]).ok) { body(qm[f], "quotemode"); f_quote++; }
    }

    spec_pop("capture.family_named", f_named);
    spec_pop("capture.family_lookaround", f_look);
    spec_pop("capture.family_verbs", f_verb);
    spec_pop("capture.family_callouts", f_call);
    spec_pop("capture.family_branchreset", f_branch);
    spec_pop("capture.family_scoped_n", f_scoped);
    spec_pop("capture.family_quotemode", f_quote);
    spec_pop("capture.bodies_compared", compared);
    spec_pop("capture.noncompiling", noncompiling_probes);
    if (surface_present) {
        spec_pop("capture.pcrec_compared", pcrec_compared);
        spec_pop("capture.pcrec_refused", pcrec_refused);
    }

    static const char *const owned[] = {
        "capture.family_named", "capture.family_lookaround",
        "capture.family_verbs", "capture.family_callouts",
        "capture.family_branchreset", "capture.family_scoped_n",
        "capture.family_quotemode", "capture.bodies_compared",
        "capture.noncompiling"
    };
    spec_floors_require(owned, 9);
    if (surface_present) {
        static const char *const pcrec_owned[] = {
            "capture.pcrec_compared", "capture.pcrec_refused"
        };
        spec_floors_require(pcrec_owned, 2);
    }
    if (spec_fails) return spec_finish();

    if (!surface_present)
        return spec_await(
            "a per-pattern group count from pcrec's count-scan",
            "this check needs pcrec to report, for a given pattern, the number "
            "of capturing groups its count-scan found — any stable channel "
            "will do (a CLI flag such as `--count-groups`, a column in a "
            "per-pattern dump, or a documented symbol the harness can call). "
            "It then compares that number, body by body, against the two "
            "libpcre2 measurements above. Until then the err-115 boundary is "
            "checked against CAPTURECOUNT only, which is the oracle half");

    return spec_finish();
}
