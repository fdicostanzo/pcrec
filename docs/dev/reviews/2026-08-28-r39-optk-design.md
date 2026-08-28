# r39 — D6 critic panel on the [OPT-K] DESIGN NOTE (docs/design/offset_k_skip.md at lane/optk d13f5be), before the emitter side

Three read-only critics, no make: critic-sem (opus; semantics + answer
identity — REPORT PENDING at the time of this skeleton), critic-cost
(sonnet; cost model + numbers — transcribed prefix_k.c's model_cost into
python, reproduced §4.7's 20/372/6,037 ppm exactly, then substituted
MEASURED byte frequencies over bench/loglines 163,048 B / 112 subjects
and bench/email 42,653 B / 85), critic-arch (sonnet; architecture fit +
process obligations — verified against the lane's LIVE uncommitted
emitter, which already existed point-for-point during the review).

VERDICTS SO FAR. arch: the design fits — a genuine SELECTION over
[ENG-FORM]'s candidate lists (dfa_pfs[] gains two entries at the head,
the five k=0 forms unchanged byte-for-byte, emit_scan_loop untouched,
one new `emit_block` slot on the existing DfaPf); `Nfa.anch_start` in
the IR layer, set once in pcrec_build_nfa, is the right home; D83's
hook (static table, findings file named-not-built) and the D66 answer
(A_LOOK lowers to N_EPS on this NFA — nfa.c:621 — so the walk cannot
see a lookbehind's bytes today) both hold. cost: NO WRONG-SELECTION
found on any population tried (real loglines/email frequencies, an
adversarial dense-UUID subject with `-` at 10.8 %, hex32-id stays
declined at 0.82-1.25×); what fails is the note's arithmetic hygiene.

## Findings and triage

| # | lens | severity | finding | disposition |
|---|---|---|---|---|
| A1 | arch | MISSING-OBLIGATION (confirmed) | §5.1/§6.2 claim the `-fno-offset-skip` build is BYTE-IDENTICAL to the pre-row compiler's output; false by D81 (selection facts are stamped unconditionally — `_DFA_PREFILTER_OFFSETS "none"` on every abi-9 DFA artifact). Foreseeable at design time; already corrected in the lane's uncommitted tree | ACCEPTED → optk: the note of record says "differs by exactly one stamp line" and states what the control proves (answer identity + loop objdump equality) |
| A2 | arch | MISSING-OBLIGATION (in progress) | structural check `tests/codegen/run_offset_skip.sh`, the tests/mech sabotage row, and abi site 4 (run_recursion_identity.sh FILEPIN re-pin) not yet in the tree; sites 1-3 landed live | ACCEPTED → landing bar, before delivery |
| A3 | arch | LAYERING nit | prefix_k.c `wclose` and dfa.c `clo_walk` are two hand-maintained exhaustive NKind switches (different semantics — sound over-approximation vs exact context-parametrized closure — so NOT a parallel mechanism), nothing keeps them in sync on a new NKind | ACCEPTED → a line in the note naming the pairing; a shared NKind-count guard if cheap |
| A4 | arch | nit | walk-termination-on-accept re-derives a min-width-adjacent fact mrl.c's pcrec_minw computes over the AST for the VM | NO ACTION (different representation, different consumer) |
| C1 | cost | MODEL | three inconsistent "predicted gain" numbers for the same rows: §4.5 19×/31×/3,600×; §4.7's ratio column is a candidate-MASS ratio (40,350×/201×/134×); model_cost(base)/model_cost(new) — what the materiality check tests — is 192×/38×/23× (static table) | ACCEPTED → one formula; relabel §4.7's column; §4.5 and §7 quote the model_cost ratio |
| C2 | cost | MODEL | the static prior is 3-12× off on the load-bearing bytes vs real log text (digits 265,848 ppm measured vs 74,760; `-` 17,927 vs 4,984; `t` 27,200 vs 60,061); selection survives (78×/25×/44× with the measured table) but §4.3's sensitivity grid never sweeps the PRIOR | ACCEPTED → add the prior sweep (measured-loglines table as a SECOND prior, sensitivity only; the shipped table stays static per D83/learnings §3) |
| C3 | cost | MODEL | C_ENTER = 10.7 cycles (measured, opt3) × "~2 bytes a false start survives" (uncited) is labelled MEASURED | ACCEPTED → measure false-start survival on the three exercising patterns or drop the label and state the band |
| C4 | cost | DESIGN | for `\b`-prefixed patterns the walk computes S[0] (stack-frame: literal `a`, 33 K ppm) and discards it; the offset-0 verify keeps only the 63-byte escape set. §5.4 needs the escape set for termination, but a tighter ADDITIONAL k=0 verify is one more (k, set) member | ACCEPTED as a question → optk evaluates under the model; include if material, else record why |
| P1 | cost | PLAN | §7.1 names no number to hold the timing run against — a 5× real gain on a 23× prediction would pass every stated check | ACCEPTED → state the model_cost prediction per exercising row (static and measured prior) with a tolerance before measuring |
| P2 | cost | PLAN | load discipline inherited by reference only; the box carries lanes today (load1 1.06-1.66 observed during the review) | ACCEPTED → restate in §7.1 (idle box, taskset, load1 per row) |
| P3 | cost | PLAN | no artifact-size estimate for the accessor block + stamps; abi 7 overshot its own +5 KB estimate 6× | ACCEPTED → one-line estimate before the bump, checked after |
| C5 | cost | nit | C_VERIFY (250) honestly unmeasured; the per-candidate bounds check is not in the model | NOTED (rare path) |
| — | cost | unverified | §4.3's 1,352-pattern C_ENTER sweep counts (11/33/120 changing k-set) — plausible, not reproducible without make | NOTED |

Sent to optk as change requests 2026-08-28 ~13:5x (message id 2e57c580).
critic-sem's findings are appended below when they arrive.
