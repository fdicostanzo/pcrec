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
  Open as of 2026-08-19: K2 (cosmetic), K28 (emitted dead-state-DFA
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
  both-directions prose⇔column check). Failing regressions live in
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
- `reviews/` — compiled checkpoint critic reviews (D6), one file per
  checkpoint: findings, triage dispositions, reflection.
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
