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
                                  3 ignore the floor                          */

void g2_ref_items(const g2_site *d, g2_items *it);

/* The subsets S (bit S of the result) among `alive` for which outcome `o`
 * is the contract's answer on (s, n, lo, fl). 0 = no subset explains it; why
 * then says what the first subset wanted. */
uint64_t g2_ref_check(const g2_site *d, const g2_items *it, uint64_t alive,
                      const uint8_t *s, size_t n, size_t lo, size_t fl,
                      const struct g2_out *o, char *why, size_t whyn);

#endif /* G2_REF_H */
