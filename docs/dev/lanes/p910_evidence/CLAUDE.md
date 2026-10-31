# p910_evidence/ — instruments behind docs/dev/lanes/p910_report.md

Lane p910 (2026-10-29), evidence only; nothing builds or runs these. Twins are
hand edits of pcrec's OWN emitted `rx.c` (scratch), never pcrec code.

- `drv.c` — the bench's find-all (rx_search from pos, advance off the match),
  instructions:u / cycles:u around the find-all only; prints count + span hash.
- `mk_p9_twins.py` — P9 window-FIND twins (autofind, autofind2, vmfind,
  vmfind0, vmfindm1, vmfind2).
- `mk_p9_seedskip.py` — P9 DFA-local twin (autoseed): every seed state skips
  over its own stay set, read off the artifact's tables.
- `mk_p10_twins.py` — P10 twins: `pre` (presence check at attempt entry) and
  `paced` (checkpoint at max(D0, rest >> SHIFT) bytes into the attempt);
  `paced2` (call-free core with resume) is the codegen control.
- `gen_stress.py` — the seeded P9 answer-identity stress subjects.
- `gen_witness.py` — the P10 witnesses (RECONSTRUCTED shapes; see its header).
- `census.py` — compile-only census (corpus + bench): seed states and their
  shape, skip gate, REQ_WHY and route stamps. `census.tsv.gz` — its output.
- `p10_controls.py` — P10 twins over every one-attempt bench pattern;
  `p10_controls.tsv.gz` — its output (job 691).
- `job_690_census.sh`, `job_691_p10controls.sh` — the boxqueue jobs that ran them.
- `run_p9.sh`, `sum_p9.py`, `sum_p10.py` — runners/summaries;
  `p9_results.tsv.gz`, `p10_results.tsv.gz` — raw rows (pattern, variant,
  group, file, len, matches, span hash, instr, cycles); `p9_counter.tsv` —
  the P9 counter-subject rows.
- `twin_*.diff` — the twin edits against the shipped artifact.
