/* check03_lexical.c — INVARIANT 3: LEXICAL membership, behavioural.
 *
 * THE PROMISE. "A row is LEXICAL iff `a<syntax>*` compiles and the quantifier
 * binds the preceding atom, per libpcre2 — swept over all 100 rows, so a
 * fourth lexical construct is FOUND, not assumed away."
 *
 * PREDICTOR, stated before the sweep ran:
 *   For each registry row's `syntax` S, S is LEXICAL iff
 *     (a) `a S *` compiles, AND
 *     (b) the `*` binds the atom BEFORE S, i.e. `^Z S *$` accepts "ZZ".
 *   Condition (b) alone is not enough: a construct that MATCHES a "Z" itself
 *   makes `^Z S *$` accept "ZZ" while the `*` binds the CONSTRUCT (`(?<n>a)`,
 *   `[[:alpha:]]` and `\w` all do this). So the membership test carries a
 *   control — `^Z S $` must NOT accept "ZZ" — which fails exactly when S ate
 *   the second Z on its own. Membership is (b) AND the control.
 *
 * WHY 'Z' AND NOT 'a'. The obvious probe, `^a S *$` against "aaa", is
 * confounded: 20 of the 100 rows pass it, because so many syntax probes in
 * the registry are spelled with a literal 'a' in them ((?<name>a), (a)(?-1),
 * (?+1)(a)) and therefore match the probe subject themselves. 'Z' appears in
 * no row's matchable text. That confound is measured, not assumed — the
 * check re-runs the naive probe and prints both counts, so the gap stays
 * visible instead of being a comment nobody can check.
 *
 * WHAT MAKES THIS A CHECK AND NOT A CENSUS. The sweep alone would pass on any
 * result. So the measured set is compared against a PINNED set (below), and
 * the check fails on any difference in either direction: a row that stops
 * being lexical, and — the direction the promise names — a FOURTH row that
 * becomes lexical. Growing the set is a deliberate one-line edit here.
 *
 * MEASURED RESULT, and a disagreement with the invariant statement: the
 * promise says "(Today: exactly three.)". Swept over all 100 rows against
 * libpcre2 10.46, exactly TWO rows satisfy the promise's own definition:
 * `\E` (row 26) and `(?#...)` (row 56). The third lexical-MODE construct,
 * `\Q` (row 25), fails clause (b) and it is not close: `a\Q*` does compile,
 * but quote mode turns the `*` into a LITERAL, so there is no quantifier to
 * bind anything. `^Z\Q*$` accepts exactly one string, "Z*$" — the `$` is
 * swallowed too. See the \Q cell printed below, which this check asserts
 * explicitly so the reason the count is two survives in the output.
 *
 * SABOTAGE (verified 2026-08-11, by building a copy against a modified
 * spec_common.h): change the control subject in spec_is_lexical() from "ZZ" to
 * "Z" and the control stops discriminating — 12 further rows are reported as
 * LEXICAL-and-not-pinned, 13 failures with the members floor. Corrupting the
 * pinned set fails in the other direction, naming the row libpcre2 no longer
 * agrees about.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check03 check03_lexical.c -ldl
 * Run:   check03 floors.txt registry.tsv
 */
#include "spec_common.h"

/* The pinned LEXICAL set, by `syntax` text. Adding to this list is how a
 * newly-found lexical construct gets accepted — deliberately, in review. */
static const char *const PINNED_LEXICAL[] = { "\\E", "(?#...)", NULL };

/* Membership is spec_is_lexical() in spec_common.h — the same function the
 * endpoint model (check08) uses for its first step, so the two checks cannot
 * drift apart on what "lexical" means. This wrapper only adds the
 * `a S *`-compiles flag, which this check reports as its own population. */
static int lexical_p(const char *S, int *compiles_out)
{
    char q[512];
    snprintf(q, sizeof q, "a%s*", S);
    *compiles_out = spec_compile(q).ok;
    return spec_is_lexical(S);
}

int main(int argc, char **argv)
{
    const char *rp = NULL;
    spec_start("check03_lexical", argc, argv, &rp);

    long swept = 0, compiles = 0, lexical = 0, naive = 0, controlled_out = 0;
    const char *found[64]; int nfound = 0;

    for (int i = 0; i < spec_nrows; i++) {
        const char *S = spec_col(&spec_rows[i], SPEC_COL_SYNTAX);
        int c = 0;
        swept++;
        int lex = lexical_p(S, &c);
        if (c) compiles++;

        /* the naive probe, re-run so the confound stays measured */
        char naive_pat[512];
        snprintf(naive_pat, sizeof naive_pat, "^a%s*$", S);
        int nv = c && spec_matches(naive_pat, "aaa") == 1;
        if (nv) naive++;
        if (nv && !lex) controlled_out++;

        if (!lex) continue;
        lexical++;
        if (nfound < 64) found[nfound++] = S;
    }

    printf("  rows swept %ld; `a S *` compiles for %ld; LEXICAL %ld\n",
           swept, compiles, lexical);
    printf("  naive probe (^a S *$ vs \"aaa\") would have said %ld; "
           "the control excludes %ld of them\n", naive, controlled_out);
    printf("  LEXICAL set:");
    for (int i = 0; i < nfound; i++) printf(" %s", found[i]);
    printf("\n");

    spec_pop("lexical.rows_swept", swept);
    spec_pop("lexical.quantifier_compiles", compiles);
    spec_pop("lexical.members", lexical);
    spec_pop("lexical.control_exclusions", controlled_out);

    /* measured set == pinned set, both directions */
    for (int i = 0; PINNED_LEXICAL[i]; i++) {
        int seen = 0;
        for (int j = 0; j < nfound; j++)
            if (!strcmp(found[j], PINNED_LEXICAL[i])) seen = 1;
        if (!seen)
            spec_fail("row '%s' is PINNED lexical but libpcre2 no longer "
                      "agrees — the construct's binding changed",
                      PINNED_LEXICAL[i]);
    }
    for (int j = 0; j < nfound; j++) {
        int pinned = 0;
        for (int i = 0; PINNED_LEXICAL[i]; i++)
            if (!strcmp(found[j], PINNED_LEXICAL[i])) pinned = 1;
        if (!pinned)
            spec_fail("row '%s' is LEXICAL by measurement and is NOT pinned — "
                      "this is the fourth-construct case the invariant exists "
                      "to catch. Confirm it, then add it to PINNED_LEXICAL",
                      found[j]);
    }

    /* The \Q cell, asserted rather than annotated: the invariant says three
     * and the measurement says two, and the whole of the difference is this
     * row. If \Q ever starts binding, this fires and the count is revisited. */
    {
        int c = 0;
        int lex = lexical_p("\\Q", &c);
        int only = spec_matches("^Z\\Q*$", "Z*$");
        printf("  \\Q cell: `a\\Q*` compiles=%d, LEXICAL=%d, "
               "`^Z\\Q*$` accepts \"Z*$\"=%d\n", c, lex, only);
        if (!c || lex || only != 1)
            spec_fail("the \\Q cell moved: expected compiles=1 lexical=0 "
                      "quoted-literal=1, got %d/%d/%d. The invariant's "
                      "\"exactly three\" counts \\Q as lexical-MODE; under the "
                      "invariant's own binding definition it is not a member, "
                      "and this cell is why", c, lex, only);
        spec_pop("lexical.qe_cell", 1);
    }

    static const char *const owned[] = {
        "lexical.rows_swept", "lexical.quantifier_compiles", "lexical.members",
        "lexical.control_exclusions", "lexical.qe_cell"
    };
    spec_floors_require(owned, 5);
    return spec_finish();
}
