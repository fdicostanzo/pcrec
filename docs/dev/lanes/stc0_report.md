# stc0 — [START-TABLE] C0: the sweep instrument and the Q3 trace experiment

Lane stc0, 2026-10-06, opus. Branch `lane/stc0` off main `73f66ba9`. The work is
tooling only, and nothing under `src/` changes on the lane branch. The trace
prototype lives on the scratch branch `scratch/stc0-trace` (worktree
`worktrees/stc0-trace`) and is NOT merged. The design is
`docs/design/start_table.md` rev 2.1, §3.2 C0, §3.3 items 2-5, and §6 Q3/Q7.

**Status:** the light work is complete and validated. Three things are owed:
- (a) the every-flag deny sweep and the full two-build gate run. Both are heavy and
  armed as one detached chain that waits for main's `.lift`; see §6.
- (b) the S-ids for the six sabotage rows. They are drafted and validated, but
  not committed until main allots a block.
- (c) the Q7 census-script move, which this lane did not take on (§7).

## 1. Deliverables

`scripts/emit_sweep.py`:
- **Stream 6, `facts`.** `--features all --emit-facts=byte,utf8 --pattern P` over
  streams 1/2's patterns, identity required. It takes no `--extra`, because the
  listing compiles both encodings itself. The note's "five streams" text was
  already corrected to six in §R.1; the script's own header now says SIX.
- **`opt_argv(extra)`**, the ONE splice point every argv builder calls (streams
  1-4, the arms, the trace).
- **`--extra=ARGS`** (repeatable, shell-split) and **`--extra-base=ARGS`**. Streams
  1-4 run at base+extra on both sides. Streams 1-2 also count, per side, the
  DIFFER against the base. The run FAILS unless `DIFFER_PINS` has a floor for
  that (base, flag), or `--no-differ-floor` waives it loudly.
- **`--arms start`**, over the DISTINCT corpus patterns (`deny_census.py`'s
  population, so the two instruments count one set). `DIFFER_PINS` has 62 pinned
  cells plus 2 asserted zeros:
  - the 14 deny/force flags (the 13 `START_FLAGS` + `-fno-length-prune`), times
    {byte, utf8} bases, times {c-default, c-vm};
  - plain `-e utf8` (byte base);
  - `-i` at both bases;
  - a NULL arm (an empty flag) that must read exactly 0;
  - `ASSERT_ZERO`, which is `-fno-end-window` at utf8, both streams.

  Each cell holds:
  - a per-side bytes floor;
  - a start-stamp floor (`start_keys_moved`, the census's own "visible" definition);
  - a manifest: one named pattern that must differ on each side, the shortest
    mover in `deny_movers.tsv`. The plain arms use `a`. `-fno-length-prune` uses
    `(a)*b`, found by probing and verified in all four cells.

  A (0, 0, None) cell is a flag that does not act on that route, and its only
  check is identity. Off the full corpus (`--no-corpus`/`--limit`/`--every`),
  floors are NOT applied and the report says so. The checks that still apply
  there are identity, manifests in the population, the asserted zeros and the
  null arm, because a zero holds on any subset. Per-arm results go to
  `arms.tsv`.
- **`--patterns-file FILE`** (repeatable; `--list-source` escapes, with a new
  `encode_escape` inverse that is round-trip tested). Also **`--no-corpus`**,
  **`--every K`** (deny_census's exact sampling rule) and
  **`--streams LIST`**.
- **`build_from_rev(..., cflags=)`** and **`--build-cflags`**. These are the
  `-D` pass-through: `make -j4 CC=… CFLAGS=…`, with the same cflags on both
  sides.
- **`--trace`**. Both sides are built with `TRACE_CFLAGS = -O2 -g
  -DPCREC_CAND_TRACE`, or taken from `--trace-bin`/`--trace-ref-bin`. Streams
  1-2 run with stderr captured, kept apart from stdout. The sweep tags every
  `CANDTRACE` line with its pattern index, arm and seq; the compiler prints none
  of them. The output is `trace_{a,b}.tsv`. The trace build's stdout is checked
  against the same side's default build, per pattern, by hash. Then
  `trace_diff.compare` runs, with `--trace-declared` and `--trace-unordered`, and
  a records-per-arm floor (`TRACE_RECORDS_FLOOR`, applied on the full corpus).
- **Same-binary mirroring.** When the two sides are one file (realpath), each
  argv compile runs once. The run is reported as a MEASUREMENT.
- **The start-family stamp parser moved here.** `START_STAMPS`, `stamps_of`,
  `route_of` and `start_keys_moved` used to live in
  `docs/design/start_table/row_census.py`. That file now re-exports them, and
  `deny_census.py` calls `es.start_keys_moved`. One implementation, so the gate
  and the census cannot disagree about "a start stamp moved".
- **PINS re-pinned to the measured reach** (one-binary run, all six streams,
  `73f66ba9`):

  | stream | measured | old pin | new pin |
  |---|---|---|---|
  | reach, stream 1 | 4,159 | 3,480 | 4,110 |
  | reach, stream 2 | 4,160 | 3,480 | 4,110 |
  | reach, stream 3 | 4,160 | 3,480 | 4,110 |
  | facts (new) | 4,119 | — | 4,070 |
  | argv rows | 4,606 | 3,900 | 4,550 |
  | composition files | 369 | 300 | 360 |
  | producing | 38 | 32 | 38 |
  | artifacts | 108 | 88 | 100 |

  The margins are the originals' (~1% on the argv axes, zero slack on producing).

**`scripts/trace_diff.py`** (new). It compares two trace streams per (pattern,
arm):
- ORDERED by default. `--unordered` compares the SET of records, ignoring order
  and multiplicity; that mode exists because of §4's finding.
- `--declared FILE` filters a site's records from both sides. A declaration that
  filters nothing on the working side FAILS, as stale.
- `--min-records N` applies to every arm present. With no arm present, an int
  floor FAILS.
- `--keys`.
- Exit codes: 0 clean, 1 differ, 2 bad input.

**Self-tests** (`scripts/tests/`, D48 on-change; the mech arm `emitsweep` runs
both):
- `emit_sweep.py.test` (7 checks, ~4 s): the arms over their own manifest
  population; an unpinned `--extra` arm must fail; the escape round-trip.
- `trace_diff.py.test` (17 checks, pure python). It covers:
  - a planted swap, a reorder and a cross-pattern swap (multiset-equal);
  - a row change;
  - undeclared and declared additions, and a stale declaration;
  - empty streams with and without a floor, a one-side-empty stream and a floor
    above the records;
  - a bad header;
  - three `--unordered` cases.

  Its first run caught a real hole in `trace_diff.py`: an int floor over NO arms
  checked nothing (the empty-vs-empty shape). It was fixed before landing.

**`tests/mech/run_sabotage_matrix.sh`** has the new suite word `emitsweep`
(vocabulary entry + arm), registered before its rows.

**`docs/design/start_table/trace_experiment.py`** → `trace_experiment.tsv` (§4).

**Docs updated:**
- `scripts/CLAUDE.md`, `scripts/tests/CLAUDE.md`;
- `docs/design/start_table/CLAUDE.md`;
- `docs/testing.md` (the emit_sweep section);
- `docs/dev/lanes/CLAUDE.md`;
- `docs/design/start_table.md`: §3.2's C0 row marked DONE, plus a "C0's
  outcome" paragraph, and §6 Q3's result block.

`make strict`: clean (`strict: whole tree compiles clean with -Werror -Wshadow`).

## 2. Controls: the failing direction

| control | plant | result |
|---|---|---|
| dropped `--extra` on both sides (plumbing) | `opt_argv` returns `[]` | `emit_sweep.py.test` RED: every manifest fails ("0 arms differ on both sides"), the one-arm `--extra` run fails |
| dropped `-e utf8` on both sides | `opt_argv` drops `-e`/`utf8` | RED: the asserted zero reads byte's count (`-fno-end-window` utf8 ≠ 0), the plain `-e utf8` manifest fails. As the note predicted, the `--extra-base='-e utf8' --extra=-fno-start-set` single arm still PASSES (it moves at byte too); the by-design controls are what catch it |
| each floor when its arm's flag is removed | as row 1 (every arm's flag removed at once) | every arm reads differ = 0, so every manifest fails. The null arm proves the counter reads exactly 0 on an identical argv (0/0 on both streams). Every nonzero floor is therefore violated by arithmetic. This was not re-run over the full corpus per arm; that would be 62 heavy runs for a deterministic 0 |
| unpinned arm | `--extra=-fno-scan-edge` | FAILS "NO DIFFER FLOOR PINNED" (in the self-test) |
| trace ordered compare | multiset instead of sequence | `trace_diff.py.test` RED (swap-caught, reorder-caught) |
| trace empty floor | the no-arm branch disabled | RED (empty-floor-caught) |
| trace per-arm floor | `got < fl` never true | RED (floor-above-records) |
| trace stale declaration | the not-observed check disabled | RED (declared-stale) |
| trace records floor, real binaries | `--trace` with the HOOKLESS main build as both trace bins | FAILS: `RECORDS FLOOR side a arm c-default: 0 < 89135` (×4), `trace: FAIL`, rc 1. The same run with the prototype trace build: CLEAN, rc 0 |
| trace build moves no emitted byte | prototype trace build vs main's default build, 4,606 rows × 2 streams | stdout differs on 0 / 0 patterns per stream |

**Cross-implementation check** (1-in-10 sample, 360 distinct patterns,
`--every 10`): `emit_sweep --arms start` (one binary) and `deny_census.py
--flags=<the 14 + --encoding=utf8,-i> --every 10` agree on all **62 of 62**
(base, flag, stream) cells: bytes movers, start-stamp movers and refusal moves.
The byte comparisons are separate code. The stamp parser is now shared (§1), so
the stamp column agreeing tests the counting, not the parser.

**Sabotage rows (drafted, ids owed).** Six rows on arm `emitsweep`, all
DETECTED when planted against the two self-tests:
- **A** `opt_argv` drops every option;
- **B** `opt_argv` drops `-e utf8`;
- **C** trace order ignored;
- **D** empty-trace floor disabled;
- **E** per-arm floor disabled;
- **F** stale declaration accepted.

Draft anchors are in `worktrees/stc0-scratch/rows/rows.json`. They need an S-id
block from main (the kit holds S530-S549; this lane did not take one). They then
become `tests/mech/sabotages/S<id>_*.sh`, one per row, `SAB_SUITES="emitsweep"`,
`SAB_EXPECT=DETECTED`.

## 3. The every-flag deny sweep

**OWED** (heavy). `deny_census.py` over the 29 `--list-axes` flags outside
`START_FLAGS`, full corpus × 4 arms, jobs 6. The list is derived from the
`--list-axes` `cli_flag` column and is identical to `allflags_sample.tsv`'s 29.
`-fno-length-prune` is already a deny arm in `DIFFER_PINS`, pinned from the
sample as a lower bound (a subset's movers never exceed the whole's). The
sweep's own job is to (1) re-pin those four cells and (2) report the non-start
movers: flags that move a start stamp without a route change, beyond the
sample's `-fno-length-prune`, `-fno-ctx-node`, `-fno-splice-calls` and
`-fno-cls-kit`. Output: `worktrees/stc0-scratch/heavy/allflags/deny_census.tsv`
(+ transitions/hidden/movers).

Cost estimate, measured on this lane's runs: the 1-in-10 sample with 16 flags
took 135 s at `-j2`, so expect ~15-25 min at `-j6`. The note's 54 min came from
a different sample's rate.

## 4. Frank's Q3 trace experiment — BAR MET

**Prototype.** `scratch/stc0-trace` @ `7ed6af9c`: 39 lines, all under
`#ifdef PCREC_CAND_TRACE`. A `PCREC_CAND_TRACE_REC(slot, route, row, site)`
macro in `src/core/internal.h` prints `CANDTRACE slot route row site func` to
stderr at each walk's RETURN. The sites:
- `dfa_pf_of` (`pf-of`), `vm_start_row` (`vm-start`) and
  `pcrec_dfa_scan_state_written` (`scan-state`), slot NEXT;
- `dfa_form_derive` (`form-fwd`/`form-other`), slot NEXT;
- `req_admit` (PRESENCE), `req_use` (FIRST);
- `dfa_search_start_of` (RECOVER);
- `vm_plan_reseed`'s chosen row (RETRY);
- the end-window clamp, an INLINE site (WINDOW).

`row` is the row's name string. `site` is a declared literal. `func` is
`__func__`, carried only to measure brittleness.

**Population.** 3,595 distinct corpus patterns × streams 1-2. The parent prints
69,095 / 29,766 records. Over the 4,606 corpus rows emit_sweep reads, it prints
89,135 / 38,523: those are the pinned floors, lower bounds for C1's superset of
sites. The trace build's stdout is byte-identical to the default build's (§2).

**Results** (`docs/design/start_table/trace_experiment.tsv`). Counts are
(pattern, arm) sequences that differ from the parent.

| variant | kind | byte movers | trace `spec` (ordered; slot,route,row,site) | trace `func` (spec+`__func__`) | trace `set` |
|---|---|---|---|---|---|
| D1 row-order swap (`run-pinned-bounded` ↔ `run-pinned`) | plant | 18 | 18 | 18 | 18 |
| D2a predicate flip (G1 `dominated` negated) | plant | 3,642 | 3,642 | 3,642 | 3,642 |
| D2b predicate boundary (`n >= 256` → `n > 256`, VM hat) | plant | 48 | 48 | 48 | 48 |
| D3 route mis-key (`dfa_pf_of` on `CAND_ROUTE_VM`) | plant | 2,158 | **2,480** | 2,480 | 2,480 |
| D4 row change, bytes identical: scan-state with bit 32 forced | plant | 0 | 0 | 0 | 0 |
| D4b row change: form-fwd with bit 32 forced (stamp unchanged, body row moved) | plant | 132 | 132 | 132 | 132 |
| D4c row change, bytes identical: scan-state with `.forward = false` | plant | **15** | **176** | 176 | 176 |
| N1 rename (`dfa_pf_of`, `req_use`) | neutral | 0 | **0** | **6,443** | 0 |
| N2 function move (`req_use` to EOF) | neutral | 0 | **0** | 0 | 0 |
| N3 emitter-source reformat | neutral | 0 | **0** | 0 | 0 |
| N4 a reader asks FIRST once more (beyond the ruled bar) | neutral | 0 | **6,443** | 6,443 | **0** |

**Verdict: the bar is MET.** Every plant that the corpus reaches was caught by
the trace. Under the specified `site` key, the ruled selection-neutral commits
gave 0 false alarms. Read with:
- **The trace sees what bytes cannot.**
  - D4c is the bytes-identical row change: the scan-state reader keeps only
    `reseeds`, and where the true row was `byte-class-bounded` (also `false`) no
    byte moves. The trace caught 176 patterns; bytes caught 15.
  - D3's 322 extra patterns are artifacts where the mis-keyed walk still lands
    on `none`. The record's `route` field moves, and no byte does. Those are
    latent bugs a later row change would expose.
- **D4 reached nothing.** The note's own `run-pinned → offset-set` example,
  planted at the scan-state reader, reached 0 patterns: no corpus artifact
  selects `run-pinned` at that site. It is a population fact, not a miss
  ([MECH-REACH]). D4c is the reached version of the same plant class.
- **C1 design condition 1: `site` must be a declared string literal, never
  `__func__`/`__LINE__`.** Measured: carrying `__func__` false-alarms the
  rename on 6,443 sequences, and the spec key reads 0.
- **C1 design condition 2: gate on the SET compare.** N4 is not in Frank's list
  but is exactly what C3-C5 do (readers rebuilt around `cand_select`). It is
  selection-neutral, yet it false-alarms the ORDERED compare on every sequence
  that reaches the reader. The SET compare reads it clean, and caught every plant
  at the identical count. So C1 gates on `trace_diff.py --unordered`. It runs the
  ordered compare as a diagnostic and declares its multiplicity changes, which
  C5b's filter still requires, since a new site's records are new set members.
  The ordered compare's extra power (order and multiplicity) is not selection
  power on this evidence.
- **The trace proves only print-agreement at inline sites.** The WINDOW record
  is printed by the same branch that emits the clamp (§3.3 item 5's stated
  limit); no plant targeted it.

**For C1:** the hook design above lands for real at C1 with the two
conditions. `cand_select`'s return becomes one more print site (C3). The trace
floor re-pins at C1's own count. The prototype is not merged.

## 5. Box and runtimes (Mac, `-j2` unless stated)

| run | time |
|---|---|
| prototype build | ~11 s; plant builds 11-14 s each |
| experiment | 11 variants × 7,190 compiles, ~20-25 s each |
| `emit_sweep` six streams, one binary | 82 s |
| streams 1-2 + trace, one binary | 49-52 s |
| arms on the 1-in-10 sample, one binary | 116 s |
| deny_census, 1-in-10, 16 flags | 135 s |

No heavy suite ran.

## 6. OWED: the heavy chain

`worktrees/stc0-scratch/heavy_chain.sh <lane/stc0 head sha>` runs detached under
`caffeinate -s`. It:
1. waits for `/Users/fdicostanzo/pcrec/worktrees/stc0/.lift`;
2. takes `worktrees/.mac-suite.lock` (file form, `set -C`, owner line, released
   on exit);
3. runs (A) §3's sweep, then (B) the full C0 gate:
   `emit_sweep.py --ref 73f66ba9 --tree-rev <head> --arms start --jobs 6`.

B covers all six streams, the self-check, and the arms with two real builds. At
`src`-identical revisions it must read identity on every stream and every arm,
at or above every re-pinned floor.

Logs: `worktrees/stc0-scratch/heavy/{chain,allflags,gate}.log`. The completion
line is `== stc0 heavy chain DONE rc=N (A=a B=b) ==`. Expect ~40-70 min once
lifted.

**The follow-up agent:**
- re-pins the four `-fno-length-prune` cells (and any other cell that moved)
  from `heavy/allflags/deny_census.tsv`;
- reads B's verdict from `gate.log`'s floor and identity lines. An arm FAIL at a
  src-identical pin is an instrument finding;
- appends the non-start mover list here.

## 7. Not done, and why

- **Q7's census-script move** (`call_graph.py`, `inventory.tsv` and
  `inventory_check.py` to `tests/codegen/` as a standing check). It requires a
  measured run time, a sabotage row and a robustness verdict on the parse. That
  is its own check-design job and was not in this brief's items 1-4; it was
  flagged to main at lane start. `row_census.py` goes to `tests/codegen/` only
  as the hit-counter's cross-check, now that Q3 passed (C1/C2's job).
- **The sabotage rows** (§2): waiting on main's S-id block.
