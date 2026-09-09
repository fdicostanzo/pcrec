/* tests/backrefs/fold_agreement_utf8_check.c — [M5.0] STAGE 4's HALF OF THE
 * FOLD AGREEMENT CHECK: the same obligation `fold_agreement_check.c` carries
 * for the `byte` encoding, for the `utf8` one.
 *
 * WHY IT IS A SECOND FILE AND NOT A WIDER SWEEP IN THE FIRST. The byte check
 * walks 65,536 ORDERED BYTE PAIRS, which is the whole of its domain. Under
 * `utf8` the domain is 1.1M CODE POINTS and the residual compares CHARACTERS,
 * so neither the loop nor the buffer layout transfers. `utf8_design.md` §4.6
 * says so and adds the reason a naive port would be wrong for a second
 * reason: a 1.1M-cell sweep on every `make test` is a per-suite price this
 * project does not pay.
 *
 * §4.6 PROPOSED A SAMPLE AND THIS FILE SWEEPS THE RELATION INSTEAD, which is
 * both cheaper and stronger. The interesting set §4.6 lists (K/U+212A,
 * S/U+017F, omega/U+2126, micro/U+00B5, angstrom/U+212B, sigma/final sigma,
 * and the two NON-folds U+0130 and U+0131) is 8 pairs chosen by hand. The
 * relation itself is 2,938 members across 1,454 classes, so walking every
 * member of every class costs 2,938 residual calls — a few milliseconds — and
 * is EXHAUSTIVE in the direction that matters. The hand-picked cells are a
 * subset of it by construction, so nothing is lost by not listing them.
 *
 * TWO DIRECTIONS, because a relation has two ways to be wrong:
 *
 *   (A) EVERY member of every fold class must compare EQUAL in the residual.
 *       A residual that folded too little fails here — which is the whole of
 *       what a hand-picked sample can see.
 *   (B) The residual must fold NOTHING ELSE. Swept over 0..0xFFFF against the
 *       next code point, which is where a residual that folded too much (a
 *       decoder losing its bounds, a binary search returning a neighbour)
 *       shows up. A sample cannot ask this at all: it only ever names pairs
 *       that DO fold.
 *
 * AND PART C IS THE ONE §4.6 DOES NOT HAVE, because stage 4 created the
 * hazard it guards. There are now TWO fold relations in this compiler —
 * `pcrec_fold_ascii` (hand-written, MEASURED against libpcre2's 8-bit non-UTF
 * build) and `pcrec_fold_ucd_simple` (GENERATED from a vendored file) — and
 * the `byte` encoding's answers must not move when that file's VERSION does.
 * Part C ties them: restricted to ASCII, the Unicode relation must be exactly
 * the 26 pairs `pcrec_ascii_fold` carries, and no byte >= 0x80 may have an
 * ASCII fold partner. A UCD bump that changed either is then a LOUD failure
 * naming the byte, which is D26's re-measurement event rather than a silent
 * re-baselining of every caseless answer under `--encoding=byte`.
 *
 * THE TWO SIDES ARE INDEPENDENT in the same sense the byte check's are: the
 * residual is read out of an artifact PCREC ACTUALLY EMITTED (this file is
 * compiled against a generated `gen.c` and calls the shipped
 * `rx_bref_match_caseless` directly), and the compiler side is the
 * `PcrecFold` object the PARSER uses. Neither can be edited into agreement
 * with the other without moving the thing it stands for. */

#include <stdio.h>

#include "core/internal.h"
#include "gen.h"

/* Encode one code point as UTF-8; returns the length, 0 for a surrogate or an
 * out-of-range value. Deliberately written out here rather than borrowed from
 * anywhere in `src/`: this side of the check must not share a spelling with
 * the side it checks. */
static int u8enc(unsigned cp, unsigned char *out)
{
    if (cp >= 0xD800u && cp <= 0xDFFFu) return 0;
    if (cp > 0x10FFFFu) return 0;
    if (cp < 0x80u) { out[0] = (unsigned char)cp; return 1; }
    if (cp < 0x800u) {
        out[0] = (unsigned char)(0xC0u | (cp >> 6));
        out[1] = (unsigned char)(0x80u | (cp & 0x3Fu));
        return 2;
    }
    if (cp < 0x10000u) {
        out[0] = (unsigned char)(0xE0u | (cp >> 12));
        out[1] = (unsigned char)(0x80u | ((cp >> 6) & 0x3Fu));
        out[2] = (unsigned char)(0x80u | (cp & 0x3Fu));
        return 3;
    }
    out[0] = (unsigned char)(0xF0u | (cp >> 18));
    out[1] = (unsigned char)(0x80u | ((cp >> 12) & 0x3Fu));
    out[2] = (unsigned char)(0x80u | ((cp >> 6) & 0x3Fu));
    out[3] = (unsigned char)(0x80u | (cp & 0x3Fu));
    return 4;
}

/* Does the SHIPPED residual call `a` and `b` caselessly equal? The capture is
 * character `a` and the cursor sits at character `b`, so the entry returns
 * b's own byte length when they fold together and a negative value otherwise
 * — the LENGTH-return protocol, exercised here as well as asserted. */
static int resid_eq(unsigned a, unsigned b)
{
    unsigned char buf[8];
    int la = u8enc(a, buf);
    int lb = u8enc(b, buf + la);
    ptrdiff_t r;
    if (la == 0 || lb == 0) return -1;
    r = rx_bref_match_caseless(buf, (size_t)(la + lb), 0, (size_t)la,
                               (size_t)la);
    return r == (ptrdiff_t)lb;
}

/* THE RELATION'S OWN DOMAIN, in one call: `partners` over the WHOLE code-point
 * space answers with every code point that is some other code point's fold
 * partner — which is exactly the set of code points in a class of size > 1.
 * Asking it once is what keeps this check affordable: the alternative, one
 * `partners` call per code point, is 1.1M walks of a 2,938-entry relation. */
static void fold_domain(Arena *ar, PcrecCpSet *dom)
{
    PcrecCpSet all;
    pcrec_cpset_init(&all, ar);
    pcrec_cpset_add(&all, 0, 0x10FFFFu);
    pcrec_cpset_init(dom, ar);
    pcrec_fold_ucd_simple.partners(&all, dom);
}

/* `cp`'s fold class according to the COMPILER's own object, written into
 * `out` (including `cp`); returns the member count, or -1 if the class does
 * not fit — which is a failure and not a truncation, since the bound below is
 * this file's OWN and must not silently become the answer. */
#define MAX_ORBIT 16

static int compiler_orbit(Arena *ar, unsigned cp, unsigned *out)
{
    PcrecCpSet in, add;
    int n = 0;
    pcrec_cpset_init(&in, ar);
    pcrec_cpset_add(&in, cp, cp);
    pcrec_cpset_init(&add, ar);
    pcrec_fold_ucd_simple.partners(&in, &add);
    out[n++] = cp;
    for (int i = 0; i < add.n; i++)
        for (unsigned c = add.iv[i].lo; c <= add.iv[i].hi; c++) {
            if (c == cp) continue;
            if (n >= MAX_ORBIT) return -1;
            out[n++] = c;
        }
    return n;
}

int main(void)
{
    Arena ar = {0};
    PcrecCpSet dom;
    int bad = 0;
    long members = 0, classes = 0, negatives = 0, ascii_tied = 0, domain = 0;

    fold_domain(&ar, &dom);

    /* ---- (A) every member of every fold class compares equal ------------ */
    for (int iv = 0; iv < dom.n; iv++) {
        for (unsigned cp = dom.iv[iv].lo; cp <= dom.iv[iv].hi; cp++) {
            unsigned orb[MAX_ORBIT];
            int n = compiler_orbit(&ar, cp, orb);
            domain++;
            if (n < 0) {
                printf("DEFECT U+%04X's fold class exceeds this check's own "
                       "bound of %d members\n", cp, MAX_ORBIT);
                bad++;
                continue;
            }
            if (n < 2) {
                printf("DEFECT U+%04X is in the relation's domain and has no "
                       "partners — the domain derivation and the per-code-"
                       "point one disagree\n", cp);
                bad++;
                continue;
            }
            classes++;
            for (int i = 0; i < n; i++) {
                int e = resid_eq(cp, orb[i]);
                members++;
                if (e < 0) continue;      /* unencodable: surrogates only */
                if (!e && ++bad <= 10)
                    printf("DISAGREE U+%04X vs U+%04X: the compiler's fold "
                           "class holds both, the SHIPPED residual says "
                           "different\n", cp, orb[i]);
            }
        }
    }

    /* ---- (B) the residual folds nothing the compiler does not ----------- */
    for (unsigned cp = 0; cp < 0xFFFFu; cp++) {
        int in_class = 0, e;
        if (cp >= 0xD800u && cp <= 0xDFFFu) continue;
        if (cp + 1 >= 0xD800u && cp + 1 <= 0xDFFFu) continue;
        /* Two adjacent code points can share a class only if BOTH are in the
         * relation's domain, so the cheap test comes first and the orbit walk
         * runs for a handful of pairs rather than for 65,535. */
        if (pcrec_cpset_has(&dom, cp) && pcrec_cpset_has(&dom, cp + 1)) {
            unsigned orb[MAX_ORBIT];
            int n = compiler_orbit(&ar, cp, orb);
            for (int i = 0; i < n && n > 0; i++)
                if (orb[i] == cp + 1) in_class = 1;
        }
        e = resid_eq(cp, cp + 1);
        if (e < 0) continue;
        negatives++;
        if (e != in_class && ++bad <= 10)
            printf("DISAGREE U+%04X vs U+%04X: residual says %s, the "
                   "compiler's fold says %s\n", cp, cp + 1,
                   e ? "equal" : "different",
                   in_class ? "equal" : "different");
    }

    /* ---- (C) the ASCII restriction is `pcrec_ascii_fold`, exactly ------- */
    for (unsigned c = 0; c < 256u; c++) {
        unsigned orb[MAX_ORBIT];
        unsigned want = pcrec_ascii_fold[c];
        int n = compiler_orbit(&ar, c, orb);
        int seen = 0;
        if (n < 0) { bad++; continue; }
        for (int i = 0; i < n; i++) {
            if (orb[i] >= 0x80u || orb[i] == c) continue;
            seen++;
            if (c >= 0x80u) {
                printf("DEFECT byte 0x%02x has an ASCII fold partner U+%04X "
                       "under the vendored Unicode data. The `byte` encoding "
                       "folds no byte >= 0x80 (MEASURED against libpcre2's "
                       "8-bit non-UTF build), so the two relations no longer "
                       "agree on ASCII\n", c, orb[i]);
                bad++;
            } else if (orb[i] != want) {
                printf("DEFECT 0x%02x folds to 0x%02x under the vendored "
                       "Unicode data and to 0x%02x in pcrec_ascii_fold — a "
                       "UCD version bump has moved the `byte` encoding's "
                       "answers (a D26 re-measurement event)\n",
                       c, orb[i], want);
                bad++;
            }
        }
        if (c < 0x80u) {
            if (want != c && seen != 1) {
                printf("DEFECT 0x%02x has an ASCII partner 0x%02x in "
                       "pcrec_ascii_fold and %d in the vendored data\n",
                       c, want, seen);
                bad++;
            }
            if (want == c && seen != 0) {
                printf("DEFECT 0x%02x folds to nothing in pcrec_ascii_fold "
                       "and to %d ASCII partner(s) in the vendored data\n",
                       c, seen);
                bad++;
            }
            if (want != c) ascii_tied++;
        }
    }
    arena_free(&ar);

    /* The MEASURED shape, asserted so a check agreeing over an EMPTY relation
     * cannot read as a pass — the byte check's own rule, one encoding over. */
    if (classes != 2938) {
        printf("DEFECT %ld code points in a fold class of size > 1, 2938 "
               "measured at Unicode 16.0.0 — the relation has changed size, "
               "which is a DATA event and not a number to re-pin here\n",
               classes);
        bad++;
    }
    if (domain != classes) {
        printf("DEFECT the relation's domain holds %ld code points and %ld of "
               "them have a class of size > 1 — the two derivations disagree\n",
               domain, classes);
        bad++;
    }
    if (ascii_tied != 52) {
        printf("DEFECT %ld ASCII bytes tied, 52 expected (the ASCII "
               "letters)\n", ascii_tied);
        bad++;
    }

    if (bad) {
        printf("fold-agreement-utf8: %d disagreement(s)\n", bad);
        return 1;
    }
    printf("fold-agreement-utf8: %ld folding code points / %ld ordered pairs "
           "compare EQUAL and %ld adjacent-pair controls compare as the "
           "compiler says, in the SHIPPED utf8 $_bref_match_caseless; the "
           "vendored relation restricted to ASCII is pcrec_ascii_fold's %ld "
           "bytes exactly\n", classes, members, negatives, ascii_tied);
    return 0;
}
