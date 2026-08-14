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
  embedded code, R-c group vs non-group forms). ONE context-struct
  signature `ptrdiff_t (const rx_ctx *)` on both sides — `rx_ctx`
  carries subject/len/pos + captures-so-far, so a compiled matcher
  links directly as a callout AND callouts can predicate on prior
  groups (`(\d+)(<fn_gt_100>)`); VM-forcing confirmed; the
  pcre2_callout_block mirror moves to PCRE2-compat GENERATION mode;
  `(<x>)` literal-group collision flagged as module-gated; freeze
  obligations F1–F7; six open questions for Frank. Unpaneled —
  reviewed with the M4 match-API design.
- `subst_template_design.md` — [M4-SUBST] phase-1 design note (2026-08-14):
  the SUBSTITUTION TEMPLATE COMPILER, written before M4's match-API freeze
  because Frank's ratified observation is that the template compiler consumes
  only the capture-offset CONTRACT. **PROPOSED throughout; no panel has seen
  it and §9's eleven questions are unruled.** §2 is the half with the
  deadline: C1-C11, requirements ON M4's match API (offset-pair shape, group
  count as a compile-time constant, the UNSET sentinel in both slots, every
  pair written on every match, byte offsets per DD-12) plus an explicit
  non-requirements list. Also: the tiering mechanism (PCRE2's run-time
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
  were refuted, two of them changing the design.
- `design_registry_selectors.md` — SR-9 design proposal for string selectors
  in the construct registry. §2's "one uniform rule" mechanism was REVIEWED
  AND SUPERSEDED by R6 (2026-08-10; not built): the registry can identify a
  doorway and name a module but not always the construct itself (`(?(R)`,
  `\12` depend on later-pattern or running state). Build the `byte + tail`
  design in §7 instead — pending Frank's approval and PC-3.

Maintenance: update this file when files are added/removed or their roles
change.
