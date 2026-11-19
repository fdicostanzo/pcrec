# COMMON brief: critic round r59 (preddoc3), DESIGN mode

## Scope mandate (binding)
Touch ONLY the pcrec repository, READ-ONLY. You never run `make`, never edit any file in any repository, never commit.
The ONLY files you write: your own findings file (pre-created, path in your prompt) and scratch under your own
subdirectory `/var/tmp/pcrec-pcrec/scratch/crit-preddoc3/<lens>/`. Never write under /tmp or $HOME. NO BACKGROUND
JOBS: every command runs in the foreground under `timeout` (e.g. `timeout 120 python3 -I x.py`). Never chain `cd`
with another command (a hook blocks it): use absolute paths or a `(cd X && ...)` subshell. PCRE2 source is never
opened. Python: always `python3 -I`.

## The subject (frozen at commit 65bd0f4de of branch lane/pred-rev28)
Six documents, converted from the frozen draft and the record, in the format below:
- READ-ONLY COPIES (read THESE): `/var/tmp/pcrec-pcrec/scratch/crit-preddoc3/R/subject/predicates/`
  `core.md core_details.md library.md library_details.md parked.md parked_details.md` (+ that dir's CLAUDE.md).
- THE FORMAT: `R/subject/doc_format.md` (what a piece, a status, a `rulings:`/`slugs:`/`rejected:` field is).
- THE RECORD (the owner's words; the ONLY source of rulings): `R/subject/COND-FAMILY.md` (5,485 lines).
- THE FROZEN DRAFT, revision 29.1 (the source the documents were converted from): `R/subject/predicates_draft.md`
  (10,275 lines; read by grep and by section, never whole: §R.8 the open table, §R.9 reversed/narrowed rulings,
  §13 open questions, §8 libraries, §16 superseded direction).
- THE PARKED LIST: `R/subject/predicates_future.md` (items 1-38).
- The lint: `R/subject/pred_doc_lint.py` (it reports clean, 4,056 checks; you need not re-run it).
(`R/` = `/var/tmp/pcrec-pcrec/scratch/crit-preddoc3/R/`.) Optional reader: `(cd /home/pcrec/projects/pcrec/worktrees/pred && scripts/entry <tag> -l 2)`
prints one piece + its details entry; it reads the LIVE worktree, so first check
`git -C /home/pcrec/projects/pcrec/worktrees/pred rev-parse HEAD` is 65bd0f4de...; if not, use the R/ copies only.

WHAT THE DOCUMENTS ARE FOR (the owner's request): a session reads the BASE files (core.md, library.md, parked.md)
whole and knows the current language, the library and the parked ideas; reasoning, history and "what was rejected and
why" are reached by tag in the details files.

TIMING FACT: the draft's revision 29 folded the owner's rulings up to class-order. The record's 2026-11-19 OWNER entries
from "### 2026-11-19 OWNER RULING — other-holes" (record line 4834) onward were made AFTER the draft and are NOT in it;
where they override the draft, the documents should follow the record.

A rule of the format you will need (doc_format.md, quoted): "CORE HOLDS PRIMITIVES ONLY: a piece whose definition is a
body in the core language is a LIBRARY piece". Status words: `ruled` (the owner ruled it) | `principle` | `reading`
(the draft's or the manager's, not ruled) | `open <slug>` | `under-construction` | `parked` | `?`.

## Owner's quotes
ONE lens verifies quotes word for word against the record: the RULING lens. Other lenses cite quotes without re-checking.

## DENYLIST (never read, never grep into)
- `docs/dev/lanes/preddoc1_report.md`, `preddoc2_report.md`, `preddoc3a_report.md`, `preddoc3b_report.md`,
  `preddoc3c_report.md` (the writers' reports), and everything under `docs/dev/lanes/preddoc*_evidence/` (EXCEPTION:
  the EXAMPLE critic may read those evidence scripts only AFTER its own runs are written to its file).
- `/var/tmp/pcrec-pcrec/scratch/predcensus/` (an earlier census's output).
- `docs/dev/reviews/2026-11-19-r57-preddoc2.md` and its directory `docs/dev/reviews/2026-11-19-r57-preddoc2/`.
- `/var/tmp/pcrec-pcrec/scratch/crit-preddoc3/.coord/` and every OTHER lens's subdirectory and findings file.
- other worktrees than `worktrees/pred`, job logs, the box queue, `git log` bodies beyond subject lines.
You do not need the repository at all: everything is in R/. If you grep the repository anyway, exclude the denied
paths (`--exclude=preddoc*_report.md --exclude-dir=preddoc1_evidence ...` for plain grep).

## Output (binding)
Your findings file ALREADY EXISTS (pre-created with headings; it is NOT an input). APPEND to it (Edit, or
`cat >> FILE <<'EOF'`), NEVER overwrite it with Write (the harness refuses a subagent's whole-file Write). Append each
finding the MOMENT you have it, one append per finding. Each finding:

    ### <LENS>-n  CONFIRMED | SUSPECTED   severity: answer|doc|design|maintenance   effort: S|M|L
    where: <file + tag> (and record line / draft line)
    what: ...
    evidence: <the record line quoted, the command run, observed vs expected>
    proposed fix: ...

A finding against a ruled piece cites the record entry and argues. Lists you build (censuses) go in your file as an
appendix table WITH the command or method that built them, so the coordinator can re-run them. State the size of the
population you checked (and, for runs, the longest witness you used). End your file with `## PROBED-AND-HELD` (what
you checked and found fine, with counts) and then a last line exactly `CRITIC COMPLETE`. Your final reply (at most 150
words) may fail to reach anyone: that is EXPECTED for a nested agent, the CRITIC COMPLETE line in your file is the
delivery; never escalate to the manager.
