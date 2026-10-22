# src/opt — algorithmic optimization passes

Transformations pcrec must do because gcc cannot (APPROACH §5): they change the
algorithm, not the instruction selection. Passes run between DFA construction
(src/ir) and emission (src/gen). Several files here are ANALYSES (no mutation)
that live here because an error in them is silent (wrong answers, no warning).

## Standing rules

- Maintenance: update this file when passes are added/removed; every directory
  CLAUDE.md lists its files.
- A TRANSFORMATION pass takes (Ctx *, Dfa *) or (Ctx *, Nfa *), mutates in place
  and MUST be behavior-preserving; every pass needs corpus coverage that would
  catch a semantic change (the full suite runs against post-pass output).
  Scan-avoidance analyses that only inform codegen (prefilters, skip states) live
  in the emitter; move one here only if it grows its own IR transformation.
- AST-level passes (altcls.c, `pcrec_discharge_atomic`) take (Ctx *, Ast *) and
  RETURN the possibly-new root, which the caller MUST PUBLISH. Still
  behavior-preserving, corpus-covered, deny-only + D46-stamped.
- Every pass is gated by a D46 deny bit (`-fno-*`) and observable by a stamp.
  A new selection axis owes a D46 stamp+force pair and a sabotage-matrix row.
- Soundness direction: every decision is in the SOUND direction; anything
  unmodellable DECLINES (declining is always safe). `pcrec_minw` rounds DOWN
  (under-estimate safe); `pcrec_maxw`/`pcrec_cwmax` round UP (under-estimate is a
  silent miscompile, false match on negative lookbehind).
- Switches over `AKind` have NO `default:` arm (a new node kind must be a compile
  error under `make strict`'s -Wswitch). Seven such switches live in atomic.c;
  each new whole-tree predicate lands there.
- Walks of `A_CAT`/`A_ALT` spines and `A_CAP` chains are ITERATIVE (D10/DD-10/K20);
  only paren nesting recurses (Theta(d)).
- A WHOLE-TREE predicate MUST NOT follow `Ast.u.call.body` (the AST's first back
  edge; non-terminating on `(a(?1))`); the callee is visited at its own lexical
  position. Six of atomic.c's seven switches DECLINE `A_CALL`; `pcrec_bref_mark`
  marks `u.call.target` without descent.
- Memos live ON THE NODE or in a Ctx-owned struct, never in a file-static
  ([TS-3] forbids mutable globals). The arena's ZERO must be the sound answer
  (`u.call.minw` 0, `nonnullable` inverted, `maxw_known` false -> UNBOUNDED).
- ONE derivation per fact (memory `pcrec-general-mechanisms-not-special-cases`):
  possessify's unique-iteration predicate is exported to revdet.c; saturating
  arithmetic is `pcrec_sat_add`/`pcrec_sat_mul` in mrl.c (ceiling as parameter);
  `pcrec_nullable` is mrl.c's; `pcrec_state_view_invariant` (scanedge.c) is read by
  emit_dfa.c's axis J. Do not add a second spelling.
- Never make an optimisation flag change which ENGINE a pattern gets: the free
  atomic discharge is NOT gated by `-fno-possessify`.
- Pass order is part of the design (reviewable fact, asserted by
  `tests/codegen/run_cpset_structure.sh`): altcls first after parse;
  `pcrec_discharge_atomic` right after altcls (hoisted out of select_engine,
  [DD-14] wave G); `pcrec_callgraph_build` AFTER every node-REBUILDING pass
  (altcls rebuilds `A_CAP`; the graph's `.body` is the only writer, here only) and
  BEFORE engine selection; `pcrec_postresolve` right after the graph;
  `pcrec_lower_enc` AFTER postresolve and BEFORE `pcrec_build_nfa`/`pcrec_emit_vm`,
  splicing IN PLACE (never reallocating a group root; `cap_sig` checks it).
- Passes run once; select_engine's rewrite/`discharge` socket is deleted
  ([TOUR-5]); building one needs a first customer (docs/dev/plan.md [ENG-CUT]).
- Rewrites that change tree shape must not introduce capturing groups (altcls
  allocates only A_CLASS/A_CAT/A_ALT/A_EMPTY).
- Changing emitted text from any pass = abi bump + identity-gate re-pin in the
  same change (D76/D94); update `docs/spec/` (tuning.md, match_api.md) for any
  caller-visible change (D80).
- Further standing rules (failure memory, scan-edge/view-edge gates, `$`-follow facts read off the node, verdict surfaces as stamps): moved verbatim to NOTES.md.
- Do not carry a pass's soundness argument here: it lives in the file's own header
  (read it before touching possessify's verdict ladder, revdet's uniqueness checks,
  scanedge's eight preconditions, altcls's ladder boundary).

## Files

- altcls.c — [OPT-ALTCLS] FIRST pass: stage 1 merges adjacent bare-class alt
  branches (`b|c` -> `[bc]`); stage 2 prefix-factors adjacent literal-first-byte
  branches (`frank|fred` -> `fr(?:ank|ed)`), iterative loop + depth cap
  `PCREC_MAX_ALTCLS_FACTOR_DEPTH`. Gates `PCREC_NO_ALTCLS_MERGE`/`_FACTOR`
  (deny-only), stamps `<PREFIX>_ALTCLS_MERGES`/`_FACTORED` (common to both
  emitters). Wider multi-char class merge is UNSOUND. Tests tests/altcls/;
  sabotage S66/S67.
- callgraph.c — [DD-14] THE CALL GRAPH: which groups are called, what they reach;
  sole writer of `.body`; Kleene fixpoints for `minw`, `maxw` ([DD-14.LB], no cycle
  test: saturation absorbs), `cwmin`; publishes `nonnullable` off `minw` ([K69],
  least fixpoint); `cg_eligibility` decides `CALL_SPLICE` per TARGET (not in a
  cycle, expansion within `PCREC_MAX_SPLICE_NODES`, composing over nested splices,
  saturating; `-fno-splice-calls` returns before any of it). Does NOT compute
  nullable/W (recurrence lives in the emitter). `\K` inside lookaround through a call
  is NOT refused (PCRE2's rule is lexical; tests/recursion/kreset.rxt). Sabotage
  S166 (pass order), S165 (prefilter vs call), S171 (maxw one round).
- derive.c — [COMPOUND] B2 DERIVATIONS: `pcrec_derive_split_q` ([MATCH-SPLIT]'s Q:
  kill `\G`/non-multiline `^` `\A` to the never node, prune bottom-up, GROUP-KEEP
  rule, G5 check, `PcrecDeriveReport`); `pcrec_ast_crosses_attempts`. Runs second in
  the tree-hook list (after the composer, before altcls). Tests tests/compound/.
- lower_enc.c — [M5.0] ENCODING LOWERING: `LowerOps` table, one row per encoding (no
  `if (enc == ...)`); code-point classes -> byte-sequence ASTs; sole producer of
  `A_WCLASS` ([CLS-TREE] S3); clears `u.rep.revbody` where lowering would change the
  body (`subtree_is_identity` vs `identity_max`); exports `pcrec_pat_char`; no
  `default:` arm; does not follow `u.call.body`. Tests: tests/codegen/run_cpset_structure.sh.
- postresolve.c — [DD-14.LB] POST-RESOLUTION CHECKS: re-asks module `lookaround`'s
  fixed-width rule at the pattern offset the hook RECORDED, after the graph exists
  (record -> build graph -> re-ask). Owns WALK and ORDER (ascending pattern offset);
  `src/parse/mod_lookaround.c` owns the RULE. Pending is `u.look.widths == NULL`
  (loud by construction). Walks via `pcrec_ast_visit`. Sabotage S169/S170; tests
  tests/recursion/inlookaround.rxt.
- (prefix_k.c, the [OPT-K] offset-k SELECTION, RETIRED at D172 S2 commit 6: the
  memfn kit's window family decides which offsets the skip tests, prefix_k's
  model transcribed as its A-model/C-model rows (memfn/src/window.c, constants
  memfn/src/plan_cost.def); pcrec states the walk, `kset_walk`, as a fact and
  reads the family's phase-1 reply. Its header's MISCOMPILE-1 account (role A
  k0 vs role B the walk's frontier[0]) is docs/design/offset_k_skip.md's.)
- select_engine.c — per-pattern ENGINE selection ([M4.5b], engine_m4.md §5.1), `--engine` and prefilter refusals, drives possessify.c on the chosen engine. Full entry in NOTES.md.
- atomic.c — [M6.4.2] `pcrec_discharge_atomic` (the FREE DISCHARGE: deletes an
  `A_ATOMIC(A_REP(X))` cut whose TRANSPARENT possessify verdict is positive; GREEDY
  only; keyed on the GROUP; survey sees call sites [K93]); the seven no-`default:`
  switches; predicates `pcrec_has_atomic` (read post-discharge), `pcrec_has_bref`,
  `pcrec_bref_mark` (§3.2.4 marked set; all refs of a duplicated name),
  `pcrec_has_lookaround` (twin of has_atomic, read with `Vm.mrl_win`),
  `pcrec_has_call`, `pcrec_has_linked_call` (narrowing; meaningful only after the
  graph), `pcrec_has_live_capture` (dead-capture elision; not a DEFINE rule),
  `pcrec_ast_stamped_by` (SR-8 stamp for RK_QUANTSUFFIX). Not registered in a
  `discharge` socket.
- possessify.c — [ENG-BREP] POSSESSIFICATION (eng_brep_design.md §2, D47.1): marks `A_REP` needing no resume frames; `pcrec_poss_survey` is the same verdict as a query. Full entry in NOTES.md.
- revdet.c — [ENG-BREP] REVERSE-DETERMINISTIC RUNG analysis (engine_m4.md §2.5,
  eng_brep_design.md §3): `Ast.u.rep.revbody` is verdict AND material (non-NULL iff
  the rung applies; read by `vm_cost_rep`, `vm_count_slots`, `vm_rep`). Forward
  uniqueness imported from possessify; reverse check on the reversed body;
  `rd_alt_disjoint` re-derived on purpose; `pcrec_revdet_first` exported; `\K`
  DECLINES (correctness requirement). Tests tests/rungselect/; sabotage S50-S52.
- mrl.c — [M4.6d] width analyses: `pcrec_minw` (BYTES, MRL prune, exhaustive switch,
  saturating at `PCREC_MINW_MAX`; `A_CALL` reads `u.call.minw`; `A_BREF` contributes
  0, exact), `pcrec_cwmin`/`pcrec_cwmax` (CHARACTERS; `A_CLASS` = 1; `maxw` retired
  into `cwmax`; only caller is module `lookaround`'s width rule), `pcrec_nullable`
  ([PATFACTS] 3.5, one owner), `pcrec_sat_add`/`pcrec_sat_mul` ([PATFACTS] 3.6).
  `PCREC_W_UNBOUNDED == PCREC_MINW_MAX` so unbounded absorbs. Tests tests/mrl/
  (D27-blinded corpus; `maxw_check.c`, `cwmax_check.c`), tests/core/sat_arith_check.c.
- scanedge.c — [OPT-5] DFA SCAN EDGE: after `pcrec_minimize_dfa`, DELETES scan-shaped state chains; eight preconditions, each a decline; gate `-fno-scan-edge` (docs/spec/tuning.md §2.18). Full entry in NOTES.md.
- dfamemo.c — [OPT-RETRY-REUSE] MACHINE MEMO: `pcrec_build_min_dfa` (build +
  minimize), every DFA build site in compile.c goes through it; memoized across retry
  attempts by content key; only clean builds stored; compile_driver's local.
- minimize.c — Moore-style DFA minimization with signature hashing; `eolvar` and
  `endvar` (resolved through the EOL chain) join the signature; initial partition
  splits on BOTH accept bits (`accept*2 + waccept`); `Dfa.s1w` and `Dfa.s1g[]` remap
  in their own loops. Moore needs O(n) rounds (K25: `a{0,25000}` sets
  tests/resource's CPU budget).
- startanch.c, endwin.c — MOVED to `src/facts/` ([PATFACTS] step 3.0, D126); entries in
  src/facts/CLAUDE.md.
- reqbyte.c — DELETED ([FINDINGS] B1 = [PATFACTS] 3.1, D126): walk -> `src/facts/req.c`, picks -> `src/core/findings.c`; its still-binding rules are in NOTES.md.

## Per-topic entries (kept as one-line tags; cited by tests/mech sabotage rows)

- Per-topic tag entries ([DD-14 wave G], [M4.6f], [OPT-4.1], [OPT-4.2], [K53-SELRETRY], [OPT-PRECHECK-ADMIT], [DD-11.5]): moved verbatim to NOTES.md, section "Per-topic entries (cited by tests/mech sabotage rows)".

## Pointers

APPROACH.md §5; docs/design/engine_m4.md (§2.5, §5.1, §5.2, §6.1); eng_brep_design.md;
atomic_groups_design.md; subroutines_design.md (§3-§5, §8-§9); lookaround_design.md;
utf8_design.md §2; offset_k_skip.md; opt5 docs (docs/dev/opt5_step0_profile.md,
docs/design/opt5_step2_twopass.md); poss_arms.md; dec_fallback.md; reqpos_2b.md;
reqbyte_freq_pick.md; docs/spec/tuning.md (§2.17, §2.18, §2.29); docs/dev/decisions.md
(D10, D46, D47.5, D67, D77, D126); src/facts/CLAUDE.md; tests/{mrl,possessify,rungselect,
altcls,prefilter,recursion,offsetskip}/CLAUDE.md; tests/mech/sabotages/.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/src__opt.md

See also NOTES.md in this directory (history, lessons, rationale, moved detail).
