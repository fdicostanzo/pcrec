# [PATFACTS] STEP 1 — THE INVENTORY

D120 chartered this as a read-only step: every per-pattern analysis in the
tree (file, question, tree level, `Job`/`Ast`/`Ctx` field, consumers,
encoding dependence), the redundancies, and the facts computed twice or
reached ad hoc. Nothing here is designed — STEP 2 (the four-lens design,
memory `pcrec-design-evaluation-lenses`) and STEP 3 (implement-then-replace)
are separate, later plan rows. This document is read-only evidence at commit
`b5c1423b` (main); re-grep before citing a line number once a lane has
touched `src/opt/`, `src/ir/`, or `src/gen/`.

**Method.** Seven read-only sub-lanes, each assigned a disjoint file set
under `src/opt/`, `src/ir/`, `src/gen/`, or the three existing partial
design notes (`compare_stack.md`, `reqbyte_freq_pick.md`, `reqpos_2b.md`)
plus `cycle1_analysis.md`. Every file the D120 charter or the plan row names
was read in full except `emit_dfa.c`/`emit_vm.c` (1.2 MB combined —
grep-driven targeted reads of named functions). Cross-checked: the pipeline
ordering below was independently re-derived from a direct grep of
`src/core/compile.c` (not merely quoted from `internal.h`'s prose), and one
correction to the `[DD-14 wave G]` comment's own phrasing is noted where the
grep disagreed with a paraphrase.

---

## FINDINGS FIRST

### The two D120-named incidents, confirmed present and NOT yet fixed

1. **`reqbyte.c`'s necessary-byte-set and the necessary-run analysis are the
   SAME bottom-up walk with a second accumulator** — confirmed literally:
   `pcrec_req_byte` (`src/opt/reqbyte.c:583`) calls one internal walk,
   `rb_walk` (`:380`), whose accumulator `RbVal` (`:162`) bundles `RbSet set`
   and `RbRuns runs` explicitly "because they come off one walk" (the file's
   own header). This is not a live redundancy needing a fix — the two
   accumulators were already folded into one function — but it IS the
   concrete shape D120's incident (1) describes, preserved here as evidence
   that "implement two facts inside one walk" is a real, load-bearing
   pattern this tree already uses in one place and a PatFacts record should
   generalize rather than special-case.
2. **The byte-frequency prior `pcrec_byte_freq_ppm` (`src/opt/prefix_k.c:125`)
   has (at least) three call SITES, each restating an encoding gate.**
   Confirmed and refined: (a) `prefix_k.c`'s own offset-k selection cost
   model (`:306,315,326-329,462-531`) calls it **UNGATED** — no
   `encoding==PCREC_ENC_BYTE` test at all, unlike its two siblings; (b)
   `reqbyte.c`'s necessary-byte argmin pick (`rb_pick:525,530`), run
   scan-index pick (`rn_scan_index:544,546`) and run window-truncation pick
   (`rn_window_start:572`) — three call expressions inside ONE file, sharing
   one `bytekey = (encoding == PCREC_ENC_BYTE)` gate; (c) `emit_dfa.c:5499`
   (`req_byte_dominated_by`), gated the same way. So structurally this is
   closer to **three call SITES (one per file)**, one of which
   (`prefix_k.c`'s own) is not gated at all — a discrepancy from its two
   siblings not previously flagged, recorded here as a finding (§ Redundancy
   R9 below), separate from D120's cited incident. **D122 ADDENDUM 2(3)
   already rules the fix** ("the prior's encoding gate moves INTO the
   accessor... one derivation") — chartered, not built; this inventory is
   the evidence D120 wanted before the design.

### New redundancies found beyond the two named incidents (numbered R1-R12; consolidated, deduplicated across all seven sub-lane reports)

- **R1 — `pcrec_has_bref`/`pcrec_has_linked_call` computed twice per compile
  for two different reasons.** `select_engine.c:611,658` computes them
  (as locals `has_bref`/`has_call`) to decide engine forcing/prefilter
  eligibility; `emit_vm.c:13184,13201` independently RE-WALKS the whole tree
  to compute the same two predicates again, purely to render the
  `--emit-ir` `VmStamp` listing. Nothing carries the selection-time answer
  forward as a `Job`/`Ctx` field, so a debug listing pays for (and can, in
  principle, disagree with) a second full-tree walk of a fact already known.
- **R2 — no `Job`/`Ctx` field caches `has_bref`/`has_call`/`has_atomic`/
  `has_lookaround` at all**; every reader (`atomic.c`'s `pcrec_has_atomic`/
  `pcrec_has_lookaround`/`pcrec_has_bref`/`pcrec_has_linked_call`,
  `select_engine.c`'s locals, `emit_vm.c`'s listing) re-walks the
  post-discharge tree from scratch. This is the general shape D120 opened
  the row to fix, present at four-plus call sites for four related
  booleans, none of them expensive alone but all four together are one
  extra whole-tree pass apiece with no result surviving past its own call.
- **R3 — `pcrec_mrl_sat_add`/`pcrec_mrl_sat_mul` (`mrl.c:96,104`) and
  `pcrec_cg_sat_add`/`pcrec_cg_sat_mul` (`callgraph.c:462,472`)** are the
  same saturating-arithmetic primitive (bounded add/multiply against the
  same `MRL_MINW_MAX`/`PCREC_MINW_MAX` ceiling) implemented twice in two
  files. Both are non-`static`/exported, so nothing structural stops
  `callgraph.c` calling `mrl.c`'s versions directly — this looks like an
  oversight rather than a deliberate split.
- **R4 — nullability has (at least) two independent per-node predicates
  that must agree and are coded separately**: `pcrec_minw(a)==0`
  (`src/opt/mrl.c`, used by `select_engine.c`'s `fit.lang_nullable` and by
  `nfa.c`'s `pcrec_startgate_needed`) and `vm_nullable`
  (`emit_vm.c:1281`, a separate per-kind switch used for VM empty-iteration
  guards). They are DELIBERATELY not unified for `A_CALL` — `vm_nullable`'s
  arm reads `!a->u.call.nonnullable` (the callgraph fixpoint,
  `callgraph.c`'s `cg_minw_publish`-adjacent field) while `pcrec_minw`'s
  own `A_CALL` arm reads `Ast.u.call.minw` — but for every OTHER `AKind` the
  two are two independently-written switches over the same structural
  question, with no shared table. A third instance of the same underlying
  fact, `nfa.c`'s `cstart_check_omission`, is EXPLICITLY documented as a
  deliberate independent re-derivation (a cross-check, not a redundancy —
  see the ir/ section).
- **R5 — `vm_cursor_fits`/`vm_det_seq` (`emit_vm.c:1721,1853`) are
  re-derived at three separate call sites within `emit_vm.c` itself**
  (`vm_cost_rep`, `vm_count_slots`, `vm_rep`) — `src/gen/CLAUDE.md` already
  names this as a known re-derivation risk (unfixed, self-documented). This
  is D120's failure mode occurring WITHIN one file, not only across
  `opt/`-vs-`gen/` boundaries.
- **R6 — `vm_isl_words`/`vm_isl_build` (the alternation-island trie
  analysis, `emit_vm.c:3716,3915`) re-asks a shape question `altcls.c`'s
  stage-1/stage-2 merge/factor passes already partially answered**, over
  largely the same alternation subtrees, at a later pipeline stage. Not a
  literal duplicate (different questions — mergeable-into-one-class vs.
  finite-literal-language/trie-eligible) but a second full walk of ground
  the first walk already restructured.
- **R7 — `pcrec_scan_range`/`pcrec_state_view_invariant`
  (`scanedge.c:199,237`) is read from two places** (`scanedge.c`'s own
  `member_ok` wrapper AND `emit_dfa.c:6015,6025`'s axis-J
  start-pinned-search predicate) — this is recorded as a POSITIVE
  precedent, not a redundancy: `src/opt/CLAUDE.md` states this was
  deliberately built as one derivation with two readers specifically to
  avoid a parallel mechanism. Likewise `pcrec_startgate_needed`
  (`internal.h`, declared for `nfa.c`) is a pure accessor over
  `Job.fit.lang_nullable` rather than a second nullability walk, and
  `startanch.c`'s `Job.start_anchor` is confirmed by ONE DIRECTIONAL
  assertion against the DFA's own `dfa_interior_dead` answer
  (`emit_dfa.c:7427,7431`) rather than two independent sources of truth.
  These three are the template a PatFacts design should generalize, cited
  here alongside the redundancies they contrast with.
- **R8 — `DFA_SELECT`'s per-axis form choice (`dfa_select`, `emit_dfa.c:4290`
  and its eight candidate-list instantiations) is re-derived (not cached)
  at each of several reader sites per axis** (loop-shape emission, the
  stamp emitter, the `rx_info` field writer) — each call is cheap and the
  file's own discipline is "one derivation per call, not cached across
  calls", but there is no `Job` field holding the chosen form, so a
  PatFacts record that wanted to expose "which prefilter form does this
  artifact use" to another pass (D122's literal-search kit reuse) would
  have nowhere to read it from today.
- **R9 — `prefix_k.c`'s own use of `pcrec_byte_freq_ppm` is UNGATED on
  encoding**, unlike its two sibling call sites in `reqbyte.c` and
  `emit_dfa.c` (see "the two D120-named incidents" above). Flagged as an
  inconsistency for STEP 2 to resolve rather than assumed harmless — the
  walk is over byte-class NFA states regardless of encoding, so the
  prior's ranking may be merely SUBOPTIMAL rather than UNSOUND under
  `utf8` (the prior is a cost-model fallback, never a correctness
  promise), but nobody has verified that argument against the ungated
  code path.
- **R10 — `req_admit` (`emit_dfa.c:5514`, `[OPT-PRECHECK-ADMIT]`) is a
  bespoke, one-off "is this analysis's result already covered by another
  route" admission test, built for exactly one fact (`Job.req_byte`/
  `req_run`).** D122's literal-search kit direction (D122(3), "carry
  verified facts forward") needs the same admission logic for MORE sites
  (VM literal-run super-instruction, DFA_PF_MEMCHR) that do not have one
  yet — this is not a redundancy today, but a generalization gap: the one
  instance that exists is not a reusable primitive, it is
  `req_admit`-shaped code specific to `Job.req_byte`.
- **R11 — a rejected redundancy, kept as a positive precedent**: a proposed
  second stamp `<PREFIX>_VM_INLINE_CHAIN` was DECLINED at design time
  specifically because it would have been a second spelling of the
  already-existing `has_push`/`emitted_push` fact (`src/gen/CLAUDE.md`'s
  own record). Evidence that this failure mode is watched for, at least
  reactively, in emitter-side design reviews already.
- **R12 — altcls.c's branch-peeling "is this a single byte" test
  (`pcrec_cls_single`, used at `altcls.c:190`, `reqbyte.c:454`,
  `emit_vm.c:3659`) and prefix_k.c's offset-k cost model both ask a
  "can this position be pinned to one byte" question**, at different
  pipeline stages (pre-engine-selection rewrite eligibility vs.
  post-selection scan-cost ranking) — not a strict duplicate, but exactly
  the shape D122 addendum 2(2) already names as the byte-cube's future
  home (`src/core/`'s `cube_of`): a single-byte pin is the degenerate case
  of a cube, and the fact that three unrelated files each ask a version of
  "is this one byte" is itself evidence for centralizing the cube.

### The pipeline order (re-derived directly from `src/core/compile.c`, not merely quoted)

```
pcrec_parse
  -> pcrec_altcls              (compile.c:1362)   [rewrite; Job.altcls_merges/altcls_factored]
  -> pcrec_discharge_atomic    (compile.c:1378)   [rewrite; hoisted out of select_engine at DD-14 wave G]
  -> pcrec_callgraph_build     (compile.c:1397)   [Ctx.callgraph; 3 Kleene fixpoints + linkage/splice eligibility]
  -> pcrec_select_engine       (compile.c:1424)   [Job.fit / Job.engine; runs pcrec_possessify, pcrec_revdet
                                                    internally, both VM-only-gated]
  -> pcrec_postresolve         (compile.c:1435)   [re-asks module lookaround's fixed-width rule now the
                                                    call graph exists; runs AFTER select_engine, not
                                                    immediately after callgraph — a correction to a loose
                                                    paraphrase of the "[DD-14 wave G]" comment, confirmed
                                                    by direct grep of compile.c's call order]
  -> pcrec_lower_enc           (compile.c:1488)   [rewrite; encoding-specific class lowering; may CLEAR
                                                    Ast.u.rep.revbody post-hoc if unsound under utf8]
  -> pcrec_start_anchor        (compile.c:1503)   [Job.start_anchor — runs on the LOWERED tree]
  -> pcrec_end_window          (compile.c:1506)   [Job.end_window — runs on the LOWERED tree, beside
                                                    start_anchor]
  -> pcrec_req_byte            (compile.c:1517)   [Job.req_byte / Job.req_run — runs on the LOWERED tree]
  -> pcrec_build_nfa / pcrec_nfa_wrap_unanchored  (compile.c:1537, :1647, :1653)
  -> pcrec_build_dfa (x1-3: main, reverse, [ENG-ABS] optional anchored) (compile.c:1654,1657, and the
                                                    optional machine built separately, compile.c:360, LAST
                                                    among a compile's DFA builds per its own budget rule)
  -> pcrec_minimize_dfa        (compile.c:1660-1661, :1698, :368)
  -> pcrec_scanedge_dfa        (compile.c:1678,1680, :375)
  -> emission (pcrec_emit_dfa / pcrec_emit_vm)
```

Two things this ordering makes explicit and load-bearing for a future
PatFacts record:

1. **Not every analysis shares one tree level.** `select_engine.c`'s
   internal work (possessify, revdet, the `forces_*`/`lang_*` predicates)
   runs on the PRE-LOWERING (code-point) tree; `startanch.c`/`endwin.c`/
   `reqbyte.c` run on the POST-LOWERING (byte-class) tree. A single record
   populated at one moment cannot serve both without either moving
   lowering earlier (a real design cost — lowering must be redone, and D26
   the `mrl.c`/`callgraph.c` char-width fixpoints are deliberately measured
   in CHARACTERS specifically because they run pre-lowering) or splitting
   the record into (at least) two population points.
2. **A fact computed at stage N can be INVALIDATED (not merely read) by
   stage N+1.** `revdet.c`'s `Ast.u.rep.revbody` is set during
   `select_engine.c`'s internal `pcrec_revdet` call (pre-lowering) and can
   be retroactively CLEARED by `lower_enc.c`'s `subtree_is_identity` check
   if the reversed body is not byte-identity-safe under `utf8` (reversal
   and lowering do not commute for a multi-byte character). A PatFacts
   design needs a way to represent "this fact may still be revoked by a
   later stage", not just "this fact is available from stage N onward".

### Requested facts from incoming customers (enumerated, not designed)

**(a) [OPT-LITSCAN]** ("carried verified facts", D122(3)) — every distinct
fact-shaped thing this customer will eventually need to READ from a
PatFacts record, drawn from `compare_stack.md`'s own sequence and D122's
addenda:

1. The necessary literal run's byte sequence, offset from the candidate
   start, and length (today `Job.req_run`/`ReqRun`).
2. Per-offset candidate byte-sets from the NFA walk (`PrefixKSets`,
   `prefix_k.c:386`), each with its own cost/selection weight.
3. The byte-frequency prior's value for a given byte, with the ENCODING KEY
   resolved at the accessor (D122 addendum 2(3): "the prior's encoding gate
   moves INTO the accessor"), not restated per reader.
4. The byte cube `(K,T)` for a position or set — singleton, fold pair, or
   general AND-mask cube (`cube_of`, not yet in `src/`; three throwaway
   copies exist in `studies/`/`docs/dev/optloop/` today).
5. Fold-table-derived pair sets (`src/core/fold.c`'s ASCII partner table,
   `utf8_fold_pairs.inc`) as the compile-time source of a K/T mask.
6. The admission verdict for a given pre-check site: is it dominated by a
   later route and hence elidable (`req_admit`'s question, generalized
   beyond its one instance — R10 above).
7. Which engine route (DFA prefilter / VM / VM-hybrid prefilter) reaches a
   given program point — a "carried fact" is sound only for the route that
   actually verified the run.
8. The verified span's end position/state after a successful literal-run
   verify, so a matcher can enter there instead of re-scanning.
9. Whether a class/run test needs the K/T mask form at all — the
   pay-for-what-you-use predicate (all-exact vs. caseless/non-singleton
   cube) per position (D122 addendum).
10. The subject-end guard bound for wide/SWAR loads (a cross-cutting fact
    every wide compare/scan form needs, tied to the chosen run length
    rather than pattern-specific, per D122 addendum 3's SWAR admission).

**(b) [VAR]** — `docs/design/variables_pattern.md` §2, quoted verbatim:
"This is `[PATFACTS]`'s first outside customer, and D120 ... absorbs the
five one-line ANALYSIS declines specifically; it does not and cannot absorb
`nfa.c`'s lowering or `emit_vm.c`'s emission, which are real per-kind work
no shared record removes." The five analyses that must treat an `A_VAR`
node (opaque until match time) as a declared NEUTRAL ELEMENT rather than a
new hand-written case label each:

- necessary byte + necessary run (`reqbyte.c`'s `rb_walk`, joining the
  existing `A_BREF` arm) → empty set.
- start anchor (`startanch.c`'s `sa_walk`) → contributes nothing.
- end window (`endwin.c`'s `ew_walk`) → `EW_NONE`.
- min/max width (`mrl.c`) → `minw`/`cwmin` = 0 (a variable may be empty),
  `cwmax` joins the existing `A_BREF` unbounded arm.
- first-byte/prefix/frequency-prior analysis (`prefix_k.c`) —
  structurally unreachable (a var-bearing pattern is already VM-only with
  no prefilter by the time this pass would run); the real gate is a third
  whole-tree predicate `has_var` in `select_engine.c`'s
  `prefilter_decision`, alongside `has_bref`/`has_call`.

[VAR]'s ask of PatFacts is narrow: a record whose per-node contribution for
an opaque/run-time-valued atom (today `A_BREF` and `A_VAR`; a third such
construct is a foreseeable future customer) is ONE declared neutral element
per analysis, rather than N hand-written case labels repeated per
construct.

**(c) [FINDINGS]** — plan.md's row (opened 2026-09-25, commit `b5c1423b`,
`STATE:started`, think-lane stage only). **Genuinely thin, by design**:
Frank's own sequencing is think → design → critique loop, and no design
note has landed yet. What exists: a distinction between FILE-GENERAL
findings (byte-frequency-style statistics computed OUTSIDE pcrec, from a
reference corpus) and PATTERN-SPECIFIC findings, and a named list of
still-missing pieces (`reqbyte_freq_pick.md` §2.2: name resolution, a `row`
reader, a CLI surface, the named analyses + generators, the analyzer
itself, and "a RUN-LEVEL value", unspecified beyond "not yet built").
Named customers already waiting on it: [OPT-FREQPICK]/[OPT-REQPOS] tier
2b's run-form choice, [OPT-LITSCAN] S4(a)'s caseless-run pick,
[OPT-FIRSTSET], offset-k, and the byte-frequency prior's own
encoding-gate-into-accessor move (D122 addendum 2(3)). Recorded here as
REQUESTED BUT UNDESIGNED — padding this section with an invented shape
would misrepresent a charter Frank deliberately sequenced behind a
not-yet-run think lane.

---

## PER-FILE INVENTORY

Tables below use these column heads: **Site** (file:function:line),
**Question**, **Tree level**, **Result lives in**, **Consumers**,
**Encoding dependence**. "Tree level" abbreviations: `raw AST` = as parsed;
`post-altcls` = after `pcrec_altcls`; `post-discharge` = after
`pcrec_discharge_atomic`; `post-callgraph` = after `pcrec_callgraph_build`
(node carries `u.call.{minw,cwmax,cwmin,link}`); `pre-lowering` = any point
before `pcrec_lower_enc` (code-point classes, character-unit widths);
`lowered` = after `pcrec_lower_enc` (byte-class, byte-unit widths); `NFA`,
`DFA` = the built machine; `VM program` = the emitter's in-construction
program.

### src/opt/altcls.c — alternation → class normalization (rewrite pass with two embedded eligibility analyses)

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `altcls_branch_peel`:180, via `pcrec_cls_single` | Is this branch's first atom a single-byte literal class (peelable prefix byte)? | raw AST, spine-flattened | return value, not stored | `altcls_extend_prefix`:218,226; `altcls_factor_run`:271 (same file) | Declines for any code point above 0xFF — fewer branches peelable under `utf8`. |
| `altcls_walk_alt` merge test:340-357 | Is a maximal adjacent run of branches all bare `A_CLASS` (mergeable into one class)? | raw AST | rewrites tree; `Job.altcls_merges++` | `<PREFIX>_ALTCLS_MERGES` stamp, `pcrec_emit_prologue` (shared, both emitters) | Operates on the interval-set (`PcrecCpSet`) representation post-[M5.0], so identical under byte/utf8 by construction. |
| `altcls_factor_run` grouping:260-299 | Which maximal adjacent branches share a literal first byte, worth prefix-factoring? | raw AST | rewrites tree; `Job.altcls_factored++` | `<PREFIX>_ALTCLS_FACTORED` stamp (same prologue) | Same byte-confinement decline as above. |
| `altcls_walk` per-kind decline table:397-517 | For each `AKind`, is this node opaque to both merge/factor stages? (`A_BREF`,`A_VAR`,`A_KRESET`,`A_LOOK`,`A_CALL`,`A_ATOMIC` all decline) | raw AST | returns node unchanged | dispatch within this file only | Structural, kind-based; no encoding dependence. |

Runs FIRST, immediately after parse, before every other pass — downstream
analyses see shapes this pass may have merged/factored.

### src/opt/atomic.c — module `atomic-groups`' whole-tree predicates + free discharge

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `pcrec_has_atomic`:59 | Does the tree still carry an `A_ATOMIC` cut? | post-discharge | function, recomputed | `emit_vm.c:9980` (`mrl_win` computation) | none |
| `pcrec_has_lookaround`:149 | Does the tree carry any `A_LOOK`? | post-discharge | function, recomputed | `emit_vm.c:9981` (same `mrl_win` expr, ANDed with above) | none |
| `pcrec_has_collapsible_rep`:221 | Does the tree carry a counted repeat `[OPT-4]`'s collapse would change? | raw/post-altcls | function; cached ONCE into `EngineFit.prefilter_has_collapsible_rep` (`select_engine.c:571`) | `emit_vm.c:9965` reads `fit.prefilter_has_collapsible_rep` (never re-derives) | Declines to descend `A_LOOK` bodies (erased to epsilon by NFA builder regardless of encoding). |
| `pcrec_ast_stamped_by`:290 | Did registry row `row`'s producer stamp any node in this tree (D65 built-status)? | post-discharge | function; reads `Ast.reg` | `src/dump/syntax_dump.c:932,958` (`--list-syntax`) | none |
| `pcrec_discharge_atomic`:527 | For every `A_ATOMIC(A_REP(X))`, is the cut PROVABLY a no-op? | raw/post-altcls (runs immediately after `pcrec_altcls`; hoisted out of `select_engine` at DD-14 wave G) | AST rewrite (splices atomic out); deletion IS the record | consumed implicitly by everything downstream that no longer sees the cut | Structural, no encoding dependence. |
| `pcrec_has_bref`:565 | Does the tree contain any backreference? | raw AST | function; also called directly as a local in `select_engine.c:611` and independently re-derived at `emit_vm.c:13184` for the `--emit-ir` listing (R1/R2 above) | `select_engine.c:611`, `emit_vm.c:13184` | none |
| `pcrec_bref_mark`:647 | Which capture groups are referenced by a surviving backreference (incl. duplicate-name run members)? | post-discharge | fills caller's `bool*` array, no persistent field | `mod_backrefs.c:835` (group-erasure decision), `emit_vm.c:9880` (capture-slot planning) | none |
| `pcrec_has_live_capture`:807 | Is there a capture group some emitted code can actually WRITE (dead-group elision)? | post-discharge | function | `select_engine.c:139` | none |
| `pcrec_has_linked_call`:919 | Does the tree carry a call with no finite inlining (narrowing of `pcrec_has_call` — a SPLICED call is excluded)? | post-callgraph (needs `u.call.link`) | function; independently re-derived at `emit_vm.c:13201` for the listing (R1/R2) | `select_engine.c:658` (local `has_call`), `emit_vm.c:13201` | none |
| `pcrec_has_call`:954 | Does the tree carry any subroutine call node at all? | raw AST | function | `mod_lookaround.c:534,546,556` (fixed-width lookbehind deferral rule) | none |

Every exhaustive `AKind` switch in this file explicitly declines to follow
`Ast.u.call.body` (the whole-tree-walk-must-not-follow-the-back-edge rule,
design §4.4), to avoid non-terminating compiles on self-referencing
patterns.

### src/opt/callgraph.c — the call graph (three Kleene fixpoints + linkage/splice eligibility)

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `pcrec_callgraph_build`:676 (called `compile.c:1397`) | Build the call graph: targets, edges, run 3 fixpoints | post-discharge, PRE-select_engine (`compile.c:1397` precedes `select_engine`'s call at `:1424` — the graph must exist before selection reads it) | `Ctx.callgraph` (opaque, arena-owned) | all accessors below | none structurally |
| `cg_minw_publish`:245 | Min-width Kleene fixpoint per call target (descends from infinity) | call-graph over post-discharge AST | `Ast.u.call.minw` | `mrl.c`'s `pcrec_minw` `A_CALL` arm | none (byte-width metric) |
| `cg_cwmax_publish`:299 | Max CHARACTER-width fixpoint per target (ascends from `PCREC_W_UNBOUNDED`) | call-graph, pre-lowering | `Ast.u.call.maxw`+`maxw_known` | `mrl.c`'s `pcrec_cwmax` `A_CALL` arm → `endwin.c`'s decline test, `mod_lookaround.c`'s fixed-width rule via `postresolve.c` | Character-unit only while `utf8` has no separate backend — file header names this as the one spot a future UTF-8-aware width backend must revisit. |
| `cg_cwmin_publish`:330 | Min CHARACTER-width fixpoint per target | call-graph, pre-lowering | `u.call.cwmin` | `mrl.c`'s `pcrec_cwmin` | same caveat as above |
| `cg_eligibility`:487 | Is a call target SPLICE-eligible (no cycle via `reaches(i,i)`, expansion fits `PCREC_MAX_SPLICE_NODES`/`_TOTAL`)? | call-graph structure | `Ast.u.call.link = CALL_SPLICE` (or not) | `pcrec_has_linked_call`, `pcrec_callgraph_spliced` (`emit_vm.c:7612`), `select_engine.c`'s SR-8 splice exemption | none |
| `pcrec_callgraph_reaches`:907 | Does target `i` reach target `j`? | call-graph | function over precomputed closure | `emit_vm.c:2691,7342,7414,7420,7427,7630` (region/frame planning) | none |
| `pcrec_callgraph_spliced`:914 | Is target `i`'s linkage `CALL_SPLICE`? | call-graph | function reading `u.call.link` | `emit_vm.c:7612` (whether to emit a shared callee region at all) | none |

Accessor family `pcrec_callgraph_ntargets/target/body/index` are pure
structural readers, consumed by `emit_vm.c` (region emission, the
`vm_count_slots` walk, `vm_nullable` at `:7179`) and `nfa.c:969`
(prefilter-eligibility narrowing).

### src/opt/endwin.c — the end-anchor start window

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `ew_walk`:81 | Which end-anchor strength (NONE/EOL/Z) does every match of this subtree satisfy at its own end? | raw/post-altcls AST | local, folded into `pcrec_end_window`'s return | internal only | Reads `Ast.u.anch.multiline` for the `A_EOL` case. |
| `ew_see_gstart`:145 | Does the pattern contain `\G` anywhere (decline — `\G`'s truth depends on `search_from`)? | raw AST | local bool | internal only | none |
| `pcrec_end_window`:154 (called `compile.c:1504-1506`, after `pcrec_lower_enc`) | How many bytes from the subject's END can a match begin, or -1 (decline)? | **lowered** AST | `Job.end_window` (-1 = decline) | `emit_dfa.c:653,671,8133,8136`; `emit_vm.c:12508` | Declines outright under a multi-byte encoding (`PcrecEnc.start_cls != NULL || max_cp > 0xFFu`) since a byte-offset clamp could land mid-character. |

`pcrec_end_window` directly calls `pcrec_cwmax(root)` (mrl.c/callgraph.c's
fixpoint) as its width source — a direct, one-hop consumer relationship,
not a redundancy.

### src/opt/mrl.c — width analysis (three functions, opposite safe directions)

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `pcrec_minw`:120 | Minimum bytes any match consumes (under-estimate is the SAFE direction) | **lowered** tree (post-`pcrec_lower_enc`, post-altcls/discharge/callgraph) | return value; `A_CALL` arm reads `Ast.u.call.minw` | `select_engine.c:568` (`fit->lang_nullable`), `startanch.c:80`, `callgraph.c:829` (feeds its own fixpoint), `emit_vm.c:392,3382,5271,5840,5978,6110,8358,8709,9855` | `A_CLASS` = 1 byte in either encoding — the one place minw is loose rather than tight per-encoding; safe because it's a lower bound. |
| `pcrec_cwmax`:305 | Max width in CHARACTERS (over-estimate is the safe direction — opposite of minw) | **pre-lowering** AST (asked from module `lookaround`'s parse hook, before `pcrec_lower_enc` runs) | return value; `A_CALL` reads `Ast.u.call.cwmax`/`cwmax_known` | `mod_lookaround.c:308,319`, `endwin.c:88,93,172`, `startanch.c:78,84`, `callgraph.c:870` | Character-unit by design — encoding-invariant by definition, unlike minw. |
| `pcrec_cwmin`:444 | Min width in characters | pre-lowering AST | return value; `A_CALL` reads `u.call.cwmin` | `mod_lookaround.c:308,319` (`cwmin==cwmax` fixed-width test), `callgraph.c:849` | same as cwmax |

`pcrec_minw` is called at MORE THAN ONE POINT in the pipeline against trees
at different lowering stages — `select_engine.c`'s prefilter decision reads
it (a point that's arguably pre-lowering, since `select_engine` runs before
`pcrec_lower_enc`) while the file's own header describes the canonical call
as post-lowering. **This is currently implicit in call-site position rather
than a stated contract** — a concrete gap for STEP 2's design to close
rather than merely note.

### src/opt/lower_enc.c — the encoding lowering pass and its embedded decisions

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `ops_for`:445 | Which `LowerOps` row (byte/utf8) applies | table dispatch | local | `pcrec_pat_char`, `pcrec_lower_enc` | IS the encoding switch — the only `if (enc==UTF8)`-shaped decision in the compiler, per the file's own header. |
| `pcrec_pat_char`:462 | Decode one pattern character's byte length at a pattern offset | raw pattern text | return value | `src/parse/parse.c` literal sites | byte=1; utf8=full decode, refuses ill-formed text |
| `subtree_is_identity`:473 | Does lowering leave every class in this DETACHED subtree (`u.rep.revbody`) unchanged? | revdet's reversed-body copy (detached) | return value, consumed inline | `lower_walk:545-547` (clears `u.rep.revbody` when false — the retroactive-invalidation case noted above) | Threshold is per-encoding (0xFF byte / 0x7F utf8); always true under `byte`, so the revdet rung never drops for this reason there. |
| `lower_walk`:514 | Rewrite every `A_CLASS` node to the encoding's byte-level form, in place | AST post-altcls/discharge/callgraph/select_engine/postresolve | splices in place | everything downstream (NFA build, both emitters) | THIS is the encoding-dependent rewrite itself. |
| `cap_sig`:591 | Invariant check: did lowering move/drop/duplicate any `A_CAP` root? | pre vs. post snapshot | two locals compared in `pcrec_lower_enc` | internal only (`pcrec_ctx_fail` on mismatch) | n/a |

Single caller: `compile.c:1488`.

### src/opt/minimize.c

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `state_sig`:39 | Per-state Moore-refinement signature (transition targets + resolved `eolvar`/`endvar` chain value + dual accept bits) | DFA, post subset-construction | local, folds into partition-refinement hash | internal only | n/a |
| `pcrec_minimize_dfa`:74 | Driver: partition-refine to the minimal DFA; remap `s0`/`s1`/`s1w[]`/`s1g[]` | DFA | mutates `Dfa*` in place | `compile.c:368,1660-1661,1698` | — |

Reads `Dfa.ncls`, `DState.eolvar/endvar`, `Dfa.s1u[]/s1g[]` directly rather
than through an accessor — flagged as a candidate cross-file reach, but
likely INTENDED (minimize.c operates in place on the very structure
`ir/dfa.c`'s `intern()` built, as a second construction stage on the same
data rather than a downstream consumer of a published fact).

### src/opt/possessify.c — the possessification analysis/rewrite

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `first_of`:175 | FIRST-byte set a subtree can begin with (Glushkov-style) | pre-lowering AST (possessify runs from `select_engine.c:481`, before `pcrec_lower_enc`) | return value (`First` struct) | internal to `pss_walk`/`gk_build` | Reads code-point classes, not yet lowered. |
| `body_admits_unique_iteration`/`pcrec_uniq_scratch`/`pcrec_uniq_iteration`:721,762,769 | (U1)/(U2): does this body decompose into iterations UNIQUELY (one-unambiguous + prefix-free position automaton)? | AST | return bool | **exported and reused verbatim by `revdet.c:689,691`** on the REVERSED body — one implementation, two call sites, a deliberate anti-redundancy design | — |
| `pss_walk`/`pss_verdict`/`pss_rep`:808,814,848,890 | Can this `A_REP` be marked possessive (no retreat needed)? | AST | `Ast.u.rep.possessive` | `emit_vm.c` (frame-free emission) | Reads `Ast.u.anch.multiline` PER-NODE (confirmed CURRENT at possessify.c:329, explicitly "NOT `cx->mods`" — the historical scope-blind defect reading the parser's end-of-pattern state at verdict time is fixed). |
| `pcrec_poss_survey`:1117 | Same verdict as `pss_walk`, as a pure query (no marking) | AST | callback-reported, no field | **one caller**: `atomic.c:545` (`ds_add`, free-discharge eligibility) | same multiline note |
| `pcrec_possessify`:1145 | Driver: run `pss_walk` to fixpoint | AST | writes `Ast.u.rep.possessive`, monotone | **one caller**: `select_engine.c:486` | — |

### src/opt/postresolve.c

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `pr_count`/`pr_collect`:95-117 | Which lookbehind nodes recorded a pending fixed-width check at parse time (`u.look.widths == NULL`)? | post-callgraph AST | local `PrPend` array | internal, feeds `pcrec_postresolve` | n/a |
| `pcrec_postresolve`:128 (called `compile.c:1435`, AFTER `pcrec_select_engine`, not immediately after callgraph — see pipeline-order correction above) | For each call-bearing lookbehind, re-derive module `lookaround`'s §2.5 fixed-width rule now the call graph exists; refuse at the recorded offset if it fails | post-callgraph, pre-lowering AST | mutates `Ast.u.look.widths` via `pcrec_lookaround_fix_widths` (`mod_lookaround.c:411`) — a parse-module function, not a `Job` field | `emit_vm.c:6757` (`vm_look_behind`, `pcrec_ctx_fail`s if still NULL); ordering constraint on `lower_enc.c` (must run after, since a resolved width changes character-vs-byte units) | Width is in CHARACTERS here; `lower_enc.c` converts to bytes afterward. |

This is the "record at parse time / rebuild the graph / re-ask" shape named
in `subroutines_design.md` §3.4(d) — not a new fact-computation itself, but
the site where a module's own rule (owned by `mod_lookaround.c`) is
re-executed once a later-arriving prerequisite (the call graph) exists.

### src/opt/prefix_k.c — [OPT-K] fixed-offset tier-1 prefix analysis + the byte-frequency prior's home

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `pcrec_prefix_ksets`:386 | Which bytes must appear at offset `j` (0..`PCREC_PREFIX_K_MAX`-1) from a match's own start (walked from `Nfa.anch_start`); which offset is cheapest to `memchr`-scan vs. verify | NFA (post-lowering, needs the built NFA) | `PrefixKSets` — an EMITTER-LOCAL struct, not a `Job` field (`emit_dfa.c:3401` declares it inside `UnanchStart`) | one call site: `emit_dfa.c:3536` (`unanch_start`'s candidate derivation); `--debug` dump via `optk_debug_dump` (`emit_dfa.c:3538`) | Sound under any encoding (walks the byte-class NFA directly); the cost-model PRIOR it uses is byte-only (below). |
| `pcrec_byte_freq_ppm`:125 (table at :89) | Static byte-frequency prior in ppm — a fixed table, NOT itself a per-pattern analysis, called by three per-pattern analyses across three files | n/a (constant table) | none | See "the two D120-named incidents" above for the full three-site enumeration and the ungated-in-this-file finding (R9). | Encoding gate restated at two of its three call sites; ungated at the third (this file's own use). |

### src/opt/reqbyte.c — [OPT-REQBYTE] + [OPT-REQPOS] tier 2b

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `pcrec_req_byte`:583 (internally `rb_walk`:380) (called `compile.c:1517`, after `pcrec_lower_enc`) | (a) which bytes must appear ANYWHERE in `[search_from, subject_length)` for any match; (b) the longest guaranteed-contiguous literal byte run every match must contain — ONE bottom-up walk, two accumulators (D120 incident 1, confirmed folded already — see FINDINGS FIRST) | **lowered** tree | `Job.req_byte` (-1 = none) and `Job.req_run` (`ReqRun{bytes[],idx,len}`) — chosen at ONE site so they cannot disagree (internal.h's own comment) | both emitters' search entries (gated by `req_admit` in `emit_dfa.c`, [OPT-PRECHECK-ADMIT]) | Walk itself is encoding-neutral; the ARGMIN PICK of which set/run member to scan is byte-only (`bytekey` flag), falls back to PCRE2's rightmost-member/leftmost-window rule otherwise. |

### src/opt/revdet.c — reverse-deterministic rung eligibility

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `rd_shape`:97 | Can the backward emitter reproduce this quantifier body at all (no assertion, no non-exact nested repeat, ≤`PCREC_MAX_REVDET_BODY_GROUPS` groups)? | raw AST (pre-lowering — revdet runs from `select_engine.c:507`) | local `Shape{ngroups,ok}` | feeds `rd_rep` immediately | none |
| `pcrec_uniq_iteration` (possessify.c:769), called `revdet.c:689,691` | Does the (forward, then reversed) body admit unique iteration? | pre-lowering AST | bool | shared with possessify.c's own verdict — one derivation, two callers | n/a |
| `rd_reverse`:296 | Builds the body's REVERSED AST | pre-lowering AST → new detached AST (`rd_node`:260, D70-kind-guarded copy) | `Ast.u.rep.revbody` (when the rung is taken) | `emit_vm.c:1524,1551,5397` — one field is both the verdict and the emission material | Post-hoc revocable by `lower_enc.c` (reversal and lowering do not commute for multi-byte characters). |
| `rd_alt_disjoint`:581, using `pcrec_revdet_first`:481 | Does the reversed body's dispatch have no choice points (re-derived rather than trusted as implied by U1)? | reversed AST | bool; the FIRST-set is also consumed by `emit_vm.c:5117`, `possessify.c:207,232`, `cpset.c:278` | see above | Widening fallback (`pcrec_cls_bits_widen`) for a class carrying code points >0xFF. |
| `pcrec_revdet`:784 (called `select_engine.c:507`) | Hunts the whole tree for eligible `A_REP` nodes (single level only — no rung offered to a quantifier nested inside another's already-rung body) | post-altcls/discharge AST | writes `Ast.u.rep.revbody`; return count discarded by caller | one call site | n/a |

Ordering: eligibility is decided pre-lowering, then potentially REVOKED
post-lowering — the invalidation shape named in FINDINGS FIRST.

### src/opt/scanedge.c — DFA scan-edge / dead-interior-state elimination

The one `opt/` pass that operates purely on the built DFA, not the AST.

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `pcrec_scan_range`:199 | For a scan-shaped chain over class `cls`, what `[lo,hi]` byte range does it correspond to? | DFA (post-minimization) | return value | `emit_dfa.c:3645,6254,6263` | none |
| `pcrec_state_view_invariant`:237 | Does this state carry no `eolvar`/`endvar` position-view divergence (precondition 3)? | DFA | return value | `member_ok` (this file), `emit_dfa.c:6015,6025` — ONE derivation, two readers (a positive precedent, R7) | none |
| `shaped`:249, `acc_of`:266, `in_degrees`:273 | Is state `s` scan-shaped for `(class,exit)`; its accept bit; which states are view/seed targets (chain-head exclusion) | DFA | locals | `collect` | none |
| `collect`:312 | Builds the actual scan chains (maximal runs meeting all 8 preconditions) | DFA | local `chains` array | `pcrec_scanedge_dfa` | Precondition 8 takes `prefilter_reseeds` (derived from `emit_dfa.c:5570`, an EMITTER-side fact) as an explicit cross-file PARAMETER rather than re-deriving it — a clean interface, flagged as worth noting for its shape. |
| `pcrec_scanedge_dfa`:482 (called `compile.c:375,1678,1680`) | Deletes interior chain states, renumbers survivors to sit at the machine's top rows | DFA | mutates `Dfa` in place | `emit_dfa.c`'s `dfa_form_derive` (layout invariant check), the whole emitted scan-loop machinery | none |

Gated by `PCREC_NO_SCAN_EDGE` (deny-only, D46-stamped axis I). No AST or
encoding dependence.

### src/opt/select_engine.c — the central engine-choice hub (largest file, 67 KB)

Runs on the post-altcls/discharge/callgraph tree, PRE-lowering. Result
published wholesale to `cx->job->fit` (`EngineFit`) at the pass's end, plus
side effects on `Ast.u.rep.{possessive,revbody}` via its internal
`run_possessify`/`run_revdet` calls (both gated `fit.chosen==ENGM_VM`
only).

| Site | Question | Result | Consumers | Encoding |
|---|---|---|---|---|
| `forces_captures`:107-143 | Does the artifact promise group offsets AND can any actually be written (`want_caps && ncap>0 && pcrec_has_live_capture`)? | contributes to `mask` → `fit.engines`/`fit.chosen` | engine-choice switch | none |
| `first_dfa_excluding`/`forces_registry`:200-350 | Is there a VM-only-stamped (`Ast.reg`) node, walking through/around calls/lookarounds per D67 SR-8? | `mask`, `why`/`why_pos`/`node_why` | same | none |
| `forces_dfa_overflow`:383-391 | Did a PRIOR compile_driver attempt's DFA build overflow (`Ctx.dfa_disabled`)? | `mask`, `why` | engine-choice switch; the `[SEL-1]` retry ladder in `compile.c` | none |
| `esel_of`:933-967 (9-arm outcome ladder, table 890-901) | Which `<PREFIX>_ENGINE_SEL` (`ESEL_*`) token records HOW the engine got chosen | `fit.engine_sel` | both emitters' stamp emission, `--emit-ir`, bench D81 bucketing | none |
| `prefilter_decision` (fn body 556-868) — `fit.lang_nullable` | `pcrec_minw(root)==0` — reuses mrl.c, not a second walk | `fit.lang_nullable` | `compile.c`'s `[OPT-4.1]` build gate, `--emit-ir` | none |
| same fn — `fit.prefilter_has_collapsible_rep` | `pcrec_has_collapsible_rep(root)` | `fit.prefilter_has_collapsible_rep` | same 2 sites | none |
| same fn — `has_bref` local:611 | `pcrec_has_bref(root)` | local (feeds `fit.prefilter`) | see R1/R2 | none |
| same fn — `has_call` local:658 | `pcrec_has_linked_call(root)` | local | see R1/R2 | none |
| same fn — `has_var` local:686 | `pcrec_has_var(root)` — any `A_VAR`? | local | feeds prefilter refusal | none |
| same fn — `lang_nullable_declinable` local:837 | `lang_nullable && !has_bref && !has_call && !force_on` | local | feeds the two decline fields below | none |
| same fn — `fit.prefilter_declined_nullable`/`_default`:854-859 | Did a rung's rescue get declined for nullability / did the ordinary hybrid's own exact prefilter get declined? | `EngineFit` fields | `esel_of`, bench bucketing (`docs/spec/tuning.md` §2.17), `--emit-ir` | none |
| same fn — `fit.prefilter`:860-867 (the final verdict) | Does this artifact run the VM hybrid DFA prefilter at all? | `EngineFit.prefilter` | `emit_vm.c` (`RX_VM_PREFILTER` stamp, build gate), `esel_of` | none |
| `run_possessify`:481-487 | Drives `pcrec_possessify` to fixpoint, VM-only gated | `Ast.u.rep.possessive` | `emit_vm.c` | none |
| `run_revdet`:503-508 | Drives `pcrec_revdet`, same VM-only gate | `Ast.u.rep.revbody` | `emit_vm.c` | `lower_enc.c` may clear `revbody` afterward under `utf8` |

This file is the single largest CONSUMER of other passes' outputs
(`mrl.c`'s `pcrec_minw`, `atomic.c`'s `pcrec_has_bref`/`_linked_call`/
`_live_capture`, `callgraph.c`'s `u.call.link`, `Ast.reg` stamps from every
module) — confirmed as the redundancy-prone hub D120 names, and confirmed
NOT reading `pcrec_byte_freq_ppm` directly (the D120 incident does not
extend to this file).

### src/opt/startanch.c — the start-anchor analysis

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `sa_walk`:70 | At which positions can a match begin — accumulates `SA_BOT`/`SA_GSTART` bits | **lowered** AST (called after `pcrec_lower_enc`) | local | `pcrec_start_anchor` | Reads `Ast.u.anch.multiline` and `pcrec_cwmax`; correctness after lowering depends on running post-lower. |
| `pcrec_start_anchor`:143 (called `compile.c:1503`) | Reduces `sa_walk`'s bits to `PCREC_SANCH_BOT`/`_GSTART`/`_NONE` | lowered AST | `Job.start_anchor` | `emit_dfa.c:5411,5463-5477,7427,7431` (a ONE-DIRECTIONAL confirming assertion against the DFA's own `dfa_interior_dead` answer — R7 positive precedent, not a redundancy); `emit_vm.c:10960,12752,12758`; `axes_dump.c:581` | none directly |
| `pcrec_start_anchor_name`:153 | Canonical string for a `PCREC_SANCH_*` value | n/a | `<PREFIX>_VM_START` stamp, `--list-axes` rows | none |

### src/ir/nfa.c

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `ast_bare`:94 | Strip `A_CAP` wrapper (D31 group-erasure) | AST | local, not cached | every `->k` dispatch/spine walk in this file | none |
| `disjoint_run_len`:373 | Longest prefix of a flat alternation's branches whose class bitmaps at `depth` are pairwise disjoint (bounds safe reordering, trie rule 2) | AST (flattened branch list) | local, consumed by `trie_build` | `trie_build:466,471` | Byte-level, already-lowered bitmaps. |
| `trie_key`:539 | Is this alternation branch trie/string-edge eligible — a left-leaning `A_CAT` spine whose every leaf is `A_CLASS` with a byte-confined interval set? Produces the byte-sequence key if so. **This IS the M2.8 eligibility test [OPT-VMLIT]'s plan row cross-references for "which alternation branches are straight runs."** | AST | local `TItem{seq,len}`, not cached | the M2.8 factoring path invoked from `compile_ast`'s `A_ALT` handling | Calls `pcrec_cls_bits` (`src/core/cpset.c`), which REFUSES a non-byte-confined class — so under `utf8` a class naming a code point >0xFF makes the branch ineligible BY CONSTRUCTION, not by a separate encoding test. |
| `cstart_check_omission`:1086 | Verify (not derive) that omitting the K50 character-boundary gate was sound: does any state reachable without consuming a byte either accept, or admit a byte the encoding refuses as a character start? | NFA (epsilon+assertion closure of start state) | none — pure verification, `pcrec_ctx_fail`s on violation | one caller: `pcrec_nfa_wrap_unanchored` | Reads `PcrecEnc.start_cls`; a no-op under `byte`. Explicitly documented as a deliberate SECOND, independent proof against `pcrec_startgate_needed`'s AST-level answer — a double-check, not a redundancy. |
| `pcrec_startgate_needed` (internal.h, defined for nfa.c) | Does this pattern need the K50 boundary gate on the unanchored self-loop (nullable)? | reads `Job.fit.lang_nullable` | not separately stored — a pure accessor, deliberately named to avoid a second derivation | `nfa.c:1150,1153`, `emit_dfa.c:7487` | Only meaningful where `start_cls != NULL` (utf8). |
| `pcrec_nfa_has_bot`:1200 | Does the NFA contain any BOT-family node (`^`/`(?m)^`/`\G`), which the unanchored one-pass machine cannot evaluate? | NFA (linear scan) | not cached, recomputed each call | `compile.c:1649` (the `ENG_UNANCH` vs `ENG_ATTEMPT` engine-shape fork) | none directly |

### src/ir/dfa.c

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `refine_by`/`eqclasses`:118,155 | Byte-equivalence-class partition: which of the 256 byte values can share one transition-table column? (refined by every `N_CLASS` bitmap, then the word set, newline set, and K50's `start_cls`) | NFA scan → DFA alphabet | `Dfa.clsmap[256]`, `Dfa.ncls`, `Dfa.rep[256]` | `minimize.c:45,81,194-195`, `emit_vm.c:1566`, `emit_dfa.c`'s whole transition-table emission — the fact that makes tables `ncls`-wide instead of 256-wide | `startcls` argument non-NULL only where an `N_CSTART` gate exists (utf8). |
| `intern`'s `Ctx.subset_elems` accounting:1029-1089 | Per-pattern subset-construction COST: how many NFA-state-list elements has this compile interned so far, checked against `PCREC_MAX_AUTO_DFA_ELEMS` (auto-only) then `PCREC_MAX_SUBSET_ELEMS` (hard cap) | subset-construction-in-progress | `Ctx.subset_elems`, `Ctx.dfa_overflowed`/`_why`/`_is_budget` | `[SEL-1]`'s auto retry (`forces_dfa_overflow`); `[ENG-ABS]`'s optional-machine caller (`compile.c:367`) | None directly; a wider alphabet from `eqclasses` under utf8 can change how many distinct views intern, indirectly. |
| `intern`'s state-count cap:983-1008 | Has this pattern's DFA exceeded `d->maxstates`? | subset-construction | `Ctx.dfa_overflowed`, `d->overflowed` | same as above | none |
| `view_same`:946 | Are two class-axis views for a candidate state IDENTICAL (aliasable to one stored list)? | subset-construction | drives `owner[u]` aliasing (which is what makes the cost charge exact) | internal to `intern` | none |
| `intern`'s dedup loop:970-981 | Has this exact closed-state identity already been interned — DFA STATE MINIMIZATION AT CONSTRUCTION TIME | subset-construction | `Dfa.tab[]`, `Dfa.st[]` | every worklist successor lookup | none |
| `DState.eolvar`/`endvar` interning rule (dfa.c:953-967) | Is this state's EOL/END view DIFFERENT from its base/EOL-view reference, warranting a separate interned variant (canonicalized RELATIVE to the EOL view, not the base, to avoid over-interning `$`-free-of-`\z` patterns) | subset-construction | `DState.eolvar`/`endvar` (-1 = "same as reference") | `minimize.c`, `scanedge.c`, `emit_dfa.c` | none |
| `s1u[]`/`s1g[]` start-state family, `sides_of`:1160 | Which interior start state applies given class-axis context (word-boundary/`(?m)`), and the `\G`-closed start family — CONFIRMED construction, not analysis (no separate decision fact stored beyond the resulting start-state IDs) | NFA→DFA closure per context | `Dfa.s1u[UPC_N]`, `Dfa.s1g[UPC_N]` | `emit_dfa.c`, `minimize.c`, `prefix_k.c`, `scanedge.c`, `startanch.c` | `s1g[]` exists only where `Mach.has_gst`; `s1u[]` context arrays only where `upc_live[u]` — pay-for-what-you-use. |

Reachability/dead-state elimination over the BUILT DFA is NOT in `dfa.c` —
`PCREC_DFA_DEAD` (-1) is only the per-branch "this optional machine's
construction gave up" sentinel. The actual state-merging/equivalence
analysis lives entirely in `src/opt/minimize.c` (see above).

### src/gen/emit_dfa.c / src/gen/emit_vm.c — the emitters

Both files are read grep-driven (488 KB / 743 KB — too large to read
linearly). Consumption of an `opt/`-computed fact is listed tersely; only
genuinely emitter-computed decisions (no `opt/` pass already made them) are
tabled in full.

**Pure consumption (a fact computed by an `opt/` pass, read here without new decision content)** — grouped by field:

- `Job.req_byte`/`Job.req_run`: `emit_dfa.c` (`req_admit`'s definition site
  and the pre-check emitter it gates, ~`:5514`), `emit_vm.c` (search-entry
  candidate use).
- `Job.start_anchor`: `emit_dfa.c` (`req_admit`'s own read), `emit_vm.c`
  (attempt-loop bound).
- `Job.end_window`: both emitters bound the attempt/scan loop on it.
- `Job.altcls_merges`/`altcls_factored`: stamped once in the shared
  prologue (`pcrec_emit_prologue`, `emit_dfa.c`) — not per-emitter
  duplicated.
- `Ast.u.call.nonnullable`: `emit_vm.c:1405` (`vm_nullable`'s `A_CALL`
  arm).
- `Ast.u.call.minw`: `pcrec_minw` reads it (not this file); the emitter's
  own root-minw check consumes `pcrec_minw(root)` at emission time.
- `job->fit.prefilter`/`.chosen`/`.engine_sel`: read throughout both
  emitters for the `RX_ENGINE`/`RX_ENGINE_SEL`/`RX_ENGINE_WHY`/
  `RX_VM_PREFILTER` stamps.
- `job->enc_mask`: mutated BY the VM emitter's own `A_BREF`/`A_VAR`
  emission as it emits calls (an OR accumulated, not a pure external read),
  then read by `pcrec_emit_prologue`.
- `job->dfa`/`.rdfa`/`.adfa`: read wherever a stamp folds over "every
  machine the artifact contains" (up to 3 machines per [ENG-ABS]).
- `job->vm_emitted_nodes`/`vm_rungs`/`vm_frame_capacity`/`vm_subject_ceiling`:
  WRITTEN by the emitter itself at the end of `pcrec_emit_vm` (an outbound
  field, not a consumed one).

**Emitter-computed analyses (no `opt/` producer exists for these):**

| Site | Question | Tree level | Result lives in | Consumers | Encoding |
|---|---|---|---|---|---|
| `vm_nullable`, `emit_vm.c:1281` | Can this node's language match the empty string? A SEPARATE per-kind switch from `pcrec_minw(a)==0` (R4) | lowered AST | `static` function, not memoized | `emit_vm.c:1417,1424,1478,2198,2373,2951,4919,5966,7179` (empty-iteration guards, cursor-rung eligibility) | none |
| `vm_cost` family (`vm_cost_rep/cap/cat/alt/atomic/look/call/kreset`), `emit_vm.c:2083-2757` | How many resume frames/trail entries/step-charge does this subtree need (drives frame_capacity/subject_ceiling and the entry-shape size term)? | lowered AST | returned `Cost` struct, consumed immediately by capacity planning, not cached on the node | frame/trail capacity stamps | `vm_cost_look` uses a documented UNIFORM lookaround charge (over-charges rather than analyzing the body); `vm_cost_call` reads `v->rgn_cost[idx]` via `pcrec_callgraph_index` — an `opt/`-level fact consumed here. |
| `has_push`/`Vm.emitted_push`/`Vm.emitted_set` | Did any site actually emit a resume push / trail write — a BYPRODUCT of emission bookkeeping, not a tree walk | emission-in-progress | `Vm` struct fields | fail-label dispatch omission, `<PREFIX>_VM_ENTRY_SHAPE` ladder legality, `always_inline` gate | none |
| `vm_lifts`/`vm_cuts`, `emit_vm.c:1473,1519` | Can an atomic-group's cut be pushed into a child `A_REP`'s possessive rung? | lowered AST, post-possessify/revdet | threaded parameter (`under_atomic`), never stored — recomputed at each descent to avoid staleness under `-fno-possessify` | `vm_rep`, `vm_cost_rep`, `vm_count_slots_rep`, `vm_revdet_fits` | none |
| `vm_count_slots` family, `emit_vm.c:2758-3200ish` | How many and which slot-index families does this subtree need, per emitted COPY (not per lexical node)? Also fills `save`/`nsave` on `Ast.u.call`. | lowered AST, walked in the SAME order as `vm_emit`'s own emission (a same-file ordering invariant — the `[DD-14 wave B+C]` §4.4c bug this was written to fix) | `Vm` struct running counters; also calls `vm_isl_build` for island push counts | `RX_NSLOTS`, frame/trail capacity, the listing | none |
| `vm_isl_words`/`vm_isl_build`/`vm_isl_cands`, `emit_vm.c:3716,3915,4120` | Is this subtree's language a finite set of literal byte strings (the `[ENG-ISL]` alternation-island question, over the POST-altcls-factored tree, finer-grained than altcls's own merge/factor test — R6) | lowered AST (post-altcls) | `VmIsl`/`VmIslNode`, emitter-local | `vm_alt`'s dispatch, `vm_count_slots` (push count), `vm_cost` | none |
| `vm_det_seq`/`vm_cursor_fits`, `emit_vm.c:1721,1853` | Is this `A_REP` body a sequence of disjoint singleton-byte tests scannable as a byte-class span rather than by frame replication? | lowered AST | emitter-local `uint8_t[32]` bitmap, recomputed at 3 call sites (R5) | `vm_cost_rep`, `vm_count_slots`, `vm_rep` | Byte-confined-class test in spirit. |
| `vm_marked`, `emit_vm.c:1177` | Is this capture group referenced by any backreference (PUBLISH-AT-CLOSE vs. write-on-traverse for `A_CAP`)? | lowered AST (derived from `A_BREF` nodes) | recomputed at 4 sites (cost analysis, slot count, `A_CAP` emission, slot legend) | see above | none |
| `vm_rev_caps`, `emit_vm.c:1926` | Capture-recovery walk for the reverse-deterministic rung's backward pass | `Ast.u.rep.revbody` | emitter-local | the backward-emission path | none |
| `DFA_SELECT` mechanism (`dfa_select`, `emit_dfa.c:4290`, and `dfa_reprs[]`:4628, `dfa_views[]`:4746, `dfa_seeds[]`:4809, `dfa_accs[]`:4899, `dfa_pfs[]`:5359, `dfa_matches[]`:5818, `dfa_edges[]`:6200, `dfa_scans[]`:6288) | Which of several candidate emitted FORMS applies to this machine — per axis, first-matching `applies` predicate in preference order (the exact table-driven shape D122 addendum 2 names as the literal-search kit's model) | DFA (built machine) | the chosen candidate is re-derived (not `Job`-cached) at each reader site per axis (R8) | loop-shape emission, stamp emitters, `rx_info` field writers | none — DD-12(7) forbids encoding conditionals in the emitter. |
| `dfa_premul`/`fold_tr`/`fold_acc`, `emit_dfa.c:3133,2829,2846` | Is this machine small enough to premultiply its transition table by stride; are all cells of a transition/accept table identical (uniform-table fold)? | DFA | emitter-local, consumed by the table-emission call and the `<PREFIX>_DFA_UNIFORM_FOLDS` stamp — ONE shared derivation | both | none |
| `req_admit`, `emit_dfa.c:5514` (definition), `:309` (declared) | Given `Job.req_byte`/`req_run`, is the whole-window pre-check DOMINATED by a route the artifact already runs (the prefilter, or a one-attempt pinned DFA route)? **This is a second-order consumer of an `opt/` fact that adds real decision content of its own — exactly D122's "carry verified facts forward / elide a dominated pre-check" shape, built for ONE fact only (R10).** | DFA + `Job.req_byte`/`req_run` | emitter-local bool | gates whether the pre-check is emitted at all | reads `dfa_search_is_pinned`, `dfa_cand_scan_byte` (via `dfa_pf_of`), `Job.start_anchor` |
| `dfa_search_is_pinned`, `emit_dfa.c:6056` | Is the reverse machine's start-state accept UNCONDITIONAL, letting the reverse pass (search-start recovery) be elided entirely? Deliberately reads `up[UPC_PLAIN].accept`, NOT the wider `state_acc_any` bit `unanch_start` computes — a documented near-miss correction. | DFA | emitter-local bool, re-derived at 5 documented reader sites | dispatch, `<PREFIX>_DFA_START` stamp, `rx_info.search_form`, two stamp-name folds that must stop reading `job->rdfa` once pinned (an ordering hazard, explicitly flagged in `src/gen/CLAUDE.md`) | none |
| `emit_state_legend`, `emit_dfa.c:3925` | Cosmetic-only: BFS shortest-path-to-example-string per state for `--emit-ir`/legend text. K60 found this used to raw-`malloc` and silently degrade on OOM; D105 moved it to arena allocation, routing through the general failure mechanism. **Not a per-pattern decision beyond rendering.** | DFA | text buffer | `--emit-ir` output | none |

---

## SUMMARY: WHAT A PatFacts DESIGN (STEP 2) INHERITS

- A canonical linear pipeline with (at least) THREE distinct tree "epochs"
  a record must represent: pre-lowering/pre-callgraph, post-callgraph
  pre-lowering, and post-lowering — not one snapshot.
- At least one fact (`Ast.u.rep.revbody`) that is decided at one epoch and
  can be REVOKED by a later one — a "still valid?" bit, not just a value,
  is needed for at least this fact and plausibly others STEP 2 should
  audit for the same shape.
- Two positive precedents already in the tree (`pcrec_startgate_needed`,
  `pcrec_scan_range`/`pcrec_state_view_invariant`, `Job.start_anchor`'s
  one-directional DFA confirmation) showing "one derivation, several
  readers, no re-derivation" is achievable today without a unified record
  — evidence the mechanism is proven, only inconsistently applied.
- A concrete, general primitive gap: no site exists for "is this pre-check
  dominated by an already-verified fact" except `req_admit`, built for one
  fact. [OPT-LITSCAN]'s whole direction needs this generalized.
- A concrete, small, mechanical fix available immediately and separable
  from the PatFacts design itself: R3's duplicated saturating-arithmetic
  helpers (`mrl.c`/`callgraph.c`) could be unified today with no design
  dependency.
- Two "requested but not yet needed" customers ([OPT-LITSCAN], [VAR]) with
  enumerated fact lists above, and one genuinely undesigned customer
  ([FINDINGS]) that STEP 2 should not wait on.
