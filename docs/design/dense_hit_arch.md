# The dense-hit remedy for the required-run handoff rows: architecture note
STATUS: DRAFT (lane archdense, 2026-11-18; the [ARCH-STEP] pilot; not reviewed)
FORM: full   (trigger: 5 existing decision sites touched (site map S1, S4, S6, S8, S9); mechanisms added: one new question at the kit's presence site (S6/S7), one new system-constant source (S7))
TREE: T = 57fcb5737dff37bd97429fb1e889ca0233d12e10 (lane/archdense cut from main)   REQUIREMENTS: [REQ-PAST-LAST]'s three NOTES of 2026-11-12 @T; D144, D146, D147, D157, D195 (docs/dev/decisions.md @T); [FLAG-DEMOTE], [LANDWALK], [REQRUN-VM], [REQ-HANDOFF-L1] @T; `docs/spec/tuning.md` §2.41¶7a-¶9b @T; memfn/docs/requests.md R-30, R-41 and responses.md's R-30 notes @T   REGISTER READ: `docs/dev/guide/architecture.md` register @T

Every command below runs from any checkout with `T=57fcb5737`; `GG` stands for `git grep -n` at `$T`
(`git grep -n PATTERN $T -- PATHS`). No command reads the working tree.

## Goals served

- **Goal 1 (one home per question).** The re-entry already has one text, `emit_req_landmark_move`, shared by its
  two consumers (S4). The feature must change it THERE and not grow a consumer copy. The question it serves,
  "where does the search resume after a failure?", is answered in three slots today (S3, S12, S13). This note
  does not unify them now; it proposes register row P1 with its trigger.
- **Goal 3 (seams).** The feature changes what crosses the pcrec-to-kit module seam (D146, D157). The question
  asked at the presence site gets a weaker contract (S6), and a system fact needs a home (S7). Facts only, no
  method.
- **Goal 4 (remodels ride along).** Six register rows match the sites. One remodel lands first: the seam's
  reply contract, U1. The demotion half of the feature waits for [FLAG-DEMOTE]'s internal deny word (register
  row 15).
- **Traded against.** The speed gate against goal 3's split of concerns, at S7. If pcrec owns the block
  look-ahead, a system constant (the page size) enters pcrec, which D146 keeps free of architecture
  knowledge. If the kit owns it, part of the re-entry's cadence moves to the kit, although
  `tuning.md` §2.41¶7a says the re-entry is pcrec's. This is the owner question **lookahead-home**.
- **The gate has two comparators here** (the owner 2026-11-17, "no existing regex gets slower"; the [REQ-PAST-LAST]
  no-loss NOTE). Today's rows: no case may become slower than the current re-entry, for example sparse hits where the
  bounded row's per-attempt move skips far. The plain loop: no case may be slower than with the rows denied, which is
  the condition for demotion. These two do not coincide. Owner question **gate-comparator**.

## Requirements read

All three are from [REQ-PAST-LAST]'s NOTES (`scripts/entry REQ-PAST-LAST -l 2` @T), quoted from the row:

1. Frank, 2026-11-12, "Queue that fix": "after the FIRST failed attempt, obtain the LAST occurrence of the required
   run at or after (known hit start + 1) ONCE (a kit request R-n stating that FACT only, D157: the kit chooses the
   method ...), then each attempt compares its position with that number instead of re-asking the presence site."
   It then says the rows "may move from the public -fno-req-handoff deny to a test lever (D195 / FLAG-DEMOTE) ONLY IF
   the method has no losing case".
2. The no-loss condition: "no case slower than the plain loop (Frank 2026-11-12 on cold mmapped subjects): a
   backward scan loses on cold mapped tails, a forward keep-latest pass loses when a match comes early in a long
   subject with hits to its end ... The request states the fact + the no-loss requirement; otherwise the public bit
   stays ... needs a measurement card (new method)."
3. Frank, "blocks instead of doubling, 'also helps with streaming'": "one presence question per block of B bytes ahead
   of the loop (yes: the block's attempts run unasked; no: scan forward to the next occurrence, end of subject
   stops); forward-only, at most one block ahead ... derive it from a SYSTEM constant (Frank): the stream's chunk when
   streaming, else the page size ... and show insensitivity across that range in the measurement."

THE ARCHITECT'S READING (not a ruling). NOTE 1's "LAST occurrence ONCE" needs look-ahead to the subject's end.
NOTE 3's "at most one block ahead" forbids that. NOTES 2-3 rule out the method of NOTE 1. The WHAT is shared by
all three: stop past the run's last occurrence, do not re-ask per hit on dense hits, and lose no case. So the
requirements do not contradict each other on what the feature does, and the stop rule does not fire. The
**lookahead-home** question asks the owner to confirm this reading.

VOCABULARY (each grepped at T; hit counts are in the command list):
- rows and payload: `handoff-attempts`, `handoff-attempts-entry`, `handoff-attempts-unbounded` (FIRST slot of
  `cand_rows[]`, executor `cand_select`); `CandUse.whole`, `CandUse.reenter`; `REQ_USE_HANDOFF`; NEXT's
  `handoff-reentry`; RETRY's `adaptive-dense`.
- predicates: `req_handoff_vm_run`, `req_handoff_entry_applies`, `req_handoff_attempts_applies`,
  `req_handoff_unbounded_applies`, `req_parts_in_whole`, `req_reentered`, `pf_handoff_applies`.
- emission: `emit_req_handoff_rest`, `emit_req_landmark_move`, `emit_req_reentry_use`,
  `pcrec_emit_req_attempt_reentry`, `pf_emit_handoff`; emitted locals `landmark_position`, `handoff_position`,
  `attempt_position`.
- facts and K: `req_handoff_k`, `pcrec_fact_req_whole_run(...)->whole_maxoff`, `PCREC_W_UNBOUNDED`.
- kit seam: `req_site_define`, `mf_site.head_max`, `MF_HEAD_MAX_UNBOUNDED`, `MF_H_ASSIGN`, `mf_site.ret_pred` ("the
  leftmost hit"), `mf_hooks.n` (the read limit), `mf_hooks.lo`, `on_miss`, `on_miss_leaves`.
- options and stamps: `PCREC_NO_REQ_HANDOFF` (bit 46, `-fno-req-handoff`), `RX_REQ_HANDOFF` / `req_handoff_stamp`.
- driver: `Job.req_handoff_vm`, `Ctx.req_handoff_dropped`, the `drop-handoff` rung of `fit_rungs[]`.
- ZERO HITS (new): a system page size (`sysconf|_SC_PAGE|PAGE_SIZE|getpagesize`, 0 hits in src cli lib memfn), a
  subject stream chunk (`-i -w chunk`, 0 hits in src/gen memfn/src); `match_api.md` §5.2¶6 says the API keeps "No
  partial-match or streaming window state". Both belong to S7.

REQ-OPEN items: **lookahead-home** (S6, S7), **streaming-meaning** (S7), **scan-reentry-too** (S4, S12),
**gate-comparator** (S1, S4), **split-deny** (S9).

## Site map

| # | site (file, function or table) | command (at T) | today | class | goal/rule |
|---|---|---|---|---|---|
| S1 | `cand_rows[]` FIRST rows `handoff-attempts` and `handoff-attempts-unbounded`, src/gen/emit_dfa.c (executor `cand_select`) | C1 | the two attempt-loop rows that re-enter (`.reenter = true`, `.whole = true`), deny `PCREC_NO_REQ_HANDOFF`; their `desc` states the per-hit re-ask | ROW: the remedy changes what these rows do after a failed attempt, with no new choice in the table | goal 1; Decisions are declared tables; A row checks its own contract |
| S2 | `cand_rows[]` FIRST row `handoff-attempts-entry` | C1 | moves the first attempt only; no re-entry | AS-IS: nothing is re-asked per hit, so the dense-hit loss does not exist on it | goal 1 |
| S3 | `CandUse.reenter`, src/gen/emit_dfa.c `typedef struct CandUse`, read by `req_reentered` | C5 | a bool: whether the row re-enters after each failed attempt | AS-IS while the remedy REPLACES the per-hit re-ask (whether to re-enter stays the row's; how is the text's). It becomes WIDEN, and P1 lands first, if the design keeps two re-entry forms selectable | goal 1; One question, one primitive |
| S4 | `emit_req_landmark_move`, src/gen/emit_dfa.c, the one re-entry text of two consumers (`pf_emit_handoff`, `pcrec_emit_req_attempt_reentry`) | C2 | re-asks the pre-check when the kept hit is behind the position, then moves to the hit less K where K is finite; it branches on `k >= PCREC_W_UNBOUNDED` and on `f` (the forward scan's form) | SHARED: already the one home. The remedy is written here, never as a copy in one consumer. A branch on WHICH consumer calls is the aggregation to avoid (REQ-OPEN **scan-reentry-too**) | goal 1; One question, one primitive; Build the general form |
| S5 | `pcrec_emit_req_attempt_reentry`, src/gen/emit_dfa.c; called from the VM retry in src/gen/emit_vm.c | C3 | runs after the encoding's advance and before the start-set seek, on each failed attempt | AS-IS: "after the first failed attempt" is this point; the call does not move | goal 3 (an existing cross-emitter call, H-HEADER) |
| S6 | `emit_req_reentry_use`, src/gen/emit_dfa.c: the presence site's second use; kit reply `mf_site.ret_pred`, memfn/include/memfn.h | C4, C10 | asks the kit's ALL_PRESENT site from the position, reads to `subject_length`, ASSIGNs the LEFTMOST hit to `landmark_position`; a miss is NOMATCH | WIDEN: the reply's contract covers the leftmost hit only ("RETURN/ASSIGN the leftmost hit of preds[ret_pred]"). The remedy needs a weaker question, "an occurrence at or after lo, which one is the kit's choice", or a question bounded by a block whose miss does not end the search. The shape depends on REQ-OPEN **lookahead-home**. Generic writers: every ALL_PRESENT ASSIGN form in memfn/src (C10 counts them) assumes leftmost | goal 3; A module seam is an API with a written contract; Across the kit boundary, send facts |
| S7 | the block size B's SOURCE: a system page size, or a stream chunk | C8, C9 | nothing: 0 hits for either at T; `match_api.md` §5.2¶6 says there is no streaming state | NEW-SEAM: a new fact, and the side that states it is open (REQ-OPEN **lookahead-home**, **streaming-meaning**). In the kit, the page size is a target fact (D146 addendum 1: the target table is the kit's). In pcrec, it is a new tuning constant with a derivation | goal 3; Tuning constants are suspect |
| S8 | `req_parts_in_whole`, src/gen/emit_dfa.c: the linearity conjunct of both re-entering rows | C16 | admits the row only where every part of the pre-check is a byte or slice of the whole run, "so re-asking the site after every failed attempt keeps the search linear" | ROW: a conjunct of existing rows whose stated reason assumes the per-hit re-ask. The design re-argues it for the new form, and may keep or drop it | goal 1; A row checks its own contract |
| S9 | the deny: `PCREC_NO_REQ_HANDOFF` (lib/pcrec.h bit 46, src/core/axes.def), the deny column of 5 rows and the world reads (`.under`/`.by`) of `cand_nodes[]` | C7 | ONE public bit denies all five handoff rows (`handoff`, the three attempt rows, NEXT's `handoff-reentry`); the flag audit KEEPS it for K88's loss on the DFA-route `handoff` row | ROW (the rows' deny column). Moving the attempt rows to a test lever splits bit 46's coverage, which is register row 15's internal deny word ([FLAG-DEMOTE]). REQ-OPEN **split-deny** | goal 1; public deny only if slower (Frank 2026-10-29, D195) |
| S10 | `req_handoff_stamp` (`RX_REQ_HANDOFF`), src/gen/emit_dfa.c; `match_api.md` §6.3.7¶11 | C11 | the value is K, `"unbounded"` or `"none"` | AS-IS: the value does not change. The spec SENTENCE describing the re-ask changes (D80, under Seams) | goal 3 |
| S11 | the `drop-handoff` rung of `fit_rungs[]` (src/core/compile.c) reading `Job.req_handoff_vm`; `Ctx.req_handoff_dropped` | C6, C13 | after a size-cap refusal, retries without the attempt rows; the emitter writes the flag back to the driver (register row 6c, a noted deviation) | AS-IS: the remedy's text is inside what the rung drops, and the feature adds no emitter-to-driver fact | goal 3 (layer direction; 6c) |
| S12 | NEXT row `handoff-reentry` (`pf_handoff_applies`), the forward scan's re-entry through S4 | C15 | re-enters only at the DFA's start state with nothing accepted; has the same per-hit re-ask (known_issues K105: x1.537 on `[a-y]\d{0,100}:` over ':'-dense digits) | AS-IS if the remedy reaches only the attempt loop, but through S4's shared text (REQ-OPEN **scan-reentry-too**) | goal 1; Notice siblings |
| S13 | RETRY rows (`exact` ... `adaptive-dense`), src/gen/emit_dfa.c: "where the next attempt resumes" behind a prefilter | C14 | `adaptive-dense` already "starts inside a capped step block that is armed" (a block rule, chosen by the byte-rate prior) | AS-IS (a sibling, not touched). It is the third home of the resume question: proposed register row P1 | goal 1; Notice siblings |

COMMANDS (each at `$T`, from the repository root; hit counts as printed at T):
- C0 (premise): `git grep -n "handoff-attempts-unbounded" $T -- src docs/spec | head` gives 6 lines (tuning.md, match_api.md,
  compile.c, internal.h, emit_dfa.c twice); `git merge-base --is-ancestor f6365477c $T` exits 0.
- C1: `git grep -n '"handoff-attempts' $T -- src/gen/emit_dfa.c` gives 7: the three FIRST rows' names and `.list` names, and the BOUND read's site label in `req_handoff_vm_run`.
- C2: `git grep -n "emit_req_landmark_move(" $T -- src` gives 4: the declaration, the definition and two callers
  (`pf_emit_handoff`, `pcrec_emit_req_attempt_reentry`).
- C3: `git grep -n "pcrec_emit_req_attempt_reentry(" $T -- src` gives 3: internal.h, emit_dfa.c, and emit_vm.c (the VM retry).
- C4: `git grep -n "emit_req_reentry_use(" $T -- src` gives 2: the definition and its one caller, in S4.
- C5: `git grep -n -w "reenter" $T -- src` gives 4: the field, `req_reentered`'s read, and the two rows that set it.
- C6: `git grep -n -E "req_handoff_vm|req_handoff_dropped" $T -- src` gives internal.h (`Job`, `Ctx`), compile.c (the
  rung's reader and the retry's writer), and emit_dfa.c (the writers `emit_req_handoff_rest`, `pf_emit_handoff`; the
  readers `req_handoff_vm_run`, `pf_handoff_applies`).
- C7: `git grep -n "PCREC_NO_REQ_HANDOFF" $T -- src cli lib memfn/src` gives 13: lib/pcrec.h bit 46, axes.def, five
  row denies, and six world reads in `cand_nodes[]`.
- C8: `git grep -n -E "sysconf|_SC_PAGE|PAGE_SIZE|getpagesize" $T -- src cli lib memfn/src` gives 0.
- C9: `git grep -n -i -w "chunk" $T -- src/gen memfn/src` gives 0.
- C10: `git grep -n "ret_pred" $T -- memfn/include/memfn.h` gives the field comment "ALL_PRESENT: RETURN/ASSIGN the leftmost
  hit of preds[ret_pred]"; `git grep -c "MF_H_ASSIGN" $T -- memfn/src` gives 10 files that read the ASSIGN handoff.
- C11: `git grep -n "req_handoff_stamp" $T -- src` gives the declaration, the definition and the one stamp writer.
- C13: `git grep -n '"drop-handoff"' $T -- src/core/compile.c` gives 1, the rung in `fit_rungs[]`.
- C14: `git grep -n '"adaptive-dense"' $T -- src/gen/emit_dfa.c` gives 3, all on the one RETRY row (its name, token and `.list` entry).
- C15: `git grep -n "pf_handoff_applies" $T -- src` gives 2: the predicate and the NEXT row `handoff-reentry`.
- C16: `git grep -n "req_parts_in_whole(" $T -- src` gives 3: the definition and the two re-entering rows' predicates.
- C17: `git grep -n "req_reentered(" $T -- src` gives 4: the declaration, the definition, and the readers in
  `emit_req_handoff_rest` and `pcrec_emit_req_attempt_reentry`.
- WITNESS of the emitted text (illustration only: the main tree's `build/pcrec`, built 2026-11-15 from main, not
  from T; the git commands above are the evidence): `timeout 60 build/pcrec -p rx --engine=vm -o OUT.c --pattern
  '[^@ ]+@x'` stamps `RX_REQ_HANDOFF "unbounded"`. Its retry has `if (landmark_position < attempt_position) {
  landmark_position = rx_reqrun(subject, subject_length, attempt_position); if (landmark_position >= subject_length)
  return 0; }`. The same with `[^@ ]{1,5}@x` stamps `"5"` and has the same re-ask followed by the move. These are the
  two cells `tuning.md` §2.41¶8c measures: 1.38 against 0.81 ms denied, and 1.56 against 0.71 ms.

## Register rows looked up

Searches run at T: `git show $T:docs/dev/guide/architecture.md | grep -n -E
"emit_dfa|emit_vm|compile.c|internal.h|cand_rows|req_handoff|memfn|REQ-PAST-LAST|FLAG-DEMOTE"`. Then
`docs/design/stream/roadmap.md` §1-§2 for the same files and tag (register row 12). Then `scripts/entry -g`
for D-row "Revisit when" triggers naming `req_handoff`/`emit_req_`; none matched, because the decisions
profile is dormant (see the lane report).

| register row | why it matches | disposition |
|---|---|---|
| 1 (start-table rows carry their act) | `cand_rows[]`; the `cand_finish_of(cx) == CAND_ROUTE_VM` tests (`req_reentered`, `pf_emit_handoff`) | NOT CARRIED: the feature adds no recover or finish act and no new route test; the design must keep it so (it reads `req_reentered`, it does not re-test the route) |
| 2 (engine identity asked one way) | `pcrec_artifact_has_dfa_scan` / `cand_route_of` reads in S3, S5, S12 | NOT CARRIED: no new reader of engine identity |
| 6a (Job/Ctx writer and readers) | `Job.req_handoff_vm`, `Ctx.req_handoff_dropped`, `cx->job->mf_pre` | NOT CARRIED: its event is "the next feature that adds an emitter-to-driver flag"; this one adds none |
| 6c (NOTED DEVIATION: emitter-written facts the driver re-plans on; `req_handoff_vm` named) | S11 | NOT CARRIED, reason: L, an abi/spec event for the caps' unit, whose events are [VMREC] and roadmap H-FLAGS. The feature adds no back-flow, and its text stays inside what `drop-handoff` drops. The correction still waits for its event |
| 12 / roadmap A-SEAM | its ride-along triggers list [REQ-PAST-LAST] by tag; the next step moves `CandUse` and the row/hand types to a seam header with no bytes | NOT CARRIED, reason: the remedy as architected changes no field of `CandUse`/`CandRow` (S3 AS-IS). TRIGGER RESTATED: if the design adds or changes a payload field (a second re-entry form, S3 becoming WIDEN), A-SEAM's step lands first, ahead of P1 |
| 12 / roadmap A-PLAN | the kit's site call is to split into a plan call and an emit call, "the first stream step that touches search sites" | NOT CARRIED: this is a feature, not a stream step. The new seam facts are written so they serialize (Seams, last column) and can move to the plan call unchanged |
| 12 / roadmap H-FLAGS, H-LADDER | `req_handoff_vm`; `drop-handoff` | NOT CARRIED: no new flag and no new droppable row |
| 13 ([VMREC] (b)/(c), riding) | src/gen/emit_vm.c | NOT CARRIED: steps (b) and (c) are not started at T (`scripts/entry VMREC -l 1`), so no refactor is in flight on the retry text. If one starts first, it outranks this feature on emit_vm.c's retry (Refactors outrank optimization) |
| 15 (internal deny word, riding [FLAG-DEMOTE]) | S9: the attempt rows can leave public bit 46 only through an internal deny | JOINS [FLAG-DEMOTE]: the DEMOTION half of this feature (NOTE 1's conditional move to a test lever) waits for row 15 and is not this feature's unit. The remedy half does not need it (separable) |
| 3 (refusal table, [FLAG-DEMOTE]) | the same option word | NOT CARRIED: the feature adds no refusal |
| 7b, 9, 10, 19 | they name emit_dfa.c / emit_vm.c / memfn | NOT CARRIED: no post-render rewrite (7b), no emitter split (9), no CandRow offset (10), no new declared table (19) |

Noted deviations on touched sites: one, 6c, disposed above. This note recommends no deviation, so it proposes none.

ROWS THIS NOTE PROPOSES (register columns):

| # | remodel | shape (rule) | where | event that carries it | size, gate | deletes | status |
|---|---|---|---|---|---|---|---|
| P1 | One home for "where the search resumes after a failure": the VM attempt loop's re-entry (FIRST's `CandUse.reenter` plus `pcrec_emit_req_attempt_reentry`), the forward scan's re-entry (NEXT `handoff-reentry`) and the hybrid retry (RETRY rows, `adaptive-dense`'s step block) answered by one slot's rows and acted through the row | Notice siblings (three homes); One home per question (goal 1); Act through the row | `CandUse.reenter` and `req_reentered` (C5, C17); `emit_req_landmark_move` (C2); RETRY rows (C14), src/gen/emit_dfa.c; the VM retry in src/gen/emit_vm.c (C3) | a SECOND re-entry form selectable on any of the three (S3 becomes WIDEN), or [START-DENSE], or a fix for K105 or K88 (the same loss family, flag audit 2026-11-12 item (c): "a skip whose expected length is ~0 still pays its call") | M, no-mover | the `reenter` bool, the consumer branch in `emit_req_landmark_move`, the VM-only route's private retry spelling | open |

## Remodels that land first

**U1: the presence site states the question its caller needs (S6), a kit seam event.** One unit. It is not built
until **lookahead-home** is answered, because the two answers give it two shapes.
- What changes shape. The reply contract of the kit's presence use covers "the LEFTMOST hit" only (C10). It is widened
  by one stated question: either "an occurrence at or after lo; which one is the kit's choice" (the kit owns the
  look-ahead), or "the leftmost hit below a stated read limit, whose miss does not end the search" (pcrec owns the
  blocks; `mf_hooks.n` is already per use, but an ASSIGN miss today is pcrec's leaving `on_miss`). The facts and the
  question are pcrec's; how it is answered is the kit's (D157). pcrec PROPOSES the request text below and files
  nothing.
- Gate: kit seam event (D146): `MF_SITE_ABI`/`MF_VOCAB` meaning, with zero pcrec movers until a consumer states the new
  question (the D157 precedent: "Zero pcrec movers ... until a kit row consumes it").
- Size: S.
- Checks that bind the moved code: the kit's G2 (`make test-memfn-g2`, presence cases), `mf_vocab_has`, the presence
  deny run `tests/memfn/run_presence.sh` over `tests/litscan/presence_deny.rxt`. On the pcrec side none, because pcrec
  states nothing new until the feature lands.
- Separable: yes. It lands with no caller asking the new question, answer- and byte-identical.
- Speed gate: byte-identical artifacts are the proof.
- Deletes: nothing. Its reason is the feature's need, a seam shape that does not hold the question (rule "A shape
  states the inputs it covers").
- PROPOSED REQUEST TEXT (for the manager to file as the next R-n; this lane files nothing): "FACT. [REQ-PAST-LAST]'s
  re-entering attempt rows re-ask the pre-check site's whole-run presence after every failed attempt that has passed
  the kept hit. On dense hits that is one ask every few bytes (tuning.md §2.41¶8c: 1.38 against 0.81 ms). The caller
  needs, at a position p after a failed attempt: whether the whole run occurs at or after p, and if so a position at
  which it occurs; the leftmost is not required (the stop and the attempts below that position are sound with any
  occurrence). REQUIREMENTS, the owner's (2026-11-12): no subject on which the search is slower than with the rows
  denied, cold memory-mapped subjects included; the subject is read forward; reads ahead of p are bounded (a stream
  supplies one chunk at a time). ASK: (1) a reply: can the site state this question as it stands, and in what form;
  (2) whether a system constant (the page size) is a fact your target table would hold." The request names no block,
  doubling or backward scan.

No other unit lands first. The demotion half waits for register row 15 (riding [FLAG-DEMOTE]). P1 waits for its
trigger.

## The general form and its siblings

- THE GENERAL FORM. A loop that re-asks a search site after each local failure needs only the WEAKEST fact that keeps
  its next steps sound. For the stop (unbounded or bounded K) that fact is "some occurrence at or after p". For the
  bounded row's move to `c − K` it is "the LEFTMOST occurrence at or after p". The re-entry asks one question
  (`landmark_position`, the leftmost hit) for two uses. The remedy separates the two facts. The bounded row may keep
  asking the leftmost hit for its move where that is worth it, and both rows ask the weaker fact for the stop.
  Deciding where the move is worth it is the design's job.
- THE FAMILY TODAY. "A skip or re-ask whose expected length is about 0 still pays its call" (flag audit 2026-11-12,
  item (c)): K88 (the entry handoff on back-to-back matches; `-fno-req-handoff`), K105 (the forward scan's re-entry on
  a landmark denser than its prior), the start-set hat on dense starts (known_issues K83/K85, [START-DENSE]), the
  hybrid retry's `adaptive-dense` capped step block (BUILT, the RETRY slot, C14), and this feature. The one member
  with a block rule already built is `adaptive-dense`. Its predicate reads the byte-rate prior; the owner's block
  NOTE asks for a rule with no prior and no adaptivity (and memory: run-time adaptive switching "has not proved its
  worth"). This note proposes P1 for the resume question and does not unify the rules.
- PLANNED ROWS THAT EXTEND THE SAME SHAPE. [LANDWALK] and its child [LANDWALK-PRES] use the landmark position
  generally (responses.md R-30 note: "[LANDWALK] is the general use of the position; this stop-early rule is the cheap
  part"). The walk iterates hits in ascending order, which fits the leftmost question (unchanged). [START-DENSE] would
  be P1's trigger. [K88-HANDOFF-DENSE] concerns the entry, not the re-entry, and fits. [PRIOR-COST-UNIFY] is parked;
  this feature adds no prior reader, so the family's count of four stays. [SUBST-STREAM] (deferred) is the only row
  that brings subject chunks: it would extend S7's fact. Each fits the widened S6 question. None needs a wider shape
  than U1.
- UNLOCKS, each with its trigger. (a) The forward scan's re-entry takes the same weaker question. Trigger: K105's
  bench cell, or the owner's **scan-reentry-too**. (b) If the remedy has no losing case, the attempt rows leave public
  bit 46 for a test lever. Trigger: the no-loss measurement plus register row 15 landed. (c) The 242 declined patterns
  of [REQ-PAST-LAST]'s unserved remainder (DFA bodies, hybrids, no single required byte) are not unlocked by this
  feature. Their unlocks stay where review r2-reqpast TH-7 filed them.

## Seams

| seam | writer | readers | facts down | facts up | new calls and their layer direction | text round trip |
|---|---|---|---|---|---|---|
| pcrec to kit presence site (MODULE, D146/D157; contract memfn/include/memfn.h plus integration.md; tests G2) | `req_site_define` (define), `emit_req_reentry_use` (use), src/gen/emit_dfa.c | the kit's presence and compose code (memfn/src) | today: the predicate's parts, `handoff` ASSIGN, `head_max` (K or `MF_HEAD_MAX_UNBOUNDED`), and per use `lo`, `n` = subject end, `on_miss` NOMATCH. NEW (U1): the question's contract, a weaker one ("some occurrence at or after lo"); the read-ahead constraint as a fact about the subject (forward reads, bounded ahead; REQ-OPEN **streaming-meaning**) | today: the leftmost hit or the miss. NEW: an occurrence position with the kit's choice of which; if the kit owns B, nothing else; if pcrec does, nothing new (B is pcrec's) | none new: the same define and use calls. pcrec to kit is a module call, both ways allowed | yes: every new fact is a value in `mf_site`/`mf_hooks` (an enum value or an integer), no text protocol |
| start table to emitter (LAYER, inside pcrec) | the FIRST row chosen by `cand_select` (`CandUse`) | `req_reentered`, `emit_req_landmark_move` | unchanged: `whole`, `reenter`, K | none | none new; one way, down | n/a (in-process records) |
| VM emitter to start-table emitter (LAYER, same level; cross-emitter prototype in internal.h, roadmap H-HEADER) | src/gen/emit_vm.c retry | `pcrec_emit_req_attempt_reentry` | the position variable name | none | none new | n/a |
| emitter to driver (LAYER, wrong way, register 6c) | `emit_req_handoff_rest`, `pf_emit_handoff` write `Job.req_handoff_vm` | the `drop-handoff` rung | — | the flag (existing back-flow) | none new: the feature adds no back-flow | n/a |
| caller contract (spec, D80) | the landing change | callers | `tuning.md` §2.41¶8b (the re-entry sentence), ¶8c (the re-ask, "It can be slower" and its measurement), ¶9 (default); `match_api.md` §6.3.7¶11 (the stamp sentence describing the re-ask); the rows' `desc` in `--list-axes` | — | — | n/a |
| option word (public bit 46 to a test lever; [FLAG-DEMOTE], D195) | axes.def / lib/pcrec.h | `cand_select` (row deny), `cand_nodes[]` world reads | only on the no-loss verdict | — | none | n/a |

## What is deleted

- By the feature: the per-hit re-ask on the re-entering attempt rows (the emitted `if (landmark_position <
  attempt_position) { ... re-ask ... }` asked at every passed hit, C2/C3); `tuning.md` §2.41¶8c's dense-hit caveat
  ("It can be slower ... where occurrences are dense every failed attempt passes one and re-asks") and the same
  sentence in ¶8b, if the measurement removes the loss. On the no-loss verdict only, and through [FLAG-DEMOTE]: the
  attempt rows' public deny coverage (bit 46 keeps the DFA-route `handoff` and NEXT's re-entry).
- By U1: nothing (reason given under U1).
- By P1 (when its trigger fires, not now): the `reenter` bool, the consumer branch in the shared re-entry text, and
  the VM-only route's private retry spelling.

## What the design step must decide

Handed on, not decided here:
- S4/S6: the method within the owner's rulings (blocks, B from a system constant) and the **lookahead-home** answer;
  for the bounded row, whether its move keeps asking the leftmost hit (sparse hits, where it skips far) and how the
  move and the stop share the kept positions.
- S7: B's value and derivation (rule "Tuning constants are suspect"; the owner: show insensitivity across the page and
  chunk range), and where in the artifact it is read (a build-time constant, or a run-time `sysconf` in the artifact:
  a libc call that `<PREFIX>_MEMFN_LIBC` would list, D147 addendum 6).
- S8: the linearity argument for the new form; whether `req_parts_in_whole` stays a conjunct, and why.
- S1/S3: whether the per-hit form survives as a lever. If it does, S3 becomes WIDEN and A-SEAM's step, then P1, land
  first.
- The give-up direction (`tuning.md` §2.41¶9a): a block whose attempts "run unasked" runs MORE attempts than today's
  stop on some subjects. The design shows the direction stays "a give-up may become an answer, never the reverse".
- The measurement card (Frank 2026-10-23), in the method owner's card file (memfn/data/cards if the kit's). The regime
  covers warm and cold memory-mapped subjects (NOTE 2's cold case is "argued, not measured"), dense, sparse and
  early-match subjects, and both comparators (**gate-comparator**). D144 alpha on the Linux box at both kit layers
  (D147).
- Checks that bind the rewritten text and must be re-aimed or shown still to reach ([MECH-REACH]): sabotage rows S1702,
  S1955-S1957, S3074-S3077 and S1700-S1713 (tests/mech/sabotages), `tests/litscan/handoff_vm.rxt` and
  `gen_handoff_vm.py`, `tests/codegen/run_prechecks.sh` and `run_dfa_stamps.sh`, `cand_oracle_witnesses.tsv` (found by
  `git grep -l -E "landmark_position|handoff-attempts|REQ-PAST-LAST|emit_req_landmark_move" $T -- tests scripts`).
- The abi event: the emitted retry text moves, so this is an abi bump with readers found by grep (D76/D94). A kit byte
  move in the same commit is one pcrec abi event (D146/D147, memfn/CLAUDE.md).

## Open questions for the owner

Each has a slug, today's behaviour, an example and the architect's leaning.

- **lookahead-home**: who owns the block look-ahead and its size B, pcrec's attempt loop or the kit? TODAY: pcrec's
  re-entry decides when to ask, after each failed attempt that has passed the kept hit (`tuning.md` §2.41¶7a: "the
  re-entry ... [is] pcrec's"). The kit answers one fixed question, the leftmost occurrence from the position. EXAMPLE:
  `[^@ ]+@x` under `--engine=vm` over 1 MB of ` @x` asks the kit about every 3 bytes. Under blocks it asks about once
  per B bytes, and someone has to know B (the page size, or a stream's chunk). WHY IT SHAPES THE TREE: if the kit
  owns it, U1 asks "any occurrence at or after p", and B is a target fact in the kit's table (D146: pcrec holds no
  architecture knowledge). If pcrec owns it, U1 asks a bounded question, and B becomes pcrec's first system constant.
  LEANING: the kit owns how the position is obtained, B included, and pcrec owns the compare and the stop (NOTE 1's
  "each attempt compares its position with that number"). This keeps D157 (pcrec states the question and the
  constraints, never blocks) and ¶7a (the origin and the stop stay pcrec's). Please also confirm the reading that
  NOTE 3 replaces NOTE 1's "the LAST occurrence ... ONCE" as a method, while NOTE 1's purpose stands.
- **streaming-meaning**: which "streaming" does "also helps with streaming" mean? TODAY: there is no subject
  streaming. `match_api.md` §5.2¶6 says "No partial-match or streaming window state", and [SUBST-STREAM] is deferred
  ("Frank parked streaming 2026-10-23"). `docs/design/stream/` is the INSTRUCTION-stream architecture, a different
  thing. EXAMPLE: a future streaming search of `[^@ ]+@x` over a socket would have only the current chunk to look
  ahead in, so a look-ahead to the subject's end cannot work there, and one block ahead can. LEANING: you mean subject
  streaming. Today B derives from the page size alone, and the chunk is a fact to state when streaming re-opens (D77:
  no hook built now). The instruction-stream roadmap is touched only through A-SEAM/A-PLAN (register lookup).
- **scan-reentry-too**: does the remedy also cover the DFA forward scan's re-entry? TODAY: the forward scan's
  `handoff-reentry` row uses the SAME re-entry text (`emit_req_landmark_move`) and the same per-hit re-ask, at its
  start state. EXAMPLE: `[a-y]\d{0,100}:` over ':'-dense digit text costs x1.537 (known_issues K105). LEANING: not in
  this feature. The shared text takes the remedy through a stated fact of the consumer (no branch on which caller),
  and the forward scan stays byte-identical until K105's own measurement (D77). If the design cannot do that without
  a consumer branch, P1's trigger has fired.
- **gate-comparator**: is "no case slower" measured against today's rows, against the plain loop, or against both?
  TODAY: the bounded row moves each attempt to (next hit − K), which on sparse hits skips far. EXAMPLE:
  `[^@ ]{1,5}@x` under `--engine=vm` over 1 MB with one `@x` every 4 KB. Today each re-ask jumps about 4 KB. A block
  form that ran a "yes" block's attempts unasked would lose that jump, and would be slower than today while still
  faster than the plain loop. LEANING: both. The speed gate (2026-11-17) protects today's numbers, and the no-loss
  NOTE governs only the demotion.
- **split-deny**: may the attempt rows leave `-fno-req-handoff` while the DFA-route `handoff` row keeps it? TODAY: one
  public bit (46) denies all five handoff rows, and the flag audit KEEPS it for K88's loss on back-to-back literal
  matches. EXAMPLE: after a no-loss verdict, `-fno-req-handoff` would no longer turn off the re-entry of `[^@ ]+@x`
  under `--engine=vm`; a `--harness=` lever would. LEANING: yes, through [FLAG-DEMOTE]'s internal deny word (register
  row 15), as that set's own change and not this feature's.
