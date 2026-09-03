/* rxt_compose.c — [DD-13b.W1.3] THE COMPOSER: binding a `.rxt` source's
 * definitions into the target pattern's tree.
 *
 * ONE FILE, because every mechanism in it is meaningless without the others
 * and a reviewer must be able to read the whole thing without leaving it:
 * the sub-parse, the assignment MAP, the injection, the two re-basing
 * passes, and the re-resolution that turns a deferred by-name call into a
 * number. Design: docs/design/dd13_format/w1_impl.md §2 (the mechanism) and
 * §8 (what D89 changed and why §2 alone is not buildable as written).
 *
 * THE ONE-PARAGRAPH VERSION. `pcrec_parse` has already run and has left
 * every by-name subroutine call this pattern could not resolve sitting in
 * `cx->pending_refs` with `deferred` set (DECIDED (6); the flag is
 * `cx->defer_file_refs`, which is on only when a definition set exists). For
 * each such name that the set declares, the definition's own text is
 * SUB-PARSED on the SAME `Ctx` with the numbering scope swapped out, so it
 * is numbered from 1 in its own space and means exactly what it means in its
 * own file; the sub-parse's result is then re-based into the caller's space
 * through a MAP and concatenated onto the caller's root as
 * `A_REP{0,0}(A_CAP{base}(body))`, which is the shape `(?(DEFINE)…)` already
 * desugars to. Binding a definition can defer further names, so the whole
 * thing is a worklist to a fixpoint with a visited set — cycles are legal
 * (self- and mutual recursion compile and match on both oracles, r44-sem M8)
 * and terminate there.
 *
 * WHAT D89 ADDED, AND IT IS THE PART §2 HAS NO MECHANISM FOR. Frank's Q-W1
 * ruling makes a library's groups NON-CAPTURING TO THE CALLER by default,
 * in three tiers:
 *
 *   DELIVERED  the definition NAMES it -> a slot above `ngroups` AND a
 *              `groups[]` row whose `.ref` is the definition's name. This is
 *              the only tier a caller can see, and it is seen BY NAME.
 *   HIDDEN     unnamed, but the definition itself references it (a backref
 *              target, a call target) -> a slot, no row, no name lookup.
 *   ERASED     unnamed and referenced by nothing inside the definition ->
 *              the `A_CAP` is DELETED and it spends NO NUMBER AT ALL, which
 *              is D89(2)(a)'s "rewritten to `(?:…)` … truly non-capturing,
 *              zero slots, and the PCRE2 textual control is the same pattern
 *              byte for byte".
 *
 * A tier that spends no number is not expressible by §2.5's "add `base` to
 * every `A_CAP`" walk, because the survivors must then CLOSE UP. So the
 * offset becomes a MAP, `local number -> final number, or 0 for erased`,
 * which is the ASSIGNMENT TABLE §2.7 already names as the one derivation
 * with three readers (`RX_NCAPS`, the `rx_group_entry` array,
 * `--emit-composed`). The map is strictly more general than the offset it
 * replaces: with nothing erased it IS `+base`, which is why §2.5's MEASURED
 * cell (library `dd` = `(\d)\1`, caller `^(\d)-(?&dd)$`, `dd`'s own group 1
 * -> 3 and `\1` -> `\3`, matching `5-77` and rejecting `5-75`) is still the
 * expected answer.
 *
 * DELIVERY IS DECLARED BY NAMING (DECIDED, w13). D89 point 4 leaves delivery
 * to "the lib's own names" and builds no in-pattern syntax in W1, so: a
 * definition's group is delivered exactly when the definition NAMES it.
 * Naming a group in a library IS the author's declaration that it is part of
 * the library's interface. Every alternative — a head line listing delivered
 * names, a per-target list, an in-pattern marker — either builds W1.4's
 * syntax early or creates a SECOND place an interface is declared, and this
 * project refuses second places (memory
 * `pcrec-general-mechanisms-not-special-cases`). The cost is that a
 * definition cannot name a group PRIVATELY; that is question Q-W3 in
 * w1_impl §8.8, and today's workaround is `(?:…)` plus a comment.
 *
 * WHAT THIS FILE DOES NOT DO. `(?&^.name)` (the caller-scope prefix),
 * `(?&site=name)` (the delivering call) and `--emit-composed` are §1.5's
 * pattern-level extensions and are W1.4's, not W1.3's — none of them is
 * spellable today, so nothing here can reach them. `(?R)`/`(?0)` inside a
 * bound definition is REFUSED (Q-W2, D89 point 3): the ruling is missing,
 * not the meaning.
 */

#include <string.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

/* ---- the saved numbering scope (w1_impl §2.2) --------------------------
 *
 * A definition lives in a different `pattern` line — a different STRING —
 * and the tree makes a SUB-PARSE ON THE SAME `Ctx` the cheap answer: the
 * alternative is a second `Ctx` with its own arena plus a deep node-clone
 * pass, i.e. a second place that must know every `AKind` and every D70
 * payload and that goes stale silently when a kind is added.
 *
 * EVERY FIELD BELOW IS LOAD-BEARING, and `ncap` most of all: it is read
 * DURING the parse, because PCRE2's multi-digit rule makes `\12` a
 * backreference iff the RUNNING count is >= 12 and an octal literal
 * otherwise (`Ctx.ncap`'s own comment). Parsing a definition with the
 * caller's count already advanced would therefore change what the
 * definition MEANS, not merely how it is numbered — which is why
 * w1_impl §3's sabotage row for a forgotten swap tests MEANING and not only
 * renumbering.
 *
 * `pending_refs` is CAPTURED, not merely restored (§2.5's N4). The re-basing
 * pass is keyed on the definition's OWN pending records; if leaving the
 * sub-parse simply put the caller's list back, the very things the pass is
 * keyed on would be gone before it ran. */
typedef struct {
    const char          *pat;
    size_t               patlen;
    size_t               pos;
    unsigned             ncap;
    NamedGroup          *named_groups;
    unsigned             n_named_groups;
    PendingRef          *pending_refs;
    unsigned             n_pending_refs;
    ParseMods           *mods;
    const pcrec_options *opt;
    bool                 in_quote;
    int                  depth;
} RxtScope;

/* One bound definition, in binding (closure) order. */
typedef struct {
    const RxtDef *def;
    int           base;        /* the WRAPPER's group number (INTERNAL)   */
    Ast          *inject;      /* A_REP{0,0}(A_CAP{base}(body))           */
} Bound;

typedef struct {
    Ctx    *cx;
    Bound  *bound;
    size_t  nbound;
    /* Every definition's captured pending list, kept so the re-resolution
     * pass can reach a reference a definition itself deferred. Parallel to
     * `bound`. */
    PendingRef **pend;
} Composer;

/* ---- looking a name up ------------------------------------------------- */

static const RxtDef *def_by_name(const Ctx *cx, const char *name)
{
    for (size_t i = 0; i < cx->defs->n; i++)
        if (strcmp(cx->defs->v[i].name, name) == 0) return &cx->defs->v[i];
    return NULL;
}

static Bound *bound_by_name(Composer *co, const char *name)
{
    for (size_t i = 0; i < co->nbound; i++)
        if (strcmp(co->bound[i].def->name, name) == 0) return &co->bound[i];
    return NULL;
}

/* ---- the re-basing tree walk (w1_impl §2.5, pass 1 of 2) ---------------
 *
 * Remap every `A_CAP.u.cap.no` through `map`, and SPLICE OUT the wrapper of
 * every group `map` sends to 0 (the ERASED tier). This is deliberately the
 * same traversal `mod_backrefs.c`'s `br_strip_caps` uses for
 * `--no-captures`, down to the iterative `A_CAT`/`A_ALT` spine walks: a flat
 * concatenation is as long as the pattern and this project has paid for that
 * lesson three times (D10/DD-10). The two are not folded into one function
 * because they decide DIFFERENT questions — one asks "did any reference name
 * this group", the other "what is this group's number in the caller's space"
 * — and folding them would make a `--no-captures` composed build ask the
 * first question twice with two different `keep` arrays.
 *
 * AN `A_CALL` IS VISITED AS ITSELF and `u.call.body` is never followed
 * (design §4.4a site 27, `br_strip_caps`' own note): there is nothing to
 * descend into, and following the back edge in a tree REWRITE would rewrite
 * nodes another part of the tree still points at and would not terminate on
 * a recursive callee. Call TARGETS are re-based by the second pass, off the
 * pending records, which is the only place that can tell a locally-resolved
 * call from a deferred one. */
static Ast *rc_remap_caps(Ast *a, const int *map, int nmap)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF: case A_CALL:
            return a;
        case A_CAP:
            a->l = rc_remap_caps(a->l, map, nmap);
            if (a->u.cap.no > 0 && a->u.cap.no < nmap) {
                int to = map[a->u.cap.no];
                if (to == 0) { a = a->l; continue; }   /* ERASED */
                a->u.cap.no = to;
            }
            return a;
        case A_LOOK:
        case A_REP: case A_ATOMIC:
            a->l = rc_remap_caps(a->l, map, nmap);
            return a;
        case A_CAT:
            for (Ast *t = a; t->k == A_CAT; t = t->l)
                t->r = rc_remap_caps(t->r, map, nmap);
            {
                Ast *t = a;
                while (t->l->k == A_CAT) t = t->l;
                t->l = rc_remap_caps(t->l, map, nmap);
            }
            return a;
        case A_ALT:
            for (Ast *t = a; t->k == A_ALT; t = t->l)
                t->r = rc_remap_caps(t->r, map, nmap);
            {
                Ast *t = a;
                while (t->l->k == A_ALT) t = t->l;
                t->l = rc_remap_caps(t->l, map, nmap);
            }
            return a;
        }
        return a;
    }
}

/* ---- marking which groups survive -------------------------------------
 *
 * `keep[i]` is true when local group `i` is DELIVERED (the definition names
 * it) or HIDDEN (the definition's own resolved references reach it). It is
 * derived from the definition's captured `named_groups` and captured
 * `PendingRef` list and from nothing else — in particular NOT from a tree
 * walk, because a tree walk cannot distinguish a call the sub-parse resolved
 * locally from one it deferred, and a deferred call's `target` is 0. */
static void rc_mark_kept(const NamedGroup *names, const PendingRef *pend,
                         bool *keep, int nmap)
{
    for (const NamedGroup *g = names; g; g = g->next)
        if (g->number > 0 && g->number < nmap) keep[g->number] = true;

    for (const PendingRef *pr = pend; pr; pr = pr->next) {
        if (pr->deferred) continue;          /* a FILE reference: not local */
        if (pr->kind == PEND_CALL) {
            int t = pr->node->u.call.target;
            if (t > 0 && t < nmap) keep[t] = true;
        } else {
            for (int i = 0; i < pr->node->u.bref.nrefs; i++) {
                int t = pr->node->u.bref.refs[i];
                if (t > 0 && t < nmap) keep[t] = true;
            }
        }
    }
}

/* ---- the pending-record pass (w1_impl §2.5, pass 2 of 2) ---------------
 *
 * Re-base the resolved targets of exactly the references the SUB-PARSE
 * resolved locally. Stating this as one walk with the tree pass hid that the
 * two need different iteration; stating it as two makes the `(?R)` and
 * deferred cases fall out, because neither is in this list with a resolved
 * value.
 *
 * A REFERENCED GROUP IS NEVER ERASED by construction (`rc_mark_kept` above
 * marks exactly these), so `map[t] == 0` here would be an internal
 * inconsistency rather than an input a pattern can produce; the guard is
 * written as `> 0` so a future tier cannot turn it into a silent zero. */
static void rc_rebase_refs(Ctx *cx, PendingRef *pend, const int *map, int nmap)
{
    for (PendingRef *pr = pend; pr; pr = pr->next) {
        if (pr->deferred) continue;
        if (pr->kind == PEND_CALL) {
            int t = pr->node->u.call.target;
            if (t > 0 && t < nmap && map[t] > 0) pr->node->u.call.target = map[t];
            continue;
        }
        /* `A_BREF.refs` IS A `const int *` and the re-base writes a FRESH
         * array rather than casting the const away. It is not defensiveness:
         * `br_name_run` resolves a duplicated name to a RUN whose members
         * are all in the definition's own space, and the emitted matcher
         * reads that array at match time, so an in-place write would be a
         * write through a pointer the type says nobody writes through — the
         * exact shape a future sharing of one run between two nodes would
         * turn into a silent aliasing bug. One arena array per node costs a
         * handful of bytes on a pattern that has a backreference at all. */
        int n = pr->node->u.bref.nrefs;
        if (n <= 0) continue;
        int *fresh = arena_alloc(&cx->arena, (size_t)n * sizeof *fresh);
        for (int i = 0; i < n; i++) {
            int t = pr->node->u.bref.refs[i];
            fresh[i] = (t > 0 && t < nmap && map[t] > 0) ? map[t] : t;
        }
        pr->node->u.bref.refs = fresh;
    }
}

/* ---- finding a whole-pattern recursion inside a definition -------------
 *
 * `(?R)`, `(?0)`, `(?00)` and `\g<0>` all build an `A_CALL` with
 * `u.call.target == 0` and QUEUE NO PENDING RECORD (`mod_recursion.c:41`
 * and `:128`) — which is precisely what makes them findable here and
 * nowhere later. By the time the composer's re-basing runs, `target == 0`
 * has FOUR readings (the arena zero, `(?R)`, a deferred cross-definition
 * call, and a call this pass has not reached yet), and w1_impl §2.5 deleted
 * revision 1's `target == 0` carve-out for exactly that reason. So the test
 * is not "target is 0" but "this `A_CALL` is in the tree and no record in
 * the sub-parse's own pending list mentions it", which is decidable ONLY
 * here, with the definition's captured list in hand.
 *
 * The membership test is linear in the list. A definition is one pattern
 * line and its call count is a handful; the alternative — a mark bit on the
 * node — would be a field on `Ast` for one question asked once, which
 * PARSE-1 forbids for far better reasons than cost. */
static bool rc_recorded(const Ast *a, const PendingRef *pend)
{
    for (const PendingRef *pr = pend; pr; pr = pr->next)
        if (pr->node == a) return true;
    return false;
}

static const Ast *rc_find_root_call(const Ast *a, const PendingRef *pend)
{
    if (!a) return NULL;
    switch (a->k) {
    case A_CALL:
        return rc_recorded(a, pend) ? NULL : a;
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
    case A_BREF:
        return NULL;
    case A_CAP: case A_LOOK: case A_REP: case A_ATOMIC:
        return rc_find_root_call(a->l, pend);
    case A_CAT: case A_ALT: {
        const Ast *h = rc_find_root_call(a->l, pend);
        return h ? h : rc_find_root_call(a->r, pend);
    }
    }
    return NULL;
}

/* ---- binding one definition -------------------------------------------- */

/* The sub-parse's own refusals must name the DEFINITION's file and line, not
 * an offset into a pattern the author never wrote (w1_impl §2.9: provenance
 * is a property of the SUB-PARSE, not a field on a node — `internal.h`'s
 * PARSE-1 invariant says `Ast` carries no position of any kind). `ctx_fail`
 * takes a pattern offset, so the definition's coordinates go in the TEXT and
 * the offset stays the sub-parse's own, which is the only number that
 * locates a failure inside the definition. */
static void rc_bind(Composer *co, const RxtDef *def)
{
    Ctx *cx = co->cx;

    RxtScope sc = {
        cx->pat, cx->patlen, cx->pos, cx->ncap,
        cx->named_groups, cx->n_named_groups,
        cx->pending_refs, cx->n_pending_refs,
        cx->mods, cx->opt, cx->in_quote, cx->depth
    };

    /* THE WRAPPER TAKES A NUMBER, AND IT IS INTERNAL (w1_impl §2.6, D89
     * point 1). `A_CALL.target` is a group number and `callgraph.c` binds by
     * matching `A_CAP.u.cap.no`, so a callable body must hold a number in
     * the same space every other group is in; a separate id space would be a
     * second key in the binder. The number is never authored, never a
     * `groups[]` row and never a name — Frank's Q-W1 ruling withdrew the
     * caller-visible half r45sem had attached to it. */
    int base = (int)cx->ncap + 1;

    /* `mods` is SEEDED FROM THE DEFINITION BLOCK'S OWN `flags`, not restored
     * and not inherited (r45sem M2): format_design §2.6 makes `flags`
     * block-scoped, so a definition that wrote `flags i` must get it and one
     * that did not must NOT pick up the target's. `pcrec_parse_mods_init`
     * seeds `.caseless` from `cx->opt->flags`, so the seed is supplied by
     * swapping a private options copy in for the sub-parse — the ONE field
     * that differs, with everything else (encoding, the capture request, the
     * budgets) staying the target's, because those are properties of the
     * ARTIFACT and a definition has no artifact of its own. */
    pcrec_options defopt = *cx->opt;
    defopt.flags = (defopt.flags & ~(unsigned long long)PCREC_CASELESS)
                 | (def->flags & (unsigned long long)PCREC_CASELESS);

    cx->pat            = def->pattern;
    cx->patlen         = strlen(def->pattern);
    cx->pos            = 0;
    cx->ncap           = 0;
    cx->named_groups   = NULL;
    cx->n_named_groups = 0;
    cx->pending_refs   = NULL;
    cx->n_pending_refs = 0;
    cx->in_quote       = false;
    cx->depth          = 0;
    cx->opt            = &defopt;
    pcrec_parse_mods_init(cx);

    Ast *body = pcrec_parse_info(cx, NULL);

    int          k     = (int)cx->ncap;
    NamedGroup  *names = cx->named_groups;
    PendingRef  *pend  = cx->pending_refs;

    cx->pat            = sc.pat;
    cx->patlen         = sc.patlen;
    cx->pos            = sc.pos;
    cx->named_groups   = sc.named_groups;
    cx->n_named_groups = sc.n_named_groups;
    cx->pending_refs   = sc.pending_refs;
    cx->n_pending_refs = sc.n_pending_refs;
    cx->mods           = sc.mods;
    cx->opt            = sc.opt;
    cx->in_quote       = sc.in_quote;
    cx->depth          = sc.depth;
    /* `ncap` is NOT restored: the caller's count keeps running upward as
     * definitions are injected above it, and `ncap_primary` (frozen before
     * the first bind) is what `rx_info.ngroups` emits. */
    cx->ncap = sc.ncap;

    /* Q-W2, D89 point 3: `(?R)`/`(?0)`/`(?00)`/`\g<0>` inside a bound
     * definition is REFUSED for W1. After injection the two readings — the
     * caller's root, or the definition's own wrapper — are both defensible,
     * and D87 chose mechanisms over silent defaults. The refusal is raised
     * HERE, at the sub-parse, because nothing later can tell it from the
     * three other situations that leave `u.call.target` at 0 (the arena
     * zero, and a deferred cross-definition call). A whole-pattern
     * recursion queues NO pending record, so it is exactly an `A_CALL` the
     * captured list does not mention — which is what this walk tests. */
    {
        const Ast *rec = rc_find_root_call(body, pend);
        if (rec)
            ctx_fail(cx, 0,
                     "definition '%s' (%s:%zu) uses whole-pattern recursion "
                     "((?R), (?0) or \\g<0>) inside a definition, which this "
                     "build refuses: after composition it could mean the "
                     "caller's whole pattern or the definition's own body, "
                     "and the ruling that picks one is not written yet",
                     def->name, def->file, def->line);
    }

    /* THE MAP (w1_impl §8.0). `nmap` is `k + 1` so a group number indexes it
     * directly; entry 0 is unused and stays 0, which is what makes an
     * unnumbered `A_CAP` (there are none today) fall into the erased arm
     * rather than into an out-of-range read. */
    int   nmap = k + 1;
    bool *keep = arena_alloc(&cx->arena, (size_t)nmap * sizeof *keep);
    int  *map  = arena_alloc(&cx->arena, (size_t)nmap * sizeof *map);
    rc_mark_kept(names, pend, keep, nmap);

    int next = base;
    for (int i = 1; i < nmap; i++) map[i] = keep[i] ? ++next : 0;

    body = rc_remap_caps(body, map, nmap);
    rc_rebase_refs(cx, pend, map, nmap);

    cx->ncap = (unsigned)next;

    /* THE DELIVERED ROWS. A definition's named groups join the caller's
     * `named_groups` list with `scope` set, at their FINAL numbers, so
     * `emit_info_def` sees one list and sorts it once. They are APPENDED
     * conceptually and PREPENDED physically, exactly as the parser's own
     * declarations are (`mod_named_groups.c`), because the emitted order is
     * decided by the sort and not by the list. */
    for (NamedGroup *g = names; g; ) {
        NamedGroup *nx = g->next;
        if (g->number > 0 && g->number < nmap && map[g->number] > 0) {
            g->number = map[g->number];
            g->scope  = def->name;
            g->next   = cx->named_groups;
            cx->named_groups = g;
            cx->n_named_groups++;
        }
        g = nx;
    }

    /* THE INJECTION (w1_impl §2.4): `A_REP{0,0}(A_CAP{base}(body))`. Not a
     * new shape — `mod_recursion.c`'s `(?(DEFINE)…)` port builds exactly
     * this, quoting D71 item 4's "the `{0}` layout rule the R34 verifier
     * forced already IS DEFINE's semantics", so `callgraph.c`'s
     * number-to-`A_CAP` bind, the splice/linkage choice, the slot layout and
     * `rx_group_entry.ref` are all reused unchanged.
     *
     * `greedy` is semantically dead at a zero repetition (the emitter writes
     * "X{0}: matches empty, no code") but is set from the SAME scoped
     * `(?U)` state `p_rep` and the DEFINE port both read, so the injected
     * shape and the textual `(?(DEFINE)…)` control produce structurally
     * identical trees and a check can ASSERT that rather than assume it. */
    Ast *cap = pcrec_ast_node(cx, A_CAP);
    cap->l = body;
    cap->u.cap.no = base;

    Ast *rep = pcrec_ast_node(cx, A_REP);
    rep->l = cap;
    rep->u.rep.rmin = 0;
    rep->u.rep.rmax = 0;
    rep->u.rep.greedy = !cx->mods->ungreedy;

    co->bound[co->nbound].def    = def;
    co->bound[co->nbound].base   = base;
    co->bound[co->nbound].inject = rep;
    co->pend[co->nbound]         = pend;
    co->nbound++;
}

/* ---- the fixpoint ------------------------------------------------------
 *
 * WHICH DEFERRED REFERENCE IS TAKEN NEXT decides the CLOSURE ORDER, which
 * decides the numbers, which a caller can see through `RX_NCAPS` and through
 * the delivered rows' `slot` column. So it is not left to whatever order a
 * prepended list happens to be in: the caller's references are taken in
 * SOURCE ORDER (the list is prepended, so it is walked and the LEFTMOST
 * unbound name is chosen), then each bound definition's own, recursively, in
 * the same rule. That is a depth-independent, text-order closure — the same
 * order a reader gets tracing the file by hand, and the same order the
 * textual oracle control can re-derive from the source without asking the
 * composer.
 *
 * CYCLES ARE LEGAL AND TERMINATE HERE: `bound_by_name` is the visited set,
 * so a definition that reaches itself or reaches back into a caller is bound
 * ONCE and the second reference simply binds to the existing wrapper. */
static const RxtDef *rc_next_wanted(Composer *co, PendingRef *list,
                                    const char **unknown, size_t *at)
{
    const RxtDef *best = NULL;
    size_t        best_at = 0;
    for (PendingRef *pr = list; pr; pr = pr->next) {
        if (!pr->deferred || !pr->name) continue;
        if (bound_by_name(co, pr->name)) continue;
        const RxtDef *d = def_by_name(co->cx, pr->name);
        if (!d) {
            /* A name the set does not declare: not this pass's business, and
             * NOT an error here either — the re-resolution raises it, once,
             * with the leftmost-failure rule the parser already keeps. */
            if (!*unknown || pr->at < *at) { *unknown = pr->name; *at = pr->at; }
            continue;
        }
        if (!best || pr->at < best_at) { best = d; best_at = pr->at; }
    }
    return best;
}

Ast *pcrec_rxt_compose(Ctx *cx, Ast *root)
{
    /* THE EARLY RETURN IS THE IDENTITY CLAIM. Without a definition set this
     * pass is one pointer test, and every artifact pcrec emits without
     * `--source` is byte-identical to before this file existed — which is
     * what makes the identity gate's comparison (A) a real check of this
     * change rather than a tautology. */
    if (!cx->defs || cx->defs->n == 0) return root;

    /* `ncap_primary` is NOT set here: `compile_driver` seeds it from `ncap`
     * on EVERY compile, immediately before this call, so the field is right
     * whether or not this function does anything and `emit_dfa.c` can read
     * it unconditionally. Setting it here as well would be a second writer
     * of one fact, agreeing today and available to disagree later. */

    Composer co;
    co.cx     = cx;
    co.nbound = 0;
    co.bound  = arena_alloc(&cx->arena, cx->defs->n * sizeof *co.bound);
    co.pend   = arena_alloc(&cx->arena, cx->defs->n * sizeof *co.pend);

    /* The worklist. Each round takes the leftmost unbound name reachable
     * from the caller or from anything bound so far; binding it may defer
     * more names, which the next round sees. It cannot run more than
     * `defs->n` rounds, because every round binds one definition and
     * `bound_by_name` never lets one be bound twice. */
    for (size_t round = 0; round <= cx->defs->n; round++) {
        const char *unknown = NULL;
        size_t      uat     = 0;
        const RxtDef *want = rc_next_wanted(&co, cx->pending_refs,
                                            &unknown, &uat);
        for (size_t i = 0; !want && i < co.nbound; i++)
            want = rc_next_wanted(&co, co.pend[i], &unknown, &uat);
        if (!want) break;
        rc_bind(&co, want);
    }

    /* ---- RE-RESOLUTION -------------------------------------------------
     *
     * Every deferred by-name call now binds to its definition's WRAPPER
     * number, which is the group `callgraph.c` will find and the number
     * `--emit-composed` would print. A name the set does not declare
     * RE-RAISES `mod_backrefs.c`'s own refusal — the same sentence at the
     * same offset — so the four `perr` blocks in
     * `tests/recursion/d27/sr_refusals.rxt` are untouched by this step, and
     * a file that composes nothing behaves as it always did.
     *
     * THE LEFTMOST FAILURE IS STILL THE ONE REPORTED, and under composition
     * a bare offset is no longer totally ordered — `pr->at` may be an offset
     * into a DEFINITION's text (r45sem S2). The ordering key is therefore
     * (which list, then offset): the caller's references are compared among
     * themselves first, and only if the caller has none does a definition's
     * unresolved name get reported, naming that definition's file and line
     * so the two coordinate systems are never silently mixed. */
    for (PendingRef *pr = cx->pending_refs; pr; pr = pr->next) {
        if (!pr->deferred || !pr->name) continue;
        Bound *b = bound_by_name(&co, pr->name);
        if (b) { pr->node->u.call.target = b->base; pr->deferred = false; continue; }
    }
    {
        const PendingRef *worst = NULL;
        for (const PendingRef *pr = cx->pending_refs; pr; pr = pr->next)
            if (pr->deferred && pr->name && (!worst || pr->at < worst->at))
                worst = pr;
        if (worst)
            ctx_fail(cx, worst->at,
                     "%s refers to a capture group named '%s', which this "
                     "pattern does not declare", worst->what, worst->name);
    }
    for (size_t i = 0; i < co.nbound; i++) {
        for (PendingRef *pr = co.pend[i]; pr; pr = pr->next) {
            if (!pr->deferred || !pr->name) continue;
            Bound *b = bound_by_name(&co, pr->name);
            if (b) { pr->node->u.call.target = b->base; pr->deferred = false; continue; }
            ctx_fail(cx, 0,
                     "definition '%s' (%s:%zu): %s refers to '%s', which is "
                     "neither one of its own groups nor a definition this "
                     "source declares",
                     co.bound[i].def->name, co.bound[i].def->file,
                     co.bound[i].def->line, pr->what, pr->name);
        }
    }

    /* ---- THE SPLICE ----------------------------------------------------
     *
     * Concatenated onto the caller's root in CLOSURE ORDER, left-leaning, so
     * the spine `br_strip_caps` and every other `A_CAT` walker expects is
     * the spine they get. Nothing is injected when nothing was bound, which
     * is the case for a `--source` build whose target references no
     * definition — and that artifact is then byte-identical to the same
     * pattern built with plain `-p`, which is the cheapest control this step
     * has. */
    for (size_t i = 0; i < co.nbound; i++) {
        Ast *cat = pcrec_ast_node(cx, A_CAT);
        cat->l = root;
        cat->r = co.bound[i].inject;
        root = cat;
    }
    return root;
}
