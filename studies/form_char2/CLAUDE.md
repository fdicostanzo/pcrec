# studies/form_char2/ — [FORM-CHAR2] fold vs table measurement

Report: docs/dev/lanes/formchar2_report.md. Never built by pcrec's make. Real-compiler arms (default /
-fno-cls-fold / -fno-cls-fold -fno-cls-pack), no hand twins.

- `count_sites.py`, `site_counts.py`, `fn_counts.py` — static instruction/size counts (objdump).
- `fold_census.py` — corpus + pcrec-bench (read-only) fold-site population.
- `witnesses.py`, `build.py`, `drv.c`, `run.py`, `analyze.py` — timing harness (11 interleaved rounds, null-control arm, load gate).
- `results/` — committed outputs (arm64 scratch timing is directional only; x86 timing owed, see report).
