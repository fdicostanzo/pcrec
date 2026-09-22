/* [OPT-REQPOS] THE THROWAWAY POSITIONED NECESSARY-BYTE WALK — the D77
 * census instrument, NOT a mechanism and never wired into the build.
 *
 * ============================================================================
 * WHAT IT IS AND WHY IT IS A SEPARATE PROGRAM
 * ============================================================================
 *
 * `[OPT-REQBYTE]` (batch 1, `src/opt/reqbyte.c` on lane/optimpl1) derives ONE
 * fact: a byte every match must contain.  `[OPT-REQPOS]`'s row asks a
 * POSITIONED question on top of it -- where in the match can that byte sit --
 * and its D77 trigger is a census, before any build.  This file is that
 * census's analyzer.
 *
 * It links `libpcrec.a` and drives the REAL parser and the REAL encoding
 * lowering (`tests/registry/definitions_check.c`'s `parse_one` recipe, which
 * is `tests/mrl/maxw_check.c`'s), so the tree it walks is the tree the
 * emitters walk: after `pcrec_lower_enc` every `A_CLASS` is a BYTE class and
 * a singleton is exactly one `memchr` argument.  It does NOT re-implement
 * pcrec's parse, and it does NOT read `--emit-ir` (which refuses on every
 * DFA-winning pattern, `w2x_report.md` §5, so an IR-driven census would have
 * silently measured a biased half of the corpus).
 *
 * THE BIT THAT MAKES IT CHECKABLE: it carries `src/opt/reqbyte.c`'s OWN set
 * and pick rules verbatim (union at `A_CAT`, intersect at `A_ALT`, rightmost
 * pick, empty set at every decline) beside the new position/run tracking, so
 * its `req_byte` column MUST equal the landed `RX_REQ_BYTE` stamp on every
 * pattern.  The census driver cross-checks exactly that; a disagreement means
 * this analyzer is wrong, not that the stamp is.
 *
 * ============================================================================
 * THE THREE FACTS, AND THE TIERS THEY DECIDE
 * ============================================================================
 *
 *   req_byte   the necessary byte, `reqbyte.c`'s own pick.
 *   dmin/dmax  the tightest interval of offsets, FROM THE MATCH START, at
 *              which a guaranteed occurrence of that byte sits.  `dmax`
 *              unbounded is written -1.
 *   run        the longest NECESSARY LITERAL RUN -- a maximal sequence of
 *              bytes every match contains contiguously, at fixed deltas from
 *              each other -- with its own offset interval.
 *
 * Tier, per the plan row:
 *   1   dmin == dmax        a FIXED offset: `src/opt/prefix_k.c` territory,
 *                           already built for the DFA route.
 *   2   dmax finite         a BOUNDED range: a failed attempt at `s` with the
 *                           next occurrence at `q` may jump to `q - dmax`.
 *   2b  run length >= 2     the PAIR: memchr the rarest member, then ONE
 *                           unaligned word compare at the known delta.
 *   3   dmax unbounded      reverse-inner territory ([ENG-ISL]).
 *
 * ============================================================================
 * SOUNDNESS DIRECTION, STATED ONCE
 * ============================================================================
 *
 * Every conservative arm widens: `dmin` may UNDER-estimate and `dmax` may
 * OVER-estimate, both of which only weaken the bound; the empty set and an
 * unbounded `dmax` disable a tier rather than mis-apply it.  A backreference
 * and a linked call take unbounded width and no bytes, `reqbyte.c`'s own two
 * declines; a lookaround's body is not descended into, for `reqbyte.c`'s
 * stated correctness reason (a lookbehind's bytes sit BEFORE the match).
 *
 * KNOWN FALSE NEGATIVES (under-estimates, all safe, all stated because a
 * census that does not name them over-claims its own zeroes):
 *   (i)  at an `A_ALT` the run analysis keeps only the branches' common
 *        PREFIX and common SUFFIX, so `(?:abc|abd)` reports run "ab" (right)
 *        but `(?:xabcy|zabcw)` reports no run at all (a real "abc" missed).
 *   (ii) a run is not merged ACROSS iterations of a repeat, so `(?:ab){2,}`
 *        reports run "ab" and not "abab".
 *   (iii) a class with more than one member contributes no byte, which is
 *        every caselessly-folded literal (D23 folds `(?i)a` to `[aA]` at
 *        parse time) -- so a `(?i)` pattern's run figures are floors.
 *
 * Build (never by `make`):
 *   gcc -O2 -Ilib -Isrc -o reqpos_probe reqpos_probe.c build/libpcrec.a
 * Input : one record per line, `id<TAB>hex-encoded pattern bytes`.
 * Output: one TSV row per record.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

#define W_INF   (-1LL)          /* unbounded width / offset */
#define MAXRUN  64              /* a run longer than this is reported clamped */

typedef struct {
    unsigned char bits[32];     /* necessary bytes -- reqbyte.c's set */
    int  pick;                  /* reqbyte.c's chosen member, -1 when empty */
    long long minw, maxw;       /* node width in BYTES; maxw W_INF = unbounded */
    long long pmin[256], pmax[256];   /* tightest guaranteed offset per byte */
    int  head_len, tail_len, best_len;
    unsigned char head[MAXRUN], tail[MAXRUN], best[MAXRUN];
    long long best_pmin, best_pmax;
} Res;

static long long wadd(long long a, long long b)
{ return (a == W_INF || b == W_INF) ? W_INF : a + b; }

static long long wmul(long long a, long long n)
{ return (a == W_INF || n < 0) ? W_INF : a * n; }

static long long wsub(long long a, long long b)          /* a - b, a may be INF */
{ return a == W_INF ? W_INF : a - b; }

static long long wmax(long long a, long long b)
{ return (a == W_INF || b == W_INF) ? W_INF : (a > b ? a : b); }

static bool hasb(const Res *r, int b)
{ return b >= 0 && (r->bits[b >> 3] & (unsigned char)(1u << (b & 7))) != 0; }

static void setb(Res *r, int b)
{ r->bits[b >> 3] |= (unsigned char)(1u << (b & 7)); }

static Res res_empty(long long mn, long long mx)
{
    Res r;
    memset(&r, 0, sizeof r);
    r.pick = -1; r.minw = mn; r.maxw = mx;
    r.best_pmin = 0; r.best_pmax = 0;
    return r;
}

/* Record a guaranteed occurrence of `b` at offset interval [lo,hi], keeping
 * the TIGHTEST one seen (smallest `hi`), because `dmax` is what tier 2 pays
 * for. */
static void note(Res *r, int b, long long lo, long long hi)
{
    if (!hasb(r, b)) { setb(r, b); r->pmin[b] = lo; r->pmax[b] = hi; return; }
    if (r->pmax[b] == W_INF || (hi != W_INF && hi < r->pmax[b])) {
        r->pmin[b] = lo; r->pmax[b] = hi;
    }
}

static void setrun(unsigned char *dst, int *dlen,
                   const unsigned char *a, int alen,
                   const unsigned char *b, int blen)
{
    int n = 0, i;
    for (i = 0; i < alen && n < MAXRUN; i++) dst[n++] = a[i];
    for (i = 0; i < blen && n < MAXRUN; i++) dst[n++] = b[i];
    *dlen = n;
}

static void keep_best(Res *r, const unsigned char *s, int len,
                      long long lo, long long hi)
{
    if (len > r->best_len) {
        memcpy(r->best, s, (size_t)len);
        r->best_len = len; r->best_pmin = lo; r->best_pmax = hi;
    }
}

static Res walk(const Ast *a);

/* CONCATENATION.  `l` is to the LEFT, so `r`'s offsets shift by `l`'s width
 * and `r`'s pick wins -- reqbyte.c's rightmost rule at the one node kind that
 * has a left and a right in subject order. */
static Res cat(Res l, Res r)
{
    Res o = res_empty(wadd(l.minw, r.minw), wadd(l.maxw, r.maxw));
    int b;
    for (b = 0; b < 256; b++) {
        if (hasb(&l, b)) note(&o, b, l.pmin[b], l.pmax[b]);
        if (hasb(&r, b))
            note(&o, b, wadd(r.pmin[b], l.minw), wadd(r.pmax[b], l.maxw));
    }
    o.pick = (r.pick >= 0) ? r.pick : l.pick;

    /* A run reaching offset 0 of the whole node survives only if `l` IS that
     * run -- fixed width and entirely literal. */
    if (l.head_len == l.minw && l.minw == l.maxw)
        setrun(o.head, &o.head_len, l.head, l.head_len, r.head, r.head_len);
    else
        setrun(o.head, &o.head_len, l.head, l.head_len, NULL, 0);
    if (r.tail_len == r.minw && r.minw == r.maxw)
        setrun(o.tail, &o.tail_len, l.tail, l.tail_len, r.tail, r.tail_len);
    else
        setrun(o.tail, &o.tail_len, r.tail, r.tail_len, NULL, 0);

    keep_best(&o, l.best, l.best_len, l.best_pmin, l.best_pmax);
    keep_best(&o, r.best, r.best_len,
              wadd(r.best_pmin, l.minw), wadd(r.best_pmax, l.maxw));
    /* THE MERGE: `l`'s tail ends at `l`'s end in every string and `r`'s head
     * begins at `r`'s start, so the two are contiguous and their start offset
     * is `l`'s width minus the tail's length. */
    if (l.tail_len && r.head_len) {
        unsigned char m[2 * MAXRUN]; int mlen;
        setrun(m, &mlen, l.tail, l.tail_len, r.head, r.head_len);
        if (mlen > MAXRUN) mlen = MAXRUN;
        keep_best(&o, m, mlen, l.minw - l.tail_len, wsub(l.maxw, l.tail_len));
    }
    keep_best(&o, o.head, o.head_len, 0, 0);
    return o;
}

/* ALTERNATION.  Only a byte necessary for BOTH branches survives, and its
 * offset interval is the UNION of the two -- whichever branch matched, an
 * occurrence lies inside it. */
static Res alt(Res l, Res r)
{
    Res o = res_empty(l.minw < r.minw ? l.minw : r.minw, wmax(l.maxw, r.maxw));
    int b, i;
    for (b = 0; b < 256; b++) {
        if (!hasb(&l, b) || !hasb(&r, b)) continue;
        long long lo = l.pmin[b] < r.pmin[b] ? l.pmin[b] : r.pmin[b];
        long long hi = (l.pmax[b] == W_INF || r.pmax[b] == W_INF)
                       ? W_INF : (l.pmax[b] > r.pmax[b] ? l.pmax[b] : r.pmax[b]);
        setb(&o, b); o.pmin[b] = lo; o.pmax[b] = hi;
    }
    /* reqbyte.c's pick rule, verbatim: the right branch's pick if it
     * survived, else the left's, else the largest surviving byte. */
    o.pick = -1;
    if (hasb(&o, r.pick))      o.pick = r.pick;
    else if (hasb(&o, l.pick)) o.pick = l.pick;
    else for (i = 255; i >= 0; i--) if (hasb(&o, i)) { o.pick = i; break; }

    for (i = 0; i < l.head_len && i < r.head_len && l.head[i] == r.head[i]; i++)
        o.head[i] = l.head[i];
    o.head_len = i;
    for (i = 0; i < l.tail_len && i < r.tail_len
               && l.tail[l.tail_len - 1 - i] == r.tail[r.tail_len - 1 - i]; i++) ;
    o.tail_len = i;
    memcpy(o.tail, l.tail + (l.tail_len - i), (size_t)i);
    keep_best(&o, o.head, o.head_len, 0, 0);
    if (o.tail_len)
        keep_best(&o, o.tail, o.tail_len,
                  o.minw - o.tail_len, wsub(o.maxw, o.tail_len));
    return o;
}

/* The `A_CAT` and `A_CAP`/`A_ATOMIC` spines are walked ITERATIVELY, for
 * `src/opt/reqbyte.c`'s and `src/opt/mrl.c`'s shared reason: both are as long
 * as the PATTERN, not as deep as its nesting, and this project has segfaulted
 * its own compiler on a 20,000-byte literal for want of exactly that.  (A
 * first draft of this file recursed and died on the shipped corpus, which is
 * why the rule is restated here rather than assumed.)  `acc` carries what has
 * been analyzed to the RIGHT of the current node, so the spine is folded
 * right to left -- the order pcrec's own left-leaning `A_CAT` builds. */
static Res walk(const Ast *a)
{
    Res acc; int have_acc = 0;
    for (;;) {
    switch (a->k) {
    case A_CAT: {
        Res r = walk(a->r);
        acc = have_acc ? cat(r, acc) : r;
        have_acc = 1;
        a = a->l;
        continue;
    }
    case A_CAP:
    case A_ATOMIC: a = a->l; continue;
    case A_ALT: {
        /* `A_ALT` nests to the LEFT; fold the whole spine so a 9-branch
         * alternation is one intersection and not eight nested ones. */
        Res s2 = walk(a->r);
        const Ast *t = a->l;
        while (t->k == A_ALT) { s2 = alt(walk(t->r), s2); t = t->l; }
        s2 = alt(walk(t), s2);
        return have_acc ? cat(s2, acc) : s2;
    }
    case A_REP: {
        Res b = walk(a->l);
        long long mn = wmul(b.minw, a->u.rep.rmin);
        long long mx = (a->u.rep.rmax < 0) ? W_INF : wmul(b.maxw, a->u.rep.rmax);
        if (a->u.rep.rmin < 1) {
            Res o = res_empty(0, mx);
            return have_acc ? cat(o, acc) : o;
        }
        /* A guaranteed occurrence sits in the FIRST iteration, which starts
         * at offset 0 of the repeat -- so the body's own offsets carry over
         * unchanged, which is what keeps `dmax` tight under a `+`. */
        Res o = b; o.minw = mn; o.maxw = mx;
        return have_acc ? cat(o, acc) : o;
    }
    case A_CLASS: {
        int b = pcrec_cls_single(a);
        Res o = res_empty(1, 1);
        if (b >= 0) {
            note(&o, b, 0, 0); o.pick = b;
            o.head[0] = o.tail[0] = o.best[0] = (unsigned char)b;
            o.head_len = o.tail_len = o.best_len = 1;
            o.best_pmin = o.best_pmax = 0;
        }
        return have_acc ? cat(o, acc) : o;
    }
    /* Zero-width: no byte, no width.  `A_LOOK`'s body is deliberately not
     * descended into (reqbyte.c's header says why that is CORRECTNESS). */
    case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
    case A_LOOK: {
        Res o = res_empty(0, 0);
        return have_acc ? cat(o, acc) : o;
    }
    /* The two declines.  Width is 0..unbounded: under-estimating `minw` and
     * over-estimating `maxw` both only weaken the bound. */
    case A_BREF:
    case A_CALL: {
        Res o = res_empty(0, W_INF);
        return have_acc ? cat(o, acc) : o;
    }
    }
    }
}

/* ------------------------------------------------------------------ driver */

static Ast *parse_lower(const char *pat, Ctx *cx, pcrec_options *defo, int enc)
{
    memset(cx, 0, sizeof(*cx));
    cx->enabled_features = pcrec_enabled_mask();
    pcrec_default_options(defo);
    defo->encoding = enc;
    cx->pat = pat;
    cx->patlen = strlen(pat);
    cx->opt = defo;
    cx->job = calloc(1, sizeof(Job));
    if (!cx->job) { fprintf(stderr, "out of memory\n"); exit(2); }
    cx->arena.cx = cx;
    Ast *root = NULL;
    if (setjmp(cx->jb) == 0) {
        pcrec_parse_mods_init(cx);
        root = pcrec_parse_info(cx, NULL);
        /* THE PIPELINE PREFIX, and it is three passes and not one.
         *
         * A first draft ran parse + `pcrec_lower_enc` only, on the reasoning
         * that lowering is what makes an `A_CLASS` a BYTE class.  The
         * cross-check against batch 1's `RX_REQ_BYTE` stamp caught it: on
         * `/user|/users` the stamp reads 114 (`r`) and the probe read 115
         * (`s`), because `pcrec_altcls` FACTORS that alternation to
         * `/user(?:s)?` before anything downstream sees it
         * (`RX_ALTCLS_FACTORED 1` on the artifact) and the optional tail then
         * contributes no necessary byte at all.  The general form is worth
         * more than the cell: AN ANALYSIS'S ANSWER IS A PROPERTY OF THE TREE
         * AT ITS OWN CALL SITE, so a census that reconstructs the pipeline
         * must reconstruct every REWRITING pass above that site -- and the
         * only reason this one was found is that the census was built with a
         * cross-check against the shipped stamp rather than against its own
         * reasoning.
         *
         * `pcrec_discharge_atomic` is included for the same reason even
         * though it cannot move this answer (the walk treats `A_ATOMIC` as
         * transparent, `reqbyte.c`'s own arm): matching the shipped prefix is
         * cheaper than arguing each pass's irrelevance.  Everything BELOW the
         * lowering in `compile.c` is analysis, not rewriting, so the prefix
         * stops there. */
        if (root) root = pcrec_altcls(cx, root);
        if (root) root = pcrec_discharge_atomic(cx, root);
        if (root) root = pcrec_lower_enc(cx, root);
    }
    return root;
}

static void emit_hex(const unsigned char *s, int n)
{ int i; for (i = 0; i < n; i++) printf("%02x", s[i]); if (!n) printf("-"); }

int main(int argc, char **argv)
{
    char err[256];
    int enc = PCREC_ENC_BYTE;
    if (argc > 1 && !strcmp(argv[1], "-e") && argc > 2 && !strcmp(argv[2], "utf8"))
        enc = PCREC_ENC_UTF8;
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0) {
        fprintf(stderr, "features: %s\n", err); return 2;
    }
    printf("id\tstatus\treq_byte\tdmin\tdmax\ttier\trun_len\trun_hex\t"
           "run_pmin\trun_pmax\tpick_in_run\tminw\tmaxw\tset_hex\n");

    char *line = NULL; size_t cap = 0; ssize_t got;
    while ((got = getline(&line, &cap, stdin)) > 0) {
        if (got && line[got - 1] == '\n') line[--got] = 0;
        if (!got) continue;
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab = 0;
        const char *id = line, *hex = tab + 1;
        size_t hn = strlen(hex) / 2;
        char *pat = malloc(hn + 1);
        for (size_t i = 0; i < hn; i++) {
            unsigned v; sscanf(hex + 2 * i, "%2x", &v); pat[i] = (char)v;
        }
        pat[hn] = 0;

        Ctx cx; pcrec_options defo;
        Ast *root = parse_lower(pat, &cx, &defo, enc);
        if (!root) {
            printf("%s\trefused\t-1\t-1\t-1\t-\t0\t-\t-1\t-1\t0\t-1\t-1\t-\n", id);
        } else {
            Res r = walk(root);
            int p = r.pick;
            long long dmin = p >= 0 ? r.pmin[p] : -1;
            long long dmax = p >= 0 ? r.pmax[p] : -1;
            const char *tier;
            if (p < 0)                    tier = "none";
            else if (dmax == W_INF)       tier = "3";
            else if (dmin == dmax)        tier = "1";
            else                          tier = "2";
            int in = 0;
            for (int i = 0; i < r.best_len; i++) if (r.best[i] == p) in = 1;
            printf("%s\tok\t%d\t%lld\t%lld\t%s\t%d\t", id, p, dmin, dmax,
                   tier, r.best_len);
            emit_hex(r.best, r.best_len);
            printf("\t%lld\t%lld\t%d\t%lld\t%lld\t",
                   r.best_len ? r.best_pmin : -1,
                   r.best_len ? r.best_pmax : -1,
                   in, r.minw, r.maxw);
            /* THE WHOLE NECESSARY SET, not just the pick.  `reqbyte.c` emits
             * ONE member (the rightmost, PCRE2's own choice); which member is
             * cheapest is a SUBJECT question, so the census reports the set
             * and lets the frequency join decide. */
            { int any = 0, b2;
              for (b2 = 0; b2 < 256; b2++)
                  if (hasb(&r, b2)) { printf("%02x", b2); any = 1; }
              if (!any) printf("-"); }
            printf("\n");
        }
        pcrec_arena_free(&cx.arena);
        free(cx.job);
        free(pat);
    }
    free(line);
    return 0;
}
