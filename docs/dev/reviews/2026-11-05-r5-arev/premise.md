# crit-arev premise findings (lens: premise)

Review tree: /home/pcrec/projects/pcrec/worktrees/crit-arev at f15f30f25. Line numbers are that tree's
(same as arev.md's anchors, src/ unchanged since 7cebea04e).

## Findings

### PREMISE-1 — W2's two default forms do NOT go through `emit_reverse_block`; "three walks share one renderer" holds only at `emit_scan_loop`
CONFIRMED (read). Severity: design/doc. Effort: S (re-state §1, §3.3(a), S1's scope). Blast radius: S1's
"0 movers" plan and R28's sufficiency. Design: arev.md header para, §1 "What they already share", §1 table row W2,
§2.1 `dead` row W2; roadmap A-REV "Today" ("all three render through ONE body, `emit_reverse_block`").
- `emit_rev_end` (src/gen/emit_dfa.c:14229) has THREE arms. Only the untagged two-seed arm calls
  `emit_reverse_block(c, &rev, "revend", "continue;")` (:14317).
- `emit_rev_end_one_seed` (:14022) sets `rev->lbl = "revend"; rev->dead = "break;";` itself and calls
  `emit_scan_loop(c, rev)` directly (:14054).
- `emit_rev_end_tagged` (:14081) sets `rev->accv = "revend_dist"; rev->lbl = "revend"; rev->dead = "break;";`
  and calls `emit_scan_loop(c, rev)` directly (:14116).
- So the one-seed and tagged forms (the ones arev's table row W2 names: "(`emit_rev_end` :14229, its one-seed and
  tagged forms)") re-implement `emit_reverse_block`'s two lines by hand, with a DIFFERENT dead hand (`break;`, not
  the `continue;` the table gives W2) and, in form W (`formw`, :14250-14262), a compile-time seed STATE
  (`reverse_state = <cell>` from `revend_seed_state`, `rev.seed = &dfa_seeds[1]`, `entry_set/entry_dead/entry_head`)
  instead of a seed position whose context is read at run time. The §2.1 `seed` field ("the position expression
  the walk starts at, and its right context") has no slot for "the seed STATE resolved at compile time" (form W,
  endmark.md §R.4.6), and the `dead` field's W2 cell (`continue;`) is wrong for 2 of the 3 arms.
- Consequence: (a) the shared body that actually exists is `emit_scan_loop`, which is ALSO every FORWARD walk's
  renderer (:13532 forward search, :14503 the lmverify run, :14581, :14660) — it is the DFA scan renderer, not a
  reverse-walk renderer, so "already share one renderer" proves less than the note leans on; (b) S1 ("W1-W3 fill
  `RevWalk` and `emit_reverse_block` takes it") must also absorb two hand-set call sites plus form W's
  compile-time seed and `accv` (tags), which the step table does not list; (c) R28's recipe (reverse
  `DfaDir` objects minus 1) cannot see these two bypasses, so R28 → 0 would not mean "every reverse walk goes
  through one body". A recipe that would: count call sites of `emit_scan_loop` whose form's dir has
  `reverse == true` outside `emit_reverse_block` (today 2).

### PREMISE-2 — W2 never reads `Job.xrdfa`: on `tagged` the driver SWAPS the whole lowered set into `rdfa`/`dfa`/`nfa`/`rnfa`/`adfa`
CONFIRMED (read). Severity: design. Effort: S-M (re-state §1 row W2, §2.1 `machine` W2 cell, §2.4). Blast radius:
§2.4's "machine per site" table and the S3 builder shape.
- `revend_choose_form` (src/core/compile.c:567-591): on `RF_TAGGED` it swaps `job->nfa<->xnfa`, `rnfa<->xrnfa`,
  `dfa<->xdfa`, `rdfa<->xrdfa`, and `adfa<->xadfa` (:585-590), comment: "On `tagged` the lowered set replaces
  today's in the Job (one lowering per artifact, D164 add. 4)".
- `emit_rev_end` derives its form only from `&job->rdfa` (emit_dfa.c:14266); no emitter reads `xrdfa`
  (`grep -rn xrdfa src/` → internal.h:3489 and compile.c only). After the swap `xrdfa` holds TODAY's machine,
  which nothing emits.
- arev §1 row W2 ("`Job.rdfa`, or the lowered `Job.xrdfa`"), §2.1 `machine` W2 ("R or XR") and §2.4
  ("`Job.rdfa`, `Job.xrdfa`, `Job.lmdfa` become entries of one per-artifact machine table keyed by (site, role)")
  describe a per-walk machine choice that does not exist. What exists is a per-ARTIFACT lowering that changes the
  machine of EVERY walk at once (W1's composite reverse pass on relocate, the forward search, the anchored A that
  W3's verify reads). A (site, role) table that lets one walk take the lowered reverse machine while another keeps
  today's breaks D164 add. 4's "one lowering per artifact" unless the table also carries the artifact-level
  lowering as a fact; §2.4 should say which (a build request `lowered` beside `exact`/`collapsed`, applied per
  artifact) or drop `xrdfa` from the list.

### PREMISE-3 — W1's reverse walk carries NO tag: the D164 B3 distance tag in a W1 artifact is the FORWARD scan's
CONFIRMED (read). Severity: doc/design (one §2.1 cell, one §2.2 row, the G9 sibling count). Effort: XS. Blast radius:
§2.1 `tags` W1 cell, §2.2 "report a tagged end: W1/W2 under D164 B3", §5 "Tagged exits, two members".
- W1 is emitted by `unanch_scan` (emit_dfa.c:13495; arev cites `emit_unanchored`, which only calls it at :13736). The
  tag text in it is `if (fwd->accv) ... unsigned %s = 0;` (:13526) and, after the reverse block,
  `if (fwd->accv) match_end_position -= (size_t)__builtin_ctz(%s);` with `fwd->accv` (:13629-13630): the FORWARD
  form's accept value. The reverse form passed to `emit_reverse_block` at :13625 has no `accv`.
- The one path where W1 runs on a lowered (tagged) artifact is `emit_rev_end_tagged`'s relocate, which passes
  `rel`, copied BEFORE `rev->accv` is set: `DfaForm rel = *rev;   /* the composite's reverse pass reads truth only */`
  (:14087), and sets `fwd->accv = "forward_dist"` (:14158).
- So: W1 `tags` = none (not "none / distance"); among the reverse walks only W2's tagged arm records a distance tag
  (`rev->accv = "revend_dist"`, :14090). `accv` is equally a FORWARD facility (`fwd` :13526, the anchored
  `tf.accv = "anchored_dist"` :14658), i.e. "report a tagged end" is a DfaForm/acc-axis property of every table
  walk, not a reverse-walk exit; the kind should take it from the shared form, not re-declare it.

### PREMISE-4 — W4's `charge` cell cites the wrong mechanism: `vm_charge` is the COMPILE-TIME program-size cap; the revdet walk charges no run-time work at all
CONFIRMED (read + emitted C). Severity: design (G10 and S3's give-up argument lean on a precedent that does not
exist). Effort: XS to restate; S3 must design the charge from scratch. Blast radius: §2.1 `charge` row, §2.5 G10,
§3.1 "The work charge".
- `vm_charge` (src/gen/emit_vm.c:932): `if (++v->nodes > PCREC_MAX_VM_NODES) pcrec_ctx_fail(... "pattern too
  large (VM exceeds %d emitted nodes)")` — a count of EMITTED nodes, "never estimated from the AST beforehand". It is
  called once per `vm_rev_emit` node at compile time (:5527).
- Emitted walk for `((a)|b){0,4}c` (premise/rd.c lines 582-619, compiled from the review tree): no
  `RX_CHARGE_WORK`, no `steps_left` between `// revdet walk: one step back` and `// revdet walk: done`. The only
  `RX_CHARGE_WORK` in the loop (rd.c:564) charges frames discarded by the forward SCAN's cut (`vm_work`, :5853),
  not the walk.
- So "W4: per step, as today (`vm_charge`)" is wrong twice: it is not per step at run time, and today's walk is
  uncharged. A VM-hosted `VK_AUTO` has no run-time charge precedent among the four walks; G10 is new design,
  not a generalization, and §3.1's "one unit per walk, declared" needs its own argument for why an uncharged
  bounded-width walk is acceptable (revdet's is bounded by the committed span; the lookbehind's by W).

### PREMISE-5 — revdet (W4) is a representation of ONE STEP only; its walk loop, stop rule, tag rule and dead hand are a different mechanism the `RevWalk` record does not carry
CONFIRMED (read + emitted C). Severity: design. Effort: M (either widen the record or narrow S2's claim). Blast
radius: §1 row W4, §2.1 W4 column, §2.2 rows "commit" and "tagged end", §3.2 "The fit"/"The step", R03.
What W4 computes (emit_vm.c:5900-5945; rd.c:575-619):
- `vm_rev_emit` (:5521) renders ONE reversed ITERATION of the loop body (`a->u.rep.revbody`), a structural program
  from the cursor to the previous iteration boundary. That part IS a deterministic reverse automaton with a
  unique accept (revdet.c header, REVERSE check: the reversed body admits a unique iteration, U1+U2): the
  "representation" reading holds for the STEP.
- The WALK is the host loop in `vm_revdet_rep`, not in `Rev`/`vm_rev_emit`: `walkl` (`if (cursor <= floor) goto
  wendl`), the step, `wstepl` (`if (prev_position < 0) prev_position = cursor;` then
  `if (groups_seen >= ng) goto wendl; goto walkl;`). Its facts: (a) it repeats the step from each landing (a
  moving seed whose stream is the walk's own result); (b) it STOPS on a predicate over accumulated TAG state
  (`groups_seen >= ng`), an exit neither `farthest`, `first` nor the host's moving-floor/seed loops of §2.2 name;
  (c) its result is TWO different things: the FIRST step's landing (`prev_position`, the greedy retreat's
  `VPOS_REVDET_PREV`) and the group spans from ALL steps; (d) captures are PATH tags written MID-step under a
  first-seen guard (`if (!group_seen[j]) group_span[j][1] = cursor;` at a group's END, seen set only at its START),
  accumulated ACROSS steps — not a value at an accept (contrast D164's `accv`, recorded at the accept,
  `acc_record`, emit_dfa.c:6522-6543); (e) its "fail label" `wendl` is DONE (publish what was seen), never a
  decline: the walk cannot fail the match, so `dead` means "stop" here and "decided/no match" for L — two hand
  types under one field; (f) it reads no context byte below the floor (`cur <= floor` stops; revdet declines any
  assertion in the body, revdet.c shape scan), so §2.1's floor rule "the byte below it is read as context (S74)"
  does not apply to W4.
- Consequences: §2.2's "report a tagged end: either behaviour with `tags` ... W4 (`groups`)" conflates accept tags
  with path tags (a TDFA property, §5's HELD row, which is exactly why a table representation of W4 is not
  available today); S2's "`vm_rev_emit` becomes the kind's structural renderer, unchanged in its text" moves only
  the step — the loop (b)-(e) stays hand-written in `vm_revdet_rep`, so after S2 the moving-seed/stop/publish loop
  is still a private mechanism and R03's restated recipe (`} Rev;` present) would read 0 while it stays.
  `Rev`'s own fields (`cur`, `floor`, `ga`, `gs`, `ns`, `grp`, `ngrp`, `faill`, `loop`; :5490-5500) are emitted
  NAMES for the step renderer; it holds no machine, no seed value (the seed is a separate `VL_RV_CURSOR` LSET
  record, :5915) and no exit, so "describing the same five things in a VM spelling" (§1) overstates it.
- Verdict on the owner's question 2 premise: the STEP is the same automaton in another representation; the WALK is a
  different mechanism (per-iteration chain with an accumulated-tag stop and a first-step side result). The note
  should say which of the two R03 measures.

### PREMISE-6 — the `first` walk behaviour does not exist in the shared table renderer; it is new emission, and the kit-owned stay skips record only the FARTHEST position of an accepting run
CONFIRMED (read). Severity: design/size (S3 scope). Effort: M. Blast radius: §2.2 ("A reverse walk has exactly two
BEHAVIOURS"), §2.3 ("`VK_AUTO`'s renderer ... body is `emit_reverse_block`"), §3.1 rows `exist`/`gate`, S3.
- `emit_scan_loop` (emit_dfa.c:13244) leaves its loop only on dead (`if (... is_dead(...)) break;`, :13334/:13364)
  or at the bound (`acc_emit_tail_*`: `if (at_bound) { bound_accept; break; }`, ~:6604). Every accept-axis row
  (`dfa_accs[]`, :6621: `by-class`, `scalar-viewed`, `scalar-plain`) RECORDS an accept and continues
  (`acc_record`: `if (expr) rec = pos;`, :6522-6533). There is no row or operand that stops at an accept. Among the
  table walks (W1-W3) only `farthest` exists; `first` exists only in W4's structural step, where it is not an
  accept test at all (the program simply ends at the iteration's start, PREMISE-5).
- The stay skips are kit sites (`DELEG_STAY`, `dir_rev_skip` :9249 → `pcrec_memfn_emit`): they advance over a whole
  run of an accepting stay state and then record ONE position, the run's last (`acc_record_const` after the
  advance, :9266-9268); scan edges likewise (`emit_scan_edge`, :12841, accept replays at :12907-12934). A `first`
  that must return the POSITION of the nearest accept would overshoot inside such a run; it would need the skip
  declined at accepting states or the kit site to stop early (a kit change, D146/D147, a pcrec abi event).
- What survives: for the `exist`/`gate` rows only the BOOLEAN matters, so stopping after a skip is sound and the
  overshoot is harmless; `first` there is "stop at any accept", an early-exit optimization of `farthest`, which
  answers the same question. The note should (i) say `first` is NEW renderer behaviour built in S3, not an existing
  one; (ii) restrict its meaning to "existence, early stop" for table machines (position semantics only on a
  machine with at most one accept, where skip overshoot cannot occur only if the skip never crosses that accept);
  (iii) list the emit_scan_loop change (a new loop exit, plus each skip/edge path) in S3's scope and byte budget.

### PREMISE-7 — the record is reverse-only (`RevWalk`), but the roadmap's automaton family and arev's own S4/§5 need the same record FORWARD
CONFIRMED (read). Severity: design (a parallel record built in advance). Effort: S (name/scope the record as the
direction-general automaton operand with `direction` as a field). Blast radius: §2.1, §2.3 (`VK_AUTO` "operands =
one `RevWalk`"), §3.3(b), §5, A-DFATOP/A-HYB/A-ISL areas of the roadmap.
- Manifesto §2 (f15f30f25 docs/design/stream/manifesto.md:49-51): automaton records are "a deterministic machine run
  forward or backward, with a declared exit". The five exits are the manifesto's (held), but they belong to
  automaton records of EITHER direction.
- The roadmap already spells the family direction-general with exit modifiers: `AUTO GATE`, `AUTO COMMIT`,
  `AUTO ENUM`, `AUTO TAGGED`, `AUTO EXISTS`, "reverse `AUTO`" beside plain `AUTO` (subject_roadmap.md:91-96, 147,
  167, 634-646, 730). Forward members there: rows 2/3/4 (`AUTO COMMIT`), 8 (cursor rung, `AUTO ENUM`), 9 (ENG-ISL
  trie, `AUTO ENUM`), 12 (`AUTO TAGGED`/`AUTO EXISTS`).
- arev's own steps lean on a FORWARD automaton record it never defines: §3.3(b) "the anchored forward AUTO
  (verify)"; §5 "`exist` from a forward AUTO run over the subject" ([ENG-LOOK]); §5 "[LANDWALK-FWD] = a forward AUTO
  replacing the verify". In code the forward walks already share the very renderer (`emit_scan_loop`, PREMISE-1)
  and the same tag facility (`accv`, PREMISE-3), and the anchored/lmverify pair repeats the reverse/landmark
  copy pattern on the forward side (`dfa_dir_lmverify` :9460 vs `dfa_dir_anchored` :9412, comment "the anchored
  object's strings, its own name"), and a THIRD spelling of the same "instance name" need exists as a run-time copy:
  `pcrec_emit_dfa_retry` (:14698-14712) does `DfaDir dir = dfa_dir_anchored; dir.c.name = "retry"; dir.statev =
  "retry_state"; ...`. G3 (names per instance) is a direction-general need with three forward/reverse members today.
- So the "two walk behaviours carry all five exits" claim (§2.2) is argued for reverse walks only; a `RevWalk`
  plus a later forward record would be two operand records for one record family (the general-mechanisms rule).
  The fix is cheap at S0: a direction field, `seed`/`floor` read as start/bound, and §2.2's table restated per
  direction (forward `farthest` = longest end, `first` = earliest end; ENUM = the cursor rung's monotone ends).

### PREMISE-8 — smaller §1 premise errors (location, sharing, provenance)
CONFIRMED (read). Severity: doc. Effort: XS. Design: §1 table W1, "What they already share", header para.
- W1 is `unanch_scan` (emit_dfa.c:13495), the reverse block at :13625; `emit_unanchored` is one of its FOUR callers
  (:13736, plus W2 tagged relocate :14161, W2 two-seed relocate :14364, W3's relocate :14513). So W1 is also the
  LOWER/ENDSET FINISHER of W2 and W3: a W2/W3 artifact with a relocate holds TWO reverse walks in one function
  (that is why `dfa_dir_landmark` needs its own state variable name). §1's finisher column ("search-from relocate")
  hides that the relocate is another instance of the kind; §2.3's finisher contract should list "another
  `RevWalk` (W1) after a forward scan" as a FINISH row's body.
- "one optional machine builder shape (`revend_build_one` ...; `lmwalk_build` is its second caller)" as a W1-W3
  share: W1's machine and W2's untagged machine are the MANDATORY `Job.rdfa`, not built by `revend_build_one`
  (compile.c:454; its callers are `revend_build_marked` for `xdfa`/`xrdfa`/`xadfa`, two of them FORWARD, and
  `lmwalk_build` :547). The builder is shared by optional machines of both directions, not by the reverse walks.
- "This is roadmap r1 U3's 'one walk emitter', built in p1build": `emit_reverse_block` was introduced by fddd803ac
  (2026-10-10, "[OPT-REVEND] L1 ... the seeded reverse-block helper (S1)"); p1build (6a86bb830, 2026-10-29) added the
  landmark caller and `dfa_dir_landmark`, i.e. the R28 copy.
- §1 quotes `dfa_dir_landmark`'s comment ("the reverse object's strings character for character under its own name"):
  the object differs from `dfa_dir_reverse` in `ind`/`bind`, `tbl_hdr` and `acc_meaning` too (:9442-9457 vs
  :9360-9375); the note's "to get a new state-variable name and indentation" is the accurate half.

### PREMISE-9 — the three A-REV ratchet recipes count SPELLINGS a rename or a move zeroes, and R28 cannot see the members PREMISE-1 found
CONFIRMED (read; recount below). Severity: maintenance (check design; learnings §3, "controls that share a source with
what they control"). Effort: S. Design: arev §4.3, roadmap §5 rows R03/R10 and proposed R28.
- Recounts at f15f30f25 (= 7cebea04e for src/): R28 as written = `static const DfaDir` objects with `reverse` true
  (`dfa_dir_reverse` :9360, `dfa_dir_landmark` :9442) minus 1 = **1** (agrees). R03 restated (`} Rev;` in emit_vm.c)
  = **1** (:5500, agrees). R10 (`emit_landmark_walk` present) = **1** (:14398, agrees). Ratchet sums in roadmap §5:
  24 at 3f777330e and 29 at p1build's merge re-add correctly from the table's columns.
- R28 → 0 by turning the landmark direction into a run-time copy (`DfaDir dir = dfa_dir_reverse; dir.statev = ...`,
  the shape :14700 already uses for the anchored one) without any `RevWalk`; and R28 never counted the two
  hand-set `emit_scan_loop` reverse call sites (PREMISE-1). R03 → 0 by renaming `Rev` to `RevWalk` while
  `vm_revdet_rep`'s private walk loop stays (PREMISE-5). R10 → 0 by renaming or splitting `emit_landmark_walk`.
- Each recipe reads the NAME of what the step deletes, so the step that moves it also moves the count, whether or
  not the mechanism was unified. Recipes that measure the claim: R28' = reverse-direction `DfaForm`s rendered by
  any path other than the kind's one entry (count call sites of `emit_scan_loop` with a reverse `dir` outside
  `emit_reverse_block`, plus reverse `DfaDir` objects minus 1: today 2 + 1 = 3); R03' = loops over a reverse walk's
  result written outside the kind's host loop (today: `vm_revdet_rep`'s `walkl`/`wstepl`, W2's seed loop, W3's
  hit loop, i.e. the §5 "moving-seed, three members" family, minus 1); R10 as P-d states it ("renders as existing
  kinds": no `pcrec_sb_puts`/`printf` of loop text in the walk's emitter).

## PROBED-AND-HELD

- **Priority target (1), the landmark walk's rendering path: HOLDS.** `emit_landmark_walk` (emit_dfa.c:14398) renders
  its REVERSE walk through `emit_reverse_block(c, &ml, dfa_dir_landmark.c.name, "{ landmark_position++; continue; }")`
  (:14489); the hand-written part is the OUTER search loop (LMHIT `find_use`, the reach guard, the inline
  `lmverify` scan `emit_scan_loop(c, &av)` :14503, the relocate `unanch_scan` :14513), which is what R10 counts. Emitted
  C for `a+b` (route `RX_DFA_SCAN "landmark-walk"`, premise/p_f1d53b.c:401-420) shows `rx_landmark_state
  landmark_state` inside the walk block. arev distinguishes the two correctly (S1 vs S4); no contradiction with R10.
- W1 RECOVER reverse pass goes through `emit_reverse_block(c, rev, dfa_dir_reverse.c.name, NULL)` (:13625); W2's
  two-seed arm through `emit_reverse_block(c, &rev, "revend", "continue;")` (:14317). (W2's other two arms: PREMISE-1.)
- `emit_reverse_block` (:13409-13416) "only sets the form's `lbl` and `dead` and calls `emit_scan_loop`": exact.
- §1 premise-test anchors, all 14 checked at the review tree: `Rev` :5500, `vm_rev_emit` :5521, `vm_revdet_rep` :5705
  (emit_vm.c); `VK_CONSUME_BACK` vm_stmt.h:59; `vm_r_consume_back` vm_stmt.c:403; `dfa_member_machines` :4916 with
  `out[4]` and four bits F/R/A/ML; `struct DfaDir` :5787; `dfa_dir_reverse` :9360, `_landmark` :9442, `_lmverify`
  :9460; `emit_scan_loop` :13244; `emit_reverse_block` :13409; `emit_landmark_walk` :14398; `lmwalk_build` compile.c:547,
  `revend_build_one` :454; `CAND_ML` internal.h:9285; `NFA_ERASED_*` enum after `Nfa` (internal.h:2430-2440);
  `lmwalk_conj[]` lmwalk.c:276; `rx_reverse_accepts_class` absent and the accessor emitted per machine (:6154). 14/14.
- W3 machine "built only where `lmnfa.erased == 0`": compile.c:549-552 holds. W3 seed `landmark_position + 1`,
  floor `search_from` (`dfa_dir_landmark.at_bound = "rewind_position <= search_from"`), exit farthest, dead → next
  hit, finishers verify-at inline / LOWER relocate (asserted :14411-14419): all hold.
- The count-collapse arm (§2.4): nfa.c:845-849 `if (b->collapse && (rmin > 1 || rmax > 1)) { rmin = rmin ? 1 : 0;
  rmax = -1; erased |= NFA_ERASED_COUNT; }` = `X{m,n}` → `X{min(m,1),}`: holds.
- revdet's (U1)/(U2) on the REVERSED body (§2.2 "the reversed body is prefix-free"): revdet.c:24-33, the REVERSE
  check applies the unique-iteration predicate (U1, U2, non-nullable) to the reversed body: holds.
- W4 floor = entry slot (`flr = "(size_t)slot_values[se]"`, emit_vm.c set by `vm_set(v, se, scan_position)`), seed
  `rv<i>_cursor = scan_position` (:5915), hosted as records `VK_CONSUME_BACK`/`VK_BRANCH`/`VK_LSET`: holds (emitted
  rd.c:582-619). Answer check: `((a)|b){0,4}c` on `abac`: pcrec `match 0 4`, libpcre2 10.46 `[0-4,2-3,2-3]` (span agrees).
- Priority target (4), the five exits ARE the manifesto's: manifesto.md:49-51 "commit to one end, enumerate ends in
  preference order, act as a gate, test existence, or report a tagged end". Holds (scope caveat PREMISE-7; tag kinds
  PREMISE-3/5; `first` PREMISE-6).
- "Enumerate = `farthest` with a moving floor" gives PCRE2's order for a lookbehind's candidates (ascending start =
  longest first, regardless of laziness, then the body's forward preference with the end pinned; top-level branches
  in written order). libpcre2 10.46, 6 cells: `(?<=(a{1,3}))x`/`aaax` → g1 0-3; `(?<=(a{1,3}?))x`/`aaax` → g1 0-3 (lazy
  still longest); `(?<=(a|aa)(a?))x`/`aaax` → 0-2,2-3; `(?<=(a?)(a|aa))x`/`aaax` → 0-1,1-3; `(?<=(a)|(aa))c`/`aac` → g1
  1-2 (branch order beats length, arev §3.1's WD2 confirmed); `(?<=(a{1,2})|(a{2,3}))c`/`aaac` → g1 1-3. Also
  `(?<=(a+))x` REJECT 125 (unbounded), consistent with arev's non-goal.
- Rev-end route population: both `ab$` and `(a|ab)c$` compile to `RX_DFA_SCAN "rev-end"` and emit the ONE-SEED arm
  (premise/p_476952.c:197, p_32a279.c:386), i.e. the arm that bypasses `emit_reverse_block` is the common one (feeds
  PREMISE-1's severity). `[ab]+[bc]` → `"unanchored"`, `a+b` → `"landmark-walk"`, matching arev §9.
- Ratchet arithmetic (roadmap §5): 24 at 3f777330e and 29 at p1build's merge re-add from the table's columns; R28 = 1,
  R03 restated = 1, R10 = 1 at the build commit (PREMISE-9).
- §2.3 precedent: `pcrec_emit_dfa_engine` (emit_dfa.c:15988) exists, called from emit_comb.c and referenced by the
  VM hybrid's inlined body (emit_vm.c:11403, `.hybrid = cx->job->fit.prefilter` :14170): the precedent exists (its
  "static function called from the loop" shape not re-verified beyond these anchors).

## Questions for a pcre2-reader

- None needed: the enumerate-order fact was settled from libpcre2 10.46 as a library (6 cells above). The ORDER for a
  NEGATIVE variable lookbehind with captures is not observable (no captures escape a negative assertion).
