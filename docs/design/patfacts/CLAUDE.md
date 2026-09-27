# docs/design/patfacts/ — [PATFACTS] (D120) design record

D120 chartered ONE ORGANIZED PATTERN-ANALYSIS RECORD, replacing the ad-hoc
per-pass walks and cross-file reaches every per-pattern analysis in the
tree uses today. This directory holds the plan row's own record, one file
per step.

## Files

- `inventory.md` — STEP 1, the INVENTORY (lane pfinv, 2026-09-25,
  read-only): every per-pattern analysis found in `src/opt/`, `src/ir/`,
  and both emitters (`src/gen/emit_dfa.c`, `emit_vm.c`) — file:function:line,
  the question it answers, the tree level/pipeline epoch it walks, where its
  result lives, every consumer, and its encoding dependence — plus the
  redundancies (D120's two named incidents confirmed, ten more found), the
  ordering dependencies (the full pipeline re-derived directly from
  `src/core/compile.c`, not merely quoted from prose), and the enumerated
  (not designed) requested facts of the three incoming customers named at
  charter time: [OPT-LITSCAN] (D122(3)'s "carried verified facts"), [VAR]
  (`variables_pattern.md` §2's five neutral-element analyses), and
  [FINDINGS] (recorded honestly as requested-but-undesigned — its own plan
  row is still at the think-lane stage).

  **Delta 2026-09-26** (appended by lane pfdesign, step 2's refresh):
  the facts K64/K65/K66, S1 steps 1-6 and `[OPT-REQRUN-ENC]` added or
  moved (N1-N9); the new redundancies R13 (the `[OPT-REQRUN-ENC]`
  incident: two copies of the prior's non-byte decline, `rb_pick` vs
  `rn_scan_index`, that diverged), R14 (the k-set walk re-run per
  admission ask), R15 (one fact-deny, several consumers, one name); and
  the positive precedents S1 added (`OfsTest`, `req_run_tests`).
- `design.md` — STEP 2, THE DESIGN (lane pfdesign, 2026-09-26, PROPOSED;
  **REVISION 2** the same day, lane pfrev, after the D6 panel r1,
  `../../dev/reviews/2026-09-26-r1-patfacts-design.md`. Every FIX row is
  applied and marked `[r1 ID]` inline, and the revision log at the top lists
  what moved). The design: lazy memoized accessors over `Job.pf`, sealed at
  three epochs. E1 (structural) is FORCED eagerly at its seal, because
  `pcrec_lower_enc` rewrites in place. E2 is the lowered tree. E3 (the NFA)
  is sealed PER BRANCH, only where the forward NFA is wrapped, with named
  declines on `ENG_ATTEMPT` and the no-DFA route. Other topics: core vs
  derived facts; the encoding rule (derivations take the encoding DESCRIPTOR
  as a declared input; the prior's NONE answer is spelled once per QUESTION
  KIND inside findings primitives, amending `findings/design.md`
  §6.1-§6.3); fact vs row denies; the first customers ([FINDINGS] B1, with
  step 3.0 a hard prerequisite; `[OPT-LITSCAN]` S2a, which exercises no
  record machinery; S2b specified, not built). **Revision 2's largest change
  answers Frank's relocation question: the PROPOSED layout is an ANALYSIS
  LAYER, `src/facts/`** (§4.2). It has one file per fact family, a consumer
  header `facts.h`, and a facts-private `facts_derive.h` split out of
  `core/internal.h` first. Five carve-outs apply: decisions stay in their
  passes, rate readers go with B1's primitives, and each relocation rides its
  own migration step, one per commit. An include-graph plus link-symbol
  check with a generated target list replaces revision 1's grep. The
  residual it cannot catch, a hand re-spelling, is stated. §9 is the step-3
  migration order (3.0a is the `internal.h` split; 3.4 is flagged a possible
  mover), and §9.1 classifies movers as SEMANTIC (a K-row) or SCAFFOLDING
  (the D76 ritual). §10 lists what is not built, with triggers. §11 is the
  inspection surface `--emit-facts` (Frank's 2026-09-26 scope addition: a
  debug listing under a spec page, one printer reading the memo, fact stamps
  sharing its renderers, a guarded force loop that never refuses a compile,
  four checks with independent oracles). §12 has eleven questions for Frank,
  Q11 being "adopt the `src/facts/` layer".

STEP 3 (implement-then-replace, migrating existing analyses one at a
time under the identity gates) is a later plan-row step, sequenced by
`design.md` §9.

Maintenance: update this file when a STEP 2/3 design note is added.
