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

/* Which member of the necessary SET the emitted `memchr` tests: the rarest
 * under the prior, ties broken by the threaded rightmost member when it is
 * among the minima and by the largest such byte otherwise.
 *
 * The tiebreak's second clause exists because `rightmost` is not always
 * among the minima, and a rule that silently fell back to "whichever bit a
 * loop found first" is what `rb_intersect` already refuses. */
int pcrec_find_set_pick(const unsigned char bits[32], int rightmost,
                        bool bytekey)
{
    int b, best = -1;
    unsigned lo = 0;
    if (!bytekey || rightmost < 0) return rightmost;
    for (b = 255; b >= 0; b--) {
        unsigned p;
        if (!(bits[b >> 3] & (unsigned char)(1u << (b & 7)))) continue;
        p = pcrec_byte_freq_ppm(b);
        if (best < 0 || p < lo) { lo = p; best = b; }
    }
    /* Scanning DOWN above already leaves `best` as the LARGEST of the minima,
     * so only the "the rightmost member is among them" clause needs stating. */
    if (pcrec_byte_freq_ppm(rightmost) == lo) return rightmost;
    return best;
}

/* Which member of the RUN the emitted `memchr` tests: the rarest under the
 * prior, ties to the LEFTMOST — and the set pick's own fallback (rightmost)
 * where the prior does not apply. The per-candidate cost of the whole run
 * check is the number of occurrences of THIS byte in the window, which is
 * why the choice is not cosmetic.
 *
 * [OPT-REQRUN-ENC] The fallback WAS leftmost, and pcrec-bench's O-60 finding
 * falsified it under `-e utf8`: a run's LEFTMOST member is a lead byte
 * whenever the run opens mid-character, shared by every character in that
 * script block (measured: 12.0%/20.7% of the corpus/bench RUN-path artifacts,
 * docs/dev/optloop/reqrunenc_census.md). A run's last byte can be a lead byte
 * only if the run is truncated mid-character, which the census found in ZERO
 * of 912 real `-e utf8` runs, so the rightmost rule closes it with no
 * byte-range logic (D77). */
int pcrec_find_run_scan_index(const unsigned char *bytes, int n, bool bytekey)
{
    int i, best = 0;
    unsigned lo;
    if (!bytekey) return n - 1;
    lo = pcrec_byte_freq_ppm(bytes[0]);
    for (i = 1; i < n; i++) {
        unsigned p = pcrec_byte_freq_ppm(bytes[i]);
        if (p < lo) { lo = p; best = i; }
    }
    return best;
}

/* Where a run longer than `PCREC_MAX_REQ_RUN_EMIT` is TRUNCATED to: the start
 * of the window of that length containing `idx` whose bytes sum to the lowest
 * prior, ties to the leftmost, and the leftmost such window where the prior
 * does not apply.
 *
 * The scan member is in every candidate window by construction, so its own
 * ppm is a constant of the comparison and no term has to be excluded. */
int pcrec_find_run_window_start(const unsigned char *bytes, int n, int idx,
                                bool bytekey)
{
    int lo_s = idx - (PCREC_MAX_REQ_RUN_EMIT - 1), hi_s = idx;
    int s, best;
    unsigned long long lo = 0;
    if (lo_s < 0) lo_s = 0;
    if (hi_s > n - PCREC_MAX_REQ_RUN_EMIT) hi_s = n - PCREC_MAX_REQ_RUN_EMIT;
    best = lo_s;
    if (!bytekey) return best;
    for (s = lo_s; s <= hi_s; s++) {
        unsigned long long t = 0;
        int k;
        for (k = 0; k < PCREC_MAX_REQ_RUN_EMIT; k++)
            t += pcrec_byte_freq_ppm(bytes[s + k]);
        if (s == lo_s || t < lo) { lo = t; best = s; }
    }
    return best;
}
