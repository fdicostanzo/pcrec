# CRITIC cost — p48
Twin (mine): `git archive 02a054851` copy under cost/tw, patched so the entry predicates read `scan_span > 0`
(5 expressions in 3 functions: `dfa_seed_can_be_scan_head` x3, `revend` entry_head x3 lines; `dfa_start_is_scan_head`
left alone), built once `nice make -j2`. Probes: 16 ad-hoc patterns + the 11-row scan_edge_census manifest, stock vs twin.

## Verdict on the split
ENTRY now: small and justified on the evidence (sites hold, 0 answer diffs on 40 probe subjects, benefit is outside the band on 3 of 4 cells). The document under-counts what the build touches (tests, a shared predicate) but the build stays small. RELAX and TABLE later: right, and already carried by plan rows. STAY floor: right to defer; its trigger is unnamed.

## Findings
### COST-1 ENTRY: the doc's "four sites" hides a shared predicate; patching the obvious one breaks prefilter placement
- status: SUSPECTED
- severity: design
- effort: S      blast radius: emit_dfa.c `dfa_start_is_scan_head` (12872), `emit_scan_loop` s0head (12920, 12982, 13059)
- where: report "The entry rule ... the four sites above"; Questions 1
- claim: At 02a054851 the entry predicates are 6 `scan_span != 0` expressions in 3 functions (emit_dfa.c:12896,12897 in `dfa_seed_can_be_scan_head`; :13705-13706 and :13768 revend `entry_head`; plus :12874 `dfa_start_is_scan_head`). The first and the revend ones were unchanged since b05ccfc0b (diff of the two commits touches none of them; same lines +3 offset), so the doc's site list still matches. But :12874 is ALSO the `s0head` predicate that decides where the candidate-start prefilter is emitted (12982/13059: "it MOVES rather than being replayed"). A builder who changes "all four" to `> 0` through that helper changes prefilter placement as well as the jump. The doc never says the s0 case must be split off (my twin changed only the seed function's s0 test, not the helper).
- evidence / repro: emit_dfa.c:12872-12898, 12920-12921, 12982, 13059 in the review tree. With my twin (s0 test inlined as `> 0`), `x*`, `(?<!.)a*`, `\bw*x`, `q*(?=z)`, `x*\bfoo` lose exactly the `goto ..._scan_edge` and `..._scan_edge:;` label lines (diff of emitted C, 2-6 lines each) and answer identically to stock on 10 subjects each (0 diffs, run under watchdog). So the split-off is sound; the point is that the doc does not state it, and its "ng twin emits text identical to nogoto" was shown only on base10num (s0 not a head).
- proposal: build brief names the helper split (entry-dispatch question vs s0/prefilter question; the code comment at 12862-12870 already says they are different questions), adds an s0-unbounded-head witness (`x*\bfoo`-shape with a prefilter) to the sabotage set.

### COST-2 ENTRY: existing checks assert the general entry test on exactly the population the rule removes; the doc's witness list omits them
- status: CONFIRMED
- severity: maintenance
- effort: S      blast radius: tests/codegen/run_scan_edge_census.sh (2) at :198-205; S227; the doc's sabotage proposal
- where: report "Sabotage witnesses" (design standing question 2); Summary leaning
- claim: `run_scan_edge_census.sh` check (2) fails the build when a seeded machine with an edge lacks `if (is_stop && !is_dead) goto ..._scan_edge;`. Under the rule, 6 of the 11 manifest rows lose that line.
- evidence / repro: twin vs stock over the 11 manifest patterns, count of the entry-test line: `(\b\w+\b)`, `\b\w+\b`, `\b\w+\b$`, `\b\w+\b\z`, `\b\w+\z`, `\b\K\w+` 1 -> 0; `(foo\B)` 1 -> 1 (bounded reverse; also why S227's `foo\B` witness survives); 4 rows were already 0. So check (2) must be rewritten to "iff a bounded head is seedable", and then its witnesses cover ONLY `(foo\B)` for the keep side. Neither this file nor S227/S764/S780 (seedhead/entry) appears in the doc's cost line "297 artifacts, spec hunk".
- proposal: put these three scripts (+ the S227 comment, which describes "killed cell" reasoning that is now bounded-only) in the build's site list; add one unbounded seeded witness whose ABSENCE of the jump is asserted (the doc's `!= 0` plant), so the check is two-sided.

### COST-3 ENTRY: abi/pin cost, counted
- status: CONFIRMED
- severity: maintenance
- effort: S      blast radius: ~8 files for the number plus one re-pin
- where: report design Q3 ("needs readers by grep")
- claim: the doc defers the count. At 02a054851 `PCREC_ARTIFACT_ABI` is 92 (emit_dfa.c:55, landed two commits ago by lane s3m after a 91->92 renumber). Readers of the number by grep: src/gen/emit_dfa.c (1), tests/codegen/run_codegen_tests.sh ABI_EXPECT (1), tests/codegen/run_recursion_identity.sh (B) pin (1, re-pin FILEPIN), tests/mech/sabotages/S693 (1, 2 lines), docs/spec/match_api.md (3), docs/dev/history/abi_changelog.md (entry), plus tests/mech S283's figure comment and run_cpset_structure.sh (comment). That is 8 files before the §2.18 hunk (tuning.md :434 [2.18¶3] states the entry line verbatim, so the hunk is a rewritten sentence, not an addition) and the (B) identity re-pin.
- evidence / repro: `grep -rnE "(abi|ABI)[^0-9]{0,12}\b92\b|ABI_EXPECT=92|!= 92|RX_ABI_H 92"` over src tests docs/spec lib scripts: 8 hits in 6 files; the s3 history (renumber 85->92) shows the lane cost of any abi bump is dominated by sequencing, not by editing. Every abi bump is serial: whoever lands next takes 93; a standalone entry build is one more entry in that queue. SUSPECTED collision: other in-flight lanes (trailgc, vmcons) may also hold a provisional 93.
- proposal: the build brief takes the number at landing, not at branch time (what s3m/reqvm1 did).

### COST-4 ENTRY: the benefit argument is stronger than the doc states, and "+1.0% residual" is not a cost of the rule
- status: CONFIRMED
- severity: doc
- effort: S      blast radius: none (argument)
- where: report "What the bench null band means here" vs its own table
- claim: The doc argues x1.20 "sits on the band edge as a timing" and rescues it by instruction determinism. Its own table lists bench ratios x1.35 (trim-match-60k noatomic), x1.33 (grok), x1.31 (hyb-datepath-16k) alongside x1.205, i.e. three of four recorded cells exceed the ±19.92% large-cell band. If those subjects are >=1 us cells (a 60 KB scan certainly is), the loss is outside noise on its face and needs no determinism rescue. The +1.0% residual (ng vs single, 3.5 ins x 49k entries) is the edge's own F, which the rule does not and cannot remove; it is the same cost the doc accepts as "insurance" for row 3, so it is not a reason to wait. Building now is justified: no waiting trigger is needed beyond the existing O-111 cells (D77: the measured gap exists).
- evidence / repro: report table lines 142-150 (bench column); 297 movers = 603 loop-entry machines, 295 corpus unbounded-only + 2 bench; 40 corpus "new since SET".
- proposal: restate; keep the leaning (build alone, when the one-build slot frees). Plan line 38 holds ONE optimization build at a time until [INLINE-C] is done; INLINE-C is STATE:started (stage 4 next), so the real trigger is that slot, not a measurement.

### COST-5 TABLE: a table whose only live rows are today's code and whose priced row is "always transparent" is a mechanism ahead of its measurement
- status: CONFIRMED
- severity: design
- effort: M      blast radius: scanedge.c selection, `--list-axes`, [LIST-TABLES], [PRIOR-COST-UNIFY]
- where: report "The table: SCAN_SITE_ROWS" rows 0,1,3,5 vs rows 2,4; G3
- claim: Rows 0, 1, 3, 5 are today's behaviour re-spelled; row 2 (`priced-out`) is TRANSPARENT today by the doc's own words ("which today is always"); row 4 is HELD. Building the table before the first priced row would ship a first-match table with one data-driven row that never fires and a card (`kit-advance@1`) that is explicitly "designed, not run" and unmeasured (doc: "added ... when row 3's trigger fires", but row 3 is the unconditional admit; the trigger names the wrong row; the card feeds rows 2 and 4). That is D77's anti-pattern (build ahead of a measured need) and memory pcrec-build-under-measurement. It is also not free in a crowded space: the plan already has [PRIOR-COST-UNIFY] (blocked) whose body lists `MIN_SCAN_CHAIN` and the byte-rate-prior admissions as members of ONE dispersed family, and [LIST-TABLES] (not-started) for listing; a SCAN_SITE_ROWS table would be a fifth/ninth member before those are resolved.
- evidence / repro: grep plan.md: [PRIOR-COST-UNIFY] STATE:blocked (members incl. `MIN_SCAN_CHAIN` limits.def:397); [LIST-TABLES] STATE:not-started; [LANDWALK-EDGEPRICE] STATE:not-started, trigger "stage 1 of [LANDWALK] landed and a card of its own shows the relaxation pays on the walk's loops".
- proposal: confirm the manager's split: no table until the first priced row lands, i.e. inside [LANDWALK-EDGEPRICE]. Fix the card's trigger sentence (it says "row 3" where rows 2/4 read it). Keep the entry rule as an emitter derivation (as the doc does), which is the correct no-table shape.

### COST-6 RELAX/TABLE: collisions, none blocking
- status: CONFIRMED
- severity: maintenance
- effort: S      blast radius: ordering only
- where: report Question 3; plan rows
- claim: Putting rows 2/4 + card in the reverse-walk build is already how the plan files it: [LANDWALK-EDGEPRICE] STATE:not-started, "its own follow-up" after [LANDWALK] stage 1, trigger "a card of its own shows the relaxation pays on the walk's loops" (r1 D11), i.e. the plan has split it off stage 1, which is stricter than the doc's "IN the P1/T4 build". [LANDWALK] stage 1 waits on Frank's build go and on [INLINE-C]; no row among the STATE:started set names scanedge.c or the entry dispatch of emit_dfa.c. The only in-flight overlap on files is emit_dfa.c itself (reqvm1, s3m, ic* all edited it in the last week: 6 of the 12 most recent commits touching it carry abi bumps). Relaxation also moves a size-cap pin (`abcdefghij[0-9]+`, 21,619 vs 21,500, §6a) by the doc's measurement; that re-pin belongs to the later build.
- evidence / repro: `git log --since=2026-10-20 --format='%h %s' -- src/opt/scanedge.c src/gen/emit_dfa.c`; plan lines 240, 288.
- proposal: reword Question 3 to match the plan row (the relaxation is a separate follow-up of stage 1, not part of it).

### COST-7 STAY: no plan row, trigger unnamed, 192 is partly measured
- status: SUSPECTED
- severity: design
- effort: M      blast radius: `pick_skip_states` (emit_dfa.c:5063), every stay-bearing artifact
- where: report Question 4; Summary item 4
- claim: The doc calls 192 "an unmeasured cardinality guess", but the code comment at emit_dfa.c:5043-5053 records M2.10: replacing it by a live-byte fraction measured 27% SLOWER on `[01]*1[01]{8}` reverse (D13) with the explicit warning "do not re-attempt without measuring the REVERSE machine". The doc cites M2.10 only as a prediction check. Its own k* gives p > 0.70 (about 179 bytes), within 13 bytes of 192, so a uniform-prior priced row moves almost nothing; the movers appear only when the byte-rate MASS replaces cardinality, and no count of those states on the corpus is given (the 80/41 are relaxation-added edges replacing stays, a different population). There is no plan row (`grep` for 192/stay floor in plan.md finds none), and the doc's own Question 4 says "filed, not scheduled".
- evidence / repro: emit_dfa.c:5040-5063 `bestcnt = 191`; doc Summary item 4 (k*=2.3 -> p>0.70) and Questions 4. Count not made: would need a pick_skip_states trace over 4,981 patterns (over my probe budget).
- proposal: leave it, but file the row with the trigger "a measured stay-vs-table cell on the reverse machine (M2.10's warning) or a cell where a stay set below 192 is the loss"; do not fold it into the table before the card has STAY-dispatch rows.

### COST-8 ENTRY shape: cheaper as ONE helper at the source, not four edits; nothing it does is foreclosed or duplicated
- status: CONFIRMED
- severity: maintenance
- effort: S      blast radius: emit_dfa.c entry derivations (+ `Dfa` annotation, optional)
- where: report "The entry rule is a derivation in the emitter"
- claim: `scan_span != 0` is spelled 11 times in emit_dfa.c (5113, 5310, 5388, 5391, 12312, 12526, 12750, 12874, 12896/7, 13705/6, 13768); only the entry subset (6) changes. The same predicate "this head's own cell was killed" is what scanedge.c line 711 (`if (ch->span > 0)`) computes. One shape: scanedge.c writes it once as a `DState` fact (e.g. a cell-killed bit, or the `> 0` convention named in internal.h:2634-2657) and the entry derivations read it; this removes the 6 re-spellings and also serves the later reverse-walk entry (seeded at a landmark) and the compound/revend writers without a seventh copy. It does not foreclose RELAX: for a one-state unbounded head the bit is 0 by construction, which is exactly the doc's argument; for a landmark-seeded reverse DFA the same derivation applies to the seed set. Per the D157/D146 split nothing goes to the kit.
- evidence / repro: grep above; scanedge.c:711; internal.h:2634.
- proposal: build brief says "name the question once"; costs a one-line helper, saves a sixth copy at the landmark seed.

## PROBED-AND-HELD
- doc's site list vs 02a054851 — held; emit_dfa.c diff b05ccfc0b..02a054851 is 18+/21- lines and touches none of the entry predicates (same code, line offset +3..+5); s0 predicate shared with the prefilter placement is the one thing the list omits (COST-1).
- bounded-only rule answer-identity — held on my twin: 16 ad-hoc patterns compiled (stock vs twin), 4 seeded/unbounded shapes (`x*\bfoo`, `(?<!.)a*`, `\bw*x`, `q*(?=z)`) x 10 subjects each: 0 diffs. Only the 2 entry lines (jump, label) differ.
- bounded head keeps the jump — held: `foo\B` and `(foo\B)` identical stock vs twin (reverse bounded edge).
- the doc's argument that an unbounded head's cells are never killed — held: scanedge.c:711 `if (ch->span > 0)` is the only kill.
- 297 artifacts / 2 bench — not recomputed (needs the 5,302-pattern census, over my compile budget); the 11-row manifest sample is 6/11 dropping the jump, consistent in direction.
