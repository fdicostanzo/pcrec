# covertime — [KIT-VERIFY] `measure`: harness-routed `cover` against default (lane covertime, sonnet, 2026-10-21)

Branch `lane/covertime` from main `aeb381c25` (Z2 merged). Measurement only: nothing under `src/`,
`cli/`, `lib/`. Instruments: `docs/design/kit_proof/measure/` (own CLAUDE.md). Rulings file
`docs/dev/lanes/covertime_rulings.md` re-read before each commit and before queueing: no entries.

## STATE AT HANDOFF

- Built and committed: subjects, the python-`re` answer gate, the timing driver, the table reader and
  the queue job `650-covertime-slot`. The job is QUEUED (`scripts/boxqueue status` names it).
- **OWED: the timing run.** It starts only when its `--ready` quiet gate passes (load1 < 2.0 on two
  samples at least 55 s apart, no running queue job, no box-lock holder). Its log is the queue run
  dir's `job.log` (`worktrees/.boxqueue/running/650-covertime-slot/`, then `done/` or `failed/`);
  the completion line is `== covertime COMPLETE rows=N launches=5`; the table is
  `<worktree>/build/covertime/table.md` (also at the end of `job.log`).
- Verified now, with no clock: **PREMISE.** All 8 cells read `RX_DFA_SCAN "cover"` on the
  harness build (`--harness=kit-proof --features all`) and none reads it on the default build
  (`build/covertime/cover_stamps.tsv`: DEF and AA `unanchored`, COV `cover`). The brief's stop rule
  (fewer than 4 cells read cover) does not fire. **ANSWER GATE: 216 arm cells (3 arms x 72 subjects)
  all equal to python `re`** (`measure.sh smoke`, and `--dry-run` repeats it).
- NOT a reading: one throwaway calibration launch (`measure.sh calib`, T = 2 ms, N = 3) ran while
  other queue jobs held the box (load1 15). It exists only to size the cap. Its direction is worth
  knowing so the real table is not a surprise: COV was SLOWER than DEF by a large factor on every
  sparse `throughput` and `search_short` cell and FASTER on `dense`. The reason is visible in the
  artifact text: on `lit-l8` the cover `rx_search` is the kit's REPORT text, a byte-at-a-time
  compare loop at every position (`RX_DFA_PREFILTER "none"`, `RX_MEMFN_LIBC "none"`), where
  DEF has the `run-pinned` prefilter with `memchr`. Do not quote any calibration number.

## What was measured (design)

| item | choice |
|---|---|
| cells (8) | the four named in the brief, patterns from `docs/dev/kvcensus/patterns.tsv.gz`: `lit-l8` `abcdefgh`, `year4` `\d{4}`, `file-ext-order` `\.tar\|\.tar\.gz`, `hex8-bounded` `\b[0-9a-f]{8}\b`. Four more from `tests/kitproof/cases.tsv`'s `verdict ... cover` rows (the admitted population Z2's own check holds), one per shape the first four lack: `foobar` (plain literal), `\bcat\b` (boundary-bounded literal), `(?m)done$` (line-anchored literal), `\w(?=\d)\w` (lookahead-bearing class pair) |
| arms (3) | DEF = `build/pcrec`; COV = `build/pcrec-harness --harness=kit-proof`; AA = `build/pcrec` again, a separate compile and link of the same source (the A/A floor). All `--features all`, `-p rx`, then `gcc -O2`, static link with the same `cdrv.c` |
| regimes (3) | `throughput`: match_api.md section 3.1.3's find-all over a ~1 MiB subject (ns per find-all). `search_short`: one `rx_search` from 0 per short record, 1024 records of 32-160 B (ns per pass of 1024). `match`: one anchored `rx_match` at 0 per record. These are this lane's own definitions; the bench's regimes are not read (brief: do not read pcrec-bench files), so the names are the bench's and the shapes are a stand-in |
| subjects (3 per cell) | generated, deterministic (`random.Random` seeded from cell and class; no clock, no file read). `real`: the cell's natural text (prose, a path listing, log lines) with the match planted at a sparse natural rate plus near-misses that must not match. `none`: the same filler and near-misses, zero matches (asserted). `dense`: matches back to back. Records are cut from the class's raw text, a quarter of `real` records cut to contain (`search_short`) or start at (`match`) a match; `none` records are re-cut until they hold no match (a cut can create one) |
| timing | one core pinned with `taskset` (cpu 7; its SMT sibling cpu 15 idle, load of both read at each launch start and at the end), 5 launches; per launch, per (cell, regime, class), the three arms once each in an order rotated each item; each arm calibrates reps so a sample takes >= 20 ms, takes 9 samples, reports the median; datum = that median per launch. Per (cell, regime, class, arm): median and IQR (inclusive quartiles) over the 5 launches |
| gate | before any clock: for every cell, class and regime all three arms print `ops N hits H hash X` equal to python `re`'s (the same loop, search from p, p = end). Any difference: exit 3, `== covertime GATE FAILED`, no timing |

Standing questions (`docs/design/CLAUDE.md`): the measurement regime is the whole point (hit versus
miss, short versus long, one core, Zen 4 box, gcc 15.2 -O2); the independent control is python `re`
for answers and the A/A arm for noise; regenerating data moves nothing (no committed data, `build/`
is gitignored).

## The table to fill in

`python3 -I docs/design/kit_proof/measure/read.py <worktree>/build/covertime` prints it (the job
already did; the same text is the tail of `job.log` and `build/covertime/table.md`). Format:

| cell | regime | class | matches | DEF ns [IQR] | COV ns [IQR] | AA ns | COV/DEF | AA/DEF | floor | reading |
|---|---|---|---|---|---|---|---|---|---|---|

`matches` is the throughput match count, or hits/records for the short regimes. ns is per PASS, so
for the short regimes ns/op = ns / 1024. Then the per-regime summary (geometric mean COV/DEF by
class, counts of FASTER/NULL/SLOWER), the FINDINGS list and the A/A floor.

## The reading rule

Per row, with `med` and `IQR` over the 5 launches:

- `R = med(COV) / med(DEF)` (below 1 means cover is faster); `AA = med(AA) / med(DEF)`.
- `floor = max(|AA - 1|, IQR(DEF)/med(DEF), IQR(COV)/med(COV), 0.02)`. The 0.02 is an UNMEASURED
  default (D149), there so one lucky row with a zero IQR and AA = 1.000 cannot call a 0.5% move.
- `reading = FASTER` if `R < 1 - floor`; `SLOWER` if `R > 1 + floor`; else `NULL`.
- **A cell where cover is `SLOWER` beyond its floor is a FINDING.** It goes in the report with the
  cell, regime, class and ratio, whatever the geometric mean says.
- The question to answer from the table: does cover make users' searches faster (which regimes and
  classes read FASTER, by how much: the `real` rows are the realistic ones, `dense` is the case
  the kit's saving is per match, `none` is the pure scan), and where does it lose (every SLOWER row).
  `design/kit_proof.md` section 8.1 predicts a sparse `throughput` cell reads near null; a SLOWER
  there contradicts that.
- A run is READABLE only if the log shows: the gate passed, `== covertime COMPLETE rows=1944
  launches=5` (8 cells x 3 regimes x 3 classes x 3 arms x 5 launches), the A/A median |AA/DEF - 1|
  small (the table's last section; a median above 0.03 means the box was not quiet, re-queue),
  and the launch-start lines show load1 < 2 and sibling busy near 0. A launch whose start line
  shows otherwise is NOISY: say which, and re-queue the job (`scripts/boxqueue retry`).

## How to read the verdict (for the fresh agent)

1. `scripts/boxqueue state covertime-slot` and the run dir's `result` line; green needs
   `done=1`.
2. `scripts/verdict <job.log>`; then the log's `== covertime COMPLETE` line and the table.
3. Fill the report's `RESULT` section below from the table: the per-regime geometric means, the
   FINDINGS list, a one-line GO / NO-GO input for B1 stated as the numbers (the verdict is the
   manager's; the official one is the bench's, D144 addendum 4).

## RESULT

Read 2026-10-21 by lane coverread from job `650-covertime-slot` (`outcome=green rc=0 wall=229s`).
Rulings file `covertime_rulings.md`: no entries ("none yet").

**Readable: yes.** Gate passed (`216 arm cells ... all equal to python re`, before any clock);
`== covertime COMPLETE rows=1080 launches=5` (the reading rule's "rows=1944" is an arithmetic slip:
8 x 3 x 3 x 3 x 5 = 1080); launch-start lines load1 0.89-1.00, cpu7 0.0%, sibling cpu15 0.0-1.0%, end
sibling 0.5% (no NOISY launch); A/A |AA/DEF - 1| median 0.001, p90 0.005, max 0.017 (below the 0.03
bar). Run-to-run spread is small: nearly all IQRs are under 1% of the median; the largest are
hex8-bounded throughput (COV IQR 1.6%), word-digit throughput dense (COV 2.4%), done-eol throughput
dense (COV 1.7%), year4 search_short none (COV 3.3%). Every SLOWER/FASTER reading clears its floor
(0.020-0.040) by a wide margin except the near-edge rows (year4 match real 0.957, foobar match none
0.927 FASTER).

### Per regime (geomean COV/DEF; FASTER/NULL/SLOWER of 8 cells)

| regime | real | none | dense |
|---|---|---|---|
| throughput | 2.083 (2/0/6) | 2.149 (2/0/6) | 0.573 (7/0/1) |
| search_short | 1.932 (1/0/7) | 2.463 (1/0/7) | 0.449 (7/0/1) |
| match | 0.991 (1/7/0) | 0.986 (1/7/0) | 1.002 (0/8/0) |

Totals: throughput 11 FASTER / 0 NULL / 13 SLOWER; search_short 9 / 0 / 15; match 2 / 22 / 0.
**28 FINDINGS** (every SLOWER row; the list is the table's FINDINGS section: 13 throughput + 15
search_short, 0 match).

### Per cell (COV/DEF; real / none / dense)

| cell | throughput | search_short | match |
|---|---|---|---|
| lit-l8 | 9.91 / 10.46 / 0.289 | 3.86 / 6.26 / 0.332 | NULL x3 |
| foobar | 7.49 / 7.81 / 0.319 | 3.98 / 5.21 / 0.318 | NULL, FASTER 0.927 (none), NULL |
| file-ext-order | 3.73 / 4.13 / 0.953 | 2.84 / 5.05 / 0.372 | NULL x3 |
| cat-bounded | 1.35 / 1.21 / 0.407 | 2.03 / 2.49 / 0.342 | NULL x3 |
| done-eol | 1.27 / 1.33 / 0.468 | 1.21 / 1.97 / 0.355 | NULL x3 |
| year4 | 1.21 / 1.33 / 0.740 | 1.42 / 1.74 / 0.508 | FASTER 0.957 (real), NULL, NULL |
| hex8-bounded | FASTER 0.908 / FASTER 0.925 / SLOWER 1.317 | 1.56 / 1.31 / SLOWER 1.172 | NULL x3 |
| word-digit | FASTER 0.681 / 0.679 / 0.709 | FASTER 0.818 / 0.735 / 0.580 | NULL x3 |

(Unmarked numbers in `real`/`none` columns of the other cells are SLOWER; `dense` unmarked are
FASTER.) Cover is FASTER on `dense` for throughput and search_short in every cell except
hex8-bounded (SLOWER 1.317 and 1.172). Only word-digit (the lookahead-bearing class pair) is FASTER
across every throughput and search_short class. `match` is NULL or within ~7% everywhere; no SLOWER.

### The prediction (cover `rx_search` has no memchr, slow on sparse subjects): CONFIRMED

The cells where DEF has a literal prefilter (lit-l8, foobar, file-ext-order) lose most on the
sparse classes: lit-l8 `throughput` real/none 9.9x / 10.5x (65.6 us -> 650 us per ~1 MiB find-all,
about 0.62 ns/byte for COV against about 0.06 ns/byte for DEF), foobar 7.5x / 7.8x, file-ext-order
3.7x / 4.1x; `search_short` none 6.3x (lit-l8), 5.2x (foobar), 5.1x (file-ext-order). `none` is worse
than `real` in every one of those cells (pure scan). The same cells flip to FASTER on `dense`
(lit-l8 0.289, foobar 0.319, file-ext-order 0.953 throughput; 0.32-0.37 search_short), where the
per-match saving dominates. Cells without a literal prefilter in DEF (year4, cat-bounded, done-eol,
hex8-bounded) lose far less (1.2-2.5x), and word-digit wins. This lane did not read the emitted
text; the "byte compare, no memchr" mechanism is the handoff's artifact reading, consistent with
these timings but not proven by them.

### Against `design/kit_proof.md` section 8.1

Section 8.1 predicts a sparse `throughput` cell reads near null. It does not: of 16 sparse
(`real`/`none`) throughput rows, 12 are SLOWER by 1.2-10.5x, 4 are FASTER (hex8-bounded 0.91-0.93,
word-digit 0.68), and none reads NULL. The prediction is contradicted.

### GO / NO-GO input for B1 (numbers only; the ruling is the manager's)

By the reading rule, cover as routed by the harness build on this population is not a net win:
sparse `throughput` and `search_short` (the realistic and pure-scan classes) are SLOWER in 6 and 7
of 8 cells for `real` and for `none` alike, geomean 2.08 / 2.15 (throughput) and 1.93 / 2.46
(search_short); the broad wins are `dense` (geomean 0.57 throughput, 0.45 search_short) and one cell
(word-digit). `match` is neutral (geomean 0.99, 22 of 24 NULL). The rule makes any SLOWER cell a
FINDING whatever the geomean; there are 28. Read plainly, the numbers read NO-GO for turning the
cover proof on by default as the harness build routes it today. Scope: 8 cells (4 from the brief, 4
from the admitted cases); one machine (Zen 4, one pinned core, gcc 15.2 -O2); the official verdict
is the bench's (D144 addendum 4).

## Notes

- Cap 900 s, sized from the small calibration: 4.5 s for one launch at T = 2 ms, N = 3 (216 timed
  arm cells, mostly process overhead); the real run is 5 x (4.5 + 216 x (N + 1) x 20 ms) = about
  240 s, times 3 for slack, plus the cached build and gate.
- The queue's `--dry-run` has a 30 s bound, so the build and gate are cached by a key of
  `build/pcrec`, `build/pcrec-harness`, `cdrv.c`, `cells.tsv`, `gen_subjects.py` and the gcc
  version; a changed input rebuilds (about 60 s) inside the work, not the dry run. The first,
  uncached build and gate ran during this lane, single core, before any clock.
- Multi-core work: none. The build is sequential `gcc` calls; the one calibration launch was
  pinned to cpu 7 while the box was loaded by other lanes' `make test` jobs, not by a timing
  window.
- Facts only to the kit (D157): nothing here proposes a kit method.
