# Lane l1fix: review r53's FIX-NOW items on the L1 remodel branch

Lane l1fix (opus), 2026-11-19. Branch `lane/l1build` (worktree `worktrees/l1build`), from tip `edec6b7f5`. The brief
is the MANAGER RULINGS section of `docs/dev/reviews/2026-11-19-r53-l1remodels.md`. Every FIX-NOW item is applied as
ruled: F1, F2, F3, F4, F6 (the code variant), F8 (minimal), F9, F10 and F12. F7's register-row-5 note rides F10.
F5, F11, F13 and F14 (DOC/PLAN/NOTED) are untouched. A_CALL/A_BREF → NODE stays PLAN.

## Summary

- **The commits:**
  - 3 commits add bindings: a twin case, an `.rxt` block and sabotage rows S3355-S3357 (F1, F2, F3).
  - 2 commits change `src/` (F6; F8+F9). Both are byte-identical by construction, and each has its own
    identity gate (below).
  - 1 commit is evidence (F4), 1 is docs (F10 + F7's note), and 1 is the census instrument (F12).
- **Each new sabotage row was hand-measured RED under its plant** on a scratch export, and is GREEN unplanted.
  `REACH_ONLY` reads all three REACHED.
- **The anchor tripwire resolves at the tip:** 1310 rows, 1364 sites, all anchors resolve.
- **Checks at the tip (`9903c386b` and later):**
  - `make strict` is clean.
  - `tests/core/kindrow_check.sh` passes 6/6.
  - B2 (`check_derive.py`) passes 115 cases with 0 failures.
  - `tests/altcls/` passes 310/310.
- **The census instrument** now prints `CENSUS-VERDICT: STOP|PROCEED` and exits nonzero on STOP and on an EXPECT
  disagreement. Both drills are red as designed.
- **Both identity gates are GREEN with 0 movers.** Owed: the mech rows on every changed file, and `make test`. These
  are queued; their keys are in STATE AT HANDOFF.

## Fixes by finding

| id | commit | what |
|---|---|---|
| F1 | `be76ad164` | Twin case `hand4:r53negnever` `^a|(?!^)b$` added to `docs/design/compound/twin/results/cases2_owed.tsv` (check_derive.py reads it; the differential's 177-case-arm record stays true of cases2.tsv, so the owed file is its home); S3355 drops `pcrec_ast_row`'s negative-lookaround NEVER override. Twin CLAUDE.md names the case. |
| F2 | `e3b1b8958` | S3356 flips kindrow.def's A_CAT NEVER cell ANY → EVERY, SAB_REACH `^abc|xyz$` → `RX_COMPOUND "split"`; S899's header re-described: it binds `q_alt`'s per-arm drop, not the column. The design sentence ("the line the extraction rewrites") is DOC for the next span_arms revision, not edited here. |
| F3 | `0c42988cf` | The oracle-generated `S-b` block `(a)(?:ab|\1dd|ad)` (`aadd` → 0 4, group 1 0 1; plus `aab`, `aad`) in `tests/altcls/altnf_rules.rxt`, by adding the cell to its generator `docs/dev/lanes/altbuild_evidence/altnf_rules_gen.py` and regenerating (diff: the one new block only); S3357 reads A_BREF as a zero-width unit in `pcrec_ph_node`. |
| F4 | `96100c5ee` | `l1build_evidence/firstunit_anchors_l1.py DIR subject`: a SUBJECT-numbered range set (lines at `39981a9d1`): RM6 = derive.c 150-362 (q_* and `qp_walk`, so S1190 is in), RM6k = kindrow.def, RM6h = internal.h's KindRow block through `pcrec_never_by_row`, REM3 = `anf_head`, REM3d = desc.c's head rule. Output: `l1build_evidence/anchor_map_subject.txt`. |
| F6 | `713cf7506` | derive.c's leaf arm reads the row: `pcrec_never_by_row(cx, pcrec_ast_row(a).never, false, false)`. The restated leaf `false` is gone. `pcrec_never_by_row` gains `Ctx *cx`, and its KNEVER_NODE arm is a loud `pcrec_ctx_fail`. `pcrec_ctx_fail` is re-declared just above it, because its home declaration sits 2,000 lines later in internal.h. kindrow.def gains the sentence: the column is the language-level answer, and the KILL is the reader's own (A_GSTART/A_CTX read NO). |
| F8+F9 | `39981a9d1` | `ph_wmul` is a reader of `pcrec_sat_mul(x, k, PCREC_W_UNBOUNDED + 1)` returning false above `PCREC_W_UNBOUNDED`, `*out` written on success only; the REP arm's `1LL << 40` is `PCREC_W_UNBOUNDED`. `ph_body` makes a NULL body on A_LOOK/A_CAP/A_ATOMIC/A_REP a loud `pcrec_ctx_fail`. |
| F10 (+F7) | `9903c386b` | Register row 5's status (architecture.md): derive.c's never pass done, leaf list deleted, A_CALL/A_BREF NO until L1's feature decides; F7's note (the head rule restates TEXT; trigger L1's feature commit or the next new AKind). src/opt/CLAUDE.md's derive.c entry names the NEVER column (kept under the 12 KB cap by tightening the same entry). internal.h's KindRow comment names `never`'s reader. |
| F12 | `4633830d6` | `census_l1.py`: `CENSUS-VERDICT: STOP|PROCEED (...)`. The verdict is read from the POPULATION's predicted movers, never from EXPECT. An empty population read by the model is a STOP (K35). rc: 0 = PROCEED with every EXPECT row agreeing, bit 1 = an EXPECT disagreement, bit 2 = STOP. The docstring states it. |

**F8's boundary, argued.** The old code is `false iff k != 0 && x > W/k`. For `x, k > 0` that is `x*k > W`.
- `pcrec_sat_mul(x, k, W+1)` returns `x*k` when `x <= (W+1)/k`. Then `x*k <= W+1`, and the new test `p > W` is
  false exactly when `x*k <= W`.
- Otherwise it returns `W+1`. Then `x*k > W+1`, and both the old and the new form return false.
- When `k == 0` or `x == 0`, both forms give 0 and true.
- `x` is a head width (≥ 0). `k` is `rmin`, or `rmax` once `rmax >= 0` has been checked.

So the two forms agree on every input either one can see, and the identity gate measures it.

**F6's design point.** A NODE row (A_CLASS, A_REP) never reaches the propagation: derive.c keeps their own code
(`is_never_leaf`, REP's `m`). The loud arm therefore fires only if a later edit turns a kind's cell into NODE without
giving its reader node code, such as A_CALL/A_BREF under L1's PLAN.

## Identity verdicts

The gate is the design's own: `scripts/emit_sweep.py --ref-bin <base e121371b2> --bin <commit build>`, run over the
corpus plus `docs/dev/lanes/sae1_evidence/bench_patterns.txt`, covering every stream (.c streams 1-2 and 4, emit-ir,
composition, dumps, facts stream 6). The verdict is `sae1_evidence/ident_check.py` against an EMPTY census. The base
build is lane l1build's `$PCREC_TMPDIR/scratch/l1build/trees/base`; its `src/` and `cli/` were diffed equal to
`git archive e121371b2`.

| job | commit | verdict |
|---|---|---|
| `200-l1fix-ident-f6` | `713cf7506` (F6) | GREEN (wall 157 s): every stream population=7460 (composition 465, + 7), movers=0, asymmetric=0; `census movers: 0; facts-stream movers: 0`; `== ident_check COMPLETE: 0 unexplained` |
| `200-l1fix-ident-f89` | `39981a9d1` (F8+F9) | GREEN (wall 158 s): the same, movers=0 on every stream; `== ident_check COMPLETE: 0 unexplained` |

Later commits change no compiled source except one internal.h comment (F10), so they emit nothing new.

## Sabotage rows

All three were hand-measured on a scratch export of the lane tip, with the plant applied and the tree rebuilt.

| row | site | witness / detector | unplanted | planted | reach |
|---|---|---|---|---|---|
| S3355 | internal.h `pcrec_ast_row`'s negative-LOOK NEVER override | test-compound B2, twin case `^a|(?!^)b$` | B2 115 cases, 0 fail | B2 1 fail: `never disagrees: twin False, build True` | `SAB_REACH_POP` on the twin row: 1 |
| S3356 | kindrow.def A_CAT NEVER cell | test-compound | (the unit was green at the tip per l1build's gate) | test-compound FAIL: E0 4 fixtures, B2 5 cases (`^a$`, `\Gab`, `a{0,4}\A`, `^ab`, `\Gab` utf8), B4 3 controls + 13 decline-list cases; split.rxt stays green (V-2) | `^abc|xyz$` → `RX_COMPOUND "split"` (plant: `"none"`) |
| S3357 | desc.c `pcrec_ph_node` BREF/VAR/CALL wall | `tests/altcls/altnf_rules.rxt` S-b block | 84/84 | 2/84 fail (the `aadd` span and its group slot) | `ALTCLS_FACTORED 1` / `ALTCLS_MERGES 0` (plant: 0 / 1) + population 1 |

`REACH_ONLY=1` reads all three REACHED. The matrix runs of these rows, together with every row on a file this lane
changed, are queued (STATE AT HANDOFF).

**The census drills (F12)**, on the base build with `--model-only`:
- **Drill A:** an empty tree plus an empty bench gives `CENSUS-VERDICT: STOP (empty population ...)`, rc 2.
- **Drill B:** one EXPECT row mutated (`x[^\x00-\xff]y` dead → none) gives `DIFF` and `STOP`, rc 3.
- **The full run at the base** (`$PCREC_TMPDIR/scratch/l1fix/census/full.log`, under the box lock): 54 predicted movers (corpus 54, bench 0), 26 EXPECT rows with 0 disagreements, `CENSUS-VERDICT: PROCEED (54 predicted movers ...)`. That is rc 0 by the rule; the exit code itself was not captured, because the boxlock wrapper's output went to the log.

## STATE AT HANDOFF

- **Commits on `lane/l1build` after `edec6b7f5`:**
  - `be76ad164` F1;
  - `e3b1b8958` F2;
  - `0c42988cf` F3;
  - `713cf7506` F6;
  - `39981a9d1` F8+F9;
  - `96100c5ee` F4;
  - `9903c386b` F10 (+F7 note);
  - `4633830d6` F12;
  - this report.
- **Rulings file** `l1fix_rulings.md`: empty. Last applied: none.
- **Not done (as ruled):**
  - F5, F11 and F13 are DOC for the next span_arms revision, including the S899 design sentence (F2's DOC half).
  - F7 beyond the row-5 note is PLAN; F14 is NOTED.
  - A_CALL/A_BREF → NODE is PLAN.
- **Queued box-queue jobs** (owner `l1fix`; scripts under `$PCREC_TMPDIR/scratch/l1fix/jobs/` and the worktree's
  `build/l1fix_stages`). They are owed to the manager's merge verdict, not to this lane:

  | key | what | pass |
  |---|---|---|
  | `200-l1fix-ident-f6`, `200-l1fix-ident-f89` | the identity gates | DONE, both GREEN (above) |
  | `200-l1fix-b202611191316002982870.mechA` | S893 S899 S904 S1187 S1189 S1190 S3355 S3356 (the compound-arm rows) | each at its declared expectation |
  | `201-l1fix-b202611191316002982870.mechB` | S236 S1340 S1440 S1480 S1638-S1641 S1886 S1888-S1891 S1920 S3357 | the same |
  | `202-l1fix-b202611191316002982870.test` (chained: each waits for the one before to go green) | `make test` through perfrun on the tip: the new `.rxt` block moves corpus populations, and this covers test-compound, test-altcls, test-core and test-cpset-structure | no `*** [... test-X] Error` line |

  Nothing may be committed in the worktree while the mech jobs run: the runner archives HEAD per row.
