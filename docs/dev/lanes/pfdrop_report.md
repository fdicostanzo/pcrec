# Lane pfdrop — D135: the prefilter-drop rung and `--fast-or-fail`

Branch `lane/pfdrop` from main `736a07f1`. Plan row `[PF-DROP]`. Mac only.
Not pushed.

## 1. What was built

- **The size-cap ladder is now one first-match table.** It is `fit_rungs[]`
  in `src/core/compile.c`, with rows in order: `unroll-rescue`,
  `prefilter-collapse`, `drop-anchored`, `drop-premul`, `drop-prefilter`,
  `refuse`.
  - Each row carries a name, its own caller deny bit, a `degrading` column,
    an `applies` predicate and an action.
  - `fit_select` takes the first row that applies and is not denied. The
    catch branch's `switch` only carries that row out.
  - The old `size_eligible`/`drop_eligible`/`premul_eligible` if-chain is
    gone. Each rung's conjuncts moved into its row's predicate, less the
    shared `cx.size_cap_refused`, which is now the walk's own guard.
  - The unroll rescue is a row too (`applies` NULL). Its choice is still made
    inside `size_term_choose`, which now takes `rescue_ok`: the table's
    verdict on that row.
- **The new last rung, `drop-prefilter`** (`SDR_NO_PREFILTER`, `SDR_MAX` 3).
  - When an emitted-size cap refuses a VM hybrid that still has a prefilter,
    the rung ORs `PCREC_NO_PREFILTER` into the driver's flags and re-emits.
    This is the premul rung's own shape, so the prefilter decision needs no
    new input.
  - It restarts the size term, for the collapse rung's reason. So
    `COMPILE_MAX_ATTEMPTS` gains a third ladder run:
    `3 + 3*(N+1) + 1 + SDR_MAX`.
  - It is not offered under `-fprefilter`, or on a [SEL-1] retry
    (`!dfa_disabled`). The second exclusion keeps `esel_of`'s premise true: a
    drop rung and a DFA overflow never share a compile.
  - Stamps: `RX_VM_PREFILTER "none"`, `RX_ENGINE_SEL "size-cap-retry"`, and a
    new line `RX_VM_PREFILTER_WHY "size cap retry, hybrid N > CAP"`. The new
    line is written only where the rung fired. `N` is the last refused
    attempt's size.
  - It prints the ladder's loud stderr note.
  - Apart from those two stamps, the artifact is byte-identical to the
    caller's own `-fno-prefilter` artifact. A check asserts this.
- **Witness.** `(\p{Xwd})` under `-e utf8`.
  - Before: refused at 1,026,586 bytes.
  - After: compiles at 31,300 bytes, with answers checked against libpcre2
    (§4).
- **`--fast-or-fail`** (working spelling; `PCREC_FAST_OR_FAIL`, bit 41).
  - It works through one predicate, `fit_rung_denied`: a row is transparent
    if the caller set its own deny bit, or set the switch and the row is
    degrading. No rung tests the switch itself.
  - It is masked out of `rx_info.flags`, so an artifact that fits is
    byte-identical with or without it.
  - It is parsed in `cli/main.c` as a policy flag, not an axes.def `-f` row.
  - Existing per-rung denies are unchanged.

## 2. Rung order: evidence

- **Setup.**
  - Mac M1, gcc-16 `-O2`, find-all over 1 MiB subjects.
  - Each cell: 5 launches round-robin × 7 passes, median of the per-launch
    medians, in ns/byte.
  - The box was loaded (load1 4-6).
  - Scripts are in the session scratch (`pfdrop-scratch/tm/run.sh`,
    `run2.sh`, `drv.c`), not committed.
  - **The noise floor on this box is about ±5%** (`docs/dev/reseed/
    timing_mac.md`'s base/deny column). So every ratio under ~1.06 below is
    directional at best.

| rung | witness | subject | before (ns/B) | rung taken (ns/B) | cost |
|---|---|---|---:|---:|---:|
| unroll-rescue (K 8→1) | `(x(?:(?:ab|ba){3}c){1,300}y)` (counter rung, `RX_VM_RUNGS 0x10`) | matching `x(ab|ba){3}c…y` runs | 6.78 | 7.20 | **1.06x** (all five K=1 launches slower than all five K=8) |
| unroll-rescue | `((?:the|fox) ){2,50}`, `(x[ab]{1,4000}y)` | text / counts | 2.350 / 5.047 | 2.364 / 5.045 | 1.00x — **vacuous**: K did not change these programs (no counter rung) |
| prefilter-collapse | `(q[a-z]{3,9}z)` exact vs `-fprefilter-collapse` | text / sparse | 0.219 / 0.024 | 0.225 / 0.024 | **1.03x** / 1.00x |
| drop-anchored | (not re-measured) | — | — | — | `_match` pays a reverse pass, ~50% of the DFA's time ([OPT-2] STEP 2, already in the spec) |
| drop-premul | `(?:quick|lazy)\s+[a-z]+` DFA | text / sparse | 1.328 / 0.310 | 1.398 / 0.310 | **1.05x** / 1.00x (spec cites ~1.27x scan-bound) |
| **drop-prefilter** | `(\p{Xwd})` hybrid (cap raised) vs `-fno-prefilter` | sparse (1 word char / ~700 B) | 1.616 | 2.835 | **1.75x** |
| drop-prefilter | `(\p{Xwd}+)` | sparse | 1.621 | 6.407 | **3.95x** |
| drop-prefilter | `(q[a-z]{3,9}z)` exact vs none | text | 0.219 | 4.419 | **20x** |
| drop-prefilter | `(\p{Xwd})` | dense text (every other char matches) | 14.713 | 3.183 | **0.22x: FASTER** |
| drop-prefilter | `(\p{Xwd}+)` | dense text | 8.295 | 4.337 | 0.52x: faster |

**What the numbers settle, and what they do not.**

- The prefilter drop is the dearest rung wherever matches are sparse, by a
  wide margin: 1.75-20x against ≤1.06x for every other rung measured. **Last
  place is confirmed.**
- A collapsed prefilter keeps almost all of the exact one's value (1.03x
  against the drop's 20x on the same pattern). So collapse-before-drop is
  confirmed decisively.
- The three small rungs (unroll 1.06x, collapse 1.03x, premul 1.05x) sit
  inside or at the Mac noise floor. **The Mac cannot order them against each
  other.**
  - It does not need to for correctness: engine scope makes most pairs
    disjoint. Collapse and prefilter drop are VM-hybrid, anchored and premul
    are DFA, and the unroll rescue runs inside every VM attempt, so it is
    structurally first.
  - Anchored-before-premul was ruled APPEND (K59) and is not re-litigated.
  - If the manager wants those three ordered by number, that is a Linux
    measurement (ubuntubudu, quiet box) to schedule.
- **A side finding, not acted on:** on a dense subject the hybrid is *slower*
  than the bare VM (`(\p{Xwd})` 4.6x slower with the prefilter). The
  prefilter cannot dismiss anything there and adds its own pass. This could
  be a D119 optimization-loop cause (a hybrid whose prefilter language
  admits most bytes). It is unmeasured on the bench; it is filed here only
  as an observation.

## 3. Degrading classification

A rung is degrading if it makes the artifact slower in order to make it fit.
All five measure slower, so all five are degrading, and `--fast-or-fail`
denies all of them today.

| rung | degrading | evidence |
|---|---|---|
| unroll-rescue | **yes** | 1.06x on a counter-rung witness (§2). The design note's own record is "~1-3% slower on single-level large counts", with parity on its selected population. The rescue picks the largest fitting K precisely because a smaller K costs throughput. |
| prefilter-collapse | yes | 1.03x here; a superset filter admits more candidates by construction |
| drop-anchored | yes | `_match` reverse pass, ~50% ([OPT-2]) |
| drop-premul | yes | 1.05x here, ~1.27x scan-bound (`opt3_dfa_scan_measurement.md`) |
| drop-prefilter | yes | 1.75-20x where matches are sparse (§2) |

- The `degrading` column exists so that a future rung costing no run time
  (a pure layout change) is allowed under the switch by saying so in its
  row.
- The unroll rescue was first classified *not* degrading, from the vacuous
  witnesses. The counter-rung witness reversed that, and the table says yes.
  It is the one judgment call here. If the manager reads 1.06x on a loaded
  Mac as noise, flipping its cell is one token, and
  `run_size_term.sh` §5's new cell flips with it.
- **Out of scope, stated rather than silently excluded: the [SEL-1] rungs.**
  - These are DFA state-cap fallbacks: engine DFA→VM, and a VM prefilter
    collapsed or dropped because its own DFA build overflowed.
  - They respond to construction budgets during `auto` engine selection,
    not to the emitted-size caps. They are not rows of this table, and
    `--fast-or-fail` does not deny them.
  - A caller who wants those do-or-die already has `--engine=dfa` and
    `-fprefilter`.
  - Question Q2 below asks the manager to confirm this reading of "every
    rung".

## 4. Tests (oracle-verified)

- **`tests/uprops/size_ladder_prefilter_drop.rxt`** (new).
  - 11 subjects / 19 cases on `(\p{Xwd})` under utf8: spans plus group 1.
  - Every expectation was checked against libpcre2 **10.46**, the
    reference. That was a light `pcre2test` probe over the tailnet; the
    transcript is in scratch `probe_1046.txt`.
  - They were also checked against 10.48 locally.
  - Includes U+203F (Pc) and U+0301 (Mn) as members. My first guess was
    wrong there; the oracle corrected it.
  - Result: 19/19 pass. The base compiler refuses the block, which is the
    failing direction.
- **`tests/resource/run_resource_tests.sh`, new section `[PF-DROP]`** (9
  cells):
  - the witness compiles, with its stamps, its WHY line and its note;
  - it is byte-identical to `-fno-prefilter` apart from the two stamps;
  - four `--fast-or-fail` cells, one per retry rung (prefilter drop,
    collapse, anchored, premul). Each first checks that the witness takes its
    rung at the default (reach), then that it refuses on the size cap under
    the switch;
  - a fitting `(\p{L})` is byte-identical under the switch.
- **`tests/uprops/run_uprops_tests.sh` §5** (utf8 arm only, so
  `make test-uprops-utf8`):
  - sweeps the rescued artifact over the whole code-point space;
  - requires it to equal `\p{Xwd}`'s member set, and libpcre2's through
    `uprops_compare.py`, whose drift policy needs pcrec's own Mn/Pc/Cn sweeps
    beside it.
  - `uprops_sweep.c`'s capture array is now `RX_NCAPS` rows, so a captured
    pattern sweeps without overflowing it.
- **`tests/codegen/run_size_term.sh` §5**: new cell. `--fast-or-fail` denies
  the unroll cap rescue, and the reference compiler's witness refuses on the
  code cap.
- **`tests/codegen/run_prefilter_collapse.sh`: the K41 witness-2 control is
  RE-PINNED.** The old control said "`-fno-prefilter-collapse` restores the
  refusal". That is false now: with the collapse row denied, the prefilter
  drop takes the witness. The control now asserts the drop's stamps under
  `-fno-prefilter-collapse` and the refusal under `--fast-or-fail`. The
  intent is kept: denying the collapse row alone moves the artifact to
  another rung, which proves the default's hybrid was the collapse's doing.
- **Corpus identity / refusal-set sweep.**
  - Every corpus `pattern` block with its encoding, features and engine
    (3,578 distinct; 177 blocks with flags, esc, var, budget or analysis were
    skipped), base `736a07f1` against this branch, at default axes.
  - **0 byte moves. 1 rc move: the witness itself.** 3,138 both compile,
    439 both refuse.
  - The script is scratch `idsw/sweep.py`.

## 5. Spelling proposal and open questions (manager rules)

- **Q1 — spelling.** The working spelling is `--fast-or-fail`, bit
  `PCREC_FAST_OR_FAIL`.
  - I propose keeping it as a **policy flag, not a `-f` axis**. An axes.def
    row would put it in `--list-axes`, in `make test-axes`'s sweep and in
    tuning.md §2's bit cross-check. It is not an answer-identical shape
    choice; it narrows what pcrec accepts, the way a limit does.
  - Alternatives:
    - `--size-fit=fast-or-fail|degrade`: a value parameter, extensible, but
      it needs a `pcrec_options` field, which is a library struct change.
    - `-fno-degrade-to-fit`: axis-family spelling, rejected for the reason
      above.
  - A `config`-block key is not built (D77).
- **Q2 — scope.** Confirm that the [SEL-1] DFA-state-cap fallbacks are
  outside "every rung" (§3). My recommendation is yes, outside.
- **Q3 — abi.** No bump taken.
  - The new stamp line and the note appear only on artifacts that were
    refused before. The corpus sweep found no existing artifact moving.
  - `--fast-or-fail` is masked out of `rx_info.flags`.
  - This is the K53/K59 precedent (neither bumped). If the manager reads a
    new stamp NAME as an abi event, the bump would be 50→51 on top of
    uvbuild's.
- **Q4 — a changed contract, flagged.** `-fno-prefilter-collapse` on an
  over-cap hybrid used to REFUSE. It now ships with no prefilter.
  - limits.md, tuning.md §2.17 and the K41 control say so.
  - The flag now buys "never a superset prefilter", and refusal is
    `--fast-or-fail`'s job.
  - This follows from D135's "existing per-rung denies stay", with the
    ladder as a first-match table. Flagged because it changes what an
    existing flag delivers.
- **Q5 (D77, not built).** A [SEL-1] retry whose collapsed prefilter is
  over the SIZE cap still refuses. The prefilter-drop rung excludes
  `dfa_disabled` to keep `esel_of`'s premise. There is no witness. The
  trigger would be one found.
- **Pre-existing, noted.** The collapse rung is offered to a pattern with no
  collapsible repeat. `(\p{Xwd})` pays one wasted attempt whose collapsed
  language equals the exact one before the drop fires. Not changed.

## 6. Spec hunks (D80), same change

- **`docs/spec/limits.md`**
  - New §8 section "The size-cap ladder, and `--fast-or-fail`", with the
    order, engine, cost, deny and degrading table, the switch, and the new
    rung's stamps and witness.
  - The prefilter-drop note text.
  - The §3.3 [OPT-4] paragraph (what `-fno-prefilter-collapse` buys now).
  - The `+2` gap narrowed for hybrids.
- **`docs/spec/cli.md`**: a `--fast-or-fail` section and a revision entry.
- **`docs/spec/tuning.md`**: a §2.5 fourth off-route paragraph, and §2.17's
  two passages on what the deny buys. No "(bit N)" was added to §2, because
  the switch is not an axis and `run_axes.sh` cross-checks those mentions.
- **`docs/spec/match_api.md`**: §6.3's `"size-cap-retry"` row names the new
  rung and its stamps (it also now names the K59 rung, which the row had
  omitted), and the macro listing shows `RX_VM_PREFILTER_WHY`.
- **`registry.md`**: untouched. No axis or flag list moved.
- **Code comments**: `internal.h` (the `SDR_NO_PREFILTER` value and the
  `ESEL_SIZE_CAP_RETRY` table row) and `select_engine.c` (`esel_of` notes B
  and D).

## 7. Mech rows

The highest S-id on main was S408; uvbuild owns S409-S419.

| row | plants | expected detector |
|---|---|---|
| S420 | prefilter-drop row never applies | harness on `size_ladder_prefilter_drop.rxt` (block refuses) + resource |
| S421 | `fit_rung_denied` ignores `PCREC_FAST_OR_FAIL` | resource's four ff cells + pfcollapse K41 ff control |
| S422 | `RX_VM_PREFILTER_WHY` never written | resource WHY cell + pfcollapse K41 control |
| S423 | prefilter-drop row's `degrading` cell reads false | exactly one resource ff cell (locality) |

- **S237** and **S252** were RE-ANCHORED onto `fit_anchored_applies` and
  `fit_premul_applies`. Their intent was re-verified: the rung is never
  taken and the walk falls through as the old chain did.
- **S253**'s anchor survived verbatim, with the same column.
- All seven pass `VALIDATE_ONLY=1`. Measured verdicts are OWED (§8).

## 8. Validation

**Done, green (Mac):**

- `make strict CC=gcc-16`: "strict: whole tree compiles clean with -Werror
  -Wshadow".
- `tests/resource/run_resource_tests.sh`: checks passed 38, failed 0
  (Section 2 is the known darwin SKIP). A later edit was cosmetic only
  (padding in one message).
- `tests/codegen/run_prefilter_collapse.sh`: 58 passed, 0 failed.
- `tests/codegen/run_size_term.sh`: 32 passed, 0 failed.
- `tests/harness/run.sh tests/uprops/size_ladder_prefilter_drop.rxt`:
  19 passed, 0 failed.
- `ENC=utf8 UPROPS_NAMES="Xwd Mn Pc Cn" tests/uprops/run_uprops_tests.sh`:
  27 passed, 0 failed, including §5's libpcre2 10.48 comparison.
- Corpus identity/refusal sweep: §4.

**OWED: running detached now** (`nohup caffeinate`). The chain script is
`worktrees/pfdrop-scratch/val/chain.sh`, and its summary goes to
`worktrees/pfdrop-scratch/val/chain.log`, one line per step. The completion
line is `=== chain DONE`. Each step writes its own log in the same directory.

- `make test-registry` (includes `limits_check.sh`, whose comment quoting
  `COMPILE_MAX_ATTEMPTS` was updated), `test-rxtsource`, `test-resource`,
  `test-codegen` (accepted darwin red: the `nm arm_a.o` line only), and
  `test-uprops-utf8`.
- Mech, one row at a time: S237, S252, S253, S420, S421, S422, S423.
- `make test-axes` with `AXES="-fno-prefilter-collapse"`. This is the one
  axis whose delivered behaviour changed (Q4). The corpus has no over-cap
  hybrid, so I predict it is answer-identical.
- The verdict for each make target is its `*** [test-X] Error` lines.

**Owed beyond this lane:**

- a Linux full `make test` at merge;
- a Linux timing pass, only if the manager wants the three small rungs
  ordered by number (§2).

## Triage (pftri)

Lane `pftri` (sonnet, 2026-09-30) read the chain's `test-registry` and
`test-rxtsource` logs (`worktrees/pfdrop-scratch/val/`). Both reds were STALE
PINS that pfdrop's own delivery should have moved; neither is a regression, and
neither is environmental. Verdicts are make's `*** [test-X] Error` lines, not
grep counts.

### test-registry (rc=2): one real check failure, one stale allowlist

The log has exactly one `FAIL:` line (`test-registry.log:1042`), from
`tests/registry/limits_check.sh`'s D107 detector:
`src/core/internal.h:2430: enum member SDR_NO_PREFILTER = 3 -- ... on NEITHER
allowlist`. `run_registry_tests.sh`'s coverage guard then reported
`limits_check shows 36 passing checks (37 expected; 1 failed`, the same failure
seen from the wrapper (line 1052), so it is one failure counted twice.

- Cause: [PF-DROP] added the drop ladder's fourth rung ordinal
  `SDR_NO_PREFILTER = 3` (and moved `SDR_MAX` 2 -> 3). It is the same kind as
  `SDR_NONE`/`SDR_NO_ANCHORED`/`SDR_NO_PREMUL`/`SDR_MAX`, which are on the
  NON-LIMIT allowlist as "THE FOURTH KIND — cardinalities and ordinals". The
  new sibling was not added.
- Fix (`tests/registry/limits_check.sh`): `SDR_NO_PREFILTER` added to the
  NON-LIMIT allowlist with the existing kind's reason (a rung ordinal, a number
  nothing can be measured against), and the comment that names the family
  updated. Not a loosening: the constant is an ordinal beside three
  already-allowlisted ones, and the detector still fires for any other unlisted
  constant.
- The coverage guard's pin (37) is unchanged and correct: the run before the
  fix counted 36 only because the failed check did not print its PASS line.
- Evidence: `bash tests/registry/limits_check.sh` after the fix:
  `checks passed: 37`, `checks failed: 0`.

### test-rxtsource (rc=2): the census was not re-pinned for the new corpus file

10 FAILs, one cause: pfdrop added `tests/uprops/size_ladder_prefilter_drop.rxt`
(1 file, 1 block, 19 non-comment lines: 8 `m`, 3 `n`, 8 `g`) and did not move the
census. Every FAIL is that count read from a different angle: `census MOVED`
(found 259/4314/32545, pinned 258/4313/32526), `file list`, the three C1 block
counts, the case-row derivation, C3's file count, C3's reconcile line and the
W23-S7 entry-file count. Deltas +1/+1/+19 match the new file exactly.

The five `HARNESS FAILURE` lines for `tests/findings/golden/*.rxt` in the same
log are NOT this lane's: they are the five known unparseable-head golden files
that leg B / C0a already name (`PASS: leg B ... the 5 known unparseable-head
(golden analyzer-dialect) file(s)`), untouched by pfdrop.

Re-pins in `tests/rxtsource/run_rxtsource_tests.sh`, each with a dated comment
naming the file and why:

| pin | old | new | why |
|---|---|---|---|
| `CENSUS_FILES/BLOCKS/LINES` | 258/4313/32526 | 259/4314/32545 | the new file |
| `RUNSH_FILES/BLOCKS/LINES` | 234/4313/32526 | 235/4314/32545 | same delta; `tests/uprops/` is a run.sh directory, not known_fail |
| `C3_SKIP` | 18455 | 18474 | +19 SKIP |
| `C3_SKIP_NOPYTHON` | 1964 | 1983 | all 19 are no-python-expression (`\p{Xwd}` has no python `re` spelling), so python-version-invariant |
| `C3_VERIFIABLE` | 15960 | 15979 | PASS+INFO+nopython+perr-accept moves by the same 19 |

C3's classification was MEASURED, not inferred: `verify_rxt.py
tests/uprops/size_ladder_prefilter_drop.rxt` reports `SKIP=19 (...
no-python-expression=19 ...)`, `PASS=0`. The C3 reconcile equation
(`PASS + INFO + SKIP + 89 = CENSUS_LINES`) then holds with `CENSUS_LINES=32545`.

### Re-validation

- `bash tests/rxtsource/run_rxtsource_tests.sh` (the exact script
  `make test-rxtsource` runs; log `worktrees/pfdrop-scratch/val/pftri_rxtsource.log`):
  `checks passed: 271`, `checks recorded: 1`, `checks failed: 0`, rc=0, ending
  `PASS: rxtsource: INV-COMPAT holds over 259 files / 4314 blocks / 32545
  expectation lines`. The one RECORD is the standing darwin python-3.9 vs
  3.14 C3 note. Before: 10 failed.
- `bash tests/registry/limits_check.sh`: 37 passed, 0 failed (before: 36/1).
- **OWED: `make test-registry` as a whole target.** pfdrop's chain (test-codegen,
  mech S237/S252/S253/S420-S423, test-axes) was still running when this lane
  ended, so the 6-minute registry run was not started alongside it. A detached
  follow-up (`pftri_followup.sh`, under `nohup caffeinate`) waits for
  `=== chain DONE` in `chain.log`, then runs `make test-registry CC=gcc-16`.
  Its result is one line in `worktrees/pfdrop-scratch/val/pftri_followup.log`
  ending `=== pftri DONE`; the full log is `pftri_test-registry.log` there.
  Read the verdict as make's `*** [test-registry] Error` lines.
- The later chain steps (codegen, uprops-utf8, mech, axes) had not reported
  when this lane ended; their reds, if any, are unclassified. None of the
  fixes above touches `src/`, so those steps are unaffected by this triage.

## Triage (pftri2)

Lane `pftri2` (sonnet, 2026-09-30), continuing pftri. Inputs:
`worktrees/pfdrop-scratch/val/` (chain.sh, chain.log, per-step logs).

### mech S237/S252/S253/S420-S423: HARNESS INVOCATION ERROR, not a detection result

All seven rows `rc=2` in ~1 s. Each log reads
`FATAL: no sabotage definitions matched 'S237-' under .../tests/mech/sabotages/`:
`chain.sh` passed the row as `S237-` (trailing dash), but
`run_sabotage_matrix.sh` takes an ID PREFIX (`S237`), matched against the
`sabotages/S*.sh` listing (files are `S237_size_drop_rung_deleted.sh`, no `S237-`
prefix). Nothing was measured; the rows were never run. Re-driven SOLO with the
correct prefix (below).

Intent of the two re-anchors (S237/S252) was re-verified by diff against the
branch point: both move the rung's eligibility from the inline
`cx.size_cap_refused && ...` chain into the `fit_rungs[]` row predicates
(`fit_anchored_applies` / `fit_premul_applies`, `src/core/compile.c:~697`),
conjunct for conjunct less the walk's own shared guard; the plant (`return
false`) still removes exactly that one rung and the walk falls through as before.

### test-codegen (rc=2): TWO reds, one accepted and ONE REAL (fixed)

`test-codegen.log` has exactly two `FAIL:` lines and one `*** [test-codegen]
Error 1`:

1. `FAIL: nm could not read arm_a.o (no rx_search symbol)` — the standing darwin
   probe red (documented in wake.md and 30+ lane reports). ACCEPTED, not this
   lane's.
2. `FAIL: [SABANCHOR] ... STALE ANCHORS: 1 -- S295_vm_anchor_bound_flags_leak.sh
   src/gen/emit_dfa.c ANCHOR NOT FOUND` — REAL, pfdrop's own. [PF-DROP]
   appended `| PCREC_FAST_OR_FAIL;` to `emit_info_def`'s `strategy_denials`
   mask (`src/gen/emit_dfa.c:2697-2705`), so the line S295's `SAB_BEFORE` quotes
   (`PCREC_NO_REQ_BYTE;`) is now `PCREC_NO_REQ_BYTE |`. The delivery re-anchored
   S237/S252 but never ran `scripts/m6read_check_sab_anchors.py` over the whole
   set, so a row whose FILE it edited (rather than a row it meant to touch)
   went stale. Class: stale anchor after an emitter edit (coding_guide §4.3).
   Fix (commit `7ac53930`): S295 `SAB_BEFORE`/`SAB_AFTER` trailing `;` -> `|`.
   Intent unchanged: the plant still drops exactly `PCREC_NO_VM_ANCHOR_BOUND`
   from the mask (the rest of the mask, incl. `PCREC_FAST_OR_FAIL`, is untouched
   and still compiles). `python3 scripts/m6read_check_sab_anchors.py`:
   `sabotages checked: 375 (391 anchor sites)` / `all anchors resolve`.

### Other chain steps (verdicts from chain.log)

- test-resource rc=0, test-uprops-utf8 rc=0 (green).
- test-registry / test-rxtsource: pftri's stale-pin fixes (above).

### OWED at hand-off (detached, `nohup caffeinate`, log paths)

Armed by `val/pftri2_chain.sh`, which waits for `=== pftri DONE` in
`pftri_followup.log` (itself waiting on the chain's `test-axes
AXES=-fno-prefilter-collapse`, still in its baseline run at hand-off), then
runs one at a time: mech `S237 S252 S253 S420 S421 S422 S423 S295` (logs
`val/mech2_<id>.log`) and `make test-codegen` (`val/pftri2_test-codegen.log`).
One-line-per-step summary: `val/pftri2.log`, ending `=== pftri2 DONE`.
Read mech verdicts as DETECTED/UNDETECTED/UNREACHED/ANOMALY in each
`mech2_*.log` (expected: all DETECTED; S421 is answer-identity-neutral by
design, check its SAB_DESC for the expected suites); read test-codegen as
make's `*** [test-codegen] Error` line -- expected: only the standing `nm
arm_a.o` FAIL remains. Also still owed from pftri: `val/pftri_followup.log`
(`make test-registry`) and `chain.log`'s test-axes line.
