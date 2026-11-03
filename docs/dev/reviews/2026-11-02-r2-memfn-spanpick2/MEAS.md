# MEAS — crit-memfn-spanpick2 (fix-induced lens, pricing/measurement half + measurement standing questions)

Subject: span_pick.md rev 2 (frozen copy, 5b3bc376a). Review tree: worktrees/crit-memfn-spanpick2 (959c08124).

## Findings

Population/evidence used: rev 2 frozen copy; R-33 raw sweep (5,329 alternatives via r33_sim/sim.py);
5 compiles (review-tree build: smp20 x3 arms, pr09; trace build: smp20 once). No make, no timing.

### MEAS-1 — the stream line's `streams x byte(method)` re-introduces the per-stream factor C1 removed from `hit` (C1: PARTLY / INTRODUCES-NEW)
CONFIRMED. Severity: speed (would flip a priced pick) + design. Effort: one sentence + one card definition. Blast: every priced stream comparison (PAIR vs memchr/walk). §The pick (formula), §Cost cards.
- Formula (span_pick.md :170): `streams x byte(method) x 1e6`; `streams` has no card and no definition. The card table (:192) keys `find.byte` PER METHOD, PAIR included, "per byte scanned". C1's own principle (:181-182): PAIR's second stream is "in its measured hit(PAIR), not a formula factor".
- If `find.byte(PAIR)` is the PAIR method's measured cost per subject byte (what the card says), it already holds both streams, and `streams=2` counts the scan twice. If it is a per-stream number, the PAIR card duplicates memchr's and the table's "per method" is wrong. `span_pick/onestream.py` prices it as `streams * C_SCAN` with C_SCAN = memchr's 0.06 (i.e. byte(PAIR) per stream).
- The ambiguity flips the note's own example: with a two-stream-measured byte(PAIR)=0.12 read through `streams=2`, smp20 P/hit 20 becomes 264,694 vs '/' 153,477 (instead of 144,694): the verdict the table says "turns on hit(PAIR)" is decided by this undefined factor instead.
- Fix: drop `streams` from the formula and define `find.byte(m)` as the method's cost per subject byte (all its streams), as `hit` now is; recompute onestream (same numbers if byte(PAIR) := 2 x C_MEMCHR).
- Related SUSPECTED (low): `hit(PAIR)` "per candidate returned ... slope over hit density" is measurable, but the card regime names landings (periodic/random) and not the MEMBER SPLIT ({x} only vs x/X alternating); if the PAIR renderer restarts the non-hitting stream, the slope depends on the split. Confirm by reading compose's PAIR arm restart and naming the split in the card's `subject`.

### MEAS-2 — Horspool's line reads `hit(hors)`, which no card or prerequisite list names (C6: PARTLY)
CONFIRMED. Severity: design (a term with no card). Effort: small. §The pick :174, §Cost cards :192-196, §Robustness :262-263, §Staging later rows :338-339.
- The line is `(1e6/E_r[sh]) x (probe + q_r x (hit(hors) + verify_r))`. `find.byte`'s method list is memchr, memchr-back, PAIR, walk; `find.hit` is "per method" with no list; §Robustness ("with `hors.probe` and `hit(walk)` defined and carded, priced Horspool is decided by measured cards") and the later row ("Horspool priced: `hors.probe`, `hit(walk)`") both omit `hit(hors)`. So the prerequisite list is short by one card, and priced Horspool could ship "decided by measured cards" with an uncarded term (or with hit(walk) silently standing in for hit(hors)).
- Also undefined: whether verify_r on the Horspool line excludes S_last (the probe already tested it via q_r); counting it twice prices a probe-hit's first compare double.
- Fix: name `hit(hors)` (or state hit(hors) := hit(walk) as an ASSUMPTION with its basis), add it to both prerequisite lists, and say verify_r runs over the window's other positions.

### MEAS-3 — "each term computed exactly and rounded half-up once at its end" is not implementable in D176 Q5's fixed-point integers (C1: INTRODUCES-NEW)
CONFIRMED (arithmetic + population count). Severity: design/doc. Effort: small (declare a scale). §The pick :164-167.
- `passes_r = m_r(S) x prod_i pass_r(i)` with `pass = m/1e6`: an exact value has denominator 1e6^n. int128 (measure_sets §1.7's intermediate) holds 1e6^6 at most (1e36 < 1.7e38 < 1e42). Over R-33's sweep (`meas/factors.py`): 192 of 5,329 alternatives have more than 6 non-full positions, 34 have 20 or more. `1e6 / E_r[sh]` is a rational too. "Exactly, once" therefore means bignum/rational arithmetic in the kit, a new mechanism; D176 Q5 rules "higher-resolution FIXED-POINT integers", which implies a declared scale and per-step rounding at that scale.
- "Half-up" vs measure_sets §1.7's "round half AWAY FROM ZERO": the same for positive prices, but name one rule.
- Fix: declare the fixed-point scale (e.g. prices in 1e-12 units, each factor rounded at that scale, so `m x prod pass` cannot vanish for any window the kit admits) and cite §1.7's rounding.

### MEAS-4 — two quoted numbers in §Robustness are mis-attributed / mis-stated (C1 doc; lesson 1)
CONFIRMED. Severity: doc. Effort: trivial. §Robustness :240-249, §The independent control :411-412.
- ":241 Zen 1 `plan_cost.def` constants scan 0.06, verify 2.5, enter 20, hit 20 c": plan_cost.def has NO hit row (rows: C_MEMCHR, C_BITMAP, C_VERIFY, C_ENTER, C_MISPRED, MATERIAL_NUM/DEN, MAX_SET, HORS_MIN). 20 c is R-33's H_HIT ASSUMPTION (`docs/dev/lanes/r33_sim/sim.py:29,44`, r33_report.md :85 "ASSUMPTION, nothing on file").
- "F favours '/' 2:1 either way" (:248, repeated :411): onestream.out gives 2.0000 at hit 20 and 3.0563 at hit 40 — "at least 2:1".

### MEAS-5 — `verify.cmp` is measured at two pass rates (and replaces C_MISPRED) but the formula has one `cmp(form_i)` and no mispredict term
CONFIRMED (text). Severity: design (a card regime with no term). Effort: small. §Cost cards :195, §The pick :175.
- The card: "per T-SETTEST form, per T-CMP row x length class | pass rate 0 and 0.5 | replaces C_VERIFY (UNMEASURED), C_MISPRED". The price: `verify_r = sum_i cmp(form_i) x prod_{j<i} pass_r(j)` — one number per form, independent of pass_r(i). Which reading the price takes, or how the two combine with the step's pass rate (C_MISPRED's role today), is undefined, so one regime of the card has no reader, or the mispredict cost is silently dropped (on dense steps it is 6x C_VERIFY in plan_cost.def).
- Fix: write `cmp(form_i, pass_r(i))` with its interpolation between the two measured points, or drop the 0.5 regime and say mispredicts are model error.

### MEAS-6 — among qualifiers, "the least worst-case ratio" decides with no band, so D176 Q5's tie rule holds only against the default (A3: PARTLY)
CONFIRMED (text vs D176 Q5). Severity: design. Effort: one clause. §The pick step 3 :153-156; §The tables (TIE) :120-121.
- D176 Q5: "prices within the measurement-noise band tie, decided by the existing declared tie rows". Rev 2 applies it only default-vs-candidate (T_BAND -> TIE_DEFAULT). Two qualifiers whose worst-case ratios differ by less than their band are decided by that sub-noise difference, not by TIE. Rev 2 says "then TIE", i.e. only on EXACT equality.
- Fix: "least worst-case ratio beyond the band; qualifiers within band of each other go to TIE's rows".

### MEAS-7 — the band of a COMPARISON is undefined, and model error is 0 for the first priced row (C2: INTRODUCES-NEW)
CONFIRMED (text). Severity: design. Effort: small. §Robustness :234-238, §The pick step 2 :151-152.
- The band is defined per PRICE (quadrature of card noise x coefficient). Qualification is a comparison of two prices that SHARE cards (smp20: both read verify.cmp and enter; PAIR vs memchr share nothing else). Summing the two bands, quadrature of the two, or the band of the difference (shared cards' coefficients subtracted first) give different verdicts near the edge; the choice is an unstated hand-set rule — exactly the freedom "nothing is tuned" excludes.
- "Model error is NOT in the band ... the spread of that ratio is the model-error term the NEXT priced row adds": the first priced row therefore runs with model error = 0, the same "unmeasured read as 0" C2 removed for noise. The row's own 588-style run is the guard, but the note should say so (or require the first row to carry a stated model-error allowance labelled UNMEASURED DEFAULT, D149).
- Fix: band of a comparison = quadrature of (coefficient difference x noise) per card; first priced row: model error UNMEASURED, gated by its own run.

### MEAS-8 — noise becomes a decision input, but the set's identity (values_digest, no-shadowing) excludes noise; stage 2's owed list omits those hunks (C2: INTRODUCES-NEW)
CONFIRMED (spec text). Severity: design + doc (D80 contract). Effort: small (spec hunks + one digest-coverage decision; possibly a digest-version bump). §Cost cards :203-206, §What moves.
- `docs/spec/measures.md` §3.3¶1: values_digest "covers no provenance column", and `noise_e6` is one; §5¶4 no-shadowing accepts a file with a committed (id, rev) iff its values_digest matches; the stamp is `id@rev:values_digest` (§4¶2). measure_sets.md §4.1: noise is a provenance column not handed over, "No selection reads noise today"; §1.6 "the same values from any provenance give the same digest".
- Once the band reads noise, a FILE or `-I` set naming a committed `zen4-grid1@1` with identical values and different `noise_e6` loads (not shadowing), stamps the identical string, and can change a pick: the stamp no longer names what decided the bytes.
- Stage 2's list (kit request, MF field, "`measures.md` §4 and match_api hunks", producer, derived rule) misses: values_digest coverage of noise (spec §3.3¶1, and its readers by grep), §5¶4, measure_sets §4.1/§1.6. Also "`measures.md` §4" is the STAMP section; the kit channel's homes are measure_sets §4.1 and match_api.
- Fix: move noise into the digest (a digest version event) or forbid a FILE from sharing a committed id; list the hunks.

### MEAS-9 — "a new REVISION of zen4-grid1 (rev 2)" contradicts the spec's one-run rule; the question asked of main is the wrong one (D3: PARTLY)
CONFIRMED (text). Severity: doc/design. Effort: trivial. §Cost cards :208-213; Staging stage 2.
- `docs/spec/measures.md` §8¶1 (the contract): "a second reading of the same cells is published as a new `rev`, and a new run as a new `id`". measure_sets.md §2.2: "A re-measure on the same box is a NEW id (`zen4-grid3`), because it is a new run"; §0 "One box, one run, one method version, never mixed". Rev 2's own job is a new run ("the grid keys are re-measured under it", "grid-sized"), so by the contract it is a new id (`zen4-grid2`, which is also what memfn/data/cards/kit-grid.tsv's header calls kit-grid@2's run: "grid2's").
- Rev 2 asks main "whether a revision may carry a successor method version" — the contract already refuses it on the ONE-RUN rule regardless of method version. The conflict to surface is D176 Q3 (and plan [MEASURE-SET]'s "next: ... as zen4-grid1 rev 2") vs spec §8¶1; rev 2's default choice ("rev 2") is the one the spec forbids.
- Fix: default to a new id (`zen4-grid2`) and name the departure from D176 Q3's wording, citing §8¶1.

### MEAS-10 — what an unnamed compile prices with moves twice and the note names neither move (D2: PARTLY; standing Q3)
CONFIRMED (spec/design text; M2 is planned, not landed). Severity: design. Effort: small. §Cost cards :215-217, §What moves.
- Today: DEFAULTS `idk zen4-grid1@1` (holds; measures.md §5¶6). That set has no span card, so a priced row on a bare compile finds every card absent and keeps (unpriced). For bare compiles to price at all, DEFAULTS must flip to the new set (spec §5¶6 "the latest committed set"; DEFAULTS.log; §8¶3) — a default change with its census (measure_sets §3.4), not stated in stage 2 ("stamps unchanged").
- At M2 (plan [MEASURE-SET]: "the envelope default is M2"; measure_sets §3.4, D166 add. 2) the idk default becomes an ISA envelope, which EXCLUDES every per-byte cost row ("every reader of a cost row skips"). Every `find.byte`/`hit`/`enter` card is such a row, so every priced row goes dark on every bare compile at M2, and every artifact whose pick consulted moves its stamp (and possibly its pick back to the default) — a mass mover event the note's §What moves does not mention.
- Fix: one paragraph in §What moves: DEFAULTS flip at the first priced row (census), and the M2 interaction (envelope must carry the span cards' safe direction, or priced rows are named-set-only).

### MEAS-11 — "keys a pick read are counted pcrec-side (the stamped set against the artifact's trace)": the artifact carries no trace, and the trace is the kit's self-report (D1: INTRODUCES-NEW; standing Q2)
CONFIRMED. Severity: design (a control sharing a source with its subject, learnings §3/K35). Effort: medium. §The independent control :413-415, Goals 4 :33-34.
- Repro: `build/pcrec -p rx --measures=zen4-grid1 -o s20.c --pattern '(?i)x/1234'`; `grep -c MFTRACE s20.c` = 0. MFTRACE exists only on the stderr of a separately built -DMF_TRACE binary (`tracebuild/pcrec`, 98 lines for the same pattern). So the D176 Q1 check ("every cost an artifact used is a declared row of its stamped set") would read the KIT's trace of the keys the KIT says it read — not pcrec-side, not from the artifact, and not independent of the code it checks. measure_sets §4.2 also rules the kit reports a boolean, never per-key traffic.
- And the stamp half of §What moves rests on the kit's `consulted`, which kit.h :286-292 defines as set by a "ROUTED finder decision" (never assigned anywhere today: `git grep 'consulted *='` in memfn/src finds only the read at compose.c:1303); T-PICK is a new table, so the recorder's extension to T-PICK is owed and unstated.
- Fix: name the independent count (e.g. pcrec-side: re-price from the stamped set's rows with a python twin that shares no code, then diff the pick), and list "`consulted` set by T-PICK rows" as part of the first priced row's change.

### MEAS-12 — the drop-F plant's witness class is the class C5 gates, so the plant cannot fire for the first priced rows (D4: INTRODUCES-NEW)
CONFIRMED (text). Severity: design ([MECH-REACH]). Effort: small. §The independent control :410-412, §Robustness :252-255.
- D4's witness: "a site where P admits a challenger and F refuses it (a dense two-member stop)". C5: "Any priced row over two-member stops is gated on a fix (an encoding fact, or a third, adversarial rate model)". The later rows listed first (priced Horspool, RESEED admission) name no site where F refuses a P winner. So until the C5-gated row, the F requirement — the note's main robustness claim — has no plant that reaches; "chosen with the cards" defers it without saying it may be UNREACHED.
- Fix: per priced row, its drop-F witness from that row's own population, or the row declares the plant UNREACHED (never a pass).

### MEAS-13 — SIMD-form `find.byte` rows either have no reader or a reader outside T-PICK (C7: INTRODUCES-NEW)
CONFIRMED (text). Severity: design (D77 / measure_sets §7.3 reader closure). Effort: small. §Cost cards :192, §The pick step 6 :161-162, §What stage 1 deletes N12 :374.
- "each SIMD form its OWN row" on the card, but "Only scalar plans are compared; SIMD forms are rungs inside the chosen scalar plan": no pick reads a SIMD-form card, and measure_sets §7.3 measures only quantities with a reader ("a quantity nobody reads is not measured (D77)").
- N12 says vany is "a T-FIND SIMD form, declined (no card) — live when carded": that IS a card reader, inside rung admission — a priced choice that is not a T-PICK row (no deny, no per-regime run under D186) and that makes SIMD-on artifacts consult the set (a stamp mover on one layer only), which §What moves does not list.
- Fix: choose — no SIMD-form cards until a SIMD rung reader is chartered as its own choice row (D186), or carry them and add that reader with its stamp consequence.

### MEAS-14 — `enter` keyed by consumer kind x entry fact still carries an assumed survival length; OFS sites have no key (C4: PARTLY)
SUSPECTED (regime). Severity: design. Effort: medium. §Cost cards :196-198.
- Today's C_ENTER is "10.7 c/B times an ASSUMED ~2 bytes a false start survives" (plan_cost.def). Survival is a property of the PATTERN's automaton after the stop, not of the consumer kind or the entry fact; a per-box card keyed by (kind, entry) measured "false-start survival" on some fixture pattern bakes that fixture's survival in. The card then replaces MEASURED x ASSUMED by MEASURED-on-one-pattern. Confirm: two patterns of one kind/entry with different post-stop automata give different per-entry costs; if so, survival is a pcrec-stated fact (from the DFA) times a per-byte card.
- OFS sites state no consumer kind (381/381, counts.out), so `enter(kind, ...)` has no key there; fine while T-FIND declines on OFS, but say the price is undefined there. "until the two `enter` cards exist" (:198) is a kind x entry product, not two cards.

### MEAS-15 — §The measurement regime covers the cards only; numbers the pick reads in every stage have no regime/flip statement (standing Q1)
CONFIRMED (text). Severity: doc. Effort: small. §The measurement regime :389-396; §Robustness :234-236.
- Read at every stage and not in the section: KEY/M's plan_cost.def integers (Zen 1, ubuntubudu, while the default compile's set is zen4; C_ENTER MEASURED x ASSUMED; MARGIN ARGUED), HORS_MIN (PROVISIONAL, one job-581 cell, dev box), the cards' gate_e6 (UNMEASURED DEFAULT, D149; the NEW cards each get one — rev 2 cites only kit-grid@1's 3 %, while its cards are kit-grid@2's), and the prior (authored; ONE-STREAM's bound reads it). "No constant appears except the card gates" is true of the BAND only; the pick keeps MARGIN, HORS_MIN and the TIE rows until their retirements — the section should list them with "would a different regime flip it" (smp20's table shows hit 20 vs 40 does).

## PROBED-AND-HELD

- **Recount reproduces**: `python3 -I span_pick/onestream.py r33_sim r33data/sweep.jsonl` output is byte-identical to the committed `onestream.out` (diff empty). smp20 numbers hold: P 144,694 / 153,476.5 -> 153,477 half-up; hit 40 166,634 ('/' wins 8.6 %); F 295,858 / 147,929 / 452,108. Population 1,637 = 1,056 + 577 + 4 (onestream.out). (C1 recompute, A2's row census)
- **C2 facts**: `mf_measure` has no noise field (memfn/include/memfn.h:1189-1194: key, value_e6, unit, source); the committed set holds 68 rows, all `kit.`, all `noise_e6` '-' (python count over measure_store/zen4-grid1/1/set.tsv); "missing noise = UNMEASURED, never 0" agrees with measure_sets §4.3 (absent = skip). Gated cards carry gate_e6 30000 (3 %), labelled UNMEASURED DEFAULT (kit-grid.tsv header).
- **D1 stamp today**: "" on every artifact sampled — 4 compiles (smp20 default, `--measures=zen4-grid1`, `--engine=vm`; pr09 named set) all `#define RX_MEASURES ""` and `.measures = ""`; `art->consulted` is never assigned in memfn/src (only read, compose.c:1303); spec measures.md §4¶4 says the same. "Condition before any key lookup => only admitted sites consult" is consistent with the recorder's semantics (set on a lookup, found or absent; §4¶2). Stamp-only movers as their own class and per-card-rev stamp moves agree with stamp-on-load (measure_sets §3.5).
- **ONE-STREAM reads no card**: it reads byte rates, which smp20 already consults today (`RX_FINDINGS "byte-rate=default:1822fb973b95a4da"`), so no new MEASURES or FINDINGS consult; "no consult, stamp unchanged" HOLDS.
- **finder_check.py checks D and F** exist as described (tests/memfn/finder_check.py:36-44, :436-455: same decisions under no set and the full synthetic set; `consulted` 0 on every compile, true arms OWED to the first reading row). D1's "replaced in the first consulting row's change" is the right home.
- **D2**: `measure_store/DEFAULTS` = `idk zen4-grid1@1`; spec measures.md §5¶6 says exactly that; no option declares a class. The cite holds (its forward motion is MEAS-10).
- **A1**: D186 addendum 1 A1 text matches Goals 4 and §The pick ("no cost-based departure ships until the cards are measured"; hand rows until then); stage 2 "no reader, no consult" agrees with measure_sets §7.3's reader closure. HOLDS.
- **A3** default-vs-candidate half HOLDS (T_BAND -> TIE_DEFAULT is a declared TIE row; D176 Q5 and D186 cited); the qualifier half is MEAS-6.
- **C1** units: masses ppm, F = |S| x 1e6/256 ppm, cards value_e6 in the set's unit (walk per-byte, D176 Q1), hit per candidate returned, Horspool line carries x1e6 via 1e6/E[sh] and pays no stream line — consistent; the residual defects are MEAS-1/3/4.
- **C5** HOLDS: the class is named uncovered and two-member priced rows are gated (plan row 1 text).
- **C6** HOLDS for `hors.probe` (defined, regime named) and D176 Q2's form; `hit(hors)` is MEAS-2.
- **C7** "a SIMD-on compile never picks another stop or alternative" HOLDS by step 6's construction; the card side is MEAS-13.
- **D4** held-out class HOLDS as text: pr09 and c04989 are in the ONE-STREAM census (onestream.out), neither is the motivating site, and the bound (the default's flat mass) is not fit on them; R-33 notes pr09 has no DEF timing (r33_report :226), so it is genuinely unmeasured for this row. The drop-F half is MEAS-12.
- **D5** HOLDS as PLAN ("a priced pick is a long-subject pick", plan row 3 [SPAN-PICK-PERCALL]).
- **C4** keying text and MARGIN retention HOLD (MARGIN stays M's default until both entry cards exist); regime is MEAS-14.

## Summary

Re-checked A1, A3, C1, C2, C4, C5, C6, C7, D1-D5 against code, spec and R-33's raw sweep (5 compiles, recount reproduced byte-identical). A1, C5, D5 and the stamp/no-noise facts HOLD. 15 findings, none an answer risk:
the price still multiplies `find.byte` by an uncarded `streams` (flips smp20's example), `hit(hors)` has no card, "exact once" rounding is not fixed-point, `verify.cmp`'s two regimes feed one term, and the qualifier and comparison bands are undefined (A3/C2 partial).
Data/stamp: noise would decide but values_digest/no-shadowing exclude it; "zen4-grid1 rev 2" contradicts spec §8¶1 (new run = new id); DEFAULTS' flip and M2's cost-free envelope silence priced rows on bare compiles; key counting from the kit's trace is not independent; the drop-F witness sits in the C5-gated class; SIMD-form cards have no legitimate reader.
Standing questions: regime section omits the non-card numbers the pick reads (MEAS-15); control (MEAS-11/12) and what-moves (MEAS-8/10) incomplete.
