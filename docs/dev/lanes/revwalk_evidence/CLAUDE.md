# revwalk_evidence/ — instruments behind docs/dev/lanes/revwalk_report.md

Lane revwalk (2026-10-29), design + census only; nothing here is built or run by `make`.

- `tiers.py` — the tier census (parse-only; pcrec runs only as `--list-source`): best inner landmark per
  unanchored pattern, the walk-back tier of its prefix (T1 fixed, T2 one plain run, T3 forced-boundary
  segments, T4 general reverse DFA, G1 decline), exclusion / composition / G4 / scan-edge columns, and the
  whole-pattern (end-seeded) tier. Reader, flatten, landmarks, NFA and arms imported from
  `docs/design/where_to_start/rincensus.py`. `--selftest` = C1 (20 hand rows); `--sabotage chain` must FAIL it.
- `model.py` — the tactic model on real patterns: the segment walk + anchored libpcre2 verify (LOWER where S
  reads a group of P) against libpcre2's unanchored search, every startpos; mutations max_start / no_ctx /
  no_max must be detected.
- `facts_control.py` — control C3 from pcrec's own `--emit-facts` (start_anchor, req_set, req_set_maxoff)
  and the route per tier; > 50 compiles, so run under `scripts/boxlock run`.
- `summary.txt`, `rows.tsv.gz` (one row per pattern, pattern text included), `selftest.txt`, `model.txt`,
  `facts_control.txt` — the committed outputs (provenance line first).

Re-run: `PCREC=build/pcrec CORPUS=. OUT=<scratch> python3 tiers.py` (~7 min);
`PCRE2_LIB=/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0 python3 model.py --subjects 8` (~10 min).
