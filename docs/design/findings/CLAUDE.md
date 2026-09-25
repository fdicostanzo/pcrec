# docs/design/findings/ — the [FINDINGS] row's design documents

The findings-file consumer (D83 + its 2026-09-22 addendum; plan row
[FINDINGS], opened by Frank 2026-09-25): subject-aware compile decisions
read NAMED ANALYSIS VALUES from the shipped default, shipped named
analyses, user-supplied files, or an exemplar analyzer's output, through
ONE accessor. Sequence (Frank): (1) think lane → requirements + questions,
(2) design note, (3) D6 critique loop, then build.

## Files

- `requirements.md` — STEP 1 (lane findthink, 2026-09-25). A thinking
  deliverable, NOT a design: §0 findings, §1 the customers (C1-C11,
  with measured sensitivity), §2 the numbered requirements (R1-R41,
  each sourced and testable), §3 ten questions for Frank with options and
  recommendations, §4 non-goals and risks. Frank answered §3 the same day
  (D123 + addenda 1–7).
- `design.md` — STEP 2, the DESIGN NOTE (lane findesign, 2026-09-25;
  PROPOSED, not yet paneled — the D6 critique loop is step 3). Read §0
  (eleven findings, incl. RUNEST's 2-byte-ppm size claim refuted, `-I`
  refused without a file operand, the include_next self-shadow rule, the
  seam-overlap shard merge) and §1 (the decision table) first. Specifies
  the bundle/kind/query/derivation data model with DECLARED applicability
  (`serves <query> when <enc> via <derivation>`), counts-not-ppm storage,
  the integer normalization and `markov1` run-rarity arithmetic, Route I
  resolution (own source → `-I DIR/<name>.rxt` → embedded store) with the
  built-in `default` as the chain's terminal by identity, the three-call
  accessor and its C1–C11 map, the `<P>_FINDINGS` stamp + FNV digest over
  consumed values (abi 32→33 with the gate move), the text-embedded store,
  the analyzer contract, the test/oracle/sabotage/census plan, the
  B0–B6 build plan, the spec hunks, the R1–R41 disposition and three
  open questions.
