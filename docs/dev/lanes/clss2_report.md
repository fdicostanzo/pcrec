# clss2 report: [CLS-TREE] S2, the byte tier (2026-09-30, lane clss2, opus)

Branch `lane/clss2` from main `92f4c9b7`. This is the row's last step, as
D131 item 5 re-scoped it: **the kit's byte forms are a SIZE-leaning `--tune`
position only, and the default byte-class form stays a table.** It is two
abi events in two commits. On the lane they are numbered 49 -> 51 -> 52,
after lane uvbuild's 50; the manager renumbers at merge.

The manager ruled Q1-Q4 in `worktrees/clss2/clss2_rulings.md`, then reopened
them for Frank. Q1 (the fold's default) and Q3 (retiring `-fno-cls-fold`) are
**HELD and not built**. Q2 and Q4 touch no default byte-class artifact, and
both are built. See §7.

## 1. What was built

### Commit `22d150a8`: the VM byte tier (abi 49 -> 51)

The VM's per-class shape classifier `vm_cls_shape` is retired. The kit's
class-form table (`src/gen/clskit.c` `ROWS`) now chooses each byte class's
test. It is one first-match table, and it gained four BYTE rows:

| row | positions | predicate | the VM emits | deny |
|---|---|---|---|---|
| `byte-range` | all five | one interval, every member <= 0xFF | the inline compare, as before (`1` / `==` / the unsigned-subtract range) | none |
| `byte-fold` | all five | an ASCII case pair {X, x} (`is_ascii_fold_pair`) | the [FORM-CHAR] fold compare `(b \| 0x20) == lower`, as before | `CLSD_BYTE_FOLD` = `-fno-cls-fold` |
| `byte-kit` | -2, -1 | a byte set | `<prefix>_class_kit<N>(b)`, a `static inline` kit `K` matcher | `CLSD_BYTE_KIT` = `-fno-cls-kit` |
| `byte-table` | all five | a byte set | a table read: the class's own bitmap, or the shared atom table | — |

- **The artifact-level table choice is unchanged.** `vm_cls_tables` still
  runs `TAB_ROWS` over every class that is not on an inline row. When the
  atom row fires, every such class reads the atom table at every position
  (clsfit's proposed -2/-1 order: the atom table first, then the kit). When
  it does not fire, a `byte-kit` class is re-spelled to its kit matcher, and
  a `byte-table` class keeps its bitmap.
- **The re-spelling generalises `vm_cls_respell`.** `VmClsRead` gives each
  class its final spelling (inline, bitmap, atom or kit). The program is
  still written in the bitmap spelling and re-spelled after `vm_plan_entry`,
  so the entry rung is decided on the same text as before (S405's
  invariant).
- **`RX_VM_CLS_KIT` counts byte-class kit matchers as well as wide ones.**
  It is one kit-activity stamp. `RX_VM_CLS_FOLDS` is kept for now (Q3 is
  held), and it now counts the `byte-fold` row.
- **`byte-table` lists every position**, so a denied `byte-kit` at -2/-1
  falls to a table rather than to a code-point row. `byte-fold` also lists
  every position while Q1 is held. At -2/-1 it takes the fold compare
  unchanged, because the kit's CUBES spelling is larger there: a function
  plus a bound check.
- **Wide classes pass through the same table.** `vm_wcls` passes deny 0 as
  before. A wide set with one interval at or below U+00FF now takes
  `byte-range`, which is one compare after the decode, where it used to
  take a `B1` table. That is the only default-position mover (§3).

### Commit `979b0b62`: the scan edge's axis-I kit body (abi 51 -> 52)

This is D131 item 5's "re-point the scan-edge axis-I class bodies", as its
own commit and abi event.

- `dfa_scans` gains a third object, `kit`, placed between `range` and
  `bitmap`. It applies where the edge's class, read off the machine's class
  map, lands on the `byte-kit` row, so at -2/-1 only.
- Its test is `<prefix>_<machine>_scankit<head>(peek)`. The matcher is
  emitted at FILE scope through a new `DfaScan.emit_defs` hook. That hook is
  called beside each machine's accessor block (`emit_scan_defs`: forward,
  reverse, anchored), because `emit_tables` writes inside the search
  function, where a function cannot be declared.
- `-fno-cls-kit` is the object's own D82 `deny`. Denied, the edge keeps its
  loop and falls to `bitmap`.
- `RX_DFA_SCAN_EDGE` gains the value `"kit"`. `--list-axes` lists the
  candidate, and the two composite rows are renumbered to 4 and 5.
- A VM hybrid's inlined prefilter gets the same body through the shared
  emitter.

### Readers of the abi number (D94, found by grep, each event)

1. `src/gen/emit_dfa.c:51` `PCREC_ARTIFACT_ABI`.
2. `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` and its transition
   message.
3. `docs/spec/match_api.md` §6's "is `N` today" paragraph. The previous
   entry becomes "was".
4. `tests/codegen/run_recursion_identity.sh` comparison (B) `FILEPIN`,
   self-pinned to `22d150a8` and then to `979b0b62`, in follow-up commits
   `9ff80d8d` and `98deee54`.

A grep over `src lib cli tests docs/spec Makefile` for the old digit finds
no other reader of the current value. The remaining hits are historical
narrative such as "pre-abi-49 retry", and they stay. No manifest pins an
artifact byte count that these events move. The digit keeps the same length,
and default stamp values are unchanged. `run_cpset_structure.sh`'s CHECK 3
rows are re-verified by `make test-cpset-structure` (§5).

## 2. Spec hunks (D80)

- `docs/spec/tuning.md`:
  - §2.22 `-fno-cls-fold`: the recognizer is now the `byte-fold` row. The
    section also covers what the deny falls to at each position and that Q1
    is open.
  - §2.33 `-fno-cls-kit`: the byte tier and the scan edge are added, the
    stamp is widened, and "Denied" now covers both.
  - §5.4 λ row: the byte-class forms per position.
- `docs/spec/match_api.md`:
  - §6: the abi 51 and 52 entries.
  - §6.3: `_VM_CLS_FOLDS`'s derivation, `_VM_CLS_KIT`'s IFF (both matcher
    families), and `_DFA_SCAN_EDGE`'s `"kit"` row (five values).
- `cli.md` and `registry.md` are unchanged. No flag was added or removed,
  because Q3 is held.

## 3. Identity and movers

- **Default position, `scripts/cls_identity.py --ref 92f4c9b7`**, over
  16,009 triples on the byte and utf8 axes:
  - Commit 1, before the abi bump: 13,832 identical, 2,167 both refuse,
    **10 movers**. All ten are utf8 wide classes whose set is one interval at
    or below U+00FF: `x[\x{e0}-\x{ff}]y`, `([\x80-\x8f])` in a repeat,
    `[\xc2-\xdf](?!...)`, `[a-é]+`, and `x(?=[éè])` (é and è are adjacent).
    Each moved from a `B1` bitmap matcher to one range compare. Example:
    `rx_wcls0_b[4] = {255,...}` plus a load became `return 1` after the
    bound check. The instrument control passed.
  - HEAD `98deee54`, with the abi digit normalized to 49 (`/tmp/clss2_h`):
    **the same 10 movers and nothing else**, 13,832 identical, 2,167 both
    refuse. REACH is 1,582/1,582, and CONTROL 1 passed. CONTROL 2
    (`--control`) read FAIL, but that is an artefact of the normalization,
    not a finding. It builds its perturbed compiler from the tree at abi 52
    and compares it against the digit-normalized abi-49 binary, so every
    byte triple "moves" by the digit (163 of them). It was not run on
    commit 1, and it is owed on a merged tree where both sides share a digit
    (log: `/tmp/clss2_runs/clsid2.log`).
- **Size-leaning positions, `docs/dev/lanes/clss2_tune_sweep.py`**: every
  corpus pattern at `--tune=-2` and `-1`, default route and `--engine=vm`,
  against 92f4c9b7, with the digit normalized. The run is **OWED**, as step
  one of the detached chain2 (§6). Its verdict line is `RESULT: PASS|FAIL`
  in `/tmp/clss2_runs/chain2/tunesweep.log`, and its TSV is written to
  `docs/dev/lanes/clss2_tune_sweep.tsv` in the validation worktree
  `worktrees/clss2v` (copied into the chain2 directory).
- **FORM-CHAR's default `.text` (Q1 evidence)**, ci-256 on the forced VM,
  gcc-16 -O2 Mach-O:

  | build | `__text` | table `.rodata` | `RX_VM_CLS_FOLDS` |
  |---|---|---|---|
  | fold | 65,964 | 0 | 26 |
  | `-fno-cls-fold` | 69,868 | 256 | 0 |

  With the fold denied, the 26 classes are table-read, so the atom row fires
  at >= 11 classes and they share one 256-byte table. The fold therefore
  saves 5.6% of `__text` and 256 B of `.rodata` here. The auto route is a
  DFA artifact, and it is identical either way (2,036 `__text`). This is
  what (A) would give up at default.

## 4. Tests added or changed

- `tests/codegen/run_tune_dial.sh` §3e (+40 checks): the byte class's test
  per position, read off the text (scattered, scattered under
  `-fno-cls-kit`, range, fold), and `RX_VM_CLS_KIT` equals the kit matchers
  the text defines.
- `tests/codegen/run_clspack.sh`:
  - PART 4: the byte-kit answer differential, `--tune=-2` against
    `-fno-cls-kit`, on three witnesses, 199,168 cells, with non-vacuity per
    witness.
  - PART 5: the scan-edge `kit` body. It checks the stamp and matchers per
    position, the deny, and that a range stays `range`, then runs the answer
    differential over DFA artifacts, 151,552 cells.
- `tests/clskit/crosscheck.py`: the row restatement gains `byte-range`,
  `byte-fold`, and `byte-table` at every position. `NDENY` goes from 7 to 8.
- Sabotage rows:
  - Three new: **S430** (the kit matcher built from the neighbouring class's
    set; arm `clspack`), **S431** (`-fno-cls-kit` not reaching the byte
    rows; `tunedial` and `clspack`), **S432** (the byte-kit row at
    position 0; `tunedial` and `clskit`).
  - Re-anchored with intent unchanged: **S228** (to clskit.c's
    `is_ascii_fold_pair`), **S400** (the atom emission moved into the
    per-class switch), and **S403** (the re-spell is now conditional on any
    non-bitmap read).
  - `scripts/m6read_check_sab_anchors.py`: all 374 anchors resolve.

## 5. Validation (Mac, gcc-16)

| check | result |
|---|---|
| `make strict` | clean, both commits |
| `make test-codegen` (commit 1 tree) | 11/12 scripts. The only red is the accepted darwin `nm could not read arm_a.o` (run_inline_capability.sh) |
| `run_tune_dial.sh` | 62/0 |
| `run_clspack.sh` (HEAD) | 42/0 |
| `cls_identity.py --ref 92f4c9b7` (commit 1, and HEAD normalized) | the 10 predicted wide-class movers only (§3) |
| `make test-clskit`, `test-cpset-structure`, `test-registry`, `test-rxtsource`, `test-tune-dial` on commit 1 | chain1, detached, **results OWED** in `/tmp/clss2_runs/chain1/summary.txt` (last line `CHAIN COMPLETE`) |

## 6. Owed

Everything below runs detached (`nohup caffeinate -s`). There is one line
per step in the summary file, and its last line is `CHAIN COMPLETE`. The
verdict is make's `*** [test-X] Error` count, which each summary line
carries.

- **chain1** (`/tmp/clss2_runs/chain1/summary.txt`, tree `9ff80d8d`, commit
  1): `test-codegen` is done (above), then `test-clskit`,
  `test-cpset-structure`, `test-registry`, `test-rxtsource` and
  `test-tune-dial`.
- **chain2** (`/tmp/clss2_runs/chain2/summary.txt`) starts when chain1
  completes, on tree `f024bc5b` = HEAD, in the validation worktree
  `worktrees/clss2v`:
  1. the -2/-1 mover census (§3);
  2. the six suites again on HEAD;
  3. mech rows **S430 S431 S432** and the re-anchored **S228 S400 S403**,
     solo, one row per run. The expected verdict is DETECTED. For S228,
     S400 and S403, a detection rather than an anomaly is also the
     re-anchor proof;
  4. the whole `.rxt` corpus under `RXTFLAGS="--tune=-2"` on the default
     route and under `--engine=vm`. That is the oracle-backed answer check
     at the position the kit fires, standing in for `make test-axes` over
     `--tune`, which runs all four positions and is multi-hour.
- **Not run:** `make test-axes AXES="-fno-cls-kit"`. At the default position
  the flag moves only the atom row, which is already swept. Its S2 meaning
  is at -2/-1, and step 4 plus the PART 4/5 differentials cover that. Run it
  if the manager wants the formal sweep.
- **Linux full `make test`** is the manager's to schedule.
- `worktrees/clss2v` is a detached validation worktree. Remove it after
  chain2 with `git worktree remove`.

## 7. Open questions for Frank (the manager reopened Q1-Q4)

The four questions and the recommendations are in the handback and in
`clss2_rulings.md`. As built:

- **Q1, the fold's default. HELD.** The fold compare stays at every
  position (`byte-fold`, every position). If (A) is ruled, drop `TP_0`,
  `TP_P1` and `TP_P2` from the row's positions. At -2/-1 the pair then
  reaches `byte-kit` and K's CUBES. At the default it reaches a table, which
  is the atom table on ci-256; §3 gives the bytes. It also moves any
  caseless-letter VM artifact. If (B) is ruled, widen the predicate to one
  cube.
- **Q2, `byte-range`. BUILT as recommended.** Its one consequence nobody
  ruled is the 10 wide-class movers in §3: one compare in place of a `B1`
  table, a strict size and speed improvement. The recommendation is to
  accept them. The alternative is to have `vm_wcls` deny the row, which
  would be a special case.
- **Q3, retiring `-fno-cls-fold` and `RX_VM_CLS_FOLDS`. HELD.** Nothing is
  removed. If it is ruled as recommended, three things go:
  - `axes.def`'s row and the `--list-axes` `cls-fold` row;
  - the enumerator, with bit 24 left as a "retired" comment;
  - `CLSD_BYTE_FOLD` and its mapping in `vm_cls`/`scan_kit_choice`.

  Then `RX_VM_CLS_FOLDS` retires into `RX_VM_CLS_KIT`. That is only coherent
  once Q1 moves the fold into the kit.
- **Q4, the scan-edge kit body. BUILT as recommended.**
