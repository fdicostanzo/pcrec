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
 * The set's one member is the art's TARGET (`pcrec_memfn_target`, unit U3):
 * every art states it to the kit (`mf_art_target`), and the artifact places
 * the kit's guard and region text for it (src/gen/emit_dfa.c,
 * `pcrec_emit_target_open`/`_close`) and names it in `<PREFIX>_TARGETS`. */
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

/* The compile's one CPU target, the kit's row, for `mf_art_target`, the
 * artifact's guard and region and its `<PREFIX>_TARGETS` stamp. The set is
 * validated before any pass runs (`pcrec_compile`, the CLI's option parse),
 * so a refusal here is an internal error, never a quiet default. */
const mf_target *pcrec_memfn_target(Ctx *cx)
{
    SimdSet s = { 0, 0 };
    char err[256];
    if (resolve(cx->opt->flags, cx->opt->memfn_simd, &s, err, sizeof err) != 0)
        pcrec_ctx_fail(cx, 0, "internal error: the CPU target set was refused "
                       "after option parse: %s", err);
    return s.first;
}

/* `<PREFIX>_TARGETS`' value: the family and the members, `family:members`
 * (docs/spec/match_api.md §6.3), every token the kit's; `none` for the
 * portable target's absent family. */
const char *pcrec_memfn_targets_stamp(Ctx *cx)
{
    const mf_target *t = pcrec_memfn_target(cx);
    return pcrec_sb_fragf(&cx->arena, "%s:%s", t->family ? t->family->name : "none",
                          t->name);
}

/* Writes the kit's text that opens the artifact's target code: the family
 * guard (file scope, once) and the target's region open, before the part's
 * first function. Both are target-dependent bytes, so they sit in one
 * CPU-guarded bracket (StrBuf.simd_guarded): no length decision reads them.
 * A part writes nothing (its text lies inside its shell's region); the
 * portable target's texts are empty, so a default artifact gains no byte. */
void pcrec_emit_target_open(Ctx *cx, StrBuf *c)
{
    if (pcrec_is_part(cx)) return;
    const mf_target *t = pcrec_memfn_target(cx);
    const char *guard = t->family ? mf_family_c_of(t->family)->guard : "";
    const char *open = mf_target_c_of(t)->region_open;
    if (!*guard && !*open) return;
    pcrec_sb_simd_open(c);
    pcrec_sb_puts(c, guard);
    pcrec_sb_puts(c, open);
    pcrec_sb_simd_close(c);
}

/* The region's close, after the part's last function (before `main`, which
 * is shared file text and stays outside it); as the open, guarded, nothing
 * on a part or for the portable target. */
void pcrec_emit_target_close(Ctx *cx, StrBuf *c)
{
    if (pcrec_is_part(cx)) return;
    const char *close = mf_target_c_of(pcrec_memfn_target(cx))->region_close;
    if (!*close) return;
    pcrec_sb_simd_open(c);
    pcrec_sb_puts(c, close);
    pcrec_sb_simd_close(c);
}
