# ROWCON critic: reachability (D6, read-only)

Reviewed: row_contracts.md rev 1 (§1.4, §4 T5, Q-ROW-2) against audit_kit_rows.md §2, §5, learnings §3.
Method: read only; nothing compiled or run. Facts below are the audit's, re-read at the cited lines, not re-measured.

## BLOCKER

### B1. Per-row CHOSEN counters are the unit of "reach", but the failing population is the (row x honoured-field-value) cell. A row can be CHOSEN 10,000 times and every K96-class bug still sit unreached.

Evidence: all 8 suspect cells (S1-S8) are cells inside rows that are, or would be, "reached". S2-S4 (PRE x unparenthesised s/n/lo) live in a row (A2) that pcrec reaches today (audit §5.1: 94 pre artifacts). A per-row floor of "CHOSEN >= 1" is satisfied by pcrec's own sites while the ternary-hook-style cell is never driven (G2 never sets on_miss_leaves, so never reaches A2 at all; A3 is reached about once, batch 22, in one hook style). §3 point 5 admits the gate "cannot see" a claimed-but-wrong field and then says "G2 gains a hook-style axis per honoured field", but §1.4 and T5 define reach only as per-row CHOSEN. The sentence that closes the gap is one clause in §3 with no check, no counter and no floor behind it. That is the exact shape learnings §3 warns about ("liveness arguments are not value arguments"; "what would have to be true for it to fail, and who chose that input").

Fix: define reach at the cell grain: for each row R and each field F in R.honours, the cell (R, F, value-class) where value-class is a small declared set per field in `fields.def` (miss: NULL / equal-to-n / other; floor: NULL / "0" / other; s,n,lo,on_miss: plain / ternary-unparenthesised / multi-statement; indent NULL / set; etc.). The decision record carries, for the chosen row, the non-default mask AND the value-class of each honoured non-default field. The per-row counter becomes a per-cell counter `hits[row][field][class]`. G2 floor: every cell with `F in R.honours` and class in F.classes has >= 1 CHOSEN hit, else FAIL. A field declared honoured with no class driven is the K96 shape by construction. The classes are declared in fields.def by the contract text (not derived from the generator), see B2.

### B2. Every control named in §1.4 shares a source with what it controls.

- Counters: the kit's own `mf_select`, in the artifact `mf_art`. They count what the selector chose. If the selector has a bug that drifts a site to another row, the counter faithfully reports the drifted row. "Row X has count N" is evidence that the selector ran, not that row X's text is right. Counter and table are one module, one author, one failure mode.
- Gate and counters share `fields.def`: the nondefault mask that decides admission is the same mask the record reports. A wrong `default_test` (e.g. floor "0" vs NULL, the very thing Q-ROW-1 is deciding) makes the gate wrong AND the census agree with it. The 13 disagreement rulings are therefore uncontrolled. Nobody independent checks that a ruled default matches the contract text.
- Witness census (T5.2) "compiles it and asserts the record names the row": the assertion reads the kit's decision record, so a witness that drifts to another row is detected only if the witness pins the row name from a source other than the record (see M2).
- The docs/spec literal floor (§1.4.3): counts rows-per-table and witnessed-rows. It shares no source with the table, good, but it is the weakest class in learnings §3 ("Floors answer 'did someone delete a lot', never 'the right ones'; exact counts disarm themselves via their own failure message; the fix is a manifest naming irreplaceable rows"). It is not the independent control the design says it is. It cannot detect: a row replaced by another, a witness drifting, a cell dead. It also counts only rows, so it is silent on B1's grain.

Truly independent controls available (use all three, they fail differently):
1. A MANIFEST, not a count: a committed list of row names per table (`row_manifest.tsv`, hand-written from the audit, in docs/spec), each with its declared witness (G2 family id, C5 fixture id, or corpus cell) and its declared status (reached-from-pcrec / generic-only). The check diffs the kit's `--list-axes` row listing against the manifest by NAME both ways. A deleted or silently renamed row fails.
2. Text-signature oracle (independent of the decision record): each row has a regex over the emitted artifact text that only that row can write (A1: file-scope `static inline size_t` + memchr stream; A2: `rq_set[]` / `rx_reqrun`-style gate; A3: expression with `+ lo` and no file-scope part; A4: bare byte loop; B1: `rx_w<W>(` with `&`; B2: two `rx_w<W>` joined; B3: `& K) ==`; B4: `memcmp`). The census asserts record-row == signature-row. A drift or a counter bug breaks the agreement. This is what run_handoff_reach.sh already does ("artifact-text markers"). Weakness: the signature is a kit-author-authored notion of "what text this row writes", so have it written from audit §1.1's "text it writes" column by someone who has not read the row's code (the D27 author, g2x's family).
3. Semantic oracle: G2's byte-loop reference (already independent: it checks the compiled answer against a scalar byte loop on a generated predicate space). Reach for a cell should be defined as "this cell was CHOSEN AND its compiled matcher agreed with the reference on >= K subjects", otherwise a cell can be counted as reached by a site whose output was never compared (a G2 site that only checks it compiles).

## MAJOR

### M1. Sub-table rows (T4) are in the mechanism but not in the reach story.

§1.5 turns the 12 untabled branches into sub-tables "wherever they choose between forms"; T5 mentions only "per row". A sub-table row (e.g. ofsskip PAIR vs single stream, precheck gate/run/set-rest, generic's six body forms and member-vs-range) is a row whose reach nobody counts. The audit shows exactly this blind spot today: PAIR leapfrog is "not confirmed in the corpus within the cap", reached by C5 `ofs-pair` only; A2 masked-whole-run-with-rest is C5 only. With the counters keyed to table id + row id, the sub-tables are free to count; the design just has to say so.
Fix: the manifest in B2.1 spans every table including sub-tables (qualified `table/row` names); T4 may not land a sub-table without its manifest rows and witnesses in the same commit; the spec floor counts them by table.

### M2. Detecting a witness that silently drifts to another row ([MECH-REACH]) is not designed.

The census witness "asserts the record names the row" (T5.2). Failure modes it does not cover:
- A later change to a lower row's gate or a new row inserted ABOVE the witness's target makes the pattern take the new row; the witness asserts row X, fails loudly (good) - but the fix author is then free to edit the assertion to the new row, and nothing flags that X lost its only witness. The manifest in B2.1 closes this: the witness set per row is committed; a row left with zero witnesses fails the floor regardless of which assertion was edited.
- A witness asserting only "the record names row X" doesn't prove the text that reached the artifact came from row X (counter vs text). Add the signature check (B2.2).
- The pcrec pattern drifts to a different SITE (pcrec's own pre-kit decision changes: `-fno-offset-skip`, `-fno-req-run`, the START-TABLE C2-C7 remodel) so the kit never sees it. The kit's census sees "row X zero", correct and loud, but the cause is outside the kit. That is the [MECH-REACH] case in its pure form. Fix: pair each corpus witness with a pcrec-side invariant already present in the artifact (e.g. the `RX_REQ_HANDOFF` stamp or `RUN_WORDS` count the audit already cites) so a failure localizes to "site vanished" vs "row changed".
- Witness stops compiling/loading (a skipped step counts as green): hard-fail on an empty witness list and on a skipped witness; count witnesses actually executed, printed in the verdict (K35: nobody counts the executed population).

### M3. Q-ROW-2: a T6 pcrec hook is NOT needed; the cheapest independent route is the artifact text plus the existing traced-site-census build. Recommend rejecting T6 for ROWCON.

Reasoning: the audit §4 shows pcrec passes `res = NULL` at every `mf_use` (memfn_sites.c:278, :286, :296), `mf_call` has no `res`, and C4 class 7 bans pcrec comparing `form_id`. T6 would add a pcrec-side `res` plumbing for a test-only purpose and, worse, it makes the census read the kit's own `form_id`/record, one source (B2). Routes, cheapest first:
1. Text-signature route (above): compile the witness with the plain `build/pcrec`, grep the artifact for the row's signature. Needs no pcrec change, no kit trace build, and is independent of the decision record. Cost: a signature per row (8 + sub-tables), a regex each. The A-arms already have distinguishing text; B1-B4 are separated by `RX_RUN_WORDS` plus the text (B1 vs B2 by count, B3/B4 only distinguishable by `& K)` vs `memcmp`).
2. The existing site_census.py traced build already logs a line per `mf_define`/`mf_emit` call. Add the arm name in the KIT's trace line (`#ifdef MF_TRACE` in `kit_fail`'s neighbour, compile-time knob, scratch builds only, same convention as PCREC_CAND_TRACE), and join on the census's per-compile accounting. That is "kit only", needs no pcrec edit, and is a cross-check against route 1. It shares the kit's decision with the counters, so it is a liveness check only; use it for the corpus-wide "which rows does any pattern reach" population count, with route 1 as the control.
3. T6 only if a row's reach cannot be told from text (B3 vs B4 after the deny is forced is distinguishable; so likely never). If ever built: keep under PCREC_CAND_TRACE as the design says, and say so in plan as UNTRIGGERED (D77), with the measured trigger "a row whose artifact text is not distinguishable".

### M4. "Declared unreachable from pcrec (generic), witnessed by G2/C5" hides dead code unless the declaration carries a trigger.

§1.4.2 lets any unreachable row ride on a reason. Today this is A4 generic (inferred, not measured: audit §5.1) - and generic is also the totality row (§3.2), so its keep-reason is structural and strong. But the mechanism admits any other row, and the audit's own table shows rows that are exactly this today: A1 PAIR leapfrog, A2 masked-whole-run-with-rest, and (per G2) A2/B1 never reached. D77 asks why keep a row nothing reaches.
Fix: the declaration has a closed vocabulary of reasons: (a) `total-fallback` (generic only; the build-time assert makes it true); (b) `pending-site` naming the manifest row and plan item that will send it traffic (e.g. M5/M6 delegation, `pending` row in site_manifest.tsv), with C17's "ends at 0 pending" as the clock; (c) `contract-reach` meaning a row serving contract inputs pcrec may later send, which then MUST have a G2 family with its own K35 floor and an owner. Anything else = delete the row. Add a count: number of rows declared by each reason, pinned in spec. "Unreachable and unexplained" is a FAIL, not a default.

### M5. Hit counters live in `mf_art`: reach counted in G2 mixes populations, and zero-hit rows can be masked by aggregation.

If one `mf_art` spans many sites (pcrec: one art per artifact), the counters sum over sites. G2 needs per-row counts across all its arts: the aggregation point is a test-harness choice; the design must say G2 sums per-art snapshots and that an art that failed (kit_fail, sticky first-error-wins) contributes nothing to a row that had CHOSEN it before the error. Also: CHOSEN is counted at `mf_define` (selection happens once, `mf_use` re-dispatches via the stored arm), so a define whose use then refuses counts as reached with no rendered use. Count at successful render completion (define AND each use), not at selection, or reach credits refused sites. Also a deny-masked selection (DENIED verdict) must not count.

## MINOR

### m1. Population counts nobody counts (K35) still missed.
- Number of sites G2 renders per (row, field, class) cell (B1). Number of G2 sites that reach `kit_fail` refusals per refuse_test: a `refuse_test` in `fields.def` that no site ever hits is a dead refusal, same disease as a dead row. Give refusals their own manifest (each `refuse_test` has a witness site that expects the exact refusal text).
- Number of DENIED verdicts per row: a row's `deny` is a second reach dimension (the row with the deny forced must land on a lower row, A/B pair). T2 adds denies but says alpha is N/A; the deny path is still code needing a driver: `--memfn=no-NAME` for every row must be exercised and must change the chosen row.
- The define/use mask-mismatch refusal (§1.2): count of G2 sites with a differing use mask. K96's own use-side check was the instance that was missed; today G2 hook styles vary at define and use? Unknown (not in the audit). Name the floor.
- Number of executed witnesses in the corpus census (M2).
- `honours` mask bits not exercised: every set bit in any `honours` needs a cell (B1), including bits set for fields no pcrec site ever sends (policy, opts, span_lo, consumer; the "benign hazards" list). The audit marks these `i` (ignored), the design's allowlist default declines them from every row - correct - but then the generic row "honours ALL" is a claim about 15+ fields that nothing drives (policy, consumer, span, cand_ppm). "Honours" for a field the row ignores because it is a fact/hint should be modelled as `ignores` (declared, no cell required), distinct from `honours` (cell required), else the generic ALL assert is satisfied vacuously (the mask is true by construction, the same "empty-vs-empty" failure mode learnings §3 names).
- The `fields.def` default predicates themselves (Q-ROW-1): 13 rulings with no test. Each needs a positive and a negative probe site proving the gate reads the ruled default (miss NULL on FUNC admitted/aliased to n; miss NULL on EXPR refused with the expected text; floor "0" == NULL).

### m2. The census learns nothing about density/hint-sensitive row choices.
Rows whose predicates read plan hints or ppm (pred.plan_hint/plan_pos, cand_ppm) pick differently by value; one witness per row hides the region. Out of scope for ROWCON reach if hints stay `i`; if any row starts reading them the cell grain (B1) must include them.

### m3. Order sensitivity (§3.6) has no reach control: overlapping predicates mean row N+1 can be shadowed completely by N. A shadowed row has CHOSEN = 0 forever and the floor catches it, but only if some witness is intended for it; add a table-level check "each row has a site on which it is the FIRST applicable row ignoring all lower rows" (the witness definition), computed independently by the G2 generator's own shape, not by the record.

## Answers to the specific questions

- Right grain? No: row grain is insufficient (B1). Needed: cell = (row, honoured field, value-class), plus sub-table rows (M1), plus refusal and deny paths (m1).
- Independence: counters, gate, census, fields.def defaults all share the kit's own source. G2's families (blinded author) and the reference byte-loop are the real independent controls. The docs/spec literal floor is a count, not a manifest; replace/augment with a name-level manifest (B2). Add text signatures (B2.2).
- Unreachable-from-pcrec rows: current declaration is too permissive (M4); closed reason vocabulary with triggers and a count.
- Drift detection: M2 (manifest of witnesses per row, signature check, pcrec-side invariant, executed-witness count, hard-fail on empty/skipped).
- T5 without T6: yes (M3): artifact text signature, plus a kit-only compile-time trace on the traced census build; reject T6 for ROWCON.
- K35 counts still missed: m1.

## Verdict

NOT READY to pass as written. The mechanism (allowlist gate, one table type) fixes the declined-field class soundly, and the exported-mechanism decision is fine for reach (Q-ROW-3 no objection). But the reach/ (R) leg is defined at a grain that would have passed K96 and S2-S8 green, and its controls are the kit's own. Required before T5: B1 (cell grain) and B2 (name-level manifest + text-signature oracle + reference-agreement). MAJOR items M1-M5 should be folded into §1.4/T5 in the same revision; M3 answers Q-ROW-2 (no T6).

Counts: BLOCKER 2, MAJOR 5, MINOR 3 (m1 lists 6 sub-items).
Top finding: B1, per-row CHOSEN reach is satisfied by the rows that already hide S2-S8; reach must be per (row, honoured field, value-class) cell.
