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

- `byteid_report.md` — [K59RUNG-BYTEID] (2026-09-17, lane byteid,
  measurement only): the corpus-wide byte-identity sweep confirming the
  dial+K59 train (merge `cf0962e3`) moves no emitted byte beyond the
  `RX_TUNE` stamp's own known, constant delta. 3,938 corpus pattern lines,
  1,500 movers, every one exactly +27 bytes (the unconditional
  `RX_TUNE "balanced"` line plus a same-length `.abi: 25 -> 26`
  substitution), verified by full-diff inspection across the corpus's
  whole size range, not just by size. See `docs/dev/dialtrain_byteid.md`
  for the full memo.

- `btriage_20260917_report.md` — triage of `battery_20260917_102334`'s
  `test`-stage red (2026-09-17, lane btriage, sonnet; log-reading +
  targeted fixes only — the dial+K59 train's own merge battery on
  ubuntubudu was still running its axes/san/lint/mech stages for this
  lane's whole working period). Named with a date suffix because an
  earlier, unrelated lane (`btriage2`, 2026-09-10) already committed a
  report at the un-suffixed `btriage_report.md`. **Verdict: the red does
  not block the `cf0962e3` pin** — both failures are stale test-side
  pins, neither a defect in the `--tune`/K59RUNG mechanism. (1)/(2):
  `tests/resource/run_resource_tests.sh`'s two `size_moved` witnesses
  were rescued below the 1,000,000-byte cap by K59's new `SDR_NO_PREMUL`
  drop-ladder rung, which — unlike `min-size`'s own dial position — fires
  at EVERY `--tune` position on any DFA-engine artifact the cap refuses;
  a real, intended, verified consequence the merge's own delivery should
  have re-pinned and didn't. Row 1 re-witnessed at a larger count
  (`{1,8000}` → `{1,13000}`, still refuses at 1,034,779 bytes); row 2
  (`a{5,25000}`) has NO safe larger witness — raising `N` past ~31,500
  under its deny flags hits K25's own chain-minimization slow zone before
  ever regaining the cap (measured, two substitute shapes tried and
  rejected) — so it is retired from the refusal loop and flipped to a
  dedicated acceptance check asserting the rescue itself, the same
  flip-the-assertion precedent this file's own [OPT-4.1]/[OPT-4.2] cells
  already used. (3): `tests/rxtsource/run_rxtsource_tests.sh`'s
  `C3_PASS` pin (13708) predates `e0bc115b` (lane `cmtfix`, [O-31 F1],
  merged hours before k59rung the same day) adding
  `tests/base/comment_escape.rxt`'s 6 python-verifiable cases without
  re-pinning C3 — pre-existing staleness unrelated to k59rung's own diff,
  surfaced only because this battery is the first `make test` run after
  both commits landed. Re-pinned to 13714, isolated-verified via
  `verify_rxt.py` on the single new file. Both fixes re-validated locally
  (25/0 resource, was 20/2; 212/0/1-recorded rxtsource, was 211/1) — the
  one `RECORD:` line is this box's pre-existing darwin C3
  non-native-pin behavior, unrelated to either fix.

- `w1kit_report.md` — [REVW.1] WAVE 1 STAGES 1-2, the EMISSION KIT
  (2026-09-18, lane w1kit, opus): the text layer
  (`sb_text`/`sb_textn`/`sb_field`/`sb_join`/`sb_row` in `src/core/sb.c`),
  its adoption across the five TSV producers, `cli_err`, and L10-2's
  bounded-join fix. Read §0 first: **the charter's central stage-1 proposal
  is refuted by the tree.** `lens10_emission_kit_charter.md` §2.2(4) promotes
  `rxt_source.c`'s `put_escaped` as the one field escape and names the
  registry dumps as its customers; that vocabulary DOUBLES a backslash, and
  **150 data rows** across `--list-syntax`/`--list-families`/
  `--list-definitions`/`--list-axes`/`--list-limits` carry a raw one (the
  `syntax` column is literally `\d`, and `tests/reject/` builds probe
  patterns from it). The charter half-saw this — it keeps `put_text`
  separate on exactly this ground and names the `\xNN` tail as the shared
  part — and drew the line one file too far left. The kit ships TWO
  vocabularies over ONE implementation instead.
  Also worth reading for four things. **The charter's own stage-1
  precondition is answered ZERO** (no `--list-*` row carries a non-TAB
  control byte or a wrong field count), so the escaping is insurance and
  byte-neutral *in the correct vocabulary* and a 150-row regression in the
  proposed one. **L10-2's severity is LATENT, not live** (the module list is
  179 bytes of 512, the encoding menu 10 of 128), and `pcrec_enc_names`'
  defect is worse in kind than recorded: the separator is written under a
  DIFFERENT bound from the name, so a tight cap emits `"byte, "` — a
  DANGLING SEPARATOR, a menu reading as though a name went missing rather
  than as a truncated list. **`sb_join` is DECLINED at both bounded joins
  with a measured reason** — it needs a `StrBuf`, and `pcrec_enc_names` sits
  on `pcrec_compile`'s own refusal path where a failed realloc would
  `abort()` the CALLER (coding guide §1.1); one stated policy at both beats
  one of them reaching the primitive. And **`cli_err` ships with no `where`
  parameter**: the charter's item 7 gives it one (with a `format(printf,
  3, 4)` attribute that does not match its own signature) and not one of
  `cli/main.c`'s 79 stderr sites has that shape. D26 is proven two ways by
  instruments that deliberately do not share a rule — a 79-message set
  normalized by deleting `"pcrec: "` and `"\n"` ANYWHERE (not by stripping
  a prefix and a trailing newline the way the conversion does, which would
  have read green on exactly the four ternary-tailed sites the conversion's
  own first rule got wrong) and a 1.68 MB live argv sweep. Anchors: S200
  re-aimed FILE-ONLY (the escape moved verbatim, same column — method rule
  (ii) working), S241 re-derived against the cell array; both DETECTED at
  `rxtsource:2fail/210pass` and `1fail/211pass`. PARKED on `lane/w1kit`;
  `make test` launched as the lane's last act, log path in the report.

- `w2b_report.md` — [REVW.2] WAVE 2 SLICE C, EP2 step 11 / lens 10 STAGE 3
  (2026-09-18, lane w2b, opus): the FRAGMENT RETIREMENT. `sb_fragf` /
  `sb_fragfv` landed in `src/core/sb.c` with a unit check, each emitter given
  a three-line adapter (`vm_rolef` rebuilt on it, `dfa_fragf` new), and the
  fixed scratch buffers retired across BOTH emitters in eight batches —
  **81 declarators inherited, 75 retired, 6 left on a named exclusion list**.
  Every batch byte-neutral on three independent artifact streams against a
  pinned branch-point binary (3,938-row corpus argv sweep at three argv
  shapes, 304-file composition sweep, `run_ir_listing.sh`), zero movers
  anywhere. Read it for five things.
  **§2 is the exclusion list and its reason is structural**: one standing
  scope exclusion (`Vm.up`, lens 10's own note) plus the six-buffer
  ENCODING-SEAM GUARD/ADVANCE family, whose text carries the caller's indent
  and the backend's expression and **never the `-p` prefix** — which is what
  puts it outside the K38 class the stage exists to retire, and what
  `limits.def:360` already said.
  **§3.1 measured `vm_rolef`'s truncation removal BEFORE taking it**: the
  charter names it as the one fragment builder that truncates, so removing
  the truncation could have moved a byte; a probe over the whole corpus at
  both prefixes found 7,876 compiles each, **0 truncating calls, longest role
  135 bytes against the 160 bound**.
  **§4.3 is the anchor finding.** The charter predicted 4 directly-broken
  rows by name and all four broke — but SIX did. The two it missed share a
  shape its own rule cannot see: it counted rows quoting an `snprintf` or a
  `char NAME[…]` declaration, while `S37` quotes an ARGUMENT LINE of such a
  call and `S53` quotes the CONSUMER that passes the buffer VARIABLE. *A
  buffer's blast radius is not the lines that mention the buffer; it is the
  whole statement that writes it, every continuation line of that statement,
  and every call that reads the variable.* §4.2 carries the two re-aims that
  needed thought rather than substitution — `S37`'s one anchor matches TWO
  emission paths only because it carries the shallower arm's indent, and
  `S53`'s AFTER had to change too.
  **§5.3 is a check's own blind spot, measured**: `sb_fragf`'s no-truncation
  promise is enforced by the `vsnprintf` SIZE argument and the exactness of
  the ALLOCATION is unobservable — an allocation one byte short moves neither
  `tests/core/sb_fragf_check.c` nor AddressSanitizer, because `arena_alloc`
  rounds to 16 and zeroes and ASan sees only the arena's own block `malloc`.
  And **§5.2 is what the stage's own item 0 bought immediately**: widening
  `run_ir_listing.sh` from 11 patterns to 16 with per-row `--features` (reach
  30 → 42 of 44 `vm_rolef` sites) found TWO defects in a pre-existing check
  the old eleven could not reach — an extraction counting `RX_CALL` return
  addresses as resume points, and an EQUALITY assertion where the cap's
  soundness is only an INEQUALITY.

- `w2x_report.md` — [REVW.2] WAVE 2 SLICE D, EP2 step 10 / lens 1 X8
  (2026-09-18, lane w2x, opus): THE STAMP PAIR. `sb_stampf`/`sb_stampwf`/
  `sb_stamp_str` and `sb_upper` in `src/core/sb.c`, with **57 of the 73 stamp
  sites converted across BOTH emitters, `Vm.up` RETIRED and the fragment
  census down to 6** — every batch byte-identical on four streams, so not an
  `abi` event. Read §0 first: **EP2's "52 sites" is 52 LINES over 44
  STATEMENTS**, of which only 37 are value stamps; the other 15 lines are
  seven multi-line function-like MACRO bodies whose emitted text is a program
  and which no stamp helper can take. Three readers confirmed the count and
  none decomposed it — *a census counting the right thing can still count a
  different UNIT than the work item citing it* — and the same conflation
  explains EP2's "4 abutting" anchors, which are really THREE rows stacked on
  ONE line (the four rows genuinely inside the span sit on the macro
  statements).
  Also worth reading for four things. **Lens 1's typed `emit_stamp_int`/
  `_bool` cannot be built byte-neutrally**: one file's 37 value stamps use
  seven integer spellings (`%lluULL`, `0x%xu`, `%lldLL`, …) plus six raw C
  expressions, and those are C TOKENS the artifact's own compiler reads, not
  renderings of a number — so the value is a FORMAT and the NAME is the
  literal a grep enumerates. **`Vm.up` was never the stamp helper's to
  retire** (w2b is right) **but it is `sb_upper`'s**, at three lines and zero
  reader changes across its 100 readers: lens 10 and w2b both treat retiring
  it as inseparable from a 110-site data-flow change, and moving its STORAGE
  is not that change. **§5 records an instrument defect worth inheriting**:
  `--emit-ir` at the DEFAULT engine refuses on every DFA-winning pattern, so
  the first build of the byte-identity sweep reached 1,754 of 3,938 rows and
  read perfectly green — the REACH figure caught it, not the pass count.
  And **§8's plant 2** — `%-*s` written `%*s` leaves the unpadded sub-check
  GREEN, because at width 0 the two spellings are identical, so 30 of the 37
  call sites could not have caught it and neither could a sweep built from
  the shipped population's two widths.

- `capsurvey_report.md` — **capsurvey** (2026-09-22, opus; docs-only,
  nothing under `src/`/`tests/`/`docs/spec/`, no timing, pcrec-bench
  read-only). Delivers `docs/dev/optloop/captures_via_dfa_survey.md` plus
  its census and 27 `REFERENCES.md` entries, answering Frank's *"I'd be
  interested in if anyone is capturing using dfa"*. Read it for five
  findings, of which the first reframes the brief. **F1: pcrec ALREADY
  implements the RE2/rust two-pass hybrid** — the capture-erased
  forward+reverse DFA pair hands the VM an exact anchored window and the VM
  assigns the captures, which is that design line for line — so "adopt the
  RE2 shape" is not a mechanism anyone can propose; the residual is that
  the END the DFA computes exactly is consumed only as an MRL pruning
  ceiling. **F2: and the tree has already ruled against taking that
  residual** — `emit_vm.c:12199-12213` writes out the structural
  span-equality argument and then declines it, because R21 split it into
  "erasure STRUCTURAL, span-equality BELIEVED-WITH-GATE" after K17/K18; a
  hard end bound would make a *believed* claim load-bearing in the
  unsound direction, so the residual is a GATE question, not a design one.
  **F3: the census's first cut was the wrong cut.** `RX_ENGINE` ×
  `RX_VM_PREFILTER` reads "26 hybrid"; adding `RX_ENGINE_WHY` shows 26
  patterns are VM *because of a capture group* and only 17 of those are on
  the hybrid, while 10 of the 27 hybrid rows carry `RX_NCAPS 1` and assign
  no groups at all — and those same 10 are exactly the rows where `mrl_win`
  is false, so captures and an exact end coincide on this population and
  nothing makes them coincide in general. Of the 9 capture-forced rows with
  no prefilter, **7 are patterns no DFA can express**, leaving the hybrid's
  genuinely unserved population at TWO, for [OPT-4.2]'s nullable reason
  that `f2_rescue_split.md` already owns. **F5 is a citation lesson worth
  the read**: two of sixteen `file:line` cites were wrong, and neither by
  ordinary drift — one was copied from another document in this repository
  and was exactly as stale as that document with nothing marking it, and
  one was a line number read off an EMITTED ARTIFACT rather than the
  emitter, which is precise, checkable, points at the wrong file, and
  survives a "does this line exist" check (reading the real site then
  showed there are TWO prune macros, not one). Ranking delivered:
  **one-pass DFA first** (the only construction in the survey that gives
  leftmost-first captures from a DFA, and `rx_match_anchored` is already
  the anchored capture-assigning call it would replace), (a)'s residual
  second, **TDFA a recorded deferral** (it replaces determinization AND
  minimization, and its published disambiguation policies are
  leftmost-greedy or POSIX — neither is PCRE preference; re-open condition
  named as a fragment-level tagged machine, which `APPROACH.md` §2 tier 3
  already calls "a later upgrade"). Nothing owed.

- `c2design_report.md` — **cycle-2 DESIGN NOTES** (2026-09-22, lane
  `c2design`, opus; docs-only, nothing under `src/`/`cli`/`lib/`/`tests/`/
  `docs/spec/`, pcrec-bench read-only, no timing). Delivers
  `docs/design/reqbyte_freq_pick.md` (**BUILD**: `[OPT-REQBYTE]`'s pick by
  argmin over a byte-frequency prior, PCRE2's rightmost rule surviving as the
  tiebreak) and `docs/design/reqpos_2b.md` (**BUILD**: `[OPT-REQPOS]` tier 2b
  as the necessary literal RUN; tier 2 declined and not a precondition). Read
  the report for thirteen findings, headed by the one that reshapes the first
  note: **the static byte-frequency prior ALREADY SHIPS** at
  `src/opt/prefix_k.c:91` with `[OPT-OFSK]` as its consumer, a sum check, and
  a header naming D83's findings file as the replacement for that one
  function — so the pick is a second CALL, not an interface, and it already
  delivers all three of `reqpos_census.md` §5's whole-call wins with no
  findings file (11 of 12 `capability` movers go to a strictly rarer byte in
  the bench's own subject, 0 to a commoner one). Also: `firstset_design.md`
  §5.2's proposed `double pcrec_findings_density` is refuted by
  `prefix_k.c`'s own stated integer rule; the census's "three whole-call
  answers" counts two rows pcrec already WINS, so the pick's honest D119
  improve population is 0.4294 weighted and not 1.4617; tier 2b reads no
  offset from the match start at all; 2b's decline rule cannot come from
  `freq`, by arithmetic (an independence product over-predicts the measured
  run gain by 5×/8×/**3,257×**); a run's gain is not a function of its length
  (the longest finite-gain run in the population, 8 bytes, has gain 1.00×);
  and constant-length `memcmp` lowers to one load + one compare at L ∈ {4,8}
  on gcc-16, which is a better emitted form than the row's own
  `memcpy`-into-`uint64` sketch and avoids `[WORD-FOLD]`'s over-read question
  entirely. Two drive-by corrections flagged and not fixed: `coding_guide.md`
  §3.1 and `src/gen/CLAUDE.md:25` both cite `src/core/limits.def` for
  `PCREC_ARTIFACT_ABI`, which lives at `src/gen/emit_dfa.c:51`; and bit 31 is
  the last bit spellable `1u << N` in the flags enum.

- `<lane>_rulings.md` — the manager's rulings to a lane, written BY FILE while the lane runs (a busy lane reads messages only when it idles; the file is polled at each stage boundary — memory `pcrec-lane-hold-lift-artifact`). GITIGNORED BY DESIGN (see .gitignore): it is live coordination, not a deliverable; the lane's report §"Rulings received" restates every ruling that shaped the delivered work, and the journal carries the manager's side. When a delivered worktree is removed, its rulings file is copied here as a LOCAL, still-ignored file (edge1, w13 on 2026-09-04; lim2's was lost with its worktree — its rulings 1-5 are in lim2_report.md §7 and 6-7 in journal parts 62-64) — these local files do NOT travel by git (memory `pcrec-two-machine-split`).

- `w3_report.md` — [REVW.3] WAVE 3 (LAYERING) (2026-09-19, lane w3, opus):
  the dump tier to `src/dump/`, `src/gen/enc/` to `src/enc/`, the layer
  model in tool and prose, the rxt minimal cut, and `internal.h`'s
  declaration tail grouped by defining layer. Five item commits, every one
  byte-neutral on all four `scripts/emit_sweep.py` streams at full reach
  (3,938 argv rows x 3 shapes + 96 composition artifacts, 0 movers / 0
  asymmetric everywhere), NOT an `abi` event, no `docs/spec/` hunk owed,
  nothing owed at hand-off.
  Read §0 first — three things, of which two are refutations of the
  charter's own pricing. **The call-level back-edge census is 30, not the
  19 lens 6 §2.3 predicted**: filing `core/compile.c` in a `driver` tier
  does reclassify its 20 pipeline calls as forward edges, and it CREATES
  22 new ones pointing the other way, every one of them `ctx_fail` or
  `ctx_nomem` — *the file is itself two layers, the exact shape lens 6
  diagnosed one level up for the directory*. The item-1 dump move
  accounts for the whole 39 -> 28 drop on its own (the two L4 rows), and
  §2 separates the three numbers cleanly. **Lens 6 priced that same move
  at "0 anchors" and said in the same section that it had not run its own
  coupling grep**; run here it is two sabotage rows and 62 live citations.
  And **one check needed a fix rather than a substitution**:
  `run_cpset_structure.sh`'s CHECK 1R greps a HISTORICAL tree, so
  re-spelling its `enc.h` path would have kept the required red while
  silently changing its cause from "the field is absent" to "the file is
  absent" — *a relocation can convert a check's red into a different
  claim with nothing failing.*
  Also worth reading: §1's item-4 note on why the rxt cut costs one more
  edited file than lens 6's "2 files" (renaming `compile_driver` would
  stale ~30 comments including four `--list-axes` strings a caller reads,
  and exporting it unprefixed is lens 9's P5 hazard, so the static driver
  keeps its name behind a `pcrec_`-prefixed face); §1's item-5 note that
  the guide's own `-Wcomment` rule, read that morning, still cost a build
  (`src/core/*.c` inside a C comment); §3 on being
  `scripts/emit_sweep.py`'s first customer (it needed no change; the
  REACH figure, not the pass count, is what makes a zero-mover result
  evidence); §5 flagging the `APPROACH.md` §8 rewrite for Frank; and §6,
  headed by **wave 4's brief must cite `src/dump/axes_dump.c`**.

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
- `k57fix_report.md` — [K57] FIXED (2026-09-15, lane k57fix, sonnet): a
  `|` block scalar's dedent strip was a byte count, so a continuation
  line indented less than the block's own dedent depth had content
  silently deleted; now a REFUSAL by name, class `value-shape`, in all
  three legs (`src/parse/rxt_source.c`'s `read_prose_region`, `run.sh`'s
  `prose_take`, `verify_rxt.py`'s prose-region arm). Worth reading for
  the leg-B finding: a streaming per-line reader cannot just clear
  `prose_open` on the first refusal, because the region's remaining
  lines then fall through to the top-level dispatch and raise a SECOND,
  unrelated `structure-attachment` failure that `extract_class`'s
  last-bracket read reports instead of the real one — found live on the
  new three-leg fixture (`prose_dedent_body.rxtin`), fixed with a
  per-region latch (`prose_bad`). `prose_dedent.rxtin` is unchanged in
  content and inverted in assertion, exactly as r59-R4 predicted.
  `docs/spec/rxt_format.md`'s S3 section gains the dedent-decode rule it
  never stated (only the region's extent, before this). PARKED on
  `lane/k57fix`, not merged — the box was under BOILERPLATE's
  one-heavy-suite rule (lane dialsweep) for the lane's whole working
  period, so only rxtsource + strict ran; full `make test` is owed to
  the manager at the next merge battery.

- `dialdesign_report.md` — [OPT-DIAL] STEP 1, THE DESIGN (2026-09-16, lane
  dialdesign, opus; design only, nothing under `src/`/`tests/`/`docs/spec/`).
  Delivers `docs/design/opt_dial_design.md` and REVISION 2 of
  `docs/design/opt_dial_inventory.md`. Read §1 first — three findings, each
  of which a D6 panel should attack.
  **§1.1: the FIRST SIZE NOTCH IS EMPTY and no threshold fixes it.** Among
  the axes whose denial SAVES bytes, the measured penalties jump from
  1.00× straight to 1.794× — so every tier-one bound below 1.794 makes
  notch `−1` identical to the middle on every discrete row, and the first
  bound that does anything makes it identical to `−2` instead. The λ row
  reaches the same conclusion by an independent route (its ops cap admits
  nothing between the middle's 108 probe ops and the frontier's next point
  at 175), which the report flags as a confirmation with the caveat that
  one set is all the λ evidence there is.
  **§1.2: the FOUR-UNITS problem collapsed to ONE unknown.** Frank's
  threshold rule is stated in one unit and the inventory's rows carry
  penalties in four; the note fixes the unit as the whole-match multiplier
  and converts a COMPONENT row exactly as `1 + φ(m−1)`, which turns a
  guessed threshold into a falsifiable sentence — *`-fno-tiered-entry`
  belongs in the min-size column iff per-call entry cost is at most 24.6%
  of match time.* The report records the near-miss: an earlier draft
  invented a second "regime" with a guessed cross-regime factor, produced
  the identical table, and hid the unknown inside the guess.
  **§1.3: λ and the discrete table are NOT consistent at the extreme, and
  the reason is structural.** The consistency test is a ratio test
  checkable TODAY without the calibration constant (`ρ/σ` constant across
  positions), and it fails at `−2` — because `x₂` is a hard SAFETY CAP
  while λ=0 is a pure objective with no safety term, a shape difference no
  choice of λ repairs. The repair gives the DP the same cap
  (`ops ≤ x₂ · ops(middle)`), which `\p{L}` passes at 1.91× against 2.00×
  — and the report declines to treat that near-agreement with
  `-fno-anchored-dfa`'s own 1.99-against-2.00 as corroboration, since the
  two share no mechanism.
  §2 is what REVISION 2 found wrong in STEP 0, **none of it because a
  number moved**: the draft policy table violates STEP 0's own allowlist
  rule in STEP 0's own document (the rule in §6, the table in §3, nothing
  tying them — `learnings.md` §3's shape one document earlier in the
  pipeline); the dial's flagship `--vm-entry-shape` row has its two axes
  measured on two DIFFERENT PAIRS of rungs and the rung the default selects
  has no measured run time at all; and two axes had landed in `tuning.md`
  since STEP 0 and were never inventoried, one of which
  (`-fno-startpos-guard`) is the one axis in that document that is not
  answer-identity-preserving and so introduces a bucket STEP 0 lacked.
  §3 carries five findings the brief did not anticipate, headed by
  `-fno-anchored-dfa`'s min-size cell being admissible only as a
  DEPENDENCY on `[K53-SELRETRY]`'s drop ladder, and by the K45 check the
  dial needs being one the axes sweep structurally cannot be (the refusing
  SET compared as keys, never as a count, because this design's two
  refusal hazards run in opposite directions and a count would let both
  slip through at once). §4 is the method note on where the percentages
  came from and which denominator the threshold rule uses; §6 is the
  seven-item Frank queue. `make strict` GREEN; nothing owed.
- `dialimpl_report.md` — [OPT-DIAL] THE IMPLEMENTATION (2026-09-16/17, lane
  dialimpl, opus): `--tune=N` and its five aliases, the pinned policy table
  (`src/core/tune.c`), the `tune` config directive with D93's file-wins
  precedence, the `<PREFIX>_TUNE` stamp, abi 25 -> 26, six checks, three
  sabotage rows and the D80 spec delta. **Read §1 first: the RATIFIED `−2`
  cell violates the design's own eligibility gate, and the check the design
  chartered found it on its first run.** `--tune=min-size` COMPILES
  `[^\p{C}\p{M}\p{P}]`, which the other four positions refuse at
  `PCREC_MAX_EMIT_BYTES` — a refusal-set move, which §6.2 forbids in either
  direction. The cause is `-fno-premul-table`'s unconditional `−2` denial,
  verified independent of the dial (the bare flag does the same thing at the
  identical byte count), and the reason the table missed it is that **§3.1's
  gate 2 was asked of three rows and never of that one**: its citation argues
  `y`, `x₂` and `φ_scan`, the size and time gates, with the refusal gate
  simply absent. The general form is worth more than the cell — *any size
  lever large enough to matter can rescue a pattern the caps refuse, so gate 2
  is a question every size-side cell must be asked*. Filed as **K59** with
  three dispositions, all Frank's, rather than narrowed by the lane (k49fix's
  precedent); the corpus population is ZERO, which is exactly why the design
  bought the synthetic near-cap family and why with no F3 the hazard would
  have shipped unobserved.
  Also worth reading for four smaller findings. **The design's §5.3a manifest
  list is short by two** (it names ten `EMITTED_BYTES` rows; the file carries
  twelve), and **the named real witness moved +31 bytes where the design
  predicted 23-28** — its prefix is longer than `rx`, which is the design's own
  "compute the delta PER READER" instruction catching something. **A check's
  FAILURE MESSAGE is a second, undeclared claim about the space of causes**,
  found by this lane's own failing-direction validation: two arms went red
  blaming the WITNESS while the TABLE was wrong — `w23impl_report.md`'s
  generalisation met from the other side. And **the mech arm's `${f:-1}`
  default reads a MISSING suite log as DETECTED** rather than as ANOMALY,
  which is pre-existing across every arm and cost this lane one false
  DETECTED before the suite was committed.
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

- `dfam12_report.md` — [LIM-2]/dfamin M1+M2 (2026-09-16, lane dfam12,
  sonnet; measurement only). M1 (candidate C's paper-partition-rule yield)
  was already fully measured by m1part (2026-09-04); this lane adds ONE
  new population m1part's own force-includes did not cover — K25's own
  chain shapes (`a{0,N}`/`(?:abcdefghij){N}`) — and finds ZERO yield
  anywhere on it (raw_n == min_n on every row; these are strict sequential
  chains with no redundancy for any candidate to find). M2 (candidate B's
  dominance prize) was DORMANT since 2026-09-04 and is built fresh here as
  a real, measurement-only `[PROBE-M2]` edit to `src/ir/nfa.c`/`src/ir/
  dfa.c`/`src/core/internal.h` (tags each `X{m,n}` tail-loop copy's NFA
  nodes, prunes a closure's position list the instant it is built, gated
  on `getenv("PCREC_PROBE_M2")`, byte-identical by default — measured, not
  argued). Real but NARROW over the shipped corpus (14.3% of 1,232 rows
  touched, 4.0% see raw-state relief, aggregate K7 relief 4.6%), rich and
  MIXED on `tests/counterk/counterk.rxt` (raw state count roughly halves
  on some rows; K7 charge alone drops up to ~2,000x on others with raw
  count UNCHANGED — two separable wins), ZERO on K25's chain shapes for
  the same structural reason M1 finds zero there, and — the sharpest
  finding — a REGRESSION on the study's own chartering witness: the K18
  census pattern goes from a clean 27,575-state compile to a hard refusal
  under the stand-in, exactly the open-loop-context brittleness
  `dfa_online_minimization_study.md` §4.3 (B2) predicted, now measured
  concretely. Read the memo (`docs/dev/dfamin_m1m2.md`) §8 for the lane's
  own B-vs-C read: neither measurement justifies building either candidate
  now, and a real verdict on B needs the general context-aware simulation
  preorder (never built here) plus the cross-product safety corpus §4.3
  already names as a precondition. The probe is committed SEPARATELY
  (not reverted) per the OPT5M2-PROBE precedent's second option, since
  `studies/lim2_m2/`'s harness links its `extern` counters directly — see
  that directory's own CLAUDE.md for what happens to it once the manager
  drops the probe commit at merge.

- `k60meas_probe.patch` — the [K60-PROBE] measurement instrumentation from lane k60meas (the `longjmp`-value candidate fix plus its attempt/absorption counters, gated on `PCREC_K60_PROBE`/`PCREC_K60_FIX`, byte-identical and behaviour-identical when off), DROPPED at merge per the dfam12_probe_m2.patch precedent; durable copy kept so the measurement is reproducible without re-deriving it. One file (`src/core/compile.c`), nothing depends on it. Re-apply with `git am` to rebuild the harness. See `docs/dev/k60_measurement.md` §4.
- `dfam12_probe_m2.patch` — the [PROBE-M2] measurement instrumentation (gated on PCREC_PROBE_M2, no-op by default), DROPPED at merge per the OPT5M2-PROBE precedent; durable copy kept because studies/lim2_m2/ links its extern counters (that directory's CLAUDE.md explains). Re-apply it to rebuild the M2 harness.

- `mojfix_report.md` — O-31 finding F4 triage (2026-09-17, lane mojfix,
  sonnet): **NOT A PCREC DEFECT, no `src`/`tests`/`docs/spec` change.**
  pcrec compiles and matches raw high-byte (>= 0x80) pattern-text
  literals correctly on every engine/capture axis, verified both on
  darwin/arm64 (default `char` unsigned, and again forced
  `-fsigned-char`) and as a light probe against the bench's own PINNED
  binary at the exact commit (a770139e) on the real x86_64 reference
  box. The bench's own `testees/pcrec/adapter.py:2961`
  (`pattern.decode("latin-1")` feeding a Python `str` into
  `subprocess.run`'s argv) corrupts every pattern byte >= 0x80 into a
  2-byte UTF-8 sequence before pcrec ever sees it — `os.fsencode`'s
  `surrogateescape` re-encode does not invert a plain `latin-1` decode,
  only a `surrogateescape` one — confirmed by direct `/proc/self/cmdline`
  measurement and by showing pcrec answers CORRECTLY on the exact
  (corrupted) bytes it was actually handed. Read-only to pcrec-bench per
  the scope mandate; the report carries the two candidate fixes (pass
  raw `bytes` in argv directly, or decode with
  `errors="surrogateescape"`) for the manager to relay.

- `f2rescue_report.md` — O-31 F2 (2026-09-17, lane f2rescue, sonnet;
  measurement only, nothing under `src/`/`tests/`): why the captures
  axis strips pcrec's own prefilter rescue on `trim-nested-star`, and
  whether the decline boundary can narrow to "declines only when a
  capture intersects the collapsed region." See
  `docs/dev/f2_rescue_split.md` for the full memo. Headline: the ask's
  premise needed two corrections first — `trim-nested-star` (and a
  second corpus instance found here, `evil-alt-nested`) never reaches
  the count-collapse rung at all (no counted `{m,n}` to collapse), so
  what fires is the collapse-AGNOSTIC default decline, not the
  rung-scoped one the ask names; and `winpath-near-miss` has zero
  capturing groups and is not in this population at all (its ledger row
  is the unrelated `auto`-vs-forced-`--engine=vm` comparison). Both
  declines derive from one local with **no capture conjunct** — captures
  matter only as one of several routes that force VM selection,
  independent of nullability. A constructed witness family shows the
  rung-scoped decline is STRUCTURALLY UNREACHABLE whenever captures are
  present (confirmed corpus-wide: 56+2 DEFAULT-decline hits, zero
  rung-form hits, across the shipped corpus and the bench's capability
  set). Verdict: the boundary cannot narrow by capture location at
  all — it is correctly testing GLOBAL emptiness-admission, which has no
  relationship to where a capture sits (demonstrated with a disjoint-
  capture witness that would wrongly build a lossy prefilter under the
  proposed narrowing). Recommends two design-event alternatives instead
  (a partial-admission prefilter; a VM step budget, the same lever O-31
  finding 3 already asks for), neither built here.
- `mechfix_report.md` — the mech arm missing-log default (2026-09-17, lane
  mechfix, sonnet): every suite arm's `[ "${f:-1}" -gt 0 ]` scored a
  MISSING/unscrapeable suite log as f=1 → a false DETECTED (S249's first
  run is the incident, flagged by dialimpl as pre-existing across all
  arms). Fixed at ONE general site — `score_arm`, the single place a
  scraped count becomes a verdict bit, all 52 sites routed through it
  (50 uniform + framebuffer/registry variants) — rendering
  `NAME:NO-LOG(<file>)` or the documented `ERRfail/?pass` cell and
  scoring `any_unmeasured` → ANOMALY (S155's vocabulary, outranked by a
  real `any_fail`), never a synthesized count in either direction. Read
  the report for the failing-direction transcript (the false DETECTED
  reproduced pre-fix on a temp tree, both anomaly variants shown
  post-fix), the healthy-path A/B (pre-fix vs post-fix driver
  byte-identical counts at the same HEAD), and the finding that S249's
  recorded `8fail/9pass` had already drifted to `11fail/9pass` under the
  k59rung merge — through both drivers, so the drift is the tree's, not
  the scorer's. PARKED on `lane/mechfix`; full `make mech` owed to the
  nightly checkpoint.

- `f3search_report.md`, `f3search_driver.c` — O-31 finding 3 ROUND 2
  (2026-09-17, lane f3search, sonnet; measurement only, nothing under
  `src/`/`tests/`): the bench's refutation of round 1 (`b"a"*17+b"!"`,
  all three captures arms >60 s, "first iteration never returning")
  answered with verdict **(a)** — the step budget is initialized ONCE
  per `<prefix>_search` call, shared across the per-startpos attempts,
  STEPS propagates out immediately, the reset does not refill, and the
  only re-arm (the deep tier) is FRAMES-gated. One call on the exact
  subject: 2.5-2.8 s typed `PCREC_ERR_STEPS` at both the tip and the
  bench's pin `a770139e`, all three arms; n=17 is exactly the first n
  where the budget fires (n=16 completes nomatch under budget). The
  >60 s is the BENCH's regime: `PROBE_ITERS["search_short"]=200`
  batches the subject 200×, each iteration legally re-pays the
  per-call budget (D51's own ~10 s-per-call envelope, pcre2's
  per-match-call shape too), and the 60 s alarm fires around iteration
  8 — the first iteration RETURNS at 2.73 s, measured with the bench
  driver's own loop shape. Recommends a bench-side fix only (break the
  batch on a first-iteration give-up; wall-cap the probe). The driver
  is the committed reproduction piece (encseam §3.1 shape + the bench
  batch loop).

- `codeguide_report.md` — THE WIRED CODING GUIDE (2026-09-17, lane
  codeguide, opus; docs only): delivers `docs/dev/coding_guide.md` (271
  lines) plus its three wiring edits — a root-CLAUDE.md situation-index
  row, a `BOILERPLATE.md` rule for code-writing lanes, and the
  `docs/dev/CLAUDE.md` entry — distilling the 2026-09-17 twelve-lens code
  review into rules a session writing C follows. Read the report for its
  CITATION VERIFICATION table (all eleven `file:line` cites opened on the
  lane's own tree rather than copied from a report; one corrected) and for
  three findings: the guide states the CURRENT `abi` value deliberately,
  accepting a known drift point the D76/D94 grep sweep will find, because
  a writer needs to know what to grep for; TWO of the review's rules have
  no home in the tree's own comments and this guide is now their only one
  (EP2's finding that no byte-identity gate reads the `--emit-ir` listing,
  and `replace.py`'s whole-file/line-agnostic anchor matching, which makes
  verbatim relocation free and RE-INDENTATION the thing that breaks an
  anchor); and the charter's comment-escape rule is narrower than the
  incident that produced it — lane `cmtfix` found TWO hazards, `*/` and
  `/*` (gcc `-Wcomment` under the harness's own `-Werror` `GENCFLAGS`),
  the second reachable with no `*/` anywhere in the file, so the guide
  states both.

- `fixnow_report.md` — [REVW.FIX] the code review's FIX-NOW pile landed
  (2026-09-17, lane fixnow, sonnet), ten commits in the synthesis's own
  order per `docs/dev/reviews/2026-09-17-code-review.md` §1: the
  `Job.scr_test`/`scr_desc` Ctx back-pointer (L8-F1, a live caller-abort
  on OOM); `san_scripts.txt` gains the cpset/mrl unit checks (L5-R0.2);
  the `lib/pcrec.h` header sweep (L9-P2/P7/P8 — the stale "utf8 not yet
  implemented" claim, `<PREFIX>_NCAPS` genericized, a false "order of
  magnitude" deleted); the `cli_parse`/`apply_target` libdirs leak plus
  `write_file`/stdout `ferror()` coverage (L8-F2/F5, discharging
  L10-L10-8); the FNV-1a helper pair (L3-F3, 9 sites deduped,
  byte-preserving); the "missing closing ) for group" `#define`
  (L3-F5, 8 sites + the registry_check.c ninth home, plus a stale
  check fix found while validating); headers for the 43 headerless
  ≥50-line functions plus the misplaced `emit_attempt` banner
  (L4-C1/C2 — read the report for the population re-derivation: the
  census tool's own `start_line` drifts on 7 of 76 rows, corrected by
  grep rather than trusted); `match_api.md` §8.0's worked example gains
  `-Wl,-dead_strip` (L6 §5.1); `select_engine.c:496`'s superseded claim
  corrected in place (L4-A2); and the pilot, `cg_walk`/`pr_walk` merged
  into `pcrec_ast_visit` (L1-X2, with both sabotage rows re-aimed and
  re-verified DETECTED at their exact pre-merge figures). Comment-only
  or byte-preserving throughout; `make strict` clean after every item.
  PARKED on `lane/fixnow`, not merged — `make test` was launched
  backgrounded as the lane's last act per BOILERPLATE and is OWED at
  hand-off (`build/fixnow_test.log` in the worktree); a bonus
  `tests/recursion/run_recursion_diff.sh` run (beyond the brief's
  stated bar, the most direct exercise of item 10's `callgraph.c` call
  sites) is also OWED, log path in the report.

- `waveu_report.md` — [REVW.U] WAVE U, the code review's NETS wave
  (2026-09-17, lane waveu, sonnet). Four deliverables, one commit each.
  L5-R0: `tests/lib/unit_cc.sh`'s `unit_build`, the one way an
  internal-property check is compiled, adopted in place at the seven
  pre-existing checks that link only `libpcrec.a` (a real
  `-Wmissing-field-initializers` gap found and fixed at
  `definitions_check.c` along the way). L5-R2: `tests/core/
  sat_arith_check.c`, the saturating-arithmetic agreement between
  `mrl_sat_add`/`vm_fadd`/`cg_sat_add` and their `_mul` siblings — the
  six functions dropped `static` (declared in `core/internal.h`, no
  `abi` event, never emitted text) — sabotage S254, the mech arm `core`.
  L5-R1: the ALLOCATION-FAILURE INJECTOR (`tests/core/alloc_inject.h` +
  `alloc_check.c`, opt-in `make alloc`, zero `src/`/`cli`/`lib` edits).
  **Confirms L8-F1 (fix-now #1, `23eb3d34`) in both directions**: built
  at that commit's parent, the `--engine=vm` witness `[a-z]{2,10}`
  reproduces SIGABRT live (`sb_grow`'s unattached-buffer `abort()`);
  on the current tree, cleanly diagnosed. **And found K60
  (`docs/dev/known_issues.md`, filed not fixed) on its first real
  run**: two other witnesses show `pcrec_compile` succeeding despite a
  forced allocation failure at a real rate (21%/8%) — a stale
  per-attempt retry-eligibility flag (`cx.size_cap_refused`/
  `dfa_overflowed`, never reset across `compile_driver`'s retry
  attempts) and the size-term ladder's own documented "any reason, this
  K is out" catch-all both silently absorb a genuine OOM into a
  successful compile from a later internal attempt — invisible to every
  answer-level check and to `ulimit -v`, which cannot steer to a
  non-final attempt. Three dispositions filed, none taken (K59's own
  precedent). L8-F6: a grep-derived allocation-site FILE-SET census
  (Section 0, `tests/resource/run_resource_tests.sh`) replacing a stale
  six-file hand list (found: two files had gained raw allocations
  unnoticed); a darwin-viable positive control (Section 2b, the
  injector, unconditional on both platforms — Section 2's `ulimit -v`
  approach has been the discipline's only control since [M4.7b] and has
  been skipped on this dev box since the 2026-09-04 Mac move, exactly
  the window F1 shipped in); three sabotage rows (S255/S256/S257, the
  discipline's first — zero before this wave), mech arm `resource`.
  Also fixes a real pipeline-exit-status bug (`"$BIN" | tee` reads
  `tee`'s exit code, never `$BIN`'s) found live when `make alloc`
  reported success despite visible `FAIL:` lines — `${PIPESTATUS[0]}`,
  the `run_registry_tests.sh` precedent, in both new scripts and in
  `run_core_tests.sh`. PARKED on `lane/waveu`, not merged — `make
  test` launched backgrounded as the lane's last act per BOILERPLATE,
  OWED at hand-off (log path in the report).

- `w1stage0_report.md` — [REVW.1] wave 1 stage 0 (2026-09-17/18, lane
  w1stage0, sonnet): the emission-kit wave's PRECONDITION stage, three
  deliverables, nothing under `src/`/`cli`/`lib/` touched. (1) The
  long-prefix full-corpus sweep (`tests/codegen/run_longprefix_sweep.sh`),
  repairing lens10_emission_kit_charter.md's [MECH-REACH] finding (the
  tree's only prior long-prefix control compiles the pattern `a`): 1,499
  of 1,500 `-p rx`-compiling corpus patterns also compile at the legal
  60-byte prefix boundary, zero gcc `-Werror` anomalies — no live K38
  recurrence found; committed baseline
  `docs/dev/w1stage0_evidence/longprefix_baseline.tsv`. (2) The `irsb`
  byte-neutrality arm (EP2's addition): a new block in
  `tests/codegen/run_ir_listing.sh` pinning the `--emit-ir` listing's raw
  bytes per pattern against a committed baseline — the stream none of the
  four standing `.c`-identity gates compare; pins the OUTPUT bytes, not
  the render mechanism (D108); sabotage S258 verified DETECTED (and
  UNDETECTED against the pre-arm commit, mech's own `git archive HEAD`
  shape). (3) The listing-reach census (EP2's addition): measures whether
  `run_ir_listing.sh`'s population reaches the rung emitters whose role
  text IS the listing — 27 of 41 `vm_rolef` call sites (66%) for the
  11-pattern fixture, 31 of 41 (76%) for the whole corpus at default
  engine selection, both missing lookbehind and subroutine-call emission
  entirely; recorded as a finding for a future stage-3 lane's population
  choice, not acted on here. See `docs/dev/w1stage0.md` for the full
  memo. PARKED on `lane/w1stage0`, not merged — full `make test` launched
  backgrounded as the lane's last act per BOILERPLATE, OWED at hand-off
  (log path in the report).
- `btriage2_20260918_report.md` — triage of `battery_20260918_051433`'s
  `test`-stage red (2026-09-18, lane btriage2, sonnet; the manager's
  battery on ubuntubudu pinned at 272bf970, the fix-now pile + wave U).
  Date-qualified for the same reason `btriage_20260917_report.md` is — an
  earlier, unrelated `btriage2` lane (2026-09-10) is on record under the
  plain name. **Verdict: the 272bf970 pin holds** — the entire red is ONE
  failure, a stale test-side witness with insufficient CPU-budget margin,
  not a defect in the fix-now pile or wave U. `tests/resource/
  run_resource_tests.sh`'s Section 1b `size_moved` loop shares Section
  1's `K7_CPU` (45s) budget; its row 1 witness
  (`(?:[a-z][0-9]){1,13000}`) measures 25.17s user CPU on the dev box —
  under 1.8x margin, well short of K7_CPU's own ~3x calibration
  convention — because its refusal path pays for TWO minimizations
  ([K59-PREMUL]'s drop ladder retries once before the final refusal;
  measured against the SAME pattern under `--max-emit-bytes=9000000`,
  which never retries, at 12.58s). ubuntubudu is a materially slower
  single core (AMD Ryzen 5 1600) than the Mac dev box that calibrated
  K7_CPU (Apple M1 Max), which is what turned an already-thin Mac margin
  into a real Linux CPU-budget miss — the battery's own trailer shows a
  near-idle box (load average 0.52 on 12 threads) at the time, ruling out
  contention. Also traced and ruled out: the three fix-now-pile commits
  since `cf0962e3` touching adjacent files (`66363dcd` header comments
  only, `5886e315` a byte-preserving FNV-1a helper refactor at `-O2`,
  `23eb3d34` an unrelated `Ctx` back-pointer attach) — none plausibly
  changes DFA-minimization cost, and row 2 of the same loop (measured
  11.27s here) shows no comparable slowdown. Fix: a new `SIZECAP_CPU`
  (default 90s) watchdog CPU budget scoped to Section 1b's two
  `watchdog` calls only — Section 1's own `K7_CPU` is untouched since
  that section's resource-ceiling IS the feature under test there.
  Re-validated locally: `bash tests/resource/run_resource_tests.sh`
  27/0/0 (1 platform-expected skip), `make strict CC=gcc-16` clean.
  `tests/resource/CLAUDE.md` updated (documents Section 1b, which the
  file's own section list had been missing since wave U added Section 0
  — a separate pre-existing staleness fixed in passing). PARKED on
  `lane/btriage2`, not merged — the manager's battery was still running
  its axes/san/lint/mech stages at hand-off.
- `santriage3_report.md` — TRIAGE of `battery_20260918_051433`'s `san`-
  stage red on ubuntubudu (2026-09-18, lane santriage3, sonnet; read-only
  log triage, fix built and validated LOCALLY on this Mac per K54 — no
  ubuntubudu run). **Verdict: the `272bf970` pin holds, does not slip.**
  `run_san_group: 37/38 scripts passed` — the sole failure is
  `tests/codegen/run_cpset_structure.sh` CHECK 4 (the interval-algebra
  model check), and it is class (ii): `main()` in
  `tests/codegen/cpset_model_check.c` never called `arena_free(&cx.arena)`
  despite every real `src/` path doing so at every exit — a pre-existing
  gap in a `tests/` unit-check program, unmasked for the first time now
  that wave U's `unit_build` threads `$SANFLAGS` into this file's compile
  ([REVW.U L5-R0.1]) AND LeakSanitizer is genuinely LIVE on ubuntubudu
  today (confirmed by this very report — K26's 2026-08-18 no-op finding
  no longer holds there). The shell's own FAIL label is misleading: the
  algebra never disagreed (`bad == 0`, "PASS" printed) — LSan's atexit
  leak report overrides the exit code the shell reads. Fixed with one
  line (`arena_free(&cx.arena);` before `return bad;`); local validation
  (plain build PASS/rc=0; the exact `SAN_CFLAGS` build with
  `detect_leaks=0`, this box's own K54-driven Darwin posture, PASS/rc=0;
  the WHOLE `run_cpset_structure.sh` script post-fix, 28/28 checks) —
  `detect_leaks=1` itself was never run locally, per K54's documented
  hang, so the literal "LSan no longer reports" is confirmed by code
  review (the only allocation site is the arena `arena_free` now walks
  and frees) rather than by a local repro; owed to the next ubuntubudu
  run. Also corrects the brief's own premise: `run_alloc_tests.sh` is
  NOT in `san_scripts.txt` at all (its own separate opt-in `make alloc`
  target) — wave U/L5-R0.2 added three manifest entries, not four, and
  `run_mrl_tests.sh`/`run_core_tests.sh` are both independently clean in
  this log. No manifest change made or needed. Branch `lane/santriage3`
  (`ddcc8c20`), PARKED, not merged.
- `k60meas_report.md` — K60 THE MEASUREMENT (2026-09-18, lane k60meas,
  opus; measurement only, K60 NOT fixed). The memo is
  `docs/dev/k60_measurement.md`; this report carries the commit list (with
  the `[K60-PROBE]` `src/core/compile.c` commit marked DROP AT MERGE, the
  `dfam12_probe_m2.patch` precedent) and four findings the brief did not
  anticipate. **The sharpest is that a defect entry's own diagnosis and its
  own repro came from different places and only the repro was checked**:
  K60 names a never-reset `cx.size_cap_refused` as its ONE CONFIRMED
  mechanism, and the `Ctx` is a loop-local `memset` at the top of every
  attempt — three lines of `compile.c` refute it, and zero of 148 measured
  absorptions involve a stale flag. **Second: a mechanism named in a defect
  entry and reached by NONE of that entry's witnesses is a mechanism nobody
  has measured** — the `[ART-SIZE]` ladder catch is excluded from W1/W3 by
  `fit.chosen == ENGM_VM` and from W2 by the `emit_code` threshold, and
  adding one witness (W4, a real corpus pattern) moved its measured rate to
  68.4%, the worst in the file, while the entry filed it as the SECONDARY
  explanation of a witness that cannot reach it. **Third, an instrument
  finding**: extending the injector's ABI produced 60 "killed by signal 11"
  trials that were entirely a stale `build-alloc/` tree — `alloc_inject.h`
  is `-include`d and cannot be a Makefile prerequisite, and the four
  injector functions cross a link boundary with no shared prototype, so a
  stale one-argument call against a four-argument definition is a wild
  pointer and a SIGSEGV *inside the injector*, indistinguishable from the
  abort/signal outcome the check detects; fixed by renaming the symbols
  with the signature change, so a stale object fails to LINK. **Fourth**:
  the lane walked into this house's recorded `-o`-basename trap on its own
  byte-identity sweep (`identical=0 differing=1158` on a comment-only
  probe), the fourth recorded instance — the durable fix is a shared
  fixture and this lane did not build one.

- `mtriage_report.md` — TRIAGE of the manager's killed `make test` at main
  `f6474777` (2026-09-18, lane mtriage, sonnet; log-reading + one targeted
  fix, no other `make`/`mech`/`san` runs before the closing full `make
  test`). Two FAILs and a `rc=124` timeout dispositioned. **The `[census]`
  FAIL was real and the check did its job**: `[D105]`'s own commit
  (`6e14d210`) deleted all five raw `malloc`s from `src/gen/emit_dfa.c`
  (`emit_state_legend`'s restructuring onto the arena), so the
  raw-allocation file-set census in `tests/resource/
  run_resource_tests.sh` correctly went red — a delivery-bar miss (d105
  moved the population its own change measures and did not re-pin it),
  re-pinned here to 9 files. `nm could not read arm_a.o` is the
  already-documented standing darwin red (`docs/dev/wake.md`), reproduced
  independently by both merged lanes at their own branch points — no fix.
  **The timeout is itself a finding, not an anomaly**: 30 of 40
  `TEST_SECTIONS` completed (28 green, the 2 above), one was mid-run at
  the kill, 9 never started; `docs/dev/tt4m_time.md`'s only recorded
  darwin serial baseline (5124.29s/~85.4 min, measured 2026-09-12/13) was
  taken against a 38-section suite, and `TEST_SECTIONS` has grown to 40
  since — so the manager's 5400s/90-min bound left ~zero margin over an
  already-stale baseline, with no concurrent-load confound (d105's own
  heavy corpus run had finished and been reported ~16 minutes before the
  manager's run launched). `bash tests/resource/run_resource_tests.sh`
  GREEN (27/0/0, 1 expected darwin skip) after the re-pin; `make strict`
  clean. PARKED on `lane/mtriage`; full `make test` launched backgrounded
  as the lane's last act per BOILERPLATE, OWED at hand-off (log path in
  the report).
- `d105_report.md` — [D105] (2026-09-18, lane d105, opus): `emit_state_legend`'s
  silent-degradation path DELETED, built as Frank re-ruled it — `path` becomes
  a fixed `LEGEND_MAX_EXAMPLE`-int local and its unbounded allocation goes, the
  four BFS arrays move to the compile's arena so refusal rides the existing
  `ctx_nomem` mechanism, and brief mode allocates neither `from` nor `via`.
  K60's LEGEND class (40 of 148 absorptions) closed: `make alloc` reads W1
  15 → 0 and W3 25 → 0 in both sweeps; W4's 108 is the disjoint ladder class
  and is untouched. Read it for four things. **§3.2's REACH census is the
  methodological point**: byte identity over artifacts that contain no legend
  proves nothing, so the second full-corpus arm counts them — 3,024 of 3,517
  compared artifacts carry one, with all three arms of the rewritten function
  represented, against zero movers in either arm (3,938 corpus pattern lines,
  1,500 compared at default axes and 3,517 at `--features all`). **§2 is a
  check-design result that arrived sideways**: the per-witness POPULATION pin
  was added for K35's reason and turned out to be the ONLY arm that fails on
  W3's sustained sweep against the unrepaired library, because that sweep
  absorbs zero even with the defect present — the absorption pin alone reads
  PASS there. **§5.2 declines sabotage row S260 with its mechanism**: a plant
  reverting the function to raw `malloc` with a silent return is undetectable
  by any arm `make mech` runs, because the `resource` arm's section 2b greps
  only for `KILLED THE PROCESS BY SIGNAL` and a silent absorption produces
  none — the trigger for building the row (K60's ladder class landing, so
  section 2b can assert the pins without taxing `make test`) is named instead.
  And **§1.2 is a defect found while validating**: `run_alloc_tests.sh` counted
  `^FAIL` out of a stdout-only log while `alloc_check` writes FAIL to stderr,
  so every red run reported "0 witness(es) misbehaved".

- `allocpins_report.md` — [ALLOC-PINS] (2026-09-18, lane allocpins, sonnet):
  D110, the ruling this lane implements — `tests/core/alloc_check.c`'s
  per-witness population expectations become FLOORS (half the measured
  population: W1 57→28, W2 11→5, W3 303→151, W4 162→81) rather than
  equality pins, `expect_absorbed_*` staying exact since both K60 classes
  are closed; `tests/resource/run_resource_tests.sh` section 2b now asserts
  `alloc_check`'s own rc + the absence of any `SUCCEEDED THROUGH` line, so a
  plant reopening either class is detectable inside `make test` itself, not
  only via the opt-in `make alloc`; `scripts/battery.sh` gains an `alloc`
  stage (after `san`, before `lint`, `make test` untouched). Two sabotage
  rows, S259 (D109's `cx.failed_nomem` propagation neutered — the ladder
  class) and S260 (`emit_state_legend`'s `dist` array reverts to a raw
  `malloc` with a silent NULL return — the legend class), both solo-run
  DETECTED — S260's second fail is a bonus: `emit_dfa.c` sits outside
  Section 0's own pinned allocation-site file set, so the plant trips that
  census too, on top of section 2b's absorption check. Floor control
  verified in the failing direction (a scratch floor set above the live
  population, reverted before commit). PARKED on `lane/allocpins`, not
  merged.

- `w2y_report.md` — [REVW.2] WAVE 2 SLICE E, EP2 steps 12-15 (2026-09-18,
  lane w2y, opus): the LAST four, so wave 2 is complete. F7 at both
  dispatchers (`vm_count_slots_look`/`vm_count_slots_rep`;
  `vm_wordb`/`vm_cap`/`vm_bref`/`vm_cat`), F14's `vm_look_behind_branch`,
  F8's `vm_listing_events` + `vm_listing_slot_row`/`vm_listing_slots` —
  verbatim relocations throughout, byte-identical on four streams per step
  against a pinned branch-point binary, NOT an `abi` event.
  Read §0 first: **EP2's anchor table is EXACT for all four steps (8/2/4/0)**,
  and the report says when that table can be trusted rather than merely
  scoring it — *a span-resolution anchor count is exact for a RELOCATION and a
  floor for a data-flow change*, which is precisely why w2a's (7 vs 9) and
  w2b's (6 vs 4) differed and these did not.
  Also worth reading for four things. **§3.2 is the finding the next
  sweep-builder needs**: the COMPOSITION arm — mandatory since w2a §4 item 6,
  because nothing else witnesses `vm_splice`'s DELIVER block — does not reach
  that block at all without `--features all`, since both deliver fixtures need
  module `recursion` and `--source` passes no features; 29 files / 84 artifacts
  at default against 32 / 96 with it, and neither figure reconciles with w2x's
  recorded 30 / 72, so three lanes have now hand-rebuilt one mandatory arm from
  prose and got three populations. **§3.3 is a vacuity check that a byte-identity
  green cannot be**: step 15 writes `irsb`, which no `.c` gate reads, so the
  3,518 listings were re-walked and classified by section — all nine rewritten
  families render rows on real corpus patterns (revdet thinnest at 58) and all
  five empty-population sentences render too; the census's own first draft read
  three families wrong because its markers were substrings of those families'
  own prose. **§4.1/§4.2 are the two re-aims that were not dedents**: S98's
  dedented `SAB_BEFORE` would ALSO have matched `vm_cost_rep` (the line that
  made the anchor unique was the `case` label the extraction deleted), and S133
  carries two anchors in one file of which only ONE moved — a whole-row
  mechanical dedent would have broken the correct half and then reported the
  row red after the re-aim. And **§2/step 15 records the one repetition lens 11
  named that cannot be folded**: the revdet slot family's three rows come from
  one loop index, so any per-family walk reorders the section.
  PARKED on `lane/w2y`, not merged.

- **dd8_report.md** — [DD-8] `--emit-ir` ADOPTS `docs/spec/table_contract.md`
  (lane dd8, branch `lane/dd8` from `7ee40500`, 2026-09-19; D106 + its three
  addenda, D108). The listing renders as machine-first TSV — NINE named
  `#section` blocks, the PROGRAM body among them
  (`label|op|args|target|note`) — through the wave-1 emission kit's `sb_row`,
  off the same `VEvent` walk as before. **§0 is the scope question answering
  itself**: D106 left open whether the body needed a sibling line-oriented
  contract, and the build says no — five columns carry all twelve instruction
  kinds and nothing had to be bent. **§2.1 is the rule that shaped every
  empty population**: the table contract makes the last `#` line before a
  section's data that section's HEADER, so a trailing remark inside an EMPTY
  section would silently become its column list — which is why an absent
  population is a ROW with empty cells, and why the reach census can count an
  empty arm as a projection instead of a re-walk. **§2.2/§2.3 are two named
  failures fixed by declaring a column**: `slots` gains a FAMILY column (w2y
  §3.3's census was defeated by families recognised from prose), and
  `prefilter` becomes nine value TOKENS matched by equality (the old `yes`
  needle was a substring of several OFF-route sentences). **§3.1 is the
  instrument finding a later lane should read before writing a byte sweep**:
  the first driver read 100% MOVERS and the compiler was innocent — the
  emitted `.c` carries `#include "<basename>.h"` derived from `-o`, so two
  different output NAMES are two different artifacts, and every prior lane
  validated against the opposite failure (a false GREEN from too little
  reach). **§3.2 adds the positive control** the `irsb` stream has needed
  since w2y: an arm that MUST move (2,804 of 2,804), so the `.c` arms' zeros
  are evidence rather than blindness. **§4.3 is a finding for [OPT-4.1]**:
  the `no-nullable-collapsed` route is a live arm of a shipped diagnostic
  that NO input can print, because [OPT-4.2]'s decline fires first and
  count-collapse can never make a language nullable — pre-existing, argued
  structurally, and not this lane's to fix. Eleven consumer scripts converted
  to declaration-based parsing (§5, with the hot-loop hoist shape in §5.1),
  `tests/lib/table.sh` given the mechanism's row-reading half, 16 baselines
  deliberately recaptured, `run_ir_listing.sh` 128 -> 144 checks, six
  sabotage rows re-driven SOLO and all DETECTED. NOT an abi event.
- `bsweep_report.md` — [BSWEEP] (2026-09-19, lane bsweep, sonnet): the
  COMMITTED emitter byte-neutrality sweep, `scripts/emit_sweep.py`, built
  once so w2a/w2b/w2x/w2y/w2census stop each re-deriving it from prose.
  Self-check (two independent builds of the same reference revision) +
  the real ref-vs-tree comparison, both against `ac21aaaf` vs. main
  `7f0f1e55` (wave 2 slice E) — 0 movers/asymmetric on all four streams,
  an independent re-verification of `w2y_report.md` §3's own claim — plus
  three isolated, reverted scratch sabotages (the `.c`-stream header
  comment; `vm_render_listing`'s own header, `--emit-ir`-only; `vm_splice`'s
  DELIVER loop, composition-arm-only, four surgically exact movers with
  `plaincall.c`'s `deliver_n == 0` as the built-in negative control).
  **Read §1.3 for the reconciliation the manager asked for mid-flight**:
  this tool's own FIRST cut measured 30 producing / 72 artifacts, matching
  w2x's recorded figure and disagreeing with w2y's recorded 32/96 — traced
  to two real bugs in `sweep_composition` itself (an `rc == 0` gate that
  skipped a fixture's genuine partial success; a composition-arm timeout
  under the argv streams' own concurrency), both fixed (`--comp-timeout`/
  `--comp-jobs`), giving a corrected 32/96 that now matches w2b's AND
  w2y's own `--features all` figure exactly — three of five lanes' numbers
  reconciled to one, w2x's left as a plausible-but-unconfirmed instance of
  the same class of bug (its own scratch driver is gone).

- `w4_report.md`, `w4_modesweep.py`, `w4_dashsweep.py`, `w4_diagsweep.sh` —
  [REVW.4] WAVE 4 (CLI + CONFIG) (2026-09-19, lane w4, opus): the axis
  table (`src/core/axes.def`, D111), the limits detector's D107 inversion,
  `SIZE_TERM_BAR_DEFAULT` to a `limits.def` row, the mode relation written
  once, and the `cli_parse` table. Six item commits plus one repair, every
  one byte-neutral on all `scripts/emit_sweep.py` streams; the wave adds
  the FIFTH stream (`dumps`, the seven `--list-*` surfaces) because the
  four `.c` streams structurally cannot see a registry dump move.
  Read §0 first — five things, of which two are refutations of ruled or
  reviewed premises. **D111's ruled ship shape for `lib/pcrec.h` (a
  generated enumeration block) was PRICED AT 650-700 LINES against its own
  ~150-line stop threshold and declined**: a row names its bit as a TOKEN
  rather than a number, so the bit stays spelled once in the public header,
  the header is byte-identical across the wave, and there is nothing to
  generate, no marker and no drift check — *a centralization that removes
  the duplication needs no instrument to watch it.* And **L11-F6's "X9 IS
  THE WHOLE REMEDY" for `emit_predicate_axes` is measurably false**: the
  function is 178 code lines before AND after, because what X9 owns is the
  flag COLUMNS and what makes the function long is ~40 per-candidate rows
  of narrative — *a centralization removes the columns a table owns, never
  the rows a narrative owns.*
  Also worth reading: the `cli/main.c:<line>` citation rot is not the
  review's 5 of 28 but effectively all 27 (resolved one by one against the
  branch-point file before anything was touched), and `docs/spec/` now
  carries ZERO of them; D107's "~14 allowlist lines" is really 40, and its
  three non-limit kinds needed a fourth; and §0 (5) names a re-pin the D94
  grep ritual is STRUCTURALLY BLIND to — `run_registry_tests.sh`'s coverage
  guard moved with item 2 while spelling a number item 2 never touched, the
  second recorded instance of *a reader whose text never cites the number
  still moves with it*. The three committed sweep scripts are the
  acceptance instruments: 1,407 mode pair/triple invocations, 248
  `--`-position invocations over 62 grep-harvested flag spellings, and 63
  diagnostic invocations, all 0 differing against the previous item's own
  binary.

- `emitverb_report.md` — [EMIT-VERB] (2026-09-19, lane emitverb, opus): the
  emitted-comment axis and its DEFAULT FLIP, two events per D112 item 4.
  Event 1 lands `-fno-comments`/`-fcomments` byte-neutrally (the first reader
  of `axes.def`'s `default_state`; the gate is `sb_cmt_open`/`sb_cmt_close` in
  the emission kit, D108); event 2 flips the default and bumps `abi` 26 -> 27.
  Read §3a first — **the `.o` proof found a real defect and it is not the one
  the brief predicted**. Five of 3,517 corpus artifacts compiled to DIFFERENT
  OBJECT FILES because `emit_vm.c`'s entry-shape AUTO rung compares
  `job->vmsb.len` — RAW emitted bytes, comments INCLUDED — against the
  4,096-byte knee, so a comment-free program crosses it and takes a different
  rung. Fixed by making the GATE size-neutral (`sb_len_uncut`), not by
  re-basing the term; whether a size term should price comment bytes at all is
  left open with its population (D77). The transferable form: *a render-time
  gate over emitted text is only neutral if nothing upstream reads that
  text's LENGTH as a decision.*
  Also worth reading for four things. **§4.4: the comment-reader census was
  done by MEASUREMENT because grep could not do it** — two passes were run
  and both were useless (needles built from shell variables; generic
  substrings matching emitted prose), so flipping the default and running
  the suites IS the census, and every red it produced is in the table with
  its conversion. **Two D94-addendum readers were found by the suites that
  COUNT rather than by the bump's grep**: the registry's axes-coverage pin
  (102 -> 108, a count of `^PASS: ` lines) and the cpset `EMITTED_BYTES`
  manifest. **§4.5 is a latent defect the third force macro made live**:
  `run_axes.sh` picked "the one DO-OR-DIE axis" by `PCREC_FORCE_*` name
  prefix keeping the last match, with two candidates already present and
  bash's hash order deciding — silent in both directions. And **§0's three
  corrections to the sources**, headed by the force macro's own spelling:
  `axes_registry_check.sh` derives the header's bit table with a
  `PCREC_(NO|FORCE)_` grep, so the deny/force naming convention is encoded
  in a CHECK and `PCREC_EMIT_COMMENTS` was invisible to it.

- `evtriage_report.md` — TRIAGE of [EMIT-VERB]'s two closing-chain reds
  (2026-09-19, lane evtriage, opus). **RED 1 (`run_specimen_identity.sh`,
  10 fails) is PRE-EXISTING and FIXED**: the branch point `4af16eb7`, run with
  its OWN script and OWN binary, returns the identical verdict — same five
  PASSes, same ten FAILs, same diff bodies, same `[strip] 22 of 1372` count —
  so the `-fcomments` conversion, the comment gate and the abi 26 -> 27 bump
  are all exonerated by one table. Two independent stalenesses, both live only
  because `make test-specimen` is an ON-DEMAND gate no `TEST_SECTIONS` member
  runs. (A) `.nentries` was missing from both exclusion lists: it reads the
  SAME `cx->n_named_groups` that `.nnames` reads and landed at abi 15, after
  both lists were written — *an exclusion list that names a family member by
  member goes stale the day the family gains one*. (B) the `[nocaps]` fill
  needle `^        for (int rx_g = 1;` matched a SECOND emission site — wave
  G's gated dead-group fill AND `emit_anchored_match_caps_def`'s
  unconditional loop in `<prefix>_match_caps` — so four FAILs were false
  positives while the property asserted had held continuously; re-aimed at the
  block header `strip_named` already anchors on, and given the POSITIVE
  CONTROL an absence assertion needs (1 block in each capture-declaring
  spelling's default artifact, 0 in `orig`'s), since an absence reads green
  when its needle dies. 13/0 after, was 5/10. **RED 2 (`make test` rc=2) is
  UNDETERMINED at hand-off**: the chain kept only `tail -60`, the trailer dir
  is markers-only and is `rm -rf`'d, and the surviving 24,948-line
  `watchdog.log` is entirely clean (zero non-`ok` verdicts) — so every failure
  was an assertion and none can be named from artifacts. §2 carries the
  not-yours rubric (the standing darwin `nm arm_a.o` red alone explains an
  rc=2) and §3 the re-run, launched as the lane's last act with its log path
  and `sections ran:` completion line. PARKED on `lane/evtriage`, not merged.

- `evtriage2_report.md` — TRIAGE ROUND 2 on [EMIT-VERB] (2026-09-19, lane
  evtriage2, opus): the `make test` reds the emitverb lane's own
  comment-reader census missed, because that census was done by running
  SUITES and `make test` runs more than the suites a lane thinks to run.
  Eight FAIL lines / five families over a complete run (`sections ran: 40/40`,
  rc 2); one is the standing darwin `nm` probe and the other four are fixed
  here. Read §1-§4 for the four dispositions, which between them are D112's
  whole question worked out on real cases.
  **§3 is the failure MODE worth carrying**: `run_backref_diff.sh` §10
  counted the role-text phrase `empty-iteration guard`, read zero on every
  fixture, and failed four times NAMING SABOTAGE ROW S107 — *a comment reader
  does not fail vaguely; it fails as the exact defect it was written for.*
  Converted to the guard's SLOT DECLARATION, which is written under the same
  `if (guard)` that writes the phrase, so it is the same fact and not a
  proxy; the 4/3/7 population reproduced unchanged, and S107 re-driven solo
  is DETECTED at `brefdiff 4fail/11pass`, the same four failures the phrase
  produced.
  **§1 is the only genuine class-2 case and the reason is structural**: an
  island's sole per-site marker is `vm_rolef` role text, its code is an
  ordinary first-byte `switch` with no island-specific token, and
  `RX_VM_ALT_ISLANDS` is already the block's second term — so a `-fcomments`
  artifact is generated with EXACTLY ONE CUSTOMER rather than switching the
  shared one. Its control is a POPULATION FLOOR, because the term is a
  biconditional and 15 of 16 fixtures exercise only its empty direction.
  **§2**: the `[M4.5c]` traced-artifact check had bound a stamp to a comment
  with one `&&` and failed naming the half that was fine (`RX_TRACE 1` was
  present throughout) — SPLIT, with a third arm asserting the default build
  carries no prose, without which a compiler ignoring the axis reads green on
  both. **So no gap D112 created was found and the abi 27 bump takes no rider
  from this lane** — a result, not an absence, since the brief allowed for one.
  **§4** is not a comment reader at all: a raw `wc -c` pin, comment-INCLUSIVE,
  where the cap it is about is comment-EXCLUDED — battriage's SECOND READER
  CLASS, third instance, and the same run proves the cap comment-invariant
  for free (its two refusal rows still print 1,034,778 / 1,335,605; a
  comment-counting cap would have ACCEPTED both). The re-pin had to be
  measured with the cell's OWN `-o` basename — a differently-named scratch
  file reads 762,107 against the check's 762,105, the `-o`-basename trap's
  fourth recorded instance. **§8** flags one pre-existing drift left alone:
  S107's `SAB_DOC_FIGURE` is +1 on both sides since §9b landed three weeks
  after it was measured.

- `evtriage3_report.md` — TRIAGE ROUND 3 on [EMIT-VERB] (2026-09-19, lane
  evtriage3, opus): `tests/codegen/run_recursion_identity.sh` at the new (B)
  pin, 7 passed / **11 failed** -> **16 / 0**, plus three more reds the
  concurrent gate surfaced. Read §0 first: the brief's lesson was "a
  known-red script masks every other FAIL in it", and the mechanism turned
  out to be worse than inattention — **the sweep loop `continue`s on a
  filter fault, so every count below it reads ZERO and every downstream
  assertion fails as a STALENESS claim about a population that was never
  measured.** That is how the script came to report, in its own voice, that
  `SIZE_TERM_REGION_MOVERS` "no longer move their program region" — false,
  and a cascade of red 1. *A filter self-check that `continue`s is a
  fail-closed gate on the whole body, and if its message does not say what
  it INVALIDATED, the counts below it get read as evidence.*
  **Red 1 is D112 class 2 and the fix is `-fcomments`, not a re-derived
  count**: one of the D37 filter's three lines is the `/* Feature set: */`
  COMMENT, and the gate reads comments a SECOND time — comparison (A)
  compares the program region unfiltered, and `vm_rolef` role text is the
  property that caught [M6.6.2] wave E's prose change. Narrowing the filter
  to two would have left a comment-free subject region compared against the
  pre-module pin's comment-bearing one, retiring the gate's most valuable
  property while reading green on the filter. Measured: 5 call-free VM
  patterns MOVED at the default axis, 4 of 5 SAME under `-fcomments` (the
  fifth is the [ENG-ISL] excuse the script already handles). Every
  SUBJECT-side generator takes the flag; `gen_b` does not — `ac4917d`
  predates the axis and REFUSES it, measured, and emits comments
  unconditionally. `gen_c` takes it too, so comparison (B) does not quietly
  lose whole-file comment sensitivity at the flip. The "exactly three"
  self-check is unchanged.
  **Red 2 needed no re-derivation and the four-tree A/B is what says so**:
  the two named size-term patterns move their region identically at
  `4af16eb7` (pre-EMIT-VERB), `385f3cab` (event 1), main default and main
  `-fcomments` — four fires on every tree, and the post-fix run reads
  `fired (4 across the axes)`, the number the A/B predicted before it ran.
  D112's open "should a size term price comment bytes" question is NOT
  landed by this evidence and stays open with its population.
  **The other three reds are two stories.** `[SEL-1]`'s `--no-captures`
  fallback population 1 -> 2 is a CORPUS event: `[ADM71.4]` (`e021b982`,
  same day) added a nullable counted repeat built to reach the DFA state
  cap, and all three compilers stamp it identically — re-pinned. The last
  two are **the [EMIT-VERB] rider's own +9 bytes** (`74c2192c` put the abi
  into the ESSENTIAL generated-by line), reaching two readers whose text
  cites a byte count and no abi digit — `battriage_report.md`'s SECOND
  READER CLASS, fourth and fifth instances. The `a{5,25000}` rescue pin
  reconciles exactly (762,104 event 1 + 1 event 2's blank line = 762,105 the
  old pin + 9 = 762,114), confirmed by DIFFING the artifacts rather than
  inferring from the size. And the cpset CHECK 3 manifest drifted on **all
  12** `EMITTED_BYTES` rows, not the 5 its own message showed: `diff | head
  -20` cut it off, and both readers of the battery log counted the
  population from the message — *a check that says "this is a DIFF TO
  REVIEW" must print the diff it wants reviewed*; window widened in the same
  commit. Validation COMPLETE (recursion-identity 16/0, vm_identity 10/0,
  resource 0 failed, cpset 28/0, specimen 13/0, comments_axis 65/0,
  test-codegen 9/10 with the standing darwin `nm` probe as the sole red,
  S40 re-driven solo DETECTED). PARKED on `lane/evtriage3`, not merged.

- **w5_report.md** — [REVW.5] WAVE 5 (public surface) + [REVW.A1], the LAST
  items of the 2026-09-17 code review (lane `w5`, opus, 2026-09-19, branch
  `lane/w5` from `25b1984f`, 13 commits). **Headline: `nm -g
  build/libpcrec.a` reports 295 exports and ZERO without a `pcrec_` prefix**
  — 34 were unprefixed at the branch point, which is neither D104's 12 nor
  the fact sheet's 29 (four more landed with [EMIT-VERB] in between, by the
  same `static`-dropped-for-cross-TU mechanism, and the population has grown
  at every measurement anyone has taken of it). Items: the §8.2 struct
  quotation goes 9 members -> 19 as shipped and `tuning.md` §4's mirror 14
  bits -> 28 with a statement that it is exhaustive and a named list of the
  four bits deliberately outside it; the mask catalogue stops delegating to
  `lib/pcrec.h` (a D80 inversion); `pcrec_limits_tsv` is DECLARED in the
  public header and its declaration LEAVES `internal.h`, with lens 9's
  `#define`-generation option declined in writing because it would be a
  second spelling of every number; two of P4's eleven constants turned out
  not to exist (`PCREC_PREFILTER_EXACT_NFA_STATES` was deleted at [OPT-4]
  and the header still described a threshold that is gone;
  `PCREC_VM_INLINE_CHAIN_MAX_BYTES` had an INVENTED prefix); and the abi
  change log is cut from four homes to one, `match_api.md` §6, with
  `emit_dfa.c`'s 449-line narrative becoming 22 lines and a D76 addendum
  recording why §6 was the only complete one (the bump ritual already writes
  it). **The union mode membership was MEASURED AND DECLINED**: 4 acceptance
  flips over 1,407 invocations and three of the four are `--flavour`'s
  DOCUMENTED primary use (`--list-syntax`/`--list-definitions`/`--explain`);
  `w4_report`'s motivating example (`--probe-ask --flavour` "is accepted") is
  false — it is refused today, by the site's own applies-to arm. Three
  method lessons worth the read: the anchor population is a question about
  ANCHOR TEXT and `grep -rl` over-counts it by 4x while two hand-written
  extractors under-counted it (hand it to BASH, or better, use the tree's
  own `scripts/m6read_check_sab_anchors.py`, which this lane found only after
  rebuilding it); a sabotage `SAB_DOC_FIGURE` that QUOTES a check's failure
  message is a reader of that message and cites no symbol grep could find
  (S254); and `check01_isolation.sh`'s SPEC-M positive control has been DEAD
  on darwin since the two-machine split (its `EXC_SYMBOL` lacks the
  underscore darwin's `nm` prepends), A/B-ed against the branch point and
  reported rather than fixed. Merged/not: delivered on `lane/w5`, the
  wave-closing sweep and 24 of 33 sabotage re-drives OWED with commands in
  the report's §7.
- `axtriage_report.md` — TWO unrelated lanes share this name and this
  file, kept as two sections (the 2026-09-09 one was never given a
  bullet here either; both are recorded now). Section 1 (2026-09-09):
  the stage-5 battery `axes` red was `--engine=vm`'s first-ever
  documented refusal (K55, `\P{Unknown}` under `-e utf8` past
  `PCREC_MAX_VM_EMIT_CODE_BYTES`) — one `REFUSAL_PATTERN` entry, not an
  engine regression. Section 2 (2026-09-19/20, RELAUNCHED on the same
  worktree/branch name from a much later main, 25b1984f): a different
  red on a different corpus file — `--engine=dfa` forced on adm71's new
  `(?:ab){0,16000}` (`tests/base/opt41_rung_nullable_decline.rxt`,
  built to overflow `PCREC_MAX_DFA_STATES_TABLE` so `auto` declines the
  [SEL-1] collapse rung) reaches `src/ir/dfa.c:954`'s own do-or-die
  state-cap diagnostic, which tuning.md §2.11/[SEL-1] already documents
  verbatim (no spec gap) but which `run_axes.sh`'s own 2026-09-03 (K45)
  comment had explicitly anticipated and left OUT for having zero
  measured population at the time — now populated, one substring added.
  Single-file positive/negative control confirms the fix
  (`refused_undoc`: 6 -> 0); swept every OTHER axis on the same file too
  (item (d)), finding no other genuine defect, only the same
  floor-vs-scope artifact on two axes with their own K35 floors.
  Full-corpus floor confirmation and `make test-codegen` are OWED —
  `worktrees/w5`'s own `make test` held the box for this lane's whole
  working period (box-concurrency rule 9). PARKED on `lane/axtriage`,
  not merged.
- `w5r_report.md` — [REVW.5.1] the wave-5 rider (lane w5r, sonnet, 2026-09-20; item 3 landed by the manager): `--flavour` gets its OWN applies-to relation and the 13 real modes one union mask, acceptance proven unchanged (w4_modesweep.py 1,407/1,407 identical; cli 284/0; 5-stream sweep 0 movers); `tests/spec_mod0/check01_isolation.sh`'s positive control revived on darwin (nm's `_` prefix stripped where nm output is read; population 36/9/4/1 unchanged; its sabotage DETECTED solo); S107's SAB_DOC_FIGURE re-recorded as MEASURED 2026-09-20 (brefdiff 4fail/11pass; the +1 is §9b).

- `nltriage_report.md` — TRIAGE of the Linux battery's `[OPT-4.1]
  -fprefilter` red at main `05499cba` (2026-09-20, lane nltriage, opus;
  triage + targeted fix, no ssh to ubuntubudu — a battery held it).
  **Verdict: MARGINAL CPU BUDGET, not introduced by any commit in the
  suspect range.** The same compile measures 11.288 / 11.305 / 11.292
  median user-CPU seconds at `25b1984f` / `55321f28` / `05499cba` (five
  runs each, spread under 0.4% across all fifteen, byte-identical
  18,160-byte artifacts), so lane/w5's 34 renames moved nothing — and
  `src/ir/dfa.c`/`src/opt/minimize.c` differ over the range by identifier
  text alone. Two corroborations the brief did not ask for: the battery's
  OWN reported `peak rss 26796 kB` against this box's 29,056 kB says the
  killed process had reached ~92% of the work's memory high-water mark and
  was therefore doing the same work, and the check's `-O1` reference build
  is exonerated as a cost (an `-O2` build runs the case in 11.36s — it is
  memory-bound minimization, K25). `K7_CPU`=45s is 3.99x this box's number
  against the ">2x inflation under a real -j12 mix" its own calibration
  comment prices in, on a box `xarch_step0.md` measures 1.93x slower:
  `btriage2_20260918_report.md`'s finding recurring at a second cell in the
  same file.
  **Fixed on two axes rather than by widening the budget.** (1) The witness
  is scaled to the cap instead of the budget to the witness —
  `(a|b){0,12000}` at a reference cap of 100,000 rather than
  `(a|b){0,30000}` at 500,000 — which is **strictly better on every margin
  the cell depends on**: the exact artifact clears the cap by 3.74x rather
  than 1.83x (*the* margin, whose erosion made this cell vacuous four
  separate times, now the widest it has ever been), the declined-nullable
  default (12,114 B) and the collapsed rescue (18,151 B) sit 5-8x under the
  cap so the cell still tests an OVERRIDE and not a compiler that always
  takes the rung, and CPU goes 11.29s -> 1.83s for a 24.6x budget margin.
  The rescue artifact is the SAME artifact, diffed rather than inferred
  from its size — the only moving lines are the pattern text, the `-o`
  basename, the cap value and the count digits. No `SAB_REACH_POP` floor
  reaches this cell (the three naming this script all land on
  `size_rung_cell`/Section 1b, which use `$PCREC` and the real cap).
  (2) The `rc` arm becomes a `case`: the old `if [ $? -eq 0 ] ... else`
  folded a real refusal, a watchdog CPU kill, a wall timeout and an RSS
  kill into ONE message asserting that limits.md §3.3 had gone false —
  *a check's FAILURE MESSAGE is a second, undeclared claim about the space
  of causes*, in its sharpest recorded form, since the message named a spec
  section by number. 122/123/124 are now distinguished and the two
  CPU-inflation can produce route through `load_guard_tripped` (Section 1's
  [TT-10] shape); only `rc 1` keeps the §3.3 sentence.
  **The tier question answers itself from the spec**: §3.3's own next
  paragraph reads "What pcrec does NOT promise is a bound on wall-clock
  compile TIME ... D45 is a TEST HARNESS policy, not a caller-facing
  contract ... a guard on the SUITE", so a `scripts/watchdog` CPU kill sits
  on the other side of the line §3.3 exists to draw — the check was reading
  a correct spec at the wrong altitude and no spec hunk is owed.
  Validation COMPLETE on this box: resource **27/0/0** (1 expected darwin
  skip), `make strict CC=gcc-16` clean, and both failing directions forced
  (`K7_CPU=1` reports the budget rather than §3.3; a raised reference cap
  still reddens the stamp arm, so the cheap witness is not vacuous). §7
  names the one optional quiet-box Linux measurement that would pin the
  Mac/Linux ratio for the minimization path — a number no measurement in
  the tree currently holds, and which every `K7_CPU`-family budget is
  implicitly calibrated against. PARKED on `lane/nltriage`, not merged.
- `hdrgen_report.md` — [HDR-1] a purpose header for every function in
  `src/gen/emit_vm.c` and `src/gen/emit_dfa.c` (lane hdrgen, 2026-09-20,
  from `c007e9d2`; Frank's charter: "from the name, it isn't clear what
  `vm_ev` is about"). 129 headers on a measured 131-function unheaded
  population (emit_vm 26, emit_dfa 105), sized per coding_guide §4.2 — one
  line for an axis predicate or a name builder, the three-part form for the
  eleven long ones. The brief's 137 was the committed census's figure; the
  6-function gap is a banner-classification difference between two readings
  of one rule, resolved by classifying every function in both files rather
  than sampling. UNCLEAR list EMPTY. The two residual rows (`vm_rolef`,
  `dfa_fragf`) are a CENSUS ARTIFACT, not a gap: each already has a header,
  above the printf-attribute forward declaration that sits between it and
  the definition, so the mechanical rule reads the `__attribute__` line and
  scores them unheaded. Comments only, so not an abi event — and PROVEN so
  rather than asserted: `scripts/emit_sweep.py --ref c007e9d2` (see the
  report's Validation section), `make strict CC=gcc-16` clean, sabotage
  anchors 285/285 unmoved.

- `hdrrest_report.md` — [HDR-1] purpose headers for `src/`/`cli/`/`lib/`
  EXCLUDING `src/gen/emit_vm.c`/`src/gen/emit_dfa.c` (2026-09-20, lane
  hdrrest, sonnet): 276 functions across 43 files that carried no header
  (a section banner or nothing directly above the signature) at the
  branch point now carry one, sized to the function per
  `docs/dev/coding_guide.md` §4.2 as [HDR-1] extends it. Also lands
  `function_census.py`'s new `header` column (validated against the
  manager's own pre-population census: identical 504/75/338-of-917
  totals and per-file counts everywhere it listed one), the guide's
  one-sentence extension, and the regenerated
  `tools/review/out/function_census.tsv`. Zero `HDR-1 UNCLEAR` markers;
  `scripts/m6read_check_sab_anchors.py` reports 285/285 resolving
  unchanged (insertions are new lines strictly above a signature, and
  the mechanism resolves by text match, not line number). `make -j4
  CC=gcc-16 && make strict CC=gcc-16` CLEAN; `scripts/emit_sweep.py
  --ref c007e9d2` / `make test-codegen` / `make test-registry` OWED — a
  darwin battery held the box for this lane's whole working period, so
  they run backgrounded as the lane's last act, polling the battery's
  own trailer for completion first (log path and exact completion line
  in the report). PARKED on `lane/hdrrest`, not merged. Companion
  lane `hdrgen` owns the two excluded emitter files.

- `hdr2_report.md` — [HDR-2] the first-sentence header pass (2026-09-20,
  lane hdr2, sonnet): the readability experiment's fix for [HDR-1]'s own
  regression (`docs/dev/reviews/2026-09-20-readability-experiments.md`
  §1 — a header lowered function comprehension 68% -> 57% because it led
  with a tag/invariant instead of what the function does). Lands
  `coding_guide.md` §4.2's FIRST-SENTENCE rule, then re-reads every
  function header in `src/gen/emit_vm.c` (43 tag-first + 6
  cross-reference-first) and `src/gen/emit_dfa.c` (32 tag-first + 12
  backtick-first) against it, covering grade_summary2.md §(d)'s whole
  "wrong under B, correct under C" named population that lives in these
  two files (the `vm_isl_*` island-trie family among them) plus its
  field half (`Vm.cg`/`has_calls`/`nsplice*`/`nlookmark_total`/
  `ev`/`evcap`, none of which had a trailing comment before this).
  **Acceptance: functions reach 82.9% under the re-run experiment
  (bar >= 68%, MET with margin); fields read 31.9% (bar >= 42%, missed)**
  — traced to fields the grader itself named (`Vm.cx`, `Vm.enc_mask`,
  `Vm.rgn_emit`) having NO trailing comment at all and sitting on
  NEITHER of §(d)'s two named lists, so outside this row's chartered
  scope; a second guesser run scored fields far higher but its own
  grader flagged a row-alignment break past row 35 (the population's
  duplicate names, e.g. two `Vm.b` rows, make a kind/name realignment
  unreliable) and is discarded rather than reported as a pass.
  Comments only; `make -j4`/`make strict` clean, `scripts/emit_sweep.py
  --ref bc6750bc` 0 movers on all five streams, sabotage anchors
  285/285.

- `rel1a_report.md` — [REL-1.1]/[REL-1.2] (2026-09-21, lane rel1a, sonnet):
  the first README.md landing (roadmap corrected — M4/M5 shipped, M3
  streaming the one open milestone — public surfaces named and pointed
  at their owning docs/spec/ file) and `docs/pcre2_compliance.md`'s
  compliance-refresh zero-drift re-run. Docs only.
- `rel1b_report.md` — [REL-1.4] version plumbing (2026-09-21, lane
  rel1b): D115's ruling built exactly — `PCREC_VERSION` = `"0.1.0-beta"`,
  independent of `abi`, `--version`, exported from `lib/pcrec.h`, stamped
  in the emitted provenance line, abi 27 -> 28, CHANGELOG.md seeded.
- `rel1c_report.md` — the D116 README REWORK (2026-09-21, lane rel1c):
  README.md cut from rel1a's 125 lines to 65 per Frank's "brief and
  friendly, no number that can drift" ruling — the seven-section
  structure the ruling specifies, with a digit-by-digit audit of every
  remaining number's drift risk.
- `iface_digest.md` — the D116 INTERFACE DIGEST (2026-09-21): facts
  extracted for Frank's pre-guide interface discussion — the CLI, the
  four-function library surface and the generated artifact's own
  surface, every claim cited to `file:line` or a live `--help`/
  `--version` run, no recommendations.
- `edgefit_report.md` — [OPT-EDGE] I-82 LADDER FIT + m=2 MECHANISM
  (2026-09-21, lane edgefit, sonnet; data + report only, no `src`/
  `tests`): the numbers D117 rules on. The ladder fit (`t(k)=a+b·k`
  over the shared-sentinel dispatch, with the caveat that the four
  rungs are different patterns/subjects, not one machine scaled, so
  `b` is this ladder's own average slope) and the m=2 floor cell's
  bimodal signature attributed by mechanism (which BINARY moves flips
  between runs; neither round index nor measurement order predicts the
  mode) rather than dismissed as unexamined noise. Does not rule on the
  floor itself — that is the manager's, per D117.
- `rel16_report.md` — [REL-1.6] CI (2026-09-21, lane rel16, sonnet):
  `.github/workflows/ci.yml` (checkout, `libpcre2-dev` so PC-3/PC-4/uprops
  run rather than SKIP, `make`/`make strict`/`make test` at a 90-minute
  step timeout, upload-on-failure), `.github/PULL_REQUEST_TEMPLATE.md`,
  and the `docs/testing.md`/root `CLAUDE.md` CI notes. The report is the
  "does it fit?" reading plan (job status, `time`'s wall/user/sys tail, the
  `sections ran: N/M` trailer) plus the reasoned finding that NO
  per-section timing exists to read (`run_group.sh` prints none;
  `tt4m_time.md` already found the same structural gap on the Mac box) and
  a DESIGNED-not-built `test-ci` subset fallback (D77) with its removal
  order and why `test-corpus` is never a candidate for it. Cannot be
  validated further from this worktree — running Actions and reading the
  result is the manager's, per the brief.
- `backtri_report.md` — [BACKLOG-TRIAGE] (2026-09-22, lane backtri,
  sonnet, docs-only, read-only against plan.md): the triage inventory
  (`docs/dev/backlog_triage_2026-09-22.md`), 93 rows (81 not-started + 12
  dormant-started, corrected from the brief's unanchored-grep 100/102 —
  an anchored count is 81, the discrepancy traced to rows whose own prose
  says "formerly STATE:not-started"). Worth reading for the honesty-check
  findings surfaced while dispositioning triggers rather than asked for:
  [DD-1]'s remaining charter already shipped under [M5.0] stage 4's own
  "DD-1's FOLD CLOSURE" (plan.md never got a closure note); [DD-12] is a
  one-line unfinished stub superseded by the real UTF-8 design; [DD-7]'s
  both halves are already dispositioned in its own text pending one
  unverified "M4.3 panel" citation; a cluster of four rows (DD-2,
  M4-CALLOUTS, M4-SUBST, DD-6) name M4/M6-assertions as their trigger and
  that milestone shipped months ago with none of them revisited;
  [CC-CLANG] still reads "awaiting merge review" though `git merge-base`
  confirms it merged; [DD-11]'s stated M6.6 gate closed 2026-08-24 with
  the follow-on never reopened; [BENCH-1]'s own text already concedes it
  is superseded by D78/D119. Recommends folding [BENCH-1] into D119's
  OPTLOOP model and closing [OPT-4.2] (a closed Frank ruling sitting in
  an open row) as plan-row cleanup, neither acted on here (read-only).

- `profread_report.md` — [OPTLOOP.1.profile] (2026-09-22, lane profread,
  sonnet, docs-only): the I-85 profile pass (12 transcripts on
  ubuntubudu) read against `cycle1_analysis.md` §3's own EXPECT lines,
  block by block, numbers cited to transcript file:line. See
  `docs/dev/optloop/cycle1_profile.md` for the full reading. Four of
  five mechanisms (M1, M2, M3, M5) PARTIALLY CONFIRMED — real,
  correctly-directioned effects that miss a stated numeric target or
  fail a named target/carve-out cell; M4 CONFIRMED cleanly. Two
  target-cell anomalies: M2's `evil-alt-nested` twin is non-constant and
  INVERTED with subject size; M3's `json-constant` twin REGRESSES
  (×1.10 slower), refuting M3 for that row by the block's own stated
  criterion. M1's uniform ~2.2x floor gap (0.037 measured vs. 0.017
  stated) is shown NOT a set-grain artefact by direct recompute. M6
  decides its own open question (a steps-per-attempt effect, not a
  per-step one). Also finds the run's own stated pin (`405668e9`) is one
  commit behind what was actually built (`69172a00`, docs-only,
  inert for the measurements).
- `optrev_report.md` — [OPTLOOP.1.analysis] = [BENCH-REVIEW], cycle 1 of
  the optimization loop (2026-09-22, lane optrev, opus; analysis only,
  nothing under `src/`/`tests/`, nothing written in pcrec-bench). Delivers
  `docs/dev/optloop/cycle1_analysis.md` + its reproduction pieces: all 128
  (pattern, regime) cells of `capability@0.1` at pin `25b1984f` ranked by
  D119's priority rule, cause-bucketed off the D81 stamps, five target
  mechanisms with their owed Linux profile command lists, the deferral
  dispositions, and six proposed plan rows. Read the report for four
  things. **The bench's own `floor-byte` row is the control that makes the
  analysis citable**: pcrec reads 17,611 ns at 1 MiB against libpcre2's
  17,693 and rust's 17,817, so the 0.0168 ns/byte "one memchr-class pass"
  rate every winner achieves is a rate pcrec ALREADY achieves — which is
  why the gaps are attributed to pre-checks pcrec does not compute rather
  than to a speed it cannot reach; the same row read the other way shows
  `--engine=vm` on the single literal `~` costing 35x `auto`, because a
  forced VM has no prefilter and walks every start position. **A
  best-of-variants ranking hides the shipped default**, and on
  `evil-alt-nested`/`trim-nested-star` that hides 49,016x and 39,447x
  (captures move the artifact off the DFA onto a prefilter-less VM), so
  the analysis carries a separate default-config table. **The
  [OPT-FIRSTSET] witness is one construct wide and was built rather than
  argued**: `A[A-Z0-9]{16}` stamps `memchr` with a 1-byte candidate set
  and `\bA[A-Z0-9]{16}` stamps `byte-class-bounded` with the 63-byte word
  class (77.21% of the bench text), while PCRE2 records
  `FIRSTCODEUNIT='A'` for both — the named cause of [OPT-3]'s own measured
  "the skip loop skips ZERO bytes". And **an extraction bug that reads as
  a compiler bug**: `--list-source`'s `pattern` column is escaped in
  `pcrec_sb_field`'s vocabulary, so a pattern taken from it and handed
  back to `--pattern` undecoded produces nine plausible refusals ("range
  out of order in character class", "missing terminating ]") on patterns
  the bench compiles at the same pin — caught not by re-reading the
  decoder but by diffing all 64 decoded patterns against the bench's
  independently-derived `patterns/*.rx` exports, 64 of 64 identical.
  Nothing owed by the lane; the Linux profile blocks are a precondition on
  any implementation lane and are named by section id in report §5.

- `closefold_report.md` — [BACKLOG-TRIAGE]'s close/fold pass (2026-09-22,
  lane closefold, sonnet, docs-only): applies Frank's ruling "Agree with
  close items" — DD-1/DD-12/DD-7/BENCH-1/OPT-4.2/TT-14 flipped to
  `STATE:completed` with a closure note and archived to
  `plan_completed.md` (anchored counts 81→77 not-started, 19→17 started,
  reconciling exactly); [BENCH-1]'s dependency/gate text re-pointed at
  [OPTLOOP] in seven rows found by grep (BENCH-CEIL, ENG-ABS, ENG-CUT,
  ENG-ISL, ENG-PGO, SIMD-META, OPT-SIMD) without changing their STATE;
  one root-CLAUDE.md situation-index row added; [OPT-4.2]'s witness-gap
  ruling cross-referenced into `known_issues.md`'s K41 entry (no prior
  cross-reference existed). SCOPE ADDITION, same lane: Frank's
  ratification of cycle1_analysis.md §5's six proposed rows landed as
  `  - [ID]` sub-rows under `[OPTLOOP.1.impl]`, extracted programmatically
  from the source's fenced blocks and verified byte-exact before commit,
  each carrying a `(RATIFIED ...)` batch-tag prefix; not-started count
  moves 77→83 (+6).
- `capsview_report.md` — [OPTLOOP.1-CAPSVIEW] (2026-09-22, lane `capsview`,
  docs-only): Frank's apples-to-apples ruling on `cycle1_analysis.md`'s
  ranking, answered by re-ranking pcrec's SHIPPED DEFAULT (`auto-caps`)
  against capture-bearing competitor engines only, instead of §1's
  best-of-four-pcrec-variants figure. 65 of §1's 91 win/tie rows were
  carried by `auto-nocaps`, not the default; 58 of those still hold under
  the caps-only view, 5 flip to a loss (two more than §1.1 named), and one
  pattern (`wild-datetime-datefinder-alternation`) never had a real
  `auto-caps` number at all. The five §3 mechanisms are robust (move
  under 2%) under `auto-caps` alone; the remaining unexplained caps-losing
  population (25 rows, score 6.0106) is dominated by a 14-row "capture
  group" `RX_ENGINE_WHY` bucket (score 4.6833), named as the population
  for the manager's separate captures-mechanism survey. See
  `docs/dev/optloop/cycle1_caps_view.md` (the memo) and
  `docs/dev/optloop/CLAUDE.md` for the reproduction scripts/data.
- `admin1_report.md` — [MACPORT-XARGS] + [LIM-OVR] bundle (2026-09-22,
  lane admin1, sonnet). [MACPORT-XARGS] is a FINDING, not a fix: Frank
  himself closed the row's whole charter directly on 2026-09-10 (commit
  `fb1b9c5e`), four days after it was chartered and never re-flagged in
  plan.md — live-verified 212/0/1 on darwin, no code change made or
  needed; also flags that `docs/dev/backlog_triage_2026-09-22.md`'s own
  MACPORT-XARGS row cites the same now-stale 14-failure figure as if the
  row were still open. [LIM-OVR]: the audit the charter asked for
  ("audit the other five BUILD_D rows") found FOUR two-lever rows, not
  one — `PCREC_DEFAULT_WARN_EMIT_BYTES` was missed by any audit that
  only greps `cli/main.c`'s `raise_only_limits[]` table, since its
  `--warn-emit-bytes=` flag is wired through a separate bespoke
  `else if` block (it is settable, not raise-only). Built the `FLAG_D`
  token exactly as scoped (identical `-D`-movable-default machinery to
  `BUILD_D`, an honest `"flag+-D"` dump rendering) and the owed
  override-honesty check (`tests/registry/limits_check.sh` part 4, reads
  `cli/main.c` independently of `limits.def`'s own claim, both
  directions), sabotage-validated live and S208 re-aimed. `make strict`
  clean; `limits_check.sh` 27/0; `make test-codegen` 9/10 scripts (the
  sole red is the standing darwin `nm arm_a.o` probe, unrelated,
  documented in 29 other lane reports). **This landing's own count guard
  in `tests/registry/run_registry_tests.sh` (a DIFFERENT file from the
  one edited, and never re-run here) was left pinned at the pre-[LIM-OVR]
  value — see lane regred below.**
- `regred_report.md` — (2026-09-22, lane regred, sonnet) why `make
  test`'s registry section exited 1 on darwin with every check inside it,
  `limits_check.sh` included, reporting `checks failed: 0` and no `FAIL:`
  line anywhere: `run_registry_tests.sh`'s own coverage guard on
  `limits_check.sh`'s PASS count was still pinned at 24 after [LIM-OVR]
  (lane admin1, same day) added three PASS lines, taking the real count
  to 27 — a stale-pin recipe bug, not a darwin-specific red (the same
  drift reproduces identically on Linux). Re-pinned 24 -> 27 with the
  file's own explanatory-comment convention. Zero `src/` changes.
  Validation OWED at handback: the box's one-heavy-suite-at-a-time rule
  had another lane's `make test-axes` still running, so `make
  test-registry` itself was not re-run before handback — see the report
  for the exact command owed.
- `admin2_report.md` — plan archive sweep + learnings + BOILERPLATE
  (2026-09-22, lane admin2, sonnet, docs-only, three commits). (1) Moves
  62 of plan.md's 70 resident `STATE:completed` rows to `plan_completed.md`
  (the header's own promise, unhonored since same-day closefold/admin1/
  regred/capsurvey merges had already made the brief's 71/72 baseline
  stale by the time this lane started — the real count was 70, since
  `STATE:completed-in-place` is a genuinely distinct, deliberately-kept
  state the loose grep also matched). Grouped by parent `##` heading;
  [REL-1] and its 11 numbered children collapse to one stub matching the
  file's own pre-existing "archived to plan_completed.md (...)"
  convention, with a similar pointer under the still-open [SPEC-1]. Kept
  8 rows resident despite being `STATE:completed`, each argued from the
  file's own content: [TT-4]/[TT-4.1] (an adjacent STATE:started sibling,
  [TT-4M], explicitly narrates re-opening [TT-4]'s closed levers),
  [OPTLOOP.1.analysis] (the brief's named exception), [ENG-ISL.S0] (same
  shape, judged), and the four indented [DD-13a]/[DD-13b.W1]/[DD-13b]/
  [DD-13b.panel] children of the still-STATE:started [DD-13] (with
  [DD-13b.W1.3], also started, physically wedged between two of them) —
  [DD-13c], despite the similar name, is a separate non-child row and
  archived normally. Corrects one mechanical block-boundary
  mis-attribution before it shipped: a naive "next bullet or heading"
  scanner would have swept ten lines of the PARENT [ENG-ISL]'s own
  continuation prose into the archived [ENG-ISL.S0] block, because that
  prose restarts a different topic with no bullet marker of its own.
  Anchored counts reconcile exactly (81/14/70->8 in plan.md,
  203->265 in plan_completed.md). (2) `learnings.md` §3 addendum, three
  lessons from the ff63ebf3 gate misread: a coverage guard living in a
  DIFFERENT FILE from what it counts (regred's finding, its own comment
  history's fourth instance of the shape); "sections ran: N/M" counting
  launched, not passed, sections (lane axesfix's finding); and
  [MECH-REACH]'s seventh instance, a whole-window pre-check retiring a
  witness population by omitting the pattern's required byte. (3) Three
  terse `BOILERPLATE.md` additions (detached owed runs; darwin timeout
  sizing per suite, `AXES=` verified against `run_axes.sh` before
  citing; naming the FILE a "re-ran standalone, clean" claim covers) plus
  one root-`CLAUDE.md` situation-index row on reading a gate's real
  verdict. Docs-only throughout; no build or suite run applicable to any
  of the three deliverables.

- `c2prep_report.md` — **cycle-2 PREPARATION** (2026-09-22, lane `c2prep`,
  opus; docs + throwaway census instruments only, nothing under
  `src/`/`lib/`/`cli/`/`tests/`, no timing anywhere). Three deliverables under
  `docs/dev/optloop/`: `firstset_design.md`, `reqpos_census.md`,
  `onepass_census.md`. Read the report for five findings, of which the first
  two are refutations of ratified text.
  **`[OPT-FIRSTSET]`'s mechanism as ratified is UNSOUND, and its own proposed
  identity check passes it** — narrowing `rx_can_begin_match` to the AST-level
  first-byte set makes `\b(?:true|false|null)\b` report a SPURIOUS match on
  `"atrue xnull "` where the shipped artifact answers `matches=0`, because the
  DFA's start state encodes the preceding byte's word class and the bytes
  leaving it live include every word byte; `{t,f,n}` IS a subset of word-63,
  so M3's "the new set must be a subset" guard is satisfied by the unsound
  narrowing. The repair is one line reusing `rx_forward_seed_state`, a table
  the artifact already emits, and changes no count.
  **The cost model the note was chartered to supply declines nothing**:
  `skipped + steps == n` exactly, so cost per byte is `(L·b + w·a + c)/(L+w)`
  with `L = (1−d)/d`, an identity predicting the measured skipped fraction to
  within 0.03% on four configurations, whose derivative in `L` is negative for
  every admissible parameter — and the one measurement contradicting it
  (`json-constant`'s ×1.10) is the one no accounting over its own artifact's
  counts reproduces, missing it by 2.36×.
  **`[OPT-REQPOS]` tier 2 does not clear D77** (two of cycle 1's 34 losing
  cells; 6.0% of the corpus) while **tier 2b does** (27.3% of the bench, and
  five `capability` patterns whose byte is PRESENT and whose RUN is ABSENT).
  **The one-pass DFA survives its kill gate by 3×** (capture-bearing reach
  31.46% corpus / 29.41% hybrid against ~10%), with two results beyond it: the
  UTF-8 narrowing the survey expected moves that figure 0.06 points because
  46.3% of the population is excluded by node KIND first, and `pcrec_altcls`
  factoring is worth +3.16 points, so pcrec's reach is measured on pcrec's
  trees.
  Also worth reading for **F1, the cheapest item in the delivery**: 14 of 36
  `capability` patterns have a rarer necessary byte than PCRE2's rightmost
  rule picks and on three the rarer byte is ABSENT while the picked one is
  PRESENT, so batch 1's shipped pre-check cannot fire where a
  frequency-informed pick would answer the whole call in one pass — no new
  emitted mechanism, just which member of a set `reqbyte.c` already carries.
  And for **F5**, two build-time findings recorded in the probe sources: a
  census walk must fold the `A_CAT` spine iteratively (the first draft died on
  the corpus), and a census that reconstructs the pipeline must reconstruct
  every REWRITING pass above the analysis's own call site (the first draft
  read `s` where batch 1 stamps `r` on `/user|/users`, because
  `pcrec_altcls` factors it) — caught only because the census was built with
  a cross-check against a shipped stamp rather than against its own reasoning.
  documented in 29 other lane reports).

- `optimpl1_report.md` — [OPTLOOP.1.impl] BATCH 1 (2026-09-22, lane
  optimpl1, opus): the three WHOLE-WINDOW PRE-CHECKS — [OPT-ANCHOR-VM]
  (`src/opt/startanch.c`, the VM's attempt-loop start bound), [OPT-ENDWIN]
  (`src/opt/endwin.c`, the end-anchor start window) and [OPT-REQBYTE]
  (`src/opt/reqbyte.c`, the necessary-byte pre-check), each an axis, each its
  own commit group, plus ONE `abi` 28 -> 29 bump with the full D94 ritual.
  Read §0 first — three findings.
  **[OPT-REQBYTE]'s own plan row names a carve-out cell that this
  implementation FALSIFIES**: `router-prefix-order` is listed as
  byte-identical because PCRE2 records no required unit for it, and pcrec
  stamps `'r'` — the row's premise was PCRE2's derivation, and this one
  INTERSECTS an alternation's branches and does not impose PCRE2's "other
  than at its start" restriction, both deliberately. The cell is no longer a
  byte-identity control.
  **`cycle1_analysis.md`'s own M4 hand-twin over-counts the window by one**
  (`maxw(abc$)` is 3, not 4), so the landed artifact stamps a window of 4
  where the twin used 5 — the twin is sound and is not what the mechanism
  computes.
  **And two of the three mechanisms have NO answer-level detector anywhere in
  the tree**, which is why S263 measures `corpus:0fail/28960pass` beside a red
  structural arm while S264 — the one mechanism that MOVES where a search
  starts — measures `corpus:178fail/28848pass`. The trio is a small
  experiment in which optimizations a corpus can police.
  Also worth reading: §1.2 on the encoding decline discharging TWO
  obligations with one test (`start_cls != NULL` is both "no mid-character
  start" and "one byte per character", the second of which is what lets
  `pcrec_cwmax`'s CHARACTER count stand as a BYTE count); §5.2 on D107's scan
  producing a fifth and a sixth NON-LIMIT kind; and §5.4 on why every claim
  in `tests/assertions/end_window.rxt` is carried at two subject lengths.
  **TRIAGE (b1triage, 2026-09-22, sonnet), appended to the same report**:
  batch 1's owed suite runs surfaced 13 reds in `make test` plus a FATAL
  `make test-axes` baseline. 12 of the 13 are ONE mechanism, confirmed
  before any fix by grepping each witness's own emitted `!memchr(...)`:
  [OPT-REQBYTE] short-circuits to nomatch before the give-up/exemption/
  divergence path under test ever runs, because six checks' witnesses
  deliberately omit the pattern's own required byte
  ([MECH-REACH] — `tests/cli` case15, `run_gen_timeout_tests.sh`,
  `run_vm_tests.sh` §4/§4.5/§4.7, `run_possessify_tests.sh` §3b,
  `run_mrldiff.sh`'s answer-more exemption, `run_island_tests.sh` §2.20).
  `-fno-req-byte` at each exact build site, six commits, no `src/` change.
  The 13th (`run_expansion_diff.sh`'s §6.3 population) is a REAL corpus
  move — batch 1's own `tests/assertions/end_window.rxt` (+13 blocks/+66
  cells) — re-derived and re-pinned with the corpus change named in the
  pin's own comment, per that check's stated instruction.
