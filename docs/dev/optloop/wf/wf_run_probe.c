/* [WORD-FOLD] THE D77 CUBE-RUN CENSUS INSTRUMENT — a throwaway analyzer, not
 * a mechanism and never wired into the build.
 *
 * ============================================================================
 * WHAT IT ANSWERS
 * ============================================================================
 *
 * `docs/dev/plan.md`'s `[WORD-FOLD]` row proposes ONE AND-mask compare form,
 * `(w & K) == T` over an 8-byte (or wider) load, that covers an EXACT literal
 * position (K=0xFF), a caseless letter (K=0xDF) and every other ONE-CUBE class
 * uniformly. Its D77 gate is a CENSUS, before any build: how many corpus/bench
 * literal-run windows of length >= 4 (and >= 8) exist, and of those, how many
 * have at least one position that is a cube but NOT a singleton byte (the
 * form's unique value over a plain memcmp) versus being broken by a position
 * that is not a cube at all.
 *
 * This file walks the REAL parser/lowering pipeline (the same prefix
 * `docs/dev/optloop/c2/reqpos_probe.c` established and cross-checked: parse +
 * `pcrec_altcls` + `pcrec_discharge_atomic` + `pcrec_lower_enc`), so the tree
 * it walks is the tree the emitters walk — after the lowering every `A_CLASS`
 * is a BYTE class (`docs/dev/plan.md`'s own scope statement: "byte-domain
 * cubes only ... utf8 multi-byte folds were never byte cubes").
 *
 * ============================================================================
 * THE ONE-CUBE TEST, BYTE DOMAIN
 * ============================================================================
 *
 * `byte_cube_of` is `studies/cls_tree_study/kit.py`'s / `discover.c`'s
 * `cube_of` (the O(k) closed-form AND/OR-of-ranges test, MEASURED there
 * against all 1,114,112 code points with zero disagreement) SPECIALIZED to a
 * FIXED 8-bit domain [0,255] rather than a dynamically-sized DP section — the
 * domain a byte-class position always has, matching the plan row's own
 * `memcpy(&w, subject+pos, 8); (w & K) == T` form, where K is 8 bits wide by
 * construction. The O(k) necessary-condition shortcut is skipped (it exists
 * in the DP's context to avoid an O(2^nbits) blowup at nbits up to ~24; here
 * nbits is always 8) — the exact test walks all 256 points directly against
 * the interval list, which is cheap and leaves no room for a false positive
 * the O(k) shortcut could otherwise hide.
 *
 * A class with `nfree == 0` (the cube is a single point) is a SINGLETON —
 * `reqpos_probe.c`'s own `pcrec_cls_single`, subsumed here as the `nfree==0`
 * case of the same one test rather than a separate function, matching the
 * plan row's own claim that "a byte PAST THE LITERAL'S END is the degenerate
 * all-bits-free cube" and every other position is the same shape.
 *
 * ============================================================================
 * THE RUN WALK
 * ============================================================================
 *
 * Structurally identical to `reqpos_probe.c`'s `head`/`tail`/`best` cat/alt
 * merge (the A_CAT spine walked ITERATIVELY for the same reason stated
 * there — it is as long as the PATTERN, not as deep as its nesting, and a
 * recursive version has segfaulted this project's own compiler on a
 * 20,000-byte literal before), with ONE change: instead of tracking "does
 * this position carry byte B", each position now carries a `Pos` (cube
 * membership: is-a-cube, is-a-singleton, K, T). A class that is NOT a cube at
 * all contributes an EMPTY position (breaks any run through it), exactly the
 * shape `reqpos_probe.c` gives a non-singleton class today.
 *
 * `best` tracks the SINGLE LONGEST run per pattern, not every run in it —
 * the same simplification `reqpos_census.md` made for its own necessary-run
 * census (the tier tables there are also a per-pattern longest-run
 * classification). For the population question this census answers ("how
 * many patterns carry a run of length >= N, and of what composition") the
 * longest run is exactly the right witness: if the longest run in a pattern
 * is >= N, so is at least one run; a pattern's SECOND-longest run is not
 * separately counted, which under-counts totals but never over-counts
 * populations. `n_class_atoms`/`n_cube_atoms` are also tracked, as a coarse
 * proxy for how much a pattern's cube-eligible literal content is being
 * fragmented by non-cube breaks (best_len vs n_cube_atoms).
 *
 * KNOWN FALSE NEGATIVES (all safe — they under-report, never over-report,
 * `reqpos_probe.c`'s own stated direction):
 *   (i)   at an `A_ALT` only the branches' common PREFIX and common SUFFIX
 *         survive, so `(?:xabcy|zabcw)` reports no run where `abc` is one.
 *   (ii)  a run is not merged ACROSS iterations of a repeat: `(?:ab){2,}`
 *         reports run "ab", not "abab".
 *   (iii) a lookaround's body is NOT descended into (mirroring
 *         `reqbyte.c`/`reqpos_probe.c`'s own arm) — a literal run entirely
 *         inside a lookaround is invisible here, even though its bytes ARE
 *         consumed by the emitted matcher. Recorded as a scope limitation,
 *         not fixed: this census's population question is about the SAME
 *         literal-chain shape `[OPT-VMLIT]`'s row already scopes to ordinary
 *         concatenation, and a lookaround body is a second walk this
 *         instrument does not attempt.
 *
 * Build (never by `make`):
 *   gcc -O2 -Ilib -Isrc -o wf_run_probe wf_run_probe.c build/libpcrec.a
 * Input : one record per line, `id<TAB>hex-encoded pattern bytes`.
 * Output: one TSV row per record.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

#define MAXRUN 96               /* a run longer than this is reported clamped */

typedef struct { int cube; int exact; unsigned K, T; } Pos;

typedef struct {
    long long minw, maxw;
    int head_len, tail_len, best_len;
    Pos head[MAXRUN], tail[MAXRUN], best[MAXRUN];
    long long n_class_atoms, n_cube_atoms;
} Res;

static long long wadd(long long a, long long b)
{ return (a < 0 || b < 0) ? -1 : a + b; }   /* -1 is this file's W_INF */

static long long wmul(long long a, long long n)
{ return (a < 0 || n < 0) ? -1 : a * n; }

/* ---- the byte-domain one-cube test ------------------------------------ */

static unsigned range_and8(unsigned a, unsigned b)
{ int sh = 0; while (a != b) { a >>= 1; b >>= 1; sh++; } return a << sh; }

static unsigned range_or8(unsigned a, unsigned b)
{
    if (a == b) return a;
    unsigned x = a ^ b; int m = 0;
    while (x) { x >>= 1; m++; }
    return (a | b) | ((1u << m) - 1u);
}

/* Is `iv[0..n)` (sorted, disjoint, non-adjacent, `cpset.c`'s own invariant)
 * exactly one AND-mask cube of the 8-bit byte domain? O(n) aggregate plus a
 * 256-point exact check (cheap at this width; see the header). */
static int byte_cube_of(const PcrecCpRange *iv, int n, unsigned *K, unsigned *T)
{
    if (n <= 0) return 0;
    unsigned a_all = 0xFFu, o_all = 0, nmem = 0;
    for (int t = 0; t < n; t++) {
        if (iv[t].lo > 0xFFu || iv[t].hi > 0xFFu) return 0; /* not byte-domain */
        unsigned x0 = iv[t].lo, x1 = iv[t].hi;
        a_all &= range_and8(x0, x1);
        o_all |= range_or8(x0, x1);
        nmem += x1 - x0 + 1;
    }
    unsigned val = a_all;
    unsigned care = 0xFFu & ~(o_all & ~a_all);
    int nfree = 8 - __builtin_popcount(care);
    unsigned csize = 1u << nfree;
    if (csize != nmem) return 0;
    for (unsigned x = 0; x < 256; x++) {
        int incube = ((x & care) == val);
        int inset = 0;
        for (int t = 0; t < n; t++)
            if (x >= iv[t].lo && x <= iv[t].hi) { inset = 1; break; }
        if (incube != inset) return 0;
    }
    *K = care; *T = val;
    return 1;
}

/* ---- run bookkeeping, mirroring reqpos_probe.c's shape ---------------- */

static Res res_empty(long long mn, long long mx)
{
    Res r; memset(&r, 0, sizeof r); r.minw = mn; r.maxw = mx; return r;
}

static void setrun(Pos *dst, int *dlen, const Pos *a, int alen,
                   const Pos *b, int blen)
{
    int n = 0, i;
    for (i = 0; i < alen && n < MAXRUN; i++) dst[n++] = a[i];
    for (i = 0; i < blen && n < MAXRUN; i++) dst[n++] = b[i];
    *dlen = n;
}

static void keep_best(Res *r, const Pos *s, int len)
{
    if (len > r->best_len) {
        if (len > MAXRUN) len = MAXRUN;
        memcpy(r->best, s, (size_t)len * sizeof *s);
        r->best_len = len;
    }
}

static Res walk(const Ast *a);

static Res cat(Res l, Res r)
{
    Res o = res_empty(wadd(l.minw, r.minw), wadd(l.maxw, r.maxw));
    o.n_class_atoms = l.n_class_atoms + r.n_class_atoms;
    o.n_cube_atoms  = l.n_cube_atoms  + r.n_cube_atoms;

    if (l.head_len == l.minw && l.minw == l.maxw)
        setrun(o.head, &o.head_len, l.head, l.head_len, r.head, r.head_len);
    else
        setrun(o.head, &o.head_len, l.head, l.head_len, NULL, 0);
    if (r.tail_len == r.minw && r.minw == r.maxw)
        setrun(o.tail, &o.tail_len, l.tail, l.tail_len, r.tail, r.tail_len);
    else
        setrun(o.tail, &o.tail_len, r.tail, r.tail_len, NULL, 0);

    keep_best(&o, l.best, l.best_len);
    keep_best(&o, r.best, r.best_len);
    if (l.tail_len && r.head_len) {
        Pos m[2 * MAXRUN]; int mlen;
        setrun(m, &mlen, l.tail, l.tail_len, r.head, r.head_len);
        if (mlen > MAXRUN) mlen = MAXRUN;
        keep_best(&o, m, mlen);
    }
    keep_best(&o, o.head, o.head_len);
    return o;
}

/* Common PREFIX/SUFFIX of the two branches, same-cube positions only —
 * `reqpos_probe.c`'s byte-equality test generalized to cube equality. */
static int pos_eq(Pos a, Pos b)
{ return a.cube && b.cube && a.K == b.K && a.T == b.T; }

static Res alt(Res l, Res r)
{
    Res o = res_empty(l.minw < r.minw ? l.minw : r.minw,
                      (l.maxw < 0 || r.maxw < 0) ? -1
                      : (l.maxw > r.maxw ? l.maxw : r.maxw));
    o.n_class_atoms = l.n_class_atoms + r.n_class_atoms;
    o.n_cube_atoms  = l.n_cube_atoms  + r.n_cube_atoms;
    int i;
    for (i = 0; i < l.head_len && i < r.head_len && pos_eq(l.head[i], r.head[i]); i++)
        o.head[i] = l.head[i];
    o.head_len = i;
    for (i = 0; i < l.tail_len && i < r.tail_len
               && pos_eq(l.tail[l.tail_len - 1 - i], r.tail[r.tail_len - 1 - i]); i++) ;
    o.tail_len = i;
    memcpy(o.tail, l.tail + (l.tail_len - i), (size_t)i * sizeof *o.tail);
    keep_best(&o, l.best, l.best_len);
    keep_best(&o, r.best, r.best_len);
    keep_best(&o, o.head, o.head_len);
    if (o.tail_len) keep_best(&o, o.tail, o.tail_len);
    return o;
}

/* Same iterative-spine discipline as reqpos_probe.c, for the same reason. */
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
        Res s2 = walk(a->r);
        const Ast *t = a->l;
        while (t->k == A_ALT) { s2 = alt(walk(t->r), s2); t = t->l; }
        s2 = alt(walk(t), s2);
        return have_acc ? cat(s2, acc) : s2;
    }
    case A_REP: {
        Res b = walk(a->l);
        long long mn = wmul(b.minw, a->u.rep.rmin);
        long long mx = (a->u.rep.rmax < 0) ? -1 : wmul(b.maxw, a->u.rep.rmax);
        if (a->u.rep.rmin < 1) {
            Res o = res_empty(0, mx);
            o.n_class_atoms = b.n_class_atoms; o.n_cube_atoms = b.n_cube_atoms;
            return have_acc ? cat(o, acc) : o;
        }
        Res o = b; o.minw = mn; o.maxw = mx;
        return have_acc ? cat(o, acc) : o;
    }
    case A_CLASS: {
        unsigned K = 0, T = 0;
        int is_cube = byte_cube_of(a->u.cls.iv, a->u.cls.n, &K, &T);
        Res o = res_empty(1, 1);
        o.n_class_atoms = 1;
        if (is_cube) {
            o.n_cube_atoms = 1;
            Pos p; p.cube = 1; p.K = K; p.T = T; p.exact = (K == 0xFFu);
            o.head[0] = o.tail[0] = o.best[0] = p;
            o.head_len = o.tail_len = o.best_len = 1;
        }
        return have_acc ? cat(o, acc) : o;
    }
    case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
    case A_LOOK: {
        Res o = res_empty(0, 0);
        return have_acc ? cat(o, acc) : o;
    }
    case A_BREF:
    case A_CALL:
    case A_VAR: {   /* A_VAR is a leaf like A_BREF: its bytes come from the
                     * caller at match time, not from the pattern (internal.h). */
        Res o = res_empty(0, -1);
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
        /* Same pipeline prefix reqpos_probe.c cross-checked: altcls FACTORS
         * alternations before anything downstream sees them, so a census that
         * skipped it would measure the pre-factoring tree, not the emitted
         * one's. */
        if (root) root = pcrec_altcls(cx, root);
        if (root) root = pcrec_discharge_atomic(cx, root);
        if (root) root = pcrec_lower_enc(cx, root);
    }
    return root;
}

static void print_run(const Pos *p, int len)
{
    if (!len) { printf("-\t-"); return; }
    for (int i = 0; i < len; i++) printf("%02x%02x", p[i].K & 0xFF, p[i].T & 0xFF);
    putchar('\t');
    for (int i = 0; i < len; i++) putchar(p[i].exact ? 'e' : 'c');
}

int main(int argc, char **argv)
{
    char err[256];
    int enc = PCREC_ENC_BYTE;
    if (argc > 1 && !strcmp(argv[1], "-e") && argc > 2 && !strcmp(argv[2], "utf8"))
        enc = PCREC_ENC_UTF8;
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0) {
        fprintf(stderr, "features: %s\n", err); return 2;
    }
    printf("id\tstatus\tminw\tmaxw\tbest_len\tn_exact\tn_cube_ns\t"
           "n_class_atoms\tn_cube_atoms\tKT_hex\tkinds\n");

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
            printf("%s\trefused\t-1\t-1\t0\t0\t0\t0\t0\t-\t-\n", id);
        } else {
            Res r = walk(root);
            int n_exact = 0, n_cns = 0;
            for (int i = 0; i < r.best_len; i++)
                if (r.best[i].exact) n_exact++; else n_cns++;
            printf("%s\tok\t%lld\t%lld\t%d\t%d\t%d\t%lld\t%lld\t",
                   id, r.minw, r.maxw, r.best_len, n_exact, n_cns,
                   r.n_class_atoms, r.n_cube_atoms);
            print_run(r.best, r.best_len);
            printf("\n");
        }
        pcrec_arena_free(&cx.arena);
        free(cx.job);
        free(pat);
    }
    free(line);
    return 0;
}
