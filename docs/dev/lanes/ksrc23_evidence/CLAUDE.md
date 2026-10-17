# docs/dev/lanes/ksrc23_evidence/ — lane ksrc23's zero-mover evidence

[KNOW-SRC] K2 + K3 (2026-10-17). See `../ksrc23_report.md` §3.

- `g1e1_summary.tsv` — `../e1build_evidence/g1e1_sweep.sh`'s summary, REF =
  the branch point 343605a57's build, NEW = the K3 head 66c51d710: 28 runs,
  0 movers, 0 asymmetric (an rc of 1 is an instrument floor; the report
  names each).
- `census.txt` — `scripts/emit_sweep.py --data analysis` trailer lines for
  `log`, `weblog` and `kdefault` (the shipped default renamed in both copies),
  each bundle against its own canonical view: 0 movers over 18,882 artifacts.
- `chain.sh`, `dflt.sh` — the two drivers that produced them (paths are the
  lane worktree's).

Maintenance: update this file when files are added/removed or their roles
change.
