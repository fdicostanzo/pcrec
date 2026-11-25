# Review r94 memfn-plantcheck (code, light) — DRAFT, dispositions PROPOSED


## RULING (kit manager, 2026-11-24)

- FIX-NOW as proposed, for a fix lane (plantfix2, opus) on lane/memfn-plantcheck: CA-1 to CA-6, CA-7 (the comment reword), CA-8, GF-1, GF-2, PAR-1, PAR-2 and PAR-3. CA-5's critic harness (35 mutants) is the fix lane's acceptance gate.
- The open item is ruled YES (GF-1). Twin equality is enforced in the same pass, through a plants.py `dump` entry (no second decoder): normalise the SABOTAGE marker and comments, and every shared id must be a declared twin.
- GF-2: renumber the RUNNER plant S1540 to the free kit-range id S1544, with a simultaneous substitution. The mech id stays. This goes to main as a notice (the mech dir is the id registry).
- PLAN (to main): a plant_want table for run_g2_win.sh (CA-7); recording the kit id ranges where the registry can see them (GF-2); mut.py's 282 unchecked mutants, routed to the predicate manager via main (GF-3); a --plants pool on its trigger, the next full sweep owed (PAR-5, D77).
- DOC: GF-3 (scope the claim to "the four shell runners").
- Also in the fix lane, from plantfix's own report: tests/mech/CLAUDE.md names the plant pass, and briefs say poll artifacts, never pgrep.
- Process lesson (main's): when a branch carries commits beyond the lane, the review BASE is the lane's parent, not the merge-base.
- plan.md line cites are rewritten to tags (PL14).

- Subject: lane plantfix on lane/memfn-plantcheck. Frozen code SUBJECT = 14e8c419b; LANEBASE = b9f81ef80
  (the lane's parent; `git merge-base main` = main HEAD e11c5f4ef, but the branch also carries the kit's
  arch-review commits, so the review diff is LANEBASE..SUBJECT, 13 files).
- FREEZE NOTES: (1) main's ruling (one kit lane, floor, 4 re-aims, a stale-FROM control) has no file record
  visible to the round (launch message only; any copy is in the denied journal/responses). (2) The branch moved
  during setup (2dd4cf4af, 8bd727eab), journal-only. FREEZE DRIFT: none (decisions.md/plan.md unchanged
  c0f8bd689..main at hand-back).
- Review tree built once, `nice make -j2 CC=gcc-16`, rc 0. Baseline anchor script at SUBJECT: rc 0,
  `runner plants checked: 81 (89 edits, 4 runners), floor 81`, ~14 s.

## Lenses as run

| lens | model | question | why |
|---|---|---|---|
| check adequacy | opus | can the pass + plants.py `check` + `--plant-check` go green while a plant would not apply in the real mode; per-clause mutation; the 4 re-aims in real mode | the subject IS a checker; >5 plant rows touched by its population |
| general form (bug fix) | sonnet | is the class closed tree-wide; twins; S1540; standing questions (siblings, unlocks) | D203 bug fix; the round's open item |
| parallelism | sonnet | concurrency identity, worker death, side effects; the runners' --plants loops | owner standing item |

## Findings and PROPOSED dispositions

Check-adequacy (pass and applier):
- **CHECKADEQUACY-5** (design, CONFIRMED) No standing control for the plant pass or plants.py. The ruling's
  "sabotage-style control that plants a stale FROM" lives only as lane evidence; no suite runs it. 29 of 35
  per-clause mutants survive the tree's only check (the live run), incl. `sys.exit` ignoring p_fail (0/28
  faults red) and floor 0. **FIX-NOW**: a standing self-test (a `--selftest` of the script, run by the
  [SABANCHOR] block) over a git-archive copy planting stale / ambiguous / NO SPEC / ORPHAN / dropped runner /
  dying mode, each red with its status word, clean copy green. The critic's harness
  (`checkadequacy/h/harness.py`, 35 mutants) is the fix lane's acceptance gate.
- **CHECKADEQUACY-6** (design, CONFIRMED) `check` and `apply` share `decode()` but not the apply LOOP
  (plants.py:100-112 vs 154-175): apply-side mutants (applies an AMBIGUOUS FROM, never writes, returns early)
  are invisible to the pass by construction; the "kept bit for bit" dialect claim has no pin (Q5, Q6 survive).
  **FIX-NOW**: one loop: `check` runs `cmd_apply`'s loop over an in-memory/temp copy of the named files; add
  decoder rows (4-field wreply refuses, `@@` in TO kept, pres `\\\\n`) to the self-test.
- **CHECKADEQUACY-1** (maintenance, CONFIRMED) check reads a different BASE than apply: pres `--plant-check`
  hands C0DIR = the whole `docs/design/memfn/span_pick/` while `--plant` copies only `census0.py`
  (repro S9301: check OK, apply "no such file"); `cur` keyed by raw path (`vrun.c` vs `./vrun.c`); wreply checks
  the working tree, applies to a `git ls-files` copy. **FIX-NOW**: one variable naming the c0 file set read by
  both modes; realpath keys (dies with CA-6's one loop); wreply check over the tracked set.
- **CHECKADEQUACY-2** (maintenance, CONFIRMED) ORPHAN detection (plants.py:125 `\s*(S[0-9]+)\)`) misses `S1|S2)`,
  `S1 )`, `"S1")`; the alternation form is house style in the same runners. 4 of 5 spellings green.
  **FIX-NOW**: parse case labels from `declare -f plant_spec` (bash's own normal form), split on `|`.
- **CHECKADEQUACY-3** (maintenance, CONFIRMED) discovery is a spelling (`plant_spec() {`, col 0, *.sh under
  tests/ and memfn/tests/): `function plant_spec {`, a runner under scripts/ or examples/ is never read, green.
  **FIX-NOW**: discover callers of `tests/lib/plants.py` tree-wide, cross-check against plant_spec definers in
  any spelling; a mismatch is UNREADABLE.
- **CHECKADEQUACY-4** (maintenance, CONFIRMED) the floor is a SUM, `>=`, no runner-count term: wreply leaving
  discovery + 2 plants added to proof = 81, green. **FIX-NOW**: exact per-runner pins `{runner: n}` (red in both
  directions, names the runner).
- **CHECKADEQUACY-7** (doc, CONFIRMED by run) re-aimed S3092 goes red, but first FAIL is `reply id`, not the
  "form class" its comment names; run_g2_win.sh asserts no per-plant reason (no plant_want). S1423, S3064,
  S1224: RED-FOR-REASON. **FIX-NOW** (comment reword to the observed class); a plant_want table for run_g2_win.sh
  **PLAN** (pre-existing runner shape).
- **CHECKADEQUACY-8** (doc, CONFIRMED by reading) [SABANCHOR]'s verdict texts (run_codegen_tests.sh ~3693-3697)
  still speak only of mech anchors; a plant-pass red points at tests/mech/sabotages. **FIX-NOW** (trivial):
  name both halves; parse `runner plants checked: N` beside `sabotages checked: N`.

General form:
- **GENERALFORM-1** (design, CONFIRMED) twins never compared: 40 runner plants share an id with a mech row:
  16 byte-equal, 23 differ only in the mech `/* SABOTAGE Sxxxx */` marker or a comment, 0 material drift among
  true twins, 1 collision (S1540). The 4 stale plants were twin drift (the mech half was re-anchored, the runner
  half lagged); the pass now catches only the loud half (applies?), not the silent half (still the twin?), and 38
  mech headers claim "one source of the text" falsely. **Recommendation on the open item: YES, enforce**, in the
  same pass, through a `dump` entry of plants.py (decoded FILE/FROM/TO per edit) so the pass never re-decodes;
  normalise the trailing SABOTAGE marker and comments; every shared id must be a declared twin.
  **FIX-NOW** (equality + declaration check, ~40 lines; all 39 twins pass today, no data change).
- **GENERALFORM-2** (doc/design, CONFIRMED) S1540 is an id COLLISION, not a twin: run_g2_win.sh:229 (ofsskip.c,
  kit range S1540-S1559, lane s3pair 2026-10-23) vs tests/mech/sabotages/S1540_cmp13_align_entry_skipped.sh
  (src/gen/emit_dfa.c, lane fsfix 2026-10-24). The mech dir is the id registry (tests/mech/sabotages/CLAUDE.md
  "Numbering"); kit ranges are recorded only in runner comments. **FIX-NOW**: renumber the RUNNER plant to a
  free kit-range id (S1544-S1548 free; the mech id is keyed in tests/ci shard/measure tsvs, costlier) by the
  manager's instruction with a simultaneous substitution; GENERALFORM-1's declaration check makes a future
  collision red. **PLAN**: record kit id ranges where the registry can see them.
- **GENERALFORM-3** (design, CONFIRMED) the class is closed for the four shell runners, not tree-wide: python
  PLANTS in g2 any/mfind/simd (25) and rows_check/kindrow/decider_census/run_finder self-check at run time inside
  make test (held); UNCHECKED: scripts/tests/pred_doc/mut.py (282 hand-copied old/new mutants of
  pred_doc_lint.py, run by no suite) and scripts/cls_identity.py (1, on-demand). **DOC** (scope the CLAUDE.md/
  NOTES claim to "the four shell runners"); mut.py **PLAN** to the predicate manager (a count-only
  `--check-anchors` mode or a suite section).
- **GENERALFORM-4** (NOTED) general form "a plant is data read by one applier whose count mode is the checker's
  reader"; unlocks twin equality, cross-id-space collision checks, one population line.

Parallelism:
- **PARALLELISM-1** (maintenance, CONFIRMED; also found by the coordinator at setup) every `--plant-check` of
  run_g2_win.sh / run_g2_pres.sh / run_proof.sh leaks its mktemp WORK dir (`exec` skips the EXIT trap): 3 dirs per
  `make test-codegen`, in `${TMPDIR:-/tmp}` for win/proof (CLAUDE.md: /tmp is not used). **FIX-NOW**: handle
  `--plant-check` before the mktemp (as run_wreply.sh does).
- **PARALLELISM-3** (hang, CONFIRMED) on timeout the pass kills only the runner's bash, then `communicate()` with no
  timeout: a non-exec'd grandchild holding the pipes hangs `make test-codegen` unboundedly (repro: still running at
  400 s). Latent today (all 4 runners `exec`). **FIX-NOW**: `start_new_session=True`, `os.killpg`, bounded
  second communicate.
- **PARALLELISM-2** (speed, CONFIRMED) the 120 s timeout is per runner, sequential: 3 hung runners = 376 s.
  **FIX-NOW** (trivial): one shared deadline.
- **PARALLELISM-5** (speed, by reading) the runners' full `--plants` modes iterate 79 compile-dominated,
  independent plants serially (win 38, pres 35, proof 6; wreply 2 under the box lock); a pool over per-worker
  src copies under ONE box lock would give ~6-7x on 8 workers. Not on any gate. **PLAN** with trigger (the next
  time a full --plants sweep is owed, e.g. a mass re-aim), per D77; the owner's standing item makes it a finding,
  the manager rules the timing.

## PROBED-AND-HELD (summary; details in review/)
- 29-fault battery: 21 red for their own reason in every dialect (stale win FROM, ambiguous wreply FROM, missing
  file, NO SPEC, plain ORPHAN, runner deleted/renamed/moved, PLANTS emptied, mode-less fifth runner, garbage,
  exit 3, silent exit 0, hang, pres edit 2/2 stale, stale `@c0/`, stale wreply PERT). The pass's row/summary/rc
  double entry kills every plants.py counting mutant.
- The ruling's control rebuilt: a stale FROM turns the pass red in win, pres multi-edit, pres `@c0/`, wreply PERTS.
- Re-aims, real `--plant`: S1423, S3064, S1224 RED-FOR-REASON; S3092 RED-OTHER (CA-7).
- One decoder: 12 `@@` hits across tests/memfn/scripts/tools, 1 decoder; no private heredoc appliers left.
- Concurrent vs serial `--plant-check`: 5x4 runs byte-identical and equal to the serial concatenation; stderr empty;
  4 calls 0.25 s concurrent vs 0.65 s serial (immaterial against the 14 s mech half). Worker death (kill -9,
  exit 3, stderr) red, named, prompt.
- Population: 38/35/6/2 = 81, no duplicate id across runners.

## By-id completeness
CHECKADEQUACY-1..8, GENERALFORM-1..4, PARALLELISM-1/2/3/5 (PAR-0, PAR-4 are measurement notes, held).
Every finding has a proposed disposition. Verification: inline by the coordinator (all CONFIRMED findings carry
critic repros or are code-reading claims; spot-checked plants.py:125 regex, pres c0 argument vs copy, absence of
any standing caller of plants.py/--plant-check outside the 4 runners and the pass, the temp leak reproduced at
setup); no verifier agent (skill §6.2 inline clause).

## Lessons for the guide (proposed)
- A checker subject whose mode delegates to a "count" twin of an "apply" entry: the check-adequacy brief should
  demand that check RUN the apply loop (shared decode is not shared behaviour): CA-6 found it by mutation.
- `exec` after a `trap ... EXIT` in a runner's early-exit mode leaks: add to the check-design lessons.
