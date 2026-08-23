/* atomic.c — module `atomic-groups`' AST-level pass and its two walks
 * ([M6.4.2], docs/design/atomic_groups_design.md §5.3/§5.4).
 *
 * THREE THINGS LIVE HERE, and they are here together because they are the
 * three questions nothing else in the tree can answer about an `A_ATOMIC`:
 *
 *   pcrec_has_atomic      does this tree still carry a cut?  (H3's predicate)
 *   pcrec_ast_stamped_by  did a given registry row's producer build anything
 *                         in this tree?  (D65's built-status derivation, for
 *                         the rows that reach no doorway)
 *   pcrec_discharge_atomic delete every cut that is PROVABLY a no-op
 *
 * RECURSION DISCIPLINE (D10/DD-10/R1 R-2, and K20 the third time): `A_CAT` and
 * `A_ALT` spines are LEFT-NESTED and as long as the pattern, so every walk
 * below descends a spine ITERATIVELY and recurses only into the items hanging
 * off it, whose depth the parser's group-nesting cap bounds. A
 * 20,000-character pattern segfaulted pcrec once already for want of this.
 *
 * NONE OF THE THREE SWITCHES CARRIES A `default:` — mrl.c:18-24's rule. A node
 * kind added after this file is written must be a COMPILE ERROR at each of
 * them, because "can this construct contain a cut", "can it carry a producer's
 * stamp" and "is it transparent to the discharge" are three questions only the
 * author of the new kind can answer, and inheriting the wrong answer is silent
 * in all three cases. */

#include <string.h>

#include "core/internal.h"

/* ---- has_atomic: H3's predicate, and the free discharge's own postcondition
 *
 * Read at EMISSION (src/gen/emit_vm.c), which is AFTER the discharge has run,
 * so it answers "is there a cut in the artifact" rather than "did the pattern
 * text contain one". That distinction is the whole payoff of running the
 * discharge before engine selection: `[^"]*+"` compiles to a pure DFA with the
 * MRL ceiling intact, and `(?>a|ab)c` is VM-forced with the ceiling off. */
bool pcrec_has_atomic(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_ATOMIC:
            return true;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        /* [M6.5.2] A backreference carries no subtree at all — `l` and `r` are
         * unused — so it can neither BE a cut nor CONTAIN one. */
        case A_BREF:
            return false;
        case A_CAP: case A_REP:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_has_atomic(a->r)) return true;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                if (pcrec_has_atomic(a->r)) return true;
                a = a->l;
            }
            continue;
        }
        return false;
    }
}

/* ---- stamped_by: "did THIS row's producer build anything here" ------------
 *
 * D65 derives a row's BUILT status by driving the row's own `syntax` through
 * the machinery that would compile it and reading the outcome. For the four
 * DOORWAY kinds that machinery is `doorway_route` + `doorway_call`, and the
 * outcome is an `ExtResult` (src/parse/syntax_dump.c). RK_QUANTSUFFIX reaches
 * no doorway at all — the possessive suffix is a quantifier suffix recognised
 * inside `p_rep`, deliberately — so its rows need a second arm, and this is the
 * signal that arm reads.
 *
 * IT IS THE SR-8 STAMP, NOT A SECOND FACT. `Ast.reg` is written by the
 * producer at construction and by nothing else, so "the row's producer ran" and
 * "a node carries the row" are the same statement. That is what makes the
 * DEFECT verdict reachable rather than decorative: a row whose `syntax` does
 * not actually exercise its own construct parses fine and stamps nothing, and
 * the derivation says DEFECT instead of quietly reporting `built`.
 *
 * Generic in the row, not special-cased to `atomic-groups`: the next
 * non-doorway kind gets this arm for free. */
bool pcrec_ast_stamped_by(const Ast *a, const RegRow *row)
{
    for (;;) {
        if (a->reg == row) return true;
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        /* [M6.5.2] no subtree; the `a->reg == row` test at the top of the loop
         * has already answered for the node itself. */
        case A_BREF:
            return false;
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_ast_stamped_by(a->r, row)) return true;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                if (pcrec_ast_stamped_by(a->r, row)) return true;
                a = a->l;
            }
            continue;
        }
        return false;
    }
}

/* ---- the FREE DISCHARGE (design §5.3) -----------------------------------
 *
 * Delete every `A_ATOMIC` whose cut is PROVABLY A NO-OP, splicing its body
 * back in. The condition is possessify's own §2.2 verdict, and that is exactly
 * right rather than convenient: the verdict's entire content is *"no retreat
 * into this loop can produce a match the preferred path does not"*, which is
 * precisely *"the cut deletes nothing"*.
 *
 * IT SHIPS FOR THE `A_ATOMIC(A_REP(X))` ARM ONLY — the possessive spellings —
 * because that is the arm with EVIDENCE: 0 violations over 532 positive-verdict
 * patterns x 16 subjects, with four controls that fire independently
 * (`atomic_groups_measurements/out/free_discharge.txt`). The plain-group
 * `(?>X)` arm is DEFERRED at ZERO measured cells (R31 E7): the probe reads the
 * verdict off the non-possessive twin's `RX_VM_STRATS`, which requires a
 * QUANTIFIER, so nothing was ever measured about it; and it would need a
 * callable (U1)/(U2) predicate over an ARBITRARY SUBTREE, which is strictly
 * more than the one-`A_REP` verdict possessify.c exposes. `[ENG-CUT]` subsumes
 * it.
 *
 * WHY IT IS WORTH HAVING. It is what makes the `engines` column's per-PATTERN
 * split real: `--engine=dfa '[^"]*+"'` SUCCEEDS (the node is gone before SR-8's
 * consultation runs, so nothing forces the VM and the artifact is a pure DFA)
 * while `--engine=dfa '(?>a|ab)c'` REFUSES by name. A user who writes a
 * possessive for SPEED gets what they asked for; a user who writes one that
 * changes the LANGUAGE gets told so. 532 of 1,764 generated possessive
 * patterns (30.2%) are inside it, and the canonical idiom family — `[^"]*+"`,
 * `a*+b`, `a++c` — is entirely inside it.
 *
 * THE VERDICT IS ASKED WITH THE GROUP'S OWN FOLLOW, i.e. TRANSPARENTLY, and
 * that is a different question from the one the MARKING walk asks about the
 * same node. `(?>a*)a` is NOMATCH on "aaa" while `a*a` is (0,3), so the
 * discharge must refuse it — and only the transparent reading (follow = {a},
 * FIRST(a) = {a}, not disjoint, verdict FALSE) does. src/opt/possessify.c's
 * `A_ATOMIC` arm answers both and says why.
 *
 * D67 CONTRACT NOTE 3 HOLDS BY CONSTRUCTION: this is a DELETION. The nodes
 * that survive are the body's own and keep their own `Ast.reg` stamps (a `\K`
 * inside a discharged group must keep forcing the VM), and no NEW node is born
 * to inherit the discharged one's. Sabotage row S97 makes the output inherit
 * it and the engine-selection assertion goes red.
 *
 * EMISSION-NEUTRAL ON THE VM PATH, and that is a checkable claim rather than a
 * hope: if the discharge fires, possessify's own fixpoint re-derives the
 * identical verdict on the same quantifier and re-marks it, so the emitted VM
 * code is byte-identical whether or not the discharge ran. The discharge
 * changes ENGINE SELECTION and nothing else. THE ONE CARVE-OUT is
 * `-fno-possessify`: with that flag `run_possessify` does not run while this
 * pass still does, so a DISCHARGED `a*+` emits a plain backtracking loop where
 * the undischarged one emits a cut. Not a correctness problem — the
 * discharge's own verdict says the two lower to the same answers — but it is
 * why §11.3's rule 2 is scoped to an UNDISCHARGED possessive. */

/* THE SET HOLDS `A_ATOMIC` NODES, not the `A_REP`s under them: the verdict is
 * asked about a GROUP, with that group's own follow, and two nested groups over
 * one quantifier ask two different questions. See possessify.c's `A_ATOMIC` arm
 * for the measured cell (`(?>a*+)a`) that says why. */
typedef struct {
    Ast **hit;      /* A_ATOMIC nodes whose cut is a PROVED no-op, arena-owned */
    int   n, cap;
    Ctx  *cx;
} DischargeSet;

static void ds_add(void *user, Ast *grp)
{
    DischargeSet *d = user;
    if (d->n == d->cap) {
        int ncap = d->cap ? d->cap * 2 : 16;
        Ast **nv = arena_alloc(&d->cx->arena, (size_t)ncap * sizeof *nv);
        if (d->n) memcpy(nv, d->hit, (size_t)d->n * sizeof *nv);
        d->hit = nv;
        d->cap = ncap;
    }
    d->hit[d->n++] = grp;
}

static bool ds_has(const DischargeSet *d, const Ast *grp)
{
    for (int i = 0; i < d->n; i++) if (d->hit[i] == grp) return true;
    return false;
}

/* The rewrite. Returns the (possibly replaced) node.
 *
 * Recursion discipline as everywhere else in this file: spines iteratively,
 * items recursively. `A_CAT`/`A_ALT` are rebuilt IN PLACE — these nodes are
 * this compile's own arena memory, nothing else holds a pointer to them, and
 * an out-of-place rebuild would allocate a second tree for a pass that changes
 * a handful of nodes. */
static Ast *dis_walk(DischargeSet *d, Ast *a)
{
    switch (a->k) {
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
    /* [M6.5.2] TRANSPARENT to nothing and containing nothing: a backreference
     * has no body for a cut to hide in. */
    case A_BREF:
        return a;
    case A_CAP: case A_REP:
        a->l = dis_walk(d, a->l);
        return a;
    case A_CAT: case A_ALT: {
        /* The left-nested spine, walked iteratively — it is as long as the
         * pattern, and D10/DD-10/R1 R-2 (and K20, three times) say a walk that
         * recurses on it segfaults pcrec on a 20,000-character literal. The
         * recursion that REMAINS is into a spine element's RIGHT child and into
         * the spine's HEAD, whose depth the parser's group-nesting cap bounds.
         *
         * REWRITTEN IN PLACE: these nodes are this compile's own arena memory,
         * nothing else holds a pointer to them, and an out-of-place rebuild
         * would allocate a second tree for a pass that changes a handful of
         * nodes. */
        Ast *t = a;
        for (;;) {
            t->r = dis_walk(d, t->r);
            if (t->l->k != a->k) { t->l = dis_walk(d, t->l); break; }
            t = t->l;
        }
        return a;
    }
    case A_ATOMIC:
        a->l = dis_walk(d, a->l);
        /* THE DISCHARGE ITSELF: splicing the BODY in is the whole rewrite —
         * the `A_ATOMIC` node is dropped, not copied, so nothing inherits its
         * stamp (D67 note 3) and the body's own nodes keep theirs.
         *
         * The `A_REP` re-test is not redundant with the survey's: the survey
         * only ever reports a group whose child was an `A_REP` WHEN IT RAN, and
         * the descent above cannot turn an `A_REP` into anything else (it
         * rewrites a repeat's child, never the repeat), so this holds — and it
         * is written out because the splice below reads `a->l` as the
         * replacement and a future rewrite that broke the invariant would
         * otherwise splice something unexamined. */
        if (ds_has(d, a) && a->l->k == A_REP) return a->l;
        return a;
    }
    return a;
}

Ast *pcrec_discharge_atomic(Ctx *cx, Ast *root)
{
    /* THE FAST PATH IS THE COMMON ONE and it is not an optimisation: a pattern
     * with no cut must not have possessify's survey run over it at all, or
     * every compile in the tree pays for a module it does not use. That is
     * also what keeps §11.1's identity claim true for an atomic-free pattern
     * by CONSTRUCTION rather than by the survey happening to change nothing. */
    if (!pcrec_has_atomic(root)) return root;

    /* [M6.4.2] D46's controllability half, and `-fno-possessify`'s DENY shape.
     * See lib/pcrec.h for why this is its OWN flag rather than a clause on
     * that one: this denial changes which ENGINE a pattern gets, and an
     * optimisation flag must not. */
    if (cx->opt && (cx->opt->flags & PCREC_NO_ATOMIC_DISCHARGE)) return root;

    DischargeSet d;
    memset(&d, 0, sizeof d);
    d.cx = cx;
    pcrec_poss_survey(cx, root, ds_add, &d);
    return dis_walk(&d, root);
}

/* ---- [M6.5.2] the two BACKREFERENCE tree predicates ----------------------
 *
 * They live here, beside `pcrec_has_atomic` and `pcrec_ast_stamped_by`, for
 * the reason this file's header gives: three switches over `AKind` with NO
 * `default:` arm, so a node kind added later is a compile error at each of
 * them rather than a silent inheritance. These two make it five.
 *
 * BOTH ARE ASKED OF THE POST-DISCHARGE TREE, exactly as `pcrec_has_atomic`
 * is. Nothing discharges a backreference today — §6.3 measured the
 * finite-language expansion and DECLINED to ship it, because its only possible
 * customer is a `--no-captures` build and the size boundary is a source-size
 * judgement no corpus exists to make yet — but asking the tree rather than a
 * parse-time counter is what keeps that a decision about scope instead of an
 * assumption baked into two call sites. */

/* §7.1's predicate: does anything here compare subject text to subject text? */
bool pcrec_has_bref(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_BREF:
            return true;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
            return false;
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_has_bref(a->r)) return true;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                if (pcrec_has_bref(a->r)) return true;
                a = a->l;
            }
            continue;
        }
        return false;
    }
}

/* §3.2.4's MARKED SET: the UNION of every `A_BREF`'s `refs`.
 *
 * EVERY MEMBER OF A DUPLICATED NAME'S RUN, not merely the one a given match
 * resolves to (R32 re-check E13). §8.3's chain reads each member's pair at
 * MATCH time until it finds a published one, so an unmarked member is read
 * under write-on-traverse and re-admits E1 through it — and the measured cell
 * is not a corner: `(?J)^(?:(?<a>q))?(?:(?<a>a|b\k<a>))+$` on "aba" is (0,3)
 * with group 1 UNSET and group 2 = (1,3), so the chain falls through the unset
 * FIRST member to the second, which is the one being RE-ENTERED. There is no
 * statically resolved member to mark.
 *
 * A number out of `mark`'s range is ignored rather than clamped: `nmark` is
 * `ncap + 1` and resolution already refused every reference above it, so an
 * out-of-range entry cannot exist — and if one ever could, writing past the
 * array is the failure this guard makes impossible instead of unlikely. */
void pcrec_bref_mark(const Ast *a, bool *mark, int nmark)
{
    for (;;) {
        switch (a->k) {
        case A_BREF:
            for (int i = 0; i < a->nrefs; i++)
                if (a->refs[i] > 0 && a->refs[i] < nmark) mark[a->refs[i]] = true;
            return;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
            return;
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                pcrec_bref_mark(a->r, mark, nmark);
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                pcrec_bref_mark(a->r, mark, nmark);
                a = a->l;
            }
            continue;
        }
        return;
    }
}
