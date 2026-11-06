/* [RUN-POS-SET] THE ALTERNATION OWNER: one rewrite procedure for an
 * alternation's branch list (docs/design/alt_normal_form.md §3.2, §3.3; D-next
 * in §12). A pure function from a branch list in PREFERENCE ORDER and the
 * caller's RULE SET to a rewritten list; it reads no option and no prior (a
 * denied rule is removed from the rule set by the caller, §11), allocates only
 * new nodes, and knows no encoding: a position is a class node, whose interval
 * list is a set over whatever alphabet the caller's level has (code points
 * above the lowering, bytes inside it).
 *
 * TODAY'S RULE SET IS {M}, SIBLING MERGE (stage 1: `lower_class_utf8` hands
 * its UTF-8 boxes here). Prefix and suffix factoring (rules P and S, the
 * altcls caller) are stage 2b's; their fields exist so a caller states its set.
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
 * COST. Grouping is by a hash of the all-but-`p` key, so a sweep is O(n·w)
 * plus the adjacency checks of each attempted fold. A span whose every live
 * branch is mergeable of width `w` passes row 2 whole, read in O(1) from a
 * prefix count; only a span holding another width or a non-mergeable branch
 * walks its branches. The lowering's boxes come in ascending code point, so
 * their widths are contiguous and every span takes the O(1) path. Stage 2b's
 * mixed-width user lists are where the walk costs (§3.3 SIM-3); its work
 * bound arrives with that caller. */
#include "../core/internal.h"

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
} AnfBr;

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
    Ast *u = pcrec_ast_node(cx, A_CLASS);
    PcrecCpSet s;
    pcrec_cpset_init(&s, &cx->arena);
    pcrec_cpset_add_set(&s, a->u.cls.iv, a->u.cls.n);
    pcrec_cpset_add_set(&s, b->u.cls.iv, b->u.cls.n);
    pcrec_cpset_publish(&s, u);
    return u;
}

/* Fills `b` from branch `a`: a fixed-position set sequence (a class, or a
 * left-nested `A_CAT` spine whose every element is a class) is MERGEABLE and
 * gets its positions; anything else is kept whole and only ever passed over. */
static void anf_describe(Ctx *cx, AnfBr *b, Ast *a)
{
    memset(b, 0, sizeof *b);
    b->node = a;
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

/* The all-but-`p` key hash of mergeable branch `b` (`p` = -1: every position). */
static unsigned anf_key(const AnfBr *b, int p)
{
    unsigned h = (unsigned)b->w * 0x9e3779b9u;
    for (int i = 0; i < b->w; i++)
        if (i != p) h = (h ^ b->ph[i]) * 0x01000193u + (unsigned)i;
    return h;
}

/* Are mergeable branches `a` and `b` (one width) equal at every position but
 * `p` (`p` = -1: at every position)? */
static bool anf_key_eq(const AnfBr *a, const AnfBr *b, int p)
{
    if (a->w != b->w) return false;
    for (int i = 0; i < a->w; i++)
        if (i != p && !anf_cls_eq(a->pos[i], b->pos[i])) return false;
    return true;
}

/* THE ADJACENCY TEST (§3.2, first match): may mergeable branch `j` move up
 * past live branch `m`? Row 1: `m`'s head is disjoint from `j` at some
 * position both have, so `m` cannot match where `j` does. Row 2: `m`
 * consumes exactly `j`'s width and writes nothing (a mergeable branch is a
 * set sequence: one width, no capture, no `\K`), so only a same-span match is
 * possible and nothing observable differs. Row 3: anything else REFUSES,
 * among them every non-mergeable `m` until stage 2b reads its head and its
 * WRITES from the description (§3.5). */
static bool anf_passes(const AnfBr *m, const AnfBr *j)
{
    if (!m->merge) return false;                            /* row 3 */
    int h = m->w < j->w ? m->w : j->w;
    for (int p = 0; p < h; p++)
        if (anf_cls_disjoint(m->pos[p], j->pos[p])) return true;   /* row 1 */
    return m->w == j->w;                                    /* row 2 / 3 */
}

/* Does `j = b[to]` reach slot `from`: does it pass the adjacency test against
 * every live branch strictly between? `other` is the prefix count of branches
 * that are not mergeable of `j`'s width (row 2's whole-span fast path). */
static bool anf_reach(const AnfBr *b, const int *other, int from, int to)
{
    if (other[to] - other[from + 1] == 0) return true;
    for (int m = from + 1; m < to; m++)
        if (!b[m].dead && !anf_passes(&b[m], &b[to])) return false;
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

/* Drops every mergeable branch identical to an earlier live mergeable one. */
static void anf_drop_dups(Ctx *cx, AnfBr *b, int n)
{
    AnfHeads t;
    anf_heads_init(cx, &t, n);
    for (int j = 0; j < n; j++) {
        if (b[j].dead || !b[j].merge) continue;
        unsigned k = anf_key(&b[j], -1);
        int *slot = &t.bucket[k & t.mask];
        bool dup = false;
        for (int h = *slot; h >= 0 && !dup; h = t.prev[h])
            dup = t.key[h] == k && anf_key_eq(&b[h], &b[j], -1);
        if (dup) { b[j].dead = true; continue; }
        t.key[j] = k;
        t.prev[j] = *slot;
        *slot = j;
    }
}

/* One (width `w`, position `p`) pass of step M: each mergeable width-`w`
 * branch, in list order, folds into the EARLIEST head of its all-but-`p` group
 * it can reach (heads tried from the last backwards, stopping at the first
 * refusal: reach is monotone), or becomes a head. Returns the folds made. */
static int anf_merge_pass(Ctx *cx, AnfBr *b, int n, int w, int p, int *other)
{
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
            if (!anf_reach(b, other, h, j)) break;
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
static int anf_merge(Ctx *cx, AnfBr *b, int n)
{
    int maxw = 0, folds = 0;
    for (int i = 0; i < n; i++)
        if (b[i].merge && b[i].w > maxw) maxw = b[i].w;
    int *other = pcrec_arena_alloc(&cx->arena, (size_t)(n + 1) * sizeof *other);
    bool *has = pcrec_arena_alloc(&cx->arena, (size_t)(maxw + 1) * sizeof *has);
    for (int i = 0; i < n; i++)
        if (b[i].merge) has[b[i].w] = true;

    anf_drop_dups(cx, b, n);
    for (;;) {
        int swept = 0;
        for (int w = 1; w <= maxw; w++) {
            if (!has[w]) continue;
            for (int p = w - 1; p >= 0; p--)
                swept += anf_merge_pass(cx, b, n, w, p, other);
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

int pcrec_altnf(Ctx *cx, Ast **br, int n, PcrecAnfRules rules, int *folds)
{
    int nf = 0;
    if (rules.merge && n > 1) {
        AnfBr *b = pcrec_arena_alloc(&cx->arena, (size_t)n * sizeof *b);
        for (int i = 0; i < n; i++) anf_describe(cx, &b[i], br[i]);
        nf = anf_merge(cx, b, n);
        int out = 0;
        for (int i = 0; i < n; i++)
            if (!b[i].dead)
                br[out++] = b[i].dirty ? anf_rebuild(cx, &b[i]) : b[i].node;
        n = out;
    }
    if (folds) *folds = nf;
    return n;
}
