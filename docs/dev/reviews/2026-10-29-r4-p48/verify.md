# VERIFY p48 (sonnet verifier)
Review tree: worktrees/crit-p48 @ 02a05485148faadf96910332e4386ba0ac9e3268 (rev-parse confirmed). Probes in verify/. No twin built; consequence claims re-derived from code reading, emitted C, and recomputed arithmetic.

## SUMMARY
- SOUND-1: HOLDS (code quoted; second reader `s0head`; harmless only via scanedge.c s0 refusal)
- COST-1: HOLDS (same fact as SOUND-1; its SUSPECTED status is settled by the code quotes)
- DESIGN-7: HOLDS (second reader and the x* unconditional-goto mover class both reproduced; "three slots" and the SUSPECTED twin part are design/unverifiable)
- SOUND-2: PARTLY (the `!= 0` half is invisible to answer checks: holds. But the subject only says the second witness breaks "answers", so a structural detector is arguably implied, though it names none)
- COST-2: HOLDS on mechanism (check (2) asserts the entry line on rows the rule removes; S764/S780 anchor on the exact `entry_head` text). Count: I get 7 of 11 forward rows losing the line, not 6 (no twin; derived from edge-block shape)
- DESIGN-1: HOLDS (masses recomputed; id=\d+; stamps "none"; utf8 NONE). Nuance: subject l.379-380 lists what the UNPRICED relaxation admits; the subject does count the priced-in subset (53/18/13)
- DESIGN-2: PARTLY (rows 3/4 text omits (6), (8), and the s0 `!a` refusal, which is not numbered even in row 1's "(1)-(8)"; but the s0 refusal is a code line that stays, so "wasted slots on s0" needs the refusal to be dropped, which nobody proposes)
- DESIGN-3: HOLDS for the collision (set already has kit beta/f/xover cards, one-card-per-owner.quantity); "same quantity" is overstated (existing xover rows compare kit search forms vs the walk, not ADVANCE)
- DESIGN-4: HOLDS (reorder at a 4-cap is a decline; masses rank `\s`/hex below every row-4 admit; utf8 key NONE unstated). Conditional on >4 unbounded candidates on that machine
- DESIGN-5: PARTLY (a) REFUTED against the subject's stated "uniform prior" (the two criteria agree within 179 vs 192 bytes); holds only if the retired-into row is row 4's byte-rate prior (subject l.469 is ambiguous); (b) HOLDS (card does price the STAY compare); (c) overreach, not a contradiction of D13's measurement
- DESIGN-6: HOLDS (369/922 = 0.400 vs G2's 0.35; 0.29 is cycles)
- DESIGN-8: HOLDS (b) and (c); (a) PARTLY (reading of row 2's scope)
- DESIGN-10: HOLDS on facts (two selectors, two caps, two rankings, no survey row); the "third member"/unification is design opinion; plan row PRIOR-COST-UNIFY already lists `pass < 4`
- COST-3: HOLDS (abi 92; 8 hits in 6 files by the quoted grep; abi_changelog + cpset comment make ~8)
- COST-5: HOLDS (facts and states); "D77 anti-pattern" is judgement, and consistent with the manager's split
- COST-6: HOLDS ([LANDWALK-EDGEPRICE] is a separate not-started follow-up of stage 1)
- COST-8: PARTLY (literal `scan_span != 0` appears 9 times, not 11; scanedge.c:711 kill guard holds)
- COST-7, DESIGN-9: SUSPECTED, skipped. DESIGN-9 cannot be settled outside the denylist (raw break-even rows are in p48_evidence); the report's own table (l.215-231) is consistent with the critic's arithmetic only under one r/k convention. COST-7: emit_dfa.c:5043-5053 (D13/M2.10 warning) is confirmed in code; no plan row for the 192 floor was looked for beyond PRIOR-COST-UNIFY's text, which lists `pass < 4` but not 192

## SOUND-1, COST-1, DESIGN-7 (second reader of dfa_start_is_scan_head; x* mover class)
Verdict: HOLDS.
emit_dfa.c:12872-12875:
`static bool dfa_start_is_scan_head(const Dfa *d) { return d->s0 >= 0 && d->s0 < d->n && d->st[d->s0].scan_span != 0; }`
Its own header (12859-12862): "ONE reader since STEP 1.1 ... The candidate-start prefilter fires at `s0` ... when `s0` is a head the prefilter belongs on the EDGE path ... it MOVES rather than being replayed". And "IT USED TO ANSWER THE LOOP'S ENTRY DISPATCH TOO, and that was a different question wearing the same predicate".
Entry reader that calls it first: 12890-12892 `dfa_seed_can_be_scan_head`: `if (dfa_start_is_scan_head(d)) return true;`, then `scan_span != 0` at 12896-12897 over `s1u`/`s1g`.
Second reader (prefilter placement): 12920 `bool s0head = edges && dfa_start_is_scan_head(f->d);` -> 12982 `if (f->pf->u.pf.emit && !s0head) f->pf->u.pf.emit(c, f);` (generic path) vs 13059 `if (f->pf->u.pf.emit && s0head) f->pf->u.pf.emit(c, f);` (edge path). Revend writers: 13705-13706 and 13768 `entry_head ... scan_span != 0`.
So to drop the s0 entry jump for an unbounded s0 head one MUST change the call at 12892 (or the helper), and changing the helper also flips `s0head`. Narrowing it moves the prefilter to the generic path for an unbounded s0 head.
Why harmless today: scanedge.c:495-500: "A NON-ACCEPTING self-loop at `s0` is the start-anywhere thread ... `[a-z]*`'s own s0 self-loop is ACCEPTING and is kept: a machine whose start state accepts has no candidate-start prefilter at all", `if (s == d->s0 && !a) continue;`. Emitted `[a-z]*`, `x*`: `RX_DFA_PREFILTER "none"` (probe). Plus pf_open guard emit_dfa.c:6624 `if (%s == %d && %s == (size_t)-1)`. Coincidence of the pass, as DESIGN-7 says.
Mover class (DESIGN-7): `build/pcrec -p rx --features all --emit-main --pattern 'x*'` -> line 101 `goto rx_forward_scan_edge;   // the start state carries a scan edge` (and line 180 for the anchored machine), UNCONDITIONAL, no seed table. `[a-z]*` identical. `(?<=a)[a-z]*` instead carries the conditional line 140 `if (rx_forward_is_stop(forward_state) && !rx_forward_is_dead(forward_state)) goto rx_forward_scan_edge;   // seeded straight onto a scan-edge head`. The subject (l.589-590) calls the movers "seeded unbounded heads" and lists `x*`; `x*` is not seeded, so two entry-line spellings must be covered by the abi reader grep. Holds.
Not verified: whether the critics' twins narrowed the helper (DESIGN-7's SUSPECTED part); the subject's own `patch_nogoto.py` is under the denylist.

## SOUND-2, COST-2 (sabotage half invisible; existing check (2) asserts the removed line)
SOUND-2: PARTLY. Subject l.515-518: "the entry rule: base10num-noatomic's forward machine (a seeded unbounded head, which must have no entry jump), and a seeded BOUNDED head (which must keep it). Planting `!= 0` back must break the first; planting `< 0` must break the second's answers." Only the second is stated to break answers, so the first is implicitly structural. The critic's point that no answer check can see the first holds (answer-identical by the rule's own argument), but the subject does not claim an answer check sees it; it names no detector either.
COST-2: HOLDS on mechanism. tests/codegen/run_scan_edge_census.sh:198-205:
`# (2) The entry dispatch has to be able to SEE a seeded head. Where the machine emits a seed table AND carries an edge, the emitted entry must be the general test ...`
`if grep -q "rx_${mv}_seed_state" ...; then if ! grep -q "if (rx_${mv}_is_stop(...) && !rx_${mv}_is_dead(...)) goto rx_${mv}_scan_edge;" ... bad "... has a seed table and a scan edge, but its loop entry is not the general head test"`.
Manifest (lines ~115-127): 11 rows. I emitted each with the script's flags (`-fcomments --memfn=no-window-search -fno-rev-end -fno-start-width -fno-start-landing`): all 11 carry the seed table and the entry line today (so check (2) applies to all 11). Edge shape per row: rows `(\b\w+\b)`, `\b\w+\b`, `\b\w+\b$`, `\b\w+\b\z`, `\b\w+\z`, `\b\w\b`, `\b\K\w+` (7, forward) have only unbounded edge blocks (no `scan_run_length = 1` block) -> the bounded-only rule removes their entry line; the 4 reverse rows (`(foo\B)`, `foo\B`, `\Bfoo\B`, `\bfoo\B`) have a bounded block (`scan_run_length = 1`) and keep it. The critic reports 6 losing / 1 kept / 4 "already 0"; my count is 7 / 4 / 0 (derived from block shape, no twin, so mine could miss a bounded head elsewhere in the seed family). Either way check (2) would go red on at least 6 manifest rows.
S227 (tests/mech/sabotages/S227_scan_edge_entry_s0_only.sh): about the entry dispatch, witness `foo\B` (bounded, reverse) survives; its header says on `\b\w+\b` "the answer STILL does not move". S764/S780: their `SAB_BEFORE` text is verbatim the `rev->entry_head = (sn >= 0 && d->st[sn].scan_span != 0) || (snl >= 0 && d->st[snl].scan_span != 0);` lines, so the build must re-anchor them (mentions of seedhead: S227 text only "entry"/"seeded head"; none uses the word `seedhead`). The subject (grep S227|S764|S780|run_scan_edge_census) names none of them.

## DESIGN-1 (row 4's byte prior declines the runs the relaxation admits)
Verdict: HOLDS (core), with one nuance.
Recomputed from src/core/findings_table.inc `pcrec_find_tbl_counts_0` (256 counts) with python3 -I (verify/m.py): `\d` 10 bytes p=0.075 E[k]=0.08; `[a-z]` p=0.663 E[k]=1.97; `[\w.$]` 0.817 (4.47); `[^]]` 0.998; `\s` 0.138 (0.128 without \n); hex 0.305; `o` 0.050. Threshold k*/(1+k*) = 2.3/3.3 = 0.697. So row 4 (E[k] >= k*) declines `\d+-` and `foo[a-z]*bar`'s `[a-z]*`; admits `[\w.$]+` and `[^]]*`.
`id=\d+;`: `build/pcrec -p rx --features all --emit-main --pattern 'id=\d+;'` -> `#define RX_DFA_SCAN_EDGE "none"` (no edge today, no edge block in C). The "split-exit one-state digit self-loop" shape is by reasoning (exits `;` and dead), not separately verified.
utf8: findings.md §2 paragraph 7: "under `-e byte` every reader reads its rates and under `-e utf8` the `byte-rate` answer is NONE"; §5 paragraph 3 `query=none` under utf8 default. Subject l.403-404: a missing input makes its row transparent -> row 4 falls to row 5 (NONE).
Nuance: subject l.379-380 ("What the relaxation admits") describes the UNPRICED relaxation; the subject separately counts the priced-in subset (l.581, 53/18/13 forward/reverse/anchored). The critic's point that the examples are then declined by row 4's own price stands; calling the line wrong is a stretch.
Incidental probe: `\d+-` and `foo[a-z]*bar` stamp "range" today but carry no forward edge; the edge is an inline reverse-machine loop (`while (... subject[rewind_position - 1] - 48 <= 9u)`), consistent with the subject's forward-machine framing.

## DESIGN-2 (rows 3/4 omit (6), (8), the s0 refusal)
Verdict: PARTLY.
Subject rows (l.423-426): row 1 "preconditions (1)-(8)"; row 3 "(2), (3); (7) at selection"; row 4 "(2), (3); (7); AND priced in". The subject l.296-304 and 356-372 say the corrected twin keeps (6) and (8) and that the emitter's `dfa_form_derive` refuses loudly (emit_dfa.c:12745-12757) if (8) is dropped. So the row text omits (6), (8): HOLDS as a text gap.
scanedge.c: (6) `if (viewtgt[s]) { ... }` (~lines 396-412 in the collect loop), (8) `if (prefilter_reseeds && seedtgt[s]) continue;`, s0 refusal in the unbounded branch: `if (nx == s) { if (s == d->s0 && !a) continue;` with the comment "ONE SHAPE IS REFUSED HERE AND IT IS THE UNANCHORED WRAP'S OWN ... would spend one of this machine's four slots re-skipping bytes the prefilter has skipped". That refusal is not numbered, so row 1's "(1)-(8)" does not name it either.
Consequence claim: "row 4 as written matches s0 on every unanchored machine" is true of the row's TEXT only; in code the refusal sits in the same `nx == s` branch and would stay unless someone removes it. The critic's "second slot" point (rule lives in `collect`'s `continue`s, not the row) is a fair design observation. Severity doc, not an answer risk.

## DESIGN-3 (card collides with existing beta/f/xover cards)
Verdict: HOLDS (collision); PARTLY on "same quantity".
measure_store/zen4-grid1/1/set.tsv cards section: line 25 `kit	beta	1	form;kind;shape	ratio ...`; line 30 `kit	f	1	form;kind;lenclass	walkbytes ...`; line 34 `kit	xover	1	form;vs;kind	bytes	derived`. Rows: lines 102-104 `kit.xover.{A1,S1,V1}.WALK.DFA_SCAN	bytes	...	derived	interp-log2`; line 12 `unit_key	kit.beta.WALK.DFA_SCAN.r1e0c0`. measure_store/DEFAULTS = `idk zen4-grid1@1`.
docs/spec/measures.md:83 [2.2¶2]: "A set holds at most one card per `owner.quantity`." The subject's card (l.612-632) declares `kit beta 1` dims `form; dispatch; dir`, `kit f 1` dims `form; dispatch; dir`, `pcrec walk 1`, derived `xover.ADVANCE.<form>.<dispatch>`; "added to the canned grid" = this set would hold two `kit beta` cards. Derived key token order also differs from the existing xover dims (`form;vs;kind`). Unless it is a different set (the subject says "canned grid" and names the card `kit-advance@1`, which is ambiguous), the collision holds.
"Same quantity": the existing xover rows are kit search forms (A1/S1/V1) against the DFA walk; an ADVANCE edge-vs-table-step crossover is analogous in algebra (f/(1-beta)) but is a different comparison, so "already holds this same quantity" is overstated. The D146/D157 point (a STAY-vs-EDGE `dispatch` dimension under a kit card is a pcrec method fact) is design opinion; the card text does put `dispatch (EDGE, STAY)` in the kit rows.

## DESIGN-4 (cap ranking by prior mass)
Verdict: HOLDS (conditional on a machine with more than 4 unbounded candidates).
Subject l.441-448: "among unbounded heads, rank by descending prior mass p ... can only reorder edges; it cannot decline a measured win ... matters only once the relaxation lands". scanedge.c:543-553 `chain_cmp` today: unbounded first, then `nmembers` descending, then lower head, then cls. Cap: limits.def:395 `PCREC_MAX_SCAN_EDGES, 4 ... "awaiting a measured re-choice"`.
Masses (m.py): `\s` 0.138, hex 0.305 (both measured wins), every row-4 admit has p >= 0.697 by construction, so descending p ranks the wins last. Reorder at a cap IS a decline for the 5th: the subject's own census line 584 `… displaced a HEAD edge at the 4-slot cap | 2 | 3`. utf8: the key is NONE (findings.md §2 paragraph 7) and the subject names no rank then.
Not run: whether `\s+$` or hex machines actually exceed 4 unbounded candidates.

## DESIGN-5 (stay rule vs p > 0.70)
Verdict: PARTLY.
Quoted: emit_dfa.c:5043-5044 "pick up to 4 states ... that stay put on >= 192 of 256 bytes", `int best = -1, bestcnt = 191;` (5069), rank by `stay` (byte cardinality, 5112-5115). D13 (decisions.md:357-391): reverted M2.10, "~27% SLOWER", "Mechanism unknown and deliberately left so rather than guessed at: the suspicion is that a backward byte-at-a-time skip loop loses to the reverse table walk ... Untested."
Masses under the DEFAULT byte prior (m.py): `[^a-z]` 230 bytes p=0.337 (E[k]=0.51); `[^\w]` 193 bytes p=0.193; `[0-9a-z]` 36 bytes p=0.738 (E[k]=2.82). Under the byte prior the stay rule and p>0.70 disagree both ways, as the critic says.
But the subject's own wording is "uniform prior": l.241 "the stay rule's 192/256 = 0.75 is a cardinality version of the same inequality", l.695-698 "Under this break-even it is the inequality p > 0.70 with a uniform prior". With a uniform prior p = bytes/256: threshold 0.697*256 = 178.4 bytes vs 192; `[^a-z]` (0.898) and `[^\w]` (0.754) are admitted by both, `[0-9a-z]` (0.14) declined by both. Movers are only sets of 179-191 bytes. So (a) is refuted as stated against the subject's text; it holds against subject l.469 ("retired into the same priced row", i.e. row 4's byte-rate row), which is ambiguous.
(b) HOLDS in substance: subject l.631-632 itself says the STAY-dispatch arm is measured "so the generic-path compare cost of STAY is in the row", i.e. not a per-entry F; Q4's "it is the inequality" does not reflect that.
(c) The subject says M2.10's regression "is what the inequality predicts" for a 2-byte stay set; the inequality (low mass) does predict decline, and D13 records only the measurement plus an untested suspicion. Overreach in tone, not a contradiction of a recorded fact.

## DESIGN-6 (G2 arithmetic)
Verdict: HOLDS. Subject l.395-396: "`\s+$` at <= 0.35x of pre-SET instructions on `t-trim-match-60k`". Table l.151: `\s+$` ... (ins; cycles) set `369k; 120k`, single `922k; 412k`. python3: 369/922 = 0.4002, 120/412 = 0.2913. Summary item 3 (l.63): "-60% instructions, x0.29 cycles". G2 as written fails on HEAD's own numbers; 0.29 is cycles.

## DESIGN-8 (two missing-price verdicts; card says "row 3"; no ADVANCE row)
Verdict: HOLDS for (b), (c); PARTLY for (a).
(c): subject l.615-616: "It is added to the canned grid when row 3's trigger fires. Until then the rows are UNMEASURED and row 3 is transparent." Row 3 reads no data (l.524 "Rows 0, 1, 3 and the entry rule read no data"), and the rows that read the card are 2 and 4. Holds.
(b): subject l.403-404 "A missing one makes its row transparent". Row 2 (l.424) is `TRANSPARENT while either is NONE, which today is always` -> falls to row 3 (ADMIT). Row 4 transparent -> row 5 (NONE). `grep -c ADVANCE measure_store/zen4-grid1/1/set.tsv` = 0 and DEFAULTS = `idk zen4-grid1@1`, so k* is missing today, row 4 is transparent, and the relaxation admits nothing until a set with an ADVANCE row (and a DEFAULTS move) exists. Q3 (l.688-694) says the P1/T4 build "supplies the measured cell"; bench ask (c) (l.646-648) says the card is owed only when row 2's or row 4's trigger fires; the ordering (card before enabler) is not stated. Holds.
(a): row 2's E[k] source is stated only for uniform-exit loops (`run-rarity`, which every resolution answers NONE: findings.md §2 paragraph 2); row 4 uses the byte-rate prior for split-exit. Whether row 2 also applies to split-exit loops (it says "one-state self-loop") is a reading question; the double slot is plausible but not demonstrable from text.

## DESIGN-10 (third member of an undeclared family)
Verdict: HOLDS on facts; the unification is design opinion.
emit_dfa.c:5063 `pick_skip_states(const Dfa *d, int exclude, int out[4])`, up to 4 (`pass < 4`), ranked by `stay` cardinality, floor `bestcnt = 191`, excludes `scan_span != 0` (5113). scanedge.c `chain_cmp` (unbounded, nmembers, head) and `PCREC_MAX_SCAN_EDGES` 4 (limits.def:395). decision_families_survey.md §3.1-§3.14 headings listed; `grep -i 'pick_skip|stay skip|stay set|chain_cmp|PCREC_MAX_SCAN_EDGES|self-loop'` finds no row. Cross-check: plan row [PRIOR-COST-UNIFY] (plan.md) already lists `pass < 4` (`emit_dfa.c:4747` there) and `MIN_SCAN_CHAIN` among a dispersed family, so the family is known to the plan but the stay/edge selector pair is not in the survey.

## COST-3 (abi number and reader grep)
Verdict: HOLDS. `git rev-parse HEAD` in the review tree = 02a05485148faadf96910332e4386ba0ac9e3268; emit_dfa.c:55 `#define PCREC_ARTIFACT_ABI 92`. The critic's grep (`(abi|ABI)[^0-9]{0,12}\b92\b|ABI_EXPECT=92|!= 92|RX_ABI_H 92` over src tests docs/spec lib scripts) returns 8 lines in 6 files: src/gen/emit_dfa.c:55; tests/mech/sabotages/S283_...sh:35 (figure comment); S693_abi_not_bumped.sh:81 (`SAB_BEFORE='#define PCREC_ARTIFACT_ABI 92'`); tests/codegen/run_recursion_identity.sh:1286 (FILEPIN comment); docs/spec/match_api.md:211,212,215; tests/codegen/run_codegen_tests.sh:3208 `ABI_EXPECT=92`. Beyond the grep: docs/dev/history/abi_changelog.md:26 "`rx_info.abi` is `92` on every artifact today", so ~8 files holds if abi_changelog and the cpset comment are counted. "Other lanes may hold a provisional 93" is SUSPECTED in the critic's file; not checked.

## COST-5, COST-6 (plan rows)
Verdict: HOLDS (facts). Rows are indented in plan.md, not at `^- \[`; located by `grep -n 'LANDWALK-EDGEPRICE\]\|PRIOR-COST-UNIFY\]'` and read only their own lines.
- plan.md-91 `- [PRIOR-COST-UNIFY] STATE:blocked`; line 90 lists `MIN_SCAN_CHAIN` (`limits.def:392` there, 397 per the critic; drift) and `pass < 4` among eight further members of one dispersed byte-prior family.
- plan.md (LIST-TABLES row) `- [LIST-TABLES] STATE:not-started`, "UNSCHEDULED", "next: starts on Frank's word; no row-specific trigger recorded".
- plan.md-293 `- [LANDWALK-EDGEPRICE] STATE:not-started — p48's priced one-state relaxation on the walk's loops, as its own follow-up (r1 D11)`; status: "split out of stage 1 by review r1"; `trigger: stage 1 of [LANDWALK] landed and a card of its own shows the relaxation pays on the walk's loops`; line 293: "p48's SCAN_SITE_ROWS row 4 (split-exit, priced by k* about 2.3 B)".
So the plan places rows 2/4 + card as a follow-up of stage 1 (COST-6) and the subject's Q3 "IN the P1/T4 build" differs (the row was filed 2026-10-29, same day as the subject). COST-5's "D77 anti-pattern" is judgement; its facts (rows 0,1,3,5 re-spell today's behaviour, row 2 transparent today, card trigger naming row 3) are confirmed (see DESIGN-8).

## COST-8 (spellings of scan_span != 0; kill guard)
Verdict: PARTLY.
`grep -n 'scan_span != 0' src/gen/emit_dfa.c` = 9 lines: 5113, 12312, 12750, 12874, 12896, 12897, 13705, 13706, 13768. The critic's "11 times" counts 5310 and 12526 (`int span = ... scan_span`, locals) and 5388/5391 (`< 0` / `> 0`), which are not `!= 0` spellings. Entry subset (12874, 12896, 12897, 13705, 13706, 13768) = 6, as COST-1 says; 12750 is the (8) read-back in `dfa_form_derive`; 5113 is the stay exclusion; 12312 a fourth reader (known/kn_step-style helper).
scanedge.c:711-713 holds verbatim: `if (ch->span > 0) for (int c = 0; c < d->ncls; c++) if (pcrec_scan_has(hd, c)) hd->tr[c] = -1;` inside the take loop; the file header says the same ("dead is the one value every existing reader ... handles").
The "one DState fact" proposal is design; not evaluated further.

## SUSPECTED, skipped
- COST-7: nothing outside the denylist settles whether a plan row for the 192 floor exists beyond what is above; the D13/M2.10 warning at emit_dfa.c:5043-5053 and decisions.md D13 are confirmed.
- DESIGN-9: the raw r = 1..6 rows are in p48_evidence (denylisted). From the subject's table alone: "ins crossing r = 4 (105 = 105)" with F = 14, g = 13.0 - 7.1 = 5.9 gives k* = 2.37 on the linear model; whether r = 4 means k = 3 (total run includes the entry byte) is a convention the subject states in Summary item 4 ("crossing measured at a total run of 4"). The tension the critic sees exists under that convention (tie at k = 3 would need F = 17.7, not 14), but it cannot be confirmed here.

VERIFY COMPLETE
