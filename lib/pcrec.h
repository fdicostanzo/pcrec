/* pcrec — PCRE-to-C regex compiler: public library API.
 * Compile a pattern to specialized C source; the generated code has no
 * dependency on this library. */
#ifndef PCREC_H
#define PCREC_H

#include <stddef.h>
#include <stdint.h>

/* [M5-SEAM] (D58, 2026-08-18) THE ENCODING NAMESPACE. Exactly one encoding
 * per COMPILE CALL — a `pcrec_options` field, never process- or file-global,
 * so mixed encodings in one compilation unit or binary are supported by
 * construction (self-contained artifacts, distinct prefixes, each embedding
 * exactly one encoding's residual block; DD-12 (8)).
 *
 * `PCREC_ENC_BYTE` was spelled `PCREC_ENC_ASCII` before [M5-SEAM], and the
 * CLI spelled it `-e ascii`. RENAMED, not aliased (pre-v1, docs/spec/
 * match_api.md §9's announced-boundary form): the semantics were always
 * "every byte is a character, 8-bit clean" — bytes >= 0x80 are ordinary
 * bytes with no case and no meaning, which is precisely NOT what "ASCII"
 * says — and D58 names the encoding `byte` in the ruling text itself. Two
 * names for one namespace member is [SR-10]'s motivating defect, so there
 * is no compatibility alias: `-e ascii` is now an unknown encoding. */
enum {
    PCREC_ENC_BYTE = 0,   /* byte semantics, 8-bit clean; the default */
    PCREC_ENC_UTF8 = 1    /* not yet implemented (arrives with milestone M5) */
};

/* [M4.4] (D43.2/D44.8): pcrec's own boolean options, one bit each in
 * pcrec_options.flags. `PCREC_CASELESS` parallels PCRE2_CASELESS (RULED
 * D44.8: not PCREC_CASE_INSENSITIVE) so a caller porting from PCRE2
 * recognises it on sight; `PCREC_EMIT_MAIN` and `PCREC_NO_CAPTURES` have no
 * PCRE2 equivalent. `PCREC_NO_CAPTURES` is RESERVED here (D42.1's
 * captures-default axis is M4.5-era) — no CLI flag or compile-time behavior
 * sets or reads it yet; the bit exists so a caller's code compiled against
 * this header does not need revisiting when M4.5 wires it.
 *
 * [M4.5b] PCREC_NO_CAPTURES is now LIVE (D42.1: captures are ON by default;
 * this bit recovers the pre-M4.5 pure-DFA artifact, RX_NCAPS 1). */
enum {
    PCREC_CASELESS    = 1u << 0,  /* was pcrec_options.caseless */
    PCREC_EMIT_MAIN   = 1u << 1,  /* was pcrec_options.emit_main */
    PCREC_NO_CAPTURES = 1u << 2,  /* --no-captures (D42.1) */
    /* [M4.5c] (DD-8, engine_m4.md S10): emit an INSTRUMENTED matcher that
     * prints every resume-frame push/pop and capture write to stderr as it
     * runs. A GENERATION AXIS like every other option here (D18) — the
     * instrumentation is compiled in, not switched at run time — and never
     * the default: a traced artifact writes to stderr, which is not something
     * a shipped matcher should ever do. The artifact stamps that it is
     * traced, so no one has to guess. VM artifacts only; a DFA matcher has
     * no resume frames to trace. */
    PCREC_TRACE       = 1u << 3,
    /* [ENG-BREP] `-fno-possessify`: DENY the possessification rewrite
     * (docs/design/eng_brep_design.md §2, D47.3).
     *
     * A TESTING AND TUNING AXIS, not a user feature. Possessification changes
     * no answer — that is its entire claim — so the only reason to turn it off
     * is to CHECK that claim: the row's primary instrument is a
     * pcrec-vs-pcrec differential that compiles the same pattern twice, once
     * with the rewrite and once without, and compares spans, every capture
     * slot and the failure surface. A strategy that cannot be denied cannot be
     * differentially tested.
     *
     * DENY rather than FORCE, and D47.3 rules the difference load-bearing:
     * each quantifier walks its own ladder skipping the denied steps, so a
     * denial composes per-quantifier with no need to ADDRESS one quantifier
     * inside a pattern. It is the first member of a family — the rest of the
     * ladder's denials (`-fno-counter`, a rung selector, a value parameter for
     * K) arrive with the strategies they deny. */
    PCREC_NO_POSSESSIFY = 1u << 4,
    /* [ENG-BREP] `-fno-revdet`: DENY the REVERSE-DETERMINISTIC rung
     * (docs/design/engine_m4.md §2.5, D47.3), the second member of the family
     * the bit above opened.
     *
     * Same shape and same reasons. The rung changes no answer — a quantifier
     * emitted as one body copy plus a backward walk matches exactly what the
     * same quantifier replicated `n` times matches — so the only reason to turn
     * it off is to CHECK that claim, and the check is a pcrec-vs-pcrec
     * differential in which the DENIED build falls one rung to frames, i.e. to
     * literal replication, i.e. to the semantic ground truth
     * (eng_brep_design.md §5.1). A strategy that cannot be denied cannot be
     * differentially tested.
     *
     * DENY rather than FORCE, so it composes per quantifier with no need to
     * ADDRESS one quantifier inside a pattern: each walks its own ladder
     * skipping the denied rungs. Denying this one drops a qualifying
     * quantifier to frames; denying it does not, and must not, deny
     * possessification, which is an orthogonal modifier at every rung. */
    PCREC_NO_REVDET     = 1u << 5,
    /* [ENG-BREP] `-fno-counter`: DENY the COUNTER rung
     * (docs/design/counterk_impl/counterk_design.md), the THIRD member of the
     * family, and the one whose denial is load-bearing beyond testing.
     *
     * Same shape and same reasons as the two above. What is specific to it:
     * denying the rung drops a bounded repeat to VM_RUNG_FRAMES_BOUNDED, which
     * for a bounded repeat is LITERAL REPLICATION — N copies of the body, which
     * is exactly what ships today and is therefore the semantic GROUND TRUTH
     * the differential compares against (§8.1). So this flag is not merely how
     * the rung is tested; it is what makes the ground truth reachable at all,
     * the same role `-fno-revdet` plays one rung up.
     *
     * That ground truth has a KNOWN LIMIT, and it is this rung's own endgame:
     * above the replication cap there is no `-fno-counter` build to compare
     * against, because the cap is what refuses it. §8.1's differential is blind
     * there by construction, and §8.5 cell 1 covers that region by the oracle
     * sweep and by the strategy's own N-independence instead. */
    PCREC_NO_COUNTER    = 1u << 6,
    /* [M4.6d] `-fno-length-prune`: DENY MINIMUM-REMAINING-LENGTH pruning
     * (docs/design/k23_impl/k23_design.md, D51 ruling 1), the family's FOURTH
     * member and D46's controllability half for this optimization.
     *
     * Same shape and same reasons as the three above, with one difference
     * worth stating: MRL is not a RUNG, it is a bound emitted ON whichever
     * rung a quantifier already took, so denying it changes no rung, no slot
     * and no capacity — an artifact built with it is byte-for-byte the one
     * pcrec emitted before MRL existed. That is what makes the denial the
     * ground truth of the differential: the same corpus, the same subjects,
     * pruned against unpruned, byte-identical answers expected on every
     * capture slot (§7.4's pcrec-vs-pcrec instrument). */
    PCREC_NO_LENGTH_PRUNE = 1u << 7,
    /* [M4.6f] `-fno-prefilter`/`-fprefilter`: the D46 close-out for the
     * PREFILTER axis (docs/design/engine_m4.md §6.1/§4.7, D46/D47.3).
     *
     * A DIFFERENT SHAPE from the four bits above, and deliberately so.
     * Those deny a per-QUANTIFIER strategy, which is why D47.3 rules DENY
     * (not FORCE) the right spelling for them — each quantifier walks its
     * own ladder skipping a denied step, so "force possessify on THIS
     * quantifier" has no addressing problem to solve because there is
     * nothing to address. `fit.prefilter` (src/opt/select_engine.c) is not
     * per-quantifier; it is ONE verdict for the whole artifact, decided
     * jointly with `--engine`: auto+captures turns it on, `--engine=vm`
     * turns it off (R21 E-6) as a SIDE EFFECT of choosing the engine, with
     * no way to ask for the combination independently. D46's own
     * motivating scenario is exactly this coupling: a test built to pin
     * one axis silently moves on another. So this is a FORCE PAIR, not a
     * deny-only flag — both directions are independently reachable, which
     * is what decouples "which engine" from "does the hybrid prefilter
     * run ahead of it".
     *
     * DO-OR-DIE (D47.3's posture) rather than a silent downgrade:
     * `PCREC_FORCE_PREFILTER` on a pattern that compiles to the DFA engine
     * (no VM artifact exists to attach a prefilter to) REFUSES, the same
     * `--engine`-precedent shape as the DFA/VM engine conflicts in
     * src/opt/select_engine.c's own switch. `PCREC_NO_PREFILTER` is always
     * buildable — `--engine=vm` already ships that exact configuration
     * today — so it never refuses.
     *
     * Same masked-out-of-`rx_info.flags` treatment as the four bits above
     * and for the identical reason (src/gen/emit_dfa.c's emit_info_def):
     * the prefilter changes no answer, only how one is found (§6.1's
     * exactness claim), so two identically-behaving artifacts must not
     * differ in their reflection surface over a knob with no observable
     * effect. What the axis DOES is recorded in `<PREFIX>_VM_PREFILTER`
     * (src/gen/emit_vm.c), which reports what the emitter did rather than
     * what it was asked — the D46 half a denied-or-forced request can be
     * checked against. */
    PCREC_NO_PREFILTER    = 1u << 8,
    PCREC_FORCE_PREFILTER = 1u << 9,
    /* [OPT-ALTCLS] `-fno-altcls-merge`/`-fno-altcls-factor`: D46's
     * controllability half for the ALTERNATION->CLASS NORMALIZATION pass
     * (docs/dev/plan.md's [OPT-ALTCLS] row, src/opt/altcls.c).
     *
     * BACK TO D47.3's DENY-ONLY SHAPE, not `_PREFILTER`'s force pair — and
     * for the family's original reason, not the prefilter's exception to
     * it. Each mergeable/factorable alternation RUN in the pattern is its
     * own selection point, addressed independently the way each A_REP
     * walks its own possessify/revdet ladder; there is no single
     * artifact-wide verdict the way `fit.prefilter` is one, so FORCE has
     * no addressing problem to solve because (as with possessify/revdet)
     * there is nothing to force — a run that cannot merge/factor always
     * DECLINES, safely, the same as an A_REP that cannot possessify.
     *
     * TWO BITS, not one, because the two stages are independently useful
     * to pin: stage 1 (single-char runs -> one class) and stage 2 (prefix
     * factoring, emitting no new capturing groups) are different rewrites
     * with different soundness arguments, and stage 2 runs on stage 1's
     * OUTPUT (docs/dev/plan.md's interaction note), so denying stage 1
     * alone still lets stage 2 factor an all-single-char run's literal
     * spelling, while denying stage 2 alone leaves single-char merging
     * live. A differential that wants ONLY one stage held constant needs
     * both knobs separately reachable.
     *
     * Same masked-out-of-`rx_info.flags` treatment as the deny family
     * above and for the identical reason (src/gen/emit_dfa.c's
     * emit_info_def): the pass changes no answer, only the emitted shape,
     * so two identically-behaving artifacts must not differ in their
     * reflection surface over a knob with no observable effect. What the
     * pass DID is recorded in `<PREFIX>_ALTCLS_MERGES`/
     * `<PREFIX>_ALTCLS_FACTORED` (pcrec_emit_prologue, shared by both
     * emitters since this pass runs before either engine is built,
     * unlike the VM-only possessify/revdet stamps) — the D46 half a
     * denied request can be checked against. */
    PCREC_NO_ALTCLS_MERGE  = 1u << 10,
    PCREC_NO_ALTCLS_FACTOR = 1u << 11,
    /* [M6.4.2] `-fno-atomic-discharge`: DENY the FREE DISCHARGE
     * (docs/design/atomic_groups_design.md §5.3; src/opt/atomic.c).
     *
     * The discharge deletes an `A_ATOMIC` whose cut possessify's §2.2 verdict
     * proves is a NO-OP. Like every other member of this family it changes no
     * ANSWER — that is its entire claim — so the only reason to turn it off is
     * to CHECK that claim, with a pcrec-vs-pcrec differential that compiles the
     * same pattern twice and compares spans, every capture slot and the failure
     * surface. A rewrite that cannot be denied cannot be differentially tested.
     *
     * WHAT IT DENIES IS AN ENGINE, NOT A STRATEGY, and that is the one way it
     * differs from the five above. Every other `-fno-` here leaves the same
     * artifact kind and changes the machinery inside it; denying THIS one
     * leaves the `A_ATOMIC` in the tree, so SR-8's consultation sees a
     * DFA-excluding node and the pattern compiles to the VM where it would have
     * compiled to a pure DFA. `--engine=dfa -fno-atomic-discharge '[^"]*+"'`
     * therefore REFUSES, which is correct and is the flag doing its job.
     *
     * IT IS SEPARATE FROM `-fno-possessify` DELIBERATELY. The discharge is NOT
     * gated by that flag (src/opt/select_engine.c drives it unconditionally),
     * because an OPTIMISATION denial must not decide which engine a pattern
     * gets. Folding the two together would have made `-fno-possessify` do
     * exactly that. */
    PCREC_NO_ATOMIC_DISCHARGE = 1u << 12,
    /* [DD-14 wave G] `-fno-splice-calls`: DENY the SPLICE LINKAGE for every
     * subroutine call site (docs/design/subroutines_design.md §6.3, §9.2;
     * src/opt/callgraph.c's eligibility rule).
     *
     * WHAT IT DENIES. A call site whose callee is not in a cycle and whose
     * expansion fits the size budget is emitted INLINE, with its own exit;
     * every other site takes the CALL linkage into one shared emitted region.
     * This flag forces the LINKAGE everywhere, which is exactly the artifact
     * wave B+C shipped — so the denied build is the ground truth of §9.2's
     * SECOND CONTROL, the one control this module has that the lookaround
     * module did not: for every non-recursive call-bearing pattern the
     * SPLICE-linked and LINKAGE-linked artifacts are two DIFFERENT PROGRAMS
     * BUILT BY THIS COMPILER that must agree on every answer and every group
     * span. A rewrite that cannot be denied cannot be differentially tested.
     *
     * IT IS `PCREC_NO_ATOMIC_DISCHARGE`'s SHAPE, NOT `-fno-possessify`'s, and
     * the difference is the same one: this denial CHANGES WHICH ENGINE a
     * pattern gets. A spliced call has an exact finite lowering, so `nfa.c`
     * can build the machine and `select_engine` need not force the VM;
     * denying the splice leaves a LINKED call, which is structurally VM-only
     * (§8.1) and carries no prefilter (§8.2). So
     * `--engine=dfa -fno-splice-calls '(?:(?<g>a)){0}(?&g)'` REFUSES, which is
     * correct and is the flag doing its job — the atomic discharge's own
     * `--engine=dfa -fno-atomic-discharge '[^"]*+"'` precedent exactly.
     *
     * AND FOR THAT REASON IT DOES *NOT* JOIN `emit_info_def`'s
     * `strategy_denials` MASK (src/gen/emit_dfa.c). That mask is for knobs
     * with no observable effect; this one selects an engine, so `rx_info.flags`
     * records it exactly as it records `PCREC_NO_ATOMIC_DISCHARGE`. What the
     * emitter DID is reported separately by `<PREFIX>_VM_CALL_SPLICED` /
     * `<PREFIX>_VM_CALL_LINKED` (two counts, not one string — docs/spec/tuning.md §2.9)
     * (src/gen/emit_vm.c) — sites spliced vs sites linked — which is the D46
     * half a denied request is checked against. */
    PCREC_NO_SPLICE_CALLS = 1u << 13,
    /* [OPT-1] `-fno-tiered-entry`: DENY the TWO-TIER DEFAULT ENTRY
     * (docs/design/two_tier_entry.md, docs/spec/tuning.md §2.12), D46's
     * controllability half for the entry-shape axis.
     *
     * WHAT IT DENIES. An un-suffixed entry (`<prefix>_search`,
     * `<prefix>_match`, `<prefix>_match_caps`) normally runs the match on a
     * SMALL, page-budgeted on-stack buffer and, on `PCREC_ERR_FRAMES` only,
     * calls a `noinline` static that owns the full stamped default and re-runs
     * the match from scratch. That exists because gcc's stack-clash protection
     * probes every page of the entry's frame on EVERY call, which cost 233.8
     * vs 46.3 ns on a 16-byte subject ([OPT-1] STEP 1). This flag emits the
     * SINGLE-TIER shape instead — the entries exactly as they shipped before
     * [OPT-1] — which is both the bisect lever for the optimization and the
     * build an identity gate can compare the old entry against.
     *
     * DENY-ONLY, D47.3's default shape: there is one entry shape per artifact,
     * so there is nothing to ADDRESS and nothing to force.
     *
     * IT JOINS `emit_info_def`'s `strategy_denials` MASK
     * (src/gen/emit_dfa.c), unlike the two bits above it and for the mask's
     * own stated reason: the tier changes NO ANSWER — the deep tier is a
     * bit-for-bit replay of what the single-tier entry does, from scratch
     * (two_tier_entry.md §4) — so two artifacts that answer identically must
     * not differ in their reflection surface over it. What the emitter DID is
     * reported by `<PREFIX>_FAST_FRAMES`/`<PREFIX>_FAST_TRAIL`
     * (src/gen/emit_vm.c), which equal `_RESUME_FRAMES`/`_TRAIL_FRAMES`
     * exactly when the artifact has one tier — by this flag or by the three
     * degenerate cases §3.1 enumerates. That is the D46 half a denied request
     * is checked against. */
    PCREC_NO_TIERED_ENTRY = 1u << 14,
    /* [OPT-3] `-fno-premul-table`: DENY the PRE-MULTIPLIED DFA TRANSITION
     * TABLE (docs/design/premultiplied_dfa_table.md, docs/spec/tuning.md
     * §2.13), D46's controllability half for the DFA scan's table-form axis.
     *
     * WHAT IT DENIES. A DFA scan's transition table normally holds
     * `next_state * classes` rather than `next_state`, so the emitted step is
     * `state = table[state + class]` and the loop's carried dependency chain is
     * `add, load` instead of `lea, lea, movslq, load`. [OPT-3] STEP 1 measured
     * that chain as the WHOLE of the scan's per-byte cost (10.7 cycles/byte,
     * latency-bound with ~2x spare issue width) and the premultiplied form as
     * 1.276x on the comparative bench's three throughput subjects. This flag
     * emits the INDEXED form instead — the tables and the loop exactly as they
     * shipped before [OPT-3] — which is both the bisect lever for the
     * optimization and the build an identity gate compares the new one
     * against.
     *
     * DENY-ONLY, `-fno-tiered-entry`'s shape: there is one table form per
     * machine and a generation-time rule picks it (the form is REFUSED above a
     * size bound, where the loop is memory-bound and the premultiplied accept
     * table's growth would buy nothing), so there is nothing to ADDRESS and
     * nothing to force.
     *
     * IT JOINS `emit_info_def`'s `strategy_denials` MASK (src/gen/emit_dfa.c),
     * for the mask's own reason: the table form changes NO ANSWER — it changes
     * the ENCODING of a state, not the machine, and the corpus plus the
     * bench's 91 subjects are compared span for span across both forms — so
     * two artifacts that answer identically must not differ in their
     * reflection surface over it. What the emitter DID is reported by
     * `<PREFIX>_DFA_TABLE`, which reads `"indexed"` under this flag and
     * `"premultiplied"`, `"mixed"` or `"none"` otherwise. That is the D46 half
     * a denied request is checked against. */
    PCREC_NO_PREMUL_TABLE = 1u << 15,

    /* [OPT-K] `-fno-offset-skip` — deny the OFFSET-k candidate-start skip.
     *
     * WHAT IT DENIES. A DFA artifact's forward scan filters candidate match
     * starts on the byte AT the candidate. This axis lets it filter on a SET
     * of (offset, byte-set) tests every match must satisfy — for
     * `\d{4}-\d{2}-…` a digit at offset 0 AND a `-` at offset 4 — derived
     * from the pattern's own prefix and chosen by a cost model over a byte
     * frequency prior (docs/design/offset_k_skip.md). The selectivity is the
     * CONJUNCTION: on log text `-` at offset 4 is structural and a digit at
     * offset 0 is in every line, and neither alone filters anything.
     *
     * ANSWER-IDENTITY-preserving, and the argument is one line: the skip
     * refuses only starts the stepped scan would refuse, because each test is
     * a NECESSARY condition of a match beginning there. So the denied build is
     * a valid ground truth, and it is more than that — it emits what the
     * compiler emitted before this axis existed, to the line, apart from the
     * one `<PREFIX>_DFA_PREFILTER_OFFSETS` stamp every `abi` 9 artifact
     * carries. That is what makes it the control the identity gate compares
     * against rather than a fourth variant.
     *
     * DENY-ONLY, `-fno-premul-table`'s shape and not `-fno-prefilter`'s force
     * pair: the compiler picks one k-set per artifact from its own cost model,
     * so there is nothing for a caller to ADDRESS and nothing to force. A
     * caller who wants a different k-set wants a different cost model, which
     * is D83's findings-file hook and not a flag.
     *
     * IT JOINS `emit_info_def`'s `strategy_denials` MASK (src/gen/emit_dfa.c)
     * for that mask's own reason: it changes no answer, so two artifacts that
     * behave identically must not differ in their reflection surface over it.
     * What the emitter DID is reported by `<PREFIX>_DFA_PREFILTER`
     * (`"offset-set"` / `"offset-set-bounded"`) and by
     * `<PREFIX>_DFA_PREFILTER_OFFSETS`, which names the chosen offsets. */
    PCREC_NO_OFFSET_SKIP = 1u << 16,

    /* [ENG-ABS] `-fno-anchored-dfa` — deny the UNWRAPPED anchored match-here
     * machine on a DFA artifact.
     *
     * WHAT IT DENIES. `<prefix>_match` and `<prefix>_match_caps` promise a
     * match at exactly `ctx->pos`. A DFA artifact used to reach that answer by
     * running its ordinary UNANCHORED search and rejecting any match whose
     * start is not `ctx->pos` — correct, but it pays a reverse pass it does
     * not need (the start is known) and a failing probe can skim the rest of
     * the subject hunting a later match the filter then discards. This axis
     * emits a THIRD machine instead: the same subset construction over the
     * same NFA, rooted at the pattern's own first state rather than at the
     * start-anywhere self-loop, run forward from `ctx->pos` with no reverse
     * pass and no candidate skip (docs/design/anchored_match_unwrapped.md).
     *
     * ANSWER-IDENTITY-preserving, and the argument is §3.3 of that note: the
     * wrapped machine's state is the anchored machine's state followed by the
     * threads of later starts, D3's accept-pruning cuts every later start out
     * of the run the moment a `ctx->pos` thread accepts, and the reverse pass
     * is exactly what distinguishes the two — which is the work this form does
     * not have to do rather than work it skips.
     *
     * DENY-ONLY, `-fno-premul-table`'s shape: the compiler emits the form
     * wherever the machine fits its caps, so there is nothing for a caller to
     * ADDRESS and nothing to force. A pattern whose anchored machine overflows
     * the DFA caps falls back to the search-and-filter form, which is a
     * SELECTION OUTCOME and never a refusal.
     *
     * IT JOINS `emit_info_def`'s `strategy_denials` MASK (src/gen/emit_dfa.c)
     * for that mask's own reason: it changes no answer, so two artifacts that
     * behave identically must not differ in their reflection surface over it.
     * What the emitter DID is reported by `<PREFIX>_DFA_MATCH`, which reads
     * `"search-filter"` under this flag and `"unwrapped"` otherwise. */
    PCREC_NO_ANCHORED_DFA = 1u << 17,

    /* [ART-SIZE] DENY THE SIZE TERM'S K SELECTION (D84; docs/design/
     * artifact_size_term.md §7.2). Bit 17 is [ENG-ABS]'s.
     *
     * With this set the counter rung's K is PCREC_DEFAULT_UNROLL_K (or
     * `unroll_k`) unconditionally: the emitted-size threshold is not tested
     * and the unroll ladder is not evaluated, so the artifact is the one
     * today's compiler emits. `<PREFIX>_UNROLL_K_WHY` reads `"denied"`, which
     * is a DIFFERENT value from `"default"` on purpose — a check must be able
     * to tell "the term was denied" from "the term ran and the artifact was
     * below the threshold" (a distinction the first design's three-value
     * stamp could not express).
     *
     * IT DOES NOT REACH EITHER EMITTED-SIZE CAP, and that is a ruling rather
     * than an oversight (D84 ruling 1): a safety refusal a flag can turn off
     * is not a safety refusal, and D45's consequence 1 is a compiler-side
     * obligation. The caps are instead OVERRIDABLE UPWARD, raise-only, via
     * `max_emit_code_bytes`/`max_emit_bytes` below. So a denied build can
     * still be REFUSED for size — correctly: denying the term removes the
     * mechanism that would have made the artifact smaller, it does not make a
     * 2 MB artifact acceptable. */
    PCREC_NO_SIZE_TERM = 1u << 18,

    /* [OPT-4] THE PREFILTER'S LANGUAGE (K39; docs/design/
     * prefilter_count_independence.md). Bit 18 is [ART-SIZE]'s.
     *
     * The VM hybrid's prefilter is a FILTER: what it owes the VM is a sound
     * REJECTION and a lower bound on the match start, never an exact language
     * — `src/ir/nfa.c` already answers for a strict superset whenever the
     * pattern carries an atomic group or a lookaround. Above
     * `PCREC_PREFILTER_EXACT_NFA_STATES` a counted repeat `X{m,n}` is
     * therefore lowered, FOR THE PREFILTER ONLY, as `X{min(m,1),}` — a
     * superset whose proof never mentions `n`, so the prefilter's DFA (and
     * the artifact) stops scaling with the count.
     *
     * `PCREC_NO_PREFILTER_COLLAPSE` recovers the exact prefilter, and with it
     * the sharper match start and the `"prefilter-window"` pruning ceiling
     * that a superset prefilter cannot carry — at the count-proportional size
     * this flag exists to let a caller choose. `PCREC_FORCE_PREFILTER_COLLAPSE`
     * drops the state budget instead, so the collapse applies to EVERY counted
     * repeat and the emitted size is count-independent rather than merely
     * count-bounded. Requesting both is refused.
     *
     * NEITHER FLAG CHANGES AN ANSWER. The prefilter axis is
     * answer-identity-preserving (D46), which is what makes the deny/force
     * pair a sweepable control rather than a semantic switch, and
     * `<PREFIX>_VM_PREFILTER_LANG` is where the artifact says which language
     * it was built from, and `<PREFIX>_VM_PREFILTER_LANG_WHY` beside it says
     * which of the five reasons produced that value — including the measured
     * NFA state count the budget was compared against, so a caller deciding
     * whether to pass either flag can see how close this pattern sits to the
     * knee without recompiling it. */
    PCREC_NO_PREFILTER_COLLAPSE    = 1u << 19,
    PCREC_FORCE_PREFILTER_COLLAPSE = 1u << 20,

    /* [OPT-5] THE DFA SCAN EDGE (docs/dev/opt5_step0_profile.md;
     * src/opt/scanedge.c). A region of a DFA whose states differ only in HOW
     * MANY bytes of one fixed class have been counted is one EDGE, emitted as
     * a bounded scan loop whose loop-carried register is the cursor — instead
     * of one data-dependent transition-table load per byte, which the profile
     * measured at ~6x the cost of the identical language on pcrec's own VM.
     *
     * IT IS THE FIRST DFA AXIS WHOSE DENIAL CHANGES THE MACHINE AND NOT ONLY
     * THE EMITTED LOOP: the run's interior states are DELETED (the scan edge
     * replaces them), so `[a-z]{0,16384}`'s forward machine is two states
     * rather than 16,385. Denying it restores both the states and the table
     * walk, which is what makes the denied build a byte-for-byte reference
     * for the answer-identity sweep. It changes no answer either way. */
    PCREC_NO_SCAN_EDGE = 1u << 21
};

/* [ENG-BREP] the counter rung's UNROLL FACTOR, K (counterk_design.md §4.1;
 * eng_brep_design.md §4.5's "K must not become a per-pattern heuristic in v1",
 * held strictly by D47's ADDENDUM). ONE per-artifact constant: every
 * quantifier in a pattern unrolls by the same K, with no per-quantifier
 * variation of any kind. The downward clamp that would have varied it moved
 * whole to plan row [ENG-CLAMP].
 *
 * A TUNING AXIS, and the value parameter of the deny flag above. K = 0 means
 * the built-in default (PCREC_DEFAULT_UNROLL_K, D47.2). */
enum {
    PCREC_UNROLL_K_DEFAULT = 0
};

/* [M4.5b] (docs/design/engine_m4.md §5.6): the per-pattern engine override.
 * AUTO is APPROACH §2's "automatic per pattern"; the other two are diagnostic
 * (reproduce a bug, measure the hybrid against VM-only) and REFUSE cleanly
 * rather than falling back silently. PCREC_ENGINE_VM additionally DISABLES
 * the DFA prefilter (D44/R21 E-6), which is what makes it an independent
 * second derivation of the match span rather than an echo of the DFA's. */
enum {
    PCREC_ENGINE_AUTO = 0
};

/* [ABI-NS] (D60 addendum, 2026-08-18): PCREC_ENGINE_DFA/PCREC_ENGINE_VM are
 * `#define`d here, NOT `enum` members like PCREC_ENGINE_AUTO above, and that
 * is a forced choice, not a style pick. Every generated artifact ALSO emits
 * `#define PCREC_ENGINE_DFA 1` / `#define PCREC_ENGINE_VM 2` (its
 * PCREC_RX_ABI_H block, src/gen/emit_dfa.c) naming `rx_info.engine`'s
 * contract, byte-identical to the two lines below on purpose — an artifact
 * must stay self-contained (no dependency on pcrec.h, top-level CLAUDE.md),
 * so it cannot simply reference this header's spelling. A consumer TU that
 * includes BOTH this header and a generated artifact's header therefore sees
 * the SAME name declared twice; two identical `#define`s of one name are a
 * silent no-op redefinition (measured: no diagnostic under
 * `-Wall -Wextra -Werror`), regardless of which file is included first. An
 * `enum` member here would NOT be safe the same way: `#define PCREC_ENGINE_DFA
 * 1` from an artifact's header, included BEFORE this one, textually rewrites
 * this file's own `PCREC_ENGINE_DFA = 1,` enumerator to `1 = 1,` -- a hard
 * compile error, verified directly. Keep these two byte-identical to
 * emit_dfa.c's emission if either side's spelling ever needs to change. */
#define PCREC_ENGINE_DFA 1
#define PCREC_ENGINE_VM  2

/* [M4.5b] `step_budget`'s sentinels (engine_m4.md §4.6). The default is a
 * BRING-UP PLACEHOLDER: D12 rules that budgets come from measured medians and
 * [M4.6] is where the measurement happens. */
enum {
    PCREC_STEP_BUDGET_DEFAULT = 0,   /* emit the compiled-in default (500,000,000, D51; docs/spec/limits.md) */
    PCREC_STEP_BUDGET_NONE    = -1   /* --fno-step-budget: emit no counter */
};

/* [ENG-BREP counter-K] `work_budget`'s sentinels, the same shape as the pair
 * above (D47 SECOND ADDENDUM settlement 4; default ruled at D49). The THIRD
 * bound: per-iteration forward work the fail label never sees — frames
 * discarded at a cut, and iterations of a frameless scan. A step is still one
 * backtrack resumption and this counter never touches it.
 *
 * There is deliberately NO `--fno-work-budget`: v1 rides ONE existence gate,
 * so `--fno-step-budget` suppresses both counters (D49's manager-accepted
 * conventions). That keeps tests/vm/run_vm_tests.sh's no-counter pin true as
 * written, and splitting the gate later is purely additive. `_NONE` exists
 * anyway because it is what that single gate SETS this field to. */
enum {
    PCREC_WORK_BUDGET_DEFAULT = 0,   /* emit the compiled-in default (1,000,000,000, D49; docs/spec/limits.md) */
    PCREC_WORK_BUDGET_NONE    = -1   /* no work counter (rides --fno-step-budget) */
};

typedef struct {
    const char *prefix;      /* C identifier prefix for generated symbols; default "rx" */
    int         encoding;    /* PCREC_ENC_* */
    uint64_t    flags;       /* PCREC_CASELESS | PCREC_EMIT_MAIN | ... (D43.2/D44.8,
                                 [M4.4]: BREAKS the prior separate `caseless`/`emit_main`
                                 int fields into bits of one word — one representation of
                                 each boolean fact end to end, CLI parse through this field
                                 through the generated rx_info.flags, §5 match_api_m4.md).
                                 PCREC_CASELESS: match case-insensitively (ASCII letters
                                 only — Unicode folding is module 'utf8', M5). Compiled
                                 AWAY into the automaton's byte classes: the generated code
                                 carries no flag, no branch and no case conversion, and its
                                 entry point has the same signature either way (D18). That
                                 zero-cost claim is scoped to the ASCII tier's constructs:
                                 backreferences under (?i) (module 'backrefs', and the M4 VM
                                 before them) compare captured SUBJECT text at run time and
                                 are where it gets re-examined (D23).
                                 PCREC_EMIT_MAIN: append a standalone main() to the .c. */
    const char *header_name; /* name used in the generated #include "...";
                                NULL = self-contained .c (declarations inlined,
                                h_src not produced) */
    int         engine;      /* [M4.5b] PCREC_ENGINE_* (default AUTO) */
    int64_t     step_budget; /* [M4.5b] backtrack resumptions the emitted VM
                                 will spend before returning <PREFIX>_ERR_STEPS;
                                 PCREC_STEP_BUDGET_DEFAULT / _NONE. A GENERATION
                                 AXIS, not a runtime parameter (D18) — and the
                                 only shape the frozen rx_matchfn signature
                                 leaves open (engine_m4.md §4.6). Ignored on a
                                 DFA artifact, which cannot backtrack. */
    int64_t     work_budget; /* [ENG-BREP counter-K] work units the emitted VM
                                 will spend on forward work the fail label does
                                 not see before returning <PREFIX>_ERR_WORK;
                                 PCREC_WORK_BUDGET_DEFAULT / _NONE. A GENERATION
                                 AXIS like step_budget, and a SEPARATE counter
                                 from it (D47 SECOND ADDENDUM settlement 4):
                                 one unit per frame discarded at a cut, one per
                                 frameless scan iteration. Ignored on a DFA
                                 artifact, which does neither. */
    int         unroll_k;    /* [ENG-BREP] the counter rung's unroll factor K:
                                 one emitted body copy per K iterations.
                                 PCREC_UNROLL_K_DEFAULT (0) = the built-in
                                 PCREC_DEFAULT_UNROLL_K. A TUNING AXIS; one
                                 value per artifact, never per quantifier
                                 (D47 ADDENDUM). Ignored on a DFA artifact and
                                 wherever the counter rung is not selected. */
    int         frame_capacity; /* [M4.5b] <PREFIX>_BT_FRAMES, the resume-stack
                                 capacity (engine_m4.md §4.5's SECOND bound);
                                 0 = let the compiler size it (exactly, where
                                 the pattern's dynamic depth is statically
                                 bounded; the default otherwise). */
    /* [ART-SIZE] THE TWO EMITTED-SIZE CAPS' RAISE-ONLY OVERRIDES (D84 ruling
     * 1; src/core/limits.h carries the defaults and the derivations).
     * 0 = the built-in PCREC_MAX_VM_EMIT_CODE_BYTES / PCREC_MAX_EMIT_BYTES.
     *
     * RAISE-ONLY: a value BELOW the built-in default is refused as a
     * malformed option rather than honoured. A lower cap is not a use case
     * this row has a measurement for, and — the reason that matters — a
     * raise-only flag cannot be used to MANUFACTURE a refusal, so no caller
     * can turn these into a way to make someone else's build fail.
     *
     * The effective values are STAMPED on every artifact
     * (`<PREFIX>_MAX_EMIT_CODE_BYTES`, `<PREFIX>_MAX_EMIT_BYTES`), because a
     * selection fact is unconditional (D81) and a reader of an artifact
     * should be able to see which limits it was built under.
     *
     * WHERE A REAL BUILD SETS THESE is the pattern-source file's `config`
     * block (D84 addendum 3, dd13_format/usecases_and_outline.md §2 wave 3):
     * per target, declared beside the pattern, applied to everything built
     * with that config, and visible to whoever reads the file next. The CLI
     * flags serve the single-pattern case and the test harness. */
    uint64_t    max_emit_code_bytes;
    uint64_t    max_emit_bytes;

    /* [OPT-4] AN ADVISORY SIZE WARNING, and the word advisory is the whole
     * design (Frank, 2026-08-29). When an ACCEPTED artifact's total emitted
     * bytes exceed this, pcrec writes ONE line to stderr naming the size, this
     * limit, and the stamps that explain it — and then returns the artifact.
     * It never refuses, never changes what is emitted, and is not an
     * optimization axis: nothing selects on it and no artifact records it.
     *
     * WHY A WARNING AND NOT A LOWER CAP. The caps above are raise-only
     * precisely so no caller can manufacture someone else's refusal; a
     * lowerable cap would undo that. A warning gives the same early notice
     * with none of the authority — the build still succeeds, so a config that
     * sets it can never break a downstream consumer.
     *
     * 0 DISABLES IT. The default is `PCREC_DEFAULT_WARN_EMIT_BYTES`
     * (250,000 total bytes), chosen an order of magnitude under
     * `PCREC_MAX_EMIT_BYTES` so the line arrives while a pattern can still be
     * changed rather than at the moment it is refused. Unlike the caps this is
     * NOT raise-only: lowering it is exactly what a project that wants tighter
     * notice should do, and lowering a warning cannot fail anyone's build. */
    uint64_t    warn_emit_bytes;

    /* [DD-13b.W1.2] THE ARTIFACT'S NAME — what `rx_info.name` reports.
     *
     * A `.rxt` source's pattern BLOCK may carry a `name`, and a `target`
     * names one; the artifact built from it should be able to say which
     * definition it IS, independently of the symbol prefix a build happened
     * to choose. `prefix` answers "what are my symbols called"; this answers
     * "what am I".
     *
     * NULL MEANS "use `prefix`", and that is the whole of the rule Frank
     * ruled at format_design §6.3: NO ARTIFACT EVER CARRIES A NULL NAME.
     * Every invocation that predates this field — every CLI compile without
     * `--source`, every library caller — therefore stamps its own prefix and
     * needs no edit, and the emitter has no NULL case to get wrong.
     *
     * It is a NAME, not a symbol: it is emitted as a string literal and no
     * generated identifier is derived from it, so it is unconstrained by C
     * identifier syntax. `.rxt`'s own `name` grammar (docs/spec/rxt_format.md)
     * is stricter, and that is that format's rule rather than this field's. */
    const char *name;
} pcrec_options;

/* [M4.4] (subst note §9 Q8, D42.4): which input string pcrec_error.pos
 * indexes into. pcrec_compile()'s error path always sets
 * PCREC_ERR_INPUT_PATTERN today — it has no other input yet; the
 * substitution-template compiler ([M4-SUBST], not yet built) is the first
 * producer of PCREC_ERR_INPUT_TEMPLATE. */
typedef enum {
    PCREC_ERR_INPUT_PATTERN  = 0,
    PCREC_ERR_INPUT_TEMPLATE = 1
} pcrec_err_input;

typedef struct {
    char            msg[256];  /* human-readable diagnostic */
    size_t          pos;       /* byte offset into the input named by `input`,
                                   when applicable */
    pcrec_err_input input;     /* which input string `pos` indexes into */
} pcrec_error;

typedef struct {
    char *c_src;      /* malloc'd; free with pcrec_output_free */
    char *h_src;      /* malloc'd or NULL when options.header_name == NULL */
} pcrec_output;

void pcrec_default_options(pcrec_options *opt);

/* Returns 0 on success (out filled), -1 on failure (err filled if non-NULL). */
int pcrec_compile(const char *pattern, const pcrec_options *opt,
                  pcrec_output *out, pcrec_error *err);

/* Generated searcher contract, RESHAPED at [M4.4] (D44.2, docs/design/
 * match_api_m4.md §1.0) — the prior `<prefix>_span` out-struct form is
 * RETIRED, with no compatibility alias, in favor of a caps-array parameter
 * that is already the FINAL shape (RX_NCAPS simply grows from 1 upward at
 * [M4.5] with no further signature change):
 *
 *   int <prefix>_search(const unsigned char *s, size_t n, size_t startpos,
 *                        ptrdiff_t (*caps)[2]);
 *
 * Searches s[startpos..n) and returns 1 on a match, 0 on no match, or a
 * NEGATIVE typed give-up code when the engine ran out of budget: the
 * artifact's `<PREFIX>_ERR_STEPS`/`_FRAMES`/`_WORK`/`_RECURSE`, all inside
 * [`<PREFIX>_ERR_FLOOR`, -2] (D49; the same code space `<prefix>_match`
 * and `<prefix>_match_caps` return, docs/spec/match_api.md §4).
 * [DD-14 wave A, D71 item 1] `_RECURSE` is RESERVED, no producer today —
 * the recursion-depth counter is a future diagnostic-generation axis, not
 * part of the default artifact.
 * The return is therefore NOT two-valued: `if (<prefix>_search(...))` treats a give-up
 * as a match, and a caller that must not do that tests `== 1` (or `> 0`)
 * for "matched" and `< 0` for "gave up". Values strictly below the floor
 * are reserved for a future abort semantic.
 * [DD-14 wave A commit 2, D71 item 1] `<PREFIX>_ERR_INTERNAL`, below the
 * floor, is that semantic's first producer: it means the artifact caught
 * its OWN analysis/emission inconsistency, never a resource give-up
 * (module 'lookaround''s negative-polarity lookbehind end-check is the
 * one producer today). This entry PROPAGATES it exactly like a give-up
 * rather than trapping on it — trapping is what a COMPOSED call site
 * (one `rx_matchfn` invoking another) must do, not a top-level entry.
 * `caps` may be NULL (existence-only search, today's entire caller
 * population). On a match, if caps != NULL, RX_NCAPS pairs are written as
 * half-open [start, end) byte offsets; caps[0] IS the whole-match span (no
 * second name for it). On no match — and on a give-up, which is a failure
 * for this rule too — caps (if non-NULL) is left UNTOUCHED; the int return
 * value alone communicates the outcome. startpos > n returns 0. `^` anchors
 * to absolute offset 0 regardless of startpos. s may be NULL only when
 * n == 0, and the matcher never reads s[n]. RX_NCAPS is 1 on any
 * DFA-compiled artifact (which is every artifact built `--no-captures`);
 * RX_NCAPS > 1 implies the VM engine ([M4.5], where captures became the
 * default).
 *
 * Every generated matcher also exports, unconditionally: `<prefix>_match`
 * (the `rx_matchfn`-typed match-here entry, anchored at `ctx->pos`, no
 * search loop, no capture output — a length, -1, or a give-up code from
 * the same space as above), `<prefix>_match_caps`
 * (the anchored capture-DELIVERING sibling: same anchoring and same return
 * space, plus a `caps_out` parameter),
 * — and, since [DD-14.FB] (2026-08-25, D71 item 2) — the three
 * CALLER-BUFFER siblings `<prefix>_search_in`, `<prefix>_match_in` and
 * `<prefix>_match_caps_in`, each its un-suffixed twin plus a final
 * `const <prefix>_buffers *`. That descriptor carries `{frames, nframes,
 * trail, ntrail}` — two regions of caller storage and their CAPACITIES,
 * counted in frames and trail entries rather than bytes — and a NULL
 * descriptor is DEFINED to be exactly the un-suffixed call. It exists
 * because a generated matcher never allocates, so the two arrays a
 * backtracking match needs otherwise live on the entry's own stack frame:
 * MEASURED, `<prefix>_search`'s frame is 131,216 bytes on a call-bearing
 * artifact where `<prefix>_search_in`'s is 144. The header also stamps
 * `<PREFIX>_RESUME_FRAMES`/`_TRAIL_FRAMES` (the DEFAULT capacities, not
 * limits), `<PREFIX>_RESUME_FRAME_SIZE`/`_TRAIL_FRAME_SIZE` and
 * `<PREFIX>_BUFFER_ALIGN`, which is the arithmetic a caller needs to turn
 * a reservation into a capacity. All of it is emitted on EVERY artifact,
 * both engines — present and inert on a DFA artifact, whose `_in` entries
 * take a descriptor and ignore it — so a call site does not stop compiling
 * when a pattern selects the other engine. docs/spec/match_api.md §10.
 * `extern const struct rx_info <prefix>_info` (a static
 * reflection structure: option flags, encoding, pattern text, group counts,
 * selected engine, budgets, and — since [DD-13c] — the two SELECTION FACTS
 * `scan`/`prefilter`, the runtime mirrors of the `<PREFIX>_DFA_SCAN` /
 * `<PREFIX>_DFA_PREFILTER` macros for a consumer with no header to read them
 * from; docs/spec/match_api.md §6 states the rule, including what each reads
 * on a VM artifact that is not a §6.1 hybrid), and — since [M5-SEAM] (D58) —
 * `size_t <prefix>_next_pos(const unsigned char *s, size_t n, size_t pos)`,
 * the ENCODING RESIDUAL: the next CHARACTER boundary strictly after `pos`,
 * every position >= n counting as a boundary. It is the ONE place an
 * artifact's byte-vs-character distinction lives, and it is what a find-all
 * loop advances through after a ZERO-LENGTH match (docs/spec/match_api.md
 * §3.1 writes that loop out and §3.1.1 states this entry's contract). Under
 * the byte encoding its body is `pos + 1`; a UTF-8-compiled artifact
 * supplies a boundary-aware body under this same signature, so a caller's
 * loop is written once. Do NOT inline the `+ 1` back: that is the one edit
 * that makes a byte-compiled caller wrong against another encoding's
 * artifact. The fixed-literal ABI types these entries
 * share (`rx_ctx`, `rx_matchfn`, `rx_callout_ref`, `rx_renderfn`,
 * `rx_group_entry`, `struct rx_info`) are declared in the generated .c/.h,
 * not here — they are PER-ARTIFACT-EMITTED, not part of pcrec's own library
 * surface, exactly like `<prefix>_search` itself. The CONTRACT for all of
 * this — every entry point, the give-up codes, capture semantics, the
 * reflection surface — is docs/spec/match_api.md, which is authoritative;
 * docs/design/match_api_m4.md is the design record behind it.
 *
 * The one-shot search form above is the WHOLE generated search contract
 * today. The streaming interface APPROACH.md §6 specifies (<prefix>_stream_init/
 * feed/end) is not emitted yet: it arrives with milestone M3, whose design gate
 * (docs/dev/plan.md, M3.0) owns reconciling that contract with the two-pass
 * engine before any streaming code is written. */

void pcrec_output_free(pcrec_output *out);

#endif /* PCREC_H */
