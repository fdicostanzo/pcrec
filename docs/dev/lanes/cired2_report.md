# cired2 report: CI red on main 9ea9c4a76 (run 40575634945)

## Summary
One real red: `test-rxtsource` in shard 1/3, caused by the scandog merge's
`tests/recursion/cscan.rxt`. Two causes, both harness/pin problems, no pcrec bug:
(1) the section's corpus census and C3 population pins were never moved for the
new file; (2) cscan.rxt is the corpus's FIRST `pattern-esc` block, and C1's
leg-A-vs-leg-B diff compared leg A's decoded pattern with leg B's as-written
text (the dump-value seam, rxt_format.md section 1.5 para 3). Shard 2 was not a
failure: it was CANCELLED at its first step. Fixed in this branch; rxtsource is
green locally (298 passed, 0 failed).

## Failures
- Job results: test (1/3) failure, test (3/3) success, test (2/3) cancelled.
- test (1/3): `make test-shard CISHARD=1/3`, 26/26 sections ran in 2759 s, one
  red: `*** [Makefile:599: test-rxtsource] Error 1` (286 passed, 12 failed).
  The 12: census MOVED 300/6219/74663 vs pinned 299/6218/74528; file list 300 vs
  299; C1 leg A, B and C each emit 6219 block rows vs census 6218; C1 leg A !=
  leg B (the cscan.rxt line-20 pattern row, decoded vs quoted); case-row
  derivation does not reconcile (74663 vs 74528); C3 discovered 300 files vs
  299; C3 version-invariant pin moved (verifiable 24418 vs 24283); C3 pins
  moved (SKIP 52545 vs 52410, no-python-expression 2372 vs 2237); C3 does not
  reconcile (74663 vs 74528); W23-S7 corpus control: 300 entry files vs 299.
- test (2/3): the step "Install build tools (pkg-config)" is `cancelled`, every
  later step `skipped`: no test ran. Not a 55-minute step timeout and not a
  test failure; a runner/infra cancel. Its sections were NOT exercised by this run.
- test (3/3), build, make strict: green.

## Cause
cscan.rxt (+1 file, +1 block, +135 case lines, all no-python-expression SKIP)
moved every count in the section (all pins except C3_PASS), and as the first
`pattern-esc` block exposed that C1's A-vs-B projection had no handling for the
seam. Reproduced locally with the exact section:
`bash tests/rxtsource/run_rxtsource_tests.sh` gave the same 12 FAILs.
The scandog lane ran only the cscan.rxt harness run, not the section (the
boilerplate's "new .rxt corpus file" rule).

## Fix
- tests/rxtsource/run_rxtsource_tests.sh: re-pinned CENSUS_FILES/BLOCKS/LINES
  (300/6219/74663), RUNSH_FILES/BLOCKS/LINES (276/6219/74663), C3_SKIP 52545,
  C3_SKIP_NOPYTHON 2372, C3_VERIFIABLE 24418, each with a note naming the file
  and why. Pins are the measured deltas of the one added file, not re-derived.
- C1 seam: leg A names its `pattern-esc` blocks (column 19); leg B's pattern
  field for exactly those blocks goes through new tests/rxtsource/esc_decode.py,
  an independent decoder of the seven-escape table plus the dump's re-escape,
  before the diff. The check still compares every byte; nothing was skipped. A
  missing/unquoted esc block makes the filter exit 1, which fails the check.
- tests/rxtsource/CLAUDE.md lists the new file. No cscan case was deleted.

## Validation
- `bash tests/rxtsource/run_rxtsource_tests.sh` (under boxlock): rc=0, 298
  passed, 0 failed; "C1 leg A == leg B ... on 6219 blocks".
- `make test-claudemd-size`, `test-spec-history`, `test-known-fail`,
  `test-startset` (1m45s), `test-vm`: all green (no `*** [..test-` lines).
- NOT run locally: `test-corpus` (full, ~13 min) and the remaining shard 2
  sections; CI's shard 2 never ran them, so the next CI run is their first look
  at cscan.rxt. The cscan.rxt-alone run was 135 passed 0 failed (scandog).
- Not sabotage-tested: the esc_decode filter was not given a planted-defect row.

## STATE AT HANDOFF
Branch lane/cired2, committed; rulings file read, last entry applied: none
(file was empty). Nothing OWED. Manager: merge, then watch shard 2 on the next
CI push (test-corpus, test-startset were green/run only as above).
