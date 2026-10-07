# ROWCON r2 critic: reach / visibility / contract re-check (D6, read-only)

Target: `worktrees/memfn/docs/design/memfn/row_contracts.md` rev 2.1 (branch lane/memfn-rowcon).
Checked against: the r1 critic texts, `dispositions.md`, `tests/memfn/site_census.py`,
`scripts/emit_sweep.py` (`--trace`), `Makefile` (KITSRCS/KITFLAGS), `memfn/src/options.def`,
`memfn/docs/journal.md` (R4c listing mover), memfn/CLAUDE.md, learnings §3. Nothing compiled or run.

Counts: BLOCKER 0, MAJOR 6, MINOR 6.
Verdict: REVISE-MINOR. The r1 blockers are resolved in design. The remaining majors are
specification gaps in text that is still cheap to change (rev 2.2), not structural flaws. M1 (gate
vs no-silent-defaults) and M2 (the deny that "is never a supported mode") must be settled before T2/T3b are cut.

## MAJOR

### M1. The gate `nondefault ⊆ honours` has no meaning once there are no defaults (§4.1, §4.2 vs §4.3, §2.2)

Rev 2.1 deletes the default column ("NO default column", §4.1) and says stated values are
explicit tokens (`MF_MISS_N`, `floor = "0"`, `indent = ""`). But §4.3 still admits a row iff
`nondefault ⊆ honours`, and §2.2 still records `subject_mask: the non-default fields`.
If "non-default" is replaced by "stated", the gate breaks. pcrec now states `miss`, `floor`,
`indent` on EVERY site (R-6), so every row that does not read `floor`/`miss`/`indent` (ofsskip at
define: audit "I at define") fails `stated ⊆ honours` and every pcrec site falls to generic. The
zero-mover gate would catch that, but only after T3a is built. If instead the trivial tokens are
treated as "inert", that is a default under another name, which is precisely what Q-ROW-1
removed, and the reach grain "a row reached only at defaults does not count" (§5) is undefined.

Fix: say it in the text. `honours` is per (field, VALUE CLASS), the same classes §4.1 already
declares for reach: `miss: {N-token, other}`, `floor: {"0", other}`, and so on. A row admits a
stated class iff it honours that class. `MF_MISS_N` and `"0"` are then ordinary classes, rows
declare them honoured or not, the reach cell and the honours bit are the same object, and there
is no hidden default. Reword §2.2's `subject_mask` as the STATED mask plus the class bits.

### M2. `--memfn=no-snapshot` ("alpha OFF arm only, never a supported mode") is not expressible in the registry and conflicts with the deny rule (§4.4)

memfn/CLAUDE.md: a byte-moving change "adds its row ... reached as `--memfn=no-NAME`; that deny
is the change's alpha OFF arm". The options.def row is a public, validated, listed switch:
`mf_opts_check` accepts it, `--list-axes` prints it, and `make test-axes` ("every
optimization-axis deny/force flag ... answer-identical to default over the whole corpus") sweeps
every `--list-axes` row. The registry has kinds DENY and PAIR only, no "unsupported/diagnostic"
kind. Consequences the text does not face:
- A user can pass `--memfn=no-snapshot` and get the K96-class hazard back. "Never supported" is
  prose with no enforcement.
- `test-axes` and G2 run every deny. Under `no-snapshot`, the ternary hook text that §4.5 says "STAYS
  valid because the snapshot makes it safe" is unsafe again (S2-S4 reinstated), so G2/the sweep
  either reports wrong answers on the deny or must be told to exclude it. Exclusion needs a
  registry attribute (new X-macro column), a spec sentence, and an independent check that the
  exclusion list is exactly {no-snapshot}.
- Does `no-snapshot` also lift the lexical refusals (comment/`#`/dangling else)? Unstated. Those are
  not byte-moving, so they should survive the deny; say so.
- D144 item 4 is about optimizations; this is a correctness change. Applying the rule is
  defensible (the G1 timing needs an OFF arm), but then the deny's status must be recorded where
  the rule lives.
Fix: either (a) add a registry kind/column `MF_OPT_DIAG` (listed, parsed, excluded from the
answer-identity sweep and from G2 hook-style families, floor counts it separately), with the spec
hunk; or (b) do G1 against the pre-T3b commit as comparator and add NO options.def row (the
CLAUDE.md "per-migration-step comparator" idiom), and say that this change is the one exception to
the "row in the same commit" rule, with Frank's ruling. Recommend (b): it removes a hazard switch
from the user surface. If (a), the T3b package also owes the `memfn` section floor bump (T2 births
it; T3b raises it by one) and the `--list-axes` dump re-pin.

### M3. T3b's snapshot is under-specified exactly where the abi event is decided (§4.4)

The "exact spelling is decided in T3" defers what the abi event pins. Open points that change
bytes and so cannot be decided after the bump:
- EXPR/RETURN-expression handoffs: there is no statement position for `const size_t mf_lo = (lo);`.
  A GNU statement-expression `({ ... })` changes both shape and, inside conditions, evaluation. The
  design never says how an EXPR site snapshots.
- Name collisions: two kit sites in one block redeclare `mf_lo`. Needs braces or a per-site
  suffix; both are byte decisions.
- Hazard 8 is closed "by construction" only by FREEZING the value. If any pcrec `on_cand` today
  legitimately advances a hook variable mid-site and the kit then reads it (a cursor), snapshot
  changes ANSWERS, not just bytes. The census of pcrec's `on_cand`/`on_miss` texts that write a
  hook identifier is the named measurement; it is not in T3b.
- Conversions: a hook whose C type is not `size_t` (uint32 loop var, signed) gets one explicit
  conversion; its width/sign rule is unstated (hazard 6 "one explicit conversion").
- Does the snapshot apply to define-time hooks (file-scope FUNC params) as well as use-time?
  Binding classes (§4.1) exist for exactly this; §4.4 says only "at the top of each site".
Fix: state each in §4.4 or make T3b's first sub-step a decision lane with those five answered
before the byte-moving commit.

### M4. MF_TRACE: the census-turns-it-on claim is false for `site_census.py` as it exists, and the switch can change struct layout (§2.2, §2.3)

- `tests/memfn/site_census.py:build_traced` recompiles only CALLER files over a COPY of
  `build/libpcrec.a` with `-include` shims. The kit's own objects (`compose.o`, the new `table.o`)
  are archive members compiled by the default `make` without `MF_TRACE`. Defining `MF_TRACE` for
  pcrec files does nothing to the engine. So "pcrec's traced build ... defines both" needs either
  (i) a census change to recompile `memfn/src/*.c` with `-DMF_TRACE` and replace those members (and the
  archive-member uniqueness check `members.count(base) != 1` must hold for table.o), or (ii) the
  `emit_sweep --trace` route, whole-tree build via the `cflags` pass-through, where `KITFLAGS = $(CFLAGS)`
  carries `-DMF_TRACE` for free. (ii) needs no Makefile change; (i) is a script change only. The doc
  must say which. It is not a pcrec Makefile change either way, but it IS a change to a test script.
- Two different tools are conflated: `site_census.py` is the C17 SITE census (which sites exist),
  the reach census is a new tool summing REACH/decision lines. §5/T4 should name the new script and its home.
- Layout: §2.3 keeps counters "under MF_TRACE only", per table and per (row, field, class) cell. If
  those counters live in `mf_table` (or the header-only `MF_TABLE_TYPED` wrapper touches them),
  `memfn.h` has `#ifdef MF_TRACE` struct layout, and an object compiled with the flag against a
  kit compiled without it (exactly the census's partial recompile) is an ODR/layout mismatch,
  silently. Keep the counters in a side array in `table.c` keyed by table pointer, with no field in
  any public struct, and say so.
- `REACH lines at exit` implies an `atexit` or destructor in a library linked into `libpcrec.a`
  plus process-global counters; r1 contract M6 rejected globals for reentrancy. Acceptable under
  MF_TRACE only, but state "trace builds are single-threaded; tests/thread never runs traced".
- Stderr pollution: in the combined traced build both `CANDTRACE` lines and the kit's blocks go
  to stderr. `emit_sweep.py` filters by `CANDTRACE\t` tag (lines 1170-1189), so the kit block must
  never begin with that tag, and `emit_sweep`'s "trace build's stdout must equal default" holds
  only if nothing prints to stdout. Add both as stated rules. §2.2's "a migrated trace line is the
  same line" is also inconsistent with "one block per decision": say whether the kit prints a
  CANDTRACE-format line or its own block.
- The census PARSES trace text, which makes the print format a machine contract (r1 vis m2). State
  that a line grammar is fixed, versioned, and that `mf_decision_print` is the single producer.

### M5. Reach independent controls are row-grain; the cell grain still has no control that avoids the engine's source (§5, r1 reach B1/B2)

`rows.tsv` is one line per (table, row) with reach class and witness: row grain. The text signature
is per row. G2 agreement is "on every reached cell", where "reached" comes from the engine counter
and the cell set from `fields.def` classes: both from the engine's own source, the shared-source
shape learnings §3 names. So the claim "none shares a source with the engine or the profile" holds
for the row layer and fails for the cell layer: a class left out of `fields.def` is a cell nobody
expects. Also unstated: who writes the signatures (r1 reach B2.2 asked for an author who has not
read the row's code), what `rows.tsv`'s "reach class" values are (they should BE §5's closed
vocabulary), and the witness-drift items that r1 M2 listed and rev 2.1 skipped: hard-fail on an
empty or skipped witness list, an executed-witness count in the verdict (K35), a pcrec-side invariant
(stamp) per corpus witness so a failure separates "site vanished" from "row changed".
Fix: add a committed `cells.tsv` (row, field, class, witness id) written from the contract text by
the blinded author (g2x), diffed BY NAME against the `fields.def` classes both ways; the census
verdict prints compiles run, decision lines parsed, witnesses executed, cells hit, all with
non-zero floors. The census "population" (compiles traced, decision lines parsed) is otherwise
uncounted: a table that silently fails to trace (the layout/partial-recompile case above) reads as
"all rows unreached", loud, but a trace that covers only half the tables reads as "half unreached".

### M6. Q-ROW-4 fallback ("if ruled no, Layer 1 shrinks to a kit-private walk") is not coherent with the rest of the plan (§6, §2.4, §3, T0)

If Layer 1 is kit-private, then: (a) the "partially generalized (G)" acceptance leg is dropped, not
deferred; (b) `mf_table_rows` is the `--list-axes` source for the memfn section, which is kit
output either way, so it survives; (c) `MF_TABLE_TYPED` and `mf_query.site` exist only for pcrec
adoption (§3 customers 1, 2, 5; Appendix A), so they go; (d) T0's `cand_rows`-SHAPED fixture has
no purpose; (e) "decisions move into the kit (M)" still requires the kit to host pcrec's
tables later, which a private walk cannot do. So "no" silently turns (G) and (M) into non-goals.
Say that: the fallback is "Layer 1 internal now (static, no `MF_NS` export, no memfn.h section),
exported when a pcrec table adopts it (D77 trigger)", which keeps T0 and Layer 2 identical and
only moves the header. Also unaddressed from r1 contract M2: the fixture-on-paper proof that
satisfies (G) while no consumer exists is the thing the charter question asks Frank to bless;
the plan should say T0 is cut so it costs the same under either answer.

## MINOR

- m1. Two deny namespaces remain (r1 vis M3): the row's `deny` is a `uint64` of "caller's deny
  bits (pcrec: PCREC_NO_*)", but the kit's denies are `MF_D_*` in `site.denies` AND `--memfn=no-NAME`
  strings in `opts`. §2.1/§2.2 does not say how `query.flags` is built for the kit nor what
  `DENIED.mask` names. One sentence.
- m2. §2.4 says `mf_table_rows` is the single source of the axis registry (D152 one spelling), but
  the `memfn` section "is read from `mf_options()`" and `--memfn=` is parsed from `options.def`,
  "what is printed and what is parsed are one table". Arm denies must therefore come from
  options.def rows, or options.def rows must be generated from the arm table; otherwise there are
  two registries and the section floor shares source with the thing it floors. Name the direction.
- m3. §2.2 "the SET-compare diff gate reads the same four fields": `PCREC_CAND_TRACE_RECF` (runtime
  formatted row names) is not in Appendix A and `mf_row.name` is static, so formatted names remain
  outside the engine. Add the row to Appendix A as "stays pcrec's".
- m4. No `NOT_EVALUATED`/`EVALUATED` verdict (r1 vis M7, m1): rows after the winner and rows
  outranked-but-true are invisible. Cheap, and it separates "shadowed" from "false everywhere",
  which the shadowed-row control (r1 reach m3) needs. `fit_rungs`' derived-predicate deny (r1 vis M6.4)
  also has no caller hook.
- m5. Where `mf_check_stated` runs relative to selection (§4.2: "whenever the CHOSEN row reads an
  unstated field") matters: refusing after selection means a lower row that does not read the field
  is never tried. That may be intended (loud), but it must be a stated ordering, and the decision
  record needs a verdict kind for it (REFUSED_UNSTATED naming the field), which §2.2's kind list lacks.
- m6. §4.5 lists integration.md rev 4.9, `MF_SITE_ABI` 4→5, responses.md, G2; it omits the
  `memfn.h` hook comments and the NEW public constants (`MF_MISS_N` etc., plus the `mf_table*`
  section if exported). Those are header changes in the extraction surface. Also T3b is a SECOND
  contract-layer bump (pcrec abi) distinct from `MF_SITE_ABI`: name both so a grep for "the abi
  number" (D94) is unambiguous.

## T3b package completeness (asked)

Present in §4.4/§7: abi bump with grep re-pins (D76/D94), stamp values, D80 spec hunk, G1 at both
layers, deny row `--memfn=no-snapshot`, same commit.
Missing or unstated:
1. The `memfn` section floor in `docs/spec/registry.md` §6 (T2 births it; T3b +1) and the `--list-axes`
   dump re-pin, if the deny row exists (see M2); `axes_registry_check.sh` `[memfn floor]`.
2. The `MEMFN_FORMS`/`MEMFN_LIBC` stamp semantics: "FORMS is `none` iff identical to its SIMD-off
   compile". Whether the snapshot changes the stamp value for all artifacts is not stated; say it
   explicitly and run the registry/codegen/rxtsource suites (D94 addendum, 2026-09-19), which the
   memory index says still move with the number.
3. `make test-codegen` before delivery (CLAUDE.md situation index) and the identity gate (B) pin.
4. The decision lane (M3) and the on_cand/on_miss hook-write census.
5. C5 pins (`ARMS_EXPECTED`, `ARMS_ROW_FLOOR`) and the C12/C17 ratchets: artifact text moved at every site.
6. G2 expectation updates by the blinded author (listed under §4.5, but ordered AFTER the T3b commit
   in practice: G2 must not be red in between). Sequence or hold G2.

## T2 listing mover vs R4c

R4c's precedent (journal 2026-10-06/07, Q-M1b-3): a kit row accessor so `--list-axes` stream 5
stays byte-identical, and a declared `--list-axes` PAIR mover with the D80 hunk and registry
re-pin. T2's treatment follows the same recipe (declared mover, D80 hunk, re-pins, floor REACHED,
same commit), so the shape is right. Gaps: which section and which row-key spelling the arms take
(r1 vis M5 / table_contract.md §Sections) is still not written; the audited consequence for
`docs/spec/registry.md` §6 (42-value axis transcript if arms become an axis) and `cli.md`
`--list-axes` is not listed; and the arm denies' parse side (m2). Also "options.def born empty" is
still true today (0 `MF_OPT(` rows), so T2 is the FIRST row in the registry: the first-row
floor-born event deserves its own sentence, not just "goes from UNREACHED to REACHED".

## Docs that rev 2.1 makes stale

| file | what goes stale |
|---|---|
| memfn/CLAUDE.md | Status paragraph; "Layout" (`src/` gains `table.c`, `fields.def`); "The boundary with pcrec" table (the kit now also owns a decision engine: needs the Q-ROW-4 charter line); "The kit's option namespace" (rows now also come from arm tables; a diagnostic kind if M2(a)); "Every kit change that moves bytes carries its own deny" (the no-snapshot exception) |
| memfn/src/CLAUDE.md | the first-match arm table description and `arm` interface (now an `mf_row` head + profile) |
| memfn/include/memfn.h | `MF_SITE_ABI` 4→5 and comment; hook comments for every field (stated vs unstated, `floor` "0 when NULL" now false, `miss` NULL); new `MF_MISS_N` and tokens; new section for `mf_table`/`mf_select`/`mf_decision` if exported; `mf_run_rows` comment |
| memfn/PROVENANCE.md | rows for `table.c`, `fields.def` (C16); `MF_NS` allowlist check C15 for the new exports |
| docs/design/memfn/integration.md | §14.0-14.2 and §15.1 hook semantics, new rev 4.9 section, §22 plan rows, §10.2 G2 floors, §17 C5 fixtures; the audit's "not counted" row |
| tests/memfn/CLAUDE.md | C5 pins (`ARMS_ROW_FLOOR`, `ARMS_EXPECTED`), census scripts (new reach census, `site_census.py` change for kit-member recompile), C4 class 7 only if `form_id` is ever read pcrec-side (it is not, T6 dropped), new `rows.tsv`/`cells.tsv`; G2 refusal table and per-cell floors |
| memfn/tests/CLAUDE.md | G2 refusal-table description (unstated fields refused), hook-style families |
| docs/spec/registry.md §6 | `memfn` section floor literal (first row born), `axis` transcript if arms become an axis |
| docs/spec/table_contract.md, cli.md `--list-axes` | section shape and row-key spelling for the arms |
| docs/spec/match_api.md | stamps sections for `MEMFN_FORMS`/`MEMFN_LIBC` (T3b); the abi-number readers (D94 grep); the caller-text contract hunk (D80) |
| docs/dev/plan.md, decisions.md | [MEMFN-ROWCON] row; a D-id for Q-ROW-1 and Q-ROW-4; D152 "tables" family gains the kit; any row naming K96 as a gate |
| tests/registry/axes_registry_check.sh | `[memfn floor]` UNREACHED→REACHED (T2), +1 at T3b if the deny row exists |
| scripts/emit_sweep.py docstring | stream 5 "whole-file byte identity" now carries declared movers; `--trace` docs gain the kit block rule (M4) |
| memfn/README.md, memfn/docs/responses.md | the notice for the contract change (R-6, rev 4.9) |

## By-id table (r1 critic_reach / critic_visibility / critic_contract)

Status: R = RESOLVED, P = PARTLY, N = NOT, by rev 2.1.

| id | r1 finding | status | rev 2.1 § and residual |
|---|---|---|---|
| reach B1 | reach grain per row | P | §2.3, §4.1 classes, §5 Grain. Cell grain defined; cell SET has no independent control (M5); honours-by-class missing (M1) |
| reach B2 | controls share source | P | §5 controls 1-4. rows.tsv/signatures are row grain; signature author unnamed; cell layer shares `fields.def` (M5) |
| reach M1 | sub-table rows uncounted | P | T4 dropped (§7, D77). Arm-internal choices (PAIR vs single, precheck rest, generic body forms) stay uncounted until a K96-class trigger |
| reach M2 | witness drift | P | §5.2 signatures, §5.4 deny-delta. Empty/skipped witness hard-fail, executed count, pcrec-side invariant: N (M5) |
| reach M3 | T6 not needed | R | §2.2 (T6 dropped, MF_TRACE); but see M4 on whether the channel actually works |
| reach M4 | closed unreachable vocabulary | R | §5 (total-fallback / pending-site:trigger / contract-reach:family). Pinned count per reason not stated (minor) |
| reach M5 | count at successful render, aggregation | P | §2.3 (successful render, census sums). A later-failing art (sticky error) still credits earlier sites; stated for the kit only. Aggregation tool unnamed (M4) |
| reach m1 | K35 populations (6 sub-items) | P | deny-delta R (§5.4); per-field cells R (§5); refusal manifest N; define/use mismatch floor N (rule withdrawn, no replacement floor); executed witnesses N; `ignores` vs `honours` N (§4.3 says generic honours every handled field, still vacuous-able); probes for stated tests N |
| reach m2 | hint-sensitive rows | N | unaddressed (hints stay out of scope; one sentence would close it) |
| reach m3 | shadowed rows | P | rows.tsv requires a witness per row; no "first applicable ignoring lower rows" definition, no EVALUATED counter (m4) |
| vis B1 | record vs C1/CandRow | R | §2.2 mapping, scope/route/site, Appendix A. Residual: `_RECF` formatted names (m3); "same line" vs "block" (M4) |
| vis B2 | no named reader | P | §2.2 MF_TRACE + G2/CLI print. The human-level surface (an explain flag) is neither provided nor consciously deferred; channel mechanics broken for site_census (M4) |
| vis M1 | full failing mask | R | §2.2 GATED mask = ALL failing fields |
| vis M2 | PRED_FALSE reason | R | §2.1/2.2 `applies` returns reason code |
| vis M3 | which deny switch | P | §2.2 DENIED mask; kit's two namespaces unresolved (m1) |
| vis M4 | fixed record, nesting | R | §2.2 `MF_DECISION_MAX`, overflow flag, `parent` |
| vis M5 | listing claims | P | §2.4, T2 declared mover. Section/spelling, registry §6, deny parse side open (T2 section, m2) |
| vis M6 | generality blockers | P | route/scope R, totality R (`on_none`), typing R (`MF_TABLE_TYPED`), C15 R (T0), fast path R (`rec==NULL`, MF_TRACE off); derived-predicate deny (fit_rungs) N |
| vis M7 | EVALUATED, deny-delta, two counter homes | P | deny-delta R (§5.4); EVALUATED N (m4); canonical home: kit counts at render, pcrec at select, "canonical at migration" unstated |
| vis m1 | rows after winner | N | not stated (m4) |
| vis m2 | explain wording not contract | N | and made worse: the census parses trace text (M4) |
| vis m3 | declared site keys for kit sites | R | moot: kit prints its own blocks; must not use the `CANDTRACE\t` tag (M4) |
| vis m4 | generic reach measured | R | §2.3, §5 census counts it |
| contract B1 | define/use phases | R | §4.1 binding (SITE/DEFINE_BOUND/USE_ONLY/DEFINE_ONLY), "each phase runs its own gate". §4.3 describes one gate only; write the use-phase gate (thin) |
| contract M1 | contract change bookkeeping | P | §4.5 rev 4.9, ABI 4→5, responses, G2. Omits memfn.h, new constants, the pcrec-abi distinction (m6); Q-ROW-1 now a different (larger) contract change than the one r1 reviewed |
| contract M2 | charter | P | Q-ROW-4 asked (§6) but PENDING; fallback incoherent (M6) |
| contract M3 | listing zero-mover false | P | T2 "ONE DECLARED listing mover" (§7). Same-commit floor birth R; remaining gaps under "T2 listing mover" above |
| contract M4 | res ABI / form_id | R | §2.2: no `mf_result`/`mf_call` change, no `form_id` compare |
| contract M5 | D77 for T4/adoption | R | T4 dropped; adoption an offer; Q-ROW-3 answered |
| contract M6 | counters in mf_art | R | §2.3: not in `mf_art`; census sums. New globals under MF_TRACE need the single-thread statement (M4) |
| contract m1 | mf_select signature | R | §2.1 one signature |
| contract m2 | PROVENANCE/SPDX/MF_NS | R | T0 C15/C16 |
| contract m3 | static assert shares source | R | §4.3 replaced by G2 per-field cells on generic |
| contract m4 | order hook-style axis before T3 | P | T3b snapshot removes the S2-S7 class structurally, but T2's `honours` claims still land before T4's cells |
| contract m5 | check ordering and error text | P | §4.2 refusal names the field; the order vs selection, and the error text naming the arm, not stated (m5) |
| contract m6 | D153 rebase tax | R | accepted/noted (dispositions T-J) |
| contract (D153 section) | pcrec files touched | R | T0-T4 touch none; T2's axes_dump hunk re-checked at cut |
| contract (stale docs) | docs list | P | rev 2.1 does not restate the list; see the table above for the updated one |

## Verdict

REVISE-MINOR. No blockers. Rev 2.1 resolves the r1 blockers (reach grain, visibility channel,
define/use binding) at design level and its trace route needs no pcrec hook. Fix before the T2/T3 cuts:
M1 (honours per value class under no-defaults), M2 (the no-snapshot deny), M3 (snapshot specifics), then M4
(trace plumbing) and M5 (cell-grain control) before T4, and M6 when Frank rules Q-ROW-4.
