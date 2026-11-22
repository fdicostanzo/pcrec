# COMMON brief — critic round r81, topic k159fix (CODE mode, light round)

## Scope mandate (binding)
Work touches ONLY the pcrec repo (/home/pcrec/projects/pcrec); do NOT touch pcrec-bench. Do not create, modify
or delete files anywhere else. You are READ-ONLY on the repo: no edits, no commits, never `make`, never a suite
(make test, run_facts_checks.sh, mech, sabotage matrix). Your scratch goes ONLY under your own lens dir
`/var/tmp/pcrec-pcrec/scratch/crit-k159fix/<lens>/` (never /tmp; set TMPDIR=<your lens dir> for tools).
Never `cd` into a worktree (a hook blocks it): use absolute paths, `git -C DIR`, or `( cd X && ... )` subshells.
Bound every run that can hang: the kit's run.sh already wraps scripts/watchdog; for anything else use
`scripts/watchdog -c CPU -s WALL -m MEM -- cmd` (a bare -m number is BYTES; use a suffix, e.g. 2g).
The box is shared and busy (a kit test job holds it): keep probes single-process, `nice`, at most ~300 compiles total
per critic, and no single probe over 60 CPU s.

## Subject (frozen)
- SUBJECT = 1ffad2f2c532aeb226f3d5262f05cbaa4b0e3702 (branch lane/k159fix tip)
- BASE    = 92f5e77b6aecad456b7bbc31a34cf9487dbddf9d (merge-base with main)
- The code commits: dc08453cc (the stop, src/facts/kset.c), 8dede63f7 (guard + sabotage + evidence script).
- Diff: `git -C /home/pcrec/projects/pcrec diff BASE SUBJECT -- src/ tests/ docs/dev/known_issues.md docs/dev/lanes/k159fix_evidence src/facts/CLAUDE.md`
  (that pathspec already excludes the denied report). Files changed: src/facts/kset.c (`pcrec_width_walk`),
  tests/codegen/run_facts_checks.sh (new section 9b `[facts-width-cpu]`), tests/mech/sabotages/S3505_width_walk_no_repeat_stop.sh,
  docs/dev/lanes/k159fix_evidence/width_cells.py, docs/dev/known_issues.md (K159 entry), plan.md row [K159-PLUS-SUPERLINEAR].
- The problem being fixed is known issue K159 (read its entry in docs/dev/known_issues.md at SUBJECT via
  `git -C /home/pcrec/projects/pcrec show SUBJECT:docs/dev/known_issues.md`, search "## K159"): the width fact's
  frontier walk had no exit but the `j > nfa->n` size bound, so nested `+` compile time grew about x4.5 per level.
- Read rulings via `git -C /home/pcrec/projects/pcrec show <commit>:path`, never the live tree. The owner ruling the
  fix answers is "growth-time-bound" (2026-11-21, "fix first"; CPU seconds), quoted in the plan row's trigger line.
  The owner's standing code-review item (2026-11-22): "An item for code review is o(n2) algorithms".

## Trees and binaries (prebuilt; do not build)
- SUBJECT review tree: /home/pcrec/projects/pcrec/worktrees/crit-k159fix  (build/pcrec)
- BASE tree (git archive export): /var/tmp/pcrec-pcrec/scratch/crit-k159fix/base  (build/pcrec)
- Plant tree for sabotage S3505 (SUBJECT with the row's SAB_BEFORE->SAB_AFTER applied, rebuilt):
  /var/tmp/pcrec-pcrec/scratch/crit-k159fix/plants/S3505/tree  (build/pcrec)
- Kit: `kit/run.sh TREE 'PATTERN' [pcrec args]` (TREE = base | subject | plant:S3505; prints the width fact rows
  of `--emit-facts=byte,utf8` and `cpu=<s> rc=<rc>`); `kit/nest.py D` prints the K159 nested-`+` witness at depth D.
  Pass patterns in single quotes or as `@file`; check the pattern actually reached pcrec (shell quoting eats `\b`).
- The width fact's listing: `build/pcrec --emit-facts=byte,utf8 --pattern P` (rows tab-separated; field 2 = fact name).
  Other entry points: `--emit-facts` (default listing the guard reads), `--engine=vm`, `-e utf8`.
- Guide (rules reviewed against): docs/dev/guide/coding.md, docs/dev/guide/critics.md, docs/dev/learnings.md §3 (checks).

## Denylist (do not read, grep or diff)
docs/dev/lanes/k159fix_report.md and every docs/dev/lanes/k159fix_* EXCEPT docs/dev/lanes/k159fix_evidence/width_cells.py;
the lane's commit BODIES (subject lines only: use `git log --format=%s`); job logs; the box queue (scripts/boxqueue state,
queue.log); other worktrees under /home/pcrec/projects/pcrec/worktrees/ except crit-k159fix; docs/dev/reviews/*k159*;
the round dir's `.coord/` directory and other lenses' subdirectories. For plain grep use
`--exclude='k159fix_report.md' --exclude-dir=.coord`; for git grep add `':!docs/dev/lanes/k159fix_report.md'`.

## Output format
Your findings file `<lens>/findings.md` is PRE-CREATED with headings. APPEND to it (shell `>>` or Edit) — never
overwrite it with Write (the harness refuses a subagent's whole-file Write and the file stays empty). Append each
finding THE MOMENT you have it, one append per finding.
Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, exact command, observed vs expected) or SUSPECTED (what
would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius; file:line or §.
A finding against a ruled D-row cites it and argues, or drops. Under PROBED-AND-HELD list what you probed that held,
with case counts, and state the largest witness size (NFA states / nesting depth / pattern length) your probes reached.
Write `CRITIC COMPLETE` as the last line of the file when done. Then run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-k159fix --deliver /var/tmp/pcrec-pcrec/scratch/crit-k159fix/<lens>/deliver.txt <lens>`
and end only once it prints DONE (fix what it names). Final reply at most 150 words; a failed final reply is EXPECTED
for a nested agent and needs no escalation: the findings file is the delivery.
