# COMMON brief — critic round predspec27 (DESIGN mode), read this first

## Scope mandate (binding)
- Touch ONLY the two mandated repositories, /home/pcrec/projects/pcrec and /home/pcrec/projects/pcrec-bench, and
  ONLY READ them. You edit NOTHING in either repo. You never run `make`, a test suite, `scripts/boxqueue`, or anything
  heavy. Scratch ONLY under your own lens dir `/var/tmp/pcrec-pcrec/scratch/crit-predspec27/<lens>/` (lower-case lens
  name, already created). Nothing under /tmp. Absolute paths or `git -C`; a `cd X && cmd` chain is blocked by a hook
  (a `(cd X && cmd)` subshell is fine).
- PCRE2 facts come from RUNNING libpcre2 (through the evidence's `pcre2h.py`, or python `re` as a second control),
  never from reading a PCRE2 source copy (D181).
- Pass patterns in single quotes or via a file (shell quoting eats `\b`, `\k`, `$y`). Python: `python3 -I -B`.
- Bound every run: `timeout 900 ...`, one process at a time.

## The subject (frozen)
- `docs/design/predicates_draft.md` REVISION 27, commit a088fe542c63 (main HEAD b22285a36 holds the same text). It is
  a DESIGN-ONLY language document (the predicate language, [COND-FAMILY] #6): no product code exists for it and none
  is to be built; there is no build tree. Read the READ-ONLY copies, not the repo:
  - `R/subject/predicates_draft_rev27.md` (9,333 lines; the subject)
  - `R/subject/diff_rev26.1_to_rev27.diff` (636 lines: what REV 27 changed: the round's weight)
  - `R/subject/diff_rev26_to_rev27.diff` (1,390 lines: rev 26 was the last REVIEWED revision; rev 26.1 was not
    reviewed. Rev 26.1-only hunks are in scope only where rev 27 rests on them.)
  - `R/subject/predicates_future.md` (the parked-ideas file at main HEAD; item 30 is filed by the record).
  (`R/` = `/var/tmp/pcrec-pcrec/scratch/crit-predspec27/R/`.)
- WHAT REV 27 IS (its own changelog, lines 9-23): a FOLD of the five COND-FAMILY entries of 2026-11-18 afternoon:
  backref-label RULED (capture); the value-hole DISCUSSION; value-hole "yes but"; match-is-rx RULED; read-is-constant
  RULED. Where rev 27 lives in the draft (find more with `grep -n 'REV 27'`, 53 hits):
  - R.1.15 THE VALUE HOLE, rewritten: lines 2037-2125
  - R.1.16 ONE TYPE (NEW): lines 2126-2212, with THE TYPE TABLE (rows T1..; line 2168 on) and ANSWERS CHANGED
    (rows A1-A16, lines 2196-2211)
  - R.1.0 place table's MATCH VALUE row (line 834); R.1.13 / R.1.7 (b) (around 1199-1204, 1683-1701)
  - §R.2 (2213-), §R.6 (2394-), §R.7 (2486-), §R.8 THE OPEN TABLE (2586-2890: value-hole and backref-label ANSWERED;
    new questions numeral-width, unset-in-hole, dollar-warning, same-name-twice, array-in-hole, value-test,
    lift-order, construction-line), §R.9 (2891-), §R.11 rows 120-124 (lines 3262-3266), §4.1, §0.1 L28/L33.

## The record of the owner's words (the ONLY source of rulings)
- `R/subject/record_2026-11-18_afternoon.md` = docs/design/plan_row_bodies/COND-FAMILY.md from the entry
  "2026-11-18 OWNER RULING — backref-label: capture" to the end of the file (5 entries, 97 lines; frozen at main
  b22285a36; every entry predates the subject commit). Earlier COND-FAMILY entries (the morning of 2026-11-18 and
  before) are cited by the draft; read them with
  `git -C /home/pcrec/projects/pcrec show b22285a36:docs/design/plan_row_bodies/COND-FAMILY.md` (454 KB: grep it,
  never read it whole).
- Passages marked "THE MANAGER'S READINGS", "the manager's", "MANAGER'S ANSWER" are NOT the owner's and are fair
  game: a critic may refute them. Only the owner's quoted words ("HIS WORDS") and the entries' RULED lines bind.
- Only the RULING lens checks the owner's quotes word for word against the record; every other lens cites quotes as
  the draft gives them without re-checking.
- decisions.md / plan.md, if you need them: `git -C /home/pcrec/projects/pcrec show 57fcb5737:docs/dev/decisions.md`
  (the freeze), never the live tree.

## Evidence the draft cites (runnable read-only copy)
- `R/tree/docs/dev/lanes/predspec27_evidence/` (predspec27_model.py, its CLAUDE.md, committed outputs), plus
  `predspec261_evidence/`, `predspec26_evidence/`, `rxmodel_evidence/pcre2h.py` (the libpcre2-8 10.46 binding:
  RUN it, never study its internals for PCRE2 facts).
- Run (seconds, one process; writes only to stdout):
      (cd /var/tmp/pcrec-pcrec/scratch/crit-predspec27/<lens> && timeout 900 python3 -I -B \
         /var/tmp/pcrec-pcrec/scratch/crit-predspec27/R/tree/docs/dev/lanes/predspec27_evidence/predspec27_model.py > fwd.out)
  The coordinator checked: 21 of 21 OK, identical to the committed .out.
  Sabotage: `PREDSPEC27_SABOTAGE=1` (all) or a comma list `s1,..,s8` (list in the script header). There is NO
  separate ORDER/SWAP switch; the sabotages ARE the switches. Ask of any switch you use: can it fail, and does it
  reverse something that carries meaning? A switch that moves nothing meaningful guards nothing.
- To modify a script, COPY it into your lens dir (keep `rxmodel_evidence/pcre2h.py` reachable: copy that dir beside it
  or set sys.path) and edit the copy. Never write into R/.
- The evidence is RULE-AS-CODE for its TT part (consistency, never an independent control): its CLAUDE.md says so.

## Guide files the round reviews against
- docs/dev/guide/critics.md ("Lessons from review rounds"), docs/dev/guide/architecture.md (goals),
  docs/design/CLAUDE.md (standing questions). Read only what your question needs.

## DENYLIST (do NOT read, grep or diff these before your findings file is complete)
- docs/dev/lanes/predspec27_report.md; docs/dev/lanes/predspec26_report.md; docs/dev/lanes/predspec261_report.md;
  any docs/dev/lanes/predspec2* report file.
- docs/dev/reviews/2026-11-17-r42-predspec242*, 2026-11-17-r43-predspec25*, 2026-11-18-r47-predspec26* (files AND
  directories), and any other review of predicates_draft.md.
- `git log` bodies beyond subject lines; job logs; other worktrees (`worktrees/`); the box queue; other `crit-*`
  round dirs under scratch; the coordinator's `.coord/` dir in this round dir.
- When you grep or diff the repo, EXCLUDE these: plain grep `--exclude='predspec2*_report.md' --exclude-dir='2026-11-1[78]-r4[2-9]*' --exclude-dir=worktrees`;
  git pathspecs `':!docs/dev/lanes/*_report.md' ':!docs/dev/reviews/*'`. Better: grep the R/ copies only.
- The draft itself CITES r47 finding ids (A1.., B1..) and the reports by name: reading the draft's own text about them
  is fine; opening the cited files is not.

## Output format (binding)
- Your findings file ALREADY EXISTS, pre-created by the coordinator with its headings, at
  `/var/tmp/pcrec-pcrec/scratch/crit-predspec27/<LENS>.md`. It is YOUR OUTPUT, not an input. Write into it
  INCREMENTALLY: append each finding the moment you have it, one append per finding (Edit or a heredoc append).
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command or quoted lines, observed vs expected) or
  SUSPECTED (what would confirm it); severity (answer / design / doc / maintenance); effort; blast radius; location
  (draft line + section; the record entry by its heading). A finding against a RULED entry cites the entry's words and
  argues, or is dropped.
- "answer" severity = a sentence of the draft gives a pattern/text a different verdict, hit or value than the draft's
  own rules (or the owner's ruling) give.
- State the MINIMUM WITNESS LENGTH your probe pool reached (text length and pattern size): a 0-differ below the length
  a witness needs is not evidence.
- End with `## PROBED-AND-HELD` (what you checked that held, with case counts), then the line `CRITIC COMPLETE` as the
  LAST line of the file. That line is the delivery.
- Then run: `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-predspec27 --deliver /var/tmp/pcrec-pcrec/scratch/crit-predspec27/<LENS>_deliver.txt <LENS>`
  and end only when it prints DONE (fix what it names).
- Final reply at most 150 words. You are a nested agent: a failed or undeliverable final reply is EXPECTED and needs no
  escalation to anyone; the file is the delivery. If your findings-file Write is REFUSED, SendMessage your findings to
  the agent that launched you at once, marked relayed; do not route around the refusal any other way.
- Time: aim to finish in 30-40 minutes. One question; depth beats breadth.
