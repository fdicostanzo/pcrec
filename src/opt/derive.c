/* [COMPOUND] DERIVATIONS: tree rewrites that make a compound's PART from its
 * parent pattern (docs/design/compound.md §B.1; build step B2). A derivation
 * runs at the composer hook's position (`compile_driver`'s tree-hook list:
 * after `pcrec_parse`, before `pcrec_altcls`), so the derived tree gets
 * every optimization any tree gets, and group numbers are the parse's.
 *
 * `pcrec_derive_split_q`: [MATCH-SPLIT]'s Q = P with its floor anchors
 * killed, then pruned. Q is searched only PAST the floor (from
 * `next_pos(f)`), where every killed node is false in P too, so P and Q
 * anchored at any later start are the same matcher.
 *
 *  1. KILL. Every `\G` becomes the never node (an empty `A_CLASS`):
 *     REQUIRED, since a `\G` left in Q would assert at the position the
 *     controller searches Q from. Every `^`/`\A` with no `(?m)`
 *     (`A_BOL`, `!u.anch.multiline`) becomes never: a route optimization,
 *     false past the floor anyway. NOT killed: a node inside a lookbehind or
 *     inside a group called (transitively) from one, which can be read at a
 *     position below the attempt start; `(?m)^`. A `\G` there DECLINES.
 *  2. PRUNE, bottom-up: a `CAT` with a never item is never; an `ALT` drops
 *     never arms; `REP{m>=1}` of never is never and `REP{0,...}` of never is
 *     EMPTY; a positive `LOOK` of never is never, a negative one EMPTY; a
 *     group, an atomic group or a lookahead of never is never.
 *     THE GROUP-KEEP RULE: a capture group anything can still reach (a call
 *     target, a backreference target -- `refs[]` read as a SET, so every
 *     group a duplicate name names) is never DELETED: the construct holding
 *     it stays in the tree as a never arm, which cannot match past the floor,
 *     which is what P does there. Calls are left as they are; a pruned group
 *     keeps its number on its node and nothing renumbers.
 *  3. CHECK (compound.md §E.3 G5), an independent walk of the derived tree,
 *     not the derivation's own counters: no `\G` survives, every surviving
 *     `^`/`\A` is in a lookbehind region, no kept group was deleted; and the
 *     number of floor anchors KILLED is read as P's count minus Q's.
 *
 * The REPORT (`PcrecDeriveReport`) goes to the caller through
 * `PcrecEmitIn.derive_report`: killed counts, `\G` present, Q never (the
 * floor-only form), kept never arms (A2's first-build decline reads it), the
 * decline reason. A DECLINE is a refusal of the part (`pcrec_ctx_fail`),
 * which declines its row.
 *
 * Spine discipline (coding_guide §2.4, src/opt/atomic.c:22-36): `A_CAT` and
 * `A_ALT` spines are left-nested and as long as the pattern, so every walk
 * here descends a spine iteratively and recurses only into the items; no
 * walk follows `u.call.body` (unbound at this position anyway). */
#include "core/internal.h"

#include <string.h>

/* What pass 1 learns about P: which groups must survive, which lie in a
 * lookbehind region, and the capture node of each group number. */
typedef struct {
    Ctx *cx;
    int ncap;
    const Ast **cap;          /* [1..ncap]: the group's A_CAP node */
    bool *kept;               /* [0..ncap]: a call or backreference names it */
    bool *lb_called;          /* [0..ncap]: called from a lookbehind region */
    bool more;                /* the closure grew this round */
} QFacts;

/* Pass 1's walk: records each group's node, every kept group, and every
 * group called from inside a lookbehind region (`lb`). */
static void qf_walk(QFacts *f, const Ast *a, bool lb)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_CTX: case A_GSTART: case A_KRESET: case A_VAR: case A_WCLASS:
            return;
        case A_BREF:
            for (int i = 0; i < a->u.bref.nrefs; i++)
                if (a->u.bref.refs[i] >= 0 && a->u.bref.refs[i] <= f->ncap)
                    f->kept[a->u.bref.refs[i]] = true;
            return;
        case A_CALL: {
            /* `(?R)` reaches the root, which is never deleted: the root is
             * Q itself. The callee's BODY is visited at its own lexical
             * position, never through `.body`. */
            int t = a->u.call.target;
            if (t >= 0 && t <= f->ncap) {
                f->kept[t] = true;
                if (lb && !f->lb_called[t]) { f->lb_called[t] = true; f->more = true; }
            }
            return;
        }
        case A_CAP:
            if (a->u.cap.no >= 0 && a->u.cap.no <= f->ncap) {
                f->cap[a->u.cap.no] = a;
                if (f->lb_called[a->u.cap.no]) lb = true;
            }
            a = a->l;
            continue;
        case A_LOOK:
            if (a->u.look.behind) lb = true;
            a = a->l;
            continue;
        case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            for (; a->k == k; a = a->l) qf_walk(f, a->r, lb);
            continue;
        }
        }
        return;
    }
}

/* Pass 1: the facts, with the lookbehind-called set closed (a group called
 * from inside a group called from a lookbehind is in the region too). */
static void qf_build(Ctx *cx, const Ast *root, QFacts *f)
{
    memset(f, 0, sizeof *f);
    f->cx = cx;
    f->ncap = cx->ncap;
    f->cap = pcrec_arena_alloc(&cx->arena, (size_t)(f->ncap + 1) * sizeof *f->cap);
    f->kept = pcrec_arena_alloc(&cx->arena, (size_t)(f->ncap + 1));
    f->lb_called = pcrec_arena_alloc(&cx->arena, (size_t)(f->ncap + 1));
    do {
        f->more = false;
        qf_walk(f, root, false);
    } while (f->more);
}

/* The derivation's working state over the rewrite. */
typedef struct {
    Ctx *cx;
    const QFacts *f;
    int killed_g, killed_bol, pruned_arms, kept_never;
    const char *decline;
} QDer;

/* A rewritten subtree: the node, whether it can never match, and whether it
 * holds a group the group-keep rule protects. */
typedef struct { Ast *a; bool never; bool keeps; } QRes;

static Ast *never_node(Ctx *cx) { return pcrec_ast_node(cx, A_CLASS); }

static bool is_never_leaf(const Ast *a) { return a->k == A_CLASS && a->u.cls.n == 0; }

/* A copy of `a` with child `l` (single-child kinds; `a` is never written). */
static Ast *with_child(Ctx *cx, const Ast *a, Ast *l)
{
    if (a->l == l) return (Ast *)a;
    Ast *n = pcrec_arena_alloc(&cx->arena, sizeof *n);
    *n = *a;
    n->l = l;
    return n;
}

static QRes q_rewrite(QDer *q, Ast *a, bool lb);

/* An `A_CAT` spine: never if any item is never -- unless a kept group sits
 * in it, when the spine stays as a never arm (the group-keep rule). */
static QRes q_cat(QDer *q, Ast *a, bool lb)
{
    size_t n = 1;
    for (Ast *t = a; t->k == A_CAT; t = t->l) n++;
    QRes *it = pcrec_arena_alloc(&q->cx->arena, n * sizeof *it);
    size_t i = n;
    Ast *t = a;
    for (; t->k == A_CAT; t = t->l) it[--i] = q_rewrite(q, t->r, lb);
    it[--i] = q_rewrite(q, t, lb);
    bool never = false, keeps = false;
    for (i = 0; i < n; i++) { never |= it[i].never; keeps |= it[i].keeps; }
    if (never && !keeps) return (QRes){ never_node(q->cx), true, false };
    Ast *r = it[0].a;
    for (i = 1; i < n; i++) {
        Ast *c = pcrec_arena_alloc(&q->cx->arena, sizeof *c);
        c->k = A_CAT; c->l = r; c->r = it[i].a;
        r = c;
    }
    return (QRes){ r, never, keeps };
}

/* An `A_ALT` spine: never arms are dropped, except one holding a kept group,
 * which stays (and is counted: A2's first-build decline reads it). */
static QRes q_alt(QDer *q, Ast *a, bool lb)
{
    size_t n = 1;
    for (Ast *t = a; t->k == A_ALT; t = t->l) n++;
    QRes *it = pcrec_arena_alloc(&q->cx->arena, n * sizeof *it);
    size_t i = n;
    Ast *t = a;
    for (; t->k == A_ALT; t = t->l) it[--i] = q_rewrite(q, t->r, lb);
    it[--i] = q_rewrite(q, t, lb);
    Ast *r = NULL;
    bool never = true, keeps = false;
    for (i = 0; i < n; i++) {
        if (it[i].never && !it[i].keeps) { q->pruned_arms++; continue; }
        if (it[i].never) q->kept_never++;
        never &= it[i].never;
        keeps |= it[i].keeps;
        if (!r) { r = it[i].a; continue; }
        Ast *c = pcrec_arena_alloc(&q->cx->arena, sizeof *c);
        c->k = A_ALT; c->l = r; c->r = it[i].a;
        r = c;
    }
    if (!r) return (QRes){ never_node(q->cx), true, false };
    return (QRes){ r, never, keeps };
}

/* Kill, then prune, one subtree; `lb` is "inside a lookbehind region". */
static QRes q_rewrite(QDer *q, Ast *a, bool lb)
{
    Ctx *cx = q->cx;
    switch (a->k) {
    case A_GSTART:
        if (lb) {
            q->decline = "a \\G inside a lookbehind region cannot be killed";
            return (QRes){ a, false, false };
        }
        q->killed_g++;
        return (QRes){ never_node(cx), true, false };
    case A_BOL:
        if (lb || a->u.anch.multiline) return (QRes){ a, false, false };
        q->killed_bol++;
        return (QRes){ never_node(cx), true, false };
    case A_CLASS:
        return (QRes){ a, is_never_leaf(a), false };
    case A_EMPTY: case A_EOL: case A_END: case A_CTX: case A_KRESET:
    case A_BREF: case A_VAR: case A_WCLASS:
    /* Calls are left as they are (§B.1): a callee is rewritten at its own
     * lexical position, and the call reaches the rewritten group. */
    case A_CALL:
        return (QRes){ a, false, false };
    case A_CAT:
        return q_cat(q, a, lb);
    case A_ALT:
        return q_alt(q, a, lb);
    case A_CAP: {
        const int no = a->u.cap.no;
        const bool inlb = lb || (no >= 0 && no <= q->f->ncap && q->f->lb_called[no]);
        QRes b = q_rewrite(q, a->l, inlb);
        bool keeps = b.keeps || (no >= 0 && no <= q->f->ncap && q->f->kept[no]);
        return (QRes){ with_child(cx, a, b.a), b.never, keeps };
    }
    case A_ATOMIC: {
        QRes b = q_rewrite(q, a->l, lb);
        return (QRes){ with_child(cx, a, b.a), b.never, b.keeps };
    }
    case A_REP: {
        QRes b = q_rewrite(q, a->l, lb);
        if (!b.never) return (QRes){ with_child(cx, a, b.a), false, b.keeps };
        if (a->u.rep.rmin >= 1)
            return b.keeps ? (QRes){ with_child(cx, a, b.a), true, true }
                           : (QRes){ never_node(cx), true, false };
        /* REP{0,...} of never matches only empty */
        return b.keeps ? (QRes){ with_child(cx, a, b.a), false, true }
                       : (QRes){ pcrec_ast_node(cx, A_EMPTY), false, false };
    }
    case A_LOOK: {
        QRes b = q_rewrite(q, a->l, lb || a->u.look.behind);
        if (!b.never) return (QRes){ with_child(cx, a, b.a), false, b.keeps };
        if (!a->u.look.neg)
            return b.keeps ? (QRes){ with_child(cx, a, b.a), true, true }
                           : (QRes){ never_node(cx), true, false };
        /* a negative lookaround of never always holds */
        return b.keeps ? (QRes){ with_child(cx, a, b.a), false, true }
                       : (QRes){ pcrec_ast_node(cx, A_EMPTY), false, false };
    }
    }
    /* No `default:` (mrl.c:18-24): a new kind must decide here. */
    pcrec_ctx_fail(cx, 0, "internal error: derive: unhandled node kind %d", (int)a->k);
    return (QRes){ a, false, false };
}

/* G5's counts over one tree, an independent walk: `\G` nodes, `^`/`\A`
 * (no `(?m)`) outside a lookbehind region, and which groups are present. */
typedef struct {
    const QFacts *f;
    int g, bol_out;
    bool *present;            /* [0..ncap] */
} QProps;

static void qp_walk(QProps *p, const Ast *a, bool lb)
{
    for (;;) {
        switch (a->k) {
        case A_GSTART: p->g++; return;
        case A_BOL: if (!lb && !a->u.anch.multiline) p->bol_out++; return;
        case A_CLASS: case A_EMPTY: case A_EOL: case A_END: case A_CTX:
        case A_KRESET: case A_BREF: case A_VAR: case A_WCLASS: case A_CALL:
            return;
        case A_CAP:
            if (a->u.cap.no >= 0 && a->u.cap.no <= p->f->ncap) {
                p->present[a->u.cap.no] = true;
                if (p->f->lb_called[a->u.cap.no]) lb = true;
            }
            a = a->l;
            continue;
        case A_LOOK:
            if (a->u.look.behind) lb = true;
            a = a->l;
            continue;
        case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            for (; a->k == k; a = a->l) qp_walk(p, a->r, lb);
            continue;
        }
        }
        return;
    }
}

static void qp_count(Ctx *cx, const QFacts *f, const Ast *root, QProps *p)
{
    memset(p, 0, sizeof *p);
    p->f = f;
    p->present = pcrec_arena_alloc(&cx->arena, (size_t)(f->ncap + 1));
    qp_walk(p, root, false);
}

Ast *pcrec_derive_split_q(Ctx *cx, Ast *root)
{
    QFacts f;
    qf_build(cx, root, &f);
    QProps before;
    qp_count(cx, &f, root, &before);
    QDer q = { .cx = cx, .f = &f };
    QRes r = q_rewrite(&q, root, false);
    /* G5, by the independent walk of the derived tree. */
    QProps after;
    qp_count(cx, &f, r.a, &after);
    if (!q.decline) {
        if (after.g || after.bol_out)
            pcrec_ctx_fail(cx, 0, "internal error: derive: a floor anchor survived "
                           "outside a lookbehind region (compound.md §E.3 G5)");
        for (int no = 1; no <= f.ncap; no++)
            if (f.kept[no] && before.present[no] && !after.present[no])
                pcrec_ctx_fail(cx, 0, "internal error: derive: kept group %d was "
                               "deleted (compound.md §E.3 G5)", no);
    }
    const int killed = (before.g + before.bol_out) - (after.g + after.bol_out);
    if (!q.decline && killed == 0) q.decline = "nothing killed";
    PcrecDeriveReport *rep = cx->emit_in ? cx->emit_in->derive_report : NULL;
    if (rep) {
        *rep = (PcrecDeriveReport){
            .decline = q.decline, .killed = killed, .killed_g = before.g - after.g,
            .pruned_arms = q.pruned_arms, .kept_never = q.kept_never,
            .never = !q.decline && r.never, .has_g = before.g > 0,
        };
    }
    if (q.decline)
        pcrec_ctx_fail(cx, 0, "compound part: the derivation declines: %s", q.decline);
    return r.a;
}

const PcrecDerive pcrec_derive_split_q_row = { "split-q", pcrec_derive_split_q };

/* The attempt-scope predicate: does any node of `root` carry a registry row
 * whose effect spans attempts or observes their order (RF_CROSSES_ATTEMPTS:
 * the callout rows; the attempt-crossing verbs are ROADMAP_NEVER and refused
 * at parse). A compound's controller runs P's attempts as separate calls, so
 * such a pattern declines (compound.md §B.8, A3). */
static void xa_visit(void *ud, const Ast *a)
{
    if (a->reg && (a->reg->flags & RF_CROSSES_ATTEMPTS)) *(bool *)ud = true;
}

bool pcrec_ast_crosses_attempts(const Ast *root)
{
    bool hit = false;
    pcrec_ast_visit(root, xa_visit, &hit);
    return hit;
}
