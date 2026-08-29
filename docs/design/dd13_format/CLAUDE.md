# docs/design/dd13_format/ — the [DD-13] unified file format design

Design material for plan row [DD-13]: the unified pattern-source / test
file format (compilation manifest + test carrier + pcrec-bench set
format). Process is staged — [DD-13a] requirements, [DD-13b] design,
[DD-13c] adversarial panel — and no parser is written before (c) closes.

## Files

- `frank_inputs.md` — append-only dated log of Frank's requirements,
  rulings-in-direction, and flagged open decisions (the OD-n ledger),
  accumulated ahead of [DD-13a]; the requirements note consumes it.
- `requirements.md` — **[DD-13a] REQUIREMENTS note (2026-08-17, dd13a
  lane), read-only fact-gathering, no grammar proposed.** Enumerates every
  consumer's needs (`.rxt` harness/corpus, [V-E] manifest+finder, [V-F]
  transformer, [V-G] user testing, pcrec-bench sets, D27 machine
  generation, [M4-SUBST] templates) as ID'd requirements (R-RXT-*,
  R-VE-*, R-VF-*, R-VG-*, R-BENCH-*, R-GEN-*, R-SUBST-*), each cited to
  its source. Corpus survey: 54 `.rxt` files, 1,100 pattern blocks,
  9,977 expectation lines across `tests/`, all oracle-verified — the
  evidence behind its "DIALECT, not subset or migration" answer to the
  compatibility question (§9): existing `.rxt` files stay valid and
  unchanged under the new format (R-COMPAT-1), which grows a strict
  superset around them. Carries `frank_inputs.md`'s OD-1..OD-5 ledger
  forward as requirements-with-open-decisions (§11, none resolved), states
  five cross-consumer tensions (§10, notably T-1's interface-vs-
  reference-only-pattern testability question and T-3's pcrec-specific-
  numbering-vs-engine-neutral-bench-expectations question), seven
  anti-requirements (§12, headed by AR-1 — must not force re-verification
  of the existing corpus — and AR-2 — must not add dispatch to the
  D20-protected single-pattern common case), and a five-item "for the
  panel" list (§13) naming its own weakest evidence. Confirms
  `subst_template_design.md` intersects narrowly — one deferred
  template-text field owed to the manifest (D38 Q7), no other coupling.
  Consumed by [DD-13b]; no parser exists yet (D6 panel gate at [DD-13c]
  still applies). **PANELED R27 (2026-08-17,
  `../../dev/reviews/2026-08-17-r27-dd13a.md`): one BLOCKER, all
  dispositions FIX-NOW (one deferred half).** F1 (both critics, both
  three-way confirmed): the note's §7 claimed a `.rxt`/manifest grep over
  `subst_template_design.md` returned three hits when the true count is
  six — the miscount hid §5.5 (a second manifest hook) and, more
  seriously, an unsurveyed §8 "Testing sketch" that works out a full
  `.rxt` substitution-testing extension (`repl`/`s`/`sg`/`serr`), the
  most concrete format-extension prior art in the repo. Fixed: §7
  rewritten with the corrected grep, R-SUBST-3 records the prior art.
  Five majors fixed: R-VE-12 (encoding field, plan.md's own manifest
  field list), R-RXT-10 (`tests/reject/`'s documented perr-can't-say-WHY
  limitation, a previously unsurveyed consumer), Appendix additions for
  [M3.1] chunk-boundary tests and [DD-11]'s newline axis (neither
  forecloseable, neither with a proposed directive), T-6 (per-file
  population accounting vs FILE INCLUDES), and §9's compatibility answer
  reargued with softened confidence (DIALECT still stands — r27b's own
  steelman against it failed — but "import" is shown not to disambiguate
  dialect from migration on its own, with APPROACH.md §8 Q1's "grown
  from .rxt" added as a second, independent corroboration, and the g/gp
  precedent marked categorically flatter than what DD-13 actually needs).
  Six minors/nits fixed: the D26/D27 "gold-plate" citation reworded to
  the brief's own do-not-design instruction (D27 had zero textual
  support anywhere in the repo, raised to MAJOR on a same-day addendum
  after a third sub-review); a footnote on `tests/base/CLAUDE.md`'s
  drifted case-line count (676 quoted vs 679 recounted — the quoted file
  drifted, not this note's arithmetic; left unedited to avoid a conflict
  with a held branch); OD-2's semantic-vs-compile-option tweak split
  marked as this note's own derived distinction, not Frank's; a
  keyword-collision-risk appendix bullet; three citation-location
  corrections (R-VE-1's quote lives in the [DD-13] row, not [V-E]'s;
  R-BENCH-6's is APPROACH §2, not §3; R-VE-8's "measured, never read
  from docs" restored in full); and R-BENCH-1's four-tag grouping
  attributed as the note's own synthesis. One correction IN the note's
  favor: §13's self-critique of R-GEN-1 as "one generator" was itself
  wrong — the panel found four more independent no-forcing-function
  instances (the R22 D27-blinded capture author, plus the possessify/
  rungselect/counterk generated corpora), all using only existing
  directive vocabulary — n=5, not n=1, now recorded in §6 with the
  residual honestly narrowed (all five are flat corpora; none has
  exercised cross-references, config sections, or includes). Fix pass
  landed by the dd13afix lane same day; census and ~45/50 sampled
  citations were independently re-verified and held throughout.

Maintenance: update this file when files are added/removed or change
roles.
- `usecases_and_outline.md` — the manager's position paper for Frank (2026-08-28, forty-fourth session): use cases U1-U11, a ten-line-kind outline in three demand-staged waves, three worked files, the directory-vs-grown-file evaluation (verdict: directory = convention, sidecar dropped), and the six rulings the [DD-13b] design note would build under.
