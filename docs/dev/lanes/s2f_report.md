# s2f report: census0's forecast with the measured cards (span_pick stage 2, unit S2f, kit request R-35)

STATE: delivered. The numbers below are COMMITTED (census0 ran directly: pure pricing over the S2b sweep, 1 s, no compiles). Three gate jobs are OWED (queued by the kit manager): kit-s2f-strict, kit-s2f-census, kit-s2f-sections.

## Summary

- Added `census0.py forecast SWEEP --measures SET [--swept-at COMMIT] [-o FILE]` (`docs/design/memfn/span_pick/census0.py`): the S2b pricer with the cards of `measure_store/zen4-grid3/1/set.tsv` (= DEFAULTS `idk`, `zen4-grid3@1:2d2b3c0861443bec`) in place of the stand-ins. Output committed at `docs/design/memfn/span_pick/census0_cards.out`.
- Moves no emitted byte, adds no reader. `census0.out` is NOT rewritten: it is a TIMED path (`slot/plan.py` reads it; est's `NON_TIMED` table), so a rewrite would make a later est refuse. The forecast is a new file beside it (path `docs/` = not timed).
- Watched witness: the measured card point is BELOW k* (k 1.9407 vs k* 4.2094 at gap 256, 3.0270 at gap 1024), so {X,x} is kept, beyond band.
- Row 1 forecast: 207 row-1-class units, 206 priced; movers listed below.

## vcls fold into census0

- `census0.py` now carries `class_measure(form, arg)` (settest: compare count of the member set; rc-words: word count of a run), `settest_shape`, `rc_cls`, `plan_run_len` and `vcls_lines`; the forecast output section (3) is the fold, stamped with the sweep's sha-256 `b88599f6...bffba4` and the commit (`71cad723e`, passed as `--swept-at`).
- Its data lines equal `slot/vcls.out`'s byte for byte (checked here by diff: VCLS-EQ; the census job re-checks).
- `slot/vcls.py` and `vcls.out` are NOT deleted: `slot/link.py` imports `vcls.shape`, `slot/plan.py` reads `vcls.out`, and est classes `vcls.out` as timed. Retirement is a slot change for the manager to rule; until then two implementations of one census agree by an enforced diff (independent control). The span_cards §3.2 PLAN line carries the status.

## Control (smp20 golden)

`census0_control.sh` on the S2b bundles (`/var/tmp/pcrec-pcrec/scratch/memfn/s2b/j0/ws/bundles`): `census0 control: GREEN` (smp20.out byte for byte plus its golden line). The `control` and `sweep` code paths are untouched; `sweep` on the S2b sweep still reproduces the committed `census0.out` byte for byte (diff empty). The job repeats both on the sweep re-made at this base.

## Forecast with measured cards

- Path: `load_cards` reads the set file's `#section rows` (`value_e6`, `noise_e6`; unit walkbytes), the file `--measures=FILE` reads; no kit call. Cards: byte `kit.find_byte.{libc,pair,walk}` (libc = memchr 0.038049, pair 0.073843, walk 1.0), hit `kit.find_hit.<form>.random.<one|alt>.<gap>` (PAIR reads `alt`), verify `kit.verify_cmp.settest.<c1|c2|cn>.{p0,p50}` with cmp(p) interpolated on the pass rate, enter `kit.enter.<site_kind>.NONE`.
- Two points, the hit gaps 256 and 1024 (random landing; the set does not say which density a site has). The stand-in corners are gone: k, hit(PAIR) and hit(memchr) are measured.
- Band: quadrature of (coef difference x card noise); "beyond band" = cheaper by more than z 3.0 x band (UNMEASURED DEFAULT, span_cards §6).
- Not priced, counted in `census0_cards.out` section (4): incumbent alternative PARKED (1,368 of 3,430 RTE window units), D-hors 14, memchr-back 39, unobserved 5, site kind 0 (371) and 2 (71) have no enter card. rc-* run compares are not priced (verify is per position, as in the stand-in sweep). Fused-bound verify rows (value 0) are lower bounds. T-FIND's admission is still census0's assumption (memchr for 1 member, PAIR for 2, walk for any).
- Priced RTE units: 1,562 at each point; DEF 16.

## Watched witness (k*)

smp20 `(?i)x/1234`, blind P, default arm (section (6) of `census0_cards.out`). Check: the stand-in k* at h1 20, hit(PAIR) 1x on this sweep's P model is 2.1464 (span_pick.md: 2.146).

| gap | {X,x} PAIR price | cheapest one-member ('/') | k* | k measured | reading |
|---|---|---|---|---|---|
| 256 | 178,779 | 265,100 | 4.2094 | 1.9407 | BELOW k*; {X,x} cheaper by 86,321, band 1 sigma 2,773: beyond band |
| 1024 | 228,682 | 270,014 | 3.0270 | 1.9407 | BELOW k*; cheaper by 41,332, band 1 sigma 4,175: beyond band |

Prices in walkbytes per 1e6 subject bytes, enter kind 6. The measured card point is BELOW k* at both gaps: {X,x} stays the blind pick (the stage-2 row's "unchanged"); the cards moved k* up (stand-in 2.146 at h1 20) mostly because measured hit costs are large against the byte cards (hit/byte ratio about 1,450 vs the stand-in's 333).

## Row 1 mover forecast

Row-1 class = a NONE alternative whose core position 0 is a two-member set. RTE: 207 units, 206 priced. Movers at the measured point (BAND-0 / beyond band z 3):

| arm | class | gap 256 | gap 1024 |
|---|---|---|---|
| RTE | k2/pair -> k2/walk | 59 / 0 | 91 / 5 |
| RTE | k2/walk -> k2/pair | 11 / 7 | 7 / 6 |
| RTE total | | 70 / 7 | 98 / 11 |
| DEF (12 units, all priced) | k2/pair -> k2/walk | 6 / 0 | 10 / 0 |
| DEF | k2/walk -> k2/pair | 2 / 2 | 2 / 2 |

Other (non-row-1) RTE movers: pair -> memchr 3 / 3 (gap 256), 4 / 4 (1024); pair -> walk 3 / 0, 5 / 1; one walk -> memchr 1 / 1. Reading: nearly all row-1 movement is pair <-> walk, not to a one-member stop; most pair -> walk departures are inside band, so a banded rule keeps them. All counts are `census0_cards.out` sections (4) and (5).

## Gate jobs

Under `/var/tmp/pcrec-pcrec/scratch/memfn/s2f/jobs/` (common.sh sourced by each; each `--dry-run` run here, rc 0, caps/est/expect lines present):
- `487-kit-s2f-strict` (make strict);
- `488-kit-s2f-census` (re-makes the sweep, 5,524 compiles, then control, sweep vs committed `census0.out`, forecast vs committed `census0_cards.out`, fold vs `vcls.out`; completion line `== s2f census COMPLETE: rc=0`);
- `489-kit-s2f-sections` (test-knowledge test-memfn-finder test-codegen test-registry test-memfn-arch test-claudemd-size test-spec-history).
OWED keys: kit-s2f-strict kit-s2f-census kit-s2f-sections. Nothing queued or run beyond `make` in the worktree (needed for the census dry run).

## Charter-vs-committed checklist

- [x] vcls fold into census0 (`class_measure`, stamped), data lines equal `vcls.out`: committed in `census0.py`, `census0_cards.out`. `vcls.py` retention explained above.
- [x] Control holds unchanged: GREEN, census0.out unchanged byte for byte.
- [x] Re-run with the measured cards through the documented path (set file rows): `census0_cards.out`.
- [x] Watched witness reading with numbers: BELOW k*.
- [x] Row 1 forecast mover list with counts per class and arm.
- [x] census0 output committed: `docs/design/memfn/span_pick/census0_cards.out` (not `census0.out`, a timed path).
- [x] Job files 487/488/489, dry-run each, boxqueue cap/est/expect lines.
- [x] CLAUDE.md of span_pick updated; span_cards §3.2 status sentence.
- [ ] Gate jobs run: OWED (kit-s2f-strict, kit-s2f-census, kit-s2f-sections).
