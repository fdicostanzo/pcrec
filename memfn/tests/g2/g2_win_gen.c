/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's window family, lane
 *   wsc1, D172 S2 commit 1).
 *
 * memfn/tests/g2/g2_win_gen.c — G2'S WINDOW FAMILY, THE GENERATOR (the only
 * file of the family that calls the kit). It GENERATES window sites
 * (docs/design/memfn/window_site.md rev 3.2 §1: spans with random starts,
 * negative ones included, sets, cores and verify facts; one or two
 * alternatives with their ENTRY; table offers; the floor, SUBJECT or an
 * expression; byte-rates NONE, skewed or tie-heavy), and for each:
 *   asks the kit's PHASE 1 (mf_wdecide) on a plain art (the family is every
 *   art's since S2 commit 6), and copies the reply;
 *   renders PHASE 2 (mf_emit) in one of the frames Table E serves (FUNC/
 *   RETURN, STMT/ASSIGN into a variable or in place into `lo`, STMT/ON_MISS),
 *   with each empty outcome and on_miss shape the frame allows;
 *   writes OUT/g2w_sites.c: every definition, a uniform wrapper per site
 *   (g2_win.h g2w_fn) and the site table: the facts AS GENERATED, the rate,
 *   the frame and the kit's reply. The driver (g2_win_run.c) holds the reply
 *   to the reference's decision and every answer to the facts.
 * A site the kit refuses is a failure (the floor serves every frame of the
 * family but a stated `moved`, which G2 never states, and a REPORT site),
 * except a REPORT site E-find cannot render (D172 S3: a frame other than
 * STMT/ASSIGN, or no stop by G2's own decision), which MUST be refused and
 * is then rendered as a DFA_SCAN site. The CONTROLS: a plain art decides and
 * renders; E-find renders a REPORT site and its deny `no-window-search` refuses
 * it (and sends any other site to the floor); D-hors's deny `no-window-skip`
 * removes its skip table.
 *
 *   g2_win_gen SEED NSITES OUTDIR   (env G2W_S3_SITES: the dense sites, 400;
 *                                    G2W_C1_SITES: the caseless sites, 300;
 *                                    G2W_R2_SITES: the two-byte sites, 300)
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"
#include "g2_win.h"

/* ---- text ------------------------------------------------------------------- */

typedef struct { char *p; size_t len, cap; } buf;

static void bput(buf *b, const char *s, size_t n)
{
    if (b->len + n + 1 > b->cap) {
        b->cap = (b->len + n + 1) * 2;
        b->p = realloc(b->p, b->cap);
        if (!b->p) { perror("realloc"); exit(2); }
    }
    memcpy(b->p + b->len, s, n);
    b->len += n;
    b->p[b->len] = 0;
}

static void bputs(buf *b, const char *s) { bput(b, s, strlen(s)); }

static void bvprintf(buf *b, const char *fmt, va_list ap)
{
    char tmp[4096];
    va_list ap2;
    va_copy(ap2, ap);
    int k = vsnprintf(tmp, sizeof tmp, fmt, ap2);
    va_end(ap2);
    if (k < 0) return;
    if ((size_t)k < sizeof tmp) { bput(b, tmp, (size_t)k); return; }
    char *big = malloc((size_t)k + 1);
    vsnprintf(big, (size_t)k + 1, fmt, ap);
    bput(b, big, (size_t)k);
    free(big);
}

static void bprintf(buf *b, const char *fmt, ...) __attribute__((format(printf, 2, 3)));
static void bprintf(buf *b, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    bvprintf(b, fmt, ap);
    va_end(ap);
}

static void sk_puts(void *u, const char *s) { bputs(u, s); }
static void sk_vprintf(void *u, const char *fmt, va_list ap) { bvprintf(u, fmt, ap); }
static int  sk_cmt_open(void *u, int tier) { (void)u; (void)tier; return 0; }
static void sk_cmt_close(void *u) { (void)u; }
/* a C string literal's body: every byte as a three-digit octal escape */
static void sk_cstr(void *u, const uint8_t *bytes, size_t len)
{
    for (size_t i = 0; i < len; i++) bprintf(u, "\\%03o", bytes[i]);
}

static mf_sink mk_sink(buf *b)
{
    mf_sink s;
    memset(&s, 0, sizeof s);
    s.u = b;
    s.puts = sk_puts;
    s.vprintf = sk_vprintf;
    s.cmt_open = sk_cmt_open;
    s.cmt_close = sk_cmt_close;
    s.cstr = sk_cstr;
    return s;
}

static void *ar_alloc(void *u, size_t n) { (void)u; return calloc(1, n ? n : 1); }
static mf_arena g_arena = { NULL, ar_alloc };

/* ---- G2's facts while it builds them (g2_win.h's types are the read-only
 * view the reference and the driver take) --------------------------------------- */

typedef struct {
    int      start, len, verify, core_lo, core_len;
    uint8_t  set[G2W_MAXPOS][32];
    uint32_t table[G2W_MAXPOS];
} gspan;
typedef struct { int entry, nspan; gspan span[G2W_MAXSPAN]; } galt;
typedef struct { int nalt; galt alt[2]; int wfloor, floor_is_lo, dense, assign; } gfacts;

/* The read-only view of `f` in `x`, its spans in `v`. */
static void view(const gfacts *f, g2w_site *x, g2w_span (*v)[G2W_MAXSPAN])
{
    x->nalt = f->nalt;
    x->wfloor = f->wfloor;
    x->floor_is_lo = f->floor_is_lo;
    for (int ai = 0; ai < f->nalt; ai++) {
        const galt *a = &f->alt[ai];
        for (int i = 0; i < a->nspan; i++) {
            const gspan *g = &a->span[i];
            g2w_span *w = &v[ai][i];
            w->start = g->start; w->len = g->len; w->verify = g->verify;
            w->core_lo = g->core_len ? g->core_lo : 0; w->core_len = g->core_len;
            w->set = g->set;
            w->table = g->table;
        }
        x->alt[ai].entry = a->entry;
        x->alt[ai].nspan = a->nspan;
        x->alt[ai].span = v[ai];
    }
}

/* ---- the random stream -------------------------------------------------------- */

/* THE STREAMS. The S2 population (NSITES sites) draws from `rng`; D172
 * S3's DENSE sites, appended after it (G2W_S3_SITES of them), draw from a
 * stream of their own, so every site the space generated before S3 is
 * generated unchanged (S2's floors were measured on it). */
static unsigned long long rng, rng3 = 0xD172535ull, rng4 = 0xC1CA5E1E55ull,
                          rng5 = 0x2B1A1250ull, rng6 = 0x40B5EB1ull;
static unsigned long long *rngp = &rng;
static int s3_dense;                    /* generating S3's dense sites */
/* THE CASELESS SITES (code review r1 C1/C13, after the dense ones, from a
 * stream of their own): REPORT windows whose positions are mostly two-member
 * cubes (a caseless literal's shape, a high-byte cube among them), so that
 * Table B's PAIR decides their stop and E-find renders it two ways, B-fn
 * (the offset-skip function) and B-pair (the loop's two streams, where a
 * context item keeps the plan from being the function's predicate). */
static int c1_caseless;
static const uint8_t CUBES[][2] = { { 'A', 'a' }, { '0', '1' }, { 0xC4, 0xE4 } };
#define NCUBES (sizeof CUBES / sizeof CUBES[0])
/* THE TWO-BYTE SITES (code review r2 R2-1, after the caseless ones, from a
 * stream of their own): REPORT windows with one position holding ANY two
 * bytes (rarely a one-bit cube), the others one of three bytes drawn with
 * them, and sometimes an item after the window holding two bytes (a
 * lookahead's `[Qq]`), so that Table B's widened PAIR decides their stop and
 * B-pair renders it. The bytes are the driver's subject alphabet's, so a
 * dropped stream deletes matches. */
static int r2_two;
/* THE BELOW-WINDOW SITES (the S3 final review's CHECK-2, after the two-byte
 * ones, from a stream of their own): a dense REPORT window with a dense
 * two-position verify-YES core item just before it, sparser than the window,
 * so the stop (the least mass) lies in a window wholly below the candidate:
 * the population of D-hors's `whi >= 0` scope (no D-hors there; the census
 * below holds it). */
static int h2_below;
static const uint8_t TWOB[] = { 'a', 'b', 'c', '0', '1', '\n', 'x', 0xC4 };
#define NTWOB (sizeof TWOB / sizeof TWOB[0])
static unsigned rnd(unsigned n)
{
    unsigned long long r = *rngp;
    r ^= r << 13; r ^= r >> 7; r ^= r << 17;
    *rngp = r;
    return n ? (unsigned)(r % n) : 0;
}

/* G2's byte alphabet: two one-bit cubes ('a'/'A', '0'/'1') and others. */
static const uint8_t ALPHA[] = { 'a', 'A', 'b', 'c', '0', '1', '\n', 'x' };
#define NALPHA (sizeof ALPHA)

static void set_add(uint8_t s[32], int b) { s[b >> 3] |= (uint8_t)(1u << (b & 7)); }

/* A random position set: one member mostly, a cube, a few members, full,
 * rarely empty. *tabled: worth a table offer (two or more members). */
static void rand_set(uint8_t s[32], int one_only, int *tabled)
{
    memset(s, 0, 32);
    *tabled = 0;
    unsigned k = one_only ? 0 : rnd(100);
    if (k < 60) { set_add(s, ALPHA[rnd(NALPHA)]); return; }
    if (k < 75) { if (rnd(2)) { set_add(s, 'a'); set_add(s, 'A'); } else { set_add(s, '0'); set_add(s, '1'); } return; }
    if (k < 92) {
        unsigned m = 2 + rnd(3);
        for (unsigned i = 0; i < m; i++) set_add(s, ALPHA[rnd(NALPHA)]);
        *tabled = 1;
        return;
    }
    if (k < 98) { memset(s, 0xFF, 32); return; }
    /* empty: an empty meet's own case */
}

static void rand_span(gspan *sp, int start, int len, int verify, int one_only)
{
    memset(sp, 0, sizeof *sp);
    sp->start = start;
    sp->len = len;
    sp->verify = verify;
    unsigned c = rnd(10);
    if (c < 6) { sp->core_lo = 0; sp->core_len = len; }            /* all core */
    else if (c < 8) { sp->core_lo = 0; sp->core_len = 0; }         /* empty    */
    else {
        sp->core_lo = (int)rnd((unsigned)len);
        sp->core_len = 1 + (int)rnd((unsigned)(len - sp->core_lo));
    }
    for (int j = 0; j < len; j++) {
        int t;
        rand_set(sp->set[j], one_only, &t);
        if (t && rnd(2)) sp->table[j] = 1 + (uint32_t)j + 100u * (uint32_t)rnd(3);
    }
}

/* A run span (R): exact or cube positions, verify NO, core all. */
static void run_span(gspan *sp, int start, int len, int first_byte)
{
    memset(sp, 0, sizeof *sp);
    sp->start = start;
    sp->len = len;
    sp->verify = G2W_NO;
    sp->core_lo = 0;
    sp->core_len = len;
    for (int j = 0; j < len; j++) {
        if (j == 0 && first_byte >= 0) { set_add(sp->set[j], first_byte); continue; }
        if (rnd(5) == 0) { set_add(sp->set[j], 'a'); set_add(sp->set[j], 'A'); }
        else set_add(sp->set[j], ALPHA[rnd(NALPHA)]);
    }
}

static int one_member(const uint8_t s[32])
{
    int k = -1, n = 0;
    for (int b = 0; b < 256; b++) if (s[b >> 3] >> (b & 7) & 1) { k = b; n++; }
    return n == 1 ? k : -1;
}

/* ---- the families ------------------------------------------------------------- */

enum { FAM_PARKED, FAM_PAIR, FAM_MASS, FAM_MLINE, FAM_PART, FAM_REPORT, FAM_RANDOM, FAM_N };
static const char *const fam_name[FAM_N] = { "parked", "pair", "mass", "mline", "part",
                                              "report", "random" };

/* The PF shape's PARKED alternative: {0: k0} YES core [0] (bounded: {1: any}
 * in the same span, core [0, 2)), and R in it only under the pin fact (an
 * exact position at 0 equal to k0's one byte). */
static void parked_alt(galt *a, int *k0b)
{
    memset(a, 0, sizeof *a);
    a->entry = G2W_E_PARKED;
    gspan *sp = &a->span[a->nspan++];
    int bounded = rnd(3) == 0;
    rand_span(sp, 0, bounded ? 2 : 1, G2W_YES, rnd(3) != 0);
    sp->core_lo = 0;
    sp->core_len = sp->len;
    if (!sp->set[0][0] && one_member(sp->set[0]) < 0 && rnd(2)) set_add(sp->set[0], 'b');
    if (rnd(4) == 0) {      /* k0 of several bytes, its table offered (the walk) */
        memset(sp->set[0], 0, 32);
        set_add(sp->set[0], 'a'); set_add(sp->set[0], 'b'); set_add(sp->set[0], 'x');
        sp->table[0] = 1;
    }
    if (bounded) memset(sp->set[1], 0xFF, 32);
    *k0b = one_member(sp->set[0]);
    if (*k0b >= 0 && rnd(2)) run_span(&a->span[a->nspan++], 0, 2 + (int)rnd(5), *k0b);
}

/* The RESEED alternative: {0: F0}, one span per walked offset ascending
 * (§1.1's walk-index listing), and R. */
static void reseed_alt(galt *a)
{
    memset(a, 0, sizeof *a);
    a->entry = G2W_E_RESEED;
    gspan *f0 = &a->span[a->nspan++];
    rand_span(f0, 0, 1, G2W_YES, rnd(2));
    f0->core_lo = 0;
    f0->core_len = 1;
    int nw = 1 + (int)rnd(6), off = 0;
    for (int i = 0; i < nw && a->nspan < G2W_MAXSPAN - 1; i++) {
        off += 1 + (int)rnd(3);
        gspan *w = &a->span[a->nspan++];
        rand_span(w, off, 1, G2W_NO, rnd(4) != 0);
        w->core_lo = 0;
        w->core_len = rnd(12) ? 1 : 0;          /* rarely a non-core walked offset */
    }
    if (rnd(2)) run_span(&a->span[a->nspan++], (int)rnd(4), 2 + (int)rnd(6), -1);
}

static void gen_facts(int fam, gfacts *x)
{
    memset(x, 0, sizeof *x);
    x->nalt = 1;
    x->wfloor = rnd(2) ? G2W_F_SUBJECT : G2W_F_UNSTATED;
    switch (fam) {
    case FAM_PARKED: {
        int k0;
        parked_alt(&x->alt[0], &k0);
        break;
    }
    case FAM_PAIR: {
        int k0;
        x->nalt = 2;
        int pk = (int)rnd(2);           /* the alternatives are UNORDERED */
        parked_alt(&x->alt[pk], &k0);
        reseed_alt(&x->alt[1 - pk]);
        break;
    }
    case FAM_MASS: {
        galt *a = &x->alt[0];
        a->entry = G2W_E_NONE;
        a->nspan = 1 + (int)rnd(3);
        for (int i = 0; i < a->nspan; i++)
            rand_span(&a->span[i], (int)rnd(10) - 3, 1 + (int)rnd(6),
                      rnd(3) ? G2W_YES : G2W_NO, 0);
        if (rnd(4) == 0) x->wfloor = G2W_F_EXPR;
        break;
    }
    case FAM_MLINE: {
        galt *a = &x->alt[0];
        a->entry = G2W_E_NONE;
        a->nspan = 1;
        gspan *sp = &a->span[0];
        sp->start = -1;
        sp->len = 1;
        sp->verify = G2W_YES;
        sp->core_lo = 0;
        sp->core_len = 1;
        set_add(sp->set[0], '\n');
        x->wfloor = G2W_F_EXPR;
        x->floor_is_lo = 1;
        break;
    }
    case FAM_PART: {
        galt *a = &x->alt[0];
        a->entry = G2W_E_NONE;
        a->nspan = 1;
        if (rnd(2)) run_span(&a->span[0], (int)rnd(3), 1 + (int)rnd(8), -1);
        else rand_span(&a->span[0], (int)rnd(3), 1, G2W_YES, 0);
        a->span[0].verify = rnd(3) ? G2W_YES : G2W_NO;
        break;
    }
    case FAM_REPORT: {
        galt *a = &x->alt[0];
        a->entry = G2W_E_NONE;
        int k = c1_caseless ? 2 + (int)rnd(7) : r2_two ? 1 + (int)rnd(8) : 1 + (int)rnd(5);
        rand_span(&a->span[a->nspan++], 0, k, G2W_YES, 0);
        a->span[0].core_lo = 0;
        a->span[0].core_len = k;
        if (c1_caseless) {  /* every position a cube, or (mixed) three in four */
            x->assign = 1;
            int mixed = (int)rnd(2);
            for (int j = 0; j < k; j++) {
                memset(a->span[0].set[j], 0, 32);
                const uint8_t *c = CUBES[rnd(NCUBES)];
                set_add(a->span[0].set[j], c[0]);
                if (!mixed || rnd(4)) set_add(a->span[0].set[j], c[1]);
                a->span[0].table[j] = 0;
            }
        }
        uint8_t tw[3];
        if (r2_two) {       /* one position two bytes; the rest all three, or
                               (one in six) one of them, so the pair is
                               mostly the rarest position: PAIR's stop */
            x->assign = 1;
            tw[0] = TWOB[rnd(NTWOB)];
            do tw[1] = TWOB[rnd(NTWOB)]; while (tw[1] == tw[0]);
            do tw[2] = TWOB[rnd(NTWOB)]; while (tw[2] == tw[0] || tw[2] == tw[1]);
            int jp = (int)rnd((unsigned)k);
            for (int j = 0; j < k; j++) {
                memset(a->span[0].set[j], 0, 32);
                if (j == jp) {
                    set_add(a->span[0].set[j], tw[0]);
                    set_add(a->span[0].set[j], tw[1]);
                } else if (rnd(6) == 0) {
                    set_add(a->span[0].set[j], tw[rnd(3)]);
                } else {
                    for (int q = 0; q < 3; q++) set_add(a->span[0].set[j], tw[q]);
                }
                a->span[0].table[j] = 0;
            }
        }
        if (h2_below) {     /* five distinct alphabet bytes a position; not REPORT
                               (E-find cannot find a set stop below the
                               candidate, so a REPORT site there is refused):
                               E-find's frames reach Table D, the rest the floor */
            x->dense = 1;
            for (int j = 0; j < k; j++) {
                memset(a->span[0].set[j], 0, 32);
                for (unsigned q = rnd(NALPHA), m = 0; m < 5; m++)
                    set_add(a->span[0].set[j], ALPHA[(q + m) % NALPHA]);
                a->span[0].table[j] = 0;
            }
            gspan *it = &a->span[a->nspan++];   /* three distinct a position */
            memset(it, 0, sizeof *it);
            it->start = -2;
            it->len = 2;
            it->verify = G2W_YES;
            it->core_lo = 0;
            it->core_len = 2;
            for (int j = 0; j < 2; j++)
                for (unsigned q = rnd(NALPHA), m = 0; m < 3; m++)
                    set_add(it->set[j], ALPHA[(q + m) % NALPHA]);
            x->wfloor = rnd(3) == 0 ? G2W_F_EXPR : G2W_F_SUBJECT;
            break;
        }
        if (s3_dense) {     /* D172 S3: a DENSE window (every position three to
                               five draws of the alphabet, under the tie-heavy
                               rate: D-hors's population, window_site.md §2.5) */
            x->dense = 1;
            x->assign = 1;
            for (int j = 0; j < k; j++) {
                memset(a->span[0].set[j], 0, 32);
                unsigned m = 3 + rnd(3);
                for (unsigned q = 0; q < m; q++) set_add(a->span[0].set[j], ALPHA[rnd(NALPHA)]);
                a->span[0].table[j] = 0;
            }
        }
        /* the caseless sites state an item less often (with none, the plan
           can be the offset-skip function's predicate: B-fn) */
        if (c1_caseless ? rnd(4) == 0 : rnd(2) != 0) {  /* an item before span 0:
                                                            FAILS (core) or SATISFIES */
            int w = 1 + (int)rnd(2);
            rand_span(&a->span[a->nspan], -w, w, rnd(3) ? G2W_YES : G2W_NO, 1);
            gspan *it = &a->span[a->nspan++];
            it->core_lo = 0;
            it->core_len = rnd(2) ? w : 0;
        }
        if (c1_caseless ? rnd(4) == 0 : rnd(2) != 0) {  /* one after it */
            rand_span(&a->span[a->nspan], k, 1, rnd(3) ? G2W_YES : G2W_NO, 0);
            gspan *it = &a->span[a->nspan++];
            it->core_lo = 0;
            it->core_len = rnd(2);
            if (r2_two && rnd(2)) {     /* a lookahead's two bytes */
                memset(it->set[0], 0, 32);
                set_add(it->set[0], tw[0]);
                set_add(it->set[0], tw[2]);
                it->table[0] = 0;
            }
        }
        if (rnd(c1_caseless ? 6 : 3) == 0) x->wfloor = G2W_F_EXPR;
        break;
    }
    default: {
        x->nalt = rnd(4) ? 1 : 2;
        for (int ai = 0; ai < x->nalt; ai++) {
            galt *a = &x->alt[ai];
            a->entry = x->nalt == 2 ? (ai == 0 ? G2W_E_PARKED : G2W_E_RESEED)
                                    : (int)(1 + rnd(3));
            a->nspan = 1 + (int)rnd(4);
            for (int i = 0; i < a->nspan; i++)
                rand_span(&a->span[i], (int)rnd(14) - 5, 1 + (int)rnd(5),
                          rnd(2) ? G2W_YES : G2W_NO, 0);
        }
        if (rnd(3) == 0) x->wfloor = G2W_F_EXPR;
        break;
    }
    }
    for (int ai = 0; ai < x->nalt; ai++)
        for (int i = 0; i < x->alt[ai].nspan; i++)
            if (x->alt[ai].span[i].start < 0 && x->wfloor == G2W_F_UNSTATED)
                x->wfloor = G2W_F_SUBJECT;
}

/* 1 iff span `g` has the run R's shape: two or more positions, each one
 * member or a one-bit cube (G2's own reading, written from the F-8 ruling). */
static int g_run_shaped(const gspan *g)
{
    if (g->len < 2) return 0;
    for (int j = 0; j < g->len; j++) {
        int m[3], k = 0;
        for (int b = 0; b < 256 && k < 3; b++)
            if (g->set[j][b >> 3] >> (b & 7) & 1) m[k++] = b;
        if (!(k == 1 || (k == 2 && __builtin_popcount((unsigned)(m[0] ^ m[1])) == 1))) return 0;
    }
    return 1;
}

/* The run R is identified by its SHAPE and is UNIQUE per alternative (the
 * kit manager's F-8 ruling): 1 iff some alternative of `x` states two such
 * spans. fix: give every such span after an alternative's first a
 * three-member position 0, so the statement states one R. */
static int two_runs(gfacts *x, int fix)
{
    int any = 0;
    for (int ai = 0; ai < x->nalt; ai++) {
        int n = 0;
        for (int i = 0; i < x->alt[ai].nspan; i++) {
            gspan *g = &x->alt[ai].span[i];
            if (!g_run_shaped(g)) continue;
            if (n++ && fix) { set_add(g->set[0], 'b'); set_add(g->set[0], 'c'); set_add(g->set[0], 'x'); }
        }
        if (n > 1) any = 1;
    }
    return any;
}

/* ---- G2's facts as the kit's statement ------------------------------------------ */

static void to_kit(const gfacts *x, mf_site *s, mf_walt *alts, mf_wspan (*spans)[G2W_MAXSPAN])
{
    for (int ai = 0; ai < x->nalt; ai++) {
        const galt *a = &x->alt[ai];
        for (int i = 0; i < a->nspan; i++) {
            const gspan *g = &a->span[i];
            mf_wspan *w = &spans[ai][i];
            memset(w, 0, sizeof *w);
            w->start = g->start;
            w->len = (uint8_t)g->len;
            w->verify = g->verify == G2W_YES ? MF_VERIFY_YES : MF_VERIFY_NO;
            w->core = MF_CORE_STATED;
            w->core_lo = (uint8_t)g->core_lo;
            w->core_len = (uint8_t)g->core_len;
            if (!w->core_len) w->core_lo = 0;
            memcpy(w->set, g->set, sizeof g->set);
            memcpy(w->table_ref, g->table, sizeof g->table);
        }
        alts[ai].entry = a->entry == G2W_E_PARKED ? MF_ENTRY_PARKED
                       : a->entry == G2W_E_RESEED ? MF_ENTRY_RESEED : MF_ENTRY_NONE;
        alts[ai].nspan = (uint8_t)a->nspan;
        alts[ai].spans = spans[ai];
    }
    s->nalt = (uint8_t)x->nalt;
    s->alts = alts;
    s->wfloor = x->wfloor == G2W_F_EXPR ? MF_WFLOOR_EXPR
              : x->wfloor == G2W_F_SUBJECT ? MF_WFLOOR_SUBJECT : MF_WFLOOR_UNSTATED;
}

/* An alternative's empty range: its largest verify-YES core offset >= 0, -1. */
static int hy_of(const galt *a)
{
    int hy = -1;
    for (int i = 0; i < a->nspan; i++) {
        const gspan *g = &a->span[i];
        if (g->verify != G2W_YES) continue;
        for (int j = g->core_lo; j < g->core_lo + g->core_len; j++)
            if (g->start + j >= 0 && g->start + j > hy) hy = g->start + j;
    }
    return hy;
}

/* ---- the hooks ------------------------------------------------------------------- */

typedef struct { int id; char names[8][48]; int nn; } hctx;

static const char *h_fn_name(void *u, uint32_t ref)
{
    hctx *h = u;
    (void)ref;
    char *p = h->names[h->nn++ % 8];
    snprintf(p, 48, "g2w_f%d", h->id);
    return p;
}

static const char *h_table_name(void *u, uint32_t ref)
{
    hctx *h = u;
    char *p = h->names[h->nn++ % 8];
    snprintf(p, 48, "g2w_t%d_%u", h->id, ref);
    return p;
}

/* ---- main ------------------------------------------------------------------------ */

static long fails, refused_ok, rendered, asked_ok, two_run_refused;
/* D172 S3: E-find's reach by its text's parts (K35), and the REPORT sites
   E-find cannot render, each refused */
static long ef_n, ef_libc, ef_walk, ef_hors, ef_run, ef_below, ef_report, report_refused;
static long ef_pair, ef_fn;     /* Table B's PAIR: in the loop (B-pair), the function (B-fn) */
static long ef_hwin;            /* the stop's verify-YES core window wholly below the candidate */

static void fail(int id, const char *what, const char *detail)
{
    fails++;
    if (fails <= 30) printf("FAIL: site %d: %s: %s\n", id, what, detail ? detail : "");
}

/* ---- THE S3 CONTROLS (D172 S3; window_site.md §5.2's deny rows) ------------------ */

/* Renders a fixed window site of kind `kind` in frame `form`/`handoff` under
 * `opts`, the tie-heavy rate when `dense` (every alphabet byte 60,000 ppm);
 * span 0 is `k` positions of `members` each, verify YES, its core the first
 * `kc` (a non-core position is one no legacy row expresses). 0 and the form
 * id and text in *form / *text, or -1 (refused). */
static int ctl_render(int kind, int form, int handoff, const char *opts, int k, int kc,
                      const char *members, int dense, const char **form_id, buf *text)
{
    static mf_wspan sp;
    static mf_walt al;
    static uint32_t rate[256];
    memset(&sp, 0, sizeof sp);
    sp.start = 0;
    sp.len = (uint8_t)k;
    sp.verify = MF_VERIFY_YES;
    sp.core = MF_CORE_STATED;
    sp.core_lo = 0;
    sp.core_len = (uint8_t)kc;
    for (int j = 0; j < k; j++)
        for (const char *m = members; *m; m++) set_add(sp.set[j], (unsigned char)*m);
    memset(&al, 0, sizeof al);
    al.entry = MF_ENTRY_NONE;
    al.nspan = 1;
    al.spans = &sp;
    for (int b = 0; b < 256; b++) rate[b] = 50;
    for (unsigned i = 0; i < NALPHA; i++) rate[ALPHA[i]] = 60000;
    mf_akind kd;
    memset(&kd, 0, sizeof kd);
    kd.tag = "byte-rate";
    kd.version = 1;
    kd.present = MF_KIND_PRESENT;
    kd.prov.source = MF_PROV_MEASURED;
    kd.prov.bundle = "g2w";
    kd.prov.digest = 1;
    kd.payload = rate;
    mf_analysis an = { MF_ANALYSIS_LIST_V, 1, &kd };
    mf_site s;
    memset(&s, 0, sizeof s);
    s.abi = MF_SITE_ABI;
    s.form = (uint8_t)form;
    s.op = MF_OP_FIND;
    s.handoff = (uint8_t)handoff;
    s.empty = MF_EMPTY_MISS;
    s.use = MF_USE_POSITION;
    s.body = MF_BODY_ONESHOT;
    s.site_kind = (uint8_t)kind;
    s.span_hi = MF_SPAN_UNBOUNDED;
    s.policy = MF_P_PORTABLE_ONLY;
    s.opts = opts;
    s.ret_pred = MF_NO_PRED;
    s.pred.fn_ref = 1;
    s.nalt = 1;
    s.alts = &al;
    s.wfloor = MF_WFLOOR_SUBJECT;
    mf_art *art = mf_art_begin(&g_arena, "g2c", MF_P_PORTABLE_ONLY, 0, NULL, dense ? &an : NULL);
    hctx hc = { 9999, { { 0 } }, 0 };
    mf_hooks h;
    memset(&h, 0, sizeof h);
    h.s = "s"; h.n = "n"; h.lo = "lo"; h.result = "r"; h.miss = "((size_t)-1)";
    h.fn_name = h_fn_name; h.u = &hc;
    buf b2 = { 0 };
    mf_sink sb = mk_sink(text), sf = mk_sink(&b2);
    mf_result res;
    mf_class c;
    int rc = mf_emit(art, &s, &h, &sb, &sf, &res);
    mf_art *aq = mf_art_begin(&g_arena, "g2c", MF_P_PORTABLE_ONLY, 0, NULL, dense ? &an : NULL);
    int qc = mf_ask(aq, &s, &h, &c);
    if (b2.p) bputs(text, b2.p);
    free(b2.p);
    if (!rc != !qc) return -2;          /* the query and the define disagree */
    if (rc) return -1;
    static char fid[sizeof res.form_id];
    snprintf(fid, sizeof fid, "%s", res.form_id);
    *form_id = fid;
    return 0;
}

static void s3_controls(long *ok)
{
    const char *fid = "";
    buf t = { 0 };
    int rc = ctl_render(MF_SK_REPORT, MF_FORM_STMT, MF_H_ASSIGN, NULL, 4, 4, "a", 0, &fid, &t);
    if (rc || strcmp(fid, "window-search")) fail(-1, "control", "E-find does not render a REPORT site");
    else (*ok)++;
    free(t.p); t = (buf){ 0 };
    rc = ctl_render(MF_SK_REPORT, MF_FORM_STMT, MF_H_ASSIGN, "no-window-search", 4, 4, "a", 0, &fid, &t);
    if (rc != -1) fail(-1, "control", "no-window-search: a REPORT site rendered (or ask and define disagree)");
    else (*ok)++;
    free(t.p); t = (buf){ 0 };
    rc = ctl_render(MF_SK_REPORT, MF_FORM_FUNC, MF_H_RETURN, NULL, 4, 4, "a", 0, &fid, &t);
    if (rc != -1) fail(-1, "control", "a REPORT site in the FUNC frame rendered (the floor took it)");
    else (*ok)++;
    free(t.p); t = (buf){ 0 };
    rc = ctl_render(MF_SK_DFA_SCAN, MF_FORM_STMT, MF_H_ASSIGN, NULL, 3, 2, "ab0", 1, &fid, &t);
    if (rc || strcmp(fid, "window-search")) fail(-1, "control", "E-find does not render a DFA_SCAN site no legacy row serves");
    else (*ok)++;
    free(t.p); t = (buf){ 0 };
    rc = ctl_render(MF_SK_DFA_SCAN, MF_FORM_STMT, MF_H_ASSIGN, "no-window-search", 3, 2, "ab0", 1, &fid, &t);
    if (rc || strcmp(fid, "wf-floor")) fail(-1, "control", "no-window-search: a DFA_SCAN site not on the floor");
    else (*ok)++;
    free(t.p); t = (buf){ 0 };
    rc = ctl_render(MF_SK_REPORT, MF_FORM_STMT, MF_H_ASSIGN, NULL, 3, 3, "ab0", 1, &fid, &t);
    if (rc || !t.p || !strstr(t.p, "_sh[")) fail(-1, "control", "a dense window renders no D-hors table");
    else (*ok)++;
    free(t.p); t = (buf){ 0 };
    rc = ctl_render(MF_SK_REPORT, MF_FORM_STMT, MF_H_ASSIGN, "no-window-skip", 3, 3, "ab0", 1, &fid, &t);
    if (rc || !t.p || strstr(t.p, "_sh[")) fail(-1, "control", "no-window-skip: the D-hors table stays");
    else (*ok)++;
    free(t.p);
}

static void emit_set(buf *b, const uint8_t s[32])
{
    bputs(b, "{");
    for (int i = 0; i < 32; i++) bprintf(b, "%s%u", i ? "," : "", s[i]);
    bputs(b, "}");
}

int main(int argc, char **argv)
{
    if (argc != 4) { fprintf(stderr, "usage: g2_win_gen SEED NSITES OUTDIR\n"); return 2; }
    rng = strtoull(argv[1], NULL, 10) * 2654435761ull + 0x9E3779B97F4A7C15ull;
    int nsites = atoi(argv[2]);
    const char *s3n = getenv("G2W_S3_SITES");
    int n3 = s3n ? atoi(s3n) : 400;
    const char *c1n = getenv("G2W_C1_SITES");
    int n4 = c1n ? atoi(c1n) : 300;
    const char *r2n = getenv("G2W_R2_SITES");
    int n5 = r2n ? atoi(r2n) : 300;
    const char *h2n = getenv("G2W_H2_SITES");
    int n6 = h2n ? atoi(h2n) : 100;
    buf defs = { 0 }, table = { 0 }, data = { 0 };
    long famn[FAM_N] = { 0 }, frames[4] = { 0 };

    /* THE CONTROL (S2 commit 6: the family is every art's): a window site on
       an art that previews nothing is decided, and a site stating only spans
       renders there */
    {
        gfacts x;
        gen_facts(FAM_PARKED, &x);
        mf_site s;
        memset(&s, 0, sizeof s);
        mf_walt alts[2];
        static mf_wspan spans[2][G2W_MAXSPAN];
        to_kit(&x, &s, alts, spans);
        s.abi = MF_SITE_ABI;
        s.form = MF_FORM_STMT; s.op = MF_OP_FIND; s.handoff = MF_H_ASSIGN;
        s.empty = MF_EMPTY_MISS; s.body = MF_BODY_ONESHOT;
        mf_art *art = mf_art_begin(&g_arena, "g2w", MF_P_PORTABLE_ONLY, 0, NULL, NULL);
        mf_wreply r;
        if (mf_wdecide(art, &s, &r)) fail(-1, "control", "mf_wdecide refused on a plain art");
        else refused_ok++;
        buf b1 = { 0 }, b2 = { 0 };
        mf_sink sb = mk_sink(&b1), sf = mk_sink(&b2);
        mf_hooks h;
        memset(&h, 0, sizeof h);
        h.s = "s"; h.n = "n"; h.lo = "lo"; h.result = "r"; h.miss = "((size_t)-1)";
        mf_result res;
        if (mf_emit(art, &s, &h, &sb, &sf, &res))
            fail(-1, "control", mf_art_error(art));
        else refused_ok++;
        if (strcmp(res.form_id, "") == 0) fail(-1, "control", "a spans-only site named no form");
        else refused_ok++;
        s3_controls(&refused_ok);
    }

    bputs(&defs, "#include <stddef.h>\n#include <stdint.h>\n#include <string.h>\n"
                 "#include \"g2_win.h\"\n#define G2W_UNWRITTEN ((size_t)-2)\n\n");
    for (int id = 0; id < nsites + n3 + n4 + n5 + n6; id++) {
        if (id == nsites) {             /* D172 S3's dense sites: their own stream */
            rngp = &rng3;
            s3_dense = 1;
        }
        if (id == nsites + n3) {        /* the caseless sites: theirs */
            rngp = &rng4;
            s3_dense = 0;
            c1_caseless = 1;
        }
        if (id == nsites + n3 + n4) {   /* the two-byte sites: theirs */
            rngp = &rng5;
            c1_caseless = 0;
            r2_two = 1;
        }
        if (id == nsites + n3 + n4 + n5) {  /* the below-window sites: theirs */
            rngp = &rng6;
            r2_two = 0;
            h2_below = 1;
        }
        int fam = s3_dense || c1_caseless || r2_two || h2_below ? FAM_REPORT
                : id < FAM_N * 4 ? id % FAM_N : (int)rnd(FAM_N);
        gfacts gf;
        gen_facts(fam, &gf);
        famn[fam]++;
        /* TWO SPANS OF R'S SHAPE in one alternative are REFUSED (F-8 ruling;
           wf_check): count it on a preview art, then state one R */
        if (two_runs(&gf, 0)) {
            mf_site t;
            memset(&t, 0, sizeof t);
            mf_walt talts[2];
            static mf_wspan tspans[2][G2W_MAXSPAN];
            to_kit(&gf, &t, talts, tspans);
            t.abi = MF_SITE_ABI;
            t.op = MF_OP_FIND;
            mf_art *ar = mf_art_begin(&g_arena, "g2w", MF_P_PORTABLE_ONLY, 0, NULL, NULL);
            mf_wreply tr;
            if (!mf_wdecide(ar, &t, &tr))
                fail(id, "two runs", "an alternative stating two spans of R's shape was decided");
            else { refused_ok++; two_run_refused++; }
            two_runs(&gf, 1);
        }
        /* every offer its own id within the site (one table per id) */
        for (int ai = 0, k = 0; ai < gf.nalt; ai++)
            for (int i = 0; i < gf.alt[ai].nspan; i++)
                for (int j = 0; j < gf.alt[ai].span[i].len; j++)
                    if (gf.alt[ai].span[i].table[j]) gf.alt[ai].span[i].table[j] = (uint32_t)++k;
        g2w_site x;
        memset(&x, 0, sizeof x);
        static g2w_span views[2][G2W_MAXSPAN];
        view(&gf, &x, views);
        static uint32_t rate[256];
        /* the rate: NONE, skewed, or tie-heavy (every alphabet byte equal) */
        x.rate_kind = (int)rnd(3);
        if (gf.dense) x.rate_kind = 2;
        if (x.rate_kind == 1) {
            for (int b = 0; b < 256; b++) rate[b] = 1 + rnd(40);
            for (unsigned i = 0; i < NALPHA; i++) rate[ALPHA[i]] = 1000 + rnd(120000);
        } else if (x.rate_kind == 2) {
            for (int b = 0; b < 256; b++) rate[b] = 50;
            for (unsigned i = 0; i < NALPHA; i++) rate[ALPHA[i]] = 60000;
        }
        x.rate = x.rate_kind ? rate : NULL;
        mf_akind kind;
        memset(&kind, 0, sizeof kind);
        kind.tag = "byte-rate";
        kind.version = 1;
        kind.present = MF_KIND_PRESENT;
        kind.prov.source = MF_PROV_MEASURED;
        kind.prov.bundle = "g2w";
        kind.prov.digest = 1;
        kind.payload = rate;
        mf_analysis an = { MF_ANALYSIS_LIST_V, 1, &kind };

        mf_site s;
        memset(&s, 0, sizeof s);
        mf_walt alts[2];
        static mf_wspan spans[2][G2W_MAXSPAN];
        to_kit(&gf, &s, alts, spans);
        s.abi = MF_SITE_ABI;
        s.op = MF_OP_FIND;
        s.body = MF_BODY_ONESHOT;
        static const uint8_t kinds[] = { MF_SK_DFA_SCAN, MF_SK_DFA_HAT, MF_SK_HYB_PF,
                                         MF_SK_VM_ATTEMPT, MF_SK_DFA_ATTEMPT, MF_SK_REPORT };
        s.site_kind = fam == FAM_MLINE ? MF_SK_DFA_ATTEMPT : kinds[rnd(fam == FAM_REPORT ? 6 : 5)];
        s.span_hi = MF_SPAN_UNBOUNDED;
        s.policy = MF_P_PORTABLE_ONLY;
        s.pred.fn_ref = 1;

        char pfx[24];
        snprintf(pfx, sizeof pfx, "g2w%d", id);
        mf_art *art = mf_art_begin(&g_arena, pfx, MF_P_PORTABLE_ONLY, 0, NULL,
                                   x.rate_kind ? &an : NULL);
        mf_wreply r;
        if (mf_wdecide(art, &s, &r)) { fail(id, "mf_wdecide refused", NULL); continue; }
        /* the reply, field by field */
        x.reply.alt = r.alt; x.reply.reseed = r.reseed; x.reply.has_stop = r.has_stop;
        x.reply.stop = r.stop; memcpy(x.reply.stop_set, r.stop_set, 32);
        x.reply.nplan = r.nplan;
        for (int i = 0; i < r.nplan; i++) { x.reply.plan[i] = r.plan[i]; x.reply.plan_term[i] = r.plan_term[i]; }
        x.reply.pinned = r.pinned; x.reply.run_stated = r.run_stated;
        x.reply.run_member = r.run_member; x.reply.run_lo = r.run_lo; x.reply.run_len = r.run_len;
        memcpy(x.reply.path, r.path, sizeof x.reply.path);

        /* the frame; a miss of n only where every hit lies below n (a tested
           core position at an offset >= 0, by G2's own decision) */
        g2w_dec ref;
        g2w_decide(&x, x.rate, &ref);
        int below_n = 0, below_n1 = 0;    /* every hit < n; every hit < n - 1 */
        for (int k = 0; k < ref.ntest; k++) {
            if (ref.tcore[k] && ref.toff[k] >= 0) below_n = 1;
            if (ref.tcore[k] && ref.toff[k] >= 1) below_n1 = 1;
        }
        int fr = fam == FAM_MLINE ? G2W_FR_ASSIGN : (int)rnd(4);
        if (fr == G2W_FR_ASSIGN_LO && !below_n) fr = G2W_FR_ASSIGN;
        x.frame = fr;
        frames[fr]++;
        x.miss_n = fr == G2W_FR_ASSIGN_LO ? 1 : below_n ? (int)rnd(2) : 0;
        if (below_n1 && fr != G2W_FR_FUNC && rnd(2)) x.miss_n = 2;   /* a bounded end */
        int onm = (int)rnd(3);          /* 0 none, 1 braced, 2 goto (leaves) */
        if (fr == G2W_FR_ONMISS && onm == 0) onm = 1;
        if (fam == FAM_MLINE) onm = 2;
        x.empty = fr == G2W_FR_FUNC ? G2W_EMPTY_MISS
                : fam == FAM_MLINE ? G2W_EMPTY_AT_N : (int)rnd(4);
        if (fr == G2W_FR_ASSIGN_LO) {
            /* pf_walk refuses AT USE a NOP site stating an on_miss its
               applicability admits (pffind.c pf_walk_use; reported, wsc1
               finding F-4): the in-place frame states none under NOP */
            if (onm == 1) onm = 0;
            x.empty = onm == 2 ? G2W_EMPTY_MISS : G2W_EMPTY_NOP;
        }
        s.form = fr == G2W_FR_FUNC ? MF_FORM_FUNC : MF_FORM_STMT;
        s.handoff = fr == G2W_FR_FUNC ? MF_H_RETURN : fr == G2W_FR_ONMISS ? MF_H_ON_MISS
                                                                           : MF_H_ASSIGN;
        s.empty = x.empty == G2W_EMPTY_MISS ? MF_EMPTY_MISS : x.empty == G2W_EMPTY_NOP
                ? MF_EMPTY_NOP : x.empty == G2W_EMPTY_EXCLUDED ? MF_EMPTY_EXCLUDED : MF_EMPTY_AT_N;
        s.on_miss_leaves = fr != G2W_FR_FUNC && onm == 2;
        s.use = MF_USE_POSITION;
        /* D172 S3: a dense window is a REPORT site in an ASSIGN frame, the
           shape D-hors renders (E-find; the legacy rows serve a whole-core
           window of any other kind) */
        if (gf.assign) {
            s.site_kind = MF_SK_REPORT;
            frames[fr]--;
            fr = rnd(2) && below_n ? G2W_FR_ASSIGN_LO : G2W_FR_ASSIGN;
            frames[fr]++;
            x.frame = fr;
            x.miss_n = fr == G2W_FR_ASSIGN_LO ? 1 : below_n ? (int)rnd(2) : 0;
            onm = (int)rnd(3);
            x.empty = (int)rnd(4);
            if (fr == G2W_FR_ASSIGN_LO) {
                if (onm == 1) onm = 0;
                x.empty = onm == 2 ? G2W_EMPTY_MISS : G2W_EMPTY_NOP;
            }
            s.form = MF_FORM_STMT;
            s.handoff = MF_H_ASSIGN;
            s.empty = x.empty == G2W_EMPTY_MISS ? MF_EMPTY_MISS : x.empty == G2W_EMPTY_NOP
                    ? MF_EMPTY_NOP : x.empty == G2W_EMPTY_EXCLUDED ? MF_EMPTY_EXCLUDED : MF_EMPTY_AT_N;
            s.on_miss_leaves = onm == 2;
        }

        /* NOP over two alternatives whose empty ranges differ is REFUSED
           (wf_check): count it, then render the site under MISS */
        if (x.nalt == 2 && x.empty == G2W_EMPTY_NOP && hy_of(&gf.alt[0]) != hy_of(&gf.alt[1])) {
            mf_site t = s;
            mf_hooks th;
            memset(&th, 0, sizeof th);
            th.s = "s"; th.n = "n"; th.lo = "lo"; th.result = "r"; th.miss = "((size_t)-1)";
            buf b1 = { 0 }, b2 = { 0 };
            mf_sink s1 = mk_sink(&b1), s2 = mk_sink(&b2);
            mf_art *ar = mf_art_begin(&g_arena, "g2w", MF_P_PORTABLE_ONLY, 0, NULL, NULL);
            mf_result rr;
            if (!mf_emit(ar, &t, &th, &s1, &s2, &rr) || !strstr(mf_art_error(ar), "NOP"))
                fail(id, "NOP refusal", "two alternatives disagreeing on the empty range rendered");
            else refused_ok++;
            x.empty = G2W_EMPTY_MISS;
            s.empty = MF_EMPTY_MISS;
        }
        /* D172 S3: a REPORT site E-find cannot render (a frame other than
           STMT/ASSIGN, or no stop by G2's OWN decision) is REFUSED, the floor
           serving no REPORT site; it is then rendered as a DFA_SCAN site */
        if (s.site_kind == MF_SK_REPORT &&
            !((fr == G2W_FR_ASSIGN || fr == G2W_FR_ASSIGN_LO) && ref.has_stop)) {
            mf_hooks th;
            memset(&th, 0, sizeof th);
            th.s = "s"; th.n = "n"; th.lo = "lo"; th.result = "r"; th.miss = "((size_t)-1)";
            th.on_miss = fr == G2W_FR_ONMISS ? "{ }" : NULL;
            hctx th_c = { id, { { 0 } }, 0 };
            th.fn_name = h_fn_name; th.table_name = h_table_name; th.u = &th_c;
            buf b1 = { 0 }, b2 = { 0 };
            mf_sink s1 = mk_sink(&b1), s2 = mk_sink(&b2);
            mf_art *ar = mf_art_begin(&g_arena, "g2w", MF_P_PORTABLE_ONLY, 0, NULL,
                                      x.rate_kind ? &an : NULL);
            mf_result rr;
            if (!mf_emit(ar, &s, &th, &s1, &s2, &rr))
                fail(id, "REPORT refusal", "a REPORT site E-find cannot render was rendered");
            else report_refused++;
            free(b1.p);
            free(b2.p);
            s.site_kind = MF_SK_DFA_SCAN;
        }
        hctx hc = { id, { { 0 } }, 0 };
        char miss_lbl[48], onmiss[96], fname[48];
        snprintf(miss_lbl, sizeof miss_lbl, "g2w_m%d", id);
        if (onm == 2) snprintf(onmiss, sizeof onmiss, "goto %s;", miss_lbl);
        else snprintf(onmiss, sizeof onmiss, "{ *missed = 1; }");
        snprintf(fname, sizeof fname, "g2w_f%d", id);
        mf_hooks h;
        memset(&h, 0, sizeof h);
        h.s = "s";
        h.n = "n";
        h.lo = "lo";
        h.floor = x.wfloor == G2W_F_EXPR ? (x.floor_is_lo ? "lo" : "fl") : NULL;
        h.result = fr == G2W_FR_ASSIGN_LO ? "lo" : "r";
        h.miss = x.miss_n == 1 ? MF_MISS_N : x.miss_n == 2 ? "n - 1" : "((size_t)-1)";
        h.on_miss = fr == G2W_FR_FUNC || (onm == 0) ? NULL : onmiss;
        h.indent = "    ";
        h.fn_name = h_fn_name;
        h.table_name = h_table_name;
        h.u = &hc;

        buf body = { 0 }, file = { 0 };
        mf_sink sb = mk_sink(&body), sf = mk_sink(&file);
        mf_result res;
        memset(&res, 0, sizeof res);
        if (mf_emit(art, &s, &h, &sb, &sf, &res) || mf_art_end(art, NULL)) {
            fail(id, "render refused", mf_art_error(art));
            continue;
        }
        mf_class asked;
        mf_result def;
        rendered++;
        if (!strcmp(res.form_id, "window-search")) {
            const char *t = body.p ? body.p : "";
            const char *ft = file.p ? file.p : "";
            ef_n++;
            ef_libc += strstr(t, "memchr(") != NULL;
            ef_hors += strstr(ft, "_sh[256]") != NULL;
            ef_walk += strstr(t, "while (") != NULL;
            ef_run += strstr(t, "memcmp(") || strstr(t, "_w2(") || strstr(t, "_w4(") ||
                      strstr(t, "_w8(") || strstr(t, " & 0x") || strstr(t, ") & ");
            ef_below += ref.has_stop && ref.stop < 0;
            ef_report += s.site_kind == MF_SK_REPORT;
            ef_pair += strstr(t, "_ha < ") != NULL;
            ef_fn += strstr(ft, "_ofsskip__body(") != NULL;
            /* B-fn renders the FIND slot's pick, PAIR: the function's BODY is
               fn-pair's two streams (window.c b_fn_holds) */
            if (strstr(ft, "_ofsskip__body(") && !strstr(ft, "ha < pos"))
                fail(id, "B-fn", "the offset-skip function renders one stream under PAIR");
        }
        /* D-hors's scope (window_site.md §2.5): its window, the stop's
           verify-YES core span of two positions or more, reaches the candidate
           (whi >= 0). G2's own reading of the facts, not the kit's: every site
           whose window lies wholly below is counted, and none may render a skip
           table */
        {
            int hi = 0, found = 0;
            const galt *ca = &gf.alt[ref.alt];
            for (int i = 0; ref.has_stop && i < ca->nspan && !found; i++) {
                const gspan *g = &ca->span[i];
                int lo0 = g->start + g->core_lo;
                if (g->verify != G2W_YES || g->core_len < 2) continue;
                if (ref.stop < lo0 || ref.stop >= lo0 + g->core_len) continue;
                found = 1;
                hi = lo0 + g->core_len - 1;
            }
            if (found && hi < 0) {
                ef_hwin++;
                if (file.p && strstr(file.p, "_sh[256]"))
                    fail(id, "D-hors scope", "a skip table over a window wholly below the candidate");
            }
        }
        x.pair = strstr(body.p ? body.p : "", "_ha < ") || strstr(file.p ? file.p : "", "ha < pos");
        /* the define-time query agrees with a define over the SAME phases
           (§4.5 rule 2: mf_ask answers mf_define's selection, MF_PH_DEFINE;
           mf_emit's also reads the use hooks, so it may choose otherwise) */
        memset(&def, 0, sizeof def);
        if (mf_defined(art, res.handle, &def)) fail(id, "mf_defined", mf_art_error(art));
        {
            mf_art *aq = mf_art_begin(&g_arena, pfx, MF_P_PORTABLE_ONLY, 0, NULL,
                                      x.rate_kind ? &an : NULL);
            mf_art *ad = mf_art_begin(&g_arena, pfx, MF_P_PORTABLE_ONLY, 0, NULL,
                                      x.rate_kind ? &an : NULL);
            buf b3 = { 0 };
            mf_sink s3 = mk_sink(&b3);
            uint32_t hd;
            mf_result dd;
            if (mf_define(ad, &s, &h, &s3, &hd) || mf_defined(ad, hd, &dd)) {
                fail(id, "mf_define", mf_art_error(ad));
            } else if (mf_ask(aq, &s, &h, &asked) || memcmp(&asked, &dd.cls, sizeof asked)) {
                fail(id, "mf_ask", "the query's class differs from the define's");
            } else {
                asked_ok++;
            }
            free(b3.p);
        }

        /* the tables pcrec would emit for every offer the text reads */
        for (int ai = 0; ai < x.nalt; ai++)
            for (int i = 0; i < x.alt[ai].nspan; i++)
                for (int j = 0; j < x.alt[ai].span[i].len; j++) {
                    uint32_t t = x.alt[ai].span[i].table[j];
                    if (!t) continue;
                    char nm[48];
                    snprintf(nm, sizeof nm, "g2w_t%d_%u[", id, t);
                    if (!strstr(body.p ? body.p : "", nm) && !strstr(file.p ? file.p : "", nm))
                        continue;
                    nm[strlen(nm) - 1] = 0;
                    bprintf(&defs, "static const unsigned char %s[256] = {", nm);
                    for (int b = 0; b < 256; b++)
                        bprintf(&defs, "%s%d", b ? "," : "",
                                x.alt[ai].span[i].set[j][b >> 3] >> (b & 7) & 1);
                    bputs(&defs, "};\n");
                }
        if (file.p) bputs(&defs, file.p);
        bprintf(&defs, "static size_t g2w_call%d(const unsigned char *s, size_t n, size_t lo, "
                       "size_t fl, int *wrote, int *missed)\n{\n    (void)fl; (void)s; (void)n;\n"
                       "    *missed = 0;\n", id);
        switch (fr) {
        case G2W_FR_FUNC:
            bprintf(&defs, "    *wrote = 1;\n    return %s;\n}\n", body.p ? body.p : "0");
            break;
        case G2W_FR_ASSIGN:
            bprintf(&defs, "    size_t r = G2W_UNWRITTEN;\n%s    *wrote = r != G2W_UNWRITTEN;\n"
                           "    return r;\n", body.p ? body.p : "");
            if (onm == 2)
                bprintf(&defs, "%s:\n    *missed = 1;\n    *wrote = r != G2W_UNWRITTEN;\n"
                               "    return r;\n", miss_lbl);
            bputs(&defs, "}\n");
            break;
        case G2W_FR_ASSIGN_LO:
            bprintf(&defs, "    *wrote = 1;\n%s    return lo;\n", body.p ? body.p : "");
            if (onm == 2) bprintf(&defs, "%s:\n    *missed = 1;\n    return lo;\n", miss_lbl);
            bputs(&defs, "}\n");
            break;
        default:
            bprintf(&defs, "    *wrote = 0;\n%s    return 0;\n", body.p ? body.p : "");
            if (onm == 2) bprintf(&defs, "%s:\n    *missed = 1;\n    return 0;\n", miss_lbl);
            bputs(&defs, "}\n");
            break;
        }
        bputs(&defs, "\n");
        (void)fname;

        /* the site table's row: the facts AS GENERATED (each span's sets and
           offers, each alternative's spans, as their own arrays), the frame,
           the rate and the reply */
        for (int ai = 0; ai < gf.nalt; ai++) {
            const galt *a = &gf.alt[ai];
            for (int i = 0; i < a->nspan; i++) {
                const gspan *g = &a->span[i];
                bprintf(&defs, "static const uint8_t g2w_s%d_%d_%d[][32] = {", id, ai, i);
                for (int j = 0; j < g->len; j++) { if (j) bputs(&defs, ","); emit_set(&defs, g->set[j]); }
                bprintf(&defs, "};\nstatic const uint32_t g2w_o%d_%d_%d[] = {", id, ai, i);
                for (int j = 0; j < g->len; j++) bprintf(&defs, "%s%u", j ? "," : "", g->table[j]);
                bputs(&defs, "};\n");
            }
            bprintf(&defs, "static const g2w_span g2w_p%d_%d[] = {\n", id, ai);
            for (int i = 0; i < a->nspan; i++) {
                const gspan *g = &a->span[i];
                bprintf(&defs, "    { %d, %d, %d, %d, %d, g2w_s%d_%d_%d, g2w_o%d_%d_%d },\n",
                        g->start, g->len, g->verify, g->core_len ? g->core_lo : 0, g->core_len,
                        id, ai, i, id, ai, i);
            }
            bputs(&defs, "};\n");
        }
        bprintf(&defs, "static const uint8_t g2w_pv%d[%d][32] = {", id, G2W_NPROOF);
        for (int k = 0; k < G2W_NPROOF; k++) { if (k) bputs(&defs, ","); emit_set(&defs, def.cls.proven[k]); }
        bputs(&defs, "};\n");
        if (x.rate_kind) {
            bprintf(&defs, "static const uint32_t g2w_r%d[256] = {", id);
            for (int b = 0; b < 256; b++) bprintf(&defs, "%s%u", b ? "," : "", rate[b]);
            bputs(&defs, "};\n");
        }
        bprintf(&data, "    { \"%s#%d\", %d, {", fam_name[fam], id, x.nalt);
        for (int ai = 0; ai < x.nalt; ai++)
            bprintf(&data, "%s{ %d, %d, g2w_p%d_%d }", ai ? "," : "", x.alt[ai].entry,
                    x.alt[ai].nspan, id, ai);
        bprintf(&data, "}, %d, %d, %d, %d, %d, %d, %d, ", x.wfloor, x.floor_is_lo, x.frame,
                x.empty, x.miss_n, fr == G2W_FR_FUNC ? 0 : onm, x.rate_kind);
        if (x.rate_kind) bprintf(&data, "g2w_r%d", id);
        else bputs(&data, "NULL");
        bprintf(&data, ", { %d, %d, %d, %d, ", r.alt, r.reseed, r.has_stop, r.stop);
        emit_set(&data, r.stop_set);
        bprintf(&data, ", %d, {", r.nplan);
        for (int i = 0; i < r.nplan; i++) bprintf(&data, "%s%d", i ? "," : "", r.plan[i]);
        if (!r.nplan) bputs(&data, "0");
        bputs(&data, "}, {");
        for (int i = 0; i < r.nplan; i++) bprintf(&data, "%s%d", i ? "," : "", r.plan_term[i]);
        if (!r.nplan) bputs(&data, "0");
        bprintf(&data, "}, %d, %d, %d, %d, %d, \"%s\" }, g2w_pv%d, \"%s\", \"%s\", %d },\n",
                r.pinned, r.run_stated, r.run_member, r.run_lo, r.run_len, r.path, id,
                res.form_id, res.row, x.pair);
        bprintf(&table, "    g2w_call%d,\n", id);
        free(body.p);
        free(file.p);
    }
    char path[4096];
    snprintf(path, sizeof path, "%s/g2w_sites.c", argv[3]);
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); return 2; }
    fputs(defs.p, f);
    fprintf(f, "const g2w_site g2w_sites[] = {\n%s};\n", data.p ? data.p : "");
    fprintf(f, "const g2w_fn g2w_fns[] = {\n%s};\n", table.p ? table.p : "");
    fprintf(f, "const unsigned g2w_nsites = %ld;\n", rendered);
    fclose(f);
    printf("g2_win_gen: %ld sites rendered of %d (S3 dense %d, caseless %d, two-byte %d, "
           "below-window %d); families:", rendered, nsites + n3 + n4 + n5 + n6, n3, n4, n5, n6);
    for (int i = 0; i < FAM_N; i++) printf(" %s=%ld", fam_name[i], famn[i]);
    printf("; frames: func=%ld assign=%ld assign_lo=%ld onmiss=%ld; controls refused %ld; "
           "queries agreeing %ld; two runs refused %ld\n", frames[0], frames[1], frames[2],
           frames[3], refused_ok, asked_ok, two_run_refused);
    printf("g2_win_gen: e-find %ld: libc %ld walk %ld hors %ld run %ld below %ld report %ld "
           "pair %ld fn %ld hwin %ld; report refused %ld\n", ef_n, ef_libc, ef_walk, ef_hors, ef_run,
           ef_below, ef_report, ef_pair, ef_fn, ef_hwin, report_refused);
    printf("g2_win_gen failures: %ld\n", fails);
    return fails ? 1 : 0;
}
