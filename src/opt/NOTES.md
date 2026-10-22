# NOTES — history, lessons and rationale for this directory

Not auto-injected. CLAUDE.md is the orientation guide; text moved here verbatim from it (2026-10-22, size limit) lives below.

## Per-topic entries (cited by tests/mech sabotage rows)

- [DD-14 wave G] splice linkage: `callgraph.c` sets `CALL_SPLICE`; atomic.c gains
  `pcrec_has_linked_call` and `pcrec_has_live_capture`; select_engine reads both
  (`forces_captures`, prefilter predicate, `first_dfa_excluding` exempts
  `CALL_SPLICE` before the SR-8 row test).
- [M4.6f] the prefilter force pair, applied in select_engine.c (see its entry above;
  cited by S64, D46 do-or-die; docs/spec/tuning.md §2.17).
- [OPT-4.1] nullability predicate: ONE derivation (E1 `nullable`, `src/facts/widths.c`
  over `pcrec_nullable`), THREE readers: select_engine's `fit.prefilter` clause (a
  collapse rung's rescue is DECLINED for a nullable language), compile.c's build gate
  (`-fprefilter-collapse`), the `--emit-ir` `; prefilter` line. `-fprefilter` overrides
  on the SIZE rung, makes the [SEL-1] rung ineligible (compile REFUSES);
  `-fprefilter-collapse` overrides on neither. Contract: docs/spec/tuning.md §2.17.
- [OPT-4.2] the decline generalizes off the rung: ONE predicate (`lang_nullable_declinable`
  = `empty_admits` && !has_bref && !has_call && !force_on; now T2 rows 3-5),
  TWO scopes: `prefilter_declined_nullable` (rung offered, `collapse_reason != CR_NONE`)
  and `_default` (`CR_NONE`, `would_prefilter`, `!cx->dfa_disabled`); mutually exclusive;
  own value `ESEL_DECLINED_NULLABLE_DEFAULT`. Contract docs/spec/tuning.md §2.17 and
  match_api.md §6.3. Tests tests/resource `(a|b){0,30000}`, tests/prefilter `(a)*`;
  sabotage S216, S612.
- [K53-SELRETRY] `ESEL_SIZE_CAP_RETRY` covers BOTH retry rungs (prefilter collapse; drop
  the optional anchored machine, `cx->size_drop_rung != SDR_NONE`); mutually exclusive by
  engine; NO `fit.prefilter` conjunct on the DFA half; which rung is read from axis
  stamps. Sabotage S237/S238.
- [OPT-PRECHECK-ADMIT] whether a pre-check is EMITTED is NOT this directory's question:
  `src/gen/emit_dfa.c`'s `req_admit` decides (docs/spec/tuning.md §2.29);
  `<PREFIX>_REQ_BYTE`/`_REQ_RUN` = what the pass FOUND, `_REQ_WHY` = whether used
  (readers: tests/codegen/run_prechecks.sh §3 and §5).
- [DD-11.5] parts 2 and P2e: `A_BOL`/`A_END` are no longer kinds; start/end pins are
  A_CTX rows read via `pcrec_ctx_class(n)` with no `default:` (derive.c `q_rewrite`,
  `qp_walk`; possessify.c `first_of`, `ps_node`); `\z` is the one nullable A_CTX.

## Files entry: reqbyte.c (DELETED) and its binding rules

- reqbyte.c — DELETED ([FINDINGS] B1 = [PATFACTS] 3.1, D126): walk -> `src/facts/req.c`,
  picks -> `src/core/findings.c` (`pcrec_find_set_pick`, `pcrec_find_run_scan_index`,
  `pcrec_find_run_window_start`), compositions `pcrec_req_window`/`pcrec_req_pick`
  -> src/facts/req.c. Its rules, still binding on those homes: the analysis produces
  a SET and the emitter picks one member (ALT intersects); the pick is the ARGMIN of
  the byte-rate prior (rightmost tiebreak) and the prior is read ONLY under `byte`
  (elsewhere rightmost; [OPT-FREQPICK]/[OPT-REQRUN-ENC] abi 37->38: `!bytekey`
  fallback is RIGHTMOST); [OPT-REQPOS] 2b necessary literal RUN (declines: multi-member
  class, MIN-0 repeat, alternation keeps common prefix/suffix only; truncated to the
  lowest-prior window of `PCREC_MAX_REQ_RUN_EMIT`); a LOOKAROUND body is not descended;
  the empty set is the safe answer; [K65] `Job.req_set`, [K66] `ReqRun.whole/whole_len/at`.
  Tests tests/codegen/run_prechecks.sh §3, §3.6, §3.7, §4, §4.9; sabotage S265-S268, S294.

## Files entry: scanedge.c

- scanedge.c — [OPT-5] DFA SCAN EDGE: after `pcrec_minimize_dfa`, DELETES scan-shaped
  state chains (criterion is a property of the transition table, not of `{m,n}`);
  EIGHT preconditions, each a decline ((6) view-target heads, (7) smaller source index,
  (8) no seed-family head on a RESEEDING prefilter, taken as a PARAMETER from
  `pcrec_dfa_scan_state_written`); [OPT-EDGE] STEP 1 renumbers heads to the top rows;
  STEP 1.1 narrowed (8); [OPT-VEDGE] relaxes (3)/(6) under `-fno-view-edge`
  (`PCREC_NO_VIEW_EDGE`, bit 42; `end_is_exit` parameter); exports
  `pcrec_state_view_invariant` (STEP 2). Gate `-fno-scan-edge` (`PCREC_NO_SCAN_EDGE`),
  docs/spec/tuning.md §2.18. Tests: counterk/classes/bounded_repeats/possessify/k18_*,
  tests/codegen/run_scan_edge_census.sh, tests/assertions/view_edge.rxt; sabotage
  S213, S214, S440.

## Files entry: select_engine.c

- select_engine.c — per-pattern ENGINE selection ([M4.5b], engine_m4.md §5.1): the
  analysis table run once. `forces_registry` (SR-8, D67; `Ast.reg`/`Ast.reg_at`
  stamped by `pcrec_ast_stamp`), `forces_captures` (request-derived; `node_derived`
  bit tells the `--engine=dfa` refusals apart), `forces_dfa_overflow` ([SEL-1], fed
  back by compile.c's one-shot retry via `Ctx.dfa_disabled`). Owns the `--engine`
  override refusals (before machine construction) and the prefilter refusals:
  backrefs ([M6.5.2]), calls ([DD-14]), `dfa_disabled`; [M4.6f] the PREFILTER FORCE
  PAIR (`-fprefilter`/`-fno-prefilter`, both refuse together; `-fprefilter` refuses
  when `fit.chosen != ENGM_VM`; D46; tests/prefilter/). Drives possessify.c on the
  CHOSEN engine (`run_possessify`). T2 (`pf_admits[]`, ten first-match rows over
  `PfAdmitSel`) is the prefilter admission and `fit_attrib_walk` (`esel_of`) the
  `ENGINE_SEL` attribution ([DEC-FALLBACK] B2-B7, dec_fallback.md §1.4/§1.7); rows ask
  `nullable`/`empty_admits` only where the old derivation did. Tests tests/vm/
  run_vm_tests.sh §3b, tests/prefilter/, tests/registry/registry_check.c tripwire.

## Standing rules: failure memory, scan/view-edge gates, verdict surfaces

- Failure memory: `minimize.c`'s local tables are the only compile-path
  allocations the Job does not own: free by hand before `pcrec_ctx_nomem`. A new
  input read in `src/ir/dfa.c` or dfamemo.c MUST join the dfamemo key.
- A `Ctx`-less walker (`pcrec_minw`/`pcrec_maxw`/predicates) cannot see a memo
  except via node fields; pcrec_minw is legitimately called before the graph
  exists (possessify).
- `-fno-scan-edge`/`-fno-view-edge` gate the PASS itself (an emitter filter cannot
  put back deleted states); emit_dfa.c's axes carry the same bit (one bit, two
  readers). scanedge: the emitter CHECKS the head layout (`dfa_form_derive` fails
  loudly if a head is not at `n - nheads + k`); heads are the machine's TOP rows
  in their existing relative order (precondition 7 relies on that).
- `$`-follow/multiline facts are read off the NODE (A_CTX rows), never from
  `cx->mods` at verdict time ((?m) is scoped; D47.5 addendum, assertions_design.md §8).
- Verdict surfaces are artifact stamps, not prose: `ENGINE_SEL` values are a
  closed set (K35); give a distinct population a distinct value
  (`ESEL_DECLINED_NULLABLE_DEFAULT`), keep placement argument in internal.h.

## Files entry: possessify.c

- possessify.c — [ENG-BREP] POSSESSIFICATION (eng_brep_design.md §2, D47.1): marks
  `A_REP` needing no resume frames; monotone; returns newly-marked count. Verdict is
  FIRST/FOLLOW disjoint + non-nullable + unique iteration (U1)/(U2) + lazy-only
  conjunct (every conjunct is a paid refutation: read the header). `pcrec_poss_survey`
  is the SAME verdict as a query. `A_ATOMIC` is transparent in `first_of`/`gk_build`,
  NOT in `pss_walk` (self-contained, empty follow). `\G` takes `\A`'s (downward-closed)
  decline arm; `\K` is transparent (epsilon). [K93] call targets carry a JOINED
  `CallCtx`; [ART-POSS-ARMS] arms A (A_CTX gates; `PCont`/`PSum`, R-5 equality check)
  and B (`A_BREF` FIRST via `text_first`); `Ctx.poss_arms` stamp
  `<PREFIX>_VM_POSS_ARMS`; deny bits `-fno-poss-ctx-follow`/`-fno-poss-bref-first`;
  [DD-11.5] `pcrec_poss_ctx_admits` never narrows a row reading an absent side.
  Exports `pcrec_uniq_scratch`/`pcrec_uniq_iteration`. Tests tests/possessify/;
  sabotage S45-S49, S84, S560-S565, S586-S588, S601-S604, S612.
