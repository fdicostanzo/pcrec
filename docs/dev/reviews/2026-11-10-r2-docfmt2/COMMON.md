# COMMON brief — critic round docfmt2 (design RE-CHECK), 2026-11-10

Read this whole file first. Then your own one-question prompt.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench
  (/home/pcrec/projects/pcrec-bench), and READ ONLY in both. You edit nothing
  in either repo, create no branch, commit nothing, never run `make`, never run
  a test suite, never touch the box queue, never launch agents.
- The ONE writable place is your own directory
  /var/tmp/pcrec-pcrec/scratch/crit-docfmt2/<your-lens>/ (it exists). Never /tmp.
  Scratch copies of repo files for plants go there. If you run any repo
  script, read its header first, run it on COPIES in your dir where it takes
  a file, with `PCREC_TMPDIR=<your dir>`, and only scripts that do not write
  into the repo. Python: `python3 -I`.
- Do not kill processes. Bound uncertain commands with `timeout 120`.

## Subject (frozen)
- Design doc rev 2: `docs/design/doc_index_format.md` + its appendix
  `docs/design/doc_index_format_appendix.md`, branch `lane/docfmt`, doc
  commit 6ea705ed9446f043b555899d14570b53cd36e6ba (unchanged at the branch
  tip 74c467983). READ THE COPIES (not on main):
  /var/tmp/pcrec-pcrec/scratch/crit-docfmt2/subject/doc_index_format_rev2.md
  /var/tmp/pcrec-pcrec/scratch/crit-docfmt2/subject/doc_index_format_appendix_rev2.md
- What rev 2 answers: critic round 1's review WITH the manager's rulings
  (every proposed disposition accepted), copy:
  /var/tmp/pcrec-pcrec/scratch/crit-docfmt2/subject/r1_review_with_rulings.md
  Rev 2's opening table maps each finding F1-F17 to its change.
- What it is: one format for pcrec's ruling and tracker files (decisions.md
  832 KB, plan.md 468 KB, later known_issues/upstream): a tight INDEX (one
  statement line per entry) + a DETAILS file with the full original text,
  read through a levelled accessor `scripts/entry`, one linter (doc_lint,
  plan_lint folded in at T2), one profile table `scripts/doc_profiles.py`.
- BUILD UNITS under this re-check (the build go is for these two):
  T1 = doc_profiles.py, scripts/entry, the gestalt soft-cap ROWS row,
  docs/dev/doc_format.md, the `test-doc-lint` section (doc §5 T1 row, §2.3,
  §2.4, §10). Unit 1 (with 1.0) = census + addendum OWNER TABLE + control +
  cite resolver (1.0), then the decisions.md split into index (`?` lines) +
  decisions_details.md by converter, doc_lint decisions profile C1-C13 (doc §5
  rows 1.0 and 1, §2.2, §5.2, appendices A, B, C, E).
- BUILD TREE (what a build lands on; every cited file, reader and census
  number is checked HERE): main e9687de272b79eebf2c7a87198d0fcb837359949. A
  clean detached checkout, read-only for you:
  /home/pcrec/projects/pcrec/worktrees/crit-docfmt2/   <- read and grep HERE,
  never in /home/pcrec/projects/pcrec (the live tree moves). The doc's census
  was taken at main 6638e3679; between it and the build tree main changed
  scripts/gestalt (a declared ROWS table, `--all`, an idle-held row),
  scripts/tests/gestalt.test, scripts/NOTES.md,
  .claude/skills/pcrec-manager/monitoring.md. Any cited code that moved
  between the census commit and the build tree is a finding.
- RULINGS in force: decisions.md and plan.md at the build tree (via the
  checkout or `git -C /home/pcrec/projects/pcrec show e9687de27:docs/dev/decisions.md`),
  PLUS the two lane-only entries, copies:
  subject/D192.md (the owner's six answers; on lane/docfmt decisions.md:10126)
  and plan row [DOC-INDEX] (lane/docfmt plan.md, Active section; read only via
  `git -C /home/pcrec/projects/pcrec show lane/docfmt:docs/dev/plan.md | grep -n -A6 '^- \[DOC-INDEX\]'`).
  Never the live tree's ruling files.
- MANAGER'S CHOICE ALREADY MADE (do not re-litigate; recorded by message
  only): the plan index IS read at wake along with the decisions index (the
  owner asked for a primary file kept in memory for reference; ~80 KB total
  fits); the post-compact hook does NOT inline either.
- Planned timing (fact): NO merges to main from 2026-11-11 01:00 until the
  full suite ends (~14:00); 20:00-01:00 daily is the owner's hold.

## Guide and context files (in the build tree)
- docs/dev/guide/critics.md, architecture.md, style.md
- docs/dev/learnings.md §3 (controls sharing a source with what they
  control; uncounted populations, K35)
- docs/design/CLAUDE.md (standing questions for designs)
- root CLAUDE.md; scripts/CLAUDE.md; tests/CLAUDE.md; docs/testing.md
- scripts/plan_lint.py, scripts/plan_lint.sh, scripts/hooks/pre-commit,
  scripts/hooks/pre-push-light, scripts/hooks/post_compact.sh, tests/plan_lint/,
  tests/memfn/rows_check.py, tests/memfn/stream_support.tsv, scripts/gestalt,
  scripts/tests/gestalt.test, Makefile (TEST_SECTIONS, hooks), tests/ci/shards.tsv,
  tests/lib/san_excluded.txt, tests/lib/san_scripts.txt, .claude/skills/*/SKILL.md

## DENYLIST (do not open, grep or print)
- docs/dev/lanes/docfmt_report.md, docfmt1_report.md, docfmt2_report.md (any
  tree, any branch); plain-grep exclude: `--exclude='docfmt*_report.md'`
- /var/tmp/pcrec-pcrec/scratch/crit-docfmt/ (round 1's raw files; the
  committed review copy above IS allowed)
- `git log` BODIES on lane/docfmt (subject lines only); do not `git show`
  lane/docfmt commits except via the copies above and the [DOC-INDEX] grep
- /var/tmp/pcrec-pcrec/scratch/crit-docfmt2/.coord/ and other critics' dirs
- job logs, the box queue, other worktrees under worktrees/ (except crit-docfmt2)
- Broad grep over the checkout: `grep -r --exclude-dir=.git --exclude='docfmt*_report.md' ...`

## Output format
- Your findings file DOES NOT EXIST YET. CREATE it as your FIRST action, with
  these headings, then write it INCREMENTALLY — append each finding the moment
  you have it, one append per finding:

      # <LENS> critic — docfmt2
      ## Findings
      ## PROBED-AND-HELD

- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command,
  observed vs expected) or SUSPECTED (what would confirm it); severity
  (answer / speed / size / maintenance / doc / design); effort; blast radius;
  the doc § (and file:line in the build tree). A finding that contradicts a
  ruled D-row, the owner's answers (D192) or the manager's choice above cites
  it and argues, or drops. Say whether it is NEW in rev 2 (fix-induced) or a
  round-1 finding left unfixed (name the F-id).
- Readiness verdicts use exactly: ready / ready with listed text fixes / not ready.
- PROBED-AND-HELD: what you checked that held, with case counts.
- If your findings-file Write is refused, SendMessage your findings to the
  coordinator at once (marked relayed); do not route around the refusal.
- When done, run:
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-docfmt2 --deliver /var/tmp/pcrec-pcrec/scratch/crit-docfmt2/<lens>/deliver.txt <lens>`
  (the deliver file is already written for you) and fix until it prints DONE.
  Final reply at most 150 words.
