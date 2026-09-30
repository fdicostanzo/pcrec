# clspack — [OPT-CLSPACK] built (lane clspack, opus, 2026-09-30)

Branch `lane/clspack` from `lane/s4build` `1c887998`. D131 item 6 as ruled:
"the shared atom table is the default byte-class table from N ≈ 11 live class
sites up (≤ 64 atoms), because it ties the bitmap on time (O-77) and is smaller
there. Per-site bitmaps stay below that N." abi 47 -> 48.

## 0. Read first — four things

1. **The shipped corpus has NO artifact the row fires on.** Over every corpus
   `pattern` line, on the default route and forced `--engine=vm` (6,804
   artifacts, 6,057 compiled at the branch point), the most per-site class
   bitmaps any artifact carries is **6**. So every mover in this delivery is a
   constructed witness (`tests/base/clspack_atoms.rxt`, §3). The census says so
   in its own histogram rather than leaving it implied.
2. **The atom spelling moved the entry rung, and the first build shipped it.**
   The VM's entry-shape AUTO rung compares the program's LENGTH against the
   4,096-byte knee (`vm_plan_entry`). An atom table read
   (`rx_class_atom3(subject[i])`) is shorter source text than a bitmap read
   (`(rx_class_bitmap3[(subject[i]) >> 3] >> ((subject[i]) & 7)) & 1`), so
   re-spelling first let the TABLE FORM decide the RUNG. Measured on
   `atom-reads` (4,621 program bytes): rung `inline`, `__text` 5,368 against
   its bitmap twin's 2,120 (2.5x). Fixed by running the table selection AFTER
   `vm_plan_entry` and recording the compared length in
   `VmEntry.program_bytes`, which `<PREFIX>_VM_PROGRAM_BYTES` now reports. It is
   [EMIT-VERB]'s lesson in a new place: *a text rewrite is neutral only if
   nothing upstream reads that text's length as a decision.* A check arm
   (`run_clspack.sh`, the rung/PROGRAM_BYTES rows) and sabotage S405 pin it.
3. **The brief said "the movers are exactly the N ≥ 11 patterns"; they are,
   PLUS one stamp line on every VM artifact.** `<PREFIX>_VM_CLS_ATOMS` (the
   shared table's atom count, 0 for per-class bitmaps) is unconditional on
   every VM artifact, the D81 VM-only activity family's shape, as S4's
   `VM_CLS_KIT` and S2a's `VM_LIT_RUNS` are. It is there because the house's
   predicate-axis listing (`--list-axes`) names a stamp for every row, and a
   conditional stamp is the shape this tree has twice had to remove checks
   for. With the abi digit and a zero stamp line removed, the PROGRAM/TABLE
   movers are exactly the predicted set, by ID (§4). If the manager prefers
   no stamp, removing it is one line plus the listing row and the manifest
   re-record.
4. **The re-spelling is a text rewrite over the finished program, and that is
   deliberate.** The class pool is discovered by EMITTING the program
   (`vm_plan`'s own header: "the class pool ... discovered by emitting and
   would otherwise need a second, drift-prone analysis to predict"), and the
   atom decision needs the whole pool. So the program is emitted in today's
   bitmap spelling, `vm_cls_test` records each distinct (class, byte
   expression) read, and `vm_cls_respell` replaces exactly those strings,
   both spellings coming from ONE renderer (`vm_cls_read`). An occurrence of
   `(<prefix>_class_bitmap` the list does not explain is an internal error, so
   an unconverted read cannot ship silently. The alternatives were worse: a
   pre-pass predicting the pool is the drift-prone second analysis the tree
   rules out, and re-emitting the program would reset dozens of emission
   counters.

## 1. What was built

| piece | where |
|---|---|
| THE TABLE SELECTION — `TAB_ROWS`, an ARTIFACT-level first-match table: row `atom` (>= `PLACE.atom_min_sites` = 11 table-read byte classes, partition <= `PLACE.atom_max` = 64 atoms; deny `CLSTD_ATOM`), row `site` (always). Both rows list all five `--tune` positions (`positions` is the data a later ruling moves). The atom predicate IS `pcrec_clskit_atoms`, so the emitted table is the one the predicate measured. `pcrec_clskit_select_tables`, `pcrec_clskit_table_rows` (listable, [LIST-TABLES]). | `src/gen/clskit.{c,h}` |
| The placements' citation: 11 from `256 + 8N < 32N` (N > 10.7, cls_tree_design.md §1.7.3 item 3), at no measured time cost (O-77, §1.7 addendum); 64 is the mask width. Both were already `PLACE` cells (S1); now read. | `src/gen/clskit.c` `PLACE` |
| The VM side: `vm_cls_read` (the one renderer of both table-read spellings), `vm_cls_note_read`, `vm_cls_tables` (builds the byte sets of the pool's BITMAP-shaped classes, maps `-fno-cls-pack`, selects), `vm_cls_respell`; table emission writes `<prefix>_class_atoms[256]` + one `static inline <prefix>_class_atom<N>` per class via the kit's `pcrec_clskit_emit_atom_table`/`_atom` (reused, no parallel mechanism); `VmEntry.program_bytes`. | `src/gen/emit_vm.c` |
| `-fno-cls-pack` = `PCREC_NO_CLS_PACK`, bit 38; axes.def row; masked out of `rx_info.flags` (`strategy_denials`); `cls-pack` predicate-axis rows in `--list-axes`. | `lib/pcrec.h`, `src/core/axes.def`, `src/gen/emit_dfa.c`, `src/dump/axes_dump.c` |
| `<PREFIX>_VM_CLS_ATOMS`; abi 47 -> 48 | `src/gen/emit_vm.c`, `src/gen/emit_dfa.c` |
| Spec: `tuning.md` §2.35 (+ the flags table row), `match_api.md` §6 (the abi log) and §6.3 (the stamp) | `docs/spec/` |

The selection's shape follows the brief: the per-set shape choice
(`vm_cls_shape`: ALL/SINGLE/RANGE/FOLD/BITMAP) is unchanged and decides WHICH
classes read a table; the new table decides HOW they read it. `TAB_ROWS` is
not a `ROWS` row because its input is every such class in the artifact —
the clss1b ruling's reason, now built.

## 2. The population

`docs/dev/lanes/clspack_census.py` (committed), run with the branch-point
binary: per-site bitmap histogram, default route `0:2958 1:62 2:8`, forced VM
`0:2417 1:583 2:26 6:3`, nothing at 7..11+. **Zero predicted movers in the
shipped corpus.** D77 reading: the row is ruled (D131), so it is built; its
reach today is the witnesses below and whatever bench/user pattern carries 11
scattered classes (csv/loglines shapes, per the row's filing).

## 3. The witnesses — `tests/base/clspack_atoms.rxt`

Generated by `tests/base/gen_clspack_atoms.py`, every cell python3 `re`
(`verify_rxt.py`: ALL CHECKS PASSED, SKIP=0; harness 79/0):

| block | classes | atoms | row |
|---|---|---|---|
| `atom-11` | 11 scattered (`[aeiou]`, `[bcdfg]`, ...) | 12 | atom (exactly the threshold) |
| `site-10` | 10 | — | site (one short) |
| `atom-reads` | 12 incl. `\b`'s word set, read by a span-loop cursor, a lazy loop, a counted repeat and `\b` | 13 | atom |
| `atom-64` | 11 over 63 bytes with distinct membership codes (`engine vm`) | 64 | atom (the mask width) |
| `atom-65` | 11 over 64 bytes (`engine vm`) | 65 | site |

## 4. Validation

| check | result |
|---|---|
| `make strict CC=gcc-16` | clean (after the last src commit `8407666a`) |
| `tests/codegen/run_clspack.sh` (new, rides `test-cpset-structure`, mech arm `clspack`) | **24/0**: the row off each firing artifact (stamp = an atom count computed from the `-fno-cls-pack` artifact's bitmaps, one table, one matcher per class, no bitmap left, every read a matcher call); the entry rung and `RX_VM_PROGRAM_BYTES` equal the `-fno-cls-pack` build's, with a straddle row proving the arm can fail; both thresholds from the other side; the deny; all five `--tune` positions; the stamp's scope; **343,040-cell answer differential** atom vs `-fno-cls-pack` (every byte 0..255 at every position of every matching subject, span + every capture slot + failure surface, `possdiff_driver.c` shared) |
| `tests/harness/run.sh tests/base/clspack_atoms.rxt` | 79/0 |
| MOVERS BY ID (`clspack_census.py --base <1c887998 build> --cand <tip>`, the abi digit and a zero stamp line normalized away) | **moved 6 = predicted 6** (atom-11, atom-reads, atom-64, each on both routes it compiles as VM on), **0 unpredicted, 0 predicted-but-unmoved, 0 moved without the atom form**, over 6,814 artifacts / 6,067 compiled. The two atom-65 artifacts (>= 11 sites, 65 atoms) correctly did not move. TSV: `docs/dev/lanes/clspack_census.tsv` |
| `test-rxtsource` | **270/0**, 1 RECORD (the standing darwin py3.9 C3 note); census re-pinned 255/4280/31941 -> 256/4285/32020, `C3_PASS` +79, `C3_VERIFIABLE` +79 |
| registry axes coverage | 147 (pin 144 -> 147, `-fno-cls-pack`'s triple) |
| `run_cpset_structure.sh` | 28/0 after re-recording CHECK 3's five VM rows, each exactly +26 (the stamp line; diffed against the branch point at the same `-o` basename: stamp + two same-length abi digits, nothing else) |
| `scripts/m6read_check_sab_anchors.py` | 363 sabotages / 379 anchor sites, all resolve |
| sabotage rows (solo, final tree) | **S400** mask shifted: clspack 4/20, corpus 16/63 — DETECTED. **S401** deny ignored: clspack 4/20 — DETECTED. **S402** threshold `>`: clspack 5/19 — DETECTED. **S403** re-spell skipped: clspack 10/14, corpus 46/33 — DETECTED. **S404** 64-atom cap dropped: clspack 1/23 — DETECTED. **S405** re-spell before the rung: clspack 4/20 — DETECTED. |

### Size table (movers; `gcc-16 -O2 -c`, Mach-O; `docs/dev/lanes/clspack_size.tsv`)

| witness | classes | atoms | form | rung | `__text` | table `.rodata` | segment total |
|---|---|---|---|---|---|---|---|
| atom-11 | 11 | 12 | atom | inline | 2,632 | 256 | 3,752 |
| atom-11 | 11 | — | site | inline | 3,528 | 352 | 4,704 |
| atom-reads | 12 | 13 | atom | plain | 1,928 | 256 | 3,264 |
| atom-reads | 12 | — | site | plain | 2,120 | 384 | 3,600 |
| atom-64 | 11 | 64 | atom | inline | 3,284 | 256 | 5,704 |
| atom-64 | 11 | — | site | inline | 3,528 | 352 | 6,000 |
| chain-16 | 16 | 17 | atom | inline | 3,600 | 256 | 4,800 |
| chain-16 | 16 | — | site | inline | 4,904 | 512 | 6,288 |
| chain-32 | 32 | 44 | atom | plain | 2,216 | 256 | 3,552 |
| chain-32 | 32 | — | site | plain | 2,536 | 1,024 | 4,640 |

The table bytes are the model's (`256` vs `32N`); `__text` is smaller too on
every witness (the per-site shift-and-mask becomes one shift of an immediate),
which matches form0's family-D finding on `.text`. No timing was taken here:
Darwin timing is never citable, and O-77 is the ruled time evidence.

## 5. OWED — the detached chain

`build/chain.sh` in the worktree, launched detached (`nohup caffeinate -s`),
one step at a time, each step's log in `build/chain/<step>.log` and one line
per step in `build/chain/summary.txt`; the last line is `CHAIN COMPLETE`.
Steps: S400-S404 re-measured solo (DONE, figures in §4); `make test-codegen`, `test-registry`,
`test-cpset-structure`, `test-clskit`, `test-vm`, `test-resource`,
`test-anchored-match`, `test-tune-dial` (PROCS=2); `run_recursion_identity.sh`
(the atom table added as the fourth region-moving deny axis, with a stamped
converse; (B) re-pinned to `8407666a`); `scripts/emit_sweep.py --ref 1c887998`;
`scripts/cls_identity.py --ref 1c887998`. What emit_sweep/cls_identity should
read: every VM artifact moves by the stamp line and every artifact by the abi
digit; the census above is the instrument that removes exactly those two and
finds the six. **Full `make test` OWED to the manager.** Status at hand-off is
in the handback message.

## 6. Open questions for the manager / Frank

1. **Should `-fno-cls-kit` also deny the atom row?** D129 Q2 made
   `-fno-cls-kit` "the one kit-level deny — emit today's class forms", and the
   atom table is a kit form. S4 defined `-fno-cls-kit` as the WIDE-class
   route only. This lane gave the atom row its own flag (bit 38, per the brief)
   and did not wire `-fno-cls-kit` to it. clskit.h's old comment predicted the
   `-fno-cls-kit` mapping; it now says the table selection carries its own deny.
2. **The stamp** (§0 item 3): keep or drop.
3. **Spec section number**: this lane wrote `tuning.md` §2.35, since S4 holds
   §2.33 and lane reseed's `-fno-hyb-reseed` section is also numbered §2.33 on
   its branch (a merge-time renumber, presumably to §2.34).
4. **`--tune`**: both rows list all five positions today. §1.7.3 proposed the
   kit's byte forms at `−2`/`−1` below 11 sites; S2 (those forms) is not built,
   so the `site` row answers there.

## 7. Files

- `src/gen/clskit.{c,h}`, `src/gen/emit_vm.c`, `src/gen/emit_dfa.c`,
  `src/dump/axes_dump.c`, `src/core/axes.def`, `lib/pcrec.h`
- `docs/spec/tuning.md`, `docs/spec/match_api.md`
- `tests/base/clspack_atoms.rxt`, `tests/base/gen_clspack_atoms.py`
- `tests/codegen/run_clspack.sh`, `Makefile` (test-cpset-structure)
- `tests/mech/run_sabotage_matrix.sh` (arm `clspack`), `tests/mech/sabotages/S400`-`S405`
- re-pins: `tests/registry/run_registry_tests.sh`,
  `tests/rxtsource/run_rxtsource_tests.sh`,
  `tests/codegen/manifests/m5_stage1_stamps.tsv` + `run_cpset_structure.sh`,
  `tests/codegen/run_recursion_identity.sh`, `tests/codegen/run_codegen_tests.sh` (ABI_EXPECT)
- `docs/dev/lanes/clspack_census.py`, `clspack_census.tsv`, `clspack_size.tsv`
- CLAUDE.md: `src/gen/`, `tests/base/`, `tests/codegen/`, `docs/dev/lanes/`
- `docs/dev/plan.md` [OPT-CLSPACK] -> STATE:started, BUILT PENDING MERGE
