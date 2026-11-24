# Lane predfix88 — review r88 applied to the predicate documents and evidence; the review filed

Lane predfix88 (opus), 2026-11-23, branch lane/predfix88 cut from lane/pred-rev28 at b63928b48. Design only: no
file under src/, cli/, lib/, memfn/, tests/ or scripts/ was touched. The subject is the record entry "2026-11-23
MANAGER — review r88 (predfold1123b): the dispositions; no owner words" (the last entry of
docs/design/plan_row_bodies/COND-FAMILY.md in this worktree), its draft
`$PCREC_TMPDIR/scratch/crit-predfold1123b/review.md`, and the manager's notice R-1 in the rulings file.

## STATE AT HANDOFF

OWED: none (every FIX-NOW applied; G3, NAMES-5 and B10 are the manager's PLAN rows, not owed by this lane).
- Rulings file: last entry applied **R-1** (2026-11-23, the owner's shorthand-is-callers; a notice, not new work).
  Applied: the open piece nested-made is NOT written (drafted uncommitted, removed before the first commit; the
  tag was never committed); list-is-label, both-uses, pair-twice-alone left as they were; the WILL BE REVERSED list is under OWNER QUESTIONS LEFT.
- Lint `python3 -I scripts/pred_doc_lint.py`: checks passed 8600, failed 0. `make -s test-plan-lint`: checks passed: 2, checks failed: 0.
- Model: `predfix88_model: 25 checks, 0 failed` (committed .out). Plants: `predfix88_sabotage: 39 plants, 0 not
  caught` (committed .out).
- Review r88 FILED: docs/dev/reviews/2026-11-23-r88-predfold1123b.md + directory (six critic texts, verify.md,
  process.md); index line in docs/dev/reviews/NOTES.md after r86's.
- Commits on lane/predfix88: b3338f679 (WIP: the documents and the model) and the delivery commit (the review, the evidence outputs, the indexes, this report).

## DISPOSITIONS APPLIED

Every FIX-NOW of the entry, by id (the review's APPLIED section has the same list, by site):

| id | where it landed |
|---|---|
| A1 | core/labels/paths/label-reference: the shorthand where no label is made on the spot, else the call's path; pointer to core/labels/ownership |
| A2 | core/operators/bindings/unspecified: one rule + a conservative overlay (the manager's reading) for a pattern position, a set, a whole count, a comparison bound; the pattern line re-grounded on the overlay; open exact-count-unspecified with (a) run ("Candidate (a)", `{${n},${n}}` with `_` is `{0,}`) and (b) the compile error in force; reading (b) "passed to any parameter" stated |
| A3 | call-forms: the VALUE-per-copy sentence (the manager's reading) grounded on the 2026-11-17 ruling's words "an exact count of n is `\d{2}\|\d{4}`" (record entry "2026-11-17 OWNER RULING — the count proposal (the rx module's count-argument) (Frank, to session 138, evening)."); lines "An array count, the value per copy" and "..., a second mention (not taken)"; lib/rx/repeat bullet; the three-bodies readings line RETIRED |
| A4 | argument-default: "Written out" limited to a body placing the argument once (line "Written out"); two-spot case has no written-out form (lines "Alone first", "Alone first, the caller's label written"); the details reading "(A3, kept)" SUPERSEDED; open both-uses named in the base |
| A5 | argument-default: the shorthand label protected, a marked reading; line "From outside" (the sugar refused); the written-out export is hand-worked, NOT run (see MANAGER READINGS TESTED) |
| A6 | label-omitted (statement: "a parameter with no default is never omitted, labels or not"; call-forms line 4 bullet, a reading); label-default's statement |
| A7 | export statement 3 and flat-read-outside: stacked labels one step; new open piece core/labels/rule/stacked-chain with four run lines |
| A8 | ownership table: every reading-backed cell marked; "the one cell" gone |
| A9 | ownership table: the forwarded column dropped, forwarding in row 5's writer text; the listed cell grounded on transform-export; modes stated; "every case" narrowed; the caller row's `A.h` refusal printed ("The caller's label, then the binding's name"); the caller's list printed ("The caller's list"). The nested-made sentence and OPEN piece: NOT written (R-1) |
| A10 | core/labels/rule: the spot a label is ON (written directly around the part), for condition 4 and line 5 (the manager's reading); closed-argument's line "A label over a wider spot". NAMES-5 PLAN |
| A11 | core/holes/option `see:` + `_` bullet; core/holes/name: `_` into a capturing group's whole-name hole is `(...)` (the manager's reading), line "A capturing group, the unspecified label" (libpcre2) |
| A12 | core_details: argument-default's `rejected:` line moved to history, marked REVERSED; five rulings lines quoting "argument-default: for me this is an error" marked REVERSED in their consequence (call-prefix, closed-argument, argument-default, two-sources, nested-scope); call-prefix's case-2 reading and closed-argument's (b) marked REVERSED; spot-read-name marked ANSWERED; core/holes/count's "`_` for the maximum" |
| A13 | padded's `needs:`/`see:`; padded_to ruled (its rulings stand, the name a placeholder), witness line "Three digits at least, two zeros" (`005`); parked pass-through-mark says padded_to; placeholders row |
| A14 | label-names-spot, two-sources, binding-prefix's pointer, label-in-argument's headline and reading (c), call-prefix case 1 tied to line 3 + line "A labelled call, through the macro's name", closed-argument's title (details heading renamed with it), export statement 2 |
| A15 | parked empty-argument, optional-arguments, compile-time-conditional, call-head-forms: live triggers |
| A16 | G4 only: core/holes/insert's per-position table (one value, several values, zero values, `_`) |
| A17 | "repeat:" to "repeat-head:" in two history lines; "the part with no label" marked the manager's consequence; his body quoted as written with `P` marked a placeholder; the door example marked his belief |
| A18 | U1 (core/labels/paths, by line 2), U6 (lib/control/when, by call-forms); U4 not written |
| B1 | SUCCESSOR: 14 models re-run, library.md served from each model's own pinned commit, nested runs routed to their own pins; 40 reds declared by their FAIL lines VERBATIM (predfix88_succ_decl.tsv); a TRACEBACK always fails (plant p34) |
| B2 | predfix84's stale `rx.repeat(rx.digit, 3)` declaration dropped; the stale test covers inherited declarations, and found one more (`[h = rx.digit] SEQ ((h: <5))?`, no longer a crash), dropped |
| B3 | TABLE reads the header, the column sentence, the rows, every read in a cell (second reads too, and the header's refused read) and the three-mode answer from core.md; plants p21-p24 |
| B4 | rule sentences pinned per check (CALLFORMS, UNSPEC, SHORTHAND, NOLABEL, STACK, SPOTON); EXPAND's written-out forms read from the documents (p4, p8, p14, p28) |
| B5 | QUOTES: each sentence pinned to its own piece (p35) |
| B6 | the `005` witness (p20), plants for LIBLINES, NULLABLE (p32), SWEEP's same-key moved arm (p30) |
| B7 | CRASH never an accepted refusal; every refusal has a key; p3 re-aimed (a later default bound by value: refused to legal), arms named in each FAIL line |
| B8 | NESTED, EXPRARG refused "not modelled"; SAMELIST fixed; messages re-worded (the caller's own label, a labelled call's name) |
| B9 | a SIGALRM unit timeout naming the check; the plant runner's per-plant timeout; a strict last-line match naming the target |
| B10 | PLAN: measured, below |

## MANAGER READINGS TESTED

Each run by the model (check in brackets); "the manager's" marks are in the documents.

- A2 overlay: `P2(_, /b/)`, `E(rx.digit, _)`, `G(_)`, `Q(_)` refused; exact-count-unspecified (a) runs `{0,}` [UNSPEC].
- A3 value per copy: `(?|\d{2,2}|\d{4,4})`, WHOLE `123` FAILS; the not-taken second-mention reading `123` HOLDS [ARRAYCOUNT].
- A5 protected: `[pub = B(A)] & (pub.A.h: ..)` refused [SHORTHAND, READINGS]. UNTESTED: that the written-out
  `[pub = B([A = A])]` exports `pub.A.h` (the model passes no caller label through a call at all; the critic's
  claim, hand-worked, marked so in the base).
- A7 stacked-chain (a): `n.d`, `m.d` legal, `n.m.d` refused; (b) as the nested form, legal [STACKCHAIN].
- A10 spot ON: `B(rx) := [p = rx SEQ /x/] SEQ /x/`: `A.h` legal; `[p = rx]` directly refused [SPOTON].
- A11 capture name: `(\d)x`, one capture, through libpcre2 [CAPNAME].
- Both uses / alone first: the shorthand reads the alone spot in either order; the written caller's label reads the
  last mention, so the two-spot case has no written-out form [SHORTHAND, READINGS].
- A labelled call's macro name refused (condition 4, a reading) [LIBLINES].

## ANSWERS CHANGED

None of the owner's. SWEEP (b63928b48 under predfold1123b's engine against today under this one): no printed
answer moved; 12 lines added, each in DOC. The engine's own answers changed only where B8 made it refuse
loudly (no printed line meets a nested body or an expression-argument read) and where SPOTON makes a body's
wider-spot label no label on the argument's spot (one new line).

## WHAT MOVED

- docs/design/predicates/core.md, core_details.md, library.md, library_details.md, parked.md, parked_details.md
  (+213/-103; one new piece, core/labels/rule/stacked-chain, with its details entry; 34 details history lines naming lane predfix88).
- docs/dev/lanes/predfix88_evidence/ (new: model, .out, sabotage .out, succ_decl.tsv, CLAUDE.md).
- docs/dev/reviews/2026-11-23-r88-predfold1123b.md + directory; docs/dev/reviews/NOTES.md (index line).
- docs/dev/history/claude_md/docs__dev__lanes.md (this report's line).

## OWNER QUESTIONS LEFT

- exact-count-unspecified (new, open): `_` into a whole count `{${n}}`: (a) `{0,}`, (b) a compile error (in force).
- stacked-chain (new, open): two public stacked labels: (a) no chain (in force), (b) chain.
- nested-made: NOT written (R-1: dissolved by shorthand-is-callers).
- Still open as they were: list-is-label (asked), both-uses, pair-twice-alone, capture-in-set, optional-entry-edges.
- No FIX-NOW was left for changing or presuming an owner answer.

WILL BE REVERSED by shorthand-is-callers (every sentence, cell, line and check I wrote or kept that makes the
caller's `A.d` a compile error because the BODY labelled, listed or closed the spot):
- core/labels/rule: line 3's gloss "A label made there is made by anyone on that use, the body included (the
  manager's reading (a))"; the new spot-ON bullet's condition-4 half.
- core/labels/ownership: row 2's labelled, listed, closed and stacked cells (`A.h` a compile error).
- core/labels/paths/closed-argument: the statement and bullets resting on condition 4 for a body's label; lines
  "The body labelling the spot", "The body listing the spot", "Closed by the macro", "Closed by a `_` part label";
  "A label over a wider spot" (its point vanishes).
- core/labels/paths/call-prefix: line "A's own d, the body labelling the spot (case 2)"; "case 2 ... the shorthand
  where the body makes no label on the spot".
- core/labels/paths/argument-default: the condition-4 bullet ("by anyone, the body included"); "Written out ...
  for a body that places the argument once" and "no written-out form" (the ruling makes `B(A)` mean `B([A = A])`
  always); the both-uses bullet and lines "Both uses", "Alone first" (the written-out reading becomes the
  shorthand's); A5's protected-shorthand bullet and "From outside" are likely affected too (the label becomes the
  caller's own).
- core/labels/paths/label-reference (A1's "where no label is made on the spot, else the call's path");
  core/labels/paths/two-sources ("where the body makes no label on the spot").
- library.md: lib/convention/argument-labels "The same read through the argument's name"; lib/control/peek,
  lib/control/atomic, lib/search/hits, lib/search/occurrences "Through the argument's name"; lib/control/when's
  `when(A, (A.h: ..))` bullet and line.
- core_details: the readings of the above that cite condition 4 for a body's label.
- predfix88_model.py: SHORTHAND's labelled/listed/closed/`_p` arms, TABLE's row-2 cells, NAMEGRID's `A.h`
  labelled/listed/closed/`_p`/stacked/two-public cells, LIBLINES' peek/atomic/hits/occurrences/identity/when arms,
  SPOTON's second arm, READINGS' both-uses rows, and the plants aimed at them (p10, p18, p29, p38).
- NOT reversed (the caller's own text labels the spot): `B([a = A]) & (A.h: ..)` and `[h = hits(..)] & (hits.hit: ..)`.

## EVIDENCE AND COMMANDS

- Lint: `python3 -I scripts/pred_doc_lint.py` (from the worktree): checks passed 8600, failed 0.
- Model: `timeout 1800 python3 -I -B docs/dev/lanes/predfix88_evidence/predfix88_model.py > predfix88_model.out`;
  last line `predfix88_model: 25 checks, 0 failed`.
- Plants: `PREDFIX88_SABOTAGE=all timeout 7200 python3 -I -B .../predfix88_model.py > predfix88_sabotage.out`; last
  line `predfix88_sabotage: 39 plants, 0 not caught`.
- B10, measured: the full run (SUCCESSOR included) 62 s wall, single process; SUCCESSOR's 14 models 58 s
  of it (predfix83 the longest at 14.3 s, preddef 11.9 s, predfix82 9.9 s, the rest under 5 s each); LIGHT (no SUCCESSOR) about 3 s; the plant run 164 s (39 plants, a subprocess each).
  Over the PLAN's 2-minute trigger: NO (62 s, under 2 min): no pool built; the PLAN's trigger did not fire.
- B1's pins (PINS8): the commit that committed each model's .out. Deviation from the entry's words "the library of
  its own start commit", for the manager: at the START commits predbound dies at load (`AssertionError:
  \`(month_numbered\(S\) := months & .*?)\``, its library reader against a body re-spelled during its own lane),
  and a traceback is never declarable; the delivery commit is the library each committed output was produced
  against (the other start-commit counts I took were with the defective runner below, so I do not quote them). A
  reply either way is asked in the final message.
- A runner defect found and fixed in this lane: inside `--succ`, both `subprocess.run` and `Popen` were patched,
  so a nested run was routed twice, got a doubled pin, failed the 4-argument test and started the FULL model, which
  recursed (48 processes before I stopped it with scripts/safekill). Now only `Popen` routes, a routed command is
  never re-routed, and a malformed `--succ` call exits loudly.
- The SUCCESSOR reasons are per red CLASS (documents moved since that model's delivery: DOC, SWEEP, MARKS, SCAN,
  AWAITS, UNMARKED, GRID, FSWEEP, CLOSEDB, PREDREF, nested SUCCESSOR; predfold1123's NULLABLE is a program of
  today's documents its SWEEP runs, held green by this model's own NULLABLE), each pinned by its full FAIL text.
- Scratch (not committed): `$PCREC_TMPDIR/scratch/predfix88/` (succ8/, dump/, light*.out, full*.out, probes).
