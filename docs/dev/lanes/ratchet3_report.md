# ratchet3 report: A-REV ratchet rows restated, [GIVEUP-DIFF] widened

Docs only. Lane ratchet3 (sonnet), branch lane/ratchet3 from main 60b130fb4.

## Premise test
Confirmed before editing: roadmap §5 carried R03 (`src/opt/revdet.c` present: 1) and R10
(`emit_landmark_walk` present: 1) with the old name-counting recipes, and no R28 row, as arev.md
§4.3 and "Recipe words, rev 2" say.

## What changed
- `docs/design/stream/roadmap.md` §5: R03 → R03', R10 → R10' (old ids named in the id cell), new row
  R28'; recipes as arev §4.3 / rev 2 words. A dated paragraph after the baseline paragraph
  ("2026-11-06, restated by re-definition per arev §4.3; manager"): total 29 → 36 (R03' +2, R28'
  +5, R10' unchanged at 1), a re-definition and not a step.
- `docs/design/stream/roadmap.md` §3 A-REV: the "Parallel mechanisms" bullet and the S1 prerequisite
  now say the §5 restatement is DONE.
- `docs/dev/plan.md` [GIVEUP-DIFF]: status, trigger and refs lines only; trigger widened to the
  variable-lookbehind hand-off row (arev S3: `--harness=` arm, ONE_WAY declared on the arm's job,
  witness HO-V). `timeout 120 scripts/plan_lint.sh`: 299 rows parsed, 0 violations.
- History index line appended to `docs/dev/history/claude_md/docs__dev__lanes.md`.

## Recounts at 60b130fb4 (file: src/gen/emit_dfa.c unless noted)
- R28' (i): `grep -c '^static const DfaDir [a-z_]* = {'` = 5 (the forward declaration
  `static const DfaDir dfa_dir_forward;` does not match); run-time copy
  `grep -n '^ *DfaDir [a-z_]* *= *dfa_dir_'` = 1 (line 14700, `pcrec_emit_dfa_retry`); 5 + 1 − 3
  directions = 3. (ii): `emit_rev_end_one_seed` (14022) and `emit_rev_end_tagged` (14081), called from
  `emit_rev_end`, with seed code outside `emit_reverse_block`: 2. Total 5. Matches arev.
- R03': by reading the loop-printing lines: `emit_rev_end` (`for (int revend_seed`, 14306),
  `emit_landmark_walk` (`for (;;)`, 14483), `vm_revdet_rep` in `emit_vm.c` (backward `vm_goto(v, walkl)`,
  5925-5940): 3. Matches arev.
- R10': `awk 'NR>=14398 && NR<=14560 && /for \(|while \(|goto /'` over `emit_landmark_walk`: one loop
  (`for (;;)` at 14483) and a `} while (0);` scaffold at 14504 that closes a `do` and is not counted:
  1. Matches arev.

No count differs from arev §4.3.

## Weakness recorded (STOP RULE)
R10' as rev 2 words it counts loop constructs in the emitter's own body AND its static callees. Read
literally that over-counts: callees `emit_scan_loop` (`for (;;)` at 13289, `goto` at 13282/13286/13389)
and `emit_reverse_block` (`while (` at 13606) print loops too, giving at least 3 at today's HEAD, and
those are the shared renderers the end state keeps. I kept arev's words but wrote into the roadmap row
that the shared renderers are not counted and the callees are "the helpers only it calls". The
manager may prefer to move that exclusion into arev §4.3 (not edited here). Also, the R03'/R10'
recipes remain judged by reading the printed loop lines, not a single mechanical grep; no
rename-proof one-line grep exists for them.

## STATE AT HANDOFF
Committed on lane/ratchet3; docs only; rulings file empty/absent entries (none applied). No
`_deliver.txt` existed for this lane. Nothing owed.
