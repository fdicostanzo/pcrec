# 2026-10-09 — FULL D6 panel on D156 locate × finish (docs/design/locate_finish.md, merge 57fe04ef)

Three read-only critics, session 102, at main 44466b8c (src unchanged since 525dec33):
**lfcrit1** (opus) exactness and the give-up surface against libpcre2; **lfcrit2**
(sonnet) start-table fit, checks, census reproduction and readers; **lfcrit3** (opus)
generality, simplicity, family, and unlocks. Frank, on lfcrit3: "i like how that
critic added extra stuff instead of just saying how it wouldn't work" (now standing
practice, memory `pcrec-critics-propose-unlocks`).

**What held:** every file:line in §2-§5. The census re-ran byte-identical
(summary.txt; corpus rows 5,431 = `CENSUS_BLOCKS` pin). F-1, F-2 and F-3 are real
at main. D156's frame is upheld by all three lenses; no shipped mechanism falls
outside it.

Dispositions are the manager's and are applied by the revision lane. Status is
ACCEPTED unless marked otherwise.

## lfcrit3 — generality / simplicity / family (LF-G1..G14; 0 blocker, 8 major)

| id | sev | finding | disposition |
|---|---|---|---|
| G1 | MAJOR | CAND and LOWER are one type. Their obligation cells are identical; "one try then re-locate vs attempt loop" is a RE-ENTRY POLICY the RETRY slot already chooses. §4.5's superset locator hands LOWER, contradicting "superset ⇒ at most CAND". | ACCEPT: merge; policy stays with RETRY/verifier resume; withdraw F-6 (D156 was right); degradation = superset ⇒ {LOWER, NOMATCH} |
| G2 | MAJOR | The six types are points of a product: start interval [s,t] + "s proven" bit × end set D. UPPER has no pair, and the shipped CT_WINDOW (accepted by VERIFIER, handed by no row) is never disposed of. | ACCEPT: state O1-O10 and totality on the two axes; keep enum spellings in code; drop ENDSET's \|D\|≤2 cap; map or delete CT_WINDOW |
| G3 | MAJOR | Finishers are (action × engine hat): report, nomatch, verify-at s, search-from s; DFA or VM hat by route (D124 lens 5, CandPf.emit/emit_vm precedent). F6 is F7 entered at its loop head. | ACCEPT: four rows, hat by route; vm-* rows go |
| G4 | MAJOR | FINISH duplicates what exists. (a) cand_nodes' VERIFIER/LOOP/CALLER ARE the finisher set; after L0 "verify a CAND" would have two homes. (b) dfa_matches[] (axis G) IS FINISH for match-here, with a deny and anchored_ok; match-here's locator is a trivial `caller` locator. | ACCEPT: promote the nodes into FINISH; FOLD dfa_matches[] (the last entry-point axis outside the table; axis J's C3 precedent); F-2 dissolves |
| G5 | MAJOR | Q1, slot vs separate table, with consequences (listing per take-set, trace hand field; separate array duplicates walk/listing/trace and splits the typed-edge check). | ACCEPT: a slot block keyed (route, hand), justified by G4(b)'s real choice |
| G6 | MAJOR | "Next locator in table order" is a fallback ladder inside a first-match table, and is contradicted by every concrete case (the target is always the route's fallback/composite). | ACCEPT: relocate names the route's fallback LOCATE row; progress = strictly raised lo (O9); same-locator re-entry is a separate edge with its own progress obligation |
| G7 | MAJOR | Posture is not a function of the pair. (a) W1 on CR_VM is NEUTRAL on exact hybrids and ONE_WAY on VM-only/collapsed, so the cell is a JOIN. (b) WIDTH `ceiling` declared ONE_WAY while the same-shape PRESENCE verdicts read NEUTRAL. (c) `handoff` CG_FIXED is a ruled CONTRACT (K82 Q10) that derivation would erase. (d) Declared-vs-derived shares a source. (e) DFA routes are N/A, not NEUTRAL. | ACCEPT: two columns, a derivable classification (join over covered artifacts) and a declared, checked obligation (FIXED); independent control = a give-up differential (default vs deny over swept budgets, K82h §3.1a's 35 blocks + VM-only end-window witnesses) |
| G8 | MINOR | A3/A4/A5 are one `composite` row with a hat by route. A1 `empty` and WIDTH `ceiling` are one "nothing fits → NOMATCH" family. | ACCEPT |
| G9 | MINOR | Stage 2's `locate-decides` is G1 `dominated` with a new dominator: add a PRESENCE→LOCATE read. "LOCATE first" holds per body, not per artifact. | ACCEPT |
| G10 | MINOR | Stamp rule: cite DD-13c; classify DFA_SCAN readers that use "unanchored" as a MACHINE proxy; keep D-2's census and sabotage separable inside L2 so a red bisects. | ACCEPT |
| G11 | MINOR | Stage 1's `fit.chosen == ENGM_DFA` conjunct is one of the reads §3.3 centralizes: spell it as a read of cand_finish_of. | ACCEPT |
| G12 | D77 | Cut L0 to {LOCATE {empty, composite}; cand_finish_of replacing the ten reads; F-3 + F-1 data corrections; the dfa_matches fold}. FINISH rows with no choice wait. | ACCEPT |
| G13 | MAJOR (unlock) | §4.5's relax(P) is a SOUND general erasure for A_BREF. Run forward, it is a superset prefilter for every acyclic-backref VM-only artifact (backrefs_design §7.4's chartered prefilter, no E2 gate; VM-only search measured 6.2-130x slower). | FILE as a candidate row with trigger: census of VM-only backref artifacts where relax(P) is acyclic and the N7 hat does not narrow, plus one bench backref cell paying the attempt loop |
| G14 | unlocks | (1) rev-end = rev-inner with landmark = end: a seed-SET reverse walk; `(?m)$` seeded at every '\n' + n. (2) A fixed-width RECOVER row, start = end − W. (3) A forward regular-prefix locator over P·Σ*. (4) A subset locator handing UPPER+EXISTS (BOONIES-class). | FILE each with its trigger (in the finding) |

## lfcrit2 — table fit / checks / census / readers (LF-C1..C12)

| id | sev | finding | disposition |
|---|---|---|---|
| C1 | HIGH | FINISH totality cannot be evaluated: FINISH is keyed on the ENTRY route, while LOCATE rows hand from BODY routes (a hybrid's body asks CR_DFA/ATTEMPT, its FINISH runs CR_VM). F-3's fix is not data-only (exactness/`mrl_win` is a VM fact RECOVER's CandSel lacks). F3 reads dfa_matches[], but ATTEMPT's verify does not use that machine, so under `-fno-anchored-dfa` ATTEMPT's CAND has no finisher. §3.2 maps match-here CAND to F4, which takes only ENDSET\|LOWER. | ACCEPT: key totality on (locator route, finisher route); split the verify row (ATTEMPT always / DFA gated on unwrapped); settle match-here's type. G1/G3/G4 reshape most of this |
| C2 | MED | A5 `trivial` would fire on hybrids (gate on `!pcrec_artifact_has_dfa_scan`). "Next locator in table order" needs a second walk cand_select cannot do. E-FL makes the first cycle in `succ`, and the self-check tests cycles only in the reads graph, so O9 is unchecked. | ACCEPT (with G6, G8) + a progress check on succ cycles |
| C3 | MED | L0 is not "0 re-aims": S566 anchors a line L0 rewrites (`:9768`); S222 sits beside the A1 readers. `pcrec_emit_dfa_engine`'s `empty` decision lives inside two emitters. | ACCEPT: derive the re-aims (start_table edit-set method) |
| C4 | MED | run_cand_oracle.sh has no UNREACHED allowance; F6/F3-ENDSET have no producer at L0, so L0 goes red. | ACCEPT: add a declared-unreached allowance or defer the rows (G12 defers them) |
| C5 | MED | L0 plant 5 (declared vs derived posture) is circular; no plants for dropping `.hand`, the F3/F4 order, or reverting F-2; plant 3 is caught only if F-3 lands; `.hand` mandatory-or-ignored unstated. | ACCEPT (G7's differential is the independent control) |
| C6 | MED | Stamp rule wrong for REQ_*: REQ_WHY's four closed tokens would read "emitted" with no pre-check. DFA_TABLE/DFA_UNIFORM_FOLDS/DFA_SCAN_EDGE/orientation are ignored (the forward machine is absent under form C). revend.md §5.2 vs this note conflict on DFA_START/END_WINDOW, and neither records the supersession. | ACCEPT: a REQ_WHY token, decide every downstream stamp, record the supersession in both notes |
| C7 | MED | Missed reader OUTSIDE the repo: pcrec-bench testees/pcrec/adapter.py:699-705, :802-806 (closed dfa_scan/dfa_start vocabularies), plus report.py and tools/selfcheck.py. D-2's ruling asked for a bench adapter note. | ACCEPT: L2 deliverable = an `[inbox]` adapter note + window handshake |
| C8 | LOW | §3.3's grep misses `pcrec_artifact_has_dfa_scan` (12 callers; :3119/:3193 are the rx_info.scan/search_form mirrors); :10708 is undispositioned; the VM class is 15 lines, not 16. | ACCEPT |
| C9 | LOW | Stale spec citation (match_api.md:4686-4703 is now the VM stamp block; DFA_START is at :788-796, :4829-4839); five DFA_SCAN value tables need the fourth value. | ACCEPT |
| C10 | LOW | C3 control is one-sided (the converse holds: 22 rows, all utf8); the unbounded stage-1 class has no control beyond a copy of ew_walk; the exact/superset classifier has none — `RX_VM_RESEED "exact"` is independent (759/1,493 hybrids, 0 disagreements). | ACCEPT: add C4 to analyze.py; a two-sided C3 |
| C11 | LOW | `locate-decides` reads `cand_route_of`, which defaults to DFA when job->engine is unwritten; 275 end-pinned VM-only artifacts would defer to a walk that doesn't exist. | ACCEPT: gate on `pcrec_artifact_has_dfa_scan` |
| C12 | LOW | CT_WINDOW not reconciled with SPAN; no declared-listing file for the `locate` axis; F1 `nomatch` has no producer on CR_VM. | ACCEPT (with G2) |

## lfcrit1 — exactness / give-up surface (LF-E1..E12; 1 HIGH, 4 MED, 3 LOW, 4 UPHELD)

Probes in the critic's scratchpad: a stage-2 hybrid twin (`mkhyb.py`, form C inside the hybrid's inlined prefilter), a window→captures→libpcre2→find-all checker, a 45-pattern ASan battery, rev-inner and relaxation probes.

| id | sev | finding | disposition |
|---|---|---|---|
| E1 | HIGH | §4.6 rev-inner (AND where_to_start.md §2.2 step 1, D151): "CAND per occurrence; a failed verify moves to the NEXT occurrence" is UNSOUND when S back-references a group in P — exactly rev-inner's VM-route population. The verify at s*(j) can fail while a larger s in starts(j) succeeds. `(a+)X\1` on "aaXa": libpcre2 (1,4), the tactic NOMATCH. A second witness returns a LATER match. 82 wrong / 82,903 (1,199 gated cases with a backref in S); the `lowerbound` form 0 wrong. The study's published 0/129,222 reproduces, so its population was too thin (K35). | ACCEPT: precondition G4 (S holds no reference into P's groups, backref or `${}`); otherwise type LOWER(s* of the first non-empty occurrence) and finish with the attempt loop. CORRECT where_to_start.md §2.2 step 1 in the revision |
| E2 | MED | §1.4 O4: "subsequence, no ceiling looser" admits a TIGHTER ceiling, and a ceiling below the priority end is a WRONG ANSWER, not a posture difference. `(\s+){2}$` on "  \n" gives g1 (1,3) for (2,3); 2,188 + 4,010 wrong / 27,884 under control tien1. | ACCEPT: O4 = a subsequence of (start, ceiling) PAIRS, plus an explicit obligation that the ceiling is ≥ the priority end at s (D51's unsound direction) |
| E3 | LOW | The named F6 witnesses are greedy, so max(D) IS the priority end and F6 never matters (0 / 27,884). Only LAZY ties exercise it: `(\s+?){2}$` moves the window on 2,188-3,282 cells, with captures equal and the give-up threshold equal (19 budgets × 5 lengths). The give-up hazard is argued, not witnessed. | ACCEPT: keep F6; re-aim the sabotage witness to `(\s+?){2}$` (window compare); mark the hazard unwitnessed |
| E4 | MED | §4.5's "52-byte cls_casefold set in byte mode" is stale since K94: under `--ucp` byte a caseless reference folds Latin-1. `(\xe9)(?i)\1$` --ucp on "\xe9\xc9" (0,2); the ASCII-closed relaxation rejects it. | ACCEPT: close under the REFERENCE's own compare fold (ascii / latin1 / utf8 simple fold) |
| E5 | MED | DUPNAMES: A_BREF.refs[] is a SET. `(?J)(?:(?<n>a)\|(?<n>b))\k<n>$` on "xbb" (1,3); relaxing the first member only rejects it. | ACCEPT: relax = UNION over refs[] |
| E6 | MED | The closure must be taken on the LOWERED positive set: re-lowering the copy under caseless mods folds before negation and SHRINKS negated classes (`([^b])(?i)\1$` on "BB"). | ACCEPT: closure = S ∪ fold(S) on the bitmap/interval set, never a re-parse |
| E7 | LOW | "Cyclic reference ⇒ Σ*" misses a recursive CALL inside G_N and A_VAR `${v}` (no relax at all). | ACCEPT: A_VAR → Σ* or decline; the cost gate excludes every Σ* source |
| E8 | LOW | Relocate (F4/F6, "search_from = s") moves `\G`'s reference point. REVEND declines `\G`; rev-inner does not. `(?:\G\|b)(b?)\w*X` on "-bbX": g1 (2,3) from 0, (1,2) relocated. | ACCEPT: relocate hands `lo` and leaves `\G` on the caller's search_from (K82 Claim 2′), or every relocate producer declines `\G` |
| E9 | UPHELD | Stage 2 NEUTRAL: walk vs shipped prefilter on 48 hybrids (exact, clamped, ties, views, `\K`, `-i`, supersets, collapsed, X1, utf8), every string to length 6-7 at every lo: 0 / 5,199,120 window diffs, 0 capture diffs, 0 / 4,565,716 vs libpcre2, 0 / 719,283 find-all, ASan clean; controls fire. | — (the strongest evidence in the round) |
| E10 | UPHELD | O8: every ew_walk arm keeps the end pin under each erasure; X1 is load-bearing on stage 2 too (4 lookaround shapes SEGV without the skip). | ACCEPT the rider: the X1 sabotage row gets a hybrid witness |
| E11 | UPHELD | Tie table T1-T3 / dfa_matches[]: 18 form-C twins, 0 / 1,682,892 cells, 0 vs libpcre2. F-2 confirmed. | — |
| E12 | UPHELD | §4.5 as a start bound: with the true closure, 0 violations over 3,000 generated patterns (~1.08M checks, byte and UCP); select_engine.c:877's assertion-keeping copy gives 117 violations, so "not that erasure" holds; ONE_WAY is the right direction. | — |

## Verdict

**The frame holds**, and stage 2's NEUTRAL claim is the best-evidenced result of the round (E9).

The note is NOT build-ready. Its type and finisher sets shrink to the general form (G1-G4); FINISH folds in `dfa_matches[]` and the existing graph nodes; totality keys on (locator route, finisher route) (C1); posture splits into a derivable join and a declared contract with a give-up differential as its control (G7/C5). E2 corrects a wrong-answer hole in O4. E1 is a real unsoundness in the filed rev-inner design and in where_to_start.md §2.2.

Next: revision lane `locfin2` (rev 2, a disposition table by id), then a focused re-check by two critics, one of them with the generality/unlocks lens.

## Filed from this panel (candidates with triggers, not builds)
- G13: the relaxed-backref machine run FORWARD, as a superset prefilter for VM-only acyclic-backref artifacts.
- G14 (1)-(4): the seed-set reverse walk (`(?m)$`), fixed-width RECOVER (end − W), the forward regular-prefix locator, the subset locator (BOONIES).

## Frank's §7 questions — status after the panel

The critics' judgments are recorded in the findings above. The revision restates the
questions under the revised model. Q1 (slot vs table) is answered by G4/G5; Q5
(posture) is reshaped by G7.
