# CRITIC SLOT — r72 memfn-bsu1

## Findings

### SLOT-1 — the use re-derives each L/H stretch's loop extent at render time, beside the stored list
SUSPECTED (the agreement is proved by argument, not by a check). window.c wf_test_to (subject :3653-3675)
reads the stored `{i, k, h}` only as a GATE (`i < end`) and then calls `wf_loop_len(w, i, head)` at every
entry of the stretch, re-walking the run with the stretch's h to find where the loop starts and how long it
is. So the run's extent has TWO producers: the enumerator (wf_stretches, wf_loop_len at head 0) and the
renderer (wf_loop_len at head h). They agree today only because every break condition in wf_loop_len except
`off[i] < head` is head-independent and compares against the start's table/set (read :3613-3625; I checked
the argument holds for I, L, H(64), H(N)), and nobody's comment states that. A later edit that makes the
run head-dependent (or U2's V, which renders from stored k) leaves two readers of different shapes. The
design prescribes this shape (§3.1 "wf_loop_len gains the head as a parameter ... the H rows render with
their own h"), so the finding is against §3.1 and the code both, against R-2's own rule ("one selection ...
the agreement is now literal"). FIX: render from stored facts only: loop start = the first entry of
[i, i+k) with off >= h, len = i+k-start (lone tests where len < 2); wf_loop_len is then called only by the
enumerator and loses the head parameter (always 0). Severity maintenance; effort small (wf_test_to only,
one identity gate re-run); blast radius window.c wf_test_to/wf_loop_len.

### SLOT-2 — the probed index plan_ix(w, w->hl) is derived twice (d_hors_head and hors_skip)
CONFIRMED by reading (subject window.c :4087 and :4106). hors_skip is R-1's spelling verbatim (§3 gives the
formula with `ih = plan_ix(w, w->hl)`), so this matches the ruling; it is a minor second derivation of one
plan fact. General form: b_hors_prepare, which writes w->hl, also stores the probed index (`w->hix`), read by
the head, the skip rule and (U2) T-vwin. Severity maintenance; effort trivial; blast radius B-hors only.

### SLOT-3 — design/comment text drifted from the built table (six contracts, use_s_none, {i,k,form,j}, "plan facts")
CONFIRMED by reading. Not a gap, a text set:
- §14 U1 "its six contracts" and §3 "54 of 64 after wfS's six rows": at U1 there are FOUR contracts and four
  reach slots (52 of 64); the two V contracts land at U2. Say "four (six at U2)".
- §3 spells a new `use_s_none`; the code reuses window.c's `use_nothing` (identical value; the better form:
  wfE's private `use_e_none` and finder.c's `use_none` are the duplicates). §3 should name use_nothing.
- §3 stores `{i, k, form, j}`; the code stores `{i, k, h}` (form as an inline head, no j). Correct for U1 (j
  is 0, every U1 form is an h), but §3/§14 never say U1 stores the subset.
- The table comment (window.c :1890-1892) "The rows read plan facts, not site fields": T-deny/T-force read the
  SITE's `opts` (mf_site.opts, kit_opt_state) and T-lever the ART's levers; none reads a plan fact. True
  claim: "no contract field (FLD_*)", which is why every field is a wildcard. Same phrase in §3.
- window.c's file header (:47) still lists "Tables A, M, E, and T-FIND's fd_rows" as the kit_tables; wfS
  is missing.
Severity doc; effort minutes; blast radius block_span.md §3/§14, window.c comments.

### SLOT-4 — a dead guard and an unreachable branch reported as "out of memory"
CONFIRMED by reading. (a) s_lever_holds tests `x->d->art &&` (window.c :1903), a leftover of wf_span_head's
guard; it cannot fail: wf_stretches dereferences `art->nsites` unconditionally before any walk (:1961), as
wf_plan_site does (:2630). (b) `if (r >= WF_NSROWS) return -1; /* unreachable */` (:1969): both callers turn
-1 into `*why = "out of memory"` (:2582-2583 via wf_find_prepare -> :2687-2689, and :2695-2697), so if a
future contract ever declined T-head the refusal would be misnamed. Fix: drop (a); for (b) kit_fail with a
named message (or the gate's describe), as the family does for its other impossible states (e.g. :1756).
Severity maintenance; effort trivial.

### SLOT-5 — the self-check does not cover the new `skip` column (or `head`) of an E-find search row
CONFIRMED by reading. wf_find_prepare calls `w->srch->skip(w)` unconditionally (:2582); the column is the
LAST positional initializer of each E-find row (after `basis`, :2262-2274), and wf_tables_check (:2491-2505),
whose stated job is "what no initializer states", checks the E-find rows only for having no predicate. A
fifth E-find search row written without the trailing `skip` (easy: it follows a long basis string) is a NULL
call at the first compile that reaches it, a crash rather than the art refusal the self-check gives every
other hole (and the U1 sabotage set has no row on it). Fix: one line in wf_tables_check, "an E-find search
row has no head or skip". Severity maintenance; effort 2 lines + (optionally) one plant; blast radius
wf_tables_check.

### SLOT-6 — SIBLING OF A FAMILY: wfS is the 8th kit_table and the 4th window table with a private contract macro
CONFIRMED by reading (standing question). kit_tables: fd, runcmp, fn, arms, wfA, wfM, wfE, wfS; window.c's
four each carry a private thunk trio (x_ct/x_holds/x_opt) and a private WF_CT_* macro. WF_CT_S's body is
WF_CT_A(name, row, use_nothing, MF_ANY, MF_ANY) with the table string changed ("wfS" for "wfA"); WF_CT_E
and WF_CT_M are the same "WF_SERVES_* + the table's keyed fields" shape. wfS did the right thing on the use
array (reused use_nothing). Not a U1 defect (the kit_table accessor design makes thunks per table by
construction). General form: one `WF_CT(table, name, row, uses, keyed-field overrides...)` with WF_CT_A/M/E/S
as one-line spellings, and one `KIT_TABLE_THUNKS(prefix, rows)` macro for the trio. Trigger: the next window
table, or U2 if the V rows need a keyed field (they should not: own, brow, w32 and k are plan/art facts, so
wfS's contracts stay all-wildcard and WF_CT_S gains no parameter). Severity design/maintenance; effort small.

### SLOT-7 — GENERAL FORM + UNLOCKS: what U2's V rows want from this table that U1 did not give
(a) The stored form is `int32_t h` (struct wf_stretch :1381-1384); V is not an h, so U2 retypes the record
and its one reader. General form: store the CHOSEN ROW (its index in wf_spanrows) with its h, and give
wf_spanrows a `render` column (I/L/H one renderer reading h, V the selector call); wf_test_to then dispatches
on the row, never on a form if-chain beside the table. Trigger: U2's first V row.
(b) SMALLEST FORM ("V for the site's first eligible stretch only", §3.2) needs a fact the walk reads; wf_sx
carries `w` (whose str[0..nstr) is the list so far), so a row CAN derive it, but §3's `j` is not stored. With
(a), j is a count of earlier V rows in the list. Trigger: U2.
(c) Trace identity: a wfS END carries no stretch identity. CONFIRMED: `[0-9a-f]{20}[g-z]{20}
--window-search-width=4095` under trace:subject writes two byte-identical `MFTRACE END table=wfS art=1 site=1
phase=define chosen=T-head` lines, so U4's pin "the second eligible stretch falls to T-head" cannot be read
off the trace. Sibling: wfA's per-alternative records have the same gap. Unlock: an optional tag in
gate_tctx printed on SEL/END (`key=i5,k20` for wfS, `alt=` for wfA). Trigger: the first check that reads a
per-stretch outcome from the trace (U4's SMALLEST-FORM cell).
(d) With SLOT-1 fixed, V and L/H read one stored extent (k) and the renderer derives nothing.

## PROBED-AND-HELD

- R-1 (`skip` a plan fact): HELD. `ren_search_row.skip` column, stop_skip on RB_PAIR/RB_MEMCHR/RB_WALK,
  hors_skip on RB_HORS, E-stmt rows NULL (designated); `w->skip = w->srch->skip(w)` after find_groups and the
  search/stream prepare, before the enumerator; plan_of writes -1 beside stop_ix; floor and fused B-fn keep
  -1 (B-fn returns before find_groups; it renders through ofs_fn_define_at, never wf_test_to, so its empty
  list is never read). head's `int *skip`, test's `int skip`, wf_find_expr's local all gone. One producer.
- R-2 / R71-3 / R71-7(d) (store once; the floor call; one `gphases` parameter): HELD. wf_stretches has exactly
  two call sites (wf_find_prepare, wf_plan_site's E_GENERIC branch); wf_find_prepare has one call site and
  gained exactly `gphases` (quiet = !build). Only one reader of the list (wf_test_to), reached by the floor
  define, the floor expr and C-find's use. Caveat SLOT-1.
- R-3 (spelling): the kit_table line is §3's verbatim; `in.s` set so the opt column would apply; s_opt NULL
  on all four rows (V's `span-vector` is U2); wf_tables_check's line present with §3's message (it also
  checks the `h` column, stricter than §3).
- Row order and forms vs the retired if-chain: T-deny (st<0 -> I), T-force (st>0 -> L), T-lever (art lever ->
  H(span_head)), T-head (H(64)): same predicates, same order, same values (diff read line by line).
- Identity argument for the per-stretch evaluation (§3.1 claim): checked that wf_loop_len's run end is
  head-independent and that no head-h loop can start outside a head-0 stretch, so non-V bytes cannot move.
- Trace (trace_format.md hunk): `table=wfS` names E-find and floor sites, joins wfA/wfM/wfE as not printed in
  the reach registry; observed one SEL + 4 ROW + 1 END per stretch at phase=define, site= the define's
  handle (trace:subject, `[0-9a-f]{32}`: 1 stretch, T-head); rows_check.py/reach_equal.py read only their
  from/gone table sets, so wfS is ignored as wfE is (read).
- The decider census edit matches §14 U1's R-1 of lane bsu1 text (wf_stretches fn, wf_spanrows data, T-SPAN
  in the header, HITS 67->68, MEMBER_COUNT 70->72).
- No stale `wf_span_head` / `w->head` reader in memfn/src or its CLAUDE.md files.
- Compiles: 3 (trace:subject): `[0-9a-f]{32}` default, the same `--memfn=no-window-search` (went E-stmt, no
  wfS walk: legacy frame, correct), `[0-9a-f]{20}[g-z]{20} --window-search-width=4095` (two stretches, two
  T-head ENDs). No plant/base compares run (not this lens): none to classify. Witness length: minimum 32,
  maximum 40 positions.

CRITIC COMPLETE
