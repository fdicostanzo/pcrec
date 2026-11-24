# COMMON brief: critic round r92 memfn-archrev2 (ARCHITECTURE mode, a LIGHT RE-CHECK)

Round dir: RD = /var/tmp/pcrec-claude/scratch/crit-memfn-archrev2

## Mandate (read first; binding)

- Touch ONLY the pcrec repository, and that READ-ONLY. pcrec-bench is out of scope. No edits to any repo, no commits.
- Write ONLY under RD/<your-lens>/ (your scratch) and your pre-created findings file. Nowhere else on this machine.
- Never run `make`, a test suite or a build. Grep, read, python3 -I one-liners over the R/ copies are fine.
- Pass patterns to grep in single quotes or via a file.

## The subject

- SUBJECT: `RD/R/subject/arch_review_rev2.md` = `memfn/docs/arch_review_2026-11.md` rev 2, at commit e3f3b5a12 on
  lane/memfn-arch. It is the memfn kit's overall ARCHITECTURE REVIEW of its four sections (chartered by R-49),
  reviewing each section against `docs/dev/guide/architecture.md` and filing suggestions ARV-n, smaller first.
- Rev 2 is a fresh architect's revision answering review r91. r91 is an INPUT you may read:
  `RD/R/subject/r91/review.md` (its RULING section says what was ruled: F1-F20 FIX-NOW, F14's RUL-13 to main, F21 the
  manager's) and the r91 critic texts beside it (`aggregation.md`, `sitemap.md`, `register.md`, `firstunit.md`,
  `ruling.md`, `COMMON.md`, `process.md`).
- Rev 1 (`RD/R/subject/arch_review_rev1.md`) and the diff rev1 -> rev2 (`RD/R/subject/rev1_to_rev2.diff`) are there to
  scope what changed.
- Requirements: R-49 in `RD/R/tree/memfn/docs/requests.md` (grep `^## R-49`) and `RD/R/subject/KIT-ARCH-STEP.md`.
- TREE T = a0f13ad83a2432f14341831ba4d1ff68964b79d9 (the note's header). `RD/R/tree/` is a `git archive` of T with the
  denied material removed. READ CODE AND RULINGS THERE (grep -rn over RD/R/tree). main HEAD at the freeze
  (e11c5f4ef) differs from T only in BOILERPLATE.md and three memfn/docs ledgers: decisions.md, plan.md and
  docs/dev/guide are identical, and no cited code site moved. So RD/R/tree IS the ruling record at the freeze.
- Guide: `RD/R/tree/docs/dev/guide/architecture.md` (goals 1-4, judgement (a)-(e), KINDS OF ROW, the ride-along
  register). Architect method: `RD/R/tree/.claude/skills/pcrec-architect/SKILL.md` (its self-check: no layout outside
  "What the design step must decide").
- Anchor map kit: `RD/R/kit/anchor_map.py` (run: `python3 -I RD/R/kit/anchor_map.py RD/R/tree [PREFIX]`), its output
  `RD/R/kit/anchor_map_memfn.tsv` (every mech sabotage row anchored under memfn/, with its enclosing function and
  line at T) and `anchor_map_all.tsv` (every file).

## RE-CHECK SCOPE (the kit manager's)

ARV-9 and its §8 hand-off H1 (the window.c split); ARV-16 (new: the position primitives leave window.c); ARV-10 and
ARV-12; the re-posed owner question in §9 (`window-file-split`); the re-sized ARV-5, ARV-6, ARV-8, ARV-11 and ARV-14;
the ARV-1/ARV-18 split; the new §8 "What the design step must decide" as a whole. Outside this scope, report only
what a scoped item makes wrong.

Arch mode does NOT review algorithms, code, measurements or build cost; those belong to later rounds.

## Rulings since r91 the note must follow (their only record is a DENIED ledger; quoted verbatim here)

Main's ruling of 2026-11-24 on r91's RUL-13, verbatim:
"Q36's extraction trigger is NOT superseded. The 11-04 manifesto and plan-as-text seam split the kit internally
(planner vs emitter); they don't extract it from the repo. ARV-14 may still propose moving formhash.c/k1_ref.c out of
the product library on its OWN trigger, e.g. a measured library-size or link cost. Write it that way, not as "Q36
extraction"."
F21 (the [KIT-ARCH-STEP] plan row's "three stages") is main's to fix, NOT the note's: do not raise it.
The owner's standing kit memories named by R-49 are not readable on this box: rely on R-49's wording and the
committed records that quote them.

## Round rules (accepted lessons)

- SIZE and GATE of every suggestion belong to the FIRST-UNIT lenses ALONE (r91 lesson: three lenses re-derived ARV-9's
  ranges). Other lenses do not re-derive sizes, ranges or binding-check counts.
- Each count the note quotes is FLOOR (name list), SHAPE (regex over a construct) or CEILING (also matches comments).
  Ask, for any count you rely on: what spelling does this regex miss?
- ONE lens (ruling) verifies owner quotes and ruling quotes word for word against the record; others cite them.
- Fix-induced question for every scoped item: does the fix hold; did it add a new error (a new read, a hand, a row, a
  check, a layout decided outside §8, a contradiction with another section); and did any r91 finding go unanswered?

## DENYLIST (do not open, grep or list)

- `docs/dev/lanes/archrev_*`, `docs/dev/lanes/archrev2_*` (the architect lanes' reports/deliver/rulings) anywhere.
- `memfn/docs/journal.md` entries dated 2026-11-24, and `memfn/docs/responses.md` items about R-48/R-49 (RD/R/tree's
  copies are already truncated before them; do not read the repo's live copies).
- `git log` bodies beyond subject lines; job logs; the box queue; any other worktree (`/Users/claude/pcrec/worktrees/*`);
  the live repo tree generally (use RD/R/). `RD/.coord/` (the coordinator's notes). Other critics' directories.
- If you grep the live repo for any reason, use `--exclude=journal.md --exclude=responses.md --exclude='archrev*'`.

## Output format

- Your findings file is PRE-CREATED for you (it exists, with headings). APPEND to it (Edit, or a shell `>>`); NEVER
  overwrite it with Write (the harness refuses a subagent's whole-file Write and the file stays empty).
- Append each finding the moment you have it, one append per finding: id `<LENS>-n`, CONFIRMED (repro: the command
  or quoted lines, observed vs expected) or SUSPECTED (what would confirm it), severity (answer / speed / size /
  maintenance / doc / design), effort, blast radius, note § / file:line at T. Name the r91 F-id it relates to, if any.
  A finding against a ruled D-row cites it and argues, or drops.
- End with `## PROBED-AND-HELD` (what you checked that holds, with counts), then the line `CRITIC COMPLETE` last.
- Then run: `/Users/claude/pcrec/scripts/lanecheck --dir RD --deliver RD/<lens>/DELIVER.txt <lens>` (with RD
  spelled out) and fix what it reports until it prints `lanecheck: DONE rc=0` ("DONE rc=1" is a failure).
- A failed final reply is EXPECTED for a nested agent and needs no escalation: the CRITIC COMPLETE line is the
  delivery. Final reply at most 150 words. If your findings-file append is REFUSED, SendMessage your findings to the
  coordinator at once, marked relayed.
