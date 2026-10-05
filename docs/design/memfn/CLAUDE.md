# docs/design/memfn/ — the [MEMFN] memory-functions project's design record

`[MEMFN]` (docs/dev/plan.md, opened by Frank 2026-10-04): a general-purpose
project of byte search/compare kernels that pcrec could later EMIT into its
self-contained generated C. Steps: R1 requirements (here), R2 survey of
existing projects against them, R3 findings to Frank, who decides adopt /
fork / a new separate repo. Deliverables live here until that ruling.
Nothing here touches pcrec's emission (D91).

## Files

- `requirements.md` — R1 (lane memfnreq, 2026-10-04). The function menu
  (F1-F13, exact semantics, compare_stack.md sites, ranked), the
  binding-form criterion (out-of-line call / local helper / inline /
  injected, its cost model and a first-match decision table), the
  requirements that follow (RB-1..RB-9), non-functional requirements
  (N-1..N-11), the survey's scored rubric (§5), the unknowns (§6) and three
  questions for Frank (§7, headed by the licence of generated output).
- `survey.md` — R2 (lane memfnsurvey, 2026-10-04). 21 open-source projects
  scored against requirements.md's rubric (licence under both Q1 readings,
  form, ISA, F coverage, bounds behaviour, line-by-line M/H scores), the
  F × project coverage matrix, the ideas to harvest per F item with
  file/function citations, a per-F verdict (BUILD by translating Rust
  `memchr`, F4/F5 classifiers per ISA from published designs; nothing
  adopt-as-is), the gaps nobody fills, and what is owed on Linux.
- `probes/` — R1's measured probe: `callcost.c` (libc `memchr` against
  inline scalar/SWAR/NEON-or-SSE2 forms, by span length, plus the fused
  two-needle pass against two libc calls) and `probes.mk` (build, the
  exhaustive `--check`, the ASan build, disassembly). Built into
  `build/memfn_probe/` (gitignored); never built by pcrec's make. Also R2's
  survey harness (`survey_*.c`, `survey_build.sh`), built against scratch
  clones of the third-party sources, never vendored.
- `probes/out/` — archived transcripts (`callcost.mac.{gcc,clang}.txt`),
  each with a box/compiler/provenance header. Mac numbers are directional
  only (D144 addendum 1); the Linux run is owed (requirements.md §2.6).
  R2's `survey_*.txt` (correctness incl. Rosetta 2 x86, timing, PCRE2-JIT).

Maintenance: update this file when files are added/removed or change roles.
