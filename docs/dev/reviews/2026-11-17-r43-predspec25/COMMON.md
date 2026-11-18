# COMMON brief: critic round predspec25 (design re-check), 2026-11-17

## Scope mandate (binding)
- You touch ONLY the pcrec repository (/home/pcrec/projects/pcrec) READ-ONLY, and you need nothing there: everything is copied below. pcrec-bench: not needed.
- You WRITE only under your own subdirectory /var/tmp/pcrec-pcrec/scratch/crit-predspec25/<lens>/ (already created) and your pre-created findings file. Never /tmp, never $HOME, never either repo.
- Never run `make`, a suite, or anything multi-core or long. The box is under the owner's evening hold until 01:00 and a peer's TIMING jobs run after: ONE light process at a time (python scripts of seconds, single libpcre2 calls), each under `timeout 600`.
- Never `cd X && cmd` (a hook blocks it); use absolute paths or a `(cd X && cmd)` subshell.
- Run python as `python3 -I -B`. Pass patterns in single quotes or via a file.

## Subject (frozen)
- docs/design/predicates_draft.md REVISION 25 (commit db77f9daed0f, on main at 97e4fe96becd). A DESIGN ONLY subject: predicates are not being built; there is no build tree and no compiler question. The only executable controls are libpcre2-8 (installed) and Python `re`.
- THIS IS A RE-CHECK: revisions 24 and 24.2 were reviewed; revisions 24.3 (that review's fixes), 24.4 and 25 were NOT. Your scope is everything that changed since rev 24.2.
- Read-only copies (use THESE, never the live tree):
  - R/subject/predicates_draft.md (rev 25; 8,020 lines: READ FIRST its §R, lines ~505-2000; §R wins over later sections where they disagree; later sections carry "[REV 25]", "[REV 24.x]" marks)
  - R/subject/predicates_draft_rev24.2.md (the last reviewed revision) and R/subject/draft_diff_rev24.2_to_rev25.diff (the whole change, 1,542 lines)
  - R/subject/COND-FAMILY.md: the RULINGS RECORD (the owner's words, "HIS WORDS"). Rev 24.4 folded the entries from "2026-11-17 OWNER RULING — operand-context" (line 2574); rev 25 folds from "2026-11-17 OWNER RULING — pass-start-read" (line 2768) to the end (line 3089). Entries before 2574 were in force at the reviewed revisions. Text marked "MINE" or "THE MANAGER'S ANSWER" in the record is the manager's reading, not the owner's ruling.
  - R/subject/rx_module.md (the proposal the rx-module rulings answer); R/subject/predicates_future.md (parked matters; items 19-25 and item 24's entries are new) and R/subject/future_rxmodule_diff_since_rev24.2.diff
  - R/subject/joint_condition.md, R/subject/condition_kind.md (client/earlier design docs, for reference only)
  (R = /var/tmp/pcrec-pcrec/scratch/crit-predspec25)
- Rulings files at the freeze: docs/dev/decisions.md and docs/dev/plan.md at commit 838499cf98379b8a; if you need them, read with `git -C /home/pcrec/projects/pcrec show 838499cf9:docs/dev/decisions.md` (grep it; never the live tree). You probably need neither: the predicate rulings live in COND-FAMILY.md.

## The evidence (runnable, read-only copy)
- R/tree/docs/dev/lanes/predspec25_evidence/predspec25_model.py (+ its CLAUDE.md and committed output predspec25_model.out). It LOADS R/tree/docs/dev/lanes/predspec244_evidence/predspec244_model.py in memory (the parser, the path enumerator, the "one label rule", mode helpers) and uses R/tree/docs/dev/lanes/rxmodel_evidence/pcre2h.py, a ctypes wrapper of the installed libpcre2-8 (you may IMPORT it and call it; it is pcrec's own file; but never look for or open any PCRE2 source code).
- It writes nothing but stdout. Run (seconds):
    (cd /var/tmp/pcrec-pcrec/scratch/crit-predspec25/<lens> && timeout 600 python3 -I -B /var/tmp/pcrec-pcrec/scratch/crit-predspec25/R/tree/docs/dev/lanes/predspec25_evidence/predspec25_model.py > fwd.out)
  The coordinator re-ran it: byte-identical to the committed .out.
- Its switches: PREDSPEC25_SABOTAGE=1 (deliberately wrong rules; listed in the script header and CLAUDE.md); predspec244's PREDSPEC244_RULES (243 / 244 / carry) chooses the label rule. Ask whether each switch CAN FAIL: a switch that reverses nothing carrying meaning guards nothing. The engine's HEADER lists the readings it implements: each must be a sentence of the subject.
- To test your own constructions write a small script in YOUR dir that imports pcre2h (sys.path.insert to R/tree/docs/dev/lanes/rxmodel_evidence) and, if useful, execs the predspec244 engine as predspec25_model.py does (copy that loading idiom).

## Rules for reading the subject
- Quote the SUBJECT's sentence (with its line in R/subject/predicates_draft.md) for every rule you test. Do not rely on any paraphrase in a brief, including this one.
- Every program has MODES: WHOLE value, SEARCHED (top level), FIND-ALL places (an `occurrences`/`contains` argument, a `records` item), and the nested filter role. State the mode of every answer you claim.
- Owner quotes: ONLY the ruling-check lens verifies "HIS WORDS" word for word against COND-FAMILY.md; other lenses cite them without re-checking.

## Denylist (never open, grep or list the contents of)
- docs/dev/lanes/*_report.md for every predspec* lane, and file40_report.md, file42_report.md, rxlib_report.md, rxmodel_report.md, lastpass_report.md
- every docs/dev/reviews/ file or directory whose name contains predspec, jointcond, absfold or condkind (the subject's rev 24.3 changelog NAMES one of them: do not open it)
- docs/dev/dev_journal.md, docs/dev/wake.md, docs/dev/owner.md, git log bodies, job logs, other worktrees, the box queue
- /var/tmp/pcrec-pcrec/scratch/crit-predspec25/.coord/ and every other lens's subdirectory and findings file
- If you grep the live repo at all (you should not need to), exclude those paths (`--exclude=` per file for plain grep).

## Output format
- Your findings file ALREADY EXISTS (pre-created with headings): /var/tmp/pcrec-pcrec/scratch/crit-predspec25/<lens>.md. Write into it; APPEND each finding the moment you have it, one append per finding (never hold findings to the end).
- Each finding: id `<LENS>-n`; CONFIRMED (repro: input, command or file:line, observed vs expected) or SUSPECTED (what would confirm it); severity (answer / design / doc / maintenance); effort; blast radius; § and line in R/subject/predicates_draft.md (or the record line). A finding against a RULED entry cites the entry and argues, or drops.
- End the file with `## PROBED-AND-HELD` (what you tested that held, with case counts), then the line `CRITIC COMPLETE` as the LAST line, written last.
- Then run: `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-predspec25 --deliver /var/tmp/pcrec-pcrec/scratch/crit-predspec25/<lens>_deliver.txt <lens>` and END only when it prints `DONE rc=0` (fix what it reports; ignore its "commit" wording: nothing is committed).
- Final reply at most 150 words. If a Write to your findings file is refused, SendMessage your findings to the coordinator at once, marked relayed; never route around a refusal.
- Keep to your ONE question. Aim to finish within ~45 minutes.
