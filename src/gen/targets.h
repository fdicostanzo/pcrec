/* src/gen/targets.h — the target table's types, the list resolution and the
 * region/guard renderers ([XARCH-DEV] U1; docs/design/memfn/target_seam.md
 * §2, §6.1; the rows are src/gen/targets.def). */
#ifndef PCREC_GEN_TARGETS_H
#define PCREC_GEN_TARGETS_H

#include "core/internal.h"

/* One id per family row; PCREC_FAM_NONE is `generic`'s (no family). */
typedef enum {
    PCREC_FAM_NONE,
#define PCREC_FAMILY(id, name, guard, baseline, simd_list) id,
#define PCREC_TARGET(id, name, family, attr, features)
#include "gen/targets.def"
#undef PCREC_FAMILY
#undef PCREC_TARGET
    PCREC_FAM_N
} PcrecFamilyId;

/* One id per target row, in the table's order. */
typedef enum {
#define PCREC_FAMILY(id, name, guard, baseline, simd_list)
#define PCREC_TARGET(id, name, family, attr, features) id,
#include "gen/targets.def"
#undef PCREC_FAMILY
#undef PCREC_TARGET
    PCREC_TGT_N
} PcrecTargetId;

typedef struct {
    const char    *name;
    const char    *guard;      /* the file-scope `#error`'s condition       */
    PcrecTargetId  baseline;
    const char    *simd_list;  /* what `-fmemfn-simd` resolves to (rule 3)  */
} PcrecFamily;

typedef struct {
    const char    *name;       /* primary: stem tag and probe string too    */
    PcrecFamilyId  family;
    const char    *attr;       /* the region's additive list; "" = none     */
    const char    *features;   /* the sorted tokens handed to the kit       */
} PcrecTarget;

/* An artifact's target set: one family (PCREC_FAM_NONE for `{generic}`) and
 * its members in the order given, without repeats. */
typedef struct {
    PcrecFamilyId family;
    unsigned      n;
    PcrecTargetId t[PCREC_TGT_N];
} PcrecTargetSet;

/* The row of a family or a target. */
const PcrecFamily *pcrec_family(PcrecFamilyId f);
const PcrecTarget *pcrec_target(PcrecTargetId t);
/* The family pcrec was built for (PCREC_FAM_NONE when the table has none). */
PcrecFamilyId pcrec_host_family(void);

/* Resolves the target set from the option word, an optional comma list of
 * target names and an optional family name, through target_seam.md §2's
 * first-match table (the `-f[no-]memfn-simd` pair is an alias of it, never a
 * second gate). Writes `*out` and returns NULL, or returns the refusal text
 * (an unknown name, an empty member, members of two families) and leaves
 * `*out` unspecified. Until U3 gives the list and the family their options,
 * every library caller passes NULL for both. */
const char *pcrec_target_set(uint64_t flags, const char *list, const char *family,
                             PcrecTargetSet *out);
/* True iff the set is `{generic}`: the kit is held to portable text. */
bool pcrec_target_set_generic(const PcrecTargetSet *s);

/* Writes the region that compiles what follows for target `t`, and the line
 * that ends it (target_seam.md §6.1; nothing for a target with no attr). */
void pcrec_target_region_open(StrBuf *c, PcrecTargetId t);
void pcrec_target_region_close(StrBuf *c, PcrecTargetId t);
/* Writes the file-scope refusal of every compile outside family `f`
 * (nothing for PCREC_FAM_NONE). */
void pcrec_family_guard(StrBuf *c, PcrecFamilyId f);

#endif
