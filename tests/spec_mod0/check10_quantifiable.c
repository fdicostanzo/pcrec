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
    long rows = 0, yes = 0;
    int row_q[256];
    for (int i = 0; i < spec_nrows; i++) {
        row_q[i] = quantifiable(spec_col(&spec_rows[i], SPEC_COL_SYNTAX));
        rows++;
        if (row_q[i]) yes++;
    }
    printf("  libpcre2 says quantifiable for %ld of %ld rows\n", yes, rows);
    spec_pop("quantifiable.rows", rows);

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
        "quantifiable.option_forms"
    };
    spec_floors_require(owned, 3);

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
    long compared = 0, formvalued = 0;
    for (int i = 0; i < spec_nrows; i++) {
        const SpecRow *r = &spec_rows[i];
        const char *val = r->col[qcol];
        const char *S = spec_col(r, SPEC_COL_SYNTAX);
        int is_yes = !strcmp(val, "yes") || !strcmp(val, "y") ||
                     !strcmp(val, "1") || !strcmp(val, "true");
        int is_no  = !strcmp(val, "no")  || !strcmp(val, "n") ||
                     !strcmp(val, "0") || !strcmp(val, "false");
        if (is_yes || is_no) {
            compared++;
            if (is_yes != row_q[i])
                spec_fail("row '%s': pcrec says quantifiable='%s', libpcre2 "
                          "says `a%s*` %s", S, val, S,
                          row_q[i] ? "COMPILES" : "does not compile");
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
    printf("  compared %ld two-valued rows; %ld form-resolved rows\n",
           compared, formvalued);
    spec_pop("quantifiable.compared_rows", compared);
    return spec_finish();
}
