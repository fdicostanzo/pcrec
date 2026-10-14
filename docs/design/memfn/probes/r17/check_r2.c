/* R-17 revision 2 (lane r17r5): the CANDIDATE-SEQUENCE answer check of the
 * stateful twins. WRITTEN, NOT RUN (setfind.md §13; owed with the slot).
 *
 * The property (setfind.md §8.2): for ANY sequence of lo values over one
 * subject, with the state declared once and never reset, every answer of a
 * stateful twin equals the byte loop's F(lo) -- and the cell's stateless
 * `swar` twin's (stateful == stateless == byte loop). Reference: a next-member
 * array built from the cell's TABLE (the member list), never from a form's
 * terms, so F(lo, hi) = lo >= hi ? lo : min(next[lo], hi), O(1) per use.
 *
 * Sequences, each starting from a FRESH state (sreset), each at hi = n and
 * hi = n - 1 (the bounded site):
 *   Q1 find-all: lo = 0, then lo = ans + 1 until ans == hi
 *   Q2 find-all with jumps: lo = ans + 1 + g, g in [0, 8) and [0, 70)
 *   Q3 random walk: 64 uses at lo in [0, n + 2] (backwards included)
 *   Q4 sweeps: lo = n down to 0, then 0 up to n
 *   Q5 block edges: lo = 0, then 63 64 65 127 128 129, hi-65 hi-64 hi-63
 *   Q6 empties interleaved: n, n+1, 0, n+5, 1, hi, 2 (an empty use must
 *      leave the state alone)
 *   Q7 null subject: n = 0, s = NULL, lo = 0 and 1 (no read, no write)
 * Subjects (n <= NMAX = 160, so sequences cross two 64-byte blocks):
 *   F1 every byte at every lane phase: s[i] = i*step + seed, 32 seeds x 2 steps
 *   F2 one probe from the cell's alphabet over three backgrounds, every p, at
 *      n in {64, 65, 129} (block-boundary lengths)
 *   F3 2,000 random alphabet subjects
 *   F4 600 subjects ending at a PROT_NONE page, 600 starting after one
 *
 * POPULATIONS (K35), counted by inspecting the state around each call:
 *   cache  uses that entered with lo in [base, top)
 *   fill   uses after which (base, top) changed
 *   back   uses whose lo was below the previous use's lo
 *   walk   adaptive uses taken in walk mode (steps > 0 on entry)
 * Each is printed per twin and must be > 0 for every twin that has the
 * mechanism (the run's first reading then sets literal floors; owed).
 *
 * PLANT: the binary built with -DPLANT_STALE (run_time_r2.sh builds both)
 * must catch EVERY twin with a cache (mask and ring forms; adapt_mask).
 *
 * Last line: `R17R2 CHECK: twins=T calls=C mismatches=M` (or, planted,
 * `R17R2 PLANT: cache twins caught = X of Y`); exit 0 iff M == 0 (planted:
 * iff X == Y) and every population is non-zero.
 */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#ifdef __x86_64__
#include <immintrin.h>
#endif

#include "twins_r2_gen.h"

#ifndef NMAX
#define NMAX 160
#endif
#if NMAX < 129
#error "NMAX must be >= 129 (F2 builds n = 129 subjects in buf)"
#endif

static size_t NX[NMAX + 2];
static unsigned char REF[256];
static unsigned long long calls[NTW2], bad[NTW2], p_cache[NTW2], p_fill[NTW2],
    p_back[NTW2], p_walk[NTW2];
static int have_avx2;
static find_fn SWAR;            /* the cell's stateless swar twin */
static sstate ST;
static uint64_t rng = 0x9E3779B97F4A7C15ull;
static uint64_t xs(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }

static void build_next(const unsigned char *s, size_t n)
{
    NX[n] = n;
    for (size_t i = n; i-- > 0;) NX[i] = REF[s[i]] ? i : NX[i + 1];
}

static size_t ref(size_t lo, size_t hi)
{
    if (lo >= hi) return lo;
    return NX[lo] < hi ? NX[lo] : hi;
}

static size_t last_lo;

/* One use: call the twin, compare with the byte loop and the stateless twin,
 * count the populations. */
static size_t use(size_t t, const unsigned char *s, size_t n, size_t lo, size_t hi)
{
    const twin2 *w = &TW2[t];
    sstate before = ST;
    if ((size_t)(lo - ST.base) < (size_t)(ST.top - ST.base)) p_cache[t]++;
    if (ST.steps) p_walk[t]++;
    if (lo < last_lo) p_back[t]++;
    last_lo = lo;
    size_t got = w->sf(&ST, s, lo, hi);
    size_t want = lo <= n ? ref(lo, hi) : lo;
    size_t sl = SWAR && s ? SWAR(s, lo, hi) : want;
    calls[t]++;
    if (ST.base != before.base || ST.top != before.top) p_fill[t]++;
    if (lo >= hi && memcmp(&before, &ST, sizeof ST) != 0) {
        if (bad[t] < 3) fprintf(stderr, "STATE WRITTEN ON EMPTY %s/%s n=%zu lo=%zu hi=%zu\n",
                                w->cell, w->form, n, lo, hi);
        bad[t]++;
    }
    if (got != want || sl != want) {
        if (bad[t] < 3)
            fprintf(stderr, "MISMATCH %s/%s n=%zu hi=%zu lo=%zu want=%zu got=%zu swar=%zu\n",
                    w->cell, w->form, n, hi, lo, want, got, sl);
        bad[t]++;
    }
    return got;
}

static void seqs(size_t t, const unsigned char *s, size_t n)
{
    for (int b = 0; b < 2; b++) {
        if (b && n == 0) break;
        size_t hi = n - (size_t)b, a, lo;
        /* Q1 */
        sreset(&ST); last_lo = 0;
        for (lo = 0;; lo = a + 1) { a = use(t, s, n, lo, hi); if (a >= hi) break; }
        /* Q2, two jump scales */
        for (int sc = 0; sc < 2; sc++) {
            uint64_t m = sc ? 70 : 8;
            sreset(&ST); last_lo = 0;
            for (lo = 0; lo <= n + 2;) { a = use(t, s, n, lo, hi); if (a >= hi) break; lo = a + 1 + (size_t)(xs() % m); }
        }
        /* Q3 */
        sreset(&ST); last_lo = 0;
        for (int k = 0; k < 64; k++) use(t, s, n, (size_t)(xs() % (n + 3)), hi);
        /* Q4 */
        sreset(&ST); last_lo = 0;
        for (size_t i = n + 1; i-- > 0;) use(t, s, n, i, hi);
        for (size_t i = 0; i <= n; i++) use(t, s, n, i, hi);
        /* Q5 */
        sreset(&ST); last_lo = 0;
        use(t, s, n, 0, hi);
        static const size_t e[] = { 63, 64, 65, 127, 128, 129 };
        for (size_t k = 0; k < sizeof e / sizeof e[0]; k++) if (e[k] <= n + 2) use(t, s, n, e[k], hi);
        for (size_t d = 63; d <= 65; d++) if (hi >= d) use(t, s, n, hi - d, hi);
        /* Q6 */
        sreset(&ST); last_lo = 0;
        size_t q6[] = { n, n + 1, 0, n + 5, 1, hi, 2 };
        for (size_t k = 0; k < sizeof q6 / sizeof q6[0]; k++) use(t, s, n, q6[k], hi);
    }
}

static void near(unsigned char *in, int b)
{
    in[b] = 1;
    for (int k = 0; k < 8; k++) in[b ^ (1 << k)] = 1;
    in[(b + 1) & 255] = in[(b - 1) & 255] = 1;
}

static int alphabet(const unsigned char *T, unsigned char *a)
{
    unsigned char in[256] = { 0 };
    int cnt = 0, lo = -1, hi = -1;
    for (int b = 0; b < 256; b++) if (T[b]) { cnt++; if (lo < 0) lo = b; hi = b; }
    if (cnt <= 8) { for (int b = 0; b < 256; b++) if (T[b]) near(in, b); }
    else { near(in, lo); near(in, hi); for (int k = 1; lo + k <= hi; k <<= 1) in[lo + k] = 1; }
    in[0x00] = in[0xFF] = in[0x20] = in[0x61] = 1;
    int n = 0;
    for (int b = 0; b < 256; b++) if (in[b]) a[n++] = (unsigned char)b;
    return n;
}

static void one_subject(size_t t, const unsigned char *s, size_t n)
{
    build_next(s, n);
    seqs(t, s, n);
}

/* optional argv: cell names; only twins of those cells run (a reduced run,
 * e.g. under the sanitizers); none = all */
static int wanted(const char *cell, int argc, char **argv)
{
    if (argc < 2) return 1;
    for (int i = 1; i < argc; i++) if (!strcmp(argv[i], cell)) return 1;
    return 0;
}

int main(int argc, char **argv)
{
    long pg = sysconf(_SC_PAGESIZE);
#ifdef PLANT_STALE
    const int plant = 1;
#else
    const int plant = 0;
#endif
#ifdef __x86_64__
    __builtin_cpu_init();
    have_avx2 = __builtin_cpu_supports("avx2");
#endif
    unsigned char *g = mmap(NULL, 3 * pg, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (g == MAP_FAILED) { perror("mmap"); return 2; }
    mprotect(g, pg, PROT_NONE);
    mprotect(g + 2 * pg, pg, PROT_NONE);
    unsigned char *page = g + pg;
    unsigned char buf[NMAX + 8];

    for (size_t t = 0; t < NTW2; t++) {
        const twin2 *w = &TW2[t];
        if (!w->sf || (w->simd == 2 && !have_avx2) || !wanted(w->cell, argc, argv)) continue;
        memcpy(REF, w->T, 256);
        SWAR = NULL;
        for (size_t u = 0; u < NTW2; u++)
            if (!strcmp(TW2[u].cell, w->cell) && !strcmp(TW2[u].form, "swar")) SWAR = TW2[u].f;
        unsigned char A[256], BG[3];
        int na = alphabet(w->T, A), nbg = 0;
        for (int b = 0x20; b < 0x120 && nbg < 1; b++) if (!w->T[b & 255]) BG[nbg++] = (unsigned char)b;
        for (int i = 0; i < na && nbg < 2; i++) if (!w->T[A[i]] && A[i] != BG[0]) BG[nbg++] = A[i];
        for (int b = 0; b < 256 && nbg < 3; b++) if (w->T[b]) BG[nbg++] = (unsigned char)b;
        /* F1 */
        static const unsigned steps[] = { 1, 37 };
        for (unsigned si = 0; si < 2; si++)
            for (unsigned seed = 0; seed < 32; seed++)
                for (size_t n = 0; n <= NMAX; n++) {
                    for (size_t i = 0; i < n; i++) buf[i] = (unsigned char)(i * steps[si] + seed * 8);
                    one_subject(t, buf, n);
                }
        /* F2 */
        static const size_t f2n[] = { 64, 65, 129 };
        for (int bi = 0; bi < nbg; bi++)
            for (int pi = 0; pi < na; pi++)
                for (size_t k = 0; k < 3; k++) {
                    size_t n = f2n[k];
                    for (size_t p = 0; p < n; p++) {
                        memset(buf, BG[bi], n);
                        buf[p] = A[pi];
                        one_subject(t, buf, n);
                    }
                }
        /* F3 */
        for (int r = 0; r < 2000; r++) {
            size_t n = (size_t)(xs() % (NMAX + 1));
            for (size_t i = 0; i < n; i++) buf[i] = A[xs() % (uint64_t)na];
            one_subject(t, buf, n);
        }
        /* F4 */
        for (int r = 0; r < 600; r++) {
            size_t n = (size_t)(xs() % (NMAX + 1));
            unsigned char *e = page + pg - n;
            for (size_t i = 0; i < n; i++) e[i] = A[xs() % (uint64_t)na];
            one_subject(t, e, n);
            for (size_t i = 0; i < n; i++) page[i] = A[xs() % (uint64_t)na];
            one_subject(t, page, n);
        }
        /* Q7: the null subject */
        NX[0] = 0;
        sreset(&ST); last_lo = 0;
        use(t, NULL, 0, 0, 0);
        use(t, NULL, 0, 1, 0);
    }

    unsigned long long C = 0, M = 0;
    int ntw = 0, ncache = 0, caught = 0, pop_ok = 1;
    for (size_t t = 0; t < NTW2; t++) {
        const twin2 *w = &TW2[t];
        if (!w->sf || !wanted(w->cell, argc, argv)) continue;
        if (w->simd == 2 && !have_avx2) { printf("%-6s %-13s SKIPPED (no avx2)\n", w->cell, w->form); continue; }
        int is_adapt = !strncmp(w->form, "adapt", 5);
        printf("%-6s %-13s calls=%llu mismatches=%llu cache=%llu fill=%llu back=%llu walk=%llu\n",
               w->cell, w->form, calls[t], bad[t], p_cache[t], p_fill[t], p_back[t], p_walk[t]);
        ntw++;
        C += calls[t];
        M += bad[t];
        if (w->cache) { ncache++; if (bad[t]) caught++; }
        if (!plant) {
            if (w->cache && (!p_cache[t] || !p_fill[t])) pop_ok = 0;
            if (!p_back[t]) pop_ok = 0;
            if (is_adapt && !p_walk[t]) pop_ok = 0;
        }
    }
    if (!pop_ok) printf("R17R2 POPULATION: a mechanism's population is zero (see the rows above)\n");
    printf("R17R2 CHECK: twins=%d calls=%llu mismatches=%llu%s\n", ntw, C, M,
           plant ? " (PLANTED stale state)" : "");
    if (plant) {
        printf("R17R2 PLANT: cache twins caught = %d of %d\n", caught, ncache);
        return caught == ncache ? 0 : 1;
    }
    return (M == 0 && pop_ok) ? 0 : 1;
}
