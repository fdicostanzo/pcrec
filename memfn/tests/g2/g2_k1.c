/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2, lane memfng2).
 *
 * memfn/tests/g2/g2_k1.c — the kit's K1 REFERENCE functions (mf_ref_*,
 * memfn.h) against G2's own loops, written here from the header's one-line
 * statements of what each answers. G2 never uses mf_ref_* as its oracle
 * (g2_ref.c is independent of them); this checks them in their own right,
 * since the header names them "the oracle side for G2" and the stand-alone
 * product's reference set.
 *
 * Every length 0..129, every alignment 0..15 (exact-size heap copies, so
 * the ASan build sees an over-read), a hit at every position, near-misses.
 * Prints `G2-K1 checks passed: N` / `G2-K1 checks failed: M`.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"

static uint64_t rs = 0x6a09e667f3bcc909ULL;
static uint64_t rnd(void)
{
    uint64_t z = (rs += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

static long pass, fail;
static void check(int ok, const char *what, size_t n, size_t got, size_t want)
{
    if (ok) { pass++; return; }
    if (fail++ < 30) fprintf(stderr, "FAIL K1 %s n=%zu: got %zu want %zu\n", what, n, got, want);
}

static int in(const uint8_t *set, unsigned b) { return set[b >> 3] >> (b & 7) & 1; }

int main(void)
{
    uint8_t subj[130];
    for (size_t n = 0; n <= 129; n++)
        for (int rep = 0; rep < 40; rep++) {
            /* a small alphabet so every byte the queries name occurs */
            unsigned alpha = 2 + (unsigned)(rnd() % 6);
            for (size_t i = 0; i < n; i++) subj[i] = (uint8_t)('a' + rnd() % alpha);
            if (n && rep % 3 == 0) subj[rnd() % n] = (uint8_t)rnd();
            size_t al = (size_t)rep & 15;
            uint8_t *heap = malloc(al + n + 1);
            uint8_t *s = heap + al;
            memcpy(s, subj, n);
            uint8_t a = (uint8_t)('a' + rnd() % 8), b = (uint8_t)('a' + rnd() % 8), c = (uint8_t)rnd();
            size_t w;

            /* F1: the first i with s[i] == c, else n */
            for (w = 0; w < n && s[w] != a; w++) {}
            size_t g = mf_ref_find_byte(s, n, a);
            check(g == w, "find_byte", n, g, w);
            /* F2: the first i with s[i] one of the bytes */
            for (w = 0; w < n && s[w] != a && s[w] != b; w++) {}
            g = mf_ref_find_any2(s, n, a, b);
            check(g == w, "find_any2", n, g, w);
            for (w = 0; w < n && s[w] != a && s[w] != b && s[w] != c; w++) {}
            g = mf_ref_find_any3(s, n, a, b, c);
            check(g == w, "find_any3", n, g, w);
            /* F4 / F5 over a random set */
            uint8_t set[32];
            for (int k = 0; k < 32; k++) set[k] = (uint8_t)(rnd() & rnd());
            for (w = 0; w < n && !in(set, s[w]); w++) {}
            g = mf_ref_find_in_set(s, n, set);
            check(g == w, "find_in_set", n, g, w);
            for (w = 0; w < n && in(set, s[w]); w++) {}
            g = mf_ref_skip_in_set(s, n, set);
            check(g == w, "skip_in_set", n, g, w);
            /* F9: the first i with s[i..i+len) == lit; len 0 matches at 0 */
            size_t len = (size_t)(rnd() % 5);
            uint8_t lit[8];
            if (n && rep % 2) {
                size_t at = (size_t)(rnd() % n);
                for (size_t j = 0; j < len; j++) lit[j] = at + j < n ? s[at + j] : 'a';
            } else for (size_t j = 0; j < len; j++) lit[j] = (uint8_t)('a' + rnd() % alpha);
            w = n;
            for (size_t i = 0; i + len <= n; i++)
                if (!memcmp(s + i, lit, len)) { w = i; break; }
            g = mf_ref_find_literal(s, n, lit, len);
            check(g == w, "find_literal", n, g, w);
            /* F7: 1 iff pos + len <= n and every (s[pos+j] & mask[j]) == run[j] */
            for (size_t pos = 0; pos <= n + 1; pos++) {
                uint8_t run[8], mask[8];
                size_t rl = (size_t)(rnd() % 6);
                for (size_t j = 0; j < rl; j++) {
                    mask[j] = rnd() % 3 ? 0xFF : (uint8_t)~(1u << (rnd() % 8));
                    run[j] = (uint8_t)((pos + j < n && rnd() % 4 ? s[pos + j] : (uint8_t)rnd()) & mask[j]);
                }
                int usemask = (int)(rnd() & 1);
                int want = pos + rl <= n;
                for (size_t j = 0; want && j < rl; j++)
                    want = (s[pos + j] & (usemask ? mask[j] : 0xFF)) == (usemask ? run[j] : run[j]);
                if (!usemask) {     /* exact: the run must equal the bytes */
                    want = pos + rl <= n;
                    for (size_t j = 0; want && j < rl; j++) want = s[pos + j] == run[j];
                }
                int gv = mf_ref_run_verify(s, n, pos, run, usemask ? mask : NULL, rl);
                check(gv == want, "run_verify", n, (size_t)gv, (size_t)want);
            }
            free(heap);
        }
    printf("G2-K1 checks passed: %ld\nG2-K1 checks failed: %ld\n", pass, fail);
    return 0;
}
