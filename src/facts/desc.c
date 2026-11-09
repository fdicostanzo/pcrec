/* src/facts/desc.c — [RUN-POS-SET] stage 2p: the fixed-width piece
 * description's arm combinators (desc.h; docs/design/alt_normal_form.md
 * §3.4-§3.5).
 *
 * The arms:
 *   unit  the empty string: one group, width 0 (CAT's identity; the walk
 *         seeds its accumulator with it, and T3's row E-1 passes it for an
 *         `A_EMPTY` node)
 *   zero  a node other than the empty string that consumes nothing (an
 *         assertion, `\G`, `\K`, a check callout, a lookaround read as no
 *         body: span_arms §4.1 E-4/E-5): one group,
 *         width 0, NOT exact (its strings are a subset of the empty
 *         string's), so a group built through it is not exact either
 *   pos   one position: one group, width 1, exact
 *   cat   the PRODUCT: every left group before every right group, widths
 *         add, positions concatenate; groups of one total width hull-merge
 *   alt   the UNION of the two group lists; same-width groups hull-merge
 *   none  a wall: no description, and none for anything built on it
 *
 * A HULL MERGE of two groups of one width is the position-wise union of the
 * positions both store (right-aligned: both store the LAST positions of
 * their width). It is a superset of the two, which is the statement a group
 * makes. It stays EXACT only where both are exact and they differ in at most
 * one position, the one case where the product of the unions is the union
 * of the products (rule M's fact, §3.2).
 *
 * Bounds: over `max_groups` groups the description is dropped (`PD_OVER`):
 * sound, a reader then has today's single run. Each group stores at most
 * `max_pos` positions, its LAST ones: the walk builds right to left, so a
 * full group is reused whole by every step to its left (no copy), and a
 * suffix of a piece is a piece.
 *
 * THE ADJACENCY HEAD (`PdHead`, desc.h) is the second column: FIRST
 * positions, read through zero-width nodes, with the consumed width range and
 * WRITES. Its combinators sit after the description's. */
#include <string.h>

#include "core/internal.h"
#include "facts/desc.h"

PdDesc pcrec_pd_unit(void)
{
    static const void *nopos[1];
    static PdGroup g = { 0, 0, true, nopos };
    return (PdDesc){ 1, 0, &g };
}

PdDesc pcrec_pd_zero(void)
{
    static const void *nopos[1];
    static PdGroup g = { 0, 0, false, nopos };
    return (PdDesc){ 1, 0, &g };
}

PdDesc pcrec_pd_none(void)
{
    return (PdDesc){ -1, PD_WALL, NULL };
}

PdDesc pcrec_pd_pos(Ctx *cx, const void *pos)
{
    PdGroup *g = pcrec_arena_alloc(&cx->arena, sizeof *g);
    const void **p = pcrec_arena_alloc(&cx->arena, sizeof *p);
    p[0] = pos;
    *g = (PdGroup){ 1, 1, true, p };
    return (PdDesc){ 1, 0, g };
}

/* `l` followed by `r`, as one group: `r`'s stored positions, preceded by
 * as many of `l`'s last ones as fit, where `r` stores its whole width (a
 * truncated `r` has a gap before its first stored position). */
static PdGroup pd_cat_group(Ctx *cx, const PdCfg *c, const PdGroup *l,
                            const PdGroup *r)
{
    PdGroup o = { l->w + r->w, r->n, false, r->pos };
    if (r->n == r->w && r->n < c->max_pos && l->n > 0) {
        int k = l->n < c->max_pos - r->n ? l->n : c->max_pos - r->n;
        const void **p = pcrec_arena_alloc(&cx->arena, (size_t)(k + r->n) * sizeof *p);
        memcpy(p, l->pos + (l->n - k), (size_t)k * sizeof *p);
        memcpy(p + k, r->pos, (size_t)r->n * sizeof *p);
        o.pos = p;
        o.n = k + r->n;
    }
    o.exact = l->exact && r->exact && o.n == o.w;
    return o;
}

/* The hull merge of two groups of one width (the header's statement). */
static PdGroup pd_hull(Ctx *cx, const PdCfg *c, const PdGroup *a,
                       const PdGroup *b)
{
    int n = a->n < b->n ? a->n : b->n, diff = 0;
    const void **p = pcrec_arena_alloc(&cx->arena, (size_t)(n ? n : 1) * sizeof *p);
    for (int i = 0; i < n; i++) {
        const void *x = a->pos[a->n - n + i], *y = b->pos[b->n - n + i];
        if (!c->alpha->same(x, y)) diff++;
        p[i] = c->alpha->join(cx, x, y);
    }
    return (PdGroup){ a->w, n, a->exact && b->exact && n == a->w && diff <= 1, p };
}

/* `g[0..n)` sorted by width, equal widths hull-merged, into a description;
 * over the group bound, none. */
static PdDesc pd_norm(Ctx *cx, const PdCfg *c, PdGroup *g, int n)
{
    for (int i = 1; i < n; i++)
        for (int j = i; j > 0 && g[j - 1].w > g[j].w; j--) {
            PdGroup t = g[j]; g[j] = g[j - 1]; g[j - 1] = t;
        }
    int m = 0;
    for (int i = 0; i < n; i++) {
        if (m && g[m - 1].w == g[i].w) g[m - 1] = pd_hull(cx, c, &g[m - 1], &g[i]);
        else g[m++] = g[i];
    }
    if (m > c->max_groups) return (PdDesc){ -1, PD_OVER, NULL };
    return (PdDesc){ m, 0, g };
}

/* A description that reached either side's drop stays dropped, with the
 * first reason seen. */
static bool pd_dropped(PdDesc l, PdDesc r, PdDesc *o)
{
    if (l.ng >= 0 && r.ng >= 0) return false;
    *o = (PdDesc){ -1, l.ng < 0 ? l.why : r.why, NULL };
    return true;
}

PdDesc pcrec_pd_cat(Ctx *cx, const PdCfg *c, PdDesc l, PdDesc r)
{
    PdDesc o;
    if (pd_dropped(l, r, &o)) return o;
    /* The unit is the identity; a `zero` group is not, since the product
     * below carries its inexactness into every group. */
    if (l.ng == 1 && l.g[0].w == 0 && l.g[0].exact) return r;
    if (r.ng == 1 && r.g[0].w == 0 && r.g[0].exact) return l;
    long long n = (long long)l.ng * r.ng;
    if (n > c->max_groups * (long long)c->max_groups)
        return (PdDesc){ -1, PD_OVER, NULL };
    PdGroup *g = pcrec_arena_alloc(&cx->arena, (size_t)n * sizeof *g);
    int k = 0;
    for (int i = 0; i < l.ng; i++)
        for (int j = 0; j < r.ng; j++) g[k++] = pd_cat_group(cx, c, &l.g[i], &r.g[j]);
    return pd_norm(cx, c, g, k);
}

PdDesc pcrec_pd_alt(Ctx *cx, const PdCfg *c, PdDesc l, PdDesc r)
{
    PdDesc o;
    if (pd_dropped(l, r, &o)) return o;
    PdGroup *g = pcrec_arena_alloc(&cx->arena, (size_t)(l.ng + r.ng) * sizeof *g);
    memcpy(g, l.g, (size_t)l.ng * sizeof *g);
    memcpy(g + l.ng, r.g, (size_t)r.ng * sizeof *g);
    return pd_norm(cx, c, g, l.ng + r.ng);
}

/* ---- the adjacency head ---------------------------------------------- */

PdHead pcrec_ph_unit(void)
{
    return (PdHead){ 0, true, true, false, 0, 0, NULL };
}

PdHead pcrec_ph_pos(Ctx *cx, const void *pos)
{
    const void **p = pcrec_arena_alloc(&cx->arena, sizeof *p);
    p[0] = pos;
    return (PdHead){ 1, true, true, false, 1, 1, p };
}

PdHead pcrec_ph_wall(long long minw, bool bounded, long long maxw, bool writes)
{
    return (PdHead){ 0, false, bounded, writes, minw, bounded ? maxw : 0, NULL };
}

/* `l` followed by `r`: `l`'s head, continued by `r`'s where `l` is closed. */
PdHead pcrec_ph_cat(Ctx *cx, const PdCfg *c, PdHead l, PdHead r)
{
    PdHead o = l;
    o.writes = l.writes || r.writes;
    o.minw = l.minw + r.minw;
    o.bounded = l.bounded && r.bounded;
    o.maxw = o.bounded ? l.maxw + r.maxw : 0;
    if (!l.closed) return o;
    int k = r.h < c->max_pos - l.h ? r.h : c->max_pos - l.h;
    if (k > 0 && l.h == 0) {
        o.pos = r.pos;
    } else if (k > 0) {
        const void **p = pcrec_arena_alloc(&cx->arena, (size_t)(l.h + k) * sizeof *p);
        memcpy(p, l.pos, (size_t)l.h * sizeof *p);
        memcpy(p + l.h, r.pos, (size_t)k * sizeof *p);
        o.pos = p;
    }
    o.h = l.h + k;
    o.closed = r.closed && k == r.h;
    return o;
}

/* `l` or `r`: the position-wise union over the heads both have. */
PdHead pcrec_ph_alt(Ctx *cx, const PdCfg *c, PdHead l, PdHead r)
{
    int h = l.h < r.h ? l.h : r.h;
    const void **p = NULL;
    if (h > 0) {
        p = pcrec_arena_alloc(&cx->arena, (size_t)h * sizeof *p);
        for (int i = 0; i < h; i++) p[i] = c->alpha->join(cx, l.pos[i], r.pos[i]);
    }
    bool bounded = l.bounded && r.bounded;
    return (PdHead){ h, l.closed && r.closed && l.minw == r.minw, bounded,
                     l.writes || r.writes, l.minw < r.minw ? l.minw : r.minw,
                     bounded ? (l.maxw > r.maxw ? l.maxw : r.maxw) : 0, p };
}
