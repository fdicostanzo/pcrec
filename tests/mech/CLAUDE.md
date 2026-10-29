# tests/mech — GENERATE the sabotage detection tables ([MECH-1])

Every "disabling X fails N cases" figure that used to live by hand in
`tests/*/CLAUDE.md` goes stale silently, and every attempt to maintain one by
hand in this project has failed at least once — including twice inside the
same review, and once inside the paragraph written specifically to warn about
it (see `tests/reject/CLAUDE.md`). This directory owns the sabotage EDITS
themselves, applies each to a pristine tree, and prints a matrix instead of a
copied number. Docs should cite this script's output, not a hand-typed count.

## Files

- **run_sabotage_matrix.sh** — the driver.
- **lib/replace.py** — the ONLY thing that edits a sabotaged file.
- **reach_only_selftest.sh** ([MECH-REACHONLY], 2026-10-21) — self-test of `REACH_ONLY=1` (see its section below): a live probe, a failing probe, a declared-UNREACHED one.
- **nocompile_selftest.sh** (review 2026-10-24 r1 subst, CHK-1) — self-test of the compile gate (`NOCOMPILE_ERE`: a failing arm whose log shows compiled code failing is ANOMALY, never DETECTED): S1354's original non-compiling plant must read ANOMALY, its warning-clean plant DETECTED.
- **rows_for.sh** ([TT-8], 2026-08-23) — lists the `SAB_ID`s whose `SAB_FILE`/`SAB_FILE2`/`SAB_HARNESS_TARGET` matches one or more given paths, at a path-component ...
- **sabotages/S\*.sh** — one file per sabotage, sourced by the driver.
- `run_recursion_identity.sh` — section "[recidfix/varland] S273, and the FIRST ARM `run_recursion_identity.sh` has ever had (2026-09-25)" (history file)

## Standing rules (kept from the Files notes)

- THE RUNNER ARCHIVES HEAD PER ROW (`git archive HEAD` is re-read for EVERY sabotage): COMMIT BEFORE YOU START AND COMMIT NOTHING DURING THE RUN, or the matrix measures N trees.
- A MISSING OR UNSCRAPEABLE SUITE LOG SCORES ANOMALY, NEVER A SYNTHESIZED COUNT: all arms route through `score_arm`; never default a missing failure count to a detection.
- Mech ids are passed without a suffix (`S222`, never `S222_...`); read a row verdict from its own `== mech run COMPLETE` trailer; take S-ids from the range your brief names.


## D69 — the mech re-run policy is TIERED, and how to run it (2026-08-23)

Full matrix != every merge. `docs/dev/decisions.md` D69 tiers the re-run
obligation by what changed (docs-only -> tripwire; tests-only -> tripwire +
the changed rows; src changed -> tripwire + the rows whose `SAB_FILE` or
target changed; module/milestone CLOSE -> the full matrix), on the argument
that a row's verdict is a property of the pair (compiler, corpus) and this
lane's retro-diff of `build/mech_m64.log` (99 rows) against
`build/mech_m65.log` (118 rows) found ZERO rows flipping DETECTED ->
UNDETECTED without their own `SAB_FILE`/definition changing across 99 rows
in common — the measurement the ruling's risk acceptance rests on. The
tripwire is `python3 scripts/m6read_check_sab_anchors.py`; the rows for a
changed-files list are `bash tests/mech/rows_for.sh <path>...` (above).
Full tiers table, the anchor-drift/new-row accounting for the two
exceptions the retro-diff DID find (`S48`'s anchor-count fix, `S107`/
`S108` undetected-from-birth), and the earlier-journal corroboration:
docs/testing.md's "D69 — the mech re-run policy is TIERED, and how to run
it" section.

## A sabotage that zero checks catch is the finding, not a bug

If every suite a sabotage lists comes back with 0 failures, the matrix marks
that row `**UNDETECTED**` and calls it out again in a summary block at the
end. An UNDETECTED verdict means a guard regressed and is the thing to go fix.

**As of 2026-08-12 there are no UNDETECTED rows** (35 of 35 DETECTED, 0
anomalies, 0 pc3-skipped), and the row that used to be the standing exception
is worth reading before anyone re-adds one.

`S19-new-wrong-row` — the SR-4 blind spot, "a NEW row with a plausible wrong
module and no hand-written entry" — was documented HERE and in its own header
as EXPECTED to land UNDETECTED, with PC-3 named as the only thing that could
see it and declared out of scope for this matrix. Both halves of that were
retired at MOD-0.8c slice 1, and the two failure modes are different lessons:

- **It had already stopped being UNDETECTED, and nothing noticed.** Measured
  at `11352be` with `reject` as its only arm, BEFORE the new arms existed:
  `reject 1fail/486pass`. The exact iterated-row count (100 ≠ 101) trips, as
  `tests/reject/CLAUDE.md` records. A hand-maintained "expected UNDETECTED"
  that had quietly become DETECTED is precisely the staleness this directory
  exists to prevent — occurring in the directory that exists to prevent it,
  which is this project's oldest recurring shape and its fourth instance.
- **PC-3 is in scope now**, because there is a `pc3` arm. Measured:
  `pc3 1fail/154pass` — libpcre2 has no `\j`, so the fabricated `RS_MODULE`
  row fails PC-3's "a row naming a construct PCRE2 does not have" clause.
  That is an external answer rather than a count moving, which matters: R8/C4-10
  records that a count-shaped tripwire prints its own remedy, so following its
  instructions verbatim is how a wrong row gets past the suite.

(Rest of this section: see the history file.)

## Conventions

Anchors are copied from `git show HEAD:<path>`, not from a live working-tree
read — this repository routinely has other in-flight work editing the same
files this tool sabotages, and `run_sabotage_matrix.sh` always measures
committed HEAD via `git archive` regardless of what the working tree looks
like at run time. When source drifts enough that an anchor's occurrence count
changes, the run fails LOUDLY on that one sabotage (`APPLY-FAILED`, anchor
mismatch reported by `lib/replace.py`) rather than silently applying to the
wrong place or skipping. Re-derive the anchor from `git show HEAD:<path>` when
that happens; do not weaken the count check.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__mech.md`.
