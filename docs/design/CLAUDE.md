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
- `anchored_match_unwrapped.md` — [ENG-ABS]'s SECOND MECHANISM, the note of
  record (lane engabs, 2026-08-29; landed): anchored match-here via the
  UNWRAPPED forward DFA. Opened on `[OPT-2]` STEP 2's measurement (the reverse
  pass at ~50 % of the DFA's cost on every matching subject). §2 names the
  THIRD machine's ROLE and derives it as a PARAMETER of the existing subset
  construction rooted at `Nfa.anch_start`; **§3 is the ACCEPT-DISCIPLINE
  IDENTITY ARGUMENT** in four named steps (the wrapped machine's state factors
  as the anchored machine's followed by later starts; accept-pruning deletes
  every later start the instant a `ctx->pos` thread accepts; hence the two last
  accepts coincide; hence the absence of one means no match begins there) plus
  views, seed, zero-length, the prefilter's unsoundness here, and find-all;
  §5.2 rules a cap overflow a SELECTION OUTCOME with the three properties that
  shape has and a `try`/`catch` at the site would not; §6 the `abi` 9→10 four
  sites; §7 the measurement; §9 the checks and the vacuity trap they are built
  against. Its §8 and §10 carry three OPEN items measured and deliberately not
  built (D77): class-table sharing, `ENG_ATTEMPT`'s own match-here form, and
  `[OPT-2]` lever (b).
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
  follow promoted to MEASURED-WITH-GATE (0 safe / non-zero under `(?m)`;
  originally cited as 0/720 vs 180/720 — STALE per the R30 re-run, whose
  numbers are 0/168 and 12/168 on the greedy population, same qualitative
  result, see assertions_design.md §8.8 — either way the gate must be a
  LIVE check); §3.4's capture derivation regains the
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
- `dd13_format/` — the [DD-13] unified pattern-source/test file format:
  Frank's accumulated design inputs (frank_inputs.md, append-only, with
  the OD-n open-decision ledger) ahead of the staged
  requirements→design→panel process. No parser before [DD-13c] closes.
  See its own CLAUDE.md.
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
  **BUILT 2026-08-17 ([M4.6d], the mrl lane); the note gains §14, its BUILD
  OUTCOME section.** The recommendation landed as designed and nothing in §4
  was refuted: `pcrec_minw` in a new `src/opt/mrl.c`, the follow-min threaded
  down `src/gen/emit_vm.c`'s existing walk (closing §9.4 — no restructuring
  was needed), the lattice-rounded clamp folded into the greedy cursor scan's
  own bound, and the prefilter-window ceiling with D51 ruling 2's three
  obligations as code rather than as prose. Exemplar ≤1 step, three-level
  shape ≤1, differential 202,458 cells / 0 divergences over strides 1-3 and
  BOTH ceiling forms. **PREDICTION 6 is ANSWERED IN THE NEGATIVE**: the
  reverse-deterministic rung needs no lattice argument at all, because its
  forward scan IS the walk onto the boundary set — the bound stops the scan
  one boundary early, and E1's substitution failure mode has no spelling
  there. **The E1 CLASS RECURRED ONE RUNG FURTHER DOWN and a D27-BLINDED test
  author found it**: on the counter rung one body copy serves every trip, so
  the compile-time follow-min tops out at `K + residue` — 9 on `(a{1,3}){65}`
  where the truth is 65 — and K23 stayed alive on that shape while the
  differential, the structural checks and the acceptance cell all agreed with
  the bug, because all three were derived from the model the bug was in.
  §4.5's runtime term (read from the trailed counter slot) is the fix. §14.7
  lists what the build corrected in this note: §9.1's `rx_work` sketch is
  superseded by a match-function parameter, and §4.5's "once-per-trip is
  BELIEVED enough" splits into a FREQUENCY that holds and a VALUE that does
  not.
- `mrl_impl/` — the [M4.6d] MRL BUILD lane's own probe and archived outputs,
  kept separate from `k23_impl/` (the DESIGN lane's territory) for the same
  never-confuse-the-lanes reason `possessify_impl/` and its siblings are
  separate from `eng_brep_measurements/`: the design lane's numbers come from
  prototypes that patch already-emitted C, this lane's from the shipped
  compiler. Its step figures are BOUNDS (a doubling search over the emitted
  step budget), not counts, and say so. See its own CLAUDE.md.
- `m46a_impl/` — **[M4.6a] BUDGET CALIBRATION** (2026-08-17): measures the four
  runtime-bound bring-up placeholders (`VM_DEFAULT_STEP_BUDGET`,
  `VM_DEFAULT_WORK_BUDGET`, `VM_DEFAULT_BT_FRAMES`/`VM_DEFAULT_TRAIL_FRAMES`)
  against `engine_m4.md` §4.6's stated method, EXTENDED (§4.6's own text names
  only the step budget) to all four via one generic instrument that reads the
  real shipped counters (RX_ERR_WORK included, D49/settlement 4) rather than a
  proxy. Three layers: the literal corpus+bench reading (finding: every
  committed `tests/bench` THROUGHPUT case compiles `--no-captures`, so it
  contributes ZERO VM-budget signal — the corpus alone underrepresents what
  the bounds must hold against); SCALE, synthetic legitimate large-subject
  probes split by engine mode (a load-bearing distinction found while
  measuring it: `--engine=vm`-forced numbers can be orders of magnitude
  above what the DEFAULT/production path — where the DFA prefilter still
  runs ahead of a capture-bearing pattern's VM, engine_m4.md §4.7 — ever
  sees); and a RATIO re-anchor of `k23_impl`'s retracted 5.24 proxy
  work-per-step number against the real meter (measures 0 — the K23
  exemplar shape is pure backtracking with no frameless-scan or cut site,
  so the retracted proxy has no real-meter analog on it at all).
  Headline finding: an ordinary capturing repeated-alternation pattern
  (`(a|b)+c`-shaped, common in log/token parsing) costs steps and work
  LINEARLY in subject length even on its OPTIMIZED rung (reverse-
  deterministic, O(1) frames) — measured 4,000,002 steps at 8 MB under the
  DEFAULT engine, 4x the shipped step-budget default — and a related shape
  that misses the reverse-deterministic rung (`(GET |POST |...)*X`, whose
  alternatives share a last byte) reaches the shipped frame capacity by
  `subject_ceiling = 256` bytes. See its own CLAUDE.md.
- `k24bisect_impl/` — K24's bisect AND fix lanes (2026-08-17, both closed).
  Bisect: first-bad commit is `1dbb6ce` (the `[M4.4]` API-break commit), NOT
  K18 (the brief's prime suspect, exonerated — K18 never touches this
  pattern's emitted output). Mechanism: once `1dbb6ce` adds same-TU
  `rx_match`/`rx_match_caps`, gcc -O2's partial-inlining pass splits
  `rx_search` into a trampoline plus a separately-placed
  `rx_search.part.0`; the hot-loop instructions are byte-identical
  before/after and all the way to the current tip, but the split's
  layout-sensitivity costs ~25-26% throughput, confirmed causally with a
  `-fno-partial-inlining` control. **FIXED** (`k24_fix_note.md`):
  `__attribute__((noclone))` on `<prefix>_search` in the EMITTED artifact —
  pcrec cannot dictate its users' CFLAGS — emitted at
  `emit_search_head`, the one site serving both the DFA entry and the VM
  hybrid's static prefilter, with assembly byte-identical to the
  `-fno-partial-inlining` control. Case (c) recovered to 391.063 MB/s at its
  historical 1.02x spread with the floor untouched; full gate 10/10.
  Two results in the head-to-head are worth more than the choice: attributes
  on the WRAPPERS (`noipa`/`noinline`) do NOT work, because gcc's
  `pass_split_functions` runs on the callee and ignores callers' attributes;
  and `hot`/`cold` layout steering recovers the number while leaving the
  split in place, with the two combined measuring WORSE than doing nothing.
  The VM audit answered NO (its wrappers call `match_impl` directly, and a
  computed-goto body cannot be outlined at all). See its own CLAUDE.md.
- `m46e_impl/` — **[M4.6e]** (2026-08-17, closes M4.6): the last M4.6
  measure-then-implement pair, `RX_HYBRID_MIN` (engine_m4.md §12 ASK-6) and
  the trie-factored VM alternation switch (§2.2 item 4/§6.4). **BOTH
  MEASURED-NO, neither built.** RX_HYBRID_MIN: the crossover variable is
  match OFFSET, not subject length — hybrid's cost is flat in `n`, VM-only's
  grows with offset (one function call per candidate start position in the
  naive retry loop) — so a length-only `n < RX_HYBRID_MIN` branch cannot
  target the real variable and would regress bench case (i)'s own buffer
  (offset 20, past the 8-12 byte crossover, where hybrid already measures
  65% faster). Trie switch: real chain overhead on disjoint alternations
  (+18% worst-vs-best branch position on a 5-way word alternation) but
  narrow — 6.34% of the corpus's capture-bearing patterns, and neither
  shipped capture-bearing bench shape hits it — declined on D18 against the
  new emitter analysis's own build cost (a D46 stamp+force pair, a
  permanent sabotage row, per `src/opt/CLAUDE.md`'s established price for a
  selection axis). engine_m4.md's own ASK-6, §2.2 item 4 and §6.4 carry the
  annotations in place. See its own CLAUDE.md.
- `altcls_pinned_impl/` — the [OPT-ALTCLS] lane's pinned throughput
  instrument (2026-08-17/18): stage 2's owed quantified-keyword
  re-measurement (CONFIRMED at -7.61%, superseding the design-evening
  probe's unarchived -15.0..-15.6% figure) and stage 3's FIRST-set entry
  guard verdict (MEASURED-NO under every default-routing shape tried,
  including a purpose-built weak-prefilter-coverage arm; a real ~11x win
  confined to `--engine=vm`, a comparability facility, does not justify a
  new selection axis on the default path — `m46e_impl`'s trie-switch
  decline is the exact precedent). The guard/firstset implementation does
  NOT merge, not even denied-by-default; it survives only in git history
  (`a07a87c`, reverted at `8b5acb4`). See its own CLAUDE.md for the
  revisit-when triggers.
- `assertions_design.md` — **PROPOSED, REVISED AFTER R30, and BUILT THROUGH
  ALL FIVE [M6.2] WAVES (A-E, 2026-08-19)** ([M6.1],
  2026-08-18; panel `../dev/reviews/2026-08-18-r30-assertions-design.md`).
  **Read the doc's PANEL OUTCOME block before any section**, which now points
  at the BUILD ANNOTATIONS as well as the panel's findings — waves A-E each
  annotated the sections they built, and **one of those annotations is a
  CORRECTION rather than a landing record**: wave E found that §6.3 rule 3's
  proposed cure ("the VM has to report both positions") was NOT NEEDED,
  because the rule is derived from the DFA artifact's match-here entry and a
  `\K` pattern is VM-forced, so it never has that entry — the VM's is
  anchored by construction and already returns the consumed length. The FOUNDATIONS
  survived adversarial re-derivation unusually well — the D47.5 miscompile
  ("the single best-supported claim in the document"), the `\A`/`\Z` alias at
  1,008 cells / 0 disagreements, `\G`'s mechanism, the `\Z` oracle divergence,
  the `mods` blast radius, and all six probes reproducing — but the
  ENGINE-SPLIT half took **two HIGH refutations**: the spine had **no mechanism
  at all** for assertion context at `startpos > 0` (E1 — a fourth mechanism,
  runtime start-state seeding from `s[startpos-1]` forward and `s[end]`
  reverse, now §3.8; 5 of 10 measured cells differ, and through the find-all
  loop a match is LOST), and `(?m)^`'s routing is not the free inheritance the
  first draft claimed but a permanent move into a **measured O(n²)** class
  (E2 — 3.99x per doubling, 1996x slower than the anchored twin at n=64,000;
  the `memchr('\n')` candidate-start prefilter is now a design element and Q3
  is reframed on that footing, with the DD-7 unpark a Frank ruling). Six
  mediums landed in the same sections: `\z`'s byte-identity argument
  canonicalized against the wrong reference (E3); §3.4 and §3.5 were never
  composed, and composed they **EXCEED** the state cap — 38,009 against 32,000
  (E4); the skip hazard was attributed to `\b`, which by the document's own
  state-identity argument cannot suffer it, making Wave B's proposed sabotage a
  no-op on every pattern that wave lands (E5 — cure and sabotage move to Wave
  C, and all FIVE scan-avoidance mechanisms are now enumerated with individual
  fates, memchr being un-intersectable); the zero-cost accept measurement is
  scoped to ENG_UNANCH and had no `pos == n` column (E6 — the view-axis ×
  class-axis composition rule is now written); `\K` "structurally cannot" was
  overstated, since leftmost-first is a total order and tagged DFAs recover
  exactly such positions (E7 — the conclusion stands, the door is now recorded
  as closed by choice); and §9.3's match-here paragraph was **factually wrong**
  — the DFA's `rx_match` IS `rx_search` plus a start filter — which withdrew
  Wave D's owed differential and exposed a live `\K` hazard in the filter and
  the returned length (E8). Three provenance findings are this lane's own
  failures and are recorded as such: a header hand-written to IMITATE the
  archiver (M7 — "worse than absent provenance"), the locale-collation
  `sort -u` undercount reproduced verbatim after reading the entry that named
  it (M6 — 1030 true, 609 reported, **421 silently merged**; every headline
  number identical on the corrected corpus), and an unverifiable `-Wswitch`
  hand experiment (M8). All now committed tooling. Four instruments added
  (startpos-context cells, the `(?m)^` cost curve, the `-Wswitch` alarm, the
  `LC_ALL=C` harvest); the state prototype gained a SECOND disclosed fidelity
  gap running opposite to the first (M2 — it minimises a LANGUAGE where pcrec
  tracks thread PRIORITY, so `\w{3,16}`'s 4.50x was an artifact and the >2.00x
  count drops to one, while the 4.75x headline SURVIVES on a pattern whose
  baseline is verified against pcrec exactly).
  **FOCUSED RE-CHECK (both critics resumed against the revision): 7 of 8 engine
  discharges and 5 of 6 measurement ones held; N1 is a SECOND defect and the
  sharpest thing in the whole round** — §3.8 filled mechanism 4 at three of the
  FOUR places it is needed, and the missing one is the reverse machine's
  TERMINATION boundary: at `pp == startpos` the loop breaks
  (`emit_dfa.c:1056`) before `s[startpos-1]` is read, so a LEADING `\B`
  evaluates blind and, on the document's own cell, the forward pass finds the
  match and the reverse pass THROWS IT AWAY. `\b` is safe by accident (its
  blind assumption coincides with its truth condition), so a trailing-only or
  `\b`-only sweep reports clean against a design that loses matches — and the
  lane's OWN forward fix is what made the reverse defect reachable. Now
  §3.8.3.1, with an invariant covering every `sfound` writer (the reverse skip
  included) rather than a one-line patch. Also: the Q1 withdrawal had been
  applied at §11 while §5.2 still carried the withdrawn recommendation verbatim
  (M5 PARTIAL — a live internal contradiction), §3.7.1's table came from a
  different run than the archive it cited (N2), and the `memchr('\n')`
  mitigation was justified on the quadratic arm when its real benefit is the
  LINEAR non-crossing case (N3 — a non-crossing arm added to the probe measures
  85-185x, and Q3(b) is re-grounded on it).
  **N1 VERIFIED AND CLOSED by a focused re-check**, which then found **N9** in
  the fix itself: the reverse loop has TWO exits, and §3.8.3.1's first wording
  ("peeled epilogue … below that break") would have run on the DEAD-STATE exit
  at `emit_dfa.c:1059` — writing `sfound` at a position the walk never reached
  AND indexing an accept table with a negative state, K27's out-of-bounds class
  in emitted code. The accept is now attached to the boundary break itself, so
  both are unreachable by construction. The same pass sharpened the `:1044`
  rendering: the emitter's `if` there is COMPILE-time, so the artifact carries a
  bare unconditional `sfound = pp;` inside the skip block — worse than the
  design's first rendering showed. Two instrument near-misses are now recorded
  in the prose rather than in driver comments, because each would have produced
  a quotable number: an all-'a' subject that measures the `(?m)^` curve as FLAT
  (and would have confirmed the struck sentence), and gcc -O2 deleting a repeat
  loop so a memchr arm read 0.000000 over 200 searches — the second the more
  dangerous, since an infinite ratio reads as a STRONGER result for the
  mitigation it supports. Original content below.
- `assertions_design.md` (**pre-R30 summary, retained for history — read the
  R30 entry above first; the "exactly three" spine below is REFUTED by E1 and
  the `(?m)^` cost claim by E2**) — the module
  `assertions` design gate — `\b` `\B`, `\A` `\z` `\Z`, `(?m)` multiline
  `^`/`$`, `\G`, `\K` — answering the row's seven questions before any [M6.2]
  code. Its spine was that every construct is exactly one of three things, and
  the engine split follows from which: an ABSOLUTE POSITION TEST (`\A`, `\z`,
  `\G` — free), a NEXT-BYTE VIEW (`$`/`(?m)$` forward, `\b`'s right side —
  folds into the transition and accept tables BY BYTE CLASS), or a
  PREVIOUS-BYTE CONTEXT BIT (`\b`'s left side, `(?m)^` — folds into the DFA
  state identity); the forward and reverse machines swap which is which, and
  `\K` is the one construct that is none of them (path-dependent reported
  start, so VM-only — which `src/parse/registry.c:365` already ships as
  `VM_ONLY`). **Its most important finding is a live landmine: D47.5's gate is
  built and shipping and is SCOPE-BLIND** — `src/opt/possessify.c:579` captures
  `cx->mods.multiline` once, after the parse, so `(?m:a{0,4}$)` and
  `(?m)a{0,4}$(?-m)` would EXEMPT a multiline `$` and miscompile the day the
  `m` letter is accepted, and D47.5's own recorded test obligation tests the
  one row the shipped code gets right. The proposed cure resolves multiline at
  PARSE time onto the node, and the note states the INVARIANT ("scoped modifier
  state is resolved at parse time onto the node; no post-parse pass reads
  `cx->mods`") as the requirement, separately from the SPELLING. On the
  spelling it recommends a distinct node kind over a flag and records that the
  manager leans the other way, deciding it on a measurement rather than taste:
  a new `AKind` enumerator produces **15 `-Wswitch` warnings across 6 files**
  (probe enumerator added, tree rebuilt, warnings counted, edit reverted) where
  a new struct field produces none — so a flag's failure mode IS the silent
  bug being fixed, while a node kind's is a build diagnostic at 15 of 19 switch
  sites. **The lane then found that this is not a new convention but pcrec's
  OWN named rule**: `src/opt/mrl.c:18-24` (R26 V7) already mandates
  `default:`-less exhaustive switches so that "a node kind added after this
  file is written must be a COMPILE ERROR here… exactly the alarm the analysis
  cannot otherwise raise", and `src/opt/altcls.c:405` cites it as "mrl.c's
  rule" — a description that fits `possessify.c`'s situation word for word. It also proposes making the invariant STRUCTURAL: after the fix
  `cx->mods` has zero legitimate consumers outside `src/parse/`, so moving
  `ModState` out of `Ctx` turns "no post-parse pass reads it" from a discipline
  rule into a compile error, which is the durable answer to "which other
  modifiers need this notice" — measured NO today (every other modifier already
  resolves at parse position, `parse.c:80/105/117/164/179/494/631/693/908/910`)
  and un-reachable in future by construction. **Two premises were re-measured rather than inherited and one was
  refuted**: `(?m)` already refuses with module `assertions`
  (`src/parse/mod_modifiers.c:280`), not `modifiers`, so question (vii) needs
  no re-attribution work at all. `\A` and `\Z` turn out to be EXACT ALIASES of
  the shipped `A_BOL`/`A_EOL` nodes, so they are parser rows with no engine
  work; `\z` needs one more closure view, interned only when it differs, so a
  `\z`-free pattern's artifact is byte-identical by construction rather than by
  a flag. State-budget claims are MEASURED two ways per the row's requirement:
  EXACTLY in pcrec (the word-set alphabet refinement costs at most +1
  equivalence class on 38 realistic patterns and +2 on 574 `.rxt` ones;
  largest `states × ncls` after word+newline refinement is 48,012 against a
  2,000,000 cap) and by a calibrated PROTOTYPE for the state count `\b`'s
  context bit costs (minimised ratio 1.00x/1.11x/4.75x, reproducing pcrec's own
  count on 29 of 33 assertion-free arms, with its one fidelity gap — no
  priority pruning — stated in the file). The hot-path cost of the
  `states × ncls` accept table those views force is MEASURED AT ZERO on D11's
  own shape. Also reports two things it does not own: **ENG_ATTEMPT's
  `for (start = startpos; start <= start_max; start++)` is an external
  byte-arithmetic advance loop in shared emitter code** that D58's "the hot
  path has NO external advance loop" rationale does not cover (true of
  ENG_UNANCH only), which this module makes more prominent because `(?m)^` and
  `\G` both route patterns onto that engine; and **python3 `re` is the WRONG
  oracle for `\Z`** — python's `\Z` is PCRE2's `\z`, measured 1 of 7 cells
  disagreeing in the silent direction, so Wave A's expectations must come from
  the libpcre2 differential. DD-4 is answered without `engine_m4.md` §7.3's
  wrap toggle: ENG_ATTEMPT already emits the un-self-looped shape and `\G` is
  `start_max = startpos`, a third value for a string the emitter already picks
  between. Delivers a five-wave [M6.2] structure (A `\A`/`\z`/`\Z` + the gate
  refactor while it is provably a no-op; B `\b`/`\B`; C `(?m)`; D `\G`;
  E `\K`), EIGHT open questions for Frank — headed by whether the NEWLINE
  CONVENTION axis (DD-11) is declared now on `--encoding`'s per-pattern
  refuse-by-name precedent, and including a recommendation that D47.5 gain an
  ADDENDUM at merge (its live-branch requirement is necessary but not
  sufficient; this lane deliberately edits neither `../dev/decisions.md` nor
  `eng_brep_design.md`) — five BELIEVED claims each with its refutation
  experiment, and seven things it does not measure headed by the REVERSE
  machine's state cost. Measurements: `assertions_measurements/`. Unpaneled —
  a D6 adversarial panel reviews it before [M6.2] starts.
- `assertions_measurements/` — the [M6.1] lane's five probes, its archiver and
  the archived outputs; see its own CLAUDE.md. Some instruments read pcrec
  itself and some are prototypes or oracle comparisons, and the design doc
  marks every claim accordingly. Every file in `out/` is written by
  `probes/archive.sh`, so one provenance header (probe, probe's own commit, run
  commit + branch + tree-clean, date, python3/libpcre2/gcc versions) covers all
  of them.
- `atomic_groups_design.md` — **PROPOSED, PANELED (R31) AND REVISED** ([M6.4.1], 2026-08-22; panel `../dev/reviews/2026-08-22-r31-atomic-groups-design.md`). **Read the PANEL OUTCOME block at the top before any section** — it now covers
  the panel AND its focused re-check, which closed E1-E8 and raised two new
  findings against claims the first revision had introduced (the lift needed a
  LAZY carve-out as well as a nullable one — 7 of 8 cells miscompiled — and
  `vm_cuts` had to be context-threaded because `struct Ast` has no parent
  pointer). The two central results SURVIVED and came out stronger — the hybrid hazard is now measured on the LIVE prefilter at **114 cells of silent match loss** — while nine HIGH findings hit how they land, and every section they touched carries its annotation inline. What moved: SR-8 is now BUILT by this module (M-1/D67, reversing §8); RULE 3's possessive-rung lift gained a NULLABLE carve-out (it would have HUNG the emitted matcher), a measured FIVE-path dispatch table, and a shared `vm_cuts()` predicate for the emitter and four pre-passes; H3's fix is one predicate at THREE sites, not one at `:4351` (the first form moved the STAMP and not the code, so the design's own check would have agreed with the bug); the structural checks now match CALL SITES and a SECOND CUT SPELLING this lane found while fixing E2; the possessify-under-cut evidence was rebuilt from 59 refutable cells to **10,504**; RULE 1 is re-grounded on D62's own principle after its cited precedent turned out to say the opposite. It also opened **K29** (a pre-existing counter-rung defect) and the D27 goal facts lost their alphabet leak. Original scope:
  module `atomic-groups`, `(?>...)` plus the possessive spellings `*+ ++ ?+
  {n,m}+` as SEMANTICS. Its three load-bearing results, each with an
  instrument: (1) `vm_cut`'s no-trail-rewind invariant is **proof-INDEPENDENT**
  — the argument that licenses it never mentions possessify's §2.2 verdict —
  so the [ENG-BREP] cut is reusable UNCHANGED for an unconditional cut, and a
  prototype on the emitted machinery reproduces PCRE2 on 14/14 rows, 9 of them
  non-vacuous; (2) **THE HYBRID HAZARD IS REAL AND MEASURED**: the DFA
  prefilter necessarily runs the UNCUT language, and while its REJECTION and
  its START survive that (0 violations in 17,640 cells), its span END does
  NOT — **122 refuting cells** — and today's emitter feeds exactly that end to
  the VM as the [M4.6d] MRL pruning ceiling, so a one-predicate change at
  `src/gen/emit_vm.c:4351` is the module's one mandatory emitter fix; (3) the
  FREE DISCHARGE (an atomic/possessive whose body already satisfies
  possessify's §2.2 proof is a no-op, so the pattern stays DFA-eligible) is
  MEASURED sound at **0 violations over 532 positive-verdict patterns** with
  its own four controls — narrowed by R31 E7 to the possessive spellings only,
  the plain-group arm deferred for want of evidence. Also: `A_ATOMIC` is a NODE KIND rather than a flag on
  the measured ground that a new `AKind` raises 15 `-Wswitch` diagnostics
  where a struct field raises none — and two of the fifteen are the
  `src/opt/revdet.c` sites where an atomic node must DECLINE or the module
  ships a miscompile (`rd_node` CLEARS `Ast.possessive` on the reversed copy
  the emitter walks, `revdet.c:178-179`). The full Berglund cut construction is
  CHARTERED as follow-on row `[ENG-CUT]` with a size estimate, not built.
  Measurements: `atomic_groups_measurements/`. A D6 adversarial panel (R31)
  reviews it before [M6.4.2] starts; §14 is the document's own list of where
  to attack.
- `atomic_groups_measurements/` — the [M6.4.1] lane's **twelve** probes (four added across the R31 revisions), its
  archiver and the archived outputs; see its own CLAUDE.md. **Every instrument
  here reads a compiler that cannot compile the construct it measures**, so
  every in-pcrec arm works through a proxy (the atomicity-erased twin, or the
  possessify verdict stamp `RX_VM_STRATS`) and the design marks each claim
  MEASURED / PROTOTYPE / STRUCTURAL accordingly. Every file in `out/` is
  written by `probes/archive.sh`. The `-Wswitch` number is a **re-run** of
  `assertions_measurements/probes/probe_wswitch_alarm.sh`, not a rebuild.
- `backrefs_design.md` — **PROPOSED, REVISED AFTER R32** (NOT approved at
  4cd461f: eight HIGH findings; read the PANEL OUTCOME block at the top and
  §16's what-changed table before any section). The [M6.5.1] design gate in
  front of
  module `backrefs` (numeric `\1`..`\99` with PCRE2's octal disambiguation,
  the `\g` and `\k` spellings, `(?P=name)`, and `(?J)`/DUPNAMES, which the
  [M6.5] row rules is IMPLEMENTED by this module rather than merely
  re-decided). Unpaneled at time of writing — R32 is its D6 panel, before
  [M6.5.2]. Its spine is one fact: a backreference is not a class-membership
  test, so caselessness cannot fold away at parse time (D23 boundary 1 comes
  due), the DFA cannot carry it, and the encoding seam gains its SECOND
  residual entry. Load-bearing results, each measured: **PCRE2's group count
  is ASYMMETRIC** — `\1`..`\9` see the whole pattern (`\1(a)` compiles) while
  `\10`+ see only what precedes them (`\10(a)..(j)` is the octal byte 0x08),
  so an implementation with one count is wrong in one direction and no
  groups-before test notices; **the caseless compare's fold is EXACTLY
  pcrec's own 52-byte `cls_casefold` set**, verified byte for byte on both
  sides, so the seam entry reuses a table rather than choosing one; **the
  finite-language expansion's only possible customer is a `--no-captures`
  build**, because a backreference pattern is capture-bearing by construction
  and `forces_captures` already sends it to the VM — measured on the shipped
  compiler, and the reason the expansion is CHARTERED AS A FOLLOW-ON rather
  than shipped here, with the DECLINE boundary bisected at `|L(G)| = 10,525`
  (7.1 MB of emitted C); **the backref-erased prefilter is a sound superset
  but reports a DIFFERENT SPAN on up to 2,525 of 4,000 subjects**, so
  `engine_m4.md` §6.1's exact-window hybrid is unavailable and VM-only search
  costs one to two orders of magnitude (6.2x-130x measured); and **libpcre2's own `PCRE2_INFO_NAMETABLE` is sorted
  (name asc, number asc)**, which is the [M6.5] row's ruled `rx_info.groups`
  layout, so pcrec reproduces a precedent instead of inventing a convention.
  Two findings the panel should attack first because they change code outside
  the module: `tests/codegen/run_codegen_tests.sh`'s [M5-SEAM] check
  **forbids** a residual entry from appearing in any engine body, which is
  exactly where a backreference compare must be called from (§4.4 proposes a
  per-ENTRY `engine_callable` declaration, `next_pos` unchanged); and
  `src/opt/select_engine.c`'s `--engine=dfa` override advises `--no-captures`
  for every capture-bearing pattern, which for this module's whole population
  is advice that does not help — a PRE-EXISTING defect, reproduced on the
  shipped binary with `\K` (§6.2). Measurements: `backrefs_measurements/`.
  **What R32 refuted, because a reader of the first draft must not trust their
  memory of these sections**: (E1) §3.2's central premise — "a non-UNSET slot
  pair is a capture" — is FALSE while a group is re-entered, since
  `emit_vm.c:3813-3835` publishes START at open and END at close, so the two
  slots belong to different iterations; the design's OWN archived cell S3
  refuted it and two shapes underflow a `size_t` in emitted code. §3.2 is
  rewritten as **PUBLISH-AT-CLOSE** (a per-group pending slot, the pair
  published together), measured over 5,808 cells at 138→0 divergences and
  40→0 reversed spans, with a backref-free control arm that is 0/0 in both
  disciplines — which is what lets the fix be scoped to referenced groups and
  keeps §11.3's byte-identity claim. (E2) the erasure is a superset only for
  an **assertion-free** referenced group (6/10 control cells are false
  negatives otherwise), so §7.4's chartered nomatch-only prefilter gains a
  gate it cannot ship without. (E3) a digit run beginning `8`/`9` is **always
  decimal** — no octal reading exists — and references above `\99` are real.
  (M-1/C1, found by this lane against its own design) `forces_backref` would
  have been a third exception covering TWELVE rows to a check whose text says
  the second builds SR-8; **D67 rules SR-8 built in [M6.4.2]** and §6.1 is
  rewritten to node stamping. (C2/E7) the proposed complement check shared a
  source with its subject; (C3) two corpus files were marked python-verifiable
  in the direction that loses the oracle; (C4) no sabotage row covered the
  wrong-answer mode; (C5) the `built` column is asserted by nothing today.
  All five §15 ASKs are RULED. §16 tabulates the rest.
- `backrefs_measurements/` — the [M6.5.1] lane's eight instruments, its oracle
  helper, its archiver and the archived outputs; see its own CLAUDE.md.
  **No instrument here reads a backreference through pcrec, because pcrec
  cannot compile one** — the in-pcrec arms measure a SEPARATE AXIS on patterns
  pcrec can compile (the prefilter axis, the fold axis, the expansion's
  OUTPUT), which is what makes them exact rather than modelled. Borrows
  `eng_brep_measurements/probes/pcre2_ctypes.py` rather than copying it, and
  adds compile-error NUMBERS, the name table and three option bits whose
  values are asserted BEHAVIOURALLY at import. Every file in `out/` is written
  by `probes/archive.sh` (R30 M7's rule, inherited: the archiver is the only
  writer — and R32 D1/C14 found every header stamping "module `assertions`",
  now re-scoped with all NINE outputs re-archived in one batch). Its own
  CLAUDE.md lists **NINE defects across ten instruments** — five found by this
  lane, four by R32 — every one producing confident wrong output rather than
  an error, and the two shapes they fall into: a population or filter that
  does not contain the thing being measured (seven), and an instrument with no
  way to FAIL (two). **The tenth entry is the one worth reading**: E1's
  counterexample was already archived here as cell S3 from the first day; no
  probe was wrong, nothing compared the archive to the design's claim.
  `probes/simvm.py` — the R32 critic's own simulator, ADOPTED rather than
  rewritten so the lane cannot soften the instrument that refuted it — and
  `probes/probe_publish_discipline.py` make that comparison mechanical.
- `la_d27_extract.md` — the [M6.6.3] blinded author's extract of
  lookaround_design.md §2 + §7 + §10.1 (the construct table, the goal-facts
  list, the population), cut by the manager at build completion so the D27
  cell can allow it without allowing the design's implementation sections.
  Regenerate only by re-cutting; never edit independently of its source.
- `lookaround_design.md` — **PROPOSED, PANELED (R33) AND REVISED**
  ([M6.6.1], 2026-08-23; panel
  `../dev/reviews/2026-08-23-r33-lookaround-design.md`). **Read the PANEL
  OUTCOME block at the top before any section.** Five HIGH, thirteen MEDIUM
  and seven LOW — **every one accepted as a design edit, none refuting the
  mechanism.** §3's lowering, §4's seam entry, §5's prefilter ruling and §6's
  replacement table all held; what fell is a scoping the lowering never
  stated, one measurement METHOD, one wave's landing bar, an unbudgeted arm
  count, and a rule that was a substring test. **C1-1 is the one worth
  reading**: `v->fmin`/`v->fdyn` are baked into a body's prune bound as a
  LITERAL and a lookahead's follow OVERLAPS its own body, so an unscoped body
  makes `(?!(a+)b)a+b` on `"aab"` answer **(0,3) — a FALSE MATCH** where PCRE2
  says nomatch; `vm_atomic` scopes both terms but its own header attributes
  that to THE CUT, and §3.6 derived the non-atomic form BY DELETING THE CUT.
  Now §3.2.1 states the rule as a property of the OVERLAP, S-LA17 defends it,
  and the mechanism is reproduced on this build (3 of 3 bodies' bound literal
  moves with the follow). **Two findings came back STRONGER than filed,
  because implementing the fix measured something the critic had not**: this
  lane's first answer to C1-1's lookbehind half was a simplification (a
  fixed-width body has no quantifier, so the hazard cannot arise behind) that
  is **MEASURED FALSE** — `a{3}` is fixed-width by §2.5's own rule AND takes a
  cursor rung whose bound moves 1→3 — and C3-1's "inert today" is refuted by
  its own fix, since the substring test also missed **seven non-leading bare
  `(?m)` blocks** C3 did not name, moving the driver population
  270/8,495 → **263/8,260**. C2-1 refuted §5.8's METHOD (pcrec's unanchored
  forward DFA is ACCEPT-PRUNED — every accepting state a dead sink — so it is
  the leftmost-occurrence automaton, not `Σ*·L`, and it UNDER-counts:
  `a|bc` emits 3 where `|D(Σ*·L)|` is 4, inside this module's own shipped
  population); §5.8 now reports the emitted number as a LOWER BOUND beside a
  self-checked subset construction, 6 product rows move, and **the conclusion
  survives** (64 non-control rows, 0 over the cap). C2-2 found D65 flips
  `built` on the PORT and not the emitter, so waves B and C are FOLDED; C2-3
  budgeted the **23 `case A_ATOMIC` sites in 10 files** the first version put
  at four, including the two predicates §5.6's ruling depends on. Original
  content below.
- `lookaround_design.md` (**pre-R33 summary, retained for history — read the
  R33 entry above first**) — the
  design gate in front of [M6.6.2], module `lookaround` — the last module of
  M6. Covers `(?=` `(?!` `(?<=` `(?<!`, the non-atomic `(?*` `(?<*`, and
  PCRE2's twelve alpha-assertion spellings. R33 is its D6 panel; §12 is the
  document's own list of where to attack, written before the panel rather than
  after. Its spine is that a lookaround is **a sub-match whose result is a
  verdict and whose position is discarded**, so unlike a backreference it needs
  no new operation and unlike an atomic group it changes no quantifier's rung:
  it is `vm_atomic`'s shape plus a saved cursor, and **§3.2's emitted C is the
  shipped emitter's own output for `((?>ab)c)` with the two added lines
  marked**, which is the strongest form that claim can take. Load-bearing
  results, each measured: **the negative form needs NO capture snapshot and no
  position slot**, because `RX_PUSH` records the cursor and `trail_depth` at
  entry and the fail label restores both before jumping (both macros quoted
  verbatim) — the cheapest finding in the module and the reason §3 is short;
  **PCRE2 10.46's lookbehind has TWO preference orders that disagree with each
  other** — top-level branches in WRITTEN order, step-back lengths within one
  branch **LONGEST FIRST** regardless of how the alternation is written — which
  is exactly why the design ships the **fixed-per-top-level-branch** subset
  (where the length loop has one iteration and the two orders coincide) and
  refuses variable-length with pcrec's own reason; the **caps are two different
  numbers and one is not a property of the construct** (`max_varlookbehind`
  bisects to a default of **255**, err 200 past it, and does not apply to a
  fixed body at all, whose own ceiling is 32759 / err 120); **`\K` in a
  lookaround is err 199** and the extra-option bit that lifts it is **0x40**
  (derived by sweep after the documentation-order guess 0x8000 measured
  nothing); **captures are retained by a positive lookaround, discarded by a
  negative one and unset when a positive one fails after partially capturing**,
  with libpcre2 and python agreeing on all 27 cells; and the **back-step is the
  [M5-SEAM]'s THIRD residual entry**, which `enc.h`'s own "road not taken"
  paragraph predicted by name — so this module is the [M6.5.2] entries-table
  refactor's first validation and needs **zero interface change** to it (§12
  P-1 makes that falsifiable rather than a compliment). On the prefilter it is
  the **atomic-groups case, not the backrefs case**: erasing a lookaround is a
  one-line superset proof, H1 (rejection) and H2 (start) hold at **0 violations
  over 45 cells**, and H3 (window END) fails at **8** — all eight in planted
  controls once H3 is measured in its SHARP anchored-at-the-true-start form
  rather than the naive leftmost-vs-leftmost one, which reports 12 — so the
  prefilter SHIPS and the MRL ceiling is dropped by one predicate read at
  **three** sites (R31 E3's finding consumed, not repeated). The ruling is
  necessary rather than precautionary: **the hazard coexists with a live
  `prefilter-window` ceiling on 16 of 30 swept shapes**, measured on the
  shipped compiler's own stamp. **THE DFA ANSWER IS NOT THIS
  MODULE'S** (Frank, 2026-08-23): the one-character FOLD is ruled out as a
  duplicate code path, the general form is chartered as **`[ENG-LOOK]`** —
  lookaround by PRODUCT CONSTRUCTION, `(?<=L)` at p being `subject[..p] ∈
  Σ*·L` — and §5 hands that row its three stated prerequisites instead. One of
  them is new measurement this lane owed nobody until the ruling: **the
  component-automaton SIZES, read off the emitter's own array dimensions**
  after compiling each body alone, since pcrec's unanchored forward DFA for
  `L` IS the `Σ*·L` recognizer. Every assertion-expansion and
  enumerable-real-lookaround body is **2-25 states**; the product bound clears
  the 32,000 cap on **64 of 64 non-control rows** while the deliberately-
  extreme controls put **18 of 62** over it, so the zero is a result and not a
  small population. **§6 IS THE OTHER HALF OF THAT RULING AND IS THE SECTION
  TO READ FIRST**: every member of the assertion family IS a lookaround, so
  [DD-11]/D66's expansions (`\b` ≡ `(?<=\w)(?!\w)|(?<!\w)(?=\w)`, `(?m)^`
  ≡ `\A|(?<=\n)(?!\z)`, `\Z` ≡ `(?=\n?\z)`, …) are this module's own
  design examples — all nine verified equivalent at **972 cells / 0
  disagreements**, with the `(?!\z)`-dropped control firing at 4/108 — and
  **every one of them compiles under the fixed-per-branch rule**, because the
  only variable-width body in the family sits inside a lookAHEAD where there
  is no width rule (the same body one direction over would be refused; §12
  P-12 attacks the coincidence). Textually substituting them into the
  assertions module's shipped corpus is a **CORPUS GENERATOR, not a product
  mechanism** (the PRODUCT-side substitution is [DD-14]'s subroutine-call
  primitive, ruled and sequenced), and it converts **8,495 of that corpus's
  10,120 libpcre2-verified cells** into a lookaround corpus with a
  two-comparison self-oracle — `A == B` (pcrec's two lowerings of one
  language) *and* `A == C` (libpcre2), neither sufficient alone. §6.3 costs
  all five qualification rules separately; the expensive one is scoped `(?m:`
  at 24 blocks / 871 cells and the character-class one costs **0 on this
  corpus and is still required**. §6.4 states what the lowering owes [DD-14]
  and shows §3 already provides it: every lookaround body is a self-contained
  sub-program with ONE entry and ONE success exit, its state in trailed slots
  rather than C locals. §9.2 accordingly **WITHDRAWS** the fold-based positive
  control the first revision proposed and keeps the ordinary refusal control,
  recording that a control built on a mechanism that does not exist would have
  gone green by construction. Two of the charter's own premises
  were **refuted** and §7 says so: python `re` ACCEPTS quantified lookaround
  (all fourteen forms, agreeing with libpcre2 on all nine behavioural cells)
  and AGREES with libpcre2 on every capture cell — marking either
  `# pcre2-only` would throw away a working oracle, which is R32 C3 in the
  other direction. **A third was refuted by the charter's own 2026-08-23
  addition**: python is warned to choke on "several expansions", and it takes
  ALL NINE, because the variable-width lookbehind it rejects appears in none
  of them — so the expanded corpus stays python-verifiable. It also reports a **D26 tier-2 registry defect this module
  owns**: all twelve alpha spellings answer *"requires module `verbs`"*,
  because the `(*` doorway is one `FIXED` row while the names live in
  `mod_verbs.c` — the same defect one doorway over from the one
  `registry.c:692` already records for `(?*`. Four ASKs for Frank (§14), none
  of them ruling contradictions. Measurements: `lookaround_measurements/`.
- `lookaround_measurements/` — the [M6.6.1] lane's TEN probes, its oracle
  helper and its archiver; see its own CLAUDE.md. **No instrument reads a
  lookaround through pcrec, because pcrec cannot compile one** — every
  in-pcrec arm measures a separate axis on patterns pcrec CAN compile (the
  refusals and registry rows, the ERASURE that would become the prefilter, the
  assertions module's already-shipped `\b` and `(?m)^` artifacts). Borrows
  `../backrefs_measurements/probes/br_oracle.py`, which borrows
  `pcre2_ctypes.py` — two levels, no second binding. Its `out/CLAUDE.md`
  carries **NINE instrument defects the lane found by running its own
  probes**, every one producing a confident wrong number: **two constants that
  are wrong at the value a reader would take from the documentation's list
  order** (`PCRE2_INFO_MAXLOOKBEHIND` at 23 read a different field and would
  have made a whole column zeros; the `\K` extra-option bit at 0x8000 did
  nothing), a budget axis made vacuous by PCRE2's own required-code-unit start
  optimization, a `(?m)` applied to one arm of a self-oracle only (which would
  have published "the D66 expansion is not equivalent to `(?m)^`" as a
  finding), a tail set blind to the very defect a sibling axis found, two
  oracles compared across a report-shape difference, and — the one worth
  reading — **a sweep population that could not contain a qualifying shape**,
  reporting "0 qualifying" over a space in which 0 was the only possible
  answer. The reachability guard that replaced it is what turned that zero
  into the 16-of-30 the design's prefilter ruling rests on — **and the ninth
  defect is that same shape recurring in a SECOND probe of this lane's own**,
  the `[ENG-LOOK]` sizing sweep, whose first "0 over the cap" was over a
  population three orders of magnitude below it. It was found by applying the
  sixth defect's lesson rather than by a panel, which is the argument for
  writing a reachability guard into every sweep rather than into the one that
  has already failed.
- `sr_d27_extract.md` — the [DD-14] blinded author's extract of
  `subroutines_design.md` §2 + §3 + §10.1 (the construct table, the measured
  semantics, the oracle rules and the population) plus the post-approval
  rulings that touch this module (D71 items 1/4/5, D73, the [DD-14.LB]
  amendment), cut by the manager ahead of the D27 cell so it can allow this
  file without allowing the design's implementation sections (§§1, 4-9,
  11-14: the lowering, the linkage, the call graph, `W`, the gate, the
  sabotage rows). Regenerate only by re-cutting; never edit independently of
  its source.
- `subroutines_design.md` — **PROPOSED, NOT YET PANELED** ([DD-14]'s design
  gate, 2026-08-23; module `recursion` — subroutine calls `(?1)` `(?+1)`
  `(?-1)` `(?&name)` `(?P>name)` `\g<1>` `\g<name>` `\g'1'` `(?R)` `(?0)`, and
  two spellings the charter's list did not have, **`\g<0>` and `\g'0'`**).
  Its spine is that a call is **the same pattern text run again with the
  capture state put back on the way out**, and four measurements force the
  lowering. **The callee WRITES the capture slots and the RETURN restores
  them** — seen live through `pcre2_set_callout` reading the ovector INSIDE
  the call, because the after-the-fact state cannot tell "restored" from
  "never written". **The callee INHERITS the caller's captures** (a `\1`
  inside a called body sees the caller's group). **The call is BACKTRACKABLE
  on 10.46** (atomic before 10.30), measured on a body reachable only by the
  call with four atomic controls refusing — so the return cannot be an
  `RX_CUT`. And **PCRE2 10.46 refuses NO left recursion at compile time**:
  error 140 is *"invalid escape sequence in (\*VERB) name"*, every
  left-recursive shape compiles, and the match-time `rc -52`'s obvious reading
  is **refuted** — `^(a|(?1)a)$` performs 199 nested recursions all entered at
  offset 0 and MATCHES, so a same-position guard would be a miscompile.
  Consequences: **a call IS a resume frame** (§5.2 derives the clobber bug that
  kills the plan row's separate call-stack array); the capture restore is over
  a compile-time **slot write set** — every family, per emitted instance —
  stored **in the trail itself** by a trailed
  self-write, EXCLUDING slots 0 and 1 because **`\K` is measured NOT to be
  restored** and pcrec spells `\K` as a write to `RX_SLOT_WHOLE_START`; the
  emitted function gains a **SECOND indirect jump**, amending
  `emit_vm.c:9-12`'s stated one-`goto *` invariant. The charter's
  "once-emitted-with-two-linkages" **collapses** when written out, leaving
  SPLICE / HYBRID / CALL, PROTOTYPE-measured at **298.6 / 87.6 / 80.1** emitted
  bytes per call site (least-squares over k = 0…16), with **CALL smallest at
  every k and SPLICE fastest** — which at one call site (197 bytes, 9–14%) is
  the measured NO to "should a lookaround body compile as a call", a lookaround
  body being `k = 1` by construction. Engine selection is `VM_ONLY`
  structurally; the prefilter is dropped in wave E because erasing a call is
  **not** a superset, and that costs a MEASURED **21×–350×** on the non-recursive half of the population, which is why the
  sound construction (splice the non-recursive callee's NFA fragment, `Σ*` for
  a recursive one) is designed and scheduled rather than waved at. Six ASKs
  for Frank, the first of which re-opens the plan row's own reserved give-up
  code now that its premise (a separate call stack) is gone. Measurements:
  `subroutines_measurements/`.
- `subroutines_measurements/` — the [DD-14] lane's TWELVE probes, its oracle
  helper, its archiver and FOUR prototypes (two of them the R34 C2 panel's own,
  ADOPTED UNCHANGED); see its own CLAUDE.md. **No
  instrument reads a subroutine call through pcrec, because pcrec cannot
  compile one** — every in-pcrec arm measures a separate axis (the refusals
  and the 26 registry rows, the give-up code space and every site the
  `ERR_FLOOR` move touches, the emitted primitives quoted from `src/`, and —
  for the prefilter — the INLINED EQUIVALENTS of call-bearing patterns,
  verified equivalent 420 cells / 0 disagreements before any timing). Borrows
  `../lookaround_measurements/probes/la_oracle.py` → `br_oracle.py` →
  `pcre2_ctypes.py` — **three levels, no second binding**. It adds one
  instrument new to this project: **`callout_trace()`**, a
  `pcre2_set_callout` callback reading the LIVE ovector inside a called body,
  which is the only way to separate "the callee never wrote the slots" from
  "the callee wrote them and the return restored them" — two hypotheses with
  the same after-the-fact table and completely different emitted code. **And it BUILT §5's mechanism and ran it**
  (`prototype/callproto.c` + `probes/probe_callproto.py`): the frame that
  carries the return label, the non-popping return, the fail label's one added
  line and the `|W|` trailed save/restore, compiled twice — the second time as
  the plan row's REJECTED separate `call_stack[]` — giving **45 cells agreeing
  with libpcre2, 4 agreed-in-kind, 0 disagreements, and the broken build wrong
  on 3 of 50 including a FALSE MATCH**. That run is what found the design's
  capture restore set incomplete. Its
  `out/CLAUDE.md` carries **TEN instrument defects the lane found by running
  its own probes**, and **the first one would have gone into the design**: a
  retry-cost axis whose subject picked the callee's LAST alternative, so no
  call was ever re-entered after a failing follow — it reported LINEAR costs
  and an "atomic control" HIGHER than the backtrackable one, which reads as
  *"the atomic linkage costs more"*. The others: a depth bisection reporting a
  default limit it never reached; a probe that DIED at row 40 of 80 because
  the oracle's `search()` raises on `rc -52`; a callout cell that fired no
  callout; `-o /dev/null` making every COMPILING cell read "Permission denied";
  a vacuous match-limit self-check; `--emit-main`'s argv-fed subject silently
  capped at `MAX_ARG_STRLEN`; a flag check that grepped documentation instead
  of invoking the flag; a `\g<` census counting in-class escapes as calls; and
  a prototype differential whose group-count column disagreed with the C side's,
  announcing SIX false disagreements with libpcre2 for a construct that agrees
  perfectly.
- `frame_buffer_design.md` — **PROPOSED, NOT PANELED; nothing in it is
  built** ([DD-14.FB], 2026-08-24): the design record behind
  `../spec/match_api.md` §10, D71 item 2's CALLER-PROVIDED FRAME BUFFER.
  Its three load-bearing results are all measurements, and two of them
  answer questions the ruling left open rather than restating it.
  **(1) THE TRAIL MUST BE CALLER-PROVIDED TOO, and a frames-only feature
  would be INERT.** The ruling names the `resume_stack` array only; sweeping
  the two capacities INDEPENDENTLY on `^(a(?1)?b)$` measures **2.000 resume
  frames and 8.982 trail entries per nesting level** — so at the stamped
  2048/3072 the TRAIL binds, the artifact gives up at n = 342 with two
  thirds of its resume stack unreachable, and raising the resume capacity to
  200,000 with the trail left alone measures **the same n = 342**. A caller
  handed a gigabyte of frames under a frames-only version would see no
  change at all. **(2) THE C-STACK COST, which is the number the ruling is
  about**: `gcc -fstack-usage` puts `rx_search` at **131,296 bytes** on a
  call-bearing artifact against the prototype `rx_search_in`'s **224** —
  586× — and a 128 KB `pthread_attr_setstacksize` thread (musl's default)
  **SIGSEGVs** on a 2-byte subject through the shipped entry while the
  prototype matches an 800 KB one on the same thread. **(3) THE mmap
  WORKED EXAMPLE IS RUN, not computed**: 2 × 64 MB `MAP_NORESERVE` costs
  1.7 MB of RSS untouched and reaches libpcre2's own measured 800 KB depth
  in 0.056 s touching 88 MB, with the ceiling landing where the trail
  arithmetic predicts (between n = 466,000 and 470,000). It also PRICES the
  one objection that could sink the design — the push site reading a
  capacity FIELD rather than an immediate — at **no difference this
  instrument can resolve** (~10%), and says so in those words rather than
  claiming it free. Recommends the buffer-DESCRIPTOR shape over a
  caller-allocated run-state object (which cannot deliver the feature: the
  run state's size is fixed by the capacity macros, so allocating a bigger
  one buys nothing) and over a per-artifact setter (TS-1 rejects a mutable
  static; a thread-local passes the concurrency test and fails the
  REENTRANCY one). **The delegation direction is the design's one
  non-obvious mechanism**: `_in` with a NULL descriptor calls the
  un-suffixed entry, never the reverse, because C cannot declare a local
  conditionally and the obvious wrapper direction would put the 128 KB of
  default storage on the frame of the caller who supplied their own.
  Carries **ONE ASK for Frank (ASK-1, §7.4)**: whether the stamped default
  for call-bearing patterns should be RAISED as ASK 2 originally directed,
  with all three options measured — the measurements point the other way,
  since raising it worsens the [TS-4] cost the same ruling cites, and the
  step budget's 500M / work budget's 10⁹ calibration method does not
  transfer to a resource paid for in C stack rather than time.
  Also carries **FINDING-1, which is independent of whether the design
  lands**: the 128 KB SIGSEGV above makes `../spec/match_api.md` §5.3's
  concurrency CONTRACT false today for call-bearing artifacts, and it
  arrived with [DD-14] waves B+C (the two per-frame call fields took a
  frame from 24 to 40 bytes; 2048 × 16 is exactly what crosses 128 KB).
  §11 is the implementation lane's checklist — eleven items, the seven
  capacity-reading sites enumerated by file:line, three cells (one of which
  needs a harness route that does not exist: `budget frames=` sizes the
  ARTIFACT, not the call, so a `frames-buffer=` directive is proposed) and
  six sabotage rows. §12 lists four falsifiable predictions. A D6
  adversarial panel has not seen it.
- `m6read_samples/` — **APPROVED (Frank, 2026-08-21) and now the STYLE OF
  RECORD; the emitter conversion is BUILT against it** ([M6-READ] sample
  stage): the ONE sample commented artifact the row owes
  before any emitter conversion, delivered as two hand-edited before/after
  pairs (a DFA artifact with prefilter + forward scan + reverse pass, and a
  capture-bearing VM artifact) plus the naming scheme, the style rationale
  and the conversion plan. Nothing in `src/` was touched; the `*_after.c`
  files show what the emitter SHOULD produce. Its load-bearing results:
  **object-code neutrality holds** (`.text` + `.rodata` byte-identical,
  exported symbols identical, behaviour identical on every subject tried)
  but the NAIVE form of that check FALSE-ALARMS — renaming a static function
  or a function-local static table renames its internal-linkage symbol, so a
  disassembly-TEXT diff reports 12/18 differences in which every line is a
  symbol name and no instruction moved; "neutral" therefore has to be
  DEFINED as executed-bytes plus exported-symbols, which is what
  `check_neutrality.sh` enforces. The state legends need no tagging pass and
  no after-the-fact inference (engineering note (iv) discharged cheaply): a
  BFS over the transition table the emitter is about to write labels each
  state with the shortest input reaching it, and `--emit-ir` ALREADY prints
  the VM's slot legend and per-label intents from the emitter's own walk, so
  the readable C and the IR listing become two renderings of one walk. Pin
  budget measured at **~94** (77 in the identifier set surveyed, +~17 sibling
  tables) plus 64 stale doc mentions — but the real hazard is ONE line,
  `tests/codegen/run_ir_listing.sh:132`, which greps the listing's own prose
  for `stv[N]`: rename emitter and listing consistently and both sides go
  empty and the `diff -q` passes VACUOUSLY, the control-shares-a-source-with-
  what-it-controls failure this project has already recorded once. Five
  judgment calls are flagged for Frank rather than assumed, headed by where
  "ABI" stops (parameter spellings have no linkage and were renamed in `.c`
  and `.h`; the shared `PCREC_RX_ABI_H` block is untouched, so note (ii)'s
  re-quote stays body-text-only) and by the deliberate NON-rename of the
  `rx_L<N>` labels, which are shared vocabulary with `--emit-ir`.
  **CONVERSION OUTCOME (same day):** built into both emitters, and §3b of the
  README records the four places the built version had to deviate from the
  approved sample — four of the five proposed macros are unsafe because ONE
  ARTIFACT CAN HOLD MORE THAN ONE ENGINE (OS-0b) and a row stride is a
  per-engine fact; `RX_TOO_SHORT`/`RX_CLAMP_SPAN` became `RX_PRUNE_*` because
  `RX_MRL_*` was a GREPPABLE FAMILY that `tests/mrl` asserts an ABSENCE
  through, and two unrelated names would have made that check pass vacuously
  (**a rename must preserve the PROPERTIES names carry, not just their
  readability** — the single most transferable finding of the lane); the VM's
  cursor took the DFA's `scan_position` so one role has one name across
  artifacts; and four revdet-rung names are deliberately left short because
  their meaning could not be established with enough confidence, a
  confidently-wrong full name being worse for a reader than a short one. The
  conversion also found that the rename reaches ENGLISH four distinct ways
  (possessives, pluralisation literals, an apostrophe terminating a quoted awk
  block, and articles), that longer names silently TRUNCATE in fixed `char`
  buffers (three sites, one of them making the IR listing misreport a slot
  write), and that a BOUNDED gate implemented as `head -n N` over a sorted
  corpus is a fixed fixture with a blind spot — it reported green three times
  while the emitter produced revdet artifacts that did not COMPILE, caught
  only by `tests/altcls`'s two-artifact `-Werror` differential. See its own
  CLAUDE.md and `src/gen/CLAUDE.md`'s emitted-vocabulary section.
- `design_registry_selectors.md` — SR-9 design proposal for string selectors
  in the construct registry. §2's "one uniform rule" mechanism was REVIEWED
  AND SUPERSEDED by R6 (2026-08-10; not built): the registry can identify a
  doorway and name a module but not always the construct itself (`(?(R)`,
  `\12` depend on later-pattern or running state). Build the `byte + tail`
  design in §7 instead — pending Frank's approval and PC-3.
- `registry_built_status_memo.md` — decision memo (2026-08-21, REGSTATUS
  lane): the "real fix" the [M6.2] repair slice's ITEM 3 refutation named
  (docs/dev/dev_journal.md, 2026-08-19 part 6) — a registry BUILT-STATUS
  field, so the generated compliance index can distinguish a shipped
  module's constructs from a merely-recognised one without flipping
  `RegStatus`/`Roadmap` (which stay PCRE2/base-grammar facts, unchanged).
  Finds the answer is mostly already computed at runtime: a row's own
  `aport`/`cport` `PortKind` plus ext.c's ENABLED-BUT-UNBUILT refusal
  already distinguish built from unbuilt per construct on every compile,
  and tests/reject/'s `reject_gated` pins already assert it row-by-row.
  Recommends PER-CONSTRUCT semantics (module `assertions`' real five-wave
  3/8→8/8 history is the measured reason per-module would keep lying, the
  same shape the refutation rejected one level coarser) and a
  DERIVED-AT-DUMP-TIME column in `pcrec --list-syntax`/the generated index
  — driving each row's own `syntax` through a gate-forced-open doorway
  call, reusing `--probe-ask`/`--explain`'s existing isolated-`Ctx`
  machinery — rather than a hand-declared column, which would reproduce
  the "second `built` column somebody would have to keep in sync with the
  ports" ext.c's own UNBUILT-macro comment already declined to build.
  **RATIFIED WHOLESALE (D65, 2026-08-21)** — all five recommendations ruled
  as written; none touch `RS_BASE => ROADMAP_NONE` pairing or the
  gate-CLOSED diagnostics.
  **BUILT same session (REGSTATUS lane, same worktree/branch)**:
  `pcrec_construct_built_status` (src/parse/syntax_dump.c) landed as
  designed, with one measured correction to the memo's own classification
  sketch — reading `res.what`/`res.answered_at` rather than matching the
  UNBUILT refusal's TEXT, and forcing EVERY module open rather than only a
  row's own, after both measured wrong on real rows (module `verbs`,
  module `unicode-props`, and `(?m)`'s cross-module `FEAT_ASSERTIONS`
  dependency — see src/parse/CLAUDE.md's syntax_dump.c entry and
  tests/registry/CLAUDE.md item 10 for the measurements). `--list-syntax`
  gains the `built` column; `tests/registry/registry_check.c` gains the
  D65(3) defect assertion, sabotage-validated both directions;
  docs/pcre2_compliance.md's generated index carries the column and its
  "How to read" section shrank per D65(4). Measured on the shipped
  registry: 33 of 34 "shipped-module" rows read `built`, `(?J)` reads
  `unbuilt` — the precise distinction per-construct granularity was ruled
  for. Full measurements in the memo's own implementation record.
  **CORRECTED (2026-08-21, tail lane lane/regstatustail): the consumer
  survey covered CONTENT readers (module names, gate-CLOSED wording) but
  not FORMAT readers (field count, positional splits), and the union
  battery found two — tests/reject/'s `--list-syntax` row iterator and
  tests/cli's case10, both hard-coding `NF != 15` — that broke the moment
  the 16th column landed. Both fixed (`NF != 16`); the memo's own
  "Correction" section carries the complete format-consumer survey (every
  site in the tree that parses the dump's SHAPE, not just its content) and
  the CONTENT-vs-FORMAT distinction the first pass needed and did not
  draw. Verified: full `make test` green (corpus 20,775/0, cli 269/0).

- `premultiplied_dfa_table.md` — **[OPT-3] STEP 2**, the design note written
  BEFORE the code (2026-08-26, lane srPremul): store `next_state * stride` in
  the DFA transition table so the emitted step is `state = table[state + class]`
  and the loop-carried chain drops from `lea,lea,movslq,load` to `add,load`.
  Implements the general fix `../dev/opt3_dfa_scan_measurement.md` (STEP 1)
  measured at 1.276x on the bench's throughput row, answer-identical. Carries
  the sentinel choice with its instruction sequence, which loops take the
  transform and why ENG_ATTEMPT has nothing to take, the per-machine bound and
  what happens above it, the `<PREFIX>_DFA_TABLE` stamp and the
  `-fno-premul-table` denial, the identity control, and the failure modes.

- `offset_k_skip.md` — **[OPT-K]**, the design note written BEFORE the emitter
  (2026-08-28, lane optk), on `premultiplied_dfa_table.md`'s model: the DFA
  scan's candidate-start filter stops looking only at offset 0 and instead
  derives, from the pattern's own prefix, a SET of `(offset k, byte-set)`
  tests every match must satisfy — scanning for the rarest member with one
  `memchr` AT ITS OFFSET and verifying the rest on each candidate. Answers
  D66's "does one walk serve the leading fixed lookbehind" (yes; blocked
  upstream, `src/ir/nfa.c` lowers `A_LOOK` to an epsilon) and carries the
  `[ENG-FORM]` selection shape, the identity argument, the five [CHK-2]
  things and the `abi` bump's four sites.

  **Its most useful sections are the ones where it was WRONG.** §2.2 records
  the obvious generalisation (continue the DFA start-state walk past offset 0)
  as CORRECT AND USELESS, because an ENG_UNANCH DFA state merges the threads
  from every subject position — which is why the derivation walks the NFA
  instead. §4.3 records that the draft's "the model is insensitive to
  `C_ENTER`" was refuted by its own sweep. §4.2 records that a verify's cost
  is a probe PLUS a branch misprediction, without which the model recommends
  moving a control pcrec is already ahead of the JIT on. And §7.4 records the
  largest one: **the cost model predicted 13× for a pattern the box measured
  at 0.96×-1.02×**, because a VERIFY removes loop ENTRIES while a SCAN removes
  BYTES — after which the selection gained a MEASURED rule (the scan offset
  must move off 0) sitting beside the modelled one rather than folded into it.
  §7.7 declines a real 1.08×-1.33× improvement against the row's own
  materiality bar, and says so rather than taking it.

- `artifact_size_term.md` — **[ART-SIZE] STEP 2**, the design note written
  BEFORE the emitter (2026-08-28, lane artsize3), on `offset_k_skip.md`'s
  model. **PANELED R40 (`../dev/reviews/2026-08-28-r40-artsize-term.md`, three
  critics) and REVISED THREE TIMES; read §2.0 and §6.1 before any other
  section** — the panel refuted the first version in three separate places and
  each refutation is recorded where it bit:
  (1) **the INSTRUMENT was blind** to the VM hybrid prefilter's computed-goto
  machinery (`static const void *const rx_targets_N[…]`, `rx_s<N>:`), so K41's
  SECOND witness read 118,240 B against an actual 1,220,606 B and **neither
  mechanism engaged on an already-pinned oversize pattern** — the classifier's
  own regexes were the population nobody counted (`../dev/learnings.md` §3);
  (2) **the pre-emission node count the design assumed DOES NOT EXIST**
  (`vm_count_slots` counts slot categories and returns void; `Vm.nodes` and
  `nlabel` are emission-time; the pre-pass mutates state and can `ctx_fail`),
  so the rule now DRY-EMITS the ladder from `compile.c:426` rather than
  building a counting pre-pass that would be a third party to an agreement the
  emitter's own header warns about; and (3) **"every K is answer-identical" is
  FALSE on the give-up surface** — minimum step budget 89→110 across the
  ladder, minimum backtrack frames 39 at K=1 against 28 at K=8 (descending K
  RAISES the frame need), `RX_TRAIL_FRAMES` 62→51 and caller-read — so the
  claim narrows to match results and captures and the new K sweep EXCLUDES
  `budget`/`gu` cells by construction, stated rather than discovered.
  **D84 then ruled the charter's one cap into TWO** (`../dev/decisions.md`),
  both on comment-excluded emitted C SOURCE bytes with the `.o` (≈17 %) quoted
  beside each: a CODE-BYTES cap (**500,000**, ≈85 KB `.o`, ruled by Frank in
  addendum 2 — bytes OUTSIDE table initializers, exact and emitter-counted, no
  model coefficients in any refusal) for D45's compile budget and a
  TOTAL-BYTES cap (1,000,000, ≈170 KB `.o`) for usability, both EXACT
  post-emission checks, both overridable upward (`--max-emit-code-bytes=` /
  `--max-emit-bytes=`) and stamped, neither deniable;
  **and the re-check then found the BLOCKER that makes the mechanism real**:
  `ctx_fail` is a `longjmp` to the compile's single recovery point, so a
  ladder trial cannot be "discarded" — measured, `(?:…(a|b){41}…){41}` six deep
  compiles at K=8 and REFUSES at K=6, so the ladder as first written would have
  broken a pattern that compiles today. The note now specifies a `trial` flag
  under which the five size guards RETURN an over-budget result, with the
  buffer-size EARLY ABORT as the first such guard (without it the ladder writes
  55.4 MB on a worst-rung tower to select a 42,619-byte artifact) and a stated
  AST re-publication invariant with its own sabotage row; `limits.md` gains a "Handling an oversized
  artifact" section drafted in §4.6. The two caps exist because the note
  measured a node at ~5,930x a data-table entry of gcc cost: `a{1,31000}` is
  1.38 MB and compiles in 0.34 s while K41's witness 2 is 1.26 MB and costs
  **66.92 s**. The two K41 witnesses are handled by DIFFERENT mechanisms —
  witness 1's size is node replication (the K rule takes it 2,015,585 →
  116,371 B, gcc 55.13 s → 1.02 s), witness 2's is its prefilter, which K
  cannot touch, so both caps refuse it until **[OPT-4]/K39** shrinks the
  mechanism — which moves K41's pinned fuzz-gate bucket 2 → 0 and exposes a
  second finding: a size refusal would be counted as an accept/reject
  DIVERGENCE, because `fuzz.py` diverts `state_cap` out of that bucket by
  matching its diagnostic text and nothing matches `"pattern too large:"` —
  the shipped replication-cap refusals have the same gap today. Also carries
  the non-monotone K curve (in BYTES and in NODES), the measured decline of
  all three of census §7's levers (the best is worth a corpus median 0.99 %),
  and the identity gap found by reading the gate rather than trusting a
  summary of it: `--unroll` is a VALUE axis, so no gate proves any K
  answer-identical today and [CHK-2] (c) is where that is fixed.
  Measurements: `artsize_impl/`.
- `prefilter_count_independence.md` — **[OPT-4]**, the design note written
  BEFORE the emitter (2026-08-29, lane opt4), on `offset_k_skip.md`'s model:
  K39's fix, the VM hybrid's inlined DFA prefilter no longer scaling with a
  bounded-repeat count. Its argument is that the prefilter is a FILTER and
  `src/ir/nfa.c` ALREADY over-approximates twice (`A_ATOMIC` transparent,
  `A_LOOK` to epsilon), so a count-collapse (`X{m,n}` lowered as
  `X{min(m,1),}` for the prefilter only) is a third member of an existing
  family and inherits its written-down H1/H2/H3 invariants — one more conjunct
  on `emit_vm.c`'s `v.mrl_win`, not a new mechanism. Carries the located cause
  (`compile.c`'s one NFA pair serving two roles; which of forward/reverse
  carries the count is SHAPE-dependent, so a one-direction fix would miss half
  the population), the one-line superset proof that never mentions `n`, the
  MEASURED budget that decides `exact` vs `count-collapsed` (the whole
  count-free hybrid population tops out at 20 NFA states, so 128 fires only
  where the count is the cause: 23 of 2,878 artifacts change), the
  `RX_VM_PREFILTER_LANG` stamp with its `_WHY` companion and deny/force pair,
  and — recorded rather
  than tidied away — the fact that collapsing UNCONDITIONALLY was refused on
  the measurement (96 of the 244 counted-repeat artifacts would GROW, and all
  244 would lose `prefilter-window`). §7 states the two costs it buys the size
  win with, before any of it was built, and STEP 3 fills them in MEASURED:
  the named worst case runs 9.24 s / 99,601 VM attempts collapsed against
  0.000011 s / 1 attempt exact, and §7 gained a third item because the
  prediction was incomplete in the FAVOURABLE direction — on a subject the
  prefilter rejects outright the collapsed artifact is faster, since the
  smaller DFA scans quicker. §4 carries the bar swept at ten values (a
  44-wide plateau, not a threshold) and cites the check that pins it; §8's
  predictions are all held or beaten.
  **RULING B (2026-08-29) REVERSED ITS §4, and the note says so at the top of
  that section rather than deleting it.** The knee this row was built on cost a
  base-tier corpus cell its answer — `(a{1,3}){65}` went from 0.00 s to a
  13.34 s step-budget exhaustion — so Frank re-ruled the default to
  fallback-only: the EXACT prefilter by default, the collapsed one only as a
  ladder attempt when a DFA state cap overflows or an emitted-size cap refuses
  the artifact. §4 and §5 are marked as describing a REVERSED decision (their
  measurements are real; what changed is what they were used for), §10a carries
  the ruling chain, and §10b records Frank's follow-up — that D83/[ENG-PGO]'s
  exemplar pass could decide this per target, which is the one place a
  per-pattern answer would be sound, since the right language depends on the
  SUBJECTS and not on the pattern.
- `opt4_impl/` — the [OPT-4] STEP 3 lane's probes: the nothing-moves survey
  over pcrec-bench's own 18 patterns (54 emits, all byte-identical). Its
  CLAUDE.md leads with the two traps this lane hit — comparing artifacts
  emitted to different `-o FILE` paths (the `#include` line differs, so every
  row reads as changed), and reading a timing number off this box without
  interleaving (the same binary spans 20 % run to run, enough to fake a 2x
  regression between two identical artifacts).
- `artsize_impl/` — the [ART-SIZE] STEP 2 lane's probes and archived outputs
  (the corpus size measurement and its fit, the K curve, the gcc-cost
  decorrelation run), kept separate from `../dev/artifact_size_census/`
  (STEP 1's own census script) for the same never-confuse-the-lanes reason
  `possessify_impl/` and its siblings are separate. See its own CLAUDE.md.
- `definitions_table.md` — **[DD-11] design note** (2026-08-29, lane dd11,
  D85's own charter): the census D85 lacked — every option-dependent
  replacement in the code today, construct by construct, with file:line and
  a replacement-or-primitive verdict for each (4 replacements: `(?m)^`,
  `(?m)$`, `\b`/`\B`, the possessive-suffix family; the possessive suffix is
  the ONLY construct that already performs a full AST-level syntactic
  substitution at parse time, and is this design's model). §2 confirms the
  plan row's own irreducible-core list against the code and names which
  `src/opt/` passes special-case a construct this row would replace. §3
  RECOMMENDS Option A — `RegRow` gains a `definitions` field, NOT a
  satellite table — on D24's own anti-duplication argument and the `family`
  field's precedent, and surfaces a real type hazard: the predicate must
  take an opaque `Ctx *` (`ExtPortFn`'s own shape), never `ParseMods *`,
  which D62 wave A deliberately hid outside `src/parse/`. §4 oracle-verifies
  every equivalence and REPRODUCES LIVE two already-documented python/PCRE2
  divergences (`\Z`'s own python token is PCRE2's `\z`; python's own
  `(?m)^` lacks the `!end_ok` carve-out, in the OPPOSITE direction from a
  naive first guess) — and names the sharpest hazard as SEQUENCING, not
  correctness: wiring the table into real compilation before M6.6's
  exact-lookbehind lowering exists would silently trade D62's exact
  field+fold for the DFA's lossy `A_LOOK`-erasure superset. §5 designs the
  fifth registry surface on `--list-axes`'s own shape. §6 splits "the table
  exists and answers truthfully" (safe now) from "the parser consumes a row
  to build a substitute subtree" (gated on M6.6) as separate, gated
  substeps.

  **PANELED r43 (`../dev/reviews/2026-08-29-r43-dd11-definitions.md`) AND
  REVISED.** Frank RULED IN two families the first pass excluded — the
  class escapes (`\d \D \s \S \w \W \h \H \v \V \N \R` + POSIX classes,
  predicate `always` today with UTF/UCP as the chartered second row;
  `cls_bits.inc` becomes a DERIVED artifact) and the literal escapes
  (`\a \e \f \n \r \t`, octal, `\x`/`\x{}`, `\cX`, `\N{U+}`, `\Q…\E`,
  encoding the chartered second predicate) — plus `(?n)` (a fifth shipped,
  wired replacement the census missed: `(...)` under `(?n)` IS `(?:...)`,
  verified byte-identical) and `(?U)` (excluded as a parameter). The
  first pass's "type hazard" for the predicate was TECHNICALLY WRONG (K1:
  `ParseMods` already compiles as an opaque pointer everywhere) but named
  a REAL gap the manager's ruling fixes properly: **the predicate is a
  closed-enum TAG evaluated by one exhaustive switch in `src/parse`**, not
  a stored callable — containment by construction, pinned by a grep check
  on `assertions_design.md` §8.4's precedent, rather than by a type that
  turned out not to enforce anything. r43-sem found a BLOCKER-shaped
  hazard the first pass missed entirely: the DFA's lookaround erasure is
  guarded per-call-site by `pcrec_ast_stamp` (D67/SR-8), so a table-driven
  builder that omits or mis-stamps it would let the DFA answer from the
  UNSOUND erasure — a silent miscompile, not a performance story — now an
  explicit [DD-11.5] precondition with its own sabotage row. Every
  citation, count and check disposition in the note was corrected to the
  panel's FIX/RULED rows; §7 keeps only what the panel left open (whether
  the 9 base-tier literal escapes with no `RegRow` today get minimal new
  rows or a second row-less array).

- `opt5_step2_twopass.md` — **[OPT-5] STEP 2**, the design note written BEFORE
  any emitter change. **REVISION 2 (2026-09-02, lane opt5d) works every finding
  of the D6 panel `docs/dev/reviews/2026-09-01-r49-opt5-step2.md`; §10 is the
  item-by-item disposition table and is where a reviewer starts.** Rev 1 was
  2026-09-01 under a box hold with every number cited; rev 2 was allowed one
  build, so its proof witnesses are emitted artifacts quoted from this tree.
  DESIGN ONLY — nothing under `src/`, `tests/` or `docs/spec/` lands from this
  lane; §6 is what the implementation lane lands under D80.

  THE MECHANISM (unchanged, and the panel found no input on which it answers
  wrongly): `<prefix>_search` runs a forward scan for the match END and a
  backwards scan for its START, and since STEP 1 both are cursor loops — which
  is why the bench's nine-rung ratio sits at 1.76–2.00. The **START-PINNED
  SEARCH**: where the forward machine's start state is LIVE and accepts
  unconditionally (PLAIN view, no `eolvar`/`endvar`, accept equal across every
  class context, and the same of every seed state), D3's accept-pruning has
  already killed every later start before the first byte, so
  `match_start_position == search_from` on every call and the reverse machine,
  its tables, its accessor block and its loop are **not emitted at all**.

  WHAT REVISION 2 CHANGED. (1) **The proof is re-derived from `emit_dfa.c` site
  by site** — rev 1's Claim A ("the accept probe runs before anything
  advances") is FALSE, because the probe is an axis-E object that sits BELOW
  the scan edges on any viewed or by-class artifact, and `acc_viewed_applies`
  reads a flag OR'd over BOTH machines; the claim is now "some accept ≥
  `search_from` is always recorded", with `[a-z]{0,8}|9$` and `a*|\b9` emitted
  as witnesses. (2) **The `last_accept_position == -1` gate is LOAD-BEARING,
  not dead** — on a dead seed at `startpos > 0` it is the only correct answer,
  so P3 gains a LIVENESS conjunct and every "deliberately dead" phrasing is
  deleted. (3) **The failing-call bound is CLOSED as unsound** (`a*b`/"aab":
  `tr[fs]['a'] == fs`), with no `_match` change in STEP 2 and the population
  handed to `[OPT-VEDGE]`, which also owns the bench's ×37 exhibit — the
  predicate DECLINES that whole form, which rev 1 had claimed as a rescue.
  (4) **Axis J, not H** (STEP 1 took H and I). (5) **Frank APPROVED the
  `rx_info.search_form` mirror**, against rev 1's recommendation, so the change
  carries a struct-layout event and a fourth structural check. (6) **The abi
  ritual is D94's grep**, abi 15 → 16. (7) §0 becomes a **two-instrument
  acceptance frame** with the `unwrapped` match rungs as a CONTROL and the
  `search-filter` rungs and search band as the CUSTOMERS, and an O-13/O-14
  provenance rule (O-14 had not landed; the markers are in place). (8) The
  check plan is rebuilt on **named manifests instead of counts** — the
  independence of the view-decline control expired when it was re-measured for
  this check — with birth-time `SAB_REACH`/`SAB_REACH_POP`, ids S218–S222, and
  six new owed measurements. **S219 ships declared `UNREACHED`**: §5.6b derives
  why the P3-discriminating population looks empty on `ENG_UNANCH` rather than
  merely unpopulated, and the liveness conjunct's real guard is a compiler
  assertion.

  §2 still answers bench ask (iii) NO — now MEASURED, not inferred: memo M3's
  discriminating probe pair confirms scan-edge precondition (3) is what refuses
  the `\z` whole forms — and names the **VIEW-TOLERANT SCAN EDGE**, chartered
  as `[OPT-VEDGE]`, with `[ART-SIZE]`'s first real customer as its trigger.
  §7's owed measurements are the memo's three (all now TAKEN) plus six new
  ones. §9 collects five findings against the plan row plus five raised by the
  revision itself. Companion data: `docs/dev/opt5_step2_premeasure.md` and
  `docs/dev/opt5m2_m2_changed_patterns.txt`.

- `opt_dial_inventory.md` — **[OPT-DIAL] STEP 0** (2026-09-04, lane ccd2):
  the INVENTORY behind Frank's proposed speed-vs-size dial, and a document
  rather than a mechanism by construction (D77 — the row's own STEP 0 is the
  audit, STEP 1 is the option). Every generation-time switch in
  `docs/spec/tuning.md` §2 with what it trades, its MEASURED exchange rate
  and citation, and one of three verdicts: PURE WIN (off the dial), MEASURED
  TRADE (on it), or UNMEASURED (off it until measured, with the specific
  measurement named). Then a draft policy table with the numbers in its
  cells, and the spelling question as three alternatives with their
  trade-offs.
  **THE FINDING IS THE COUNT.** Four of twenty-one switches carry a
  two-axis measured rate; two are measured pure wins; fifteen are unmeasured
  on at least one axis, nearly always on SIZE — pcrec has measured time far
  more often than bytes. A dial built today would have four rungs of
  substance and seventeen switches it must not touch. §7 names the one sweep
  (emitted `.text` per artifact, default against each deny flag, over the
  corpus) that would move six of them at once; `tests/axes` already walks
  that product for ANSWERS and records no bytes.
  Also names the fourth thing that is not a bucket: `-fno-splice-calls` and
  `-fno-prefilter-collapse` are measured on both axes and REVERSE SIGN on
  time with the subject population, which a speed-vs-size ordinal cannot
  express at all.

- `alt_dispatch_study.md` — **[ENG-ISL.S0]**, the alternation-dispatch study
  (2026-09-03, lane altstudy): the measurement note behind `[ENG-ISL]`'s
  first named island candidate ("VM ALTERNATION AS A TRIE DISPATCH",
  docs/dev/plan.md), backed by `studies/alt_dispatch/` (own Makefile,
  never built by pcrec's own `make`; nothing under `src/`/`tests/` lands
  from this lane). Five dispatch algorithms for a wide literal
  alternation, all checked against a serial-try oracle at every subject
  position of every pattern this study built: (a) today's `vm_alt`
  (`src/gen/emit_vm.c`), unfactored serial try; (b) stable first-byte
  grouping; (c) a port of `src/ir/nfa.c:192`'s M2.8 trie to a query walk,
  every accept tagged with its original alternation index, answer = the
  lowest index the walk passes; (d) `[OPT-ALTHASH]`'s k-byte (k=2,4)
  block hash, open-addressed with exact-key verification (not a true
  minimal perfect hash); and (e), added MID-STUDY by ruling R1 (Frank,
  2026-09-03) as the PRIMARY candidate — the VM-NATIVE TRIE WALK: (c)'s
  same trie plus a static per-node `subtree_min` annotation, deciding at
  every end node whether to COMMIT (push one resumable frame, stop — the
  shape a real emitted island would take) or DEFER (record into a small
  ascending-index list and keep walking). §3.2 is the exactness argument
  for (e) and is worth reading on its own: the ruling's literal wording
  ("commit iff nothing deeper beats this index") is NECESSARY but NOT
  SUFFICIENT — `src/ir/nfa.c`'s own rule-1 counter-example (`abc|a|abd` on
  `"abd"`) exposed a case where an already-DEFERRED shallower candidate
  is lower than a leaf node whose own local subtree has nothing lower,
  which the naive test would wrongly commit past; the fix tracks a
  second, running `best_deferred` value and requires beating both. Caught
  by `tests/unit_trie.c`'s own regression case before it reached the
  results tables, not by a panel. On every real bench-derived pattern
  this study measured, (e) pushes AT MOST ONE VM frame per dispatch
  (`total_frames` in `results/tries.tsv`, both algorithms' trie is order-
  INSENSITIVE by construction, `w`/`srt` pairs building the identical
  trie). §5 records what the study could not settle: `sh1`/`pfx3` beyond
  width 512 (the bench's own pools cap there), a true minimal perfect
  hash for (d), rule 2's "NFA step" half (only the decline half is
  implemented), and — flagged explicitly — that this study's (a) is a
  PURE unfactored serial try where today's real `vm_alt` is fed a
  partially-factored trie already, so its measured (a)-vs-(c)/(e) ratios
  are not a direct stand-in for the bench's own measured ×8.87 (w-256 vs
  srt-256) / ×20.1 (w-512 vs srt-512) VM order-penalty figures — a sixth,
  "today's actual partial factoring" baseline was not built. §6
  recommends between (c) and (e) for the VM island and states the D77
  trigger. See its own README.md/CLAUDE.md for reproduction.

  **SHIPPED 2026-09-03 as `[ENG-ISL]` STEP 1** — algorithm (e), the VM-native
  trie walk, is the VM's alternation lowering now (`src/gen/emit_vm.c`'s
  `vm_isl_*`, `docs/spec/tuning.md` §2.20). TWO DEVIATIONS from the study, both
  recorded because a reader comparing the two will notice them:

  1. **No runtime deferred mask.** The study sizes one and reports its depth. An
     EMITTER does not need it: every trie edge is a single byte, so sibling edges
     are disjoint, the walk is a single deterministic path, and the set of
     alternatives still live where the walk stops is a compile-time function of
     the node it stopped at. §3.2's two-sided commit rule is the RUNTIME form of
     that fact; the emitter writes the candidate list out instead, in ascending
     original index, and allocates no slot.
  2. **The predicate is over the LANGUAGE, not per branch.** The study asks
     whether each BRANCH is a literal; the emitter asks whether the alternation's
     whole subtree matches a finite set of literal byte strings. The per-branch
     form was built first and measured wrong: `src/opt/altcls.c` factors a wide
     alternation before the emitter sees it, so every branch it touched is a
     concatenation ending in a nested alternation. That build stamped ELEVEN
     islands on the bench's `w-256` — exactly its own `RX_ALTCLS_FACTORED` count
     — fired on nothing but altcls's residues, emitted a 3.0% LARGER artifact,
     and passed every answer check. `docs/dev/lanes/isl1_report.md` §2.2.

Maintenance: update this file when files are added/removed or their roles
change.
