# r30btri: triage of job 697-kit-r30b-heavy (READ-ONLY; no make, no builds, no edits)

Job dir: `worktrees/.boxqueue/failed/20261031T161424.705582682-697-kit-r30b-heavy/` (result: `outcome=failed rc=1 wall=8136s verdict=RED`, `population: steps ran=9 declared=13 SHORT`).
Logs (all under `worktrees/r30b/build/r30b/heavy/`, cited below as `codegen.log:N` etc.). Tip measured: 5a150b93e.
Everything marked (inference) was not reproduced; the one probe I ran (S1760/S1761 reach commands against the worktree's `build/pcrec`, into scratch) is stated where used.

## Summary

Four red steps, FIVE distinct findings. None is a defect in R-30's emitted code or its answers: the census (`census.log`: "census COMPLETE: 0 unexpected", every arm `unexpected=0`), axes_lever, registry, rxtsource and the 75 measured mech rows are green.

| red step | failing check | class |
|---|---|---|
| codegen (rc=2) | `[OPT-LITSCAN S4 C3] '(x?)(?i:abcdefghijkl)\1'` expects an `rx_reqrun` block that R-30 deliberately removed | (b) expected move, not re-pinned |
| memfn (rc=2) | `test-memfn-guarded`: `population simd-form: 5 below its floor 6` | (b) expected move (the same pattern), floor not re-pinned; main already restructured this check |
| test (rc=2) | the same two, plus `test-compound`: G7 lever fence (c) mention of `--harness=` in the new plant S1548 | (b)/(e): two repeats of the above, one new allowlist miss |
| reach (rc=1) | S1760-pin-compare-skipped, S1761-pin-last-link-only read `reach:MISSING(1/1)` | unexplained; not R-30's files (e), probably (c); 15 declared-UNREACHED rows are the standing set |
| (mech, rc=0 but not clean) | S678 ANOMALY: its plant does not compile (`rx_class_bitmap1 defined but not used`, -Werror) so it was NOT measured | (e) stale/unclean plant, not shown to be R-30's |

Merging main (abi 93, K134 trail compaction, simdset, VMREC) changes the picture: see "Does merging main change it".

## Per red step

### codegen (`make test-codegen`, rc=2)
- Verdict line: `codegen.log:1000` `make: *** [Makefile:678: test-codegen] Error 1`. `codegen.log:999` "run_group: 18/19 scripts passed"; the one failing script is group 0 (`codegen.log:362`).
- Only FAIL in the log: `codegen.log:289` `FAIL: [OPT-LITSCAN S4 C3] '(x?)(?i:abcdefghijkl)\1': REQ_WHY emitted with a run, but no rx_reqrun block`; `codegen.log:361` "checks failed: 1".
- Source of the check: `tests/codegen/reqcube_check.py:262-265` (`if run and why == "emitted": b0 = block(text, "rx_reqrun"); if b0 is None: bad(...)`). The witness is the `k66` entry, `reqcube_check.py:221`.
- Cause: R-30 removes the window part `rx_reqrun` (and its entry call) wherever the whole run `rx_reqrun_whole` is verified (`r30b_report.md:47`, `:130-133`: "no `rx_reqrun(`", "`rx_reqrun_whole(` kept"). `(x?)(?i:abcdefghijkl)\1` is a census mover in every arm (`census.txt` MOVED lines, c-default/c-simd/c-vm...). The check at `reqcube_check.py:262-265` still assumes every `emitted` run has a window block. The very next lines (266-277) already handle the whole block, and the same file's pass lines show `rx_reqrun_whole` present for this pattern (`codegen.log:290-292`).
- The remaining checks of the pattern (REQ_BYTE, REQ_WHY consistency, the whole block's pair streams and words) all PASS, so the new form is structurally right.
- Class: (b). The lane's report line 169 claims a probe of "71 presence/handoff/k66/reqcube patterns", but the `reqcube_check.py` population was not run through `test-codegen` before delivery; this section is run only inside `run_codegen_tests.sh:3906`.

### memfn (`make -k -j16 -Otarget test-memfn-*`, rc=2)
- Verdict line: `memfn.log:202` `make: *** [Makefile:1470: test-memfn-guarded] Error 1`. All other 14 groups pass (`checks failed: 0` at memfn.log:22,35,...,315; `test-kitproof` K1 passed 411620 failed 0 at `memfn.log:398`).
- FAIL: `memfn.log:198` `FAIL: population simd-form: 5 below its floor 6 (a reader this check needs is unreached)`; "checks passed: 9 / failed: 1" (`memfn.log:200-201`).
- Source: `tests/memfn/simd_guarded_check.py:96` (`'simd-form': 6`, "pinned AT the measure"), counted at `:229-230` (artifacts whose MEMFN_FORMS names a SIMD row).
- Cause (inference, strongly suggested): one of the sampled corpus artifacts lost its SIMD row because its window search (the "stop PAIR with its SIMD rows" the comment at `:98` names) is the thing R-30 drops. The only c-simd movers are 6 patterns (`census.txt`, `c-simd` lines): two backreference chains, `(x?)(?i:abcdefghijkl)\1`, the https/tld pattern, and the two `(x?)([a-z]+)+eeeeeeee...` forms. `(x?)(?i:abcdefghijkl)\1` is a caseless run with a `window search` and is the most likely member of the 6. I did not run the check to name the artifact.
- Class: (b).  The lane never ran `test-memfn-guarded` (it is not in the job's targeted memfn sections as a pre-delivery step; the report's validation list does not name it).

### test (`scripts/perfrun --label r30b`, full `make test`, rc=2)
- `.perfrun` note FIRST (`test.make.log.perfrun`): `DONE rc=2 wall 1332s cpu 16004s mean-busy 82% section-errors=3 class=RED-REAL contaminated=no`, "red sections: test-codegen test-compound test-memfn-guarded - not a K44/load signature; treat as a real red". So (c) is excluded by the note.
- Verdict lines (`test.make.log:4295`, `:8561`, `:8919`): `*** [Makefile:678: test-codegen]`, `*** [Makefile:1470: test-memfn-guarded]`, `*** [Makefile:1564: test-compound]`.
- test-codegen and test-memfn-guarded: the same two checks as above (`test.make.log:3584`, `:8557`).
- NEW, only seen here: test-compound. `test.make.log:8869` `FAIL (c) the lever is mentioned outside its allowlist: tests/mech/sabotages/S1548_lever_ignored.sh:13:SAB_REACH='... --harness=pres-window ...'`; `:8874` "FAIL: G7 lever fence: 1 failures"; `:8918-8919` `test-compound: FAIL`. All other compound checks pass.
- Source: `tests/compound/run_lever_fence.sh:49` (the ALLOW regexp; R-30 added `tests/memfn/run_presence.sh` at `:49` but not the new plant). Check (c) greps `--harness=` under tests/ (`run_lever_fence.sh:34-40`, comment `:34-47`). The plant S1548 mentions the lever by design (`tests/mech/sabotages/S1548_lever_ignored.sh:13`). S1543-S1547 do not name `--harness=` so only S1548 trips.
- Class: (b)/(e) allowlist not extended for the new plant; the lane ran `axes_lever` but not test-compound (the lane's changed `tests/compound/run_lever_fence.sh` shows it knew the fence exists: the diff adds only `run_presence.sh`).
- No other section errors: only these 3 (`perfrun section-errors=3`).

### reach (`REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh`, rc=1)
- Verdict: `reach.log:3222-3225`: "2 row(s) NOT declared UNREACHED read unreached: S1760-pin-compare-skipped reach:MISSING(1/1), S1761-pin-last-link-only reach:MISSING(1/1)"; `mech-reach-only: DONE rc=1 rows=1070 reached=527 unreached=2 declared-unreached=15 now-reached=0 no-probe=526`.
- The 15 declared-UNREACHED rows are the standing set (not new). None of R-30's six new plants (S1543-S1548), S278 or S693 is in the unreached list: all REACHED (their rows read `reach:ok`, in `reach.log` and `mech.log`).
- S1760/S1761 are the pin-chain rows of [INLINE-C] stage 3 (commit eac952671, `tests/mech/sabotages/S1760_pin_compare_skipped.sh:10-11`, `S1761_pin_last_link_only.sh:10-11`); their file `src/parse/rxt_source.c` and the fixtures `tests/code/frag/*` are not touched by lane r30b (`git diff 1f5574fac HEAD --stat -- src/parse tests/code` empty; the only `src/core` change is `internal.h`).
- They passed `reach:ok(1/1)` on main in job 681 (`worktrees/.boxqueue/done/20261029T125033.944851191-681-ic3-mech/job.log` lines 9, 11, 21-22).
- I ran both probe commands against `worktrees/r30b/build/pcrec` (scratch outputs only), also with the fixtures copied under an `_clean/tree`-shaped path inside `build/tmp`: both print the expected strings ("sha256 pin mismatch", "pin2_ok.rxt:5 carries no sha256 pin"). So the rows are right and the binary is right; the per-row `reach.log` that would say why the matrix probe saw otherwise was deleted with the mktemp scratch root (`mech.log:4`-style `pcrec-mech-sabotage.312b5Q`, now absent).
- Class: unexplained; (c) or (e). Not (a), not (b), not (d) (the witnesses are not R-30's and still reach when run by hand). Candidate causes (inferences, none verified): the clean tree's `make all` racing the same box job (the clean tree is `git archive HEAD` built by the matrix, `run_sabotage_matrix.sh:1019-1021`), or a probe timeout/rc=1 under 16-way parallel reach evaluation. The reason string says "exited 1", not 124, so not the 120 s bound (`run_sabotage_matrix.sh:1561-1564`).

### mech (rc=0, but note)
- `mech.log:243` "76 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 1)"; the step is rc=0 so the job did not count it, but one row was NOT measured: `mech.log:101` S678-m6-adv-member-ignores-term `ANOMALY (the plant does not compile: ... gen.c:143:28: error: 'rx_class_bitmap1' defined but not used [-Werror=unused-...] -- a compile failure is not a catch; make the plant warning-clean)`.
- S678 (`tests/mech/sabotages/S678_m6_adv_member_ignores_term.sh`, file `src/gen/memfn_sites.c`) is in the job only because R-30 edited `memfn_sites.c` (+6 lines, the lever hookup at `src/gen/memfn_sites.c:161-166`). That edit is outside `adv_member`. No earlier job log in `.boxqueue/{done,failed}` contains S678, so I cannot say whether it was already unclean on main (inference: probably yes, hand-measured 2026-10-08 by lane m6).
- The mech rows for R-30's own plants: all measured and DETECTED (`mech.log` 243: undetected 0, unexpected 0).

## Cause classes

| class | items |
|---|---|
| (a) R-30's own defect | NONE found. Census 0 unexpected in 9 arms; lever answers identical (`axes_lever` rc=0; `memfn.log:305-306` r30-lever-answers 5868 cases, 0 failed). |
| (b) expected move not re-pinned | reqcube k66 `rx_reqrun` expectation; simd-form floor 6 -> 5; lever-fence allowlist for S1548 |
| (c) environmental | none confirmed (perfrun: contaminated=no, not K44) ; reach S1760/S1761 possible, unproven |
| (d) witness stopped reaching | none of R-30's; S1760/S1761 reach lost in the matrix run only (not by hand) |
| (e) other | S678 unclean plant (anomaly); the declared 4 steps under "population SHORT" are only the 4 red steps that did not print `rc=0` |

Note on the job itself: the "SHORT" population is 9 of 13 steps `rc=0` (`result` line 2), i.e. the same four reds; nothing else is missing.

## Does merging main change it

Main is 136 commits ahead (`git log 1f5574fac..main`); main's `PCREC_ARTIFACT_ABI` is 93 (`git show main:src/gen/emit_dfa.c` line 55), the branch's is 94 (`src/gen/emit_dfa.c:55`), so the merge conflicts at every abi reader and lands as 93 + R-30 = 94 (the branch already assumed this; `r30b_job_kit-r30b-heavy` header). Specifics:
- simd-form: main already changed `tests/memfn/simd_guarded_check.py` (+11 lines: three NAMED vrun witnesses `(?i)foobarbaz`, `(?i)select.*from`, `(?i)abcdefghijklmnop` and a new `simd-form-named` floor 4, "a 4-file corpus addition shifted it from 6 to 5"). That is the same symptom. After the merge the sampled count and the named count must be re-measured with R-30 applied; the floor 6 may or may not hold. Do NOT hand-set 5 on the branch (it would conflict with main's rewrite); re-measure after the merge.
- reqcube and the fence: main does not touch `reqcube_check.py` or `run_lever_fence.sh` (`git diff 1f5574fac main --stat` for those paths empty), so those two fixes carry over unchanged.
- VMREC (stmt writer) and K134 move emitted VM bytes on main, so the census reference (`BASE=1f5574fac`, the job's `BASE`) is stale: the census must be re-based to main's tip (a3cc4de82, or whatever main is at) and its mover declarations (c-vm declared=43, `census.log` arms) re-derived. Also S1760/S1761 have no dependency on main (matrix script changed on main only by two new suite arms, `trailcompact`, `stmtwriter`).
- The mech rows' SHA key changes with the merge, so mech results at 5a150b93 do not transfer.

## Proposed fixes (NOT made)

1. `tests/codegen/reqcube_check.py:262-265`: where the whole part is present and the window part was dropped, assert `rx_reqrun` ABSENT and `rx_reqrun_whole` PRESENT (and still run the whole-block checks at 266-277) instead of requiring `rx_reqrun`. Keep the requirement for patterns with no whole part (the other `WIT` entries). Compute the condition from the facts (`req_whole_run` is set, `whole` truthy at :242) rather than from the emitted text, to keep a control independent of the thing it controls. (The tests/codegen/run_prechecks.sh:1541 comment already describes the "dominated run leaves no rx_reqrun block" shape; reuse its wording.)
2. `tests/memfn/simd_guarded_check.py:96` `FLOORS['simd-form']`: after merging main, measure `simd-form` and `simd-form-named` with R-30 applied; re-pin to the measure with a comment line saying R-30 removed the window stop pair for the whole-run artifacts (do not guess 5). Check whether any of main's three named witnesses carries a whole run beside a window (if it does, it moves too).
3. `tests/compound/run_lever_fence.sh:49` ALLOW: add `tests/mech/sabotages/S1548_` (the plant's `SAB_REACH` at `S1548_lever_ignored.sh:13` must name the lever to exercise it), and extend the comment at `:47-48`.
4. S678: make the plant warning-clean (it leaves `rx_class_bitmap1` unused at gen.c:143), then confirm it measures; first confirm on the reference tree whether this predates R-30 (single-row run at the ref).
5. S1760/S1761: no source change proposed. Re-run them alone with a KEPT scratch (`MECH_SCRATCH=<dir under build/>` so the `reach.log` survives and the clean tree is reused) to get their per-row log; only change something if the rerun reproduces.
6. Report hygiene (lane r30b): `r30b_report.md` should name `test-codegen`, `test-memfn-guarded` and `test-compound` as not run before delivery, per the delivery bar ("Run `make test` (async), not only the section you think counts", BOILERPLATE).
7. Merge main first, resolve the abi readers to 94, rebuild the census reference at main's tip, then fix 1-4 in one pass, so every re-run below is of the final tree.

## Re-run plan (one stage per boxqueue job, each well under an hour; chained with `boxqueue after`)

Pre-condition (lane r30b, not a job): fixes 1-4 plus the merge of main, committed on `lane/memfn-r30b`; the job script's BASE re-pointed to main's tip and its `--dry-run` abi check kept at 94. Durations are from this run's own timestamps.

| # | job (one stage) | after | why it must re-run | expected wall |
|---|---|---|---|---|
| 1 | `r30b2-build`: `make -j16` then `make strict` (job.log:4-8: 16 s) | - | tree changed (merge) | ~1 min |
| 2 | `r30b2-census`: refbuild at main tip + `census.py` (job.log:9-22: ~35 s here; larger with VMREC) | 1 | BASE is stale; re-derive the declared movers | ~5 min |
| 3 | `r30b2-codegen`: `make test-codegen` (job.log:23-64: 3.5 min) | 1 | red; fix 1 | ~5 min |
| 4 | `r30b2-memfn`: the 15-section memfn group (job.log:82-123: ~7 min) | 1 | red; fix 2 | ~10 min |
| 5 | `r30b2-compound`: `make test-compound` | 1 | red; fix 3 (its own stage; was not a step before) | ~10 min (inference) |
| 6 | `r30b2-regrx`: `make test-registry test-rxtsource` | 1 | abi/pin readers move with the merge (green here: 31 s + 72 s) | ~3 min |
| 7 | `r30b2-axes`: `AXES=--harness=pres-window tests/axes/run_axes.sh` (job.log:124-128: 10.5 min) | 1 | lever answers over the merged corpus | ~12 min |
| 8 | `r30b2-test`: `scripts/perfrun --label r30b -- ...` full `make test` (22 min here) | 3, 4, 5, 6 | the arbiter; run last so it is a single clean verdict | ~25 min |
| 9a | `r30b2-mech-a`: first half of the 76 ids (the six new plants S1543-S1548, S278, S693, S449 and S678 first) | 8 | the matrix keys on the SHA; the whole 76-row run was 86 min, over the hour | ~45 min |
| 9b | `r30b2-mech-b`: the second half | 9a | same | ~45 min |
| 10 | `r30b2-reach`: `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` (job.log:143-184: ~1.7 min here) with `MECH_SCRATCH` kept | 1 | red (S1760/S1761); must be re-run whole on the merged tip | ~5 min |

Stages NOT to re-run: mechval is a cheap `VALIDATE_ONLY` on the same 76 ids (fold into job 1 if the id list changes, otherwise skip); the 5 green steps that depend on neither the merge nor the fixes do not exist - every step is tip-keyed, so all re-run once on the merged tip, but only the table's stages need a separate job (mechval/build/strict/refbuild folded into 1-2).
If the manager prefers not to merge main first: run jobs 3, 4, 5 (and 10 narrowed to `S1760 S1761` with kept scratch) at the current branch tip after fixes 1-3 only, with simd-form hand-set to the measure; that would give a faster answer but a result at a tip that is going to move again.

## STATE AT HANDOFF

- Delivered: this report only (committed). No code, no log, no manifest changed; `docs/dev/artifact_size_log.tsv` and `r30b_rulings.md` left untouched.
- Scratch used: `/var/tmp/pcrec-pcrec/scratch/r30btri/` (probe outputs; two throwaway dirs under `worktrees/r30b/build/tmp/` removed).
- Open for the manager: whether to merge main before the fixes (recommended, see above); the S1760/S1761 cause is NOT established; the S678 history is unknown.
- No rulings file named in the brief; `r30b_rulings.md` belongs to the build lane and was not read.
