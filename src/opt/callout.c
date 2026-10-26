/* callout.c — [INLINE-C] stage 1b: THE CALLOUT SITES PASS (module
 * `callouts`; docs/design/inline_c.md §1.9, §1.10, §2.2).
 *
 * ONE GENERIC VISIT AND ONE WALK OVER THE TREE AS WRITTEN, run by
 * src/core/compile.c after the composer and the derivation hooks and before
 * `pcrec_altcls` and every optimization pass: the firing class is a fact about the pattern as the
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
    Ast          **sites;    /* [ncallouts]: every site, in visit order */
    int            nsites;
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

/* A group that never runs (`A_REP{..,0}`, the shape `(?(DEFINE)` and every
 * composed `lib` definition take): it holds no choice point the engine can
 * resume, and it can follow a site without making it non-tail. */
static bool co_inert(const Ast *a)
{
    return a->k == A_REP && a->u.rep.rmax == 0;
}

/* The first CHOICE POINT inside `a` the engine can resume after `a`
 * completes (§1.10), or NULL: an alternation, a quantifier whose minimum and
 * maximum differ, or a call (conservatively: its body may hold choices). A
 * choice inside an atomic group, a possessive quantifier
 * (`A_ATOMIC(A_REP)`) or an ATOMIC lookaround is SEALED by the time `a`
 * completes; a NON-ATOMIC lookaround (`(?*...)`, `(*napla:...)`) keeps its
 * choices live after it completes (a later failure re-enters it), so it
 * answers with its body's. A group that never runs holds none, and neither
 * do a backreference, an anchor and a callout site (its callee is atomic,
 * D38 §2). The node returned is the one the `once` refusal names: for a
 * non-atomic lookaround, the lookaround itself. */
static const Ast *co_choice(Ctx *cx, Ast *a)
{
    if (co_inert(a)) return NULL;
    switch (a->k) {
    case A_ALT:
        return a;
    case A_REP:
        if (a->u.rep.rmin != a->u.rep.rmax) return a;
        return co_choice(cx, a->l);
    case A_CALL:
        return a;
    case A_CAT: {
        int n;
        Ast **v = co_items(cx, a, A_CAT, &n);
        for (int i = 0; i < n; i++) {
            const Ast *c = co_choice(cx, v[i]);
            if (c) return c;
        }
        return NULL;
    }
    case A_CAP:
    case A_WCLASS:
        return co_choice(cx, a->l);
    case A_LOOK:
        /* The lookaround itself is the live construct (the refusal names
         * it, then the choice inside): re-entering it resumes that choice. */
        return !a->u.look.atomic && co_choice(cx, a->l) ? a : NULL;
    case A_ATOMIC:
    case A_CLASS: case A_EMPTY: case A_EOL: case A_CTX: case A_GSTART:
    case A_KRESET: case A_BREF: case A_VAR: case A_CALLOUT:
        return NULL;
    }
    return a;   /* unreachable: -Wswitch makes a new kind a build error */
}

/* " at offset N" for a construct node that carries its pattern offset, or
 * "" for one a rewrite built (it has none, and gets no invented offset):
 * arena text for the `once` refusal. */
static const char *co_at(Ctx *cx, const Ast *c)
{
    size_t at = 0;
    bool known = false;
    switch (c->k) {
    case A_REP:  at = c->u.rep.at; known = c->u.rep.at_known; break;
    case A_ALT:  at = c->u.alt.at; known = c->u.alt.at_known; break;
    case A_CALL: at = c->reg_at;   known = c->reg != NULL;    break;
    case A_LOOK: at = c->u.look.at; known = true; break;
    case A_CAT: case A_CAP: case A_ATOMIC: case A_WCLASS:
    case A_CLASS: case A_EMPTY: case A_EOL: case A_CTX: case A_GSTART:
    case A_KRESET: case A_BREF: case A_VAR: case A_CALLOUT:
        break;   /* never a culprit: co_choice and co_walk name none */
    }
    return known ? pcrec_sb_fragf(&cx->arena, " at offset %zu", at) : "";
}

/* The `once` refusal's naming of the live choice point `c` before a site,
 * and the fix for that construct: arena text. */
static const char *co_culprit(Ctx *cx, const Ast *c)
{
    if (c->k == A_LOOK) {
        /* The choice that makes it live is the first one inside its body. */
        const Ast *in = co_choice(cx, c->l);
        while (in && in->k == A_LOOK) in = co_choice(cx, in->l);
        const bool bh = c->u.look.behind;
        return pcrec_sb_fragf(&cx->arena,
            "the non-atomic lookaround%s keeps %s%s live after it completes; "
            "use %s (atomic), or wrap it: (?>%s...))",
            co_at(cx, c),
            in && in->k == A_REP ? "the quantifier"
            : in && in->k == A_ALT ? "the alternation"
            :                        "the subroutine call",
            in ? co_at(cx, in) : "",
            bh ? "(?<=...) / (?<!...)" : "(?=...) / (?!...)",
            bh ? "(?<*" : "(?*");
    }
    const char *what = c->k == A_REP ? "the quantifier"
                     : c->k == A_ALT ? "the alternation"
                     :                 "the subroutine call";
    const char *fix = c->k == A_REP
        ? "make it possessive (X*+, X++, X?+, X{n,m}+) or wrap it in (?>...)"
        : "wrap it in (?>...)";
    return pcrec_sb_fragf(&cx->arena, "%s%s can be backtracked into; %s",
                          what, co_at(cx, c), fix);
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
 * `rep`: the innermost enclosing quantified group whose maximum is 2 or more
 * (NULL: none); `live`: the first choice point before it that can be resumed
 * (NULL: none); `tail`: nothing follows it on any path to accept;
 * `behind`/`called`: §1.9 rows 1 and 3. */
static void co_site(CoWalk *w, Ast *a, const Ast *rep, const Ast *live,
                    bool tail, bool behind, bool called)
{
    Ctx *cx = w->cx;
    size_t at = a->u.callout.at;
    a->u.callout.site = w->next++;
    cx->callout_nodes[a->u.callout.site] = a;
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
        a->u.callout.why = pcrec_sb_fragf(&cx->arena, "inside the repeat "
            "whose quantifier%s has a maximum of 2 or more", co_at(cx, rep));
    } else if (live) {
        c = CO_CLASS_REPEATED;
        a->u.callout.why = co_culprit(cx, live);   /* same text as the refusal */
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
            ? "callout at offset %zu is marked once but can fire again: %s; "
              "a site in such a repeat cannot be marked once"
            : "callout at offset %zu is marked once but can fire again: %s",
            at, a->u.callout.why);
}

static void co_walk(CoWalk *w, Ast *a, const Ast *rep, const Ast *live,
                    bool tail, bool behind, bool called)
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
        const Ast *before = live;
        for (int i = 0; i < n; i++) {
            co_walk(w, v[i], rep, before, tail && i >= last, behind, called);
            if (!before) before = co_choice(w->cx, v[i]);
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
        co_walk(w, a->l, many ? a : rep, live, tail && !many, behind,
                called);
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

/* The pass's one generic visit (`pcrec_ast_visit`): marks every call
 * target (group number; 0 is the whole pattern) and collects every site.
 * The visitor's node is const by its signature; a site is the arena's, and
 * the declarations below write its attributes. */
static void co_scan(void *ud, const Ast *a)
{
    CoWalk *w = ud;
    if (a->k == A_CALL) {
        const int t = a->u.call.target;
        if (t == 0) w->call_root = true;
        else if (t > 0 && (unsigned)t <= w->cx->ncap) w->called[t] = 1;
    } else if (a->k == A_CALLOUT && w->nsites < w->cx->ncallouts) {
        w->sites[w->nsites++] = (Ast *)a;
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
    CoWalk w = { cx, NULL, false, 1, NULL, 0 };
    w.called = pcrec_arena_alloc(&cx->arena, cx->ncap + 1);
    memset(w.called, 0, cx->ncap + 1);
    w.sites = pcrec_arena_alloc(&cx->arena,
                                (size_t)cx->ncallouts * sizeof *w.sites);
    pcrec_ast_visit(root, co_scan, &w);
    if (w.nsites != cx->ncallouts)
        pcrec_ctx_fail(cx, 0, "internal error: the parse built %d callout "
                       "sites and the visit reached %d", cx->ncallouts,
                       w.nsites);

    for (int i = 0; i < nd; i++) {
        const PcrecCalloutDecl *d = &in->callout_decls[i];
        for (int j = 0; j < i; j++)
            if (in->callout_decls[j].num == d->num)
                pcrec_ctx_fail(cx, 0, "callout %d is declared twice", d->num);
        bool used = false;
        for (int k = 0; k < w.nsites; k++) {
            Ast *a = w.sites[k];
            if (a->u.callout.bind != CO_NUM || a->u.callout.num != d->num)
                continue;
            used = true;
            const char *msg = pcrec_callout_attrs(cx, a, d->attrs,
                                                  strlen(d->attrs), ',');
            if (msg)
                pcrec_ctx_fail(cx, a->u.callout.at, "callout %d's "
                               "declaration: %s", d->num, msg);
        }
        if (!used)
            pcrec_ctx_fail(cx, 0, "a callout declaration names callout %d, "
                           "which the pattern does not use", d->num);
    }

    cx->callout_nodes = pcrec_arena_alloc(&cx->arena,
        (size_t)(cx->ncallouts + 1) * sizeof *cx->callout_nodes);
    memset(cx->callout_nodes, 0,
           (size_t)(cx->ncallouts + 1) * sizeof *cx->callout_nodes);
    co_walk(&w, root, NULL, NULL, true, false, false);
    if (w.next != cx->ncallouts + 1)
        pcrec_ctx_fail(cx, 0, "internal error: the parse built %d callout "
                       "sites and the numbering walk reached %d",
                       cx->ncallouts, w.next - 1);
    /* §1.4 D19: an unbound binding is a link error by design, and the
     * standalone driver `--emit-main` writes could not link one. Every
     * site is a binding at stage 1b (embedded code is stage 2's). */
    if (pcrec_opt_has(cx->opt, PCREC_EMIT_MAIN)) {
        const Ast *a = cx->callout_nodes[1];
        const PcrecCalloutBinding b = pcrec_callout_binding(&cx->arena, a);
        if (b.is_extern)
            pcrec_ctx_fail(cx, a->u.callout.at, "--emit-main cannot define "
                           "the binding %s; link your own", b.symbol);
    }
}
