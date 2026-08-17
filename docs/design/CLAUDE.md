# docs/design/ — living design documents

Documents that describe a design AND the process/learning of building it —
panel-outcome blocks and refutations recorded inline rather than edited away.
Living: revised as the design is reviewed and built, unlike docs/dev/'s
append-only or historical records.

## Files

- `extension_design.md` — ADOPTED (D34: Part II is the redesign of record)
  and progressively BUILT through MOD-0.1..0.3 (the first producers landed
  2026-08-12): how a regex feature plugs into pcrec — one table, a NAME per row as the unit of
  enable/disable, two PORTS per row, and a RECOGNISE-then-PRODUCE seam. Written
  from scratch rather than as an amendment to D32/D33, and **partly REFUTED by
  the R13 panel**; the refutations are inline. Read the PANEL OUTCOME block at
  the top before any section. **PART II (§11-§18)** is the post-ruling redesign
  (D34): per-port recognition, always-live recognisers, lexical-mode rows for
  `\Q`/`\E`/`(?#)`, the `want`×`may` ask contract, the measured endpoint rule
  — itself reviewed the same session by R14
  (`../dev/reviews/2026-08-11-r14-part2.md`), which refuted its two central factual
  claims; corrections inline marked R14, and §18 holds the post-R14 state
  plus the five decisions left for Frank. Read BOTH panel-outcome blocks
  before any section.
- `design_notes_mod06.md` — MOD-0.6 (module `unicode-props`) phase-1 design
  note: the \p/\P syntax-port shape and its CLAIM/REFUSE dispatch rule
  (bound to options=0, R10 disposition 3), the K10 row fix, the streaming
  normalisation algorithm and its 48-significant-character boundary
  (measured, not assumed — tests/probes/probe_uprops.c), the in-class
  tail-sweep extension design, and the phase-2 test plan. ACCEPTED by the
  manager 2026-08-12; phase 2 (code) built from it — see
  tests/registry/CLAUDE.md and src/parse/CLAUDE.md's `mod_uprops.c` entry
  for what actually landed.
- `design_notes_mod07.md` — MOD-0.7 (`--explain` rewrite) phase-1 design
  note: the measured refutation of the plan row's own cure (the
  declared-vs-live agreement clause is swap-blind — both sides read
  `r->module`), the query→doorway mapping (one shared router, two callers),
  selection = prefix ∪ candidates, the election/promise/attribution clauses
  and their honest limits, exit 3 for dissent, §13's six manager rulings and
  §14's V1-V7 failing-direction measurements. ACCEPTED and built 2026-08-12
  — see cli/CLAUDE.md and src/parse/CLAUDE.md's `syntax_dump.c` entry for
  what landed.
- `design_callout_abi.md` — PROPOSAL (eighteenth session, 2026-08-14):
  the callout-ABI ↔ match-here alignment owed to M4's match-API freeze
  ([M4-CALLOUTS] amendment), incorporating Frank's three same-day
  rulings (R-a same-interface, R-b captures-so-far structure + future
  embedded code, R-c group vs non-group forms; R-d same day: syntax
  UNDECIDED — callout binding near-PCRE2 (`(?C...)` family favored, no
  collision), embedded code possibly its own spelling like `\{...}`;
  any reinterpreting spelling is module-gated). ONE context-struct
  signature `ptrdiff_t (const rx_ctx *)` on both sides — `rx_ctx`
  carries subject/len/pos + captures-so-far, so a compiled matcher
  links directly as a callout AND callouts can predicate on prior
  groups (`(\d+)(<fn_gt_100>)`); VM-forcing confirmed; the
  pcre2_callout_block mirror moves to PCRE2-compat GENERATION mode;
  freeze obligations F1–F7; six open questions for Frank. Unpaneled —
  reviewed with the M4 match-API design. **RULED (D38, 2026-08-14):**
  Frank's rulings applied throughout — `rx_ctx` gains `void *user` via
  the new `rx_callout_ref` binding-unit struct (§1.1); native abort is
  match-or-fail only in v1, −2+ reserved and `__builtin_trap()`-enforced
  at call sites (F2); PCRE2-compat abort is discharged by generation-time
  call-site control flow, no native mechanism. Only Q5 (syntax spelling)
  and Q6 (embedded-code restrictions) remain OPEN. **PANELED R21
  (2026-08-14):** reviewed as a ruled input alongside `match_api_m4.md`/
  `engine_m4.md` — F8 marked SUPERSEDED (folds into `rx_info`, D43.1/
  D44) and a new F9 backported (the D42.5 caps-lifetime line); see
  `docs/dev/reviews/2026-08-14-r21-m4-design.md` and this document's own
  POST-RULING UPDATES section. Dispositions APPLIED; [M4.3] CLOSED
  2026-08-14 — this doc remains a design input; the applied frozen
  surface is match_api_m4.md.
- `subst_template_design.md` — [M4-SUBST] phase-1 design note (2026-08-14):
  the SUBSTITUTION TEMPLATE COMPILER, written before M4's match-API freeze
  because Frank's ratified observation is that the template compiler consumes
  only the capture-offset CONTRACT. **PROPOSED throughout; no panel has seen
  it and §9's fourteen questions are unruled.** §2 is the half with the
  deadline: C1-C11, requirements ON M4's match API (offset-pair shape, group
  count as a compile-time constant, the UNSET sentinel in both slots, every
  pair written on every match, byte offsets per DD-12) plus an explicit
  non-requirements list. **AMENDED 2026-08-14** against
  `design_callout_abi.md`: C4/C5 adopt `rx_ctx.caps` (`ptrdiff_t[2]`,
  `{-1,-1}` unset) per F3 and the template callbacks consume `rx_ctx`
  verbatim per F6 — §2.4 and §7.2, which return three findings to the freeze
  (adoption breaks the already-emitted `<prefix>_span`, a DD-3 event; `ncap`
  is a watermark that must be pinned to `ngroups + 1` on a completed match;
  and `rx_ctx.subject` should be `const unsigned char *`, since the emitter
  indexes 256-entry class tables with subject bytes). Also: the tiering
  mechanism (PCRE2's run-time
  `SUBSTITUTE_EXTENDED` bit becomes a compile-time MODULE — `subst` /
  `subst-extended` / `subst-pcrec` — so D18 compiles the dialect away and
  D26 tier 3's "requires module 'X'" discharges the diagnostics for free);
  the compile-time bounds check that deletes PCRE2's whole "unknown
  substring" error class from generated code; proposed emitted signatures
  with first/global as a GENERATION AXIS (D18/OS-0 named entry points, not a
  flag); the global-mode empty-match rule; the beyond-PCRE2 tier (callback
  segments reusing M4-CALLOUTS' static-extern primitive) under a namespace
  rule stated as a TESTABLE property — every pcrec-only form must be a
  spelling PCRE2 rejects; and a testing sketch whose finding is that the
  whole global-mode splice geometry is testable BEFORE captures land,
  because `$0` is already `rx_span`. Every PCRE2 claim is MEASURED
  (`tests/probes/probe_subst.c` → `../measurements/probe_subst.txt`, 10.46),
  not read from documentation: three of the note's twelve stated predictions
  were refuted, two of them changing the design. **RULED (D38,
  2026-08-14):** all fourteen of §9's questions ruled (outcomes appended
  in place, e.g. length-only no-NUL buffers, `pcrec_error`'s which-input
  tag, `rx_span` breaking at the M4 freeze) and §10's summary asks marked
  ACCEPTED; the design prose itself is unchanged, only annotated.
  **PANELED R21 (2026-08-14):** reviewed as a ruled input; §2.4's
  `rx_ctx` sketch and §2.4(a)'s compat-signature idea annotated
  SUPERSEDED/OVERRULED against D38.1/D44.2, and §5.2 gained a staleness
  banner (`match_api_m4.md` is the applied surface; `rx_subst` gains
  `RX_ERR_*` codes and the A-9 compile-time-error obligation, D44.7); see
  `docs/dev/reviews/2026-08-14-r21-m4-design.md`. Dispositions APPLIED;
  [M4.3] CLOSED 2026-08-14: STATUS is now FROZEN — the M4 working baseline (D44 addendum's weight; revisable at M4.7's post-run review).
- `match_api_m4.md` — [M4.1] MATCH-API FREEZE document (2026-08-14):
  collects every already-ruled M4 obligation into ONE freezable contract —
  a collection-and-reconciliation document, not new design. STATUS:
  PROPOSED; the freeze does not take effect until AFTER [M4.3]'s panel.
  Covers, each cited to its ruling: the `<prefix>_span` -> `ptrdiff_t[2]`
  break (D38 Q12, a DD-3 versioning event landing WITH the freeze, one
  announced-break commit, no permanent conversion seam); the caps array
  surface (`rx_ctx.caps`, `RX_NCAPS`, `RX_UNSET`) with a full C1-C11
  conformance table against `subst_template_design.md` plus its explicit
  non-requirements; the unconditional match-here export (F1/F2, including
  the `__builtin_trap()` reserved-return-value enforcement and where it
  does and doesn't bind yet); `rx_ctx`'s full layout and the
  `rx_callout_ref` binding unit (F3); the `{name, number, ref}` group
  index (F8, D39 + addendum) and what it exports before module
  `named-groups` exists; the `pcrec_error` which-input tag (subst Q8); an
  OS-0 entry-point naming table spanning both the per-prefix artifact
  namespace and pcrec's own fixed `PCREC_*` namespace (kept explicitly
  separate in §0, since D38's PCREC_*/PCRE2_* addenda govern only the
  latter); and confirmation that callout call sites thread nothing beyond
  the binding ref's `user`. Marks every claim RULED (D38/D39) vs
  PROPOSED-here vs BELIEVED; §12 collects everything introduced beyond the
  rulings (concrete symbol spellings the rulings left unpicked, and one
  load-bearing synthesis — that `rx_ctx`/`rx_matchfn`/`rx_callout_ref` are
  deliberately UNPREFIXED literal names, not `<prefix>`-scoped, so that
  composability across differently-prefixed generated matchers holds) —
  and §13 lists five ASKs for Frank, none of which are ruling
  contradictions: every apparent tension between D38 and D39 resolved on
  inspection. **AMENDED (D41/D42, 2026-08-14, pre-[M4.3] amendment
  round):** every D41/D42 ruling that touches this document is integrated
  in place, not merely annotated — `<prefix>_match_caps` (D41.4) is new
  §3.1 with a proposed signature and rationale; `<prefix>_search`'s
  negative-return space is fixed (D42.3, §1); §2.1 folds in the
  `RX_NCAPS`-is-an-artifact-property rule (D42.2) and captures-on-by-
  default (D42.1); `rx_ctx.caps`'s callout lifetime joins §4's F-list
  (D42.5); §6 records the `pcrec_err_input` V-A compat obligation (D42.4);
  the former §14 checklist is replaced by an "AMENDMENTS APPLIED" record.
  §8 gained a manager-confirmed clarification (`PCREC_*` names enum-valued
  constants only, native option surface is the `pcrec_options` struct) —
  **itself SUPERSEDED same day by D43** (below): a second wave, folded
  into the same round rather than staged. **D43 (rx_info + options
  funnel, 2026-08-14):** §5 is REWORKED from "the exported group index"
  into "the `rx_info` reflection structure — F8's group index folds in"
  — a fixed ABI type `rx_info` (`rx_ctx`'s family), one
  `extern const rx_info <prefix>_info` per artifact, carrying the option
  flags, encoding, an unconditionally-embedded pattern-string pointer,
  the group count, the folded-in group index, the selected engine, and
  the step budget — superseding engine_m4.md §5.5's comment/macro stamp
  as the CANONICAL machine-readable record (macros retained alongside it
  for compile-time consumers). §8 is corrected in place (struck through,
  not silently rewritten): booleans (`caseless`, `emit_main`, the coming
  `no-captures`) now become `PCREC_*` bits in one `pcrec_options.flags`
  word (D43.2, F3's one-representation rule extended to options), with
  both candidate bit-name spellings presented (`PCREC_CASELESS`
  recommended vs. Frank's own sketch `PCREC_CASE_INSENSITIVE`) and Frank
  disposing at panel time per D43's own text. Two structural additions
  this document had to derive beyond D43's literal member list —
  `rx_group_entry` going fixed-literal for `rx_info` to stay one shared
  type, and splitting "the group count" into `ngroups`/`ngroups_named`
  since the array holds named groups only — are flagged as JUDGMENT
  CALLS for the panel (§12 items 11–12, §13 ASK 7). **Still STATUS:
  PROPOSED** — the freeze does not take effect until [M4.3]'s panel
  closes; this round exists so the panel reviews one reconciled document
  instead of a stale one plus a decision log to
  cross-reference. **PANELED R21 (2026-08-14):** the panel's judgment
  calls above are RESOLVED (D44) — `rx_group_entry` confirmed
  fixed-literal, born with a `slot` column too (D44.3); `ngroups_named`
  renamed `nnames`; `rx_info` hardened to its final layout (`abi` first
  member, `uint64_t flags`/`int64_t step_budget`, `engine`/`engine_why`
  split, `pattern_len`, `frame_capacity`/`subject_ceiling`, D44.5); the
  search entry reshapes to a caps-array parameter and `<prefix>_span`
  RETIRES (D44.2) rather than becoming a typedef. See
  `docs/dev/reviews/2026-08-14-r21-m4-design.md` and this document's own
  §15. Dispositions APPLIED; [M4.3] CLOSED 2026-08-14: STATUS is now DESIGN
  OF RECORD for M4.4-M4.7 (working-baseline weight, D44 addendum).
- `engine_m4.md` — **PROPOSED** ([M4.2], 2026-08-14): the M4 ENGINE design —
  the backtracking VM as EMITTED SPECIALIZED C (no interpreter: one function
  per pattern, one label per pattern position, an explicit fixed-size resume
  stack + capture TRAIL, and exactly one cold indirect jump), capture tracking
  under PCRE2 leftmost-first priority (write-on-traverse, exact old-value undo,
  the empty-iteration guard), DD-2's step budget (a step IS a backtrack
  resumption, counted at one place, so forward progress is free — plus the
  SECOND bound allocation-freedom forces and DD-2's row omits: backtrack-frame
  capacity), per-pattern engine selection as a pass with a socket whose future
  customers (backrefs-finite, atomic-cut) are REWRITES that discharge a
  verdict rather than analyses that return one — hence a fixpoint, the DFA
  prefilter + islands, DD-7, DD-9 and SR-8's flip. Its load-bearing structural
  claim is that for a capture-ONLY pattern the capture-erased DFA is not an
  over-approximation but literally the SAME machine the compiler builds today
  (D31's erasure), so the existing forward+reverse pair hands the VM an EXACT
  span and the VM never scans the subject — which is also the guard on the
  measured cliff (bench case (e): pcrec 25.4 GB/s vs pcre2-interp DNF>90s; a
  naive VM on `(a*)b` would land on the DNF side). **DD-9 DECIDED:** the
  hybrid does NOT and structurally CANNOT own case (f) — `[01]*1[01]{8}` is
  capture-free, so no M4 machinery ever runs on it; re-homed to [BENCH-1]'s
  prioritizer worklist with three findings attached (computed goto is the
  WRONG lever there, contra DD-9's own hint; ~2x of the 6.61x gap is the
  reverse pass; the algorithmic candidate is bit-parallel shift-and, detectable
  from the built DFA). **SR-8's flip is SMALLER than its row implies:** zero
  currently-refused constructs become compilable when the VM exists, because
  every VM_ONLY row is module-gated by a module with no producer. Reports
  THREE tensions with the ruled D38/D39 ABI rather than resolving them
  (§11: `rx_matchfn` has no room for "the engine gave up"; it cannot deliver
  captures at all, so match-here is not the capture primitive; and D31
  rejected — on a measurement — the AST node captures now need). **ANSWERS
  `match_api_m4.md` §13 ASK 4** (§5.7, the capture contract of a DFA-compiled
  group-bearing pattern): the slot count is a property of the ARTIFACT, not
  the pattern text, so a DFA-compiled artifact emits `RX_NCAPS 1`, C6 never
  bends, and `RX_NCAPS > 1` implies the VM — one checkable line, live from
  [M4.4]. The freeze doc's candidate (b) corrected so the routing trigger is
  the requested OUTPUT rather than the presence of a `(`; candidate (a)
  rejected because it makes `RX_UNSET` permanently ambiguous and, via D38's
  subst-Q3 ruling, renders silent empty strings. §5.7.1 first sharpens the
  question: the retrofitted match-here entry has no `caps` output for ANY
  engine, which is §11.2 reached independently from the other side. §12 carries
  twelve numbered ASKs, §13 eight falsifiable predictions. §0.3 fixes the
  namespace reading (ABI types literal per `match_api_m4.md` §12.7, everything
  this doc invents per-artifact) and states what a reversal would cost: only
  the callout call site. Unpaneled: [M4.3] reviews it alongside
  `match_api_m4.md` and the two ruled pre-freeze docs. **AMENDED (D41/D42,
  2026-08-14, pre-[M4.3] amendment round):** the seven ASKs D42 rules are
  annotated in place at §12 (ASK-2 reservation kept, ASK-3 caps-lifetime
  adopted, ASK-4 DD-2's two bounds adopted, ASK-5 captures ON by default,
  ASK-8 re-homed to [ENG-ABS] gated on [BENCH-1], ASK-11 DD-9 archived to
  the worklist head, ASK-12 confirmed); §5.3, §5.7.3, §11.1 and §2.6 each
  carry a RULED note where they discuss the point D41/D42 settled (captures
  default, the M4.4→M4.5 gap, the give-up residual, and the search
  posture respectively); §0.3 records that D41.1/D41.2 ruled §12.6/§12.7 as
  proposed. The five untouched measurement ASKs (1, 6, 7, 9, 10) are
  unchanged — deliberately unruled, lane work. **D43 (2026-08-14,
  same round):** §5.5 gains a RULED note that `rx_info`
  (`match_api_m4.md` §5) supersedes this section's comment/macro stamp as
  the CANONICAL machine-readable selection/budget record; the
  `RX_ENGINE`/`RX_ENGINE_WHY` macros are RETAINED alongside it
  (PROPOSED-here, this document's own call) because they are
  compile-time-visible where `rx_info` is only link/runtime-visible —
  the two serve different consumers, not redundant ones. **PANELED R21
  (2026-08-14):** a live shipped DFA priority miscompile (K17) found by
  running this document's own §13 P-1 probe — §6.1's exactness claim
  mark SPLITS (erasure STRUCTURAL held, span-equality
  BELIEVED-WITH-GATE); §3.3's empty-iteration guard narrows to
  `rmax == -1` only (E-2, MEASURED); §3.6's oracle strategy re-scopes to
  a three-way pcrec/python/pcre2 rule with no pre-built exclusion
  mechanism (E-ASK-1 refuted, 0 disagreements); §2.4/§2.5's cursor
  discipline is written out and extended to deterministic
  capture-bearing bodies with a stamped residual ceiling (D44.1); §4.2
  now charges one step per island entry (E-5); `--engine=dfa` refuses
  captures-default patterns (D44.6). See
  `docs/dev/reviews/2026-08-14-r21-m4-design.md` and this document's own
  panel-outcome block. Dispositions APPLIED; [M4.3] CLOSED
  2026-08-14 (these two remain design inputs; the applied surface is
  match_api_m4.md, now FROZEN as the working baseline). **D46 (2026-08-15,
  twenty-first session):** every strategy-selection point (engine, cursor-
  ladder rung, bounded-repeat strategy once [ENG-BREP] lands, prefilter
  on/off, islands) must be OBSERVABLE and FORCEABLE. §5.5's `RX_ENGINE`/
  `RX_ENGINE_WHY` pair is D46's own worked example of the observability
  half; [M4.5e] extends the family to the cursor-ladder rung — but as a
  BITMASK (`<PREFIX>_VM_RUNGS`, src/gen/CLAUDE.md), not a same-shaped
  scalar macro, because the rung is selected PER QUANTIFIER BODY and a
  single value would misreport a pattern whose quantifiers land on
  different rungs (corrected mid-lane from an initial scalar draft) — the
  observability half only, landed as this document's close obligation.
  Rung FORCING (D46's controllability half) has no producer yet.
  **ANNOTATED 2026-08-15/16 (R24 C-F1, by the [ENG-BREP] lane):** §6.3's
  disjoint-follow auto-possessification bullet, §6.4's "designed, built M4.6"
  status row and §2.5's `z(ab)*y` aside all stated the disjoint-follow-ONLY
  possessification rule that `eng_brep_design.md` §2.4 measured UNSOUND (117
  counterexamples). All three are annotated in place — house style, not
  rewritten — pointing at that note's §2.2 for the repaired rule
  (unique-iteration + non-nullable + disjoint-or-exact, with a lazy-only
  non-nullable-remainder conjunct). The `z(ab)*y` example itself SURVIVES the
  correction; the general claim does not. The DELIVERY seam (§5.2's
  `discharge` hook) and the M4.6 schedule are unchanged — only the analysis
  behind the hook is bigger than §6.3 assumed.
- `k18_memo_design.md` — **BUILT 2026-08-15 (k18-rewrite lane); PROPOSED,
  AMENDED PER R23 the same day** (K18 design-first lane): the
  repair of K18, the second live tier-1 DFA priority miscompile — written
  before any rewrite lane per the R21-close scheduling. The
  defect: `clo_visit`'s `seen` is a GLOBAL per-closure memo while the
  empty-iteration rule is PATH-dependent, so the redirect is lost when the
  ε re-arrival passes THROUGH an already-seen ordinary ε state instead of
  landing on a loop entry. Recommends **prototype A2** — memo keyed on
  (state, open-loop-context), the redirect re-stated as "this loop is OPEN on
  my path", plus an EMPTY-CONTEXT FAST PATH that keeps the shipped per-state
  stamp array for the (state, 0) key. Three candidates were built and measured
  head to head, and the comparison is the document's point: the cheap
  two-line alternative (B, transparent already-seen ε states) passes the
  entire 165-case K18 acceptance corpus and is still WRONG — over a dense
  18,858-pattern shape sweep A and B differ on 83 patterns / 98 cells and the
  oracle agrees with A on **98 of 98**, every one a `{0,2}`-bodied shape where
  the conflation happens at a SPLIT rather than an ε. The naive no-memo
  variant (C) is MEASURED exponential, Θ(2ⁿ) on `(?:a*|b*){n}`, confirming the
  K18 entry's own sketch. Cost of the recommendation (re-taken on the fixed
  prototype, see the R23 block below): corpus loop-nesting depth is ≤4 (353 of
  555 patterns never open a loop), aggregate inflation **x1.004 expansions /
  x0.996 visits**, blast radius on the real corpus **547 of 555 byte-identical
  with all 8 differing patterns exactly the K18 shapes**, 1704/1704 corpus
  three ways, and 226/226 changed cells old-wrong→new-right.
  Three lane-own instrumentation defects are recorded in §7 because each
  produced numbers that would otherwise have entered the note as findings — a
  fixed-capacity memo that HANGS rather than slows when full, a
  linear-scan interner that would have priced the prototype instead of the
  design, and (added by R23) the stack-entry restore below.
  **PANELED R23 (2026-08-15, `../dev/reviews/2026-08-15-r23-k18-memo.md`):
  the DESIGN was affirmed and the PROTOTYPE was refuted.** `clo_visit`
  restored the open-loop stack's depth per frame but not its ENTRIES, so a
  redirect crossing a frame boundary corrupted an ancestor's stack — and that
  single omission was simultaneously the refutation of §2a's `nonstacktop ==
  0` cell (which the note told the rewrite lane to land AS AN ASSERTION;
  it fires on 358 of 4,369 patterns) and the ENTIRE cost residual §6 was
  built on. With the entries restored the note's headline 39 s compile at the
  parser's nesting cap is **0.35 s**, the Θ(d⁴) "cost law" dissolves, and
  **§6 ruling 1 (the D=64 inexactness threshold) is WITHDRAWN rather than
  answered** — no Frank rulings remain open from this note. A2 itself
  survived every attack: zero cells A2-wrong-shipped-right across ~330,000
  independent span cells, and every population count reproduced exactly. Also
  amended: §1.5 records a fourth sub-case (the ingredient is the PREFERRED
  alternation arm, not laziness — two of `../dev/known_issues.md` K18's own
  controls are live miscompiles with their arms swapped, corrected there),
  §3's "strictly stronger, subsumes K17" withdrawn, `gen_adversarial.py`'s
  two invalid families fixed and re-run, and §5 grown to 13 items.
  §4.4's out-of-lane fuzzer-red report is back-annotated **RESOLVED
  2026-08-15** (fuzzfix, 7e27c19): the cause was `tests/fuzz/fuzz_driver.c`'s
  stale-macro caps array — a test-harness stack smash, 274 → 0 — **not** the
  M4.5 VM path the note's BELIEVED mark attributed it to. The revision's own
  re-measurement then produced **one new defect the panel had not predicted,
  refuting a STRUCTURAL claim of the note's own**: §2a's "the tail recursion
  does not deepen" is true of recursion SITES and false of recursion DEPTH —
  `clo_visit` recurses **Θ(d²)**, 31,377 frames at the parser's 250-paren cap
  against the shipped closure's 253, so the design needs ~7 MB of the default
  8 MB stack there on the PLAIN build (shipped: 192 KB) and overflows under
  asan at depth 210. Not the stack fix (the unfixed prototype measures
  identical depths), and invisible to the suite, whose corpus tops out at
  depth 4. The rewrite lane owes a decision on it (§5 item 12).
  **BUILT 2026-08-15 (k18-rewrite lane, src/ir/dfa.c).** A2 landed as
  designed, semantics unchanged. §5 item 12 is answered ITERATIVE, with the
  decision recorded inline at the item: the prototype's `open[]` array is a
  redundant materialisation of the interned context chain, so dropping it
  turns R23 S3's per-frame entry save into one carried int, makes the
  ancestor-clobber defect inexpressible, and leaves per-frame state small
  enough that the Θ(d²) descent becomes an explicit LIFO of deferred
  branches — after which C-stack depth does not depend on the pattern at
  all. All thirteen §5 items discharged; the landing record, the reproduced
  measurements (corpus blast radius 547 identical / 8 differing, 249 on the
  shape space, 226/226 direction) and the four-file guard corpus are in
  `../dev/known_issues.md` K18.
- `k18_measurements/` — the lane's prototypes, harnesses and generators; see
  its own CLAUDE.md.
- `eng_brep_design.md` — **PROPOSED** ([ENG-BREP], 2026-08-15): the
  BOUNDED-REPEAT EMISSION STRATEGY, written design-first on K18's scheduling
  precedent. Answers Frank's ruled question order — (1) POSSESSIFY, (2) rung
  selection, (3) the unroll factor K — and proposes a ladder: prove no retreat
  can succeed and emit no machinery; else take the §2.5 rung the body admits;
  else one body copy per K iterations plus a counter; with replication
  retained as ground truth. Four refutations, three of them the note's own:
  **the possessification analysis as the plan row states it is UNSOUND**
  (disjointness alone, 117 measured counterexamples, every one a `(a|ab)`-
  shaped body whose iteration can end in two places) and is repaired by
  requiring the body to admit a UNIQUE iteration (one-unambiguous +
  prefix-free), which then survives 5,016 patterns × 260 subjects at 0
  counterexamples; **a zero-width assertion in the follow breaks the
  first-set model** (`[ab]{0,4}\b` on "abc" is (0,0) greedy, (3,3)
  possessive); **the plan row's last-iteration capture derivation for the
  motivating cell is wrong** on 1,799 of 15,036 matches, because a group
  inside a loop keeps the value from the last iteration that ENTERED it —
  repaired to a backward scan, 0 of 15,036, which is the
  reverse-deterministic rung's own argument sharpened; and **third-amendment
  consequence (b) is reported NOT established**, because `src/ir/nfa.c`'s
  `A_REP` arm replicates independently of `emit_vm.c` (what IS established, and
  is new, is that the compiler's own cost on the capture-erased path is
  QUADRATIC in the unrolled count — 0.012 s at N=64 to 2.689 s at N=4000 —
  with the whole count living in the REVERSE DFA, 4,002 states, while the
  forward DFA is 2 states at every N). Censuses on two populations because
  either alone misleads: 17% of bounded quantifiers possessifiable on the
  adversarial `.rxt` corpus, **82%** on a realistic set. K is measured on both
  its curves (gcc −O2 quadratic in copies; throughput advantage exhausted by
  K ≈ 16) and both agree — recommendation K = 8. Discharges the row's four
  ruled validation requirements explicitly, including an
  explicit termination argument (the counter's strict increase, not subject
  progress, is what makes E-2's no-guard-for-bounded ruling safe — checked in
  the emitter's listing and against python3 `re`, 0 divergences). §8 lists
  ELEVEN things NOT measured, headed by the counter loop itself, which does
  not exist. Measurements: `eng_brep_measurements/`.
  **PANELED R24 (2026-08-15/16, `../dev/reviews/2026-08-15-r24-eng-brep.md`):
  the central result HELD and was STRENGTHENED; one design claim was REFUTED
  and five narrowed.** The repaired possessification rule is sound for GREEDY
  quantifiers against **libpcre2** as well as python (0 counterexamples over
  the full 5,016 × 260 family, identical population — closing §8 item 6's own
  disclosed gap from outside), and §2.2's transitive-FOLLOW line — which §8
  nominated as the most likely hiding place for a soundness bug — survived a
  42,336-pair attack at 0 divergences with failing-direction controls. What
  did NOT survive is the note's own **LAZY** extension: greedy, lazy and
  possessive do not agree on the span when the remainder is NULLABLE (316
  cells, both oracles; `a{1,3}?` on "aaaa" is (0,1) lazy, (0,3) possessive),
  because the disjointness argument's follow test is vacuous there and a lazy
  loop stops at the bottom of the exit chain where a greedy one tops out. The
  rule now carries a lazy-only non-nullable-remainder conjunct; the lane's
  probe structurally could not see it (a lazy quantifier has no possessive
  spelling, so its helper returned `None` and half the design's claim left the
  differential silently) and now sweeps both preference families, with a
  committed failing-direction control reproducing the 316. No live
  miscompile — nothing is implemented. Five narrowings applied: `$` in the
  follow promoted to MEASURED-WITH-GATE (0/720 safe, 180/720 under `(?m)`, so
  the gate must be a LIVE check); §3.4's capture derivation regains the
  ZERO-ITERATION clause the prose dropped (42% of its own validated
  population); §2.7's "wrong in the right direction" qualified to CATEGORIES,
  with the structural reason pcrec is exact for caseless (`cls_casefold` folds
  at parse time); §6's instrument disclosed as span/python-only, with the
  panel's captures-aware three-way rebuild confirming it at 15,600 cells; and
  U9 cited where the oracle choice matters. Four measurement discrepancies in
  the rung census all had ONE cause, recorded in §10.1: an uncommitted
  `sort -u` pipeline under a UTF-8 locale, whose collation merges strings
  differing only in punctuation — close to a worst case for a corpus of
  regexes — so every "distinct" figure was an undercount (11 → 15,
  311/111/96 → 398/191/148). Re-derived by two new committed scripts
  (`census_rungs.py`, `probe_cell33.sh`); the latter also found, on
  re-measurement rather than from the panel, that §3.3's "cursor rung" row had
  been measuring the DFA (`(?:ab){0,N}y` is non-capturing, so it requests no
  captures and never reaches the VM). `engine_m4.md` §6.3/§6.4/§2.5 are
  annotated in place (C-F1) — they still stated the refuted
  disjoint-follow-only rule as "designed, built M4.6".
- `eng_brep_measurements/` — the ENG-BREP lane's probes, scratch-compiler
  builder and archived outputs; see its own CLAUDE.md.
- `possessify_impl/` — the [ENG-BREP] POSSESSIFICATION implementation lane's
  own measurements, kept separate from `eng_brep_measurements/` (the design
  lane's territory) so the two are never confused: the corpus census held
  against §7's predictions, and two archived cells (throughput, and the
  capability boundary where the possessified and denied builds part — exactly
  at the denied build's stamped `subject_ceiling`). Its census script sets
  `LC_ALL=C` explicitly and says why: R24 M-F1's collation defect, which this
  lane reproduced in its own test script before the census caught it. See its
  own CLAUDE.md.
- `rungselect_impl/` — the [ENG-BREP] RUNG-SELECT lane's own probes and
  archived outputs (the reverse-deterministic rung, plus the K22 interim
  product guard it landed first as a separate slice), kept separate from
  `eng_brep_measurements/` and `possessify_impl/` for the same
  never-confuse-the-lanes reason those two are separate. See its own
  CLAUDE.md.
- `counterk_impl/` — the [ENG-BREP] COUNTER-K lane's design note, probes and
  archived outputs (the bounded-repeat COUNTER rung: one body copy per K
  iterations plus an iteration counter, replacing full replication), kept
  separate from the three lane directories above for the same
  never-confuse-the-lanes reason those are separate. Its note is DESIGN-FIRST
  and PROPOSED — no engine code exists. **PANELED R25 (2026-08-16,
  `../dev/reviews/2026-08-16-r25-counterk.md`): four blockers, nine majors and
  a second adversarial pass (findings 17-25) — all applied in place. F-1 is
  RULED (D47 ADDENDUM: strict §4.5, K stays ONE per-artifact constant and the
  CLAMP moves whole to plan row [ENG-CLAMP], withdrawing one acceptance cell
  and leaving the rest of the rung untouched). F-2 is RULED too (D47
  SECOND ADDENDUM, 2026-08-17): SETTLEMENT 4 — the frameless forward work
  §7.4 meters gets its OWN bound beside frames and trail, own `rx_info` field
  and own `RX_ERR_*` code, because the meter must see the FULL work; the step
  budget keeps its exact meaning and unit, so every existing pin is untouched
  and the note's `PCREC_STEP_SCALE` apparatus is deleted rather than retuned.
  Its DEFAULT VALUE is deliberately unruled and returns to Frank as a
  one-liner at implementation (the note's §10.5, which also carries the
  addendum's pre-release ABI rider and the PROPOSED names for the new
  surface).** Read the note's PANEL OUTCOME block and then §10.5 before any
  other section. Claims that carry it, and
  where the panel moved them: the counter must be a TRAILED `stv` slot, but for
  a sharper reason than the first draft gave — a plain local is a correctness
  failure (`(a|b){0,4}c`) while a per-frame field is CORRECT at one nesting
  level and dies on the depth-shaped vector nesting would demand; a counter
  loop is preference-equivalent to `vm_opt_chain`'s NESTED optional chain
  rather than to a chained one (witness `(?:ab|a){0,2}?b`, already a measured
  defect in `src/ir/nfa.c`); **K = 8 alone does NOTHING for K22**, whose tower
  is all `{0,2}` counts and so sits below K entirely, and the CLAMP that fixes
  it needs a BOTTOM-UP subtree pass — the ancestors-only product the first
  draft specified parks the tower at 2^17 and leaves depth 35/40 refusing
  (E1), with the corrected arithmetic proved ahead of the code by
  `counterk_impl/probes/clamp_arith.py`; the rung shrinks SIZE and not FRAMES,
  so the endgame cell trades a compile-time refusal for a ~512-byte runtime
  ceiling (E7); and **the owed E-5 one-step-per-loop-ENTRY
  charge is MEASURED NOT TO WORK** — entries and steps are the same number at
  every size (10,001 / 50,001 / 100,001 against 10,001 / 50,001 / 100,001), so
  it halves a crossover that is three orders of magnitude out — **and its
  replacement was refuted in turn**, because that rule's predicate keyed on
  PUSHES while its justification keyed on POPS and `RX_CUT` charges nothing,
  so the revdet scan, `vm_poss_chain` and counter-K's own possessive arm all
  sat in the excluded class of a rule advertising strategy-invariance. The
  redesign charges what the fail label does not see, at the CUT and at
  frameless scan completion, in exact work UNITS rather than a shifted
  quantity — measured at 8x more work uncharged than charged on the
  push-and-cut shapes. The same measurement establishes that the whole debt
  is reachable only on `--engine=vm`: the DFA prefilter means the VM is never
  entered on the shipped path (0 steps, 0.003 s where `--engine=vm` takes
  >120 s). Also records
  the measured finding that possessification does NOT stop a bounded repeat
  replicating (1,939 vs 1,997 lines at `{0,64}`), so counter-K must cover the
  possessive arm — though NOT, as the first draft said, because D47.1's
  possessify-first order is a trap: possessification is an orthogonal modifier
  and claims nothing away from any rung, so the trap would be in DECLINING the
  arm, which is a choice this rung makes (E10). The arm's population is
  measured non-empty on the path that ships (6 of 94 frames-bounded
  quantifiers, `counterk_impl/census_default.txt`), which is the honest
  argument for covering it. See its own CLAUDE.md.
- `k23_impl/` — **ACCEPTED 2026-08-17** ([M4.6c] completed same session; R26 panel + same-day verification, `../dev/reviews/2026-08-17-r26-k23.md`): the K23 design-first
  lane — `../dev/known_issues.md` K23, the exact-minimum ambiguous-
  decomposition explosion. Recommends **MINIMUM-REMAINING-LENGTH (MRL)
  PRUNING**: at every point where the emitted VM commits to a subject
  position it already knows a compile-time lower bound on the bytes any
  accepting continuation must still consume, and a position with fewer bytes
  left is provably doomed, so it is cut before a choice point is pushed. On
  the exemplar `(a{10,20}){10,50}` at 100 bytes the search goes from
  **10,621,636 steps (10.6x the default budget — the reported
  `RX_ERR_STEPS`) to 1**, and the forward scan work — a LANE PROXY for the
  quantity D49's `RX_ERR_WORK` bounds, explicitly not that meter's number —
  from 55,684,363 to **100**, exactly one pass over the subject. On the
  three-level `((a{2,4}){5,10}){5,20}` at 50 bytes it goes from
  **11,906,349,370 steps to 6** with a byte-identical capture vector.
  The note's spine is that the step count has an exact CLOSED FORM
  (`Σ_{s≤n} Comp[m,M](s) − p`, the compositions of every subject prefix into
  parts from the inner range; 9 of 9 measured instances exact), from which
  D27's black-box characterization DERIVES rather than being restated —
  including why the outer maximum cancels — and from which a predictive
  budget-crossing table follows (inner width ≥ 5 crosses 10⁶ at 81-to-100
  byte subjects). Soundness is STRUCTURAL — pruning removes only leaves with
  no accepting descendant, so the first accepting path in preference order is
  untouched and PCRE2 leftmost-greedy captures are exact — and was attacked
  with a **1,059-cell three-way differential (baseline / pruned / python
  `re`, full capture vector) at 0 disagreements**, across strides 1-3,
  subject-length residues and all four greedy/lazy combinations. The two rivals are priced and
  lose on their own terms: MEMOIZATION is sound (a pure DFS backtracker
  cannot revisit a state whose subtree succeeded) and gets 5,100x, but needs
  Θ(points × subject) memory — measured 25,650 B for a 4 KB subject cap, a
  ~21 KB subject ceiling under D19's 128 KB stack, and it is match-time where
  K18's memo precedent was compile-time; ENGINE ROUTING is measured to work
  perfectly (`--no-captures` answers the exemplar instantly at every length
  including 100,000) and is unavailable, because the DFA is capture-blind and
  D44.6 refuses a captures-default pattern. **Seven refutations, three of them
  of the K23 entry's own text**: python `re` does NOT answer instantly — it
  explores the same tree (its measured times track the closed form's node
  counts within 5% across four size steps) and takes **2.8 s** one size up,
  **31 s** two sizes up and **370 s** three sizes up, so pcrec's honest
  refusal is the better behaviour by D22's own bar and K23's justification is
  "answer a cheap question", not "catch up to python"; the boundary is narrow
  in SLACK, not in `n`, and spans ~50 bytes rather than being a cliff; and a
  slice of the entry's stated class is ALREADY FIXED — an exact-count inner
  is possessified today and the outer takes the fixed-stride cursor rung at 0
  steps, so the live population is inner width ≥ 1. Three further refutations
  are the lane's OWN: the prototype silently mis-patched 44 cells (returning
  nomatch where the oracle matched) because it assumed every span-loop scan
  site was an inner loop; the explosion needs a GREEDY INNER rather than a
  greedy outer (a lazy outer explodes identically, a lazy inner costs one
  step); and — found by the panel — the CLAMP ITSELF was unsound at stride >
  1. Cost on the common path is measured with a PLACEBO control (same sites,
  same instruction shape, bound forced vacuous) separating the clamp's own
  instructions from code-layout drift: ±3% at both sparse and full clamp
  density, sign varying by shape.
  **PANELED R26 (2026-08-17, `../dev/reviews/2026-08-17-r26-k23.md`): the
  design core HELD and was STRENGTHENED; the EMITTED FORM was REFUTED and the
  EVIDENCE re-anchored.** The soundness argument is PREFERENCE-BLIND and the
  panel's derivation of that is better than the note's own (minrest bounds
  whether an accepting continuation EXISTS — a language property, hence
  order-invariant), confirmed by measuring the lazy-outer exemplar to 0 steps
  with identical captures; the closed form held exact on three out-of-sample
  instances. What fell: **§4.1's clamp was UNSOUND on any cursor rung with
  stride > 1** — it landed the cursor off the iteration lattice, deleting the
  correct position from the choice set, 5 of 8 subjects wrong on a shape with
  the exemplar's identical baseline step count — and **the 855-cell
  differential was structurally blind to it**, because every body came from a
  single-byte alphabet and at stride 1 the broken clamp and the correct one
  emit equal code. Both fixed: the clamp is lattice-rounded
  (`cap = pos + W·⌊(CEIL − minrest − pos)/W⌋`, soundness re-derived over it),
  the generator gained STRIDE and RESIDUE axes with a committed
  failing-direction control, and the re-run is the 1,059 cells above. Also:
  the forward-work numbers gained a real archived probe and were relabelled a
  PROXY with ruling 5 withdrawn; §9.1's trailing-suffix residual turned out
  to be a CURVE on which **K23 returns at a 16-byte suffix**, and the
  panel-contributed fix — thread the prefilter's match-end window, which
  `rx_search` already computes and discards — is prototyped and MEASURED to
  close it entirely (1 step at every suffix length), now ruling request 6.
  §10 lists eleven things not measured, headed by the reverse-deterministic
  rung, whose iteration boundaries are recovered by a backwards walk rather
  than by arithmetic and so need their own lattice argument. Probes and
  archived outputs in `k23_impl/probes/` and `k23_impl/out/`; see those
  directories' own CLAUDE.md files.
- `design_registry_selectors.md` — SR-9 design proposal for string selectors
  in the construct registry. §2's "one uniform rule" mechanism was REVIEWED
  AND SUPERSEDED by R6 (2026-08-10; not built): the registry can identify a
  doorway and name a module but not always the construct itself (`(?(R)`,
  `\12` depend on later-pattern or running state). Build the `byte + tail`
  design in §7 instead — pending Frank's approval and PC-3.

Maintenance: update this file when files are added/removed or their roles
change.
