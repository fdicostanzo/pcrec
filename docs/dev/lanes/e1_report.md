# Lane e1 report — [ENTRY-TABLE] E1, the part-layout controls (2026-10-18)

Lane `e1` (opus), branch `lane/e1` from main `c88537116`. Charter:
`docs/design/compound_entries.md` rev 4 §5.1's E1 row, D163 addenda 7-12,
Frank's build GO of 2026-10-17. abi 79 -> 80 (the manager's D94 reading: the
stamp vocabulary is emitted scaffolding).

**Status at handback: built, committed, validated where noted.** OWED items
are marked OWED with their log path; see §8.

## 1. What was built, against the E1 row

| E1 row item | built as | where |
|---|---|---|
| `part_layout.def` | four X-macro families (`PL_CLASS`, `PL_VALUE`, `PL_RANK`, `PL_WHY`), each row a `lib/pcrec.h` constant as a token; every reader derives from it (CLI parsers, `--list-axes` section, stamp and listing writers) | `src/core/part_layout.def` |
| the three `pcrec_options` fields | `part_layout` (`uint32_t`, 2-bit slot per class, `PCREC_PART_LAYOUT_GET`/`_SET`), `part_inline_rank`, `part_residual`, appended; enums `PCREC_PART_*`, `PCREC_PART_RANK_*`; 0 = unset everywhere; out-of-set values refuse | `lib/pcrec.h`, `src/core/compile.c` |
| their CLI spellings | `--part-layout=CLASS:V[,CLASS:V...]`, `--part-inline-rank=R`, `--part-residual=V`; later value wins; per-class slots, so a config's raw `pcrec` line is file-wins PER CLASS with no code of its own | `cli/main.c` |
| §3.4's artifact table | `art_rows[]`: K `resolve` (always), first match of T1 `rank-unmeasured` / TM `rank-measured` / T2 `rank-none`, first match of T0 `as-emitted` / T3 `per-part`; every conjunct listed | `src/gen/part_layout.c` |
| part table P1-P10 | `part_rows[]`, first match per part, P1-P3 (owned, not-copyable, single-caller) ahead of the control rows, total (P10) | same |
| wrapper table W1-W2 | `wrap_rows[]` (`forward` / `adapt`), listed; the walk counts forwarding callers of a shared part (population zero before I3) | same |
| read by `entry_rows[]` | each part's `callers` and rank are read off the entry table's DERIVED edges (`pcrec_entry_shape` copies them into `Job.pl.er`), owned always_inline callers folded (`Job.pl.owned_inline`, set after `vm_plan_entry`) | `src/gen/entries.c`, `emit_vm.c` |
| rendered after every length decision (I5) | under T3 each subject's search head carries a MARK after `static `, the prologue a stamp mark after `<PREFIX>_TUNE`; both decision views subtract the marks' bytes (`StrBuf.layout_bytes`), splices carry them; `pcrec_part_layout_render` runs after the caps and their notes, before the prefix render | `src/core/sb.c`, `src/gen/emit_dfa.c`, `src/core/compile.c` |
| TUNE_TABLE columns, every layout cell `†` | three columns, every cell 0; the intended policies (D163 add. 8/10) recorded in a comment and in tuning.md §5.4's why column | `src/core/tune.c` |
| the stamps | `<PREFIX>_PART_LAYOUT` (T3 only; `residual=V;rank=R[@set];CLASS=V[/held|/none]`), `<PREFIX>_PART_LAYOUT_WHY` (T1/T2 only); pattern-level on a compound; a part writes neither | `src/gen/part_layout.c`, `stamp_kinds.c` |
| the `--list-axes` section | `#section part-layout` (one row per control value) and `#section part-layout-table` (every table row and its conjuncts) | `src/dump/axes_dump.c` |
| the `--emit-facts` section | `part-layout-controls` (resolved controls, rows fired, WHY) and `part-layout` (one row per subject and owned entry-table function) | `src/dump/facts_dump.c` |
| explicit controls LIVE | yes, from E1 | — |
| every preset resolves to T0 | yes; checked against the SPEC's §5.4 cells (tests/partlayout §1, fixture `preset-empty`, sabotage S1116) | — |
| §3.6 checks | §4 below | `tests/partlayout/`, `tests/axes/run_axes.sh` |
| D80 hunks of §3.9 | tuning.md §2.51-§2.53 (new), §4 mirror rows, §5.3¶3, §5.4 rows; match_api.md §6.3.11¶4, §6.3.12, §8.2; cli.md §1.1.4¶5a, §1.14¶3, §2.4, §2.11; registry.md §6¶2, ¶10, ¶11, §10; facts_listing.md §3¶3, §4.3, §4.4 | `docs/spec/` |
| D94 reader grep | §2 | — |

D163 addendum 12 holds by construction: a row writes an attribute on a static
part's definition and nothing else; no row adds a call, so no control can
create an exported-to-exported edge. The render refuses a mark that does not
follow `static `.

## 2. abi 79 -> 80: the readers found by grep

`grep` of the tree for the number's readers (excluding history/journal/
review prose that records past events):

| reader | change |
|---|---|
| `src/gen/emit_dfa.c:54` `PCREC_ARTIFACT_ABI` | 79 -> 80 |
| match_api.md §1¶7's K80 block: the `#if ... != 79` guard | 80 |
| the same block's `#error "... (abi 79) ..."` | 80 |
| the same block's `#define PCREC_RX_ABI_H 79` | 80 |
| match_api.md §6¶1's `rx_info` table, row 1 (`79`) | 80 |
| match_api.md §6¶17 ("It is `79`...") | 80 |
| `tests/codegen/run_codegen_tests.sh:3149` `ABI_EXPECT` and its transition message | 80, message gains the 79->80 clause |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` | re-aimed: BEFORE 80, AFTER 79 |
| `docs/dev/history/abi_changelog.md` | new current-value paragraph |
| `tests/codegen/run_recursion_identity.sh` (B) FILEPIN | self-pin `fc67299b5` (the lane's last src commit; the manager re-pins to the merge) |

Not changed, deliberately: `memfn/docs/wake.md:26` says "pcrec abi is 79" —
the kit's own status note, not a reader, and not this lane's file. The digit
is the same length, so no byte-count manifest moves. `make test-codegen` at
abi 80: 16/16 scripts green (`build/e1s/test-codegen2.log`).

## 3. Zero default movers

The proof is `scripts/emit_sweep.py` against main `c88537116` run on COMMIT
A, `09d7c35be` — every E1 code change at abi 79, so a byte-identical result
is a statement that no default byte moved; commit B (`fc67299b5`) then moves
the abi digits alone. Two runs (streams c-default, c-vm, emit-ir,
composition, emit-ir-auto, stderr; `--jobs 8`, taskset 0-7):

| run | command | result |
|---|---|---|
| no control | `emit_sweep.py --ref c88537116 --bin <commit A pcrec>` (self-check on: PASSED, all-identical at full reach) | **rc 0, 0 movers / 0 asymmetric on every stream**; argv 5,790 rows (`--every 1`), composition 37 producing / 106 artifacts; 102 s. `build/e1s/sweep-default.log` |
| all-`auto` control set | `--ref-bin <c88537116 pcrec> --bin <wrapper prepending --part-layout=prefilter:auto,compound:auto,find:auto,wrap:auto --part-residual=auto --part-inline-rank=none>` | **rc 0, 0 movers / 0 asymmetric on every stream**, same reach; 46 s. `build/e1s/sweep-allauto.log` |

Slot GO main 05:25:32, released 05:32:47 (`build/e1s/sweepchain.log`).
**The swept binary was a copy, as the slot's condition asks**:
`build/e1s/binA/pcrec`, copied at 05:25:17 from commit A's build (it prints
`abi 79`); `build/pcrec` was rebuilt at abi 80 only afterwards and was never
the `--bin`. Streams: c-default, c-vm, emit-ir(-vm), the four emit-ir-auto
arms, stderr, composition.

The `dumps` and `facts` streams are excluded because E1 APPENDS to both by
design; each was checked as a pure append instead: the seven `--list-*`
surfaces against main's binary — six byte-identical, `--list-axes` differs by
50 added lines at its end and 0 removed; `--emit-facts=byte,utf8` over 60
random corpus patterns — every listing's text up to the new
`#section part-layout-controls` is main's byte for byte (60/60).
tests/partlayout §6 also holds the all-`auto` set byte-identical to no
control on 397 artifacts (the population and the near-cap list).

## 4. The §3.6 checks

`make test-partlayout` (`tests/partlayout/run_partlayout_tests.sh`): **45
checks, 0 failed, ~25 s** at HEAD. Each sabotage row was HAND-VALIDATED (a
`git archive` copy of the tree, the plant applied by
`tests/mech/lib/replace.py`, rebuilt, the suite run against it; clean
baseline 41/0 at the time); the solo mech runs are OWED (§8).

| §3.6 check | where | sabotage | hand result |
|---|---|---|---|
| `0` byte-identical (emit_sweep vs pre-E1 main; and the all-auto set) | §3 above; tests/partlayout §6 (all-auto vs no control) | — | see §3 |
| layout read from the OBJECT vs an evaluator sharing no code with the tables | §1, `evaluator.py`: attribute-stripped `-O0 -fno-inline` call graph (call targets and relocations), owners' attributes from the default text, copyability asked of GCC (its own "can never be copied/inlined"), hand class/rank maps (`witnesses.tsv`), presets from the SPEC; judged on `nm` | S1113 (shared writes the inline text), S1114 (callers unfolded), S1117 (P7 above P4-P6) | 7/34, 21/20, 6/35 |
| rank fixture as a precondition | E0's `tests/compound/entry_ranks.tsv` (R0-R3 all witnessed) + the hand ranks of `witnesses.tsv` | E0's S1008 | (E0's) |
| corpus first, synthetic only where no subject | all 9 witnesses are corpus patterns; R3 prefilters exist (`(a+)bcd`, `(?>a*)a`); no copyable R1 part or copyable multi-caller compound part exists, so those rows have no subject and no synthetic witness was needed | — | — |
| preset resolution (every `†` resolves to T0) | §1 (all five `--tune` positions per witness, cells read from tuning.md §5.4) + fixture `preset-empty` | S1116 (a +2 cell leaks) | 10/31 |
| precedence | §2 `fixtures.tsv` (hand-written rows): explicit beats preset, class beats threshold, threshold beats residual, constraints beat everything, later item wins | S1117 | 6/35 |
| held requests reported | §2 (`compound=inline/held`, `prefilter=inline/held`, `wrap=shared/none`, ...) | S1118 (`/held` dropped) | 9/32 |
| H1/H2 by construction | §4: GCC refuses always_inline on the attempt route's label table ("can never be copied") and on a framed computed-goto body ("can never be inlined") | S1112 (P2 dropped: the artifact stops compiling) | 5/36 |
| LK-9 (an exported callee) | the render's internal error (a mark not after `static `) + §3's text check (every changed head is a `static` subject) | — | see deviation 3 |
| clones | §1 (no `.constprop`/`.isra`/`.part` symbol of a shared part) | none (the `noclone` is K24's, A3) | — |
| A1 disjointness | §3: at all five entry rungs, the heads a control changes are subjects only | none | — |
| the seam is copyable | §5: seam bodies under byte and utf8 carry no label table or computed goto | none | — |
| stamp neutrality | §6: every `#define <PREFIX>_*` but `_TUNE`/`_PART_LAYOUT*` unmoved under four controls over 397 artifacts | (S1115 covers the size half) | — |
| answer identity | `tests/axes/run_axes.sh` part-layout arm: default tier `--part-residual=shared`/`=inline`; `AXES_FULL=1` each class value (one run over all four classes) and each rank; values read from `--list-axes` | — | OWED (§8) |
| length neutrality on near-cap witnesses | §6 over `nearcap.txt` (the 10 largest corpus hybrids, 45-647 KB) and the population: refusal, stamps and the decision sizes `--warn-emit-bytes` reports are the no-control compile's | S1115 (the marks reach the decision) | 1/40 |
| the decline is visible | §1 + fixtures `measured-alone`, `measured-with-class` | S1111 (T1 never fires) | 11/30 |
| the attribute census | §5 over population x 9 settings against `writers.tsv` (A1-A7 + the layout table) | none | — |
| totality and population per row | §5: one record per subject; per-row totals with floors (T0 828, P2 658, P3 1379, P4-P6 123, P7 182, P8 123, P9 123, P10 64 measured; floors about half) | — | — |

## 5. make strict, make test

- `make strict`: green (whole tree, -Werror -Wshadow).
- Sections run at this tip: test-codegen (16/16, abi 80), test-registry,
  test-cli, test-compound, test-core, test-ci-shards, test-partlayout,
  limits_check: green.
- `make test`: OWED (§8).

## 6. Deviations from the design, with reasons

1. **Row TM `rank-measured` added** to the artifact table's measured group:
   the design gives `measured` two declines (T1, T2) and leaves its success
   (θ_hot a rank) implicit. Unreachable today, listed and stated so.
2. **P2/P4/P8 write `noinline` alone.** Every subject's head already carries
   K24's guarded `__attribute__((noclone))` (A3), so `noclone` is present
   without a second spelling; §1's clone check holds it.
3. **LK-9's GCC detector does not exist.** GCC 15.2 compiles `inline
   __attribute__((always_inline))` on an EXPORTED callee under `-fPIC`
   without a diagnostic (a C99 inline definition; only the `inline`-less
   spelling warns). The render refuses a mark not after `static `, and §3
   checks the text.
4. **`emit_search_head` (and the DFA engine emitters) take the entry row
   instead of a storage string**, so the head writes the mark itself;
   S1077's anchor re-aimed with the same plant. TUNE_TABLE's rows gained
   three cells, so S249/S250/S251 were re-aimed (anchors carry `, 0, 0, 0`).
   S700's anchor line in `sb.c` was kept by adding the subtraction on its
   own line.
5. **The listing records owned functions only where the entry table has a
   row** (the three `_run` bodies). A1's other helpers, `_deep` and the seam
   are owned too, never marked, and covered by the attribute census.
6. **θ_hot is a stub answering ABSENT** (`theta_hot` in part_layout.c): no
   shipped compile carries a measurement set ([MEASURE-SET] M0); the
   harness lever's set is the kit's. TM and T2 are UNREACHED and the suite
   says so.
7. **A compound part names its shell row** through a new
   `PcrecEmitIn.part_entry`, and carries `copyable`/`layout_bytes` in
   `PcrecPartFacts`.
8. **`(?=a)z`-class empty-language hybrids are not witnesses**: their
   prefilter is `return 0;`, and GCC's interprocedural constant
   propagation deletes it and its calls whatever the attribute (`noinline`
   does not stop it). Recorded in `witnesses.tsv`; see question 1.
9. **No sabotage row for clones, A1 disjointness, the seam or the census**:
   eight ids were allocated and went to the rows above. Asking main if more
   are wanted (question 4).

## 7. Open questions, each with a recommendation

1. **`shared` as `noinline` vs `noipa`.** `noinline noclone` (the design's
   spelling) still lets GCC propagate a constant return and delete the part
   (`((?=a)z)`). `noipa` would pin a body in every case but also blocks
   pure/const inference and return-value propagation on every shared part.
   **Recommend keeping `noinline`** (no measured cost, the deleted case is a
   part with no work), and stating in tuning.md §2.51 that a part GCC
   proves constant may have no body.
2. **D163 addendum 10 vs `auto`/unset under an explicit control.** Add. 10
   says that under any explicit control every part is pinned with explicit
   attributes; the design's P3/P6/P10 leave a part at its default layout
   (GCC deciding). With the presets all `†`, an explicit
   `--part-inline-rank=R2` leaves a below-threshold part to P10. **Recommend
   keeping the rows as built** (`auto` is the zero-mover control value the
   brief requires) and taking add. 10's pinning at E1′ through the PRESETS
   (`+1` residual `shared` per add. 10), not through the rows.
3. **TM/T2 need a set row.** Nothing to do until [MEASURE-SET] M0 gives a
   compile a measurement set with a derived θ_hot. **Recommend** the M0
   brief name `theta_hot` as its first pcrec-read derived row so TM/T2 get
   witnesses.
4. **Sabotage coverage.** S1111-S1118 are used. **Recommend** three more
   ids (S1119-S1121) only if wanted, for the clone count (drop K24's
   noclone on a shared head), A1 disjointness (let `subject_class` name
   `_search_run`) and an unlisted writer.
5. **CI weight of test-partlayout** is ESTIMATED (60 s) in
   `tests/ci/shards.tsv`; **recommend** re-measuring at the next
   `shard_rebalance.py` pass.

## 8. Owed, with logs

| item | log | completion line |
|---|---|---|
| emit_sweep, no control | `worktrees/e1/build/e1s/sweep-default.log` | `build/e1s/sweepchain.log`: `default sweep rc=` |
| emit_sweep, all-auto | `worktrees/e1/build/e1s/sweep-allauto.log` | `all-auto sweep rc=`, then `== sweep chain COMPLETE` |
| make test | (slot requested) | — |
| mech solo S1111-S1118, S1077, S249, S250, S251, S700, S693 | (slot requested) | — |
| test-axes part-layout arm | (slot requested) | — |
| `.o` size delta on the near-cap list (recorded, not gated) | NOT RUN: the script is written (`build/e1s/osize.py`, scratch) but its -O2 compiles of 45-647 KB artifacts would have shared the box with the slot's runs; left for E1′, whose cells need size measurements anyway | — |

## 9. For a fresh agent resuming

Commits on lane/e1: `d37f4ab58` mechanism, `ba636a0a8` spec hunks + re-aims,
`c36f410b7` tests/partlayout + mech arm + S1111-S1118, `09d7c35be` axes arm
(COMMIT A, the zero-mover proof's binary), `fc67299b5` abi 80, the (B)
self-pin, then docs. The suite is `make test-partlayout`; a hand sabotage
driver is `build/e1s/handsab.sh ROW` (scratch, not committed).
