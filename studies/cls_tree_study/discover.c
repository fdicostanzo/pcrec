/* discover.c — the sectioning DP, in C, at compiler speed.
 *
 * TWO JOBS, and it is worth being explicit that they are different:
 *
 *  (1) DELIVERABLE (3), the compile-time bound.  `section.py` answers what
 *      the sectioning rule IS; it cannot answer what discovery COSTS a
 *      compiler, because a Python DP's wall time is not a compiler's.  This
 *      file is the same algorithm at the speed the real thing would run, and
 *      its `--time` mode is the number CONSTITUTIONAL CONSTRAINT 2's
 *      pre-analysis cache is gated on (D77: build the cache only if discovery
 *      MEASURES as costly).
 *
 *  (2) AN INDEPENDENT IMPLEMENTATION.  It was written from the cost model,
 *      not translated line by line from the Python, and `--dump` prints the
 *      chosen sectioning so the two can be compared over the whole
 *      population.  Two implementations agreeing on 324 sets is a much better
 *      control than one implementation checked against itself — and the
 *      disagreement it DID find is in the memo.
 *
 * Input: a file of `lo hi` hex interval lines (see clsets.py --dump-iv).
 * Usage: discover SET.iv LAM [--dump] [--time N] [--tier2]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define MAXIV   4096
#define MAXK    64              /* max intervals per section (section.py) */

/* model weights — must equal kit.py's */
#define OP_ALU  1.0
#define OP_CMP  1.0
#define OP_LOAD 3.0
#define OP_DEP  5.0
#define DISP_BYTES 12.0
#define DISP_OPS   1.0

#define RANGES_MAXK  8
#define CUBES_MAXW   256
#define CUBES_MAXCUBES 6
#define BSEARCH_MINK 8

enum { F_ALL, F_RANGES, F_CUBES, F_MASK64, F_BITMAP, F_PAGE64, F_BSEARCH,
       F_NONE };
static const char *fname[] = { "ALL", "RANGES", "CUBES", "MASK64", "BITMAP",
                               "PAGE64", "BSEARCH", "-" };

static unsigned lo[MAXIV], hi[MAXIV];
static int n;
static int tier2 = 0;

/* ---------------------------------------------------------------- helpers */

static unsigned range_and(unsigned a, unsigned b)
{
    int sh = 0;
    while (a != b) { a >>= 1; b >>= 1; sh++; }
    return a << sh;
}

static unsigned range_or(unsigned a, unsigned b)
{
    if (a == b) return a;
    int m = 0;
    unsigned x = a ^ b;
    while (x) { x >>= 1; m++; }
    return (a | b) | ((1u << m) - 1u);
}

static int bitlen(unsigned v) { int b = 0; while (v) { v >>= 1; b++; } return b; }

/* TIER 1: is section [i..j] exactly ONE don't-care cube?  O(k).
 * Returns 1 and sets the cube's care/val, else 0.  The cube-containment check runs on
 * a 256-bit bitset (four words) — 2**nbits <= 256 because W <= 256. */
static int cube_of(int i, int j, unsigned *pcare, unsigned *pval)
{
    unsigned base = lo[i], top = hi[j];
    unsigned w = top - base + 1;
    if (w > CUBES_MAXW) return 0;
    int nbits = bitlen(w - 1); if (nbits < 1) nbits = 1;
    unsigned full = (nbits >= 32) ? 0xFFFFFFFFu : ((1u << nbits) - 1u);

    unsigned a_all = full, o_all = 0, nmem = 0;
    for (int t = i; t <= j; t++) {
        unsigned x0 = lo[t] - base, x1 = hi[t] - base;
        a_all &= range_and(x0, x1);
        o_all |= range_or(x0, x1);
        nmem += x1 - x0 + 1;
    }
    unsigned val = a_all;
    unsigned care = full & ~(o_all & ~a_all);
    int nfree = nbits - __builtin_popcount(care);
    unsigned csize = 1u << nfree;
    /* O(k) necessary condition: the cube's spill cannot exceed the
     * don't-care budget (the points x >= W the dispatch makes unreachable). */
    if (csize < nmem) return 0;
    if (csize - nmem > (1u << nbits) - w) return 0;

    /* exact: cube \subseteq members u don't-cares */
    unsigned long long mem[4] = {0,0,0,0}, cube[4] = {0,0,0,0}, ok[4];
    for (int t = i; t <= j; t++)
        for (unsigned x = lo[t] - base; x <= hi[t] - base; x++)
            mem[x >> 6] |= 1ULL << (x & 63);
    for (int b = 0; b < 4; b++) ok[b] = mem[b];
    for (unsigned x = w; x < (1u << nbits); x++)   /* don't-cares */
        ok[x >> 6] |= 1ULL << (x & 63);
    cube[val >> 6] |= 1ULL << (val & 63);
    for (int b = 0; b < nbits; b++) {
        if ((care >> b) & 1) continue;
        unsigned sh = 1u << b;                     /* cube |= cube << 2**b */
        unsigned long long t0[4];
        for (int q = 0; q < 4; q++) t0[q] = 0;
        for (unsigned x = 0; x < (1u << nbits); x++)
            if ((cube[x >> 6] >> (x & 63)) & 1)
                t0[(x + sh) >> 6] |= 1ULL << ((x + sh) & 63);
        for (int q = 0; q < 4; q++) cube[q] |= t0[q];
    }
    for (int q = 0; q < 4; q++) if (cube[q] & ~ok[q]) return 0;
    *pcare = care; *pval = val;
    return 1;
}

/* PAGE64 price, O(k): absolute 64-wide pages, so only the pages an interval
 * starts or ends in can be partial. */
static void page_price(int i, int j, unsigned *pnpages, unsigned *pnleaf)
{
    unsigned pbase = lo[i] >> 6;
    unsigned npages = (hi[j] >> 6) - pbase + 1;
    unsigned long long bm[2 * MAXK];
    unsigned bp[2 * MAXK];
    int nb = 0, full = 0;
    unsigned touched = 0;
    long prev_last = -1;
    for (int t = i; t <= j; t++) {
        unsigned pl = lo[t] >> 6, ph = hi[t] >> 6;
        if (ph - pl >= 2) full = 1;
        /* DISTINCT touched pages: two consecutive intervals can share the
         * page between them.  Double-counting it suppressed the all-empty
         * leaf and under-priced PAGE64 by 8 bytes on one section of \p{L}. */
        touched += ph - pl + 1;
        if (prev_last >= 0 && (unsigned)prev_last == pl) touched--;
        prev_last = ph;
        unsigned ps[2] = { pl, ph };
        for (int q = 0; q < 2; q++) {
            unsigned p = ps[q];
            unsigned a = lo[t] > (p << 6) ? lo[t] : (p << 6);
            unsigned b = hi[t] < ((p << 6) + 63) ? hi[t] : ((p << 6) + 63);
            unsigned long long m = (b - a + 1 >= 64) ? ~0ULL
                                 : (((1ULL << (b - a + 1)) - 1) << (a - (p << 6)));
            int f = -1;
            for (int z = 0; z < nb; z++) if (bp[z] == p) { f = z; break; }
            if (f < 0) { bp[nb] = p; bm[nb] = m; nb++; }
            else bm[f] |= m;
        }
    }
    /* distinct mask values among boundary pages, plus the two constants */
    unsigned long long seen[2 * MAXK + 2];
    int ns = 0;
    for (int z = 0; z < nb; z++) {
        int f = 0;
        for (int y = 0; y < ns; y++) if (seen[y] == bm[z]) { f = 1; break; }
        if (!f) seen[ns++] = bm[z];
    }
    if (full) {
        int f = 0;
        for (int y = 0; y < ns; y++) if (seen[y] == ~0ULL) { f = 1; break; }
        if (!f) seen[ns++] = ~0ULL;
    }
    if (touched < npages) {
        int f = 0;
        for (int y = 0; y < ns; y++) if (seen[y] == 0ULL) { f = 1; break; }
        if (!f) seen[ns++] = 0ULL;
    }
    *pnpages = npages; *pnleaf = (unsigned)ns;
}

/* cheapest kit member for section [i..j] at this lam */
static double sect_cost(int i, int j, double lam, int *pform,
                        double *pro, double *pops)
{
    unsigned base = lo[i], top = hi[j];
    unsigned w = top - base + 1;
    int k = j - i + 1;
    double bestv = 1e300; int bf = F_NONE; double bro = 0, bops = 0;

#define OFFER(F, RO, OPS) do {                                  \
        double v_ = (double)(RO) + lam * (double)(OPS);          \
        if (v_ < bestv) { bestv = v_; bf = (F);                  \
                          bro = (double)(RO); bops = (double)(OPS); } \
    } while (0)

    if (k == 1) OFFER(F_ALL, 0, 0.0);
    if (k <= RANGES_MAXK) OFFER(F_RANGES, 0, k * (OP_ALU + OP_CMP));
    if (w <= 64) OFFER(F_MASK64, 0, 2 * OP_ALU + OP_CMP);
    if (w <= CUBES_MAXW && k >= 2) {
        unsigned care, val;
        if (cube_of(i, j, &care, &val)) OFFER(F_CUBES, 0, OP_ALU + OP_CMP);
    }
    OFFER(F_BITMAP, (w + 7) / 8, OP_LOAD + 3 * OP_ALU);
    if (w >= 128) {
        unsigned np, nl;
        page_price(i, j, &np, &nl);
        unsigned idxw = (nl <= 256) ? 1 : 2;
        OFFER(F_PAGE64, np * idxw + nl * 8, OP_LOAD + OP_DEP + 4 * OP_ALU);
    }
    if (k >= BSEARCH_MINK) {
        /* log2 must be the REAL log, not a floor: section.py uses
         * math.log2 and an integer floor here made the two implementations
         * disagree on `L` at lam=16 (27 sections vs 28) — the first thing
         * the cross-check caught. */
        OFFER(F_BSEARCH, 8 * k, log2((double)k) * (OP_LOAD + 2 * OP_CMP));
    }
#undef OFFER
    *pform = bf; *pro = bro; *pops = bops;
    return bestv;
}

static double dpbest[MAXIV + 1];
static int bi[MAXIV + 1], bform[MAXIV + 1];
static double bro_[MAXIV + 1], bops_[MAXIV + 1];

static double run_dp(double lam)
{
    for (int j = 0; j <= n; j++) { dpbest[j] = 1e300; bi[j] = -1; }
    dpbest[0] = 0.0;
    for (int j = 0; j < n; j++) {
        int i0 = j - MAXK + 1; if (i0 < 0) i0 = 0;
        for (int i = j; i >= i0; i--) {
            if (dpbest[i] >= 1e299) continue;
            int f; double ro, ops;
            sect_cost(i, j, lam, &f, &ro, &ops);
            if (f == F_NONE) continue;
            double v = dpbest[i] + ro + DISP_BYTES + lam * (ops + DISP_OPS);
            if (v < dpbest[j + 1]) {
                dpbest[j + 1] = v; bi[j + 1] = i; bform[j + 1] = f;
                bro_[j + 1] = ro; bops_[j + 1] = ops;
            }
        }
    }
    return dpbest[n];
}

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: discover SET.iv LAM [--dump]"
                                    " [--time N] [--tier2]\n"); return 2; }
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror(argv[1]); return 2; }
    unsigned a, b;
    while (n < MAXIV && fscanf(f, "%x %x", &a, &b) == 2) {
        lo[n] = a; hi[n] = b; n++;
    }
    fclose(f);
    if (!n) { fprintf(stderr, "discover: empty set\n"); return 2; }

    double lam = atof(argv[2]);
    int dump = 0, reps = 0;
    for (int i = 3; i < argc; i++) {
        if (!strcmp(argv[i], "--dump")) dump = 1;
        else if (!strcmp(argv[i], "--tier2")) tier2 = 1;
        else if (!strcmp(argv[i], "--time") && i + 1 < argc) reps = atoi(argv[++i]);
    }
    (void)tier2;

    double cost = run_dp(lam);

    /* walk back */
    int secs[MAXIV], forms[MAXIV], ns = 0;
    double ro_tot = 0, ops_tot = 0;
    for (int j = n; j > 0; j = bi[j]) {
        secs[ns] = bi[j]; forms[ns] = bform[j];
        ro_tot += bro_[j]; ops_tot += bops_[j]; ns++;
    }

    if (reps) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        for (int r = 0; r < reps; r++) run_dp(lam);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        double el = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
        printf("TIME intervals=%d lam=%g reps=%d total_s=%.6f per_call_ms=%.4f\n",
               n, lam, reps, el, 1e3 * el / reps);
    }

    printf("SET intervals=%d lam=%g sections=%d rodata=%.0f ops=%.1f cost=%.1f\n",
           n, lam, ns, ro_tot, ops_tot, cost);
    if (dump)
        for (int z = ns - 1, o = 0; z >= 0; z--, o++)
            printf("SEC %d start=%d form=%s\n", o, secs[z], fname[forms[z]]);
    return 0;
}
