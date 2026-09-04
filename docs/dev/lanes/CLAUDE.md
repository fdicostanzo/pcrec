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
- `w13_runsh_composed_path.patch` — W1.3.1's starting point: lane w13's written-but-UNRUN run.sh composed-block path (dropped from lane/w13 at the manager's ruling 2026-09-04 04:3x because run.sh is the most load-bearing script in the tree and it would have landed behind three merges and a battery without its own make test). The dropped commit was 464f2896 in the w13 worktree's reflog; the patch is the durable copy. Its contract choice (the target's prefix through flush_block's tail vs the CLI allowance W1.2 refused) is Frank's question; report §18.
