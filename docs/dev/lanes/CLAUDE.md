# docs/dev/lanes/ — per-lane restart records and delivery reports

**`BOILERPLATE.md` (2026-09-06, Frank's ruling) is the standing rules every
lane reads FIRST** — scope mandate, worktree ritual, box facts, process
rules, and the lifecycle policy (NO self-keepalive crons: subagent caches
are 5-minute TTL, measured by the tokenscan analysis 2026-09-06; finish,
hand back complete, END — never idle). Briefs name only the task, tier and
deliverable, and point here. Update it when a rule changes rather than
growing briefs back.

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
- `utf8s1_report.md` — [M5.0] STAGE 1, the INTERVAL-PAYLOAD REFACTOR
  (2026-09-04/05, lane utf8s1). `A_CLASS` becomes a code-point interval list,
  `pcrec_lower_enc` lands at its derived position, `pcrec_cls_bits` becomes the
  sole path to a bitmap, `PcrecEnc` gains `max_cp`, and the identity gate reads
  100% on all four axes. Read it for the TWO ESCALATIONS in its §0, both of
  which are rulings the lane deliberately did not take.

  **§4 is the sharp one: `utf8_design.md` §2.1.2's constraint 2 is INVERTED,
  and inverted it collides with constraint 3, leaving no valid slot for the
  lowering.** The constraint's own sentence contradicts itself ("callgraph must
  run AFTER the lowering — so the lowering cannot run before :961") and the
  diagram follows the wrong half. MEASURED with a scratch REBUILDING lowering,
  which is the only kind that can test it since stage 1's byte instance
  rebuilds nothing: at the design's position it moves 45 of `tests/recursion`'s
  179 artifacts (the call site's `W` save/restore block comes out EMPTY —
  `u.call.save` derived through a stale `.body`), above the call graph it moves
  none.

  **RULED R2 while the lane ran, and CONSUMED: resolution (a).** The cure is
  the pass's SHAPE, not its slot — `pcrec_lower_enc` splices IN PLACE and never
  reallocates a node that is or contains a group root, so `:1000` stands and
  constraint 2 becomes a node-identity PROPERTY. The walk takes `Ast **slot`,
  which makes the invariant structural rather than remembered: its only
  possible write is one pointer in a parent it never rebuilt. The DESIGN-TEXT
  hunks are flagged in the report for the manager to apply at merge (D80), not
  edited by the lane.

  **§4's last two subsections carry a NEW stage-2 finding that came out of
  consuming the ruling**: `u.rep.revbody` is a reversed COPY built at
  `compile.c:988`, before the pass, and the walk does not follow it — **413
  classes across the corpus**, measured against an independently written
  census that also confirmed the walk's forward coverage EXACT (6,697 =
  7,110 − 413, zero mismatches on 2,565 compiles). Inert in stage 1; loud
  rather than silent if stage 2 ignores it.

  **§5 is the one a future reader is most likely to need: the D70 clobber has
  gone LATENT and sabotage row S121 now detects NOTHING.** `u.cls` shrank
  32→16 bytes, so `u.rep.possessive` (+49) lands on byte 1 of `n` and
  `u.rep.revbody` (+56..+63) falls outside the payload entirely — and `n <= 128`
  under `byte`, so the unguarded clear zeroes a byte that is provably already
  zero. MEASURED: with the kind guard REMOVED, 2,845/2,845 corpus patterns are
  byte-identical and `revdet_highbytes.rxt` — the file written specifically to
  detect this — reports 7/7 identical. The guard is still correct and goes live
  again at stage 3 (`\p{L}` is ~770 intervals, where a cleared byte turns
  n=256 into the EMPTY class, a LOST match), but its witness is gone.
  **RULED R2 and re-aimed in the same wave**: the row declares `SAB_REACH`
  (can the compiler build such a class at all — `\p{L}` must compile) and
  `SAB_REACH_POP` (does its own detector file carry one), both verified in
  BOTH directions, so it scores UNREACHED honestly today and the runner's
  `NOW REACHED` check fires the day stage 3 lands.

  Also worth reading: §2's account of a latent NULL deref this milestone made
  real (three probe `Ctx`es in `syntax_dump.c` reached the parser with no
  options, harmless only while nothing on a parse path read `opt`), §7's
  pricing of the render helper at 0.024% of compile time from three separate
  measurements, and §8's re-aim of four sabotage anchors — the three caseless
  rows reproducing their recorded counts (6/14/8) exactly, which is what makes
  a re-aim verifiable rather than merely resolvable.

- `k49fix_report.md` — [K49] (2026-09-05, lane k49fix): the unanchored RETRY
  ADVANCE moved off a hard-coded `pos++` onto the encoding seam, so under
  `-e utf8` a retry lands on the next CHARACTER BOUNDARY. Read it for three
  things. **§3 is a FINDING against a ruling, not against code**:
  `utf8_design.md` §5.5 asserts a mid-character start "cannot produce a wrong
  answer", Frank's **ASK 5** ruling ("leave `ENG_ATTEMPT`'s start loop alone")
  is recorded against exactly that claim, and it is FALSE — §2.6.1 of the same
  document already carried the counterexample ("'No path' INVERTS for a
  negative assertion") and the two sections were never reconciled. The lane
  filed the refutation and the re-openable marker and did NOT treat the ruling
  as overturned. **The DFA half is a separate defect, K50**, oracle-backed
  (libpcre2 answers `(3,3)` for `\B` over `61 CE B1` under both UTF option
  words; pcrec answers the `options=0` BYTE answer `(2,2)`) and reachable from
  an ordinary `startpos=0`, so the known-fail population went 2 → 2 rather than
  the 2 → 1 the brief predicted. **And §2.3 is the shape worth reusing**: the
  fix spells the boundary rule TWICE per backend (once as `next_pos`, once as
  inline `advance` text, because DD-12 (7) forbids an engine calling the
  entry), and pays for that with an agreement check that extracts the advance
  from an emitted artifact and compares it against that same artifact's
  `next_pos` — `fold_agreement_check.c`'s shape, one seam over. §5.2 flags a
  SECOND pre-existing red the lane measured and did not file: `make test-mrl`
  is red at the lane's base on `cwmax` answering 1 byte for `[^a]` under
  `-e utf8`.

- `xarch0_report.md` — [XARCH] STEP 0 (2026-09-05, lane xarch0,
  measurement only): the delivery summary for `docs/dev/xarch_step0.md`
  (Mac/M1/gcc-16 vs the bench's Linux/Ryzen/gcc-15.2 pin, compile-rate join
  plus matcher-throughput ratios). No `_log.md` — the lane's ordering is
  in its commits.

- `utf8s3_report.md` — [M5.0] STAGE 3, module `unicode-props`' PRODUCER
  (2026-09-06, lane utf8s3). `\p{L}` compiles: 45 names, both encodings, both
  polarities, in a class, under `-i`; the UCD vendored at
  `third_party/ucd-16.0.0/` behind a generic `make gen-tables`. Read it for
  five things.

  **§2's headline is the D27 corpus, not the acceptance table.**
  `tests/utf8/axis04_p_categories.rxt` was written by a BLINDED author
  against the pre-stage-2 tree with each block's oracle answer carried as a
  comment above a `perr` line. Promoted mechanically: **462 of 506 cases
  green on the first run, ZERO semantic divergences**, and all 44 failures
  the SAME compile-size refusal on six patterns.

  **§3 is K53, an ENGINE issue found through `\p`**: the OPTIONAL anchored
  DFA machine's bytes count toward `max_emit_bytes`, so it refuses patterns
  that compile without it (`\p{L}` under `-e utf8` is 1,076,640 bytes at
  default axes and **772,412** with `-fno-anchored-dfa`) — contradicting that
  machine's own design promise that its overflow is a selection outcome and
  never a diagnostic. It also refutes `utf8_design.md` §3.3's sizing
  conclusion, which measured STATES where the emitted size is
  `states x CLASSES x digits`.

  **§4b is about the whole tree and a RULING IS OWED**: the shared dlopen
  shim resolves macOS's SYSTEM libpcre2 **10.42 / Unicode 14.0.0** on this
  box, not the Homebrew 10.48 that `BOILERPLATE.md` and the `[MACPORT]`
  report both name — bare SONAMEs precede the Homebrew absolute paths. Every
  dlopen-based oracle in this repository is affected, and it re-opens what
  U13's 119 PC-3 failures actually measured. The lane added a
  Unicode-version accessor and made its own suite PRINT the resolved version
  rather than reordering the list, which would re-baseline the whole suite.

  **§5 is a cursor bug the differential structurally could not see**:
  `esc_class_value` never advanced past a produced `EXT_MEMBERS`, so
  `[^\p{L}]` excluded `{` and `}` as well as the letters. Found by the
  ORACLE-FREE invariant `[^\p{L}] == \P{L}`, because both sides of the
  membership differential compile `\p{L}` at an ATOM. `esc_atom`'s
  [M6.5.2] lesson at the class position, predicted verbatim by that entry.

  **§6 scores the brief's four traps and TWO fired inverted.** S121 did NOT
  wake at stage 3 as stage 1 predicted — and stage 1's reach probe would have
  said it had, because it asked only whether `\p{L}` COMPILES and stage 3's
  own encoding clamp makes that eight Latin-1 runs. The hazard is now proven
  STRUCTURALLY unreachable with a `\p`-free control. §9 is the caseless rule
  (`Lu`/`Ll`/`Lt` are `L&`, everything else invariant), which is why stage 4
  turned out not to be a precondition.

- `tt4m3_report.md` — [TT-4M] STEP 2c (2026-09-08, lane tt4m3):
  `HARNESS_BATCH=N` implemented in `tests/harness/run.sh` per the
  r55-revised design note. Read it for two general (non-batching-specific)
  bugs it found and fixed while building: `tests/lib/size_count.sh`'s
  `size_count_row` hardcoded the literal `RX_*` macro names, silently
  blank for any non-`rx` `-p` prefix (a first attempted fix, deriving the
  prefix from the artifact's FILENAME instead, was itself wrong and broke
  the unbatched case too — caught by re-running that leg, not assumed);
  and bash's `read` collapses/strips TAB-delimited empty fields even under
  a single-character `IFS=$'\t'`, corrupting batch member case data,
  found via a live answer-identity mismatch and fixed by packing with
  `\x01` instead. §"Findings" F4 is a suite-wiring gap the design's own
  item-5-owed sabotage row runs into: `make mech`'s `harness` suite arm
  never sets `HARNESS_BATCH`, so every line this lane added is
  structurally unreached by `make mech` today regardless of what row is
  written — the row is drafted, not committed, pending that decision.
  Delivered BUILT AND SMOKE-VERIFIED (several small-slice byte-identical
  diffs against the unbatched path, including a live degradation smoke via
  a temporary since-removed corruption hook), NOT BATTERY-VALIDATED — the
  box was held by lane utf8s4 for this lane's whole working period; §"OWED
  to the manager's 2d" names the exact commands.
- `utf8s4_report.md` — [M5.0] STAGE 4, DD-1's FOLD CLOSURE (2026-09-08, lane
  utf8s4). `(?i)k` under `-e utf8` matches U+212A: `CaseFolding.txt` vendored,
  the fold published as two `PcrecFold` objects the ENCODING chooses between,
  the caseless backreference folding code points in the artifact, S-U11 (owed
  since stage 1) live, and S-U1/2/3 DETECTED. Read it for five things.

  **§3.1 is the stage's real result and it is not in the design at all**: the
  fold applies PER CONTRIBUTION, not to a class's merged set. Folding the
  merged set is wrong in BOTH directions at once — `(?i)[\p{Lu}x]` would match
  U+0345 and `(?i)[[:lower:]]` would match U+212A, neither of which libpcre2
  does, while `(?i)[\p{Lu}k]` and `(?i)[[:lower:]k]` must still reach U+212A
  through the literal beside the produced set. So `p_class` folds its OWN
  members and unions the produced ones after; `utf8_design.md` §4.2/§4.3 say
  "the SET" and owe a hunk.

  **§3.2 is the trap an implementer walks into**: one Unicode table clamped to
  `max_cp` looks right and folds Latin-1 under `byte`. The two relations
  DISAGREE rather than nest, so the fold is a per-encoding object.

  **§3.4 is a WRONG ORACLE in the D27 corpus**, and the provenance explains it:
  axis06's four `[^\p{Ll}]` blocks were `perr` from authoring until this stage,
  so their recorded oracle had never been exercised against anything — and it
  contradicts `utf8_design.md` §4.3's own measured table, which was right.
  **A parked cell's carried oracle is an unchecked claim until the construct
  compiles.**

  **§3.11 is the seam check's own limit**: DD12a(i) excises encoding-owned
  regions by a CLOSED LIST OF ENTRY NAMES, so an entry whose body needs a
  helper grows the region without the check knowing — it reported "an encoding
  conditional reached the hot path" for three private helpers of the caseless
  compare. The check was right to fire; its region definition needed widening.

  **§3.12/§3.14 are two process findings**: rewriting `cls_casefold` staled
  S08/S09/S10, whose re-aim is verified by reproducing their own recorded
  6/14/8 counts; and the harness reported `180 passed / 0 failed` where a quiet
  box reports 237/0, so a starved worker reduces the case COUNT rather than
  failing.

- `bat4triage_report.md` — TRIAGE of the stage-4 merge battery's `test`-stage
  red (2026-09-08, lane bat4triage, log-reading + code diagnosis only, no
  suite runs — the battery was still running the axes/san/mech stages
  throughout). Every failure in `build/battery_20260908_stage4/test.log`
  enumerated and classified. TWO are real, stage-4-attributable, and FIXED
  here: `tests/codegen/run_cpset_structure.sh`'s [1c]/[2d] needles are
  literal source-text matches ([M5.0] stage 4's `parse.c`
  `cls_universe`/`enc_byte.c` struct-literal edits legitimately moved the
  text they grepped for — a check-staleness class, not a correctness
  regression) and `tests/rxtsource/run_rxtsource_tests.sh`'s census pin was
  never moved for the new `tests/utf8/fold.rxt` (+1 file/+18 blocks/+57
  lines, re-pinned here; `C3_PASS`/etc. left explicitly OWED to a Linux
  re-run). Everything else is PRE-EXISTING darwin/python noise, independently
  reproduced rather than assumed: `xargs -a`'s BSD incompatibility
  (catalogued since `76f9e85e`, predates stage 4), three genuine
  python-3.9.6-vs-reference divergences in untouched corpus files
  (`caseless.rxt`/`counterk.rxt`/`captures.rxt`, each reproduced with this
  box's own python3), a NEW finding that BSD `wc -l`/`wc -c` padding breaks
  several `[ = ]` string-equality checks in the same script (not fixed —
  out of scope, flagged for the manager), and `tests/anchored/
  run_anchored_diff.sh`'s "26 patterns fail to compile" reproduced CLEAN
  with the battery's own `build/pcrec` binary, pointing at box-load/
  watchdog contention during the concurrent `test` stage rather than a
  real compiler defect. No `_log.md`: the investigation order is this
  report's own section order.
- `santriage_report.md` — the [TT-12] battery `san`/`lint` instant-exit
  triage (2026-09-08/09, lane santriage): both stages compile the COMPILER
  AXIS through the Makefile's own `CC ?= gcc` default, which on this Mac is
  Apple clang — rejecting `-fsanitize=leak` outright (`san` died on its
  first object file, rc=2 in under a second) and lacking `-fanalyzer`
  entirely (`lint`'s own guard SKIPPED everything and read rc=0 in under a
  second, a legitimate-shaped guard hiding a real vacuity since the Mac
  move). Fixed by sourcing `tests/lib/cc_resolve.sh` in `scripts/battery.sh`
  and passing the resolved `CC` to those two stages only. History check:
  the only prior GREEN `san` in the journal predates the 2026-09-04 Mac
  move; every post-move GREEN battery ran on `ubuntubudu` — this was the
  first time `battery.sh`'s `san`/`lint` stages ever actually executed on
  darwin. Validated by reproducing the exact failing compile line and the
  `lint:` guard probe with `gcc-16` (both succeed) — no `san`/`lint`/battery
  run was started, per the box hold in force at hand-off.
- `santriage2_report.md` — K54's ROOT CAUSE (2026-09-14, lane santriage2,
  sonnet, read-only triage of the W23.1 merge battery's killed san stage):
  `ASAN_OPTIONS="detect_leaks=1"` makes every gcc-16-sanitized process on
  arm64-darwin HANG AT EXIT at ~100% CPU (240s+ observed, never returns;
  0.07s at `detect_leaks=0`) — pattern-independent, both axes, reproduced
  on trivial patterns / `--list-schema` / `--probe-ask` / a generated
  matcher. Explains BOTH killed darwin batteries end to end (the reject
  stage's 614× exit-124 "irreplaceable checks are gone" = budget-kill
  artifact; the cli watchdog CPU kills; the harness's 0-bytes-in-5h pace,
  floor-estimated ~227 CPU-hours WITH the hang). Two named residues: the
  cli log's ~39%-vs-100% hit-rate discrepancy, and the registry buffer's
  summary-but-no-rc (killed mid-tail, not trusted green). Fix (the
  Makefile `SAN_DETECT_LEAKS` derivation) landed by the manager in the
  same change; known_issues.md K54 carries the resolution addendum.
- `w23design_report.md` — [DD-13b.W23] STEP 1 (2026-09-12, lane
  w23design, opus; design only): `format_design.md` REVISION 3, the
  [B42] absorption under F-Q1/F-Q2. Read it for the one pre-ruling
  deviated from on measurement — the bench's find-all formula
  `pos = max(end, pos+1)` DOUBLE-COUNTS an empty match found beyond the
  scan position (`(?=a)` on `"xax"`: 2 vs 1), so `mc`'s spec rule is
  `match_api.md` §3.1's shipped protocol by reference — and for the two
  leanings worked to answers: the body SUB-BLOCK mechanism (customers
  `provenance` + the reshaped `variant`; regime grouping deliberately
  NOT among them) and the §4.5-item-4 regime repair via the composer's
  derived-identifier lookup (`pcrec_rxt_prefix_from_name`'s one home,
  collision refused at use, zero name-grammar-reader changes). Frank
  queue: W23-F1 `configs describe` (D93), W23-F2 `capable` in-format,
  W23-F3 the mc deviation.
  **ADDENDUM — REVISION 3.1** ([DD-13b.W23] STEP 1.1, 2026-09-12, lane
  w23recon, opus, same branch): the RECONCILIATION against Frank's two
  2026-09-12 rulings, which were issued mid-flight and never reached the
  authoring lane. §1.2 becomes a two-layer grammar (a context-free
  STRUCTURE layer + a declared SCHEMA), the head/body indentation
  asymmetry is DELETED rather than narrowed, the `version` break is
  priced and DECLINED with the keyword reserved, §2.25 designs the
  schema and `--list-schema`, and §2.26's ownership audit moves four
  spellings. Read the addendum for **F1**, the sharpest: revision 3's
  own load-bearing parser rule — "the indentation test PRECEDES token
  dispatch, in all three body readers" — is MEASURED FALSE in two of
  the three (leg B has no indentation test at all and reaches its
  catch-all by fall-through; leg C dispatches an indented pre-body line
  on its first token), so P-Q1's one parser hazard was closed by a rule
  that mostly did not exist; the two-layer split makes the hazard
  structurally impossible instead. Also **F2**, the corpus census the
  note is written against went stale with [M5.0]'s corpora (179/3,265/
  26,691 → 210/3,936/28,943), which is why §1.1 now states the
  denominator RULE instead of the numbers; and **F3**, only 26% of
  `pattern` lines are blank-preceded, which is what closes the one
  alternative to a keyword for block grouping. And **F6**, the lane's
  own additivity claim was wrong once and a PROBE found it: the new
  attachment rule is depth-sensitive where today's head rule is not, so
  a RAGGED head body (lines at differing depths) goes from accepted to
  refused — measured byte-identical on the shipped binary today. Taken
  deliberately (population measured 0 in both repos, and forced by
  two-level nesting), and it is why the note's standing rule for when a
  change needs a `version` line went from two cases to three.
  **ADDENDUM 2 — REVISION 3.2, the r57 FIX ROUND** ([DD-13b.W23] STEP
  1.2, 2026-09-12, lane w23fix, opus, same branch): the three-critic
  panel's 3 blockers / 14 must-fixes / 12 shoulds / 4 nits worked
  through. Read it for the three PUSHBACKS, each with its measurement,
  because they are where the lane did not simply comply. **(1) Two of
  the panel's four new narrowings are narrowings AVOIDED, not taken** —
  declaring the block scalar as a structure device (S3 OPAQUE REGIONS,
  the round's central fix: three critics converged on the block scalar
  as the un-modeled object, and an indented `#` inside one is PROSE
  today at rc 0) dissolves both, so the census lists five candidates and
  marks two avoided WITH the mechanism, since a later wave that weakens
  S3 re-creates them silently. **(2) K57 is filed rather than handed
  back**: the `|` block scalar's dedent strip is a BYTE COUNT, so a
  continuation line indented less than the block's first **silently
  loses content** (`  dedented-line-two` under a 4-space block decodes
  as `dented-line-two`, exit 0) — wrong under every revision of the
  note, so no design decision fixes it by arriving. **(3) The `wave`
  column is KEPT against the panel's lean**, because its consumer is
  real during the five-merge ROLLOUT even though its population is
  empty at the delivered pin — stated with its expiry condition.
  Also worth reading: the structure layer now takes **TWO** schema
  parameters rather than one, and the second (`value = prose`) is the
  open-ended one the note was already describing without noticing; the
  constraint vocabulary goes from five kinds to **eight** after four
  W23 refusal rules failed to fit five, one of them needing precisely
  the kind the same section DEFERRED with a trigger a production one
  section earlier already met; the `pattern`/`pattern-esc`
  both-in-one-block refusal is DROPPED as an EMPTY POPULATION (both are
  block openers, so a second opener starts a new block — K35 caught at
  design time, before the check existed); and the methodology note that
  is this house's THIRD recorded instance of one trap — comparing two
  emitted artifacts written to different `-o` basenames reports a false
  difference on the `#include` line, which first read as REFUTING a
  true byte-identity finding. New Frank queue item **W23-F4**
  (ready-to-ratify, manager recommends ACCEPT): the derived-identifier
  repair removes the ability to declare a deliberately NON-CALLABLE
  definition, a boundary `src/parse/rxt_source.c:288-291` records as a
  feature.
- `w23fix3_report.md` — [DD-13b.W23] STEP 1.5 (2026-09-13, lane
  w23fix3, opus; docs only): the r58 FIX ROUND, `format_design.md`
  revision **3.4.1**. §0.10 of the note is the finding-by-finding
  record; this report is what the fixes REVEALED and is worth reading
  for six things the review did not anticipate. The sharpest: **the
  ruling that removed prose values from aux bodies falsified two worked
  EXAMPLES** (§2.27's own `matrix |` and §6.2's `policy |`), which no
  critic cited because a critic cites the rule and not its
  illustrations — so a fix round's sweep must include every fenced
  block the ruling touches, found by grepping the rule's SPELLING and
  not its NAME. Also: the open-subtree parameter costs no extra SCHEMA
  COLUMN (it reads `children`, which parameter 2 already read, so the
  note says three parameters over three columns); the parameter
  incidentally CLOSES §3.3's own flagged-open `--list-schema`
  fetchability item, because all three parameters become row sets
  selected by a column value rather than a row set plus a predicate;
  sabotage row S-R6's plant gained a structural blast radius for free;
  an aux-fixture count was wrong at 3.4 and nobody had counted it; and
  §1.6.1a carried a positive assertion of the reversed decision in a
  section about something else — this round's own instance of the
  DISPOSITION-TEXT residue class the r58 panel named, which neither a
  grep nor an inverse mechanism walk reaches.
- `w23impl_report.md` — [DD-13b.W23] THE IMPLEMENTATION NOTE (2026-09-13,
  lane w23impl, opus; docs only, no runs). Delivers
  `docs/design/dd13_format/w23_impl.md` — five merges, nineteen fixtures,
  six sabotage rows S239-S245, SW1-SW19 distributed per step, and the
  bench's 41-check bar mapped onto the staging. Read the report for five
  things the plan surfaced that the brief did not anticipate.
  **The headline is that the `NF != 15` defect is ALIVE in this repo**,
  found by RUNNING the format-reader survey §2.24 obliges rather than by
  inheriting its lesson: `tests/rxtsource/run_rxtsource_tests.sh:479-494`
  asserts that every non-comment `--list-source` row has exactly
  `ncols+1` fields, unconditionally of kind, which four `#section` blocks
  violate on every row — **and its failure message names a TAB in a field
  as the only possible cause**, so a lane meeting the red after emitting a
  section goes and reads the escape function. The generalisation, third
  instance in this house: *a check that asserts a SHAPE goes stale when
  the shape gains a variant, and its FAILURE MESSAGE is a second,
  undeclared claim about the space of causes that goes stale with it.*
  Also: the other three dump readers survive sections only because every
  section's first column is an integer and no main-table `kind` token is
  one — an invariant written nowhere, now check W23-S4, with the ordering
  rule it rests on (sections FOLLOW the main table) stated while it is
  still free; why the STEP 0 legs-B/C parity fix belongs in the step that
  builds the diagnostic-CLASS machinery rather than in any harness step
  (*a refusal neither leg can produce is a refusal with no class*) and why
  leg B DETECTS a NUL rather than carrying one; that
  `pcrec_rxt_source_ncols()` has zero callers beside a comment still
  reading "THE 15 COLUMNS" over a sixteen-entry array; and why
  §2.27.3 clause 5's value-identity check gets **no sabotage row** — its
  violation is a patch somebody writes on purpose, not a corruption of
  shipped code, so the check is the detector and the review is the gate.
  §4 discharges the standing constraints explicitly: **no abi event was
  discovered** by the file-by-file plan (confirmed, not restated), and the
  withdrawn mechanisms' absence is a per-step grep rather than a promise.
  Nothing owed.
- `w23implfix_report.md` — [DD-13b.W23] STEP 1.6 (2026-09-13, lane
  w23implfix, opus; docs-only): the r59 FIX ROUND, `w23_impl.md`
  revision **1.1**. The note's own §0.5 is the finding-by-finding
  record; this report is what the fixes REVEALED, and it is worth
  reading for six things.
  **The sharpest is that the round's residue class was CITATION
  PROVENANCE rather than disposition text**: TEN wrong `file:line`
  ranges and four wrong counts, of which SW12's two comment sites came
  from `format_design.md`'s own SW12 row (one of them, `:1126-1130`,
  naming the file-level duplicate-`description` refusal — a different
  production entirely, at a plausible-enough offset that a reader
  following the citation would have found a comment about the wrong
  rule with no signal anything was wrong), and `format_design.md`
  §2.11's `run.sh:184-216` for the harness's per-file loop is wrong
  too — which is where the r59 REVIEW itself got the range it cited
  for the discovery site. A forward grep cannot see this class and an
  inverse mechanism walk cannot either; the third pass sees it only
  if the pass opens the FILE rather than comparing two documents to
  each other.
  **Second: the withdrawal-absence check grepped the wrong five
  tokens.** `testee`/`option` are LIVE format spellings at three sites
  (`rxt_source.c:149`'s two `config_vocab` rows,
  `docs/spec/rxt_format.md:57-62`'s later-wave keyword list, and
  `run_rxtsource_tests.sh:1188`'s `CENSUS_WORDS_32` whose length is
  pinned at 32), so the withdrawal costs four sites and a deliberate
  narrowing rather than "a diff and nothing else" — an absence check
  is only as good as its token list, and a list derived from the
  mechanisms somebody remembers withdrawing will miss the third.
  **Third: spec row S3 has never landed** and its WAVE LABEL is what
  made it look landed — a label says when a row was scheduled, never
  whether it shipped.
  Also: three of the four S200-S203 sabotage rows carry a stale count
  in `SAB_DESC` (not one, as the review had it) — the same
  pinned-number-in-prose class the survey those rows detect is about;
  the review's own 22-arm split (18+5) is wrong where its total is
  right (17 pinned + 5 appended, per `format_design.md` §0.7); and
  `format_design.md` §9's A1 row carries the same unverified
  block-scoped-`include` reading A2 did, which is r58-B1 recurring one
  row up in the ruled record. Its §4 is the three one-line
  `format_design.md` corrections the lane deliberately did NOT apply,
  each with its evidence, since the brief scoped the drive-by to SW12.

- `<lane>_rulings.md` — the manager's rulings to a lane, written BY FILE while the lane runs (a busy lane reads messages only when it idles; the file is polled at each stage boundary — memory `pcrec-lane-hold-lift-artifact`). GITIGNORED BY DESIGN (see .gitignore): it is live coordination, not a deliverable; the lane's report §"Rulings received" restates every ruling that shaped the delivered work, and the journal carries the manager's side. When a delivered worktree is removed, its rulings file is copied here as a LOCAL, still-ignored file (edge1, w13 on 2026-09-04; lim2's was lost with its worktree — its rulings 1-5 are in lim2_report.md §7 and 6-7 in journal parts 62-64) — these local files do NOT travel by git (memory `pcrec-two-machine-split`).

- `utf8k53_report.md` — [K53-SELRETRY] (2026-09-10, lane utf8k53): the
  OPTIONAL-CONTRIBUTOR DROP LADDER. On an emitted-size cap refusal with the
  optional anchored machine present, `compile_driver` drops it and re-emits;
  `\p{L}` under `-e utf8` compiles at default axes and the sixteen parked
  blocks are back in `tests/utf8/`. No new stamp, no `abi` bump. Read it for
  four things.

  **§4 is the finding the row did not predict**: the corpus population of the
  fix is NOT the `\p` family. Eight patterns stop refusing and every one is a
  wide literal alternation from `tests/rxtsource/fixtures/
  bench_altwide_0_2.rxtin` — pcrec-bench's own `altwide` witnesses — because
  the codegen census compiles corpus `pattern` lines with no encoding, so the
  six `\p` names are `byte`-clamped and tiny there. That discharges K53's own
  "filed as an ENGINE issue, not a Unicode one" rather than merely asserting
  it, and it MOVES THE REFUSAL SET, which [LIM-2]'s charter ("the refusal set
  moves NOT AT ALL", with the bench's altwide refusal table as its
  before/after control) has to be re-based against.

  **§5 is two checks going red for the right reason.**
  `run_anchored_match.sh` §5's fourth bucket — "the anchored machine
  overflowed a STATE cap" — was defined BY ELIMINATION, so the eight landed in
  it and the check advised re-deriving a 4,096-state ceiling the population had
  never approached: the right alarm with the wrong cause. And the
  `tests/rxtsource` census caught a defect in the lane's OWN corpus move (the
  splitter's last group ran to end-of-file, duplicating four blocks into
  `axis04`) that NO test could see, because the duplicates compiled and
  answered correctly. *A bucket reached by elimination is one that will one day
  hold something else.*

  **§6 is why the design promise broke.**
  `anchored_match_unwrapped.md` §5.2 enumerated the budgets the optional
  machine is charged against by walking `pcrec_build_dfa`'s PARAMETERS, and
  the emitted-bytes cap is charged three machines downstream where "whose
  bytes are these" is unanswerable — so the enumeration was complete in the
  code it read and incomplete in the property it claimed. *"Optional" is a
  claim about every resource a component consumes, and they are not all
  charged where it is built.*

  **§1.2 answers the brief's ladder question and §2 its stamp question**: the
  general "drop optional contributors" shape IS right and ships as an ORDINAL
  with one rung, because a second rung needs an ORDER and an order is a
  measured run-time cost per contributor that a sample of one cannot supply;
  and the event reuses `ESEL_SIZE_CAP_RETRY` rather than minting a value,
  since the two rungs are mutually exclusive BY ENGINE and the artifact's own
  axis stamps therefore say which fired.

- `clstudy_report.md` — [CLS-TREE] THE STUDY (2026-09-11, lane clstudy,
  opus; study only, nothing under `src/`/`tests/`/`docs/spec/`). Delivers
  `docs/dev/cls_tree_study.md` + `studies/cls_tree_study/`. Read it for
  three things. **The general form covers TWICE the population the shipped
  special case does**: 8 of the 41 distinct byte classes in the corpus take
  a one-cube test and only FOUR are case-fold pairs — `{a,c}`, `{g,k}` and
  `{A,B,a,b}` get 32-byte bitmap tables today because [FORM-CHAR]'s
  `(lo^hi)==0x20`-and-both-letters classifier is structurally blind to
  them, while the kit's O(k) `cube_of` reaches all eight without being told
  what caselessness is. **The expensive half of the analysis did not pay**:
  the exact Quine-McCluskey minimizer — Constraint 1's own textbook answer —
  costs 4.9x the discovery time to change 10 of 126 sectionings for 0.36%
  fewer ops, and was dropped. **And three bugs its own instruments caught**,
  each recorded for the instrument rather than the bug: a cost model that
  prices a form without materializing it is only safe if something
  independently builds and checks; two implementations of one algorithm
  disagreed on 12 of 36 cells while each stayed self-consistent; and a
  Pareto point dominated on BOTH axes is a modelling error, not a result —
  the sweep built to characterize a trade-off refuted the cost model that
  generated it. Headline: `\p{L}` 227,409 object bytes today vs 4,359;
  discovery 26.4 ms on the worst real set, so the D77 verdict is that
  Constraint 2's pre-analysis cache is NOT triggered.

- `abifix_report.md` — [S5-ARM] landing validation for lane abifix's fix
  (2026-09-11, lane abifin: WIP commit d22ca9df already fixed
  `tests/fuzz/pcre2_abi.h`, this lane finishes the owed validation +
  disposition). The bug: [ORACLE-LINK]/D98's dlopen-to-direct-link
  conversion moved `#include <pcre2.h>` ABOVE `#define _GNU_SOURCE`/
  `#include <dlfcn.h>` on the false claim that `pcre2.h` "does not touch
  `<features.h>`" — it does, transitively via its own `<stdlib.h>` —
  silently reintroducing the `K-uprops-abi-order` hazard for every
  consumer on glibc, invisible on darwin for two days until the header
  was next built on the Linux reference box (S5-ARM), breaking
  `dladdr`/`Dl_info` in six suite stages. Fixed by re-ordering plus a
  new portable `#ifdef NULL #error` guard that fires on darwin too.
  Read this report for two things. **§3 is the utf8-count disposition
  (I-63: expected 1833, Linux printed 1829)**, derived from `git log`/
  `git diff` over `tests/utf8/` between the pins, independent of any
  live run: `[K53-SELRETRY]`'s own corpus-move fix (`880ba16d`) deletes
  exactly 4 duplicate blocks a splitter bug had put in
  `axis04_p_categories.rxt` on top of their correct home in
  `axis12_scripts.rxt` — 1833 counted the duplicates once each, 1829 is
  the correct post-dedup number and should replace 1833 anywhere else in
  the tree that cites it. **§5 is the Linux executor's exact 6-command
  re-run list** for the red stages (`make san`; `make test-registry`
  covering both PC-3 and PC-4, which are sub-stages of the one script;
  `ENC=byte`/`ENC=utf8 bash tests/uprops/run_uprops_tests.sh`, the utf8
  arm being the one to watch for the `[STORE] 387/387` line;
  `make test-atomic`). Darwin validation in §2 is all green and
  live-confirmed (uprops byte 47/0, uprops utf8 26/0 with `[STORE]
  387/387` exactly as expected, rxtsource 119/1/0, atomic_diff 8/0)
  except the long `tests/harness/run.sh tests/utf8/` count-confirmation
  run, launched last per BOILERPLATE's DO-THEN-FINISH and left OWED with
  its log path — corroborating evidence only, since §3's arithmetic does
  not depend on it.

- `m5close_report.md` — [M5.0] CLOSE-OUT RITUAL (2026-09-12, lane
  m5close, docs-only, nothing under `src/`/`tests/`). Runs the
  `compliance-refresh` skill over the whole milestone's changes: finds
  components 1 (generated construct index) and 3 (keyed annotations)
  ALREADY MATCHED the tree — the last compliance touch (`9bbdc0f9`, part
  of utf8s5's own lane work) already covered stage 5's script row, and
  neither K53-SELRETRY's fix nor [ORACLE-LINK]'s dlopen retirement moves
  anything `--list-syntax` reports (K53 is an engine/resource issue, not
  a grammar-recognition one). Component 2 (hand-written survey prose) WAS
  stale — the unicode-properties section still described K53 as an
  unresolved, permanent five-of-45-names size blocker, unaware of the
  2026-09-10 fix — corrected in place with the fix's mechanism and the
  corpus-population finding (the fix's real customer was pcrec-bench's
  `altwide` witnesses, not `\p`). `make test-registry` GREEN (PC-3 209/0,
  PC-4 62,872 cells/0 disagreements, definitions-oracle 354 cells/0
  disagreements) after a first foreground attempt timed out from box
  contention with lane rxtnul's concurrent `make test` — re-run
  backgrounded and polled via Monitor rather than blocking. Also moves
  `[M5.0]` to `plan_completed.md` verbatim (STATE flip + one appended
  completion stamp, no row content edited) and appends the
  milestone-close journal entry citing every stage's merge commit.

- `w231_report.md` — [DD-13b.W23.1] (2026-09-13, lane w231, opus): the
  SCHEMA TABLE and its surface. `rxt_schema.def` (66 rows), its reader,
  `--list-schema` as the seventh registry dump, leg A's dispatch rewritten
  as a WALK over the table (S0-S3 and the OPEN SUBTREE), the diagnostic
  CLASS tag at 62 call sites, ten structure-layer fixtures, W23-S3's six
  arms, S241/S244, five spec hunks and the `testee`/`option` withdrawal.
  Read §3 first: it is **four places the implementation note contradicts
  itself or the design**, each with the resolution taken — headed by §2.2
  and §6.1 disagreeing about whether W23 ROWS exist at this pin (resolved
  in §2.2's favour, because §2.3 is a contract the step signs and a
  DERIVED "not in this build" list needs rows), and by SW13 promising
  `version` is RESERVED with nothing implementing it (a keyword with no
  row refuses as UNKNOWN, which is the truth about a withdrawn production
  and a lie about a reserved one — so `version` got a row with a reserved
  sentinel wave and a third refusal sentence).
  §4 is what the build found: `RxtScope` was already taken by a
  file-local typedef in `rxt_compose.c`; the old hand tables' `wave`
  values had been STALE since F-Q1 collapsed W2/W3 and nothing saw it
  because every fixture greped the phrase and never the number; and
  **W23-S3's wave arm first read 0 rows out of a population of 7 and
  printed `0 of 0`** — bash's `read` collapsing the dump's empty TAB
  fields, `tt4m3_report.md`'s trap — whose transferable half is not the
  bash defect but that *an arm deriving its population from the data it
  checks must fail on an EMPTY population, or the first thing that breaks
  its extraction turns it green.* The cardinality arm likewise had to
  become dump-driven and TWO-DIRECTIONAL before S241 had a detector at
  all: the plant moves a row OUT of the at-most-one set, so an arm
  checking only that set passes under it completely.

- `w233_report.md` — [DD-13b.W23.3] (2026-09-15, lane w233, opus): THE
  FOURTEEN PRODUCTIONS. `pattern-esc` + `--pattern-esc`, `provenance`,
  `variant`, `ext`, the head declarations, `under`/`mc`/`@file:`, §2.22's
  derived-identifier call binding, the schema's `value` and `constraints`
  columns read for the first time, eleven fixtures, S240/S245, and the
  D80 spec delta. Read §4 first: it is **the two defects this step
  shipped and then found, both by measuring a production against all
  three legs rather than by reading it**. The sharper one is `under`'s
  KEY TUPLE — the extractor read a colon that the spelling does not have
  (`under <convention> <case-line>` is space-separated; leg C REFUSES
  the colon form by name), so the convention came out empty and every
  later component slid one place left: two `under` lines differing only
  in SUBJECT or only in STARTPOS were refused as duplicates **while the
  refusing fixture went red anyway**, for a reason with nothing to do
  with the rule. The regression is therefore the ACCEPT half, and the
  transferable form is that *a refuse-only pair proves a refusal
  happened and never that it happened for its rule.* The second is
  `prose_value` reading the whole line on an INDENTED one — `tok_len`
  stops at the first whitespace byte, so it measured zero — which every
  W1 caller was structurally unable to see because all of them sat at
  indent 0.
  §5 is what neither document named, headed by **the attachment branch
  holding three mistakes under one sentence** (a deeper indent under a
  childless kind; nothing open at all; a RAGGED DEDENT — and inside an
  OPEN SUBTREE the shared sentence named a rule the subtree does not
  have) and by **the wave tier's population going to zero**, which ate
  two fixtures and forced W23-S3 arm 4's repair: W23.1's *"a population
  of ZERO is also a failure here"* conflates the broken-extractor zero
  with the empty-tier one, and the fix is to assert the EXTRACTOR's
  health independently and then report the honest zero.
  §3 is six places the tree and the documents disagree, each with the
  resolution taken — headed by four aux fixtures that had to become
  HEADLESS (a FILE-scope production is a head declaration and the head
  has one parser, so §3.2's "all three ACCEPT" is unavailable at any
  point in W23 — r59-A2's disposition one production over) and by four
  design sentences the build measured FALSE (`oracle none <reason>` did
  not exist; an oracle's engine half was a strict `ident` while
  `variant`'s testee name was not; `provenance` was not required on a
  `freq` block; §2.18's sha256-syntax claim is structurally unavailable
  at this seam, and the `--list-schema` `surface` row that declares the
  non-coverage ended MID-CLAUSE about to claim the opposite).
  `make test` and `make mech` are OWED (§6) — a battery held the box for
  the lane's whole working period.

- `w233a_report.md` — [DD-13b.W23.3a] (2026-09-15, lane w233a, sonnet):
  `include`'s HARNESS HALF, **PARKED, NOT DONE** — legs A and B are
  built and verified, leg C is built for the one thing it can do, the
  three fixtures/W23-S7/S247/the census pin/SW20 are OWED. Read §3
  first for the OWED list; §2 is the load-bearing finding a fresh
  agent must not re-litigate: **leg C cannot splice**, structurally,
  because `include` sits in `parse_rxt`'s `head_words` tuple (it is
  inherently head-scoped) and the seam ruling's head-bearing refusal —
  UNCHANGED — already raises an uncaught `ValueError` on any file with
  an `include` line, in both plain and `--dump` mode, VERIFIED live.
  §1.10.2's table reads "legs B and C" symmetrically for report/splice/
  failure-attribution; the tree says leg C's half is discovery
  SUBTRACTION only, never a three-way block-count comparison — the same
  r59-A2 disposition w233's own report already recorded for file-scope
  `ext`, recurring here because `include` cannot be moved to block
  scope at all.
  §1.1 is leg A: W23.3 never emitted an `include` ROW at all (§6.3a
  item 1's "a COLUMN on a row W23.3 already emits" was wrong about the
  starting state, though right about the SIZE of the fix) —
  `RXT_DECL_INCLUDE` now does, `value`=path as written, `name`=the
  RESOLVED REAL PATH, resolved AT PARSE TIME (a deliberate, one-
  construct exception to "the head parser touches no filesystem",
  because `--list-source` is the only call the harness ever makes over
  an `include` line).
  §1.2 is leg B: entry-set SUBTRACTION (a pre-pass over the whole
  discovered set, before either dispatch branch) and SPLICE (each
  entry's closure walked depth-first, fragments INSERTED into `files[]`
  right after their entry rather than concatenated into one stream —
  which is what keeps every diagnostic correctly attributed to its own
  physical file for free, and what makes PROCS>1 correct with no
  fragment-aware code in the dispatch loop at all). Two real bugs
  before it worked, both worth reading for the general lesson: caching
  through `x="$(fn)"` is a no-op (command substitution forks a
  subshell; the cache write never escapes it) and `cd DIR && pwd` is
  LOGICAL, not `realpath(3)`'s resolved path (macOS's `/tmp` -> `/private/
  tmp` symlink silently broke every cross-directory include-target
  lookup). Verified by hand against six constructed scenarios (flat/
  nested/cross-file-duplicate/PROCS=2/named-absorbed/corpus-control) —
  the shipped corpus has zero `include` lines and cannot exercise any
  of it structurally.

- `w234_report.md` — [DD-13b.W23.4] (2026-09-15, lane w234, sonnet):
  `--list-source`'s FOUR `#section` blocks (`provenance`/`variants`/
  `cases`/`aux`), three appended pattern-row columns (`tags`/`oracle`/
  `esc`), four new head-row kinds, and the FORMAT-READER SURVEY's own
  R5/R6 repair (both made SECTION-AWARE, never a hand-written section
  list). Read §1.4 first: **six PRE-EXISTING checks needed the same
  repair** the moment a fixture's own case line legitimately grew a
  `#section cases` block, each reproduced as a genuine regression
  against a scratch build of the branch point before being attributed
  to this change. §1.5 is S242/S243/S246 and W23-S6, worth reading for
  two corrections the hand-verify caught rather than the first draft: S242's
  actual symptom is a stronger, TOTAL refusal (not the block_line drift
  a first reading predicts — the root frame's `f->base` only reaches
  BLOCK scope through the opener transition at all), and S246 variant
  (a)'s first draft sabotaged the WRONG scope's `ext` row (FILE instead
  of BLOCK, caught because `aux_identity_edited.rxtin`'s own two `ext`
  blocks are block-scoped and the plant went silently unexercised). §2
  is a FINDING: the withdrawal-absence check's data arm cannot tell a
  withdrawn `config`-body directive from an `ext` BODY line spelled the
  same way — this lane's own first-draft fixture used `testee`,
  `format_design.md`'s OWN worked example's exact word, and tripped it;
  fixed by renaming rather than narrowing the check (a design question
  left to the manager). §3 dispositions (does not resolve) the
  `w233_report.md` §3.2 OPEN ITEM on a `pattern-esc` row's dump VALUE
  disagreement between leg A and legs B/C — population zero, the `esc`
  column added here answers a different question, and which of the two
  should change is escalated rather than guessed. 191/0/0 (was 184/0/0
  at the branch point), census 210/3936/28943 unchanged, no `abi` event.

- `w235_report.md` — [DD-13b.W23.5] (2026-09-15, lane w235, sonnet): THE
  FINAL W23 STEP. Two manager rulings implemented — R-A (the pattern-esc
  dump-value seam, A-vs-(B==C) excluded by design, given its first
  non-zero population by `pattern_esc_value_seam.rxtin`) and R-B (the
  withdrawal-absence check's data arm narrowed STRUCTURALLY, an indent
  stack tracking attachment under an `ext` opener rather than a keyword
  list, restoring `aux_identity.rxtin`'s `testee` spelling and reverting
  w234's `ref` workaround) — plus `mc_illformed_utf8.rxtin` (SW7's owed
  W23.3 fixture) and W23-S5, the `all-readers` population check
  (receipts written only when all three legs actually ran, by two
  functions and nothing else). Read §2 for two NEW findings the dry run
  surfaced: leg C refuses any file whose FIRST block opens with
  `pattern-esc` (S242's own finding one leg over, meaning
  `opener_pattern_esc_pair.rxtin` has never been three-leg-reachable
  either), and `--source`/`--target`'s config resolution silently
  prefers a target's `engine vm` over an explicit CLI `--engine=dfa`
  with no diagnostic (`cli/main.c:890-891`) — exactly the "silence is
  not acceptable" shape bench check F2 asks about. §3 is the bench
  41-check dry run itself: 25 of 41 runnable, 20 green, 3 red with an
  already-documented cause (A1/A2/B5, each reproducing `w23_impl.md`
  §5's own predicted findings live), 1 red and new (F2), 1 the
  dissolved-premise shape (B6), 16 not-runnable (missing tool/sibling
  repo, or the box constraint on G1). §4 is the consolidated
  `w23_impl.md` correction list gathered from all five step reports
  (two real corrections, both already recorded in their own reports:
  w232's `indent_under_m.rxtin` class, w233a's `include` two-leg
  symmetry). 201/0 (was 191/0), mech field validation 256/256 valid
  including new sabotage S248 (a withdrawn `config testee` row's return,
  hand-verified DETECTED against the parser arm alone).

- `rulefix_report.md` — (2026-09-15, lane rulefix, sonnet): Frank's two
  rulings on w235's two findings above, implemented. **Ruling 1**: an
  explicit CLI `--engine=` now wins over a target's `engine vm` row in
  `cli/main.c:890-891` (was silent), with a non-fatal stderr diagnostic
  naming both sources and values — "explicit" is `ts.opt.engine !=
  PCREC_ENGINE_AUTO` at the point `apply_target` reaches the row, since
  that field has exactly two writers in the tree and no separate
  tracking machinery was invented for the `--engine=auto`-vs-unset
  ambiguity the ruling itself names as acceptable to leave unresolved.
  `docs/spec/cli.md`'s "the file wins" rule gains the one named
  exception. **Ruling 2**: `verify_rxt.py`'s leg C now accepts
  `pattern-esc` as a file's first block opener (`first not in
  ('pattern', 'pattern-esc')`), fixing the defect w235 found rather than
  documenting it as a seam. `opener_pattern_esc_pair.rxtin` (S242's own
  fixture) is now reachable by all three legs — re-verified live and
  given a permanent three-legged extension of S242's check, not just a
  hand-verify. Zero corpus population moved either way (0 shipped files
  open with `pattern-esc`). `tests/rxtsource` 205/0 (was 201/0: +3
  ruling-1 checks, +1 ruling-2 three-legged check), `tests/cli` 284/0,
  `make strict` clean. PARKED on `lane/rulefix`, not merged — a battery
  was in flight for the lane's whole working period; full `make test`
  is owed to the manager at the next one.

- `battriage_report.md` — triage of the 2026-09-15 W23 merge battery's two
  non-chartered reds (2026-09-15, lane battriage, sonnet; log-reading +
  targeted fixes only, `make test`/`mech`/`san`/`axes`/`lint` never run —
  the battery's own mech/san/axes/lint stages were still running for this
  lane's whole working period). Both fixed and PARKED, not merged. [K37]:
  `tests/rxtsource/run_rxtsource_tests.sh`'s W23-S6 arm-2 build invoked
  `"$PCREC" --source` bare in two subshells; wrapped in `"$TIMEOUT_BIN" 30`
  to match arm 1 and every other `--source` site in the file. The
  `run_cpset_structure.sh` CHECK 3 manifest drift is the sharper one: both
  moved `EMITTED_BYTES` rows are traced EXACTLY (byte for byte, verified
  by recompiling both witnesses with `--emit-main`) to the already-ratified
  `05c27b43`/`e1bf0025` [PORTFIX] abi-25 label fix already on this branch
  — a legitimate consequence, not a regression — and re-recorded
  deliberately. **The finding worth carrying forward**: `e1bf0025`'s own
  grep-based abi-bump re-pin sweep (grepping for the literal old abi
  number) structurally cannot find a manifest like this one, whose rows
  never cite an abi digit at all but whose byte-count VALUES move anyway
  — a second reader class ("content depends on the scaffolding" vs. "text
  cites the abi number") the ritual's grep needs to widen to cover.

- `dialsweep_report.md` — [OPT-DIAL] §7 SIZE SWEEP (2026-09-15, lane
  dialsweep, sonnet; measurement only, nothing under `src/`/`tests/`).
  Eight full-corpus passes (baseline + the six switches §7 names plus one
  bonus, `-fno-anchored-dfa`, §7 item 3) through `tests/harness/run.sh`'s
  existing `SIZELOG`/`RXTDUMP` hooks. Headline: `-fno-tiered-entry`
  graduates to a clean MEASURED TRADE (every one of 330 movers shrinks by
  a near-fixed ~1,953 B against the inventory's already-measured ~5x
  per-call win); `-fno-anchored-dfa` turns out to have the LARGEST reach
  of any switch in the whole inventory (43.39% of the corpus, monotone,
  worst case -266,794 B), replacing its old pathological-population-only
  size number. `-fno-altcls-merge`/`-fno-altcls-factor` mostly confirm the
  inventory's "likely a PURE WIN" hypothesis but each carries one real
  non-monotone counter-example, the same shape `--unroll=K`'s own curve
  warns about. `-fno-possessify`/`-fno-revdet` stay fully UNMEASURED —
  neither had a TIME number before or after; this sweep supplies only
  their size half. See `docs/dev/optdial_size_sweep.md` for the full
  per-switch memo and `docs/dev/optdial_size_sweep/` for the reproduction
  pieces. Does not edit `docs/design/opt_dial_inventory.md` itself (D80).

