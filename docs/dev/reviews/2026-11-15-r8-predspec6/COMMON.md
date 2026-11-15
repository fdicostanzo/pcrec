# COMMON brief — critic round crit-predspec6 (DESIGN mode)

## Scope mandate (binding)
- You may READ only the pcrec repo (/home/pcrec/projects/pcrec) and, if ever needed, pcrec-bench
  (/home/pcrec/projects/pcrec-bench). You write ONLY under your own lens directory
  /var/tmp/pcrec-pcrec/scratch/crit-predspec6/<lens>/ . Nothing anywhere else on the machine.
- READ-ONLY: no edits, no commits, no `make`, no suites, no builds, no worktrees. This is a design
  round; there is nothing to compile. Small python3 -I scripts of your own under your lens dir
  (e.g. a tokenizer over the draft's code spans) are fine.

## Subject
- `docs/design/predicates_draft.md` rev 6, frozen at commit 22ec6bf73 (identical at main HEAD
  aa9348f3d). Read it as `git -C /home/pcrec/projects/pcrec show aa9348f3d:docs/design/predicates_draft.md`
  (1624 lines). Cite findings as `§n.n` plus the line number in that version.
- What it is: a PRELIMINARY SPECIFICATION of a predicate language (an extension of pcrec's pattern
  language: rx literals `/.../`, `&` intersection, conditions over a pattern's labels, macros,
  arrays/records, search). DESIGN ONLY: there is NO build proposal, NO build go. Do not review
  cost, emitted code, or measurement; do not ask "should this be built".
- SYNTAX IS PLACEHOLDER: the owner rules semantics; spelling is a later step. A finding about
  a spelling is in scope only when the SAME spelling carries TWO MEANINGS, or a rule as written
  makes an example ill-formed/ambiguous. Do not propose prettier syntax.
- The owner's stated criterion for this subject (Frank, 2026-11-15, his words):
  "I want to make the semantics and grammar as simple as reasonable which in my mind means few
  types and few operators that always mean the same thing wherever they are used" and
  "What I'd like is a consistent grammar over comma where it has a specific meaning. Then macro
  application has a specific meaning."
- Rev 6 folds his latest ruling, the LAST entry of `docs/design/plan_row_bodies/COND-FAMILY.md`
  (lines 846-878 at aa9348f3d, "the type picture"). That whole file ("CF", the rulings record the
  design rests on) is ALLOWED reading: `git show aa9348f3d:docs/design/plan_row_bodies/COND-FAMILY.md`.
  Within CF the LATEST note on a topic wins; the owner's QUOTED words outrank a manager paraphrase.
  The ruling's "TO CHECK in the next round" list (CF:874-878) is manager's, not ruled: fair game.
- The worked examples in the draft's §12 are the ACCEPTANCE CASES.
- Other allowed reading: `docs/dev/decisions.md` and `docs/dev/plan.md` via `git show aa9348f3d:<path>`
  (never the live tree), `docs/design/cond_family.md`, `docs/design/cond_family_syntax_survey.md`,
  `docs/dev/lanes/predx_report.md` (cited by the draft), `docs/dev/guide/` (critics.md, architecture.md),
  `docs/design/CLAUDE.md`.

## Denylist (excluded from EVERY read, diff and grep)
- docs/dev/lanes/predspec* (every predspec lane report/deliver/rulings file, all revs)
- docs/dev/reviews/*predspec* (earlier reviews of this subject, including the r1 review file and
  any sibling directory) — note the draft CITES "review 2026-11-14-r1-predspec"; do not open it.
- docs/dev/dev_journal.md, docs/dev/wake.md, docs/dev/owner.md
- /var/tmp/pcrec-pcrec/scratch/audpred/ , /var/tmp/pcrec-pcrec/scratch/crit-predspec/ (an earlier round)
- /var/tmp/pcrec-pcrec/scratch/crit-predspec6/.coord/ and every OTHER lens's directory in this round
- worktrees/ (all of it), the box queue, job logs
- git log BODIES (subject lines only: `git log --format=%s`)
- For plain grep use: `grep -r --exclude-dir=worktrees --exclude-dir=reviews --exclude='predspec*'
  --exclude=dev_journal.md --exclude=wake.md --exclude=owner.md ...` (plain grep ignores git
  pathspecs). For git grep/diff add `':!docs/dev/lanes/predspec*' ':!docs/dev/reviews/*predspec*'
  ':!docs/dev/dev_journal.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md'`.
Simplest safe practice: read only the files named above by exact path.

## Output format
- Your findings file `<lens>/findings.md` DOES NOT EXIST YET: CREATE it as your FIRST action with
  the headings `## Findings` and `## PROBED-AND-HELD`, then APPEND each finding the moment you have
  it, one append per finding (never batch them for the end).
- Each finding: id `<LENS>-n`; CONFIRMED (with the repro: the exact draft lines/tokens, the rule
  applied, observed vs what the rule/criterion requires) or SUSPECTED (what would confirm it);
  severity (answer / design / doc / maintenance); effort (S/M/L); blast radius (which sections /
  examples); location (§ + line). A finding against a RULED item cites the CF line and argues why
  the ruling's own words are not served, or drops it. Suggest a minimal fix direction in one line.
- End with `## PROBED-AND-HELD`: what you checked that held, with counts (e.g. "38 code spans
  re-parsed, 31 clean").
- Before ending run:
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-predspec6 --deliver /var/tmp/pcrec-pcrec/scratch/crit-predspec6/<lens>/deliver.txt <lens>`
  and fix until it lists no numbered issues and exits 0 (`DONE rc=0`; `DONE rc=1` means NOT done). Final reply at most 150 words.
- If your Write to the findings file is ever refused, do not route around it: SendMessage the
  findings to `crit-predspec6` at once, marked relayed.
