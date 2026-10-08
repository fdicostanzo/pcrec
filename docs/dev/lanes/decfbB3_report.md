# decfbB3 — [DEC-FALLBACK] refactor B, step B3: replace the dispatch

Lane decfbB3 (opus), 2026-10-08, branch `lane/decfbB3` off main `0f37bfd8`
(B0, B1 and B2 merged). The charter is `docs/design/dec_fallback.md` rev 2:
§R, §1.2-§1.3, §1.8-§1.9, the §4.2 B3 row, §4.3, §4.3a, §4.4, §11's rulings.
The models are `decfbB2_report.md` (the base and the gate shape) and
`stc3_report.md` (refactor A's replace commits). B3 is a no-mover refactor
step and NOT an abi event.

## Summary (a fresh agent resumes from here)

**Status.** B3 is built and committed. Spot checks show zero default-build
movers (13 witnesses covering every T1 row, stdout + stderr + rc against a
`0f37bfd8` build: all identical). The sampled attempt histogram is
IDENTICAL (plain and lowsize, stride 25). Every new and re-aimed sabotage
row was planted and detected in a lane check. **The light tier is RUNNING
detached** (`build/b3/light.sh`, trailer `build/b3/light/trailer.log`); it
writes `== LIGHT DONE` only when every step is green, and stops with
`== LIGHT STOPPED at <step>` on the first red. The heavy chain is ARMED: it
waits for `== LIGHT DONE` AND `worktrees/decfbB3/.lift`.

What landed (`src/core/compile.c`, plus one comment in `select_engine.c`):
- **One dispatch.** The catch branch's five tests are now one
  `fit_walk(&fs, fit_labels(&cx))`. The tests were the force-loop arm, K60's
  nomem propagation, the size-term trial catch, the [SEL-1] block and the
  size-cap `fit_select`. The four code-action rows are a switch:
  `FIT_FORCE_NEXT`, `FIT_PROPAGATE`, `FIT_TERM_NEXT` and
  `FIT_REFUSE`/`FIT_UNROLL_RESCUE`.
- **The `sets` routine.** Every retrying row (3, 4, 6-9) reaches ONE routine
  after the switch, which applies the row's `sets` cell:
  - the carry (`overflow_why`, the size-cap figures);
  - the first-overflow latch;
  - `job_cleanup`;
  - `dd`, `cr` (`fit_cr_of`), `sdr` (`fit_sdr_of`), `flags_or` and the
    size-term restart;
  - the err reset and the trace record.

  The routine is the only writer of the cross-attempt state.
- **The fired record.** `fit_select` and `dropped_*` are deleted.
  `fit_record` grows the fired record (`fit_seq_rows[]`/`fit_seq_cells[]`,
  `fit_fired`) in the DEFAULT build, and `Ctx.fit_seq` is seeded in both
  builds. The trace build keeps §1.9's once and sequence invariants inside
  `fit_record`.
- **The notes** are a loop over the fired `once` rows' `note` cells, in table
  order, which is the old `dropped_*` order. The text is byte-identical: the
  cells hold the same literals.
- **The rungs' long rationale comments** moved verbatim from the deleted
  switch cases to sit above each row's `applies` predicate. The [SEL-1]
  ones sit above `fit_sel1_eligible`.

**What retired from the oracle** (A's C5 precedent). Two of its checks had
nothing left to compare once B3 deleted their old side:
- The **arrival** check: the walk's row vs the five tests, and the post-row
  state vs the `sets` cell. The five tests are gone, and the `sets` routine
  IS the writer.
- The **notes** check: the fired note rows vs `dropped_*`. The flags are gone.

What retired with them:
- the functions `FitOracle`, `fit_oracle_open/_arrival/_post/_notes` and the
  `arrival`/`note` `CANDFIT` sites;
- 15 witnesses in `run_fallback_table.sh` (d) (12 arrival, 3 note);
- `oracle_sweep.py`'s `arrival`/`note` SITES.

What stays: the oracle's TOKEN checks (`admit`, `admit-listing`, `pflw`,
`stwhy`, `attrib`, `pfwhy`), because their old derivations still exist until
B4 and B5. §1.9's invariants also stay (`fit-once`, `fit-sequence`,
`fit-attempts`, `fit-sel1-drop`, the self-check).

**Re-aims:**
- **S253** (now the notes loop skips the premul row);
- **S259** (now the arrival's label set drops NOMEM).

Both were re-verified with a plant.

**New mech rows:** S646-S651 (S652-S665 unused).

**Needs a ruling:** none blocking. "Deviations, findings and questions"
holds four findings and three choices.

**Next: B4** replaces the admission. Its PARENT is post-B3, so
`attempt_hist.py` takes `--parent-patches docs/design/dec_fallback/probes_b3.py`.

## What landed

| item | where | notes |
|---|---|---|
| the one dispatch | `compile_driver`'s `if (setjmp(cx.jb))` | `fit_walk` + a switch over the code-action rows; `-Wswitch`-exhaustive, no `default:` |
| the `sets` routine | after the switch | latch and carry read before `job_cleanup`, state written after; `fit_cr_of`/`fit_sdr_of` map a cell to its value (KEEP = the current value) |
| the fired record | `fit_record` (new, default build) | trace build: `fit-once`, `fit-sequence` (`fit_seq_legal[]` stays trace-only) |
| notes | the loop before `facts_force:` | `fit_rungs[i].note` for every fired row with a note |
| deleted | `fit_select`, `dropped_anchored/_premul/_prefilter`, the oracle's arrival/notes code, `ovf_eligible`/`retry_collapse`/`retry_drop`, `FIT_ORACLE_POST` | `fit_walk`/`fit_labels` lose `__attribute__((unused))` |
| fbt (d) | `tests/codegen/run_fallback_table.sh` | 15 retired witnesses; 50 remain |
| fbt (e), new | same | the drop notes: six witnesses, hand-written FULL stderr lines, rung order or none |
| oracle sweep | `docs/design/dec_fallback/oracle_sweep.py` | SITES without `arrival`/`note` |
| probes | `docs/design/dec_fallback/probes_b3.py` (new); `reach/build_reach.py` | see "Instruments" |
| instruments | `attempt_hist.py` (`--parent-patches`), `cross_record.py` ((a) builds HEAD with probes_b3), `state_readers.sh` (reads `fit_labels`; declares `fit_walk`), `start_table/call_graph.py` (`FB_ROOTS` names `fit_walk`) | regenerated: `call_graph_fallback.txt`, `sabotage_anchors.tsv/.summary`, `state_readers.txt` (564 → 514 lines: compile.c 344 → 294, the deleted code) |
| comment readers | `tests/resource/run_resource_tests.sh`, `tests/codegen/run_prefilter_collapse.sh` (×3), `src/opt/select_engine.c` | name the rows/predicates instead of `ovf_eligible`/`retry_collapse` (§4.5's comment rule) |
| docs | `docs/design/dec_fallback.md` §4.2 (B3's outcome), `docs/testing.md`, CLAUDE.md of `src/core`, `tests/codegen`, `tests/mech`, `docs/design/dec_fallback` | |

No `docs/spec/` hunk: nothing a caller observes moved (§4.6 owes B3 none).
The spec's names `fit_rungs[]`, `dfa_disabled` and `prefilter_lang_why`
are kept.

### Readers grepped before the first commit and re-checked after each

There are two classes of source-text reader: exact-text anchors and regexes
over src. Both broke at B2 (b2tri, b2tri2), so both were checked:
- **Sabotage anchors.**
  - `m6read_check_sab_anchors.py`: 555 rows, 573 sites, all resolve.
  - `sabotage_anchors.py` at HEAD: COUNT_MISMATCH 0, UNRESOLVED_SRC 1 (the
    pre-existing S571).
  - Lines of the old catch branch quoted by a row: S253, S259 and S624. S624
    is kept verbatim, below.
- **Probe anchors.**
  - decfb0's `build_ref.py` (the attempt histogram and cross_record (a)):
    re-anchored in `probes_b3.py`.
  - `reach/build_reach.py` (cross_record (b)): re-anchored in place.
- **Regexes over src.**
  - `tests/findings/structural_check.py`: `make test-findings` 11/0.
  - `axes_registry_check.sh` (reads `cx.size_term_why =`, untouched by B3):
    0 failed.
  - `limits_check.sh`: 0 failed.
- **Census readers.**
  - `state_readers.sh`: its R/RQ sets would have LOST `dfa_overflowed`,
    `failed_nomem`, `size_cap_refused` and `pf.forcing`. The labels moved
    into `fit_labels`, so it now reads that body (fail-closed).
  - `call_graph.py --family fallback`: exited 2 on the missing root
    `fit_select`, its fail-closed rule working. `FB_ROOTS` now names
    `fit_walk`.
- **Comment readers** (§4.5): the four above.
- **Not edited:**
  - `tools/review/out/*` (generated censuses);
  - `docs/design/memfn/probes/rowcon/customers.md` (a historical cite).

## Light tier (RUNNING, detached)

`build/b3/light.sh` runs the steps below, one at a time. Logs are under
`build/b3/light/`, and each step's `rc=` goes to `trailer.log`. Each step
must exit 0 AND print its verdict line, else the script stops.

| step | command | verdict line |
|---|---|---|
| build | `make -j16` | — |
| fbt | `run_fallback_table.sh` (a)-(e), the SEQUENCES half included | `checks failed: 0` |
| alloc | `make alloc` (W4 = row 1, W5 = row 0) | `alloc: every forced allocation failure was diagnosed` |
| emit_sweep | `--ref 0f37bfd8 --tree-rev HEAD --variant all --trace --trace-order fallback=ordered --jobs 8` | `VARIANTS: CLEAN` |
| row_reach | `--ref 0f37bfd8 --rev HEAD` | `ROW_REACH: CLEAN` |
| cross_record | `row_reach --ref HEAD --rev HEAD`, then `cross_record.py --trace-dir rr_mirror` | `CROSS-RECORD: AGREE` |
| attempt_hist | `--ref 0f37bfd8 --rev HEAD --child-patches probes_b3.py` | `ATTEMPT HISTOGRAM: IDENTICAL` |
| oracle_sweep | `--rev HEAD` (both orders) | `ORACLE_SWEEP: CLEAN` |

Results already in hand before the launch:
- **fbt.** 191/0 on the tip (was 199 at B2: −15 retired, +6 (e), +1
  first-rung (c) witness, finding 8).
- **make alloc.** 34 s on the tip, with W4 and W5 PASS. That came from the
  plant runs' clean controls; the light run repeats it on the tip.
- **attempt_hist sample.** Stride 25, plain + lowsize, parent `0f37bfd8`
  with decfb0's probes vs child `c5ef46db` with `probes_b3.py`: IDENTICAL.
  - plain: 192 compiles, histogram 1:191 2:1.
  - lowsize: 192 compiles, histogram 1:181 2:3 3:5 7:2 8:1.
  - BYTES_DIFF 0.
- **`make strict`.** Clean in the default build, the trace build, and
  trace + `NEW_FIRST`.
- **Spot identity.** 13 witnesses gave identical stdout, stderr and rc
  against a `0f37bfd8` build:
  - [SEL-1] collapse; collapse then drop; drop alone;
  - pfc → drop-prefilter; drop-anchored; the K59 premul pair with both
    notes;
  - `--fast-or-fail` refuse; `--engine=dfa` refuse; a parse refusal;
  - the trial tower; `--tune=min-size`; a no-arrival control.

## Mech rows (lane check)

Each plant was applied to a `git archive HEAD` copy with
`tests/mech/lib/replace.py` and built. Its detector script was then run
inside the planted tree (`build/b3/plants.sh`, logs
`build/b3/pl/<id>/det.log`).

| id | plant | detector | result |
|---|---|---|---|
| S253 (re-aim) | the notes loop skips `FIT_DROP_PREMUL` | `run_tune_dial.sh` §6 | DETECTED: 4 fails, "anchored-note=1 premul-note=0" at every position; the K59 witness still compiles, stamps `size-cap-retry`, table `indexed` |
| S259 (re-aim) | `fit_labels` drops `failed_nomem` | `make alloc` W4 (`resource` §2b) | DETECTED: W4 143 of 209 forced failures SUCCEEDED THROUGH (68.4%, K60's ladder class); W5 still PASS |
| S646 | T1 rows 0/1 swapped (S-F0) | `make alloc` W5 | DETECTED: "N=209 is IN the force loop ... the listing was REFUSED" |
| S647 | row 2's `on` drops `other` (S-F2) | fbt (a) | DETECTED: 2 fails, seq-trial refuses (rc 1) |
| S648 | row 6's deny bit dropped (S-F6) | fbt (a) | DETECTED: seq-pfdrop reads `prefilter-collapse@size > drop-prefilter@size` |
| S649 | the latch on every overflow (S-F8) | fbt (a)/(b) | DETECTED: 5 fails, `latch=0/0` on seq-sel1cd's record 2 |
| S650 | `FIT_CR_TO_NONE` maps to `CR_SEL1` | fbt (a) | DETECTED: 16 fails (the trace build aborts, rc 134, `fit-once`) |
| S651 | `fit_record` never appends | fbt (d)/(a) | DETECTED: 46 fails (rc 134; the attribution/pfwhy/sel1-drop checks) |
| S637 (re-run) | drop-anchored's note cell empty | fbt (e) | DETECTED: note-anch prints no note, note-premul one short |
| S627-S632, S634-S636, S638, S645 (re-run) | B2's plants, now live in the default build | fbt | all DETECTED (`build/b3/plants2.log`): S627 26 fails, S628 1 (rc 134, `fit-once`), S629 6, S630 106 (self-check refuses), S631 1, S632 1 (`drop-premul@overflow > refuse@overflow`), S634 3, S635 109, S636 6, S638 106, S645 40 |
| S633 (re-run) | drop-prefilter carries no size-cap figures | fbt (c), new first-rung witness | UNDETECTED on the tip at first, DETECTED after the fix (finding 8 below): "size cap retry, hybrid 0 > 0" |

**Rows not taken, with reasons.**
- **S-F1** (row 1 deleted) is an EQUIVALENT mutant. Row 2's `on` mask leaves
  NOMEM out, so a NOMEM arrival falls to `refuse`, whose action equals
  PROPAGATE's. Checked: with row 1 deleted, `make alloc` is green, and W4
  PASSes single-shot and sustained. D109's guard therefore lives in the
  LABEL derivation and the row order together, which is why S259 plants
  the label.
- **S-F9** (rows 3-4 stop carrying `overflow_why`). The retry would `memcpy`
  an uninitialized driver array into `Ctx.dfa_overflow_why`, so the plant's
  output is indeterminate. It is not a well-defined mutant, and the `ovw`
  carry is still asserted by fbt (a)'s post-row tuple.
- **S-F16** stays WEAK, by the note's own account.

### The RE-RUN list, derived

The derivation (at the A tree `0f37bfd8`, `--repo .`):

```
sabotage_anchors.py build/b3/ref build/b3/cg_ref.txt refactor_edit_set.tsv \
    --repo . --final after-B6 --edit-names --step B3=0f37bfd8..HEAD
```

It reports "4 definitions edited, 31 reached" and **34 rows re-run at B3**
(hunk 17, reach 17):

S64 S102 S165 S166 S169 S176 S178 S193 S216 S237 S252 S257 S261 S272 S306
S420 S421 S423 S437 S440 S612 S624 S627 S628 S629 S630 S631 S632 S633 S634
S635 S636 S637 S638.

- S102, S165, S216, S272 and S612 are B4's re-aims. They re-run here because
  B3 touched one comment in their owner, `prefilter_decision`.
- `--step` does NOT reach rev 1's hand list S189/S191/S192.
  - S189 is `build_anchored_dfa`, which reads `size_drop_rung`, a value the
    `sets` routine now writes.
  - S191/S192 are `size_term_choose`, inside row 2's action.

  No B3 hunk touches their owners, and the reach relation does not follow a
  STATE write. They run by judgment.
- fbt changed, so the `fallbacktable` arm's other rows also run: S623,
  S625, S626 and S639-S645.

The chain's 55 rows are: S253 S259 (re-aims), S646-S651 (new), the 34, the
three judgment rows, and the ten fbt rows.

## Instruments

- **`probes_b3.py`** (new) re-anchors decfb0's probes:
  - `att`/`fail`: anchors untouched, copied verbatim.
  - `sel1`: RESTATES `retry_collapse`/`retry_drop` from their own inputs
    (`dfa_overflowed`, engine, flags, `dfa_disabled`, `collapse_reason`). It
    prints only when the walk did not take rows 0-2, which is the three
    earlier tests. It does not read the walk's row, so the probe stays
    independent of the decision it watches.
  - `rung`: prints every row past 0-4.

  A walk that took a different row than the old tests would print a
  different sequence from the parent's.
- **`attempt_hist.py`** gains `--parent-patches` (B4+).
- **`cross_record.py` (a)** builds HEAD with `probes_b3.py`.
- **`reach/build_reach.py`**: the forcing/nomem/trial probes sit at the
  walk's case labels, the same events. The sel1/rung probes use the same
  restatement as `probes_b3.py`. The plain prototype builds.

## Deviations, findings and questions

1. **FINDING: S-F1 is an equivalent mutant** (above). The design's §4.4
   lists S-F1 as "nomem row deleted (S259's intent, as a row)". Under the
   `on` masks it cannot fail: `refuse` catches the arrival with the same
   action. K60's protection is held TWICE:
   - row 1 precedes row 2;
   - row 2 is not `on` NOMEM.

   Only the label derivation is a single-point failure.
   Recommendation: §4.4's S-F1 line should say so, and S259 is its row.
2. **FINDING: `call_graph.py --family fallback` and `state_readers.sh` were
   both readers of the dispatch's SHAPE.** Each failed closed, as designed:
   - `call_graph.py` exited 2 on the missing `fit_select`;
   - `state_readers.sh` would have silently lost four recovery-point
     members once the label reads moved into `fit_labels`. It is fixed by
     reading that body.

   B4/B5 should grep these two the same way (they will move again when
   `prefilter_decision` and `esel_of` are rewritten).
3. **CHOICE: `fit_trace_labels` is kept separate** from `fit_labels`. B2
   deviation 8 suggested the trace read `fit_labels`, which would re-aim
   S623. It is kept because the trace's label set is then an independent
   second derivation of the walk's input: a label plant shows up as a
   `row@label` mismatch in fbt (a) rather than moving both sides together.
   It is trace-only text, so this is no parallel mechanism in the product.
4. **CHOICE: FitSel gains no fields.** The edit set's B3 entry says "FitSel
   gains the arrival's label set and the fired record". The walk takes the
   labels as an argument, and no `applies` reads the fired record, so
   adding either would be an unread field (D77). The initializer moved to
   the top of the branch, in designated form.
5. **CHOICE: S624's anchor is kept verbatim.** `FIT_TRACE(&cx, rung->name,
   restart_term, "fb-size");` keeps its text and indentation: the walk's
   row is named `rung`, and `restart_term` is the routine's const. So S624
   re-runs and is not re-aimed. The [SEL-1] rows' `fb-sel1` record sits
   just above it, keyed on the row's `on` label (the arrival family).
6. **FINDING: the `--step` derivation misses state-write reach** (S189,
   S191, S192: a row now writes the state their owners read). Recorded as
   a limit of the reach relation: it follows calls and table names, not a
   state member's writer. Recommendation: B4/B5 keep a judgment column.
8. **FINDING: S633 went UNDETECTED once the walk became the dispatch.**
   At B2 the oracle's `fit-sets` check caught the plant (drop-prefilter
   carries no size-cap figures). From B3 the designed detector was fbt (c)'s
   `VM_PREFILTER_WHY` shape, and it passed under the plant. The (c) witness
   `(\p{Xwd})` reaches `drop-prefilter` AFTER `prefilter-collapse`, which
   had already carried the first refusal's figures. The planted artifact
   therefore printed `hybrid 1028516 > 1000000` (the EXACT attempt's
   figure) where the tree prints 1028522 (the collapsed attempt's), and the
   shape held. Fixed by a second witness that makes drop-prefilter the
   FIRST size rung (`-fno-prefilter-collapse`): under the plant it reads
   `hybrid 0 > 0`. fbt is 191/0. The general form: *a carry cell is
   observable only on a witness where no earlier row carried the same
   field.* The full byte compare (emit_sweep) would also have caught it,
   but S633's arm is `fallbacktable`.
9. **Retired, said explicitly:** the oracle's arrival and notes halves.
   The independent controls that remain for the dispatch are:
   - the default-build bytes, stderr and rc (emit_sweep, every variant);
   - the attempt histogram (a probed copy that shares no code with T1);
   - fbt (a)'s hand-written sequences and post-row fields;
   - fbt (e)'s hand-written notes;
   - alloc_check W4/W5.

## Owed: the heavy chain (ARMED)

- **Chain:** `worktrees/decfbB3/build/land/chain.sh`, B2's shape:
  - `make`;
  - `scripts/perfrun --label decfbB3 --timeout 5400 -- build/land/test.log`;
  - `make strict`, `make alloc`, `make testscripts`;
  - mech `VALIDATE_ONLY=1`;
  - the 55 mech rows above.
- **Waiter:** `build/land/waiter.sh`, a `nohup setsid` loop. It waits for
  `== LIGHT DONE` in `build/b3/light/trailer.log`, which `light.sh` writes
  only when every step passes, AND for `worktrees/decfbB3/.lift`.
- **Verdicts:**
  - `build/land/trailer.log` has one `rc=` per stage and ends `== CHAIN
    DONE`.
  - make test: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'
    build/land/test.log` (empty = green), read with the perfrun note.
  - mech: its own `== mech run COMPLETE` trailer in `build/land/mech.log`.

## Commits

`lane/decfbB3`, `0f37bfd8..`:
- `c5ef46db` the dispatch, the `sets` routine, the fired record, the notes
  loop; fbt (d) shrunk and (e) added; oracle_sweep SITES;
- `d46ec721` probes and instruments re-anchored; S253/S259 re-aimed;
  S646-S651;
- `f0353a17` the fallback call graph, anchor map and edit-set record;
- `1bbdce9f` CLAUDE.md, the design note's B3 outcome, testing.md;
- this report.
