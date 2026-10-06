# Confirmed verdicts (charter 3.2; confirmer lane artconf, 2026-10-06)

Linux (ubuntubudu, gcc 15.2 -O2), pad-controlled, vs original, cell median. Artifact knowledge only.
Format: artifact:lead | verdict | effect | note.

- loglines_stack_frame:L1 (scan the rarer required byte '(' and walk back over the identifier run) | WIN | -72% (cell), also dense/sparse | held up; biggest effect, all 7 pads agree.
- loglines_stack_frame:L2 (memchr 't' at offset 1 instead of 'a') | NOISE | -15% below threshold, pass 1 only | superseded by L1; real but small.
- loglines_stack_frame:L3 (backward scan instead of reverse DFA) | NOISE | cell -8%; dense subject WIN | only helps when many matches; layout spread as large as the effect.
- loglines_stack_frame:L4 (skip the first re-skip at the handoff) | NOISE | +8% slower, below threshold | not worth carrying.
- capability_doubled_word:a_L1 / b_L1 (start only at word starts) | WIN | -22% | both reviewers' versions equal.
- capability_doubled_word:a_L2 / b_L2 (drop the two give-back frames) | WIN | -35% | needs possessive reading; changes give-up behaviour (5,380 repairs).
- capability_doubled_word:a_L3 / b_L3 (straight-line / untrailed slot writes) | WIN | -51% / -42% (stacked on L2) | give-up behaviour changes (294,884 repairs).
- capability_doubled_word:a_L4 (fused word walk) / b_L4 (+ inline matcher) | WIN | -80% / -71% (stacks) | the largest effects of the pilot; stacks.
- capability_doubled_word:b_L5 (restart past dead spans) | WIN | -74% stack, increment over b_L4 about 3 points | small on top of the filter.
- capability_doubled_word:a_L5 / b_L6 (256-byte class tables) | WIN as stacks | -83% / -74% stack; increment over the stack not isolated (a_L4->a_L5 3.48->2.89, b_L5->b_L6 4.57->4.48) | likely small.
- capability_doubled_word:a_L6 (run counters in locals) | NOISE | -0.05% cell; ~+2% on dense/sparse/t1m | small, consistent sign; below the cell threshold.
- capability_doubled_word:poss (the pattern spelled possessively `\b(\w++)\b\s++\1\b`, the emitter's own output) | WIN | -58% | reaches most of the L2+L3+inline effect without hand edits.
- loglines_level_context:L1 (skip the {0,29} component with two memchr streams on rare bytes) | WIN | -95% | held up; all pads agree.
- loglines_level_context:L2 (same skip as a scalar 256-byte table loop) | WIN | -76% | weaker than L1 but no libc dependence.
- loglines_level_context:L3 (after-level exit table) | NOISE | -2% cell; dense +6% | layout spread 20% of orig; hit-only.
- loglines_level_context:L4 (skip the VM when the window is the answer, r3) | LOSS | +23% slower on cell and sparse; dense -47% faster | regime-dependent: wins on hit-dense text, loses on fail/syslog where the added check costs.
- loglines_level_context:L5 (frameless lazy step) | NOISE | cell -1%; dense +21% | helps only when hits dominate.
- loglines_level_context:L6 (combination of L1 r2, L3, L4 r3, L5) | WIN | -95% | equals L1 on the cell; L4's cell loss is hidden by L1.
