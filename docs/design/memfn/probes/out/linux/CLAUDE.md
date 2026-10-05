# docs/design/memfn/probes/out/linux/ — the [MEMFN] Linux x86 transcripts

The one owed Linux run of the memfn probes (ubuntubudu: AMD Ryzen 5 1600,
x86-64-v3, glibc 2.43, gcc 15.2, clang 21.1.8, `taskset -c 2`), run
2026-10-05 by lane lxrun's serial driver `scratch_lx/run_lx1005.sh` from a
pcrec tree at eb6fe6139, archived by lane lxread. Every file starts with an
`ARCHIVED` provenance header naming its source path on the box; the content
below it is verbatim. Read in `../../../linux_results.md`. Evidence only;
no check reads these files.

- `linux_run.log`, `memfn_linux.driver.txt` — `../../linux_run.sh`'s own
  log (trailer `MEMFN-LINUX-RUN COMPLETE ... fails=0`) and the driver's
  stdout for it plus the appended twins run.
- `header.txt` — the run's box/compiler header.
- `callcost.linux.{gcc,clang,gcc-avx2}.txt` — R1's `callcost` (U-1).
- `isacost.linux.*.{report,sel-base,sel-wide}.txt`, `isa_report.baseline.txt`
  — R1b's `isacost` at x86-64 and `-march=x86-64-v3` (U-8/U-9/U-10).
- `isacost.evidence.txt`, `cpu_level.v3.s` — the VEX-free detection path
  under gcc in a v3 TU, and the IRELATIVE count (U-12).
- `isanote.linux.txt` — what ld.so enforces about
  `GNU_PROPERTY_X86_ISA_1_NEEDED` (U-11). Its source-note rows demand ONE
  LEVEL MORE than their label (`isanote.sh`'s `(1 << (lv + 1)) - 1`);
  `linux_results.md` §3 reads them corrected.
- `memfn_l4.txt` — isa_evaluation.md §3.3 L-4 (`../lxrun/memfn_l4.sh`).
- `memfn_l2.txt` — L-2, today's artifacts at `-march=x86-64-v3`
  (`../lxrun/memfn_l2.sh`); its build section's ymm/BMI counts are lost to
  a script defect, recounted in `linux_results.md` §5.
- `survey_lx.txt` — survey.md §10.1: StringZilla/glibc/musl x86 timings and
  PCRE2-JIT 10.46 (`../lxrun/memfn_survey_lx.sh`).
- `lx1005_driver.txt` — the driver's RC log and script.
- `twins/` — `../../twins/twins_run.sh`'s transcripts; own CLAUDE.md.

Maintenance: update this file when files are added/removed or change roles.
