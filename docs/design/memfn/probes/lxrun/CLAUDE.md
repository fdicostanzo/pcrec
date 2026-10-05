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

Transcripts: `../out/linux/`. Maintenance: update this file when files are
added/removed or change roles.
