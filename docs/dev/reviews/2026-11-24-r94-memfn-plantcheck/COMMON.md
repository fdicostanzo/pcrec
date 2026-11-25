# COMMON brief: critic round r94 memfn-plantcheck (CODE mode, light)

## Mandate (read first)
- Touch ONLY the pcrec repository, and only READ it. You are read-only: never edit,
  commit or checkout anything in /Users/claude/pcrec or any worktree; NEVER run `make`
  (any target) or any test suite (`make test`, mech, batteries).
- Scratch ONLY under YOUR lens dir: /var/tmp/pcrec-claude/scratch/crit-memfn-plantcheck/<lens>/
  (checkadequacy | generalform | parallelism). Set `TMPDIR` to a dir under your lens dir for
  every runner/script call (the runners mktemp into $TMPDIR).
- Do not `cd` into worktrees/ (a hook blocks it); use absolute paths, `git -C`, or a `( cd X && .. )` subshell.
- Wrap anything that may run long in `timeout` (bare `timeout` is GNU on this Mac).
- The Mac: gcc is `gcc-16` (bare `gcc` is Apple clang). python3 is 3.9.

## Subject
- Lane plantfix's change on branch lane/memfn-plantcheck. FROZEN code: SUBJECT = 14e8c419b.
  LANEBASE = b9f81ef80 (the lane's parent; `git merge-base main` is main HEAD e11c5f4ef, but
  the branch also carries unrelated kit arch-review commits, so diff against LANEBASE).
  Later branch commits (2dd4cf4af, 8bd727eab) touch only memfn/docs/journal.md (denied).
- The diff to review:
  `git -C /Users/claude/pcrec diff b9f81ef80 14e8c419b -- . ':!docs/dev/lanes/plantfix_*' ':!docs/dev/lanes/plantri_*' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md'`
  Files: tests/lib/plants.py (new: THE applier), scripts/m6read_check_sab_anchors.py (the new
  runner plant pass, floor 81), memfn/tests/run_g2_win.sh, memfn/tests/run_g2_pres.sh,
  tests/memfn/run_proof.sh, tests/memfn/run_wreply.sh (each now applies via plants.py and has a
  `--plant-check` mode), plus CLAUDE.md/NOTES.md/INDEX.md text.
- Built review tree (read-only, at SUBJECT): /Users/claude/pcrec/worktrees/crit-memfn-plantcheck
  (build/pcrec and build/pcrec-harness exist). Do NOT write into it.
- Coordinator baseline at SUBJECT: `python3 -I <tree>/scripts/m6read_check_sab_anchors.py`
  ends `runner plants checked: 81 (89 edits, 4 runners), floor 81` / `all runner plants apply`, rc 0, ~14 s
  (the mech-anchor half dominates).

## What the subject is and claims
A CHECK change fixing a bug CLASS (D203): four runners carried hand-copied sabotage "plants"
(a `plant_spec` case function + a `PLANTS` id list, applied by `--plant ID` / `--plants`) that
no check read; 4 of 81 went stale. Its claims: (1) one applier module all 4 runners apply
through; (2) a plant pass in the [SABANCHOR] script (which rides `make test-codegen`,
tests/codegen/run_codegen_tests.sh [SABANCHOR] block) reads every runner plant THROUGH that
module, population floor 81; (3) re-aims of the 4 stale plants S1423, S3092 (run_g2_win.sh),
S3064 edit 1 (run_g2_pres.sh), S1224 (run_proof.sh); (4) mech-row output byte-identical;
each runner's --plants verdicts unchanged except the 4 re-aims; each re-aimed plant still
goes red for its named reason.

Main's ruling the subject implements (verbatim; its record is a launcher message, no file):
"Build ALL of it in ONE kit lane: the applier module, the plant pass in
scripts/m6read_check_sab_anchors.py (you may edit that file in this lane; I review it), the
population floor, and the 4 re-aims. One mechanism, one owner, so no checker half drifts from
the applier. It's a bug fix under D203; it needs no owner build go. Deliver as a code PR; a
light critic round before landing (review r94, topic memfn-plantcheck). Include a
sabotage-style control that plants a stale FROM and shows the pass goes red."

House rules in play: ONE decoder, no second mechanism (the pass must not re-decode plants
itself); the three dialects (win / pres / wreply) are kept bit for bit from the old private
heredocs (pres keeps `\\\\n` as the C escape `\\n`). Read rulings files only as
`git show 14e8c419b:docs/dev/decisions.md` etc. (D203 = bugs are classes). Guide:
docs/dev/guide/critics.md, docs/dev/learnings.md §3 (check design).

## Run kit
- `/var/tmp/pcrec-claude/scratch/crit-memfn-plantcheck/kit/mkcopy.sh DEST [subject|base]`
  makes a private writable copy (git archive; subject copy also gets build/). DEST must be
  under your lens dir. Mutate COPIES only; every script resolves its root from its own path,
  so `python3 -I DEST/scripts/m6read_check_sab_anchors.py` and `bash DEST/<runner> --plant-check`
  check the copy. ~15 s per anchor-script run; cap 120 anchor-script runs per critic.
- `--plant-check` is cheap (no build). The FULL `--plant ID` / `--plants` modes compile the
  kit (minutes per plant; run_wreply.sh takes the box lock): ONLY the check-adequacy lens may run
  `--plant ID`, at most the 4 re-aimed ids, once each, on its copy, under
  `timeout 1800`, never --plants and never run_wreply.sh's.
- Known Mac reds (not findings): test-codegen's run_size_term.sh, run_case_spelling_identity.sh,
  run_residual_twins.sh; make strict's aarch64 targets-check rc 2. Linux CI runs on the PR.

## Assignments (one owner each)
- PLANTS (mutating plants/runners/the pass in copies, the stale-FROM control): check-adequacy ONLY.
- Hand-copied literals elsewhere / twin census / S1540: general-form ONLY.
- Timing, concurrency, worker death: parallelism ONLY.

## Denylist (never read; exclude from EVERY git diff/grep/log)
docs/dev/lanes/plantfix_* (report + evidence), docs/dev/lanes/plantri_*,
memfn/docs/journal.md, memfn/docs/responses.md, docs/dev/reviews/* about this subject,
git log BODIES (subject lines OK), job logs, other worktrees, the box queue,
/var/tmp/pcrec-claude/scratch/crit-memfn-plantcheck/.coord/ .
Git pathspec excludes: `':!docs/dev/lanes/plantfix_*' ':!docs/dev/lanes/plantri_*' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md'`.
Plain grep: `--exclude='plantfix_*' --exclude='plantri_*' --exclude=journal.md --exclude=responses.md --exclude-dir=.coord --exclude-dir=worktrees`.

## Output format
Your findings file is PRE-CREATED with its headings: APPEND to it (Edit or `>>`), never
overwrite it with Write. Append each finding the moment you have it, one append per finding.
Each finding: id `<LENS>-n`; CONFIRMED (repro: input, command, observed vs expected) or
SUSPECTED (what would confirm it); severity (answer/speed/size/maintenance/doc/design);
effort; blast radius; file:line. A finding against a ruled D-row cites it and argues, or drops.
End with PROBED-AND-HELD (with case counts), then the line `CRITIC COMPLETE`.
Then run `/Users/claude/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-claude/scratch/crit-memfn-plantcheck --deliver <your DELIVER file> <lens>`
until it prints DONE rc=0 ("DONE rc=1" is a failure). Final reply at most 150 words; a failed
final reply is EXPECTED for a nested agent: the file is the delivery. If your file append is
refused, SendMessage your findings to the coordinator at once, marked relayed.
