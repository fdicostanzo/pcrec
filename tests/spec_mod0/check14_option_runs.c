/* check14_option_runs.c — the `(?...)` OPTION RUN as a GENERATED space:
 * every byte at every position of the run, every placement and count of the
 * two markers, every terminator, every truncation, and — the family this
 * check was written to reach — every accepted spelling with a quantifier
 * after it.
 *
 * THIS CHECK IS D27 (spec-first, blinded from src/, docs/ and the rest of
 * tests/), written 2026-08-12 in the MOD-0.8b pass. It overlaps check11 on
 * purpose and differs from it in one respect that turned out to be the whole
 * value: check11's structural family is a HAND-LISTED table of 21 spellings,
 * and this one GENERATES its spellings. A hand-listed table stops at its
 * author's imagination. The generated one does not, and the first thing it
 * found is recorded under FINDING below.
 *
 * WHAT CHANGED SINCE check11 WAS WRITTEN. check11's header says every probe
 * comes back "requires module 'modifiers'" and the check is therefore
 * AWAITING-SURFACE. That is no longer true: the modifiers module is
 * implemented, `pcrec --features modifiers -o - 'a(?i)b'` succeeds, and every
 * cell below is a live comparison rather than a deferred one. This check is
 * armed from its first run.
 *
 * ------------------------------------------------------------- the promise
 *
 *   T1 (exact) pcrec must not ACCEPT what PCRE2 REJECTS. A pattern PCRE2
 *      refuses has no meaning to be faithful to, so whatever pcrec emits for
 *      it is a matcher for a language PCRE2 never defined. This is the
 *      strongest clause here and the one that fails today.
 *   T2 (exact) pcrec must not refuse as INVALID what PCRE2 ACCEPTS. It may
 *      refuse it as unimplemented or as out of pcrec's scope — both of those
 *      say the construct is REAL — but calling a real construct bad syntax is
 *      a grammar quieter than PCRE2's, which D26 puts in the exact tier.
 *   T3 (exact) A refusal emits no C. Measured as a byte count on stdout, not
 *      inferred from the exit code.
 *   T4 (not exact) The wording. Nothing here compares pcrec's sentence with
 *      PCRE2's; the message text is used only to sort a refusal into
 *      unimplemented / out-of-scope / invalid.
 *
 * ============================== FINDING =================================
 *
 * A QUANTIFIER APPLIED TO A BARE OPTION RUN IS ACCEPTED BY pcrec AND IS
 * ERROR 109 IN libpcre2, AND THE CODE pcrec EMITS MATCHES.
 *
 *     $ build/pcrec --features modifiers --emit-main -o /tmp/q.c 'a(?i)*'
 *     $ echo $?                        # 0 — and /tmp/q.c is a real matcher
 *     libpcre2: error 109 at offset 5  # "quantifier does not follow a
 *                                      #  repeatable item"
 *
 * Compiled and run, the emitted matcher accepts "a", "aa" and "aaa": the `*`
 * was bound to the preceding `a`, i.e. the bare option run was modelled as a
 * LEXICAL construct that contributes no atom, exactly like `\E` or `(?#...)`.
 * That is the intuitive model and it is wrong — PCRE2 does not let a
 * quantifier past an option run at all. `a(?i)**` is even diagnosed by pcrec
 * as "multiple quantifiers on the same item", which is the same wrong model
 * speaking twice.
 *
 * The SCOPING form is not affected and is this family's built-in control:
 * `a(?i:b)*` compiles under both, so the family cannot be dismissed as a
 * sweep that disagrees with everything. Of the 7,040 (spelling x quantifier)
 * cells run while this file was written, 4,472 disagreed and 2,568 agreed,
 * and the split is exactly bare-run versus scoping-run with no exceptions.
 *
 * pcrec's OWN REGISTRY already carries the right answer: every `modifiers`
 * row's `quantifiable` cell reads `form`, meaning quantifiability depends on
 * which form the construct takes. The producer disagrees with the registry.
 *
 * This check therefore FAILS today, on this family and nothing else. That is
 * the intended state: the assertion is pinned to what PCRE2 requires, not to
 * what pcrec currently does, and it will pass without an edit when the
 * producer refuses `a(?i)*`.
 * ========================================================================
 *
 * ---------------------------------------------------------------- generation
 *
 *   A doorway_byte    every byte 0x01..0xFF straight after `(?`, terminated
 *                     and unterminated.
 *   B run_byte        every byte 0x01..0xFF in each of six positions relative
 *                     to a letter and to the `-` marker.
 *                     BOUNDARY for A and B: 0x00 is unreachable — a pattern is
 *                     one argv element and argv strings are NUL-terminated.
 *                     There is no CLI surface that can express it.
 *   C letter_pairs    every ordered pair over the letters libpcre2 itself
 *                     accepted in family A (measured, never recalled), in four
 *                     forms.
 *   D marker_place    every insertion of `-`, `^`, `--`, `^^`, `-^`, `^-` at
 *                     every position of every run over {i,m,s,x} of length
 *                     0..2, bare and with a `:a` body.
 *                     BOUNDARY: length 0..2 (21 runs, 57 insertion points).
 *                     Length 3 was run while this file was written (313 points,
 *                     3,756 cells) and produced no verdict class the shorter
 *                     sweep did not already produce.
 *   E junk_insert     every letter that is NOT in the measured-valid set,
 *                     inserted at every position of a valid three-letter run.
 *   F truncation      every prefix of nine canonical spellings.
 *   G runlen          runs of 1..32 repeats, and the doubled-x levels.
 *   H degenerate      every prefix marker crossed with every terminator,
 *                     including the empty terminator and two junk ones.
 *   I whitespace      each of six whitespace bytes at eight positions, with
 *                     and without a preceding `(?x)` — x mode's tolerance
 *                     stops at the option-run syntax itself, and this family
 *                     is what would notice if pcrec applied it one level too
 *                     far.
 *   J quantified      the FINDING family. Every spelling both engines accepted
 *                     in families A..I, followed by each of eight quantifiers.
 *                     BOUNDARY: the accepted set is strided down to 64 BARE and
 *                     64 SCOPING spellings — separately, so the control's size
 *                     is a property of this check rather than of whatever the
 *                     accepted set happens to contain — giving 1,024 cells. The
 *                     unstrided set (880 spellings, 7,040 cells) was run while
 *                     this file was written and the split was identical: every
 *                     bare-run cell disagreed, every scoping-run cell agreed.
 *
 * ------------------------------------------------------------- the predictor
 *
 * As in check13, a generated sweep cannot carry a per-cell prediction, so each
 * cell's oracle verdict is measured at run time and the check asserts the
 * RELATION T1..T3. The oracle half is anchored by one literal prediction,
 * measured while this file was written: exactly eleven single LETTERS L make
 * `(?L)` compile, and they are C J R U a i m n r s x. Twenty-one single BYTES
 * do, the extra ten being the non-letter doorways `(?!)`, `(?#)`, `(?*)`,
 * `(?-)`, `(?0)`, `(?:)`, `(?=)`, `(?>)`, `(?^)`, `(?|)` — real constructs
 * mostly owned by other modules, and anchored separately because the `(?`
 * doorway is shared and its shape is part of what this check measures.
 * A different set on either anchor means the oracle moved and every family
 * below is measuring something else.
 *
 * --------------------------------------------------------- deferred cells
 *
 * A cell where pcrec answers "requires module 'X'" is COUNTED, not compared:
 * pcrec has not reached that construct, which is not a defect. Two shapes of
 * this appear here and both are reported as populations rather than as
 * failures, because D26 puts the wording of a refusal for something pcrec does
 * not implement outside the exact tier:
 *
 *   - a letter whose EFFECT belongs to another module (`m` needs multiline,
 *     so it defers to `assertions`; `J` defers to `named-groups`);
 *   - a doorway byte that belongs to another construct family entirely
 *     (`(?&`, `(?<`, `(?(`, `(?#`, `(?>`, `(?|`, `(?[`, `(?=`, `(?!`, `(?'`).
 *
 * One consequence is worth naming because it is invisible from the exit code:
 * an INVALID option run containing a deferred letter is reported as
 * "requires module" rather than as invalid — `(?m--)` defers, `(?i--)` is
 * diagnosed. The option-run grammar check therefore runs AFTER the per-letter
 * module gate, not before it. Nothing here fails on that; the count is pinned
 * so the shape is visible, and it can only shrink as modules land.
 *
 * -------------------------------------------------------------- sabotage
 *
 * Validated 2026-08-12 against two stand-ins, each an executable script put in
 * PCREC's place:
 *
 *   accept-everything (exit 0, a stub translation unit on stdout) — 3,473
 *   disagreements across nine families (doorway_byte 488, run_byte 1,468,
 *   letter_pairs 160, marker_place 528, junk_insert 164, truncation 45,
 *   degenerate 36, whitespace 96, quantified 488): T1 on every cell libpcre2
 *   rejects.
 *
 *   refuse-everything ("pcrec: syntax error", exit 1, no module named) — 698
 *   disagreements across seven families (doorway_byte 22, run_byte 62,
 *   letter_pairs 324, marker_place 156, truncation 9, runlen 112,
 *   degenerate 13), AND four population floors fail: with nothing accepted
 *   there are no spellings to quantify, so optrun.quantified and its scoped
 *   control both collapse to 0. That second half is the point of the floors —
 *   the comparison going quiet is caught by the count, not by the comparison.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check14 check14_option_runs.c -ldl
 * Run:   check14 floors.txt registry.tsv [pcrec-path]
 */
#include "spec_common.h"
#include "spec_pcrec.h"

static const char *pcrec_path;

/* ------------------------------------------------------- disagreement budget
 * (Same reasoning as check13's: a generated sweep fails in thousands of cells
 * at once, and printing all of them buries the line a reader needs.) */
typedef struct { const char *family; long shown, total; } Budget;
#define BUDGET_SHOW 6

static void budget_fail(Budget *b, const char *fmt, ...)
{
    b->total++;
    if (b->shown < BUDGET_SHOW) {
        b->shown++;
        va_list ap; va_start(ap, fmt);
        printf("  DISAGREE "); vprintf(fmt, ap); printf("\n");
        va_end(ap);
        spec_fails++;
    }
}

static void budget_close(Budget *b)
{
    if (b->total > b->shown) {
        printf("  DISAGREE [%s] ... and %ld more of the same family "
               "(%ld total; the first %ld are shown in full)\n",
               b->family, b->total - b->shown, b->total, b->shown);
        spec_fails++;
    }
}

/* ------------------------------------------------------------- populations */
static long pop_compared, pop_deferred, pop_scope, pop_accepted_both;
static long defer_letter, defer_doorway;

/* Spellings both engines accept, collected for family J. A spelling that does
 * not fit is COUNTED rather than dropped in silence: a collection that quietly
 * loses cells is the vacuous-population shape this suite exists to refuse. */
#define ACC_MAX 1024
#define ACC_LEN 48
static char accepted[ACC_MAX][ACC_LEN];
static int  n_accepted, n_accept_dropped;

/* One cell. Returns pcrec's verdict class. `collect` asks for the spelling to
 * be remembered for the quantifier family when both engines accept it. */
static SpecVClass cell(Budget *b, const char *pat, int collect)
{
    SpecVerdict o = spec_compile(pat);
    SpecPcrecRun r = spec_pcrec_compile(pcrec_path, "all", pat, NULL);
    SpecVClass vc = spec_pcrec_classify(&r);

    if (vc == SPEC_VC_ERROR) {
        budget_fail(b, "[%s] pcrec neither accepted nor refused '%s' "
                       "(ran=%d timed_out=%d exit=%d stderr: %.120s)",
                    b->family, pat, r.ran, r.timed_out, r.exit_code, r.err);
        return vc;
    }
    if (vc != SPEC_VC_ACCEPTED && r.out_bytes != 0)
        budget_fail(b, "[%s] pcrec refused '%s' but wrote %ld bytes to stdout — "
                       "a refusal must emit no C", b->family, pat, r.out_bytes);

    if (vc == SPEC_VC_MODULE) {
        pop_deferred++;
        const char *m = spec_pcrec_module(&r);
        if (!strcmp(m, "assertions") || !strcmp(m, "named-groups")) defer_letter++;
        else defer_doorway++;
        return vc;
    }
    if (vc == SPEC_VC_SCOPE) { pop_scope++; return vc; }

    pop_compared++;
    if (vc == SPEC_VC_ACCEPTED) {
        if (!o.ok)
            budget_fail(b, "[%s] MISCOMPILE RISK: pcrec ACCEPTED '%s' and wrote "
                           "%ld bytes of C; libpcre2 rejects it with error %d",
                        b->family, pat, r.out_bytes, o.err);
        else {
            pop_accepted_both++;
            if (!collect) { /* family A's unterminated half is not a spelling */ }
            else if (n_accepted < ACC_MAX && strlen(pat) < ACC_LEN)
                snprintf(accepted[n_accepted++], ACC_LEN, "%s", pat);
            else n_accept_dropped++;
        }
    } else if (o.ok) {
        budget_fail(b, "[%s] '%s' compiles under libpcre2, but pcrec refused it "
                       "as INVALID rather than as unimplemented or out of scope "
                       "(stderr: %.140s)", b->family, pat, r.err);
    }
    return vc;
}

/* ------------------------------------------------------------------- main */

int main(int argc, char **argv)
{
    const char *rp = NULL;
    spec_start("check14_option_runs", argc, argv, &rp);
    pcrec_path = (argc >= 4 && argv[3][0]) ? argv[3] : getenv("PCREC");
    if (!pcrec_path || !*pcrec_path) pcrec_path = "build/pcrec";

    /* ---- family A: the byte straight after "(?" --------------------------- */
    Budget bA = { "doorway_byte", 0, 0 };
    long fA = 0;
    char valid[64]; int nvalid = 0;        /* the LETTERS among them */
    char doorway[128]; int ndoorway = 0;   /* every byte among them */
    for (int by = 1; by < 256; by++) {
        char p1[8], p2[8];
        snprintf(p1, sizeof p1, "(?%c", (char)by);
        snprintf(p2, sizeof p2, "(?%c)", (char)by);
        cell(&bA, p1, 0); cell(&bA, p2, 1); fA += 2;
        if (!spec_compile(p2).ok) continue;
        if (ndoorway < (int)sizeof doorway - 1) doorway[ndoorway++] = (char)by;
        if (((by >= 'A' && by <= 'Z') || (by >= 'a' && by <= 'z')) &&
            nvalid < (int)sizeof valid - 1)
            valid[nvalid++] = (char)by;
    }
    valid[nvalid] = 0; doorway[ndoorway] = 0;
    budget_close(&bA);
    printf("  bytes B for which libpcre2 compiles \"(?B)\": \"%s\" (%d), of "
           "which letters: \"%s\" (%d)\n", doorway, ndoorway, valid, nvalid);
    /* Two anchors, both measured while this file was written. The letter set
     * is what the option-run families are built from; the full byte set is
     * wider because `(?` is a doorway shared with most of PCRE2's group
     * syntax — `(?!)`, `(?:)`, `(?#)`, `(?0)`, `(?|)` and the rest are real
     * constructs owned by other modules, and a change in THAT set would move
     * the boundary this check is measuring even though no letter moved. */
    if (strcmp(valid, "CJRUaimnrsx") != 0)
        spec_fail("ANCHOR: the LETTERS accepted as \"(?L)\" are \"%s\"; the "
                  "prediction recorded in this file's header is \"CJRUaimnrsx\". "
                  "Either the oracle moved or every family below is measuring a "
                  "different space", valid);
    if (strcmp(doorway, "!#*-0:=>CJRU^aimnrsx|") != 0)
        spec_fail("ANCHOR: the BYTES accepted as \"(?B)\" are \"%s\"; the "
                  "prediction recorded in this file's header is "
                  "\"!#*-0:=>CJRU^aimnrsx|\" — the shared `(?` doorway changed "
                  "shape", doorway);
    spec_pop("optrun.doorway_byte", fA);

    /* ---- family B: every byte at six positions inside a run --------------- */
    Budget bB = { "run_byte", 0, 0 };
    long fB = 0;
    static const char *const run_shapes[] = {
        "(?i%c)", "(?%ci)", "(?i%cm)", "(?i-%c)", "(?i%c:a)", "(?i%c"
    };
    for (int by = 1; by < 256; by++)
        for (size_t s = 0; s < sizeof run_shapes / sizeof run_shapes[0]; s++) {
            char pat[16];
            snprintf(pat, sizeof pat, run_shapes[s], (char)by);
            cell(&bB, pat, 1); fB++;
        }
    budget_close(&bB);
    spec_pop("optrun.run_byte", fB);

    /* ---- family C: ordered pairs over the MEASURED letter set ------------- */
    Budget bC = { "letter_pairs", 0, 0 };
    long fC = 0;
    static const char *const pair_forms[] = { "(?%c%c)", "(?%c-%c)", "(?-%c%c)", "(?%c%c:a)" };
    for (int i = 0; i < nvalid; i++)
        for (int j = 0; j < nvalid; j++)
            for (size_t f = 0; f < sizeof pair_forms / sizeof pair_forms[0]; f++) {
                char pat[16];
                snprintf(pat, sizeof pat, pair_forms[f], valid[i], valid[j]);
                cell(&bC, pat, 1); fC++;
            }
    budget_close(&bC);
    spec_pop("optrun.letter_pairs", fC);

    /* ---- family D: marker placement and count ----------------------------- */
    Budget bD = { "marker_place", 0, 0 };
    long fD = 0;
    static const char *const markers[] = { "-", "^", "--", "^^", "-^", "^-" };
    static const char letters4[] = "imsx";
    char runs[32][4]; int nruns = 0;
    runs[nruns++][0] = 0;                                     /* the empty run */
    for (int a = 0; a < 4; a++) { runs[nruns][0] = letters4[a]; runs[nruns][1] = 0; nruns++; }
    for (int a = 0; a < 4; a++)
        for (int b2 = 0; b2 < 4; b2++) {
            runs[nruns][0] = letters4[a]; runs[nruns][1] = letters4[b2];
            runs[nruns][2] = 0; nruns++;
        }
    for (int r = 0; r < nruns; r++) {
        size_t L = strlen(runs[r]);
        for (size_t pos = 0; pos <= L; pos++)
            for (size_t m = 0; m < sizeof markers / sizeof markers[0]; m++) {
                char body[16], bare[32], bodied[32];
                size_t n = 0;
                memcpy(body + n, runs[r], pos);            n += pos;
                strcpy(body + n, markers[m]);              n += strlen(markers[m]);
                strcpy(body + n, runs[r] + pos);
                snprintf(bare,   sizeof bare,   "(?%.8s)", body);
                snprintf(bodied, sizeof bodied, "(?%.8s:a)", body);
                cell(&bD, bare, 1); cell(&bD, bodied, 1); fD += 2;
            }
    }
    budget_close(&bD);
    spec_pop("optrun.marker_place", fD);

    /* ---- family E: a junk letter inserted into a valid run ---------------- */
    Budget bE = { "junk_insert", 0, 0 };
    long fE = 0;
    for (int c = 0; c < 128; c++) {
        if (!((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z'))) continue;
        if (strchr(valid, c)) continue;
        for (int pos = 0; pos <= 3; pos++) {
            char pat[16];
            snprintf(pat, sizeof pat, "(?%.*s%c%s)", pos, "ims", (char)c, "ims" + pos);
            cell(&bE, pat, 1); fE++;
        }
    }
    budget_close(&bE);
    spec_pop("optrun.junk_insert", fE);

    /* ---- family F: every prefix of a canonical spelling ------------------- */
    Budget bF = { "truncation", 0, 0 };
    long fF = 0;
    static const char *const fulls[] = {
        "(?im-sx:a)", "(?^ims:a)", "(?xx-i)", "(?-i:a)", "(?i)",
        "(?^)", "(?-)", "(?)", "(?J:a)"
    };
    for (size_t f = 0; f < sizeof fulls / sizeof fulls[0]; f++)
        for (size_t k = 1; k <= strlen(fulls[f]); k++) {
            char pat[24];
            snprintf(pat, k + 1, "%s", fulls[f]);
            cell(&bF, pat, 1); fF++;
        }
    budget_close(&bF);
    spec_pop("optrun.truncation", fF);

    /* ---- family G: run length and the doubled-x levels -------------------- */
    Budget bG = { "runlen", 0, 0 };
    long fG = 0;
    for (int k = 1; k <= 32; k++) {
        char rep[40], pat[48];
        for (int j = 0; j < k; j++) rep[j] = 'i';
        rep[k] = 0; snprintf(pat, sizeof pat, "(?%s)", rep); cell(&bG, pat, 1); fG++;
        for (int j = 0; j < k; j++) rep[j] = 'x';
        rep[k] = 0;
        snprintf(pat, sizeof pat, "(?%s)",  rep); cell(&bG, pat, 1); fG++;
        snprintf(pat, sizeof pat, "(?-%s)", rep); cell(&bG, pat, 1); fG++;
        if (k <= 8) {
            snprintf(pat, sizeof pat, "(?^%s)", rep); cell(&bG, pat, 1); fG++;
            for (int j = 0; j < k; j++) { rep[2*j] = 'i'; rep[2*j+1] = 'x'; }
            rep[2*k] = 0;
            snprintf(pat, sizeof pat, "(?%s)", rep); cell(&bG, pat, 1); fG++;
        }
    }
    budget_close(&bG);
    spec_pop("optrun.runlen", fG);

    /* ---- family H: prefix marker x terminator ----------------------------- */
    Budget bH = { "degenerate", 0, 0 };
    long fH = 0;
    static const char *const pre[]  = { "", "^", "-", "^-", "--", "-^", "^^" };
    static const char *const term[] = { ")", ":a)", ":)", "", "|a)", " )", "::a)" };
    for (size_t p = 0; p < sizeof pre / sizeof pre[0]; p++)
        for (size_t t = 0; t < sizeof term / sizeof term[0]; t++) {
            char pat[16];
            snprintf(pat, sizeof pat, "(?%s%s", pre[p], term[t]);
            cell(&bH, pat, 1); fH++;
        }
    budget_close(&bH);
    spec_pop("optrun.degenerate", fH);

    /* ---- family I: whitespace, with and without x mode -------------------- */
    Budget bI = { "whitespace", 0, 0 };
    long fI = 0;
    static const char ws[] = { ' ', '\t', '\n', '\r', '\f', '\v' };
    static const char *const wtpl[] = {
        "(?%ci)", "(?i%c)", "(?i%c:a)", "(?%c)", "(?-%ci)", "(?i-%c)",
        "(?i%cm)", "(?%c%c)"
    };
    for (size_t w = 0; w < sizeof ws; w++)
        for (size_t t = 0; t < sizeof wtpl / sizeof wtpl[0]; t++) {
            char inner[16], pat[24];
            snprintf(inner, sizeof inner, wtpl[t], ws[w], ws[w]);
            cell(&bI, inner, 1); fI++;
            snprintf(pat, sizeof pat, "(?x)%s", inner);
            cell(&bI, pat, 1); fI++;
        }
    budget_close(&bI);
    spec_pop("optrun.whitespace", fI);

    /* ---- family J: a quantifier after an accepted spelling ----------------
     * See the FINDING block at the top of this file. The bare-run cells are
     * expected to FAIL against pcrec as it stands; the scoping-run cells are
     * the control that proves the family is discriminating rather than
     * disagreeing with everything, and they are floored separately. */
    Budget bJ = { "quantified", 0, 0 };
    long fJ = 0, quant_bare = 0, quant_scoped = 0, quant_bare_bad = 0, quant_scoped_bad = 0;
    static const char *const quants[] = { "*", "+", "?", "{2}", "{2,3}", "{0,1}", "*?", "+?" };

    /* The two shapes are strided SEPARATELY, to a fixed 64 each. Striding the
     * collected list as a whole would let the bare/scoping split — and with it
     * the size of the control population — drift with whatever the accepted set
     * happens to contain, which would make the control's floor a number about
     * the sample rather than about the check. */
    int idx[2][64], nidx[2] = {0, 0};
    for (int shape = 0; shape < 2; shape++) {
        int total = 0;
        for (int i = 0; i < n_accepted; i++)
            if ((strchr(accepted[i], ':') != NULL) == shape) total++;
        int stride = total > 64 ? total / 64 : 1, seen = 0;
        for (int i = 0; i < n_accepted && nidx[shape] < 64; i++) {
            if ((strchr(accepted[i], ':') != NULL) != shape) continue;
            if (seen++ % stride == 0) idx[shape][nidx[shape]++] = i;
        }
    }
    for (int shape = 0; shape < 2; shape++)
      for (int s = 0; s < nidx[shape]; s++)
        for (size_t q = 0; q < sizeof quants / sizeof quants[0]; q++) {
            int i = idx[shape][s];
            char pat[128];
            snprintf(pat, sizeof pat, "a%.*s%s", ACC_LEN, accepted[i], quants[q]);
            int scoped = shape;
            if (scoped) quant_scoped++; else quant_bare++;
            fJ++;

            SpecVerdict o = spec_compile(pat);
            SpecPcrecRun r = spec_pcrec_compile(pcrec_path, "all", pat, NULL);
            SpecVClass vc = spec_pcrec_classify(&r);
            if (vc == SPEC_VC_MODULE || vc == SPEC_VC_SCOPE) continue;
            if (vc == SPEC_VC_ERROR) {
                budget_fail(&bJ, "[quantified] pcrec neither accepted nor refused '%s'", pat);
                continue;
            }
            pop_compared++;
            if (vc == SPEC_VC_ACCEPTED && !o.ok) {
                if (scoped) quant_scoped_bad++; else quant_bare_bad++;
                budget_fail(&bJ, "[quantified] MISCOMPILE: pcrec ACCEPTED '%s' and "
                                 "wrote %ld bytes of C; libpcre2 rejects it with "
                                 "error %d — see this file's FINDING block",
                            pat, r.out_bytes, o.err);
            } else if (vc == SPEC_VC_INVALID && o.ok) {
                budget_fail(&bJ, "[quantified] '%s' compiles under libpcre2 but pcrec "
                                 "refused it as INVALID (stderr: %.120s)", pat, r.err);
            }
        }
    budget_close(&bJ);
    printf("  quantified: %ld bare-run cells (%ld accepted by pcrec and rejected "
           "by libpcre2), %ld scoping-run cells (%ld likewise)\n",
           quant_bare, quant_bare_bad, quant_scoped, quant_scoped_bad);
    if (quant_bare_bad > 0) {
        printf("\n"
               "  ---------------------------------------------------------------\n"
               "  FINDING: a quantifier after a BARE option run is accepted by\n"
               "  pcrec and is error 109 in libpcre2. Repro:\n"
               "      build/pcrec --features modifiers --emit-main -o q.c 'a(?i)*'\n"
               "  exits 0 and emits a matcher that accepts \"a\", \"aa\", \"aaa\" —\n"
               "  the `*` was bound to the preceding atom, so the option run was\n"
               "  modelled as contributing no atom. PCRE2 does not allow a\n"
               "  quantifier there at all. The SCOPING form `a(?i:b)*` is correct\n"
               "  in both and is this family's control (%ld cells, %ld wrong).\n"
               "  pcrec's own registry agrees with PCRE2: every `modifiers` row's\n"
               "  `quantifiable` cell reads `form`.\n"
               "  This check is pinned to what PCRE2 requires and will pass with\n"
               "  no edit once the producer refuses the bare-run form.\n"
               "  ---------------------------------------------------------------\n",
               quant_scoped, quant_scoped_bad);
    }
    spec_pop("optrun.quantified", fJ);
    spec_pop("optrun.quantified_scoped_control", quant_scoped);

    /* ---- what the sweep saw ------------------------------------------------ */
    printf("  pcrec: %ld cell(s) compared, %ld deferred to a module "
           "(%ld by letter, %ld by doorway), %ld out of scope\n",
           pop_compared, pop_deferred, defer_letter, defer_doorway, pop_scope);
    printf("  spellings accepted by BOTH engines: %d collected, %d too long to "
           "collect (family J quantifies %d bare + %d scoping)\n",
           n_accepted, n_accept_dropped, nidx[0], nidx[1]);
    if (n_accept_dropped > 0)
        spec_fail("%d accepted spelling(s) did not fit the family-J collection "
                  "buffer and were not quantified — raise ACC_LEN/ACC_MAX rather "
                  "than letting the population shrink in silence", n_accept_dropped);
    spec_pop("optrun.pcrec_compared", pop_compared);
    spec_pop("optrun.pcrec_deferred", pop_deferred);
    spec_pop("optrun.accepted_both", pop_accepted_both);

    static const char *const owned[] = {
        "optrun.doorway_byte", "optrun.run_byte", "optrun.letter_pairs",
        "optrun.marker_place", "optrun.junk_insert", "optrun.truncation",
        "optrun.runlen", "optrun.degenerate", "optrun.whitespace",
        "optrun.quantified", "optrun.quantified_scoped_control",
        "optrun.pcrec_compared", "optrun.pcrec_deferred", "optrun.accepted_both"
    };
    spec_floors_require(owned, (int)(sizeof owned / sizeof owned[0]));
    return spec_finish();
}
