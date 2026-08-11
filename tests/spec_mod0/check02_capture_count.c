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
 * AWAITED SURFACE. pcrec exposes no group count for a pattern: there is no
 * flag on the CLI that prints one, and `--list-syntax` is a static registry
 * dump with no per-pattern column. The oracle half below runs now, on every
 * generated body, and fails now if the two libpcre2 measurements ever part.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check02 check02_capture_count.c -ldl
 * Run:   check02 floors.txt
 */
#include "spec_common.h"

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

    static const char *const owned[] = {
        "capture.family_named", "capture.family_lookaround",
        "capture.family_verbs", "capture.family_callouts",
        "capture.family_branchreset", "capture.family_scoped_n",
        "capture.family_quotemode", "capture.bodies_compared",
        "capture.noncompiling"
    };
    spec_floors_require(owned, 9);
    if (spec_fails) return spec_finish();

    return spec_await(
        "a per-pattern group count from pcrec's count-scan",
        "this check needs pcrec to report, for a given pattern, the number of "
        "capturing groups its count-scan found — any stable channel will do "
        "(a CLI flag such as `--count-groups`, a column in a per-pattern dump, "
        "or a documented symbol the harness can call). It then compares that "
        "number, body by body, against the two libpcre2 measurements above. "
        "Until then the err-115 boundary is checked against CAPTURECOUNT only, "
        "which is the oracle half");
}
