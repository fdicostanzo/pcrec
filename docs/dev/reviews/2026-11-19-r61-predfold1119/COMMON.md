# COMMON brief — critic round r61 predfold1119 (design mode)

## Scope mandate (binding)
- Work touches ONLY the pcrec and pcrec-bench repositories, and you are READ-ONLY on both: no edits, no commits,
  no `make`, nothing in the box queue (scripts/boxqueue), no timing runs, no worktrees.
- Your scratch goes ONLY under your own dir `/var/tmp/pcrec-pcrec/scratch/crit-predfold1119/<LENS>/` (create it).
  Nothing in /tmp, nothing in $HOME, nothing anywhere else.
- Never `cd` into a worktrees/ path in a chained command; use absolute paths or a `( cd X && ... )` subshell.
- Never read PCRE2 source (D181). Use python3 `re` as the regex oracle.
- HARD TIME LIMIT: write your `CRITIC COMPLETE` line by 23:50 box clock (`date`), whatever you have; NO process of
  yours may run after 00:15. Bound every command: `timeout 120 python3 -I ...`.

## Subject (frozen)
The predicate language's definition documents (DESIGN ONLY, nothing is built), as changed in one session.
Freeze = commit 2e0adc746 (branch lane/pred-rev28); BASE = 50f56b1cd. Everything you need is copied READ-ONLY to
`R = /var/tmp/pcrec-pcrec/scratch/crit-predfold1119/R/`:
- `R/subject/subject.diff` — THE SUBJECT: `git diff 50f56b1cd..2e0adc746 -- docs/design/predicates/` (core.md,
  core_details.md, library.md, library_details.md; parked*.md unchanged).
- `R/subject/{core,core_details,library,library_details,parked,parked_details}.md` — the files AT THE FREEZE.
  Read the changed pieces in the context of the whole of core.md and library.md. (`*_details.md` hold each
  piece's rulings:/rejected:/readings:/evidence:/history: entries.)
- `R/subject/doc_format.md` — the format (piece = heading `### Title [tag] status date`, statement line,
  needs:/see:/by:, bullets, run lines `WHOLE .. / SEARCHED .. / FIND-ALL ..`). The lint is green and is NOT the subject.
- `R/subject/COND-FAMILY.md` — THE RULINGS RECORD at the freeze, the only source of the owner's (Frank's) rulings.
  `R/subject/record_session.md` = its lines 5551-5978: the entries this session folded (bare-condition-labels,
  looped-warning, hole-export, array-scope, class-positions, quantified-order; discussion entries; two entries
  titled MANAGER = the manager's own readings, handed to this round TO BE ATTACKED; the sort-function remark).
  Earlier record entries stay in force wherever a changed piece cites them (a details `rulings:` item names the
  record entry's title exactly).
- The language's THREE MODES (core.md defines them; read its definition, do not rely on this gloss): WHOLE
  (the program judges the whole subject value), SEARCHED (the first hit in a longer subject, reported `text`@offset),
  FIND-ALL (every non-overlapping hit, a list). A property stated without its mode is a finding.

## Evidence (runnable, read-only)
- Lane evidence models, in a runnable mirror `R/tree/` (docs/design/predicates + the record + docs/dev/lanes/*_evidence):
    ( cd R/tree && timeout 120 python3 -I docs/dev/lanes/predloop_evidence/predloop_model.py )
    ( cd R/tree && GIT_DIR=/home/pcrec/projects/pcrec/.git timeout 120 python3 -I docs/dev/lanes/predasc_evidence/predasc_model.py )
  (predasc reads its base commit via read-only `git show`; the GIT_DIR prefix is required.)
  Sabotage switch: `PREDLOOP_SABOTAGE=sN` / `PREDASC_SABOTAGE=sN` (one plant at a time; see the header of each .py).
  Ask whether each switch can fail on what carries meaning: a plant that reverses nothing meaningful guards nothing.
  The models only READ; to modify one, copy it into YOUR dir first.
- The manager's hand-folded pieces (bare-condition-labels, looped-warning, hole-export, array-scope, the sort bullet)
  have NO committed evidence beyond what the record entries quote. The scratch scripts the record names are copied to
  `R/scratch_named/` (looped.py looped_item.py bcl_end_vs_point.py bcl_guess.py classpos_inf.py nestloop.py asc.py);
  run them from your own dir, e.g. `timeout 120 python3 -I R/scratch_named/x.py`; check first they write nothing.
- EVIDENCE RULE: every sentence of yours about what a pattern MATCHES is RUN (python3 -I `re`, under `timeout`) and
  shows the call, or is marked HAND-WORKED. Build each example's regex MECHANICALLY from the piece's own text
  (what the piece says the hole/lift/enumerate expands to), never from your memory of the rule. Pass patterns in
  single-quoted heredocs or files (shell quoting eats `\b`). STATE THE MINIMUM AND MAXIMUM WITNESS LENGTH your pool
  reached; a 0-differ count below the witness length is not evidence. Drill an edge case in SECOND place and at
  `min >= 2`, not only first.

## Denylist (do NOT open, grep or print)
docs/dev/lanes/predloop_report.md, docs/dev/lanes/predasc_report.md, every docs/dev/lanes/*_rulings.md and
*_deliver.txt, docs/dev/pred/{journal,wake,owner,to_main,from_main}.md, git log BODIES (subject lines OK),
/var/tmp/pcrec-pcrec/scratch/{predloop,predasc}/, everything under /var/tmp/pcrec-pcrec/scratch/pred/ (use the
copies in R/scratch_named/ only), docs/dev/reviews/2026-11-19-r59-* and -r60-* (earlier rounds), every other
docs/dev/reviews/ file on predicates, the coordinator's `.coord/` dir in the round dir, other critics' dirs and files,
other worktrees. You should not need the repo at all; if you must, use only
`git -C /home/pcrec/projects/pcrec show 2e0adc746:<path>` for docs/design/predicates/* or the record.

## Quote verification
ONE lens verifies the owner's quotes word for word against the record: RULING. Other lenses cite quotes without
re-checking them.

## Output (each critic)
Your findings file ALREADY EXISTS (pre-created by the coordinator with headings): `R/../<LENS>.md`, i.e.
`/var/tmp/pcrec-pcrec/scratch/crit-predfold1119/<LENS>.md`. APPEND to it (Edit, or `cat >> file <<'EOF'`);
NEVER overwrite it with Write (the harness refuses a subagent's whole-file Write and the file stays empty).
Append each finding THE MOMENT you have it, one append per finding. Format per finding:
  ### <LENS>-n  CONFIRMED|SUSPECTED  severity: answer|doc|design|maintenance  effort: S|M|L
  where: file § / tag (and line in R/subject/<file>)
  claim: ...
  repro: the exact call + observed vs expected (CONFIRMED), or what would confirm it (SUSPECTED)
  blast radius: which other pieces read this
  proposed fix: one line
A finding against a RULED piece cites the record entry and argues, or drops. Under `## PROBED-AND-HELD` list what
you checked that held, with case counts. Finish with the single line `CRITIC COMPLETE` appended last.
A nested agent's final reply often fails to reach the coordinator: that is EXPECTED and needs no escalation; the
`CRITIC COMPLETE` line in your file is the delivery. Final reply at most 150 words.
