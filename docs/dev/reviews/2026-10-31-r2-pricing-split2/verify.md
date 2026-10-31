# verify (sonnet), critic round pricing-split2

## Findings

### FIXIND-4 + COMPOSE-3 (RECOVER `landing` reads the kit's `exists`)
Quoted in the review tree: emit_dfa.c:9662-9683 `start_landing_applies` calls `cand_ask(cx, CAND_SLOT_RECOVER, CAND_ROUTE_DFA, ...)`
and `return cs.cls.exists != 0;` (header: "L4 the NEXT row selected ... HAS a block to record in (`next-none` has none)");
memfn.h:1088-1090 "exists: 0 for a form that searches nothing (NONE)"; compose.c:309 "every row today writes a search text
(exists 1: NONE is not built, F0 lands at B5)"; `reverse-pass` is `cand_always`, `.needs CAND_MR` (emit_dfa.c:~10561). Subject §3.3
(snapshot l.473-481): "The backend adds only terms invariant to the kit's choice at that site: the match phase, RECOVER and FINISH
per match". Probes (3 compiles): `x[0-9]*` PREFILTER "memchr"/START "landing"; `qz*` "memchr"/"landing"; `[QXZ]\w*` "byte-class"/"landing"
(all match the critics' stamps). The chain follows: a kit NONE pick makes `exists` 0, `landing` invalid, RECOVER falls to
`reverse-pass`; so RECOVER's per-match term is not invariant to the kit's pick. COMPOSE-3's second point (two homes for "no search":
kit NONE row and backend no-site path `next-none`) is supported by the same text. Caveat: NONE is unbuilt, so today it is latent, as
both critics say; the "exact composition" claim as written is false.
Verdict: HOLDS

### FIXIND-5 + COMPOSE-1 (beyond-window walk invariant to the kit's plan)
Subject §3.3 (snapshot l.465-471): "`A(plan) = per_entry(route) + (rewalk(plan) + beyond(site)) x per_byte(route)`", beyond =
"the consumer's expected survival BEYOND the stated window from a false start". The chain-rule identity is correct on its face:
entries(o) x P(rest of window passes | entry) = P(whole window matches here), which every plan shares (each plan's checks are necessary
conditions), so the true beyond-window consumer work is plan-invariant (a backend-class term by the subject's own accounting rule).
Re-ran fixind/beyond.py (python3 -I, review-tree default_ppm.tsv): `true` column is the constant 243.427 for all four `ereh` plans;
the "rev1" column ranges 849,751 / 863,982 / 71,579 / 243 (reproduced exactly). Re-ran compose_sim.py (28 s, output byte-identical to
compose_out.txt): reading Z (beyond=0) and reading U (unconditioned prod p x T) give 0 mispicks at every T; reading C (beyond=T) at T=2
mispicks 5,685 of 85,176 unpinnable windows (6.67 %, mean regret 1.17 %) and at T=8 59,209 (69.5 %, mean regret 23.7 %). Caveats: (1) both
scripts use the r1 independence model with truth defined by that same model, so they show the formula is inconsistent with the chain rule,
not a measured regret; (2) the mispick rates apply to reading C. The subject's wording ("from a false start", "error bound") is
ambiguous between U (harmless, near zero) and C (mispicks), so "its natural reading mispicks up to 96 %" is a reading choice; the
substantive claim (the term is plan-invariant, needs no kit input, and a per-entry charge of it is wrong) follows.
Verdict: HOLDS (identity and reproduction); the mispick magnitudes are conditional on reading C.

### COMPOSE-2 (presence on/off changes other slots' bytes)
Quoted: probe_r1/p14.c:118-124 `rx_search`: `if (... !memchr(subject + search_from, 98, ...)) return 0;` precedes `rx_reqrun` (FIRST)
and the DFA with NEXT, so with presence ON a subject lacking the byte runs only the presence pass; OFF it runs FIRST + NEXT + match.
r17b_prime.md P1 row (l.785): "argmin {verify = 1, verify = 0} by expected cost", MEASURED, routed at B5, NOT BUILT (Q-R17P-28); M23 row
(l.2011): `kit.gate.byte1.DFA_SCAN.early/late/absent = +8.1 / 0 / -247,000 u.B`. Subject §2.5 (l.409-416): "the kit's per-site choice is invariant to a
positive scaling of its per-byte terms"; §3.3 accounting rule: "other slots' bytes" are backend terms; §1.4 item 1 (l.233) itself calls presence
"a per-path term whose value the kit supplies", and the T3 row (l.205) says "presence VALUE needs B". The presence saving is
P(absent) x (downstream path cost), not a scaling of the site's own per-byte terms, so the "invariant other-slot bytes" sentence fails at
this one choice and "one quote per site" cannot cover it without a presence-keyed quote or a path-supplied downstream price. The claim that the kit
cannot price it from per-route consumer cards follows for any route whose downstream differs from the one M23 was measured on. Caveat:
M23 already gives the kit a route-keyed measured number for DFA_SCAN, so today it is priceable on that one shape; the finding is about the
composition claim, not an impossibility.
Verdict: HOLDS

### RULING-1 (`cover` vs composite is one D172 request; backend homing splits an axis)
Quoted D172 (decisions.md:9891): "Find-window and REPORT are the SAME request (REPORT = verify everything; the kit fast-finds a stop, then
verifies)". known.c:470-496 (`cover_window`/`pcrec_cover_site`): spans stated with `MF_ENTRY_NONE`, every span `MF_VERIFY_YES`,
`s->site_kind = MF_SK_REPORT`. memfn.h:541-542 `mf_entry { UNSTATED, NONE, PARKED, RESEED }`. Subject §2.4 (l.377-379): cover is "one kit
find-then-verify loop with no forward DFA, no reverse pass, no match phase"; S3 row (l.627) "none" backend adds. The quotes and cites are
accurate. What does not follow: the study treats S2 (engine verifies: consumer = DFA/VM candidate entry) and S3 (REPORT: no engine
consumer) as different path families with different site kinds; whether a site's consumer is an engine at all is a pcrec fact (cover's
C3-C12 conjuncts), not a depth setting the kit can choose without being told it may skip the consumer. D172 says the REQUEST is shared, not that
the engine-or-not choice moves to the kit. Cover's spans (match core plus context sides) are also not necessarily the composite PF's spans.
The accounting-rule point (match phase varies with the pick) is true only if the KIT picks cover; as written the backend does, so the rule
is not violated. The critic's alternative (home `cover` in the kit with an explicit "consumer may be skipped" fact) is a coherent design option
and a forest-for-trees observation, not a defect in the study as written; "stage 1 violates the draft" (pcrec compares two kit quotes) is
true literally against the draft wording "pcrec compares no two kit forms" only if a REPORT quote counts as a "form"; judgement.
Verdict: PARTLY (facts and cites hold; "splits one axis / accounting rule fails" is conditional on a design choice the study did not make)

### RULING-4 (no-search has two homes; S0 vs today's no-search artifacts carry a kit presence site)
Subject: l.488-489 and l.911 (D176 Q1 draft) "'no search' is a priced row: the kit's NONE row inside a site, and the backend's no-site path across
paths"; l.626 S0 row "no site on the path ... kit hands back -"; l.908 marks D161 add. 14 "AFFIRMED, no change" for (a′) while charging (d)
"REVERSED in part: scan-or-not across footprints becomes the backend's". D161 add. 14 (decisions.md:9511-9513): the kit's table "decides the form,
including NOT pre-scanning at all". Probe (1 compile) `(?s).+x\d`: `RX_DFA_PREFILTER "none"` AND `RX_REQ_BYTE "120"`, `RX_REQ_WHY "emitted"`, body
l.82 `!memchr(subject + search_from, 120, ...)`, `RX_MEMFN_LIBC "memchr"`: today's no-search artifact does carry a kit presence site, so the S0
row ("no site on the path"; PRESENCE only "in S2's pick", l.631) does not describe it. emit_dfa.c:1476 `need = ... MF_SK_VM_ATTEMPT ? MF_REQUIRED :
MF_OPTIONAL` confirmed (VM attempt presence REQUIRED). r17b_prime.md:270: F0 NONE is NOT BUILT, M22 `kit.gnone` = -1 (never wins) on three consumer
kinds. The two-homes point and the add. 14 partial-reversal charge follow from the study's own two statements (l.488 vs l.908 vs l.911).
Verdict: HOLDS

### FIXIND-1 + FIXIND-3 + RULING-8 (clause 8 vs CG_FIXED, classification, three wordings, D158 draft vs D158, kit give-up fact)
Quoted: emit_dfa.c:9823-9832 "CG_FIXED ... the row must never move the VM's give-up surface ... Its control is behavioural ([GIVEUP-DIFF]) ...
never a comparison of two columns" and enum {CG_ANY, CG_FIXED} (a single bit); :5677-5681 "The give-up CLASSIFICATION (neutral / one-way) is derived by
an instrument over the corpus, never declared here"; locate_finish.md:446-466 §1.5 ("Classification (derived, never declared) ... computed by an
INSTRUMENT over the corpus ... nothing in `src/` declares it"; reasons (a) not a function of the pair, (c) CG_FIXED a ruled contract; "NEUTRAL <
ONE_WAY < forbidden" is a join over artifact classes per (row, route) cell, relative to the deny arm). Subject: §5.5 l.734-737 "no larger than the
slot's least (equivalently: the set may move a pick only in the ONE_WAY direction ...)" + "`CG_FIXED` is declared per row; the filter needs it per
path (the union)"; l.739 / l.906 D158 draft "never moves the give-up surface"; l.965-966 clause 8 "no larger than the slot's least; a set revision never
moves the give-up surface". The three wordings are not equivalent ("no larger than the least" = no move; "ONE_WAY only" permits a give-up to
become an answer; "never moves" forbids). D158 (decisions.md:9393): "An optimization may turn a give-up into an answer (ONE_WAY)"; Q-WR-3
(:9524): "a give-up may become an answer ... relaxes at ST4 per measured cell"; the D158 row in §8 (l.906) has no Q-WR-3 companion. A union of
CG_FIXED bits yields one bit and orders nothing, and the classification that orders surfaces is by design not in src/: HOLDS. The "slot's least" being
undefined for incomparable surfaces follows from the join being per-cell/per-artifact-class. Sub-claim FIXIND-3 "the kit holds no give-up fact for a
window site": memfn.h:531-536 does say a window site states no `need` (pred-level), but window spans carry `core`/REQUIRED-ness (D176 Q4, mf_core) and
subject §1.4 item 1(b) already notes REQUIRED vs OPTIONAL for presence, so "nothing to obey the rule with" is overstated; the gap is for the
consumer-scan choice (crossing 9 `first-class` VM, a row the study marks ONE_WAY/F5 in the allowance manifest) and that part holds.
Verdict: HOLDS (FIXIND-1, RULING-8, the stricter-than-D158 point); PARTLY for FIXIND-3's "kit has no give-up fact".

### FIXIND-2 (clause 8 cannot fire at LOCATE; on VM routes it forces picks)
Quoted: emit_dfa.c:10186-10187 `rev-end` `.routes = CR_DFA`; :10208 `cover` `.routes = CR_DFA`; locate_finish.md:455 (e) "on DFA finisher routes no VM
runs, so posture is N/A, not NEUTRAL". Subject l.843 stage 3 gate: "clause 8's give-up filter in the census" for LOCATE `cover`/composite. So the
filter has nothing to check at the first priced slot: follows. run_axes.sh:1019-1043 (GROUP F4: "the VM attempt loop's rows skip attempts before the whole
run's hit less K, so a deny-arm GIVE-UP may become the handoff's answer"; "EMPTY by construction ON THE DFA-SCAN ROUTES"), GROUP F5 (`first-class`, the VM hat).
locate_finish.md:515-518: "RETRY `adaptive*` ONE_WAY, `exact`/`clamped`/`retry-anchored`/`fixed` NEUTRAL". emit_dfa.c:10482-10492: `adaptive` is `cand_always`
(deny `PCREC_NO_HYB_RESEED`), `fixed` is `cand_always` "(fallback, the deny's landing row)". With a ONE_WAY row's surface smaller than its NEUTRAL deny-landing
successor's, "no larger than the slot's least" removes `fixed` wherever `adaptive` is valid: forced, not priced; `fixed` reachable only when `adaptive` is
denied. Count of 8 and 26 allowance keys not re-counted (not needed for the argument). Consequence stated by the critic (no shipped pick moves; P labels in §1.2 /
Q4's RETRY row promise choices clause 8 removes) follows.
Verdict: HOLDS

### RULING-2 + RULING-3 ("no clause reversed"; D146 K0 supersession; PR R2.3; add. 11 has no §8 row; Q-WR-9 scope)
Quoted: D146 (decisions.md:8995) "pcrec does no cost comparison ... This supersedes integration.md rev 2's K0 price query and its cross-project cost
units"; integration.md:174-175 "Revision 2's K0 capability-and-price query (§7) is SUPERSEDED: no price crosses the boundary, and pcrec does no cost
comparison"; PR.md (kit draft) R2.3 "THE SPLIT (ruled 2026-10-31)": the KIT "never receives engine costs (D161 add. 6, D157 stand)", under a HOLD note
that R2.3/R2.4 are HELD pending this study. Subject l.567 (S2 cell, (a′)): "no clause reversed"; l.902 D146 first half row: "ADDENDUM (new direction, Frank
2026-10-31, NOT a fired Revisit-when)"; l.1018-1019 open point 16 files "R2.3's 'never receives engine costs' contradicts (a′)" as a relay to the kit "on PR".
(a′) has a pcrec backend comparing priced paths with kit quotes and the kit reading pcrec-supplied consumer rows: a price crosses the boundary both
ways, which D146's operative sentence and integration.md rev 3 exclude by name. The S2 cell's "no clause reversed" therefore contradicts the study's
own D146 row ("new direction"); RULING-2 HOLDS (the HOLD note softens the PR R2.3 half: it is held, not in force; filing it as a PR defect rather than an
owner-held item is a framing fault but minor). RULING-3: D161 add. 11 (decisions.md:9498) ruled "the only pcrec-side quantity is a MEASURED per-candidate
fixed cost per route ... FILED, not built: trigger = a TUG cell measured losing for want of it"; (a′) adds a per-byte card and site facts; the subject's §8
table has no add. 11 row (rows: D146 x2, D147, D152, D158, D161 add. 6, add. 14, D166, D172, D176 Q1, Q4, Q-WR-9, D157, D153/D77): confirmed absent.
Q-WR-9 (:9526ff) "pricing the pre-scan ... If it fires, the consumer's cost enters as a per-route MEASURED constant ... add. 6 gets a dated addendum". But
the study itself says "pre-authorized, WIDENED in scope beyond the pre-scan (a new scope Frank rules)" (l.567) and "titled 'pricing the pre-scan', so this
is an extension" (l.486), so "overstates" is only partly right: the widening is disclosed; the missing add. 11 row and "the ruled shape" label remain.
Verdict: RULING-2 HOLDS; RULING-3 PARTLY (add. 11 row absence holds; "overstates the authorization" is softened by the study's own disclosure)

### RULING-12 (consumer cards per route vs six consumer kinds; five homes for consumer cost data)
memfn.h:414-415 confirmed: `mf_site_kind { UNSTATED, DFA_SCAN, DFA_HAT, HYB_PF, VM_ATTEMPT, DFA_ATTEMPT, REPORT }` (six kinds). measure_store/zen4-grid1/1/set.tsv
keys are by consumer kind (counted: `kit.gstar.*` rows for both DFA_SCAN and DFA_HAT, `kit.beta.*.DFA_SCAN`, `kit.wuse...DFA_SCAN`, `kit.ccold...DFA_SCAN`). plan_cost.def:38-41
`C_ENTER 2000`, "10.7 c/B times an ASSUMED ~2 bytes", basis "MEASURED x ASSUMED" (confirmed; also feeds FIXIND-5's illustrative T). M23 (r17b_prime.md:2011) and
D161 add. 11's per-candidate fixed cost (decisions.md:9498, FILED not built) confirmed. Subject l.461-463 keys its two cards "per route" (and Q-WR-9's own text says
"per-route MEASURED constant"), so the route-vs-kind mismatch is real: DFA_SCAN and DFA_HAT are distinct kit keys under one DFA route; HYB_PF is a pair. The "five
homes" count includes one filed-not-built constant (add. 11) and the (a′) cards that the study says REPLACE `C_ENTER` (Q1 draft), so the number is partly rhetorical; the
substantive unification advice (one section keyed by consumer kind, one owner, D166 add. 2 staleness) stands as a design suggestion.
Verdict: PARTLY (key mismatch HOLDS; "five homes" overcounts planned/unbuilt items)

### COMPOSE-4 (RETRY adaptive-dense reads the kit's pick; per-entry cost depends on the RETRY row)
Quoted: emit_dfa.c:10086-10087 `cand_rs_dense_applies`: `pcrec_dfa_cand_ppm(s->cx) * s->vm->reseed_gap > 1000000ull`; :8430-8456 `dfa_cand_ppm_of` reads
`cs.cls.exists` and `cs.cls.proven0` (the kit's class: the PICK) and returns 1000000 when `!cs.cls.exists`; header: "Its one reader is RETRY's
`adaptive-dense` row (R4)". So a RETRY row's VALIDITY reads the kit's pick (confirmed; a second reader of `exists`, besides COMPOSE-3's RECOVER). Row descs
(:10478-10492): `adaptive-dense` "starting inside an armed step block", `adaptive` "short step probation, then re-seed", `fixed` "today's retry": the VM
consumer's per-entry behaviour differs by row. Subject §3.3 (l.461-463) "These two cards per route are ALL the consumer data the kit reads". The arithmetic
(a min over (path, kit option) with each path handing its own consumer key is exact, so unlock 3 / C16 joint pricing dissolves) is sound. What is not shown: that the
per-entry COST really differs by RETRY row in magnitude (no measurement; row descriptions only), so "two cards per route are ALL" being false is argued, not
measured; and the study itself already lists RETRY as home P with the [START-DENSE] trigger and marks the kit's pick read as a validity read to become a price
(R4 X). The code read is solid; the magnitude is INFERENCE.
Verdict: PARTLY (code dependence and exactness argument HOLD; materiality of a RETRY-keyed per-entry difference unmeasured)

### FIXIND-6 + RULING-10 ("expected bytes seen" path-dependent; fills D162's reserved slot without a measured case)
Subject §2.5 (l.403-416): the presence pass runs first, "NEXT's per-byte price applies only to bytes after the first landmark; a subject without the presence byte
runs only the presence pass", and "pcrec states the site's expected bytes as a site fact ... (**INFERENCE** that per-call differences matter on today's forms)"; Q4
S2 row (l.626) lists it and the beyond-window survival as ‡ site facts with no trigger; §3.6 G5 "one quote per site". Own example shows a site's expected bytes depend on
which PATH (FIRST handoff, presence on/off) is hypothesized, so a kit quote asked per site cannot hold one number for it; asking per (site, path) multiplies asks:
follows. D162 ruling 1 (decisions.md:9532): "Distributions only: the kit derives per-site answers ... A per-site slot is RESERVED, filled only when a measured case needs
a fact the kit cannot derive (match density the likely first)". Both facts are tagged INFERENCE (l.416, l.469) i.e. no measured case; l.593 names the reserved slot with a
trigger only for the separate per-artifact consumer cost item. D162 has no row in §8 (confirmed by reading the §8 table above). Who computes the estimate is unstated.
Verdict: HOLDS

### FIXIND-12 + RULING-13 S3 cell ("no reply-shape event" vs mf_wreply fields and §7 row 5)
Quoted: subject Summary l.82 "no reply-shape event"; §3.6 row 8 l.570 "no reply-shape event; `C_ENTER` becomes set rows ..."; §7 row 5 under (a′) (l.876): "kit reply: `mf_wreply` (`memfn.h:1435`), MF_SITE_ABI 20 ...
small-medium: price components + set id on the existing pick (R7.1 already wants ranking as data)", trigger "the D176 build". memfn.h:1420-1435 `mf_wreply` has
alt, reseed, has_stop, stop, stop_set, nplan, plan, plan_term, pinned, run_*, path: no price, set id or ranking field. Adding them changes the reply's shape (an
MF_SITE_ABI-bearing change, which row 5/row 3 themselves cost). The study's "no reply-shape event" can only mean "no frontier-sized reply"; stated literally it contradicts its own
row 5. Smaller than (d)'s event, so S3's ordering survives, as the critics say.
Verdict: HOLDS

### FIXIND-7 (form-dropping rungs drop-premul etc. move prices; compile.c:1342-1376)
Quoted: subject clause 7 (l.962-964) speaks only of "A rung that drops a strategy family ... RE-RUNS the path argmin"; clause 1/3 (l.951) let prices read "the backend's table form and frame
discipline"; compile.c:1342-1376 rungs `drop-anchored`, `drop-premul` (note: "slower per-byte scan dispatch, measured ~1.27x on scan-bound subjects"), and `drop-end-mark`,
`prefilter-collapse` change backend FORM facts, not a strategy family. A retry after `drop-premul` raising the per-byte price and moving a LOCATE pick (e.g. cover vs composite)
is therefore unaddressed by clause 7: gap confirmed. `fit_seq_legal[]` exists (compile.c:1794-1815, pairwise legal transitions) so the possibility of a re-run sequence outside it is
coherent, but I did not construct one (needs a prototype argmin): that sub-claim is SUSPECTED only.
Verdict: HOLDS for the clause-7 gap and the price movement; the `fit_seq_legal[]` trip is NOT VERIFIED (no prototype)

### RULING-7 (req_dominated_applies: a backend presence dominance on LOCATE-whole paths)
Quoted: emit_dfa.c:8576-8590 `req_dominated_applies`: "the BODY's LOCATE row answers presence itself (`u.locate.whole`: the `rev-end` walk, the empty engine), so the pre-check has
nothing left to dismiss ... `CAND_READ(CAND_SLOT_PRESENCE, CAND_SLOT_LOCATE, &ls, "req-whole")->u.locate.whole` -> return true", then the kit's P2 `proven_by` read. So presence is
dropped by pcrec's LOCATE pick, outside the kit's P0-P9: confirmed. But the study already lists this input: subject §1.2 l.157 `dominated` | "S (LOCATE `whole`, `:8590`), Kf (kit P2
`proven_by`, `:8605-8614`)". What the study does not do is name it in §3.6 S1 ("PRESENCE has one home (kit, P1)", l.566) or in the §8 D176 Q4 row ("unchanged", l.912). So the
omission is in the S1 cell and the Q4 text, not in the row inventory; the critic's own note that clause 2 permits a number-free dominance at the side owning the fact limits
this to a wording fix.
Verdict: PARTLY (code holds; the study's §1.2 row already shows the LOCATE input, the gap is in the S1 cell and §8 Q4 row)

### RULING-14 (pred-memchr reclassified P with no home)
`pred-memchr` appears once in the subject (l.170: "‡ P (was V; a predecessor `memchr` on a common byte can cost more than it skips) | Kq + B"), CR_ATTEMPT-only
(emit_dfa.c:10421-10423, slot NEXT, `attempt_cand` "memchr-or-nothing by charter"). Grep of the snapshot for the row name finds no home in §1.4's items, the Q4 table, §6.4 or §8. It is a
single-byte scan-or-not at the attempt site, i.e. D161 add. 14's purview, as the critic says. Minor (one row).
Verdict: HOLDS

### RULING-15 (§G vs architecture.md's goals rule)
Quoted: architecture.md:7-12 "three to five goals, each naming who benefits and a measurable form ...; a PRIORITY ORDER ...; and NON-GOALS". Subject §G (l.102-116): nine rows (G1, G2, G3, S1, S2,
G4, G5, S3, S4), columns rank/goal/checkable form only (no who-benefits), no non-goals list. PR §0 (ruling/PR.md:32-36) non-goals include "choosing the engine (DFA vs VM) ... ; a second
backend", and §G's S4 scores "backend portability" for a second backend; S2 "count of standing rulings the option REVERSES" is a process metric. All confirmed. The rule says "every design note";
the study is a design note by its own framing, so the finding is a doc-grade rule breach, not a soundness defect.
Verdict: HOLDS

## PROBED-AND-HELD
Cites and quotes re-read from the review tree and held: emit_dfa.c:9662-9686, :9823-9832, :5677-5681, :8430-8456, :8576-8610, :10086-10087, :10186-10208, :10478-10492; memfn.h:414-415, :531-536, :541-542,
:1088-1090, :1420-1435; compose.c:309; plan_cost.def:38-41; known.c:470-496; compile.c:1342-1376, :1794-1815; locate_finish.md §1.5; decisions.md D146/D158/D161 add. 11, 14/D172/D176/D162/Q-WR-3/Q-WR-9;
run_axes.sh GROUP F4/F5; r17b_prime.md P1, M22, M23; set.tsv consumer-kind keys. Scripts re-run: beyond.py (identical to beyond_out.txt on the four ereh rows) and compose_sim.py (byte-identical to
compose_out.txt). Compiles: 4 (`x[0-9]*`, `qz*`, `[QXZ]\w*`, `(?s).+x\d`), all stamps as the critics reported. Counts: 16 items judged: HOLDS 10 (items 1, 2, 3, 5, 7, 11, 12, 13, 15, 16), mixed HOLDS/PARTLY 2 (items 6, 8), PARTLY 4 (items 4, 9, 10, 14); REFUTED 0; one NOT VERIFIED sub-claim (fit_seq_legal trip); compile budget used 4 of 15. Not re-derived: the 8/26 allowance-key counts, the 24/4/23 row arithmetic, the 85k/115k window populations beyond re-running the script.

## STATE AT HANDOFF
STATE: complete
OWED: none

VERIFY COMPLETE
