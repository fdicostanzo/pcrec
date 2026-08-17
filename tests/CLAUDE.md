# tests — test framework and corpus

Houses the .rxt test format, test runner, and per-feature test cases. Each feature module gets its own subdirectory (e.g., base/ for base-tier regexes). The harness compiles each pattern, builds a driver, and diffs actual output against expectations.

## Files

- **lib/** — infrastructure shared by every suite. `gen_timeout.sh` is D45's
  ONE implementation of the generated-code compile budget (CPU-primary
  since the D45 third addendum: GENCPU 10s plain / 60s san + wall backstop
  GENTIMEOUT 60s/180s, axis derived from the flags):
  every compile of emitted C in the tree runs through its `gen_cc`, and
  exceeding the budget is a loud FAILURE naming the case, never a hang.
  Since 2026-08-16 (D45 second addendum) it also owns the EXECUTION budget
  for generated matchers — `gen_run_secs`/`gen_run` (scripts/watchdog-backed:
  run timeout + RSS ceiling + a section-tagged log line per run in
  `build/watchdog.log`) at per-pattern sites, the bare number at
  high-count inner loops; see lib/CLAUDE.md and docs/testing.md.
  `run_gen_timeout_tests.sh` is its own section in `make test` — a positive
  control that the wrapper FIRES, plus a coverage assertion that every suite
  routes through it, because a test-infrastructure property is invisible to
  every other suite in the tree. `run_group.sh` ([TT-2], 2026-08-15) runs N
  independent suite scripts concurrently as one Makefile section recipe
  (`test-codegen`, `test-vm`), with the lost-worker-hard-fails discipline
  every other parallel path in the tree follows; see its own CLAUDE.md and
  docs/testing.md "Internal parallelism and section composition ([TT-2])"
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
- **known_fail/** — regressions asserting CORRECT behavior for confirmed-but-deferred bugs (docs/dev/known_issues.md); excluded from `make test` so the suite stays honest. EMPTY as of 2026-08-15 (K18 fixed and moved to tests/base/, joined there by the three axes its own repro could not reach), which the ratchet treats as a legitimate good state rather than an error
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
- **codegen/** — structural assertions that behavior-preserving optimizations
  are actually PRESENT in emitted code (R2-PR3: three could be disabled with
  zero test signal), plus a differential check that the M2.8 trie is
  output-preserving against a `-DPCREC_NO_TRIE` reference build (R3.3), the
  [M4.5b] §5.4 byte-identity gate, and [M4.5c]'s DD-8 program-listing check.
  The last two RUN under `make test-vm` rather than `make test-codegen`, on a
  measured smoke-budget argument recorded in its CLAUDE.md
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
- **captures/** — [M4.5a] capture-group expectation corpus: the `g`/`gp`
  `.rxt` line kinds (per-GROUP capture-slot spans, attached to the preceding
  `m`/`ms` case — see docs/testing.md's "Capture-group expectations" section
  for the full format, the live-vs-pending-VM population-accounting rule,
  and the python-oracle tier). `basic.rxt`: 14 `m`/`ms` cases carrying 3
  live `g` + 28 pending-VM `gp` group checks, all oracle-verified against
  python `re`. Runs today against [M4.4]'s DFA-only artifacts (`RX_NCAPS` is
  always 1, so every non-slot-0 expectation is pending-VM by construction
  until [M4.5]'s VM emitter lands); see its own CLAUDE.md
- **possessify/** — [ENG-BREP]'s possessification rung: its oracle-verified
  `.rxt` corpus, the pcrec-vs-pcrec DIFFERENTIAL that is the row's primary
  validation instrument (the same pattern compiled with the rewrite and with
  `-fno-possessify`, linked into one TU, compared on span + every capture slot
  + the failure surface), and the structural checks a `.rxt` file cannot make
  (the stamp matches the emitted machinery, D47.3's do-or-die, the
  byte-identity gate over verdict-free patterns). Part of `make test` as
  `make test-possessify`. Read its CLAUDE.md before adding to any of the
  three: they see different things and none substitutes for another, and it
  records the two ways this directory's own instruments measured nothing at
  first
- **rungselect/** — [ENG-BREP]'s REVERSE-DETERMINISTIC rung, in the same three
  shapes tests/possessify/ uses one rung up: its oracle-verified `.rxt` corpus
  (generated, both oracles, 0 disagreements), the pcrec-vs-pcrec DIFFERENTIAL
  that is the row's primary instrument (the same pattern with the rung and with
  `-fno-revdet`, where denying it falls to literal replication — the semantic
  ground truth — linked into one TU and compared on span + every capture slot +
  the failure surface), and the structural checks a `.rxt` file cannot make
  (rung selection pinned per DECLINE REASON, the bitmask on a three-rung
  artifact, D47.3's do-or-die, corpus-wide byte identity, and the acceptance
  cell's size). Part of `make test` as `make test-rungselect`. Its CLAUDE.md
  records the one thing that surprises: the differential's count ceiling is 64
  and it is a property of the GROUND TRUTH, since the denied build is the one
  that replicates
- **`counterk/`** — the [ENG-BREP] COUNTER rung's differential: the counter
  build against its own `-fno-counter` (replication = ground truth) build, over
  a population whose counts are chosen for their RESIDUE MOD K and whose bodies
  include stride > 1. Carries the two axes R26 E1/E2 proved a differential is
  structurally blind without. See its own CLAUDE.md.
- **`mrl/`** — [M4.6d] MINIMUM-REMAINING-LENGTH pruning (K23's fix, D51
  ruling 1), in the same three shapes tests/possessify/ established. The
  IMPLEMENTATION lane's own tests: the D27 corpus of record for K23 is
  `base/d27_k23_ambiguous_decomposition.rxt` (the `d27k23` cell), and this
  directory deliberately does not duplicate its region. The differential's own
  axis is the ENGINE: the two ceilings differ (`--engine=vm` measures to the
  subject end, the default path threads the prefilter's match-end window), and
  the window form is the only conservative choice in this design whose error
  direction is unsound. Read its CLAUDE.md for the episode that produced its
  §1b acceptance cell — a cell-isolated author's owed-region file located a
  real gap (the counter rung's follow-min is a RUNTIME expression, not a
  compile-time constant) that the differential, the structural checks and the
  step-collapse cell all agreed with, because all three were derived from the
  model the bug was in.
- **`prefilter/`** — [M4.6f] the D46 close-out for the PREFILTER axis:
  `RX_VM_PREFILTER` (the stamp) and `-fprefilter`/`-fno-prefilter` (the
  force pair) for `fit.prefilter` (src/opt/select_engine.c, engine_m4.md
  §6.1/§4.7), giving the DFA-hybrid prefilter the same D46 pair
  `RX_VM_RUNGS`/`RX_VM_STRATS`/`RX_VM_PRUNES` already have. A FORCE pair
  rather than a deny-only D47.3 flag, because the axis is one verdict per
  artifact rather than a per-quantifier ladder step. One structural
  script, deliberately no differential sibling: the prefilter is not a new
  algorithm needing its own pcrec-vs-pcrec sweep, its correctness already
  rides tests/vm's S3.7 differential and tests/mrl's ceiling-form
  coverage — this substep adds only observability and controllability on
  top. See its own CLAUDE.md for the independent-control verification.
- **`altcls/`** — [OPT-ALTCLS]'s ALTERNATION -> CLASS NORMALIZATION, in the
  same three-check shape tests/possessify/ established: an oracle-verified
  `.rxt` corpus, the pcrec-vs-pcrec DIFFERENTIAL that is the row's primary
  instrument (the pass live vs. `-fno-altcls-merge -fno-altcls-factor`,
  SHARING tests/possessify/possdiff_driver.c rather than a second copy of
  the same comparison — and, unlike possessify/revdet/counter-K, NOT forcing
  `--engine=vm`, since this pass runs before engine selection and touches
  both artifacts), and the structural checks a `.rxt` file cannot make
  (exact merge/factor counts on both engines, D46 do-or-die/no-trace, the
  two stages' independent controllability, `RX_NCAPS` invariance under
  factoring). Part of `make test` as `make test-altcls`. See its own
  CLAUDE.md for why the differential's engine choice differs from every
  other deny-family suite's.
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
