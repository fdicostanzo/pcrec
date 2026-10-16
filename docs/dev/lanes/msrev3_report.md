# Lane msrev3 — measure_sets.md revision 3 (2026-10-16)

Design-doc lane (opus), from main `063b4a4b4`, branch `lane/msrev3`. Nothing under `src/`,
`cli/`, `lib/` or `tests/` changed. No build and no suite were run, because the change
is documents only.

## Delivered

- `docs/dev/reviews/2026-10-16-r2-measure-sets-recheck.md`, committed from the main
  tree's untracked copy. Its entry in `docs/dev/reviews/CLAUDE.md` follows the r1 entry's
  shape.
- `docs/design/measure_sets.md` revision 3. Its §R3 table maps every finding to a
  disposition and a section. The r2 tags `[r2 <id>]` mark the changed text in place.
- The `docs/design/CLAUDE.md` entry gains a REVISION 3 paragraph.

## Dispositions

All 8 MAJORs and both r1 PARTIALs (msc1-5, msc2-9) are ACCEPTED and discharged. All 11
MINORs are accepted. n7 is accepted in part: the over-staling is recorded as by design,
and the body normalization is DEFERRED to M4, the first stage with a `pcrec.` row.
Nothing is rejected.

## What changed

- **M1.** Revision 3 adds the `evaluator-params` kind and the placement rule as a
  first-match table (§9.1a). §9.11 fixes `prereg.tsv`'s format and digest (the prereg
  hash) from today.
- **M2.** Every per-kind divergence is a kinds-table column (§9.5). Measures adopt the
  shipped `name-else-file` classification and refuse an S2 mismatch. K1 names
  `res_fixtures.py` as the witness.
- **M3.** R5 is new: decoded = independent. Each kind has an independent reader table.
  For analysis that reader is `analyze/`'s reader, extended at K3 (the extension is
  priced). The `f.tsv` example now works.
- **M4.** The census is emit_sweep's `--data` mode. `knowledge_census.sh` and
  `census_population.tsv` are withdrawn, and S952 is re-aimed.
- **M5.** Each kind has two digest roles (ITEM, STAMP) with literal domain bytes of
  explicit length, all grandfathered. K1 carries a digest pin (S986).
- **M6.** `lib` is a resolve-only row with `entry_match = probe-exists`, which keeps K1
  zero-mover. The case-exactness drift is filed as F12.
- **M7.** Request R-MS6 asks the kit for an arm counter. The admitted arms come from the
  fired-rows section, and a check compares it with the `dispatch` set's construction.
  S956 is re-aimed.
- **M8.** The parts are libc-only and the kinds table sits at the library tier.
  `pcrec-measure` compiles the parts plus the measures row only, held by the dependency
  check (S989).
- **Minors.** n9: the movers census is keyed by transition (`DEFAULTS.log` and
  `movers/<seq>.tsv`). n6: a code table defines the unit and status bytes. The
  (id, rev) shadow key is new (n5). n8, n10 and n11 are fixed as the re-check proposed.
- **D167.** Q-R17P-14's `libc-mismatch` is folded in.

## Findings this lane made

- **F13.** The re-check's count of 11 sabotage rows anchored in `src/core/findings.c` is
  15. Four rows spell `SAB_FILE='…'` with single quotes. K1's re-aims are therefore
  derived from an edit set.
- **A tooling hazard, not filed.** In this environment, `grep` is a shell function that
  runs ugrep with `--ignore-files`. Run inside the worktree, it silently printed NOTHING
  for some searches, and its scans of `worktrees/*` are blind. Use `command grep` to
  verify anything.

## Proposed ids (main allocates)

S983-S990 are main's next free ids per `worktrees/.mgr/sabotage_ids.txt`, past R-21's
S964-S980.

## Open for Frank

OQ-1 (§10.6): who READS the evaluator-parameter kind. The choice is pcrec's parts
compiled into the kit, or the kit's own reader of one shared format and digest spec. The
lane leans to the second.

## For the manager

- File R-MS6 in `memfn/docs/requests.md`, and relay §9.11's format to the kit.
- File F12 as a known-issues row.
- The plan rows' "next" lines are untouched.
