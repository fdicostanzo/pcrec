# docs/dev/optloop/c2/ — cycle 2's PREPARATION artifacts (lane c2prep)

The scripts, raw censuses and probe sources behind the three cycle-2
preparation documents one directory up (`firstset_design.md`,
`reqpos_census.md`, `onepass_census.md`).  Reproduction pieces, not a
runnable harness for anything else: each takes its inputs from the
environment and writes nothing outside the directory it is pointed at.

**Nothing here times anything.**  Every number is a COUNT.  The lane ran
on darwin, where `docs/dev/xarch_step0.md` and D119's own mechanics rule
timing uncitable; where a fact needs a clock it is written as OWED to the
Linux executor, never estimated here.

Everything is read-only with respect to `/Users/fdicostanzo/pcrec-bench`:
the throughput subjects are REGENERATED from its own `captext.py` into a
scratch directory and verified against the SHA-256 values
`../cycle1_analysis.md` setup 0.3 pins.

## Files

- `subject_freq.py`, `subject_freq.json` — the bench throughput subjects'
  byte and literal-RUN census.  Shared input to `firstset_design.md`'s
  cost model (a candidate set's summed byte frequency) and to
  `reqpos_census.md`'s tier-2b half (how rare a PAIR is against the
  single byte).  Run: `SUBJ=<dir> python3 subject_freq.py`.
- `scanloop_sim.py` — a COUNTING replay of the emitted unanchored DFA
  scan loop, reading the tables straight out of an emitted `.c` so the
  machine is pcrec's own.  Reports state-0 residency, skip-loop entries
  and BYTES ACTUALLY SKIPPED under the artifact's own candidate table or
  a substituted one.  This is what `firstset_design.md` §3 uses to show
  that M3.c's `json-constant` twin did skip 74.57% of the subject — so
  "the skip loop never ran" is refuted as the explanation of its
  regression.  Requires `RX_DFA_TABLE "premultiplied"` (today's default).
- `reqpos_probe.c` — `[OPT-REQPOS]`'s POSITIONED necessary-byte walk: it
  extends `src/opt/reqbyte.c`'s set and pick rules (batch 1, `lane/optimpl1`)
  with the tightest offset interval at which the necessary byte sits and the
  longest necessary literal RUN with its own interval — which is what the
  row's tiers 1 / 2 / 2b / 3 are defined against.  Links `libpcrec.a` and
  drives the REAL parser, `pcrec_altcls`, `pcrec_discharge_atomic` and
  `pcrec_lower_enc`.  Its header states the three known false NEGATIVES and
  the two build-time findings that shaped it (the `A_CAT` spine must be
  walked iteratively; the pipeline prefix must include every REWRITING pass
  above the analysis's own call site).  Build:
  `gcc -O2 -Ilib -Isrc -o reqpos_probe reqpos_probe.c build/libpcrec.a`.
- `reqpos_census.py` — the census driver: builds the two populations, runs
  the probe, cross-checks against batch 1's `RX_REQ_BYTE` stamp and joins
  the bench rows against the subject census.  Env: `PCREC PCREC_B1 PROBE
  BENCH CORPUS SUBJ OUT`.  It writes a scratch JSON; the COMMITTED form is
  the TSV below.
- `reqpos_census.tsv` — the census itself, 8,137 rows over three
  populations (`bench`, `corpus`, `corpus_utf8`).  Header comment states
  the column meanings and the `dmax = -1` convention.
- `reqpos_crosscheck.txt` — the cross-check's own result: 63 checked, 63
  agree, 0 disagree, 1 skipped.  It is the reason the TSV's `req_byte`
  column can be cited as batch 1's own fact.
- `reqpos_report.py`, `reqpos_tiers.txt` — the tier tables
  `../reqpos_census.md` §2/§3 carry, and their rendering.
- `reqpos_losing_join.txt` — the join against `../cycle1_rows.tsv`'s 34
  losing cells (§3's tables).
- `run_selectivity.py`, `run_selectivity.txt` — tier 2b's own number: each
  necessary run counted as a literal in `t-1m` against its rarest member
  byte.  Scoped to `capability` when read, since the other sets' regimes use
  their own subjects.
- `onepass_probe.c` — the throwaway ONE-PASS predicate
  (`../captures_via_dfa_survey.md` §3.6 M-A): pairwise-disjoint `FIRST` sets
  at every alternation, a repeat whose exit the next byte alone decides, and
  a hard refusal on lookaround / backreference / subroutine call.  Its header
  states the three known false negatives, records that there are NO known
  false positives (the direction a reach gate depends on), and carries the
  `pcrec_altcls` finding.  `-no-factor` denies both altcls axes so the
  precedents' own criterion is readable off the same instrument.
- `onepass_census.py`, `onepass_census.tsv`, `onepass_summary.json` — the
  three populations the survey names, their per-row verdicts and the summary
  `../onepass_census.md` is written from.

## `[OPT-FIRSTSET]` §4.6's reconciliation pieces (lane `fsreconcile`, 2026-09-22)

The instruments behind `../firstset_design.md` §4.6, which re-opens §4's
soundness finding against the REAL compiled two-pass `rx_search` rather than
against `scanloop_sim.py`'s forward-only replay.  **Every one of them is
answer-only; none reads a clock.**

- `firstset_witness.c` — the witness driver: one subject per line, the
  artifact's own find-all loop, every SPAN printed.  Spans rather than a
  count because the question has three answers a count cannot separate (a
  LOST match, a SPURIOUS one, a match at the wrong span).  The emitted prefix
  is a build parameter (`-DART_SEARCH=`/`-DART_NCAPS=`), which is what lets
  the same file drive an artifact emitted at any `-p`.
- `firstset_exhaust.c` — the exhaustive comparator: every string of length
  0..L over an alphabet through all THREE artifacts in ONE process, and it
  CLASSIFIES each disagreement by direction, since the direction is the
  finding.  The three link together only because they are emitted at three
  different `-p` prefixes (`rx`/`tw`/`rs`) and hand-edited afterwards.
- `firstset_witness.sh` — the runner that produces both from a pcrec build
  and nothing else: emits the three variants per pattern, applies the
  narrowing and §4.4's re-seed through two asserting Python patchers (the
  asserts are the STOP signal if the artifact's shape has moved), then runs
  the 72-subject structured set and the two exhaustive sweeps.  Env:
  `PCREC`, `CC` (default `gcc-16`), `OUT`.
- `firstset_witness_results.txt` — that script's own output as measured on
  darwin: 9 of 72 structured-set disagreements (all LOST matches, all in the
  word-context cell), 0 for the re-seed, and 552 / 0 / 0 by direction over
  4.03M exhaustively compared subjects.
## M-B reduction pieces (lane `mbread`, 2026-09-23)

- `onepass_mb.py`, `onepass_mb.tsv` — the reducer for `../onepass_census.md`'s
  "M-B — measured" section: turns pcrec-bench lane `b76optloop`'s raw
  arm1 (`--features all`)/arm2 (`--features all --no-captures`) `ns/byte`
  lines (`docs/dev/lanes/b76optloop_report.md` block (C), pcrec-bench
  commit `efec5366`) into a per-(pattern, subject) VM-pass share
  `(arm1-arm2)/arm1`, per-pattern medians, the population median/IQR, and
  a regime split (throughput vs. match) since `captures_via_dfa_survey.md`
  §3.6's own decision rule uses different thresholds for each. The
  17x4-cell table is hardcoded in `RAW_TABLE` (the bench report presents
  it as markdown, not a machine-readable file) — a re-run against a new
  bench report edits that constant. Re-run: `python3 onepass_mb.py`
  (regenerates `onepass_mb.tsv` in place). Reads no clock itself (the
  bench lane already did the timing); this is a pure reduction.
- `skiproute_census.py`, `skiproute_census.tsv`, `skiproute_summary.json` —
  THE ROUTE CENSUS, which is what makes §4.6.3's general argument a count
  rather than an argument: every shipped `.rxt` pattern line compiled at
  `--features all -p rx`, cross-tabbed `RX_ENGINE × RX_DFA_PREFILTER ×
  RX_DFA_START × RX_VM_PREFILTER`, with three facts read off the EMITTED TEXT
  (does it carry a skip, a reverse walk, a seeded start).  Headline: 0 of
  3,535 compiled artifacts run a skip with no reverse walk, 0 of 217
  `pinned` artifacts carry any prefilter, and the narrowing's real reach is
  54 artifacts (42 plain DFA, 12 VM hybrid).  Its own first detector is
  documented in place as a [MECH-REACH] instance — it required the reverse
  TRANSITION TABLE, which [CC-DIFF] STEP 1's uniform fold is allowed to
  delete while the reverse WALK stays, and read 84 false positives.
