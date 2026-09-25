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

STEP 2 (the design, through the four evaluation lenses, memory
`pcrec-design-evaluation-lenses`) and STEP 3 (implement-then-replace,
migrating existing analyses one at a time under the identity gates) are
separate, later plan-row steps — nothing in this directory yet designs a
`PatFacts` record's shape; `inventory.md` is read-only evidence for STEP 2
to consume.

Maintenance: update this file when a STEP 2/3 design note is added.
