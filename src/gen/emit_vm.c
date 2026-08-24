/* The backtracking VM as EMITTED SPECIALIZED C (docs/design/engine_m4.md §2).
 *
 * THERE IS NO INTERPRETER. APPROACH's opening sentence is that the generated
 * matcher "has no runtime interpreter, no dispatch tables to walk
 * generically", and a backtracking VM is the construct most likely to smuggle
 * one back in — the textbook shape is a bytecode array plus a `switch` in a
 * loop. So the pattern's program IS the emitted control flow: one label per
 * pattern position, every continuation resolved at compile time into a
 * fallthrough or a direct `goto`, and exactly ONE indirect jump in the whole
 * function — the `goto *` at the fail label, which fires once per backtrack
 * and never per byte (§2.7: the VM has no per-byte dispatch, so D13's
 * table-vs-computed-goto arbitration simply does not arise here).
 *
 * The five decisions the emitted shape encodes (§2.2):
 *   1. One function per pattern. Label addresses are function-local, which is
 *      fine WITHIN a call — APPROACH §6's A-4/A-5 "&&label does not survive a
 *      return" is a STREAMING constraint, not a within-call one.
 *   2. The fail label is the only backtracker and the only indirect jump.
 *   3. Greedy vs lazy is WHICH SIDE IS THE FALLTHROUGH. Greedy pushes the
 *      exit and falls into the body; lazy pushes the body and falls into the
 *      exit. No flag is consulted at run time (D18: options compile away,
 *      applied to quantifier preference).
 *   4. Alternation is the same shape, as a CHAIN — one live frame per
 *      alternation at any instant, not one frame per untried branch.
 *   5. Position is a plain local, restored from the resume frame, never
 *      trailed. So is the §2.5 cursor (D44/R21 E-4: a resume frame IS its
 *      save point, the same relationship `pos` has to every frame).
 *
 * BACKTRACKING IS AN EXPLICIT ARRAY, NEVER C RECURSION (§2.3), for three
 * independent reasons any one of which suffices: this project has already
 * paid for unbounded recursion on pattern structure twice (DD-10, D10); D19's
 * 128 KB thread-stack budget is a real number and a recursive matcher's depth
 * is data-dependent; and you cannot portably check C stack depth, while DD-2
 * requires that you check something.
 *
 * WHAT THIS FILE DOES NOT DO, deliberately (§6.4, and the [M4.5] scope line):
 * no DFA islands, no accept-list islands, no auto-possessification, no
 * RX_HYBRID_MIN threshold, no trie-factored first-byte switch. Those are
 * M4.6's, and several of them are gated on measurements nobody has taken.
 * The §2.5 cursor ladder lands at its two lowest rungs (see vm_det_seq).
 */

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "core/internal.h"
/* [M6.5.2] the encoding seam's ENTRY IDS. This emitter names two of them (the
 * backreference compare and its caseless twin) as it emits their calls; the
 * TEXT of every entry stays in src/gen/enc/, which is DD-12 (7)'s whole
 * point — nothing here knows what an encoding does, only which entries this
 * artifact needs. */
#include "gen/enc/enc.h"

/* ---- capacities ------------------------------------------------------------
 *
 * BRING-UP PLACEHOLDERS, and stated as such (§4.6, D12: budgets come from
 * measured medians, and there is no measurement yet — [M4.6] takes it by
 * running the corpus and the bench matrix with the counter instrumented and
 * setting the default from the maximum any legitimate pattern needs, with a
 * stated margin). What is NOT a placeholder is the MECHANISM and the honest
 * stamping: whatever these numbers are, rx_info says what the artifact
 * actually enforces.
 *
 * PCRE2's own match_limit default (10,000,000) is explicitly NOT adopted: its
 * unit is internal match() calls, which it also spends on non-backtracking
 * recursion, where ours is resumptions. Copying the number would be false
 * precision dressed as compatibility, which D26 tier 3 exists to prevent.
 *
 * The two array caps are bounded by D19's 128 KB thread stack rather than
 * chosen for generosity: rx_run_state is a LOCAL of the search entry, a resume
 * frame is 24 B and a trail entry 16 B (D44.1's measured per-entry constants),
 * so 2048 + 3072 is ~96 KB — a large but survivable share of that budget
 * (~32 KB remains for the entry's scalars and callees), and the reason the
 * residual unbounded class carries a stamped subject_ceiling instead of
 * pretending the limit is not there. RECALIBRATED [M4.6a] 2026-08-17 (was
 * 1024/1536 ≈ 49 KB, a bring-up value): the corpus-and-scale sweep
 * (docs/design/m46a_impl/) measured the shipped default's real reach on the
 * exposed shape class (same-trailing-byte capturing alternations, which miss
 * the revdet rung and fall to frames-unbounded) at a 256-byte
 * subject_ceiling — small for legitimate multi-token text; 2x doubles reach
 * to ~512 bytes and is the maximum headroom-preserving step under D19
 * (~2.6x is the absolute fit). Multi-KB reach needs an ENGINE change
 * (cursor/revdet eligibility for same-trailing-byte alternations), not this
 * knob. */
enum {
    VM_DEFAULT_RESUME_FRAMES    = 2048,
    VM_DEFAULT_TRAIL_FRAMES = 3072,
    /* Exact sizing (§2.5: "where the pattern's dynamic depth is statically
     * bounded the emitter computes the exact requirement") is clamped here.
     * Past the clamp the requirement is bounded but does not fit the stack
     * budget, so the artifact enforces the clamp and says so. RECALIBRATED
     * [M4.6a] 2026-08-17 with the DEFAULT pair above (was 1024/1536): the
     * two pairs are distinct knobs — this one caps the large-BOUNDED class's
     * exact sizing, the pair above serves the UNBOUNDED class — but both
     * emit the same two arrays under the same D19 arithmetic, so they move
     * together or the calibration is half-landed (measured: changing only
     * the pair above left `((a)|ab){0,4000}c` at 1024 frames / ceiling 307,
     * which is how the two-knobs fact was discovered). */
    VM_MAX_AUTO_RESUME_FRAMES    = 2048,
    VM_MAX_AUTO_TRAIL_FRAMES = 3072
};

/* §4.6's budget, named rather than spelled inline. RULED 500,000,000 (D51
 * ruling 3, 2026-08-17) — was 1,000,000, a bring-up placeholder.
 *
 * WHY IT MOVED, and it is D49's own failure-direction asymmetry applied
 * consistently rather than a new argument. [M4.6a]'s calibration measured an
 * ORDINARY capturing repeated-alternation shape — `(a|b)+c`-shaped, the stuff
 * of log and token parsing — costing steps LINEARLY in subject length even on
 * its optimized rung, about 0.5 steps per byte, so 4,000,002 steps at 8 MB.
 * At 10^6 the shipped default refused a legitimate 2 MB match. At 500M both
 * bounds tolerate roughly 1 GB of ordinary subject, which is parity with the
 * work bound's own ruled ~10^9. Too LOW is a wrong answer on the shipped
 * path; too high costs diagnostic-path time on a pathological one, and only
 * the first is an error a caller cannot see.
 *
 * WHAT IT COSTS, accepted with eyes open: at the measured ~50M steps/s the
 * worst-case delay before an honest refusal is about ten seconds. DD-2 is
 * ROBUSTNESS, not a latency guarantee, and D22 says so.
 *
 * WHY IT LANDS WITH MRL AND NOT BEFORE. Post-MRL the K23 resident costs one
 * step, so the ratchet's known_fail entry flips because the DEFECT is fixed.
 * Raising the budget first would have flipped the same test by outspending
 * the explosion — 10.6M steps against a 500M budget — and left the class
 * itself untouched one size up (`(a{11,22}){11,50}` needs 111M, and the law
 * climbs ~11x per unit of m). The two changes are ordered so the test that
 * moves says what it means.
 *
 * The 20M measured-conservative option is the road not taken; it is recorded
 * in docs/design/m46a_impl/'s proposal table. A bring-up-calibrated value the
 * project can move again with evidence, in [M4.6a]'s own posture. */
#define VM_DEFAULT_STEP_BUDGET 500000000LL

/* [ENG-BREP counter-K] The THIRD bound's default (D47 SECOND ADDENDUM
 * settlement 4; the VALUE ruled at D49). Its unit is a WORK UNIT — one frame
 * discarded at a cut, one iteration of a frameless scan — and it is a
 * SEPARATE counter from the step budget, which keeps its exact meaning of one
 * backtrack resumption. Nothing is scaled into anything.
 *
 * WHY 10^9 AND WHAT IT COSTS, because the number is a judgement and not a
 * measurement. A frameless scan charges one unit per subject byte, so an
 * ordinary single-pass linear match reaches this bound at roughly 1 GB of
 * subject, and the possessify quadratic (n^2/2 units) trips at n ~= 45,000,
 * about a second of work. The measured alternative was ~1.6x10^7 — the value
 * commensurate with a backtrack resumption at the MEASURED 16:1 work ratio
 * (a resumption costs about 16 scan iterations; counterk_design.md 7.4) —
 * which would trip the quadratic at n ~= 5,700 but refuse ordinary linear
 * matching above ~16 MB. D49 took 10^9 on the failure-direction asymmetry:
 * too high costs diagnostic-path time, too low is a WRONG ANSWER on the
 * shipped path.
 *
 * A BRING-UP VALUE in exactly the sense VM_DEFAULT_STEP_BUDGET is one — D12
 * rules budgets come from measured medians, and [M4.6] takes the measurement
 * for both. This is NOT in src/core/limits.h, and deliberately: that file's
 * own inclusion rule is "a number belongs here if changing it changes what
 * pcrec ACCEPTS, REJECTS or PROMISES", and a runtime give-up budget changes
 * none of the three at compile time. It lives beside its two siblings. */
#define VM_DEFAULT_WORK_BUDGET 1000000000LL

/* The §2.5 cursor rung only fires for bodies whose emitted inline test stays
 * small; past this the body goes to the frames rung, which is correct and
 * merely costs frames. Keeps `(?:abcdef){3}*`-shaped bodies from emitting a
 * wide conjunction for no gain. */
enum { VM_MAX_STRIDE = 32 };

/* Capture groups a cursor-rung body may contain. A body of stride <= 32 can
 * still nest arbitrarily many groups (`((((a))))` is four groups in one byte),
 * so this is NOT implied by VM_MAX_STRIDE and needs its own bound. */
enum { VM_MAX_BODY_CAPS = 64 };

/* ---- the emitter's state -------------------------------------------------*/

/* ---- [M4.5c] the emitted-program LISTING (DD-8, engine_m4.md S10) --------
 *
 * S10's ONE constraint is load-bearing and it is the reason this is an EVENT
 * STREAM rather than a second walk over the AST: "the dump must be derived
 * from the same structure the emitter walks, never a parallel description — a
 * second source of truth for what the VM does is worse than no dump."
 *
 * So every event below is appended by the SAME call that writes the
 * corresponding C. `vm_lbl` writes a label and records one; `vm_push` writes an
 * RX_PUSH and records one; `vm_set` writes an RX_SET and records one. There is
 * no code path that can emit a label without recording it, because there is no
 * second way to emit a label.
 *
 * Every SECTION of the listing is then a VIEW over that one stream — the
 * program listing, the choice-point summary with its preference order, the
 * slot map, the island list and the callout list are all filters, so they
 * cannot disagree with each other either. Two sections drifting apart is the
 * same failure as the dump drifting from the emitter, one level down.
 *
 * The `role` strings are the only content that is not mechanically derived,
 * and they are decoration: they say WHY a choice point exists, never that one
 * does. The structural check (tests/codegen/run_ir_listing.sh) pins the
 * derivable half — label set, push count, slot set — against the emitted C. */
typedef enum {
    VE_LABEL,    /* a: label id                                    */
    VE_CLASS,    /* a: class pool id, b: next label                */
    VE_PUSH,     /* a: resume label id                             */
    VE_SET,      /* a: slot_values slot                            */
    VE_GOTO,     /* a: target label id                             */
    VE_FAIL,
    VE_ACCEPT,
    VE_ASSERT,   /* text: the assertion's name                     */
    VE_NOTE,     /* text: an inline note on the current label      */
    VE_ISLAND,   /* reserved: no producer (engine_m4.md S6.3)      */
    VE_CALLOUT,  /* reserved: no producer (module 'callouts')      */
    VE_RUNG,     /* [D46] a: the A_REP's own entry label id,
                  *       b: VmRungKind ordinal                     */
    VE_STRAT,    /* [ENG-BREP] a: the A_REP's own entry label id,
                  *       b: VmStratKind ordinal                    */
    VE_CUT,      /* [ENG-BREP] a: the cut-mark slot_values slot    */
    VE_PRUNE,    /* [M4.6d] a: the A_REP's own entry label id,
                  *       b: VmPruneKind ordinal                    */
    /* [DD-14 wave B+C] the SUBROUTINE CALL's two events. Both write C, so
     * unlike VE_RUNG/VE_STRAT/VE_PRUNE they belong in the PROGRAM trace:
     * a call and a return are things that EXECUTE. */
    VE_CALL,     /* a: the callee region's entry label id,
                  *    b: the return label id                       */
    VE_RETURN    /* a: the callee region's entry label id           */
} VEKind;

/* [D46] the S2.5 rung ladder's own small named value set, ONE PER
 * QUANTIFIER BODY (never per artifact — vm_cursor_fits is consulted once
 * per A_REP node, at this file's own three call sites, so two quantifiers
 * in one pattern can and do land on different rungs). Bit values, not
 * sequential ordinals, because the compile-time macro is a SUMMARY BITMASK
 * over however many distinct rungs one program's quantifiers actually use. */
typedef enum {
    VM_RUNG_CURSOR           = 0,  /* index into vm_rung_bit[], not a bit */
    VM_RUNG_FRAMES_BOUNDED   = 1,
    VM_RUNG_FRAMES_UNBOUNDED = 2,
    /* [ENG-BREP] engine_m4.md §2.5's REVERSE-DETERMINISTIC rung, between the
     * cursor and the frames: ONE body copy, a deterministic forward scan, one
     * resume frame for the whole loop, and a backward walk over the reversed
     * body for the retreat and for §3.4's last-iteration captures. */
    VM_RUNG_REVDET           = 3,
    /* [ENG-BREP] the COUNTER rung, the ladder's last step before replication:
     * ONE body copy per K iterations plus a TRAILED iteration counter, so the
     * emitted size of a bounded repeat stops being a function of its COUNT.
     * It sits BELOW revdet — a body that admits the backward walk should take
     * that rung, which owes no per-iteration frames at all; the counter rung
     * is what catches the bodies both earlier rungs decline. */
    VM_RUNG_COUNTER          = 4
} VmRungKind;
enum { VM_NRUNG = 5 };
static const unsigned vm_rung_bit[VM_NRUNG] = { 0x1u, 0x2u, 0x4u, 0x8u, 0x10u };
static const char    *const vm_rung_kindname[VM_NRUNG] =
    { "cursor", "frames-bounded", "frames-unbounded", "revdet", "counter" };

/* [ENG-BREP/D46] the LADDER's first rung as its own small named value set,
 * sitting BESIDE the rung rather than inside it: a possessified quantifier
 * still takes a rung (it is the rung's machinery that shrinks), so folding
 * possessification into VmRungKind would make the two facts compete for one
 * value. Same bitmask shape and same reason — the strategy is chosen PER
 * A_REP, so an artifact whose quantifiers differ needs a mask, not a scalar.
 *
 * The do-or-die half D47.3 moves to observability rides on this: under
 * `-fno-possessify` the POSSESSIVE bit must not appear in any artifact, and
 * tests/possessify/run_possessify_tests.sh asserts exactly that rather than
 * trusting the flag. */
typedef enum {
    VM_STRAT_POSSESSIVE   = 0,   /* index into vm_strat_bit[], not a bit */
    VM_STRAT_BACKTRACKING = 1
} VmStratKind;
static const unsigned vm_strat_bit[2] = { 0x1u, 0x2u };
static const char    *const vm_strat_kindname[2] =
    { "possessive", "backtracking" };

/* [M4.6d] MINIMUM-REMAINING-LENGTH PRUNING, the ladder's THIRD observable
 * axis, in the same shape and the same place as the two above and for the
 * same reason: whether a quantifier carries an MRL bound is decided PER
 * A_REP — it depends on that quantifier's own FOLLOW-MIN, so `(a{2,4}){3,9}b`
 * clamps at every replica and `(a{2,4}){3,9}` clamps at none — and a scalar
 * "is this artifact pruned" would lie on the mixed case.
 *
 * The distinction the two values draw is between "a bound exists here and is
 * emitted" and "the analysis ran and produced ZERO", which are very different
 * facts about an artifact and would otherwise be indistinguishable from the
 * outside. A quantifier whose follow needs no bytes (the trailing `{10,50}`
 * of `(a{10,20}){10,50}` past its tenth replica) has `minrest == 0` and gets
 * no clamp: correct, and nothing to see. An artifact where EVERY quantifier
 * reads UNCLAMPED is either a pattern with no length constraint at all or a
 * threading bug, and only the stamp can tell a test which.
 *
 * D47.3's do-or-die half rides on this exactly as it does on the strategy
 * mask: under `-fno-length-prune` the CLAMPED bit must not appear in any
 * artifact, and tests/mrl/run_mrl_tests.sh asserts that rather than trusting
 * the flag. */
typedef enum {
    VM_PRUNE_CLAMPED   = 0,   /* index into vm_prune_bit[], not a bit */
    VM_PRUNE_UNCLAMPED = 1
} VmPruneKind;
static const unsigned vm_prune_bit[2] = { 0x1u, 0x2u };
static const char    *const vm_prune_kindname[2] =
    { "clamped", "unclamped" };

typedef struct {
    VEKind      k;
    int         a, b;
    const char *role;   /* arena-owned; NULL when there is nothing to say */
} VEvent;

/* [DD-14 wave B+C] `Cost` gains a TAG and is forward-declared here, because
 * `Vm` now carries the per-region cost memo and `Vm` is defined first. The
 * struct's own definition and every comment on it are unmoved. */
typedef struct Cost Cost;

typedef struct {
    Ctx      *cx;
    StrBuf   *b;          /* SCRATCH: the VM function's body, see vm_emit_all */
    const char *p;        /* --prefix */
    char      up[80];     /* uppercased prefix */
    int       nlabel;
    int       ngroups;    /* capturing groups (0 when --no-captures) */
    int       nguard;     /* empty-iteration guard slots assigned so far */
    int       nguard_total; /* the count vm_count_slots found: the low-water
                             * slots sit ABOVE all of them, so their base can
                             * only be computed from the TOTAL, never from
                             * the running assignment counter */
    int       nlow;       /* cursor low-water slots assigned so far */
    int       nlow_total; /* the count vm_count_slots found — vm_slot_mark's
                           * base, for vm_slot_low's own reason */
    int       nmark;      /* [ENG-BREP] possessive cut-mark slots so far */
    int       nmark_total;
    int       nrev;       /* [ENG-BREP] revdet LOOPS so far (3 slots each) */
    int       nrev_total;
    int       nctr;       /* [ENG-BREP counter-K] counter LOOPS so far, one
                           * TRAILED iteration-counter slot each. Trailed and
                           * not a local: RULED (R25 ASK 3), and the saving the
                           * design note proposed for the possessive arm was a
                           * MANDATORY-PHASE MISCOMPILE — the mandatory copies
                           * have no cut between them, so a body-internal frame
                           * from iteration 1 resumes reading a stale local and
                           * `(?:a|bc){3}+` runs one iteration where it must run
                           * three. */
    int       nctr_total;
    /* [M6.6.2] THE LOOKAROUND's TWO SLOT FAMILIES (design §3.3's per-shape
     * table, §3.7's budget). They sit at the TOP of the layout, ABOVE the
     * pending block, so every base below them is unmoved and a
     * lookaround-FREE artifact's slot numbering is byte-identical to what it
     * always was — which is the property tests/codegen/run_lookaround_
     * identity.sh's FREE bucket asserts.
     *
     * TWO FAMILIES AND NOT ONE, and it is not bookkeeping: which of them a
     * given lookaround allocates is READ OFF ITS FLAGS (`vm_look_needs_mark`
     * / `vm_look_needs_pos` below), so "no mark slot was allocated" is how a
     * reader tells a NON-ATOMIC form from an atomic one in the emitted C and
     * in `--emit-ir` (§3.6). It is at most two per lookaround and sometimes
     * one — never a flat two. */
    int       nlookmark;        /* SLOT_LOOK_MARK<n> assigned so far */
    int       nlookmark_total;
    int       nlookpos;         /* SLOT_LOOK_POS<n> assigned so far */
    int       nlookpos_total;
    /* [M6.5.2] PUBLISH-AT-CLOSE's bookkeeping, and it is a PRE-COMPUTED MAP
     * rather than a running counter, unlike every slot family above it.
     *
     * `pend_of[g]` is group g's PENDING slot index (0-based within the pending
     * block) or -1 for a group no backreference names. The marked set is a
     * property of the whole tree — the union of every `A_BREF`'s `refs` —, so
     * it is known before the walk begins and there is nothing to assign as the
     * walk proceeds. That is also what makes the cost claim checkable: an
     * unmarked group's emitted code is byte-identical to what it always was,
     * because `pend_of[g] < 0` selects the pre-[M6.5] arm.
     *
     * `npend_total` sizes the block; both are zero for every pattern with no
     * backreference, so the layout below the pending block never moves. */
    const int *pend_of;
    int        npend_total;
    /* [M6.5.2] the residual entries this artifact turns out to need, OR'd as
     * the A_BREF arm emits each call. Copied to `Job.enc_mask` before the
     * prologue, which is what makes "the artifact declares exactly the entries
     * it calls" true by construction rather than by a second analysis. */
    unsigned   enc_mask;
    int       unroll_k;   /* [ENG-BREP counter-K] K, resolved ONCE from the
                           * options (PCREC_DEFAULT_UNROLL_K when unset). One
                           * per artifact, never per quantifier — D47 ADDENDUM
                           * holds eng_brep_design.md §4.5 strictly. Read here
                           * rather than at each site so the emitter and the
                           * two pre-passes cannot disagree about it. */
    int       nrevcaps;   /* the largest capture-group count any one revdet
                           * body has — sizes the SHARED recovery locals. One
                           * array serves every revdet loop because a walk's
                           * results are PUBLISHED into slot_values before control
                           * leaves the loop, so nothing outlives its own
                           * commit. */
    int       nocap;      /* [ENG-BREP] >0 while emitting (or costing) a revdet
                           * loop's FORWARD body, where capture writes are
                           * SUPPRESSED: they are what would otherwise make the
                           * trail grow per iteration, and they are redundant,
                           * because §3.4's backward walk recovers every one of
                           * them from the committed span. A counter rather
                           * than a bool so a nested construct cannot clear a
                           * suppression it did not set. */
    long long npush;      /* [M4.5c fix] emitted RX_PUSH sites, counted in the
                           * pre-pass. Reported in the listing so a check can
                           * hold it against the artifact; not itself a cap. */
    long long maxcopies;  /* the largest REPLICATION FACTOR any one bounded
                           * repeat over a choice-bearing body demands. This is
                           * what PCREC_MAX_VM_REPEAT_COPIES bounds, and it is
                           * known before emission — which is the point. */
    long long nodes;      /* emitted-node budget, against PCREC_MAX_VM_NODES */
    unsigned  rungs;       /* [D46] BITMASK of VmRungKind values PRESENT in
                            * this program — the rung decision is PER
                            * QUANTIFIER BODY (vm_cursor_fits is consulted
                            * once per A_REP, emit_vm.c's own emission and
                            * slot-counting call sites), so a pattern with
                            * two quantified bodies can and does mix rungs;
                            * a SCALAR "the rung" would lie on that case.
                            * Set bit-by-bit, once per A_REP, by
                            * vm_rung_mark() — called from the same real
                            * emission sites that already label that A_REP's
                            * own entry (vm_cursor_rep / vm_rep's frames
                            * fallthrough), never re-derived from the AST.
                            * See vm_rung_mark() and the VE_RUNG listing
                            * section for the per-quantifier detail this
                            * mask summarizes. */
    unsigned  strats;      /* [ENG-BREP] the same shape one rung down the
                            * ladder: BITMASK of VmStratKind values present,
                            * set by the same vm_rung_mark() call that sets
                            * `rungs`, from the same `vm_cuts()` answer the
                            * emitter is about to act on ([M6.4.2]: the LIFT
                            * routes a semantic possessive onto these rungs
                            * with no `Ast.u.rep.possessive` behind it, and a stamp
                            * that said BACKTRACKING on a loop that cuts would
                            * be the K29 class of lie). One call, one
                            * truth — the macro, the listing section and the
                            * emitted machinery cannot disagree about whether
                            * a quantifier was possessified, because there is
                            * one place that says so. */
    unsigned  prunes;      /* [M4.6d] the same shape one axis over: BITMASK of
                            * VmPruneKind values present, set by the same
                            * vm_prune_mark() the emission site calls at the
                            * point it has the quantifier's own minrest in
                            * hand. One call, one truth — the macro, the
                            * listing section and the emitted bound cannot
                            * disagree about whether a quantifier was
                            * clamped. */
    /* [M4.6d] MRL's FOLLOW-MIN ACCUMULATOR (k23_design.md §4.3): the minimum
     * number of subject bytes any accepting continuation must consume AFTER
     * the node currently being emitted. Threaded DOWN the walk rather than
     * computed per program point, which is the design's own rule and is what
     * makes the per-replica constant fall out of the walk instead of needing
     * an index into the replicas.
     *
     * It is a member rather than a vm_emit parameter for one reason: vm_emit
     * has a dozen call sites and a parameter would have made every one of
     * them a place to get it wrong silently. As a member with ONE mutator
     * (vm_emit_f, which saves and restores), a site that says nothing
     * inherits its caller's value — which is the correct answer at every site
     * that does not change the follow (A_CAP, A_ALT's branches, an optional
     * copy). */
    long long fmin;
    /* [M4.6d] the follow-min's RUNTIME half, as a C expression, or NULL.
     *
     * Almost every follow-min is a compile-time constant, because almost
     * every loop the emitter walks is replicated or unrolled and the emitter
     * therefore knows which copy it is writing. ONE rung breaks that: the
     * counter rung's MANDATORY phase emits K body copies that serve every
     * trip, so "how many mandatory iterations are still to come" is
     * `count - slot_values[ctr] - j` and lives in a trailed slot rather than in the
     * emitter. k23_design.md §4.5 designed exactly this expression; the
     * blinded test author MEASURED that leaving it out leaves K23 alive on
     * `(a{1,3}){65}`, where the compile-time view sees at most K iterations
     * of follow and the real one is 65.
     *
     * Combined with `fmin` at each emission site as `fmin + (fdyn)`, so an
     * inner site inside a counter trip inherits the outer trip's term
     * automatically -- the same inherit-by-default rule `fmin` itself has. */
    const char *fdyn;
    bool      mrl;        /* [M4.6d] MRL pruning is ON for this artifact
                           * (i.e. `-fno-length-prune` was not passed). Read
                           * at every emission site through vm_mrl_test /
                           * vm_mrl_gate, never re-derived from the flags. */
    bool      mrl_win;    /* [M4.6d] the CEILING is the prefilter's match-end
                           * window (D51 ruling 2) rather than the subject
                           * end. Set ONCE before the walk, from
                           * job->fit.prefilter AND the two suppressing
                           * predicates ([M6.4.2]'s atomic, [M6.6.2] wave E's
                           * lookaround); the walk itself never reads it,
                           * because the ceiling is hidden behind the emitted
                           * macro. FOUR READERS, and the four-ness is R31 E3:
                           * the --emit-ir description, the RX_VM_PRUNE_CEILING
                           * stamp, and the TWO lines that BUILD the ceiling
                           * (the search entry and the retry recompute). A
                           * reader that re-derived from job->fit.prefilter
                           * instead would let the stamp disagree with the code
                           * it describes — that was the defect, and codegen
                           * rule 1 asserts on both sources because of it. */
    long long ndynskip;   /* [M4.6d] times vm_dyn_add took its LENGTH RETREAT,
                           * dropping an outer runtime follow-min term because
                           * the composed expression grew past
                           * VM_MRL_DYN_MAX. The retreat is sound (it
                           * under-estimates) and is unreachable on anything
                           * pcrec compiles today — which is exactly why it is
                           * counted rather than trusted: an unstamped
                           * fallback that starts firing is a silent loss of
                           * pruning nobody would attribute. Reported in the
                           * listing beside the bound-site count. */
    long long nclamp;     /* [M4.6d] emitted MRL bound sites, counted as they
                           * are written. Reported in the listing so a check
                           * can assert the bounds EXIST rather than trusting
                           * that the analysis ran — vm_work's own discipline,
                           * applied to a bound instead of to a charge. */
    long long ngst;       /* [M6.2 wave D] emitted `\G` test sites, counted as
                           * they are written. It is the gate on the
                           * `<prefix>_startpos` PARAMETER, and it is counted
                           * during the walk for `nclamp`'s exact reason: the
                           * function header is printed after the body, so the
                           * emitter can read what the body actually needed
                           * instead of a second analysis predicting it. A
                           * `\G`-free program keeps the signature it had
                           * before this wave and stays byte-identical. */
    long long nkreset;    /* [M6.2 wave E] emitted `\K` write sites, counted as
                           * they are written — `ngst`'s shape and `nclamp`'s
                           * reason. It is the gate on ONE decision in a
                           * DEFAULT artifact: whether `<prefix>_caps_out`
                           * derives `caps[0][0]` from slot 0 or from its
                           * `start` argument. A `\K`-free program takes the
                           * pre-wave arm and is byte-identical, and because
                           * that is the only default-artifact site reading
                           * this counter, "a `\K`-free pattern pays nothing"
                           * is a one-predicate claim rather than the
                           * multi-site construction waves B-D each had to
                           * argue.
                           *
                           * TWO NON-DEFAULT SURFACES read it as well, and
                           * neither weakens that: `--emit-ir`'s SLOTS row
                           * (slot 0 stops being entry-only the moment a `\K`
                           * exists, and a listing saying otherwise would
                           * describe a different program from the one beside
                           * it — S10's drift), and `--trace`'s ACCEPT line
                           * (which reports the consumed span AND the reported
                           * one, because on a `\K` artifact they differ and
                           * either alone misleads). A listing writes no
                           * artifact at all, and `--trace` is a generation
                           * axis whose artifact is different by
                           * construction. */
    bool      tracing;    /* --trace: emit an instrumented artifact */
    bool      has_budget; /* [ENG-BREP counter-K] the counters exist in this
                           * artifact (ONE gate for both, D49). Read by the
                           * WORK charge sites, which are emitted DURING the
                           * walk — unlike the fail label's step charge, which
                           * is emitted afterwards and can read the local.
                           * Set before vm_emit for exactly that reason. */
    long long nwork;      /* [ENG-BREP counter-K] emitted WORK charge sites,
                           * counted as they are written. Reported in the
                           * listing so a check can assert the sites exist
                           * rather than trusting that the flag was passed —
                           * D47.3's do-or-die discipline, applied to a
                           * charge instead of to a rung. */
    /* [DD-14 wave B+C] THE CALL GRAPH AND THE PER-REGION TABLES.
     *
     * `cg` is `cx->callgraph` (NULL for a call-free pattern), and every field
     * below is indexed by TARGET INDEX — `pcrec_callgraph_target(cg, i)` is
     * the group number, `0` meaning the ROOT.
     *
     * `has_calls` GATES EVERY BYTE THIS MODULE ADDS TO AN ARTIFACT, and it is
     * one flag rather than a condition re-derived at each of the six emission
     * sites for the reason §9.1's identity gate needs: the resume frame gains
     * two fields, `RX_PUSH` gains a line, the fail label gains a line, the two
     * reset functions gain a line each, and the `RX_CALL` macro appears — so a
     * call-FREE artifact is byte-identical to a pre-module one BY
     * CONSTRUCTION, never by a filtered comparison.
     *
     * `rgn_w`/`rgn_nw` are `W` (§5.3a), computed HERE and not in
     * `src/opt/callgraph.c` because they are SLOT INDICES and slot indices are
     * this file's own layout — see that file's header for the full argument. */
    const struct CallGraph *cg;
    bool      has_calls;
    int       nregion;    /* emitted callee regions == pcrec_callgraph_ntargets */
    long long ncall;      /* emitted RX_CALL SITES, counted as they are written
                           * — `nclamp`'s discipline applied to a call: a check
                           * can assert the sites EXIST rather than trusting
                           * that the graph ran. NOT the gate (`has_calls` is),
                           * because a call parked under `X{0}` emits no site
                           * while its region is still emitted. */
    int      *rgn_lbl;    /* region i's ENTRY label id */
    int      *rgn_exit;   /* region i's EXIT label id (where RX_RETURN sits) */
    int     **rgn_w;      /* W(i), ascending slot indices */
    int      *rgn_nw;     /* |W(i)| */
    Cost     *rgn_cost;   /* region i's own cost, memoised (§5.7) */
    /* class bitmap pool, deduplicated */
    uint8_t (*cls)[32];
    int       ncls, clscap;
    /* [M4.5c] the listing's event stream — see VEvent above */
    VEvent   *ev;
    int       nev, evcap;
} Vm;

static void vm_ev(Vm *v, VEKind k, int a, int b, const char *role)
{
    if (v->nev == v->evcap) {
        int ncap = v->evcap ? v->evcap * 2 : 256;
        VEvent *nv = arena_alloc(&v->cx->arena, (size_t)ncap * sizeof(VEvent));
        if (v->nev) memcpy(nv, v->ev, (size_t)v->nev * sizeof(VEvent));
        v->ev = nv;
        v->evcap = ncap;
    }
    v->ev[v->nev].k = k;
    v->ev[v->nev].a = a;
    v->ev[v->nev].b = b;
    v->ev[v->nev].role = role;
    v->nev++;
}

/* Arena-owned formatted text for a role string. */
static const char *vm_rolef(Vm *v, const char *fmt, ...)
    __attribute__((format(printf, 2, 3)));
static const char *vm_rolef(Vm *v, const char *fmt, ...)
{
    char buf[160];
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(buf, sizeof buf, fmt, ap);
    va_end(ap);
    if (n < 0) return NULL;
    size_t sz = (size_t)n + 1;
    if (sz > sizeof buf) sz = sizeof buf;
    char *q = arena_alloc(&v->cx->arena, sz);
    memcpy(q, buf, sz - 1);
    q[sz - 1] = 0;
    return q;
}

static int vm_label(Vm *v) { return v->nlabel++; }

static void vm_charge(Vm *v)
{
    if (++v->nodes > PCREC_MAX_VM_NODES)
        ctx_fail(v->cx, 0, "pattern too large (VM exceeds %d emitted nodes)",
                 PCREC_MAX_VM_NODES);
}

/* Slot layout in `slot_values` (§2.4: ONE flat array, so the restore loop is written
 * once, the overflow bound is one number, and a future slot class costs a
 * layout row rather than a new save/restore path).
 *
 *   [0 .. 2*ngroups+1]  capture pairs; slots 0,1 are $0 (written by the ENTRY,
 *                       not by the VM — §3.4)
 *   next nguard         empty-iteration guards (§3.3), one per rmax==-1
 *                       nullable quantifier on the frames rung
 *   next nlow           cursor low-water marks (§2.5's RULED re-push
 *                       discipline). NOT the cursor itself, which is a plain
 *                       untrailed local: what a span loop cannot recover from
 *                       its own resume frame is where the loop STARTED, and
 *                       that is what lives here. It is written once per loop
 *                       ENTRY (not per iteration, and not per retreat), so it
 *                       costs O(1) trail per entry, which is the whole point.
 */
static int vm_slot_guard(Vm *v, int i) { return 2 * (v->ngroups + 1) + i; }
static int vm_slot_low(Vm *v, int i)   { return 2 * (v->ngroups + 1) + v->nguard_total + i; }
/* [ENG-BREP] the fourth slot class: a possessified frames-rung loop's CUT
 * MARK, the resume-stack depth to truncate back to. It sits above the low-water
 * marks, so like them its base is computed from the TOTALS the pre-pass found
 * and never from a running counter. */
static int vm_slot_mark(Vm *v, int i)
{
    return 2 * (v->ngroups + 1) + v->nguard_total + v->nlow_total + i;
}
/* [ENG-BREP] the fifth slot class: THREE per reverse-deterministic loop, and
 * three whatever the preference or the verdict.
 *
 *   +0  `entry` — the loop's start position. The capture walk's FLOOR.
 *   +1  `low`   — the boundary after `rmin` iterations. The retreat's FLOOR.
 *   +2  `hi`    — the maximal boundary the forward scan reached. The lazy
 *                 extension's CEILING, which is what lets a lazy loop enforce
 *                 its `{m,n}` cap POSITIONALLY instead of with a per-extension
 *                 trailed counter.
 *
 * A uniform three even where a given shape reads only two: the count has to
 * agree across vm_count_slots, vm_cost_rep and the emitter, and a
 * per-preference rule would put that agreement in three places instead of one.
 * All three are written ONCE per loop ENTRY, never per iteration, which is the
 * property this whole rung exists for. */
static int vm_slot_rev(Vm *v, int loop, int which)
{
    return 2 * (v->ngroups + 1) + v->nguard_total + v->nlow_total
         + v->nmark_total + 3 * loop + which;
}

/* [ENG-BREP counter-K] the ITERATION COUNTER, one slot per counter loop, the
 * fifth and last slot class. Sits above the revdet block for the same reason
 * every class above sits above the one before it: the base is computed from
 * the TOTALS the pre-pass found, never from the running assignment counters,
 * so an emitter that assigns its Nth counter cannot land on a slot the
 * pre-pass had earmarked for something else.
 *
 * ONE slot, not the revdet rung's three: this loop's bounds are compile-time
 * constants (m, NOPT and K are all known when the C is written), so nothing
 * needs a low-water mark or a ceiling recorded at run time. The counter is the
 * only run-time quantity the shape has. */
/* [M6-READ] THE SLOT LEGEND. Requirement (5) applied to the one place in a VM
 * artifact where a bare number is an IDENTITY rather than an index: the slot
 * array. `RX_SET(2, ...)` says nothing; `RX_SET(RX_SLOT_GROUP1_START, ...)`
 * says everything, and the macro resolves to the same 2 -- engineering note
 * (i)'s "state names via macros/enums resolving to the same values", so the
 * object code cannot move.
 *
 * The classification is the SAME arithmetic vm_slot_guard/low/mark/rev/ctr use
 * above, read backwards. It is deliberately not a second table: a slot's
 * meaning is decided by the layout, and a parallel list would be a second
 * source of truth about it -- which is how a slot two live loops share gets
 * emitted (this file's own warning, at vm_counter_rung).
 *
 * Writes the SUFFIX only; the caller prefixes. Returns false for a slot the
 * layout does not account for, which is a bug rather than a naming gap, so the
 * caller falls back to the bare number rather than inventing a name. */
static bool vm_slot_name(Vm *v, int slot, char *buf, size_t bufsz)
{
    int ngroup_slots = 2 * (v->ngroups + 1);
    int base_guard   = ngroup_slots;
    int base_low     = base_guard + v->nguard_total;
    int base_mark    = base_low   + v->nlow_total;
    int base_rev     = base_mark  + v->nmark_total;
    int base_ctr     = base_rev   + 3 * v->nrev_total;

    if (slot < 0) return false;
    if (slot < ngroup_slots) {
        int g = slot / 2;
        const char *half = (slot % 2) ? "END" : "START";
        if (g == 0) snprintf(buf, bufsz, "SLOT_WHOLE_%s", half);
        else        snprintf(buf, bufsz, "SLOT_GROUP%d_%s", g, half);
        return true;
    }
    if (slot < base_low) {
        snprintf(buf, bufsz, "SLOT_EMPTY_GUARD%d", slot - base_guard);
        return true;
    }
    if (slot < base_mark) {
        snprintf(buf, bufsz, "SLOT_SPAN_LOW%d", slot - base_low);
        return true;
    }
    if (slot < base_rev) {
        snprintf(buf, bufsz, "SLOT_CUT_MARK%d", slot - base_mark);
        return true;
    }
    if (slot < base_ctr) {
        static const char *which[3] = { "ENTRY", "LOW", "HI" };
        int off = slot - base_rev;
        snprintf(buf, bufsz, "SLOT_REVDET%d_%s", off / 3, which[off % 3]);
        return true;
    }
    if (slot < base_ctr + v->nctr_total) {
        snprintf(buf, bufsz, "SLOT_COUNTER%d", slot - base_ctr);
        return true;
    }
    /* [M6.5.2] the pending block, named by its GROUP rather than by its index
     * — `SLOT_GROUP3_PENDING` beside `SLOT_GROUP3_START`/`_END` is what makes
     * publish-at-close readable in the artifact. The search is over `pend_of`,
     * the same map the emitter writes through, so a name here cannot describe
     * a slot the emitter uses for something else. */
    int base_pend     = base_ctr  + v->nctr_total;
    int base_lookmark = base_pend + v->npend_total;
    int base_lookpos  = base_lookmark + v->nlookmark_total;
    if (slot < base_lookmark) {
        int off = slot - base_pend;
        for (int g = 1; g <= v->ngroups; g++)
            if (v->pend_of && v->pend_of[g] == off) {
                snprintf(buf, bufsz, "SLOT_GROUP%d_PENDING", g);
                return true;
            }
        return false;
    }
    /* [M6.6.2] the lookaround's two families, at the TOP of the layout. The
     * bound above is what keeps the pending search from claiming them: before
     * this module every slot past the counters WAS a pending slot, and an
     * unbounded search would have named a LOOK slot "not accounted for" and
     * silently fallen back to the bare number. */
    if (slot < base_lookpos) {
        snprintf(buf, bufsz, "SLOT_LOOK_MARK%d", slot - base_lookmark);
        return true;
    }
    if (slot < base_lookpos + v->nlookpos_total) {
        snprintf(buf, bufsz, "SLOT_LOOK_POS%d", slot - base_lookpos);
        return true;
    }
    return false;
}

/* [M6-READ] The slot as it is WRITTEN IN THE ARTIFACT: the legend macro when
 * the layout accounts for the slot, the bare number when it does not. One
 * helper, so every site that names a slot inside an emitted expression spells
 * it the same way `vm_set` does — the alternative is each site re-deriving
 * `<PREFIX>_` + `vm_slot_name`, which is three spellings of one convention. */
static void vm_slot_expr(Vm *v, int slot, char *buf, size_t bufsz)
{
    /* Sized from what it holds — `up` is at most 80 bytes and `vm_slot_name`
     * writes at most 48 — because a silently TRUNCATED slot name is an
     * artifact that names the wrong cell, and this file has already been bitten
     * once by a too-small snprintf buffer (see the listing's VE_SET arm). */
    char nm[48];
    if (vm_slot_name(v, slot, nm, sizeof nm))
        snprintf(buf, bufsz, "%s_%s", v->up, nm);
    else
        snprintf(buf, bufsz, "%d", slot);
}

static int vm_slot_ctr(Vm *v, int i)
{
    return 2 * (v->ngroups + 1) + v->nguard_total + v->nlow_total
         + v->nmark_total + 3 * v->nrev_total + i;
}

/* [M6.5.2] THE SIXTH SLOT CLASS: one PENDING slot per MARKED group — a group
 * some backreference in this pattern names (backrefs_design.md §3.2.4).
 *
 * WHAT IT IS FOR. `A_CAP` used to WRITE ON TRAVERSE: the start slot at the
 * opening position, the end slot at the closing one. On iteration n > 1 of a
 * quantified group that leaves `slot_values[2k]` holding iteration n's start
 * and `slot_values[2k+1]` holding iteration n-1's END — neither is
 * `PCREC_UNSET`, so an "is it set" test passes on a pair that is NOT A CAPTURE.
 * `(a|b\1)+` on "ab" is libpcre2 (0,1) with group 1 = (0,1); the
 * write-on-traverse model answers (0,2) with group 1 = (1,2). Worse,
 * `^(?:(a|b\1)y)+` on "aybay" leaves `ref_s = 2 > ref_e = 1`, so the emitted
 * `(size_t)(ref_e - ref_start)` underflows to `SIZE_MAX` and the compare reads
 * out of bounds — K27's class, in a matcher someone else compiles.
 *
 * SO THE OPENING POSITION GOES HERE and the (start, end) PAIR is published
 * TOGETHER at the closing position. A backreference then reads only PUBLISHED
 * pairs, and "published" means "some iteration of this group COMPLETED", which
 * is exactly what libpcre2's reference sees. MEASURED arm-vs-arm over 5,808
 * cells in one simulator differing only in publication discipline:
 * publish-at-open gives 138 divergences and 40 reversed spans, publish-at-close
 * 0 and 0; a backref-FREE control population is 0/0 in BOTH, which is what
 * licenses scoping the change to marked groups instead of rewriting capture
 * semantics for every pattern pcrec compiles.
 *
 * IT SITS AT THE TOP OF THE LAYOUT, above the counters, so every base below it
 * is unmoved and a backref-free artifact's slot numbering is untouched.
 * Sabotage row S103 restores publish-at-open; S104 marks only one member
 * of a duplicated name's run. */
static int vm_slot_pend(Vm *v, int group)
{
    return 2 * (v->ngroups + 1) + v->nguard_total + v->nlow_total
         + v->nmark_total + 3 * v->nrev_total + v->nctr_total
         + v->pend_of[group];
}

/* [M6.6.2] THE SEVENTH AND EIGHTH SLOT CLASSES: a lookaround's CUT MARK (the
 * resume-stack depth at the assertion's entry, what `RX_CUT` truncates back
 * to) and its SAVED CURSOR (the position `L_ok` puts `scan_position` back to).
 *
 * They sit ABOVE the pending block, so every base below is unmoved: a pattern
 * with no lookaround gets exactly the slot numbering it got before this
 * module, which is what makes the identity gate's FREE bucket a real claim
 * rather than a tautology.
 *
 * TWO SEPARATE FAMILIES rather than a two-slot stride, because the shapes do
 * not all take both — §3.3's table:
 *
 *   (?=X)  positive lookahead    mark YES  pos YES
 *   (?!X)  negative lookahead    mark YES  pos NO   (P7: the pushed frame
 *                                                    restores the cursor)
 *   (?*X)  non-atomic lookahead  mark NO   pos YES  (nothing is cut)
 *   (?<=X) positive lookbehind   mark YES  pos YES  (wave D)
 *   (?<!X) negative lookbehind   mark YES  pos YES  (the end-check still
 *                                                    compares against entry)
 *   (?<*X) non-atomic lookbehind mark NO   pos YES  (wave D)
 *
 * A stride of two would allocate slots no shape writes, and §3.6's "no mark
 * slot is allocated for a non-atomic form" would stop being observable. */
static int vm_slot_lookmark(Vm *v, int i)
{
    return 2 * (v->ngroups + 1) + v->nguard_total + v->nlow_total
         + v->nmark_total + 3 * v->nrev_total + v->nctr_total
         + v->npend_total + i;
}
static int vm_slot_lookpos(Vm *v, int i)
{
    return 2 * (v->ngroups + 1) + v->nguard_total + v->nlow_total
         + v->nmark_total + 3 * v->nrev_total + v->nctr_total
         + v->npend_total + v->nlookmark_total + i;
}

/* [M6.6.2] WHICH SLOTS THIS LOOKAROUND TAKES — the table above as two
 * predicates, and they are predicates for the reason `vm_marked` and
 * `vm_is_counter` are: `vm_count_slots` and `vm_look` MUST agree exactly, and
 * a rule each of them re-derives is a rule one of them will eventually derive
 * differently. Under-counting here is not a missed optimisation — it is
 * `vm_slot_lookmark(v, v->nlookmark++)` past `RX_NSLOTS`, an out-of-bounds
 * write in EMITTED code, K27's class. */
static bool vm_look_needs_mark(const Ast *a)
{
    /* Something is CUT exactly when the assertion commits: the atomic forms
     * commit to the body's first success, and EVERY negative form commits on
     * body success (§3.3's `L_body_won` cut is not an optimisation — without
     * it a failing assertion leaves a live choice point that later resumes at
     * `L_neg_ok` and proceeds AS IF the assertion had held). There is no
     * non-atomic negative spelling in PCRE2 at all (§2.1: `(*nanla:` is err
     * 195), so `neg` implies a cut with no third case to consider. */
    return a->u.look.atomic || a->u.look.neg;
}
static bool vm_look_needs_pos(const Ast *a)
{
    /* The cursor has to be RESTORED from a slot unless something else already
     * restores it. For a negative LOOKAHEAD nothing does the restoring but the
     * fail label's own pop of the `L_neg_ok` frame, which records
     * `scan_position` at push time — P7, §3.3's finding, and the reason that
     * form needs no snapshot machinery. A negative LOOKBEHIND still needs the
     * slot even though the restore is free, because §3.4's END-CHECK compares
     * the body's finishing position against the ENTRY position (wave D). */
    return !a->u.look.neg || a->u.look.behind;
}

/* Is group `g` MARKED — does some backreference in this pattern name it? ONE
 * predicate, read at the four sites that must agree (the cost analysis, the
 * slot count, `A_CAP`'s emission and the slot legend), for the reason
 * src/gen/CLAUDE.md states about `vm_cursor_fits`: a fact three sites each
 * re-derive is a fact one of them will eventually derive differently. */
static bool vm_marked(const Vm *v, int group)
{
    return v->pend_of && group > 0 && group <= v->ngroups
        && v->pend_of[group] >= 0;
}

/* [ENG-BREP counter-K] Does this quantifier take the COUNTER rung, and is the
 * shape the one implemented so far?
 *
 * ONE predicate, called from all three sites that must agree — vm_cost_rep,
 * vm_count_slots and vm_rep's real emission — for the reason src/gen/CLAUDE.md
 * states about `vm_cursor_fits`: a rung decided by three separate readings of
 * "does this look like a counter loop" is a rung that will eventually be
 * emitted by one of them and not costed by another, and the failure mode is a
 * slot two live loops share.
 *
 * SCOPE: §3.1's mandatory phase AND §3.2/§3.3's optional phase, greedy and
 * lazy. The POSSESSIVE arm (§3.4) is a separate slice and still falls through
 * to the frames rung, as does any unbounded tail.
 *
 * THE THRESHOLD IS PER PHASE, and that is deliberate rather than a shortcut:
 * K is a threshold on emitted SIZE and the two phases contribute to it
 * independently, so `{20,22}` counts its mandatory half and replicates its two
 * optional copies. A single whole-quantifier test would either unroll two
 * copies for nothing or leave twenty replicated.
 *
 * THE STRICTNESS IS §3.2's [R25 E3] and it is structural, not arithmetic. A
 * phase's trip guard is `slot_values[ctr] + K > count` evaluated at ctr = 0, so at
 * count < K it takes the tail immediately and the tail emits all `count`
 * copies — which for the optional phase IS `vm_opt_chain`, so the emission is
 * byte-identical to the frames rung by construction. At count == K the loop
 * RUNS one trip: the same NUMBER of copies as replication, not the same CODE.
 * So byte-identity holds at K > count and nowhere else. */
static bool vm_counter_fits(const Vm *v, const Ast *a)
{
    if (v->cx->opt->flags & PCREC_NO_COUNTER) return false;
    if (a->u.rep.rmin == 0 && a->u.rep.rmax == 0) return false;
    /* UNBOUNDED: only the MANDATORY prefix is the counter's (§11 residual 1).
     * The tail stays on the frames star, which already emits one body copy and
     * has nothing to gain. `X*` and `X+` therefore never reach this rung —
     * their rmin is 0 or 1 — while `X{4000,}` does, and before this clause it
     * did not: it replicated 4,001 mandatory copies and was REFUSED while
     * `X{4000}` compiled. §8.5 cell 3 names both spellings. */
    if (a->u.rep.rmax < 0) return a->u.rep.rmin >= v->unroll_k;
    return a->u.rep.rmin >= v->unroll_k
        || (a->u.rep.rmax - a->u.rep.rmin) >= v->unroll_k;
}

/* How many times the counter rung EMITS the body for an exact count: K copies
 * inside the trip, plus the `m mod K` residue copies in the tail. This is the
 * number that replaces `m` everywhere the frames rung would have replicated,
 * and it is what makes `((a)|ab){4000}` compile — 8 copies where the frames
 * rung wanted four thousand. Shared by the emitter and both pre-passes so the
 * three cannot disagree about how much body there is. */
static int vm_counter_copies(const Vm *v, const Ast *a, bool cuts)
{
    const int K = v->unroll_k;
    const int m = a->u.rep.rmin, nopt = a->u.rep.rmax - a->u.rep.rmin;
    const int mand = (m >= K ? K + m % K : m);
    if (a->u.rep.rmax < 0) return mand + 1;   /* + the star's own single body copy */
    /* The POSSESSIVE optional phase has NO trip, NO tail and NO K [R25 E6]:
     * it is ONE emitted body re-entered per iteration, because the cut at each
     * iteration boundary is what the shape buys and unrolling buys nothing on
     * top of it. That is also why §8.5's byte-identity cell is scoped away
     * from this arm — a possessified repeat cannot satisfy it at any --unroll. */
    /* [M6.4.2] `cuts`, not `a->u.rep.possessive`: a LIFTED semantic possessive takes
     * the same single re-entered body, and a copy count that disagreed with
     * emission would size PCREC_MAX_VM_REPEAT_COPIES against the wrong tree. */
    if (cuts) return mand + (nopt >= K ? 1 : nopt);
    return mand + (nopt >= K ? K + nopt % K : nopt);
}

/* ---- AST predicates ------------------------------------------------------*/

static const Ast *bare(const Ast *a)
{
    while (a->k == A_CAP) a = a->l;
    return a;
}

/* §3.3: a quantifier whose body can match the empty string must not loop
 * forever. Nullability is the compile-time property that decides whether the
 * guard is emitted at all. */
static bool vm_nullable(const Ast *a)
{
    /* A_CAT and A_ALT spines are walked ITERATIVELY, not recursed on. That is
     * R1's R-2 hardening and D10/DD-10's rule, and this function violated it
     * until a 20,000-character literal SEGFAULTED pcrec at the default 8 MB
     * stack (`(aaa...)`, no special flag — measured, and the threshold tracks
     * `ulimit -s`, which is what identifies it as stack exhaustion rather than
     * anything subtler). src/ir/nfa.c's compile_ast flattens for exactly this
     * reason and says so; three functions in this file did not, and this is
     * one of them. The recursion that REMAINS is on a spine node's RIGHT
     * child, whose own depth is bounded by the parser's group-nesting cap. */
    for (;;) {
        switch (a->k) {
        case A_CLASS: return false;
        case A_EMPTY: case A_BOL: case A_EOL: case A_END: return true;
        /* [M6.2 wave B] zero-width, hence nullable. [M6.2 wave D] `\G` too.
         * NULLABLE is about the BYTES a node can consume, not about whether
         * it can succeed — an assertion that fails still consumes nothing. */
        /* [M6.2 wave E] `\K` is nullable in the strongest sense in this
         * switch: it is not merely a test that consumes nothing, it is an
         * epsilon (src/ir/nfa.c). */
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET: return true;
        /* [M6.5.2] TRUE, and getting it wrong is a HANG rather than a wrong
         * answer. A referenced group can publish an EMPTY capture, and the
         * reference then consumes nothing: `^(x?)y\1z$` on "yz" is (0,2) with
         * group 1 = (0,0), and `^(a?)\1{3}$` matches "" at (0,0). Answering
         * false here would let a nullable quantifier body lose its
         * empty-iteration guard, and `(\1)*` would loop forever on a
         * zero-width iteration. Sabotage row S107, whose detector is the
         * harness's derived timeout rather than a wrong span. */
        case A_BREF: return true;
        /* [M6.6.2] TRUE, AND GETTING IT WRONG IS A BUDGET BURN RATHER THAN A
         * WRONG SPAN — which makes it the arm most likely to be written by
         * reflex and least likely to be caught by a corpus reading answers.
         *
         * A lookaround consumes nothing on EVERY path, whatever its body is:
         * that is the construct's definition (keep the verdict, throw the
         * position away), and it is why `pcrec_minw` and `pcrec_maxw` both
         * answer 0. `false` here would deny the empty-iteration guard to a
         * quantifier above one, and design §2.6 measured that quantified
         * lookaround SHIPS — all fourteen forms compile in both oracles, and
         * `^(?=a)*a$`, `^(?:(?=a))*a$`, `^(?:(?=a)|b)*a$`, `^(?:(?!x))*a$`
         * and `^(?:(?=(a)))*a$` all answer in 0.0000s and agree with python.
         * That is only true because the guard is there.
         *
         * WHAT THE FAILURE LOOKS LIKE, stated because "it hangs" is the
         * intuitive and wrong answer (design §9.3, R33 C2-14): every VM
         * artifact carries a step budget by default and `--fno-step-budget` is
         * the only opt-out, so the lost guard BURNS the budget and returns
         * PCREC_ERR_STEPS. A harness that only compares spans scores that as
         * an error rather than as a mismatch, which is what sabotage row
         * S-LA9's detector has to be written to notice.
         *
         * NOT TRANSPARENT, unlike A_ATOMIC below: this answer does not depend
         * on the body at all. A lookaround whose body consumes bytes still
         * consumes none itself. */
        case A_LOOK: return true;
        /* [DD-14] TRUE, AND IT IS A DELIBERATELY INCOMPLETE PLACEHOLDER — the
         * SOUND bottom of this predicate, not its answer. Read the whole
         * comment before touching it.
         *
         * THE TRUE ANSWER IS "nullable iff the callee is" (design §2.6/§4.4a
         * site 1), and it is a FIXPOINT over the SCC-condensed call graph,
         * memoised, with cycle bottom `false` iterated upward. THIS
         * SIGNATURE CANNOT EXPRESS IT: `vm_nullable` is a bare `const Ast *`
         * walker with no context and no visited set, so following
         * `u.call.body` would recurse for ever on `(a(?1))` and HANG THE
         * COMPILER (design §4.4). The fixpoint is `src/opt/callgraph.c`'s
         * (wave B+C) and this arm will read its memo.
         *
         * WHY `true` AND NOT THE FIXPOINT'S OWN BOTTOM. The cycle bottom
         * `false` is correct INSIDE the iteration, where a later round can
         * raise it; standing alone as a placeholder it is the UNSOUND
         * direction — `false` denies the empty-iteration guard to a
         * quantifier above a NULLABLE callee, and design §2.6 measured that
         * `(?(DEFINE)(?<g>a?))(?&g)*` on "aaa" is (0,3) and
         * `(?(DEFINE)(?<g>))(?&g)*` on "" is (0,0), i.e. both TERMINATE on
         * 10.46 only because something bounds the empty iteration. `true`
         * keeps the guard, which costs a slot and a test on a call that never
         * needed one and can never lose a match. `A_BREF`'s arm above takes
         * the same direction for the same reason.
         *
         * IT IS UNREACHABLE IN THIS WAVE — nothing produces an `A_CALL` — and
         * `vm_emit`'s own arm is a hard `ctx_fail`, which is what makes
         * landing it incomplete safe rather than merely quiet. Wave B+C
         * replaces it in the same edit that builds the graph.
         *
         * DESIGN §2.6's FURTHER RULING RIDES ON THIS ARM and is NOT
         * discharged by it: the POSSESSIVE rung (`vm_poss_star`) emits no
         * empty-iteration guard and fires no work charge at all, so a
         * nullable callee routed there loops at zero consumption for ever.
         * What keeps that unreachable is the RUNG DECLINES, in
         * `src/opt/possessify.c`'s `pss_walk` and `src/opt/revdet.c`'s
         * `rd_shape` — not this answer. THOSE ARE S-SR9a's ROW; THIS ARM IS
         * S-SR9's, which returns `false` here and predicts the step budget
         * ending the search on `^(?(DEFINE)(?<g>a?))(?&g)*$` rather than a
         * wrong span — so its detector must notice an ERROR, not a
         * mismatch. */
        /* [DD-14 wave B+C] THE FIXPOINT'S ANSWER, READ OFF THE NODE.
         *
         * §2.6: a call is nullable iff its CALLEE is, and that is a fixpoint
         * over the call graph with cycle bottom `false` iterated UP — measured
         * on 10.46, where a NULLABLE callee (`(?&g)*` with `g` = `a?`) and an
         * EMPTY one both TERMINATE under `*`, i.e. something bounds the empty
         * iteration and this answer is what emits it.
         *
         * THE FIELD'S POLARITY IS INVERTED AND THAT IS THE WHOLE POINT.
         * `u.call.nonnullable` reads FALSE from the arena, so an un-run
         * fixpoint answers NULLABLE — the guard is emitted, which costs a slot
         * and a test and can never lose a match. The other polarity's zero
         * would DROP the guard on a nullable callee and hang the emitted
         * matcher, which is the direction wave A2's `return true` placeholder
         * was chosen to avoid and the reason the field is not simply
         * `nullable`. `pcrec_emit_vm` runs the fixpoint before the first
         * consumer; the polarity is what makes that ordering a performance
         * property rather than a correctness one.
         *
         * DESIGN §2.6's FURTHER RULING RIDES ON THIS ARM and is NOT discharged
         * by it: `vm_poss_star` emits no empty-iteration guard and fires no
         * work charge, so a nullable callee routed onto the possessive rung
         * loops at zero consumption for ever. What keeps that unreachable is
         * the RUNG DECLINE in `src/opt/possessify.c` (D71.6) — S-SR9a's row.
         * This arm is S-SR9's. */
        case A_CALL: return !a->u.call.nonnullable;
        case A_CAP:   a = a->l; continue;
        /* [M6.4.2] TRANSPARENT: the cut removes MATCHES, never BYTES, so
         * `(?>X)` can match empty exactly when `X` can. `(?>)` is legal and
         * matches empty (measured: (0,0) on "abc"), and `(?>a*)*b` must get the
         * empty-iteration guard for the same reason `(?:a*)*b` does — the star
         * above it is what iterates, and this answer is what tells it so. */
        case A_ATOMIC: a = a->l; continue;
        case A_REP:   if (a->u.rep.rmin == 0) return true; a = a->l; continue;
        case A_CAT:
            /* nullable iff EVERY element is */
            while (a->k == A_CAT) {
                if (!vm_nullable(a->r)) return false;
                a = a->l;
            }
            continue;
        case A_ALT:
            /* nullable iff ANY branch is */
            while (a->k == A_ALT) {
                if (vm_nullable(a->r)) return true;
                a = a->l;
            }
            continue;
        }
        return true;
    }
}

/* ---- [M6.4.2] THE ATOMIC LIFT: two predicates, five callers ---------------
 *
 * `(?>X q)` and `X q+` are the same construct (parse.c desugars the suffix to
 * `A_ATOMIC(A_REP(X))`), and the naive lowering — vm_atomic's general shape
 * around an ordinary quantifier — costs `RX_RESUME_FRAMES` where the SAME
 * language spelled `a*+` costs one frame: `vm_star` pushes one frame per
 * iteration and the cut only reclaims them at the group's exit. So an
 * `A_ATOMIC` whose child is an `A_REP` LIFTS its cut into that quantifier's own
 * possessive rung, which cuts per iteration.
 *
 * THE LIFT IS NOT FREE, AND THE R31 PANEL REFUTED THE CLAIM THAT IT IS TWICE,
 * THE SAME WAY BOTH TIMES. The possessive rungs' shape is licensed by
 * eng_brep_design.md §2.2's verdict, and each licence is a separate CONJUNCT
 * of that verdict which a USER-WRITTEN possessive deletes:
 *
 *   - `vm_poss_star` HAS NO EMPTY-ITERATION GUARD, and says so, because §2.2
 *     refuses to possessify a NULLABLE body at all. `(?>(?:a*)*)b` is legal in
 *     both oracles and has one; routed onto that rung the emitted matcher
 *     PUSHES AND CUTS AT ZERO CONSUMPTION FOREVER, and no work charge fires to
 *     stop it. Sabotage row S100's expected result is a TIMEOUT.
 *   - THE POSSESSIVE RUNGS ARE GREEDY-ONLY BY SIGNATURE — `vm_opt_chain` takes
 *     `bool greedy`, `vm_poss_chain`/`vm_poss_star`/`vm_counter_poss_opt` do
 *     not and never read it, and `vm_cursor_rep`'s possessive scan is
 *     unconditionally maximal — because :2053-2062 argues the PREFERENCE
 *     COLLAPSE as a §2.2 consequence: under disjointness both preferences land
 *     on the maximal exit. `(?>a*?)b` has no §2.2 verdict and its lazy exit is
 *     NOT the maximal one. MEASURED: 7 of 8 lift-eligible lazy cells
 *     miscompile — `(?>a*?)b` on "aaab" is (3,4) in BOTH oracles and (0,4)
 *     through the lift. Sabotage row S99.
 *
 * §14 item 9 records the shape rather than the two instances: this claim has
 * been refuted twice the same way, so the enumeration of §2.2 consequences the
 * emitted shapes depend on is EMPIRICAL and may be incomplete. The systematic
 * version — read §2.2's conjuncts and ask of EACH which emitted shape depends
 * on it — is what found the third one, the RUNG'S OWN GATE (`vm_rev_canmove`'s
 * exact-count clause), which is condition (d) at that function.
 *
 * SO THE LIFT'S SCOPE IS GREEDY, NON-NULLABLE `A_REP` BODIES, CHECKED HERE AND
 * ASSERTED AGAIN AT EACH RUNG'S OWN ENTRY. Everything else takes the general
 * shape, which is correct for every body and merely more expensive. */
static bool vm_lifts(const Ast *a)
{
    const Ast *r = a->l;
    if (r->k != A_REP)     return false;   /* the lift is an A_REP shape */
    if (!r->u.rep.greedy)        return false;   /* carve-out TWO  (§3.2.2a) */
    if (vm_nullable(r->l)) return false;   /* carve-out ONE  (§3.2.2)  */
    return true;
}

/* DOES THIS `A_REP` EMIT A CUT? The ONE predicate the emitter and all four
 * pre-passes call instead of reading `->u.rep.possessive` — src/gen/CLAUDE.md's
 * one-call-one-truth rule, and `vm_cut`'s own header gives the precedent (the
 * work charge became a primitive because "the charge has THREE emission sites
 * in two different spellings" and a probe missed one).
 *
 * IT MUST BE ONE PREDICATE BECAUSE THE PRE-PASSES ARE NOT ADVISORY. `->
 * possessive` is read at 23 sites over 8 functions, three of them pre-passes
 * that must agree with emission EXACTLY or the artifact is malformed rather
 * than merely slow: `vm_count_slots` allocates the cut-mark slot (a lift it
 * cannot see runs `vm_slot_mark(v, v->nmark++)` past `RX_NSLOTS` — an
 * OUT-OF-BOUNDS WRITE IN EMITTED CODE, K27's class), `vm_cost_rep` computes
 * the frame and trail budgets from the possessive branch, and `vm_counter_
 * copies` decides how many body copies exist. Sabotage row S98.
 *
 * `vm_rev_canmove` is the SHARPEST of the four and the reason this is a
 * predicate rather than a convention: it returns `!a->u.rep.possessive && ...`, so a
 * lifted possessive read through the raw field is handed a RETREAT FRAME and
 * CAN GIVE BACK — the uncut semantics, silently. §6.5's `rd_shape` decline
 * closes the plain-group case and cannot reach this one, because `rd_shape`
 * sees the `A_REP`, not the `A_ATOMIC` above it.
 *
 * THREADED, NOT STORED, and that is a correctness choice rather than an
 * elegant one (D67's corollary, R31 re-check N2). `struct Ast` has no parent
 * pointer and the pre-passes are independent descents from the root, so a node
 * cannot ask whether it is under an `A_ATOMIC`; the obvious alternative is a
 * `lifted` flag written at parse time, and it goes STALE — under
 * `-fno-possessify` the free discharge RUNS and `run_possessify` DOES NOT, so
 * a flag left behind by a deleted `A_ATOMIC` would cut a loop the flag was
 * passed to leave uncut. Threading has no state a rewrite can leave behind,
 * because the answer is recomputed from the shape that is actually there.
 *
 * `under_atomic` is a ONE-LEVEL EDGE PROPERTY: true only for the `A_REP` that
 * is the DIRECT child of a lifting `A_ATOMIC`, false everywhere inside that
 * quantifier's body. A greedy `A_REP` containing a lazy one is closed by that
 * definition rather than by a special case — measured `(?>(?:a*?b)*)d` at
 * RUNGS 0x5 / STRATS 0x3, the outer collapse not leaking inward. */
static bool vm_cuts(const Ast *a, bool under_atomic)
{
    return a->u.rep.possessive || under_atomic;
}

/* DOES THIS `A_REP` TAKE THE REVERSE-DETERMINISTIC RUNG? `a->u.rep.revbody` is
 * src/opt/revdet.c's verdict AND the material the backward walk is emitted
 * from, so it was read directly at three sites — the emitter, `vm_cost_rep` and
 * `vm_count_slots`. [M6.4.2] adds a SECOND condition, so it becomes a
 * predicate, on `vm_counter_fits`'s own precedent ("the one shared predicate
 * the two pre-passes also call, never a second reading of the same
 * conditions").
 *
 * THE SECOND CONDITION IS RULE 3's (d), and putting it at only ONE of the three
 * sites is a MEASURED defect rather than a tidiness argument. With the decline
 * in `vm_rep` alone, `pcrec --engine=vm --no-captures -fno-possessify
 * '(?>(?:a|bc){2})d'` emitted an artifact whose pre-pass had allocated three
 * REVDET slots and no mark while the emitter took the FRAMES rung and asked for
 * a mark — so `RX_SET(RX_SLOT_REVDET0_ENTRY, resume_depth)` and `RX_CUT(2)`
 * both landed on the revdet loop's OWN entry slot. That is exactly the
 * two-live-loops-share-one-slot failure `vm_count_slots`' header names, and
 * exactly why E4 asked for one named predicate rather than three agreeing
 * readings.
 *
 * See `vm_rev_canmove` for what condition (d) IS and why (a), (b) and (c) do
 * not imply it. The population is measured EMPTY at the default flags —
 * `rd_shape`'s gate is strictly stronger than §2.2's on everything
 * constructible, so a revdet-approved exact-count body is always possessified
 * too — and `-fno-possessify` is what makes the branch live, since the
 * discharge and the lift both run while `run_possessify` does not. */
static bool vm_revdet_fits(const Ast *a, bool under_atomic)
{
    if (!a->u.rep.revbody) return false;
    if (under_atomic && !a->u.rep.possessive && a->u.rep.rmax >= 0 && a->u.rep.rmin == a->u.rep.rmax)
        return false;
    return true;
}

/* ---- the class pool -----------------------------------------------------*/

static int vm_cls(Vm *v, const uint8_t *bits)
{
    for (int i = 0; i < v->ncls; i++)
        if (memcmp(v->cls[i], bits, 32) == 0) return i;
    if (v->ncls == v->clscap) {
        int ncap = v->clscap ? v->clscap * 2 : 16;
        uint8_t (*nv)[32] = arena_alloc(&v->cx->arena, (size_t)ncap * 32);
        if (v->ncls) memcpy(nv, v->cls, (size_t)v->ncls * 32);
        v->cls = nv;
        v->clscap = ncap;
    }
    memcpy(v->cls[v->ncls], bits, 32);
    return v->ncls++;
}

/* The membership test for class `ci` on byte expression `byte`.
 *
 * Three shapes, cheapest first, and the choice is a property of the SET, not a
 * heuristic: a singleton is one compare, a contiguous range is the standard
 * unsigned-subtract trick (one subtract, one compare, no branch), and anything
 * else reads the 32-byte bitmap. A full 256-byte set needs no test at all
 * beyond the caller's own bounds check. The bitmap is the same 256-bit
 * representation the AST and the DFA already use (§2.9), so nothing here has
 * to agree with a second encoding of "which bytes". */
static void vm_cls_test(Vm *v, StrBuf *b, int ci, const char *byte)
{
    const uint8_t *bits = v->cls[ci];
    int lo = -1, hi = -1, count = 0;
    for (int c = 0; c < 256; c++)
        if (cls_has(bits, (unsigned)c)) { if (lo < 0) lo = c; hi = c; count++; }

    if (count == 256) { sb_puts(b, "1"); return; }
    if (count == 1)   { sb_printf(b, "%s == %d", byte, lo); return; }
    if (count == hi - lo + 1) {
        sb_printf(b, "(unsigned)(%s - %d) <= %du", byte, lo, hi - lo);
        return;
    }
    sb_printf(b, "(%s_class_bitmap%d[(%s) >> 3] >> ((%s) & 7)) & 1", v->p, ci, byte, byte);
}

/* ---- §2.5's cursor ladder: is this body a deterministic fixed-length run? --
 *
 * Returns the body's length in bytes (>= 1) and fills `out` with its class
 * sequence, or 0 when the body does not qualify.
 *
 * WHY THIS RUNG IS NOT OPTIONAL. §2.5's STRUCTURAL note: a quantified SIMPLE
 * item must not push one frame per iteration, because an 8 MB `a*` cannot
 * store 8 M frames in an allocation-free matcher. So this is not a speed
 * optimization that could be deferred to M4.6 — without it the VM cannot run
 * `a*` on a long subject at all.
 *
 * EXACTNESS CONDITION (§2.5): determinism plus fixed length give any consumed
 * run a UNIQUE decomposition into iterations, so every retreat position is a
 * real iteration boundary and no other exists. A choice-bearing body like
 * `(a|bc)` breaks the constant stride and falls back to frames — which is why
 * A_ALT is rejected here even when its branches happen to have equal length:
 * equal length is not determinism, and the capture spans D44.1 derives from
 * the cursor would be wrong for the branch not taken.
 *
 * D44.1 EXTENDS the rung to CAPTURE-BEARING bodies, which §2.5 as originally
 * written excluded by definition (a capture write needs an RX_SET call, which
 * a plain span loop never makes) — so every capture-bearing quantifier fell
 * back to one frame PER ITERATION regardless of whether its body was actually
 * deterministic, which is where the panel's measured Θ(n) working set came
 * from. Here A_CAP is transparent to the length computation and its group's
 * span is DERIVED FROM THE CURSOR at loop exit instead (see vm_cap_offsets),
 * so a deterministic capture-bearing body allocates no per-iteration frame
 * AND no per-iteration trail entry.
 *
 * THE RUNGS THIS DOES NOT IMPLEMENT, named so they are not mistaken for
 * oversights: disjoint-follow auto-possessification (§6.3 schedules it at
 * M4.6 with the island work it shares an analysis with), the
 * reverse-deterministic backwards walk, and the boundary-record rung. Each is
 * a strict improvement over falling back to frames, none is needed for
 * correctness, and the last two need a per-quantifier reversed automaton this
 * milestone has no other customer for. */
static int vm_det_seq(const Ast *a, const uint8_t **out, int cap)
{
    a = bare(a);
    switch (a->k) {
    case A_CLASS:
        if (cap < 1) return 0;
        out[0] = a->u.cls.bits;
        return 1;
    case A_CAT: {
        int nl = vm_det_seq(a->l, out, cap);
        if (nl == 0) return 0;
        int nr = vm_det_seq(a->r, out + nl, cap - nl);
        if (nr == 0) return 0;
        return nl + nr;
    }
    case A_REP: {
        /* A fixed count is still deterministic: `(?:ab){2}` is a 4-byte run.
         * Anything else — a range, or unbounded — is a choice point. */
        if (a->u.rep.rmin != a->u.rep.rmax || a->u.rep.rmin <= 0) return 0;
        int total = 0;
        for (int i = 0; i < a->u.rep.rmin; i++) {
            int nl = vm_det_seq(a->l, out + total, cap - total);
            if (nl == 0) return 0;
            total += nl;
        }
        return total;
    }
    default:
        /* A_ALT (choice), A_EMPTY (zero length), A_BOL/A_EOL (zero-width
         * assertions, which would make "scan ahead by stride" wrong).
         *
         * [M6.2 wave C] ONE OF §8.3's FOUR `default:` SITES, inspected for
         * `Ast.u.anch.multiline` awareness and needing none: this DECLINES on the
         * kind, and a `$` is zero-width under either spelling. The full
         * inspection is recorded at the field (src/core/internal.h).
         *
         * [M6.6.2] RE-INSPECTED FOR `A_LOOK` and SOUND UNCHANGED, for the
         * sentence directly above: a lookaround is ZERO-WIDTH, so "scan ahead
         * by stride" is wrong for it exactly as it is for `$`, and declining
         * on the kind is the right answer without reading a field. This is
         * also the site that GATES the next one — `vm_cap_offsets` runs only
         * on a body this function approved.
         *
         * [DD-14] RE-INSPECTED BY HAND FOR `A_CALL`, one of design §4.4a's
         * four `default:`-carrying sites (its site 2), and SOUND WITH NO ARM
         * ADDED — recorded here because `-Wswitch` will not name this switch.
         * A call is not a STRIDE: its width is the callee's, unbounded for a
         * recursive one, and not a compile-time fact at all without the call
         * graph. `return 0` IS the decline and it is the answer a correct arm
         * would have written, so an explicit `case A_CALL:` here would be a
         * restatement rather than a decision. The decline is also what keeps
         * this function's own gate honest for the next two sites: a
         * call-bearing body is never `vm_det_seq`-approved, which is what
         * makes `vm_cap_offsets`' and the cursor rung's declines
         * unreachable rather than merely correct. */
        return 0;
    }
}

/* For the D44.1 extension: every capturing group inside a deterministic
 * fixed-length body, with its byte offset and length RELATIVE to the
 * iteration start. Returns the count, or -1 if more than `cap` were found. */
typedef struct { int group, off, len; } CapOff;

static int vm_cap_offsets(const Ast *a, int base, CapOff *out, int *n, int cap)
{
    switch (a->k) {
    case A_CLASS: return base + 1;
    case A_CAP: {
        int end = vm_cap_offsets(a->l, base, out, n, cap);
        if (end < 0) return -1;
        if (*n >= cap) return -1;
        out[*n].group = a->u.cap.no;
        out[*n].off = base;
        out[*n].len = end - base;
        (*n)++;
        return end;
    }
    case A_CAT: {
        int mid = vm_cap_offsets(a->l, base, out, n, cap);
        if (mid < 0) return -1;
        return vm_cap_offsets(a->r, mid, out, n, cap);
    }
    case A_REP: {
        int at = base;
        for (int i = 0; i < a->u.rep.rmin; i++) {
            at = vm_cap_offsets(a->l, at, out, n, cap);
            if (at < 0) return -1;
        }
        return at;
    }
    default:
        /* [M6.6.2] RE-INSPECTED FOR `A_LOOK`, the third of design §11's four
         * `default:`-carrying sites. SOUND, and GATED by the row above: `-1`
         * IS the decline, and this runs only on a body `vm_det_seq` already
         * approved — which it cannot be with a lookaround in it, since that
         * function declines on the kind. Both halves hold independently.
         *
         * [DD-14] RE-INSPECTED BY HAND FOR `A_CALL` (design §4.4a site 3) and
         * SOUND WITH NO ARM ADDED, both halves again and independently: `-1`
         * IS the decline the design's table asks for, and a call-bearing body
         * cannot be `vm_det_seq`-approved because that function declines on
         * the kind one site up. Note this walk computes byte OFFSETS relative
         * to the iteration start — a quantity a call does not have, since its
         * width is the callee's — so declining is the only answer available
         * as well as the right one. */
        return -1;   /* unreachable for a vm_det_seq-approved body */
    }
}

/* THE RUNG DECISION, in ONE place (§2.5's ladder, D44.1's extension).
 *
 * Three call sites need it and they MUST agree: the slot counter (which sizes
 * `slot_values` before anything is emitted), the capacity analysis (which sizes the
 * two arrays and stamps the ceiling), and the emitter itself. Two of them
 * disagreeing does not produce a diagnostic — it produces a matcher whose
 * arrays are sized for a shape it does not have.
 *
 * It returns false when the body is not deterministic-fixed-length, AND when
 * its captures overflow `VM_MAX_BODY_CAPS`. The second condition is not a
 * tidiness bound: the cursor rung writes each group's span from the cursor at
 * loop exit, so a group the offset table could not hold would simply never be
 * written and would report UNSET on a match it participated in — a silent
 * wrong span, the one failure mode this project's compatibility standard
 * refuses outright. Falling back to the frames rung costs frames and is
 * always correct. */
static bool vm_cursor_fits(const Ast *rep, const uint8_t **seq, int *stride,
                           CapOff *caps, int *ncaps)
{
    int n = 0;
    int len = vm_det_seq(rep->l, seq, VM_MAX_STRIDE);
    if (len <= 0) return false;
    if (vm_cap_offsets(rep->l, 0, caps, &n, VM_MAX_BODY_CAPS) < 0) return false;
    *stride = len;
    *ncaps = n;
    return true;
}

/* ---- §2.5's REVERSE-DETERMINISTIC rung: the two facts every site needs ----
 *
 * The VERDICT itself is not computed here: src/opt/revdet.c decides it and
 * leaves the body's REVERSED AST on `Ast.u.rep.revbody`, non-NULL exactly when the
 * rung applies. That is deliberate — the rung has three call sites that must
 * agree (the slot counter, the capacity analysis and the emitter) and the
 * cursor rung's own history is that a condition read three times is a condition
 * that can drift. One field, read three times, cannot.
 *
 * These two helpers are the DERIVED facts the three sites still share.
 *
 * `vm_rev_canmove`: whether the loop owes a resume frame at all. It does not
 * when it CUTS (no retreat is reachable) and it does not at an EXACT count
 * (there is one exit, so top and bottom of §2.3's chain are the same
 * position). Both cases still run the backward walk when the body has groups,
 * because the captures still have to be derived.
 *
 * [M6.4.2] THE FIRST CLAUSE READS `vm_cuts`, AND THIS IS THE SHARPEST OF THE
 * FOUR PRE-PASS SITES (R31 E4). Under RULE 2 the module never writes
 * `Ast.u.rep.possessive`, so a LIFTED possessive read through the raw field gets
 * `!a->u.rep.possessive == true` here, is handed a retreat frame, and CAN GIVE BACK
 * — answering the UNCUT language, silently. `rd_shape`'s decline (§6.5) closes
 * the plain-group case and structurally cannot reach this one: it sees the
 * `A_REP`, never the `A_ATOMIC` above it.
 *
 * THE SECOND CLAUSE IS RULE 3's CONDITION (d), AND IT IS NOT IMPLIED BY THE
 * OTHER THREE (r31eng's final finding). (a) cut-equivalence, (b)
 * preference-preservation and (c) nullable-safety are properties of the BODY;
 * a lift also inherits whatever gate the RUNG it lands on applies to itself,
 * and those gates were written for a population §2.2 had already filtered.
 * "There is one exit at an exact count" is a (U1)/(U2) UNIQUE-ITERATION
 * statement that consults no verdict, and for a body §2.2 REJECTS at
 * `rmin == rmax` it is false.
 *
 * MEASURED EMPTY TODAY, and that is why it is a comment plus a decline rather
 * than a computation: 14 bodies x 3 exact counts found no body that is
 * revdet-APPROVED and possessify-REJECTED at `rmin == rmax` — `rd_shape`'s
 * gate is strictly stronger than §2.2's on everything constructible
 * (`(?:a|ab){2}c` takes FRAMES_BOUNDED and answers correctly). The
 * NEIGHBOURING cell is NOT empty and the distinction is the point:
 * `(?:ab|cd){2,4}c` IS revdet-approved and possessify-rejected, but `rmax >
 * rmin` there, so `canmove` is true and what would break is the FIRST clause,
 * which `vm_cuts` covers. One clause of one predicate is covered by E4's fix
 * and the other by nothing, which is why (d) is its own condition.
 *
 * THE DECLINE THAT MAKES IT SAFE BY CONSTRUCTION rather than by luck is in
 * `vm_rep`: a LIFTED `A_REP` at an exact count does not take this rung at all.
 * The cell being empty today means that decline costs nothing measurable; the
 * day either gate moves it is what keeps the answer right. */
static bool vm_rev_canmove(const Ast *a, bool cuts)
{
    return !cuts && (a->u.rep.rmax < 0 || a->u.rep.rmax > a->u.rep.rmin);
}

/* `vm_rev_caps`: the body's capturing group NUMBERS, in AST order, which is the
 * dense index the emitted recovery locals are addressed by. One number per
 * A_CAP node and not per emitted instance — a fixed-count repeat around a group
 * emits it several times and they all share one number and one pair of slots
 * (revdet.c's shape scan counts the same way, which is what keeps its
 * PCREC_MAX_REVDET_BODY_GROUPS bound meaning the same thing this array's size
 * means). */
static void vm_rev_caps(const Ast *a, int *out, int *n, int cap)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        /* [M6.2 wave E] `\K` carries no capture NUMBER, so it contributes
         * nothing to this dense index. It is also unreachable here — this
         * runs only on a revdet-approved body and src/opt/revdet.c's shape
         * scan declines every body carrying a `\K`, for a reason that is this
         * function's own subject matter: the rung recovers capture values by
         * a backward walk over iteration boundaries, and a `\K` position is
         * not on that lattice. */
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        /* [M6.5.2] carries no capture NUMBER and is UNREACHABLE for `\K`'s
         * reason: `rd_shape` declines every body holding a backreference,
         * because there is no reversed spelling of "compare against what group
         * k captured". */
        case A_BREF:
        /* [DD-14] DECLINES, joining `A_BREF` and `A_ATOMIC`: it carries no
         * capture NUMBER of its own, and it is UNREACHABLE for their reason —
         * `rd_shape` (src/opt/revdet.c) declines every body holding a call.
         * RETURNING rather than reaching the callee is what keeps this dense
         * index a faithful mirror of what `rd_shape` counted: a group number
         * this walk found through `u.call.body` but `rd_shape` never saw would
         * shift every later entry and address the wrong recovery local. */
        case A_CALL:
        /* [M6.4.2] UNREACHABLE, and it declines rather than descending. This
         * runs only on a revdet-APPROVED body, and `rd_shape` (src/opt/revdet.c)
         * declines every body containing an `A_ATOMIC` — an atomic group is not
         * reversal-invariant, because its cut is defined relative to the
         * FORWARD priority order. Returning (rather than walking into the body)
         * keeps this dense index a faithful mirror of what `rd_shape` counted:
         * a group number this walk invented but `rd_shape` never saw would
         * break the correspondence PCREC_MAX_REVDET_BODY_GROUPS rests on.
         *
         * [M6.6.2] A LOOKAROUND JOINS IT, same arm and same reason one step
         * further out: `rd_shape` declines every body containing one (a
         * lookaround has no reversed spelling at all — its body runs FORWARD
         * even for a lookbehind, design §3.5), so this is unreachable, and
         * returning rather than walking into the body keeps this dense index a
         * faithful mirror of what `rd_shape` counted. A group number this walk
         * invented from inside a lookaround body would break exactly the
         * correspondence named above. */
        case A_LOOK:
        case A_ATOMIC:
            return;
        case A_CAP:
            if (*n < cap) out[(*n)++] = a->u.cap.no;
            a = a->l;
            continue;
        case A_REP:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) { vm_rev_caps(a->r, out, n, cap); a = a->l; }
            continue;
        case A_ALT:
            while (a->k == A_ALT) { vm_rev_caps(a->r, out, n, cap); a = a->l; }
            continue;
        }
        return;
    }
}

/* ---- capacity analysis (§2.5's two capacities, §4.5's SECOND bound) -------
 *
 * Two bounds, two errors, and they are different failures with different
 * diagnoses (§4.5): a pattern can overflow the frame array in a handful of
 * steps (`((a)|b){0,10000}` on a long subject) and a pattern can burn the step
 * budget with a two-frame stack (`(a*)b`).
 *
 * `unbounded` marks the residual class D44.1 names: quantifier bodies that are
 * NOT provably single-path, whose depth grows with the subject. For those the
 * artifact carries an HONEST STAMPED CEILING rather than silently capping at
 * whatever the default array size happens to be — a caller can then know the
 * limit without discovering it by triggering PCREC_ERR_FRAMES.
 *
 * Conservative in the safe direction throughout: over-estimating cost lowers
 * the stamped ceiling, which under-promises rather than over-promises. */
struct Cost {
    long long frames, trail;  /* max simultaneously live (bounded part) */
    long long pf, pt;         /* per-ITERATION frames/trail of the outermost
                               * growing quantifier — the divisor the stamped
                               * ceiling is computed from. Read as per-byte,
                               * which is the conservative direction: an
                               * iteration consumes at least one byte unless the
                               * body is nullable, and a nullable body's loop is
                               * stopped by the empty-iteration guard after one
                               * such iteration (S3.3). */
    bool      unbounded;      /* depth grows without a static bound */
    bool      growable;       /* depth grows WITH the subject at all — true for
                               * `unbounded`, and ALSO for a bounded repeat
                               * whose count is large. The two are stamped the
                               * same way and the distinction only decides
                               * whether the EXACT requirement is worth trying
                               * to honour. */
};

static Cost vm_cost(Vm *v, const Ast *a, bool under_atomic);

/* [M6.4.2] `under_atomic` is threaded, never stored — see vm_cuts(). It is
 * TRUE only for the A_REP that is the direct child of a LIFTING A_ATOMIC. */
static Cost vm_cost_rep(Vm *v, const Ast *a, bool under_atomic)
{
    const bool cuts = vm_cuts(a, under_atomic);
    const uint8_t *seq[VM_MAX_STRIDE];
    CapOff caps[VM_MAX_BODY_CAPS];
    int stride = 0, nc = 0;
    Cost c = { 0, 0, 0, 0, false, false };

    if (a->u.rep.rmin == 0 && a->u.rep.rmax == 0) return c;

    /* [ENG-BREP] The REVERSE-DETERMINISTIC arm is taken BEFORE the body's cost
     * is computed, because on this rung the body is costed with capture writes
     * SUPPRESSED and that changes the number. The ladder order is the emitter's
     * (vm_rep): cursor first, then this, then frames.
     *
     * THE HEADLINE IS `pf = 0`. Frames do not grow with the iteration count —
     * the scan cuts the body's choice points at every iteration boundary and
     * the whole loop owes ONE resume frame — so an artifact whose only growing
     * quantifier is on this rung declares no subject ceiling at all, where the
     * frames rung declared one per iteration.
     *
     * The TRAIL still can grow, and saying so is the honest half (the same
     * honesty the possessive arm below already carries). Suppressed captures
     * cost nothing per iteration, so a body like `((a)|b)` grows nothing; a
     * body containing a nested quantifier that owns slots of its own still
     * writes them once per iteration, and that case earns a real ceiling from a
     * real per-iteration divisor. */
    /* [ENG-BREP counter-K] §3.1's mandatory phase, costed BEFORE the frames
     * arm for the same ladder-order reason the revdet arm below is.
     *
     * FRAMES ARE NOT WHAT THIS RUNG SHRINKS, and the note owes that plainly
     * (§3.5, [R25 E7]). The rung shrinks emitted SIZE; the frame requirement is
     * whatever the body needs, times the iterations that can be live at once.
     * The mandatory phase pushes nothing of its own — a mandatory copy that
     * fails fails the quantifier — but the BODY's choice points are still live
     * across all m iterations, exactly as under replication, because nothing
     * cuts between mandatory copies. So the requirement is per-ITERATION and
     * counted over m, not over the K + residue copies the emitter writes.
     *
     * Counting the EMITTED copies here instead of the ITERATIONS would be a
     * silent cap of precisely the kind the revdet arm below records finding the
     * hard way: the artifact would size for 8 iterations and take 4000. */
    if (!vm_cursor_fits(a, seq, &stride, caps, &nc)
        && !vm_revdet_fits(a, under_atomic)
        && vm_counter_fits(v, a)) {
        Cost body = vm_cost(v, a->l, false);
        const long long K = v->unroll_k;
        const long long mm = a->u.rep.rmin;
        if (a->u.rep.rmax < 0) {
            /* UNBOUNDED: only the mandatory prefix is the counter's, so this
             * is the frames rung's own unbounded arm plus the counter's trail
             * writes. Computing `rmax - rmin` here would be -1 - m, a negative
             * count that made the frame requirement garbage and returned
             * RX_ERR_FRAMES on every subject — found by writing §8.5 cell 3's
             * `{4000,}` member as a check the moment the emitter accepted it. */
            c.unbounded = c.growable = true;
            c.pf = 1 + body.frames + body.pf;
            c.pt = (vm_nullable(a->l) ? 1 : 0) + body.trail + body.pt;
            c.frames = mm * body.frames;
            c.trail  = mm * body.trail + (mm >= K ? 1 + mm / K : 0);
            return c;
        }
        const long long nn = a->u.rep.rmax - a->u.rep.rmin;
        /* Frames and trail are the frames rung's OWN numbers, and they must
         * be: the rung changes how much C is WRITTEN, not how many iterations
         * RUN or what they push. This is the frames arm's bounded expression
         * verbatim — mandatory copies contribute the body only, optional
         * copies contribute a loop frame each as well. If these lines ever
         * diverge from the frames arm below, one of them is wrong. */
        if (cuts) {
            /* Possessified, the frame requirement stops depending on the
             * iteration count entirely — the cut at every iteration boundary
             * keeps ONE loop frame live at a time — so this mirrors the frames
             * rung's own possessive arm rather than the bounded one. The TRAIL
             * still depends on the count, because the cut deliberately does not
             * rewind it, and saying so is the honest half. */
            /* THE TWO PHASES' PEAKS ADD; they do not max. The frames rung's
             * own possessive arm takes the max, and copying that here was a
             * SILENT CAP measured by §8.1's differential: `((a)|bc){9,20}d` on
             * twelve 'a's returned RX_ERR_FRAMES where replication matched.
             *
             * The reason is an ordering the max reading assumes away. The cut
             * mark is recorded BEFORE the mandatory copies, and nothing cuts
             * between them, so all `mm * body.frames` mandatory frames are
             * still live when the optional loop pushes its stop frame and
             * enters its body. Only the cut at the END of that first optional
             * iteration discards them. So the peak is during optional
             * iteration 1, with both phases resident at once — and after it,
             * exactly one frame survives, which is what the rung buys.
             *
             * Over-counting here costs capacity; under-counting is a wrong
             * answer on a subject the artifact should have matched. */
            long long peak_mandatory = mm * body.frames;
            long long peak_loop      = 1 + body.frames;
            c.frames = peak_mandatory + peak_loop;
            c.trail  = (mm + nn) * body.trail
                     + 1                                  /* the cut mark */
                     + (mm >= K ? 1 + mm / K : 0)
                     + (nn >= K ? 1 + nn : 0);            /* +1 per iteration */
            c.pf     = body.pf;
            c.pt     = 1 + body.trail + body.pt;
            c.unbounded = body.unbounded;
            c.growable  = true;
            return c;
        }
        c.frames = mm * body.frames + nn * (1 + body.frames);
        c.trail  = (mm + nn) * body.trail
                 /* the counter: an init plus one write per TRIP, per PHASE
                  * that actually runs a loop. A phase below K replicates and
                  * writes the counter not at all. */
                 + (mm >= K ? 1 + mm / K : 0)
                 + (nn >= K ? 1 + nn / K : 0);
        /* The per-iteration divisors the ceiling machinery uses. Taken from
         * the frames arm for the same reason, with the counter rounded UP from
         * its true 1/K to 1: over-counting here tightens a stamped ceiling,
         * while under-counting is a SILENT CAP — the failure the revdet arm
         * below records finding the hard way, and the asymmetry that decides
         * which way to round when the honest number is fractional. */
        c.pf     = 1 + body.frames + body.pf;
        c.pt     = 1 + body.trail + body.pt;
        c.unbounded = body.unbounded;
        c.growable  = true;
        return c;
    }

    if (!vm_cursor_fits(a, seq, &stride, caps, &nc)
        && vm_revdet_fits(a, under_atomic)) {
        const bool move = vm_rev_canmove(a, cuts);
        int grp[PCREC_MAX_REVDET_BODY_GROUPS];
        int ng = 0;
        Cost body;
        vm_rev_caps(a->l, grp, &ng, PCREC_MAX_REVDET_BODY_GROUPS);
        v->nocap++;
        body = vm_cost(v, a->l, false);
        v->nocap--;
        c.frames = 1 + body.frames + (move ? 1 : 0);
        c.pf     = 0;
        /* THE TRAIL ACCUMULATES ACROSS ITERATIONS AND THE FRAMES DO NOT, and
         * the asymmetry is the cut's doing: the scan discards the body's frames
         * at every boundary and deliberately does NOT rewind its trail (the
         * same rule vm_cut carries, for the same reason — a failure OUTSIDE the
         * loop still has to restore what the loop wrote). So a body that owns
         * any trailed slot of its own pays for it once per ITERATION.
         *
         * Counting one iteration's worth here was this arm's first version and
         * it is a SILENT CAP, which is the one failure mode this analysis
         * exists to prevent. MEASURED: `(?:x((a)|b){2}y){0,3}z`'s body contains
         * a possessified exact-count repeat, whose cut mark is one trailed
         * write per entry, so three outer iterations need three of them — and
         * the artifact stamped a capacity for one and returned RX_ERR_FRAMES on
         * "xabyxabyxaayz", a subject it should answer. Caught by this rung's
         * own .rxt corpus on the run that added the nested-repeat family.
         *
         * Capture writes inside the body are SUPPRESSED on this rung, so the
         * common case has `periter == 0` and nothing accumulates at all — which
         * is why the defect needed a body with a nested quantifier owning a
         * slot to show up. */
        {
            const long long periter = body.trail + body.pt;
            const long long base = 3 + 2 * (long long)ng;
            c.pt = periter;
            if (a->u.rep.rmax >= 0) {
                c.trail = base + (long long)a->u.rep.rmax * periter;
                c.unbounded = body.unbounded;
            } else {
                /* No static iteration bound, so no exact requirement exists
                 * when the body writes anything: the ceiling machinery takes
                 * over from `pt`. */
                c.trail = base + periter;
                c.unbounded = body.unbounded || periter > 0;
            }
            c.growable = body.growable || c.unbounded || periter > 0;
        }
        return c;
    }

    Cost body = vm_cost(v, a->l, false);

    if (vm_cursor_fits(a, seq, &stride, caps, &nc)) {
        /* cursor rung: ONE live frame ever, one low-water write per entry,
         * plus one write per capture in the body per (re)try — all of which
         * the resume frame's own mark rewinds, so they do not accumulate.
         *
         * [ENG-BREP] Possessified, the frame and the low-water write are both
         * gone (vm_cursor_rep's possessive path emits neither), so the honest
         * requirement is zero frames and the capture writes alone. This is
         * where §7's "those artifacts newly stamp no limit truthfully" comes
         * from: an artifact whose every quantifier is possessified reports a
         * frame requirement of 0, and pcrec_emit_vm's `fits` test then finds
         * nothing to declare a ceiling for. Under-reporting here would be a
         * silent cap, so the branch has to mirror the emitter exactly. */
        c.frames = cuts ? 0 : 1;
        c.trail  = (cuts ? 0 : 1) + (v->nocap ? 0 : 2 * nc);
        return c;
    }

    /* [ENG-BREP] the possessified frames rung, both bounds in one arm because
     * the whole point is that the two now cost the same: ONE loop frame is
     * live at a time (vm_poss_chain / vm_poss_star cut back to the mark at
     * every copy boundary), so the frame requirement stops depending on the
     * iteration count entirely.
     *
     * The TRAIL still does depend on it, and saying so is the honest half. The
     * cut discards frames and deliberately does not rewind the trail, so a
     * body that writes captures still adds entries per iteration. That is why
     * `growable` is decided on the trail here rather than assumed false: for a
     * capture-free body nothing grows and the artifact stamps "no limit"
     * truthfully (§7's prediction), while for a capture-bearing one the
     * ceiling machinery still has a real per-iteration divisor to work from —
     * just no longer a frames one. */
    if (cuts) {
        long long peak_mandatory = (long long)a->u.rep.rmin * body.frames;
        long long peak_loop      = 1 + body.frames;
        c.frames = peak_mandatory > peak_loop ? peak_mandatory : peak_loop;
        c.trail  = 1 + (a->u.rep.rmax < 0 ? (long long)a->u.rep.rmin
                                    : (long long)a->u.rep.rmax) * body.trail;
        c.pf     = body.pf;                    /* frames: NOT per iteration */
        c.pt     = body.trail + body.pt;       /* trail: still per iteration */
        {
            bool grows = body.unbounded || body.growable || c.pt > 0;
            c.unbounded = a->u.rep.rmax < 0 ? grows : body.unbounded;
            c.growable  = a->u.rep.rmax < 0 ? grows : (body.growable || c.pt > 0);
        }
        return c;
    }

    if (a->u.rep.rmax < 0) {
        /* frames rung, unbounded: one frame per iteration, and an iteration
         * that consumes nothing terminates the loop (§3.3's guard), so every
         * completed iteration but the last consumes at least one byte. */
        c.unbounded = c.growable = true;
        c.pf = 1 + body.frames + body.pf;
        c.pt = (vm_nullable(a->l) ? 1 : 0) + body.trail + body.pt;
        c.frames = (long long)a->u.rep.rmin * body.frames;
        c.trail = (long long)a->u.rep.rmin * body.trail;
        return c;
    }

    /* frames rung, bounded: rmin mandatory copies plus (rmax - rmin) nested
     * optionals, each optional contributing its own live frame (§3.3's RULED
     * replication reading — a bounded quantifier compiles as its copies, with
     * no guard slot and no suppression test at all).
     *
     * `growable` is set here too, and that is the point of the flag. A bounded
     * repeat's requirement IS statically known — but "statically known" and
     * "fits the emitted array" are different claims, and `((a)|b){0,4000}c`
     * satisfies the first and not the second. Stamping subject_ceiling = 0
     * ("not applicable") for such an artifact says there is no limit when
     * there is one, which is exactly the silent cap D44.1's honest stamp
     * exists to replace. The per-iteration costs below let pcrec_emit_vm
     * stamp a real ceiling whenever the requirement does not fit. */
    c.frames = (long long)a->u.rep.rmin * body.frames
             + (long long)(a->u.rep.rmax - a->u.rep.rmin) * (1 + body.frames);
    c.trail = (long long)a->u.rep.rmax * body.trail;
    c.unbounded = body.unbounded;
    c.growable = true;
    c.pf = 1 + body.frames + body.pf;
    c.pt = body.trail + body.pt;
    return c;
}

static Cost vm_cost(Vm *v, const Ast *a, bool under_atomic)
{
    Cost c = { 0, 0, 0, 0, false, false };
    switch (a->k) {
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    /* [M6.2 wave B] one emitted test, no frame, no slot, no trail entry --
     * the same cost every other assertion arm has. [M6.2 wave D] `\G` is
     * one more comparison against a parameter, so the same nothing. */
    case A_WORDB: case A_NWORDB: case A_GSTART:
        return c;
    /* [M6.2 wave E] `\K` IS THE ONE ASSERTION-FAMILY NODE THAT IS NOT FREE
     * HERE, and getting this arm wrong is not a missed optimisation.
     *
     * Every kind on the line above emits a test and nothing else. `\K` emits
     * `<PREFIX>_SET(0, pos)`, which is a TRAIL ENTRY — one slot save, so the
     * write can be undone exactly when a backtrack passes back over it. If
     * this arm returned the zero Cost, `trail_frames` would be sized one
     * entry short per `\K` on the deepest path and the artifact would answer
     * PCREC_ERR_FRAMES on a pattern it can match. Inside a quantifier the
     * multiplication is A_REP's, exactly as it is for A_CAP's two entries.
     *
     * It allocates no SLOT and vm_count_slots says so: slot 0 is group 0's
     * start, which `slot_values` has always reserved and nothing has ever written.
     *
     * `v->nocap` is not consulted, unlike A_CAP below, and the reason is
     * structural rather than an omission: `nocap` is set only inside a
     * reverse-deterministic body's forward scan, and src/opt/revdet.c
     * declines every body containing a `\K`. There is no state of the
     * emitter in which this write is suppressed. */
    case A_KRESET:
        c.trail = 1;
        return c;
    /* [M6.5.2] THE ZERO ARM, and it is worth saying why the construct that
     * LOOKS expensive is the one that costs nothing here.
     *
     * A backreference writes no slot, pushes no frame and creates no choice
     * point: for a given state there is exactly one length it can consume, so
     * `vm_alt` is not involved and neither capacity moves. What this module
     * costs in capacity is entirely `A_CAP`'s — one extra trailed write per
     * MARKED group per traverse, the arm below — which is the opposite of
     * where a first reading puts it.
     *
     * The compare's byte-by-byte work is charged against the WORK budget at
     * the emission site instead (§3.8), because that is per-SUBJECT work the
     * fail label never sees, which is exactly what that budget meters and not
     * what this analysis sizes. */
    case A_BREF:
        return c;
    case A_CAP:
        c = vm_cost(v, a->l, false);
        /* [ENG-BREP] no trail entry while capture writes are suppressed —
         * vm_emit's own A_CAP arm reads the same flag, so the cost and the
         * emitted code cannot disagree about whether the write happens.
         *
         * [M6.5.2] THREE for a MARKED group, two for every other: publish-at-
         * close writes the pending slot at the open and BOTH published slots
         * at the close. `vm_emit`'s A_CAP arm reads the same `vm_marked`
         * predicate, so the number the trail array is sized from and the
         * number of writes the artifact makes are one decision, not two. */
        if (!v->nocap) c.trail += vm_marked(v, a->u.cap.no) ? 3 : 2;
        return c;
    case A_CAT: {
        /* Spine walked ITERATIVELY (R1 R-2 / D10) — see vm_nullable's comment
         * for the segfault that says why. The accumulation order reproduces
         * the recursive definition exactly: A_CAT sums both sides, so summing
         * along the spine is the same number. */
        const Ast *t = a;
        while (t->k == A_CAT) {
            Cost r = vm_cost(v, t->r, false);
            c.frames += r.frames;
            c.trail  += r.trail;
            c.pf     += r.pf;
            c.pt     += r.pt;
            c.unbounded = c.unbounded || r.unbounded;
            c.growable  = c.growable  || r.growable;
            t = t->l;
        }
        {
            Cost h = vm_cost(v, t, false);
            c.frames += h.frames;
            c.trail  += h.trail;
            c.pf     += h.pf;
            c.pt     += h.pt;
            c.unbounded = c.unbounded || h.unbounded;
            c.growable  = c.growable  || h.growable;
        }
        return c;
    }
    case A_ALT: {
        /* The chain shape keeps exactly ONE alternation frame live at a time
         * (see vm_alt), and a failed branch's own frames are popped before the
         * next branch runs — so this is max-plus-one, not a sum.
         *
         * Iterative, and the fold is INNERMOST-FIRST because that is the shape
         * the recursion had: a flat alternation is a LEFT-NESTED chain, so
         * `1 + max` applied at each node accumulates outward. Folding in any
         * other order would silently change the number this function reports,
         * which is what sizes the frame array. */
        int nbr = 1;
        for (const Ast *t = a; t->k == A_ALT; t = t->l) nbr++;
        const Ast **br = arena_alloc(&v->cx->arena, (size_t)nbr * sizeof(Ast *));
        int i = nbr;
        const Ast *t = a;
        while (t->k == A_ALT) { br[--i] = t->r; t = t->l; }
        br[0] = t;

        c = vm_cost(v, br[0], false);
        for (int j = 1; j < nbr; j++) {
            Cost r = vm_cost(v, br[j], false);
            c.frames = 1 + (c.frames > r.frames ? c.frames : r.frames);
            c.trail  = c.trail > r.trail ? c.trail : r.trail;
            c.pf     = c.pf > r.pf ? c.pf : r.pf;
            c.pt     = c.pt > r.pt ? c.pt : r.pt;
            c.unbounded = c.unbounded || r.unbounded;
            c.growable  = c.growable  || r.growable;
        }
        return c;
    }
    case A_REP:
        return vm_cost_rep(v, a, under_atomic);
    /* [M6.4.2] R31 C10, and "no new give-up code; the caps are unchanged" was
     * WRONG. The atomic group's mark is written with `vm_set`, which is the
     * TRAILED writer — that is what makes NESTING and RE-ENTRY work (an outer
     * backtrack restores the mark and the entry label re-sets it) — so an
     * A_ATOMIC inside a quantifier costs ONE TRAIL ENTRY PER ENTRY TO THE
     * GROUP. Inside a repeat the multiplication is A_REP's, exactly as it is
     * for A_CAP's two entries.
     *
     * AN UNCHARGED TRAILED WRITE IS THE DEFECT `tests/mech/sabotages/
     * S87_kreset_trail_uncharged.sh` already guards one construct over: the
     * artifact sizes `trail_frames` one entry short per group on the deepest
     * path and answers PCREC_ERR_FRAMES on a subject it can match. Sabotage
     * row S95 is this module's own, and it needs its OWN row because the
     * answers do not change — only the stamped `subject_ceiling` moves.
     *
     * A LIFTED group charges NOTHING here: its cut mark is the RUNG's, already
     * counted by `vm_cost_rep`'s possessive arms, and charging again would
     * double-count. FRAMES are the body's either way — the group pushes none
     * of its own, and the body's are live until the cut.
     *
     * One STRUCTURAL consequence worth knowing, reported rather than fixed:
     * because the cut discards frames and NOT trail entries, a capture-bearing
     * atomic body under a quantifier (`(?>(a))*`) makes the TRAIL the binding
     * cap where FRAMES normally binds first. That is a shift in which cap
     * fires, not a new failure mode, and rx_info's stamped `subject_ceiling`
     * reports it honestly either way. */
    case A_ATOMIC:
        if (vm_lifts(a)) return vm_cost(v, a->l, true);
        c = vm_cost(v, a->l, false);
        c.trail += 1;
        return c;
    /* [M6.6.2] THE BODY'S COST PLUS ONE FRAME AND TWO TRAIL ENTRIES, and the
     * three numbers are three separate claims about design §3.2/§3.3's shape:
     *
     *   frames += 1   the NEGATIVE form pushes a resume frame BEFORE the body
     *                 (§3.3, and sabotage row S-LA4 moves the push after it),
     *                 so a lookaround's own frame is not zero the way an
     *                 atomic group's is. Charged for BOTH polarities rather
     *                 than read off `.neg`: see below.
     *   trail  += 2   one for the cut's mark, exactly as A_ATOMIC charges
     *                 (`RX_CUT` on the atomic spellings), and one for the
     *                 cursor SAVE — `slot_values[POS] = scan_position`, the
     *                 write §3.2 restores from and sabotage row S-LA2 drops.
     *                 A trailed write that is not charged sizes `trail_frames`
     *                 short on the deepest path and answers PCREC_ERR_FRAMES
     *                 on a subject the artifact can match; S87 is the standing
     *                 guard for that failure on another construct.
     *
     * IT DOES NOT READ `.neg` OR `.atomic`, ON PURPOSE, and that is the
     * decision rather than an oversight. This analysis is documented as
     * "conservative in the safe direction throughout: over-estimating cost
     * lowers the stamped ceiling, which under-promises rather than
     * over-promises". Charging the union of what any spelling needs is
     * therefore free in the safe direction, and it keeps design §3.1(a)'s
     * one-reader property intact — the three flags stay read at `vm_look`
     * alone, so there is no second reader to drift and no D62 control 3
     * obligation lands on this file.
     *
     * RE-CHECKED AT WAVE B+C AGAINST `vm_look` AS LANDED, and both constants
     * stand as the safe-direction UNION they were written to be:
     *
     *   frames +1  EXACT for the negative form (its one `L_neg_ok` push) and
     *              an OVER-charge of one for the positive and non-atomic
     *              forms, which push nothing of their own.
     *   trail  +2  EXACT for the positive ATOMIC form (both slot writes are
     *              `vm_set`, i.e. trailed) and an over-charge of one for the
     *              negative form (mark only) and for the non-atomic one
     *              (cursor only). `RX_CUT` adds no trail entry.
     *
     * An over-charge costs a lower stamped `subject_ceiling` and nothing else;
     * an under-charge is the K27-class failure named above.
     *
     * [WAVE D] `+ nbranch` IS THE LOOKBEHIND's OWN FRAMES, and it is read off
     * the WIDTH TABLE's companion count rather than off `.look.behind` — so
     * this analysis still reads NONE of design §3.1(a)'s three flags and
     * `vm_look` remains their single reader. `nbranch` is 0 for a LOOKAHEAD
     * (the parse hook writes the two width fields together and NULL/0 is the
     * lookahead's ANSWER, not a placeholder), so a lookahead's charge is
     * unchanged to the line. For a lookbehind the exact figure is `m - 1` —
     * one retry frame per NON-final branch, all of which the cut discards on
     * success (§3.7) — so `+ m` deliberately over-charges by one, in the
     * direction this whole analysis is documented to err in. */
    case A_LOOK:
        c = vm_cost(v, a->l, false);
        c.frames += 1 + a->u.look.nbranch;
        c.trail  += 2;
        return c;
    /* [DD-14] A LOUD REFUSAL, not a number — this is a GRAPH site (design
     * §4.4a site 5) and the graph is wave B+C's.
     *
     * THE TRUE COST is the callee's, `Cost.unbounded` on a cycle, PLUS this
     * site's own `2 * |W|` of trail: one save and one restore per slot in the
     * callee region's write set (§5.7). Both halves need
     * `src/opt/callgraph.c` — the first is a memoised walk over the SCC
     * condensation, the second reads `u.call.nsave`, which that same pass
     * fills. Neither is derivable here: following `u.call.body` from this
     * function would recurse for ever on a recursive callee, and `nsave` is 0
     * on every node until the pass runs.
     *
     * WHY LOUD RATHER THAN A SAFE BOTTOM. This function HAS a `Ctx`
     * (`v->cx`), which `vm_nullable` and `pcrec_minw` do not, so it can say
     * what is wrong instead of guessing in the safe direction. And there is
     * no cheap safe bottom to guess: the safe direction here is
     * OVER-charging, whose top is `unbounded`, and stamping every
     * call-bearing artifact `unbounded` would silently disable the honest
     * `subject_ceiling` D44.1 exists to publish. An under-charge is worse
     * still — `trail_frames` sized short on the deepest path, answering
     * PCREC_ERR_FRAMES on a subject the pattern matches, which is exactly
     * `S87_kreset_trail_uncharged.sh`'s class.
     *
     * UNREACHABLE IN THIS WAVE: nothing produces an `A_CALL`, and `vm_emit`'s
     * arm is the same hard failure — this arm and that one are what make
     * taking only part of wave B+C impossible. */
    /* [DD-14 wave B+C] THREE CHARGES, and §5.7's own headline is that only
     * the second is new machinery: "nothing new is needed to COUNT a call's
     * work", because the callee is emitted by `vm_emit` and every push, pop
     * and cut inside it goes through the same primitives the fail label's
     * single decrement already sees.
     *
     *   1. THE CALLEE REGION'S OWN COST, read from the per-region memo
     *      `pcrec_emit_vm` computed before this walk. It cannot be computed
     *      here: `vm_cost(v, a->u.call.body, false)` recurses for ever on a
     *      recursive callee, which is design §4.4's hang in the one function
     *      that has a `Ctx` to fail through and therefore the one place where
     *      failing loudly would have been available and still wrong.
     *   2. THE SAVE/RESTORE — `2 * |W|` trail entries per call site, a
     *      compile-time constant (§5.3 property 4). An artifact that
     *      under-sizes `trail_frames` returns PCREC_ERR_FRAMES on a pattern it
     *      can MATCH, which is S87/S95's exact failure mode, and S-SR7 is the
     *      two-site row that pins it against the emission.
     *   3. THE CALL FRAME ITSELF, one resume frame per activation. It is not
     *      popped by the return (§5.1 — the callee's choice points must
     *      survive it, §3.2 MEASURED), so it is LIVE for the whole activation
     *      and belongs in the simultaneous count.
     *
     * A CYCLIC TARGET IS `unbounded` AND `growable`, which is P12's
     * honest-ceiling machinery reused rather than rebuilt: the depth of a
     * recursion is data-dependent by nature, so the artifact stamps a
     * `subject_ceiling` and says what it enforces instead of pretending the
     * limit is not there. `RX_CHARGE_WORK` is NOT used (§5.7): a call
     * discards nothing, and the work counter's customers are cuts and
     * back-steps.
     *
     * THE UN-RUN CASE IS THE SOUND ONE. Before `pcrec_emit_vm` fills the memo
     * there is no `cg` at all, and this arm then charges only the frame and
     * the (zero) saves — but the arm is unreachable in that state, because a
     * tree with an `A_CALL` has a graph by construction (compile.c runs the
     * pass before emission). The guard is written anyway, in the OVER-charging
     * direction, because a cost analysis that reads an absent table should
     * refuse to under-promise rather than trust its caller. */
    case A_CALL: {
        int idx = v->cg ? pcrec_callgraph_index(v->cg, a->u.call.target) : -1;
        if (idx < 0 || !v->rgn_cost) {
            c.frames += 1;
            c.unbounded = c.growable = true;
            return c;
        }
        c = v->rgn_cost[idx];
        c.frames += 1;
        c.trail  += 2LL * a->u.call.nsave;
        if (pcrec_callgraph_reaches(v->cg, idx, idx))
            c.unbounded = c.growable = true;
        return c;
    }
    }
    return c;
}

/* ---- slot counting (must mirror the emitter's own rung decisions) --------*/

/* Counts slot_values slots AND emitted resume points, in one walk that mirrors the
 * emitter's own rung decisions and its replication. Both counts have to be
 * exact for the same reason: a slot count that under-counts makes two live
 * loops share one slot, and a resume-point count that under-counts lets an
 * artifact past the cap that the cap exists to stop. The push arithmetic
 * matches the emitter site for site — vm_alt pushes nbr-1 for an nbr-branch
 * alternation (which is one per A_ALT node, since a flat alternation is
 * left-nested), vm_cursor_rep pushes 1, the unbounded star pushes 1, and
 * vm_opt_chain pushes one per optional copy. Verified against the emitted
 * `&&label` count over the corpus.
 *
 * [K22] `repl` is the PRODUCT of the replication factors of every frames-rung
 * bounded repeat this call is nested inside — 1 at the root. It exists because
 * this walk is the one place in the compiler that pays the copy tree's full
 * cost before anything bounds it: `PCREC_MAX_VM_REPEAT_COPIES` bounds one
 * quantifier's own factor (a `{0,2}` tower never comes near it) and
 * `PCREC_MAX_VM_NODES` is charged during EMISSION, which this pre-pass runs
 * before. So a depth-40 `{0,2}` tower walked 2^40 nodes here and hung the
 * compiler with no diagnostic. Multiplying the factors down the nesting path
 * and refusing above PCREC_MAX_VM_REPLICATION_PRODUCT costs one multiply per
 * A_REP and turns the hang into the refusal the node cap was always going to
 * produce; see limits.h for why the two share a value and why that makes the
 * check unable to refuse anything that compiles today. */
/* [M6.4.2] `under_atomic` threaded exactly as in vm_cost — see vm_cuts(). A
 * lift this pre-pass cannot see runs `vm_slot_mark(v, v->nmark++)` past
 * `RX_NSLOTS`: an out-of-bounds write in EMITTED code, K27's class. */
static void vm_count_slots(Vm *v, const Ast *a, long long repl,
                           bool under_atomic)
{
    const uint8_t *seq[VM_MAX_STRIDE];
    CapOff caps[VM_MAX_BODY_CAPS];
    int stride = 0, nc = 0;
    switch (a->k) {
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    /* [M6.2 wave E] `\K` allocates NO slot, and that is the mechanism rather
     * than an accident. Its write goes to slot 0 — group 0's start — which
     * `nstate`'s `2 * ncaps` term has reserved since [M4.5b] and which
     * nothing has ever written (`vm_set` for group k uses `2*k`, and k >= 1;
     * every other family bases at `2 * (ngroups + 1)`). Choosing the slot
     * that already MEANS "the reported start" is what makes the trail, the
     * per-search UNSET initialisation and the exact-restore undo apply to
     * `\K` with no new machinery at all. See vm_emit's A_KRESET arm. */
    /* [M6.5.2] allocates NO slot and pushes NO resume point. The PENDING
     * slots publish-at-close needs are not counted here at all: the marked set
     * is a whole-tree property known before this walk starts, so
     * `pcrec_emit_vm` sizes that block from `Vm.npend_total` directly. A
     * counter incremented during the walk would allocate one slot per emitted
     * INSTANCE of a group rather than one per group, which for a fixed-count
     * repeat around a marked group is the "slot two live loops share" failure
     * this file's own warning names. */
    case A_BREF:
    case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        return;
    case A_CAP: vm_count_slots(v, a->l, repl, false); return;
    /* [M6.6.2 wave B+C] THE LOOKAROUND'S OWN SLOTS, AND ITS OWN RESUME POINT,
     * counted here — the arm wave A2 landed deliberately incomplete and this
     * wave completes, in the same edit as `vm_look`.
     *
     * The three lines below mirror `vm_look` site for site and read the SAME
     * two predicates it does, which is the whole reason those predicates
     * exist: an under-count is `vm_slot_lookmark(v, v->nlookmark++)` past
     * `RX_NSLOTS`, an out-of-bounds write in EMITTED code (K27's class), and
     * a missed `npush` lets an artifact past the resume-point cap.
     *
     * `false` is passed for `under_atomic`: a lookaround's cut, when it has
     * one, is the ASSERTION's and not a lift of a quantifier beneath it — the
     * same reading `vm_atomic`'s unlifted branch takes. Descending is
     * required either way, because the body's own groups, marks and resume
     * points are emitted through `vm_emit`. */
    case A_LOOK:
        if (vm_look_needs_mark(a)) v->nlookmark++;
        if (vm_look_needs_pos(a))  v->nlookpos++;
        /* The negative form's ONE extra frame: the "body failed" continuation
         * pushed BEFORE the body (§3.3). The positive and non-atomic forms
         * push nothing of their own. */
        if (a->u.look.neg) v->npush++;
        /* [WAVE D] AND A LOOKBEHIND's PER-BRANCH RETRY FRAMES, one per
         * NON-final branch (§3.4): `vm_look_behind` pushes `&&L_b(i+1)` for
         * every branch but the last, so the count is `nbranch - 1`. EXACT
         * here rather than the safe-direction union `vm_cost` takes, because
         * this walk's under-count is the one that lets an artifact past the
         * resume-point cap. `nbranch` is 0 for a lookahead, so the guard is
         * what keeps `-1` from being charged to one. */
        if (a->u.look.nbranch > 1) v->npush += a->u.look.nbranch - 1;
        vm_count_slots(v, a->l, repl, false);
        return;
    /* [DD-14] A LOUD REFUSAL, and design §4.4c is emphatic that this site is
     * the one whose FIRST answer was wrong: "the first version said LEXICAL
     * ONLY and it was WRONG — the consequence is an out-of-bounds slot
     * write", K27's class and this function's own header warning.
     *
     * THE RULE §4.4c LANDS ON: the layout must account for EVERY EMITTED
     * REGION — each lexical occurrence as today, PLUS one for each emitted
     * callee region — and `W` is computed over the CALLEE REGION's own slot
     * indices. Three separate facts make a lexical count wrong, and each was
     * measured:
     *
     *   1. `X{0}` EMITS NOTHING AND COUNTS NOTHING (this function returns at
     *      its `rmin == 0 && rmax == 0` guard), AND A CALLEE CAN LIVE THERE —
     *      the classic pre-DEFINE idiom. Measured on 10.46:
     *      `^(?:(?<g>a|ab)){0}(?&g)c$` on "abc" is (0,3), and the atomic and
     *      rung-bearing variants match too. So the region the emitter must
     *      produce for the call has slot instances NOTHING COUNTED. Measured
     *      in-pcrec: `^((?>a)){1}b$` allocates 2 cut marks, `^((?>a)){0}b$`
     *      allocates none.
     *   2. The `CALL_LINKAGE` shape emits the callee region SEPARATELY
     *      (§6.3), so it needs its OWN instances. "Double-counting" is the
     *      CORRECT count here, not a bug to avoid.
     *   3. `u.call.save` lists SLOT INDICES, and the lexical copy's and the
     *      callee region's differ. A restore written against the wrong
     *      indices is §5.3b's axis-C miscompile by a second route.
     *
     * SO THIS ARM CANNOT BE WRITTEN WITHOUT `src/opt/callgraph.c`, which
     * knows which groups get an emitted region — and §4.4c adds that this
     * function gains a PARAMETER for "count this subtree as a region even if
     * a `{0,0}` ancestor would prune it". Both are wave B+C's, in the same
     * edit as `vm_emit`'s arm.
     *
     * LOUD BECAUSE THERE IS A `Ctx` AND NO SAFE BOTTOM. Under-counting is an
     * out-of-bounds write in EMITTED code; over-counting by a guess would
     * make `RX_NSLOTS` wrong in the other direction on every artifact.
     * S-SR19 is the detector, and §4.4c records that its cell must carry a
     * RUNG-BEARING or ATOMIC callee — a callee with only capture slots
     * allocates from a family `{0}` does not prune, and the row would go
     * green for the wrong reason.
     *
     * AND EVERY OTHER `LEXICAL ONLY` VERDICT IN THIS WAVE WAS RE-CHECKED
     * AGAINST THAT PRUNE (§4.4c): `dis_walk` (src/opt/atomic.c) and
     * `br_strip_caps` (src/parse/mod_backrefs.c) descend `A_REP`
     * UNCONDITIONALLY — no `{0,0}` guard at all — and the three whole-tree
     * predicates have no prune either, so THIS was the only site affected. */
    /* [DD-14 wave B+C] THE CALL SITE ITSELF ALLOCATES NOTHING AND DESCENDS
     * NOWHERE, and §4.4c's "GRAPH" verdict is discharged ONE LEVEL UP rather
     * than here — which is a simplification of the design and is worth stating
     * as one.
     *
     * §4.4c's rule is "the layout accounts for EVERY EMITTED REGION — each
     * lexical occurrence as today, PLUS one for each emitted callee region".
     * `pcrec_emit_vm` implements exactly that by calling this function ONCE
     * PER REGION, in ascending target order, after the main-body walk — and
     * `vm_emit` then emits the regions in the same order, so the running
     * counters and the pre-pass agree site for site, which is the property
     * this whole function exists to hold. There is nothing left for the arm to
     * do: a call SITE emits a frame push, |W| trailed writes and a `goto`, and
     * not one of them allocates a slot.
     *
     * THAT IS ALSO WHY §4.4c's PROPOSED PARAMETER ("count this subtree as a
     * region even if a `{0,0}` ancestor would prune it") IS NOT HERE. The
     * region walk starts AT the callee's own `A_CAP`, so no `{0,0}` ancestor
     * is on the path at all — the prune this function takes at its `rmin == 0
     * && rmax == 0` guard is in the MAIN-BODY walk, where it is CORRECT
     * (`X{0}` emits nothing lexically and must allocate nothing). The region's
     * slots are counted by the separate call, which is what closes the hole
     * S-SR19 defends: `^(?:((?>a|ab))){0}(?1)z$` allocates the region's cut
     * mark even though the lexical occurrence allocates none.
     *
     * `repl` DOES NOT MULTIPLY A REGION. A call under `{0,4000}` replicates
     * the SITE — a push and a goto per copy — and the region is emitted ONCE,
     * so the region's own count is taken at `repl == 1`. */
    case A_CALL:
        return;
    /* [M6.4.2] A LIFTED group allocates NO mark of its own — the rung below
     * allocates it, and counting one here as well would make `RX_NSLOTS` one
     * too large on every possessive spelling. An UNLIFTED one allocates
     * `vm_atomic`'s mark and pushes nothing. */
    case A_ATOMIC:
        if (vm_lifts(a)) { vm_count_slots(v, a->l, repl, true); return; }
        v->nmark++;
        vm_count_slots(v, a->l, repl, false);
        return;
    case A_ALT:
        /* Iterative spine walk (R1 R-2 / D10) — see vm_nullable. One push per
         * A_ALT NODE, which for a left-nested flat alternation of k branches
         * is k-1, exactly what vm_alt emits. */
        while (a->k == A_ALT) {
            v->npush++;
            vm_count_slots(v, a->r, repl, false);
            a = a->l;
        }
        vm_count_slots(v, a, repl, false);
        return;
    case A_CAT:
        while (a->k == A_CAT) { vm_count_slots(v, a->r, repl, false); a = a->l; }
        vm_count_slots(v, a, repl, false);
        return;
    case A_REP: {
        const bool cuts = vm_cuts(a, under_atomic);
        if (a->u.rep.rmin == 0 && a->u.rep.rmax == 0) return;
        if (vm_cursor_fits(a, seq, &stride, caps, &nc)) {
            /* [ENG-BREP] the possessive span loop allocates NEITHER — no
             * low-water slot and no resume point. Mirrors vm_cursor_rep's own
             * branch; the two are the same condition read twice, which is the
             * standing hazard this function's header comment is about. */
            if (!cuts) {
                v->nlow++;
                v->npush++;              /* vm_cursor_rep: exactly one */
            }
            return;
        }
        /* [ENG-BREP] the REVERSE-DETERMINISTIC rung. Three slots, one loop, and
         * NO REPLICATION — which is the whole point, and is also why this arm
         * returns before the `maxcopies` line below ever sees the quantifier:
         * `((a)|b){0,4000}c` demands one body copy here where the frames rung
         * demanded four thousand.
         *
         * The push arithmetic, site for site with vm_revdet_rep:
         *   1  the scan's exit frame (this iteration cannot run -> leave)
         *   1  the retreat/extension frame, only when the loop can move
         * and NOTHING for the backward walk, which is emitted as a
         * DETERMINISTIC matcher with no choice point at all — reverse
         * one-unambiguity is exactly the licence to dispatch on the next byte
         * instead of pushing a frame per branch.
         *
         * The forward body is walked ONCE, or twice for a lazy loop that can
         * move, because that shape emits a second forward copy for its
         * extension step. The REVERSED body allocates no slots and pushes
         * nothing, so it is not walked here at all. */
        if (vm_revdet_fits(a, under_atomic)) {
            int grp[PCREC_MAX_REVDET_BODY_GROUPS];
            int ng = 0;
            bool move = vm_rev_canmove(a, cuts);
            vm_rev_caps(a->l, grp, &ng, PCREC_MAX_REVDET_BODY_GROUPS);
            if (ng > v->nrevcaps) v->nrevcaps = ng;
            v->nrev++;
            v->npush += 1 + (move ? 1 : 0);
            vm_count_slots(v, a->l, repl, false);
            if (move && !a->u.rep.greedy) vm_count_slots(v, a->l, repl, false);
            return;
        }
        /* [ENG-BREP counter-K] the COUNTER rung, and like the revdet arm above
         * it returns BEFORE the `copies` replication line — which is the whole
         * point of the rung. The body is emitted K + (m mod K) times, not m
         * times, so `((a)|ab){4000}` charges 8 copies against
         * PCREC_MAX_VM_REPEAT_COPIES where the frames rung charged four
         * thousand and was refused.
         *
         * NO PUSHES: §3.1's mandatory phase has no choice point at the loop
         * level (a mandatory copy that fails fails the quantifier), so the only
         * frames are the body's own, counted by the walk below. ONE slot, the
         * trailed counter.
         *
         * `repl` is passed through UNCHANGED rather than multiplied by the copy
         * count: K22's product guard bounds the replication a nesting path
         * performs, and this rung does not replicate per iteration — it emits a
         * fixed K + residue whatever `m` is. Multiplying here would re-import
         * exactly the explosion the rung removes. */
        if (vm_counter_fits(v, a)) {
            const int K = v->unroll_k;
            const int nopt = a->u.rep.rmax - a->u.rep.rmin;
            int copies = vm_counter_copies(v, a, cuts);
            v->nctr++;
            if (cuts) v->nmark++;   /* the cut mark, as the frames rung */
            /* Emitted PUSH sites: the mandatory phase has none, and the
             * optional phase has one per emitted optional copy — K inside the
             * trip plus the residue's, which is what vm_opt_chain emits for
             * the tail. The POSSESSIVE optional phase emits exactly ONE, at
             * its single re-entered body. Emitted SITES, not live frames:
             * vm_cost_rep counts the runtime requirement, which is still one
             * per ITERATION for the non-possessive shapes and ONE for the
             * whole loop possessified. */
            v->npush += cuts ? (nopt >= K ? 1 : nopt)
                             : (nopt >= K ? K + nopt % K : nopt);
            if (copies > v->maxcopies) v->maxcopies = copies;
            for (int i = 0; i < copies; i++) vm_count_slots(v, a->l, repl, false);
            return;
        }
        /* frames rung: the star's own push, or one per optional copy. The
         * possessive shapes push at the SAME sites (vm_poss_star once,
         * vm_poss_chain once per optional copy) — what changes is how many are
         * live at a time, not how many are emitted — so this arithmetic is
         * unchanged. The cut mark is the one new slot. */
        v->npush += a->u.rep.rmax < 0 ? 1 : (a->u.rep.rmax - a->u.rep.rmin);
        if (cuts) v->nmark++;
        /* Frames rung: the body's code is REPLICATED once per mandatory copy
         * and once per optional copy, and each copy's own loops need their own
         * slots — so the count must replicate exactly as the emitter does or
         * two live loops would share one slot. */
        {
            int copies = a->u.rep.rmax < 0 ? a->u.rep.rmin + 1 : a->u.rep.rmax;
            if (copies < 1) copies = 1;
            /* THE REPLICATION FACTOR, recorded before any of it is emitted.
             * Only the frames rung reaches here: a body the cursor rung
             * accepts is single-path and compiles to a span loop whatever the
             * count, so `a{0,65535}` never contributes. */
            if (copies > v->maxcopies) v->maxcopies = copies;
            /* [K22] and the factor's PRODUCT down the nesting path, checked
             * BEFORE the loop below walks it. `v->maxcopies` above is a MAX and
             * structurally cannot see this: nesting multiplies factors that are
             * individually far under PCREC_MAX_VM_REPEAT_COPIES. The check is
             * placed here rather than after the walk for the only reason it
             * exists — the walk is the cost. Overflow is not reachable: the
             * running product is refused the moment it exceeds the limit, so it
             * never carries more than limit * PCREC_MAX_REPEAT. */
            {
                long long total = repl * copies;
                if (total > PCREC_MAX_VM_REPLICATION_PRODUCT)
                    ctx_fail(v->cx, 0,
                             "pattern too large: nested bounded repeats would "
                             "replicate a body %lld times in total (limit %d). "
                             "Repetition counts MULTIPLY through nesting, so "
                             "depth costs far more than any one count suggests "
                             "-- lower a count, or reduce the nesting",
                             total, PCREC_MAX_VM_REPLICATION_PRODUCT);
                for (int i = 0; i < copies; i++)
                    vm_count_slots(v, a->l, total, false);
            }
            if (a->u.rep.rmax < 0 && vm_nullable(a->l)) v->nguard++;
        }
        return;
    }
    }
}

/* ---- emission -----------------------------------------------------------*/

static void vm_emit(Vm *v, int entry, const Ast *a, int next);

/* THE FIVE PRIMITIVES. Every one of them writes C *and* records the listing
 * event for what it just wrote — one call, one truth (engine_m4.md S10). A
 * label that does not appear in the listing is not a listing bug, it is an
 * impossibility: there is no other way to emit a label. */

static void vm_lbl(Vm *v, int id, const char *role)
{
    /* The `__attribute__((unused))` follows emit_attempt's precedent: a label
     * that is only ever reached through a resume frame's `&&` address, or one
     * the flattening below makes unreachable, must not fail the harness's
     * -Werror generated-code build. */
    /* [M6-READ] The label's INTENT, emitted as a line comment from the SAME
     * `role` string the listing gets. One call writes both, so the C and
     * `--emit-ir` cannot drift about what a label is for -- which is the
     * property S10 asks of the listing, now extended to the code it describes.
     *
     * The label NUMBER is deliberately not renamed: it is shared vocabulary
     * with the listing and with tests/codegen/run_ir_listing.sh, so it is a
     * documented cross-artifact identifier rather than an opaque local. It
     * gets a name in a comment, not a new spelling. */
    if (role && *role)
        sb_printf(v->b, "// %s\n", role);
    sb_printf(v->b, "%s_L%d: __attribute__((unused));\n", v->p, id);
    vm_ev(v, VE_LABEL, id, 0, role);
}

static void vm_goto(Vm *v, int id)
{
    sb_printf(v->b, "    goto %s_L%d;\n", v->p, id);
    vm_ev(v, VE_GOTO, id, 0, NULL);
}

static void vm_fail(Vm *v)
{
    sb_printf(v->b, "    goto %s_fail;\n", v->p);
    vm_ev(v, VE_FAIL, 0, 0, NULL);
}

/* `posexpr` is what the frame records as its resume position — `pos` for every
 * ordinary choice point, and the span-loop cursor for S2.5's rung, which is
 * the one site that resumes somewhere other than the current position. Under
 * --trace the macro takes the label id too, so the instrumented artifact can
 * name the frame it is pushing; that extra argument is the ONLY difference
 * --trace makes to this line, and it makes none at all without it. */
static void vm_push_at(Vm *v, int lblid, const char *posexpr, const char *role)
{
    if (v->tracing)
        sb_printf(v->b, "    %s_PUSH(%d, &&%s_L%d, %s);\n",
                  v->up, lblid, v->p, lblid, posexpr);
    else
        sb_printf(v->b, "    %s_PUSH(&&%s_L%d, %s);\n",
                  v->up, v->p, lblid, posexpr);
    vm_ev(v, VE_PUSH, lblid, 0, role);
}

static void vm_push(Vm *v, int lblid, const char *role)
{
    vm_push_at(v, lblid, "scan_position", role);
}

static void vm_set(Vm *v, int slot, const char *val, const char *role)
{
    {
        char nm[48];
        if (vm_slot_name(v, slot, nm, sizeof nm))
            sb_printf(v->b, "    %s_SET(%s_%s, %s);\n", v->up, v->up, nm, val);
        else
            sb_printf(v->b, "    %s_SET(%d, %s);\n", v->up, slot, val);
    }
    vm_ev(v, VE_SET, slot, 0, role);
}

/* [ENG-BREP] THE CUT — the possessive loop's one new operation, and a
 * primitive rather than an inline sb_printf for the same "one call, one truth"
 * reason as the five above.
 *
 * It truncates the resume stack back to the depth recorded in `slot`,
 * discarding every frame the loop and its body pushed since. That is exactly
 * what a positive §2.2 verdict licenses: no retreat into this loop can produce
 * a match the preferred path does not, so those frames are provably dead.
 *
 * IT DOES NOT TOUCH THE TRAIL, and must not. The frames are dead; the capture
 * writes they would have rewound are NOT, because a failure OUTSIDE the loop
 * still has to restore the loop's groups to their pre-loop values. A frame
 * below the cut carries a trail mark from before the loop ran, so unwinding to
 * it still rewinds everything the loop wrote — which is why discarding frames
 * without rewinding the trail is safe rather than merely convenient. */
/* [ENG-BREP counter-K] THE WORK CHARGE (D47 SECOND ADDENDUM, settlement 4;
 * counterk_design.md §7.4). A SEVENTH primitive, and a primitive for a reason
 * this section learned the hard way: the charge has THREE emission sites in
 * two different spellings, and the probe that priced this design reported a
 * confident zero for the revdet rung because the first version instrumented
 * only the `RX_CUT` macro and missed the rung that cuts by assigning `run->resume_depth`
 * directly. One call here is what keeps a fourth site from repeating that.
 *
 * WHAT IS CHARGED, and equally WHAT IS NOT. The rule is "per-iteration work
 * the fail label NEVER SEES", and the second half is the part two earlier
 * drafts got wrong:
 *
 *   pushed, then CUT            -> CHARGED, at every cut: the frames being
 *                                  discarded were never popped through
 *                                  rx_fail, so nothing counted them.
 *   never pushed, no retreat    -> CHARGED, at scan completion: the
 *     frame (possessified scan)    frameless scan's iteration count.
 *   scanned, then RETREATED     -> NOT CHARGED. Its iterations pop through
 *     one stride per pop          the fail label 1:1 and are ALREADY charged
 *                                 in full. Charging here double-bills the
 *                                 triangular quantity, which is exactly what
 *                                 R25 finding 26 refuted — and the refuting
 *                                 number (the same 50,005,000 under `steps`
 *                                 and under `scan`) was sitting in the note's
 *                                 own published control row.
 *
 * The emitted subtraction is SIGNED and the cast order is load-bearing:
 * `run->resume_depth` is `unsigned` and `slot_values[]` is `ptrdiff_t`, so the count must be
 * taken as `(ptrdiff_t)run->resume_depth - slot_values[slot]` and never the other way, or a
 * momentarily-negative intermediate wraps to an enormous positive charge. */
/* [M6.5.2] `indent` exists because one charge site is inside an emitted BLOCK
 * rather than at statement level (the A_BREF compare declares locals, so it
 * needs braces). Threading the indentation is what keeps this ONE call — the
 * alternative is a second `sb_printf` at that site, and then `nwork` and the
 * listing's NOTE event would count charges the artifact does not make, or the
 * other way round. */
static void vm_work_at(Vm *v, const char *indent, const char *countexpr,
                       const char *role)
{
    if (!v->has_budget) return;
    sb_printf(v->b, "%s%s_CHARGE_WORK(%s);\n", indent, v->up, countexpr);
    v->nwork++;
    vm_ev(v, VE_NOTE, 0, 0, role);
}

static void vm_work(Vm *v, const char *countexpr, const char *role)
{
    vm_work_at(v, "    ", countexpr, role);
}

static void vm_cut(Vm *v, int slot, const char *role)
{
    /* BEFORE the cut, necessarily: RX_CUT overwrites `run->resume_depth` with the mark,
     * so after it runs the count this charge needs no longer exists. */
    {
        char cnt[192];
        snprintf(cnt, sizeof cnt, "(ptrdiff_t)run->resume_depth - slot_values[%d]", slot);
        vm_work(v, cnt, "work charge: frames discarded by this cut");
    }
    sb_printf(v->b, "    %s_CUT(%d);\n", v->up, slot);
    vm_ev(v, VE_CUT, slot, 0, role);
}

/* [D46] the SIXTH primitive: writes no C (the rung was already selected by
 * the C written around this call), but records the SAME "one call, one
 * truth" way every other primitive does — sets the artifact-wide summary
 * bit AND appends the per-quantifier VE_RUNG event in one place, so the
 * bitmask macro and the RUNGS listing section can never drift apart. Called
 * once per A_REP, at the point vm_cursor_rep / vm_rep's frames fallthrough
 * already knows which rung THIS quantifier took — never a second pass over
 * the AST re-deciding it (that would risk drifting from vm_cursor_fits's
 * three real call sites, exactly what the 0b4b0be fix consolidated away). */
static void vm_rung_mark(Vm *v, int lblid, VmRungKind k, bool possessive,
                         const char *role)
{
    VmStratKind s = possessive ? VM_STRAT_POSSESSIVE : VM_STRAT_BACKTRACKING;
    v->rungs  |= vm_rung_bit[k];
    v->strats |= vm_strat_bit[s];
    vm_ev(v, VE_RUNG,  lblid, (int)k, role);
    vm_ev(v, VE_STRAT, lblid, (int)s, role);
}

/* ---- [M4.6d] MINIMUM-REMAINING-LENGTH PRUNING ---------------------------
 *
 * docs/design/k23_impl/k23_design.md, adopted by D51 ruling 1. At a program
 * point `q` the emitter knows `minrest(q)` — a compile-time lower bound on
 * the bytes any accepting continuation from `q` must still consume — as
 * `pcrec_minw(node) + v->fmin`. A position with fewer bytes left than that is
 * DOOMED: no continuation from it can accept, so it is cut before a choice
 * point is pushed for it.
 *
 * TWO FORMS, and which one applies is fixed by the rung (§4.5). The
 * difference is not cosmetic and §4.1 states the rule once:
 *
 *   TEST  — where the bound examines a position the engine has ALREADY
 *           reached. One comparison; nothing is assigned, so nothing has to
 *           be a position the loop could occupy.
 *   CLAMP — where the bound SELECTS a position out of a range (the greedy
 *           cursor rung). An assigned value must land ON THE CURSOR'S
 *           ITERATION LATTICE, so the cap is rounded DOWN to `pos + W*k`.
 *           R26 E1 measured the unrounded form UNSOUND at stride > 1: it
 *           substitutes a position the loop can never occupy for one it can,
 *           which satisfies "removes only doomed candidates" and still
 *           deletes the correct answer.
 *
 * THE CEILING is `<prefix>_ceil`, a parameter of the match function rather
 * than a member of `<prefix>_work` (the note's §9.1 sketch): a parameter
 * cannot be left stale by an entry point that forgets to set it, because
 * forgetting is a compile error. Its VALUE is `min(n, win[0][1])` — the
 * prefilter's match-end window, D51 ruling 2 — on the entries that run a
 * prefilter, and the subject end everywhere else (obligation (a)).
 *
 * SOUNDNESS IS PREFERENCE-BLIND (§2.8). `minrest` bounds whether an accepting
 * continuation EXISTS, which is a property of the language and therefore
 * order-invariant: a subtree with no accepting leaf has none under greedy,
 * under lazy and under any future preference spelling, so deleting it cannot
 * move the first accepting leaf in ANY order. That is why nothing below
 * branches on `a->u.rep.greedy` for CORRECTNESS — only for which of the two forms
 * the emitted shape wants. */

/* The saturating add the follow-min accumulator needs. pcrec_minw saturates
 * its own arithmetic at PCREC_MINW_MAX; the accumulator has to hold the same
 * ceiling or a long enough concatenation of saturated subtrees could still
 * overflow. Under-estimating is the safe direction and saturation is an
 * under-estimate, so pinning here costs nothing but the line. */
static long long vm_fadd(long long a, long long b)
{
    long long r = a + b;
    return r > PCREC_MINW_MAX ? PCREC_MINW_MAX : r;
}

/* Its multiplying sibling, for the per-replica constant `k * minw(body)`. */
static long long vm_fmul(long long a, long long b)
{
    if (a <= 0 || b <= 0) return 0;
    if (a > PCREC_MINW_MAX / b) return PCREC_MINW_MAX;
    return a * b;
}

/* Emit `a` with an explicit follow-min, restoring the caller's on the way
 * out. THE ONLY MUTATOR of `v->fmin`: a site that changes what follows says
 * so here and nowhere else, and a site that says nothing correctly inherits.
 * `v->fdyn` is deliberately NOT touched -- a runtime term set by an enclosing
 * loop is still in force inside every node under it. */
static void vm_emit_f(Vm *v, int entry, const Ast *a, int next, long long fmin)
{
    long long save = v->fmin;
    v->fmin = fmin;
    vm_emit(v, entry, a, next);
    v->fmin = save;
}

/* The same, additionally setting the RUNTIME half. Only the counter rung's
 * mandatory phase calls it. */
static void vm_emit_fd(Vm *v, int entry, const Ast *a, int next,
                       long long fmin, const char *fdyn)
{
    const char *sd = v->fdyn;
    long long sf = v->fmin;
    v->fdyn = fdyn;
    v->fmin = fmin;
    vm_emit(v, entry, a, next);
    v->fmin = sf;
    v->fdyn = sd;
}

/* Sum two runtime follow-min terms, either of which may be absent.
 *
 * THE LENGTH CAP IS A SOUNDNESS-PRESERVING RETREAT, not a defensive check.
 * Nested counter trips concatenate their terms, and a deep enough tower would
 * put an unbounded expression at every bound site in the emitted C. Past the
 * cap the OUTER term is dropped, which UNDER-estimates the follow-min -- the
 * safe direction, and the only one available: an expression that is merely
 * long is not wrong, but silently emitting megabytes of it would be a
 * different defect. Unreachable on anything pcrec compiles today; written
 * down because the arithmetic must be right where nobody is watching. */
enum { VM_MRL_DYN_MAX = 240 };

static const char *vm_dyn_add(Vm *v, const char *a, const char *b)
{
    size_t n;
    char *p;
    if (!a) return b;
    if (!b) return a;
    n = strlen(a) + strlen(b) + 4;
    if (n > VM_MRL_DYN_MAX) { v->ndynskip++; return b; }
    p = arena_alloc(&v->cx->arena, n);
    snprintf(p, n, "%s + %s", a, b);
    return p;
}

/* The minrest OPERAND as the emitted C spells it: a bare constant when the
 * bound is wholly compile-time, and `k + (runtime term)` when a counter trip
 * is in force. Arena-owned so the caller does not have to size a buffer for
 * an expression whose length it cannot know. */
static const char *vm_mrl_amt(Vm *v, long long k)
{
    size_t n;
    char *p;
    if (!v->fdyn) {
        p = arena_alloc(&v->cx->arena, 32);
        snprintf(p, 32, "%lld", k);
        return p;
    }
    n = strlen(v->fdyn) + 40;
    p = arena_alloc(&v->cx->arena, n);
    snprintf(p, n, "%lld + (%s)", k, v->fdyn);
    return p;
}

/* [M4.6d] the EIGHTH primitive, and vm_rung_mark's sibling: writes no C (the
 * bound was already written by the site that called this), records the
 * artifact-wide summary bit AND the per-quantifier VE_PRUNE event in one
 * place. Called once per A_REP by every rung, with the quantifier's OWN
 * minrest — so "did this quantifier get a bound" is answered by the site that
 * decided it rather than by a second reading of the AST. */
static void vm_prune_mark(Vm *v, int lblid, bool clamped, const char *role)
{
    VmPruneKind k = clamped ? VM_PRUNE_CLAMPED : VM_PRUNE_UNCLAMPED;
    v->prunes |= vm_prune_bit[k];
    vm_ev(v, VE_PRUNE, lblid, (int)k, role);
}

/* The TEST form. `posexpr` is the position under test — `pos` at an ordinary
 * program point, the cursor local where a loop is about to commit to one.
 * `dst` is where a doomed position goes: a label id, or -1 for the fail label.
 *
 * Returns whether anything was emitted, so a caller can mark the quantifier
 * clamped-or-not from the same call that decided it. A `minrest` of 0 emits
 * NOTHING — the test would be vacuous, and an artifact whose pattern has no
 * length constraint stays byte-for-byte what it was before MRL existed. */
static bool vm_mrl_test(Vm *v, const char *posexpr, long long minrest,
                        int dst, const char *role)
{
    if (!v->mrl || (minrest <= 0 && !v->fdyn)) return false;
    sb_printf(v->b, "    if (%s_PRUNE_TOO_SHORT(%s, %s)) ", v->up, posexpr,
              vm_mrl_amt(v, minrest));
    if (dst < 0) sb_printf(v->b, "goto %s_fail;\n", v->p);
    else         sb_printf(v->b, "goto %s_L%d;\n", v->p, dst);
    v->nclamp++;
    vm_ev(v, VE_NOTE, 0, 0, role);
    return true;
}

/* The TEST form used as a GATE on a whole subtree: emits the test at `entry`
 * and returns the label the subtree should be emitted at instead. When no
 * bound applies it returns `entry` unchanged and costs not one byte, which is
 * what keeps an unconstrained pattern's emitted C identical. */
static int vm_mrl_gate(Vm *v, int entry, long long minrest, int dst,
                       const char *role)
{
    int pass;
    if (!v->mrl || (minrest <= 0 && !v->fdyn)) return entry;
    pass = vm_label(v);
    vm_lbl(v, entry, role);
    vm_mrl_test(v, "scan_position", minrest, dst, role);
    vm_goto(v, pass);
    return pass;
}

/* Flat alternation as a CHAIN (§2.2 property 4, refined). The design's text
 * says "N-way alternation pushes a chain, one frame per untried branch, in
 * reverse preference order"; pushing all N-1 frames eagerly and pushing them
 * one at a time as each branch is tried are both correct, and this emits the
 * second because it holds ONE live frame per alternation instead of N-1,
 * which is what keeps `(a|b|c|...)` off the frame-capacity bound. The
 * preference order is identical either way: the frame pushed at branch k
 * resumes branch k+1. */
static void vm_alt(Vm *v, int entry, const Ast *a, int next)
{
    Ctx *cx = v->cx;
    int nbr = 1;
    for (const Ast *t = a; t->k == A_ALT; t = t->l) nbr++;
    const Ast **br = arena_alloc(&cx->arena, (size_t)nbr * sizeof(Ast *));
    int i = nbr;
    const Ast *t = a;
    while (t->k == A_ALT) { br[--i] = t->r; t = t->l; }
    br[0] = t;

    int *bentry = arena_alloc(&cx->arena, (size_t)nbr * sizeof(int));
    int *resume = arena_alloc(&cx->arena, (size_t)nbr * sizeof(int));
    for (int j = 0; j < nbr; j++) bentry[j] = vm_label(v);
    resume[0] = entry;
    for (int j = 1; j < nbr; j++) resume[j] = vm_label(v);

    for (int j = 0; j < nbr; j++) {
        vm_lbl(v, resume[j], j == 0
               ? vm_rolef(v, "alternation entry (%d branches)", nbr)
               : vm_rolef(v, "alternation resume: try branch %d of %d",
                          j + 1, nbr));
        if (j + 1 < nbr)
            vm_push(v, resume[j + 1],
                    vm_rolef(v, "branch %d of %d preferred; resume tries "
                                "branch %d", j + 1, nbr, j + 2));
        vm_goto(v, bentry[j]);
    }
    for (int j = 0; j < nbr; j++) vm_emit(v, bentry[j], br[j], next);
}

/* §2.5's cursor rung, with D44.1's capture extension.
 *
 * GREEDY: consume greedily to the furthest position, then push exactly ONE
 * resume frame recording the cursor. On BACKTRACK the engine decrements the
 * cursor by the stride and RE-PUSHES the same frame (same label, new pos)
 * before retrying the continuation — so a second backtrack into the loop has
 * somewhere to land, and the stack still holds never more than one live frame
 * for this loop even though the loop may be re-entered (furthest − low-water)
 * times across the whole match. Each re-push REPLACES the just-popped frame
 * rather than growing the stack (D44/R21 E-4's re-push discipline, written out
 * explicitly there because it had been left unshown).
 *
 * The cursor is a plain local; the resume frame's own `pos` field is its save
 * point. What the frame cannot carry is where the loop STARTED, which the
 * low-water test needs and which an OUTER backtrack must restore — a second
 * entry to the same loop at a different position would otherwise leave a stale
 * low-water mark behind for the first entry's frame to retreat against. That
 * is what the trailed low-water slot is for, and it is written once per loop
 * ENTRY, so the mechanism designed to avoid per-iteration trail entries does
 * not quietly reintroduce one.
 *
 * CAPTURES (D44.1): a deterministic body's group spans are computed FROM THE
 * CURSOR at the point the continuation is taken, not written per iteration —
 * `[cursor − stride + off, cursor − stride + off + len)` for a group at
 * relative offset `off`. The writes go AFTER the push, so the frame's own mark
 * rewinds them on every retreat and they never accumulate on the trail. */
static void vm_cursor_rep(Vm *v, int entry, const Ast *a, int next,
                          const uint8_t **seq, int stride,
                          const CapOff *caps, int ncaps, bool under_atomic)
{
    StrBuf *b = v->b;
    /* [ENG-BREP] A POSSESSIFIED span loop owes NOTHING but the scan: no resume
     * frame, no low-water slot and no trail entry of its own.
     *
     * The low-water slot exists so the RETREAT can tell "still above rmin"
     * from "exhausted", and it has to be a trailed slot rather than a local
     * because the frame that resumes the retreat may be popped long after the
     * loop was left. With no retreat there is no such reader — and `pos` is
     * still the loop's entry position at every point below, because the scan
     * writes only `<p>_cur` and `pos` is not assigned until the loop commits.
     * So the possessive path reads `pos` where the backtracking one reads
     * `slot_values[low]`, allocates no slot, and writes no trail entry. vm_cost_rep
     * and vm_count_slots carry the same branch; all three must agree or two
     * live loops share one slot. */
    const bool poss = vm_cuts(a, under_atomic);
    /* [M6.4.2] THE PREFERENCE PRECONDITION, CHECKED, and this rung is where
     * R31's N1 was FOUND: it satisfies CUT-EQUIVALENCE (it is frameless — no
     * slot, no labels, no push, so there is nothing a cut would remove) and
     * still answers the WRONG LANGUAGE on a lazy body. Cut-equivalence is a
     * claim about FRAMES only; the scan below is unconditionally MAXIMAL, and
     * `(?>a*?)b` on "aaab" is (3,4) in both oracles and (0,4) here. */
    if (poss && !a->u.rep.greedy && !a->u.rep.possessive)
        ctx_fail(v->cx, 0,
                 "internal error: the cursor rung's possessive scan was given "
                 "a LAZY body with no §2.2 verdict behind it. The scan is "
                 "unconditionally maximal, which that verdict is what "
                 "licenses (see the preference-collapse note below)");
    /* [ENG-BREP] a cursor loop NESTED in a revdet loop's forward scan writes no
     * captures either (v->nocap): the enclosing rung's backward walk recovers
     * this body's groups along with every other group in it, and a per-iteration
     * write here would reintroduce the trail growth the enclosing rung removed.
     * vm_cost_rep's cursor arm reads the same flag for the same number. */
    if (v->nocap) ncaps = 0;
    int low = poss ? -1 : vm_slot_low(v, v->nlow++);
    int retry = poss ? -1 : vm_label(v), again = poss ? -1 : vm_label(v);
    long long lo_off = (long long)a->u.rep.rmin * stride;
    /* The loop's entry position, spelled for whichever of the two it is. */
    char entrypos[32];
    if (poss) snprintf(entrypos, sizeof entrypos, "(ptrdiff_t)scan_position");
    else      snprintf(entrypos, sizeof entrypos, "slot_values[%d]", low);

    /* class ids first, so the pool is stable before any test is written */
    int *ci = arena_alloc(&v->cx->arena, (size_t)stride * sizeof(int));
    for (int i = 0; i < stride; i++) ci[i] = vm_cls(v, seq[i]);

    /* The body's own inline test, written once and reused by both rungs. */
    StrBuf t;
    memset(&t, 0, sizeof t);
    for (int i = 0; i < stride; i++) {
        char byte[64];
        snprintf(byte, sizeof byte, "subject[%s_span_cursor + %d]", v->p, i);
        sb_puts(&t, " && (");
        vm_cls_test(v, &t, ci[i], byte);
        sb_puts(&t, ")");
    }
    const char *test = t.p ? t.p : "";

    char bounds[32];
    if (a->u.rep.rmax < 0) snprintf(bounds, sizeof bounds, "{%d,}", a->u.rep.rmin);
    else             snprintf(bounds, sizeof bounds, "{%d,%d}", a->u.rep.rmin, a->u.rep.rmax);
    /* The PREFERENCE disappears when the quantifier is possessified, and that
     * is the analysis's conclusion rather than a shortcut. On the exact-count
     * arm there is one exit, so top and bottom of §2.3's chain are the same
     * position. On the disjointness arm a greedy loop tops out by preference,
     * and a LAZY one is FORCED to the same top: at any non-maximal exit the
     * body could iterate again, so that byte is in FIRST(X), so by
     * disjointness the follow cannot begin there — and the lazy conjunct
     * (non-nullable remainder) is what rules out the match simply ENDING
     * there instead. Both preferences therefore land on the maximal exit,
     * which is what makes one emitted shape correct for both. */
    const char *rung = vm_rolef(v, "span-loop cursor %s, stride %d, %s%s",
                                bounds, stride,
                                a->u.rep.greedy ? "greedy" : "lazy",
                                poss ? ", POSSESSIFIED (no frame, no giveback)"
                                     : "");
    vm_lbl(v, entry, rung);
    /* [D46] this A_REP's own rung, reusing the SAME role text vm_lbl just
     * wrote — one description, two views (the PROGRAM section's label line
     * and the RUNGS section's per-quantifier entry), not two computations
     * of "what is this quantifier doing" that could disagree. */
    vm_rung_mark(v, entry, VM_RUNG_CURSOR, poss, rung);
    /* [M4.6d] THE BOUND THIS LOOP CARRIES. `v->fmin` is what must still be
     * consumed after the loop, so a cursor value `c` is viable only while
     * `CEIL - c >= fmin`. That is the whole of K23's fix at this rung: the
     * exemplar's inner span loop is asked for 90 bytes of follow at the first
     * replica, 80 at the second, and the clamp deletes ten of its eleven
     * choices at each one. */
    const long long mrl = v->mrl ? v->fmin : 0;
    vm_prune_mark(v, entry, v->mrl && (mrl > 0 || v->fdyn != NULL), rung);
    /* The loop's ENTRY position, trailed. Both rungs derive their bounds from
     * it: low-water is entry + stride*rmin, ceiling is entry + stride*rmax.
     * The possessive path reads `pos` for the same quantity and writes no
     * slot at all — see the note at the top of this function. */
    if (!poss)
        vm_set(v, low, "(ptrdiff_t)scan_position",
               "span-loop low-water mark (loop entry scan_position)");

    if (poss) {
        /* The scan, and then the commit. One straight line: consume to the
         * furthest position the bound allows, refuse if that is short of
         * rmin, publish the groups, take the continuation. Nothing here can
         * be resumed, which is the whole point — the emitted C contains no
         * label the loop could come back to. */
        sb_puts(b, "    {\n");
        if (a->u.rep.rmax >= 0) sb_puts(b, "        unsigned long it_ = 0;\n");
        sb_printf(b, "        %s_span_cursor = scan_position;\n", v->p);
        sb_printf(b, "        while (%s_span_cursor + %d <= subject_length", v->p, stride);
        if (a->u.rep.rmax >= 0) sb_printf(b, " && it_ < %dUL", a->u.rep.rmax);
        sb_printf(b, "%s) { %s_span_cursor += %d;", test, v->p, stride);
        if (a->u.rep.rmax >= 0) sb_puts(b, " it_++;");
        sb_puts(b, " }\n    }\n");
        /* [counter-K] THE FRAMELESS SCAN'S CHARGE, and this is the exact site
         * counterk_design.md §7.4 specifies: AFTER the scan loop and BEFORE the
         * rmin test. The scan has completed, `pos` is still the loop's entry
         * (the possessive path writes no low-water slot and never moves `pos`),
         * so the cursor delta IS the work done; after the rmin test the value
         * is consumed. Charging here rather than one line later is what makes a
         * scan that then FAILS the rmin test still pay for the bytes it read.
         *
         * Divided by the stride because the unit is an ITERATION, not a byte —
         * a compile-time constant division that folds away entirely at the
         * stride of 1 every measured shape has. Whether a wide-stride iteration
         * should cost proportionally more is a real question the measurement
         * does not answer (it swept stride-1 shapes only); iterations is what
         * §7.4 specifies and what its calibration identity is stated over, so
         * iterations is what ships. Recorded as a residual rather than decided
         * here. */
        {
            char cnt[192];
            snprintf(cnt, sizeof cnt,
                     "((ptrdiff_t)(%s_span_cursor - %s)) / %d", v->p, entrypos, stride);
            vm_work(v, cnt, "work charge: frameless scan iterations");
        }
        sb_printf(b, "    if ((ptrdiff_t)%s_span_cursor < %s + %lld) goto %s_fail;\n",
                  v->p, entrypos, lo_off, v->p);
        vm_ev(v, VE_NOTE, 0, 0,
              "fewer than rmin iterations: the loop cannot be satisfied");
        /* [M4.6d] MRL on the POSSESSIFIED arm is the TEST form, deliberately,
         * and this is the one place the choice is not simply "which shape the
         * rung wants".
         *
         * A possessified loop has exactly ONE exit position — that is what
         * the §2.2 verdict says — so if that position is doomed the whole
         * quantifier is, and one comparison says so. CLAMPING here would be a
         * different thing: it would move the loop to a SMALLER position and
         * then run the continuation from there, i.e. re-introduce the very
         * retreat possessification proved dead. Under a correct verdict that
         * position cannot match either and the clamp would be harmless; under
         * a subtly wrong one it would manufacture a match neither the
         * possessive nor the plain greedy semantics produces. MRL's soundness
         * must not come to depend on possessify's, so it does not. */
        {
            char cx[64];
            snprintf(cx, sizeof cx, "%s_span_cursor", v->p);
            vm_mrl_test(v, cx, mrl, -1,
                        "MRL: too few bytes remain after the loop's one exit "
                        "position for any accepting continuation");
        }
        if (ncaps) {
            sb_printf(b, "    if ((ptrdiff_t)%s_span_cursor >= %s + %d) {\n",
                      v->p, entrypos, stride);
            for (int i = 0; i < ncaps; i++) {
                char val[96];
                snprintf(val, sizeof val, "(ptrdiff_t)(%s_span_cursor - %d)", v->p,
                         stride - caps[i].off);
                vm_set(v, 2 * caps[i].group, val,
                       vm_rolef(v, "group %d open, derived from the cursor",
                                caps[i].group));
                snprintf(val, sizeof val, "(ptrdiff_t)(%s_span_cursor - %d)", v->p,
                         stride - caps[i].off - caps[i].len);
                vm_set(v, 2 * caps[i].group + 1, val,
                       vm_rolef(v, "group %d close, derived from the cursor",
                                caps[i].group));
            }
            sb_puts(b, "    }\n");
        }
        sb_printf(b, "    scan_position = %s_span_cursor;\n", v->p);
        vm_goto(v, next);
        sb_free(&t);
        return;
    }

    if (a->u.rep.greedy) {
        /* [M4.6d] THE CLAMP, FOLDED INTO THE SCAN'S OWN BOUND (§4.6). Two
         * separate wins from one expression, and they are different
         * quantities:
         *
         *  - STEPS. The cursor starts at the largest position an accepting
         *    continuation could use instead of at the largest position the
         *    body matches, so the doomed suffix of the retreat chain is never
         *    walked. That is the collapse: 10,621,636 -> 1 on the exemplar.
         *  - FORWARD WORK, which the step counter is structurally blind to.
         *    Applying the clamp AFTER the scan would still read every byte
         *    the scan can reach; folding it into the loop guard means the
         *    scan stops at the cap, and the measured proxy drops from 190 to
         *    100 — exactly one forward pass per accepting iteration, the
         *    floor.
         *
         * THE LATTICE (§4.1, R26 E1), AND WHAT ACTUALLY MAKES IT HOLD —
         * CREDIT THE FOLD, NOT THE ROUNDING. R26 E1's defect is an
         * OFF-LATTICE CURSOR: a value assigned to `<p>_cur` that the span loop
         * could never occupy, which poisons the whole retreat chain below it.
         * §4.1 answers it by rounding the cap down to `pos + W*k`, because
         * there the clamp ASSIGNS. Here it does not: the cap is the scan's own
         * LOOP BOUND, and `<p>_cur` starts at `pos` and only ever moves by
         * `W`. The largest value the loop can reach is therefore
         * `pos + W*floor((lim_ - pos)/W)` whether or not `lim_` was
         * pre-rounded — the bound is SELF-ROUNDING, and an off-lattice cursor
         * has no spelling in this emission at all.
         *
         * MEASURED, twice and from both directions: sabotage S60's first form
         * removed the rounding and came back UNDETECTED across a
         * 202,458-cell differential; the landing panel's soundness critic
         * independently removed it and got byte-identical answers at strides
         * 2 and 3. Convergent, from opposite ends.
         *
         * `<PREFIX>_MRL_CAP` KEEPS THE ROUNDING ANYWAY, and this is the one
         * thing to understand before deleting it as dead code. It is
         * DEFENCE-IN-DEPTH FOR A FUTURE UN-FOLDING: the day a site consumes
         * the cap by ASSIGNING it — a rung that picks a position rather than
         * bounding a loop, which §4.5 says the variable-length boundary-record
         * rung would — the rounding is what keeps that site sound, and it will
         * be there rather than needing to be rediscovered from R26 E1.
         * `run_mrl_tests.sh` cell 2 greps for the DIVISION so that this
         * deliberately-dead defence cannot be quietly removed by a refactor
         * that read "dead" as "deletable".
         *
         * WHAT IS LOAD-BEARING HERE IS THE GUARD ABOVE THE BLOCK. It is what
         * makes the subtraction inside `MRL_CAP` well-defined: a ceiling below
         * `pos + minrest` means no continuation is feasible from here at all,
         * which is a failure and not a clamp. Vacuous, the subtraction wraps,
         * `lim_` becomes enormous and the loop stops bounding the SUBJECT —
         * measured as an ASAN heap-buffer-overflow (sabotage S60's second
         * form, asserted structurally by `run_mrl_tests.sh` §2b).
         *
         * At W = 1 the rounding is the identity in any case. */
        const bool fold = vm_mrl_test(v, "scan_position", mrl, -1,
                                      "MRL: the continuation cannot fit from "
                                      "this loop's entry at all");
        sb_puts(b, "    {\n");
        if (a->u.rep.rmax >= 0) sb_puts(b, "        unsigned long it_ = 0;\n");
        if (fold)
            sb_printf(b, "        const size_t lim_ = %s_PRUNE_CLAMP_SPAN(scan_position, %s, %d);\n",
                      v->up, vm_mrl_amt(v, mrl), stride);
        sb_printf(b, "        %s_span_cursor = scan_position;\n", v->p);
        sb_printf(b, "        while (%s_span_cursor + %d <= %s", v->p, stride,
                  fold ? "lim_" : "subject_length");
        if (a->u.rep.rmax >= 0) sb_printf(b, " && it_ < %dUL", a->u.rep.rmax);
        sb_printf(b, "%s) { %s_span_cursor += %d;", test, v->p, stride);
        if (a->u.rep.rmax >= 0) sb_puts(b, " it_++;");
        sb_puts(b, " }\n    }\n");
        if (fold)
            vm_ev(v, VE_NOTE, 0, 0,
                  "MRL: the clamp IS the scan's own bound, so the doomed suffix "
                  "is never scanned and never retreated over -- and the bound "
                  "is self-rounding, since the cursor only ever moves by W");
        vm_goto(v, retry);

        vm_lbl(v, retry, "span-loop: take the continuation at the cursor");
        sb_printf(b, "    if ((ptrdiff_t)%s_span_cursor < slot_values[%d] + %lld) goto %s_fail;\n",
                  v->p, low, lo_off, v->p);
        vm_ev(v, VE_NOTE, 0, 0, "below the low-water mark: exhausted");
    } else {
        /* LAZY: the shortest acceptable run first, extended one stride per
         * backtrack. Greedy vs lazy is which side is the fallthrough (S2.2
         * property 3) — here the CONTINUATION is, and the frame resumes the
         * extension, exactly mirroring the greedy rung's frame resuming the
         * retreat. Getting this wrong is not a performance difference: `(a*?)a`
         * on "aa" gives [0,2)/g1=[0,1) under a greedy scan where both oracles
         * give [0,1)/g1=[0,0). */
        sb_printf(b, "    %s_span_cursor = scan_position;\n", v->p);
        if (a->u.rep.rmin > 0) {
            sb_puts(b, "    {\n        unsigned long it_ = 0;\n");
            sb_printf(b, "        while (it_ < %dUL) {\n", a->u.rep.rmin);
            sb_printf(b, "            if (!(%s_span_cursor + %d <= subject_length%s)) goto %s_fail;\n",
                      v->p, stride, test, v->p);
            sb_printf(b, "            %s_span_cursor += %d; it_++;\n", v->p, stride);
            sb_puts(b, "        }\n    }\n");
        }
        vm_goto(v, retry);

        vm_lbl(v, retry, "span-loop: take the continuation at the cursor");
        /* [M4.6d] THE LAZY MIRROR, and it needs NO LATTICE ROUNDING (§2.7,
         * R26 V7). A lazy cursor walks UP from the minimum, so the bound caps
         * how far the ascent may go rather than choosing a starting maximum —
         * it TESTS a cursor that is already on the lattice by construction
         * (it started at `pos + rmin*W` and has only ever been incremented by
         * `W`). Copying the greedy expression here would give the same answer
         * and pay for a division it does not need.
         *
         * Placed at the shared continuation label rather than at the
         * extension: every ascent passes through here, and the cursor only
         * ever GROWS, so one doomed arrival means every later one is doomed
         * too and the whole remaining ascent is cut by this one comparison. */
        {
            char cx[64];
            snprintf(cx, sizeof cx, "%s_span_cursor", v->p);
            vm_mrl_test(v, cx, mrl, -1,
                        "MRL: the ascent has passed the last position an "
                        "accepting continuation could attempt_position from");
        }
    }

    {
        char cur[64];
        snprintf(cur, sizeof cur, "%s_span_cursor", v->p);
        vm_push_at(v, again, cur, a->u.rep.greedy
                   ? "shorter run is the resume (retreat one stride)"
                   : "longer run is the resume (extend one stride)");
    }
    if (ncaps) {
        /* Only a loop that ran at least once wrote its groups. Below that the
         * previous value stands, which is what `(a)*` matching zero times must
         * report — and, inside an enclosing loop, is what makes a failed final
         * iteration restore group k to the value the SUCCESSFUL earlier
         * iteration left rather than to unset (S3.2). */
        sb_printf(b, "    if ((ptrdiff_t)%s_span_cursor >= slot_values[%d] + %d) {\n",
                  v->p, low, stride);
        for (int i = 0; i < ncaps; i++) {
            char val[96];
            snprintf(val, sizeof val, "(ptrdiff_t)(%s_span_cursor - %d)", v->p,
                     stride - caps[i].off);
            vm_set(v, 2 * caps[i].group, val,
                   vm_rolef(v, "group %d open, derived from the cursor "
                               "(D44.1: not written per iteration)",
                            caps[i].group));
            snprintf(val, sizeof val, "(ptrdiff_t)(%s_span_cursor - %d)", v->p,
                     stride - caps[i].off - caps[i].len);
            vm_set(v, 2 * caps[i].group + 1, val,
                   vm_rolef(v, "group %d close, derived from the cursor",
                            caps[i].group));
        }
        sb_puts(b, "    }\n");
    }
    sb_printf(b, "    scan_position = %s_span_cursor;\n", v->p);
    vm_goto(v, next);

    vm_lbl(v, again, a->u.rep.greedy ? "span-loop retreat (resumed from the frame)"
                               : "span-loop extend (resumed from the frame)");
    /* the fail label restored pos from this frame, i.e. to the cursor value
     * the push recorded — so the retreat/extension needs no save slot */
    sb_printf(b, "    %s_span_cursor = scan_position;\n", v->p);
    if (a->u.rep.greedy) {
        sb_printf(b, "    if ((ptrdiff_t)%s_span_cursor < slot_values[%d] + %lld + %d) goto %s_fail;\n",
                  v->p, low, lo_off, stride, v->p);
        sb_printf(b, "    %s_span_cursor -= %d;\n", v->p, stride);
    } else {
        if (a->u.rep.rmax >= 0)
            sb_printf(b, "    if ((ptrdiff_t)%s_span_cursor >= slot_values[%d] + %lld) goto %s_fail;\n",
                      v->p, low, (long long)a->u.rep.rmax * stride, v->p);
        sb_printf(b, "    if (!(%s_span_cursor + %d <= subject_length%s)) goto %s_fail;\n",
                  v->p, stride, test, v->p);
        sb_printf(b, "    %s_span_cursor += %d;\n", v->p, stride);
    }
    vm_goto(v, retry);
    sb_free(&t);
}

/* Nested optional chain for a bounded repeat: `X{0,3}` is `(X(X(X)?)?)?`,
 * NESTED and not chained. The two accept the same language and differ in
 * BACKTRACK PREFERENCE — with chained optionals a later copy's alternation
 * choice outranks an earlier copy's, so lazy bounded repeats pick the wrong
 * span. nfa.c's A_REP arm carries the measurement that found this
 * (`(?:ab|a){0,2}?b` on "abab" gave [0,2) where PCRE2 and python give [0,4)),
 * and the VM must make the same choice for the same reason. */
static void vm_opt_chain(Vm *v, int entry, const Ast *body, int count,
                         int next, bool greedy, long long bw)
{
    if (count <= 0) {
        vm_lbl(v, entry, "bounded repeat: all optional copies exhausted");
        vm_goto(v, next);
        return;
    }
    int bentry = vm_label(v), other = vm_label(v), inner = vm_label(v);
    vm_lbl(v, entry, vm_rolef(v, "optional copy (%d remaining), %s",
                              count, greedy ? "greedy" : "lazy"));
    /* [M4.6d] CUT BEFORE PUSH, in the literal sense the design names it. If
     * one more iteration plus everything after the loop cannot fit in what
     * remains, the BODY branch has no accepting leaf — so the skip is the
     * only survivor and the frame that would have offered the other branch is
     * never pushed.
     *
     * ONE test covers the whole rest of the chain: every later copy is
     * entered at this same position with this same minrest, so a doomed copy
     * here means a doomed copy at every level below, and jumping straight to
     * `next` skips them all. That is also why the emitted answer is the same
     * for both preferences — `next` is the greedy fallback and the lazy
     * fallthrough alike, which is §2.8's preference-blindness showing up as
     * one line of code instead of two. */
    vm_mrl_test(v, "scan_position", vm_fadd(bw, v->fmin), next,
                "MRL: no room for another iteration and the follow -- take "
                "the skip, push nothing");
    if (greedy) {
        vm_push(v, other, "body preferred; resume SKIPS this copy");
        vm_goto(v, bentry);
    } else {
        vm_push(v, other, "skip preferred; resume TAKES this copy");
        vm_goto(v, next);
    }
    vm_lbl(v, other, greedy ? "optional copy: the skip"
                            : "optional copy: the body");
    vm_goto(v, greedy ? next : bentry);
    /* The copy's own follow is the loop's follow: what comes after THIS copy
     * is a chain of OPTIONAL copies (minimum width 0) and then the
     * continuation. Nothing to add, which is why this reads as an inherit. */
    vm_emit(v, bentry, body, inner);
    vm_opt_chain(v, inner, body, count - 1, next, greedy, bw);
}

/* [ENG-BREP] The possessified frames rung, bounded: `X{m,n}` after its `m`
 * mandatory copies, with `count` optional copies left to run.
 *
 * The shape, and why it is not simply vm_opt_chain minus the pushes. In this
 * VM a frame serves TWO purposes at an optional copy — resume when the
 * CONTINUATION fails (retreat into the loop), and resume when the BODY fails
 * (this copy cannot run, so exit the loop). Possessification kills the first
 * and leaves the second completely alive: `(?:a|bc){0,4}d` still has to notice
 * that neither branch matches and leave the loop. Deleting the push would
 * break that, which is why this is a different emission rather than a smaller
 * one.
 *
 * So exactly ONE loop frame is live at a time, whatever the count:
 *
 *     Lj:  CUT(mark)          <- the previous copy is committed; its frames,
 *                                and its body's, are dead by the verdict
 *          PUSH(exit, pos)    <- the only loop frame: if this copy's body
 *                                fails, resume here with pos back at the
 *                                start of the copy that failed
 *          <body>  -> L(j+1)
 *     L(count+1): CUT(mark); goto next     <- every copy taken
 *     exit:       goto next                <- the pop already restored pos,
 *                                             and left resume_depth exactly at mark
 *
 * The body's OWN frames are not disturbed while it runs, which matters: a
 * one-unambiguous body still needs them to FIND its match (`(?:a|bc)` on "bc"
 * tries `a` first and backtracks). One-unambiguity says at most one branch can
 * SUCCEED, not that the emitter guesses right — so the cut is at the copy
 * boundary, where the previous body has already succeeded, and never inside
 * one.
 *
 * The frame requirement is therefore `1 + body` instead of
 * `(n-m) * (1 + body)`, and it no longer depends on the count at all. That is
 * the §7 prediction about `rx_info`'s stamped ceiling, and vm_cost_rep carries
 * the matching arithmetic. */
static void vm_poss_chain(Vm *v, int entry, const Ast *body, int count,
                          int next, int mslot, long long bw, bool pref_ok)
{
    int exitl = vm_label(v);
    /* [M6.4.2] THE PREFERENCE PRECONDITION, CHECKED. This rung takes no
     * `greedy` parameter and never reads one — `vm_opt_chain` above does —
     * because :2053-2062 argues the PREFERENCE COLLAPSE as a §2.2 CONSEQUENCE:
     * under disjointness a greedy loop tops out by preference and a LAZY one
     * is FORCED to the same top, so one emitted shape is correct for both.
     *
     * SO THE LICENCE IS "GREEDY **OR** §2.2-PROVED", not "greedy". A lazy
     * quantifier with a POSITIVE verdict is legitimately possessified today —
     * measured on all six dispatch paths — and the collapse is sound there
     * BECAUSE the verdict holds. What has no licence is a cut that arrives
     * with NO verdict: a LIFTED user-written possessive over a lazy body,
     * where 7 of 8 eligible cells miscompile (`(?>a*?)b` on "aaab" is (3,4) in
     * both oracles and (0,4) through the lift). `vm_lifts` refuses those, and
     * this is the checked restatement — a precondition a new caller can
     * silently violate is the shape R31's E1 and N1 are both made of. */
    if (!pref_ok)
        ctx_fail(v->cx, 0,
                 "internal error: the possessified bounded rung was given a "
                 "LAZY body with no §2.2 verdict behind it. Its shape ignores "
                 "preference, which that verdict is what licenses");
    int cur = entry;

    for (int j = 0; j < count; j++) {
        int bentry = vm_label(v), after = vm_label(v);
        vm_lbl(v, cur, vm_rolef(v, "possessified optional copy (%d remaining)",
                                count - j));
        vm_cut(v, mslot,
               "cut: the previous copy is committed, its choice points are dead");
        /* [M4.6d] cut before push, on the possessive arm too. The one frame
         * this copy would push exists to notice that the body cannot run;
         * where MRL already knows it cannot, the frame is pure cost. */
        vm_mrl_test(v, "scan_position", vm_fadd(bw, v->fmin), next,
                    "MRL: no room for another copy and the follow");
        vm_push_at(v, exitl, "scan_position",
                   "the loop's ONLY frame: this copy failing leaves the loop");
        vm_goto(v, bentry);
        vm_emit(v, bentry, body, after);
        cur = after;
    }

    vm_lbl(v, cur, "possessified repeat: every copy taken");
    vm_cut(v, mslot, "cut: the loop is complete and owns no live choice point");
    vm_goto(v, next);

    if (count > 0) {
        vm_lbl(v, exitl, "possessified repeat: a copy could not run -- exit "
                         "with the iterations that did");
        /* The pop restored `pos` to this copy's start AND left the resume
         * stack at exactly `mark`, because the frame it popped was the one
         * this loop pushed at that depth. Nothing to undo. */
        vm_goto(v, next);
    } else {
        /* X{m,m}: no optional copy, so nothing ever pushed `exitl`. The label
         * is still emitted so the listing's label set matches the artifact's
         * — vm_lbl is the only way to emit one, and a label the emitter
         * allocated but never wrote would break that correspondence. */
        vm_lbl(v, exitl, "possessified repeat: unreachable (exact count)");
        vm_goto(v, next);
    }
}

/* [ENG-BREP] The possessified frames rung, UNBOUNDED (`X{m,}`). Same one-frame
 * discipline as the bounded chain, with the copies replaced by a real loop.
 *
 * NO EMPTY-ITERATION GUARD IS NEEDED, and that is structural rather than an
 * omission. §3.3's guard exists to stop a NULLABLE body iterating forever;
 * §2.2's rule refuses to possessify a nullable body at all, and the two
 * nullability predicates are the same function computed twice — src/opt/
 * possessify.c's Glushkov nullability (A_CLASS false, zero-width true, CAT
 * and, ALT or, REP `|| rmin == 0`, A_CAP transparent) is `vm_nullable` above,
 * arm for arm. So `a->u.rep.possessive` on an unbounded repeat implies
 * `!vm_nullable(a->l)`, every iteration consumes at least one byte, and the
 * loop terminates on the subject rather than on a guard. */
static void vm_poss_star(Vm *v, int entry, const Ast *body, int next, int mslot,
                         long long bw, bool pref_ok)
{
    int bentry = vm_label(v), bend = vm_label(v), exitl = vm_label(v);
    /* [M6.4.2] BOTH PRECONDITIONS, CHECKED rather than commented, because a
     * precondition a NEW CALLER can silently violate is the shape R31's E1 and
     * N1 are both made of.
     *
     * NULLABLE: the paragraph above says this rung needs no empty-iteration
     * guard because §2.2 refuses nullable bodies. `(?>(?:a*)*)b` is legal in
     * both oracles, HAS one, and routed here would push and cut at zero
     * consumption forever with no work charge to stop it — sabotage row S100,
     * whose expected result is a TIMEOUT (loud under D45, not a hang).
     *
     * LAZY: see vm_poss_chain's own check for why the licence is "greedy OR
     * §2.2-proved" rather than "greedy". */
    if (vm_nullable(body))
        ctx_fail(v->cx, 0,
                 "internal error: the possessified unbounded rung was given a "
                 "NULLABLE body. It emits no empty-iteration guard, and that "
                 "is licensed by §2.2 refusing such bodies -- not by anything "
                 "this rung does");
    if (!pref_ok)
        ctx_fail(v->cx, 0,
                 "internal error: the possessified unbounded rung was given a "
                 "LAZY body with no §2.2 verdict behind it; its shape ignores "
                 "preference, which that verdict is what licenses");

    vm_lbl(v, entry, "possessified unbounded repeat: one frame for the whole "
                     "loop, however many iterations run");
    vm_cut(v, mslot,
           "cut: the previous iteration is committed, its choice points are dead");
    /* [M4.6d] cut before push. Reached once per iteration, so this also
     * bounds the loop: the first position at which another iteration plus the
     * follow cannot fit ends the loop without a frame. */
    vm_mrl_test(v, "scan_position", vm_fadd(bw, v->fmin), exitl,
                "MRL: no room for another iteration and the follow");
    vm_push_at(v, exitl, "scan_position",
               "the loop's ONLY frame: the iteration failing leaves the loop");
    vm_goto(v, bentry);

    vm_emit(v, bentry, body, bend);

    vm_lbl(v, bend, "possessified unbounded repeat: one iteration done");
    vm_goto(v, entry);

    vm_lbl(v, exitl, "possessified unbounded repeat: the exit");
    /* No cut here: the frame this loop pushed sat at depth `mark`, so popping
     * it left the stack there already, and the body's frames above it were
     * popped on the way. */
    vm_goto(v, next);
}

/* ---- [ENG-BREP] the REVERSE-DETERMINISTIC rung ---------------------------
 *
 * engine_m4.md §2.5's rung, between the cursor and the frames. Design and the
 * full derivation: docs/design/rungselect_impl/rungselect_design.md.
 *
 * ONE body copy instead of `rmax` of them. The emitted loop is a deterministic
 * FORWARD SCAN that counts iterations, ONE resume frame for the whole loop, and
 * a BACKWARD WALK over the reversed body that serves two jobs at once — it
 * finds the previous iteration boundary for a retreat, and it recovers §3.4's
 * last-iteration captures.
 *
 * THE BACKWARD WALK HAS NO CHOICE POINTS, and that is the rung's name made
 * concrete. src/opt/revdet.c only selects the rung when the REVERSED body is
 * one-unambiguous, so at an alternation the next byte decides the branch and
 * the walk dispatches on it instead of pushing a frame per branch. A failure
 * anywhere in a step is therefore final for that step, which is why every
 * failure edge below goes to ONE label (the walk's end) rather than to
 * `rx_fail`.
 *
 * IT NEVER TOUCHES `pos`. The walk is a DERIVATION, not a move: it runs on its
 * own cursor local, so the boundary the loop committed at is still `pos` when
 * the walk finishes and the continuation is taken. */
typedef struct {
    const char *cur;    /* the walk's own cursor local */
    const char *floor;  /* the loop's entry position, as a slot_values read */
    const char *ga;     /* the capture-recovery locals: spans */
    const char *gs;     /* ... and their seen flags */
    const char *ns;     /* the seen counter */
    const int  *grp;    /* body group numbers, in the dense index's order */
    int         ngrp;
    int         faill;  /* where any failure in a step lands */
} Rev;

static int vm_rev_index(const Rev *R, int capno)
{
    for (int i = 0; i < R->ngrp; i++) if (R->grp[i] == capno) return i;
    return -1;
}

static void vm_rev_emit(Vm *v, int entry, const Ast *a, int next, const Rev *R)
{
    StrBuf *b = v->b;
    char byte[80];
    vm_charge(v);
    snprintf(byte, sizeof byte, "subject[%s - 1]", R->cur);

    switch (a->k) {
    case A_CLASS: {
        int ci = vm_cls(v, a->u.cls.bits);
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_CLASS, ci, next, "consumed BACKWARD");
        sb_printf(b, "    if (%s > %s && (", R->cur, R->floor);
        vm_cls_test(v, b, ci, byte);
        sb_printf(b, ")) { %s--; goto %s_L%d; }\n", R->cur, v->p, next);
        vm_goto(v, R->faill);
        return;
    }
    case A_CAP: {
        /* §3.4's rule, delivered by the direction of travel. Going backward the
         * FIRST time a group is met is the LAST iteration that ENTERED it,
         * which is exactly the value PCRE2 reports — and exactly what the plan
         * row's constant-offset formula got wrong on 1,799 of 15,036 matches,
         * because a later iteration taking the other branch does not CLEAR a
         * group an earlier one wrote.
         *
         * The writes go to LOCALS, not through RX_SET. Two reasons and both are
         * load-bearing: the values must be published AFTER the loop's resume
         * frame is pushed (so a retreat rewinds them rather than accumulating
         * them, the cursor rung's own ordering rule), and a walk that wrote
         * through the trail would cost entries per ITERATION where publishing
         * costs them per GROUP.
         *
         * A partially-written group is harmless: `seen` is set only at the
         * group's left edge, i.e. only once the whole group has matched, so a
         * step that dies in the middle leaves a stale span nobody publishes. */
        int j = vm_rev_index(R, a->u.cap.no);
        int inner = vm_label(v), close = vm_label(v);
        vm_lbl(v, entry, vm_rolef(v, "group %d: its END, met first going backward",
                                  a->u.cap.no));
        if (j >= 0)
            sb_printf(b, "    if (!%s[%d]) %s[%d][1] = (ptrdiff_t)%s;\n",
                      R->gs, j, R->ga, j, R->cur);
        vm_goto(v, inner);
        vm_rev_emit(v, inner, a->l, close, R);
        vm_lbl(v, close, vm_rolef(v, "group %d: its START -- the last iteration "
                                     "that entered it wins", a->u.cap.no));
        if (j >= 0)
            sb_printf(b, "    if (!%s[%d]) { %s[%d][0] = (ptrdiff_t)%s;"
                         " %s[%d] = 1; %s++; }\n",
                      R->gs, j, R->ga, j, R->cur, R->gs, j, R->ns);
        vm_goto(v, next);
        return;
    }
    case A_CAT: {
        /* The tree is ALREADY reversed (src/opt/revdet.c swapped every A_CAT's
         * children), so this walks it in the ordinary left-to-right way and the
         * reversal is not re-applied here. Spine flattened iteratively for
         * nfa.c's R-2 reason. */
        int nsp = 0;
        const Ast *t = a;
        while (t->k == A_CAT) { nsp++; t = t->l; }
        const Ast **rs = arena_alloc(&v->cx->arena, (size_t)nsp * sizeof(Ast *));
        int i = nsp;
        t = a;
        while (t->k == A_CAT) { rs[--i] = t->r; t = t->l; }
        int cur = entry, nx = vm_label(v);
        vm_rev_emit(v, cur, t, nx, R);
        cur = nx;
        for (int j = 0; j < nsp; j++) {
            int after = (j + 1 == nsp) ? next : vm_label(v);
            vm_rev_emit(v, cur, rs[j], after, R);
            cur = after;
        }
        return;
    }
    case A_ALT: {
        /* THE BYTE DECIDES, so there is no frame here. Reverse one-unambiguity
         * makes the branches' first sets pairwise disjoint — checked directly
         * on this tree by src/opt/revdet.c's `rd_alt_disjoint`, at the place the
         * emitter depends on it rather than inherited from (U1) three functions
         * away — so at most one test below can succeed and a branch that fails
         * after being chosen has no alternative to try. */
        int nbr = 1;
        for (const Ast *t = a; t->k == A_ALT; t = t->l) nbr++;
        const Ast **br = arena_alloc(&v->cx->arena, (size_t)nbr * sizeof(Ast *));
        int i = nbr;
        const Ast *t = a;
        while (t->k == A_ALT) { br[--i] = t->r; t = t->l; }
        br[0] = t;
        int *bentry = arena_alloc(&v->cx->arena, (size_t)nbr * sizeof(int));
        for (int j = 0; j < nbr; j++) bentry[j] = vm_label(v);

        vm_lbl(v, entry, vm_rolef(v, "backward alternation (%d branches):"
                                     " the byte selects, no frame", nbr));
        sb_printf(b, "    if (%s <= %s) goto %s_L%d;\n",
                  R->cur, R->floor, v->p, R->faill);
        for (int j = 0; j < nbr; j++) {
            uint8_t f[32];
            pcrec_revdet_first(br[j], f);
            int ci = vm_cls(v, f);
            sb_puts(b, "    if (");
            vm_cls_test(v, b, ci, byte);
            sb_printf(b, ") goto %s_L%d;\n", v->p, bentry[j]);
        }
        vm_goto(v, R->faill);
        for (int j = 0; j < nbr; j++) vm_rev_emit(v, bentry[j], br[j], next, R);
        return;
    }
    case A_REP: {
        /* Only an EXACT count reaches here (revdet.c's shape scan declines
         * every other kind), and an exact count is literal replication, which
         * reverses to literal replication of the reversed sub-body. */
        int cur = entry;
        for (int i = 0; i < a->u.rep.rmin; i++) {
            int nx = (i + 1 == a->u.rep.rmin) ? next : vm_label(v);
            vm_rev_emit(v, cur, a->l, nx, R);
            cur = nx;
        }
        return;
    }
    default:
        /* [M6.6.2] RE-INSPECTED FOR `A_LOOK`, the fourth and last of design
         * §11's `default:`-carrying sites. SOUND AND LOUD: this falls to a
         * hard compile error rather than a silent accept, which is the right
         * outcome, because a lookaround reaching the BACKWARD WALK would mean
         * the reversed body contains one — a thing that has no meaning (design
         * §3.5 lowers even a lookbehind with a FORWARD body). It is now
         * doubly unreachable: `rd_shape` declines the body, and `rd_reverse`
         * raises its own named error before this walk is ever emitted.
         *
         * [DD-14] RE-INSPECTED BY HAND FOR `A_CALL` (design §4.4a site 7),
         * SOUND AND LOUD WITH NO ARM ADDED — and §4.4a records that this
         * default is REACHABLE IN A NEW WAY for this construct: a call can
         * carry a WHOLE SUBTREE into the backward walk rather than a single
         * node, because `u.call.body` names one. What keeps that a diagnostic
         * rather than a miscompile is the FIVE DECLINES in src/opt/revdet.c
         * (sites 14-18) — `rd_shape` refuses the body, so no reversed program
         * containing a call is ever built, and `rd_reverse` raises its own
         * named `A_CALL` error if one somehow is. The hard `ctx_fail` below is
         * the third layer, and a silent accept here would emit a backward walk
         * that simply skipped the call. */
        break;
    }
    ctx_fail(v->cx, 0, "internal error: bad AST node in the backward walk");
}

static void vm_revdet_rep(Vm *v, int entry, const Ast *a, int next,
                          bool under_atomic)
{
    StrBuf *b = v->b;
    const bool cuts = vm_cuts(a, under_atomic);
    const int loop = v->nrev++;
    const int se = vm_slot_rev(v, loop, 0);
    const int sl = vm_slot_rev(v, loop, 1);
    const int sh = vm_slot_rev(v, loop, 2);
    const bool move   = vm_rev_canmove(a, cuts);
    const bool greedy = a->u.rep.greedy;
    int grp[PCREC_MAX_REVDET_BODY_GROUPS];
    int ng = 0;
    vm_rev_caps(a->l, grp, &ng, PCREC_MAX_REVDET_BODY_GROUPS);
    /* The walk runs when something needs it: a GREEDY loop that can move needs
     * the previous boundary, and any loop with groups needs their values. A
     * lazy loop moves FORWARD, so it needs the walk only for captures. */
    const bool walk = (greedy && move) || ng > 0;

    /* One named scalar per field per loop, rather than one array of structs.
     * Not a style choice: the emitted matcher is built -Wall -Wextra -Werror,
     * and gcc cannot see through a computed-goto control flow well enough to
     * prove an array element is written before it is read, so the array form
     * failed -Wmaybe-uninitialized on four corpus patterns. A scalar carries
     * its own `= 0` at its declaration and the question does not arise. */
    char rv[80], cur[96], flr[32];
    snprintf(rv,  sizeof rv,  "%s_rv%d", v->p, loop);
    snprintf(cur, sizeof cur, "%s_rv%d_cursor", v->p, loop);
    snprintf(flr, sizeof flr, "(size_t)slot_values[%d]", se);

    char bounds[32];
    if (a->u.rep.rmax < 0) snprintf(bounds, sizeof bounds, "{%d,}", a->u.rep.rmin);
    else             snprintf(bounds, sizeof bounds, "{%d,%d}", a->u.rep.rmin, a->u.rep.rmax);
    const char *role = vm_rolef(v, "reverse-deterministic rung %s, %s%s"
                                   " -- ONE body copy, no replication",
                                bounds, greedy ? "greedy" : "lazy",
                                !cuts ? ""
                                  : a->u.rep.possessive ? ", POSSESSIFIED"
                                                  : ", ATOMIC (a written cut)");

    int scanl = vm_label(v), bodyl = vm_label(v), bodyok = vm_label(v);
    int shortl = vm_label(v), fulll = vm_label(v), commitl = vm_label(v);
    int walkl = 0, revl = 0, wstepl = 0, wendl = 0, extl = 0, extbl = 0, extok = 0;
    if (walk) {
        walkl = vm_label(v); revl = vm_label(v);
        wstepl = vm_label(v); wendl = vm_label(v);
    }
    if (move && !greedy) {
        extl = vm_label(v); extbl = vm_label(v); extok = vm_label(v);
    }

    /* ---- entry ---------------------------------------------------------- */
    vm_lbl(v, entry, role);
    /* [M6.4.2] THE STAMP REPORTS WHAT WAS EMITTED, which for a LIFTED
     * possessive is the cutting shape. §6.4(c) of the design says the stamp
     * "stays exactly possessify's verdict" so that `--list-rungs` consumers
     * can keep reading it as the optimisation's own verdict; that sentence is
     * about `Ast.u.rep.possessive` (RULE 2, which holds — this module never writes
     * the field) and it does not survive the LIFT, which genuinely routes a
     * semantic possessive onto this rung. A STRATS of BACKTRACKING on an
     * artifact whose loop cuts is a D46 stamp that lies, and it is the exact
     * class of lie K29 was opened for. Reported as a deliberate deviation. */
    vm_rung_mark(v, entry, VM_RUNG_REVDET, cuts, role);
    /* [M4.6d] PREDICTION 6, answered. k23_design.md §4.5 and §13's prediction 6
     * expected this rung to need its own lattice argument and NOT to get it
     * from §4.1's division, because its iteration boundaries are recovered by
     * a BACKWARDS WALK rather than by arithmetic. Both halves are right, and
     * the consequence is the opposite of the one predicted: the argument is
     * re-made here, and it is SIMPLER than the cursor rung's, not harder.
     *
     * The cursor rung has to ROUND because it assigns — it picks a cursor
     * value out of a range and must land on `pos + W*k`. This rung never
     * assigns a boundary at all. Its FORWARD SCAN is itself the walk onto the
     * boundary set: every value `pos` takes during the scan is a boundary the
     * body actually matched, by construction. So the bound is applied by
     * STOPPING the walk one boundary early — the TEST form, at the scan's own
     * loop head, cutting before the frame is pushed — and the position it
     * stops at is a member of the choice set for exactly the reason `pos +
     * W*k` is one on the cursor rung. There is nothing to round, and the E1
     * class of bug (substituting a position the loop cannot occupy) is not
     * expressible here: no code path writes a boundary this rung did not
     * reach by matching the body.
     *
     * The retreat chain needs no bound of its own, and that is the second
     * half. It walks BACKWARDS from the committed boundary, so every position
     * it visits has MORE bytes remaining than the one the bound already
     * admitted — the whole chain below a viable commit is viable. Pruning it
     * would be dead code, which is why none is emitted.
     *
     * NOT the possessive arm's problem either: a possessified revdet loop
     * takes the same scan and the same stop, and the stop is a test rather
     * than a substitution, so vm_cursor_rep's possessive caution does not
     * arise here. */
    const long long F  = v->fmin;
    const long long bw = pcrec_minw(a->l);
    vm_prune_mark(v, entry,
                  v->mrl && (vm_fadd(bw, F) > 0 || v->fdyn != NULL), role);
    vm_set(v, se, "(ptrdiff_t)scan_position",
           "revdet: the loop's entry position (the capture walk's floor)");
    if (a->u.rep.rmin == 0)
        vm_set(v, sl, "(ptrdiff_t)scan_position",
               "revdet: low-water = the entry, since rmin is 0");
    sb_printf(b, "    %s_iteration = 0;\n", rv);
    vm_goto(v, scanl);

    /* ---- the forward scan ------------------------------------------------
     * One body copy, run to the maximal boundary. The CUT at every iteration
     * boundary is what makes the resume stack O(1) in the iteration count, and
     * it is licensed by the forward unique-iteration property: once the body
     * has matched [p,q) there is no other way to match an iteration there, so
     * its internal choice points are provably dead. The cut is at a BOUNDARY
     * and never inside a body — a one-unambiguous body still needs its own
     * frames to FIND its match, which is vm_poss_chain's own recorded lesson. */
    vm_lbl(v, scanl, "revdet scan: try one more iteration");
    if (a->u.rep.rmax >= 0)
        sb_printf(b, "    if (%s_iteration >= %dUL) goto %s_L%d;\n",
                  rv, a->u.rep.rmax, v->p, fulll);
    /* [M4.6d] the stop, and it goes to `shortl` rather than to `fulll` — which
     * is not cosmetic. `fulll` is reached from the rmax test above, where the
     * iteration count is known to have met rmin; an MRL stop can fire at ANY
     * count, so it must pass through the label that checks it. `shortl` is
     * also the resume label of the frame this test skips pushing, and
     * arriving there directly leaves exactly the state that frame's pop would
     * have restored: `pos` is this boundary either way, `it` is untouched, and
     * `run->resume_depth` is already at the depth the pop would have left it. */
    vm_mrl_test(v, "scan_position", vm_fadd(bw, F), shortl,
                "MRL: no room for another iteration and the follow -- stop the "
                "scan on the boundary it is standing on");
    sb_printf(b, "    %s_frame_mark = run->resume_depth;\n", rv);
    vm_push_at(v, shortl, "scan_position",
               "this iteration cannot run -- leave the loop with the ones that did");
    vm_goto(v, bodyl);

    /* Capture writes SUPPRESSED for the whole forward body: they are what would
     * make the trail grow per iteration, and the backward walk recovers every
     * one of them from the committed span.
     *
     * [M4.6d] the body's follow-min is the LOOP's, not the loop's minus this
     * iteration: ONE body copy serves every iteration, so the only sound
     * constant is the weakest one — what must be consumed after the LAST
     * iteration. The rung's own scan-head test above is what recovers the
     * per-iteration strength a replicated rung gets from its copies. */
    v->nocap++;
    vm_emit_f(v, bodyl, a->l, bodyok, F);
    v->nocap--;

    vm_lbl(v, bodyok, "revdet scan: one iteration committed");
    /* [counter-K] THE SECOND SPELLING OF A CUT, and the one the step-charge
     * probe first reported a confident zero for. This is a cut — it discards
     * every frame the body pushed — and it is charged like one, even though it
     * never goes near the RX_CUT macro. */
    {
        char cnt[192];
        snprintf(cnt, sizeof cnt, "(ptrdiff_t)run->resume_depth - (ptrdiff_t)%s_frame_mark", rv);
        vm_work(v, cnt, "work charge: frames discarded by the revdet scan cut");
    }
    sb_printf(b, "    run->resume_depth = %s_frame_mark;\n", rv);
    vm_ev(v, VE_NOTE, 0, 0, "cut to the iteration's entry depth: a unique-iteration"
                            " body has no second parse of what just matched");
    sb_printf(b, "    %s_iteration++;\n", rv);
    if (a->u.rep.rmin > 0) {
        sb_printf(b, "    if (%s_iteration == %dUL) {\n", rv, a->u.rep.rmin);
        vm_set(v, sl, "(ptrdiff_t)scan_position",
               "revdet: low-water = the boundary after rmin iterations");
        sb_puts(b, "    }\n");
    }
    vm_goto(v, scanl);

    /* `it` is read HERE and never at the commit label, which a retreat re-enters
     * long after an outer backtrack may have re-entered the loop and reset it.
     * Everything the commit tests is a slot or `pos`. */
    vm_lbl(v, shortl, "revdet scan: the body could not run at this boundary");
    if (a->u.rep.rmin > 0)
        sb_printf(b, "    if (%s_iteration < %dUL) goto %s_fail;\n", rv, a->u.rep.rmin, v->p);
    vm_goto(v, fulll);

    vm_lbl(v, fulll, "revdet: the forward scan is complete");
    vm_set(v, sh, "(ptrdiff_t)scan_position",
           "revdet: the maximal boundary reached (the lazy extension's ceiling)");
    if (!greedy && move) {
        sb_printf(b, "    scan_position = (size_t)slot_values[%d];\n", sl);
        vm_ev(v, VE_NOTE, 0, 0,
              "lazy: commit at the MINIMUM and extend on backtrack");
    }
    vm_goto(v, commitl);

    /* ---- commit ---------------------------------------------------------- */
    vm_lbl(v, commitl, "revdet: commit at this boundary");
    if (walk) {
        Rev R;
        char ga[64], gs[64], ns[64];
        snprintf(ga, sizeof ga, "%s_revdet_group_span", v->p);
        snprintf(gs, sizeof gs, "%s_revdet_group_seen", v->p);
        snprintf(ns, sizeof ns, "%s_rv%d_groups_seen", v->p, loop);
        R.cur = cur; R.floor = flr; R.ga = ga; R.gs = gs; R.ns = ns;
        R.grp = grp; R.ngrp = ng; R.faill = wendl;

        sb_printf(b, "    %s_cursor = scan_position;\n", rv);
        sb_printf(b, "    %s_prev_position = -1;\n", rv);
        if (ng) {
            sb_printf(b, "    %s_groups_seen = 0;\n", rv);
            sb_printf(b, "    { int i_; for (i_ = 0; i_ < %d; i_++)"
                         " %s_revdet_group_seen[i_] = 0; }\n", ng, v->p);
        }
        vm_goto(v, walkl);

        vm_lbl(v, walkl, "revdet walk: one step back over the committed span");
        sb_printf(b, "    if (%s <= %s) goto %s_L%d;\n",
                  cur, flr, v->p, wendl);
        vm_goto(v, revl);
        vm_rev_emit(v, revl, a->u.rep.revbody, wstepl, &R);

        vm_lbl(v, wstepl, "revdet walk: landed on the previous boundary");
        sb_printf(b, "    if (%s_prev_position < 0) %s_prev_position = (ptrdiff_t)%s;\n",
                  rv, rv, cur);
        if (ng) {
            sb_printf(b, "    if (%s_groups_seen >= %d) goto %s_L%d;\n",
                      rv, ng, v->p, wendl);
            vm_goto(v, walkl);
        } else {
            vm_ev(v, VE_NOTE, 0, 0,
                  "no group to witness: one step is all the retreat needs");
            vm_goto(v, wendl);
        }
        vm_lbl(v, wendl, "revdet walk: done (all groups witnessed, or the "
                         "loop's entry reached)");
    }

    /* The frame is pushed BEFORE the captures are published, so its trail mark
     * sits below them and every retreat rewinds the previous commit's values
     * instead of accumulating them (the cursor rung's own ordering rule). */
    if (move) {
        if (greedy) {
            char pv[112];
            snprintf(pv, sizeof pv, "(size_t)%s_prev_position", rv);
            sb_printf(b, "    if ((ptrdiff_t)scan_position > slot_values[%d] && %s_prev_position >= 0) {\n",
                      sl, rv);
            vm_push_at(v, commitl, pv,
                       "retreat: resume this very label with scan_position at the "
                       "PREVIOUS boundary, and re-derive from there");
            sb_puts(b, "    }\n");
        } else {
            sb_printf(b, "    if ((ptrdiff_t)scan_position < slot_values[%d]) {\n", sh);
            vm_push_at(v, extl, "scan_position",
                       "extend: one more iteration is the lazy resume");
            sb_puts(b, "    }\n");
        }
    }
    for (int j = 0; j < ng; j++) {
        char val[64];
        sb_printf(b, "    if (%s_revdet_group_seen[%d]) {\n", v->p, j);
        snprintf(val, sizeof val, "%s_revdet_group_span[%d][0]", v->p, j);
        vm_set(v, 2 * grp[j], val,
               vm_rolef(v, "group %d open, recovered by the backward walk",
                        grp[j]));
        snprintf(val, sizeof val, "%s_revdet_group_span[%d][1]", v->p, j);
        vm_set(v, 2 * grp[j] + 1, val,
               vm_rolef(v, "group %d close, recovered by the backward walk",
                        grp[j]));
        sb_puts(b, "    }\n");
    }
    vm_ev(v, VE_NOTE, 0, 0, "a group the walk never witnessed keeps its previous"
                            " value -- which is §3.4's ZERO-ITERATION clause at"
                            " the boundary where the loop never ran");
    vm_goto(v, next);

    /* ---- the lazy extension --------------------------------------------- */
    if (move && !greedy) {
        vm_lbl(v, extl, "revdet: extend by one iteration (lazy resume)");
        /* [M4.6d] the lazy mirror of the scan-head stop. The extension only
         * ever moves FORWARD, so the first boundary at which another
         * iteration plus the follow cannot fit exhausts the whole ascent —
         * and unlike the scan's stop this one FAILS, because there is no
         * shorter alternative left to fall back to: the shorter ones were
         * already tried, which is what "lazy" means. */
        vm_mrl_test(v, "scan_position", vm_fadd(bw, F), -1,
                    "MRL: the lazy ascent has nowhere left to go");
        sb_printf(b, "    %s_frame_mark = run->resume_depth;\n", rv);
        vm_goto(v, extbl);
        v->nocap++;
        vm_emit_f(v, extbl, a->l, extok, F);
        v->nocap--;
        vm_lbl(v, extok, "revdet: the extra iteration matched");
        {
            char cnt[192];
            snprintf(cnt, sizeof cnt, "(ptrdiff_t)run->resume_depth - (ptrdiff_t)%s_frame_mark", rv);
            vm_work(v, cnt, "work charge: frames discarded by the revdet "
                            "extra-iteration cut");
        }
        sb_printf(b, "    run->resume_depth = %s_frame_mark;\n", rv);
        vm_goto(v, commitl);
        /* The body FAILING here needs no frame of its own: the push above only
         * happens below `hi`, and below `hi` the chain guarantees a next
         * boundary — so a failure means this path is genuinely exhausted, which
         * is what falling through to rx_fail already means. */
    }
}

/* [ENG-BREP counter-K] §3.1's MANDATORY PHASE: m iterations, no choice point
 * at the loop level.
 *
 *   L_min:    RX_SET(ctr, 0)
 *   L_mtrip:  if (slot_values[ctr] + K > m) goto L_mtail
 *             <K copies of the body>       ; no PUSH: a mandatory copy that
 *             RX_SET(ctr, slot_values[ctr] + K)    ; fails fails the whole quantifier
 *             goto L_mtrip
 *   L_mtail:  <m mod K copies>             ; the residue, as emitted today
 *             goto next
 *
 * WHY NO PUSH ANYWHERE IN IT. A mandatory copy is not optional: if it cannot
 * match, the quantifier cannot match, and falling through to `rx_fail` is
 * already the right answer. The BODY's own choice points still push, which is
 * the whole reason the counter has to be trailed.
 *
 * THE RESIDUE IS A COMPILE-TIME CONSTANT, not a runtime remainder. `L_mtail`
 * is reachable only through the trip guard, and `slot_values[ctr]` is only ever 0 or
 * incremented by exactly K, so the tail is entered at ctr = K*floor(m/K) and
 * the residue is exactly `m mod K` copies. eng_brep_design.md §4.2 writes the
 * tail as "(n - slot_values[ctr]) copies", which reads as a runtime quantity; it is
 * not, and that is what keeps the tail as ordinary replication at a smaller
 * count rather than something new.
 *
 * THE COUNTER IS WRITTEN ONCE PER TRIP, not per iteration — a second,
 * independent reason K > 1 pays, and one the §4.4 curves do not measure: the
 * counter's trail cost is 1/K per iteration. Inside a trip the K copies are
 * distinct code and the program counter distinguishes them, which is
 * replication's own encoding used at scale K. */
static void vm_opt_chain(Vm *v, int entry, const Ast *body, int count,
                         int next, bool greedy, long long bw);
static void vm_poss_chain(Vm *v, int entry, const Ast *body, int count,
                          int next, int mslot, long long bw, bool pref_ok);
static void vm_star(Vm *v, int cur, const Ast *a, int next);

/* ONE PHASE of the counter rung: `count` iterations, K at a time, with the
 * `count mod K` residue emitted by the caller's own tail.
 *
 * The two phases differ in exactly one way and share everything else, which is
 * why they are one function: the MANDATORY phase pushes nothing (a mandatory
 * copy that fails fails the whole quantifier, so falling through to rx_fail is
 * already right), while the OPTIONAL phase pushes one frame per iteration
 * because each iteration is a choice point.
 *
 * WHY A LOOP IS NEST-EQUIVALENT AND NOT CHAIN-EQUIVALENT, which is the one
 * place getting this shape wrong is a MEASURED live defect rather than a
 * slowdown. `vm_opt_chain` emits X{0,3} as (X(X(X)?)?)? -- NESTED -- and its
 * own comment records why: with CHAINED optionals a later copy's alternation
 * choice outranks an earlier copy's, and `(?:ab|a){0,2}?b` on "abab" gives
 * [0,2) where PCRE2 and python give [0,4).
 *
 * A counter loop LOOKS like a chain and is not. An iteration's skip frame
 * means "the loop ran j-1 times and then left", which is identical to the
 * nested form's `other` label; the frames are pushed in the same order and
 * popped LIFO in the same order, so the preference sequence is the same --
 * n, n-1, ..., 0 greedy and 0, 1, ..., n lazy. What a CHAIN would additionally
 * admit is skipping copy 1 and taking copy 2, and a loop structurally cannot
 * express that. Unrolling does not disturb it: at K > 1 the pushes occur in
 * the same order and mean the same thing. */
static void vm_counter_phase(Vm *v, int entry, const Ast *a, int count,
                             int next, int ctr, bool optional, long long bw)
{
    StrBuf *b = v->b;
    const int K = v->unroll_k;
    const int residue = count % K;
    /* [M4.6d] the loop's follow-min, taken before anything below changes it —
     * and, for a MANDATORY phase, what the phase's own RESIDUE adds to it.
     *
     * The residue is not optional and it is not somewhere else: every exit
     * from the trip loop lands on `tail`, which emits `count mod K`
     * replicated copies before handing over. So a copy inside a trip is
     * followed by the rest of its trip AND those copies AND the loop's own
     * follow. Leaving the residue out is sound (an under-estimate always is)
     * and it is exactly what stops K23's exemplar collapsing: at K = 8 and
     * rmin = 10 it under-counts by two whole iterations, which is enough
     * slack at the first copy for the ambiguity to survive. Found by
     * measuring the exemplar rather than by reading the code. */
    const long long F   = v->fmin;
    const long long res = optional ? 0 : vm_fmul(count % K, bw);
    const long long TF  = vm_fadd(F, res);
    const int trip = vm_label(v);
    const int tail = vm_label(v);
    const int skip = optional ? vm_label(v) : -1;

    vm_lbl(v, entry, optional ? "counter: optional phase begins"
                              : "counter: mandatory phase begins");
    /* The reset is TRAILED like every other write to this slot, and that is
     * what makes ONE slot serve both phases (§2.3, RULED): a resume into a
     * MANDATORY-phase body frame rewinds past the optional phase's reset and
     * recovers the mandatory count. */
    vm_set(v, ctr, "0", "counter rung: iteration counter (trailed)");
    vm_goto(v, trip);

    {
        int body0 = vm_label(v);
        int cur;
        vm_lbl(v, trip, "counter trip: another K iterations, or the residue");
        sb_printf(b, "    if (slot_values[%d] + %d > %d) goto %s_L%d;\n",
                  ctr, K, count, v->p, tail);
        vm_ev(v, VE_NOTE, 0, 0,
              "trip guard: the residue is a compile-time constant");
        /* [M4.6d] ONCE PER TRIP, which is §4.5's own recommendation for this
         * rung and is where the design says the check's natural home is. Past
         * the guard, K MANDATORY iterations are certain to run, so `K*bw + F`
         * is a sound compile-time minrest and a position short of it fails
         * the quantifier outright.
         *
         * Once-per-trip prunes by a factor of K less often than
         * once-per-iteration would, and stays sound for the reason a check
         * omitted is always sound: pruning forgone, never an answer changed.
         * The runtime-expression form §4.5 sketches
         * (`max(0, rmin - slot_values[ctr]) * bw + F`, reading the counter) is
         * strictly stronger and is NOT taken in v1 — it puts a load, a
         * multiply and a subtract on the trip path to tighten a bound whose
         * population nobody has measured. Recorded as a residual rather than
         * guessed at. */
        /* [M4.6d] THE RUNTIME FOLLOW-MIN (§4.5), and this rung is the only
         * place it is needed. One body copy serves every trip, so the
         * compile-time view sees at most `K + residue` iterations of follow
         * where the truth is `count - slot_values[ctr] - j`. On `(a{1,3}){65}` those
         * are 9 and 65: the compile-time bound leaves the whole ambiguous
         * decomposition alive, and the blinded test author measured exactly
         * that before this expression existed. The counter is a TRAILED slot
         * (R25 E5), so a resume into a body frame restores the right value
         * and the expression is correct on the backtracking path too. */
        if (!optional) {
            const char *dyn = NULL;
            if (v->mrl && bw > 0) {
                dyn = vm_dyn_add(v, v->fdyn,
                                 vm_rolef(v, "%lld * ((ptrdiff_t)%d - slot_values[%d])",
                                          bw, count, ctr));
            }
            {
                const char *sd = v->fdyn;
                v->fdyn = dyn ? dyn : v->fdyn;
                vm_mrl_test(v, "scan_position", dyn ? F : vm_fadd(vm_fmul(K, bw), TF), -1,
                            dyn ? "MRL: the mandatory iterations still owed "
                                  "(counter-derived) plus the follow do not fit"
                                : "MRL: this trip's K mandatory iterations, the "
                                  "residue and the follow do not fit");
                v->fdyn = sd;
            }
        }
        vm_goto(v, body0);
        cur = body0;
        for (int i = 0; i < K; i++) {
            int nx = vm_label(v);
            /* Within a MANDATORY trip, `K - 1 - i` further copies are certain
             * to run after this one; within an OPTIONAL trip none is, so the
             * body inherits the loop's own follow. */
            const long long cf = optional ? F
                                          : vm_fadd(vm_fmul(K - 1 - i, bw), TF);
            if (!optional) {
                /* Copy `i` is followed by `count - slot_values[ctr] - (i+1)` further
                 * MANDATORY iterations -- across the rest of this trip, every
                 * later trip, and the residue, all of which are certain to
                 * run. The compile-time `cf` above is the same quantity seen
                 * from inside one trip, and the two agree exactly at the LAST
                 * trip; everywhere else the runtime form is larger, which is
                 * the whole point. */
                const char *dyn = NULL;
                if (v->mrl && bw > 0) {
                    dyn = vm_dyn_add(v, v->fdyn,
                                     vm_rolef(v, "%lld * ((ptrdiff_t)%d - slot_values[%d])",
                                              bw, count - (i + 1), ctr));
                }
                if (dyn) vm_emit_fd(v, cur, a->l, nx, F, dyn);
                else     vm_emit_f(v, cur, a->l, nx, cf);
            } else if (a->u.rep.greedy) {
                /* GREEDY: the body is the preferred path and LEAVING is the
                 * resume, so the frame carries the skip label. */
                int bodyl = vm_label(v);
                vm_lbl(v, cur, "counter iteration (greedy): body preferred");
                vm_mrl_test(v, "scan_position", vm_fadd(bw, F), skip,
                            "MRL: no room for another iteration and the follow");
                vm_push(v, skip, "greedy: leaving the loop here is the resume");
                vm_goto(v, bodyl);
                vm_emit_f(v, bodyl, a->l, nx, cf);
            } else {
                /* LAZY: leaving is the preferred path and TAKING another
                 * iteration is the resume, mirroring vm_opt_chain's own lazy
                 * arm. Greedy vs lazy is which side is the fallthrough. */
                int bodyl = vm_label(v);
                vm_lbl(v, cur, "counter iteration (lazy): leaving preferred");
                vm_mrl_test(v, "scan_position", vm_fadd(bw, F), skip,
                            "MRL: no room for another iteration and the follow");
                vm_push(v, bodyl, "lazy: taking another iteration is the resume");
                vm_goto(v, skip);
                vm_emit_f(v, bodyl, a->l, nx, cf);
            }
            cur = nx;
        }
        vm_lbl(v, cur, "counter trip complete: charge K and go round");
        {
            char val[64];
            snprintf(val, sizeof val, "slot_values[%d] + %d", ctr, K);
            vm_set(v, ctr, val, "counter rung: += K, once per TRIP");
        }
        vm_goto(v, trip);
    }

    /* THE RESIDUE. For the optional phase the tail IS `vm_opt_chain` at a
     * smaller count -- today's emission, verbatim -- which is what makes the
     * K > count case byte-identical to the frames rung by construction rather
     * than by careful arithmetic. */
    if (optional) {
        vm_opt_chain(v, tail, a->l, residue, next, a->u.rep.greedy, bw);
        vm_lbl(v, skip, "counter: the loop is done, take the continuation");
        vm_goto(v, next);
        return;
    }
    if (residue == 0) {
        /* The tail label still EXISTS -- the trip guard branches to it -- so
         * it is emitted and hands straight over rather than being elided,
         * which would leave the guard jumping at an undefined label. */
        vm_lbl(v, tail, "counter residue: none (count is a multiple of K)");
        vm_goto(v, next);
        return;
    }
    {
        int res0 = vm_label(v);
        int cur;
        vm_lbl(v, tail, "counter residue: count mod K copies, replicated");
        vm_goto(v, res0);
        cur = res0;
        for (int i = 0; i < residue; i++) {
            int nx = vm_label(v);
            /* Mandatory replicated copies: the frames rung's own arithmetic,
             * at a smaller count. */
            int at = vm_mrl_gate(v, cur, vm_fadd(vm_fmul(residue - i, bw), F),
                                 -1, "MRL: mandatory residue copies plus the "
                                     "follow do not fit");
            vm_emit_f(v, at, a->l, nx,
                      vm_fadd(vm_fmul(residue - i - 1, bw), F));
            cur = nx;
        }
        vm_lbl(v, cur, "counter residue complete");
        vm_goto(v, next);
    }
}

/* [ENG-BREP counter-K] §3.4's POSSESSIVE optional phase: ONE frame for the
 * whole loop instead of one per iteration, via RX_CUT against a mark recorded
 * at loop entry — `vm_poss_chain`'s discipline applied per ITERATION rather
 * than per COPY.
 *
 *   L_trip:  if (slot_values[ctr] >= NOPT) goto next
 *            PUSH(L_stop)          ; this iteration cannot run -> leave
 *            <body>  -> L_step
 *   L_step:  RX_CUT(mark); RX_SET(ctr, slot_values[ctr] + 1); goto L_trip
 *   L_stop:  RX_CUT(mark); goto next
 *
 * THE PUSH STAYS, and deleting it is not available. `vm_poss_chain`'s recorded
 * lesson applies unchanged: a frame at an iteration serves TWO purposes —
 * resume when the CONTINUATION fails, which possessification kills, and resume
 * when the BODY fails (this iteration cannot run, so leave the loop), which
 * stays completely alive. Cutting at the boundary is what possessification
 * buys; removing the frame is not.
 *
 * NO TRIP, NO TAIL, NO K [R25 E6]. Unrolling buys nothing here: the cut at
 * every iteration boundary already makes the frame requirement independent of
 * the count, which is the only thing K was bought for. One emitted body copy,
 * re-entered.
 *
 * THE COUNTER IS THE SAME TRAILED SLOT AS EVERYWHERE ELSE, and the "saving"
 * an earlier draft proposed for it — a plain untrailed local, on the revdet
 * rung's `_it` precedent — was a MANDATORY-PHASE MISCOMPILE [R25 E5]. The cut
 * argument that licenses an untrailed local is true of THIS phase and false of
 * the mandatory one: mandatory copies have no cut between them, so a
 * body-internal frame pushed during mandatory iteration 1 survives, resumes
 * reading a stale local, and `(?:a|bc){3}+` runs one iteration where it must
 * run three. */
static void vm_counter_poss_opt(Vm *v, int entry, const Ast *a, int nopt,
                                int next, int ctr, int mark, long long bw)
{
    StrBuf *b = v->b;
    const long long F = v->fmin;
    const int trip = vm_label(v);
    const int body0 = vm_label(v);
    const int step = vm_label(v);
    const int stop = vm_label(v);

    /* [M6.4.2] the same checked preference precondition as the two rungs
     * above: this function never reads `a->u.rep.greedy`, and that is licensed by
     * §2.2's collapse rather than by anything here. */
    if (!a->u.rep.greedy && !a->u.rep.possessive)
        ctx_fail(v->cx, 0,
                 "internal error: the counter rung's possessive optional phase "
                 "was given a LAZY body with no §2.2 verdict behind it; its "
                 "shape ignores preference, which that verdict is what "
                 "licenses");
    vm_lbl(v, entry, "counter: possessive optional phase begins");
    vm_set(v, ctr, "0", "counter rung: iteration counter (trailed)");
    vm_goto(v, trip);

    vm_lbl(v, trip, "counter trip (possessive): one iteration, or leave");
    sb_printf(b, "    if (slot_values[%d] >= %d) goto %s_L%d;\n", ctr, nopt, v->p, next);
    vm_ev(v, VE_NOTE, 0, 0, "the bound is a compile-time constant");
    /* [M4.6d] cut before push, once per iteration. `stop` cuts and takes the
     * continuation, which is exactly what the popped frame would have done. */
    vm_mrl_test(v, "scan_position", vm_fadd(bw, F), stop,
                "MRL: no room for another iteration and the follow");
    vm_push(v, stop, "possessive: this iteration cannot run, so leave the loop");
    vm_goto(v, body0);
    vm_emit_f(v, body0, a->l, step, F);

    vm_lbl(v, step, "counter iteration committed: cut, count, go round");
    vm_cut(v, mark, "cut: the iteration is committed and owns no live choice point");
    {
        char val[64];
        snprintf(val, sizeof val, "slot_values[%d] + 1", ctr);
        vm_set(v, ctr, val, "counter rung: += 1 (possessive: no trip, no K)");
    }
    vm_goto(v, trip);

    vm_lbl(v, stop, "counter: the loop is done (possessive), take the continuation");
    vm_cut(v, mark, "cut: the loop is complete and owns no live choice point");
    vm_goto(v, next);
}

/* [ENG-BREP counter-K] §3's COUNTER RUNG: the two phases composed.
 *
 * `X{m,n}` is a MANDATORY phase of m iterations (no choice point) followed by
 * an OPTIONAL phase of n-m (one choice point each). Each phase independently
 * takes the counter loop when its own count reaches K and ordinary replication
 * when it does not, so a `{20,22}` unrolls its mandatory half and replicates
 * its two optional copies -- which is the right split, because K is a
 * threshold on emitted SIZE and the two phases contribute independently.
 *
 * ONE counter slot serves both (§2.3, RULED ASK 4), with the explicit
 * NOPT == 0 carve-out: a quantifier with rmin == rmax emits no optional-phase
 * reset at all, because a slot written but never read would break the
 * byte-identity property §3.2 promises unconditionally at K > NOPT. */
static void vm_counter_rep(Vm *v, int entry, const Ast *a, int next,
                           bool under_atomic)
{
    const bool cuts = vm_cuts(a, under_atomic);
    const int K = v->unroll_k;
    const int m = a->u.rep.rmin;
    const bool unbounded = a->u.rep.rmax < 0;
    const int nopt = unbounded ? 0 : a->u.rep.rmax - a->u.rep.rmin;
    const int ctr = vm_slot_ctr(v, v->nctr++);
    /* The possessive arm needs a cut mark as well, recorded BEFORE the
     * mandatory copies rather than after them: the cut at the first optional
     * iteration then also discards the mandatory bodies' own dead frames, so
     * the loop is atomic as a whole, which is what "possessive" means. */
    const int mark = cuts ? vm_slot_mark(v, v->nmark++) : -1;
    /* [M4.6d] the rung's two MRL quantities, taken once (the frames rung's
     * own reason: per-copy recomputation would be quadratic in the count). */
    const long long F  = v->fmin;
    const long long bw = pcrec_minw(a->l);
    int cur;

    const char *role;
    if (unbounded)
        role = vm_rolef(v, "counter rung, {%d,}, K=%d, %s "
                           "(mandatory counted, tail on the frames star)",
                        a->u.rep.rmin, K, a->u.rep.greedy ? "greedy" : "lazy");
    else
        role = vm_rolef(v, "counter rung, {%d,%d}, K=%d, %s "
                           "(mandatory %s, optional %s)",
                        a->u.rep.rmin, a->u.rep.rmax, K,
                        a->u.rep.greedy ? "greedy" : "lazy",
                        m >= K ? "counted" : "replicated",
                        nopt == 0 ? "none"
                                  : (nopt >= K ? "counted" : "replicated"));
    vm_lbl(v, entry, role);
    vm_rung_mark(v, entry, VM_RUNG_COUNTER, cuts, role);
    vm_prune_mark(v, entry,
                  v->mrl && (vm_fadd(bw, F) > 0 || v->fdyn != NULL), role);
    if (cuts)
        vm_set(v, mark, "(ptrdiff_t)run->resume_depth",
               "possessive cut mark (resume-stack depth at loop entry)");
    cur = vm_label(v);
    vm_goto(v, cur);

    if (m >= K) {
        int done = vm_label(v);
        vm_counter_phase(v, cur, a, m, done, ctr, false, bw);
        cur = done;
    } else {
        for (int i = 0; i < m; i++) {
            int nx = vm_label(v);
            int at = vm_mrl_gate(v, cur, vm_fadd(vm_fmul(m - i, bw), F), -1,
                                 "MRL: mandatory copies left plus the follow "
                                 "do not fit");
            vm_emit_f(v, at, a->l, nx, vm_fadd(vm_fmul(m - i - 1, bw), F));
            cur = nx;
        }
    }

    if (unbounded) {
        /* §11 residual 1: the TAIL is the frames star's, unchanged. The
         * counter shrank the mandatory prefix and claims nothing else.
         *
         * [M6.4.2] **K29's FIX, AND IT LANDS BEFORE THE LIFT ON PURPOSE.**
         * `vm_counter_fits` accepts an unbounded repeat when `rmin >= K`, and
         * this arm hands the tail to `vm_star`, which never reads
         * `a->u.rep.possessive` and emits neither spelling of a cut. So
         * `(?:ab|b){8,}c` was stamped POSSESSIVE, allocated and WROTE
         * `RX_SLOT_CUT_MARK0`, and READ IT NOWHERE — a dead slot, a D46 stamp
         * that lies, and a frame/trail budget computed for a path that was not
         * emitted. Harmless for ANSWERS while possessification is proof-gated
         * (the cut it failed to emit would have discarded provably-dead
         * frames), which is why it survived since [ENG-BREP].
         *
         * UNDER THE LIFT IT IS A MISCOMPILE: a semantic `X{n,}+` routed here
         * would answer the UNCUT language. That is why K29's fix is ordered
         * BEFORE the lift rather than after it — landing the lift first turns
         * an observability defect into a wrong answer.
         *
         * THE FIX IS THE GENERAL SHAPE'S OWN EXIT CUT, at the star's exit. The
         * star pushes one frame per iteration and every one of them is live
         * until the loop leaves; the loop leaves ONLY through `vm_star`'s
         * `exit` label (its MRL test, its empty-iteration guard, and the pop of
         * any pushed frame all land there), so one cut there discards the whole
         * loop's frames AND the mandatory phase's, back to the mark recorded
         * before any of them. `resume_depth >= mark` holds at that label
         * because the mark is set before the first push.
         *
         * IT CHANGES EMITTED BYTES FOR PATTERNS THAT HAVE NOTHING TO DO WITH
         * THIS MODULE — every `X{n,}` with `n >= K` and a positive §2.2
         * verdict. That is deliberate: K29 is a fix to code that predates the
         * module, and the identity claim in §11.1 is about ATOMIC-FREE patterns
         * whose emitted C this module does not touch, not about a pre-existing
         * defect this wave is required to carry. */
        if (cuts) {
            int cutl = vm_label(v);
            vm_star(v, cur, a, cutl);
            vm_lbl(v, cutl, "counter rung, unbounded tail: the loop is "
                            "complete -- cut back to the mark (K29)");
            vm_cut(v, mark, "cut: the loop is complete and owns no live "
                            "choice point");
            vm_goto(v, next);
            return;
        }
        vm_star(v, cur, a, next);
        return;
    }
    if (nopt == 0) {
        vm_lbl(v, cur, "counter: exact count complete");
        vm_goto(v, next);
        return;
    }
    if (cuts) {
        if (nopt >= K) vm_counter_poss_opt(v, cur, a, nopt, next, ctr, mark, bw);
        else           vm_poss_chain(v, cur, a->l, nopt, next, mark, bw,
                                     a->u.rep.greedy || a->u.rep.possessive);
        return;
    }
    if (nopt >= K) vm_counter_phase(v, cur, a, nopt, next, ctr, true, bw);
    else           vm_opt_chain(v, cur, a->l, nopt, next, a->u.rep.greedy, bw);
}

/* [ENG-BREP counter-K] THE UNBOUNDED STAR, extracted from vm_rep so the
 * COUNTER rung can hand its tail to it.
 *
 * `X{m,}` is a mandatory phase of m iterations followed by an unbounded tail,
 * and §11 residual 1 is explicit that only the tail stays on the frames star —
 * the mandatory prefix is the counter's, exactly as it is for `X{m,n}`. Before
 * this extraction the counter rung declined `rmax < 0` outright, so
 * `((a)|ab){4000,}` still replicated its 4,001 mandatory copies and was
 * REFUSED while `((a)|ab){4000}` compiled. §8.5 cell 3 names all three
 * spellings, and the gap was found by writing that cell as a check rather than
 * by reading the code.
 *
 * The body is moved VERBATIM: same locals, same order, same emitted text. Its
 * one parameter change is the entry label's name. */
static void vm_star(Vm *v, int cur, const Ast *a, int next)
{
    /* the unbounded star */
    bool guard = vm_nullable(a->l);
    int gslot = guard ? vm_slot_guard(v, v->nguard++) : -1;
    int bentry = vm_label(v), bend = vm_label(v), exit = vm_label(v);

    vm_lbl(v, cur, vm_rolef(v, "unbounded repeat, %s, frames rung%s",
                            a->u.rep.greedy ? "greedy" : "lazy",
                            guard ? ", nullable body (empty-iteration guard)"
                                  : ""));
    /* [M4.6d] cut before push, at the top of every iteration. A nullable body
     * has `bw == 0` and the test collapses to the loop's own follow-min,
     * which is still worth having: `(a*)*b` on a subject with no `b` left is
     * cut here rather than at the guard. */
    vm_mrl_test(v, "scan_position", vm_fadd(pcrec_minw(a->l), v->fmin), exit,
                "MRL: no room for another iteration and the follow");
    if (guard)
        vm_set(v, gslot, "(ptrdiff_t)scan_position",
               "empty-iteration guard: where this iteration began");
    if (a->u.rep.greedy) {
        vm_push(v, exit, "another iteration preferred; resume is the EXIT");
        vm_goto(v, bentry);
    } else {
        vm_push(v, bentry, "the exit is preferred; resume is another ITERATION");
        vm_goto(v, exit);
    }

    vm_emit(v, bentry, a->l, bend);

    vm_lbl(v, bend, "unbounded repeat: one iteration done");
    if (guard) {
        /* THE EMPTY-ITERATION RULE (§3.3), and its exact shape matters.
         *
         * An iteration that consumed nothing must not iterate again — but it
         * is NOT rolled back. Control takes the EXIT CONTINUATION, so the
         * empty iteration's own capture writes STAND. §3.3 says exactly this
         * ("control takes the exit continuation") and it is worth stating why,
         * because the mechanism invites the other reading: failing the path
         * instead would let the trail undo the write for free, and it is
         * WRONG. Both oracles give `(a*)*` on "a" a group 1 of [1,1) — the
         * second, empty iteration at position 1 ran, wrote its group, and then
         * stopped the loop. The roll-back reading reports [0,1), the FIRST
         * iteration's value, across the whole nullable-body family; `(|a)+`
         * additionally loses the WHOLE MATCH, reporting [0,1) where both
         * oracles give [0,0), because rolling back the empty iteration lets
         * the loop go round again.
         *
         * The exit frame this iteration pushed stays on the stack, so a later
         * failure of the continuation resumes it and enters the exit once more
         * with the empty iteration's writes rewound. That duplicate is
         * harmless — same position, same continuation, and base-tier matching
         * never reads captures, so the second attempt fails exactly as the
         * first did — but it is real work and one charged step. Dropping the
         * frame instead is not available: it need not be on top, because the
         * body may have left its own choice points above it and those must
         * still get their turn. Recorded for [M4.6] rather than solved with a
         * mechanism that mutates a frame in place, which does not survive the
         * loop being re-entered. */
        sb_printf(v->b, "    if ((ptrdiff_t)scan_position != slot_values[%d]) goto %s_L%d;\n",
                  gslot, v->p, cur);
        vm_goto(v, exit);
    } else {
        vm_goto(v, cur);
    }

    vm_lbl(v, exit, "unbounded repeat: the exit");
    vm_goto(v, next);}

static void vm_rep(Vm *v, int entry, const Ast *a, int next, bool under_atomic)
{
    const uint8_t *seq[VM_MAX_STRIDE];
    CapOff caps[VM_MAX_BODY_CAPS];
    int stride = 0, ncaps = 0;
    const bool cuts = vm_cuts(a, under_atomic);

    if (a->u.rep.rmin == 0 && a->u.rep.rmax == 0) {   /* X{0} matches empty */
        /* [M6.4.2] CUT-EQUIVALENT trivially, under the lift as well: no code is
         * emitted, so nothing is pushed and a cut would have nothing to
         * discard. `(?>a{0})b` and `a{0}+b` both reduce to `b`. */
        vm_lbl(v, entry, "X{0}: matches empty, no code");
        vm_goto(v, next);
        return;
    }

    if (vm_cursor_fits(a, seq, &stride, caps, &ncaps)) {
        vm_cursor_rep(v, entry, a, next, seq, stride, caps, ncaps, under_atomic);
        return;
    }

    /* [ENG-BREP] the ladder's second rung, below the cursor and above the
     * frames. `a->u.rep.revbody` is src/opt/revdet.c's verdict AND the material the
     * backward walk is emitted from, so this site cannot select the rung
     * without having the thing the rung needs.
     *
     * [M6.4.2] RULE 3's CONDITION (d), AND IT IS THIS SITE'S TO ENFORCE. A lift
     * inherits the SELECTED RUNG's own gate, and `vm_rev_canmove`'s EXACT-COUNT
     * clause is such a gate: "there is one exit" is a (U1)/(U2)
     * unique-iteration statement consulting no verdict, so for a body §2.2
     * rejects at `rmin == rmax` it is false and the retreat frame this rung
     * then omits is one the loop needed. (a) cut-equivalence, (b)
     * preference-preservation and (c) nullable-safety are all properties of the
     * BODY and none of them implies this.
     *
     * MEASURED EMPTY TODAY — 14 bodies x 3 exact counts found no
     * revdet-approved, possessify-rejected body at an exact count, because
     * `rd_shape`'s gate is strictly stronger than §2.2's on everything
     * constructible. So DECLINING here costs nothing measurable, and it turns a
     * cell that is "safe by luck" into one that is safe by construction: a
     * LIFTED exact-count repeat falls through to the frames rung, which emits
     * `vm_poss_chain` with `count == 0` — one mark, one cut, no retreat frame
     * to get wrong. `a->u.rep.possessive` (the PROVED case) is unaffected and keeps
     * the rung, because there the verdict is exactly what licenses the gate. */
    if (vm_revdet_fits(a, under_atomic)) {
        vm_revdet_rep(v, entry, a, next, under_atomic);
        return;
    }

    /* [ENG-BREP counter-K] the ladder's LAST rung before replication, and the
     * one that catches the bodies all three above decline. Selected by the one
     * shared predicate the two pre-passes also call, never by a second reading
     * of the same conditions. */
    if (vm_counter_fits(v, a)) {
        vm_counter_rep(v, entry, a, next, under_atomic);
        return;
    }

    /* [D46] the fallthrough below is the WHOLE frames rung for this
     * quantifier — mandatory copies, the bounded opt-chain and the unbounded
     * star are marked once here rather than at each of their own returns.
     * `a->u.rep.rmax` already distinguishes bounded from unbounded at this point
     * (nothing downstream can change it), so the split is made HERE rather
     * than duplicated at each return site below. */
    /* [M4.6d] the two quantities every MRL site on this rung is derived from,
     * taken ONCE here: the loop's own follow-min (what must be consumed after
     * the whole quantifier) and the body's minimum width. Computing them per
     * copy instead would make the emitter quadratic in a replication count
     * that reaches 4,000. */
    const long long F  = v->fmin;
    const long long bw = pcrec_minw(a->l);

    {
        char fbounds[32];
        bool bounded = a->u.rep.rmax >= 0;
        if (bounded) snprintf(fbounds, sizeof fbounds, "{%d,%d}", a->u.rep.rmin, a->u.rep.rmax);
        else         snprintf(fbounds, sizeof fbounds, "{%d,}", a->u.rep.rmin);
        const char *frole = vm_rolef(v, "frames rung, %s %s, %s%s",
                                     bounded ? "bounded" : "unbounded", fbounds,
                                     a->u.rep.greedy ? "greedy" : "lazy",
                                     !cuts ? ""
                                       : a->u.rep.possessive
                                       ? ", POSSESSIFIED (one frame for the"
                                         " whole loop, no giveback)"
                                       : ", ATOMIC (a written cut: one frame"
                                         " for the whole loop, no giveback)");
        vm_rung_mark(v, entry, bounded ? VM_RUNG_FRAMES_BOUNDED
                                        : VM_RUNG_FRAMES_UNBOUNDED,
                     cuts, frole);
        /* One more iteration plus the follow: the minrest every site on this
         * rung tests, and therefore exactly the predicate for "did this
         * quantifier get a bound at all". */
        vm_prune_mark(v, entry,
                  v->mrl && (vm_fadd(bw, F) > 0 || v->fdyn != NULL), frole);
    }

    /* ---- the frames rung ------------------------------------------------
     * rmin mandatory copies, then either the unbounded star or (rmax - rmin)
     * nested optionals. RULED (D44/R21 E-2): the empty-iteration guard exists
     * ONLY for rmax == -1. The panel MEASURED the "or high-bounded" reading
     * against libpcre2 — with the guard applied to bounded repeats too, 60 of
     * 225,240 generated pairs diverge; restricted to rmax == -1, 0 of 225,240.
     * PCRE2's actual behaviour is that bounded repeats REPLICATE: a {1,2} body
     * is body-body?, each copy an independent opportunity to match empty or
     * not, because there IS no "continuation" test at a bounded count — there
     * is just the next copy. */
    int cur = entry;

    /* [ENG-BREP] The possessified frames rung takes the SAME mandatory copies
     * and then a different tail. The cut mark is recorded FIRST, before the
     * mandatory copies rather than after them, so the cut at the first
     * optional copy also discards the mandatory bodies' own dead frames — the
     * loop is atomic as a whole, which is what "possessive" means. Leaving
     * them would also be correct (the verdict says they are dead, so resuming
     * one cannot change the answer); discarding them is simply the win. */
    if (cuts) {
        int mslot = vm_slot_mark(v, v->nmark++);
        int body0 = vm_label(v);
        vm_lbl(v, entry, "possessified repeat: record the resume-stack depth "
                         "to cut back to");
        vm_set(v, mslot, "(ptrdiff_t)run->resume_depth",
               "possessive cut mark (resume-stack depth at loop entry)");
        vm_goto(v, body0);
        cur = body0;
        for (int i = 0; i < a->u.rep.rmin; i++) {
            int nx = vm_label(v);
            int at = vm_mrl_gate(v, cur, vm_fadd(vm_fmul(a->u.rep.rmin - i, bw), F),
                                 -1, "MRL: mandatory copies left plus the "
                                     "follow do not fit");
            vm_emit_f(v, at, a->l,  nx,
                      vm_fadd(vm_fmul(a->u.rep.rmin - i - 1, bw), F));
            cur = nx;
        }
        if (a->u.rep.rmax >= 0) vm_poss_chain(v, cur, a->l, a->u.rep.rmax - a->u.rep.rmin, next,
                                        mslot, bw, a->u.rep.greedy || a->u.rep.possessive);
        else              vm_poss_star(v, cur, a->l, next, mslot, bw,
                                       a->u.rep.greedy || a->u.rep.possessive);
        return;
    }

    /* [M4.6d] THE MANDATORY COPIES, and this is where K23's fix lands on the
     * frames rung. Copy `i` is followed by `rmin - i - 1` further mandatory
     * copies and then the loop's own follow, so the emitter threads exactly
     * that down and gates the copy on one more than it — §4.3's second
     * threading line, which the design note calls "the whole of K23's fix".
     *
     * Failing OUTRIGHT is the right answer here and only here: a mandatory
     * copy is not optional, so a position from which the remaining mandatory
     * copies cannot fit fails the whole quantifier. Every other site on this
     * rung takes an EXIT instead, because every other copy is optional. */
    for (int i = 0; i < a->u.rep.rmin; i++) {
        int nx = vm_label(v);
        int at = vm_mrl_gate(v, cur, vm_fadd(vm_fmul(a->u.rep.rmin - i, bw), F),
                             -1, "MRL: mandatory copies left plus the follow "
                                 "do not fit");
        vm_emit_f(v, at, a->l, nx,
                  vm_fadd(vm_fmul(a->u.rep.rmin - i - 1, bw), F));
        cur = nx;
    }

    if (a->u.rep.rmax >= 0) {
        vm_opt_chain(v, cur, a->l, a->u.rep.rmax - a->u.rep.rmin, next, a->u.rep.greedy, bw);
        return;
    }

    vm_star(v, cur, a, next);
}

/* ---- [M6.4.2] THE ATOMIC GROUP ------------------------------------------
 *
 * `(?>X)` in the GENERAL shape (design §3.3) — everything the lift declines,
 * which is every body that is not a greedy, non-nullable `A_REP`:
 *
 *     L_entry:  RX_SET(SLOT_CUT_MARKk, run->resume_depth)   // BEFORE any push
 *               goto L_body
 *     L_body:   <body>  -> L_cut          // ordinary emission, ordinary frames
 *     L_cut:    RX_CHARGE_WORK(depth - mark);  RX_CUT(SLOT_CUT_MARKk)
 *               goto L_next
 *
 * `vm_cut` is REUSED UNCHANGED, and that is the design's single most
 * load-bearing claim (CUT-INV, §3.1). The invariant people worry about — the
 * cut does not rewind the trail — is INDEPENDENT of the §2.2 proof that
 * licenses today's cuts. `vm_cut`'s own header gives two reasons for the rule
 * and only ONE of them is possessify's: discarding the FRAMES is what §2.2
 * licenses (an atomic group has no such licence, and discards frames that are
 * NOT dead — that is precisely the semantics), while leaving the TRAIL alone
 * rests on nothing but frame arithmetic. Stated as the invariant:
 *
 *   Let M be the resume depth at entry and T0 the trail depth there. Every
 *   frame below M was pushed before T0, so its `trail_mark <= T0`; every trail
 *   entry the body writes has index >= T0; `RX_CUT` sets `resume_depth = M`
 *   and leaves `trail_depth` alone. So any later pop of any frame below the
 *   mark still satisfies `trail_depth > frame.trail_mark` for every one of the
 *   body's entries and unwinds them all. The fail label's `>`-not-`==` is what
 *   makes that last step true.
 *
 * THREE PROPERTIES OF THE SHAPE, each with the line that makes it true:
 *
 *  1. THE MARK'S `RX_SET` PRECEDES EVERY `RX_PUSH` IN THE BODY — CUT-INV's
 *     clause 2, and the reason the emission order below is not cosmetic. It
 *     also makes the mark itself TRAILED (`vm_set` is the trailing writer),
 *     which is what makes NESTING and RE-ENTRY work: an outer backtrack
 *     restores the mark slot and this entry label re-sets it on every entry, so
 *     `(?>a|b)*c` cuts independently per iteration. Sabotage row S90 moves the
 *     `RX_SET` after the first push; codegen rule 3 is the check.
 *  2. `RX_CUT` IS AN ASSIGNMENT, NOT A `min()`, so it is only correct while
 *     `resume_depth >= mark` at every cut site. That holds because control
 *     cannot reach `L_cut` after a pop below the entry frame — such a pop
 *     jumps to a resume label OUTSIDE the group — and nested marks are
 *     monotone by construction (an inner group's mark is taken at a depth at
 *     or above this one's).
 *  3. NOTHING REWINDS THE TRAIL. Captures written inside the body are RETAINED
 *     on success (`(?>(a)|ab)` on "ab" is (0,1) with group 1 = (0,1)) and
 *     UNDONE on an outer failure (`((?>(a)|ab))c|(abc)` on "abc" is (0,3) with
 *     groups 1 and 2 UNSET). Only RETENTION discriminates the invariant: a cut
 *     that wrongly rewound the trail gets the UNDO half trivially right,
 *     because it did the undo early. Sabotage row S89.
 *
 * The mark slot joins the existing `SLOT_CUT_MARK<n>` family, so it is
 * greppable and the slot legend names it, and it is spelled in ONE place —
 * src/gen/CLAUDE.md's two rules. */
/* [M6.4.4] THE FOLLOW DOES NOT CROSS A CUT — the tier-1 miscompile the
 * blinded D27 corpus found on `(?:aa|a)++ab`, and the reason this scoping is a
 * SEMANTIC boundary rather than a missed optimisation.
 *
 * `(?>X)` matches X's OWN FIRST SUCCESS. Which success that is must be decided
 * without consulting what follows the group, because the cut makes the choice
 * final: a determination that peeked at the follow would pick a DIFFERENT (and
 * always later) success than X alone reaches, and then commit to it.
 *
 * `v->fmin` is exactly such a peek. It is the minimum width of what follows,
 * and the MRL machinery turns it into a bound: every possessive rung ends its
 * loop at the first position where "one more iteration PLUS THE FOLLOW" does
 * not fit (`vm_poss_star` :2791, `vm_poss_chain` :2714), and the mandatory
 * copies gate on it likewise. FOR AN UNCUT LOOP THAT SHORTCUT IS
 * ANSWER-PRESERVING and `vm_opt_chain`'s own comment proves it: the body
 * branch has no accepting leaf there, so the skip is the only survivor — and
 * the skip is still AVAILABLE to retreat to. UNDER A CUT IT IS NOT. The loop
 * must run as far as the BODY goes and then commit; stopping early at a
 * position the greedy run would have walked past manufactures an exit the cut
 * exists to destroy.
 *
 * MEASURED, on `(?:aa|a)++ab` over "aaab" (libpcre2 10.46 and python3 `re`
 * both NOMATCH): the loop takes "aa", reaches offset 2 with two bytes left,
 * MRL says one more iteration (1) plus the follow (2) does not fit in 2, exits
 * without the third `a`, and the follow matches "ab" — (0,4), the UNCUT
 * language. With the follow cut off at the group boundary the bound is the
 * body's own width, the loop takes the third `a`, the follow fails at offset 3
 * and there is nothing to retreat to. `-fno-length-prune` gave the right
 * answer throughout, which is what identified the prune as the carrier.
 *
 * SO BOTH ROUTES OUT OF THIS FUNCTION SCOPE IT, and the general shape needed
 * it just as much as the lift: `(?>a(?:aa|a)+)ab` puts the loop one level
 * INSIDE the group, where `under_atomic` is false and possessify's own §2.2
 * verdict was computed against the body's EMPTY follow while the emitter was
 * still carrying `ab` — the two disagreeing about which follow they mean is
 * the whole defect. Cutting `fmin`/`fdyn` at the boundary makes them agree by
 * construction, for every shape, instead of at each rung by hand.
 *
 * WHAT IS NOT LOST: the body's INTERNAL follows. The concatenation arm rebuilds
 * suffix sums from `v->fmin` (:4321), so `(?>(?:aa|a)+a)` still gives its loop
 * the trailing `a` as a follow — only the group's OUTER follow is dropped. And
 * nothing atomic-FREE changes: this function is reached for `A_ATOMIC` alone,
 * so `run_atomic_identity.sh`'s claim is untouched.
 *
 * This is H3 (§4.4) one level down and it is the same sentence: the prefilter
 * answers for the UNCUT language, so its span end is not a bound on a cut
 * match's end; `v->fmin` answers for the follow, so it is not a bound on a cut
 * body's search. */
static void vm_atomic(Vm *v, int entry, const Ast *a, int next)
{
    const char *sd = v->fdyn;
    long long   sf = v->fmin;
    v->fmin = 0;
    v->fdyn = NULL;

    /* THE LIFT (§3.2, RULE 3): route the cut into the quantifier's own
     * possessive rung, which cuts PER ITERATION where this shape cuts once at
     * the group's exit. Without it `(?>a*)` exhausts RX_RESUME_FRAMES where
     * `a*+` — a spelling PCRE2 calls identical — costs one frame. `vm_lifts`
     * carries the scope and the evidence. */
    if (vm_lifts(a)) {
        vm_rep(v, entry, a->l, next, true);
        v->fmin = sf;
        v->fdyn = sd;
        return;
    }

    int mslot = vm_slot_mark(v, v->nmark++);
    int bodyl = vm_label(v), cutl = vm_label(v);

    vm_lbl(v, entry, "atomic group: record the resume-stack depth to cut "
                     "back to (BEFORE the body pushes anything)");
    vm_set(v, mslot, "(ptrdiff_t)run->resume_depth",
           "atomic-group cut mark (resume-stack depth at group entry)");
    vm_goto(v, bodyl);

    /* The body's follow-min is ZERO, not the group's — see this function's
     * header. The group consumes exactly what the body consumes, so a
     * CAPTURING wrapper would inherit `v->fmin` unchanged (A_CAP's arm's own
     * reading); an ATOMIC one must not, because the cut makes the body's
     * choice final and the follow is not allowed to influence it. */
    vm_emit(v, bodyl, a->l, cutl);

    vm_lbl(v, cutl, "atomic group: the body's FIRST success -- cut, and never "
                    "reconsider");
    vm_cut(v, mslot, "cut: the group is committed; every choice point the body "
                     "created is discarded, dead or not");
    vm_goto(v, next);

    /* The follow is back in force AFTER the cut: `next` and everything past it
     * are outside the group and prune normally. Only the body was scoped. */
    v->fmin = sf;
    v->fdyn = sd;
}

/* ---- [M6.6.2] THE LOOKAROUND ---------------------------------------------
 *
 * `(?=X)` `(?!X)` `(?*X)` `(?<=X)` `(?<!X)` `(?<*X)` — all six, since wave D
 * landed the back-step seam entry. Design: docs/design/lookaround_design.md
 * §3. TWO functions: `vm_look_behind` below emits §3.4's per-branch back-step
 * chain, and `vm_look` after it is the whole construct.
 *
 * A lookaround is A SUB-MATCH WHOSE RESULT IS A VERDICT AND WHOSE POSITION IS
 * DISCARDED, and every line below follows from that one sentence. It is not a
 * new kind of matching — the body is the same AST `vm_emit` already walks,
 * emitted with ordinary frames — so unlike a backreference it needs no new
 * operation. What it needs is A CUT AND A POSITION RESTORE, plus (behind
 * only) a BACK-STEP and an END-CHECK.
 *
 *   POSITIVE ATOMIC (§3.2) — `vm_atomic`'s shape plus a saved cursor:
 *
 *     L_entry:  RX_SET(SLOT_LOOK_MARKk, run->resume_depth)   // BEFORE any push
 *               RX_SET(SLOT_LOOK_POSk,  scan_position)       // trailed, like the mark
 *               goto L_body
 *     L_body:   <X>                              -> L_ok
 *     L_ok:     RX_CHARGE_WORK(depth - mark);  RX_CUT(SLOT_LOOK_MARKk)
 *               scan_position = (size_t)slot_values[SLOT_LOOK_POSk];
 *               goto L_next
 *
 *   THE TWO `RX_SET`/restore LINES ARE THE ENTIRE DIFFERENCE between `(?>ab)c`
 *   and `(?=ab)c`, which is the strongest form §3's central claim can take.
 *
 *   NEGATIVE (§3.3) — the same, with ONE FRAME PUSHED FIRST AND NO SNAPSHOT
 *   MACHINERY AT ALL, which is the finding that makes `vm_look` short:
 *
 *     L_entry:  RX_SET(SLOT_LOOK_MARKk, run->resume_depth)
 *               RX_PUSH(&&L_neg_ok, scan_position)      // "the body failed"
 *               goto L_body
 *     L_body:   <X>                              -> L_body_won
 *     L_body_won:   RX_CHARGE_WORK(...); RX_CUT(SLOT_LOOK_MARKk); goto rx_fail
 *     L_neg_ok: goto L_next
 *
 *   `RX_PUSH` records the cursor AND `trail_depth`, and the fail label
 *   restores the first and rewinds to the second before jumping (:6061-6073,
 *   emitted verbatim into every VM artifact). So arriving at `L_neg_ok` means
 *   the cursor is already back and every capture the body wrote is already
 *   undone — no position slot, no capture snapshot. MEASURED that this is the
 *   right semantics: `(?!(a)x)ab` on "ab" is (0,2) with g1 UNSET, and
 *   `(?!(a)x)(a)` on "ab" is (0,1) with g1 unset and g2=(0,1) (the second cell
 *   proves the answer is READ rather than truncated by libpcre2's
 *   trailing-unset rule).
 *
 *   THE `L_body_won` CUT IS NOT AN OPTIMISATION. It discards the body's frames
 *   AND the `L_neg_ok` frame, because the mark was taken before the push. If
 *   it did not, the failing assertion would leave a live choice point that
 *   later resumes at `L_neg_ok` and lets the whole pattern proceed AS IF THE
 *   NEGATIVE ASSERTION HAD HELD — the exact wrong answer. Sabotage row S124.
 *
 *   NON-ATOMIC (§3.6) — the atomic shape MINUS the cut, and nothing else:
 *
 *     L_entry:  RX_SET(SLOT_LOOK_POSk, scan_position)   // no mark: nothing is cut
 *               goto L_body
 *     L_body:   <X>                              -> L_ok
 *     L_ok:     scan_position = (size_t)slot_values[SLOT_LOOK_POSk];
 *               goto L_next
 *
 *   It is correct without further machinery for a reason worth stating: when
 *   the follow fails, a frame inside the body resumes, the body reaches a
 *   SECOND success, and control arrives at `L_ok` AGAIN — where the slot is
 *   re-read and the cursor restored again. The slot survives that round trip
 *   because `vm_set` wrote it (trailed) BEFORE any body frame was pushed, so
 *   every body frame's `trail_mark` is above the slot's trail entry and no
 *   rewind to a body frame can undo it; a rewind to a frame BELOW the
 *   assertion does undo it, which is exactly when it should be. MEASURED, on
 *   "abab": `(?*(a|ab))\1$` is (2,4) where `(?=(a|ab))\1$` is NOMATCH.
 *
 * THREE PROPERTIES OF THE SHAPE, each with the line that makes it true — they
 * are `vm_atomic`'s three, restated because a reader must not have to go and
 * check that they still hold:
 *
 *  1. THE MARK'S `RX_SET` PRECEDES EVERY `RX_PUSH`, the negative form's own
 *     included. It also makes the mark TRAILED, which is what makes NESTING
 *     and RE-ENTRY work: an outer backtrack restores the slot and this entry
 *     label re-sets it on every entry, so `(?=a|b)*c` marks independently per
 *     iteration. The same is true of the POS slot and it has to be —
 *     `(?=(?=a)b)c` has two live position slots at once.
 *  2. `RX_CUT` IS AN ASSIGNMENT, NOT A `min()`. Correct while
 *     `resume_depth >= mark` at every cut site, which holds because control
 *     cannot reach the cut after a pop below the entry frame — such a pop
 *     jumps to a resume label OUTSIDE the assertion — and nested marks are
 *     monotone by construction.
 *  3. NOTHING REWINDS THE TRAIL, AND THAT IS THE SEMANTICS. Captures written
 *     inside a POSITIVE lookaround are RETAINED on success and UNDONE on an
 *     outer failure. MEASURED both ways: `(?=(a))a` on "a" is (0,1) with
 *     g1=(0,1); `(?:(?=(a))x|(a))` on "ab" is (0,1) with g1 UNSET and
 *     g2=(0,1). Only RETENTION discriminates — a cut that wrongly rewound the
 *     trail gets the UNDO half right by accident.
 *
 * THE FOLLOW IS SCOPED ACROSS THE BODY, AND NOT BECAUSE OF THE CUT (§3.2.1,
 * R33 C1-1). This is the one silent miscompile in §3 and the attribution is
 * the part that matters. `vm_atomic`'s own header attributes its identical
 * save-zero-restore to the CUT — "the group matches X's own first success, so
 * the choice must be made without peeking at the follow" — and THAT REASON
 * DOES NOT TRANSFER. Here the reason is the OVERLAP: a lookahead's follow
 * starts at the assertion's ENTRY position, so the body's bytes and the
 * follow's bytes are THE SAME BYTES and `body_remaining + fmin` DOUBLE-COUNTS
 * them. That argument is untouched by deleting the cut, which is why the
 * NON-ATOMIC arm below scopes just as hard as the atomic one.
 *
 * WHAT AN UNSCOPED BODY WOULD ANSWER, measured against both oracles:
 *
 *   (?=(a+)b)a+b  on "aab"  truth (0,3) g1=(0,2)  unscoped: body bound 1+2=3
 *                                                 -> MISSED MATCH
 *   (?!(a+)b)a+b  on "aab"  truth NOMATCH         unscoped: the body is pruned
 *                                                 to fail, so the NEGATIVE
 *                                                 assertion SUCCEEDS
 *                                                 -> FALSE MATCH
 *
 * The negative row is the dangerous one: an unsound prune inside a negative
 * assertion turns "the body could not be shown to match" into "the assertion
 * holds". Sabotage row S132 is its detector, and that row's anchor has to
 * include this function's own text — `v->fmin = 0; v->fdyn = NULL;` is the
 * SAME TWO LINES `vm_atomic` carries.
 *
 * RESTORED ON EVERY RETURN PATH, not at one label (R33 V-8). `vm_look` still
 * has a SINGLE EXIT and the restore sits on it, and wave D kept that property
 * on purpose rather than attaching the restore to a label some path skips:
 * the per-branch lookbehind chain is emitted by a HELPER that returns
 * normally, and every branch leaves through the same `L_ok` the lookahead
 * arm uses. There is no return path in this section that does not pass the
 * two restore lines at `vm_look`'s end.
 *
 * `vm_cut` IS REUSED UNCHANGED, on the argument `atomic_groups_design.md` §3.1
 * established and this construct consumes rather than re-proves: the
 * no-trail-rewind invariant rests on FRAME ARITHMETIC, not on possessify's
 * §2.2 verdict. A lookahead's cut discards frames that are NOT dead, exactly
 * as an atomic group's does — which is the semantics, and is what §2.2's
 * atomicity discriminator measures. */
/* [M6.6.2 wave D] THE LOOKBEHIND's BRANCH CHAIN (design §3.4), emitted here
 * rather than inline in `vm_look` because it is the one part of this
 * construct that is a LOOP over a table and everything else is straight-line.
 *
 * Per TOP-LEVEL BRANCH `i` of fixed width `k_i`, in WRITTEN ORDER (§2.4 level
 * 1 — MEASURED: `(?<=(a)|(aa))c` on "aac" reports g1=(1,2) and
 * `(?<=(aa)|(a))c` reports g1=(0,2), so the FIRST branch written wins in
 * both, whichever is longer):
 *
 *     L_bi:     if (scan_position < k_i) goto L_b(i+1);   // not enough subject
 *               RX_PUSH(&&L_b(i+1), scan_position)        // retry the NEXT branch
 *               RX_CHARGE_WORK(k_i)
 *               scan_position = $_back_step(subject, subject_length,
 *                                           scan_position, k_i);
 *               if (scan_position == $_BACK_STEP_NONE) goto rx_fail;
 *               goto L_bodyi
 *     L_bodyi:  <B_i>                                     -> L_endi
 *     L_endi:   if (scan_position != (size_t)slot_values[POS]) <decline>
 *               goto L_ok
 *
 * and the LAST branch pushes nothing and sends both of its failure paths to
 * `rx_fail` — for `(?<=` that is the assertion failing, and for `(?<!` it is
 * the pop of the `L_neg_ok` frame, i.e. the assertion HOLDING (§3.3's wrapper
 * needs no second shape: running out of branches IS ordinary failure).
 *
 * WHY FORWARD-PLUS-END-CHECK AND NOT A REVERSE MACHINE (§3.5), in one line
 * each, because an implementer will ask: pcrec's reverse pass is a DFA over
 * the CAPTURE-ERASED pattern and a lookbehind body may contain captures
 * (measured: `(?<=(a)(b))c` on "abc" reports g1=(0,1) g2=(1,2)), a
 * backreference and nested lookaround, none of which survive erasure; a
 * reverse VM would be a SECOND emitter over a mirrored AST, whose measured
 * cost is `revdet.c`'s `rd_node` clearing `Ast.possessive` on the reversed
 * copy; and the forward body reuses `vm_emit` UNCHANGED, so every rung, prune
 * and budget charge works inside a lookbehind on the day it works outside one.
 * The price is stated rather than hidden: `m` branches run the body up to `m`
 * times per candidate position, bounded by the compile-time constant Σk_i.
 *
 * THREE THINGS IN THIS SHAPE ARE NOT THE FIRST THING A READER EXPECTS.
 *
 * 1. `scan_position < k_i` IS THE START-OF-SUBJECT GUARD, AND IT READS THE
 *    ABSOLUTE POSITION, NEVER `startpos`. A lookbehind READS SUBJECT BYTES
 *    BEFORE THE SEARCH WINDOW and that is the semantics, not an oversight —
 *    MEASURED in both oracles: `(?<=a)b` on "ab" AT STARTPOS 1 MATCHES (1,2),
 *    and `(?<!a)b` on the same input at the same startpos does NOT. Clamping
 *    this to `scan_position - startpos < k` is sabotage row S135, whose
 *    prediction is that `startpos.rxt`'s `ms` cells go red while every
 *    startpos-0 cell stays green. The guard is emitted AS WELL AS delegated
 *    to the seam entry's sentinel because a `size_t` compare against a
 *    compile-time constant is free and because the branch has somewhere
 *    better to go than failure — the NEXT branch.
 *
 * 2. THE SENTINEL CHECK IS FOR THE BACKEND THAT DOES NOT EXIST YET (§4.2(3),
 *    R33 C1-4). Under the byte backend the guard above is EXACT, so
 *    `$_BACK_STEP_NONE` can never come back and this comparison is dead code
 *    that changes no answer — which is exactly why sabotage row S134 deleting
 *    it is a CODEGEN row rather than a behavioural one. Under UTF-8, `k`
 *    characters is at least `k` bytes, so the guard still soundly rejects but
 *    stops being exact, and this check is what keeps the shape correct.
 *    IT LEAVES BY `rx_fail` RATHER THAN BY `goto L_b(i+1)`, and the design's
 *    own sketch had the latter: the assignment has already CLOBBERED
 *    `scan_position` with the sentinel, so a direct jump would run the next
 *    branch's guard against `(size_t)-1` and back-step from there — and the
 *    frame pushed two lines up would be left live to retry that branch a
 *    SECOND time. `rx_fail` pops that very frame, which restores both the
 *    cursor and the trail and lands on `L_b(i+1)`, which is the retry the
 *    push was written for.
 *
 * 3. THE END-CHECK IS PROVABLY REDUNDANT FOR THE SUBSET THIS MODULE SHIPS AND
 *    IS EMITTED ANYWAY. A branch with `minw == maxw == k` consumes exactly k
 *    bytes on every successful path, so a body started at `pos - k` that
 *    succeeds ends at `pos` and this comparison cannot fail on a correct
 *    compiler. It is emitted because it is THE ONLY RUNTIME EVIDENCE that
 *    `pcrec_maxw` — this module's one piece of genuinely new analysis — agrees
 *    with what the emitter did with it, and because it stops being redundant
 *    the day the variable-length follow-on lands.
 *
 *    AND ITS FAILURE ACTION SPLITS BY POLARITY (R33 C1-5; Frank's ASK 2
 *    ruling). For `(?<=X)` a declined branch is the assertion FAILING, so a
 *    wrong width degrades to a clean no-match — weaker than an abort, far
 *    better than a miscompile, and the cheap `goto rx_fail` is right. For
 *    `(?<!X)` a declined branch is the assertion SUCCEEDING, so a wrong width
 *    is a FALSE MATCH indistinguishable from a legitimate non-match: on that
 *    arm the end-check would BE the miscompile it exists to prevent. So the
 *    negative arm returns HARD out of the matcher instead.
 *
 *    WHICH `RX_R_*` — [DD-14] WAVE A COMMIT 2 (D71 item 1) MINTS THE CODE
 *    THIS SITE NEEDS, RATHER THAN ELIMINATING AMONG ONES THAT DON'T FIT.
 *    Before this commit D49 gave the artifact exactly three give-up codes —
 *    `RX_R_STEPS`, `RX_R_FRAMES`, `RX_R_WORK` — and none of the three MEANS
 *    "internal error"; this site used `RX_R_FRAMES` by ELIMINATION (the one
 *    least entangled with this module's own measured failure modes — S127's
 *    `RX_R_STEPS` prediction, §3.7's `RX_R_WORK` prediction), a compromise
 *    kept only until the code space had room for the honest answer. D49
 *    reserves everything strictly below `PCREC_ERR_FLOOR` for "a future
 *    abort semantic", and THIS IS EXACTLY THAT SEMANTIC: not a give-up (no
 *    resource was exhausted) but the artifact catching its own analysis
 *    disagreeing with its own emission — `pcrec_maxw` said one width, the
 *    emitter walked another. `RX_R_INTERNAL` (`PCREC_ERR_INTERNAL`, -6, BELOW
 *    the floor) is minted for exactly this shape. A composed call site
 *    honouring F2's `if (ret < PCREC_ERR_FLOOR) __builtin_trap();` traps on
 *    it — that IS the design, not a gap this site works around. The SAFETY
 *    property the ASK 2 ruling asked for is unchanged: a hard return out of
 *    the matcher is not a false match, whichever code carries it.
 *
 * THE BRANCH NODES ARE WALKED HERE AND THE WIDTHS ARE NOT RE-DERIVED. §3.1(c)
 * stores `u.look.widths` precisely so this function does not recompute them;
 * what it must still do is find the branch SUBTREES, because `vm_emit` needs
 * them. The walk fills its array from the END for `p_alt_info`'s reason (a
 * flat alternation is LEFT-NESTED, so the spine yields branches backwards) —
 * the same loop shape `mod_lookaround.c`'s `la_widths` uses, so index `i`
 * pairs branch `i` with `widths[i]` by construction — and a spine that
 * disagrees with `nbranch` is `ctx_fail`, not a silently mispaired table. */
static void vm_look_behind(Vm *v, const Ast *a, int okl, int mslot, int pslot)
{
    StrBuf *b = v->b;
    const int m = a->u.look.nbranch;
    const bool neg = a->u.look.neg;

    if (m < 1 || a->u.look.widths == NULL)
        ctx_fail(v->cx, 0, "internal error: a LOOKBEHIND reached vm_look with "
                           "no width table — the parse hook did not run");
    if (pslot < 0)
        ctx_fail(v->cx, 0, "internal error: a LOOKBEHIND reached vm_look with "
                           "no position slot — the end-check has nothing to "
                           "compare against");

    /* THE SEAM, CONSULTED BEFORE THE CALL IS EMITTED, exactly as the `A_BREF`
     * arm consults it and for that arm's reason: an emitter may route a
     * construct through a residual entry only if the BACKEND declares that
     * entry callable from an engine body. Unreachable for the byte backend,
     * which declares this one `true`; it is the NEXT backend this line is
     * for. */
    if (!pcrec_enc_entry_engine_callable(
            pcrec_enc_by_id(v->cx->opt->encoding), PCREC_ENCE_BACK_STEP))
        ctx_fail(v->cx, 0,
                 "internal error: this encoding's back-step is not declared "
                 "engine-callable, so a lookbehind cannot be routed through "
                 "the seam from an engine body");
    v->enc_mask |= PCREC_ENCE_BACK_STEP;

    const Ast **br = arena_alloc(&v->cx->arena, (size_t)m * sizeof *br);
    int *bl   = arena_alloc(&v->cx->arena, (size_t)m * sizeof *bl);
    int *bodl = arena_alloc(&v->cx->arena, (size_t)m * sizeof *bodl);
    int *endl = arena_alloc(&v->cx->arena, (size_t)m * sizeof *endl);
    {
        int i = m;
        const Ast *t = a->l;
        for (; t->k == A_ALT; t = t->l) {
            if (i <= 1)
                ctx_fail(v->cx, 0, "internal error: a lookbehind body's "
                                   "alternation spine is longer than its "
                                   "stored branch count");
            br[--i] = t->r;
        }
        if (i != 1)
            ctx_fail(v->cx, 0, "internal error: a lookbehind body's "
                               "alternation spine is shorter than its stored "
                               "branch count");
        br[0] = t;
    }
    for (int i = 0; i < m; i++) {
        bl[i]   = vm_label(v);
        bodl[i] = vm_label(v);
        endl[i] = vm_label(v);
    }

    vm_goto(v, bl[0]);

    for (int i = 0; i < m; i++) {
        const int k = a->u.look.widths[i];
        const bool last = (i + 1 == m);

        /* `vm_rolef`'s buffer is 160 bytes and it TRUNCATES rather than
         * failing, so this role is kept short enough to survive a 2-digit
         * branch index and width — a truncated comment in the emitted C is a
         * sentence that stops mid-word, which is what the first version of
         * this line shipped. */
        vm_lbl(v, bl[i], vm_rolef(v,
               "lookbehind branch %d of %d, fixed width %d: step back and run "
               "the branch FORWARD%s", i + 1, m, k,
               last ? " (the LAST branch: no retry frame)" : ""));

        /* The start-of-subject guard. ABSOLUTE, never relative to startpos —
         * see this function's header, note 1, and sabotage row S135.
         *
         * NOT EMITTED FOR A ZERO-WIDTH BRANCH, and that is the CONDITION
         * being unsatisfiable rather than an exception carved out for one
         * body shape: "fewer than 0 characters precede the cursor" is false
         * for every cursor, and `scan_position` is a `size_t`, so the emitted
         * test would be `scan_position < 0` — which gcc proves false under
         * `-Wextra` (`-Wtype-limits`) and the harness's `-Werror` generated
         * build then REFUSES. Found by `(?<=)x` and `(?<!)x`, §2.6's
         * degenerate bodies, which are legal in both oracles and ship. The
         * back-step call and its sentinel check are still emitted at width 0,
         * because D58's rule is about WHERE the arithmetic lives and not
         * about whether this particular constant makes it a no-op. */
        if (last) {
            if (k > 0)
                sb_printf(b, "    if (scan_position < %d) goto %s_fail;\n",
                          k, v->p);
            /* A NOTE AND NOT AN `assert`, and the reason is the listing's
              * own convention rather than taste: `VE_ASSERT` renders
              * "-> L<a>" and `a` is the label taken when the assertion HOLDS
              * (the `^` and `(?m)^` arms set it to `next`). These three sites
              * leave by `rx_fail`, which is not a label id, so an ASSERT event
              * here would print a confident `-> L0` naming a label the code
              * never jumps to. */
            vm_ev(v, VE_NOTE, 0, 0, k > 0 ? vm_rolef(v,
                  "lookbehind: fewer than %d characters precede the cursor, "
                  "and this is the last branch -- the assertion fails here", k)
                  : "lookbehind: a ZERO-WIDTH branch, so no start-of-subject "
                    "guard is emitted -- the condition it would test is false "
                    "for every cursor");
        } else {
            if (k > 0) {
                sb_printf(b, "    if (scan_position < %d) goto %s_L%d;\n",
                          k, v->p, bl[i + 1]);
                vm_ev(v, VE_ASSERT, bl[i + 1], 0, vm_rolef(v,
                      "lookbehind: fewer than %d characters precede the "
                      "cursor, so try the next branch", k));
            } else {
                vm_ev(v, VE_NOTE, 0, 0,
                      "lookbehind: a ZERO-WIDTH branch, so no start-of-subject "
                      "guard is emitted -- the condition it would test is "
                      "false for every cursor");
            }
            vm_push(v, bl[i + 1],
                    "lookbehind: the NEXT-BRANCH continuation -- this branch's "
                    "body failing retreats into the branch written after it");
        }

        {
            char cnt[32];
            snprintf(cnt, sizeof cnt, "%d", k);
            vm_work(v, cnt, "work charge: the back-step, charged as the "
                            "compile-time width rather than the runtime cost "
                            "so the accounting does not depend on the "
                            "encoding backend");
        }

        /* THE SEAM CALL. Never `scan_position - k` here: that is byte
         * arithmetic which is correct today and silently wrong under a UTF-8
         * backend, it is what D58 scope item 3 exists to prevent, and the
         * [M6.6] plan row forbids it in its own text. Sabotage row S133
         * inlines it and the [M5-SEAM] fixture-declared per-site count is its
         * only possible detector, because inlining changes NO ANSWER under
         * this backend. */
        sb_printf(b, "    scan_position = %s_back_step(subject, "
                     "subject_length, scan_position, %d);\n", v->p, k);
        vm_ev(v, VE_NOTE, 0, 0, vm_rolef(v,
              "lookbehind: the ENCODING SEAM's back-step, %d character%s",
              k, k == 1 ? "" : "s"));
        sb_printf(b, "    if (scan_position == %s_BACK_STEP_NONE) goto %s_fail;\n",
                  v->p, v->p);
        vm_ev(v, VE_NOTE, 0, 0,
              "lookbehind: the back-step ran off the start of the subject -- "
              "dead under the byte backend, where the guard above is exact");
        vm_goto(v, bodl[i]);

        /* The body, forward, through `vm_emit` unchanged (§3.5(3)). */
        vm_emit(v, bodl[i], br[i], endl[i]);

        vm_lbl(v, endl[i], neg
               ? "lookbehind END-CHECK (negative): the branch must finish "
                 "exactly where the assertion started. On THIS polarity a "
                 "declined branch would be the assertion SUCCEEDING, i.e. a "
                 "FALSE MATCH, so a disagreement returns HARD"
               : "lookbehind END-CHECK: the branch must finish exactly where "
                 "the assertion started -- the only runtime evidence that the "
                 "width analysis and this emission agree");
        {
            char sl[64];
            vm_slot_expr(v, pslot, sl, sizeof sl);
            if (neg) {
                /* [DD-14 wave A commit 2] RX_R_INTERNAL, not RX_R_FRAMES --
                 * see this function's header comment, note 3, "WHICH
                 * RX_R_*". Below PCREC_ERR_FLOOR: not a give-up, the
                 * artifact's own inconsistency check firing. */
                sb_printf(b, "    if (scan_position != (size_t)slot_values[%s]) "
                             "return %s_R_INTERNAL;\n", sl, v->up);
                vm_ev(v, VE_NOTE, 0, 0,
                      "lookbehind end-check FAILED on the negative arm -- a "
                      "hard return (RX_R_INTERNAL, below the give-up floor) "
                      "rather than a decline, because a decline here is a "
                      "false match");
            } else {
                sb_printf(b, "    if (scan_position != (size_t)slot_values[%s]) "
                             "goto %s_fail;\n", sl, v->p);
                vm_ev(v, VE_NOTE, 0, 0,
                      "lookbehind end-check FAILED -- this branch declines");
            }
        }
        vm_goto(v, okl);
    }
    (void)mslot;
}

static void vm_look(Vm *v, int entry, const Ast *a, int next)
{
    StrBuf *b = v->b;

    /* §3.2.1 — SAVE, ZERO, and (at the single exit below) RESTORE. */
    const char *sd = v->fdyn;
    long long   sf = v->fmin;
    v->fmin = 0;
    v->fdyn = NULL;

    const bool neg    = a->u.look.neg;
    const bool atomic = a->u.look.atomic;
    const bool behind = a->u.look.behind;

    /* The two families, allocated per shape off the shared predicates. -1 is
     * "this shape does not take one", and every use below is guarded. */
    const int mslot = vm_look_needs_mark(a) ? vm_slot_lookmark(v, v->nlookmark++) : -1;
    const int pslot = vm_look_needs_pos(a)  ? vm_slot_lookpos(v,  v->nlookpos++)  : -1;

    const int okl = vm_label(v);
    const int negokl = neg ? vm_label(v) : -1;

    /* THE ENTRY LABEL'S ROLE IS THE LISTING'S RECORD OF THE THREE FLAGS
     * (design §11's wave-A2 amendment: `--emit-ir` renders the VEvent stream,
     * so a lookaround's listing is whatever this function records). One call
     * writes the emitted C comment and the VE_LABEL event, so the two cannot
     * drift about what this construct is. */
    vm_lbl(v, entry,
           neg    ? (behind ? "negative lookbehind: record the resume-stack depth to cut back to (BEFORE any push), the cursor the END-CHECK compares against, then push the body-failed continuation"
                            : "negative lookahead: record the resume-stack depth to cut back to (BEFORE any push), then push the body-failed continuation")
           : atomic ? (behind ? "positive lookbehind (atomic): record the resume-stack depth to cut back to, and the cursor to come back to (which is also what the END-CHECK compares against)"
                              : "positive lookahead (atomic): record the resume-stack depth to cut back to, and the cursor to come back to")
                    : (behind ? "positive lookbehind (NON-ATOMIC): record the cursor to come back to; nothing is cut, so no mark slot is allocated and the per-branch retry frames STAY LIVE"
                              : "positive lookahead (NON-ATOMIC): record the cursor to come back to; nothing is cut, so no mark slot is allocated"));

    if (mslot >= 0)
        vm_set(v, mslot, "(ptrdiff_t)run->resume_depth",
               "lookaround cut mark (resume-stack depth at the assertion's entry)");
    if (pslot >= 0)
        vm_set(v, pslot, "(ptrdiff_t)scan_position",
               "lookaround: the cursor to restore -- the assertion consumes nothing");
    if (neg)
        vm_push(v, negokl, "negative lookaround: the BODY-FAILED continuation "
                           "-- reaching it means the assertion HOLDS");

    /* The body's follow-min is ZERO, not the assertion's — see this function's
     * header. Emitted through `vm_emit` like any other subtree, which is why
     * §3.7's budget needs nothing new to count its work.
     *
     * A LOOKBEHIND SENDS EVERY BRANCH TO THE SAME `okl`, so the tail below is
     * one shape for both directions: what changes is how control GETS there
     * (one body, or `m` back-step-then-body branches), never what happens
     * once it has. */
    if (behind) {
        vm_look_behind(v, a, okl, mslot, pslot);
    } else {
        const int bodyl = vm_label(v);
        vm_goto(v, bodyl);
        vm_emit(v, bodyl, a->l, okl);
    }

    if (neg) {
        vm_lbl(v, okl, "negative lookaround: the body SUCCEEDED, so the "
                       "ASSERTION FAILS -- cut away the body's frames AND the "
                       "body-failed continuation, then fail");
        vm_cut(v, mslot, "cut: the assertion has failed; the body-failed "
                         "continuation must not survive to be resumed later");
        vm_fail(v);

        vm_lbl(v, negokl, "negative lookaround: the body is EXHAUSTED, so the "
                          "assertion HOLDS -- the fail label's pop of this "
                          "frame has already restored the cursor and rewound "
                          "every capture the body wrote");
        vm_goto(v, next);
    } else {
        vm_lbl(v, okl, atomic
               ? "positive lookaround: the body's FIRST success -- cut, "
                 "restore the cursor, and never reconsider"
               : "positive lookaround (NON-ATOMIC): a body success -- restore "
                 "the cursor, leaving the body's choice points LIVE so a "
                 "later failure can re-enter and reach a DIFFERENT success");
        if (atomic)
            vm_cut(v, mslot, "cut: the assertion is committed; every choice "
                             "point the body created is discarded, dead or not");
        {
            char sl[64];
            vm_slot_expr(v, pslot, sl, sizeof sl);
            sb_printf(b, "    scan_position = (size_t)slot_values[%s];\n", sl);
            vm_ev(v, VE_NOTE, 0, 0,
                  "lookaround: the position is DISCARDED -- the cursor goes "
                  "back to the assertion's entry");
        }
        vm_goto(v, next);
    }

    v->fmin = sf;
    v->fdyn = sd;
}

/* [DD-14 wave B+C] `W`, THE ACTIVATION-PRIVATE RESTORE SET (design §5.3a).
 *
 *   W(g) = every SLOT INSTANCE the EMITTED REGION for g can write,
 *          union W(h) for every h that region calls,
 *          MINUS slots 0 and 1.
 *
 * IT IS NOT "THE CAPTURE SLOTS", AND THAT ANSWER IS MEASURED WRONG RATHER
 * THAN MERELY INCOMPLETE — the row this design had refuted TWICE, by two
 * different executions:
 *
 *   `SLOT_GROUP<n>_PENDING`  a LOST MATCH. `^(a(?1)?b)\1$` on "aabbaabb"
 *                            answers nomatch where 10.46 answers (0,8): the
 *                            backreference MARKS group 1, so it lowers
 *                            publish-at-close, and the inner activation
 *                            overwrites the outer's pending value. 11/2.
 *   `SLOT_CUT_MARK<n>`       SIX FALSE MATCHES, and the false-match set is
 *                            EXACTLY the non-atomic control's language:
 *                            `^((?>a(?1)?))a$` starts matching "aa".."aaaaaaaa"
 *                            because the inner activation's mark overwrites
 *                            the outer's, so the outer's `RX_CUT` — an
 *                            ASSIGNMENT — becomes a no-op and the atomic group
 *                            stops being atomic. 4/6.
 *
 * EVERY FAMILY IS THE SAME SHAPE: each is written at a construct's ENTRY and
 * read at that construct's EXIT, and two ACTIVATIONS of one construct are
 * NESTED rather than sequential, so the inner write is still in the slot when
 * the outer reads it. Five of the seven families replicate PER EMITTED COPY,
 * not per lexical construct (`^((?>a)){3}$` has ONE atomic group and FOUR cut
 * marks), which is why the set is built from the COUNTER RANGES this region's
 * own `vm_count_slots` pass consumed rather than from a walk over its nodes.
 *
 * SLOTS 0 AND 1 ARE EXCLUDED BY CONSTRUCTION rather than by a filter: the
 * capture half below starts at group 1, and no other family's base reaches
 * below `2 * (ngroups + 1)`. §3.4(b) MEASURED why it matters — `\K` is NOT
 * restored by a return (`^(a\Kb)(?1)$` on "abab" is (3,4)) and pcrec spells
 * `\K` as a write to `RX_SLOT_WHOLE_START`, which is slot 0. A return that
 * restored "everything the callee wrote" would answer (0,4).
 *
 * AND `g`'s OWN CAPTURE SLOTS ARE MEMBERS, which an earlier draft left out and
 * the design's own prototype refuted: `^((a)(?1)?(b))$` on "aabb" is g1 =
 * (0,4), so the recursive call OVERWROTE group 1's start with 1 and the return
 * put 0 back. Without them the matcher reports g1 = (1,4) — a wrong span on a
 * correct match, which no `m`/`n` expectation catches and only a `g` line
 * does. */
typedef struct { int guard, low, mark, rev, ctr, lookmark, lookpos; } VmSnap;

static VmSnap vm_snap(const Vm *v)
{
    VmSnap s;
    s.guard = v->nguard; s.low = v->nlow; s.mark = v->nmark;
    s.rev = v->nrev; s.ctr = v->nctr;
    s.lookmark = v->nlookmark; s.lookpos = v->nlookpos;
    return s;
}

/* The region's CAPTURE half: every group whose `A_CAP` lies inside it. Walked
 * ITERATIVELY on `A_CAT`/`A_ALT` spines (D10/DD-10/K20) and STOPPING AT AN
 * `A_CALL` — following `.body` would be design §4.4's non-terminating walk,
 * and it is unnecessary: what a NESTED call writes arrives through the
 * transitive union below, over the graph, which terminates by construction. */
static void vm_w_caps(Vm *v, const Ast *a, bool *w, int nstate)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF: case A_CALL:
            return;
        case A_CAP: {
            int g = a->u.cap.no;
            if (g > 0 && g <= v->ngroups) {
                if (2 * g + 1 < nstate) { w[2 * g] = true; w[2 * g + 1] = true; }
                if (vm_marked(v, g)) {
                    int ps = vm_slot_pend(v, g);
                    if (ps >= 0 && ps < nstate) w[ps] = true;
                }
            }
            a = a->l;
            continue;
        }
        case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            const Ast *t = a;
            for (; t->k == k; t = t->l) vm_w_caps(v, t->r, w, nstate);
            a = t;
            continue;
        }
        }
        return;
    }
}

/* Publish one round of the nullability fixpoint onto the `A_CALL` nodes. Same
 * shape as `src/opt/callgraph.c`'s `minw` publisher and for the same reason:
 * the walkers that READ the answer are bare `const Ast *` descents with no
 * context, so the node is the only place both sides can meet. */
static void vm_publish_nonnull(Vm *v, Ast *a, const bool *nn)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF:
            return;
        case A_CALL: {
            int i = pcrec_callgraph_index(v->cg, a->u.call.target);
            a->u.call.nonnullable = i >= 0 ? nn[i] : false;
            return;
        }
        case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            Ast *t = a;
            for (; t->k == k; t = t->l) vm_publish_nonnull(v, t->r, nn);
            a = t;
            continue;
        }
        }
        return;
    }
}

/* Publish `W` onto every `A_CALL` node: `u.call.save`/`nsave`, read by
 * `vm_call`'s save emission, by `vm_region`'s restore emission and by
 * `vm_cost`'s `2 * |W|` trail charge. Three readers, one write. */
static void vm_publish_saves(Vm *v, Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF:
            return;
        case A_CALL: {
            int i = pcrec_callgraph_index(v->cg, a->u.call.target);
            if (i < 0)
                ctx_fail(v->cx, 0, "internal error: subroutine call to group "
                                   "%d is not in the call graph",
                         a->u.call.target);
            a->u.call.save  = v->rgn_w[i];
            a->u.call.nsave = v->rgn_nw[i];
            return;
        }
        case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            Ast *t = a;
            for (; t->k == k; t = t->l) vm_publish_saves(v, t->r);
            a = t;
            continue;
        }
        }
        return;
    }
}

static void vm_w_range(bool *w, int nstate, int lo, int hi)
{
    for (int i = lo; i < hi; i++) if (i >= 0 && i < nstate) w[i] = true;
}

/* [DD-14 wave B+C] THE CALL SITE (design §5.1, §5.3).
 *
 *     L_site:  RX_CALL(&&L_ret, scan_position)   ; a resume frame carrying a
 *                                                 ; RETURN LABEL
 *              RX_SET(W[0], slot_values[W[0]])   ; |W| trailed SELF-writes
 *              ...                               ; parking the caller's values
 *              RX_SET(W[n-1], slot_values[W[n-1]])
 *              goto L_callee_g
 *     L_ret:   <the continuation>
 *
 * THE SAVES COME AFTER THE PUSH AND THE ORDER IS LOAD-BEARING (§5.1). The call
 * frame's `trail_mark` is then EXACTLY the index of the first save, so the
 * return reads `W[j]`'s parked value at `trail[trail_mark + j]` with `j` a
 * compile-time constant — no search, no loop, no runtime slot test. It also
 * means a rewind that ABANDONS the call discards the saves along with the
 * frame that owned them.
 *
 * THE SELF-WRITE IS HOW THE TRAIL BECOMES THE STORAGE, with no new array
 * anywhere. `RX_SET` is `RX_TRAIL` then the write, and `RX_TRAIL` records the
 * old value UNCONDITIONALLY with no same-value elision (P7, quoted at the
 * macro) — so `RX_SET(s, slot_values[s])` leaves the slot UNCHANGED and parks
 * its current value on the trail at a known offset. The restore at the
 * region's exit is itself TRAILED, which is why backtracking INTO a returned
 * call correctly re-establishes the callee's own values (§3.2 requires it;
 * §3.1's per-level cells show it is the observable semantics).
 *
 * WHY THE SET IS `W` AND NOT "THE CAPTURES", and this is the row the design
 * had refuted TWICE: the capture-only version loses `SLOT_GROUP<n>_PENDING`
 * (a LOST MATCH, measured 11/2) and `SLOT_CUT_MARK<n>` (SIX FALSE MATCHES
 * whose language is exactly the non-atomic control's, measured 4/6). `W` is
 * every slot the emitted REGION can write, over the REGION's own indices,
 * minus slots 0 and 1 — `\K` writes slot 0 and is MEASURED not to be restored
 * by a return (§3.4(b)). `vm_region_w` builds it.
 *
 * NOTHING IS CUT HERE. §3.2 MEASURED the call BACKTRACKABLE on 10.46 (atomic
 * before 10.30), with four atomic controls refusing, so the return may not be
 * an `RX_CUT` and the callee's choice points stay live across it. */
static void vm_call(Vm *v, int entry, const Ast *a, int next)
{
    vm_charge(v);
    const int idx = v->cg ? pcrec_callgraph_index(v->cg, a->u.call.target) : -1;
    if (idx < 0 || !v->rgn_lbl)
        ctx_fail(v->cx, 0, "internal error: subroutine call to group %d has no "
                           "emitted region", a->u.call.target);

    const int ret = vm_label(v);
    vm_lbl(v, entry, a->u.call.target == 0
                     ? "call the WHOLE PATTERN (anchors included)"
                     : "call a capture group's pattern");
    /* Through a primitive, like every other emitted push: the listing's
     * PROGRAM trace and the artifact are two views of one walk (§10's drift
     * rule), and a call is a thing that EXECUTES. */
    sb_printf(v->b, "    %s_CALL(&&%s_L%d, scan_position);\n", v->up, v->p, ret);
    vm_ev(v, VE_CALL, v->rgn_lbl[idx], ret,
          vm_rolef(v, "call group %d; the frame carries the return label",
                   a->u.call.target));
    v->ncall++;
    for (int j = 0; j < a->u.call.nsave; j++) {
        /* Sized from what it holds — `up` is at most 80 bytes and
         * `vm_slot_name` writes at most 48 — for the reason `vm_slot_expr`
         * states one function over: a silently TRUNCATED slot name is an
         * artifact that names the wrong cell, and this file has already been
         * bitten once by a too-small snprintf buffer. */
        char val[160];
        char nm[48];
        if (vm_slot_name(v, a->u.call.save[j], nm, sizeof nm))
            snprintf(val, sizeof val, "slot_values[%s_%s]", v->up, nm);
        else
            snprintf(val, sizeof val, "slot_values[%d]", a->u.call.save[j]);
        vm_set(v, a->u.call.save[j], val,
               "park this activation's value on the trail (a trailed SELF-write)");
    }
    vm_goto(v, v->rgn_lbl[idx]);
    vm_lbl(v, ret, "the call returned; continue here");
    vm_goto(v, next);
}

/* [DD-14 wave B+C] ONE SHARED CALLEE REGION PER DISTINCT CALLED GROUP, EMITTED
 * AFTER THE MAIN BODY, WITH ITS OWN EXIT (design §3.5, §5.4, §6.3).
 *
 * THE EXIT IS THE WHOLE OF §6.3's SPLIT, and §3.5 is why it is a RULE rather
 * than an optimisation. A call reaches the GROUP, not the group's LEXICAL
 * OCCURRENCE, and the occurrence's wrapper is a property of the occurrence:
 * MEASURED on 10.46, `^ab(?<=(ab))(?1)$` matches "abab" (the callee must leave
 * through its OWN exit, not the lookbehind's end-check-cut-and-restore),
 * `^(?!(z|zy))x(?1)c$` matches "xzyc" (it must RETRY inside a region whose
 * lexical home is cut on the assertion's success), and `^(?>(a|ab))z(?1)c$`
 * matches "azabc" (it must GIVE BACK, though its lexical home is atomic). An
 * emitter that let the region fall out through the occurrence's continuation
 * gets all three wrong, and `^(?:(?<g>a|ab)){0}(?&g)c$` has no lexical
 * emission to fall out of at all.
 *
 * THE FOLLOW IS SCOPED TO ZERO ACROSS THE BODY (§5.4), for a reason one
 * construct over from `vm_look`'s: there the follow OVERLAPS the body, here it
 * is UNKNOWN, because a shared body has many callers with different follows
 * and a prune bound baked from one caller's follow is wrong for every other.
 * `vm_emit_fd` saves, zeroes and restores both terms on every path out.
 *
 * THE RESTORE READS THE TRAIL AT A COMPILE-TIME OFFSET off the ACTIVATION's
 * own frame (§5.3c). The saves cannot have been rewound while the activation
 * is live: every frame the body pushed has a `trail_mark` at or above
 * `trail_mark + |W|`, so no rewind that keeps the call alive can reach them,
 * and one that does has popped the call frame itself.
 *
 * AND THE `goto *` IS WRITTEN OUT HERE RATHER THAN HIDDEN IN AN `RX_RETURN`
 * MACRO, which is a deliberate deviation from §5.1's sketch. §5.8's invariant
 * is `goto *` count == 1 + the number of emitted SHARED CALLEE BODIES, and
 * S-SR13 asserts THE RELATION rather than a constant — so it must be
 * assertible over the artifact's TEXT. A macro puts one `goto *` in the
 * definition and none at the uses, which makes the count `1 + (has_calls ? 1 :
 * 0)` and the relation unstateable. Inline, the artifact carries exactly one
 * per region and the check is a grep. */
static void vm_region(Vm *v, int i)
{
    const int g = pcrec_callgraph_target(v->cg, i);
    const Ast *body = pcrec_callgraph_body(v->cg, i);

    vm_emit_fd(v, v->rgn_lbl[i], body, v->rgn_exit[i], 0, NULL);
    vm_lbl(v, v->rgn_exit[i],
           vm_rolef(v, "the callee region for %s returns",
                    g == 0 ? "the whole pattern" : "a capture group"));
    for (int j = 0; j < v->rgn_nw[i]; j++) {
        char val[192];
        snprintf(val, sizeof val,
                 "run->trail[run->resume_stack[run->call_top].trail_mark + %d]"
                 ".saved_value", j);
        vm_set(v, v->rgn_w[i][j], val,
               "restore the caller's value, itself TRAILED so a retreat into "
               "this callee re-establishes the callee's own");
    }
    /* THE SECOND INDIRECT JUMP (§5.8), and the amendment to this file's own
     * opening comment: the property that matters is that the indirect jumps
     * are OFF THE HOT PATH — one per backtrack, one per call return — and that
     * there is still no per-byte dispatch, so D13's table-vs-computed-goto
     * arbitration does not arise.
     *
     * THE FRAME IS NOT POPPED. §3.2 MEASURED the call backtrackable, so the
     * callee's choice points must survive the return and so must the return
     * label they will come back through. `call_top` walks DOWN the activation
     * chain to the frame this one was entered from — a linked list through
     * frames that already exist, which is what makes it stable under the frame
     * array's own growth (§5.1 property 2).
     *
     * THE SENTINEL TEST IS D72's CODE, not a give-up. Reaching a region's exit
     * with no live activation means the artifact's own analyses disagree — a
     * region is only ever entered from the `RX_CALL` two lines above its
     * `goto`, so it is unreachable — and PCREC_ERR_INTERNAL is exactly the
     * "the artifact detected an inconsistency between its own analyses" code
     * D72 minted, strictly below the give-up floor so a caller's raise-a-bound
     * retry cannot loop on it. Without the test the same event is
     * `resume_stack[(unsigned)-1]`, which is K27's class in emitted code. */
    sb_printf(v->b,
        "    {\n"
        "        const unsigned %s_call_frame = run->call_top;\n"
        "        if (%s_call_frame >= %s_RESUME_FRAMES) return %s_R_INTERNAL;\n"
        "        run->call_top = run->resume_stack[%s_call_frame].call_top;\n"
        "        goto *run->resume_stack[%s_call_frame].call_ret;\n"
        "    }\n",
        v->p, v->p, v->up, v->up, v->p, v->p);
    vm_ev(v, VE_RETURN, v->rgn_lbl[i], 0,
          "return to the caller through the frame's own label");
}

static void vm_emit(Vm *v, int entry, const Ast *a, int next)
{
    StrBuf *b = v->b;
    vm_charge(v);

    switch (a->k) {
    case A_CLASS: {
        int ci = vm_cls(v, a->u.cls.bits);
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_CLASS, ci, next, NULL);
        sb_puts(b, "    if (scan_position < subject_length && (");
        vm_cls_test(v, b, ci, "subject[scan_position]");
        sb_printf(b, ")) { scan_position++; goto %s_L%d; }\n", v->p, next);
        vm_fail(v);
        return;
    }
    case A_EMPTY:
        vm_lbl(v, entry, "empty");
        vm_goto(v, next);
        return;
    case A_BOL:
        if (a->u.anch.multiline) {
            /* [M6.2 wave C] `(?m)^` (assertions_design.md §9.3). THE GUARD IS
             * IN THE EXPRESSION, K27's discipline and `\b`'s precedent four
             * arms down: `pos == 0` short-circuits before `s[pos-1]` is ever
             * formed, so the arm never computes an out-of-range pointer even
             * on the legal `(s == NULL, n == 0)` subject of match_api.md
             * §3.1. Writing the position case in prose and the byte case in
             * code is exactly how that read gets left unguarded.
             *
             * THE NEWLINE COMES FROM THE CLASS POOL (D64): the same
             * `pcrec_cls_newline` src/ir/dfa.c refines its alphabet by and
             * `\N` compiles from — one definition, three readers, no `'\n'`
             * respelled here. */
            /* `pos < n` IS NOT A BOUNDS GUARD — it is the semantics.
             * PCRE2's multiline `^` "does not match after a newline that ends
             * the string", so `(?m)^` on "a\n" holds at 0 and NOT at 2 while
             * `(?m)$` holds at 1 AND 2. assertions_design.md §9.3's table row
             * omits it and python3 `re` disagrees with PCRE2 about it (U11);
             * this arm follows PCRE2, which D26 makes the source of truth. */
            int ni = vm_cls(v, pcrec_cls_newline);
            vm_lbl(v, entry, NULL);
            vm_ev(v, VE_ASSERT, next, 0,
                  "(?m)^ attempt_position of subject or after a non-final newline");
            sb_puts(b, "    if (scan_position == 0 || (scan_position < subject_length && (");
            vm_cls_test(v, b, ni, "subject[scan_position-1]");
            sb_printf(b, "))) goto %s_L%d;\n", v->p, next);
            vm_fail(v);
            return;
        }
        /* `^` is start of SUBJECT, absolute — it anchors to offset 0 whatever
         * startpos was, matching the emitted contract in lib/pcrec.h and the
         * DFA's own N_BOT. */
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_ASSERT, next, 0, "^ attempt_position of subject (absolute offset 0)");
        sb_printf(b, "    if (scan_position == 0) goto %s_L%d;\n", v->p, next);
        vm_fail(v);
        return;
    case A_EOL:
        if (a->u.anch.multiline) {
            /* [M6.2 wave C] `(?m)$` — end of subject or BEFORE ANY newline,
             * which is a strictly wider set than plain `$`'s "before a FINAL
             * newline". `pos == n` short-circuits before `s[pos]`. */
            int ni = vm_cls(v, pcrec_cls_newline);
            vm_lbl(v, entry, NULL);
            vm_ev(v, VE_ASSERT, next, 0,
                  "(?m)$ end of subject or before a newline");
            sb_puts(b, "    if (scan_position == subject_length || (");
            vm_cls_test(v, b, ni, "subject[scan_position]");
            sb_printf(b, ")) goto %s_L%d;\n", v->p, next);
            vm_fail(v);
            return;
        }
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_ASSERT, next, 0,
              "$ end of subject, or before a final newline");
        sb_printf(b, "    if (scan_position == subject_length || (scan_position + 1 == subject_length && subject[scan_position] == '\\n')) "
                     "goto %s_L%d;\n", v->p, next);
        vm_fail(v);
        return;
    case A_END:
        /* [M6.2 wave A] `\z` — end of subject, and NOT before a final
         * newline. assertions_design.md §9.3: both engines carry every
         * construct, because `--engine=vm` is what makes the DFA's answers
         * trustworthy rather than an echo of themselves. Note this arm reads
         * no byte at all, so it needs none of the guards `\b`'s spelling will
         * (K27's class): `pos == n` is a position test. */
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_ASSERT, next, 0, "\\z end of subject (absolute)");
        sb_printf(b, "    if (scan_position == subject_length) goto %s_L%d;\n", v->p, next);
        vm_fail(v);
        return;
    case A_GSTART:
        /* [M6.2 wave D] `\G` — the first matching position
         * (assertions_design.md §9.3's table row, §4).
         *
         * IT IS THE ONLY ASSERTION IN THIS SWITCH THAT READS A VALUE FROM
         * OUTSIDE THE PROGRAM, and that is what costs the extra parameter on
         * `<prefix>_match_impl`. `pos`, `n` and `s` are all in scope already;
         * "the offset this search was started from" is not, because
         * `ctx->pos` is the offset THIS ATTEMPT was started from and the
         * search entry's retry loop moves it. The parameter is emitted only
         * where a `\G` exists (`v->ngst`), on the MRL ceiling's precedent and
         * for the same discharge: an obligation of the form "every caller
         * must remember to pass X" becomes a compile error rather than a
         * convention.
         *
         * WHAT THE THREE ENTRIES PASS, and R30 E8 is the reason the two
         * match-here ones are not an oversight:
         *   `<prefix>_search`      -> its own `startpos` argument;
         *   `<prefix>_match`       -> `ctx->pos`;
         *   `<prefix>_match_caps`  -> `ctx->pos`.
         * Under a match-here entry `\G` means `pos == ctx->pos`, trivially
         * true at entry — the same answer the design's first draft reached
         * through a premise ("the rx_ctx has no startpos") that is factually
         * wrong. It is threaded; it IS `ctx->pos`.
         *
         * No guard is needed and none is written: this arm reads no byte, so
         * K27's class does not arise here any more than it does for `\z`. */
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_ASSERT, next, 0,
              "\\G the first matching position (search_from)");
        v->ngst++;
        sb_printf(b, "    if (scan_position == %s_search_from) goto %s_L%d;\n",
                  v->p, v->p, next);
        vm_fail(v);
        return;
    case A_KRESET:
        /* [M6.2 wave E] `\K` — RESET THE REPORTED START (§6.2, §9.3's last
         * table row). The module's last construct, and the only arm in this
         * switch that emits no test and cannot fail: there is no `vm_fail`
         * below it and no `goto` guarded by anything.
         *
         * IT IS A CAPTURE WRITE, SPELLED AS ONE. `vm_set` is the same
         * primitive A_CAP's two writes go through, so `\K` inherits the whole
         * of §3.2's write-and-undo discipline for free rather than by a
         * parallel mechanism:
         *
         *   - it is TRAILED, so a backtrack past this point restores the
         *     PREVIOUS value exactly (never a clear). That is not a corner
         *     case: `(?:a\K)*ab` on "aaab" is PCRE2 (2,4), reached by writing
         *     3 on the greedy path, failing the follow, and retreating to a
         *     state where the write of 3 must be GONE and the write of 2 must
         *     stand. `(?:a\K|ax)c` on "axc" is the same requirement across an
         *     alternation instead of a loop: (0,3), which needs the `a\K`
         *     branch's write of 1 undone when that branch loses. Both are
         *     corpus cells; both are libpcre2-measured.
         *   - it is rewound by `<prefix>_unwind` on a failed attempt, so a
         *     `\K` reached during a doomed attempt at `start` cannot leak into
         *     the answer for `start + 1`.
         *   - it appears in the listing as a slot write, through the same
         *     `vm_ev` the primitive already does.
         *
         * THE SLOT IS 0, AND CHOOSING IT IS THE WHOLE DESIGN. Slot 0 is group
         * 0's start — reserved by `nstate`'s `2 * ncaps` term since [M4.5b],
         * and never written by anything, because `vm_set` for group k uses
         * `2*k` with k >= 1 and every other slot family bases at
         * `2 * (ngroups + 1)`. So the slot that already MEANS "the reported
         * start of the match" is the one `\K` writes, no slot is allocated,
         * no capacity changes, and `<prefix>_caps_out` reads one existing
         * array element instead of taking a new parameter.
         *
         * PCREC_UNSET IS THE "NO `\K` WAS CROSSED" SIGNAL and it is not an
         * overload: `run_state_init` fills every slot with it once per search, and
         * the trail restores it by construction on every rewind to mark 0. A
         * position can never legitimately be PCREC_UNSET (-1), so the test in
         * `report_captures` is total. `(?:a\K)?b` on "b" is the cell — PCRE2 (0,1),
         * the `\K` not crossed — beside `(?:a\K)?b` on "ab", which is (1,2).
         *
         * `vm_charge` at the top of this function has already counted the
         * node; nothing else here costs anything. */
        v->nkreset++;
        vm_lbl(v, entry, NULL);
        vm_set(v, 0, "(ptrdiff_t)scan_position",
               "\\K resets the reported start of the match to here");
        vm_goto(v, next);
        return;
    case A_WORDB:
    case A_NWORDB: {
        /* [M6.2 wave B] `\b` / `\B` (assertions_design.md §9.3).
         *
         * THE GUARDS ARE IN THE EXPRESSION, and that is R30 m2's correction
         * rather than defensive padding. The natural spelling —
         * `word(s[pos-1]) != word(s[pos])` — reads `s[-1]` at `pos == 0` and
         * `s[n]` at `pos == n`, and docs/spec/match_api.md §3.1 makes
         * `(s == NULL, n == 0)` a LEGAL subject, so at `n == 0` BOTH operands
         * must short-circuit before any dereference. That is K27's exact
         * class: undefined behaviour in EMITTED code, which a user compiling
         * a generated matcher under their own -fsanitize=undefined sees
         * pcrec's name on.
         *
         * Out-of-subject counts as NON-WORD, which is what makes the guard
         * and the semantics the same expression: a failed bounds test yields
         * 0, which is exactly the value the missing byte would contribute.
         *
         * THE WORD SET COMES OUT OF THE CLASS POOL (§7.2 item 3), so it is
         * `pcrec_cls_word_esc` — the SAME table `\w` compiles from, interned
         * by content, so a pattern using both emits ONE bitmap and the two
         * constructs cannot disagree about what a word character is. */
        int wi = vm_cls(v, pcrec_cls_word_esc);
        bool neg = a->k == A_NWORDB;
        vm_lbl(v, entry, NULL);
        vm_ev(v, VE_ASSERT, next, 0,
              neg ? "\\B not a word boundary" : "\\b word boundary");
        sb_puts(b, "    if (((scan_position > 0 && (");
        vm_cls_test(v, b, wi, "subject[scan_position-1]");
        sb_puts(b, ")) ");
        sb_puts(b, neg ? "==" : "!=");
        sb_puts(b, " (scan_position < subject_length && (");
        vm_cls_test(v, b, wi, "subject[scan_position]");
        sb_printf(b, ")))) goto %s_L%d;\n", v->p, next);
        vm_fail(v);
        return;
    }
    case A_CAP: {
        /* §3.2 WRITE ON TRAVERSE: caps[k][0] when control passes the opening
         * position, caps[k][1] when it passes the closing one. Undo is EXACT
         * RESTORE of the previous value, never a clear — the trail, not this
         * site, is where that lives.
         *
         * [M6.5.2] EXCEPT FOR A MARKED GROUP — one a backreference names —
         * where the pair is PUBLISHED TOGETHER AT THE CLOSE
         * (backrefs_design.md §3.2, `vm_slot_pend`'s comment for the two
         * measured refutations of write-on-traverse). The open position goes
         * to the pending slot; the close writes both published slots from it.
         *
         * WRITE-ON-TRAVERSE IS UNOBSERVABLE WITHOUT A BACKREFERENCE, which is
         * why the correction is scoped rather than universal: at match
         * completion every group is closed and the published pair equals what
         * write-on-traverse leaves. The 5,808-cell sweep's backref-free
         * control arm is 0 divergences in BOTH disciplines, and §11.3's
         * byte-identity gate then holds by construction — an unmarked group
         * takes the same two lines it always did. */
        const bool marked = vm_marked(v, a->u.cap.no);
        int inner = vm_label(v), close = vm_label(v);
        vm_lbl(v, entry, vm_rolef(v, "group %d opens", a->u.cap.no));
        /* [ENG-BREP] SUPPRESSED inside a revdet loop's forward scan (v->nocap):
         * a per-iteration write is exactly the trail growth that rung exists to
         * remove, and §3.4's backward walk recovers the value the scan would
         * have left. vm_cost's A_CAP arm reads the same flag, so the emitted
         * code and the number the capacities are sized from cannot disagree.
         *
         * [M6.5.2] THE SUPPRESSION COVERS THE PENDING SLOT TOO, and it must:
         * the pending write and the pair it feeds are ONE publication, so
         * suppressing half of it would leave the backward walk's reconstructed
         * pair sitting beside a stale pending value from an earlier iteration.
         * Writing it as one guarded block is what makes "in step with the
         * pair" structural rather than a rule someone has to remember —
         * sabotage row S118 drops the pending write alone. (The backward
         * walk writes the published pair DIRECTLY, both halves adjacent, so it
         * is already a publication in the sense a reference needs.) */
        if (!v->nocap) {
            if (marked)
                vm_set(v, vm_slot_pend(v, a->u.cap.no), "(ptrdiff_t)scan_position",
                       vm_rolef(v, "group %d open, PENDING until this "
                                   "iteration closes", a->u.cap.no));
            else
                vm_set(v, 2 * a->u.cap.no, "(ptrdiff_t)scan_position",
                       vm_rolef(v, "group %d open, written on traverse",
                                a->u.cap.no));
        }
        vm_goto(v, inner);
        vm_emit(v, inner, a->l, close);
        vm_lbl(v, close, vm_rolef(v, "group %d closes", a->u.cap.no));
        if (!v->nocap) {
            if (marked) {
                char sl[144], val[176];
                vm_slot_expr(v, vm_slot_pend(v, a->u.cap.no), sl, sizeof sl);
                snprintf(val, sizeof val, "slot_values[%s]", sl);
                vm_set(v, 2 * a->u.cap.no, val,
                       vm_rolef(v, "group %d PUBLISHED: the pair goes out "
                                   "together, so a reference never sees a "
                                   "half-open span", a->u.cap.no));
            }
            vm_set(v, 2 * a->u.cap.no + 1, "(ptrdiff_t)scan_position",
                   vm_rolef(v, "group %d close, written on traverse",
                            a->u.cap.no));
        }
        vm_goto(v, next);
        return;
    }
    case A_BREF: {
        /* [M6.5.2] THE COMPARE (backrefs_design.md §3.2.3, §8.3).
         *
         * A chain of tests and a call. It reads the two PUBLISHED slots —
         * never a saved copy — and the trail discipline is what makes that
         * safe: the fail label rewinds to the popped frame's `trail_mark`
         * BEFORE transferring control, so by the time any label runs
         * `slot_values` holds exactly what that path published.
         *
         * THE UNSET TEST IS TOTAL, and only because of publish-at-close.
         * `run_state_init` fills every slot with `PCREC_UNSET` once per search
         * and the trail restores it on every rewind, so a PUBLISHED slot is
         * UNSET iff no live path has published it. Under write-on-traverse the
         * same sentence was FALSE for a re-entered group, and that is R32 E1
         * (see `vm_slot_pend` for the two measured refutations).
         *
         * PCRE2 FAILS on an unset reference; it does not match empty.
         * `^(a)?\1$` on "" is NO MATCH — measured, with python3 `re` agreeing
         * on all eight such cells. `PCRE2_MATCH_UNSET_BACKREF` would flip two
         * of them and is explicitly out of scope (§3.3).
         *
         * THE CHAIN IS §8.3's DUPNAMES RESOLUTION, emitted uniformly. For a
         * reference to a duplicated name, `refs` is the whole name-run in
         * ASCENDING GROUP NUMBER and the rule is "the FIRST member that is
         * SET" — measured against four candidate rules over eighteen cells,
         * with the "yy" cell killing "first by number" and the "xyy" cell
         * killing "last set". PCRE2 does NOT retry later members when the
         * first set one's COMPARE fails, which is what makes this a
         * frame-free if/else chain rather than a choice point. For
         * `nrefs == 1` it degenerates to a single `if`, which is the argument
         * for carrying the set uniformly: the dupnames path is the ordinary
         * path with the chain length at one, not a second, rarer,
         * less-tested path.
         *
         * "SET" INCLUDES SET-TO-EMPTY, and testing only the START slot is what
         * gets that right: `ref_start == ref_end` is a published empty
         * capture, the entry returns 0, and the reference succeeds having
         * consumed nothing. An implementation testing `ref_end > ref_start` as
         * a proxy for "is it set" turns every empty capture into a failure —
         * sabotage row S105.
         *
         * `ref_start <= ref_end` IS STRUCTURAL, not hoped for: a published
         * pair records the start before the body ran and the end after it, so
         * the subtraction the entry makes cannot underflow. That is the whole
         * memory-safety half of publish-at-close, and the entry's contract
         * states the precondition rather than paying for a runtime check.
         *
         * THE SEAM CALL IS NOT AN OPTIMISATION BOUNDARY. The compare must
         * route through the encoding residual FROM BIRTH (D58 scope item 3):
         * an inline `(s[i] | 32) == (s[j] | 32)` here is byte arithmetic that
         * is correct today and silently wrong under a UTF-8 backend, where one
         * captured character can fold to two and the consumed LENGTH stops
         * equalling `ref_end - ref_start`. That is why the entry returns a
         * length rather than a bool, and why there are TWO entries rather than
         * one with a `caseless` flag — D18/D23's rule is that an option
         * compiles away, and D23 measured a runtime fold indirection costing
         * 26% on a pattern with no letters in it. Sabotage row S109 inlines
         * the compare, and the codegen check's fixture-declared per-site count
         * is its only possible detector: inlining changes NO ANSWER under the
         * byte backend. */
        StrBuf *bb = v->b;
        char fn[96];
        /* NOT named `entry`: that is `vm_emit`'s LABEL parameter, and naming
         * a local after it here shadowed it — `vm_lbl(v, entry, ...)` then
         * emitted the label `PCREC_ENCE_BREF` (2) instead of the caller's, so
         * every `^(a)\1$`-shaped artifact carried a DUPLICATE LABEL and did
         * not compile. Caught by the corpus within one run; recorded because
         * `-Wall -Wextra` does not include `-Wshadow`. */
        const unsigned seam_entry = a->u.bref.caseless ? PCREC_ENCE_BREF_CASELESS
                                                : PCREC_ENCE_BREF;
        /* THE BACKEND'S OWN DECLARATION IS CONSULTED BEFORE THE CALL IS
         * EMITTED, and this is `engine_callable`'s one consumer on the compile
         * path (enc.h). DD-12 (7) forbids the matching machinery from
         * depending on the encoding, and `tests/codegen`'s [M5-SEAM] check
         * enforces it from OUTSIDE, on the artifact. This is the same rule
         * enforced from INSIDE, at the one site that could break it: an
         * emitter may route a construct through a residual entry only if the
         * backend says that entry may be called from an engine body.
         *
         * A backend whose compare declared `engine_callable = false` would
         * otherwise emit an artifact the codegen check then rejects — a
         * failure two steps and one test run away from its cause. Refusing
         * here makes it one step and names it. Unreachable for the byte
         * backend, which declares both compare entries callable; it is the
         * NEXT backend this line is for. */
        if (!pcrec_enc_entry_engine_callable(
                pcrec_enc_by_id(v->cx->opt->encoding), seam_entry))
            ctx_fail(v->cx, 0,
                     "internal error: this encoding's backreference compare is "
                     "not declared engine-callable, so it cannot be routed "
                     "through the seam from an engine body");
        v->enc_mask |= seam_entry;
        snprintf(fn, sizeof fn, "%s_bref_match%s", v->p,
                 a->u.bref.caseless ? "_caseless" : "");
        vm_lbl(v, entry, vm_rolef(v, "backreference to %s%s",
                                  a->u.bref.nrefs == 1 ? "one group" : "a name-run",
                                  a->u.bref.caseless ? ", caseless" : ""));
        sb_puts(bb, "    {\n        ptrdiff_t ref_start = PCREC_UNSET, "
                    "ref_end = PCREC_UNSET, took;\n");
        for (int i = 0; i < a->u.bref.nrefs; i++) {
            char ns[144], ne[144];
            vm_slot_expr(v, 2 * a->u.bref.refs[i], ns, sizeof ns);
            vm_slot_expr(v, 2 * a->u.bref.refs[i] + 1, ne, sizeof ne);
            sb_printf(bb,
                "        %sif (slot_values[%s] != PCREC_UNSET) {\n"
                "            ref_start = slot_values[%s];\n"
                "            ref_end   = slot_values[%s];\n"
                "        }%s",
                i ? "else " : "", ns, ns, ne,
                i + 1 == a->u.bref.nrefs ? "\n" : " ");
        }
        sb_printf(bb,
            "        /* No PUBLISHED capture on this path. PCRE2 FAILS here;\n"
            "         * it does not match the empty string. */\n"
            "        if (ref_start == PCREC_UNSET) goto %s_fail;\n"
            "        took = %s(subject, subject_length,\n"
            "                  (size_t)ref_start, (size_t)ref_end,\n"
            "                  scan_position);\n",
            v->p, fn);
        vm_ev(v, VE_FAIL, 0, 0, NULL);
        /* §3.8's WORK CHARGE, through the SAME `vm_work` primitive every other
         * charge site uses — one call, one truth, and a no-op on an artifact
         * with no budget. `took` on success; on failure the entry's negative
         * encoding carries the PREFIX it compared, so the bytes the fail label
         * never sees are charged EITHER WAY. Without it `(a*)\1` over a long
         * subject does unbounded byte comparison per step and DD-2's
         * robustness claim is quietly false for this module's whole
         * population. */
        vm_work_at(v, "        ", "took >= 0 ? took : -took - 1",
                   "backreference compare: the bytes it examined, which the "
                   "fail label never sees");
        sb_printf(bb,
            "        if (took < 0) goto %s_fail;\n"
            "        scan_position += (size_t)took;\n"
            "        goto %s_L%d;\n"
            "    }\n",
            v->p, v->p, next);
        vm_ev(v, VE_FAIL, 0, 0, NULL);
        vm_ev(v, VE_GOTO, next, 0, NULL);
        return;
    }
    case A_CAT: {
        /* flatten the left-leaning spine iteratively (nfa.c's R-2 hardening,
         * for the same reason: a flat concatenation of any length must not
         * overflow the C stack of pcrec's OWN emitter) */
        int nsp = 0;
        const Ast *t = a;
        while (t->k == A_CAT) { nsp++; t = t->l; }
        const Ast **rs = arena_alloc(&v->cx->arena, (size_t)nsp * sizeof(Ast *));
        int i = nsp;
        t = a;
        while (t->k == A_CAT) { rs[--i] = t->r; t = t->l; }
        /* [M4.6d] §4.3's FIRST threading line, over the flattened spine: the
         * element at index j is followed by everything after it plus this
         * concatenation's own follow. Computed as a SUFFIX SUM in one backward
         * pass — `minw` per element rather than per element-pair — so the
         * threading costs one walk over the spine and not one per position.
         *
         * `sfx[j]` is the follow-min of element j; `sfx[nsp]` is the whole
         * concatenation's own, i.e. what the caller set. The leftmost element
         * (`t`, which the flattening loop peeled off the bottom of the spine)
         * takes `sfx[0]`. */
        long long *sfx = arena_alloc(&v->cx->arena,
                                     (size_t)(nsp + 1) * sizeof(long long));
        sfx[nsp] = v->fmin;
        for (int j = nsp - 1; j >= 0; j--)
            sfx[j] = vm_fadd(pcrec_minw(rs[j]), sfx[j + 1]);
        int cur = entry;
        int nx = vm_label(v);
        vm_emit_f(v, cur, t, nx, sfx[0]);
        cur = nx;
        for (int j = 0; j < nsp; j++) {
            int after = (j + 1 == nsp) ? next : vm_label(v);
            vm_emit_f(v, cur, rs[j], after, sfx[j + 1]);
            cur = after;
        }
        return;
    }
    case A_ALT:
        vm_alt(v, entry, a, next);
        return;
    case A_REP:
        /* NOT under an atomic lift: `vm_atomic` is the ONLY caller that passes
         * true, which is what makes `under_atomic` a one-level edge property
         * rather than an inherited context. */
        vm_rep(v, entry, a, next, false);
        return;
    case A_ATOMIC:
        vm_atomic(v, entry, a, next);
        return;
    /* [M6.6.2 wave B+C] THE LOOKAROUND — `vm_look` above, which is `vm_atomic`
     * plus a saved cursor for the positive form, one pushed frame for the
     * negative one, and the atomic shape minus the cut for `(?*`. Wave A2's
     * loud `ctx_fail` stood here; the three edits it made inseparable all
     * landed together — this arm, `vm_count_slots`' own (which now allocates
     * both slot families and the negative form's frame), and the re-check of
     * `vm_cost`'s two constants recorded at that arm. */
    case A_LOOK:
        vm_look(v, entry, a, next);
        return;
    /* [DD-14] THE PRODUCER SITE, AND IT IS A HARD FAILURE UNTIL WAVE B+C.
     *
     * The call linkage is design §5: `RX_CALL` writes the return label into
     * the RESUME FRAME (§5.1 — the frame IS the call record; §5.2 derives and
     * §5.9's prototype REPRODUCES the clobber bug a separate `call_stack[]`
     * array has, three of fifty cells wrong, one a FALSE MATCH), the
     * activation-private save/restore of `u.call.save` rides the trail
     * (§5.3), `RX_RETURN` and the fail label's two lines close it, and
     * `CALL_SPLICE` (wave G) inlines the callee instead.
     *
     * IT IS NAMED RATHER THAN LEFT TO THE TAIL's generic "bad AST node in VM
     * emitter", which would send the next reader hunting for tree corruption
     * after a half-landed wave B+C. THIS ARM IS WHAT MAKES THE THREE COUPLED
     * EDITS INSEPARABLE: this one, `vm_count_slots`' region accounting
     * (§4.4c) and `vm_cost`'s graph-fed charge. Any two of them without the
     * third fail here, loudly, instead of emitting an artifact. */
    case A_CALL:
        vm_call(v, entry, a, next);
        return;
    }
    ctx_fail(v->cx, 0, "internal error: bad AST node in VM emitter");
}

/* ---- [M4.5c] rendering the listing ---------------------------------------
 *
 * Every section below is a VIEW over v->ev, the stream the emitter's own walk
 * produced. Nothing here re-derives anything from the AST — if it did, it
 * would be the parallel description engine_m4.md S10 forbids, and the first
 * time someone changed the emitter without changing the dump the dump would
 * start lying quietly. */

/* A byte class as a human reads it: 'a', [a-z], [0-9a-fx], or a count when it
 * is too scattered to spell. Derived from the SAME 256-bit bitmap the emitted
 * test is derived from (the class pool), not from the pattern text. */
static void vm_cls_describe(Vm *v, StrBuf *o, int ci)
{
    const uint8_t *bits = v->cls[ci];
    int count = 0;
    for (int c = 0; c < 256; c++) if (cls_has(bits, (unsigned)c)) count++;
    if (count == 256) { sb_puts(o, "any byte"); return; }
    if (count == 0)   { sb_puts(o, "(empty class)"); return; }

    /* Spell at most eight ranges; past that the count is more informative
     * than a wall of hex. */
    int nr = 0, shown = 0;
    for (int c = 0; c < 256; ) {
        if (!cls_has(bits, (unsigned)c)) { c++; continue; }
        int lo = c;
        while (c < 256 && cls_has(bits, (unsigned)c)) c++;
        nr++;
        if (nr > 8) continue;
        if (shown++ == 0) sb_puts(o, count == 1 ? "" : "[");
        else sb_puts(o, "");
        int hi = c - 1;
        char a[8], b[8];
        for (int k = 0; k < 2; k++) {
            int ch = k ? hi : lo;
            char *dst = k ? b : a;
            if (ch >= 32 && ch < 127 && ch != '\\' && ch != ']' && ch != '\'')
                snprintf(dst, 8, "%c", ch);
            else
                snprintf(dst, 8, "\\x%02x", ch);
        }
        if (lo == hi) sb_printf(o, count == 1 ? "'%s'" : "%s", a);
        else          sb_printf(o, "%s-%s", a, b);
    }
    if (nr > 8) {
        sb_printf(o, "...%d ranges, %d bytes]", nr, count);
    } else if (count != 1) {
        sb_puts(o, "]");
    }
}

typedef struct {
    long long budget, bt_frames, trail_frames, ceiling;
    int       nstate, nguard, nlow, nmark, ncaps;
    bool      has_budget, prefilter;
    /* [M6.5.2] does this artifact contain a backreference? Read only by the
     * listing's prefilter line, which without it names a FLAG the caller did
     * not pass as the reason a backref pattern has none. */
    bool      has_bref;
    const char *why;
} VmStamp;

/* [D46] renders v->rungs (the summary bitmask) as a comma-joined list of
 * kind names, e.g. "cursor, frames-unbounded", or "none" for a pattern with
 * no A_REP at all (a real, distinct answer — a caller asking "did the
 * cursor rung ever run" needs to tell "there was nothing to select between"
 * from "frames won every time", and D46's controllability half will need
 * the same distinction to report a forced selection with nothing to act
 * on). Read straight from the mask vm_rung_mark() built during the real
 * emission walk — never re-derived from the AST, per S10's own rule
 * (engine_m4.md S10): one structure, walked once, is what every view has
 * to agree with. The PER-QUANTIFIER detail this summarizes is the RUNGS
 * listing section below, built from the same VE_RUNG events. */
static void vm_rungs_describe(unsigned mask, StrBuf *o)
{
    if (!mask) { sb_puts(o, "none"); return; }
    bool first = true;
    for (int k = 0; k < VM_NRUNG; k++) {
        if (!(mask & vm_rung_bit[k])) continue;
        if (!first) sb_puts(o, ", ");
        sb_puts(o, vm_rung_kindname[k]);
        first = false;
    }
}

static void vm_strats_describe(unsigned mask, StrBuf *o)
{
    if (!mask) { sb_puts(o, "none"); return; }
    bool first = true;
    for (int k = 0; k < 2; k++) {
        if (!(mask & vm_strat_bit[k])) continue;
        if (!first) sb_puts(o, ", ");
        sb_puts(o, vm_strat_kindname[k]);
        first = false;
    }
}

static void vm_render_listing(Vm *v, StrBuf *o, const VmStamp *st)
{
    Ctx *cx = v->cx;

    sb_puts(o, "; pcrec VM program listing (DD-8; docs/design/engine_m4.md S10)\n");
    sb_puts(o, ";\n");
    sb_puts(o, "; Produced BY the emitter's own walk, not by a second walk over the\n");
    sb_puts(o, "; AST: every line below was written by the same call that wrote the\n");
    sb_puts(o, "; corresponding C. S10's one constraint -- \"the dump must be derived\n");
    sb_puts(o, "; from the same structure the emitter walks, never a parallel\n");
    sb_puts(o, "; description\" -- is therefore structural here, not a discipline.\n");
    sb_puts(o, ";\n");
    sb_puts(o, "; pattern      ");
    for (size_t i = 0; i < cx->patlen; i++) {
        unsigned char ch = (unsigned char)cx->pat[i];
        if (ch >= 32 && ch < 127) sb_putc(o, (char)ch);
        else sb_printf(o, "\\x%02x", ch);
    }
    sb_puts(o, "\n");
    sb_printf(o, "; engine       vm (forced by: %s)\n", st->why ? st->why : "--engine=vm");
    /* [M4.6f] the "off" reason now has TWO routes -- an explicit
     * -fno-prefilter, or the R21 E-6 side effect of --engine=vm with no
     * -fprefilter to override it back on -- and the listing names the one
     * that actually fired rather than assuming the older, single-route
     * text. The "yes" text does not need the same split: a forced-on
     * prefilter (-fprefilter under --engine=vm) is the SAME machinery as an
     * auto-derived one, §6.1's exactness claim unchanged either way. */
    /* [M6.5.2] A THIRD "off" ROUTE, tested FIRST because it is the one no flag
     * explains: a BACKREFERENCE pattern has no prefilter under ANY invocation.
     * Erasing a backreference is a real approximation that is not even a
     * SUPERSET once the referenced group's transitive closure holds an
     * assertion or an atomic/possessive operator, and where it IS a superset
     * its leftmost SPAN differs from the true one on a large fraction of
     * subjects -- so there is no exact window to hand the VM either way
     * (backrefs_design.md §7). Without this arm the listing said
     * "NO (--engine=vm)" for a pattern compiled under `auto`, i.e. a
     * diagnostic naming a flag the caller did not pass. */
    sb_printf(o, "; prefilter    %s\n", st->prefilter
              ? "yes -- the capture-erased forward+reverse DFA pair hands the VM"
                " an exact window (S6.1); the VM never scans"
              : st->has_bref
              ? "NO (backreference) -- the erased approximation is neither a"
                " sound superset nor the true span (S7); no flag changes this"
              : (cx->opt->flags & PCREC_NO_PREFILTER)
              ? "NO (-fno-prefilter) -- forced off; the VM scans from search_from itself"
              : "NO (--engine=vm) -- the VM scans from search_from itself (R21 E-6)");
    /* [D46] the rung stamp's QUICK-GLANCE summary: which rung KINDS appear
     * ANYWHERE in this program, not which one "the" program uses -- the
     * rung is selected per A_REP, so a pattern with two quantified bodies
     * can and does mix rungs (that is exactly the case a scalar summary
     * would get wrong). Read straight off v->rungs, the same bitmask the
     * <PREFIX>_VM_RUNGS macro below is built from. The RUNGS section further
     * down is the per-quantifier detail this line summarizes. */
    sb_puts(o, "; rungs        ");
    vm_rungs_describe(v->rungs, o);
    sb_puts(o, " -- see the RUNGS section below for which quantifier took"
               " which\n");
    /* [ENG-BREP] the ladder's first rung, summarized the same way and for the
     * same reason. "possessive" appearing here means at least one quantifier
     * needs no backtracking machinery at all; "backtracking" means at least
     * one still does. Both appearing is the mixed artifact a scalar would
     * misreport. */
    sb_puts(o, "; strategies   ");
    vm_strats_describe(v->strats, o);
    sb_puts(o, " -- see the STRATEGIES section below for which quantifier"
               " took which\n");
    /* [ENG-BREP] the pass's OWN census, from src/opt/possessify.c, and it is
     * deliberately not derived from the STRATEGIES rows below. Those are per
     * EMITTED quantifier, so a replicated bounded-repeat body contributes one
     * row per copy; these are per SOURCE `A_REP`, which is the only population
     * comparable with eng_brep_design.md §2.6's own census. Counting the rows
     * instead would measure replication as much as it measures the rule. */
    if (cx->opt->flags & PCREC_NO_POSSESSIFY)
        /* "0 of 0" would read as "this program has no quantifiers", which is
         * a different fact and usually a false one. A denied pass has not
         * counted anything, and the line says so. */
        sb_puts(o, "; possessify   DENIED (-fno-possessify): the pass did not"
                   " run, so nothing here was analysed\n");
    else
        sb_printf(o, "; possessify   %d of %d source quantifier%s possessified"
                     " (eng_brep_design.md S2)\n",
                  cx->poss_marked, cx->poss_total,
                  cx->poss_total == 1 ? "" : "s");
    /* The macro is <PREFIX>_NCAPS, not RX_NCAPS: naming a macro the artifact
     * does not contain would send a reader of a `-p myrx` listing looking for
     * a symbol that is not there. Every emitted name in this listing comes
     * from the same v->up/v->p the emitter used. */
    sb_printf(o, "; caps         %s_NCAPS %d (%d capturing group%s in the"
                 " pattern text)\n",
              v->up, st->ncaps, (int)cx->ncap, cx->ncap == 1 ? "" : "s");
    if (st->has_budget)
        sb_printf(o, "; step budget  %lld backtrack resumptions\n", st->budget);
    else
        sb_puts(o, "; step budget  none (--fno-step-budget)\n");
    sb_printf(o, "; capacities   %lld resume frames, %lld trail entries",
              st->bt_frames, st->trail_frames);
    if (st->ceiling > 0)
        sb_printf(o, " (subject ceiling %lld bytes)\n", st->ceiling);
    else
        sb_puts(o, " (exact: no subject ceiling)\n");
    sb_printf(o, "; program      %d labels, %d events\n", v->nlabel, v->nev);
    /* The PRE-PASS count, not a recount of the event stream. It is what
     * PCREC_MAX_VM_RESUME_POINTS is checked against before emission, so
     * printing it here is what lets a check compare the cap's own input
     * against the artifact that came out (tests/codegen/run_ir_listing.sh). */
    sb_printf(o, "; resume pts   %lld\n", v->npush);
    sb_printf(o, "; max replicas %lld (limit %d, checked before emission)\n",
              v->maxcopies, PCREC_MAX_VM_REPEAT_COPIES);

    /* ---- SLOTS ---------------------------------------------------------
     * The layout comes from vm_slot_guard/vm_slot_low, the same two functions
     * the emitter indexes with; "written" is derived from the VE_SET events,
     * so a slot the layout reserves and the program never writes shows up as
     * exactly that. */
    sb_puts(o, "\nSLOTS (the slot_values array, engine_m4.md S2.4)\n");
    sb_printf(o, "  %-12s %-22s %s\n", "slot", "holds", "note");
    for (int k = 0; k <= v->ngroups; k++) {
        int w = 0;
        for (int i = 0; i < v->nev; i++)
            if (v->ev[i].k == VE_SET && (v->ev[i].a == 2 * k || v->ev[i].a == 2 * k + 1))
                w++;
        char what[32];
        if (k == 0) snprintf(what, sizeof what, "$0 whole match");
        else        snprintf(what, sizeof what, "group %d", k);
        sb_printf(o, "  %2d,%-9d %-22s %s\n", 2 * k, 2 * k + 1, what,
                  /* [M6.2 wave E] slot 0 STOPS being entry-only the moment a
                   * `\K` exists: that is the whole of the construct's
                   * mechanism, and a listing still claiming "written by the
                   * ENTRY, not the VM" would describe a different program
                   * from the one beside it. The listing's own constraint
                   * (S10: derived from the structure the emitter walks) is
                   * about drift like this, and it costs one condition. */
                  k == 0 ? (v->nkreset > 0
                              ? "start written by the VM (\\K); end by the ENTRY"
                              : "written by the ENTRY, not the VM (S3.4)")
                         : (w ? "written on traverse, trailed" : "never written"));
    }
    if (v->nguard_total == 0)
        sb_puts(o, "  (no empty-iteration guard slots: no nullable unbounded"
                   " quantifier on the frames rung)\n");
    for (int i = 0; i < v->nguard_total; i++)
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_guard(v, i),
                  "empty-iteration guard", "where the current iteration began (S3.3)");
    if (v->nlow == 0)
        sb_puts(o, "  (no span-loop low-water slots: no cursor rung in this"
                   " program)\n");
    for (int i = 0; i < v->nlow; i++)
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_low(v, i),
                  "span-loop low-water", "the loop's entry position (S2.5)");
    for (int i = 0; i < v->nmark; i++)
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_mark(v, i),
                  "cut mark",
                  "resume-stack depth at entry -- a possessified loop's "
                  "(eng_brep_design.md S2) or an atomic group's ([M6.4.2])");
    for (int i = 0; i < v->nrev; i++) {
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_rev(v, i, 0),
                  "revdet loop entry", "the capture walk's floor (S2.5)");
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_rev(v, i, 1),
                  "revdet low-water", "boundary after rmin iterations: the retreat's floor");
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_rev(v, i, 2),
                  "revdet ceiling", "maximal boundary reached: the lazy extension's cap");
    }
    /* [M6.6.2] the lookaround's two families. They are listed SEPARATELY and
     * their counts can differ, which is the point: `nlookmark < nlookpos` says
     * this artifact contains a NON-ATOMIC form, and that is how a reader tells
     * the two atomicities apart in the listing (design §3.6). */
    for (int i = 0; i < v->nlookmark; i++)
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_lookmark(v, i),
                  "lookaround cut mark",
                  "resume-stack depth at the assertion's entry -- the atomic "
                  "and negative forms commit ([M6.6.2])");
    for (int i = 0; i < v->nlookpos; i++)
        sb_printf(o, "  %-12d %-22s %s\n", vm_slot_lookpos(v, i),
                  "lookaround cursor",
                  "the entry position the assertion restores: a lookaround "
                  "keeps the VERDICT and discards the POSITION");

    /* ---- RUNGS -----------------------------------------------------------
     * [D46] the PER-QUANTIFIER detail the header's "; rungs" summary line
     * folds into one bitmask. One row per A_REP, in emission order, each
     * naming the label the rung was recorded against (vm_rung_mark's own
     * `entry` argument) and the rung kind — never re-derived: every row
     * below is a VE_RUNG event vm_cursor_rep / vm_rep's frames fallthrough
     * appended at the same call that decided the rung. */
    sb_puts(o, "\nRUNGS (engine_m4.md S2.5; D46's per-quantifier stamp)\n");
    {
        int n = 0;
        for (int i = 0; i < v->nev; i++) {
            if (v->ev[i].k != VE_RUNG) continue;
            n++;
            sb_printf(o, "  at L%-6d %-18s %s\n", v->ev[i].a,
                      vm_rung_kindname[v->ev[i].b],
                      v->ev[i].role ? v->ev[i].role : "");
        }
        if (n == 0)
            sb_puts(o, "  (none: no quantifier in this program consulted the"
                       " rung ladder at all)\n");
    }

    /* ---- STRATEGIES ------------------------------------------------------
     * [ENG-BREP] the per-quantifier possessification verdict, as ACTED ON:
     * every row is a VE_STRAT event appended by the same vm_rung_mark() call
     * that decided the emitted shape, so a row saying "possessive" and an
     * artifact that emitted a resume frame for that quantifier are not two
     * things that could disagree — there is one call and it did both. */
    sb_puts(o, "\nSTRATEGIES (eng_brep_design.md S2; D47.3's per-quantifier"
               " stamp)\n");
    {
        int n = 0;
        for (int i = 0; i < v->nev; i++) {
            if (v->ev[i].k != VE_STRAT) continue;
            n++;
            sb_printf(o, "  at L%-6d %-14s %s\n", v->ev[i].a,
                      vm_strat_kindname[v->ev[i].b],
                      v->ev[i].role ? v->ev[i].role : "");
        }
        if (n == 0)
            sb_puts(o, "  (none: this program has no quantifier to possessify)\n");
    }

    /* ---- PRUNING ---------------------------------------------------------
     * [M4.6d] the per-quantifier MRL verdict, as ACTED ON. Same construction
     * and same guarantee as the two sections above: every row is a VE_PRUNE
     * event appended by the site that had the quantifier's own minrest in
     * hand, so "clamped" here and a bound in the emitted C are one fact
     * recorded once, not two that could disagree. */
    sb_printf(o, "\nPRUNING (k23_design.md; D51's per-quantifier stamp)"
                 "\n  ceiling: %s\n  bound sites emitted: %lld\n"
                 "  runtime-term length retreats: %lld%s\n",
              !v->mrl ? "none (-fno-length-prune)"
                      : v->mrl_win ? "min(subject_length, prefilter window end) -- D51 ruling 2"
                                   : "the subject end -- either no prefilter, or the prefilter's window END is not a bound on this match's end because the pattern carries an ATOMIC GROUP (atomic_groups_design.md 4.4 H3) or a LOOKAROUND (lookaround_design.md 5.6)",
              v->nclamp, v->ndynskip,
              v->ndynskip ? "  <- an outer counter-derived term was DROPPED"
                            " (sound: it under-estimates), so this artifact"
                            " prunes less than the analysis could"
                          : "");
    {
        int n = 0;
        for (int i = 0; i < v->nev; i++) {
            if (v->ev[i].k != VE_PRUNE) continue;
            n++;
            sb_printf(o, "  at L%-6d %-12s %s\n", v->ev[i].a,
                      vm_prune_kindname[v->ev[i].b],
                      v->ev[i].role ? v->ev[i].role : "");
        }
        if (n == 0)
            sb_puts(o, "  (none: this program has no quantifier to bound)\n");
    }

    /* ---- PROGRAM -------------------------------------------------------*/
    sb_puts(o, "\nPROGRAM\n");
    for (int i = 0; i < v->nev; i++) {
        const VEvent *e = &v->ev[i];
        switch (e->k) {
        case VE_LABEL:
            if (e->role) sb_printf(o, "  L%-6d ; %s\n", e->a, e->role);
            else         sb_printf(o, "  L%d\n", e->a);
            break;
        case VE_CLASS: {
            StrBuf d;
            memset(&d, 0, sizeof d);
            vm_cls_describe(v, &d, e->a);
            sb_printf(o, "         consume %-28s -> L%d\n", d.p ? d.p : "?", e->b);
            (void)0;
            sb_free(&d);
            break;
        }
        case VE_ASSERT:
            sb_printf(o, "         assert  %-28s -> L%d\n",
                      e->role ? e->role : "?", e->a);
            break;
        case VE_PUSH: {
            char tgt[24];
            snprintf(tgt, sizeof tgt, "resume L%d", e->a);
            sb_printf(o, "         PUSH    %-28s ; %s\n", tgt,
                      e->role ? e->role : "choice point");
            break;
        }
        case VE_SET: {
            /* Widened for [M6-READ]: `stv[2] <- pos` fitted in 24, but
             * `slot_values[2] <- scan_position` is 30 and snprintf silently
             * TRUNCATED it to `slot_values[2] <- scan_`. A rename that moves
             * emitted names has to check the listing's column widths too. */
            char slot[48];
            snprintf(slot, sizeof slot, "slot_values[%d] <- scan_position", e->a);
            sb_printf(o, "         set     %-28s ; %s\n", slot,
                      e->role ? e->role : "");
            break;
        }
        case VE_GOTO:
            sb_printf(o, "         -> L%d\n", e->a);
            break;
        case VE_FAIL:
            sb_puts(o, "         -> fail (backtrack)\n");
            break;
        case VE_NOTE:
            sb_printf(o, "         ; %s\n", e->role ? e->role : "");
            break;
        case VE_ACCEPT:
            sb_puts(o, "         -> accept\n");
            break;
        case VE_ISLAND: case VE_CALLOUT:
            break;
        case VE_RUNG:
        case VE_STRAT:
        case VE_PRUNE:
            /* the RUNGS, STRATEGIES and PRUNING sections above are these
             * events' own
             * views; PROGRAM stays a straight-line trace of what actually
             * executes, and neither a rung nor a strategy selection writes C
             * of its own to trace. */
            break;
        /* [DD-14 wave B+C] BOTH WRITE C, so like VE_CUT and unlike
         * VE_RUNG/VE_STRAT/VE_PRUNE they belong in the straight-line trace:
         * a call and a return are things that EXECUTE. */
        case VE_CALL: {
            char tgt[40];
            snprintf(tgt, sizeof tgt, "callee L%d, return L%d", e->a, e->b);
            sb_printf(o, "         CALL    %-28s ; %s\n", tgt,
                      e->role ? e->role : "subroutine call");
            break;
        }
        case VE_RETURN:
            sb_printf(o, "         RETURN  %-28s ; %s\n", "goto* frame.call_ret",
                      e->role ? e->role
                              : "the callee region's own exit (never the "
                                "lexical occurrence's)");
            break;
        case VE_CUT: {
            /* [ENG-BREP] this one DOES write C, so unlike the two above it
             * belongs in the trace. */
            char slot[32];
            snprintf(slot, sizeof slot, "frames <- slot_values[%d]", e->a);
            sb_printf(o, "         CUT     %-28s ; %s\n", slot,
                      e->role ? e->role : "commit: discard the loop's frames");
            break;
        }
        }
    }
    sb_puts(o, "  accept   ; return scan_position - ctx->pos; the capture slots at this"
               " instant ARE the answer (S3.1)\n");
    sb_puts(o, "  fail     ; the ONLY backtracker and the only indirect jump;"
               " one step charged here (S4.2)\n");

    /* ---- CHOICE POINTS -------------------------------------------------*/
    {
        int n = 0;
        sb_puts(o, "\nCHOICE POINTS (preference order: the frame pushed at a site"
                   " resumes the LESS preferred alternative)\n");
        int cur = -1;
        for (int i = 0; i < v->nev; i++) {
            if (v->ev[i].k == VE_LABEL) cur = v->ev[i].a;
            if (v->ev[i].k != VE_PUSH) continue;
            n++;
            sb_printf(o, "  at L%-6d resume L%-6d %s\n", cur, v->ev[i].a,
                      v->ev[i].role ? v->ev[i].role : "");
        }
        if (n == 0)
            sb_puts(o, "  (none: this program never backtracks -- it is a straight"
                       " line, and the resume stack is never pushed)\n");
    }

    /* ---- ISLANDS / CALLOUTS --------------------------------------------
     * Honestly empty, and empty by COUNT rather than by a hardcoded blank:
     * the day a producer exists these sections fill in with no change here. */
    {
        int isl = 0, co = 0;
        for (int i = 0; i < v->nev; i++) {
            if (v->ev[i].k == VE_ISLAND)  isl++;
            if (v->ev[i].k == VE_CALLOUT) co++;
        }
        sb_printf(o, "\nDFA ISLANDS (%d)\n", isl);
        if (isl == 0)
            sb_puts(o, "  (none: islands are [M4.6]; engine_m4.md S6.3/S6.4 --"
                       " the auto-possessification that proves an island exact"
                       " does not exist yet)\n");
        sb_printf(o, "\nCALLOUT SITES (%d)\n", co);
        if (co == 0)
            sb_puts(o, "  (none: module 'callouts' has no producer, so no"
                       " pattern can reach a call site -- engine_m4.md S9.1)\n");
    }
}

/* ---- the artifact -------------------------------------------------------*/

static long long vm_ceiling(long long cap, long long per)
{
    if (per <= 0) return 0;
    return cap / per;
}

void pcrec_emit_vm(Ctx *cx, Ast *root)
{
    Job *job = cx->job;
    StrBuf *c = &job->csb;
    Vm v;
    GenNames g;

    memset(&v, 0, sizeof v);
    v.cx = cx;
    v.b = &job->vmsb;   /* Job-owned, so the longjmp cleanup path frees it */
    v.p = cx->opt->prefix;
    /* [M6.5.2] `ngroups` IS THE SLOT-LAYOUT GROUP COUNT, and it is no longer
     * the same number as the artifact's reported `NCAPS`.
     *
     * §6.3's ruling: under `--no-captures` a group a BACKREFERENCE names keeps
     * its internal slots and reports none — `\K`'s precedent, where the flag
     * drops the group slots a CALLER can see and not the machinery a match
     * needs. So the slot array must span the highest MARKED group even when no
     * capture is reported, while `NCAPS` stays 1 and `caps_out` copies only
     * the whole-match pair. For a captures-on build the two numbers coincide
     * exactly as they always have, and for a `--no-captures` build with no
     * backreference `ngroups` is 0 and every downstream number is what it was
     * before this module existed.
     *
     * The parser has already deleted the `A_CAP` wrapper of every UNMARKED
     * group on a `--no-captures` build (`pcrec_bref_resolve`), so the slots
     * this reserves for the gaps below the highest marked number are never
     * written. They are reserved because the layout indexes by GROUP NUMBER —
     * `(a)(b)(c)\3` needs slot 6, whatever groups 1 and 2 do — and a
     * compacting map would be a second numbering for the emitter, the
     * listing and `report_captures` to agree about. */
    {
        int nmarkarr = (int)cx->ncap + 1;
        bool *mk = arena_alloc(&cx->arena, (size_t)nmarkarr * sizeof *mk);
        memset(mk, 0, (size_t)nmarkarr * sizeof *mk);
        pcrec_bref_mark(root, mk, nmarkarr);
        int *pend = arena_alloc(&cx->arena, (size_t)nmarkarr * sizeof *pend);
        int npend = 0, highest = 0;
        for (int grp = 0; grp < nmarkarr; grp++) {
            pend[grp] = -1;
            if (grp > 0 && mk[grp]) { pend[grp] = npend++; highest = grp; }
        }
        v.ngroups = cx->want_caps ? (int)cx->ncap : highest;
        v.pend_of = pend;
        v.npend_total = npend;
    }
    /* Set BEFORE the walk: vm_push_at reads it to decide whether the emitted
     * RX_PUSH carries its label id. */
    v.tracing = (cx->opt->flags & PCREC_TRACE) != 0;
    /* [ENG-BREP counter-K] K, resolved ONCE here. Set BEFORE vm_count_slots,
     * which is the first of the three consumers to run — vm_counter_fits reads
     * it, and a zero would make every quantifier "below K" and silently
     * disable the rung in the pre-pass while the emitter used the real value. */
    v.unroll_k = cx->opt->unroll_k > 0 ? cx->opt->unroll_k
                                       : PCREC_DEFAULT_UNROLL_K;
    /* [M4.6d] MRL's two artifact-wide facts, both set BEFORE the walk. The
     * enable flag is read at every emission site; the ceiling FORM is read
     * only by the stamp and by the entry points, because the walk itself sees
     * the ceiling through a macro and never needs to know which of the two it
     * is. `fit.prefilter` is select_engine's verdict and is final by now. */
    v.mrl     = (cx->opt->flags & PCREC_NO_LENGTH_PRUNE) == 0;
    /* [M6.4.2] RULE H3 — THE ONE PREDICATE, READ AT THREE SITES, and the
     * three-ness is R31 E3's whole finding.
     *
     * The prefilter is the capture-erased DFA, which for a cut-bearing pattern
     * necessarily answers for the UNCUT language (src/ir/nfa.c lowers an atomic
     * body transparently, because a subset construction keeps every alternative
     * alive — which IS the non-atomic semantics). Its REJECTION stays sound (no
     * uncut match means no atomic match) and its span START stays a lower bound
     * (H2, and the emitted loop already re-asks it on every retry), but its
     * span END IS NOT AN UPPER BOUND on the cut match's end:
     *
     *   (?>a|ab)c|abcd  on "abcd"   is (0,4);  the uncut twin is (0,3).
     *
     * MEASURED: 122 refuting cells over 17,640, and — on the EMITTED prefilter
     * rather than inferred from an oracle — 114 cells across 42 patterns
     * carrying a "prefilter-window" ceiling AND a window end strictly BELOW the
     * cut match's end. That is silent match loss in the DEFAULT engine.
     *
     * THE FIRST DESIGN OF THIS FIX EDITED THIS LINE AND NOTHING ELSE, AND THE
     * CHECK IT PROPOSED WOULD HAVE AGREED WITH THE BUG. `v.mrl_win` was read at
     * exactly two places — the `--emit-ir` description and the
     * `RX_VM_PRUNE_CEILING` STAMP — while the lines that BUILD the ceiling (the
     * search entry's `window_end = min(window[0][1], n)` and the retry
     * recompute) were gated on `prefn` and `v.nclamp > 0` and never on this
     * flag. Flipping it would have stamped "subject-end" on an artifact whose
     * ceiling was still live. So the two emission sites now read this SAME
     * flag, which is what makes the stamp unable to disagree with the code it
     * describes — and codegen rule 1 asserts on BOTH sources, because either
     * alone is satisfiable by a half-done edit.
     *
     * `pcrec_has_atomic` is asked of the POST-DISCHARGE tree, so a pattern
     * whose cut was proved a no-op keeps its ceiling: `[^"]*+"` loses nothing.
     * Dropping the PREFILTER entirely was the alternative and is strictly
     * worse — it would discard H1 and H2 as well, and losing the prefilter is
     * a DD-2 regression by engine_m4.md §4.7's own standard. Keeping rejection
     * and the start seed while dropping only the ceiling costs one predicate. */
    /* [M6.6.2 wave E] AND THE SECOND CONJUNCT, WHICH ARRIVES AT THE SAME
     * PLACE THROUGH A DIFFERENT DOOR. Design §5.6(2).
     *
     * `src/ir/nfa.c`'s `A_LOOK` arm lowers a lookaround to EPSILON — the
     * assertion is simply erased — so the prefilter answers for the
     * lookaround-FREE language. `L(P) SUBSET L(erase(P))` at every position
     * (§5.3, a one-line proof), which keeps H1 (rejection) and H2 (the span
     * START, re-asked on every retry) sound; the span END is again NOT an
     * upper bound:
     *
     *   ((?:a(?!q)|aq)(?:xy){0,4}q)  on "aqq"  is (0,3);  the erased twin
     *   ((?:a|aq)(?:xy){0,4}q) anchored there ends at 2.
     *
     * MEASURED (§5.4/§5.5): 8 sharp H3 violations over 45 cells, and — on the
     * EMITTED prefilter of the erasure rather than an oracle — 16 of 30 swept
     * shapes carry a LIVE "prefilter-window" ceiling AND a window end strictly
     * below the true match's end. The witness above is in
     * tests/lookaround/prefilter.rxt by name, and before this conjunct landed
     * pcrec answered NOMATCH on every one of that block's matching subjects.
     *
     * THE FLAT PREDICATE IS DELIBERATE. §5.4 shows the hazard needs a
     * lookaround inside an ALTERNATION, so a narrower predicate could ask for
     * that shape; it is rejected because the shape condition is a second
     * analysis with no independent check, and its failure mode is silent match
     * loss where the flat one's is a pruning ceiling a pattern rarely had.
     *
     * `pcrec_has_lookaround` is asked of the POST-DISCHARGE tree for the same
     * reason `pcrec_has_atomic` is: a pass that ever proves a lookaround
     * vacuous and deletes it gives the pattern its ceiling back.
     *
     * AND §5.6(3) IS THE OTHER HALF OF THIS WAVE, which is why the paragraph
     * above about R31 E3 is stated once and applies to both conjuncts: the two
     * lines that BUILD the ceiling read this SAME flag, and codegen rule 1
     * asserts on BOTH sources for BOTH modules through one shared check.
     * S-LA13 is the row, and it sabotages the two BUILDERS while leaving the
     * stamp reading the flag. */
    v.mrl_win = job->fit.prefilter && !pcrec_has_atomic(root)
                                   && !pcrec_has_lookaround(root);
    v.fmin    = 0;   /* nothing follows the whole pattern */

    pcrec_gen_names(cx, &g);
    memcpy(v.up, g.upper, sizeof v.up);

    /* THE REPORTED capture count, which `--no-captures` pins at 1 whatever
     * the slot layout holds (§6.3, and §10's measured row: `--no-captures
     * '(a)\1'` must still MATCH "aa" and must deliver no group offsets). */
    const int ncaps = cx->want_caps ? v.ngroups + 1 : 1;

    /* [DD-14 wave B+C] THE CALL GRAPH, AND THE NULLABILITY FIXPOINT THAT MUST
     * PRECEDE EVERY OTHER WALK.
     *
     * `cx->callgraph` is NULL for a call-free pattern, so `has_calls` is the
     * ONE flag every byte this module adds to an artifact is gated on — the
     * frame's two fields, `RX_PUSH`'s extra line, `RX_CALL`, the fail label's
     * line and the two resets. §9.1's identity claim is therefore structural.
     *
     * THE NULLABLE FIXPOINT RUNS FIRST because `vm_nullable` is consulted by
     * `vm_cost`, `vm_count_slots`, `vm_lifts` and the emitter itself, and its
     * `A_CALL` arm reads `u.call.nonnullable`. The polarity makes running late
     * a PERFORMANCE fault rather than a correctness one (an unset field reads
     * "nullable", which emits a guard that is never wrong), but running it
     * here makes the answer the real one.
     *
     * BOTTOM `false`, ITERATED UP (§2.6), which is the OPPOSITE direction from
     * `minw`'s and for the opposite reason: nullability's least fixpoint over
     * a cycle is "not nullable", and a round that finds a nullable path raises
     * it. `n` rounds suffice — each settles at least one more target — and the
     * extra round is asserted to change nothing rather than assumed to. */
    v.cg = cx->callgraph;
    v.has_calls = v.cg != NULL;
    v.nregion = pcrec_callgraph_ntargets(v.cg);
    if (v.has_calls) {
        const int nt = v.nregion;
        bool *nn = arena_alloc(&cx->arena, (size_t)nt * sizeof *nn);
        for (int i = 0; i < nt; i++) nn[i] = false;   /* == "nullable", the bottom */
        for (int round = 0; round <= nt; round++) {
            bool changed = false;
            vm_publish_nonnull(&v, root, nn);
            for (int i = 0; i < nt; i++)
                if (!nn[i] && !vm_nullable(pcrec_callgraph_body(v.cg, i))) {
                    nn[i] = true;
                    changed = true;
                }
            if (!changed) break;
            if (round == nt)
                ctx_fail(cx, 0, "internal error: the subroutine nullability "
                                "fixpoint did not settle in %d rounds", nt);
        }
        vm_publish_nonnull(&v, root, nn);

        v.rgn_lbl  = arena_alloc(&cx->arena, (size_t)nt * sizeof *v.rgn_lbl);
        v.rgn_exit = arena_alloc(&cx->arena, (size_t)nt * sizeof *v.rgn_exit);
        v.rgn_w    = arena_alloc(&cx->arena, (size_t)nt * sizeof *v.rgn_w);
        v.rgn_nw   = arena_alloc(&cx->arena, (size_t)nt * sizeof *v.rgn_nw);
        v.rgn_cost = arena_alloc(&cx->arena, (size_t)nt * sizeof *v.rgn_cost);
        for (int i = 0; i < nt; i++) { v.rgn_w[i] = NULL; v.rgn_nw[i] = 0; }
    }

    /* Slot counting first: RX_NSLOTS has to be known before the rx_run_state type
     * is emitted, and it must agree EXACTLY with what the emitter goes on to
     * assign — so the counter mirrors the emitter's own rung decisions rather
     * than approximating them. */
    vm_count_slots(&v, root, 1, false);
    /* [DD-14 wave B+C] AND ONE PASS PER EMITTED CALLEE REGION, IN ASCENDING
     * TARGET ORDER — design §4.4c's rule, and the order is what makes the
     * running counters and the emitter agree.
     *
     * §4.4c: "the layout accounts for EVERY EMITTED REGION — each lexical
     * occurrence as today, PLUS one for each emitted callee region — and `W`
     * is computed over the CALLEE REGION's own indices." Three separate facts
     * make a lexical-only count wrong, and the first is the one no reasoning
     * from the tree finds: `X{0}` EMITS NOTHING AND COUNTS NOTHING, and a
     * callee parked there is a REAL IDIOM (the classic pre-DEFINE spelling,
     * measured matching on 10.46 for plain, recursive, atomic and rung-bearing
     * callees), so the region the emitter must produce has slot instances that
     * NOTHING COUNTED. The failure is `vm_slot_mark(v, v->nmark++)` past
     * `RX_NSLOTS` — an out-of-bounds write in EMITTED code, K27's class, which
     * this function's own header names. S-SR19 is its detector and its cell
     * must carry a RUNG-BEARING or ATOMIC callee: a callee with only capture
     * slots allocates from a family `{0}` does not prune, so a plain cell goes
     * green on a broken layout.
     *
     * "DOUBLE-COUNTING" IS THE CORRECT COUNT. A called group's body is walked
     * twice — once at its lexical position, once as a region — because the
     * emitter emits it twice, as two programs with different exits (§3.5,
     * §6.3). The SNAPSHOTS taken around each region pass are what `W` is built
     * from: they are exactly the counter ranges that region consumed, which is
     * the only place the region's own indices exist. */
    VmSnap *snap_before = NULL, *snap_after = NULL;
    if (v.has_calls) {
        snap_before = arena_alloc(&cx->arena,
                                  (size_t)v.nregion * sizeof *snap_before);
        snap_after  = arena_alloc(&cx->arena,
                                  (size_t)v.nregion * sizeof *snap_after);
        for (int i = 0; i < v.nregion; i++) {
            snap_before[i] = vm_snap(&v);
            vm_count_slots(&v, pcrec_callgraph_body(v.cg, i), 1, false);
            snap_after[i] = vm_snap(&v);
        }
    }
    /* [M4.5c fix] REFUSE BEFORE EMITTING. PCREC_MAX_VM_NODES alone let
     * `((a)|b){0,4000}c` through at 3.5 MB (D45's own case); this is the
     * compiler-side bound that stops it, and it is checked here — after the
     * pre-pass, before a single byte of the matcher is written — because the
     * whole point is not to do the work. See limits.h for the measurement
     * behind the number and for why the cap is on REPLICATION rather than on
     * total emitted size. */
    if (v.maxcopies > PCREC_MAX_VM_REPEAT_COPIES)
        ctx_fail(cx, cx->first_cap_pos == (size_t)-1 ? 0 : cx->first_cap_pos,
                 /* Inside pcrec_error.msg's 256 bytes on purpose: a diagnostic
                  * that names the fix and is then truncated has not named it. */
                 "pattern too large: a bounded repeat would replicate its body "
                 "%lld times (limit %d). A body containing an alternation is "
                 "copied once per repetition -- lower the count, or remove the "
                 "alternation so the body compiles to a span loop instead",
                 v.maxcopies, PCREC_MAX_VM_REPEAT_COPIES);
    const int nguard_total = v.nguard, nlow_total = v.nlow;
    /* [ENG-BREP] possessive cut marks, and since [M6.4.2] atomic-group cut
     * marks too — one family, because they are the same operation with two
     * different licences (a proof, or the user writing the cut). */
    const int nmark_total = v.nmark;
    const int nctr_total  = v.nctr;    /* [ENG-BREP] counter loops, 1 slot each */
    const int nrev_total  = v.nrev;    /* [ENG-BREP] revdet loops, 3 slots each */
    /* [M6.6.2] the lookaround's two families — at most two per assertion and
     * sometimes one, decided per shape by `vm_look_needs_mark`/`_pos`, which
     * `vm_count_slots` and `vm_look` both read so they cannot disagree. */
    const int nlookmark_total = v.nlookmark;
    const int nlookpos_total  = v.nlookpos;
    v.nguard_total = nguard_total;
    v.nlow_total   = nlow_total;
    v.nmark_total  = nmark_total;
    v.nrev_total   = nrev_total;
    v.nctr_total   = nctr_total;
    v.nlookmark_total = nlookmark_total;
    v.nlookpos_total  = nlookpos_total;
    v.nguard = v.nlow = v.nmark = v.nrev = v.nctr = 0;
    v.nlookmark = v.nlookpos = 0;
    /* [M6.5.2] `2 * (ngroups + 1)`, not `2 * ncaps`: the capture-pair region
     * is sized by the SLOT LAYOUT, which under `--no-captures` can hold marked
     * groups the artifact reports none of. The two are equal on every
     * captures-on build and on every backref-free one, so no existing
     * artifact's `RX_NSLOTS` moves. The pending block sits on top — see
     * `vm_slot_pend` — so every base below it is unmoved as well. */
    const int nstate = 2 * (v.ngroups + 1) + nguard_total + nlow_total
                     + nmark_total + 3 * nrev_total + nctr_total
                     + v.npend_total + nlookmark_total + nlookpos_total;

    /* [DD-14 wave B+C] `W` PER REGION, THEN THE REGIONS' OWN COSTS — in that
     * order, because `vm_cost`'s call arm charges `2 * |W|` of trail and
     * cannot do so before `W` exists.
     *
     * The three families of member are collected in three different ways and
     * each way is forced by the layout: the CAPTURE slots by a walk (they are
     * indexed by GROUP NUMBER and are shared with the lexical occurrence), the
     * other seven families by the COUNTER RANGES this region's own
     * `vm_count_slots` pass consumed (they are per EMITTED COPY, so the ranges
     * are the only place the region's own indices exist), and the callees'
     * sets by the graph's TRANSITIVE relation.
     *
     * THE UNION IS TAKEN FROM THE UNMODIFIED SETS. `reaches` is already
     * transitive, so `W(i) = base(i) | union of base(j) over reaches(i, j)`
     * needs one pass — but only if the right-hand side reads the ORIGINAL
     * sets. OR-ing in place would make the result depend on iteration order,
     * which is the shape of bug that shows up on one pattern in a corpus. */
    if (v.has_calls) {
        const int nt = v.nregion;
        bool **base = arena_alloc(&cx->arena, (size_t)nt * sizeof *base);
        for (int i = 0; i < nt; i++) {
            base[i] = arena_alloc(&cx->arena, (size_t)nstate * sizeof **base);
            memset(base[i], 0, (size_t)nstate * sizeof **base);
            vm_w_caps(&v, pcrec_callgraph_body(v.cg, i), base[i], nstate);
            vm_w_range(base[i], nstate,
                       vm_slot_guard(&v, snap_before[i].guard),
                       vm_slot_guard(&v, snap_after[i].guard));
            vm_w_range(base[i], nstate,
                       vm_slot_low(&v, snap_before[i].low),
                       vm_slot_low(&v, snap_after[i].low));
            vm_w_range(base[i], nstate,
                       vm_slot_mark(&v, snap_before[i].mark),
                       vm_slot_mark(&v, snap_after[i].mark));
            vm_w_range(base[i], nstate,
                       vm_slot_rev(&v, snap_before[i].rev, 0),
                       vm_slot_rev(&v, snap_after[i].rev, 0));
            vm_w_range(base[i], nstate,
                       vm_slot_ctr(&v, snap_before[i].ctr),
                       vm_slot_ctr(&v, snap_after[i].ctr));
            vm_w_range(base[i], nstate,
                       vm_slot_lookmark(&v, snap_before[i].lookmark),
                       vm_slot_lookmark(&v, snap_after[i].lookmark));
            vm_w_range(base[i], nstate,
                       vm_slot_lookpos(&v, snap_before[i].lookpos),
                       vm_slot_lookpos(&v, snap_after[i].lookpos));
        }
        for (int i = 0; i < nt; i++) {
            bool *w = arena_alloc(&cx->arena, (size_t)nstate * sizeof *w);
            memcpy(w, base[i], (size_t)nstate * sizeof *w);
            for (int j = 0; j < nt; j++) {
                if (j == i || !pcrec_callgraph_reaches(v.cg, i, j)) continue;
                for (int k = 0; k < nstate; k++) if (base[j][k]) w[k] = true;
            }
            /* SLOTS 0 AND 1 ARE NEVER MEMBERS (§3.4(b)'s `\K` measurement).
             * Nothing above can put them there — the capture walk starts at
             * group 1 and no family's base reaches below `2*(ngroups+1)` — so
             * this is an ASSERTION written as a filter, and the filter is what
             * makes it one line rather than a paragraph nobody checks. */
            int n = 0;
            for (int k = 2; k < nstate; k++) if (w[k]) n++;
            int *lst = arena_alloc(&cx->arena, (size_t)(n ? n : 1) * sizeof *lst);
            int q = 0;
            for (int k = 2; k < nstate; k++) if (w[k]) lst[q++] = k;
            v.rgn_w[i]  = lst;
            v.rgn_nw[i] = n;
        }
        vm_publish_saves(&v, root);

        /* THE REGIONS' OWN COSTS, memoised so `vm_cost`'s `A_CALL` arm never
         * has to walk a callee — which for a recursive one is design §4.4's
         * non-terminating descent.
         *
         * A CYCLIC TARGET IS `unbounded` AND SETTLED FIRST, which is what
         * makes the rest a finite DAG evaluation: a recursion's depth is
         * data-dependent by nature, so P12's honest-ceiling machinery is
         * reused rather than a number invented. Everything else is evaluated
         * once its whole reachable set is settled, and `nt` rounds suffice
         * because each round settles at least one more target. */
        for (int i = 0; i < nt; i++)
            if (pcrec_callgraph_reaches(v.cg, i, i)) {
                Cost u = { 0, 0, 0, 0, true, true };
                v.rgn_cost[i] = u;
            }
        {
            bool *done = arena_alloc(&cx->arena, (size_t)nt * sizeof *done);
            for (int i = 0; i < nt; i++)
                done[i] = pcrec_callgraph_reaches(v.cg, i, i);
            for (int round = 0; round <= nt; round++) {
                bool changed = false, all = true;
                for (int i = 0; i < nt; i++) {
                    if (done[i]) continue;
                    bool ready = true;
                    for (int j = 0; j < nt; j++)
                        if (j != i && pcrec_callgraph_reaches(v.cg, i, j)
                                   && !done[j]) ready = false;
                    if (!ready) { all = false; continue; }
                    v.rgn_cost[i] =
                        vm_cost(&v, pcrec_callgraph_body(v.cg, i), false);
                    done[i] = true;
                    changed = true;
                }
                if (all) break;
                if (!changed)
                    ctx_fail(cx, 0, "internal error: the subroutine cost "
                                    "memo did not settle");
            }
        }
    }

    /* §2.5's two capacities. */
    Cost cost = vm_cost(&v, root, false);
    long long bt_frames, trail_frames, ceiling = 0;
    bool fits;
    if (cx->opt->frame_capacity > 0) {
        bt_frames = cx->opt->frame_capacity;
        trail_frames = cx->opt->frame_capacity;
    } else if (cost.unbounded) {
        bt_frames = VM_DEFAULT_RESUME_FRAMES;
        trail_frames = VM_DEFAULT_TRAIL_FRAMES;
    } else {
        bt_frames = cost.frames + 1;
        trail_frames = cost.trail + 1;
        if (bt_frames > VM_MAX_AUTO_RESUME_FRAMES) bt_frames = VM_MAX_AUTO_RESUME_FRAMES;
        if (trail_frames > VM_MAX_AUTO_TRAIL_FRAMES)
            trail_frames = VM_MAX_AUTO_TRAIL_FRAMES;
    }
    if (bt_frames < 1) bt_frames = 1;
    if (trail_frames < 1) trail_frames = 1;

    /* THE STAMP IS ABOUT WHAT THE ARTIFACT ENFORCES, NOT WHAT IT WANTED.
     * A ceiling is owed whenever the depth grows with the subject AND the
     * exact requirement does not fit the arrays actually emitted — which
     * covers the unbounded class (where no exact requirement exists) and the
     * large-bounded one (where it exists and is too big) with one rule. A
     * pattern whose requirement DOES fit has no limit to declare, and stamps
     * 0 truthfully. Getting this wrong in the other direction is what a
     * silent cap looks like: `((a)|b){0,4000}c` is statically bounded at 4000
     * frames, gets the VM_MAX_AUTO_RESUME_FRAMES clamp, and would otherwise have stamped "not applicable". */
    fits = !cost.unbounded && cost.frames + 1 <= bt_frames
                           && cost.trail + 1 <= trail_frames;
    if (cost.growable && !fits) {
        long long a = vm_ceiling(bt_frames, cost.pf);
        long long b = vm_ceiling(trail_frames, cost.pt);
        ceiling = (a && b) ? (a < b ? a : b) : (a ? a : b);
    }

    long long budget = cx->opt->step_budget;
    if (budget == PCREC_STEP_BUDGET_DEFAULT) budget = VM_DEFAULT_STEP_BUDGET;
    const bool has_budget = budget != PCREC_STEP_BUDGET_NONE;

    /* [ENG-BREP counter-K] The THIRD bound. ONE existence gate in v1 (D49):
     * `--fno-step-budget` suppresses BOTH counters, which is what keeps
     * tests/vm/run_vm_tests.sh:147-157's no-counter pin true exactly as
     * written. `--work-budget=N` is the independent VALUE knob, so the two are
     * separately tunable while they exist; splitting the gate later is purely
     * additive. */
    long long work_budget = cx->opt->work_budget;
    if (work_budget == PCREC_WORK_BUDGET_DEFAULT)
        work_budget = VM_DEFAULT_WORK_BUDGET;
    if (!has_budget) work_budget = PCREC_WORK_BUDGET_NONE;

    /* Set BEFORE the walk, and that is not incidental: the WORK charge sites
     * are emitted DURING vm_emit (at each cut, at each frameless scan
     * completion), unlike the fail label's step charge, which is written after
     * the walk and can simply read the local. */
    v.has_budget = has_budget;
    /* Always present (docs/spec/match_api.md §3.1 promises it unconditionally,
     * and tests/codegen's K27 fixture calls it directly); the A_BREF arm ORs
     * in whichever compare entries it actually emits. */
    v.enc_mask = PCREC_ENCE_NEXT_POS;

    /* Emit the program into the scratch buffer FIRST: the class pool, the
     * cursor-local's presence and the emitted-node count are all discovered
     * by emitting, and all three have to appear in text that precedes the
     * program. Assembling in this order is what keeps them from being
     * predicted by a second, drift-prone analysis. */
    {
        int rootentry = vm_label(&v);
        int acc = vm_label(&v);
        /* [DD-14 wave B+C] THE REGIONS' LABELS ARE ALLOCATED BEFORE THE MAIN
         * BODY IS WALKED, because a call site in the main body needs the
         * region's entry label to `goto`, and a region may call another region
         * (or itself) — so no emission order makes the labels available late.
         * The regions themselves are emitted AFTER the accept label, which is
         * where §6.3 puts them: one shared copy per DISTINCT called group,
         * reached only by `goto`, never fallen into. */
        for (int i = 0; i < v.nregion; i++) {
            v.rgn_lbl[i]  = vm_label(&v);
            v.rgn_exit[i] = vm_label(&v);
        }
        vm_emit(&v, rootentry, root, acc);
        /* THROUGH vm_lbl, not a direct sb_printf. This was the one place that
         * emitted a label by a second route, and it is exactly the drift
         * engine_m4.md S10 warns about: the label existed in the artifact and
         * not in the listing, so the listing described a program one label
         * short of the emitted one. Caught by
         * tests/codegen/run_ir_listing.sh's label-set check on its first run,
         * which is the argument for having written that check at all — the
         * "one call, one truth" property is structural only while there is
         * genuinely one call. */
        vm_lbl(&v, acc, "the pattern is complete");
        vm_ev(&v, VE_ACCEPT, 0, 0, NULL);
        sb_printf(v.b, "    goto %s_accept;\n", v.p);
        /* rootentry is label 0 by construction; the prologue jumps to it */

        /* [DD-14 wave B+C] THE SHARED CALLEE REGIONS (§6.3). Emitted in the
         * SAME ascending target order the slot pre-pass counted them in, which
         * is what keeps the running slot counters and `vm_count_slots`'
         * totals agreeing site for site. */
        for (int i = 0; i < v.nregion; i++) vm_region(&v, i);
    }

    /* BEFORE the prologue, which is where the declarations are written, and
     * AFTER the walk, which is where the need was discovered. */
    job->enc_mask = v.enc_mask;
    pcrec_emit_prologue(cx, &g, ncaps);

    /* §5.5's stamp. RETAINED alongside rx_info (D43.1 makes rx_info the
     * CANONICAL machine-readable record) because the two serve different
     * consumers and are therefore not redundant: rx_info is a .rodata symbol,
     * readable only by LINKING against the artifact or reading the compiled
     * binary, while these are preprocessor-visible at COMPILE time, which is
     * what a tests/codegen structural check or a build-time `#ifdef` needs.
     *
     * [AS-BUILT DEVIATION, REPORTED] §5.5 shows this stamp on every artifact;
     * it is emitted on VM artifacts ONLY. Emitting it on the DFA path too
     * would put a new line in output that §5.4's byte-identity gate compares,
     * forcing the gate to FILTER rather than compare whole files — and a
     * filtered gate is exactly the check-design failure this project has
     * recorded twice. rx_info.engine already carries the engine on both
     * artifacts, so nothing is lost but the compile-time visibility, which on
     * a DFA artifact has no consumer. */
    sb_printf(c, "/* Engine: vm (forced by: %s) */\n",
              job->fit.why ? job->fit.why : "--engine=vm");
    if (has_budget)
        sb_printf(c, "/* Step steps_left: %lld backtrack resumptions; backtrack "
                     "frames: %lld */\n", budget, bt_frames);
    else
        sb_printf(c, "/* Step steps_left: none (--fno-step-steps_left); backtrack "
                     "frames: %lld */\n", bt_frames);
    sb_printf(c, "#define %s_ENGINE \"vm\"\n", v.up);
    sb_puts(c, "#define ");
    sb_printf(c, "%s_ENGINE_WHY ", v.up);
    pcrec_emit_c_string_literal(c, job->fit.why ? job->fit.why : "--engine=vm",
                                strlen(job->fit.why ? job->fit.why : "--engine=vm"));
    sb_puts(c, "\n");
    /* [M4.6f] THE PREFILTER STAMP: D46's observability half for
     * select_engine.c's fit.prefilter, in the SAME PLACEMENT as
     * RX_ENGINE/RX_ENGINE_WHY immediately above and for the same reason -- a
     * per-prefix, preprocessor-visible macro, VM-artifacts-only (a DFA
     * artifact has no separate prefilter DECISION: its own scan-avoidance
     * memchr/bitmap prefilter, emit_dfa.c's unconditional `prefilter` local,
     * is an unrelated always-on optimization, not a selection point D46
     * governs).
     *
     * ARTIFACT-LEVEL, not per-quantifier -- select_engine.c decides
     * fit.prefilter ONCE per pattern, so this is a SCALAR string like
     * RX_ENGINE and RX_VM_PRUNE_CEILING rather than a bitmask like
     * RX_VM_RUNGS/RX_VM_STRATS/RX_VM_PRUNES: those are masks because the
     * rung/strategy/clamp is selected per A_REP and a scalar would lie on a
     * mixed artifact ([M4.5e]'s own corrected design note); there is no
     * per-quantifier axis here to mix.
     *
     * job->fit.prefilter is FINAL by the time this runs (this file's own
     * comment at the MRL ceiling site: "fit.prefilter is select_engine's
     * verdict and is final by now"), and it is the SAME value `prefn`
     * below is built from -- one flag, read twice, never a second
     * computation of it. It also carries D47.3's do-or-die: a request this
     * artifact could not honour would have REFUSED in select_engine.c before
     * emission ever started, so a build that reaches this line already
     * reflects whatever `-fprefilter`/`-fno-prefilter` asked for (or the
     * derived default when neither was passed). */
    sb_printf(c, "#define %s_VM_PREFILTER \"%s\"\n", v.up,
              job->fit.prefilter ? "hybrid" : "none");
    /* [D46] the RUNG STAMP: same PLACEMENT as RX_ENGINE/RX_ENGINE_WHY above
     * (a per-prefix, preprocessor-visible macro family, VM-artifacts-only
     * for the same §5.4 byte-identity reason the comment above states), but
     * a SUMMARY BITMASK rather than a scalar -- the rung is selected PER
     * QUANTIFIER BODY (vm_cursor_fits is consulted once per A_REP, at this
     * file's three real call sites), so a pattern with two quantified
     * bodies can and does mix rungs, and a scalar "the rung" would LIE on
     * that case. v.rungs is already final here: vm_emit's real walk (above,
     * in the scratch buffer) is the ONLY place vm_rung_mark() runs, so this
     * is the same per-quantifier selection the emitted C actually made, not
     * a second computation of it. The PER-QUANTIFIER detail (which A_REP
     * took which rung) is --emit-ir's RUNGS section, off the same
     * v->rungs-building VE_RUNG events; this macro is deliberately only the
     * summary a build-time #ifdef/grep can act on.
     *
     * [ABI-NS] (D60, 2026-08-18): the NAMED bit constants this OR'd value is
     * built from (PCREC_VM_RUNG_CURSOR/_FRAMES_BOUNDED/_FRAMES_UNBOUNDED/
     * _REVDET/_COUNTER) are pcrec-contract facts — which bit means which
     * rung is fixed and artifact-independent — and moved to the shared
     * PCREC_RX_ABI_H block (emit_dfa.c's emit_rx_abi_types), unprefixed and
     * emitted unconditionally on every artifact. Only the OR'd MASK below,
     * whose value genuinely varies per artifact, stays here per-prefix.
     * vm_rung_bit[] (this file) and the block's literal 0x1u/0x2u/... values
     * must agree — they are the same contract stated twice, and this file's
     * own array is what the mask below is built from.
     *
     * rx_info deliberately does NOT gain a member for this at [M4.5e]: the
     * struct's layout is the frozen M4 ABI (match_api_m4.md S5, D44.5's
     * "the layout below is FINAL" ruling), and adding a field is an abi-
     * version-bump event this close does not take on its own -- flagged for
     * the manager rather than done here. */
    sb_printf(c, "#define %s_VM_RUNGS 0x%xu\n", v.up, v.rungs);
    /* [ENG-BREP] the STRATEGY stamp, D46's observability half for the ladder's
     * first rung, in the same shape and the same place and for the same
     * reason: possessification is decided PER A_REP, so an artifact whose
     * quantifiers differ needs a mask.
     *
     * It also carries D47.3's do-or-die half. `-fno-possessify` denies the
     * rewrite, and the way a check knows the denial was honoured is that
     * PCREC_VM_STRAT_POSSESSIVE is absent from this value — not that the
     * flag was passed. A denied strategy appearing in a stamp is a hard test
     * failure, which is testable precisely because the stamp is built from
     * the same `vm_cuts()` answer the emitter acts on. [M6.4.2]: under
     * `-fno-possessify` a WRITTEN possessive still cuts — the flag denies the
     * REWRITE, never a construct the user spelled — so this bit is present on
     * such an artifact and its absence is the denial's own evidence only for
     * a pattern with no atomic construct in it.
     *
     * [ABI-NS] (D60): PCREC_VM_STRAT_POSSESSIVE/_BACKTRACKING are the same
     * class of pcrec-contract fact as the rung bits above, and moved to the
     * shared block the same way — see that comment. Only the OR'd MASK
     * below stays here. */
    sb_printf(c, "#define %s_VM_STRATS 0x%xu\n", v.up, v.strats);
    /* [M4.6d] the PRUNE stamp: the same shape and the same place as the two
     * above, plus one thing neither of them needs — the CEILING FORM, which
     * is a property of the ARTIFACT rather than of a quantifier and is
     * therefore a string beside the mask rather than a bit inside it.
     *
     * D51 ruling 2 (c) makes disclosing it an obligation rather than a
     * courtesy. `--engine=vm` disables the DFA prefilter, so its artifacts
     * fall back to the subject-end ceiling and KEEP the trailing-suffix curve
     * §9.1 measures — the pruning is sound either way and merely less tight,
     * and the difference has to be visible in the stamp rather than
     * discovered by measuring two artifacts against each other.
     *
     * [ABI-NS] (D60): PCREC_VM_PRUNE_CLAMPED/_UNCLAMPED moved to the shared
     * block for the same reason as the rung/strategy bits above; only the
     * OR'd MASK below stays here. */
    sb_printf(c, "#define %s_VM_PRUNES 0x%xu\n", v.up, v.prunes);
    /* The CEILING the artifact actually uses, and "none" when it uses none —
     * which is the same word whether the analysis produced nothing or was
     * DENIED. That identity is deliberate and load-bearing: `-fno-length-prune`
     * has to leave no trace on a pattern that carries no bound, or the
     * byte-identity property that makes the denied build the differential's
     * ground truth is destroyed by the stamp announcing the denial. It is the
     * same rule emit_dfa.c's strategy-denial mask states for `rx_info.flags`,
     * one stamp over. Where a bound DOES exist the stamp names its form, which
     * is what ruling 2 (c) asks for; where none exists there is no form to
     * name. */
    sb_printf(c, "#define %s_VM_PRUNE_CEILING \"%s\"\n", v.up,
              v.nclamp == 0 ? "none"
                            : v.mrl_win ? "prefilter-window" : "subject-end");
    if (v.tracing) {
        sb_puts(c,
            "/* TRACED ARTIFACT (--trace, DD-8/engine_m4.md S10): this matcher\n"
            " * prints every resume-frame push and pop, every capture write,\n"
            " * and its accept/fail to STDERR as it runs. It is a DEBUG build\n"
            " * and nothing else: it writes to stderr, it is not fast, and it\n"
            " * is never what a plain invocation produces. */\n");
        sb_puts(c, "#include <stdio.h>\n");
        sb_printf(c, "#define %s_TRACE 1\n", v.up);
    }
    sb_printf(c, "#define %s_NSLOTS %d\n", v.up, nstate < 1 ? 1 : nstate);

    /* [M6-READ] THE SLOT LEGEND, as macros resolving to the numbers they
     * replace. Requirement (5): these table numbers are IDENTITIES, not
     * indexes, and naming them is the single largest readability gain in a VM
     * artifact -- `RX_SET(2, ...)` becomes `RX_SET(RX_SLOT_GROUP1_START, ...)`.
     * Every name comes from vm_slot_name, i.e. from the layout arithmetic
     * itself, so it cannot disagree with where the emitter actually writes. */
    if (nstate > 0) {
        sb_puts(c, "\n/* SLOT LEGEND -- names for the numbered cells of the slot\n"
                   " * array. A capture group occupies a PAIR of slots, its start and\n"
                   " * its end. The whole-match pair is listed for completeness: the\n"
                   " * VM does not write it unless the pattern has a \\K, because the\n"
                   " * entry already knows where the attempt began. */\n");
        for (int sl = 0; sl < nstate; sl++) {
            char nm[48];
            if (!vm_slot_name(&v, sl, nm, sizeof nm)) continue;
            sb_printf(c, "#define %s_%-24s %d\n", v.up, nm, sl);
        }
        sb_putc(c, '\n');
    }
    sb_printf(c, "#define %s_RESUME_FRAMES %lld\n", v.up, bt_frames);
    sb_printf(c, "#define %s_TRAIL_FRAMES %lld\n", v.up, trail_frames);
    if (has_budget)
        sb_printf(c, "#define %s_STEP_BUDGET %lldLL\n", v.up, budget);
    if (work_budget != PCREC_WORK_BUDGET_NONE)
        sb_printf(c, "#define %s_WORK_BUDGET %lldLL\n", v.up, work_budget);
    sb_puts(c, "\n");

    /* ---- rx_run_state: the whole mutable working set, §2.2 ------------------
     * All locals — no globals (TS-1: usable FROM threads, all-const tables,
     * no mutable state outside the caller's own frame) and no allocation
     * (PC-5/D38's COPY_MATCHED_SUBJECT = NEVER precedent). */
    sb_printf(c,
        "/* Everything one match attempt can change, in one struct, so that no\n"
        " * state lives in globals and two attempts can never interfere.\n"
        " * Allocated by the caller on the stack; this file never allocates.\n"
        " *\n"
        " *   slot_values   the group boundaries recorded so far, by slot number\n"
        " *   resume_stack  alternatives not yet tried, most recent last; each\n"
        " *                 frame is \"if you get stuck, come back to HERE\"\n"
        " *   trail         an undo log of slot_values writes, so popping a\n"
        " *                 resume frame restores the groups exactly as they were\n"
        " *   *_depth       how many entries of each are currently live\n"
        " */\n"
        "typedef struct {\n"
        "    ptrdiff_t slot_values[%s_NSLOTS];\n"
        "    struct { const void *resume_label; size_t resume_position;\n"
        "             unsigned trail_mark;%s%s } resume_stack[%s_RESUME_FRAMES];\n"
        "    struct { unsigned slot_index; ptrdiff_t saved_value; }\n"
        "             trail[%s_TRAIL_FRAMES];\n"
        "    unsigned resume_depth, trail_depth;%s\n",
        v.up, v.tracing ? " int id;" : "",
        /* [DD-14 wave B+C] THE CALL RECORD IS THE RESUME FRAME (design §5.1),
         * and §5.2 is why it is a DERIVATION rather than a preference. The
         * obvious alternative — `const void *call_stack[N]` indexed by call
         * depth and POPPED at the return — has a bug that needs three events
         * to appear: A returns, its continuation calls B (overwriting A's
         * return label), B fails, the backtracker resumes inside A's callee,
         * and A's second return lands in B's continuation. The frame's depth
         * mark restores the DEPTH and cannot restore the CONTENTS. §5.9 BUILT
         * both and measured it: the array build is wrong on 3 of 50 cells, one
         * of them a FALSE MATCH, and agrees on the other 47 — which is what
         * localises the failure to the clobber sequence.
         *
         * A frame is never overwritten while it is live, so the structure
         * whose contents the backtracker already restores is the right home.
         *
         * `call_top` IS ON EVERY FRAME, NOT ONLY ON CALL FRAMES: it is what
         * the fail label restores, so an ORDINARY frame pushed inside a callee
         * has to carry which activation was current when it was pushed
         * (§5.5's drawn cell — the pop of an alternation frame is what lets the
         * SECOND `RX_RETURN` find the right label). It is a resume-stack INDEX
         * rather than a depth, so a nested activation's chain is a linked list
         * through frames that already exist.
         *
         * THERE IS NO `call_depth` AND NO `call_mark` (D71.1). The design's
         * §5.1 has three fields and a two-line fail label; the ruling keeps
         * the CODE `PCREC_ERR_RECURSE` as a reserved ABI fact and moves the
         * recursion-depth COUNTER to a [V-H] diagnostic generation axis, so
         * the default artifact's give-up for a deep call is
         * `PCREC_ERR_FRAMES` — calls consume ordinary frames, and the frame
         * capacity is the ceiling. Two fields, one line.
         *
         * EMITTED ONLY ON A CALL-BEARING ARTIFACT, which is what makes §9.1's
         * byte-identity claim structural: a call-free pattern's `rx_run_state`
         * is the one it has always had. */
        v.has_calls ? " const void *call_ret; unsigned call_top;" : "",
        v.up, v.up,
        v.has_calls ? "\n    unsigned call_top;   /* the CURRENT activation's"
                      " frame index, or CALL_TOP_NONE */" : "");
    if (has_budget) sb_puts(c, "    long long steps_left;   /* backtracks remaining */\n");
    if (work_budget != PCREC_WORK_BUDGET_NONE)
        sb_puts(c, "    long long work_left;    /* forward work units remaining */\n");
    sb_printf(c, "} %s_run_state;\n\n", v.p);

    /* The internal give-up sentinels. They share the search entry's public
     * PCREC_ERR_* values ([ABI-NS]/D60: unprefixed since those are
     * pcrec-contract facts, not per-artifact ones), but the sentinels
     * themselves are a different contract at a different layer (§4.4's
     * three layers: impl returns a private sentinel, the rx_matchfn export
     * collapses it to -1 per D38.4's frozen return space, and only
     * <prefix>_search — which D38 says nothing about — has room for the
     * honest code), so they get their own PER-PREFIX names. */
    sb_printf(c, "#define %s_R_STEPS   ((ptrdiff_t)PCREC_ERR_STEPS)\n", v.up);
    sb_printf(c, "#define %s_R_FRAMES  ((ptrdiff_t)PCREC_ERR_FRAMES)\n", v.up);
    sb_printf(c, "#define %s_R_WORK    ((ptrdiff_t)PCREC_ERR_WORK)\n", v.up);
    /* [DD-14 wave A] %s_R_RECURSE joins its three siblings, sentinel only:
     * D71 item 1 reserves the CODE now and defers the recursion-depth
     * COUNTER to a future [V-H] diagnostic axis, so no arm in this file
     * returns %s_R_RECURSE yet -- it exists so the search entry's collapse
     * (below) and every consumer of the sentinel family already agree on
     * its name before module 'recursion' supplies a producer. */
    sb_printf(c, "#define %s_R_RECURSE ((ptrdiff_t)PCREC_ERR_RECURSE)\n", v.up);
    /* [DD-14 wave A commit 2] %s_R_INTERNAL is NOT a give-up sentinel --
     * it names the below-the-floor abort code (PCREC_ERR_INTERNAL) through
     * the identical private-sentinel/public-code seam, because the seam's
     * reason (§4.4's three layers) is about WHERE a typed negative value
     * has room to travel, not about which side of the floor it lands on.
     * `vm_look_behind`'s negative-arm end-check is its one producer today. */
    sb_printf(c, "#define %s_R_INTERNAL ((ptrdiff_t)PCREC_ERR_INTERNAL)\n\n", v.up);
    /* [DD-14 wave B+C] "no subroutine call is active". Out of range for the
     * frame array on purpose, so a return with no live activation indexes
     * nothing — the region exit's own guard turns that into
     * `PCREC_ERR_INTERNAL` (D72) rather than K27's class in emitted code. */
    if (v.has_calls)
        sb_printf(c, "#define %s_CALL_TOP_NONE ((unsigned)-1)\n\n", v.up);

    /* [ENG-BREP counter-K] THE WORK CHARGE (D47 SECOND ADDENDUM settlement 4).
     *
     * It TESTS as well as decrements, which is a decision with a cost and is
     * made deliberately: an untested decrement means a loop that SUCCEEDS can
     * overrun the bound by orders of magnitude and still return a match, which
     * is the exact DD-2 failure mode a bound exists to prevent. A budget
     * consulted only where it was already consulted is not a budget. The price
     * is that the emitter's former one-charge-site invariant is gone and a
     * give-up can now return from inside a loop body.
     *
     * The `> 0` guard is not defensive noise. It skips the whole operation for
     * the zero-work cut that is the common case, and it makes a hypothetically
     * inverted count (which would be a real bug elsewhere) unable to REFUND
     * budget, which is the one failure mode that would silently disarm the
     * bound rather than merely mis-size it. */
    if (work_budget != PCREC_WORK_BUDGET_NONE) {
        sb_printf(c,
            "/* Charge forward work the backtracker never sees. A scan that\n"
            " * races over a megabyte costs no STEPS -- it never backtracks --\n"
            " * so without this meter a slow attempt would look costless. */\n"
            "#define %s_CHARGE_WORK(n_) do {                                    \\\n"
            "        ptrdiff_t nw_ = (ptrdiff_t)(n_);                     \\\n"
            "        if (nw_ > 0) {                                       \\\n"
            "            run->work_left -= (long long)nw_;                       \\\n"
            "            if (run->work_left < 0) return %s_R_WORK;               \\\n"
            "        }                                                    \\\n"
            "    } while (0)\n\n",
            v.up, v.up);
    }

    /* [M4.6d] THE TWO MRL FORMS, as macros rather than inline expressions.
     * Two reasons, and the second is the one that matters: the emitted C is
     * smaller (the design measured +3.2% with the expressions written out at
     * every site), and a structural check has ONE token to look for when it
     * asks whether the optimization is present in an artifact.
     *
     * `<prefix>_ceil` is the match function's ceiling parameter (see its
     * definition below) and `p_` the position under test. `MRL_CAP` is
     * defined only where `MRL_SHORT` is false: it subtracts, so its result is
     * meaningful exactly where the guard has already established that the
     * subtraction does not underflow. Every call site pairs them.
     *
     * THE ROUNDING IS THE WHOLE OF `MRL_CAP`. `w_` is the cursor's stride, so
     * the integer division floors the cap onto `p_ + w_*k` — a position the
     * span loop can actually occupy. Without it the cap lands between two
     * iteration boundaries and poisons the entire retreat chain below it,
     * which R26 E1 measured as 5 of 8 subjects answered `nomatch` where both
     * pcrec-unpruned and python match. At `w_ == 1` the division is the
     * identity and gcc removes it. */
    /* The ceiling parameter's spelling, written once: the declaration, the
     * definition and the three call sites all read these two strings rather
     * than re-deriving the name, so a rename cannot leave one of them behind. */
    char mrl_param[96];
    snprintf(mrl_param, sizeof mrl_param, ", const size_t %s_window_end", v.p);
    /* [M6.2 wave D] `\G`'s parameter, written once for the same reason and
     * appended AFTER the ceiling's so the two are order-independent at every
     * site: each is emitted or omitted on its own flag, and a program with
     * both gets `(ctx, w, ceil, startpos)`. */
    char gst_param[96];
    snprintf(gst_param, sizeof gst_param, ", const size_t %s_search_from", v.p);

    if (v.nclamp > 0) {
        sb_printf(c,
            "/* MINIMUM-REMAINING-LENGTH pruning. At each point the compiler\n"
            " * knows the fewest bytes any successful continuation must still\n"
            " * consume. If fewer than that remain before the window ends, this\n"
            " * position cannot lead to a match and the program fails now\n"
            " * instead of exploring from it. _CLAMP_SPAN is the same fact used\n"
            " * to SHORTEN a scan rather than abandon it, rounded down to a\n"
            " * whole number of iterations so the cursor stays on a position\n"
            " * the loop could actually have stopped at. */\n"
            "#define %s_PRUNE_TOO_SHORT(p_, mr_) \\\n"
            "    ((%s_window_end) < (size_t)(mr_) || (%s_window_end) - (size_t)(mr_) < (p_))\n"
            "#define %s_PRUNE_CLAMP_SPAN(p_, mr_, w_) \\\n"
            "    ((p_) + (size_t)(w_) * (((%s_window_end) - (size_t)(mr_) - (p_)) / (size_t)(w_)))\n\n",
            v.up, v.p, v.p, v.up, v.p);
    }

    if (!v.tracing) {
        sb_printf(c,
            "#define %s_TRAIL(slot_) do {                                  \\\n"
            "        if (run->trail_depth >= %s_TRAIL_FRAMES) return %s_R_FRAMES;    \\\n"
            "        run->trail[run->trail_depth].slot_index = (unsigned)(slot_);               \\\n"
            "        run->trail[run->trail_depth].saved_value = slot_values[(slot_)];                       \\\n"
            "        run->trail_depth++;                                             \\\n"
            "    } while (0)\n"
            "#define %s_SET(slot_, v_) do {                                \\\n"
            "        %s_TRAIL(slot_); slot_values[(slot_)] = (v_);                 \\\n"
            "    } while (0)\n"
            "#define %s_PUSH(lbl_, p_) do {                                \\\n"
            "        if (run->resume_depth >= %s_RESUME_FRAMES) return %s_R_FRAMES;       \\\n"
            "        run->resume_stack[run->resume_depth].resume_label = (lbl_);                             \\\n"
            "        run->resume_stack[run->resume_depth].resume_position = (p_);                             \\\n"
            "        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth;                          \\\n"
            "%s"
            "        run->resume_depth++;                                             \\\n"
            "    } while (0)\n"
            /* [ENG-BREP] the possessive CUT. No trail rewind, deliberately —
             * see vm_cut()'s comment: the frames are dead, the capture writes
             * they would have rewound are not. */
            "#define %s_CUT(slot_) do {                                   \\\n"
            "        run->resume_depth = (unsigned)slot_values[(slot_)];                      \\\n"
            "    } while (0)\n\n",
            v.up, v.up, v.up, v.up, v.up, v.up, v.up, v.up,
            v.has_calls ? "        run->resume_stack[run->resume_depth]"
                          ".call_top = run->call_top;                      \\\n"
                        : "",
            v.up);
    } else {
        /* The traced forms. Same mechanism, same order of operations, one
         * fprintf each — deliberately NOT a separate implementation: a traced
         * run that took a different path from the untraced one would be a
         * debugging tool that lies, which is worse than none. */
        sb_printf(c,
            "#define %s_TRAIL(slot_) do {                                  \\\n"
            "        if (run->trail_depth >= %s_TRAIL_FRAMES) return %s_R_FRAMES;    \\\n"
            "        run->trail[run->trail_depth].slot_index = (unsigned)(slot_);               \\\n"
            "        run->trail[run->trail_depth].saved_value = slot_values[(slot_)];                       \\\n"
            "        run->trail_depth++;                                             \\\n"
            "    } while (0)\n"
            "#define %s_SET(slot_, v_) do {                                \\\n"
            "        fprintf(stderr, \"[%s] set   slot_values[%%d] %%td -> %%td\\n\",  \\\n"
            "                (int)(slot_), slot_values[(slot_)], (ptrdiff_t)(v_));  \\\n"
            "        %s_TRAIL(slot_); slot_values[(slot_)] = (v_);                 \\\n"
            "    } while (0)\n"
            "#define %s_PUSH(id_, lbl_, p_) do {                           \\\n"
            "        if (run->resume_depth >= %s_RESUME_FRAMES) return %s_R_FRAMES;       \\\n"
            "        run->resume_stack[run->resume_depth].resume_label = (lbl_);                             \\\n"
            "        run->resume_stack[run->resume_depth].resume_position = (p_);                             \\\n"
            "        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth;                          \\\n"
            "%s"
            "        run->resume_stack[run->resume_depth].id = (id_);                             \\\n"
            "        fprintf(stderr, \"[%s] push  #%%u resume L%%d at scan_position %%zu"
                        " (trail %%u)\\n\",                                 \\\n"
            "                run->resume_depth, (id_), (size_t)(p_), run->trail_depth);         \\\n"
            "        run->resume_depth++;                                             \\\n"
            "    } while (0)\n"
            "#define %s_CUT(slot_) do {                                   \\\n"
            "        fprintf(stderr, \"[%s] cut   %%u -> %%td frame(subject)\\n\",   \\\n"
            "                run->resume_depth, slot_values[(slot_)]);                        \\\n"
            "        run->resume_depth = (unsigned)slot_values[(slot_)];                      \\\n"
            "    } while (0)\n\n",
            v.up, v.up, v.up, v.up, v.p, v.up, v.up, v.up, v.up,
            v.has_calls ? "        run->resume_stack[run->resume_depth]"
                          ".call_top = run->call_top;                      \\\n"
                        : "",
            v.p, v.up, v.p);
    }

    /* [DD-14 wave B+C] `RX_CALL` — `RX_PUSH` with a RETURN LABEL and one more
     * line (design §5.1). Emitted only on a call-bearing artifact.
     *
     * A CALL FRAME'S `resume_label` IS THE FAIL LABEL ITSELF, and that is not
     * a placeholder: when the frames inside a call are exhausted the call has
     * no alternatives of its own, so popping it must continue failing. Making
     * it `&&<prefix>_fail` means the fail label needs NO knowledge of frame
     * kinds and no branch — its one added line runs for every frame and is
     * correct for both. The cost is one extra backtrack step per abandoned
     * call, charged where the budget is already charged; §3.2 MEASURED PCRE2
     * doing TWICE the backtracks of an inlined control over 1..8 call sites,
     * which is the same order of overhead.
     *
     * THE FRAME IS NOT POPPED BY THE RETURN (§5.1), which is the whole point:
     * §3.2 measured the call BACKTRACKABLE, so the callee's choice points must
     * survive the return and so must the label they will come back through.
     *
     * ONE CAPACITY TEST, NOT TWO (D71.1). The design's §5.6 has a second
     * counter against `RX_CALL_DEPTH` answering `PCREC_ERR_RECURSE`; the
     * ruling keeps the CODE reserved and moves the COUNTER to a diagnostic
     * generation axis, so a deep call exhausts the ordinary frame capacity and
     * answers `PCREC_ERR_FRAMES`. "Rebuild with the diagnostic axis to learn
     * which bound" is the documented story. */
    if (v.has_calls) {
        if (!v.tracing)
            sb_printf(c,
                "/* A subroutine call: a resume frame that also carries the\n"
                " * label to come back to. It is NOT popped by the return --\n"
                " * the callee's choice points stay live across it, so a later\n"
                " * failure can retreat back INTO the call. */\n"
                "#define %s_CALL(ret_, p_) do {                               \\\n"
                "        if (run->resume_depth >= %s_RESUME_FRAMES) return %s_R_FRAMES; \\\n"
                "        run->resume_stack[run->resume_depth].resume_label = &&%s_fail;   \\\n"
                "        run->resume_stack[run->resume_depth].resume_position = (p_);     \\\n"
                "        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth; \\\n"
                "        run->resume_stack[run->resume_depth].call_top = run->call_top;   \\\n"
                "        run->resume_stack[run->resume_depth].call_ret = (ret_);          \\\n"
                "        run->call_top = run->resume_depth;                               \\\n"
                "        run->resume_depth++;                                             \\\n"
                "    } while (0)\n\n",
                v.up, v.up, v.up, v.p);
        else
            sb_printf(c,
                "#define %s_CALL(ret_, p_) do {                               \\\n"
                "        if (run->resume_depth >= %s_RESUME_FRAMES) return %s_R_FRAMES; \\\n"
                "        run->resume_stack[run->resume_depth].resume_label = &&%s_fail;   \\\n"
                "        run->resume_stack[run->resume_depth].resume_position = (p_);     \\\n"
                "        run->resume_stack[run->resume_depth].trail_mark = run->trail_depth; \\\n"
                "        run->resume_stack[run->resume_depth].call_top = run->call_top;   \\\n"
                "        run->resume_stack[run->resume_depth].call_ret = (ret_);          \\\n"
                "        run->resume_stack[run->resume_depth].id = -1;                    \\\n"
                "        fprintf(stderr, \"[%s] call  #%%u at scan_position %%zu"
                            " (trail %%u)\\n\",                              \\\n"
                "                run->resume_depth, (size_t)(p_), run->trail_depth);      \\\n"
                "        run->call_top = run->resume_depth;                               \\\n"
                "        run->resume_depth++;                                             \\\n"
                "    } while (0)\n\n",
                v.up, v.up, v.up, v.p, v.p);
    }

    /* The per-search reset (§2.4): slot_values is initialised to UNSET ONCE per
     * SEARCH call, not per start position. On a failed attempt the trail
     * rewind to mark 0 restores every slot the attempt wrote back to UNSET by
     * construction, so the per-attempt reset is O(writes-since-attempt-start)
     * rather than O(NG) — which matters for the VM-only per-start loop, where
     * a naive memset per start position would be O(NG*n). */
    sb_printf(c,
        "/* Start a fresh attempt: every group unset, nothing to undo, both\n"
        " * budgets full. */\n"
        "static void %s_run_state_init(%s_run_state *run)\n"
        "{\n"
        "    int i;\n"
        "    for (i = 0; i < %s_NSLOTS; i++) run->slot_values[i] = PCREC_UNSET;\n"
        "    run->resume_depth = 0; run->trail_depth = 0;\n",
        v.p, v.p, v.up);
    /* [DD-14 wave B+C] §5.6 site 5a — NOT an `ERR_FLOOR` site but a MISSING
     * INITIALISER, and R34's LENS2-7 found it by noticing the design's own
     * prototype set the sentinel BY HAND in `main()`, which is exactly the
     * kind of scaffolding a prototype hides behind. Without it the very first
     * return of a search reads `resume_stack[garbage]`. */
    if (v.has_calls)
        sb_printf(c, "    run->call_top = %s_CALL_TOP_NONE;\n", v.up);
    if (has_budget) sb_printf(c, "    run->steps_left = %s_STEP_BUDGET;\n", v.up);
    if (work_budget != PCREC_WORK_BUDGET_NONE)
        sb_printf(c, "    run->work_left = %s_WORK_BUDGET;\n", v.up);
    sb_puts(c, "}\n\n");

    /* [DD-14 wave B+C] §5.6 site 5b — the per-START-POSITION reset. It rewinds
     * the trail and zeroes `resume_depth` WITHOUT resetting the budgets,
     * deliberately (a bump-along must not buy itself a fresh allowance);
     * `call_top` joins the FIRST group, not the second, because an attempt at
     * the next start position must not inherit the previous attempt's
     * activation. */
    char reset_call_top[160];
    reset_call_top[0] = 0;
    if (v.has_calls)
        snprintf(reset_call_top, sizeof reset_call_top,
                 "    run->call_top = %s_CALL_TOP_NONE;\n", v.up);

    sb_printf(c,
        "/* Roll the run state back to as-if-untouched WITHOUT resetting the\n"
        " * budgets, so retrying at the next starting position cannot buy\n"
        " * itself a fresh allowance. */\n"
        "static void %s_reset_for_next_attempt(%s_run_state *run)\n"
        "{\n"
        "    while (run->trail_depth) { run->trail_depth--; run->slot_values[run->trail[run->trail_depth].slot_index] = run->trail[run->trail_depth].saved_value; }\n"
        "    run->resume_depth = 0;\n"
        "%s"
        "}\n\n",
        v.p, v.p, reset_call_top);

    /* ---- the class bitmaps ------------------------------------------------
     * File-scope `static const` (TS-1: all-const tables, no mutable globals),
     * named under --prefix like every other file-scope symbol this project
     * emits, and only for classes that actually needed a bitmap — singletons
     * and contiguous ranges compile to a compare and never reach the pool. */
    {
        bool any = false;
        for (int i = 0; i < v.ncls; i++) {
            int lo = -1, hi = -1, count = 0;
            for (int cb = 0; cb < 256; cb++)
                if (cls_has(v.cls[i], (unsigned)cb)) {
                    if (lo < 0) lo = cb;
                    hi = cb;
                    count++;
                }
            if (count == 256 || count == 1 || count == hi - lo + 1) continue;
            any = true;
            sb_printf(c, "static const unsigned char %s_class_bitmap%d[32] = {", v.p, i);
            for (int j = 0; j < 32; j++) {
                if (j % 8 == 0) sb_puts(c, "\n   ");
                sb_printf(c, " %3d,", v.cls[i][j]);
            }
            sb_puts(c, "\n};\n");
        }
        if (any) sb_puts(c, "\n");
    }

    /* ---- the prefilter (§6.1, §4.7) ------------------------------------ */
    const char *prefn = NULL;
    if (job->fit.prefilter) {
        size_t sz = strlen(v.p) + sizeof("_prefilter");
        char *pf = arena_alloc(&cx->arena, sz);
        snprintf(pf, sz, "%s_prefilter", v.p);
        prefn = pf;
        sb_puts(c,
            "/* The capture-erased forward+reverse DFA pair, emitted by the\n"
            " * SAME emitter the DFA-only artifact uses (src/gen/emit_dfa.c),\n"
            " * under a private name. It is not an over-approximation: D31\n"
            " * erases the group at parse time and A_CAP is invisible to the\n"
            " * NFA builder, so this IS the machine the capture-erased pattern\n"
            " * compiles to (engine_m4.md 6.1, STRUCTURAL). It hands the VM an\n"
            " * anchored window so the VM never scans the subject, which is not\n"
            " * an optimization but the guard on a measured cliff: bench case\n"
            " * (e) is 25.4 GB/subject on pcrec today against pcre2-interp's DNF>90s,\n"
            " * and adding two parentheses must not move pcrec onto the DNF\n"
            " * side. Prefilter-before-VM is therefore an ORDERING RULE (4.7),\n"
            " * not a tuning knob: a pattern whose prefilter can answer must\n"
            " * never reach the step budget. */\n");
        pcrec_emit_dfa_engine(cx, prefn, "static ");
        sb_puts(c, "\n");
    }

    /* ---- rx_match_anchored: the program ------------------------------------ */
    /* [M4.6d] THE MRL CEILING IS A PARAMETER, not a member of `<prefix>_work`
     * as k23_design.md §9.1's sketch had it. The design's obligation (a) is
     * that an entry which runs NO prefilter must default the ceiling to the
     * subject end "or the clamp reads a stale window" — and the way to
     * discharge an obligation of the form "every caller must remember to set
     * X" is to make forgetting a compile error. A parameter does that; a
     * struct member initialised at three call sites does not.
     *
     * It is emitted ONLY where the program contains an MRL bound, so an
     * artifact with no clamp keeps the signature it had before MRL existed
     * and stays byte-identical. */
    sb_printf(c,
        "static ptrdiff_t %s_match_anchored(const rx_ctx *ctx, %s_run_state *run%s%s)\n"
        "{\n"
        "    const unsigned char *const subject = ctx->subject;\n"
        "    const size_t subject_length = ctx->len;\n"
        "    size_t scan_position = ctx->pos;\n"
        "    ptrdiff_t *const slot_values = run->slot_values;\n",
        v.p, v.p,
        v.nclamp > 0 ? mrl_param : "",
        v.ngst > 0 ? gst_param : "");
    if (v.rungs & vm_rung_bit[VM_RUNG_CURSOR])
        sb_printf(c, "    size_t %s_span_cursor = 0;   /* the span-loop cursor (engine_m4.md 2.5):\n"
                     "                             a plain local, UNTRAILED, whose save\n"
                     "                             point is a resume frame */\n",
                  v.p);
    /* [ENG-BREP] the reverse-deterministic rung's working locals. All UNTRAILED
     * and all read only where they are provably live: `it`/`mk` inside the
     * forward scan, `c`/`prev`/`ns` inside one commit's own backward walk. What
     * has to survive a backtrack lives in slot_values (the three slots per loop) or in
     * the resume frame's recorded position, which is where the retreat target
     * rides.
     *
     * The capture-recovery arrays are SHARED across every revdet loop in the
     * program and sized by the widest body, because a walk's results are
     * published into slot_values before control leaves the loop that ran it — nothing
     * here outlives its own commit. */
    for (int i = 0; i < nrev_total; i++)
        sb_printf(c,
            /* [M6-READ] These suffixes MUST match the ones the use sites
             * NAMES (M6-READ): `cursor` is the walk cursor; `groups_seen`
             * is the count the walk has witnessed, tested against the group
             * count at the wstep label (`if (groups_seen >= ng)`);
             * `revdet_group_span[j][2]` is the span the backward walk
             * recovered for group j and `revdet_group_seen[j]` whether it has
             * been witnessed. Read off THIS file's own emission sites (the
             * `ga`/`gs`/`ns` locals and the "no group to witness" note),
             * which is where the rung's vocabulary actually lives.
             *
             * These suffixes MUST match the ones the use sites
             * compose with `%s_<suffix>` from the `rv` base -- they are the
             * same variable, spelled in two places. The rename moved the uses
             * and left the declarations, and a revdet artifact stopped
             * compiling; the two-artifact altcls differential caught it. */
            "    size_t %s_rv%d_cursor = 0; unsigned long %s_rv%d_iteration = 0;\n"
            "    unsigned %s_rv%d_frame_mark = 0; ptrdiff_t %s_rv%d_prev_position = -1;\n"
            "    int %s_rv%d_groups_seen = 0;\n",
            v.p, i, v.p, i, v.p, i, v.p, i, v.p, i);
    if (nrev_total && v.nrevcaps) {
        sb_printf(c, "    ptrdiff_t %s_revdet_group_span[%d][2] = {{0}};\n", v.p, v.nrevcaps);
        sb_printf(c, "    unsigned char %s_revdet_group_seen[%d] = {0};\n", v.p, v.nrevcaps);
    }
    sb_puts(c, "    (void)subject; (void)subject_length; (void)slot_values;\n");
    /* Three of the five per-loop locals are used only by shapes that do not
     * always occur — the walk cursor and `prev` exist only when a walk is
     * emitted, and the seen-counter only when the body has groups — and the
     * generated matcher is built -Wall -Wextra -Werror. `--no-captures` on a
     * possessified rung loop is the combination that has none of them, and it
     * failed -Wunused-variable before this line. `it` and `mk` are used by every
     * shape and are deliberately not listed, so a future shape that stops using
     * one still gets caught. */
    for (int i = 0; i < nrev_total; i++)
        sb_printf(c, "    (void)%s_rv%d_cursor; (void)%s_rv%d_prev_position; (void)%s_rv%d_groups_seen;\n",
                  v.p, i, v.p, i, v.p, i);
    if (v.tracing)
        sb_printf(c, "    fprintf(stderr, \"[%s] enter at scan_position %%zu of %%zu\\n\","
                     " scan_position, subject_length);\n", v.p);
    sb_printf(c, "    goto %s_L0;\n\n", v.p);
    sb_puts(c, v.b->p ? v.b->p : "");
    /* The three trace lines. Built here rather than inline so the untraced
     * artifact's text is the SAME format string with three empty inserts —
     * one emitted shape, not two, for the same reason the traced macros above
     * keep the untraced order of operations: a debug build that took a
     * different path would be a tool that lies. */
    /* [M6-READ] Widened: the renamed emitted locals (pos -> scan_position,
     * w -> run, b_ -> frame_index) made every one of these trace strings
     * longer, and snprintf TRUNCATES rather than failing. gcc's
     * -Wformat-truncation caught two of the three; the third is widened with
     * them because a silently cut trace line is a debugging tool that lies. */
    char accept_tr[288], fail_tr[288], exhaust_tr[192];
    accept_tr[0] = fail_tr[0] = exhaust_tr[0] = 0;
    if (v.tracing) {
        /* [M6.2 wave E] ON A `\K` ARTIFACT THIS LINE SAYS BOTH SPANS, because
         * on such an artifact they are different and one of them alone is
         * misleading. `[ctx->pos, pos)` is what the PROGRAM consumed, which is
         * what a trace of the program should say; the REPORTED span starts at
         * the last crossed `\K`, and a reader watching `(?:a\K)*ab` retreat
         * would otherwise see "ACCEPT [0,4)" and the caller print "2 4" with
         * nothing connecting them. Emitted only where a `\K` exists, so a
         * `\K`-free traced artifact keeps its line byte for byte. */
        if (v.nkreset > 0)
            snprintf(accept_tr, sizeof accept_tr,
                     "    fprintf(stderr, \"[%s] ACCEPT consumed [%%zu,%%zu)"
                     " reported [%%td,%%zu)\\n\", ctx->pos, scan_position,"
                     " slot_values[0] != PCREC_UNSET ? slot_values[0] : (ptrdiff_t)ctx->pos,"
                     " scan_position);\n", v.p);
        else
            snprintf(accept_tr, sizeof accept_tr,
                     "    fprintf(stderr, \"[%s] ACCEPT [%%zu,%%zu)\\n\","
                     " ctx->pos, scan_position);\n", v.p);
        snprintf(fail_tr, sizeof fail_tr,
                 "    fprintf(stderr, \"[%s] backtrack: %%u frame(subject), trail %%u\\n\","
                 " run->resume_depth, run->trail_depth);\n", v.p);
        /* A separate guarded statement rather than a brace around the
         * existing one: that keeps the UNTRACED artifact's bytes identical
         * (the insert is simply empty), which is what run_vm_identity.sh's
         * gate cares about and what a debug flag has no business changing. */
        snprintf(exhaust_tr, sizeof exhaust_tr,
                 "    if (run->resume_depth == 0)\n"
                 "        fprintf(stderr, \"[%s] FAIL: resume stack empty\\n\");\n",
                 v.p);
    }
    sb_printf(c,
        "\n%s_accept: __attribute__((unused));\n"
        "    /* 3.1: leftmost-first is FIRST COMPLETE MATCH WINS, not compare\n"
        "     * candidates. The VM returns here immediately and the capture\n"
        "     * slots at this instant are the answer — no candidate comparison,\n"
        "     * no longest-wins, no second pass. The caller's capture_spans array is\n"
        "     * filled by the ENTRY, not here (3.4). */\n"
        "%s"
        "    return (ptrdiff_t)(scan_position - ctx->pos);\n"
        "\n%s_fail: __attribute__((unused));\n"
        "    /* THE ONLY BACKTRACKER AND THE ONLY INDIRECT JUMP.\n"
        "     * A step is one backtrack resumption (4.2), counted at exactly\n"
        "     * this place — so forward progress is FREE (a linear match over\n"
        "     * 100 MB costs zero steps), the steps_left is subject-length-\n"
        "     * independent, and the counter measures precisely the thing it is\n"
        "     * meant to bound. D22: DD-2 is ROBUSTNESS, not a security\n"
        "     * boundary, and it must not be traded against execution speed. */\n"
        "%s%s"
        "    if (run->resume_depth == 0) return -1;\n",
        v.p, accept_tr, v.p, fail_tr, exhaust_tr);
    if (has_budget)
        sb_printf(c, "    if (--run->steps_left < 0) return %s_R_STEPS;\n", v.up);
    {
        char pop_tr[352];
        pop_tr[0] = 0;
        if (v.tracing)
            snprintf(pop_tr, sizeof pop_tr,
                     "        fprintf(stderr, \"[%s] pop   #%%u resume L%%d at"
                     " scan_position %%zu (rewind trail %%u -> %%u)\\n\",\n"
                     "                frame_index, run->resume_stack[frame_index].id, scan_position, run->trail_depth,"
                     " run->resume_stack[frame_index].trail_mark);\n", v.p);
        sb_printf(c,
            "    {\n"
            "        const unsigned frame_index = --run->resume_depth;\n"
            "        scan_position = run->resume_stack[frame_index].resume_position;\n"
            "%s"
            "%s", pop_tr,
            /* [DD-14 wave B+C] §5.5's ONE ADDED LINE, and it restores WHICH
             * ACTIVATION IS CURRENT — exactly as the line above it restores
             * `scan_position` and the loop below it rewinds the trail.
             *
             * IT RUNS FOR EVERY FRAME AND NEEDS NO BRANCH, which is what a
             * call frame's `resume_label` being the fail label itself buys
             * (see `RX_CALL`): the fail label needs no knowledge of frame
             * kinds, so this is a line rather than a test.
             *
             * §5.5's DRAWN CELL IS WHY IT IS NOT OPTIONAL, and this lane
             * REPRODUCED it before adding the line: on `^(a(?1)?b)$` / "aaabbb"
             * the retreat pops the innermost call frame and then an ordinary
             * alternation frame INSIDE the enclosing activation, and without
             * this restore `call_top` still names the POPPED call frame — so
             * the enclosing activation's return reads `trail_mark` one level
             * too deep and restores the wrong values. Measured on the traced
             * artifact: group 1 came back (2,5) where it must be (1,5), one
             * level off at every depth, and the whole match was lost.
             *
             * THE DESIGN CALLS THIS "the fail label's TWO lines" (§5.1/§5.5).
             * Under D71.1 the second — `call_depth = resume_stack[..].call_mark`
             * — does not exist in the default artifact at all, because the
             * recursion-depth COUNTER moved to a diagnostic generation axis
             * and calls consume ordinary frames. S-SR2 names THIS line, which
             * §9.3 already records as the one whose deletion changes answers;
             * S-SR2a, the other line's row, moves to that axis with it.
             *
             * EMITTED ONLY ON A CALL-BEARING ARTIFACT — §9.1's byte-identity
             * claim, held by construction rather than by a filtered diff. */
            v.has_calls
              ? "        run->call_top = run->resume_stack[frame_index]"
                ".call_top;\n"
              : "");
    }
    sb_puts(c,
        "        while (run->trail_depth > run->resume_stack[frame_index].trail_mark) {\n"
        "            run->trail_depth--;\n"
        "            slot_values[run->trail[run->trail_depth].slot_index] = run->trail[run->trail_depth].saved_value;\n"
        "        }\n"
        "        goto *run->resume_stack[frame_index].resume_label;\n"
        "    }\n"
        "}\n\n");

    sb_printf(c, "#undef %s_TRAIL\n#undef %s_SET\n#undef %s_PUSH\n\n",
              v.up, v.up, v.up);

    /* ---- the caps copy-out (§3.4) --------------------------------------
     * The VM's working slots are LOCAL and the ENTRY copies the capture region
     * out on a completed match — one linear copy of 2*ncaps ptrdiff_t on the
     * success path only. Aliasing the caller's array directly was considered
     * and rejected: slot_values also holds guards and low-water marks, so aliasing
     * would split the trail's slot space across two base pointers to save a
     * copy whose size is the GROUP COUNT, not the subject length.
     *
     * On a completed match EVERY pair is written (subst C6): slots untouched
     * during the match still hold UNSET from the initialisation. On a failed
     * match the caller's array is UNTOUCHED, because nothing was copied. */
    /* [M6.2 wave E] THE `\K` RULE, and it is ONE LINE in exactly one place
     * (assertions_design.md §6.3 rule 1).
     *
     * `caps[0][0]` on a `\K` artifact must come FROM THE VM ALONE. The
     * prefilter's span start — the `start` argument below, which under the
     * hybrid is `win[0][0]`, i.e. the REVERSE PASS's answer — is the PRE-`\K`
     * start, and it is used for exactly one thing: bounding where the VM
     * begins. Writing it out would report the position matching began at,
     * where PCRE2 reports the position where the last crossed `\K` was.
     *
     * Both halves of the ternary are live and each has its cell. `a\Kb` on
     * "ab" crosses the `\K` and reports (1,2); `(?:a\K)?b` on "b" does not
     * cross it, the slot still holds the per-search PCREC_UNSET, and the
     * answer is the prefilter's own start — (0,1), which is right. So the
     * fallback is not a defensive default, it IS `\K`'s semantics for a path
     * that never passed one.
     *
     * `caps[0][1]` IS UNTOUCHED and must be: `\K` moves the reported START
     * and nothing else. `ab\K` on "ab" is PCRE2 (2,2) — a reported span of
     * length zero after consuming two bytes — which is the shape that makes
     * the match-here entries' return value a separate question (see them
     * below).
     *
     * A `\K`-FREE ARTIFACT TAKES THE PRE-WAVE ARM, character for character.
     * This is the only site that reads `v.nkreset` into a DEFAULT artifact,
     * which is what makes "wave E costs a `\K`-free pattern nothing" a claim
     * about one predicate rather than about a construction spanning four
     * files. `vm_render_listing` and the `--trace` ACCEPT line read it too;
     * a listing writes no artifact, and a traced artifact is a different
     * artifact by construction (the axis says so in its own text). */
    sb_printf(c,
        "/* Copy the run's slot values out into the caller's caps array. The\n"
        " * whole-match pair is not written by the VM at all -- the entry knows\n"
        " * where the attempt began and how long it ran. Group g lives in the\n"
        " * slot PAIR (2g, 2g+1), which is why this indexes arithmetically. */\n"
        "static void %s_report_captures(const %s_run_state *run, ptrdiff_t (*capture_spans)[2],\n"
        "                        size_t match_start, ptrdiff_t match_length)\n"
        "{\n"
        "    int group;\n"
        "%s"
        "    capture_spans[0][1] = (ptrdiff_t)match_start + match_length;\n"
        "    for (group = 1; group < %s_NCAPS; group++) {\n"
        "        capture_spans[group][0] = run->slot_values[2 * group];\n"
        "        capture_spans[group][1] = run->slot_values[2 * group + 1];\n"
        "    }\n"
        "}\n\n",
        v.p, v.p,
        v.nkreset > 0
          ? "    /* \\K: the reported start is where the winning path last\n"
            "     * crossed a \\K (slot 0, trailed), NOT where matching began.\n"
            "     * PCREC_UNSET means no \\K was crossed on this path. */\n"
            "    capture_spans[0][0] = run->slot_values[0] != PCREC_UNSET ? run->slot_values[0]\n"
            "                                         : (ptrdiff_t)match_start;\n"
          : "    capture_spans[0][0] = (ptrdiff_t)match_start;\n",
        v.up);

    /* ---- <prefix>_search (§2.6) ---------------------------------------- */
    sb_printf(c,
        "int %s(const unsigned char *subject, size_t subject_length, size_t search_from,\n"
        "       ptrdiff_t (*capture_spans)[2])\n"
        "{\n"
        "    %s_run_state run;\n"
        "    rx_ctx ctx;\n"
        "    ptrdiff_t result;\n"
        "    size_t attempt_position;\n"
        "%s"
        "    if (search_from > subject_length) return 0;\n",
        g.searchfn, v.p,
        v.nclamp > 0 ? "    size_t window_end;\n" : "");

    /* The recompute, spelled once and used only where a bound reads it. */
    char retry_win[512];
    retry_win[0] = 0;
    if (v.nclamp > 0 && prefn)
        /* H3 site 2 of 3 (the RETRY recompute). The recompute itself STAYS on a
         * cut-bearing artifact — it re-seeds `attempt_position` from the
         * prefilter, which is H2 and is sound, and D51 ruling 2 is why it
         * exists at all. Only the CEILING it also computed is dropped. */
        snprintf(retry_win, sizeof retry_win,
                 "        {\n"
                 "            ptrdiff_t window[1][2];\n"
                 "            if (%s(subject, subject_length, attempt_position, window) != 1) return 0;\n"
                 "            attempt_position = (size_t)window[0][0];\n"
                 "%s"
                 "        }\n",
                 prefn,
                 v.mrl_win
                   ? "            window_end = (size_t)window[0][1] < subject_length ? (size_t)window[0][1] : subject_length;\n"
                   : "            window_end = subject_length;\n");

    /* [M4.6d] THE MRL CEILING, and D51 ruling 2's three obligations, all
     * discharged in this one function.
     *
     * (a) NO-PREFILTER ENTRIES DEFAULT TO THE SUBJECT END. The `else` arm
     *     below, and `<prefix>_match`/`<prefix>_match_caps`, pass `n` /
     *     `ctx->len`. There is no path on which the ceiling is not passed,
     *     because it is a parameter.
     *
     * (b) THE START++ RETRY IS NOT ALLOWED TO GO STALE, and this is the
     *     obligation the ruling makes hard. The window is per-ATTEMPT: the
     *     prefilter's forward scan stops at a dead transition, so
     *     `win[0][1]` is the last accepting END BEFORE that break, and on a
     *     subject holding a second, later match it is therefore too SMALL —
     *     the UNSOUND direction, which deletes real matches rather than
     *     merely pruning less.
     *
     *     A STRUCTURAL argument that the retry cannot fire is available and
     *     is written down here because it is worth knowing, but it is NOT
     *     what makes this safe. The argument: the prefilter is the
     *     capture-ERASED machine (D31's erasure — A_CAP is invisible to the
     *     NFA builder, engine_m4.md §6.1), so it accepts exactly the
     *     pattern's language; it reported that `s[win[0][0], win[0][1])` is
     *     in that language; therefore a match anchored at `win[0][0]` exists
     *     and the VM, which searches that same language, finds one — so `r`
     *     is non-negative on the first pass and `start++` is never reached.
     *     That argument rests on span-equality between the two machines,
     *     which R21 SPLIT into "erasure STRUCTURAL, span-equality
     *     BELIEVED-WITH-GATE" after finding two live priority miscompiles
     *     (K17, K18) in exactly this territory. Resting an unsound-direction
     *     correctness property on a believed claim is what the ruling
     *     forbids, and 0-firings-in-99-trials is explicitly not a discharge.
     *
     *     So the window is RECOMPUTED, which is the ruling's other branch and
     *     costs nothing on a path the argument above says is dead. It is the
     *     SAME three lines as the entry call — deliberately, so there is one
     *     spelling of "ask the prefilter where the next match is" rather than
     *     two that could drift — and re-seeding `start` from the fresh window
     *     is both sound (the prefilter answers for `[start, n)`) and strictly
     *     faster than stepping one byte at a time.
     *
     * (c) WHICH FORM IS ACTIVE is stamped: `<PREFIX>_VM_PRUNE_CEILING`, above.
     *
     * (d) AND THE EMITTED COMMENT ON THE NO-CEILING ARM SAYS "cut-bearing" AND
     *     IS NOT GENERALIZED TO NAME THE LOOKAROUND CASE. [M6.6.2] wave E, and
     *     it is a RULING rather than an oversight. Generalizing it was tried
     *     and REVERTED: that string is emitted into every artifact this arm
     *     reaches, and 54 of those are ATOMIC-bearing and therefore
     *     LOOKAROUND-FREE, so widening it moved 37 bytes on 54 patterns that do
     *     not use the module — which `run_lookaround_identity.sh` caught as 54
     *     differing comparisons on the default and --no-captures axes with
     *     --engine=vm and -fno-prefilter GREEN. That is design §9.1's own
     *     predicted signature for a mis-edited `v.mrl_win`, arriving for a
     *     reason §9.1 did not predict: prose, not the predicate.
     *
     *     Making the string accurate per artifact would need a SECOND flag
     *     recording WHY the ceiling was dropped, and a second flag beside
     *     `v.mrl_win` is the two-sources-that-can-disagree defect the predicate
     *     exists to avoid. The accurate, both-cases description therefore lives
     *     where it costs no emitted bytes: `--emit-ir`'s PRUNING line and the
     *     `mrl_win` field comment at the top of this file.
     */
    if (prefn) {
        sb_printf(c,
            "    {\n"
            "        ptrdiff_t window[1][2];\n"
            "        if (%s(subject, subject_length, search_from, window) != 1) return 0;\n"
            "        attempt_position = (size_t)window[0][0];\n"
            "%s"
            "    }\n",
            prefn,
            v.nclamp == 0 ? ""
              /* H3 site 1 of 3 (the search ENTRY). */
              : v.mrl_win
              ? "        window_end = (size_t)window[0][1] < subject_length ? (size_t)window[0][1] : subject_length;\n"
              : "        window_end = subject_length;  /* cut-bearing artifact: the prefilter answers for the UNCUT language, so its span END is not a bound on this match's end */\n");
    } else {
        sb_puts(c, "    attempt_position = search_from;\n");
        if (v.nclamp > 0) sb_puts(c, "    window_end = subject_length;\n");
    }

    sb_printf(c,
        "    %s_run_state_init(&run);\n"
        "    ctx.subject = subject; ctx.len = subject_length; ctx.ncap = 0;\n"
        "    ctx.caps = NULL; ctx.user = NULL;\n"
        "    for (;;) {\n"
        "        ctx.pos = attempt_position;\n"
        "        result = %s_match_anchored(&ctx, &run%s%s);\n"
        "        if (result == %s_R_STEPS)   return PCREC_ERR_STEPS;\n"
        "        if (result == %s_R_FRAMES)  return PCREC_ERR_FRAMES;\n"
        "        if (result == %s_R_WORK)    return PCREC_ERR_WORK;\n"
        /* [DD-14 wave A] the fourth PROPAGATION line, D49's whole point:
         * a give-up must reach the caller with its own code, never fold
         * into a plain no-match. No arm returns %s_R_RECURSE yet (D71
         * item 1 -- no producer this wave), so this line is dead code on
         * every artifact today and stays that way until module
         * 'recursion' lands one; it is added HERE, with its siblings,
         * rather than later, so the collapse is never missing a code the
         * ABI already reserves. */
        "        if (result == %s_R_RECURSE) return PCREC_ERR_RECURSE;\n"
        /* [DD-14 wave A commit 2] R_INTERNAL PROPAGATES too, exactly like
         * a give-up -- the search entry is a TOP-LEVEL entry, not a
         * composed call site, so F2's trap obligation does not apply
         * here; it applies to whichever future call site invokes this
         * artifact's rx_matchfn AS a callout. `vm_look_behind`'s
         * negative-arm end-check is the one live producer today. */
        "        if (result == %s_R_INTERNAL) return PCREC_ERR_INTERNAL;\n"
        "        if (result >= 0) break;\n"
        "        %s_reset_for_next_attempt(&run);\n"
        "        if (attempt_position >= subject_length) return 0;\n"
        "        attempt_position++;\n"
        "%s"
        "    }\n"
        "    if (capture_spans) %s_report_captures(&run, capture_spans, attempt_position, result);\n"
        "    return 1;\n"
        "}\n\n",
        v.p, v.p, v.nclamp > 0 ? ", window_end" : "",
        /* [M6.2 wave D] `startpos`, NOT `start`. `start` is the position this
         * ATTEMPT begins at and the loop below moves it; `\G` asks about the
         * position the SEARCH was asked to begin at, which is the parameter.
         * On a fully-`\G` pattern the two coincide only on the first pass,
         * which is exactly why every later pass must fail — and why passing
         * `start` here would make `\G` an unconditional truth and turn
         * `\Gfoo` into `foo`. */
        v.ngst > 0 ? ", search_from" : "",
        v.up, v.up, v.up, v.up, v.up, v.p, retry_win, v.p);

    /* ---- <prefix>_match / <prefix>_match_caps (§3, §3.1, §4.4) --------- */
    /* [M6.2 wave E, R30 E8] `\K` AND THIS ENTRY: BOTH OF §6.3 RULE 3'S
     * REQUIREMENTS ARE ALREADY MET HERE, AND NOT BY ACCIDENT.
     *
     * §6.3 quotes the DFA artifact's `rx_match` — `rx_search` plus
     * `caps[0][0] != ctx->pos`, returning `caps[0][1] - caps[0][0]` — and
     * shows both lines breaking under `\K`: the filter compares against
     * the POST-`\K` start and rejects a genuine anchored match, and the
     * return is the POST-`\K` length where a D38 callout's advance needs
     * the CONSUMED one. The rule it derives is "filter on the pre-`\K`
     * start, return the consumed length".
     *
     * THIS ENTRY IS NOT THAT SHAPE, which is E8's other correction: the
     * two engines' match-here entries do not share one. This one calls
     * `<prefix>_match_impl` directly, so:
     *
     *   - THE FILTER IS STRUCTURAL. `match_anchored` starts at `ctx->pos` and
     *     never moves it; there is no retry loop and no start-equality
     *     test to get wrong. "Anchored at the requested position" is a
     *     property of the call, not a property checked afterwards, so
     *     there is nothing here for a post-`\K` start to be compared
     *     against. `a\Kb` at `ctx->pos == 0` returns 2, where the DFA
     *     entry's filter would return -1.
     *   - THE RETURN IS ALREADY THE CONSUMED LENGTH. `match_anchored` returns
     *     `pos - ctx->pos`, computed from positions, not from `caps`, so
     *     `\K` cannot reach it. `ab\K` at 0 returns 2 while its reported
     *     span is (2,2) — the case where the two numbers genuinely differ
     *     and a `caps`-derived return would be 0, which as a callout
     *     advance is an infinite loop.
     *
     * So wave E changes NOTHING in this function, and that is a claim
     * worth a test rather than a comment: `tests/assertions/kreset_
     * entries.c` drives this entry and `<prefix>_match_caps` beside
     * `<prefix>_search` on one `\K` artifact, and
     * `run_codegen_tests.sh`'s `[M6.2-KRESET]` block asserts the DFA
     * artifact's own entry is unchanged. A `\K` pattern never HAS a DFA
     * entry (it is VM-forced), which is why the second half has to be
     * checked on a `\K`-free artifact. */
    sb_printf(c,
        "/* F1's unconditional export, typed rx_matchfn.\n"
        " *\n"
        " * D49: THE GIVE-UP CODES ARE CARRIED HERE, not collapsed to -1. The\n"
        " * return space is >= 0 matched length, -1 no match, and a distinct\n"
        " * code in [PCREC_ERR_FLOOR, -2] for each way the engine can give up\n"
        " * (PCREC_ERR_STEPS, PCREC_ERR_FRAMES, PCREC_ERR_WORK, PCREC_ERR_RECURSE\n"
        " * -- [DD-14]: reserved, no producer yet, D71 item 1). Anything BELOW the floor\n"
        " * stays reserved for the future abort semantic and is what a callout\n"
        " * call site traps on.\n"
        " *\n"
        " * This SUPERSEDES D42.3, which collapsed every give-up to -1 because\n"
        " * D38.4 had reserved the whole < -1 space. Three things moved: pcrec is\n"
        " * pre-release, so a 'final' label reads as 'stable absent a reason';\n"
        " * the typedef is BIDIRECTIONAL, so under the collapse an\n"
        " * embedder-WRITTEN callout had no legal spelling for 'I gave up' at\n"
        " * all (anything below -1 traps the process); and the collapse let an\n"
        " * inner give-up read as a plain path failure, so an outer match could\n"
        " * report an ANSWER where a bound had actually blown. A caller that\n"
        " * only asks 'did it match' still writes `result < 0` and is unaffected. */\n"
        "ptrdiff_t %s(const rx_ctx *ctx)\n"
        "{\n"
        "    %s_run_state run;\n"
        "    ptrdiff_t result;\n"
        "    if (ctx->pos > ctx->len) return -1;\n"
        "    %s_run_state_init(&run);\n"
        "    result = %s_match_anchored(ctx, &run%s%s);\n"
        "    /* No translation and no clamp: the impl's return space IS this\n"
        "     * contract's -- >= 0, -1, or one of the R_ sentinels, which are\n"
        "     * the ERR_ codes (give-up or, [DD-14] wave A commit 2, the\n"
        "     * below-the-floor PCREC_ERR_INTERNAL -- this entry propagates\n"
        "     * it exactly like a give-up, for the same top-level-entry\n"
        "     * reason <prefix>_search does). A defensive floor test here\n"
        "     * would be dead code pretending to be a safeguard. */\n"
        "    return result;\n"
        "}\n\n",
        g.matchfn, v.p, v.p, v.p,
        v.nclamp > 0 ? ", ctx->len" : "",
        /* [M6.2 wave D, R30 E8] The match-here entry's `startpos` IS
         * `ctx->pos` — it is threaded, not absent — so `\G` here is
         * `pos == ctx->pos`, trivially true at entry. That makes the two
         * entries AGREE EXACTLY for a fully-`\G` pattern, and legitimately
         * DISAGREE for a partial one (`\Gfoo|bar`): `<prefix>_search` may
         * find `bar` at a later offset where this entry's caller asked about
         * one position only. tests/assertions/run_gstart_diff.sh pins both
         * halves, scoped, because an unscoped "the entries agree" test would
         * be red on correct behaviour. */
        v.ngst > 0 ? ", ctx->pos" : "");

    sb_printf(c,
        "/* The capture-delivering sibling. Same D49 return space as\n"
        " * <prefix>_match above -- it always had room for the codes (it is not\n"
        " * an rx_matchfn), and now the two agree instead of differing over a\n"
        " * reservation only one of them was bound by. capture_spans_out is UNTOUCHED on\n"
        " * every negative return, give-up included: a caller that gave up has\n"
        " * no captures, and A-8's untouched-wins rule does not bend for it. */\n"
        "ptrdiff_t %s(const rx_ctx *ctx, ptrdiff_t (*capture_spans_out)[2])\n"
        "{\n"
        "    %s_run_state run;\n"
        "    ptrdiff_t result;\n"
        "    if (ctx->pos > ctx->len) return -1;\n"
        "    %s_run_state_init(&run);\n"
        "    result = %s_match_anchored(ctx, &run%s%s);\n"
        "    if (result < 0) return result;\n"
        "    if (capture_spans_out) %s_report_captures(&run, capture_spans_out, ctx->pos, result);\n"
        "    return result;\n"
        "}\n\n",
        g.matchcapsfn, v.p, v.p, v.p,
        v.nclamp > 0 ? ", ctx->len" : "",
        v.ngst > 0 ? ", ctx->pos" : "", v.p);

    pcrec_emit_residual(cx);

    pcrec_emit_info(cx, &g, 2, job->fit.why,
                    has_budget ? budget : -1, work_budget, bt_frames, ceiling);

    if (cx->opt->flags & PCREC_EMIT_MAIN)
        pcrec_emit_main(cx, &g);

    /* [M4.5c] The listing, rendered LAST — the event stream is complete by
     * now, and so are the stamp numbers it reports, which are the same
     * variables the artifact above was stamped from rather than a second
     * computation of them. */
    if (cx->want_ir) {
        VmStamp st;
        st.budget = budget;
        st.bt_frames = bt_frames;
        st.trail_frames = trail_frames;
        st.ceiling = ceiling;
        st.nstate = nstate;
        st.nguard = nguard_total;
        st.nlow = nlow_total;
        st.nmark = nmark_total;
        st.ncaps = ncaps;
        st.has_budget = has_budget;
        st.prefilter = prefn != NULL;
        st.has_bref  = (v.enc_mask &
                        (PCREC_ENCE_BREF | PCREC_ENCE_BREF_CASELESS)) != 0;
        st.why = job->fit.why;
        vm_render_listing(&v, &job->irsb, &st);
    }
}
