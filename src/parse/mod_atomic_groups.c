/* mod_atomic_groups.c — module `atomic-groups` ([M6.4.2]): the `(?>...)`
 * group port, and the registry lookup src/parse/parse.c's possessive-suffix
 * desugaring stamps from.
 *
 * Design: docs/design/atomic_groups_design.md, panel-approved at R31
 * (docs/dev/reviews/2026-08-22-r31-atomic-groups-design.md).
 *
 * WHAT AN ATOMIC GROUP IS, in one sentence: `(?>X)` matches whatever `X`
 * matches at the current position on `X`'s OWN first attempt, and then refuses
 * to reconsider — if what follows fails, the whole group fails rather than
 * letting `X` try again. That is a CUT, and the whole of the lowering is
 * "record the resume-stack depth on entry, run the body, truncate back to that
 * depth when the body first succeeds" (src/gen/emit_vm.c's `vm_atomic`).
 *
 * TWO SPELLINGS, ONE NODE KIND. `(?>X)` arrives here. The possessive suffixes
 * `X*+ X++ X?+ X{n,m}+` do NOT — they are quantifier suffixes recognised by
 * `p_rep` in parse.c, which desugars `X q+` to `A_ATOMIC(A_REP(X))`, PCRE2's
 * own definition of the construct. That equivalence is MEASURED rather than
 * read off the documentation, and the measurement had to be REBUILT once: the
 * first version tested only bodies with a unique iteration (`a*+` vs `(?>a*)`),
 * where per-iteration and group-exit cutting CANNOT differ. Re-measured over
 * bodies whose iteration can end in two places — `(?:a|ab)`, `(?:ab?)`,
 * `(?:a|bc)`, `(?:a*)`, `(?:a?)` — it is 18 pairs / 47 cells / 28 of them
 * non-unique-body / 0 disagreeing
 * (atomic_groups_measurements/out/atomic_semantics.txt).
 *
 * WHY THE SUFFIXES HAVE ROWS BUT NO PORT. registry.c's header names the
 * possessive `+` as a deliberate exemption: it is a sub-case of a BASE
 * construct, and giving it a doorway would cost the base tier a registry lookup
 * on every quantifier. The exemption stands — nothing on the parse path
 * consults RK_QUANTSUFFIX by lookup — but the rows now exist so the DUMP is
 * complete (`--list-syntax`, and the generated index in
 * docs/pcre2_compliance.md), and so that SR-8 has a row to name when it
 * explains why a possessive pattern is VM-only. `pcrec_atomic_suffix_row`
 * below is how parse.c reaches the row for the spelling it just parsed.
 *
 * THE ENGINE STAMP (SR-8, D67). Both producers write `Ast.reg`, and that is
 * the whole of this module's contribution to engine selection — there is no
 * `forces_atomic` analysis, because D67 replaced the per-construct shape with
 * ONE generic consultation over producer-stamped nodes. A node that reaches
 * `src/opt/select_engine.c` unstamped claims BOTH engines, which fails in the
 * UNSOUND direction on purpose (contract note 2): what catches a forgotten
 * stamp is the generic tripwire in tests/registry/registry_check.c — every
 * VM_ONLY row with a producer must refuse `--engine=dfa` BY NAME — not a lucky
 * default. Sabotage row S96 removes the stamp and that assertion goes red.
 *
 * THE OFFSET COMES WITH THE STAMP. `pcrec_ast_stamp` writes `Ast.reg` AND
 * records `Ctx.first_vmonly_pos` in one statement, so the row and the offset
 * the `engine_why` diagnostic pairs cannot be recorded at different moments and
 * drift. The offset is needed at all because no AST node carries a source
 * position; the VERDICT still walks the post-discharge tree, because a
 * parse-time counter would keep counting nodes a rewrite deleted.
 *
 * NOT A SCOPE BOUNDARY FOR ANYTHING BUT ITS OWN BODY. `(?>` is a
 * body-carrying group, so it saves and restores the scoped inline-option state
 * around its body exactly as `p_group_body`'s plain-`(` tail does and as
 * mod_named_groups.c's port does — measured behaviour, not a choice: `(?i)`
 * set inside a group is restored at the immediately-enclosing `)`. It is NOT a
 * capturing group (PCRE2: `(?>` takes no number), so `cx->ncap` is untouched. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

ExtResult pcrec_agport_atomic(Ctx *cx, const RegRow *rw, ExtWant want,
                              size_t at, size_t from)
{
    const char *p = cx->pat;
    const size_t n = cx->patlen;

    /* `from` is the byte after the `>` selector — the first byte of the body.
     * The doorway's contract (ExtWant, internal.h) is that the cursor moves
     * only under WANT_RESULT, and this port is only ever called there: the
     * gate demotes a disabled module's ask to WANT_VERDICT, which ext.c
     * answers with the module refusal before any port runs. */
    (void)want;

    ParseMods saved_mods = *cx->mods;
    size_t    saved_pos  = cx->pos;
    cx->pos = from;

    AltInfo info;
    Ast *body = pcrec_parse_body(cx, &info);

    if (cx->pos >= n || p[cx->pos] != ')') {
        *cx->mods = saved_mods;
        cx->pos = saved_pos;
        REFUSE(at, "missing closing ) for group");
    }
    size_t end = cx->pos + 1;
    *cx->mods = saved_mods;
    cx->pos = saved_pos;

    /* The S-M1 anchor wrap, shared rather than mirrored: `(?>^)*` stays
     * quantifiable exactly as `(^)*` is. mod_named_groups.c's own copy of this
     * rule had gone stale before [M6.2] wave D made it one function; this site
     * calls that one function. */
    body = pcrec_wrap_bare_anchor(cx, body);

    /* `(?>)` IS LEGAL AND MATCHES EMPTY — measured against libpcre2 10.46:
     * `(?>)` on "abc" is (0,0) and `(?>)a` is (0,1). `pcrec_parse_body` returns
     * an A_EMPTY for an empty body, so nothing special is needed here; the
     * cell is in the corpus because "legal" is the surprising answer. */

    Ast *a = pcrec_ast_node(cx, A_ATOMIC);
    a->l = body;
    /* PROPAGATED, not defaulted — A_CAP's own rule, and for the same reason:
     * `not_repeatable` is a property of what this construct RETURNS to p_rep,
     * and p_rep tests the returned node's flag. `(?>(?i))*` must answer the
     * same way `((?i))*` does rather than diverging on the wrapper. */
    a->not_repeatable = body->not_repeatable;
    /* SR-8/D67: the stamp, from the row this port was dispatched on. Not a
     * copy of the mask — the ROW, so the `engines` column keeps exactly one
     * home and `select_engine.c` can also name the construct. */
    pcrec_ast_stamp(cx, a, rw, at);

    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = a;
    res.end = end;
    return res;
}

const RegRow *pcrec_atomic_suffix_row(int quant_byte)
{
    size_t n;
    const RegRow *rows = pcrec_registry(RK_QUANTSUFFIX, &n);
    for (size_t i = 0; i < n; i++)
        if (rows[i].sel == quant_byte) return &rows[i];
    return NULL;
}
