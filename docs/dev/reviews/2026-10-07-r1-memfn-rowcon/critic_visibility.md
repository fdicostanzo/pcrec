# ROWCON critic: visibility into decisions

Target: `row_contracts.md` (rev 1, branch lane/memfn-rowcon), sections 1.3, 1.5, 2, T6, plus the two audits. Read-only review; nothing was compiled or run. Line numbers are those of the files as read.

Counts: 2 BLOCKER, 6 MAJOR, 4 MINOR. Verdict at the end.

## BLOCKER

### B1. The decision record does not map onto C1's trace or CandRow; the design claims it does

Design claim (section 1.3): "C1's slot/route/row/site key maps onto table id + context + verdict + caller site key". Field mapping against `PCREC_CAND_TRACE_REC(slot, route, row, site)` (internal.h:6998) and `CandRow` (start_table.md section 1.1):

| pcrec field | mf_decision / mf_select | status |
|---|---|---|
| slot | none. The design has one `mf_table` per table. start_table.md Q2 ruled ONE `cand_rows[]` with a `slot` field, "not per-slot arrays". | GAP |
| route | none. `routes` mask (CR_DFA/CR_ATTEMPT/CR_VM) is a row filter run before `applies` (`cand_routed`). Not in `mf_row`, not in the signature, and no verdict for "skipped, wrong route". | GAP |
| row (chosen name) | `CHOSEN` + `name` | ok |
| site (string literal) | "caller site key" is named in prose but is not in the `mf_select` signature or in `mf_decision`. | GAP, and it cannot be fixed by adding a `const char *site` parameter: C1 requires `"" site` so that a non-literal is a compile error (C0 measured a `__func__` site false-alarming on 6,443 sequences). A literal passed through a function parameter loses that compile-time check. The macro has to stay in pcrec, wrapping the call. |
| `_RECF` (row name formatted at run time) | `mf_row.name` is `const char *` static. A formatted name cannot come back from `mf_select`. | GAP |
| `hands` / `accepts` / `list[route]` / payload union `u` | no equivalent | these are not decision-record fields, but they are CandRow columns the walk must not lose. `mf_row` must be embeddable as the first member, and `applies` is `const void *`, which drops the typed `const CandSel *`. |
| consumer | `scripts/emit_sweep.py --trace` does a SET compare of `CANDTRACE\t..` lines, with 25 declared site keys. `mf_explain` prints "one line per row", which is a different format. | The line format is the contract the sweep reads. Not stated who owns it after migration. |

So the record is a superset only for the winner name and the table id. The statement in section 2 that `CandRow`'s fields are a superset of `mf_row`'s is right, and it is exactly why the record is not a migration target yet: the missing parts (slot, route, site, route-skip verdict) are the part C1 has already proven useful.

Fix: define the record as `{table_id, ctx_tag (opaque u32: slot<<8|route for pcrec, 0 for the kit), site (const char *, set by the caller AFTER the call, never passed through the walk), nondefault, per-row {verdict, aux}}`. Add a verdict `SKIPPED_FILTER` (not routed or wrong slot) and a pre-filter hook, `int (*in_scope)(const mf_row *, uint64_t scope)`, plus a `scope` argument on `mf_select`. This lets one table hold all 37 rows and be walked per (slot, route). Add a worked field-mapping table to the doc (this table, corrected). Require that C2's both-walks oracle can be expressed as `mf_select` with a scope. Keep the macro, `PCREC_CAND_TRACE_REC(slot, route, mf_chosen_name(rec), "literal")`, in pcrec. State that `mf_explain` is NOT the CANDTRACE format and that pcrec keeps printing CANDTRACE itself.

### B2. "Where would a human see it" is undefined; V is not met by default

Section 1.3 says what the record contains and that `mf_explain` prints it. It never says who calls it, with what switch, to what stream. Evidence from the audit (section 4 of audit_kit_rows):
- `mf_result` is the only existing out-channel, and pcrec passes `res` = NULL at every call (memfn_sites.c:278, :286, :296); `mf_call` has no `res` parameter.
- G2 never reads `form_id`. C4 class 7 forbids pcrec comparing it.
- T6 (the only pcrec-side surface) is "OPTIONAL", trace-build-only, and conditional on Q-ROW-2.

So after T0-T5 a human can see a decision only inside the C5 fixtures and G2 output, and only if someone writes the code. A pcrec user, or the dumps stream, sees nothing. For the stated V acceptance criterion ("which row decided and why the others didn't") the deliverable is a data type with no reader.

Further consequences the design does not face:
- Adding `mf_decision *` to `mf_use` / `mf_call` / `mf_emit` / `mf_define` is a change to `memfn.h`. It is an extraction-surface change (C15 allowlist, `MF_NS` symbols) and needs the R-6 request to be filed first, not "if T5 needs it".
- If the record is ever put in an artifact comment or a stamp, that is an abi event (D76/D94) and a `docs/spec/` hunk (D80). If it only goes to stderr in a scratch build, say so and that no spec hunk is needed.
- The hit counters live in `mf_art` (per artifact, section 1.4). The G2 floor needs them aggregated across artifacts. Either the accessor drains into a caller-owned table at art end, or G2 sums per-art reads. Unspecified.

Fix: name the three surfaces and give each an owner:
1. Kit-level: `mf_explain(rec, sink)` called by G2 and C5 on every site (so the G2 report carries a per-row CHOSEN table; this is T5).
2. Compiler-level, no spec impact: the `PCREC_CAND_TRACE` build only (T6), promoted from OPTIONAL to a required step of T5. T5's corpus census needs it, and Q-ROW-2 answers itself: without T6 the census has no channel.
3. Human-level: a CLI explain flag (for example `pcrec --explain-selection`, or the existing probe family `--probe-ask`) is a separate ruled item. Mark it explicitly "not proposed, would be caller-observable, needs the D80 hunk and a dumps-stream decision" so it is a conscious deferral.

## MAJOR

### M1. "First failing field only" throws away the thing K96 needed

Section 1.3 records GATED with the FIRST failing field. The gate is `nondefault & ~honours`, and the whole failing set is already in hand as a mask at no cost. Recording one id means the explain output for a K96-class site says "miss" when the site also states `floor` and `s` was unparenthesized. The panel cannot tell whether the next fix lands on generic or on another decline.
Fix: store `uint64_t gate_missing = nondefault & ~row->honours` per GATED row; the printer expands it to field names from `fields.def`.

### M2. PRED_FALSE has no reason, which is where most declines live

The gate covers fields. The shape predicates (`applies(ctx)`, term kinds, counts, plan hints) are exactly where "why not this row" is most often asked (audit section 1: all 8 rows). `int (*applies)(const void *)` returns only 0/1, so `PRED_FALSE` is as opaque as today's silent `return 0` (audit section 4, last line).
Fix: the predicate returns a small reason code (0 = applies, otherwise a per-table enum or an index into a static reason-string array on the row); the record keeps it. Keep the existing 0/1 predicates working by a thin adapter for pcrec's tables (non-zero = "predicate false").

### M3. DENIED does not say by which switch

Section 1.5's `deny` field is "MF_D_* bit and/or options.def row". Two namespaces (the `MF_D_*` mask via `site.denies`; `--memfn=no-NAME` via `opts`), and the record stores only DENIED. A reader cannot tell `-fno-run-overlap` from `--memfn=no-runcmp`.
Fix: DENIED carries `aux = bit index | namespace tag` or the options.def row index.

### M4. Fixed-size record and nested decisions are unspecified

- Rows per table vary (kit 4, runcmp 4; pcrec `cand_rows[]` is 37). The record is "fixed-size". The cap and the overflow behaviour (silently truncate, or abort in the trace build?) are not stated.
- Section 1.5 turns 12 untabled branches into sub-tables. Each sub-table decision is a second `mf_select`. The record has one table id. So the arm-level record and its form-level children cannot be linked; "why did the site use the pair form" is unanswerable.
Fix: a record is a flat array of `{table_id, parent_index, row, verdict, aux}` entries with a stated cap and an overflow flag.

### M5. Listing: the claim "listing change only" is wrong in three places, and moves a registry/dumps stream

- T1 says the listing is byte-identical; T2 adds A1-A4 (new rows in `--list-axes`), T4 adds sub-tables, and `honours` / the field vocabulary are not stated as listed at all. The text covers only "the `--list-axes` memfn section floor goes up".
- Today the `memfn` section is options.def-driven (empty), and `run-overlap` rows are read live from `mf_run_rows`. Composer arms are neither. Which section do they appear in, and with what row-key spelling? `table_contract.md` Sections shape governs this; the doc does not cite it.
- `--list-axes` is a dumps-stream and registry-check input. New rows move that stream (a mover in emit_sweep's dumps tier even though no artifact byte moves) and raise the registry's row/pass counts, which are pinned floors. The doc says "no pcrec bytes" in every step but never classifies the dumps stream. The bar for T2 needs a gate that includes dumps, not only emit streams.
- Unlike `run-overlap`, an arm deny in `options.def` form (`--memfn=no-ofsskip`) is not byte-neutral to use: denying ofsskip falls to generic, whose text differs from pcrec's pre-migration text (audit section 5.1, A4 row). "its alpha is N/A" holds for the row's addition and not for its use. memfn/CLAUDE.md says a row is the OFF arm of a byte-moving change; here the row's existence moves nothing, but its use moves bytes, so it also needs the stamp (`MEMFN_FORMS`) consequence stated.
Fix: add a short "listing" subsection: which section, which spelling, the literal floors in `docs/spec/`, the dumps-stream classification (listing mover, not an artifact mover), and an explicit sentence on deny use.

### M6. Generality: what would block pcrec's adoption of `mf_select`

Checked against dfa_select/DFA_SELECT and the C2 walk:
1. Route masks and slot filtering (B1 above).
2. `cand_always` is a row-level predicate in pcrec. Kit totality is by `honours = ALL` plus `refuse_test`. For a table with no fields (pcrec), the doc says the gate is a no-op, but never says what `mf_select` returns when no row applies: NULL, a loud refusal, or a crash? pcrec deliberately crashes on a missing fallback (emit_dfa.c:5071-5088) and the kit refuses via `kit_fail`. Both behaviours are legitimate. Fix: `mf_select` returns NULL and the caller owns the failure policy.
3. `applies(const void *)` against `applies(const DfaSel *)` / `const CandSel *`. Type safety is lost for 13 tables. Fix: generic macro `MF_TABLE_T(type)` or document the cast discipline in the T0 unit tests.
4. Deny: pcrec's rows carry one or two `PCREC_NO_*` bits and some tables a `degrading` flag (`--fast-or-fail`, `fit_rungs[]`). `deny` is `uint64_t` in both, so a plain bit-test works, but the "deny by a derived predicate" case (fit_rungs) needs a caller-side `denied()` hook.
5. Boundary: the kit's `MF_NS` symbols and the C15 allowlist pin new exports; every symbol in the `table.c` set is a pcrec abi/extraction surface event. Not mentioned in T0.
6. Cost: the walk records per row. pcrec's walks run once per compile, so this is cheap, but in a default build the record must be skipped completely (`rec == NULL` fast path), or C1's "default build compiles no code for it" property is lost.

### M7. Reach counters: CHOSEN-only counts, and the independent control is the weakest form

- Counting only CHOSEN means a row always shadowed by an earlier row reads 0, which is correct for dead-row detection. But a row never evaluated because its predecessor always wins is indistinguishable from a row whose predicate is false everywhere. Adding an `EVALUATED` / `PRED_TRUE_BUT_OUTRANKED` count is nearly free and separates "unreachable by construction" from "never exercised".
- Section 1.4 item 3 pins a floor of ROWS and WITNESSED ROWS as a literal. That shares no source with the table, but it counts rows, not that they are chosen, which is the K35 weakness (a count of a population nobody counts). start_table.md section 3.4's per-row control is the deny-delta count (the number of sites whose bytes move when the row is denied), independent of the table. The ROWCON design drops that control; it should adopt it for the kit rows (deny the row, count movers across the census) rather than rely on the record alone.
- Counters are in `mf_art`. pcrec's plan keeps its hit counters under `PCREC_CAND_TRACE` only. Two homes for the same fact. Say which is canonical at migration.

## MINOR

- m1. Section 1.3: "the explain output shows the order at every decision" (section 3 item 6) assumes `mf_explain` prints all rows including those after CHOSEN. The record shape only says "per row evaluated". Say whether rows after the winner appear (they should, as `NOT_EVALUATED`, so "why didn't row N win" has an answer and the listing order is visible).
- m2. `mf_explain` wording becomes a contract the moment a check diffs it (C5 pins already digest text). State that it is diagnostic and that checks read the structured record, never the text (D26 spirit).
- m3. T6 must extend C1's declared site keys (25) for the kit's call sites in `memfn_sites.c` (literal keys, as C2-C7 are asked to do). Otherwise the sweep's SET compare sees unknown records.
- m4. The audit's inference that pcrec never reaches the generic arm (audit_kit_rows 5.1, A4) is flagged there as "not a measurement". The record is exactly what would turn it into one; say so in T5, because it decides whether generic needs a declared unreachable in the corpus census.

## Verdict

REVISE before the panel passes it. The mechanism (allowlist gate, one default per field, sub-tables) is sound, and the visibility lens does not argue against it. The record and the migration story are the weak parts. Specifically: B1 (the record lacks slot, route, site and a filter verdict, so "migration target" is not yet true) and B2 (no named reader or surface, so V is not delivered by T0-T5). M1-M3 are cheap and should be folded into the record shape now, because retrofitting fields into a record that pcrec has already adopted is the expensive version. M5-M6 should be answered in the doc before T2, since T2 is the first step that moves the listing. Q-ROW-2 should be answered "yes, T6 is required"; Q-ROW-3 "not now" is right.
