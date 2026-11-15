# COMMON brief: critic round predspec10 (design, SHORT confirming re-check)

## Scope mandate (binding)
- Work touches ONLY the repos /home/pcrec/projects/pcrec and /home/pcrec/projects/pcrec-bench, READ-ONLY.
- You write ONLY under your own subdirectory of the round dir R=/var/tmp/pcrec-pcrec/scratch/crit-predspec10/
  (R/simulate/ or R/census/), plus the findings file named in your prompt. Nowhere else on the machine.
- Never run `make`, never edit either repo, never commit, never touch worktrees/.
- Run python as `python3 -I`. Do not `cd` in a compound command; use absolute paths.

## Subject (frozen)
- The draft: docs/design/predicates_draft.md, rev 10, at commit 8d6b77c4fd2779a202f08fb2c4b8aeea7f6d2703 (main HEAD at
  the freeze; byte-identical to the lane commit 287289b5e). READ-ONLY COPY: R/subject/predicates_draft.md (2917 lines).
  Cite it as `§N` or `draft:LINE` (line numbers of that copy).
- The rulings record: docs/design/plan_row_bodies/COND-FAMILY.md at the same commit, READ-ONLY COPY
  R/subject/COND-FAMILY.md (1000 lines; cite as CF:LINE). ALLOWED IN FULL. The 2026-11-15 entries (CF:749-1000) are
  the rulings in force for the latest revisions; a later entry wins over the one it corrects. The draft cites them as
  CF:LINE with these same line numbers.
- Other repo files (decisions.md, plan.md) only via `git -C /home/pcrec/projects/pcrec show 8d6b77c4f:PATH`.
- What it is: a preliminary specification of a predicate language, DESIGN ONLY, no build proposal. Nothing is built;
  there is no review tree and no compiler to run for it.

## The owner's criteria (his words)
"few types and few operators that always mean the same thing wherever they are used"; "a consistent grammar over
comma where it has a specific meaning. Then macro application has a specific meaning."; "I think it will help if our
rx is consistent".

## What rev 10 changed
Its Changelog (draft:5-19) lists every addition. A fix-induced question applies to BOTH lenses: what did rev 10 ADD,
and is each addition consistent with the rest of the draft and with the rulings?

## Oracle (no tool building needed)
- R/oracle.py: the SYSTEM libpcre2-8 (10.4x) via its public API. `python3 -I R/oracle.py search|whole|all PAT SUBJ`
  (search = first searched match; whole = whole-value anchored at both ends; all = every non-overlapping hit with the
  standard empty-match advance). Prints group spans, None = unset. Importable: sys.path.insert(0, R).
- python3 `re` is the second oracle. Nobody reads PCRE2 source.

## DENYLIST (paths excluded from every read, diff and grep)
docs/dev/lanes/predspec* (the draft cites `docs/dev/lanes/predspec*_report.md` and a rulings file: do NOT open them);
docs/dev/reviews/*predspec* and any review directory for this subject (the draft cites review files: do NOT open
them); docs/dev/dev_journal.md; docs/dev/wake.md; docs/dev/owner.md; /var/tmp/pcrec-pcrec/scratch/audpred/;
/var/tmp/pcrec-pcrec/scratch/crit-predspec*/ OTHER than this round dir; /var/tmp/pcrec-pcrec/scratch/predspec*/;
git log bodies beyond subject lines; worktrees/; R/.coord/ (coordinator notes); the other critic's subdirectory and
findings file. Work from the two subject copies; you should not need to grep the repo at all. If you do, plain grep
needs `--exclude-dir=lanes --exclude-dir=reviews --exclude=dev_journal.md --exclude=wake.md --exclude=owner.md
--exclude-dir=worktrees`.

## Output format
- Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action with these headings:
  `# <LENS> findings: predspec10`, `## Findings`, `## PROBED-AND-HELD`. Then append each finding the moment you have
  it, ONE APPEND PER FINDING (never hold findings for a final write).
- Each finding: id `<LENS>-n`; CONFIRMED (with the repro: the draft text quoted with draft:LINE, the rule applied,
  the oracle command and output, observed vs claimed) or SUSPECTED (what would confirm it); severity (answer /
  design / maintenance / doc); effort; blast radius; location (§ and draft:LINE). A finding against a RULED item cites
  the CF line and argues, or drops. "answer" = an example/row whose claimed answer the rules do not give.
- `## PROBED-AND-HELD`: what you checked that held, with counts (examples, rows, occurrences, oracle calls).
- If your file Write is refused, SendMessage your findings to the coordinator at once, marked relayed; do not route
  around the refusal.
- END: run `python3 -I /home/pcrec/projects/pcrec/scripts/lanecheck --dir R --deliver R/<lens>.deliver <lens>`
  (R spelled out in full) and fix what it reports until it prints `lanecheck: DONE rc=0`. Then end with a final reply
  of at most 150 words.
