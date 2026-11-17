# COMMON brief — critic round predspec24 (DESIGN), 2026-11-17

## Scope mandate (binding)
Touch ONLY the two mandated repositories (/home/pcrec/projects/pcrec and /home/pcrec/projects/pcrec-bench), and only
READ them. Write ONLY under your own lens directory `/var/tmp/pcrec-pcrec/scratch/crit-predspec24/<lens>/` (your
findings file is already there). No `make`, no build, no worktree, no git writes, no edits to either repo, nothing in
/tmp. DESIGN ONLY: nothing is built, no build go is asked. The box is SHARED: every python run is single-process,
under `timeout 1800` (shorter is better), ONE AT A TIME (never two of your runs at once), with your lens dir as cwd
and `PCREC_TMPDIR=<your lens dir>`. HARD STOP: nothing of yours may be running after 00:30 (a timing window opens at
01:00); finish, write and end well before.

## Subject (frozen; read these copies, not the live tree)
R = /var/tmp/pcrec-pcrec/scratch/crit-predspec24 (R/subject and R/tree are read-only copies)
- SUBJECT: `R/subject/predicates_draft.md` = docs/design/predicates_draft.md REVISION 24 (commit 4e4389ab3, merged as
  092e0fd1a; main HEAD at the freeze, f7111da43, carries the same text: that is the tree a build would land on; no
  code is cited as changed). Rev 24 REPLACES the draft's foundation: its §R (lines 409-802) is the definition of record
  and WINS over any later section ("READ FIRST"). Later sections carry "[REV 24]" marks naming what is superseded;
  §R.9 lists the reversed rulings and marked sections; §16 and the changelog are history.
- The REPLACED foundation, for diffs: `R/subject/predicates_draft_rev23_2.md` (= `git show 9b61e41e9:...`, rev 23.2;
  its §R was the three-valued model). Read it only to compare; it is not under review.
- RULINGS RECORD (append-only; a later entry supersedes an earlier one): `R/subject/COND-FAMILY.md` (as at the freeze).
  Every entry dated 2026-11-17 is new since the previous revision: they start at line 2067; the owner's rulings of the
  day start at line 2101 ("OWNER LEAN — branch-scope") and run to the end. Each entry separates the OWNER'S WORDS
  ("HIS WORDS", quoted) and RECORD from readings marked MINE (the manager's). The last 8 lines (the rx-module ADDENDUM,
  about 14:55) were written AFTER the subject's commit. `R/subject/COND-FAMILY_at_subject.md` is the file as the
  subject's commit saw it. The draft's "CF:NNN" cites are line numbers in this file.
- `R/subject/predicates_future.md` (items 14 and 17-21 are cited by rev 24).
- `R/subject/decisions.md` (main at the freeze). Any other ruling file ONLY via
  `git -C /home/pcrec/projects/pcrec show f7111da43:<path>`, never the live tree.

## Evidence (runnable read-only copy)
`R/tree/docs/dev/lanes/predspec24_evidence/predspec24_model.py` (rev 24's engine; its HEADER lists the readings it
implements) loads `lastpass_evidence/lastpass_model.py`, which loads `pathimpact_evidence/pathimpact_model.py` (a path
enumerator over Python `re`) and `rxmodel_evidence/pcre2h.py` (libpcre2-8 10.46 via ctypes, WITH CALLOUTS: usable as
the ORACLE; see its own header and rxmodel_evidence/CLAUDE.md). Run from YOUR lens dir:
  `cd R/<lens> && PCREC_TMPDIR=$PWD timeout 1800 python3 -I R/tree/docs/dev/lanes/predspec24_evidence/predspec24_model.py > fwd.out`
(37 s, 166 MB; the coordinator re-ran it: byte-identical to the committed `predspec24_model.out`; it writes stdout
only). Switches (PREDSPEC24_SWAP / _SABOTAGE / _RULES=23.2): the engine's header. You may import the engines (and
pcre2h) from your own scripts in your lens dir (sys.path to the read-only dirs); never write into R/tree or R/subject.
Lane reports you MAY read (evidence the subject cites, not reviews of it): `R/tree/docs/dev/lanes/pathimpact_report.md`,
`rxmodel_report.md`, `lastpass_report.md`. `docs/design/rx_module.md` is a SEPARATE proposal, not the subject.

## Who owns what is RULED (attack the manager's, respect the owner's)
- OWNER words are only what COND-FAMILY.md quotes as HIS WORDS. Everything labelled the manager's ("MINE", "THE
  MANAGER'S READING / RULING / PROPOSAL / RESTATEMENT", "THE DRAFT'S READING", "told, not asked") is NOT the owner's:
  attack it. Rev 24's §R.8 / §R.11 name them: three-valued (retired), record-under-not (dissolved), condition-or
  (deleted), hits-committed, join-order, polarity-rule, looped-warning, sql-picture, repeated-means; OPEN items:
  complement-place, nested-complement, lookahead-labels, group-truth / pass-table in named forms, atomic-spelling,
  conditional-spelling, every-pass-spelling.
- A finding against an OWNER ruling cites it and argues (a consequence he may not have seen), or drops.
- Owner quotes: ONLY the ruling lens verifies quotes word for word against the record; other lenses cite them as the
  draft gives them without re-checking.

## Modes
Every answer has a MODE: WHOLE value, SEARCHED (the first match in a subject), FIND-ALL (every match, left to right),
and the NESTED places of §R.1.1 (either side of `&`, a `label:` set, an `occurrences`/`contains` argument, a `records`
item, inside a complement, inside a lookahead, inside a loop body via a hole, inside `atomic(...)`). A property stated
without its mode is a finding. Numerals are canonical (§2.2: `0|[1-9]\d*`): recompute counts with the DOCUMENT's set
rules, not an engine's lambda.

## Denylist (do not open, grep or list)
- docs/dev/lanes/predspec24_report.md and docs/dev/lanes/predspec24_deliver.txt (and every other *_deliver.txt);
- docs/dev/owner.md, docs/dev/wake.md; docs/dev/dev_journal.md (the whole file: you do not need it);
  docs/dev/full_suite_ledger.md;
- EVERY file under docs/dev/reviews/ (earlier reviews of this subject; you get no review input);
- /var/tmp/pcrec-pcrec/scratch/crit-* other than this round's dir, and every other directory under
  /var/tmp/pcrec-pcrec/scratch/;
- `git log` bodies beyond subject lines; other worktrees (worktrees/*); the box queue; ~/.claude (memory);
- R/.coord/ (the coordinator's notes) and every OTHER lens's directory under R.
You should not need the repo at all beyond the `git show f7111da43:...` files. If you plain-grep the repo, add
`--exclude-dir=worktrees --exclude-dir=reviews --exclude=owner.md --exclude=wake.md --exclude=dev_journal.md
--exclude=full_suite_ledger.md --exclude=predspec24_report.md --exclude='*_deliver.txt'`; with `git grep`, the
pathspecs `':!docs/dev/reviews' ':!docs/dev/dev_journal.md' ':!docs/dev/lanes/predspec24_report.md' ':!*_deliver.txt'`.

## Method rules
- Pass patterns in single quotes or via a file (shell quoting eats `\b`, `\d`). Quote the draft by § and line number
  in R/subject/predicates_draft.md.
- You are briefed from the SUBJECT's text: where this COMMON or your prompt and the subject disagree, test the subject.
- APPEND EACH FINDING TO YOUR FILE THE MOMENT YOU HAVE IT, one append per finding. Do not save findings for the end.

## Output format
Your findings file ALREADY EXISTS (the coordinator pre-created it with its headings); it is your OUTPUT, not an input.
Append under `## Findings`. Each finding: id `<LENS>-n`; CONFIRMED (with a repro: the program, the text, the mode, the
command or the hand derivation, observed vs expected) or SUSPECTED (what would confirm it); severity (answer / design /
doc); effort; blast radius; the draft's § and line. Then `## PROBED-AND-HELD` (what you checked that held, with case
counts). The LAST line of the file is exactly `CRITIC COMPLETE`. Then run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-predspec24 --deliver /var/tmp/pcrec-pcrec/scratch/crit-predspec24/<lens>/deliver.txt <lens>`
(substitute your lens name) and end only once it prints DONE. Final reply at most 150 words. If a Write to your file
is refused, return your findings as your FINAL REPLY instead (it reaches the coordinator; mark them relayed); never route around a refusal.
