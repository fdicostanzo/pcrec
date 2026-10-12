# docs/dev/optloop/lossreview/vm/ — instruments and data behind `../vm.md`

Lane `lrvm`, 2026-10-11. Nothing here is built or run by `make`. Nothing
writes in pcrec-bench: the subjects are regenerated in a `git archive` copy.
Scripts take their paths from the environment: `LR` (a scratch dir, e.g. the
worktree's gitignored `build/lr`), `PCREC` (the compiler) and `BENCHCOPY`
(the archive copy).

- `regen_subjects.sh OUTDIR` — archives pcrec-bench (read-only), runs the
  syntax/capability/bounded/loglines throughput and short-subject generators
  in the copy, and sha256-checks every subject against the manifests. At
  bench d359564f it reports 31 + 278 OK.
- `vmcells.txt` — the 30 VM-route patterns analysed (set/pattern).
- `cells_vm.py`, `cells.tsv` — the bench's set-grain numbers per VM cell:
  every comparator, ns lost vs jit and vs the best non-vectorscan peer, and
  whether pcre2-interp is also slower. The input is the 10-11 gap report's
  `gap_rows.json`.
- `gcovrun.sh SET/PATTERN [pcrec args]`, `fadrv.c` — the line-count
  instrument. It compiles with the bench's flags, builds `--coverage`, runs
  the bench's find-all loop over the throughput subjects and writes
  `$LR/gcov/<name>/rx.c.gcov`. `gtop.py` prints the hottest lines.
- `gcov_counts.py`, `gcov_counts.tsv` — per-cell event counts summed from
  the gcov lines by their emitted text: attempts, VM-hat seek iterations,
  DFA hat skips, forward and attempt DFA steps, memchr calls, span
  iterations, frames popped, trail-reset and trail-pop iterations, and
  `rx_span_match` calls.
- `stayprobe.py ART.c SUBJ...` — simulates a DFA artifact's forward machine
  on subjects and reports the hottest states, their self-loop byte counts
  and whether a stay table exists. It shows the `\b` word-wait state that
  M2.1's 192-byte rule declines.
- `twins/` — the hand twins:
  - `twin.py`: mechanical transforms of an emitted artifact (`static_seam`,
    `trail_free`, `seek_memchr`, `stay=STATE`, `precheck=BYTE`,
    `stepset=BYTE`, `rewind`).
  - `run_twin.sh`: builds base and twin the bench's way and answer-checks
    them over throughput, short and `extra_subjects.py` subjects.
  - `fatime.c`: the quiet-slot timing driver.
  - `twins.tsv` (20 twins, their questions, their answer-check counts) and
    `run_all_twins.sh`.
  Timing is OWED; see `../vm.md` §5.
