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
| C9 | LOW | Stale spec citation (match_api.md §6.3.4¶11, was :4686-4703 -- that range is now the VM stamp block; DFA_START is at §3.1¶21 and §6.3.4¶11, were :788-796, :4829-4839); five DFA_SCAN value tables need the fourth value. | ACCEPT |
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

---

# RE-CHECK of revision 2 (lane locfin2, merge 1ec2d53b)

Two read-only critics: **lfre1** (opus; soundness + table fit) and **lfre2** (opus; generality, simplicity, family, unlocks).

## lfre2 — generality / family / unlocks (LR-G1..G14)

| id | sev | finding | disposition |
|---|---|---|---|
| LR-G1 | MAJOR | G3 landed halfway: FINISH has 7 rows (three verify-at rows, two search-from rows, split by hat and machine) where 4 do (nomatch, report, verify-at, search-from), each with its hat from the finisher route. Row availability becomes a predicate on the route's machines (adfa on CR_DFA iff built; the ATTEMPT machine; the VM). `-fno-anchored-dfa` then denies what it removes (the adfa build). F-11/Q7 is one visible conjunct kept for L0's no-mover proof. Do it at L0, where the fold already happens. | ACCEPT |
| LR-G2 | MAJOR | The 5-value shape key does not cover the product, and `p` ("a match starts at s") cannot say "a match exists in I" (VMSEED stage 4's window, G14(4)'s EXISTS). Two type vocabularies remain (CT_* inside, shapes at the boundary). | ACCEPT: `(I, e, D)` with e = "some match starts in I"; key FINISH on the existing CT_* bits (names kept as listing aliases); AT = CT_LOWER\|CT_UPPER at a point |
| LR-G3 | MAJOR (latent) | `cand_lang_exact` / `pcrec_vm_prefilter_window` decide exactness from a LIST of known erasures (atomic, look, collapse) and never test BREF/VAR. G13's relaxed prefilter would read EXACT: the boundary hands SPAN, and mrl_win uses the window end as the ceiling (the atomic-groups 122-cell class). (d′) at emit_dfa.c:7361 reads the same function. Also, C4's "independent RX_VM_RESEED" reads the same function; the independent side is the census's classifier. | ACCEPT: the body's lowering RECORDS its applied erasure set; exact ⇔ empty; all four readers read it; a precondition on G13; fix the C4 wording |
| LR-G4 | MAJOR (forest) | F-9, F-10, the `empty` off-path conjuncts (8 `dfa_engine_is_empty` callers), has_dfa_scan's 12 callers, the four membership spellings, cand_finish_of and §5.1's per-stamp edits are ONE family: what the selected path USES. `empty` is the first path-changing locator, rev-end the second, [START-LANDING]'s rows the third and fourth. | ACCEPT: each row declares `.needs` (machines F/R/A/ATTEMPT/VM + slots); the path = closure over the selected rows; membership = union of needs ∩ what built; every site reads it; "off-path ⇒ absence" becomes ONE generated stamp rule. Widen L2.0 to build it (form C dropping F is the D77 trigger); write L0's route functions as reads of it |
| LR-G5 | MINOR | [GIVEUP-DIFF] largely exists: test-axes' GIVEUP1 relation (tests/axes/run_axes.sh:1270-1320) is default vs every deny over the corpus. Missing: direction (the allowance ignores which side gave up), a budget ladder, per-row witnesses. F-1's PRESENCE half is already witnessed (64 -fno-req-byte keys, 22 -fno-start-set); W1's is not. | ACCEPT: make GIVEUP1 direction-checked from the derived classification + a ladder arm; construct W1's witness; no new section |
| LR-G6 | MINOR | REQ_WHY "locator" re-creates the parallel spelling G9 removed. | ACCEPT: ask PRESENCE in both stages; `u.locate.whole` selects `dominated`; REQ_WHY stays 4 tokens |
| LR-G7 | MINOR | CandSel.lroute has no reader, and its 0 default means DFA (C11's shape). | ACCEPT: drop it until a predicate needs it |
| LR-G8 | MINOR | F3's `!dfa_engine_is_empty` exists because `caller` is not composed with the body's static NOMATCH. | ACCEPT: compose them, drop the conjunct; name it as an L0 carve-out (one of LR-G4's off-path conjuncts) |
| LR-G9 | UPHELD | The posture split is clean: rev-end, relaxed-reverse and rev-inner each fill the classification with no new column. Note: undeniable rows' control is the window-identity twin; stratify by L0's derivations + LR-G3's erasure set. | ACCEPT the notes |
| LR-G10 | UNLOCK (trigger MET) | [START-LANDING] belongs in the composite's RECOVER slot: `pinned` (0-byte), `landing` (1-byte), `end-minus-width`, then `reverse-pass`. One row each; SPAN to FINISH unchanged; NEUTRAL on hybrids; R drops out of the machine set (LR-G4). G14(2)'s trigger is met by walk_survey K3. utf8 needs a fixed BYTE width. Ranks above REVEND (50.9 vs 30.9 ms). | ACCEPT: fold §7.3 into [START-LANDING] and record its placement |
| LR-G11 | UNLOCK | K4's fact-less form: a second LOCATE row `candidate-verify` (the ATTEMPT candidate loop with the unwrapped anchored machine verifying). | FILE with its trigger (a fact-less bench cell where reverse bytes dominate and the landing-hit rate clears break-even) |
| LR-G12 | UNLOCK | Match-here across three routes (F-11, K8's VM-route `_match` scan, the empty / -fno-anchored-dfa fallbacks) is ONE row under LR-G1. | FILE with K8's trigger (a long-subject match cell) |
| LR-G13 | UNLOCK | The bounded-interval hand (VMSEED stage 4's window, G14(4), a "match starting in [s,t]" entry) is AT with t>s, under search-from's filter. | FILE with VMSEED stage 4's trigger; the entry itself is BOONIES |
| LR-G14 | BOONIES | On superset hybrids the landing is already a sound LOWER without the reverse pass. | FILE (BOONIES) |

lfre2's §8 judgments are recorded in its message: L0 first, with LR-G1 and LR-G4 adopted there; stage 2 FILED; the stamp rule generated from the path derivation; one tuning.md preamble sentence with per-entry markers; the relaxed locator gets its own deny bit; rev-inner ranks below [START-LANDING] and REVEND, and its twin measures the LOWER form first; ATTEMPT match-here measured as the K8 family.

## lfre1 — soundness / table fit (LR-S1..S13)

Verdict: the model holds. L0 is NOT build-ready until LR-S1 is fixed; L2 is ready after L0 plus LR-S3/S5/S7. No further panel is needed: the manager checks each fix directly.

| id | sev | finding | disposition |
|---|---|---|---|
| LR-S1 | HIGH, blocks L0 | "At L0 the only FINISH asker is match-here" is FALSE. Three machine-membership readers call `dfa_match_is_unwrapped` (dfa_table_name :4466, dfa_scan_edge_name :4523, dfa_uniform_folds :4577), and they run on HYBRIDS via pcrec_emit_dfa_scan_stamps (emit_vm.c:11330) and the orientation block (:10870). Re-keyed to cand_finish_of (CR_VM on hybrids), they hit a NO-ROW selection on ~39 bench / 1,192 corpus hybrids (e.g. `(a+)b`). | ACCEPT. The fix CONVERGES with LR-G4: move the machine-membership derivation (L2.0's `dfa_machines_of`, generalized per LR-G4 as rows' `.needs` ∩ what built) INTO L0, ahead of the fold, so membership readers read the machine fact, never the FINISH selection. Add the three functions + :10870 to the edit set, with a hybrid witness |
| LR-S2 | — / MED | `cand_lang_exact`'s derivation CLEARED (every erasure classified; BREF/VAR/linked-call never reach a prefilter today). NOT cleared: C4 is plumbing (RX_VM_RESEED `exact` reads mrl_win, the same conjuncts), not an independent control. The window is consumed at THREE sites (entry, RETRY recompute 13261-13327, adaptive re-seed), and the projection must cover all three. | ACCEPT: relabel C4 as plumbing; name an answer-level control before L3 (E9's window twin vs libpcre2); the projection covers all three sites (and LR-G3's erasure-set record closes the latent hole) |
| LR-S3 | MED | O4 text CLEARED (libpcre2 confirms both witnesses), but applied inconsistently: §1.3 VM verify-at says "ceiling max(D) where clamped" (wrong on clamped hybrids), §1.4 says the opposite, §2.3 F6 takes no ENDSET. | ACCEPT: ENDSET never reaches VM verify-at; strike it from §1.3 and from the matrix's VM cell |
| LR-S4 | CLEARED / LOW | Progress as (lo, rank) has no witness against it. Residual: the shipped RETRY `exact` row runs after a FAILED SPAN verify, and the model has no F6 failure edge. | ACCEPT: add verify→RETRY or have L3's twin assert RETRY is unreached on exact hybrids |
| LR-S5 | CLEARED + NEW LOW/MED | E1/G4 cleared on the witness. NEW: DUPNAMES `(?J)(?<n>a+)X(?<n>b)?\k<n>` (libpcre2 aaXa→(1,4)): refs[] spans P and S, so a G4 reading "the ref is into S" passes and the per-occurrence verify returns NOMATCH. | ACCEPT: G4 = no member of ANY `A_BREF.refs[]` in S names a group of P, stated in both notes, as a CLOSED predicate over node kinds (callouts/conditionals fail closed when built) |
| LR-S6 | CLEARED / LOW | L0 re-aims reproduce byte-for-byte (6 re-aim, 18 + 98 re-run); the 3 unresolved rows are outside the family. Gaps: LR-S1's sites; the boundary trace beside :13405 is S88/S141's anchor (add emit_vm.c to the edit set and re-derive); `hand = BOUNDED` vs `AT`; the `(\w+)\1` witness assumes a VM LOCATE ask no item places. | ACCEPT |
| LR-S7 | MED | pcrec-bench tools/selfcheck.py DOES pin the vocabularies (`dfa_start: reverse-pass` at :3705-3707 and :3729-3731, exactly L2.1's attempt-start movers; `dfa_scan: unanchored` at :3552-3554). | ACCEPT: the L2 inbox note names them as known movers |
| LR-S8 | LOW | F-9 undercounted (compile.c:2381, emit_dfa.c:10713). §3.3 misses compile.c:229 (`build_anchored_dfa` reads the F3 deny too, so "the deny moves with its row" is half true). | ACCEPT (LR-G4's derivation absorbs them) |
| LR-S9 | — | F-10/F-11 REAL; F-10's spellings are LR-S1's readers, so L2.0's work must precede the fold. | ACCEPT (same as LR-S1) |
| LR-S10 | LOW | match_api.md §6.3.4¶2 (was :4731)'s machine-proxy sentence is ALREADY false on `pinned` artifacts (stamp "unanchored", no reverse machine). | ACCEPT: the spec hunk is owed independently of rev-end, so file it to land with L0 |
| LR-S11 | LOW | [GIVEUP-DIFF] reaches only deniable rows; RETRY exact/clamped/anchored are undeniable by a ruled contract (emit_dfa.c:8331-8345). | ACCEPT: `.contract` carries those rulings too |
| LR-S12 | LOW | [ART-SIZE] drop rung SDR_NO_ANCHORED turns rev-end T2 into T3, which EMITS the forward machine form C dropped, so dropping can GROW the artifact. | ACCEPT: the drop rung gets a rev-end clause |
| LR-S13 | LOW | The 5-value key is partial (VMSEED's window); AT's I is a request filter (never degrade it); F6 id reused across revisions. | ACCEPT (LR-G2 resolves the key; rename the id) |

## Re-check verdict

**Both critics converge on one structural change.** The machine and path derivation (LR-G4's `.needs` closure ∩ what built) moves INTO L0, ahead of the `dfa_matches[]` fold. That fixes LR-S1's blocker, absorbs F-9/F-10/LR-S8 and generates the stamp rule. Add LR-G1 (four FINISH rows with route hats, done at L0), LR-G2 (key on the CT_* bits with an `e` bit), LR-G3 (a recorded erasure set), and the text fixes above.

Next: revision 2.1 (lane `locfin21`). The manager checks each fix directly; no further panel (lfre1's recommendation, accepted). Then Frank's questions, restated.
