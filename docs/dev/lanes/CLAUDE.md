# docs/dev/lanes/ — per-lane restart records and delivery reports

One `<lane>_log.md` (the lane's own running log: what it did, in order,
for its restart) and one `<lane>_report.md` (the delivery: commits, the
brief's acceptance table filled with MEASURED values, findings) per lane
that chose to keep them. Optional — briefs allow it, never require it.
A `<lane>_brief.md` is the MANAGER's artifact, kept only when a lane is
PARKED mid-flight across a session boundary: the original launch brief
preserved verbatim (stale sections marked) so a fresh agent can be
relaunched onto the lane's branch without the dead session's context.
Delete it when the lane's row completes and merges.
They are the lane's voice, not the manager's: the plan, journal and
decisions log carry the manager's record, and on any disagreement the
committed docs in docs/dev/ win. Historical once the lane is merged;
never edited afterwards.

- `w11_log.md`, `w11_report.md` — [DD-13b.W1.1] (2026-08-30, lane w11):
  the .rxt HEAD grammar, `--list-source`, the three-parser identity proof
  C1, the wiring of verify_rxt.py (C3), sabotage rows S194-S204.
- `w11f_report.md` — the r46 fix lane (2026-08-30, lane w11f): the panel's
  triage on the [DD-13b.W1.1] merge (`docs/dev/reviews/
  2026-08-30-r46-w11-impl.md`) fixed finding by finding — the BLOCKER
  (leg B's escape emitting a table index instead of a byte's value), 8
  must-fix + 2 chk must-fix + sem24/32, most of the shoulds each with a
  new `.rxtin` fixture, and the manager's sem10 ruling (a blank line ends
  a `config` body exactly as it ends a block scalar). New sabotage row
  `S205`.
- `opt41_report.md` — [OPT-4.1] (2026-08-30, lane opt41): the nullability
  gate on [OPT-4]'s count-collapsed prefilter rescue. Carries the PHASE-1
  prediction table for the bench's eleven labelled forms (stated before any
  measurement), the answer to O-10 ask (iv) with its code line, two findings
  about the brief's own premises (the K39 witnesses are NOT nullable; the
  `_LANG_WHY` value alone cannot carry the measured case), and three open
  questions. No `_log.md`: the lane's ordering is in its commits.
- `w12_log.md`, `w12_report.md` — [DD-13b.W1.2] (2026-08-31, lane w12):
  targets, `rx_info.name`/`nentries`, the abi ritual and H11. **Delivered
  BUILT-NOT-VALIDATED**: the box hold was in force for the lane's whole
  working period, so every acceptance number in the report is marked OWED
  and abi site 4 (the FILEPIN) is deliberately unset — it must name the
  step's last src commit. Its report is worth reading for four defects the
  lane found by SELF-REVIEW in place of a build (a `--source`/query
  conflict tested below the query dispatch, where each query returns
  first and would have won silently; a backtick inside a double-quoted
  message; a `--lib-path` leak invariant; a config DIAMOND double-counting
  joined `pcrec` flag text) and for the finding that the `head_basic`
  fixture had been FALSE since W1.1 — its `lib` named no file and its
  `target` named no block, both inert while nothing resolved them.
- `lim1_report.md` — [LIM-1] (2026-08-30/31, lane lim1): the limits table (src/core/limits.def, 44 rows), `--list-limits`, the size-cap rescue's distinct RX_ENGINE_SEL value, S208/S209. Final wave committed by the MANAGER (takeover: the lane went unresponsive after its verification runs; content verified per the report's measured table, re-verified at landing).
- `opt5d_log.md`, `opt5d_report.md` — [OPT-5] STEP 2 design note (2026-09-01
  lane opt5d wrote rev 1; 2026-09-02 lane opt5d2 wrote REVISION 2 against the
  r49 panel, `docs/dev/reviews/2026-09-01-r49-opt5-step2.md`). The report's §5
  carries seven findings against the review and the note's premises — two of
  them real implementation-lane catches (the `rx_info` mirror appends after
  `nentries`, not `match_form`; its guard is `pcrec_artifact_has_dfa_scan`,
  not `match_form`'s engine test) — and one RETRACTED at landing (finding 4,
  the `dfa_table_name` line: the review's `:2664` was right). The one r49
  item not fully discharged is 8 (no synthetic witness reaches P3; S219 ships
  UNREACHED with the derivation).
- `edge1_report.md` — [OPT-EDGE] STEP 1 + K43 (b) (2026-09-03, lane edge1):
  the shared-sentinel edge dispatch (heads renumbered to the machine's TOP
  rows, one unsigned compare for dead-or-head, the edge blocks moved verbatim
  off the generic path) and the designated-range slot initializer. Carries the
  PREDICTION TABLE stated before any build and SCORED against the measurement,
  including three misses. Worth reading for six findings: two `-Werror`
  defects in the lane's own emitted code that no answer check can see (an
  unused label where the edge path is reached by fall-through; `(unsigned)s >=
  0u` on a machine all of whose states are heads); a NEW precondition (8) the
  mechanism forces on `src/opt/scanedge.c` (the offset-set prefilter's reseed
  is the one mid-body writer of the state variable the stop test cannot see);
  that the win is O(1) in the edge count and therefore NIL at one edge; that
  `PCREC_MAX_SCAN_EDGES` has silently changed from a hot-path budget to an
  emitted-bytes one; and that the brief's "8-edge ladder" cannot be built,
  since four is the per-machine ceiling. Its draft structural check is
  DELIVERED RED on two of four witnesses, with the three repairs that were
  tried and measured recorded so nobody re-tries them blind.
- `w13_report.md` — [DD-13b.W1.3] (2026-09-03, lane w13): the composer,
  the name grammar, the altwide dogfood and the composition identity proof,
  written entirely under the evening box hold. **Delivered BUILT, NOT
  SUITE-VALIDATED**, and its §3 is the list of what that costs. Worth
  reading for four things: §1's account of why D89 made `w1_impl.md` §2
  unbuildable as written (a THIRD tier that spends no group number, so the
  re-basing offset had to become a map); §2's eleven measurements, of which
  M3 is the sharpest — the erased tier is worth one slot against the PCRE2
  textual control, whose `groups[]` additionally exposes the wrapper name to
  the caller, which is what D89(2) forbids — and M4 is identity (A) sampled
  at 81 artifacts / 0 differing against a compiler built from `main`; §6's
  five questions, each with the provisional choice implemented and the
  alternative named, including one the lane declined to build blind (the
  `run.sh` composed-block path); and §7, the exporter rules to relay to
  pcrec-bench, with the finding that their `floor` prefix collision is
  CROSS-SET and therefore never fires on a per-set export.
- `vmfl0_log.md` — [OPT-VMFL]/[ENG-DIRECT] STEP 0 (2026-09-02, lane vmfl0):
  the census script, the hand-twin transform, and the R1 mid-flight
  ruling's arrival, in order. See `docs/dev/optvmfl_step0.md` for the
  findings themselves.
- `opt5i_log.md`, `opt5i_report.md` — [OPT-5] STEP 2 IMPLEMENTATION (2026-09-02,
  lane opt5i): the START-PINNED SEARCH ELISION — axis J, the P0-P5 predicate
  with its compiler assertion, the `RX_DFA_START` stamp and the
  `rx_info.search_form` mirror, abi 15 → 16, `tests/codegen/run_search_pinned.sh`
  and sabotage rows S218-S222. The log carries the PREDICTION TABLE written
  before any census was run and the measured comparison against it (175 pinned,
  exactly M1's number; −311,811 bytes net). The report's §7 carries seven
  findings against the note and the tree — the sharpest being that C3 holds only
  for `startpos <= n` (the emitted range guard sits above the scan, so the note's
  "on every call" is falsified by one cell per subject), that the
  `RX_DFA_TABLE` fold's reverse-drop has an EMPTY corpus population so the
  census cannot demonstrate it, and that the hybrid `window_end` clamp the note
  quotes as universal is conditional on an MRL clamp existing. The (B) identity
  pin is deliberately UNSET and owed to the manager at merge: D76's pin must
  name a commit reachable after the merge, which a lane branch's is not.
- `landing_report.md` — the union battery's [OPT-5] STEP 2 LANDING-BAR fixes
  (2026-09-02/03, lane landing): re-pins `tests/rxtsource/
  run_rxtsource_tests.sh`'s corpus census (opt5i's two new corpus files,
  +2/+5/+95, traced to the exact PASS/own-oracle split rather than
  copied from the truncated battery log) and fixes a latent `grep -c`/`||`
  bug in `tests/codegen/run_codegen_tests.sh`'s K24 control that made its
  accessor-count assertion silently vacuous on every green run. No
  `_log.md`: the lane's ordering is in its commits. Also records a
  main-tree scope violation caught and closed before any commit (exact
  timestamps in the report), separate from the manager's own journal entry
  on the same incident.
- `ccdiff1_report.md` — [CC-DIFF] STEP 1 (2026-09-03, lane ccdiff1): the two
  emitter spellings STEP 0 measured, landed as ONE abi event (16 -> 17).
  `always_inline` on a FRAMELESS VM artifact's eight entry-chain statics, gated
  on the same `has_push` bool `RX_VM_FRAMELESS` reads (a FRAMED artifact is
  byte-identical, the stamp aside), and the uniform-table fold in the DFA
  emitter — an all-equal `<m>_next_state` or `<m>_is_accepting` is not emitted
  and its accessor returns the constant, with the table parameter dropped and
  the state/class parameters kept so a call site's `subject[pos++]` still runs.
  Carries the PREDICTION TABLE written before the census, the abi site list BY
  GREP, and the two stamp rulings: `RX_DFA_UNIFORM_FOLDS` SHIPS (the fold makes
  a table ABSENT, and this tree has twice had to remove a check reading a fact
  off a macro's absence), `RX_VM_INLINE_CHAIN` does NOT (it would carry
  `RX_VM_FRAMELESS`'s value by construction). The (B) identity pin is left at
  `da4fe60` and owed to the manager at merge, opt5i's precedent.
- `edge2_report.md` — [OPT-EDGE] STEP 1.1 (2026-09-04, lane edge2): narrowing
  precondition (8), plus the ladder and floor STEP 1 left owed. Read §1.1
  first: (8) turned out to guard TWO hazards where the row named one, and the
  filed narrowing built alone would have shipped a lost-match miscompile on
  its own acceptance population — axis D's `seeded` initializer installs any
  member of the seed family before the loop, while `emit_scan_loop`'s entry
  dispatch only recognised the start state, a fact about the PASS recorded
  nowhere but in a comment in the emitter. The report carries the prediction
  table written before any edit and scored with two MISSES that are its own
  findings: the two `offset-set` artifacts DO regain an edge (on their REVERSE
  machine, which has no prefilter — STEP 1's census read the artifact-level
  prefilter stamp at the wrong resolution), and precondition (8) removed
  ENTIRELY changes nothing measurable, so the reseed hazard has no witness in
  the corpus or in ten constructed shapes. §4.2 is the entry hazard's witness
  (`foo\B` on `"xfoofoox"` answers `[]` against `[(1,4) (4,7)]`). The ladder
  and floor are designed, harnessed and rung-verified but NOT TIMED — the box
  was under hold at load 3.5-4.2 for the lane's whole write phase.
- `ccd2_report.md` — [CC-DIFF] STEP 2 + [OPT-DIAL] STEP 0 (2026-09-04, lane
  ccd2), written entirely under the box hold, so every number is a SINGLE
  COMPILE and no ns/call was taken. The entry chain becomes a four-rung
  ordinal (`plain`/`shared`/`forward`/`inline`) with a `limits.def` size
  term, two stamps, a capability probe and the dial's inventory. Worth
  reading for five things. §3.4 is the FINDING: rung `forward` has rung
  `inline`'s object-code properties EXACTLY — no entry frame, no
  stack-protector canary anywhere, no out-of-line chain symbol — at
  0.50-0.61x its `.text` and gcc time over 20 artifacts with no exception,
  so [CC-DIFF] STEP 1's six body copies were never what the mechanism
  needed (three distinct call shapes, three copies). §2.1 is the
  CORRECTNESS term the brief's framing did not have: "a frameless artifact
  has nothing to bind" is FALSE — the TRAIL is storage a frameless artifact
  can still write (`(abc)(def)` pushes nothing and saves two capture slots),
  so forwarding through a zero-capacity descriptor would turn a match into a
  `FRAMES` give-up. §3.3 is the qualification on rung `shared`: it does NOT
  delete the canary, only moves it to the three `_in` entries, which is
  structurally the shape STEP 0 measured at 0.986 (nothing) — so its run
  time is genuinely open and §6 names it as the number the row turns on.
  §6b is a BUILD DEFECT the change surfaced and fixed: `src/core/limits.def`
  was not a Makefile prerequisite, so editing a limit rebuilt nothing and
  one binary carried two values of one constant — the same defect the rule's
  own comment records for `cls_bits.inc`, one file later. And §9 carries
  [OPT-DIAL] STEP 0's count: four of twenty-one switches have a two-axis
  measured rate, two are pure wins, fifteen are unmeasured — nearly always
  on SIZE.
- `w13_runsh_composed_path.patch` — W1.3.1's starting point: lane w13's written-but-UNRUN run.sh composed-block path (dropped from lane/w13 at the manager's ruling 2026-09-04 04:3x because run.sh is the most load-bearing script in the tree and it would have landed behind three merges and a battery without its own make test). The dropped commit was 464f2896 in the w13 worktree's reflog; the patch is the durable copy. Its contract choice (the target's prefix through flush_block's tail vs the CLI allowance W1.2 refused) is Frank's question; report §18.

- `macport_report.md` — [MACPORT] (2026-09-04, lane macport, the Mac
  move's port of the test/validation infrastructure to darwin/arm64):
  watchdog and safekill's darwin arms (ps-based stats, the perl-setsid
  wrapper, and the load-bearing `exec` finding), the four shared
  tests/lib shims (assoc/loadavg/ncpu/cc_resolve), the `wait -n` FIFO
  throttle at 5 sites, tests/resource's darwin skip, and FOUR real
  latent bugs found only under genuine bash 3.2 (mapfile, a safekill
  ps-fork TOCTOU, descendant self-exclusion, and `IFS=$'\x01'` not
  splitting — the last silently no-op'ing 67 of axes_registry_check's
  96 checks). Its "unexplained bash 5.3" headline was resolved at merge
  (Frank's deliberate install, ruling R3, which the lane never consumed
  — a rulings-file poll gap); its PC-3 escalation became
  upstream_issues.md U13 (10.46→10.48 drift, classified by the
  manager's probe). The Linux arm was verified green (16/16 + 13/13) on
  ubuntubudu by the manager at landing; the shrunk item-8 shebang sweep
  was finished by the manager (six `#!/bin/bash` → `env bash`).
- `utf8design_report.md` — [M5.0] the UTF-8 DESIGN GATE (2026-09-04, lane
  utf8design; design only, nothing under `src/`/`tests/`/`docs/spec/`).
  Delivers `docs/design/utf8_design.md` + `utf8_measurements/`. Worth reading
  for three things. **It refutes its own charter in three places**: the
  `[M5.0]` row's CROSS-NOTE prescribes a `pcrec_maxw` cure that would refuse
  every lookbehind under UTF-8 (10.46 measures lookbehind length in
  CHARACTERS, so the byte-width `minw == maxw` test is the wrong instrument);
  `[DD-12]` assigns the CharSet widening to MOD-0.6 where D33 §7's own
  amendment reassigns it to this milestone; and `[DD-12] (3)` calls
  `PCRE2_MATCH_INVALID_UTF` "essentially the byte-wise semantics" when it is
  measurably not (a byte engine matches `a.c` through an `0xFF`; that mode
  does not). **Its method is new to this house** — the first lane whose
  reference oracle is on another machine, solved by bundling the borrowed
  binding chain verbatim into a stdin payload rather than copying it, so
  `br_oracle.py`'s no-second-binding rule survives the machine boundary and
  nothing is written on the old box. And **its instrument-defect list
  includes one reproduced verbatim** from `subroutines_measurements/`'s own
  recorded entry (`-o /dev/null` making compiling cells read as refusals,
  because pcrec also writes `OUT.h`) — the second time this house has
  recorded that shape, which the report argues means the durable fix is a
  shared fixture rather than another entry. Six ASKs, headed by the
  invalid-UTF semantic and by vendoring UCD data files.
- `<lane>_rulings.md` — the manager's rulings to a lane, written BY FILE while the lane runs (a busy lane reads messages only when it idles; the file is polled at each stage boundary — memory `pcrec-lane-hold-lift-artifact`). GITIGNORED BY DESIGN (see .gitignore): it is live coordination, not a deliverable; the lane's report §"Rulings received" restates every ruling that shaped the delivered work, and the journal carries the manager's side. When a delivered worktree is removed, its rulings file is copied here as a LOCAL, still-ignored file (edge1, w13 on 2026-09-04; lim2's was lost with its worktree — its rulings 1-5 are in lim2_report.md §7 and 6-7 in journal parts 62-64) — these local files do NOT travel by git (memory `pcrec-two-machine-split`).
