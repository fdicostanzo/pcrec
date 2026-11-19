# covs2g — [COVER-CAP] stage 2, the checks past 32 (unit 2 of covs2b's partition; tests only)

Lane covs2g (opus), 2026-11-16, for the manager. Branch `lane/covs2g`, cut from `lane/covs2b`
@ e34b90d3c. Build go: the owner, 2026-11-16 ~17:30, "Cover-build-go: go" (quoted in the brief).
Item ids: W.. = `docs/dev/lanes/r45read_report.md`, P.. = `docs/dev/lanes/r45chk_report.md`;
covs2b_report.md called this unit "covs2d".

## STATE AT HANDOFF

- STATE: done. No STOP rule fired. Nothing under `src/`, `cli/`, `lib/` or `memfn/` changed; no
  emitted byte moved; no abi number, flag bit or D/K/R id taken.
- RULINGS FILE: `docs/dev/lanes/covs2g_rulings.md` re-read before each commit and before this
  report: EMPTY (no R-n applied).
- PREMISE TEST: holds. After `make`, `build/pcrec --window-search-width=4094 -p rx --pattern
  '[0-9a-f]{33}'` compiles (rc 0) and reads `RX_DFA_SCAN "cover"`, `RX_ENGINE_SEL "selected"`.
- Box: evening hold; locally only one plain `make`, one trace build into lane scratch, single
  compiles and single-case runs. No suite, no `make test`, no axes, no mech, no sanitizer run
  locally. One attempt to run `tests/kitproof/run_cover.sh` whole was refused by the permission
  layer; it was not retried; its rows were checked one case at a time instead (VALIDATION).
- Sabotage ids used: S3264, S3265, S3266 (of S3264-S3275).
- OWED: none (box queue). The cloud runs are under CLOUD RUNS DISPATCHED; their verdicts reach
  main as CLOUD-DONE.

## ITEM TABLE

| item | status | check, its population | plant that reddens it |
|---|---|---|---|
| W16 `n >= 33` kitproof rows | done (d3868b8e2) | `cases.tsv`: 32 answer rows on `W` at n 40/100 (literal, class, `\b` class, utf8 `\d{40}`), each shape with an END-AT-`k` row (match ends at the subject end); answers by `gen_answers.sh` over libpcre2 10.46; floor 105 -> 140 | S3264 / S3265 (below) redden answer rows; a `W` letter dropped from `kp_flags` turns every `W` answer row's REACH red (on the default arm these shapes read `unanchored`, probed) |
| W16 the 10 `W` twins | done (d3868b8e2) | 10 verdict rows on `W` (literal @LD1/40/100/1000, class @D1/40/100/1000, `\b` class 40/100) + 2 facts twins (`a{600}(?:b|cc)` -> `end-at-k|601|601|..`, `a{4095}` -> `cover|4095|4095|..`, sets identical to the x0-held default rows); floors verdict 50 -> 60, facts 19 -> 21 | the same `W`-drop plant: each twin's pattern reads a decline / `width-limit` on the default arm (probed for the facts pair and `[0-9a-f]{33}`, `{40}`) |
| W16 `test-axes` width arm | done (f0e88611b) | `run_axes.sh` job `--window-search-width=<ceiling - 1>` (4095, ceiling read from `--list-limits`, fail loud), `lost_ok` 0, AXES token `--window-search-width`; the whole corpus (7,071 rows); how many of them change route under it is NOT counted here (the sweep counts no covers; covs2a's predictor at D=64 named 3 INTO patterns, a lower bound) | answer identity is run_axes' own machinery (unchanged); a refused pattern is LOST (`lost_ok` 0) |
| W16 compound-part trace compile | done, recorded | `covs2g_evidence/compound_trace.log`: `^\w+|[0-9a-f]{40}` on the trace build: part `q`'s `KITPROOF` line reads `width-limit` at the default and `cover k=40` under `--window-search-width=4095` (the option reaches the part). The parent then picks `RX_COMPOUND "none"`; no split compound with a cover part >= 33 was found in the shapes tried | n/a (a recorded probe, as the design asks) |
| W16 covcost2 record | done, recorded | `covs2g_evidence/covcost2.tsv`, 8 cells (below, VALIDATION) | n/a (a record, one outcome criterion: met) |
| W16 ASan `run_cover.sh` | done (fec43100e); run OWED in cloud | `run_cover.sh` in `tests/lib/san_scripts.txt` (its `DEFER-PLAIN` row removed from `san_excluded.txt`); harness taken beside `$PCREC`, drivers built with `$GENCFLAGS`, `unit_build` already honours `$LIBPCREC`; san shard table regenerated (44 scripts, PASS) | the TT-9 check reddens if the script leaves both lists |
| W16 §11.6.3 P1/P2 | done (011ff980a) | mech S3264, arm kitproof; witness answer row `W [0-9a-f]{40}` on `0` x 40 | hand-probed (plants.log): P1 alone silent, P2 alone declines C14 `proven/under@36:30`, both: cover answering no match (libpcre2 0:40) |
| W16 §11.6.3 P3/P4 | done (011ff980a) | mech S3265, arm kitproof; witness answer row `a{5}` on `aaaaa` (default arm) | hand-probed: P3 alone silent, P4 alone `proven/under@6:00`, both: `aaaaa`/`aaaaaa` lose their match. P4 is planted on pcrec's side (one more stated span at k+1, byte 97 only), not in the kit's tree; same observable as the design's kit-tree plant |
| W16 B2 reference compile = W1's | done (011ff980a) | `run_anchored_match.sh` §4c: `src/gen/known.c` alone at the kit's declared `MF_WSPAN_POS` + 2 (4097, read from `memfn/include/memfn.h`) must fail BY THE ASSERTION'S MESSAGE; control at 4096 must compile. 2 checks | mech S3266 (assertion deleted), arm anchoredmatch; hand-probed: §4c reads FAIL on the planted copy, control PASS |
| W17 | done (d3868b8e2) | `verdict W [0-9a-f]{@D1}` (and 9 more `W` rows at n >= 33) read `cover` | as the `W` twins |
| W20 / P2 predictor | done (31328e5c6) | `docs/dev/lanes/covs2g_evidence/predict.py`: covs2a's predictor plus FORM = N1 from `MFWSTMT` at `--hstar` (both meets, runs across span boundaries, two-member sets, last offset >= h*); red = a mover outside INTO, OUT, FORM; a FORM mover moving a facts row is red; 0 alternatives read is red (K35). `--selftest`: 5 witness verdicts + 2 plants, rc 0 (`predict_selftest.log`). The corpus trace pass is NOT run (heavy; night order P3/P9) | selftest plants: two-member clause dropped (flips `a{32}`), span boundaries ending a run (drops `\w{32}\B` at h*=32); the h*=33 / h*=24 rows catch a dropped `>= h*` |
| W20 S3223's comment | done (f0e88611b) | comment only; `VALIDATE_ONLY` clean | n/a |
| W22 `limits.def:156` home count | ALREADY DONE (37f1dbacb, covs2a) | `LIMITS_H (41)`, 41 rows | n/a |
| W22 `run_registry_tests.sh` limits pin | ALREADY DONE (covs2a, 42 -> 44) | 44, as covs2b's limits_check 44/0 | n/a |
| W22 `limits_check.sh` comment | ALREADY DONE (52114a019) | reads "the eight BUILD_D/FLAG_D rows"; 8 counted | n/a |
| W22 `run_cover.sh` `LIBPCREC` | ALREADY DONE (unit_build) + harness/GENCFLAGS here | see the ASan row | n/a |

## WHAT WAS BUILT

- `tests/kitproof/cases.tsv` (+47 rows), `answers.tsv` (regenerated, the 105 old answers byte-identical),
  `run_cover.sh` (floors 60/21/140; harness beside `$PCREC`; drivers via `$GENCFLAGS`), `CLAUDE.md`.
- `tests/codegen/run_anchored_match.sh` §4c and its header line.
- `tests/mech/sabotages/S3264_cover_proof_range_cut_at_33.sh`, `S3265_cover_proof_range_cut_to_k1.sh`,
  `S3266_cover_seam_assertion_removed.sh`; S3223's comment; `tests/ci/cloud_mech_shards.tsv` regenerated
  (1,321 ids, 90 shards, PASS).
- `tests/axes/run_axes.sh` width arm; `tests/ci/cloud_axes_shards.tsv` + one unit `--window-search-width`
  on shard 17 BY HAND (LEFT OPEN says why); population check PASS (119 jobs, 28 passes).
- `tests/lib/san_scripts.txt` / `san_excluded.txt`; `tests/ci/cloud_san_shards.tsv` regenerated.
- `docs/dev/lanes/covs2g_evidence/`: `predict.py`, `predict_selftest.log`, `covcost2.tsv`,
  `compound_trace.log`, `plants.log`.

## VALIDATION

- Premise compile: above. Trace build: `make BUILD_DIR=$PCREC_TMPDIR/scratch/covs2g/trb
  CFLAGS="-O2 -g -DPCREC_CAND_TRACE" all`, rc 0.
- kitproof rows, checked case by case outside the suite (NOT `run_cover.sh` itself): the 11 `W`
  verdict rows read `cover`; the 35 new answer rows on 8 artifacts, each `RX_DFA_SCAN "cover"`,
  34 equal libpcre2's line exactly and the 35th (`Wu \d{40}` on `é` + 40 digits) equal outside the
  `x` startoffset run_cover.sh does not compare. The facts twins' values are the probe's output.
- `bash tests/ci/cloud_mech_check.sh`, `cloud_axes_check.sh`, `cloud_san_check.sh`: PASS.
- `VALIDATE_ONLY=1 run_sabotage_matrix.sh S3264 S3265 S3266` and `S3223`: FIELDS OK. Each new
  row's `SAB_REACH`, run by hand on the clean tree, prints exactly its `SAB_REACH_EXPECT`.
- covcost2 (`scripts/watchdog -s 120 -m 4g -c 120`, `--features all --emit-main`; then `gcc -O2 -c`):

| pattern | enc | arm | C bytes | scan | sel | gcc s | gcc RSS KB | .text |
|---|---|---|---|---|---|---|---|---|
| `a{4095}` | byte | default | 17,299 | unanchored | selected | 0.05 | 33,236 | 2,008 |
| `a{4095}` | byte | W 4095 | 16,761 | cover | selected | 0.04 | 32,176 | 1,656 |
| `a{4095}` | utf8 | default | 21,260 | unanchored | selected | 0.09 | 35,276 | 3,739 |
| `a{4095}` | utf8 | W 4095 | 20,505 | cover | selected | 0.06 | 33,252 | 2,107 |
| `[0-9a-f]{1000}` | byte | default | 20,817 | unanchored | selected | 0.04 | 32,680 | 1,560 |
| `[0-9a-f]{1000}` | byte | W 4095 | 158,121 | cover | selected | 0.51 | 113,372 | 29,752 |
| `[0-9a-f]{1000}` | utf8 | default | 24,561 | unanchored | selected | 0.08 | 34,940 | 3,195 |
| `[0-9a-f]{1000}` | utf8 | W 4095 | 160,552 | cover | selected | 1.61 | 162,308 | 90,491 |

  pcrec CPU <= 0.62 s, max RSS <= 81 MB in every cell (the tsv has each). CRITERION met: every
  `W` cell reads `cover`, none `size-cap-retry`, none killed, all under the 250,000 B warning. The
  `[0-9a-f]{4095}` cell is READ-3 and was not run (brief).
- Widths used: the `W` arm is 4095 (ceiling - 1) as the design fixes it; the class shapes it
  compiles stop at n = 1000 (verdict) and n = 100 (answers), the literal at 1000/100, `a{4095}`
  only as a facts row and a cost cell. READ-3's failing shape (`[0-9a-f]{4095}` at 4095) is in no
  cell; nothing pins it.
- NOT run locally (box rules): `make test`, `test-kitproof`, `test-anchored-match`, axes, mech,
  asan. They are the cloud runs below.

## CLOUD RUNS DISPATCHED

All on the branch tip with this report, owner main, as the lane's last act:

- `covs2g-test`: `scripts/cloudrun --owner main --kind test --name covs2g-test --ref lane/covs2g`
  (make test: test-kitproof with the new rows and floors, test-anchored-match §4c, TT-9, registry).
- `covs2g-mechrows`: `--kind mechrows --rows S3264,S3265,S3266` (the three new rows; S3223 is a
  comment change and was not re-run).
- `covs2g-asan`: `--kind asan` (the kind whose table runs `tests/lib/san_scripts.txt`, now with
  `run_cover.sh`).
- `covs2g-axes`: `--kind axes` (`run_axes.sh` changed; the width arm is on shard 17).

## LEFT OPEN

- **The axes shard generator splits the `--harness=mfind` pair.** `cloud_units_plan.py axes`
  (with or without `--plan`) writes `--harness=mfind` and `--harness=mfind -fmemfn-simd=x86-64-v3`
  as two units, and `cloud_axes_check.sh` then fails (EXTRA + DUPLICATED, since `AXES=--harness=mfind`
  selects both). Pre-existing, not this lane's change; so the committed table is the previous one
  plus one hand-added row (`--window-search-width`, shard 17, the lightest, ESTIMATE 387 s). The
  table's owner should fix the generator's grouping (a `GROUPS` entry, `cloud_units_plan.py`).
- **The predictor's corpus pass** (P2's trace-build pass over the sweep's corpus, and P3's hand-off
  of the predicted movers at h* to the kit's identity check) is night order: heavy, not run here.
- **A split compound with a cover part >= 33** was not found; the part trace shows the option
  reaching a part (`q`), with the parent then choosing `none`. If a check on a SPLIT artifact is
  wanted, it needs a witness shape this lane did not find.
- **The width arm's reach is uncounted**: run_axes counts no covers. Counting the corpus patterns
  that become covers at 4095 is a census over the corpus (heavy), not run.
- **`MFWSTMT` prints kind `?` for the cover site** (`routed_kind_name` has no REPORT entry);
  cosmetic for the predictor (it keys on the site id), noted for covs2c's owner.
- r27 READ-3 untouched (brief).
