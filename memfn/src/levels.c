/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/levels.c — the accessor over levels.def, the kit's ISA levels
 * (R4e' batch 1; integration.md §R4.9.2.2): mf_levels() for the tests,
 * kit_level() for the seam and the rows, and kit_target_levels(), THE
 * ADMISSION of a level by a target (unit U2, R-37; target_seam.md §3). All
 * read the one table built here.
 */
#include <stddef.h>
#include <string.h>

#include "kit.h"

static const mf_level level_table[] = {
#define MF_LEVEL(token, family, needs, header, vw, test_march, forbid, stamp) \
    { #token, family, needs, header, vw, test_march, forbid, stamp },
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

/* 1 iff the comma-separated token list `list` holds the `len` bytes at `tok`
 * as one whole member. */
static int list_has(const char *list, const char *tok, size_t len)
{
    for (const char *p = list; *p;) {
        size_t n = strcspn(p, ",");
        if (n == len && !memcmp(p, tok, len)) return 1;
        p += n;
        if (*p) p++;
    }
    return 0;
}

/* THE ADMISSION (target_seam.md §3): level `l` is admitted for target `t`
 * iff `t` has a family, it is the level's, and every need of the level is
 * among t's features. The portable target (no family) admits none. */
static int admits(const mf_target *t, const mf_level *l)
{
    if (!t->family || strcmp(t->family->name, l->family)) return 0;
    for (const char *p = l->needs; *p;) {
        size_t n = strcspn(p, ",");
        if (!list_has(t->features, p, n)) return 0;
        p += n;
        if (*p) p++;
    }
    return 1;
}

unsigned kit_target_levels(const mf_target *t)
{
    unsigned m = 0;
    for (unsigned lv = 0; t && lv < MF_NLEVEL; lv++)
        if (admits(t, &level_table[lv])) m |= 1u << lv;
    return m;
}
