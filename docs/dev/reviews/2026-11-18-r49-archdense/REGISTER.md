# CRITIC REGISTER: archdense (2026-11-18, architecture mode)

## Findings

### REGISTER-1 (CONFIRMED; doc; effort S; blast: the register-lookup record only)
Roadmap areas H-ABI and H-COUNTS match the feature and have no disposition in "Register rows looked up" (note lines 125-147).
- Note: line 261-262 "The abi event: the emitted retry text moves, so this is an abi bump with readers found by grep (D76/D94)"; lines 257-260 list the pins to re-aim. Row 12 is cited only as A-SEAM, A-PLAN, H-FLAGS, H-LADDER (lines 139-141).
- Roadmap at T, H-ABI: "Ride-along triggers. Every byte-moving change; [STAMP-REVIEW]; [IFACE-PUSH]." and H-COUNTS: "every change that moves a pattern's strategy re-pins them" (its pins include `tests/registry` counts and the codegen stamp manifests). The roadmap's own replay of [REQRUN-VM] (the feature's predecessor on the same rows, section 3 table) lists "abi 90 -> 91 and its readers (H-ABI ...)" and "startset 3, codegen 5, axes, registry and memfn-reach pins (H-COUNTS ...)" as that change's undeclared crossings.
- Repro: `grep -c -E 'H-ABI|H-COUNTS|A-HYB|H-SITES|A-READS' R0/R/subject/dense_hit_arch.md` prints 0; `git -C /home/pcrec/projects/pcrec show 57fcb5737:docs/design/stream/roadmap.md | grep -n 'Ride-along triggers. Every byte-moving'` hits H-ABI.
- Rule: architecture.md line 635-638: "(1) grep this table for every file and function the feature will touch and for its plan tag; ... (4) a row that a note decides not to carry says why in the note". Row 12 makes the roadmap areas rows by reference (line 599-600).
- Fix: add H-ABI (rides: the bump is the feature's own abi event; readers by grep, D94) and H-COUNTS dispositions. The abi bump is already conceded in the note, so this is a missing row in the table, not a missing idea.

### REGISTER-2 (CONFIRMED; design; effort S; blast: sites S5/S12 and the demotion half)
Roadmap area A-HYB (the VM hybrid prefilter window) matches S12 and the VM retry call and is not cited, although the note cites its ride-along trigger elsewhere.
- Roadmap A-HYB at T: "Today. src/gen/emit_vm.c: pcrec_vm_prefilter_window ...; the window protocol ..."; "Next step. P-c: the prologue (forward + reverse pair, window handoff, retry) as records ... byte-identical"; "Ride-along triggers. [OPT-HYB-RESEED-XCALL]; [ENG-THIN]; [K88-HANDOFF-DENSE]; ..."; "Prerequisites ... p1build merged (it edits pcrec_cand_finish_vm and the handoff row)".
- The feature's sites: S12 NEXT `handoff-reentry` is the hybrid prefilter's re-entry when `pcrec_req_site_in_prefilter` (emit_dfa.c: `return cand_finish_of(cx) == CAND_ROUTE_VM && req_scan_reentered(cx)`), and emit_vm.c:13482 reads it (`git -C /home/pcrec/projects/pcrec grep -n -E 'pcrec_req_site_in_prefilter|pcrec_emit_req_attempt_reentry' 57fcb5737 -- src/gen/emit_vm.c` gives lines 13482 and 13971). Neither the line-13482 site nor the hybrid's window is in the site map (C3 mentions only "the VM retry"), and the note names [K88-HANDOFF-DENSE] only in its sibling list (line 207: "concerns the entry, not the re-entry, and fits"), never as A-HYB's trigger with a disposition.
- Rule: architecture.md line 635-638 (steps 1 and 4, quoted in REGISTER-1).
- Fix: an A-HYB line in the register table (not carried because the remedy half leaves the prefilter byte-identical per scan-reentry-too leaning, or rides). Same for H-SITES (U1 changes a site's reply contract; roadmap H-SITES "Today" names `tests/memfn/site_manifest.tsv` and `c4_allowlist.tsv` as the per-site pins; U1's checks list does not mention them) and A-READS (S9 reads `CandNode.under/by`, which A-READS names as one of three world spellings); both may be NOT CARRIED with a one-line reason.

### REGISTER-3 (SUSPECTED; doc; effort S; blast: row 12/A-SEAM disposition)
The A-SEAM disposition's reason does not answer A-SEAM's trigger as written.
- Note line 139: "NOT CARRIED, reason: the remedy as architected changes no field of CandUse/CandRow (S3 AS-IS)."
- Roadmap A-SEAM at T: "Ride-along triggers. ...; [START-DENSE]; [REQ-PAST-LAST]; ..." and "Next step, byte-identical. Move the hand enum, CandNode and the row/hand types into a seam header (no logic, no emitted byte ...)". The trigger names the TAG, and the step is a pure move that does not depend on whether a field changes. The register's own step (2), line 636-637: "each matching row's remodel lands FIRST, as its own answer-identical unit (or joins the abi event in flight)".
- Also not fully true at T: S9 (note line 87) classes the deny column as "ROW (the rows' deny column)" and the demotion half changes `CandRow` deny cells and `CandNode.under/by` world reads, which are exactly the types A-SEAM moves.
- What would confirm: the manager's reading that a trigger fires only when the feature changes the area's types. If so the reason is fine for the remedy half only, and the note should say the demotion half is also covered by "joins row 15".
- Fix: state the real reason (the move is byte-identical churn in the same functions the remedy edits, and waits for no event; or "lands first, S, no-mover") rather than the field-change test.

### REGISTER-4 (SUSPECTED; design; effort S; blast: P1's event and the unit order)
P1's carrying event is, by the note's own general form, probably already met, yet the note says P1 "waits for its trigger".
- Note line 186: "P1 waits for its trigger." Line 193-196: "The bounded row may keep asking the leftmost hit for its move where that is worth it, and both rows ask the weaker fact for the stop." Line 249-250: "whether the per-hit form survives as a lever. If it does, S3 becomes WIDEN and A-SEAM's step, then P1, land first." P1's event (line 153): "a SECOND re-entry form selectable on any of the three (S3 becomes WIDEN)".
- Two question forms (leftmost for the move, weaker for the stop) in one loop is the note's own leaning; if the design follows the general form, the P1 event fires in the design step, and the order "A-SEAM move, P1, then feature" would be forced, not optional. The "Remodels that land first" section lists only U1 (line 186: "No other unit lands first").
- Rule: architecture.md line 636, step (2) (quoted in REGISTER-3).
- Fix: say which design answers fire the event, and list P1 (and A-SEAM's move) as "lands first IF the design keeps two forms", with the owner-visible consequence (size M), next to U1.

### REGISTER-5 (NOTED, not a finding)
Line 147 "This note recommends no deviation, so it proposes none." The feature lands a block rule for the resume question beside `adaptive-dense`'s existing block rule without unifying (note lines 13-14, 200-203). That is the guide's own allowance, architecture.md line 160-162: "where a feature must land beside a mechanism before its remodel, the allowance is his own implement-then-replace with an open register row", and P1 is that open row (columns present: remodel, shape (rule), where with commands C2/C3/C5/C14/C17, event, size/gate, deletes, status "open"). Small by the guide's test (line 156-157: touches one site family, no new reader of another unit's structure, no seam changed) EXCEPT U1 changes a seam, which is carried by its own unit, so no extra deviation row is owed. Optional doc improvement: say in line 147 that P1 is the implement-then-replace row.

## PROBED-AND-HELD


Rows checked against the note's sites (all at T, from the register copy `R0/R/subject/architecture_at_T.md` lines 594-646, and `git show 57fcb5737:docs/design/stream/roadmap.md`):
- 20 numbered register rows (1, 2, 3, 4, 5, 6a-6c, 7a, 7b, 8-20) read against S1-S13: the note's table covers 1, 2, 3, 6a, 6c, 7b, 9, 10, 12 (A-SEAM, A-PLAN, H-FLAGS, H-LADDER), 13, 15, 19. Rows 4, 5, 6b, 7a, 8, 11, 14, 16-18, 20 are not cited; I judged each not triggered: 4/14 (measure library, alternation fold: the feature reads the `whole_maxoff` fact via `req_handoff_k` and changes no fact, `git show 57fcb5737:src/gen/emit_dfa.c | sed -n 9154,9157p`), 7a (the REQ_HANDOFF stamp value is unchanged, S10), 8 (CLI table; the demotion half belongs to row 15), 18 (spec sentence only, not the rx_info shape), 5/11/16/17/20 (no AST kind, grammar, A_CTX, ^ or Ctx wrapper touched).
- Dispositions whose reason I verified true at T: row 1 (`req_reentered` tests `cand_finish_of(cx) != CAND_ROUTE_VM` at emit_dfa.c:9340; `pf_emit_handoff` at :7896; no new route test in the remedy as described), row 2 (the note's S3/S5/S12 reads exist: :7958, :9340), row 6a/6c (compile.c:1229 and :2462 are the reader and writer; 6c's event text matches the register), row 13 ([VMREC] plan row at T: "steps (b) and (c) not started"), row 15 ([FLAG-DEMOTE] STATE:not-started, riding), row 12/A-PLAN (roadmap A-PLAN "the first stream step that touches search sites").
- p1build is merged at T (`git log --oneline 57fcb5737 --grep=p1build` shows dc6a40dfb Merge lane/p1build), so A-SEAM's prerequisite holds; the note did not rely on it.
- Noted-deviation rows: only 6c exists (`grep -n -i 'noted deviation' architecture_at_T.md`); the note cites it (line 138, 147) with a reason; the "corrected first unless the note says why not" rule (guide line 640-643) is met.
- P1 columns: all eight register columns present, event is a named tag or row (START-DENSE not-started at T, K105, K88-HANDOFF-DENSE not-started), status "open"; rule names (Notice siblings, One home per question, Act through the row) all exist in the guide (lines 219, 55, 383).
- Commands re-run: 9 git grep/show invocations at T, 4 greps of the note, 2 of the guide.
- Not checked (other lenses): site-map completeness beyond the register's files, owner quotes, first-unit sizing.

CRITIC COMPLETE
