# COST findings: bakeoff (pricing_bakeoff.md @ a7b229f3f)

Scope: cost, overlap, D77 trigger, D153 remodel, bench capability (read-only), levers' place, siblings, general form.
Hours are the design's own numbers (G4/section 11: 6 h Zen 4, 5 h Zen 1, 2 h Mac = 13 h).

## Findings

### COST-1 Stage 1 (three boxes) and the Zen 1 ground truth are paid BEFORE the early stop that can make them unnecessary
- status: CONFIRMED
- severity: design
- effort: small (reorder + gate)
- blast radius: under the design's own row-1 / row-2 outcomes about 9 of the 13 box hours (Zen 4 stage 1 2 h, Zen 1 5 h, Mac 2 h) and two lanes (pcrec cards, wrapper) are spent on constants no placement will read; the "owed under every outcome" claim that justifies the order is false.
- where: section 11 table and the paragraph after it; section 4 intro ("owed whatever the bake-off decides"); G4; section 9.3 rows 1-4; section 7.4
- finding: Stage 2's listed prerequisites are stage 0 only (L-ROW, census, arm list, L-KIT, B1/B4/B5), yet stage 1 (re-measure on Zen 4, Zen 1, Mac, each twice) is scheduled first and the stage-2 early stop (row 1: FM regret on H-open below delta, read with C-BLIND) comes after. Row 1 reads only FM and the oracle: no card, no simulator. Row 1's own verdict says "the pricing build is not triggered (D77)", so the consumer cards (C-BYTE/C-ENTRY/C-WALK/C-MATCH) and C-REPORT are owed to nothing under row 1; they are owed "under every PRICED option" (PR R9.1), and FM is not priced. The Mac set and the whole Zen 1 line (stage 1 there plus the 60-site subset) feed only the cross-box reading of 7.4, which is read only in rows 5-6; rows 0-4 and 7 never read it. Rows 2-3 need Zen 4 cards (stage 3) but not Zen 1/Mac. measure_sets.md section 10.1 gives each of these builds its own D77 trigger (M3 "a stated install-time need", M4 "the regime table's pcrec-side build", M2 "a second box's OFFICIAL set"); stage 1 pulls that work forward before the bake-off has measured that pricing pays.
- repro: arithmetic from section 11: stage 1 = 2 windows per box (Zen 4 ~1 h each = 2 h; Zen 1 1-2 h each = 2-4 h; Mac 1-2 h each = 2-4 h) plus Zen 1 stage 2 = 2 h. Prerequisite cell of stage 2: "stage 0's census and arm list; L-KIT ...; B1, B4, B5" (no stage 1). Row 1 (9.3): "Placement changes no answer; the pricing build is not triggered (D77)".
- proposed fix: order 0 -> 2 (Zen 4, D and H, row-1 read) -> stage 1 on Zen 4 only (needed by stage 3, rows 2-3) -> Zen 1/Mac stage 1 and the Zen 1 H subset only once a row-5/6 candidate exists. State in section 11 which stages are conditional on which row; drop "reused under every outcome" or restrict it to the kit's Q1 cards.

### COST-2 The bench cannot time STREAMED cells as 5.1/5.2 require; the independence argument and the 5.6 arithmetic both rest on that
- status: CONFIRMED
- severity: design
- effort: medium (a bench change, or accept the grid1 fallback and drop the independence claim)
- blast radius: either the oracle is timed on a repeated buffer (the condition the design itself says flatters the walk, section 1 item 1) or a bench feature that no cost line prices must be built; if the fallback grid1 is used, cards and oracle share a harness family (G2 / section 8 harness-split row void).
- where: 5.1 (bench "already" does this), 5.2 (64 distinct 64 KiB buffers, streamed), 5.6, 8 harness-split row, B5; pcrec-bench testees/pcrec/timed.h (struct timed_in: one buf, len, iters), docs/methodology.md "What is timed"
- finding: the bench's timed loop is timed_run(const struct timed_in*) over ONE buffer with an iteration count; methodology.md: "Each trial ... times a loop of repeated calls to the same compiled matcher", "Each subject's iteration count is calibrated ... toward a fixed timed-work target", and "Per-row calibration target (ns of timed work per trial): 50000000". No buffer rotation or cursor exists (grep of timed.h, methodology.md, bench CLAUDE.md for stream|cursor|rotat finds only an unrelated `_in` frame-buffer axis). So (1) a streamed cell is not a bench capability; B5 asks only whether the bench can take our subject BYTES, not whether its loop can stream them. (2) The calibration target is per ROW (one subject), not per cell: if each of the 64 buffers is a bench subject, a cell costs 64 x 50 ms x 5 trials = 16 s, not the 0.25 s of 5.6; 9,000 cells would be 40 h, not 40 min. If the 64 buffers are one subject, the bench needs the missing rotation. Either way 5.6 and the stage-2 row of 11 are unsupported. (3) The bench's own note puts a clean cell's p90 per-row spread at 6-19% (gate_shape_v14.md, "the p90 per-row spread of a clean cell is 6-19 %"), against a 2-point margin and per-cell differences "down to the A/A floor"; B3 asks this but 5.6/9.2 are costed as if the answer were yes.
- repro: read /home/pcrec/projects/pcrec-bench/testees/pcrec/timed.h (single buf, len, iters in timed_in); methodology.md "What is timed" section (quotes above). Arithmetic: 64 x 0.05 s x 5 = 16 s per cell; 16 s x 9,000 = 144,000 s = 40 h. Design expects 0.25 s per cell.
- proposed fix: add the streamed timed loop to section 11 as a priced bench work item (bench dev, a timed.c variant plus its proof script) or choose grid1 as primary and rewrite G2 / 8's harness-split row as NOTED; re-derive 5.6 from the bench's per-row rule; make B5 ask about the loop, not the bytes.

### COST-3 The levers are in the trace build, but the bench times only what plain `make` at a pin builds: L-ROW cannot reach the PINNED tier as designed
- status: CONFIRMED
- severity: design
- effort: medium
- blast radius: H must run at the PINNED tier (5.1) but L-ROW/L-KIT as trace-build environment variables are unreachable there. The only reachable spellings are (i) a CLI/flag spelling in the default build (public surface: spec hunk per D80, registry rows, the flag rule; it breaks "default build moves no byte" and C-LEVER's premise) or (ii) a bench pin.sh change that builds a second (trace) compiler per pin per box. Neither is in the cost table; B4 frames it as a spelling question.
- where: 3.4 (L-ROW "trace build only"), 5.1 "Levers through the bench", B4, 11 stage 0; pcrec-bench testees/pcrec/pin.sh:107-108; configs.toml [testees.pcrec-local]
- finding: pin.sh archives the pin and runs `make -j$JOBS` (plain default build, binary build/pcrec); no CAND_TRACE tree is built (the repo builds one only inside test scripts, tests/memfn/run_pres_picks.sh). The adapter takes per-config argv `flags`; the only other channel is PCREC_BIN + PCREC_LOCAL_FLAGS on pcrec-local, which is scratch tier, "never pinned, never ranked", and is one process-wide string, not per config. No per-config environment exists. So L-ROW can drive the D sweep (scratch) but not H (pinned).
- repro: `grep -n 'make -j' /home/pcrec/projects/pcrec-bench/testees/pcrec/pin.sh` -> 107-108; configs.toml comment on pcrec-local: "never pinned, never ranked". Design 5.1: "Every H reading ... runs at the PINNED tier".
- proposed fix: decide before the build go: (i) test-only CLI spelling in the default build, costed as a public-surface change (spec hunk, registry, [IFACE-PUSH] interplay), or (ii) price a pin.sh variant that also builds the trace compiler. Put the choice in F5, not only B4.

### COST-4 The stated totals disagree with their own arithmetic and with each other
- status: CONFIRMED (a-c), SUSPECTED (d)
- severity: doc
- effort: small
- blast radius: the calendar Frank is asked to clear (F6) is mis-sized, on the boxes with a shared slot.
- where: 0 item 6, G4, 5.6, 11 "Total", F6, B2
- finding: (a) Mac: 11 gives stage 1 as "~1-2 h" per window, two windows per box = 2-4 h; G4/11/F6 total says 2 h. (b) Per-cell time differs between boxes: Zen 4, 9,000 cells in 1-2 h (0.4-0.8 s/cell); Zen 1, 60 sites x 9 x 2 x 2 = 2,160 cells in about 2 h (3.3 s/cell), 4-8 times slower per cell with no stated reason; the design's own 0.25 s/cell would give ~9 min for 2,160 cells. (c) Zen 4: 2 h (stage 1) + 1-2 h (stage 2) + up to 1 h (3b) = 4-5 h against 6 h; the SIMD-on secondary reading on H-open (5.1) and a re-measure of the VM-kind cards after [VMREC] (b)/(c) (11 remodel paragraph, "or measured now and re-measured") are timed windows nobody counted. (d) "Seven lanes": the 11 table lists stage 0: 2, stage 1: 1, stage 2: 1, stage 3: 2, 3b: 1 ("a fresh small lane"), stage 4: 1 = 8 non-kit lanes; seven only if 3b is not a lane. Kit lanes (L-KIT, K5, K7), the store-owner ruling (K6) and bench-dev work (COST-2/3) are outside "seven".
- repro: arithmetic as above from 11 and 5.6 text.
- proposed fix: recompute with one per-cell time and print the derivation; state or drop the SIMD-on and re-measure windows; count 3b and list kit/bench lanes separately.

### COST-5 Arms per site (~9) is below the design's own arm counts
- status: SUSPECTED
- severity: size
- effort: small
- blast radius: stage 2 and the top-up run 10-70% more cells than costed; with COST-2 the box hours move further.
- where: 5.6 ("~9 arms (including the A/A configs)"), 3.1 (median 3-5, p90 ~10), 3.5 (kit sites: default + 3-6 footprint-bests + 2 random), 3.5 top-up (J top 3 + every rule pick under every constant set)
- finding: cross-path arms 3-5 (median) + kit within-site extras (3-6 footprint-bests + 2 random, default already counted) 5-8 + 2 A/A = 10-15 per site for the 170/177 sites that have a kit start-search site, before the top-up. 9 is under the sum at the median.
- repro: the sum above; confirm when the census states the arm count.
- proposed fix: cost stage 2 from the census (the design already says the bench sizes it); mark 9 as a placeholder and do not quote 6 h until then.

### COST-6 Stage 1's "pcrec half" is not one sonnet lane: it is the store's M3 + M4, and the "one wrapper" is M3 under another name
- status: CONFIRMED
- severity: maintenance
- effort: small (design), large (the work)
- blast radius: a duplicate measuring driver beside M3's pcrec-measure, and a lane estimate that hides a milestone with a spec hunk.
- where: 4.3, 11 stage 1 row (one sonnet lane), K7; docs/design/measure_sets.md section 7 (line 1174 "The install-time tool (M3)", line 1177 pcrec-measure "one driver, owner-supplied cards and probes"), section 10.1 (lines 2199-2200: M3 and M4 rows with their D77 triggers); plan.md [MEASURE-SET] FORMAL LIBRARY Q3(a) ("a canned, self-contained pcrec script ... that measures any machine into a set")
- finding: the design never names M3 (its only "M3" is the ruling tag [R-M3]). "One command per box that runs every card and writes one set with one provenance block" (4.3) is pcrec-measure (driver, owner cards/probes, quick profile, per-group gates, local tier). The kit half (K7) and pcrec half (M4 cards) are its owner-supplied cards; the wrapper should be M3's driver. M4 is "pcrec's own quantities, their cards, the pcrec-side dependency hash's body normalization, cand_rows[] as readers in the census" (measure_sets.md:2200), a milestone with a spec hunk (4.2 admits it). One sonnet lane is optimistic.
- repro: `grep -n 'M3\|pcrec-measure' pricing_bakeoff_a7b229f3f.md` -> only line 386 ([R-M3]); `sed -n 1174,1182p docs/design/measure_sets.md`.
- proposed fix: say stage 1 builds M3 (research profile) + M4 to measure_sets.md's design; re-cost as two lanes plus the kit's; record that this is the "stated need" M3's trigger waits for.

### COST-7 F7's "do not wait for L-KIT" hides a second full H timing
- status: SUSPECTED
- severity: design
- effort: small
- blast radius: running without L-KIT and adding it later (to grade a'-vs-d) needs a new pin, hence re-timing all of H, on a population whose H-open was already read.
- where: F7, 10 item 1, 5.1 ("A pin change between the H sweep and the top-up voids the top-up's cells"), 3.2 (H-open contaminated after a revision; one revision at most)
- finding: kit within-site arms exist only if L-KIT is in the artifacts timed at the pin. Timing H without it and adding it later is a new pin; the 5.1 rule voids the cells, so H is re-timed and H-open is no longer unread. The "weaker evidence" route of 10 item 1 is not a cheap deferral: it spends H-open.
- repro: SUSPECTED; confirm by asking whether L-KIT lives in the pcrec pin or in the kit's separate test build (K1).
- proposed fix: F7 should cost the later pass (one more H window, H-sealed becomes the held-out) or tie H timing to L-KIT's arrival.

### COST-8 Remodel overlap (D153) is stated for stage-1 cards only; "VMREC (b)/(c) move the form" is unsupported
- status: SUSPECTED
- severity: maintenance
- effort: small
- blast radius: either an unneeded wait on [VMREC] (if (b)/(c) are byte-identical like (a)) or stale H ground truth for VM-route sites (if they move bytes and the H pin precedes them); G5's "reusable archive" is pin-specific either way.
- where: 11 "Remodel overlap" paragraph; D182 (decisions.md:9994+); plan.md [VMREC] (status: (a) done byte-identical, (b)/(c) not started)
- finding: D182 says only that step (a) is byte-identical, no abi bump; it does not say (b)/(c) move bytes. 11 asserts they "move the VM consumer's form" with no cite. If they are zero-mover, cards do not stale and no wait is needed. If they move bytes, H's VM-route arms (pin choice) are affected too, which the paragraph omits. L-ROW edits the cand_select / cand_rows[] neighbourhood of emit_dfa.c, which [DECISION-LOG] (not started, plan.md ~1469) and [OPT-SETS] also name; no STATE:started row names cand_rows/cand_select as a work site (grepped), so no hard conflict found.
- repro: `sed -n 9996,9998p docs/dev/decisions.md` (step (a) byte-identical; nothing for (b)/(c)); plan.md [VMREC] next: line.
- proposed fix: ask the vmrec lane whether (b)/(c) are zero-mover; put the H pin in the ordering paragraph; name R-30b (abi 94) as an H-pin predecessor for window arms, not only for L-KIT.

### COST-9 H-sealed is timed in every outcome and read in almost none
- status: CONFIRMED (arithmetic)
- severity: size
- effort: small
- blast radius: about a third of H's timed cells is spent for a reserve opened only after a rule revision, "one revision at most".
- where: 3.2 (H-sealed = 1/3 of H "timed in the same windows"), 9.3 rows 0-4
- finding: H 150-200 sites, H-sealed ~55 = 28-37% of the H sweep. Rows 0-4 and 7 never open it. The sealing value is real, but timing it in the same window is a choice and the design does not state its cost.
- repro: 55 / (150..200) = 27.5-36.7%.
- proposed fix: state the price; consider timing H-sealed in its own later window at the same pin only if a revision happens, or accept the cost explicitly.

## Standing questions

### (1) SIBLING OF A FAMILY
Yes, five members are the 2nd/3rd of a family already in the tree:
1. The one-command re-measure / "one wrapper" (4.3) is M3 pcrec-measure (docs/design/measure_sets.md:1174-1182, table :2199); plan.md [MEASURE-SET] Q3(a). UNIFY: build M3's driver; kit half and pcrec half are its owner cards (COST-6).
2. The prereg file with CHOSEN constants, sha journalled, sealed raw logs (3.2, 9.3) is the second instance of the evaluator-params kind and the kit's prereg.tsv (docs/design/measure_sets.md:1596, :2143-2186, row E-P :2201; docs/design/memfn/regime_eval.md rev 2.4 items 1-2, 2.8 sealing, 4.3 C7). UNIFY: same canonical format; the prereg hash IS the kind's digest.
3. The census (3.1: compile every pattern under deny arms, read CANDTRACE per arm) is the third member of scripts/emit_sweep.py ARMS (BASE,FLAG) with CANDTRACE tagged per pattern and arm (scripts/emit_sweep.py:68-84) and tests/axes/run_axes.sh (every deny flag over the corpus). Precedent: measure_sets.md 9.3 and review-table row M4 (line 28): "the census is an emit_sweep MODE, not a second tool". UNIFY: census as an emit_sweep mode with a BFS arm generator.
4. The scorer/simulator with cross-fit oracle, A/A floors, C7, noise quadrature, streamed condition, blinded J-population is the replay evaluator of [REGIME-EVAL] (regime_eval.md rev 2.4; plan.md [REGIME-EVAL] not-started; ~6.8-7.2 h of timing in its plan, regime_eval.md:1166). Two evaluators, same machinery, same Zen 4 windows. UNIFY the scorer and C-SCORE/C7 code at least; time-share the streamed grid where populations coincide.
5. Trace-build env levers (PCREC_PICK_PLANT src/gen/emit_dfa.c:10974; PCREC_MF_MEAS_CONSULT src/gen/memfn_sites.c:990; PCREC_MF_ROUTE_TRACE/MEAS_TRACE) are the existing family; L-ROW would be a third but the first used to PRODUCE timed artifacts (COST-3). L-VALID and "read the path from CANDTRACE" belong to [DECISION-LOG] (plan.md ~1469-1474: "promote the selection trace ... rather than add a parallel writer") and [LIST-TABLES]. UNIFY at the third member: a named-row deny belongs with the [OPT-SETS] row-set surface, not a private env.

### (2) GENERAL FORM + UNLOCKS
General form: a REPLAY EVALUATOR FOR COMPILE-TIME DECISIONS: (a) enumerate the valid choice set of a decision site by compiling under forced alternatives, (b) time each alternative on held-out subjects with cross-fit, (c) grade any decision rule written as a pure function of a declared view by regret against the measured best, with a prereg, a sealed reserve and planted-failure controls. The placement question is one instance; the rule plug-in changes, the machinery does not.
Unlocks, with triggers:
- One evaluator for [REGIME-EVAL] and the stop-ranking acceptance runs. Trigger: the second of them is scheduled.
- Regret-gated landing of any new selection row ([DEC-FALLBACK]/[OPT-SETS] rows, new NEXT or LOCATE rows). Trigger: a row proposed whose benefit is only argued (D77).
- Per-box constants QA: C-REPRO as the acceptance test of M3 on a new machine. Trigger: the first official second-box set (M2).
- The shadow/regret population (PR R5.2) for a shipped pricing build. Trigger: the pricing build's go.
- A [DECISION-LOG] audit: L-VALID's valid-row dump is that channel's machine form. Trigger: [DECISION-LOG] step 0.

## PROBED-AND-HELD
- 13 cited code locations in src/gen/emit_dfa.c and memfn (cand_rows[] 10154 and end 10630, CandPath 11828, cand_select_quiet 10869, cand_select 10721, used restore 10996, cand_rs_dense_applies 10087, comments at 7872 and 8020, fallback comment 10735, window.c:620, compose.c:309, memfn.h:414-415, PCREC_PICK_PLANT 10974): 13 of 13 match.
- Trace build vs default build: 3 patterns (`[<>&]x`, `foo\d+bar`, `(a|b)+c`) compiled with build/pcrec and build-trace/pcrec: emitted C identical except the `#include "x.h"` line echoing the output file name (3 of 3; C-LEVER's premise holds with no lever set).
- NEXT `memchr` row carries .deny = 0 (emit_dfa.c:10397), so "no public deny reaches it" holds (1 of 1).
- 5.6 arithmetic on its own premises: 250 x 9 x 2 x 2 = 9,000 cells; x 0.25 s = 37.5 min (matches "~40 min"); 250 x 9 = 2,250 (matches "~2,200 arms") (3 of 3).
- G4 / 11 / F6 totals agree with each other (6/5/2 h) and Zen 1 5 h agrees with B2 (3 of 3; the inconsistencies are COST-4 against the arithmetic).
- STATE:started rows touching cand_rows / cand_select as a work site: 0 of the started list ([VMREC], [MEASURE-SET], [MEMFN] adjacent, not overlapping).
- Stage-1 sets kept uncommitted scratch until K6 avoids a default-build mover (1 of 1).
