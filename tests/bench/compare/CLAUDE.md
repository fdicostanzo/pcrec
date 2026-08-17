# tests/bench/compare — cross-engine comparison matrix and its ratchet

Produces the numbers this project quotes about itself: pcrec against
PCRE2-interp, PCRE2-JIT and python `re` over a fixed case matrix. Slow (tens of
minutes, full matrix), so it is run deliberately — before and after any
performance-relevant change — rather than from a make target.

## Files

- **compare.sh** — the matrix. Pins to a core, repeats `BENCH_TRIALS` times per
  engine/case, reports medians and max/min spread, verifies every case's match
  span against an oracle, and emits a machine-readable TSV block plus a
  `results-<host>-<date>.md` write-up.
- **eng_pcrec.c**, **eng_pcre2.c**, **eng_py.py** — the per-engine drivers.
- **gate.sh** — the ratchet over compare.sh's own pcrec numbers. `UPDATE=1`
  rewrites floors.tsv (and appends to run_history.tsv); `EARN=1` reports
  (never applies) a margin run_history.tsv can justify per case (R3.7).
- **floors.tsv** — per-case reference value AND per-case margin.
- **run_history.tsv** — accumulated independent runs, one row per (run, case),
  seeded from the two results-\*.md snapshots and every `rebaseline.sh` /
  `gate.sh UPDATE=1` run since (R3.6/R3.7). What `EARN=1` and `rebaseline.sh`
  read to decide whether a case has "enough" independent data yet.
- **rebaseline.sh** — the re-baseline MECHANICS for a single floors.tsv case
  (R3.6): runs `compare.sh` N times for one case, checking load before/after
  each run, appends to run_history.tsv, and reports the cross-run median —
  it does not write floors.tsv itself.
- **results-\<host\>-\<date\>.md** — captured baselines.

## Conventions

**The floors are machine-specific.** On new hardware, regenerate with
`UPDATE=1 bash gate.sh` and treat that as re-baselining, not as a comparison.
Never widen a margin to make a red run green; journal the change instead.

The gate deliberately checks pcrec's ABSOLUTE numbers, not ratios against the
other engines: a ratio moves when PCRE2, python or the box changes, and R2-B1
showed those ratios flipping sign run to run.

Margins are per case, derived from that case's own trial spread as
`clamp(1/(spread*1.05), 0.70, 0.90)` (R3.5). One global 0.70 fires only below
1.43x, which is how M2.10's 27% regression passed this gate while the review
credited the gate with catching it. The ceiling is fixed rather than derived
from a single run's WITHIN-run spread, which is a sample, not a distribution.

CORRECTION (R3.7, 2026-08-11): this file used to justify the 0.90 ceiling with
"the box's noise floor is ~10% no matter how tight one run looks" — that
number was never backed by any measurement in this repository (also corrected
in gate.sh and floors.tsv; D17 in docs/dev/decisions.md still needs the same fix).
The ceiling stays at 0.90 regardless: `run_history.tsv` (one row per case per
independent `compare.sh` run — see `rebaseline.sh`) and `gate.sh`'s `EARN=1`
mode are the honest path to tightening it, and as of this correction every
case still has fewer than `EARN_MIN_RUNS` (default 8) independent dates of
history, so nothing has been earned yet. Each run still prints, per case, the
smallest regression its margin can catch.

Two known gaps, carried deliberately: case (d) matches at 0.99% of its buffer
so its "throughput" is exit latency (R2-B4, fixed in run_bench's sibling case
but not here), and gate.sh has no minimum-coverage floor beyond requiring that
every floor row was measured.

**Case (j), added [M4.6b] (2026-08-17), is the one case in this matrix that is
CAPTURE-BEARING on purpose.** `([01]*)1([01]{8})` is DD-9's capture-bearing
sibling of case (f) — engine_m4.md §8.5's non-regression floor for the
VM+prefilter hybrid: capture groups route pcrec off (f)'s pure DFA and onto
the hybrid (confirmed per-run from the compiled artifact's
`rx_info.engine == ENGM_VM` and a non-NULL `engine_why`), which is exactly
the shape most likely to embarrass it — the DFA prefilter finds a span
covering the whole 8 MB buffer (span/subject ratio 1.0, §6.2(a)'s stated
worst case), so the VM then re-walks essentially all of it a third time.
Floor derivation (floors.tsv): three independent quiet-box `CASES=j` runs,
150.350/150.369/150.397 MB/s, spreads 1.00x-1.01x — reference is the median
(150.369), margin is the standard R3.5 formula
(`clamp(1/(spread*1.05), 0.70, 0.90)`) at the worst of the three spreads,
which clamps to the 0.90 ceiling like most other rows here. Every other case
in this file is deliberately span-only (see the Scope disclosure section of
README.md); (j) is the sole exception and README.md's disclosure is worded
to say so.

**FINDING, not fixed here (M4.6b, 2026-08-17): cases (c) and (i) were already
silently measuring a different engine than their floors were set against, the
same D46 story `run_bench.sh`'s case (d) already lived through.** A full
10-case `gate.sh` run after adding (j) — box quiet throughout, 1-min load
0.56 start / 1.16 end against a 6.00 limit, `results-ubuntubudu-20260817.md`
— failed case (c): measured 251.429 MB/s (spread 1.02x, re-confirmed at
242.510 MB/s on a fresh isolated `CASES=c` run moments later) against a
349.754 floor, a real and reproducible ~1.5x drop from every prior recorded
run of this case (384.880-390.344 MB/s across 2026-08-09/2026-08-11). This is
NOT caused by the (j) edit — (c)'s subject bytes are drawn from the shared
`rng` at the identical point in the sequence as before (the new (j) subject
block is appended strictly after (i)'s), and (c)'s pattern, build flags and
driver are untouched.

The cause: `(alpha|beta|gamma|delta|epsilon)` (case (c)'s pattern, and the
IDENTICAL pattern text `run_bench.sh` pinned to `--no-captures` for exactly
this reason) has one incidental capturing group, so under D42.1
(captures-on-by-default, landed 2026-08-14) it now compiles to
`rx_info.engine == ENGM_VM` (confirmed directly: `engine_why` = "capture
group at pattern offset 0") — the VM+prefilter hybrid — where it compiled to
`ENGM_DFA` when the 388.615 floor was captured (2026-08-09/11, before
D42.1). Case (i)'s pattern `a(b|c)+d` has the same problem (`engine_why` =
"capture group at pattern offset 1") and shows the identical symptom at a
smaller apparent size only because its own margin is loose enough to absorb
it: latency drifted 83.36 -> 105.48 ns/call (a ~26% regression, same
direction) but still clears its 119.086 ns/call limit, since case (i)'s
margin was set at the D17/R3.6 floor (0.700, the widest in this file) for
unrelated noise reasons before D42.1 existed. **No case in this file besides
the deliberately-added (j) was ever pinned against engine drift the way
`run_bench.sh` pinned its own case (d) and (c) here** (see that file's own
"D46/D42.1" comments for the precedent and the fix shape: `--no-captures` on
the affected pattern, if the intent is still to measure the pure DFA). Left
for the manager to rule on — out of M4.6b's mandate (add case (j) with its
own floor), and the fix is a design decision (pin (c)/(i) to `--no-captures`
to restore their original DFA-only intent, vs. accept new floors that measure
what ships by default) rather than a mechanical one.

**Suspect-window fact for the bisect: case (c)'s artifact stamps the
VM/hybrid path, not the DFA path.** `rx_info.engine` is `ENGM_VM` (2), not
`ENGM_DFA` (1); `RX_ENGINE_WHY` / `engine_why` reads "capture group at
pattern offset 0". So whatever moved (c) from ~388 MB/s to ~245-251 MB/s
lives on the VM/prefilter side of the split (D42.1 onward: possessify,
revdet, counter-K), not on the pure-DFA side (K18's closure rewrite is a DFA
change and both cases' artifacts never touch that code path at all — they
were never on it before D42.1 either, since D42.1 is precisely what moved
them off ENGM_DFA).

**Also worth the manager's attention: `floors.tsv`/`gate.sh` are not in any
battery leg.** `make bench` runs only `run_bench.sh`'s separate suite (see
this directory's own README/CLAUDE.md); `compare.sh`/`gate.sh` here are
deliberately manual — "Slow (tens of minutes, full matrix), so it is run
deliberately... rather than from a make target" per this file's own opening
line. That is exactly how (c)/(i) went three days (2026-08-14 to
2026-08-17) with a floor silently measuring the wrong engine and nothing
red anywhere — the same instrument-outside-the-battery shape as the
fuzzer-red incident this project already has a name for. Whether `gate.sh`
should join a battery leg (even a manual/checkpoint one, given its own
"tens of minutes" cost) or just get an explicit "ages freely, re-run before
trusting" marker is a call this finding raises but does not answer.

Maintenance: update this file when cases, engines or gating rules change.
