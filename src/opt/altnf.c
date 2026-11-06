/* [RUN-POS-SET] THE ALTERNATION OWNER: one rewrite procedure for an
 * alternation's branch list (docs/design/alt_normal_form.md §3.2, §3.3; D-next
 * in §12). A pure function from a branch list in PREFERENCE ORDER and the
 * caller's RULE SET to a rewritten list; it reads no option and no prior (a
 * denied rule is removed from the rule set by the caller, §11), allocates only
 * new nodes, and knows no encoding: a position is a class node, whose interval
 * list is a set over whatever alphabet the caller's level has (code points
 * above the lowering, bytes inside it).
 *
 * TWO CALLERS, TWO RULE SETS (§3.3 "Rule sets per caller"). The lowering
 * (`lower_class_utf8`, byte level) hands its UTF-8 boxes with {M}; altcls
 * (code-point level, before the call graph) hands every alternation spine it
 * walks with {M, P, S}. THE PROCEDURE over one list is ROUNDS of M to its
 * fixpoint, then P, then S; P's rests and S's heads are themselves lists the
 * procedure runs on (`anf_list`, recursion on split depth only, bounded by
 * `PCREC_MAX_ALTCLS_FACTOR_DEPTH`); a round that P or S changed is followed
 * by another, and every rule strictly lowers the list's position count, so
 * the rounds end.
 *
 * WHAT M DOES. Two MERGEABLE branches (fixed-position set sequences: a class,
 * or a left-nested `A_CAT` spine of classes) of one width `w` that are equal
 * at every position but `p` become one branch with the union at `p`. The later
 * branch `j` MOVES UP into the earlier slot `i`, past every branch `m` between
 * them, and the one adjacency test (`anf_passes`, §3.2's table) decides
 * whether that move can change an answer. ORDER, declared (§3.3 "Order"): for
 * each width ascending, positions LAST FIRST, sweeps repeated until a full
 * sweep folds nothing. The result is a reproducible reduction, not a canonical
 * form; Gate U1b pins its box counts on the widest classes.
 *
 * DUPLICATES. A mergeable branch identical at every position to an EARLIER
 * mergeable branch is dead whatever lies between (the same string meets the
 * same continuation and fails as the earlier copy did), so it is dropped with
 * no reach test (§3.3 step 1, r7 SIM-1).
 *
 * P, PREFIX FACTORING. A maximal run of at least two CONSECUTIVE branches
 * whose first spine element is an equal class becomes `K(?:rests)`, `K` the
 * longest run of equal leading CLASS elements (fixed-width, capture-free,
 * single-way: §3.2's condition by construction; never read through a
 * zero-width node, r7 SND-3), a branch equal to `K` an EMPTY in its slot.
 *
 * S, SUFFIX FACTORING. A maximal run of at least two ADJACENT branches whose
 * last spine elements are IDENTICAL nodes (`anf_node_same`: a kind it does
 * not compare is never identical, the sound direction) becomes `(?:heads)C`,
 * `C` the longest common identical suffix (right distributivity keeps the
 * tried order exactly, §3.2).
 *
 * THE ADJACENCY HEAD of a branch that is not mergeable (any `m` the test
 * meets) is the description module's head column (src/facts/desc.h
 * `PdHead`), built here by one walk per branch (`anf_head`) and read by rows
 * 1 and 2; its arms are §3.5 FIX-2's table.
 *
 * COST. Grouping is by a hash of the all-but-`p` key, so a sweep is O(n·w)
 * plus the adjacency checks of each attempted fold. A span whose every live
 * branch is mergeable of width `w` passes row 2 whole, read in O(1) from a
 * prefix count; only a span holding another width or a non-mergeable branch
 * walks its branches. The lowering's boxes come in ascending code point, so
 * their widths are contiguous and every span takes the O(1) path. A mixed-
 * width user list walks (§3.3 SIM-3), so the WORK of one call (adjacency
 * tests plus interval comparisons, `anf_tick`) is bounded by
 * `PCREC_MAX_ALTNF_WORK`; past it the call stops rewriting and leaves the
 * rest of its lists as they are (a decline, never a refusal). */
#include "../core/internal.h"
#include "facts/desc.h"

#include <string.h>

/* One branch of the list under rewrite. */
typedef struct {
    Ast        *node;   /* the branch as given; replaced only when `dirty` */
    const Ast **pos;    /* MERGEABLE: its `w` class nodes, left to right */
    unsigned   *ph;     /* MERGEABLE: one hash per position (anf_cls_hash) */
    int         w;      /* MERGEABLE: its width in positions */
    bool        merge;  /* a fixed-position set sequence */
    bool        dirty;  /* a position was widened by a fold */
    bool        dead;   /* folded into a head, or dropped as a duplicate */
    bool        hd_set; /* NOT MERGEABLE: `hd` is computed (on first need) */
    PdHead      hd;     /* NOT MERGEABLE: its adjacency head (§3.5) */
} AnfBr;

/* One call's state: the rules, the work spent against the bound, the split
 * depth of the list in hand, and the caller's counters. */
typedef struct {
    Ctx            *cx;
    PcrecAnfRules   rules;
    PdCfg           pd;
    long long       work;
    int             depth;
    PcrecAnfStats  *st;
} AnfRun;

/* Charges `n` units of work; false once the call is over its bound. */
static bool anf_tick(AnfRun *r, long long n)
{
    r->work += n;
    return r->work <= (long long)PCREC_MAX_ALTNF_WORK;
}

/* A hash of class `a`'s interval list, the key unit of the grouping. */
static unsigned anf_cls_hash(const Ast *a)
{
    unsigned h = 2166136261u;
    for (int i = 0; i < a->u.cls.n; i++) {
        h = (h ^ a->u.cls.iv[i].lo) * 16777619u;
        h = (h ^ a->u.cls.iv[i].hi) * 16777619u;
    }
    return h ^ (unsigned)a->u.cls.n;
}

/* Do classes `a` and `b` hold the same set? Published lists are normalized
 * (sorted, disjoint, non-adjacent), so equal sets are equal lists. */
static bool anf_cls_eq(const Ast *a, const Ast *b)
{
    if (a == b) return true;
    if (a->u.cls.n != b->u.cls.n) return false;
    for (int i = 0; i < a->u.cls.n; i++)
        if (a->u.cls.iv[i].lo != b->u.cls.iv[i].lo ||
            a->u.cls.iv[i].hi != b->u.cls.iv[i].hi) return false;
    return true;
}

/* Do classes `a` and `b` share no member? A merge walk over two sorted lists. */
static bool anf_cls_disjoint(const Ast *a, const Ast *b)
{
    int i = 0, k = 0;
    while (i < a->u.cls.n && k < b->u.cls.n) {
        const PcrecCpRange *x = &a->u.cls.iv[i], *y = &b->u.cls.iv[k];
        if (x->hi < y->lo) i++;
        else if (y->hi < x->lo) k++;
        else return false;
    }
    return true;
}

/* A new class node holding the union of `a` and `b`. */
static const Ast *anf_cls_union(Ctx *cx, const Ast *a, const Ast *b)
{
    if (anf_cls_eq(a, b)) return a;
    Ast *u = pcrec_ast_node(cx, A_CLASS);
    PcrecCpSet s;
    pcrec_cpset_init(&s, &cx->arena);
    pcrec_cpset_add_set(&s, a->u.cls.iv, a->u.cls.n);
    pcrec_cpset_add_set(&s, b->u.cls.iv, b->u.cls.n);
    pcrec_cpset_publish(&s, u);
    return u;
}

/* The code-point alphabet of the head column: a position is a class node. */
static const void *anf_pd_join(Ctx *cx, const void *a, const void *b)
{
    return anf_cls_union(cx, a, b);
}

static bool anf_pd_same(const void *a, const void *b)
{
    return anf_cls_eq(a, b);
}

static const PdAlpha anf_pd_cls = { anf_pd_join, anf_pd_same };

/* `x * k` for a width, saturating: past it the width is unbounded. */
static bool anf_wmul(long long x, int k, long long *out)
{
    if (k != 0 && x > (1LL << 40) / k) return false;
    *out = x * k;
    return true;
}

/* THE ADJACENCY HEAD of `a` (§3.5 FIX-2's column; desc.h `PdHead`), one walk:
 * spines iterative, recursion on nesting only. A zero-width node is read
 * THROUGH; a repeat contributes no head (FIX-1: `rmin >= 1` included, a REP
 * head waits for [REPEAT-RUN]); a backreference, a variable, a `consume`
 * callout and a call have no head and unknown writes (row 3); a call reads
 * no cached field (FIX-3: unset before the call graph). */
static PdHead anf_head(const AnfRun *r, const Ast *a)
{
    switch (a->k) {
    case A_CLASS:
        return pcrec_ph_pos(r->cx, a);
    case A_EMPTY:
    case A_EOL:
    case A_CTX:
    case A_GSTART:
        return pcrec_ph_unit();
    case A_KRESET: {
        PdHead u = pcrec_ph_unit();
        u.writes = true;
        return u;
    }
    case A_CALLOUT:
        if (pcrec_ast_row(a).text == KTEXT_ANY)
            return pcrec_ph_wall(0, false, 0, true);
        return pcrec_ph_unit();
    case A_LOOK: {
        PdHead u = pcrec_ph_unit();
        u.writes = anf_head(r, a->l).writes;
        return u;
    }
    case A_BREF:
    case A_VAR:
    case A_CALL:
    case A_WCLASS:
        return pcrec_ph_wall(0, false, 0, true);
    case A_CAP: {
        PdHead b = anf_head(r, a->l);
        b.writes = true;
        return b;
    }
    case A_ATOMIC:
        return anf_head(r, a->l);
    case A_REP: {
        PdHead b = anf_head(r, a->l);
        long long lo = 0, hi = 0;
        if (!anf_wmul(b.minw, a->u.rep.rmin, &lo)) lo = 1LL << 40;
        bool bounded = b.bounded && a->u.rep.rmax >= 0 &&
                       anf_wmul(b.maxw, a->u.rep.rmax, &hi);
        return pcrec_ph_wall(lo, bounded, hi, b.writes);
    }
    case A_CAT: {
        PdHead acc = pcrec_ph_unit();
        PCREC_SPINE_EACH(e, a, A_CAT)
            acc = pcrec_ph_cat(r->cx, &r->pd, anf_head(r, e), acc);
        return acc;
    }
    case A_ALT: {
        PdHead acc = { 0 };
        bool first = true;
        PCREC_SPINE_EACH(e, a, A_ALT) {
            PdHead b = anf_head(r, e);
            acc = first ? b : pcrec_ph_alt(r->cx, &r->pd, b, acc);
            first = false;
        }
        return acc;
    }
    }
    return pcrec_ph_wall(0, false, 0, true);   /* unreachable under -Wswitch */
}

/* Fills `b` from branch `a`: a fixed-position set sequence (a class, or a
 * left-nested `A_CAT` spine whose every element is a class) is MERGEABLE and
 * gets its positions; anything else is kept whole and only ever passed over. */
static void anf_describe(Ctx *cx, AnfBr *b, Ast *a)
{
    memset(b, 0, sizeof *b);
    b->node = a;
    if (a->k == A_EMPTY) {          /* the empty sequence, width 0 (r7 SIM-5) */
        b->merge = true;
        return;
    }
    int w = 0;
    PCREC_SPINE_EACH(e, a, A_CAT) {
        if (e->k != A_CLASS) return;
        w++;
    }
    b->pos = pcrec_arena_alloc(&cx->arena, (size_t)w * sizeof *b->pos);
    b->ph  = pcrec_arena_alloc(&cx->arena, (size_t)w * sizeof *b->ph);
    int i = w;
    PCREC_SPINE_EACH(e, a, A_CAT) {
        b->pos[--i] = e;
        b->ph[i] = anf_cls_hash(e);
    }
    b->w = w;
    b->merge = true;
}

/* Is position `i` part of the grouping key that excludes position `p`? The
 * one statement of "equal everywhere but `p`", read by the hash and the
 * equality test alike. */
static bool anf_in_key(int i, int p)
{
    return i != p;
}

/* The all-but-`p` key hash of mergeable branch `b` (`p` = -1: every position). */
static unsigned anf_key(const AnfBr *b, int p)
{
    unsigned h = (unsigned)b->w * 0x9e3779b9u;
    for (int i = 0; i < b->w; i++)
        if (anf_in_key(i, p)) h = (h ^ b->ph[i]) * 0x01000193u + (unsigned)i;
    return h;
}

/* Are mergeable branches `a` and `b` (one width) equal at every position but
 * `p` (`p` = -1: at every position)? */
static bool anf_key_eq(const AnfBr *a, const AnfBr *b, int p)
{
    if (a->w != b->w) return false;
    for (int i = 0; i < a->w; i++)
        if (anf_in_key(i, p) && !anf_cls_eq(a->pos[i], b->pos[i])) return false;
    return true;
}

/* THE ADJACENCY TEST (§3.2, first match): may mergeable branch `j` move up
 * past live branch `m`? Row 1: `m`'s head is disjoint from `j` at some
 * position both have, so `m` cannot match where `j` does. Row 2: every way of
 * `m` consumes exactly `j`'s width and `m` writes nothing, so only a
 * same-span match is possible and nothing observable differs. Row 3:
 * anything else REFUSES. A mergeable `m` is its own head (a set sequence:
 * one width, no capture, no `\K`); any other `m` is read through its
 * adjacency head (`anf_head`). */
static bool anf_passes(AnfRun *r, AnfBr *m, const AnfBr *j)
{
    if (!m->merge && !m->hd_set) {
        m->hd = anf_head(r, m->node);
        m->hd_set = true;
    }
    int mh = m->merge ? m->w : m->hd.h;
    int h = mh < j->w ? mh : j->w;
    for (int p = 0; p < h; p++) {
        const Ast *mp = m->merge ? m->pos[p] : m->hd.pos[p];
        if (!anf_tick(r, 1 + mp->u.cls.n + j->pos[p]->u.cls.n)) return false;
        if (anf_cls_disjoint(mp, j->pos[p])) return true;          /* row 1 */
    }
    if (m->merge) return m->w == j->w;                      /* row 2 / 3 */
    return m->hd.minw == j->w && m->hd.bounded && m->hd.maxw == j->w &&
           !m->hd.writes;                                   /* row 2 / 3 */
}

/* Does `j = b[to]` reach slot `from`: does it pass the adjacency test against
 * every live branch strictly between? `other` is the prefix count of branches
 * that are not mergeable of `j`'s width (row 2's whole-span fast path). */
static bool anf_reach(AnfRun *r, AnfBr *b, const int *other, int from, int to)
{
    if (!anf_tick(r, 1)) return false;
    if (other[to] - other[from + 1] == 0) return true;
    for (int m = from + 1; m < to; m++)
        if (!b[m].dead && !anf_passes(r, &b[m], &b[to])) return false;
    return true;
}

/* An open-addressing-free bucket map from a key hash to the latest HEAD with
 * that hash; heads with one hash chain through `prev` in list order. */
typedef struct {
    int      *bucket;   /* [mask + 1]: latest head index, or -1 */
    int      *prev;     /* [n]: the previous head in the same bucket, or -1 */
    unsigned *key;      /* [n]: the head's key hash */
    unsigned  mask;
} AnfHeads;

/* An empty head map for a list of `n` branches. */
static void anf_heads_init(Ctx *cx, AnfHeads *t, int n)
{
    unsigned sz = 16;
    while (sz < 2u * (unsigned)n) sz <<= 1;
    t->mask = sz - 1;
    t->bucket = pcrec_arena_alloc(&cx->arena, sz * sizeof *t->bucket);
    t->prev   = pcrec_arena_alloc(&cx->arena, (size_t)n * sizeof *t->prev);
    t->key    = pcrec_arena_alloc(&cx->arena, (size_t)n * sizeof *t->key);
    for (unsigned i = 0; i < sz; i++) t->bucket[i] = -1;
}

/* Drops every mergeable branch identical to an earlier live mergeable one;
 * returns how many. */
static int anf_drop_dups(Ctx *cx, AnfBr *b, int n)
{
    int drops = 0;
    AnfHeads t;
    anf_heads_init(cx, &t, n);
    for (int j = 0; j < n; j++) {
        if (b[j].dead || !b[j].merge) continue;
        unsigned k = anf_key(&b[j], -1);
        int *slot = &t.bucket[k & t.mask];
        bool dup = false;
        for (int h = *slot; h >= 0 && !dup; h = t.prev[h])
            dup = t.key[h] == k && anf_key_eq(&b[h], &b[j], -1);
        if (dup) { b[j].dead = true; drops++; continue; }
        t.key[j] = k;
        t.prev[j] = *slot;
        *slot = j;
    }
    return drops;
}

/* One (width `w`, position `p`) pass of step M: each mergeable width-`w`
 * branch, in list order, folds into the EARLIEST head of its all-but-`p` group
 * it can reach (heads tried from the last backwards, stopping at the first
 * refusal: reach is monotone), or becomes a head. Returns the folds made. */
static int anf_merge_pass(AnfRun *r, AnfBr *b, int n, int w, int p, int *other)
{
    Ctx *cx = r->cx;
    other[0] = 0;
    for (int i = 0; i < n; i++)
        other[i + 1] = other[i] + (!b[i].dead && !(b[i].merge && b[i].w == w));

    AnfHeads t;
    anf_heads_init(cx, &t, n);
    int folds = 0;
    for (int j = 0; j < n; j++) {
        if (b[j].dead || !b[j].merge || b[j].w != w) continue;
        unsigned k = anf_key(&b[j], p);
        int *slot = &t.bucket[k & t.mask];
        int into = -1;
        for (int h = *slot; h >= 0; h = t.prev[h]) {
            if (t.key[h] != k || !anf_key_eq(&b[h], &b[j], p)) continue;
            if (!anf_reach(r, b, other, h, j)) break;
            into = h;
        }
        if (into >= 0) {
            b[into].pos[p] = anf_cls_union(cx, b[into].pos[p], b[j].pos[p]);
            b[into].dirty = true;
            b[j].dead = true;
            folds++;
            continue;
        }
        t.key[j] = k;
        t.prev[j] = *slot;
        *slot = j;
    }
    /* A fold widened a head at `p`; its hash there is re-read once, here. */
    for (int i = 0; i < n; i++)
        if (!b[i].dead && b[i].merge && b[i].w == w)
            b[i].ph[p] = anf_cls_hash(b[i].pos[p]);
    return folds;
}

/* Step M to its fixpoint (§3.3): duplicates dropped, then every width
 * ascending and every position last first, swept until nothing folds. */
static int anf_merge(AnfRun *r, AnfBr *b, int n)
{
    Ctx *cx = r->cx;
    int maxw = 0, folds = 0;
    for (int i = 0; i < n; i++)
        if (b[i].merge && b[i].w > maxw) maxw = b[i].w;
    int *other = pcrec_arena_alloc(&cx->arena, (size_t)(n + 1) * sizeof *other);
    bool *has = pcrec_arena_alloc(&cx->arena, (size_t)(maxw + 1) * sizeof *has);
    for (int i = 0; i < n; i++)
        if (b[i].merge) has[b[i].w] = true;

    folds = anf_drop_dups(cx, b, n);
    for (;;) {
        int swept = 0;
        for (int w = 1; w <= maxw; w++) {
            if (!has[w]) continue;
            for (int p = w - 1; p >= 0; p--)
                swept += anf_merge_pass(r, b, n, w, p, other);
        }
        if (swept == 0) break;
        folds += swept;
    }
    return folds;
}

/* Branch `b` rebuilt from its positions: the class itself at width 1, else a
 * left-nested `A_CAT` spine, p_cat's own shape. */
static Ast *anf_rebuild(Ctx *cx, const AnfBr *b)
{
    Ast *res = (Ast *)b->pos[0];
    for (int i = 1; i < b->w; i++) {
        Ast *cat = pcrec_ast_node(cx, A_CAT);
        cat->l = res;
        cat->r = (Ast *)b->pos[i];
        res = cat;
    }
    return res;
}

/* Step M over the list `br[0..*n)`, compacted in place; returns the folds
 * (a dropped duplicate counts as one). */
static int anf_merge_list(AnfRun *r, Ast **br, int *n)
{
    AnfBr *b = pcrec_arena_alloc(&r->cx->arena, (size_t)*n * sizeof *b);
    for (int i = 0; i < *n; i++) anf_describe(r->cx, &b[i], br[i]);
    int nf = anf_merge(r, b, *n);
    int out = 0;
    for (int i = 0; i < *n; i++)
        if (!b[i].dead)
            br[out++] = b[i].dirty ? anf_rebuild(r->cx, &b[i]) : b[i].node;
    *n = out;
    return nf;
}

/* ---- rules P and S: spines as element arrays -------------------------- */

/* Branch `a`'s CAT spine, left to right (a non-CAT node is a spine of one). */
static int anf_flatten(Ctx *cx, const Ast *a, Ast ***out)
{
    int n = 0;
    PCREC_SPINE_EACH(e, a, A_CAT) { (void)e; n++; }
    Ast **arr = pcrec_arena_alloc(&cx->arena, (size_t)n * sizeof *arr);
    int i = n;
    PCREC_SPINE_EACH(e, a, A_CAT) arr[--i] = (Ast *)e;
    *out = arr;
    return n;
}

/* A left-nested `A_CAT` spine of `arr[0..n)`, p_cat's shape; EMPTY at 0. */
static Ast *anf_cat(Ctx *cx, Ast *const *arr, int n)
{
    if (n == 0) return pcrec_ast_node(cx, A_EMPTY);
    Ast *res = arr[0];
    for (int i = 1; i < n; i++) {
        Ast *cat = pcrec_ast_node(cx, A_CAT);
        cat->l = res;
        cat->r = arr[i];
        res = cat;
    }
    return res;
}

/* A left-nested `A_ALT` spine of `arr[0..n)`, n >= 1. */
static Ast *anf_alt(Ctx *cx, Ast *const *arr, int n)
{
    Ast *res = arr[0];
    for (int i = 1; i < n; i++) {
        Ast *alt = pcrec_ast_node(cx, A_ALT);
        alt->l = res;
        alt->r = arr[i];
        res = alt;
    }
    return res;
}

/* Are nodes `a` and `b` IDENTICAL for suffix factoring (§3.2: the same node,
 * every capture index included)? Only kinds whose whole payload is compared
 * here can be; any other kind is never identical (a decline, the sound
 * direction): a capture (no two branches share an index, branch reset being
 * refused), a lookaround, a callout, a call, `\K`. Spines walk iteratively. */
static bool anf_node_same(AnfRun *r, const Ast *a, const Ast *b)
{
    for (;;) {
        if (a == b) return true;
        if (a->k != b->k || !anf_tick(r, 1)) return false;
        switch (a->k) {
        case A_CLASS:
            if (!anf_tick(r, a->u.cls.n)) return false;
            return anf_cls_eq(a, b);
        case A_EMPTY:
            return true;
        case A_CTX:
            if (a->u.ctx.fn != b->u.ctx.fn || a->u.ctx.anchor != b->u.ctx.anchor ||
                a->u.ctx.written || b->u.ctx.written ||
                a->u.ctx.n != b->u.ctx.n || !anf_tick(r, a->u.ctx.n)) return false;
            for (int i = 0; i < a->u.ctx.n; i++)
                if (a->u.ctx.iv[i].lo != b->u.ctx.iv[i].lo ||
                    a->u.ctx.iv[i].hi != b->u.ctx.iv[i].hi) return false;
            return true;
        case A_REP:
            if (a->u.rep.rmin != b->u.rep.rmin || a->u.rep.rmax != b->u.rep.rmax ||
                a->u.rep.greedy != b->u.rep.greedy ||
                a->u.rep.possessive != b->u.rep.possessive) return false;
            a = a->l;
            b = b->l;
            continue;
        case A_CAT:
        case A_ALT:
            if (!anf_node_same(r, a->r, b->r)) return false;
            a = a->l;
            b = b->l;
            continue;
        case A_EOL:
        case A_GSTART:
        case A_KRESET:
        case A_LOOK:
        case A_BREF:
        case A_VAR:
        case A_CALLOUT:
        case A_CALL:
        case A_CAP:
        case A_ATOMIC:
        case A_WCLASS:
            return false;
        }
        return false;   /* unreachable under -Wswitch */
    }
}

static int anf_list(AnfRun *r, Ast **br, int n);

/* The list `sub[0..m)` a rule just created, run through the procedure one
 * split deeper (past the depth bound it stays as it is), then spelled as
 * the element sequence it contributes to its branch: nothing for a lone
 * EMPTY, the spine of a lone branch, else one alternation. */
static int anf_sublist(AnfRun *r, Ast **sub, int m, Ast ***elems)
{
    if (r->depth < PCREC_MAX_ALTCLS_FACTOR_DEPTH) {
        r->depth++;
        m = anf_list(r, sub, m);
        r->depth--;
    }
    if (m == 1 && sub[0]->k == A_EMPTY) { *elems = NULL; return 0; }
    if (m == 1) return anf_flatten(r->cx, sub[0], elems);
    Ast **one = pcrec_arena_alloc(&r->cx->arena, sizeof *one);
    one[0] = anf_alt(r->cx, sub, m);
    *elems = one;
    return 1;
}

/* Rule P over `br[0..*n)`; true when it factored a run. */
static bool anf_prefix(AnfRun *r, Ast **br, int *n)
{
    Ctx *cx = r->cx;
    Ast ***el = pcrec_arena_alloc(&cx->arena, (size_t)*n * sizeof *el);
    int *len = pcrec_arena_alloc(&cx->arena, (size_t)*n * sizeof *len);
    for (int i = 0; i < *n; i++) len[i] = anf_flatten(cx, br[i], &el[i]);
    int out = 0, i = 0;
    bool changed = false;
    while (i < *n) {
        int j = i + 1;
        if (el[i][0]->k == A_CLASS)
            while (j < *n && el[j][0]->k == A_CLASS && anf_tick(r, 1 + el[j][0]->u.cls.n) &&
                   anf_cls_eq(el[i][0], el[j][0])) j++;
        if (j - i < 2) { br[out++] = br[i++]; continue; }
        int k = 1;
        for (;;) {
            bool all = true;
            for (int x = i; x < j && all; x++)
                all = len[x] > k && el[x][k]->k == A_CLASS && len[i] > k &&
                      el[i][k]->k == A_CLASS && anf_tick(r, 1 + el[x][k]->u.cls.n) &&
                      anf_cls_eq(el[i][k], el[x][k]);
            if (!all) break;
            k++;
        }
        Ast **rest = pcrec_arena_alloc(&cx->arena, (size_t)(j - i) * sizeof *rest);
        for (int x = i; x < j; x++) rest[x - i] = anf_cat(cx, el[x] + k, len[x] - k);
        Ast **tail;
        int nt = anf_sublist(r, rest, j - i, &tail);
        Ast **nb = pcrec_arena_alloc(&cx->arena, (size_t)(k + nt) * sizeof *nb);
        memcpy(nb, el[i], (size_t)k * sizeof *nb);
        if (nt) memcpy(nb + k, tail, (size_t)nt * sizeof *nb);
        br[out++] = anf_cat(cx, nb, k + nt);
        if (r->st) r->st->factored++;
        changed = true;
        i = j;
    }
    *n = out;
    return changed;
}

/* Rule S over `br[0..*n)`, P's mirror; true when it factored a run. */
static bool anf_suffix(AnfRun *r, Ast **br, int *n)
{
    Ctx *cx = r->cx;
    Ast ***el = pcrec_arena_alloc(&cx->arena, (size_t)*n * sizeof *el);
    int *len = pcrec_arena_alloc(&cx->arena, (size_t)*n * sizeof *len);
    for (int i = 0; i < *n; i++) len[i] = anf_flatten(cx, br[i], &el[i]);
    int out = 0, i = 0;
    bool changed = false;
    while (i < *n) {
        int j = i + 1;
        if (el[i][len[i] - 1]->k != A_EMPTY)
            while (j < *n && anf_node_same(r, el[i][len[i] - 1], el[j][len[j] - 1])) j++;
        if (j - i < 2) { br[out++] = br[i++]; continue; }
        int s = 1;
        for (;;) {
            bool all = len[i] > s;
            for (int x = i + 1; x < j && all; x++)
                all = len[x] > s &&
                      anf_node_same(r, el[i][len[i] - 1 - s], el[x][len[x] - 1 - s]);
            if (!all) break;
            s++;
        }
        Ast **head = pcrec_arena_alloc(&cx->arena, (size_t)(j - i) * sizeof *head);
        for (int x = i; x < j; x++) head[x - i] = anf_cat(cx, el[x], len[x] - s);
        Ast **lead;
        int nl = anf_sublist(r, head, j - i, &lead);
        Ast **nb = pcrec_arena_alloc(&cx->arena, (size_t)(nl + s) * sizeof *nb);
        if (nl) memcpy(nb, lead, (size_t)nl * sizeof *nb);
        memcpy(nb + nl, el[i] + len[i] - s, (size_t)s * sizeof *nb);
        br[out++] = anf_cat(cx, nb, nl + s);
        if (r->st) r->st->factored++;
        changed = true;
        i = j;
    }
    *n = out;
    return changed;
}

/* THE PROCEDURE (§3.3) over the list `br[0..n)`, in place; returns the new
 * count. Rounds of M, P, S until a round's P and S change nothing; a list in
 * which M folded at least once is counted once (`merge_lists`). */
static int anf_list(AnfRun *r, Ast **br, int n)
{
    bool merged = false;
    for (;;) {
        if (r->rules.merge && n > 1 && anf_merge_list(r, br, &n) > 0) merged = true;
        bool changed = false;
        if (r->rules.prefix && n > 1 && anf_tick(r, n)) changed |= anf_prefix(r, br, &n);
        if (r->rules.suffix && n > 1 && anf_tick(r, n)) changed |= anf_suffix(r, br, &n);
        if (!changed) break;
    }
    if (merged && r->st) r->st->merge_lists++;
    return n;
}

int pcrec_altnf(Ctx *cx, Ast **br, int n, PcrecAnfRules rules, PcrecAnfStats *st)
{
    AnfRun r = { cx, rules, { &anf_pd_cls, 0, PCREC_MAX_REQ_RUN_SCAN }, 0, 0, st };
    return anf_list(&r, br, n);
}
