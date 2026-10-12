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
- `b3cost_probe.c` + `census/b3cost.py` — lane b3cost (2026-10-12): B3's reverse machine at the TAGGED
  size (D164 add. 3). The probe links `libpcrec.a`, builds the real reverse DFA (select_engine, lower_enc,
  `pcrec_build_min_dfa`, optional `pcrec_scanedge_dfa`) for `X$`, `X\n?\z`, `X\z`, `X\n\z`, and takes the
  tagged machine as the Moore-minimized PRODUCT of the last two (accept pair = the mark distance set).
  Three controls print in the output: model == emitted states for today and for the untagged proxy, and the
  product with an OR output == the untagged machine. Output `results/b3cost.txt`; report
  `docs/dev/lanes/b3cost_report.md`. Run line in `census/b3cost.py`'s header.
- `b3meas/` — lane b3meas (2026-10-12): B3 MEASURED, today's shipped rev-end vs a B3 hand twin and a
  restyled control, answers against libpcre2, loads and ns/call per regime (own CLAUDE.md); report
  `docs/dev/lanes/b3meas_report.md`.
- `b3rev/` — lane b3rev (2026-10-12): B3 REVISION 2 (endmark.md §R), selective tagging: the machine probe
  (`b3rev_probe.c`: every machine a B3 artifact carries, tagged and lowered, before and after scan-edge, the tie
  fact per context atom, `mark_prio`), its driver (`b3rev.py census|sweep|refusal`), raw results, and `timing/`
  (the walk-form and lowered-finisher clock). Own CLAUDE.md; report `docs/dev/lanes/b3rev_report.md`.
- `results/` — `diff_all_len5.txt` (3,527 patterns, 28,237,887 cells, 0
  differences), `diff_plants.txt`, `twin_k16000.txt`, `twin_plants.txt`,
  `census.txt` (at `885eccff`), `b3cost.txt` (at `0e8849125`).
