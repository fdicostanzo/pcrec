# studies/dfacap_spike/ — tagged-DFA captures spike (lane capspike, 2026-11-12)

STUDY CODE, never product: a Python reference construction that tests whether
a priority-ordered tagged DFA gives PCRE2-exact capture offsets. Nothing here
is built by `make` or linked into pcrec. Report: docs/dev/lanes/capspike_report.md;
background: docs/design/dfa_captures_research.md.

## Files

- `tdfa.py` — parser (the named subset), tagged NFA, closure (priority DFS, PCRE
  empty-iteration rule), Pike-VM reference, TDFA construction + interpreter + cost
  stats. `CAPSPIKE_SABOTAGE=noempty|noctx|fifo|nocopy` are the controls.
- `oracle.py` — the witnesses: libpcre2 through the repo's ctypes binding
  (borrowed from docs/design/eng_brep_measurements/probes/pcre2_ctypes.py), and
  this worktree's `build/pcrec --engine=vm` artifacts via a batch driver.
- `cases.py` — the named hard cases, exhaustive subjects, three-way differential.
- `population.py` — the census's captures-only class: subset admission, corpus
  subjects + exhaustive small subjects, differential and cost rows.
- `results/` — committed outputs (`cases.txt`, `sabotage.txt`, population TSVs and summaries).

Run (niced, scratch under $PCREC_TMPDIR/scratch/capspike/): `python3 cases.py 6`.
