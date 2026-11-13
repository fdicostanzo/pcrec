# Review 2026-11-12 r? — memfn Part D design rev 2 (critic round memfn-partd2-1112, design mode, a NARROW RE-CHECK)

**DRAFT by the coordinator. Dispositions are PROPOSED; the kit manager (and main, for the pcrec-side
and joint items) rules them.** Critic texts, COMMON and the verifier's file: `review/` beside this file
(fix.md, ready.md, seam.md, verify.md, COMMON.md).

## Subject and freeze

- Subject: `docs/design/memfn/part_d.md` **rev 2** at `92976462f` (branch lane/memfn-pdesign, tip
  b2b944dfe), the kit's answer to review `2026-11-12-r1-memfn-partd` as ruled (FIX-NOW F1-F12,
  F14-F21, F23-F26; DOC F13, F22; F26 direct translation IN; F9 scoped; F11 R BY ROLE, joint).
- Build tree: main `0f1d54089` (later than the design's base 35bee4da9; nothing under memfn/, src/,
  cli/, lib/ moved between them, only two tests/startset manifests). Review tree built there once
  (`nice make -j2`, rc 0).
- Client design in force: `docs/design/run_pos_set_stage3_readiness.md`, last changed at 14570db62, an
  ancestor of the subject; unchanged on main through hand-back.
- Rulings frozen at decisions.md/plan.md `0f1d54089`. Re-diffed at critic return and at hand-back:
  plan.md +6 lines (a new [ASK-DEFINE-FRAME] row, unrelated); decisions.md unchanged. **No freeze
  drift that touches the subject.**
- FREEZE NOTES: (1) F26's and F9's rulings have their ONLY record in the r1 review's Rulings section,
  on the lane branch (not yet on main). (2) F11's record is plan.md [RUN-POS-SET]'s NOTE of
  2026-11-12; its wording "any multi-position verify-NO span pcrec states is R" is broader than the
  ruling's intent (see P14).

## Lenses as run

| lens (file) | model | the one question | why chosen |
|---|---|---|---|
| fix-induced (fix) | opus | (a) does each `[r1pd Fn]` fix close its finding without opening one: trace what it ADDS, its unstated siblings, pairs of fixes on one check; (b) per-unit verdicts for D0 and D3 | a re-check of a revised design (launcher-chosen); D0/D3 verdicts folded here under the 3-critic cap |
| readiness D1+D2 (ready) | opus | per unit: cites at the build tree, completeness by own grep, loaders over new row shapes, the deny applied literally, can its code land and checks pass alone, can each plant red | last check before a build go (launcher-chosen); one critic for two units because of the cap |
| seam round trip (seam) | opus | for each NEW STATE of existing fields (R by role, the decline, the scan-less run, set_leads -1 on a stated run), every reader on BOTH sides that infers one field from another; F11's text round trip; sibling-of-family and general form + unlocks | the r1 round's top process note: F1-F3 were all that shape |
| verifier (verify) | opus | re-derive every finding that would change the design or a unit's check; resolve the RDY-8 / SEAM-8 conflict | opus because two critics' mechanisms conflicted |

All three critics and the verifier returned complete files in the launch turn (11-18 min; verifier
7 min); no resend, nudge or replacement.

## Which lens caught what

- **Every lens independently found the same G1 hole** (P1: pcrec's head-part `need`), the third
  time this shape appears in two rounds: a pcrec-side reader of "a stated run" on the decline.
- The seam lens found the pcrec-side readers no kit-side review sees (P3, P4, P8, P15-P17), and the
  overbroad R-by-role sentence (P14).
- The fix-induced lens found what F4's scan-less body ADDS (P2, P9) and F26's census consequences
  (P12-P13 with ready), and the G2 presence driver that never renders a decline (P6).
- The readiness lens found what the units' checks cannot do: the inert witnesses (P5), a reference
  model left on the old rule (P11), a dead plant (P12), and loader rules for a `fn` row (P10).
- Overlaps (consolidated): P1 (fix, ready, seam); P2 (fix, ready); P7 (ready, seam); P13 (fix, ready,
  two pairs).

## Overall verdict (proposed): NOT READY as a whole; D0-D2 READY WITH LISTED TEXT FIXES once four small decisions are ruled; D3 NOT READY

Per unit:
- **D0 — ready with listed text fixes**: P18 (set-position rate rule and the other `run[]`/`mask[]`
  readers), P11's base-count split, and which §5.2 floors are armed at D0 vs D2.
- **D1 — ready with listed text fixes, after decision P3**: P1 (the §9 line), P4, P5, P6, P7, P13
  (finder_check), P19, P20.
- **D2 — ready with listed text fixes, after decision P9**: P2, P10, P11, P12, P13 (census, emit_sweep
  cells, S1409/S3009), P14, P21.
- **D3 — NOT READY** (P9, P15): its census has no record to read after F26, and its floor is zero
  until the joint landing, so its plant cannot red at D3.

Why not "ready with listed text fixes" overall: one G1 compile failure on every declined run with a
member (P1; one clause, but on pcrec's side where the kit's checks cannot see it), an out-of-bounds
read on every scan-less part (P2), and four small open decisions (P3 P2 on a decline, P8 the pick
shadow, P9 the scan-less body's card, P15 D3's record). None needs a redesign. **Proposed next step:
a rev 3 with the FIX-NOW items, then no full round**: one readiness critic on D3 plus a diff check of
P1-P3's text by the manager.

## Findings (consolidated; ids P-n; source ids in brackets; verifier verdict)

### G1 / answer level

- **P1 — pcrec's head-part `need` is chosen by `run >= 0`: every declined run with a verified member
  fails `mf_define`** [FIX-6, RDY-9, SEAM-4; verify HOLDS, code read both sides, stage-3 INFERRED].
  `src/gen/emit_dfa.c:1509-1510` `if (run >= 0) gate_need = (mf_need)s->pspans[head].need;` (OPTIONAL
  on every non-VM-attempt route, :1409); D1 makes `pres_layout_check` (compose.c:697-701) expect
  REQUIRED where the run is untested, and `part_is_byte` compares `need` exactly. §9 item 2 names
  only the next line's check. Reaches F1's and F2's own witnesses (where their route reaches the
  pre-check, P5). NOT CLOSED (r1 F2's pcrec half). **PROPOSED: FIX-NOW** — §9 item 2 names
  `gate_need` with the check: both read `pres[run].verify`; same rule for G2's layout (P6).

- **P2 — the scan-less predicate reads `term[255]`, and `fn-walk` "above `fn-memchr`" sits below
  `fn-pair`, which holds on it** [FIX-1, RDY-4; verify HOLDS; libc-note sub-claim SUSPECTED].
  `ofs_fn_scan` (ofsskip.c:141) reads `p->term[p->plan_hint]` unguarded (`MF_NO_PRED` 0xFF,
  `MF_MAX_TERM` 32); callers `fn_define` :631 (every derived part), `run_comment` precheck.c:156,
  `ofs_fn_serves` :483, `legend_at`/`legend`; `ofs_fn_applies` reads it at :127. Guarding the call
  leaves `x.b` 0 and `pair_holds` (`x->b >= 0`, :376) true, so first-match `fn-pair` renders a pair
  body on byte 0 (wrong answer on a MATCHING subject, INFERRED; F4's witness answers nomatch by
  accident). `fn_define` notes `memchr` for every body (:632-634), which a `fn-walk` body never
  writes (libc_census equality, SUSPECTED). NEW (opened by F4). **PROPOSED: FIX-NOW** — `fn-walk` is
  the FIRST BODY row; `ofs_fn_scan` and its callers listed in §3.1 with the `MF_NO_PRED` guard; the
  libc note is the body row's own; a G2 floor "scan-less REQUIRED runs on a MATCHING subject".

### Design (decisions)

- **P3 — P2's "still requiring `proof->run`" makes `dominated` UNREACHABLE on a decline; F3's
  witness row assumes a proof pcrec never states** [SEAM-8; verify HOLDS]. pcrec's `proof.run` is
  `cs->run_verified` (emit_dfa.c:8719-8723), set only on offset rows and only where the kit's earlier
  ask TESTED the run (`ofs_test_verifies_run` :7502). So on a decline it is 0 on every route, and kit
  P2 (presence.c:321) gives `dom` 0. `x.(?:cat|dog)` (today `_REQ_WHY "dominated"`, MEASURED) gets a
  same-byte `memchr('x')` pre-check in front of a `memchr('x')` body at stage 3 (the double pass
  emit_dfa.c:8573-8576 exists to remove), and `_REQ_WHY` moves to `emitted`. PARTLY (r1 F3: the
  admission hole is closed, but its witness and the dominance outcome are not). **PROPOSED: FIX-NOW
  (decision, kit manager)** — leaning SEAM-8's: where the run has no scan (`SF_RUN_NOSCAN`, known
  before P2), P2 treats the run span as run-less (dominance by the set pick; the run span `proven_by`
  with the rest), and the F3 witness row is rewritten with pcrec's real proof.

- **P8 — the pick shadow's `leads`/`rlead` expectation recomputes the kit's scan from shape: it
  disagrees at stage 3 on declined runs and on findable wide runs, and `run_pres_picks.sh` allows no
  disagreement** [SEAM-3; verify HOLDS as a gap, the stage-3 disagreement INFERRED].
  `req_set_leads_own` (emit_dfa.c:11109-11125) ranks EVERY position by `pcrec_find_run_scan_index`;
  rev 2 makes the kit's scan the least-mass FINDABLE position (a private rule) and `set_leads` -1 on
  a no-scan run. Correcting the expectation needs either the reply (shares the control's source,
  K35) or pcrec re-implementing "findable" (D157, what F11 forbids). §9 item 5 names `rdom`/`rlead`
  with no rule and omits `leads`. NEW. **PROPOSED: FIX-NOW (decision, main + kit)** — retire `leads`
  and `rlead` as independent expectations on runs with a non-cube position, as K38-2 retired
  `scan`/`rwin` (:11289-11292), naming the successor control (C2 and G2's decline equality).

- **P9 — `fn-walk` is not card `walk`: the scan-less body is an UNCARDED form, so G4's "no new
  method" and D3's "counted" rest on a card that measures something else** [FIX-2; verify HOLDS].
  formhash.c:296 `walk` = `MF_FH_FIND` on `pf_walk` over a TABLE; :285-290 "with no table the composer
  renders the generic byte loop, which is not the walk". The name also misdescribes behaviour (D174).
  NEW (opened by F4). **PROPOSED: FIX-NOW (decision, kit manager)** — add its card in the same change
  (memory `pcrec-new-method-needs-measurement-card`) or state it UNMEASURED with a visible row; rename
  to what it does (e.g. a "verify every candidate" body).

- **P15 — D3's widened census has no record to read after F26, and its floor is zero until the joint
  landing** [FIX-12; verify HOLDS; the sweep's collector not opened]. `vcls.py:96-118` and
  `census0.py:250-254` read window statements (`alts`) and the family reply (`wr`); F26's direct
  translation writes TERMS only, no `alts`, no `wr`. The K35 floor ("pcrec's artifact count of
  stage-3 run parts") is 0 on the kit branch, so the plant cannot red at D3. PARTLY (r1 F19).
  **PROPOSED: FIX-NOW (decision)** — name the record (the derived part's terms as handed to ofsskip,
  or an MFTRACE line `run_part_terms` prints), and either arm D3's check at the joint landing only,
  saying so, or give it a pre-landing floor from G2's rendered wide sites.

### Readiness (a unit's own check cannot pass or cannot fail as written)

- **P4 — `set-leads` admits on a decline: pcrec's lead reader reads "a run is stated", not the kit's
  `set_leads`** [SEAM-2; verify HOLDS]. `req_pres_head(lead=true)` (emit_dfa.c:8761-8769) returns the
  verified order-0 member whenever `run >= 0`; `req_set_leads_applies` (:8661-8668) never reads
  `set_leads`. On a decline the row's text ("the set pick's memchr first, then the run search") is
  false, the CT_HIT census attributes the site to it, and `rlead` contradicts `leads` on the same
  site. `_REQ_WHY` unchanged. NEW (the F2/F5 shape, pcrec side). **PROPOSED: FIX-NOW** (§9 items 2/5:
  the lead reader reads a TESTED run).

- **P5 — the F2 and F7 witnesses never reach the code they witness on the default route: the cover's
  LOCATE-whole dominates them before any kit ask** [RDY-8; verify PARTLY: RDY-8's mechanism (cover
  proves the run) REFUTED, the conclusion HOLDS by `req_dominated_applies`' LOCATE-whole branch,
  emit_dfa.c:8627-8632]. Today MEASURED: `[a-z]{8}.q` and `\d{3}-\d{4}` `cover`/`dominated`,
  `\d[aA]\d` `cover`/`none` (its `none` becomes `dominated` once a run is stated, INFERRED). Under
  `--memfn=no-window-search` they take offset/byte-class rows and DO reach the decline. NEW.
  **PROPOSED: FIX-NOW** — witness F2/F7 under `--memfn=no-window-search` or on a prefixed shape
  (`(a|bc)\d{3}-\d{4}`); the D27 author's list inherits the caveat.

- **P6 — G2's presence family returns before render on an untested run link: a declined site is
  never laid out, rendered or oracle-checked** [FIX-7; verify HOLDS]. `g2_pres_gen.c:571-592`
  (`if (!tested) { ... return; }`); its layout writes the head's need as `g_ps[head].need` (:541),
  the `run >= 0` reading of P1. So the rendered half of F1/F2 is seen only by pcrec, the gap r1's
  lesson 1 named. NEW. **PROPOSED: FIX-NOW** (D1/D2 text, M) — split the branch; the layout's head
  need by `trun`; floors "declined sites rendered and oracle-checked" and "declined with no verified
  member: no pre-check"; `g_p2_untested` must not count declines.

- **P7 — at D1 alone, every scan-less REQUIRED run refuses in `derive_run_part` under a message no
  gate counts** [RDY-1, SEAM-7; verify HOLDS the fact]. window.c:2547-2551 refuses
  `!rr->has_scan || !rr->ver_len`; D1 adds P0's `has_scan` 0 reply, D2 deletes the function. Either
  D0's "any other message FAILS" gate reds at D1, or (if D0-only) the landing condition "K-1 count at
  most D0's base" is met BY the message move. PARTLY (r1 F14). **PROPOSED: FIX-NOW** — D1 relaxes
  :2547 to `!rr->ver_len` (falls to the K-1 refusal), or D1's check counts both messages.

- **P10 — `fn-walk`'s row cannot take "D1's obligations": rows_check exempts only `fd` rows from a
  fixture witness** [RDY-5; verify HOLDS]. `rows_check.py:811-819`; check C demands a control
  fixture. NEW. **PROPOSED: FIX-NOW** — an arm_fixtures site (REQUIRED all-wide run: scan-less) with
  its control (one findable position: `fn-memchr`), `FIXTURE_FLOOR` +2; or a pcrec witness at the
  joint landing.

- **P11 — D2 moves the G2 window GENERATOR's R model but not its REFERENCE `run_of`: the correct
  build reds DECIDE and plant p8 stays green; `two_runs`' new fix leaves two spelled verify-YES
  spans unfixed** [RDY-6, FIX-5; verify HOLDS (RDY-6), PARTLY (FIX-5: the verify-YES-only half
  holds; the "fix creates the shape" half depends on unwritten `wf_check` text)]. `g2_win_ref.c:127-138`
  (shape, any verify), `g2_win_run.c:98-104`; `g2_win_gen.c:569-582`, :426. PARTLY (r1 F22).
  **PROPOSED: FIX-NOW** — D2 moves `run_of` too; `two_runs` keeps the three-member fix for a second
  spelled verify-YES span; a floor on chosen wide-R alternatives with an exact member (p8's reach);
  D0's base count split by verify.

- **P12 — plant p9 (the scope dropped) has no detector that can red** [RDY-7; verify PARTLY:
  structure HOLDS, magnitude unverified]. emit_sweep cannot see it (pcrec's population is 0 by §6
  C7's own premise); `FORM_FLOORS` are one-sided minimums (run_g2.sh:357-361). NEW. **PROPOSED:
  FIX-NOW** — a two-sided pin (G2 counts OFS/STMT sites with a tableless multi-member SET term or no
  scan rendered by ofsskip: exactly 0 while the scope stands), or a fixture control.

- **P13 — row, census and pin obligations the unit lists miss** [verify HOLDS each, pins quoted]:
  (a) D1: `finder_check.py:152` `PRES_ROWS` and the table-size check red on the new row; `B3B_PRES`
  is the natural decline fixture [FIX-10, RDY-2]; (b) D2: `decider_census` `translate:run-rank`
  (tsv:57), `RUN_CALLERS` (exact), `MEMBER_COUNT`, and S3006's anchor move with the shared ranking
  function [FIX-4, RDY-3]; (c) D2: the new deny arm needs `emit_sweep` `ASSERT_ZERO` cells, which
  become `DIFFER_PINS` with a floor and a stage-3 manifest at the joint landing (:1868-1876, "NO
  DIFFER FLOOR PINNED") [FIX-8]; (d) D2: S1409's anchor (`run_g2_win.sh:121-122`) is the message
  §2.2 rewrites, and the verify-YES span's uniqueness rule has no plant; S3009 re-anchors if
  `kit_run_opts_of` carries the deny; state the deny's carrier [RDY-10; S3009 SUSPECTED]; (e) §4
  reason 1's "re-pinned in decider_census.tsv, arm_fixtures --finder-rows and S1122" names no pin of
  a row INDEX; the order pin is finder_check (a) [RDY-11]. PARTLY (r1 F15). **PROPOSED: FIX-NOW**
  (text).

- **P14 — the R-by-role sentence is unscoped: pcrec states a SECOND multi-position verify-NO span,
  the run presence span** [SEAM-6; verify HOLDS]. `emit_dfa.c:1426` (`req_pres_spans`) states
  `pcrec_memfn_wspan(sp, 0, run->whole_len, MF_VERIFY_NO)`, which the kit REQUIRES verify NO
  (compose.c:571-572). §2.2's "the only multi-position verify-NO span among them is R itself" is
  false; no byte moves (that span never reaches `merge`), but the new `mf_wspan.verify` text and the
  plan note's wording make it an R. NEW. **PROPOSED: FIX-NOW** (text: scope to a window site's
  alternative, correct the count) **and ask main to scope the [RUN-POS-SET] NOTE's wording the
  same way**.

### Text and doc

- **P16 — spec sentences that read "a run is stated" as "the run is the landmark / is scanned"**
  [SEAM-5]: `match_api.md` §6.3.7¶11 (the LANDMARK is the run where `_REQ_RUN` is not "none"),
  `tuning.md` §2.41¶1 and ¶7a, §2.28¶1, §2.29¶4. PARTLY (r1 F25). **PROPOSED: FIX-NOW** (add to §4's
  hunk list and the readiness memo §2.3).
- **P17 — two emitted comments that read the run's scan or landmark from the wrong field**
  [SEAM-1, SEAM-9]: `req_note_run` (emit_dfa.c:1150-1181) prints "the scan is on byte ... at offset 0"
  on a scan-less run; `emit_req_handoff_rest` (:1089) names the whole run on a decline. Emitted text
  (abi-carried). NEW. **PROPOSED: FIX-NOW** (§9 items 2 and 4 name both).
- **P18 — D0's conversion leaves the rate rule for a SET position unstated, and the natural one
  makes F24's floor 0** [FIX-11; SUSPECTED]. `gen_rates` (g2_pres_gen.c:247-266) and further
  `run[]`/`mask[]` readers (:503, :770, :830-832, g2_pres_run.c:569). p1 itself still reds via the
  decline equality (ready's PROBED). PARTLY (r1 F24, F16). **PROPOSED: FIX-NOW** (text: the rule, the
  readers, F24's count recorded > 0 at the base).
- **P19 — memfn.h `mf_link`'s MEMBER and ORDER texts keep "no run is stated", the D27 author's
  source** [FIX-9]. memfn.h:1191 area. NEW. **PROPOSED: FIX-NOW** (D1's memfn.h list adds them).
- **P20 — the decline row's `facts`/`nofacts` are unstated** [FIX-3; verify PARTLY: the gap holds,
  the claimed `test-axes` red is unreachable from pcrec's statements]. **PROPOSED: DOC** (one
  sentence: OPTIONAL + `SF_RUN_NOSCAN`, no `nofacts`).
- **P21 — the scoped `ofs_fn_applies` argument's caller list**: it omits `ofs_fn_serves` (the window
  family's B-pair, window.c:1916-1918) and names the BODY walk and G2's families, which never call it
  [FIX-13]. **PROPOSED: DOC.**
- **P22 — floors for p4's and the F1 twin check's reach** ("declines with a verified member",
  "declines on ASSIGN sites") [RDY-11]. **PROPOSED: FIX-NOW** (text).

### Standing questions (seam)

- **P23 — sibling family: "this position has a `(T, K)` spelling" is written four times** (the
  `findable` column, the scan stretch, the verify-YES pinned span's test, `run_bytes`' refusal),
  beside `in_stretch`; pcrec's side has the same for "a run shipped" (`whole_len >= 2`, `run >= 0`).
  **PROPOSED: FIX-NOW (design text, cheap)** — one kit accessor read by all, one plant; one pcrec
  predicate "the pre-check tests the run" (memory `pcrec-general-mechanisms-not-special-cases`).
- **P24 — general form**: a presence link's TEST KIND = f(need, findability), per span, not per run
  (findable: find + verify; not findable and REQUIRED: verify every candidate; not findable and
  OPTIONAL: untested). Unlocks: C1/C2 drop in as new find methods with no new state; P2 reads the
  same table (P3). **PROPOSED: NOTED** — a §6 row with C1's trigger or "the first member span with no
  find form".

## PROBED-AND-HELD (summary; counts in each critic file)

- r1 fixes CLOSED with no new finding (fix): F3's placement, F5, F8, F10, F12, F13, F16 (its three
  functions), F17, F18, F20, F25, F26 (the ranking over the stretch answers the global scan first:
  the TIE rows are translation-invariant strict orders, window.c:874-884; ready agrees).
- Cites: fix 24/24, ready all named functions and 11/11 sabotage ids exist and target what part_d says;
  `MF_WSPAN_POS` = `MF_MAX_TERM` = 32, `MF_NO_PRED` 0xFF.
- The D2 deny applied literally: identity on every mode today (no wide position exists; 4 today
  artifacts compiled), and it compiles the design's witnesses (F7's one-position stretches become
  `run_len` 1 RUN terms that `ofs_fn_applies` admits; ready).
- Loaders: the D1 decline row loads as an `fd` `pending-site:` row; `run-verify-wide` parses; the
  `--list-axes` floor is `>=` (ready).
- Seam: `req_run_at` reads `has_scan` before `scan` (§9 item 4 holds); `pres_row` resolved by id
  survives the index shift; decline only on OPTIONAL, scan-less only on REQUIRED (`req_pres_spans`
  :1409); `xy/users\d+` today `run-pinned`, offsets `0*,1,..,7`, `@0` (MEASURED), and keeps them under
  R by role (INFERRED); no pcrec reader infers R or the pinned row from shape (the only shape
  inference of the kit's scan is the trace shadow, P8). 31 pcrec + 17 kit readers traced.
- G3 at D1 by construction (ready): today's run is never untested outside P2.
- Witnesses run: 9 + 7 + 6 single compiles; 5 answers against python3 `re` (F1, F2, F3, F7 x2): all
  agree today.

## By-id completeness

fix: FIX-1 P2, FIX-2 P9, FIX-3 P20, FIX-4 P13b, FIX-5 P11, FIX-6 P1, FIX-7 P6, FIX-8 P13c, FIX-9 P19,
FIX-10 P13a, FIX-11 P18, FIX-12 P15, FIX-13 P21. ready: RDY-1 P7, RDY-2 P13a, RDY-3 P13b, RDY-4 P2,
RDY-5 P10, RDY-6 P11, RDY-7 P12, RDY-8 P5, RDY-9 P1, RDY-10 P13d, RDY-11 P13e+P22. seam: SEAM-1 P17,
SEAM-2 P4, SEAM-3 P8, SEAM-4 P1, SEAM-5 P16, SEAM-6 P14, SEAM-7 P7, SEAM-8 P3, SEAM-9 P17, standing
questions P23, P24. 33 critic findings + 2 standing answers -> 24 consolidated; none dropped.

## D27 recommendation

Already ruled YES at build. Its witness list (§5.1) inherits P5 (F2/F7 need a route that reaches the
pre-check) and P3 (F3's "with it" column is not what pcrec's real proof yields).

## Lessons for the guide (proposed)

1. **Adopt r1's lesson 1 into the seam lens, extended to trace shadows and emitted comments.** The
   same G1 hole (P1) was found by all three lenses, and the seam lens's new-state enumeration found
   five more pcrec readers (P3, P4, P8, P17x2) that r1 and rev 2 missed. Proposed lens-table text,
   seam round trip: "When the subject introduces a new STATE of existing fields, enumerate every
   reader on the OTHER side that infers one field from another, INCLUDING trace-build shadow
   expectations and emitted comments, and hand-execute each on the new state."
2. **A witness must reach the code it witnesses at its unit's route.** P5: three of the design's own
   witnesses are dominated before any kit ask on the default route. Proposed readiness clause: "for
   each witness, compile today's half and name the ROUTE and admission row it takes; a witness
   decided upstream of the changed code is inert."
3. **Enumerate a new row's obligations by grepping a SIBLING row's id.** Rev 2's F15 list still
   missed finder_check's `PRES_ROWS`, rows_check's fixture rule for `fn` rows, emit_sweep's arm
   cells and the census pins (P10, P13). Proposed readiness clause: "list a new table row's
   obligations by `git grep` of an existing sibling row's id over tests/, memfn/tests/, scripts/ and
   tests/mech/; every file naming a sibling is an obligation."
4. **A changed generator needs its reference model moved in the same unit** (P11): a plant restoring
   the old rule then agrees with the unchanged reference and stays green.

## Rulings (kit manager, 2026-11-12)

Overall: NOT READY as a whole, as proposed. Rev 3 follows, then ONE readiness critic on D3 only. The D0-D2 fixes are text only.
- FIX-NOW: P1-P19, P22 and P23.
- DOC: P20 and P21.
- NOTED: P24.

Decisions:
- **P3:** the leaning. Where the run has no scan (`SF_RUN_NOSCAN`, known before P2), P2 treats the run span as run-less: dominance by the set pick, so `x.(?:cat|dog)` keeps `dominated`. F3's witness is restated on a proof pcrec does state.
- **P9:** the scan-less body gets ITS OWN card in the same change, visibly UNMEASURED. It is renamed for its behaviour (a "verify every candidate" body), never `walk`, under D174. Its place in the choice order is stated by fact (it must not sit below fn-pair on the scan-less predicate, as P2 found).
- **P15:** the record is an MFTRACE line, `run_part_terms`, printed where the derived part's terms are handed to ofsskip. That is a source independent of the census's own derivation. The PRE-LANDING floor comes from G2's rendered wide sites, so D3's plant can red on the kit branch. The pcrec-artifact floor is raised at the joint landing.
- **P8: JOINT with main, PENDING.** Kit leaning: retire `leads`/`rlead` as independent expectations on runs with a non-cube position, as K38-2 retired `scan`/`rwin`. The successor controls are C2 and G2's decline equality. Correcting the expectation instead would share the reply's source (K35) or make pcrec re-implement "findable" (D157).
- **P14:** the text is scoped to a window site's alternative, with the count corrected. Main is asked to scope the [RUN-POS-SET] note the same way.

Process notes, proposed to main for the critic skill:
- send contradicting critic pairs to the verifier as one item;
- the seam lens's new-STATE reader clause extends to trace shadows and emitted comments.
