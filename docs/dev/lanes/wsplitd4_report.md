# wsplitd4 report: window split design rev 2.2 (r99 text fixes)

## Summary
`docs/design/memfn/window_split.md` is now rev 2.2, with a new §R2.2 changelog table. It applies review r99's RULING and nothing else. `files.spec` changed in one place: the kit_pos.c title. No code, cut, edits spec or test was touched.

## Items applied
- CLOSURE-1: §8.1 has a new STEP 0, placed after C0 and before C0a and C0b. It is one Linux dev-box queue job run by main at the base. The job runs `make strict`, `test-memfn-finder` (until C0a), `test-memfn-stamps`, `test-memfn-g2`, plain `run_g2_win.sh`, `run_g2_pres.sh` plain and `--plants`, the g2v/simdfloor mech rows, and G5 (both halves). Each arm has its exact command and pass line. The plant pass form is stated: `PLANT <id> RED ...` with exit 0, and GREEN means NOT DETECTED.
- S3012: §7.3, §8.2, §8.3 and §8.4 no longer rely on `run_g2_pres.sh --plants` executing S3012.
  - They take PR #1's pins from `lane/memfn-plantcheck @ 90b0acc66`: win 39, pres 34, proof 6, wreply 2, which is 81 plants and 39 twins.
  - The re-aimed counts under C0 = PR #1 are win 34 (the 33 plus S3012), pres 6, proof 1. I re-ran `binders.py` on that state in scratch to get these: 187, 75, 49, 67 and 4 rows, all OK.
  - §8.4 states that its tables are r98/r99-era runs on `838deefe2`, before the S3012 move. The 38 and 35 plant-check counts there are stale for PR #1, and the note gives the new counts.
- OC1: its own commit C0a, not U1. The sibling grep (D203) found one multi-line `awk -v` site, `run_purity_reach.sh:70`, and 0 other sites. All the other `-v` values are one line, and §8.1 lists them. After C0a, test-memfn-finder is a Mac arm too.
- OC2 and OC3: the reasons are recorded in §8.4. OC2 is `MOVERS_FLOOR = 1` against 0 movers on aarch64. OC3 is x86 text on arm64.
- DOC items:
  - G5's mech half is its own arm with its reason (§8.2 G5).
  - G3 lists the re-aimed ids exactly (§8.2 G3).
  - The kit_pos.c title in `files.spec` names `kit_run_set` and `kit_run_at`.
  - G1.8's binders command sets `TMPDIR`, in both §8.2 and §8.4 (COORD-2).
- I also bumped the revision mention in `window_split/CLAUDE.md`.

## Re-runs
- `assemble.py` and `syncheck.sh gcc-16` give `syncheck: 82 PASS, 0 FAIL (gcc-16)`, unchanged.
- Assembled tree against rev 2.1's: the only difference is line 4 of `kit_pos.c`, the title comment.
- `binders.py` on the PR #1 runner state: all five populations at their floors, 0 bad.

## STATE AT HANDOFF
Branch lane/wsplitd4. The rulings file `wsplitd4_rulings.md` was re-read and is empty, so no later ruling was applied. Nothing is OWED.
Two things were not independently checked:
- The Step 0 pass lines for `test-memfn-stamps`, `test-memfn-g2` and the plain win/pres runs (`checks failed: 0`) come from the suites' tails and the existing doc.
- The G5 REACH_ONLY reason on the Mac is stated from r99's "no base run" fact, not measured.
