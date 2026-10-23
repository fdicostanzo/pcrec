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

## Macro removal (nomacro)

Lane nomacro (sonnet), 2026-10-23, Frank's ruling: `RX_FOREACH` dropped, `_next` / `_next_n` and `rx_info.next` / `rx_info.next_n` stay (D175). abi stays 84 (the event is unlanded; its changelog entry is amended).

**Sites changed.** Emission: `src/gen/emit_iter.c` (the whole RX_FOREACH block: `RX_FOREACH_PAIRS`, `rx_foreach`, `rx_foreach_begin`, `rx_foreach_pull`, the macro; `rx_nextnfn` stays, it types `rx_info.next_n`). Spec: `docs/spec/match_api.md` (contents entry, §1¶5/¶6, the §2 listing, §3.1.3, §3.8.2 rewritten as "Looping over any artifact's record" with a loop for `info->next` and one for `info->next_n`, §4 table and ¶9a, §6¶14c; anchors `s3-8-2` and `s3-8-2-p1..p4` kept, the old p3-p5 content gone and no citer left). Tests: `tests/findall/iter_drv.c` (F, Fstop, Fcount, Fabi cells replaced by `g1_drain` / `gn_drain` plain loops over the record, cells G1 and GN), `run_iter_diff.sh` (REACH_NEED), `run_findall_tests.sh` (ASan build loses `-DRX_FOREACH_PAIRS=8`), `cells.tsv` comment, `tests/encseam/findall_driver.c` (a plain `fa_info.next_n` loop), comments in tests/assertions, tests/codegen, tests/resource, CLAUDE.md/NOTES.md of src/gen, tests/findall, tests/encseam. `run_facts_checks.sh`: `FOREACH` removed from MACHINERY. Docs: decisions.md D175; abi_changelog.md 84 entry amended; plan.md [FINDALL-NEXT] row; `findall_iter_i2.md` gets a superseded-in-part banner; the twin harness `docs/design/findall_iter/twin/` keeps its F/Fb arms as the evidence behind D175 (they need a pre-D175 compiler; noted in its CLAUDE.md), `tdrv.c`'s stride probe now `-DNN_STRIDE_ONE` instead of `#ifdef RX_FOREACH`.

**Rows retired** (git-deleted, the S293/S1421 precedent): S1315 (doubling), S1316 (brk), S1317 (kmax), S1318 (abi unchecked), and S1320 (refills early; also macro-only, not named in the brief). S1314 (`rx_info.next_n` NULL) stays, re-aimed: its witness is the info arm plus GN, the plain `next_n` loop, reach token `g1`. VALIDATE_ONLY on S1314: valid.

**Pins moved** (each from the check's own output):
- reach tokens (`run_iter_diff.sh`, `run_findall_tests.sh`): `f1 f2 fstopend fcount2 fcount63 fabi kmaxcap frefused` -> `g1 g2 gn5`; test-findall prints `reach n3m4=72 split=118 g2=144` (ASan run), green.
- `tests/codegen/manifests/m5_stage1_stamps.tsv` (test-cpset-structure check [3]): all twelve EMITTED_BYTES rows -2,686 (uniform; no other row moved), now 29 checks pass.
- `tests/codegen/run_recursion_identity.sh` FILEPIN (the (B) pin): 934f8bed1 -> 24d2888f5 (this lane's src commit; the manager re-pins to the merge).
- abi number readers: none move (84 stays); test-codegen 331+ checks green, abi 84 sentences intact.
- `tests/resource` byte pin: unmoved (the macro was in the .h, the pin counts the .c); test-resource 42 green.

**Commits:** 24d2888f5 (removal, tests, spec, decisions), 351f30ff7 (manifest re-record, FILEPIN).

**Validation run by this lane:** make -j16, make strict, test-findall, test-encseam, test-codegen, test-registry, test-plan-lint, test-spec-history, test-claudemd-size, test-cpset-structure, test-entry-shape-identity, test-resource: green. Queued, not run: iterland-test, iterland-mech (see the handback).
