# studies/u8pick_twin/ — [U8-PICK] STEP 0, the two-artifact twin

Lane `u8pick0` (2026-10-09, sonnet, MEASUREMENT ONLY; nothing under `src/`
changed). One literal compiled `-e byte` and `-e utf8`, then timed on the
bench's own seven utf8 throughput subjects, interleaved on one pinned core.
The question and verdicts are in `docs/dev/lanes/u8pick0_report.md`; this
directory is the instrument and the raw results. Scratch tier, Linux dev box
(Ryzen 7 7700X), box NOT quiet (load1 9-60 recorded per cell).

## Arms (all linked into ONE process; passes interleave A,B,C,P,S,M)

- `A` = `-e byte` artifact (prefix `pa`); `B` = `-e utf8` artifact (`pb`), today's compiler.
- `C` = `-e utf8 --analysis u8prior` (`pc`): the scratch STRUCTURAL UTF-8 prior,
  the experiment behind the report's fix sketch (ASCII default rows at 80%, five
  script blocks equal-share at 20%; assumptions, not a measurement, not derived
  from any bench subject).
- `P` = `-e utf8` from the BENCH PIN `c4c70f2c`'s compiler (`pd`): the calibration
  arm that maps this box onto the bench box (factor per cell, ~2.0-3.4x).
- `S` = naive AVX2 packed-pair find-all, `M` = glibc `memmem` find-all: proxies
  for the peers' algorithm class, for plain-literal cells only. NOT rust's or
  RE2's code and not tuned; `S` is a weak floor (do not read it as "SIMD
  can't beat pcrec").

## Files

- `run_study.sh` — reproduces everything from a built pcrec worktree
  (`WORK_DIR` defaults to `build/u8`, gitignored).
- `gen_subjects.py` — regenerates the bench's 7 throughput subjects READ-ONLY
  (imports the bench's `utf8text`, writes no bytecode there), sha256-checked
  against the bench's `manifest_throughput.tsv` (7/7 match).
- `cells.tsv` — the 12 `lit-*` patterns, copied from `bench/utf8/patterns/`.
- `build_cell.sh`, `drv.c` — per-cell compile + the find-all driver (the bench
  adapter's loop, `testees/pcrec/timed.c`: advance to the match end; answers
  are FNV-hashed per arm, so identity is checked in the same process).
- `run_all.sh` — cell x subject x 15 passes, `taskset`-pinned, load1 recorded.
- `summarize.py` — answer identity, median +- sd, the `2*(sd_a+sd_b)` test,
  the bench-style pooled table. `project.py` — projects each arm onto the bench
  box with the cell's own P calibration (a PROJECTION, not a measurement).
- `stamps.py`, `picktable.py`, `bytecounts.py` — the stamps / memchr bytes read
  off the emitted C, each pick's total stop count over the subjects against the
  literal's rarest byte (an oracle bound), and the raw byte counts.
- `gen_u8prior.py` — writes the scratch `u8prior.rxt` (451 KB; regenerated, not committed).
- `mk_norev.py` — the hand-twin that replaces the reverse-pass start recovery
  with `start = end - WIDTH` (refutes the reverse pass as the per-match cost).
- `results/` — `run_core13.tsv` (raw, 15 passes), `summary_core13.txt` and
  `summary_core7.txt` (a second core, same ratios), `projection_core13.tsv`,
  `picktable.tsv`, `bytecounts.tsv`, `stamps.tsv`, `twin_norev_*`, `facts_*`
  (`--emit-facts` for the four decisive cells).

Bench access was READ-ONLY (reports and pattern/generator files); the bench was
not run and nothing was written there.
