# studies/selflip — probe files for lane selflip (facts only, nothing built)

- `probe.c`: times `rx_search` (one-shot, or find-all with FINDALL=1) over a subject file; links one generated artifact (`rx.c`/`rx.h`).
- `run.sh NAME PATTERNFILE ENGINE SUBJECT ITERS [pcrec flags]`: generates `out/NAME_ENGINE/`, builds the probe once, prints ns/call. `out/` is gitignored.
- Timings are indicative only (shared box); the bench's numbers are the record. Report: docs/dev/lanes/selflip_report.md.
