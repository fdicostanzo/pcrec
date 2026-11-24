# plantfix2 report: review r94's fixes to the runner plant pass

Lane plantfix2 (opus), 2026-11-24, branch lane/plantfix2 cut from the kit branch lane/memfn-plantcheck
@ c1efbe938. A D203 bug fix: no edit under src/, cli/, lib/ or memfn/src/, no emitted byte moved, no abi
event. Answers every FIX-NOW of review r94 (docs/dev/reviews/2026-11-24-r94-memfn-plantcheck.md, RULING
section). Evidence: docs/dev/lanes/plantfix2_evidence/ (the adapted mutant harness and its output).

## Summary

- PREMISE held: `python3 -I scripts/m6read_check_sab_anchors.py` at the cut printed
  `runner plants checked: 81 (89 edits, 4 runners), floor 81`, rc 0.
- ONE LOOP (CA-6): `tests/lib/plants.py` now has one decoder and ONE apply loop (`run_edits`) over a
  file store; `apply` runs it over the disk, `check` over an in-memory copy keyed by realpath and
  admitting exactly the files the runner's --plant copy holds (`--files`, CA-1). A third entry, `dump`,
  prints each edit decoded (FILE, FROM, TO as JSON strings) with a `twin` field (GF-1).
- The runners: `--plant-check [check|dump]`, handled BEFORE the work-directory mktemp in all four
  (PAR-1: no leaked dirs), passing `--labels <(declare -f plant_spec)` (CA-2: ORPHAN read from bash's
  own normal form, alternations split on ` | `, quotes stripped; a label that is no id is BAD LABEL),
  pres's `C0_FILES` (one variable, both modes) and wreply's `tracked_files` (one function, both modes)
  as the copy's file set (CA-1), and `PLANT_TWINS` (GF-1).
- The pass: discovery by CALLERS of tests/lib/plants.py tree-wide (`git ls-files -co --exclude-standard`,
  non-.md), cross-checked against plant_spec definers in any spelling, a mismatch UNREADABLE, with a
  declared `NOT_RUNNERS` table (4 evidence files, each with its reason; a vacuous entry is red) (CA-3);
  exact per-runner pins `PLANT_PINS` (38/35/6/2), red in both directions and naming the runner (CA-4);
  twin equality and id-collision/declaration checks (GF-1); concurrent runner calls in their own
  sessions under ONE shared deadline, the group killed and the pipes read with a bound (PAR-2/PAR-3).
- The STANDING CONTROL (CA-5): `--selftest`, run by [SABANCHOR] concurrently with the live run: 55
  planted-fault cases in hardlinked copies of the tracked tree, each red with its own status word (the
  clean copy green, one respelling green by design), plus 11 decoder/apply unit rows.
- GF-2: the RUNNER plant S1540 is S1544 (run_g2_win.sh plant_spec label + PLANTS, memfn/tests/NOTES.md);
  the mech S1540 is unchanged. The selftest restores the old id and shows it red as an ID COLLISION.
- Twin check: `runner plant twins checked: 39`, all 39 declared twins equal to their mech rows.
- Mutant gate: see "Self-test and mutants".

## Findings answered

| r94 id | answer |
|---|---|
| CHECKADEQUACY-1 | pres: `C0_SRC`/`C0_FILES` in run_g2_pres.sh, read by `--plant` (the cp loop) and `--plant-check` (`--files c0`); wreply: `tracked_files()` read by build_copy and `--plant-check` (`--files base`); check's store keyed by `os.path.realpath`. The critic's S9301 (`@c0/counts.py`) and S9302 (`vrun.c`/`./vrun.c`) are selftest cases, now MISSING FILE and edit 2/2 STALE. |
| CHECKADEQUACY-2 | `case_labels()` parses `declare -f plant_spec` (passed by each runner as `--labels`): label lines by bash's normal-form position, split on ` | `, quotes stripped; non-id labels are BAD LABEL. Selftest: 5 ORPHAN spellings + a glob label. |
| CHECKADEQUACY-3 | `discover()`: callers = non-.md files naming tests/lib/plants.py (git's view of the tree), definers = `^\s*(function\s+plant_spec\b|plant_spec\s*\(\s*\))`; caller-not-definer and definer-not-caller UNREADABLE; `NOT_RUNNERS` declares the 4 evidence files (a vacuous entry red). Selftest: fifth runners under tests/, scripts/, examples/, `function plant_spec {`, both mismatch directions, vacuous entry, respelled `plant_spec () {` (still read, green). |
| CHECKADEQUACY-4 | `PLANT_PINS = {runner: n}` (win 38, pres 35, proof 6, wreply 2): unpinned, not read, or off-pin each a named red line. Selftest: deleted / renamed / moved runner, PLANTS emptied, pin up, pin down. |
| CHECKADEQUACY-5 | `--selftest` (55 cases + 11 unit rows, pooled, output identical to `--serial`), run by [SABANCHOR]. Main's stale-FROM control is its case 2 (and stale cases in pres edit 2, `@c0/`, wreply PERT). Mutant gate below. |
| CHECKADEQUACY-6 | `run_edits` is the one loop; `check` = the loop over `MemStore`. Unit rows: 4-field wreply refuses (file untouched), `@@` in TO kept, pres `\\\\n` kept as `\\n`, win `\\n`/`\\&`, cumulative apply, ambiguous/stale/missing refusals with the old texts, check cumulative in memory only, dump fields. |
| CHECKADEQUACY-7 | S3092's comment now names the class it is caught by first (`reply id`), with form class as a possible co-fire. |
| CHECKADEQUACY-8 | [SABANCHOR] parses both `sabotages checked: N` and `runner plants checked: N`; separate verdict texts for a mech-half red, a plant-half red (mech clean), a missing plant population, and a red selftest; the ok text names both halves and the selftest tally. All four reds and the green driven (Validation). |
| GENERALFORM-1 | `dump` entry (plants.py's decoder, no second decoder); the pass compares each declared twin's edits to its row's SAB_FILE/BEFORE/AFTER (and site 2), after stripping C comments (the `/* SABOTAGE Sxxxx */` marker among them), `#` comments in .py targets, and whitespace runs. Every shared id must be declared (else ID COLLISION); a declared twin needs a row and a PLANTS entry; one id in two runners is red. 39/39 equal. Declaration spelling below. |
| GENERALFORM-2 | S1540 -> S1544 in run_g2_win.sh (label + PLANTS + the id comment, with R-1's range S1541-S1559) and memfn/tests/NOTES.md; one substitution, readers by `git grep S1540` (history/reviews/lane reports/tests/ci tsvs left: history, or the mech id). |
| PARALLELISM-1 | `--plant-check` handled before `WORK=$(mktemp ...)` in win, pres and proof (wreply already was). The before tree leaked 3 dirs per pass; after: 0 (Validation). |
| PARALLELISM-2 | One deadline for all runner calls (`PLANT_CHECK_TIMEOUT`, default 120 s, a selftest knob); each call drained by its own thread. Selftest: two runners hung, one 3 s deadline. |
| PARALLELISM-3 | `start_new_session=True`, `os.killpg(SIGKILL)` on the deadline, second `communicate(timeout=5)`, then the pipes closed ("ITS PIPES STILL HELD"). Selftest drills: exec'd hang, a grandchild heartbeat loop (must be DEAD after the pass), a grandchild that setsid()s away holding the pipes (red within 15 s). |
| GENERALFORM-3 (DOC) | tests/lib/CLAUDE.md, tests/memfn/CLAUDE.md, scripts/INDEX.md, plants.py docstring: "the four shell runners" (the g2 python PLANTS named as outside). tests/mech/CLAUDE.md names the plant pass and its control. |

TWIN DECLARATION SPELLING: a runner-side variable `PLANT_TWINS` beside `PLANTS`, passed as `--twins`
to `plants.py dump`, which writes it as each edit row's `twin` field. Why there: (1) the drift r94
found was always the RUNNER copy lagging, so the declaration lives with the copy that can lag; (2) the
mech dir is the id registry and its 1404 rows are read by run_sabotage_matrix.sh, whose schema this lane
may not touch (and a new SAB_ field would need its reader); (3) the mech headers' "same plant as ..."
is prose, and reading prose is exactly the spelling-discovery class CA-3 retired. pres declares
`PLANT_TWINS="$PLANTS"` (all 35 are twins), proof 4 ids, win and wreply none.

## Self-test and mutants

OWED-FILL

## Twin check

`runner plant twins checked: 39 (declared twins of a tests/mech/sabotages row)`, and `all runner plants
apply, every shared id is an equal declared twin`: pres 35 + proof 4 (S1221, S1224, S1225, S1419) = 39,
the 39 true twins r94's generalform critic counted (16 byte-equal, 23 equal modulo the SABOTAGE marker or
a comment). The 40th shared id, S1540, is gone (S1544 has no mech row). Red drills in the selftest: the
runner's TO moved (S1221), the row's FROM moved (S3045), the row's file moved and its site count grown
(S1221), an undeclared shared id, the S1540 collision restored, a declared twin without a row, a
declared twin not in PLANTS, one id in two runners.

## Validation

OWED-FILL

## STATE AT HANDOFF

OWED-FILL
