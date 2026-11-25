# plantfix report: one plant applier, the runner plant pass, the four re-aims (FUW-12's class)

Lane plantfix (opus), 2026-11-24, branch lane/plantfix cut from lane/memfn-plantcheck @ b9f81ef80.
A D203 bug fix: no edit under src/, cli/, lib/ or memfn/src/, no emitted byte moved, no abi event.
Triage it answers: docs/dev/lanes/plantri_report.md. Evidence: docs/dev/lanes/plantfix_evidence/.

## Summary

- PREMISE held: plantri's census (`python3 -I plantri_evidence/plant_census.py TREE`) at the cut
  reads 81 plants, 4 STALE (S1423, S3092 in run_g2_win.sh; S3064 edit 1 in run_g2_pres.sh; S1224
  in run_proof.sh), 89 edit rows.
- ONE APPLIER: `tests/lib/plants.py`. The four runners' private heredoc appliers are gone; their
  `--plant`/`--plants` modes call `plants.py apply`, and each gains a `--plant-check` mode that hands
  the SAME edit list (one shell function, `plant_edits`, used by both modes) to `plants.py check`.
- PLANT PASS: `scripts/m6read_check_sab_anchors.py` now discovers every `plant_spec` runner, runs its
  `--plant-check` (the four concurrently, ~0.3 s) and prints its own population line,
  `runner plants checked: 81 (89 edits, 4 runners), floor 81`, held to a literal floor of 81. It
  fails on STALE, AMBIGUOUS, MISSING FILE, NO SPEC, UNDECODABLE and ORPHAN, and on a runner that
  defines `plant_spec` without a `--plant-check` mode (never run). The mech rows' output is
  byte-identical (control M).
- RE-AIMS: all four re-aimed at today's code; none hit the STOP rule (every guarded site still
  exists). Each goes red under its runner's plant mode for the reason the plant names (Re-aims).
- CONTROLS C0-C6 and M: each verdict as designed (Controls).
- R-1 (a) twin census: of 40 runner plants with a same-id mech row, 16 are EQUAL, 23 differ only by
  comment text (the mech rows' `/* SABOTAGE Sxxxx */` markers), and S1540 is an ID COLLISION, not a
  drift: the kit's S1540 (run_g2_win.sh, ofsskip.c) and pcrec's mech S1540 (emit_dfa.c,
  cmp13 align entry) are two different sabotages sharing one id. R-1 (b): see Validation.

## Mechanism

WHERE THE MODULE LIVES: `tests/lib/`, not `memfn/tests/`. Two of the four runners are pcrec-side
(`tests/memfn/run_proof.sh`, `tests/memfn/run_wreply.sh`, whose plants target `src/gen/`), the
checker is `scripts/`, and the kit's own runners already source `tests/lib/` (`cc_resolve.sh`,
`timeout_bin.sh`), so `tests/lib/` adds no new dependency direction.

`tests/lib/plants.py` (its docstring is the spec):

- `apply DIALECT BASE [C0DIR] -- EDIT...`: the edits in order, cumulative, each FROM exactly once or
  exit 1 at that edit with the runner's old refusal text on stderr.
- `check DIALECT BASE [C0DIR] RUNNER -- (--plant ID N EDIT...)...`: count only, in memory, per
  plant from a fresh read, edits cumulative as in apply. One TSV row per edit
  (`ID EDIT/N STATUS COUNT PATH`), plus ORPHAN rows for `plant_spec` case ids that `PLANTS` does
  not list, then `plant-check: P plants, E edits, B bad`; exit 0 iff B = 0.
- Three DIALECTS, each the runner's pre-plantfix rule bit for bit (unifying them is a separate
  decision, plantri "Fix shape" 3): `win` (win, proof: the shell's `%%@@*` / `#*@@` split, `\n`
  then `\&`), `pres` (`\\n` kept as the C escape, `@c0/X` the census copy), `wreply` (exactly three
  fields, `\n` only).

Runners (each: `plant_edits ID` sets `EDITS=(...)`; `--plants` and `--plant-check` both build from it):

| runner | edits per plant | apply call | `--plant-check` base |
|---|---|---|---|
| memfn/tests/run_g2_win.sh | the one spec | `apply win $WORK/src` | memfn/src |
| memfn/tests/run_g2_pres.sh | one per plant_spec line | `apply pres $WORK/src $WORK/c0` | memfn/src, @c0 = docs/design/memfn/span_pick |
| tests/memfn/run_proof.sh | the one spec | `apply win $WORK/src` | memfn/src |
| tests/memfn/run_wreply.sh | S1414 alone; else both PERTS then the spec | `apply()` -> `apply wreply DIR` (also the main path's perturbed copy) | the tree root |

run_wreply.sh's box-lock `exec` and its `WORK` mktemp moved below the definitions (no behaviour
change for any other mode), so `--plant-check` takes no lock and builds nothing.

THE PASS (`scripts/m6read_check_sab_anchors.py`, after the unchanged mech pass): discovery is every
`*.sh` under `tests/` and `memfn/tests/` with a line starting `plant_spec() {`; each is run as
`bash RUNNER --plant-check` with `CC_RESOLVE_ANNOUNCED=1` (cc_resolve's Mac notice) so that ANY
other stderr, an exit code other than 0/1, a missing or second summary line, a malformed row, or a
summary that disagrees with the rows (ids, bad count, exit code) makes the runner UNREADABLE. The
population line is the pass's own; `PLANT_FLOOR = 81` is a literal (raise it with the plants).
Exit code: 1 if the mech pass or the plant pass fails. [SABANCHOR]
(`tests/codegen/run_codegen_tests.sh`) reads the exit code and prints the whole output on red, so
it carries the plant pass with no edit there (that file is outside this lane's edit list; its
ok-line wording still names only the sabotage rows, a wording follow-up for its owner).

PARALLELISM (owner ruling 2026-11-23): the four `--plant-check` runs are started together
(`subprocess.Popen`) and collected; measured 0.34 s for the four, at load 22. The script's wall
is the mech pass's (~14.6 s at the base, unchanged); nothing further to parallelise in the plant
pass.

What it does NOT prove (plantri "Fix shape" 4): an applying plant is not a reaching plant; OK means
"the plant still applies exactly once". Whether each plant still goes red is the `--plants` run's
question (measured once here, Validation).

PROPOSAL (R-1 (a), not built): the general form of the twin check is "a runner plant and its
same-id mech row produce the same planted file, up to comments". It is more than a few lines (the
mech row must be sourced by bash and applied by mech's rule beside the runner's edits;
`twin_census.py` is ~100 lines of evidence), and its population needs a ruling first: 23 of 40
twins differ by the mech rows' SABOTAGE comments, so the check must compare code-only, and S1540
shows the id space is not one namespace (kit S1540-S1559 vs a pcrec mech S1540), so "same id" is
not "same plant" until the collision is ruled. Recommended shape if ruled: a `twins` sub-entry of
`plants.py check` taking the mech row path, printing TWIN-EQUAL / TWIN-DIFFERS rows the pass
counts.

## Re-aims

Each found by `git log -S` on the old FROM; none hit the STOP rule.

| plant | moved by | guarded | re-aimed FROM (decoded) | TO |
|---|---|---|---|---|
| S1423 (win) | d4b25d950 (bsu2: B-hors stores its probed index once, `w->hix = plan_ix(w, w->hl)`) | D-hors's bound one short: `c + K > n` as `c + K - 1 > n`, the probe reads s[n] | `    int ih = w->hix;` + the unchanged bound line in `d_hors_head` (the first line keeps it unique: `find_head` holds the same bound line, control C6) | unchanged but its first line: the bound rendered `if (C + chi > N) break;`, still different from the callers' `if (!(C + chi < N)) break;` (wf_bound) |
| S3092 (win) | 4d00fccfe (span4kfix SEAM-1: the answered branch as statements) | frame_row swapped E-find <-> E-generic on REPORT sites: G2's form class | `            reply_frame(fp, out, rows);` / `            rc = 0;` in the answered branch (`if (ok && !art->err[0] && rows_hold(...))`) | the same swap statement after them |
| S1224 (proof) | 4d00fccfe (the ask as one statement) | a proof bit set only by a SIMD layer: C-PROOF | its mech twin's SAB_BEFORE (tests/mech/sabotages/S1224_proof_bit_simd_only.sh, re-anchored ad5a89b26) | the twin's SAB_AFTER |
| S3064 edit 1 (pres) | 4d00fccfe (the ALL_PRESENT branch's refusal block) | C2's decision plant: the reply says ver_len + 1; EXTENT must red | site 1 of its mech twin (S3064_reply_claims_one_more_position.sh, ad5a89b26) | the twin's SAB_AFTER (site 1); edit 2 was not stale and is unchanged |

Equality with the twins, through the applier (`plantfix_evidence/twincmp.sh TREE`): S1224's
planted compose.c is byte-equal to the twin's; S3064's differs from the twin's only by edit 2's
missing `/* SABOTAGE S3064 */` comment (edit 2 untouched by this lane).

CATCHES (each under its runner's plant mode on the after tree; Validation has the commands):

| plant | command (after tree = a clone of lane/plantfix @ 9d086e8e6) | verdict line | the reason the plant names? |
|---|---|---|---|
| S1423 | `bash memfn/tests/run_g2_win.sh --plant S1423` (and in `--plants`) | `PLANT S1423 RED   (driver passed failed: 6780 160): FAIL: site parked#107 PLAN: layout U n 1 lo 0 F 0: got 0 wrote 1 missed 0, want -1` | yes: the bound one short lets a candidate whose window needs s[n] through (layout U, n 1); 160 failures in the window family |
| S3092 | `bash memfn/tests/run_g2_win.sh --plant S3092` | `PLANT S3092 RED   (driver passed failed: 6940 0): FAIL: site 40: reply id: method's emptiness is not exactly the rows no T-FIND row decides` | yes: the runner prints only the first FAIL; a re-run with the work dir kept tallies the generator's FAIL classes as `form class` 916, `reply id` 1832, `cell` 252, so the form class the plant names is red |
| S1224 | `bash tests/memfn/run_proof.sh --plants` | `PLANT S1224 RED   (proof_check / proof_run passed failed: 42 101 / 401 0): FAIL: C site 2 C-PROOF: proven[] differs across the layers` | yes: C-PROOF |
| S3064 | `bash memfn/tests/run_g2_pres.sh --plant S3064` | `PLANT S3064 RED   (family; oracle RED (1 oracle: rows=28249 violations=71)): FAIL generic.default site 32 (precheck): EXTENT: part at 0 len 32: position 30 is NOT compared, the reply's stretch is [22, 31)` | yes: `RED` (not "RED BUT NOT BY ITS DETECTOR"), so plant_expect's `: EXTENT: ` matched; the same EXTENT line as the mech twin's SAB_DOC_FIGURE |

## Controls

All on fresh `git archive HEAD` copies under the scratch dir, never the live tree
(`bash docs/dev/lanes/plantfix_evidence/controls.sh TREE BASE_CHECKER SCRATCH`; output committed as
`plantfix_evidence/controls.out`; BASE_CHECKER is the cut's own checker, from a frozen clone):

| control | sabotage | verdict line(s) |
|---|---|---|
| C0 positive | none | rc=0; `runner plants checked: 81 (89 edits, 4 runners), floor 81`; `all runner plants apply` |
| C1 stale FROM | S1401's FROM gains `XYZZY_STALE` in run_g2_win.sh | rc=1; `BAD RUNNER PLANTS: 1` / `memfn/tests/run_g2_win.sh S1401 edit 1/1 STALE count 0 memfn/src/window.c` |
| C2 out of discovery | run_wreply.sh's `plant_spec() {` renamed | rc=1; `runner plants checked: 79 (85 edits, 3 runners), floor 81`; `RUNNER PLANT POPULATION 79 IS BELOW ITS FLOOR 81 ...` |
| C3 runner deleted | run_proof.sh removed | rc=1; `runner plants checked: 75 (83 edits, 3 runners)`; `... 75 IS BELOW ITS FLOOR 81 ...` |
| C4 no mode | a new runner defining plant_spec, no --plant-check | rc=1; `UNREADABLE RUNNERS: 1` / `tests/memfn/run_nomode.sh DEFINES plant_spec BUT HAS NO --plant-check MODE`; the runner was not run |
| C5 orphan | a `S9999)` case not in run_proof.sh's PLANTS | rc=1; `tests/memfn/run_proof.sh S9999 edit - ORPHAN` |
| C6 ambiguous | S1423's FROM cut to the bound line alone | rc=1; `memfn/tests/run_g2_win.sh S1423 edit 1/1 AMBIGUOUS count 2` |
| M mech identity | none | the new script's mech lines equal the cut's checker output on the same copy: SAME (`sabotages checked: 1404 (1463 anchor sites)`) |

APPLIER EQUIVALENCE (the module against the four deleted heredocs, not a pass control):
`plantfix_evidence/applier_compare.sh BEFORE NEW` (output `applier_compare.out`) applied every plant (and wreply's PERTS alone) with the
OLD heredoc text extracted from the cut's runners and with `plants.py apply`, each on a fresh copy,
and compared the trees and exit codes: `compare: same=82 diff=0` (81 plants + PERTS; the four
stale plants refuse identically, rc=1). And the module's `check` reproduces plantri's census: 81
plants, 89 edits, the same 4 STALE.

## Validation

All on the Mac (M1 Max, gcc-16), under `worktrees/.mac-suite.lock` (directory form, owner line
naming this lane; released at the end). `scripts/boxlock status`: "no flock(1) on this box; nothing
is locked".

- `make strict` (worktree): rc 2, `strict: the kit's target table check did not pass` /
  `targets-check: MISMATCH the host family MF_FAM_AARCH64 compared no target against gcc -march`.
  The `-Werror -Wshadow` compile loop (which runs first, under `set -e`) passed; the red is the
  kit's target table check on an aarch64 host, and the cut (frozen clone at b9f81ef80) gives the
  identical three MISMATCH lines, rc 2. Pre-existing on this box; this lane edits no C.
- `make test-codegen` (worktree): `run_group: 19/22 scripts passed`, `make: *** [test-codegen]
  Error 1`. The [SABANCHOR] block (inside run_codegen_tests.sh, which PASSED) printed `PASS:
  [SABANCHOR] scripts/m6read_check_sab_anchors.py: all 1404 sabotage rows' anchors resolve ...`
  with the plant pass inside the same rc. The three red scripts are `run_size_term.sh` (K100:
  `re.error: multiple repeat`, this box's python 3.9), `run_case_spelling_identity.sh` (`empty
  .text`, Mach-O) and `run_residual_twins.sh` (no PLT on Mach-O); each re-run alone on the cut's
  frozen clone is red the same way (rc 1; 39/1, 2 passed 33 failed, 7/2). None is touched by this
  lane. Linux test-codegen is not run here (the manager's merge battery).
- `python3 -I scripts/m6read_check_sab_anchors.py` at the delivered tree: `sabotages checked: 1404
  (1463 anchor sites)` / `all anchors resolve` / `runner plants checked: 81 (89 edits, 4 runners),
  floor 81` / `all runner plants apply`, rc 0. Wall: the plant pass's four runners 0.34 s
  (concurrent, load 22); the whole script ~15-20 s, which is the unchanged mech pass (the cut's
  script alone: 14.6 s).
- Each runner's `--plant-check` (the quick mode this lane adds): win 38 plants / 38 edits, pres 35 /
  41, proof 6 / 6, wreply 2 / 4, each `0 bad` after the re-aims (before them: 2, 1, 1, 0 bad).

RUNNERS BEFORE/AFTER (driver `plantfix_evidence/run_side.sh`; outputs `plantfix_evidence/runs/`).
BEFORE = a frozen clone of the cut b9f81ef80, each id run alone (`--plant ID`, because the cut's
`--plants` stops at its first stale plant); AFTER = a clone of 9d086e8e6 (the code as delivered),
`--plants`. Compared on the `PLANT` lines:

| runner | before | after | diff of PLANT lines |
|---|---|---|---|
| run_proof.sh | 5 RED, S1224 `FAIL: S1224: the plant does not apply` | `--plants` rc 0, 6 RED, 66 s | `> PLANT S1224 RED ... C-PROOF` only |
| run_g2_win.sh | 36 RED, S1423 and S3092 `the plant does not apply` | `--plants` rc 0, 38 RED, 1440 s | `> PLANT S1423 RED ...`, `> PLANT S3092 RED ...` only |
| run_g2_pres.sh | 34 plants' lines, S3064 `the plant does not apply` | `--plants` rc 1, 2315 s | `> PLANT S3064 RED ... EXTENT ...` only |
| run_wreply.sh | `FAIL: S1413: the planted copy does not build` (and S1414) | the same (`--plants` exits at the first) | identical failure; see below |

run_g2_pres.sh's rc 1 is the same seven plants on both sides, each `RED BUT NOT BY ITS DETECTOR` (or
`MOVED A PASS IT MUST LEAVE UNCHANGED`): S3012, S3098-S3103, whose detectors are x86 SIMD-level
cells and the kernel-address recording driver ("the recording driver printed no cells line"),
which an aarch64 host cannot run. Identical before and after; a Linux run is where they are
scored. run_wreply.sh cannot build a tree copy on the Mac at all (BSD tar: `Option
--ignore-failed-read is not supported`), before and after alike; with a scratch PATH shim `tar`
that drops that one flag (`plantfix_evidence/tar_shim.sh`, run by `run_wreply_side.sh`; outputs
`runs/*_run_wreply.shim.*`), both sides print the identical `PLANT S1413: RED (... P-b ...)`,
`PLANT S1414: RED (... run-pinned ...)`, `plants: 2 of 2 red`, rc 0.

R-1 (b): every plant's red was measured once here as a by-product (all 81 run): 81 apply; on the
Mac 74 go red by their own detector, the 7 pres SIMD-level plants above are host-limited (red, not
by their detector) and need the Linux run.

R-1 (a) census (`python3 -I plantfix_evidence/twin_census.py TREE`, output `twin_census.tsv`; it
imports `plants.decode` and evaluates each runner's own `plant_edits`, its edit counts equal the
runners' `--plant-check` counts, 38/41/6/4): 40 twins; EQUAL 16 (win 0 of 1, pres 13 of 35, proof 3 of
4, wreply none have twins), comment/whitespace-only 23 (the mech rows' `/* SABOTAGE Sxxxx */` markers), and S1540
whose code differs because the two S1540s are different sabotages (an id collision for the kit
manager and main to rule).

## STATE AT HANDOFF

- Branch lane/plantfix, committed (code at 9d086e8e6; docs, evidence and this report after it).
  Report: docs/dev/lanes/plantfix_report.md; evidence: docs/dev/lanes/plantfix_evidence/; history
  index line added to docs/dev/history/claude_md/docs__dev__lanes.md.
- Rulings file docs/dev/lanes/plantfix_rulings.md re-read before each commit, before the long runs
  and before this report: one entry, R-1 (the twin census and the red question); R-1 applied
  (census reported, twin check proposed and not built, (b) measured as a by-product).
OWED: none
- Not run here: Linux `make test-codegen` / the merge battery (the manager's), and a Linux
  `--plants` for the seven host-limited pres plants.
- For the reviewer (r94): [SABANCHOR]'s ok-line in tests/codegen/run_codegen_tests.sh still names
  only the sabotage rows (outside this lane's edit list); tests/mech/CLAUDE.md does not yet mention
  the plant pass; the S1540 id collision.
- Process slip, disclosed: two of my wait loops used `pgrep -qf` (read-only, no kill; the scripts/
  rule says never `pgrep -f`), and one self-matched its own command line, so I stopped it with
  TaskStop. No process was signalled.
