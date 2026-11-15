# covs1 — [COVER-CAP] stage 1 (lane covs1, opus, 2026-11-15)

Build of `docs/design/cover_cap.md` rev 4.1 stage 1 (review round covcap-r4: FI-1..FI-6,
READY-1..READY-5 folded), on BUILD GO "Go on all stages" (Frank, 2026-11-15; this lane
builds stage 1 only). Branch `lane/covs1` from main 91bae2d98.

## STATE AT HANDOFF

- Rulings: `covs1_rulings.md` was EMPTY at every read (last read just before this report);
  no R-n applied.
- Code, spec, abi, witnesses, sabotage rows, instruments and stale text: DONE and
  committed. Last src commit 358f3654b (the recursion identity gate is self-pinned to it).
- Local checks run by the lane: `make strict` clean; `tests/kitproof/run_cover.sh` 171
  passed, 0 failed (47 verdicts, 16 facts, 105 answers, 2160 answer cells);
  `tests/codegen/run_offset_skip.sh` 24 passed, 0 failed; every new and re-anchored
  sabotage row DETECTED in a local plant pre-check (below); X0 stated check on 9 sample
  rows green (6 checked, 2 timed out, 0 red).
- QUEUED (box queue, owner covs1, each `--ready` keeps the 20:00-01:00 hold; scripts in
  `docs/dev/lanes/covs1_evidence/`, results under `/var/tmp/pcrec-pcrec/scratch/covs1/`):
  `covs1-sections`, `covs1-sweep`, `covs1-predict` (after sweep), `covs1-z2`,
  `covs1-ctime`, `covs1-asan`, `covs1-reach`, and `covs1-cloud` (after sections green; it
  dispatches the cloud runs). None had run when the lane ended (the kit's
  `kit-mfind-ident2/3` and `kit-mfind-gate` jobs were ahead). Verdicts are main's to read.
- STOP rule: not triggered (no design/code contradiction left unresolved, no lost cover
  seen locally, no answer moved in the kitproof or offset-skip checks). The sweep/predict
  jobs are where an unexplained mover or a lost cover would surface.

## WHAT WAS BUILT

- The exact stretch is read off the ANCHORED MACHINE (§3.1): `KnWalk` walks virtual
  (state, count) rows with stamp dedup, row arrays sized to the virtual-row count, an
  arena-doubled set array, the eol view tracked per depth (C9 checks every depth 0..k,
  rows at k included: FI-3), and stops at EMPTY / VIEW / ACCEPT / BRANCH. No new limit:
  the stretch is bounded by `PCREC_ANCHORED_MAX_STATES` (4095 positions, named internal
  error past it; R-13 in `cover_window`).
- The cover table (§3.3): C4 gains the `erased` and `island` guards; C7 runs the walk and
  fills the record (stop, k, exact_len, sets, with known marks); new row C15
  `statement-fits` (seam kind) after C7: `k <= MF_WSPAN_POS`, `k+1 <= MF_WREACH`,
  `k < MF_MAX_FWD`; C8 declines `machine-inexact` on BRANCH and fills `MkEnd`; C10/C11 read
  the walk's rows; C12 reads the record's first set.
- The listing: new `#section cover` (`encoding|why|k|exact_len|sets`) in `--emit-facts`,
  one row per encoding, renderer `pcrec_cover_listing_cells` in `src/gen/known.c`
  (spec `docs/spec/facts_listing.md` §4.5 ¶1-¶5, §3 ¶3; §4.1.2 ¶7c retired).
- abi 107 -> 108 (every reader by grep: emit_dfa.c, match_api.md, codegen ABI_EXPECT,
  S693, the abi changelog).
- Witnesses (`tests/kitproof/cases.tsv`): 23 verdicts, 10 facts rows, 50 answers from
  libpcre2 10.46; `run_cover.sh` reads the `cover` section; floors 47/16/105 (§5.3).
- Sabotage (mech arm `kitproof`, §5.4): S3220 (a, length bound), S3221 (b, identity),
  S3222 (c, liveness), S3223 (d, C15 removed), S3224 (f, a byte added to S_0), S3225
  (FI-3, C9 skips the rows at k); S1131/S1136/S1139 re-anchored; `tests/kitproof/reach.sh`
  gains `--facts` (a witness reaches its site by its listing row); cloud mech shard tables
  regenerated. Local plant pre-check: all 9 rows DETECTED, each witness flips as designed.
- Instruments: the trace build's hull check (`pcrec_facts_hull_check`) and a `COVERSET`
  trace record (full-fidelity sets, stated rule, width); `x0.py stated` takes a WMAX
  column as its horizon and `part1_site` a `wmax` (FI-5); `z2.py` re-pointed from SPANSET
  to the listing (stated vs unstated, horizon) plus COVERSET (sets), with K35 counts and a
  per-item bound (`Z2_STATED_ITEM_SECS`, TIMED-OUT counted, never green);
  `emit_sweep.py`'s facts stream takes a declared GONE fact (`FACT:row:gone>`) and a
  declared NEW section (`NAME:section:>new`), both judged both ways.
- §5.5 re-points: `run_offset_skip.sh`'s hex32 decline and `-fno-offset-skip` identity
  witnesses now use the capture form `\b([0-9a-f]{32})\b` (checked: same prefilter form,
  first-class-bounded, offsets none). `run_entry_shape_identity.sh`'s `[0-9a-f]{32}`
  witness is a forced `--engine=vm` build and does NOT move (all five rungs byte-identical
  to main apart from the abi digits), so it is left as is.
- Stale text: the grep of the seven names reaches 0 unmarked mentions outside HISTORY;
  living notes (`ctx_span.md` incl. §11 N-1, `span_arms.md`, `alt_normal_form.md`,
  `window_contract.md`, and `kit_proof.md`) carry a dated "superseded by cover_cap.md
  rev 4, 2026-11-15" marker on each mention line.

## DELETED

- The NFA span slice: `pcrec_span_walk` and its section of `src/facts/kset.c`, the fact
  `span_facts` (facts.def row, PF_SPAN cases, SPANSET/one-walk block, accessor
  `pcrec_fact_span_stated`, decline cases in facts_dump.c), `MkLang`,
  `PF_WHY_ERASED`/`PF_WHY_MARKED`, `pcrec_known_derive`/`MkDerived`, the 48-deep horizon,
  the 24-deep exact loop and `KN_CAP`.
- The limit `PCREC_SPAN_WALK_SUBSETS` (limits.def row; registry count 82 -> 81).
- Sabotage row S1149 (its plant's site is gone); its whys in cases.tsv renamed.

## MOVERS PREDICTED VS OBSERVED

Predicted (§6, stage 1): bench `lit-l31`, `hex32`, `dig-exact-32`, `hex32-id` into the
cover in both encodings; corpus `litrun.rxt`'s 31- and 32-position literals in both encodings
and the k = 1 patterns of §2; nothing out of the cover. Spot-checked locally on the
candidate: `[0-9a-f]{32}`, the 31- and 32-letter literals, `\b[0-9a-f]{32}\b`,
`\d{32}` (utf8), `(?:S(?i:ab)|(?i:sab))`, `(?:[a-z]{0,3}\z|x)[0-9]{3}` are `cover`; the
33-letter literal and `a{40}(?:b|cc)` decline (`statement-fits`); every design-quoted
listing value matched.

OBSERVED: NOT YET MEASURED. The count of record is the sweep (`covs1-sweep`, baseline =
91bae2d98 with its abi digits raised to 108, the ic2 precedent, so the stamp is not a
mover), compared by `covs1-predict` (`predict.py`): prediction from the BASELINE trace
build's own decisions (producer-short/unstated, or fixed-width with wmin <= 32), every
predicted-but-unmoved pattern listed with the candidate's why, LOST covers and
UNEXPLAINED movers each a red (rc 1), and the whole-population decision census
(baseline -> candidate why, both encodings, plus C4 `erased`/`island` counts, K35).
Expected predicted-but-unmoved shape: e.g. `a{30}(?:b{30}c|d)` (baseline
producer-short, candidate `end-at-k`: declines either way).

## VALIDATION

| check | result |
|---|---|
| `make strict` | clean |
| `run_cover.sh` (test-kitproof) | 171 passed, 0 failed |
| `run_offset_skip.sh` | 24 passed, 0 failed |
| plant pre-check, 9 rows (scratch copy) | 9 DETECTED |
| X0 stated, 9 sample rows | 6 green, 2 TIMED-OUT (`[0-9a-f]{32}`, `\d{32}` utf8, 20 s item bound), 0 red |
| `entry_shape_identity` hex32, 5 rungs vs main | byte-identical except abi digits |
| pin sections (codegen, compound, partlayout, resource, cpset-structure, startset, rxtsource, registry, kitproof, spec-history, plan-lint, anchored-match, cand-oracle) | QUEUED `covs1-sections` |
| emit sweep + prediction | QUEUED `covs1-sweep`, `covs1-predict` |
| Z2 census + X0 stated (1-in-5, 90 s item bound) | QUEUED `covs1-z2` |
| compile-time census + `a{4095}`, `[ab]*a[ab]{10}-{2000}`, `[ab]*a[ab]{8}-{300}` both encodings | QUEUED `covs1-ctime` (locally: `a{4095}` compiles in 0.5 s) |
| `make asan` + run_cover on ASan binaries | QUEUED `covs1-asan` |
| `REACH_ONLY=1` sabotage matrix | QUEUED `covs1-reach` |
| cloud test, axes, recidentity, mechrows (S693, S1131, S1136, S1139, S3220-S3225) | QUEUED `covs1-cloud`, released by `covs1-sections` green |

## DESIGN DEVIATIONS

1. The facts witness VALUE in `cases.tsv` joins the cover cells with `|`, not a tab (a
   tab breaks the file's 5-column format).
2. C15 sits in the table right after C7 with id C15 (the design's placement, numbered
   last so earlier ids keep their meaning).
3. The record's "known" marks are booleans (`k_known`, `exact_known`).
4. Row arrays are sized to the virtual-row count up front rather than "grown as needed";
   the set array is the one that grows (arena doubling).
5. `MkEnd` is filled inside C8, and its internal-error bound check is there.
6. The listing renderer lives in `src/gen/known.c` (`pcrec_cover_listing_cells`, declared
   in `core/internal.h`) so `src/dump/` includes no kit header.
7. One extra plant, S3225 (FI-3: C9 skipping the rows at k).
8. `reach.sh --facts`: S1131/S1136/S1139 reach by the listing row, since their witnesses'
   site is now a listing cell.
9. `limits.def`'s INTERNAL_H banner count corrected to 17 (it was stale; other banners
   are stale too and were left).
10. `z2.py` reads stated vs unstated and the horizon from the LISTING as designed, but the
    SETS from a new trace record `COVERSET`: the listing spells a multi-byte set as `[N]`,
    which X0 cannot check. The width is not derived at decision time, so the trace record
    cannot carry it (`?`); the listing does.
11. X0's per-item time bound (TIMED-OUT, counted, inconclusive): 32-wide class stretches
    outran 600 s in the sample run.
12. `kit_proof.md` is treated as a living note (dated per-line markers) rather than its C8
    and bound sentences being rewritten.
13. Cloud dispatch is a queue job gated on the local pin sections (RUNS.md "PIN SECTIONS
    LOCALLY BEFORE DISPATCH", an abi event) instead of a direct last act; the axes run is
    dispatched with test (the brief), not after test green (RUNS.md's default).

## OWED

- Main: read the queued verdicts (`covs1-sections`, `-sweep`, `-predict`, `-z2`,
  `-ctime`, `-asan`, `-reach`, `-cloud`) and the four cloud runs (CLOUD-DONE to main).
  A LOST or UNEXPLAINED line from `covs1-predict` is this design's STOP condition.
- Main at landing: re-pin the recursion identity gate's FILEPIN and ABASEPIN from the
  self-pin 358f3654b to the landing merge; full cloud mech once on the final commit.
- Main: [DD-11.5] must be re-scoped before its next step (its NOTE of 2026-11-15: its
  charter builds on the span slice this lane deleted).
- Stage 2 (kit request §4.3, the 4095-position seam) is not built here.
- Re-timing (§7, G3/G5) is not run: it needs a Frank-cleared window.
