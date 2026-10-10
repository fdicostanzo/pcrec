# ROWCON critic: contract, boundary, docs

Target: worktrees/memfn/docs/design/memfn/row_contracts.md (rev 1) and probes/rowcon/audit_kit_rows.md, audit_pcrec_tables.md. Read-only; nothing compiled or run. Cites are in the memfn worktree unless stated.

## BLOCKER

### B1. The define/use "same gate, masks must match" rule refuses legitimate FUNC sites (row_contracts.md s1.2 bullet 3, s3 item 4)

The design says the gate runs on define hooks AND use hooks and "a use whose non-default mask differs from its define's is refused".
- The audit's own matrix shows define and use hooks legitimately differ. OFS ignores `s`/`n`/`lo`/`floor`/`miss` at define and requires them at call (audit s2.3: "I at define; R at call", ofsskip.c:280-283, :420).
- A FUNC site's define hooks are file-scope: `s`, `n`, `lo` are the function's PARAMETERS, so they are unstated at define and stated at use.
- A mask-equality rule therefore refuses every FUNC site pcrec sends today. A subset rule is not enough either: `floor` stated at define but NULL at use must be refused (S8), while `s` NULL at define and stated at use must be admitted.
- The design needs a partition of the fields into DEFINE-time fields (they must agree at use), USE-only fields and BOTH-time fields, in `fields.def`. As written it has one default per field and one mask per site, which cannot express it.
- Related: `mf_define` selects once over define hooks and `mf_use` re-dispatches through `r->arm` (compose.c:275, :304). The gate therefore has to run in two places with different field sets.
- Fix: add a `phase` column to `MF_FIELD` (DEFINE | USE | BOTH), state the use-vs-define check per phase, and re-derive S8 in that vocabulary. Without this, T2 either breaks FUNC sites (breaks byte-identity) or ships a gate that is silently weaker than s3 claims.

## MAJOR

### M1. Q-ROW-1 is a contract change, but the design treats it as an internal table edit (s1.1, s5)

The recommended ruling "`miss` NULL is `n` for FUNC/RETURN and a REFUSAL elsewhere" CHANGES the contract.
- Today generic refuses NULL `miss` for RETURN EXPR (generic.c:646) and the FUNC call (:609). memfn.h and integration.md s14.1 say `miss` is "the value written when no cand exists" and are silent on NULL (audit s3 row 1).
- G2's refusal table, written blind from that contract, treats a missing `miss` hook as a refusal (tests/CLAUDE.md "missing hooks"). Letting generic accept NULL as `n` flips G2's expected outcome.
- The less invasive ruling is the opposite one: NULL `miss` is refused everywhere. It matches the contract text and generic, and changes only OFS (`miss_is_n`, ofsskip.c:382-385). pcrec never sends NULL, so no artifact moves.
- The same applies to the other rulings. `floor` "0" == NULL is already contract text (memfn.h "0 when NULL"), so it narrows no contract. `indent` NULL = "" (disagreement 6), `on_miss` NULL on ASSIGN (7), `n` NULL (5) and `on_miss` statement shape (9) each widen or narrow an unwritten contract.
- Which of these need what:

| ruling | needs |
|---|---|
| any hook that goes from refused to accepted, or the reverse | memfn.h hook comment; integration.md s14.1/s14.2 text plus a `[revN]` section (R4.9) in the R4.7/R4.8 style; G2 expectation change, reported by a D27-blinded author, not by the kit |
| a change in what an existing field MEANS | `MF_SITE_ABI` 4 -> 5 (its comment says "layout and meaning of every struct below", memfn.h:39). Q-M1b-7 and R4.7 are the precedent: M1b bumped it for a pure retirement |
| a `responses.md` notice to the pcrec manager | required whenever a contract sentence moves (D78; R4.7/R4.8 each did) |
| a D80 `docs/spec/` hunk | only if a caller-observable surface moves (see M3) |

- The plan has no step for any of these. T0 says only "`fields.def` with the Q-ROW-1 rulings".
- Fix: add a step "T0c: contract text", with these four deliverables, and make Q-ROW-1 a per-field ruling that names, for each of the 13 cells, which side is edited (the contract, or the row). Prefer "tighten the row" wherever the contract is silent: it leaves memfn.h untouched.

### M2. A kit-exported generic `mf_select` is outside the written charter and the plan never asks the question (s2)

- D146/memfn/CLAUDE.md: the kit "returns the C text for that site". The boundary table's kit column is "the code for each delegated site / the plan over those facts / the form, the fallback". `mf_row`/`mf_table`/`mf_select`/`mf_decision`/`mf_explain` with hit counters is a general-purpose decision-table library: it renders no text.
- The plan.md row says Frank wants the explain record kit-owned, so it can host pcrec's decisions at M5. That justifies the RECORD SHAPE for the kit's own decisions. It does not by itself license exporting a table walker for pcrec's 13 unrelated tables (dfa_pfs, fit_rungs, analyses[] ...).
- Q36 says extraction to a separate repo waits for "a stable API across several migration steps AND a real second consumer". A generic table library inside the kit widens the extracted product's surface (K3's pitch is "bespoke memory functions") before the first consumer exists.
- Q-ROW-3 asks "should pcrec adopt now?" but not "is a decision-table utility the kit's business at all?".
- Fix: either (a) keep T0-T5 internal (`static` in `kit.h`, no `MF_NS` export, no memfn.h section) and export only the RECORD accessor, deferring the generic export to a trigger (a pcrec table actually adopts it, D77); or (b) put a charter ruling in front of Frank: "the kit may export a generic table type". Recommend (a). It also removes the symbol/licence work in m2.
- If (b) stands, the design's own claim "pcrec adopts it through memfn.h, which is the same crossing as `mf_options` and needs no new boundary" is half true. `mf_options`/`mf_run_rows` are READ-ONLY listing accessors (audit7 (c)); no pcrec code calls a kit function to SELECT. Adoption would be the first, and it puts a kit function in pcrec's compile path.

### M3. "Zero-mover throughout" is false for the listing stream (s4 closing paragraph, T1, T2)

- emit_sweep.py stream 5 is "registry dumps: the seven `--list-*` surfaces, whole-file byte identity" (scripts/emit_sweep.py:37-40). T1/T2 change what `--list-axes` prints in two ways:
  1. T2 gives the four arms a name, a deny and (per s1.5) an accessor so they appear in a listing. "The composer arms appear in no listing" is the audit's visibility gap and T2 closes it, so the `memfn` section (or a new axis) gains rows.
  2. T1 "mf_run_rows projects it ... listing byte-identical" is fine ONLY IF the projection keeps the `run-overlap` rows exactly; T2's new denies add `--memfn=no-NAME` spellings.
- Consequences the plan does not list:
  - Stream 5 moves. The plan's gate "0 movers, all streams" fails at T2, or the listing row additions have to be declared EXPECTED movers like `--emit-ir`.
  - `tests/registry/axes_registry_check.sh:186-195` reads the `memfn` section row count against the literal `` `memfn` section floor: N `` in docs/spec/registry.md. Today the section is empty and the check is UNREACHED (line 189). T2 makes it REACHED for the first time. The floor must be born in the same commit (D80, registry.md s6).
  - docs/spec/registry.md s6 (the `axis` transcript, 42 values) goes stale if the arms are listed as an axis rather than as `memfn` rows. docs/spec/table_contract.md §1 and cli.md `--list-axes` (cli.md (old line 914-950)) describe the sections.
  - The registry PASS count rises with the new `[memfn floor]` OK line (and any per-row checks). Any pinned PASS counts in tests/registry must be re-read.
- Also: a deny that removes `ofsskip` falls the site to generic, which is a different text than pcrec's pre-migration text. The deny is therefore not N/A, it is a byte MOVER under the deny (the plan says "its alpha is N/A"). memfn/CLAUDE.md: "a row of the kit's own registry ... that deny is the change's alpha OFF arm" and D144 item 4. The row is then not inert: it is a new observable switch, and it needs a C5 pin and a row in `--memfn=` documentation. Say so, or do not add denies for non-moving arms (compose.c:112-120 chose not to, deliberately).
- Fix: change the T2 gate to "stream 5 moves by exactly the declared memfn rows; streams 1-4,6 byte-identical", pin the floor in the same commit, and list the registry/spec files in T2's deliverable.

### M4. `mf_result` / `mf_use(..., res)` for the record is an ABI change; T6's census conflicts with form_id opacity (s1.3, s4 T6, s5 Q-ROW-2)

- The decision record is delivered "through `res`". `mf_result` is a public struct pcrec reads (memfn.h:297-301); adding fields is a layout change = `MF_SITE_ABI` bump (the Q-M1b-2 precedent appended `stamp_int` and bumped 3 -> 4). `mf_call` has no `res` at all (audit s4), so a signature change on a public entry follows.
- The corpus census "compiles it and asserts the record names the row". That means pcrec-side (or a test harness linking the kit) READS a row name from kit state. C4 class 7 (tests/memfn/arch_blind_check.py:146-149, sabotage S521) bans pcrec comparing `form_id` and memfn.h calls it "opaque; consumers never parse it" (memfn.h:298). A test can legitimately read it; a pcrec build cannot. T6 is "trace build only" so it is compile-time off, but the check has to be amended and the amendment is a contract change.
- audit_kit_rows s4 notes G2 and C5 already read `form_id` for the test side. The cleanest route for the census is the kit-only one: a kit test binary that links `libpcrec.a` and drives the CLI's corpus through the kit's own accessor, not a pcrec build option. That answers Q-ROW-2 without T6.
- Fix: answer Q-ROW-2 "kit-only route" and drop T6 until a trigger; or, if kept, carry the ABI bump and the C4 amendment in the T6 row. Either way, note that `MF_VOCAB` is untouched (nothing about op x handoff x kinds changes).

### M5. D77: T4 (sub-tables) and the pcrec-adoption path have no named measured need; T3 and T5 do

- Needs that ARE measured and named: K96 (a wrong-answer class, G2-reached) and the audit's 8 K96-class cells + 13 disagreements are the evidence for the gate (T0/T2/T3). T5's reach floor answers K35 and is the control G2/g2x already need.
- T4 turns 12 untabled branches into sub-tables. The design's own test is D152's ("several options, interacting preconditions, attached machinery"), and the plan says "wherever they choose between forms. A branch that only spells one form stays code". That is a judgement per branch with no measurement behind it, and there is no soundness incident in any of the 12. The audit lists them as a visibility gap, not a defect. Note also that sub-tables multiply `--memfn=no-NAME` rows and thus the spec floor, C5 pins and G2 per-row floors.
- The pcrec-adoption path (s2 "after C7, `cand_select` becomes a thin wrapper over `mf_select`") is speculative by the plan's own admission ("pcrec's side then decides"). It is also the justification for exporting the generic mechanism (M2). D77/memory "build under measurement": name the trigger or do not build.
- Fix: mark T4 `STATE: held, trigger: the first form-selecting branch that gains a second form or a deny row` (a branch already gets a row the day it moves bytes); build the generic export under a trigger; keep T0-T3 + T5.

### M6. The record-hit counters live in `mf_art`, which is per Job ATTEMPT (s1.4; memfn.h `mf_art` comment "one per Job ATTEMPT")

- A corpus census over many compiles needs cross-art accumulation. A per-art counter dies with the attempt; the size ladder re-emits, so a single compile can contribute several arts. The design never says who accumulates, which is exactly the gap that makes "witnessed" claims unfalsifiable (K35: a floor on a population nobody counts).
- If the accumulator is process-level mutable state in the kit, it breaks re-entrancy of a library linked into `libpcrec.a` (the kit is otherwise instance-state-only) and needs a reset API plus thread rules (tests/thread exists).
- Fix: specify the accumulation point (a caller-owned `mf_hits` array handed in at `mf_art_begin`, or an accessor on the art that the census sums). Do not use a global.

## MINOR

- m1. s1.5 gives `mf_select(table, nondefault, denies, ctx, rec)` but s1.3 gives `mf_select(table, ctx, rec)`. Pick one; the gate needs `nondefault` computed from `(site, hooks)`, so `ctx` must carry the site and both hook sets, and the `applies(const void *ctx)` signature loses type safety that the kit's two existing `applies` (arm: `(site, hooks)`; rc_row: run term) have.
- m2. If the generic export stays (M2): `table.c` needs a `PROVENANCE.md` row and SPDX + provenance header (C16, memfn/CLAUDE.md "Symbols, licence, provenance"); `fields.def` is under `src/` so C16 compares it too (the tracked set is "one row per file under include/ and src/"). Every new external symbol goes through `MF_NS`, and `tests/memfn/c15_allowlist.txt` is BORN EMPTY and stays empty only if every one of `mf_row/table/select/decision/explain` plus the counter accessor is MF_NS'd. Bare `mf_select` is a very generic name in an extracted build (`mf_*` namespace); the kit's other generic names (`mf_site`, `mf_hooks`) share the prefix, but a verb as common as `select` is a collision risk for a stand-alone product.
- m3. The "static assert / startup assert over the table" for "generic honours ALL" is a check that shares its source with what it checks (the `honours` mask declared by the same file author). docs/dev/learnings.md s3 / memory `pcrec-check-design-lessons`. The independent half is G2's per-row floor, which the design does name (s1.4); say that the static assert is only a structural check and is not evidence generic is correct.
- m4. s3 item 5 admits the gate cannot see a row that CLAIMS a field but mishandles it (S2-S7 parenthesization). Honouring `miss` by "claim" in T3 then depends on the G2 hook-style axis, which is a G2/g2x change (a D27-blinded lane's territory). The plan has G2 changes inside T5 but T3's soundness depends on it; order T5's hook-style axis BEFORE T3, or T3 re-adds the S2-S7 bugs undetected.
- m5. `refuse_test` in `fields.def` (s1.2) moves refusals from per-row `kit_fail` calls into a table; `mf_site_check` (compose.c `site_check`, `mf_define` s259-278) already refuses vocabulary violations. State the order (vocabulary gate, then `refuse_test`, then selection) and where the loud-error text names the arm today ("ofsskip: ...") and what it names after.
- m6. s4 says every step gates vs main with "emit_sweep gate" but the kit-side lanes (m1b*, r4c2*) are editing compose.c/runcmp.c/precheck.c concurrently. See the D153 section: a rebase tax, not a design flaw.

## D153 (remodel-first) check

- START-TABLE C2-C7 and DEC-FALLBACK: T0-T5 touch no pcrec file. T1's `mf_run_rows` projection edits `src/dump/axes_dump.c:656-666` ONLY if the accessor's type changes (mf_run_row -> mf_row). That file is the listing consumer; START-TABLE C5/C6 are expected to change the same dump (start_table.md s2.4 D-3: the hand `applies` prose table in axes_dump.c has drifted). Coordinate: keep `mf_run_row` as a read-only projection so axes_dump.c does not change in ROWCON.
- T6 touches `src/gen/memfn_sites.c` (the pcrec-side caller), which m1b/r4c lanes are migrating now. Sequence it after them or drop it (M4).
- Within the kit, D153 item 1 lists "memfn's zero-mover migration steps (R4c/M1 now; R4g M2, R4h M3)" as REMODEL work with priority. ROWCON restructures `arms[]`, `rc_row` and the form branches those steps migrate into. It is the kit manager's own plan, so it is not a D153 violation, but it should be sequenced against M1b/R4c-2 lanes (active: m1b*, r4c2*), not run in parallel against `compose.c`/`runcmp.c`.
- The pcrec-adoption path (s2) correctly waits for C7. Agreed.

## Docs that ROWCON would make stale

| file | what goes stale |
|---|---|
| memfn/CLAUDE.md | "Layout" (`src/` list gains `table.c`, `fields.def`); "The kit's option namespace" (rows now also from arms; `select_arm` reads `opts`; "a SIMD row is inert" unchanged); "The boundary with pcrec" (a generic exported table, if M2(b)); Status paragraph |
| memfn/src/CLAUDE.md | the "FIRST-MATCH arm table (`ofsskip`, `precheck`, `runcmp`, generic)" paragraph (lines 22, 43, 52, 55) and the `arm` interface description (line 11-13) |
| memfn/tests/CLAUDE.md | G2 "reports per-row CHOSEN counts and FAILS if a row has 0" is a new floor on `run_g2.sh`; the refusal-table description changes with Q-ROW-1 |
| tests/memfn/CLAUDE.md (and run_arm_pins.sh) | `ARMS_ROW_FLOOR=34`, `ARMS_EXPECTED` literals (C5), and the census witnesses; `arch_blind_check.py` class 7 if M4 stays |
| memfn/PROVENANCE.md | rows for `table.c`, `fields.def` (C16) |
| memfn/include/memfn.h | `MF_SITE_ABI` comment and number (M1/M4); `mf_hooks` field comments for every ruled field; the `mf_run_rows` comment; the new section's header; `mf_result` |
| docs/design/memfn/integration.md | s14.0/14.1/14.2 (hook semantics), s15.1 (`miss`), new `[rev4.9]` section in the R4.7/R4.8 shape, s22 plan (new step rows), s17 (C5 fixtures), s10.2 (G2 floors); the audit's row "Not counted: `use`, `policy`, `opts`" |
| docs/spec/registry.md s6 | `memfn` section floor literal (born at first row), `axis` transcript if arms become an axis; docs/spec/table_contract.md §1, docs/spec/cli.md `--list-axes` (914-950) |
| docs/spec/match_api.md | stamps sections that cite `MEMFN_FORMS`/`MEMFN_LIBC` (2350, 4025-4048) only if a stamp changes; otherwise unaffected |
| docs/dev/plan.md | the [MEMFN-ROWCON] row (572), its trigger rows ([LIST-TABLES], [START-TABLE] C2's hit counter, K96 row), and any row naming K96 as a gate |
| docs/dev/decisions.md | a new D-id for the ROWCON mechanism and the Q-ROW-1 rulings; D152's "tables" family gains the kit |
| tests/registry/axes_registry_check.sh | `[memfn floor]` goes from UNREACHED to REACHED (lines 186-195) |
| scripts/emit_sweep.py docstring | stream 5 "whole-file byte identity" now has declared movers |

## What the plan gets right

- The allowlist-not-denylist inversion (s1.2) is the correct structural fix for the K96 class, and it matches the repo's own `mk_d27_cell.sh` rule.
- Choosing the kit's own tables as first users and not touching pcrec (Q-ROW-3) is correct under D153.
- Counting rows reached by CHOSEN with a literal floor in spec is a proper independent control (shares no source with the table).

## Verdict

Not ready to implement as written. Fix B1 (define/use phases) before T0 is coded: it changes the shape of `fields.def` and the gate. Resolve the contract-change bookkeeping (M1) and the listing/gate claim (M3) in the plan text; make the charter ruling on the generic export (M2) and park T4/T6/adoption under D77 triggers (M5, M4). With those edits the core (fields.def + honours gate + per-row reach floor, T0-T3 and T5) is sound and worth building.

Counts: BLOCKER 1, MAJOR 6, MINOR 6.
