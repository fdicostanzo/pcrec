# CRITIC CHECKS — r67 k152

## Findings


### CHECK-1 — the fix leaves 3 mech sabotage anchors stale (CONFIRMED)
Repro: `python3 -I $W/scripts/m6read_check_sab_anchors.py` in the review tree prints `STALE ANCHORS: 3`: S1100_collapse-drops-rmin (ANCHOR NOT FOUND), S14_nbr_threshold (ANCHOR NOT FOUND), S1176_ctx_row_frag_drops_fn (ANCHOR COUNT 1, SAB_COUNT 2). Same script in the base tree: `all anchors resolve` (1368 sabotages). Cause: nfa.c's moved arm bodies lost one indent level (e.g. `st->ctxfn = a->u.ctx.fn;` now 8 spaces at :878/:886, was 12 at base :730), so the verbatim multi-line/indented anchors no longer match. Effect: those 3 sabotages cannot apply, so the matrix cannot show their suites (memfnfinder, trie, ctx) still detect; a mech gate would go red or silently lose coverage. Severity: maintenance/check (blocks landing if the anchor check is gated). Effort: small (re-indent the 3 SAB_BEFORE/AFTER; S1176 count 2->1). Blast: tests/mech/sabotages only. Also contradicts "Bodies moved verbatim" only in whitespace; the lane did not update dependents of the moved text.

### CHECK-2 — three of the four new DEPTH_FAMILIES rows pass on base and on the S3470 plant (CONFIRMED, by design but unannounced)
Budget thread 442368, depth 250 / 251, hw bytes (subject | base | plant:S3470):
nclitrep 293744 | 440176 | 440176 (rc=0 all); litpost 317744 | 440560 | 440560; nclitpost 292864 | 440560 | 440560; litcompound 307056 | DIED 139 | DIED 139. Depth 251 rc=-1 "too deeply nested" hw=122152 identical on all three trees for all four rows.
So only litcompound can ever go red on the fix being undone; nclitrep/litpost/nclitpost witness nothing against undo of K152 (they are green at base). Their value is only headroom against a different/CI compiler, and the script checks pass/fail against the budget, not headroom. Headroom now: subject litpost 317744 = 28.2% under 442368 (nclitrep 33.6%, nclitpost 33.8%, litcompound 30.6%); base/plant litpost 0.4% (440560) and litcompound over. The S3470 claim "litcompound dies" is real (139 on plant and base, 1 run each). Severity: design/check (the header's "one row" argument is honest about this; rows 1-3 are growth-sweep floor, not detectors). Effort: none required; suggest the rows' comment say "green at base, headroom only".

### CHECK-3 — SAB_COUNT 10 / COUNT2 1 are exact; partial undo is invisible to every check (CONFIRMED count; SUSPECTED partial)
`grep -n PCREC_OWN_FRAME src/ir/nfa.c` gives 10 `static PCREC_OWN_FRAME ` definitions (588,666,691,733,834,839,854,868,890,899) plus 1 comment line (661), so SAB_COUNT 10 matches the anchor `static PCREC_OWN_FRAME ` (checker lists S3470 as resolved). Partial undos (marks dropped but nfa_cat single-site: 408,560 B; nfa_rep alone inlined: 408,560 B) are lane-measured under the 442,368 budget, so run_compile_stack.sh stays green; I could not rebuild partial plants (SUSPECTED: regression of any single arm, or nfa_cat's two loops back alone, slips every check; headroom to the budget would be only ~7.6% on those). That is a ruled-by-design stance (budget not headroom) but the 7.6% margin at partial undo is thinner than the 28% shown for the fix; not fixable without a headroom ratchet.

### CHECK-4 — litcompound reach check is real but weak (CONFIRMED, minor)
kit/emit.sh subject on litcompound-250: rc=0, rx.c has 15 `"compound"` lines (RX_END_WINDOW/RX_REQ_WHY/RX_REQ_HANDOFF). The control (same nest without `^` and `|b$`) emits 0, so the grep does discriminate the compound route. Weakness: it greps a quoted word anywhere in the C, not the stamp; fine as a reach proxy. Held.

### CHECK-5 — house rule: marks without their stated use; one comment overstates (CONFIRMED, doc)
internal.h:366 says "Mark an arm for either reason, and say which in its header". nfa.c: `trie_key` (588) is newly marked and its header (:581-587) names no use; nfa_class/nfa_ctx/nfa_wclass/nfa_eol (838-890) are covered only by a group comment (~:826) that says "the others are leaves", which is neither stated use (a leaf is not a "recursive arm"; if it is scratch-dead-before-recursion it is the FIRST use, say so). nfa_cat's header says "three arms" while ten functions are marked (the 10-count lives only in S3470). The group comment "Bodies moved verbatim" is true for leaves but nfa_cat's body is NOT verbatim (its two loops merged into one site) as its own header admits; fine in context, worth one clause. "FIRST use" at nfa_erase_by_row (:831) and "SECOND use" at nfa_cat (:661) are true against internal.h. coding.md:198 ("two uses ... say which") is satisfied for nfa_cat/nfa_erase_by_row only. Severity doc; effort trivial.

## PROBED-AND-HELD
- Stack matrix: 4 rows x depths 250/251 x 3 trees (subject, base, plant:S3470) = 24 runs, plus 2 emit runs; min depth 250, max depth 251. Depth-251 refusal identical on all trees (hw=122152).
- S3470 claim litcompound DIED 139: real on plant and base. SAB_COUNT 10 / COUNT2 1: exact, S3470 anchors resolve.
- litcompound reach grep discriminates (15 hits vs 0 on the control).
- Compile-time results byte-identity of emitted C was not probed (other lens).
CRITIC COMPLETE
