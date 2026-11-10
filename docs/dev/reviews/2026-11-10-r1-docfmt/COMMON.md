# COMMON brief — critic round docfmt (design), 2026-11-10

Read this whole file first. Then your own one-question prompt.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench
  (/home/pcrec/projects/pcrec-bench), and READ ONLY in both. You edit nothing
  in either repo, create no branch, commit nothing, never run `make`, never run
  a test suite, never touch the box queue.
- The ONE writable place is your own directory under the round dir
  /var/tmp/pcrec-pcrec/scratch/crit-docfmt/<your-lens>/ (create it). Never /tmp.
  Scratch copies of repo files for plants go there too. If you run any repo
  script, run it on COPIES in your dir, with `PCREC_TMPDIR` set to your dir,
  and only scripts that do not write into the repo (read their header first).
  Python: `python3 -I`.
- Do not kill processes. Bound uncertain commands with `timeout 120`.

## Subject (frozen)
- Design doc: `docs/design/doc_index_format.md` rev 1, branch `lane/docfmt`,
  doc commit a8e23570407aa9cabae2817255836b1a45df23aa. A read-only copy:
  /var/tmp/pcrec-pcrec/scratch/crit-docfmt/subject_doc_index_format_rev1.md
  (read THIS copy; the doc is not on main).
- BUILD TREE (where every cited file, census number and reader lives; what a
  build would land on): main 6638e3679ddd6c1612abda1c9b3339576e636a9c. A clean
  detached checkout of it, read-only for you:
  /home/pcrec/projects/pcrec/worktrees/crit-docfmt/   ← read and grep HERE,
  not in /home/pcrec/projects/pcrec (the live tree moves as lanes land).
- Ruling files: read via that checkout or `git -C /home/pcrec/projects/pcrec
  show 6638e3679:docs/dev/decisions.md` (and plan.md), never the live tree.
- What it is: one standard format for pcrec's ruling and tracker files
  (decisions.md 832 KB, plan.md 468 KB, then known_issues.md; the kit's
  request/response ledgers as a proposal): a tight INDEX (one recall line per
  entry) plus a DETAILS file with the full original text, read through a
  levelled accessor `scripts/entry`, linted by one linter folded from
  `scripts/plan_lint`. The consumer is an AI manager session that keeps the
  index in context and pulls details on demand.
- The owner's ruling record for rev 0's questions (its only record besides the
  doc's §7), quoted verbatim from docs/dev/owner.md:13 at the freeze:
  "(answered 2026-11-10: doc index format: opus writes + opus critic checks
  statements; details-file layout ours (accessor hides it); a LEVELED accessor
  with item grep and a work-choosing view; SOFT caps, gestalt line only when
  over; kit ledger yes, send the kit the proposal once vetted; known issues
  third. Rev 1 lane docfmt1 running, then a critic round, then build units.)"
- Planned timing (fact for cost lenses): NO merges to main from 2026-11-11
  01:00 until the full suite ends (~14:00).

## Guide and context files (in the build tree)
- docs/dev/guide/critics.md, architecture.md, style.md (rules you review against)
- docs/dev/learnings.md §3 (check design: controls that share a source with
  what they control; uncounted populations, K35)
- docs/design/CLAUDE.md (the standing questions for designs)
- root CLAUDE.md (pointers to these files; the situation index)
- scripts/plan_lint.py, scripts/plan_lint.sh, scripts/hooks/pre-commit,
  tests/plan_lint/, tests/memfn/rows_check.py, tests/memfn/stream_support.tsv,
  scripts/gestalt, scripts/hooks/post_compact.sh, .claude/skills/*/SKILL.md

## DENYLIST (do not open, grep or print)
- docs/dev/lanes/docfmt_report.md, docs/dev/lanes/docfmt1_report.md,
  docs/dev/lanes/docfmt*_deliver.txt (any tree, any branch)
- `git log` BODIES on lane/docfmt (subject lines only are fine); do not
  `git show` any lane/docfmt commit except the doc file at a8e2357 (use the
  copy above instead)
- /var/tmp/pcrec-pcrec/scratch/crit-docfmt/.coord/ and other critics' dirs
- docs/dev/reviews/ files about this subject (none known), job logs, the box
  queue, other worktrees under worktrees/ (except crit-docfmt)
- Plain grep exclude string for broad greps over the checkout:
  `--exclude-dir=.git --exclude='docfmt*'`
  (the checkout at main contains none of the denied files, but use it anyway).

## Output format
- Your findings file DOES NOT EXIST YET. CREATE it as your FIRST action, with
  these headings, then write it INCREMENTALLY — append each finding the moment
  you have it, one append per finding:

      # <LENS> critic — docfmt
      ## Findings
      ## PROBED-AND-HELD

- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command,
  observed vs expected) or SUSPECTED (what would confirm it); severity
  (answer / speed / size / maintenance / doc / design); effort; blast radius;
  the doc § (and file:line in the build tree where relevant). A finding that
  contradicts a ruled D-row or the owner's answers above cites it and argues,
  or drops.
- PROBED-AND-HELD: what you checked that held, with case counts.
- If your findings-file Write is refused, SendMessage your findings to the
  coordinator at once (marked relayed); do not route around the refusal.
- When done, run:
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-docfmt --deliver /var/tmp/pcrec-pcrec/scratch/crit-docfmt/<lens>/deliver.txt <lens>`
  (the deliver file is already written for you) and fix until it prints DONE.
  Final reply at most 150 words.
