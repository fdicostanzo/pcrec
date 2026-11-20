# COMMON brief: critic round r60 (preddoc5), DESIGN mode, a RE-CHECK

## Scope mandate (binding)
Touch ONLY the pcrec repository, READ-ONLY. Never run `make`, never edit any file in any repository, never commit.
The ONLY files you write: your own findings file (pre-created, path in your prompt) and scratch under your own
subdirectory `/var/tmp/pcrec-pcrec/scratch/crit-preddoc5/<lens>/`. Never write under /tmp or $HOME. NO BACKGROUND
JOBS: every command in the foreground under `timeout` (e.g. `timeout 120 python3 -I x.py`). LIGHT work only (the box
is in its evening hold): reading, grep, the lint, single `python3 -I` runs with the `re` module. Never chain `cd` with
another command (a hook blocks it): absolute paths or a `(cd X && ...)` subshell. PCRE2 source is never opened.
Python: always `python3 -I`. Pass patterns in single quotes or via a file.

## The subject (frozen at commit d8634250a of branch lane/pred-rev28)
`R/` = `/var/tmp/pcrec-pcrec/scratch/crit-preddoc5/R/` (read-only copies; you need nothing else).
- THE SUBJECT, six documents: `R/tree/docs/design/predicates/{core,core_details,library,library_details,parked,parked_details}.md`
  (+ that dir's CLAUDE.md). BASE files = core.md, library.md, parked.md; DETAILS = the *_details.md files.
- THE SAME SIX BEFORE THE FIXES (commit 65bd0f4de, what review r59 read): `R/before/docs/design/predicates/`.
- THE FIX DIFF 65bd0f4de..d8634250a (documents, doc_format, record): `R/subject/diff_65bd0f4de_d8634250a.diff` (3,533 lines).
- THE FORMAT: `R/tree/docs/dev/pred/doc_format.md`.
- THE RECORD (the owner's words; the ONLY source of rulings): `R/tree/docs/design/plan_row_bodies/COND-FAMILY.md`
  (5,549 lines; entries are `### <date> <WHO> ...` headings; read by grep and by range).
- THE FROZEN DRAFT rev 29.1 (the conversion source): `R/tree/docs/design/predicates_draft.md` (grep/sections only).
- THE PARKED LIST: `R/tree/docs/design/predicates_future.md`.
- THE PRIOR ROUND, review r59 (INPUT for a re-check, except where your prompt says otherwise):
  `R/tree/docs/dev/reviews/2026-11-19-r59-preddoc3.md` (findings, counts, "Dispositions as ruled and applied") and
  its dir `R/tree/docs/dev/reviews/2026-11-19-r59-preddoc3/` (critic texts and APPENDICES: compA.md appendix A =
  the 144 owner rulings, appendix B = the 188 slugs; compB.md appendix A = the 98 provided names, appendix B = the
  100 rejected candidates; example.md appendix C = the 38 parked items; readwhole.md = the blind read).
- Tools: the lint `(cd R/tree && timeout 120 python3 -I scripts/pred_doc_lint.py)` (clean, 4,844 checks; L10
  skipped in the copy); one piece + its details entry: `(cd R/tree && timeout 30 python3 -I scripts/entry <tag> -l 2)`
  (e.g. `core/modules/positional`). Both read the copies, not the live tree.

WHAT THE DOCUMENTS ARE FOR (the owner's request): a session reads the BASE files whole at wake-up and knows the
current language, the library and the parked ideas; reasoning, history, rulings and "what was rejected and why" are
reached by tag in the details files.

A CHANGE OF RULE SINCE r59 (record entries "2026-11-19 OWNER, refining where provided names live: every `x()` in the
library, marked defined in the language or not" and "2026-11-19 OWNER, on the manager's take on provided names: "I
agree with your take"", record lines 5512-5549): every call-form name `x(...)` / `m.x(...)` is a LIBRARY piece with
a `defined:` line: `defined: language` (it has a body) or `defined: native (<why>)` or `defined: ?` (open /
under-construction only); the core holds syntax and meaning and no call-form name. r59's PLACE-1 ("move primitives to
the core") is therefore REPLACED, not unfixed. Quote of doc_format.md on the library piece shape: read it there.

Status words (doc_format.md): `ruled` | `principle` | `reading` | `open <slug>` | `under-construction` | `parked` | `?`.

## Owner's quotes
ONE lens verifies the owner's quotes word for word against the record: the RULING lens. The others cite quotes
without re-checking them (they may still report a quote that is absent from the record altogether).

## DENYLIST (never read, never grep into)
- `docs/dev/lanes/preddoc1_report.md` ... `preddoc5_report.md` (including preddoc3a/3b/3c, preddoc4) and everything
  under `docs/dev/lanes/preddoc*_evidence/` (the fix lanes' own tables and evidence are the claims under test).
- `/var/tmp/pcrec-pcrec/scratch/crit-preddoc5/.coord/` and every OTHER lens's subdirectory and findings file.
- `/var/tmp/pcrec-pcrec/scratch/predcensus/`, other worktrees, job logs, the box queue, `git log` bodies beyond
  subject lines.
You do not need the repository: everything is in R/. If you grep the repository anyway, exclude the denied paths
(`--exclude='preddoc*_report.md' --exclude-dir='preddoc*_evidence'` for plain grep).

## Output (binding)
Your findings file ALREADY EXISTS (pre-created with headings; it is NOT an input). APPEND to it (Edit, or
`cat >> FILE <<'EOF2'`), NEVER overwrite it with Write (the harness refuses a subagent's whole-file Write). Append each
finding the MOMENT you have it, one append per finding. Each finding:

    ### <LENS>-n  CONFIRMED | SUSPECTED   severity: answer|doc|design|maintenance   effort: S|M|L
    where: <file + tag> (and record line / draft line)
    what: ...
    evidence: <the record line quoted, the command run, observed vs expected>
    proposed fix: ...

A finding against a ruled piece cites the record entry and argues. Lists and tables you build go in your file as an
appendix WITH the command or method that built them, so the coordinator can re-run them. State the size of the
population you checked (and, for any `re` run, the longest witness you used). End your file with
`## PROBED-AND-HELD` (what you checked and found fine, with counts) and then a last line exactly `CRITIC COMPLETE`.
Your final reply (at most 150 words) may fail to reach anyone: that is EXPECTED for a nested agent; the CRITIC
COMPLETE line in your file is the delivery; never escalate to the manager.
