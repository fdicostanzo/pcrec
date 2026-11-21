# COMMON brief: critic round predspec26 (review r47, 2026-11-18), DESIGN mode, a RE-CHECK

Read this whole file first, then your own one-question prompt.

## Scope mandate (binding)

- Touch ONLY the pcrec repository (/home/pcrec/projects/pcrec) and, if ever needed, its sibling pcrec-bench; you need
  only pcrec, READ-ONLY. You edit NOTHING in either repo. No commits, no worktrees.
- Scratch ONLY under your own lens directory `R0/<lens>/` (R0 = /var/tmp/pcrec-pcrec/scratch/crit-predspec26). Never
  /tmp. When you run a script, set `PCREC_TMPDIR=R0/<lens>` and run from that directory.
- Never run `make`, a suite, the box queue, or anything heavy. Single light processes only: ONE drill process of yours
  at a time (a python script calling python `re` or libpcre2, or the evidence engine; seconds each). Every command of
  uncertain length under `timeout` (e.g. `timeout 300 python3 -I -B ...`).
- Never `cd X && cmd` (a hook blocks it): use absolute paths, `git -C`, or a subshell `(cd X && cmd)`.
- The round must be finished well before 20:00 today. Aim for 20-40 minutes.

## The subject (frozen)

- SUBJECT: `docs/design/predicates_draft.md` revision 26 at commit 29c16a6ba (main HEAD holds the same text). Read the
  READ-ONLY COPY: `R0/R/subject/predicates_draft.md` (8,750 lines; do not read it whole: use grep and ranges).
- This is a RE-CHECK. The last REVIEWED revision is rev 25 (commit db77f9daed0f): `R0/R/subject/predicates_draft_rev25.md`.
  Rev 25.1 (commit 8b6291f5d, NOT reviewed) is `R0/R/subject/predicates_draft_rev25.1.md`. Scope your reading through
  the diffs: `R0/R/subject/diff_rev25_to_rev26.diff` (1,690 lines; the two unreviewed revisions together) and
  `R0/R/subject/diff_rev25.1_to_rev26.diff` (1,152 lines; rev 26 alone).
- Rev 26 does TWO things: STAGE A folds a day of owner rulings (every COND-FAMILY entry dated 2026-11-18, from
  "2026-11-18 MANAGER CORRECTION — "the right side of `&`" was the manager's slip" to the end of the record as it
  stood at the subject commit; the draft's §R.11 rows 76-107); STAGE B RESTRUCTURES §R.1 around ONE PLACE TABLE
  (new R.1.0, subject lines 725-772: the place table and THE HOLE POSITIONS table), replacing rev 25.1's R.1.1 PLACES
  paragraph and its R.1.14 position table by pointers, and adds R.1.15 (the value hole fleshed out, UNRULED). The
  restructure must LOSE NOTHING the old prose said. The draft's own changelog entry for rev 26 is subject lines 7-23.
- RULINGS RECORD: `docs/design/plan_row_bodies/COND-FAMILY.md`, the owner's words. Copy at the ruling freeze
  (commit b850ee1, main HEAD): `R0/R/subject/COND-FAMILY.md` (3,645 lines; the 2026-11-18 entries are lines 3091-3645).
  Entries are labelled RULED, LEAN, OBSERVATION, DISCUSSION, PROPOSAL or IDEA; passages marked as the MANAGER'S
  readings are NOT the owner's words. ONE ENTRY WAS WRITTEN AFTER THE SUBJECT COMMIT: lines 3632-3645 ("2026-11-18
  MANAGER CORRECTION — three of the manager's readings of this morning were NOT supported by the runs"); its diff is
  `R0/R/subject/COND-FAMILY_after_subject.diff`. It is a manager's entry (no owner words), not folded in rev 26.
- Parked ideas: `R0/R/subject/predicates_future.md` (item 24 gained entries 21-29 in rev 26). The rx module proposal:
  `R0/R/subject/rx_module.md`.
- Ruling files: read `docs/dev/decisions.md` and `docs/dev/plan.md` ONLY as `git -C /home/pcrec/projects/pcrec show
  8949a92:docs/dev/decisions.md` (the freeze), never the live tree. To find a plan row use `grep -n '^- \[TAG\]'` on
  that output and read only that row.
- Guide (the rules critics review against): `/home/pcrec/projects/pcrec/docs/dev/guide/architecture.md` (goals),
  `docs/dev/guide/critics.md`. Design-note standing questions: `docs/design/CLAUDE.md`.
- DESIGN ONLY: predicates are not being built. The CONTROLS are libpcre2 and python `re`.

## The evidence (runnable, read-only copy)

- `R0/R/tree/docs/dev/lanes/predspec26_evidence/` (CLAUDE.md, `predspec26_model.py`, `.out`, sabotage outputs); it
  builds on `predspec251_evidence/` and `predspec25_evidence/` (same tree). The libpcre2 wrapper is
  `R0/R/tree/docs/dev/lanes/rxmodel_evidence/pcre2h.py`: IMPORT and RUN it, never read its source (D181 wall); for your
  own drills: `sys.path.insert(0, "R0/R/tree/docs/dev/lanes/rxmodel_evidence"); import pcre2h as P` and look at how
  `predspec26_model.py` calls it (you may read the model).
- Re-run (seconds; the coordinator checked it is byte-identical to the committed .out, CHECKS 111 of 111 OK):
      (cd R0/<lens> && PCREC_TMPDIR=R0/<lens> timeout 300 python3 -I -B R0/R/tree/docs/dev/lanes/predspec26_evidence/predspec26_model.py > fwd.out)
  Sabotage: env `PREDSPEC26_SABOTAGE=1` (all) or `s1,s2,..` (list in that dir's CLAUDE.md).
- The engine has NO ORDER/SWAP switch (only sabotages). Ask whether any of its rules is a trap or order-dependent and
  would need one; a switch that reverses nothing that carries meaning guards nothing.
- The engine's CLAUDE.md has a table of its classifier predicates (RULE-AS-CODE) beside the draft sentence each
  claims to implement: a classifier line is a CONSISTENCY check, never an independent control. Engine readings with
  no sentence in the subject are findings.
- Modes: WHOLE (the program against a whole value), SEARCHED (first match in a subject), FIND-ALL (PCRE2's global
  loop, R.1.2). A find-all PLACE (an `occurrences`/`contains` argument, a `records` item) is a mode of its own.
  Numerals, quoting the subject's §2.4 rule (subject line ~630): "an integer comparison set contains CANONICAL
  numerals of VARIABLE WIDTH (the `\d+` shape: no leading zeros, sign or decimal point unless the literal has them)".
- Spellings in the draft (`SEQ`, `!`, `rx.digit`, `[x = A]`, warning names) are PLACEHOLDERS: never a finding on syntax.

## Denylist (never open, grep or diff these; exclude them from every repo grep)

- Every `docs/dev/lanes/predspec*_report.md`; `docs/dev/lanes/file40_report.md`, `file42_report.md`,
  `file43_report.md`, `rxlib_report.md`, `rxmodel_report.md`, `lastpass_report.md`; every other lane report.
- Every file or directory under `docs/dev/reviews/` whose name contains predspec, jointcond, absfold or condkind (the
  subject cites reviews r40, r42, r43 by path: do NOT open them).
- `docs/dev/dev_journal.md`, `docs/dev/wake.md`, `docs/dev/owner.md`, git log BODIES (subject lines only), job logs,
  the box queue, other worktrees (`worktrees/`), and `R0/.coord/` (the coordinator's notes).
- You should not need the repo beyond the guide and `git show 8949a92:`. If you grep it, use `git -C
  /home/pcrec/projects/pcrec grep ... -- ':!docs/dev/lanes/*report*' ':!docs/dev/reviews' ':!docs/dev/dev_journal.md'
  ':!docs/dev/wake.md' ':!docs/dev/owner.md'`; a plain `grep -r` needs `--exclude-dir=reviews --exclude='*report*'
  --exclude=dev_journal.md --exclude=wake.md --exclude=owner.md`.

## Rules of the subject you will cite

- When you state a rule of the subject, QUOTE its sentence with its line; never paraphrase a rule from this brief.
- Owner quotes: ONLY the RULING lens verifies the owner's quoted words word for word against the record; other lenses
  cite them without re-checking.
- Pass regex patterns in single quotes or via a file; a shell must never eat a backslash. Check each pattern you cite
  is the one you ran.

## Output format

- Your findings file ALREADY EXISTS (the coordinator created it with its headings): `R0/<LENS>.md`. It is your output,
  not an input. Append to it INCREMENTALLY: ONE APPEND PER FINDING, the moment you have it.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command or grep, observed vs expected) or SUSPECTED
  (what would confirm it); severity (answer / design / doc / maintenance); effort; blast radius; subject line(s) or §.
  A finding against a RULED entry cites the entry (COND-FAMILY line) and argues, or is dropped.
- End the file with `## PROBED-AND-HELD` filled (what you checked that held, with case counts), then a last line
  exactly `CRITIC COMPLETE`.
- Then run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir R0 --deliver R0/<LENS>_deliver.txt <lens>` and end when
  it prints DONE (fix the file if it does not).
- Final reply at most 150 words. A failed final reply is EXPECTED for a nested agent and needs NO escalation to anyone:
  the CRITIC COMPLETE line in your file is the delivery. If a Write/append to your file is REFUSED, SendMessage your
  findings to the coordinator (name: crit-predspec26) at once, marked relayed; never route around a refusal.
