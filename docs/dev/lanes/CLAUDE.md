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
