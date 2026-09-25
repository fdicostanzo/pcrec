# findrev — [FINDINGS] r2 panel revision (lane report)

2026-09-25, from main `5a2094e7`. Doc-only lane: no `make`, no suite.

## Delivered

- `docs/design/findings/design.md`: the panel outcome block, plus §R, ONE
  disposition table (35 rows: fcrit-model B1–B3, S4–S12, notes 13–19;
  fcrit-sound F1–F3, F5, F6, F8–F11, F13; fcrit-analyzer A1–A8). In-place
  edits are marked `[r2 <id>]`. New sections: §6.2a (per-reader
  answer/give-up guarantees) and the §6.4 consumption-asking rules.
- `docs/dev/reviews/2026-09-25-r2-findings-design.md`: the panel record,
  per critic, with an OPEN FOR FRANK list and a verdict.
- `docs/design/findings/CLAUDE.md`, `docs/design/CLAUDE.md` and
  `docs/dev/reviews/CLAUDE.md` entries updated. The abi text is now "the
  next number at landing", with no literal.

## OPEN FOR FRANK (details in the review)

1. C2b: `rn_window_start`'s run-window choice has K65's shape on
   no-DFA-front VM routes. This was found by this lane and is argued, not
   measured. Rec: extend K65 (a) to runs, inside the K65 fix lane.
2. Stamp redaction mode for the bundle name. Rec: no; document it and
   revisit on a user ask.
3. Confirm that an `analysis` block in an `include "path"` fragment is a
   parse error. Rec: yes.

## Gaps (stated, not hidden)

The relay did not carry the content of fcrit-model notes 13–19 or of
fcrit-sound F4, F7 and F12. F13 arrived as one word ("gates"). None of
these is claimed as applied; the manager should re-supply them from the
transcript or close them.

## Verdict

No BLOCKING item remains unapplied in the design. A focused re-check is
recommended for three pieces of text no critic has seen yet: §6.2a, the
§7 digest with the §10.2 defaults, and §6.4. B2 is gated on three
external items: K65's fix on main, GIVEUP1 merged, and a ruling on OPEN 1.
