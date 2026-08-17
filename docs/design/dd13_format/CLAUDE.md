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
  still applies).

Maintenance: update this file when files are added/removed or change
roles.
