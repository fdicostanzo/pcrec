# sp1bfix -- review fixes for span_pick stage 1, unit 1b

Lane sp1bfix (sonnet) for the kit manager. Branch `lane/memfn-sp1bfix`, cut from `lane/memfn-sp1b` @ cca35ffd1.
Review: `/var/tmp/pcrec-pcrec/scratch/memfn/sp1bfix/review.md`. Rulings R1..R14 as the kit manager's brief gave them.
Stage 1 stays byte-identical: no emitted byte, no pcrec abi, no MF_CLASS_V, no MF_SITE_ABI move.
NOTE: `docs/dev/lanes/sp1bfix_deliver.txt` did not exist at start; the brief listed it as a deliverable, so this
lane WROTE it (modelled on sp1b_deliver.txt) so lanecheck can run. Replace it if the manager wants other sections.

## What changed

- Mech rows S1094 and S1096 re-anchored (tests/mech/sabotages/); S1094 now plants in `memfn/src/window.c`.
- `tests/memfn/mass_check.c`: 5 new goldens for the cap over the TOTAL of 2+ rated positions; `MASS_FLOOR` 20 -> 25
  (`tests/memfn/run_finder.sh`, `tests/memfn/CLAUDE.md`).
- Comments and docs: `memfn/src/kit.h` (TIE readers), `memfn/src/window.c` (LEFTMOST = LOWER, T_* names live in kit.h),
  `memfn/src/presence.c` (kit_mass's NONE-row exceptions), `docs/design/memfn/window_site.md` section 2.1,
  `docs/design/memfn/span_pick.md` section The tables (named exceptions).
- D187 count: trace-build-only `MFTRACE KITMASS calls=C cubes=Q nonnormal=N mask0=M` (memfn/src/presence.c), summed by
  `tests/memfn/reach_equal.py` into `nonnormal-cubes N mask0-cubes M`; format in `memfn/docs/trace_format.md`.
  No behaviour or shape change to kit_mass or kit_pos.

## By id

| id | ruling | what I did / evidence |
|---|---|---|
| R1 | FIX-NOW | S1094: SAB_FILE window.c, plant in `kit_tie_member_key`: `(0xFFFFu - o) << 8 \| byte` (the ORDER field complemented, an UNKNOWN order 0 goes highest, the byte still breaks an equal order upward). Intent is the member ORDER, as the original `oa < ob` was (it left the byte compare alone). S1096: the whole tie condition `(wm == wl && kit_tie_takes(T_WINDOW, w, at))` replaced by `wm <= wl` (tie to the rightmost window), the same mutant. HAND-MEASURED (sabotaged scratch copy built, `tests/codegen/run_cand_oracle.sh` the candoracle arm's own command): clean tree 178 pass 0 fail; S1094 plant 163 pass **8 fail** DETECTED; S1096 plant 173 pass **5 fail** DETECTED. Figures in SAB_DOC_FIGURE. `python3 -I scripts/m6read_check_sab_anchors.py`: `sabotages checked: 1102 (1141 anchor sites)` / `all anchors resolve` (was STALE ANCHORS: 2). `VALIDATE_ONLY=1` over S1094 S1096 S1097 S458: 4 valid. No real mech run (the matrix takes the box lock; left to the gate shard, jobs 377/378/379). |
| R2 | FIX-NOW | Goldens: all x2 under rate2 (2,560,000 uncapped, CAP 1,000,000); two 128-byte half cubes under rate2 (640,000 each, 1,280,000 uncapped, CAP 1,000,000); half cube + set abc, CAP 655,000 (under the cap). MASS_FLOOR 25 (25 run, 25 pass). Plant (per-position cap, no total cap) on a scratch copy: RED 3 (`CAP rated two full sets capped: got 2000000, want 1000000`; `CAP rated two half cubes capped: got 1280000`; plus the old `NONE k=512 capped`), the two new rated cases being the ones the old golden set missed. Tree not edited by the plant. |
| R3 | main's | not mine |
| R4 | FIX-NOW | kit.h comment scoped to the PICK ties of window.c's choosers/run_member and presence's set pick/window; names window.c's direct `wf_ties[T_CMODEL/T_MARGIN].to` reads, presence's run_scan and translate's run rank (1c joiners), P2/P4. |
| R5 | DOC | window.c enum line: `LEFTMOST = LOWER over window starts`; name kept. |
| R6 | FIX-NOW | window_site.md section 2.1 TIE table: T_PRES_MEMBER row added; T_WINDOW row names its reader `kit_tie_takes`. |
| R7 | folded into R8 | the count below; no shape change. |
| R8 | count only | see Counter reading. |
| R9 | DOC | named in kit_mass's comment (presence.c) and as a row of span_pick.md section The tables, named exceptions (retires when presence joins the call or a priced NONE row lands). |
| R10 | NOTED | not mine. |
| R11 | DOC | one line under window.c's TIE header. |
| R12 | REJECTED | not mine. |
| R13, R14 | NOTED | not mine. |

## Counter reading

Trace build (`CFLAGS=-DMF_TRACE`, sp1bfix tip), per-process line `MFTRACE KITMASS calls=C cubes=Q nonnormal=N mask0=M`.
The tag is `KITMASS`: every MFTRACE reader in the tree matches another prefix (`REACH table=`, `FD `, `FDROUTE `,
`END `, `ASK `, `grep -v '^MFTRACE '`), `reach_equal.py` ignores non-REACH lines by its regex, and the emitted C is
untouched (the lines go to stderr), so base-vs-head comparison sees no diff: checked, reach_equal --limit 300 x 2 arms
reports 0 patterns differing; a tool-side filter was therefore not needed. `reach_equal.py` now also sums the line
over its runs (informational, never a verdict; BASE prints none) and prints `nonnormal-cubes N mask0-cubes M`
before its DONE trailer; the reach gate job declares that line.
Light readings (this lane, not the gate):

| population | compiles | runs with a KITMASS line | calls | cubes | nonnormal | mask0 |
|---|---|---|---|---|---|---|
| reach_equal --limit 300 (the first 300 of the sorted corpus+bench union), arms default and `-e utf8`, head side | 600 | 498 (both arms) | 125,180 | 34,766 | **0** | **0** |
| bench list + job 588 sample + zzzzzzz~J (379 distinct patterns), default | 379 | 317 | 212,156 | 51,418 | **0** | **0** |
| the same, `-e utf8` | 379 | 321 | 230,840 | 49,440 | **0** | **0** |
| the same, `--engine=vm` | 379 | 319 | 238,528 | 274,336 | **0** | **0** |

Control (so a zero is a reading, not a dead counter): `mass_check.c` linked against `build/libpcrec_mftrace.a` prints
`calls=25 cubes=50 nonnormal=0 mask0=3`; a 4-line program passing `{t=0x41, mask=0xF0}` prints `nonnormal=1`.
Zero non-normal and zero mask-0 cubes over about 1,360 compiles (a sample, not the full gate population): per D187
the set-only conversion goes with unit 1c if the gate-wide count (reach job, 18 arms, full corpus) is also zero.

## Validation

All light, in the lane (main's queue had mech S1159 running; nothing here took the box lock).

| check | command / file | result |
|---|---|---|
| build | `make -j8` | clean |
| strict | `make strict` | rc 0 |
| finder + golden | `make test-memfn-finder` (run_finder.sh, part `mass`) | `mass checks passed: 25`, failed 0; section total 1960 passed |
| census | `make test-memfn-rows` | passed 57, failed 0 |
| anchors | `python3 -I scripts/m6read_check_sab_anchors.py` | all anchors resolve (was 2 stale) |
| mech fields | `VALIDATE_ONLY=1 run_sabotage_matrix.sh S1094 S1096 S1097 S458` | 4 valid |
| candoracle hand plants | see R1 | S1094 8 fail, S1096 5 fail, clean 0 |
| byte identity spot | frozen base `scratch/memfn/sp1b/ref/build/pcrec` vs this tip's build/pcrec, 330 patterns (bench list, 588, zzzzzzz~J) x arms default and `-e utf8`, stdout + stderr + rc | 660 of 660 identical |
| trace identity spot | frozen base -DMF_TRACE vs this tip's, 95 patterns, default arm, stdout, rc, and the whole stderr less the one KITMASS line | 95 of 95 identical |
| make test-codegen | NOT run whole (its group runs about 15 scripts; far over 5 minutes); only its [SABANCHOR] part, the anchor script above | zero stale |

Not run (owed to the gates): make test, the identity sweep, reach equality over the full population, mech for real.

## Gate jobs

Prepared, NOT queued, in `/var/tmp/pcrec-pcrec/scratch/memfn/sp1bfix/jobs/` (copied from sp1b's: keys `kit-sp1b2-*`,
`TREE=worktrees/sp1bfix`, outputs under the sp1bfix scratch, the frozen BASE b0f3d0339 builds read from
`scratch/memfn/sp1b/`). All ten dry-run rc 0:

370-kit-sp1b2-strict, 371-kit-sp1b2-memfn, 372-kit-sp1b2-reach (now also declares `nonnormal-cubes N mask0-cubes M`),
373/374/375-kit-sp1b2-ident1..3, 376-kit-sp1b2-test, 377/378/379-kit-sp1b2-mech..mech3 (same 45 rows; S1094 and S1096
were already in the list; no row retired). The chain order is sp1b's (strict, memfn, reach, ident1-3, test, mech1-3).
Nothing was queued and no mech.sh was run.

## OWED

Every gate in the list above (none launched, by the brief). The counter's gate-wide value arrives in job 372's log as
`nonnormal-cubes N mask0-cubes M`. The real S1094/S1096 mech rows run in shards 377/378/379.

## STATE AT HANDOFF

OWED: none queued by this lane (gates are prepared, not launched). Everything is committed on `lane/memfn-sp1bfix`.
