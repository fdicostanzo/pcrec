# CODE REVIEW SYNTHESIS COLLATION (2026-09-17)

Lane `collate` (sonnet, mechanical collation — no judgment exercised on
finding validity). Inputs: the ten delivered lens reports (lens 7's
deliverable is folded into lens 4's report per the ratification's "7
merges into 4" disposition), **plus `emitvm_second_pass.md`, added as a
twelfth source once delivered** (cited `EP2` below) — the chartered
second pass over `src/gen/emit_vm.c` that lenses 1, 2, 5 and 10 all
separately named as owed (§2.7/§6).

Source paths (each lens cited below by `L<n>` + its own finding ID; EP2
uses the same convention):

- L1 `worktrees/lens1dup/docs/dev/reviews/lens_reports/lens1_semantic_duplication.md`
- L2 `worktrees/lens2sep/docs/dev/reviews/lens_reports/lens2_domain_tool_separation.md`
- L3 `worktrees/lens3cfg/docs/dev/reviews/lens_reports/lens3_config_centralization.md`
- L4 `worktrees/lens4clar/docs/dev/reviews/lens_reports/lens4_clarity_archaeology.md`
- L5 `worktrees/lens5unit/docs/dev/reviews/lens_reports/lens5_unit_seams.md`
- L6 `worktrees/lens6dep/docs/dev/reviews/lens_reports/lens6_dependency_rxt_cut.md`
- L8 `worktrees/lens8err/docs/dev/reviews/lens_reports/lens8_error_cleanup.md`
- L9 `worktrees/lens9pub/docs/dev/reviews/lens_reports/lens9_public_surface.md`
- L10 `worktrees/lens10kit/docs/dev/reviews/lens_reports/lens10_emission_kit_charter.md`
- L11 `worktrees/lens11alt/docs/dev/reviews/lens_reports/lens11_function_altitude.md`
- EP2 `worktrees/emitpass2/docs/dev/reviews/lens_reports/emitvm_second_pass.md`

(There is no lens 7 file — its charter is carried inside L4 §2/§3/§4 per
the ratification.)

Vocabulary normalized to A4 (severity: CORRECTNESS-RISK / MAINTAINABILITY /
POLISH; effort: MECHANICAL / LOCAL / CROSS-CUTTING / DESIGN-EVENT) exactly
as each report states it. Where a report used a compound or hedged label
(e.g. "MAINTAINABILITY with a latent CORRECTNESS-RISK", "MAINTAINABILITY
trending CORRECTNESS-RISK"), the row preserves the compound verbatim rather
than forcing it into one bucket, and is flagged **[compound]**.

---

## 1. FINDINGS TABLE

One row per finding, cited by `L<n>-<id>`. `Cross-ref` lists other
findings touching the same code, mechanism, or population; a bare
mention of another lens (no id) means the connection is thematic rather
than a shared site. Severity/effort as each report states verbatim.

### Lens 1 — semantic duplication

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| L1-X1 | Extract the whole-tree AST spine-walk traversal (75 hand-written sites, 48 exhaustive `AKind` switches); keep each predicate's own exhaustive switch, only the descent moves | `src/opt/atomic.c` (9 walks) + `callgraph.c:cg_walk` + `postresolve.c:pr_walk` + `lower_enc.c` (2 walks) | CORRECTNESS-RISK | CROSS-CUTTING (stageable) | 6 files, 6 sabotage rows (S91,S97,S104,S158,S159,S174), 3 codegen checks | L5-R5 (unit net for the merged walk); L11-F7 (per-kind *producers* — X1 explicitly does not cover them); L11 §5.1 item 3 (probed-held: the nine predicates must not merge, only the traversal) |
| L1-X2 | `cg_walk`/`pr_walk` are edge-policy identical (`group_frac` 1.000 both); merge into one `pcrec_ast_visit` | `src/opt/callgraph.c:121-147`, `src/opt/postresolve.c:92-122` | MAINTAINABILITY | MECHANICAL | 2 files, 2 sabotage rows re-aimed (S-U10, S171 — quote the call text, not the body) | L5-R5 (recommends the check be written against this merged function FIRST, before X1) |
| L1-X3 | Saturating add/mul written 3× (mrl/vm/callgraph); `mrl_sat_add`≡`vm_fadd` after macro expansion; nothing checks the two prose statements of the requirement agree | `src/opt/mrl.c:93-104`, `src/gen/emit_vm.c:3136-3148`, `src/opt/callgraph.c:458-471` | CORRECTNESS-RISK | MECHANICAL | 3 files, 3 sabotage rows re-aimed (S58,S59,S-U4) | L5-R2 (the unit check X3 needs before it's safe — R2 IS the precondition test for X3's own `cg_sat_add` guard question); L3 rider (`CG_EXP_INF` vs `PCREC_MINW_MAX` — same value, two sources, filed as lens 3's) |
| L1-X4 | Three byte-identical arena `strndup` helpers (backrefs/named-groups/recursion); no arena-string library | `src/parse/mod_backrefs.c:141-147`, `mod_named_groups.c:76-82`, `mod_recursion.c:99-105` | MAINTAINABILITY | MECHANICAL | 4 files, 0 checks (verified by grep), 0 emitted bytes | L8-F4 (the *fourth*, `rxt_source.c`'s arena strndup pair, is the one that does NOT take `Ctx*` and cannot diagnose OOM — X4's three correct ones are the contrast) |
| L1-X5 | Growable arena array invented ~10 times (double-on-full, arena copy, zero new element) | `src/parse/rxt_source.c` (6 sites), `cpset.c:72-81`, `atomic.c:376-387`, `lower_enc.c:202-212`, `cli/main.c:362-373` | MAINTAINABILITY | LOCAL | 5 files, 1 sabotage row re-aimed (S201) | **OVERLAP CLUSTER — see §2.1.** L2-L2-8 (7), L5-R3 (13), L11 §6 item 1 (28) |
| L1-X6 | `mod_backrefs.c`/`mod_recursion.c` share 6 clone groups; group-relative-offset arithmetic factored in one file, re-typed inline in the other | `mod_backrefs.c` vs `mod_recursion.c`, multiple functions | MAINTAINABILITY | LOCAL | 3 files, 5 sabotage rows name backrefs.c + 1 names recursion.c, 2 codegen checks | L11-F10 (the *intra-function* triplication inside `pcrec_brport_g`'s `\g` parse — X6's cross-file framing does not reach it) |
| L1-X7 | DFA table emitter written 6 times (header/16-per-line wrap/indent/brace identical; only cell type/length/expression vary) | `src/gen/emit_dfa.c` 6 functions, 2610-3530 | MAINTAINABILITY | MECHANICAL | 1 file, `run_premul_table.sh`, 0 sabotage rows, byte-identity gate is the proof | L2-rank4 (table *writing* unfactored vs. table *selection* being the tree's model instance); L5-R6 (conditional unit net, pending a population census of `N∈{0,1,15,16,17}` and mod-16 residues) |
| L1-X8 | 73 hand-typed `#define <PREFIX>_NAME` stamp sites, no `emit_stamp_str/int/bool` helper | `src/gen/emit_vm.c` (52 sites), `emit_dfa.c` (21 sites) | MAINTAINABILITY (real D94 benefit) | LOCAL | 2 files, every codegen/abi check that greps a stamp name | L10 kit item (3) (adopts X8 verbatim, recommends it ride stage 3); **L11-F1 CONFIRMS X8 EXACTLY — all 52 `emit_vm.c` sites are inside `pcrec_emit_vm`, zero in `vm_render_listing`, which corrects L1's own ADDENDUM-1 join-table row** (L11 §0, §6 correction); **EP2 §2.1 independently RE-CONFIRMS the exact count** (52 sites, all at line ≥8539, 36 through `sb_printf`) and places X8 as step 10 of its wave sequence — riding L10's stage 3 rather than leading it, since it is the sequence's only abi-adjacent step and needs L10's `sb_name`/`sb_upper` substrate first (§2.8 item 4) |
| L1-X9 | Optimization-axis table has 3 hand-maintained sources + 2 awk scrapers reconciling them; `cli_parse` 20 `-fno-X` arms, `axes_dump.c` 178-line hand-written function | `cli/main.c:379-809`, `src/parse/axes_dump.c:375-668`, `lib/pcrec.h` | MAINTAINABILITY, trending CORRECTNESS-RISK | DESIGN-EVENT | `cli/main.c`, `axes_dump.c`, `lib/pcrec.h`; DELETES 2 awk scrapers rather than re-aiming them | **OVERLAP CLUSTER — see §2.2.** L2-L2-7 (`--tune` menu duplication), L11-F6 (`emit_predicate_axes` — X9 IS THE WHOLE REMEDY, no split proposed), L11-F3 (`cli_parse` — X9+X10 remove ~1/3 of the body) |
| L1-X10 | CLI integer-valued option arm written 5×; magic prefix-length numbers repeated | `cli/main.c:568,585,647,660,701` | POLISH | MECHANICAL | `cli/main.c` only; 13 codegen scripts reference the file but none plants inside these arms | L11-F3 (used directly for `cli_parse`'s 5 `strtol` arms) |
| L1-X11 | Enum-to-string family: 14 switches, all `group_frac` 1.000; `RxtSchemaScope` rendered 3 ways in one file | `src/parse/rxt_schema.c` (7), `syntax_dump.c` (4), `rxt_source.c` (2), `definitions.c` (1) | MAINTAINABILITY | LOCAL | 4 files, 1 sabotage row re-aimed (S241) | L2-rank5 (**different files, same class** — L2 recommends NO CHANGE for `syntax_dump.c`'s 4 mappers under D82 bound 3; not a contradiction, disjoint populations) |
| L1-X12 | `strcmp` ladders that are lookups (`stamp_macro_of`, `override_name`) — a 2-column table written as control flow | `axes_dump.c:150-169`, `limits_dump.c:38-44`, concentrated also in `rxt_source.c` (11), `cli/main.c` (6) | POLISH | MECHANICAL | per-site, tiny | L11-F9 (`rxt_source.c`'s TSV row writer — X12 covers the file's 11 ladders but not this function); L11 §7 (the tree-wide scan finding only 7 functions with ≥5 `strcmp` calls — `stamp_macro_of`/`cli_flag_of` are 2 of the 7, i.e. X12's own members) |

**Rejected-as-duplication groups (L1 §2, not filed as findings; recorded here for completeness, moved to §5 PROBED-AND-HELD):** clone group 7 (`pf_emit_*` prefilter pairs — caller-observable stamp difference), group 4 (module ports — doorway contract, not duplication), group 26 (`axis_row`/`limit_row` — correct TSV-printer shape), group 1's low-`group_frac` members (long functions containing one walk instance, not clones).

### Lens 2 — domain/tool separation (text-emission mechanism map)

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| L2-L2-1 | 49 emitter fragment buffers hand-pick a size where `PCREC_MAX_EMIT_NAME_LEN` exists; K38 is the recorded miscompile of exactly this | `emit_vm.c` (41), `emit_dfa.c` (8) | CORRECTNESS-RISK | LOCAL (size sweep) / CROSS-CUTTING (`txt_f` fold) | 2 files; 24 sabotage anchors direct, 89 in radius; 5 of 8 source-grepping checks; no abi event | **OVERLAP CLUSTER — see §2.3.** L3-F6 (94, whole tree), L10-L10-1 (48, re-measured, REVISES SEVERITY downward — see §2.3); L5-R4.1 (the unit check that makes the acceptance claim mechanical) |
| L2-L2-2 | No fragment primitive exists; ~105 `snprintf`-into-`char[N]` sites; `vm_rolef` is 90% of the primitive and truncates anyway | `emit_vm.c:754-770` | MAINTAINABILITY | CROSS-CUTTING | same wave as L2-1 | L10 kit item (1) `sb_fragf` (adopts, D82-bound-3-verified against `vm_rolef`+`derived_name`+43 stack sites) |
| L2-L2-3 | Taught primitive for prefix interpolation (`pcrec_enc_emit_text`) already exists at 2 call sites while the emitters hand-perform the identical op 652×; recommends AGAINST a wholesale conversion pending measurement | `src/gen/enc/enc.c:88-94` vs. `emit_vm.c`/`emit_dfa.c` | MAINTAINABILITY | **DESIGN-EVENT** (abi event if attempted) | emitted bytes move ⇒ abi bump + full D76/D94 re-pin | **SUPERSEDED — see §2.4.** L10-L10-7 takes the measurement L2 named and CLOSES the question (verdict: do not do it, on three independent countings); L10-F2 decomposes the 652 to 306 prefix-bound |
| L2-L2-4 | 5 independent TSV row emitters, 2 incompatible escapers, 3 dump files escape NOTHING; `syntax_dump.c` has an escaper its TSV path doesn't call | `rxt_source.c`, `syntax_dump.c`, `axes_dump.c`, `limits_dump.c`, `schema_dump.c` | MAINTAINABILITY (+ latent CORRECTNESS-RISK) | LOCAL | 5 files; 2 sabotage anchors; `tests/rxtsource` field-count pins; no abi event | L10 kit items (4)/(5) `sb_field`/`sb_row` (adopts verbatim, promotes `put_escaped`); L5-R4.2 (the unit check — structural no-control-byte property + injectivity property); L11-F9 (`pcrec_rxt_source_tsv`'s header/row-writer table-not-actually-shared defect — same file, distinct concern from escaping) |
| L2-L2-5 | `cli/main.c` has no diagnostic channel: 76 open-coded `fprintf(stderr,…)`, 72 hand-writing `"pcrec: "` | `cli/main.c` | MAINTAINABILITY | MECHANICAL | 1 file; 0 sabotage anchors; `tests/cli` wording pins (D26: unchanged) | L10 kit item (7) `cli_err` (adopts unchanged, stage 2); L10-L10-4 (restates as a wave-1 stage) |
| L2-L2-6 | `cli_parse` is a 64-arm `if`/`else if` chain over 62 option spellings; file's own `raise_only_limits[]` already argues for the table it didn't generalize | `cli/main.c:379-809` | MAINTAINABILITY | CROSS-CUTTING | 1 file; 0 anchors; `tests/cli`; no abi event | **SAME FINDING as L11-F3**, which adds the `--` correctness hazard (`!no_more_opts &&` re-typed 59×) and the lens-1 join (X9+X10) |
| L2-L2-7 | 8 valid-value menus, 1 table-driven; `--tune`'s menu is a second spelling of `tune.c`'s own alias table (D103 makes `tune.c` the dial's one home) | `cli/main.c` 8 sites | MAINTAINABILITY | LOCAL | 1 file + 2 registries; no abi event | L1-X9 (axes-table centralization, same mechanism one level up) |
| L2-L2-8 | Growable-array append has 7 open-coded copies (clone groups 10 and 3) | `rxt_source.c`, `cli/main.c`, `emit_vm.c` | POLISH | LOCAL | 3 files; **shared with lens 1 — dedupe in synthesis** (L2's own instruction) | **OVERLAP CLUSTER — see §2.1.** L1-X5 (10), L5-R3 (13), L11 §6 item 1 (28) |
| L2-L2-9 | DFA table *writing* unfactored though table *selection* is the tree's exemplary taught primitive | `emit_dfa.c` groups 11, 7 | POLISH | LOCAL | inside the 113-anchor radius ⇒ ride step 3 or skip | L1-X7 (same population, L2 frames it as the writing/selection contrast); L5-R6 |
| L2-L2-10 | Four `group_frac` 1.000 enum→string mappers in `syntax_dump.c`. **RECOMMEND NO CHANGE** | `syntax_dump.c` 4 functions | — (anti-finding) | NONE | none | L1-X11 (different files — see L1-X11's cross-ref) |

### Lens 3 — magic numbers / config centralization

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| L3-F1 | D90's `limits_check.sh` detector is keyed on the constant's NAME (`MAX\|MIN\|CAP\|LIMIT\|BUDGET\|THRESHOLD\|_LEN\|DEPTH\|NEST`); a tuning constant spelled otherwise (`SIZE_TERM_BAR_DEFAULT`, `C_MEMCHR`, etc.) is invisible; 14 such `#define`s found, 8 meet the allowlist's own admission criterion and are on it for none of them | `tests/registry/limits_check.sh:277`; `compile.c:458`; `prefix_k.c:260-295` | MAINTAINABILITY | LOCAL | 1 check file; 0 source files if allowlist-only; 0 sabotage anchors | **[judgment call, marked as such by the author]** — proposes inverting the filter (scan all numeric `#define`s regardless of name) rather than widening vocabulary a third time; RULING-WORTHY, see §3 |
| L3-F2 | `[ART-SIZE]` ladder's two parameters (threshold, bar%) live in two homes — one is a `limits.def` row, the other a bare `#define` argued at its site but on no allowlist | `src/core/compile.c:458`, `src/core/limits.def:161` | MAINTAINABILITY | MECHANICAL (or none) | 2 files if moved; re-pins `limits_check.sh` manifest + `docs/spec/limits.md` §3 if a row is added | RULING-WORTHY — author offers two dispositions (a) deliberate-and-document vs (b) accidental-and-add-row, does not choose; see §3 |
| L3-F3 | FNV-1a's constants open-coded 9× across 2 files, same algorithm written twice (`dhash`/`minimize.c` inline loop); nothing names the algorithm | `src/ir/dfa.c:852-866,302,383`, `src/opt/minimize.c:130-134` | MAINTAINABILITY | MECHANICAL | 2 files, 0 checks, 0 emitted bytes (blast radius genuinely nil, verified) | **Author states the lens-1 loop (ADDENDUM 1) applies directly** — the shared abstraction is `fnv1a_32_init`/`fnv1a_32_mix`, X-style |
| L3-F4 | `"requires module '%s'"` spelled 20 ways in 8 distinct format strings outside the one ruled `RegDiag` home; includes a repeated non-ASCII em dash and a byte-identical string split across two modules | `mod_uprops.c` (9 copies), `ext.c` (4), `mod_modifiers.c`, `mod_recursion.c`, `mod_backrefs.c`, `parse.c`, `syntax_dump.c` | MAINTAINABILITY | LOCAL | 6 source files; ~80 test files bind to RENDERED text (zero re-aim cost for a byte-preserving change) | L1-X4/X6 (same "missing library" class, different phrase); adjacent to L3-F5 (same mechanism, smaller scale) |
| L3-F5 | `"missing closing ) for group"` duplicated at 8 sites; the comment licensing the duplication ("a module owns a DIFFERENT message") is FALSE — 7 modules spell it identically | `parse.c:1404`, `ext.c` ×2, 5 `mod_*.c` files | MAINTAINABILITY (+ docs-accuracy edge) | MECHANICAL | 7 source files, 4 test files (rendered text only); 1 NINTH home in `tests/registry/registry_check.c` (compiled-in `want=` string — a check sharing a source with what it checks) | L4 territory (a comment a reader will trust and a grep refutes — lens 4's exact class, though filed by L3); F4 (same mechanism, smaller) |
| L3-F6 | 94 fixed-size scratch buffers across 19 sizes; `emit_vm.c`'s own comments record being bitten twice already; NOT proposing 94 `limits.def` rows (would contradict D90's own boundary) — proposes a targeted audit: which buffers' bound derives from a `limits.def` row and which don't | `src/gen/emit_vm.c` (46 of 94) | CORRECTNESS-RISK (latent; no live truncation confirmed) | CROSS-CUTTING | up to 94 declaration sites; 0 emitted bytes if sizes preserved | **OVERLAP CLUSTER — see §2.3.** L2-L2-1 (49, two emitters only), L10-L10-1 (48, re-measured) — L10 §2.4 explicitly says the `sb_fragf` fix DISSOLVES F6's D90 question rather than answering it (needs no size constant at all) |
| L3-F7 | Emitted matcher's own identifier names are free-floating string literals at ~50 sites (`"scan_position"` ×19, etc.); filed WITH its own counter-argument (a rename is already a D76/D94-ritualized abi event, so the 50-site count is not the real cost) | `emit_dfa.c`, `emit_vm.c` | POLISH | MECHANICAL | 2 files, 0 emitted bytes, 0 check re-aims (checks match emitted text, not compiler source) | L10 kit (fragment/stamp layers touch the same identifiers); ride lens-10's emission-kit wave if it lands, "on its own it does not earn a wave" |

**PROBED-AND-HELD (H1-H9)** — see §5.

### Lens 4 — clarity + archaeology

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| L4-C1 | Header coverage INVERTS with function length: 12.5% of ≥200-line functions have a ≥3-line header vs. 67.6% at 25-49 lines; 43 functions at ≥50 code lines have ZERO preceding comment | `pcrec_emit_vm`, `pcrec_rxt_source_parse`, `compile_driver`, `main`, `vm_render_listing`, `vm_emit`, `emit_attempt`, `vm_revdet_rep`, `emit_predicate_axes`, `pcrec_rxt_source_tsv` (top 10) | MAINTAINABILITY | LOCAL (per function) | 43 functions touched if all, 0 checks staled | **Every one of the 10 worst-header functions also appears in L11's 100+-line scoreboard** (L11-F1, F2, F5, F4, F8, F7, [emit_attempt PASSES], [vm_revdet_rep PASSES], F6, F9) — the two lenses' worklists overlap almost entirely on WHICH functions to touch, for different reasons (headers vs. structure) |
| L4-C2 | `emit_attempt`'s section banner sits above the WRONG function (`emit_target`, a 4-line helper) | `emit_dfa.c:6365-6373` | POLISH | MECHANICAL | 1 file, 0 checks | Special case of C1; rides it |
| L4-C3 | [M6-READ]'s emitted-identifier rename reached the emitted side but not the compiler-side locals producing them (`acc2`, `seed`, `gseed`, etc., 26 sites) | `emit_dfa.c:6417-6435,6555-6561` | MAINTAINABILITY | MECHANICAL | 1 file, 26 sites, 1 sabotage row re-aimed (S82 — quotes `gseed` literally) | — |
| L4-C4 | Opaque single/double-letter locals in long scopes (`a`,`b` ceiling holders; `mk`,`nn`; `fk`; `nc`,`nv`) | `emit_vm.c:9220-9222,8626,8794`, `compile.c:1611`, `rxt_source.c:2126-2127` | POLISH | MECHANICAL | 3 files, 0 checks | shares `emit_vm.c` region with L11-F1 (region 8539-9000) — not the same lines, same neighborhood |
| L4-A1 | The `abi` change-log lives in 3 independently-written, disagreeing, incomplete homes (431-line code comment missing 8 events; an 11,861-char check failure message missing 2; `src/gen/CLAUDE.md`); 2 transitions (20→21, 21→22) recorded NOWHERE | `emit_dfa.c:1534-1964`; `tests/codegen/run_codegen_tests.sh:2795` | CORRECTNESS-RISK (documentation-of-contract) | LOCAL | 2 files, 1 check message | D76/D94 abi-ritual theme (general, cited across L1-X8, L2, L10); proposes moving history to `docs/spec/match_api.md` §6.3 (a home that already exists) |
| L4-A2 | A superseded [M6.4.2] claim left standing in present tense, corrected 15 lines below rather than in place — the ONE exception to an otherwise-honest 47/48 correction-in-place discipline | `select_engine.c:496-516` | MAINTAINABILITY | MECHANICAL | 1 file, 0 checks | shares file with L11's `pcrec_select_engine` (PASSES all 5 questions, §5 item 2) |
| L4-A3 | `RECALIBRATED` provenance prose (48 lines) sits above 4 constants the file no longer declares (they moved to `limits.def` at [LIM-1]/D90) | `emit_vm.c:69-116` | POLISH | MECHANICAL | 1 file, 0 checks | proposes moving prose to `limits.def`'s own `anchor` field per row — a mechanism L3's F1/F2 discussion also touches (allowlist-adjacent) |

### Lens 5 — unit-testing recommendations

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| L5-R0 | The repo HAS a unit tier (10 files, 6 dirs) with no name, no shared build, no membership rule, and 4 different flag policies; 2 of the 10 scripts are absent from `san_scripts.txt` | 10 files across `tests/codegen/`, `tests/parse/`, `tests/mrl/`, `tests/backrefs/`, `tests/utf8/`, `tests/registry/` | MAINTAINABILITY (+1 CORRECTNESS-RISK consequence) | MECHANICAL | 6 scripts, 1 manifest, 1 new `tests/lib/` helper; 0 sabotage anchors; no abi event | — |
| L5-R0.2 | The tree's best unit check (`cpset_model_check.c`) has NEVER been built under a sanitizer | `run_cpset_structure.sh:553`, `run_mrl_tests.sh:522` | CORRECTNESS-RISK | MECHANICAL (2 lines) | 2 lines in `san_scripts.txt` | **FIX-NOW — see §4.** Ranked #1 by L5's own §9 |
| L5-R1 | Allocation-failure injection via `-include` header + `BUILD_DIR` param (no `src/` edit); the only instrument that finds an F1 (=L8-F1) directly | proposed `tests/core/alloc_inject.h`, `ALLOC_DIR` Makefile target | CORRECTNESS-RISK | LOCAL | 1 new build tree, 1 new check, 0 bytes under `src/`, 0 sabotage anchors staled, no abi event | **EXPLICIT DISAGREEMENT with L8-F6(d) — see §3.** L8 files the injector as DESIGN-EVENT deferred under D77; L5 reclassifies it LOCAL on the `-include`+`BUILD_DIR` spelling |
| L5-R2 | Unit check for the saturating-arithmetic agreement (X3): pairwise equality + monotone/capped/absorbing laws over a boundary input set; decides X3's own open precondition (`cg_sat_add`'s extra guard) by evaluation | proposed `tests/core/sat_arith_check.c` | CORRECTNESS-RISK | MECHANICAL | 1 new check file, 0 src bytes, 0 anchors staled | L1-X3 (this check is the precondition that makes X3's unification safe; must be written BEFORE the refactor, against today's 3 implementations) |
| L5-R3 | Arena vector primitive's 4 properties specified BEFORE wave 1 builds it (content preservation, zeroed-new-element, capacity-monotone, alignment); census finds **13** sites, not 10 or 7 | `cont_push` (dfa.c), `patch_push` (nfa.c), `vm_push_at` (emit_vm.c) — 3 NOT in either L1 or L2's lists, plus the 10 L1 already named | MAINTAINABILITY (CORRECTNESS-RISK if primitive ships unchecked) | MECHANICAL | 1 new check; primitive's own wave carries S201's re-aim | **OVERLAP CLUSTER — see §2.1.** L1-X5 (10), L2-L2-8 (7), L11 §6 item 1 (28) |
| L5-R4.1 | `txt_f`/`sb_fragf`'s no-truncation property, checked over a boundary ladder crossing every hand-sized buffer's size; makes L2's step-3 acceptance number MECHANICALLY true rather than argued | proposed `tests/core/txt_check.c` | CORRECTNESS-RISK (for `txt_f`; K38 is the recorded miscompile of exactly its absence) | LOCAL | 1 new check; the kit's own migration carries the 24 anchor re-aims, not this check | L2-L2-1/L2-2, L10-L10-1 (the population this check protects — see §2.3's revised count) |
| L5-R4.2 | `txt_field`/`txt_row`'s structural (no unescaped control byte) AND injectivity (`decode(encode(s))==s`, via a DELIBERATELY DIFFERENT unescaper) properties — the count-based field-check in the tree today cannot see either | proposed `tests/core/txt_check.c` | MAINTAINABILITY→CORRECTNESS-RISK for injectivity | LOCAL | 1 new check | L2-L2-4, L10 items (4)/(5); complements (does not replace) L2's own "does any dump string contain a tab today" measurement, which NEITHER lens took |
| L5-R4.3 | `txt_join`'s over-long policy property: complete list or a documented prefix, NEVER a reordered subset — the property that would have caught `enabled.c`'s live bug | proposed check | MAINTAINABILITY | LOCAL | 1 new check | **SAME UNDERLYING BUG as L10-L10-2** (`render_modules` out-of-order partial list) |
| L5-R5 | AST-traversal net: bounded C-stack depth on a long spine + the back-edge (`u.call.body`) is never followed — properties invisible to answer-level coverage (a crash has no attribution; non-termination looks like any slow compile) | proposed check, written against L1-X2's merged `pcrec_ast_visit` FIRST, inherited by X1 later | CORRECTNESS-RISK (the discipline it checks is a segfault + non-terminating compile) | LOCAL | 1 new check; X1's own extraction carries the sabotage re-aims, not this check | L1-X1, L1-X2 |
| L5-R6 | DFA table emitter's wrapping boundaries (N=0,1,15/16/17, N≡0 mod 16) — CONDITIONAL on a population census not taken here; if all 5 boundary classes occur in the corpus this is PROBED-AND-HELD instead | proposed check over a stub cell function | POLISH | MECHANICAL | 1 new check; conditional | L1-X7, L2-L2-9 |

### Lens 6 — dependency hierarchy / rxt cut

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| L6-R1 | **The rxt cut FAILS today** — verified by 4-arm link experiment: a matcher-only consumer links all 3 rxt objects behind ONE symbol reference (`pcrec_rxt_compose`); `-dead_strip` alone recovers 43,968 of 44,448 bytes with NO source change, so the source cut's marginal win is ~480 bytes, not 365 KB | `core/compile.c:715-724,1157`; chain through `parse/rxt_compose.c`→`rxt_source.c`→`rxt_schema.c` | MAINTAINABILITY | LOCAL | 2 files edited, 1 file added, 0 checks staled (0 sabotage rows anchor on `rxt_compose`, verified by grep), 0 emitted bytes moved, no abi event | L8-F4 (`rxt_source.c`'s arena-abort-vs-diagnose split becomes exposed the moment this cut ships); L9 (cites arm 1 directly for its own link-level census, §1.3/§2.2) |
| L6-L1 | `src/gen/enc/` is misfiled: all 6 include back-edges are this ONE directory, and every one reads only the seam's DATA half (never the TEXT/emission half) | `enc.h`, 6 back-edge sites across core/ir/opt/parse | MAINTAINABILITY | LOCAL | ~12 source files, 34 doc/check citations, 6 sabotage `SAB_FILE` rows | proposes moving `src/gen/enc/`→`src/enc/`, inserting an `enc` tier between `core` and `parse` |
| L6-L2 | **The include graph understates cross-layer coupling by 6.5x** — 6 include back-edges vs. **39 call-level back-edge references**, 31 of which are invisible to ANY include-based instrument because `core/internal.h` declares them all | `tools/review/out/include_backedges.tsv` vs. an `nm -g`/`nm -u` join | MAINTAINABILITY (diagnosis; no move proposed) | — | — | methodological finding — "a control sharing a source with what it controls," at the INSTRUMENT level; feeds L6-L3 and L6-L5 |
| L6-L3 | `core/` is TWO layers wearing one name: the shared bottom tier (correctly placed) and `compile.c`, the 1,892-line pipeline DRIVER, which by definition sits ABOVE `gen/`; 20 of L2's 39 back-edges are this one conflation | `src/core/compile.c` | MAINTAINABILITY | DESIGN-EVENT | naming/layer-model only, or a file move (NOT proposed — D77: fix the model, not the file) | — |
| L6-L4 | The 4 `*_dump.c` CLI surfaces (2,773 lines) live in `src/parse/` and reach into `gen/`/`opt/`; they are ALREADY link-clean, which is the contrast that makes R1 worth fixing | `syntax_dump.c`, `axes_dump.c`, `schema_dump.c`, `limits_dump.c` | POLISH | MECHANICAL | 4 files, Makefile wildcard already covers | L9 (independently confirms the dump tier is the only link-clean archive members, from the symbol-export side) |
| L6-L5 | `src/core/internal.h` IS a god-header: 5,522 lines, 225 function declarations of which only 32 (14.2%) are defined in `src/core/`; included by 52 of ~55 `.c` files; #2 churn hotspot (171 touches) | `src/core/internal.h` | MAINTAINABILITY | CROSS-CUTTING | 52 TUs recompile per touch; 1 sabotage anchor | L9-P5 (same root cause from the public-surface side: 47 contract vs. 113 internal names, no lexical divider); L2-L2 (the 31 hidden back-edges this header causes) |

**PROBED-AND-HELD (8 items)** — see §5.

### Lens 8 — error-path and cleanup consistency

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| L8-F1 | **Live hole, K7's own defect verbatim**: `Job.scr_test`/`scr_desc` were never wired to `Ctx`, so an allocation failure in either calls `abort()` and kills the caller's process — reachable on an ordinary VM cursor-rung pattern | `src/core/compile.c:758-762` (attachment comment says "four" Job buffers; there are six) | **CORRECTNESS-RISK** | MECHANICAL | 1 file, 1 line; 0 checks staled | **FIX-NOW — see §4.** Ranked #1 by L8's own §"Ranked for the synthesis" |
| L8-F2 | `cli_parse`'s failure returns leak `libdirs` at BOTH call sites, falsifying the file's own stated invariant ("every other exit has nothing to free") | `cli/main.c:1228`, `apply_target:890-935` | MAINTAINABILITY | MECHANICAL | 1 file, 2 sites | L11-F3/F4 (both propose restructuring `cli_parse`/`main` — this fix should ride whichever wave touches the file, per L8's own ranking) |
| L8-F3 | `emit_state_legend` silently changes the emitted artifact on OOM (exits 0 either way; `abi`-adjacent readers can move without saying so) | `src/gen/emit_dfa.c:3602-3618,3647-3648` | MAINTAINABILITY | LOCAL | 1 file; interacts with D76/D94 | **RULING-WORTHY — see §3** ("wants a one-line ruling — refuse vs. announce — before the edit") |
| L8-F4 | `rxt_source.c` runs TWO disciplines for one event: `calloc` OOM aborts (bare `Arena*`, no `Ctx`), `realloc` OOM diagnoses — the author clearly intended diagnosis and the arena half silently does the opposite | `src/parse/rxt_source.c:2101-2103` vs `:3477-3480` | MAINTAINABILITY | LOCAL | 1 file; couples to `[LIB]` (lens 6's rxt cut) | L6-R1 (severity is bounded ONLY while `pcrec_rxt_source_*` has no library caller — the cut exposes it); L1-X4 (the 3 correctly-`Ctx`-taking strndup siblings are the contrast) |
| L8-F5 | `write_file`/stdout path never observe a write error (`fputs` return + `ferror` unread); `pcrec -o - 'a+' > /full/disk` exits 0 having written nothing | `cli/main.c:292-299,1209,1726` | MAINTAINABILITY | MECHANICAL | 1 file, 3 sites | **SAME FINDING as L10-L10-8** — see §2.5 |
| L8-F6 | The discipline's ONLY check (`run_resource_tests.sh` §2) is SKIPPED on darwin, can pass VACUOUSLY (verdict arm accepts 3 different diagnostics, only 1 of which is an allocation failure), and has a stale hand-written file list (6 files named, 10 exist) | `tests/resource/run_resource_tests.sh:659,679-694,705-706` | MAINTAINABILITY (check design) | LOCAL | check tier | L5-R0.2/R1 (F6(a)/(b)/(c) are the staged precursors to L5's own injector; L5 explicitly orders R1 AFTER F6a/b/c) |
| L8-F7 | A target's `.c`/`.h` pair can be left half-written on short-circuit write failure (multi-target `--source` loop leaves targets `0..i-1` already written) | `cli/main.c:1210-1211,1728-1729` | POLISH | LOCAL | 1 file, 2 sites | — |

**PROBED-AND-HELD (H1-H13)** — see §5.

### Lens 9 — public-surface tightness

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| L9-P1 | `libpcrec.a` exports **12 symbols with NO namespace prefix** (`arena_alloc`, `sb_puts`, `ctx_fail`, …); reproduced live: a consumer's own `arena_alloc`/`sb_puts` FAILS TO LINK | `arena.o`, `sb.o`, `nfa.o` symbols | CORRECTNESS-RISK (consumer-side, loud) | CROSS-CUTTING | 1,652 source sites / 12 names; 26 test files incl. 8 sabotage rows (all on `ctx_fail`) | **RULING-WORTHY — see §3.** Two priced fixes: (a) rename the 12 (1,652 sites) vs (b) archive-symbol localization (fixes all 256 non-public exports at once, per-platform build machinery — a D2 tension); author explicitly frames as "a Frank question, not a manager default" |
| L9-P2 | `lib/pcrec.h:26` denies a SHIPPED encoding ("`PCREC_ENC_UTF8`... not yet implemented"); measured: `-e utf8` compiles, exit 0, since [M5.0] closed | `lib/pcrec.h:24-27` | CORRECTNESS-RISK (documentation) | MECHANICAL | 1 file, 0 checks | **FIX-NOW — see §4.** "R29's exact class, in the same file R29 fixed" — recurring defect shape |
| L9-P3 | `docs/spec/match_api.md` §8.2 quotes `pcrec_options` with 9 members; shipped struct has 19; a SECOND spec doc (`tuning.md` §4) cites §8.2 as authoritative "in full" | `match_api.md:3319-3335` vs `lib/pcrec.h:710-944` | MAINTAINABILITY | MECHANICAL | 2 spec files, 0 checks | — |
| L9-P4 | Library has NO limits surface: 11 raise-only limits constants cited in header prose are undeclared; a library consumer's only route to a default is to trigger the refusal and parse English out of `err.msg` | `lib/pcrec.h` (11 names), `src/core/limits.def` | MAINTAINABILITY | LOCAL | 1 header + 1 spec hunk | L3 (D90/`limits.def` as ruled central home — this finding proposes the public header DERIVE from it, not move anything out); L6-R1 (the library-use-case framing) |
| L9-P5 | `PCREC_*` is ONE flat namespace holding 47 contract names and 113 internal-only names with no lexical divider; the public header's own contract prose CITES 11 of the internal names as if the reader had them | `lib/pcrec.h`, `src/core/internal.h` | MAINTAINABILITY | DESIGN-EVENT | tree-wide | L6-L5 (same root cause — `internal.h`'s god-header shape); named trigger (D77): "a second collision or a v1 declaration, whichever arrives first" |
| L9-P6 | Rx-info-mask/axis catalogue has 3 homes; `match_api.md` §8.2 delegates the catalogue TO THE SOURCE COMMENT — a D80 inversion (spec should be authoritative, not point at code) | `match_api.md` §8.2 vs `tuning.md` §2 vs `emit_dfa.c`'s `strategy_denials` array | MAINTAINABILITY | LOCAL | 1 spec hunk | L4 (documentation-accuracy/D80 theme) |
| L9-P7 | 7 sites in the public header spell the DEFAULT-prefix emitted constant (`RX_NCAPS` ×5, `RX_PUSH`, `RX_SET`) inside generic `<PREFIX>_` contract prose | `lib/pcrec.h:39,977,1003,1009,1011,797,798` | POLISH | MECHANICAL | 1 file, 0 checks | **FIX-NOW — see §4.** Rides with P2/P8 |
| L9-P8 | `lib/pcrec.h:883-885` claims the warn default is "an order of magnitude under" the max; it is 4×, and WAS 4× at the commit that wrote the sentence (checked via `git show` — never true, not drift) | `lib/pcrec.h:883-885` | POLISH | MECHANICAL | 1 file, 0 checks | **FIX-NOW — see §4.** |

**PROBED-AND-HELD (9 items)** — see §5.

### Lens 10 — emission-kit unification (wave 1 charter)

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| L10-L10-0 | The tree's ONLY long-prefix control (`run_cli_tests.sh` case 3) compiles the pattern `a`, reaching ~none of the 48 literal-sized emitter buffers; the check that exists to stop K38 recurring cannot see the population it is about | `tests/cli/run_cli_tests.sh:195-216` | CORRECTNESS-RISK (instrument) | LOCAL | 1 check + 1 new sweep; 0 src files; 0 anchors; no abi | proposed as STAGE 0, a precondition for stage 3, not a cleanup |
| L10-L10-1 | Fragment layer, RE-MEASURED: 43 `snprintf`-into-`char[N]` sites; tightest margin in the WHOLE TREE is 9 bytes (`gst_param[96]`); **ZERO of the 48 sites provably truncate at a legal 60-byte prefix today** — severity REVISED from L2's CORRECTNESS-RISK to "MAINTAINABILITY + latent CORRECTNESS-RISK" | `emit_vm.c`, `emit_dfa.c` | MAINTAINABILITY (+ latent CORRECTNESS-RISK) [compound, REVISED from L2's CORRECTNESS-RISK] | CROSS-CUTTING | 2 files; **4 anchors directly, 123 in radius** (re-measured — L2 said 24 directly); 7 source-reading checks (L2 named 5, missed 2); no abi event | **OVERLAP CLUSTER — see §2.3.** L2-L2-1 (49), L3-F6 (94) |
| L10-L10-2 | `sb_join`: 5 implementations, 3 different undocumented over-long policies; `render_modules` produces an **out-of-order partial list**, not a truncated prefix (LIVE BUG, not merely a cleanup) | `src/parse/enabled.c:180` | **CORRECTNESS-RISK** (live, small) | LOCAL | 4 files; 0 anchors; no abi | **SAME BUG as L5-R4.3**'s motivating example; underlying population is L2's M8 (5 implementations) |
| L10-L10-3 | Field/row layer per L2's items (4)/(5), promoted from `rxt_source.c`'s `put_escaped` | 5 dump files | MAINTAINABILITY (+ latent CORRECTNESS-RISK) | LOCAL | 5 files; 1-2 anchors; `tests/rxtsource` field-count pins; no abi | L2-L2-4, L5-R4.2 |
| L10-L10-4 | CLI channel per L2's item (5), unchanged | `cli/main.c`, 76 sites | MAINTAINABILITY | MECHANICAL | 1 file; 0 anchors; `tests/cli` wording pins; no abi | L2-L2-5 |
| L10-L10-5 | `sb_name`/`sb_upper`: the UPPERCASED prefix is a second derived name from one source, independently derived at ≥3 sites, and is the LARGEST single non-prefix binding in the whole `%s_` census (139 of 584) | `emit_dfa.c:659` (`prefix_upper`), `emit_vm.c:376` (`Vm.up`, ~110 read sites) | MAINTAINABILITY | LOCAL (primitive) / **DESIGN-EVENT** (`Vm.up` retirement) | 2 files for the primitive; `Vm.up` retirement is OUT of wave 1 | NEW finding, derived from L10's own decomposition of L2's 652 (F2 in L10's own numbering) — no other lens names this |
| L10-L10-6 | `emit_vm.c:8165`'s recorded LIVE truncation (`char slot[48]`, a listing column) is bounded by SLOT-NAME length, not prefix length — invisible to every prefix-based instrument; retiring the buffer WILL move listing bytes | `emit_vm.c:8165-8167` | **CORRECTNESS-RISK** | LOCAL, escalate | 1 site; `--emit-listing` bytes; column-width-as-contract | **RULING-WORTHY — see §3** |
| L10-L10-7 | The template layer. **RECOMMEND NO CHANGE — CLOSED, not deferred.** Population is 1 by L2's own metric (and that 1 performs zero substitutions); 30 calls / 1.9% of emitted literal bytes by L10's corrected metric; structurally cannot reach the 64%-of-bytes MIXED bucket where the readability win actually is | two emitters | — (anti-finding) | NONE | none | **SUPERSEDES L2-L2-3** — see §2.4 |
| L10-L10-8 | `write_file` (`cli/main.c:292-299`) checks `fclose` but not `ferror()` on the `fputs` that wrote the artifact | `cli/main.c:292-299` | POLISH (correctness, remote) | MECHANICAL | 1 site; do not ride stage 2 | **SAME FINDING as L8-F5** — see §2.5 |

### Lens 11 — function composition & altitude

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| L11-F8 | `vm_render_listing`: 3 identical 12-line section loops + 6 identical slot loops (Q4 fails twice) | `emit_vm.c:8067-8131`, `8019-8054` | MAINTAINABILITY | MECHANICAL | 1 file, 0 sabotage rows, `run_vm_tests.sh` names the function | **corrects L1's join table** (X8 does NOT apply here — 0 stamp sites); recommended as the cheapest first move to prove the review's method |
| L11-F12 | `vm_cursor_rep`: the emitted bounded span-scan loop is written TWICE (identical 8-line C fragment, differing in one bound token), 140 lines apart, with NO agreement check | `emit_vm.c:4151-4158,4292-4303` | MAINTAINABILITY (emitted-text divergence risk) | MECHANICAL | 1 file, **5 sabotage rows** attribute inside; identity gate must prove no byte moves | L1 ADDENDUM-2 item 1 (this IS inside the unreviewed `emit_vm.c` surface L1 flagged); cites k49fix's twice-spelled-boundary-needs-an-agreement-check precedent; **CONFIRMED by EP2-E2, which also finds the proposed `(…, test, bound)` signature cannot express the greedy arm's extra in-block declaration (`lim_`) — see §2.8 item 5 for the corrected `clamp`-parameter signature** |
| L11-F10 | `pcrec_brport_g`: three `\g`-delimiter branches (brace/angle/bare) are ONE parse triplicated; **lowest comment ratio in the 31-function population (1.20)** | `mod_backrefs.c:318-467` | MAINTAINABILITY | LOCAL | 1 file, 0 sabotage rows inside this function | L1-X6 (applies to the FILE's cross-module sharing, NOT to this intra-function repetition — X6 doesn't reach it) |
| L11-F13 | `p_class`: the class-endpoint read (low/high) is spelled twice with the same 3-way program; K12's own ruling records the order as load-bearing | `parse.c:1069-1073` vs `:1165-1170` | MAINTAINABILITY, ruled-record argument in favor | LOCAL | 1 file, 2 sabotage rows attribute inside (incl. S-U1, outside the moved region) | K12 (`docs/dev/known_issues.md`) cited as an argument FOR the extraction |
| L11-F6 | `emit_predicate_axes`: 178 lines with NOT ONE `if` or loop — a data table written as code | `axes_dump.c:375-668` | MAINTAINABILITY | **DESIGN-EVENT** (it IS X9, not a local edit) | per L1-X9's blast radius | **X9 IS THE WHOLE REMEDY — no lens-11 split proposed at all** (ADDENDUM-1's pure case) |
| L11-F9 | `pcrec_rxt_source_tsv`: the header reads `rxt_columns[]`; the ROW WRITER does NOT — the comment claiming a structural guarantee ("header and row writer cannot disagree") is FALSE, the agreement rests entirely on an external test | `rxt_source.c:3787-3906` | MAINTAINABILITY trending CORRECTNESS-RISK | LOCAL | 1 file; `--list-source` is a published D80 contract | L1-X12 applies to the file's 11 ladders, not this function; notes "THE 15 COLUMNS" stale comment header is `w23implfix_report.md`'s SECOND recorded instance (a 20-entry array) |
| L11-F11 | `pcrec_modport_optrun`: 14 parallel booleans set by a switch, applied by 14 consecutive one-line `if`s; unset-wins ordering is a property of APPLY ORDER a naive table would erase | `mod_modifiers.c:242-488` | MAINTAINABILITY | LOCAL | 1 file, **4 sabotage rows attribute inside** (S22,S24,S25,S26) — R17's own "correct-today-unguarded port corners" | cites R17 (`2026-08-12-r17-mod05.md`) as the reason all 4 rows must be re-run in the FAILING direction, not merely re-anchored |
| L11-F7 | Per-kind dispatchers with one fat arm (`vm_emit`, `vm_count_slots`, `compile_ast`): the FILE already ratified the delegate-per-kind pattern once (`vm_cost`→`vm_cost_rep`) and didn't apply it 3 functions later | `emit_vm.c:7129-7643` (211), `:2566-2914` (119), `ir/nfa.c:551-945` (121, marked *mild*) | MAINTAINABILITY | LOCAL (per function) | `vm_emit` 9 sabotage rows, `vm_count_slots` 1, `compile_ast` 1 | **L1-X1 explicitly does NOT cover this** (X1 is whole-tree verdict walks; these are per-kind producers) |
| L11-F14 | Three loop-bodies-that-are-functions: `vm_look_behind`, `pcrec_syntax_explain` (genuine small wins), `emit_attempt`'s state loop (PROBED and HELD — listed only so it isn't re-found) | `emit_vm.c:6315-6444`, `syntax_dump.c:1565-1717`, `emit_dfa.c:6729-6870` | POLISH | MECHANICAL | `vm_look_behind` 3 sabotage rows, `pcrec_syntax_explain` 0, `emit_attempt` 2 | cross-refs L11's own §5.1 item 1 (the `emit_attempt` half is PROBED-AND-HELD) |
| L11-F15 | `pcrec_scanedge_dfa`: nine parallel arrays hand-allocated/hand-freed — ~25 of 108 code lines are storage bookkeeping at a different altitude than the chain-finding algorithm | `scanedge.c:478-521,688-689` | POLISH (MAINTAINABILITY on the failure path) | LOCAL | 1 file, 1 sabotage row | notes L8-H6 already verified this function's cleanup is CORRECT on all 4 exits — this finding is about extraction, not correctness; L1-X5 does not cover it (fixed-size, not growable) |
| L11-F3 | `cli_parse`: 60-arm `else if` chain, `!no_more_opts &&` re-typed 59 times — a 60th arm has NO structural reminder, so `--` silently breaks for that flag; ALSO: 28 spec citations to `cli/main.c:<line>`, ≥5 already stale today | `cli/main.c:379-809` | MAINTAINABILITY, named correctness hazard | CROSS-CUTTING (it is X9+X10+a table) | `cli/main.c`, 0 sabotage rows, `tests/cli` pins wording, 28 spec line-refs | **SAME FINDING as L2-L2-6**, adds the correctness hazard + lens-1 join (X9, X10) + spec-citation staleness |
| L11-F4 | `main`: 7 modes; the mutual-exclusion relation is written 6 TIMES with 4 DIFFERENT memberships, correct today only because of BLOCK ORDER | `cli/main.c:1223-1736` | MAINTAINABILITY trending CORRECTNESS-RISK | LOCAL (after F3) | `cli/main.c`, 0 sabotage rows, `tests/cli` pins 35 refusal diagnostics, D80 spec hunk required | sequenced to ride AFTER F3 |
| L11-F5 | `compile_driver`: 402-line pipeline with a 266-line RETRY POLICY (5 rungs) inlined in the middle; the pipeline region itself is clean and uniform — the failure is that the setjmp handler and the pipeline share one function | `core/compile.c:556-1789` (setjmp block: `822-1088`) | MAINTAINABILITY | LOCAL, stated technical constraint (`volatile`/setjmp) | `core/compile.c`, **7 sabotage rows attribute inside** | **A1 cites and does NOT contradict** `utf8k53_report.md`'s ruled rejection of a rung-table at N=1; explicitly notes the ruled event that WOULD reopen the table question (`SDR_NO_PREMUL`) has now arrived, ruled by Frank 2026-09-17, making the ladder N=2 |
| L11-F2 | `pcrec_rxt_source_parse`: 25 productions inlined in one 548-line loop, BESIDE the schema table that was supposed to end exactly this (W23.1 already declared STRUCTURE; per-production SEMANTICS stayed inline) | `rxt_source.c:2095-3069` | MAINTAINABILITY trending CORRECTNESS-RISK | CROSS-CUTTING | `rxt_source.c` (4,037 lines), 1 sabotage row attributes inside; D80 spec event if any refusal moves | L1's own X5/X12 "not enough" admission for this file; L1 ADDENDUM-2 item 2 (names file as unreviewed remainder); L4/L5 both separately name this file for a second pass |
| L11-F1 | `pcrec_emit_vm`: an ANALYSIS pass (2 fixpoints, ~30% of the body, emits NO text) + a CONFIGURATION pass + an EMITTER share one 778-line body; the most anchor-dense function in the tree | `emit_vm.c:8539-11575` | MAINTAINABILITY (code is correct; cost is read/edit time) | CROSS-CUTTING, STAGEABLE | 1 file, **26 sabotage rows attribute inside — 10% of the tree's whole failing-direction net** [EP2 MEASURES 29 rows / 32 records, 11.1% — see §2.8 item 1] | **CONFIRMS L1-X8 exactly** (all 52 stamp sites are inside this function); **IS, in large part, the "second pass over `emit_vm.c`" every other lens named as owed** — see §6 register; **EP2 IS THAT PASS, FORMALLY, AND CORRECTS THIS FINDING IN FIVE PLACES — see §2.8** (anchor count; `vm_build_region_saves`'s signature cannot compile; a second clean extraction `vm_plan_regions` is missing from this table; the proposed 4-commit order is wrong in 3 places; EP2-E0 additionally reaches an X1-cluster duplication L11 did not find) |

**PASSES (13 functions, §5) and PROBED-AND-HELD (7 items, §5.1)** — see §5.

### Lens emitpass2 — `src/gen/emit_vm.c`, the second pass (chartered by L1 §4 item 1, sequenced by L10 §4.3)

Every number below was RE-DERIVED by EP2 at `7d444f9e` directly from the
file and from `tests/mech/sabotages/`, never copied from a prior report;
where a number disagrees with one already in this table, the row states
the disagreement and the instrument difference (per EP2's own framing,
echoing L10 §2.4's warning that instruments disagree — which EP2 finds
applies to anchor counts too, not only buffer counts).

| cite | claim | file:line | severity | effort | blast radius | cross-ref |
|---|---|---|---|---|---|---|
| EP2-E0 | The 4 walks at `emit_vm.c:6613-6748` are ONE 28-line spine walker duplicated into TWO genuinely different edge-policy pairs (stop-leaf-then-descend vs. act-leaf-then-plain-descend at `A_CALL`); merge the traversal, keep both edge policies as two callbacks | `emit_vm.c:6613-6748` (`vm_grp_set`, `vm_w_caps`, `vm_publish_nonnull`, `vm_publish_saves`) | MAINTAINABILITY | MECHANICAL | 1 file, 1 anchor re-aim (S149), 0 abi | **L1-X1** (the whole-tree walk extract reaches this cluster materially — EP2's own §2.1 finding); explicit anti-perversion note: "the verdict merges the TRAVERSAL and keeps both VERDICTS," exactly L1-X1's `atomic.c` framing |
| EP2-E1 | The file's OWN declared helper (`vm_slot_expr`) is re-derived by hand at 4 sites (`vm_call`, `vm_splice` ×3), each with its own pair of buffers; an arena-returning sibling (`vm_slot_ref`) retires **8 of the 40 category-(a) buffers in one edit**, 20% of stage 3's population, with ZERO anchors inside | `emit_vm.c:6818-6825,6942-6949,7009-7020,7023-7031` | MAINTAINABILITY (the file's own comment calls the pattern a defect class) | MECHANICAL | 1 file, 0 anchors inside (2 abut: S147, S173), 0 abi (byte-identical by construction) | **L2-L2-1/L2-2, L10-L10-1** (this is the single highest-value, lowest-cost slice of the whole fragment-layer population — not named by any prior report) |
| EP2-E2 | **CONFIRMS L11-F12** (the emitted bounded span-scan written twice, `vm_cursor_rep`/`emit_vm.c:4151-4158,4295-4303`) by direct source verification — **but L11's proposed signature `(v, a, stride, test, bound)` cannot compile**: the greedy arm emits an extra declaration (`lim_`) INSIDE the block it opens, which the shared bound expression then names, so the helper needs a `clamp` parameter that owns opening the block | `emit_vm.c:4151-4158,4295-4304` | MAINTAINABILITY | MECHANICAL | 1 file, 0 anchors inside, 0 abi | **CORRECTS L11-F12** — see §2.8 |
| EP2-E3 | `{m,n}` bound text rendered 4 times, 3 different spellings (2× `bounds[32]`, 1× `fbounds[32]`, 1× inline in two `vm_rolef` calls with no buffer); one arena-returning helper retires 3 more category-(a) buffers; reaches BOTH the `.c` artifact (via a `// %s` comment) and the `--emit-ir` listing | `emit_vm.c:4105-4107,4862-4864,5761-5764,5506,5510` | POLISH | MECHANICAL | 1 file, 0 anchors, 0 abi; both byte-streams must be compared | new finding, no prior report reached this site |
| EP2-P1 | The call-target nullability fixpoint (`:8792-8810`, emits nothing, mutates the AST via `vm_publish_nonnull`) extracts cleanly as `vm_resolve_nonnull(Vm*, Ast*)`; the `nt+1`-round settle assertion (`ctx_fail` at `:8806`) must travel | `emit_vm.c:8792-8810` | MAINTAINABILITY | LOCAL | 1 file, 0 anchors inside, not an abi event (emits no text) | refines **L11-F1**'s region-8539-9000 row — see §2.8 |
| EP2-P2 | A SECOND clean, zero-anchor fixpoint (region-linkage flags + transitive group set + `spl_nw`) sits inside L11's own 8539-9000 span and is **not named by L11's table at all** — `vm_plan_regions(Vm*)` | `emit_vm.c:8826-8865` | MAINTAINABILITY | LOCAL | 1 file, 0 anchors inside, not an abi event | new finding within L11's own region — see §2.8 |
| EP2-P3 | The `W` save-set build (`:9000-9150`) is the one candidate whose seam is NOT free: **L11's proposed `vm_build_region_saves(Vm*, Ast*, int nstate)` cannot compile** — it reads `snap_before[]`/`snap_after[]` (7 family ranges per region) produced by an INTERLEAVED counting pass L11's table treats as part of a different, contiguous region; the snapshots must become parameters. Carries the `spl_nw` agreement `ctx_fail` (`:9138-9143`), which must travel with its comment | `emit_vm.c:9000-9150` | MAINTAINABILITY | LOCAL | 1 file, **6 anchors inside** (S148,S150,S151,S152×2,S153) | **CORRECTS L11-F1's proposed signature** — see §2.8 |
| EP2-P4 | The region cost fixpoint (cyclic targets settled first, then readiness-ordered DAG evaluation) extracts cleanly as `vm_memo_region_costs(Vm*)`, zero anchors, depends only on P2 | `emit_vm.c:9150-9186` | MAINTAINABILITY | LOCAL | 1 file, 0 anchors inside, not an abi event | refines L11-F1's region-9000-9189 row |
| EP2 (anchor correction) | L11-F1's "26 sabotage rows attribute inside `pcrec_emit_vm`, 10% of the tree's net" is a measured UNDERCOUNT: the true figure is **29 distinct rows / 32 anchor records (11.1% of 261 rows)**, located by sourcing every `S*.sh` and exact-string-locating its `SAB_BEFORE` — L1's own 85-rows-in-the-whole-file figure reproduces exactly | `emit_vm.c` (whole function, `:8539-11575`) | — (correction) | — | — | **CORRECTS L11-F1** — see §2.8 |
| EP2 (sequencing correction) | L11's proposed 4-commit order (X8 first, then `vm_resolve_nonnull`, `vm_build_region_saves`, `vm_plan_capacities`) is corrected in three places: **X8 must NOT go first** (it is the only step with an abi question, and depends on L10's `sb_name`/`sb_upper`, which L10's stage 3 supplies — X8 rides stage 3, per L10 §4.3 item 4, not step 1); **P2 (`vm_plan_regions`) is missing from L11's order entirely**, a free zero-anchor extraction that must precede P3/P4; **P3 before P4 is backwards** — P4 is zero-anchor and depends only on P2, P3 is six-anchor and needs the snapshot parameters, so doing P4 first means a red in P3 bisects to P3 alone | — | — (correction) | — | — | **CORRECTS L11-F1's staging** — see §2.8 |
| EP2-§3.5 | The tree's sabotage-application mechanism (`tests/mech/lib/replace.py`) matches `SAB_BEFORE` as a WHOLE-FILE, LINE-AGNOSTIC substring — so a verbatim same-file RELOCATION costs zero re-aims, and only a TEXT CHANGE (chiefly re-indentation: 92 of 94 `emit_vm.c` anchors carry leading whitespace) breaks an anchor. Reframes the cost model for every wave touching this file: price by "does the moved text keep its column," not by lines moved | `tests/mech/lib/replace.py` | — (methodological finding) | — | — | governs the ordering of every `emit_vm.c` step in EP2's own §5 sequence table and should govern L10's stage 3 ordering too |
| EP2-§4 | The buffer population is **58 declaration statements / 66 declarators in THREE sizing categories**, not 40/48 — category (c) (5 sites, `DERIVED_CONSTANT + literal margin`, e.g. `PCREC_MAX_EMIT_NAME_LEN + 64`) is uncounted by every prior instrument and would **pass L10's stage-3 acceptance criterion untouched**, which the criterion was explicitly written to avoid (the K35 shape, one category over) | `emit_vm.c:4989,5079,5137,7800,11381` | CORRECTNESS-RISK (the criterion gap) | — | 1 file; recommends the criterion be restated over `char <ident>[` with ANY size expression, floor at 58/66 not 40/48 | **OVERLAP CLUSTER, EXTENDED — see §2.3** |
| EP2 §1 (`irsb`/L12 finding) | `vm_render_listing` (L12) writes a DIFFERENT output stream (`job->irsb`, the `--emit-ir` listing) that NONE of lens 10's four standing byte-identity gates or its full-corpus emit-diff (both `.c`-artifact-only) can see; the only comparator is `tests/codegen/run_ir_listing.sh`; 6 of stage 3's category-(a)/(c) buffers write only to this stream | `emit_vm.c:7645-8278` (L12), `:11557` (the one call site) | CORRECTNESS-RISK (instrument gap) | — | any stage touching L12's 6 buffers owes this arm explicitly | **new named-owed item for L10's stage 3 — see §6 follow-on register** |
| EP2 A1 (ruled-record confirmation) | The non-emitting fixpoints (P1-P4) may NOT move to `src/opt/`: `src/core/internal.h:5412-5418` rules `vm_nullable`'s recurrence file-`static` to the emitter (10 call sites across L3/L5/L8), and all four candidates write into `Vm`, a file-local, unexported `typedef struct` — moving either would export `Vm` or split the recurrence across the ruled boundary. The realistic home is file-static helpers in `emit_vm.c` itself (what L11-F1 already proposed) | `src/core/internal.h:5412-5418` | — (A1 ruled-record check; not a new finding) | — | — | **confirms and narrows L11-F1's proposed home** — recorded in the follow-on register (§6) per the team lead's instruction |

**PROBED-AND-HELD (8 items, EP2 §6)** — see §5.

---

## 2. OVERLAP CLUSTERS

Findings that are the same underlying item reported by multiple lenses.
Population disagreements are surfaced explicitly, with each source's
number and its instrument — **not resolved**.

### 2.1 The growable-array/arena-vector family — POPULATION DISAGREEMENT: 10 / 7 / 13 / 28

Four independent countings of "the same double-on-full, arena-copy,
zero-new-element growth idiom, invented repeatedly instead of a shared
`pcrec_arena_vec_push`":

| source | count | instrument |
|---|---|---|
| L1-X5 | **10** | clone-detector groups 3 and 10 (`clone_candidates.tsv`), hand-enumerated |
| L2-L2-8/rank3 | **7** | clone groups 10 (4 members `group_frac` 1.000) + 3 (`row_push` 0.485, `libdir_push`, `vm_ev`, `vm_isl_insert`) |
| L5-R3 | **13** | `function_census.tsv` re-scanned by the check-design lens; adds `cont_push` (`ir/dfa.c:444`), `patch_push` (`ir/nfa.c:103`), `vm_push_at` (`emit_vm.c:2964`) — explicitly "the last three are in neither lens's list" |
| L11 §6 item 1 | **28** | `grep -rn "cap \* 2 :"` over the whole tree — the largest number, because it counts INLINE copies buried inside longer functions (e.g. inside `pcrec_rxt_source_parse`'s `RXT_PUSH_FRAME` macro, `pcrec_rxt_compose`), which neither clone-detector-based count could see since they are not standalone functions |

All four agree `cli/main.c:libdir_push` is correctly EXCLUDED (it
`realloc`s rather than arena-allocates and is the CLI's own stated
invariant — L1-X5, L8-H10). L5-R3 explicitly warns against writing the
unit check "against today's thirteen copies" — write it once the
primitive exists. **No lens claims its own count is exhaustive**; L11
explicitly frames its 28 as "part of why the long functions are long,"
i.e. a different question (extraction opportunity) than L1/L2/L5's
(missing library primitive).

### 2.2 The optimization-axis / config table family (X9)

L1-X9 charters the extraction (`src/core/axes.def`, an X-macro table
replacing 3 hand-maintained sources + 2 awk scrapers). Three other
findings are downstream consumers of the same table:

- **L2-L2-7** — `--tune`'s CLI menu is a second, independently-hand-typed
  spelling of `tune.c`'s own alias table (D103 names `tune.c` the dial's
  one home); one of L1-X9's 8 menu instances.
- **L11-F6** — `emit_predicate_axes` (178 code lines, not one `if` or
  loop) is explicitly scored as ADDENDUM-1's *pure case*: X9 is the
  whole remedy, no function-specific split proposed at all.
- **L11-F3** — `cli_parse`'s 20 `-fno-*` arms are named as the ~60-line
  slice X9 removes from the function, alongside X10's 5 `strtol` arms;
  together lens 1's two extracts take out roughly a third of the
  function's body before lens 11's own findings apply to the remainder.

No population disagreement here — all four cite the same table's
existence and location; they differ only in which CONSUMER of the
missing table each lens was looking at.

### 2.3 The emitter scratch-buffer family — POPULATION DISAGREEMENT: 94 / 49 / 48 / 58 (66 declarators)

Four countings of "fixed-size `char NAME[N]` scratch buffers fed by
`snprintf`, unnamed-sized, in the emitters":

| source | count | scope | instrument |
|---|---|---|---|
| L3-F6 | **94** | whole `src/`+`cli/` tree | grep for `char NAME[<literal>]` declarations across 19 distinct sizes |
| L2-L2-1 | **49** (41 `emit_vm.c` + 8 `emit_dfa.c`), plus 34 already named by `PCREC_MAX_EMIT_NAME_LEN` | the two emitters only | grep census |
| L10-L10-1 | **48** (40 `emit_vm.c` + 8 `emit_dfa.c`) declaration statements at code positions; author's own script's caveat: a per-LINE grep gives 53 (6 in comments), and ~14 same-line continuation declarators are additional buffer OBJECTS the declaration count doesn't separate | the two emitters only | `lens10_evidence/buf_risk.py`, re-run independently |
| EP2-§4 | **58 declaration statements / 66 declarators** in `emit_vm.c` ALONE (not both emitters), across **three** sizing categories: (a) bare literal — 40 statements/45 declarators, reconciling L10's own 40 exactly, but at a DIFFERENT resolution (L10's 40 is statements; EP2 separately counts 45 declarators, since 5 lines declare 2-3 each); (b) bare `PCREC_MAX_EMIT_NAME_LEN` — 13 statements/16 declarators, reconciling L10's 16 exactly (also a statements-vs-declarators reading of L10's OWN two numbers); (c) **`DERIVED_CONSTANT + literal margin`** (e.g. `PCREC_MAX_EMIT_NAME_LEN + 64`) — **5 sites, matched by NO prior instrument** | `emit_vm.c` only | `emitvm_evidence/` scripts, re-derived independently at `7d444f9e` |

**L10 §2.4's own instruction, stated explicitly and preserved here
verbatim in spirit: "all three instruments agree on the shape and NONE
of them should be cited as an exact site list without being re-run."**
**EP2 confirms this applies even to its own two numbers** — L10's "40"
and "16" turn out to be counted at different resolutions internally
(statements vs. declarators), reconciled only once EP2 separated the
two axes explicitly.

The counts are not simply contradictory — L3's 94 is whole-tree, the
others are `emit_vm.c`-only or two-emitters subsets — but the
resolution differences (statements vs. declarators, and now a THIRD
sizing category no earlier instrument's grep pattern could match) are
themselves the finding: each re-run of "the same" measurement has moved
the number, which is the point every instrument in this cluster now
makes explicitly about not citing any single count as exact.

**Severity disagreement riding the same population**: L2 files this
CORRECTNESS-RISK on K38's precedent. L10, having measured the actual
truncation margins (tightest 9 bytes, worst case bounded, zero sites
provably truncate at a legal 60-byte prefix TODAY), REVISES the
severity to "MAINTAINABILITY + latent CORRECTNESS-RISK" and states
explicitly: *"L2's acceptance number cannot be used ... a criterion the
branch point satisfies measures nothing about the change."* L3-F6
independently reaches the same "latent, not live" disposition from the
whole-tree side. This is a genuine severity DOWNGRADE across the
review's own timeline (L2 → L10), not resolved here — flagged for the
manager.

**EP2 then finds a GAP in L10's own repaired acceptance criterion**,
riding the same population: L10's stage-3 completeness criterion
("zero literal-sized `char NAME[…]` scratch buffers remain … floor of
48 declarations") would be satisfied with EP2's category (c) — 5 sites
— left completely untouched, since a grep for a bare integer literal or
for `PCREC_MAX_EMIT_NAME_LEN` alone does not match
`PCREC_MAX_EMIT_NAME_LEN + 64`. EP2 files this CORRECTNESS-RISK (the
criterion gap, not the buffers themselves — none of the 5 is shown to
truncate) and recommends restating the criterion over `char <ident>[`
with ANY size expression, with the floor moved to 58 declaration
statements / 66 declarators in `emit_vm.c` alone (not 48 across both
emitters). **This is the K35 shape — a population nobody counted —
recurring inside the very criterion L10 wrote to retire an earlier
instance of it**, one category over. Not resolved here; the manager
should treat L10's stage-3 acceptance number as still open pending this
repair.

### 2.4 The template-layer question (`pcrec_enc_emit_text`) — SUPERSEDED, not a disagreement

L2-L2-3 named the measurement (count runs of ≥5 consecutive prefix-only
`sb_*` calls) and recommended AGAINST building the template layer
*pending that measurement*, explicitly declining to build the counter
itself ("D77's trigger, not a gap in this report").

L10 took the measurement L2 named (§1 of L10's report) and found the
population is **1** by L2's own metric, and that one run performs ZERO
prefix substitutions. Decomposing further, L10 finds the corrected
population (single-call literal blocks) is 28, of which 27 substitute
nothing; the true interpolation population is 30 calls / 1,474 bytes
(1.9% of emitted literal text). L10 also corrects L2's headline number:
*"652 `%s_` substitutions"* decomposes to only **306 of 584 pairable
occurrences (52.4%)** actually binding the prefix — the rest bind the
uppercased prefix (139, the single largest binding — itself a NEW
finding, L10-L10-5), a machine name, a table tag, or a function name.

**Verdict: L10-L10-7 CLOSES the question L2-L2-3 left open, on ground L2
itself specified.** This is not a disagreement to surface — it is the
measured resolution of a named-but-unmeasured item, and the synthesis
should treat L2-L2-3 as superseded by L10-L10-7 rather than as a
standing finding.

### 2.5 `write_file`'s missing `ferror()` check — DUPLICATE FINDING

**L8-F5** and **L10-L10-8** are the identical finding, found
independently by two lenses: `cli/main.c:292-299`'s `write_file` checks
`fclose`'s return but not `ferror()` on the `fputs` that wrote the
artifact, so a short write on a full disk can be reported only if it
happens to surface at close. L8 additionally covers the stdout path
(`main.c:1209,1726`, no `fflush`/`ferror` before `return 0`); L10 covers
only the `write_file` half and explicitly notes "do not ride stage 2"
(the CLI-channel wave). **Dedupe to one finding, citing both lenses**,
with L8's fuller stdout-path coverage as the more complete version.

### 2.6 The allocation-failure injector — TIER DISAGREEMENT

**L8-F6(d)** proposes a build-time `-D` allocation-failure injector,
files it as **DESIGN-EVENT**, and explicitly defers it under D77 behind
three cheaper precursors (F6(a)/(b)/(c) — a sabotage row, a verdict-arm
split, a grep-derived file-list replacement).

**L5-R1** independently arrives at the identical mechanism (an
allocation-counting injector reached via `-include` + a parameterized
`BUILD_DIR`) and explicitly **reclassifies it from DESIGN-EVENT to
LOCAL**, arguing the assumption that made it look heavyweight (needing
an allocation hook compiled into the library) is false — the tree's own
`BUILD_DIR`/`CFLAGS` machinery already supports it with zero edits under
`src/`. L5 keeps L8's staging order (F6(a)/(b)/(c) first) but disagrees
on the TIER the injector itself belongs in.

**This is a real disagreement between two lens reports on the same
proposed mechanism's effort classification — flagged for the manager
in §3, not resolved here.**

### 2.7 `emit_vm.c`'s "second pass" — five lenses converge on the same surface; NOW DELIVERED as EP2, which corrects L11 in five places

L1 §4 item 1 names the need explicitly: *"the single largest unreviewed
surface in the primary tier ... I am naming the need."* L2 §6 (residual
risk) flags the non-text-mechanics tail as a likely-richer-than-sampled
population. L5 §10 item 1 independently names the identical need from
the check-design side (*"the VM's rung/slot/frame emission is the
largest body of code in the tree with no internal-property check of any
kind"*). L10 §4.3 goes further and SEQUENCES it — explicitly ordering a
"lens 1 second pass" to run BEFORE its own stage 3 (the fragment layer),
because stage 3 works in exactly that surface and a post-hoc review
would be reviewing the refactor rather than the original design.

**L11's report substantially anticipated that second pass**, though it
was not chartered as one: F1 (`pcrec_emit_vm` — the analysis/config/
emit split), F7 (`vm_emit`'s fat arms), F8 (`vm_render_listing`'s
repetition), and F12 (`vm_cursor_rep`'s duplicated span-scan) all live
inside exactly the surface L1/L2/L5/L10 named as unreviewed, and L11 §7
stated it was NOT naming a further second-pass need on the emitters for
exactly that reason.

**EP2 is now that formally-chartered second pass, and it independently
re-derived every number rather than inheriting L11's** (per its own
§0 discipline: "where a number disagrees with a prior report, the
disagreement is stated and the instrument difference named"). It
confirms L11's central diagnosis (an analysis pass, a configuration
pass and an emitter share one body) while correcting it in five
measured places — see §2.8. **This is the review's clearest instance of
a follow-on request being both substantially anticipated by one lens
(L11) and then formally discharged, with corrections, by the lane
chartered to do it (EP2)** — the manager should treat EP2's §5
sequence table as the authoritative wave-1 ordering for `emit_vm.c`
work, superseding L11-F1's own four-commit proposal, and should update
L10's stage plan with EP2's two named repairs (§2.3's buffer-floor
repair; the `irsb`/listing-reach items in §6).

### 2.8 L11-F1 vs. EP2 — five corrections, itemized

EP2 verified L11-F1's proposal against the actual source (rather than
reviewing it as prose) and found five measured corrections, each
recorded here as prior-number + EP2's-number + the instrument
difference, per the team lead's instruction:

1. **Anchor count: 26 → 29 rows / 32 anchor records.** L11-F1 states
   "26 sabotage rows attribute inside this function ... 10% of the
   whole failing-direction net," derived by L11's own general-purpose
   attribution method (§1 of L11's report: parse `SAB_FILE` + first
   non-blank `SAB_BEFORE` line, locate by span). EP2's dedicated
   anchor-mapping pass over the same function — sourcing every `S*.sh`,
   exact-string-locating each `SAB_BEFORE`, and separately counting
   ROWS vs. anchor RECORDS (a row with `SAB_FILE2` contributes 2) —
   finds **29 distinct rows / 32 records, 11.1% of the tree's 261
   rows**, not 26/10%. L11's own report explicitly flagged its
   attribution counts as FLOORS (~24 of 261 tree-wide anchors didn't
   match today's source byte-for-byte in L11's pass); this is that
   floor being met from inside the one function it undercounted most.
2. **`vm_build_region_saves`'s proposed signature cannot compile.**
   L11-F1 proposes `static void vm_build_region_saves(Vm *v, Ast *root,
   int nstate);`. EP2, reading the span line by line, finds the region
   reads `snap_before[i].guard/.low/.mark/.rev/.ctr/.lookmark/.lookpos`
   and the matching `snap_after[i]` — seven family ranges per region
   produced by an INTERLEAVED counting pass — which are `VmSnap`-typed
   locals in `pcrec_emit_vm`, not derivable from `(v, root, nstate)`
   alone. The corrected signature adds `const VmSnap *before, const
   VmSnap *after` parameters (EP2-P3).
3. **A second clean extraction (`vm_plan_regions`) is missing from
   L11's table entirely**, folded invisibly into its `8539-9000` region
   row (L11 measured that row as one 13%-share region; EP2 finds it is
   actually TWO non-emitting fixpoints back to back — `vm_resolve_
   nonnull` and `vm_plan_regions`, EP2-P1/P2 — with a separate
   already-a-function snapshot pass between them and P3's true start).
4. **L11's proposed 4-commit order is corrected in three places** (all
   filed as EP2 §5, echoed in the EP2 findings table above): X8 does
   NOT go first (it is the sequence's only abi-adjacent step and
   depends on L10's `sb_name`/`sb_upper` substrate, which L10's stage 3
   supplies — X8 rides stage 3, matching L10 §4.3 item 4's own
   recommendation, rather than leading the whole sequence); the missing
   `vm_plan_regions` extraction (correction 3) must precede P3 and P4;
   and P3-before-P4 is backwards on cost grounds — P4 is zero-anchor
   and depends only on P2, P3 is six-anchor, so taking P4 first means a
   red in P3 bisects to P3 alone.
5. **L11-F12 (`vm_cursor_rep`'s duplicated span-scan) is CONFIRMED but
   its proposed signature is wrong.** L11 proposes
   `vm_emit_span_scan(StrBuf*, const Vm*, const Ast*, int stride, const
   char *test, const char *bound)`. EP2 finds the greedy arm emits an
   extra declaration (`lim_`) INSIDE the block the helper would open,
   which the shared bound expression then names — so a `bound`
   STRING parameter cannot express it; the corrected signature takes a
   `clamp` parameter that owns opening the block (EP2-E2).

None of these five corrections changes L11-F1's underlying diagnosis
(the split is real and the seam is clean); all five are measured
repairs to L11's proposed IMPLEMENTATION, found by EP2 verifying against
source rather than inheriting L11's read. **Flagged for the manager: any
wave brief drawn from L11-F1 as currently written will discover
correction 2 and 5 at compile time; EP2's §5 sequence table is the
version that compiles.**

---

## 3. RULINGS-FOR-FRANK LIST

Every finding a report explicitly flagged as needing Frank's ruling or a
manager ruling, in the reports' own words.

1. **L9-P1** — rename the 12 unprefixed exported symbols (1,652 source
   sites, 8 sabotage re-aims) vs. archive-symbol localization (fixes all
   256 non-public exports at once, but is per-platform build machinery
   against D2's "plain GNU make on purpose"). Author: *"a Frank question,
   not a manager default."*
2. **L8-F3** — `emit_state_legend`'s silent OOM degradation: refuse the
   compile (consistent with the rest of the tree) vs. announce the
   omission in the artifact (preserves today's degrade-gracefully
   intent). Author: *"wants a one-line ruling before the edit."*
3. **L10-L10-6** — `emit_vm.c:8165`'s `--emit-listing` column-width
   truncation: is the listing's column width a CONTRACT (the site's own
   comment warns a rename must check it) or may it move freely when the
   buffer is retired? Author: *"a manager question, not built here...
   escalate rather than fix in-flight."*
4. **L10 §2.2 item 3 / §4.3 point 4** — should lens 1's X8 (stamp
   emission) ride L10's stage 3, since both share the same 123 anchors
   and 7 checks? Author recommends yes but states *"flagged for the
   manager rather than assumed."*
5. **L1-X9 / L2 §8** — the axes-table design event (`axes.def`) overlaps
   between lens 1 and lens 2's own reports; L2's closing note says the
   synthesis should *"merge, not double-count."*
6. **L3-F1** — invert `limits_check.sh`'s name-keyed filter to scan ALL
   numeric `#define`s regardless of spelling (vs. widening the
   vocabulary a third time, which the author argues just defers the next
   miss). Explicitly marked *"a judgment call, marked as such."*
7. **L3-F2** — the `[ART-SIZE]` bar/threshold split: is the asymmetry
   deliberate (percent vs. byte-ceiling are different kinds of thing) or
   accidental? Author offers both dispositions and neither chooses.
8. **§2.6 above** — the allocation-failure injector's effort tier:
   L8 says DESIGN-EVENT deferred under D77; L5 says LOCAL, buildable now.
   Two lens reports disagree on the same proposed mechanism.
9. **L9-P5** — `PCREC_*`'s namespace split (47 contract / 113 internal)
   is named as a DESIGN-EVENT with a stated trigger ("a second collision
   or a v1 declaration, whichever arrives first") rather than proposed
   now — a standing decision point, not an open question today.
10. **L6-L3** — whether `src/core/compile.c` should physically move to a
    `driver/` tier, or whether fixing the layer-MODEL (a tool constant +
    prose) is sufficient. Author explicitly declines to propose the
    move: *"D77 says wait for a measured need."*

---

## 4. FIX-NOW CANDIDATES

Findings any report marked as immediate/one-line/independent-of-waves.

| cite | fix | why it's fix-now |
|---|---|---|
| **L8-F1** | `cx.job->scr_test.cx = cx.job->scr_desc.cx = &cx;` (one line) | Author: *"do this first regardless of wave ordering; it does not wait on a refactor."* Closes a live caller-`abort()`. |
| **L9-P2** | One-line comment fix (`PCREC_ENC_UTF8` is shipped, not "not yet implemented") | Author: *"do it first."* Recurrence of R29's exact defect class. |
| **L5-R0.2** | Add `run_cpset_structure.sh` and `run_mrl_tests.sh` to `san_scripts.txt` (2 lines) | Author's own #1 rank: *"the only CORRECTNESS-RISK item here that is already true rather than prospective."* |
| **L9-P8** | Delete "an order of magnitude" / write "well under" | One line, 0 checks. |
| **L9-P7** | `RX_NCAPS`→`<PREFIX>_NCAPS` in 5 comment sites (+2 more) | Mechanical, 0 checks; rides with P2/P8 as one commit per L9's own §8 ranking. |
| **L4-A2** | Attach the [DD-14] wave-G correction to the [M6.4.2] paragraph it supersedes (one clause) | One edit; the one exception to an otherwise-honest 47/48 correction-in-place discipline. |
| **L3-F3** | FNV-1a helper pair (`fnv1a_32_init`/`fnv1a_32_mix`) | MECHANICAL, 0 checks, 0 emitted bytes — author's own "pre-tour cleanup" ranking. |
| **L3-F5** | Fold "missing closing ) for group" to one `#define` beside `REFUSE`, correct the stale comment | MECHANICAL — author's own "pre-tour cleanup" ranking. |
| **L1-X2** | Merge `cg_walk`/`pr_walk` into `pcrec_ast_visit` | Author: *"the cheapest true finding in the report and it is also the pilot that de-risks X1."* 2 sabotage re-aims (call-text quotes, not body). |
| **L11-F8** | Collapse `vm_render_listing`'s 3 section loops + 6 slot loops | Author: *"the cheapest possible first move for a refactor wave that wants to prove its method."* 0 sabotage anchors. |
| **L8-F2, L8-F5** | `cli_parse`/`apply_target` leak fix; `write_file`/stdout `ferror()` check | MECHANICAL, CLI-local, independent of everything — author's own ranking (tier 3). |
| **L6 §5 step 1** | Add `-Wl,-dead_strip` to `match_api.md` §8.0's worked example, with the reason | Doc-only, MECHANICAL; recovers 43,968 of 44,448 rxt-tier bytes for every consumer who copies the example, with zero code change. |
| **EP2-E1** | `vm_slot_ref`, the arena-returning sibling of the file's OWN already-declared `vm_slot_expr`, over 4 hand-rolled sites in `vm_call`/`vm_splice` | Author's own ranking: step 1 of EP2's wave sequence, 0 anchors inside, retires 8 of 40 category-(a) buffers (20% of the fragment-layer population) in one edit — the highest-value, lowest-cost item the whole `emit_vm.c` surface offers. |
| **EP2-E0, E2, E3, P1, P2, P4** | The six zero-anchor extractions in EP2's own §5 sequence (steps 2-7): the merged X1 walkers (1 anchor, near-zero), `vm_emit_span_scan`, `vm_bounds_text`, `vm_resolve_nonnull`, `vm_plan_regions`, `vm_memo_region_costs` | All verified byte-neutral by construction (zero `sb_*`/L6-primitive calls in the moved spans); author's own cost model (§3.5) ranks these first precisely because they cost zero sabotage re-aims. |

---

## 5. PROBED-AND-HELD MASTER LIST

Concatenated and deduped across all reports; each with its lens cite.
This is the review's do-not-reopen record.

**Duplication candidates examined and rejected (L1 §2):**
- Clone group 7 (`pf_emit_*` prefilter bounded/unbounded pairs) — the
  split is caller-observable through a stamp; not a duplication.
- Clone group 4 (module doorway ports) — shared signature is the
  doorway contract doing its job, not duplication; the 2 genuine
  members are absorbed into L1-X6.
- Clone group 26 (`axis_row`/`limit_row`/`emit_in_entry_defs`) — already
  the correct per-dump-type row-printer shape.
- Group 1's low-`group_frac` members (`vm_cost`, `pss_walk`,
  `rd_reverse`, `emit_attempt`, `p_class`, `compile_driver`) — long
  functions containing ONE instance of the walk idiom; belong to lens 11
  by length, covered by X1 for their idiom instance.

**Nine `atomic.c` predicate walks must NOT merge into one function** —
found independently in **L1 §5** and **L11 §5.1 item 3**: every one of
the nine differs in at least one per-kind arm with a measured
justification (e.g. `pcrec_has_collapsible_rep` prunes `A_LOOK` because
the NFA builder erases lookaround bodies); a naive merge would delete
two sabotage rows' plant sites and the `-Wswitch` compile-error alarm in
one commit. Only the traversal (not the verdicts) is extractable — this
is X1's own defining constraint.

**Config-centralization candidates held (L3 §3, H1-H9):**
- H1 — stamp-value string duplication between emitters and
  `axes_dump.c` (~30 rollup rows) is KNOWN, ARGUED, and GUARDED
  two-directionally by `axes_registry_check.sh`.
- H1a — `cli_flag_of`'s rename-blindness is caught INCIDENTALLY by a
  different check arm (the description-table join); not worth a change
  today, worth knowing if that arm is ever relaxed.
- H2 — `prefix_k.c`'s 256-entry byte-frequency table is the
  best-documented data in the tree (cited priors, stated normalization,
  a published total, an asserting check); naming its cells would destroy
  its readability.
- H2a — the ppm scale (`1000000`) spelled 15 times in one file is a
  genuine residue but belongs to whatever wave touches `prefix_k.c` for
  another reason.
- H3 — `prefix_k.c`'s cost-model constants (`C_MEMCHR` etc.) are HELD as
  `limits.def`-row candidates, counted under L3-F1's allowlist gap, not
  filed as "magic numbers."
- H4 — `tune.c`'s `TUNE_TABLE` policy cells are RULED (`tune.c:53-58`'s
  own citation-or-em-dash convention; the r60 panel rules the shape).
- H5 — `requires module` spellings inside `registry.c` are the RULED
  central home (`RegDiag`), not duplication; L3-F4 is deliberately scoped
  to the 20 sites OUTSIDE this mechanism.
- H6 — `#include` directive frequency rollup rows are the dependency
  graph — lens 6's deliverable, not a lens-3 finding.
- H7 — single/two-character literals (`'('`, `'{'`, `'^'`, ~600+
  occurrences) are the GRAMMAR, deliberately held as a class; naming
  them would move the parser away from the PCRE2 syntax page it is
  compared against.
- H8 — emitted-C fragment strings (`"    }\n"` etc.) are out of lens 3's
  scope; routed explicitly to lens 2/lens 10 (recorded here for the
  synthesis rather than dropped).
- H9 — `PREMUL_DEAD 65535` coincides numerically with `PCREC_MAX_REPEAT`
  but is an unrelated table sentinel; joining them would be a false
  abstraction.

**Rxt-cut / dependency candidates held (L6 §4, 8 items):**
1. No include cycle exists in the tree (with `enc` filed between `core`
   and `parse` per L6-L1's proposal).
2. `lib/pcrec.h` does not leak the rxt tier — the public header declares
   exactly 3 functions; the rxt drag is entirely internal.
3. The dump tier needs no cut — already outside a matcher-only
   consumer's link (L6-L4 is a filing finding, not a linkage one).
4. `enc.h`'s dependency on `core/internal.h` (StrBuf, PcrecFold only)
   is not an obstacle to the `enc`-tier move.
5. The composer's ruled position ([DD-13b.W1.3]'s ordering constraints)
   is satisfied identically by the proposed hook call.
6. No sabotage row or codegen check anchors on `rxt_compose` at all
   (verified by grep).
7. `PcrecEnc` splitting the struct (vs. splitting the file) would buy
   nothing the directory move doesn't already buy — not recommended.
8. The 44,448-byte figure for the rxt tier's `__text` contribution is
   NOT the cut's true value — `-dead_strip` alone recovers 43,968 of it
   with zero source change; the source cut's marginal win is ~480 bytes.

**Error-path candidates held (L8, H1-H13):**
- H1 — every `setjmp` has its `Ctx`; nothing that can fail allocates
  before it (5:5 pairing, zero hits in code across the pre-`setjmp`
  windows).
- H2 — the `volatile`-across-`setjmp` discipline is complete and
  mechanically backed by `-Wclobbered`/`make strict` (one caveat: vacuous
  at `-O0`, not a live finding since nobody builds that way).
- H3 — no `free()` of an arena-backed pointer anywhere (all 76 sites
  classified).
- H4 — `tab_grow`'s apparent double-free is not one (the comment's
  wording invites a second look; the claim itself is true).
- H5 — `minimize.c`'s seven heap tables are correct on all three exits
  (K7's named hand-cleanup exception, verified still correct through two
  later edits).
- H6 — `scanedge.c`'s ten heap tables are correct on all four exits (the
  nine-way free block appearing four times is a lens-1 extraction
  candidate per L11-F15, not an error-path defect).
- H7 — library re-entry is clean (zero function-local statics; the
  three file-scope mutables are write-once at spec-parse time).
- H8 — allocation is architecturally confined (`emit_vm.c`, `parse.c`,
  every `mod_*.c`, and most `opt/` passes have ZERO raw allocations —
  the reason F1 is the only hole).
- H9 — the three `Ctx`-taking `strndup` helpers (L1-X4's cluster) all
  route correctly; only `rxt_source.c`'s bare-`Arena` pair diverges
  (L8-F4).
- H10 — `apply_target`'s success path structurally cannot leak
  `ts.libdirs` (`cli_extras_clean`'s all-zero-tail test forces the free
  branch); worth preserving explicitly when L8-F2 is fixed.
- H11 — K11's returned-claims epilogue is intact (all four doorways
  still return `ExtResult`).
- H12 — file handles are balanced (3 `fopen` sites, every error route
  closes; no temp-file cleanup obligation exists anywhere).
- H13 — the `-o` path writes nothing before compile success (no partial
  overwrite hazard; the only partial state is L8-F7's `.c`/`.h` pair).

**Public-surface candidates held (L9 §6, 9 items):**
1. No leaked internal types or helpers in `lib/pcrec.h` (all 4 types, 3
   functions are caller-facing, classified against `match_api.md` §8.0).
2. No duplication/contradiction between `pcrec.h` and `internal.h`
   (the latter includes the former; nothing re-declared).
3. No `PCRE2_*` native spelling anywhere in the public header (D38's
   addendum honored exactly).
4. No flag-bit collision, gap, or reuse across all 26 bits.
5. Four inline numeric constants in the header agree exactly with
   `limits.def` (though unguarded by any check — right by care alone).
6. The splice/linkage stamp names in the header are current ([SPEC-1.3]
   drift, fixed at `40d9f79`, has not recurred).
7. The `PCREC_ENGINE_AUTO`-enum / `_DFA`/`_VM`-`#define` asymmetry is
   RULED (D60 addendum) and correct — necessary for a TU including both
   the public header and an artifact header to compile.
8. The declared 3-function surface is sufficient for the library use
   case (cites L6 arm 1 directly: it links and emits 47,649 bytes).
9. The 22 `-fno-*`/`FORCE_*` denial bits are NOT a leaked-internal
   finding — D46/D47.3/`tuning.md` §2 rule them public; recorded so a
   later lens does not re-open it without new grounds.

**Unit-seam candidates held (L5 §7, 11 items):** `cpset.c`'s interval
algebra (held on coverage; its sanitizer gap is L5-R0.2's own separate
finding), the caseless fold's byte relation, `pcrec_cwmin`/`cwmax`,
`p_alt`'s branch count, the registry's row invariants, both engines'
answers at every rung (explicitly: *"a unit test of a rung's emitted
shape would duplicate oracle coverage and is explicitly the thing this
lens must not recommend"*), the `volatile`-across-`setjmp` discipline
(same finding as L8-H2, held mechanically by a compiler diagnostic
rather than a test), the arena/heap ownership boundary (held by L8-H3 as
a review result AND by ASan as a running one), `minimize.c`/`scanedge.c`'s
hand-freed heap tables (held as REVIEW-held, not check-held — named as
the strongest injector candidates once L5-R1 exists), engine selection
(caller-observable through a stamp, has an answer-level surface), and
`sb.c`'s append/grow arithmetic (covered end-to-end by every artifact
the corpus compiles — only its FAILURE path is uncovered, which is
L5-R1).

**Function-altitude candidates held (L11 §5.1, 7 items):**
1. `emit_attempt`'s per-state block — declined; the extraction's
   parameter list would be the function's own local state handed back
   to it.
2. `pcrec_select_engine`'s prefilter block — declined; 276 span lines
   but ~25 code lines, all at the same altitude, rationale not
   separable from the decision it explains.
3. The nine `atomic.c` predicate walks — held, cross-referenced above
   with L1 §5.
4. `compile_driver`'s `volatile` declarations — held; required by
   `-Wclobbered`/`make strict`, not noise.
5. `emit_vm.c`'s job-owned scratch buffers (`scr_test`) — held; not a
   premature optimization, a LeakSanitizer-motivated fix for a
   `longjmp`-out-of-emission hazard.
6. `pcrec_minimize_dfa`'s five `malloc`s vs. `pcrec_scanedge_dfa`'s
   nine (L11-F15) — held at five; the author states the line drawn
   (fraction of function occupied) is a judgment, not a principle.
7. Splitting any of the four per-rung VM emitters by emitted label —
   held; the labels are one control-flow graph in the emitted program's
   own order.

**`emit_vm.c` second-pass candidates held (EP2 §6, 8 items):**
1. Unifying the rung emitters (cursor/reverse-deterministic/counter-K/
   frames/island/lookaround) into ONE table-driven emitter — declined;
   the table would have to carry the emitted control-flow graph itself
   (differing label counts, slot families, frame discipline, fail-label
   semantics), which is question 3 answering "correctly code-driven."
2. Merging `vm_cost_rep`/`vm_count_slots`'s `A_REP` arm/the rung
   emitters' own rung selection into one decision pass — real, and the
   file's OWN comment (`:4046-4055`) is already aware of the
   triplication and states the cross-agreement invariant instead of
   merging; a DESIGN-EVENT with its own argument, not a review finding.
3. `vm_fadd`/`vm_fmul` merging with the tree's other saturating helpers
   — already L1-X3's territory; these two saturate at `PCREC_MINW_MAX`
   for a stated follow-min-accumulator reason.
4. `vm_emit_f`/`vm_emit_fd` collapsing into one defaulted-argument
   function — declined; `vm_emit_f`'s header states it is "THE ONLY
   MUTATOR of `v->fmin`," and collapsing makes that single-mutator claim
   harder to check for a six-line saving.
5. Retiring `Vm.up[80]` (~110 readers) — L10 already scopes this out of
   wave 1 (a data-flow change through the central struct with a
   different byte-neutrality argument); EP2 concurs and adds it is the
   file's 59th declaration and belongs in a later `Vm`-field-touching
   wave.
6. `vm_emit`'s six SHORT leaf arms (`A_CLASS`, `A_EMPTY`, `A_BOL`,
   `A_EOL`, `A_END`, `A_GSTART`) as extracted functions — declined; each
   is 4-20 lines and reads correctly as a dispatcher arm. L11-F7's fat-
   arm argument applies only to the four FAT arms, which is how L11
   scoped it.
7. `vm_isl_build` as a candidate for the non-emitting-pass (P1-P4)
   treatment — declined; it emits nothing, matching P1-P4's shape, but
   it is ALREADY its own named function, which is the whole remedy.
8. The `L14` emitting regions (`:9405-11575`, 1,170 span lines of
   prologue/stamps/macros/trailers/entries) as extraction candidates —
   declined, matching L11-F1's own Q5-passes verdict for `emit_attempt`/
   `emit_info_def`'s shape; EP2 adds the measurement that these regions
   hold 22 of the function's 32 anchor records, making a speculative
   split there the sequence's most expensive move for its least benefit.

**13 functions PASS all five of lens 11's questions and should stay
exactly as long as they are** (full list and per-function rationale in
L11 §5): `emit_info_def`, `pcrec_select_engine`, `emit_attempt`,
`vm_revdet_rep`, `vm_counter_phase`, `vm_cost_rep`, `first_of`,
`pcrec_minimize_dfa`, `pcrec_prefix_ksets`, `pcrec_callgraph_build`,
`pcrec_rxt_compose`, `pcrec_rxt_source_resolve`, `compile_source` — plus
`frame_constraints` from the mid-length band (deepest nesting in the
tree, 73 code lines, passes all five). **L2-L2-10** and **L1-X11's**
"recommend no change" enum-mapper anti-findings and **L10-L10-7**'s
template-layer anti-finding are standing do-nots in the same spirit.

---

## 6. SECOND-PASS/FOLLOW-ON REGISTER

Every named-but-not-chartered follow-on found in the reports' own text.

1. **`src/gen/emit_vm.c`'s rung/slot/frame emission surface** — named as
   needing a second pass by **L1** (§4 item 1, "I am naming the need"),
   **L2** (§6, non-text-mechanics tail), and **L5** (§10 item 1,
   independently from the check-design side). **L10** (§4.3) sequences
   it explicitly BEFORE its own stage 3. Per §2.7 above, **L11's own
   report substantially discharges this** (F1, F7, F8, F12 all live in
   exactly this surface) — reconciliation is a manager task, not a fresh
   charter.

2. **`src/parse/rxt_source.c`'s text-handling family** — named
   independently by **L1** (ADDENDUM-2 item 2: groups 13/14,
   `value_trimmed`/`rtrim_ws`/`prose_value`/`read_wrapped_value`/
   `ident_ok`/`defname_ok`/`oracle_ref_ok`, "a real text family it did
   not judge") and **L5** (§10 item 3, citing K57's dedent-strip bug as
   "a shipped bug of exactly that shape" and recommending a lens-5
   second pass start there rather than at the emitters). **L11-F2**
   (the 548-line parse loop) and **L4**'s naming pass (§6, "the
   highest-value continuation") both separately target the same file
   for different reasons (production-as-function extraction vs. naming).

3. **`src/ir/nfa.c` and `src/ir/dfa.c`** — L1 (ADDENDUM-2 item 3) names
   `compile_ast`/`intern` as unread; **L5** (§10 item 2) sharpens this to
   `dfa.c`'s `intern` specifically as *"the one seam I would look at
   first in a second pass"* (a helper whose correctness is a property —
   equal states intern equal — that answers reveal only statistically,
   the same shape as L5-R2/R3).

4. **`lib/pcrec.h`'s macro families** — L1 (ADDENDUM-2 item 4) notes its
   own pass over the header was narrow (only where X9 needed deny-bit
   declarations) and defers the header's own duplication surface to
   lens 9, which then delivered P1-P8.

5. **The static-ability census over `libpcrec.a`'s ~244 `pcrec_`-prefixed
   exports** — named by **L9** (§7): classified by prefix but not
   individually audited for whether each needs external linkage at all;
   explicitly noted that L9-P1's archive-localization option (b) would
   make this census moot.

6. **The emitted artifact's OWN public surface** (`rx_*` fixed-literal
   ABI types, `<prefix>_buffers`, the stamp catalogue) — named by **L9**
   (§7) as *"a second public surface of comparable size to this one...
   it deserves its own pass."*

7. **The 50-99 code-line band (45 functions, 16.9% of the primary
   tier)** — named by **L11** (§7) as where a second lens-11 pass should
   go if chartered, with `vm_cost`, `vm_rep`, `vm_rev_emit` named first
   since F7 and F12 both land next to them.

8. **The 784 functions at or under 49 code lines (51.7% of the tier)** —
   **L11** (§7) states explicitly this is genuinely unmeasured for
   question 1's "too general/over-decomposed" direction, not assumed
   clean.

9. **A non-text "policy inlines mechanics" second pass over the census's
   88-and-below tail** — named by **L2** (§6) as the trigger its own
   ADDENDUM-2 asks it to name: rank 3 (growable append) was caught only
   because the clone detector happened to flag it, "which suggests there
   are more of that shape."

10. **`cli/main.c`'s option-string plumbing beyond the rollup** — named
    by **L3** (§1) as not individually audited (lens-2/lens-11
    territory as much as lens-3's).

11. **Stage-1's escaping measurement** (does any string reachable by the
    three under-escaping dump files contain a tab/newline/control byte
    today?) — named by **L2** and restated as still-owed by **L10** (§6
    item 1): *"neither lens took it... the one measurement a stage-1
    lane must take before writing code."*

12. **`Vm.up`'s retirement** — named and deliberately scoped OUT of wave
    1 by **L10** (§2.2 item 2, §6 item 5): the largest residue of
    L10-L10-5, "should not be picked up opportunistically."

13. **The secondary tier** (`tests/lib/`, `tests/harness/`) — named as
    out-of-scope-this-round by every lens that touched it (**L2, L3,
    L5, L11**), dispositioned to the next review round per the
    ratification.

14. **`emitvm_second_pass.md`** — DELIVERED (worktree `emitpass2`, cited
    `EP2` throughout this document) and now folded into this collation
    as a twelfth source, per the team lead's follow-up scope addition.
    Items 1 and 2 above are the context EP2 inherited and built on
    (§2.7, §2.8).

15. **The `irsb`/`run_ir_listing.sh` byte-neutrality arm** — named by
    **EP2** (§1, §3.3) as an item L10's stage 3 now OWES: `vm_render_
    listing` (layer L12) writes a SEPARATE output stream (the
    `--emit-ir` listing, `job->irsb`) that none of L10's four standing
    `.c`-artifact identity gates or its full-corpus emit-diff can see;
    6 of stage 3's category-(a)/(c) buffers write only to this stream,
    so any stage touching L12 must add `run_ir_listing.sh` as an
    explicit comparator rather than relying on the gates already named.

16. **The listing-reach census** — named by **EP2** (§7, "the one thing
    I would want measured before wave 1 starts and did not measure — no
    `make` allowed in this lane"): whether `run_ir_listing.sh`'s
    population actually reaches L8's rung emitters, whose `vm_rolef`
    role text is the listing's own content — the CONVERSE of the `irsb`
    finding above (item 15 shows the `.c` gates don't reach the
    listing; nobody has checked whether the listing check itself
    reaches everything a wave step touches). EP2 proposes this ride
    alongside L10's stage 0 (the long-prefix corpus control) as one
    `RXTDUMP`-style census.

17. **The A1 ruled-record boundary on `emit_vm.c`'s non-emitting
    passes** — confirmed, not reopened, by **EP2** (§3.1): `src/core/
    internal.h:5412-5418` rules the nullability fixpoint's recurrence
    (`vm_nullable`, 10 call sites across three of the file's layers)
    file-`static` to the emitter, and all four fixpoint candidates
    (EP2-P1 through P4) write into `Vm`, a file-local unexported
    struct — so NONE of them may move to `src/opt/` or an `ir/`-
    adjacent home without exporting `Vm` or splitting the recurrence
    across a ruled boundary. The realistic home stays file-static
    helpers in `emit_vm.c` itself, which is what L11-F1 already
    proposed; a sibling TU behind a private header is named as a
    legitimate LATER option, explicitly not recommended for wave 1
    (it converts a text change into a build-graph change for no
    capability the statics lack).

18. **`vm_isl_*`, the alternation-island layer (685 lines / 312 code, 9
    functions) — a ZERO-ANCHOR layer, named by EP2 (§7 item 1) as a
    gap somebody should price, framed explicitly as a `tests/mech`
    question rather than a lens question**: it is the only substantial
    layer in the whole file with no failing-direction coverage at all,
    and EP2 read only its banners and `vm_isl_emit`'s emission surface
    — `vm_isl_build`, `vm_isl_words`, and the trie insert were not read
    at line level.

19. **`emit_dfa.c`'s unrun third buffer category** — EP2's category-(c)
    finding (§4, DERIVED_CONSTANT + literal margin, 5 sites in
    `emit_vm.c`) was explicitly NOT run against `emit_dfa.c`, which is
    out of EP2's chartered scope. EP2 states plainly: "if `emit_dfa.c`
    has derived-constant-sized buffers too, stage 3's floor moves
    again" — the §2.3 buffer-population repair may be incomplete until
    someone runs the same category-(c) grep against the second
    emitter.
