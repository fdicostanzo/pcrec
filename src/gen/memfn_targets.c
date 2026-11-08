/* src/gen/memfn_targets.c — [XARCH-DEV] unit P1: the CPU TARGET SET of one
 * compile (docs/design/memfn/target_seam_units.md §2 P1, §6).
 *
 * pcrec holds a CPU target only as an OPAQUE TOKEN. The kit owns the table
 * (memfn.h `mf_target_parse`, `mf_family_parse`, `mf_portable_target`,
 * `mf_host_defaults`): this file parses every token through it, shows a
 * refusal's text unchanged (R4), and names no target, family or CPU feature
 * (check C4). What it decides is the selection (`simd_rows`, first match
 * over the flag word and the list text) and the one-member rule.
 *
 * The one policy bit the kit reads (`MF_P_PORTABLE_ONLY`) is read off the
 * set: portable iff the set is the kit's portable target alone. P1 moves no
 * byte: the host's default list and the portable target reproduce today's
 * SIMD-off / SIMD-on split exactly. */
#include <stdio.h>
#include <string.h>

#include "gen/memfn_sites.h"

/* Which input wins. `on` is the SIMD axis as the flag word resolves it, `list`
 * whether the caller gave a list text; -1 matches either. First match. */
typedef enum { ACT_LIST_OFF, ACT_PORTABLE, ACT_LIST, ACT_HOST } SimdAct;
typedef struct { int on; int list; SimdAct act; } SimdRow;

static const SimdRow simd_rows[] = {
    { 0,  1, ACT_LIST_OFF },  /* a list while SIMD is off: refused, never ignored */
    { 0, -1, ACT_PORTABLE },  /* SIMD off (the default): the kit's portable target */
    { 1,  1, ACT_LIST },      /* SIMD on with a list: exactly those */
    { 1,  0, ACT_HOST },      /* SIMD on, no list: the host family's default list */
};

/* The members seen so far: the first, and the first one that differs. */
typedef struct {
    const mf_target *first;
    const mf_target *other;
} SimdSet;

static void set_add(SimdSet *s, const mf_target *t)
{
    if (!s->first) s->first = t;
    else if (t != s->first && !s->other) s->other = t;
}

/* Parses the comma list `list` into `s`. `families` admits a family token
 * (that family's default list); the kit's own default lists are target-only,
 * so the recursion is one deep. Returns 0, or 1 with the kit's text in err. */
static int add_list(const char *list, int families, SimdSet *s, char *err, size_t n)
{
    const char *p = list;
    for (;;) {
        size_t len = strcspn(p, ",");
        const mf_target *t = mf_target_parse(p, len, err, n);
        if (t) {
            set_add(s, t);
        } else if (families) {
            char ferr[256];
            const mf_family *f = mf_family_parse(p, len, ferr, sizeof ferr);
            if (!f) {
                size_t used = strlen(err);
                if (used < n) snprintf(err + used, n - used, "; %s", ferr);
                return 1;
            }
            err[0] = 0;
            if (add_list(f->defaults, 0, s, err, n) != 0) return 1;
        } else {
            return 1;
        }
        p += len;
        if (!*p) return 0;
        p++;
    }
}

/* The compile's target set, by the first matching row; one member or a
 * refusal (kit text, or this file's plain message) in err. */
static int resolve(uint64_t flags, const char *list, SimdSet *s, char *err, size_t n)
{
    int on = pcrec_axis_on(flags, PCREC_NO_MEMFN_SIMD, PCREC_FORCE_MEMFN_SIMD) ? 1 : 0;
    int has = list != NULL;
    const SimdRow *row = simd_rows;
    while ((row->on >= 0 && row->on != on) || (row->list >= 0 && row->list != has))
        row++;
    err[0] = 0;
    switch (row->act) {
    case ACT_LIST_OFF:
        snprintf(err, n, "a CPU list was given but SIMD is off: "
                 "state -fmemfn-simd=LIST, not a list beside -fno-memfn-simd");
        return 1;
    case ACT_PORTABLE:
        set_add(s, mf_portable_target());
        return 0;
    case ACT_LIST:
        if (add_list(list, 1, s, err, n) != 0) return 1;
        break;
    case ACT_HOST:
        if (add_list(mf_host_defaults(), 0, s, err, n) != 0) return 1;
        break;
    }
    if (s->other) {
        const mf_target *a = s->first, *b = s->other;
        if (a->family != b->family)
            snprintf(err, n, "the CPU list mixes families ('%s' and '%s'); "
                     "a list names the targets of one family", a->name, b->name);
        else
            snprintf(err, n, "the CPU list names more than one target ('%s' "
                     "and '%s'); one target per list until multi-target "
                     "artifacts are built (unit U4)", a->name, b->name);
        return 1;
    }
    return 0;
}

int pcrec_memfn_simd_check(uint64_t flags, const char *list, char *err, size_t n)
{
    SimdSet s = { 0, 0 };
    return resolve(flags, list, &s, err, n);
}

/* The set is validated before any pass runs (`pcrec_compile`, the CLI's
 * option parse), so a refusal here cannot occur; if it did, the portable
 * bit is the conservative answer for the artifact. */
uint32_t pcrec_memfn_policy(const pcrec_options *opt)
{
    SimdSet s = { 0, 0 };
    char err[256];
    if (resolve(opt->flags, opt->memfn_simd, &s, err, sizeof err) != 0)
        return MF_P_PORTABLE_ONLY;
    return s.first == mf_portable_target() ? MF_P_PORTABLE_ONLY : 0u;
}
