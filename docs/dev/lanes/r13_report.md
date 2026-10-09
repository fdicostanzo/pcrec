# r13 — [MEMFN] R-13, R4e′ batch 1: `vrun-w16` / `vrun-w32`, the first SIMD rows (CANDIDATE)

Lane r13 (opus), 2026-10-09. Branch `lane/memfn-r13`, cut from main
631771b7 (RQ-3 landed, pcrec abi 71). Design of record:
`docs/design/memfn/integration.md` §R4.9 (rev 4.9, D155 and addenda 1-2).

## 1. Summary (resume from here)

- **What landed.** The PREFIX slot of `fn_rows[]` (memfn/src/ofsskip.c)
  holds its first two rows, `vrun-w32` above `vrun-w16`. Both are SIMD
  layer, rendered only at `-fmemfn-simd`, which stays OFF by default, and
  both are CANDIDATE (`tests/memfn/simd_accept.tsv`).
  - The rows sit over `fn-pair` FUNCs only: an offset-skip/pre-check FUNC
    whose predicate is ONE run, scanned at a two-member cube, and which is
    its site's only predicate.
  - Each renders a guarded helper `<fn>__w16`/`<fn>__w32` beside
    `<fn>__body`. The FUNC becomes the D155 shape-(c) selector, whose whole
    body is the `#if`/`#elif`/`#else` chain.
  - `MEMFN_FORMS` reads `vrun@w32+w16`.
- **pcrec's half.** `mf_sink` gained `simd_open`/`simd_close` (MF_SITE_ABI
  9), wired to RQ-3's counters. The `--memfn=no-vrun-w16` and
  `--memfn=no-vrun-w32` denies are the kit registry's first rows; the
  `--list-axes` memfn floor is now 2.
- **The floor rule holds.** At `-fno-memfn-simd`, `emit_sweep` against the
  main binary reads movers=0 on every artifact stream, at each commit. The
  one moving dump is `--list-axes` (its new memfn rows). There is **no
  pcrec abi event**.
  - At `-fmemfn-simd`, C18's four legs, the guard lint and C9-x86 hold on
    all 44 movers.
  - G2's new SIMD family is green at four levels plus ASan+UBSan. Every
    plant is red where its level is live and green where it is compiled
    out.
  - The pcrec corpus files that hold movers answer 5,714/0 at six
    level/sanitizer settings.
  - 15 sabotage rows (S716-S730) were run solo; §6 has their verdicts.
- **What is NOT done (OWED, §8):**
  - identity on every arm (the full gate);
  - the N2 census (pins the rows' pcrec floors);
  - G2 full and `make test`;
  - the tier-U SIMD-on vs SIMD-off timing sweep. It needs RQ-2 and the RQ-4
    slot, and RQ-2 is what supplies the form's second filter position (§3,
    item 2).

## 2. Commits

| commit | group |
|---|---|
| ac471af9 | (1) the sink ops: `mf_sink.simd_open`/`simd_close`, MF_SITE_ABI 8 → 9; `pcrec_memfn_sink` wires RQ-3's `pcrec_memfn_sink_simd_open/_close` |
| 55d5ece2 | (2a) `vrun-w16`: levels.def + `mf_levels()`, `mf_formdecl`, vrun.c, the seam's level blocks and selector chain, the walk's `--memfn=` deny and `kit_ask`, `policy` as a bit-set gate field, `chosen=none`, MEMFN_FORMS, options.def's first row, registry floor 1, spec hunks, cli cases, rows/bounds/C11 movers half |
| a529b1bc | (3) G2's SIMD family (`memfn/tests/run_g2_simd.py`, `g2/g2_simd_*`), run_g2.sh section 4a |
| dcf68b30 | (4) C18 four legs + guard lint + C9-x86, `make test-memfn-simdfloor` |
| d172612f | (2b) `vrun-w32` above `vrun-w16`: decl, contract, deny, bound, floor 2, cli cases, G2/C18 expectations |
| faefecbd | (5) sabotage S716-S730; mech arms `simdfloor`, `g2simd`; S570/S686/S687/S691/S695 re-aimed |
| (tip) | (6/7) `simd_accept.tsv` + rows_check check F; CLAUDE.md files; this report |

## 3. Design choices against §R4.9 (each deviation with its reason)

1. **MF_SITE_ABI 9 carries the sink ops only.** §R4.9.7 folds them and
   `mf_pred.plan_pos2` into one bump. RQ-2 (`pcrec_find_pick2` /
   `plan_pos2`) is not built, so `plan_pos2` comes with RQ-2's own bump. The
   bump is kit-internal and no emitted byte reads it.
2. **KB: the filter is the scanned position KA alone.** Q-R9-3 ruled that
   pcrec states KB, and the kit picks none of its own. Until RQ-2 lands, the
   candidate filter is `(s[c+KA] & M) == V` over VW lanes.
   - Every passing lane goes to the BODY's run compare, so the answers are
     exact either way.
   - This is NOT the two-position filter R-1 timed. Landing RQ-2 adds one
     `and` in `vrun.c:cmask` and moves only `-fmemfn-simd` bytes.
3. **Walk tests 3 (REACH) and 4 (OVER) are the PREFIX rows' predicate
   conjuncts** (`prefix_holds`), not tests inside `kit_walk`. Only `fn_rows[]`
   has a PREFIX slot and a chosen BODY to compare with. The verdict is the
   same `PRED_FALSE`, in the same order.
   - Test 1 (DENY) is in `kit_walk` itself, through a table's new `opt`
     accessor (`kit_opt_denied`, options.c).
   - The PREFIX predicate also requires that the define sink OFFERS the
     bracket ops: a host that cannot count guarded bytes never receives
     them. This is a new contract sentence in memfn.h.
4. **levels.def gained a `header` column** (`emmintrin.h`/`immintrin.h`). The
   intrinsics header is a level fact, and the design states it only in prose.
   `mf_level` is public in memfn.h (data strings only; C4 does not scan
   memfn/). The `MF_I_*` instruction classes are kit-private (kit.h).
5. **The `policy` field** is a stated BIT-SET value. Its classes are PORTABLE,
   INLOOP and SIZE, with NONE for no bit, and a row must serve every bit the
   value carries (gate.c `class_set_of`). This is the §R4.9.2.3 design.
   - No separate `budget` field was added: D91's budget already reaches
     the site as `MF_P_INLOOP`.
   - Every scalar contract serves `MF_ANY`. The SIMD rows serve NONE|SIZE
     (SIZE until R4d's D103 diff, [r9 F-12]).
6. **`guarded_max` needs a bounded verify text, so a shape bound is
   required.** The guarded helper holds one run compare, whose text grows
   with the run length. Q-R9-9 (a) rules a CONSTANT per-row bound, so APPLIES
   takes runs of length 2..`VRUN_MAX_RUN` = 32.
   - This is a CHOSEN shape bound, labelled in vrun.c, and it is Q-R13-1
     below.
   - A longer run renders as today, at the scalar layer.
7. **The trace's open item from R4e′.0** (a PREFIX walk that chooses no row
   was being spelled as a refusal) is now `END chosen=none`, taken through
   `gate_tctx.optional` (memfn/docs/trace_format.md).
8. **`RUN_WORDS` counts unbracketed text only** (§R4.9.2.4). The guarded
   verify restores `art->words`. Sabotage S723 shows C18 sees the
   alternative.
9. **MEMFN_FORMS** is `vrun@w32+w16`, one token per SIMD FUNC in site order.
   The levels listed are the RENDERED ones, top-down.
   `simd_guarded_check.py` now bounds a token `FORM@L1+L2` by the sum of
   its rows `FORM-Lk`.
10. **Includes and blocks.**
    - An intrinsics `#include` is written once per artifact per level
      (`mf_art.simd_inc`).
    - Level blocks are written in ascending order, so w32 falls through to
      a w16 defined above it.
    - The selector's `#if … #else` part and its `#endif` are bracketed. Its
      `#else` call is not, since it is the SIMD-off line byte for byte.
11. **G2's SIMD family is a separate runner** (run_g2.sh section 4a), and it
    is NOT blinded (same author as the rows).
    - Its space is offset-skip FIND/FUNC sites. The pre-check customer
      renders through the same seam and is covered on pcrec's side: by the
      corpus answer sweep over the mover files at six settings (§5), and by
      C18 on its named witnesses (DFA ASSIGN, DFA, no-DFA ON_MISS, VM
      hybrid).
    - The per-path execution floors use the TEST's own text
      instrumentation of the rendered file, not `--coverage`.
12. **C18 is a section of its own**, `make test-memfn-simdfloor`, not the
    `emit_sweep` `simd` arm with projections (§R4.9.8 F-5). It is still ONE
    paired compile (ON/OFF) per cell, with every leg and C9-x86 projected
    from it.
    - C-SEL is not built as its own check. On every mover, C18 (c) proves
      that only `MEMFN_FORMS` and `SIMD_GUARDED_BYTES` move, so every other
      stamp is equal and ON/OFF refuse alike. RQ-3's check gained a `simd`
      arm, so its neutrality half now runs beside real SIMD rows.
    - The near-cap witnesses by name are not added (Q-R13-5).
13. **The acceptance record** `simd_accept.tsv` was born, with CANDIDATE lines
    per row × level × {zen1, zen4}, and rows_check check F holds it to the
    `simd` rows. C19's digest half is UNREACHED until a timing run writes a
    transcript.
14. **Not done from §R4.9.7's "born in batch 1" list:**
    - the bench submission (RQ-5, main's);
    - "§10.6's limits name the official boxes", whose target document I
      could not identify (Q-R13-6).

## 4. D149: every constant of the form

| constant | kind | label |
|---|---|---|
| VW (16, 32) | correctness | DERIVED: the level's register width (levels.def) |
| T | correctness | DERIVED: the predicate's highest read (`vrun_t`, the BODY's `maxk`) |
| R = VW + T (entry test, whole-block test, final block base) | correctness | DERIVED (§R4.9.3) |
| the 1× block loop | performance | `UNMEASURED DEFAULT:` labelled in vrun.c; the 2×/4× unrolls and both cut-overs above R are owed tier-U sweeps (§8) |
| VRUN_MAX_RUN 32 | shape bound | CHOSEN, labelled (Q-R13-1) |
| guarded_max 2,400 (w16) / 2,500 (w32) | bound | MEASURED: G2's worst case (2,383 / 2,413 bytes each row alone; 4,784 both), rounded up to the next 100 |
| CHECK_FLOOR 17M, PATH_FLOOR 1,000, class floors | test floors | MEASURED then ~90% (19,209,480 checks per build) or written as K35 literals |
| simdfloor MOVERS/SIMD_FUNC floors 39, levels 2 | test floors | MEASURED 44 / 44, ~90%; levels literal |
| C11 MOVERS_FLOOR 1, guarded `simd-form` floor 5 | test floors | MEASURED 3 (C11's quick sample) / 6, literal |

## 5. Light validation (all pinned `taskset -c 12-15` or `8-11`, gcc 15.2, the dev box)

- `make -j8`, `make strict`: clean at every commit.
- **SIMD-off zero movers.** `scripts/emit_sweep.py --ref-bin <main
  631771b7 binary> --every 20`, all streams, real run:
  - after (1): movers=0 everywhere, both at default and at
    `--extra=-fmemfn-simd`;
  - after (2a) and (2b): movers=0 on every artifact stream (c-default,
    c-vm, emit-ir-vm, facts, emit-ir-auto ×4, stderr, composition). dumps
    moved 1: `--list-axes`, the memfn rows.
- `make test-memfn-g2` (quick, with the SIMD section): **checks passed
  51,169,262, failed 0**.
  - SIMD family: 455 passed, 0 failed. Each build ran 19,209,480 answer
    checks with 0 fails and 0 faults: x86-64, x86-64-v3, x86-64-v4,
    -mgeneral-regs-only, and ASan+UBSan at v3.
  - Paths at v3: w32 entry 8,217,330 / whole 5,468,366 / final 1,625,124 /
    verified 4,080,776; w16 under it 5,220,220 / 3,584,034 / 1,376,646 /
    2,284,834. At x86-64 the w32 paths are 0, and at gpr-only every path is
    0.
  - All 30 plant cells behaved as required: red where live, green where
    compiled out.
  - Rows (c): 19 ≥ 19. fn/vrun-w16 chose 826 and fn/vrun-w32 826 (g2 floors
    743).
- `make test-memfn-simdfloor`: 8,779 cells (4,387 patterns × 2 engines + 5
  named), 44 movers, 44 SIMD FUNCs, every named bin a mover, **51 passed /
  0 failed**.
- `make test-memfn-guarded`: 10/0, with the `simd` arm; population
  simd-form 6.
- `make test-memfn-stamps`: 25/0. FORMS movers half: 3 movers of 1,143.
- `make test-memfn-rows`: 149/0 (with check F). `make test-memfn-arms`:
  0 failed. `make test-memfn-link`: 8/0. `make test-cli`: 0 failed (+6
  cases). `tests/registry/axes_registry_check.sh`: 0 failed (memfn floor
  2/2).
- **Answer sweep per level** (`tests/harness/run.sh` over the 10 corpus
  files that hold every SIMD mover, `RXTFLAGS=-fmemfn-simd`):
  - 5,714 passed, 0 failed, 0 compile failures at each of x86-64, v3, v4
    and `-mgeneral-regs-only`;
  - the same at ASan+UBSan at x86-64 and at v3.
- Sabotage anchor tripwire (`scripts/m6read_check_sab_anchors.py`): all
  604 rows resolve.

## 6. Sabotage S716-S730 (solo, `bash tests/mech/run_sabotage_matrix.sh SNNN`, tree faefecbd)

| id | edit | arms | verdict |
|---|---|---|---|
| S716 | final-block guard one short (vrun.c) | g2simd | DETECTED |
| S717 | lane mask off by one | g2simd | DETECTED |
| S718 | reach R one short (over-read past n) | g2simd | DETECTED (9 fail, faults) |
| S719 | in-block verify replaced by 1 | g2simd | DETECTED |
| S720 | lanes highest first | g2simd | DETECTED |
| S721 | `over` admits fn-memchr | g2simd | see `docs/dev/lanes/r13_mech.txt` |
| S722 | SIMD rows serve PORTABLE (render at SIMD-off) | g2simd simdfloor | (same) |
| S723 | RUN_WORDS counted inside the bracket | simdfloor | (same) |
| S724 | the `#include` escapes its guard | simdfloor | (same) |
| S725 | w32 under the w16 guard | simdfloor | (same) |
| S726 | w32 under an `__AVX__` guard | simdfloor | (same) |
| S727 | the `--memfn=` deny ignored | cli g2simd | (same) |
| S728 | MEMFN_FORMS left `none` on a mover | memfnstamps simdguarded | (same) |
| S729 | a named rung rendered without being re-asked | cli g2simd | (same) |
| S730 | the selector's `#endif` outside the bracket | simdfloor | (same) |

Re-aimed with the same intent (their anchors moved with the seam): S570,
S686, S687, S691 and S695. Their solo verdicts are in the same file. The
solo runs come from a detached chain that was still running when this
report was committed. `docs/dev/lanes/r13_mech.txt` is its summary, written
by the lane at handback (see §9 for the completed state).

## 7. Open questions (each with my leaning)

- **Q-R13-1** VRUN_MAX_RUN 32, a CHOSEN shape bound that makes
  `guarded_max` a constant. The alternative is a per-site bound formula,
  which re-opens Q-R9-9. *Leaning: keep it.* Runs over 32 bytes are rare,
  stay scalar, and a longer bound is a one-line change with its own G2
  measurement.
- **Q-R13-2** Land the KA-only filter as CANDIDATE before RQ-2? *Leaning:
  yes.* It is opt-in and exact, and RQ-2 moves only `-fmemfn-simd` bytes.
  The tier-U sweep must wait for RQ-2 anyway (§8).
- **Q-R13-3** MF_SITE_ABI 9 now, RQ-2's `plan_pos2` at 10. *Leaning:
  fine.* The bump is kit-internal.
- **Q-R13-4** G2's SIMD family is not D27-blinded. *Leaning: a blinded G2
  lane for the SIMD contract after the rows settle (post-RQ-2).*
- **Q-R13-5** C-SEL by name, with the near-cap witnesses, is not built (§3,
  item 12). *Leaning: C18 (c) plus RQ-3's `simd` arm suffice for CANDIDATE.
  Build it with R4d or when movers reach a near-cap artifact.*
- **Q-R13-6** "§10.6's limits name the official boxes": which document?
  *Leaning: `docs/spec/limits.md` gains one sentence at RQ-5 time.*
- **Q-R13-7** A sink without bracket ops gets no SIMD row (a new memfn.h
  contract sentence). *Leaning: keep it; it is what makes RQ-3's count
  total.*

## 8. OWED (exact commands; heavy, the kit manager's slot with main)

1. **Identity on every arm, both layers** (the floor rule at full
   population):
   `python3 scripts/emit_sweep.py --tree . --ref 631771b7 --jobs 12 > build/scratch/r13_sweep.log 2>&1`
   then the same with `--arms start` and with `--variant all`. Expect 0
   artifact movers; only the `--list-axes` dump moves.
   For the SIMD-on census: `--extra=-fmemfn-simd`. Expect movers exactly
   the FUNC-bearing single-run `fn-pair` artifacts, counted against
   test-memfn-simdfloor's 44 cells.
2. **N2 census** (pins the `vrun-*` pcrec floors, PLACEHOLDER today): the
   command in `tests/memfn/row_floors.tsv`'s header
   (`docs/design/memfn/probes/rowcon/n2_census.sh`, then `n2_report.py
   --floors tests/memfn/row_floors.tsv --propose`). Its `-fmemfn-simd` arm
   is the only one that reaches the rows.
3. **G2 full:** `make test-memfn-g2-full` (its section 4a runs the SIMD
   family's full plant matrix and both ASan builds).
4. **make test:** `scripts/perfrun --label r13 -- build/scratch/r13_test.log`.
   The verdict is `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`. New
   section: `test-memfn-simdfloor` (31 s).
5. **The mech rows** listed in §6 that the chain had not finished, solo:
   `bash tests/mech/run_sabotage_matrix.sh SNNN`.
6. **The tier-U timing sweep** (SIMD-on vs SIMD-off) at the batch-1 cells:
   union-select gate / sweep / pc64-1024 and mod-i, with arms OFF, ON, DENY
   and DISPLACED at `-O2 -march=x86-64 -mtune=generic` and
   `-march=x86-64-v3`, plus the null population, interleaved (§R4.9.5).
   **It needs RQ-2** (`pcrec_find_pick2` and `mf_pred.plan_pos2`): RQ-2
   supplies KB, the fused filter's second position.
   - Without KB the rendered form is the KA-only filter, which is not the
     `ffl` R-1 timed. A sweep now would measure a form that RQ-2 then
     replaces.
   - §R4.9.5 item 10's KB sweep cannot run at all without the fact.
   **It also needs RQ-4's slot.** It runs after RQ-2's re-render, and then
   RQ-5's bench submission.
7. The objdump comparison of the scalar fall-through region, OFF vs ON
   (F-R9-1), reported in the submission.

## 9. Charter vs committed

| charter item | state |
|---|---|
| 1 sink ops wired, zero movers both ways | DONE (ac471af9; emit_sweep default + `--extra=-fmemfn-simd`, movers 0) |
| 2 PREFIX rows `vrun-w16` then `vrun-w32`, over `fn-pair` only, levels.def order | DONE (55d5ece2, d172612f) |
| own `--memfn=no-NAME` deny, first entries, floor raised with readers | DONE (options.def; registry.md §6 floor 2; axes_registry_check reads it) |
| a pcrec cli case for each deny | DONE (6 cases) |
| per-row bound in simd_bounds.tsv, `make test-memfn-guarded` | DONE (2,400 / 2,500 measured; checker maps tokens to rows) |
| every guarded byte bracketed | DONE (C18 (c): inserted bytes == SIMD_GUARDED_BYTES on all 44 movers) |
| SIMD-off byte-identical to main, no abi event | DONE (sampled sweep at each commit; full gate OWED, §8 item 1) |
| 3 G2: generated space vs the scalar loop, -msse2/-mavx2, ASan+UBSan, guard pages 0..2VW+T, alignments | DONE (a529b1bc, d172612f) |
| 4 C18's four legs + guard lint | DONE (dcf68b30), plus C9-x86 |
| 5 sabotage S716-S730, solo, DETECTED or declared | rows written; solo verdicts in §6 / `r13_mech.txt` |
| mech arm wiring | DONE (`simdfloor`, `g2simd`) |
| 6 provenance: SPDX/headers, PROVENANCE.md, CLAUDE.md files | DONE (C16 green: test-memfn-link 8/0) |
| 7 this report; OWED list; lanes/CLAUDE.md line | DONE |
| no build of the filed list | held: no fn-memchr over, no lead form, no w64, no cascade |
