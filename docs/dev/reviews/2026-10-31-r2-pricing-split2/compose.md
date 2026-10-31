# crit-pricing-split2 / compose (opus): does (a′) compose exactly?

Lens: SOUNDNESS/SIMULATE of the composition claim (rev 1 §3.3's accounting rule, §2.5, §3.6 G1/G5
and the hybrid sentence, Q4's S2 row). Subject: the snapshot `../subject_splitstudy_report.md`
(lane/splitstudy c06ac74ef). Review tree `worktrees/crit-pricing-split2` @ a3cc4de82.
Scratch (this dir): `compose_sim.py` + `compose_out.txt` (mine); `sim.py`, `sim_out.txt`,
`probe_r1/` (copied from r1's simulate dir, read only; `probe_r1/p14.c` is r1's emitted
`foo(bar|baz)+`). No compile, no matcher run, no make. No denied file opened. The Read tool was
used on no file under docs/dev/lanes/.

Method for (2): r1's option space (PARKED k0 + RESEED stop x verify subset), r1's prior
(`tests/findings/default_ppm.tsv`) and r1's walk model (`walk_len2`), extended past the window:
a false entry of option o walks `Lin(o) + Ppass(o) x T` bytes, Lin = r1's in-window walk (proven
positions re-walked), Ppass(o) = P(every unproven window position matches | entry), T = the
expected bytes walked beyond the window GIVEN the window passed (swept 0, 1, 2, 4, 8, 16). The
"true" winner is the exhaustive argmin of `kit + entries x 10.7 c/B x walk`. Populations: r1's
115,248 literal windows (Part 3b) and 85,176 unpinnable windows (Part 3c), plus `ereh`.

## Findings

### COMPOSE-1. `beyond(site)` is the wrong term: the beyond-window walk is INVARIANT to the kit's choice, so it belongs with the backend's terms; added per entry as §3.3 writes it, its natural reading mispicks up to 96 % of windows (CONFIRMED, arithmetic + data)

- **Claim tested**: §3.3 "the consumer's expected survival BEYOND the stated window from a false
  start (a derived machine fact in bytes, with an error bound per R4.6) ... `A(plan) =
  per_entry(route) + (rewalk(plan) + beyond(site)) x per_byte(route)`"; Q4 S2 row "‡ beyond-window
  survival (bytes, error bound)" as a new site fact; §3.6 "once pcrec states the beyond-window
  survival as a site fact, no such term was found".
- **The identity.** Per subject byte, option o's beyond-window bytes are `entries(o) x Ppass(o) x
  T`. `entries(o) x Ppass(o)` = P(stop and the verified positions match) x P(the rest match | that)
  = P(the WHOLE window matches here): the same for every plan of the site, by the chain rule
  alone (no independence assumption needed). So the beyond-window walk is a per-byte constant of
  the site, exactly like the match phase, and cancels across the kit's options. The kit needs no
  beyond fact at all; its choice depends only on `rewalk(plan)` inside the window.
- **What the formula as written does.** `beyond(site)` is one number added to every plan's
  per-entry walk, so it is charged `entries(o) x beyond` (plan-dependent through entries).
  `compose_sim.py`, `compose_out.txt`:
  - reading Z (beyond = 0, today's knowledge) and reading U (beyond = the unconditioned
    `prod p_j x T`, "from a false start" literally): **0 mispicks** on both populations at every T.
  - reading C (beyond = T, the survival "beyond the stated window" given the walk got there, the
    natural derived machine fact): 3b: 1.29 % / 8.05 % / 32.8 % / 70.5 % / 96.1 % of windows
    mispicked at T = 1/2/4/8/16, mean regret up to 29.0 %, worst 75.9 % (`leee`); 3c: 0.14 % ...
    94.9 %, mean regret up to 36.5 %, worst 92.4 %. The error always pushes toward DEEPER verify
    plans (fewer entries), e.g. `ereh`-class `reee`: picks stop@2 verify{0,3} over stop@3 verify{0}.
- So the new site fact the SIM-1 fix introduced is a no-op where it is tiny and a mispicker where
  it is stated as the conditional survival; its "error bound per R4.6" and "is it material on
  today's sites" (§3.3 INFERENCE) are questions about a term that should not be in the quote.
- **Answers the brief's "is beyond(site) computable by pcrec, with what error"**: it is computable
  (a continuation-machine walk), but it is not needed; computing it buys nothing for the site's
  choice and costs a new site fact, a measurement row, an error bound and an abi field.
- **Severity** design (a wrong formula in the ruled shape's central section). **Effort** small:
  `A(plan) = per_entry(route, ...) + rewalk(plan) x per_byte(route)`; delete the beyond fact from
  §3.3, Q4 S2 and the §3.6 hybrid sentence; add "the full-window walk past the window" to the
  backend's invariant terms (it is P(window) x T x per_byte per subject byte, a site constant).
  **Blast radius**: §3.3, Q4 S2 row, §3.6 G1 text, §5 R4.6 error-bound obligation, §6 stage 0's
  measurement list. **Introduced by**: the SIM-1 fix (new claim). **Changes the
  RECOMMENDATION?** No; it SIMPLIFIES (a′) (one site fact fewer). It changes the seam rule's
  accounting clause text.

### COMPOSE-2. Presence on/off, which (a′) leaves to the kit, changes the bytes EVERY OTHER SLOT on the path sees, and its value needs a subject-regime fraction the kit does not hold: the accounting rule's "other slots' bytes are invariant" fails at the presence pass (CONFIRMED, emitted code + kit doc)

- **Claim tested**: §3.3 accounting rule ("The backend adds only terms invariant to the kit's choice
  at that site: ... the other slots' bytes"); §2.5 "the kit's per-site choice is invariant to a
  positive scaling of its per-byte terms, so it needs the fraction only if its options differ in
  per-call cost"; §3.3 "KIT ...: the presence fold and presence on/off (P1)"; §3.6 the hybrid
  sentence.
- **The code.** `probe_r1/p14.c` (`foo(bar|baz)+`, r1's probe of main a3cc4de82) `rx_search`:
  `if (subject_length <= search_from || !memchr(subject + search_from, 98, ...)) return 0;` then
  `rx_reqrun` (FIRST, the handoff's landmark run search) then the DFA with `rx_ofsskip` (NEXT).
  The presence pass gates FIRST, NEXT and the match phase: with it ON, a subject without `b` runs
  only the presence pass; with it OFF, the same subject runs FIRST's run search and the DFA over
  the rest. The presence links are stated on the start-search site and decided by the kit
  (`r17b_prime.md:785-789` P0-P4; P1 `priced` "argmin {verify = 1, verify = 0} by expected cost").
- **Why it breaks the rule.** The presence choice is not a positive scaling of the site's per-byte
  terms: its saving is `P(absent) x (the path's downstream per-byte cost: FIRST + NEXT + match
  phase)`, i.e. the backend's terms times an outcome probability §2.5 itself assigns to the
  backend ("Under (a′) the backend owns the cross-path fractions"). The kit's own measured input
  shows the shape: M23 `kit.gate.byte1.DFA_SCAN.early/late/absent = +8.1 / 0 / -247,000 u·B`
  (`r17b_prime.md:2011`): one route-keyed number per POSITION class, whose weights are the
  subject regime's, and whose `absent` value is a whole-artifact downstream cost measured on ONE
  path shape (it differs between a handoff path and a cover path).
- The study already says so in another place: §1.4 item 1 "PRESENCE ... is a per-path term whose
  value the kit supplies". A per-path term priced by the kit means the kit's quote depends on the
  path (its downstream cost and the regime's P(absent)), which is not "one quote per site" (§3.6
  G5) and is a term the kit cannot compute from per-route consumer rows.
- **The two exact shapes.** (i) The kit returns its best with presence ON and its best with
  presence OFF (a two-member frontier on one property), the backend adds the path's downstream
  bytes x P(present) and takes the min: the hybrid of §3.6, NOT reduced to (a′). (ii) The backend
  states, per path, P(absent) and the downstream per-byte price as site data: pcrec's path price
  crosses into the kit, beyond Q-WR-9's "per-route MEASURED constant" (a new ruling scope). (i)
  keeps D157 and add. 6's spirit; it is one bit, not (d)'s 204 options.
- **Severity** design. **Effort** small to state, medium to build (the quote grows one property).
  **Blast radius**: §3.3's accounting rule, §2.5's invariance sentence, §3.6 G1/G5 and the hybrid
  sentence, §3.8's general-form paragraph ("a frontier is needed only for a property the child
  cannot price (size, U1/U2)": presence is one now). **Introduced by**: the SIM-5 fix's §2.5
  invariance sentence and the new §3.3 rule (new claim). **Changes the RECOMMENDATION?** Not (a′)
  over (d) ((d) has the same dependence and more), but it falsifies "(a′) composes exactly" as
  stated and the §3.6 claim that the hybrid reduces to (a′).

### COMPOSE-3. RECOVER `landing`'s validity reads the kit's `exists`, so the kit's NONE row (new under (a′)) changes the backend's per-match RECOVER cost; "no search" also has two homes (CONFIRMED, code)

- **Claim tested**: §3.3 "KIT ...: whether to scan at all (a NONE row)"; "The backend adds only
  terms invariant to the kit's choice at that site: ... RECOVER and FINISH per match"; §3.3/§8
  D176 Q1 row "'no search' is a priced row: the kit's NONE row inside a site, and the backend's
  no-site path across paths"; S1 (one decider per choice).
- **The code.** `src/gen/emit_dfa.c:9666-9683`, `start_landing_applies` (RECOVER S3 `landing`):
  `cand_ask(cx, CAND_SLOT_RECOVER, CAND_ROUTE_DFA, &fd, &cs); ... return cs.cls.exists != 0;` and
  its header (`:9655-9659`) "L4 the NEXT row selected for the forward machine HAS a block to record
  in (`next-none` has none)". `memfn/include/memfn.h:1088-1090`: `exists` "0 for a form that
  searches nothing (NONE)". `memfn/src/compose.c:309`: "every row today writes a search text
  (exists 1: NONE is not built". So today the landing row's `exists` read is constant 1 on a kit
  site; the moment the kit's NONE row exists and is picked, `landing` is invalid and RECOVER falls
  to `reverse-pass`, a reverse walk per match instead of a stored position.
- **Consequence.** The kit's NONE-vs-scan choice changes a backend per-match term (RECOVER's row
  and cost) by `match density x (reverse-pass - landing)`, a quantity the kit does not hold (match
  density and RECOVER's price are the backend's). MODELLED illustration (no timing): a site where
  NONE beats the best scan by 0.1 c/B, at 1 % match density and an 8-byte match, loses 0.86 c/B
  of reverse walk (8 x 10.7 x 0.01): the local pick is the global loser.
- **The two homes.** The study places "no search" in the kit (NONE row in a site) AND in the
  backend (the no-site path, e.g. `next-none`, `emit_dfa.c:10424`). Two deciders for one choice is
  the S1 failure the study scores (d) down for; here it is also exactly where composition breaks.
- **Fix** (either): (i) "no search" is the backend's path only (the no-site path, priced with the
  route's no-search card); the kit's site quote never includes NONE, so `exists` is 1 on every
  quoted site, as today; or (ii) the ask states `exists` required as a constraint and the kit
  quotes per constraint (a one-bit frontier, the COMPOSE-2 shape). (i) is the simplification: one
  home, no new property.
- **Severity** design. **Effort** small. **Blast radius**: §3.3 KIT bullet, §8 D161 add. 14 and
  D176 Q1 rows' texts (the addendum text Frank would rule), Q4 S2 ("ONE pick (its NONE row
  included)"). **Introduced by**: rev 1's NONE wording (the D176 addendum reading; new claim).
  **Changes the RECOMMENDATION?** The seam rule's kit-role clause, not (a′) over (d).

### COMPOSE-4. RETRY (home P) reads the kit's candidate density, and the VM consumer's per-entry cost depends on the RETRY row; route-keyed consumer cards cannot carry that, so the separable min is exact only with one quote per (site, consumer key) (CONFIRMED, code; the exactness argument is arithmetic)

- **Claim tested**: §3.3 "per route, (i) ... (ii) its fixed cost per entry. These two cards per
  route are ALL the consumer data the kit reads"; the accounting rule; §3.6 G5 "one quote per site";
  §1.4 item 4 (R4, home P) and §3.8 unlock 3 ("Multi-site joint pricing (start x reseed, C16) ...
  Trigger: R4's population mispicking after RETRY is priced").
- **The code.** RETRY's `adaptive-dense` (`emit_dfa.c:10087-10088`):
  `pcrec_dfa_cand_ppm(s->cx) * s->vm->reseed_gap > 1000000ull`, where `pcrec_dfa_cand_ppm`
  (`:8430-8456`) is the prior's mass over the kit class's `proven0`: the kit's PICK. The RETRY rows
  (`:10450-10476`) run different per-candidate VM work (`adaptive-dense` "starts inside a capped
  step block that is armed"; `exact`/`clamped`/`anchored` today's retry). So on the VM route (the
  hybrid), per_entry is per_entry(route, RETRY row), and RETRY's row reads the kit's output.
- **The exact form.** For a path p, the kit's best given that path's consumer data c(p) is
  `min_o [K(o) + entries(o) x A(o; c(p))]`; the total `min_p [B(p) + that]` IS exact (it is a plain
  min over (p, o) with B independent of o), provided (1) each path hands the kit its OWN consumer
  key (route AND the RETRY row, later RECOVER/FINISH where they bear on entries), and (2) no P-row's
  VALIDITY reads o (R4 does today; under pricing it must become a price term, which it does once
  RETRY is priced). So C16 needs no "multi-site joint pricing" machinery and no unlock: it is exact
  under (a′) with path-keyed consumer cards and one ask per distinct key. That is a
  simplification of §3.8 unlock 3, but it contradicts "two cards per route are ALL" and "one quote
  per site".
- **Severity** design (exactness claim and data shape) / doc. **Effort** small to restate.
  **Blast radius**: §3.3 "what crosses", §3.6 G5, §3.8 item 3, §6 stage 0's "two consumer cards per
  route". **Introduced by**: the SIM-1 fix (A(plan) with per-route cards; new claim). **Changes the
  RECOMMENDATION?** No; it sharpens it (unlock 3 dissolves into the composition).

### COMPOSE-5. "The true min" holds only relative to the kit's declared rule: MARGIN 2/1 (kept, §3.5) makes the site quote the price of the guarded pick, not of the site's minimum (CONFIRMED, data)

- **Claim tested**: §3.3 "min over paths of [backend terms + min over kit options]"; §3.6 G1
  "exact composition given the kit's data"; §3.5 "MARGIN ... stays the kit's".
- **Data** (`compose_out.txt`, key M): with the true A(plan), MARGIN after the plain argmin picks
  a costlier option on 612-617 of 85,176 unpinnable windows (0.72 %, mean regret 0.57 %) and on
  129-131 of 115,248 literal windows (0.11 %, mean 0.10 %), worst ~2x (by construction: PARKED is
  kept until RESEED is modelled under half).
- Nothing is inconsistent in the quote (it prices what the kit will render); but the G1 cell should
  read "exact up to the kit's declared guards (MARGIN)", and the §3.5 measurement row is where that
  regret gets bought back or justified.
- **Severity** doc. **Effort** none. **Introduced by**: new claim (§3.3 wording). **Changes the
  RECOMMENDATION?** No.

### COMPOSE-6. A(plan) omits the displaced scan; immaterial (CONFIRMED, code + data)

- The emitted loop resumes the scan where the walk fell back: `probe_r1/p14.c` `rx_search`,
  `if (forward_state == 0 && ...) { size_t cand = rx_ofsskip(subject, subject_length,
  scan_position); ...}`, after the DFA advanced `scan_position` over the walked bytes. So a walked
  byte is not scanned: per walked byte the net is per_byte(route) minus the option's own scan price.
  `compose_out.txt` key D: 24 of 115,248 and 4 of 85,176 windows pick differently, worst 0.09 %.
- **Severity** doc. **Effort** none (label it a dropped second-order term). **Changes**: nothing.

### COMPOSE-7. §3.6 G5 ("one quote per site") rests on the composition claim; with COMPOSE-2 to -4 it is one quote per (site, consumer key, presence bit [, exists bit]) (SUSPECTED speed, CONFIRMED doc)

- Count: r1 put the raw path space at 6,720 tuples before route and validity (simulate.md
  PROBED-AND-HELD); each path carries 1-2 kit sites; the distinct consumer keys per site are the
  route x RETRY rows (<= 4 on the VM route) and the presence bit (2). So <= ~8 quotes per site
  against (d)'s up to 204 options; the G5 ranking (a′) > (d) HOLDS, but the cell's text is wrong and
  the absolute compile-time cost (each quote is an `mf_ask`-style kit call over Table A) is not
  measured against the 1 % bar. Confirm: count `mf_ask` calls under a prototype on the census set.
- **Severity** doc (speed SUSPECTED). **Changes the RECOMMENDATION?** No.

### The two standing questions

- **Sibling of an existing family?** Yes, two, and neither is the one the study names. (1) The
  per-site quote is the sibling of the kit's existing define-time QUERY `mf_ask` and its form
  CLASS (`r17b_prime.md` §4.5, PR-9; `emit_dfa.c:8396-8400` "THE READERS' QUERY ... pure, asked of
  the compile's own art, before the selection that reads it"): pcrec already asks the kit a pure
  per-site question before its own selection, and the readers are declared (`cand_nodes[].kask` /
  `.kfields`, `emit_dfa.c:9880-9890`: EXISTS, PROVEN0, PROVEN_PREV, LIBC_FREE, INCLUDES). The quote
  is that class plus price components; it should be ONE query, not a second channel. (2) The
  consumer cards are siblings of the route-keyed consumer quantities the kit already reads, M22
  `kit.gnone` and M23 `kit.gate.*.DFA_SCAN.*` (`r17b_prime.md:1945`, `:2011`). D176's
  `plan_cost.def` is the kit's OWN constants table (the cards replace `C_ENTER` there), and SRS's
  A-mass is the within-site cancellation domain; COMPOSE-1's identity is another member of that
  cancellation family (any term proportional to P(the whole window passes) cancels across a
  site's options, as the A-mass consumer terms do).
- **General form + unlocks.** The general form is the nested argmin with INTERESTING PROPERTIES
  (System R's "interesting orders"): the child (the kit's site) returns, per value of each property
  a parent row READS, its best option with price components; the parent hands the child the data
  that varies with the parent's choice (its consumer key). Composition is exact iff (a) every
  parent term that varies with the child's choice reads only a declared property, and (b) every
  child term that varies with the parent's choice is a declared input. The tree already DECLARES
  the candidate property list: `kfields` (EXISTS, PROVEN0, PROVEN_PREV, ...) is exactly the set of
  kit outputs pcrec rows read, so the exactness check is mechanical. Unlocks:
  1. A self-check "a priced slot that reads a `kfields` field of a kit site on its OWN path either
     keys the quote by that field or proves it invariant" (the trace build already traps undeclared
     asks, `emit_dfa.c:9880-9890`). Trigger: the first priced slot that reads a kit field
     (RECOVER `landing` EXISTS, RETRY R4 PROVEN0, FIRST's K admission PROVEN0).
  2. Path-keyed consumer cards (route x RETRY row), which retire unlock 3 (C16). Trigger: RETRY
     priced ([START-DENSE]).
  3. The presence bit as the first quote property (COMPOSE-2). Trigger: P1 built (Q-R17P-28's
     re-ask, "a measured-bundle workload exists").
  4. Size (U1/U2) as the next property, the study's own case. Trigger as §3.8.

## PROBED-AND-HELD

- **(a′) recovers the true winner on SIM-1's data** (`compose_out.txt`): on `ereh` the true best
  is RESEED stop@3 verify{0} (28.629 at T = 0, 28.726 at T = 8) and (a′) with `rewalk(plan)` picks
  it; on all 115,248 literal and 85,176 unpinnable windows, at all six T values, (a′) without the
  beyond term (reading Z) and with reading U pick the true winner: 0 mispicks of 1,202,544
  (window, T) cases. The SIM-1 fix HOLDS once COMPOSE-1's term is dropped.
- **rewalk(plan) is computable by the kit from what it holds today**: the walk needs the spans'
  per-position sets, the prior's masses (the kit's frequency kind) and the plan's proven positions,
  all kit-side; no pcrec fact is needed beyond the spans already stated.
- **The kit's C-model GREEDY with A(plan) equals the exhaustive best** on every window of both
  populations at every T (key G: 0 mispicks): the greedy shape (`window.c:494-497`, `if (nc >=
  cost) continue;`) survives the plan-dependent per-entry cost; no search change is needed.
- **Match density / landmark density another slot sees**: the kit's choice changes neither (the
  matches are the subject's; FIRST's landmark is pcrec's run search). The per-byte scaling of a
  NEXT site by FIRST's fraction leaves the kit's argmin unchanged (§2.5's invariance holds for
  everything except the presence pass, COMPOSE-2).
- **FIRST's K admission** (`req_landmark_admits`, `emit_dfa.c:9016-9025`) reads the kit's pick of
  the OTHER path (the `-fno-req-handoff` path's start set, `req_start_set` :8978-8994): under a path
  argmin this read dissolves into comparing the two paths' totals, each with its own quote.
  Separable: HELD.
- **PARKED vs RESEED per-entry overhead**: both enter the same emitted loop (`probe_r1/p14.c`
  rx_search; the stop scan returns a position, the DFA steps from it); the difference is the
  re-walk, which A(plan) carries. No separate per-kind card needed on today's form: HELD
  (SUSPECTED only for forms not in the probe).
- **The match phase and FINISH per match**: invariant to the kit's choice at the site (the
  matches are the same for every option): HELD (r1's check, re-confirmed by the identity in
  COMPOSE-1, which puts the beyond-window walk in the same class).
- **Cites checked** (review tree): `window.c:494-497` (C-model acceptance), `:636-648`
  (`wf_arows[]`), `:708-711` (MARGIN basis), `emit_dfa.c:11828` (`CandPath`), `:11946`
  (`members = needs & built`), `:10087` (R4), `:9016-9025`, `:10424` (`next-none`),
  `r17b_prime.md:787`, `:1945`, `:2011` (P1, M22/M23): all match.
- Counts: claims checked 10 (accounting rule; beyond term; rewalk computability; greedy; §2.5
  invariance; match/landmark density; RECOVER; RETRY/C16; FIRST K admission; G1/G5 cells); windows
  simulated 200,424 x 6 T values; code sites read 9; compiles 0; matcher runs 0.

## STATE AT HANDOFF

- STATE: complete
- OWED: none
- Artifacts: `compose_sim.py`, `compose_out.txt` (this dir); copies `sim.py`, `sim_out.txt`,
  `probe_r1/` from r1's simulate dir.
