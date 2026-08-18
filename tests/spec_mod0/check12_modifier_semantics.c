/* check12_modifier_semantics.c — the MODIFIERS module's BEHAVIOUR: what each
 * letter DOES, how scope and restoration work, and the two interaction
 * families the brief named as dangerous (options x classes, options x
 * quantifiers).
 *
 * D27 (spec-first, blinded from src/ and the rest of tests/): every
 * predictor below was MEASURED against libpcre2 10.46 while writing this
 * file (dlopen oracle, no UTF/UCP needed except where stated), never
 * recalled from memory of PCRE2's documentation. check11 owns whether a
 * spelling is RECOGNISED; this check owns what a recognised spelling DOES —
 * disjoint by design, so a construct this check exercises is assumed
 * syntactically valid (check11 covers the boundary).
 *
 * SIX CASE FAMILIES:
 *
 * A. PER-LETTER EFFECT (i, m, s, x — each an on/off contrasting pair proving
 *    the letter changes the verdict, not merely that the pattern compiles).
 *
 * B. OPTIONS x CLASSES — x vs doubled xx. Whitespace inside a character
 *    class is DATA under single `x` and IGNORED under `xx`
 *    (PCRE2_EXTENDED_MORE) — measured, and the exact boundary the brief
 *    asked to be covered as a dangerous interaction: pcrec's registry has
 *    only one row for `x`, so whether the surface can even express `xx` as
 *    distinct from `x` is itself a fact this family can catch (via check11)
 *    before this file's behavioural half has anything to compare.
 *
 * C. OPTIONS x QUANTIFIERS — U (ungreedy) inverts the greediness of `+` and
 *    `+?`, and unsetting it (`-U`) restores the default — verified via the
 *    MATCH SPAN pcrec's own `--emit-main` prints (`match START END`), not
 *    merely a match/no-match boolean, because greediness is invisible to a
 *    boolean verdict on a pattern that matches either way.
 *
 * D. SCOPING — the finding this file is built around (see below): a bare
 *    `(?i)` (no colon) is in effect from that point to the end of the
 *    ENCLOSING group, and MEASURED TO CROSS `|` — every branch of that
 *    group AFTER the setting point is affected, not just the branch the
 *    setting occurred in. A scoped `(?i:...)` restores at its OWN `)`, and
 *    covers every branch of ITS OWN alternation. A setting inside a NESTED
 *    group never leaks past that group's own close.
 *
 * E. RESET — `(?^)` restores every option to PCRE2's compiled default
 *    (not merely "off"; it is followed by nothing, and `(?^i)` resets
 *    everything AND THEN sets `i`, in that order).
 *
 * F. CAPTURE / `n` — `(?n)` silences auto-capturing `(...)` from that point
 *    (scoped exactly like i/m/s/x); a NAMED group still captures under it;
 *    `(?-n)` restores auto-capture. Measured via `--count-groups`
 *    (check02's own vehicle), not matching, because capture COUNT is not
 *    observable through `--emit-main`'s match/span output.
 *
 * *** THE FINDING THIS FILE'S SCOPING FAMILY EXISTS TO PIN ***
 * The naive, textbook-intuitive model of PCRE-family option scoping is "a
 * bare (?i) applies to the rest of its OWN branch, reset at the next `|`."
 * MEASURED AGAINST libpcre2 10.46, that model is WRONG: `^a(?i)b|c$` against
 * "C" MATCHES — the option set inside the first branch is still in effect
 * for the SECOND branch, because both branches belong to the same enclosing
 * group and `|` does not end that scope. (The scope DOES end at the
 * enclosing group's own close: `^(a(?i)b|c)d$` against "CD" does NOT match —
 * the `d` outside the group is unaffected.) A pcrec whose parser resets
 * option state at every `|` — the intuitive implementation — would pass
 * every SINGLE-BRANCH case in this file and fail exactly the two
 * ACROSS-`|` cases below, silently, because both sides agree everywhere
 * else. This is precisely the alphabet-inheritance risk D27 exists to
 * guard against: an author reading PCRE2's docs (or worse, recalling them)
 * is likely to reach for the intuitive-and-wrong model, and a test suite
 * derived from THAT SAME reading would agree with it.
 *
 * TWO CASES ARE ORACLE-ONLY BY DESIGN, NOT BY OMISSION (`a` and `r`, family
 * G below). Both letters are only OBSERVABLE under Unicode property mode
 * (PCRE2_UCP) — `(?a)` restricts `\w`/`\d` from Unicode categories back to
 * ASCII, and `(?r)` restricts caseless folding across the ASCII/non-ASCII
 * boundary (its very name in the registry's own note). pcrec's CLI exposes
 * `-e byte|utf8` (spelled `-e ascii|utf8` until [M5-SEAM]/D58) and no
 * UCP-equivalent flag; UTF8 encoding alone (multibyte
 * DECODING) does not imply Unicode CATEGORY tables. So there is currently no
 * pcrec surface a comparison for these two letters could even be pointed
 * at — family G measures the libpcre2 fact and floors the population, so a
 * regression in the ORACLE side is still caught today, and a pcrec
 * comparison can be wired in the moment a UCP-capable encoding surface
 * exists, with no edit to the measured facts themselves.
 *
 * PCREC-SIDE COMPARISON, where attempted: `--features modifiers -o FILE.c
 * --emit-main -- PATTERN`, then `gcc` the result and run it with the subject
 * as argv[1] (`match START END` / exit 0, or `nomatch` / exit 1 — pcrec's
 * own documented convention, confirmed live against the binary before this
 * file trusted it). PER-PROBE surface detection, exactly like check11: a
 * probe whose pcrec verdict is anything other than "requires module" counts
 * toward `compared`; while every probe here is refused identically
 * (measured TODAY: true), the whole check reports AWAITING-SURFACE with the
 * oracle side fully run.
 *
 * SABOTAGE (verified 2026-08-12, exact command in the suite's report). A
 * wrapper standing in for pcrec that delegates every invocation to the real
 * binary UNCHANGED, except that compiling `(?i)a` with `--emit-main`
 * produces a hand-written `main` performing a case-SENSITIVE search for
 * `a` — i.e. a matcher that accepts the construct but gets ITS SEMANTICS
 * wrong, the shape a real miscompile would take once the module lands.
 * Caught exactly and only there: `'(?i)a' vs 'A' (family letter_effect):
 * pcrec does NOT match, libpcre2 MATCHES`, naming the pattern, the subject,
 * and the family — every other case (which the stand-in passes through
 * unchanged) still agrees. The would-be scoping sabotage this header
 * originally described — a parser that resets option state at every `|` —
 * requires editing pcrec's own lowering, which a D27 writer denied `src/`
 * cannot fabricate as a stand-in the way check07's --features wrapper
 * could; the scoping family (D) is armed and will catch that shape of bug
 * the day the module's `|`-handling exists to be wrong, but this check has
 * not yet exercised that specific catch, and says so rather than claiming
 * a verification that did not happen.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check12 check12_modifier_semantics.c -ldl
 * Run:   check12 floors.txt registry.tsv [pcrec-path]
 */
#include "spec_common.h"
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

/* ------------------------------------------------------------ running argv
 * One general-purpose child-process runner: no shell, timeout-bounded,
 * captures stdout and stderr. Used both for pcrec and for the generated
 * binaries this check compiles from pcrec's own output. */

#define RUN_TIMEOUT_MS 4000

typedef struct { int ran; int timed_out; int exit_code; char out[512]; char err[512]; } Run;

static Run run_argv(const char *path, char *const argv[])
{
    Run r; memset(&r, 0, sizeof r);
    int opfd[2], epfd[2];
    if (pipe(opfd) != 0) return r;
    if (pipe(epfd) != 0) { close(opfd[0]); close(opfd[1]); return r; }
    pid_t pid = fork();
    if (pid < 0) { close(opfd[0]); close(opfd[1]); close(epfd[0]); close(epfd[1]); return r; }
    if (pid == 0) {
        close(opfd[0]); dup2(opfd[1], STDOUT_FILENO); close(opfd[1]);
        close(epfd[0]); dup2(epfd[1], STDERR_FILENO); close(epfd[1]);
        /* execvp, not execv: pcrec_path is always a resolved path (fine
         * either way), but $CC/"gcc" is ordinarily a bare command name that
         * only execvp's PATH search will find. */
        execvp(path, argv);
        _exit(127);
    }
    close(opfd[1]); close(epfd[1]);
    fcntl(opfd[0], F_SETFL, fcntl(opfd[0], F_GETFL, 0) | O_NONBLOCK);
    fcntl(epfd[0], F_SETFL, fcntl(epfd[0], F_GETFL, 0) | O_NONBLOCK);

    struct timespec deadline;
    clock_gettime(CLOCK_MONOTONIC, &deadline);
    deadline.tv_sec += RUN_TIMEOUT_MS / 1000;

    size_t to = 0, te = 0; int status = 0, exited = 0;
    for (;;) {
        pid_t w = waitpid(pid, &status, WNOHANG);
        if (w == pid) exited = 1;
        ssize_t n;
        while (to < sizeof r.out - 1 && (n = read(opfd[0], r.out + to, sizeof r.out - 1 - to)) > 0) to += (size_t)n;
        while (te < sizeof r.err - 1 && (n = read(epfd[0], r.err + te, sizeof r.err - 1 - te)) > 0) te += (size_t)n;
        if (exited) break;
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);
        if (now.tv_sec > deadline.tv_sec || (now.tv_sec == deadline.tv_sec && now.tv_nsec >= deadline.tv_nsec)) {
            kill(pid, SIGKILL); waitpid(pid, &status, 0); r.timed_out = 1; break;
        }
        struct timespec nap = {0, 2 * 1000 * 1000};
        nanosleep(&nap, NULL);
    }
    close(opfd[0]); close(epfd[0]);
    r.out[to] = 0; r.err[te] = 0; r.ran = 1;
    if (!r.timed_out) r.exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    return r;
}

/* --------------------------------------------------------------- scratch
 * A private working directory under $TMPDIR (default /var/tmp — /tmp is a
 * quota'd tmpfs on this box, same reason run_spec_mod0.sh uses it). */
static char workdir[512];

static void workdir_init(void)
{
    const char *base = getenv("TMPDIR");
    if (!base || !*base) base = "/var/tmp";
    snprintf(workdir, sizeof workdir, "%s/spec_mod0_c12.XXXXXX", base);
    if (!mkdtemp(workdir)) {
        fprintf(stderr, "FAIL[check12_modifier_semantics]: mkdtemp failed under '%s'\n", base);
        exit(2);
    }
}

static void workdir_cleanup(void)
{
    /* Best-effort: this suite is not part of `make test` and the runner's
     * own WORK dir cleanup does not reach into here, so this check tidies
     * up after itself rather than leaking files into $TMPDIR run after run. */
    char cmd[600];
    snprintf(cmd, sizeof cmd, "rm -rf '%s'", workdir);
    if (system(cmd) != 0) { /* best-effort; a leaked scratch dir costs nothing but disk */ }
}

typedef enum { VC_ACCEPTED, VC_UNIMPL, VC_INVALID, VC_ERROR } VClass;

static const char *pcrec_path;
static long compared, refused_unimpl;

/* Compiles PAT with --emit-main into a fresh .c file under workdir, and (if
 * accepted) gcc-builds it into a fresh binary. On success returns VC_ACCEPTED
 * and fills bin_path; caller runs the binary. */
static VClass build_pcrec_binary(const char *pat, char *bin_path, size_t bin_sz)
{
    static int seq;
    char c_path[560];
    snprintf(c_path, sizeof c_path, "%s/p%d.c", workdir, seq);
    snprintf(bin_path, bin_sz, "%s/p%d", workdir, seq);
    seq++;

    char *cargv[] = { (char *)pcrec_path, (char *)"--features", (char *)"modifiers",
                       (char *)"-o", c_path, (char *)"--emit-main",
                       (char *)"--", (char *)pat, NULL };
    Run r = run_argv(pcrec_path, cargv);
    if (!r.ran) { spec_fail("build_pcrec_binary: fork/exec failed for '%s'", pat); return VC_ERROR; }
    if (r.timed_out) { spec_fail("build_pcrec_binary: pcrec timed out on '%s'", pat); return VC_ERROR; }
    if (r.exit_code == 1) return strstr(r.err, "requires module '") ? VC_UNIMPL : VC_INVALID;
    if (r.exit_code != 0) {
        spec_fail("build_pcrec_binary: pcrec exited %d (expected 0 or 1) for '%s' (stderr: %s)",
                   r.exit_code, pat, r.err);
        return VC_ERROR;
    }

    const char *cc = getenv("CC"); if (!cc || !*cc) cc = "gcc";
    char *gargv[] = { (char *)cc, (char *)"-O1", (char *)"-o", bin_path, c_path, NULL };
    Run gr = run_argv(cc, gargv);
    if (!gr.ran || gr.timed_out || gr.exit_code != 0) {
        spec_fail("build_pcrec_binary: gcc failed to build pcrec's output for '%s' "
                  "(exit=%d stderr=%s) — pcrec ACCEPTED this pattern but its C is broken",
                  pat, gr.exit_code, gr.err);
        return VC_ERROR;
    }
    return VC_ACCEPTED;
}

/* Runs a pcrec-built binary against SUBJ. *matched is set from the exit
 * code; *start and *end are parsed from "match START END" when matched. */
static int run_pcrec_binary(const char *bin_path, const char *subj, int *matched,
                            size_t *start, size_t *end)
{
    char *argv[] = { (char *)bin_path, (char *)subj, NULL };
    Run r = run_argv(bin_path, argv);
    if (!r.ran || r.timed_out) return 0;
    if (r.exit_code == 0) {
        *matched = 1;
        if (sscanf(r.out, "match %zu %zu", start, end) != 2) return 0;
        return 1;
    }
    if (r.exit_code == 1) { *matched = 0; *start = *end = 0; return 1; }
    return 0;
}

/* ----------------------------------------------------- case A/B/D/E: match */

/* One (pattern, subject, predicted-match) case. Predicted against libpcre2
 * HERE (self-checking, like check11's probe()), then — when pcrec's surface
 * answers with something other than "requires module" — against pcrec's own
 * generated binary. */
static void case_match(const char *pat, const char *subj, int predict_match, const char *family)
{
    int got = spec_matches(pat, subj);
    if (got < 0) {
        spec_fail("PREDICTOR BROKEN for '%s' vs '%s' (family %s): does not "
                  "even compile under libpcre2 — fix this check's case list",
                  pat, subj, family);
        return;
    }
    if (got != predict_match)
        spec_fail("PREDICTOR WRONG for '%s' vs '%s' (family %s): predicted "
                  "%s, libpcre2 says %s — a bug in this check, not pcrec",
                  pat, subj, family, predict_match ? "MATCH" : "NO MATCH",
                  got ? "MATCH" : "NO MATCH");

    char bin[600];
    VClass vc = build_pcrec_binary(pat, bin, sizeof bin);
    if (vc == VC_ERROR) return;
    if (vc == VC_UNIMPL) { refused_unimpl++; return; }
    if (vc == VC_INVALID) {
        /* pcrec has an opinion but refuses the pattern outright: since
         * check11 owns whether this exact spelling should be recognised,
         * and every case here is chosen to be recognised (per check11's own
         * family A/C), a REFUSED-AS-INVALID here on a pattern this check
         * assumes is valid is itself worth surfacing. */
        spec_fail("'%s': pcrec REFUSED-AS-INVALID a pattern this check "
                  "assumes is syntactically valid (family %s) — is check11's "
                  "grammar assumption wrong, or is this a real pcrec bug?",
                  pat, family);
        compared++;
        return;
    }
    compared++;
    int matched = 0; size_t start = 0, end = 0;
    if (!run_pcrec_binary(bin, subj, &matched, &start, &end)) {
        spec_fail("'%s' vs '%s' (family %s): pcrec's own generated binary "
                  "did not run cleanly", pat, subj, family);
        return;
    }
    if (matched != predict_match)
        spec_fail("'%s' vs '%s' (family %s): pcrec %s, libpcre2 %s", pat, subj,
                   family, matched ? "MATCHES" : "does NOT match",
                   predict_match ? "MATCHES" : "does NOT match");
}

/* One (pattern, subject, predicted span) case — for greediness, where a
 * boolean verdict cannot see the difference. */
static void case_span(const char *pat, const char *subj, size_t exp_start, size_t exp_end,
                      const char *family)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    /* local compile+match to get libpcre2's own span, since spec_matches()
     * only returns a boolean */
    pcre2_code_8 *c = spec_abi.compile((PCRE2_SPTR)pat, strlen(pat), 0, &err, &eoff, NULL);
    if (!c) { spec_fail("PREDICTOR BROKEN: '%s' does not compile under libpcre2", pat); return; }
    pcre2_match_data_8 *md = spec_abi.match_data_create(16, NULL);
    int rc = spec_abi.match(c, (PCRE2_SPTR)subj, strlen(subj), 0, 0, md, NULL);
    size_t gs = 0, ge = 0;
    if (rc >= 0) {
        PCRE2_SIZE *ov = spec_abi.get_ovector_pointer(md);
        gs = ov[0]; ge = ov[1];
    }
    spec_abi.match_data_free(md); spec_abi.code_free(c);
    if (rc < 0 || gs != exp_start || ge != exp_end) {
        spec_fail("PREDICTOR WRONG for '%s' vs '%s' (family %s): predicted "
                  "span [%zu,%zu), libpcre2 gives %s[%zu,%zu)", pat, subj, family,
                  exp_start, exp_end, rc < 0 ? "NO MATCH " : "", gs, ge);
        return;
    }

    char bin[600];
    VClass vc = build_pcrec_binary(pat, bin, sizeof bin);
    if (vc == VC_ERROR) return;
    if (vc == VC_UNIMPL) { refused_unimpl++; return; }
    if (vc == VC_INVALID) {
        spec_fail("'%s': pcrec REFUSED-AS-INVALID a pattern this check "
                  "assumes is syntactically valid (family %s)", pat, family);
        compared++;
        return;
    }
    compared++;
    int matched = 0; size_t start = 0, end = 0;
    if (!run_pcrec_binary(bin, subj, &matched, &start, &end)) {
        spec_fail("'%s' vs '%s' (family %s): pcrec's own generated binary did not run cleanly",
                   pat, subj, family);
        return;
    }
    if (!matched || start != exp_start || end != exp_end)
        spec_fail("'%s' vs '%s' (family %s): pcrec gives %s[%zu,%zu), "
                  "libpcre2 gives [%zu,%zu)", pat, subj, family,
                   matched ? "" : "NO MATCH ", start, end, exp_start, exp_end);
}

/* ------------------------------------------------------------- case F: n */

static void case_capture(const char *pat, int predict_cc, const char *family)
{
    int cc = spec_capture_count(pat);
    if (cc < 0) { spec_fail("PREDICTOR BROKEN: '%s' does not compile under libpcre2", pat); return; }
    if (cc != predict_cc)
        spec_fail("PREDICTOR WRONG for '%s' (family %s): predicted capturecount %d, "
                  "libpcre2 says %d — a bug in this check, not pcrec", pat, family, predict_cc, cc);

    char *argv[] = { (char *)pcrec_path, (char *)"--features", (char *)"modifiers",
                      (char *)"--count-groups", (char *)"--", (char *)pat, NULL };
    Run r = run_argv(pcrec_path, argv);
    if (!r.ran) { spec_fail("case_capture: fork/exec failed for '%s'", pat); return; }
    if (r.timed_out) { spec_fail("case_capture: pcrec timed out on '%s'", pat); return; }
    if (r.exit_code == 1) {
        if (strstr(r.err, "requires module '")) { refused_unimpl++; return; }
        spec_fail("'%s' (family %s): pcrec REFUSED-AS-INVALID a pattern this "
                  "check assumes is valid", pat, family);
        compared++;
        return;
    }
    if (r.exit_code != 0) {
        spec_fail("case_capture: pcrec --count-groups exited %d (expected 0 or 1) "
                  "for '%s'", r.exit_code, pat);
        return;
    }
    compared++;
    char *end; errno = 0;
    long got = strtol(r.out, &end, 10);
    if (errno || end == r.out) {
        spec_fail("'%s' (family %s): pcrec --count-groups exited 0 but printed "
                  "unparseable stdout '%s'", pat, family, r.out);
        return;
    }
    if (got != predict_cc)
        spec_fail("'%s' (family %s): pcrec --count-groups reports %ld, libpcre2 "
                  "CAPTURECOUNT is %d", pat, family, got, predict_cc);
}

/* --------------------------------------------------- family G: oracle-only
 * Unicode-dependent letters (a, r) — no pcrec comparison attempted; see the
 * header for why. Measured with explicit PCRE2_UTF|PCRE2_UCP compile
 * options, which spec_common's helpers do not expose (they always compile
 * with options=0), so this family talks to the ABI directly. */
#define G_PCRE2_UTF 0x00080000u
#define G_PCRE2_UCP 0x00020000u

static void case_oracle_only(const char *pat, const char *subj, int predict_match, const char *note)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *c = spec_abi.compile((PCRE2_SPTR)pat, strlen(pat), G_PCRE2_UTF | G_PCRE2_UCP,
                                       &err, &eoff, NULL);
    if (!c) { spec_fail("oracle-only '%s': does not compile under UTF+UCP (err=%d)", pat, err); return; }
    pcre2_match_data_8 *md = spec_abi.match_data_create(16, NULL);
    int rc = spec_abi.match(c, (PCRE2_SPTR)subj, strlen(subj), 0, 0, md, NULL);
    spec_abi.match_data_free(md); spec_abi.code_free(c);
    int got = rc >= 0;
    if (got != predict_match)
        spec_fail("oracle-only '%s' vs subject (family oracle_only_unicode, %s): "
                  "predicted %s, libpcre2 says %s", pat, note,
                  predict_match ? "MATCH" : "NO MATCH", got ? "MATCH" : "NO MATCH");
}

/* ------------------------------------------------------------------- main */

int main(int argc, char **argv)
{
    const char *rp = NULL;
    spec_start("check12_modifier_semantics", argc, argv, &rp);

    pcrec_path = (argc >= 4 && argv[3][0]) ? argv[3] : getenv("PCREC");
    if (!pcrec_path || !*pcrec_path) pcrec_path = "build/pcrec";
    workdir_init();

    /* ---- family A: per-letter effect -------------------------------- */
    long f_letter = 0;
    case_match("(?i)a", "A", 1, "letter_effect"); f_letter++;
    case_match("a",     "A", 0, "letter_effect"); f_letter++;   /* control */
    case_match("(?m)^b", "a\nb", 1, "letter_effect"); f_letter++;
    case_match("^b",     "a\nb", 0, "letter_effect"); f_letter++;   /* control */
    case_match("(?m)a$", "a\nb", 1, "letter_effect"); f_letter++;
    case_match("a$",     "a\nb", 0, "letter_effect"); f_letter++;   /* control */
    case_match("(?s)a.b", "a\nb", 1, "letter_effect"); f_letter++;
    case_match("a.b",     "a\nb", 0, "letter_effect"); f_letter++;   /* control */
    case_match("(?x)a b", "ab",  1, "letter_effect"); f_letter++;
    case_match("a b",     "ab",  0, "letter_effect"); f_letter++;   /* control */
    case_match("a b",     "a b", 1, "letter_effect"); f_letter++;   /* control: x off, space literal, present */
    spec_pop("modsem.letter_effect", f_letter);

    /* ---- family B: options x classes (x vs doubled xx) ---------------- */
    long f_class = 0;
    case_match("(?x)[a b]",  " ", 1, "interaction_classes"); f_class++;   /* single x: space is DATA */
    case_match("(?xx)[a b]", " ", 0, "interaction_classes"); f_class++;   /* doubled x: space IGNORED */
    case_match("(?xx)[a b]", "a", 1, "interaction_classes"); f_class++;   /* control: a still literal */
    spec_pop("modsem.interaction_classes", f_class);

    /* ---- family C: options x quantifiers (U inverts +, +?) ------------ */
    long f_quant = 0;
    case_span("(?U)a+",  "aaa", 0, 1, "interaction_quantifiers"); f_quant++;
    case_span("a+",      "aaa", 0, 3, "interaction_quantifiers"); f_quant++;   /* control */
    case_span("(?U)a+?", "aaa", 0, 3, "interaction_quantifiers"); f_quant++;   /* U flips lazy to greedy too */
    case_span("a+?",     "aaa", 0, 1, "interaction_quantifiers"); f_quant++;   /* control */
    case_span("(?U)a+(?-U)b+", "aaabbb", 0, 6, "interaction_quantifiers"); f_quant++;   /* -U restores greediness */
    spec_pop("modsem.interaction_quantifiers", f_quant);

    /* ---- family D: scoping — see the header finding -------------------- */
    long f_scope = 0;
    /* D1/D2: leak ACROSS | to the end of the enclosing group (top level) */
    case_match("^a(?i)b|c$", "C",  1, "scoping"); f_scope++;   /* THE FINDING */
    case_match("^a(?i)b|c$", "AB", 0, "scoping"); f_scope++;
    /* D3/D4: leak across | WITHIN a parenthesised group, not past it */
    case_match("^(a(?i)b|c)$",  "C",  1, "scoping"); f_scope++;   /* THE FINDING, nested */
    case_match("^(a(?i)b|c)d$", "CD", 0, "scoping"); f_scope++;   /* ...but not past the group's own close */
    /* D5/D6: a SCOPED group's alternation is uniformly affected */
    case_match("^(?i:a|b)$", "A", 1, "scoping"); f_scope++;
    case_match("^(?i:a|b)$", "B", 1, "scoping"); f_scope++;
    /* D7/D8: a bare setting inside a nested group does not leak past its close */
    case_match("^(a(?i)b)c$", "abC", 0, "scoping"); f_scope++;
    case_match("^(a(?i)b)c$", "abc", 1, "scoping"); f_scope++;
    /* D9/D10: nested unset inside an outer scoped group */
    case_match("^(?i:a(?-i:b)c)$", "AbC", 1, "scoping"); f_scope++;
    case_match("^(?i:a(?-i:b)c)$", "ABC", 0, "scoping"); f_scope++;
    spec_pop("modsem.scoping", f_scope);

    /* ---- family E: reset (?^) ------------------------------------------ */
    long f_reset = 0;
    case_match("^(?i)a(?^)b$", "AB", 0, "reset"); f_reset++;   /* ^ turns i back off before b */
    case_match("^(?i)a(?^)b$", "Ab", 1, "reset"); f_reset++;
    case_match("^(?s)(?^i)a.b$", "A\nb", 0, "reset"); f_reset++;   /* ^ turns s off; dot no longer matches \n */
    case_match("^(?s)(?^i)a.b$", "Axb",  1, "reset"); f_reset++;   /* ...but ^i then turns i ON */
    spec_pop("modsem.reset", f_reset);

    /* ---- family F: capture / n ------------------------------------------ */
    long f_capture = 0;
    case_capture("(?n)(a)(b)",        0, "capture_n"); f_capture++;
    case_capture("(a)(?n)(b)",        1, "capture_n"); f_capture++;   /* n scoped: only what follows is silenced */
    case_capture("(?n)(a)(?-n)(b)",   1, "capture_n"); f_capture++;   /* -n restores auto-capture */
    case_capture("(?n:(a))(b)",       1, "capture_n"); f_capture++;   /* scoped n: only inside the group */
    case_capture("(?n)(?<k>a)(b)",    1, "capture_n"); f_capture++;   /* named groups still capture under n */
    spec_pop("modsem.capture_n", f_capture);

    /* ---- family G: oracle-only, Unicode-dependent (a, r) ---------------- */
    long f_unicode = 0;
    case_oracle_only("\\w",     "\xce\xb1", 1, "a: UCP \\w matches a Unicode letter, no restriction");
    case_oracle_only("(?a)\\w", "\xce\xb1", 0, "a: (?a) restricts \\w back to ASCII under UCP");
    case_oracle_only("(?a)\\w", "x",        1, "a: ...ASCII letters still match");
    case_oracle_only("(?i)k",   "\xe2\x84\xaa", 1, "r: Kelvin sign U+212A folds to 'k' under UCP+i, no r");
    case_oracle_only("(?ri)k",  "\xe2\x84\xaa", 0, "r: (?r) blocks the ASCII/non-ASCII caseless fold");
    case_oracle_only("(?ri)k",  "k",             1, "r: ...plain ASCII still matches");
    f_unicode = 6;
    spec_pop("modsem.oracle_only_unicode", f_unicode);

    workdir_cleanup();

    printf("  pcrec: %ld probe(s) compared, %ld refused-as-unimplemented "
           "(oracle_only_unicode's %ld are never sent to pcrec — no UCP surface exists yet)\n",
           compared, refused_unimpl, f_unicode);
    spec_pop("modsem.pcrec_compared", compared);
    spec_pop("modsem.pcrec_refused_unimpl", refused_unimpl);

    static const char *const owned[] = {
        "modsem.letter_effect", "modsem.interaction_classes",
        "modsem.interaction_quantifiers", "modsem.scoping", "modsem.reset",
        "modsem.capture_n", "modsem.oracle_only_unicode",
        "modsem.pcrec_compared", "modsem.pcrec_refused_unimpl"
    };
    spec_floors_require(owned, 9);
    if (spec_fails) return spec_finish();

    if (compared == 0)
        return spec_await(
            "the modifiers module accepting (or opinionatedly refusing) at "
            "least one pattern this check's cases assume is syntactically "
            "valid, so its BEHAVIOUR can be compared",
            "this check needs pcrec (under --features modifiers) to compile "
            "and run at least one of the letter/scoping/reset/interaction "
            "patterns above through --emit-main, or answer --count-groups "
            "for the capture_n family, with something other than the generic "
            "\"requires module 'modifiers'\" gate refusal. Until then every "
            "probe is refused identically, which tests the gate (check07's "
            "job), not what the letters DO (this check's job)");

    return spec_finish();
}
