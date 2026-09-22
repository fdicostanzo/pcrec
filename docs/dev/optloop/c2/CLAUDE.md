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
