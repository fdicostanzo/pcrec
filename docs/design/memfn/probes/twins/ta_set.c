/* memfn twins T-A: a SET CLASSIFIER PER SHAPE against the GENERIC one.
 *
 * Question ([MEMFN] R1d, D77): for a find-first-in-set (requirements.md F4)
 * over a real corpus/bench byte class, does a classifier TAILORED to the
 * class's shape beat the fixed generic kernel, and by how much, by span and
 * hit density? Every row below is "find the first i with s[i] in SET" in
 * the same skeleton (vec.h FIND_BODY); only the classifier differs:
 *
 *   scalar   a byte loop over a 256-entry membership table (today's
 *            pf_emit_bcls shape: one load per byte)
 *   nib2     the GENERIC kernel: the two-table nibble lookup (shufti):
 *            lo[c & 15] & hi[c >> 4] != 0, tables read from a descriptor.
 *            Exact for any set whose high-nibble rows take <= 8 distinct
 *            low-nibble patterns (every set below). Needs a byte shuffle:
 *            NEON tbl, SSSE3/AVX2 pshufb; absent on an SSE2-only build
 *   shape    the classifier the set's SHAPE admits (the set's own row says
 *            which): eq2/eq3 (OR of compares), range ((c - lo) <= span,
 *            unsigned), cube (((c - lo) & care) == 0, cls_tree_study.md §4.3;
 *            {S,s} in its absolute form (c & 0xDF) == 'S'),
 *            nib1 (<= 16 members, low nibbles unique: T[c & 15] == c, one
 *            shuffle), rangesor (\w as three range/eq tests)
 *   libc     (eq2/eq3 only) one memchr per member, min of the hits
 *
 * Sets (members exact; provenance in the set table): ["'] the userpass
 * bench cell's quote class; \h (bc024); [0-9]; {S,s} (bc011) and {A,B,a,b}
 * (bc019), the cube shapes; \s (bc016) and [\d-] (bc012), nibble-unique;
 * \w (bc000), the general case.
 *
 * Timed: a FIND-ALL over a span of n bytes (call, count, restart one past
 * the hit) so hit density is in the number: none (no member: one call reads
 * the span), sparse (one member per 1009 B), dense (one per 13 B), real (the
 * syntax sub-bench's t-64k text, its own density per set). ns per find-all,
 * min of REPEATS loops each >= 50 ms (D144 addendum 1), spread in %.
 *
 * Correctness (--check): every kernel against an independent reference (a
 * table built from the member list, never from a classifier) over n
 * 0..300, alignments 0..31, every hit position and none, each member byte;
 * every one of the 256 byte values planted alone; guard pages at both span
 * ends; a random fuzz of whole find-all sequences. Build with ASan+UBSan for
 * the exact-allocation over-read check (probes.mk twins-check-asan).
 */
#include "vec.h"

/* ---- sets --------------------------------------------------------------- */

struct set {
    const char *id, *shape, *src;
    const char *members; /* exact bytes */
    int k;
    uint8_t mem[256];          /* reference membership */
    uint8_t lo[16], hi[16];    /* nib2 */
    int nib2ok;
};

enum { S_Q2, S_H3, S_D, S_SS, S_AB, S_SP, S_DM, S_W, NSET };
static struct set sets[NSET] = {
    { "q2", "eq2", "[\"'] userpass bench cell", "\"'", 0, {0}, {0}, {0}, 0 },
    { "h3", "eq3", "\\h corpus bc024", "\t \xA0", 0, {0}, {0}, {0}, 0 },
    { "d", "range", "[0-9]", "0123456789", 0, {0}, {0}, {0}, 0 },
    { "ss", "cube1", "{S,s} corpus bc011", "Ss", 0, {0}, {0}, {0}, 0 },
    { "ab", "cube2", "{A,B,a,b} corpus bc019", "ABab", 0, {0}, {0}, {0}, 0 },
    { "sp", "nib1", "\\s corpus bc016 (6, nibble-unique)", "\t\n\v\f\r ", 0, {0}, {0}, {0}, 0 },
    { "dm", "nib1", "[\\d-] corpus bc012 (11, nibble-unique)", "-0123456789", 0, {0}, {0}, {0}, 0 },
    { "w", "rangesor", "\\w corpus bc000 (63)",
      "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz", 0, {0}, {0}, {0}, 0 },
};

static void sets_init(void)
{
    for (int x = 0; x < NSET; x++) {
        struct set *d = &sets[x];
        d->k = (int)strlen(d->members);
        for (int j = 0; j < d->k; j++)
            d->mem[(uint8_t)d->members[j]] = 1;
        /* shufti: one bucket per distinct non-empty high-nibble row */
        uint16_t row[16] = {0}, bucket[8];
        int nb = 0;
        for (int c = 0; c < 256; c++)
            if (d->mem[c]) row[c >> 4] |= (uint16_t)(1u << (c & 15));
        d->nib2ok = 1;
        for (int h = 0; h < 16; h++) {
            if (!row[h]) continue;
            int b = 0;
            while (b < nb && bucket[b] != row[h]) b++;
            if (b == nb) {
                if (nb == 8) { d->nib2ok = 0; break; }
                bucket[nb++] = row[h];
            }
            d->hi[h] = (uint8_t)(1u << b);
            for (int l = 0; l < 16; l++)
                if (row[h] >> l & 1) d->lo[l] |= (uint8_t)(1u << b);
        }
        if (!d->nib2ok) { fprintf(stderr, "set %s: nib2 needs > 8 buckets\n", d->id); exit(2); }
    }
}

/* ---- generic kernels (descriptor at run time) --------------------------- */

INL size_t f_scalar(const uint8_t *s, size_t n, const struct set *d)
{
    const uint8_t *m = d->mem;
    for (size_t i = 0; i < n; i++)
        if (m[s[i]]) return i;
    return n;
}

#if VHAVE_TBL
INL size_t f_nib2(const uint8_t *s, size_t n, const struct set *d)
{
    const vu8 LO = vtab(d->lo), HI = vtab(d->hi), F = vdup(0x0F);
    const uint8_t *lo = d->lo, *hi = d->hi;
#define CLS(v) vnz(vand(vtbl(LO, vand((v), F)), vtbl(HI, vshr4(v))))
#define PRED(c) (lo[(c) & 15] & hi[(c) >> 4])
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
#endif

/* ---- shape kernels (constants in the code) ------------------------------ */

INL size_t k_q2_shape(const uint8_t *s, size_t n)
{
    const vu8 A = vdup('"'), B = vdup('\'');
#define CLS(v) vor(veq((v), A), veq((v), B))
#define PRED(c) ((c) == '"' || (c) == '\'')
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
INL size_t k_h3_shape(const uint8_t *s, size_t n)
{
    const vu8 A = vdup('\t'), B = vdup(' '), C = vdup(0xA0);
#define CLS(v) vor(vor(veq((v), A), veq((v), B)), veq((v), C))
#define PRED(c) ((c) == '\t' || (c) == ' ' || (c) == 0xA0)
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
INL size_t k_d_shape(const uint8_t *s, size_t n)
{
    const vu8 LO = vdup('0'), SP = vdup(9);
#define CLS(v) vle(vsub((v), LO), SP)
#define PRED(c) ((uint8_t)((c) - '0') <= 9)
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
INL size_t k_ss_shape(const uint8_t *s, size_t n)
{
    const vu8 CARE = vdup(0xDF), VAL = vdup('S');
#define CLS(v) veq(vand((v), CARE), VAL)
#define PRED(c) (((c) & 0xDF) == 'S')
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
/* {A,B,a,b} is a cube over x = c - 'A' (members x = 0, 1, 0x20, 0x21: free
 * bits 0x21), cls_tree_study.md §4.3's cube_of form. Not an absolute cube:
 * 'A' ^ 'B' = 0x03, so the offset is load-bearing (the check caught the
 * absolute spelling). */
INL size_t k_ab_shape(const uint8_t *s, size_t n)
{
    const vu8 LO = vdup('A'), CARE = vdup(0xDE), Z = vdup(0);
#define CLS(v) veq(vand(vsub((v), LO), CARE), Z)
#define PRED(c) ((((c) - 'A') & 0xDE) == 0)
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
#if VHAVE_TBL
/* nib1: T[l] = the member whose low nibble is l, else a byte whose low
 * nibble is not l (so it never equals the subject byte) */
INL size_t k_sp_shape(const uint8_t *s, size_t n)
{
    static const uint8_t T[16] = { ' ', 0x00, 0x03, 0x02, 0x05, 0x04, 0x07, 0x06,
                                   0x09, '\t', '\n', '\v', '\f', '\r', 0x0F, 0x0E };
    const vu8 TV = vtab(T), F = vdup(0x0F);
#define CLS(v) veq(vtbl(TV, vand((v), F)), (v))
#define PRED(c) (T[(c) & 15] == (c))
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
INL size_t k_dm_shape(const uint8_t *s, size_t n)
{
    static const uint8_t T[16] = { '0', '1', '2', '3', '4', '5', '6', '7',
                                   '8', '9', 0x0B, 0x0A, 0x0D, '-', 0x0F, 0x0E };
    const vu8 TV = vtab(T), F = vdup(0x0F);
#define CLS(v) veq(vtbl(TV, vand((v), F)), (v))
#define PRED(c) (T[(c) & 15] == (c))
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
#endif
INL size_t k_w_shape(const uint8_t *s, size_t n)
{
    const vu8 B20 = vdup(0x20), LA = vdup('a'), S25 = vdup(25), D0 = vdup('0'),
              S9 = vdup(9), US = vdup('_');
#define CLS(v) vor(vor(vle(vsub(vor((v), B20), LA), S25), vle(vsub((v), D0), S9)), veq((v), US))
#define PRED(c) ((uint8_t)(((c) | 0x20) - 'a') <= 25 || (uint8_t)((c) - '0') <= 9 || (c) == '_')
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}

#define IDX(p, s, n) ((p) ? (size_t)((const uint8_t *)(p) - (s)) : (n))
INL size_t k_q2_libc(const uint8_t *s, size_t n)
{
    size_t a = IDX(memchr(s, '"', n), s, n), b = IDX(memchr(s, '\'', n), s, n);
    return a < b ? a : b;
}
INL size_t k_h3_libc(const uint8_t *s, size_t n)
{
    size_t a = IDX(memchr(s, '\t', n), s, n), b = IDX(memchr(s, ' ', n), s, n),
           c = IDX(memchr(s, 0xA0, n), s, n);
    a = a < b ? a : b;
    return a < c ? a : c;
}

/* ---- the kernel table --------------------------------------------------- */

#define GEN_SCALAR(S, I) INL size_t k_##S##_scalar(const uint8_t *s, size_t n) { return f_scalar(s, n, &sets[I]); }
#define GEN_NIB2(S, I) INL size_t k_##S##_nib2(const uint8_t *s, size_t n) { return f_nib2(s, n, &sets[I]); }
GEN_SCALAR(q2, S_Q2) GEN_SCALAR(h3, S_H3) GEN_SCALAR(d, S_D) GEN_SCALAR(ss, S_SS)
GEN_SCALAR(ab, S_AB) GEN_SCALAR(sp, S_SP) GEN_SCALAR(dm, S_DM) GEN_SCALAR(w, S_W)
#if VHAVE_TBL
GEN_NIB2(q2, S_Q2) GEN_NIB2(h3, S_H3) GEN_NIB2(d, S_D) GEN_NIB2(ss, S_SS)
GEN_NIB2(ab, S_AB) GEN_NIB2(sp, S_SP) GEN_NIB2(dm, S_DM) GEN_NIB2(w, S_W)
#define TBLX(X, S, I) X(S, nib2, I)
#else
#define TBLX(X, S, I)
#endif
#if VHAVE_TBL
#define NIB1X(X, S, I) X(S, shape, I)
#else
#define NIB1X(X, S, I)
#endif

/* X(set, variant, set index): every (set, variant) the build has */
#define KERNELS(X)                                                            \
    X(q2, scalar, S_Q2) TBLX(X, q2, S_Q2) X(q2, shape, S_Q2) X(q2, libc, S_Q2) \
    X(h3, scalar, S_H3) TBLX(X, h3, S_H3) X(h3, shape, S_H3) X(h3, libc, S_H3) \
    X(d, scalar, S_D) TBLX(X, d, S_D) X(d, shape, S_D)                         \
    X(ss, scalar, S_SS) TBLX(X, ss, S_SS) X(ss, shape, S_SS)                   \
    X(ab, scalar, S_AB) TBLX(X, ab, S_AB) X(ab, shape, S_AB)                   \
    X(sp, scalar, S_SP) TBLX(X, sp, S_SP) NIB1X(X, sp, S_SP)                   \
    X(dm, scalar, S_DM) TBLX(X, dm, S_DM) NIB1X(X, dm, S_DM)                   \
    X(w, scalar, S_W) TBLX(X, w, S_W) X(w, shape, S_W)

struct tctx { const uint8_t *s; size_t n; long hits; };

/* one noinline find-all body per kernel: the kernel is inlined into it */
#define TIMER(S, V, I)                                                        \
    OOL static double t_##S##_##V(const void *ctx, long reps)                 \
    {                                                                         \
        struct tctx *c = (struct tctx *)ctx;                                  \
        long tot = 0;                                                         \
        double t0 = now_ns();                                                 \
        for (long r = 0; r < reps; r++) {                                     \
            const uint8_t *s = c->s;                                          \
            __asm__ volatile("" : "+r"(s));                                   \
            size_t n = c->n, i = 0;                                           \
            for (;;) {                                                        \
                size_t j = k_##S##_##V(s + i, n - i);                         \
                if (j >= n - i) break;                                        \
                tot++;                                                        \
                i += j + 1;                                                   \
            }                                                                 \
        }                                                                     \
        __asm__ volatile("" : : "r"(tot));                                    \
        c->hits = tot / reps;                                                 \
        return now_ns() - t0;                                                 \
    }
KERNELS(TIMER)

struct kern { const char *set, *var; int si; size_t (*fn)(const uint8_t *, size_t); tbody tm; };
#define ROW(S, V, I) { #S, #V, I, k_##S##_##V, t_##S##_##V },
static const struct kern kerns[] = { KERNELS(ROW) };
#define NK (int)(sizeof kerns / sizeof kerns[0])

/* ---- correctness -------------------------------------------------------- */

static size_t ref(const struct set *d, const uint8_t *s, size_t n)
{
    for (size_t i = 0; i < n; i++)
        if (d->mem[s[i]]) return i;
    return n;
}

/* a non-member filler byte for position i (varied, printable where possible) */
static uint8_t filler(const struct set *d, size_t i)
{
    uint8_t c = (uint8_t)(0x21 + (i * 7) % 94);
    while (d->mem[c]) c = (uint8_t)(c + 1 > 0x7E ? 0x21 : c + 1);
    return c;
}

static long g_bad, g_cases;
static void expect(const struct kern *k, const uint8_t *s, size_t n, size_t want,
                   const char *what, size_t a, size_t b)
{
    g_cases++;
    size_t got = k->fn(s, n);
    if (got != want && g_bad++ < 20)
        printf("BAD %s/%s %s n=%zu a=%zu b=%zu got=%zu want=%zu\n",
               k->set, k->var, what, n, a, b, got, want);
}

/* expect() behind a fault catcher, in its own frame so nothing in the
 * caller lives across the siglongjmp */
OOL static void expect_guarded(const struct kern *k, const uint8_t *s, size_t n,
                               size_t want, const char *what, size_t a, size_t b)
{
    if (sigsetjmp(g_jb, 1) == 0)
        expect(k, s, n, want, what, a, b);
    else if (g_bad++ < 20)
        printf("FAULT %s/%s %s n=%zu a=%zu b=%zu\n", k->set, k->var, what, n, a, b);
}

static int check(void)
{
    const size_t NMAX = 300;
    for (int x = 0; x < NK; x++) {
        const struct kern *k = &kerns[x];
        const struct set *d = &sets[k->si];
        /* (1) exact-allocation spans: every n, alignment, hit position */
        for (size_t n = 0; n <= NMAX; n++)
            for (size_t al = 0; al < 32; al++) {
                uint8_t *blk = malloc(al + n + 1), *s = blk + al;
                for (size_t i = 0; i < n; i++) s[i] = filler(d, i + al);
                for (size_t h = 0; h <= n; h++) {
                    if (h < n) s[h] = (uint8_t)d->members[(h + al) % d->k];
                    expect(k, s, n, h, "pos", al, h);
                    if (h < n) s[h] = filler(d, h + al);
                }
                free(blk);
            }
        /* (2) every byte value alone, at three positions */
        static const size_t ns[] = { 1, 15, 16, 17, 31, 33, 64, 65, 100, 129, 300 };
        for (size_t z = 0; z < sizeof ns / sizeof ns[0]; z++) {
            size_t n = ns[z];
            uint8_t *s = malloc(n);
            for (int b = 0; b < 256; b++) {
                size_t ps[3] = { 0, n / 2, n - 1 };
                for (int q = 0; q < 3; q++) {
                    for (size_t i = 0; i < n; i++) s[i] = filler(d, i);
                    s[ps[q]] = (uint8_t)b;
                    expect(k, s, n, d->mem[b] ? ps[q] : n, "byte", (size_t)b, ps[q]);
                }
            }
            free(s);
        }
        /* (3) guard pages: flush against the end, and just after the start */
        for (size_t n = 0; n <= NMAX; n++) {
            for (int side = 0; side < 2; side++)
                for (size_t off = 0; off < (side ? 32u : 1u); off++) {
                    uint8_t *s = side ? gstart(off) : gend(n);
                    for (size_t i = 0; i < n; i++) s[i] = filler(d, i);
                    for (size_t h = 0; h <= n; h += (n > 64 ? 7 : 1)) {
                        if (h < n) s[h] = (uint8_t)d->members[h % d->k];
                        expect_guarded(k, s, n, h, side ? "gstart" : "gend", off, h);
                        if (h < n) s[h] = filler(d, h);
                    }
                }
        }
        /* (4) fuzz: whole find-all sequences over random bytes */
        for (int t = 0; t < 3000; t++) {
            size_t n = (size_t)(rng() % 400);
            uint8_t *s = malloc(n + 1);
            int dens = (int)(rng() % 4);
            for (size_t i = 0; i < n; i++) {
                uint64_t r = rng();
                s[i] = (r & 3) < (uint64_t)dens ? (uint8_t)(r >> 8)
                                                : ((r >> 2 & 15) == 0 ? (uint8_t)d->members[(r >> 16) % d->k]
                                                                      : filler(d, i));
            }
            size_t i = 0;
            while (i <= n) {
                size_t w = ref(d, s + i, n - i);
                expect(k, s + i, n - i, w, "fuzz", (size_t)t, i);
                if (w >= n - i) break;
                i += w + 1;
            }
            free(s);
        }
    }
    printf("check (" VISA "): %d kernels, %ld cases, %ld bad, %ld faults\n", NK, g_cases,
           g_bad, (long)g_faults);
    return g_bad != 0;
}

/* ---- timing ------------------------------------------------------------- */

static const size_t spans[] = { 16, 64, 256, 1024, 4096, 16384, 65536 };
#define NSPAN (sizeof spans / sizeof spans[0])
enum { D_NONE, D_SPARSE, D_DENSE, D_REAL, ND };
static const char *const dname[ND] = { "none", "sparse", "dense", "real" };

int main(int argc, char **argv)
{
    sets_init();
    guard_init(4096);
    const char *only = NULL, *real = NULL;
    for (int a = 1; a < argc; a++) {
        if (!strcmp(argv[a], "--check")) return check();
        if (!strncmp(argv[a], "--set=", 6)) only = argv[a] + 6;
        if (!strncmp(argv[a], "--real=", 7)) real = argv[a] + 7;
        if (!strcmp(argv[a], "--quick")) g_min_loop_ns = 5e6;
    }
    size_t rn = 0;
    uint8_t *rtext = real ? slurp(real, &rn) : NULL;
    if (rtext && rn < 65536) { fprintf(stderr, "--real text under 64 KiB\n"); return 2; }
    uint8_t *buf = aligned_alloc(64, 65536);
    printf("# memfn twins T-A (set classifier per shape vs generic), vec=%s VW=%d\n", VISA, VW);
    printf("# ns per FIND-ALL over the span: min of %d loops >= %.0f ms, (+spread%%)\n",
           REPEATS, g_min_loop_ns / 1e6);
    printf("# real = %s\n", real ? real : "(not given: row skipped)");
    for (int x = 0; x < NSET; x++) {
        const struct set *d = &sets[x];
        if (only && strcmp(only, d->id)) continue;
        printf("\n## set %s  shape=%s  k=%d  (%s)\n", d->id, d->shape, d->k, d->src);
        for (int dn = 0; dn < ND; dn++) {
            if (dn == D_REAL && !rtext) continue;
            for (size_t i = 0; i < 65536; i++) {
                if (dn == D_REAL) buf[i] = rtext[i];
                else {
                    buf[i] = filler(d, i);
                    size_t per = dn == D_SPARSE ? 1009 : 13;
                    if (dn != D_NONE && i % per == per - 1)
                        buf[i] = (uint8_t)d->members[(i / per) % d->k];
                }
            }
            printf("%-7s %-7s", dname[dn], "members");
            for (size_t j = 0; j < NSPAN; j++) {
                long h = 0;
                for (size_t i = 0; i < spans[j]; i++) h += d->mem[buf[i]];
                printf(" %14ld", h);
            }
            printf("\n");
            for (int q = 0; q < NK; q++) {
                if (kerns[q].si != x) continue;
                printf("%-7s %-7s", dname[dn], kerns[q].var);
                for (size_t j = 0; j < NSPAN; j++) {
                    struct tctx c = { buf, spans[j], 0 };
                    double lo, hi;
                    tmeasure(kerns[q].tm, &c, &lo, &hi);
                    printf(" %9.2f(+%2.0f)", lo, 100 * (hi / lo - 1));
                    fflush(stdout);
                }
                printf("\n");
            }
        }
    }
    return 0;
}
