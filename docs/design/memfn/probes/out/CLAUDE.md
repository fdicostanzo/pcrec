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

`linux/` — the 2026-10-05 Linux x86 run (linux_run.sh + twins_run.sh +
lane lxrun's L-2/L-4/survey scripts), archived by lane lxread with
provenance headers; read in `../../linux_results.md`. Own CLAUDE.md.

Maintenance: update this file when files are added/removed or change roles.
