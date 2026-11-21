# COMMON brief: critic round archdense (2026-11-18), ARCHITECTURE mode (the first real use)

Read this whole file first, then your own one-question prompt. R0 = /var/tmp/pcrec-pcrec/scratch/crit-archdense.

## Scope mandate (binding)

- Touch ONLY the pcrec repository (/home/pcrec/projects/pcrec) and its sibling pcrec-bench; you need only pcrec,
  READ-ONLY. You edit NOTHING in either repo. No commits, no worktrees, no checkouts.
- Scratch ONLY under your own lens directory `R0/<lens>/` (it exists). Never /tmp, never anywhere else.
- Never run `make`, a suite, the box queue, or anything heavy. Read-only `git` commands are your main tool. You MAY
  run the main tree's existing `/home/pcrec/projects/pcrec/build/pcrec` on a SINGLE pattern (under `timeout 60`,
  output under `R0/<lens>/`) to illustrate an emitted-text claim; it was built from main, not from T, so label such a
  result an illustration. Single light processes only.
- Never `cd X && cmd` (a hook blocks it): use absolute paths and `git -C /home/pcrec/projects/pcrec`, or a subshell.
- Aim for 20-40 minutes. The round must be finished well before 20:00 today.

## The subject (frozen)

- SUBJECT: the ARCHITECTURE NOTE `docs/design/dense_hit_arch.md` at commit 5dcc98dfc (branch lane/archdense). Read the
  READ-ONLY COPY `R0/R/subject/dense_hit_arch.md` (302 lines; fine to read whole). It was written by the
  `pcrec-architect` skill; the skill's required note shape (what each section must hold) is in
  `R0/R/subject/pcrec_architect_SKILL_at_T.md`.
- TREE: the note was written against T = 57fcb5737dff37bd97429fb1e889ca0233d12e10. READ ALL CODE AND RULINGS AT T:
  `git -C /home/pcrec/projects/pcrec grep -n PATTERN 57fcb5737 -- PATHS` and
  `git -C /home/pcrec/projects/pcrec show 57fcb5737:PATH`. Never the working tree. (main HEAD is T plus one journal
  commit: no cited site moved between T and main; the coordinator diffed it.)
- What an architecture note is: the step between requirements and design. It answers "where does this feature live
  in today's tree, and what must change shape first?": a site map found by grep (each site classed), the ride-along
  register rows it touches, the remodels that land first (units), the general form and siblings, the seams, what is
  deleted, and what the design step must decide. It designs NO algorithm, writes no code, proposes no schedule.
  This round does NOT review the algorithm, measurements or build cost (later rounds own those): it reviews whether
  the note's map of the tree, its register dispositions, its first units and its seams are right and complete.
- REQUIREMENTS (what the feature must do): plan row [REQ-PAST-LAST] at T, its three NOTES of 2026-11-12 (the last
  three lines). Copy: `R0/R/subject/req_past_last_row.md` (the row's lines are long; read them whole). The note's
  header lists further sources, all at T: decisions D144, D146, D147, D157, D195 (`docs/dev/decisions.md`); plan rows
  [FLAG-DEMOTE], [LANDWALK], [REQRUN-VM], [REQ-HANDOFF-L1]; `docs/spec/tuning.md` §2.41 (the section starts at the
  heading `### 2.41`); `memfn/docs/requests.md` R-30 (heading `## R-30`) and R-41; `memfn/docs/responses.md` R-30 notes.
  To read one plan row: `git -C /home/pcrec/projects/pcrec show 57fcb5737:docs/dev/plan.md | grep -n '^- \[TAG\]'`,
  then read that row only (to the next `- [` line).
- THE RULES the note is reviewed against: `docs/dev/guide/architecture.md` at T, copy `R0/R/subject/architecture_at_T.md`
  (the five tiers; the ride-along REGISTER is its last section, "# The ride-along register", line ~594). Also
  `docs/dev/guide/coding.md` and `docs/dev/guide/critics.md` at T if you need them.
- Seams / kit: the kit is `memfn/` (contract `memfn/include/memfn.h`, `docs/design/memfn/integration.md`); the
  instruction-stream roadmap is `docs/design/stream/roadmap.md` (register row 12 points to it).

## Denylist (never open, grep or diff these; exclude them from every repo grep)

- `docs/dev/lanes/archdense_report.md` (the architect's own report; it exists only on lane/archdense, not at T) and
  anything else `docs/dev/lanes/archdense*`.
- `docs/dev/dev_journal.md`, `docs/dev/wake.md`, `docs/dev/owner.md`, git log BODIES (subject lines only), job logs,
  the box queue, every other worktree (`/home/pcrec/projects/pcrec/worktrees/`, above all `worktrees/archdense`), and
  `R0/.coord/` (the coordinator's notes), and other lenses' directories and files in R0.
- Your greps run at T, where the report does not exist; still add `':!docs/dev/lanes/archdense*'
  ':!docs/dev/dev_journal.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md'` to any `git grep` over the whole tree.
  A plain `grep -r` (avoid it) needs `--exclude='archdense*' --exclude=dev_journal.md --exclude=wake.md
  --exclude=owner.md --exclude-dir=worktrees --exclude-dir=.coord`.
- Earlier reviews of OTHER subjects are allowed (the note cites review 2026-11-12-r2-reqpast TH-7; you may read it).

## Rules you will cite

- When you state a rule of the note or the guide, QUOTE its sentence with its line (note line, or architecture.md
  line in the copy); never paraphrase a rule from this brief.
- Owner quotes: ONLY the RULING lens verifies the owner's quoted words word for word against the record; other lenses
  cite them without re-checking.
- Every count or "N hits" claim you make carries the exact command that printed it. Pass grep patterns in single
  quotes.
- Spellings and naming of new things (U1's question text, P1's name) are not findings unless they mislead.

## Output format

- Your findings file ALREADY EXISTS (the coordinator created it with its headings): `R0/<LENS>.md`. It is your output,
  not an input. Append to it INCREMENTALLY: ONE APPEND PER FINDING, the moment you have it.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: the git grep/show command, observed vs what the note says) or
  SUSPECTED (what would confirm it); severity (answer / speed / design / maintenance / doc); effort; blast radius;
  note line(s) or section; the guide rule it rests on (quoted, with its line). A finding against a RULED D-row or an
  owner NOTE cites it and argues, or is dropped. A deviation that HAS a register noted-deviation row and is small is
  reported NOTED with its row, not as a finding.
- End the file with `## PROBED-AND-HELD` filled (what you checked that held, with counts: how many sites, rows,
  commands you re-ran), then a last line exactly `CRITIC COMPLETE`.
- Then run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir R0 --deliver R0/<LENS>_deliver.txt <lens>` (R0 spelled
  out in full) and end when it prints DONE (fix the file if it does not).
- Final reply at most 150 words. A failed final reply is EXPECTED for a nested agent and needs NO escalation to anyone:
  the CRITIC COMPLETE line in your file is the delivery. If a Write/append to your file is REFUSED, put your findings
  in your final reply, marked relayed; never route around a refusal.
