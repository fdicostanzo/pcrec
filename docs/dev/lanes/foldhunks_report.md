# [M5.0] STAGE 4 design-text hunks applied at merge (lane `foldhunks`)

2026-09-08, sonnet, `worktrees/foldhunks`, branch `lane/foldhunks`, docs-only
(no `make`, no build, no suite run). Applies `docs/dev/lanes/utf8s4_report.md`
§4's six owed hunks to `docs/design/utf8_design.md`, per the stage-1 precedent
that the manager applies these at merge.

| hunk | section(s) | what changed |
|---|---|---|
| 1 | §4.2, §4.3 | per-contribution fold rule added as a dated corrected-text block (report §3.1) — literals/ranges fold by the encoding relation, named byte sets fold by `pcrec_fold_ascii` at every encoding, property sets do not fold; §4.3 notes the negation is over the per-contribution-folded set |
| 2 | §4.6 | sampled differential marked SUPERSEDED by the relation sweep (report §3.6); ~12 KB size estimate corrected to measured 25,675 bytes / 55,053-byte whole artifact (report §3.9) |
| 3 | §4.6 | ASCII-restriction tie added — the vendored relation restricted to `[0,0x7F]` is exactly `pcrec_fold_ascii`'s 52 letters, now a checked hazard rather than a coincidence (report §3.3) |
| 4 | §8.2 | S-U11's `SAB_REACH_POP` corrected — 22 is an assertion count, not a grep-line count (`check_1n_fold` asserts it directly; the row's grep floor is 11) (report §3.7); S-U3's sabotage spelling marked not expressible as a text hunk, with the shipped 0xFF-clamp recorded as what was built instead (report §3.8) |
| 5 | §9.2 | stage-1 entry notes S-U11 actually landed at stage 4, not stage 1 as planned, and names the cost (three stages of unwatched premise); stage-4 acceptance records `tests/utf8/fold.rxt`'s landing (45/45) and PC-4's 22-assertion result (report §3.5, §1-§2) |
| 6 | §4.1.1 | standing-instrument ask marked DISCHARGED, citing the built check and its numbers |

Also appended a dated addendum to `docs/design/CLAUDE.md`'s `utf8_design.md`
entry naming the six hunks and pointing at this report and `utf8s4_report.md`
§4.

Every hunk carries the dated attribution the brief asked for (stage 4, lane
`utf8s4`, applied at merge) and restates only what the design needs to be
correct — evidence and full measurement tables stay in
`docs/dev/lanes/utf8s4_report.md`, which each hunk cites by section.

One commit follows this report. No `make`/build/suite was run (docs-only
lane, box under a merge battery). Handing back to the manager; ending now.
