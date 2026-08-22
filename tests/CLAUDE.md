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
- **reject/** — the "unsupported constructs fail cleanly, never miscompile" mandate, asserted per construct (274 hand-written rejections + 99 reached by iterating `pcrec --list-syntax`, + 99 accept-controls + 66 gated + zero known-wrong pins since FIX-2 graduated the last five, plus a manifest of the rows an exact count would not protect; these four figures are hand-copied and went stale TWICE during R9 alone (C4-3, then C4V-3 when the counts changed again in the same review), moved again at Q2/SR-9, at A1/§18.2 (→246/62), at FIX-3 (→248/63), at [STD1b] (D37, 2026-08-13: 306/65/0/15→274/99/0/55, the bare-default flip's re-baseline) at [M6.3] (2026-08-18: 55→59 gated, the four named-groups boundary pins — the backref-by-name and (?J) module-boundary proofs plus the 129-byte name-length wall) and at [M6.2] wave A (2026-08-19: 59→66 gated, the enabled-but-unbuilt refusals) — the harness prints them in its own summary block, so read them from a run rather than from here; the two layers catch different things and neither replaces the other — see its CLAUDE.md). Cannot live in .rxt: a `perr` block asserts only THAT a pattern is rejected, never WHY, and the module name is the point. 20 of the rejections are the base-grammar brace errors from FIX-1 and R7 (K5/K6/K8), which have no registry row and name a PCRE2 error instead of a module; another 36 are Q1's verb-doorway outcomes, which pin one name per FORM GROUP rather than one per name — the other 26 verb names are covered by tests/registry/pcre2_check.c alone, which SKIPS without libpcre2 installed
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
- **resource/** — [M4.7b] what compiling a pattern COSTS, which no other suite
  asserts and no `.rxt` block can express: K7's failure modes (SIGKILL, abort,
  multi-gigabyte RSS) are indistinguishable to the harness from the crash it
  scores as a hard failure, so `perr` cannot pin them. Three sections under
  `scripts/watchdog` — bounded outcome for eleven large-bounded-repeat shapes
  under a peak-tree-RSS ceiling and CPU/wall budgets; a positive control for
  the allocation-failure paths under a BINDING `ulimit -v` (an unbinding limit
  is scored a FAILURE, not a shrug); and one check per BOUND, so each shape is
  shown reaching the cap that describes it rather than merely reaching one.
  Sabotage-validated three ways, each catching only its own section. NOT on the
  `ubsan`/`asan` axes by design — ASan reserves terabytes of address space, so
  section 2 would die in the loader and section 1's ceiling would have to be
  loosened until it asserted nothing. Its CPU budget is currently set by K25
  (minimization), not by anything K7's accounting bounds; see its CLAUDE.md
- **known_fail/** — regressions asserting CORRECT behavior for
  confirmed-but-deferred bugs (docs/dev/known_issues.md); excluded from `make
  test` so the suite stays honest, and RUN by the ratchet, which fails if one
  starts passing. **NO LONGER EMPTY as of [M6.4.2]** (it was, from 2026-08-15,
  when K18 was fixed): `u9_atomic.rxt` holds the two U9 patterns with
  LIBPCRE2's answer. That entry is unusual for this directory and says so in
  its own header — U9 is filed as a PCRE2-SIDE oddity, pcrec agrees with python
  and with a hand derivation, and D26 nonetheless makes PCRE2 the source of
  truth. The module landing is the event U9's own entry names as making it
  reachable, so the ratchet is the honest holding place for a ruling nobody has
  made yet: the cells stay, they stay loud, and if pcrec is ever changed to
  reproduce U9 this file FIRES
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
- **fuzz/** — PCRE2-oracle differential fuzzer. The many-seed campaign
  (`make fuzz`) stays manual/checkpoint-only; **[M4.7e]** added a
  fixed-seed slice wired into `make test` as `make test-capturediff`
  (SKIPS loudly without libpcre2, PC-3's pattern)
- **classes/** — module `classes` corpus (MOD-0.3c): the first per-module
  test directory. Blocks carry the `features classes` directive; see its
  CLAUDE.md for the §9.3 watched-failing record and the oracle split
- **modifiers/** — module `modifiers` corpus (MOD-0.5c/d): authored in
  parallel by a worktree subagent from the MOD-0.5a rulings + oracles,
  landed WITH the producers. Blocks carry `features modifiers`; python
  oracle where it agrees, `# pcre2-only` elsewhere (xxmode entirely —
  docs/dev/upstream_issues.md U8 is the measured python divergence); see its
  CLAUDE.md for the §9.3 record and the escape-vs-raw-tab landing correction
- **named_groups/** — module `named-groups` corpus ([M6.3]): the three
  declaring spellings `(?<name>...)` `(?'name'...)` `(?P<name>...)`,
  identical-to-a-plain-group numbering (including the `(?n)` divergence —
  a named group captures even when `(?n)` disables plain-group numbering),
  and the two `.rxt`-expressible name-syntax refusals (duplicate name,
  leading digit). Blocks carry `features named-groups`; python oracle
  live for `(?P<name>...)`, `# pcre2-only` (translated-spelling oracle)
  for the other two spellings and for `(?n)`'s interaction — see its
  CLAUDE.md and docs/dev/upstream_issues.md U10. Always LIVE `g` never
  `gp`: this module unconditionally forces the VM. The name-length
  boundary and the cross-module refusal proofs (backrefs-by-name, `(?J)`)
  live in tests/reject/ instead — no `.rxt` block can assert WHICH other
  module's name is in a diagnostic.
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
- **`assertions/`** — module `assertions` ([M6.2]), ALL FIVE WAVES: `\A`,
  `\Z`, `\z`, `\b`, `\B`, `(?m)`, `\G` and `\K` — every construct the
  module owns. **The one directory in the tree
  whose ORACLE RULE differs from the project default, and the reason is
  measured — FOUR TIMES, in three DIFFERENT ways**: python `re`'s `\Z` IS
  PCRE2's `\z` (python has no single escape for PCRE2's `\Z` at all), python's
  multiline `^` matches after a newline that ENDS the string while PCRE2's
  does not, and python has no `\G` OR `\K` AT ALL (waves D and E, U11c and U11d — total
  exclusions rather than wrong or different answers; `\K` has no rewriting
  either, since python's `re` gives a pattern no way to move its own match's
  reported start). THREE of the module's eight constructs are excluded
  WHOLLY (`\Z`, `\G`, `\K`) and a fourth PARTLY (`(?m)`, its `^` half only);
  `\A`, `\z`, `\b`, `\B` and `(?m)$` are python-verified cell for cell at 0
  divergences, which is what makes the rule a statement about particular
  CONSTRUCTS rather than about the module. The first two disagree
  in the silent direction — no match, a shorter span, or a match PCRE2 does
  not report — so every `\Z` block and every `(?m)`-with-`^` block carries
  `# pcre2-only`, WHOLESALE rather than per diverging cell; every `\G` and
  every `\K` block carries it because there is nothing for python to answer
  at all, and
  `verify_pcre2.py` re-verifies the whole directory against libpcre2 on every
  run, through `tests/fuzz/pcre2_oracle` and `tests/harness/verify_rxt.py`'s
  own parser (one libpcre2 access path, one `.rxt` parser). `\A`, `\z`,
  `\b`/`\B` and `(?m)$` blocks stay python-verified, which is the standing
  proof the splits are about those two constructs and not about the module.
  `run_assertions_tests.sh` (`make test-assertions`) carries what a `.rxt`
  file cannot: that oracle, the CONTROL under tests/reject's
  enabled-but-unbuilt rows (the constructs each wave builds must COMPILE with
  the gate open, or those rows measure an empty module), the D47.5 exemption
  firing read off `<PREFIX>_VM_STRATS` in both directions, and the composed
  state budget refusing rather than miscompiling. `run_mline_diff.sh` is the
  wave C differential — a generated subject sweep over the `(?m)$` family
  against libpcre2 on both engines, with its own population claim checked.
  `run_kreset_diff.sh` is wave E's, and it is the only instrument anywhere
  that asks libpcre2 the MATCH-HERE question: `tests/fuzz/pcre2_oracle` has no
  anchored mode, so the script asks about `\G(?:PAT)` at the same startpos —
  wave D's construct used as wave E's oracle device — which makes the FILTER
  and the CONSUMED-LENGTH halves of assertions_design.md §6.3 rule 3 checkable
  against an external engine rather than against pcrec's own arithmetic. It is
  also the only place all THREE entries of one artifact are driven side by
  side, which `\K` is what makes necessary: `<prefix>_match` delivers no
  captures, so its RETURN is all a D38 callout has, and on a `\K` pattern that
  number and the reported span are different quantities.
  `run_gstart_diff.sh` is wave D's, and it is the SECOND place in the tree
  that drives docs/spec/match_api.md §3.1's find-all loop (see `encseam/`
  below) — here against libpcre2 driven through the SAME loop, which is where
  `\G` gets its "contiguous with the previous match" meaning — plus the only
  comparison anywhere of the two ENTRIES of a single artifact. **Wave D's
  oracle exclusion is a THIRD kind**: python answers a `\Z` cell WRONGLY and a
  `(?m)^` cell DIFFERENTLY, but it has no `\G` at all (`re.error: bad escape
  \G`), so `gpos.rxt` is `# pcre2-only` in its entirety and wave C's
  python-validates-the-plumbing arm had to be re-pointed at the sweep's own
  `\G`-free control patterns.
  See its own CLAUDE.md, and docs/dev/upstream_issues.md U11, U11b and U11c
- **`atomic_groups/`** — module `atomic-groups` ([M6.4.2]): `(?>...)` and the
  possessive suffixes `*+ ++ ?+ {n,m}+`, which are the SAME construct (PCRE2
  defines `X*+` as `(?>X*)` and parse.c desugars to the same tree). Seven
  `.rxt` files, and the ORACLE RULE is the project's default with the
  divergences DETECTED rather than declared: every expectation was produced by
  libpcre2 10.46 through the committed ctypes binding, python `re` was driven
  over the SAME cells in the same pass, and a block carries `# pcre2-only`
  exactly where python disagreed or could not compile — 13 of 729 cells, which
  turn out to be EXACTLY the four families the design's Appendix B.3 predicted
  (`\K`/`\G`, the BRACE possessive over a two-exit body where python cuts per
  ITERATION and PCRE2 at the GROUP EXIT, U9, and scoped `(?i)`).
  `run_atomic_diff.sh` is the behavioural instrument and its ENGINE arm is the
  point: §4's hazard — the capture-erased prefilter necessarily answers for the
  UNCUT language, so its span END is not a bound on a cut match's end, measured
  at 114 cells of silent match loss before RULE H3 — lives in the DIFFERENCE
  between the default hybrid and `--engine=vm`. It also carries the
  `-fno-possessify` arm (the only place sabotage S92 can be red), the DISCHARGE
  differential (the only thing checking "changes no answer" for a rewrite that
  changes which ENGINE a pattern gets), and the three entries side by side with
  `\G(?:PAT)` as the match-here oracle. **U9 is NOT here**: its two patterns sit
  in `known_fail/u9_atomic.rxt` with libpcre2's answer, which pcrec does not
  reproduce — a ruling somebody owes, held loud rather than decided by the
  implementation lane. See its own CLAUDE.md for why the sweep had to be
  batched (44 cells/minute -> 60 seconds) and for the non-vacuity floor that
  stops the whole thing being green on a compiler that ignores the atomicity
- **`encseam/`** — [M5-SEAM] (D58) the ENCODING SEAM's behavioural suite,
  and the first in the tree to run a find-all LOOP (wave D's
  `assertions/run_gstart_diff.sh` is the second, and its driver is
  TRANSCRIBED from this one rather than re-interpreted):
  docs/spec/match_api.md §3.1's protocol, compiled against real artifacts
  and run, advancing through the `<prefix>_next_pos` encoding residual, on
  BOTH engines (every case compiled captures-on and `--no-captures`).
  Oracle is python3 `re`, TWO-ANSWERED — `re.finditer` AND the protocol
  driven by `re.search` — because the two legitimately differ for an
  empty-PREFERRING pattern and a single-answer oracle would either fail the
  honest cases or accept any difference at all. Each case's class (`exact`
  or `lossy` against finditer) is checked in BOTH directions, with `lossy`
  additionally required to be a strict SUBSET. Non-vacuity measured by
  sabotaging the driver's advance (26 fail / 0 pass). Part of `make test`
  as `make test-encseam`, and on both sanitizer axes since it runs
  generated code. Its NEGATIVE counterpart — no engine body may CALL a
  residual entry — lives in tests/codegen/ instead; see its own CLAUDE.md
  for why the two cannot substitute for each other
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
  (not part of `make test`: builds the tree once per sabotage from a
  fresh `git archive HEAD`; the full matrix measures ~50 min at `PROCS=4`,
  2026-08-21, correcting an earlier "~6 minutes" figure that undercounted
  it) — see its CLAUDE.md. [TT-3]'s `CCACHE=1` toggle (docs/testing.md
  "Compile caching") is a qualified win here specifically (25-29% faster
  warm on single-row samples) even though it is a measured NO for
  `make test` — the tree-rebuild-per-sabotage shape is the opposite of
  `make test`'s thousands-of-sub-millisecond-compiles shape.

## Conventions

.rxt format: comments (#), pattern blocks (pattern <regex>), and match/nomatch assertions (m/n with subject and expected span). See docs/testing.md for the full format spec. Run tests via `make test` or `bash tests/harness/run.sh [files...]`. Env vars: PCREC, CC, GENCFLAGS, KEEP=1 (preserve temp dir), VERBOSE=1 (per-test output), LINTGEN=1 (SAN-1: rides the GENCFLAGS compile pass with `gcc -fanalyzer` on every generated matcher — `make test LINTGEN=1`; opt-in, see docs/testing.md "Sanitizer + lint battery"), CCACHE=1 ([TT-3]: routes generated-code and tree-build compiles through ccache — opt-in, MEASURED a clear NO for `make test`'s own workload, see docs/testing.md "Compile caching").

Maintenance: update this file when subdirectories/test modules are added or removed.
