# twintime — report (2026-10-11)

[LOSS-REVIEW] quiet-box twin timing slot, lane `twintime` (sonnet), branch `lane/twintime`
from main `aa2ddb1d` (pcrec abi 75; pcrec-bench `d359564f`, read-only). Scratch tier, Zen 4 (7700X),
gcc 15.2.0, core 14 (sibling idle), one timing process at a time, ~15 min of timing in total.

The deliverable is `docs/dev/optloop/lossreview/twintime/` (own CLAUDE.md, raw TSVs, pooled TSVs,
`summary.md`); read `summary.md`. Results in one table (gain = faster than base; null band = base vs base
re-run over 8 code layouts; verdicts per fixes.md r2 C1: refute only BELOW the band's low end):

| arm | cell | delta % (layouts min..max) | null | band | verdict |
|---|---|---|---|---|---|
| `bak2-static-seam` | bak-2 | +9.71 (+8.49..+10.38) | +-0.2 | 10-21 | borderline at the low edge (0.29 pp under; bar inside layout range) |
| `bak2-static-noinline` (new) | bak-2 | +8.45 (+6.89..+8.92) | +-0.2 | splits PLT/spec. | PLT-only is ~87% of the seam arm; gcc adds a `.constprop` clone, so |
| `bak2-static-noinline-noclone` (new strict arm) | bak-2 | +7.76 (+6.03..+8.33) | +-0.2 | | PLT-only ~80%; specialization+inlining = 1.3-1.95 pp |
| `bak1-static-seam` | bak-1 | +13.51 (+11.74..+15.50) | +-0.25 | 9-18 | confirmed |
| `modj-static-seam` | mod-j-uc | +5.61 (+3.87..+6.83) | +-0.2 | 5.7-11.4 | borderline at the low edge (0.09 pp under); real, 3x null |
| `phone-static-seam` (added) | phone | -0.02 (-9.94..+6.14) | +-1.0 | 5.7-11.3 | within noise (layout lottery) |
| `bakpy-` / `bakgrel-static-seam` (added) | bak-py / bak-g-rel | +13.53 / +13.47 | +-0.2 | 9-18 (assumed) | confirmed; fixes.md's "taken at bak-1's value" holds |
| T5 `fo20` | 6 pick-defect cells | +53..+94 (sharp-s x16.7) | +-0.2 | stops column | met; modelled gains reproduced |
| T5 `fo20` | nfc-pair, asr-b-ascii | +1.4, +1.6 | +-0.2 | | met, nothing to gain |
| T5 `fo20` | **ci-strasse** | **-11.61** | +-0.2 | "+6%" | regression larger than the floor allowed |
| T5 `fo20` | cls-s-ucp (unlisted) | +66.10 | +-0.1 | "62 others <6%" | an unlisted mover, a win |

Edits to existing files: `vm/twins/twin.py` (two transforms: `static_noinline`, `static_noinline_noclone`),
`vm/twins/twins.tsv` (three rows); nothing under `src/`, `tests/`, `docs/spec/`. Deviations from the charter:
the chartered `noinline` arm is not PLT-only (gcc `.constprop.0` clone), so a strict `noclone` arm was
added; `phone`, `bak-py` and `bak-g-rel` seam twins were added (phone's band is in the panel's list; the other two
test fixes.md's assumed count). The `time.sh` that `run_twin.sh` writes is broken for multi-subject cells
(the subject list is newline-separated into the heredoc), so `timeit.py` replaces it; not fixed in `run_twin.sh`.
gcc writes temp files to `/tmp` unless `TMPDIR` is set (the first `run_twin.sh` calls did, transiently); the new
scripts export `TMPDIR=$LR/tmp`.

Owed / not done: the five C1 short-subject cells, the trail-free and `no-start-set` twins, and any Zen 1
(bench-box) confirmation of the two low-edge cells and phone (D144 add. 4).
