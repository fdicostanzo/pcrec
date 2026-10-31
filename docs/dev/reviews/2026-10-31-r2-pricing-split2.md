# Review 2026-10-31 r2 pricing-split2 (design RE-CHECK): where search-strategy pricing lives, rev 1

DRAFT by the coordinator (crit-pricing-split2). Dispositions are PROPOSED; the manager rules.

**Manager rulings:** every proposed disposition RULED AS PROPOSED (manager, 2026-10-31). **PARTIAL re-check, stopped: Frank ruled a bake-off.**

## Subject

- `docs/dev/lanes/splitstudy_report.md` REV 1 on `lane/splitstudy` @ c06ac74ef06a173d9f46569891f82744e8b9b74d
  (identical at the branch tip c63c04fba, which adds the lane note). It revises rev 0 (70464e9a3) in answer to
  round r1 `pricing-split` (`$PCREC_TMPDIR/scratch/crit-pricing-split/review.md`, all dispositions ruled as
  proposed). Lane note with the per-finding CHANGES table: `docs/dev/lanes/splitstudy2_report.md`.
- Build base = main HEAD a3cc4de82, which is also rev 1's cite base: no cited code moved. Review tree
  `worktrees/crit-pricing-split2`, detached there, built once (`nice make -j2`, unlocked, ~19 min).
- rev 1 recommends option (a′): the kit reads per-route consumer rows from the measurement set and decides
  everything inside a window site; the backend runs one path argmin over pcrec's own choices, LOCATE first.
  The seam rule now has eight clauses. (d), the footprint split, is the fallback.

## Proposed verdict

**(a′) over (d) survives this round.** No finding reverses the ranking. On corrected counts (a′) still
reverses fewer rulings, has fewer homes per choice, and needs a smaller reply event than (d).

**rev 1's new central claims do not hold as written.** Each has a small, concrete repair:

1. **"(a′) composes exactly" and "the hybrid reduces to (a′)" (§3.3, §3.6) are false.** The backend terms the
   accounting rule calls invariant are not invariant in three places:
   - RECOVER `landing` reads the kit's `exists`, so a kit NONE pick moves RECOVER to `reverse-pass`.
   - Presence on/off gates every downstream slot's bytes.
   - RETRY reads the kit's pick, and the consumer's per-entry work depends on the RETRY row.

   In each place the exact form is rev 1's own general form (§3.8): the kit returns its best per value of a
   small declared property set, here `exists`, presence, and the consumer key. That is the hybrid. One remedy
   comes from the critics: the tree already declares the kit outputs pcrec rows read (`kfields`), so this
   exactness check is mechanical.
2. **The new `beyond(site)` site fact is the wrong term** (two lenses independently). The beyond-window walk is
   P(the whole window matches) x T, which is the same for every verify plan by the chain rule. Under rev 1's own
   rule it is a backend term. Charged per entry, it biases the kit toward deeper verify plans. Deleting it
   SIMPLIFIES (a′) by one site fact, one measurement row and one error bound.
3. **"No search" has two homes** (the kit's NONE row and the backend's S0 path). §8's "D161 add. 14 AFFIRMED" is
   false for (a′) as written. This is also exactly where the composition breaks (item 1, the `exists` read).
4. **Clause 8 (give-up) is not computable and is stated three non-equivalent ways.** `CG_FIXED` is a contract
   bit, not an order. The NEUTRAL/ONE_WAY classification is derived by an instrument and, by ruling, never
   declared. "The slot's least" does not exist for incomparable surfaces. The D158 addendum draft is stricter
   than D158 and Q-WR-3, which allow ONE_WAY. Where the clause bites (VM routes), it forces picks that §1.2/Q4
   label as priced. At stage 3 (DFA-only LOCATE) it cannot fire.
5. **"No clause reversed" is false.** D146's operative sentence supersedes integration.md rev 2's K0 price query
   by name, and a backend argmin over kit quotes is that mechanism. Frank should be asked to reverse it knowingly,
   with D146's Why (recalibration) answered. The S2 verdict for (a′) survives the corrected count.

**Proposed next step.** A rev 2 on `lane/splitstudy`, text-sized except item 1, which adds a property set to the
kit's quote. The owner's (a′)-vs-(d) question can be framed now, because no finding moves it. Its framing should
use the corrected facts: the D146 reversal named, and "exact up to a declared property set". Leaning: no third
full round. Instead, one fix-induced critic on rev 2's §3.3, the no-search home and clause 8 only, because those
are where fixes have introduced defects twice.

## Lenses as run

| lens | model | one question | why chosen |
|---|---|---|---|
| fix-induced (`fixind`) | opus | for each CHANGES row: does the fix hold; what read, hand-off, row, site fact, clause or check does it add; trace each in a3cc4de82; sibling fields unstated; spot-check >= 12 rows | skill's lens for a RE-CHECK of a revised design (launcher asked for it as the centre) |
| soundness/simulate of the composition (`compose`) | opus | does (a′) compose exactly (§3.3 accounting rule, `A(plan)`, §3.6 hybrid sentence)? test against code and re-run r1's SIM data under (a′)'s formula; + standing questions (sibling of family, general form + unlocks) | rev 1's central new claim is an exactness-by-decomposition claim; rev 1's STATE AT HANDOFF names it the claim to test hardest |
| ruling check + slot tracing + goals (`ruling`) | opus | classify (a′) against each ruling's operative clause quoted in full; one home per choice under (a′); audit §3.6 cell by cell against §G's forms; §G vs architecture.md; + forest-for-trees | the recommendation changed basis to "the ruled shape, no clause reversed"; r1's lesson 1 (quote operative clauses in full) |
| verifier | sonnet | 16 consolidated CONFIRMED items that would change the design | skill §6.2 |

Not run: premise (it ran in r1; rev 1's new premises are the composition, which `compose` tested), cost and
overlap (no build go is asked; rev 1's cost table is downstream of the open design points), adversary,
contract, and the code-mode lenses. No D27 spec-first author is recommended, because there is no caller
contract.

## Which lens caught what

- fixind: clause 8's missing order, and that it forces picks or cannot fire (only lens); `exists`/RECOVER
  (with compose); beyond term (with compose); form rungs moving prices; shadow quiet/CANDROW reach hazard;
  path simplicity order unfilled; stage-3 gate missing the D176 build; KSTRACE already exists.
- compose: presence on/off breaks the accounting rule (only lens); RETRY consumer key (only lens); `exists`
  (with fixind); beyond term with the chain-rule identity and re-run populations (with fixind); MARGIN
  qualifies "true min"; `kfields` as the declared property list (general form).
- ruling: the D146 K0 reversal; add. 11 has no §8 row; no-search two homes (with compose's second point);
  `cover` as a REPORT alternative; consumer-card key per route vs six consumer kinds; §8 omissions; A11
  strain; §3.6 cells not derivable; §G's form; `pred-memchr` without a home; LOCATE-whole presence dominance.
- Overlaps (consolidated below): FIXIND-4 = COMPOSE-3; FIXIND-5 = COMPOSE-1; RULING-4 ~ COMPOSE-3 (second half);
  FIXIND-1/-3 ~ RULING-8; FIXIND-12 = RULING-13 (S3 cell); FIXIND-6 ~ RULING-10 ~ COMPOSE-7.

## Findings, consolidated, with PROPOSED dispositions

V = verifier verdict (HOLDS / PARTLY / -: not sent, because it is a doc item, SUSPECTED, or judgement). The
verifier refuted nothing: 16 items, 10 HOLDS, 2 mixed, 4 PARTLY, 1 sub-claim not verified.

### A. The composition claim (§3.3, §2.5, §3.6 G1/G5 and hybrid sentence, clause 5)

| id(s) | finding | V | proposed | reason |
|---|---|---|---|---|
| FIXIND-4, COMPOSE-3 (first half) | RECOVER `landing` validity reads the kit's `cs.cls.exists` (`emit_dfa.c:9662-9683`). `exists` is 0 exactly for NONE (`memfn.h:1088-1090`; NONE not built, `compose.c:309`). So the kit's NONE pick, which rev 1 adds, moves RECOVER to `reverse-pass` (a per-match reverse walk plus the reverse machine). The accounting rule's "RECOVER ... per match" is not invariant. Shipped witnesses `x[0-9]*`, `qz*`, `[QXZ]\w*` (stamps `landing`). Latent today | HOLDS | FIX-NOW (study rev) | falsifies "composes exactly". Remedy: key the quote by `exists`, or take NONE out of the kit's quote (see B-1) |
| COMPOSE-2 | Presence on/off (kit, P1) gates FIRST, NEXT and the match phase (`rx_search` order in r1's `foo(bar\|baz)+` probe). Its value is P(absent) x the path's downstream cost, not a positive scaling of the site's per-byte terms (§2.5's invariance sentence fails here). M23 is one number measured on one path shape. Exact shapes: (i) the kit quotes best-with-presence and best-without (a one-bit frontier), or (ii) the backend states P(absent) and the downstream price to the kit (a new ruling scope beyond Q-WR-9) | HOLDS | FIX-NOW (study rev): adopt (i) as the leaning; restate §2.5, §3.6 hybrid sentence and §3.8 ("presence is a property the child cannot price") | the hybrid does not reduce to (a′) |
| COMPOSE-4 | RETRY `adaptive-dense` validity reads the kit's pick (`pcrec_dfa_cand_ppm`, `emit_dfa.c:8430-8456`, `:10086-10087`; a second reader of `exists`). The VM consumer's per-entry behaviour differs by RETRY row. "Two cards per route are ALL" fails. Exact form: each path hands the kit its own consumer key (route x RETRY row). That dissolves §3.8 unlock 3 (C16 joint pricing) into the composition | PARTLY (code and arithmetic hold; magnitude unmeasured) | FIX-NOW (study rev text) | a simplification: one unlock deleted |
| FIXIND-6, RULING-10, COMPOSE-7 | "Expected bytes seen" (§2.5's new site fact) depends on the hypothesized PATH by §2.5's own example, so quotes are per (site, path or key), not "one quote per site" (§3.6 G5). It and `beyond(site)` would fill D162's RESERVED per-site slot with no measured case (both tagged INFERENCE); D162 has no §8 row. compose counts at most ~8 quotes per site, against (d)'s 204, so the G5 ranking survives; the cell text does not | HOLDS | FIX-NOW (study rev): per-key asks, D162 row or a trigger per fact | D77/D162 |
| FIXIND-5, COMPOSE-1 | `beyond(site)` charged per entry is wrong. entries(o) x P(rest passes \| entry) = P(whole window matches), which every plan shares, so the beyond walk is plan-invariant and is a backend term. As a per-entry fact it biases toward deeper verify. Re-run (verifier byte-identical): reading Z/U 0 mispicks of 1.2 M (window, T) cases; reading C (conditional survival) 6.7 % mispicks at T=2, 69.5 % at T=8 on 85,176 windows (model-internal, not measured regret). With the term dropped, (a′) with `rewalk(plan)` picks the true winner on `ereh` and on every window; the kit's C-model greedy equals exhaustive | HOLDS (magnitudes conditional on reading C) | FIX-NOW (study rev): delete the fact; add "the full-window walk" to the backend's invariant terms | SIMPLIFIES (a′): one site fact, measurement row and error bound fewer |
| COMPOSE-5 | With MARGIN 2/1 kept, the quote prices the guarded pick: 0.72 % / 0.11 % of windows, mean regret 0.57 % / 0.10 % (modelled) | - | DOC: G1 cell "exact up to the kit's declared guards" | wording |
| COMPOSE-6 | `A(plan)` omits the displaced scan (walked bytes are not scanned): worst 0.09 % | - | NOTED (label a dropped second-order term) | immaterial |
| RULING-9 | §3.3's formula and §8's add. 6 draft prescribe the kit's cost method in a ruling text (architecture.md "never describe how the kit would use a fact"). Also, `rewalk(plan)` needs a consumer fact (does the engine RE-STEP verified positions? D147 add. 15) that §3.3 omits (SUSPECTED materiality) | - | DOC (ruling drafts state the facts crossing and "no ASSUMED factor", not the formula); the re-step fact into Q4 | D157 |

### B. Homes (one table per slot)

| id(s) | finding | V | proposed | reason |
|---|---|---|---|---|
| RULING-4, COMPOSE-3 (second half) | "No search" has two homes: the kit's NONE row and the backend's S0 (§3.3, §8 D176 Q1 draft). They render the same loop from the same card and tie exactly. S0 as tabulated drops the kit presence site that today's no-search artifacts carry (`(?s).+x\d`: PREFILTER `none` + `RX_REQ_BYTE "120"`, a `memchr` presence). On the VM attempt route presence is REQUIRED (`emit_dfa.c:1476`). §8's "add. 14 AFFIRMED" is false for (a′) as written. **The critics' remedies differ:** compose leans backend-only (the kit never quotes NONE, so `exists` stays 1 and A's RECOVER break disappears); ruling leans kit-only (F0 NONE per add. 14 and Frank's 2026-10-31 notice, with S0 kept only as a validity fallback where no site can be stated) | HOLDS | FIX-NOW (study rev): one home, chosen with both forces stated. Coordinator leaning: the kit's home (add. 14, Frank's notice), with `exists` as a quote property (A-row 1), because A-row 2 already needs the property mechanism | one table per slot; it is also where composition breaks |
| RULING-1 | `cover` vs composite is, by D172 ("Find-window and REPORT are the SAME request"), REPORT vs find-window of one request. In code: `cover` states a window site with `MF_ENTRY_NONE`, every span `MF_VERIFY_YES`, `MF_SK_REPORT` (`known.c:470-496`). Homing it in the backend's LOCATE argmin splits one kit axis. Homing it in the kit makes "LOCATE first" actually "kit first" and needs a match-phase card. Verifier: the facts hold; "defect" depends on a choice rev 1 did not make (whether a site's consumer is an engine at all is a pcrec fact, C3-C12) | PARTLY | DOC (study rev): state the choice and its reason; this decides what stage 1-3 build | design option, forest-for-trees with RULING-12 |
| RULING-12 | Consumer cards keyed "per route" (3 `CandRoute`s) vs six consumer kinds (`mf_site_kind`, `memfn.h:414-415`), by which the set's existing kit cards are keyed (DFA_SCAN and DFA_HAT share a route; HYB_PF is a pair). Mapping onto the smaller enum is the "One table per slot" narrowing. Unification proposal: one set section of consumer cards keyed by consumer kind, one owner, D166 add. 2 staleness; `C_ENTER` and M23 derive from it. Verifier: the key mismatch holds; "five homes" overcounts unbuilt items | PARTLY | FIX-NOW (study rev text: key per consumer kind); unification PLAN (D176 build) | narrowing |
| RULING-7 | `req_dominated_applies` (`emit_dfa.c:8576-8590`) drops presence on LOCATE-`whole` paths: a backend presence dominance, so the S1 cell "PRESENCE has one home" and §8's "D176 Q4 unchanged" are false. §1.2 already lists the input | PARTLY | DOC (study rev): name it as a clause-2 dominance in S1 and the Q4 row | wording |
| RULING-14 | `pred-memchr`, reclassified V -> P by the PREMISE-5 fix, has no home in §1.4, Q4, §6.4 or §8 (a single-byte scan-or-not at the attempt site: add. 14's purview, home K) | HOLDS | DOC (study rev) | inventory |

### C. Clause 8 and give-up (§5.5, clause 8, §8 D158 row)

| id(s) | finding | V | proposed | reason |
|---|---|---|---|---|
| FIXIND-1, RULING-8 | A per-path union of `CG_FIXED` is one bit ("contains a must-not-move row") and orders nothing (`emit_dfa.c:9823-9832`: "never a comparison of two columns"). The ordering classification is "derived by an instrument over the corpus, never declared here" (`:5677-5681`; locate_finish.md §1.5 reasons (a) and (c)). Re-declaring it reverses locate_finish r2 G7/LR-S11 (no §8 row); the instrument is not readable at compile time. Surfaces are partially ordered, so "the slot's least" can fail to exist. The three wordings (no larger than the least / ONE_WAY only / never moves) are non-equivalent. The D158 draft forbids what D158 and Q-WR-3 allow (ONE_WAY) | HOLDS | FIX-NOW (study rev): restate clause 8 as D158's own deny-relative comparison, with the per-pair relation's SOURCE named (for example, pricing only blocks recorded NEUTRAL on the covered classes by the instrument, read at design time and recorded on the path family) and an incomparable-pair rule; one wording; a Q-WR-3 row | a contract-bearing clause that cannot be computed as written |
| FIXIND-2 | The stage 3 gate "clause 8 in the census" cannot fire: LOCATE's priced block is CR_DFA only, where posture is N/A. On VM routes the clause forces picks: `handoff-attempts*` over `scan-from-startpos` (GIVEUP1 GROUP F4), and RETRY `adaptive*` over `fixed` (`fixed` is "the deny's landing row", reachable only under `-fno-hyb-reseed`). §1.2's P labels and Q4's "adaptive vs fixed" promise choices the clause removes. No shipped pick moves | HOLDS | FIX-NOW (study rev text): P only where posture is NEUTRAL or N/A; drop the stage 3 gate item or give it a site where it can fire | a check that cannot fire |
| FIXIND-3 | Under (a′) the kit makes set-driven choices that can cross the give-up surface: crossing 9 (`first-class` VM NONE, ONE_WAY, GROUP F5). Clause 8 covers only the backend's valid set. Verifier PARTLY: windows do carry REQUIRED-ness for presence, so "nothing to obey with" is overstated; the gap is for the consumer-scan choice | PARTLY | FIX-NOW (study rev): clause 8 binds the kit's within-site choices, with a give-up-bearing site fact for the consumer-scan choice (K65's shape) | unstated ruling consequence |
| FIXIND-13 | The nullable decline is called a price in clause 2 and a validity failure in §2.1. It is a route-pair `pf_admits[]` row that clause 8 does not reach this round | - | DOC | consistency |

### D. Ruling basis and scoring (§3.6, §8, §G)

| id(s) | finding | V | proposed | reason |
|---|---|---|---|---|
| RULING-2 | "No clause reversed" (§3.3, §3.6 S2, §7 row 11, §8) is false. D146: "pcrec does no cost comparison ... This supersedes integration.md rev 2's K0 price query" (integration.md:174-175, :5201). (a′)'s backend argmin over kit quotes is K0 generalized. rev 1's own §8 D146 row says "new direction". PR R2.3 ("THE SPLIT (ruled 2026-10-31)", kit "never receives engine costs") is held pending this study; rev 1 files it as a PR drafting defect (open point 16), which misfiles an owner-held item. On the corrected count (a′) still reverses fewer than (d) | HOLDS | FIX-NOW (study rev): name the D146 reversal; answer D146's Why item by item (regime, shared-source, RECALIBRATION); re-file open point 16 as an owner item | Frank must rule a reversal knowingly (r1 lesson 1 again) |
| RULING-3 | D161 add. 11 ("the only pcrec-side quantity is a MEASURED per-candidate fixed cost per route ... FILED") is the ruling (a′) extends most, and §8 has no row for it. "The ruled shape" is true of the kit half only. Q-WR-9 authorizes the pre-scan; the widening is disclosed by rev 1 but has no measured trigger (D77). Mitigation: `C_ENTER` already ships | PARTLY | FIX-NOW (study rev): add. 11 row; "ruled shape (kit half), new direction (backend half)" | ruling completeness |
| RULING-5 | Every §8 draft omits part of its clause: Q-WR-9's "default KEEP unless ... OPTIONAL and E measured" (does the precondition survive for presence?); Frank's own Q1 text from the 2026-10-31 notice; D146's K0 sentence and Guard; add. 6's list misses `cover`/REPORT; missing rows for add. 11, D162, D167 add. 1 A11 and the 2026-10-31 split | - (quotes cross-checked in items 8 and 11) | FIX-NOW (study rev §8) | the texts Frank signs |
| RULING-6 | The handoff family prices the landmark site's quote against the displaced start scan's quote. D167 add. 1 A11 forbids "read-back of the kit's form or of 'what the displaced scan skips'" for the landmark admission. Whether a quote is a "read-back of the form" is a reading | - (SUSPECTED) | PLAN: the manager reads A11 (form vs price of the form); the result goes into the §8 list | ruling reading |
| RULING-11 | The D147 draft's "SIMD re-forms only within the chosen site" leaves undefined whether the kit's within-site STRATEGY (NONE vs scan, entry kind, stop) may move with the layer | - (SUSPECTED) | DOC (study rev: define "re-forms") | |
| RULING-13, FIXIND-12 | §3.6 cells checked against §G's own forms. G1 and G5 are unscored (no regret or census exists; G1's argument fails per A). G3 is FAIL for both (MARGIN ARGUED stays in a priced choice), not "tie". S1 is not met as stated (B). S2 per RULING-2. G4 is FAIL for both against PR's bar. S3's "no reply-shape event" is false: `mf_wreply` (`memfn.h:1420-1435`) has no price components, set id or ranking, and §7 row 5 itself says "small-medium". The relative verdicts on S1/S2/G4/S3 survive | HOLDS (S3); rest - | FIX-NOW (study rev): rescore as "argued/unscored" where the form has no data; the RECOMMENDATION's "beats (d) on every goal above S4" becomes a judgement on S1, S2, G4, S3 | how the case is put to Frank |
| RULING-15 | §G has nine goals (architecture.md: three to five), no who-benefits, no non-goals. S4 scores a second backend, which PR §0 lists as a non-goal. S2 is a process metric, and S1 is a design constraint | HOLDS | DOC (study rev): PR's five goals, S1 as a constraint, S2 into the ruling section, PR's non-goals carried | guide rule |

### E. Migration mechanics (§6, clause 7, §5.4)

| id(s) | finding | V | proposed | reason |
|---|---|---|---|---|
| FIXIND-7 | Clause 7 covers family-dropping rungs only. `drop-premul`/`drop-anchored`/`drop-end-mark`/`prefilter-collapse` (`compile.c:1342-1376`) change FORM facts that clause 3 lets prices read (`drop-premul` ~1.27x scan), so a retry can flip LOCATE for an unrelated reason. Size is out of the price, so a re-run pick may be larger (the `fit_seq_legal[]` trip is unverified) | HOLDS (trip NOT VERIFIED) | FIX-NOW (study rev): one sentence on whether a form rung may move the strategy pick | unstated sibling |
| FIXIND-9 | The `pf.used` save/restore holds, but the cited precedent (`req_pres_proof_quiet`) also runs QUIET. An un-quiet shadow in the trace build marks rows REACHED for `run_cand_oracle.sh`, so the reach check stops firing for them. Stage 1's identity gate omits CANDTRACE/CANDROW identity | - | FIX-NOW (study rev: one remedy line and one identity arm) | check adequacy ([MECH-REACH]'s shape) |
| FIXIND-11 | The two-pass tie rule needs a total simplicity order over PATHS (tuples of rows), and none is declared | - | FIX-NOW (study rev: declare one key, for example `cand_nodes[]` slot order then row order) | unfilled cell |
| FIXIND-14 | Stage 3 needs the kit to read the consumer rows (the D176 build, §7's last sentence), but §6.4 files that as a separate trigger, and stage 3's gate omits it | - | FIX-NOW (study rev: name it in the gate) | ordering gap |
| FIXIND-10 | §5.4's interim cites D176 Q5's resolution as present. It is ruled, not built; today's integer-unit ties are rounding ties, which Q1 rules out. Otherwise the interim held: it does not contradict `wf_ties[]` and moves no pick | - | DOC (stage 3 gate lists Q5's build) | tense |
| FIXIND-8 | I2's rate half exists already (`KSTRACE`, `findings.h:420-439`); the set-read half is the new instrument | - | DOC | §7 row 10 slightly high |
| FIXIND-15 | `fixed` is not P (it is the fallback): counts become fb 5 / priced 22. The name "NONE row" collides with `MF_ENTRY_NONE`. Does "entry kinds the consumer accepts" replace today's per-alternative span lists, or ride beside them? `path-needs-unbuilt` is at `:11950` | - | DOC | |

## PROBED-AND-HELD (merged)

- Fixes spot-checked: 22 CHANGES rows (fixind). Held as fixed: SLOT-1 (Q-WR-9 quoted in full), PREMISE-6,
  SLOT-5, PREMISE-11, SIM-3, PREMISE-3, PREMISE-4, SLOT-7, SLOT-11, COST-3, COST-9 (68 rows counted), SLOT-8,
  SLOT-12 (zero movers), SLOT-13 (clause 4's miss cannot fire on today's kit: answers open point 14 in rev 1's
  favour), PREMISE-10/COST-4 (save/restore), SLOT-4 (the re-run is what the driver already does), SIM-6 (the
  two-pass rule is order-free and moves no pick), COST-1 (`cover` CR_DFA), PREMISE-5 (24/4/23 = 51 recounted).
- SIM-1's fix holds once the beyond term is dropped: (a′) with `rewalk(plan)` recovers the true winner on
  `ereh` and on all 115,248 + 85,176 windows at six T values. `rewalk` is computable from what the kit holds
  today. The C-model greedy equals exhaustive with the plan-dependent per-entry cost (compose; verifier re-ran
  the script byte-identical).
- Match and landmark density are invariant to the kit's pick; FIRST's K admission dissolves under a path argmin
  into comparing two paths' totals; PARKED vs RESEED needs no separate per-kind card on today's forms (compose).
- Rulings: Q-WR-9's letter is not breached by the kit half; D146's arch-blindness half holds if card names stay
  arch-free; D157 holds for the cards; one decider each for PARKED/RESEED, the presence fold, MARGIN, verify
  depth (apart from REPORT), the size ladder and the route pair; D166 staleness key, D152 and D147 SIMD-off
  addenda are consistent extensions (ruling; 17 rulings classified, 15 slots traced, 9 cells audited).
- Compiles: fixind 6, ruling 4, verifier 4 (re-runs), compose 0; about 110 file:line cites checked across
  lenses, with one off (`:11946` -> `:11950`).

## By-id completeness

- fixind: FIXIND-1..15 → C (1, 2, 3, 13), A (4 with COMPOSE-3, 5 with COMPOSE-1, 6), E (7, 8, 9, 10, 11, 14, 15),
  D (12 with RULING-13). All dispositioned.
- compose: COMPOSE-1..7 → A (1, 2, 3 first half, 4, 5, 6, 7), B (3 second half). Standing questions: A (the
  `kfields` general form, verdict item 1) and B (RULING-12's consumer-card family). All dispositioned.
- ruling: RULING-1..15 (R0 is the classification table, not a finding) → B (1, 4, 7, 12, 14), A (9, 10), C (8),
  D (2, 3, 5, 6, 11, 13, 15). All dispositioned.

## Lessons for the guide (proposed)

1. **An exactness-by-decomposition claim** ("the child's min and the parent's min compose exactly") gets the
   check: list every parent row that READS a child output (here the declared `kfields`/`kask` readers) and every
   child term that varies with the parent's choice. Composition is exact only if each is a declared property or
   a declared input. Two lenses found the `exists` read independently; it was in the declared reader list all
   along.
2. **For each term a fix ADDS to a cost formula, ask whether it varies with the choice being priced.** A term
   invariant to the choice belongs to the parent and needs no new fact (COMPOSE-1: rev 1 added a site fact,
   measurement row and error bound for a term that cancels by the chain rule).
3. **"No clause reversed" claims: grep the rulings for supersession sentences** ("This supersedes X") and check
   whether the proposal re-creates X (RULING-2). This extends r1's lesson 1 (quote operative clauses in full) to
   the clauses that retire an earlier mechanism by name.
