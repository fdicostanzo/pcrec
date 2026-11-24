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
- The STANDING CONTROL (CA-5): `--selftest`, run by [SABANCHOR] concurrently with the live run: 56
  planted-fault cases in hardlinked copies of the tracked tree, each red with its own status word (the
  clean copy green, one respelling green by design), plus 11 decoder/apply unit rows.
- GF-2: the RUNNER plant S1540 is S1544 (run_g2_win.sh plant_spec label + PLANTS, memfn/tests/NOTES.md);
  the mech S1540 is unchanged. The selftest restores the old id and shows it red as an ID COLLISION.
- Twin check: `runner plant twins checked: 39`, all 39 declared twins equal to their mech rows.
- Mutant gate: 65 mutants (the critic's 35 re-spelled + 30 on new clauses): 63 killed, 2 argued
  EQUIVALENT (P15, N15), 0 survived.

## Findings answered

| r94 id | answer |
|---|---|
| CHECKADEQUACY-1 | pres: `C0_SRC`/`C0_FILES` in run_g2_pres.sh, read by `--plant` (the cp loop) and `--plant-check` (`--files c0`); wreply: `tracked_files()` read by build_copy and `--plant-check` (`--files base`); check's store keyed by `os.path.realpath`. The critic's S9301 (`@c0/counts.py`) and S9302 (`vrun.c`/`./vrun.c`) are selftest cases, now MISSING FILE and edit 2/2 STALE. |
| CHECKADEQUACY-2 | `case_labels()` parses `declare -f plant_spec` (passed by each runner as `--labels`): label lines by bash's normal-form position, split on ` | `, quotes stripped; non-id labels are BAD LABEL. Selftest: 5 ORPHAN spellings + a glob label. |
| CHECKADEQUACY-3 | `discover()`: callers = non-.md files naming tests/lib/plants.py (git's view of the tree), definers = `^\s*(function\s+plant_spec\b|plant_spec\s*\(\s*\))`; caller-not-definer and definer-not-caller UNREADABLE; `NOT_RUNNERS` declares the 4 evidence files (a vacuous entry red). Selftest: fifth runners under tests/, scripts/, examples/, `function plant_spec {`, both mismatch directions, vacuous entry, respelled `plant_spec () {` (still read, green). |
| CHECKADEQUACY-4 | `PLANT_PINS = {runner: n}` (win 38, pres 35, proof 6, wreply 2): unpinned, not read, or off-pin each a named red line. Selftest: deleted / renamed / moved runner, PLANTS emptied, pin up, pin down. |
| CHECKADEQUACY-5 | `--selftest` (56 cases + 11 unit rows, pooled, output identical to `--serial`), run by [SABANCHOR]. Main's stale-FROM control is its case 2 (and stale cases in pres edit 2, `@c0/`, wreply PERT). Mutant gate below. |
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

THE SELF-TEST (`python3 -I scripts/m6read_check_sab_anchors.py --selftest`; `--serial` for one by one).
A copy of the tracked files the pass reads (`SELFTEST_TREE`, working-tree content, so an edited checker
is the one tested; of tests/mech/sabotages only the rows whose id a pinned runner names), one git index
in it, then one HARDLINKED copy per case (faults write by replace, never in place). Each case runs
`--plant-only` in its copy and must exit with its rc AND print each of its status words; every case also
asserts its TMPDIR is empty afterwards (PAR-1 standing), and the two grandchild drills assert the hung
group is DEAD (a heartbeat file that must stop changing). 56 cases: clean (green); stale FROM in win's
spec, pres edit 2/2 (the source moved), `@c0/` (census0.py moved), a wreply PERT; ambiguous; missing
file; `@c0/` outside the copy's set; one file by two spellings; undecodable; NO SPEC; 5 ORPHAN spellings;
BAD LABEL; runner deleted / renamed / moved; respelled `plant_spec () {` (green: still read); PLANTS
emptied; pin up; pin down; 4 fifth-runner shapes; both caller/definer mismatches; a vacuous NOT_RUNNERS
entry; the mode printing garbage, a well-formed lie, exiting 3, exiting 0 silently, stderr in check,
stderr in dump, the right answer with exit 3, its summary twice, an unparsable summary, check and dump
naming different plants, dump dying, reading only the first id; exec'd hang, grandchild hang (killed),
grandchild escaping the group (bounded pipes), two hung runners on one deadline; 9 twin/collision
drills (Twin check). 11 unit rows on plants.py itself (CA-6's decoder rows among them).

WALL TIME: 16-20 s pooled (10 workers; base copy 0.4 s; measured repeatedly at box load 5-35, the box
shared by 11 users), 52 s serial; pooled and serial outputs byte-identical (`cmp`, stdout; the wall
lines go to stderr). In [SABANCHOR] it runs CONCURRENTLY with the live run (the mech half ~14 s).

THE MUTANT GATE: docs/dev/lanes/plantfix2_evidence/harness.py, the critic's harness adapted: its faults
F1-F14 are now the self-test's cases, so it keeps the MUTANTS, re-spelled onto the fixed code's site for
the same clause, plus 30 on the clauses this fix added. Kill = the live run (both halves, what
[SABANCHOR] runs) OR the self-test exits non-zero, over a full copy of the tracked tree; the unmutated
control must be green first (it was, both runs).

| set | mutants | killed | equivalent | survived |
|---|---|---|---|---|
| the critic's 35 (Q1-Q20, P1-P15) | 35 | 34 | 1 (P15) | 0 |
| added (Q9b, P1b-P1d, P4b, N1-N25) | 30 | 29 | 1 (N15) | 0 |
| total | 65 | 63 | 2 | 0 |

Run 1 (all 65, on the code before the last two cases): 61 killed, survivors Q19, P4, P15, N15
(evidence `mutants_run1.out`). Q19 (UNDECODABLE not counted bad) had no undecodable edit at pass level,
and P4 (check's stderr ignored) was masked because the stderr case wrote stderr in BOTH modes, so the
dump half caught it: the self-test gained "an undecodable edit" and the stderr case was made check-only
(no other mutant's kill rested on that case: run 1 names it only for P4b, killed by its own dump case).
Run 2 (the 4 survivors, final code, `mutants_run2_survivors.out`): Q19, P4 KILLED; P15, N15 survive:

- P15 EQUIVALENT (`nplants += len(ids)` for `nplants += P`): the line is reached only past the
  INCONSISTENT guard `if len(ids) != P or ...: ... break`, so `len(ids) == P` wherever it runs.
- N15 EQUIVALENT (`communicate(timeout=budget)` for the shared deadline's remainder): every runner call
  is waited in its own thread, all submitted in one burst, so a per-call budget and the shared deadline
  differ only by the threads' start skew (milliseconds); the "two runners hang" case is ~3 s under both.
  The shared deadline is kept as the contract it states: it is the one that stays right if the waits
  ever become sequential again (PAR-2's original shape).

Mapping notes: Q7 (OK if count >= 1), Q14 (apply refuses only on 0) and Q20 (AMBIGUOUS not bad) were
three sites in the old two-loop code; in the one loop Q7 is the loop's own `c != 1` test (both modes),
Q14 is now the APPLY side's consumer (`if st != 'OK'` -> `if st == 'STALE'`: exit 0 with the edit
unapplied), Q20 the check side's count; Q9 (not cumulative) is the loop's write, Q9b check's store
alone; P1 (floor 0) is "pins ignored" (P1b-P1d each pin branch); P13 (timeout not recorded) is the
`rc is None` branch.

## Twin check

`runner plant twins checked: 39 (declared twins of a tests/mech/sabotages row)`, and `all runner plants
apply, every shared id is an equal declared twin`: pres 35 + proof 4 (S1221, S1224, S1225, S1419) = 39,
the 39 true twins r94's generalform critic counted (16 byte-equal, 23 equal modulo the SABOTAGE marker or
a comment). The 40th shared id, S1540, is gone (S1544 has no mech row). Red drills in the selftest: the
runner's TO moved (S1221), the row's FROM moved (S3045), the row's file moved and its site count grown
(S1221), an undeclared shared id, the S1540 collision restored, a declared twin without a row, a
declared twin not in PLANTS, one id in two runners.

## Validation

All on the Mac (gcc-16), TMPDIR=$PCREC_TMPDIR/scratch/plantfix2/tmp, under worktrees/.mac-suite.lock
(taken with an owner line naming plantfix2, released after).

- LIVE (`python3 -I scripts/m6read_check_sab_anchors.py`, rc 0):
  `sabotages checked: 1404 (1463 anchor sites)` / `all anchors resolve` /
  `runner plants checked: 81 (89 edits, 4 runners, each at its pin)` /
  `runner plant twins checked: 39 (declared twins of a tests/mech/sabotages row)` /
  `all runner plants apply, every shared id is an equal declared twin`. ~14 s (mech half), plant half ~1.5 s.
- MECH SECTION BYTE-IDENTICAL: before (c1efbe938, git archive) vs after, the output up to the
  `runner plants checked:` line: `diff` empty (md5 cc3c5370... both). And under planted mech faults (S01's
  anchor made stale + an unsourceable row S9999, in a before copy and an after copy): `diff` empty
  (`UNREADABLE ROWS: 1 ... DOES NOT SOURCE: broken`, `STALE ANCHORS: 1 ... S01 ... ANCHOR NOT FOUND`).
- --plant-check BEFORE vs AFTER (each runner, ROOT normalised): win differs ONLY in
  `S1540 1/1 OK 1 memfn/src/ofsskip.c` -> `S1544 1/1 OK 1 memfn/src/ofsskip.c`; pres, proof, wreply: diff
  empty. Leaks: the before tree's --plant-check left 3 work dirs per pass (g2pres, g2win, proof, every
  run: 9 dirs from 3 runs), the after tree 0 (and the self-test asserts it per case).
- TARGETED --plant: `bash memfn/tests/run_g2_win.sh --plant S1544` (after) and the before tree's
  `--plant S1540` (LIB = this build): both `PLANT S1544|S1540 RED (driver passed failed: 6788 152): FAIL:
  site mass#61 PLAN: layout U n 9 lo 0 F 0: got 9 wrote 1 missed 0, want 2`, rc 0. Unchanged but the id.
- [SABANCHOR] BLOCK, isolated (the block's own lines run with stub ok/bad): green on this tree (`PASS:
  ... all 1404 sabotage rows' anchors resolve and all 81 runner plants apply at their pins, every shared
  id an equal declared twin; its --selftest is green (56 cases, 11 unit rows, 0 failed) ...`); MECH-half
  red (copy with S01 stale), PLANT-half red (copy with a stale win FROM; text says the mech half's 1404
  rows resolve), SELFTEST red (copy with mutant Q5: live green, selftest red): each its own FAIL text.
- `make strict CC=gcc-16`: 0 warnings/errors in the compile; rc 2 from the kit target table check only
  (`targets-check: MISMATCH the host family MF_FAM_AARCH64 compared no target ...`), PRE-EXISTING on the
  Mac (the brief), not fixed.
- `make test-codegen CC=gcc-16`: `run_group: 19/22 scripts passed`, `make: *** [test-codegen] Error 1`;
  the 3 reds are exactly the PRE-EXISTING Mac-only run_size_term.sh, run_case_spelling_identity.sh,
  run_residual_twins.sh (not fixed); its [SABANCHOR] line PASS (55 cases then; the block re-run above on
  the final tree, 56 cases, PASS).
- `scripts/check_claudemd_size.sh --all`: 440 files within limits.
- NOT RUN: `make test` in full; the Linux boxes / CI (the self-test uses only python3, bash, git and
  `date`; os.link, start_new_session, os.setsid are POSIX). The full battery is the manager's at merge.

## STATE AT HANDOFF

STATE: delivered. Branch lane/plantfix2, tip in the handback. Last ruling applied: R-1 (S1544 free;
the kit's runner-plant range S1541-S1559 named in run_g2_win.sh's id comment). OWED: none.

Files: tests/lib/plants.py; scripts/m6read_check_sab_anchors.py; memfn/tests/run_g2_win.sh,
run_g2_pres.sh; tests/memfn/run_proof.sh, run_wreply.sh; tests/codegen/run_codegen_tests.sh
([SABANCHOR] only); docs: tests/lib/CLAUDE.md, tests/memfn/CLAUDE.md, tests/mech/CLAUDE.md,
memfn/tests/NOTES.md, scripts/INDEX.md, the lanes history index; evidence plantfix2_evidence/.

For main / the next round:
- GF-2 NOTICE (r94 RULING): the runner plant S1540 is now S1544; the mech S1540 (CMP-13) is untouched.
- Readers that were NOT edited and still say S1540 for the runner plant are history (lane reports,
  reviews, memfn/docs/journal.md); tests/ci's two tsvs name the MECH S1540, correctly.
- 38 mech headers still say "one source of the text" (tests/mech/sabotages, outside this lane's edit
  scope): the text is two copies, now HELD equal by the twin check; rewording them is the mech
  owner's.
- NOT_RUNNERS: the census counts any non-.md file that names tests/lib/plants.py, so a new script or
  comment naming the applier goes red until it is a runner or a declared NOT_RUNNERS entry (by design:
  the [SABANCHOR] block's own comment was reworded during this lane for that reason).
- PLAN items r94 routed elsewhere (plant_want for run_g2_win.sh, kit id ranges in the registry, mut.py's
  282 mutants, a --plants pool) are untouched.
