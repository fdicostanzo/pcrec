# comppin report (2026-10-16, lane comppin, sonnet)

Merge main (353249282, E0 + swfix) into the kit branch lane/memfn-fd, then pin the
composition floors of the two non-start-family DIFFER_PINS arms.

## Merge
`git merge main` conflicted in two files, both append-both index lists (new report /
review lines on each side): `docs/dev/lanes/CLAUDE.md`, `docs/dev/reviews/CLAUDE.md`.
Resolved by dropping the markers only, keeping every line of both sides.
`scripts/emit_sweep.py` auto-merged cleanly: sweeparm's DIFFER_PINS floors
(`-fmemfn-simd`, `-fcomments`, byte and utf8) and swfix's `COMPOSITION_EXTRA_PINS` /
re-measured `VARIANT_PINS` both present. Merge commit 4464e1c10.
Verdicts at 4464e1c10 (pinned `taskset -c 12-15`, `-j4`): `make -j4 strict` rc=0;
`make test-spec-history` rc=0 (145 passed, 0 failed).

## Pins
Measured at 4464e1c10, one binary both sides, composition stream alone, full population:
`taskset -c 12-15 python3 scripts/emit_sweep.py --ref-bin build/pcrec --bin build/pcrec
--no-self-check --streams composition --no-differ-floor --jobs 4 --extra=FLAG`
(386 composition files). Before the entry: `COMPOSITION FLOORS: NOT APPLIED ... producing=37
artifacts=106` for both flags (neither flag changes which fixtures compile).
Entries added, AT the measured value (the `--engine=vm` entry's stance):
`-fmemfn-simd` 37 / 106, `-fcomments` 37 / 106.
After the entry: both runs rc=0, no NOT APPLIED line, no VIOLATION line, population
`composition_producing=37 composition_artifacts=106`.

## Plants
S981/S982 (DIFFER manifest, a dropped flag) re-run at 4464e1c10: each `mech run COMPLETE: 1 rows
(unexpected 0, undetected 0)`. They do NOT cover the composition entries (they plant the
DIFFER cell), so no new S-id was invented: the self-test `scripts/tests/emit_sweep.py.test`
gained, per arm, a clean-and-APPLIED check and +1 plants of each floor via a sed'ed copy
(swfix's own mechanism for `--engine=vm`). 24 pass / 0 fail; the four new plants read
`COMPOSITION {PRODUCING,ARTIFACTS} FLOOR VIOLATION: 37 < 38` / `106 < 107`. A deleted
entry reads NOT APPLIED, which the clean-and-APPLIED check fails. A dropped flag is S981/S982's.
If a mech row for the composition entries is wanted, a sabotage id is needed from the manager.

## Checklist
(a) measured at 4464e1c10, counts above. (b) bound: APPLIED and green runs above; plant +1 red.
(c) plants: self-test (+ S981/S982 for the flag). (d) emit_sweep.py pin comment and
scripts/CLAUDE.md describe the entries; `scripts/CLAUDE.md` and `docs/dev/lanes/CLAUDE.md` indexes.
