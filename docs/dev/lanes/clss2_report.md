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

## Review fixes (clss2fix)

Lane clss2fix (opus), 2026-09-30, on `lane/clss2` after merging main
(`9cf941be`: D138, D139, review r3). Work list: the dispositions table of
`docs/dev/reviews/2026-09-30-r3-cls-tree-s2.md`, D138 and D139. One abi
event, numbered on the lane after this lane's 51/52: **abi 52 -> 53**
(`ddfefeb7`; the src tip is `2c45260a`, recursion (B) self-pinned to it in
`bc387736`). The manager renumbers at merge (S-M1: uvbuild first, then clss2
with its "was 50" paragraph).

### What was built

**D139 item 2 — the scan edge has no class decision (E-M2, S-M2).**
`dfa_scans[]`'s three class bodies and `pcrec_scan_range` (and its
`internal.h` declaration) are gone. `emit_dfa.c`'s `scan_choice` asks
`clskit.c`'s `ROWS` for the edge class's form at a new SITE, `CLSS_SCAN`,
priced at `SCAN_TEST_CALLS` = 2 (the guard and the loop each write the test),
and `scan_test` writes the answer through the kit's own emitters, the same
ones the VM's class reads now use:

| emitter (clskit.c) | forms | used by |
|---|---|---|
| `pcrec_clskit_emit_inline` | range (`1` / `b == c` / `b <= hi` / `(unsigned)(b - lo) <= span u`), fold (`(b \| 0x20) == x`) | `vm_cls_test`, `scan_test` |
| `pcrec_clskit_read` | kit call `name(b)`; table read in a representation: 32-byte bitmap, atom matcher, 256-byte scan table `name[b]` | `vm_cls_read`, `scan_test` |
| `pcrec_clskit_emit_kit` | the kit matcher (now takes `cp_max`) | VM byte/wide kits, the edge's file-scope `scankit` |

- **The table representation is a `TAB_ROWS` row.** `TAB_ROWS` and `ROWS`
  rows carry a `sites` mask. `TAB_ROWS` is `atom` (VM only, unchanged),
  **`scan-table`** (scan site: one 256-byte table per edge, `CLST_BYTE256`,
  today's per-context choice kept as the row's predicate), `site`.
- **D138 Q1 at the scan edge.** The fold is two rows: `byte-fold` (-2/-1,
  both sites) and **`byte-fold-default`** (0/+1/+2, VM only). So at the
  default positions the VM keeps its fold byte-identically and a scan
  edge's pair keeps its table, as today. FORM-CHAR2's measurement flips
  both sites with one row: delete it (table everywhere), or add the scan
  site (fold everywhere). tuning.md §2.22 and §2.18 say so.
- **Stamp and listing.** `RX_DFA_SCAN_EDGE` is `pcrec_clskit_test_name` of
  the answer (`range` / `fold` / `kit` / `bitmap`, plus the composites);
  `"fold"` is new, -2/-1 only. `--list-axes`' `scan-body` rows are read off
  `ROWS` (`pcrec_clskit_byte_tests`), not restated.
- **One flags -> deny mapping.** `pcrec_clskit_deny_of` (a `DENY_FLAG`
  table) and `pcrec_clskit_tabdeny_of`, used by `vm_cls`, `vm_wcls`,
  `vm_cls_tables` and `scan_choice` (D139 item 3: a row's flag denies it
  wherever the table is read).
- **E-M2 witness.** `(?i)xa{3,}b` at `--tune=-2`, default route, gcc-16 -O2
  `__text`+`__TEXT,__const`: 2,642 -> 2,158 B (-484). The edge now stamps
  `"fold"` where it read the 256-byte table.

**Spelling unification (D139 item 2's "one spelling serves both"), measured
before committing.** The VM's `(unsigned)(b - lo) <= span u` and the scan
edge's `(unsigned char)(b - lo) <= span` compile the same. The unified
spelling keeps the tighter form of each case: `1` for all 256 (the scan
edge wrote `b <= 255`), `b <= hi` from 0 (the VM wrote a subtract of 0),
and the VM's type-general subtract otherwise (the `unsigned char` cast is
only exact for a byte-typed operand).

Default movers, emit sweep, lane base `9cf941be` vs the change, every
distinct corpus `pattern` line with `--features all`:

| route | same | refuse | movers | what moved |
|---|---|---|---|---|
| default | 3,052 | 406 | **79** | every mover is the scan edge's subtract range spelling, and nothing else |
| `--engine=vm` | 3,130 | 406 | **1** | a VM range from 0 now reads `b <= N` |

79 of 3,131 compiling default artifacts is 2.5% (under 5% of the 1,683
DFA-engine ones), not a large share, so it was committed. Unifying the
other way (the `unsigned char` spelling) would have moved 119 VM artifacts.
Answers are identical by construction and by the checks below.

**D139 item 1 — `byte-kit` only where smaller (E-M3).** The row's predicate
is `P_KIT_SMALLER`, `P_P3_SMALLER`'s shape:
`calls x kit_sel_bytes < table.rodata + calls x table.read_text`.
- The table is the one the site reads for a lone set (`lone_table`, via
  `TAB_ROWS`): a 32 B bitmap on the VM, the 256 B table on a scan edge.
  `TABLE_COST` holds the measured standalone costs: bitmap read text 32 B,
  256-table read text 16 B.
- `calls` is the number of times the test is written, since a kit is
  inlined at each: the VM counts its bitmap reads in the finished program
  (`vm_cls_reads`, re-asked in `vm_cls_tables`), and the scan edge uses 2.
- **The dispatch term is per domain.** `PLACE.kit_disp_bytes` (578) was
  fitted on the K53 wide sets. Refitted the same way (standalone matchers,
  gcc-16 -O2) on the 41 corpus byte classes, measured minus model is mean
  -0.3 B, range -28..+26, so `kit_disp_bytes_byte` = 0. With 578, every
  byte kit would price above every byte table, and the row would retire by
  arithmetic, not by measurement.
- The dead bound is gone. `emit_bound` skips the bound when the set spans
  `0..cp_max`, and a byte kit passes `cp_max` 0xFF (that is exactly the
  `(unsigned)(cp - 0u) > 255u` line).

The review's five witnesses, re-measured (`--tune=-2`, gcc-16 -O2,
`__text`+`__TEXT,__const`, bytes; "old" is the lane base, "deny" is
`-fno-cls-kit`):

| witness | route | old | new | deny |
|---|---|---|---|---|
| `x[^\n\r]{30}y` | default | 3,008 | 3,008 | 2,944 |
| `x[^\n\r]{30}y` | VM | 1,064 | 1,064 | 1,000 |
| `[^"\\]*"` | default | 1,950 | 1,950 | 2,174 |
| `[^"\\]*"` | VM | 744 | 744 | 776 |
| `\w+@\w+` | default | 2,440 | 2,440 | 3,048 |
| `\w+@\w+` | VM | 1,460 | 1,460 | 1,108 |
| `[0-9a-fA-F]+z` | default | 1,943 | 1,943 | 2,167 |
| `[0-9a-fA-F]+z` | VM | 884 | 884 | 776 |
| `x[acegikmoq]+y` | default | 1,532 | 1,532 | 1,532 |
| `x[acegikmoq]+y` | VM | 788 | 788 | 852 |

**The fix does not move these five witnesses, and that has to be said
plainly.**
- On the scan edge the model keeps the kit, which is right there: -224,
  -224 and -608 against the 256-byte table.
- On the VM the model predicts the kit smaller on all five, while the
  in-context measurement has it larger on three: +64, +352 and +108.
- The standalone model is accurate: 41/41 byte kits are within 28 B.
  The miss is gcc's in-context code generation around the inlined
  matcher. The pair that shows it: `[0-9a-fA-F]` and `[acegikmoq]` both
  model at 24 B and 1 read, yet one loses 108 B and the other wins 64 B.
- Over the 41 corpus byte classes in one VM shape (`x[C]+y`, 1 read), the
  kit is smaller on 23, larger on 9 and ties on 9. Net, the model's
  choices save 352 B against all-table.
- A threshold fitted to that population (an extra ~19 B) saves more
  (-800 B), but it splits two sectionings whose models differ by 2 B, which
  is overfitting.

The literal reading of D139 (`kit_sel_bytes` with 578 on byte sets) was
raised with the manager at the start, with this data. It would turn the
kit off on both sites: it fixes the three VM regressions and gives up the
scan edge's 224-608 B wins. It is one PLACE cell, and the report does not
choose it.

### Review items

| # | disposition | evidence |
|---|---|---|
| E-M3 | FIXED as above; the witnesses' VM residual is reported, not hidden | table above |
| E-M2 | FIXED: the scan edge maps nothing — it reads ROWS | `(?i)xa{3,}b` -484 B at -2; tune-dial §3f; clspack PART 5 `fold` differential |
| E-M1 | FIXED: spec says the row flags deny wherever the table is read | tuning.md §2.22/§2.33, lib/pcrec.h, match_api §6.3 |
| S-M1 | for the manager at merge; this lane's event is 53 | match_api §6 "is 53 / was 52 / was 51" |
| S-M2 | FIXED: tuning.md §2.18 rewritten (four run tests, the table's answer, SIMD reserved as a LOOP form); axes_dump.c descriptions + composite comment; emit_dfa.c axis I header and `scan_edge_of` comment | — |
| C-M1 | owed: the `make test-axes` run below | chain log |
| C-M2 | the manager's (Linux) | — |
| C-M3 | owed: the corpus under `RXTFLAGS=--tune=-2` and `-1` below | chain log |
| C-M4 | report wording only; nothing to build | — |
| C-M5 | owed: `cls_identity.py --ref 92f4c9b7 --control` on this tree below | chain log |
| V-1 | FIXED: `axes_registry_check` coverage pin 155 -> 158 (S2's `kit` row: one more deny triple, the pin never moved) -> 161 (the `fold` row's `-fno-cls-fold` triple) | `axes_registry_check.sh` 161/0 |
| C-L6 | FIXED: S431's reach probe paired (`KIT-ON ... 1` / `KIT-OFF ... 0`); PART 4 widened to `-1`, a caseless class, a hi=0xFF class, `-e utf8` byte and wide classes; PART 5 to `-1`, `-e utf8`, a fold-vs-deny differential and, via the driver's new opt-in `-DDIFF_MATCH`, the MATCH entry (the anchored machine, which `_search` never runs) with a reach check that the witness carries kit edges on its reverse and anchored machines | clspack below |
| C-L8 | FIXED: tune-dial §3e recognizes each form by its own spelling (kit / bitmap / fold / range; anything else fails); + a kit-larger case, a fold-denied case; new §3f for the scan edge (stamp AND text per position) | tune-dial below |
| S-L3 | FIXED: every live `vm_cls_shape` reference (lib/pcrec.h, run_recursion_identity.sh's failure message and comment, run_cls_fold_agreement.sh, fold_pairs_dump.c, run_codegen_tests.sh, tests/codegen/CLAUDE.md, S275) now names `is_ascii_fold_pair` / `pcrec_clskit_emit_inline`; historical "before abi 51" mentions stay | `git grep vm_cls_shape` |
| S-L4 | FIXED: tuning.md §2.22 and the plan row point at D138 | — |
| E-L1/E-L3 | not in scope (file as `[CLS-ONE-TABLE]`); note that D139 retires one of E-L1's "two deny paths for the DFA kit" | — |

**Sabotage anchors (by grep).** Eight rows went stale and were re-anchored
with intent unchanged, each with a note: S275 (the fold spelling moved to
clskit.c), S364 (the per-domain `kit_sel_bytes`), S393 (vm_wcls' select
input), S401/S406 (the tab deny moved to `pcrec_clskit_tabdeny_of`), S430
(`cp_max`), S431 (`DENY_FLAG`; now reaches both sites) and S432 (the row's
new shape). `scripts/m6read_check_sab_anchors.py`: 378 rows / 394 sites,
all resolve. **New rows S433-S436:**
- S433: the scan site is ignored (tunedial);
- S434: the one range spelling drops its top byte, both engines (harness,
  `tests/base/d27_captures.rxt`);
- S435: the kit's call count is ignored (clskit);
- S436: the kit bound is dropped wherever a set reaches 0xFF (clspack's
  new `hi255` witness).

### Spec hunks (D80) and abi readers (D94, found by grep)

Spec hunks:
- `docs/spec/tuning.md`: §2.18 (the edge's run test is the class table's
  answer; four candidates; the D138 Q1 default; SIMD reserved as a LOOP
  form), §2.22 (the fold rows at both sites; the default HELD per D138 Q1,
  with Q3 pointing at D138; "wherever the table is read"), §2.33 (byte-kit
  only where smaller, the per-domain dispatch term, the bound; the scan edge
  row), §5.4 λ row.
- `docs/spec/match_api.md`: §6 "is 53", §6.3 `RX_DFA_SCAN_EDGE` (six
  values, `"fold"` new, the range spelling), `_VM_CLS_FOLDS` / `_VM_CLS_KIT`
  scope.
- `docs/spec/registry.md` §6: 106 rows / 37 axes, re-derived; the line was
  stale by `cls-kit` and `cls-pack`.
- `lib/pcrec.h`: `-fno-cls-fold` / `-fno-cls-kit` docs.
- `docs/spec/cli.md` needed no change: no flag was added or removed (D138
  Q3 (a) keeps `-fno-cls-fold`).

abi readers, found by `git grep` for the digit:
- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`;
- `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` and its transition
  message;
- `match_api.md` §6;
- `run_recursion_identity.sh` FILEPIN, re-pinned to `2c45260a`.

(A) moved on ONE pattern: `[\0-\7]` on `--engine=vm` (the range-from-0
spelling). That gate now admits D139's one-spelling rewrite MECHANICALLY
(`cls_range0_rewrite`, the [VAR] M6 rename's shape: the pre-module region
rewritten with the one substitution, then compared again), with its own
counter in the summary line. Every other reader of "the number" is
historical narrative.

### Validation (Mac, gcc-16)

Run during the lane, each named by the file that ran:

| check | result |
|---|---|
| `make strict` | clean |
| `tests/codegen/run_tune_dial.sh` | 113 passed / 0 failed (was 62; §3e rewritten, §3f new) |
| `tests/codegen/run_clspack.sh` | 57 / 0 before the `hi255` witness; PART 4 313,344 cells, PART 5 270,848 search + 270,848 match cells |
| `tests/clskit/crosscheck.py` over `populations.py` + the rebuilt driver's dump | 591 sets, 94,560 selections (5 positions x 8 denies x 2 sites x 2 call counts), 10 rows, 3 ties, **0 disagreements** |
| `tests/registry/axes_registry_check.sh` | 161 passed / 0 failed (the new pin) |
| `scripts/m6read_check_sab_anchors.py` | 378 rows, all anchors resolve |
| emit sweep, default and `--engine=vm`, lane base vs change | 79 / 1 movers, all the one spelling (above) |
| `run_recursion_identity.sh` (first run, before the (A) exception) | (B) default: 2,765 call-free patterns byte-identical against the pin; (A) default and the other labels: pass; (A) `--engine=vm`: the one `[\0-\7]` region, now admitted by the rewrite. Re-run owed in the chain |

**OWED: the detached chain**, `worktrees/clss2fix-scratch/chain.sh`, on
tree `4cf2a5e8`. Summary:
`worktrees/clss2fix-scratch/runs/chain/summary.txt`, one line per step with
make's `*** [` count; the last line is `CHAIN COMPLETE`. Per-step logs sit
beside it. Steps, in order:
1. build, strict;
2. `run_recursion_identity.sh` (the re-pinned gate with the new rewrite);
3. the default and forced-VM emit sweeps (for the record);
4. `make test-tune-dial`, `test-cpset-structure`, `test-registry`,
   `test-rxtsource`, `test-clskit`, `test-codegen` (the accepted darwin
   red is `nm arm_a.o` only);
5. `run_clspack.sh` with the `hi255` witness;
6. mech, solo, one row per run: S433-S436 (new), S430-S432, S228, and the
   re-anchored S275 S364 S393 S400 S401 S403 S406 — the expected verdict
   is DETECTED for every row;
7. `scripts/cls_identity.py --ref-bin <92f4c9b7 built with its abi digit
   set to 53> --bin build/pcrec --control` (C-M5). Both sides now share a
   digit, so control 2 compares like with like. The expected movers are
   S2's 10 wide-class triples plus this lane's range-spelling triples,
   nothing else;
8. the `.rxt` corpus under `RXTFLAGS=--tune=-2` and `--tune=-1`, each on
   the default route and `--engine=vm` (C-M3);
9. `make test-axes AXES="-fno-cls-fold -fno-cls-kit"` (C-M1).

Linux `make test` + `test-codegen` (C-M2) are the manager's.

### Open for the manager

- **D139 item 1's calibration** (sent as a question at the start, no reply
  before the handback). This lane built the per-domain term (byte = 0 by
  measurement) and the per-site table cost. The literal 578 is one PLACE
  cell away (`kit_disp_bytes_byte = 578`); it would turn the byte kit off on
  both sites.
- **D138 Q1's -2/-1 half.** "The kit's CUBES serve all 8 one-cube classes at
  -2/-1" is still built as the fold compare at -2/-1 (`byte-fold`), as the
  clss2 build left it. The fold compare is smaller than a CUBES kit
  function, and D139 did not revisit it. Removing `byte-fold`'s -2/-1
  positions sends the pairs to `byte-kit`, where smaller. That is one row
  edit, if wanted.
