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
