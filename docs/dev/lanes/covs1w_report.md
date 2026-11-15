# covs1w report: triage of the RED covs1-sweep (lane/covs1 @ 65ad7d226)

## STATE AT HANDOFF

Rulings file `covs1w_rulings.md`: empty; last R-n applied: none. Branch lane/covs1, no `src/` change,
abi stays 108. Files touched: `docs/dev/lanes/covs1_evidence/job_sweep` (exit contract),
`docs/dev/lanes/covs1_evidence/sweep_verdict.py` (new), `docs/dev/lanes/covs1_evidence/predict.py`
(row check), this report, `covs1w_deliver.txt`. `scripts/emit_sweep.py` NOT touched (no tool defect).
Queue: `200-covs1-sweep` re-added with `boxqueue add --name` (the 20:00-01:00 hold stays in the job's `--ready`);
`200-covs1-predict` (pending, unchanged script, reads the live predict.py) waits on key `covs1-sweep`, so it
follows the re-added job. No STOP: 0 lost covers, 0 unexplained movers, 0 unexplained rows.

## CAUSE

The red was the sweep's OWN exit contract, not a regression. `emit_sweep.py` exits 1 whenever any mover exists
(`sys.exit(0 if overall_ok else 1)`, line ~4044), and the job `exec`'d it, so any branch that is supposed to have
movers could never turn the sweep green and `covs1-predict` (which waits on the sweep being green) could never run.
The movers themselves are the design's predicted GAINED covers: a pattern that now compiles to a cover leaves the
DFA scan route, so the route rows (`RX_DFA_SCAN/PREFILTER/START`, `end_window`, `width`, `req_*`, `run_pin`,
`land_char`, ...) change, which `--facts-declared-moves 'span_facts:row:gone>,cover:section:>new'` cannot declare
(it declares only the two items; §5.2 says every other row keeps its guard, and movers are the predicted list).
Question (4): "DECLARED MOVES patterns=1 rows=2" is the DUMPS stream's line (`--list-limits` gone row + `desc`
cell). The FACTS stream's own line reads `patterns=6513 rows=13026` (span_facts gone + cover section new on every
compile that reached): the declaration is spelled correctly and counts what it should.

## MOVERS

Population of the sweep: `enumerate_corpus`, 7071 corpus rows = 5516 distinct patterns, both encodings in the
facts stream. The design census (§2) used `bench_pop()+corpus_pop()` (11,738 compiles); the two populations are
different, so counts relate only through each tool's own baseline decisions (below).

| stream | movers (keys) | distinct patterns | predicted gained covers | other |
|---|---|---|---|---|
| c-default | 15 | 13 | 13 | 0 |
| facts | 15 | 13 | 13 | 0 |
| c-vm, emit-ir-vm, emit-ir-auto (4 arms), stderr, composition, dumps | 0 | 0 | - | 0 |

asymmetric = 0 in every stream. The 13 patterns (15 keys: two literals occur twice in `litrun.rxt`):
`ABCDEFGHIJKLMNOPQRSTUVWXYZabcde` (k=31), `...abcdef` (k=32); and 11 k=1 covers from
`tests/possessify/composition_d27.rxt`: `-{0,}?(?<!\W)-`, `a*(?<=A)b`, `a*\bA`, `(?:a*\b)*b`, `[a-c]*\ba`,
`[A-C]*\b[a-c]`, `[a-z]*\b[0-9]`, `\d*(?<=a)\w`, `\d{0,}?\B-`, `\W*(?<!\W)\w`, `\w*\b\w`.
predict.py (run over the real movers file): `lost=0 unexplained=0 unexplained-rows=0 unkeyed=0 gained-movers=13`.
Baseline decision census: byte exact/producer-short->cover 12, fixed-width->cover 1 (the k=32 literal),
utf8 10 + 1; also fixed-width->statement-fits 7 and ->exact/machine-inexact 3 per encoding (listing only, no artifact
moves). Compiles gained: byte 13, utf8 11 = 24 (4 are the long literals k>=25, 20 are k=1). For `-{0,}?(?<!\W)-`
and `\W*(?<!\W)\w` utf8 is not a cover (stays `finisher-dfa`); only `span_facts` and the new `cover` section move there.

Open count note (not a STOP): the design says "18 small covers gained" over ITS population; this corpus shows 20
k=1 gained compiles (11 patterns, byte 11 + utf8 9). Both are all predicted by the baseline `why`
(exact/producer-short), so nothing is unexplained, but the 18 vs 20 gap and that the design expected
producer-short = 0 (§3.1 R-9) while 12/10 exist are for the manager to relate to the design's census; I did
not re-run census.py.

## FIXES

1. `job_sweep` contract: the sweep tees its report and then `exec`s `sweep_verdict.py`, which is green iff the
   instrument ran to completion (self-check passed, DONE line, REAL RUN present, DELIVER witness OK, every tag
   floor held, all 11 streams reported, movers file written), asymmetric=0 everywhere, and movers appear ONLY in
   c-default and facts (the two streams a gained cover touches; a mover in c-vm, emit-ir, stderr, composition or
   dumps is red). It never judges WHICH patterns move. Tested: the failed log passes (rc 0); the same log with a
   forged `c-vm movers=2` fails (rc 1).
2. `predict.py` is the judge, now also of row kinds. For every observed mover it re-lists the facts of the
   BASELINE and CANDIDATE binaries and requires: some encoding GAINS a cover by the baseline-vs-candidate
   KITPROOF decisions (baseline `why` != cover, candidate cover); every moved row is `span_facts`, the new `cover`
   section (declared) or one of a declared ROUTE_ROWS table written in predict.py (not read from the candidate);
   and a route row moves only in an encoding where the candidate is a cover. Anything else prints
   `UNEXPLAINED-ROWS` and exits 1, as do LOST, UNEXPLAINED and unkeyed movers. The prediction (baseline why,
   wmin from the baseline listing) is independent of the candidate's output being judged. First run flagged
   `finisher-dfa` as a moved row: it is the `why` cell of the cover section's row, mis-keyed; fixed by keying every
   row of `#section cover` as `cover`. Limit: ROUTE_ROWS is a declared allowance, reviewed here against the 13
   movers' observed moves; widening it is a design-level decision. The sabotage-style negative for predict (a
   mover that is not a gained cover) was not planted; the sweep_verdict negative above was.

## OWED RUNS

- `200-covs1-sweep` (re-added; ~100 s of sweep after builds; green = `sweep_verdict: ... instrument ok`).
- `200-covs1-predict` (already pending; follows the sweep; green = `predict: DONE rc=0`, expect gained-movers=13).
Verdicts to read from the queue records; I did not wait.
