# docs/dev/optloop/wf/ — `[WORD-FOLD]`'s D77 census artifacts (lane wfcensus)

The scripts, probes and raw census data behind `../wordfold_census.md`.
Reproduction pieces, not a runnable harness for anything else — each takes
its inputs from the environment and writes nothing outside the directory
it is pointed at, matching `../c2/`'s own shape and rules (nothing here
times anything; everything is read-only with respect to
`/Users/fdicostanzo/pcrec-bench`).

## Files

- `wf_run_probe.c` — the run walk: drives the real parser + `pcrec_altcls`
  + `pcrec_discharge_atomic` + `pcrec_lower_enc` pipeline prefix
  (`../c2/reqpos_probe.c`'s own cross-checked prefix), classifies every
  byte-domain `A_CLASS` position by the one-cube test (`byte_cube_of`, a
  fixed-8-bit-domain specialization of `studies/cls_tree_study/kit.py`'s
  `cube_of`, closed with an exact 256-point check), and reports the
  SINGLE LONGEST cube-run per pattern (`best`), its exact/cube-not-singleton
  composition, and the K/T mask pair per position. Hand-verified against
  nine crafted patterns before the corpus/bench run (`../wordfold_census.md`
  §1 lists them: plain literal, caseless literal, a digit-run break, a
  non-cube `[a-z]` break, `(?i)github_pat_`, caseful/caseless alternation,
  a mid-run `.` break, and `{a,c}`'s incidental non-caseless cube — every
  one matched hand-derived K/T values and break points). Build (never by
  `make`): `gcc -O2 -Ilib -Isrc -o wf_run_probe wf_run_probe.c
  build/libpcrec.a`. Input: `id<TAB>hex-pattern` per line; output: one TSV
  row per record.
- `wf_census.py` — the population driver: builds the `bench`
  (`bench/*/patterns/*.rx`, read-only against pcrec-bench) and `corpus`
  (every shipped `.rxt`'s `pattern`/`pattern-esc` line via
  `--list-source`, decoded with the SAME `pcrec_sb_field` inverter
  `reqpos_census.py` uses) populations, runs `wf_run_probe` over each at
  both `byte` and `-e utf8` encodings, and writes `wf_census.json`. Env:
  `PCREC PROBE BENCH CORPUS OUT`.
- `wf_census.json` — the raw joined census: one record per (population,
  pattern) with the probe's own columns plus `pattern_hex` and
  `is_caseless` (a literal `(?i)`/`(?i:` text search, informational only).
  Three populations: `bench` (249), `corpus` (3,995, byte domain),
  `corpus_utf8` (3,995, `-e utf8`) — read `../wordfold_census.md` §2's
  caveat before citing the utf8 arm's cube-not-singleton counts, which
  are dominated by `.`/`[^...]`'s own UTF-8 continuation-byte
  decomposition and are NOT literal-run population.
- `wf_stamps.py` — compiles every QUALIFYING pattern (`best_len >= 4`
  only — the ~4,000-pattern full corpus is not compiled a second time
  for this) at `--features all -p rx` and reads `RX_ENGINE`,
  `RX_ENGINE_WHY`, `RX_VM_FRAMELESS`, `RX_VM_PREFILTER`, `RX_DFA_SCAN`,
  `RX_DFA_PREFILTER` off the emitted artifact. Env: `PCREC IN OUT`.
- `wf_stamps.json` — that script's output: `bench` (78 qualifying rows),
  `corpus` (117 qualifying rows).
- `wf_offsetk_probe.c` — the `(?i)` offset-k degradation walk: drives the
  SHIPPED `pcrec_prefix_ksets` (`src/opt/prefix_k.c`) directly, not a
  re-derivation, over the D7-fast-path pipeline prefix `studies/n1budget/
  n1_measure.c` established (parse -> altcls -> discharge -> callgraph ->
  select_engine -> postresolve -> lower_enc -> build_nfa ->
  `pcrec_nfa_wrap_unanchored`). `k0` (the offset-0 DFA-start-state byte
  set) is passed as the WHOLE ALPHABET — a declared scope limit, not a
  soundness gap: `docs/design/offset_k_skip.md` §3.5 states offsets
  `j >= 1` come entirely from the NFA walk and never read `k0`, and this
  probe reports only `j >= 1`. Reports, per pattern, whether ANY offset
  has `count == 1` (a case-invariant byte the memchr-class skip could
  still use). Bot-anchored/`\G` patterns are excluded
  (`pcrec_nfa_has_bot`), matching `n1_measure.c`'s own D7-route scope.
  **`cx.enabled_features` must be set from `pcrec_enabled_mask()` after
  `pcrec_enabled_set_spec`** — the first draft omitted it and every
  pattern silently refused parsing; caught by hand-verifying a plain
  `needle` control before trusting a `(?i)needle` result, recorded here
  because the failure mode (silent `refused-or-bot` on every row) would
  otherwise look like "no `(?i)` pattern reaches the D7 route" rather
  than "the probe's own setup is incomplete." Build (never by `make`):
  `gcc -O2 -Ilib -Isrc -o wf_offsetk_probe wf_offsetk_probe.c
  build/libpcrec.a`.
- `wf_offsetk.json` — that probe's raw output over every `(?i)` pattern in
  bench+corpus (60), driven by an inline one-off script (not committed
  separately — the population-build logic is `wf_census.py`'s
  `bench_pop`/`corpus_pop` reused ad hoc; see `../wordfold_census.md` §6
  for the exact filter).
- `wf_report.py` — renders `wf_summary.txt` (the exact numbers
  `../wordfold_census.md` cites) from the three JSON files above. Reads
  them from the CURRENT directory; run after `wf_census.py`/`wf_stamps.py`
  have written their outputs here.
- `wf_summary.txt` — `wf_report.py`'s committed output.

## Reproduction

```
gcc -O2 -Ilib -Isrc -o wf_run_probe wf_run_probe.c ../../../../build/libpcrec.a
gcc -O2 -Ilib -Isrc -o wf_offsetk_probe wf_offsetk_probe.c ../../../../build/libpcrec.a
PCREC=../../../../build/pcrec PROBE=./wf_run_probe \
  BENCH=/Users/fdicostanzo/pcrec-bench CORPUS=../../../.. OUT=. \
  python3 wf_census.py
PCREC=../../../../build/pcrec IN=./wf_census.json OUT=. python3 wf_stamps.py
python3 wf_report.py
```
