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
 * The set's one member is the art's TARGET (`pcrec_memfn_target`, unit U3),
 * derived once per attempt onto the Ctx: every art states it to the kit
 * (`mf_art_target`), the artifact names it in `<PREFIX>_TARGETS`, and this
 * file places the kit's guard and region text for it (the guard and the
 * region's open from `pcrec_emit_prologue`, its close from
 * `pcrec_emit_artifact_end`, src/gen/emit_dfa.c). */
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

/* A target's family token, or `none` for the portable target's absent one.
 * Targets and families are compared by these TOKENS, never by address
 * (target_seam_units.md §3: pcrec holds a target as its token). */
static const char *family_name(const mf_target *t, const char *none)
{
    return t->family ? t->family->name : none;
}

static void set_add(SimdSet *s, const mf_target *t)
{
    if (!s->first) s->first = t;
    else if (strcmp(t->name, s->first->name) && !s->other) s->other = t;
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
        if (strcmp(family_name(a, ""), family_name(b, "")))
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

/* Derives the compile's one CPU target, once per attempt, onto the Ctx
 * (`Ctx.cpu_target`): the kit's row and its `<PREFIX>_TARGETS` value. The
 * set was validated before any pass ran (`pcrec_compile`, the CLI's option
 * parse), so a refusal here is an internal error, never a quiet default;
 * this is the one point it can fail. */
void pcrec_memfn_target_derive(Ctx *cx)
{
    SimdSet s = { 0, 0 };
    char err[256];
    if (resolve(cx->opt->flags, cx->opt->memfn_simd, &s, err, sizeof err) != 0)
        pcrec_ctx_fail(cx, 0, "internal error: the CPU target set was refused "
                       "after option parse: %s", err);
    struct PcrecCpuTarget *ct = pcrec_arena_alloc(&cx->arena, sizeof *ct);
    ct->row = s.first;
    /* `family:members`, every token the kit's; `none` for the portable
     * target's absent family (docs/spec/match_api.md §6.3.10¶14) */
    ct->stamp = pcrec_sb_fragf(&cx->arena, "%s:%s", family_name(s.first, "none"),
                               s.first->name);
    cx->cpu_target = ct;
}

/* The compile's one CPU target, the kit's row as derived for this attempt,
 * for `mf_art_target`, the artifact's guard and region. */
const mf_target *pcrec_memfn_target(Ctx *cx)
{
    return cx->cpu_target->row;
}

/* `<PREFIX>_TARGETS`' value for it. */
const char *pcrec_memfn_targets_stamp(Ctx *cx)
{
    return cx->cpu_target->stamp;
}

/* Writes `text` as one CPU-guarded bracket (StrBuf.simd_guarded), so no
 * length decision reads it; nothing for "" or on a compound's part (its text
 * lies inside its shell's guard and region). */
static void put_target_text(Ctx *cx, StrBuf *c, const char *text)
{
    if (pcrec_is_part(cx) || !*text) return;
    pcrec_sb_simd_open(c);
    pcrec_sb_puts(c, text);
    pcrec_sb_simd_close(c);
}

/* The kit's family guard: once per artifact, at file scope ahead of every
 * `#include`, so a compile for another family stops at its `#error` rather
 * than in a header. None for the portable target (it has no family). */
void pcrec_emit_target_guard(Ctx *cx, StrBuf *c)
{
    const mf_target *t = pcrec_memfn_target(cx);
    put_target_text(cx, c, t->family ? mf_family_c_of(t->family)->guard : "");
}

/* The mark the artifact's TARGET HEADERS replace (`pcrec_memfn_target_headers`,
 * rendered by the finishing pass, src/gen/memfn_stamps.c): file scope, after
 * the prologue's own `#include` lines and ahead of the region open, in its
 * own bracket so no length decision reads it. Every artifact but a part
 * carries it until the render, which leaves "" where no header is owed. */
void pcrec_emit_target_headers_mark(Ctx *cx, StrBuf *c)
{
    if (pcrec_is_part(cx)) return;
    pcrec_sb_simd_open(c);
    pcrec_sb_puts(c, PCREC_TARGET_HEADERS_MARK);
    pcrec_sb_simd_close(c);
}

/* The `#include` lines the artifact's code needs that its prologue could not
 * write ahead of the region: a compound part's own (`PcrecPartFacts.string_h`)
 * where its text lies inside the shell's region. gcc gives a header's inline
 * functions the target in force where it is FIRST included, so a header first
 * read inside the region breaks every later use of it outside (a fortified
 * `memcpy`, a consumer's intrinsics, a second artifact; review
 * 2026-11-08-r5-xarch X-1, X-2); first included here, the part's own later
 * line is a no-op. "" without a region (the part's line is then at file
 * scope's target already). Read once, after the last emit. */
const char *pcrec_memfn_target_headers(Ctx *cx)
{
    const PcrecCompShell *sh = cx->job->comp_shell;
    bool string_h = false;
    for (int i = 0; sh && cx->job->region_placed && i < PCREC_COMP_MAXPARTS; i++)
        if (sh->text[i]) string_h = string_h || sh->facts[i].string_h;
    return string_h && !cx->job->string_h ? "#include <string.h>\n" : "";
}

/* The target's region open, before the part's first function; "" (no region)
 * for a target with nothing to enable. */
void pcrec_emit_target_open(Ctx *cx, StrBuf *c)
{
    const char *open = mf_target_c_of(pcrec_memfn_target(cx))->region_open;
    if (pcrec_is_part(cx) || !*open) return;
    cx->job->region_open = cx->job->region_placed = true;
    put_target_text(cx, c, open);
}

/* The region's close, after the part's last function and before `main`
 * (shared file text, outside every region). The open and this close are the
 * region's only writers; `pcrec_emit_artifact_end` is this one's only caller,
 * and the attempt's end refuses a region left open. */
void pcrec_emit_target_close(Ctx *cx, StrBuf *c)
{
    if (!cx->job->region_open) return;
    put_target_text(cx, c, mf_target_c_of(pcrec_memfn_target(cx))->region_close);
    cx->job->region_open = false;
}
