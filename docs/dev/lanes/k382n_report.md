# k382n — K38-2 brought up to date with main 51481d1b3, abi re-bumped 103 -> 104

Lane k382n (opus), branch lane/memfn-k382 in worktrees/k382. The new BASE is main 51481d1b3 ([S1]: never-match
VM hybrids are the DFA empty artifact, and searches stop at the minimum width, abi 103; plus xarchfix and
mechfast). Main took 100 -> 103 (101 and 102 had been reserved), so K38-2 lands over it at abi 104 and 101 stays
unused.

## Summary

- **Merge.** Main 51481d1b3 merged in ff1885b16. Ten files conflicted, and each was resolved on its merits.
  `make strict` is clean.
- **abi.** The abi is 104. Every reader of the number was found by grep. The recursion-identity FILEPIN
  self-pins to the merge (a08b3160d, see below). ABASEPIN stays main's 06699f615.
- **Cloud tables.** The mech and axes shard tables were taken from main and re-derived by
  `make cloud-reweight` (mech: 90 shards, 1244 ids; axes: 20 shards). `make cloud-check`: 16 passed, 0 failed.
- **S1909.** The witness was stale, not the plant. It is re-aimed to the restored part's `@`-less run
  `"61626364"`. It was verified by single compiles on the tip, and with the plant applied.
- **Census.** The census against the new BASE is GREEN on the 300-pattern sample, with 0 unexplained, on
  the first run (job 581-kit-k382n-census). Main's S1 content explained nothing new on either side, and no
  census bug surfaced.
- **Gate jobs.** 600-606 are re-pointed to BASE 51481d1b3 (abi 103 on BASE, 104 on the tip). Every
  `--dry-run` passes. 607-609 are dropped, because mech runs in the cloud. Nothing is queued.

OWED: S278, S517, S1909 (cloudrun --kind mechrows; S278 and S517 are k382cm2's, S1909 is this lane's re-aim)

## Merge and conflicts

`git merge main` ran alone in its own command. It conflicted in ten files:

- `docs/dev/history/abi_changelog.md`. K38-2's entry now reads "is `104` ... 103 -> 104". It notes the re-bump
  over s1land, and that 101 stays unused. Main's [FIND-MINW] entry becomes "was `103`". Main's [NEVER-MATCH]
  "was `102`" entry is kept as it was.
- `src/gen/emit_dfa.c`. `PCREC_ARTIFACT_ABI 104`.
- `docs/spec/match_api.md`. There were three regions: the guard `!= 104` with its `#error` "(abi 104)" and
  `#define PCREC_RX_ABI_H 104`; the rx_info table row (`104`); and §6¶17 "It is `104`". The K38-2 side's other
  hunks merged cleanly.
- `tests/codegen/run_codegen_tests.sh`. The `[DD-14.FB]` transition string is main's (ending
  `100->103: [FIND-MINW] ...`), plus K38-2's own text as `103->104`. `ABI_EXPECT=104`.
- `tests/mech/sabotages/S693_abi_not_bumped.sh`. Both sides' re-aim notes are kept, plus this lane's.
  `SAB_BEFORE` is 104. `SAB_AFTER` stays 100 (main's number at the lane's base, as main's minw left it). Any
  number other than 104 is detected.
- `tests/codegen/run_recursion_identity.sh`. Main's [NEVER-MATCH] comment line is kept. FILEPIN carries the
  K38-2 re-bump note, with main's chain behind it. Its value moved to the merge ff1885b16 in the next commit
  (a08b3160d), because a commit cannot name itself. ABASEPIN stays main's 06699f615, because K38-2 moves no
  call-free program region. k382m kept ABASEPIN the same way.
- `tests/codegen/run_cpset_structure.sh`. Both re-record notes are kept: k382m's `^foo$` -2 bytes, and minw's
  six +106/+120 rows. The manifest rows auto-merged. `test-cpset-structure` is green in `make test-codegen`.
- `tests/axes/run_axes.sh`. The array is main's, minus `--harness=pres-window`, which K38-2 retired with the
  two-part run (cli/CLAUDE.md option 5). Main's `--harness=no-min-width` arm is kept.
- `tests/ci/cloud_mech_shards.tsv` and `tests/ci/cloud_axes_shards.tsv`. These were not hand-merged. See "Cloud
  tables re-derived".

Everything else merged clean. That includes `src/facts/*`, `src/core/internal.h`, `docs/spec/facts_listing.md`,
`docs/spec/tuning.md` and `tests/codegen/run_prechecks.sh`, which both sides touched. The kit's `MF_SITE_ABI` is
27 and `MF_CLASS_V` is 9 on the merged tree, from K38-2. Main stays at 26/8, and S1 does not move them. After the
merge, `make` and `make strict` are clean.

## abi 104 re-bump (readers by grep)

The grep was `git grep -nIE '(abi|ABI)[^0-9]{0,40}\b10[0-4]\b|\b10[0-4]\b[^0-9]{0,25}(abi|ABI)|ABI_H 10'` over
the tree. It excluded only docs/dev/history, reviews, lanes reports, the journal and plan_completed. A second
grep looked for `\b(101|103)\b` near `abi`/`rx_info`/`PCREC_ARTIFACT` in tests, memfn/tests, docs/spec, src,
cli, lib, scripts and the census.

Readers moved:

- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI 104`.
- `docs/spec/match_api.md`:
  - the guard;
  - the `#error` text;
  - `#define PCREC_RX_ABI_H`;
  - the rx_info table row;
  - §6¶17.
- `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` and its message.
- The S693 BEFORE.
- `abi_changelog.md`.
- The recid FILEPIN self-pin.
- The census defaults: `--abi 103:104`, `--base-rev 51481d1b3`, its docstring, and
  `docs/dev/lanes/k382_evidence/README.md` (4b65d8470).

The remaining hits are historical or explanatory and stay. These are:

- main's re-aim notes, "abi 103" in run_prechecks/run_prefilter/run_resource/cand_oracle_witnesses;
- "abi 100"/"abi 102" in run_dfa_stamps, run_partlayout and check_lever;
- match_api §6.3.6's `"empty"` row ("abi 100");
- plan.md status lines;
- the kit journal/wake.

The number keeps its width (3 digits), so no size pin moves with the digits.

## Cloud tables re-derived

- `tests/ci/cloud_mech_shards.tsv`: `git checkout --theirs` (main's table, with mechfast's 90-shard planner
  shape), then `make cloud-reweight KIND=mech`. The population is the branch's 1244 ids. These are main's ids,
  minus K38-2's retired S449/S1543-S1548, plus K38-2's new rows. Predicted wall is 2586 s, and the indivisible
  floor is 2586 s (S221 2551 s).
- `tests/ci/cloud_axes_shards.tsv`: the same steps with `KIND=axes`, which drops the retired
  `--harness=pres-window` unit. Predicted wall went 3108 s -> 3102 s.
- `tests/ci/cloud_kinds.tsv` and `cloud_units_plan.py` (the kinds rows, the mechrows kind, the planner flag) are
  main's, auto-merged.
- `tests/ci/measured_mech.tsv` is main's, unchanged. Its writer is `tests/ci/cloud_measure.py`, which
  re-measures from completed GitHub runs (`gh`). No new run exists to measure, and the branch's new rows take the
  planner's default weight. So the file was not re-derived; the reweigh reads it as committed.
- `make cloud-check`: 16 passed, 0 failed (`scratch/memfn/k382n/cloudcheck.log`). The mech population check
  reads "90 shards of cloud_mech_shards.tsv hold the 1244 sabotage ids of tests/mech/sabotages exactly once".

## S1909

- **The cloud red.** Cloud mech run 43261368093 shard 5 read S1909 UNREACHED. Its reach probe greps the
  `--harness=restore=empty` artifact of `^a|abcd(?:\b)*efgh$` for `RX__Q_REQ_RUN "61626364@1"`.
- **What the tip prints now.** The tip build prints `RX__Q_REQ_RUN "61626364"` for the restored part. No search
  of this artifact reads a run position, so the `@` is dropped (match_api.md §6.3.7¶7's @ table, row 3). The
  unrestored default prints `"6162636465666768"`.
- **The planted code is live.** The plant (compound.c `walk_arms` dropped) was applied to a `git archive HEAD`
  copy under `scratch/memfn/k382n/s1909/`. That harness prints `"6162636465666768"` under
  `--harness=restore=empty`. The part is no longer restored, so the plant still moves its cell.
- **The fix.** The witness is re-aimed to the quoted text `RX__Q_REQ_RUN "61626364"`, which the unrestored run
  does not contain. The cell and the detector are the same. The probe prints `REACH-PART-RESTORED` on the tip.
  This is commit cea074796.
- **Not retired.** No shard table moves, because the row population is unchanged. The mech row itself is OWED
  to `cloudrun --kind mechrows`.

## Census against the new BASE

BASE is a niced `git archive 51481d1b3` build at `$PCREC_TMPDIR/scratch/memfn/k382n/base/` (abi 103,
checked from its artifact's `.abi`). NEW is the tip (abi 104). The command was
`census.py --abi 103:104 --base-rev 51481d1b3 --sample 300 --jobs 4`, run as queue job 581-kit-k382n-census:
GREEN, wall 196 s, `scratch/memfn/k382n/census1.txt`.

- **census1: GREEN, 0 unexplained** (`== census COMPLETE: 0 unexplained, verdict GREEN rc=0`; 0 `UNEXPECTED`
  lines; 284 arm lines, 275 of them x-arms). The K35 floor is not applied on a sample run.

  | arm | movers | must | P1 | P2a | P2b | P2sd | P3 | P4 |
  |---|---|---|---|---|---|---|---|---|
  | c-default | 38 | 32 | 4 | 9 | 23 | 6 | 11 | 5 |
  | c-utf8 | 41 | 32 | 9 | 14 | 18 | 9 | 14 | — |
  | c-vm | 32 | 32 | — | 31 | 1 | — | 31 | — |
  | c-vm-utf8 | 33 | 32 | — | 31 | 1 | 1 | 31 | — |
  | c-simd | 38 | 32 | 4 | 9 | 23 | 6 | 11 (P3v 1) | 5 |
  | ir | 0 | — | — | — | — | — | — | — |

  The facts arm had 274 movers, all of them Fret. The composition stream had 1 mover over 460 files.
- **Did main's new content move anything?** No. c-default and c-vm read the same counts as k382m's census4
  against e889ba64c (38/32/4/9/23/11/5 and 32/32/31/1/31). Both sides carry S1's never-match and min-width
  changes, so they cancel. No artifact is unexplained, and no new class appeared.
- **No real K38-2 mover went undeclared.** Nothing called for a STOP.
- **Not re-run here.** k382m's negative control (`--control no-norm`, RED) was not re-run. The census code did
  not change beyond its defaults and docstring.

## Gate jobs

`$PCREC_TMPDIR/scratch/memfn/k382/jobs/` is re-pointed. The original common.sh is at
`scratch/memfn/k382n/common.sh.orig`.

- **`common.sh`.**
  - `BASE=51481d1b3` and `ABI_OLD=103; ABI_NEW=104`.
  - `REF` is k382n's niced archive build at `scratch/memfn/k382n/base/build/pcrec`. It is abi 103, which
    `check_inputs` verifies.
  - `REFTR` and `WREF` carry `$BASE` in their paths, so the reach and ident jobs rebuild the -DMF_TRACE and
    witness BASE from 51481d1b3.
- **Comment updates.** `ident.sh` names the event. `604-kit-k382-reach` notes the re-point and still declares
  no GONE/MAP; it builds BASE from `git archive $BASE`. `606-kit-k382-plants` no longer points at 607-609.
- **Dropped.** 607-609 (`mech1..3`) and their `mech.sh` moved to `scratch/memfn/k382n/dropped_jobs/`. Mech now
  runs in the cloud.
- **Dry runs.** Every `--dry-run` passes: 600-606 rc 0. The ident shards read
  `--abi 103:104 --base-rev 51481d1b3 --witness-bins .../witness-base-51481d1b3/pcrec ...`. NOT queued; the kit
  manager queues them.

## Checks

| check | result |
|---|---|
| `make strict` (merged tree) | clean (`scratch/memfn/k382n/strict.log`) |
| `make test-codegen` (after the self-pin) | rc 0, 920 PASS, run_group 21/21 (`codegen.log`) |
| memfn finder/rows/link/targets (`make -k -j4 -Otarget`) | rc 0; no `***` line; every family `checks failed: 0` (`memfn.log`) |
| anchors (`python3 -I scripts/m6read_check_sab_anchors.py`) | 1244 sabotages, 1290 anchor sites, all resolve |
| `make cloud-check` | 16 passed, 0 failed |
| `CLAUDEMD_ROOT=worktrees/k382 scripts/check_claudemd_size.sh --all` | 365 within limits |
| S1909 reach probe (tip) and plant (archive copy) | REACH-PART-RESTORED; the plant prints the unrestored run |
| census sample 300 (job 581-kit-k382n-census) | GREEN, 0 unexplained, wall 196 s (`census1.txt`) |

Not run here: test-recursion-identity. The FILEPIN self-pin is to the merge, and nothing under `src/` moved
after it. It is a cloud kind (`recidentity`).

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| 1. merge main alone, resolve on merits; cloud_mech_shards.tsv never hand-merged, main's kinds rows + planner, re-derive by cloud-reweight, measured_mech by its writer if any, cloud-check | ff1885b16; mech (and axes) tables re-derived; measured_mech.tsv kept (its writer needs new GitHub runs); cloud-check 16/0 |
| 2. abi 104 at every reader found by grep, incl. the FILEPIN self-pin; strict, test-codegen, commit | ff1885b16 + a08b3160d; strict clean; test-codegen rc 0 |
| 3. S1909 re-aimed to a reaching pattern, verified by a single compile (or retired) | cea074796, re-aimed (the plant is live) |
| 4. census BASE = the merged main, `--abi 103:104`, 300 sample GREEN 0 unexplained | 4b65d8470; job 581 GREEN, 0 unexplained |
| 5. gate jobs 600-606 re-pointed, dry-runs pass, not queued; 607-609 dropped | done (scratch, not committed) |
| CHECKS list | all run; see Checks |
| report with the deliver file's sections and an `OWED:` line; lanecheck DONE | this file |

## STATE AT HANDOFF

- **Branch.** lane/memfn-k382 is committed and clean at the tip of this report. There is no rulings file.
- **The box.** Nothing is queued and no run is in flight. Job 581 ended green.
- **What the kit manager does next.**
  - Queue gate jobs 600-606.
  - Run `cloudrun --kind mechrows --rows S278,S517,S1909`.
  - Run cloud test/axes on the merged branch.

OWED: S278, S517, S1909 (cloudrun --kind mechrows; row ids touched since the last full cloud mech, the kit manager dispatches)
