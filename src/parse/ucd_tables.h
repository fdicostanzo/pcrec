/* ucd_tables.h — THE ONE INTERFACE to the Unicode property tables
 * ([DATA-PLAN] A1).
 *
 * `third_party/ucd-16.0.0/generate.py` compiles the vendored UCD into a
 * generated table; `ucd_tables.c` is the ONLY file that includes it or knows
 * how it is laid out.  Everything else — the `\p{..}` scanner, module `ucp`,
 * the code-language and named-group tables, the tests — asks the questions
 * below and gets back interval lists, names and a version string.  A caller
 * never sees an offset, a blob or an encoding, and no caller may name the
 * generated file or its symbols (`tests/core/run_core_tests.sh`'s ucd-wall
 * check fails the build if one does).
 *
 * A "set" is a sorted, disjoint, NON-ADJACENT code-point interval list, the
 * invariant `src/core/cpset.c` keeps, so a result can go straight to
 * `pcrec_cpset_add_set`.
 *
 * A "row" is one (name, namespace mask) entry.  Names are PRE-NORMALISED
 * (upper case; space, tab, hyphen, underscore removed), the form
 * `mod_uprops.c`'s scanner accumulates.  Row ORDER is the writer's and is not
 * a contract.
 */
#ifndef PCREC_UCD_TABLES_H
#define PCREC_UCD_TABLES_H

#include <stdbool.h>
#include <stddef.h>

#include "core/internal.h"   /* Arena, PcrecCpRange */

/* The NAMESPACE a `\p` body's prefix selects: none, `sc=`, `scx=`, `bc=`,
 * `blk=`, `age=`.  A row answers in a MASK of these.  The generator writes the
 * same numbers; ucd_tables.c asserts they agree. */
#define PCREC_UCD_NS_BARE 1u
#define PCREC_UCD_NS_SC   2u
#define PCREC_UCD_NS_SCX  4u
#define PCREC_UCD_NS_BC   8u    /* Bidi_Class, short names */
#define PCREC_UCD_NS_BLK  16u   /* pcrec extension: Block */
#define PCREC_UCD_NS_AGE  32u   /* pcrec extension: Age */

/* The first row named `name[0..len)` whose mask intersects `ns`, its set (the
 * `-i` set when `caseless`).  NULL if there is no such row; a row whose set is
 * empty answers non-NULL with `*n == 0`.  The array is allocated from `a` and
 * lives as long as the arena.  Cost: a scan of the rows plus a decode linear
 * in `*n` (about 2 microseconds for `\p{L}`'s 677 intervals). */
const PcrecCpRange *pcrec_ucd_find(Arena *a, const char *name, size_t len,
                                   unsigned ns, bool caseless, int *n);

/* Is `cp` in the BARE-namespace, case-sensitive set named `normname`?  1 or 0,
 * or -1 when no such row exists.  Allocates nothing (an early-exit decode), so
 * a per-character reader needs no arena. */
int pcrec_ucd_contains(const char *normname, unsigned cp);

/* Row enumeration, for the checks that must ask the oracle about every name
 * pcrec ships.  `row_name` is NULL past the end and reports the mask in `*ns`
 * (which may be NULL); `row_set` is `find` for row `i`. */
size_t pcrec_ucd_row_count(void);
const char *pcrec_ucd_row_name(size_t i, unsigned *ns);
const PcrecCpRange *pcrec_ucd_row_set(Arena *a, size_t i, bool caseless,
                                      int *n);

/* The Unicode version the tables are PINNED at ("16.0.0"), static. */
const char *pcrec_ucd_unicode_version(void);

#endif /* PCREC_UCD_TABLES_H */
