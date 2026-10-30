/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's find-any family,
 *   lane simdset).
 *
 * memfn/tests/g2/g2_any_gen.c — the GENERATOR of G2's find-any family
 * (run_g2_any.py): the family's only kit caller. It draws a GENERATED space
 * of member byte sets (K 2..3: 0x00, 0xFF, high-bit bytes, duplicates,
 * one-bit neighbours, random) and renders, for each set, the standalone
 * kernel `mf_kernel_find_any` at four level choices: none (the portable
 * body alone), each level alone, and every level (the ladder). It writes
 *   DIR/g2a_kernels.c  the kernels' text, then `g2a_table[]`: per kernel its
 *                      selector, K, the bytes AS GIVEN (duplicates kept)
 *                      and its level bits;
 *   DIR/g2a_meta.tsv   one row per kernel: id, k, bytes, levels.
 * It also asks for each refusal (K 1 and 4, a bad name, a level bit past
 * mf_levels(), a sink without vprintf) and fails unless each is refused.
 *
 *   g2_any_gen SEED NSETS DIR
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"

static void fput(void *u, const char *s) { fputs(s, (FILE *)u); }
static void fvp(void *u, const char *f, va_list ap) { vfprintf((FILE *)u, f, ap); }

static unsigned long long rng;
static unsigned rnd(unsigned n)
{
    rng = rng * 6364136223846793005ULL + 1442695040888963407ULL;
    return (unsigned)(rng >> 33) % n;
}

/* The fixed head of the space: every edge the charter names, then random. */
static const struct { unsigned k; uint8_t b[3]; } fixed[] = {
    {2, {0x00, 0xFF}}, {2, {0xFF, 0x00}}, {3, {0x00, 0x80, 0xFF}},
    {2, {0x7F, 0x80}}, {2, {0x80, 0x81}}, {3, {0xFE, 0xFF, 0x01}},
    {2, {'a', 'a'}},   {3, {'x', 'x', 'x'}}, {3, {'a', 'b', 'a'}}, {3, {0x00, 0x00, 0x01}},
    {2, {'a', 'A'}},   {2, {'\n', '\r'}},  {3, {'"', '\'', '\\'}}, {2, {0x10, 0x11}},
    {2, {0xC3, 0xA9}}, {3, {0x20, 0x09, 0x0A}},
};
#define NFIXED (sizeof fixed / sizeof fixed[0])

int main(int argc, char **argv)
{
    if (argc != 4) { fprintf(stderr, "usage: g2_any_gen SEED NSETS DIR\n"); return 2; }
    rng = strtoull(argv[1], NULL, 10);
    unsigned nsets = (unsigned)atoi(argv[2]);
    size_t nlv;
    mf_levels(&nlv);
    char path[4096], err[256];
    snprintf(path, sizeof path, "%s/g2a_kernels.c", argv[3]);
    FILE *f = fopen(path, "w");
    snprintf(path, sizeof path, "%s/g2a_meta.tsv", argv[3]);
    FILE *meta = fopen(path, "w");
    if (!f || !meta) { perror("g2_any_gen"); return 2; }
    mf_sink o = { .u = f, .puts = fput, .vprintf = fvp };

    /* the refusals: each must be refused, with a text */
    uint8_t b4[4] = {1, 2, 3, 4};
    struct { const char *why, *fn; unsigned k; uint32_t lv; int nosink; } neg[] = {
        {"k 1", "g2a_neg", 1, 0, 0}, {"k 4", "g2a_neg", 4, 0, 0},
        {"name", "2bad", 2, 0, 0}, {"name", "a b", 2, 0, 0},
        {"level", "g2a_neg", 2, 1u << nlv, 0}, {"sink", "g2a_neg", 2, 0, 1},
    };
    mf_sink half = { .u = f, .puts = fput };
    for (size_t j = 0; j < sizeof neg / sizeof neg[0]; j++) {
        err[0] = 0;
        if (mf_kernel_find_any(neg[j].nosink ? &half : &o, neg[j].fn, b4, neg[j].k, neg[j].lv,
                               err, sizeof err) != -1 || !err[0]) {
            fprintf(stderr, "g2_any_gen: refusal '%s' (#%zu) not refused\n", neg[j].why, j);
            return 1;
        }
    }

    unsigned nk = 0;
    char tab[1 << 16];
    size_t tl = 0;
    uint32_t all = (1u << nlv) - 1;
    for (unsigned s = 0; s < nsets; s++) {
        unsigned k;
        uint8_t b[3];
        if (s < NFIXED) {
            k = fixed[s].k;
            memcpy(b, fixed[s].b, 3);
        } else {
            k = 2 + rnd(2);
            for (unsigned j = 0; j < k; j++) {
                switch (rnd(4)) {
                case 0: b[j] = (uint8_t)(0x80 | rnd(128)); break;          /* high bit */
                case 1: b[j] = j ? (uint8_t)(b[j - 1] ^ (1u << rnd(8)))     /* one bit off */
                                 : (uint8_t)rnd(256); break;
                case 2: b[j] = j ? b[rnd(j)] : (uint8_t)rnd(256); break;   /* a duplicate */
                default: b[j] = (uint8_t)rnd(256);
                }
            }
        }
        /* level choices: none, each level alone, all of them */
        uint32_t choice[8];
        unsigned nc = 0;
        choice[nc++] = 0;
        for (unsigned l = 0; l < nlv; l++) choice[nc++] = 1u << l;
        choice[nc++] = all;
        for (unsigned c = 0; c < nc; c++) {
            char fn[64];
            snprintf(fn, sizeof fn, "g2a_%u", nk);
            if (mf_kernel_find_any(&o, fn, b, k, choice[c], err, sizeof err)) {
                fprintf(stderr, "g2_any_gen: kernel %u refused: %s\n", nk, err);
                return 1;
            }
            fprintf(meta, "%u\t%u\t%u,%u,%u\t%u\n", nk, k, b[0], b[1], k > 2 ? b[2] : 0,
                    (unsigned)choice[c]);
            tl += (size_t)snprintf(tab + tl, sizeof tab - tl,
                                   "    { g2a_%u, %u, { %u, %u, %u }, %uu },\n", nk, k, b[0],
                                   b[1], k > 2 ? b[2] : 0, (unsigned)choice[c]);
            if (tl >= sizeof tab - 1) { fprintf(stderr, "g2_any_gen: table overflow\n"); return 1; }
            nk++;
        }
    }
    fprintf(f, "static const struct g2a_kernel g2a_table[] = {\n%s};\n"
               "#define G2A_NKERNEL %u\n", tab, nk);
    if (fclose(f) || fclose(meta)) { perror("g2_any_gen"); return 2; }
    fprintf(stderr, "g2_any_gen: %u kernels over %u sets, %zu levels\n", nk, nsets, nlv);
    return 0;
}
