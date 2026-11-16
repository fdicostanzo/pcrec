# COMMON brief: critic round predspec12 (design, SHORT confirming re-check, rev 11 -> rev 12)

## Scope mandate (binding)
- Work touches ONLY the repos /home/pcrec/projects/pcrec and /home/pcrec/projects/pcrec-bench, READ-ONLY.
- You write ONLY under your own subdirectory of the round dir R=/var/tmp/pcrec-pcrec/scratch/crit-predspec12/
  (R/simulate/ or R/census/), plus the findings file named in your prompt. Nowhere else on the machine.
- Never run `make`, never run suites or box-queue jobs (the owner's evening hold is on until 01:00 box clock: only small
  scripts, each under `timeout 60`), never edit either repo, never commit, never touch worktrees/.
- Run python as `python3 -I`. Do not `cd` in a compound command; use absolute paths. Nobody reads PCRE2 source (D181).

## Subject (frozen)
- The draft: docs/design/predicates_draft.md REV 12, commit c265543e1ce9f27e7d16f2d8a21222c11938a389 on branch
  lane/predspec12 (tip 3ed4d4d09). READ-ONLY COPY: R/subject/predicates_draft_rev12.md (3282 lines). Cite it as `§N`
  or `draft:LINE` (line numbers of that copy).
- The revision: R/subject/rev11_to_rev12.diff (rev 11 = main's copy, R/subject/predicates_draft_rev11.md, for
  comparison only). Rev 12's Changelog is draft:5-17.
- The rulings record: docs/design/plan_row_bodies/COND-FAMILY.md at the branch base 61f8e9f88 (identical on main
  b9b9e8635), READ-ONLY COPY R/subject/COND-FAMILY.md (1024 lines; cite as CF:LINE; the draft cites the same line
  numbers). ALLOWED IN FULL. The owner's model runs from "the type picture" (CF:846) to the end; a later entry wins
  over the one it corrects. THE ONE RULING REV 12 FOLDS IS THE LAST ENTRY, CF:1001-1024 (2026-11-15 evening: ONE
  anchoring rule, `anchored()`, naming of provided transforms). Read it first, in full. Note its RECORD part (CF:1009
  onward) is the manager's advice the owner accepted ("Ok I agree", CF:1006-1009); its last sentence (CF:1022-1024,
  "To apply in the next revision ... not ruled") is NOT a ruling.
- Other repo files (decisions.md, plan.md) only via `git -C /home/pcrec/projects/pcrec show b9b9e8635:PATH`.
- What it is: a preliminary specification of a predicate language, DESIGN ONLY, no build proposal. Nothing is built;
  there is no review tree and no compiler to run for it.

## The owner's criteria (his words)
"few types and few operators that always mean the same thing wherever they are used"; "a consistent grammar over
comma where it has a specific meaning. Then macro application has a specific meaning."; "I think it will help if our
rx is consistent"; and, for this ruling: "We need consistent rules around when rx is anchored and to what. I don't
want to have a bunch of "primitive" functions have special cases concerning that." (CF:1002-1004).

## Evidence the lane committed (you may read and run these)
- R/subject/predspec12_anchor.py and its output R/subject/predspec12_anchor.out: 16 rows checking the anchoring rule on
  the system libpcre2-8 and Python `re`. Re-run it with `timeout 60 python3 -I R/subject/predspec12_anchor.py`.
  Treat it as a claim: check that each spliced body is the one the draft's TEXT writes (§8, §2.6) and that each row's
  mode (filter = whole value, final = searched) is the one the draft's rule gives.

## Oracle (no tool building needed)
- R/oracle.py: the SYSTEM libpcre2-8 via its public API. `timeout 60 python3 -I R/oracle.py search|whole|all PAT SUBJ`
  (search = first searched match; whole = matched WHOLE, PCRE2_ANCHORED|PCRE2_ENDANCHORED; all = every
  non-overlapping hit with the standard empty-match advance). Prints group spans, None = no match / unset.
  Importable: sys.path.insert(0, R). Python 3 `re` is the second oracle (fullmatch / search; it spells \z as \Z).

## DENYLIST (paths excluded from every read, diff and grep)
docs/dev/lanes/predspec* EXCEPT the two evidence files (use the R/subject copies; the draft cites
`docs/dev/lanes/predspec*_report.md` and rulings files: do NOT open them); docs/dev/reviews/*predspec* and any review
directory for this subject (the draft cites review files such as `2026-11-15-r12-predspec10`: do NOT open them);
docs/dev/dev_journal.md; docs/dev/wake.md; docs/dev/owner.md; worktrees/ (including worktrees/predspec12);
/var/tmp/pcrec-pcrec/scratch/audpred/; /var/tmp/pcrec-pcrec/scratch/crit-predspec*/ OTHER than this round dir;
/var/tmp/pcrec-pcrec/scratch/predspec*/; git log bodies beyond subject lines; R/.coord/ (coordinator notes); the
other critic's subdirectory and findings file. Work from the R/subject copies; you should not need to grep the repo at
all. If you do, plain grep needs `--exclude-dir=lanes --exclude-dir=reviews --exclude=dev_journal.md
--exclude=wake.md --exclude=owner.md --exclude-dir=worktrees`.

## Output format
- Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action with these headings:
  `# <LENS> findings: predspec12`, `## Findings`, `## PROBED-AND-HELD`. Then append each finding the moment you have
  it, ONE APPEND PER FINDING (never hold findings for a final write).
- Each finding: id `<LENS>-n`; CONFIRMED (with the repro: the draft text quoted with draft:LINE, the rule applied,
  the oracle command and output, observed vs claimed) or SUSPECTED (what would confirm it); severity (answer /
  design / maintenance / doc); effort; blast radius; location (§ and draft:LINE). A finding against a RULED item cites
  the CF line and argues, or drops. "answer" = an example/row whose claimed answer the rules do not give.
- `## PROBED-AND-HELD`: what you checked that held, with counts (rows, cases, occurrences, oracle calls).
- If your file Write is refused, SendMessage your findings to the coordinator at once, marked relayed; do not route
  around the refusal.
- END: run `python3 -I /home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-predspec12
  --deliver /var/tmp/pcrec-pcrec/scratch/crit-predspec12/<lens>.deliver <lens>` and fix what it reports until it
  prints `lanecheck: DONE rc=0`. Then end with a final reply of at most 150 words.
