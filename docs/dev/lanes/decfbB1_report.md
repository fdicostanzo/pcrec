# decfbB1 — [DEC-FALLBACK] refactor B, step B1: the fallback trace

Lane decfbB1 (opus), 2026-10-08, branch `lane/decfbB1` off `lane/decfbB0`
tip `6794d272` (B0 not yet merged when the lane started; B0's heavy chain
finished green during this lane, `worktrees/decfbB0/build/land/trailer.log`
ends `mech (39 rows) rc=0` / `== CHAIN DONE`). The charter is
`docs/design/dec_fallback.md` rev 2: §4.2's B1 row, B0 items 8 and 11(a),
§4.3, §4.3a, §4.4, §1.9, §11. The model is `decfbB0_report.md`.

The `src/` change is `#ifdef PCREC_CAND_TRACE` text only. It is NOT an abi
event: the default build moved 0 emitted bytes and 0 stderr bytes in every
variant and base, and nothing was bumped.

## Summary (a fresh agent resumes from here)

**Status.** B1 is delivered and its light tier is validated. The heavy
chain is ARMED, detached, on `worktrees/decfbB1/.lift` (see "Owed").

- **The trace.** Five slots on [START-TABLE] C1's `PCREC_CAND_TRACE_REC`/
  `_RECF`, one stream, ten declared site keys (format below).
- **The B1 gate:** CLEAN, 656 s. Command: `emit_sweep.py --ref 6794d272
  --tree-rev HEAD --variant all --trace --trace-order fallback=ordered
  --trace-declared docs/design/dec_fallback/trace_declared_B1.txt --jobs 6`.
  - 90 stream cells (5 variants x 2 bases x 9 streams), every one `movers=0
    asymmetric=0`. The `stderr` stream is among them.
  - The trace build moved 0 stdout bytes against the default build in every
    variant, on both streams.
  - C1's records are identical B0 vs B1 in every variant. B1's records are
    the declared multiplicity.
  - The fallback-trace site keys reached: 8/8.
- **The CROSS-RECORD: AGREE.** `cross_record.py`, ~6 min.
  - (a) decfb0's probed copy: 5 variants x 4,794 compiles, 0 differ.
    Arrivals per variant: plain 466, lowsize 907, lowdfa 597, lowboth 845,
    lowthr 466.
  - (b) the rev-2 prototype: 60 variant x arm cells, 288,660 compiles, 0
    differ. They carried 54,715 arrivals, 239,852 admits, 171,523 gates and
    223,186 final stamps.
  - Only after this agreement is the trace the gate.
- **`row_reach.py`** (B0 item 8): CLEAN on the full mirror, 60 cells, ~3 min.
  It is red both ways (S623's plant and a dropped `gate` record, below).
- **`run_fallback_table.sh` (a)** (B0 item 11(a)): 128/0 (was 66), ~17 s.
  It is red both ways.
- **Carry-overs.**
  - K99 filed.
  - emit_sweep PINS re-pinned, and the trace floors re-pinned to B1.
  - The note's forced-on SIZECAP witness corrected.
  - The `--list-limits` finding is below.
- **Mech rows.** S620-S626, all DETECTED.
- **One new finding needs a ruling** (F1): the size term's restart leaks the
  ladder's K.

**Next:** B2. It implements T1's new columns and rows 0-4, T2, T3, T4 and
the attribution walk beside the old code, plus the both-derivations oracle.
From B2 on, the five slots are COMPARED parent vs child, not filtered:
- `fallback` ordered, the rest as sets;
- `trace_declared_B1.txt` is meaningless against any later parent;
- `row_reach.py --ref PARENT --rev CHILD` joins each commit's gate.

## The trace (what B2-B5 are held to)

Every record is `CANDTRACE <slot> <route> <row-field> <site>`.

| slot | route | row field | site keys | where |
|---|---|---|---|---|
| `fallback` | the arrival LABEL SET (`forcing\|nomem\|overflow\|size`, `other` when none) | T1 row taken, then the POST-ROW tuple `dd= cr= sdr= fo= ovw= sc=B/L latch=E/F restart=` | `fb-forcing`, `fb-nomem`, `fb-trial`, `fb-sel1`, `fb-size`, `fb-refuse` | `compile_driver`'s catch branch (`FIT_TRACE`, `src/core/compile.c`) |
| `admit` | the scope (`none`/`sel1`/`sizecap`, the CR) | T2 row, `pf=` verdict | `admit` | `pcrec_select_engine`, after the fit is published (`fit_trace_admit_attrib`, `src/opt/select_engine.c`) |
| `gate` | the scope | T3 row (`rung` for both rung PFLWs), `pflw=` | `gate` | the collapse gate, after the PFLW is written |
| `stwhy` | `-` | the T4 token | `st-why` | after `cx.size_term_why =` |
| `attrib` | `-` | the `ENGINE_SEL` token, `from=` the row whose cell gave it | `attrib` | beside `admit` |

The tuple fields:
- `fo` is `defo.flags & (NO_PREMUL_TABLE | NO_PREFILTER)`, the two bits the
  rows OR in.
- `ovw` is `overflow_why` once `dfa_disabled` makes it valid, else `-`.
- `latch` is `dfa_was_engine`/`budget_fallback`.
- `restart` says whether the size term was reset.

A row that writes nothing (`forcing`, `nomem`, `refuse`) prints before its
action, so its tuple is the unchanged state.

How each record reads today's code:
- **`admit`** is read off TODAY's derivation, in T2's ORDER. Its inputs are
  the two declined-nullable flags and the ternary's inputs; `kinds` is a
  memo read that `prefilter_decision` asked first.
- **`gate`** is T3's row projected from the PFLW just written.
- **`attrib`'s `from`** is computed from the token and the attempt record
  (CR, SDR). The latest attributing row is derivable there because every
  attributing row fires at most once.

All three print values the decision already computed, which is C1's rule.
Labels are computed through `cx.job` (only `forcing` lives there), so a
record after `job_cleanup` is still correct.

## Deliverables

| item | deliverable | where | both directions |
|---|---|---|---|
| B1 | the five slots, declared literal site keys, `#ifdef` only | `src/core/compile.c` (`FIT_TRACE`, `fit_trace_labels`), `src/opt/select_engine.c` (`fit_trace_admit_attrib`), `src/core/internal.h` (`pcrec_cr_trace_name`) | clean: the gate run (0 default-build movers, 0 trace-vs-default stdout moves). `make strict` clean; the trace build compiles with `-Wall -Wextra -Wshadow -Wclobbered -Werror` |
| B1 | the byte sweep, trace build vs default | the gate run (`trace build vs default build` lines) | 0/0 on c-default and c-vm in all 5 variants |
| B1 | the CROSS-RECORD | `docs/design/dec_fallback/cross_record.py` | clean: AGREE (above). Red: S623's plant (labels swapped) gives (a) lowdfa 10 differ and (b) lowdfa base 18 differ, both FAIL (stride-10 sample) |
| 8 | `row_reach` | `docs/design/dec_fallback/row_reach.py` | clean: the full mirror. Red: the S623 plant, `--ref HEAD --rev PLANT`, gives DECLARED ZERO REACHED (e.g. `T1 sel1-collapse size` 18 in lowdfa) and REACHED CELL DROPPED. A dropped `gate` record gives every T3 cell DROPPED plus the K35 table check. Plants were dangling commits `4c49071f`/`b6ff5206` |
| 11(a) | the SEQUENCES half | `tests/codegen/run_fallback_table.sh` (a) | 128/0. Red: S623 18 fail, S624 9, S625 2, S626 3. A latch-on-every-overflow plant (S-F8's shape on today's code) reads red on `seq-sel1cd` record 2 |
| (a) | K99 | `docs/dev/known_issues.md` | filed, not fixed |
| (b) | emit_sweep PINS | `scripts/emit_sweep.py` `PINS` | re-pinned from a one-tree measurement run (below); the re-run at the new floors passed |
| (c) | the forced-on SIZECAP note | `docs/design/dec_fallback.md` §4.2 item 6 | corrected |
| (d) | `--list-limits` | this report, Findings | — |

Also in this lane:
- emit_sweep's `TRACE_VARIANT_RECORDS_FLOOR` and `TRACE_RECORDS_FLOOR` are
  re-pinned to B1's working-side counts. plain is 334,904 / 120,524 (C1-only
  B0 values: 315,269 / 105,080).
- New: `FALLBACK_TRACE_SITES`, a reach check in the variant path.
- `trace_declared_B1.txt`.
- `call_graph.py` skips in-body `#ifdef PCREC_CAND_TRACE` blocks as sites,
  and prints file-scope trace blocks as `def-trace` owner lines. Both are
  byte-neutral on the family and the sites.
- Regenerated: `call_graph_fallback.txt`, `sabotage_anchors.tsv/.summary` and
  `state_readers.txt`.
- Self-tests: `emit_sweep.py.test` 14/0, `trace_diff.py.test` 30/0.

### row_reach at the base arm (records; the T1 cell is the label set)

| table / row | cell | plain | lowsize | lowdfa | lowboth | lowthr |
|---|---|---:|---:|---:|---:|---:|
| T1 size-term-trial | other | 3 | 22 | 3 | 6 | 3 |
| T1 sel1-collapse | overflow | 4 | 4 | 96 | 96 | 4 |
| T1 sel1-drop | overflow | 2 | 2 | 69 | 69 | 2 |
| T1 prefilter-collapse | size | 3 | 105 | 0 | 84 | 3 |
| T1 drop-anchored | size | 15 | 98 | 0 | 38 | 15 |
| T1 drop-premul | size | 0 | 74 | 0 | 13 | 0 |
| T1 drop-prefilter | size | 3 | 93 | 0 | 75 | 3 |
| T1 refuse | other / size | 442 / 0 | 442 / 87 | 442 / 0 | 442 / 38 | 442 / 0 |
| T2 default-on | none / sel1 / sizecap | 1269 / 3 / 3 | 1509 / 9 / 105 | 1269 / 95 / 0 | 1425 / 191 / 84 | 1509 / 9 / 3 |
| T2 forced-off | sizecap | 3 | 93 | 0 | 75 | 3 |
| T3 rung-sizecap / rung-sel1 | | 0 / 1 | 55 / 7 | 0 / 30 | 41 / 126 | 0 / 7 |
| T4 cap-rescue / capacity-declined | | 0 / 0 | 14 / 1 | 0 / 0 | 21 / 1 | 0 / 1 |

The full table, every arm, is `build/b1/rr_full/reach.tsv`. It is not
committed; the run reproduces it in ~3 min.

The counts are per RECORD (attempt), so T2-T4 run above the prototype's
per-compile numbers. T1 and the arrival cells match `reach.md`'s.

Every declared zero held. That is §4.3a's UNREACHED list plus T2/T3's scope
zeros and every two-label arrival, 49 cells in all. It includes the two
§1.7 sequences (size row then [SEL-1] row, and the reverse).

### emit_sweep PINS (one-tree run at B1, all streams)

| pin | measured | floor (was) |
|---|---:|---:|
| argv population | 5,423 | 5,370 (4,550) |
| reach default / vm / ir | 4,972 / 4,973 / 4,973 | 4,920 (4,110) |
| reach facts | 4,932 | 4,880 (4,070) |
| composition files | 373 | 365 (360) |
| composition producing / artifacts | 38 / 108 | 38 / 100 (unchanged) |

## Choices where the brief or the note was open

1. **`attrib`'s fired-row INDEX is printed as the row's NAME.** Before B3
   there is no `fit_seq[]` to index. A name identifies the row exactly,
   because each attributing row fires at most once, and it is what B5's
   walk naturally prints. B2-B5 must print the same name.
2. **`admit` names T2's row where today's order and T2's differ** (§1.4):
   `has_var` with `-fno-prefilter`, and `dd && CR == SEL1 && force_off`. The
   verdict is today's. B4's walk prints its own row, and the parent/child
   compare holds the two together. The rev-2 prototype's `t2_row` agreed on
   all 239,852 admits.
3. **Two conditional records are wrapped in `#ifdef`** (nomem, refuse); the
   rest are bare macro calls. Every sabotage anchor resolves (545 sites);
   decfb0's and the prototype's probe anchors still apply; the edit set is
   unchanged.
4. **The trace build's own readers of the state** (31 lines) are in
   `state_readers.txt`. They move with the state at B2-B5.
5. **fbt (a) has its own four trace compilers.** They are kept apart from
   (b)/(c)'s untraced ones, so an artifact verdict never rides a trace build.
6. **Row reach is counted per record, not per final stamp.** That is how F1
   below became visible.

## S-ids (range S620-S639)

The main tree and `worktrees/*/tests/mech` were grepped first; S619 was the
highest.

| id | what | detector (arm) | at B1 |
|---|---|---|---|
| S620 | S-I2: trace_diff's `ordered` slot compared as a set | `trace_diff.py.test` (emitsweep) | DETECTED 4/40 |
| S621 | S-I3: `emit-ir-auto` loses `-fno-prefilter` | `emit_sweep.py.test` (emitsweep) | DETECTED 1/43 |
| S622 | S-I4: fbt (b) drops its `overflowed-prefilter` witness | fbt (b) floor (fallbacktable) | DETECTED 1/124 |
| S623 | the trace's labels swap overflow/size | fbt (a) | DETECTED 18/110 |
| S624 | the `fb-size` record dropped | fbt (a) | DETECTED 9/119 |
| S625 | `admit` swaps `var-nullable`/`nullable-exact` | fbt (a) | DETECTED 2/126 |
| S626 | `attrib` swaps the [SEL-1] source row | fbt (a) | DETECTED 3/125 |

S627-S639 are unused. `sabotage_anchors.py` classes S623/S625/S626 under the
new `def-trace` owners, and S624 as RE-RUN at B3+B5. It is still 11 re-aims
with the one pre-existing unresolved site (S571).

## Findings

- **F1 (NEW, needs a ruling): the size term's RESTART leaks the ladder's K.**
  - The mechanism. `restart_term` (`prefilter-collapse`, `drop-prefilter`)
    resets `st_phase` to `ST_DEFAULT`. It does NOT reset `defo.unroll_k`,
    which the ladder trials and the FINAL attempt wrote (`compile.c`:
    `defo.unroll_k = SIZE_TERM_LADDER[st_idx]` / `= st_final_k`).
  - So the "restarted" default attempt runs at the leaked K. Its size term
    reads `option` (`defo.unroll_k > 0 && st_phase == ST_DEFAULT`) and the
    ladder can never run again (`run` needs `defo.unroll_k == 0`). The
    restart the code comments promise does not happen.
  - MEASURED in row_reach's records: intermediate `stwhy option` records in
    lowsize/lowboth on compiles with no `--unroll`. Every one of them
    REFUSED. Two witnesses:
    - `(?:aa|a){8,12}+ab`: the lowsize base arm and 5 more;
    - `(a{1,3}){65}`: lowsize `--tune=min-size`.
  - A scratch compiler that resets `defo.unroll_k` to the caller's value on
    restart COMPILES both (rc 0, `prefilter-collapse > drop-prefilter`), so
    the leak turns rescuable patterns into refusals.
  - Population at shipped limits: 0 in the corpus (no plain-variant
    `option` record). No artifact byte moves.
  - B preserves it as a no-mover, so T4's `option` row fires there too. It
    also means §1.8's bound overstates the restarted ladder's real cost.
  - Recommend: a K-entry (the next K after K99, the manager's to assign)
    and a later mover row; the fix moves refusals to compiles.
- **F2 (carry-over d): `--list-limits` prints `limits.def`'s literal, not
  the compiled value.** Under `-DPCREC_MAX_AUTO_DFA_ELEMS=3000` it still
  lists `30000000`. A caller reading it as "the limits this binary enforces"
  is misled on any `-D` build. B0's plumbing control avoided it with witness
  stamps. Recorded only, as the brief asked.
- **F3: `decfbB0_report.md`'s reach table misquotes its own pins.** Its
  "Floors" table gives plain/byte reach 5,075 / 5,069 / 5,069 / 4,955. The
  committed `VARIANT_PINS` (and this lane's re-measurement, identical in all
  10 cells) are 4,972 / 4,973 / 4,973 / 4,932. The pins are right; the
  report's prose is not. Not edited (it is B0's record).
- **Process note.** Before I exported `TMPDIR`, two of this lane's runs
  defaulted to `/tmp`: `run_fallback_table.sh`'s `mktemp` and one mech row's
  scratch root. Both directories were self-cleaned, and checked gone.
  Everything after that ran with `TMPDIR=worktrees/decfbB1/build/b1/tmp`,
  and the chain sets its own.

## Owed: the heavy chain (ARMED)

- **Chain:** `worktrees/decfbB1/build/land/chain.sh`, B0's shape. It runs, in
  order:
  - `make`, then `make -k -j6 -Otarget test` (which now includes fbt's 128
    checks);
  - `make strict`, `make alloc`, `make testscripts`;
  - mech `VALIDATE_ONLY=1`;
  - 25 mech rows: S620-S626; S550-S555, the emitsweep suite this lane
    changed; and the 12 rows `sabotage_anchors.py --step B1=6794d272..HEAD`
    computes as re-run at B1: S166, S169, S178, S193, S253, S257, S259,
    S261, S306, S40, S437, S440.
- **Verdicts:**
  - `build/land/trailer.log` has one `rc=` per stage and ends
    `== CHAIN DONE`.
  - make test: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'
    build/land/test.log`; empty means green.
  - mech: its own `== mech run COMPLETE` trailer in `build/land/mech.log`.
- **Waiter:** a `nohup setsid` loop on `worktrees/decfbB1/.lift`. Its PID is
  in the handback message.

Already run in this lane, outside the chain:
- the B1 gate;
- the cross-record (full);
- row_reach (full mirror, plus the two plants);
- fbt (clean, plus four plants);
- `make strict`;
- the emit_sweep and trace_diff self-tests;
- the PINS measurement plus its re-check;
- the seven new mech rows (`mech run COMPLETE: 7 rows`, 0 unexpected).

## Commits

`lane/decfbB1`, `6794d272..`:
- the trace, with the call-graph skip and regenerated instruments;
- emit_sweep's site reach check plus the declared multiplicity;
- fbt (a);
- `row_reach.py`;
- `cross_record.py`;
- the trace floors;
- the PINS;
- fbt records plus S620-S626;
- the `def-trace` owners, the re-derived anchors and CLAUDE.md entries;
- K99, plan.md, the design note and testing.md;
- this report.
