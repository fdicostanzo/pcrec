/* span_cards/slot/gen.c — THE SUBJECT GENERATOR (span_cards.md §2.3, §3.2): seeded, the expectation's only
 * source. The answer gate compares what an arm finds with what this file planted, before any clock.
 *   find   one MISS TEXT shared by every find arm: bytes drawn from outside every find form's members
 *          (slot_find_members, the forms' own facts via link.py), so the forms read the same bytes and
 *          differ only by their hits; hits planted periodic (every gap-th byte) or random (E distinct
 *          uniform positions), E = len / gap exactly (§2.3), split one (hit[0]) or alt (alternating).
 *   cmp    candidates at S i + j (S = CAND_STRIDE, j seeded in [0, S - L)), E = len / S; a candidate passes with
 *          probability 0 (p0) or 1/2 (p50); a failing one differs at ONE uniformly seeded position; filler
 *          bytes uniform; the masked-off bits of a run's passing bytes random.
 *   art    the subject file, its expectation from its `expect` file (python re's answer, j1/ and enter/).
 * Seeds: (arm's subject family, length, subject index). A twin draws its arm's subjects. A find base
 * (landing miss) draws the shared miss text without hits. A verify base (null) draws the p0 subjects of its
 * class's instance (its run, mask or members), not its p50 arm's: the base is a different subject from the
 * p50 row it is subtracted from (the null loop reads the candidate's first byte only, so its cost does not
 * depend on the pass rate; r9 SLOT-14). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "slot.h"

static uint64_t sm(uint64_t *x)                 /* splitmix64 */
{
    uint64_t z = (*x += 0x9e3779b97f4a7c15ull);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebull;
    return z ^ (z >> 31);
}

uint64_t fnv_pos(uint64_t h, uint64_t pos)
{
    for (int i = 0; i < 8; i++) {
        h ^= (pos >> (8 * i)) & 0xff;
        h *= 1099511628211ull;
    }
    return h;
}

static int in(const unsigned char *bm, unsigned b) { return (bm[b >> 3] >> (b & 7)) & 1; }


void gen_subject(const arm *a, uint32_t len, uint32_t idx, unsigned char *buf, uint32_t *cand, size_t *nc,
                 uint64_t *count, uint64_t *sum, uint64_t *h, int sentinel)
{
    *count = *sum = 0;
    *h = FNV0;
    *nc = 0;
    if (a->kind == K_ART) {
        FILE *f = fopen(a->subj, "rb");
        size_t got = f ? fread(buf, 1, len, f) : 0;
        if (f) fclose(f);
        if (got != len) { fprintf(stderr, "gen: %s: %zu of %u bytes\n", a->subj, got, len); exit(2); }
        FILE *e = fopen(a->expect, "r");
        unsigned long long c = 0, s = 0, x = 0;
        if (!e || fscanf(e, "%llu %llu %llx", &c, &s, &x) != 3) { fprintf(stderr, "gen: %s\n", a->expect); exit(2); }
        fclose(e);
        *count = c; *sum = s; *h = x;
        return;
    }
    if (a->kind == K_FIND) {
        uint64_t st = 0x5eed0000ull ^ ((uint64_t)len << 20) ^ idx;
        for (uint32_t i = 0; i < len; i++) {
            unsigned b;
            do b = (unsigned)(sm(&st) & 0xff); while (in(slot_find_members, b));
            buf[i] = (unsigned char)b;
        }
        if (a->landing == LD_MISS && !sentinel) return;
        uint32_t E = a->landing == LD_MISS ? 0 : len / a->gap;
        uint64_t sh = 0x417e0000ull ^ ((uint64_t)a->gap << 32) ^ ((uint64_t)a->landing << 40) ^ idx;
        unsigned char *mark = calloc(len, 1);
        if (!mark) { fprintf(stderr, "gen: out of memory (%u-byte hit map)\n", len); exit(2); }
        if (a->landing == LD_PERIODIC) {
            for (uint32_t k = 0; k < E; k++) mark[(uint64_t)k * a->gap + a->gap - 1] = 1;
        } else if (a->landing == LD_RANDOM) {
            for (uint32_t k = 0; k < E; ) {
                uint32_t p = (uint32_t)(sm(&sh) % len);
                if (!mark[p]) { mark[p] = 1; k++; }
            }
        }
        if (sentinel)
            mark[len - 1] = 1;
        uint32_t k = 0;
        for (uint32_t p = 0; p < len; p++) {
            if (!mark[p]) continue;
            buf[p] = a->hit[a->split ? (k & 1) : 0];
            k++;
            (*count)++;
            *sum += p;
            *h = fnv_pos(*h, p);
        }
        free(mark);
        return;
    }
    /* cmp and null: candidates every CAND_STRIDE bytes */
    uint64_t st = 0xc0de0000ull ^ ((uint64_t)len << 20) ^ ((uint64_t)a->pass << 48) ^ idx;
    for (uint32_t i = 0; i < len; i++) buf[i] = (unsigned char)(sm(&st) & 0xff);
    int L = a->L ? a->L : 1;
    uint32_t E = len / CAND_STRIDE;
    for (uint32_t i = 0; i < E; i++) {
        uint32_t pos = i * CAND_STRIDE + (uint32_t)(sm(&st) % (CAND_STRIDE - (uint32_t)L));
        cand[i] = pos;
        int passes = a->pass == 50 && (sm(&st) & 1);
        if (sentinel && i == E - 1)
            passes = 1;
        int bad = passes ? -1 : (int)(sm(&st) % (uint64_t)L);
        for (int j = 0; j < L; j++) {
            unsigned b;
            if (a->L) {                     /* a run: under the mask equal to the run byte, or not */
                do b = (unsigned)(sm(&st) & 0xff);
                while (((b & a->mask[j]) == (a->run[j] & a->mask[j])) == (j == bad));
            } else {                        /* a set test: a member, or not */
                do b = (unsigned)(sm(&st) & 0xff); while (in(a->member, b) == (j == bad));
            }
            buf[pos + (uint32_t)j] = (unsigned char)b;
        }
        if (passes && a->kind == K_CMP) {
            (*count)++;
            *sum += i;
            *h = fnv_pos(*h, i);
        }
    }
    *nc = E;
    if (a->kind == K_NULL) { *count = E; *sum = 0; *h = FNV0; }
}
