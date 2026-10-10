/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's SIMD family, lane
 *   r13, R-13).
 *
 * memfn/tests/g2/g2_simd_driver.c — G2's SIMD FAMILY, the DRIVER and its
 * REFERENCE (R4e' batch 1; integration.md §R4.9.7 "G2, the kit's own").
 *
 * THE REFERENCE (`ref` below) is a plain scalar byte loop over the bytes G2
 * GENERATED (g2_simd.h): the first c >= pos with c + off + L (+1 with the
 * second term) <= n whose every run byte holds under its mask (and whose
 * next byte is 'z' with the second term), else n. It calls no kit function
 * and shares no code with the kit's generator: the oracle relation is EXACT
 * RETURNED-POSITION equality.
 *
 * THE SUBJECTS, per site and per span length n in 0..2*32 + T + 8 (every
 * length; the w32 level's 2*VW + T and past it):
 *   - a NO-HIT subject of near-misses (runs with one byte wrong, filter
 *     bytes at the scanned position without the run): the filter passes,
 *     the verify fails, the loop continues;
 *   - a SINGLE hit planted at EVERY candidate offset;
 *   - MULTI-hit subjects (2..4 hits, two in one block, in the overlapped
 *     final block's already-covered lanes), each called along its restart
 *     chain (pos = the previous answer + 1) and at every pos 0..n;
 * in TWO layouts: E, the subject ends exactly at a PROT_NONE guard page
 * (`s + n` is the page boundary: one byte read past n faults); B, the
 * subject starts exactly at a page whose predecessor is PROT_NONE (a read
 * below `s` faults) and, beyond that, at every alignment 0..31 inside a
 * plain buffer. Under ASan (`-fsanitize=address`) the plain buffer is a
 * heap copy whose [buf, s) and [s + n, end) are POISONED per case
 * (ASAN_POISON_MEMORY_REGION), so an aligned-down load below `s` and a read
 * past `n` are seen at every alignment (§R4.9.7: a 16-aligned malloc leaves
 * [buf, s) addressable otherwise).
 * A fault (SIGSEGV/SIGBUS) is a FAILURE, reported with its site and case.
 *
 * Prints `G2V checks=N fail=M faults=F` and per-class counts; exit 1 on any
 * failure. `g2v_path[]` is the runner's per-path instrumentation (-DG2V_PATHS
 * text edits of the rendered file, never the kit's).
 */
#define _GNU_SOURCE
#include <setjmp.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "g2_simd.h"

#if defined(__SANITIZE_ADDRESS__)
#include <sanitizer/asan_interface.h>
#define G2V_ASAN 1
#else
#define G2V_ASAN 0
#endif

unsigned long g2v_path[8];

static unsigned long checks, fails, faults;
static sigjmp_buf jb;
static volatile sig_atomic_t in_call;

static void on_fault(int sig)
{
    (void)sig;
    if (in_call) siglongjmp(jb, 1);
    _exit(3);
}

static unsigned long long rng = 88172645463325252ull;
static unsigned rnd(unsigned n)
{
    rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
    return n ? (unsigned)(rng % n) : 0;
}

/* the reference: the module comment's loop */
__attribute__((noinline))
static size_t ref(const g2v_site *v, const unsigned char *s, size_t n, size_t pos)
{
    size_t need = v->off + v->L + v->two;
    for (size_t c = pos; c < n && need <= n - c; c++) {
        int ok = 1;
        for (unsigned j = 0; j < v->L && ok; j++)
            ok = (s[c + v->off + j] & v->mask[j]) == v->run[j];
        if (ok && v->two) ok = s[c + v->off + v->L] == 'z';
        if (ok) return c;
    }
    return n;
}

static long pagesz;
static unsigned char *regE, *regB;   /* [guard][page...] / [page...][guard] */
#define REGION (4 * 4096)

static int g_print = 20;

/* One call at `s` against the reference; a fault is a failure. */
static void check(const g2v_site *v, const unsigned char *s, size_t n, size_t pos,
                  const unsigned char *truth, const char *what)
{
    volatile size_t want = ref(v, truth, n, pos), got = (size_t)-1;
    checks++;
    in_call = 1;
    if (sigsetjmp(jb, 1) == 0) {
        got = v->fn(s, n, pos);
        in_call = 0;
    } else {
        in_call = 0;
        faults++;
        fails++;
        if (g_print-- > 0)
            fprintf(stderr, "FAIL fault: site %u L=%u off=%u n=%zu pos=%zu (%s)\n",
                    v->id, v->L, v->off, n, pos, what);
        return;
    }
    if (got != want) {
        fails++;
        if (g_print-- > 0) {
            fprintf(stderr, "FAIL answer: site %u L=%u off=%u n=%zu pos=%zu got=%zu want=%zu (%s) s=",
                    v->id, v->L, v->off, n, pos, (size_t)got, (size_t)want, what);
            for (size_t i = 0; i < n; i++) fprintf(stderr, "%02x", truth[i]);
            fputc('\n', stderr);
        }
    }
}

/* Every layout for one subject `t[0..n)` at `pos`. */
static void run_layouts(const g2v_site *v, const unsigned char *t, size_t n, size_t pos,
                        int aligns, const char *what)
{
    /* E: s + n at the guard page */
    unsigned char *e = regE + 3 * pagesz - n;
    memcpy(e, t, n);
    check(v, n ? e : regE + 3 * pagesz, n, pos, t, what);
    /* B: s at the page after the guard */
    unsigned char *b = regB + pagesz;
    memcpy(b, t, n);
    check(v, b, n, pos, t, what);
    if (!aligns) return;
    static unsigned char *heap;
    if (!heap) heap = malloc(256 + 64);
    for (unsigned a = 0; a < 32; a++) {
        unsigned char *s = heap + a;
        memcpy(s, t, n);
#if G2V_ASAN
        ASAN_POISON_MEMORY_REGION(heap, a);
        ASAN_POISON_MEMORY_REGION(s + n, 256 + 64 - a - n);
#endif
        check(v, s, n, pos, t, what);
#if G2V_ASAN
        ASAN_UNPOISON_MEMORY_REGION(heap, 256 + 64);
#endif
    }
}

/* A byte that is NOT the run byte at j under its mask (where one exists). */
static unsigned char wrong_at(const g2v_site *v, unsigned j)
{
    if (v->mask[j] == 0) return (unsigned char)rnd(256);
    for (;;) {
        unsigned char b = (unsigned char)rnd(256);
        if ((b & v->mask[j]) != v->run[j]) return b;
    }
}

/* A byte that holds at j (one of the cube's members, or any, under the mask). */
static unsigned char right_at(const g2v_site *v, unsigned j)
{
    unsigned char free_bits = (unsigned char)~v->mask[j];
    return (unsigned char)(v->run[j] | (rnd(256) & free_bits));
}

static void plant(const g2v_site *v, unsigned char *t, size_t c)
{
    for (unsigned j = 0; j < v->L; j++) t[c + v->off + j] = right_at(v, j);
    if (v->two) t[c + v->off + v->L] = 'z';
}

/* filler: near-misses everywhere (a run with one byte wrong at a random
 * offset), or noise; every planted hit afterwards is a true one */
static void fill(const g2v_site *v, unsigned char *t, size_t n)
{
    for (size_t i = 0; i < n; i++) t[i] = (unsigned char)(rnd(4) ? rnd(256) : 'z');
    size_t need = v->off + v->L + v->two;
    if (n < need) return;
    for (unsigned k = 0; k < n / 3 + 1; k++) {
        size_t c = rnd((unsigned)(n - need + 1));
        plant(v, t, c);
        t[c + v->off + rnd(v->L)] = wrong_at(v, rnd(v->L));
        unsigned j = rnd(v->L);
        t[c + v->off + j] = wrong_at(v, j);
    }
}

static void run_site(const g2v_site *v)
{
    unsigned T = v->off + v->L + v->two - 1;
    size_t nmax = 2 * 32 + T + 8;
    unsigned char t[512];
    size_t need = v->off + v->L + v->two;
    for (size_t n = 0; n <= nmax; n++) {
        /* no hit (near-misses), every pos */
        fill(v, t, n);
        for (size_t pos = 0; pos <= n + 1; pos++) run_layouts(v, t, n, pos, pos == 0, "nohit");
        if (n < need) continue;
        /* a single hit at every candidate */
        for (size_t c = 0; c + need <= n; c++) {
            fill(v, t, n);
            plant(v, t, c);
            run_layouts(v, t, n, 0, 0, "single");
            if (c) run_layouts(v, t, n, c, 0, "single-at");
        }
        /* multiple hits: a restart chain and every pos */
        for (int r = 0; r < 3; r++) {
            fill(v, t, n);
            unsigned k = 2 + rnd(3);
            size_t c0 = rnd((unsigned)(n - need + 1));
            plant(v, t, c0);
            if (c0 + 1 + need <= n) {   /* a second hit within 4 of the first: one block */
                size_t room = n - need - c0;
                plant(v, t, c0 + 1 + rnd((unsigned)(room < 4 ? room : 4)));
            }
            for (unsigned h = 2; h < k; h++) plant(v, t, rnd((unsigned)(n - need + 1)));
            for (size_t pos = 0; pos <= n; pos++) run_layouts(v, t, n, pos, pos == 0, "multi");
        }
    }
}

int main(int argc, char **argv)
{
    unsigned only = argc > 1 ? (unsigned)atoi(argv[1]) : ~0u;
    pagesz = sysconf(_SC_PAGESIZE);
    regE = mmap(NULL, 4 * pagesz, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    regB = mmap(NULL, 4 * pagesz, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (regE == MAP_FAILED || regB == MAP_FAILED) { perror("mmap"); return 2; }
    mprotect(regE + 3 * pagesz, pagesz, PROT_NONE);
    mprotect(regB, pagesz, PROT_NONE);
    struct sigaction sa = { 0 };
    sa.sa_handler = on_fault;
    sigaction(SIGSEGV, &sa, NULL);
    sigaction(SIGBUS, &sa, NULL);
    for (unsigned i = 0; i < g2v_nsites; i++) {
        if (only != ~0u && g2v_sites[i].id != only) continue;
        run_site(&g2v_sites[i]);
    }
    printf("G2V checks=%lu fail=%lu faults=%lu\n", checks, fails, faults);
    for (int l = 0; l < 2; l++)
        printf("G2V paths level=w%d entry_fallthrough=%lu whole_block=%lu final_block=%lu verified=%lu\n",
               16 << l, g2v_path[4 * l], g2v_path[4 * l + 1], g2v_path[4 * l + 2],
               g2v_path[4 * l + 3]);
    return fails ? 1 : 0;
}
