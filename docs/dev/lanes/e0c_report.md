# e0c — E0c of compound_entries.md rev 4: every exported entry written through its row's combinator emitter

Lane `e0c` (opus), 2026-10-16, branch `lane/e0c` from main `353249282`. Design:
`docs/design/compound_entries.md` rev 4 §4.1 ("each combinator has ONE emitter") and §5.1
(E0c); D163 addenda 7-11, D88 addendum 1. Predecessors: `e0build_report.md` (E0a/E0b),
`e0sw_report.md`.

## 1. What was built

A RE-SPELLING. No emitted byte is meant to move and nothing here is an abi event.

- **The combinator column is read.** `EntryComb` became `PcrecEntryComb`
  (`core/internal.h`). `pcrec_entry_shape` stores each entry's row combinator in
  `Job.entry_comb`, and `pcrec_entry_comb` answers it. It fails as an internal error when
  asked before the shape is stated or for an entry with no row on the shape.
- **`src/gen/emit_comb.c` (new): the combinator emitters.** `pcrec_emit_entry(cx, g, e, t)`
  reads `e`'s combinator and calls that combinator's ONE emitter. The engine hands a
  `PcrecEntryText` with one member per combinator. A row whose member the engine did not
  supply is an internal error.
  - **forward** (`comb_forward`) writes all nine forwarding entries:
    - INERT: the DFA's three `_in` entries (were `emit_in_entry_defs`'s three texts).
    - CALLER: the VM's three `_in` entries (were `vm_emit_search_in`/`_match_in`/
      `_match_caps_in`).
    - OWN, OWN_TIERED and EMPTY: the VM's three un-suffixed entries on each entry rung
      (were `vm_emit_default_entry`, moved verbatim as `fwd_own`).

    Each `_in` binding is now ONE format, and the per-entry differences (return type,
    parameter layout, arguments, whether the caller's variables are arguments) are data in
    `fwd_sigs[]`.
  - **finish-at** (`comb_finish_at`) is axis G's dispatch on `PcrecFinForm`, the FINISH
    row's action:
    - FILTER: `emit_match_def`/`emit_match_caps_def`, moved verbatim.
    - VERIFY: `pcrec_emit_dfa_anchored_match` (the old `emit_anchored_entries` less its
      caps half, still in `emit_dfa.c` because it builds the anchored machine) plus the
      delegate `emit_anchored_match_caps_def`, moved.
    - NOMATCH: `emit_nomatch_match_def`, moved, plus the same delegate.
    - PART: the compound's one attempt, `pcrec_emit_compound_match` in `emit_compound.c`.
  - **locate-then-finish** is `pcrec_emit_dfa_engine` under the entry's own linkage, for
    the DFA's `<p>_search` and for the VM hybrid's embedded search (`PCREC_ENTRY_PREFILTER`).
  - **first-nonzero** is `emit_compound.c`'s emitter, made extern as
    `pcrec_emit_compound_search`. The shell's combinator check moved into it.
    `pcrec_emit_compound_body` split into `pcrec_emit_compound_parts` (the parts' texts)
    and the three controller entries, which go through their rows.
- **The engine emitters keep only the ORDER of the file and what each entry is built from.**
  - `pcrec_emit_dfa`: the search through locate-then-finish, axis G's pair through
    finish-at, `emit_in_entry_defs` reduced to its comment plus three dispatches, and the
    shell branch through first-nonzero and PART.
  - `vm_emit_entries`: the rung picks the OWN binding, then six dispatches.
- **Updated:** `src/gen/CLAUDE.md` (the `entries.c` entry and a new `emit_comb.c` entry,
  the compound entries), file headers, and comments naming moved functions, including
  `tests/codegen/run_anchored_match.sh`'s header.

Not routed (§4 item 2): the VM's internal `_run` bodies.

## 2. Validation

| check | command / file | result |
|---|---|---|
| build | `make -j4` (taskset 0-7) | clean |
| strict | `make strict` | clean (`-Werror -Wshadow`) |
| spot identity | `build/scratch/quick.sh`: 16 shapes x 8 arms, `.c` and `.h` against a main build at the same `-o` basename | 128 compiles, 0 differ |
| sampled zero-mover sweep | `scripts/emit_sweep.py --ref-bin <main 353249282> --every 10 --jobs 4` (taskset 0-7), self-check on, every default stream | **0 movers, 0 asymmetric** on c-default, c-vm, emit-ir-vm, facts, the four emit-ir-auto arms, stderr, composition and dumps (5,790 argv rows, 106 composition artifacts; floors not applied, partial population); rc 0, 158 s |
| `make test-codegen` | `build/scratch/codegen.log` | rc 0, `run_group: 16/16 scripts passed` |
| `make test-compound` | `build/scratch/compound.log` | rc 0, `test-compound: PASS` |
| stackdepth (clean) | `tests/thread/run_stackdepth_tests.sh` | 5/0 (the S1071 control) |
| anchors | `scripts/m6read_check_sab_anchors.py` | 743 rows / 767 sites, all resolve with their SAB_COUNT |
| mech fields | `VALIDATE_ONLY=1 run_sabotage_matrix.sh` | S1069-S1078 FIELDS OK |
| **full emit_sweep, every stream and arm** | `build/v/chain.sh` | **OWED** (§3) |
| **`make test`** | `build/v/chain.sh` through `scripts/perfrun` | **OWED** (§3) |
| **single-row mech, 31 rows** | `build/v/chain.sh` | **OWED** (§3) |

### 2.1 Sabotage: S1069-S1078, each plant on the emitter it proves live

Every plant was applied by hand to a `git archive HEAD` tree (`build/scratch/plant.sh`,
through `tests/mech/lib/replace.py`). The tree was built and the row's own suites were run.
The matrix figures are owed at the slot.

| id | emitter / binding | plant | hand result |
|---|---|---|---|
| S1069 | forward INERT | the DFA `_match_in` answers -1 | framebuf 2fail/5pass (corpus framebuffer.rxt 0fail: its DFA cells never match AT startpos, so dropped from the row) |
| S1070 | forward CALLER | every VM `_in` ignores a non-NULL descriptor | corpus 1fail/15pass, framebuf 3fail/3pass |
| S1071 | forward OWN_TIERED | the fast tier's FRAMES returned, no escalation | stackdep 3fail/3pass (clean 0fail/5pass) |
| S1072 | forward EMPTY | the forward rung passes NULL, not the empty descriptor | corpus (tests/vars/basic.rxt) 18fail/6pass |
| S1073 | finish-at FILTER | `_match` drops the start-equals-`ctx->pos` test | anchdiff 10fail/4pass (1,280 patterns diverge) |
| S1074 | finish-at VERIFY/NOMATCH | the two own-body forms swapped | anchoredmatch 21fail/13pass |
| S1075 | finish-at dispatch | VERIFY written as FILTER | anchoredmatch 25fail/12pass |
| S1076 | finish-at PART | the compound `_match` returns the end, not the length | test-compound FAIL, 32 FAIL lines |
| S1077 | locate-then-finish | the body reads `<p>_search`'s linkage, not its own row's | §2.2 |
| S1078 | the table's column | `entry_rows[]` names finish-at for the DFA `_match_in` | every DFA compile refuses: "internal error: entry match_in's row is `finish-at`, and its engine supplied no text that combinator writes"; §2.2 |

### 2.2 The two figures still running at hand-off

S1077 (compound) and S1078 (codegen) were running at hand-off. The result is in
`build/plant/S1077/cu.log` and `build/plant/S1078/cg.log`, and the handback message carries it.

### 2.3 Re-aims and re-runs (derived, not remembered)

`build/scratch/rerun.py BASE` derives both lists from the edit set. The edit set is
`git diff BASE..HEAD` over `src/`, mapping each row's anchor to its owner definition.
"Both quote styles" holds because each row's SAB_BEFORE is read by sourcing it in bash.

- **Re-aimed, anchor in moved text (4):**
  - **S180:** SAB_FILE `emit_comb.c`, COUNT 3 -> 1. One bind line now serves all three
    `_in` entries, and the plant still swaps all three.
  - **S179** and **S183:** `emit_comb.c`, with BEFORE/AFTER re-derived on the one CALLER
    format. Each plant stays `_search_in`-only through an `s->entry ==
    PCREC_ENTRY_SEARCH` operand, so neither row's population widens.
  - **S190:** SAB_FILE only (the delegate moved verbatim, same column).

  Each row carries a RE-ANCHORED note.
- **Re-run, anchor unchanged in a changed owner (19):**
  - 16 rows in `vm_emit_search_body`, whose prefilter emission now goes through the
    dispatch: S141 S144 S168 S181 S36 S370 S371 S400 S430 S469 S556 S63 S85 S88.
  - 3 rows in `pcrec_emit_compound_search`: S891 S895 S903.

  S164/S184/S41 sit in `vm_plan`. The script lists them, but the only change in `vm_plan`
  is a comment naming `fwd_own`, so they are not re-run. S1008 (`entries.c`'s
  `rk_prefilter`) is untouched.

## 3. The owed heavy chain

`build/v/waiter.sh` was armed detached (`setsid nohup`; its PID is in `build/v/waiter.pid`).
It polls `worktrees/e0c/.lift`, which the manager creates, and then runs `build/v/chain.sh`
once. Each step writes `<step> rc=N` on its own line in `build/v/chain.log`. The steps:

1. `make -j16`, and a reference `build/pcrec` from `git merge-base HEAD main`.
2. `scripts/emit_sweep.py`, fourteen runs (`build/v/sweep-<name>.log`):
   - **full**: every default stream, with self-check;
   - **arms**: the start-family deny arms;
   - **comments**, **simd**, **utfcheck**;
   - **vm**, **deny**, **vmdeny**: e0tri's list;
   - **entry**, **entry2** and **untiered**: `--vm-entry-shape=forward`/`shared` and
     `-fno-tiered-entry`, the forward emitter's three OWN bindings;
   - **emain**: `--emit-main`;
   - **variants**: `--variant all` from `--ref`/`--tree-rev HEAD`;
   - **trace**: the trace stream. Axis G's `dfa_match_of` asks keep their count and order.

   Any non-zero rc is a mover or a floor, and a mover is a finding for the manager.
3. `scripts/perfrun --label e0c -- build/v/test.log`. The verdict is
   `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/v/test.log`, which must be empty.
4. `PROCS=4 run_sabotage_matrix.sh` over the 31 rows of §2.1/§2.3 (`build/v/mech.log`),
   read from its `== mech run COMPLETE` trailer.
5. `build/v/DONE`. The completion line in `chain.log` is `== e0c chain COMPLETE ==`.

## 4. Findings and choices

1. **The `_in` entries were already one shape.** Across both engines the six `_in` texts
   differed only in the binding and in per-entry signature data. With the binding as the
   forward emitter's parameter, they became two formats over one table. The bytes matched
   on the first build, and the anchors (S179/S180/S183) needed re-deriving.
2. **The VM's `_run` bodies (internal `finish-at`/`locate-then-finish` rows) are still
   written by `emit_vm.c`.** They are file-private VM code, so routing them would need a
   callback into `Vm`. The brief scopes E0c to exported entries. The table already states
   their combinators, and E1's layout row reads them from there.
3. **Axis G's form is the FINISH row's action.** `PcrecFinForm` is chosen by the same
   `dfa_match_of` reads in the same order as before. No trace record moves, and the trace
   arm in §3 checks this.
4. **One closure fact carries the per-entry dispatch.** The old nomatch and anchored
   branches wrote `_match` even when only `_match_caps` was requested. The dispatcher writes
   an entry only where the closure keeps it. These are equal because `_match_caps -> _match`
   is an edge on both own forms.
5. **Process.** Light validation ran pinned (`taskset -c 0-7`, `-j4`). Plant trees were
   built under `build/plant/`, and scratch went to `build/scratch/`. Nothing was written
   outside the worktree.

## 5. Not done / for the manager

- `.lift` is the manager's to create.
- The plan row `[ENTRY-TABLE]` is the manager's. Its status should name E0c built on
  `lane/e0c` once the chain is green.
