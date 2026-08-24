/* mod_lookaround.c — module `lookaround` ([M6.6.2]): the ONE group port all
 * six registry rows dispatch through.
 *
 * Design: docs/design/lookaround_design.md, panel-approved at R33
 * (docs/dev/reviews/2026-08-23-r33-lookaround-design.md). §8.1 is this file's
 * charter; §2.5, §2.6 and §2.7 are the three rules it enforces.
 *
 * WHAT A LOOKAROUND IS, in one sentence (design §0.2): a SUB-MATCH whose
 * result is a VERDICT and whose POSITION is discarded. Everything this file
 * does follows from that — the node consumes nothing (`pcrec_minw` and
 * `pcrec_maxw` both answer 0, and `vm_nullable` answers true), it is not a
 * capturing construct (`cx->ncap` is untouched here; groups INSIDE the body
 * capture exactly as they would anywhere else, measured: `(?=(a))a` on "a" is
 * (0,1) with g1=(0,1)), and the lowering is `vm_atomic`'s shape plus a saved
 * cursor (src/gen/emit_vm.c's `vm_look`).
 *
 * ONE PORT FOR SIX ROWS, and design §8.1's reason is the one that matters: the
 * six constructs differ ONLY in the three `Ast.u.look` flags this function
 * sets, so a second port function would be a SECOND PLACE the `<`-tail split
 * is decided. The dispatch below is a single table keyed on the row's own
 * `sel`/`tail` — the same two fields the registry arbitrated on to get here —
 * so the port cannot disagree with the row that elected it.
 *
 * THE WAVE B+C SPLIT, AND IT IS A TAIL CHECK RATHER THAN A REFUSAL PATH
 * (design §8.3, R33 V-3). D65 derives a row's `built` column from the PORT's
 * `ExtResult` at `WANT_RESULT` (src/parse/syntax_dump.c) and never runs the
 * emitter, so the column flips for exactly the rows whose tail this function
 * ACCEPTS. At this wave the three LOOKAHEAD tails (`=`, `!`, `*` at the `(?`
 * doorway) are recognised and the three `<` tails are DECLINED with the
 * enabled-but-unbuilt diagnostic — so `--list-syntax` reads `built` for
 * `(?=...)`, `(?!...)`, `(?*a)` and `unbuilt` for the three lookbehind rows,
 * which is the honest answer while `vm_look` has no back-step. **WAVE D
 * DELETES `la_kind`'s three `false` rows** (and the `LA_UNBUILT` arm with
 * them) when src/gen/enc's `PCREC_ENCE_BACK_STEP` lands; nothing else in this
 * file changes for the lookbehind, because `Ast.u.look.behind` is already set
 * from the table.
 *
 * WHY THE DECLINE IS AN `EXT_REFUSAL` AND NOT AN `EXT_NOT_MINE`: the `(?`
 * doorway CANNOT decline (internal.h's ExtResult comment — its catch-all is
 * REJECTED, so `EXT_NOT_MINE` from it is a registry defect the wall reports).
 * A refusal answered AT `WANT_RESULT` is exactly D33's "gate open, port
 * missing" signal, which is the one `pcrec_construct_built_status` reads.
 *
 * `\K` IS REFUSED INSIDE A LOOKAROUND (§2.7), PERMANENTLY. libpcre2 10.46
 * refuses it in all four polarities with err 199, whose own text names
 * `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK`; pcrec matches the DEFAULT and does not
 * implement the option (adopting any `EXTRA_*` bit is a D38 ruling event).
 * Frank ruled the reopening closed on 2026-08-23: "it's considered bad mojo
 * and weird". THE CHECK IS NEEDED RATHER THAN FREE — `\K` is module
 * `assertions` and already ships, so without it `(?=a\K)b` would compile
 * today's `\K` inside tomorrow's lookaround and quietly move the reported
 * match start. `la_has_kreset` below is RECURSIVE THROUGH NESTED GROUPS AND
 * NESTED LOOKAROUNDS and stops AT the assertion's `)` (R33 C1-7): §2.7's
 * eleven refused cells include `(?=(a\K))x`, `(?=a(?:\K))x` and
 * `(?=(?:(?=\K)))x` — the three an immediate-children check would miss — and
 * its four COMPILING cells (`(?=a)\Kb`, `a(?=b)\Kc`, `(?<=a)\Kb`, `a\Kb`) are
 * what a check latching on "a lookaround was seen" would wrongly break. Both
 * sets are `tests/lookaround/refused.rxt`'s and sabotage row S128's.
 *
 * WHAT THIS FILE DELIBERATELY DOES NOT DO. It writes `widths = NULL` and
 * `nbranch = 0`: the width TABLE is the LOOKBEHIND's (§2.5, §3.1(c)) and wave
 * D computes it here with `pcrec_minw`/`pcrec_maxw` over the body's top-level
 * branches. A LOOKAHEAD has no width rule at all — any body is legal, measured
 * in both oracles — so NULL is the answer and not a placeholder.
 */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

/* THE ROW TABLE — the six constructs, and the only place the three flags are
 * decided. Keyed on the row's own `sel` and `tail`, the two fields
 * `pcrec_registry_arbitrate` already matched to elect the row, so this table
 * cannot elect a different construct than the registry did.
 *
 * `built` is the WAVE B+C SPLIT and nothing else: a row with `built == false`
 * is declined at `WANT_RESULT`, which is what D65 reads as `unbuilt`. */
typedef struct {
    int         sel;
    const char *tail;       /* NULL for a tail-less row */
    bool        behind;
    bool        neg;
    bool        atomic;
    bool        built;      /* wave B+C: false for the three `<` tails */
    const char *shown;      /* the construct, for the unbuilt diagnostic */
} LaRow;

static const LaRow la_rows[] = {
    /* sel  tail  behind  neg   atomic  built  shown        */
    { '=',  NULL, false, false, true,  true,  "(?=...)"  },
    { '!',  NULL, false, true,  true,  true,  "(?!...)"  },
    /* `(?*X)` is PCRE2's NON-ATOMIC positive lookahead — the `(?` spelling of
     * `(*napla:...)`, proven behaviourally rather than by its name (§2.2, on
     * "abab"): `(?*(a|ab))\1$` is (2,4) where `(?=(a|ab))\1$` is NOMATCH. */
    { '*',  NULL, false, false, false, true,  "(?*...)"  },
    /* THE THREE `<` TAILS — recognised, DECLINED at this wave. `(?<` is three
     * constructs and a name, split by tail at SR-9; every other tail byte is
     * the named-group row and never reaches this port. */
    { '<',  "=",  true,  false, true,  false, "(?<=...)" },
    { '<',  "!",  true,  true,  true,  false, "(?<!...)" },
    { '<',  "*",  true,  false, false, false, "(?<*...)" },
};

static const LaRow *la_kind(const RegRow *rw)
{
    for (size_t i = 0; i < sizeof la_rows / sizeof la_rows[0]; i++) {
        const LaRow *k = &la_rows[i];
        if (k->sel != rw->sel) continue;
        if ((k->tail == NULL) != (rw->tail == NULL)) continue;
        if (k->tail && strcmp(k->tail, rw->tail) != 0) continue;
        return k;
    }
    return NULL;
}

/* §2.7's scope, as a walk. TRUE when an `A_KRESET` occurs ANYWHERE in this
 * subtree — through nested groups, quantifiers, atomic groups and nested
 * lookarounds alike.
 *
 * A nested lookaround's own body is reached by its own port first (the inner
 * `(?=\K)` of `(?=(?:(?=\K)))x` refuses before this walk ever runs), so the
 * `A_LOOK` arm below is belt-and-braces rather than the mechanism — but it is
 * the arm a reader would expect to find, and leaving it out would make the
 * three-cell claim above depend on parse ORDER rather than on this predicate.
 *
 * BOTH SPINES ARE WALKED ITERATIVELY (D10/DD-10): a flat concatenation is as
 * long as the pattern, and this project has paid for that lesson three times.
 * There is NO `default:` — mrl.c:18-24's rule — so a node kind added later is
 * a compile error here rather than a silent "no `\K` in that". */
static bool la_has_kreset(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_KRESET:
            return true;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_BREF:
            return false;
        case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            const Ast *t = a;
            for (; t->k == k; t = t->l)
                if (la_has_kreset(t->r)) return true;
            a = t;
            continue;
        }
        }
        return false;
    }
}

ExtResult pcrec_laport_group(Ctx *cx, const RegRow *rw, ExtWant want,
                             size_t at, size_t from)
{
    const char *p = cx->pat;
    const size_t n = cx->patlen;

    /* The doorway's contract (ExtWant, internal.h): the cursor moves only
     * under WANT_RESULT, and this port is only ever called there — the gate
     * demotes a disabled module's ask to WANT_VERDICT, which ext.c answers
     * with the module refusal before any port runs. `want` is still READ, by
     * the REFUSE macro below, which stamps it as `answered_at`. */
    const LaRow *k = la_kind(rw);
    if (!k) BAD_ROW(at, "a module 'lookaround' row");

    /* THE WAVE B+C SPLIT (§8.3). Declined BEFORE the body is parsed: a
     * construct with no lowering owes its diagnostic at its own offset, not
     * after a sub-parse that might raise a different one first. */
    if (!k->built)
        REFUSE(at, "module '%s' " PCREC_UNBUILT_MARKER " %s is not "
                   "implemented yet", rw->module, k->shown);

    /* A body-carrying group, so the SCOPED inline-option state is saved and
     * restored around the body exactly as `p_group_body`'s plain-`(` tail and
     * mod_atomic_groups.c's port do — measured behaviour, not a choice:
     * `(?i)` set inside a group is restored at the immediately-enclosing `)`.
     * It is NOT a capturing group (PCRE2 gives a lookaround no number), so
     * `cx->ncap` is untouched. */
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

    /* §2.7, and the offset is the ASSERTION's rather than the `\K`'s because
     * `Ast` carries no position of any kind (PARSE-1's own note). D26 puts the
     * wording in tier 3 and the OFFSET convention in tier 2: pointing at the
     * construct pcrec is refusing is that convention. */
    if (la_has_kreset(body))
        REFUSE(at, "\\K is not allowed inside a lookaround");

    /* An EMPTY body needs nothing special — `pcrec_parse_body` returns an
     * A_EMPTY and §3's shapes swallow it, which is why `(?=)` and `(?!)` ship
     * (§2.6, measured in both oracles: `a(?=)b` is (0,2), `a(?!)b` is NOMATCH,
     * `(?:(?!))|a` is (0,1)). The cells are in the corpus because "legal" is
     * the surprising answer, not because the code has an arm for them. */

    Ast *a = pcrec_ast_node(cx, A_LOOK);
    a->l = body;
    /* `r` is unused for this kind — internal.h's A_LOOK comment. */

    /* THE THREE FLAGS, D62 state: resolved HERE, by the position that knows,
     * and read by `vm_look` alone. */
    a->u.look.behind = k->behind;
    a->u.look.neg    = k->neg;
    a->u.look.atomic = k->atomic;
    /* THE WIDTH TABLE IS THE LOOKBEHIND's (§2.5/§3.1(c)) — wave D fills it
     * from `pcrec_minw`/`pcrec_maxw` over the body's `info.nbr` top-level
     * branches. A LOOKAHEAD has no width rule, so NULL is the ANSWER and not a
     * placeholder, and `nbranch` is 0 with it because the two are one fact. */
    a->u.look.widths  = NULL;
    a->u.look.nbranch = 0;
    (void)info;

    /* PROPAGATED, not defaulted — A_CAP's rule and A_ATOMIC's, for their
     * reason: `not_repeatable` is a property of what this construct RETURNS to
     * `p_rep`, and `p_rep` tests the returned node's own flag. Note what this
     * does and does not decide. `(?=a)*` and the other thirteen quantified
     * forms compile (§2.6, and `pcrec_is_bare_anchor` answers FALSE for
     * A_LOOK, which is what lets them); `(?=(?i))*` COMPILES in libpcre2 10.46
     * (measured at this wave) and pcrec refuses it, exactly as pcrec already
     * refuses `((?i))*` and `(?>(?i))*`. That is ONE pre-existing question
     * about a bare option run — parse.c's A_CAP arm records it — and
     * propagating here keeps it one question instead of giving this construct
     * a second, divergent answer. */
    a->not_repeatable = body->not_repeatable;

    /* SR-8/D67: the stamp, from the row this port was dispatched on — the ROW
     * and not a copy of its mask, so `engines` keeps exactly one home and
     * src/opt/select_engine.c can also name the construct. D67 also says
     * STAMP EVERY NODE THE PORT BUILDS; this port builds exactly one. */
    pcrec_ast_stamp(cx, a, rw, at);

    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = a;
    res.end = end;
    return res;
}
