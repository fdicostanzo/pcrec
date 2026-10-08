/* tests/possessify/ctx_admits_check.c -- [ART-POSS-ARMS] (docs/design/
 * poss_arms.md section 7 "ctx_admits", section 8.2's A-F3 note): AN
 * EXHAUSTIVE MODEL CHECK of `pcrec_poss_ctx_admits`, arm A's table-shaped
 * primitive, exported for exactly this file.
 *
 * THE UNIVERSE. All 16 truth tables `fn` x the 3 NON-EMPTY left-polarity
 * masks `pmask` (bit 0: the left character is not in C, bit 1: it is) x a
 * set of gate sets C. The C set deliberately includes the shapes each clause
 * of the rule exists for: the empty set; all 256 bytes; every code point; the
 * ASCII word set; single bytes at the ends of the byte tier; a set with
 * members ONLY above 0xFF ({U+0100}), which is the A-F3 case; a set
 * straddling the 0xFF/0x100 edge; a mixed set (bytes AND beyond the tier);
 * and seeded random sets. 16 x 3 x |C| cells, every one compared.
 *
 * THE MODEL IS WRITTEN FROM THE RULE, NOT FROM THE FUNCTION. It never builds
 * a bitset by walking intervals the way the function does: it asks, byte by
 * byte, "is this byte in C" with a plain linear scan over the interval list
 * (the list is never assumed sorted by the model), and derives the admitted
 * next-memberships Q(P) by a direct existential over P and the table's bit
 * (p << 1 | q). Then, per the rule:
 *   - Q(P) = {0,1}: NO narrowing (the function returns false);
 *   - Q(P) = {}   : the gate never passes: narrowed to the EMPTY set (true,
 *                   out all zero);
 *   - Q(P) = {q}  : S = { byte <= 0xFF : (byte in C) == q }; if S is EMPTY
 *                   while Q(P) is not, the function WIDENS (returns false)
 *                   -- section 2.1's truncation rule, because a member above
 *                   0xFF is not representable in a byte set and an empty S
 *                   would otherwise claim "nothing can follow" when
 *                   something above the tier can; else (true, out == S).
 *
 * K35 / non-vacuity: the four outcomes (no-narrow, narrowed-empty, narrowed,
 * widen-for-empty-S) must each occur a nonzero number of times, and the
 * per-outcome counts are printed, so a model whose universe silently
 * excluded a branch cannot read as green. The A-F3 unit cell is also an
 * explicit named cell below, not left to the sweep.
 *
 * FAILING DIRECTION (what each plant would flip): dropping the widen-on-empty
 * rule turns the A-F3 cell and every {U+0100}/qok[1] cell into a (true, {})
 * answer; truncating at 0xFE or counting the bytes of C above 0xFF into the
 * byte set flips the straddle cells; swapping the q sense inverts every
 * single-q cell; reading `pmask` bits the wrong way round flips the
 * asymmetric tables (fn = 0x4, 0x2 ...).
 *
 * Deterministic: seeded constant PRNG. Exit 0 = all agree. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "core/internal.h"

typedef struct { const char *name; PcrecCpRange iv[16]; int n; } CSet;

static int in_c(const CSet *c, unsigned b)
{
    for (int i = 0; i < c->n; i++)
        if (b >= c->iv[i].lo && b <= c->iv[i].hi) return 1;
    return 0;
}

static unsigned long long rng_state = 0x9E3779B97F4A7C15ull;
static unsigned rnd(void)
{
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return (unsigned)(rng_state >> 16);
}

static int cnt_nonarrow, cnt_empty, cnt_narrow, cnt_widen;
static int failures, cells;

/* Evaluate the model for (fn, c, pmask) and compare with the function. */
static void check(uint8_t fn, const CSet *c, unsigned pmask, const char *tag)
{
    int qadm[2] = { 0, 0 };
    for (unsigned p = 0; p < 2; p++)
        for (unsigned q = 0; q < 2; q++)
            if (((pmask >> p) & 1u) && ((fn >> ((p << 1) | q)) & 1u))
                qadm[q] = 1;

    uint8_t out[32];
    memset(out, 0xA5, sizeof out);            /* poison: a function that skips the write is caught */
    bool got = pcrec_poss_ctx_admits(fn, c->iv, c->n, pmask, out);
    cells++;

    bool want_ret; uint8_t want[32];
    memset(want, 0, sizeof want);
    int compare_out = 1;
    if (qadm[0] && qadm[1]) {
        want_ret = false; compare_out = 0; cnt_nonarrow++;
    } else if (!qadm[0] && !qadm[1]) {
        want_ret = true; cnt_empty++;
    } else {
        int q = qadm[1];                       /* the one admitted next-membership */
        int any = 0;
        for (unsigned b = 0; b < 256; b++)
            if (in_c(c, b) == q) { want[b >> 3] |= (uint8_t)(1u << (b & 7)); any = 1; }
        if (any) { want_ret = true; cnt_narrow++; }
        else     { want_ret = false; compare_out = 0; cnt_widen++; }
    }
    if (got != want_ret || (compare_out && memcmp(out, want, 32) != 0)) {
        failures++;
        if (failures <= 20)
            fprintf(stderr, "FAIL %s: fn=0x%02x C=%s pmask=%u: got %s, want %s%s\n",
                    tag, fn, c->name, pmask, got ? "true" : "false",
                    want_ret ? "true" : "false",
                    (got == want_ret && compare_out) ? " (out set differs)" : "");
    }
}

int main(void)
{
    static CSet sets[64];
    int ns = 0;
#define ADD0(nm)            do { sets[ns].name = nm; sets[ns].n = 0; ns++; } while (0)
#define ADD1(nm, a, b)      do { sets[ns].name = nm; sets[ns].iv[0] = (PcrecCpRange){a, b}; sets[ns].n = 1; ns++; } while (0)
    ADD0("empty");
    ADD1("all-256-bytes", 0, 0xFF);
    ADD1("every-codepoint", 0, 0x10FFFF);
    ADD1("single-0x00", 0, 0);
    ADD1("single-a", 'a', 'a');
    ADD1("single-0xFF", 0xFF, 0xFF);
    ADD1("only-U+0100", 0x100, 0x100);               /* A-F3: members ONLY above 0xFF */
    ADD1("only-above-tier-range", 0x100, 0x10FFFF);
    ADD1("straddle-0xFE-0x101", 0xFE, 0x101);
    ADD1("digits", '0', '9');
    /* ASCII word set \w */
    sets[ns].name = "ascii-word"; sets[ns].n = 4;
    sets[ns].iv[0] = (PcrecCpRange){'0', '9'}; sets[ns].iv[1] = (PcrecCpRange){'A', 'Z'};
    sets[ns].iv[2] = (PcrecCpRange){'_', '_'}; sets[ns].iv[3] = (PcrecCpRange){'a', 'z'};
    ns++;
    /* mixed: bytes AND beyond the tier */
    sets[ns].name = "mixed-a-z-and-U+0100-0200"; sets[ns].n = 2;
    sets[ns].iv[0] = (PcrecCpRange){'a', 'z'}; sets[ns].iv[1] = (PcrecCpRange){0x100, 0x200};
    ns++;
    /* every byte except one, plus a code point above the tier */
    sets[ns].name = "all-but-0x80-and-U+0100"; sets[ns].n = 3;
    sets[ns].iv[0] = (PcrecCpRange){0, 0x7F}; sets[ns].iv[1] = (PcrecCpRange){0x81, 0xFF};
    sets[ns].iv[2] = (PcrecCpRange){0x100, 0x100};
    ns++;
    /* seeded random sets: sorted, disjoint, non-adjacent intervals over 0..0x400 */
    char (*names)[24] = malloc(40 * sizeof *names);
    for (int r = 0; r < 40; r++) {
        CSet *s = &sets[ns];
        snprintf(names[r], sizeof names[r], "random-%d", r);
        s->name = names[r]; s->n = 0;
        unsigned pos = rnd() % 8;
        int k = 1 + (int)(rnd() % 5);
        for (int i = 0; i < k && pos <= 0x400 && s->n < 16; i++) {
            unsigned lo = pos + rnd() % 60;
            unsigned hi = lo + rnd() % 90;
            s->iv[s->n++] = (PcrecCpRange){lo, hi};
            pos = hi + 2 + rnd() % 60;
        }
        ns++;
    }

    for (int t = 0; t < 16; t++)
        for (unsigned pm = 1; pm <= 3; pm++)
            for (int i = 0; i < ns; i++)
                check((uint8_t)t, &sets[i], pm, "sweep");

    /* A-F3's unit cell, NAMED: C = {U+0100}; (?=C) has fn = 0xA (the answer
     * is q regardless of p, bit (p<<1|1) set). Q(P) = {1}, S(P) = {} (nothing
     * of C in the byte tier), so the function MUST WIDEN, never claim "empty
     * narrowing". Its negative sibling (?!C), fn = 0x5, admits q = 0: S is all
     * 256 bytes and narrows. */
    {
        CSet af3 = { "U+0100 (A-F3)", { { 0x100, 0x100 } }, 1 };
        uint8_t out[32];
        for (unsigned pm = 1; pm <= 3; pm++) {
            bool r = pcrec_poss_ctx_admits(0xA, af3.iv, af3.n, pm, out);
            cells++;
            if (r) { failures++; fprintf(stderr, "FAIL A-F3: (?=U+0100) pmask=%u narrowed (returned true), must widen\n", pm); }
            r = pcrec_poss_ctx_admits(0x5, af3.iv, af3.n, pm, out);
            cells++;
            int full = 1;
            for (int i = 0; i < 32; i++) if (out[i] != 0xFF) full = 0;
            if (!r || !full) { failures++; fprintf(stderr, "FAIL A-F3 sibling: (?!U+0100) pmask=%u must narrow to all 256 bytes\n", pm); }
        }
    }
    free(names);

    printf("ctx_admits: %d cells (16 fn x 3 pmask x %d C + A-F3 unit cells): "
           "no-narrow %d, narrowed-empty %d, narrowed %d, widen-on-empty-S %d\n",
           cells, ns, cnt_nonarrow, cnt_empty, cnt_narrow, cnt_widen);
    if (!cnt_nonarrow || !cnt_empty || !cnt_narrow || !cnt_widen) {
        fprintf(stderr, "FAIL: a rule branch was never exercised (K35)\n");
        failures++;
    }
    if (failures) { fprintf(stderr, "ctx_admits: %d FAILURES\n", failures); return 1; }
    printf("ctx_admits: all cells agree with the model\n");
    return 0;
}
