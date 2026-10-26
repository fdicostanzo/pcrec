# studies/selflip — probe files for lane selflip (facts only, nothing built)

- `probe.c`: times `rx_search` (one-shot, or find-all with FINDALL=1) over a subject file; links one generated artifact (`rx.c`/`rx.h`).
- `run.sh NAME PATTERNFILE ENGINE SUBJECT ITERS [pcrec flags]`: generates `out/NAME_ENGINE/`, builds the probe once, prints ns/call. `out/` is gitignored.
- `memmem_probe.c`: glibc `memmem` find-all, the lower bound for a kit-proven literal span.
- `capjoin.py`, `sweep.py`: join the bench's 2026-10-26 subject-grain tsv (auto-caps vs vm-caps) to each pattern's stamps and its `cover` verdict (the sweep is compile-only, ~1,000 invocations: run under `scripts/boxlock run`).
- `sweep.tsv` (219 patterns), `capjoin.tsv`: the sweep's outputs.
- Timings are indicative only (shared box); the bench's numbers are the record. Report: docs/dev/lanes/selflip_report.md.
