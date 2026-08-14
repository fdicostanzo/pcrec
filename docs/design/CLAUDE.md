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
  and Q6 (embedded-code restrictions) remain OPEN.
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
  cross-reference.
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
  the two serve different consumers, not redundant ones. **Still
  PROPOSED**, unpaneled.
- `design_registry_selectors.md` — SR-9 design proposal for string selectors
  in the construct registry. §2's "one uniform rule" mechanism was REVIEWED
  AND SUPERSEDED by R6 (2026-08-10; not built): the registry can identify a
  doorway and name a module but not always the construct itself (`(?(R)`,
  `\12` depend on later-pattern or running state). Build the `byte + tail`
  design in §7 instead — pending Frank's approval and PC-3.

Maintenance: update this file when files are added/removed or their roles
change.
