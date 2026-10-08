# docs/dev/optloop/nullanch/ — [NULLABLE-ANCH] STEP 0 (lane nullanch0, 2026-10-08)

The compile-side census of the shape "nullable pattern whose hybrid prefilter
the [OPT-4.2] decline removed", plus the quick local timing and the answer
differential that D77 asks for before a mechanism is built. MEASUREMENT ONLY:
nothing under `src/` was touched. The reading is
`docs/dev/lanes/nullanch0_report.md`.

## Files

- `run_census.sh` — rebuilds all of it from a built tree (probe, census,
  summary, timing, differential). Light: `-j4`, single-core timing.
- `anch_probe.c` — links `build/libpcrec.a` (the `p2info.c`/`lim2_census.c`
  idiom): parse -> altcls -> discharge_atomic -> callgraph, then
  `pcrec_nullable` and the CORRECTED-PREDICATE CANDIDATE — the set of
  empty-path constraint masks (absolute start `^`/`\A`, absolute end `$`/`\Z`/
  `\z`), `dismissable` iff every empty path carries both. Cross-checks its own
  nullability against `pcrec_nullable` (`xchk`, must be 0).
- `census.py` — population (4,000 distinct corpus patterns + 303 bench) x
  stamps of the default / `--no-captures` compiles x the probe x `--emit-ir`
  for the declined ones. Imports `scripts/emit_sweep.py` for the corpus
  enumeration and the escape vocabulary.
- `summarize.py` — the tables; `census_summary.txt` is its output at 9029f5db.
- `census_rows.tsv` — one row per distinct pattern (936 KB; the census data).
- `timing_driver.c`, `timing.sh`, `timing_results.tsv` — INDICATIVE local
  timing (single core, `taskset -c 3`, median of 5 batches): default VM vs the
  `-fprefilter` hand twin vs the shipped `--no-captures` DFA arm. Not a bench
  result.
- `diff_driver.c`, `diff.sh`, `diff_results.txt` — every subject up to a bound
  over a small alphabet, default vs `-fprefilter` twin, rc + captures.

## The BUILD's instruments (lane nullanch1, 2026-10-08)

The row itself is `src/facts/widths.c`'s `empty_admits` fact; these measure
it. Reading: `docs/dev/lanes/nullanch1_report.md`.

- `movers.py` → `movers_result.txt` — the mover manifest: census.py's
  population compiled by a REFERENCE and a WORKING pcrec (same abi), every
  pattern whose `.c` differs, with ENGINE_SEL/VM_PREFILTER both sides, and the
  `declined-nullable-default` count each side (112 -> 107; exactly the five).
- `diff1_driver.c`, `diff1.sh` → `diff1_results.txt` — the answer
  differential at full width: reference default vs working default, every
  subject to a bound over an alphabet holding `\n`, AND every start offset.
- `pcre2_cells.py` → `pcre2_transcript.txt` — the libpcre2 10.46 transcript
  for the movers; `--rxt` writes `tests/base/nullable_anch.rxt`'s blocks from
  it (oracle first). The two give-up cells' libpcre2 answer is `-47` (U4);
  they are checked on the language-equal patterns and by python (U19).
- `timing1.sh` → `timing1_results.tsv` — STEP 0's timing driver over the
  reference default, the working default and `--no-captures`, near-miss and
  long-match subjects; INDICATIVE, one core.

Bench inputs are READ from `pcrec-bench` (never written): the pattern files
and the published `reports/` lines the report cites.
