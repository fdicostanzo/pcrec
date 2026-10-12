# b3meas — B3 (the match-end mark on rev-end) measured: loads and ns/call, today vs a B3 hand twin

Lane b3meas, 2026-10-12, main `32141d473` (abi 76), Linux dev box (7700X, gcc 15.2 `-O2`). No `src/` change. Evidence:
`docs/design/endmark/b3meas/` (`gen.py`, `harness.c`, `probe.c`, `report.py`); `results/report.txt` has every table below.

## Verdict
B3 saves a pass **where the subject ends in `\n` and the artifact can tie**: 30 of the 139 distinct byte artifacts
twinned (35 of the 266 rows; 1 of 9 bench, `tail-space-eol`). That is exactly the per-line regime, a line with its
`\n`. There it cuts loads 2.4-3.0x and time **2.4-2.5x (about 10 → 4 ns/call)**. When X spans the subject the saving
is a whole pass: `(?s)(.+)$` on 1 MiB goes from 622 µs to 213 µs. Elsewhere (the 109 no-tie artifacts, or no final
`\n`) B3's own effect is 0.95-1.16x: the dropped second-seed probe (1-2 loads) against a machine with 1.4-1.6x the
states, which costs 5-10% on long walks without a `\n`. **Worth:** about 6 ns per line-shaped call on tie-capable
patterns and nothing material on the rest. The same win is reachable without tagging those 109 (§4). Separately,
today's emitted walk is 1.04-1.40x slower than the SAME algorithm in plain table style, which is as large as B3's
whole effect on no-tie artifacts.

## Method
- **Population.** b3cost's 266 rows (205 distinct), plus `[ \t]+$`, `\.(?:txt|log)$`, `;\s*$` and the only
  state-dependent witness, endmark.md §1.5's synthetic `(?:\s+|x\s*?)$`; no shipped pattern is state-dependent. 139
  twinned; excluded 44 context-axis (`\b`, lookarounds), 16 utf8, 7 not DFA rev-end. Capture rows use `--no-captures`.
- **B3 twin.** Today's file with `T_search` replaced by ONE walk from n over the Moore-minimized product of pcrec's
  own reverse DFAs for `X\z` and `X\n\z`. A tie takes `n-c` where `mark_prio` is const, else verify-at. `mark_prio`
  is classified from libpcre2's choice on every observed tie (B3's best case); all 30 shipped tie artifacts read const.
  Bounded vs unbounded X is read off the tagged machine (acyclic or not).
- **Control R.** Today's algorithm (two seeds, today's machine and views, verify-at) in the twin's code style.
  **R/B3 is B3's own effect; today/R is code style.**
- **Answers** vs libpcre2 10.46: 90,950,619 exhaustive cells (every start position, length ≤ 5) + 11,635 regime
  subjects, 0 wrong for today, B3 and R. Loads = every `subject[...]` read, instrumented.
- **Regimes.** L = 40-200 B log-like lines; K4/M1 = 4 KiB / 1 MiB blobs with a varying last line; each with/without
  a final `\n`, matching (m) or not (n) per libpcre2.
- **Timing.** `taskset -c 2`, 21 rotating rounds of ≥ 2 ms, back-to-back calls over 2-24 subjects (warm cache);
  other lanes held CPUs 12-15. **A/A floor** (today vs a separately compiled copy): class geomean 0.93-1.02,
  per-cell p5-p95 0.90-1.05. A second full run agrees (per-cell run1/run2 p5-p95 0.92-1.12).

## 1. Where the extra passes happen (loads per call, today / B3; L regimes, K4/M1 alike except long X)
| class (artifacts) | L-nl-m (ties / subjects) | L-nl-n | L-nonl-m | L-nonl-n |
|---|---|---|---|---|
| no-tie (109) | 22.4 / 20.6 (0) | 5.3 / 3.3 | 20.3 / 19.4 | 3.3 / 2.3 |
| tie, const, bounded X (12) | 10.2 / 4.3 (54 / 162) | 5.0 / 2.0 | 4.6 / 3.6 | 2.0 / 1.0 |
| tie, const, unbounded X (17) | 68.7 / 23.0 = 2.99x (281 / 402) | 5.2 / 2.4 | 25.0 / 24.1 | 2.1 / 1.1 |
| tie, state-dependent (1 synthetic) | 6.5 / 3.4 (5 / 24) | — | 3.8 / 3.8 | 2.0 / 1.0 |

- **The second seed** runs on every `\n`-terminated subject of all 266: on no-tie artifacts it costs seed n's dead
  step plus a view probe (+2 loads); without a final `\n`, the `s[n-1]` check (+1).
- **The forward finish** fires only on a tie (a final `\n` X can consume, s* reached from both seeds): on every `\n`
  line for nullable X (`\s*$`, `\W*$`, `;\s*$`) and X running to the line start (`[^\n]*\n?$`, `([^/]+)$`,
  `(?s)(.+)$`); `\s+$` only with blanks before the `\n`. The full 3.00x lands on unbounded X: 185,046 → 61,682 on 1 MiB.

## 2. ns/call (class geomean, L regimes; K4/M1 within ±0.1)
| class | regime | today ns | B3 ns | today/B3 | R/B3 (B3's effect) | today/R (style) | A/A |
|---|---|---|---|---|---|---|---|
| no-tie | nl-m / nl-n | 6.8 / 4.5 | 5.5 / 2.9 | 1.24 / 1.55 | **0.95** / 1.11 | 1.31 / 1.40 | 1.01 / 0.98 |
| no-tie | nonl-m / nonl-n | 6.2 / 3.3 | 4.7 / 2.4 | 1.22 / 1.30 | 1.16 / 1.10 | 1.04 / 1.19 | 0.98 / 0.95 |
| tie const bounded | nl-m / nl-n | 10.2 / 5.4 | 3.8 / 2.7 | **2.53** / 2.00 | **2.37** / 1.95 | 1.07 / 1.03 | 0.96 / 0.93 |
| tie const bounded | nonl-m / nonl-n | 4.6 / 3.3 | 3.1 / 2.4 | 1.45 / 1.34 | 1.31 / 1.13 | 1.10 / 1.19 | 1.00 / 0.98 |
| tie const unbounded | nl-m / nl-n | 9.9 / 5.4 | 3.8 / 3.0 | **2.41** / 1.85 | **2.25** / 1.64 | 1.07 / 1.13 | 1.00 / 1.00 |
| tie const unbounded | nonl-m / nonl-n | 4.9 / 3.4 | 3.7 / 2.5 | 1.29 / 1.39 | 1.18 / 1.01 | 1.10 / 1.37 | 1.01 / 0.99 |
| tie state-dependent | nl-m / nonl-m | 7.1 / 4.8 | 4.1 / 3.6 | 1.74 / 1.33 | 1.76 / 1.41 | 0.99 / 0.94 | 0.99 / 0.98 |

Cells: `\s+$` (bench) L-nl-m 6.9 → 3.3 ns; `;\s*$` 13.0 → 3.6; `[^\n]*\n?$` 81 → 27; `(?s)(.+)$` K4 2.41 → 0.83 µs,
M1 622 → 213 µs (2.92x).

## 3. Cost side, measured
- **States** (today's minimized reverse X$ DFA → tagged product): no-tie 508 → 803 (1.58x), tie bounded 55 → 86
  (1.56x), tie unbounded 50 → 70 (1.40x). Machine bytes (class map + next + accept) 1.07-1.16x, the 256 B class map
  dominating; the search body's arrays, run tables included, 1.37x / 0.80x / 1.15x by the same classes.
- **Does the bigger table cost time where B3 saves nothing? Yes, a little.** R/B3 is 0.89-0.92 on no-tie `\n`
  matching cells (`.*\.txt$`, `done$`, `\.(?:txt|log)$`; class 0.95) and 0.90-0.95 on long no-`\n` walks
  (`[^\n]*\n?$`, `([^/]+)$`, short `(?s)(.+)$`), reproduced in both runs: a 5-10% loss at the per-cell floor's edge.

## 4. A narrower fix
B3's own gain (R/B3 ≥ 1.6) is confined to the 30 tie-capable artifacts on `\n` subjects; on no-tie artifacts the dead
seed is ~1.1x. So tag ONLY tie-capable artifacts (b3cost's C6) and let the last byte (and `search_from`) pick the one
live seed elsewhere (argued from `nl_last` false, not built): the same win without +58% states on 109 artifacts.

## Caveats
`mark_prio` is empirical (B3's best case); where the static fact answers state-dependent the measured gain is
1.45-1.76x, not 2.4x. The product mislabels an unmarked `\z` accept as distance 1 on `ab\z|b\Z` and `\d+$|\w+\z`
(b3sem S5); const0 covered both, 0 wrong. utf8 and context-axis artifacts are not twinned. Run-skip on every
self-loop state is generous to B3, and R gets the same.
