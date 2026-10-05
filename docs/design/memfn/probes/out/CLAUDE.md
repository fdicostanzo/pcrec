# docs/design/memfn/probes/out/ — archived probe transcripts

`callcost.<box>.<compiler>.txt`: verbatim `callcost` output under a
provenance header (box, OS, compiler, probe commit, load note). Evidence for
requirements.md §2.4, never read by a check. Mac files are directional only.

R1b (isa_selection.md): `isacost.mac.{gcc,clang}.sel-{base,wide}.txt`
(`--isa-report` then the timing table, under the same header shape) and
`fmvdarwin.mac.txt` (§0 items 3-4's evidence). The Linux transcripts land
in `build/memfn_linux/<stamp>/` from `../linux_run.sh` and are archived
here by whoever reads them.
`survey_*.txt` (R2, lane memfnsurvey): `survey_chk.{mac.arm,mac.arm-asan,
rosetta.x86,rosetta.x86-asan}.txt` (correctness; Rosetta 2 runs x86 SSE4.2/
AVX2 code for correctness only, never timing), `survey_tim.mac.{gcc,clang}.txt`
and `survey_pcrejit.mac.txt` (timing, directional). Each carries its own
box/compiler/source-commit header.

`twins/` (R1d, lane memftwin): one Mac run of `../twins/twins_run.sh`
verbatim — `run.log` (every build, `--check` and ASan line), `ta.*`,
`tb.*`, `tc.*` (timing, directional) and `tc_asm.*` (the disassembly
diffs), each under the run's provenance header; plus `check.rosetta.txt`
(the x86 SSE2/SSSE3/AVX2 builds' `--check` under Rosetta 2, correctness
only). The Linux run lands in `build/memfn_twins/<stamp>/`.

`twins/r4b/` (R4b, lane memfnr4b, memfn R-1): the Mac DIRECTIONAL run of
`../twins/tb_r4b.c` — `tb_r4b.mac.gcc.txt` (gcc-16 NEON, raw `R` rows under
a provenance header) and its rendering `tb_r4b.mac.gcc.table.md`
(`tb_r4b_table.py`); `check.{gcc,clang,asan}.txt` (NEON) and
`check.x86.{x86-64,x86-64-v3,asan}.txt` (clang `-arch x86_64` under
Rosetta 2, correctness only). `twins/r4b/linux/` is the Linux VERDICT run
of `../lxrun/memfn_r4b.sh` (ubuntubudu, gcc 15.2, probe 4ecea50b, pin
d4d9ed90, R4B-DONE status=0, 2026-10-05), copied back from its OUTDIR
(`scratch_lx/r4b2`): `run.log`, `header.txt`, `check.*.txt`, `tb.*.txt`
(raw rows per build x launch), `readings.{gcc,clang}.md` (gcc is the
verdict; clang directional), `pcrec.build.log`. Read in
docs/dev/lanes/memfnr4b_report.md §9.

`linux/` — the 2026-10-05 Linux x86 run (linux_run.sh + twins_run.sh +
lane lxrun's L-2/L-4/survey scripts), archived by lane lxread with
provenance headers; read in `../../linux_results.md`. Own CLAUDE.md.

Maintenance: update this file when files are added/removed or change roles.
