# src/facts/ — the pattern-facts ANALYSIS LAYER ([PATFACTS], D120/D126)

ONE organized record of what a pattern HAS (kind mask, nullability, necessary bytes/run, start anchor/set, end window, k-set walk, run pin, span/width/landing facts), computed once per compile attempt behind one accessor per fact, sealed by epoch, with fact-level `-fno-` denies applied inside the accessor. Design: `docs/design/patfacts/design.md` (rev 2, D126; §9 migration order, one relocation per commit under a zero-movers A/B emit-diff gate).

## Standing rules

- Layer order: `lib -> core(base) -> enc -> parse -> ir -> facts -> opt -> gen -> driver -> dump -> cli`. A derivation depends on the sealed IR, node-grain pure functions, OTHER facts only through accessors along `facts.def`'s DEPENDS-ON edges, and the encoding DESCRIPTOR as a declared input (carve-out (d)), never `cx->opt->encoding`. DECISIONS (G1 domination, offset-k selection, `req_admit`, `DFA_SELECT`) stay in their passes (carve-out (c)). Known wrong-way edge: `facts -> opt` call-level back-edge (`pcrec_minw`/`pcrec_cwmax` in `src/opt/mrl.c`, `atomic.c` predicates); move them down only on a defect traced to it (design §4.2.1, §10).
- Every accessor does four steps via `pf_enter` + derive (epoch guard, memo, deny, derive); no accessor may skip one. A derivation reads other facts only through `pf_ask`. The `used` bit is set by a PASS asking, never by a derived fact's own derivation; NON-PASS reads (`pcrec_fact_req_set_stated`, `_req_whole_run_stated`, `_req_run_stated`, `_req_byte_stated`) must not set it (Q-WR-12).
- Adding/changing a fact = a `facts.def` row (`PF_FACT(ID, name, epoch, kind, deny, owner, depends)`, one row per line); accessor ids, deny application, epoch guard and `--emit-facts` row order are generated from it. Each fact has ONE renderer (`pcrec_fact_render`, no-default switch) used by `pcrec_fact_stamp` and `--emit-facts` (Q9). A derivation stores the `why` it reports (decline reason, rate rule) with the value, never inferred.
- `facts_derive.h` is FACTS-PRIVATE: only this directory and the files named in `facts.def`'s OWNER column (read as plain text) may include it; `tests/codegen/run_facts_checks.sh` checks the include graph AND link symbols (S296/S297).
- Seals: E1 is EAGER (`pcrec_facts_seal_e1` right after `pcrec_callgraph_build`, forces kind mask and nullability because `pcrec_lower_enc` rewrites the tree in place); `pcrec_facts_seal_e2` re-derives on the LOWERED tree and refuses the compile if either moved (`pf_check_e1`; `run_facts_checks.sh` [facts-e1], S302/S303). E3 seals PER BRANCH, inside `compile_driver`'s ENG_UNANCH arm right after `pcrec_nfa_wrap_unanchored`; an unsealed E3 fact answers `absent` with `decline:attempt-unwrapped-nfa` or `decline:no-forward-nfa` ([facts-e3], S306/S307).
- `--emit-facts` FORCE LOOP (`pcrec_facts_force_all`/`_failed`) runs after the artifact is complete; a failing forced ask becomes that fact's `absent` row, not a refused compile (Q10).
- Every reader of the run pin owes the KIND GATE (`src/gen/emit_dfa.c` reads it only through `us_run_pin`).
- `kset.c`'s `NKind` switch has NO `default:` (a new consuming kind treated as an assertion is the unsound direction); it is the second hand-maintained exhaustive `NKind` walk (first: `src/ir/dfa.c` closure), paired only by `-Wswitch`. `startset.c`/`pcrec_start_set`: spines iterative, no `default:`, `Ast.u.call.body` not followed.
- `endwin.c` can LOSE a match if wrong (it moves the search start): keep its four structural declines (unbounded `pcrec_cwmax`; multi-byte encoding via `PcrecEnc.start_cls != NULL`; any `\G`; multiline `$`/D62 ctl 3) and its answer-level net (`tests/assertions/end_window.rxt`).
- `pcrec_start_anchor`: `PCREC_SANCH_BOT` implies the DFA's `anchored`, the converse is NOT asserted (`emit_attempt` confirms, does not derive a second answer). The `req.c` walk reads no prior and no option (core fact); the `req_run`/`req_byte` compositions live here (a `src/core/` file including `facts_derive.h` would point the graph the wrong way); they ask the byte-rate accessor FIRST (findings design §6.4 rule 1) and `req_rate_why` asks `pcrec_find_byte_rate_answers`, never the consumption memo (structural_check.py S4). `rn_put` refuses a non-canonical pair as an internal error; `PCREC_MAX_REQ_RUN_POS_SET`=2 (1 under `-fno-req-run-fold`) is handed in by `facts.c`.
- Span slice (`pcrec_span_walk`, KIT-VERIFY U1 Z2): `KsetWalk` stays UNCHANGED; the trace build holds the slice inside that hull; declines a superset (`Nfa.erased`) or mark-distance machine; bounded by `PCREC_PREFIX_K_MAX` and `PCREC_SPAN_WALK_SUBSETS` (limits.def).
- DD-11.5: multiline anchors are A_CTX nodes (the `Ast.u.anch.multiline` branches are deleted); `sa_walk`, `ew_walk_marked`, `em_set` switch on `pcrec_ctx_class(n)` with no `default:`.
- What no check catches: a HAND RE-SPELLING (a consumer writing its own walk, calling no derivation, including no private header). Defence: helpers are `static` here and `tools/review/clone_candidates.py` at review time; a reviewer looks for it (design §4.2.3).
- Sabotage anchors for walks here (S206/S207 widths, S263 startanch, S264 endwin, S268/S446/S451/S453/S456/S465/S466/S474/S805-S807 req, S280 pin, S501/S502 startset, S611/S613 empty masks): keep them reaching their site when editing.
- Maintenance: update this file when a file is added, moved in or removed.

## Files

- facts.def — THE TABLE of facts (also the OWNER-file list).
- facts.h — consumer header: value types (`ReqRun`, `ReqSet`, `PCREC_SANCH_*`, `MkLang`), `PatFacts` (`Job.pf`), seals, accessors, renderers; no derivation; included by `core/internal.h`.
- facts.c — the record: accessors, memo/deny/epoch, seals, `used` bit, renderers, force loop.
- facts_derive.h — facts-private derivation declarations (`RbSet`, `RbRun`, `rb_has`).
- kinds.c — E1 kind mask `pcrec_pattern_kinds` (`PF_KIND_*` bits; `pcrec_has_call` has no bit, D77).
- widths.c — E1 root nullability `pcrec_pattern_nullable` (via `pcrec_nullable`, K69) and the [NULLABLE-ANCH] empty-path masks `pcrec_pattern_empty_masks` / fact `empty_admits` (checked by `pf_check_e1`; reader: `select_engine.c` prefilter admission).
- startanch.c — [OPT-ANCHOR-VM] START ANCHOR `pcrec_start_anchor` (BOT/GSTART/NONE), read by both emitters (test `run_prechecks.sh` §1).
- startset.c — [START-SET] START SET `pcrec_start_set` (superset, lowered tree; D148, `docs/design/startset.md`; `tests/startset/`).
- endwin.c — [OPT-ENDWIN] END WINDOW `pcrec_end_window`, plus the split-out `end_pin` fact `pcrec_end_pin` ([OPT-REVEND] L1; `end_window` depends on it) (`run_prechecks.sh` §2).
- req.c — [OPT-REQBYTE]/[OPT-REQPOS] necessary set + literal run walk (`pcrec_req_walk`), derived `req_run`/`req_byte`, `req_run_maxoff` ([K82]), `req_set_maxoff`/`req_landmark_maxoff` ([REQ-HANDOFF-L1]), position-cube runs ([OPT-LITSCAN] S4 C3, `litscan_s4.md` §2.3).
- kset.c — [OPT-K] K-SET WALK `pcrec_kset_walk`, RUN PIN `pcrec_run_pin` (exact stretch, C3), span slice `pcrec_span_walk`, the [START-LANDING] SL1 shared frontier iterator (`wclose`, `wstart`/`wadvance`), `pcrec_width_walk` (fact `width`) and `pcrec_land_char` (fact `land_char`; readers: RECOVER rows `end-minus-width`, `landing`).

## Pointers

`docs/design/patfacts/design.md`, `findings/design.md`, `litscan_s1.md`, `litscan_s4.md`, `start_landing.md`, `startset.md`, `kit_proof.md` §5.2, `ctx_span.md`; D77, D119, D120, D126, D148; `tests/codegen/run_facts_checks.sh`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/src__facts.md
