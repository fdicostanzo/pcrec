/* src/gen/targets.c — the target table's rows, the resolution of an
 * artifact's target set, and the region and family-guard text
 * ([XARCH-DEV] U1; docs/design/memfn/target_seam.md §2, §6.1;
 * docs/design/memfn/target_seam_units.md).
 *
 * Every name, attribute list and guard comes from src/gen/targets.def, the
 * one file the arch-blindness detector exempts: this file spells none of
 * them. Until U3 the resolved set reaches the emitted text only through the
 * kit's one policy bit (`pcrec_memfn_policy`), so no artifact moves. */
#include <string.h>

#define PCREC_TARGET_HOST
#define PCREC_TARGET_TEXT
#include "gen/targets.h"

static const PcrecFamily families[PCREC_FAM_N] = {
    [PCREC_FAM_NONE] = { "", "", PCREC_TGT_N, "" },
#define PCREC_FAMILY(id, name, guard, baseline, simd_list) \
    [id] = { name, guard, baseline, simd_list },
#define PCREC_TARGET(id, name, family, attr, features)
#include "gen/targets.def"
#undef PCREC_FAMILY
#undef PCREC_TARGET
};

static const PcrecTarget targets[PCREC_TGT_N] = {
#define PCREC_FAMILY(id, name, guard, baseline, simd_list)
#define PCREC_TARGET(id, name, family, attr, features) \
    [id] = { name, family, attr, features },
#include "gen/targets.def"
#undef PCREC_FAMILY
#undef PCREC_TARGET
};

const PcrecFamily *pcrec_family(PcrecFamilyId f) { return &families[f]; }
const PcrecTarget *pcrec_target(PcrecTargetId t) { return &targets[t]; }
PcrecFamilyId pcrec_host_family(void) { return PCREC_HOST_FAMILY; }

/* THE LIST TABLE (target_seam.md §2), first match. A predicate column is
 * 1 (must hold), 0 (must not) or -1 (any). `deny` is `-fno-memfn-simd`
 * given; `list` a target list given; `on` the axis on after its deny, its
 * force and axes.def's declared default (`pcrec_axis_on`), so the flag pair
 * is read here and nowhere else. */
typedef enum { TS_GENERIC, TS_LIST, TS_FAMILY_DEFAULT } TsFrom;

static const struct { signed char deny, list, on; TsFrom from; } ts_rows[] = {
    /* deny list  on    set */
    {  1,   -1,  -1,   TS_GENERIC },        /* 1: the deny wins (tuning.md §2.43) */
    { -1,    1,  -1,   TS_LIST },           /* 2: the given list, one family      */
    { -1,    0,   1,   TS_FAMILY_DEFAULT }, /* 3: the family's declared list      */
    { -1,    0,  -1,   TS_GENERIC },        /* 4: the default, today's bytes      */
};

static bool ts_col(signed char want, bool have)
{
    return want < 0 || (bool)want == have;
}

/* The target named by the `len` bytes at `s`, or PCREC_TGT_N. */
static PcrecTargetId target_named(const char *s, size_t len)
{
    for (unsigned t = 0; t < PCREC_TGT_N; t++)
        if (strlen(targets[t].name) == len && !memcmp(targets[t].name, s, len))
            return (PcrecTargetId)t;
    return PCREC_TGT_N;
}

/* Fills `*out` from a comma list: every member named, repeats dropped, one
 * family across all of them (`generic` belongs to none, so it stands alone). */
static const char *set_from_list(const char *list, PcrecTargetSet *out)
{
    out->n = 0;
    out->family = PCREC_FAM_NONE;
    for (const char *p = list;; p++) {
        const char *e = strchr(p, ',');
        size_t len = e ? (size_t)(e - p) : strlen(p);
        if (!len) return "a target list has an empty member";
        PcrecTargetId t = target_named(p, len);
        if (t == PCREC_TGT_N) return "a target list names a target pcrec does not know";
        if (out->n && targets[t].family != out->family)
            return "a target list names members of more than one target family";
        out->family = targets[t].family;
        bool seen = false;
        for (unsigned i = 0; i < out->n; i++) seen |= out->t[i] == t;
        if (!seen) out->t[out->n++] = t;
        if (!e) return NULL;
        p = e;
    }
}

const char *pcrec_target_set(uint64_t flags, const char *list, const char *family,
                             PcrecTargetSet *out)
{
    bool deny = pcrec_flags_has(flags, PCREC_NO_MEMFN_SIMD);
    bool on = pcrec_axis_on(flags, PCREC_NO_MEMFN_SIMD, PCREC_FORCE_MEMFN_SIMD);
    size_t r = 0;
    while (!(ts_col(ts_rows[r].deny, deny) && ts_col(ts_rows[r].list, list != NULL) &&
             ts_col(ts_rows[r].on, on)))
        r++;   /* row 4 matches whatever rows 1-3 left */

    PcrecFamilyId f = pcrec_host_family();
    switch (ts_rows[r].from) {
    case TS_LIST:
        return set_from_list(list, out);
    case TS_FAMILY_DEFAULT:
        if (family) {
            for (f = PCREC_FAM_NONE + 1; f < PCREC_FAM_N; f++)
                if (!strcmp(families[f].name, family)) break;
            if (f == PCREC_FAM_N) return "a target family pcrec does not know";
        }
        if (f != PCREC_FAM_NONE) return set_from_list(families[f].simd_list, out);
        break;   /* no family row for this host: nothing to plan for but generic */
    case TS_GENERIC:
        break;
    }
    out->family = PCREC_FAM_NONE;
    out->n = 1;
    out->t[0] = PCREC_TGT_GENERIC;
    return NULL;
}

bool pcrec_target_set_generic(const PcrecTargetSet *s)
{
    return s->n == 1 && s->t[0] == PCREC_TGT_GENERIC;
}

void pcrec_target_region_open(StrBuf *c, PcrecTargetId t)
{
    if (*targets[t].attr)
        pcrec_sb_printf(c, PCREC_REGION_OPEN_FMT, targets[t].attr, targets[t].attr);
}

void pcrec_target_region_close(StrBuf *c, PcrecTargetId t)
{
    if (*targets[t].attr) pcrec_sb_puts(c, PCREC_REGION_CLOSE_TEXT);
}

void pcrec_family_guard(StrBuf *c, PcrecFamilyId f)
{
    if (f != PCREC_FAM_NONE)
        pcrec_sb_printf(c, PCREC_FAMILY_GUARD_FMT, families[f].guard, families[f].name);
}
