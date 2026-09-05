# docs/dev/ — development-process documents

Documents that track execution against the design, not the product itself.
Append-only where noted; the restart/status-recovery record for the project.

## Files

- `plan.md` — the ACTIVE milestone/step tracker mirroring APPROACH §9;
  STATE:completed rows do not live here. Machine-greppable step states
  (`STATE:not-started|started|completed|blocked|deferred`); format and grep
  recipes documented at the top of the file. Expand a milestone into
  substeps only when work on it begins.
- `plan_completed.md` — archive of completed plan rows, grouped by
  completion date, text preserved verbatim (split from plan.md 2026-08-13).
  A row cited elsewhere as "docs/dev/plan.md [ID]" lives here once it is
  STATE:completed; `grep -c "STATE:completed" docs/dev/plan_completed.md`
  counts them.
- `dev_journal.md` — append-only dated journal, newest at bottom. Append an
  entry after every significant work session; this is the primary
  restart/status-recovery record.
- `decisions.md` — ADR-lite decision log (D1, D2, ...): decision, why,
  revisit-when. Add an entry whenever a choice would surprise a future reader.
- `known_issues.md` — confirmed bugs in pcrec ITSELF that are deferred rather
  than fixed immediately; each has a minimal repro and a scheduled milestone.
  Open as of 2026-08-19: K28 (emitted dead-state-DFA
  artifact fails the harness's own -O1 -Werror GENCFLAGS —
  maybe-uninitialized caps in the `<prefix>_match` wrapper; found by the
  [M6.2] wave B corpus, pre-existing, own-slice fix scheduled before the
  module close),
  K26 (INFRASTRUCTURE: LeakSanitizer
  is a measured no-op on this box, so make asan's leak tier has never run —
  canary obligation + host-config ruling recorded in the entry), K25 (compile TIME in DFA
  minimization — Moore refinement needs O(n) rounds on a chain, so
  `a{0,25000}` spends a measured 15.3 s of its 15.4 s there against
  0.03 s for everything K7's accounting bounds; filed out of K7's fix,
  bounded memory, terminates), K9 (the public
  API takes no pattern length, so a pattern containing NUL compiles as its
  prefix and reports success — rx_info.pattern_len at the M4 freeze is the
  fix's API half) and K23 (exact-minimum ambiguous-decomposition boundary
  exhausts the step budget on a 100-byte ordinary input; found by the D27
  blinded quantifier corpus 2026-08-16; regression in
  tests/known_fail/d27_nested_min_boundary.rxt; owned [M4.6]). K28
  (FIXED 2026-08-19, [M6.2] repair slice — the own-slice fix it was
  scheduled for: an anchored pattern whose DFA is one dead state emitted
  C that failed the harness's own `-O1 -Werror` GENCFLAGS, gcc reporting
  a `caps` array maybe-uninitialized on a read the wrapper's own
  `found != 1` test makes unreachable. Fixed by INITIALIZING it;
  restructuring the test into two `if`s was measured NOT to silence it.
  THE ENTRY NAMED ONE SITE AND THERE WERE THREE — `<prefix>_match`,
  `<prefix>_match_caps` and the standalone `main()`, the latter two
  hidden because `-Werror` stops at the first report. Clean at all five
  opt levels and on both sanitizer axes; the six excluded corpus
  spellings reinstated oracle-verified in the same change). K27
  (CLOSED 2026-08-18, [M5-SEAM] — the emitter-touching wave it was
  scheduled for: `if (pos >= n) return 0;` above the non-EOL memchr
  arm only, the EOL arm's own bound already implying s != NULL;
  UBSan-verified in both directions — guarded artifact clean,
  guard-stripped artifact reproduces the report; regression rides the
  ubsan battery via the [K27] codegen check). K7
  (CLOSED 2026-08-18, [M4.7b] — the entry whose own DIAGNOSIS was the
  thing that was wrong: it placed the memory in the subset construction,
  and it was in the NFA builder. The `X{m,n}` tail loop in src/ir/nfa.c
  rebuilt its out-patch set every iteration, Theta(n^2) arena traffic
  behind a LINEAR state count, which is exactly why no cap could see it
  — `a{0,20000}` 4.68 GB -> 13.2 MB, and both caps K7 called unreachable
  now fire in 0.1 s. A SECOND, unrelated quadratic in the exact-count
  form — n+1 states whose state-SETS average n/2 — is bounded by the new
  PCREC_MAX_SUBSET_ELEMS, which NARROWS exact repeats above `a{9795}`.
  The caller-abort, the worst item on its list because pcrec is a
  library, is closed by routing every malloc-failure site through
  ctx_nomem(). Pinned by tests/resource/). K24
  (CLOSED 2026-08-17, k24fix lane — the only throughput-only entry this
  file has carried: gcc -O2's partial-inlining pass was splitting
  `<prefix>_search` into a trampoline plus a `.part.0` clone in every
  unanchored DFA artifact since the [M4.4] API break, identical
  instructions, a pure code-PLACEMENT cost that held compare.sh case
  (c)'s D12 floor red. Fixed by `__attribute__((noclone))` on
  `<prefix>_search` in the EMITTED text — pcrec cannot dictate its
  users' CFLAGS. Floor never touched; case (c) came back to 391.063
  MB/s at its historical spread, gate 10/10. The VM was never at risk,
  and the reason is structural: a computed-goto body cannot be
  outlined). K22
  (CLOSED 2026-08-16 by the F-1 ruling, decisions.md D47 ADDENDUM: hang
  half fixed by the interim product guard; the compile-these-shapes half
  re-homed as plan row [ENG-CLAMP]'s charter, not a bug). K18 (FIXED 2026-08-15, k18-rewrite lane: the
  empty-iteration exit lost when the ε re-arrival passes THROUGH an
  already-seen state rather than landing ON a loop entry — K17's structurally
  distinct sibling. The closure memo is now keyed on (state, open-loop
  context) and the redirect on "this loop is OPEN on my path", per
  design/k18_memo_design.md's A2; 1,459 live guard cases in tests/base/ on
  four axes, blast radius 8 of 622 corpus patterns, 251/251 changed cells
  toward the oracle. Its precondition status for M4.6's hybrid is
  DISCHARGED). K17 (FIXED 2026-08-14 same day as found —
  R21 panel E-1; the K1 one-shot guard removed from clo_visit, 120
  family tests, 294/294 changed cells toward the oracle), K10 (FIXED 2026-08-12 by MOD-0.6's K10 slice: `RF_CLASS_INVALID` removed
  from the `{U+` row, `[\N{U+41}]` now promises module `unicode-props`;
  guarded by `check_class_syntax_reach` and seven offset pins — see
  docs/dev/known_issues.md), K11 (FIXED 2026-08-11 by MOD-0.1's returned-claims epilogue: doorways
  return a tagged ExtResult, one epilogue renders refusals, call sites end in
  internal-error walls — the stub-build repro now exits 1 cleanly at both
  sites; the cls_set range-check hazard stays assigned to the first
  scalar-returning module),
  K12 (FIXED 2026-08-11 by MOD-0.1's endpoint-rule slice: the five-step §16
  order in p_class, SET-shape certified from the measured class_expect column
  through the returned-claims epilogue; body-dependent rows like `\p` keep
  their module promise until unicode-props' first WIDE producer lands —
  MOD-0.6 landed recogniser-only and deliberately kept this boundary, see
  design_notes_mod06.md §8.2 — a pinned, deliberate boundary), K13 (FIXED 2026-08-11 at [FIX-3]: the twelve
  rows answered the CLASS position with module `backrefs` for constructs it
  can never implement — `[\8]` is the literal `8`, `[\k]` the literal `k`;
  now octal/literal fallback per RF_CLASS_BASE) and K14 (FIXED 2026-08-11 in
  MOD-0.1's first slice: pcrec named a module for constructs its own
  compliance survey calls architecturally OUT-OF-SCOPE — now a ROADMAP_NEVER
  column per-row and per-VerbName, a no-promise diagnostic, and a
  both-directions prose⇔column check), and K2 (FIXED 2026-08-22 by module
  `backrefs` shipping ([M6.5.2]), confirmed with a FIXED marker at
  [SPEC-1.10] 2026-08-30 after the module landing had left the entry
  looking orphaned: `\1` under `--features backrefs` now reads "refers to
  capture group 1, but this pattern has 0" rather than the stale
  "(backreference/octal)" wording; the gate-closed default message is
  unchanged and was never the defect). Failing regressions live in
  tests/known_fail/ (excluded from `make test`).
- `upstream_issues.md` — suspected bugs and divergences in OTHER engines
  (PCRE2, python re) found by our differential tooling; the citable
  rationale behind oracle exclusions. Add an entry whenever tooling
  implicates another engine.
- `chain_profile.md` — [TT-5] stage-1 read-only profile of the per-merge
  validation chain (`make test`/`strict`/`ubsan`/`asan`/`lint`/mech):
  stage wall times across three logged runs (a growth trend, not one
  sample), what each stage re-does that another already did, and a ranked
  candidate list with the measurement each needs before becoming a row.
  Written 2026-08-23; re-read before citing its numbers if the battery
  driver or `tests/mech/sabotages/` have changed since.
- `tt8_mech.md` — [TT-8]'s memo: the mech `PROCS` leak into inner
  `reject`/`harness` sharding (found live via `ps`/`/proc/<pid>/environ`
  sampling, not only read from the dispatch code), the `INNER_PROCS` fix,
  single-row before/after validation, the D69 retro-diff evidence
  (`build/mech_m64.log` vs `mech_m65.log`: zero rows observed flipping
  DETECTED -> UNDETECTED without their own `SAB_FILE`/definition changing),
  and the manager's still-owed commands (the PROCS re-validation sweep, the
  full "after" matrix) — both box-exclusive and not run by this lane.
  Written 2026-08-23.
- `lanes/` — per-lane restart logs and delivery reports (`<lane>_log.md`, `<lane>_report.md`; optional, the lane's own voice, historical after merge). See lanes/CLAUDE.md.
- `reviews/` — compiled checkpoint critic reviews (D6), one file per
  checkpoint: findings, triage dispositions, reflection.
- `summaries/` — executive summaries written for Frank at his request, the
  manager's voice, each citing the ledger/review it summarises. See
  summaries/CLAUDE.md.
- `learnings.md` — the consolidated learnings digest, distilled from a
  complete read of the journal (written 2026-08-17 at Frank's request,
  126 entries in). Eight sections: measurement discipline, oracle
  strategy, check design (summary — the fuller catalogue is in the
  manager's memory), testing strategy, design process, orchestration,
  durable technical facts, and the meta-lesson. Future sessions read
  THIS instead of the whole journal's HISTORY for inherited lessons —
  the journal TAIL remains the mandatory session-start read for current
  work; update this file at session close only when a NEW lesson class
  appears.
- `tt4_measurement.md` — [TT-4.1] MEASUREMENT memo (Frank's order: measure
  before any harness change to `make test`'s batched compilation).
  Stage A: a `gcc`/`cc`/`pcrec` invocation-census shim over one full
  `make test`, section by section — invocation counts, gcc-bound
  core-seconds, section wall+CPU; names `corpus` (255.79s gcc-core) and
  `atomic` (70.65s) as the two worst gcc-bound sections, NOT the
  `rungselect`/`counterk` sections whose wall is largest among the rest
  (dominated by match-execution/harness-loop time, not gcc) — with a
  direct shim-off isolation measurement backing that split. Stage B: a
  batching prototype (never the harness) measuring three compile shapes
  (one-shot baseline / link-batching / whole-TU batching) at several
  batch sizes on real patterns from those two sections — best measured
  speed-up 3.66x (shape B / TU-batching, N=16, against the harness's own
  12-way-parallel baseline), a confirmed emitter-side obstacle
  (`PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES` are unprefixed `#define`s
  that collide when TU-concatenating matchers built with different
  `--features`), and the measured cost of one batch member failing to
  compile. **Stage A2** (manager-requested, same day): Stage A left 76%
  of `make test`'s 3,777 CPU-s unattributed; added `timeout`/`python3`
  shims and re-censused the top remainder sections, finding `corpus` is
  the ONLY section with any per-case matcher-run exec at all (19,185
  spawns) — the other six (`assertions`, `rungselect`, `counterk`,
  `backrefs`, `mrl`, `altcls`) already run their whole subject sweep
  inside ONE process via their own C differential drivers, invisible to
  any exec-boundary shim by construction. **A second manager finding
  (same day) then DECOMPOSED what first looked like one "245.59x
  exec-batching" lever into TWO separate effects**: this box's
  `/usr/bin/timeout` is uutils coreutils (0.8.0), measured costing
  ~108.7ms/call at ~0 CPU vs. GNU coreutils' ~4ms — a WALL-CLOCK-only,
  near-free, one-`PATH`-substitution lever worth ~43% of `corpus`'s own
  section wall alone, explicitly scoped as ITS OWN row rather than folded
  into batching design; the TRUE exec-batching-specific lever (reducing
  process COUNT, not `timeout`'s own overhead), isolated once the binary
  choice is fixed, is a much smaller 5.57x. Three levers, on two
  different axes (CPU vs. wall), stated honestly: gcc-batching nets ~12%
  of the suite's total CPU; the `timeout`-swap and exec-batching levers
  answer a wall-clock question, concentrated entirely in `corpus`, and
  are not additive with the CPU figure. The remaining majority of both
  axes is real differential-driver/oracle compute this row reports as
  unaddressed rather than assumed solved. Evidence lives in
  `studies/tt4_batching/` (census shim, bench harness, committed results);
  see its own CLAUDE.md. No recommendation about the harness's own design
  beyond what the numbers directly support — that is [TT-4.2]'s row (the
  `timeout`-binary swap is a separate row again, per the manager).
- `tt7_combined_axis.md` — [TT-7] evidence memo for `make san`, the ONE
  combined `-fsanitize=address,undefined,leak` axis proposed to replace
  running `ubsan` and `asan` back to back (chain_profile.md candidate (a),
  75m00s measured for the two separate passes at m65). Diagnosis
  distinctness (three scratch sabotages plus three planted into copies of
  `tests/harness/driver.c` against a real generated matcher, each caught by
  its own tool — the leak case reproduces K26's documented LSan-no-op on
  this box, unaffected by combining), D45 budget parity (measured
  byte-identical to either single axis, all four `tests/lib/gen_timeout.sh`
  functions), and the exact command + pass criteria for the manager's
  timing run. See also `docs/testing.md`'s "[TT-7] combined axis"
  subsection. **STATUS: PENDING** the timing run — WHICH RAN 2026-08-23 (45:50 vs 63:43, adopted; see
  docs/testing.md "[TT-7] combined axis — ADOPTED"); the memo's own text
  predates the adoption and stays as the evidence record.
- `wake.md` — untracked (gitignored) hand-off brief for session start/resume;
  lives in this directory but is not committed. Committed docs win on any
  disagreement with it.

- `bare_pcrec_survey.txt` — K37's evidence (2026-08-25, lane srMech): the
  line-numbered list of every bare (unbudgeted) `pcrec` invocation in
  tests/**/*.sh outside tests/recursion/ — 45 files / 347 call sites at
  ae9c98c. Data for the harness lane that lands one `pcrec_run` helper;
  regenerate by grep when it is consumed, then delete this file.

Maintenance: update this file when files are added/removed or their roles
change.
- `opt3_dfa_scan_measurement.md` — [OPT-3] STEP 1 (2026-08-26, lane srOpt3, measurement only, nothing under `src/`): attributes the DFA's per-byte cost between the candidate-start SKIP loop and the TRANSITION loop. The skip loop is NOT the loss — it is entered 190,651 times on `t-b` and skips ZERO bytes, because the byte that returns the machine to state 0 is consumed by the transition loop first, so it can only ever skip the 2nd..nth byte of a non-candidate run (real text's runs are length 1). All the cost is the transition loop at ~3.2 ns / 10.7 cycles per table step, LATENCY-bound on a 7-cycle address+load chain (2 independent streams run 1.97x faster). A 7x faster shufti skip makes all three bench subjects SLOWER. Recommends pre-multiplying the transition table by its stride: measured 1.27x on the bench's own row, answer-identical over 40,469 answer lines / 91 subjects, 1.465x -> 1.151x against PCRE2-JIT.
- `opt5_step0_profile.md` — [OPT-5] STEP 0 (2026-08-31, lane opt5m, measurement only, nothing under `src/`): why the counted DFA loses ~5-6x to pcrec's OWN VM on in-class letter runs yet wins ~2x on digits. Mechanism: the DFA's premultiplied walk is a DATA-dependent loop-carried chain (next_state's load address is the previous iteration's loaded value — pointer-chasing; opt3's 7-cycle shape, now every DFA machine's by [ENG-FORM]), the VM's possessified span-loop is ADDRESS-only (independent loads). Both ratios FLAT across a 64x n range → no count crossover, NOT a limits.def threshold; the digits win is fixed per-call overhead under the bench's find-all regime (one rx_search per byte on a nullable pattern). Candidate fix (unchartered): emit the VM's bounded-scan shape for any DFA region isomorphic to "count one class up to a bound".
- `opt5_step2_premeasure.md` — [OPT-5] STEP 2 pre-panel measurement (2026-09-01, lane opt5m2 24ba0c4, measurement only): the three numbers `docs/design/opt5_step2_twopass.md` §7 owed before the D6 panel — M1 `N_pinned` = 175 over 2,845 corpus patterns (all pure-DFA, ZERO among VM hybrids on the DEFAULT axis; decline reasons 1,642 notacc / 47 view / 8 classctx / 0 at the seed stage), M2 `N_declined_by_view` = 16 at today's tree (all `(?m)...$`), M3 the whole-form `(?:[a-z]{0,2048})\z` decline is `member_ok`'s precondition (3), the position-view check, confirmed by a discriminating probe pair. Also records the same-basename `-o` methodology bug that over-counted M2 by ~100x before it was reported. The lane's `src/gen/emit_dfa.c` `[OPT5M2-PROBE]` stamp is measurement-only and deliberately did NOT land.
- `optvmfl_step0.md` — [OPT-VMFL] STEP 0 (2026-09-02, lane vmfl0, measurement only, nothing under `src/`/`tests/`/`docs/spec/`): the bench's forced-VM ×9 (O-14/I-31/I-32) traced further. (a) the `has_push`/`RX_RESUME_FRAMES` census over 2,603 VM-compiled corpus+bench artifacts finds divergence runs in ONE direction only — 198 `frames>1`-yet-frameless artifacts, ALL of them lookaround constructs whose body has no choice point (`vm_cost`'s uniform lookaround charge over-counting to completion), ZERO of the opposite (`frames==1`-yet-pushing) direction I-32 flagged as theoretically live; also finds the frameless shape reaches 35% of its own population under ordinary `auto` selection, not only `--engine=vm`-forced builds. (b) a direct-branch-dispatcher hand-twin (computed `goto *` → `switch` over the artifact's own resume-label set) on three `frames>=2` bench artifacts is answer-identical on 15/15 subject cells but MIXED on timing — `nest2-64` (24 resume labels, digit-run-scan-dominated body) 3-4% faster on both regimes measured, `csv5`/`ctx-lazy-256` (4-6 labels, dispatch/literal-chain-dominated bodies) flat to 2.9% SLOWER — the D77 trigger for building the dispatcher for real is NOT met by this evidence. (c) drafts (does not land) `RX_VM_FRAMELESS`, a (b)-family `.c`-private unconditional boolean stamp reading `has_push` at its own definition site, no `rx_info` mirror per the `RX_DFA_TABLE`/D77 precedent.
- `opt5m2_m2_changed_patterns.txt` — lane opt5m2 24ba0c4's companion data for the memo's M2: the verbatim 16-pattern list whose artifacts move when `unanch_start`'s `start_acc` is narrowed from `state_acc_any` to the view-strict read. The seed of the NAMED MANIFEST the [OPT-5] STEP 2 note's S218 control is defined against (r49 [check M2]: pin the shape-defined class with a floor, never the count 16).
- `engabs_reach_probe.md` — 2026-08-30 read-only probe answering bench O-9 ask (ii): `unwrapped` stops at `PCREC_ANCHORED_MAX_STATES` = 4096 by design (ladder per skeleton × form; the `\z` wrapper halves the reachable count for `{0,n}`); the refusal-vs-fallback stamp facts for ask (i).
- `opt2_anchored_match_measurement.md` — [OPT-2] STEP 2 (2026-08-28, lane opt2m, measurement only, nothing under `src/`): REFUTES the plan row's hypothesis — comparing `rx_match` on `orig`'s plain DFA vs its `(?:orig)\z` DFA over the bench's 85 compliance subjects shows only 3.7% overhead (3.3% on matching subjects), not the 3.7x/2.15x gap it was meant to explain, because a `match`-regime subject IS the match end-to-end so the plain form also scans to the end. Instead, a cost-isolation patch deleting the `\z` artifact's reverse pass cuts the DFA-vs-VM gap on matching subjects from 2.08x behind to 1.05x (parity), and to 0.57x (43% AHEAD) on the 35 ordinary short valid-email subjects — the reverse pass is ~50% of DFA cost on every matching subject, because `rx_match` never needs the match START the reverse pass computes (`ctx->pos` already is it). Recommends `[ENG-ABS]`'s already-chartered unwrapped-forward-DFA anchored entry (not built here) as the lever, now with a second, independent forcing-function measurement behind it.
- `spec_survey.md` — [SPEC-1] step 1 (2026-08-25, lane srSpec, read-only): the spec-coverage gap table (54 rows), the proposed docs/spec/ file set, the ordered [SPEC-1.n] lanes, and the STALE OR WRONG findings. A survey deliverable like chain_profile.md; superseded row by row as the lanes land.
- `artifact_size_census.md` — [ART-SIZE] STEP 1 (2026-08-28, lane artsize, measurement only, nothing under `src/`/`tests/`): the census Frank's 2 MB-VM-artifact concern chartered. Over 2,772 corpus+bench patterns (2,488 compiled, 0 gcc timeouts/budget kills anywhere in the shipped corpus — median `.o` 6,760 B, p99 14,364 B), every top-20 outlier by `.o` and by gcc time is the SAME mechanism (a bounded/exact repeat over a >1-branch alternation forced onto the counter/frames rungs); a byte attribution (prose/tables/program/scaffold/main, validated to sum to the file size on all 2,488 artifacts) finds program+tables correlates with `.o` at r=0.99 while comments alone correlate at only r=0.43 — a size term should price program+tables, not source bytes. The 2 MB witness (the fuzz gate's seed-1 pattern) sits 3x above the corpus's own largest artifact and is NOT explained by any existing cap being near its boundary — `PCREC_MAX_VM_REPEAT_COPIES` (64) and `PCREC_MAX_VM_REPLICATION_PRODUCT` (131,072 nodes) sit at 47% and 5.7% respectively, both calibrated against runaway/exponential blowup rather than "cap-compliant and still 2 MB," which is exactly STEP 2's gap. Tension curves on the witness + top-5 corpus outliers find THREE separate levers: `--unroll=1` is free on nested-repeat patterns (75-79% smaller, no measured speed cost) and nearly useless on single-level large-count ones; `-fno-premul-table` is the well-behaved already-expected [OPT-3] trade; `--engine=vm` is the measured shape of "size vs performance" itself — shrinks `.o` to 4-9% of default on prefiltered patterns at up to a measured 359,000x throughput cost on the failing path, because the hybrid DFA prefilter IS the size and the speed at once. `docs/dev/artifact_size_census/census.py` (own CLAUDE.md) reproduces §2-§5.
- `artifact_size_log.tsv` — [ART-SIZE.1b]'s METRICS LOG, the ratchet lane's
  own deliverable (Frank's ruling on docs/dev/plan.md's [ART-SIZE.1b] row:
  the log IS the deliverable, per-pattern movement is a `git diff` a
  reviewer reads, never a per-pattern gate). Written by
  `tests/size/run_size_log.sh` at the END of a FULL-CORPUS `test-corpus`
  run (never by a targeted/partial run — see that script's own header):
  one row per corpus artifact test-corpus already compiled — pattern id,
  engine/rungs/prefilter stamps, comment-excluded size, gcc CPU/wall
  seconds, load1 — stamped with a header naming the commit, date, load at
  start, and the row count the SAME run produced (so a truncated file is
  detectable by comparing the two, `tests/size/check_size_tripwire.sh`'s
  own unpinned-max guard). **DELIBERATELY NOT under `docs/measurements/`**
  despite matching that directory's stable-filename/diffable shape (D35):
  `docs/CLAUDE.md`'s own rule for that directory is "no check may read
  these files" and `check_size_tripwire.sh` DOES read this one every
  `make test` — a same-run live artifact a check reads is a different
  thing from an archived report a check trusts as a stale oracle, but
  keeping it out of that directory avoids the ambiguity by construction.
  Read with `scripts/size_diff OLD.tsv NEW.tsv` for a summarised movement
  report rather than a raw two-file diff. See `tests/size/CLAUDE.md` and
  `docs/testing.md` "The artifact-size log".
- `ccdiff_step0.md` — [CC-DIFF] STEP 0 (2026-09-02, lane ccdiff, measurement only, nothing under `src/`/`tests/`/`docs/spec/`): why clang beats gcc by ×2.4-2.6 on some bench cells and loses by ×2 on others, from the SAME emitted C (bench ledger 2026-09-02 §5). ONE transformation carries the general forced-VM signal (§5.2's 0.599 median over 43 throughput cells): **clang inlines the VM entry chain `rx_search`→`rx_search_run`(→`rx_match_anchored` when frameless) and gcc stops at the first call boundary**, so every gcc `<prefix>_search` call builds a 152-byte frame for `rx_run_state`+`rx_run_buffers`, pays a `-fstack-protector-strong` canary (the arrays trigger it; Ubuntu default) and CALLs out of line, for storage a frameless artifact never touches — witnessed by `nm`: `rx_search_run` is a local symbol in the gcc build of loglines `stack-frame` and absent from the clang one. Second, narrower: **uniform-table constant folding** — LLVM folds a variable-index load from an all-equal constant object (`ConstantFoldLoadFromUniformValue`), gcc 15 does not, so on `cls-upto-4` clang proves the whole DFA step dead (all six tables uniform after [OPT-5]'s scan edge absorbed them) and deletes the outer loop, the table bases and the frame: 142 insns → 76. The two CONTROLS where clang loses are gcc doing something right and are unrelated to either: `floor`/thr/vm (1.996) is gcc **rotating the attempt loop and merging two redundant subject-length compares** (4 insns/2 branches vs clang's 6/3), `level-context`/search (1.693) is clang **failing to hoist a loop-invariant bound** out of a duplicated prefilter block (48-insn loop vs gcc's 16). `floor`/match/auto's ledger 0.432 **DOES NOT REPRODUCE** (measured ~0.79 on a byte-identical artifact; clang's absolute number matches the ledger to 1.4%, gcc's is 2× this lane's) and shows no transformation difference — a layout artefact for the bench to re-run, not a pcrec finding.
- `ccdiff_step0_evidence/` — [CC-DIFF] STEP 0's reproduction pieces: the three hand-twin transforms (`twinA.py` uniform-table folding, `twinC.py` single-IV scan edge, `twinV.py` always_inline the VM helpers), their diffs against the emitted artifacts, the per-cell hot-loop disassembly under both toolchains, the corpus reach sweep (`sweep.tsv`, 180 artifacts) and the timing logs. Text only; no objects or shared libraries.
- `optvmfl_step0_evidence/` — [OPT-VMFL] STEP 0's reproduction pieces archived out of the session scratchpad by the manager at merge (2026-09-02): the census script + its JSON result, the hand-twin transform (`handtwin/make_twin.py`), the correctness/timing driver sources and the 5-trial logs the memo `optvmfl_step0.md` §3 cites. Generated artifacts (.c/.h/.o/.bin) are NOT archived — they regenerate from the pinned compiler.
- `tt12_cpu_samples_battery_de32a4b.tsv`, `tt12_battery_stage_markers_de32a4b.log` — [TT-12] STEP 0's raw data: the union battery of 2026-09-02 on de32a4b sampled every 30 s (load1, all-core busy%, stage tag) plus the battery's timestamped stage markers; the analysis lane reads these, never re-runs the battery for them.
- `tt12_step0_profile.md` — [TT-12] STEP 0 (2026-09-03, lane tt12a, analysis only, no runs): per-stage idle core-hours from the samples above — `san` (18.5 idle core-hours, 30 of its 34 scripts are structurally single-threaded regardless of `PROCS`, the 4 PROCS-aware ones' CPU spikes located by ordinal position) and `mech` (14.0 idle core-hours; 44.5% of samples sit in a narrow band just above the `PROCS=4` row-concurrency ceiling since only 2 of ~30 suite arms read `PROCS` themselves — battery.sh's `PROCS=4` contradicts [TT-8]'s own 28:43-vs-36:36 `PROCS=6` finding). `test-axes` (opt5i's `axes2.log`): each axis's ~175 s is one `tests/harness/run.sh` run bottlenecked on ONE 3,065-case `.rxt` file among 190 (file-granularity dispatch, not a `PROCS` cap). `test` at `-j12` is the opposite problem — load1 47.6 on 12 cores (K44). Five ranked recommendations, each naming its confirming measurement (D77); none built here.
- `dfa_online_minimization_study.md` — [LIM-2] STUDY-1 (2026-09-04, lane dfamin, READ-ONLY: nothing under `src/`/`tests/`, no `make`, no compile, no benchmark; REVISED the same day after Frank clarified the charter — §3 rewritten, §4 extended, §5 changed, §1-§2 untouched). Chartered after lim2's census found `tests/base/k18_cost_gates.rxt`'s witness shrinking 97.06% under minimization (27,575 raw states → 1,010), so raw subset-construction size cannot bound the EMITTED (minimized) table's size and no percent-of-raw margin can be made to. Asks whether states can be compacted AS THEY ARE GENERATED. **§1** states what a state is here — a priority-ORDERED list per class-axis view plus `eolvar`/`endvar`, interned on all of it (`src/ir/dfa.c:809`/`:871`) — and finds two things the charter did not name: the final emitted state NUMBERING is `minimize.c:161`'s first-occurrence order over the RAW creation order, so byte identity is *plausibly* preserved by any compaction that merges into the earlier state but must be MEASURED (three named holes), and compaction MOVES THE REFUSAL SET (the caps read `d->n`) while NOT reducing the K7 `subset_elems` charge. **§2** is the web survey: Nicol & Frohme, "Deconstructing Subset Construction — Reducing While Determinizing" (arXiv 2505.10319, TACAS 2026) is the closest published work; the whole incremental-minimization family (Watson/Daciuk 2003; Almeida–Moreira–Reis 2014) minimizes a COMPLETE automaton, so "anytime" does not mean "before the machine exists"; Baburin & Cotterell (DCFS 2025) prove predicting subset blow-up PSPACE-hard. **§3** (revised) answers Frank's two-pass questions from the code. The thorough pass is an OPTIMIZATION, not a correctness requirement — `minimize.c:69`/`:160` already make "merged nothing" an ordinary shipped outcome — with three non-correctness dependencies, of which the scan-edge one is an ORDERING constraint and whose minimality half is left as an open question for a prototype. It gives a five-tier taxonomy of merges by what each must know, whose ranking criterion is that **only Tier 1 (dominated positions) and Tier 4 (a full online registry) make CONSTRUCTION cheaper** — Tiers 2 and 3 merge states already paid for. And it records the reframing: **a size bail needs provable INEQUIVALENCE while compaction proves EQUIVALENCE**, so compaction cannot make the projection exact unless the incremental result IS the artifact — which is the one configuration where Frank's optional-second-pass idea and lim2's margin problem solve each other, and it is a property of the full registry alone. **§4** is the brittleness analysis: candidate B (dominance pruning) is brittle as the tree stands because three of its seven failure modes live in a counted-repeat × assertion cross-product cell no existing sweep generates; the full registry C is the more dangerous mechanism and the better-CHECKABLE one, because it alone can be diffed for isomorphism against the existing pipeline over the whole corpus. **§5** recommends: solve lim2's bail separately and now (it is a different problem); READ THE PAPER FIRST since C is only ranked on its abstract; then M1 (the closed fraction) and M2 (the dominance prize) decide between B and C. Do NOT build A (periodic partial minimization) — it is the one candidate ranked down on merits rather than on missing measurements, since no M1 outcome favours it. **§6 is M5, DONE 2026-09-04 by lane `m5paper` (READ-ONLY, same terms): the paper and its MIT-licensed Java reference implementation (`github.com/jn1z/OTF`) read in full, retiring §2.3's and §3.8's `unverified` marks. It INVERTS the ranking. The OTF loop's output is REDUCED, NOT MINIMAL — paper §3.1 requires a final minimization and the implementation runs an unconditional Hopcroft pass after it — so candidate C's defining property (optional second pass, hence raw = emitted and an EXACT projection) is FALSE, and no intermediate count is a lower bound either. Two structural findings: the paper's Table 1 is a 2×2 of this study's own candidates (its SC-S IS candidate B, its OTF is candidate A plus a generalization layer), and C REQUIRES A rather than subsuming A′ because UNIFY is called only from the intermediate minimization — so "do not build A" and "build C" are inconsistent. C is demoted below B; §5.1's step 4 becomes B-first; M1 must measure the paper's partition rule rather than the closed fraction (§3.5's "precisely the closed subgraph" is too pessimistic and was the sole basis for ranking A down); M6's second-pass half is answered in advance and only its scan-edge minimality-vs-finality question survives. Their evaluation contains NO regular expressions and no counted repeats at all.**
- `nf25_notes_for_authors.md` — the running notebook toward a response-to-the-authors document for [NF25] (Frank, 2026-09-04: "if we successfully use this paper to build an algorithm ... generate a doc in response ... for now, keep notes"); every lane that builds on or measures against [NF25] appends a dated bullet in the same change.
- `form_char_step0.md` — [FORM-CHAR] STEP 0 + [OPT-CLSPACK] STEP 0 (2026-09-04, lane form0, measurement only, nothing under `src/`/`tests/`/`docs/spec/`): is a caseless CLASS test faster than a folded COMPARE, and is a 256-byte table load faster than the 32-byte bit array's load+shift+and, on both engines, cache footprint counted. Four hand-twin families, each a mechanical transform of an emitted base artifact's own class-bitmap or scan-edge tables (byte sets parsed off the compiler's OWN emitted text, never re-derived from the pattern), correctness-checked per twin against its base (52/52 cells agree) and sized (`.text`/`.rodata`, `gcc -O2 -c`) under the evening box hold. (A) VM literal chain `abcdef` caseless, 6 sites: `fold` wins both axes (-38% `.text`, `.rodata` deleted entirely), `table` loses both (+31% `.text`, 8× `.rodata`), `atom` is between — **and a `gcc -O2 -S` compiler-equivalence check CLOSES this family's speed question without a stopwatch**: `c=='a'||c=='A'`, `(c=='a')|(c=='A')` and `(c|0x20)=='a'` all compile to the SAME branchless mask+compare+sete with no load at all, so `table`'s one-load-latency argument has nothing to beat here (`studies/form_char_twins/asm_evidence.c`, `results/three_spellings.s`). (B) a general (`[a-zA-Z0-9_]`, 4 runs) and sparse (`[aeiou]`, 5 singletons) class, 1 site each: `table` loses `.text` at both; `rangecmp` is a near-wash on general (+2.8%) and a clear win on sparse (-5.6%) — genuinely open pending timing, since both real alternatives here DO read from memory. (C) the DFA scan edge — a small witness (`(?i)a{2,40}Z`, 4 sites), a `nonpair` witness (`[ace]{2,40}Z`, 4 sites, NOT a case-fold pair) and `ci-256` (pcrec-bench's own bitmap-edge witness, read-only, 8 sites, every site a case-fold pair): the "bitmap" 256-byte body costs `.text` at every scale (+24% small, +20% nonpair, +0.8% ci-256) and all the `.rodata` `range`/`fold` need none of; on the NON-fold-pair witness `range`/`fold` compile to byte-identical objects (the fallback discipline confirmed), while on the fold-pair witnesses they diverge by a small, real, now compiler-explained margin (`fold`'s one mask+compare vs `range`'s two-compare-plus-or) — the earlier draft called this "noise" and that was an understatement, corrected here. `table` vs `range`/`fold` stays genuinely open pending timing, unlike family A. (D) N=16 distinct classes (`abcdefghijklmnop` caseless VM, above the plan row's ~10-class estimate): the shared atom table is SMALLER than both alternatives on `.text` (-41%/-54%) as well as `.rodata` (2×/16× smaller) — not a space-for-time trade on this axis, a plausible CSE mechanism named but not disassembly-confirmed, genuinely open pending timing + disassembly. Recommends AGAINST the 256-byte table form everywhere measured; `fold` (family A) is now ready to build on its own merits (the speed question is closed); `atom`@N≥16 (family D) is the second candidate, contingent on timing. Owes: the timing run itself (scoped to families B/C/D — no longer A) and a disassembly read of family D. Evidence and reproduction harness at `studies/form_char_twins/` (own CLAUDE.md/README.md).
- `xarch_step0.md` — [XARCH] STEP 0 (2026-09-05, lane xarch0, measurement
  only, nothing under `src/`): macOS/M1/gcc-16 vs Linux/Ryzen/gcc-15.2 on
  identical emitted C. Half 1 (compile rates): a full-corpus SIZELOG run
  joined against the already-committed Linux log at its own commit
  (`81731547`) -- 0 `size_bytes` movers across 2,925 common rows (byte
  identity holds perfectly), gcc CPU-seconds ratio Mac/Linux median 0.518
  (Mac ~1.93x faster, flat across DFA/VM engine stamps), reaffirming
  [TT-14] (spawn tax, not compute) with an independent number; also notes
  a 37-row gap (all Linux-only, all from four assertions `.rxt` files at
  that WIP-commit's own 751 pre-existing test failures -- not investigated
  further, out of scope). Half 2 (matcher throughput at the bench's pin
  `334fd10e`): THE HOOK -- `floor` forced-VM at `--vm-entry-shape=1/2/3`
  on ARM shows `forward` TYING `plain` (ratio 0.996-1.004), NOT
  reproducing the x86 ledger's 2.0x `forward`-shape regression, confirming
  o17facts's I-50 section 2 hypothesis that the x86 regression is a
  gcc-15.2 inline-merge idiom loss rather than a `forward`-shape property;
  NEW finding neither side predicted -- `shared` is the ARM outlier
  instead, ~3x slower than both other shapes. Also: altwide
  `w-8`/`w-64`/`w-256` vm+auto ratios (0.49-1.10x, nothing near 5x),
  bounded `cls-upto-4/32/1024`+`dig-upto-16` dispatch-overhead cells (Mac
  ~2.1-4.5x faster, with the `cls-upto` cells' two runs disagreeing up to
  35% with each other -- flagged as likely Apple Silicon P-core/E-core
  scheduling noise at nanosecond scale, uncorrected), and loglines
  `iso-ts` marked INCONCLUSIVE (a synthesized, non-bench subject produced
  the opposite sign from the bench's pinned ratio -- a subject-mismatch
  artifact, not a finding). Every number SCRATCH TIER.
- `xarch_step0_evidence/` -- [XARCH] STEP 0's reproduction pieces: the two
  size-log TSVs (Mac and Linux copies) and their join script/output
  (`half1/`), the `--vm-entry-shape` hook driver and its three run logs
  (`half2_hook/`), the generic throughput-sweep driver plus interleaved
  round-robin orchestrator plus read-only bench-subject reproduction
  script (`half2_altwide/`), the whole-subject match-dispatch driver
  (`half2_bounded/`), and the synthesized loglines subject
  (`half2_loglines/`). Text/driver-source only; no generated
  `.c`/`.h`/`.o` artifacts (they regenerate from the pinned compiler and
  pattern text cited in the memo).
