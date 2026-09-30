/* [UTF-VALID] revision (lane uvrev) cost probe, answering critic r2 F8:
 * (A) the SPARSE-non-ASCII subject (mostly-ASCII text with an occasional
 *     two-byte character), where the 8-byte ASCII fast path is neither the
 *     ASCII-text win nor the random-mix regression;
 * (B) the PER-CALL FIXED COST on small subjects, the find-all case: the
 *     entry a precheck would call (a non-inlined function doing the raw
 *     lookbehind step-back and the validation), against a pcrec `-e utf8`
 *     `_search` call on the same subject.
 * Validators are utfcheck_bench.c's (same rule, same offsets). Darwin timing
 * is DIRECTIONAL ONLY (house rule).
 *
 *   pcrec -p p1 -e utf8 -o p1.c --pattern 'jumpz'
 *   pcrec -p p2 -e utf8 -o p2.c --pattern '[a-z]+@[a-z]+'
 *   pcrec -p p3 -e utf8 --features all -o p3.c --pattern '\bfox\b'
 *   gcc-16 -O2 -o b2 utfcheck_bench2.c p1.c p2.c p3.c && ./b2
 */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "p1.h"
#include "p2.h"
#include "p3.h"

static size_t v_bytewise(const unsigned char *s, size_t n, size_t i)
{
    while (i < n) {
        unsigned c = s[i];
        if (c < 0x80) { i++; continue; }
        size_t k; unsigned lo = 0x80, hi = 0xBF;
        if (c >= 0xC2 && c <= 0xDF) k = 1;
        else if (c == 0xE0) { k = 2; lo = 0xA0; }
        else if (c == 0xED) { k = 2; hi = 0x9F; }
        else if (c >= 0xE1 && c <= 0xEF) k = 2;
        else if (c == 0xF0) { k = 3; lo = 0x90; }
        else if (c == 0xF4) { k = 3; hi = 0x8F; }
        else if (c >= 0xF1 && c <= 0xF3) k = 3;
        else return i;
        if (n - i <= k) return i;
        if (s[i + 1] < lo || s[i + 1] > hi) return i;
        for (size_t j = 2; j <= k; j++) if ((s[i + j] & 0xC0) != 0x80) return i;
        i += k + 1;
    }
    return n;
}
static size_t seq_len(const unsigned char *s, size_t avail)
{
    unsigned c = s[0], lo = 0x80, hi = 0xBF;
    size_t k;
    if (c >= 0xC2 && c <= 0xDF) k = 1;
    else if (c == 0xE0) { k = 2; lo = 0xA0; }
    else if (c == 0xED) { k = 2; hi = 0x9F; }
    else if (c >= 0xE1 && c <= 0xEF) k = 2;
    else if (c == 0xF0) { k = 3; lo = 0x90; }
    else if (c == 0xF4) { k = 3; hi = 0x8F; }
    else if (c >= 0xF1 && c <= 0xF3) k = 3;
    else return 0;
    if (avail <= k || s[1] < lo || s[1] > hi) return 0;
    for (size_t j = 2; j <= k; j++) if ((s[j] & 0xC0) != 0x80) return 0;
    return k + 1;
}
static size_t v_ascii8(const unsigned char *s, size_t n, size_t i)
{
    while (i < n) {
        while (i + 8 <= n) {
            uint64_t w; memcpy(&w, s + i, 8);
            if (w & 0x8080808080808080ull) break;
            i += 8;
        }
        if (i >= n) break;
        if (s[i] < 0x80) { i++; continue; }
        size_t k = seq_len(s + i, n - i);
        if (!k) return i;
        i += k;
    }
    return n;
}
/* The entry shape the revised note proposes: startpos in, the artifact's own
 * raw step-back of LB characters (skip continuation bytes, unvalidated,
 * clamped at 0), then the validator. Not inlined: the entry wrapper calls it. */
__attribute__((noinline)) static size_t invalid_at(const unsigned char *s, size_t n,
                                                   size_t startpos, unsigned lb)
{
    size_t f = startpos;
    for (unsigned k = 0; k < lb && f > 0; k++) {
        f--;
        while (f > 0 && (s[f] & 0xC0) == 0x80) f--;
    }
    return v_ascii8(s, n, f);
}

static double now(void)
{
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}
static volatile size_t sink;
#define N_BYTES (64u << 20)
#define RUNS 7

/* One two-byte character (U+00E9, "é") at a jittered period of ~`every`
 * bytes, ASCII prose otherwise. every=0: pure ASCII. */
static void fill_sparse(unsigned char *s, size_t n, unsigned every)
{
    const char *ascii = "the quick brown fox jumps over the lazy dog 0123456789\n";
    size_t al = strlen(ascii), i = 0, r = 12345, next = every ? every : (size_t)-1;
    while (i < n) {
        r = r * 1103515245 + 12345;
        if (i >= next && i + 2 <= n) {
            s[i++] = 0xC3; s[i++] = 0xA9;
            next = i + every / 2 + (r >> 16) % every;
        } else s[i++] = (unsigned char)ascii[(r >> 8) % al];
    }
}

int main(void)
{
    unsigned char *s = malloc(N_BYTES);
    /* (A) sparse subjects, whole-buffer rate */
    unsigned evs[] = { 16, 64, 256 };
    printf("# (A) sparse non-ASCII, 64 MiB, ns/byte best of %d\n", RUNS);
    printf("subject\tbytewise\tascii8+bytewise\n");
    for (int e = 0; e < 3; e++) {
        fill_sparse(s, N_BYTES, evs[e]);
        if (v_bytewise(s, N_BYTES, 0) != N_BYTES || v_ascii8(s, N_BYTES, 0) != N_BYTES) { printf("SELF-CHECK FAILED\n"); return 1; }
        double best[2] = { 1e9, 1e9 };
        for (int v = 0; v < 2; v++)
            for (int k = 0; k < RUNS; k++) {
                double t0 = now();
                sink = v ? v_ascii8(s, N_BYTES, 0) : v_bytewise(s, N_BYTES, 0);
                double t = (now() - t0) / N_BYTES * 1e9;
                if (t < best[v]) best[v] = t;
            }
        printf("1-per-~%u-bytes\t%.4f\t%.4f\n", evs[e], best[0], best[1]);
    }
    /* (B) small subjects, per-call ns. Subjects are consecutive windows of
     * the ~1-per-64 sparse buffer (so some carry a multi-byte character), each
     * starting on a character boundary. */
    fill_sparse(s, N_BYTES, 64);
    size_t sizes[] = { 8, 32, 128, 512, 4096 };
    printf("# (B) per call, ns, best of %d; subject = a window of the 1-per-~64 buffer\n", RUNS);
    printf("size\tcheck(LB=0)\tcheck(LB=1)\tp1_search(jumpz)\tp2_search([a-z]+@[a-z]+)\tp3_search(\\bfox\\b)\n");
    for (int z = 0; z < 5; z++) {
        size_t S = sizes[z], calls = (size_t)(N_BYTES / 2) / S;
        if (calls > (1u << 21)) calls = 1u << 21;
        double best[5] = { 1e9, 1e9, 1e9, 1e9, 1e9 };
        for (int col = 0; col < 5; col++)
            for (int k = 0; k < RUNS; k++) {
                size_t acc = 0;
                double t0 = now();
                for (size_t c = 0; c < calls; c++) {
                    size_t off = c * S;
                    while ((s[off] & 0xC0) == 0x80) off++;
                    const unsigned char *w = s + off;
                    ptrdiff_t caps[1][2];
                    switch (col) {
                    case 0: acc += invalid_at(w, S, 0, 0); break;
                    case 1: acc += invalid_at(w, S, 1, 1); break;
                    case 2: acc += (size_t)p1_search(w, S, 0, caps); break;
                    case 3: acc += (size_t)p2_search(w, S, 0, caps); break;
                    case 4: acc += (size_t)p3_search(w, S, 0, caps); break;
                    }
                }
                sink = acc;
                double t = (now() - t0) / calls * 1e9;
                if (t < best[col]) best[col] = t;
            }
        printf("%zu\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n", S, best[0], best[1], best[2], best[3], best[4]);
    }
    return 0;
}
