# MEAS — measurement + cost critic, span_pick.md rev 1 (frozen 324aae3a9c5a...)

Review tree: worktrees/crit-memfn-spanpick (884996ef6). Compiles used: 3 (of ~40). Python: meas/dual.py.
Paths below are repo-relative unless absolute.

## Findings

### MEAS-1  The band's input (noise_e6) has no channel to the kit and no value in the committed set
CONFIRMED. design. Hits §Cost cards "handed to the kit on mf_art_begin ... the existing channel, no new
fact" and §Robustness "Each card row carries its A/A noise_e6".
- `memfn/include/memfn.h:1189-1194` `mf_measure` = {key, value_e6, unit, source}. No noise field.
- `docs/design/measure_sets.md` §4.1 (l.948-950): "No provenance columns. abs_ns_e6, noise_e6, n ... are
  pcrec's listing's. A kit row that wants noise asks by REQUEST. No selection reads noise today."
- `measure_store/zen4-grid1/1/set.tsv`: all 68 kit rows have noise_e6 = "-" and n = "-" (awk over the rows
  section: 68 rows, 0 with noise, 0 with n). 26 derived, 42 measured.
So the whole "margin is measured, no constant appears" rule has no data today and needs: a kit request (main
files it, single writer), an `mf_measure` layout change (an MF_SITE_ABI / class event, pcrec abi, spec hunk
in match_api + measures.md §4 which says "kit rows only, value and unit"), a producer that writes noise
(stage 2), and a noise rule for DERIVED rows (xover, saving: 26 of 68 rows; §7.3 defines noise only for a
group's A/A and a fit residual). None of this is in a stage. Fix: add it to stage 2 with its abi/spec cost,
or state the band as a stage-3 prerequisite.
Effort: M. Blast: stage 2/3 plan, abi count.

### MEAS-2  "One set per compile" is NOT consistent with measure_sets as written: the span cards and the grid keys cannot share a set under two methods
CONFIRMED. design. Hits §Cost cards "must sit in the same set: the stage-2 job measures both, or the set
carries grid1's rows re-read under one method version".
- measure_sets.md l.122 "Sets. One box, one run, one method version, never mixed."; §1.4 l.409-412 cross-set
  comparison only within one `method@ver`, unit regime is pinned per method; spec measures.md §2.1 header
  `method` is ONE `owner-name@ver`.
- The design names a NEW method `kit-span@1` (a new cards file, memfn/data/cards/). A set whose header names
  one method cannot hold kit-grid@1 grid keys and kit-span@1 rows. The only legal spelling is span cards as
  quantities of a successor method (kit-grid@2, which CLAUDE.md of cards says is "grid2's prep lane's, not
  written here"), and the set re-measures every grid quantity under that ver.
- "Re-read" is not available: spec measures.md §8¶1 "A committed revision never changes"; a re-read is a new
  measurement. So stage 2 is not "one short timing job per box"; it is grid2 (full profile, "run in a slot",
  measure_sets §7.3/7.6) plus the span cards. Cost understated by roughly the whole grid.
- Consequence for DEFAULTS (measure_store/DEFAULTS: idk -> zen4-grid1@1): a new set without the grid keys,
  made the default, drops the finder's pay-rule operands (finder.c:469 fd_lookup, absent = skip) and moves
  every finder-pay site: a mover class outside the span pick, in a stage the design says "moves nothing".
- §7.3's READER CLOSURE ("a quantity nobody reads is not measured, D77") also applies: at stage 2 no reader of
  the span cards exists (stage 3 adds them), so the measuring tool's closure is empty unless stage 1 declares
  the readers. D176 Q3 ruled the measurement, but not the order "cards before any reader".
Effort: M (a method rev + a grid-sized job). Blast: stage 2 cost, DEFAULTS movers.

### MEAS-3  "Stages 1-2 move nothing; stage 3 moves only picks" is wrong for the stamp; the first consult moves every consulting artifact
CONFIRMED (premise), SUSPECTED (extent). design. Hits §What moves when the data is regenerated ("Generated C
carries no costs ... moves bytes only where a T-PICK row admits a departure"), §Cost cards ("an artifact
stamps the set it priced with").
- spec measures.md §4¶2-¶4: the stamp is `id@rev:digest` iff ANY reader consulted the set (found or absent),
  empty otherwise. Today every stamp is "": checked, `build/pcrec -p rx --pattern '(?i)x/1234'` and
  `'a(b|c)+d'` both print `#define RX_MEASURES ""` (default and `--measures zen4-grid1`).
- §The pick step 1 says "price every plan" and the T-PICK gate is step 3 / a later paragraph. If pricing runs
  before the gate (or the default is priced to compare), the set is consulted at EVERY priced site, so the
  stamp line changes on every such artifact even when the pick is `keep`; and any later card revision changes
  the digest, so the line moves again on every consulting artifact with zero pick movers. That is an abi event
  plus an identity/manifest re-pin on the whole population, not "only picks".
- The design's movers census (`movers/<seq>.tsv`, "expected empty") must count stamp-only diffs separately or
  it is neither empty nor informative.
Fix: say the order (T-PICK condition tested before any card key is looked up, so a `keep` site never
consults), and say the stamp event explicitly in stage 3's abi line and in the regeneration section.
Effort: S (doc) / M if the order is changed in code. Blast: every stage-3 abi event, test pins.

### MEAS-4  "Target class" as a fixed fact has no input; the class a compile reads is the default or --measures
CONFIRMED. design. Hits §The shape step 1 "target class (-> the measurement set)", §Chosen by the target.
`cli/main.c` `--target` is the .rxt build prefix (cli/CLAUDE.md:22), not a CPU class; spec measures.md §5¶6
"one class, idk (a compile that declares none)"; src/core/measures_table.inc:130 has only `idk`. No option
declares a class. So "keyed by class (zen4, Zen 1, Apple)" works only as `--measures=NAME`, and an
unnamed compile on any machine prices with zen4's cards (what N13 calls a problem for the constants today).
A class-declaring input is a new CLI/lib option, which the iface-push rule batches into [IFACE-PUSH];
Open question 2 only covers the envelope. Fix: state that stage 3 prices with the named set only and that an
unnamed compile uses zen4 by DEFAULTS (a conscious choice), or add the option row to the iface push.
Effort: S doc. Blast: stage 2 (Zen 1/Apple sets are unselectable by default), design honesty.

### MEAS-5  Card regime vs the regime the pick faces: per-byte streaming cards, but the losses and the bar are per-call
SUSPECTED (what confirms: price a search_short loss with the 4 cards). design. Hits §Cost cards,
§The measurement regime, goal 2.
- The price is "per 1e6 subject bytes": scan + hits + verify + enter. No per-call fixed term. grid1 carries
  `f` (fixed per call, n in {48,64,128}), `ccold`, `delta`, `wuse` precisely because per-call cost flips
  method choices; t588tri/bar588 losses cited (smp14 1.267, smp24 1.259) are search_short cells, and the
  stage-3 bar is "every regime of a 588-style run" including search_short and match. A pick that cannot see a
  call-level term can only be validated per regime, never predicted per regime; the cards' "miss-only stream,
  fresh long buffer" regime is one regime of three.
- `enter` ("per consumer kind, false-start survival measured not assumed"): false-start survival depends on
  the candidate (its offset, what verify passed, the DFA's behaviour after re-seed), so it differs between
  plans of one site; the design asserts "only passes_r differs" and prices enter as a constant per consumer.
  That is plan_cost.def's C_ENTER "MEASURED x ASSUMED ~2 bytes" re-stated with a measured constant.
Fix: either a per-call term and a `enter` card by candidate class, or state that the pick is a long-subject
pick and that search_short stays the per-row evidence (then the A/A floor argument for short regimes changes).
Effort: M. Blast: stage 2 card list.

### MEAS-6  The band covers card repeatability, not model error; the "no constant" claim leans on a gate that is itself an UNMEASURED DEFAULT
CONFIRMED (premise), SUSPECTED (effect). design. Hits §Robustness "The margin is measured, not tuned".
- band = quadrature of each card's A/A+fit noise x coefficient. Model error (independent positions: the
  design itself marks it an ASSUMPTION and cites pricing_requirements R4.6 "its measured error bound joins the
  band"; the landing-regime spread; prior x 2.3x wrong) is not a card, so not in the band; nothing measures
  R4.6's bound in any stage.
- measure_sets §7.3: a group passes only if noise <= `gate_e6`, which in kit-grid@1 is 30000 (3 %) "UNMEASURED
  DEFAULT, D149". So every surviving band is <= a constant nobody derived. Not tuning, but "no constant
  appears" should read "no constant except the card gates".
- Rough reach, my arithmetic (meas/dual.py, SIGN ONLY: R-33 differ_keyB.tsv, KEY B constants H 20, scan 0.06,
  walk 1.16; P = R-33's own gap>1, F = flat |S|/256 mass with scan+hit only, no verify, no band; 340 of 346
  rows parse): sim pick beats today under both P and F in 119 of 340 (35 %), under P only 66, under F only 155.
  By kind, both: COVER 6/7, PF differ-alt 42/95, PF differ-method 67/220, LMHIT 2/3, PRE 2/2, OFS 0/13. So
  the pre-band ceiling of stage 3's reach is about a third of R-33's disagreements, and the smp20 class (R4)
  is about 6 units.
Effort: doc + a model-error measurement if R4.6 is to be honoured. Blast: stage-3 rows 3-4.

### MEAS-7  Controls: the F-model sabotage witness may not reach its site, and the validation set is the set that motivated F
CONFIRMED (the design's own §Robustness text), SUSPECTED (the rest). design. Hits §The independent control.
- "a plant that drops model F must flip smp20's class witness": §Robustness says smp20 flips only if zen4's
  find.byte/find.hit separate '/' beyond band under P, and that otherwise the rule keeps {x,X}. If the cards
  keep {x,X}, dropping F changes nothing at smp20, so the witness does not reach its site ([MECH-REACH]).
  The plant needs a synthetic set (measure_sets §8) that forces the flip, or a second witness where F
  decides and P does not (a witness whose F verdict and P verdict differ by construction).
- F was introduced from smp20's arithmetic (R-33: "under F, '/' wins by a wide margin"), and the stage-3
  acceptance for item 1 is job 588 on the same smp20. R5.2 ("validation sites share no number with the cards")
  holds for the cards; it does not hold for the rate-model choice. Needs a held-out class (R-33's R4
  neighbours pr09 `x[Q%]y`, `a[\18]b`, `a[*/]b` have no DEF timing, per r33_report) or a stated owner exception.
- "a check that every cost an artifact's pick read is a declared row of its stamped set": the list of keys
  read comes from the kit's own consult recorder (the thing `consulted` is built on). Stage 1's check is
  counted pcrec-side from artifact diffs (good, K35); this one has no pcrec-side count. Name who counts.
Effort: S-M. Blast: stage-3 check plan.

### MEAS-8  Abi/identity story is inconsistent inside the note and thinner than the precedent it cites
CONFIRMED. design/doc. Hits §Staging stage 1 "Abi: none", goal 2, §What moves.
- Goal 2: "artifacts byte-identical to main but for the abi digits". §Staging stage 1: "Abi: none if bytes
  identical; an MF_SITE_ABI event only if the plan call's seam changes mf_site". window_site §5.2 pairs every
  MF_SITE_ABI event with a pcrec abi bump, readers by grep (D76/D94), and a re-pin. The plan/emit split and
  method+resume joining the plan reply (§The designer/emitter split "What moves across") do change the reply
  struct; the note should decide now, not "if".
- Witness list: window_site §5.2 required emit_sweep byte-identical "on every arm (default, each deny,
  --engine=vm, both SIMD layers), stamps included, tests/findings/manifests/*_movers.txt unchanged, reach
  floors". span_pick's stage 1 names only main vs branch over corpus, bench, 588 sample. The stage turns
  `--memfn=no-X` denies into T-FIND/T-PICK filters (A-PLAN point 5), which is where a unification slips: a
  denied arm picks through a different row than the default. Cost of the full arm set is ~5,400 compiles x arms.
- Unit systems: stage 1's KEY rows keep plan_cost.def's integers (1/100 cycle, truncating, Zen 1, "re-measuring
  any row is a byte-moving kit event: its own deny, a pcrec abi event, G1 at both layers", plan_cost.def
  header). Stage 3 prices in walk-relative e6 ratios. Two cost systems coexist from stage 2 to the last stage-3
  row; the default plan is chosen by one and priced by the other. State which wins at a disagreement (it must be
  the default: keep) and that the integer truncation order of C-model is preserved (byte identity).
Effort: S doc, M test plan. Blast: stage 1.

### MEAS-9  COST: stage 1 is the justified stage but is sized as one change; stage 2 is a grid-sized job; stage 3 is pricing revived before its D186/D77 trigger
CONFIRMED (the facts), judgment for the rest. design (cost).
Stage table (code / jobs / windows / abi / re-pins / buys / trigger):

| stage | code | jobs and windows | abi / re-pin | buys | trigger |
|---|---|---|---|---|---|
| 1 unify + plan/emit split | ~9.5k lines of kit files touched in part (finder 1162, window 2788, compose 1451, presence 247, runcmp 689, precheck 570, ofsskip 995, pffind 570, generic 871); 24 inventory items U1-U10, N1-N14; A-PLAN "M" | byte-identity sweep ~5.4k compiles x arms (box queue, one heavy suite at a time); G2; rxtsource, registry, codegen suites | MF_SITE_ABI + pcrec abi + identity re-pin if the reply changes (see MEAS-8) | deletions: 5 find deciders to 1, 3 tie rules to 1, 3-4 mass variants to 1, stops ratchet-down (roadmap ratchet). Zero speed | simplification qualifies alone (memory pcrec-simplification-is-a-benefit); no D77 trigger needed. A-PLAN needs "the kit's agreement" and rides "the first stream step that touching search sites"; STREAM has no step with a go |
| 2 cards | new method rev (MEAS-2), cards file, noise channel (MEAS-1) | dev box night window (cleared with owner, not 20:00-01:00), ubuntubudu slot, Mac directional; grid-sized | spec measures.md §8¶3 hunk, `--list-measurements`, built-in set embed; DEFAULTS move later | nothing by itself; unblocks stage 3, retires plan_cost.def Zen 1 rows | D176 Q3 ruled it, gated on step-0 census; but D77: measure under a named reader, and at stage 2 no reader exists |
| 3 item 1 (smp20 class) | T-PICK row, deny, priced key | 588-style run RTE vs deny, every regime, A/A | its own abi event + movers census + stamp event (MEAS-3) | one measured loss class: smp20 1.58-4.03x; population about 6 of 5,406 patterns (R-33 R4: 7 under KEY B, 3 under KEY A), pre-band | D186 choice change |
| 3 item 2 (Horspool priced) | row + HORS_MIN deletion | 588 run | abi event | 6 D-hors sites keep wins; hex8-bounded dense 1.53 loss | D176 Q2 ruled |
| 3 item 3 (RESEED admission) | row | 588 run; no timing of a RESEED stop exists (R-33: confounded) | abi event | 95 PF units (64 with gap>=1.5), bench ledger shows 3.6x off on loglines/level-context | none timed |
| 3 item 4 (dense pairs) | renderer first (unit change, Open Q5), then row | 588 run | 2 abi events | R-33: 154 of 225 prefer the walk by the sim's own key; only about 71 rare pairs gain; the utf8 421x/202x cases are a PRIOR defect (r33_report) | Open Q5, prior fix |

Observations that make "costlier must prove more" bite:
1. Stage 3 as a whole is within-engine pricing. [PRICE-BAKEOFF] was DEFERRED the same day (plan.md: "revisit
   only when an unmeasured choice shows headroom"; pricing_requirements header: pilot reached 0.981 of ideal
   at 0 rules, within-engine headroom about 2 %; "a pricing build waits for the stream work"). D186 says
   "Pricing returns only if hand-written rows start conflicting" and its revisit trigger is "the row table grows
   past what hand-written rows can keep loss-free". Item 1 is ONE row and nothing conflicts yet, so the case
   for the cards + two rate models + bands at item 1 is not made. The honest D186 alternative for item 1 is a
   hand T-PICK row on stated facts (no entry, candidates differ in member count) with 588 evidence; its price
   is a threshold the design wants to avoid (suspect-tuning-constants), which is the argument the note should
   make, with the smp20 population count (about 6) next to it.
2. Stage 2 before stage 3 item 1 buys cards that, by the design's own §Robustness, may not even flip smp20
   (Open question 3: "fix the prior"). The owner's cheapest first move may be the prior row for the {x,X} vs '/'
   pair facts (a data change judged alone), not a card stage.
3. Stage 1 is separable: U4/U5/U9 (primitives), U2/U6 (kit-only), N3 (dead code), U3/U10/N1/N6 (the planning
   core) are independent byte-identity units. One change with a 24-item list is the shape D153 and the
   architecture guide warn against (a failed item blocks all; "any item that cannot be byte-identical leaves"
   is the escape, but the sweep must then be re-run).
Effort: n/a. Blast: owner decision on staging and on whether stages 2-3 wait for a trigger.

### MEAS-10  Overlap and unnamed dependencies
CONFIRMED. design (cost/overlap).
- §The shape "presence states unbounded spans (D176 Q4)": that is [MEMFN-UNBOUNDED-SPANS] (plan.md:952,
  STATE:not-started, "an MF_SITE_ABI event ... same change"). Stage 1's T-PRES/T-FIND for presence depends on
  a row nothing builds. State that presence in stage 1 keeps today's (non-span) statement.
- Open question 5 (PF two-stream renderer) and N4/"PAIR in PF frames" are [MEMFN-PAIRSTOP] (not-started) /
  Q6 "filed, not built"; stage 3 item 4 cannot start before it. Name it as a prerequisite row, not a
  "unit addition".
- A-PLAN (roadmap §0a, line 379): plan call / emit call split is its "next step", "the kit's agreement" and a
  ride-along on "the first stream step that touches search sites"; STREAM row: "no step built, none has a go".
  The note's claim that the split and stage 1 are one change commits the kit to A-PLAN's step without that
  go. If stage 1 is meant as A-PLAN's step, say so and take the roadmap's ratchet accounting (deleted parallel
  mechanisms vs added: T-PICK and KEY rows are new selection tables beside the first-match tables).
- pricing_requirements.md is an unreviewed DEFERRED draft ("no rev 2 and no critic round now", open questions
  O1-O5 not put to Frank). The note borrows R4, R4.6, R4.2, R5.2/5.3, R6.1, R6.2 and R2.7 as requirements;
  cite them as ideas, or copy the ones relied on into this note (a deferred draft can change under it).
- pcrec-side findings (landmark, run pin, next_keys): D167 / D153 [START-TABLE] remodel not in flight now
  (no [START-TABLE] row STATE:started in plan.md grep), so no D153 conflict found, but the pcrec-side scan
  index and run pin are read by findings.c and req.c; any change there rides this design's abi event.
Effort: S doc. Blast: dependency graph.

## PROBED-AND-HELD

- Unit consistency: the set's unit row `kit.beta.WALK.DFA_SCAN.r1e0c0` (value 1.0, 0.1892 ns/B) IS the scalar
  walk per-byte cost in the pinned regime (set header unit_key); the design's price unit matches D176 Q1. 1 key.
- "Chosen by the target, not the host": no host probe exists in the set loader (spec §5 name/FILE/-I/DEFAULTS
  only). Held.
- DEFAULTS `idk -> zen4-grid1@1` (measure_store/DEFAULTS) and spec §5¶6/§8¶3 agree with the design's account
  of today. 3 sources.
- Card shape rules: `memfn/data/cards/CLAUDE.md` and finder_check.py check C read every table by listing and
  hold keys to cards and deps to form hashes (as the design says). measure_sets §7.2 "checker refuses a row
  off its card". Held.
- MAX_SET: `src/core/limits.def:393` PCREC_OFSK_MAX_SET=4 equals plan_cost.def MAX_SET row (U9's duplicate is real).
- Constants quoted in R-33 (C_MEMCHR 6, C_BITMAP 116, C_VERIFY 250 UNMEASURED, C_ENTER 2000 MEASURED x ASSUMED)
  match memfn/src/plan_cost.def. 7 rows.
- Stamp empty today: 3 compiles (smp20 default, smp20 --measures zen4-grid1, a(b|c)+d), all `RX_MEASURES ""`.
- Unmeasured-and-visible rule ("a plan whose method has no card is unpriced and cannot challenge"): consistent with
  measure_sets §4.3 "No fallbacks ... falls to the table's own default" and spec 0¶2 "a skip, never a presumed value".
- "Re-measuring is a deliberate data change" paragraph: consistent with plan_cost.def header's byte-moving
  kit event rule and D76/D94 (readers by grep). The ritual is stated; the gaps are MEAS-3/8.
- No D153 conflict: no remodel lane row ([START-TABLE]) is STATE:started in plan.md's grep.

## Summary

1. The band's input does not reach the kit and is empty in the committed set (MEAS-1); the span cards cannot share a set with grid keys under two methods, so stage 2 is a grid-sized job (MEAS-2).
2. "Stages 1-2 move nothing / only picks move" is wrong for the stamp: today `RX_MEASURES ""`; the first consulting stage flips it everywhere (MEAS-3). No class-declaring input exists (MEAS-4).
3. Cards are long-subject per-byte; the losses and the bar are per-call/search_short; the band omits model error; the F-plant may not reach smp20 (MEAS-5/6/7).
4. Cost: stage 3 is within-engine pricing revived the day it was deferred; item 1 reaches about 6 units; a hand T-PICK row is the D186 baseline to beat (MEAS-9).
5. Stage 1 is the justified part but should be split; depends on unbuilt rows [MEMFN-UNBOUNDED-SPANS], [MEMFN-PAIRSTOP] and A-PLAN's go (MEAS-10).
