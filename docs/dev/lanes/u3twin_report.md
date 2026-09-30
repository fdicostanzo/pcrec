# u3twin report -- [UCP] U3 island hand-twin (2026-09-30, sonnet, measurement only)

Branch `lane/u3twin`. Memo: `docs/design/ucp_measurements/u3_island_twin.md`.
Harness: `studies/u3_island_twin/`.

## Delivered
- Island twin generator (F1 computed from pcrec's flat byte tables; F2
  hand-derived), three vector producers, eight cases, oracle (local and 10.46
  over ssh), correctness driver, sanitizer mode, failing-direction controls,
  reach census, timing harness, bundle.
- Correctness COMPLETE: 8 cases x 31,168 cases, 0 differences against libpcre2
  10.46, today's artifacts, forced VM and each other; ASan/UBSan clean.

## Timing and verdict (ubuntubudu, 2026-09-30 01:08, COMPLETE)
gcc 15.2 -O2, Ryzen 5 1600, 11 rounds, load1 0.47-0.48 before every unit
(gate 0.5), 28 cells, answers/checksums identical across all arms and rounds
in every cell. Data: `studies/u3_island_twin/results/bench_ubuntubudu.tsv`,
`bench_summary.tsv`, `bench.log`. Full table and reading: memo s3-s4.
- Consuming wide classes (16 cells): island slower than the best all-byte arm
  in 14 (1.04-1.65x; latin1/mixed worst, 1.18-1.65x); one clear win, xwd/cjk
  with bitmap1, 15.29 vs 18.39 ns/char (0.83x); nd/latin1 0.98x is 2.2%
  against a 1.9% floor (marginal, not counted). Against today's default artifact
  only, l/cjk is a win too (0.76x) but the raised-cap artifact beats it.
- x1/x2 (no all-byte form): island DFA 4-5x faster than the VM hybrid on
  ascii/latin1 (x1) and ascii/latin1/mixed (x2), 1.35x (x1/mixed) and 2.65x
  (x2/cjk) slower where the hybrid prefilter skips text. x3 (UCP `\b`, no
  baseline) 7.7-19.4 ns/char.
- Null control bc/bb 0.990-1.006 (x2: 0.895-0.930, inside its 10.5% floor).
- Verdict: the island is NOT a speed win over a cache-resident all-byte
  machine; a speed-leaning theta setting is not supported. It stands as a
  capability route (Row 1) and, unmeasured here, a size/compile-time route.
- Caveats: one box/compiler; the twin has no premultiplied table or scan-edge
  skip (up to 17-27% handicap on l, measured as bd vs bb); t_decode/t_stop not
  separated; the CJK cause is a hypothesis.

## Findings so far
1. F1 twins fall out of the byte tables mechanically: 2 boundary states per
   direction for every consuming class tried (base 12-698 states).
2. The design's ⊥ rule and repaired back_step hold end to end against 10.46
   on a 31k-case ill-formed matrix, forward, reverse, seed and reverse
   boundary.
3. A twin without the artifact's own necessary-byte pre-check loses ~80x to it
   on text lacking the byte (Mac scratch, loaded box): the island's fair
   comparison keeps today's pre-checks in front, as ucp_design s3.6 says.
4. Local libpcre2 10.48 (Unicode 17) disagrees with pcrec's UCD 16 on new
   code points; use the 10.46 reference for any Unicode-set oracle.
5. Three of thirteen planted defects are unobservable for these patterns
   (memo s2); do not read the controls as covering surrogates or overlong
   ASCII.
