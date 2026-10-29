# docs/dev/lanes/p1dsg2_evidence/ — lane p1dsg2 evidence (P1 landmark walk, design rev 1)

Evidence cited by `../p1dsg2_report.md` (2026-10-29, opus; design + measurement only). Historical
after merge; never edited.

- `unique_rule.py` / `unique_rule.txt` — A1: the (state, class) UNIQUE rule on pcrec's emitted
  reverse tables, an independent subset-construction model, and libpcre2 10.46 exhaustive per-hit vs
  find-all on the witness table (verdict PASS).
- `xo_subjects.py`, `xo_raw.txt`, `xo_fit.py`, `xo_fit.txt` — the cycles crossover sweep (wlen
  {2,8,32} x miss/hit arm x 7 densities, shipped vs twin from p1dsg's scratch) and its fit.
- `population2.py` / `population2.txt` — the parse-only admission census under rev 1 (choice rule,
  `bot` row; `--selftest`, `--sabotage choice`); reuses `../revwalk_evidence/tiers.py`.
- `bench_stamps.py` / `bench_stamps.txt` — corrects the census's bench `next-landmark`/`excl-*` rows
  with each artifact's RX_ENGINE / RX_DFA_PREFILTER stamps (37 compiles).
