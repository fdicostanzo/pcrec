/* memfn twins T-B: FUSED scan+verify against today's emitted run gate.
 *
 * Question ([MEMFN] R1d, D77): on the K82 caseless-run cells, does one
 * vector loop that both FINDS and VERIFIES a masked run beat what pcrec
 * emits today (two libc memchr streams, then a masked word compare per
 * candidate, k82diag_report.md §1) and a memchr2-style single pass plus a
 * separate verify?
 *
 * The function every variant computes is the emitted gate's, exactly:
 *   gate(s, n, pos) = the first c >= pos with c + L <= n and
 *                     (s[c+j] & m[j]) == v[j] for every j < L, else n
 * Cells (pcrec main 8a41efd2's own emitted rx_reqrun, `-p rx`):
 *   us  union-select  (?i)union.*?select.*?from   run SELECT, scan @4 C/c
 *   up  userpass      (?:username|USERNAME|user|USER)...  run USER, scan @0 U/u
 *   mi  mod-i         (?i)cat                     run CAT, scan @0 C/c
 * every m[j] = 0xDF (letters), v = the upper-case run.
 *
 * Variants:
 *   emit     today's rx_reqrun, VERBATIM from the emitted artifact (two
 *            memchr streams, each re-searched only when passed, both fresh
 *            on every call; overlapping rx_w2/rx_w4 masked compares)
 *   m2v      one inline pass for the scan byte's two cases (vec.h FIND_BODY
 *            with an eq2 classifier at the scan offset), then the same
 *            masked compare; restart one past a failed candidate
 *   ffl      FUSED, first/last filter: per block, the scan offset's masked
 *            compare AND a second offset's (the run's last byte, or its
 *            first when the scan offset is last), candidates verified by
 *            the masked word compare from the mask bits, never re-scanned;
 *            2×VW unrolled
 *   fall     FUSED, all bytes: the AND of all L offsets' masked compares;
 *            a set bit IS the answer (no verify); 2×VW unrolled
 * Spans shorter than VW + L - 1 take a byte loop in m2v/ffl/fall.
 *
 * Regimes (ns, min of REPEATS loops >= 50 ms, spread in %):
 *   gate    one call from pos 0: what rx_search pays per search call
 *   sweep   call, restart at the hit + 1, to the end: every candidate the
 *           gate would hand on (k82cost T3's handoff use, and the find-all
 *           regime the cause-B cells live in)
 *   short   one gate call per capability short subject (75, 1..512 B),
 *           ns per subject: the short-call term (k82diag §2)
 *
 * Correctness (--check): every variant's whole sweep against the reference
 * over n 0..200, alignments 0..31, a planted run at every position, on a
 * near-miss alphabet (the run's letters in both cases, partial runs); guard
 * pages at both ends; random fuzz. ASan+UBSan build for exact-end reads.
 */
#include "vec.h"

/* ---- the emitted gates, verbatim (main 8a41efd2, -p rx) ------------------ */

static inline uint32_t rx_w4(const void *p) { uint32_t w; memcpy(&w, p, 4); return w; }
static inline uint16_t rx_w2(const void *p) { uint16_t w; memcpy(&w, p, 2); return w; }

static inline size_t emit_us(const unsigned char *subject, size_t n, size_t pos)
{
    size_t ha = 0, hb = 0;
    int fresh = 1;
    while (pos + 5 < n) {
        size_t cand;
        if (fresh || ha < pos + 4) {
            const void *q = memchr(subject + pos + 4, 67, n - pos - 4);
            ha = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        if (fresh || hb < pos + 4) {
            const void *q = memchr(subject + pos + 4, 99, n - pos - 4);
            hb = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        fresh = 0;
        cand = ha < hb ? ha : hb;
        if (cand >= n) return n;
        cand -= 4;
        if (cand + 5 >= n) return n;
        if ((rx_w4(subject + cand) & rx_w4("\337\337\337\337")) == rx_w4("SELE") && (rx_w4(subject + cand + 2) & rx_w4("\337\337\337\337")) == rx_w4("LECT")) return cand;
        pos = cand + 1;
    }
    return n;
}

static inline size_t emit_up(const unsigned char *subject, size_t n, size_t pos)
{
    size_t ha = 0, hb = 0;
    int fresh = 1;
    while (pos + 3 < n) {
        size_t cand;
        if (fresh || ha < pos) {
            const void *q = memchr(subject + pos, 85, n - pos);
            ha = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        if (fresh || hb < pos) {
            const void *q = memchr(subject + pos, 117, n - pos);
            hb = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        fresh = 0;
        cand = ha < hb ? ha : hb;
        if (cand >= n) return n;
        if (cand + 3 >= n) return n;
        if ((rx_w4(subject + cand) & rx_w4("\337\337\337\337")) == rx_w4("USER")) return cand;
        pos = cand + 1;
    }
    return n;
}

static inline size_t emit_mi(const unsigned char *subject, size_t n, size_t pos)
{
    size_t ha = 0, hb = 0;
    int fresh = 1;
    while (pos + 2 < n) {
        size_t cand;
        if (fresh || ha < pos) {
            const void *q = memchr(subject + pos, 67, n - pos);
            ha = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        if (fresh || hb < pos) {
            const void *q = memchr(subject + pos, 99, n - pos);
            hb = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        fresh = 0;
        cand = ha < hb ? ha : hb;
        if (cand >= n) return n;
        if (cand + 2 >= n) return n;
        if ((rx_w2(subject + cand) & rx_w2("\337\337")) == rx_w2("CA") && (rx_w2(subject + cand + 1) & rx_w2("\337\337")) == rx_w2("AT")) return cand;
        pos = cand + 1;
    }
    return n;
}

/* ---- the run, as compile-time constants ---------------------------------
 * RUN(L, V, KA, KB): length, upper-case run, scan offset, second offset. */
#define RUN_us 6, "SELECT", 4, 5
#define RUN_up 4, "USER", 0, 3
#define RUN_mi 3, "CAT", 0, 2

/* masked compare of the whole run at p (all masks 0xDF): one or two
 * overlapping words, the emitted compare's own spelling */
INL int run_eq(const uint8_t *p, int L, const char *V)
{
    if (L >= 4) {
        uint32_t m = 0xDFDFDFDFu, a, b;
        memcpy(&a, V, 4);
        memcpy(&b, V + L - 4, 4);
        return (rx_w4(p) & m) == a && (rx_w4(p + L - 4) & m) == b;
    }
    uint16_t m = 0xDFDF, a, b;
    memcpy(&a, V, 2);
    memcpy(&b, V + L - 2, 2);
    return (rx_w2(p) & m) == a && (rx_w2(p + L - 2) & m) == b;
}

INL size_t byte_loop(const uint8_t *s, size_t n, size_t pos, int L, const char *V, int KA)
{
    for (size_t c = pos; c + (size_t)L <= n; c++)
        if ((s[c + KA] & 0xDF) == (uint8_t)V[KA] && run_eq(s + c, L, V)) return c;
    return n;
}

/* m2v: one inline two-case pass for the scan byte, then verify */
INL size_t f_eq2(const uint8_t *s, size_t n, uint8_t up, uint8_t lo)
{
    const vu8 A = vdup(up), B = vdup(lo);
#define CLS(v) vor(veq((v), A), veq((v), B))
#define PRED(c) ((c) == up || (c) == lo)
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
INL size_t f_m2v(const uint8_t *s, size_t n, size_t pos, int L, const char *V, int KA, int KB)
{
    (void)KB;
    const uint8_t up = (uint8_t)V[KA], lo = (uint8_t)(V[KA] | 0x20);
    while (pos + (size_t)L <= n) {
        size_t qn = n - pos - (size_t)KA;
        size_t f = f_eq2(s + pos + KA, qn, up, lo);
        if (f >= qn) return n;
        size_t c = pos + f;
        if (c + (size_t)L > n) return n;
        if (run_eq(s + c, L, V)) return c;
        pos = c + 1;
    }
    return n;
}

/* fused: candidates from masked compares at offsets in the vector loop */
INL size_t f_fused(const uint8_t *s, size_t n, size_t pos, int L, const char *V,
                   int KA, int KB, int ALL)
{
    const vu8 M = vdup(0xDF);
    const vu8 VA = vdup((uint8_t)V[KA]), VB = vdup((uint8_t)V[KB]);
    vu8 VV[8];
    for (int j = 0; j < L; j++) VV[j] = vdup((uint8_t)V[j]);
#define CMASK(p)                                                              \
    ({  vu8 r_;                                                               \
        if (ALL) {                                                            \
            r_ = veq(vand(vload((p)), M), VV[0]);                             \
            for (int j_ = 1; j_ < L; j_++)                                    \
                r_ = vand(r_, veq(vand(vload((p) + j_), M), VV[j_]));         \
        } else                                                                \
            r_ = vand(veq(vand(vload((p) + KA), M), VA),                      \
                      veq(vand(vload((p) + KB), M), VB));                     \
        vmask(r_) & VMASK_ONE; })
#define TRY(mk, base)                                                         \
    do {                                                                      \
        uint64_t mm_ = (mk);                                                  \
        while (mm_) {                                                         \
            size_t c_ = (base) + vfirst(mm_);                                 \
            if (ALL || run_eq(s + c_, L, V)) return c_;                       \
            mm_ &= mm_ - 1;                                                   \
        }                                                                     \
    } while (0)
    const size_t T = (size_t)L - 1; /* the loads reach VW + L - 1 past i */
    if (n < pos + VW + T) return byte_loop(s, n, pos, L, V, KA);
    size_t i = pos;
    for (; i + 2 * VW + T <= n; i += 2 * VW) {
        uint64_t m0 = CMASK(s + i), m1 = CMASK(s + i + VW);
        if (m0 | m1) {
            TRY(m0, i);
            TRY(m1, i + VW);
        }
    }
    for (; i + VW + T <= n; i += VW)
        TRY(CMASK(s + i), i);
    if (i + L <= n) { /* one final block ending at n; lanes before i are done */
        size_t f = n - T - VW;
        TRY(CMASK(s + f) & lane_from(i - f), f);
    }
    return n;
#undef CMASK
#undef TRY
}

/* ---- variant table --------------------------------------------------------- */

#define GEN(C)                                                                         \
    INL size_t k_##C##_emit(const uint8_t *s, size_t n, size_t p) { return emit_##C(s, n, p); } \
    INL size_t k_##C##_m2v(const uint8_t *s, size_t n, size_t p) { return f_m2v(s, n, p, RUN_##C); } \
    INL size_t k_##C##_ffl(const uint8_t *s, size_t n, size_t p) { return f_fused(s, n, p, RUN_##C, 0); } \
    INL size_t k_##C##_fall(const uint8_t *s, size_t n, size_t p) { return f_fused(s, n, p, RUN_##C, 1); }
GEN(us) GEN(up) GEN(mi)

#define KERNELS(X) \
    X(us, emit) X(us, m2v) X(us, ffl) X(us, fall) \
    X(up, emit) X(up, m2v) X(up, ffl) X(up, fall) \
    X(mi, emit) X(mi, m2v) X(mi, ffl) X(mi, fall)

struct tctx { const uint8_t *s; size_t n; const uint8_t *const *ss; const size_t *sn; int ns; long hits; };

/* regime bodies, one per kernel: gate (one call), sweep (to the end),
 * short (one call per short subject) */
#define TIMER(C, V)                                                           \
    OOL static double tg_##C##_##V(const void *ctx, long reps)                \
    {                                                                         \
        struct tctx *c = (struct tctx *)ctx;                                  \
        size_t acc = 0;                                                       \
        double t0 = now_ns();                                                 \
        for (long r = 0; r < reps; r++) {                                     \
            const uint8_t *s = c->s;                                          \
            __asm__ volatile("" : "+r"(s));                                   \
            acc += k_##C##_##V(s, c->n, 0);                                   \
        }                                                                     \
        __asm__ volatile("" : : "r"(acc));                                    \
        c->hits = (long)(acc / (size_t)reps);                                 \
        return now_ns() - t0;                                                 \
    }                                                                         \
    OOL static double ts_##C##_##V(const void *ctx, long reps)                \
    {                                                                         \
        struct tctx *c = (struct tctx *)ctx;                                  \
        long tot = 0;                                                         \
        double t0 = now_ns();                                                 \
        for (long r = 0; r < reps; r++) {                                     \
            const uint8_t *s = c->s;                                          \
            __asm__ volatile("" : "+r"(s));                                   \
            size_t n = c->n, p = 0;                                           \
            for (;;) {                                                        \
                size_t h = k_##C##_##V(s, n, p);                              \
                if (h >= n) break;                                            \
                tot++;                                                        \
                p = h + 1;                                                    \
            }                                                                 \
        }                                                                     \
        __asm__ volatile("" : : "r"(tot));                                    \
        c->hits = tot / reps;                                                 \
        return now_ns() - t0;                                                 \
    }                                                                         \
    OOL static double th_##C##_##V(const void *ctx, long reps)                \
    {                                                                         \
        struct tctx *c = (struct tctx *)ctx;                                  \
        long tot = 0;                                                         \
        double t0 = now_ns();                                                 \
        for (long r = 0; r < reps; r++)                                       \
            for (int k = 0; k < c->ns; k++) {                                 \
                const uint8_t *s = c->ss[k];                                  \
                __asm__ volatile("" : "+r"(s));                               \
                tot += k_##C##_##V(s, c->sn[k], 0) < c->sn[k];                \
            }                                                                 \
        __asm__ volatile("" : : "r"(tot));                                    \
        c->hits = tot / reps;                                                 \
        return now_ns() - t0;                                                 \
    }
KERNELS(TIMER)

struct kern {
    const char *cell, *var;
    size_t (*fn)(const uint8_t *, size_t, size_t);
    tbody tg, ts, th;
    int L;
    const char *V;
};
#define ROW(C, V) { #C, #V, k_##C##_##V, tg_##C##_##V, ts_##C##_##V, th_##C##_##V, 0, NULL },
static struct kern kerns[] = { KERNELS(ROW) };
#define NK (int)(sizeof kerns / sizeof kerns[0])

static void kern_init(void)
{
    for (int x = 0; x < NK; x++) {
        const char *c = kerns[x].cell;
        kerns[x].V = !strcmp(c, "us") ? "SELECT" : !strcmp(c, "up") ? "USER" : "CAT";
        kerns[x].L = (int)strlen(kerns[x].V);
    }
}

/* ---- correctness ------------------------------------------------------------ */

static size_t ref(const uint8_t *s, size_t n, size_t pos, int L, const char *V)
{
    for (size_t c = pos; c + (size_t)L <= n; c++) {
        int j = 0;
        while (j < L && (s[c + j] & 0xDF) == (uint8_t)V[j]) j++;
        if (j == L) return c;
    }
    return n;
}

static long g_bad, g_cases;
static void sweep_check(const struct kern *k, const uint8_t *s, size_t n, size_t pos0,
                        const char *what, size_t a, size_t b)
{
    size_t p = pos0;
    for (;;) {
        size_t want = ref(s, n, p, k->L, k->V), got = k->fn(s, n, p);
        g_cases++;
        if (got != want) {
            if (g_bad++ < 20)
                printf("BAD %s/%s %s n=%zu a=%zu b=%zu pos=%zu got=%zu want=%zu\n",
                       k->cell, k->var, what, n, a, b, p, got, want);
            return;
        }
        if (want >= n) return;
        p = want + 1;
    }
}
OOL static void sweep_guarded(const struct kern *k, const uint8_t *s, size_t n,
                              const char *what, size_t a, size_t b)
{
    if (sigsetjmp(g_jb, 1) == 0)
        sweep_check(k, s, n, 0, what, a, b);
    else if (g_bad++ < 20)
        printf("FAULT %s/%s %s n=%zu a=%zu b=%zu\n", k->cell, k->var, what, n, a, b);
}

/* a near-miss byte: the run's letters in either case, a byte that masks onto
 * a letter only by its 0x20 bit, or noise */
static uint8_t nearmiss(const struct kern *k, uint64_t r)
{
    switch (r & 7) {
    case 0: case 1: case 2: return (uint8_t)(k->V[(r >> 3) % (unsigned)k->L] | ((r >> 8) & 1 ? 0x20 : 0));
    case 3: return (uint8_t)((r >> 3) & 0xFF);
    case 4: return (uint8_t)(k->V[(r >> 3) % (unsigned)k->L] ^ 0x80);
    default: return (uint8_t)('a' + (r >> 3) % 26);
    }
}
static void plant(const struct kern *k, uint8_t *s, uint64_t r)
{
    for (int j = 0; j < k->L; j++) s[j] = (uint8_t)(k->V[j] | ((r >> j) & 1 ? 0x20 : 0));
}

static int check(void)
{
    const size_t NMAX = 200;
    for (int x = 0; x < NK; x++) {
        const struct kern *k = &kerns[x];
        rng_state = 0x9E3779B97F4A7C15ull + (uint64_t)x;
        for (size_t n = 0; n <= NMAX; n++)
            for (size_t al = 0; al < 32; al++) {
                uint8_t *blk = malloc(al + n + 1), *s = blk + al;
                for (size_t h = 0; h <= n; h++) {
                    for (size_t i = 0; i < n; i++) s[i] = nearmiss(k, rng());
                    if (h + (size_t)k->L <= n) plant(k, s + h, rng());
                    sweep_check(k, s, n, 0, "pos", al, h);
                    if (h & 1) sweep_check(k, s, n, h / 2, "pos0", al, h);
                }
                free(blk);
            }
        for (size_t n = 0; n <= NMAX; n++)
            for (int side = 0; side < 2; side++)
                for (size_t off = 0; off < (side ? 32u : 1u); off++) {
                    uint8_t *s = side ? gstart(off) : gend(n);
                    for (size_t i = 0; i < n; i++) s[i] = nearmiss(k, rng());
                    if (n >= (size_t)k->L) plant(k, s + n - (size_t)k->L, rng());
                    sweep_guarded(k, s, n, side ? "gstart" : "gend", off, 0);
                }
        for (int t = 0; t < 4000; t++) {
            size_t n = (size_t)(rng() % 600);
            uint8_t *s = malloc(n + 1);
            for (size_t i = 0; i < n; i++) s[i] = nearmiss(k, rng());
            for (int q = (int)(rng() % 6); q > 0; q--)
                if (n >= (size_t)k->L) plant(k, s + rng() % (n - (size_t)k->L + 1), rng());
            sweep_check(k, s, n, 0, "fuzz", (size_t)t, 0);
            free(s);
        }
    }
    printf("check (" VISA "): %d kernels, %ld calls, %ld bad, %ld faults\n", NK, g_cases,
           g_bad, (long)g_faults);
    return g_bad != 0;
}

/* ---- timing ----------------------------------------------------------------- */

int main(int argc, char **argv)
{
    kern_init();
    guard_init(4096);
    const char *dir = NULL;
    for (int a = 1; a < argc; a++) {
        if (!strcmp(argv[a], "--check")) return check();
        if (!strncmp(argv[a], "--subjects=", 11)) dir = argv[a] + 11;
        if (!strcmp(argv[a], "--quick")) g_min_loop_ns = 5e6;
    }
    if (!dir) { fprintf(stderr, "usage: tb_run --check | --subjects=DIR [--quick]\n"); return 2; }
    char path[4096];
    /* the short subjects: <u32 len><bytes>... */
    snprintf(path, sizeof path, "%s/cap-short.bin", dir);
    size_t sl;
    uint8_t *sb = slurp(path, &sl);
    const uint8_t *ss[256];
    size_t sn[256];
    int ns = 0;
    for (size_t o = 0; o + 4 <= sl && ns < 256;) {
        uint32_t len;
        memcpy(&len, sb + o, 4);
        uint8_t *cp = malloc(len + 1); /* each in its own allocation, exact */
        memcpy(cp, sb + o + 4, len);
        ss[ns] = cp, sn[ns++] = len;
        o += 4 + len;
    }
    printf("# memfn twins T-B (fused scan+verify vs the emitted run gate), vec=%s VW=%d\n", VISA, VW);
    printf("# ns: min of %d loops >= %.0f ms, (+spread%%); short = ns per subject over %d\n",
           REPEATS, g_min_loop_ns / 1e6, ns);
    static const char *const cells[3] = { "us", "up", "mi" };
    static const char *const subj[3][2] = { { "cap-t-64k", "cap-t-1m" },
                                            { "cap-t-64k", "cap-t-1m" },
                                            { "syn-t-64k", "syn-t-1m" } };
    for (int ci = 0; ci < 3; ci++) {
        printf("\n## cell %s\n%-6s gate:%-19s gate:%-19s sweep:%-18s sweep:%-18s %s\n",
               cells[ci], "var", subj[ci][0], subj[ci][1], subj[ci][0], subj[ci][1], "short");
        uint8_t *tb[2];
        size_t tn[2];
        for (int q = 0; q < 2; q++) {
            snprintf(path, sizeof path, "%s/%s.bin", dir, subj[ci][q]);
            tb[q] = slurp(path, &tn[q]);
        }
        for (int x = 0; x < NK; x++) {
            if (strcmp(kerns[x].cell, cells[ci])) continue;
            printf("%-6s", kerns[x].var);
            double lo, hi;
            for (int q = 0; q < 2; q++) {
                struct tctx c = { tb[q], tn[q], NULL, NULL, 0, 0 };
                tmeasure(kerns[x].tg, &c, &lo, &hi);
                printf(" %11.1f(+%2.0f)@%-7ld", lo, 100 * (hi / lo - 1), c.hits);
            }
            for (int q = 0; q < 2; q++) {
                struct tctx c = { tb[q], tn[q], NULL, NULL, 0, 0 };
                tmeasure(kerns[x].ts, &c, &lo, &hi);
                printf(" %11.0f(+%2.0f)#%-6ld", lo, 100 * (hi / lo - 1), c.hits);
            }
            struct tctx c = { NULL, 0, ss, sn, ns, 0 };
            tmeasure(kerns[x].th, &c, &lo, &hi);
            printf(" %8.2f(+%2.0f)#%ld\n", lo / ns, 100 * (hi / lo - 1), c.hits);
            fflush(stdout);
        }
    }
    printf("\n# gate: ns per call from 0, @ = returned position (n = absent)\n"
           "# sweep: ns per sweep to the end, # = gate hits\n"
           "# short: ns per short subject, # = subjects whose gate passed\n");
    return 0;
}
