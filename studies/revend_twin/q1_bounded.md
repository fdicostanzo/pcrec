# Q1 (design revend.md section 10): REVEND form B vs W1 on bounded patterns

Lane revq1, 2026-10-09. Scratch tier, Linux dev box (Ryzen 7 7700X, gcc 15.2 -O2), main 6973d7f5
(abi 70). Question: on bounded end-pinned patterns that `[OPT-ENDWIN]`'s W1 already serves, is
form B (seeded reverse walk to s*, then the unchanged forward pass from s*, then the existing
reverse pass) at parity with W1, or does the extra walk cost?

## Verdict

NOT parity, and the answer splits by shape of the subject, not by pattern:

- **Matching subject: B is slower, about 1.4-1.55x** (+5 to +10 ns on the 12-28 ns floor cells;
  +330 ns on `(?:[a-z]{0,1024})\z` with a 1000-byte tail, 723 -> 1056 ns). B runs three passes
  over the match (walk, forward, reverse) where W1 runs two plus a constant clamp. The
  `$`/`\Z` rows with a trailing newline pay the second seed too (1.5-1.74x, +8-10 ns). The cells
  nearest parity are the ones where the match is long relative to fixed costs on a wider table
  (`a{5,10}b{5,10}$`: 1.14-1.17x, `\d{1,8}$`: 1.06-1.24x).
- **Non-matching or short-tail subject: B is faster**, because its cost follows the match (or
  the walk's early death) while W1's follows the bound W: it always scans the last W bytes
  forward. Non-matching: 0.01-0.79x on every pattern (-1 to -13 ns, -480 ns on the 1024-wide). Wide windows are where it is
  large: `(?:[a-z]{0,1024})\z` with a short tail 478 -> 7.6 ns (0.02x); `[a-z]{0,64}\z` 31 ->
  7.5 ns (0.24x).
- **Crossover** is roughly where the match length is about half the bound W: below it B wins,
  above it W1 wins. On the bench's class B cells (`done$`/`done\z`/`done\Z`, `abc$`: W = 4-5,
  the subject tail IS the match) B is the slower arm by about 8 ns of about 14 (1.55x).
- **W1-denied** (the whole-subject forward scan) is 3-5 orders of magnitude above both
  (9 us - 1.4 ms), so either arm is a large win over nothing; the question is only W1 vs B.

Whether +5-10 ns matters is the manager's/Frank's call: in the bench these are the 24-454 ns floor
cells, so the harness' per-call overhead dilutes a +8 ns difference, but the direction is
unambiguous on the cells the design names as do-not-regress (design section 11 item 3).

## Method

- `run_q1.sh`: per pattern, three artifacts via `build/pcrec --features all -e byte`:
  `o` default (W1 stamp `END_WINDOW` = the bound), `d` with `-fno-end-window` (stamp `none`),
  and `t` = form B twin built from `d` by `mktwin.py` with `TWIN_FORM=lower`. B is built from
  the W1-denied source so the walk is not clipped by W1's clamp. Where the artifact has a REQ
  pre-check/handoff (`t_reqrun`, most `$` rows), `mktwin.py` now moves it to AFTER the walk
  (design 4.1 PRESENCE: it must scan [s*, n), not [search_from, n)); previously those rows
  were refused (`forward-pass markers`).
- Population (`q1_patterns.tsv`): the bench class B cells named in the design (`anc-dollar`
  = `done$`, `anc-z-lc` = `done\z`, `anc-z-uc` = `done\Z`, `ctrl-abc-dollar` = `wild-semdiv-
  dollar-trailing-newline-pcre2` = `abc$` [one pattern, one row], `letters-bounded-tail-z`),
  the brief's `\d{1,8}$`, `[a-z]{0,64}\z`, `(?:foo|barbaz)\.txt$` (`[a-z]{0,1024}\z` is the
  bench row), and five class B corpus witnesses from the census (`\bfoo$`, `a{5,10}b{5,10}$`,
  `[^c]{1,3}\z`, `ERROR$`, `x[a-z]{0,5}\z`). 13 rows.
- Subjects (`mksubj_q1.py`): prose body of 1 MiB and of 64 KiB + tail: `long` (uses most of the
  bound), `short`, `non` (non-matching tail), `nl` (short tail + final newline, `$`/`\Z` rows
  only). Where a bound is tiny, `long` = `short` (same bytes; both reported). 96 cells.
- Identity (before any timing): `check.c` (artifact `o` vs twin `t` vs libpcre2 10.46 oracle,
  every search_from on the ~850-subject pool + the 12 long bodies + find-all loops): 26 pool
  runs, `twin_diff=0`, `orig_vs_pcre2=0`, `twin_vs_pcre2=0`, `findall_diff=0` on every row
  (`results/q1_identity.txt`). `timedrv3` also asserts all three arms (o, t, d) return the same
  span on each of the 96 timing subjects: 0 ANSWER-DIFF. The twin's existing sabotage controls
  (`results/control_*.txt`) were not re-run: only the REQ-move in `mktwin.py` is new, and its
  effect is exercised by the identity sweep.
- Timing (`timedrv3.c`, `run_q1.sh 7 5`): taskset -c 7; per pass, per cell, 31 rounds of 2000
  calls each of `o` and `t` (3 of `d`), arms interleaved inside every round; 5 passes. Table
  values are the median over the 5 passes of each pass' median, with the range [min-max] of the
  pass medians. `q1_table.py` generates the table; raw rows in `results/q1_timing.tsv`.

## Contamination and noise

A detached chain was running on the box: load1 was 4.77-5.04 across the whole run (median 4.96;
`results/q1_timing.tsv` has load1 per cell). The run was pinned to CPU 7, but I did not check
what the chain placed on its SMT sibling. One visible effect: in many cells a single pass of
the five ran ~1.6x slower on BOTH arms (e.g. `[14.2-23.6]`), which is why the "overlap" flag
fires on 41 of 96 cells. In those cells the lower ends of the ranges are tight and give the same
ratio as the medians (e.g. `done$` long: 14.2 vs 22.0 ns on the minima), so I read the overlap
as one contended pass, not as B and W1 being indistinguishable. **Cells within 20% (flag `within20`, 13 of 96): `\d{1,8}$` short and nl (ratios 0.89-1.17,
differences of 0.4-1.4 ns, inside the noise), `a{5,10}b{5,10}$` long/short/nl (1.09-1.17,
+2.6 to +7.2 ns, B slower), `x[a-z]{0,5}\z` 1m short (1.13, +0.8 ns).** Call these near parity;
the +-1 ns ones are inside the run-to-run range. Nearest others: `\d{1,8}$` long (1.22-1.24),
`x[a-z]{0,5}\z` 64k short (1.23). Every other cell differs by more than 30% and, at the
minima, the arms' ranges do not cross. The `within20` cells are the ones worth re-running on a
quiet box.

## Table, 1 MiB subjects (64 KiB in `results/q1_table.md`; every ratio within about 0.1 of the 1 MiB one)

ns per search call; "W1 today" and "form B" show median [range of pass medians]; "W1-denied" is the median.

| pattern | size | tail | W1 today ns | form B ns | W1-denied ns | B/W1 | B-W1 ns | flag |
|---|---|---|---|---|---|---|---|---|
| `bench-anc-dollar` | 1m | long | 14.3 [14.2-23.6] | 22.2 [22.0-31.8] | 312606 | 1.55 | +7.9 | overlap |
| `bench-anc-dollar` | 1m | short | 14.4 [14.2-23.6] | 22.3 [22.2-31.8] | 313294 | 1.55 | +7.9 | overlap |
| `bench-anc-dollar` | 1m | non | 3.5 [3.4-5.4] | 2.7 [2.7-5.2] | 309510 | 0.77 | -0.8 | overlap |
| `bench-anc-dollar` | 1m | nl | 18.5 [18.3-24.9] | 28.4 [28.0-37.1] | 320000 | 1.54 | +9.9 |  |
| `bench-anc-z-lc` | 1m | long | 18.4 [15.7-24.3] | 24.3 [24.2-33.6] | 317499 | 1.32 | +5.9 | overlap |
| `bench-anc-z-lc` | 1m | short | 15.8 [15.7-24.0] | 24.3 [24.2-32.1] | 320902 | 1.54 | +8.5 |  |
| `bench-anc-z-lc` | 1m | non | 3.5 [3.4-5.5] | 2.2 [2.2-4.1] | 316604 | 0.63 | -1.3 | overlap |
| `bench-anc-z-uc` | 1m | long | 14.3 [14.2-23.0] | 22.1 [22.1-31.4] | 311805 | 1.55 | +7.8 | overlap |
| `bench-anc-z-uc` | 1m | short | 14.3 [14.2-23.1] | 22.3 [22.2-31.7] | 312676 | 1.56 | +8.0 | overlap |
| `bench-anc-z-uc` | 1m | non | 3.4 [3.4-5.4] | 2.7 [2.7-5.2] | 309190 | 0.79 | -0.7 | overlap |
| `bench-anc-z-uc` | 1m | nl | 18.5 [18.3-27.7] | 28.4 [28.1-39.7] | 313581 | 1.54 | +9.9 |  |
| `bench-abc-dollar` | 1m | long | 12.2 [12.1-18.9] | 17.5 [17.3-25.2] | 48865 | 1.43 | +5.3 | overlap |
| `bench-abc-dollar` | 1m | short | 12.2 [12.1-19.2] | 17.5 [17.4-25.3] | 48899 | 1.43 | +5.3 | overlap |
| `bench-abc-dollar` | 1m | non | 4.6 [4.4-8.9] | 2.7 [2.7-5.1] | 49156 | 0.59 | -1.9 | overlap |
| `bench-abc-dollar` | 1m | nl | 11.5 [11.4-18.1] | 20.0 [19.8-28.1] | 48779 | 1.74 | +8.5 |  |
| `bench-letters-bounded-tail-z` | 1m | long | 722.9 [720.6-1294.4] | 1056.0 [1054.4-1779.1] | 1362308 | 1.46 | +333.1 | overlap |
| `bench-letters-bounded-tail-z` | 1m | short | 478.5 [471.9-515.9] | 7.6 [7.5-7.6] | 1342291 | 0.02 | -470.9 |  |
| `bench-letters-bounded-tail-z` | 1m | non | 481.6 [475.2-509.4] | 4.1 [4.0-4.2] | 1364132 | 0.01 | -477.5 |  |
| `w-d18-dollar` | 1m | long | 15.6 [15.5-23.9] | 19.3 [19.1-31.6] | 505914 | 1.24 | +3.7 | overlap |
| `w-d18-dollar` | 1m | short | 7.1 [7.1-14.2] | 7.5 [7.4-14.2] | 508318 | 1.06 | +0.4 | within20,overlap |
| `w-d18-dollar` | 1m | non | 8.1 [8.0-15.5] | 2.5 [2.5-5.0] | 529946 | 0.31 | -5.6 |  |
| `w-d18-dollar` | 1m | nl | 8.2 [8.0-15.1] | 9.6 [9.1-18.1] | 518357 | 1.17 | +1.4 | within20,overlap |
| `w-az64-z` | 1m | long | 44.6 [44.3-89.7] | 61.3 [60.2-122.9] | 1364823 | 1.37 | +16.7 | overlap |
| `w-az64-z` | 1m | short | 31.3 [30.9-31.6] | 7.5 [7.4-7.6] | 1357887 | 0.24 | -23.8 |  |
| `w-az64-z` | 1m | non | 32.1 [31.7-32.5] | 4.1 [4.0-4.1] | 1364392 | 0.13 | -28.0 |  |
| `w-foo-barbaz-txt` | 1m | long | 28.3 [28.1-36.0] | 43.0 [42.8-52.1] | 463053 | 1.52 | +14.7 |  |
| `w-foo-barbaz-txt` | 1m | short | 23.6 [23.4-23.8] | 33.8 [33.6-34.2] | 463741 | 1.43 | +10.2 |  |
| `w-foo-barbaz-txt` | 1m | non | 13.6 [13.5-13.6] | 2.7 [2.7-2.7] | 464756 | 0.20 | -10.9 |  |
| `w-foo-barbaz-txt` | 1m | nl | 23.9 [23.7-29.4] | 35.9 [35.5-43.1] | 466236 | 1.50 | +12.0 |  |
| `c-bfoo-dollar` | 1m | long | 16.8 [16.7-17.0] | 23.4 [23.2-23.6] | 89819 | 1.39 | +6.6 |  |
| `c-bfoo-dollar` | 1m | short | 16.8 [16.7-16.9] | 23.5 [23.3-23.6] | 90086 | 1.40 | +6.7 |  |
| `c-bfoo-dollar` | 1m | non | 11.5 [11.4-11.5] | 2.7 [2.7-2.7] | 89676 | 0.23 | -8.8 |  |
| `c-bfoo-dollar` | 1m | nl | 16.6 [16.5-22.0] | 25.6 [24.6-31.7] | 88781 | 1.54 | +9.0 |  |
| `c-a5b5-dollar` | 1m | long | 41.2 [40.9-41.7] | 48.4 [48.1-49.4] | 400458 | 1.17 | +7.2 | within20 |
| `c-a5b5-dollar` | 1m | short | 27.6 [27.3-27.8] | 31.5 [31.2-31.7] | 399500 | 1.14 | +3.9 | within20 |
| `c-a5b5-dollar` | 1m | non | 20.3 [20.0-30.2] | 6.7 [6.6-6.8] | 400502 | 0.33 | -13.6 |  |
| `c-a5b5-dollar` | 1m | nl | 34.6 [34.3-34.9] | 40.4 [40.0-40.7] | 398688 | 1.17 | +5.8 | within20 |
| `c-notc13-z` | 1m | long | 5.4 [5.3-5.4] | 7.7 [7.6-7.8] | 207424 | 1.43 | +2.3 |  |
| `c-notc13-z` | 1m | short | 5.4 [5.3-5.4] | 7.7 [7.6-7.7] | 207498 | 1.43 | +2.3 |  |
| `c-notc13-z` | 1m | non | 4.9 [4.6-5.0] | 2.1 [2.1-2.1] | 207875 | 0.43 | -2.8 |  |
| `c-error-dollar` | 1m | long | 15.7 [15.6-25.7] | 22.0 [21.7-35.5] | 7601 | 1.40 | +6.3 | overlap |
| `c-error-dollar` | 1m | short | 15.7 [15.7-26.2] | 22.0 [21.9-35.2] | 7578 | 1.40 | +6.3 | overlap |
| `c-error-dollar` | 1m | non | 7.6 [5.7-8.6] | 2.8 [2.7-5.4] | 7531 | 0.37 | -4.8 |  |
| `c-error-dollar` | 1m | nl | 19.8 [19.5-25.3] | 27.9 [27.6-38.4] | 7581 | 1.41 | +8.1 |  |
| `c-xaz5-z` | 1m | long | 18.7 [18.6-27.9] | 28.3 [28.1-35.8] | 267257 | 1.51 | +9.6 |  |
| `c-xaz5-z` | 1m | short | 6.0 [6.0-11.1] | 6.8 [6.7-11.1] | 246752 | 1.13 | +0.8 | within20,overlap |
| `c-xaz5-z` | 1m | non | 4.8 [4.8-8.9] | 2.3 [2.3-4.3] | 251811 | 0.48 | -2.5 |  |

## Caveats

- The twin is hand-made (the design's own scratch tier): the real REVEND emission could trim
  the walk's loop overhead (the `n`/`n-1` seed loop is what makes the `nl` rows cost +10 ns),
  or add a fixed cost the twin does not model. The 3-passes-vs-2 structure is not an artifact of
  the twin; the constants might be.
- Subjects are synthesized prose bodies (same recipe as `mksubj.py`), not the bench's bytes.
  Per-call overhead of the bench harness is not modeled; ns here are the search call alone.
- Only search_from = 0 is timed, byte encoding only (W1 declines utf8; that cell is REVEND's
  alone and is not part of this question).
