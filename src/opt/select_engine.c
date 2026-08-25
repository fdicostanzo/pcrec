/* Per-pattern engine selection (docs/design/engine_m4.md §5).
 *
 * Before [M4.5b] this was one `if` inline in compile.c's driver, and it chose
 * between the two DFA SHAPES (ENG_UNANCH vs ENG_ATTEMPT) rather than between
 * ENGINES. §5.1 moves the engine question into a pass with a registered-
 * analysis SOCKET, for a reason worth restating because it is the design's
 * least obvious call: the socket's future customers (backrefs-finite
 * expansion, the atomic/possessive cut) are not analyses that RETURN a
 * verdict, they are REWRITES that DISCHARGE one — `(abc)\1` is VM-forced
 * until the finite-language expansion turns it into `abcabc`, at which point
 * it is DFA-compilable. So the pass is a FIXPOINT: analyse, offer each
 * registered `discharge` a chance, re-analyse, stop when nothing changes or
 * the bound is hit. It ships here with ZERO registered discharge hooks (§5.2:
 * "ship it in M4.6 with zero registered discharge hooks; the bound exists
 * from day one so a later rewrite pair cannot loop"), which is deliberate —
 * the bound is cheaper to write now than to retrofit around a rewrite.
 *
 * WHAT FORCES THE VM TODAY (§5.3's table, restricted to constructs that have
 * a producer): TWO rows — "capturing group with captures REQUESTED", and
 * `\K` ([M6.2] wave E).
 *
 * **THE PARAGRAPH THAT USED TO STAND HERE SAID "EXACTLY ONE ROW", AND ITS
 * REASON EXPIRED RATHER THAN BEING WRONG.** It ran: every other VM_ONLY row
 * in the registry is gated by a module with no producer (§9.1), so the parser
 * refuses those patterns long before selection runs and this pass can never
 * see one — which is also why SR-8's flip is smaller than its row implies
 * (ZERO currently-refused constructs become compilable when the VM exists).
 * Module `assertions` now HAS a producer and `\K` is its VM_ONLY row
 * (src/parse/registry.c), so the premise no longer holds and two other
 * statements in this file move with it: SR-8's flip has its first member, and
 * the `--engine=dfa` override's second branch below stops being empty by
 * population. Both are annotated where they are stated.
 *
 * [M4.7a]: SR-8's consuming socket is deliberately NOT built here yet — zero
 * producers means zero customers (D18/OS-0/D53's standing "earn its axis"
 * discipline). tests/registry/registry_check.c's check_engine_capability_
 * tripwire is what stands in for it: it asserts every VM_ONLY-masked
 * RS_MODULE row has no wired producer, so the day a module wires the first
 * one, THAT check fails and names this file as the thing to build before the
 * producer lands, not after. **IT FIRED ON `\K`, WHICH IS THE DAY IT WAS
 * WRITTEN FOR** — see that check for what wave E did to it, and why the
 * answer was to give it a NAMED, ARGUED exception rather than to delete it.
 *
 * THE TRIGGER IS THE REQUESTED OUTPUT, NOT THE PRESENCE OF A `(` (§5.3, the
 * correction to the freeze document's candidate (b)). `a(b|c)+d` compiled
 * with --no-captures is capture-free WORK and stays on the DFA forever; the
 * same pattern compiled by default (D42.1: captures ON) wants group offsets
 * and therefore needs an engine that can produce them.
 */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

/* §5.2's socket. One registered analysis today. `discharge` is the rewrite
 * half — NULL here, and the fixpoint below is written to run correctly with
 * every hook NULL, which is the state it ships in. */
typedef struct {
    const char *name;
    /* Does this construct force an engine, and where? Returns an ENGM_* mask
     * of the engines that can still compile the pattern. */
    unsigned  (*forces)(Ctx *cx, const Ast *a, size_t *why_pos,
                        const char **why);
    /* Optional: rewrite the AST so the forcing no longer applies. Returns
     * NULL to decline. Must be semantics-preserving. */
    Ast      *(*discharge)(Ctx *cx, Ast *a);
    /* [M6.4.2 / D67 contract note 1] IS THIS ROW NODE-DERIVED?
     *
     * Two kinds of forcing remain after SR-8 and the `--engine=dfa` override
     * has to tell them apart. `forces_captures` is REQUEST-derived — a
     * property of the generation REQUEST, with no registry row behind it —
     * and its refusal names `--no-captures`, which is a real way out because
     * the caller asked for captures merely by not passing the flag.
     * `forces_registry` is NODE-derived, and there is NO flag that makes a
     * `\K` or an atomic pattern DFA-compilable, so advising one is a lie.
     *
     * The defect this closes is live on the shipped compiler: `--engine=dfa
     * '(a)\Kb'` answers "this pattern requires captures (on by default); pass
     * --no-captures ..." — advice that does not help, because `\K` still
     * forces the VM after the captures are gone. */
    bool        node_derived;
} EngineAnalysis;

/* The fixpoint's bound. §5.2 asks for it "from day one so a later rewrite
 * pair cannot loop" — with no discharge hooks registered the loop provably
 * runs once, so this is structure for a customer that does not exist yet,
 * which is the whole point of building the socket now. */
enum { SELECT_MAX_ROUNDS = 8 };

/* ---- the one registered analysis: captures ---- */

/* engine_m4.md §5.3 row 1. Note what this does NOT look at: it does not walk
 * the AST hunting for A_CAP, it asks whether the artifact will PROMISE group
 * offsets. Those are the same set by construction — A_CAP nodes exist iff
 * cx->want_caps was true at parse time (parse.c's capturing-`(` hook) — but
 * asking the question the design's way keeps the trigger honest if a future
 * construct produces capture slots without an A_CAP node. */
static unsigned forces_captures(Ctx *cx, const Ast *a, size_t *why_pos,
                                const char **why)
{
    if (!cx->want_caps || cx->ncap == 0) return ENGM_DFA | ENGM_VM;
    /* [DD-14 wave G] THE DEAD-CAPTURE ELISION, and it is the one place this
     * row looks at the TREE.
     *
     * The paragraph above says this analysis deliberately does not hunt for
     * `A_CAP`, because the question is whether the artifact will PROMISE group
     * offsets. That is still the question and the answer has not changed: the
     * artifact promises them either way, and `dfa_artifact_ncaps` is what
     * makes the DFA able to. What this line adds is the second half nobody had
     * to ask while every promised group was writable — CAN A MATCH EVER SET
     * ONE? A group whose only occurrence sits under a zero-count repeat has no
     * emitted instruction that assigns it, and a subroutine call to it is
     * capture-transparent (§3.1, MEASURED through the live ovector), so the
     * honest value of every pair it promises is PERMANENTLY UNSET. An engine
     * that cannot record captures can promise that perfectly well.
     *
     * THIS IS THE SPECIMEN'S WHOLE STORY. The RFC 5322 email pattern factored
     * with `(?&name)` calls has four named definitions under `{0}`, all four
     * dead; without this line it forces the VM, and with the VM it loses the
     * prefilter (~23x on a no-`@` megabyte), the rungs (a STEPS give-up where
     * the DFA answers in 4 ms) and a frame per iteration. With it, and with
     * every call SPLICED, the pattern compiles to the same DFA the
     * hand-inlined original does.
     *
     * IT IS NOT GATED ON THERE BEING A CALL, and that costs something honest:
     * `(a){0}b` and `^(?(DEFINE)(?<w>x))a$` carry no call at all and move from
     * the VM to the DFA too. Gating would have made this a `recursion` special
     * case for a fact that is not about `recursion`. The identity gate names
     * the affected call-free patterns rather than filtering them. */
    if (!pcrec_has_live_capture(a)) return ENGM_DFA | ENGM_VM;
    *why_pos = cx->first_cap_pos;
    *why = "capture group";
    return ENGM_VM;
}

/* ---- SR-8: THE GENERIC ENGINE-CAPABILITY CONSULTATION ([M6.4.2], D67) ----
 *
 * ONE analysis over every module-produced node's own registry row, replacing
 * the per-construct `forces_kreset` that stood here.
 *
 * WHAT IT REPLACES AND WHY THE REPLACEMENT IS THE RIGHT SHAPE NOW. [M4.7a]
 * declined to build this on D18/OS-0/D53's earn-its-axis discipline: zero
 * VM_ONLY rows had producers, so a generic column consultation would have been
 * machinery designed at sample size zero. [M6.2] wave E wired the first (`\K`)
 * and answered it with a bespoke row plus a NAMED exception in
 * `tests/registry/registry_check.c`'s tripwire — and that tripwire's own text
 * said what to do next, in advance: *"If a SECOND construct arrives here, do
 * not add a second exception: two is when the generic consultation has earned
 * its axis and SR-8 is the right build."* `(?>` is the second. D67 rules the
 * build; this is it, in the shape D55 specified.
 *
 * THE MECHANISM, and every clause of it is load-bearing:
 *
 *   - A module's PRODUCER stamps each node it creates with the registry row it
 *     was dispatched on (`Ast.reg`, `pcrec_ast_stamp`). The row — not a copy of
 *     its `engines` mask, because a copied mask is a second home for a registry
 *     fact and because `why`'s text has to come from the row anyway.
 *   - This analysis ANDs `pcrec_ast_engines()` over the tree. An UNSTAMPED node
 *     contributes ANY_ENGINE, so a forgotten stamp fails in the UNSOUND
 *     direction ON PURPOSE (D67 contract note 2): what catches it is the
 *     generic tripwire — every VM_ONLY row with a producer must refuse
 *     `--engine=dfa` BY NAME — and not a lucky default. Sabotage row S96.
 *   - It runs over the POST-DISCHARGE tree, which is the whole reason it can
 *     be a per-ROW column at all while the answer is per-PATTERN. `(?>` is
 *     genuinely VM-only for `(?>a|ab)c` and genuinely not for `[^"]*+"`; the
 *     column cannot be made true by editing it (that is the first evidence it
 *     has ever had in BOTH directions), and `pcrec_discharge_atomic` DELETES
 *     the node before this runs, so the column stays a conservative per-row
 *     fact and the tree says the per-pattern answer.
 *
 * WHY IT WALKS THE TREE rather than reading a parse-time counter — the same
 * reason `forces_kreset` did, generalised: the socket exists for REWRITES that
 * DISCHARGE a forcing, and a counter would keep saying VM after one deleted the
 * node. `why_pos` still comes from `Ctx.first_vmonly_pos`, because no AST node
 * carries a source position; it is read only where the walk already found a
 * node.
 *
 * WHAT DOES *NOT* RETIRE INTO IT: `forces_captures` (D67 contract note 1). That
 * row is REQUEST-derived — a property of the generation request, with no
 * registry row behind it — so two kinds of forcing remain, request-derived and
 * NODE-derived, and the `--engine=dfa` branch below has to tell them apart. */

/* The first DFA-excluding node in walk order, or NULL. Returns the ROW because
 * that is what carries the `why` text (D67: "why_pos/why from the first
 * DFA-excluding node's row").
 *
 * Iterative on both spines, recursive only into a spine element's right child
 * and into a body — D10/DD-10's discipline, held the way possessify.c,
 * revdet.c and altcls.c hold it. A flat concatenation is allowed to be 20,000
 * elements long; the nesting depth is bounded by the parser's group cap. */
static const RegRow *first_dfa_excluding(const Ast *a)
{
    for (;;) {
        /* [DD-14 wave G] THE ONE NODE WHOSE ROW IS CONSERVATIVE AND WHOSE
         * PATTERN-LEVEL ANSWER IS A PASS COMPUTED FACT, and it is `(?>`'s
         * situation exactly, resolved by a different move for a structural
         * reason.
         *
         * D67's rule is that the `engines` column is a per-ROW fact that
         * "cannot be made true by editing it", and §8.1's argument for marking
         * every `recursion` row VM_ONLY is sound as a per-ROW fact: `(?1)` in
         * general names a callee that may be recursive, and `^(a(?1)?b)$`
         * generates a^n b^n, which is not regular. It is NOT the per-PATTERN
         * answer, and `(?>` is the precedent for that gap — genuinely VM-only
         * for `(?>a|ab)c`, genuinely not for `[^"]*+"`. `(?>`'s gap is closed
         * by `pcrec_discharge_atomic` DELETING the node before this walk runs,
         * so the column stays conservative and the TREE says the answer.
         *
         * A CALL CANNOT BE DELETED THE SAME WAY. Deleting it means copying the
         * callee's subtree into the tree at every site, which duplicates the
         * callee's `A_CAP` nodes — two occurrences of one group number, which
         * is `callgraph.c`'s "two programs for one group" hazard arriving by a
         * third route — and it would do it before the emitter has said whether
         * it wants the copy. So the gap is closed by the LINKAGE instead: a
         * `CALL_SPLICE` node is one whose callee `src/opt/callgraph.c` has
         * PROVED acyclic and small enough to inline, and `src/ir/nfa.c` builds
         * exactly that inlining. The fact is computed by a pass and read here,
         * which is the same shape as the discharge; what differs is that the
         * node survives, because the VM emitter still needs it.
         *
         * THE POLARITY IS THE SAFE ONE. Before `pcrec_callgraph_build` runs,
         * `link` is the arena's `CALL_SPLICE` — the UNSOUND value — so this
         * line is correct only because that pass now runs FIRST (src/core/
         * compile.c). A future reader who moves selection back ahead of the
         * graph gets a DFA artifact for a recursive pattern; the sabotage row
         * over this line is what says so. */
        if (a->k == A_CALL && a->u.call.link == CALL_SPLICE) return NULL;
        if (a->reg && !(a->reg->engines & ENGM_DFA)) return a->reg;
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        /* [M6.5.2] A LEAF, and its OWN stamp is what excludes the DFA — the
         * test at the top of this loop has already read it. There is no
         * subtree to descend into, which is why a backref-bearing pattern
         * needs no per-module analysis at all: its twelve registry rows are
         * VM_ONLY, their producer stamps every `A_BREF` it builds, and this
         * generic walk finds the first one. D67's whole point, and the reason
         * `analyses[]` gains no line for this module. */
        case A_BREF:
            return NULL;
        /* [M6.6.2] DESCENDS, and there is NO new predicate anywhere for this
         * module (design §5.1). SR-8 does the whole job through `Ast.reg`: the
         * six registry rows are VM_ONLY, their producer stamps every A_LOOK it
         * builds, and the `a->reg && !(a->reg->engines & ENGM_DFA)` test at
         * the top of this loop finds it — which is why `analyses[]` gains no
         * line, exactly as it gained none for backrefs.
         *
         * The DESCENT is the part that is not free. This switch's own comment
         * below says inheriting "no" is the silent wrong answer because it
         * would let a VM-only construct NESTED inside the new kind reach the
         * DFA — and a lookaround body is a place other modules' constructs
         * live. `(?=\K)` is refused by design §2.7, but `(?=(?>a))` is not,
         * and its A_ATOMIC has to be found. */
        case A_LOOK:
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        /* [DD-14] A LEAF, `A_BREF`'s arm exactly: its OWN stamp is what
         * excludes the DFA and the test at the top of this loop has already
         * read it. Every `recursion` row is VM_ONLY (design §8.1), the ports
         * stamp every `A_CALL` they build, and this generic walk finds the
         * first one — so `analyses[]` gains no line for this module either.
         *
         * NO DESCENT, and here that is exact rather than conservative. The
         * callee is a subtree of THIS tree at its own lexical position, so any
         * VM-only construct inside it is found by this same walk without the
         * back edge — which is the whole content of design §4.4's rule, and
         * following the edge would hang this predicate on `(a(?1))`, a
         * predicate asked of every pattern.
         *
         * WHAT THIS SITE DOES NOT DO is force the prefilter off. That is a
         * SEPARATE fact (design §8.2: the call-erased approximation is not a
         * sound superset, and §8.3 measured 21x-350x for the alternative), it
         * is `pcrec_has_call`'s consumer, and it is wave E's one line — not
         * this arm's. */
        case A_CALL:
            return NULL;
        case A_CAT:
            while (a->k == A_CAT) {
                const RegRow *r = first_dfa_excluding(a->r);
                if (r) return r;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                const RegRow *r = first_dfa_excluding(a->r);
                if (r) return r;
                a = a->l;
            }
            continue;
        }
        /* No `default:` — mrl.c:18-24's rule. A node kind added after this
         * file is written must be a COMPILE ERROR here, because "can this
         * construct carry a producer's stamp, and can it CONTAIN one" is a
         * question only the author of the new kind can answer, and inheriting
         * "no" is the silent wrong answer: it would let a VM-only construct
         * nested inside the new kind reach the DFA. */
        return NULL;
    }
}

static unsigned forces_registry(Ctx *cx, const Ast *a, size_t *why_pos,
                                const char **why)
{
    const RegRow *r = first_dfa_excluding(a);
    if (!r) return ENGM_DFA | ENGM_VM;
    *why_pos = cx->first_vmonly_pos == (size_t)-1 ? 0 : cx->first_vmonly_pos;
    /* THE TEXT IS THE ROW'S OWN `syntax`, which is what makes this generic
     * without inventing a per-construct sentence: it is the field whose whole
     * job is "how the construct is written", it is what `--list-syntax`
     * displays, and `\K`'s row spells it "\K" — so [M6.2] wave E's shipped
     * diagnostic ("\K requires the VM engine, which --engine=dfa excludes") is
     * reproduced BYTE FOR BYTE by the generic path that replaced its bespoke
     * analysis. That reproduction is D67's "same verdict, same position" made
     * checkable.
     *
     * ONE KIND IS DIFFERENT AND IT IS NOT AN EXCEPTION TO THE RULE, it is the
     * rule reading the field correctly. For a DOORWAY row the `syntax` IS the
     * construct (`(?>...)`, `\K`). For an RK_QUANTSUFFIX row it is an
     * EXAMPLE — a possessive suffix is not a pattern on its own, so the field
     * has to carry an atom (`a{1,2}+`), and printing it would name a spelling
     * the user did not write: `(?:a|ab){1,3}+c` would be explained as
     * "a{1,2}+". The four rows are ONE construct with four spellings, and this
     * is the noun parse.c's own module refusal already uses for it. */
    *why = r->kind == RK_QUANTSUFFIX ? "possessive quantifier" : r->syntax;
    return r->engines;
}

/* ORDER MATTERS ONLY FOR THE DIAGNOSTIC, and it is captures-first on purpose.
 * The pass ANDs every row's mask, so the verdict is order-independent; `why`
 * is taken from the FIRST row that excludes the DFA. A `\K` pattern that also
 * captures is therefore explained as "capture group at pattern offset N",
 * which is the reason a user can act on (`--no-captures` is a real option;
 * "do not write `\K`" is not). A capture-free `\K` pattern gets the `\K`
 * explanation, which is then the only one available and the right one. */
static const EngineAnalysis analyses[] = {
    { "captures", forces_captures, NULL, false },
    /* [M6.4.2] ONE row where `\K`'s was, and every future VM_ONLY module's
     * forcing falls out of its registry rows with no per-module analysis —
     * backrefs' twelve ([M6.5]) are the next customer and need no line here. */
    { "registry", forces_registry, NULL, true  },
};

/* ---- the pass ---- */

/* engine_why's text, arena-owned so it outlives this call and can be handed
 * straight to the emitter. §5.5's shape: "capture group at pattern offset 0". */
static const char *why_text(Ctx *cx, const char *what, size_t pos)
{
    char buf[128];
    int n = snprintf(buf, sizeof buf, "%s at pattern offset %zu", what, pos);
    if (n < 0) return what;
    size_t sz = (size_t)n + 1;
    if (sz > sizeof buf) sz = sizeof buf;
    char *p = arena_alloc(&cx->arena, sz);
    memcpy(p, buf, sz - 1);
    p[sz - 1] = 0;
    return p;
}

/* [ENG-BREP] The possessification REWRITE, driven to its fixpoint.
 *
 * WHY IT IS CALLED HERE AND NOT REGISTERED IN `discharge` ABOVE — a deliberate
 * deviation from eng_brep_design.md §2.8's literal reading, reported rather
 * than silently taken. §2.8 says possessification "is exactly that shape" (a
 * rewrite, not an analysis returning a verdict) and proposes it as an
 * `EngineAnalysis` row whose `discharge` rewrites the A_REP's strategy in
 * place. The SHAPE claim is right and this file keeps it. The REGISTRATION is
 * not available, for two reasons that only appear once the socket exists:
 *
 *   1. `discharge`'s contract is "rewrite the AST so the ENGINE FORCING no
 *      longer applies". Possessification cannot do that and must not claim to
 *      — a capture-bearing pattern still needs the VM after every one of its
 *      quantifiers is possessified. A hook that rewrites and never changes the
 *      mask would spin the fixpoint against a verdict it cannot move.
 *   2. The fixpoint only reaches `discharge` when the pattern is VM-FORCED, so
 *      registering there would possessify a capture-bearing pattern and SKIP a
 *      capture-free one compiled with `--engine=vm` — the same artifact kind,
 *      built by the same emitter, optimised differently for a reason nobody
 *      could see from the outside. That would also make the differential this
 *      row is validated by lie about its own coverage.
 *
 * So the driver is the CHOSEN engine, which is the honest condition: the mark
 * is read by src/gen/emit_vm.c and by nothing else, so a DFA artifact cannot
 * observe it and pays nothing for it. Capture-free patterns stay byte-identical
 * by construction rather than by audit, which is §5.4's gate held the way §7
 * predicts (613 of 756 corpus patterns never reach this line).
 *
 * The loop is the fixpoint §2.8 asks for, and possessification's own
 * monotonicity is what bounds it: `pcrec_possessify` returns how many
 * quantifiers it NEWLY marked, a marked quantifier is never unmarked, and a
 * second pass over a fully-marked tree returns 0. It therefore runs twice on
 * any pattern with a positive verdict and once otherwise. SELECT_MAX_ROUNDS
 * bounds it anyway, because a bound that depends on an argument in a comment
 * is not a bound. */
static void run_possessify(Ctx *cx, Ast *root, const EngineFit *fit)
{
    if (fit->chosen != ENGM_VM) return;
    if (cx->opt->flags & PCREC_NO_POSSESSIFY) return;
    for (int round = 0; round < SELECT_MAX_ROUNDS; round++)
        if (pcrec_possessify(cx, root) == 0) break;
}

/* [ENG-BREP] The ladder's SECOND rung, driven from the same place and under the
 * same two conditions, because the reasoning that put possessification here
 * (the honest driver is the CHOSEN ENGINE, not the `discharge` socket) applies
 * to it unchanged.
 *
 * It is NOT a fixpoint and does not need to be. Possessification is monotone
 * and iterated because marking one quantifier can change another's FOLLOW;
 * reverse-determinism is a property of the body's own shape and its nesting
 * alone, so one walk decides every quantifier and a second would mark nothing.
 *
 * ORDER: after possessification, not before. The two are independent — the
 * emitter treats possessification as a modifier at every rung — but running the
 * rung analysis second keeps the ladder's stated application order (D47.1:
 * possessify, then rung-select) visible in the code that drives it. */
static void run_revdet(Ctx *cx, Ast *root, const EngineFit *fit)
{
    if (fit->chosen != ENGM_VM) return;
    if (cx->opt->flags & PCREC_NO_REVDET) return;
    (void)pcrec_revdet(cx, root);
}

void pcrec_select_engine(Ctx *cx, Ast *root)
{
    EngineFit fit;
    memset(&fit, 0, sizeof fit);

    unsigned mask = ENGM_DFA | ENGM_VM;
    const char *why = NULL;
    size_t why_pos = 0;
    /* [M6.4.2 / D67 note 1] THE SECOND WHY: the first NODE-DERIVED exclusion,
     * recorded alongside the first exclusion of any kind. `RX_ENGINE_WHY`'s
     * first-row rule is UNCHANGED — the stamp still reads `why`, captures-first
     * — and this exists only so the `--engine=dfa` override can tell a
     * conflict a flag can resolve from one no flag can. */
    const char *node_why = NULL;
    size_t node_why_pos = 0;

    /* [M6.4.2] THE FREE DISCHARGE runs ONCE, before the analysis loop — NOT as
     * a registered `discharge` hook. src/opt/atomic.c's own header has the
     * three reasons, one of them measured: the fixpoint below never CALLS a
     * registered hook, so registering would run the analysis 8 times and
     * rewrite nothing. Running it first is what makes the consultation's
     * per-ROW column produce a per-PATTERN answer — `--engine=dfa '[^"]*+"'`
     * succeeds because the node is GONE by the time `forces_registry` looks.
     *
     * [DD-14 wave G] IT NO LONGER RUNS *HERE*. It is `src/core/compile.c`'s
     * own line now, immediately after `pcrec_altcls` and before
     * `pcrec_callgraph_build` — because the graph is the only writer of
     * `Ast.u.call.body` and must run after every pass that REBUILDS a node
     * (this one splices an `A_ATOMIC` out), while ENGINE SELECTION now has to
     * run AFTER the graph, since §6.3's linkage is what decides whether a call
     * is structurally VM-only. Those two orders are satisfiable together only
     * with the discharge hoisted out of this pass, and hoisting it also
     * publishes the rewritten root, which this pass could not do: the
     * assignment below was to a LOCAL, so a discharge at the very ROOT was
     * dropped on the floor here and is now kept. Nothing else moves — the
     * discharge still runs before the first analysis round, which is the only
     * property the paragraph above claims. */

    for (int round = 0; round < SELECT_MAX_ROUNDS; round++) {
        mask = ENGM_DFA | ENGM_VM;
        why = NULL;
        why_pos = 0;
        node_why = NULL;
        node_why_pos = 0;
        for (size_t i = 0; i < sizeof analyses / sizeof analyses[0]; i++) {
            size_t p = 0;
            const char *w = NULL;
            unsigned m = analyses[i].forces(cx, root, &p, &w);
            if (!(m & ENGM_DFA) && !why) { why = w; why_pos = p; }
            if (!(m & ENGM_DFA) && analyses[i].node_derived && !node_why) {
                node_why = w; node_why_pos = p;
            }
            mask &= m;
        }
        if (mask & ENGM_DFA) break;   /* nothing forces the VM: done */
        /* Offer every registered rewrite a chance to discharge the forcing.
         * None is registered today, so this loop finds nothing to do and the
         * fixpoint terminates on the first round. */
        bool rewrote = false;
        for (size_t i = 0; i < sizeof analyses / sizeof analyses[0]; i++) {
            if (!analyses[i].discharge) continue;
            /* A discharge hook that rewrites must publish the new root; the
             * first customer to need it is the first to design that plumbing
             * (it cannot be written blind — see the size-estimate obligation
             * §5.2 hands the rewrite author). */
            rewrote = true;
        }
        if (!rewrote) break;
    }

    if (mask == 0)
        ctx_fail(cx, why_pos, "internal error: no engine can compile this pattern");

    fit.engines = mask;
    fit.why = why ? why_text(cx, why, why_pos) : NULL;
    fit.why_pos = why_pos;

    /* ---- the override (§5.6), applied to the fit the analyses computed ----
     *
     * DO-OR-DIE, never a silent fallback: a request the pattern cannot honour
     * is a clean refusal. Two distinct triggers, spelled differently because
     * they are different conflicts and a shared message would lie (§9.2 item
     * 2): the captures conflict (D44.6/E-7) names --no-captures as the way
     * out, since the caller asked for captures merely by not passing it; a
     * VM_ONLY-construct conflict names the construct.
     *
     * **[M6.2 wave E] THE SECOND BRANCH NOW HAS A POPULATION: `\K`.** It was
     * written at [M4.5b] and described here as "EMPTY BY POPULATION, not by
     * omission", on the argument that every VM_ONLY construct is gated by a
     * module with no producer. That argument was retired the moment module
     * `assertions` shipped `\K` (see this file's header), and the branch ran
     * for the first time without a line of it changing — which is the whole
     * value of having written it then. `pcrec -p rx --features assertions
     * --engine=dfa 'a\Kb'` refuses with "\K at pattern offset 1 requires the
     * VM engine, which --engine=dfa excludes", where the captures branch's
     * `--no-captures` advice would have been a lie: there is no flag that
     * makes a `\K` pattern DFA-compilable, and D44.6's rule is that a request
     * the pattern cannot honour is REFUSED, never silently downgraded. */
    switch (cx->opt->engine) {
    case PCREC_ENGINE_DFA:
        if (!(mask & ENGM_DFA)) {
            /* [M6.4.2 / D67 note 1] THE ORDERING FIX: take the captures branch
             * ONLY when no NODE-DERIVED analysis contributed a why. Before it,
             * `--engine=dfa '(a)\Kb'` advised `--no-captures` — a flag that
             * cannot help, because `\K` still forces the VM after the captures
             * are gone, and D44.6's rule is that a request the pattern cannot
             * honour is REFUSED rather than answered with advice that fails. */
            if (!node_why && cx->want_caps && cx->ncap > 0)
                ctx_fail(cx, why_pos,
                         "this pattern requires captures (on by default); pass "
                         "--no-captures for a DFA-only artifact, or omit "
                         "--engine=dfa");
            ctx_fail(cx, node_why ? node_why_pos : why_pos,
                     "%s requires the VM engine, which --engine=dfa excludes",
                     node_why ? node_why : why ? why : "this pattern");
        }
        fit.chosen = ENGM_DFA;
        break;
    case PCREC_ENGINE_VM:
        /* Always available: the VM can compile everything the DFA can. This
         * is the §3.7 GATE mode — see the prefilter line below. */
        fit.chosen = ENGM_VM;
        if (!fit.why) fit.why = "--engine=vm";
        break;
    default:
        /* auto: prefer the DFA whenever it can do the job (§5.4's zero
         * regression is achieved by NOT RUNNING the new code, not by the VM
         * being fast enough). */
        fit.chosen = (mask & ENGM_DFA) ? ENGM_DFA : ENGM_VM;
        break;
    }

    /* THE PREFILTER (§6.1, §4.7, and D44/R21 E-6).
     *
     * Under `auto` a VM artifact gets the capture-erased forward+reverse DFA
     * pair as an EXACT anchored-window prefilter, and that is not an
     * optimization — §4.7 makes it the rule that keeps DD-2 from being a
     * regression. `(a*)b` over 8 MB of `a` is answered `nomatch` by the
     * prefilter in one pass at DFA speed; a naive VM would need ~7e13
     * resumptions and would "fail honestly" where pcrec answers today at
     * 25 GB/s. A budget-exceeded return on a pattern pcrec answers today is a
     * regression, not robustness.
     *
     * Under `--engine=vm` it is OFF, deliberately (E-6): with the prefilter
     * running underneath, `span(VM) == span(DFA)` is close to a TAUTOLOGY,
     * because the hybrid hands the VM the DFA's own answer as its starting
     * window. Only a prefilter-free run is an independent second derivation,
     * which is what §3.7's differential needs to be a real gate.
     *
     * [M4.6f] D46's controllability half for this axis: `-fprefilter`/
     * `-fno-prefilter` OVERRIDE the derived value above in EITHER
     * direction, decoupling "does the hybrid run" from "which engine was
     * chosen" — up to now the only way to get it OFF under an
     * otherwise-auto selection was to also force `--engine=vm`, and the
     * only way to get it ON under `--engine=vm` was not to ask for
     * `--engine=vm` at all. DO-OR-DIE (the same posture the switch above
     * applies to `--engine` itself): forcing it ON when no VM artifact
     * exists to attach a prefilter to (fit.chosen == ENGM_DFA) is not a
     * request this pass can silently ignore or silently honour by
     * building a VM artifact nobody asked for — it REFUSES. Forcing it
     * OFF has no such hole: `--engine=vm` already ships a pure,
     * prefilter-free VM artifact today, so PCREC_NO_PREFILTER is always
     * buildable whatever engine was chosen. */
    {
        bool force_on  = (cx->opt->flags & PCREC_FORCE_PREFILTER) != 0;
        bool force_off = (cx->opt->flags & PCREC_NO_PREFILTER) != 0;
        /* [M6.5.2] §7.1: A BACKREF-BEARING PATTERN GETS NO PREFILTER, and this
         * is a REFUSAL of `-fprefilter` rather than a silent override, on
         * D46's own do-or-die posture — a request the pattern cannot honour is
         * refused, never quietly answered with something else.
         *
         * WHY THERE IS NO PREFILTER TO BUILD. `engine_m4.md` §6.1's hybrid does
         * not merely need a filter that cannot false-negative: it needs the
         * forward+reverse pair to hand the VM the EXACT anchored window, and
         * that section marks the erasure half STRUCTURAL for capture-only
         * patterns because there is no approximation step at all — `(a|b)` and
         * `(?:a|b)` build the identical `Ast` (D31), so the prefilter's DFA IS
         * the pattern's DFA. A backreference has no such identity. APPROACH
         * §2's "backrefs -> their referenced sub-pattern" is a real
         * approximation, and it fails BOTH halves of the hybrid's requirement:
         *
         *   - IT IS NOT EVEN A SUPERSET once the referenced group's TRANSITIVE
         *     CLOSURE holds an assertion or an atomic/possessive operator.
         *     MEASURED: 12 of 18 positive-control cells are false negatives
         *     across those two reasons — `(\ba)\1` on "aa" is (0,2) and its
         *     erasure `(\ba)\ba` matches NOTHING — plus 3 of 5 for the
         *     transitive case, where the referenced group itself passes both
         *     conditions and the assertion sits in a group reachable only
         *     through a NESTED reference.
         *   - ITS SPAN IS WRONG WHERE IT IS A SUPERSET. Over 12,786 distinct
         *     subject-family pairs the false-negative count is 0 for all six
         *     assertion-free families and the SPAN differs on up to 389
         *     subjects in one of them: `(["'])[^"']*\1` on "\"''" is truly
         *     (1,3) and the erasure says (0,2). A VM anchored to (0,2) does
         *     not find the (1,3) match.
         *
         * SO THE MACHINE IS NEVER BUILT — src/ir/nfa.c has no `A_BREF` arm and
         * falls into its internal error deliberately, and this line is what
         * makes that unreachable. The cost is measured and stated rather than
         * hidden: roughly one to two orders of magnitude on the families where
         * a prefilter would have helped, and nothing on the families where it
         * would not. §7.4 charters the two SOUND weaker uses (a nomatch-only
         * filter gated on the transitive closure, and a literal-prefix skip)
         * so that "VM-only, no prefilter" reads as THIS module's answer rather
         * than as a permanent verdict. */
        const bool has_bref = pcrec_has_bref(root);
        /* [DD-14] A CALL-BEARING PATTERN GETS NO PREFILTER EITHER, and this
         * line is WAVE E's by the design's own schedule (§8.2, §11 wave E,
         * sabotage row S-SR17). It lands HERE, in wave B+C, because without it
         * this wave ships something worse than a missing optimisation.
         *
         * ERASING A CALL IS NOT A SUPERSET — IT IS A DIFFERENT LANGUAGE, and
         * the counterexample is one line (§8.2): `a(?1)b` with group 1 = `x`
         * matches "axb"; erase the call and `ab` is left, which does not. So
         * the prefilter's rejection would be a FALSE NEGATIVE and the hybrid
         * would answer nomatch on a matching subject. That is unlike
         * `lookaround`'s erasure (a one-line superset proof, §5.3 there) and
         * exactly like `backrefs`' above.
         *
         * AND IT IS NOT A LATENT HAZARD TODAY, WHICH IS WHY IT COULD NOT WAIT.
         * `src/ir/nfa.c`'s `compile_ast` has an `A_CALL` arm that `ctx_fail`s
         * by name (design §4.4a site 25, DECLINE, "unreachable: VM_ONLY, no
         * prefilter"), and "unreachable" was true only while nothing produced
         * an `A_CALL`. MEASURED on this branch before this line existed: every
         * one of `(a)(?1)`, `(?R)`, `(?<n>a)(?&n)` answered `pcrec: internal
         * error: bad AST node` — a capture-bearing pattern routes to the VM,
         * the VM asks for its prefilter, and the prefilter build walks a node
         * it refuses. So the choice was not "ship the optimisation early", it
         * was "ship a compiler that cannot compile the module's own corpus".
         * REPORTED: S-SR17 therefore lands in wave B+C rather than wave E, and
         * wave E's remaining deliverable is the identity gate and SR-8's
         * stamps, not this predicate.
         *
         * THE COST IS MEASURED AND STATED rather than hidden, exactly as the
         * backrefs paragraph above states its own: 21x-350x on the sparse-
         * candidate shape a prefilter exists for, over the NON-RECURSIVE half
         * of the population (§8.3, on the inlined equivalents, 15 pairs
         * verified equivalent at 420 cells / 0 disagreements before any
         * timing). §8.3's sound construction — splice an acyclic callee's NFA
         * fragment, `Sigma*` for a cyclic one — is wave G's, and it is
         * designed and scheduled rather than waved at. */
        /* [DD-14 wave G] `pcrec_has_call`'s NARROWING. §8.2's argument — the
         * call-erased pattern is a DIFFERENT language, not a bigger one, so
         * the hybrid's DFA cannot be built from it — is an argument about a
         * call with no finite inlining. A SPLICED call has one and it is
         * EXACT (`src/ir/nfa.c`'s arm inlines the callee's fragment, and
         * capture erasure is the only thing it loses, as for every other
         * construct), so a pattern all of whose calls splice gets the same
         * prefilter the hand-inlined pattern gets — which is what §8.3
         * measured the previous line's absence costing at 21x-350x. A pattern
         * with even one LINKED call still gets nothing, because the machine
         * for that call cannot be built at all. */
        const bool has_call = pcrec_has_linked_call(root);
        if (force_on && (has_bref || has_call))
            ctx_fail(cx, why_pos,
                     "-fprefilter cannot be honoured for a pattern containing a "
                     "%s: the prefilter is a capture-erased DFA, and "
                     "erasing a %s changes the language it answers "
                     "for (drop -fprefilter)",
                     has_bref ? "backreference" : "subroutine call",
                     has_bref ? "backreference" : "subroutine call");
        if (force_on && force_off)
            ctx_fail(cx, why_pos,
                     "-fprefilter and -fno-prefilter cannot both be requested");
        if (force_on && fit.chosen != ENGM_VM)
            ctx_fail(cx, why_pos,
                     "-fprefilter requires the VM engine; this pattern "
                     "compiles to the DFA engine, which carries no separate "
                     "prefilter to force (pass --engine=vm, or drop "
                     "-fprefilter)");
        fit.prefilter = (has_bref || has_call) ? false
                       : force_on ? true
                       : force_off ? false
                       : (fit.chosen == ENGM_VM) &&
                         (cx->opt->engine != PCREC_ENGINE_VM);
    }

    cx->job->fit = fit;

    /* [ENG-BREP] the bounded-repeat ladder's analyses, run last and in the
     * ladder's own application order (D47.1), because they are the only steps
     * here that need the engine ALREADY chosen. */
    run_possessify(cx, root, &fit);
    run_revdet(cx, root, &fit);
}
