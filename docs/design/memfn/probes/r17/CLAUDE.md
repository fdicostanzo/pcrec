# docs/design/memfn/probes/r17/ — R-17's scoping instruments and twins

Lane r17s (2026-10-11), memfn request R-17 (`memfn/docs/requests.md`):
FIND sites scanning a small, one-cube or one-range byte set. Report:
`docs/dev/lanes/r17s_report.md`. Nothing here is built by pcrec's make; every
binary goes to a scratch directory (the worktree's `build/`, never `/tmp`).

- `census.py` — the FIND-site population by SET SHAPE, read off EMITTED C (no
  traced build): every PF/VM-hat table walk (`while (P < N && !T[S[P]]) P++;`),
  its table parsed from the artifact, its role from the table's suffix
  (`can_begin_match` DFA prefilter, `start_bytes` DFA hat, `start_set` VM
  hat), the set classified (|S|, one cube, one range, runs, greedy prime-cube
  cover); also PF memchr finds and offset-skip `__body` helpers with no
  memchr. Three modes: the .rxt corpus (two streams, default and
  `--engine=vm`), the bench's own patterns (`--bench`, read-only, compiled as
  the pcrec-auto testee), or `--files` (classify given artifacts).
- `summarize.py` — rolls `sites.tsv` up by the form family a row would key on.
- `gen_twins.py` — renders the hand twins as C text (`twins_gen.h`), one
  specialized function per (cell, form): `table` (today), `memchr`, the
  bounded memchr cascade `mcK`, `swar` (an OR of eq/cube/range terms on
  uint64), `sse2`/`avx2` (vrun.c-style compare, overlapped final block). Its
  header states the kernel contract and every form's in-range argument.
- `check.c` — the EXHAUSTIVE answer check of every twin against the byte loop
  (all 256 bytes at every position and phase, one probe over three
  backgrounds at every (n, p, lo), random alphabet subjects, guard pages on
  both sides; hi = n and n - 1; n 0..80, every lo). `PLANT=1` plants a wrong
  reference: the check must then catch every cell.
- `time.c`, `run_time.sh` — step 2's timing harness (WRITTEN, NOT RUN by
  r17s): findall and percall regimes, density grid incl. a dense control,
  64 KiB and 1 MiB, a no-read floor row, calibrated >= 50 ms samples
  interleaved across forms, answer checksum per sample (`VOID` on a
  mismatch). `DRYRUN=1` prints the 169 pinned invocations.
- `out/` — archived results: `check.txt` / `check_planted.txt` (the check and
  its planted control), `check_asan_ubsan_n40.txt` (the same check under
  ASan+UBSan at n <= 40), `census_corpus.log` (the corpus roll-up with the K35
  body population), `summary_corpus.md` / `summary_bench.md` (census roll-ups).
  The timing output is OWED (step 2's slot).

- `gen_twins_r2.py`, `time_r2.c`, `check_r2.c`, `run_time_r2.sh`,
  `summarize_r2.py` — R-17 REVISION 2's follow-up measurement (lane r17r5,
  2026-10-12; `../../setfind.md` §13), WRITTEN; compiled, checked, dry-run by
  lane r17dry (`docs/dev/lanes/r17dry_report.md`: check 0 mismatches, planted
  152/152, ASan+UBSan clean; `check_r2` takes optional cell names for a
  reduced run); the TIMING run is owed to a kit slot. `gen_twins_r2.py` loads `gen_twins.py` by
  path and adds the synthetic cells (`syn4`/`syn5`/`syn6`/`syn8`: exactly k
  terms; `x80`: a range crossing 0x80) and the STATEFUL twins (mask8/mask64
  at SWAR, SSE2 and AVX2, `mask64i_swar` with the refill not inlined,
  `ring_swar`/`ring_avx2`) and the ADAPTIVE twins (`adapt_swar`,
  `adapt_avx2`, `adapt_mask`), all over one state type `sstate`.
  `-DPLANT_STALE` plants a stale-state defect. `check_r2.c` is the
  exhaustive candidate-SEQUENCE check (Q1-Q7 on F1-F4 subjects, n <= 160):
  stateful == stateless swar == byte loop, with population counts and the
  planted control. `time_r2.c` is time.c's timer with the state-reset axis
  (`-k`), clustered placement (`-g`), misaligned offsets (`-A`), measured
  ppm and run profile for real subjects, and a perf mode (`-P`).
  `run_time_r2.sh` runs the check and the planted check, then the grid, then
  the `perf stat` branch pass. Its last line is
  `R17R2 TIMING COMPLETE rc=N rows=K void=V perf=P`, and it runs about
  1 h 45 min (estimated). `summarize_r2.py` reports the noise band, raw and
  d_floor, the per-cell losing set, the verdict question, K, and the branch
  misses.

Maintenance: update this file when files are added/removed or change roles.
- `reading_slot.md` — the kit manager's reading of step 2's timing run (2026-10-11, main's GO, core 14): every form beats `table` except hit-dense find-all at 300k ppm (SWAR +20%, memchr +18%, avx2 +24% worst, on the bench's dense controls), so the general row needs N1's density facts or a panel-ruled decline. Data in `out/slot/`.

- `reading_slot2.md`, `analyze_slot2.py` — lane r17rd (2026-10-12): the
  reading of the follow-up timing run (`out/slot2/`, 9,654 rows, void 0) and
  the script that recomputes its tables from `times.tsv` (analysis only;
  sections verdict, reset, mask_ring, adapt, k, percall, losers, perf, all;
  `python3 -I analyze_slot2.py out/slot2 <section>`). Answers the verdict
  question, the reset axis, mask vs ring, the adaptive switch, K, percall,
  the per-width recommendation and the unmeasured regimes.

- `upa/`, `reading_upa.md` — lane r17upa (2026-10-12): USES PER ACTIVATION of
  every set-FIND site on pcrec-bench's own subjects (counts only; setfind.md
  §9.2's (P), the bench request's Q3), from an instrumented copy of the
  emitted C, driven as the bench's `timed.c` drives it, answer-identical and
  oracle-checked. Headline: search-short is at 1 use per call (below B_EVEN)
  everywhere R-17 names. In find-all, `adl` and `alt2` carry state (medians
  31-20,280 and 6), while the other named cells sit at 1 use but sparse. The
  state-lost dense corner is the bench's dense controls (`[0-9]`/`[a-z]`/`\w`
  on dense subjects), not the named cells. Own CLAUDE.md.
- `slot24_verdict.txt`, `slot24_triage.md` — R17-a's heavy validation (slot24, 2026-10-12, tip c6a3bfea vs main a080c69a) and the triage lane's (s24tri) classification of its five red lines. R17-a is a zero-mover: every sweep reads 0 movers, G2 has 0 failed, and S846-S849 are detected. The reds are main's pre-existing items (the emit_sweep pins, the utf8 `--extra` composition floor, the review-file line citation) plus mech S284 (expected UNDETECTED). The kit's own red was the N2 floor: `pf_walk` and `precheck_assign_byte` were re-pinned in tests/memfn/row_floors.tsv, and the re-read is clean.
