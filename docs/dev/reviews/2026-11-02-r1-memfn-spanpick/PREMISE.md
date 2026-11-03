# PREMISE lens — crit-memfn-spanpick round 1 (subject span_pick.md rev 1, frozen copy)

Review tree: worktrees/crit-memfn-spanpick @ 884996ef6. All file:line below are IN THE REVIEW TREE.
Method: grep + read of memfn/src and src/; a sample of single-pattern compiles with the trace build
(count stated per finding). No make, no timing.

## Findings

### PREMISE-1 — "The frame is a fixed fact chosen by pcrec's NEXT row": the frame is chosen by the KIT's Table E, whose legacy rows read the PLAN; it is a function of stated facts on the sampled population, but not by construction
CONFIRMED for the code dependency; SUSPECTED (unsampled) for a stage-1 mover. Severity: design / doc
(+ stage-1 byte-identity risk). Effort: small (state the frame class as the stated-fact key that the
data shows, and keep the legacy predicate as a validity condition or prove it constant). Blast
radius: T-FIND's validity column, N4, N11, §Frame availability, step 1 "FIXED FACTS ... frame class".
Subject: §The shape step 1; §Not tables ("The frame (Q8) is a fixed fact chosen by pcrec's NEXT row
from the reply"); §Frame availability; N4, N11.
- Who chooses: memfn/src/window.c:1444-1455 `wf_erows` (E-func, E-stmt, E-find, E-generic) is a kit
  table walked in phase 2. pcrec's NEXT rows (`next_keys`, src/gen/emit_dfa.c:7299) choose the
  route/handoff from the phase-1 reply, which carries no E row. "Chosen by pcrec's NEXT row from the
  reply" is false as written; what pcrec states is `form`/`handoff`/`wfloor`/`site_kind`.
- What it reads: E-func/E-stmt hold only if `legacy_ok(d, w, &eb)` (window.c:1196-1229: every plan
  position core, <= MF_MAX_TERM terms, the core bound vs the terms, the empty-range rule) AND
  `kit_legacy_serves` over the translated PLAN (window.c:1384-1393); E-find holds iff Table D + fd_find
  + Table B rendered the plan (window.c:1403-1407, 1719-1755). So the frame is, by code, a function of
  the plan the kit chose, and the method follows the frame (E-stmt -> fd_route, no PAIR; E-find ->
  fd_find, PAIR possible: finder.c:306 needs SF_WINDOW_STOP, set only at finder.c:938).
- What the data says (R-33 sweep, 3,489 window sites with a wfE end; script premise/py/frame.py,
  output py/frame.out): the E row is a PURE function of (form, handoff, site_kind, wfloor) on every
  sampled site (14 classes, one E row each); every two-member stop is PAIR on site_kind REPORT
  (E-find, 101) and R7w walk on every other kind (E-stmt, 279). So in practice "frame class" =
  "REPORT or not" plus form/handoff, and the plan-dependence never fired in this population.
- Consequence: (a) the design's T-FIND validity column keyed on a fixed frame class reproduces
  today's answers on the sampled population, but stage 1's byte identity then rests on an unproved
  invariant ("legacy_ok + kit_legacy_serves hold for every non-REPORT window plan"); the build must
  either prove it (and delete the plan-reading condition) or keep it as a plan-time validity input,
  in which case the frame is not a step-1 fixed fact and the inner-first order needs the verify plan
  before the method's validity is known. (b) The effective frame class IS the REPORT label
  (site_kind 6), which sits awkwardly with §The shape's "No row reads a label (REPORT, OFS)": say
  that the validity column reads the stated consumer kind.
- Smp20 illustration (3 compiles, lens dir c/smp20*.trace): one stop set {x,X} at offset 0 renders
  PAIR under E-find (default, site 1, `moved_from=A-parked`, E-stmt PRED_FALSE), fn-pair under E-func
  (VM, site 2) and the walk under E-stmt (VM, site 3, `fd=R7w`).

### PREMISE-2 — N9 "precheck's own memchr asked through T-FIND (byte-identical expected: same memchr text)": neither the question nor the text nor T-FIND's first-match answer is the same
CONFIRMED (code read + 1 compile). Severity: design / answer-risk to stage 1's zero-mover bar.
Effort: small to state, medium to build (a presence fact or a separate T-PRES rendering). Blast
radius: every pre-check site, i.e. every VM_ATTEMPT route with required bytes. Subject: §What stage 1
deletes N9 and U3 ("precheck's parts ask T-FIND"); §The tables T-FIND "replaces ... precheck's own
memchr (N9)".
- The precheck texts are PRESENCE tests, not finds: memfn/src/precheck.c:281-291 `gate` emits
  `if (n <= lo || !memchr(s + lo, b, n - lo)) on_miss`; :302-313 `landmark` a statement-expression
  ASSIGN with `<prefix>_mf<handle>_q`; :317-336 `set_rest` a `static const unsigned char rq_set[]`
  loop of memchr. None is pffind.c's `pf_memchr_use` text (pffind.c:253-266,
  `const void *q = memchr(...)` then the store). "Same memchr text" is false; byte identity is
  reachable only by keeping precheck's three renderers, i.e. N9 is not deleted.
- Asked as a FIND, T-FIND's first match is NOT memchr on the very sites precheck serves: the
  pre-check's consumer kind is `site_kind_of(cx, SKS_PRE)` (src/gen/emit_dfa.c:8737), VM_ATTEMPT
  on the VM route; finder.c:809-813 sets SF_SEEK_ROLE for span 0 of a VM_ATTEMPT site, D1
  (finder.c:282) has SF_SEEK_ROLE in its excluded facts, so the one-member answer is D1w, the walk
  (finder.c:293). Repro: `tracebuild/pcrec -p rx --engine=vm --pattern '(\w+)\s*=\s*(\w+);'` ->
  trace `kind=VM_ATTEMPT ... slot=PRES` and the artifact carries precheck's `!memchr(subject +
  search_from, 59, ...)` gate and the `rq_set[] = { 61 }` loop (lens dir c/vm1.c:301-308). Routing
  those bytes through T-FIND first-match yields walk, not memchr: a mover on every VM pre-check.
- The question is Q9's (presence: "is b anywhere in [lo, n)"), not Q3's ("next member of S at d");
  the design itself lists T-PRES for presence. N9 belongs under T-PRES's rendering, with its own
  answer (always memchr today), not under T-FIND.

### PREMISE-3 — U8 "generic.c asks T-CMP if byte-identical": byte identity is unreachable for every exact RUN term and every masked run of length >= 2, so U8 cannot be in stage 1 and T-CMP keeps two deciders after it
CONFIRMED (code read). Severity: doc / maintenance (Goal 3's "exactly ONE per question after
stage 1" is not met for T-CMP; U8 is a unit change by construction, not a conditional). Effort:
small (move U8 to the unit-change list with its own deny now). Blast radius: every generic-row
(floor) predicate with a RUN term. Subject: §What stage 1 deletes U8; Goal 3; §The tables T-CMP.
- generic.c:180-209 renders each RUN byte as `S[cand+off+j] == b` (or `(S[..] & m) == b`, or the
  constant `0` for an impossible masked byte), joined by `&&`.
- runcmp's first-match rows (runcmp.c:108-132, predicates runcmp.c:172-187): an EXACT run of any
  length gets `overlap` (len 3, 5-7, 9-15) or the undeniable `memcmp` fallback (every other
  length, 1 and 2 included) — never a per-byte `==` chain; a MASKED run of length >= 2 gets
  `words`; only a masked run of length 1 (or any masked run under MF_D_RUN_OVERLAP) reaches the
  per-byte `bytes` row. So "asks T-CMP" moves bytes on essentially every RUN term the floor renders;
  the "if byte-identical" branch is empty in practice.
- The hedge ("else a separate unit change") is correct, but the design's stage-1 accounting (U8 in
  "What stage 1 deletes", Goal 3's one-decider count) presumes it. State U8 as a unit change
  (D186 bar, its own deny, a 588-style regime run: memcmp/words vs a byte chain in an `&&`
  expression is not obviously faster on short runs) and count T-CMP at two deciders after stage 1.

### PREMISE-4 — "T-FIND asked once per candidate" has NO answer on the DFA prefilter OFS sites: they state no consumer kind, and every FIND row uses it; so the RESEED KEY row ("not memchr => UNPRICED") as written prices nothing
CONFIRMED (code read + R-33 data, 381/381 sites). Severity: design / answer-risk to stage 1 (the
RESEED KEY and MARGIN would change on every OFS site). Effort: small-medium (either pcrec states a
consumer kind on OFS sites — a pcrec-side fact, an MF_SITE_ABI event — or the RESEED KEY restates
`scan_ok` instead of reading T-FIND). Blast radius: every DFA prefilter OFS site (all of the
E-func class); U1, U3, N1, N5, N6, the RESEED/PARKED KEY rows.
Subject: §Stage 1's KEY rows RESEED ("candidates whose T-FIND answer is not memchr are UNPRICED ...
today's `scan_ok`"); U3 ("T-FIND asked once per candidate; ... `fn_rows` BODY ... become renderers
keyed by the pick"); N6 ("same answers (stage-1 keys read no method price but memchr's)").
- Every FIND row's contract uses `site_kind`: D1/D1c/D1w/PAIR/R4 `use_kind`, R7w `use_kind`
  (finder.c:198-232); R8/R1 `use_mn_kind`, R2 `use_mn`; R3a/R3b need KN_H, which never holds
  (finder.c:539). The gate DECLINES a row whose used field is UNSTATED (gate.c:15), and
  `kind_cl(MF_SK_UNSTATED)` is -1 (finder.c:400-403).
- The OFS sites state no kind: in the R-33 sweep every window site with (form FUNC, handoff 0,
  site_kind 0 = MF_SK_UNSTATED) — 381 of 381, all E-func, alternatives (PARKED, RESEED) — ends
  `fn: fn-memchr` with NO `fd` row walked (premise/py/ofs.py). Today their method comes from
  ofsskip.c `fn_rows` BODY (ofsskip.c:415-416; `pair_holds` = the scanned position is a two-member
  CUBE, else `fn-memchr`, the floor) and A-model's `scan_ok` (window.c:446-449: walked, core, ONE
  member), neither of which asks fd.
- So, asked as designed, T-FIND returns no row for every OFS candidate; "not memchr => UNPRICED"
  then leaves every RESEED candidate unpriced, A-model's stop and MARGIN's comparison disappear,
  and the alternative falls to PARKED everywhere: a mass mover, not stage 1. To stay byte-identical
  the RESEED KEY must restate scan_ok's one-member test itself (as today), and fn_rows BODY must stay
  a decider (cube => fn-pair) until pcrec states a kind on OFS sites; U3's "four deciders -> one" is
  then three until that pcrec-side change, which the design does not list (§pcrec-side findings).
- Also: fn-pair's condition (a two-member CUBE inside a RUN term) is not fd's PAIR condition (ANY
  two bytes, SF_WINDOW_STOP): "renderers keyed by the pick" must add the cube/run-term test as a
  renderer validity, i.e. a decision the renderer still makes.

### PREMISE-5 — "each is a `kit_table` on `kit_walk` ... In stage 1 each table answers first-match exactly as today": Table C (T-VERIFY) is not first-match and not on kit_walk today; it is a step-ordered pipeline where every holding row applies
CONFIRMED (code read). Severity: design / doc (a first-match T-VERIFY cannot answer as Table C does;
a kit_walk wrapper changes trace/reach output). Effort: small (say T-VERIFY is a declared step list,
or split it into per-step first-match tables). Blast radius: T-VERIFY, T-SETTEST, U10, N1, the trace.
Subject: §The tables intro and rows T-VERIFY, T-SETTEST.
- window.c:42-44 (header): "Every table is a `kit_table` on the one walk (kit_walk; Tables A, M, D,
  E) or a declared row list read in order (C, TIE, and B's renderers ...)". `c_plan`
  (window.c:968-976) applies EVERY row whose `holds` is true, in step order (C-floor | C-yes,
  C-model | C-none, C-pin, C-stop, C-run, C-asc are cumulative; C-model and C-pin also set state:
  `d->reseed`, `d->pinned`, window.c:819, :878). That is a composition of 7 steps, each with
  its own rows — at least five questions, not one first-match answer.
- C-table / C-own (window.c:962-963) are listed under BOTH T-VERIFY ("Table C's 12 rows unchanged")
  and T-SETTEST ("offered table T[b], then the kit's range chain ... C-table/C-own"): the
  six-table count double-books two rows.
- Consequence for the shape: T-VERIFY's C-pin sets RE-SEED on a PARKED alternative, and `rd_set`
  (window.c:251-254) widens what a PARKED plan may READ only when that bit is set: the "soundness
  flag" "on a PARKED alternative only verify-YES positions are readable" (§The shape) is itself an
  output of T-VERIFY, not a fixed step-2 fact. Stage 1 is unaffected (the PARKED stop is k0 only),
  but stage 3's priced position level would have to price stops whose readability depends on the
  verify plan chosen for them.

### PREMISE-6 — U9 "`plan_cost.def` row reads `limits.def`" crosses the kit boundary: the kit may not read pcrec's `src/`
CONFIRMED (grep). Severity: design (D157 / kit boundary). Effort: small (pcrec STATES the budget as
a site/art fact, or the kit owns MAX_SET and pcrec's limits.def cites it). Blast radius: U9, §Cost
cards "Not cards: MAX_SET (... read from limits.def's PCREC_OFSK_MAX_SET, U9)".
- memfn/CLAUDE.md:29: "pcrec's sources reach the kit ONLY through `memfn/include/memfn.h`; the kit
  links nothing from `src/`, `cli/`, `lib/`." The kit's only includes are `../include/memfn.h`
  (memfn/src/kit.h:14, k1_ref.c:12); no kit file includes anything under src/. memfn is its own
  0BSD unit with a PROVENANCE.md per file.
- `PCREC_OFSK_MAX_SET` is src/core/limits.def:393 (`INTERNAL_H`), pcrec's internal limit; the kit's
  copy is plan_cost.def:50-53 (`MAX_SET, 4`, provenance text names limits.def). A plan_cost.def row
  that "reads" limits.def makes the kit depend on a pcrec internal header — the inverse of the
  boundary. If the number is pcrec's (a compile budget over pcrec's statement), D157 says pcrec
  STATES it with the facts (e.g. on `mf_art_begin` or the window statement), which is a memfn.h
  field and an MF_SITE_ABI event, not a no-mover include.
- Values agree today (4 = 4), so U9 is a duplicate in fact; the fix's home is the open question.

### PREMISE-7 — "keyed by class ... chosen by the target, not the host ... its class's DEFAULTS row": no compile can declare a target class today; every compile is class `idk`
CONFIRMED (spec + store read). Severity: design (Goal 4 unreachable as worded without a new
caller-facing input). Effort: medium (a target-class option: a caller-observable change, D80 spec
hunk, and under the owner's [IFACE-PUSH] hold for new options). Blast radius: Goal 4, §Cost cards
"Chosen by the target", Open question 2, stage 3's per-class picks.
- docs/spec/measures.md 5¶6: "Today there is one class, `idk` (a compile that declares none), and its
  default is the latest committed set: `zen4-grid1@1`". measure_store/DEFAULTS holds one line,
  `idk	zen4-grid1@1`. A compile names a SET (`--measures`, 5¶1), never a class.
- So "measured on the target's class" (Goal 4) is true only when the caller hand-names a set; the
  default compile always prices with zen4's cards whatever it targets. Adding Zen 1/Apple sets in
  stage 2 changes nothing for a default compile until a class declaration exists. The design should
  list that declaration (option spelling, spec 5¶6 rewrite, DEFAULTS rows per class) as owed work, or
  re-word Goal 4 as "measured on the named set's box".

### PREMISE-8 — "Generated C carries no costs ... it moves bytes only where a T-PICK row admits a departure and the new prices change a dominance verdict": false — the `<PREFIX>_MEASURES` stamp moves on every artifact whose pick READS a card, departure or not, and again on every card revision
CONFIRMED (code read + 1 compile). Severity: design / maintenance (stage-3 movers census and abi
accounting understate the byte movers by the whole consulting population). Effort: small to state
(count stamp-only movers as their own class in each census; or rule how the stamp reads a
priced-but-kept pick). Blast radius: every stage-3 row's class; every card rev / DEFAULTS move.
Subject: §What moves when the data is regenerated; §Cost cards "Generated C carries no costs";
§Staging stage 3 (movers census) and "Re-measuring is a deliberate data change".
- memfn/include/memfn.h:1291-1294: `consulted` is "1 iff some kit row whose decision the art's text
  CARRIES resolved a key against the set, found or absent"; src/gen/memfn_stamps.c:273-291
  `meas_stamp` renders `<PREFIX>_MEASURES` as `id@rev:digest16` iff consulted, else "".
- Today no carried decision consults (the finder's key rows are inert, finder.c:378/862: "a ROUTED
  decision's lookups set `consulted` (never at B1)"), so every artifact stamps "": smp20's default
  compile carries `#define RX_MEASURES ""` (lens dir c/smp20.c:311).
- Stage 3: a site in a T-PICK row's class prices default and challengers from cards, so it consults
  even when the default stands; its stamp changes from "" to `zen4-grid1@1:<digest>` — a byte mover
  with no pick change, on the row's whole class. A later card rev changes the digest on every
  consulting artifact, again with or without a pick change. The design's "moves bytes only where ...
  a dominance verdict" and its movers census ("each moved site judged under D186 as a choice
  change") would either count these stamp-only movers as choice changes (each needing per-regime
  evidence: absurd) or miss them (K35: the census undercounts). Name the class and its handling.

- Two committed checks encode today's "no row reads a key" and break at stage 3's first row, unlisted
  in §Independent control: tests/memfn/finder_check.py check F ("`consulted` is 0 on every compile
  ... the true arms are OWED to the first row that does", :43-44) and check D ("every finder site
  under NO set and the FULL synthetic set decides the same rows", :38-41). Stage 3 owes their
  replacement (the true arms) in the same change.

### PREMISE-9 — "presence states unbounded spans (D176 Q4) ... every scenario routed through the one call" in stage 1 rests on [MEMFN-UNBOUNDED-SPANS], which is not started and is itself an MF_SITE_ABI event
CONFIRMED (plan/header read). Severity: design (stage-1 scope and its "Abi: none" claim). Effort:
small (say presence keeps T-PRES's own entry in stage 1, or list the pcrec-side row as a stage-1
dependency with its abi event). Blast radius: the presence scenario, T-PRES, Stage 1's abi line,
§pcrec-side findings (which omit it).
Subject: §What is a scenario ("presence states unbounded spans (D176 Q4) and asks the same tables
with a presence price"); §Staging stage 1 ("every scenario routed through the one call ... Abi: none
if bytes are identical").
- docs/dev/plan.md:952-957: `[MEMFN-UNBOUNDED-SPANS] STATE:not-started`, "nothing built", trigger
  "an MF_SITE_ABI event: pcrec abi bump, identity re-pin and spec hunk in the same change". The
  window statement today has no unbounded-offset span: presence is stated as `npspan`/`pspans`
  predicates on an ALL_PRESENT site and decided by the finder's PRES slot (finder.c:837-841
  `fd_scope`; P0..P9 rows finder.c:330-349) over `kit_pres_picks` (presence.c:149-247), not by the
  window family.
- So in stage 1 the presence scenario cannot "make the SAME call" without a pcrec-side statement
  change that is an abi event by its own row. Either stage 1 keeps presence on T-PRES's entry (and
  the "one call for seven scenarios" claim becomes six), or stage 1 carries the pcrec row and its
  MF_SITE_ABI event. The design's §pcrec-side findings list does not mention it.

### PREMISE-10 — the pick's "within the band the DEFAULT stands" departs from D176 Q5 ("prices within the measurement-noise band tie, decided by the existing declared tie rows") without citing it
CONFIRMED (decision read). Severity: doc / design (a ruled row is changed silently). Effort: small
(cite D176 Q5 and either add the default as a declared TIE row in `wf_ties`, or ask the owner).
Blast radius: §The pick step 3, §Robustness "The margin is measured".
- docs/dev/decisions.md D176 Q5 (line ~9917): "prices within the measurement-noise band tie, decided
  by the existing declared tie rows." The subject (§The pick 3): a challenger replaces the default
  only if cheaper beyond the combined band under BOTH models; "Otherwise the default stands", and
  only "among several qualifying challengers ... ties within a band go to the TIE table".
- These differ: under D176 Q5 a near-tie between default and challenger goes to `wf_ties`
  (window.c:79-104: offset-based rows, TIE_HIGHER/LOWER/...), which can pick the challenger; under the
  design it always goes to the default. The design's rule is arguably the right one (it is what
  makes stage 3's movers bounded and is the walk-vs-V1 precedent), but it is a change to a ruled row:
  say so, and either ask the owner or express "the default" as a declared TIE row so Q5's letter holds.

### PREMISE-11 — stage 3 is pricing inside rows; D186 says pricing is deferred until hand-written rows conflict
SUSPECTED (a reading of D186 against the design; the owner's own 2026-11-02 direction, quoted in
R-33's request, asks for a "fact-derived key: mass x streams + verify per hit", so the owner may
intend exactly this). Severity: design (owner-level premise). Effort: one owner question. Blast
radius: §The pick, §Staging stage 3, Goal 4.
- docs/dev/decisions.md D186 (line 10020-): a choice change "is a ROW in the declared choice table: a
  condition on stated facts, plus per-regime evidence"; "Pricing ([PRICE-BAKEOFF], deferred) returns
  only if hand-written rows start conflicting." The subject's T-PICK rows admit a priced departure
  whose OUTCOME is the cards' argmin, so the row's per-regime evidence covers only the picks the
  cards made when the evidence was taken; a card rev re-decides inside the row (the design handles
  that by judging each moved pick again, §Staging "Re-measuring").
- The subject cites D176 Q1 (one priced choice, 2026-10-23) as the cost basis and D186 (2026-11-02,
  later) as the staging basis; D186's "pricing deferred" sentence is the later ruling. Ask the owner
  whether a kit-local per-site price inside a T-PICK row is "pricing" in D186's sense (the
  strategy-level bake-off) or a row's action (architecture.md: "An optimizer may sit inside one
  row's action"). If the latter, the design should say so in one line citing both.

### PREMISE-12 — U5 "presence.c `tie_over` reads `wf_ties`" and U4 "one mass primitive": `tie_over` is a rule no `wf_ties` row states, and `window_mass` is not a call of the per-set primitive under the NONE rate
U5 CONFIRMED (code read); U4 SUSPECTED (arithmetic shown; whether any compile runs with no byte
rate not checked). Severity: maintenance / doc (stage-1 byte identity needs a NEW tie row and a
NONE-mode carve-out, not a pure re-pointing). Effort: small. Blast radius: P3's set pick, P3's run
window under NONE. Subject: §What stage 1 deletes U4, U5; §Not tables ("ONE tie table ... every
level reads").
- U5: presence.c:128-134 `tie_over` breaks a mass tie between two presence MEMBERS by
  `member_order` (a known pattern position above an unknown one) and then the LARGER BYTE value. Every
  `wf_ties` row (window.c:79-104) compares OFFSETS (`tie_takes`: higher/lower offset, exchange,
  parked/reseed, leftmost). Members of a presence set have no offset; "reads it" needs a new
  `wf_ties` row ("presence member: pattern order, then larger byte") — fine, but it is an addition
  to the tie table, not a deletion, and the design's U5 line should say so.
- U4: presence.c:58-121. `cube_mass(t, mask)` equals `kit_set_sum` over the cube's set (same sum;
  NONE: `uniform_mass(2^free)` = `uniform_mass(k)`) — that identity HOLDS. But `window_mass` under
  the NONE rate (rate NULL) is `uniform_mass(total members over 8 positions)` = floor(K x 1e6 / 256),
  while a sum of the per-position primitive is a sum of floors: 8 caseless positions (2 members each)
  give floor(16e6/256) = 62,500 against 8 x floor(2e6/256) = 62,496. Rewriting window_mass over the
  one primitive moves the window comparison's arithmetic under NONE; keep a NONE-mode total or show
  no compile hands the kit a NULL rate.

### PREMISE-13 — Stage 3 item 3 ("RESEED candidates of any set size priced with PAIR/walk cards", R-33's R2 "95 PF units") has no renderer in the frame those sites use; and "PF" means two different site families in the subject
CONFIRMED (code read + R-33 report). Severity: design (a stage-3 row presumes a renderer that
does not exist; the same gap the design names for item 4 is unnamed here) / doc (terminology).
Effort: small to state (add "a FUNC-frame PAIR/walk renderer" as a unit addition before item 3, as
item 4 has); medium to build. Blast radius: stage 3 item 3, Open question 5, §Frame availability's
"the end state gives every frame that hosts a find the same renderers".
- R-33's R2 sites are the DFA prefilter OFS sites (r33_report.md:168-173: "Today: A-parked, then
  A-floor for RESEED ..., then M-parked"; examples `(?i)hello.*world`, loglines level-context,
  altwide), i.e. the subject's "DFA prefilter OFS" scenario (FUNC/RETURN, E-func), not the
  subject's "PF find" scenario (DELEG_PF, STMT/ASSIGN, "one alternative with one candidate").
  R-33 calls OFS sites "PF units"; the subject copies the label into stage 3 item 3 while its own
  §What-is-a-scenario uses "PF find" for DELEG_PF. Rename (e.g. "OFS units").
- In the OFS frame the only renderer is ofsskip's function: `ofs_fn_applies` (ofsskip.c:106-134)
  admits a scan position that is ONE byte or a one-bit CUBE inside the one RUN term; fn_rows BODY is
  fn-pair (that cube) or fn-memchr (ofsskip.c:415-416). E-find serves only STMT/ASSIGN
  (window.c:2766-2771 `wf_find_ct`: `[FLD_form] = CM(STMT), [FLD_handoff] = CM(ASSIGN)`), so a FUNC
  site whose stop is any other set (R2's {A,R} non-cube pair, {L,l} outside a run term, a 21-byte
  set) falls to E-generic, the floor's byte loop.
- So item 3 cannot be "a T-PICK row" alone: T-FIND's validity column (per the design) would decline
  PAIR/walk in the FUNC frame and the row could only re-pick among one-byte/cube stops — which is
  NOT R-33's R2 population. The design must list a FUNC-frame two-stream and walk renderer (a unit
  addition with its own deny and card) as item 3's prerequisite, exactly as it does for item 4.

### PREMISE-14 — Stage 1 "Abi: none if bytes are identical; an MF_SITE_ABI event only if the plan call's seam changes `mf_site`": the design's own stage 1 grows the reply struct, which MF_SITE_ABI covers, so the event is certain
CONFIRMED (header read). Severity: doc / maintenance (stage-1 accounting; Goal 2 and §Staging
disagree with each other). Effort: small (state the MF_SITE_ABI bump and its pcrec readers in stage
1). Blast radius: §Staging stage 1 abi line, §The designer/emitter split "What moves across", Goal 2.
- memfn/include/memfn.h:39: `#define MF_SITE_ABI 20  /* layout and meaning of every struct below.`
  `mf_wreply` is below it (memfn.h:~1430-1444). The subject's §"What moves across": "The plan reply
  grows from window_site's phase-1 reply ... by the method and resume ... Moving them into the plan is
  exactly stage 1's deletion of the duplicate deciders, so the split and stage 1 are one change". A
  grown public reply is an MF_SITE_ABI event by the header's own rule, whatever `mf_site` does.
- House practice treats an MF_SITE_ABI event as a pcrec abi event (plan.md:955, [MEMFN-UNBOUNDED-
  SPANS] trigger: "an MF_SITE_ABI event: pcrec abi bump, identity re-pin and spec hunk in the same
  change"). Goal 2 already says "byte-identical to main but for the abi digits"; §Staging's
  "Abi: none if bytes are identical" contradicts it. Say: stage 1 = one MF_SITE_ABI bump (+ its
  pcrec readers by grep, D94), zero movers otherwise.

### PREMISE-15 — "every plan of one site hands to the same consumer, so only passes_r differs": false at the alternative level (PARKED resumes, RESEED re-seeds)
SUSPECTED (the premise is false by the design's own consumer list; the size of the entry-cost
difference is unmeasured). Severity: design (a missing term at pick level (c)). Effort: small (one
`enter` card per entry fact, PARKED vs RESEED, or a stated argument that they are equal). Blast
radius: §The pick level (c), stage 3 item 3 (MARGIN replaced by the robustness rule).
- Subject §The pick: "`c_enter` is per consumer kind (DFA re-seed, VM attempt) ... every plan of one
  site hands to the same consumer, so only `passes_r` differs between plans". Level (c) compares a
  PARKED alternative (the matcher resumes parked) with a RESEED one (the matcher is re-seeded at the
  candidate): two entry kinds at one site. Today's model charges both the same C_ENTER
  (window.c `model_cost`, one COST(C_ENTER) term, used by A-parked :420 and A-model), and MARGIN's 2x
  was argued as a materiality bar, not an entry-cost difference (offset_k_skip.md §4.5) — so when
  stage 3 deletes MARGIN, nothing prices a parked-vs-reseed entry difference. The `enter` card should
  be keyed by entry fact as well as consumer kind, or the design should argue they are equal.

## PROBED-AND-HELD

Compiles used: 4 of the ~40 allowed (trace build: vm1, smp20 default/dfa/vm). Data: R-33 sweep,
5,492 records, 3,489 window sites with a wfE end (two python scripts in premise/py/).
- Code cites unchanged between 34c8ed620 and 884996ef6: `git diff --stat` over memfn/src, src,
  memfn/include is empty (only memfn/docs and lane files changed). HELD.
- Cited locations HOLD in the review tree: finder.c:938 (SF_WINDOW_STOP set in fd_find), window.c
  A-parked :407-420, scan_ok :446-449, a_model_holds :451, a_model_choose :466, mass_domain :529,
  a_mass_choose :543-561; emit_dfa.c `req_run_member` :1058-1076, `pcrec_landmark_margin` :9057,
  `req_landmark_admits` :9064, `next_keys` :7299; findings.c :745, :780; req.c:779-781;
  kset.c:294; lmwalk.c:231 and `LMWALK_K_HIT_UNMEASURED` 10 (:35). B-fn is window.c:1673
  (`b_fn_holds`; the design's :1672 is its comment's last line, off by one: trivial).
- U1 (smp20 two stops) HOLDS on the R-33 data: DEF/OFS A-model -> RESEED stop @1 {/} (fn-memchr);
  RTE/COVER A-mass -> stop @0 {x,X} (E-find, PAIR, fn-pair).
- "inert R8/R3a/R3b/R4/R1/R2" HOLDS by code, not just by census: R3a/R3b/R4 need KN_H, refused at
  finder.c:539; R8's FL_E_G compare returns 0 (finder.c:525-527); R1/R2 need SF_TERMINAL_FAST, set
  only in the residual phase after a V1/W64 terminal (finder.c:714), which only R8/R2 could produce,
  and KN_N rows decline in the terminal phase (finder.c:537). Reach is provably zero; N14's "reach
  census" is not needed to delete them.
- PAIR is reachable only through fd_find (SF_WINDOW_STOP) — HOLDS; in the data every two-member stop
  is PAIR on REPORT (101) and R7w walk elsewhere (279).
- Horspool admission = mass >= HORS_MIN, window >= 2, last >= 0 (window.c:1592-1597) HOLDS; note Table D
  is asked only inside E-find (window.c:1573-1576 header), so the T-FIND Horspool row needs the same
  frame validity as PAIR (covered if the validity column applies to every method).
- N3 `mf_set_terms` has no product caller (only tests/memfn/run_link_checks.sh and old lane
  scratch) HOLDS; N12 vany reachable only through its stand-alone `mf_kernel_find_any` (G2) HOLDS.
- U2: P3's run scan (presence.c:177-183, cube_mass, rightmost-first strict <) and `run_member`
  (window.c:763-781, kit_set_sum, TIE_HIGHER) agree for verify-YES runs (same sum, same tie); HOLDS
  for the pre-check part case the design names. (verify-NO `run_member` considers exact positions
  only; P3 is never asked there.)
- U4's `cube_mass` == `kit_set_sum` over the cube identity HOLDS (both rate and NONE); see
  PREMISE-12 for `window_mass`.
- U9 values agree (4 = 4). R-33's prior numbers HOLD against the rate table a322116b1b87f9f6:
  x 997 + X 100 = 1,097; '/' 4,154; {c,d} 46,603; {",'} 4,569; flat two-member 7,812.
- Card channel: `mf_measures` handed on `mf_art_begin` with `kit.` rows only (memfn_sites.c:75-105)
  HOLDS; DEFAULTS = `idk zen4-grid1@1` HOLDS; finder_check.py check C (card shape + deps) exists
  (tests/memfn/finder_check.py:33-37) HOLDS; scripts/emit_sweep.py exists with --patterns-file for
  bench/588 samples HOLDS.
- The architecture guide permits a priced argmin with an optimizer inside a row
  (docs/dev/guide/architecture.md:21-28) HOLDS.
- D176 Q2 Horspool price form "(probe + rate x verify) / E[sh]" matches the subject's formula; D176
  Q1 "costs relative to the scalar walk" matches the unit. HOLDS.
- The seven scenarios exist as delegated sites: OFS, COVER, PF (DFA kinds and VM_ATTEMPT = the VM
  re-find), PRE, MLINE, LMHIT (src/gen/memfn_sites.def:59-96; find_site emit_dfa.c:6900-6930).
  HOLDS; the SKIP sites (STAY, EDGE, VMSPAN, VMSTRIDE) are outside the "find the span" scope and
  render through compose's arms, not a FIND decider.

## Summary

The shape (candidates -> per-question tables -> pick last) is sound, but several stage-1
"byte-identical" claims do not survive the code: T-FIND has no answer on OFS sites (no consumer kind;
PREMISE-4), precheck's memchr is a presence test that T-FIND would answer with a walk (PREMISE-2),
generic.c via T-CMP can never be byte-identical (PREMISE-3), and the reply growth is a certain
MF_SITE_ABI event (PREMISE-14). The "frame is a fixed fact" holds on the data but not by construction
(PREMISE-1); stage 3 under-counts stamp movers (PREMISE-8) and item 3 lacks a FUNC-frame renderer (PREMISE-13).
