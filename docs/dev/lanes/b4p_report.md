# b4p — R17-b′ B4′, the re-scoped routing commit (LOCKDOWN under the walk ruling)

Lane b4p, 2026-10-21, sonnet, branch `lane/memfn-b4p` (from `lane/memfn-b4scope`
f6fb97780). Authority: `memfn/docs/responses.md` "B4 RE-SCOPED"; Frank's
2026-10-21 build go; `docs/design/memfn/walk_vs_v1_record.md` §5;
`docs/design/memfn/r17b_prime.md` §1.3a, §1.6, §1.8, §3.1 (B4 row), §3.4 and
the new §3.1b. A kit lane: it never merges or pushes.

**No pcrec artifact byte moves and there is no pcrec abi event.** The only
declared move is `--list-axes`' `memfn` section: `fd-r0` and `fd-r5` leave
(floor 14 -> 12). Artifact identity is OWED to the queued sweep job (below);
the evidence in hand is the 24-cell hand comparison and the 14 green suites.

Final tip: see the handback message (the report is committed on top of the
code tip `4f948b0e1`; the report commit touches `docs/dev/` only).

## 1. What changed, by row

| row | before | after |
|---|---|---|
| R7w | default terminal, UNMEASURED-DEFAULT, unrouted, `use_none` | the DEFAULT for every set FIND, basis **MEASURED** (E8's real-text verdict, `walk_vs_v1_record.md` §5); decides; `use_kind`; serves `table_ref` REF (see 3.1) |
| R7 | V1 on covers of at most 2 terms (unrouted) | **WITHDRAWN**, id reserved, never reused |
| R5 | a stated REGULAR regime -> walk (unrouted) | **WITHDRAWN**, id reserved; its deny `fd-r5` retired |
| R0 | >= 2 RANGE terms -> walk (unrouted) | **WITHDRAWN** (ruled 2026-10-20, now executed); its deny `fd-r0` retired |
| R8 R3a R3b R4 R1 R2 | unrouted | decide (no `routed` bit); none holds a fact any compile states today (W64 unbuilt, no fast terminal, no iterator) |
| D1 D1c D1w D2, P0 P2 P3 P4 P9 | `routed` 1 | unchanged in behaviour; the bit is gone |
| RPT (REPORT row) | `routed` 0, decided on a preview art | **unchanged behaviour**: held for its R-26.6 preview, now by `fd_previews` in `fd_row_decides`; the one gate left (see 3.2) |

The reason (the walk ruling, D169 addendum) and the re-open trigger (plan row
[MEMFN-REGIME]) are in the comment above R7w in `memfn/src/finder.c` and in
four new rows of `memfn/docs/finder_history.md` (the §1.8 row-edit log).

Other retirements, in the same commit:
- the `routed` and `locked` columns of `mf_finder_row` (`memfn/include/memfn.h`)
  and of the `--finder-rows` listing; the `liner` field and `SF_COVER_R2`;
  the cover-shape computation and the `<shape>` key token;
- the trace-only shadow `fd_shadow` (and its call in `compose.c`, its
  declaration in `kit.h`), the `FDKEY` lookup records, the FIND `MFTRACE FD`
  records, the `routed=` field of the PRES record, and the POSCOV survey field
  (`trace_poscov` in `finder.c`, the `PCREC_MF_POSCOV` block in
  `src/gen/emit_dfa.c`, which the default build never compiled);
- sabotage: **S916** was a design-table id that never had a file under
  `tests/mech/sabotages/` (its home is `r17b_prime.md` §8.3, already struck at
  rev 4); it is recorded retired and reserved in the matrix header and the
  row-edit log. **S917** reads UNREACHED (no deciding row reads a set key; its
  `SAB_REACH_POP` flips to NOW REACHED when a `FL_KEY` row returns).
  **S922, S1079, S1105** planted the deleted `routed` bit: re-AIMED at
  `fd_row_decides` (S922: the REPORT row decides on every art, the intent "a row
  decides before its step"; S1079/S1105: D1 / P0 held back). **S1020, S596**
  re-anchored (R0 -> R7w; the `routed` column gone from S596's anchor), intent
  unchanged. **S921** kept (its anchor is the define, not the shadow); header
  note added.
- spec: `docs/spec/registry.md` §6¶8a (two rows removed, the "Inert, as
  `fd-r0`" sentences re-stated) and §6¶8b (`memfn` section floor 14 -> 12).
- instruments: `docs/design/memfn/r17b_prime/b4p/` (declared stream-5 delta
  `dumps_declared_B4p.tsv` + `dumps_delta.py`); `r17b_prime.md` §3.1b.

## 2. The readers, found by grep (not enumerated by hand)

`grep -rnIE 'fd-r0|fd-r5|S916'` over the tree (build/ excluded) and
`grep -rn 'routed|locked'` over `tests/memfn`, `memfn/`, `scripts/`:

| reader | action |
|---|---|
| `memfn/src/finder.c`, `memfn/src/options.def` | rows and denies removed |
| `memfn/include/memfn.h` (`routed`/`locked`), `memfn/src/kit.h`, `compose.c` | listing columns, `fd_shadow` decl and call, one comment |
| `tests/memfn/rows.tsv`, `row_floors.tsv` | R0, R5, R7 rows removed; D2/RPT/R7w/P2 signatures re-read from the FDROUTE / PRES records; R7w no longer needs `--measures` (its pin file `pins/r7w_unmeasured.measures.tsv` deleted) |
| `tests/memfn/run_rows.sh` | `ROWS_FLOOR` 40 -> 37 (20 -> 17 fd rows) |
| `tests/memfn/rows_check.py`, `finder_check.py`, `arm_fixtures.c`, `run_proof.sh` | see 4; plants ZK6/ZK7 re-aimed |
| `tests/axes/memfn_arm.py` | the four `fd-r0`/`fd-r5` ASSERT_ZERO classes removed; population check read against `--list-axes` (12 = 12) |
| `scripts/emit_sweep.py` | the two `ASSERT_ZERO`/`DIFFER_PINS` row lists lose `fd-r0`/`fd-r5` |
| `docs/spec/registry.md` | rows and the floor literal |
| `tests/cli/run_cli_tests.sh` | **grep finds no reader** (no `fd-` name, no memfn floor); nothing to edit |
| sabotage rows | S1020 S596 S917 S921 S922 S1079 S1105 (above) |
| `tests/mech/run_sabotage_matrix.sh` | header note |
| docs only, left as history: `docs/design/.../fdb1/dumps_declared_B1.tsv`, lane reports, `r17b_prime.md` rev tables | not edited |
| tooling now dead, left (docs/, never built by make): `fdb1/shadow_census.py`, `fdb1/mk_trace_harness.sh`, `b4prep/` manifest jobs | they read the retired shadow; the manager may delete them |

## 3. Judgment calls the lead should rule on

3.1 **R7w's contract changed (a row edit beyond the brief's letter).** Routing
R7w with its old contract (`use_none`, serves every `table_ref`) made
`select_arm` REFUSE every kit site its pick (`pf_walk`) does not serve: 48
generated proof-family sites (`table_ref` NONE) in `run_finder.sh`'s proof
part, plus fixtures with an unstated consumer kind, were refused instead of
rendered by the composer (first run: 57 failed checks). A routed pick is
never fallen back from, so a row must serve exactly what its arm serves (K96).
R7w now **uses `site_kind`** (a site that states no consumer kind is decided by
no default: no presumed value) and **serves `table_ref` REF** (`walk_applies`).
pcrec states the kind on every FIND site and offers a table on every set site,
so no pcrec compile changes; the 24-cell hand comparison and the queued sweep
check that. This makes "always -> the walk" read "always, where the walk
serves". Logged in `finder_history.md`.

3.2 **RPT stays preview-held.** "Every FIND and PRES row's `routed` bit becomes
1" would have made the REPORT row decide on every art, breaking R-26.3/R-26.6
(a REPORT site on a plain art is refused; `proof_check.c` holds it, plants
S1253/S1256/ZK6/ZK7 hold the gate). The bit is deleted; the hold is now the
existing `fd_previews` list. The brief's "all bits 1" is met for every row
that has a bit to set.

3.3 **The `--harness=measures=FILE` lever is KEPT.** It was built for B4's
prediction, but it has other readers (`tests/compound/run_part_measures.sh` arm
H, `memfn/data/` docs) and is a pcrec CLI surface; retiring it is a pcrec-side
change with its own readers. What retired is the B4-prediction machinery that
rode on the kit side (shadow, FDKEY, POSCOV, `routed`). Say the word and a
follow-up lane removes the lever.

3.4 **Solo mech rows and emit_sweep not run by me.** The box lock was held by
k113's chain (and 580's quiet window ran at the start); `emit_sweep`,
`run_sabotage_matrix.sh` and `REACH_ONLY=1` all take the lock (REACH_ONLY was
REFUSED at wait 0). They are queued instead (section 5). One `make -j16` (2 s)
ran before I read `boxqueue status`; if 580 was already inside its window,
discard that job's reading.

## 4. Checks (light, run by me, at code tip 4f948b0e1 or its WIP parent 76b761f4e)

| check | verdict |
|---|---|
| `make strict` | clean (rc 0) |
| `python3 -I scripts/m6read_check_sab_anchors.py` | 899 sabotages (930 anchor sites), all resolve; staged 44/0 |
| `bash tests/codegen/run_codegen_tests.sh` | 331 passed / 0 failed |
| `make test-core` | 5/0 and 7/0, rc 0 |
| `make test-registry` | 79/0, rc 0 |
| `make test-memfn-finder` (= finder_check 2324/0 incl. proof 1288/0, presence 24/0, arm_reach, pr11, proven) | 2324 / 0 |
| `make test-memfn-rows` | 236 / 0 |
| `make test-memfn-arms` | 383 / 0 |
| `make test-memfn-g2` (the quick tier, G2) | 71,217,800 / 0 |
| `test-memfn-manifest` / `-link` / `-stamps` / `-reach` / `-deleg` | 15/0, 8/0, 25/0, 4/0, 14/0 |
| `run_proof.sh --plants` (S1221-S1226, S1251-S1256, ZK6, ZK7) | all 14 RED (ZK6/ZK7 re-aimed to `fd_row_decides`) |
| `dumps_delta.py REF BIN`, REF = f6fb97780's build | 7 surfaces, 2 declared rows left, 0 failures; the reverse control (a declaration omitting `fd-r5`; one adding `fd-r8`) each FAIL rc 1 |
| `tests/axes/memfn_arm.py` population | `--list-axes` memfn rows = `MEMFN_CLASS` names, 12 = 12 |
| hand identity: 12 patterns x {default, `-fmemfn-simd`} vs f6fb97780, `-p rx --features all`, same `-o` basename | 24 cells, 0 differ (the 24-cell sample is not the sweep) |
| emit_sweep (plain, simd, comments, utf8, vm, start), 0 movers | **OWED**: job 555 |
| re-anchored sabotage rows, each DETECTED | **OWED**: job 560 (one invocation; the rows get one archive each, so each is isolated) |
| `make test` at the final tip | **OWED**: job 560 |

The retired plants' detectors held where I could run them: run_proof.sh's
plants (above) are the REPORT-gate detectors S922's re-aim relies on.

## 5. Queued (DO-THEN-FINISH)

| job | what | log (run dir under `/home/pcrec/projects/pcrec/worktrees/.boxqueue/{running,done,failed}/<TS>-NAME/`) | completion line |
|---|---|---|---|
| **555-kit-b4p-sweep** | emit_sweep vs f6fb97780: plain (every stream but dumps), `dumps_delta.py`, `--arms start` (utf8, simd, comments, start denies), `--extra=--engine=vm`; scripts at `docs/dev/lanes/b4p/` | `job.log`; per-leg lines `== b4p sweep NAME rc=N` | four `== b4p sweep NAME rc=0` lines (declared population 4) |
| **560-kit-b4p-heavy** | quiet-gated, `idle-ok`: `make -j16`, `scripts/perfrun --label b4p` (log `job.log.make` + `.perfrun`), then ONE `PROCS=4 run_sabotage_matrix.sh S1020 S596 S1079 S1105 S922 S917 S921 S1025 S1103 S1108 S1122 S1253 S1254 S1256` | `job.log` (matrix), `job.log.make` (make test) | `== mech run COMPLETE: 14 rows` then `== b4p make test rc=0` / `== b4p mech rc=0` |

Reading them: make test by `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' job.log.make` (empty =
green) beside `job.log.make.perfrun` (K44-ONLY / LOAD-SUSPECT are the shape's,
re-run solo); the matrix by each row's verdict line. Expected: S1020 S596
S1079 S1105 S922 S921 S1025 S1103 S1108 S1122 S1253 S1254 S1256 DETECTED;
**S917 UNREACHED (declared, expected)**.

## 6. Charter vs committed

| charter item | committed |
|---|---|
| 1. R7w default row, MEASURED, evidence E8 + record | yes (3.1 adds the contract fix) |
| 2. withdraw R7, R5, R0; reason in a comment and in the §1.8 log; ids reserved | yes (finder.c comment; four `finder_history.md` rows) |
| 3. retire `fd-r0`, `fd-r5`; retire S916; update every reader by grep | yes; S916 had no file (section 1); `run_cli_tests.sh` has no reader (section 2) |
| 4. LOCKDOWN: every FIND/PRES `routed` -> 1, bit deleted | yes, with RPT preview-held (3.2) |
| 4. trace-only shadow and predicted-mover lever retire; expected-mover set EMPTY | shadow, FDKEY, POSCOV retired; the CLI `--harness=measures=` lever KEPT (3.3); expected-mover set empty |
| 5. out of scope (V1 port, bit 55, `--emit-facts memfn`, PR-10, F2) | none done |
| invariant: no artifact byte, no abi event; registry stream the only move, re-pinned, both directions | no abi touched; `dumps_delta.py` two-way PASS; artifact identity: hand 24/24 now, sweep OWED |
| light checks, run myself | all green above, except emit_sweep / solo mech / REACH_ONLY (box lock; queued) |
| heavy: chain script, kit band, quiet gate, `idle-ok`, not run by me | 560 (and 555) queued |
| deliverable: this report, committed | yes |
