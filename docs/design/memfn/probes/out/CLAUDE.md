# docs/design/memfn/probes/out/ — archived probe transcripts

`callcost.<box>.<compiler>.txt`: verbatim `callcost` output under a
provenance header (box, OS, compiler, probe commit, load note). Evidence for
requirements.md §2.4, never read by a check. Mac files are directional only.

`survey_*.txt` (R2, lane memfnsurvey): `survey_chk.{mac.arm,mac.arm-asan,
rosetta.x86,rosetta.x86-asan}.txt` (correctness; Rosetta 2 runs x86 SSE4.2/
AVX2 code for correctness only, never timing), `survey_tim.mac.{gcc,clang}.txt`
and `survey_pcrejit.mac.txt` (timing, directional). Each carries its own
box/compiler/source-commit header.

Maintenance: update this file when files are added/removed or change roles.
