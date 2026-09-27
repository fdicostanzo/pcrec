/* src/core/findings.h — THE FINDINGS SEAM: the byte-rate accessor, the rate
 * primitives, and the rate READERS that sit beside them ([FINDINGS] B1 =
 * [PATFACTS] step 3.1; docs/design/findings/design.md §6, D122/D126 Q4).
 *
 * Internal. A pass that wants a byte rate reaches it through this header and
 * nothing else: there is no rate table anywhere but `src/core/findings.c`
 * (design §11.7), and no reader outside that file tests a rate pointer. */
#ifndef PCREC_FINDINGS_H
#define PCREC_FINDINGS_H

#include <stdbool.h>

/* ---- THE RATE READERS (design §6.1 "Where the rate readers live") --------
 *
 * Each is a SPEED choice among members a derivation already proved
 * necessary, so the worst a bad choice costs is speed on some subject. They
 * take plain byte arrays, so this layer needs no facts-layer type; the
 * derived facts in `src/facts/req.c` call them. */

/* Which member of a necessary SET (`bits`, 256-bit membership) the emitted
 * `memchr` tests: the rarest under the prior, ties to the threaded
 * `rightmost` member when it is among the minima and to the largest such
 * byte otherwise; `rightmost` itself where the prior does not apply. -1
 * exactly when the set is empty (`rightmost < 0`). */
int pcrec_find_set_pick(const unsigned char bits[32], int rightmost,
                        bool bytekey);

/* Which member of a necessary RUN (`bytes[0..n)`, n >= 2) the emitted
 * `memchr` tests: the rarest under the prior, ties to the leftmost; the
 * RIGHTMOST where the prior does not apply. */
int pcrec_find_run_scan_index(const unsigned char *bytes, int n, bool bytekey);

/* Where a run longer than `PCREC_MAX_REQ_RUN_EMIT` is truncated to: the start
 * of the window of that length containing `idx` whose bytes sum to the lowest
 * prior, ties to the leftmost; the leftmost such window where the prior does
 * not apply. */
int pcrec_find_run_window_start(const unsigned char *bytes, int n, int idx,
                                bool bytekey);

#endif /* PCREC_FINDINGS_H */
