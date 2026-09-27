/* src/core/findings.c — THE FINDINGS SEAM: the byte-rate readers, beside the
 * rate they read ([FINDINGS] B1 = [PATFACTS] step 3.1;
 * docs/design/findings/design.md §6, docs/design/patfacts/design.md §4.2.2
 * carve-out (b), D122/D126).
 *
 * WHAT A RATE READER IS. Every member of a necessary set and every window of
 * a necessary run is SOUND for the emitted pre-check (`src/facts/req.c`
 * proves them), so which one is scanned moves a SPEED and nothing else. The
 * one that pays is the one a subject is least likely to contain, and a
 * byte-frequency prior orders bytes by exactly that ([OPT-FREQPICK],
 * docs/design/reqbyte_freq_pick.md). PCRE2's rightmost rule survives as the
 * TIEBREAK, and as the whole answer where the prior does not apply.
 *
 * THE PRIOR IS READ ONLY UNDER THE `byte` ENCODING. The shipped table is
 * keyed to `byte` by its own contents: its 0x80-0xFF half sits at the 2 ppm
 * floor, so under `-e utf8` an argmin over it would prefer a shared UTF-8
 * lead byte (`é@` lowers to {0xC3, 0xA9, 0x40} and the argmin would take
 * 0xC3 over a genuinely rare `@`). Under every other encoding the readers
 * answer the rightmost member and the leftmost window — byte for byte the
 * answer before [OPT-FREQPICK] (reqbyte_freq_pick.md §3, Frank's ruling
 * 2026-09-22), and since [OPT-REQRUN-ENC] the run's scan member too.
 *
 * A RUN LONGER THAN `PCREC_MAX_REQ_RUN_EMIT` IS TRUNCATED, NEVER SPLIT into
 * two compares (Frank's ruling of 2026-09-22): to the window of that length
 * containing the scan member whose bytes sum to the lowest prior, ties
 * leftmost. A second compare would be a second mechanism with its own cost
 * question and no measured need (D77).
 *
 * These moved here from `src/opt/reqbyte.c` (deleted) so that the rate and
 * every reader of it sit in one file. */

#include "core/internal.h"
#include "core/findings.h"

/* ---- THE ACCESSOR ---------------------------------------------------------
 *
 * THE GATE LIVES HERE AND NOWHERE ELSE (D122 addendum 2 (3)): whether a rate
 * applies to this compile is decided once, by this function, and every reader
 * receives either a table or NULL and hands it to a primitive untested. */

const uint32_t *pcrec_find_byte_rate(Ctx *cx)
{
    PcrecFindRec *fr = &cx->job->find;
    if (!fr->byte_rate_asked) {
        fr->byte_rate_asked = true;
        if (cx->opt->encoding == PCREC_ENC_BYTE) {
            for (int b = 0; b < 256; b++)
                fr->byte_rate[b] = pcrec_byte_freq_ppm(b);
            fr->byte_rate_have = true;
        }
    }
    return fr->byte_rate_have ? fr->byte_rate : NULL;
}

/* ---- THE PRIMITIVES: one per rate QUESTION KIND, its NONE answer inside ----
 *
 * [D126 Q4] A uniform table substituted for NONE would be right for MASS
 * only: for PICK it answers `cand[0]`, which is the set pick's rightmost but
 * the run's LEFTMOST (R13's defect again), and for COMPARE it answers `true`
 * for every pair, a density claim no data supports. So each kind states its
 * own, once, here (design §6.1). */

/* The uniform rate's mass for `k` bytes: floor(k * 10^6 / 256). */
static uint32_t uniform_mass(int k)
{
    return (uint32_t)((unsigned long long)k * 1000000u / 256u);
}

int pcrec_find_pick(const uint32_t *rate, const unsigned char *cand, int n,
                    int rightmost)
{
    int i, best = 0;
    if (!rate) return rightmost;
    for (i = 1; i < n; i++)
        if (rate[cand[i]] < rate[cand[best]]) best = i;
    return best;
}

bool pcrec_find_no_commoner(const uint32_t *rate, int p, int q)
{
    if (!rate) return false;
    return rate[p] <= rate[q];
}

uint32_t pcrec_find_set_mass(const uint32_t *rate, const uint8_t set[256])
{
    unsigned long long t = 0;
    int k = 0;
    for (int b = 0; b < 256; b++) if (set[b]) { k++; if (rate) t += rate[b]; }
    if (!rate) t = uniform_mass(k);
    return t > 1000000u ? 1000000u : (uint32_t)t;
}

uint32_t pcrec_find_seq_mass(const uint32_t *rate, const unsigned char *bytes,
                             int n)
{
    unsigned long long t = 0;
    if (!rate) return uniform_mass(n);
    for (int i = 0; i < n; i++) t += rate[bytes[i]];
    return (uint32_t)t;
}

/* ---- THE RATE READERS: each builds a candidate order and asks one primitive */

/* Which member of the necessary SET the emitted `memchr` tests. The order
 * `[rightmost, the other members 255..0]` IS the tie rule: ties go to the
 * threaded rightmost member when it is among the minima, and to the largest
 * such byte otherwise — the rule a loop that silently took "whichever bit it
 * found first" would break, and that `rb_intersect` already refuses. */
int pcrec_find_set_pick(const uint32_t *rate, const unsigned char bits[32],
                        int rightmost)
{
    unsigned char cand[256];
    int n = 0;
    if (rightmost < 0) return -1;
    cand[n++] = (unsigned char)rightmost;
    for (int b = 255; b >= 0; b--)
        if (b != rightmost && (bits[b >> 3] & (unsigned char)(1u << (b & 7))))
            cand[n++] = (unsigned char)b;
    return cand[pcrec_find_pick(rate, cand, n, 0)];
}

/* Which member of the RUN the emitted `memchr` tests: the run in order, so
 * ties go to the LEFTMOST, and the positional rightmost is the NONE answer.
 * The per-candidate cost of the whole run check is the number of occurrences
 * of THIS byte in the window, which is why the choice is not cosmetic.
 *
 * [OPT-REQRUN-ENC] The NONE answer WAS the leftmost, and pcrec-bench's O-60
 * finding falsified it under `-e utf8`: a run's LEFTMOST member is a lead
 * byte whenever the run opens mid-character, shared by every character in
 * that script block (measured: 12.0%/20.7% of the corpus/bench RUN-path
 * artifacts, docs/dev/optloop/reqrunenc_census.md). A run's last byte can be
 * a lead byte only if the run is truncated mid-character, which the census
 * found in ZERO of 912 real `-e utf8` runs, so the rightmost rule closes it
 * with no byte-range logic (D77). */
int pcrec_find_run_scan_index(const uint32_t *rate, const unsigned char *bytes,
                              int n)
{
    return pcrec_find_pick(rate, bytes, n, n - 1);
}

/* Where a run longer than `PCREC_MAX_REQ_RUN_EMIT` is TRUNCATED to: the start
 * of the window of that length containing `idx` with the lowest mass, ties
 * to the leftmost by the strict `<` — so under NONE, where every window's
 * mass is equal, the leftmost.
 *
 * The scan member is in every candidate window by construction, so its own
 * rate is a constant of the comparison and no term has to be excluded. */
int pcrec_find_run_window_start(const uint32_t *rate,
                                const unsigned char *bytes, int n, int idx)
{
    int lo_s = idx - (PCREC_MAX_REQ_RUN_EMIT - 1), hi_s = idx;
    int s, best;
    uint32_t lo = 0;
    if (lo_s < 0) lo_s = 0;
    if (hi_s > n - PCREC_MAX_REQ_RUN_EMIT) hi_s = n - PCREC_MAX_REQ_RUN_EMIT;
    best = lo_s;
    for (s = lo_s; s <= hi_s; s++) {
        uint32_t t = pcrec_find_seq_mass(rate, bytes + s, PCREC_MAX_REQ_RUN_EMIT);
        if (s == lo_s || t < lo) { lo = t; best = s; }
    }
    return best;
}

/* The offset-k selection's per-set cost input (src/opt/prefix_k.c): the
 * prior summed over every member of `set`, capped at 1,000,000 (the whole
 * alphabet's own total). */
unsigned pcrec_find_set_ppm(Ctx *cx, const uint8_t set[256])
{
    unsigned t = 0;
    (void)cx;
    for (int b = 0; b < 256; b++) if (set[b]) t += pcrec_byte_freq_ppm(b);
    return t > 1000000u ? 1000000u : t;
}
