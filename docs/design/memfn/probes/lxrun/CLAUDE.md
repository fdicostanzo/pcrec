# docs/design/memfn/probes/lxrun/ — lane lxrun's Linux hand-off scripts

The scripts lane lxrun wrote for the 2026-10-05 Linux run (driver
`scratch_lx/run_lx1005.sh`, kept in `../out/linux/lx1005_driver.txt`),
copied verbatim from the box by lane lxread. Linux x86 only; never built or
run by pcrec's make; each writes only under its OUTDIR argument.

- `memfn_l4.sh` — isa_evaluation.md §3.3 L-4: does a plain `-march=x86-64-v3`
  object, `.so` or executable carry `GNU_PROPERTY_X86_ISA_1_NEEDED` unasked
  (and a pcrec artifact, with and without `-mneeded`).
- `memfn_l2.sh` — L-2: twelve bench patterns' artifacts (alpha_k82.sh's
  compiler, subjects and driver) at gcc `-O2` vs `-O2 -march=x86-64-v3`,
  answer identity then interleaved timing; floor = the larger arm's launch
  spread. Known defect: `ev()` is called with one argument under `set -u`,
  so the build section's ymm/BMI counts print nothing.
- `memfn_survey_lx.sh`, `survey_tim_x86.c`, `survey_pcrejit_lx.c` — survey.md
  §10.1: the x86 port of `../survey_tim.c` (StringZilla westmere/haswell,
  glibc, musl at the pins in its header) and `../survey_pcrejit.c` against
  the system libpcre2 (10.46).

- `memfn_r4b.sh` — R4b's (lane memfnr4b, memfn R-1) Linux VERDICT run:
  subjects, pcrec at d4d9ed90 + `../twins/gates_sync.sh`, tb_r4b builds
  (gcc SSE2/AVX2, clang directional, gcc ASan), `--check` (aborts on any
  failure), pinned launches, `../twins/tb_r4b_table.py` readings. Run from
  a checkout carrying it, with an OUTDIR; ~20-25 min; last line
  `R4B-DONE status=<n> dir=<OUTDIR>`.
- `memfn_r4c.sh` — R4c's (memfn R-4, M1 migration) Linux VERDICT run, from
  a worktree at the kit branch with the expected TIP as its argument:
  build; the zero-mover gate vs REF (e6e6d6eb); make test; the 35 mech
  rows, ONE id per matrix call; the memfn-simd axes pair; full C11; I2
  (`--arms start`, every --list-axes flag (the memfn-simd pair as inertness arms) and tune
  position x both comment tiers, the M1 denies at utf8; each arm judged by
  `memfn_r4c_i2.py`). Logs go to build/scratch/r4c_lx/; ~6-7 h; last line
  `R4C-LX-DONE gate= test= reds= mech= axes= c11= i2= i2arms= wall=`. PASS
  is every rc 0 and reds=0. RERUN mode (lane r4clx): env STEPS selects among
  gate,test,mech,axes,c11,i2 (unselected steps read `skip`), TESTSECTIONS
  runs `make <sections>` for the test step, MECHROWS the mech ids, I2ARMS an
  ERE over arm labels; the header has an example.
- `memfn_r4c_gate.py` — judges an emit_sweep log for R4c: exit 0 iff the
  self-check passed, streams 1-4 have 0 movers at their reach floors, and
  the only dump mover is --list-axes adding exactly the two declared
  memfn-simd rows. emit_sweep has no declared-mover input; this keeps an
  accepted red out of the gate.
- `memfn_r4c_i2.py` — the I2 judge (lane r4clx): one arm's emit_sweep log,
  exit 0 iff every REAL RUN stream reads movers=0 asymmetric=0, no stream
  is dumps, and every other failure line is DECLARED for that arm in its
  table (each with its measured reason) and no declaration is stale.
  `--selftest LOGDIR` doctors copies of real logs (i2_3, i2_9 of the
  91f5b607 run) into five planted reds.

Transcripts: `../out/linux/`. Maintenance: update this file when files are
added/removed or change roles.
