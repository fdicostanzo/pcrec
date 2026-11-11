# k382afix report: code review 2026-11-10 r2 k382a's FIX-NOW set (memfn K38-2a)

Lane k382afix (opus), branch lane/memfn-k382a in worktrees/k382a, on 28381e0c3 (the review with
the kit manager's rulings). Commits ff8db295a, 3ca4e7e17, 5bdb4e42b, plus this report. STATE: done.
No rulings file was named in the brief.

## Summary

Every ruled FIX-NOW item, the DOC item and the PLAN carry are in. All changes are on the test side,
with one exception: the EMIT-2 diagnostic string in `memfn/src/window.c`. That is a refusal message's
text. It changes no emitted byte and no behaviour (zero bytes: 300 BASE-vs-tip compile pairs
identical, below).

- ORC-1: the G2 presence family now writes its oracle records at the CALLER boundary. Subject, length
  and origin come from the host's attempt, as `uses()` handed them to the use. omin is the stated one,
  off the site table. The result is converted to the host's frame. The critic's +1 shift is the new
  plant S3010. It reads RED on the oracle (rows=50073 violations=1980). Against the pre-fix driver the
  same plant reads GREEN (rows=50112 violations=0).
- FAM-3: each verified position now gets per-bit near-miss probes in EXTENT, and the SOUND and uses
  subjects now carry near-miss occurrences. All three are counted and floored. The one-bit-looser mask
  is the new plant S3011. It reads RED (EXTENT near-miss; the oracle is also RED, violations=162).
  Against the pre-fix driver it reads GREEN.
- ORC-2: an absent oracle is now a FAIL. `--plants` counts an OWED oracle plant as bad. Both were
  shown with the oracle removed in a scratch root.
- ORC-4: `g_active` is now reset on the fault arm. The iface states the `reads` window.
- FAM-5: the deleted in-run `continue` is the new mech row S3012 (detector g2pres, RED). The census's
  limit is written into decider_census.py D.
- EMIT-2, FAM-1, FAM-4: text fixes.
- FAM-2, ORC-3, EMIT-3: written into sheet §5's K38-2 row as PLAN (c)-(e).

Side finding, fixed test-side: plant mode copied `memfn/src` with `cp -r`. In a scratch root whose
`memfn/src` was a symlink to the worktree, that wrote the plants INTO the worktree's real source. It
happened during my own control runs. I found it by `git status`, reverted it with `git checkout` on
the two files, rebuilt, and re-ran the controls on real copies. The runner now copies with `cp -rL`.
The review's verifier used mini-roots of the same shape. Its notes say it kept its own copy of
`memfn/src`, so its runs were not exposed.

## Fix by fix

| id | ruling | what changed | witness |
|---|---|---|---|
| ORC-1 | FIX-NOW | `memfn/tests/g2/g2_pres_run.c`: `uses()` sets the host's subject, length and attempt start (`g_hs`/`g_hn`/`g_hlo`; re-entry: `pv`) before each use. `g2p_rec` records those, not the part's `(s_, n_, lo_)`. It measures reads in the host's frame, writes `(s + r) - g_hs` as the result, and writes omin from the new site field `omin`. That field is the run span's STATED omin (`g2_pres.h`; `g2_pres_gen.c` reads `s.pspans[run].omin`). The oracle's checking logic is untouched. | New plant S3010 (`ofsskip.c ofs_fn_call` renders `lo + 1`): `run_g2_pres.sh --plant S3010` RED on the oracle step, rows=50073 violations=1980. The family classifier stays silent, as expected. Control, the same plant with HEAD-before-fix `g2_pres_{h,gen,run}.c` in a scratch root: GREEN, rows=50112 violations=0. Mech row `tests/mech/sabotages/S3010_use_passes_part_attempt_start_plus_one.sh`, reach token `REACH-G2P-USE-CALL` (new in `--reach`). |
| ORC-2 | FIX-NOW | `run_g2_pres.sh`: the OWED case of the oracle step is `note` (a FAIL). In `--plants`, an oracle-detected plant with the oracle OWED adds to `bad`. Comments fixed: the runner's header item 4, `memfn/tests/run_g2.sh` 4p, and `tests/mech/run_sabotage_matrix.sh` g2pres (the two the review named). | Scratch root with no `occurrence_oracle.py`: the normal run printed `FAIL: ORACLE OWED ...`, rc=1. `--plant S3008` printed `PLANT S3008 OWED ... NOT DETECTED`, rc=1. |
| FAM-3 | FAM-3 FIX-NOW | `g2_pres_run.c`: (1) EXTENT, EXACT: for every member of every verified position, every bit whose flip leaves the position's set, an otherwise whole occurrence carrying that near-miss must not be yielded (`nearmiss=`). (2) SOUND: a near-miss occurrence in half the subjects (`nm_sound=`). (3) uses: a near-miss occurrence of the whole run in half the subjects, which the oracle reads (`nm_uses=`). New probes draw from a second stream (`rnd2`), so the existing probes draw what they drew before. Floors in `run_g2_pres.sh` were measured over the six passes, least value less ~10%: NEARMISS 28540 (31712), NM_SOUND 3440 (3822), NM_USES 4120 (4583). | New plant S3011 (`runcmp.c rc_emit_words`: a multi-bit mask byte loses its lowest bit): RED, `EXTENT: part at 4 len 8: a near-miss 0x4d (member 0x4c, bit 0) ... is yielded`; the oracle is also RED (violations=162). Control with the pre-fix driver: GREEN (rows=50178 violations=0). Mech row `S3011_run_compare_mask_one_bit_looser.sh`, reach `REACH-G2P-WORDS-COMPARE`. Verifier's caveat checked: RED on x86-64-v3 first; all three arms run. |
| FAM-5 | FIX-NOW (small) | New mech row `S3012_in_run_stop_filter_deleted.sh` (detector g2pres) and the same plant in `run_g2_pres.sh`. `tests/memfn/decider_census.py` D's docstring now states the LIMIT: D counts the use of kit_run_decide, not the in-run filter, and names S3012 as that filter's control. | `--plant S3012` RED: in the lever pass, `mf_define` refuses the layout ("its run part is not the WINDOW its presence link verifies"). Reach `REACH-G2P-LEVER-PASS`. The census's blindness was already shown by the review (96/0 green on the plant). |
| ORC-4 | DOC + FIX-NOW | `g2_pres_run.c uses()`: `else g_active = 0;` on both fault arms (entry, re-entry). `docs/dev/lanes/k382a_oracle_iface.md`: the `reads` row states the window [-64, n + 64) and that layouts U/L fault on reads outside it. A closing paragraph says records are taken at the caller boundary, and that a part's hit at or past the length it was handed is `MISS`. | By reading. The fault arm runs only on an already-red LAYOUT run. |
| EMIT-2 | FIX-NOW (text) | `memfn/src/window.c` translate's kit_fail text: "(the T_MASS_STRETCH tie row must be a strict order)" became "(the run decision's tie row must be a strict order)". Part 1 (the :871 precondition comment) is NOTED in the review and was left unchanged. No test, spec or sabotage reads the string (grep). | Zero bytes: the identity sample below. |
| FAM-1 | FIX-NOW (text) | `tests/mech/sabotages/S3008_run_part_candidate_above_least.sh`: the OWED paragraph is replaced by one line, "an absent oracle file is a FAIL of the family". | Anchors resolve (below). |
| FAM-4 | DOC | `S3009_run_tie_left_lever_ignored.sh`: the header now says the detector is the lever pass's per-witness STATED-rule check (`LEVER`), and that the `moved` comparison adds no power and no plant isolates it. It also says REACH-G2P-LEVER-PASS counts the family's own output, while the real reach is the 24-witness floor. SAB_DESC reworded the same way. | Text only. `--plant S3009` still RED (LEVER). |
| FAM-2, ORC-3, EMIT-3 | PLAN | `docs/design/memfn/span_runs_sheet.md` §5's K38-2 row adds PLAN (c) FAM-2: read ver off the reply, and establish whether any K38-2a reader reads the reply's `ver_len`. (d) ORC-3: run-frame records, the site's reply, a floor on partial-extent hits that must be > 0 after K38-2. (e) EMIT-3, BEFORE K38-2: a G2 window case reaching the set-candidate and meet-narrowed branches under the lever. Also a revision-log row ("r2 k382a PLAN", no rev bump). | Text. |
| EMIT-1 | NOTED | nothing | - |

Other file touched: `memfn/tests/CLAUDE.md` (the presence entry: caller-boundary records,
near-misses, absent oracle a FAIL, S3007-S3012; 12,041 B, within the limit).

## Checks re-run

All runs were on the Linux dev box, niced, at parallelism 2 or less, before 19:00. Logs are under
/var/tmp/pcrec-pcrec/scratch/memfn/k382afix/.

| check | file/command run | result |
|---|---|---|
| build | `nice make -j2` | rc 0 |
| strict | `make strict` | rc 0, "whole tree compiles clean with -Werror -Wshadow" |
| presence family, whole (ASan) | `memfn/tests/run_g2_pres.sh`, all three arms, default + lever, with the ASan+UBSan build (`final_run.log`) | **oracle: green over 50136 records (rows=50136 violations=0)**; checks passed 939330, failed 0; lever 24 of 24 moved on every arm; skipped arms 0; each ASan+UBSan driver failed 0 |
| presence plants | `run_g2_pres.sh --plants` (`final_plants.log`) | all six RED, rc 0: S3007 (family EXTENT; oracle violations>0), S3008 (oracle), S3009 (family LEVER), S3010 (oracle, 1980), S3011 (family EXTENT near-miss; oracle 162), S3012 (family, lever pass mf_define) |
| controls | the pre-fix driver in a scratch root (`ctl_S3010.log`, `ctl_S3011.log`); the oracle absent (`ctl2_run.log`, `ctl2_p.log`) | S3010 GREEN and S3011 GREEN before the fix; with the oracle absent, the run FAILs and `--plant S3008` is OWED and counted bad (rc 1) |
| finder | `make test-memfn-finder` | rc 0, failed 0 (finder_check 1108, proven 31, mass 41, rundec 13, census 85, purity 1157) |
| rows | `make test-memfn-rows` | rc 0, failed 0 (239 and 96 passed) |
| link | `make test-memfn-link` | rc 0, failed 0 |
| decider census | `python3 -I tests/memfn/decider_census.py --root worktrees/k382a` | 96 passed / 0 failed; its three run-callers plants each 1 error |
| anchors | `python3 -I scripts/m6read_check_sab_anchors.py` | "sabotages checked: 1230 (1274 anchor sites) / all anchors resolve" |
| codegen | `make test-codegen` | rc 0, "run_group: 21/21 scripts passed" |
| oracle self-test | `python3 -I tests/memfn/occurrence_oracle_selftest.py` | "selftest: PASS (0 failing)" |
| mech reach | `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S3007 S3008 S3009 S3010 S3011 S3012` | "mech-reach-only: DONE rc=0 rows=6 reached=6 unreached=0" |
| zero bytes | BASE 7658295b3 (`scratch/memfn/k382a/base/build/pcrec`) vs the tip's `build/pcrec`, same output basename, 60 bench patterns (every 5th of `spanpick_bench_patterns.txt`) x 5 arms: `--features all`, + `--analysis weblog`, + `-e utf8`, + `--memfn=no-window-search`, + `--engine=vm` | 300 pairs: 294 identical, 6 refused identically, **0 differ** (one more arm, `--analysis uniform`, is not a CLI analysis and refused all 60 on both sides; it is not counted) |

The full mech rows, make test, identity, reach and plants gates are the queued jobs below. That is
the kit manager's call, not owed by this lane.

## Gate jobs

`/var/tmp/pcrec-pcrec/scratch/memfn/k382afix/jobs/` is copied from k382a's set and re-keyed
`kit-k382b-*`, numbers 550-559. The S= paths (jobs, gate outputs) point under
`scratch/memfn/k382afix`. The frozen BASE binary stays k382a's. Not queued.

- 550 strict, 551-553 ident (71 arms, zero movers), 554 reach: unchanged apart from the keys and paths.
  The lane moves no byte and adds no REACH.
- 555 test: unchanged expectations (presence family PASS, the plants of rows_check/§D).
- 556 plants: `run_g2_pres.sh` must list `S3007 S3008 S3009 S3010 S3011 S3012`. The expectation
  is `presplants=6 lines=^PLANT S30(0[789]|1[012]) RED `.
- 557-559 mech: S3010 (shard 1), S3011 (shard 2) and S3012 (shard 3) are added. 105 rows, 35/35/35.
- Every `--dry-run` passes (rc 0 on all ten).

## Charter-vs-committed checklist

| charter item | committed | where |
|---|---|---|
| ORC-1 caller-boundary records; +1 shift RED as a new sabotage row | yes | g2_pres_run.c, g2_pres.h, g2_pres_gen.c; S3010 |
| ORC-2 absent oracle a FAIL; --plants counts OWED as bad; the comments | yes | run_g2_pres.sh, run_g2.sh, run_sabotage_matrix.sh |
| FAM-3 per-bit near-misses in EXTENT and SOUND/uses; one-bit-looser mask RED as a new row | yes | g2_pres_run.c, floors in run_g2_pres.sh; S3011 |
| FAM-5 mech row for the in-run `continue`, detector g2pres; the census's limit | yes | S3012; decider_census.py D |
| ORC-4 g_active reset on the fault arm; the iface's `reads` window | yes | g2_pres_run.c uses(); k382a_oracle_iface.md |
| EMIT-2 text | yes | memfn/src/window.c (the kit_fail string only) |
| FAM-1 text | yes | S3008 header |
| FAM-4 reword S3009's row | yes | S3009 header + SAB_DESC |
| FAM-2, ORC-3, EMIT-3 as PLAN in sheet §5 K38-2 (EMIT-3 "before K38-2") | yes | span_runs_sheet.md §5 K38-2 row (c)-(e) + revision-log row |
| new sabotage ids from the top of the free range | yes | S3010-S3012 (S3009 was the highest on main and in every worktree) |
| occurrence_oracle.py's checking logic untouched | yes | not edited; ORC-1 needed no change there |
| checks listed in the brief | yes | "Checks re-run" |
| gate jobs copied, re-keyed 550-559, expectations moved, every --dry-run passes, NOT queued | yes | "Gate jobs" |
| test-side only, zero emitted bytes | yes, apart from EMIT-2's message string (ruled) | identity sample 0 differ |

## STATE AT HANDOFF

OWED: none. Every check in the brief ran and its result is above. The gate jobs 550-559 are written
and dry-run. Queueing them is the kit manager's call. No rulings file. The tree is clean apart from
`k382a.done`, an untracked file in the worktree root that lane k382a's run left behind. It is not
this lane's, and this lane did not touch it.
