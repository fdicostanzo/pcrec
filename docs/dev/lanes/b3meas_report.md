# b3meas — B3 (the match-end mark on rev-end) measured: loads and ns/call, today vs a B3 hand twin

Lane b3meas, 2026-10-12, main `32141d473` (abi 76), Linux dev box (7700X, gcc 15.2 `-O2`). No `src/` change. Evidence:
`docs/design/endmark/b3meas/` (`gen.py`, `harness.c`, `probe.c`, `report.py`; `results/report.txt` holds every table below).

## Verdict
B3 saves a pass **where the subject ends in `\n` and the artifact can tie**: 30 of the 139 distinct byte artifacts twinned
(14+21 rows of the 266; 1 of 9 bench, `tail-space-eol`). That is exactly the per-line regime: a line with its `\n`.
There it cuts loads 2.4-3.0x and time **2.4-2.5x (about 10 → 4 ns/call)**. When X spans the subject the saving is a
whole pass: `(?s)(.+)$` on 1 MiB goes from 622 µs to 213 µs. Everywhere else (the 109 no-tie artifacts, or no final
`\n`), B3's own effect is 0.95-1.16x. That is the dropped second-seed probe, 1-2 loads. Against it stands a machine
with 1.4-1.6x the states, which costs 5-10% on long walks without a `\n`. **Worth:** about 6 ns per line-shaped call
on tie-capable patterns, nothing material on the rest. The same win is reachable without tagging those 109
artifacts (§4). Separately, today's emitted walk is 1.04-1.40x slower than the SAME algorithm in plain table style.
That is as large as B3's whole effect on no-tie artifacts.

## Method
- **Population.** b3cost's rule reproduced: 266 rev-end `$`/`\Z` rows, 205 distinct. Five idioms added (`[ \t]+$`,
  `\.(?:txt|log)$`, `;\s*$`, plus the bench's `\s+$` and `\d+$`), and endmark.md §1.5's `(?:\s+|x\s*?)$` as the only
  state-dependent witness: no shipped pattern is state-dependent. The twin covers 139. Excluded: 44 with a context
  axis (`\b`, lookarounds), 16 utf8, 7 not a DFA rev-end. Capture rows were compiled `--no-captures` (their group-0
  artifact).
- **The twin B3.** It is today's file with `T_search` replaced by ONE walk from n over the tagged machine: the
  Moore-minimized product of pcrec's own reverse DFAs for `X\z` and `X\n\z`. At s*, one distance gives `n-d`. A tie
  gives `n-c` where `mark_prio` is const, else verify-at. `mark_prio` is classified EMPIRICALLY from libpcre2's choice
  on every tie in the check cells, which is B3's best case. All 30 tie artifacts read const (bounded X 12,
  unbounded 17; split by whether the tagged machine has a cycle).
- **The control R.** It is today's algorithm (two seeds, today's machine and views, verify-at), emitted in the
  twin's style (same table layout, run-skip on every self-loop state). today/R is code style. **R/B3 is B3's own
  effect.**
- **Answers.** Checked against libpcre2 10.46: 90,950,619 exhaustive cells (every start position, a 10-byte
  pattern alphabet, length ≤ 5), plus 11,635 regime subjects. 0 wrong for today, B3 and R. Loads are every
  `subject[...]` read (instrumented copy).
- **Regimes.** L = 40-200 B log-like lines. K4/M1 = 4 KiB / 1 MiB blobs with a varying last line. Each comes with
  and without a final `\n`, matching (m) or not (n) by libpcre2.
- **Timing.** `taskset -c 2`, 21 rounds in rotating order, ≥ 2 ms per measurement, back-to-back calls over the
  regime's 2-24 subjects (warm cache). The box carried other lanes on CPUs 12-15.
- **A/A floor.** today vs a separately compiled copy: class geomean 0.93-1.02, per-cell p5-p95 0.90-1.05. A second
  full run agrees: per-cell run1/run2 p5-p95 0.92-1.12, class geomeans within ±0.06.

## 1. Where the extra passes happen (loads per call, L regimes; K4/M1 the same except long X)
| class (artifacts) | L-nl-m today/B3 (ties) | L-nl-n | L-nonl-m | L-nonl-n |
|---|---|---|---|---|
| no-tie (109) | 22.4 / 20.6 (0) | 5.3 / 3.3 | 20.3 / 19.4 | 3.3 / 2.3 |
| tie, const, bounded X (12) | 10.2 / 4.3 (54 of 162) | 5.0 / 2.0 | 4.6 / 3.6 | 2.0 / 1.0 |
| tie, const, unbounded X (17) | 68.7 / 23.0 = 2.99x (281 of 402) | 5.2 / 2.4 | 25.0 / 24.1 | 2.1 / 1.1 |
| tie, state-dependent (synthetic 1) | 6.5 / 3.4 (5 of 24) | — | 3.8 / 3.8 | 2.0 / 1.0 |

- **The second seed** runs on every `\n`-terminated subject of all 266 artifacts. On no-tie artifacts it costs the
  dead step of seed n plus a view probe (+2 loads). Without a final `\n` it costs the `s[n-1]` check (+1 load).
- **The forward finish** fires only on a tie: a final `\n` that X can consume, with s* reached from both seeds. Some
  shapes tie on every `\n` line: nullable X (`\s*$`, `\W*$`, `;\s*$`) and X that runs to the line start (`[^\n]*\n?$`,
  `([^/]+)$`, `(?s)(.+)$`). `\s+$` ties only with blanks before the `\n`.
- **Where the full 3.00x lands.** Unbounded tie X on K4/M1: 784 → 262 loads, and 185,046 → 61,682 on 1 MiB.

## 2. ns/call (class geomean over artifacts, L regimes; K4/M1 within ±0.1 of L)
| class | regime | today ns | B3 ns | today/B3 | R/B3 (B3's effect) | today/R (style) | A/A |
|---|---|---|---|---|---|---|---|
| no-tie | nl-m / nl-n | 6.8 / 4.5 | 5.5 / 2.9 | 1.24 / 1.55 | **0.95** / 1.11 | 1.31 / 1.40 | 1.01 / 0.98 |
| no-tie | nonl-m / nonl-n | 6.2 / 3.3 | 4.7 / 2.4 | 1.22 / 1.30 | 1.16 / 1.10 | 1.04 / 1.19 | 0.98 / 0.95 |
| tie const bounded | nl-m / nl-n | 10.2 / 5.4 | 3.8 / 2.7 | **2.53** / 2.00 | **2.37** / 1.95 | 1.07 / 1.03 | 0.96 / 0.93 |
| tie const bounded | nonl-m / nonl-n | 4.6 / 3.3 | 3.1 / 2.4 | 1.45 / 1.34 | 1.31 / 1.13 | 1.10 / 1.19 | 1.00 / 0.98 |
| tie const unbounded | nl-m / nl-n | 9.9 / 5.4 | 3.8 / 3.0 | **2.41** / 1.85 | **2.25** / 1.64 | 1.07 / 1.13 | 1.00 / 1.00 |
| tie const unbounded | nonl-m / nonl-n | 4.9 / 3.4 | 3.7 / 2.5 | 1.29 / 1.39 | 1.18 / 1.01 | 1.10 / 1.37 | 1.01 / 0.99 |
| tie state-dependent | nl-m / nonl-m | 7.1 / 4.8 | 4.1 / 3.6 | 1.74 / 1.33 | 1.76 / 1.41 | 0.99 / 0.94 | 0.99 / 0.98 |

Single cells: `\s+$` (bench) L-nl-m 6.9 → 3.3 ns; `;\s*$` 13.0 → 3.6; `[^\n]*\n?$` 81 → 27; `(?s)(.+)$` K4 2.41 → 0.83 µs,
M1 622 → 213 µs (2.92x). The ranges per class are in `results/report.txt`.

## 3. Cost side, measured
- **States.** Today's minimized reverse X$ DFA vs the tagged product: no-tie 508 → 803 (1.58x), tie bounded
  55 → 86 (1.56x), tie unbounded 50 → 70 (1.40x).
- **Bytes.** Machine bytes (class map + next + accept) grow 1.07-1.16x, since the 256 B class map dominates small
  machines. The search body's static arrays, run tables included, change by 1.37x on no-tie, 0.80x on bounded and
  1.15x on unbounded.
- **Does the bigger table cost time where B3 saves nothing? Yes, a little.** R/B3 is 0.89-0.92 on no-tie `\n`
  matching cells (`.*\.txt$`, `done$`, `\.(?:txt|log)$`; class 0.95). It is 0.90-0.95 on long no-`\n` walks
  (`[^\n]*\n?$`, `([^/]+)$`, short `(?s)(.+)$`). Both runs reproduce these: about a 5-10% loss, at the edge of the
  per-cell floor.

## 4. A narrower fix
B3's own gain (R/B3 ≥ 1.6) is confined to the 30 tie-capable artifacts on `\n` subjects. On no-tie artifacts the
dead seed is ~1.1x. So the full gain is available from two changes: tag ONLY tie-capable artifacts (b3cost's C6),
and on the others let the last byte (and `search_from`) pick the one live seed. That second change is argued
(`nl_last` false), not built. Together they avoid +58% states on 109 artifacts.

## Caveats
- `mark_prio` is empirical (B3's best case). The static fact may answer state-dependent more often; that class
  measured 1.45-1.76x, not 2.4x.
- The product mislabels an unmarked `\z` accept as distance 1 on `ab\z|b\Z` and `\d+$|\w+\z` (b3sem S5). const0
  covered both: 0 wrong.
- utf8 and context-axis artifacts are not twinned. The twin's run-skip on every self-loop state is generous to B3,
  and R gets the same.
