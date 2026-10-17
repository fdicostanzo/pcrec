# fdb2land report (lane fdb2land, 2026-10-17, opus)

Lane fdb2land, working for the memfn kit manager. It brings R17-b′ step B2
(lane/fdb2 @ 01ffd2f2d) onto the new kit base and finishes B2's LIGHT
validation. Branch `lane/fdb2land` off `lane/fdclass` (fd0b8d129). All runs
were pinned with `taskset -c 0-11` and `-j8`/`--jobs 8`. A section is green
when nothing matches GNU make's `\*\*\* \[(Makefile:[0-9]+: )?test-`. Logs are
under `build/` (gitignored); the chain's verdict lines are in
`build/land/verdict.txt`.

## 1. Commits

| step | commit | what |
|---|---|---|
| 1 | 8655c192d | `git merge main` (aa66dbd64: S494's plant guard and the precheck_assign_byte floor 20790). Clean, auto-committed; make rc 0, strict clean |
| 2 | 5f0b72a73 | `git merge lane/fdb2`. Two doc conflicts (§2); make rc 0, strict clean |
| 2 | 917abcd64 | `drop_rms6.diff`'s cli/CLAUDE.md hunk regenerated for the merged paragraph |
| 3 | d295ca21b | `MEMFN_CLASS` fd-d1 set to DIFFER (§3) |
| 4 | 746ccc351 | memfnfinder SAB_DOC_FIGUREs measured; `drop_rms6.diff`'s three deletion blocks regenerated |
| 6 | fb4972aa4 | b1fix_report.md's quoted plan-line citation reworded (PL14, §6) |
| — | this commit | this report and its index line |

## 2. Merge conflicts and resolutions

`git merge lane/fdb2` conflicted on two files, both documentation:

- **cli/CLAUDE.md, the harness-build paragraph.** B1's reword (b1fix) names no
  `--harness=` spelling, so it satisfies the G7 fence. B2 spelled
  `--harness=arm-reach` and the reserved counter prefix. The resolution keeps
  the reword and describes R-MS6's option by its effect: it sets
  `PcrecHarnessOptions.arm_reach`, and the kit counts each routed finder site's
  arm entries under a reserved counter name. The list of places where the
  spellings live now also names `tests/memfn/run_arm_reach.sh`. Nothing in the
  file matches `--harness=` or `pcrec_harness_`. As a result, the fence no
  longer reads red on cli/CLAUDE.md (on fdb2 it did, F-B2-1).
- **docs/dev/lanes/CLAUDE.md.** Both index lines are kept, b1fix/fdclass's and
  fdb2's.

The other places the brief expected trouble auto-merged, and I checked each
one by hand:

- **tests/memfn/row_floors.tsv** keeps main's `precheck_assign_byte 20790`
  alongside B2's `D1`/`D1c`/`D1w` `PLACEHOLDER PLACEHOLDER` rows.
- **The abi readers.** `MF_SITE_ABI` is 13 (B2's). The main side has no reader
  of the kit abi number, and no pcrec abi event is involved.
- **tests/axes/memfn_arm.py** was not touched by lane/fdb2, so no conflict
  arose there. The fd-d1 change is step 3.

**proposed/drop_rms6.diff** still applies (`git apply --check` clean at the
tip). Two edits broke it, and I regenerated the affected blocks each time:

- the merged cli/CLAUDE.md paragraph. The new hunk is
  `git diff HEAD lane/fdclass -- cli/CLAUDE.md`, so applying the diff restores
  B1's reworded text exactly.
- step 4's SAB_DOC_FIGURE edits to S1080, S1081 and S1084. Their deletion
  blocks were rebuilt with `git diff --no-index <file> /dev/null`.

The other hunks are unchanged.

## 3. fd-d1, re-measured

I used the runaxes/fdclass method:
`taskset -c 0-11 python3 -I tests/axes/memfn_arm.py --pcrec build/pcrec --root . --jobs 8 --measure --cell 'fd-d1|default|--memfn=no-fd-d1' --cell 'fd-d1|simd|-fmemfn-simd --memfn=no-fd-d1'`.
It covers 4,624 distinct corpus patterns, took 26 s, and the log is
`build/fd_d1_measure.log`.

| layer | byte c-default | byte c-vm | utf8 c-default | utf8 c-vm | refused |
|---|---|---|---|---|---|
| default | 1004 | 0 | 985 | 0 | 0 |
| simd | 1004 | 0 | 985 | 0 | 0 |

The counts equal fdb2's 1,004 / 985. Both entries are now `DIFFER`, with
floors set to the measured counts and witness `' \w?\b'` (byte and utf8
c-default). The c-vm floor is 0 because the VM stream has no one-byte site.

`MEMFN_REACH_ONLY=1 bash tests/axes/run_axes.sh` reports **memfn arm: OK,
257 passed / 0 failed** (2m32s, `build/fdb2land_reach.log`). fdclass's run was
245/0; the difference is the new floor and witness checks.

## 4. Mech table (memfnfinder rows, each solo)

`make test-memfn-finder` ends with **checks passed: 902 / checks failed: 0**
(finder_check 885/0, arm_reach 16/0, and the single summed pair last). This
confirms run_finder.sh's summed-count fix.

Each row was run with `bash tests/mech/run_sabotage_matrix.sh <id>` at
d295ca21b, and each has its own `== mech run COMPLETE: 1 rows (unexpected: 0,
undetected: 0, ...)` trailer. Logs are `build/mech/<id>.log`.

| id | verdict | figure | before the fix (chain3) |
|---|---|---|---|
| S1079 | DETECTED | memfnfinder 7fail/894pass | DETECTED 4/882 |
| S1080 | DETECTED | memfnfinder 6fail/886pass | UNDETECTED |
| S1081 | DETECTED | memfnfinder 6fail/891pass | UNDETECTED |
| S1082 | DETECTED | memfnfinder 2fail/900pass | DETECTED 2/883 |
| S1083 | DETECTED | memfnfinder 1fail/901pass | UNDETECTED |
| S1084 | DETECTED | memfnfinder 11fail/881pass | DETECTED 5/880 |
| S922 | DETECTED | memfnfinder 8fail/869pass | DETECTED 8/852 |

S1080, S1081 and S1083 are now DETECTED, so the summed-count fix was the
whole cause. No detector, plant or expectation needed changing. Each row's
`SAB_DOC_FIGURE` now carries these figures.

## 5. Sweeps on the merged tip

The reference binary is `build/ref/pcrec`, built from `git archive 8655c192d`
(this lane's step-1 merge = lane/fdclass + main). It is compared against
`build/pcrec` at 746ccc351. I used the flags from fdb2's
`build/land/chain.sh`: `--no-self-check`,
`--streams c-default,c-vm,emit-ir,composition,facts,emit-ir-auto,stderr`, and
`dumps` on plain. The population is 5,790 argv rows, 386 composition files and
106 composition artifacts.

| sweep | rc | movers | elapsed |
|---|---|---|---|
| plain (+dumps) | 0 | 0 on every stream | 35 s |
| `--arms start` | 1 | 0 artifact movers; the ONLY flags are the declared DIFFER flip: `byte --memfn=no-fd-d1 c-default differ=0/1004` and `utf8 ... differ=0/985` (`<-- MOVERS`), with c-vm 0/0 | 359 s |
| `--extra=-fmemfn-simd` | 0 | 0 | 44 s |
| `--extra=-fcomments` | 0 | 0 | 54 s |
| `-e utf8` | 0 | 0 | 59 s |
| `--engine=vm` | 0 | 0 | 44 s |

The start arm's rc 1 has the same cause as in fdb2's chain. On the ref, the
deny is inert (B1 routes nothing), and on the tip it moves exactly the
declared population. Logs are `build/land/sweep_*.log`.

## 6. Suite verdicts (`build/land/<section>.log`)

| section | verdict |
|---|---|
| test-codegen | green, 35/0 (fdb2's K37 red is gone: b1fix bounded the site) |
| test-compound | **RED, one check only**: run_lever_fence (c) on `tests/memfn/run_arm_reach.sh:6` (`--harness=arm-reach`). This red is main's ruling 4, pending: the ALLOW entry is proposed as `fdb2/proposed/lever_fence_allow.diff`, and the file goes away with `drop_rms6.diff`. Every other compound check passes (7/0). cli/CLAUDE.md is no longer red (§2) |
| test-registry | green, 79/0 |
| test-cand-oracle | green, 100/0 |
| test-memfn-g2 (quick) | green, 52,987,694 / 0 |
| test-memfn-rows | green, 232/0 |
| test-memfn-deleg | green, 5/0 |
| test-plan-lint | was RED on the base: PL14 on `b1fix_report.md:44` quoting `plan.md:` plus a line number. Reworded (fb4972aa4), so re-run green 2/0. It was pre-existing on lane/fdclass and not from B2 |
| test-spec-history | green, 145/0 |

No K37 at a new site.

## 7. chain3's results, by reference

These were measured at fdb2's PRE-MERGE tip, not on this branch. The source is
`worktrees/fdb2/build/land/verdict3.txt`. The mech lines' trailers name
38cbde1b9 and 01ffd2f2d, and the sweep/census steps ran after 01ffd2f2d.

- **Routed census: 5 cells, 0 failures** (`ROUTED_CENSUS rc=0`). The floors
  are in `worktrees/fdb2/build/land/routed_floors_measured.tsv`: MLINE
  DFA_ATTEMPT D1c 61, PF DFA_HAT D1 55, PF DFA_SCAN D1 743, PF HYB_PF D1 1017,
  PF VM_ATTEMPT D1w 1606, each floor(0.9 x measured). They are not yet
  committed as `routed_floors.tsv` (OWED, §8).
- **Trace sweep: 0 movers** (rc 0, 239 s).
- **Variants: CLEAN** (rc 0).
- **Prefix invariance: 9/0.**
- **Long prefix**: rc 0, the row count 5,790 matches the census pin, and 0 gcc
  failures at prefix length 60.
- Also from chain3: S288, S289, S481-S485, S495, S1019 and S1085 were all
  DETECTED solo.

## 8. OWED for the HEAVY slot

Run these from this worktree with `export TMPDIR=$PWD/build/tmp`:

| item | command |
|---|---|
| full make test | `scripts/perfrun --label fdb2land -- build/land/test.log` |
| mech derived rows | `scripts/sabotage_anchors.py --step` over the B2 edit set (the fdb0/fdb1 method), then each row solo |
| G2 full | `make test-memfn-g2-full` |
| N2 census | the command in `row_floors.tsv`'s header. It also fills D1/D1c/D1w's `pcrec_floor` |
| test-axes, deny arm | `make test-axes AXES="--memfn=no-fd-d1"` |
| bench-pattern sweep | `scripts/emit_sweep.py --patterns-file <bench list> --no-corpus ...`, once main names the list |
| routed floors | commit `routed_floors_measured.tsv` as `docs/design/memfn/r17b_prime/fdb2/routed_floors.tsv` (fdb2_report §10.6). Re-run the routed census on this tip first if the merge is suspected of moving it |

Main still has to rule on two things: the lever fence entry for
`run_arm_reach.sh` (ruling 4) and whether to accept or drop R-MS6
(`drop_rms6.diff`, ruling 5).
