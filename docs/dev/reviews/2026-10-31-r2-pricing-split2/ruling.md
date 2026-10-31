# crit-pricing-split2 / ruling: rulings check + slot tracing on (a′) + goals

Critic: ruling (opus), 2026-10-31. Subject: rev 1 of `docs/dev/lanes/splitstudy_report.md`
(lane/splitstudy c06ac74ef, snapshot `subject_splitstudy_report.md`). Review tree
`worktrees/crit-pricing-split2` @ a3cc4de82. Read-only; 4 compiles of the review tree's
`build/pcrec` (`gnutimeout 30`, outputs `p.c`/`p1.c` in this dir). Copied for reading:
`PR.md` (the kit's draft requirements, `git show lane/memfn-pricesurvey:...`). No denied file
opened. Read-tool use: none under docs/dev/lanes/ (all via git show / sed).

## Findings

### R0. Ruling-by-ruling classification of (a′) (question 1)

Operative clauses quoted in full from the review tree's `docs/dev/decisions.md` (line numbers there).
Verdict key: RULED = (a′) is the ruled shape; EXT = an extension the ruling did not authorize but does
not contradict; REV = (a′) contradicts the clause (fully or in part). "§8" = what rev 1's §8 says.

| ruling | operative clause (verbatim) | (a′) | §8 says |
|---|---|---|---|
| D146 first half (:8995) | "The kit owns every choice inside it: SIMD forms, the always-present scalar fallback, short-span loop-free paths, libc calls. pcrec does no cost comparison and carries no architecture knowledge (Q12's refinement). This supersedes integration.md rev 2's K0 price query and its cross-project cost units." | **REV** (RULING-2): the backend argmin prices pcrec's paths WITH kit quotes, which is integration.md rev 2's K0 (a kit price list read by a pcrec table) that D146 superseded by name | "ADDENDUM", "no clause reversed" |
| D146 second half (same sentence) | "carries no architecture knowledge (Q12's refinement)": integration.md:6465 reads it as ARCH-BLINDNESS (C4 detector: no ISA vocabulary in `src/`) | EXT, holds if the cards reach pcrec only through the opaque set (no box/ISA name in `src/`) | ADDENDUM: agrees |
| D146 Why / Guard | "the r2 panel showed the cross-project price layer recreates the measurement-regime, shared-source and recalibration problems at the project boundary" / "Guard: pcrec's own bench/alpha timings with the kit on vs off" | Why answered only in part (§5.1, §5.2); recalibration (every kit card move now moves pcrec's path picks) is named in §3.3 "what it costs" but not as the answer to the Why | "answered by §5.1 and §5.2" |
| D147 (:9002-9006) | "SIMD is a LAYER on top of the scalar algorithm and never a substitute for it ... The scalar layer ... must be the best it can be with SIMD OFF"; add. 6: "What sits inside SIMD-on is the kit's choice, per site" | EXT, consistent (price on SIMD-off quotes). Omission: whether the kit's WITHIN-site strategy (NONE vs scan, entry kind, stop) may move with the layer (RULING-11) | ADDENDUM |
| D152 (:9240) | "When a table is the wrong tool: ... a choice that is really a cost comparison across all options (an argmin is a planner, not first-match — D151 avoided that)" | EXT (architecture.md's later "a priced argmin is fine" already widens it) | ADDENDUM: agrees |
| D157 (:9375-9376) | "pcrec does NOT send ... a second filter position chosen by pcrec ... D146's boundary is that pcrec states FACTS and the kit chooses FORMS ... The contract carries the facts only and implies no use of them" | holds for the cards (data the kit reads, not a pcrec pick); the new site facts are facts. Two strains: §3.3/§8 PRESCRIBE the kit's formula (RULING-9) and the handoff family re-reads kit quotes against D167 add. 1 A11 (RULING-6) | "unchanged" |
| D158 (:9393) | "if the build with an optimization DENIED answers, the default build answers too. An optimization may turn a give-up into an answer (ONE_WAY). It may never turn an answer into a give-up." | EXT; the draft addendum is internally inconsistent (RULING-8) | ADDENDUM |
| D161 add. 6 (:9470-9471) | "chunk 2's 'consumer price per route as DATA' ... is withdrawn: hard to gauge, fuzzy to use, box-specific, and stale after every engine change ... the residual per-false-candidate cost is removed by verification at the chain's last link ([KIT-VERIFY]) rather than priced ... A price returns only as a new filed row if a real cell shows the kit's choice wrong for want of it." | REV in letter, as rev 1 says (the dated addendum). Note the shipped kit ALREADY breaches its letter (`C_ENTER`, `window.c:394`), which rev 1 says (§3.4) | dated addendum, "widened" |
| D161 add. 11 (:9498) | "the only pcrec-side quantity is a MEASURED per-candidate fixed cost per route (armread_report.md: 3-8 ns DFA/hybrid/VM). FILED, not built: trigger = a TUG cell measured losing for want of it" | EXT beyond it: (a′) adds a per-BYTE card per route, a derived walk, two new site facts. Not in §8 at all (RULING-3) | absent |
| D161 add. 14 (:9513) | "the kit's candidate-finder table (add. 11) decides the form, including NOT pre-scanning at all" | **REV in part** under (a′) as written: the backend's no-site path S0 competes with every kit site (RULING-4) | "AFFIRMED, no change" |
| D161 add. 15 Q-WR-9 (:9537) | "default KEEP unless the span's `need` is OPTIONAL and E is `measured`; pricing waits for add. 11's trigger (a TUG cell measured losing for want of it). If it fires, the consumer's cost enters as a per-route MEASURED constant in the D166 set, never a pcrec price model, and add. 6 gets a dated addendum." | RULED for the kit half's PRE-SCAN only; EXT (not pre-authorized) for every other kit choice; S0 breaches its letter (RULING-1, RULING-4); the "default KEEP ... E measured" clause is dropped silently (RULING-5) | "its own addendum = the add. 6 addendum above, not reversed" |
| D166 (:9724-9726) | "one box, one run, one method version, never mixed across runs ... a set stores costs in units of the scalar walk's per-byte cost"; add. 2: "when a measured form's (normalized) body changes after its set was measured, the default set is CARRIED STALE ... never a landing gate" | EXT, consistent (staleness key is add. 2's sibling) | ADDENDUM: agrees |
| D172 (:9943) | "Find-window and REPORT are the SAME request (REPORT = verify everything; the kit fast-finds a stop, then verifies). The stop choice moves to the kit as tables ... Retiring, staged at zero movers: `ctx[]` and its caps, the REPORT kind, RPT's separate check, `plan_hint`" | **REV in part**: (a′) makes `cover` vs composite (REPORT vs find-then-engine at the same spans) a BACKEND path choice (RULING-1) | "unchanged" |
| D176 Q1 (:9958) | "'which stop, found how' is ONE priced choice in the kit's Table A over (alternative x stop position x find method) ... A cost changes under an option only through a visible key column or a different row, never a hidden adjustment" | EXT (consumer rows as a key column). The draft makes "no search" TWO priced rows in two homes, against "ONE priced choice" (RULING-4); it drops Frank's own proposed text (RULING-5) | ADDENDUM |
| D176 Q3 (:9960) | "the kit measures this box (zen4) far enough to fill Q1's cost table (memchr, two-stream pair and Horspool-probe cards plus verify per hit) ... `plan_cost.def` rows migrate into the sets" | EXT: two pcrec-owned cards per route measured by an unbuilt pcrec script is not the migration Q3 ruled (`C_ENTER` is one kit row) | §3.6 S3 says it rides Q3 "already-ruled" |
| D176 Q4 (:9961) | "presence and stop stay two QUESTIONS with different prices but ONE decider, the kit's window family, from ONE statement ... One general fold: when the chosen stop's first find ... covers the presence byte, the presence pass is dropped" | holds for the kit's fold; but pcrec's `dominated` row also drops presence when LOCATE is `whole` (`emit_dfa.c:8584-8590`), a backend-path dominance rev 1 does not list (RULING-7) | "unchanged" |
| D176 Q5 (:9962) | "prices are higher-resolution fixed-point integers ... prices within the measurement-noise band tie, decided by the existing declared tie rows" | EXT (the backend's two-pass rule is a new tie rule beside `wf_ties[]`; rev 1 says so, open point 5) | — |
| D167 add. 1 A11 (:9762) | "the landmark admission stays pcrec's. Its input is restated as a FACT: the start set's prior mass, h and K, with no read-back of the kit's form or of 'what the displaced scan skips' (`emit_dfa.c` ~7920-7934 priced a kit method, contrary to D157)" | **strained** by the handoff path family (RULING-6) | absent |

### Findings

**RULING-1. LOCATE's `cover` vs composite is, under D172 and (a′)'s own clause 5, a choice INSIDE one
window site; (a′) homes it in the backend, so the first migration stage splits one kit axis across two
deciders and breaks the accounting rule.** CONFIRMED. Severity design; effort small (study text) to
medium (stage 1's re-scope); blast radius §3.3 accounting rule, clause 5, §6.1/§6.4 stage 1-3, §8 D172
and D146 rows. Rev 1 §3.2, §3.3, §6.1; new claim (rev 1's LOCATE-first, COST-1 fix, combined with the
new clause 5).
- D172 (quoted above): "Find-window and REPORT are the SAME request (REPORT = verify everything)", and
  "the REPORT kind" is on its retirement list. In code the two are already one family: `cover` states a
  WINDOW site (`known.c:470`, `pcrec_memfn_walt_spans(cx, a, MF_ENTRY_NONE, n)`, then
  `pcrec_memfn_window_stated`, `:481`) with `site_kind = MF_SK_REPORT` (`known.c:496`) and every span
  `MF_VERIFY_YES`; the composite's PF site states PARKED/RESEED alternatives
  (`emit_dfa.c:6809`, `:6816`). The entry-kind enum is one axis: `mf_entry { UNSTATED, NONE, PARKED,
  RESEED }` (`memfn/include/memfn.h:541-542`).
- (a′) clause 5: the kit decides "entry kind, stop, method, verify depth ... scan or not" inside a site.
  REPORT is the verify-depth axis's end ("verify everything") with the NONE entry kind. Yet §3.2/§6.1
  put `cover` vs composite in the BACKEND's path argmin. Either the backend decides "verify everything"
  and the kit decides every lesser depth (two deciders on one axis of one D172 request), or the kit
  decides it, and then:
- the accounting rule (§3.3: "The backend adds only terms invariant to the kit's choice at that site:
  the match phase, RECOVER and FINISH per match") FAILS at exactly this slot: `cover` runs NO match
  phase (rev 1 §2.4, SIM-4), so the match phase varies with the kit's choice. The kit would need a
  per-match (match-phase) card, and §3.3's "These two cards per route are ALL the consumer data the kit
  reads" is false.
- The §8 D146 draft says "pcrec compares no two kit forms"; `cover` vs composite compares the kit's
  REPORT-site quote with its window-site quote: stage 1 violates the draft it ships under.
- Consequence: with `cover` moved into the kit, the backend's LOCATE priced block is empty (`empty` is
  D, `rev-end` the UNMEASURED prefix, §6.5), so "LOCATE first" is in fact KIT-first: the first priced
  choice is Table A gaining a REPORT alternative priced with consumer + match-phase cards, which is
  also Frank's 2026-10-31 direction given to the kit (`lane/memfn-wake1030:memfn/docs/responses.md`
  tail: "'No search' becomes a priced row ... so the admission verdicts fold into the one priced
  choice"). Proposed fix: home `cover` in the kit (pcrec states C3-C12 as a site fact "the consumer
  may be skipped"; C13/C14 stay kit capability facts), add the match-phase card to the consumer data,
  and re-state stage 1 accordingly; §8 D172 becomes "affirmed (REPORT = an alternative of the one
  site)".
- CHANGES the seam rule (clause 5's accounting sentence) and the migration's first stage; does NOT by
  itself change (a′) over (d) ((d) has the same split, worse).

**RULING-2. "No clause reversed" (§3.3, §3.6 S2, §7 row 11, §8) is false: both options reverse D146's
supersession of the K0 price query, and (a′) also reverses the 2026-10-31 split (PR R2.3).** CONFIRMED
(quotes). Severity design (ruling framing); effort small; blast radius §3.6 S2 cell, §7 row 11, §8 D146
row, open point 16. Rev 1 §3.6 S2, §8; introduced by the SLOT-17 fix (D146 "addendum ... new direction").
- D146's decision text ends "This supersedes integration.md rev 2's K0 price query and its
  cross-project cost units", and its title is "DELEGATION, not a price market". integration.md:5201
  describes K0: "pcrec ... asks an arch-neutral query, and gets a price list back ... pcrec's tables get
  ONE arch-blind row, `kit`, chosen iff a kit quote DOMINATES the next row's price". (a′)'s backend
  "pricing each path with the kit's per-site quotes" is that mechanism generalized. A new owner
  direction may well justify it, but it is a REVERSAL of D146's operative supersession, not an
  addendum; Frank should be asked to reverse it knowingly, with D146's Why (regime, shared-source,
  RECALIBRATION) answered item by item. §5.1/§5.2 answer regime and shared-source; recalibration (a kit
  card move now moves pcrec's path picks, so every kit set revision needs pcrec's mover census) is in
  §3.3 "what it costs" but not offered as the answer.
- PR §2 R2.3 is headed "THE SPLIT (ruled 2026-10-31)" and says the KIT "never receives engine costs
  (D161 add. 6, D157 stand)" and the backend "owns the per-route consumer costs ... and runs the ONE
  argmin across strategy rows" (`PR.md:74-85`); the HOLD note (`PR.md:55-61`) holds it pending this
  study. (a′) reverses its kit half; (d) keeps it. Rev 1 files the contradiction under open point 16 as
  a PR defect to relay ("R2.3's 'never receives engine costs' contradicts (a′)"), which misfiles an
  owner-ruled (held) item as the kit's drafting error.
- Re-count for S2: (a′) reverses D146 (operative supersession), the 2026-10-31 split's kit half (held),
  D172 in part (RULING-1), D161 add. 14 in part (RULING-4); (d) reverses D146, Q-WR-9, D176 Q1, Q4,
  D172, add. 14 (+ D157 arguable). (a′) still reverses fewer, so the S2 verdict survives; the "no
  clause reversed" sentence and the "4 extensions/addenda, 0 reversals" cell do not. Does NOT change the
  recommendation.

**RULING-3. "(a′), the ruled shape" and "the add. 6 addendum Q-WR-9 pre-authorized, widened"
overstate what the rulings authorize; D161 add. 11 is cited as support but has no §8 row.** CONFIRMED
(quotes). Severity design; effort small; blast radius Summary 3, §3.1, §3.3, §3.6 S2, §8. Rev 1 §3.1,
§3.3, §8; introduced by the SLOT-1 fix.
- Q-WR-9's authorization is conditional and scoped: "pricing waits for add. 11's trigger ... If it
  fires, the consumer's cost enters as a per-route MEASURED constant". Its title is "pricing the
  pre-scan". The trigger that fired (r17b_prime.md:273, M23 `kit.gate.byte1.DFA_SCAN.*`, :2011) is a
  PRE-SCAN cell. Nothing fired for entry kind, stop, verify depth or scan-or-not; SIM-1/SIM-3's movers
  are MODELLED (rev 1 §3.4, §3.5). So the widening is an EXTENSION under D77 with no measured trigger,
  not a pre-authorization. (Mitigation rev 1 can cite: `C_ENTER` is already a consumer cost inside
  Table A, so the widening regularizes shipped state rather than adding a new read.)
- D161 add. 11's ruled shape is narrower than (a′): "the only pcrec-side quantity is a MEASURED
  per-candidate fixed cost per route ... FILED, not built". (a′) adds a per-BYTE consumer card (which is
  what prices the NONE row), a derived walk, `beyond(site)` and "expected bytes seen". add. 11 is the
  ruling (a′) extends most and §8 has no row for it.
- "ruled shape" is true of the KIT half only; the BACKEND half's ruling basis is the 2026-10-31 split
  (RULING-2), which (a′) contradicts on the kit half. (a′) is a hybrid of two rulings, each partly
  reversed; the study should say so. Does NOT change the recommendation.

**RULING-4. "No search" has two homes under (a′) (the kit's NONE row and the backend's no-site path
S0); the backend's S0 reverses D161 add. 14 in part and breaches Q-WR-9's letter; and S0 as tabulated
drops the presence site today's no-search artifacts carry.** CONFIRMED (code + probe). Severity design
(one table per slot; an S0 without presence on a REQUIRED span would be a D158 hazard, caught only by
clause 8); effort small; blast radius §3.3, §3.6 S1/S2, Q4 table rows S0/PRESENCE, §8 add. 14 and D176
Q1 rows. Rev 1 §3.3 ("the kit's NONE row at a site plus the backend's no-site path"), §8 D176 Q1; new
claim (from the PREMISE-6 fix plus Frank's "no search is a priced row").
- Two homes for one artifact: a kit site whose pick is NONE (no pre-scan, the consumer walks every byte)
  and a path with no site (S0: "consumer per byte x all bytes", Q4 table) render the same engine loop
  and are priced from the same per-byte card in two places. Under the two-pass tie rule they tie
  exactly; which home "decides" is then a table-order accident.
- D161 add. 14: "the kit ... decides the form, including NOT pre-scanning at all". If S0 can beat a
  path with a kit site, the BACKEND decides "do not scan" across paths: the very partial reversal §8
  charges to (d) ("scan-or-not across footprints becomes the backend's"). §8 marks add. 14 "AFFIRMED"
  for (a′).
- Q-WR-9: "never a pcrec price model" for the pre-scan. Probe: `$B -p rx -o p1.c --pattern '(?s).+x\d'`
  stamps `RX_DFA_PREFILTER "none"` (NEXT = `next-none`, i.e. today's no-search) AND `RX_REQ_BYTE "120"`,
  `RX_REQ_WHY "emitted"`; the emitted body has `!memchr(subject + search_from, 120, ...)` (`p1.c:82`),
  the kit's presence site (`RX_MEMFN_LIBC "memchr"`). So today's no-search path carries a kit PRE
  site. The Q4 table's S0 row says the kit hands back "—" and PRESENCE is only "in S2's pick". Either
  S0 keeps a kit site (then S0 = a site with a NONE stop: the duplicate above), or the backend, choosing
  S0 over a path with a presence site, prices the pre-scan's value itself (Q-WR-9's letter). On the VM
  attempt route presence is REQUIRED (`emit_dfa.c:1476`: `MF_REQUIRED` for `MF_SK_VM_ATTEMPT`) and an
  S0 that drops it would turn answers into give-ups (D158; P0 is undeniable for that reason).
- Proposed fix (the unification, see RULING-12): ONE no-search row, the kit's (F0 `NONE` in
  r17b_prime.md:270, NOT BUILT; its measurement M22 found `kit.gnone` = -1 (never) on three consumer kinds, so a priced no-search competitor has no measured win on record either); S0 survives only as the VALIDITY fallback where no site can be
  stated (`next-none`'s fb role, e.g. k0 = 256 members), never as a priced competitor of a valid site.
  Changes the seam rule (clause 5's "scan or not" vs §3.3's "plus the backend's no-site path"); not the
  (a′) over (d) ranking.

**RULING-5. Every §8 draft for (a′) omits something its ruling's operative clause carries.** CONFIRMED
(quotes). Severity doc/design; effort small; blast radius §8. Rev 1 §8; introduced by the SLOT-1/2/16/
17/19 fixes (the addenda table).
- Q-WR-9 row: drops "default KEEP unless the span's `need` is OPTIONAL and E is `measured`". The widened
  add. 6 text lets the kit price presence (and everything else) from consumer cards on EVERY compile;
  whether the E-measured precondition survives for presence (Q-R17P-28's reason for not building P1 was
  "it never fires on a default compile") is unstated.
- D176 Q1 row: Frank's own proposed text (kit notice 2026-10-31: "pricing chooses the strategy, not only
  the tactic; strategies are declared rows each finding its own best option; the cheapest row wins,
  ties to the simpler; no tuning constants — every coefficient is measured or derived; the model is
  graded by regret on held-out sites") is not reproduced; the draft keeps only "no search is a priced
  row", and splits that into two homes (RULING-4), against Q1's "ONE priced choice".
- D146 rows: the K0 supersession (RULING-2) and the Guard's continued independence are not addressed.
- D161 add. 6 row: "for every choice ... that trades against consumer work (entry kind, stop, verify
  depth, presence, scan or not)" omits `cover`/REPORT (RULING-1) and the match-phase term.
- D158 row: see RULING-8. D147 row: see RULING-11.
- Missing rows: D161 add. 11 (RULING-3), D162 (RULING-10), D167 add. 1 A11 / Q-R17P-11 (RULING-6), and the
  2026-10-31 split itself (RULING-2).

**RULING-6. The handoff path family prices the landmark site's kit quote against the displaced start
scan's quote, which D167 add. 1 A11 forbids for the landmark admission; §8 omits A11.** SUSPECTED (the
ruling text and the (a′) formula are clear; whether "a quote" counts as A11's "read-back of the kit's
form" is a reading Frank or the manager owns). Severity design; effort small; blast radius §1.4 item 3,
Q4 row S5, §6.4 "filed: handoff family", §8. Rev 1 §1.4 item 3 ("Home: P"), Q4 S5 row; new claim.
- A11: "Its input is restated as a FACT: the start set's prior mass, h and K, with no read-back of the
  kit's form or of 'what the displaced scan skips' (`emit_dfa.c` ~7920-7934 priced a kit method,
  contrary to D157)". (a′)'s S5 price is "the landmark site's quote (as S2)" plus "the fraction of bytes
  the engine skips x consumer per byte", compared against the S2 path's kit quote: the displaced scan's
  price, read back. If that is acceptable under the new direction, A11 needs its own dated addendum
  (and its "recorded as a D157 exception" status resolved). To confirm: the manager's reading of A11
  ("form" vs "price of the form").

**RULING-7. "PRESENCE has one home (kit, P1)" (§3.6 S1) omits pcrec's own LOCATE-whole presence
dominator, which under (a′) becomes a fold decided by the backend's LOCATE pick.** CONFIRMED (code).
Severity design (S1 cell; D176 Q4's "ONE decider"); effort small; blast radius §1.4 item 1, §3.6 S1,
§8 D176 Q4. Rev 1 §1.4 item 1 ("Home: K"), §3.6; introduced by the SLOT-3 fix.
- `req_dominated_applies` (`emit_dfa.c:8576-8590`): "the BODY's LOCATE row answers presence itself
  (`u.locate.whole`: the `rev-end` walk, the empty engine), so the pre-check has nothing left to
  dismiss", read through `CAND_READ(CAND_SLOT_PRESENCE, CAND_SLOT_LOCATE, ...)`. Under (a′) LOCATE is
  the backend's slot, so on `rev-end`/`empty` paths the presence pass is dropped by the backend's path
  choice, outside the kit's P0-P9. It is a number-free dominance and clause 2 allows it to live with the
  side owning its facts, so this is not a defect, but the S1 cell's "one home" and §8's "D176 Q4
  unchanged" are false as stated: name the second home (a path-level presence dominance) and either
  state "LOCATE answers presence" to the kit as a site fact or record it as a clause-2 exception to Q4.

**RULING-8. The D158 draft (§8, clause 8, §5.5) states three non-equivalent rules, and "the slot's
least" give-up surface is undefined.** CONFIRMED (text). Severity design (a contract-bearing clause);
effort small; blast radius clause 8, §5.5, §8 D158 row, §7 row 13. Rev 1 §5.5, clause 8; introduced by
the SLOT-15 fix.
- §5.5: "a priced slot's valid set contains only paths whose give-up surface is no larger than the
  slot's least (equivalently: the set may move a pick only in the ONE_WAY direction ...)"; §8 and
  clause 8: "a set revision never moves the give-up surface". (i) "no larger than the least" =
  equal to the minimum, so no move at all; (ii) "ONE_WAY only" permits a give-up to become an answer,
  which D158 explicitly allows ("An optimization may turn a give-up into an answer (ONE_WAY)") and (iii)
  "never moves" forbids. They are not equivalent. (iv) Give-up surfaces are SETS of (pattern, subject,
  budget) and are only partially ordered; two valid paths with incomparable surfaces leave no "least",
  and the filter is undefined there. D158 itself is relative to the DENIED build, not to a least
  element. Proposed text: "the argmin's valid set contains only paths whose give-up surface is a subset
  of every DENY-reachable path's surface (D158's own comparison), so a set revision can move a pick only
  between paths with equal surfaces or ONE_WAY"; "per path = union over its rows' `CG_FIXED`" (as §5.5)
  then needs a proof that the union is the surface.

**RULING-9. §3.3 and the §8 add. 6 draft prescribe the kit's cost method in a ruling text; D157 and
architecture.md forbid describing how the kit uses a fact.** CONFIRMED (text). Severity doc/design;
effort small; blast radius §3.3, §8 add. 6 row. Rev 1 §3.3; introduced by the SIM-1/COST-10 fix.
- §3.3: "`A(plan) = per_entry(route) + (rewalk(plan) + beyond(site)) x per_byte(route)`, computed by the
  side that owns the plan" and "These two cards per route are ALL the consumer data the kit reads"; §8:
  "the per-entry walk is derived, never assumed". architecture.md "Across the kit boundary": "In fields,
  comments, briefs and messages never describe how the kit would use a fact." A study may model the
  kit's arithmetic to argue exactness, but the ruling text Frank signs should state the FACTS crossing
  (cards, site facts, their error bounds) and the "no ASSUMED factor" property (Frank's own "every
  coefficient is measured or derived"), not the formula.
- Substantive gap in the same place: `rewalk(plan)` is not derivable from the kit's plan and spans
  alone; it depends on whether the consumer RE-STEPS positions the kit verified. D147 add. 15 (:9409)
  records that on the DFA route "the DFA re-stepping the run from state 0", and "handing the DFA the
  post-run state (a pcrec-side change)" as out of scope. That is a consumer (engine) fact, per site
  kind, missing from §3.3's list and the Q4 S2 row. SUSPECTED as to materiality; CONFIRMED as a missing
  fact in the composition argument.

**RULING-10. Two of (a′)'s new site facts (`beyond(site)`, "expected bytes seen") fill D162's RESERVED
per-site slot without the measured case D162 requires; D162 has no §8 row.** CONFIRMED (quote).
Severity design (D77/D162); effort small; blast radius §2.5, §3.3, Q4 S2 row, §7 row 3, §8. Rev 1 §2.5,
§3.3; introduced by the SIM-5 and SIM-1 fixes.
- D162 ruling 1: "Distributions only: the kit derives per-site answers (a set's rate, a ranking). A
  per-site slot is RESERVED, filled only when a measured case needs a fact the kit cannot derive (match
  density the likely first)." Rev 1 marks both facts' materiality INFERENCE (§2.5: "INFERENCE that
  per-call differences matter on today's forms"; §3.3: "whether `beyond(site)` is material on today's
  sites is unmeasured"), i.e. no measured case. Either they wait for one (a trigger per fact) or the
  study asks for a D162 addendum.

**RULING-11. The D147 draft does not say whether the kit's within-site STRATEGY (NONE vs scan, entry
kind, stop) may move with the SIMD layer.** SUSPECTED. Severity design; effort small; blast radius §5.8,
§8 D147 row. Rev 1 §5.8; introduced by the SLOT-16 fix.
- The draft: "the backend's path argmin prices with SIMD-OFF quotes; SIMD re-forms only within the
  chosen site". Under (a′), "no search" and the entry kind ARE kit-site choices; with Frank's 2026-10-31
  direction, "no search" is a STRATEGY. If SIMD-on lets the kit pick a scan where SIMD-off picked NONE,
  the strategy moves with the layer inside the site, which is exactly the D147 tension §5.8 resolves
  for the backend only. "Re-forms" needs a definition (form only, or also stop/entry/NONE).

**RULING-12 (forest for the trees). The entry-kind / no-search alternatives are a family of four split
across three deciders; the consumer-cost data is a family of five homes; propose one alternative axis
and one consumer-data home.** CONFIRMED (code + set + rulings). Severity design; effort: design text now,
build with the D176 build; blast radius §3.3, §6.4, §8. New claim (the standing question).
- Alternatives of one window site today and under (a′): REPORT (`MF_ENTRY_NONE`, `known.c:470`; decided
  by pcrec's LOCATE first-match, a backend argmin under (a′)); PARKED and RESEED (stated by pcrec,
  `emit_dfa.c:6809/6816`, chosen by the kit's MARGIN, `window.c:669-683`); "no pre-scan" (the kit's F0
  NONE, NOT BUILT, r17b_prime.md:270, plus the backend's S0 under (a′)). Four members, three deciders.
  Unification: ONE alternative axis in the kit's choice over alternatives (`wfM`), each alternative
  stated by pcrec with its SOUNDNESS facts (C3-C12 for "consumer may be skipped", G-parked/G-reseed,
  "consumer walks every byte" always sound), priced by the kit with the consumer cards; MARGIN's
  ARGUED bar is then one row of that table, measured as rev 1 already proposes. Deleted special cases
  (the benefit): the LOCATE `cover` row's ordering rule (PS C6), S0 as a priced path, `pcrec_cover_site`'s
  separate site kind (already on D172's retirement list). Trigger: the D176 build (it already rewrites
  Table A) and D172's REPORT-kind retirement step.
- Consumer-cost data: `C_ENTER` (kit, MEASURED x ASSUMED, `plan_cost.def:38-41`); M23
  `kit.gate.byte1.DFA_SCAN.*` (kit-measured, route-keyed, r17b_prime.md:2011, the realization Q-WR-9's
  fired trigger actually produced); add. 11's per-candidate fixed cost (armread, filed); the kit's own
  cards already keyed by consumer KIND (`kit.beta.WALK.DFA_SCAN.*`, `kit.gstar.*.DFA_HAT` in
  `measure_store/zen4-grid1/1/set.tsv`); (a′)'s new pcrec-owned cards with `deps pcrec:form.<consumer>`.
  Five homes for one physical quantity. Unification: one set section of consumer cards keyed by
  `mf_site_kind`, ONE owner, D166 add. 2's staleness rule; `C_ENTER` and M23 become derived readers of it.
- Key mismatch inside this: (a′) keys the cards "per route" (CandRoute: DFA, VM, ATTEMPT), but the
  consumer kinds are six (`mf_site_kind`, `memfn.h:414-415`: DFA_SCAN, DFA_HAT, HYB_PF, VM_ATTEMPT,
  DFA_ATTEMPT, REPORT) and the set's existing kit cards are keyed by them. DFA_SCAN and DFA_HAT share a
  route and differ as consumers; HYB_PF is a route PAIR. Mapping six kinds onto three routes is the
  narrowing architecture.md "One table per slot" names ("mapping it onto a smaller enum ... drops rows
  silently"). Changes §3.3's "two cards per route" to "per consumer kind".

**RULING-13. §3.6 scoring: four cells for (a′) are not derivable from §G's checkable forms, and two rest
on claims the study marks INFERENCE or that this round refutes.** CONFIRMED (cell by cell below).
Severity doc (the verdict column overstates evidence); effort small; blast radius §3.6, Summary 3,
RECOMMENDATION's "beats (d) on every goal above S4". Rev 1 §3.6; introduced by the SLOT-20 fix.

| goal | §G checkable form | (a′) cell | derivable? |
|---|---|---|---|
| G1 | regret on a held-out population | "exact composition given the kit's data" | NO: no regret exists for either option; the composition argument's condition rests on `beyond(site)` (INFERENCE, §3.3) and per-call terms (INFERENCE, §2.5), and fails at LOCATE (RULING-1). (d)'s cell uses MODELLED numbers. Honest cell: "argued, unscored" |
| G2 | every mispick reads off one trace | tie | judgement; acceptable as "tie (argued)" |
| G3 | zero ARGUED/UNMEASURED-DEFAULT numbers on a priced slot | tie | form gives FAIL for both: MARGIN 2/1 stays an ARGUED number inside Table A's priced choice under (a′) (§3.5, `window.c:710`). "tie" hides two FAILs |
| S1 | every choice has exactly one home | (a′) | NO as stated: no-search (RULING-4), REPORT vs verify depth (RULING-1), presence fold (RULING-7), the tie rule (`wf_ties[]` + the backend two-pass, §5.4), the stop until crossings 7/8 retire, `pred-memchr` unhomed (RULING-14). (a′) still has fewer than (d) |
| S2 | count of reversals | "no clause reversed" | NO: see RULING-2 (verdict survives on the corrected count) |
| G4 | homes a new strategy/method touches; PR's bar "its row, its card, its tests" | (a′) | relative verdict OK, but the form says FAIL for both: a new pcrec strategy touches a path-family row, a rendering row, a card and a `cand_rows[]` validity row |
| G5 | <= 1 % compile-time census | (a′) | NO: unmeasured for both; the shadow's extra kit asks (§6.2 hazard 3) are a cost (a′) also pays |
| S3 | lane-sized items before the first priced slot | "no reply-shape event" | partly: the count (2 lane-sized + the D176 build vs 3) is derivable from §7, but "no reply-shape event" is false: `mf_wreply` (`memfn/include/memfn.h:1420-1435`) has no price components, set id or ranking, all of which §3.3's reply carries (§7 row 5 itself says "small-medium") |
| S4 | second backend reuses validity | (d) slightly | fine |

  Result: the RECOMMENDATION's "beats (d) on every goal above S4" is supported as a judgement on S1, S2,
  G4 and S3 (relative), not as a reading of §G's forms; G1, G5 are unscored. Does not by itself reverse
  (a′) over (d); it changes how the case should be put to Frank.

**RULING-14. `pred-memchr` (a P row) has no home under (a′).** CONFIRMED (text). Severity design (one
table per slot); effort small; blast radius §1.2, §1.4. Rev 1 §1.2 (row marked P ‡); introduced by the
PREMISE-5 fix (reclassified V -> P without a home).
- §1.2 reclassifies `pred-memchr` (`emit_dfa.c:10421`, `.routes = CR_ATTEMPT`) as P ("a predecessor
  `memchr` on a common byte can cost more than it skips", would-be inputs Kq + B), but neither §1.4's
  homes (K/P), the Q4 table nor §6.4 names its decider. It is a single-byte scan-or-not at the attempt
  site, i.e. D161 add. 14's purview: Home K, stated by pcrec as a site.

**RULING-15. §G breaks architecture.md's goals rule: nine goals (rule: three to five), no NON-GOALS, no
"who benefits"; S4 (portability) is PR's explicit non-goal; S2 is a process metric.** CONFIRMED (text).
Severity doc/design; effort small; blast radius §G, §3.6. Rev 1 §G; introduced by the SLOT-20 fix.
- architecture.md: "three to five goals, each naming who benefits and a measurable form ...; a PRIORITY
  ORDER ...; and NON-GOALS". §G has 9 rows, no who-benefits column (PR §0 has one, §G dropped it), no
  non-goals. PR §0's non-goals include "choosing the engine (DFA vs VM) — the engine is an INPUT fact
  here" and "a second backend"; §G's S4 scores a second backend, and (a′)'s backend argmin lists "later
  the route pair" as a slot it will own. S2 ("count of standing rulings the option REVERSES") benefits
  no user and biases toward the status quo; Frank can re-rule; it belongs in the ruling section, not
  the goals. S1 is a design rule (architecture.md "One table per slot"), better stated as a
  constraint every option must meet than a ranked goal.
- Ranking soundness: keeping PR's G1>G2>G3>G4>G5 and inserting S1/S2 between G3 and G4 is coherent;
  the goals, minus S2/S4, match PR §0. The ranking is sound once trimmed to PR's five plus S1 as a
  constraint, with PR's non-goals carried.

## PROBED-AND-HELD

- Q-WR-9 as a "pcrec price model": the backend argmin does NOT breach Q-WR-9's LETTER for the kit
  half (the pre-scan stays the kit's; the consumer cost enters as set data the kit reads, which is the
  clause's direction). It breaches D146 instead (RULING-2), and its letter only through S0 (RULING-4).
- D146 second half (arch-blindness): pcrec-owned consumer cards read through the opaque set id do not
  put ISA vocabulary in `src/` (integration.md:6465's sense); held, conditional on card names staying
  arch-free. The kit reading pcrec's cards is not pcrec carrying architecture knowledge.
- D157 for the cards: data, not a pcrec pick; held. "Entry kinds the consumer accepts" is today's
  alternatives statement (`pf_window_of`, `emit_dfa.c:6780-6830`, RESEED stated only where prefix_k's
  gate holds and `-fno-offset-skip` is absent: validity, not price); held.
- Entry kind today: pcrec offers PARKED always and RESEED by a validity gate (`count < 256`, walk
  stated); the kit's MARGIN chooses (`window.c:669-683`); `wf_check` admits only {PARKED, RESEED} pairs
  (`window.c:332`). One decider for PARKED vs RESEED; held.
- PRESENCE in the default build: pcrec's `dominated` row reads the kit's P2 `proven_by`
  (`emit_dfa.c:8597-8610`); pcrec's own density spelling is `#ifdef PCREC_CAND_TRACE` only
  (`:8541-8555`). One decider for the kit's fold; held (apart from RULING-7).
- MARGIN: one home (kit, `wf_mrows[]`, basis ARGUED at `window.c:710`); rev 1's "separate decision"
  held.
- Verify depth: one home (kit C-model, `window.c:394` with `C_ENTER`), apart from REPORT (RULING-1).
- Size ladder: one home (driver, `fit_rungs[]`), clause 7's re-run rule is coherent; held.
- Route pair: stays in `src/opt` (+ driver late validity) under rev 1; the six-member route family and
  "one route table, built when first priced" is a correct forest-for-trees call; held.
- RETRY: home P under [START-DENSE]; `cand_rs_dense_applies` (`emit_dfa.c:10086-10087`) is the R4 X
  as stated; held.
- D166 staleness key as add. 2's sibling, D152 priced-slot addendum, D147 SIMD-off pricing: consistent
  extensions; held.
- D161 add. 6's letter is already breached by shipped `C_ENTER` (`plan_cost.def:38-41`, "MEASURED x
  ASSUMED"); rev 1's §3.4 statement held.
- `mf_wreply` cite (`memfn.h:1435`) matches (at `memfn/include/memfn.h`).
- Counts: 17 rulings classified (14 named in the brief + D146 Why/Guard, D167 add. 1 A11, D162); 15
  slots traced (entry kind, stop, method, verify depth, presence on/off, presence fold, scan-or-NONE,
  MARGIN, LOCATE rev-end/cover/composite, handoff, RETRY, route pair, size ladder, tie rule, consumer
  cards + staleness key); 9 §3.6 cells audited; 4 compiles (`(?s).+x\d` x2, `(?s).xyz`, `[^\n]+xyz`;
  `\Cxyz` refused, requires module 'misc'); about 30 file:line cites checked, none off in a way that
  changes an argument.

## STATE AT HANDOFF

- STATE: complete
- OWED: none
- Findings RULING-1..15 (RULING-6, RULING-11 SUSPECTED; the rest CONFIRMED). Changes the SEAM RULE /
  slot table: RULING-1 (`cover` into the kit, accounting rule), RULING-4 (one no-search home),
  RULING-12 (card key per consumer kind). None reverses (a′) over (d); RULING-2, -3, -13 change how the
  case is put to Frank (reversal of D146's K0 supersession and of the 2026-10-31 split's kit half).
