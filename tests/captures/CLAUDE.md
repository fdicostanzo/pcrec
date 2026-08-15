# tests/captures — capture-group expectation corpus

[M4.5a]. `.rxt` files here use the base format (`pattern`/`m`/`n`/`ms`/`ns`)
plus the two new line kinds it introduced: `g <slot> <start> <end>` (LIVE —
must be checkable against the current artifact) and `gp <slot> <start>
<end>` (PENDING-VM — may be beyond what today's DFA-only artifacts deliver).
Both attach to the most recently preceding `m`/`ms` case in the same block.
Full format spec, the population-accounting rule (`g` on an out-of-range
slot is a hard FAILURE, never a silent skip; `gp` on one is counted
separately and self-activates once the artifact's `RX_NCAPS` grows to cover
it), and the python-oracle tier: `../../docs/testing.md`, "Capture-group
expectations" section.

## Files

- `basic.rxt` — 14 `m`/`ms` cases (13 `m`, 1 `ms`) carrying 3 `g` (slot 0,
  live — every artifact delivers the whole match today) and 28 `gp` (slots
  1+, pending-VM until [M4.5]'s VM emitter lands) group expectations. Every
  value oracle-verified against python `re`'s `match.span()`; every
  whole-match span additionally checked against the real `build/pcrec`
  output before landing. Covers: sequential groups, an optional group both
  matching and not (RX_UNSET), a repeated capturing group's last-iteration
  span (PCRE2 leftmost-first priority), nested groups, alternation with
  exactly one branch's group participating, a zero-iteration group, an
  optional middle group, a three-way alternation/repetition mix, and one
  `ms` case pairing startpos with group attachment.

## Conventions

Same `.rxt` conventions as the rest of `tests/` (see `../CLAUDE.md` and
`../harness/CLAUDE.md`), plus the `g`/`gp` extension. `RX_NCAPS` is read from
each block's generated `gen.h` by `tests/harness/run.sh`, not assumed — a
`g`/`gp` line's slot is checked against the ARTIFACT's actual delivered
count, not against the pattern's lexical group count (which the python
oracle in `verify_rxt.py` checks separately, unconditionally of the
live/pending distinction).

Maintenance: update this file when files are added/removed or their roles
change — in particular, once [M4.5]'s VM emitter lands and `RX_NCAPS` grows
past 1 for group-bearing patterns, the `gp` lines here will start
self-activating into real checks; note here if that changes which counts
are "live" vs "pending" in a way worth a fresh summary line.

## [M4.5d] D27-blinded author files (2026-08-15, R22)

- `priority_and_iteration.rxt`, `participation_and_zerowidth.rxt`,
  `structure_anchors_misc.rxt` — 85 m/ms cases + 145 group lines by the
  D27-blinded capture author (cell: match_api_m4.md + testing.md + binary
  only; python-derived, twice-verified; binary used accept/reject only).
  All gp by design (the author could not read RX_NCAPS without running
  the implementation); they self-activate per artifact. Landed 230/230
  green after whole-line comment normalization (testing.md's comment rule
  is whole-line only). Provenance + findings:
  docs/dev/reviews/2026-08-15-r22-m45d-capture-author.md.
