# docs/design/memfn/probes/out/linux/twins/ — R1d's twins on Linux x86

`../../../twins/twins_run.sh`'s output from the 2026-10-05 Linux run (see
`../CLAUDE.md` for box and provenance), verbatim under an `ARCHIVED` header:
`run.log` (every build, `--check`, ASan line; trailer `MEMFN-TWINS-RUN
COMPLETE ... fails=0`), `header.txt`, `ta.*` (T-A, five builds: gcc SSE2/
SSSE3/AVX2, clang SSSE3/AVX2), `tb.*` and `tc.*` (T-B, T-C, all six builds)
and `tc_asm.*` (T-C's disassembly-diff summaries; the per-function `.s`
files stayed on the box). Read in `../../../../linux_results.md` §6.

Maintenance: update this file when files are added/removed or change roles.
