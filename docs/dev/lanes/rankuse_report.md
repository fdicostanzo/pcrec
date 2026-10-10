# rankuse — [MEMFN] R-13 follow-up: the kit reads RQ-2's ranking (KB)

Lane rankuse (opus), 2026-10-09. Branch `lane/rankuse`, cut from
`lane/memfn-r13` 6d16bbac (R-13's `vrun-w16`/`vrun-w32` with RQ-2 / D157
merged in). Request: memfn R-13, batch 1's follow-up step
(integration.md §R4.9.5 item 10's KB row, and batch 1's prerequisites).

## 1. Summary (resume from here)

- **The choice.** The vrun rows' candidate mask now reads TWO positions:
  - KA, the BODY's scanned cube (`plan_pos`), as before;
  - KB, the FIRST position of pcrec's ranking (`mf_pred.rank_pos[0..rank_n)`)
    other than KA.

  The two compares are ANDed before the movemask, which is R-1's `ffl`
  shape. Where the ranking states no other position (`rank_n` 0, or a
  ranking of KA alone), the filter is KA alone, which is R-13's text byte
  for byte. The verify is unchanged (the whole run compare), so the
  answers are exact whichever positions are read.
- **Its basis** (D149, D157: facts on pcrec's side, the method the kit's):

  | part of the choice | label | argument |
  |---|---|---|
  | KA first | DERIVED | pcrec's own fact (`plan_pos`, the BODY's scan); the position all four of R-1's timed cells filter on |
  | WHICH second: the first ranked position other than KA | DERIVED (from the order) | the ranking is ordered by pcrec's prior rate, rarest first, so the first other entry minimises the pair's stated-prior pass rate with KA fixed, if the pair's joint rate is approximated by the product of the marginals. That approximation is not exact: adjacent bytes co-occur, and [OPT-REQPOS] measured joint rates that are not products. That is D157's own "revisit when". Only the ORDER is read, never a rate: any cut on `rank_ppm` would be a threshold with no measurement behind it |
  | HOW MANY: two | `UNMEASURED DEFAULT:` | two is the count R-1 timed (tb_r4b.c `ffl`). One, two and three positions have never been timed against each other. The deny `--memfn=no-vrun-kb` is the one-position arm, so RQ-4's slot measures it |
  | DISTANCE: none beyond KB != KA | DERIVED for correctness | every ranked position lies in the run, so KB <= T, and the reach VW + T already derived for KA covers KB's load. Whether a FAR KB beats the rarer near one is unmeasured and has no variant (§5) |

- **No pcrec abi event, and SIMD-off is untouched.**
  - Every SIMD-off artifact is byte-identical (§4.2).
  - At `-fmemfn-simd`, only the vrun helpers' guarded text moves: the
    mask line and the broadcast declarations.
  - `--memfn=no-vrun-kb` at `-fmemfn-simd` is byte-identical to R-13's
    rendering.
- **The contract edge.** `compose.c`'s new `rank_ok` refuses a ranking that
  is not distinct positions of the RUN term `plan_hint` names. The cases are
  `rank_n` past the run or past MF_RANK_MAX, a position outside the run, and
  a position given twice. A reader of the ranking never reads a malformed
  one. pcrec's rankings pass: `make test-memfn-rank` and every corpus compile
  in the suites below.
- **Bounds re-measured.** With a masked KB, the worst G2 site writes 2,661
  (w16) and 2,721 (w32) guarded bytes for each row alone, and 5,370 with
  both rows. `guarded_max` is now 2,700 / 2,800, up from 2,400 / 2,500.
- **G2's SIMD family states rankings.** It covers seven modes, rate ties,
  entries past `rank_n` that a reader of them would pick, and malformed
  copies. It holds every rendered helper's loads, in order, to the rule as
  derived from G2's OWN generated entries. G2 SIMD family `--quick`:
  1,031 passed / 0 failed (§4.1).
- **Identity** (§4.2): there are 0 SIMD-off artifact movers against
  lane/memfn-r13 across the whole argv population. At SIMD-on, the movers
  are exactly the 44 vrun FUNC artifacts, and the deny is byte-identical to
  R-13.

## 2. Commits

| commit | content |
|---|---|
| 24489c64 | vrun.c (`vrun_kb`, `cpos`/`cmask`/`bcast`, the module comment's SECOND FILTER POSITION and D149 rows), options.def `vrun-kb`, compose.c `rank_ok` |
| 59a20fe3 | G2 SIMD family (generator rankings + runner check), bounds 2,700/2,800 (vrun.c, simd_bounds.tsv, limits.md), registry.md floor 3, tuning.md §2.43, cli cases, simd_accept.tsv lines, integration.md |
| 862c09bd | sabotage rows S738-S742, CLAUDE.md files, cli case made arch-blind |
| (tip) | this report, lanes/CLAUDE.md line |

## 3. Deny rows and readers moved (found by grep)

- `memfn/src/options.def`: `vrun-kb` (DENY, budget scan, layer simd).
  `--list-axes`' memfn section now has 3 rows, and the floor in
  `docs/spec/registry.md` §6 is now 3; `axes_registry_check.sh` is green.
- `tests/memfn/simd_accept.tsv`: 4 CANDIDATE lines (`vrun-kb` × w16/w32 ×
  zen1/zen4). rows_check check F requires a line per simd-layer option.
- `tests/cli/run_cli_tests.sh`: 2 cases.
  - `no-vrun-kb` is inert SIMD-off.
  - On `(?i)cat`, the default loads at i and i + 1; the deny loads at i
    alone and keeps `vrun@w32+w16`.
- Spec: `registry.md` §6 (the row, floor 3), `tuning.md` §2.43 (the deny),
  `limits.md` (bounds 2,700 / 2,800).
- `docs/design/memfn/integration.md`: §R4.9.5 item 10's KB row (the
  choice and its basis), the batch-1 landing note, and the prerequisites
  bullet.

## 4. Validation (light only; pinned `taskset -c 12-15`, gcc 15.2, the dev box)

### 4.1 Suites

| check | verdict | log |
|---|---|---|
| `make -j4`, `make strict` | clean | `strict1.log` |
| `make test-memfn-{manifest,forms,reach,link,stamps,guarded,simdfloor,rank,arms,deleg,rows}` | all rc 0 (simdfloor 51/0 over 44 movers; guarded 10/0; rows 150/0 with check F's new lines; rank 0 failed) | `light/test-memfn-*.log` |
| `make test-cli` | 284 passed / 0 failed | `light/test-cli.log` |
| `tests/registry/axes_registry_check.sh` | rc 0 (memfn floor 3/3) | `light/axes_registry.log` |
| `make test-memfn-arch` | RED, **pre-existing on lane/memfn-r13**: C4 new-vocabulary hits in r13's S725/S726 and `run_sabotage_matrix.sh:387`. My one hit (an intrinsic name in the cli case) was removed | `light/test-memfn-arch.log` |
| `make test-codegen` | RED 14/15, **pre-existing on lane/memfn-r13**: K37 flags `tests/memfn/run_simd_floor.sh:33`, a continuation line of a `$TIMEOUT_BIN` call that this lane did not touch. [SABANCHOR] resolves all 616 rows, S738-S742 included | `light/test-codegen.log` |
| G2 SIMD family `--quick` (`memfn/tests/run_g2_simd.py`) | before the bound re-pin: 1,030 passed / 3 failed, all 3 being the old bounds. Every build: 19,250,552 checks, 0 fails, 0 faults. All 30 plant cells as required. Ranking: 7 modes 36-48 rendered sites each; shapes kb 205, no-kb 93, kb-not-rank0 82, kb-at-end 109, ties 135; 80 malformed copies refused. **After the re-pin (`g2s2.log`): 1,031 passed / 0 failed.** The same counts as before, with guarded maxima 2,661 / 2,721 / 5,370 under 2,700 / 2,800 / 5,500 | `g2s1.log`, `g2s2.log` |

All logs are under `/home/pcrec/.claude/jobs/e99da2a5/tmp/rankuse/`.

### 4.2 Identity, light tier (the full gate with `--arms start` / `--variant all` is OWED)

All three runs use `scripts/emit_sweep.py --ref-bin <lane/memfn-r13 6d16bbac
build>`. They covered every corpus pattern (argv population 5,431,
composition 373 files), with logs in `sweep/`:

| arm | result |
|---|---|
| SIMD-off (default), all streams | **0 artifact movers** on every stream: c-default, c-vm, emit-ir-vm, facts, emit-ir-auto ×4, stderr, composition. The only dump that moves is `--list-axes`, by exactly the `vrun-kb` row. Self-check passed (`off.log`) |
| `--extra=-fmemfn-simd`, all streams | c-default **44** movers and c-vm **43**: the vrun FUNC artifacts, matching test-memfn-simdfloor's 44. Every other stream has 0 movers; the dumps move by the row (`on.log`) |
| `-fmemfn-simd --memfn=no-vrun-kb` (tree, through a wrapper `--bin`) vs base `-fmemfn-simd`, streams c-default/c-vm | **0 movers** on both (4,980 / 4,981 reached). The deny arm IS R-13's rendering byte for byte (`onkb.log`) |

Both SIMD-on runs exit rc 1 only through the sweep's own "NO DIFFER FLOOR
PINNED" rule on the unpinned `-fmemfn-simd` extra arm. That rule is about
the instrument's arms and is not a mover.

The `--memfn=no-vrun-kb` deny cannot be given to the base binary (its
registry has no such row), so emit_sweep's `--extra` cannot pair it. A
wrapper script that injects it into the tree side only was the instrument.

## 5. What is NOT built, and why

- **N >= 3 positions.** No reading triggers it. The trigger is RQ-4's
  DEFAULT vs `no-vrun-kb` reading: if the pair beats KA alone by a wide
  margin in the hit-sparse cells, a third position is the next question,
  with its own deny.
- **A distance rule / far-KB variant.** A threshold would be a new
  constant. Its trigger is the pair LOSING or tying KA alone on a cell
  where KB is KA's neighbour. On R-1's cells the rule picks union-select
  SELECT@4 + L@2 and mod-i CAT@0 + A@1, where R-1 timed T@5 and T@2 by
  hand. Correlated neighbours are where joint rates depart from products.
- **Skipping the verify when the pair covers the whole exact run** (R-1's
  `PAIR_IS_RUN`, L == 2). It would be a byte-moving choice of its own, so
  it is filed rather than built.
- **Reading `rank_ppm`.** Not needed by this rule.

## 6. The RQ-4 timing question (tier U), stated exactly

At the batch-1 cells (the four R-1 cells as pcrec renders them, and the
corpus's vrun movers), compare three arms, interleaved:

- **DEFAULT** (`-fmemfn-simd`: KA AND KB);
- **KB-DENY** (`-fmemfn-simd --memfn=no-vrun-kb`: KA alone, R-13's form);
- **OFF** (`-fno-memfn-simd`).

Run them at `-O2 -march=x86-64 -mtune=generic` (w16 live) and
`-march=x86-64-v3` (w32 live), in §R4.9.5 item 7's regimes:
- throughput gate and sweep at 64 KiB and 1 MiB, hit-sparse and hit-dense;
- the per-call span ladder;
- the hit-spacing ladder (8..256 B);
- PLUS one cell where KA's byte is COMMON in the subject and the run rare.
  That is where KB earns its load, and none of R-1's subjects were built
  for it.

The question is whether `DEFAULT − KB-DENY` falls outside the null band, in
which direction, and in which regime. KB stays as the default only if it
never loses past the floor. The `UNMEASURED DEFAULT:` label in vrun.c
becomes `MEASURED-UNOFFICIAL (<CPU class>)` from that reading.

## 7. Sabotage S738-S742 (ids proposed to main, which has not confirmed them; solo runs: addendum)

| id | edit | arms |
|---|---|---|
| S738 | KB ignores `rank_pos` (takes the run's tail positions in turn) | g2simd |
| S739 | the ranking read from its wrong end (commonest first) | g2simd |
| S740 | entries past `rank_n` read (`i < MF_RANK_MAX`) | g2simd |
| S741 | the `no-vrun-kb` deny ignored | cli g2simd |
| S742 | `rank_ok` disabled (a malformed ranking accepted) | g2simd |

## 8. OWED (heavy; the manager's slot)

1. **Identity on every arm, both layers**, against lane/memfn-r13 6d16bbac
   (whose own identity gate vs main is r13's OWED item 1):
   - `python3 scripts/emit_sweep.py --tree . --ref 6d16bbac --jobs 12`,
     then the same with `--arms start` and with `--variant all`. Expected:
     0 artifact movers; the `--list-axes` dump moves (the `vrun-kb` row).
   - `--extra=-fmemfn-simd`: the movers must be exactly the vrun FUNC
     artifacts (test-memfn-simdfloor's 44), and only inside their guarded
     helpers.
   - `--extra='-fmemfn-simd --memfn=no-vrun-kb'`: 0 movers against
     6d16bbac at `-fmemfn-simd`.
2. **N2 census** (the command in `tests/memfn/row_floors.tsv`'s header): no
   row was added, so this confirms that nothing moved.
3. **G2 full:** `make test-memfn-g2-full`.
4. **make test:** `scripts/perfrun --label rankuse -- build/scratch/rankuse_test.log`.
   Read it with `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`. Expect the
   two pre-existing r13 reds (test-memfn-arch C4, test-codegen K37) unless
   r13 fixed them first.
5. **Any S738-S742 row not DETECTED solo in the addendum.**
6. **RQ-4's timing question** (§6), in the tier-U slot.

## 9. Charter vs committed

| charter item | state |
|---|---|
| design and build the kit's use of the ranked array in vrun.c's filter | DONE (`vrun_kb`, cmask) |
| choice measured, derived or labelled `UNMEASURED DEFAULT` | DONE: which = derived from the order; how many = UNMEASURED DEFAULT (2); distance = derived for correctness |
| the deny/variant that lets RQ-4 measure it, and the exact measurement | DONE (`no-vrun-kb`; §6) |
| floor rule: SIMD-off byte-identical, no pcrec abi event; light identity proof; heavy list | DONE light (§4); full gate OWED (§8 item 1) |
| own deny row + pcrec cli case in the same commit | DONE (59a20fe3 carries cli + floor; the row itself in 24489c64, one commit earlier on the branch: both are on the branch before any merge) |
| bounds re-measured | DONE (2,700 / 2,800) |
| G2 SIMD family: own byte loop, generated predicate space, rank_n 0, 1, ties, ends; `--quick` | DONE (§4.1) |
| sabotage rows that kill the new read, measured solo | rows written (S738-S742; ids pending main's confirmation); solo verdicts in the addendum |
| integration.md §R4.9.5 KB row | DONE |
| CLAUDE.md files; this report; lanes/CLAUDE.md line | DONE |
