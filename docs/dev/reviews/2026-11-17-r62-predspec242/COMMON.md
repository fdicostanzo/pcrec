# COMMON brief — critic round predspec242 (DESIGN, confirming re-check), 2026-11-17

## Scope mandate (binding)
Touch ONLY the two mandated repositories (/home/pcrec/projects/pcrec and /home/pcrec/projects/pcrec-bench), and only
READ them (you should not need them at all: the copies below are enough). Write ONLY under your own lens directory
`/var/tmp/pcrec-pcrec/scratch/crit-predspec242/<lens>/` (your findings file is already there). No `make`, no build, no
worktree, no git writes, no edits to either repo, nothing in /tmp. DESIGN ONLY: nothing is built, no build go is
asked. The box is SHARED with the owner (his evening hold): every python run is single-process, under
`timeout 1800` (shorter is better), ONE AT A TIME (never two of your runs at once), with your lens dir as cwd and
`PCREC_TMPDIR=<your lens dir>`. Never `cd X && cmd` (a hook blocks it): use absolute paths or a `(cd X && cmd)`
subshell. HARD STOP: nothing of yours may be running after 22:30 today; write your file as you go and end well before.

## Subject (frozen; read these copies, not the live tree)
R = /var/tmp/pcrec-pcrec/scratch/crit-predspec242 (R/R/subject and R/R/tree are read-only copies)
- SUBJECT: `R/R/subject/predicates_draft.md` = docs/design/predicates_draft.md REVISION 24.2 (commit dc2922ec5,
  merged as ddd83fb1c; main HEAD 110006837 carries the same text). Its §R (lines 450-1247) is the definition of
  record and WINS over any later section ("READ FIRST"). Rev 24.2 changed the loop-label rule: a loop pass has its own
  labels; a bare condition after a pattern reads the LAST pass's own label; a label two loops deep is seen at the
  OUTERMOST view; a condition written on the item is judged per pass; the CAPTURE (PCRE's carried value, read inside rx
  text) is regex's and the LABEL (read by conditions, defaults, joints, `$x`, `some`, `occurs`) is the language's
  (R.1.7, §R.6, §R.7). Rev 24.1 (the revision before) fixed an earlier round's items, among them: the engine runs the
  right operand of `&` and `!B` on the stretch's own text; the WHOLE comparison key carries labels; new PART C
  libpcre2 models; R.8's open table; R.11's ruling table. Later sections carry "[REV 24]/[REV 24.1]/[REV 24.2]" marks.
- RULINGS RECORD (append-only; a later entry on a subject supersedes an earlier one; the LAST entry on a subject is
  the settled state): `R/R/subject/COND-FAMILY.md` (main 110006837). The 2026-11-17 entries run from line 2087 to the
  end; the EVENING entries the revision folds start at line 2364 ("OWNER RULING — exception-rule") and include two
  entries the owner superseded the same evening (2423 "labels match every pass" was reconsidered at 2442, then ruled at
  2454). Each entry separates HIS WORDS (the owner's, quoted) and RECORD from readings marked MINE (the manager's).
  Note: the subject's own branch saw the file only to line 2472; the entries from 2474 (nested-pass, the black-box
  ADDENDUM, kind of language, atomic-search, polarity-rule) were on main and the subject cites them.
- `R/R/subject/predicates_future.md` (items 14 and 17-22 are cited).
- Any other ruling file (decisions.md, plan.md) ONLY via `git -C /home/pcrec/projects/pcrec show 110006837:<path>`.

## Evidence (runnable read-only copy)
`R/R/tree/docs/dev/lanes/predspec242b_evidence/predspec242b_model.py` is rev 24.2's engine: it EXECUTES rev 24.1's
engine (`predspec241_evidence/`) in memory with textual patches (its HEADER and its CLAUDE.md list them: READ THE
HEADER for the readings it implements), which in turn loads `lastpass_evidence/lastpass_model.py`, which loads
`pathimpact_evidence/pathimpact_model.py` (a path enumerator over Python `re`) and `rxmodel_evidence/pcre2h.py`
(libpcre2-8 10.46 via ctypes WITH CALLOUTS: THE ORACLE; see its header). The coordinator re-ran the engine from this
copy before briefing: about 3-4 minutes, byte-identical to the committed `predspec242b_model.out` (which is the
answer file every §R number cites, by PART and tag; read it rather than re-running when you only need a printed line).
Run (only if you need a switch or a modified copy):
  `(cd R/<lens> && PCREC_TMPDIR=$PWD timeout 1800 python3 -I -B R/R/tree/docs/dev/lanes/predspec242b_evidence/predspec242b_model.py > fwd.out)`
SWITCHES: `PREDSPEC242B_SABOTAGE=1` (after the loop a label reads the FIRST pass's own value) and
`PREDSPEC242B_RULES=24.1` (rev 24.1's reading: PCRE's carry). Ask of every switch: can the check it guards FAIL, and
does it reverse something that carries meaning? A switch that reverses nothing meaningful guards nothing.
You may import pcre2h (sys.path to the read-only rxmodel_evidence dir) and the engines from your own scripts in your
lens dir; run python with `-I -B`; never write into R/R. Earlier evidence dirs (predspec241, predspec24, lastpass,
pathimpact, rxmodel, predspec23d) are in R/R/tree too, for reference. `docs/design/rx_module.md` is a SEPARATE
proposal, not the subject.

## Who owns what is RULED (attack the manager's, respect the owner's)
- OWNER words are only what COND-FAMILY.md quotes as HIS WORDS. Everything labelled the manager's ("MINE", "THE
  MANAGER'S READING / RULING / PROPOSAL / RESTATEMENT", "THE DRAFT'S READING", "told, not asked") is NOT the owner's:
  attack it. A finding against an OWNER ruling cites it and argues (a consequence he may not have seen), or drops.
- Owner quotes: ONLY the ruling lens verifies quotes word for word against the record; other lenses cite them as the
  draft gives them without re-checking.

## Modes and the document's own rules
Every answer has a MODE: WHOLE value, SEARCHED (the first match in a subject), FIND-ALL (every match, left to right),
and the NESTED places (either side of `&`, a `label:` set, an `occurrences`/`contains` argument, a `hits(r)` list,
inside a complement, inside a lookahead, inside a loop body via a hole, inside `atomic(...)`). A property stated
without its mode is a finding. NUMERALS ARE CANONICAL (§2.2: `0|[1-9]\d*`; and THE MANAGER'S READING DICT-DOMAIN):
recompute every count and worked answer with the DOCUMENT's set rules, never an engine's lambda; in particular a
zero-padded field such as `00` or `05` is not a numeral unless the test is spelled padded (the `padded(...)` transform, §2.7 /
`padded(rx) := /0*(?:${rx})/`; check §2.2 and §2.7 for exactly what the draft says).

## Denylist (do not open, grep or list)
- docs/dev/lanes/predspec242b_report.md, predspec241_report.md, predspec24_report.md and every `*_deliver.txt`;
- docs/dev/owner.md, docs/dev/wake.md; docs/dev/dev_journal.md (the whole file: you do not need it);
  docs/dev/full_suite_ledger.md;
- EVERY file under docs/dev/reviews/ (earlier reviews of this subject; the subject cites review ids such as "review
  r40 A3": treat those as labels, do not look them up);
- every directory under /var/tmp/pcrec-pcrec/scratch/ other than THIS round's dir (in particular crit-predspec24);
- `git log` bodies beyond subject lines; other worktrees (worktrees/*); the box queue; ~/.claude (memory);
- R/.coord/ (the coordinator's notes) and every OTHER lens's directory under R.
If you plain-grep the repo, add `--exclude-dir=worktrees --exclude-dir=reviews --exclude=owner.md --exclude=wake.md
--exclude=dev_journal.md --exclude=full_suite_ledger.md --exclude='*_report.md' --exclude='*_deliver.txt'`; with
`git grep`, the pathspecs `':!docs/dev/reviews' ':!docs/dev/dev_journal.md' ':!docs/dev/lanes/*_report.md'
':!*_deliver.txt'`.

## Method rules
- Pass patterns in single quotes or via a file (shell quoting eats `\b`, `\d`). Quote the draft by § and line number
  in R/R/subject/predicates_draft.md.
- You are briefed from the SUBJECT's text: where this COMMON or your prompt and the subject disagree, test the subject.
- APPEND EACH FINDING TO YOUR FILE THE MOMENT YOU HAVE IT, one append per finding. Do not save findings for the end.

## Output format
Your findings file ALREADY EXISTS (the coordinator pre-created it with its headings); it is your OUTPUT, not an input.
Append under `## Findings`. Each finding: id `<LENS>-n`; CONFIRMED (with a repro: the program, the text, the mode, the
command or the hand derivation, observed vs expected) or SUSPECTED (what would confirm it); severity (answer / design /
doc); effort; blast radius; the draft's § and line. Then `## PROBED-AND-HELD` (what you checked that held, with case
counts). The LAST line of the file is exactly `CRITIC COMPLETE`. Then run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-predspec242 --deliver /var/tmp/pcrec-pcrec/scratch/crit-predspec242/<lens>/deliver.txt <lens>`
(substitute your lens name) and end only once it prints DONE. Final reply at most 150 words. If a Write to your file
is refused, return your findings as your FINAL REPLY instead (mark them relayed); never route around a refusal.
