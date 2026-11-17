# archreview report: architecture-level review of today's tree (unit A2 of [ARCH-STEP])

## STATE AT HANDOFF

Lane archreview (opus), branch lane/archreview, tree at cd781a306 (main at launch). Read and report only: no code,
guide, skill or test changed, no `make`, no suite. Rulings file `docs/dev/lanes/archreview_rulings.md`: empty at
every read (start, before the WIP commit, before this report); no R-n applied.
Premise test passed: `docs/dev/lanes/archhist_report.md` has `## PATTERNS ACROSS THEM` (line 125) and
`tools/review/out/function_census.tsv` exists.
Findings and options are for the owner to weigh; nothing here decides or schedules. JUDGEMENT and INFERRED are marked;
everything else carries a file:line or the command that shows it. Paths are relative to the worktree.
OWED: none

## HOW THE TREE WAS READ

Metrics. The committed `tools/review/out/*.tsv` are dated 2026-09-21 (header of `function_census.tsv`: commit ed15116,
935 rows) and predate START-TABLE, DEC-FALLBACK, entry rows, VMREC and the kit migration, so I RE-RAN four scripts at
cd781a306 into `$PCREC_TMPDIR/scratch/archreview/` (not committed):
- `function_census.py` -> 2,657 functions, 102 files, 34 with code_lines > 100 (was 935 rows: the committed one is
  not just stale, it covers a third of the functions).
- `include_graph.py` -> 510 includes, **2 back-edges** (`src/core/findings.c:52` -> `enc/enc.h`;
  `src/core/internal.h:3429` -> `facts/facts.h`).
- `clone_candidates.py` -> 154 candidate groups, 608 member rows.
- `churn_hotspots.py` -> top hotspot `src/gen/emit_dfa.c` (score 8,047,811).
- NOT re-run: `literal_census.py`, `fragment_census.py` (the literal question was not needed for any finding below).

Reading. Sizes by `find src cli lib memfn/src -name '*.[ch]' -o -name '*.def' | xargs wc -l | sort -n`: emit_dfa.c
17,233; emit_vm.c 14,539; internal.h 9,658; rxt_source.c 5,300; memfn/src/window.c 3,960; compile.c 3,915;
cli/main.c 3,623. I read: `docs/dev/lanes/archhist_report.md` whole; `docs/dev/guide/architecture.md` whole;
`docs/design/plan_row_bodies/ARCH-STEP.md`; `src/CLAUDE.md`; `src/facts/CLAUDE.md` line 7; APPROACH.md headings;
`docs/design/extension_design.md` both panel-outcome blocks (lines 16-72, 1238-1284); `docs/design/stream/roadmap.md`
§1 table and §2 hubs (lines 82-110, 496-618); `docs/design/predicates_draft.md` lines 1-60; `src/core/kindrow.def`
header; and the code at every site cited below (each opened with `sed -n` or grep, not taken on a helper's word).

Helpers. Three sonnet helpers, read-only, one area each, findings written to scratch: `chains.md` (decision chains
beside declared tables), `landing.md` (where each coming feature lands), `seams.md` (seams and parallel mechanisms,
plus a call-level back-edge script `backcalls.sh` -> 89 raw rows). I re-checked their load-bearing claims; where my
count differs I use mine and say so (example: the helper counted 45 `cand_finish_of ... CAND_ROUTE_VM` tests in
emit_dfa.c; `grep -c "cand_finish_of(cx) *[!=]= *CAND_ROUTE_VM" src/gen/emit_dfa.c` gives 26 lines, and 26 is used).

NOT read (gaps, not clean bills): `docs/design/memfn/integration.md` (9,636 lines; only memfn/CLAUDE.md's boundary
section via the helper), `docs/dev/guide/coding.md` beyond what the history report cites, memfn/src beyond the table
list (`finder.c:252 fd_rows[]`, `ofsskip.c:496`), `src/parse/rxt_source.c` (5,300 lines, the .rxt reader), the
emitters' bodies outside the cited functions, `src/enc/`, `src/dump/` beyond facts_dump.c, `analyze/`, tests/.
`docs/design/cover_cap.md`, the FLAG-DEMOTE map and `docs/design/vlookbehind.md` were read by the landing helper, not
by me; their rows below cite its file:line results, which I spot-checked only where marked.

## WHERE DECISIONS ARE STILL CHAINS

Headline (JUDGEMENT): the classic long `else if` ladder is nearly gone from the decision files (no run of four or more
`else if` in select_engine.c, compile.c outside its tables, memfn_sites.c, atomic.c, possessify.c or req.c, helper's
`ladder.awk`). What remains is a different shape the table rule does not name: **a table decides, and its ANSWER is
then re-tested by hand in several emitters** (chains 1-2), plus three families that never got a table (refusals,
CLI, kind leaves). Ranked by how likely the next features touch them:

1. **The start table's RECOVER/FINISH answer re-dispatched in the emitters.** `cand_rows[]` (src/gen/emit_dfa.c:10517,
   ~37 rows) decides the strategy; then `emit_unanchored` switches on the recover act (`case CRA_SEARCH_FROM`,
   `CRA_END_MINUS_W`, `CRA_LANDING`, `CRA_REVERSE`, emit_dfa.c ~13813-13959, followed by `if (act == CRA_SEARCH_FROM)`,
   `if (act == CRA_LANDING)` guards); `emit_attempt` tests `act == CRA_*` seven times (emit_dfa.c:15015-15049);
   `emit_rev_end` has ~19 top-level ifs over CRA_*, `RF_*` and `CAND_ROUTE_VM` (emit_dfa.c:14816); the prologue comment
   prose is keyed on `act` (emit_dfa.c:16115-16165). `grep -c CRA_ src/gen/emit_dfa.c` = 36. And 26 separate two-way
   tests `cand_finish_of(cx) ==/!= CAND_ROUTE_VM` ask "am I on the VM route" ad hoc (command above). Arms: 4 + ~7 + ~19
   + 26. Sits beside: cand_rows[] itself, `revend_forms[]` (emit_dfa.c:14110), and the pf rows that already carry
   `emit_block`/`emit_define` hooks (emit_dfa.c:13971, helper). History sibling converted: START-TABLE (archhist 10)
   converted the SELECTION, not the action; this is its unconverted half. Next features touching it: A-REV / reverse
   walks (roadmap A-REV), VLOOKBEHIND stage 2's reverse use, S4's LOOK-LOCATE (a signed-offset span row), A-HYB.
2. **Engine identity asked three ways.** `fit.chosen == ENGM_DFA/VM`, `fit.chosen ... || fit.prefilter`, and
   `cand_route_of`/`pcrec_cand_body_route` in emit_dfa.c:406, 1803, 1926, 3892, 8207, 8678; emit_iter.c:36, 41;
   compound.c:208-211 (opened: `cx->job->fit.chosen == ENGM_DFA && pcrec_cand_body_route(cx) == CAND_ROUTE_ATTEMPT
   && !strcmp(pcrec_cand_plain_selection(...), "all")`). ~10 sites. Beside fit_rungs[] (compile.c:1331). Not
   converted in history. Note the `!strcmp(..., "all")`: a decision keyed on a row's NAME string, which the "one
   table per slot" rule names as a narrowing (keying rules on a label instead of on facts).
3. **Request-validity refusals.** `prefilter_decision` (src/opt/select_engine.c:1079-1107, opened): five sequential
   `if (force_on && ...) pcrec_ctx_fail(...)` arms (callout, bref/call/var, both force and deny, the collapse pair,
   force on a non-VM engine); `compile_driver`'s ~9 option-validity ifs (compile.c:2046ff, helper: :2074, 2084, 2108,
   2137, 2191). Decides which option combinations are refused. Sits directly above `pf_admits[]` (select_engine.c:737)
   and fit_rungs[]; the refusals are the one decision family with no row, no name and no listing. History: no sibling
   converted. Next feature: FLAG-DEMOTE (every force/deny pair it moves), COVER-CAP's new limit, IFACE-PUSH.
4. **The CLI parser.** `cli_parse` (cli/main.c:1278): `awk 'NR>=1278 && NR<=1900 && /else if/' cli/main.c | wc -l` = 82
   arms; 22 `!strncmp(a, "--x=")` valued-option arms (helper). The `-f/-fno-` axes already come from
   `src/core/axes.def` (46 `PCREC_AXIS(` rows; loop `cli_axis_apply`, main.c ~1084/1380); everything else is a hand
   arm (`--size-cap` :1324, `--tune` :1467, `--step-budget` :1570). `cli_dispatch` (main.c:2904): ~13 ordered mode
   ifs beside a `CLI_MODES_*` mask. History: REVW wave 4 tabled the guard repetition (d0c8b4c22) but not the options.
   Next: COVER-CAP's `--window-search-width=N`, IFACE-PUSH.
5. **Per-kind leaf lists re-written in every AST pass.** `grep -rlE "case A_[A-Z_]+:" src | wc -l` = 27 files;
   `grep -cE "case A_[A-Z_]+:" src/opt/atomic.c` = 115 (emit_vm.c 107, possessify.c 84, mrl.c 65, revdet.c 62,
   helper). Each pass re-lists the zero-width/leaf/opaque kinds by hand; example `lm_maxw` (src/gen/lmwalk.c:80-105,
   opened) lists `A_EMPTY, A_EOL, A_CTX, A_GSTART, A_KRESET, A_LOOK, A_CALLOUT -> 0` and `A_BREF, A_CALL, A_VAR -> -1`
   although `src/core/kindrow.def` already declares exactly that as its TEXT column (ZERO / ANY) "for the language and
   width readers" (kindrow.def header). The table exists; four of its intended readers do not read it. History:
   D70 union and D62->A_CTX (archhist 1, 6) are this family. Next: any new kind (COND-FAMILY's condition kind,
   A_BOL/A_EOL -> A_CTX still open per archhist 6).
6. `emit_scan_loop` (emit_dfa.c:13524, ~12 ifs) and `vm_emit_search_body` (emit_vm.c:13133, ~19 ifs): which pieces a
   scan loop / VM search body gets (seed head, dead state, budget, prefilter). Partly hook-pointer rows already
   (`f->acc`, `f->pf`, `f->view`, helper). Next: A-HYB, A-POSDOM (the roadmap's "three next-start loops").
7. `pcrec_emit_prologue` (emit_dfa.c:16357, ~11 ifs): which headers/main/orientation are emitted; `part_layout.c` rows
   exist for parts, the non-part path is a chain. Next: anything that adds a header or a stamp (H-ABI, IFACE-PUSH).
8. `pcrec_select_engine` (select_engine.c:1519): a 3-way switch on `opt->engine` with two nested refusals in the DFA
   arm. Small; listed because the engine REQUEST is not a row while every fallback after it is.
9. Enum-to-name switches: 17-member clone group at similarity 1.000 (`fit_act_verb` compile.c:1743, `req_why_name`
   emit_dfa.c:8928, `stop_name` dump/findings_dump.c:44, `kind_name` dump/syntax_dump.c:141, ...). Not decisions;
   listed because the name lives apart from the enum's row where a row exists. Low.

Acceptable shapes, not chains (checked): the `switch (rung->act)` at compile.c:2590 is fit_rungs[]'s executor;
req.c's switches at :1013/:1095/:1108 execute `rb_*_rows[]`; `fit_cr_of`/`fit_sdr_of` (compile.c:1932/1943) decode
cells; `span_fold_kind` (memfn_sites.c:886) is a declared two-enum map.

## PARALLEL MECHANISMS

1. **Width / nullable walks over the AST, four homes.** Question: "how many bytes can this subtree consume, and can it
   be empty?" `pcrec_minw` src/opt/mrl.c:151, `pcrec_cwmax`/`cwmax_walk` mrl.c:685/545, `pcrec_cwmin` mrl.c:723,
   `pcrec_nullable` mrl.c:315; `lm_maxw` src/gen/lmwalk.c:80 (born 6a86bb830, 2026-10-29, after the
   general-form rule of 2026-08-23); `vm_width_row`/`vm_general_min_width` emit_vm.c:11427/11436; `cc_width` /
   `cover_width_bounded` src/gen/known.c:315/479; `pfa_nullable_exact`/`pfa_nullable_collapsed`
   select_engine.c:644/669 (helper lines). Evidence: `lm_maxw` multiplies unsaturated (`l * a->u.rep.rmax`,
   lmwalk.c:94) where the mrl.c family uses `pcrec_sat_mul` (mrl.c:134). VLOOKBEHIND's own design counts FOUR
   mechanisms answering "group g's X" (callgraph fixpoints, possessify `PossCap`, K127 reachability, stage-2 width;
   helper from docs/design/vlookbehind.md).
2. **First-byte sets, five-plus folds.** "Which bytes can begin this?" `first_of` src/opt/possessify.c:523,
   `item_first` :1520, `text_first` :404; `pcrec_revdet_first` src/opt/revdet.c:497; `pcrec_start_set`
   src/facts/startset.c:157; `anf_prefix` src/opt/altnf.c:550; `rn_first` src/facts/req.c:464; `pf_dfa_start_set`
   emit_dfa.c:8062 (helper). JUDGEMENT: several differ on purpose (possessify wants a path reader, kindrow's PATH
   column exists because one reader handed another's answer was a miscompile, kindrow.def header); the TEXT-reader
   members do not, and are not paired by any check.
3. **Saturating arithmetic twice.** `pcrec_sat_mul` src/opt/mrl.c:134 (opened) vs `pcrec_vm_fmul` src/gen/emit_vm.c:3874
   (and `pcrec_sat_add` vs `pcrec_vm_fadd`); clone similarity 0.778; same body, cap differs.
4. **Two answers to "what did the compiler decide", one of them re-read from text.** The decisions live in `Job`
   (fit, cand selection); `fd_decisions` src/dump/facts_dump.c:138-148 (opened) parses `#define <PREFIX>_...` lines back
   out of the finished artifact to list them. Same question, second source.
5. **Emission of one anchored attempt.** `emit_attempt` emit_dfa.c:15410 (227 lines) and `vm_emit_anchored_attempt`
   emit_vm.c:14011 answer "emit one attempt at a start" separately; start handling likewise split
   (`emit_startpos_guard` emit_dfa.c:785 vs `emit_vm_start_seek` emit_dfa.c:8358, the VM's start code living in the
   DFA file). The shared `PCREC_SANCH_*` fact is single-sourced (src/facts/startanch.c); the renderers are two (helper).
6. **"First row that applies" walkers.** `pflw_walk` compile.c:1622, `st_why_walk` compile.c:1697,
   `pf_admit_walk` select_engine.c:859: clone similarity 1.000, six lines each; also `fit_rung_of` compile.c:1513,
   `cand_select` emit_dfa.c:11163. JUDGEMENT: the intended row shape, with the walker repeated per table type.
7. **Parser-module helpers.** Six byte-identical `*_strndup` copies (mod_backrefs.c:146, mod_named_groups.c:83,
   mod_recursion.c:104, rxt_find.c:78, rxt_source.c:399, subst_template.c:119); `br_decimal`/`rc_decimal`;
   `br_name_ref` mod_backrefs.c:281 vs `rc_name_call` mod_recursion.c:293 spell the `\g`/name-reference grammar twice
   (clone 0.375). JUDGEMENT: the helpers are trivia; the reference grammar is a real two-place fix.
8. **The "make a Ctx, catch the longjmp, free the arena" idiom** at least four times: `pcrec_compile` compile.c:3762,
   `pcrec_compile_in` :3791, `pcrec_compile_defs` src/core/compile_defs.c:43, and the dump tier's `--explain` /
   `--probe-ask` ("Both setjmp their own Ctx", src/dump/CLAUDE.md) (helper).
Checked and NOT parallel: CLI vs library option parsing (both expand `src/core/axes.def`; lib/ has no parser);
dump re-deriving facts (facts_dump.c header "ONE PRINTER, NEVER A RECOMPUTATION", checked by run_facts_checks.sh),
except the stamp re-read in item 4.

## SEAMS WITHOUT A CONTRACT

Without (ranked, JUDGEMENT on rank):
1. **`Job` / `Ctx`, the whole-compile blackboard.** `struct Ctx` src/core/internal.h:3970 (~70 fields), `Job`
   internal.h:3538-3818 (63 fields). Reading files (helper, `grep -rlE "(cx|ctx|c)->FIELD\b" src cli`): `cx->opt` 43
   files in every layer, `cx->job` 27, `cx->ncap` 19, `cx->emit_in` 16 (an emit input read from parse and facts),
   `cx->mods` 17. The roadmap counts 14 emitter-written `Job` fields read by the driver (roadmap H-FLAGS "Today",
   r3-B7) and driver-to-row `Ctx.*_dropped` flags. No accessor layer, no declared writer/reader per field. Contrast:
   the facts layer (item C1 below) has exactly this discipline. archhist entries 6 and 9 (D62, FLAG-ACCESS) are this
   seam paid for one field family at a time.
2. **Call-level back-edges the include tool cannot see.** Include graph: 2 rows (above). Calls (helper's
   `backcalls.sh`, 89 raw rows incl. the driver): facts -> opt (`pcrec_minw`/`pcrec_cwmax`/`pcrec_nullable`
   mrl.c, the `pcrec_has_*` predicates atomic.c; documented as "Known wrong-way edge" src/facts/CLAUDE.md:7);
   facts -> opt for plain arithmetic (`pcrec_sat_mul`/`_add`, called src/facts/req.c:217, 579); parse -> opt
   (`pcrec_cwmin`/`pcrec_cwmax` from src/parse/mod_lookaround.c:321, opened; `pcrec_bref_mark`, `pcrec_has_call`;
   `pcrec_pat_char` src/opt/lower_enc.c from parse.c); ir -> opt (`pcrec_callgraph_ntargets` from nfa.c); core -> gen
   (src/core/compound.c:209-211 calls `pcrec_cand_body_route`, `pcrec_cand_plain_selection`, defined in emit_dfa.c).
   No check gates call direction outside facts/ (run_facts_checks.sh's link-symbol checks S296/S297 cover facts only,
   helper). INFERRED: `src/opt/mrl.c` is a node-grain measure library filed one layer above two of its clients.
3. **`emit_dfa.c` is two things in one file.** gen/CLAUDE.md lists it as both DFA engine emitters AND the shared
   prologue / ABI types / rx_info / main / stamps / find emission; it also holds VM start logic (`emit_vm_start_define`
   :8326, `emit_vm_start_seek` :8358, `pf_vm_start_applies` :8201) and `PCREC_ARTIFACT_ABI` (roadmap H-ABI: line 55).
   The shared-emission seam is "the non-static functions declared in internal.h"; no header names it. Roadmap A-SEAM
   and H-HEADER already target the start-table half.
4. **Emitted text edited or read after rendering.** `src/gen/memfn_stamps.c:334-365` counts and `strstr`s
   `PCREC_TARGET_HEADERS_MARK` / `PCREC_HELD_HEADER_MARK` in the finished artifact and splices kit headers in;
   `pcrec_vm_stmt_respell` src/gen/vm_stmt.c:1085-1100 rewrites the rendered VM body by `strstr`; `vm_stmt.c:1165`
   finds `<name>_match_anchored(` by `strstr` to copy a function body; `fd_decisions` (parallel item 4). Each is
   documented at its site and refuses loudly on a miscount; none is a typed record. JUDGEMENT: VMREC made the VM
   body records, but the loop is not closed while a respell and a string-found copy remain.
5. **Ast payload read raw by every stage** (src/core/internal.h:1491; D70 union): acceptable for an AST; the exposure
   is the 27 hand-exhaustive walks (chain 5), not the field reads. `kset.c` is "the second hand-maintained exhaustive
   NKind walk ... paired only by -Wswitch" (src/facts/CLAUDE.md, helper).
6. **Selection read across the core/gen line by row name.** compound.c:211 `!strcmp(pcrec_cand_plain_selection(cx,
   CAND_SLOT_BOUND, CAND_ROUTE_ATTEMPT), "all")`: a core-tier admission reads a gen-tier row by its name string.

With a written contract and tests (contrast; these are the model):
- C1 the facts layer: `src/facts/facts.def` + `pf_enter`/ask accessors + epoch seals; docs/spec/facts_listing.md;
  tests/codegen/run_facts_checks.sh (include graph AND link symbols).
- C2 the kit seam: one public header memfn/include/memfn.h; D146/D147/D157; tests/memfn C4 arch_blind_check.py
  (class 9 = include graph, 71-row allowlist), C5 arm pins, C10 delegated sites, C15 symbol namespace, C17 site census;
  "a kit byte move is a pcrec abi event in the same commit" (memfn/CLAUDE.md). Weak spot: its output is text, then
  seam item 4 edits it.
- C3 entries/parts: `entry_rows[]` src/gen/entries.c:255, part_layout.c rows, tests/compound/check_entry_ranks.py.
- C4 the parse registry: src/parse/registry.c row tables (:534-1648), docs/spec/registry.md, tests/registry; the
  extension design's per-port, per-doorway DATA (extension_design.md R14 outcome) is the best-tabled area in the tree.
- C5 emitted ABI (docs/spec/match_api.md, the abi stamp, identity gate), limits (limits.def + limits.md), option axes
  (axes.def, one X-macro expanded in cli, compile, emit, memfn_sites and dump).

## WHERE THE NEXT FEATURES WILL LAND

Classes: (a) a row in an existing table; (b) a new arm in a chain; (c) no home today. Sites from the landing helper's
greps (scratch `landing.md`), spot-checked where marked.

**[COVER-CAP] stage 2** (cover_cap.md §11.1-11.2; built on lane/covs2b, unlanded per helper).
- C15 "statement-fits" conjunct: `cover_conj[]` src/gen/known.c:448: (a).
- The width limit: one `PCREC_LIMIT` row in src/core/limits.def + limits.md section + limits_check count: (a).
- `--window-search-width=N`: a new `strncmp` arm in cli_parse (chain 4): (b); `pcrec_options` (lib/pcrec.h:1732) has
  no slot for a per-limit override: (c), the design's own "carrier and its abi event".
- The size-cap fallback: the cover has no rung of its own ([COVER-SIZE-LADDER]): (c), and when it gets one, the
  roadmap's H-LADDER shape says a droppable row appends a rung, a FitAct, a verb, legal pairs, a term in
  COMPILE_MAX_ATTEMPTS and a driver case: six places (roadmap H-LADDER "Declared extension shape").

**Conditions as pattern pieces** (predicates_draft.md rev 23.2, NOT STABLE; [COND-FAMILY]).
- Syntax: a module row in src/parse/registry.c (a) plus a dispatch arm in `p_atom` (b); a condition grammar
  (programs, `when`, `&`/`!` over patterns and sets, labels): (c).
- A new AST kind (the draft: "a condition is its own kind, not a macro", rev 23.1 F9): a kindrow.def row (a) and
  ~26 files of hand `case A_*` arms (b), chain 5. A three-valued per-row test has no evaluator in either engine: (c).
  INFERRED: the nearest homes are the find-all iterator's entries (src/gen/entries.c `entry_rows[]`, emit_iter.c) if
  conditions filter hits, or the lookaround machinery (emit_vm.c `vm_cost_look` :3076) if they are evaluated in-match.
  Which one is a requirements question (the draft's own open items), and it is the single biggest architecture
  question in the coming list (JUDGEMENT).
- Labels / captured values: shares a namespace with mod_named_groups.c and the variables module ([VAR]): (c).

**[FLAG-DEMOTE]** (D195; map docs/design/flag_demote_map.md).
- The internal deny word (`xdeny` in Ctx plus a `pcrec_cx_has`): a new word beside the public flags word: (c) today,
  designed by the map §1.1.
- Readers: table-driven ones (cand_rows[].deny, `DENY_FLAG[]` clskit.c:707ff, `deny_map[]` memfn_sites.c:42-62,
  `pf_deny[]` facts.c:161): (a). Direct readers: `grep -rn "pcrec_opt_has\|pcrec_flags_has" src | wc -l` = 80 (compile.c
  21, emit_dfa.c 16, emit_vm.c 12, select_engine.c 6): each a mechanical swap (b).
- Spelling: axes.def rows (a); `cli_axis_apply` already loops axes.def (a); `--harness=no-<axis>`: (b).
- Compound parts do not inherit the harness word (compound.c:58-76): (c).
- The force/deny refusals (chain 3) must be re-expressed: (b), five arms in select_engine.c:1079-1107 alone.

**[S4] lookaround set** ([REQ-LOOKAROUND], [CTX-FACTS-NEG], [LOOK-LOCATE]; plan.md:107, 300, 540; design
docs/design/span_arms.md).
- Required runs seeing through positive lookaround: `case A_LOOK:` in src/facts/req.c:1204 (rr_cat): (b), in the same
  pass that [RUN-POS-SET], [REQ-EMPTYCAT], [REQ-PAST-LAST] also edit (INFERRED serialization risk).
- LOOK-LOCATE: a new LOCATE row in `cand_rows[]` (a), but a signed (negative) offset has no field in the row schema:
  (c) INFERRED; and its recover/finish act lands in chain 1 (b).
- CTX-FACTS-NEG: per-offset context facts at negative offsets; the producer was the deleted span slice (archhist 17):
  (c); the row itself says no build before a measured need.
- Other A_LOOK readers that must agree: src/facts/startanch.c:162, startset.c:141, endwin.c:174/326, widths.c,
  select_engine.c:286: each (b).

**[VLOOKBEHIND] stage 2** (vlookbehind.md §6.2; stage 1 landed c44649a69).
- "Stage 2 adds NO emission row"; width through group references = columns of callgraph.c's per-target fixpoint
  table (`pcrec_callgraph_build`): (a) by the manager's F1 ruling.
- Acceptance/refusal: src/parse/mod_lookaround.c (`case` ~:240) and postresolve.c: (b); two limits.def rows (a).
- It is the fourth "group g's width" mechanism (parallel item 1), and mod_lookaround.c already calls the opt-tier
  width functions from parse (seam item 2): the feature lands on the exact spot a measure library would own.

**Stream manifesto / roadmap** (docs/design/stream/; plan [STREAM] not-started; ratchet baseline 24).
- Every area step is a move to a table at a named site (roadmap.md §1 table, lines 88-109): A-SEAM (hand enum and row
  types out of emit_dfa.c), A-POSDOM (one rule table over three next-start loops), A-REV (one record for every DFA
  walk), A-REC (one record vocabulary; the DFA emitter still prints directly: (c) for the DFA side), hubs H-LADDER,
  H-FLAGS, H-SITES, H-ABI, H-COUNTS, H-HEADER, each "name the owner, declare the append shape".
- JUDGEMENT: the roadmap's §3 hub evidence (three replayed changes, roadmap.md:629-631) is already an architecture
  note in all but name: for each change it lists the rows added (a) and the hubs touched without a declared shape
  (c). It is the strongest worked precedent for the A1/A6 retro test.

**Started rows touching src/** (`grep -nE "STATE:started" docs/dev/plan.md`, helper).
- [UCP] (plan.md:104): char-step `\b` as a ctxfn.def row: (a).
- [VMREC] (plan.md:206): migrating ad-hoc prints to record kinds in emit_vm.c / vm_stmt.c: (b) -> (a) in progress.
- [RUN-POS-SET] / [REQ-EMPTYCAT] / [REQ-PAST-LAST] (plan.md:234, 254, 285): all arms in req.c's rr_cat family (b).
- [MEASURE-SET] (plan.md:158): data rows in measure_store (a).
- [FINDALL-NEXT] (plan.md:177): entries.c / emit_iter.c rows (a), waiting on kit kinds.

**Unit costs** (helper greps, spot-checked):
- A new AST kind: kindrow.def row (a) + 27 files with `case A_*` labels (b) + the NFA lowering (nfa.c) + VM emission
  (emit_vm.c ~14 case sites). emit_dfa.c has 0 `case A_` sites (it reads the NFA).
- A new public deny/force bit: lib/pcrec.h `PCREC_BIT(n)` (6 bits free per [IFACE-PUSH]) + one axes.def row (a, and
  CLI, listing and axes run derive from it) + hand-listed sites: the rx_info.flags KEPT set (`grep -n "uint64_t kept"
  src/gen/emit_dfa.c`), docs/spec tuning.md / cli.md / match_api.md, tests/ci/measured_axes.tsv and the cloud shard
  table, plus each reader: roughly 8-12 sites per flag (INFERRED from `grep -rl PCREC_NO_POSSESSIFY`).
- A new valued option: a cli_parse arm (b) + MODE_ADMITS row (a) + a `pcrec_options` field + spec + the CLI option
  census: ~8 sites (`grep -rl "backtrack-frames"` = 16 files, helper).

## ARCHITECTURAL OPTIONS WE DO NOT USE

Each: what it is; where here; what it replaces or deletes; cost; trigger (D77: none proposed ahead of its trigger);
which past refactor it would have avoided. Verdicts are JUDGEMENT.

1. **Rows carry their action (dispatch through the row, not on its answer).** A table row holds function pointers or
   an action record for every slot it fills (emit, verify, describe), so emitters call `row->recover.emit(...)`
   instead of switching on the row's enum. Where: cand_rows[] RECOVER/FINISH slots and their four re-dispatching
   emitters plus the 26 route tests (chain 1); the pf rows already do it (`emit_block`/`emit_define`). Deletes: the
   CRA_* switches in emit_unanchored/emit_attempt/emit_rev_end and the act-keyed prologue prose. Cost: a no-mover
   remodel inside emit_dfa.c (M), byte-identity gate, sabotage re-aims at the moved sites; no abi. Trigger: the next
   new recover/finish act (A-REV's reverse walk or LOOK-LOCATE). Would have avoided: START-TABLE's second half before
   it accreted. **Worth it here**, riding A-SEAM/A-REV.
2. **A declared request-validity table.** Rows of "this combination of request bits and pattern facts is refused",
   each with a name, predicate and message, walked once, printable by a `--list-*` surface. Where:
   select_engine.c:1079-1107, compile.c:2046ff, cli MODE_ADMITS. Deletes: the scattered `if (force_on && ...)` arms.
   Cost: S, no abi, diagnostics wording unchanged (D26). Trigger: FLAG-DEMOTE (it touches every force/deny pair) or
   the next force flag. Would have avoided: nothing in the history yet; it is the family the "notice siblings" rule
   would flag at its third member (it has five). **Worth it here**, folded into FLAG-DEMOTE.
3. **A node-grain measure library below parse** (one attribute module: min/max width, nullable, TEXT first set, with
   saturating arithmetic; kind defaults read from kindrow.def). Where: src/opt/mrl.c moves down (into core base or a
   new `measure/` between enc and parse); lm_maxw, `pcrec_vm_fmul`/`fadd`, `vm_general_min_width`, `cc_width` become
   callers. Deletes: two or three width walks, the sat twin, the parse->opt and facts->opt back-edges
   (src/facts/CLAUDE.md:7's known wrong-way edge). Cost: M; answer-identity gate; lm_maxw's unsaturated multiply may
   move bytes on huge repeat counts (needs a check before claiming no-mover). Trigger: VLOOKBEHIND stage 2 (it adds a
   fourth group-width mechanism; facts/CLAUDE.md's own trigger is "a defect traced to it"). Would have avoided: none
   directly; it is the shape D70/D62 were about (archhist 1, 6). **Worth it here**, at VLOOKBEHIND stage 2's
   architecture note.
4. **Kind defaults as a table column, walks as one visitor with per-pass overrides.** Add the LEAF/DESCEND (and
   zero-width) split to kindrow.def and give AST passes a generic walk that consults it, so a pass writes only the
   kinds it treats specially. Where: the 27 files of chain 5 (atomic.c 115 case labels, possessify.c 84, ...). Deletes:
   repeated leaf lists; turns a new kind from ~26 (b) edits into a row plus the passes that really differ. Cost: L
   if done wholesale; S per pass if done as each pass is next touched. Risk: -Wswitch exhaustiveness is today's safety
   net and a default arm loses it; the kindrow.def PATH column exists because a defaulted answer was a miscompile.
   Trigger: COND-FAMILY's new kind, or A_BOL/A_EOL -> A_CTX. Would have avoided: part of D70 (archhist 1).
   **Worth it per pass, not wholesale**: keep exhaustive switches where the answer is semantic, use the column where
   the arm is a pure restatement of TEXT/PATH.
5. **Phase-typed stage outputs instead of the Job blackboard.** Each stage returns a const result record (selection,
   emit facts, sizes) with a declared writer, and later stages receive it by value or const pointer; `Job` stops
   being written by emitters. Where: internal.h Job/Ctx; the 14 emitter-written Job fields; `Ctx.*_dropped`. Deletes:
   roadmap R14 (H-FLAGS); makes the owner's handoff-architecture seams (memory: handoff architecture, 2026-11-01)
   real at the compile-stage level. Cost: L, internal only (no abi), identity gate; the roadmap's own interim step
   (name each field's writer and reader) is S. Trigger: the next feature that adds an emitter-to-driver flag (the
   roadmap's §3 shows every replayed change did). Would have avoided: FLAG-ACCESS and D62 were one field family each.
   **Worth it in the roadmap's two steps; the S step now, the L step only as areas migrate.**
6. **The artifact as a structured document, rendered once.** Sections, marks and stamps as typed parts in a record
   list (the VM's records extended to the whole artifact), with the kit returning parts rather than text that pcrec
   then splices; decisions listed from the Job, not parsed back from `#define`s. Where: memfn_stamps.c:334-365,
   vm_stmt.c:1085/1165, facts_dump.c:138. Deletes: three string-search protocols and their internal-error refusals.
   Cost: the facts_dump fix is S (read Job); the rest is A-REC (roadmap), M per step, and a kit seam change (a kit
   abi event, D146). Trigger: the next post-render rewrite or the next reader of a stamp. Would have avoided: VMREC
   (archhist 13: "printing IS recording"). **Worth it as A-REC already plans; the facts_dump part is cheap now.**
7. **A declared option table for the CLI's non-axis options** (name, value kind, `pcrec_options` field or CLI state
   field, MODE mask, spec section), the way axes.def drives the axes. Where: cli/main.c:1278ff (82 arms), 2904ff.
   Deletes: the hand arms; the CLI option census test and cli.md listing could read the table. Cost: M, no abi,
   CLI behaviour identical. Trigger: [IFACE-PUSH] (the owner's one interface push, memory iface-push-later), which
   reshapes options anyway. Would have avoided: REVW W4's cli_parse wave. **Worth it, at IFACE-PUSH, not before.**
8. **Split the shared artifact emitter out of emit_dfa.c.** A gen-tier "artifact" unit (prologue, entries, rx_info,
   stamps, ABI constant, VM start code) with its own header; emit_dfa.c becomes the DFA engine only. Where: emit_dfa.c
   :55, :8162-8358, :16357 and friends. Deletes: nothing logically; makes the seam visible (seam item 3). Cost: a large
   pure move (git blame churn, sabotage anchors re-homed: archhist 5 and the D70 lane both paid this), no bytes.
   Trigger: A-SEAM/H-HEADER (the roadmap already moves the start table's types first). **Worth it only riding A-SEAM;
   a standalone move is churn.**
9. **A call-level layering gate.** An `nm`-based census of defined/undefined symbols per object joined to the layer
   order, as a ratchet (the count may fall, never rise), in make test. Where: the whole tree; facts/ already has
   it (run_facts_checks.sh link checks). Deletes: the gap where `include_backedges.tsv` reads clean while ~30 call
   back-edges exist (src/CLAUDE.md "What the include graph cannot see"). Cost: S; but it is harness, and the owner
   rules harness minimal (architecture.md "Product first"). Trigger: a defect traced to a wrong-way call. **Not worth
   it now**: the known edges are written down by name; a ratchet buys little until one bites.
10. **A general term-rewriting / nanopass framework for AST passes** (rewrite rules over a generic tree, one driver).
    Where: possessify.c, atomic.c, altnf.c, derive.c, revdet.c. Would replace hand walks. **Not worth it here**: each
    pass is a proof-carrying analysis whose soundness argument is local to its code (kindrow.def's PATH column records
    a miscompile from a shared answer); a generic engine moves every pass at once under identity gates with no
    measured need. Option 4 gets the cheap part.
11. **Link-time module registration for parser modules** (each mod_*.c registers itself via a section or constructor,
    no central list). **Not worth it here**: the registry is already a declared table with a spec and tests
    (seam C4), and order matters in it (per-port, per-doorway data, extension_design.md R14 outcome); the real
    duplication is helper code (parallel item 7), fixed by a shared module-helper header, not by registration.

## WHAT THE GUIDE DOES NOT SAY

Rules the history and the tree suggest that docs/dev/guide/architecture.md lacks (one sentence each):
- A table's answer is acted on through the row (its action or hook), never by re-testing the row's enum or name in
  each consumer (chain 1, chain 2, compound.c:211's `strcmp(..., "all")`).
- Refusals of a request are a decision family like any selection: declared rows, named, listable (chain 3).
- Layering is judged at the call level, not only at the include level; a function many lower layers call lives at
  their level (seam item 2; src/CLAUDE.md already measured the gap).
- A decision is read from the record that made it, never parsed back out of emitted text (seam item 4).
- A new AST kind's cost is stated in its architecture note: the kindrow.def row and every hand-exhaustive walk it
  forces (chain 5, 27 files).
- A stage-to-stage field names its one writer and its readers; an emitter does not write driver state (roadmap
  H-FLAGS states this as an interim shape; the guide does not).
- A second walk answering a question an existing walk answers is a parallel mechanism even when it is small and
  local (lm_maxw, lmwalk.c:80, born 2026-10-29 beside mrl.c).
- The "Notice siblings" trigger should count call sites of a question, not only tables (the 26 route tests and ~10
  engine tests are one family without any table of their own).

Rules the guide has that the tree visibly does not follow:
- "The house idiom is `dfa_pfs[]` + `DFA_SELECT`" (architecture.md, "Decisions are declared tables"): `dfa_pfs[]` was
  deleted into cand_rows[] (emit_dfa.c:10080 comment), so the guide cites a table that no longer exists.
- "observable (listable, with every verdict and the winner printable)": the prefilter refusals
  (select_engine.c:1079-1107) and the compile_driver validity checks have no listing.
- "One table per slot ... keying rules on a label instead of on facts drops rows silently": compound.c:211 keys an
  admission on the selected row's name string `"all"`.
- "Build the general form; no parallel mechanisms": lm_maxw (lmwalk.c:80-105) re-spells the width walk of mrl.c and
  the TEXT column of kindrow.def, unsaturated (lmwalk.c:94).
- Not the guide but its neighbour: src/CLAUDE.md says `include_backedges.tsv` reads 0 rows; at cd781a306 it reads 2
  (src/core/findings.c:52, src/core/internal.h:3429), and the committed tools/review/out/ census (935 functions) is
  a third of today's 2,657.
