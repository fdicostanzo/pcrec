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
  **REVISION 4.7 (lane memfnfix, 2026-10-05), the kit's contract after
  G2, and D147 addendum 10 folded**: the kit session's rulings on G2's
  F1-F3 and Q-G2-1..17 as a by-id table (§R4.7.0). VERIFY honours its
  range, `lo > n` is EMPTY, ON_CAND renders NOP, out-of-enum fields
  and seven shapes are refused, an unsatisfiable run byte renders as
  constant false (Q-G2-13, revised), and five caller obligations are
  stated.
  Q-G2-5 is OPEN. Q53-Q55 are RULED: the libc record's refined form
  and N7's scope are the design of record, and no question for Frank
  is open. Read §R4.7, then §R4.6, first.
  **REVISION 4.8 (lane m1b, 2026-10-07), M1b's contract (R-5)**: the
  kit manager's Q-M1b-1..8 as a by-id table (§R4.8.0). §14.8's
  RUN_WORDS sentence corrected (pcrec's `stamp` quotes, so the kit
  writes it through a new unquoted sink op, `stamp_int`); `run_cmp`
  retired and `note` no longer carries the word-load helpers; one
  `MF_SITE_ABI` 3 → 4 bump; bit 43 crosses through one pcrec map table
  into every site's and the art's `denies`; the run-compare rows are the
  kit's (`mf_run_rows`). Read §R4.8, then §R4.7, first.
  **REVISION 4.9 (lane r9d, 2026-10-08), the SIMD layer's design pass
  (request R-9, D147 addendum 11)**:
  - `SCAN_ROWS` is the kit's own form tables (`arms[]`, `rc_row`), and
    SIMD forms are rows with a layer, an ISA level (`memfn/src/levels.def`)
    and their own deny.
  - THE FLOOR RULE: a SIMD-on rendering is the SIMD-off rendering plus
    guarded text (check C18, by the preprocessor at `-mgeneral-regs-only`).
  - Short spans fall to the next rung by a derived reach; the run-time
    cascade is a separate, filed row.
  - The verdict regime covers the box, the core and its SMT sibling, the
    consumer's `-march`, one binary per arm, and a placement control.
  - The acceptance bar is per row and per live level, against the SIMD-off
    compile at the same `-march` and against the row it displaces. Records
    go in `tests/memfn/simd_accept.tsv`, and C19 re-opens them.
  - First batch: the pre-check composite's window run with no lead.
  - Seven findings in R-1 and the box facts (F-R9-1: R-1's 16 B column
    ran the scalar path in every cell).
  - Q-R9-1 was RESOLVED by D144 addendum 4 (§R4.9.10), Q-R9-2..8 were open for Frank (now RULED, below); RQ-1..5 are pcrec-side requests.

  **`[r9]` REVISED AFTER THE D6 PANEL r9** (`../../dev/reviews/
  2026-10-08-r9-memfn-simd.md`, 43 findings, same lane): a zero-mover
  seam R4e′.0 (`fn_rows[]`, BODY/PREFIX slots, for the FUNC part PRE and
  OFS share) precedes batch 1; one shared kit walk and one deny carrier;
  `policy`/`budget` as row-contract fields; SIMD bytes neutral to pcrec's
  length decisions by construction (RQ-3); a two-tier regime under D144
  addendum 4 (official verdicts are pcrec-bench runs on each targeted
  box; the bench submission is §R4.9.5.1); the record's states
  (CANDIDATE/ACCEPTED/STALE/REJECTED); Q-R9-1 RESOLVED, Q-R9-9 new;
  §R4.9.12 maps every finding id to its section.
  `[r9fu]` A follow-up (same lane) measured the glibc-inside trap per
  site: both FUNC BODY rows call glibc `memchr`, so batch 1's rows sit
  over `fn-pair` only and `vrun` over `fn-memchr` is filed with five
  cells (§R4.9.7.1). It also checked `[MEMFN-ENTRYSINK]`: no entry point
  is assumed, and the one candidate is the filed OFS run-pinned form
  (§R4.9.7.2).
  `[D155]` Revised for Frank's rulings (same lane): Q-R9-1..9 are RULED.
  The floor rule is amended so that no function that does work holds an
  `#if`. The FUNC's loop becomes `<fn>__body`, each level is a guarded
  helper, and the FUNC itself, written once, is a selector whose whole
  body is the `#if` chain, one call per arm (§R4.9.2.5, probes; Q-R9-10
  shape (c), D155 addendum 1). SIMD-off routing is step R4e′.0b, a pcrec
  abi event measured as G1 (§R4.9.2.6). C18's leg (b) allows exactly one
  replaced call per SIMD FUNC, and its leg (d) allows a directive in a
  body only in that selector shape.
  `[MEMFN-RTDISPATCH]`'s terms are mapped onto the same helpers, with each
  site's frequency class (§R4.9.3.1). Q-R9-10 and Q-R9-11 are RULED
  (D155 addendum 1; Q-R9-11: a `freq` column in `DELEG_SITES`, built at
  `[MEMFN-RTDISPATCH]`'s trigger).
  Read §R4.9 first.
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

- `regime_eval.md` — [REGIME-EVAL] the REPLAY EVALUATOR for the knowledge-filtered
  regime table (lane regeval, 2026-10-13, PROPOSED, design only; REV 1 lane regeval2,
  2026-10-14, applies main's review: every judge cell STREAMED or ≥ 1 MiB with the
  repeated 64 KiB column ungated, consumer-bound cells as a counted class with a
  measured criterion, P-MOVE, Q-REVAL-1..11 resolved; a D6 panel follows). It covers:
  - the cell and its knowledge record (P/N/M/E/H/A under S0-S3);
  - measured ns from the grid1 harness at both layers, with the best taken from timed
    arms, never the model;
  - the dispatch gap, handed to [REGIME-TWIN];
  - FIT on grids, published as a D166 set; JUDGE on held-out populations
    ([REGIME-CORPUS] × D27-blinded patterns, the bench's published patterns, Zen 1;
    ALPHA/spike reported only);
  - the pattern→site mapping with a five-class completeness count (K35), and cell and
    slot estimates;
  - loose gate bars G1-G4 plus non-gating predictions, committed and hashed before the
    judge slot (the evaluator refuses otherwise);
  - failing-direction controls C1-C7 through the build's own knobs (set files, row
    denies), with a moved-cell "visibly worse" rule and WITNESS cells for reach;
  - one declared table, read through the kit's pick harness;
  - diffable results and the plan E0-E12; Q-REVAL-1..11.

  `regime_eval/` holds the in-sample replay PROTOTYPE on grid1's slot (own
  CLAUDE.md). It reproduces regime_tables §3's S0 row exactly and finds that the
  S1-off/S3 figures are the cost model's, not the rows', and that R3 lacks a SIMD-off
  arm.
- `setfind.md` — R-17 REVISION 2 (lane r17r5, 2026-10-12, design only, nothing
  run). It designs the small-set FIND as the DEGENERATE CASE of D161's "search
  for the window" (one span, one position, move-back 0, overshoot 0). Its
  sections:
  - §2: the window-contract mapping, with proposed fields W1-W10, each
    marked as carried now or appended by R-18;
  - §3: `mf_set_terms(set, K)` (cubes, modular arcs, the complement form,
    an IDDFS with a labelled budget, EXACT/LOWEST tags);
  - §4: the row contracts;
  - §5: the non-wrapping arithmetic;
  - §6: endianness at the load, with no `#if`;
  - §7: main's question, answered: what pcrec provides for kit-owned local
    storage (`mf_locals`, dominance, lifetime, cursor guarantees, stems);
  - §8: the STATEFUL mask and ring forms, with the proof that they equal the
    stateless form for every candidate sequence;
  - §9: the adaptive switch, and the fallback density gate;
  - §10: the define-time round-trip refusal;
  - §11: the one routing event (a zero-mover seam, then one byte move);
  - §12: the checks and sabotage rows S820-S824 and S826-S843;
  - §13: the follow-up measurement;
  - §14: pcrec-side needs, drafted as responses.md text;
  - §R: all 36 ids of panel r3.

  Report: `../../dev/lanes/r17r_report.md`. Harness text:
  `probes/r17/*_r2.*`.
  **REVISION 2.1 (lane r17r21, 2026-10-12, text only) applies the r4 light
  re-check (`../../dev/reviews/2026-10-12-r4-memfn-setfind.md`, 24 ids); read
  its §R4 first.** Each disposition was checked against the code, and four
  were corrected there: the kit cannot tell functions apart by sink (K1-5);
  the VM hat is defined above `<searchfn>_run`, since the prologue is written
  first (K1-6); no flush change is needed (K2-1); and the new rows are
  header-free instead of using a back-patched include (K2-6). Also: a helper
  takes pcrec's table as a parameter (K1-1); the window fields gain D161's
  origin, a signed move-back, a reserved unbounded value and a stated bit
  (K2-4); `mf_plan` is dropped and `decl_point` replaces `locals_offered`; the
  storage point moves to the forward-loop caller, with stems taken from the
  holding function; and the test readers of the walk text are named. The
  sabotage ids are renumbered to S826-S843. The harness is unchanged.
  **REVISION 2.2 (lane r17r22, 2026-10-12, text only) folds every settled
  direction and the slot2 timing (`probes/r17/reading_slot2.md`); read its
  §R5 first.** It is the revision a build follows, after the bench relay.
  - Forms: ONE stateful row, `pf_terms_mask`, whose body is
    `next_candidate(&state, lo)` (D155 add. 4.1): `mask8_swar` at SWAR,
    `mask64_sse2`/`mask64_avx2` as the later SIMD arms. The ring, the adaptive
    switch, the stateless term-OR and `pf_memchr_set` are not built
    (measured reasons, filed notes); K = 4.
  - Primitives (D155 add. 4): per-width text over a guarded shared helper
    block per file, keyed to abi + helper-set version, emitted only where a
    site uses it (absent at R17-a, first in R17-b's abi event); byte order
    lives in `load_vector` only.
  - §9.2 rewritten (D162 add. 1): ADMIT when density is absent; decline only
    on positive density ≥ ~300k with a state-losing call pattern; the
    state-lost residual is [FINDALL-NEXT]'s.
  - R17-b is gated by a bench relay on real subjects
    (`setfind_bench_request.md`).
  **REVISION 2.3 (lane r17r23, 2026-10-12, text only) applies the r5 light
  re-check (`../../dev/reviews/2026-10-12-r5-memfn-setfind22.md`, K3-1..K3-11);
  read its §R6 first.**
  - The shared block becomes one sub-block PER WIDTH (W8 / V16 / V32), each
    emitted only where a site uses that width (§3.4b): a SIMD-off artifact holds
    W8 only, so the SIMD arms move no SIMD-off byte. The guards carry no
    version and no value; K80's abi guard is the key (the kit cannot see
    pcrec's abi).
  - The body guard reads the bound `<stem>__c.n`; `mf_locals` binds, `mf_use`
    checks neither; a trace trap compares the bound copy with the live
    variable. R17-b const-qualifies `subject`/`subject_length` in the bodies
    holding a stateful site.
  - §9.2's (P) is uses per activation (the per-retry fact is a proxy only; a
    trace counter `mfk-upa` is filed); `T_DENSE` is a measured bracket,
    `B_EVEN` an unmeasured interpolation in (1, 4).
  - N6: pcrec refuses a `-p` prefix that is `pcrec_mfk` or begins
    `pcrec_mfk_`, case-folded (cli.md hunk drafted).
  - Sabotage re-tabulated with S846-S852; two more ids needed for R17-b.
- `setfind_bench_request.md` — the self-contained bench request DRAFT that
  gates R17-b (lane r17r22, 2026-10-12): cells, arms, regimes, a proposed
  numeric regression floor, the subject facts to report, the 64K caveat and
  the questions for the bench. Main relays it (D78); the kit never writes to
  pcrec-bench. Relayed as I-148 (advance notice). **Revision 2 (lane r17r23):**
  the gate rule (reproduce-on-rerun; F from the bench's spread or three
  layout-perturbed A/A pairs; the absolute criterion on every cell; no 0.05
  floor) and "state-losing by construction" dropped, with uses per activation
  asked.
- `setfind_bench_corrigendum_I148.md` — the SHORT corrigendum to I-148 (lane
  r17r23, 2026-10-12) that main relays to pcrec-bench before the run: the gate
  rule and the withdrawn claim, each quoted before and after, applicable
  without reading the design.
- `window_search_game.md` — D161's "search for the window" GAMED OUT before any
  request (lane wingame, 2026-10-11, design study, counts only). It derives the span
  list from real patterns with an independent extractor checked against pcrec's
  k-set walk, and maps which existing facts supply which piece (prefix: kset;
  inner literal: req_run + maxoff; no MINIMUM offsets anywhere). It censuses what
  the contract cannot express: the unbounded move-back is the biggest miss, at 15-22 %
  of unanchored patterns with a span. Five kit policies are written as code, with
  their missing inputs as parameters, and simulated over the bench's throughput
  subjects. The answer to Frank's concern: the kit ranks STOPS from D161's inputs,
  but spans differ in window cost, whose ranking depends on the CONSUMER's shape
  (DFA per window byte against VM per possible start, opposite orders on
  syslogbase), and the independence survivor estimate is off 21x-1,750x. The
  contract needs omin beside omax, a per-route CONSUMER PRICE (three coefficients +
  the no-search cost), and optionally a joint survival rate. The kit does NOT need
  to own the look-forward. Instruments: `window_search_game/` (own CLAUDE.md).
- `r17b_prime.md` — R17-b′'s DESIGN NOTE (lane r17bp, 2026-10-14, design
  only, nothing built; a D6 panel follows). It covers the kit's
  candidate-finder table (D161 add. 11) seeded with regime_tables rows R0,
  R1/R2, R5/R6 and R7, with no iterator.
  - **The table (§1).** One declared row table `fd_rows[]`. Each row has a
    `needs` bitset, a condition over references into the active
    measurement set, and a (stop, form) pick with an `unpaid` fallback.
    Rows needing only compile-time knowledge collapse; rows needing N
    become an emitted per-activation dispatch.
  - **The dispatch (§2).** The form byte is set at the storage point. Every
    use is one statement through a `<stem>__next` selector, the only shape
    the floor rule and D155 allow. The C text is given for WALK+V1,
    WALK+A1 and WALK+V1+A1.
  - **The pay rule (§2.5).** It is a no-measurable-overhead rule.
  - **The measurement table (§3, D166).** 18 families keyed (quantity,
    form, site kind, shape), in walk-byte units, all from grid1 except
    the three ABSENT dispatch charges. So the first embedded set needs a
    new run, and under grid1 R17-b′ reduces to R0 + R7.
  - **The contract (§4).** The missing facts are `body` (M), `site_kind`
    and the `start` hook. E is not built. The set's channel is
    `mf_measures` on `mf_art_begin`.
  - **Bytes, denies, controls and acceptance (§5-§7).** Covers bytes and
    the abi event, `<PREFIX>_MEASURES`, four denies, G1/G2, the
    every-committed-set answer test and 12 sabotage rows. Acceptance and
    predictions are given against ALPHA and grid1. R17-b′ does not fix
    dense find-all.
  - **Also.** The R17-b″ seam (§8), Q-R17P-1..8 (§9) and findings F1-F9
    (§11).
- `r17b_prime/` — that note's compile-only instruments and transcripts
  (cover-shape census of R17-b's movers, multi-form size twins, the
  walk-in-helper assembly check; own CLAUDE.md).
- `window_contract_rev3/` — window_contract.md revision 3's stamp census
  (own CLAUDE.md).
- `window_contract_rev31/` — window_contract.md revision 3.1's evidence: the
  B1 witness, the analysis-axis refusal census and the C-PERT prototype (own
  CLAUDE.md).
- `row_contracts.md` — [MEMFN-ROWCON] light design (rev 1, 2026-10-07,
  Frank after K96): one first-match table mechanism, exported by the kit.
  It has a field vocabulary (`fields.def`), per-row `honours` allowlists
  with a shared gate, a decision record and explain output, and per-row
  reach counters and floors. The kit's tables are its first users;
  pcrec's tables may adopt it after their remodel. Evidence is in
  `probes/rowcon/` (`audit_kit_rows.md`, `audit_pcrec_tables.md`).

- `window_contract.md` — the D161 CONTRACT NOTE, chunk 2 (lane d161note,
  2026-10-12, PROPOSED, design only; a light panel next). It covers what
  pcrec tells the kit about a search site and a compile, as facts only
  (D157).
  - **The SITE** is a bounded sub-problem with one origin. Its spans are
    `mf_pred`s with `move_back`/`overshoot`, from which `omin` is derived.
    A new `spans_seq` fact makes pairwise gaps exact. The reply is a WINDOW
    `[L, U]` or a VERDICT; a FIND miss means NOMATCH.
  - **The ANALYSIS object** (D162) is keyed by [FINDINGS] query names.
    `byte-rate` is always present, with provenance `prior-authored`,
    `prior-none` or `measured`.
  - **The kit's chain** has 1-2 links; the 3+-link extension is specified.
    [KIT-VERIFY] fits as `need = REQUIRED` plus a static `proven` return.
  - **The ONE producer** is `span_facts`. The note maps today's derivations
    onto it, with five controls and a first-match CUT table. Unbounded cuts
    stay pcrec's.
  - **The retirement sequence** S1-S4 retires `rank_*`, `ppm_*` and
    `consumer`.
  - **Rulings on the kit's proposals:** storage, W0-W3, N5 and N6
    ratified; W8 and W9 rejected; W10 moved to the analysis object.
  - **Also:** flexibility worked examples with an event table, the R-18
    outline, three questions for Frank and the panel's attack list.
  - **REVISION 2 (lane `wcrev`, 2026-10-12) applies the light D6 panel r4
    (`../../dev/reviews/2026-10-12-r4-window-contract.md`) and D161 addenda
    7-8; read its §R2 table first.** The reply is a STREAM of exact span-0
    starts (COMPLETE, ASCENDING without repeats), replacing `[L, U]`;
    context checks are not spans and pcrec tries the edge (E1). The
    producer is narrowed to hull spans, a member of the position-pin fact
    family; `start_set`/k-set stay their own facts. Presence gets its own
    table (T-PRES). S1 is a pcrec abi event (the stamp now means OFFERED).
    Every enum has an UNSTATED zero. S3's full file list includes a blinded
    lane for G2; the shadow lives to S4. R2 is REJECTED by D161 add. 8:
    proven facts are KEPT, layer-invariant by contract (C-PROOF), with
    Frank's `foobar` example. Q1 open; Q2 a leaning; Q3 deleted.
  - **REVISION 2.1 (lane `wcrev2`, 2026-10-12) applies D161 add. 9** (see its
    §R2.1): pcrec chooses only the ORIGIN of the handed sub-problem and sends
    ALL spans bounded to it with the analysis object; the kit chooses which
    spans to search and how. T-CUT is now the origin table. Q1 is ANSWERED.
  - **REVISION 3 (lane `wcrev3`, 2026-10-16) is the design main's build step
    E-1 implements; read its §R3 first.**
    - It applies winreq's C-1..C-16 (C-7: §11 plus Appendix A's ledger text;
      C-8: unlock (c) struck) and R17-b′ rev 2 §4. That brings the PRESENCE
      span class, the `byte_form` fact (D161 add. 10), ONE stream reply with
      ALL_PRESENT → VERDICT deleted, and T-WITHHOLD in place of T-PRES.
    - §3.7 is E-1. The analysis object is built per attempt from ONE kinds
      table with an `arrives` column, so no kind is special-cased. It is handed
      ONCE on `mf_art_begin`, the slot the kit's B1 declares, not per site.
    - The SIBLING check against [KNOW-SRC] finds a conflict. Revision 2 made
      `_FINDINGS` mean OFFERED, while `_MEASURES` means CONSULTED. Revision 3
      chooses CONSULTED for both: the offer is not an ask, so E-1 is
      ZERO-MOVER and no abi event. The kit's per-kind `consulted` joins the
      stamp at B3b.
    - Census (`window_contract_rev3/`): 0 default corpus artifacts stamp `""`
      today, so the OFFERED alternative's movers are deny-arm only. The
      alternative is stated exactly in §3.7.5.
    - Q3 (the stamp's meaning) and Q4 (F-2, the `rate:builtin-prior`
      mislabel) are new.
  - **REVISION 3.1 (lane `wcfix`, 2026-10-16) answers the light panel r4
    (`../../dev/reviews/2026-10-16-r4-window-contract-rev3.md`, 1 blocker, 5
    majors, 6 minors, all ACCEPTED) and Frank's Q3 ruling (CONSULTED, D167
    add. 2); read its §R3.1 first.**
    - B1: the offer derives through a NON-RAISING status derivation, the
      refusal stays on the ASK path, and an underivable kind refuses iff it is
      consulted (rule 9), so no refusal moves at E-1 or B3b. The panel's
      witness is reproduced and the refusal population is counted across the
      analysis axis; G1-E1 gains it with floors.
    - The render point for `_FINDINGS` and `_MEASURES` moves after
      `mf_art_end` in its own zero-mover commit RP (§3.7.3a); the object is
      built eagerly after the chain resolves; `find_queries[]` is the query
      vocabulary's one home.
    - Provenance is read from each block's own `provenance` stanza, with
      `bytes`/`fidelity` carried (pending Q5, discussion form).
    - X1: C-PERT, a perturbation check of the stamp against the bytes, with a
      prototype on main: 0 null-control failures and exactly 2 FAILs, which
      are F-5 (the stamp reports only the final attempt; Q6).
