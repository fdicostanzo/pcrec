# docs/dev/reviews/lens_reports/ — the code review's per-lens findings

One file per lens of the 2026-09-17 code review
(`docs/dev/reviews/code_review_criteria_draft.md`, RATIFIED). Each is one
opus lane's own voice, written READ-ONLY: findings with `file:line`
citations and concrete suggestions, never a refactor. The manager's
synthesis (`docs/dev/reviews/YYYY-MM-DD-code-review.md`) dedupes across
them and ranks per A4; on any disagreement the synthesis wins.

Every finding in these files is written to the charter's admissibility
rules — A1 (cite and argue against any ruled record it contradicts, or
drop), A2 (a duplication finding names the shared abstraction: proposed
signature, call sites replaced, what varies), A3 (name the sabotage/
codegen/abi anchors bound to the code it would move), A4 (severity /
effort / blast radius), A5 (cite the metric artifact under
`tools/review/out/`).

## Files

(The ten per-lens report files each land here from their own parked
branches at merge time — see the manager's merge record for the file
list and its own entry per file, which this lane does not duplicate.)

- `synthesis_collation.md` — lane `collate` (sonnet, mechanical
  collation, no judgment on finding validity): normalizes and
  cross-references all ten lens reports (lens 7's deliverable rides
  inside lens 4's file per the ratification's "7 merges into 4"
  disposition; `emitvm_second_pass.md` — still in flight on a live
  lane — is deliberately excluded, to be folded in by the manager).
  Six sections: (1) a findings table, one row per finding across all
  ten reports, cited `L<n>-<id>`, cross-referenced; (2) seven OVERLAP
  CLUSTERS where multiple lenses found the same underlying item —
  three carry explicit, unresolved POPULATION DISAGREEMENTS (the
  growable-array/arena-vector family at 10/7/13/28 sites depending on
  instrument; the emitter scratch-buffer family at 94/49/48 depending
  on scope; and a severity downgrade across the review's own timeline
  on that same buffer family, L2 CORRECTNESS-RISK → L10
  MAINTAINABILITY+latent once L10 measured actual truncation margins),
  one is a straight duplicate finding (L8-F5 / L10-L10-8, `write_file`'s
  missing `ferror()`), one is a tier disagreement between two lenses on
  the same proposed mechanism (the allocation-failure injector: L8
  DESIGN-EVENT vs. L5 LOCAL), one is a named measurement SUPERSEDING an
  earlier one (L10's template-layer measurement closing the question
  L2 left open), and one is five lenses converging on one unreviewed
  surface (`emit_vm.c`'s rung/slot/frame emission) that lens 11's own
  report substantially discharges without having been chartered to;
  (3) a RULINGS-FOR-FRANK list (ten items, each in the citing report's
  own words); (4) FIX-NOW candidates (immediate, one-line, or
  independent-of-waves items any report flagged as such); (5) a
  PROBED-AND-HELD master list, concatenated and deduped across all ten
  reports' own held/rejected sections plus lens 11's 13 functions that
  pass all five altitude questions and should stay long; (6) a
  SECOND-PASS/FOLLOW-ON REGISTER of fourteen named-but-not-chartered
  follow-ons, cross-referencing which lenses named each and noting
  where one lens's own delivered work already substantially answers
  another lens's stated need. Resolves nothing — every disagreement is
  surfaced with both sources and their instrument, decided by neither
  this lane nor stated as decided.

Maintenance: add a row per lens report as it lands.
