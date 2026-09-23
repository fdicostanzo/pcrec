/* mod_vars.c — module `vars` ([VAR]): `${name}` in a PATTERN, whose bytes the
 * CALLER supplies per call.
 *
 * Design: docs/design/variables_pattern.md (this consumer),
 * docs/design/variables_common.md (the grammar §1, the value model §2, the
 * call interface §3), panel `docs/dev/reviews/2026-09-23-r1-var-design.md`.
 * Read `variables_pattern.md` §1 before touching this file: everything below
 * follows from its one sentence — *a pattern variable is a backreference
 * whose span is supplied by the caller instead of being read out of
 * `slot_values[]`*.
 *
 * THIS FILE IS SMALL BECAUSE THE GRAMMAR IS NOT HERE. `src/core/varexp.c`
 * parses `${ [!] selector [op word] }` for BOTH consumers (the replacement
 * side is `subst-pcrec`'s, unbuilt); this file is the PATTERN consumer's
 * doorway, node constructor and end-of-parse name resolution, and nothing
 * else. §1.3's one per-consumer difference — which scope a bare selector
 * resolves in — costs no code here at all: in a pattern there is no match
 * when a variable is expanded, so there is no group scope to resolve in and
 * the selector is always the caller's variable.
 *
 * THERE IS NO DOORWAY DISPATCH, and that is `RK_BARE`'s charter rather than
 * an omission. `$` is base grammar, parsed directly in `p_atom`; it has no
 * `\` or `(?` doorway, so `pcrec_registry_find`/`pcrec_ext_gate` are never
 * called for it and cannot be called for `${` either. Recognition is one
 * `if` in `p_atom` and the gate is a direct `pcrec_feature_enabled` test
 * here — `\Q`'s FEAT_QUOTING shape, one construct over. The registry row
 * exists for the DUMP and for the D67 stamp `forces_registry` reads.
 *
 * WITH THE MODULE OFF, `${` IS REFUSED, NOT PARSED AS TODAY. The two design
 * notes disagree about this: `variables_common.md` §4.1 says "with the module
 * off today's parse stands in full" while `variables_pattern.md` §7's table
 * says it refuses with "requires module 'vars'". The table is right and §4.1
 * is arguing a different point (that the COLLISION rule is satisfied, which
 * it is) one sentence too far. This file takes the refusal, for the house
 * rule D34 ruling 5 / extension_design.md §12 states generally — recognisers
 * are always live, production is gated, and a recognised-but-gated construct
 * says which module would implement it — and because the alternative is to
 * hand a caller who forgot `--features vars` a pattern that CANNOT MATCH
 * ANYTHING (`variables_common.md` §0.2's proof) with no diagnostic at all.
 * The refusal-set move it costs is measured at ZERO shipped patterns: the
 * corpus contains no `${` in any `pattern` line (§0.2's own command,
 * re-run for this lane). */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

/* The `${...}` row: `RK_BARE`, selector `$`, tail `{`. Looked up rather than
 * held, because `RK_BARE`'s rows are never reached through
 * `pcrec_registry_find` and a producer that cached a pointer would be the
 * second home for a fact the table already owns. */
static const RegRow *vars_row(void)
{
    size_t n;
    const RegRow *rows = pcrec_registry(RK_BARE, &n);
    for (size_t i = 0; i < n; i++)
        if (rows[i].sel == '$' && rows[i].tail && rows[i].tail[0] == '{')
            return &rows[i];
    return NULL;   /* unreachable: the row is a static table entry */
}

/* Is the `$` at `cx->pos - 1` the start of a `${...}` variable reference
 * rather than an end-of-line assertion? Purely LEXICAL — it does not consult
 * the feature mask, because a recogniser must not depend on what is switched
 * on (extension_design.md §12) and because the gate's own refusal below needs
 * to know it was asked. */
bool pcrec_vars_is_doorway(const Ctx *cx)
{
    return cx->pos < cx->patlen && cx->pat[cx->pos] == '{';
}

/* Record `name` in `Ctx.var_names` if it is new, and return its index —
 * the artifact's OWN internal slot number, never anything a caller writes
 * (variables_common.md §3.1-§3.2, Frank's 2026-09-23 by-name ruling).
 *
 * FIRST-MENTION ORDER IS THE CONTRACT: it is the order `<PREFIX>_VAR_<NAME>`
 * macros are assigned in and the order `rx_info.vars` lists names in, so an
 * emitted artifact and a caller reading its names table see one order. The
 * scan is linear because the set is 1-3 names in every case this design has
 * looked at, which is the same D77 reasoning that keeps the MATCH-time
 * resolution a linear scan. */
static int vars_intern(Ctx *cx, const char *name)
{
    for (unsigned i = 0; i < cx->n_vars; i++)
        if (strcmp(cx->var_names[i], name) == 0) return (int)i;

    /* Grow by doubling into the arena; the old array is abandoned there,
     * which is correct for a list that lives for the whole compile and is
     * rebuilt at most log(n) times over 1-3 names. */
    unsigned cap = 1;
    while (cap < cx->n_vars + 1) cap *= 2;
    if (cx->n_vars == 0 || (cx->n_vars & (cx->n_vars - 1)) == 0) {
        const char **nv = pcrec_arena_alloc(&cx->arena, cap * sizeof *nv);
        for (unsigned i = 0; i < cx->n_vars; i++) nv[i] = cx->var_names[i];
        cx->var_names = nv;
    }
    cx->var_names[cx->n_vars] = name;
    return (int)cx->n_vars++;
}

/* Intern every selector `x` mentions, including the ones nested inside its
 * operator's WORD — which is why this recurses rather than reading `x->name`
 * alone. `${a:-${b}}` mentions both `a` and `b`, and an artifact that
 * resolved only `a` would evaluate the fallback against an unresolved slot. */
static void vars_intern_tree(Ctx *cx, const VarExp *x)
{
    (void)vars_intern(cx, x->name);
    for (size_t i = 0; i < x->nword; i++)
        if (x->word[i].nest) vars_intern_tree(cx, x->word[i].nest);
}

/* Record `x` in `Ctx.var_exps` if no expansion spelled the same way is there
 * already, and return its index — the EXPANSION slot the emitted resolver
 * writes and the emitted instruction reads.
 *
 * THE KEY IS THE CANONICAL RENDERING, not the node address: two references
 * written `${v}` in two places are one expansion with one answer, and the
 * render is what makes "written the same way" checkable without a structural
 * comparison function that would be a second definition of equality
 * (`pcrec_varexp_render`'s own header states why the render is canonical).
 *
 * A NESTED expansion gets its own slot too, and always a LOWER one than the
 * expansion that contains it, because this is called bottom-up — which is
 * what lets the emitted resolver evaluate the table in index order with no
 * dependency analysis of its own. */
static int vars_intern_exp(Ctx *cx, const VarExp *x)
{
    const char *key = pcrec_varexp_render(&cx->arena, x);
    for (unsigned i = 0; i < cx->n_var_exps; i++)
        if (strcmp(pcrec_varexp_render(&cx->arena, cx->var_exps[i]), key) == 0)
            return (int)i;

    unsigned cap = 1;
    while (cap < cx->n_var_exps + 1) cap *= 2;
    if (cx->n_var_exps == 0 || (cx->n_var_exps & (cx->n_var_exps - 1)) == 0) {
        const VarExp **nv = pcrec_arena_alloc(&cx->arena, cap * sizeof *nv);
        for (unsigned i = 0; i < cx->n_var_exps; i++) nv[i] = cx->var_exps[i];
        cx->var_exps = nv;
    }
    cx->var_exps[cx->n_var_exps] = x;
    return (int)cx->n_var_exps++;
}

/* Intern `x` and every expansion nested in its operator's WORD, BOTTOM-UP, so
 * a nested expansion's slot is always below its container's. Returns `x`'s
 * own slot. */
static int vars_intern_exp_tree(Ctx *cx, const VarExp *x)
{
    for (size_t i = 0; i < x->nword; i++)
        if (x->word[i].nest) (void)vars_intern_exp_tree(cx, x->word[i].nest);
    return vars_intern_exp(cx, x);
}

/* Parse the `${...}` whose `$` is at `at` (so `cx->pos` is one past it, on
 * the `{`) and return the `A_VAR` node, leaving `cx->pos` one past the
 * closing `}`. Refuses — never returns — on a gate miss or a grammar error.
 *
 * Reads `cx->mods->caseless`, which is why this function and not the
 * expansion parser owns the node: caselessness is the scoped `(?i)` state in
 * force AT THE REFERENCE (D62; measured for backreferences at
 * backrefs_design.md §4 axis B, and the same fact one kind over), and
 * src/core/ may not see `ParseMods` at all. */
Ast *pcrec_vars_atom(Ctx *cx, size_t at)
{
    const RegRow *rw = vars_row();

    if (!pcrec_feature_enabled(cx->enabled_features, FEAT_VARS))
        pcrec_ctx_fail(cx, at, "${...} requires module '%s'",
                       rw ? rw->module : "vars");

    size_t pos = at;
    VarExpErr err;
    const VarExp *x = pcrec_varexp_parse(&cx->arena, cx->pat, cx->patlen,
                                         &pos, &err);
    if (!x) pcrec_ctx_fail(cx, err.at, "%s", err.msg);

    Ast *a = pcrec_ast_node(cx, A_VAR);
    a->u.var.exp = x;
    a->u.var.slot = -1;             /* assigned by pcrec_vars_resolve */
    a->u.var.caseless = cx->mods->caseless;
    /* SR-8/D67: the stamp, so `forces_registry` finds the VM_ONLY row and
     * `--engine=dfa` names the construct. The whole engine decline is this
     * one line; the PREFILTER decline is `has_var`'s, in select_engine.c. */
    pcrec_ast_stamp(cx, a, rw, at);

    cx->pos = pos;
    return a;
}

/* Assign every `A_VAR` in the tree its internal slot, at END OF PARSE.
 *
 * WHY NOT AT THE DOORWAY. A doorway sees one reference at a time and could
 * intern perfectly well — but a tree REWRITE may delete references (the
 * composer, `--no-captures`' strip, `altcls` factoring) and the artifact's
 * name table must describe the tree that is EMITTED, not the tree that was
 * parsed. Running here, after the parse and before any rewrite, is the same
 * position `pcrec_bref_resolve` occupies and for a related reason: this is
 * the one place that has seen every reference and no rewrite yet.
 *
 * `[PATFACTS]` (D120) is the eventual general home for a walk like this; the
 * migration is its own, under its implement-then-replace clause. */
static void vars_assign(Ctx *cx, Ast *a);

/* The per-node half of `vars_assign`'s walk. */
static void vars_assign_node(Ctx *cx, Ast *a)
{
    if (a->k != A_VAR) return;
    vars_intern_tree(cx, a->u.var.exp);
    a->u.var.slot = vars_intern_exp_tree(cx, a->u.var.exp);
}

/* Walk the tree ITERATIVELY down CAT/ALT spines (D10/DD-10/K20: a spine is as
 * long as the pattern and this project has segfaulted its own compiler for
 * want of this), recursing only into items hanging off them, and NEVER
 * following `u.call.body` — the AST's one back edge, whose callee this walk
 * already visits at its own lexical position (subroutines_design.md §4.4). */
static void vars_assign(Ctx *cx, Ast *a)
{
    for (;;) {
        if (!a) return;
        vars_assign_node(cx, a);
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF: case A_VAR: case A_CALL:
            return;
        case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            Ast *t = a;
            for (; t->k == k; t = t->l) vars_assign(cx, t->r);
            a = t;
            continue;
        }
        }
        /* No `default:` — mrl.c's rule; the switch above is exhaustive. */
        return;
    }
}

/* END-OF-PARSE ENTRY, called once from `pcrec_parse_info` beside
 * `pcrec_bref_resolve`. A var-free pattern costs one tree walk that interns
 * nothing and leaves `Ctx.var_names` NULL — which is what makes this module
 * free for every artifact that does not use it. */
void pcrec_vars_resolve(Ctx *cx, Ast *root)
{
    vars_assign(cx, root);
}

/* Does this tree contain an `A_VAR`? The THIRD whole-tree predicate in
 * `prefilter_decision`'s hand-written set, joining `pcrec_has_bref` and
 * `pcrec_has_linked_call` — the `[DD-14]` precedent for exactly this shape.
 *
 * IT IS NOT AN OPTIMIZATION DECLINE. `src/ir/nfa.c` has no lowering for
 * `A_VAR` at all (determinization cannot see bytes that do not exist until
 * the call), so a prefilter build that walked one reaches that file's loud
 * internal error. Engine selection alone does NOT stop it: a VM-only pattern
 * normally still gets a hybrid DFA prefilter, so "VM-only" and
 * "prefilter-free" are two facts with two mechanisms, and this is the second
 * one. `variables_pattern.md` §3, and the D6 panel's MECH-B1.
 *
 * `[PATFACTS]` (D120) is named in that section as the eventual general home
 * for all three predicates; until it lands this is the shape the tree has. */
static void vars_has_visit(void *ud, const Ast *a)
{
    if (a->k == A_VAR) *(bool *)ud = true;
}

bool pcrec_has_var(const Ast *root)
{
    bool found = false;
    if (root) pcrec_ast_visit(root, vars_has_visit, &found);
    return found;
}
