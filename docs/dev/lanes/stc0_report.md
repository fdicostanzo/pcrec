# stc0 — [START-TABLE] C0: the sweep instrument and the Q3 trace experiment

Lane stc0, 2026-10-06, opus. Branch `lane/stc0` off main `73f66ba9`. The work is
tooling only, and nothing under `src/` changes on the lane branch. The trace
prototype lives on the scratch branch `scratch/stc0-trace` (worktree
`worktrees/stc0-trace`) and is NOT merged. The design is
`docs/design/start_table.md` rev 2.1, §3.2 C0, §3.3 items 2-5, and §6 Q3/Q7.

**Status:** complete except Q7's census-script move (§7). The follow-up lane
`stc0b` (2026-10-06) discharged the owed items: the heavy runs and the
`-fno-length-prune` re-pin (§6), the every-flag movers (§6) and the S-ids
S550-S555 (§6b), then merged main (abi 65) into the branch (§6c).

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

**DONE** (lane stc0b; results and the mover table are §6). As briefed: `deny_census.py` over the 29 `--list-axes` flags outside
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

## 6. Heavy runs (Linux, 2026-10-06)

Both runs completed on ubuntubudu (the 10.46 reference box), launched by the
manager from `worktrees/stc0lx` after the Mac chain was dropped for the kit's
`.mac-suite.lock`. They ran in one detached chain at `-j10`: (A) the every-flag
deny sweep, wall 543 s; (B) the full C0 gate, `emit_sweep.py --ref 73f66ba9
--tree-rev <lane head> --arms start`, wall 585 s (`gate.log`: "elapsed: 584.6s").
Both rc 0 (`chain.log`: `A_RC=0`, `B_RC=0`). Results are committed under
`docs/design/start_table/heavy_linux_2026-10-06/` (`chain.log`, `allflags.log`,
`gate.log`, `deny_census.tsv`, `arms.tsv`); the bulky movers/hidden/transitions
TSVs are not kept, since nothing cites them.

**B, the gate.** All streams and all 64 arm rows read `ok` at identity, at or
above every floor. The population was 4,606 argv rows, 369 composition files,
38 producing, 108 artifacts, so PINS held. The four `-fno-length-prune` cells
were pinned from the 1-in-10 sample and read, on the full corpus:

| cell | old floor (bytes/stamp) | measured | new pin |
|---|---|---|---|
| byte c-default | 46 / 11 | 449 / 112 | 449 / 112 |
| byte c-vm | 69 / 0 | 678 / 0 | 678 / 0 |
| utf8 c-default | 49 / 11 | 468 / 118 | 468 / 118 |
| utf8 c-vm | 85 / 0 | 815 / 0 | 815 / 0 |

Every other cell's floor already equalled its measured value. The deny-census
numbers for the same flag (§ below) agree: 449 / 112, 678 / 0, 468 / 118,
815 / 0, so the two instruments count one population.

**A, the every-flag sweep.** 29 flags outside the start family × {auto, vm} ×
{byte, utf8}, 3,221-3,230 corpus patterns per arm. Cells read
`visible/hidden/refusal`: `visible` = movers whose start-family stamps moved
(`start_keys_moved`), `hidden` = movers whose bytes moved with no start stamp
moving, `refusal` = patterns that compile at base and refuse with the flag. A
`-` is zero everywhere.

| flag | auto/byte | vm/byte | auto/utf8 | vm/utf8 | reading |
|---|---|---|---|---|---|
| `-fcomments` | 0/3221/0 | 0/3222/0 | 0/3229/0 | 0/3230/0 | comment text only, every artifact; `-fno-comments` reads 0 (the default) |
| `-fno-size-term` | 0/3221/0 | 0/3221/1 | 0/3229/0 | 0/3229/1 | all-pattern `.flags` mover: the K92 leak (bit 18 unmasked), FIXED on main (abi 65). Not a start input |
| `-fno-scan-edge` | 0/3221/0 | 0/3222/0 | 0/3229/0 | 0/3230/0 | same: K92 leak (bit 21), fixed on main. Body-only otherwise |
| `-fno-startpos-guard` | - | - | 0/3229/0 | 0/3230/0 | KEPT contract bit, utf8 only: all-pattern `.flags` by design |
| `-fstartpos-guard=align` | - | - | 0/3229/0 | 0/3230/0 | same, kept contract bit |
| `-futf-check` | - | - | 0/3229/0 | 0/3230/0 | same, kept contract bit |
| `-fno-atomic-discharge` | 44/3177/0 | 0/3222/0 | 42/3187/0 | 0/3230/0 | KEPT engine-selecting bit (Frank Q14, 2026-10-06): all-pattern `.flags`; the 44/42 visible movers are 32+8 (30+8 utf8) patterns whose `ENGINE` and the whole family move, plus 4 `VM_RESEED`-only, on the DFA side only |
| `-fno-splice-calls` | 201/3020/0 | 54/3168/0 | 203/3026/0 | 54/3176/0 | KEPT engine-selecting bit (Q14): all-pattern `.flags`; visible = route moves. Already named by the 1-in-10 sample |
| `-fno-ctx-node` | 239/56/0 | 0/295/0 | 223/55/0 | 0/278/0 | `\b`/`\B` fall back to the lookaround spelling: the route and prefilter facts move on the DFA side. Already named by the sample |
| `-fno-length-prune` | 112/337/0 | 0/678/0 | 118/350/0 | 0/815/0 | prune ceiling: window/prefilter stamps move on the DFA side only. Already a DIFFER arm |
| `-fno-cls-kit` | 0/3/0 | 0/3/0 | 3/67/7 | 1/466/12 | wide-class forms: auto/utf8's 3 visible movers are 2 whole-family route moves (the same shape as `-fno-premul-table`'s) and 1 `VM_RESEED`; vm/utf8's 1 is `REQ_WHY`; the 7/12 refusals are size-cap moves. Byte side body-only. Named by the sample (vm/utf8) |
| `-fno-prefilter` | 1125/0/0 | - | 1149/2/0 | - | the hybrid prefilter's presence IS a start stamp (`RX_VM_PREFILTER`, route class). Known |
| `-fprefilter` | 82/0/2015 | 2949/0/273 | 85/0/1997 | 2953/0/277 | the force twin: the same stamp moves, and the refusals are the documented refused-by-force population (2,015 / 273 / 1,997 / 277). Known |
| `-fno-prefilter-collapse` | 1/1/0 | - | 2/3/0 | - | the collapsed-count rescue: one start stamp moves where the rescue fires. Known |
| `-fno-possessify` | 6/227/0 | 9/618/0 | 6/229/0 | 9/615/0 | **NEW.** The ONLY start stamp that moves is `REQ_WHY` (the pre-check admission verdict), on VM-only artifacts; read from `deny_movers.tsv`'s keys column. Likely mechanism, not probed: possessification changes the VM program's frame discipline, which G2's one-attempt conjunct (K64's `vm_frameless`) reads. 6 / 9 visible |
| `-fno-altcls-merge` | 2/87/0 | 8/81/1 | 2/92/0 | 8/86/1 | **NEW, small.** `REQ_WHY` on VM-only artifacts (8 per vm arm); on the auto arms also one `REQ_HANDOFF` mover. Same reading as possessify |
| `-fno-altcls-factor` | 0/102/0 | 1/101/0 | 0/99/0 | 1/98/0 | **NEW, one pattern per vm arm.** `REQ_WHY` only; same reading |
| `-fno-premul-table` | 0/2416/0 | - | 2/2440/0 | - | **NEW at utf8 only (2 patterns).** Body-only on byte; the two utf8 movers move the WHOLE start family (`DFA_PREFILTER`/`DFA_SCAN`/`DFA_START`/`VM_PREFILTER*`/`VM_RESEED`/`VM_START_SCAN`/`END_WINDOW`/`REQ_HANDOFF`), i.e. the artifact changes route (probably a size-cap rescue; not probed) |
| `-fno-counter` | 0/35/7 | 0/38/8 | 0/35/7 | 0/38/8 | counter rung off: body-only, 7-8 patterns refuse at the size caps |
| `-fno-anchored-dfa` | 0/1481/0 | - | 0/1481/0 | - | optional anchored machine: body-only |
| `-fno-alt-island`, `-fno-cls-fold`, `-fno-cls-pack`, `-fno-lit-run`, `-fno-revdet`, `-fno-run-overlap`, `-fno-tiered-entry`, `-fno-view-edge` | 0 visible, 3-2,416 hidden | same | same | same | body-only on every arm (no start stamp moves): not start inputs |

Readings:
- **Non-start flags that move start stamps without being a route or
  prefilter switch**: `-fno-possessify`, `-fno-altcls-merge`,
  `-fno-altcls-factor` (all three move `REQ_WHY`, VM-only artifacts) and
  `-fno-premul-table`/`-fno-cls-kit` at utf8 (a handful of whole-family route
  moves). The first group is a **start-table input candidate for C1's edit
  set**: the admission (`req_admit`/`req_use`, `REQ_WHY`) reads something an
  AST rewrite upstream changes. The likely input is the VM program's
  frame/one-attempt verdict (`Job.vm_frameless`, K64's conjunct in
  `req_route_one_attempt`); C1's `cand_select` must read it through the same
  accessor, and C1's own acceptance should read these three flags' visible
  counts (6/9, 2/8, 0/1) unchanged before and after. The premul/cls-kit
  movers are 2-3 patterns and need only the identity gate.
- Everything visible beyond that is the known set: the route switches
  (`-fno-atomic-discharge`, `-fno-splice-calls`, `-fno-ctx-node`,
  `-fno-cls-kit`), the prefilter switches and `-fno-length-prune`, which is
  already a DIFFER arm and which the table must keep as an input (its prune
  ceiling is what the window/pins stamps read).
- `-fno-length-prune` is the one flag whose `visible` count is 0 on the VM
  route and 112-118 on the auto (DFA) route: the VM never reads the ceiling
  for a start stamp.

## 6b. Sabotage rows S550-S555 (mech, solo)

The six drafted rows (§2) are committed as `tests/mech/sabotages/S550_*`
... `S555_*` (block S550-S555 allotted by main), arm `emitsweep`, `SAB_EXPECT=
DETECTED`, anchors copied from `git show HEAD:<path>`. `VALIDATE_ONLY=1` read
all six valid. Each was run as a single-row `bash tests/mech/run_sabotage_matrix.sh S<id>` against
a committed HEAD (`6a77eb88`; the six ran in parallel, each in its own scratch
tree, on the Mac, about two minutes in all), and every one read **DETECTED**:

| row | plant | arm cell |
|---|---|---|
| S550 | `opt_argv` drops every option | `emitsweep:3fail/21pass` |
| S551 | `opt_argv` drops `-e utf8` | `emitsweep:2fail/22pass` |
| S552 | trace compare ignores order | `emitsweep:2fail/22pass` |
| S553 | empty-trace floor disabled | `emitsweep:1fail/23pass` |
| S554 | per-arm records floor disabled | `emitsweep:1fail/23pass` |
| S555 | stale declaration accepted | `emitsweep:1fail/23pass` |

All six reported `mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0,
unreached: 0, anomalies: 0)`.

## 7. Not done, and why

- **Q7's census-script move** (`call_graph.py`, `inventory.tsv` and
  `inventory_check.py` to `tests/codegen/` as a standing check). It requires a
  measured run time, a sabotage row and a robustness verdict on the parse. That
  is its own check-design job and was not in this brief's items 1-4; it was
  flagged to main at lane start. `row_census.py` goes to `tests/codegen/` only
  as the hit-counter's cross-check, now that Q3 passed (C1/C2's job).
- **The sabotage rows**: DONE, §6b.
