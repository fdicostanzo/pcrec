/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's find-any family,
 *   lane simdset).
 *
 * memfn/tests/g2/g2_any_gen.c — the GENERATOR of G2's find-any family
 * (run_g2_any.py): the family's only kit caller. It draws a GENERATED space
 * of member byte sets (K 2..3: 0x00, 0xFF, high-bit bytes, duplicates,
 * one-bit neighbours, random) and renders, for each set, the standalone
 * kernel `mf_kernel_find_any` at the kit target TARGET (unit U2: the kit
 * derives the levels from the target; run_g2_any.py runs this once per
 * target). Acting as the host, it writes the target's family guard once,
 * the headers the kernels report (`includes`, spelled by mf_include_c) at
 * file scope, and its region around the kernels (mf_family_c_of /
 * mf_target_c_of), the kit's text between the markers `G2A KIT TEXT
 * BEGIN`/`END`, through a sink offering the bracket ops. It writes
 *   DIR/g2a_kernels.c  the kernels' text, then `g2a_table[]`: per kernel its
 *                      selector, K and the bytes AS GIVEN (duplicates kept);
 *   DIR/g2a_meta.tsv   one row per kernel: id, k, bytes, target.
 * It also asks for each refusal (K 1 and 4, a bad name, a target that is
 * not a row of the kit's table, a NULL target, a sink without vprintf, a
 * sink without the bracket ops at a target admitting a level, a NULL
 * `includes`) and fails unless each is refused.
 *
 *   g2_any_gen SEED NSETS DIR TARGET
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"

static void fput(void *u, const char *s) { fputs(s, (FILE *)u); }
static void fvp(void *u, const char *f, va_list ap) { vfprintf((FILE *)u, f, ap); }
/* The bracket ops: G2 counts nothing here (G2's SIMD family measures the
 * guarded bytes); they only have to be offered and to pair. */
static int g_open;
static void bopen(void *u, int level) { (void)u; (void)level; g_open++; }
static void bclose(void *u) { (void)u; g_open--; }

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
    if (argc != 5) { fprintf(stderr, "usage: g2_any_gen SEED NSETS DIR TARGET\n"); return 2; }
    rng = strtoull(argv[1], NULL, 10);
    unsigned nsets = (unsigned)atoi(argv[2]);
    char path[4096], err[256];
    const mf_target *tg = mf_target_parse(argv[4], strlen(argv[4]), err, sizeof err);
    if (!tg) { fprintf(stderr, "g2_any_gen: %s\n", err); return 2; }
    mf_target copy = *tg;   /* the same facts, not a row: refused */
    snprintf(path, sizeof path, "%s/g2a_kernels.c", argv[3]);
    FILE *out = fopen(path, "w");
    snprintf(path, sizeof path, "%s/g2a_meta.tsv", argv[3]);
    FILE *meta = fopen(path, "w");
    char *kit = NULL;
    size_t kitlen = 0;
    FILE *f = open_memstream(&kit, &kitlen);   /* the kit's text, held until its
                                                  headers are known */
    if (!out || !meta || !f) { perror("g2_any_gen"); return 2; }
    mf_sink o = { .u = f, .puts = fput, .vprintf = fvp, .simd_open = bopen, .simd_close = bclose };
    uint32_t inc = 0, one = 0;

    /* the refusals: each must be refused, with a text */
    uint8_t b4[4] = {1, 2, 3, 4};
    /* nosink: 1 a sink without vprintf, 2 one without the bracket ops (at
       the x86-64 target, which admits a level whatever TARGET is) */
    const mf_target *lv_tg = mf_target_parse("x86-64", 6, NULL, 0);
    struct { const char *why, *fn; unsigned k; const mf_target *t; int nosink, noinc; } neg[] = {
        {"k 1", "g2a_neg", 1, tg, 0, 0}, {"k 4", "g2a_neg", 4, tg, 0, 0},
        {"name", "2bad", 2, tg, 0, 0}, {"name", "a b", 2, tg, 0, 0},
        {"target copy", "g2a_neg", 2, &copy, 0, 0}, {"target NULL", "g2a_neg", 2, NULL, 0, 0},
        {"sink", "g2a_neg", 2, tg, 1, 0}, {"no brackets", "g2a_neg", 2, lv_tg, 2, 0},
        {"includes NULL", "g2a_neg", 2, tg, 0, 1},
    };
    mf_sink half = { .u = f, .puts = fput };
    mf_sink nobr = { .u = f, .puts = fput, .vprintf = fvp };
    for (size_t j = 0; j < sizeof neg / sizeof neg[0]; j++) {
        err[0] = 0;
        mf_sink *sk = neg[j].nosink == 1 ? &half : neg[j].nosink == 2 ? &nobr : &o;
        if (mf_kernel_find_any(sk, neg[j].fn, b4, neg[j].k, neg[j].t, neg[j].noinc ? NULL : &one,
                               err, sizeof err) != -1 || !err[0]) {
            fprintf(stderr, "g2_any_gen: refusal '%s' (#%zu) not refused\n", neg[j].why, j);
            return 1;
        }
    }

    /* the refusals wrote nothing (held to it below): the kit's text starts here */
    fflush(f);
    if (kitlen) { fprintf(stderr, "g2_any_gen: a refusal wrote %zu bytes\n", kitlen); return 1; }
    unsigned nk = 0;
    char tab[1 << 16];
    size_t tl = 0;
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
        char fn[64];
        snprintf(fn, sizeof fn, "g2a_%u", nk);
        if (mf_kernel_find_any(&o, fn, b, k, tg, &one, err, sizeof err) || g_open) {
            fprintf(stderr, "g2_any_gen: kernel %u refused (%s) or left a bracket open\n", nk, err);
            return 1;
        }
        inc |= one;
        fprintf(meta, "%u\t%u\t%u,%u,%u\t%s\n", nk, k, b[0], b[1], k > 2 ? b[2] : 0, tg->name);
        tl += (size_t)snprintf(tab + tl, sizeof tab - tl, "    { g2a_%u, %u, { %u, %u, %u } },\n",
                               nk, k, b[0], b[1], k > 2 ? b[2] : 0);
        if (tl >= sizeof tab - 1) { fprintf(stderr, "g2_any_gen: table overflow\n"); return 1; }
        nk++;
    }
    if (fclose(f)) { perror("g2_any_gen"); return 2; }
    /* the host's frame: the guard, the headers at file scope (review
       2026-11-08 r5 X-1), the region around the kit's text */
    if (tg->family) fputs(mf_family_c_of(tg->family)->guard, out);
    for (uint32_t bit = 1; bit; bit <<= 1) {
        if (!(inc & bit)) continue;
        const char *line = mf_include_c(bit);
        if (!line) { fprintf(stderr, "g2_any_gen: include bit 0x%x has no spelling\n", (unsigned)bit); return 1; }
        fputs(line, out);
    }
    fputs(mf_target_c_of(tg)->region_open, out);
    fputs("/* G2A KIT TEXT BEGIN */\n", out);
    fwrite(kit, 1, kitlen, out);
    free(kit);
    fputs("/* G2A KIT TEXT END */\n", out);
    fputs(mf_target_c_of(tg)->region_close, out);
    fprintf(out, "static const struct g2a_kernel g2a_table[] = {\n%s};\n"
                 "#define G2A_NKERNEL %u\n", tab, nk);
    if (fclose(out) || fclose(meta)) { perror("g2_any_gen"); return 2; }
    fprintf(stderr, "g2_any_gen: %u kernels over %u sets at %s\n", nk, nsets, tg->name);
    return 0;
}
