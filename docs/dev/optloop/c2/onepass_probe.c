/* [ONE-PASS REACH CENSUS] M-A of `captures_via_dfa_survey.md` §3.6 — the
 * THROWAWAY one-pass predicate, NOT a mechanism and never wired into the
 * build.
 *
 * ============================================================================
 * WHAT THE SURVEY ASKS AND WHY IT COMES FIRST
 * ============================================================================
 *
 * §3.3 ranks the ONE-PASS DFA as the only proposable candidate for assigning
 * captures from a deterministic machine under PCRE leftmost-first semantics,
 * and §3.6 gates it on a single number: *"if fewer than ~10% of
 * capture-bearing corpus patterns are one-pass, (c) is a special case for a
 * handful of patterns and fails `pcrec-general-mechanisms-not-special-cases`;
 * the row closes with the number."*  A one-pass predicate does not exist in
 * the tree, so the census needs a throwaway analyzer.  This is it.
 *
 * ============================================================================
 * THE PREDICATE, EXACTLY
 * ============================================================================
 *
 * A pattern is ONE-PASS when, during an ANCHORED match, at most one
 * alternative can proceed at each input byte ([RE2onepass]; [RAonepass];
 * [GoOnepass]).  Spelled over pcrec's lowered AST, with `FIRST(a)` the set of
 * bytes that can BEGIN a match of `a`, `NULL?(a)` whether `a` can match
 * empty, and `F` the set of bytes that can follow `a` in the whole pattern
 * (`Fe` = the match may END right after `a`):
 *
 *   A_ALT      every pair of branches has DISJOINT `FIRST`, at most one
 *              branch is nullable, and if a branch is nullable then every
 *              other branch's `FIRST` is disjoint from `F` as well -- without
 *              that last clause "take the empty branch" and "enter a branch"
 *              are decided by the same byte, which is the ambiguity the
 *              criterion is about.
 *   A_REP      where a CHOICE exists (`rmax != rmin`): the body is not
 *              nullable and `FIRST(body)` is disjoint from `F`, so "go round
 *              again" versus "leave" is decided by the next byte alone.
 *   A_LOOK     NOT one-pass.  All three production implementations bail on a
 *   A_BREF     lookaround, a backreference and a subroutine call, and pcrec
 *   A_CALL     has no reason to be braver than RE2 here.
 *
 * Zero-width assertions (`^ $ \b \B \A \z \G \K`) are ALLOWED: they are
 * deterministic empty-width tests that Go's `onepass` admits explicitly, and
 * they consume no byte, so they cannot create a two-alternative step.
 *
 * Clause (iii) of §3.6 -- "the pattern is anchored or is being compiled for
 * the anchored entry" -- is satisfied BY CONSTRUCTION for the population the
 * survey cares about: §3.3's fit argument is that a one-pass DFA replaces
 * `rx_match_anchored`, which the hybrid already calls anchored on a window.
 * The census therefore does not require a leading anchor, and reports the
 * leading-anchored subset separately so the stricter reading is also readable
 * off the same data.
 *
 * ============================================================================
 * KNOWN FALSE NEGATIVES (this predicate under-reports; every one is safe)
 * ============================================================================
 *
 *  (a) `FIRST` is computed over BYTES after `pcrec_lower_enc`, so under
 *      `-e utf8` two classes whose UTF-8 encodings share a LEAD byte are
 *      reported as overlapping even where a character-grain analysis would
 *      separate them.  That is [RAonepass]'s own documented narrowing and is
 *      the reason the survey asks for the `utf8` arm at all -- so here it is
 *      the measurement, not an artefact.
 *  (b) Disjointness is required PAIRWISE over an `A_ALT` spine rather than
 *      via a determinizing construction, so an alternation that is one-pass
 *      only after factoring reads as not-one-pass.
 *
 *      AND THAT CUTS THE OTHER WAY TOO, which is a finding rather than a
 *      caveat: `pcrec_altcls` runs ABOVE this walk, so `(xy|xz)` -- which
 *      `captures_via_dfa_survey.md` §3.3 names, from RE2's own front end, as
 *      a pattern that is NOT one-pass -- is factored to `x(?:y|z)` before the
 *      predicate sees it (`RX_ALTCLS_FACTORED 1` on its artifact) and IS
 *      one-pass on pcrec's tree.  pcrec's reach is therefore measured on
 *      pcrec's trees and is not comparable byte for byte with a figure
 *      derived from the three precedents' criterion applied to raw pattern
 *      text.  `-no-factor` denies both altcls axes so both numbers are
 *      readable from one instrument.
 *  (c) `A_ATOMIC` is treated as transparent.  An atomic group REMOVES
 *      alternatives, so a pattern reported one-pass is still one-pass; a
 *      pattern whose ambiguity the cut removes is missed.
 *
 * There are NO known false POSITIVES, which is the direction that matters:
 * the census must not over-report reach for a mechanism whose whole gate is
 * a reach number.
 *
 * Build (never by `make`):
 *   gcc -O2 -Ilib -Isrc -o onepass_probe onepass_probe.c build/libpcrec.a
 * Input : one record per line, `id<TAB>hex-encoded pattern bytes`.
 * Output: one TSV row per record.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

typedef struct { unsigned char b[32]; } Set;

static void sset(Set *s, int i)
{ s->b[i >> 3] |= (unsigned char)(1u << (i & 7)); }
static void sor(Set *d, const Set *s)
{ int i; for (i = 0; i < 32; i++) d->b[i] |= s->b[i]; }
static bool sdisjoint(const Set *a, const Set *c)
{ int i; for (i = 0; i < 32; i++) if (a->b[i] & c->b[i]) return false; return true; }
static Set szero(void) { Set s; memset(&s, 0, sizeof s); return s; }

/* ---- FIRST and NULLABLE, computed bottom-up ------------------------------
 *
 * Both spines are folded ITERATIVELY (`src/opt/reqbyte.c`'s rule: an `A_CAT`
 * or `A_ALT` spine is as long as the PATTERN).  `first_of` returns FIRST(a)
 * and writes NULL?(a) through `nul`. */
static Set first_of(const Ast *a, bool *nul);

static Set cat_first(const Ast *a, bool *nul)
{
    /* FIRST(l r) = FIRST(l) u (NULL?(l) ? FIRST(r) : {}).  The spine leans
     * LEFT, so fold from the right with an accumulator: `acc` is FIRST of
     * everything already seen to the right, `acc_nul` its nullability. */
    Set acc = szero(); bool acc_nul = true; int have = 0;
    for (;;) {
        if (a->k == A_CAT) {
            bool rn; Set rf = first_of(a->r, &rn);
            if (!have) { acc = rf; acc_nul = rn; have = 1; }
            else {
                Set o = rf; if (rn) sor(&o, &acc);
                acc = o; acc_nul = rn && acc_nul;
            }
            a = a->l; continue;
        }
        { bool ln; Set lf = first_of(a, &ln);
          Set o = lf; if (ln && have) sor(&o, &acc);
          *nul = ln && (!have || acc_nul);
          return o; }
    }
}

static Set first_of(const Ast *a, bool *nul)
{
    switch (a->k) {
    case A_CAT: return cat_first(a, nul);
    case A_CAP: case A_ATOMIC: return first_of(a->l, nul);
    case A_ALT: {
        Set o = szero(); bool n = false, bn;
        const Ast *t = a;
        while (t->k == A_ALT) {
            Set f = first_of(t->r, &bn); sor(&o, &f); n = n || bn; t = t->l;
        }
        { Set f = first_of(t, &bn); sor(&o, &f); n = n || bn; }
        *nul = n; return o;
    }
    case A_REP: {
        bool bn; Set f = first_of(a->l, &bn);
        *nul = (a->u.rep.rmin == 0) || bn;
        return f;
    }
    case A_CLASS: {
        Set o = szero(); int i;
        for (i = 0; i < 256; i++) if (pcrec_cls_has(a, (unsigned)i)) sset(&o, i);
        *nul = false; return o;
    }
    case A_BREF: case A_CALL: {
        /* Unknown: every byte, and possibly empty.  The predicate refuses
         * these kinds outright below, so the value only has to be SOUND. */
        Set o; memset(&o, 0xff, sizeof o); *nul = true; return o;
    }
    default:
        *nul = true; return szero();       /* zero-width */
    }
}

/* ---- the predicate, top-down with a FOLLOW set --------------------------- */

static bool refused_kind;

static bool check(const Ast *a, Set F, bool Fe)
{
    for (;;) {
        switch (a->k) {
        case A_CAT: {
            bool rn; Set rf = first_of(a->r, &rn);
            if (!check(a->r, F, Fe)) return false;
            { Set nf = rf; if (rn) sor(&nf, &F);
              F = nf; Fe = Fe && rn; }
            a = a->l; continue;
        }
        case A_CAP: case A_ATOMIC: a = a->l; continue;
        case A_ALT: {
            /* Collect the whole spine's branches, then test PAIRWISE. */
            const Ast *br[256]; int nbr = 0;
            const Ast *t = a;
            while (t->k == A_ALT && nbr < 255) { br[nbr++] = t->r; t = t->l; }
            br[nbr++] = t;
            Set bf[256]; bool bn[256]; int i, j, nnul = 0;
            for (i = 0; i < nbr; i++) { bf[i] = first_of(br[i], &bn[i]); if (bn[i]) nnul++; }
            if (nnul > 1) return false;
            for (i = 0; i < nbr; i++)
                for (j = i + 1; j < nbr; j++)
                    if (!sdisjoint(&bf[i], &bf[j])) return false;
            if (nnul == 1)
                for (i = 0; i < nbr; i++)
                    if (!bn[i] && !sdisjoint(&bf[i], &F)) return false;
            for (i = 0; i < nbr; i++) if (!check(br[i], F, Fe)) return false;
            return true;
        }
        case A_REP: {
            bool bn; Set bfs = first_of(a->l, &bn);
            int rmin = a->u.rep.rmin, rmax = a->u.rep.rmax;
            if (rmax != rmin) {                 /* a real choice at the loop */
                if (bn) return false;           /* nullable body: unbounded ambiguity */
                if (!sdisjoint(&bfs, &F)) return false;
            }
            { Set nf = bfs; sor(&nf, &F);
              return check(a->l, nf, Fe && rmin == 0); }
        }
        case A_CLASS:
        case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
            return true;
        case A_LOOK: case A_BREF: case A_CALL:
            refused_kind = true; return false;
        }
        return true;
    }
}

static long node_count(const Ast *a)
{
    long n = 1;
    for (;;) {
        if (a->k == A_CAT || a->k == A_ALT) { n += node_count(a->r); a = a->l; n++; continue; }
        if (a->k == A_CAP || a->k == A_ATOMIC || a->k == A_REP) { a = a->l; n++; continue; }
        return n;
    }
}

/* ------------------------------------------------------------------ driver */

static int deny_altcls;   /* -no-factor: measure the precedents' own criterion */

static Ast *parse_lower(const char *pat, Ctx *cx, pcrec_options *defo, int enc)
{
    memset(cx, 0, sizeof(*cx));
    cx->enabled_features = pcrec_enabled_mask();
    pcrec_default_options(defo);
    defo->encoding = enc;
    if (deny_altcls)
        defo->flags |= PCREC_NO_ALTCLS_MERGE | PCREC_NO_ALTCLS_FACTOR;
    cx->pat = pat; cx->patlen = strlen(pat); cx->opt = defo;
    cx->job = calloc(1, sizeof(Job));
    if (!cx->job) { fprintf(stderr, "out of memory\n"); exit(2); }
    cx->arena.cx = cx;
    Ast *root = NULL;
    if (setjmp(cx->jb) == 0) {
        pcrec_parse_mods_init(cx);
        root = pcrec_parse_info(cx, NULL);
        /* The same three-pass prefix `reqpos_probe.c` uses, and for the same
         * reason its own header records: an analysis's answer is a property
         * of the tree at its call site. */
        if (root) root = pcrec_altcls(cx, root);
        if (root) root = pcrec_discharge_atomic(cx, root);
        if (root) root = pcrec_lower_enc(cx, root);
    }
    return root;
}

static bool leading_anchor(const Ast *a)
{
    for (;;) {
        if (a->k == A_CAT || a->k == A_CAP || a->k == A_ATOMIC) { a = a->l; continue; }
        return a->k == A_BOL || a->k == A_GSTART;
    }
}

int main(int argc, char **argv)
{
    char err[256];
    int enc = PCREC_ENC_BYTE, i;
    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-e") && i + 1 < argc && !strcmp(argv[i+1], "utf8"))
            { enc = PCREC_ENC_UTF8; i++; }
        else if (!strcmp(argv[i], "-no-factor")) deny_altcls = 1;
    }
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0) {
        fprintf(stderr, "features: %s\n", err); return 2;
    }
    printf("id\tstatus\tncap\tnodes\tonepass\twhy\tanchored\tcapped\n");
    char *line = NULL; size_t cap = 0; ssize_t got;
    while ((got = getline(&line, &cap, stdin)) > 0) {
        if (got && line[got-1] == '\n') line[--got] = 0;
        if (!got) continue;
        char *tab = strchr(line, '\t'); if (!tab) continue;
        *tab = 0;
        const char *id = line, *hex = tab + 1;
        size_t hn = strlen(hex) / 2;
        char *pat = malloc(hn + 1);
        for (size_t i = 0; i < hn; i++) { unsigned v; sscanf(hex + 2*i, "%2x", &v); pat[i] = (char)v; }
        pat[hn] = 0;
        Ctx cx; pcrec_options defo;
        Ast *root = parse_lower(pat, &cx, &defo, enc);
        if (!root) {
            printf("%s\trefused\t0\t0\t-\t-\t0\t0\n", id);
        } else {
            refused_kind = false;
            Set F = szero();
            bool op = check(root, F, true);
            long nn = node_count(root);
            int nc = (int)cx.ncap;
            /* The three precedents' own caps, §3.6's second column: RE2 caps
             * at 5 capture pairs, Go abandons at 1,000 instructions. */
            int capped = (op && nc <= 5 && nn <= 1000);
            printf("%s\tok\t%d\t%ld\t%d\t%s\t%d\t%d\n", id, nc, nn, op ? 1 : 0,
                   op ? "-" : (refused_kind ? "kind" : "ambiguous"),
                   leading_anchor(root) ? 1 : 0, capped);
        }
        pcrec_arena_free(&cx.arena);
        free(cx.job);
        free(pat);
    }
    free(line);
    return 0;
}
