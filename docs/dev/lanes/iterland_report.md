# iterland — the find-all iterator stack, prepared for landing (2026-10-22, sonnet)

Branch `lane/iterland` (worktree `worktrees/iterland`) from main `02f357b39` (abi 83).
NOT merged to main: RX_FOREACH's fate is unruled. STATE: merges and the D94
ritual done and committed; the light sections and the pin re-measure are OWED
(the box was held by the kit's job 600 for the whole lane).

## Merge record

1. `git merge lane/itertri` (8b56b7a7f; carries i1build, i2build, iteropt, iteropt2, the triage re-pins): 21 conflicted files, merge commit `55c757b50`.
   - Makefile: both section lists unioned (main's `test-claudemd-size test-kitproof test-casemap` plus the lane's `test-findall`).
   - `tests/ci/shards.tsv`, `decisions.md`: both sides kept (the lane's i2build Gloss line moved to follow the "Noted for I2" paragraph it glosses).
   - `plan.md`: [M4-SUBST] row from main kept, [FINDALL-NEXT] row from the lane with a one-line landing status (<= 300 chars, plan_lint clean).
   - Ten `CLAUDE.md` files (docs/design, docs/dev/lanes, docs/dev/reviews, src/{facts,gen,ir}, tests, tests/{assertions,codegen,harness}): main de-bulked them, the lane had appended to the pre-de-bulk text. Resolved to main's version; the lane's added lines carried VERBATIM into each directory's `NOTES.md` (new NOTES.md in 8 directories) and one pointer line added to each CLAUDE.md. All within the size limits (`check_claudemd_size` green at commit).
   - abi: see below.
   - `tests/rxtsource/run_rxtsource_tests.sh` census pins and `manifest_s2_vm_forced.tsv`: see "Re-pins owed".
2. `git merge lane/iterdoc` (231364a7a), alone: one conflict (`docs/dev/lanes/CLAUDE.md`, same de-bulk shape), merge commit `934f8bed1`. match_api.md auto-merged.

## ABI: ONE event, 83 -> 84

Main's 83 is lane corefix (K128/K129, renumbered 87 -> 83 at its landing); the
branches' own 83 (I1) and 84 (I2) fold into a single 83 -> 84 event.
`docs/dev/history/abi_changelog.md`: one entry "`rx_info.abi` is `84`" with the I1 part, the I4 part (carrying iteropt and iteropt2) as its sub-items; corefix's entry kept below as "was `83`".

Readers of the number, found by grep (`PCREC_ARTIFACT_ABI|PCREC_RX_ABI_H|ABI_EXPECT|FILEPIN|abi.{0,60}8[34]`), with hit counts after the merge:

| reader | hits | state |
|---|---|---|
| `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI` | 1 | 84 |
| `docs/spec/match_api.md` (guard block, `.abi` row, §6 sentence, mirrored sites) | 5 lines with 84, 0 with 83 | 84 |
| `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` | 1 | 84 |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` BEFORE/AFTER | 2 (+ comment, corefix and iterland RE-AIMED lines) | 84 / 83 |
| `docs/dev/history/abi_changelog.md` | 1 entry | folded |
| `tests/codegen/run_recursion_identity.sh` `FILEPIN` | 1 | re-pinned to `934f8bed1` (the merge; src/lib/cli/memfn identical to the stack's last src commit) |
| `tests/codegen/run_cpset_structure.sh`, `tests/resource/run_resource_tests.sh` | comments naming 83/84 | byte pins inside them are the owed re-measure |

Corefix's own commit (`52f209cb5`) listed five readers (emit_dfa.c, ABI_EXPECT, S693, match_api.md, abi_changelog); all five are on 84, plus the FILEPIN.

The kit's `lane/memfn-s3` also wants 84 provisionally. Whichever lands first
keeps 84; the other renumbers to 85 (the same five readers + FILEPIN, and its
abi_changelog entry).

## Re-pins owed (nothing copied; none yet re-measured)

Main gained, since the branch point, the B4 compound stamp, the K59 rung and a
start-sweep floor change; the lane's pins were measured before them. Each is
re-measured with its own check's `-o` basename, from the red line of the first
run of that check on this tree:

- `tests/rxtsource/run_rxtsource_tests.sh` CENSUS_*/RUNSH_*/C3_*: conflicts resolved to MAIN's values (the lane's `tests/findall/global.rxt` is a new corpus file, so its blocks/lines are not in them). Re-measure from `make test-rxtsource`.
- `tests/startset/manifests/manifest_s2_vm_forced.tsv`: both sides' appended rows unioned (corefix's 34 `empty_iteration.rxt` rows + the lane's 14). Row order and the manifest's own count are re-checked by `make test-startset` (in `make test`, job 602).
- `tests/codegen/run_cpset_structure.sh` and `tests/resource/run_resource_tests.sh` byte pins; the start-sweep floors; the compound B4 stamp pins: owed to the first red of `test-codegen`, `test-resource`, `test-compound`.

## Light verdicts: OWED

Chain `build/il/light.sh` (detached, each stage under `scripts/boxlock run`,
`gnutimeout 3000`): strict, test-findall, test-codegen, test-registry,
test-rxtsource, test-spec-history, test-plan-lint, test-compound.
Log `worktrees/iterland/build/il/light.log`; per-stage logs `build/il/<stage>.log`.
Completion line: `== LIGHT DONE`. It was waiting for the box lock (job 600) when this report was written.
Read the verdict with `scripts/verdict build/il/<stage>.log` (make's `*** [...test-X] Error` lines), not the stage rc alone.
Measured here: `make -j16` builds the merged tree clean; the staged pre-commit checks (plan_lint 194 rows 0 violations, claudemd size) passed on every commit.

## Queued, OWED

- `602-iterland-test`: full `make test` through `scripts/perfrun --label iterland`; ready only after `== LIGHT DONE`; expect `sections=77` (`sections ran: 77/77`, counted from `TEST_SECTIONS` of this tree; main's is 76 plus `test-findall`); cap 3600.
- `603-iterland-mech`: mech S1297-S1321 plus S02 S05 S693 (28 rows, the field validation resolved all ids); ready `after iterland-test`; expect `rows=28 last=^== mech run COMPLETE: `. S1300, S1303, S1309-S1313, S1321 are in the range; S02/S05 were re-aimed by i1tri, S693 by this merge. REACH_ONLY is not run (no new strategy site).
- Status: `scripts/boxqueue status`.

## Next agent (resume from here)

1. Wait for `== LIGHT DONE` (or run the failing stage solo). For each red stage: read the red line, re-measure that pin with the check's own `-o` basename, commit named paths only.
2. Re-run the touched section; if any src moved (it should not), FILEPIN moves to that last src commit.
3. Jobs 602 and 603 follow on their own; read both with `scripts/verdict`.
4. Merge to main only on Frank's RX_FOREACH ruling.

## Triage (iterfix)

Job 602 (`make test`, perfrun `section-errors=1 class=RED-REAL`): the ONLY red section was `test-rxtsource`
(make line `*** [Makefile:593: test-rxtsource] Error 1`); every other section green, so startset
(manifest_s2_vm_forced union), cpset_structure and resource byte pins and the compound stamps were NOT red.
The light chain agreed (only test-rxtsource, rc=2).

| section | class | cause | fix commit | solo verdict |
|---|---|---|---|---|
| test-rxtsource | (a) stale pin | merge took main's census/RUNSH/C3 values; the lane's new `tests/findall/global.rxt` was not in them. Measured from the check's own output: +1 file, +62 blocks, +1404 lines (CENSUS 293/6038/73976, RUNSH 269/6038/73976); C3 PASS +1188 (21932), SKIP +216 (51958), pcre2-only +216 (19373), verifiable +1188 (24164). The W23-S7 corpus control, the case-row derivation and the C3 reconciliation (21932+51958-3+89=73976) all follow from these pins. | the commit "iterland: re-pin rxtsource census/RUNSH/C3 for tests/findall/global.rxt" on lane/iterland | OWED: `build/il/fix-rxtsource.log` (detached, waiting on the box lock behind queue job 604-kit-s3-heavy); read with `scripts/verdict`. |

Not re-pinned (not red, nothing measured): C3_FILES, the five golden findings files' HARNESS FAILURE lines (the known unparseable-head set, printed by the W23-S7 control as before).
