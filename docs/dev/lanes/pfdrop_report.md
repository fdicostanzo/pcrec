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
