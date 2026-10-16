# grid2p — the PREP lane for the zen4-grid2 timing slot, BUILT AND CHECKED (not run)

Lane grid2p, 2026-10-16, branch `lane/grid2p` (cut from main `063b4a4b4`; see "Branch base"),
sonnet. The task: build and check the harness for `r17b_prime.md` §5.4 (D167 option (B): ONE
streamed condition). **The timed slot was not run**: the manager runs it on a quiet box. Nothing
under `src/`, `memfn/src/`, `lib/` moved (no pcrec byte, no abi event). Everything the lane's
runs wrote is under the worktree's gitignored `build/` (`build/dry/`, `build/full/`).

## Summary

1. `docs/dev/lanes/grid2/` extends grid1: it reuses grid1's driver, loader, checker, legs and
   arm-table reader, and adds the three new variant generators, the streamed subject generator,
   the item manifests, a libpcre2 oracle, method `kit-grid@2`, one `slot.sh`, and the paranoid
   suggestion with its check. Contract and launch command: `grid2/README.md`.
2. **DRY: green end to end.** `DRY=1 bash slot.sh <dir>` built, gated and timed the 2-3-groups-per-item
   subset with every optional pass in 128-169 s on a box at load 8-20 (two runs). Verdict
   `COMPLETE ... required=ok optional=done`. Evidence: `grid2/evidence/dry_slot.status`,
   `dry_time_F1.log`, `dry_estimate.txt`; the live files are `build/dry/` (gitignored).
3. **The FULL design was built and gated without the clock**: 176 subjects (752 MB) generated in
   26 s with every planted-count self-check passing, the whole build in 78 s, then the gate:
   200 groups, 1,006 items, 183 libpcre2 oracle lines, **2,809 legs OK, 0 FAIL**
   (O 191, R 806, L 806, C 1,006), 138 reach rows with 0 unreached, 84 landing-fidelity rows OK,
   50 one-byte groups reached (U2), 0 excluded, in 70 s. Then `time.sh` ran every group of all
   three timing phases with `NOCLOCK=1` (rows 749 / 80 / 296). `evidence/full_check.out`,
   `full_all.status`, `full_estimate.txt`.
4. **The gate's failing direction**: `plants.sh` (7 plants on the new arms: a wrong one-term SWAR
   lane, a wrong BASE walk table, a wrong NONE arm, a wrong twin walk helper, a wrong twin V1 mask,
   a wrong scaffold helper, the streamed cursor not cycling) are all DETECTED, the three on pickable
   arms by exit 3 with a `PICKABLE-FAIL` line, the four instrument-arm plants by an `excluded`
   row; the restore is green again (`evidence/dry_plants.out`). `paranoid_check.sh`: 60 checks, 0 fail.

## The wall estimate, and whether I believe the spec's 88 min

`estimate.py` (run by the DRY slot; `evidence/dry_estimate.txt`) multiplies the FULL design's
launches by the DRY run's measured seconds per launch, by phase and subject class.

| phase | groups | launches | est. min (two dry runs) | basis |
|---|---|---|---|---|
| F1 (items 1+2, non-F3 cells) | 115 | 2,938 | 30.5 - 36.1 | measured 0.62 - 0.74 s per launch |
| F3 (items 1+2, member-free) | 10 | 306 | 3.2 - 3.9 | measured |
| OB (items 3+4) | 50 | 1,054 | 11.4 - 11.8 | measured |
| build + subjects (measured, full) | | | ~1.7 | 78 s + 26 s |
| gate (measured, full) | | | ~1.2 | 70 s |
| **required** | | | **46 - 54** | spec 88 |
| TRIG (item 8) | 12 | 163 | 1.7 | measured |
| perf items 6-7 | | 405 rows | 1.6 | measured 0.2 s per row |
| **with the optional items** | | | **50 - 58** | spec 96 |

The spread between the two dry runs is the box: both ran at load 8-20 from other sessions
(`uptime` 19.7 at the end of the second), on a pinned CPU 12-15 whose neighbours were busy.
Plus quiet-gate waits, which the estimate cannot know, and a RERUN SHARE of 20% (EP69, an
estimate: a dry run takes one launch and cannot measure it; each +10% share is about +0.8 min).

**I do not believe 88 for this implementation, and I can say why.** The spec's figure is
regime_eval §2.1's formula `149 groups x ~7 arms x 3.4 launches x 0.95 s`. (1) 0.95 s per launch
is grid1's cost for a **64 MiB** streamed subject (load time dominates); this harness streams
**4 MiB** per subject (64 x 64 KiB, regime_eval §2.4's own judge condition and a fraction of the
7700X's 32 MiB L3), and a launch is then the driver's own floor, 50 ms calibration + 7 x 50 ms,
~0.62 s on a quiet box. (2) The 149 grid1 fit groups map to **121** distinct streamed groups
(D1's repeated and D2's streamed twin are one group once both are streamed; `fit_map.tsv` maps
every one of the 149). The two together are 0.65 x 0.81 = 0.53 of the spec's item 1+2 figure,
which is what the table shows. If the manager wants grid1's 64 MiB totals back,
`GRID2_STREAM_MIB=64` regenerates them and the wall returns to about 70 min. The spec's ~10 min
for the gate assumed grid1's deep legs; they are off here (R, L, C only, as the spec lists), and
the measured full gate is 70 s.

## What was built, against the brief (charter vs committed)

| charter item | committed | where |
|---|---|---|
| `mkvar` variant: dispatch scaffold with `f` forced to each form | yes | `mkvar2.py disp` (arms `tw0 tw1 tw2`; FORM 2 splices mkvar's v32 function in as `__next_candidate__w32`) |
| `mkvar` variant: NONE (the use's FIND deleted) | yes | `mkvar2.py ob ... none` (arm `none`, five kinds) |
| `mkvar` variant: V1 one-term | yes, with a deviation | `mkvar2.py ob ... v1` (stateless; see Deviations 4) |
| (also needed) walk-only scaffold (M18) | yes | `mkvar2.py scaf` (arm `sc0`) |
| item 1: streamed subject generator, importable by E4 | yes | `streamgen.py` (`write_stream`, `verify_stream`, `disjoint`, `window_stream`, `synthetic_stream`, `nbuf_for`); design in `design2.py` |
| item 2: twin manifest | yes | `groups2.tsv` items 12/2 (`evidence/full_groups2.tsv`) |
| item 3: one-byte cell manifest (5 kinds x 6 gaps find-all + 4 lengths) | yes, 50 groups | `ext/ob/arms.tsv` via `design2.py` |
| item 4: NONE manifest | yes, 30 groups (rides item 3's gap groups) | the `none` arm in `ext/ob` |
| items 6-8 optional passes | yes | `f2perf.sh` (items 6, 7), `time.sh` TRIG phase (item 8) |
| `slot.sh`: method `kit-grid@2`, CPU 14, rotated, 7 rounds, LAUNCHES 3 (+2 by the rerun rule), quiet gate at every group boundary | yes | `slot.sh`, `time.sh` |
| correctness gate FIRST (legs R, L, C; base vs libpcre2 10.46 through `tests/oracle/`'s local adapter); a pickable arm's failure FAILS the run | yes | `check.sh` (exit 3, `SLOT_FAILED pickable-arm-answer-failure`) |
| progress lines and a final COMPLETE/FAILED in a status file; everything under the slot dir given as an argument | yes | `slot.sh` |
| the paranoid SUGGESTION in `slot.sh`/`time.sh`/`f2perf.sh` with its check | yes | `paranoid.sh`, `paranoid_check.sh` (60 checks) |
| a DRY mode, and the wall estimate from the dry run's per-row cost | yes | `DRY=1`, `estimate.py` |
| `grid2/README.md`, `grid2p_report.md`, CLAUDE.md entries | yes | `grid2/CLAUDE.md`, `lanes/CLAUDE.md`, `grid1/CLAUDE.md` (the two hooks) |

## Deviations and things the spec text did not say

1. **Branch base and the compiler.** `lane/grid2p` was cut from main, whose compiler lacks
   `--memfn=no-pf-terms-mask` and the V1 row (`pf_terms_mask`), both on `lane/memfn-r17`. I wanted to
   reset the branch onto the kit branch; `git reset --hard` was refused by the permission layer, so
   `build.sh` takes the compiler from `PCREC=` (default `worktrees/memfn-r17/build/pcrec`, read-only
   use) and stops loudly if it lacks the deny. The lane's commits are docs-only files under
   `docs/dev/lanes/`, so merging the branch into the kit branch should be conflict-free (the only
   shared file is `docs/dev/lanes/CLAUDE.md`, one appended bullet).
2. **Streamed size is 4 MiB per subject**, not grid1's 64 MiB (above). Pre-registered in
   `streamgen.py`, not fitted; `GRID2_STREAM_MIB` overrides. Buffers: 64 x 64 KiB; 16 at 1 MiB; at
   most 1,024 for tiny n (the n = 48..128 points keep 1,024 distinct buffers, a 48-128 KiB stream).
3. **Item 2's twin arms ride item 1's groups** instead of forming separate "twin groups": the
   interleave is within a group, so a twin is timed beside the single form it is compared against
   (V1 and A1 are item 1 arms). Twin groups are 20 dense F1 groups, the F3 member-free groups (8), the
   n = 48..128 points (5) and two new dig points (n = 8, 32) = 35 groups x 3 arms; `sc0` rides the
   R0-shaped member-free groups (`hex-run`, `word-eq`, and the new `wcls` = `\w+=`) = 6 groups.
   The spec's "8 x 3 + 20 x 3 + 6 x 2" counted 96 arm-launches per round; this has 111 launches per round, +1.3 min.
   `f` is forced through an opaque compare (`(n - lo) >> 62`): a constant `f` is folded away by gcc
   (checked in the objdump; the first version of `tw0` had no dispatch left).
4. **V1 one-term is stateless.** A libc-site artifact has no declaration point for V1's per-activation
   cache, so the one-byte `v1` arm is the W8 block over `pcrec_mfk_w8_eq` without the cache
   (grid1's `Sn`/`An` are the same idea at W64). grid1's M3 (1,0,0) rows give the cached figure. Say so
   when M20 is read.
5. **Item 3/4 cells are emitted with `-fno-req-byte -fno-req-run`**: the whole-window pre-check would
   answer a member-free subject before the site ran (UNREACHED, the row would time the pre-check).
   The pre-check itself is item 8. The five patterns are `xy+z` (DFA_SCAN forward), `xy+(?=z)`
   (bounded), `\bx[a-z]+\b` (DFA_HAT), `xy+z` with `--engine=vm -fprefilter` (HYB_PF), `(?m)^xy+z`
   (ATTEMPT_PRED: the `(?m)^` skip's `memchr` for the newline; its "back" is the kit's term offset -1,
   the libc text is forward). The find-all groups use L = 64 KiB (one match per buffer; the spec fixes
   gaps, not L). ATTEMPT_PRED takes `libc`, the hand walk (its base `walk`) and `none`, as the spec says.
6. **Item 8's "DFA-route TUG cells" is a choice**: `trig-dig` (`[0-9]+x`) and `trig-word`
   (`[A-Za-z_]+=`), required byte early (offset 64) / late (n - 64) / absent, g in {8, 32}, `first`
   mode; keep = the default compile, drop = `-fno-req-byte -fno-req-run`: 12 groups, 2 arms.
7. **GATE-ONLY groups (added)**: the F3 groups hold no match, so a wrong twin or scaffold helper on
   hex-run / word-eq / quad / wcls cannot change an answer there (plant `sc0walk` would have been
   UNDETECTED). Four dense subjects `g2-gate-<cell>-S` carry those arms through the gate's legs; they ride
   `arms_f2.tsv`, so `time.sh` never times them and `f2perf.sh` skips them.
8. **Pickable** = `walk V1 S1 A1 A3 libc v1 loop none keep drop`; twins and `sc0` are instruments (excluded
   under `ALLOW_EXCLUDED=1`, the slot refuses otherwise). The deep legs (E N F A) are off.
9. **The rerun rule's NULL** is `0.031 x median(base)` (M6's eps), the only quantity that exists before
   the group's A/A floor does; `RERUN_NULL` overrides. regime_eval §2.4's abort rule (EP40-43) is the
   judge slots', not grid2's: the harness records load1 at both ends of each group and re-queues a group
   whose end load1 reached 3.0 once.
10. **grid1 was touched twice, additively**: `build.sh` `EMIT_CELLS` and `check.sh` `ORACLE_CMD`
    (both inert when unset; both named in `grid1/CLAUDE.md`).
11. **Item 6 reads groups2.tsv, not `arms_f2.tsv`.** The first version put item 6's K-arm rows into
    `arms_f2.tsv` under the timed groups' own keys; `check.sh`'s `group` ran each key twice and the
    second run truncated the first's results, so the dense groups' twin legs silently vanished from
    `check.log` (found because plant `tw0walk` read UNDETECTED). Fixed; the plants now read as above.

## For the manager

- Launch: `grid2/README.md` (the command); `PCREC=` must be the kit-branch compiler.
- Before the slot, once: `OUT=<slot dir> bash grid2/paranoid_check.sh` after a build (writes only under
  `<slot>/tmp/`, never the slot's own provenance) and `OUT=<slot dir> bash grid2/plants.sh` after a green
  check (rebuilds and restores the planted arms; run it on the DRY directory, not the real slot's).
- The slot's `ESTIMATE` status line (time.sh's) uses the measured 0.65 s per launch.
- E4 imports `streamgen`: `sys.path.insert(0, ".../grid2"); import streamgen as sg; sg.write_stream(dir, bufs)`.
- Owed to nobody here: nothing is OWED by the lane; the timed slot is the manager's.

## Files

`docs/dev/lanes/grid2/` (README, CLAUDE.md, slot.sh, build.sh, check.sh, time.sh, f2perf.sh, design2.py,
streamgen.py, mkvar2.py, estimate.py, paranoid.sh, paranoid_check.sh, plants.sh, ext_ob/, ext_trig/,
evidence/); two env hooks in `grid1/{build,check}.sh`; this report; index lines in `lanes/CLAUDE.md`.
