# sp1b — span_pick stage 1, unit 1b (primitives: U4 one mass primitive, U5 one tie spelling)

Lane sp1b (opus), branch `lane/memfn-sp1b`, cut from main b0f3d0339 (units 1a, 1f, 1g landed). Design of
record: `docs/design/memfn/span_pick.md` rev 5.2 §Staging (unit 1b's row and its witness row), §What stage 1
deletes, the Ratchet text; D186 + addenda 1-2. Build go: the owner's conditional approval of 2026-11-02,
confirmed by main's GO for stage 1. Scope: unit 1b only.

## What changed

- **U4, ONE mass primitive** (`memfn/src/presence.c`, declared in `memfn/src/kit.h`):
  `kit_mass(rate, pos, n, cap)` over a POSITION MULTISET. A position (`kit_pos`) is a stated byte set
  (`set`) or else the cube (`t`, `mask`), the bytes t | f for f a submask of ~mask, enumerated exactly as
  `cube_mass`/`window_mass` did. A byte repeated across positions is counted at each (the run window's
  `zzzzzzz~J`). `cap` is `KIT_MASS_CAP` (1e6, `kit_set_mass`'s) or `KIT_MASS_SUM` (`kit_set_sum`'s,
  PICK's cube mass); the order is unchanged: truncate the 64-bit sum to 32 bits, then cap. **The declared
  NONE row** is the primitive's no-rates branch, with its comment citing span_pick [rev5.1 R2] and D186
  add. 2: floor(k x 1e6 / 256) over the WHOLE member count, taken once (62,500 at k = 16, not 62,496).
  The rules therefore rank by member count, and their own tie rows break an equal count. Its density
  readers (HORS_MIN, MARGIN) stay the named exception.
  DELETED: `cube_mass`, `window_mass`, `kit_set_mass`, `kit_set_sum` and the helper `uniform_mass`.
  Callers moved: presence.c's set pick, run scan, run window, set-leads and the landmark admission (the
  per-factor round-up product stays the caller's, and its per-factor set is still built as
  `(b & mask) == t`); window.c's `a_parked_choose`, `a_model_choose`, `a_mass_choose`, `run_member`,
  `translate`'s run rank (still set-shaped, its cube built into a set: 1c's to change) and `d_hors_holds`.
- **U5, one tie spelling**: `tie_over` is DELETED. P3's set pick now reads a new TIE row,
  `T_PRES_MEMBER` (TIE_HIGHER over `kit_tie_member_key`: member order above the byte; an UNKNOWN order is
  0, below every known one, since a stated order is 1..256 under `kit_presence_check`). Presence's run
  window now reads `T_WINDOW` (TIE_LEFTMOST). Its start walk is ascending, so the leftmost keeps the tie
  as before. window.c's `tie_takes` became the kit-wide `kit_tie_takes`, which answers TIE_LEFTMOST as
  TIE_LOWER (`c < b`). Before this, it answered 0 for LEFTMOST, and LEFTMOST had no reader. The row enum
  (`T_MASS_STRETCH` .. `T_PRES_MEMBER`, `T_N`) moved from window.c to kit.h. The `wf_ties` table and
  `wf_tie_to` stay in window.c.
- **Census** (`tests/memfn/decider_census.tsv`, `.py`): `tie_over` is out. `window.c tie_takes` is
  renamed `kit_tie_takes`. `window.c kit_tie_member_key` (TIE) is in, and so is
  `kit.h kit_tie_takes excluded` (its prototype, like `kit_walk`'s). The run-window part's
  retires-column reads "- (reads T_WINDOW since 1b)". MEMBER_COUNT 50 -> 51. ONE RULE ADDED to the
  checker: a member's own namespace line in its file (`#define NAME MF_NS(NAME)`, exactly its name)
  belongs to the member. Without it, kit.h's `#define kit_tie_takes MF_NS(kit_tie_takes)` would be a
  stray backstop hit. Any other line naming `tie_takes` still counts.
- **Golden-value test** `tests/memfn/mass_check.c` (new; white-box like proven_check.c). It runs as part
  `mass` of `tests/memfn/run_finder.sh` (`make test-memfn-finder`), floor 20.
- **Mech** S1097 and S458 are RE-ANCHORED from `cube_mass(rate, (unsigned)q, 0xFFu) <` to
  `kit_mass(rate, &qp, 1, KIT_MASS_SUM) <` (the same `<` -> `<=` plant, intent unchanged), each with a
  header line saying so.
- Docs: `memfn/src/CLAUDE.md` (presence.c's row), `tests/memfn/CLAUDE.md` (mass_check.c's row),
  `memfn/docs/journal.md` (one entry).

Commits (oldest first): 6b62b8b00 (code), 21bf4094c (test, census, mech anchors), 2e91cf6a0 (docs), then
this report.

**Stage-1 statements.** No emitted-byte mover by construction: the same arithmetic over the same inputs
with the same truncation order (spot check below, 1251 of 1251 identical). **NOT an MF_CLASS_V event**:
no finder row was added or removed, so `pres_row` does not move. **No MF_SITE_ABI field moves**:
`memfn/include/memfn.h` is untouched; every change is behind kit.h. No pcrec abi change. **No docs/spec
hunk**: `git grep` over `docs/spec` for `cube_mass|window_mass|kit_set_mass|kit_set_sum|tie_over|
tie_takes|kit_mass|wf_ties|T_WINDOW|T_PRES_MEMBER` finds nothing; no caller-visible name changed.

## Readers (by grep)

`git grep` at HEAD for each deleted name and for `tie_takes`, over the whole tree, excluding worktrees/,
the build dirs and docs/dev/lanes/:

| reader | names | disposition |
|---|---|---|
| memfn/src/presence.c | all five masses, `tie_over` | definitions deleted; callers on `kit_mass`, the TIE table |
| memfn/src/window.c | `kit_set_mass` (:421, :472, :1596), `kit_set_sum` (:552, :774, :1334), `tie_takes` (3 calls) | on `kit_mass`; `kit_tie_takes` |
| memfn/src/kit.h | `kit_set_mass`, `kit_set_sum` prototypes, defines | replaced by `kit_pos`, `kit_mass_cap`, `kit_mass`, the T_ rows, `kit_tie_takes`, `kit_tie_member_key` |
| memfn/src/CLAUDE.md | `kit_set_mass`/`kit_set_sum` | row restated |
| tests/memfn/decider_census.tsv | `tie_over`, `tie_takes` | rows edited (above) |
| tests/memfn/decider_census.py | backstop shape `tie_takes` | kept; namespace-line rule added, MEMBER_COUNT 51 |
| tests/mech/sabotages/S1097, S458 | `cube_mass` in SAB_BEFORE/AFTER | re-anchored, intent unchanged |
| memfn/tests/run_g2_win.sh, S1417 | `wf_ties[T_MARGIN]` line | unchanged (that line did not move) |
| src/core/findings.c (`uniform_mass`, `cube_mass`), S461 | pcrec's OWN copies | KEPT (D157: pcrec's findings copy stays; span_pick §What stage 1 deletes, U4's "later") |
| docs/design/stream/roadmap.md §5 R22/R23 | recipes name the deleted functions | main's: R22 needs restating (Ratchet below) |
| docs/design/memfn/span_pick.md, units_inventory.md, memfn/docs/ideas.md, docs/dev/reviews/*, docs/dev/plan.md, dev_journal.md, docs/design/*/call_graph*.txt and sabotage_anchors*.tsv, studies/*/results/*anchors*.tsv | the old names | history / design record, not edited |

## Ratchet

Roadmap §5 R20-R27 recipes: sp1a's scratch transcription (`$PCREC_TMPDIR/scratch/memfn/sp1a/ratchet.sh`,
copied to `scratch/memfn/sp1b/ratchet.sh`), plus `ratchet_1b.sh`, whose R22 also counts the surviving
primitive `^uint32_t kit_mass\(`:

    == base b0f3d0339 (ratchet.sh, ratchet_1b.sh)
    R20=3 R21=1 R22=3 R23=1 R24=2 R25=1 R26=0 R27=0 total=11
    R20=3 R21=1 R22=3 R23=1 R24=2 R25=1 R26=0 R27=0 total=11
    == HEAD (ratchet.sh, ratchet_1b.sh)
    R20=3 R21=1 R22=-1 R23=0 R24=2 R25=1 R26=0 R27=0 total=6
    R20=3 R21=1 R22=0 R23=0 R24=2 R25=1 R26=0 R27=0 total=7

**11 -> 7**: R22 3 -> 0 (-3), R23 1 -> 0 (-1). The design allows R22 -2 or -3 and R23 -1, so 7 or 8.
Roadmap §5's R22 recipe as written counts only the four deleted names minus 1, so it reads **-1** at HEAD.
Restated, it should count the one survivor, `kit_mass`, too (0). The unit kept no counted name as a thin
caller (all four mass names and `tie_over` are gone whole). **For main**: restate R22's recipe before
landing.

## Validation

All runs were light, in the lane, on worktrees/sp1b at 2e91cf6a0's code (the report commit adds only
docs). Main's queue job 331-main-recida3 held the box, and it was not a timing job.

| check | file / command run | result |
|---|---|---|
| build | `make -j8` | clean, no warnings |
| strict | `make strict` | rc 0 |
| census | `make test-memfn-rows` (run_rows.sh + decider_census.py) | 57 passed 0 failed; backstop 39 hits (floor 30), 0 outside a member; plant window.c 2 stray RED, plant presence.c `c < sm` 1 stray RED, prototype plant RED |
| finder + golden | `make test-memfn-finder` (run_finder.sh, part `mass`) | 1955 passed 0 failed; `mass checks passed: 20`, `ok mass: 20 cases passed >= floor 20` |
| link / R-28 | `make test-memfn-link` | 11 passed 0 failed |
| G2 quick | `make test-memfn-g2` | rc 0, 70,358,652 passed 0 failed, 413 s (above the brief's ~5 min, run once) |
| golden plants | tests/memfn/mass_check.c built against a scratch copy of memfn/src with ONE edit each (`scratch/memfn/sp1b/plant.py`) | **set-shaped** (positions unioned): RED 4 (zzzzzzz~J 3322 vs 10054, NONE 11718 vs 35156, ...); **NONE per position**: RED 2 (62496 vs 62500; 35154 vs 35156); **cap ignored**: RED 3 (1280000 vs 1000000, ...). The tree was never edited (no revert needed) |
| byte identity spot | `scratch/memfn/sp1b/spot.py`: frozen base build (git archive b0f3d0339) vs HEAD, the three patterns files (417 patterns: bench 392, job 588's 24, `zzzzzzz~J`) x arms default, `-e utf8` (the NONE row everywhere), `--engine=vm`, `--features all`, `.c` + `.h` + rc + stderr compared | **1251 of 1251 identical** (77 refused identically on both sides); 2502 compiles, one process, nice 19, outside the box lock as the brief's light validation allowed |
| reach smoke | `tests/memfn/reach_equal.py --limit 25`, pzzz + p588, arms default / `-e utf8` / `--engine=vm` / `--memfn=no-pres-set-lead`, base vs HEAD MF_TRACE builds | 0 differing keys of 120, no gone rows (LIMITED: a smoke run, not a verdict) |
| mech fields | `VALIDATE_ONLY=1 run_sabotage_matrix.sh` over the 45 gate rows | 45 definitions valid (incl. re-anchored S1097, S458) |

Not run (owed to the gates): make test, the full identity sweep, full reach equality, mech for real.

## Gate jobs

Prepared, NOT queued, in `$PCREC_TMPDIR/scratch/memfn/sp1b/jobs/`. They were adapted from sp1gfix's: keys
`kit-sp1b-*`, `TREE=worktrees/sp1b`, `BASE=b0f3d0339`, frozen base builds `scratch/memfn/sp1b/ref/build/pcrec`
and `scratch/memfn/sp1b/ref-mftrace/pcrec`, and patterns files `p588.txt` and `pzzz.txt` copied into
sp1b's scratch. **Every job's `--dry-run` exits 0.** They chain with `after` in this order:

| job | what | est / cap |
|---|---|---|
| 360-kit-sp1b-strict | `make -j16; make strict` | 240 / 1200 s |
| 361-kit-sp1b-memfn | test-memfn-rows, -finder, -link, -g2, -arms, -stamps, -deleg, -manifest, test-findings, test-registry (10 sections) | 1100 / 2700 s |
| 362-kit-sp1b-reach | HEAD MF_TRACE build; reach_equal.py vs base, corpus + 3 files, 18 arms (default, vm, -fmemfn-simd, -e utf8, the 12 kit denies, `--analysis weblog` alone and with -e utf8); NO `--gone` (1b deletes no row) | 1250 / 3600 s |
| 363/364/365-kit-sp1b-ident1..3 | emit_sweep's 67 declared identity arms at b0f3d0339 + 2 analysis arms (C streams only: `--streams c-default,c-vm`), 23 per shard, `--ref-bin` the frozen base | 2450 each, run-total 7350 / 3600 s |
| 366-kit-sp1b-test | `make test` ALONE via `scripts/perfrun --label sp1b` | 1800 / 3300 s |
| 367/368/369-kit-sp1b-mech..mech3 | 45 rows FOR REAL, 15 per shard; S917, S919 DECLARED UNREACHED (shard 1 trailer `unreached: 2`) | 1800 each, run-total 5400 / 3600 s |

**Mech row list, derived two ways.** (A) Every row whose `SAB_FILE` is a file 1b edits: presence.c 12
(S270 S286 S288 S317 S458 S1094-S1099 S1856), window.c 4 (S1415 S1416 S1417 S1419), kit.h none. (B) Every
row of the `memfnfinder` arm, which runs run_finder.sh (changed: part `mass`): 31 rows (S917 S919 S1018
S1020 S1079-S1084 S1089 S1100 S1103 S1105-S1110 S1122 S1221 S1224 S1225 S1419 S1543-S1548 S1856). The
union is 45. The census files (decider_census.*) are read by `make test-memfn-rows`, which no mech arm
runs, so they add no row. S917 and S919 are UNREACHED for the LOCKDOWN reason, unchanged by 1b, as at
sp1g's shard 1 (job 357's trailer `unreached: 2`).

No dumps delta is declared on any identity arm: 1b moves no `--list-*` row (only internal kit names
changed), so no `--dumps-declared-*` is needed on the base or start arms.

## Design deviations

1. **A position is a stated byte SET or a cube**, where the design says "a list of cubes". window.c's
   positions are arbitrary sets, and the landmark admission builds each factor's set as `(b & mask) == t`.
   On a run byte with bits outside its mask, that set differs from the cube enumeration t | f, and
   `kit_presence_check` does not refuse such a byte for presence spans. A set position keeps every caller
   verbatim on every input. A cube position keeps `cube_mass`/`window_mass`'s enumeration, so a repeated
   byte still counts per position. It is still ONE primitive over a position multiset. This reshapes no
   output, and nothing is a mover.
2. **`T_PRES_MEMBER` is TIE_HIGHER over a packed key** (order << 8 | byte), not a new `wf_tie_to` value.
   The design's "second comparator shape" is the key, `kit_tie_member_key`, which sits in window.c's TIE
   section beside the table.
3. **Ratchet count**: the brief said 11 -> 8 or 9. The design's deltas (R22 -2/-3, R23 -1) give 7 or 8,
   and the measured result is 7. Roadmap §5 R22's recipe needs restating (above).
4. **The census checker gained one rule** (a member's own `MF_NS` namespace line is the member's). It is
   needed because `kit_tie_takes` is now kit-wide and declared in kit.h.
5. **The DELIVER file** `docs/dev/lanes/sp1b_deliver.txt` was written BY THE LANE, because the brief asked
   for it. BOILERPLATE says the manager writes it, and that sp1gfix's lane wrote its own.

## Charter vs committed

| promise (span_pick rev 5.2 1b rows, the brief) | artifact |
|---|---|
| U4 one mass primitive over a position multiset, repeated byte per position | `kit_mass`, presence.c; golden MULTI cases; set-shaped plant RED |
| capped/uncapped argument | `kit_mass_cap` (KIT_MASS_CAP / KIT_MASS_SUM); golden CAP cases; cap plant RED |
| NONE-mode total 62,500, not 62,496 | the NONE branch (one floor over k); golden `NONE k=16 (16 one-byte positions)`; per-position plant RED |
| landmark per-factor round-up product stays its caller's | presence.c's landmark block, unchanged arithmetic |
| the DECLARED NONE row (uniform ppm, tie by member count, density readers the named exception) | `kit_mass`'s header comment; kit.h's section comment; the HORS_MIN/MARGIN exception unchanged (census rows `d_hors_holds`, `m_margin_holds`) |
| U5 `wf_ties` stays with the presence-member row; run window reads T_WINDOW | `T_PRES_MEMBER` row + `kit_tie_member_key`; run window's `kit_tie_takes(T_WINDOW, ...)` |
| deletes 2-3 mass variants, 1 tie spelling; R22 -2/-3, R23 -1 | 4 mass names + `uniform_mass` and `tie_over` gone; R22 -3, R23 -1 (Ratchet) |
| golden-value test (NONE at k = 1, 3, 6, 16, 256; repeated byte per position; capped vs uncapped), independent of the primitive | tests/memfn/mass_check.c (literal values derived in comments), part of test-memfn-finder, floor 20 |
| green, and RED under a plant, then reverted | Validation: 3 plants RED in scratch copies; the tree was never edited |
| no-mover on every arm | spot check 1251/1251; **full witness OWED**: jobs 362-365 |
| not MF_CLASS_V, no MF_SITE_ABI field, no abi, no spec hunk | What changed, "Stage-1 statements" |
| readers by grep with dispositions | Readers |
| CLAUDE.md, kit journal, census map/ratchet | memfn/src + tests/memfn CLAUDE.md; journal entry; census 51; Ratchet |
| gate jobs prepared, dry-run rc 0, mech derivation stated | Gate jobs |
| roadmap R22 recipe restated | **OWED, main** (before 1b lands) |
| responses-ledger line | **OWED, kit session** (single writer; no seam event to announce, only the unit's done line) |
| the gates' verdicts | **OWED**, the manager's queue run of jobs 360-369 |

## STATE AT HANDOFF

STATE: delivered; the gate jobs are prepared and NOT queued. Code complete for unit 1b at the branch head.
Light validation is green (above). OWED: the gate run (jobs 360-369 in `scratch/memfn/sp1b/jobs/`, keys
kit-sp1b-strict, -memfn, -reach, -ident1..3, -test, -mech..mech3), which the manager queues; main's
restatement of roadmap §5 R22; and the kit session's responses line. No rulings file was named in the
brief. A fresh agent resumes from the job results. All green means 1b's witness is complete. Any byte
moved on an identity arm, or any reach difference, is a STOP per the brief.
