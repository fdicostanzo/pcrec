# Lane e1 report — [ENTRY-TABLE] E1, the part-layout controls (2026-10-18)

Lane `e1` (opus), branch `lane/e1` from main `c88537116`. Charter:
`docs/design/compound_entries.md` rev 4 §5.1's E1 row, D163 addenda 7-12,
Frank's build GO of 2026-10-17. abi 79 -> 80 (the manager's D94 reading: the
stamp vocabulary is emitted scaffolding).

**Status at handback: built, committed, validated.** make strict, the full
make test, the zero-mover sweeps, the test-axes arm and every solo mech row
are green at or before the tip; the one item not run is the `.o` size
record (§8).

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

`make test-partlayout` (`tests/partlayout/run_partlayout_tests.sh`): **46
checks, 0 failed, ~43 s** at HEAD (the 46th is the -Werror leg, added after
the test-axes arm found the `noinline` defect, §5). Each sabotage row was
first hand-validated, then run SOLO by `make mech`'s runner on this box,
twice: at `4ea932a4d` (the 45-check suite, `build/e1s/c2/`) and again after
the `noipa` fix at `a41465e9a` (the 46-check suite, S1113's anchor moved;
`build/e1s/c3/mech_S11xx.log`). All eight DETECTED both times; figures
below are the second run's, `fail/pass` against a clean 0/46.

| §3.6 check | where | sabotage | solo mech |
|---|---|---|---|
| `0` byte-identical (emit_sweep vs pre-E1 main; and the all-auto set) | §3 above; tests/partlayout §6 (all-auto vs no control) | — | see §3 |
| layout read from the OBJECT vs an evaluator sharing no code with the tables | §1, `evaluator.py`: attribute-stripped `-O0 -fno-inline` call graph (call targets and relocations), owners' attributes from the default text, copyability asked of GCC (its own "can never be copied/inlined"), hand class/rank maps (`witnesses.tsv`), presets from the SPEC; judged on `nm` | S1113 (shared writes the inline text), S1114 (callers unfolded), S1117 (P7 above P4-P6) | 8/38, 25/21, 6/40 |
| rank fixture as a precondition | E0's `tests/compound/entry_ranks.tsv` (R0-R3 all witnessed) + the hand ranks of `witnesses.tsv` | E0's S1008 | (E0's) |
| corpus first, synthetic only where no subject | all 9 witnesses are corpus patterns; R3 prefilters exist (`(a+)bcd`, `(?>a*)a`); no copyable R1 part or copyable multi-caller compound part exists, so those rows have no subject and no synthetic witness was needed | — | — |
| preset resolution (every `†` resolves to T0) | §1 (all five `--tune` positions per witness, cells read from tuning.md §5.4) + fixture `preset-empty` | S1116 (a +2 cell leaks) | 10/36 |
| precedence | §2 `fixtures.tsv` (hand-written rows): explicit beats preset, class beats threshold, threshold beats residual, constraints beat everything, later item wins | S1117 | 6/40 |
| held requests reported | §2 (`compound=inline/held`, `prefilter=inline/held`, `wrap=shared/none`, ...) | S1118 (`/held` dropped) | 9/37 |
| H1/H2 by construction | §4: GCC refuses always_inline on the attempt route's label table ("can never be copied") and on a framed computed-goto body ("can never be inlined") | S1112 (P2 dropped: the artifact stops compiling) | 6/40 |
| LK-9 (an exported callee) | the render's internal error (a mark not after `static `) + §3's text check (every changed head is a `static` subject) | — | see deviation 3 |
| clones | §1 (no `.constprop`/`.isra`/`.part` symbol of a shared part) | none (the `noclone` is K24's, A3) | — |
| A1 disjointness | §3: at all five entry rungs, the heads a control changes are subjects only | none | — |
| the seam is copyable | §5: seam bodies under byte and utf8 carry no label table or computed goto | none | — |
| stamp neutrality | §6: every `#define <PREFIX>_*` but `_TUNE`/`_PART_LAYOUT*` unmoved under four controls over 397 artifacts | (S1115 covers the size half) | — |
| answer identity | `tests/axes/run_axes.sh` part-layout arm: default tier `--part-residual=shared`/`=inline`; `AXES_FULL=1` each class value (one run over all four classes) and each rank; values read from `--list-axes` | — | default tier: RED on the first run (shared, 135 lost), FIXED; re-run GREEN, both ends 62,360/62,360 agree (§5) |
| the layouts compile under `-Werror` on a stated sample (not a §3.6 row; the defect §5 found) | §6's -Werror leg: population, near-cap list and `werror.txt` at `-O1 -std=gnu11 -Wall -Wextra -Werror`, both residual ends (810 compiles); against commit A's `noinline` binary it fails on population and witnesses. WIDENED at review r1 (§10.1 F11): seven settings, gcc -O1/-O2/-O3/-Os and clang | S1124 (§10) | — |
| length neutrality on near-cap witnesses | §6 over `nearcap.txt` (the 10 largest corpus hybrids, 45-647 KB) and the population: refusal, stamps and the decision sizes `--warn-emit-bytes` reports are the no-control compile's | S1115 (the marks reach the decision) | 1/45 |
| the decline is visible | §1 + fixtures `measured-alone`, `measured-with-class` | S1111 (T1 never fires) | 11/35 |
| the attribute census | §5 over population x 9 settings against `writers.tsv` (A1-A7 + the layout table) | none | — |
| totality and population per row | §5: one record per subject; per-row totals with floors (T0 828, P2 658, P3 1379, P4-P6 123, P7 182, P8 123, P9 123, P10 64 measured; floors about half) | — | — |

## 5. make strict, make test

- `make strict`: green (whole tree, -Werror -Wshadow).
- Sections run at this tip: test-codegen (16/16, abi 80), test-registry,
  test-cli, test-compound, test-core, test-ci-shards, test-partlayout,
  limits_check: green.
- `make test` (`scripts/perfrun --label e1`, at `4ea932a4d`, 73/73
  sections, 2,058 s): **rc 2, two red sections, both this lane's own
  check-side defects, both fixed** (`a28af0357`) and re-run standalone
  green:
  - `test-spec-history` 145/0: ten unlabeled paragraphs in the E1 spec
    hunks (tuning §2.51/§2.52, match_api §6.3.11, registry §6) gained
    letter-suffixed labels (`¶1a`, `¶5a`-`¶5d`, ...) so every existing
    citation still resolves; this report had cited match_api.md by line.
  - `test-memfn-arch` 15/0 (C4 class 6): `evaluator.py` matched x86
    relocation names; it now reads any relocation type.
  Log `build/e1s/c2/test.log`; verdict lines by
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`.
- `test-axes` part-layout arm (`AXES="--part-"`, 693 s,
  `build/e1s/c2/axes.log`): `--part-residual=inline` OK (62,360/62,360
  agree); **`--part-residual=shared` FAILED with 135 LOST cases, a real
  defect**: with the prefilter `noinline`, gcc -O1 analyses its body across
  the call and reports the caller's `ptrdiff_t window[1][2]`
  maybe-uninitialized, so the artifact fails the harness's `-Werror`
  compile (eight distinct patterns, e.g. `(a)\b(b)`; -O2/-O3/-Os are
  clean). A caller compiling with `-Werror` would hit it. **Fixed by
  making `shared` `__attribute__((noipa))`** (no inlining, no cloning, no
  interprocedural analysis): all eight compile clean; `make test-partlayout`
  gains the -Werror leg (§4), which fails against the `noinline` build. The
  default artifact is untouched (the text is written only under T3; 400
  sampled corpus patterns byte-identical to commit A modulo the abi digit).
  Re-run at `a41465e9a` (`build/e1s/c3/axes.log`, rc 0): both ends OK,
  62,360/62,360 keys agree, 0 lost, 0 gained, 0 mismatches.
- **Full `make test` at the tip `b57d43101`** (`scripts/perfrun --label
  e1b`, `build/e1s/c3/test.log`): **rc 0, 73/73 sections, no `*** [test-`
  line, RUN-STAMP clean**, 1,993 s.
- After the fixes, also standalone: `make strict` green; test-partlayout 46/0,
  test-spec-history 145/0, test-memfn-arch 15/0, test-registry,
  test-cli, test-codegen 16/16, test-ci-shards 9/0 standalone; anchors
  806/806 resolve.

## 6. Deviations from the design, with reasons

1. **Row TM `rank-measured` added** to the artifact table's measured group:
   the design gives `measured` two declines (T1, T2) and leaves its success
   (θ_hot a rank) implicit. Unreachable today, listed and stated so.
2. **`shared` (P2/P4/P8) writes `noipa`, not `noinline noclone`.** The
   design's spelling let gcc read a shared part's body across the call:
   at -O1 that reports the caller's `window` maybe-uninitialized and fails
   `-Werror` (§5), and it deletes a part whose body is `return 0;`.
   `noipa` implies noinline and noclone (K24's `noclone` above the head
   stays, redundant).
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
   prefilter is `return 0;`; under `auto`/`inline` gcc's interprocedural
   constant propagation deletes the part, so the hand class map would need
   a per-layout presence rule. `shared` (`noipa`) keeps it. Recorded in
   `witnesses.tsv`.
9. **No sabotage row for clones, A1 disjointness, the seam or the census**:
   eight ids were allocated and went to the rows above. Asking main if more
   are wanted (question 4).

## 7. Open questions, each with a recommendation

1. **`shared` = `noipa`: CONDITIONALLY RATIFIED by main (06:40), the
   condition DISCHARGED — the warning is a FALSE positive.** Main's
   condition: show `window` is written before every read, else the fix is
   the initialization. The path: the VM's call site reads `window[0][0]`
   only after `if (rx_prefilter(...) != 1) return 0;`. (a) Every
   `return 1;` in every prefilter of the population, the near-cap list and
   `werror.txt` (342 sites) is immediately preceded by
   `if (capture_spans) { capture_spans[0][0] = ...; capture_spans[0][1] =
   ...; }`, and the caller passes its non-NULL `window`. (b) All eight
   warning patterns are EMPTY-LANGUAGE (`(a)\b(b)`: `a`, `b` are both word
   bytes, so `\b` between them never holds); their prefilter is
   `return 0;` alone, so the read is unreachable. At -O1 gcc's IPA
   mod/ref learns that the `noinline` body writes nothing through
   `capture_spans` while the constant return is not propagated (ipa-cp is
   -O2), hence "maybe used uninitialized" on a dead read; -O2/-O3/-Os do
   not warn. (c) Run: the default and `noipa` artifacts of all eight
   witnesses plus `(a+)bcd`, `(a)b`, `(?>a*)a`, and commit A's `noinline`
   artifacts of four of them plus `(a+)bcd`, every subject over `abcdz _` to length 5 at every start (114,381 calls):
   ASan+UBSan with `-ftrivial-auto-var-init=pattern` and valgrind memcheck
   report nothing and every answer hash equals the default's
   (`e1_evidence/fp_runs.txt`, driver `fp_driver.c`). So `noipa` stays:
   it removes the false positive without an emitted initialization, keeps
   the default artifact untouched, and also keeps an empty-language part's
   body. Its cost (no pure/const inference or return propagation on a
   shared part) is unmeasured; E1′'s timing of the `+1` residual cell is
   the measurement that would show it.
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
5. **CI weight of test-partlayout** is ESTIMATED (100 s) in
   `tests/ci/shards.tsv`; **recommend** re-measuring at the next
   `shard_rebalance.py` pass.

## 8. Runs and what is still owed

| item | log | completion line |
|---|---|---|
| emit_sweep, no control | `worktrees/e1/build/e1s/sweep-default.log` | `build/e1s/sweepchain.log`: `default sweep rc=` |
| emit_sweep, all-auto | `worktrees/e1/build/e1s/sweep-allauto.log` | `all-auto sweep rc=`, then `== sweep chain COMPLETE` |
| make test | DONE at `4ea932a4d`, rc 2, both reds fixed (§5): `build/e1s/c2/test.log` | `RUN-STAMP`, `sections ran: 73/73` |
| mech solo S1111-S1118, S1077, S249, S250, S251, S700, S693 | DONE at `4ea932a4d`, all 14 DETECTED: `build/e1s/c2/mech_<id>.log` | `build/e1s/c2/chain2.log` |
| test-axes part-layout arm | DONE, shared RED, FIXED (§5): `build/e1s/c2/axes.log` | `axes rc=` |
| RE-RUNS after the `noipa` fix (GO main 06:40): test-axes arm GREEN; mech S1111-S1118 all DETECTED (46-check suite); full make test at `b57d43101` GREEN | `build/e1s/c3/` | `build/e1s/c3/chain3.log`: `== chain3 COMPLETE` |
| `.o` size delta on the near-cap list (recorded, not gated) | NOT RUN: the script is written (`build/e1s/osize.py`, scratch) but its -O2 compiles of 45-647 KB artifacts would have shared the box with the slot's runs; left for E1′, whose cells need size measurements anyway | — |

## 9. For a fresh agent resuming

Commits on lane/e1: `d37f4ab58` mechanism, `ba636a0a8` spec hunks + re-aims,
`c36f410b7` tests/partlayout + mech arm + S1111-S1118, `09d7c35be` axes arm
(COMMIT A, the zero-mover proof's binary), `fc67299b5` abi 80, the (B)
self-pin, then docs. The suite is `make test-partlayout`; a hand sabotage
driver is `build/e1s/handsab.sh ROW` (scratch, not committed).

## 10. Review fixes (lane e1fix, 2026-10-18)

Review: `docs/dev/reviews/2026-10-18-r1-e1.md` (its outcome column is
filled). Commits on lane/e1 after `b1212d3a9`: `6fbba114b` (the code and
test fixes), the `subject_class` commit, `c572e9570` (sabotage rows, probes,
comments, plan rows), then this report. abi stays 80: every change moves
controlled-path text only (zero-mover proof below).

### 10.1 What changed, per finding

| id | change |
|---|---|
| F1 | P2's layout is 0 (`as-emitted`): it writes nothing, so a body gcc cannot copy keeps its head exactly as the default artifact has it under any control. `noipa` is written by P4/P8 only. The evaluator expects P2 parts `kept` (one local symbol, no clone, head text equal to the default's). New check `p2` in `run_partlayout.py`: every population artifact whose subjects are all P2 (67), under `--part-layout=find:inline`, `--part-inline-rank=R3`, `--part-layout=compound:shared`, `--part-residual=shared` and `--part-layout=prefilter:inline`, is byte-identical to the default but the `_PART_LAYOUT` stamp. |
| F2 | `shared`'s text is K24's guard shape on lines of its own: `#ifndef __has_attribute` fallback, `#if __has_attribute(noipa)` noipa, `#else` noinline, `#endif`. clang 21 is installed on this box, so the -Werror leg gained clang -O1/-O2 legs; the census also checks every emitted `noipa` sits in that guard. clang -Werror on the residual ends is clean. |
| F3 | One statement in all three readers: a part a layout cannot apply to (not copyable, or one caller) keeps its default layout with no attribute added and is reported `/held`: `lib/pcrec.h` (the controls' comment and `PCREC_PART_SHARED`), `cli.md` §1.14¶3, `tuning.md` §2.51¶2/¶2a/¶5b (P2 "nothing"); `facts_listing.md` §4.4¶3 gains `as-emitted`. |
| F4 | `tuning.md` §2.51¶1a: `compound` changes no part at E1 (split's parts stop at P2 and P3). UNREACHED at E1, beside TM/T2 and the wrapper rows: P4, P5 and P6 for the `compound` class (every compound part is held; the census's P4-P6 populations are all prefilters). |
| F5 | Filed under [ENTRY-TABLE] (trigger: the first VM-bodied or `find` subject); the three struct comments say `copyable` is job-wide. |
| F6 | `owned_inline` reads `en.shape != PCREC_VM_ENTRY_PLAIN`; the comment states the premise (the prefilter's one call site is `_search_run`; `ai_body` is the matcher's and is not folded). |
| F7 | `wrap_rows[]` rows carry `holds` and `forwards`; `wrapper_count` walks them first-match per caller. |
| F8 | `head_rows[]` (M1 a part's shell row, M2 other part heads, M3 a subject, M4 none) replaces the chain in `pcrec_part_head_mark`; `layout_texts[]` is the ONE value-to-guarded-text table: the render, `--emit-facts`' `layout` cell and `--list-axes`' writes cell read it. It is a table of attribute spellings the other three writers could read; none migrated ([ATTR-TABLE] filed). A record's class now reads `subject_class` alone (one source). |
| F9 | UNREACHED, argued (row S1126): `pcrec_sb_len_decide`'s readers are the size term's early abort (3 x code cap, ladder attempts) and `VM_PROGRAM_BYTES` (`vmsb`, which never holds a mark: measured unmoved with the subtraction removed). An attempt within the marks' 9 bytes of 3 x cap fits the cap only at more than two thirds prose; the most comment-heavy artifact measured is ~52 % (`((a)|ab){0,500}c` under `-fcomments`: 87,311 bytes, 41,814 of code). |
| F10 | S1111-S1118 each probe their own site (table in 10.3). |
| F11 | The -Werror leg: 7 control settings (both residual ends, `prefilter:` and `compound:` shared/inline, `--part-inline-rank=R2`) over the population, near-cap list and `werror.txt` (405 patterns), deduplicated to 658 distinct texts (a stamp-only difference compiles once); gcc `-O1` on all, `-O2`/`-O3`/`-Os` on every fourth, clang `-O1`/`-O2` on every fourth residual-end text: 1,419 compiles. The claim in §4 is narrowed to that sample. |
| F13 | `memfn_stamps.c` `ident_byte`: one comment (the libc scan runs on marked text; a mark is never inside a call name). |
| Q4 | S1119-S1121 written (10.3). |

`make test-partlayout`: **48 checks, 0 failed, ~42 s** at `c572e9570` (two
new checks: `p2`, the census guard shape). `make strict`: green.
`make test-plan-lint`: green ([ATTR-TABLE] row added to the Backlog).

### 10.2 Zero default movers (abi stays 80)

`scripts/emit_sweep.py` against main `c88537116`, both arms, `--jobs 8`,
taskset 0-7, the slot GO'd in `e1_rulings.md` (`GO e1fix sweep`), run
08:16:48-08:18:48, released 08:18:48 (`build/e1s/c4/chain4.log`). The
subject is HEAD `c572e9570` exported by `git archive` into the lane's
scratchpad, `PCREC_ARTIFACT_ABI` set back to 79 there, built there, and its
binary COPIED to `scratch_e1fix/sw/bin/pcrec-head79` (never `build/`); so a
byte-identical result says no default byte moved besides the abi digit.

| arm | command | result |
|---|---|---|
| no control | `--ref c88537116 --bin .../pcrec-head79` (self-check on: PASSED, all-identical at full reach) | **rc 0, 0 movers / 0 asymmetric on every stream**: c-default 5,336, c-vm 5,337, emit-ir 5,337, emit-ir-auto (base and three arms) 5,790 each, stderr 5,790, composition 37 producing / 106 artifacts. `build/e1s/c4/sweep-default.log` |
| all-`auto` set | `--ref-bin .../pcrec-main` (a scratch copy of a `git archive c88537116` build) `--bin .../pcrec-head79-allauto` (the subject with `--part-layout=prefilter:auto,compound:auto,find:auto,wrap:auto --part-residual=auto --part-inline-rank=none` prepended), `--no-self-check` | **rc 0, 0 movers / 0 asymmetric on every stream**, same reach. `build/e1s/c4/sweep-allauto.log` |

### 10.3 Sabotage rows, solo verdicts

Every row run SOLO by `bash tests/mech/run_sabotage_matrix.sh ROW` at
`c572e9570` (`GO e1fix mech`, 08:18:48-08:31, `build/e1s/c4/mech_<id>.log`),
against a clean `make test-partlayout` of 0 fail / 48 pass. Each new row was
hand-validated first against a rebuilt copy (scratch driver, the same
figures). Every probe now reaches its own row's site (F10); each row's
`SAB_DOC_FIGURE` carries its figure.

| row | plant | probe (clean tree) | solo verdict |
|---|---|---|---|
| S1111 | T1 never holds | `--part-inline-rank=measured` stamps `_PART_LAYOUT_WHY "threshold-unmeasured"` | reach ok, 11/37, DETECTED |
| S1112 | P2 never holds | the attempt-route prefilter's facts row `P2 not-copyable as-emitted` under `prefilter:inline` | reach ok, 7/41, DETECTED |
| S1113 | `shared` writes the inline text (re-anchored on `layout_texts[]`) | `--part-residual=shared` writes the guarded noipa | reach ok, 4/44, DETECTED |
| S1114 | callers unfolded | the inline rung's prefilter row reads 2 callers (P8) beside an owned `search_run` | reach ok, 26/22, DETECTED |
| S1115 | size decision counts the marks | the size note printed under a control, with its stamp | reach ok, 1/47, DETECTED |
| S1116 | the max-speed preset leaks | `--tune=max-speed`'s controls row reads unset everywhere, rows `K,T0` | reach ok, 10/38, DETECTED |
| S1117 | P7 above P4-P6 | `prefilter:shared` + `R2` stops at `P4 class-shared` | reach ok, 6/42, DETECTED |
| S1118 | `/held` dropped | `^(a)b` under `prefilter:inline` stamps `prefilter=inline/held` | reach ok, 9/39, DETECTED |
| S1119 (Q4) | K24's noclone dropped from every search head | a P2 head under a control carries the guarded noclone | reach ok, 0/48, **UNDETECTED (expected)**: gcc 15.2 -O2 clones no part either way (shared is noipa; P2 bodies are not cloned), so the clone count has nothing to count; K24 stays held by tests/codegen |
| S1120 (Q4) | `subject_class` names `_search_run` | `search_run` is listed `owned` | reach ok, 36/12, DETECTED (the render's "subject with no head mark" internal error on every controlled VM compile; section 3's text check cannot see it, because the head is never marked) |
| S1121 (Q4) | an unlisted writer: `always_inline` on `_is_dead` | the pre-multiplied accessor's text | reach ok, 1/47, DETECTED (census) |
| S1124 (F2) | bare unguarded noipa | the guarded text, and clang on the box | reach ok, 2/46, DETECTED (census guard shape, clang -Werror) |
| S1125 (F1) | P2 writes shared | `P2 not-copyable as-emitted` under `find:inline` | reach ok, 3/45, DETECTED (`p2`, evaluator head check) |
| S1126 (F9) | `pcrec_sb_len_decide` stops subtracting the marks | asks for a witness over two-thirds prose | reach MISSING, **UNREACHED (expected)**, argued in §10.1 F9 |
| S1127 (F8) | head-mark row M3 holds for every head | a compound's exported `rx_search` under a control | reach ok, 4/44, DETECTED |

Unreached at E1 (stated, no row can see them): TM/T2 (no measurement set),
the wrapper rows W1/W2 (no forwarding caller before I3), P4-P6 for
`compound` (F4), and the decision-length subtraction (S1126).

### 10.4 make test and the axes arm

Both run detached by `build/e1s/c4/chain4.sh` after the mech rows
(`GO e1fix test`, `GO e1fix axes`):

| run | log | completion line in `build/e1s/c4/chain4.log` |
|---|---|---|
| `scripts/perfrun --label e1fix` (full make test) at `c572e9570` + the doc-only commit | `build/e1s/c4/test.log`; verdict `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` | `make test rc=` |
| `AXES="--part-" bash tests/axes/run_axes.sh` | `build/e1s/c4/axes.log` | `axes rc=`, then `== chain4 COMPLETE` |

RESULTS: see 10.5 (written when the chain completes).
