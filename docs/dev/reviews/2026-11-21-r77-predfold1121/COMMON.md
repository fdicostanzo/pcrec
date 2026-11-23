# COMMON brief: critic round predfold1121 (r77), mode DESIGN

Read this whole file first, then your own lens prompt.

## Scope mandate (binding)

- You touch ONLY the pcrec repository (/home/pcrec/projects/pcrec) and pcrec-bench, both READ-ONLY for this round.
  No edits, commits, merges or worktrees in either repo. Never `rm -rf`.
- Your scratch goes ONLY under your own lens directory `R=/var/tmp/pcrec-pcrec/scratch/crit-predfold1121/<lens>/`.
  Nothing under /tmp. Do not write in another lens's directory or in `R/`.
- Read-only critic: never run `make` or any test suite, put nothing in the box queue (`scripts/boxqueue`), do no
  timing. Python runs: `timeout 110 python3 -I -B ...`, one process at a time, each under 110 s.
- Never read PCRE2 source; a PCRE2 source fact you need is listed as a QUESTION in your file (D181). Python `re` and
  your knowledge of PCRE behaviour are fine for probes.
- Never `cd` into a directory in a chained command (a hook blocks it): use absolute paths, `git -C`, or a
  `(cd X && ...)` subshell.

## The subject (frozen)

- The predicate-language definition, plan row [COND-FAMILY]. DESIGN ONLY: no product code exists, none is proposed,
  nothing is built. Branch `lane/pred-rev28`, frozen at commit 882bcf330d00cd22a64d3dd3cfc4ad4c9a6b16b6.
- Read the FROZEN COPIES in `/var/tmp/pcrec-pcrec/scratch/crit-predfold1121/R/subject/` (read-only):
  `core.md`, `core_details.md`, `library.md`, `library_details.md`, `parked.md`, `parked_details.md`
  (base files and their details partners), `doc_format.md` (the document format), and
  `base74/` = the same six files at the last reviewed and delivered state (main's merge 74f70152e).
- THE ROUND'S SCOPE is what changed since 74f70152e: `R/subject/diff_74f70152e_to_freeze.diff` (1,530 lines, five
  files; parked.md did not change). Unchanged text is context: a finding there counts only when a changed piece now
  contradicts it or reads it.
- THE RECORD (the only source of rulings; append-only): `R/subject/COND-FAMILY.md`. The entries IN FORCE for this round
  run from the entry titled `### 2026-11-19 OWNER RULING — flags-in-filter: both sides inherit; and a question on a
  bound `&` put in a hole` (line 5980) to the END of the file (line 6836). Earlier entries are background for what
  stood before. The record's MANAGER entries (titled `MANAGER — ...`, "no owner words") hand the manager's readings
  to this round TO BE TESTED; they are not rulings. Owner entries are marked `OWNER` / `OWNER RULING`.
- `R/subject/predicates_draft_FROZEN_background.md` is the old frozen draft: background only.
- Status words, quoted from core.md's header (lines 9-16): "`ruled` (the owner ruled it), `principle` ... `reading`
  (the draft's or the manager's, not ruled), `open <slug>` (a question for him: the body is a reading or a summary,
  with the candidates), `under-construction`, `?` ... Examples are run: WHOLE (the whole value), SEARCHED (the first
  match), FIND-ALL (every match, again from the end)."
- The crossing rule, quoted from core.md lines 201-202: "Crossings: from rx text to the expression language only by
  `${...}`; from the expression language to rx only by `/.../`." Read the piece `core/model/modes` (core.md line 120
  on) for the three modes in the subject's own words before deriving any mode answer.
- Every spelling is a placeholder (`core/spellings/placeholders`): critique meaning, not spelling taste.

## Evidence (you may read and RE-RUN)

A read-only runnable mirror of the tree at the freeze is `R/tree/` (docs/design/predicates, the record,
doc_format.md, scripts/pred_doc_lint.py, and four evidence directories). The scripts read the documents by relative
path from their own location, so ALWAYS run the mirror's copy, never the repo's:

    timeout 110 python3 -I -B /var/tmp/pcrec-pcrec/scratch/crit-predfold1121/R/tree/docs/dev/lanes/predscope_evidence/predscope_model.py
    timeout 110 python3 -I -B /var/tmp/pcrec-pcrec/scratch/crit-predfold1121/R/tree/docs/dev/lanes/predarr_evidence/predarr_model.py
    (earlier lanes, same shape: predfix61_evidence/predfix61_model.py, predasc_evidence/predasc_model.py)
    (cd /var/tmp/pcrec-pcrec/scratch/crit-predfold1121/R/tree && timeout 60 python3 -I -B scripts/pred_doc_lint.py)

Each evidence dir's CLAUDE.md gives the sabotage switch (`PREDSCOPE_SABOTAGE=sN`, `PREDARR_SABOTAGE=sN`, ...) and its
committed `.out`. The scripts only print (they write no files). predasc_model.py calls `git show` on an old commit and
cannot run in the mirror; its committed `.out` is the record of it. To change a script, COPY it into your own lens
dir and keep the copy's relative layout pointing at R/tree (or edit its path constants); never edit R/.
A script's ORDER or SWAP switch, where it has one: ask whether it can fail; a switch that reverses nothing carrying
meaning guards nothing. An evidence row that shows a refusal names the MECHANISM that refuses; an emulator's own
`raise` is not evidence.

## Who checks what (do not duplicate)

- ONE lens (RULING) verifies owner quotes word for word against the record. Every other lens CITES quotes as the
  documents print them and does not re-check them.
- ONE lens (EXAMPLES) re-derives the printed worked examples of the changed pieces and re-runs the evidence scripts.
  Other lenses construct NEW witnesses; they do not re-derive printed lines.
- ONE lens (MODES) owns the capture-state, nullable-loop-body and edge-case-in-second-place drills.
- ONE lens (GENERAL) owns the general form, unlocks and duplicated statements across sibling pieces.
- ONE lens (FIXIND) owns restated-decision diffs against base74 and readers of changed or withdrawn rules.

## Denylist (do not read, and exclude from every grep and git command)

- `docs/dev/lanes/predscope_report.md`, `docs/dev/lanes/predarr_report.md`, `docs/dev/lanes/predfix61_report.md`,
  `docs/dev/lanes/predasc_report.md`, `docs/dev/lanes/predloop_report.md`, every other `docs/dev/lanes/pred*_report.md`
  and every `docs/dev/lanes/preddoc*` file.
- Every earlier review of the predicate documents under `docs/dev/reviews/` (any file or directory whose name contains
  `predspec`, `preddoc`, `predfold`, `predlint`, `condkind`, `absfold` or `jointcond`).
- `docs/dev/pred/journal.md`, `docs/dev/pred/wake.md`, `docs/dev/pred/to_main.md`, `docs/dev/pred/from_main.md`,
  `docs/dev/pred/owner.md`.
- The worktrees `worktrees/predscope`, `worktrees/predarr` and every other `worktrees/pred*` including `worktrees/pred`
  (you read the frozen copies in R/ instead).
- `/var/tmp/pcrec-pcrec/scratch/pred/`, `.../scratch/predscope/`, `.../scratch/predarr/`, and this round's
  `.coord/` directory.
- `git log` bodies beyond subject lines; the box queue and job logs.
- You should not need the repo at all: everything is in R/. If you grep the repo, use plain-grep excludes, e.g.
  `--exclude='pred*_report.md' --exclude='preddoc*' --exclude-dir='worktrees' --exclude-dir=reviews`
  and exclude `docs/dev/pred/` (journal/wake/to_main/from_main/owner) with `--exclude-dir=pred` only where you do not
  need `docs/dev/pred/doc_format.md` (its copy is R/subject/doc_format.md).

## Output (binding)

- Your findings file ALREADY EXISTS, pre-created with its headings: `<lens>/findings.md`. It is your OUTPUT, not an
  input. APPEND to it (Edit, or a shell `cat >> FILE <<'EOF'`); never overwrite it with Write (the harness refuses a
  subagent's whole-file Write and the file would stay empty). Append each finding THE MOMENT you have it, one append
  per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: the input, the rule text you applied with its file:line, the
  command if any, observed vs expected) or SUSPECTED (what would confirm it); severity (answer / design / doc /
  maintenance); effort; blast radius; the file:line in R/subject/ and the piece TAG. A finding against a ruled piece
  cites the ruling entry (record line) and argues against it, or is dropped.
- Answer-level means: a printed answer (HOLDS/FAILS, a position, a hit list) is wrong under the subject's own rules,
  or a printed program is not legal predicate language, or two pieces give the same program two answers.
- Patterns: pass them in single quotes or via a file; check every regex you run is the one you meant.
- STATE THE MINIMUM WITNESS LENGTH your probes reached (a 0-difference below the length a case needs is not evidence).
- End the file with PROBED-AND-HELD (what you checked that held, with case counts), then a last line
  `CRITIC COMPLETE <lens> <UTC time>`.
- Then run: `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-predfold1121 --deliver /var/tmp/pcrec-pcrec/scratch/crit-predfold1121/<lens>/deliver.txt <lens>`
  and end once it prints DONE (fix what it reports first).
- Final reply at most 150 words. You are a nested agent: a failed final reply is EXPECTED and needs no escalation;
  the CRITIC COMPLETE line in your file is the delivery. If your appends to the findings file are REFUSED, SendMessage
  your findings to the coordinator at once, marked relayed.
