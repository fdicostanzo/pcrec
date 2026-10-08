# docs/design/decision_families/

Working data for `../decision_families_survey.md` (the "forest for the
trees" survey) and the rows it filed.

- `stamp_inventory_raw.md` — lane `decsurvey`'s verbatim seed inventory
  (stamp-led), kept as the survey's source record.
- `decfb0/` — [DEC-FALLBACK] STEP 0 census (lane `decfb0`, 2026-10-08), a
  MEASUREMENT with no compiler change. `run_census.sh` is the entry point:
  `build_ref.py` copies src/ into `build/decfb0/tree`, patches ONLY the copy
  with stderr `DECFB` probes and builds four scratch compilers (shipped
  limits + three `-D`-lowered reference variants, run_size_term.sh /
  run_n1_budget.sh's shape); `census.py` compiles every distinct .rxt
  corpus block (via `--list-source`) with each; `summarize.py` writes
  `results.md`. The probed build's output is byte-identical to `build/pcrec`
  over the whole corpus (0 BYTES_DIFF rows). Report:
  `../../dev/lanes/decfb0_report.md`. Re-run after a compile.c change that
  moves the anchors (build_ref.py fails loudly on a drifted anchor).
