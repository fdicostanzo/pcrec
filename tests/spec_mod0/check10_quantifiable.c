/* check10_quantifiable.c — INVARIANT 10: quantifiability.
 *
 * THE PROMISE. "The per-row `quantifiable` fact matches libpcre2's `a<syntax>*`
 * verdict, all 100 rows."
 *
 * PREDICTOR, stated before the run. For each registry row, libpcre2's verdict
 * on `a<syntax>*` is two-valued — it compiles, or it does not — and pcrec's
 * per-row `quantifiable` fact must agree with it on all 100 rows. A row whose
 * fact is neither yes nor no (a third, "depends on the form" value) is only
 * justified if the row's construct FAMILY actually contains both a form that
 * takes a quantifier and a form that does not; this check computes the two
 * form sweeps below and refuses a third-value row that cannot show both.
 *
 * WHY THE ROW PROBE IS NOT THE WHOLE STORY — the measurement that shaped this.
 * A registry row carries ONE `syntax` probe, and for two families that probe
 * is not representative of the row:
 *
 *   the verb row (kind=verb, syntax `(*ACCEPT)`) — swept over all 50 names in
 *     `pcrec --list-verbs`, 18 take a quantifier and 32 do not. The row's own
 *     probe is one of the 18: `a(*ACCEPT)*` COMPILES while `a(*FAIL)*` is err
 *     109, though ACCEPT and FAIL sit in the same table with identical `forms`
 *     text. So the split is not upper-vs-lower case, and reading the row probe
 *     alone would record "quantifiable" for a row whose majority is not.
 *
 *   the option-run rows (`(?i)` and its siblings) — the bare option run
 *     `a(?i)*` is err 109, the scoped form `a(?i:b)*` compiles. Same family,
 *     opposite verdicts, and the registry probes only the bare form.
 *
 * Both sweeps run every time and print their populations, so the third value
 * is checked against measurement rather than accepted on assertion.
 *
 * AWAITED SURFACE. pcrec exposes no `quantifiable` fact today: `--list-syntax`
 * prints 12 columns (kind selector syntax module feature flavours engines
 * status diag flags expect note) and none of them is it. The oracle half below
 * — all 100 row verdicts, both form sweeps, all populations — runs now and
 * fails now if libpcre2 moves. The comparison lands the moment a column named
 * `quantifiable` appears in the dump's header; the check finds it BY NAME, so
 * no edit here is needed when it does.
 *
 * SABOTAGE (verified): none possible on the pcrec side until the column
 * exists — which is the point of failing loudly rather than skipping. On the
 * oracle side, drop `(*ACCEPT)` from the verb sweep and the verb population
 * falls below its floor; change the option-form list to only bare forms and
 * the both-outcomes assertion for that family fails.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check10 check10_quantifiable.c -ldl
 * Run:   check10 floors.txt registry.tsv verbs.tsv
 */
#include "spec_common.h"


/* ---- the two LEXICAL discriminators -------------------------------------
 *
 * Invariant 10's fourth cell value, `lexical`, means: quantifying the row's
 * syntax does not create a quantifier for the CONSTRUCT at all. Two measured
 * ways that happens, and a `lexical` cell is legitimate iff one of them holds:
 *
 *   D1  the `*` binds the PRECEDING atom, transparently — spec_is_lexical(),
 *       the same test check03 pins its membership with (`\E`, `(?#...)`);
 *
 *   D2  the `*` stops being a quantifier at all: it becomes a LITERAL. `a\Q*`
 *       compiles, but quote mode has swallowed the star, so nothing was
 *       quantified. This is the discriminator behind finding A.
 *
 * A plain `yes` FAILS on a row satisfying EITHER discriminator. Both are the
 * same mistake reached by different routes: the row compiles under a star, so
 * a check that only asked "does it compile" records `yes`, but in neither case
 * is the CONSTRUCT what got quantified. D1's star bound the atom before it;
 * D2's star is not a quantifier at all. The compile verdict is silent on the
 * question the column asks.
 *
 * HOW D2 IS MEASURED WITHOUT ASSUMING THE ANSWER. The tempting test —
 * "`^Z S *$` does not accept 'Z'" — is wrong: it fires for every row whose
 * syntax contains a mandatory consuming atom, and `(a)(?-1)` is not lexical.
 * The property that actually separates them is monotonicity:
 *
 *      A quantifier with a minimum of zero can only ADD strings to a
 *      language. It can never remove one.
 *
 * So D2 is witnessed when adding the `*` REMOVES a string: some subject that
 * `^Z S $` accepts and `^Z S *$` rejects. For `\Q` the witness is "Z$" —
 * accepted without the star (quote mode makes the `$` a literal), rejected
 * with it (the language becomes exactly {"Z*$"}). For a genuine quantifier no
 * such witness can exist, whatever S consumes.
 *
 * The witness is hunted over a generated subject set, so D2 is TRUE only when
 * a removal is actually seen; failing to find one leaves D2 false, which is
 * the safe direction. Rows whose unquantified pattern accepts nothing within
 * the bound are counted and printed, so that vacuity is visible rather than
 * silently reading as "not lexical".
 */
/* The witness search space. Two tuning decisions, both measured:
 *
 * NO TRAILING `$`. Anchoring the probe at both ends makes many rows' languages
 * EMPTY within any small bound — `^Z(?=...)$` accepts nothing at all, because
 * the lookahead needs three characters that the `$` forbids — and an empty
 * language witnesses nothing. Leaving the tail unanchored keeps the witness
 * logic intact (a zero-minimum quantifier still only adds strings) while
 * cutting the unreachable rows from 19 to the handful printed below.
 *
 * THE ALPHABET carries whitespace and a NUL-adjacent control because \s, \h,
 * \v, \R, \cX and \0 are rows whose languages contain nothing else. */
/* The witness search space. Three tuning decisions, all measured against the
 * count of rows the search could not reach (printed every run):
 *
 * NO TRAILING `$`. Anchoring the probe at both ends makes many rows' languages
 * EMPTY within any small bound — `^Z(?=...)$` accepts nothing at all, because
 * the lookahead needs three characters the `$` forbids — and an empty language
 * witnesses nothing. Leaving the tail unanchored keeps the witness logic
 * intact (a zero-minimum quantifier still only ADDS strings) and took the
 * unreachable rows from 19 to 12.
 *
 * A BYTE ARRAY, NOT A STRING. The alphabet has to contain NUL and a control
 * byte, because `\0` and `\cX` are rows whose languages contain nothing else;
 * neither can live in a C string literal.
 *
 * A STRUCTURED SET FIRST. Six rows are the `(a)^N(?-N)` family, whose shortest
 * accepted subject is "Z" followed by N+1 'a's — length 10 for `(?-9)`, far
 * past any affordable brute-force bound (10 bytes to the 10th). Enumerating
 * that shape directly costs 13 probes and clears all six, where raising
 * D2_MAXLEN to reach them would cost ten seconds. Cheap and targeted first,
 * exhaustive-within-a-bound second. */
static const unsigned char D2_ALPHA[] = {
    'Z', 'a', '*', '0', 'A', ' ', '\t', '\n', 0x18, 0x00
};
#define D2_NALPHA ((int)(sizeof D2_ALPHA))
#define D2_MAXLEN 5
#define D2_UNMEASURED_CEILING 4

static long d2_vacuous;
static int d2_was_vacuous;   /* set per call: no accepted subject in bound */

/* One subject: does it witness a removal? Returns 1 on witness, and sets
 * *accepted when the unquantified pattern accepts it at all. */
static int d2_try(const SpecPat *pn, const SpecPat *pq,
                  const char *s, size_t len, int *accepted)
{
    if (!spec_pat_match(pn, s, len)) return 0;
    *accepted = 1;
    return !spec_pat_match(pq, s, len);
}

static int star_became_literal(const char *S)
{
    char q[512], noq[512], quant[512];
    snprintf(q,     sizeof q,     "a%s*", S);
    snprintf(noq,   sizeof noq,   "^Z%s", S);
    snprintf(quant, sizeof quant, "^Z%s*", S);
    d2_was_vacuous = 0;
    if (!spec_compile(q).ok) return 0;

    SpecPat pn, pq;
    if (!spec_pat_open(&pn, noq)) return 0;
    if (!spec_pat_open(&pq, quant)) { spec_pat_close(&pn); return 0; }

    int witnessed = 0, accepted_any = 0;

    /* structured set: "Z" then k 'a's, and the same behind a literal star */
    char sb[32];
    for (int k = 0; k <= 12 && !witnessed; k++) {
        sb[0] = 'Z';
        for (int i = 0; i < k; i++) sb[1 + i] = 'a';
        witnessed = d2_try(&pn, &pq, sb, (size_t)(1 + k), &accepted_any);
        if (witnessed) break;
        sb[1] = '*';
        for (int i = 0; i < k; i++) sb[2 + i] = 'a';
        witnessed = d2_try(&pn, &pq, sb, (size_t)(2 + k), &accepted_any);
    }

    /* exhaustive within the bound */
    char buf[D2_MAXLEN + 1];
    for (int len = 0; len <= D2_MAXLEN && !witnessed; len++) {
        long total = 1;
        for (int i = 0; i < len; i++) total *= D2_NALPHA;
        for (long n = 0; n < total && !witnessed; n++) {
            long v = n;
            for (int i = 0; i < len; i++) {
                buf[i] = (char)D2_ALPHA[v % D2_NALPHA];
                v /= D2_NALPHA;
            }
            witnessed = d2_try(&pn, &pq, buf, (size_t)len, &accepted_any);
        }
    }

    if (!accepted_any) { d2_vacuous++; d2_was_vacuous = 1; }
    spec_pat_close(&pn);
    spec_pat_close(&pq);
    return witnessed;
}

static int quantifiable(const char *syntax)
{
    char pat[512];
    snprintf(pat, sizeof pat, "a%s*", syntax);
    return spec_compile(pat).ok;
}

/* A family's form sweep: how many forms take a quantifier, how many do not,
 * and how many could not be asked (the form itself does not compile, so its
 * quantifiability is undefined rather than false — counted separately so it
 * never masquerades as a "no"). */
typedef struct { long yes, no, undefined; } FormSplit;

static FormSplit sweep_verbs(const char *path, long *nnames)
{
    FormSplit s = {0, 0, 0};
    FILE *f = fopen(path, "r");
    if (!f) {
        fprintf(stderr, "FAIL: cannot open verb dump '%s'\n", path);
        exit(2);
    }
    char line[512];
    while (fgets(line, sizeof line, f)) {
        char tab[32], name[160], forms[256];
        if (line[0] == '#') continue;
        if (sscanf(line, "%31s %159s %255s", tab, name, forms) < 3) continue;
        (*nnames)++;
        int lower = !strcmp(tab, "lower");
        char base[256], quant[256];
        snprintf(base,  sizeof base,  lower ? "a(*%s:b)"  : "a(*%s)",  name);
        snprintf(quant, sizeof quant, lower ? "a(*%s:b)*" : "a(*%s)*", name);
        if (!spec_compile(base).ok) { s.undefined++; continue; }
        if (spec_compile(quant).ok) s.yes++; else s.no++;
    }
    fclose(f);
    return s;
}

static const char *const OPTION_FORMS[] = {
    "(?i)", "(?i:b)", "(?i-m)", "(?i-m:b)", "(?^)", "(?^i:b)",
    "(?x)", "(?x:b)", "(?n)", "(?n:b)", NULL
};

static FormSplit sweep_options(long *nforms)
{
    FormSplit s = {0, 0, 0};
    for (int i = 0; OPTION_FORMS[i]; i++) {
        (*nforms)++;
        char base[128];
        snprintf(base, sizeof base, "a%s", OPTION_FORMS[i]);
        if (!spec_compile(base).ok) { s.undefined++; continue; }
        if (quantifiable(OPTION_FORMS[i])) s.yes++; else s.no++;
    }
    return s;
}

int main(int argc, char **argv)
{
    const char *rp = NULL;
    spec_start("check10_quantifiable", argc, argv, &rp);
    if (argc < 4) {
        fprintf(stderr, "FAIL: need floors.txt registry.tsv verbs.tsv\n");
        return 2;
    }

    /* ---- oracle half: all 100 rows ------------------------------------- */
    long rows = 0, yes = 0, d1_rows = 0, d2_rows = 0;
    int row_q[256], row_d1[256], row_d2[256], row_vac[256];
    for (int i = 0; i < spec_nrows; i++) {
        const char *S = spec_col(&spec_rows[i], SPEC_COL_SYNTAX);
        row_q[i]  = quantifiable(S);
        row_d1[i] = spec_is_lexical(S);
        row_d2[i] = star_became_literal(S);
        row_vac[i] = d2_was_vacuous;
        rows++;
        if (row_q[i])  yes++;
        if (row_d1[i]) d1_rows++;
        if (row_d2[i]) d2_rows++;
    }
    printf("  libpcre2 says quantifiable for %ld of %ld rows\n", yes, rows);
    printf("  LEXICAL discriminators: D1 (star binds the preceding atom) %ld "
           "row(s); D2 (star became a literal) %ld row(s)\n", d1_rows, d2_rows);
    printf("  D2 witness search: %ld row(s) had no accepted subject within "
           "the bound (alphabet %zu bytes, length <= %d) — D2 left false there, "
           "which is the safe direction\n",
           d2_vacuous, (size_t)D2_NALPHA, D2_MAXLEN);
    for (int i = 0; i < spec_nrows; i++) {
        if (!row_d1[i] && !row_d2[i]) continue;
        printf("    LEXICAL-eligible row %-12s D1=%d D2=%d\n",
               spec_col(&spec_rows[i], SPEC_COL_SYNTAX), row_d1[i], row_d2[i]);
    }
    /* The rows D2 could not reach, named rather than only counted. D2 is a
     * WITNESS search: no witness leaves it false, so a row whose unquantified
     * pattern accepts nothing in the bound is UNMEASURED, not measured-false.
     * A `lexical` cell on such a row still fails (D1 and D2 both false, which
     * is the safe direction); the residual risk is the other way — a genuinely
     * D2 row marked `yes` whose witness the bound missed — so the rows where
     * that could hide are listed. A row whose quantified form does not compile
     * at all cannot be D2 and is not at risk. */
    {
        long at_risk = 0;
        for (int i = 0; i < spec_nrows; i++) {
            if (!row_vac[i] || !row_q[i]) continue;
            at_risk++;
            printf("    D2 UNMEASURED (quantified form compiles) row %s\n",
                   spec_col(&spec_rows[i], SPEC_COL_SYNTAX));
        }
        printf("  D2 unmeasured rows where a false `yes` could hide: %ld\n",
               at_risk);
        spec_pop("quantifiable.d2_unmeasured_at_risk", at_risk);
        /* A CEILING, not a floor. floors.txt pins minima, which is the right
         * shape for a population — more comparing is better. This number is
         * the opposite: it is the size of the blind spot, and it must not grow
         * quietly. The four rows at the ceiling today are `(?<=...)`,
         * `(?<*a)`, `(?R)` and `(?0)`, whose languages are empty for
         * structural reasons (unbounded recursion, and a lookbehind that
         * cannot be satisfied after `^Z`) rather than because the search bound
         * is too small — widening the alphabet or the length will not reach
         * them. */
        if (at_risk > D2_UNMEASURED_CEILING)
            spec_fail("D2 could not be measured for %ld rows whose quantified "
                      "form compiles, above the ceiling of %d. The blind spot "
                      "grew: a genuinely star-is-literal row could now be "
                      "marked `yes` without this check noticing",
                      at_risk, D2_UNMEASURED_CEILING);
    }
    spec_pop("quantifiable.rows", rows);
    spec_pop("quantifiable.lexical_d1_rows", d1_rows);
    spec_pop("quantifiable.lexical_d2_rows", d2_rows);

    /* ---- oracle half: the two form sweeps ------------------------------ */
    long nverbs = 0, nopts = 0;
    FormSplit v = sweep_verbs(argv[3], &nverbs);
    FormSplit o = sweep_options(&nopts);
    printf("  verb-name forms:   %ld names -> %ld quantifiable, %ld not, "
           "%ld undefined (the form itself does not compile)\n",
           nverbs, v.yes, v.no, v.undefined);
    printf("  option-run forms:  %ld forms -> %ld quantifiable, %ld not, "
           "%ld undefined\n", nopts, o.yes, o.no, o.undefined);
    spec_pop("quantifiable.verb_forms", nverbs);
    spec_pop("quantifiable.option_forms", nopts);

    /* Both families must genuinely show both outcomes — that is what licenses
     * a third value on those rows, and it is measured on every run rather than
     * asserted once in a comment. */
    if (v.yes == 0 || v.no == 0)
        spec_fail("the verb family no longer shows both outcomes (%ld yes, "
                  "%ld no): a form-resolved `quantifiable` value for the verb "
                  "row would be unjustified", v.yes, v.no);
    if (o.yes == 0 || o.no == 0)
        spec_fail("the option-run family no longer shows both outcomes "
                  "(%ld yes, %ld no)", o.yes, o.no);

    /* The specific cell that makes the verb row's own probe unrepresentative.
     * Pinned so the reason survives: if ACCEPT and FAIL ever agree, the row
     * probe becomes representative and this check should be revisited. */
    {
        int accept = spec_compile("a(*ACCEPT)*").ok;
        int fail_  = spec_compile("a(*FAIL)*").ok;
        printf("  row-probe cell: a(*ACCEPT)* compiles=%d, a(*FAIL)* "
               "compiles=%d\n", accept, fail_);
        if (!(accept == 1 && fail_ == 0))
            spec_fail("the (*ACCEPT)/(*FAIL) split moved (accept=%d fail=%d) — "
                      "the verb row's syntax probe was unrepresentative of its "
                      "own family because of exactly this cell", accept, fail_);
    }

    static const char *const owned[] = {
        "quantifiable.rows", "quantifiable.verb_forms",
        "quantifiable.option_forms", "quantifiable.lexical_d1_rows",
        "quantifiable.lexical_d2_rows", "quantifiable.d2_unmeasured_at_risk"
    };
    spec_floors_require(owned, 6);

    /* ---- pcrec half: awaited ------------------------------------------- */
    int qcol = spec_col_index("quantifiable");
    if (qcol < 0)
        return spec_await(
            "a per-row `quantifiable` fact in `pcrec --list-syntax`",
            "this check looks for a column literally named `quantifiable` in "
            "the dump's header line, then compares it row by row against the "
            "libpcre2 verdicts computed above. Two-valued cells must equal the "
            "row's own `a<syntax>*` verdict; a third, form-resolved value is "
            "accepted only for a row whose family form sweep above shows both "
            "outcomes (today: the verb row and the option-run rows)");

    /* The column exists: compare. Reached only once the surface lands. */
    long compared = 0, formvalued = 0, lexvalued = 0, unknownvalued = 0;
    for (int i = 0; i < spec_nrows; i++) {
        const SpecRow *r = &spec_rows[i];
        const char *val = r->col[qcol];
        const char *S = spec_col(r, SPEC_COL_SYNTAX);
        int is_yes = !strcmp(val, "yes") || !strcmp(val, "y") ||
                     !strcmp(val, "1") || !strcmp(val, "true");
        int is_no  = !strcmp(val, "no")  || !strcmp(val, "n") ||
                     !strcmp(val, "0") || !strcmp(val, "false");
        /* the fourth cell value: `lexical` */
        if (!strcmp(val, "lexical")) {
            lexvalued++;
            if (!row_d1[i] && !row_d2[i])
                spec_fail("row '%s' has quantifiable='lexical', but neither "
                          "discriminator holds: D1 (the star binds the "
                          "PRECEDING atom) is false, and D2 (the star became a "
                          "LITERAL — no subject is removed by adding it) is "
                          "false. `a%s*` %s. A `lexical` cell is legitimate "
                          "only where quantifying does not create a quantifier "
                          "for the construct, and here it does",
                          S, S, row_q[i] ? "compiles" : "does not compile");
            continue;
        }

        if (is_yes || is_no) {
            compared++;
            /* THE FALSE YES. `a\Q*` compiles, so a check that only asked
             * "does it compile" would record `yes`. But the star there is a
             * literal: adding it REMOVES subjects from the language, which a
             * quantifier with a minimum of zero cannot do. The construct is
             * not repeatable, and the compile verdict says nothing about
             * whether it is. */
            if (is_yes && row_d2[i]) {
                spec_fail("row '%s' has quantifiable='yes', but D2 holds: the "
                          "star is a LITERAL there — adding it removes "
                          "subjects from the language. `a%s*` compiling is a "
                          "FALSE YES; the construct is not repeatable and the "
                          "cell should be 'lexical'", S, S);
                continue;
            }
            if (is_yes && row_d1[i]) {
                spec_fail("row '%s' says 'yes' and D1 holds — the star binds "
                          "the preceding atom, not the construct. 'lexical' is "
                          "the accurate cell", S);
                continue;
            }
            if (is_yes != row_q[i])
                spec_fail("row '%s': pcrec says quantifiable='%s', libpcre2 "
                          "says `a%s*` %s", S, val, S,
                          row_q[i] ? "COMPILES" : "does not compile");
            continue;
        }
        /* Anything else must be the third value, `form`. An unrecognised
         * value is a hard failure and not a shrug: this check can only compare
         * vocabulary it knows, and a value it silently routed into the
         * form-resolved branch would be "checked" by a test that never looked
         * at it. A placeholder is not a verdict. */
        if (strcmp(val, "form") != 0) {
            unknownvalued++;
            spec_fail("row '%s' has quantifiable='%s', which is not one of the "
                      "legal cell values {yes, no, form, lexical}. libpcre2 "
                      "says `a%s*` %s, so the row does have an answer",
                      S, val, S, row_q[i] ? "COMPILES" : "does not compile");
            continue;
        }

        /* third value: form-resolved. Only the two measured families qualify. */
        formvalued++;
        int is_verb = !strcmp(spec_col(r, SPEC_COL_KIND), "verb");
        int is_option = strstr(S, "(?") == S && !strchr(S, ':');
        if (is_verb) {
            if (v.yes == 0 || v.no == 0)
                spec_fail("row '%s' claims a form-resolved quantifiability, "
                          "but the verb form sweep does not show both "
                          "outcomes", S);
        } else if (is_option) {
            if (o.yes == 0 || o.no == 0)
                spec_fail("row '%s' claims a form-resolved quantifiability, "
                          "but the option-run form sweep does not show both "
                          "outcomes", S);
        } else {
            spec_fail("row '%s' has quantifiable='%s', which is neither a "
                      "two-valued verdict nor a family this check has a form "
                      "population for — add its form sweep before the third "
                      "value can mean anything", S, val);
        }
    }
    printf("  compared %ld two-valued rows; %ld form-resolved rows; "
           "%ld lexical rows; %ld rows with an unrecognised value\n",
           compared, formvalued, lexvalued, unknownvalued);
    spec_pop("quantifiable.compared_rows", compared);
    spec_pop("quantifiable.lexical_cells", lexvalued);
    return spec_finish();
}
