# p1dsg_evidence/ — instruments behind docs/dev/lanes/p1dsg_report.md

Lane p1dsg (2026-10-29), evidence only; nothing builds or runs these from make.

- `drv.c` (whole-subject find-all), `drv_lines.c` (each line its own subject): instructions:u/cycles:u around the find-all, every capture span hashed.
- `extract_rw.py`: wraps the reverse-pass machine pcrec emits for `P.L` as `rw_walk(subject, seed, floor)` (pcrec's own text, renamed).
- `mk_twin.py` (DFA artifact) / `mk_vmtwin.py` (VM artifact): splice the landmark candidate loop into the shipped artifact.
- `twin_*.diff`: the twins against the shipped artifacts; `twin_dp_handedge.diff` the hand class-context scan edge.
- `results.txt`: every number the report cites. `population.py` / `population.txt`: the admission-table population.
