# CRITIC HOUSE — r72 memfn-bsu1

## Findings



### HOUSE-1 — wfS comment says rows read plan facts, not site fields; the rows read site/art fields; wf_sx.w/i/k are dead
SUSPECTED-by-reading, CONFIRMED by grep (window.c wf_sx, s_*_holds). Severity: maintenance/doc. Effort: S.
The table header states "The rows read plan facts, not site fields". s_deny_holds/s_force_holds read x->d->s->opts (site), s_lever_holds/s_lever_h read x->d->art. No row reads x->w, x->i or x->k, so wf_sx carries three unused fields and the claim is false today. The fields are U2-forward (V rows); per D77 build-under-measurement either drop them until U2 or reword the comment ("U2's rows will read ...").

### HOUSE-2 — `r >= WF_NSROWS` returns -1, and the callers report "out of memory"
CONFIRMED by reading wf_stretches / wf_find_prepare / wf_plan_site. Severity: maintenance. Effort: S.
The comment says "T-head always holds: unreachable", yet the -1 shares the function's documented "-1 out of memory" and both callers set why = "out of memory". If the table ever lost T-head (a sabotage, or a contract that declines at gphases), the failure would be misreported as OOM. Fix: an own message, or a pcrec-style assert; wf_tables_check could assert the last row is T-head (all four rows are checked non-hole, not that the last is always-true).

### HOUSE-3 — dead `opt` column in wfS
CONFIRMED. wf_spanrows[].opt is NULL in all four rows; s_opt exists only to be passed. kit_table allows opt==NULL ("NULL: none"), and T-deny/T-force are encoded as predicates over kit_opt_state, not through the table's deny/opt machinery. Copied from wfE's shape. Severity: maintenance (small). Drop column and s_opt; pass NULL. Also T-deny/T-force predicates re-spell the option reading twice (kit_opt_state < 0 / > 0): fine, but a one-line comment on why the opt column is not used (deny SELECTS a row here rather than skipping it) would stop the next reader "fixing" it.

### HOUSE-4 — stale readers of the retired `wf_span_head` (doc)
CONFIRMED by grep (denylist excludes applied). Present-tense references to a function that no longer exists:
- tests/mech/sabotages/S3278 line 3, S3279 line 3, S3281 line 3, S3282 line 3: header opens "wf_span_head (memfn/src/window.c) drops/honours ..." with the re-aim note only on a later line. S3280's header was re-pointed less, but its text is true.
- tests/memfn/decider_census.py:144 and decider_census.tsv:83 mention it only as "retired": OK.
- docs/design/memfn/block_span.md retains it in its "today's code" rows (line 136 etc.): design history for rev 4.1, acceptable (rows state BASE line numbers).
- docs/dev/lanes/forms_report.md:35-36: historical lane report, leave.
No stale `w->head`, `int *skip`, or `skip` argument readers outside block_span.md's BASE-description rows and the re-aim notes. memfn/src/compose.c/kit.h comment edits are true.

### HOUSE-5 — over-wide reflowed comment lines
CONFIRMED. Added lines of 130, 114 and 101 columns in window.c (the "H(h), chosen per stretch ... A periodic segment ..." comment, the wf_loop_len header "under inline head `head`: ...", and the ren_search RB_PAIR basis line with `stop_skip },`), against the file's ~80-100 column wrapping. The first two are comments joined on one line by an in-place edit instead of a reflow. Severity: style. Effort: S. gen_span_seed.py has one 103-col line (the "ident" row); trivial.

### HOUSE-6 — minor, judged OK or noted
- `w->skip = -1` after memset: same pattern as the adjacent `w->stop_ix = -1` with a true comment ("the memset's 0 is a real entry"); HOLDS, and it avoids a +1-biased encoding. Only risk: a third plan constructor that memsets without plan_of would read skip 0; plan_of is the only constructor (grep) so HOLDS.
- Stretch array `n / 2 + 1`: every stretch has k >= 2 (wf_loop_len contract "at least 2") and i += k-1, so at most n/2 stretches; +1 avoids a zero-size alloc when n < 2. HOLDS but undocumented: add a one-clause comment naming the k>=2 bound, else it reads as a guess (suspect-constants memory).
- wf_stretches' quiet arg is spelled `!build` at one caller and `quiet` at the other (same value): HOLDS.
- Table-vs-if-chain: wf_test_to's `si < w->nstr && w->str[si].i == i` is a stored-list reader, not a decision; no if-chain left standing. The `i < end` guard plus `head` carried across i is a small state machine; fine.
- Side effects in predicates: s_*_holds are pure; wf_stretches writes MF_TRACE (via kit_walk) at plan time only, `quiet` honoured. HOLDS.
- Duplication: wf_loop_len called once in the enumerator (head 0) and once per stretch position in wf_test_to (stored head): the same function by design, not a clone.

## PROBED-AND-HELD
Read-only, no compiles. Probes: full diff of window.c/compose.c/kit.h; grep for wf_span_head, w->head, ->head, *skip, wf_loop_len, wf_test_to, c_find_test, c_floor_test across memfn, docs, tests (about 60 hits triaged); gen_span_seed.py read fully (41-pattern count enforced, expectations from python re; no duplicated abstraction found, though GRID's `ident` atom duplicates WORD-like data deliberately). Witness lengths: not applicable (no emitted probes).

CRITIC COMPLETE
