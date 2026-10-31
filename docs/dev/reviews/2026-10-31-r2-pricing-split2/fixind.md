# fixind (fix-induced lens), critic round pricing-split2, 2026-10-31

Subject: rev 1 of `docs/dev/lanes/splitstudy_report.md` (lane/splitstudy c06ac74ef), read from the
snapshot. Review tree: `worktrees/crit-pricing-split2` at a3cc4de82 (R below). Compiler B =
R/build/pcrec. Lane note read via `git show lane/splitstudy:docs/dev/lanes/splitstudy2_report.md`.
No denied file opened. My scripts and outputs are in this dir (`beyond.py`, `beyond_out.txt`,
`probe/`).

Question: for each claimed fix (CHANGES table), does it hold, and what did it add (reads,
hand-offs, rows, site facts, clauses, checks)?

None of the findings below changes the recommendation of (a′) over (d). Findings 1-5 change the
seam rule (clauses 5, 7, 8) and §3.3/§3.6's "exact composition" claim, and two of them (4, 5) are
exactly the claims rev 1's own STATE AT HANDOFF asked to be tested hardest.

## Findings

### FIXIND-1 — clause 8's give-up filter cannot be computed from `CG_FIXED`; the column it needs is the one the tree deliberately does not declare
- **CONFIRMED** (code + design record). Severity: design. Effort: small to restate, medium to
  build any compile-time form. Blast radius: clause 8, §5.5, §7 row 13, the D158 addendum draft
  (§8). Introduced by the **SLOT-15** fix. Changes the seam rule (clause 8), not (a′) vs (d).
- rev 1 §5.5: "`CG_FIXED` is declared per row (`emit_dfa.c:9823-9830`); the filter needs it per
  path (the union over the path's rows)", and keeps paths "whose give-up surface is no larger than
  the slot's least".
- `CG_FIXED` is a CONTRACT, not a surface. R/src/gen/emit_dfa.c:9823-9832: "unset, a wildcard, or
  FIXED — the row must never move the VM's give-up surface ... Its control is behavioural
  ([GIVEUP-DIFF], the window-identity twin), never a comparison of two columns." Six rows carry it:
  FIRST `handoff`, `handoff-attempts`, `handoff-attempts-entry` (:10285, :10294, :10300) and RETRY
  `exact`, `clamped`, `retry-anchored` (:10451, :10459, :10467). No LOCATE row has one.
- The thing that ORDERS surfaces is the give-up CLASSIFICATION (NEUTRAL < ONE_WAY), and the tree
  rules it is never declared. emit_dfa.c:5677-5681: "The give-up CLASSIFICATION (neutral / one-way)
  is derived by an instrument over the corpus, never declared here: the declared column it replaces
  had no reader, and its zero value is how F-1 read W1 as neutral." `docs/design/locate_finish.md`
  §1.5: the classification is "computed by an INSTRUMENT over the corpus ... not by the compiler,
  and nothing in `src/` declares it"; reason (a): it is "not a function of the pair" (W1 is NEUTRAL
  on an exact hybrid and ONE_WAY on a VM-only artifact); reason (c): "the handoff's `CG_FIXED` is a
  RULED CONTRACT that a derivation would erase".
- So a per-path union of `CG_FIXED` yields one bit, "this path contains a must-not-move row". It
  orders nothing, and "no larger than the slot's least" has no input. Both ways to supply one
  conflict with a record. (i) Re-declare a classification column per row: that reverses
  locate_finish r2 G7 / LR-S11 (the F-1 correction), and §8 lists no such addendum. (ii) Use the
  corpus instrument: a compiler argmin cannot read it at compile time.
- Also: ONE_WAY and NEUTRAL are defined RELATIVE TO A ROW'S OWN DENY ARM ("a row that removes an
  attempt the deny arm would run"). They do not order two arbitrary siblings. RETRY's
  `adaptive-dense` and `adaptive` are both ONE_WAY against the landing row `fixed` (locate_finish
  §1.5's classification list), and nothing relates the two to each other. Give-up surfaces are sets
  of (subject, budget), so they are partially ordered and "the slot's least" need not exist.
- What would fix it: state clause 8 as a pairwise relation that must be SUPPLIED per (path, path)
  pair, say by whom, and say what the filter does when two valid paths are incomparable (refuse to
  price the slot? first-match?). Or restrict pricing to blocks whose members are all NEUTRAL on the
  covered classes (the instrument's output read at design time, recorded on the path family).

### FIXIND-2 — clause 8 never fires at stage 3, and on the VM routes it forces the picks that the fixes say are priced
- **CONFIRMED** (code + allowance manifest). Severity: design. Effort: small (restate the gates).
  Blast radius: §6.4 stage 3's gate, §1.2's P labels for FIRST and RETRY, the Q4 RETRY row.
  Introduced by the **SLOT-15** fix together with the **PREMISE-5** reclassification. Supporting
  claims only.
- Stage 3's gate lists "clause 8's give-up filter in the census". LOCATE's priced block (`cover`,
  `composite`) has two members only on CR_DFA: `cover` is `.routes = CR_DFA`
  (R/src/gen/emit_dfa.c:10208-10209), and the `rev-end` prefix is CR_DFA too. On DFA finisher routes
  "no VM runs, so posture is N/A" (locate_finish §1.5 (e)). So the gate checks nothing at the first
  priced slot. That is a check that cannot fire.
- Where clause 8 does bite, it decides the pick instead of the price. The allowance manifest
  (R/tests/axes/run_axes.sh, GIVEUP1_ALLOWANCE) carries 8 `-fno-req-handoff` keys (GROUP F4,
  :1019-1043: "the VM attempt loop's rows skip attempts ... a deny-arm GIVE-UP may become the
  handoff's answer") and 26 `-fno-start-set` keys (GROUP F5: the VM hat, `first-class`). On those
  routes the row is ONE_WAY against its successor, so the successor has the larger surface, and
  clause 8 removes it whenever the row is valid:
  - FIRST on the VM attempt route: `handoff-attempts*` (‡ P in §1.2 after PREMISE-5) vs
    `scan-from-startpos`. This is forced, not priced.
  - RETRY: `adaptive*` (ONE_WAY) vs `fixed` (NEUTRAL). `fixed` is filtered wherever `adaptive`
    applies. In fact `adaptive` is `cand_always` (:10482), so `fixed` is reachable only under
    `-fno-hyb-reseed`, and its own desc says "always (fallback, the deny's landing row)" (:10492).
    Q4's RETRY term "adaptive vs fixed (B + R)" has no second candidate.
- No shipped pick moves (the filter keeps today's first-match pick on these slots). The point is
  that §1.2's P labels and Q4's RETRY row promise price choices that clause 8 removes. rev 1 should
  say which P rows are price choices only on routes where the posture is NEUTRAL or N/A.

### FIXIND-3 — under (a′) the kit makes set-driven choices that cross the give-up surface, and the kit holds no give-up fact for a window site
- **CONFIRMED** (code + rulings). Severity: design. Effort: small (one site fact plus the
  addendum's scope). Blast radius: clause 5, clause 8, Q4's vocabulary, §8's D158 row.
  Introduced by the **SLOT-1 / PREMISE-6** fixes (the kit decides "whether to scan at all") and the
  **SLOT-11** crossing 9 ("Home: K" for `first-class` VM). Changes the seam rule (clauses 5/8);
  (a′) still stands.
- Crossing 9 gives the kit the scan-or-not decision at the VM seek site (`first-class` VM). That
  row is ONE_WAY (locate_finish §1.5: "NEXT `first-class` ONE_WAY"; 26 GIVEUP1 keys). Under (a′)
  the kit prices its NONE row with the VM's per-byte consumer card, so a new consumer-card revision
  can turn an answer into a give-up through a KIT pick. Clause 8 covers only "a priced slot's valid
  set", which is the backend's.
- The kit has nothing to obey the rule with. A window site states no `need`:
  R/memfn/include/memfn.h:531-536 says "A WINDOW SITE STATES NOTHING ELSE ... Its `pred` carries no
  term (`nterm` 0), no `need`". rev 1's Q4 adds a give-up-bearing fact only for presence
  (REQUIRED/OPTIONAL, §1.4 item 1(b)). The missing sibling is a per-site "give-up-bearing" fact.
  D161 add. 14's clarification has the K65 obligation in this shape ("an empty complete stream does
  the same"); it needs the same for the consumer-scan choice.
- The D158 addendum's text is "a decision that moves with the measurement set never moves the
  give-up surface". (a) Read as written, it binds the kit's picks too, and the kit has no input to
  obey it with. (b) It is STRICTER than D158 itself, which says "An optimization may turn a give-up
  into an answer (ONE_WAY)" (decisions.md:9393). It is also stricter than Q-WR-3 (D161 add. 15,
  decisions.md:9524: "a give-up may become an answer ... it relaxes at ST4 per measured cell").
  §8 lists no Q-WR-3 row. (c) §5.5's "(equivalently: the set may move a pick only in the ONE_WAY
  direction)" contradicts "never moves", because a ONE_WAY move does move the surface.

### FIXIND-4 — the accounting rule is false on today's code: RECOVER's per-match term depends on the kit's site pick
- **CONFIRMED** (code + 3 probes). Severity: design (an exactness claim). Effort: small to restate;
  the remedy is a one-bit frontier per site. Blast radius: §3.3 "the accounting rule", clause 5's
  last sentence, §3.6 G1 ("exact composition"), §3.6's hybrid check ("no such term was found"),
  §3.8's general form. Introduced by the **SLOT-1** fix (the (a′) accounting rule) together with
  the kit's NONE row (PREMISE-6 / D176 addendum). It does not reverse (a′) over (d).
- rev 1 §3.3: "The backend adds only terms invariant to the kit's choice at that site: the match
  phase, RECOVER and FINISH per match". RECOVER's `landing` row reads the kit's answer at the NEXT
  site. R/src/gen/emit_dfa.c:9662-9686 (`start_landing_applies`) calls
  `cand_ask(cx, CAND_SLOT_RECOVER, ...)` and returns `cs.cls.exists != 0` ("L4 the NEXT row
  selected for the forward machine HAS a block to record in"). `exists` is 0 exactly for the kit's
  NONE form (R/memfn/include/memfn.h:1088-1090: "0 for a form that searches nothing (NONE)"; NONE
  is not built yet, memfn/src/compose.c:309).
- So when the kit picks NONE (the priced "no search" row rev 1 adds), `landing` fails and RECOVER
  falls to `reverse-pass` (:10561). That is an unbounded reverse walk per match, plus the reverse
  machine (`.needs CAND_MR`), a size term as well. The kit cannot price pcrec's RECOVER rows, and
  the backend's term is not invariant to the kit's pick, so the composition is not exact.
- Probes (B -p rx, stamps): `x[0-9]*` gives `RX_DFA_PREFILTER "memchr"`,
  `RX_DFA_START "landing"`; `qz*` gives `"memchr"`, `"landing"`; `[QXZ]\w*` gives `"byte-class"`,
  `"landing"`. These are shipped picks on which a kit NONE would move RECOVER.
- The remedy is §3.8's own general form, "a frontier is needed only for a property the child
  cannot price": the kit returns its best pick for each value of `exists` (at most 2 options), and
  the backend adds RECOVER. That is a small reply-shape addition. It contradicts §3.6's "no such
  term was found, so the hybrid reduces to (a′)".

### FIXIND-5 — the beyond-window survival fact is composed wrongly: it adds a plan-dependent term where the true term is plan-invariant
- **CONFIRMED** (argument plus a script). Severity: design (an exactness claim; magnitude
  unmeasured). Effort: small (move the term). Blast radius: §3.3's `A(plan)` formula, Q4's S2 row,
  §5.3 "fuzzy to use", §7 row 3. Introduced by the **SIM-1 / COST-10** fix.
- rev 1 §3.3: `A(plan) = per_entry(route) + (rewalk(plan) + beyond(site)) x per_byte(route)`, with
  beyond a site fact pcrec states. The cost is entries(plan) x A(plan), so the beyond part is
  entries(plan) x beyond x per_byte.
- A false entry walks past the window only if every window position matched. The positions where
  the whole window matches are passed by EVERY verify plan at that alignment, because a plan's
  checks are necessary conditions. So their rate (entries(plan) x P(reach window end | plan)) is
  the same for every plan. The true beyond-window consumer work is therefore invariant to the
  kit's verify-depth choice, and this needs no model. By rev 1's own accounting rule it is a
  backend term. rev 1's form instead charges beyond bytes to entries that die inside the window,
  which biases the kit toward deeper verify plans.
- Script: `beyond.py` on R/tests/findings/default_ppm.tsv (r1 simulate's independence model,
  10.7 c/B, an illustrative 2 bytes beyond, the same as C_ENTER's ASSUMED figure). Output in
  `beyond_out.txt`. For `ereh` stop@1 verify{0} (SIM-1's option, 3,344.8 ppm, which matches SIM-1):
  rev 1's beyond term is 71,579 and the true term 243 (x1e-6 c/B). That is about 7.2 plan_cost
  units against SIM-1's totals of 28.6-32.0 units. The full-verify plan's term is 243 under both
  forms. `quick` verify{0}: rev 1 gives 14,231 and the true term 0.001.
- Siblings the new fact leaves unstated: how its "error bound per R4.6" is derived; what "bytes
  survived" means for the VM consumer (a backtracking walk); and that an EXPECTED survival needs the
  rate prior, a rate read in whichever side computes the fact (clause 1 bans rates only in
  validity, but crossings 7/8 retire rate work out of the front end).

### FIXIND-6 — "expected bytes seen" is a path fact, not a site fact: it adds a kit-to-backend read loop and multiplies the asks
- **CONFIRMED** structurally; materiality is SUSPECTED (rev 1 tags it INFERENCE). Severity:
  design. Effort: small to state. Blast radius: §2.5, Q4 S2 row, §3.6 G5, §6.2 hazard 3.
  Introduced by the **SIM-5** fix.
- §2.5's own example: NEXT's bytes are only those after the first landmark when FIRST takes the
  handoff, and none when presence fails. So a site's expected bytes depend on the hypothesized
  PATH (the backend's choice). The kit's quote then depends on the path, and the path's price on
  the quote. The kit must be asked per (site, path), not per site. This contradicts §3.6 G5 ("one
  quote per site"), and §6.2 hazard 3's declared asks multiply by path. The value is a pcrec-side
  estimate from the declared density regime fed into a kit choice, which sits next to Q-WR-9's
  "never a pcrec price model". rev 1 should say who computes it and from what, and that it is
  per-path.

### FIXIND-7 — clause 7's re-run holds, but form-dropping rungs are unstated, and they move prices
- **CONFIRMED** (code) for the gap; SUSPECTED for the `fit_seq_legal[]` trip. Severity:
  maintenance/design. Effort: small (one sentence). Blast radius: clause 7, §1.5. Introduced by the
  **SLOT-4 / PREMISE-8** fix.
- The re-run itself is what the driver already does: each rung re-runs the whole compile with its
  state (for example `cx.req_handoff_dropped`, compile.c:2342, read as validity at
  emit_dfa.c:8877 and :9046; deny bits OR'd in). An argmin inside emission re-runs by construction.
  That part HELD.
- Clause 7 speaks only of "a rung that drops a strategy family". `drop-premul`, `drop-anchored`,
  `drop-end-mark` and `prefilter-collapse` (compile.c:1342-1376) change backend FORM facts. Clause 3
  lets prices read those ("the backend's table form"), so a retry after `drop-premul` (~1.27x scan,
  compile.c:1376) raises the composite's per-byte price and can flip LOCATE to `cover` for a reason
  unrelated to what was dropped. Unstated: whether a form rung may move the strategy pick.
- Size is out of the price, so the re-run argmin can pick a LARGER path than first-match's
  successor would. The ladder then walks further rungs or refuses where first-match fitted. The
  trace build asserts the legal rung transitions pairwise (`fit_seq_legal[]`, compile.c:1792-1814);
  a pick that moves on re-run can produce a sequence not listed there (SUSPECTED; a size-capped
  probe under a prototype would confirm it).

### FIXIND-8 — I2's rate half already exists (KSTRACE); SLOT-10's withdrawal over-corrects
- **CONFIRMED** (code). Severity: doc (a supporting claim; §7 row 10 sized slightly high). Effort:
  trivial. Introduced by the **SLOT-10** fix.
- §6.3 (I2): `pcrec_find_byte_rate` "is called straight from predicates ... neither is observed. A
  hook on both". R/src/core/findings.h:420-439: in a `-DPCREC_KS_TRACE` build "every rate read
  writes one stderr record, `KSTRACE\tanalysis\t<query>\t<reader>\t<bundle|none>`, the READER being
  the calling function (`__func__`, so no call site is edited)", and the macro wraps both
  `pcrec_find_byte_rate` and `pcrec_find_set_ppm`. It is the attribution the data-mover census
  reads (`emit_sweep.py --data`). The rate half of I2 is an existing instrument plus a
  reader-to-class map. Set (measures) reads are unobserved as stated. A sibling hazard: the
  shadow's extra rate queries enter that stream, whose final-attempt queries are cross-checked
  against the `<PREFIX>_FINDINGS` items (SUSPECTED to trip only if KS_TRACE and CAND_TRACE are
  combined).

### FIXIND-9 — the shadow must still run quiet; dropping "or the quiet walk" loses the trace-stream and reach-check hazard
- **CONFIRMED** structurally. Severity: maintenance (check adequacy). Effort: trivial (one remedy
  line and one identity arm). Introduced by the **PREMISE-10 / COST-4** fix's wording.
- The `pf.used` save/restore is right. `used` has one reader (R/src/dump/facts_dump.c:169), and
  there are two precedents (emit_dfa.c:10830/10842 and :10996/:11190). That fix HELD.
- But the precedent rev 1 cites, `req_pres_proof_quiet`, does BOTH: quiet AND restore. The hit
  counter and the trace records are suppressed only under `pcrec_cand_trace_quiet`
  (emit_dfa.c:11510, :11550, :11585). The shadow "lives in the trace build", where
  `tests/codegen/run_cand_oracle.sh` reads CANDROW lines "to hold every row REACHED by its witness"
  (emit_dfa.c:10858). An un-quiet shadow that evaluates rows first-match never reaches marks them
  REACHED, so the reach check could no longer fire for them. Stage 1's identity gate lists `used`
  and `RX_MEASURES`, but not CANDTRACE/CANDROW identity.

### FIXIND-10 — §5.4's interim cites D176 Q5's resolution as present; it is ruled, not built
- **CONFIRMED** (SRS text). Severity: doc (adds one gate). Effort: trivial. Introduced by the
  **SIM-6 / COST-9** fix.
- §5.4: "ties are exact-integer ties only (D176 Q5's resolution already separates `\d\dxyz`'s 997
  vs 498 ppm)". SRS (lane/memfn-stopstudy stop_ranking_study.md:449) says of today's pick
  "main's `x` is the integer-unit tie (§4.3)". D176's Effect says the build waits. In today's unit,
  exact-integer ties ARE rounding ties, which D176 Q1 rules out ("near-ties are decided by rates,
  not rounding"). So the interim is coherent only after Q5's resolution lands, and stage 3's gate
  should list it.
- Checked and held: the interim does NOT contradict `wf_ties[]` (memfn/src/window.c:83-104; every
  row resolves an EQUALITY: equal mass, equal cost, `best * NUM == base * DEN`) or Q5's
  "decided by the existing declared tie rows". No shipped pick moves: the kit already ties on
  equality, and no backend argmin ships.

### FIXIND-11 — the "total simplicity order" over PATHS is an unfilled cell
- **CONFIRMED** (text). Severity: design (small). Effort: small. Introduced by the **SIM-6** fix
  (two-pass rule) and the SLOT-19 D152 addendum ("row order is the simplicity order").
- Pass 2 takes "the first in the declared simplicity order (total; table order as the last key)".
  Rows have a table order; a path is a tuple of rows across slots, and no order on tuples is stated
  (lexicographic by which slot first? LOCATE first?). Different choices pick different paths on an
  exact tie. One declared key is needed (for example, slot order of `cand_nodes[]` then row order).

### FIXIND-12 — "(a′) needs no reply-shape event" contradicts rev 1's own cost table
- **CONFIRMED** (text + code). Severity: doc (§3.6 S3 still favours (a′)). Introduced by the
  **SLOT-1 / COST-2** fixes.
- Summary 3 and §3.6 row 8 say "no reply-shape event". §7 row 5 under (a′): "price components + set
  id on the existing pick" (plus "its ranking as data", §3.3). `mf_wreply`
  (R/memfn/include/memfn.h:1420-1435) has no such fields, so adding them is an MF_SITE_ABI event,
  as is a NONE pick and FIXIND-4's `exists` split. It is smaller than (d)'s frontier reply, but it
  is an event.

### FIXIND-13 — the nullable decline is called a price in clause 2 and a validity failure in §2.1
- **CONFIRMED** (text). Severity: doc. Introduced by the **PREMISE-1** fix.
- Clause 2 lists "the nullable decline" among prunes "resting on a measurement" (a price,
  UNMEASURED-DEFAULT). §2.1 and the CHANGES row say "Under clause 8 the row fails VALIDITY". Also,
  the decline is a `pf_admits[]` row at ROUTE-PAIR level (`select_engine.c:669-799`), which is
  priced only at open point 7. Clause 8 ("a priced slot's valid set") does not reach it this round;
  the K row is the remedy, as rev 1 says elsewhere.

### FIXIND-14 — stage 3 depends on the kit reading the consumer rows, but §6.4 files that as a separate trigger
- **CONFIRMED** (text). Severity: design (an ordering gap). Introduced by the **COST-1** re-order
  together with the (a′) accounting rule.
- §7's closing sentence: the first priced slot needs "the D176 build for row 6" (the kit reads the
  consumer rows). §6.4 lists that stage as "filed, trigger: the D176 build", and stage 3's gate does
  not name it. Without it, the composite path's consumer walk at its NEXT site would have to be
  added by the backend, which clause 5 forbids (that walk varies with the kit's pick). Stage 3's
  gate should list it.

### FIXIND-15 — doc items
- §1.2 labels `fixed` P; its own desc is "always (fallback, the deny's landing row)" (emit_dfa.c
  :10492), and `adaptive` above it is `cand_always`. The counts become fb 5 and priced 22 (the
  24/4/23 sum to 51 does check out). From **PREMISE-5**.
- "NONE row" (no pre-scan) collides with `MF_ENTRY_NONE` (memfn.h:515-517: "no entry fact: the
  candidate is the window's own"). The kit's own name for a form that searches nothing is class
  `exists 0`. Also, "entry kinds the consumer accepts" (new in Q4): today pcrec states ALTERNATIVES,
  each its own span list with an entry fact (memfn.h:513-518). rev 1 does not say whether the new
  field replaces the alternatives or rides beside them. If it replaces them, who builds the RESEED
  alternative's spans? From **SLOT-1 / SIM-7**.
- `path-needs-unbuilt` is at emit_dfa.c:11950, not :11946 (§2.4).

## PROBED-AND-HELD

Fixes spot-checked against rev 1's text and the review tree: 22 CHANGES rows. Held as fixed
(beyond the gaps above):
- **SLOT-1**: (a′) added; Q-WR-9 quoted in full and correctly (decisions.md:9526).
- **PREMISE-6**: add. 14 affirmed (decisions.md:9511-9519).
- **SLOT-5**: `CandPath` (emit_dfa.c:11828) and `cand_path_of` (:11916).
- **PREMISE-11**: `CandRoute` (internal.h:9174); HORS_MIN still read (window.c:1594-1596).
- **SIM-3**: MARGIN's basis ARGUED (window.c:708-712).
- **PREMISE-3**: `run_pin` takes the rate (facts.c:324-328, kset.c:294).
- **PREMISE-4**: the `no_commoner` rate disjunct (emit_dfa.c:8554).
- **SLOT-7**: possessify/revdet read `fit.chosen` (select_engine.c:498-525).
- **SLOT-11**: A1's by-name read (compound.c:204-210); `T ⊊ E` and `|S|<256` UNMEASURED-DEFAULT
  texts (emit_dfa.c:7872-7876, :8020-8026).
- **COST-3**: `consulted = 0` (memfn_sites.c:977-980).
- **COST-9**: `noise_e6` is `-` on all 68 rows of measure_store/zen4-grid1/1/set.tsv (counted).
- **SLOT-8**: plan.md:331, and the census's 10/80 and 19/83. The census's third row (60/80
  match-compliance) is explained there as a bench artifact (cause D), so leaving it out is fair.
- **SLOT-12**: the LOCATE row order empty, rev-end, cover, composite matches the mixed-slot prefix
  rule (zero movers).
- **SLOT-13**: clause 4's "miss is an internal error" cannot fire on today's kit.
  emit_dfa.c:7322-7325: "the reply can carry C-pin only where they hold, since R is stated only
  then". This answers open point 14 in rev 1's favour.
- **PREMISE-10 / COST-4**: `used` save/restore (see FIXIND-9 for the part it misses).
- **SLOT-4**: the re-run mechanism (see FIXIND-7 for its siblings).
- **SIM-6**: the two-pass rule is order-free as stated; it does not contradict `wf_ties[]` or D176
  Q5's tie rows, and it moves no shipped pick.
- **COST-1**: `cover` is CR_DFA only, so the LOCATE-first slot is a DFA-route choice.
- **PREMISE-5**: the 24/4/23 = 51 arithmetic is recounted from `cand_rows[]` (51 rows listed in
  order).

Partly held, with a finding: SIM-1/COST-10 (`A(plan)` named, but FIXIND-5), SLOT-15 (FIXIND-1/2/3),
SLOT-10 (FIXIND-8). Claims tested hardest, as rev 1 asked: §3.3's composition (FIXIND-4, -5),
§3.6's scoring (FIXIND-4, -12; (a′) still wins every row it claimed), §5.4's interim (FIXIND-10;
held otherwise), clause 8 (FIXIND-1, -2, -3).

Cite checks: about 40 file:line cites; one is off (FIXIND-15) and a few are dir-less but
unambiguous (`findings.c:429` is src/core/findings.c; `memfn.h` is memfn/include/memfn.h).

Probes: 6 compiles of B (`x[0-9]+y`, `q\w+z`, `ab[cd]+e`, `x[0-9]*`, `qz*`, `[QXZ]\w*`), 1
`--emit-facts`, 1 `--list-axes`. Scripts: `beyond.py` (one run). No make, no suites.

## STATE AT HANDOFF

STATE: complete
OWED: none
