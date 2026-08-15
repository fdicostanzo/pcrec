# tests — test framework and corpus

Houses the .rxt test format, test runner, and per-feature test cases. Each feature module gets its own subdirectory (e.g., base/ for base-tier regexes). The harness compiles each pattern, builds a driver, and diffs actual output against expectations.

## Files

- **harness/** — test runner (run.sh), driver template (driver.c), python-re oracle (verify_rxt.py)
- **base/** — base-tier test corpus (.rxt files); every expectation cross-verified against python3 re (blocks marked `# pcre2-only` excepted — see docs/testing.md)
- **cli/** — CLI-surface and library-API tests (run_cli_tests.sh), part of `make test`
- **reject/** — the "unsupported constructs fail cleanly, never miscompile" mandate, asserted per construct (274 hand-written rejections + 99 reached by iterating `pcrec --list-syntax`, + 99 accept-controls + 55 gated + zero known-wrong pins since FIX-2 graduated the last five, plus a manifest of the rows an exact count would not protect; these four figures are hand-copied and went stale TWICE during R9 alone (C4-3, then C4V-3 when the counts changed again in the same review), moved again at Q2/SR-9, at A1/§18.2 (→246/62), at FIX-3 (→248/63) and at [STD1b] (D37, 2026-08-13: 306/65/0/15→274/99/0/55, the bare-default flip's re-baseline) — the harness prints them in its own summary block, so read them from a run rather than from here; the two layers catch different things and neither replaces the other — see its CLAUDE.md). Cannot live in .rxt: a `perr` block asserts only THAT a pattern is rejected, never WHY, and the module name is the point. 20 of the rejections are the base-grammar brace errors from FIX-1 and R7 (K5/K6/K8), which have no registry row and name a PCRE2 error instead of a module; another 36 are Q1's verb-doorway outcomes, which pin one name per FORM GROUP rather than one per name — the other 26 verb names are covered by tests/registry/pcre2_check.c alone, which SKIPS without libpcre2 installed
- **parse/** — checks on facts the PARSER computes but never emits, which no
  generated-C test can reach. PARSE-1's top-level branch count is the first:
  the design deliberately leaves the AST unchanged, so the count is compared
  against an INDEPENDENTLY WRITTEN reference counter (a flat byte scan, not a
  transcription of `p_alt`), which libpcre2 in turn arbitrates through its
  error-127 / error-154 thresholds — for two constructs pcrec does not
  implement, which is the point, exactly as PC-3 checked the registry before
  its modules existed. 16,384 bodies, 32,768 arbitrations, zero disagreements
  at PARSE-1 close; three sabotages of `p_alt` itself verified caught. Read its
  CLAUDE.md before trusting the AST-identity check alongside it — that one
  passed on the tree BEFORE PARSE-1 existed and is a forward-pointing
  regression net, not evidence the feature is there
- **registry/** — the SR-1 syntax construct table checked TWICE: against the parser in both directions (including a 255-byte sweep of each of the four doorways, which catches a construct added to parse.c with no registry row, D24), and — since PC-3 — against **libpcre2**, which is the first check in this repo that is not pcrec reading pcrec. Since Q2/SR-9 the `(?` doorway has three generated differentials of its own — a byte sweep, an option-run sweep and per-prefix tail sweeps — so it is no longer the case that only `(*` is name-checked. Plus compliance_section.py, which holds docs/pcre2_compliance.md to the dump (SR-4)
- **bench/** — throughput + compile-time budget regression suite (`make bench`), guards R1 A-2/A-3
- **known_fail/** — regressions asserting CORRECT behavior for confirmed-but-deferred bugs (docs/dev/known_issues.md); excluded from `make test` so the suite stays honest. Holds K18 (the empty-iteration exit lost through a seen ε state), which is a DFA-CONSTRUCTION bug: the VM's own §3.3 guard is a separate mechanism, so tests/vm exercising the K18 family and passing is EXPECTED and touches nothing on this ratchet
- **vm/** — the [M4.5b] backtracking VM engine's own tests: the two bounds
  (step budget, frame capacity) each driven to ITS OWN limit and required to
  produce its own code, the honest artifact stamps (frame_capacity,
  subject_ceiling) read and then triggered, the engine-selection surface, and
  vm_oracle.py's capture sweep — every group span against python `re`, every
  span derived a SECOND time by a prefilter-free `--engine=vm` build
  (engine_m4.md §3.7's differential, run as a gate rather than a
  nice-to-have). Separate from harness/ because the .rxt capture-expectation
  format is [M4.5a]'s concurrent work, and permanently separate for what it
  checks: bounds, stamps and cross-engine agreement are not expressible as
  .rxt expectations. Part of `make test`; `make test-vm` is the section
  target, `bash tests/vm/run_vm_tests.sh full` the checkpoint-scale sweep
- **codegen/** — structural assertions that behavior-preserving optimizations are actually PRESENT in emitted code (R2-PR3: three could be disabled with zero test signal), plus a differential check that the M2.8 trie is output-preserving against a `-DPCREC_NO_TRIE` reference build (R3.3)
- **thread/** — concurrency under ThreadSanitizer (`make test`): [TS-2] N
  threads share one compiled matcher over different subjects across five
  differently-shaped emitted engines, [TS-3] concurrent `pcrec_compile()` on
  different patterns in different threads (library built WITH TSan), both
  checked against single-threaded baselines for byte-identity as well as for
  TSan silence. SKIPS loudly (exit 0) if `$CC` lacks `-fsanitize=thread`.
  Both halves are sabotage-validated with planted races — see its CLAUDE.md
  for the measured TSan race reports
- **fuzz/** — PCRE2-oracle differential fuzzer (`make fuzz`), run manually and at checkpoints
- **classes/** — module `classes` corpus (MOD-0.3c): the first per-module
  test directory. Blocks carry the `features classes` directive; see its
  CLAUDE.md for the §9.3 watched-failing record and the oracle split
- **modifiers/** — module `modifiers` corpus (MOD-0.5c/d): authored in
  parallel by a worktree subagent from the MOD-0.5a rulings + oracles,
  landed WITH the producers. Blocks carry `features modifiers`; python
  oracle where it agrees, `# pcre2-only` elsewhere (xxmode entirely —
  docs/dev/upstream_issues.md U8 is the measured python divergence); see its
  CLAUDE.md for the §9.3 record and the escape-vs-raw-tab landing correction
- **probes/** — design-measurement probe sources against libpcre2 (via fuzz/pcre2_abi.h), NOT part of `make test`; the reproducible evidence behind the extension design's Part II/R14/§18 numbers, and the working-code hand-off package for the SPEC-MOD0 (D27) author — see its CLAUDE.md
- **spec_mod0/** — the ten module-0 invariant checks, written under D27 by an
  author denied `src/`, `docs/`, and the rest of `tests/` (`tests/probes/`
  and a black-box `build/pcrec` were the only inputs). NOT part of `make
  test` (own entry point: `bash tests/spec_mod0/run_spec_mod0.sh`) but has
  a [TT-1] section target, `make test-spec`, since it's a real oracle-backed
  gate someone should be able to spot-run — see its CLAUDE.md for the
  PASS/FAIL/AWAITING-SURFACE exit vocabulary and the current pass count
- **mech/** — GENERATES the sabotage-detection matrix ([MECH-1]) rather than
  hand-maintaining "disabling X fails N cases" figures, which have gone
  stale every time this project tried to keep them by hand. `make mech`
  (not part of `make test`: ~6 minutes, builds the tree once per sabotage
  from a fresh `git archive HEAD`) — see its CLAUDE.md

## Conventions

.rxt format: comments (#), pattern blocks (pattern <regex>), and match/nomatch assertions (m/n with subject and expected span). See docs/testing.md for the full format spec. Run tests via `make test` or `bash tests/harness/run.sh [files...]`. Env vars: PCREC, CC, GENCFLAGS, KEEP=1 (preserve temp dir), VERBOSE=1 (per-test output), LINTGEN=1 (SAN-1: rides the GENCFLAGS compile pass with `gcc -fanalyzer` on every generated matcher — `make test LINTGEN=1`; opt-in, see docs/testing.md "Sanitizer + lint battery").

Maintenance: update this file when subdirectories/test modules are added or removed.
