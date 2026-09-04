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
  docs/testing.md "Internal parallelism and section composition ([TT-2])".
  `timeout_bin.sh` ([TT-6], 2026-08-23) resolves `TIMEOUT_BIN` once per
  process — this box's default `timeout` is uutils coreutils (~108ms/call
  pure wall, ~0 CPU) against GNU coreutils' ~4ms; every bare `timeout` call
  in the tree now runs through it. MEASURED 6.31x wall on an isolated
  `make test-corpus` run; see docs/testing.md "The `timeout` binary
  itself".
- **harness/** — test runner (run.sh), driver template (driver.c),
  python-re oracle (verify_rxt.py). Since [DD-13b.W1.1] run.sh knows
  about the `.rxt` HEAD without parsing it — for a head-bearing file it
  makes ONE `pcrec --list-source` call and starts its per-line loop at the
  `line` column of the first `pattern` row — and verify_rxt.py is WIRED
  INTO `make test` for the first time (via tests/rxtsource/, over a
  `find`-derived list with a short-list hard fail)
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
- **island/** — [ENG-ISL] STEP 1, the VM's ALTERNATION ISLAND (`make
  test-island`; `docs/spec/tuning.md` §2.20). Two `.rxt` files that ride
  `test-corpus` and are BLIND to the island by construction — the axis is
  answer-identity-preserving, so an alternation the island takes and the same
  one under `-fno-alt-island` must answer identically, and a corpus that could
  tell them apart would be testing the wrong thing — plus
  `run_island_tests.sh`, the structural half the `.rxt` files cannot see (the
  stamp's IFF against the artifact, the seven declines asserted against the
  artifact rather than the reason, the declined population's byte-identity
  under the flag, that the island allocates no slot, and both directions of the
  measured narrow-width knee). 24 checks, 0.5 s. Its own CLAUDE.md says why the
  "one island, not one per factored run" assertion is the load-bearing one — it
  is the check that would have caught the defect this row shipped and measured
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
  reproduce U9 this file FIRES.

  **[DD-14] wave B+C ADDED `dd14_bc_open.rxt` AND [DD-14.LB] CLOSED IT** — all
  three of its cells left, by three different doors, and the directory is empty
  of `.rxt` again (the ratchet's own "legitimate good state"). `^(a?(?1)b)$`
  was a CORPUS BUG rather than an owed ruling and is live in `leftrec.rxt` as a
  ruled nomatch. Of the two calls inside a LOOKBEHIND, cell 1 now COMPILES —
  the parked note's own charter, a DEFERRED WIDTH RE-CHECK, is built
  (`pcrec_postresolve`, src/opt/postresolve.c) — and cell 2 is still refused,
  because **its parked note named the wrong cause**: its lookbehind body is ONE
  top-level branch of width 1..2 (the alternation lives inside the CALLEE), so
  it is `(?<=(a|bc))x` reached through a call, a §2.5 capability limit
  `lookaround/refused.rxt` has pinned all along. Both are live cells in
  `recursion/inlookaround.rxt` now. The generalisable lesson is in that file's
  own CLAUDE.md: **a parked cell's stated CAUSE is a claim, and discharging it
  is not the same as closing the cell**
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
- **thread/** — two disjoint questions about threads, in two scripts.
  **[TS-4]/[DD-14.FB]'s `run_stackdepth_tests.sh`** (`make test-stackdepth`,
  in `make test`, NO sanitizer) asks whether ONE call FITS: the emitted
  matcher on a musl-default 128 KB thread stack. It prints a `KNOWN:` line on
  a green run — the call-bearing default entry does not fit, K33, and D73
  keeps the stamped capacity that causes it — and FAILS if that ever stops
  being true. TSan is deliberately absent, because it changes the stack a call
  needs and a stack-fit question asked under it is a question about TSan. The
  rest of the directory asks whether concurrent calls RACE, under TSan:
  [TS-2] N
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
  `m`/`ms` case — see docs/spec/rxt_format.md's ".rxt format" section for
  the full syntax, the live-vs-pending-VM population-accounting rule, and
  the python-oracle tier; docs/testing.md's "Capture-group expectations"
  keeps the design rationale and the seed-corpus/sabotage-validation
  record). `basic.rxt`: 14 `m`/`ms` cases carrying 3
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

  **[M6.6.2] IT ALSO HOSTS `maxw_check.c`**, which is a different KIND of
  instrument from the three above and says so in its own CLAUDE.md: it reads a
  number the compiler never emits. `src/opt/mrl.c` gained `pcrec_maxw`
  (`pcrec_minw`'s twin with the OPPOSITE sound direction — over-estimating is
  free, under-estimating is the silent miscompile), whose only consumer is the
  lookaround module's fixed-width rule. **THAT CONSUMER NOW EXISTS** ([M6.6]
  shipped it; verified at the [DD-14] close, 2026-08-25:
  `src/parse/mod_lookaround.c:298/309` calls `pcrec_maxw` beside `pcrec_minw`
  to decide FIXED, and `src/opt/callgraph.c:722` carries its call-aware
  fixpoint), so the sentence this paragraph used to end with — "no corpus, no
  differential and no structural check can be red because of it" — EXPIRED
  when the rule landed: a wrong `maxw` is now a lookbehind that is accepted or
  refused wrongly, which the lookaround corpus and its identity gate do see.
  What remains true is why the check was written: `maxw_check.c` reads the
  number DIRECTLY, so it can be red for a reason no answer-comparison reaches. Half of what
  it asserts comes from OUTSIDE pcrec: every oracle-verified span in the whole
  `.rxt` corpus must fit inside its pattern's `maxw`.
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
- **`backrefs/`** — module `backrefs` ([M6.5.2]): every backreference
  spelling, PCRE2's octal disambiguation at the atom position, and
  `(?J)`/DUPNAMES. Nine `.rxt` files, and they are **GENERATED** —
  `gen_corpus.py` drove every cell through libpcre2 10.46 before it was
  written and python3 `re` over the same cells in the same pass, so the
  `# pcre2-only` markings are COMPUTED rather than declared. That matters more
  here than anywhere else in the tree: this module has the largest oracle
  divergence pcrec has met (of 25 measured spellings, 20 are accepted by
  libpcre2 and only 5 also work in python), and R32 C3 found the first test
  plan marking two files python-verifiable IN THE DIRECTION THAT LOSES THE
  ORACLE. Census at landing: 226 cells, 50 blocks python-verified, 62
  `# pcre2-only`, 31 `perr`; the four divergence families are filed as U12.

  **`selfref.rxt` is the file to read first.** The RE-ENTRY class —
  `(a|b\1)+` and relatives, a live reference INSIDE the group it names — is
  where publishing a capture at the group's OPEN differs from publishing at
  its CLOSE, and the first design's version of this file took only the cells
  that AGREED. Cells that agree under both disciplines cannot detect the
  difference between them.

  `run_backref_diff.sh` is the behavioural instrument (nine sections, four
  EXACT population guards, three of them asking questions nothing else in the
  tree asks), `run_dupnames_diff.sh` sweeps §8.3's resolution rule with an
  INDEPENDENTLY WRITTEN model of the rule checked against libpcre2 alongside
  pcrec, and `fold_agreement_check.c` ties the two spellings of pcrec's ASCII
  fold over all 65,536 ordered byte pairs. The module's byte-identity gate is
  `codegen/run_backref_identity.sh`, opt-in as `make test-backrefs-identity`.
- **`lookaround/`** — module `lookaround` ([M6.6.2]): `(?=X)` `(?!X)` `(?*X)`
  and, from wave D, the three lookbehind spellings. **Six `.rxt` files at wave
  B+C and they are GENERATED** — `gen_corpus.py` drove every cell through
  libpcre2 10.46 before it was written and python3 `re` over the same cells in
  the same pass, so the `# pcre2-only` markings are COMPUTED rather than
  declared. This module is the case that makes computing them worth the
  generator: design §7 catalogues TWO expectations a hand-marking would have
  written in and that measurement REFUTES — python compiles all fourteen
  QUANTIFIED lookaround forms (G8) and agrees on all 27 CAPTURE cells
  including captures in a negative lookahead (G9) — so a hand marking would
  have thrown a working oracle away in both, which is R32 C3's finding twice
  over. What python genuinely cannot do is `(?*`: it has no such construct at
  all (G5), so `nonatomic_ahead.rxt` is `# pcre2-only` IN ITS ENTIRETY and
  `verify_rxt.py` skips every cell in it.

  **`run_lookaround_diff.sh`** (`make test-lookaround`) is what closes that
  hole and two others. §1 re-drives every pcre2-only pattern through libpcre2
  at every startpos on span AND every group span — without it one of the two
  families this module ships would have exactly one oracle behind it, the one
  that generated its expectations. **§2 is the only arm in this tree whose
  population is required to DISAGREE WITH ITSELF**: `(?=` and `(?*` differ in
  exactly one emitted line, so a compiler that cut both or cut neither answers
  them identically and an agreement-only arm would go green on both
  sabotages; the exact disagreement count is asserted. §3 sweeps design
  §3.2.1's follow-scoping in BOTH polarities, because on the negative form an
  unscoped body is a FALSE MATCH rather than a missed one. It REUSES
  `backrefs/bref_oracle.py` and `bref_batch.c` rather than making a third copy
  of one mechanism. The byte-identity gate is `codegen/run_lookaround_
  identity.sh`, opt-in as `make test-lookaround-identity`.

  **`run_expansion_diff.sh` (wave E2) rides the same section and is a
  DIFFERENT KIND of instrument, not more of the same one** (design §10.1a).
  `run_lookaround_diff.sh` runs the module's OWN corpus — every spelling, every
  body shape, the refusals — which is BREADTH. This one re-expresses
  `tests/assertions/`'s 8,260 libpcre2-verified cells as lookarounds
  (`expand_corpus.py` substitutes each assertion by its §6.1 definition) and
  drives 887 generated patterns through a THREE-WAY check per cell: pcrec on
  the expanded pattern, pcrec on the FOLDED one, and libpcre2 on the expanded
  one. `A == B` is D66's self-oracle and needs no external oracle at all;
  `A == C` is what stops it passing because both lowerings are wrong the same
  way; **neither is sufficient and both are asserted**. That is DEPTH, on
  exactly one body shape. **It is a corpus GENERATOR and not a product
  mechanism** — nothing under `src/` changed for it, and the product-side
  substitution is [DD-14]'s. Its expansion table is LITERAL and is re-verified
  against libpcre2 (with a vacuity guard that must DISAGREE) before a row of it
  is used, because a table derived from the compiler would make `A == B` a
  tautology; a `--policy=none` control arm and a cell-fidelity guard against
  the corpus's own expectations are the other two anti-tautology rows. Measured
  at the wave: 29,063 three-way comparisons, 0 disagreements.
- **`recursion/`** — module `recursion` ([DD-14] wave B+C): subroutine calls
  `(?N)` `(?±N)` `(?&name)` `(?P>name)` `(?R)` `(?0)`, and — from wave D —
  `\g<N>`/`\g<name>`/`\g<±N>` `\g'N'`/`\g'name'` `\g<0>` `\g'0'`.
  **Twenty-one `.rxt` files** — wave E added `prefilter.rxt`, wave F added
  `define.rxt` and `realworld.rxt` — **GENERATED**:
  `gen_corpus.py` drives every cell (including
  every `g` line) through libpcre2 10.46 via
  `docs/design/subroutines_measurements/probes/sr_oracle.py` before writing
  it, and **there is no python arm at all** — design §10.1 MEASURED that
  python3 `re` has no subroutine-call construct whatsoever, which is an
  ABSENCE and not a divergence. `\1` and `(?P=n)` DO compile in python and are
  `backrefs`' REFERENCE construct, a trap the design names by name and
  `spellings.rxt` opens with §2.1's one-cell discriminator against.

  **THE `\g` FAMILY WAS EXPECTED-UNSUPPORTED AND MARKED RATHER THAN RED —
  AND WAVE D LANDED IT (2026-08-24; re-measured at the [DD-14] close,
  2026-08-25).** Design §8.1 kept the two `\g` registry rows `unbuilt` until
  wave D, since D65 flips `built` from the PORT and never runs the emitter, so
  the 22 blocks carrying `\g<` or `\g'` rendered as `perr` under
  `gen_corpus.py`'s `wave='D'` marker with **the oracle's answer carried in a
  `# WAVE D ORACLE:` comment** — `APPROACH.md` §7's policy as `docs/testing.md`
  states it — and wave D's edit was to delete one keyword argument and re-run.
  MEASURED NOW: `build/pcrec --list-syntax` reads `built` for all six `\g`
  subroutine rows (`\g<1>`, `\g'1'`, `\g<0>`, `\g<01>`, `\g'0'`, `\g'01'`,
  module `recursion`, port `pcrec_brport_g`), so the marker is history and the
  blocks are live match cells. The MECHANISM above is not history and is the
  part to reuse: it is how the next module's corpus is written before its
  producer exists.

  `(?(DEFINE)...)` never appears: it stays module `conditionals`' doorway
  until D71 item 4's registry row lands (wave F), and every callee-only body
  uses the oracle-verified `{0}`-callee idiom instead. The wave A `gu <code>
  "<subject>"` directive carries the give-up cells — **ONE of them, after wave
  E**: `[DD-14.EMPTY]` made an EMPTY-language pattern answer NOMATCH at the
  search entry (the root's `minw` at the analysis ceiling), so `leftrec.rxt`'s
  two left-recursion cells became ruled `n`s and `quantified.rxt`'s `^(?R)*$`
  — a genuine runaway, with a base case and a non-empty language — is the only
  `gu` left.

  **`run_recursion_diff.sh`** (`make test-recursion`) is the behavioural
  instrument, and each of its four sections exists because a `.rxt` cell
  structurally cannot make its claim. §1 is the `--no-captures` AXIS — **no
  `.rxt` directive for that flag exists anywhere in this tree**, and design
  §4.3's whole claim lives there (a call names a group exactly as a reference
  does, so `pcrec_bref_mark` must mark the target or the flag deletes the
  callee out from under the call); it asserts the slots survive in the emitted
  C AND the answer is right AND `RX_NCAPS` is 1, because the answer alone can
  be right by accident. §2 BISECTS for the artifact's own depth ceiling rather
  than pinning one — MEASURED at n = 342 for `^(a(?1)?b)$` over aⁿbⁿ, a
  684-byte subject, giving up with a TYPED code at 343 — which is the number
  §14 ASK 2 is about and the failure direction an under-charged `2·|W|` of
  trail produces. §3 sweeps 16 measured-claim patterns × 24 subjects × EVERY
  startpos on span AND every group span (1,632 cells, 0 disagreements): the
  GROUP axis is where §5.3's restore set is observable at all, and STARTPOS is
  where `reset_for_next_attempt`'s `call_top` line is. §4 is the
  `--engine=dfa` refusal with its control. It REUSES `backrefs`'
  `bref_oracle.py` and `bref_batch.c` rather than making a third copy.

  **[DD-14 wave G] `run_recursion_diff.sh` GAINS A §5** — design §9.2's SECOND
  CONTROL, the one this module has and `lookaround` did not: every `pattern`
  line under `tests/recursion/`, deduplicated, built on BOTH LINKAGES (default
  and `-fno-splice-calls`) and swept over §3's own subject grid, span AND every
  group pair (156 of 170 patterns, 15,912 cells, 0 disagreements). §1's
  slot-survival half moved onto `-fno-splice-calls` (it greps the VM's slot
  LAYOUT, and the spliced build has no VM) with the default build beside it as a
  one-cell `A == B`; §4 became three cells (recursion still refuses
  `--engine=dfa` by name, a SPLICEABLE call COMPILES, and the flag puts it
  back). **`run_specimen_identity.sh` is new and ON DEMAND**: plan row
  `[DD-14.G]`'s bar — the RFC 5322 email specimen in four spellings, whose
  factored artifacts must BE the hand-inlined one past three NAMED exclusions,
  with the 85 subjects, the libpcre2 self-check and the three 1 MB throughput
  subjects. The corpus also runs on both linkages through `run.sh`'s new
  `RXTFLAGS` env var (593/0 on each).

  **NO CELL IS PARKED ANY MORE.** Wave B+C parked three in
  `known_fail/dd14_bc_open.rxt`; [DD-14.LB] closed the file. `^(a?(?1)b)$` was
  a corpus bug (a `gu frames` expectation that could not have come from
  libpcre2 at all — a give-up is pcrec's own artifact behaviour) and is live in
  `leftrec.rxt` as a RULED nomatch. The two calls inside a LOOKBEHIND are both
  live in `inlookaround.rxt`: one as a MATCH, once the deferred width re-check
  moved the width question past `pcrec_callgraph_build`, and one as a ruled
  `perr`, because its refusal was never the timing over-rejection it was parked
  as. See `known_fail/CLAUDE.md` for the worked example and the
  `gu frames`-vs-`recurse` note (D71.1).
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
- **offsetskip/** — [OPT-K]'s OFFSET-k candidate-start skip, as ANSWERS. One
  `.rxt` file, no runner: the mechanism's structural facts live in
  `tests/codegen/run_offset_skip.sh` and the two files NAME THE SAME PATTERNS
  on purpose, because the skip is answer-identity-preserving by construction
  and this corpus would pass just as well on a compiler that had stopped
  emitting it (sabotage S187 is exactly that, and leaves this directory 80/80
  green). What it owns is the emitted skip's ARITHMETIC — the `cand = hit - k*`
  mapping at the subject start, the `cand + maxk >= n` guard at the end,
  overlapping candidates, restarts, and the RESEED, whose absence is a FALSE
  MATCH after a word character. Read its CLAUDE.md for the row that had to be
  added after a plant measured four others unable to detect the resume's
  off-by-one — a row that EXERCISES a line is not a row that DETECTS a change
  to it.
- **anchored/** — [ENG-ABS]'s ANCHORED MATCH-HERE form, as ANSWERS: the same
  pattern compiled with the unwrapped anchored machine and with
  `-fno-anchored-dfa`, linked into ONE TU under two prefixes and compared on
  every anchored entry, every capture slot and every position 0..n+1.
  **The directory exists because MEASUREMENT showed nothing else in this tree
  asks what `<prefix>_match` ANSWERS**: `tests/harness/driver.c` drives
  `<prefix>_search` and touches the anchored entries only as an
  `_in`-vs-un-suffixed cross-check (both sides one code path), and
  `make test-axes` compares the corpus's SEARCH answers under each deny flag.
  Sabotage S189 is that made real — `prune=false` on the third machine makes
  `a|ab` at pos 0 over "ab" return 2 where it must return 1, and on the planted
  tree `tests/base/alternation.rxt` (which CONTAINS that pattern and that cell)
  is 26/0 and `tests/codegen/run_anchored_match.sh` is 14/0. Read its CLAUDE.md
  for why the ground truth is the DENIED build and why the subject grid is
  written rather than harvested from the corpus's own `m` lines.
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
  stale every time this project tried to keep them by hand. Since
  [MECH-REACH] (2026-08-25) a row may also declare the REACH of its own
  witness (`SAB_REACH`/`SAB_REACH_POP`/`SAB_REQUIRE`) and score `UNREACHED`
  when the construct its detector rests on has been IMPLEMENTED, or its
  corpus population has gone to zero — the S70/S155 failure, where a row went
  on scoring for two milestones while certifying nothing. `make mech`
  (not part of `make test`: builds the tree once per sabotage from a
  fresh `git archive HEAD`; the full matrix measures ~50 min at `PROCS=4`,
  2026-08-21, correcting an earlier "~6 minutes" figure that undercounted
  it) — see its CLAUDE.md. [TT-3]'s `CCACHE=1` toggle (docs/testing.md
  "Compile caching") is a qualified win here specifically (25-29% faster
  warm on single-row samples) even though it is a measured NO for
  `make test` — the tree-rebuild-per-sabotage shape is the opposite of
  `make test`'s thousands-of-sub-millisecond-compiles shape.
- **rxtsource/** — [DD-13b.W1.1] INV-COMPAT: that growing the `.rxt`
  format changed no existing corpus file's meaning. The `.rxt` format now
  has THREE parsers (`pcrec --list-source`, `harness/run.sh`'s arm chain,
  `harness/verify_rxt.py`'s `parse_rxt`) and this section makes them agree
  byte for byte over all 179 files — plus the arm-chain hash pin, the
  keyword census, and C0a's two independent assertions that the head
  machinery was never invoked. **It is also where `verify_rxt.py` finally
  RUNS**: until this step its `main()` was invoked by nothing in the tree
  and its directory discovery was a one-level glob, so the obvious wiring
  (`verify_rxt.py tests`) verified ZERO files and exited 0. It now runs
  over a `find`-derived list with a short-list HARD FAIL.
  **`fixtures/*.rxtin` are named for their extension**: the corpus has 0
  head-bearing files, so the seam and every head refusal had an EMPTY
  population, and the fixtures are the witnesses — kept out of
  `find tests -name '*.rxt'` so they cannot join the corpus or move its
  pinned census. Read its CLAUDE.md for the two denominators, the two
  DEFERRED sabotage rows and why each waits, and the block-scalar
  contradiction and how it was resolved.
- **definitions/** — [DD-13b.W1.3] the COMPOSITION IDENTITY PROOF
  (`make test-definitions`): pcrec's own corpus composing over a shared
  definitions file, and the check that a composed artifact answers exactly
  what a HAND-WRITTEN flat one does. THREE SOURCES, no two of which share
  one — python `re` on the flat pattern, the flat pattern compiled by pcrec,
  the composed source compiled by pcrec — with the two pcrec legs agreeing
  AGAINST the oracle reported as a defect below the composer rather than as
  a pass. Its fixtures are `.rxtin` for `tests/rxtsource/fixtures/`'s reason
  and one of its own: a composed block cannot be compiled from its own text,
  so a `.rxt` here would be a corpus file the corpus runner cannot build.
  See its CLAUDE.md for the open item that leaves (`run.sh` has no
  composed-block path yet, and `verify_rxt.py` already carries the matching
  skip predicate with a population of zero).
- **size/** — [ART-SIZE.1b]'s zero-cost artifact-size metrics log +
  corpus-level tripwire, riding `test-corpus`'s own compile pass (no
  `.rxt` corpus of its own — `run_size_log.sh` wraps `tests/harness/
  run.sh` with `SIZELOG` set; `check_size_tripwire.sh` reads the assembled
  `docs/dev/artifact_size_log.tsv`, `make test-size`). See its own
  CLAUDE.md for the log format and the measured per-compile overhead.

## Conventions

.rxt format: comments (#), pattern blocks (pattern <regex>), and match/nomatch assertions (m/n with subject and expected span). See docs/testing.md for the full format spec. Run tests via `make test` or `bash tests/harness/run.sh [files...]`. Env vars: PCREC, CC, GENCFLAGS, KEEP=1 (preserve temp dir), VERBOSE=1 (per-test output), LINTGEN=1 (SAN-1: rides the GENCFLAGS compile pass with `gcc -fanalyzer` on every generated matcher — `make test LINTGEN=1`; opt-in, see docs/testing.md "Sanitizer + lint battery"), CLANGGEN=1 ([CC-CLANG]: the same shape one compiler over — defaults CC to clang for the generated-matcher compile pass, unless CC is already set explicitly; opt-in, `make test CLANGGEN=1`, writes nothing to build/, see docs/testing.md "Sanitizer + lint battery"), CCACHE=1 ([TT-3]: routes generated-code and tree-build compiles through ccache — opt-in, MEASURED a clear NO for `make test`'s own workload, see docs/testing.md "Compile caching").

Maintenance: update this file when subdirectories/test modules are added or removed.
