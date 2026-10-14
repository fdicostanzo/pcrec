/* R-17 (lane r17s): the EXHAUSTIVE answer check of every twin against the
 * byte loop.
 *
 * The reference is the scalar byte loop over the cell's set, written here
 * from the TABLE gen_twins.py derives from the cell's member list, never
 * from a form's own terms (the SWAR/SIMD terms are a second spelling of S
 * and must agree with it; the table walk is itself a twin under test):
 *
 *     ref(s, lo, hi) = least i in [lo, hi) with member(s[i]), else hi;
 *                      lo when lo >= hi.
 *
 * Every twin is called at hi = n and hi = n - 1 (the bounded site's range,
 * end_back 1) for EVERY start lo in [0, n] (lo = n included: the empty
 * range), and n in [0, NMAX]. Subject families, per cell:
 *   F1 all 256 bytes at every position and lane phase: s[i] = (i*step +
 *      seed) & 255, seed 0..255, step in {1, 37, 101}.
 *   F2 one probe byte at every position p over a background byte, every
 *      (n, p, lo): the probe from the cell's ALPHABET (every member and
 *      near-member -- each member with one bit flipped, each edge +-1 --
 *      edges only for a set of > 8 members, plus 0x00, 0xFF, 0x20, 0x61),
 *      the background from three (a text-like non-member, a non-member
 *      near-member, a member).
 *   F3 random subjects over the alphabet (xorshift, fixed seed).
 *   F4 the guard page: F3's subjects placed so the byte at hi - 1 is the
 *      last byte before a PROT_NONE page, and so s[0] is the first byte
 *      after one (an over-read or under-read is a SIGSEGV, not a pass).
 * A planted control (PLANT=1 in the environment) flips one member's table
 * bit in the reference: the check must then FAIL for every cell (each
 * cell's planted byte is one of its members), proving it can see a wrong
 * answer.
 *
 * Output: per twin, the number of calls compared and the number of
 * mismatches; last line `R17 CHECK: twins=T calls=C mismatches=M` and the
 * exit status is 0 iff M == 0 (or, under PLANT=1, iff every cell's table
 * twin mismatched at least once).
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

#include "twins_gen.h"

#ifndef NMAX
#define NMAX 80
#endif

static unsigned char REF[256];

static size_t ref(const unsigned char *s, size_t lo, size_t hi)
{
    while (lo < hi && !REF[s[lo]]) lo++;
    return lo;
}

static unsigned long long calls[NTWINS], bad[NTWINS];
static int have_avx2;

static void run_one(size_t t, const unsigned char *s, size_t n)
{
    const twin *w = &TWINS[t];
    if (w->simd == 2 && !have_avx2) return;
    for (int b = 0; b < 2; b++) {
        if (b && n == 0) break;
        size_t hi = n - (size_t)b;
        for (size_t lo = 0; lo <= n; lo++) {
            size_t want = ref(s, lo, hi), got = w->f(s, lo, hi);
            calls[t]++;
            if (got != want) {
                if (bad[t] < 3)
                    fprintf(stderr, "MISMATCH %s/%s n=%zu hi=%zu lo=%zu want=%zu got=%zu\n",
                            w->cell, w->form, n, hi, lo, want, got);
                bad[t]++;
            }
        }
    }
}

static uint64_t rng = 0x9E3779B97F4A7C15ull;
static uint64_t xs(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }

/* The cell's alphabet: members, near-members, a few fixed bytes. A set of
 * more than 8 members (a range or a wide cube) contributes its EDGES: the
 * two extreme members, their +-1 and one-bit-flip neighbours, and the
 * members at each power-of-two offset from the low edge (F1 already puts
 * every byte at every position). */
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
    for (int b = 0; b < 256; b++)
        if (T[b]) { cnt++; if (lo < 0) lo = b; hi = b; }
    if (cnt <= 8) {
        for (int b = 0; b < 256; b++) if (T[b]) near(in, b);
    } else {
        near(in, lo);
        near(in, hi);
        for (int k = 1; lo + k <= hi; k <<= 1) in[lo + k] = 1;
    }
    in[0x00] = in[0xFF] = in[0x20] = in[0x61] = 1;
    int n = 0;
    for (int b = 0; b < 256; b++) if (in[b]) a[n++] = (unsigned char)b;
    return n;
}

/* F2's backgrounds: the first non-member at or after 0x20 (text-like), the
 * first non-member near-member, and the cell's lowest member. */
static int backgrounds(const unsigned char *T, const unsigned char *A, int na, unsigned char *bg)
{
    int n = 0;
    for (int b = 0x20; b < 0x120 && n < 1; b++) if (!T[b & 255]) bg[n++] = (unsigned char)b;
    for (int i = 0; i < na && n < 2; i++) if (!T[A[i]] && A[i] != bg[0]) bg[n++] = A[i];
    for (int b = 0; b < 256 && n < 3; b++) if (T[b]) bg[n++] = (unsigned char)b;
    return n;
}

int main(void)
{
    long pg = sysconf(_SC_PAGESIZE);
    int plant = getenv("PLANT") && atoi(getenv("PLANT"));
#ifdef __x86_64__
    __builtin_cpu_init();
    have_avx2 = __builtin_cpu_supports("avx2");
#endif
    /* guard region: [PROT_NONE][data page][PROT_NONE] */
    unsigned char *g = mmap(NULL, 3 * pg, PROT_READ | PROT_WRITE,
                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (g == MAP_FAILED) { perror("mmap"); return 2; }
    mprotect(g, pg, PROT_NONE);
    mprotect(g + 2 * pg, pg, PROT_NONE);
    unsigned char *page = g + pg;

    unsigned char buf[NMAX + 64];
    size_t t0 = 0;
    while (t0 < NTWINS) {
        size_t t1 = t0;
        while (t1 < NTWINS && !strcmp(TWINS[t1].cell, TWINS[t0].cell)) t1++;
        const unsigned char *T = TWINS[t0].T;
        memcpy(REF, T, 256);
        if (plant) {
            for (int b = 0; b < 256; b++) if (REF[b]) { REF[b] = 0; break; }
        }
        unsigned char A[256];
        int na = alphabet(T, A);
        unsigned char BG[4];
        int nbg = backgrounds(T, A, na, BG);
        for (size_t t = t0; t < t1; t++) {
            /* F1 */
            static const unsigned steps[] = { 1, 37, 101 };
            for (unsigned si = 0; si < 3; si++)
                for (unsigned seed = 0; seed < 256; seed++)
                    for (size_t n = 0; n <= NMAX; n++) {
                        for (size_t i = 0; i < n; i++) buf[i] = (unsigned char)(i * steps[si] + seed);
                        run_one(t, buf, n);
                    }
            /* F2 */
            for (int bi = 0; bi < nbg; bi++)
                for (int pi = 0; pi < na; pi++)
                    for (size_t n = 1; n <= NMAX; n++)
                        for (size_t p = 0; p < n; p++) {
                            memset(buf, BG[bi], n);
                            buf[p] = A[pi];
                            run_one(t, buf, n);
                        }
            /* F3 */
            for (int r = 0; r < 4000; r++) {
                size_t n = (size_t)(xs() % (NMAX + 1));
                for (size_t i = 0; i < n; i++) buf[i] = A[xs() % (uint64_t)na];
                run_one(t, buf, n);
            }
            /* F4: subject ends at the upper guard, then starts at the lower one */
            for (int r = 0; r < 1500; r++) {
                size_t n = (size_t)(xs() % (NMAX + 1));
                unsigned char *e = page + pg - n;
                for (size_t i = 0; i < n; i++) e[i] = A[xs() % (uint64_t)na];
                run_one(t, e, n);
                for (size_t i = 0; i < n; i++) page[i] = A[xs() % (uint64_t)na];
                run_one(t, page, n);
            }
        }
        t0 = t1;
    }
    unsigned long long C = 0, M = 0;
    int ncell_bad_table = 0, ncell = 0;
    const char *last = "";
    for (size_t t = 0; t < NTWINS; t++) {
        if (TWINS[t].simd == 2 && !have_avx2) {
            printf("%-6s %-7s SKIPPED (no avx2)\n", TWINS[t].cell, TWINS[t].form);
            continue;
        }
        printf("%-6s %-7s calls=%llu mismatches=%llu\n", TWINS[t].cell, TWINS[t].form, calls[t], bad[t]);
        C += calls[t];
        M += bad[t];
        if (strcmp(last, TWINS[t].cell)) { ncell++; last = TWINS[t].cell; }
        if (!strcmp(TWINS[t].form, "table") && bad[t]) ncell_bad_table++;
    }
    printf("R17 CHECK: twins=%zu calls=%llu mismatches=%llu%s\n", (size_t)NTWINS, C, M,
           plant ? " (PLANTED reference)" : "");
    if (plant) {
        printf("R17 PLANT: cells whose table twin was caught = %d of %d\n", ncell_bad_table, ncell);
        return ncell_bad_table == ncell ? 0 : 1;
    }
    return M == 0 ? 0 : 1;
}
