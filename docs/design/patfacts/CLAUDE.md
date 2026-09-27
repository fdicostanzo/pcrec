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
- `design.md` — STEP 2, THE DESIGN (lane pfdesign, 2026-09-26, PROPOSED,
  awaiting its D6 panel): lazy memoized accessors over `Job.pf`, sealed
  at three epochs (E1 structural / E2 lowered / E3 NFA); core vs derived
  facts; one owner per derivation with `src/opt/facts.c` holding only
  memo + epoch guard + deny; the encoding rule (no fact reads the
  encoding enum; the prior's NONE answer spelled once per QUESTION KIND
  inside findings primitives, amending `findings/design.md` §6.1-§6.3);
  the deny story (fact denies are "nothing to find" for every consumer,
  row denies are rows); the first customers ([FINDINGS] B1 = the data
  tier; `[OPT-LITSCAN]` S2a = one node-grain literal-run fact; S2b
  carried facts specified, not built); the step-3 migration order with
  the gate and abi status of each step; §10 not-built with triggers;
  §11 seven questions for Frank.

STEP 3 (implement-then-replace, migrating existing analyses one at a
time under the identity gates) is a later plan-row step, sequenced by
`design.md` §9.

Maintenance: update this file when a STEP 2/3 design note is added.
