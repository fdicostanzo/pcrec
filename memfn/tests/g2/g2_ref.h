/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2, lane memfng2).
 *
 * memfn/tests/g2/g2_ref.h — the reference's interface (g2_ref.c).
 */
#ifndef G2_REF_H
#define G2_REF_H

#include <stdio.h>

#include "g2.h"

typedef struct {               /* the site's OPTIONAL items, numbered         */
    int    nitems;             /* <= G2_MAXOPT                                */
    int8_t pred_item[256];     /* -1: the predicate is REQUIRED               */
    int8_t term_item[256][G2_MAXT];
} g2_items;

extern int g2_ref_defect;      /* W1: 1 ignore end_back, 2 reverse the order,
                                  3 ignore the floor, 4 the OLD range
                                  [lo, n - end_back) for a reads-below FIND (Q-R7-1);
                                  lane g2m7 (MISMATCH): 5 the fold ignored (raw bytes
                                  compared), 6 the compare stops at reflen - 1, 7 the
                                  result a difference reports is k + 1 (driver side);
                                  lane g2m6 (strided ADVANCE, MF_SITE_ABI 8): 8 the cap
                                  counted in BYTES (span_hi / W iterations), 9 `more` strict
                                  (cursor + W < n: the last exactly-fitting block dropped),
                                  10 the terms tested in the reverse order (term W-1-i at
                                  offset i) */

void g2_ref_items(const g2_site *d, g2_items *it);

/* Q-R7-1 (memfn.h, MF_OP_FIND): is `d` a READS-BELOW FIND, one whose every
 * term reads below its candidate (offset + len <= 0 for each, len 1 for a SET
 * term)? Returns 1 and sets *E to the largest offset + len, else 0. */
int g2_ref_readsbelow(const g2_site *d, long long *E);

/* The contract's range for (n, lo): returns 1 when it is non-empty, with the
 * candidates in [lo, *hi) (hi EXCLUSIVE), else 0. A reads-below FIND takes
 * [lo, n] with c + d <= n, d = max(0, end_back + E); every other site
 * [lo, n - end_back). */
int g2_ref_range(const g2_site *d, size_t n, size_t lo, size_t *hi);

/* lane g2m7 (memfn.h MF_OP_MISMATCH): k, the least j in [0, reflen) with
 * lo + j >= n or map[s[lo + j]] != map[ref[j]]; returns 1 and sets *k on a
 * difference, 0 when the spans are EQUAL (every j in [0, reflen) agrees, so
 * reflen 0 is EQUAL). `map` is G2's OWN generated 256-byte fold map. Reads s
 * only in [lo, n) and ref only in [0, reflen). */
int g2_ref_mismatch(const uint8_t *map, const uint8_t *s, size_t n, size_t lo,
                    const uint8_t *ref, size_t reflen, size_t *k);

/* lane g2m6, the STRIDED ADVANCE (memfn.h MF_SITE_ABI 8, Q-R10-2..5): W = nterm
 * REQUIRED SET terms of preds[0], term i at offset i. From the cursor lo the loop is
 *   while ( (span_hi unbounded || cnt < span_hi)   the cap, ITERATIONS (Q-R10-5)
 *        && cursor + W <= n                         `more`, pcrec's text (G2's own)
 *        && for every i < W: s[cursor + i] in set_i )
 *       { cursor += W; cnt++; }
 * cnt starts at count_start. Returns why it stopped: G2_ST_CAP, G2_ST_MORE (the block
 * at the cursor is not wholly inside s[0..n): the first byte the kit may NOT read is
 * s[cursor]) or G2_ST_TERM (*failpos the first i whose byte is not in its set). It reads
 * s only in [lo, cursor + W) for the blocks it enters: its own reads never reach a
 * partial block. */
enum { G2_ST_CAP, G2_ST_MORE, G2_ST_TERM };
int g2_ref_stride(const g2_site *d, const uint8_t *s, size_t n, size_t lo, size_t *cursor,
                  unsigned long *cnt, int *failpos);

/* The subsets S (bit S of the result) among `alive` for which outcome `o`
 * is the contract's answer on (s, n, lo, fl). 0 = no subset explains it; why
 * then says what the first subset wanted. */
uint64_t g2_ref_check(const g2_site *d, const g2_items *it, uint64_t alive,
                      const uint8_t *s, size_t n, size_t lo, size_t fl,
                      const struct g2_out *o, char *why, size_t whyn);

#endif /* G2_REF_H */
