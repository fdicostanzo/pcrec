# docs/design/memfn/ — the [MEMFN] memory-functions project's design record

`[MEMFN]` (docs/dev/plan.md, opened by Frank 2026-10-04): a general-purpose
project of byte search/compare kernels that pcrec could later EMIT into its
self-contained generated C. Steps: R1 requirements (here), R2 survey of
existing projects against them, R3 findings to Frank, who decides adopt /
fork / a new separate repo. Deliverables live here until that ruling.
Nothing here touches pcrec's emission (D91). **Ruled 2026-10-05 (D146,
D147, Q35/Q36): the kit is pcrec-memory-functions, in-tree at `memfn/`
(its own CLAUDE.md, journal and request ledger); this directory stays
its DESIGN record.**

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
  **REVISION 2 (lane memfnk0, 2026-10-05), on Frank's Q12 ruling**:
  the kit gains K0, the CAPABILITY-AND-PRICE QUERY (§7). pcrec holds an
  opaque ISA token (default `portable`, fixed), asks an arch-neutral
  query, and gets measured prices back. ONE arch-blind `kit` row per
  table selects a kernel only where its price DOMINATES the next row's
  over the site's proven span × density box. The calibration data is
  `memfn/cal/<arm>/` (raw transcript -> generate.py -> prices.tsv), and
  v4/SVE are UNPRICED. Revision 1's vector rows, BASE/DECLARED and
  [OPT-SETS]'s ISA sub-panels are removed. Q18-Q23 are new, and the
  R4 order is revised. Read §R2 first.
  **REVISION 3 (lane memfndel, 2026-10-05), on D146 (DELEGATION; the
  project is named pcrec-memory-functions)**: K0 is superseded. pcrec
  hands the kit a SITE (`mf_site`: an op over a conjunctive predicate of
  byte-set and masked-run terms, proven span, anchoring, density hints,
  a policy word) and gets code back through text hooks (§8). pcrec
  decides only which sites are delegated (by op type) and which profile
  each gets (`baseline` = its own frozen pre-migration text, `portable`,
  `native`). Its scalar forms migrate into the kit as baseline arms,
  customer-ordered, implement-then-replace at zero movers (§9). Guards:
  kit on/off timing, the kit's tests, the abi ritual for kit byte moves,
  C4 rebuilt, cross-target syntax (§10). In-tree `memfn/` first (§11);
  option_sets.md's family and the R4a-R4j order (§12); Q24-Q34 (§13).
  Read §R3 first: its table maps every r2 panel finding to carried /
  moved inside the kit / dissolved.
  **REVISION 4 (lane memfndel4, 2026-10-05), on the r3 light panel
  (`../../dev/reviews/2026-10-05-r3-memfn-delegation.md`, 27 findings)**:
  the contract is rebuilt from the emitters' actual shapes (§14: EXPR /
  STMT / FUNC site forms, ASSIGN and ON_MISS handoffs, indent and notes,
  ADVANCE's counter and `peek`, non-wrapping ranges with declared EMPTY
  outcomes, a lower `floor`, REQUIRED/OPTIONAL terms, ALL_PRESENT with a
  returned predicate, per-artifact `mf_art` with helpers before first
  use). §15 reproduces every M1 site shape byte for byte. The shipped
  denies' fates (§14.10); the stamp on every artifact per Frank's Q3
  (§18); every remaining pcrec pricing of kit search code with its fate
  (§19); M1 narrowed and sequenced (§16); G1 on a pcrec-side diff (§17);
  two inbox files, `-fmemfn-native` default OFF, symbol policy (§20);
  the three standing questions (§21); build order (§22); Q35-Q49 (§23).
  Read §R4 first.
  **REVISION 4.2 (lane memfnsetup, 2026-10-05), on D147 (layers) and
  Frank's Q35/Q36 rulings**: the kit's scalar arms ARE the scalar layer,
  live and improvable; SIMD (native arms) is a layer that must beat the
  CURRENT scalar; every reading reports SIMD-off and SIMD-on. The frozen
  `baseline` profile becomes a per-migration-step comparator only; the
  `memfn-off` bits, `off.tsv` and the `pcrec[memfn-off]` testee are
  withdrawn; each kit change's own `--memfn-deny=` is its OFF arm; the
  stamp reports the SIMD layer. Q35/Q36 ruled (§23), Q50-Q52 new. Read
  §L first. The kit itself now lives in-tree at `../../../memfn/`.
  **REVISION 4.3 (lane memfnr43, 2026-10-05), Frank's rulings folded
  (D147 addenda 1-7)**:
  - Q35-Q42 and Q50 RULED; Q51/Q52 REJECTED;
  - ONE SIMD switch, `-fno-memfn-simd` / `-fmemfn-simd`, OFF by default
    until the SIMD hold lifts:
    - OFF = portable C (plain C, SWAR, libc);
    - ON = optimized for a specific CPU, may not run elsewhere;
    - the contents of ON are the kit's per-site choice, cascades
      included (K-6);
  - EVERY search site migrates (Q42 reversed), under a checked site
    manifest (C17). The memchr ratchet ends at 0;
  - the planner moves live at M5, with M5′ as the adoption event;
  - stamps: `MEMFN_FORMS` per Q39 plus a `MEMFN_LIBC` record;
  - §22's build order and §23's list rebuilt; Q53-Q55 new.

  Read §R4.3 first: its §R4.3.0 maps each ruling to where it now
  lives.
  **REVISION 4.4 (lane memfnr44, 2026-10-05), D147 addenda 8-9 folded**:
  - Q43 RULED: aarch64 SIMD-on forms are not accepted until Mac
    measurements are admitted as verdict-grade or an aarch64 Linux box
    exists;
  - Q44, Q45, Q46, Q48, Q49 RULED as recommended;
  - Q47 REFINED: pcrec keeps ONE axis (`-fmemfn-simd`) and the kit's
    per-form switches are its OWN option namespace, `--memfn=<opt>[,…]`,
    from a kit-owned registry (`memfn/src/options.def`), passed through
    uninterpreted. `--list-axes` prints a `memfn` section from it, one
    enumeration point for `test-axes`, the identity gates and the
    registry check, with a spec-pinned member-count floor as the
    independent control. The generated-axis-rows design and
    `--memfn-deny=` are withdrawn;
  - the open questions are Q53-Q55 only.

  Read §R4.4 first: its §R4.4.0 maps each ruling to where it now lives.
  **REVISION 4.5 (lane memfnr45, 2026-10-05), R-1's Linux verdict and
  D149 folded; rules nothing (Q53-Q55 stay open)**: the lead order is
  part of the composite site's form (§15.5); R4b DONE, R4d's trigger
  MET at SIMD-off on union-select (§22); kit forms obey D149 (§8.6
  K-7). Read §R4.5 first.
  **REVISION 4.6 (lane memfnr46, 2026-10-05), the r5 panel's 23
  findings applied; rules nothing (Q53-Q55 stay open, refined)**: the
  set-leads lead is OPTIONAL on DFA-scan routes and REQUIRED on no-DFA
  routes (K65); `use` is a per-instance fact; the composite's `empty` is
  MISS; one predicate numbering; line citations in §14-§16 replaced by
  function names. Read §R4.6, then §R4.5, first.
- `twins.md` — R1d (lane memftwin, 2026-10-04), the D77 measurement "does a
  kernel TAILORED to the pattern beat a fixed generic one": T-A set
  classifier per shape vs the generic nibble lookup, T-B a fused scan+verify
  vs today's emitted K82 run gate, T-C a `static const` descriptor through
  one header kernel vs the hand kernel (disassembly diff). Absolute ns
  tables (Mac, directional), a verdict per T, the Linux queue. Evidence in
  `probes/twins/` and `probes/out/twins/`.
- `linux_results.md` — the Linux x86 RESULTS (lane lxread, 2026-10-05,
  read-only): lane lxrun's quiet-box run on ubuntubudu read against every
  owed Linux question — callcost (U-1), isacost (U-8..U-10, U-12), isanote
  (U-11), isa_evaluation.md's L-2 and L-4, the twins on SSE2/SSSE3/AVX2 and
  the survey's x86 timings + PCRE2-JIT 10.46 — each beside its Mac number,
  with a <=12-line decision-inputs summary for Q2/Q4-Q17 at the top, the
  per-question answers (§8) and the corrections owed to the earlier notes
  (§9). Headline: glibc's F is 3.24 ns, fusion inverts above ~512 B at SSE2
  width, no level customer yet (L-2), and ld.so enforces the ISA marker for
  dynamic executables and `dlopen` only.
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
  `probes/out/linux/` holds the Linux run's transcripts (2026-10-05) and
  `probes/lxrun/` the hand-off scripts that run used beyond `linux_run.sh`
  (L-2, L-4, the x86 survey); both read in `linux_results.md`.

Maintenance: update this file when files are added/removed or change roles.
