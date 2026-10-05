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
- `isa_selection.md` — R1b (lane memfnisa, 2026-10-04), Frank's "arch
  checks, dynamic or checkable" ask: the dynamic options (D1-D8: raw query,
  `__builtin_cpu_supports`, cached flag, pointers, ifunc, multiversioning,
  the caller's word), declared-ISA artifacts (x86-64-v1..v4 / armv8-a+sve;
  route M macros against route A target attributes; the `<PREFIX>_ISA_LEVEL`
  stamp and the caller-once `<prefix>_cpu_ok()` check, DESIGNED only; the
  loader ISA marker), the hybrids, a first-match selection table per form
  and D91 budget, RB-10..RB-13, N-12..N-14, rubric H-14..H-16, U-9..U-14,
  and Q4-Q6. Mac findings: selection on a cached word is free, an uncached
  query is about 930 ns, `__builtin_cpu_supports` answers 0 for everything
  on Darwin, and Apple clang has a dyld-resolved multiversioning table on
  Mach-O.
- `isa_evaluation.md` — R1c (lane memfneval, 2026-10-04), Frank's "best
  approach to arch selection crossed with the use case" ask: a matrix of six
  approaches (baseline; per-call test; library dispatch-once; declared-ISA
  artifact; hybrid; (d) multi-artifact selection) against six use cases
  (library call; prefilter and in-loop kernels; unknown CPUs; known box;
  many artifacts; `.so` plugin), the (d) design (variant groups picked by
  the `[ART-MGR]` L1 catalog or L2 loader, the caller holding the result;
  the ISA-marker static-link hazard), a deployment-level first-match table,
  the Linux measurements that could change it (L-2: today's artifacts at
  `-march=x86-64-v3`, not in `linux_run.sh`), Q7-Q11, and an `[ART-MGR]`
  cross-note. Verdict: one mechanism (declared-ISA artifact, selection
  hoisted above it), three pick sites. Design only.
- `integration.md` — R1d (lane memfnmap, 2026-10-04), Frank's "we need to
  integrate; SIMD variants might slot into the decision tables" ask: the
  inventory of every pcrec first-match table that selects a scan / verify /
  classify form (T1-T9, file:line, rows, predicates, denies, emitted text)
  and the seven table-less scan sites (N1-N7); where SIMD joins as ROWS (one
  new nested scan-form table `SCAN_ROWS` with sites, D139's shape; T6's
  `vec-masked`), the sites that do not slot cleanly as built and their
  implement-then-replace fixes; the boundary (option (c): kit K1 per-ISA
  primitives + K2 composition generator with hooks + K3 CLI/reference
  functions; pcrec keeps selection, operands, fusion text, injection); the
  composition model (primitive families, the C1 classifier and C2 shape
  tables, the fixed library as generic-parameter outputs); Q12-Q17; the
  R1d -> R4 plan-row text. Design only.
- `twins.md` — R1d (lane memftwin, 2026-10-04), the D77 measurement "does a
  kernel TAILORED to the pattern beat a fixed generic one": T-A set
  classifier per shape vs the generic nibble lookup, T-B a fused scan+verify
  vs today's emitted K82 run gate, T-C a `static const` descriptor through
  one header kernel vs the hand kernel (disassembly diff). Absolute ns
  tables (Mac, directional), a verdict per T, the Linux queue. Evidence in
  `probes/twins/` and `probes/out/twins/`.
- `probes/` — R1's measured probe: `callcost.c` (libc `memchr` against
  inline scalar/SWAR/NEON-or-SSE2 forms, by span length, plus the fused
  two-needle pass against two libc calls) and `probes.mk` (build, the
  exhaustive `--check`, the ASan build, disassembly); R1b's `isacost.c`,
  `isanote.{c,sh}`, `fmvdarwin.{c,sh}` and `linux_run.sh` (the one owed
  Linux run, both lanes' probes). Built into
  `build/memfn_probe/` (gitignored); never built by pcrec's make. Also R2's
  survey harness (`survey_*.c`, `survey_build.sh`), built against scratch
  clones of the third-party sources, never vendored.
- `probes/out/` — archived transcripts (`callcost.mac.{gcc,clang}.txt`),
  each with a box/compiler/provenance header. Mac numbers are directional
  only (D144 addendum 1); the Linux run is owed (requirements.md §2.6,
  isa_selection.md §4).
  R2's `survey_*.txt` (correctness incl. Rosetta 2 x86, timing, PCRE2-JIT).

Maintenance: update this file when files are added/removed or change roles.
