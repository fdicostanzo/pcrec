/* emit_subst.c — [M4-SUBST] THE SUBST ARTIFACT AND THE SUPPORT UNIT: a
 * compiled substitution template as an element that turns matches into
 * PIECES, and the one file of shared functions every program compiles once.
 *
 * Design: docs/design/replace_design.md §R4 (pieces §R4.5, the map §R4.3,
 * one validation §R4.4, the support unit §R4.14, replace-all §R4.16, R13
 * §R4.17). Contract: docs/spec/subst_api.md.
 *
 * An artifact is a `.c` and a `.h`. The `.h` carries a copy of the rx shared
 * block (`pcrec_emit_rx_abi_block`, emit_dfa.c's one emitter, under its
 * existing `PCREC_RX_ABI_H` guard), then the SUBST TYPES BLOCK below
 * (prefix-free, guarded by `PCREC_SUBST_H`): the types, codes and flags, the
 * support unit's declarations, and the two `static inline` functions every
 * caller needs, the check and the context setup. Then the template's own
 * stamps, record and element. The types block lives ONLY in subst headers
 * and the support unit, so this file moves no byte of any rx artifact.
 *
 * The emitted element is straight-line code per template item: no template
 * interpreter, no name lookup, no byte copied. Every item is one piece
 * store. A reference reads its slot through the artifact's private run walk
 * (`<prefix>_subst_slot`), the one place the map is read per match. */

#include <string.h>

#include "core/internal.h"

/* THE SUBST TYPES BLOCK, part 1: codes, flags, types, the empty piece. The
 * support declarations (whose names carry the abi) and part 2 follow it. */
static const char subst_types[] =
"#include <string.h>\n"
"\n"
"/* [M4-SUBST] Codes below PCREC_ERR_ITER: none is a give-up, and nothing\n"
" * here returns -1. -13 is reserved. */\n"
"#define PCREC_SUBST_NOSPACE     (-11)  /* pc, scratch or out too small: need, sneed or *len suffices */\n"
"#define PCREC_SUBST_BADSPAN     (-12)  /* the rx reported a span a splice cannot express */\n"
"#define PCREC_SUBST_UNSET       (-14)  /* RX_SUBST_STRICT: a referenced group is unset */\n"
"#define PCREC_SUBST_MISMATCH    (-15)  /* a record, rx, map, flag or context that does not belong */\n"
"#define PCREC_SUBST_MISSING_REF (-16)  /* reference *bad_ref does not resolve */\n"
"\n"
"#define RX_SUBST_GAPS         0x1u  /* render: a gap piece before each match */\n"
"#define RX_SUBST_STRICT       0x2u  /* render: an unset group or variable is an error */\n"
"#define RX_SUBST_NOGROUP      (-1)  /* a map slot: no group, always unset, never an error */\n"
"#define RX_SUBST_USES_SCRATCH 0x1u  /* rx_subst_info.uses: the element writes scratch */\n"
"#define RX_SUBST_MAP_ABSENT   0x1u  /* pcrec_subst_map_names: a missing reference gets NOGROUP */\n"
"\n"
"/* One piece of output. p is never NULL, and is not to be read when len is 0. */\n"
"typedef struct rx_subst_piece {\n"
"    const unsigned char *p;\n"
"    size_t               len;\n"
"} rx_subst_piece;\n"
"\n"
"/* The MAP: reference r reads slot[run[r].first, run[r].first + run[r].count),\n"
" * or slot[r] alone when run is NULL; the first that participated wins. */\n"
"typedef struct rx_subst_run { int first, count; } rx_subst_run;\n"
"\n"
"typedef struct rx_subst_map {\n"
"    const int          *slot;    /* caps slots, or RX_SUBST_NOGROUP */\n"
"    size_t              nslot;   /* entries in slot[] */\n"
"    const rx_subst_run *run;     /* NULL: reference r reads slot[r] */\n"
"    size_t              nrun;    /* entries in run[] */\n"
"} rx_subst_map;\n"
"\n"
"/* One find-all's output between element calls. The caller sets pc, cap,\n"
" * scratch and scap, and starts n, sn and prev at 0. */\n"
"typedef struct rx_subst_out {\n"
"    rx_subst_piece *pc;       /* the caller's piece array */\n"
"    size_t          cap;      /* its entries */\n"
"    size_t          n;        /* pieces written so far: pc[0, n) */\n"
"    unsigned char  *scratch;  /* the caller's scratch bytes, or NULL */\n"
"    size_t          scap;     /* its size */\n"
"    size_t          sn;       /* scratch bytes used so far */\n"
"    size_t          prev;     /* end of the last match rendered: the next gap starts here */\n"
"    size_t          need;     /* after PCREC_SUBST_NOSPACE: the entries pc needs */\n"
"    size_t          sneed;    /* after PCREC_SUBST_NOSPACE: the bytes scratch needs */\n"
"} rx_subst_out;\n"
"\n"
"/* THE ELEMENT: renders k consecutive matches of one find-all as k * P\n"
" * pieces. caps holds k * ctx->ncap pairs, match i at caps + i * ctx->ncap,\n"
" * as <prefix>_next_n writes them. map NULL: the numbers are the slots. */\n"
"typedef int rx_substfn(const rx_ctx *ctx, const rx_subst_map *map,\n"
"                       ptrdiff_t (*caps)[2], size_t k, unsigned flags,\n"
"                       rx_subst_out *o);\n"
"\n"
"/* A subst artifact's record. */\n"
"struct rx_subst_info {\n"
"    unsigned              abi;           /* == PCREC_RX_ABI_H of its build */\n"
"    const char           *name;          /* the artifact's own name (its prefix) */\n"
"    const char           *template_text;\n"
"    size_t                template_len;\n"
"    int                   nrefs;         /* group references: rows in refs[] */\n"
"    const rx_group_entry *refs;          /* the REFERENCE LIST, first-appearance order */\n"
"    int                   maxnum;        /* highest group number referenced, or 0 */\n"
"    int                   npieces;       /* pieces per match, the gap included */\n"
"    int                   nvrefs;        /* ${!name} references */\n"
"    const char *const    *vrefs;         /* their names, in reference order; NULL when none */\n"
"    int                   encoding;      /* PCREC_ENC_* it was read in, or -1: any */\n"
"    unsigned              uses;          /* RX_SUBST_USES_SCRATCH when a case-forcing form appears */\n"
"    unsigned long long    support_id;    /* the support unit's content id from this build; 0 when unused */\n"
"    const unsigned long long *support;   /* &pcrec_support_id when the template calls the unit; else NULL */\n"
"    rx_substfn           *render;\n"
"};\n"
"\n"
"/* Where an empty piece points: never NULL, never read. */\n"
"static const unsigned char rx_subst_empty[1] __attribute__((unused)) = { 0 };\n"
"\n";

/* THE SUBST TYPES BLOCK, part 2: the check and the context setup, `static
 * inline` so a program that uses neither the helper nor flatten nor
 * replace-all needs no support unit (§R4.4). */
static const char subst_check_setup[] =
"\n"
"/* THE CHECK: validates template t and map against an rx's record (only its\n"
" * ncaps, ngroups and encoding are read). Returns 0, PCREC_SUBST_MISMATCH\n"
" * or PCREC_SUBST_MISSING_REF with *bad_ref the first reference that does\n"
" * not resolve (-1 for any other result). Never allocates. */\n"
"static inline int pcrec_subst_check(const struct rx_subst_info *t, const rx_subst_map *map,\n"
"                                    const struct rx_info *rx, unsigned flags, int *bad_ref)\n"
"{\n"
"    *bad_ref = -1;\n"
"    if (t->abi != PCREC_RX_ABI_H || (t->support && *t->support != t->support_id)\n"
"        || rx->ncaps < 1 || (t->encoding >= 0 && t->encoding != rx->encoding)\n"
"        || (flags & ~(RX_SUBST_GAPS | RX_SUBST_STRICT))\n"
"        || (!map && rx->ncaps > rx->ngroups + 1)\n"
"        || (map && (map->run ? map->nrun : map->nslot) < (size_t)t->nrefs))\n"
"        return PCREC_SUBST_MISMATCH;\n"
"    for (int r = 0; r < t->nrefs; r++) {\n"
"        const rx_group_entry *e = &t->refs[r];\n"
"        size_t first = (size_t)r, count = 1;\n"
"        int ok = 1;\n"
"        if (!map)                                  /* the numbers are the slots */\n"
"            ok = !e->name && e->number >= 0 && e->number < rx->ncaps;\n"
"        else if (map->run) {\n"
"            ok = map->run[r].first >= 0 && map->run[r].count >= 1\n"
"                 && (size_t)map->run[r].first <= map->nslot\n"
"                 && (size_t)map->run[r].count <= map->nslot - (size_t)map->run[r].first;\n"
"            first = ok ? (size_t)map->run[r].first : 0;\n"
"            count = ok ? (size_t)map->run[r].count : 0;\n"
"        }\n"
"        for (size_t i = first; ok && map && i < first + count; i++)\n"
"            ok = map->slot[i] == RX_SUBST_NOGROUP\n"
"                 || (map->slot[i] >= 0 && map->slot[i] < rx->ncaps);\n"
"        if (!ok) { *bad_ref = r; return PCREC_SUBST_MISSING_REF; }\n"
"    }\n"
"    return 0;\n"
"}\n"
"\n"
"/* THE CONTEXT SETUP: runs the check, then fills ctx for the element over\n"
" * iterator it (subject, len, ncap = rx->ncaps; user NULL) and resolves each\n"
" * ${!name} by name (first match wins) into vres (at least <S>_NVREFS\n"
" * entries), in the template's order. Returns 0, the check's code (ctx\n"
" * untouched), or PCREC_ERR_UNSET_VAR under RX_SUBST_STRICT. Reads\n"
" * it->vars only when the iterator is BOUND, or FRESH with\n"
" * PCREC_ITER_OPT_VARS set: in any other state the field may hold any value. */\n"
"static inline int rx_subst_ctx_init(rx_ctx *ctx, const rx_iter *it, const struct rx_info *rx,\n"
"                                    const struct rx_subst_info *t, const rx_subst_map *map,\n"
"                                    rx_var *vres, unsigned flags, int *bad_ref)\n"
"{\n"
"    const rx_var *v = (const rx_var *)0;\n"
"    size_t nv = 0;\n"
"    int rc = pcrec_subst_check(t, map, rx, flags, bad_ref);\n"
"    if (rc < 0) return rc;\n"
"    if (it->hdr == PCREC_ITER_BOUND\n"
"        || ((it->hdr & ~PCREC_ITER_OPT_MASK) == PCREC_ITER_FRESH\n"
"            && (it->hdr & PCREC_ITER_OPT_VARS))) { v = it->vars; nv = it->nvars; }\n"
"    ctx->subject = it->s; ctx->len = it->n; ctx->pos = 0;\n"
"    ctx->ncap = (size_t)rx->ncaps; ctx->caps = 0; ctx->user = 0;\n"
"    ctx->vars = t->nvrefs ? vres : (const rx_var *)0;\n"
"    ctx->nvars = (size_t)t->nvrefs;\n"
"    for (int j = 0; j < t->nvrefs; j++) {\n"
"        vres[j].name = t->vrefs[j]; vres[j].p = 0; vres[j].len = 0;\n"
"        for (size_t i = 0; i < nv; i++)\n"
"            if (v[i].name && !strcmp(v[i].name, t->vrefs[j])) {\n"
"                vres[j].p = v[i].p; vres[j].len = v[i].p ? v[i].len : 0;\n"
"                break;\n"
"            }\n"
"        if (!vres[j].p && (flags & RX_SUBST_STRICT)) return PCREC_ERR_UNSET_VAR;\n"
"    }\n"
"    return 0;\n"
"}\n";

/* The support unit's external names, each a macro over its abi-suffixed
 * spelling (§10¶3), in the order the declarations below give them. */
static const char *const support_names[] = {
    "rx_group_run", "pcrec_subst_map_names", "rx_subst_flatten",
    "rx_subst_replace_all", "pcrec_support_id",
};

/* The support unit's declarations, after the name macros. */
static const char support_decls[] =
"\n"
"/* THE SUPPORT UNIT's functions (pcrec --emit-support): defined once per\n"
" * program, where PCREC_SUPPORT_IMPLEMENTATION is defined before including\n"
" * it; every name carries the abi. PCREC_SUPPORT_STATIC, defined before the\n"
" * first pcrec header, makes them static to the one translation unit that\n"
" * includes the unit, whose definitions then declare them. */\n"
"#ifdef PCREC_SUPPORT_STATIC\n"
"#define PCREC_SUPPORT_DEF static __attribute__((unused))\n"
"#else\n"
"#define PCREC_SUPPORT_DEF\n"
"/* The run of rx's group rows named `name` (ref NULL: the caller scope):\n"
" * its length, with *first its first row; 0 when there is none. */\n"
"extern int rx_group_run(const struct rx_info *rx, const char *name,\n"
"                        const char *ref, int *first);\n"
"/* Fills a map for t from rx's records BY NAME (helper C). */\n"
"extern int pcrec_subst_map_names(const struct rx_subst_info *t,\n"
"                                 const struct rx_info *rx, unsigned opts,\n"
"                                 int *slot, size_t nslot,\n"
"                                 rx_subst_run *run, size_t nrun,\n"
"                                 rx_subst_map *map, int *bad_ref, size_t *nabsent);\n"
"/* Copies the pieces back to back into out when their total fits cap;\n"
" * returns the total, SIZE_MAX when it does not fit a size_t. */\n"
"extern size_t rx_subst_flatten(const rx_subst_piece *pc, size_t n,\n"
"                               unsigned char *restrict out, size_t cap);\n"
"/* Every match of one find-all substituted into out: the match count, or a\n"
" * negative code. */\n"
"extern int rx_subst_replace_all(rx_nextnfn next_n, rx_iter *it,\n"
"                                const struct rx_subst_info *t, const rx_ctx *ctx,\n"
"                                const rx_subst_map *map, unsigned flags,\n"
"                                rx_subst_out *o,\n"
"                                unsigned char *restrict out, size_t cap, size_t *len);\n"
"/* The support unit's content id: a hash of its own text. */\n"
"extern const unsigned long long pcrec_support_id;\n"
"#endif\n";

/* The support unit's definitions (§10), under its implementation guard. */
static const char support_defs[] =
"\n"
"PCREC_SUPPORT_DEF int rx_group_run(const struct rx_info *rx, const char *name,\n"
"                                   const char *ref, int *first)\n"
"{\n"
"    const rx_group_entry *g = rx->groups;\n"
"    int lo = 0, hi = rx->nnames, at = -1, n = 0;\n"
"    if (!g) return 0;\n"
"    if (ref) {                                     /* site rows: a short linear scan */\n"
"        size_t lr = strlen(ref);\n"
"        for (int i = rx->nnames; i < rx->nentries; i++)\n"
"            if (!strncmp(g[i].name, ref, lr) && g[i].name[lr] == '.'\n"
"                && !strcmp(g[i].name + lr + 1, name)) { if (at < 0) at = i; n++; }\n"
"            else if (at >= 0) break;\n"
"        *first = at;\n"
"        return n;\n"
"    }\n"
"    while (lo < hi) {                              /* bsearch, then back to the run's head */\n"
"        int mid = lo + (hi - lo) / 2, d = strcmp(g[mid].name, name);\n"
"        if (d == 0) { at = mid; break; }\n"
"        if (d < 0) lo = mid + 1; else hi = mid;\n"
"    }\n"
"    if (at < 0) return 0;\n"
"    while (at > 0 && !strcmp(g[at - 1].name, name)) at--;\n"
"    *first = at;\n"
"    for (n = 0; at + n < rx->nnames && !strcmp(g[at + n].name, name); n++) {}\n"
"    return n;\n"
"}\n"
"\n"
"/* For each reference r in order: appends its slots to slot[] and writes\n"
" * run[r]. A reference rx lacks is MISSING_REF (*bad_ref = r), or under\n"
" * RX_SUBST_MAP_ABSENT the single entry RX_SUBST_NOGROUP, counted in\n"
" * *nabsent with *bad_ref the first. Then fills *map and returns the check. */\n"
"PCREC_SUPPORT_DEF int pcrec_subst_map_names(const struct rx_subst_info *t,\n"
"                                            const struct rx_info *rx, unsigned opts,\n"
"                                            int *slot, size_t nslot,\n"
"                                            rx_subst_run *run, size_t nrun,\n"
"                                            rx_subst_map *map, int *bad_ref, size_t *nabsent)\n"
"{\n"
"    size_t w = 0, na = 0;\n"
"    int absent = -1, rc;\n"
"    *bad_ref = -1;\n"
"    if (nabsent) *nabsent = 0;\n"
"    if (t->abi != PCREC_RX_ABI_H || (t->support_id && t->support_id != pcrec_support_id)\n"
"        || rx->ncaps < 1 || (t->encoding >= 0 && t->encoding != rx->encoding)\n"
"        || (opts & ~RX_SUBST_MAP_ABSENT) || nrun < (size_t)t->nrefs)\n"
"        return PCREC_SUBST_MISMATCH;\n"
"    for (int r = 0; r < t->nrefs; r++) {\n"
"        const rx_group_entry *e = &t->refs[r];\n"
"        int first = e->number, n = 1, lacks;\n"
"        if (!e->name)                              /* a number: its own slot */\n"
"            lacks = e->number < 1 || e->number > rx->ngroups || e->number >= rx->ncaps;\n"
"        else {\n"
"            n = rx_group_run(rx, e->name, e->ref, &first);\n"
"            lacks = n < 1;\n"
"            for (int m = 0; !lacks && m < n; m++)\n"
"                lacks = rx->groups[first + m].slot < 0 || rx->groups[first + m].slot >= rx->ncaps;\n"
"        }\n"
"        if (lacks) {\n"
"            if (!(opts & RX_SUBST_MAP_ABSENT)) { *bad_ref = r; return PCREC_SUBST_MISSING_REF; }\n"
"            if (absent < 0) absent = r;\n"
"            na++;\n"
"            n = 1;\n"
"        }\n"
"        if (nslot - w < (size_t)n) return PCREC_SUBST_MISMATCH;\n"
"        run[r].first = (int)w;\n"
"        run[r].count = n;\n"
"        for (int m = 0; m < n; m++)\n"
"            slot[w++] = lacks ? RX_SUBST_NOGROUP : e->name ? rx->groups[first + m].slot : e->number;\n"
"    }\n"
"    if (nabsent) *nabsent = na;\n"
"    map->slot = slot; map->nslot = w; map->run = run; map->nrun = (size_t)t->nrefs;\n"
"    rc = pcrec_subst_check(t, map, rx, 0, bad_ref);\n"
"    if (rc == 0) *bad_ref = absent;\n"
"    return rc;\n"
"}\n"
"\n"
"PCREC_SUPPORT_DEF size_t rx_subst_flatten(const rx_subst_piece *pc, size_t n,\n"
"                                          unsigned char *restrict out, size_t cap)\n"
"{\n"
"    size_t tot = 0, w = 0;\n"
"    for (size_t i = 0; i < n; i++) {\n"
"        if (pc[i].len >= SIZE_MAX - tot) return SIZE_MAX;\n"
"        tot += pc[i].len;\n"
"    }\n"
"    if (tot > cap || !out) return tot;\n"
"    for (size_t i = 0; i < n; i++)\n"
"        if (pc[i].len) { memcpy(out + w, pc[i].p, pc[i].len); w += pc[i].len; }\n"
"    return tot;\n"
"}\n"
"\n"
"/* Appends pc[0, n) at out[*w] while everything so far fits cap, and counts\n"
" * it either way; *w becomes SIZE_MAX once the total stops fitting a size_t. */\n"
"static void rx_subst_append_(const rx_subst_piece *pc, size_t n, unsigned char *restrict out,\n"
"                             size_t cap, size_t *w, int *fits)\n"
"{\n"
"    for (size_t i = 0; i < n && *w != SIZE_MAX; i++) {\n"
"        if (pc[i].len >= SIZE_MAX - *w) { *w = SIZE_MAX; *fits = 0; return; }\n"
"        if (*fits && out && pc[i].len <= cap - *w) {\n"
"            if (pc[i].len) memcpy(out + *w, pc[i].p, pc[i].len);\n"
"        } else\n"
"            *fits = 0;\n"
"        *w += pc[i].len;\n"
"    }\n"
"}\n"
"\n"
"/* THE REPLACE-ALL FUNCTION: every match of it, substituted by t, the gaps\n"
" * and the tail, into out[0, *len): the match count (INT_MAX when more), or\n"
" * a negative code. NOSPACE with *len the total when out is too small (no\n"
" * match is searched twice); out == NULL with cap == 0 only sizes. Its only\n"
" * storage besides o is one RX_FOREACH_PAIRS batch on the stack. */\n"
"PCREC_SUPPORT_DEF int rx_subst_replace_all(rx_nextnfn next_n, rx_iter *it,\n"
"                                           const struct rx_subst_info *t, const rx_ctx *ctx,\n"
"                                           const rx_subst_map *map, unsigned flags,\n"
"                                           rx_subst_out *o,\n"
"                                           unsigned char *restrict out, size_t cap, size_t *len)\n"
"{\n"
"    ptrdiff_t buf[RX_FOREACH_PAIRS][2];\n"
"    size_t P, nc, k, got, w = 0, count = 0;\n"
"    int fits = 1, rc;\n"
"    if (!next_n || !it || !t || !ctx || !o || !len || !t->render || !o->pc || t->npieces < 1\n"
"        || (flags & ~RX_SUBST_STRICT) || (!out && cap) || ctx->ncap < 1\n"
"        || ctx->subject != it->s || ctx->len != it->n\n"
"        || ((t->uses & RX_SUBST_USES_SCRATCH) && !o->scratch))\n"
"        return PCREC_SUBST_MISMATCH;\n"
"    if ((it->hdr & ~PCREC_ITER_OPT_MASK) != PCREC_ITER_FRESH && it->hdr != PCREC_ITER_BOUND)\n"
"        return PCREC_ERR_ITER;\n"
"    P = (size_t)t->npieces;\n"
"    nc = ctx->ncap;\n"
"    k = nc <= RX_FOREACH_PAIRS ? RX_FOREACH_PAIRS / nc : 0;\n"
"    if (k > o->cap / P) k = o->cap / P;\n"
"    if (k > 64) k = 64;\n"
"    if (k == 0) return PCREC_SUBST_MISMATCH;\n"
"    o->n = o->sn = o->prev = o->need = o->sneed = 0;\n"
"    do {\n"
"        got = next_n(it, buf, k);\n"
"        o->n = o->sn = 0;\n"
"        rc = t->render(ctx, map, buf, got, RX_SUBST_GAPS | flags, o);\n"
"        if (rc == PCREC_SUBST_NOSPACE && o->sneed > o->scap) {   /* scratch: one match at a time */\n"
"            for (size_t i = 0; i < got; i++) {\n"
"                o->n = o->sn = 0;\n"
"                rc = t->render(ctx, map, buf + i * nc, 1, RX_SUBST_GAPS | flags, o);\n"
"                if (rc < 0) return rc;\n"
"                rx_subst_append_(o->pc, o->n, out, cap, &w, &fits);\n"
"            }\n"
"        } else if (rc < 0)\n"
"            return rc;\n"
"        else\n"
"            rx_subst_append_(o->pc, o->n, out, cap, &w, &fits);\n"
"        count += got;\n"
"    } while (got == k);\n"
"    if (it->rc < 0) return it->rc;\n"
"    if (ctx->len > o->prev) {                     /* the tail */\n"
"        rx_subst_piece tail = { ctx->subject + o->prev, ctx->len - o->prev };\n"
"        rx_subst_append_(&tail, 1, out, cap, &w, &fits);\n"
"    }\n"
"    *len = w;\n"
"    if (w == SIZE_MAX || (out && !fits)) return PCREC_SUBST_NOSPACE;\n"
"    return count > 2147483647u ? 2147483647 : (int)count;\n"
"}\n";

/* The support unit's content id: 64-bit FNV-1a over its own text. */
static unsigned long long support_hash(const char *s)
{
    unsigned long long h = 14695981039346656037ull;
    for (; *s; s++) { h ^= (unsigned char)*s; h *= 1099511628211ull; }
    return h;
}

/* The subst types block under its guard: an `#error` unless the rx shared
 * block of this build's abi is already defined (the same-build rule), then
 * once per translation unit the types, the support unit's abi-named
 * declarations, and the check and the context setup. */
static void emit_subst_block(StrBuf *sb)
{
    int abi = pcrec_artifact_abi();
    pcrec_sb_printf(sb, "#if !defined(PCREC_RX_ABI_H) || (PCREC_RX_ABI_H + 0) != %d\n"
                        "#error \"pcrec: this subst code (abi %d) needs the rx shared block of abi %d; "
                        "regenerate the rx, the subst and the support unit with one pcrec\"\n"
                        "#endif\n", abi, abi, abi);
    pcrec_sb_printf(sb, "#ifndef PCREC_SUBST_H\n#define PCREC_SUBST_H %d\n", abi);
    pcrec_sb_puts(sb, subst_types);
    for (size_t i = 0; i < sizeof support_names / sizeof *support_names; i++)
        pcrec_sb_printf(sb, "#define %s %s_v%d\n", support_names[i], support_names[i], abi);
    pcrec_sb_puts(sb, support_decls);
    pcrec_sb_puts(sb, subst_check_setup);
    pcrec_sb_puts(sb, "#endif /* PCREC_SUBST_H */\n");
}

/* The shared blocks a subst header and the support unit both open with: the
 * standard headers, the rx shared block and the subst types block. */
static void emit_shared_blocks(StrBuf *sb)
{
    pcrec_sb_puts(sb, "#include <stddef.h>\n#include <stdint.h>\n\n");
    pcrec_emit_rx_abi_block(sb);
    pcrec_sb_putc(sb, '\n');
    emit_subst_block(sb);
}

char *pcrec_emit_support(void)
{
    StrBuf u = { 0 }, all = { 0 };
    pcrec_sb_printf(&u, "/* Generated by pcrec %s (abi %d). The subst SUPPORT UNIT\n"
                        " * (docs/spec/subst_api.md section 10): include it anywhere for the\n"
                        " * declarations, and in exactly one translation unit define\n"
                        " * PCREC_SUPPORT_IMPLEMENTATION (or PCREC_SUPPORT_STATIC) first. */\n",
                    PCREC_VERSION, pcrec_artifact_abi());
    pcrec_sb_puts(&u, "#ifndef PCREC_SUPPORT_H\n#define PCREC_SUPPORT_H\n");
    emit_shared_blocks(&u);
    pcrec_sb_puts(&u, "#endif /* PCREC_SUPPORT_H */\n\n"
                      "#if defined(PCREC_SUPPORT_IMPLEMENTATION) || defined(PCREC_SUPPORT_STATIC)\n"
                      "#ifndef PCREC_SUPPORT_DEFINED\n#define PCREC_SUPPORT_DEFINED\n");
    const size_t head = u.len;
    pcrec_sb_puts(&u, support_defs);
    pcrec_sb_puts(&u, "#endif /* PCREC_SUPPORT_DEFINED */\n#endif\n");
    /* The content id is the hash of every other byte of the unit, and its
     * line opens the definitions so each of them can read it. */
    unsigned long long id = support_hash(u.p ? u.p : "");
    pcrec_sb_printf(&all, "%.*s\nPCREC_SUPPORT_DEF const unsigned long long pcrec_support_id = "
                          "0x%016llxull;\n%s", (int)head, u.p, id, u.p + head);
    pcrec_sb_free(&u);
    return pcrec_sb_take(&all);
}

/* The provenance line: pcrec's version, the abi and the template, escaped
 * for a comment. */
static void emit_subst_provenance(StrBuf *sb, const char *tmpl, size_t len)
{
    pcrec_sb_printf(sb, "/* Generated by pcrec %s (abi %d). Template: ",
                    PCREC_VERSION, pcrec_artifact_abi());
    pcrec_emit_comment_bytes(sb, tmpl, len);
    pcrec_sb_puts(sb, " */\n");
}

/* `max(1, n)`: a count that sizes a caller's array. */
static int at_least_one(int n) { return n > 0 ? n : 1; }

/* The declarations a caller includes: the storage stamps (match_api
 * §6.3.1¶1's family) behind the case-only-prefix `#error`, the record and
 * the element. */
static void emit_subst_decls(StrBuf *sb, const char *p, const char *up, const SubstTmpl *t)
{
    pcrec_sb_printf(sb, "#ifdef %s_PIECES\n"
                        "#error \"pcrec: two subst artifacts whose prefixes differ only in case "
                        "share the stamps %s_*; rename one\"\n#endif\n", up, up);
    pcrec_sb_stampf(sb, up, "NREFS", "%d", at_least_one(t->nrefs));
    pcrec_sb_stampf(sb, up, "PIECES", "%zu", t->nitems + 1);
    pcrec_sb_stampf(sb, up, "MAXNUM", "%d", t->maxnum);
    pcrec_sb_stampf(sb, up, "NVREFS", "%d", at_least_one(t->nvrefs));
    pcrec_sb_printf(sb, "extern const struct rx_subst_info %s_subst_info;\n", p);
    pcrec_sb_printf(sb, "int %s_render(const rx_ctx *ctx, const rx_subst_map *map,\n"
                        "    ptrdiff_t (*caps)[2], size_t k, unsigned flags, rx_subst_out *o);\n", p);
}

/* The `.h`: provenance, include guard, the shared blocks, the template's
 * declarations. The guard spells the prefix VERBATIM under a stem no rx
 * header uses (an rx guard is `PCREC_GEN_<UPPER>_H`). */
static void emit_subst_header(StrBuf *h, const char *tmpl, size_t len, const char *p,
                              const char *up, const SubstTmpl *t)
{
    emit_subst_provenance(h, tmpl, len);
    pcrec_sb_printf(h, "#ifndef PCREC_SUBST_GEN_%s_H\n#define PCREC_SUBST_GEN_%s_H\n\n", p, p);
    emit_shared_blocks(h);
    pcrec_sb_putc(h, '\n');
    emit_subst_decls(h, p, up, t);
    pcrec_sb_printf(h, "\n#endif /* PCREC_SUBST_GEN_%s_H */\n", p);
}

/* The record's tables: the reference list and the `${!name}` names. */
static void emit_subst_tables(StrBuf *c, const char *p, const SubstTmpl *t)
{
    if (t->nrefs) {
        pcrec_sb_printf(c, "static const rx_group_entry %s_subst_refs[] = {\n", p);
        for (int i = 0; i < t->nrefs; i++) {
            const SubstRef *e = &t->refs[i];
            pcrec_sb_puts(c, "    { ");
            if (e->name) pcrec_emit_c_string_literal(c, e->name, strlen(e->name));
            else pcrec_sb_puts(c, "NULL");
            pcrec_sb_printf(c, ", %d, -1, NULL },\n", e->number);
        }
        pcrec_sb_puts(c, "};\n");
    }
    if (t->nvrefs) {
        pcrec_sb_printf(c, "static const char *const %s_subst_vrefs[] = {\n", p);
        for (int j = 0; j < t->nvrefs; j++) {
            pcrec_sb_puts(c, "    ");
            pcrec_emit_c_string_literal(c, t->vrefs[j], strlen(t->vrefs[j]));
            pcrec_sb_puts(c, ",\n");
        }
        pcrec_sb_puts(c, "};\n");
    }
}

/* The artifact's private reference readers, emitted when it has a
 * reference: the run walk (§3¶5) and the group piece. */
static void emit_subst_slot(StrBuf *c, const char *p)
{
    pcrec_sb_printf(c,
        "\n/* The caps slot reference r (group number k, -1 for a name) reads in match\n"
        " * c: the first of its map entries that participated (no map: slot k);\n"
        " * RX_SUBST_NOGROUP when every entry is one; -2 when unset; -3 when the map\n"
        " * or the number names no slot of c. */\n"
        "static int %s_subst_slot(const rx_subst_map *map, int r, int k,\n"
        "                         ptrdiff_t (*c)[2], size_t nc)\n"
        "{\n"
        "    size_t first = (size_t)r, count = 1;\n"
        "    int seen = 0;\n"
        "    if (!map) {\n"
        "        if (k < 0 || (size_t)k >= nc) return -3;\n"
        "        return c[k][0] >= 0 && c[k][1] >= 0 ? k : -2;\n"
        "    }\n"
        "    if (map->run) {\n"
        "        if (map->run[r].first < 0 || map->run[r].count < 1) return -3;\n"
        "        first = (size_t)map->run[r].first;\n"
        "        count = (size_t)map->run[r].count;\n"
        "        if (first > map->nslot || count > map->nslot - first) return -3;\n"
        "    }\n"
        "    for (size_t i = first; i < first + count; i++) {\n"
        "        int sl = map->slot[i];\n"
        "        if (sl == RX_SUBST_NOGROUP) continue;\n"
        "        if (sl < 0 || (size_t)sl >= nc) return -3;\n"
        "        seen = 1;\n"
        "        if (c[sl][0] >= 0 && c[sl][1] >= 0) return sl;\n"
        "    }\n"
        "    return seen ? -2 : RX_SUBST_NOGROUP;\n"
        "}\n"
        "\n/* Stores slot sl's piece of match c in *q: empty when unset (UNSET under\n"
        " * RX_SUBST_STRICT unless every entry was RX_SUBST_NOGROUP), MISMATCH for\n"
        " * a slot the map cannot name, BADSPAN for a set span ending before it starts. */\n"
        "static int %s_subst_group(const unsigned char *s, ptrdiff_t (*c)[2], int sl,\n"
        "                          unsigned flags, rx_subst_piece *q)\n"
        "{\n"
        "    q->p = rx_subst_empty; q->len = 0;\n"
        "    if (sl == -3) return PCREC_SUBST_MISMATCH;\n"
        "    if (sl == -2) return (flags & RX_SUBST_STRICT) ? PCREC_SUBST_UNSET : 0;\n"
        "    if (sl < 0) return 0;\n"
        "    if (c[sl][1] < c[sl][0]) return PCREC_SUBST_BADSPAN;\n"
        "    q->p = s + c[sl][0]; q->len = (size_t)(c[sl][1] - c[sl][0]);\n"
        "    return 0;\n"
        "}\n", p, p);
}

/* A reference's piece store: reference r, group number k (-1 for a name). */
static void emit_subst_ref(StrBuf *c, const char *p, int r, int k)
{
    pcrec_sb_printf(c, "        if ((rc = %s_subst_group(s, c, %s_subst_slot(map, %d, %d, c, nc), "
                       "flags, q++)) < 0) break;\n", p, p, r, k);
}

/* One template item's piece store, inside the per-match loop. */
static void emit_subst_item(StrBuf *c, const char *p, const SubstTmpl *t, const SubstItem *it)
{
    switch (it->kind) {
    case SUBST_LIT:
        pcrec_sb_puts(c, "        q->p = (const unsigned char *)");
        pcrec_emit_c_string_literal(c, t->lit + it->off, it->len);
        pcrec_sb_printf(c, "; q->len = %zu; q++;\n", it->len);
        break;
    case SUBST_GROUP:
        if (it->num == 0)
            pcrec_sb_puts(c, "        q->p = s + c[0][0]; q->len = (size_t)(c[0][1] - c[0][0]); q++;\n");
        else                              /* a numbered reference reads the map like a name */
            emit_subst_ref(c, p, it->ref, it->num);
        break;
    case SUBST_NAME:
        emit_subst_ref(c, p, it->ref, -1);
        break;
    case SUBST_VAR:
        pcrec_sb_printf(c, "        q->p = ctx->vars[%d].p ? ctx->vars[%d].p : rx_subst_empty;\n"
                           "        q->len = ctx->vars[%d].p ? ctx->vars[%d].len : 0; q++;\n",
                        it->ref, it->ref, it->ref, it->ref);
        break;
    case SUBST_SUBJECT:
        pcrec_sb_puts(c, "        q->p = s; q->len = ctx->len; q++;\n");
        break;
    case SUBST_BEFORE:
        pcrec_sb_puts(c, "        q->p = s; q->len = (size_t)c[0][0]; q++;\n");
        break;
    case SUBST_AFTER:
        pcrec_sb_puts(c, "        q->p = s + c[0][1]; q->len = ctx->len - (size_t)c[0][1]; q++;\n");
        break;
    }
}

/* The element: the memory-safety re-asserts once per call (§4¶10), the room
 * test, then per match the span checks, the gap and the items' pieces in
 * template order. A failing match commits the matches before it (§4¶21). */
static void emit_subst_render(StrBuf *c, const char *p, const SubstTmpl *t)
{
    const size_t np = t->nitems + 1;
    pcrec_sb_printf(c, "\nint %s_render(const rx_ctx *ctx, const rx_subst_map *map,\n"
                       "    ptrdiff_t (*caps)[2], size_t k, unsigned flags, rx_subst_out *o)\n{\n", p);
    pcrec_sb_printf(c, "    const unsigned char *s = ctx->subject ? ctx->subject : rx_subst_empty;\n"
                       "    const size_t nc = ctx->ncap, P = (flags & RX_SUBST_GAPS) ? %zu : %zu;\n"
                       "    size_t prev = o->prev, i;\n"
                       "    rx_subst_piece *pc;\n"
                       "    int rc = 0;\n", np, np - 1);
    if (!t->nrefs) pcrec_sb_puts(c, "    (void)map;\n");
    pcrec_sb_puts(c, "    if ((flags & ~(RX_SUBST_GAPS | RX_SUBST_STRICT))");
    if (t->nvrefs)          /* a hand-filled ctx must carry the resolved variables */
        pcrec_sb_printf(c, "\n        || !ctx->vars || ctx->nvars < %d", t->nvrefs);
    if (t->nrefs)
        pcrec_sb_printf(c, "\n        || (map && (map->run ? map->nrun : map->nslot) < %d)", t->nrefs);
    pcrec_sb_puts(c, ")\n        return PCREC_SUBST_MISMATCH;\n");
    if (t->nvrefs)
        pcrec_sb_printf(c, "    if (flags & RX_SUBST_STRICT)\n"
                           "        for (int j = 0; j < %d; j++)\n"
                           "            if (!ctx->vars[j].p) return PCREC_ERR_UNSET_VAR;\n", t->nvrefs);
    pcrec_sb_puts(c, "    if (o->n > o->cap || (P && k > (o->cap - o->n) / P)) {\n"
                     "        o->need = (P && k > (SIZE_MAX - o->n) / P) ? SIZE_MAX : o->n + k * P;\n"
                     "        return PCREC_SUBST_NOSPACE;\n"
                     "    }\n"
                     "    for (i = 0, pc = o->pc + o->n; i < k; i++, pc += P) {\n"
                     "        ptrdiff_t (*c)[2] = caps + i * nc;\n"
                     "        rx_subst_piece *q = pc;\n"
                     "        if (c[0][0] < 0 || c[0][1] < c[0][0] || (size_t)c[0][1] > ctx->len\n"
                     "            || ((flags & RX_SUBST_GAPS) && (size_t)c[0][0] < prev)) {\n"
                     "            rc = PCREC_SUBST_BADSPAN;\n"
                     "            break;\n"
                     "        }\n"
                     "        if (flags & RX_SUBST_GAPS) { q->p = s + prev; q->len = (size_t)c[0][0] - prev; q++; }\n");
    for (size_t i = 0; i < t->nitems; i++)
        emit_subst_item(c, p, t, &t->items[i]);
    pcrec_sb_puts(c, "        prev = (size_t)c[0][1];\n"
                     "    }\n"
                     "    o->n += i * P;\n"
                     "    o->prev = prev;\n"
                     "    return rc;\n}\n");
}

/* The encoding a template binds under: its own, when a byte of it is
 * non-ASCII (it was read in that encoding: names, the UTF check); -1, any,
 * when every byte is ASCII and reads the same in each. */
static int subst_bind_encoding(const char *tmpl, size_t len, int encoding)
{
    for (size_t i = 0; i < len; i++)
        if ((unsigned char)tmpl[i] >= 0x80) return encoding;
    return -1;
}

/* The record. No template of the core module calls into the support unit,
 * so `support` is NULL and `support_id` 0. */
static void emit_subst_info(StrBuf *c, const char *tmpl, size_t len, const char *p,
                            const SubstTmpl *t, const PcrecSubstOptions *o)
{
    pcrec_sb_printf(c, "\nconst struct rx_subst_info %s_subst_info = {\n", p);
    pcrec_sb_printf(c, "    .abi = %d,\n    .name = \"%s\",\n    .template_text = ",
                    pcrec_artifact_abi(), p);
    pcrec_emit_c_string_literal(c, tmpl, len);
    pcrec_sb_printf(c, ",\n    .template_len = %zu,\n", len);
    pcrec_sb_printf(c, "    .nrefs = %d,\n", t->nrefs);
    if (t->nrefs) pcrec_sb_printf(c, "    .refs = %s_subst_refs,\n", p);
    else pcrec_sb_puts(c, "    .refs = NULL,\n");
    pcrec_sb_printf(c, "    .maxnum = %d,\n    .npieces = %zu,\n    .nvrefs = %d,\n",
                    t->maxnum, t->nitems + 1, t->nvrefs);
    if (t->nvrefs) pcrec_sb_printf(c, "    .vrefs = %s_subst_vrefs,\n", p);
    else pcrec_sb_puts(c, "    .vrefs = NULL,\n");
    pcrec_sb_printf(c, "    .encoding = %d,\n    .uses = 0,\n    .support_id = 0,\n"
                       "    .support = NULL,\n    .render = %s_render,\n};\n",
                    subst_bind_encoding(tmpl, len, o->encoding), p);
}

void pcrec_emit_subst(const char *tmpl, size_t len, const SubstTmpl *t,
                      const PcrecSubstOptions *o, pcrec_output *out)
{
    Arena a = { NULL, NULL };
    StrBuf c = { 0 }, h = { 0 };
    const char *p = o->prefix;
    const char *up = pcrec_sb_upper(&a, p);

    emit_subst_provenance(&c, tmpl, len);
    pcrec_sb_stamp_str(&c, up, "SUBST_MODULES", t->uses_pcrec ? "subst,subst-pcrec" : "subst");
    if (o->header_name) {
        pcrec_sb_printf(&c, "#include \"%s\"\n\n", o->header_name);
        emit_subst_header(&h, tmpl, len, p, up, t);
    } else {
        emit_shared_blocks(&c);
        pcrec_sb_putc(&c, '\n');
        emit_subst_decls(&c, p, up, t);
        pcrec_sb_putc(&c, '\n');
    }
    emit_subst_tables(&c, p, t);
    if (t->nrefs) emit_subst_slot(&c, p);
    emit_subst_render(&c, p, t);
    emit_subst_info(&c, tmpl, len, p, t, o);

    out->c_src = pcrec_sb_take(&c);
    out->h_src = o->header_name ? pcrec_sb_take(&h) : NULL;
    pcrec_arena_free(&a);
}
