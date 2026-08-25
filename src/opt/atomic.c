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
 * plus the two [M6.5.2] backreference walks below, [DD-14]'s
 * `pcrec_has_call` at the end of the file (module `recursion`, placed here on
 * the same argument), and — since [M6.6.2] —
 * `pcrec_has_lookaround`, which is placed HERE and not in a lookaround file
 * because it is `pcrec_has_atomic`'s twin in every respect that matters: same
 * shape, same post-discharge reading, same single consumer (`Vm.mrl_win`), and
 * the two are read in ONE expression at that consumer. A predicate whose only
 * job is to sit beside another one in a boolean AND belongs beside it.
 *
 * RECURSION DISCIPLINE (D10/DD-10/R1 R-2, and K20 the third time): `A_CAT` and
 * `A_ALT` spines are LEFT-NESTED and as long as the pattern, so every walk
 * below descends a spine ITERATIVELY and recurses only into the items hanging
 * off it, whose depth the parser's group-nesting cap bounds. A
 * 20,000-character pattern segfaulted pcrec once already for want of this.
 *
 * NONE OF THE SEVEN SWITCHES IN THIS FILE CARRIES A `default:` — mrl.c:18-24's
 * rule. A node kind added after this file is written must be a COMPILE ERROR
 * at each of them, because "can this construct contain a cut", "can it carry a
 * producer's stamp" and "is it transparent to the discharge" are questions
 * only the author of the new kind can answer, and inheriting the wrong answer
 * is silent in every case. [DD-14] adds one more that the alarm cannot state
 * on its own: every one of these walks is a WHOLE-TREE walk, so none of them
 * may follow `Ast.u.call.body` — the AST's first back edge — and each
 * `A_CALL` arm below says why declining it is not merely safe but exact. */

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
        /* [M6.6.2] DESCENDS INTO THE BODY. A cut inside a lookaround body is
         * still a cut in the tree — `(?=(?>a|ab))b` carries one — and this
         * predicate's question is "is there a cut in the ARTIFACT", not "is
         * there one on the outer path". Answering false would drop the MRL
         * window ceiling's exclusion for a pattern that still has a cut in it,
         * which is design §4's measured silent match loss reached through a
         * new door. */
        case A_LOOK:
        case A_CAP: case A_REP:
            a = a->l;
            continue;
        /* [DD-14] DECLINES, and the decline is the WHOLE-TREE RULE (design
         * §4.4), not a shrug. A call has no children: `l` and `r` are unused
         * and the callee hangs off `u.call.body`, which is a BACK EDGE. This
         * predicate walks the whole tree, so it ALREADY VISITS the callee at
         * the callee's own lexical position — `(?>a)` inside group 1 is found
         * when the walk reaches group 1, whether or not `(?1)` is followed —
         * which makes following `.body` redundant. And it is worse than
         * redundant: on `((?>a)(?1))` this bare `const Ast *` walker has no
         * visited set, so it would recurse for ever and HANG THE COMPILER, in
         * a predicate asked of EVERY pattern. No answer-comparison test can
         * detect a non-terminating compile, because there is no answer.
         *
         * The `A_CALL` NODE ITSELF is not a cut and cannot be one, so `false`
         * is what the node contributes. SABOTAGE ROW S-SR11 IS THIS ARM'S:
         * it makes this very case DESCEND into `.body`, and its predicted
         * result is that THE COMPILER HANGS on `(a(?1))` — no answer to
         * compare, so no answer-comparison test can score it, which is why
         * the row's suite is the TIMEOUT one. */
        case A_CALL:
            return false;
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

/* ---- has_lookaround: §5.6's predicate, and it is has_atomic's twin --------
 *
 * [M6.6.2] Does this tree carry an `A_LOOK`? Read at EMISSION, AFTER the
 * discharge, for the reason `pcrec_has_atomic` is read there and design
 * §5.6(4) states: if a future pass ever deletes a provably vacuous lookaround
 * (§5.7's territory, and NOT `pcrec_discharge_atomic`'s — see its A_LOOK arm),
 * the pattern should get its MRL window ceiling back. Asking the tree rather
 * than a parse-time counter is what keeps that a decision about scope instead
 * of an assumption baked into a call site.
 *
 * WHY THE PREDICATE IS FLAT rather than shaped. §5.4 shows the prefilter
 * hazard needs a lookaround INSIDE AN ALTERNATION, so this could have asked
 * for that shape instead of for any lookaround. Design §5.6 names and rejects
 * that: a shape condition is a second analysis with no independent check, the
 * atomic precedent is a flat predicate, and the measured cost of flat is that
 * a pattern loses a pruning ceiling it would rarely have had — against a
 * SILENT MATCH LOSS if the shape analysis is wrong anywhere.
 *
 * ITS CONSUMER IS `Vm.mrl_win` (src/gen/emit_vm.c), in the same expression as
 * `pcrec_has_atomic` and at the same point in the pipeline. Design §5.6(3) is
 * the part an editor must carry: the flag is not the only thing that has to
 * change, because the lines that BUILD the ceiling are gated separately, and
 * codegen rule 1 asserts on both sources. Sabotage rows S-LA12 and S-LA13. */
bool pcrec_has_lookaround(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_LOOK:
            return true;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        /* no subtree at all — `l` and `r` are unused on a backreference. */
        case A_BREF:
            return false;
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        /* [DD-14] DECLINES, `pcrec_has_atomic`'s whole-tree argument verbatim
         * (design §4.4): a lookaround inside the callee is found at the
         * callee's lexical position, and following `.body` would hang the
         * compiler on `((?=a)(?1))`. NOT IN §4.4a's TABLE — this site did not
         * exist when the design censused the tree at eacac76; it is
         * `lookaround` wave A2's own addition and it takes the same verdict as
         * its twin one function up. */
        case A_CALL:
            return false;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_has_lookaround(a->r)) return true;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                if (pcrec_has_lookaround(a->r)) return true;
                a = a->l;
            }
            continue;
        }
        /* No default arm — this file's header rule. A kind added later must be
         * a compile error here, because "can this construct CONTAIN a
         * lookaround" is a question only its author can answer, and inheriting
         * "no" leaves a live window ceiling on an artifact that has one. */
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
        /* [M6.6.2] DESCENDS, generically: this walk is not about lookaround at
         * all, it asks whether ANY row's producer built anything anywhere in
         * the tree, and a node built inside a lookaround body is still a node
         * this row's producer built. The `a->reg == row` test at the top of
         * the loop has already answered for the A_LOOK node itself. */
        case A_LOOK:
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        /* [DD-14] DECLINES — and here the decline costs NOTHING AT ALL, which
         * is worth saying because this walk descends generically everywhere
         * else. The `a->reg == row` test at the TOP of the loop has already
         * answered for the `A_CALL` node itself, which is the node this row's
         * producer (the `recursion` ports) actually built; every node in the
         * callee carries its OWN stamp and is visited at the callee's own
         * lexical position by this same whole-tree walk. Following `.body`
         * would find nothing new and would hang on `(a(?1))` (design §4.4). */
        case A_CALL:
            return false;
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
    /* [M6.6.2] DESCENDS INTO THE BODY, and the A_LOOK node itself is never
     * touched. Two halves, and they are different decisions:
     *
     * DESCENDING is right because the discharge is about A_ATOMIC nodes, and a
     * dead cut inside a lookaround body is as dead as one anywhere else. The
     * discharge is a DELETION that splices a body in, so what it does inside
     * the lookaround body cannot change the body's own sub-program contract:
     * §5.3's verdict is "the cut deletes nothing", and a rewrite that deletes
     * nothing cannot change what the body matches, which is the only thing the
     * enclosing assertion reads.
     *
     * NOT DELETING THE A_LOOK is the other half, and design §5.7 is why it is
     * written down rather than assumed. A future pass MAY delete a provably
     * vacuous lookaround (§5.6(4) is built on that possibility — it is why
     * `pcrec_has_lookaround` is asked of the POST-discharge tree). This pass is
     * not that pass: its whole verdict machinery is possessify's §2.2 answer
     * about an A_REP, which says nothing about whether an assertion is
     * vacuous. Inventing a lookaround deletion here would be a second,
     * unmeasured rewrite riding a verdict computed for a different question. */
    case A_LOOK:
    case A_CAP: case A_REP:
        a->l = dis_walk(d, a->l);
        return a;
    /* [DD-14] LEXICAL ONLY (design §4.4a site 11): the node is visited AS
     * ITSELF and `u.call.body` is never followed. This is a tree REWRITE, so
     * the reason is sharper than the predicates' one above — following the
     * back edge would DISCHARGE THE CALLEE TWICE, once at its lexical
     * position and once through every call that names it, and `dis_walk`
     * rewrites A_CAT/A_ALT spines IN PLACE. On a recursive callee it would
     * not terminate at all.
     *
     * There is nothing to descend INTO: an `A_CALL` has no `l` and no `r`.
     * Returning the node unchanged is the complete arm, and it is correct
     * because a call is not an `A_ATOMIC` and contains none — the cuts that
     * live in the callee are discharged when the walk reaches the callee.
     *
     * RE-CHECKED AGAINST THE `{0,0}` PRUNE (design §4.4c): this walk descends
     * `A_REP` UNCONDITIONALLY — it has no `rmin == 0 && rmax == 0` guard at
     * all — so a callee defined inside `(?:...){0}`, which §4.4c measured is
     * a real idiom, is still reached and still discharged. That is a property
     * of the code, not of pass ORDER. */
    case A_CALL:
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
        /* [M6.6.2] DESCENDS. A backreference inside a lookaround body compares
         * subject text to subject text exactly as one anywhere else does —
         * `(?=(a)\1)` is a real pattern — and §7.1's consequence (a
         * backref-bearing pattern gets NO prefilter) has to follow it in
         * there. Answering false would hand such a pattern a prefilter built
         * from an approximation that is not even a sound superset. */
        case A_LOOK:
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        /* [DD-14] DECLINES, the whole-tree rule again (design §4.4). A
         * backreference inside the callee is found at the callee's lexical
         * position — `(a(b)\2)(?1)` carries its `\2` in group 1's own
         * subtree — so following `.body` would add nothing and would hang on
         * `((b)\2(?1))`. The `A_CALL` node itself compares no subject text to
         * subject text: it RE-RUNS a pattern, which is §2.1's whole
         * discriminator between this construct and `A_BREF`.
         *
         * §7.1's consequence still reaches a call-bearing pattern, by a
         * DIFFERENT route: design §8.2 measured that the capture-erased
         * prefilter approximation is not a sound superset for a call either,
         * so wave E forces `EngineFit.prefilter` false through
         * `src/opt/select_engine.c`, not through this predicate. */
        case A_CALL:
            return false;
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
            for (int i = 0; i < a->u.bref.nrefs; i++)
                if (a->u.bref.refs[i] > 0 && a->u.bref.refs[i] < nmark) mark[a->u.bref.refs[i]] = true;
            return;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
            return;
        /* [M6.6.2] DESCENDS, for `pcrec_has_bref`'s reason: the marked set is
         * the UNION of every A_BREF's `refs` over the WHOLE tree, and a
         * reference the mark missed is read under write-on-traverse — E1
         * re-admitted through a lookaround body. */
        case A_LOOK:
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        /* [DD-14] MARKS `u.call.target` AND DESCENDS NOWHERE (design §4.3).
         * THE ONE ARM IN THIS FILE THAT IS NOT A DECLINE, and it is the arm
         * §4.3 measured the need for: `--no-captures` deletes the `A_CAP`
         * wrapper of every group nothing references (P10, 9 mentions vs 0),
         * and A CALL NAMES A GROUP EXACTLY AS A REFERENCE DOES — so without
         * this line `(a)(?1)` under `--no-captures` loses group 1 and the
         * call has no body at all.
         *
         * THE MARK IS NOT TRANSITIVE AND NEEDS NO FIXPOINT, which is the
         * cheaper half of §4.4's back-edge finding: if group 1's body calls
         * group 3, that call is an `A_CALL` NODE IN THE TREE, so this
         * whole-tree walk reaches it at its own lexical position and marks 3
         * directly. §4.3's first version made the marking transitive over the
         * call graph and that clause is WITHDRAWN.
         *
         * `target == 0` MARKS NOTHING — the root is not an `A_CAP` and is
         * never deleted (§2.4) — and the `> 0` half of the guard is what says
         * so. The `< nmark` half is `A_BREF`'s own convention one arm up,
         * kept for the same measured reason: wave B+C's resolver refuses
         * every call to a group that does not exist (the error-115 class,
         * §4.2), so an out-of-range target cannot arrive here — and if one
         * ever could, writing past the array is the failure this guard makes
         * impossible instead of unlikely. There is no `Ctx` in this
         * signature to fail loudly through; the guard is the file's
         * established answer to that.
         *
         * TWO SABOTAGE ROWS OWN THIS ARM, and they are not the same row:
         * S-SR10 drops `A_CALL.target` from the union (detected on the
         * `--no-captures` axis ONLY — `(a)(?1)` loses group 1's slots), and
         * S-SR11a deletes the `mark[target] = true` line to defend the
         * TWO-HOP case (`(a(?3))(b)((c))` under `--no-captures`), which is
         * the cell that shows the mark reaching group 3 through the call
         * NODE rather than through a transitive walk. */
        case A_CALL:
            if (a->u.call.target > 0 && a->u.call.target < nmark)
                mark[a->u.call.target] = true;
            return;
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

/* ---- [DD-14] does this tree carry a SUBROUTINE CALL? ---------------------
 *
 * `pcrec_has_bref`'s sibling, placed here for this file's standing reason
 * (design §4.3, and `lookaround_design.md` §11 wave A2 put
 * `pcrec_has_lookaround` here on the same argument): the tree predicates live
 * together, in switches with NO `default:`, so a node kind added later is a
 * compile error at each of them rather than a silent inheritance. These six
 * make seven.
 *
 * ASKED OF THE POST-DISCHARGE TREE, exactly as its three neighbours are.
 * Nothing discharges an `A_CALL` today and nothing is planned to — but the
 * SPLICE linkage (design §6.3, wave G) is a rewrite that REPLACES a call with
 * a copy of its callee, and if it ever runs before this predicate's consumer,
 * asking the tree rather than a parse-time counter is what makes "a spliced
 * pattern has no call left in it" a true answer instead of a stale one.
 *
 * IT DECLINES `u.call.body` LIKE EVERY OTHER WHOLE-TREE PREDICATE HERE
 * (design §4.4) — and the decline is FREE for this one in a way it is not for
 * the others: the arm it needs is `return true`, so it stops at the first
 * call and never has anywhere to descend to.
 *
 * NO CALL SITE YET. Wave E wires it as `&& !pcrec_has_call(root)` (§8.2's
 * prefilter forcing, in `src/opt/select_engine.c`), which is the wave with a
 * producer and therefore the first wave in which it can answer anything but
 * false; SABOTAGE ROW S-SR17 deletes that conjunct once it exists, so adding
 * it now would pre-satisfy its own detector. It is EXTERNAL
 * rather than static for exactly that reason: an unused static is a
 * `-Wunused-function` error under `make strict`, and adding a fake call site
 * to silence it would pre-satisfy the sabotage row that owns the real one. */
/* ---- [DD-14 wave G] IS ANY CAPTURE GROUP LIVE? (design §3.1, §8.3) -------
 *
 * A capture group is DEAD when NO EMITTED CODE CAN WRITE IT, and this walk
 * asks exactly that, over one structural fact and no construct's name.
 *
 * THE FACT: `X{0}` EMITS NOTHING. The emitter writes "X{0}: matches empty, no
 * code" and `vm_count_slots` counts nothing for it, so a group whose only
 * lexical occurrence lies under an `A_REP` with `rmax == 0` has no instruction
 * anywhere that assigns its slot pair. That is not a heuristic and not a
 * language claim — it is the emitter's own rule, read back.
 *
 * AND A CALL DOES NOT REVIVE IT, which is the half the design had to MEASURE
 * (§3.1, `out/captures.txt` C2, through a `pcre2_set_callout` reading the LIVE
 * ovector): the callee WRITES its capture slots and the RETURN puts the
 * caller's values back. "A subroutine call is CAPTURE-TRANSPARENT — the
 * capture state after the call is exactly the state before it, whatever the
 * call did." So a group reached ONLY through calls can never leave a VISIBLE
 * capture either, and this walk's `A_CALL` arm is a decline for a REASON
 * rather than for design §4.4's usual one. (§4.4's reason applies as well: the
 * callee is a subtree of this tree at its own lexical position, so a group
 * that IS live in the callee is found there.)
 *
 * IT IS NOT A `DEFINE` RULE, and that is deliberate. `(?(DEFINE)...)` lowers
 * to `A_REP{0,0}` (src/parse/mod_recursion.c), the `(?:...){0}` idiom lowers
 * to the same node, and `(a){0}b` — which names no module at all — is the same
 * fact a third time. One predicate covers all three because they are one
 * structural situation; a `DEFINE`-shaped special case would have been a
 * parallel mechanism for two thirds of its own population.
 *
 * WHAT IT IS FOR: `src/opt/select_engine.c`'s `forces_captures`. A pattern
 * whose every group is dead promises capture pairs that NO MATCH CAN SET, so
 * it does not need the capture-recording engine — the DFA can promise the same
 * permanently-unset pairs (see `dfa_artifact_ncaps`). PCRE2 agrees about what
 * is promised: MEASURED on 10.46, `(?(DEFINE)(?<g>a))(?&g)` has CAPTURECOUNT 1
 * and answers g1 UNSET, and `(?(DEFINE)(?<g>a))(x)(?&g)` has CAPTURECOUNT 2
 * with g1 UNSET and g2 SET — so the numbering a user sees does not shift and
 * the dead entry does not disappear.
 *
 * THE POLARITY IS NAMED FOR THE SAFE ANSWER. `true` ("something is live")
 * keeps the VM, which is what every capture-bearing pattern gets today, so a
 * walk that over-reports costs an engine and never a wrong span. A walk that
 * UNDER-reports puts a writable group on an engine that cannot record it,
 * which is a lost capture — the failure the sabotage row over this function
 * plants, and the reason the `A_REP` test below is `rmax == 0` exactly and not
 * "a small maximum". */
bool pcrec_has_live_capture(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_CAP:
            return true;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF:
        /* CAPTURE-TRANSPARENT (§3.1), and no descent — see the header. */
        case A_CALL:
            return false;
        case A_REP:
            /* THE ONE ARM THAT PRUNES. Zero repetitions emit no code, so
             * nothing below can be written.
             *
             * SPELLED `rmin == 0 && rmax == 0` TO MATCH `vm_count_slots`'
             * GUARD EXACTLY (src/gen/emit_vm.c's `A_REP` arm), because these
             * two are ONE predicate — "does this repeat emit anything" — asked
             * by two passes, and two spellings of one question are two chances
             * to disagree. They cannot today (`rmax == 0` implies `rmin == 0`;
             * the parser refuses `{2,0}`), which is precisely why the
             * divergence would be silent if a future construct ever produced
             * the pair some other way. */
            if (a->u.rep.rmin == 0 && a->u.rep.rmax == 0) return false;
            a = a->l;
            continue;
        case A_LOOK:
        /* A LOOKAROUND BODY'S GROUPS ARE LIVE. MEASURED on 10.46:
         * `(?=(a))a` on "a" answers g1 = (0,1) — an assertion that SUCCEEDS
         * leaves its captures set — so its body is walked like any other. */
        case A_ATOMIC:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_has_live_capture(a->r)) return true;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                if (pcrec_has_live_capture(a->r)) return true;
                a = a->l;
            }
            continue;
        }
        /* No default arm — this file's header rule. */
        return false;
    }
}

/* ---- [DD-14 wave G] does this tree carry a LINKED (non-spliced) call? ----
 *
 * `pcrec_has_call`'s NARROWING, and the narrowing is the whole of wave G's
 * engine story. §8.1 marks every `recursion` registry row VM_ONLY on a
 * structural argument — `^(a(?1)?b)$` generates a^n b^n, which is not regular
 * — and §8.2 forces the prefilter off on the argument that erasing a call
 * gives a DIFFERENT language, not a bigger one. BOTH arguments are about a
 * call whose callee has no finite inlining. A SPLICED call (design §6.3: the
 * callee is not in a cycle and the expansion fits the budget) has one, it is
 * EXACT, and `src/ir/nfa.c`'s `A_CALL` arm builds it — so a pattern all of
 * whose calls splice is exactly as regular as the pattern with the calls
 * written out by hand, which is what §8.3 MEASURED when 8 of its 15 inlined
 * equivalents compiled to pcrec's pure DFA.
 *
 * SO THE QUESTION IS NOT "IS THERE A CALL" BUT "IS THERE ONE THAT IS STILL A
 * JUMP", and this predicate asks that one. It reads `u.call.link`, so it is
 * only meaningful AFTER `pcrec_callgraph_build` — which is why that pass moved
 * ahead of `pcrec_select_engine` (see src/core/compile.c). Before the graph
 * runs, every node still carries the arena's `CALL_SPLICE`, which would be the
 * UNSOUND answer here; there is no caller in that window and there must not be
 * one, so this comment is the guard rather than an assertion the signature has
 * no `Ctx` to raise.
 *
 * IT DOES NOT FOLLOW `.body`, design §4.4's rule, and here that is exact
 * rather than conservative: a call nested inside a callee is an `A_CALL` NODE
 * in this tree at its own lexical position, so this whole-tree walk reaches it
 * anyway — and following the edge would hang the predicate on `(a(?1))`. */
bool pcrec_has_linked_call(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_CALL:
            return a->u.call.link != CALL_SPLICE;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF:
            return false;
        case A_LOOK:
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_has_linked_call(a->r)) return true;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                if (pcrec_has_linked_call(a->r)) return true;
                a = a->l;
            }
            continue;
        }
        /* No default arm — this file's header rule. */
        return false;
    }
}

bool pcrec_has_call(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_CALL:
            return true;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        /* no subtree at all — `l` and `r` are unused on a backreference. */
        case A_BREF:
            return false;
        case A_LOOK:
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_has_call(a->r)) return true;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                if (pcrec_has_call(a->r)) return true;
                a = a->l;
            }
            continue;
        }
        /* No default arm — this file's header rule. */
        return false;
    }
}
