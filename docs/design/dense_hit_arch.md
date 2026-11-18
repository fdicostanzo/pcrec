# The dense-hit remedy for the required-run handoff rows: architecture note
STATUS: ACCEPTED rev 2.1 (the manager, 2026-11-18: rev 2 after review r49, confirm critic conf-archdense "accept after small edits", its four edits applied by the manager; OPEN: the owner question lookahead-home, so U1's branch is REQ-OPEN; register proposals P1 and P2 ACCEPTED as proposals, P2 as ONE family, entered in the register at this note's landing) (lane archdense2, 2026-11-18; rev 1 by lane archdense, reviewed in
`docs/dev/reviews/2026-11-18-r49-archdense.md`, verdict NOT ACCEPTED, REVISE; every group A-L applied as ruled there)
FORM: full   (trigger: 7 existing decision sites touched (site map S1, S4, S6, S8, S9, S15, S16); mechanisms added: one new question at the kit's presence site (S6, U1), one new system-constant source (S7))
TREE: T = 57fcb5737dff37bd97429fb1e889ca0233d12e10 (unchanged from rev 1; no finding needed a later commit)   REQUIREMENTS: [REQ-PAST-LAST]'s three NOTES of 2026-11-12 @T; D144, D146, D147, D149, D151, D157, D158, D195 (docs/dev/decisions.md @T); [FLAG-DEMOTE], [LANDWALK], [REQRUN-VM] @T, [REQ-HANDOFF-L1] (plan_completed.md @T); `docs/spec/tuning.md` §2.41¶7a-¶9b @T; memfn/docs/requests.md R-30, R-41 and responses.md's R-30 notes @T; flag audit `docs/dev/flag_audit_2026-11-12.md` @T   REGISTER READ: `docs/dev/guide/architecture.md` register @T, and `docs/design/stream/roadmap.md` @T (register row 12)

Every command below runs from any checkout with `T=57fcb5737`; `GG` stands for `git grep -n` at `$T`
(`git grep -n PATTERN $T -- PATHS`), `GS` for `git show $T:PATH`. No command reads the working tree.

## Goals served

- **Goal 1 (one home per question).** The re-entry already has one text, `emit_req_landmark_move`, shared by its
  two consumers (S4). The feature changes it THERE and grows no consumer copy. Two questions are dispersed in the
  tree today. "Where does the search resume after a failure?" is answered in three slots (S3, S12, S13): proposed
  register row P1. "At this hit, ask the site, or run the next attempts unasked?" (the asking CADENCE, which is
  what this feature changes) has four built askers once the landmark walk is counted (S12, S13, S14 and the attempt
  loop S1): proposed register row P2, whose event is this feature.
- **Goal 2 (data with its owner; accessors elsewhere).** HELD. The feature writes the kit's `mf_site`/`mf_hooks`
  fields from pcrec (`req_site_define`, `emit_req_reentry_use`), and `memfn/include/memfn.h` is that seam's declared
  interface, so the access goes through the owner's declared contract. On the pcrec-owns branch of
  **lookahead-home**, B is a new pcrec constant, and its owner is a declared table (S7: `src/core/limits.def`, D90),
  never an emitter-local literal unless the design argues the precedent S7 names.
- **Goal 3 (seams).** The feature changes what crosses the pcrec-to-kit module seam (D146, D157). The question
  asked at the presence site gets a weaker contract (S6), and a system fact needs a home (S7). Facts only, no
  method.
- **Goal 4 (remodels ride along).** Twelve register rows are looked up (row 12 through nine roadmap areas). One
  remodel lands first: U1, the seam's reply contract, in one of two shapes (one per **lookahead-home** answer). The
  demotion half of the feature waits for register row 15's mechanism (the internal deny word).
- **Traded against: none.** Both **lookahead-home** answers can meet the gate. The open placement (which side of the
  seam states B) lies inside goal 3, not against it. The gate's real tension is the sparse-hit case (Register rows,
  the line under U1): a form that loses to today's per-hit move on sparse hits lands only with a lever.
- **The gate, in the owner's words** (2026-11-17, "speed-gate"; `GS docs/dev/guide/architecture.md | grep -n
  "closer to"`): "It's closer to "no existing regex should get slower" with the caveat that in practice a few
  percentage on rare forms was ok and a turn off option was allowed. Plus, it was fully acceptable if default off".
  Three allowances: a few percent on rare forms; a slowdown the user can turn off; anything off by default. THE
  RECORD'S READING of the two comparators (rev 1's owner question gate-comparator, now a statement): the gate
  governs every landing, so the remedy is compared with TODAY'S rows; NOTES 1-2 govern the demotion ("ONLY IF the
  method has no losing case"; "no case slower than the plain loop"), so the move off the public bit is compared
  with the rows DENIED. Both, for two decisions.

## Requirements read

The three NOTES of [REQ-PAST-LAST] (`scripts/entry REQ-PAST-LAST -l 2` @T), word for word, with ellipses where cut:

1. `NOTE (2026-11-12, Frank: "Queue that fix")`. The owner's words are "Queue that fix"; the body is the manager's
   QUEUED record: "QUEUED the dense-hit remedy for the handoff rows (bounded and unbounded): after the FIRST failed
   attempt, obtain the LAST occurrence of the required run at or after (known hit start + 1) ONCE (a kit request R-n
   stating that FACT only, D157: the kit chooses the method; a backward scan is cheap in RAM but defeats kernel
   readahead on cold mmapped subjects, a forward keep-latest pass reads in readahead order with no per-hit call; our
   timing covers warm data only, the cold case is argued, not measured), then each attempt compares its position
   with that number instead of re-asking the presence site. Expected: the dense-hit loss (1.38 vs 0.81 ms; bounded
   row 1.56 vs 0.71) goes away, after which the rows may move from the public -fno-req-handoff deny to a test lever
   (D195 / FLAG-DEMOTE) ONLY IF the method has no losing case (next NOTE)."
2. `NOTE (2026-11-12, no-loss condition)`: "no case slower than the plain loop (Frank 2026-11-12 on cold mmapped
   subjects): a backward scan loses on cold mapped tails, a forward keep-latest pass loses when a match comes early
   in a long subject with hits to its end; a lazy re-ask with doubling look-ahead ("any occurrence >= d bytes
   ahead?", d doubling on yes) reads forward, near the loop, with O(log) calls on dense hits, is the candidate with
   no constructed losing case. The request states the fact + the no-loss requirement; otherwise the public bit
   stays. Order: after reqpast lands, K38-2 and set S2; needs a measurement card (new method)."
3. `NOTE (2026-11-12, Frank: blocks instead of doubling, "also helps with streaming")`. The owner's quoted words are
   "also helps with streaming"; the rest is the record: "leading candidate = BLOCKED look-ahead: one presence
   question per block of B bytes ahead of the loop (yes: the block's attempts run unasked; no: scan forward to the
   next occurrence, end of subject stops); forward-only, at most one block ahead (stream- and readahead-friendly;
   doubling can demand unbounded look-ahead a stream cannot supply). B is a tuning constant: derive it from a SYSTEM
   constant (Frank): the stream's chunk when streaming, else the page size (sysconf(_SC_PAGESIZE), POSIX libc, or a
   build-time page constant if the measurement shows insensitivity; not the per-device /sys readahead window, not
   glibc-only cache sizes) and show insensitivity across that range in the measurement."

THE ARCHITECT'S READING (not a ruling). NOTE 2 is the owner's refutation of both methods NOTE 1's record names (the
backward scan loses on cold mapped tails, the forward keep-latest pass on an early match with hits to the end), and
it names a doubling candidate; NOTE 3 names blocks as the "leading candidate". Under D157 (and NOTE 1's own "the kit
chooses the method"), the METHOD is the kit's; this note carries no method as a ruling. The one owner-marked
constraint in NOTE 3 is "B is a tuning constant: derive it from a SYSTEM constant (Frank)", and it binds where a
method with a block size is chosen. The WHAT is shared by all three NOTES: stop past the run's last occurrence, do
not re-ask per hit on dense hits, lose no case. The skill's freeze rule (§3.2: "If the requirements are not stable
(... open owner questions that change WHAT the feature does), say so in the header; ... every site that depends on
an open requirement is marked `REQ-OPEN <slug>`") is met: the one open question, **lookahead-home**, changes WHERE
a fact lives, not WHAT the feature does.

THE RECORD'S READINGS (rev 1's questions, now statements; each with its quoted line):
- **streaming** ("also helps with streaming"): NOTE 3's own words answer it: "forward-only, at most one block ahead
  (stream- and readahead-friendly; doubling can demand unbounded look-ahead a stream cannot supply)" and "the
  stream's chunk when streaming, else the page size". That is SUBJECT streaming, which is not a feature at T:
  `match_api.md` §5.2¶6 says the API keeps "No partial-match or streaming window state", and [SUBST-STREAM] is
  deferred. The chunk is a future, unscheduled fact (D77: no hook built now). `docs/design/stream/` is the
  instruction-stream architecture, a different thing, touched only through the register (A-SEAM, A-PLAN).
- **scan re-entry**: NOTE 1's scope is "the dense-hit remedy for the handoff rows (bounded and unbounded)", the
  attempt rows. K105 is the forward scan's own issue with its own cause, owner row and trigger (`GS
  docs/dev/known_issues.md | grep -n "^## K105"`: "the hand-off re-entry's admission reads the byte-rate PRIOR only",
  "owned by [REQ-HANDOFF-L1]"). So the scan is not in this feature; it stays byte-identical, or its change is timed
  (a design constraint, S12).

VOCABULARY (each grepped at T; hit counts are in the command list):
- rows and payload: `handoff-attempts`, `handoff-attempts-entry`, `handoff-attempts-unbounded` (FIRST slot of
  `cand_rows[]`, executor `cand_select`); `CandUse.whole`, `CandUse.reenter`; `REQ_USE_HANDOFF`; NEXT's
  `handoff-reentry`; RETRY's `adaptive-dense`; LOCATE's `landmark-walk`.
- predicates: `req_handoff_vm_run`, `req_handoff_entry_applies`, `req_handoff_attempts_applies`,
  `req_handoff_unbounded_applies`, `req_parts_in_whole`, `req_reentered`, `pf_handoff_applies`,
  `req_landmark_admits`, `pcrec_landmark_margin`, `cand_rs_dense_applies`, `req_start_set`.
- emission: `emit_req_handoff_rest`, `emit_req_landmark_move`, `emit_req_reentry_use`,
  `pcrec_emit_req_attempt_reentry`, `pf_emit_handoff`, `emit_landmark_walk`, `pcrec_req_site_in_prefilter`;
  emitted locals `landmark_position`, `handoff_position`, `attempt_position`, `search_from`.
- facts and K: `req_handoff_k`, `pcrec_fact_req_whole_run(...)->whole_maxoff`, `PCREC_W_UNBOUNDED`.
- kit seam: `req_site_define`, DELEG_SITES rows `PRE` and `LMHIT` (`src/gen/memfn_sites.def`, columns handoffs,
  budget `DELEG_SCAN`/`DELEG_LOOP`, use ceiling), `mf_site.use` / `mf_use_kind`, the define-phase fields `op`,
  `handoff`, `ret_pred`, `on_miss_leaves` (`memfn/src/fields.def`), `mf_site.head_max`, `MF_HEAD_MAX_UNBOUNDED`,
  `MF_H_ASSIGN`, `MF_H_ON_MISS`, `mf_site.ret_pred` ("the leftmost hit"), `mf_hooks.n` (the read limit, C text),
  `mf_hooks.lo`, `on_miss`; the rows' serves tables (`[FLD_ret_pred]`, `[FLD_on_miss_leaves]`, `[FLD_n]`) read by
  `gate_check`.
- options and stamps: `PCREC_NO_REQ_HANDOFF` (bit 46, `-fno-req-handoff`), `RX_REQ_HANDOFF` / `req_handoff_stamp`.
- driver: `Job.req_handoff_vm`, `Ctx.req_handoff_dropped`, the `drop-handoff` rung of `fit_rungs[]`.
- constants: `src/core/limits.def` (D90), `vm_reseed_cal` (src/gen/emit_vm.c).
- ZERO HITS (new): a system page size (`sysconf|_SC_PAGE|PAGE_SIZE|getpagesize`, 0 hits in src cli lib memfn/src),
  a subject stream chunk (`-i -w chunk`, 0 hits in src/gen memfn/src). Both belong to S7.

REQ-OPEN items: **lookahead-home** (S6, S7, U1).

## Site map

| # | site (file, function or table) | command (at T) | today | class | goal/rule |
|---|---|---|---|---|---|
| S1 | `cand_rows[]` FIRST rows `handoff-attempts` and `handoff-attempts-unbounded`, src/gen/emit_dfa.c (executor `cand_select`) | C1 | the two attempt-loop rows that re-enter (`.reenter = true`, `.whole = true`), deny `PCREC_NO_REQ_HANDOFF`; their `desc` states the per-hit re-ask; their predicates read no rate, prior or margin (C19) | ROW: the remedy changes what these rows do after a failed attempt, with no new choice in the table | goal 1; Decisions are declared tables; A row checks its own contract |
| S2 | `cand_rows[]` FIRST row `handoff-attempts-entry` | C1 | moves the first attempt only; no re-entry | AS-IS: nothing is re-asked per hit, so the dense-hit loss does not exist on it | goal 1 |
| S3 | `CandUse.reenter`, src/gen/emit_dfa.c `typedef struct CandUse`, read by `req_reentered` | C5, C17 | a bool: whether the row re-enters after each failed attempt | AS-IS while the remedy REPLACES the per-hit re-ask (whether to re-enter stays the row's; how is the text's). It becomes WIDEN, and A-SEAM's step then P1 land first, if the design keeps two re-entry forms selectable (see the line under U1) | goal 1; One question, one primitive |
| S4 | `emit_req_landmark_move`, src/gen/emit_dfa.c, the one re-entry text of two consumers (`pf_emit_handoff`, `pcrec_emit_req_attempt_reentry`) | C2 | re-asks the pre-check when the kept hit is behind the position, then moves to the hit less K where K is finite; it branches on `k >= PCREC_W_UNBOUNDED` and on `f` (the forward scan's form: a consumer-stated fact, the precedent for a parameter path) | SHARED: already the one home. The remedy is written here, never as a copy in one consumer. A branch on WHICH consumer calls is the aggregation to avoid; a fact the consumer states (like `f`) is not | goal 1; One question, one primitive; Build the general form |
| S5 | `pcrec_emit_req_attempt_reentry`, src/gen/emit_dfa.c; called from the VM retry in src/gen/emit_vm.c | C3 | runs after the encoding's advance and before the start-set seek, on each failed attempt | AS-IS: "after the first failed attempt" is this point; the call does not move | goal 3 (an existing cross-emitter call, H-HEADER) |
| S6 | the presence site's second use: `emit_req_reentry_use` (src/gen/emit_dfa.c) on the site `req_site_define` defined for the entry (DELEG_SITES row `PRE`); kit reply contract `mf_site.ret_pred`, memfn/include/memfn.h | C4, C10, C18, C20, C21 | the re-entry REUSES the entry's one site (`pre->site`, `pre->handle`) from another lower bound, reads to `subject_length`, ASSIGNs the LEFTMOST hit to `landmark_position`; a miss is NOMATCH. The question's shape is DEFINE-phase: `op`, `handoff`, `ret_pred`, `on_miss_leaves` are `MF_PH_DEFINE` (C18); `req_site_define` sets `s->use = MF_USE_ENTRY` ("the presence verdict's use"), and `mf_use_kind` says ENTRY is "An ALL_PRESENT site's only (refused elsewhere)" (C20). DELEG_SITES `PRE` declares handoffs ON_MISS and ASSIGN, kinds SET and RUN, budget `DELEG_SCAN` ("the ONE source of MF_P_INLOOP"), use ceiling `MF_USE_ENTRY` (C21), although the re-entry asks it once per passed hit inside the attempt loop | WIDEN: the reply's contract covers the leftmost hit only ("RETURN/ASSIGN the leftmost hit of preds[ret_pred]"). The remedy needs a weaker question, and the entry's bounded move still needs the leftmost from the same site. So the weaker question is either a per-use fact or kind (a define-phase field moved to use phase, or a new `mf_use_kind` value: an `MF_SITE_ABI`/`MF_VOCAB` move), or a second define of the site (a pcrec mover inside the feature). The candidate homes split by REQ-OPEN **lookahead-home** (U1-k, U1-p); this note picks none (the design's and the kit's choice). The `budget` column's value for an in-loop use is the design's to state. The hazard population is the rows' serves declarations and the checks that assert the leftmost (C10), not the renderers | goal 3; A module seam is an API with a written contract; Across the kit boundary, send facts |
| S7 | the source of B, the block size of the owner's leading candidate: a system page size, or a stream chunk | C8, C9, C22 | nothing: 0 hits for either at T; `match_api.md` §5.2¶6, no streaming state | NEW-SEAM: a new fact, and the side that states it is open (REQ-OPEN **lookahead-home**). Kit branch: the home is the kit's; D146 addendum 1's target table holds ISA facts ("families, targets, features, the region and guard text, the run-time CPU predicate, the host default"), and whether it would hold the page size is the kit's answer. pcrec branch: B is a `limits.def` row (D90: "a new number is a table row, never a bare `#define`"; 81 rows, kind "selection knee" among them) unless the design argues the emitter-table precedent (`vm_reseed_cal` in src/gen/emit_vm.c, whose comment cites D103 and the `clskit.c` PLACE precedent); its value and derivation are the design's (D149) | goal 2; goal 3; Tuning constants are suspect |
| S8 | `req_parts_in_whole`, src/gen/emit_dfa.c: the linearity conjunct of both re-entering rows | C16 | admits the row only where every part of the pre-check is a byte or slice of the whole run, "so re-asking the site after every failed attempt keeps the search linear" | ROW: a conjunct of existing rows whose stated reason assumes the per-hit re-ask. The design re-argues it for the new form, and may keep or drop it | goal 1; A row checks its own contract |
| S9 | the deny: `PCREC_NO_REQ_HANDOFF` (lib/pcrec.h bit 46, src/core/axes.def), the deny column of 5 rows, 5 world reads (`.under`/`.by`) in `cand_nodes[]`, and the forced deny in `req_start_set` | C7 | ONE public bit denies all five handoff rows (`handoff`, the three attempt rows, NEXT's `handoff-reentry`); `req_start_set` ORs the bit in to ask NEXT's start row with the handoff denied (it feeds `req_landmark_admits`, S15); the flag audit KEEPS bit 46 for K88's loss | ROW (the rows' deny column), plus one code read (`req_start_set`) a split deny must re-aim. The split itself is a conditional confirm handed to the design step | goal 1; public deny only if slower (Frank 2026-10-29, D195) |
| S10 | `req_handoff_stamp` (`RX_REQ_HANDOFF`), src/gen/emit_dfa.c; `match_api.md` §6.3.7¶11 | C11 | the value is K, `"unbounded"` or `"none"` | AS-IS: the value does not change. The spec SENTENCE describing the re-ask changes (D80, under Seams) | goal 3 |
| S11 | the `drop-handoff` rung of `fit_rungs[]` (src/core/compile.c) reading `Job.req_handoff_vm`; `Ctx.req_handoff_dropped` | C6, C13 | after a size-cap refusal, retries without the attempt rows; the emitter writes the flag back to the driver (register row 6c, a noted deviation) | AS-IS: the remedy's text is inside what the rung drops, and the feature adds no emitter-to-driver fact | goal 3 (layer direction; 6c) |
| S12 | NEXT row `handoff-reentry` (predicate `pf_handoff_applies`, S15), the forward scan's re-entry through S4 | C15 | re-enters only at the DFA's start state with nothing accepted; re-asks per passed hit, ADMITTED by a prior margin (S15) | SHARED with S4: its code is untouched, but its BYTES depend on S4's decision, so "the forward scan stays byte-identical (or its change is timed)" is a design constraint (the scan-re-entry reading, above). K105 is that admission's failure on text denser than its prior | goal 1; Notice siblings |
| S13 | RETRY rows (`exact` ... `adaptive-dense`), src/gen/emit_dfa.c: "where the next attempt resumes" behind a prefilter | C14 | `adaptive-dense` (predicate `cand_rs_dense_applies`: the start-set rate times `reseed_gap` from `vm_reseed_cal`) starts inside a capped step block | AS-IS (a sibling, not touched). It is the third home of the resume question (P1) and a member of the cadence family (P2) | goal 1; Notice siblings |
| S14 | the landmark walk: LOCATE row `landmark-walk` (`cand_rows[]`), its emitter `emit_landmark_walk`, delegated site DELEG_SITES `LMHIT` (FIND, ASSIGN), its own `size_t landmark_position = search_from;` and its density row `pcrec_landmark_margin` in src/gen/lmwalk.c | C12, C19 | BUILT at T ([LANDWALK] stage 1; the plan tag still reads not-started): asks the kit's FIND site from one past each hit, ascending, once per hit, admitted by the same prior margin function as S15 | AS-IS: it keeps asking the leftmost hit and the feature does not touch it. It is the fourth built asker of the cadence family (P2) and an unlock with its trigger | goal 1; Notice siblings |
| S15 | the forward scan's DENSITY ADMISSION: `pf_handoff_applies` ends in `req_landmark_admits`, which returns `pcrec_landmark_margin(...) > 0` over the byte-rate prior (`pcrec_find_byte_rate`); `req_landmark_admits` also prices NEXT's "landmark" pick | C19 | the scan consumer of S4 re-asks per hit only where the prior says the landmark is sparser than K; the attempt rows (S1) have no density conjunct | ROW: a conjunct of the scan's row. With the feature, ONE shared text (S4) has a prior admission on one consumer and a prior-free rule on the other: two answers to one dense-hit question, disposed by P2 (with K105's trigger) | goal 1; Notice siblings; One question, one primitive |
| S16 | the kept hit's DECLARATIONS: `emit_req_handoff_rest` (src/gen/emit_dfa.c; `size_t landmark_position = handoff_position;` where `req_reentered`, and branches on `whole` and on K), and the VM hybrid prefilter's own `size_t landmark_position = search_from;` (src/gen/emit_dfa.c, under `pcrec_req_site_in_prefilter`); the walk's declaration is S14's | C23 | three sites declare the state the remedy changes (two here, one in S14) | SHARED with S4: the declaration and the use of one kept state; the remedy's change to what is kept is made once, read by every declaration that serves the re-entry | goal 1; One question, one primitive |

COMMANDS (each at `$T`, from the repository root; hit counts as printed at T):
- C0 (premise): `git grep -n "handoff-attempts-unbounded" $T -- src docs/spec` gives 7 lines (match_api.md, tuning.md,
  compile.c, internal.h, emit_dfa.c three times); `git merge-base --is-ancestor f6365477c $T` exits 0.
- C1: `GG '"handoff-attempts' $T -- src/gen/emit_dfa.c` gives 7: the three FIRST rows' names and `.list` names, and
  the BOUND read's site label in `req_handoff_vm_run`.
- C2: `GG "emit_req_landmark_move(" $T -- src` gives 4: the declaration, the definition and two callers
  (`pf_emit_handoff`, `pcrec_emit_req_attempt_reentry`).
- C3: `GG "pcrec_emit_req_attempt_reentry(" $T -- src` gives 3: internal.h, emit_dfa.c, and emit_vm.c (the VM retry).
- C4: `GG "emit_req_reentry_use(" $T -- src` gives 2: the definition and its one caller, in S4. The reuse of the
  entry's site: `GS src/gen/emit_dfa.c | grep -n "pre->handle, &h"` gives 2, the entry's use and the re-entry's use
  of one handle.
- C5: `GG -w "reenter" $T -- src` gives 4: the field, `req_reentered`'s read, and the two rows that set it.
- C6: `GG -E "req_handoff_vm|req_handoff_dropped" $T -- src` gives internal.h (`Job`, `Ctx`), compile.c (the rung's
  reader and the retry's writer), and emit_dfa.c (the writers `emit_req_handoff_rest`, `pf_emit_handoff`; the
  readers `req_handoff_vm_run`, `pf_handoff_applies`).
- C7: `GG "PCREC_NO_REQ_HANDOFF" $T -- src cli lib memfn/src` gives 13: lib/pcrec.h bit 46, axes.def, five row
  denies (the `.c = {...}` initialisers of the five handoff rows), five world entries in `cand_nodes[]`
  (`.under` three times, `.by` twice), and one code read, `req_start_set`'s `cand_select(CAND_SLOT_NEXT, s,
  cx->opt->flags | PCREC_NO_REQ_HANDOFF)`.
- C8: `GG -E "sysconf|_SC_PAGE|PAGE_SIZE|getpagesize" $T -- src cli lib memfn/src` gives 0.
- C9: `GG -i -w "chunk" $T -- src/gen memfn/src` gives 0.
- C10 (S6's hazard population, replacing rev 1's file count of `MF_H_ASSIGN` mentions, which mixed declarers,
  FIND-only files and renderers):
  (i) the serves declarations: `GG '\[FLD_ret_pred\]' $T -- memfn/src` gives 12 lines in 9 files (finder, generic,
  mismatch, ofsskip twice, pffind, precheck three times, runcmp, vrun, window); `gate_check` (memfn/src/gate.c)
  declines any stated class outside a row's `serves`, so a new field or class is fail-closed until every row
  declares it;
  (ii) the checks that assert the LEFTMOST: `GG -i "leftmost" $T -- memfn/tests/g2/g2_ref.c
  tests/memfn/run_arm_pins.sh` gives 3 (g2_ref.c's reference "the LEFTMOST position of predicate ret_pred (as FIND
  would return it)", run_arm_pins.sh's two ALL_PRESENT/ASSIGN pins), and `GG -E "RETURN/ASSIGN the leftmost
  hit|LEFTMOST position of predicate|is the leftmost position in" $T -- docs/design/memfn/integration.md` gives 3;
  (iii) the ALL_PRESENT ASSIGN renderers: `GG "MF_H_ASSIGN" $T -- memfn/src/precheck.c memfn/src/generic.c`; under
  a WEAKER contract none breaks (a leftmost answer is an occurrence at or after lo);
  (iv) the field comment: `GG "ret_pred" $T -- memfn/include/memfn.h` ("ALL_PRESENT: RETURN/ASSIGN the leftmost").
- C11: `GG "req_handoff_stamp" $T -- src` gives the declaration, the definition and the one stamp writer.
- C12 (S14): `GG -E '"landmark-walk"|DELEG_SITE\(LMHIT|^static void emit_landmark_walk|size_t landmark_position =
  search_from' $T -- src` gives the LOCATE row (four lines of its initialiser), `DELEG_SITE(LMHIT, MF_OP_FIND,
  DELEG_H(MF_H_ASSIGN), ...` in memfn_sites.def, `emit_landmark_walk`'s declaration and definition, and two
  `landmark_position = search_from` declarations (the walk's, and the hybrid prefilter's, S16). The walk's pin row:
  `GG LMHIT $T -- tests/memfn/site_manifest.tsv` ("every occurrence of the landmark's byte set at or after the
  position given, ascending ... used once per hit; its miss is the search's NOMATCH"). The stale tag:
  `GS docs/dev/plan.md | grep "^- \[LANDWALK\]"` reads STATE:not-started.
- C13: `GG '"drop-handoff"' $T -- src/core/compile.c` gives 1, the rung in `fit_rungs[]`.
- C14: `GG '"adaptive-dense"' $T -- src/gen/emit_dfa.c` gives 3, all on the one RETRY row (its name, token and `.list`
  entry); its predicate: `GS src/gen/emit_dfa.c | grep -n -A1 "^static bool cand_rs_dense_applies"` (the start-set
  ppm times `s->vm->reseed_gap`); `GG "vm_reseed_cal\[" $T -- src` gives 3 in emit_vm.c.
- C15: `GG "pf_handoff_applies" $T -- src` gives 2: the predicate and the NEXT row `handoff-reentry`.
- C16: `GG "req_parts_in_whole(" $T -- src` gives 3: the definition and the two re-entering rows' predicates.
- C17: `GG "req_reentered(" $T -- src` gives 4: the declaration, the definition, and the readers in
  `emit_req_handoff_rest` and `pcrec_emit_req_attempt_reentry`.
- C18 (S6, define phase): `GS memfn/src/fields.def | grep -n -E 'MF_FIELD\((handoff|op|ret_pred|on_miss_leaves)\b'`
  gives 4, each `MF_PH_DEFINE`. The rows' coverage of a non-leaving miss: `GG -E
  '\[FLD_on_miss_leaves\]|\[FLD_n\] *= CM\(IDENT\)|\[FLD_on_miss\] *=' $T -- memfn/src/precheck.c` gives
  `CM(YES)`, `CM(IDENT)` and `CM(JUMP) | CM(BRACED)`; memfn.h's `on_miss_leaves` comment admits 0 ("it may fall
  through").
- C19 (S15, S1, S14): `GG -E "req_landmark_admits\(|pf_handoff_applies\(" $T -- src` gives 4 (the admission's
  definition, `pf_handoff_applies`' definition, its call there, and a fourth call pricing NEXT's "landmark" pick);
  `GG "pcrec_landmark_margin(" $T -- src` gives 4 (internal.h, emit_dfa.c's definition and its call in
  `req_landmark_admits`, and src/gen/lmwalk.c's `st->margin = pcrec_landmark_margin(...)`). The attempt rows'
  predicates (`req_handoff_vm_run`, `req_handoff_entry_applies`, `req_handoff_attempts_applies`,
  `req_handoff_unbounded_applies`): `GS src/gen/emit_dfa.c | grep -n -A6 "^static bool req_handoff_"` shows no rate,
  prior or margin read.
- C20 (S6, use kind): `GG "mf_use_kind;" $T -- memfn/include/memfn.h` gives the enum `MF_USE_POSITION,
  MF_USE_DISCARD, MF_USE_ENTRY`; `GG "s->use = MF_USE_ENTRY" $T -- src/gen/emit_dfa.c` gives 2 (one in
  `req_site_define`).
- C21 (S6, the site row): `GG "DELEG_SITE(PRE," $T -- src` gives 1 in memfn_sites.def; the column legend:
  `GS src/gen/memfn_sites.def | sed -n 8,33p` (budget "the ONE source of MF_P_INLOOP").
- C22 (S7): `GS src/core/limits.def | grep -c '^PCREC_LIMIT('` gives 81; `GG "vm_reseed_cal\[" $T -- src` (C14);
  `GG "The target table (families" $T -- docs/dev/decisions.md` (D146 addendum 1).
- C23 (S16): `GG -E "^static void emit_req_handoff_rest|landmark_position = handoff_position" $T -- src` gives 2;
  `GG "pcrec_req_site_in_prefilter(" $T -- src` gives 5 (internal.h, its definition, two emit_dfa.c callers, the
  second the `else if` before the prefilter's declaration, and emit_vm.c's).
- WITNESS of the emitted text (illustration only, run in rev 1: the main tree's `build/pcrec`, built 2026-11-15
  from main, not from T; the git commands above are the evidence): `timeout 60 build/pcrec -p rx --engine=vm -o
  OUT.c --pattern '[^@ ]+@x'` stamps `RX_REQ_HANDOFF "unbounded"`. Its retry has `if (landmark_position <
  attempt_position) { landmark_position = rx_reqrun(subject, subject_length, attempt_position); if
  (landmark_position >= subject_length) return 0; }`. The same with `[^@ ]{1,5}@x` stamps `"5"` and has the same
  re-ask followed by the move. These are the two cells `tuning.md` §2.41¶8c measures (1.38 against 0.81 ms, and
  1.56 against 0.71 ms; MEASURED BEFORE K38-2: the row's `waits:` line owes "a re-measure of tuning.md §2.41¶8c's
  timings, which predate K38-2").

## Register rows looked up

Searches run at T: `GS docs/dev/guide/architecture.md | grep -n -E
"emit_dfa|emit_vm|compile.c|internal.h|cand_rows|req_handoff|memfn|lmwalk|limits.def|REQ-PAST-LAST|FLAG-DEMOTE"`.
Then `docs/design/stream/roadmap.md` (register row 12) for the same files, functions and tag: `GS
docs/design/stream/roadmap.md | grep -n -E "Ride-along triggers|^### "`, each area's WHERE and trigger read. Then
`scripts/entry -g` for D-row "Revisit when" triggers naming `req_handoff`/`emit_req_`; none matched, because the
decisions profile is dormant (rev 1's lane report). Each disposition answers the row's or area's ride-along
TRIGGER line.

| register row | why it matches | disposition |
|---|---|---|
| 1 (start-table rows carry their act) | `cand_rows[]`; the `cand_finish_of(cx) == CAND_ROUTE_VM` tests (`req_reentered`, `pf_emit_handoff`) | NOT CARRIED: the feature adds no recover or finish act and no new route test; the design must keep it so (it reads `req_reentered`, it does not re-test the route) |
| 2 (engine identity asked one way) | `pcrec_artifact_has_dfa_scan` / `cand_route_of` reads in S3, S5, S12 | NOT CARRIED: no new reader of engine identity |
| 3 (refusal table, [FLAG-DEMOTE]) | the same option word | NOT CARRIED: the feature adds no refusal |
| 6a (Job/Ctx writer and readers) | `Job.req_handoff_vm`, `Ctx.req_handoff_dropped`, `cx->job->mf_pre` | NOT CARRIED: its event is "the next feature that adds an emitter-to-driver flag"; this one adds none |
| 6c (NOTED DEVIATION: emitter-written facts the driver re-plans on; `req_handoff_vm` named) | S11 | NOT CARRIED, reason: L, an abi/spec event for the caps' unit, whose events are [VMREC] and roadmap H-FLAGS. The feature adds no back-flow, and its text stays inside what `drop-handoff` drops. The correction still waits for its event |
| 7b, 9, 10, 19 | they name emit_dfa.c / emit_vm.c / memfn | NOT CARRIED: no post-render rewrite (7b), no emitter split (9), no CandRow offset (10), no new declared table (19; P2 would be one, under its own event) |
| 12 / roadmap A-SEAM | its trigger line names the TAG: "[CAND-SPAN] ...; [GIVEUP-DIFF]; [START-DENSE]; [REQ-PAST-LAST]; ..." (`GS docs/design/stream/roadmap.md | sed -n 132,134p`); its next step moves the hand enum, `CandNode` and the row/hand types into a seam header, byte-identical | NOT CARRIED as a unit of this feature, reason: the step is a pure move of types this feature does not change (the remedy as architected changes no field of `CandUse`/`CandRow`, S3 AS-IS; the demotion half changes deny VALUES in `cand_rows[]`/`cand_nodes[]` cells, not a type), so it has no dependency on this feature and is carried by its own event. EXCEPTION, restated: if the design keeps a second re-entry form selectable (the line under U1), S3 becomes WIDEN and A-SEAM's step lands first, ahead of P1 |
| 12 / roadmap A-PLAN | trigger line: "[COVER-PRICE-WITNESS]; [PILOT-SIMD]; [PRICE-BAKEOFF]; any R-n that changes how a site is chosen" (`GS docs/design/stream/roadmap.md | sed -n 474,475p`) | MANAGER'S RULING (r49, group F), applied: U1 alone (a widened reply contract with zero movers) does NOT change how a site is chosen and does not fire it. The CONSUMER step fires it IF the kit's answer to the new question changes which site or method is chosen. That decision is handed to the design step, with the kit (under "What the design step must decide") |
| 12 / roadmap A-HYB | WHERE: the VM hybrid prefilter window and retry; the feature edits the VM retry (`GG "pcrec_emit_req_attempt_reentry(" $T -- src/gen/emit_vm.c`), and S12/S16 inside a hybrid are gated by `pcrec_req_site_in_prefilter` (C23); trigger line names [K88-HANDOFF-DENSE] (`... sed -n 153,154p`) | NOT CARRIED, reason: the attempt-loop rows apply only where no DFA scan is in front (`<PREFIX>_VM_PREFILTER "none"`, `tuning.md` §2.41¶8b), so the remedy changes no hybrid prologue byte; the hybrid's re-entry (S12/S16) stays byte-identical under the scan constraint. If the design cannot keep S16's hybrid declaration byte-identical, A-HYB's P-c step is looked up again |
| 12 / roadmap H-SITES | WHERE: `src/gen/memfn_sites.def`, `tests/memfn/site_manifest.tsv`, `tests/memfn/c4_allowlist.tsv`; declared shape "A new site appends one `DELEG_SITE` row" (`... sed -n 549,566p`) | RIDES on U1-p only, if the design takes the second-define shape (a second `PRE`-like row appended in the declared shape, with its pins); NOT CARRIED on U1-k (no new site) |
| 12 / roadmap A-READS | WHERE names `CandNode.under/by` (S9) | NOT CARRIED, reason: only the demotion half touches those cells, and it rides row 15's mechanism, not this feature's unit |
| 12 / roadmap H-ABI | trigger line: "Every byte-moving change; [STAMP-REVIEW]; [IFACE-PUSH]" (`... sed -n 583p`) | CARRIED by construction: the emitted retry text moves, so the feature is an abi bump with its readers found by grep (D76/D94), the feature's own event |
| 12 / roadmap H-COUNTS | WHERE lists `manifest_s2_vm_auto.tsv`, `manifest_s2_vm_forced.tsv`, `run_axes.sh`, `run_registry_tests.sh`; trigger "the next change that re-pins any of them" (`... sed -n 589,602p`) | CARRIED where it fires: the design-step grep (C-HANDOFF below) prints both s2_vm manifests and run_axes.sh; any of them the landing re-pins is re-pinned by the mover census in the same change |
| 12 / roadmap H-FLAGS, H-LADDER | `req_handoff_vm`; `drop-handoff` | NOT CARRIED: no new flag and no new droppable row |
| 13 ([VMREC] (b)/(c), riding) | src/gen/emit_vm.c | NOT CARRIED: steps (b) and (c) are not started at T (`scripts/entry VMREC -l 1`), so no refactor is in flight on the retry text. If one starts first, it outranks this feature on emit_vm.c's retry (Refactors outrank optimization) |
| 15 (internal deny word, riding [FLAG-DEMOTE]) | S9: the attempt rows can leave public bit 46 only through an internal deny | RIDES ROW 15'S MECHANISM: the DEMOTION half (NOTE 1's conditional move to a test lever) uses the internal deny word once row 15 lands. It does NOT join [FLAG-DEMOTE]'s ruled set: D195's set is "the 20 confident demotions" and the flag audit marks bit 46 KEEP. The remedy half does not need it (separable) |

Noted deviations on touched sites: one, 6c, disposed above. This note recommends no deviation, so it proposes none.

ROWS THIS NOTE PROPOSES (register columns; PROPOSALS, the manager decides at acceptance):

| # | remodel | shape (rule) | where | event that carries it | size, gate | deletes | status |
|---|---|---|---|---|---|---|---|
| P1 | One home for "where the search resumes after a failure": the VM attempt loop's re-entry (FIRST's `CandUse.reenter` plus `pcrec_emit_req_attempt_reentry`), the forward scan's re-entry (NEXT `handoff-reentry`) and the hybrid retry (RETRY rows, `adaptive-dense`'s step block) answered by one slot's rows and acted through the row. This is the guide's implement-then-replace open row for the resume question | Notice siblings (three homes); One home per question (goal 1); Act through the row | `CandUse.reenter` and `req_reentered` (C5, C17); `emit_req_landmark_move` (C2); RETRY rows (C14), src/gen/emit_dfa.c; the VM retry in src/gen/emit_vm.c (C3) | a SECOND re-entry form selectable on any of the three (S3 becomes WIDEN; this includes a per-hit lever kept beside the remedy, the line under U1), or [START-DENSE], or a fix for K105 or K88 | M, no-mover | the `reenter` bool, the consumer branch in `emit_req_landmark_move`, the VM-only route's private retry spelling | open |
| P2 | One declared rule for the asking CADENCE, "at this hit, ask the site, or run the next attempts unasked?": the scan re-entry's admission (`pf_handoff_applies` / `req_landmark_admits`, a prior margin, S15), the landmark walk's margin (`pcrec_landmark_margin` in lmwalk.c, S14), RETRY's `adaptive-dense` (a capped step block admitted by the start-set rate times `vm_reseed_cal`'s gap, S13), and the attempt loop's new rule (this feature, S1/S4) as rows of one table with their inputs declared | Notice siblings ("At about three dispersed members, propose the unified table"; this is the fourth); Decisions are declared tables; One question, one primitive | S15, S14, S13 and S4's new rule; `pcrec_landmark_margin` (C19), `cand_rs_dense_applies` and `vm_reseed_cal` (C14) | THIS FEATURE (its design step states the new rule as the table's row, the other three rows byte-identical); a K105 fix (the scan's admission) re-uses it | M; the existing three rows no-mover with byte identity, the new row under the feature's own gate | three dispersed rule spellings become rows of one table; the scan and attempt-loop consumers of S4 stop carrying two unrelated answers on one text | PROPOSED |

THE BEST ARGUMENT THAT THE ROUTES' RULES ARE NOT ONE FAMILY (so the owner sees both sides; the architect's leaning
is P2). The four rules answer at different TIMES and with different ACTS. The scan's admission and the walk's margin
are COMPILE-TIME admissions: they decide whether a row is selected at all, from a prior, and once admitted they ask
per hit for the whole search. `adaptive-dense` is a RUN-TIME capped step inside one selected row, sized by a
calibration constant. The new rule is a RUN-TIME cadence whose leading candidate the owner wants with NO prior and no
adaptivity (NOTE 3; and run-time adaptive switching "has not proved its worth"). A table whose rows mix compile-time
selection with run-time cadence would declare inputs (a prior) that one row must not read, and would join a
selection mechanism to an emitted loop shape; the honest unit might then be "one function per time", not one table.
THE REJOINDER (review r49, group A): the owner's no-prior NOTE argues the new ROW's predicate, not a separate
mechanism, and two of the four rules (the scan admission and the walk) already share one function (`pcrec_landmark_margin`); a table
can declare per-row inputs. Which is right is the manager's call at acceptance.

## Remodels that land first

**U1: the presence site states the question its caller needs (S6).** One unit, in ONE of two shapes chosen by the
**lookahead-home** answer; it is not built until that answer is in. The facts and the question are pcrec's; how it
is answered is the kit's (D157). pcrec PROPOSES the request texts below and files nothing.

**U1-k (the answer: the kit owns how the position is obtained).**
- What changes shape: the reply contract gains one stated question, "an occurrence at or after lo, which one is the
  kit's choice", PER USE (the entry's use keeps the leftmost from the same site, S6). Candidate homes, none picked: a
  define-phase field moved to use phase (an `MF_SITE_ABI` move), a new `mf_use_kind` value (an `MF_VOCAB` move), or a
  second define of the site (a pcrec mover).
- Gate: kit seam event (D146): `MF_SITE_ABI`/`MF_VOCAB` meaning. Zero pcrec movers GIVEN a serves entry in every row
  for the new field or class (C10 (i): `gate_check` fails closed, so the D157 precedent's conclusion, "Zero pcrec
  movers ... until a kit row consumes it", holds, but not its reason: the gate reads the field). The seam
  precedent's own instruments (`GS docs/design/memfn/integration.md | sed -n 528,535p`): every `emit_sweep` stream
  byte-identical against the parent at both comment tiers and every axis; `arms.tsv` pins unchanged; G2 quick
  unchanged.
- Size: S.
- Checks that bind it: the kit's G2 (`make test-memfn-g2`, presence cases), `mf_vocab_has`, the presence deny run
  `tests/memfn/run_presence.sh` over `tests/litscan/presence_deny.rxt`; the 12 `[FLD_ret_pred]` serves declarations
  (C10 (i)); the checks that assert the leftmost (C10 (ii)), which stay true for the entry's use and must not be
  read as binding the new one.
- Separable: yes. It lands with no caller asking the new question, answer- and byte-identical.
- Speed gate: byte-identical artifacts are the proof.
- Deletes: nothing. Its reason is the feature's need, a seam shape that does not hold the question (rule "A shape
  states the inputs it covers").

**U1-p (the answer: pcrec's loop owns the look-ahead and B).**
- What changes shape: the needed question is ALREADY in the contract: ALL_PRESENT with ON_MISS or ASSIGN on
  `[lo, n)` is in `PRE`'s declared handoffs (C21), and memfn.h admits a non-leaving ASSIGN miss (`on_miss_leaves` 0,
  C18). What declines it is ROW COVERAGE: the pre-check rows serve `[FLD_on_miss_leaves] = CM(YES)` only and `[FLD_n]
  = CM(IDENT)` only (C18). So: a kit ROW event (rows serving a non-leaving miss, or none if an `on_miss` jump
  suffices), plus pcrec movers inside the feature: the read limit as a new emitted local (a bare identifier, since
  `n` is served as IDENT only), and either a per-use change or a second define of the site (whose `use` would still
  be forced to `MF_USE_ENTRY`, C20: SUSPECTED that this touches `mf_use_kind`'s meaning; the kit confirms).
- Gate: kit ROW event (row coverage), byte-identical with no caller (the same instruments as U1-k); the pcrec
  movers land WITH the feature under its abi event, not as a no-mover unit.
- Size: S (kit rows) plus the feature's own movers.
- Checks that bind it: as U1-k, plus `tests/memfn/site_manifest.tsv` and `c4_allowlist.tsv` if a second site row is
  appended (H-SITES).
- Separable: the kit row event, yes (no caller states the new coverage); the pcrec movers, no (they are the
  feature).
- Deletes: nothing.

A design-step REQUIREMENT on both shapes (manager's ruling, r49 group D): the G2 reference for the new question is
written by a D27-blinded kit author at the DESIGN step (the existing reference encodes the leftmost, C10 (ii)).

PROPOSED REQUEST TEXTS (for the manager to file as the next R-n, ONE per **lookahead-home** answer; this lane files
nothing; facts and both comparators only; no method):

- TEXT FOR U1-k (assumes **lookahead-home** = the kit owns how the position is obtained): "FACT. [REQ-PAST-LAST]'s
  re-entering attempt rows (`handoff-attempts`, `handoff-attempts-unbounded`) use the pre-check site (DELEG_SITES
  `PRE`, ALL_PRESENT, ASSIGN) a second time, after each failed attempt whose position has passed the kept hit, from
  that attempt position p, reading to the subject's end. Where occurrences of the run are dense that use runs about
  once per occurrence (`tuning.md` §2.41¶8c, measured BEFORE K38-2 and owed a re-measure: 1.38 against 0.81 ms with
  the rows denied; the bounded row 1.56 against 0.71 ms). At p the loop needs: whether the whole run occurs at or
  after p, and if so a position at or after p at which it occurs. The leftmost is not needed for the stop; the
  bounded row's move to (occurrence − K) uses the leftmost today, and whether it keeps doing so is decided by
  pcrec's design. The entry's use of the same site keeps the leftmost. COMPARATORS: (1) no subject on which the
  search is slower than with today's rows (the owner's speed gate of 2026-11-17, its allowances: a few percent on
  rare forms; a slowdown the user can turn off; anything off by default); (2) for the rows to leave the public deny,
  no subject on which it is slower than with the rows denied, cold memory-mapped subjects included (the owner,
  2026-11-12). ASK: a reply: can the site state this question as it stands, and in what form." If the owner's answer
  also says NOTE 3's B binds the kit's method, the manager adds NOTE 3's B sentence, quoted as the owner's; this
  note does not draft it (D157). FUTURE, UNSCHEDULED FACT (not a requirement): subject streaming is not a feature
  (`match_api.md` §5.2¶6); if it is scheduled, a bound on reads ahead of p becomes a fact pcrec states.
- TEXT FOR U1-p (assumes **lookahead-home** = pcrec's loop owns the look-ahead and its size): "FACT. [REQ-PAST-LAST]'s
  re-entering attempt rows use the pre-check site (DELEG_SITES `PRE`, ALL_PRESENT, ASSIGN) a second time, after
  each failed attempt whose position has passed the kept hit (the dense-hit cost: `tuning.md` §2.41¶8c, measured
  BEFORE K38-2 and owed a re-measure: 1.38 against 0.81 ms denied; bounded row 1.56 against 0.71 ms). pcrec will
  state, per use, a read limit L at or below the subject's end (a bare C identifier pcrec's code computes), and
  needs the leftmost hit in [p, L); on a miss in [p, L) it needs its own loop to continue, not the search to end
  (memfn.h admits `on_miss_leaves` 0 for ASSIGN). The entry's use of the same site is unchanged. COMPARATORS: as the
  other text, (1) and (2). ASK: a reply: which existing contract values and rows serve this use, and whether a row
  coverage change is needed."
  The same future, unscheduled streaming fact applies.

No other unit lands first, UNLESS the design keeps the per-hit form as a lever. That is needed if the remedy's form
loses to today's rows on sparse hits beyond the gate's "few percent on rare forms": the gate's "turn off" allowance
does not recover today's speed here, because turning off (`-fno-req-handoff`) gives the plain loop, which is slower
still on sparse hits (today's bounded row skips to the next hit less K). Then a second re-entry form is selectable:
P1's event fires, S3 becomes WIDEN, and A-SEAM's step and then P1 land first. The demotion half waits for register
row 15's mechanism. P2's event is this feature: if the manager accepts P2, its table is the design step's home for
the new rule.

## The general form and its siblings

- THE GENERAL FORM. A loop that consults a search site after local failures has two separate choices: WHAT it asks
  (the weakest fact that keeps its next steps sound) and WHEN it asks (the cadence: at every passed hit, or after a
  stretch of attempts run unasked). For the stop (unbounded or bounded K) the fact needed is "some occurrence at or
  after p"; for the bounded row's move to `c − K` it is "the LEFTMOST occurrence at or after p". Today the re-entry
  asks one question (`landmark_position`, the leftmost hit) for both uses, at one cadence (every passed hit). The
  ruled change (the three NOTES) is to the CADENCE: no re-ask per hit on dense hits. The question's strength changes
  only as far as a cadence needs it (S6, U1). Which uses ask which fact is handed to the design.
- THE FAMILY TODAY. Two families. (1) The resume question ("where does the search resume after a failure?"): S3
  (the attempt loop), S12 (the forward scan), S13 (the hybrid retry): P1. (2) The cadence question ("at this hit,
  ask the site, or run attempts unasked?"), FOUR built askers with three rule spellings: the scan re-entry (per hit,
  admitted by a prior margin, S15), the landmark walk (per hit, admitted by the same margin function, S14),
  `adaptive-dense` (a capped step block, S13), and the attempt loop (per hit with no density conjunct today, S1;
  the feature's new rule). P2. The flag audit names the loss family (`GS docs/dev/flag_audit_2026-11-12.md | sed -n
  110p`, item (c)): "same loss family ("a skip whose expected length is ~0 still pays its call")", with K88 (the
  entry handoff on back-to-back matches), K105 (the forward scan's re-entry, whose cause is its PRIOR-only admission,
  S15), and the start-set hat on dense starts (K83/K85, [START-DENSE]).
- PLANNED ROWS THAT EXTEND THE SAME SHAPE. [LANDWALK]'s stage 1 is BUILT (S14; its tag is stale); its child
  [LANDWALK-PRES] uses the landmark position generally (responses.md R-30 note: "[LANDWALK] is the general use of the
  position; this stop-early rule is the cheap part"). The walk iterates hits in ascending order, which keeps the
  leftmost question (unchanged). [START-DENSE] is P1's trigger and a P2 member candidate. [K88-HANDOFF-DENSE]
  concerns the entry, not the re-entry, and fits. [PRIOR-COST-UNIFY] is parked; this feature adds no prior reader.
  [SUBST-STREAM] (deferred) is the only row that brings subject chunks: it would extend S7's fact. Each fits the
  widened S6 question. None needs a wider shape than U1.
- UNLOCKS, each with its trigger. (a) The forward scan's re-entry takes the same weaker question and cadence rule.
  Trigger: K105's bench cell (its own owner row). (b) If the remedy has no losing case, the attempt rows leave public
  bit 46 for a test lever. Trigger: the no-loss measurement plus register row 15 landed (a conditional confirm, under
  "What the design step must decide"). (c) The landmark walk (S14) takes the cadence rule for dense landmarks.
  Trigger: a measured dense-hit loss on the `landmark-walk` row, or P2 accepted. (d) The 242 declined patterns of
  [REQ-PAST-LAST]'s unserved remainder (DFA bodies, hybrids, no single required byte) are not unlocked by this
  feature. Their unlocks stay where review r2-reqpast TH-7 filed them.

## Seams

| seam | writer | readers | facts down | facts up | new calls and their layer direction | text round trip |
|---|---|---|---|---|---|---|
| pcrec to kit presence site (MODULE, D146/D157; contract memfn/include/memfn.h plus integration.md; tests G2) | `req_site_define` (define), `emit_req_reentry_use` (use), src/gen/emit_dfa.c | the kit's presence and compose code (memfn/src) | today: the predicate's parts, `handoff` ASSIGN, `head_max` (K or `MF_HEAD_MAX_UNBOUNDED`), `use` ENTRY (define phase); per use `lo`, `n` = subject end, `on_miss` NOMATCH. NEW, U1-k: the weaker question's contract value, per use. NEW, U1-p: a per-use read limit (C text in `mf_hooks.n`) and a non-ending miss (define-phase `on_miss_leaves` 0, or an `on_miss` statement) | today: the leftmost hit or the miss. NEW, U1-k: an occurrence position, the kit's choice of which. U1-p: the leftmost hit below the limit, or the miss | U1-k: none new if the fact is per use; a second define if the design takes that home. U1-p: a second define or a per-use change (S6). pcrec to kit is a module call, both ways allowed | U1-k: yes for the new fact (an enum value or flag). U1-p: no: the read limit is C text in `mf_hooks.n`. In both, the seam it rides on carries C text, callbacks and shared state at T (`GS memfn/include/memfn.h | grep -n -E "const char \*(s|n|lo|result|on_miss);"`), failing manifesto principle 9; that is A-PLAN's job, not this feature's |
| start table to emitter (LAYER, inside pcrec) | the FIRST row chosen by `cand_select` (`CandUse`) | `req_reentered`, `emit_req_landmark_move` | unchanged: `whole`, `reenter`, K | none | none new; one way, down | n/a (in-process records) |
| VM emitter to start-table emitter (LAYER, same level; cross-emitter prototype in internal.h, roadmap H-HEADER) | src/gen/emit_vm.c retry | `pcrec_emit_req_attempt_reentry` | the position variable name | none | none new | n/a |
| emitter to driver (LAYER, wrong way, register 6c) | `emit_req_handoff_rest`, `pf_emit_handoff` write `Job.req_handoff_vm` | the `drop-handoff` rung | — | the flag (existing back-flow) | none new: the feature adds no back-flow | n/a |
| caller contract (spec, D80) | the landing change | callers | `tuning.md` §2.41¶8b (the re-entry sentence), ¶8c (the re-ask, "It can be slower" and its measurement), ¶9 (default); `match_api.md` §6.3.7¶11 (the stamp sentence describing the re-ask); `match_api.md` §6.3.4's `"handoff"` row (restates the forward re-entry's re-ask: a hunk only if the scan's bytes or semantics move); the rows' `desc` in `--list-axes`. Not affected: `limits.md` §8.5¶3a, `facts_listing.md` §4.1.2¶8b | — | — | n/a |
| option word (public bit 46 to a test lever; register row 15's mechanism, D195) | axes.def / lib/pcrec.h | `cand_select` (row deny), `cand_nodes[]` world reads, `req_start_set` | only on the no-loss verdict; the bench is told through its inbox (D195) | — | none | n/a |

## What is deleted

- By the feature: the per-hit re-ask on the re-entering attempt rows (the emitted `if (landmark_position <
  attempt_position) { ... re-ask ... }` asked at every passed hit, C2/C3); `tuning.md` §2.41¶8c's dense-hit caveat
  ("It can be slower ... where occurrences are dense every failed attempt passes one and re-asks") and the same
  sentence in ¶8b, if the measurement removes the loss. On the no-loss verdict only, through row 15's mechanism: the
  attempt rows' public deny coverage (bit 46 keeps the DFA-route `handoff` and NEXT's re-entry).
- By U1 (either shape): nothing (reason given under U1).
- By P1 (when its trigger fires, not now): the `reenter` bool, the consumer branch in the shared re-entry text, and
  the VM-only route's private retry spelling.
- By P2 (if accepted; its event is this feature): three dispersed cadence-rule spellings become rows of one table.

## What the design step must decide

Handed on, not decided here:
- S4/S6: the method is the kit's under D157, with the owner's leading candidate (NOTE 3's blocks) and its B
  constraint as the owner stated them, and the **lookahead-home** answer; which uses ask which fact (an option: both
  rows ask the weaker fact for the stop, and the bounded row keeps asking the leftmost for its move where that is
  worth it, on sparse hits where it skips far), and how the move and the stop share the kept positions (S16's
  declarations).
- S6: the home of the weaker question (U1-k's candidates or U1-p's); the `budget` column of an in-loop use of `PRE`
  (`DELEG_SCAN` today, "the ONE source of MF_P_INLOOP"); the G2 reference for the new question, written by a
  D27-blinded kit author (manager's ruling, r49 group D).
- A-PLAN (manager's ruling, r49 group F): the CONSUMER step fires A-PLAN's trigger IF the kit's answer to the new
  question changes which site or method is chosen. The design step decides, with the kit, whether that condition
  holds.
- S7: B's value and derivation (rule "Tuning constants are suspect", D149; the owner: "show insensitivity across that
  range in the measurement"; the owner's named sources and exclusions: "the stream's chunk when streaming, else the
  page size (sysconf(_SC_PAGESIZE), POSIX libc, or a build-time page constant if the measurement shows insensitivity;
  not the per-device /sys readahead window, not glibc-only cache sizes)"); on the pcrec branch, its table (`limits.def`
  per D90, unless the design argues the `vm_reseed_cal`/PLACE precedent); where in the artifact it is read (a
  build-time constant, or a run-time `sysconf` in the artifact: a libc call the `<PREFIX>_MEMFN_LIBC` line would
  list, D147 addendum 10, Q53).
- S8: the linearity argument for the new form; whether `req_parts_in_whole` stays a conjunct, and why.
- S1/S3: whether the per-hit form survives as a lever (needed if the remedy loses to today's rows on sparse hits
  beyond the gate's allowance; then A-SEAM's step and P1 land first).
- S12/S15: the forward scan stays byte-identical, or its change is timed (the scan-re-entry reading); the shared
  text takes the remedy through a fact its consumer states, never a branch on which consumer calls. If it cannot,
  P1's trigger has fired.
- P2: if the manager accepts it, the table's row for the new rule, and the three existing rows byte-identical.
- The give-up direction (`tuning.md` §2.41¶9a: a search "may return, with them, the answer an unbounded budget
  returns ..., never the reverse"; the one-way sentence "a give-up may become an answer, never the reverse" is D151's,
  citing D148 Q6; D158 is the single rule). Attempts that "run unasked" run MORE attempts than today's stop on some
  subjects; the design shows the direction holds.
- SPLIT-DENY, a CONDITIONAL CONFIRM (manager's ruling, r49 group J): NOTE 1's record pre-authorises the move "ONLY IF
  the method has no losing case", and D195 rules the mechanism. Consequences the move must carry: the bench pins
  `-fno-req-handoff` (`GS docs/dev/flag_audit_2026-11-12.md | sed -n 115p`: "`testees/pcrec/configs.toml` pins these
  flags: ... -fno-req-handoff (2) ..."), and D195 says "the bench is told through its inbox"; the flag audit's item (c)
  says of bits 46/47 "share one bit then, not before"; bit 46 is a KEEP (`... sed -n 86p`), so the move uses register
  row 15's mechanism and does not join [FLAG-DEMOTE]'s ruled set of 20; `req_start_set`'s forced deny (S9) is
  re-aimed to the word that still covers NEXT.
- The measurement card (Frank 2026-10-23), in the method owner's card file (memfn/data/cards if the kit's). Its
  BASELINE STEP is the owed re-measure of `tuning.md` §2.41¶8c's timings, which predate K38-2. The regime covers warm
  and cold memory-mapped subjects (NOTE 1's record: "the cold case is argued, not measured"), dense, sparse and
  early-match subjects, and both comparators (today's rows for the landing; the rows denied for the demotion). D144
  alpha on the Linux box at both kit layers (D147).
- Checks that bind the rewritten text and must be re-aimed or shown still to reach ([MECH-REACH]): C-HANDOFF:
  `git grep -l -E "landmark_position|handoff-attempts|REQ-PAST-LAST|emit_req_landmark_move" $T -- tests scripts`
  prints 42 files at T; the design reads the FULL output. Among them, the text-shape pins of the emitted re-ask:
  sabotage rows S1700-S1713, S1955-S1957, S3074-S3077, S808/S809 (tests/mech/sabotages); `tests/litscan/handoff_vm.rxt`
  and `gen_handoff_vm.py`; `tests/codegen/run_prechecks.sh`, `run_dfa_stamps.sh`, `run_encoding_checks.sh` (its
  `REENTRY_*` checks); `tests/memfn/run_handoff_reach.sh`; `cand_oracle_witnesses.tsv`; the population pins
  `tests/startset/manifests/manifest_s2_vm_auto.tsv`, `manifest_s2_vm_forced.tsv` and `tests/axes/run_axes.sh`
  (H-COUNTS). The walk's S1821/S1827 are in the output but bind S14, which the feature does not touch.
- The abi event: the emitted retry text moves, so this is an abi bump with readers found by grep (D76/D94; H-ABI). A
  kit byte move in the same commit is one pcrec abi event (D146/D147, memfn/CLAUDE.md).

## Open questions for the owner

One question (rev 1's other four are now statements of the record's reading: the gate (Goals served), streaming and
the scan re-entry (Requirements read), split-deny (a conditional confirm, under "What the design step must decide")).

- **lookahead-home**: does the owner-stated B (NOTE 3: "B is a tuning constant: derive it from a SYSTEM constant
  (Frank)") bind the KIT'S METHOD, or PCREC'S LOOP? TODAY: the plan row's own Today line: "pcrec states the fact (required run, unbounded); the method is pcrec-only in this build (the kit is not asked for it, D157 stays the rule for any later kit method)." And `tuning.md` §2.41¶7a, in full: "**Which rows are the
  kit's** (R17-b′ B3b, `docs/design/memfn/r17b_prime.md` §4.4, handoff framing (a)): none of this table's. The
  handoff chooses the ORIGIN, which stays pcrec's: `K`, the moved start and its rounding, the re-entry, and the K
  admission of ¶8a are pcrec's rows over pcrec's facts. What the kit decides is the presence the admission reads
  (§2.29¶1): its links say which landmark the pre-check tests (the run where it tests it, or the one byte where no
  run is stated, `<PREFIX>_REQ_RUN`/`<PREFIX>_REQ_BYTE`, which must and do name the same choice; where the kit
  declines a stated run, the leading member its links name, whose `K` is read from that member). Under
  `--memfn=no-fd-pres-pick` an emitted pre-check also tests every member and the whole run, after the landmark it
  keeps: each is a fact every match holds at or after the start, so its miss answers no match at the entry and at
  the re-entry alike, and the kept position is the landmark's." NOTES 1-2 and D157 put the METHOD with the kit;
  ¶7a puts the re-entry (the origin) with pcrec. What is open is only which side the B constraint binds. EXAMPLE:
  `[^@ ]+@x` under `--engine=vm` over 1 MB of ` @x` asks the kit about every 3 bytes today; under a method with a
  block size someone must know that size (the page size today; a stream's chunk if streaming is ever scheduled).
  WHY IT SHAPES THE TREE: the kit's method: U1 takes shape U1-k (a seam event; B's home is the kit's, and D146
  addendum 1's target table lists ISA facts, so whether it holds a page size is the kit's answer). pcrec's loop: U1
  takes shape U1-p (a kit row event plus pcrec movers), and B becomes pcrec's first system constant, a `limits.def`
  row (S7). LEANING: the kit's method. pcrec owns the compare and the stop (NOTE 1's record: "each attempt compares
  its position with that number"), which keeps ¶7a (the origin and the re-entry stay pcrec's) and D157 (pcrec states
  the question and the constraints, never a method).
