# Lane substland: bring compiled substitution up to main (STOPPED at step 2/3)

Lane substland (opus), 2026-10-24. Branch `lane/substland`, from
lane/substext (c016116cf). Plan row [M4-SUBST]. BUILD GO: Frank 2026-10-23
"go still stands", 2026-10-24 "Proceed on your list" (merge, conflicts,
re-pins, owed items only).

## STATE AT HANDOFF

- **STOPPED by the stop rule:** a conflict needs a design choice (below,
  "The stop"). Steps 3 and 5 are not done; no queue job was added, since
  `make test` on this tree is red for that one cause.
- Commits: b1c362a9c (merge lane/subst's 511081298), c2e287ee7 (WIP merge of
  main 6ec3a2108, committed with `--no-verify`: its one pre-commit fail is the
  dangling cite named below), and this report.
- Rulings file `docs/dev/lanes/substland_rulings.md`: empty at every
  checkpoint; no ruling applied.
- Premise test held: `git rev-list --count main..lane/substext` = 43, and
  lane/subst's only commit outside substext is 511081298.

## Merge record

`git merge main` (main at 6ec3a2108) gave 18 conflicted files. All were
resolved by mechanism. The branch carried a PRE-landing copy of lane/i2build
(lane/subst was cut from it), while main landed the iterators later through
lane/iterland. So iterator-area text takes main's side throughout:

| file | resolution |
|---|---|
| Makefile (2 hunks) | branch side (main's lists plus `test-subst test-subst-d27`) |
| tests/ci/shards.tsv | main's order, plus the two subst rows |
| tests/codegen/run_codegen_tests.sh, run_facts_checks.sh | main (D175: K80-c awk on the real abi; no `FOREACH` in MACHINERY) |
| docs/design/CLAUDE.md, findall_iter/CLAUDE.md, dev/lanes/CLAUDE.md, dev/reviews/CLAUDE.md, src/gen/CLAUDE.md, tests/codegen/CLAUDE.md, tests/encseam/CLAUDE.md | main (the branch side was empty or the pre-landing text) |
| docs/dev/decisions.md, docs/dev/plan.md | main (the branch side was empty or the pre-landing status) |
| docs/dev/history/claude_md/docs__dev__lanes.md | both (the substext line, then main's) |
| docs/dev/upstream_issues.md | both: main's U21, then the branch's U22 |
| docs/spec/match_api.md | §3.8¶2a takes main's rewritten paragraph (it covers the same ill-formed-subject topic); the error table takes main's −10 row plus the branch's −11…−16 subst row |
| tests/rxtsource/run_rxtsource_tests.sh (5 hunks) | main (294/6048/74005; `make test-rxtsource` green on the merged tree, so the branch adds no census file) |
| tests/startset/manifests/manifest_s2_vm_forced.tsv | main |

One auto-merged file was also wrong: `S1306_rx_info_next_null.sh` kept the
branch's stale anchor. It now takes main's, which matches emit_dfa.c.
src/gen/CLAUDE.md went over its 12 KB limit with the emit_subst.c entry. The
entry is now one index line; its text moved to src/gen/NOTES.md.
`check_claudemd_size.sh --all` passes: 328 files.

After the merge: `make -j16` and `make strict` are green.

## ABI check (step 2): the claim holds

The substext report did not record its 11 patterns or 4 flag sets, so the
patterns could not be repeated. The method was repeated instead, with
BASE = main's tip. Main 6ec3a2108 was built from `git archive` in the
scratchpad, and this branch's `build/pcrec` was compared with it over:

- 11 patterns: `a(b|c)+d`, a 3-group date, two named groups,
  `foo|bar|baz`, `^\s*(\w+)\s*=\s*(.*)$`, `(a+)+b`, `[^,]*,`,
  `(?i)hello world`, `\bword\b`, `x*`, `(a)|(b)(c)?`;
- 4 flag sets: none, `-e utf8`, `--engine=vm`, `-e utf8 -i`, all with
  `--features all`.

Result: **44 compiles, with the `.c`, `.h` and stderr byte-identical.** The
same script did catch a difference: on its first run the two arms wrote
different file names, and every compile differed in its `#include` line.
**No rx abi event.**

## The stop: D175 dropped RX_FOREACH, and the subst module depends on it

Main dropped the `RX_FOREACH` family (D175, 2026-10-23), including
`RX_FOREACH_PAIRS`. The subst branch still uses it:

- **The product.** In `emit_subst.c`, the support unit's
  `rx_subst_replace_all` sizes its stack batch with `RX_FOREACH_PAIRS`. It
  also refuses with MISMATCH when one match has more pairs than that. The
  support unit no longer compiles as an implementation TU (`'RX_FOREACH_PAIRS'
  undeclared`).
- **The contract.** `subst_api.md`:
  - §1¶3: "`RX_FOREACH` comes with any subst header".
  - §4¶1a.
  - §6¶5: the RX_FOREACH recipe.
  - §10¶6a and §10¶7: the batch bound and the MISMATCH rule are stated in
    terms of `RX_FOREACH_PAIRS`.
  - `match_api.md` §3.8¶9a (the branch's own hunk) names `RX_FOREACH` as a
    shared reader.
- **The checks.**
  - The subst driver's `fe`/`foreach` arm and the `pairs` arm.
  - run_subst_tests.py: it cites the retired §3.8.2¶5, which is
    test-spec-history's only fail.
  - examples/subst `each()` (§6¶5).
  - In the D27 corpus: `cli/inc_body.c` (RX_FOREACH with any subst header),
    `cli/cli.sh` (`foreachpairs.*`), `api/t_glue.c` and `lib/diff_driver.c`.
  - S1500 (its anchor and description).

Light sections on the merged tree:

- Green: strict, test-registry, test-plan-lint, test-ci-shards,
  test-claudemd-size, test-casemap and test-rxtsource.
- test-spec-history fails once: the cite above.
- test-subst: 1071 passed, 6 failed. All six are driver and support-unit
  builds, and every compiler error is RX_FOREACH, RX_FOREACH_PAIRS, or what
  follows from them.

**Why this is not mine to do.** Replacing the bound needs choices:

- a NAME for a caller-overridable support-unit macro (D174 applies; substb2
  retired `PCREC_SUBST_PAIRS` in favour of `RX_FOREACH_PAIRS`);
- what replaces the §6¶5 recipe: a `— retired` stub, or an `info->next`
  loop per D175's generic-loop rule;
- re-tagging D27 expectations.

All of these are contract changes.

**Leaning, offered for the ruling:** keep every answer as it is.

- Give the support unit its own `#ifndef` bound with a behaviour-named
  macro, default 256, so the same MISMATCH rule holds.
- Restate §10¶6a/¶7 in terms of that macro.
- Rewrite §6¶5 as the `rx_info.next` loop that D175 names. The arm and the
  example follow it.
- Reword §1¶3, §4¶1a and match_api §3.8¶9a.
- Re-tag the four D27 cases with reasons.
- Re-anchor S1500.

The support unit's text, and so its content id, changes. No rx byte changes,
so there is no rx abi event (substb2's position).

## Re-pins (step 3)

Not done: they depend on the ruling above.

## OWED items of substext (step 4)

- **Verdicts of 340-343-substext:**
  - 343 (mech) was cancelled by hand.
  - 342 (`make test`) is GREEN at c016116cf (wall 1370 s). This is the
    re-run after substtri's composed.rxtin fix.
  - 596-substext-mech is GREEN at c016116cf: `== mech run COMPLETE: 54 rows
    (unexpected: 0, undetected: 0, unreached: 0, ...)`.
- **definitions.c verdicts:** S334, S336 and S1195 (every row on
  `src/parse/definitions.c`) ran in 596 and are DETECTED. They are cleared
  on the old base.
- **S1381:** DETECTED in 596. Cleared on the old base.
- **OWED 5 / the composed cell:** S1538 is DETECTED in 596. The `composed`
  cell runs in test-subst, and 342 is green. Cleared on the old base.
- **D27 for the extended forms** cannot be cleared by a merge lane. It needs
  a blinded author (a cell).
- On the merged tree, all of the above must run again. That is the planned
  `611-substland-mech`, after the ruling.

## Queued jobs

None. 610-substland-test and 611-substland-mech were not queued. A full
`make test` on this tree would be red for the known cause.
