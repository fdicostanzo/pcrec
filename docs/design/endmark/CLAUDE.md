# docs/design/endmark/ — D164's instruments and transcripts

The evidence behind `../endmark.md` (lane endmark, 2026-10-12). Nothing here is
built or run by `make`. Run the Python with `python3 -I` and
`PYTHONDONTWRITEBYTECODE=1`.

- `pcre2.py` — a minimal ctypes binding to libpcre2-8 (10.46 on the Linux dev box).
- `diff_lowering.py` — the lowering checked against libpcre2. It generates
  patterns from a small AST, writes the LOWERED spelling with an empty capture
  group `()` standing in for END_MARK, and compares group 0, every capture (with
  the close-at-mark rule for enclosing captures) and find-all at every start
  position over exhaustive subjects. `PLANT=<name>` runs one deliberately wrong
  variant (the controls; the names are in the source).
- `twin.py` — the hand twin, a priority-NFA simulation (the subset construction
  pcrec's DFA determinizes) with subject loads counted.
  - Part A: the forward scan with per-accept mark distance, against libpcre2.
  - Part B: rev-end today (two seeds plus a tie run) against the mark's tagged one
    walk with the `mark_prio` fact and the untagged walk with a forward run. It
    covers answers and the counted cost cells (compound.md §B.5's shapes).
  - Part C: reverse machine sizes.
  - `TWIN_PLANT=<name>` runs the controls.
- `tail_probe.c` — the census probe. It links `build/libpcrec.a` (build
  instructions in its header) and runs the real parser and pre-selection rewrites,
  with the lowering's tail walk and the first VM-only node outside the tail
  lookaheads.
- `census.py` — the census driver (imports `docs/dev/optloop/revend/census.py`'s
  population builders; env in its header).
- `census/cost.py` — lane emcensus (2026-10-12): the Q1 COST census. Rewrites each path-final
  `$`/`\Z`/`(?m)$` to the lowered text with `()` as the mark, compiles baseline and proxy `--no-captures`,
  reads machine states/table bytes from the emitted arrays; output `census/results/cost.txt`; report
  `docs/dev/lanes/emcensus_report.md`.
- `results/` — `diff_all_len5.txt` (3,527 patterns, 28,237,887 cells, 0
  differences), `diff_plants.txt`, `twin_k16000.txt`, `twin_plants.txt`,
  `census.txt` (at `885eccff`).
