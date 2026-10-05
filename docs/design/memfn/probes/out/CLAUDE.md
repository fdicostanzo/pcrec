# docs/design/memfn/probes/out/ — archived probe transcripts

`callcost.<box>.<compiler>.txt`: verbatim `callcost` output under a
provenance header (box, OS, compiler, probe commit, load note). Evidence for
requirements.md §2.4, never read by a check. Mac files are directional only.

R1b (isa_selection.md): `isacost.mac.{gcc,clang}.sel-{base,wide}.txt`
(`--isa-report` then the timing table, under the same header shape) and
`fmvdarwin.mac.txt` (§0 items 3-4's evidence). The Linux transcripts land
in `build/memfn_linux/<stamp>/` from `../linux_run.sh` and are archived
here by whoever reads them.

Maintenance: update this file when files are added/removed or change roles.
