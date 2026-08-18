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
 * a producer): exactly one row, "capturing group with captures REQUESTED".
 * Every other VM_ONLY row in the registry is gated by a module with no
 * producer (§9.1), so the parser refuses those patterns long before selection
 * runs and this pass can never see one. That is also why SR-8's flip is
 * smaller than its row implies: ZERO currently-refused constructs become
 * compilable when the VM exists.
 *
 * [M4.7a]: SR-8's consuming socket is deliberately NOT built here yet — zero
 * producers means zero customers (D18/OS-0/D53's standing "earn its axis"
 * discipline). tests/registry/registry_check.c's check_engine_capability_
 * tripwire is what stands in for it: it asserts every VM_ONLY-masked
 * RS_MODULE row has no wired producer, so the day a module wires the first
 * one, THAT check fails and names this file as the thing to build before the
 * producer lands, not after.
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
    (void)a;
    if (!cx->want_caps || cx->ncap == 0) return ENGM_DFA | ENGM_VM;
    *why_pos = cx->first_cap_pos;
    *why = "capture group";
    return ENGM_VM;
}

static const EngineAnalysis analyses[] = {
    { "captures", forces_captures, NULL },
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

    for (int round = 0; round < SELECT_MAX_ROUNDS; round++) {
        mask = ENGM_DFA | ENGM_VM;
        why = NULL;
        why_pos = 0;
        for (size_t i = 0; i < sizeof analyses / sizeof analyses[0]; i++) {
            size_t p = 0;
            const char *w = NULL;
            unsigned m = analyses[i].forces(cx, root, &p, &w);
            if (!(m & ENGM_DFA) && !why) { why = w; why_pos = p; }
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
     * VM_ONLY-construct conflict names the construct. Only the first is
     * reachable today — every VM_ONLY construct is module-gated by a module
     * with no producer, so the parser refuses it first (§9.1). The second
     * branch is written anyway and is EMPTY BY POPULATION, not by omission. */
    switch (cx->opt->engine) {
    case PCREC_ENGINE_DFA:
        if (!(mask & ENGM_DFA)) {
            if (cx->want_caps && cx->ncap > 0)
                ctx_fail(cx, why_pos,
                         "this pattern requires captures (on by default); pass "
                         "--no-captures for a DFA-only artifact, or omit "
                         "--engine=dfa");
            ctx_fail(cx, why_pos,
                     "%s requires the VM engine, which --engine=dfa excludes",
                     why ? why : "this pattern");
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
        if (force_on && force_off)
            ctx_fail(cx, why_pos,
                     "-fprefilter and -fno-prefilter cannot both be requested");
        if (force_on && fit.chosen != ENGM_VM)
            ctx_fail(cx, why_pos,
                     "-fprefilter requires the VM engine; this pattern "
                     "compiles to the DFA engine, which carries no separate "
                     "prefilter to force (pass --engine=vm, or drop "
                     "-fprefilter)");
        fit.prefilter = force_on ? true
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
