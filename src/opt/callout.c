/* callout.c — [INLINE-C] stage 1b: THE CALLOUT SITES PASS (module
 * `callouts`; docs/design/inline_c.md §1.9, §1.10, §2.2).
 *
 * ONE WALK OVER THE TREE AS WRITTEN, run by src/core/compile.c after the
 * composer and the derivation hooks and before `pcrec_altcls` and every
 * optimization pass: the firing class is a fact about the pattern as the
 * user wrote it, and §1.8 forbids a pass that would add fires, so nothing
 * downstream may be what the class is read from. A pattern with no site
 * (`cx->ncallouts == 0`) returns at the first line, which is what keeps every
 * callout-free compile byte-identical.
 *
 * IT DOES FOUR THINGS, in this order, each a declared rule of the design:
 *
 *   1. DECLARATIONS (§2.2): a numbered callout's attributes arrive from the
 *      `.rxt` `callout` line or `--callout`, and are applied to every site
 *      with that number before anything reads a site's width class. A
 *      declaration naming a number no site uses is REFUSED (a stale
 *      declaration is a bug, not a default), as is a number declared twice.
 *   2. NUMBERING: sites are numbered 1..n in textual order (the listing's
 *      and the stamps' `site` column).
 *   3. POSITIONS (§1.9, first match): inside a lookbehind, refused; inside a
 *      group a subroutine call or recursion can reach (a local `(?1)`,
 *      `(?R)`, `(?&n)`, a `(?(DEFINE)` group that is called, and every `lib`
 *      definition, which the composer binds as exactly such a group), refused:
 *      a call re-enters the site at a depth the view does not describe.
 *      Row 2 (a conditional's condition) cannot arise: module `conditionals`
 *      has no producer, so `(?(` is refused before a site inside it exists.
 *   4. THE FIRING CLASS (§1.10) and the `once` check: see `co_site`.
 *
 * Spines are walked iteratively (D10/DD-10): a concatenation is as long as
 * the pattern, so a CAT or ALT spine is flattened into an array first, and
 * recursion is bounded by group nesting, which the parser bounds. */

#include <string.h>

#include "core/internal.h"

typedef struct {
    Ctx           *cx;
    unsigned char *called;   /* [ncap + 1]: group g is a call target */
    bool           call_root;/* `(?R)`/`(?0)`: every site is reachable */
    int            next;     /* the next site number */
} CoWalk;

/* Flattens the `k`-spine rooted at `a` (left-deep: `k(k(x, y), z)`) into
 * its items in textual order, arena-allocated; *n is their count. */
static Ast **co_items(Ctx *cx, Ast *a, AKind k, int *n)
{
    int c = 1;
    for (const Ast *t = a; t->k == k; t = t->l) c++;
    Ast **v = pcrec_arena_alloc(&cx->arena, (size_t)c * sizeof *v);
    int i = c;
    Ast *t = a;
    for (; t->k == k; t = t->l) v[--i] = t->r;
    v[--i] = t;
    *n = c;
    return v;
}

/* Does `a` hold a CHOICE POINT the engine can resume after `a` completes
 * (§1.10): an alternation, a quantifier whose minimum and maximum differ, or
 * a call (conservatively: its body may hold choices). A choice inside an
 * atomic group, a possessive quantifier (`A_ATOMIC(A_REP)`) or a lookaround
 * is SEALED by the time `a` completes, so those answer false; so do a
 * backreference, an anchor and a callout site (its callee is atomic, D38
 * §2). */
static bool co_choice(Ctx *cx, Ast *a)
{
    switch (a->k) {
    case A_ALT:
        return true;
    case A_REP:
        if (a->u.rep.rmin != a->u.rep.rmax) return true;
        return co_choice(cx, a->l);
    case A_CALL:
        return true;
    case A_CAT: {
        int n;
        Ast **v = co_items(cx, a, A_CAT, &n);
        for (int i = 0; i < n; i++)
            if (co_choice(cx, v[i])) return true;
        return false;
    }
    case A_CAP:
    case A_WCLASS:
        return co_choice(cx, a->l);
    case A_ATOMIC:
    case A_LOOK:
    case A_CLASS: case A_EMPTY: case A_EOL: case A_CTX: case A_GSTART:
    case A_KRESET: case A_BREF: case A_VAR: case A_CALLOUT:
        return false;
    }
    return true;   /* unreachable: -Wswitch makes a new kind a build error */
}

/* An item that can follow a site without making it non-tail: a group that
 * never runs (`A_REP{..,0}`, the shape `(?(DEFINE)` and every composed `lib`
 * definition take). */
static bool co_inert(const Ast *a)
{
    return a->k == A_REP && a->u.rep.rmax == 0;
}

const char *pcrec_callout_class_name(int fclass)
{
    switch ((CalloutClass)fclass) {
    case CO_CLASS_ONCE_PER_MATCH: return "once-per-match";
    case CO_CLASS_ONCE_PER_START: return "once-per-start";
    case CO_CLASS_REPEATED:       return "repeated";
    }
    return "?";
}

/* One site: its number, its position check, its class, its `once` check.
 * `rep`: inside a quantified group whose maximum is 2 or more; `live`: a
 * choice point before it can be resumed; `tail`: nothing follows it on any
 * path to accept; `behind`/`called`: §1.9 rows 1 and 3. */
static void co_site(CoWalk *w, Ast *a, bool rep, bool live, bool tail,
                    bool behind, bool called)
{
    Ctx *cx = w->cx;
    size_t at = a->u.callout.at;
    a->u.callout.site = w->next++;
    if (behind)
        pcrec_ctx_fail(cx, at, "a callout inside a lookbehind is not "
                       "supported");
    if (called || w->call_root)
        pcrec_ctx_fail(cx, at, "a callout inside a group reached by a "
                       "subroutine call or recursion (including a lib "
                       "definition) is not supported: a call re-enters the "
                       "site at a depth its view does not describe");
    CalloutClass c;
    if (rep) {
        c = CO_CLASS_REPEATED;
        a->u.callout.why = "inside a repeat whose maximum is 2 or more";
    } else if (live) {
        c = CO_CLASS_REPEATED;
        a->u.callout.why = "a choice point before the site can be resumed "
                           "and reach it again";
    } else if (tail) {
        c = CO_CLASS_ONCE_PER_MATCH;
        a->u.callout.why = "no repeat and no live choice point before it; "
                           "tail";
    } else {
        c = CO_CLASS_ONCE_PER_START;
        a->u.callout.why = "no repeat and no live choice point before it";
    }
    a->u.callout.fclass = (int)c;
    a->u.callout.tail = tail;
    if (a->u.callout.once && c == CO_CLASS_REPEATED)
        pcrec_ctx_fail(cx, at, rep
            ? "callout at offset %zu is marked once but can fire again: it is "
              "inside a repeat whose maximum is 2 or more"
            : "callout at offset %zu is marked once but can fire again: a "
              "quantifier, alternation or call before it can be backtracked "
              "into; make the quantifier possessive (X*+) or wrap it in "
              "(?>...)", at);
}

static void co_walk(CoWalk *w, Ast *a, bool rep, bool live, bool tail,
                    bool behind, bool called)
{
    switch (a->k) {
    case A_CALLOUT:
        co_site(w, a, rep, live, tail, behind, called);
        return;
    case A_CAT: {
        int n;
        Ast **v = co_items(w->cx, a, A_CAT, &n);
        /* `last`: the index after which every item is inert. */
        int last = n - 1;
        while (last > 0 && co_inert(v[last])) last--;
        bool before = live;
        for (int i = 0; i < n; i++) {
            co_walk(w, v[i], rep, before, tail && i >= last, behind, called);
            if (!before && co_choice(w->cx, v[i])) before = true;
        }
        return;
    }
    case A_ALT: {
        /* An enclosing alternation resumes LATER branches, which do not hold
         * the site: no choice is added on the way down. */
        int n;
        Ast **v = co_items(w->cx, a, A_ALT, &n);
        for (int i = 0; i < n; i++)
            co_walk(w, v[i], rep, live, tail, behind, called);
        return;
    }
    case A_REP: {
        const int mx = a->u.rep.rmax;
        const bool many = mx < 0 || mx >= 2;
        co_walk(w, a->l, rep || many, live, tail && !many, behind, called);
        return;
    }
    case A_CAP: {
        const int no = a->u.cap.no;
        const bool c = called ||
            (no >= 0 && (unsigned)no <= w->cx->ncap && w->called[no]);
        co_walk(w, a->l, rep, live, tail, behind, c);
        return;
    }
    case A_ATOMIC:
    case A_WCLASS:
        co_walk(w, a->l, rep, live, tail, behind, called);
        return;
    case A_LOOK:
        co_walk(w, a->l, rep, live, false, behind || a->u.look.behind,
                called);
        return;
    /* The callee's body is visited at its own lexical position, never
     * through the call (the AST's one back edge). */
    case A_CALL:
    case A_CLASS: case A_EMPTY: case A_EOL: case A_CTX: case A_GSTART:
    case A_KRESET: case A_BREF: case A_VAR:
        return;
    }
}

/* Marks every call target (group number; 0 is the whole pattern). */
static void co_targets(CoWalk *w, const Ast *a)
{
    switch (a->k) {
    case A_CALL: {
        const int t = a->u.call.target;
        if (t == 0) w->call_root = true;
        else if (t > 0 && (unsigned)t <= w->cx->ncap) w->called[t] = 1;
        return;
    }
    case A_CAT: case A_ALT: {
        const AKind k = a->k;
        const Ast *t = a;
        for (; t->k == k; t = t->l) co_targets(w, t->r);
        co_targets(w, t);
        return;
    }
    case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK: case A_WCLASS:
        co_targets(w, a->l);
        return;
    case A_CLASS: case A_EMPTY: case A_EOL: case A_CTX: case A_GSTART:
    case A_KRESET: case A_BREF: case A_VAR: case A_CALLOUT:
        return;
    }
}

/* Applies the declarations of numbered callouts: one `PcrecCalloutDecl` per
 * number, each naming a number some `CO_NUM` site uses. */
static void co_apply_decl(Ctx *cx, Ast *a, const PcrecCalloutDecl *d,
                          bool *used)
{
    switch (a->k) {
    case A_CALLOUT:
        if (a->u.callout.bind == CO_NUM && a->u.callout.num == d->num) {
            *used = true;
            const char *msg = pcrec_callout_attrs(cx, a, d->attrs,
                                                  strlen(d->attrs), ',');
            if (msg)
                pcrec_ctx_fail(cx, a->u.callout.at, "callout %d's "
                               "declaration: %s", d->num, msg);
        }
        return;
    case A_CAT: case A_ALT: {
        const AKind k = a->k;
        Ast *t = a;
        for (; t->k == k; t = t->l) co_apply_decl(cx, t->r, d, used);
        co_apply_decl(cx, t, d, used);
        return;
    }
    case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK: case A_WCLASS:
        co_apply_decl(cx, a->l, d, used);
        return;
    case A_CALL: case A_CLASS: case A_EMPTY: case A_EOL: case A_CTX:
    case A_GSTART: case A_KRESET: case A_BREF: case A_VAR:
        return;
    }
}

void pcrec_callout_sites(Ctx *cx, Ast *root)
{
    const PcrecEmitIn *in = cx->emit_in;
    const int nd = in ? in->ncallout_decls : 0;
    if (cx->ncallouts == 0) {
        /* A declaration with no site at all is still stale. */
        if (nd > 0)
            pcrec_ctx_fail(cx, 0, "a callout declaration names callout %d, "
                           "which the pattern does not use",
                           in->callout_decls[0].num);
        return;
    }
    for (int i = 0; i < nd; i++) {
        const PcrecCalloutDecl *d = &in->callout_decls[i];
        for (int j = 0; j < i; j++)
            if (in->callout_decls[j].num == d->num)
                pcrec_ctx_fail(cx, 0, "callout %d is declared twice", d->num);
        bool used = false;
        co_apply_decl(cx, root, d, &used);
        if (!used)
            pcrec_ctx_fail(cx, 0, "a callout declaration names callout %d, "
                           "which the pattern does not use", d->num);
    }

    CoWalk w = { cx, NULL, false, 1 };
    w.called = pcrec_arena_alloc(&cx->arena, cx->ncap + 1);
    memset(w.called, 0, cx->ncap + 1);
    co_targets(&w, root);
    co_walk(&w, root, false, false, true, false, false);
}
