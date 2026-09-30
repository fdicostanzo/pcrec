# [SEL-COST] STEP 0 (lane selcost0, sonnet, 2026-09-29)

Analysis-only lane. No `src/`, no builds, no heavy suites. Delivers
`docs/dev/sel_cost_census.md` + `docs/dev/sel_cost_census/` (reproduction
scripts and derived data). Read the doc for the full argument; this
report is the headline for a handback.

## Headline numbers

Read pcrec-bench's `syntax@0.1` fullroster report exhaustively (pin
`751b9c6d`, 7 records, all trial-agreement `agree`) — 95 named patterns,
83-95% compile, three regimes (`large-subject-throughput`,
`short-subject-search`, `match-compliance`). The roster's only non-auto
pcrec comparator is forced `--engine=vm` (caps class only — no forced
`--engine=dfa`, no forced-VM nocaps testee exist in this roster).

Population, caps class: `large-subject-throughput` 70/80 auto wins/ties,
`short-subject-search` 64/83, `match-compliance` 20/80. On the regime
closest to real traffic (scanning a subject), `auto` already wins or ties
87.5% of the time.

Four cause groups, all backed by pcrec's own `engine_metadata` compile
stamps (never the bench's internal reduction):

- **D — `match-compliance`'s `(?:P)\z` wrapper cost.** 60/80 caps cells,
  ratio 1.05-1.91x, but ALREADY FILED on the bench's own side as [OS-4]
  ("the match-compliance regime artifact") — not a fresh [SEL-COST]
  finding, and it is the majority of the raw "wins" population, so a
  naive count would have overstated the prize ~6x.
- **B — class-run DFA pointer-chasing.** `cls-w`/`mod-a`/`cls-posix`/
  `unp-p-lc`, 8 cells, 1.08-1.38x. ALREADY FILED — the same mechanism
  `docs/dev/opt5_step0_profile.md` measured at 5-6x on its own witness.
- **A — anchored/bounded-position DFA fixed per-call cost.** 12 cells
  (start-anchor trio + end-anchor trio), 1.05-1.27x. NEW, small, single
  direction — a plausible near-term fixed-cost fix.
- **C — hybrid DFA-front-prefilter cost mispriced against the plain
  `req_byte`/`req_run` precheck it suppresses.** 34 cells (17 patterns),
  NEW and genuinely open: 11 cells are forced-VM wins (1.04-1.62x), 22
  are strong auto wins (1.09-14.68x) — the SAME compile-time pattern
  signature wants opposite answers depending on call regime, and one
  pair (`lka-pos`/`lka-neg`, identical stamps) flips by subject match
  density alone. This is the boundary any real selection term has to
  clear.

## What the doc recommends

States the compile-time-vs-runtime split explicitly (every distinguishing
fact used above is compile-time; the regime and subject shape are not),
and recommends the mechanism's SHAPE only — a first-match predicate-row
table keyed on compile-time pattern signature, valued per assumed call
regime (an `[OPT-DIAL]`-style knob), rather than a single build-time
constant. Does not design the mechanism.

## Bench context folded in

O-74 ([FINDINGS] B115 ledger): email-specimen's `floor`/`orig`
whole-subject compliance cells read ×0.648/×0.856 forced-VM-vs-auto —
same shape as cause D, different (larger) corpus, corroborating.
O-63 finding 5: syntax's own `grp-cap`/`grp-named`/`grp-named-quote`
and `rec-*` whole-subject cells, read caps-vs-nocaps (a DIFFERENT
question, D119/I-99 forbids ranking it) — but pointing the same
direction as this census's own within-caps bucket C on the identical
three patterns.

## Questions for the bench dev (docs/dev/sel_cost_census.md, final section)

1. No forced-`nocaps`-VM testee in `syntax@0.1` — the nocaps population
   has no non-auto comparator today.
2. No forced-`--engine=dfa` testee — the reverse population (auto picks
   VM, does forced DFA win) is unmeasured.
3. Whether the bench's subject generator exposes match density for the
   `lka-pos`/`lka-neg` pair, to confirm the subject-shape hypothesis
   directly rather than infer it from pattern text.
4. Whether the four borderline (1.03-1.23x) `short-subject-search` cells
   this census flagged sit above O-69's per-launch bimodality floor.

## Validation

Docs-only lane; no build applicable. `git log --oneline -1`:
`789144e2 [SEL-COST] STEP 0: exhaustive syntax-subbench read, cause-grouped`.
Reproduction scripts run cleanly against a fresh `pcrec-bench` checkout
per `docs/dev/sel_cost_census/CLAUDE.md`'s run order (note: `extract_patterns.py`
needs Python 3.11+ for `tomllib`, which this dev box's default `python3`
lacks — used `/Users/fdicostanzo/miniconda3/bin/python3.11`).

## Handback

Committed on `lane/selcost0`. Nothing owed. Ready for review/merge.
