# docs/design/stream/ — "one instruction stream", the end-state architecture

The owner's direction of 2026-11-01: every artifact is one continuous program
of typed instruction records (VM control, automaton components and kit sites
side by side), chosen per stretch by one admission table, with a two-way seam
between parts; reached incrementally, byte-identical where possible, under a
ratchet that lowers the count of parallel mechanisms and undeclared crossings
with every step. Judged on handoff architecture (F1 focus, F2 flexibility, F3
division of labour, F4 no blindness); speed is a no-regression gate. Every
step that changes code needs the owner's go. Plan row: [STREAM].

## Files

- `manifesto.md` — STABLE: why (F1-F4, "a viable long term project that can
  grow"), the end state in plain words, the principles, scope / HELD /
  non-goals, how it is checked. No file:line or counts. Changes only with
  the owner.
- `roadmap.md` — LIVING, dated, the manager revises it: the migration AREAS
  by code area (files and anchors at a named main commit, the next
  byte-identical step, prerequisites, what it deletes, ride-along triggers by
  plan tag, open review findings, size), the HUBS with owners and declared
  extension shapes, round 3's declared-vs-undeclared re-read of the three
  replayed changes, the PROVISIONAL admission table, the RATCHET inventory
  (baseline, recipes, log), the proof order, how a lane uses it.
- `arev.md` — area A-REV's design note (PROPOSED rev 0, lane arevdesign,
  2026-11-05): one reverse automaton kind (one operand record, two walk
  behaviours, a VM-record host), its clients in order (lookbehind's
  `reverse-dfa` row first, then revdet and the landmark walk), the
  byte-identical-first steps and their ratchet recipes. `roadmap.md`'s A-REV
  section is the area plan and points here.
- `approach.md` — REVISION 3, superseded by the two above; kept as the design
  record of rounds 1-3 (the long arguments, the full conjunct text, the
  finding maps in §14).
- `round1/` — the round-1 inputs (three drafts, the synthesis = rev 1, the
  common brief), verbatim; own CLAUDE.md.

The critic rounds: `docs/dev/reviews/2026-11-01-r1-stream1.md` (rev 1),
`2026-11-01-r2-stream2.md` (rev 2), `2026-11-01-r3-stream3.md` (rev 3), each
with its rulings. Line anchors in `roadmap.md` move with code: re-grep the
symbol. Never cite plan.md by line (PL14) or a docs/spec file by line.
