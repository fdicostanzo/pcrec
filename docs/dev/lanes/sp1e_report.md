# sp1e — span_pick stage 1, unit 1e: the phase-2 tables

Lane sp1e (opus), kit manager's brief of 2026-11-05. Branch `lane/memfn-sp1e`, cut from main
20fb73159 (units 1a, 1f, 1g, 1b, 1c, 1d landed). Build go: Frank's conditional approval
(2026-11-02) and main's GO for stage 1. Design of record: `docs/design/memfn/span_pick.md` rev 5.2,
§Staging row 1e and its witness row; `units_inventory.md` U3, N4, N5, N11.

**Result.** T-FIND is ONE walk. It serves both askers, and the asker fact states the difference
between them. Window.c's Table D is gone:

- D-hors is the finder table's first FIND row, unchanged.
- D-one, `c + 1`, is the resume of every other row's renderer.

`fd_route` is merged into `fd_find`. The composer asks with no stop, then renders the pick through
its declared renderer rows (`fd_renderers`). E-find asks with the stop, then renders through
Table B's renderer rows. B-hors now carries D-hors's text, and B-fn keeps its reconciliation with
fn_rows' BODY.

| Item | Outcome |
|---|---|
| Emitted bytes | none moved |
| pcrec abi | no change |
| docs/spec | no hunk |
| MF_SITE_ABI | 23, unchanged |
| MF_CLASS_V | 7 -> 8 (the finder listing gained D-hors ahead of the PRES rows, so `pres_row`/`pres_led` moved up one) |
| Ratchet R20 | 3 -> 2 |
| REACH | equal through the declared row map |

## What changed, by file

- `memfn/src/finder.c`
  - **D-hors row.**
    - It is slot FIND's FIRST row, ahead of today's order (D1, D1c, D1w, PAIR, R7w).
    - Pick FF_HORS, deny `window-skip` (unchanged, the same options.def row), basis
      UNMEASURED-DEFAULT, citing job 581 and HORS_MIN PROVISIONAL.
    - Facts: `SF_HORS_WINDOW` (bit 16) and `SF_HORS_DENSE` (bit 17).
    - Contract `ct_d_hors`: uses none, serves everything except `core`, which is CM(CORED), as in
      Table D.
  - **`hors_facts`.** This is Table D's `d_hors_holds` predicate, moved. It reads HORS_MIN from
    `plan_cost.def` through a finder-local `MF_COST` enum.
  - **`SF_WINDOW_STOP` renamed `SF_ASKER_PAIR`** (bit 15, same meaning: the asker renders PAIR).
    This is units_inventory's N4, "kept, renamed".
  - **`FD_SERVES_COMMON`** now serves the seven window fields MF_ANY. They are stated only when the
    window family asks; the gate verdict for every older row is the same as before. `FD_CT_T`
    gained a `cores` column.
  - **`fd_route` deleted**, merged into **`fd_find`**, THE ONE WALK:
    - `st` NULL is the composer: scope check, `find_facts`, and the `?need` refusal, exactly
      fd_route's.
    - `st` non-NULL is the window stop: set and offset facts, need REQUIRED, `hors_facts`, and the
      asker fact.
  - The pick-to-arm `switch` left this file (it now lives in the composer's renderer rows).
- `memfn/src/kit.h`
  - `fd_route`'s prototype deleted.
  - `FF_HORS` added.
  - `fd_stop` gains `hw`, `wlo`, `whi`, `rate`, `wf` and `renders_pair`.
  - New `fd_find` signature and comment; the `wf_plan_brow` comment updated.
- `memfn/src/compose.c`
  - `fd_renderers[]`, the composer's renderer rows: a first match over (pick, end_back), giving
    the arm.
  - `fd_renderer`, its reader.
  - `select_arm` asks `fd_find(..., NULL, ...)` and then the renderer rows.
- `memfn/src/window.c`
  - Table D deleted: `wf_drows`, `wf_dtable`, `d_hors_holds`, `d_one_holds`, its contracts,
    `WF_HORS_ID`, `drow`, `wf_d_text`.
  - New B row `B-hors` (pick FF_HORS, libc 0, path `+hors`, prepare `d_hors_prepare`).
  - `wf_brows` gains `path` and `prepare` columns.
  - `wf_b_text` is now the renderer rows' text (head, next, define); the old find-only table is
    renamed `wf_b_find`.
  - `wf_find_decide` builds an `fd_stop`, using `hors_window` for D-hors's window, and asks
    `fd_find` once.
  - Header and section comments name T-FRAME and T-FIND.
- `memfn/include/memfn.h`: `MF_CLASS_V` 8, with its history note.
- `memfn/src/options.def`: a comment only (`window-skip` denies T-FIND's D-hors). The registry text
  is unchanged.
- `tests/memfn/row_map.tsv` (NEW): the DECLARED row map.
  - `wfD D-hors -> fd D-hors`.
  - `wfD D-one -> - -`, dissolved.
- `tests/memfn/rows_check.py`: new section M, the row map, covering the derived row set, rows.tsv,
  and "no traced compile names a mapped-away table". `Art.tables` was added for it.
- `tests/memfn/reach_equal.py`
  - `--map FILE`: BASE's END selections of the mapped-away table are counted under the target's
    key; dissolved rows are printed per arm. The run is red if HEAD prints a mapped-away table's
    record, or if a target is never chosen.
  - `--no-corpus`: a smoke run, LIMITED trailer.
- `tests/memfn/rows.tsv`, `row_floors.tsv`, `run_rows.sh`
  - New fd `D-hors` line: witness `[0-9a-f]{8}`, signature ` row=D-hors arm=E-find`, control under
    `--memfn=no-window-skip`.
  - Floors PLACEHOLDER/PLACEHOLDER.
  - ROWS_FLOOR 30 -> 31.
- `tests/memfn/finder_check.py`: `FIND_ROWS` gains D-hors first.
- `tests/memfn/decider_census.tsv`, `.py`
  - `fd_route` row out; `hors_facts` and `fd_renderer` in; `d_hors_holds` out.
  - Retire triggers of `fd_find`, `wf_find_decide` and `wf_prepare` set to `-` (done at 1e).
  - MEMBER_COUNT 52 (unchanged net); HITS 37 -> 36, because `kit_walk(&wf_dtable` is gone.
- `memfn/tests/run_g2_win.sh`: plant S1542 re-aimed from window.c's Table D predicate to finder.c's
  `hors_facts`, with the same intent (the `whi >= 0` scope dropped).
- `tests/mech/sabotages/S1079_fd-d1-unrouted.sh`
  - Re-anchored from `fd_route` into `fd_find`, for the composer's ask only (`!st`), so the window
    stops stay untouched; the intent is unchanged.
  - Hand-measured DETECTED figure recorded.
- Docs
  - `memfn/docs/trace_format.md`: the wfD walk folded into fd, the D-hors FDROUTE line, the reach
    registry.
  - `memfn/docs/finder_history.md`: a row-edit log line.
  - `memfn/src/CLAUDE.md`, `tests/memfn/CLAUDE.md`, `memfn/include/CLAUDE.md`, all within their
    12 KB limits.
  - `memfn/docs/journal.md`: one entry.
  - The lanes history index entry.

## Byte identity: the argument

The emitted text is a function of (frame row, method row, renderer row). 1e changes the walk that
picks the method row; it does not change any row's text.

1. **Composer asks** (`st` NULL).
   - D-hors's predicate needs `SF_HORS_WINDOW`, which only a stated stop sets, so it is PRED_FALSE
     (DENIED under `no-window-skip`) on every composer ask.
   - A non-matching first row does not change which later row matches first. The rest of the walk
     is fd_route's walk: the same facts, gate input and tctx (table `fd`, handle `nsites+1`,
     optional 1).
   - `fd_renderers` maps each pick to the arm the deleted switch named: LIBC by end_back,
     LIBC_BACK, WALK by end_back, every other pick NULL. So the arm is the same.
2. **Window asks** (`st` set).
   - Base walked Table D first. Its D-hors used the deny `window-skip`, the CORED contract, and the
     predicate `hw && whi-wlo >= 1 && whi >= 0 && mass >= HORS_MIN`.
   - HEAD's D-hors has the same deny and contract, and `hors_facts` is that predicate (the same
     `kit_mass` call).
   - When it holds: B-hors is the one renderer row that holds on FF_HORS. Its libc 0, its path
     `+hors`, and its text and preparation (`d_hors_head/next/define`, `d_hors_prepare`) are Table
     D's D-hors text. Base's `bren = NBROWS` also gave libc 0.
   - When it does not hold: the rest of the walk is base's `fd_find` walk. The new fact bits are
     read only by D-hors, and the window fields' MF_ANY serves change no verdict. So the pick and
     the B row are base's, and the text is D-one's (`d_one_head/next`), as before.
3. **Text.** No text function changed. The tables that index them are re-keyed: `wf_b_text` by
   `bren`, which replaces `wf_d_text` by `drow`.

The identity spot check and REACH equality below confirm the argument.

## Declared trace changes (MF_TRACE builds only; no byte)

- The wfD SEL/ROW/END records are gone. E-find's stop is one `table=fd` walk, D-hors first.
- Every fd FIND walk gains a ROW record for D-hors (PRED_FALSE, or DENIED under its deny).
- D-hors chosen writes `MFTRACE FDROUTE ... row=D-hors arm=E-find`, and its WPATH reads `fd=D-hors`
  (base: no FDROUTE, `fd=-`).
- The reach registry gains `REACH table=fd row=D-hors` (D-hors uses no field, so it has no field
  cells).
- The finder listing (`--finder-rows`) gains D-hors as its first row (the MF_CLASS_V bump).

## MF_CLASS_V and MF_SITE_ABI

- **Probe.** `arm_fixtures --finder-rows`, base against HEAD, differs by exactly one added line:
  `D-hors FIND PE HORS - window-skip UNMEASURED-DEFAULT S3 -`.
- **Effect.** `pres_row` is 1 + its listing index, so every PRES row's index moved up one. This
  makes it an MF_CLASS_V event, 7 -> 8 (precedents: 1a gave 6, 1f gave 7).
- **pcrec.** pcrec reads `pres_row`/`pres_led` only through the same build's listing
  (`src/gen/memfn_sites.c` :715-736, PCREC_CAND_TRACE), so nothing caller-visible moves.
- **MF_SITE_ABI** stays 23: no field, layout or vocabulary move.

## Grep reader table

Excluded: worktrees/, build dirs, docs/dev/lanes/.

| name | live readers updated | left as history |
|---|---|---|
| `fd_route` | compose.c (select_arm), kit.h (prototype), finder.c (definition and comments), decider_census.tsv, S1079 | finder.c's one "until 1e" sentence; finder_history.md; run_sabotage_matrix.sh's re-anchor log; design docs (span_pick.md, units_inventory.md, r17b_prime.md, window_site.md, roadmap.md); docs/dev/reviews/*; docs/dev/history/* |
| `SF_WINDOW_STOP` | finder.c (PAIR row, fd_find), now `SF_ASKER_PAIR` | finder.c and kit.h "until 1e" notes; finder_history.md; design docs; reviews |
| `wf_dtable`, `wf_drows`, `d_hors_holds`, `d_one_holds`, `WF_CT_D`, `WF_NDROWS`, `WF_HORS_ID`, `wf_d_text`, `drow` | window.c (deleted), decider_census.tsv and .py (rows and HITS), run_g2_win.sh S1542 | design docs (window_site.md, units_inventory.md, span_pick.md); reviews |
| `wfD` (trace table name) | trace_format.md, rows.tsv comment, row_map.tsv, rows_check.py M, reach_equal.py --map | span_pick.md; reviews |
| `D-one` (row name) | window.c and finder.c comments (now "the resume"), row_map.tsv (dissolved), trace_format.md, options.def comment | journal, ideas, responses, design docs, reviews (history) |
| `D-hors` (row, now table fd) | rows.tsv, row_floors.tsv, finder_check.py FIND_ROWS, run_rows.sh ROWS_FLOOR, trace_format.md, finder_history.md | (no stale reader found) |

- **Anchor checker.** `python3 -I scripts/m6read_check_sab_anchors.py` first reported 1 stale row,
  S1079 (fd_route's line). After the re-anchor: "sabotages checked: 1102 (1143 anchor sites), all
  anchors resolve".
- **S1079, hand-measured DETECTED.** I applied the plant to a git archive of 7d5d6711c, built it,
  and ran `tests/memfn/run_finder.sh` against its libpcrec.a: memfnfinder 6fail/3155pass. byte1t
  and hat1 were decided by no row, and the routed census and lever cases fell under their floors.
  The row's figure is recorded in its file.

## Ratchet counter

The counter is roadmap §5's recipes, run by sp1d's `ratchet.sh`:

```
== base (20fb73159 archive)
R20=3 R21=1 R22=0 R23=0 R24=0 R25=1 R26=0 R27=0 total=5
R24-restated=0 (kit_run_member 1, rank-loop 0, p3-scan 0, run_member-own-mass 0)
R21-restated=0 (a_model_choose 0, a_mass_choose 0, cands 1)
== HEAD
R20=2 R21=1 R22=0 R23=0 R24=0 R25=1 R26=0 R27=0 total=4
R24-restated=0 (kit_run_member 1, rank-loop 0, p3-scan 0, run_member-own-mass 0)
R21-restated=0 (a_model_choose 0, a_mass_choose 0, cands 1)
```

R20's written recipe sees the change: `fd_route` 1 -> 0; `fd_find`, `select_arm` and BODY stay at
1 each, so the count is 3 -> 2. No restatement is needed. With main's restated R21 (0), the
stage-1 kit-row total is 4 -> 3.

## Validation (light only; Linux dev box, 2026-11-05, outside 20:00-01:00)

| Check | Result |
|---|---|
| `make`, `make strict` | rc 0, both before and after the last code commit |
| `make test-memfn-rows` | 222 passed / 0 failed; census 67/0. New section M: "row map: 2 lines, mapped-away tables ['wfD'], 118 traced compiles read" |
| `make test-memfn-finder` (run_finder.sh, incl. purity) | 3163 passed / 0 failed |
| `make test-memfn-arms` | 374 passed / 0 failed |
| `make test-memfn-g2` (once, after the last code commit 7b336b732; 15:42-15:48) | 70,358,652 passed / 0 failed, incl. the window family (10,444) |
| G2 window plants `run_g2_win.sh --plant "S1542 S1423 S1425"` | all RED (LOUD): S1542, re-aimed at `hors_facts`: "D-hors scope: a skip table over a window wholly below the candidate"; S1423 (127 fail) and S1425 (70 fail), whose D-hors text did not move |
| `make test-codegen` (a test script changed: run_rows.sh) | rc 0; every part 0 failed |
| Anchor checker | clean (1102 rows, 1143 sites) |

**Byte identity spot check** (`scratch/memfn/sp1e/ident/spot.sh`, frozen 20fb73159 build against
HEAD `build/pcrec`; stdout and stderr both compared):

- 1021 pairs, 2042 compiles: 1021 SAME, 0 differ, 0 rc-differ.
- Population: 405 distinct patterns (the bench list, job 588's sample, zzzzzzz~J, sp1c's extras,
  and 5 witnesses for window and find sites).
- Every pattern at the default arm.
- Every 4th pattern also at `-e utf8` (NONE), `--engine=vm`, `-fmemfn-simd`, `--analysis weblog`,
  the all-tie regime (`-I tests/findings/adversarial --analysis=uniform`) and
  `--memfn=no-window-skip`.
- Multi-target .rxt: a 6-target source (hex window, PAIR, one byte, cube, run, walk) pooled with
  examples/makefile's two sources, 9 artifacts (18 files), at default, `-e utf8`, `--engine=vm` and
  `-fmemfn-simd`: identical.
- Classification: **SAME** on every compare (no SILENT-MOVE, no LOUD).

**REACH equality through the row map** (sample, `--no-corpus`; the same 405 patterns at default,
`-e utf8` and `--analysis weblog`; MF_TRACE builds of 20fb73159 and HEAD):

- 0 patterns differ on every arm.
- Row sets: 31 = 31.
- `mapped wfD/D-hors -> fd/D-hors: chosen BASE 21 HEAD 21`.
- Dissolved D-one, base chosen: 119 / 94 / 114.
- No derived gone rows. Failing sets are identical (26/25/26, rc1 on both sides).
- Trailer: `LIMITED rc=0 differ=0`.

**Plants** (each red, then deleted):

| Plant | Classification | Result |
|---|---|---|
| rows_check M with a bogus map line (`fd D1 -> fd D-hors`) | LOUD | `FAIL: row map (1e): fd/D1 moved away but is still a row`, checks failed 1 |
| reach_equal with BASE as HEAD | LOUD | "HEAD prints a record of the mapped-away table wfD" on 3 of 5 patterns, plus "row sets differ ... lost fd/D-hors" |
| reach_equal without `--map` (smoke, 600) | LOUD | 507 patterns differ (fd/D-hors base None, head 0): the map is load-bearing |

## Gate jobs (prepared, NOT queued)

`/var/tmp/pcrec-pcrec/scratch/memfn/sp1e/jobs/`, ids 420-429, keys `kit-sp1e-*`.

- TREE=worktrees/sp1e, BASE=20fb73159.
- Frozen base builds: `scratch/memfn/sp1e/ref/build/pcrec` and `.../ref-mftrace/pcrec`.
- The patterns files were copied into this lane's scratch.
- Every job dry-runs rc 0 and has a literal `--ready` case.
- All 10 were accepted by the scratch queue: `PCREC_BOXQUEUE_DIR=.../sp1e/bqtest boxqueue add
  --no-start`, status "runner: none", 10 pending.

| id | key | what | after |
|---|---|---|---|
| 420 | kit-sp1e-strict | make strict | - |
| 421 | kit-sp1e-memfn | rows, finder, link, g2, arms, stamps, deleg, manifest, findings, registry | 420 |
| 422 | kit-sp1e-reach | REACH equality over the corpus + 4 files, `--map tests/memfn/row_map.tsv`, 19 arms (default, vm, simd, utf8, 12 denies, weblog, utf8+weblog, uniform), no --gone | 421 |
| 423-425 | kit-sp1e-ident1..3 | emit_sweep identity, 67 declared arms + an-weblog, an-weblog-utf8, an-uniform = 70, 3 shards | 422, 423, 424 |
| 426 | kit-sp1e-test | make test via perfrun | 425 |
| 427-429 | kit-sp1e-mech, -mech2, -mech3 | 50 mech rows, 17/17/16 | 426, 427, 428 |

How the mech rows were derived:

- (A) Every row whose SAB_FILE/SAB_FILE2 is a file 1e edits gives 38 rows:
  - finder.c, 12: S277 S278 S316 S452 S457 S917 S1020 S1079 S1103 S1105 S1108 S1122.
  - window.c, 6: S1094 S1095 S1415 S1416 S1417 S1419.
  - compose.c, 19.
  - memfn.h, 1: S526.
  - kit.h and options.def: none.
- (B) Every memfnfinder row gives 31 (finder_check.py changed).
- The union is 50. The runner's VALIDATE_ONLY reports 50 definitions valid; that is not a mech
  run.
- DECLARED UNREACHED: S917 and S919, in shard 1 (UNR=2).
- Not added:
  - memfnarms rows outside the union: 1e changes no run_arm_pins.sh mode, and the section is in job
    421.
  - Rows for rows_check.py, decider_census.py and reach_equal.py: these feed no mech arm; they are
    sections 421 and 422 and the lane's plants above.
  - S1542: G2's own plant, run by test-memfn-g2 in 421.

## Seam notes (principle 9: every seam a document; observations only)

- **The T-FIND seam is now one question: `fd_stop`, or NULL.** Written out as text, a window ask
  would carry:
  - the set (32 bytes) and the offset;
  - D-hors's window (`hw`, `wlo`, `whi`);
  - the rate table's identity (not its 256 words);
  - the asker fact;
  - the window facts the gate classifies.

  The composer's ask carries only the site. That asymmetry is the remaining OFS/composer split U3
  leaves to stage 3 ("not on OFS").
- **The asker fact `renders_pair` is a capability of the asker, not a fact of the stop.** Serialized
  for another process, it would be the renderer side's declaration ("I render PAIR, HORS"). Today
  the composer's `fd_renderers` table states that list implicitly: no PAIR or HORS row. A future
  seam could derive the asker fact from the renderer table instead of a hand-set bit. Not built;
  noted only. The design says it retires at 3.0.
- **The rate table crosses the seam by pointer.** As text it would need the measurement set's
  identity (the `analysis` bundle's digest), which the kit already has for its `mf_akind`, rather
  than the 256 words.
- **D-hors's window** (`hors_window`, read off the chosen alternative's verify-YES span) is
  computed by the asker, before the ask. It is a fact about the plan, not about the stop, so a
  serialized ask carries a value the planner side computed. That is in the direction of the kit
  split (planner, then back end).

## Design deviations

- **None in emitted bytes or decisions.**
- `SF_WINDOW_STOP` is RENAMED (`SF_ASKER_PAIR`), not deleted. This follows span_pick.md's map, "N4
  kept, renamed `[rev3 P1]`", and the design says the asker fact retires at 3.0.
- The composer's renderer rows are a new declared row list (`fd_renderers`). They replace the
  `switch` that was in finder.c. The brief's "compose's arms[] ... become renderers keyed by (frame
  row, method row, renderer row)" is met for the T-FIND pick. compose's `arms[]` walk for non-T-FIND
  sites (`select_arm`'s remainder) stays the named exception, per R20.
- The trace changes above are declared, not byte changes. reach_equal's map synthesizes BASE's
  wfD END counts, because base printed no wfD REACH line.

## Charter vs committed

| charter item | committed |
|---|---|
| T-FRAME (Table E, legacy first) at text time | yes, order kept (window.c Table E unchanged) |
| T-FIND one walk with the asker fact, Horspool row first, then today's order | yes: fd_rows D-hors, D1, D1c, D1w, PAIR, R7w; `fd_find` both askers; SF_ASKER_PAIR |
| renderer row keeps the reconciliation (B-fn/B-pair) | yes (B-fn, B-pair unchanged; B-hors added) |
| compose's arms / fd_find's text become renderers keyed by (frame, method, renderer) | yes for the T-FIND pick (`fd_renderers`, `wf_brows`/`wf_b_text`); select_arm and BODY stay named exceptions |
| delete fd_find/fd_route's second entry walk | yes (`fd_route` deleted; Table D's walk deleted) |
| no MF_SITE_ABI event | yes (23) |
| MF_CLASS_V iff pres_row shifts, by grep and probe | probed: the listing gains a row ahead of PRES, so 7 -> 8 |
| witness: DECLARED wfD -> fd row map (rows.tsv, row_floors.tsv, rows_check derived set, MFTRACE table names) | yes: row_map.tsv; rows.tsv and floors lines; rows_check M; trace_format.md |
| REACH EQUALITY through the map | yes: reach_equal --map; sample 0 differ; gate 422 over the corpus |
| ratchet R20 -1 with counter output | yes, 3 -> 2 (output above); no restatement needed |
| zero movers, no pcrec abi, no docs/spec hunk | yes (spot 1021/1021 SAME; no caller-visible reader: the `--list-axes` text is unchanged, and pcrec reads pres_row through the same build's listing) |
| grep readers; anchor checker; re-anchor with hand-measured DETECTED | yes (table above; S1079 6fail/3155pass) |
| CLAUDE.md files, one kit journal entry | yes |
| light validation (make, strict, finder, rows, arms, run_finder incl. purity, rows_check through the map, G2 once, anchors, spot, REACH sample) | yes, all green |
| test-codegen if test scripts are touched | yes, rc 0 |
| gate jobs 420-429, scratch-queue accepted, `--no-start` | yes |
| `docs/dev/lanes/sp1e_deliver.txt` | ABSENT: no such file in the worktree or the main tree. I did not invent one (sp1dfix wrote its own deliver file after an earlier one) |
| report + lanes history index | yes |

## STATE AT HANDOFF

STATE: done. OWED none: this lane queued nothing. Gate jobs 420-429 are prepared in
`/var/tmp/pcrec-pcrec/scratch/memfn/sp1e/jobs/` for the kit manager to queue (`boxqueue add`, without
`--no-start`, against the real queue). The scratch test queue `.../sp1e/bqtest` was never started.
Branch tip: the commit that adds this section. The worktree is clean except the deliver file.
