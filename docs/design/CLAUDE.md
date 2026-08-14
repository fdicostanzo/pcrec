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
  rejected — on a measurement — the AST node captures now need). §12 carries
  eleven numbered ASKs, §13 eight falsifiable predictions. Unpaneled: [M4.3]
  reviews it alongside `match_api_m4.md` and the two ruled pre-freeze docs.
- `design_registry_selectors.md` — SR-9 design proposal for string selectors
  in the construct registry. §2's "one uniform rule" mechanism was REVIEWED
  AND SUPERSEDED by R6 (2026-08-10; not built): the registry can identify a
  doorway and name a module but not always the construct itself (`(?(R)`,
  `\12` depend on later-pattern or running state). Build the `byte + tail`
  design in §7 instead — pending Frank's approval and PC-3.

Maintenance: update this file when files are added/removed or their roles
change.
