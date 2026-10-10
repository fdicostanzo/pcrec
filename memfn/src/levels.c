/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/levels.c — the accessor over levels.def, the kit's ISA levels
 * (R4e' batch 1; integration.md §R4.9.2.2): mf_levels() for the tests,
 * kit_level() for the seam and the rows. Both read the one table built here.
 */
#include <stddef.h>

#include "kit.h"

static const mf_level level_table[] = {
#define MF_LEVEL(token, family, guard, header, vw, test_march, forbid, stamp) \
    { #token, family, guard, header, vw, test_march, forbid, stamp },
#include "levels.def"
#undef MF_LEVEL
};

_Static_assert(sizeof level_table / sizeof level_table[0] == MF_NLEVEL,
               "one mf_level per levels.def token");

const mf_level *mf_levels(size_t *n)
{
    if (n) *n = MF_NLEVEL;
    return level_table;
}

const mf_level *kit_level(unsigned lv)
{
    return lv < MF_NLEVEL ? &level_table[lv] : NULL;
}
