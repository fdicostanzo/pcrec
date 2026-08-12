/* check11_modifier_syntax.c — the MODIFIERS module's RECOGNITION BOUNDARY:
 * which spellings of `(?...)` / `(?...:body)` (PCRE2's inline option
 * settings) are a valid construct at all, independent of what the letters
 * DO once matched.
 *
 * THIS CHECK IS D27 (spec-first, blinded from src/ and the rest of tests/):
 * every predictor below was derived from the ten invariant statements this
 * suite already enforces (D26: PCRE2 decides what is REAL) plus DIRECT
 * MEASUREMENT of libpcre2 10.46 done while writing this file — never from
 * memory of what PCRE2's docs are believed to say. Where a plausible-sounding
 * rule turned out wrong on measurement, the correction is recorded below
 * rather than silently fixed, per this suite's own convention (see
 * CLAUDE.md's "predictor that survives its first run has probably not been
 * tested").
 *
 * THE PROMISE (from the brief). "(?...)" and "(?...:body)" where "..." is a
 * run of option letters, optionally with a single '-' (unset) and a leading
 * '^' (reset), must be recognised EXACTLY where PCRE2 recognises them, and
 * refused exactly where PCRE2 refuses them — a construct pcrec does not
 * implement must be refused NAMING the module, never miscompiled, and (per
 * D26) whether a construct is REAL is decided by PCRE2, not by wording.
 *
 * FOUR CASE FAMILIES, each a boundary a hand-written test suite (one written
 * FROM the implementation) would be likely to reproduce rather than probe:
 *
 * A. ALPHABET SOUNDNESS. Every letter pcrec's OWN registry claims for the
 *    `modifiers` module (read from a run of `--list-syntax`, never hand-
 *    listed — measured today: J, U, a, i, m, n, r, s, x) really is a PCRE2
 *    option letter: `(?L)`, `(?-L)`, `(?L:a)` all compile. A registry that
 *    claims a letter PCRE2 does not support would be claiming a fake
 *    construct is real.
 *
 * B. ALPHABET COMPLETENESS — the check the registry's own single sample
 *    (`(?q)`, status `rejected`) does NOT cover. Every OTHER byte in
 *    A-Za-z — the full complement, not a hand-picked few — must be an
 *    option-letter-doorway REFUSAL in libpcre2, with two registry-derived
 *    exceptions computed at RUNTIME from the FULL registry (never
 *    hand-listed): a letter that owns some OTHER real `(?letter...)`
 *    construct in a DIFFERENT module (measured: C — callouts, P — named
 *    groups/backrefs/recursion, R — recursion) is excluded, because for
 *    those the correct pcrec behaviour is "recognised, but by another
 *    module's doorway," not "unrecognised." Missing this family would leave
 *    invisible any letter pcrec's registry silently omits that PCRE2 in fact
 *    supports — exactly the shape of gap a registry-derived check cannot see
 *    (the registry's completeness is what is under test).
 *
 * C. STRUCTURAL GRAMMAR of the option-run itself, independent of which
 *    letters appear: an EMPTY run `(?)` and a bare unset marker `(?-)` are
 *    both valid (a "set nothing" / "unset nothing" no-op — MEASURED, not
 *    the intuitive guess: the natural assumption is that `-` demands at
 *    least one letter after it, and it is wrong); `^` is legal ONLY as the
 *    very first character after `?` (`(?^i)` OK, `(?i^)` and `(?^^)` both
 *    refused); AT MOST ONE `-` may appear in a run (`(?i-m)` OK, `(?i--m)`
 *    and `(?i-m-s)` both refused — a SEPARATE finding from the `^` position
 *    rule, and the two must not be conflated: `^` is a POSITION rule, `-` is
 *    a COUNT rule); a letter may repeat, or appear on both sides of the `-`,
 *    redundantly (`(?ii)`, `(?i-i)` both OK); doubled/tripled `x` is a
 *    distinct legal spelling (`(?xx)`, `(?xxx)` OK — this is
 *    PCRE2_EXTENDED_MORE, and pcrec's registry has ONE row for `x`, so
 *    whether the surface distinguishes single from doubled `x` is exactly
 *    what this family is positioned to catch); a space anywhere inside the
 *    run is refused (`(? i)`, `(?i )` — unlike `x` mode's whitespace
 *    tolerance, which does not apply INSIDE the option-run syntax itself).
 *    Every structural probe is run BOTH bare and with a `:a` body suffix,
 *    because a run's validity is independent of which spelling it is
 *    attached to (MEASURED: `(?i--m:a)` fails the same way `(?i--m)` does).
 *
 * D. THE SHARED `(?-` DOORWAY. `(?-N)` (digit) is invariant recursion's
 *    relative-subroutine-call syntax (see the `recursion` module's registry
 *    rows), while `(?-L)` (letter) is this module's unset-options syntax —
 *    the SAME two-byte prefix routes to two different modules depending on
 *    what follows. Mixing them (`(?-1i)`, `(?-i1)`) is refused by PCRE2
 *    either way (MEASURED), and a pcrec that let a digit terminate an
 *    option-run without error, or a letter continue a relative reference,
 *    would be a real parser bug this doorway invites.
 *
 * WHAT IS ASSERTED. For every probe, this check predicts ACCEPT or REJECT
 * from libpcre2 (measured at the moment the predicting code ran, not
 * recalled), and — when the pcrec surface exists for that probe — compares
 * pcrec's verdict CLASS: ACCEPTED / REFUSED-AS-UNIMPLEMENTED (stderr
 * contains "requires module '") / REFUSED-AS-INVALID (any other refusal).
 * REFUSED-AS-UNIMPLEMENTED is counted, never compared or failed — the module
 * has not reached that construct yet, which is not a defect. An ACCEPTED
 * verdict is compared against the predicted ACCEPT/REJECT (accepting
 * something PCRE2 rejects is a miscompile risk); a REFUSED-AS-INVALID
 * verdict is ALSO compared against the prediction (rejecting something
 * PCRE2 accepts, once the module is far enough along to give a real opinion
 * rather than the generic gate refusal, is equally a defect — D26 again).
 *
 * SURFACE DETECTION is PER-PROBE, not whole-check (modelled on check02's
 * `--count-groups`, not check07's whole-check `--help` grep): a probe whose
 * pcrec verdict is anything other than REFUSED-AS-UNIMPLEMENTED counts as
 * "compared" and arms the check; while literally everything comes back
 * REFUSED-AS-UNIMPLEMENTED (measured TODAY: true for all four families —
 * `pcrec --features modifiers` refuses `(?i)a` exactly as `--features none`
 * does), the whole check reports AWAITING-SURFACE, oracle side fully run.
 *
 * SABOTAGE (verified 2026-08-12, exact command in the suite's report). A
 * wrapper standing in for pcrec that ACCEPTS every `-o` compile request
 * unconditionally (exit 0, a stub `main`) — 59 of the 113 probes disagree,
 * by name, spanning every family that contains an invalid case: all 40
 * `alphabet_complement` letters, 16 of the 42 `structural_grammar` probes
 * (exactly the malformed ones — `(?i^)`, `(?^^)`, `(?im^)`, `(?i--m)`,
 * `(?i-m-s)`, `(?--i)`, `(? i)`, `(?i )`, bare and `:a`-suffixed), and 2 of
 * the 4 `doorway_disambiguation` probes (the digit/letter mixes). The 54
 * probes this check predicts ACCEPT do not disagree, which is expected and
 * correct, not a gap: an always-accept stand-in cannot be caught on cases
 * this check already expects to be accepted. A second, undetectable-by-
 * design case: a stand-in that refuses family B's exceptions (C, P, R) as
 * ordinary unrecognised letters instead of routing them to their own
 * modules — out of scope for this check on purpose (family B only probes
 * the TRUE complement; C/P/R's own module ownership is check07's job).
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check11 check11_modifier_syntax.c -ldl
 * Run:   check11 floors.txt registry.tsv [pcrec-path]
 */
#include "spec_common.h"
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

/* ------------------------------------------------------------ running pcrec
 * Modelled on check02/check07's local copy: no shell anywhere, one argv
 * element per pattern, bounded by a wall-clock timeout. Trimmed to what this
 * check needs (compile-only, `-o -`, stdout discarded). */

#define PCREC_TIMEOUT_MS 3000

typedef struct { int ran; int timed_out; int exit_code; char err[512]; } PcrecRun;

static PcrecRun run_pcrec(const char *path, char *const argv[])
{
    PcrecRun r; memset(&r, 0, sizeof r);
    int epfd[2];
    if (pipe(epfd) != 0) return r;
    pid_t pid = fork();
    if (pid < 0) { close(epfd[0]); close(epfd[1]); return r; }
    if (pid == 0) {
        int devnull = open("/dev/null", O_WRONLY);
        if (devnull >= 0) { dup2(devnull, STDOUT_FILENO); close(devnull); }
        close(epfd[0]);
        dup2(epfd[1], STDERR_FILENO);
        close(epfd[1]);
        execv(path, argv);
        _exit(127);
    }
    close(epfd[1]);
    int fe = fcntl(epfd[0], F_GETFL, 0);
    fcntl(epfd[0], F_SETFL, fe | O_NONBLOCK);

    struct timespec deadline;
    clock_gettime(CLOCK_MONOTONIC, &deadline);
    deadline.tv_sec += PCREC_TIMEOUT_MS / 1000;

    size_t te = 0; int status = 0, exited = 0;
    for (;;) {
        pid_t w = waitpid(pid, &status, WNOHANG);
        if (w == pid) exited = 1;
        ssize_t n;
        while (te < sizeof r.err - 1 &&
               (n = read(epfd[0], r.err + te, sizeof r.err - 1 - te)) > 0)
            te += (size_t)n;
        if (exited) break;
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);
        if (now.tv_sec > deadline.tv_sec ||
            (now.tv_sec == deadline.tv_sec && now.tv_nsec >= deadline.tv_nsec)) {
            kill(pid, SIGKILL); waitpid(pid, &status, 0); r.timed_out = 1; break;
        }
        struct timespec nap = {0, 2 * 1000 * 1000};
        nanosleep(&nap, NULL);
    }
    close(epfd[0]);
    r.err[te] = 0;
    r.ran = 1;
    if (!r.timed_out) r.exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    return r;
}

typedef enum { VC_ACCEPTED, VC_UNIMPL, VC_INVALID, VC_ERROR } VClass;

/* Compiles PAT as a whole pattern under `--features modifiers`. Only the
 * verdict class matters here (matching is check12's job). */
static VClass compile_verdict(const char *pcrec_path, const char *pat)
{
    char *argv[] = { (char *)pcrec_path, (char *)"--features", (char *)"modifiers",
                      (char *)"-o", (char *)"-", (char *)"--", (char *)pat, NULL };
    PcrecRun r = run_pcrec(pcrec_path, argv);
    if (!r.ran) { spec_fail("compile_verdict: fork/exec failed for '%s'", pat); return VC_ERROR; }
    if (r.timed_out) { spec_fail("compile_verdict: pcrec timed out on '%s'", pat); return VC_ERROR; }
    if (r.exit_code == 0) return VC_ACCEPTED;
    if (r.exit_code == 1) return strstr(r.err, "requires module '") ? VC_UNIMPL : VC_INVALID;
    spec_fail("compile_verdict: pcrec exited %d (expected 0 or 1) for '%s' (stderr: %s)",
               r.exit_code, pat, r.err);
    return VC_ERROR;
}

/* -------------------------------------------------------------- bookkeeping */

static const char *pcrec_path;
static long pcrec_compared, pcrec_refused_unimpl;

/* One probe: PAT predicted ACCEPT (predict_ok=1) or REJECT (predict_ok=0) by
 * libpcre2, measured HERE (never recalled). Compares the prediction against
 * libpcre2 itself as a sanity check on the predictor, then (if pcrec ever
 * answers with something other than "requires module") against pcrec. */
static void probe(const char *pat, int predict_ok, const char *family)
{
    int got_ok = spec_compile(pat).ok;
    if (got_ok != predict_ok)
        spec_fail("PREDICTOR WRONG for '%s' (family %s): predicted %s, "
                   "libpcre2 says %s — this is a bug in this check, not in "
                   "pcrec; fix the prediction before trusting anything else "
                   "in this family", pat, family,
                   predict_ok ? "ACCEPT" : "REJECT", got_ok ? "ACCEPT" : "REJECT");

    VClass vc = compile_verdict(pcrec_path, pat);
    if (vc == VC_ERROR) return;
    if (vc == VC_UNIMPL) { pcrec_refused_unimpl++; return; }
    pcrec_compared++;
    int pcrec_ok = (vc == VC_ACCEPTED);
    if (pcrec_ok != predict_ok)
        spec_fail("'%s' (family %s): pcrec %s (%s), libpcre2 %s", pat, family,
                   pcrec_ok ? "ACCEPTED" : "REFUSED-AS-INVALID",
                   vc == VC_ACCEPTED ? "accepted" : "refused",
                   predict_ok ? "ACCEPTS" : "REJECTS");
}

/* ------------------------------------------------------------------- main */

int main(int argc, char **argv)
{
    const char *rp = NULL;
    spec_start("check11_modifier_syntax", argc, argv, &rp);

    pcrec_path = (argc >= 4 && argv[3][0]) ? argv[3] : getenv("PCREC");
    if (!pcrec_path || !*pcrec_path) pcrec_path = "build/pcrec";

    /* ---- read pcrec's OWN declared modifiers alphabet from the registry -- */
    char alpha[64]; int nalpha = 0;
    char structural[8]; int nstruct = 0;
    long registry_rows_modifiers = 0;
    for (int i = 0; i < spec_nrows; i++) {
        const SpecRow *r = &spec_rows[i];
        const char *m = spec_col(r, SPEC_COL_MODULE);
        if (!m || strcmp(m, "modifiers") != 0) continue;
        registry_rows_modifiers++;
        const char *sel = spec_col(r, SPEC_COL_SELECTOR);
        if (!sel || strlen(sel) != 1) {
            spec_fail("registry row for modifiers has a non-single-char "
                      "selector '%s' — this check's alphabet extraction "
                      "assumes single characters", sel ? sel : "(empty)");
            continue;
        }
        char c = sel[0];
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
            if (nalpha < (int)sizeof alpha - 1) alpha[nalpha++] = c;
        } else {
            if (nstruct < (int)sizeof structural - 1) structural[nstruct++] = c;
        }
    }
    alpha[nalpha] = 0; structural[nstruct] = 0;
    printf("  modifiers alphabet (from registry): \"%s\" (%d letters)\n", alpha, nalpha);
    printf("  modifiers structural selectors (from registry): \"%s\" (%d)\n", structural, nstruct);
    spec_pop("modsyn.registry_rows_modifiers", registry_rows_modifiers);

    /* ---- sanity: every registry `syntax` probe for this module compiles -- */
    long registry_syntax_ok = 0;
    for (int i = 0; i < spec_nrows; i++) {
        const SpecRow *r = &spec_rows[i];
        const char *m = spec_col(r, SPEC_COL_MODULE);
        if (!m || strcmp(m, "modifiers") != 0) continue;
        const char *S = spec_col(r, SPEC_COL_SYNTAX);
        if (spec_compile(S).ok) registry_syntax_ok++;
        else spec_fail("registry row's own syntax probe '%s' does not compile "
                        "under libpcre2 — the registry claims a fake construct", S);
    }
    spec_pop("modsyn.registry_syntax_ok", registry_syntax_ok);

    /* ---- family A: alphabet SOUNDNESS ------------------------------------ */
    long f_forms = 0;
    for (int i = 0; i < nalpha; i++) {
        char L = alpha[i];
        char p1[8], p2[8], p3[8];
        snprintf(p1, sizeof p1, "(?%c)", L);
        snprintf(p2, sizeof p2, "(?-%c)", L);
        snprintf(p3, sizeof p3, "(?%c:a)", L);
        probe(p1, 1, "alphabet_forms"); f_forms++;
        probe(p2, 1, "alphabet_forms"); f_forms++;
        probe(p3, 1, "alphabet_forms"); f_forms++;
    }
    spec_pop("modsyn.alphabet_forms", f_forms);

    /* ---- family B: alphabet COMPLETENESS ---------------------------------
     * Exceptions computed from the FULL registry, not hand-listed: a letter
     * with some OTHER real (non-rejected, non-modifiers) `(?letter...)` row
     * owns its own doorway and is excluded from "must be unrecognised." */
    int is_alpha[256] = {0}, is_exception[256] = {0};
    for (int i = 0; i < nalpha; i++) is_alpha[(unsigned char)alpha[i]] = 1;
    for (int i = 0; i < spec_nrows; i++) {
        const SpecRow *r = &spec_rows[i];
        if (strcmp(spec_col(r, SPEC_COL_KIND), "group") != 0) continue;
        const char *sel = spec_col(r, SPEC_COL_SELECTOR);
        if (!sel || strlen(sel) != 1) continue;
        char c = sel[0];
        if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'))) continue;
        const char *m = spec_col(r, SPEC_COL_MODULE);
        const char *st = spec_col(r, SPEC_COL_STATUS);
        int owned_elsewhere = (!m || strcmp(m, "modifiers") != 0) &&
                               strcmp(st, "rejected") != 0;
        if (owned_elsewhere) is_exception[(unsigned char)c] = 1;
    }
    printf("  alphabet-complement exceptions (owned by another real doorway):");
    for (int c = 'A'; c <= 'Z'; c++) if (is_exception[c]) printf(" %c", c);
    for (int c = 'a'; c <= 'z'; c++) if (is_exception[c]) printf(" %c", c);
    printf("\n");

    long f_complement = 0;
    for (int c = 'A'; c <= 'Z'; c++) {
        if (is_alpha[c] || is_exception[c]) continue;
        char p[8]; snprintf(p, sizeof p, "(?%c)", (char)c);
        probe(p, 0, "alphabet_complement"); f_complement++;
    }
    for (int c = 'a'; c <= 'z'; c++) {
        if (is_alpha[c] || is_exception[c]) continue;
        char p[8]; snprintf(p, sizeof p, "(?%c)", (char)c);
        probe(p, 0, "alphabet_complement"); f_complement++;
    }
    spec_pop("modsyn.alphabet_complement", f_complement);

    /* ---- family C: structural grammar of the option-run ------------------
     * (pattern, predicted-OK) pairs; each is run bare AND with a ':a' body
     * suffix, because a run's validity does not depend on which spelling it
     * is attached to (measured). */
    static const struct { const char *pat; int ok; } structural_cases[] = {
        { "(?)",       1 },   /* empty run: a no-op */
        { "(?-)",      1 },   /* bare hyphen, nothing after: also a no-op */
        { "(?^)",      1 },   /* reset alone */
        { "(?^i)",     1 },   /* ^ first, then a letter */
        { "(?i^)",     0 },   /* ^ not first: refused */
        { "(?^^)",     0 },   /* two ^: refused */
        { "(?im^)",    0 },   /* ^ at the end: refused */
        { "(?i-m)",    1 },   /* one hyphen: set then unset */
        { "(?i--m)",   0 },   /* two hyphens: refused (a COUNT rule, distinct from ^'s POSITION rule) */
        { "(?i-m-s)",  0 },   /* two hyphens, later */
        { "(?--i)",    0 },   /* two hyphens, leading */
        { "(?i-i)",    1 },   /* same letter on both sides of the hyphen: redundant, legal */
        { "(?ii)",     1 },   /* repeated letter, no hyphen: redundant, legal */
        { "(? i)",     0 },   /* space before a letter: refused */
        { "(?i )",     0 },   /* space after a letter: refused */
        { "(?xx)",     1 },   /* doubled x: PCRE2_EXTENDED_MORE, a distinct legal spelling */
        { "(?xxx)",    1 },   /* tripled x: still legal (measured, not assumed) */
        { "(?-x)",     1 },   /* unsetting x */
        { "(?-xx)",    1 },   /* unsetting doubled x */
        { "(?i-J)",    1 },   /* every alphabet letter accepts BOTH sides of a mixed run */
        { "(?J-i)",    1 },
        { NULL, 0 }
    };
    long f_struct = 0;
    for (int i = 0; structural_cases[i].pat; i++) {
        probe(structural_cases[i].pat, structural_cases[i].ok, "structural_grammar");
        f_struct++;
        char withbody[32];
        snprintf(withbody, sizeof withbody, "%.*s:a)", (int)strlen(structural_cases[i].pat) - 1,
                  structural_cases[i].pat);
        probe(withbody, structural_cases[i].ok, "structural_grammar");
        f_struct++;
    }
    spec_pop("modsyn.structural_grammar", f_struct);

    /* ---- family D: the shared (?- doorway (digit=recursion, letter=this) - */
    static const struct { const char *pat; int ok; } doorway_cases[] = {
        { "(?-i)",        1 },   /* letter after -: this module */
        { "(a)(?-1)",     1 },   /* digit after -: recursion (a DIFFERENT module, still a real
                                    construct — included as a sanity anchor, not this module's) */
        { "(a)(?-1i)",    0 },   /* digit then letter: refused either way */
        { "(?-i1)",       0 },   /* letter then digit: refused either way */
        { NULL, 0 }
    };
    long f_doorway = 0;
    for (int i = 0; doorway_cases[i].pat; i++) {
        probe(doorway_cases[i].pat, doorway_cases[i].ok, "doorway_disambiguation");
        f_doorway++;
    }
    spec_pop("modsyn.doorway_disambiguation", f_doorway);

    /* ---- pcrec-side population -------------------------------------------
     * Not gated behind a whole-check surface flag (see header): every probe
     * above already went through compile_verdict(). A probe that came back
     * anything other than "requires module" counted toward pcrec_compared. */
    printf("  pcrec: %ld probe(s) compared, %ld refused-as-unimplemented\n",
           pcrec_compared, pcrec_refused_unimpl);
    spec_pop("modsyn.pcrec_compared", pcrec_compared);
    spec_pop("modsyn.pcrec_refused_unimpl", pcrec_refused_unimpl);

    static const char *const owned[] = {
        "modsyn.registry_rows_modifiers", "modsyn.registry_syntax_ok",
        "modsyn.alphabet_forms", "modsyn.alphabet_complement",
        "modsyn.structural_grammar", "modsyn.doorway_disambiguation",
        "modsyn.pcrec_compared", "modsyn.pcrec_refused_unimpl"
    };
    spec_floors_require(owned, 8);
    if (spec_fails) return spec_finish();

    if (pcrec_compared == 0)
        return spec_await(
            "the modifiers module accepting or opinionatedly refusing at "
            "least one option-run construct",
            "this check needs pcrec (under --features modifiers) to answer "
            "at least one of the probes above with something other than the "
            "generic \"requires module 'modifiers'\" gate refusal — either "
            "ACCEPTED or REFUSED-AS-INVALID (a refusal that does not name "
            "the module). Until then every probe is refused identically "
            "regardless of what it is, which tests the gate (check07's job), "
            "not the option-run grammar (this check's job)");

    return spec_finish();
}
