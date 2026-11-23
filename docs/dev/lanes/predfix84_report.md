# Lane predfix84 — review r84's ruled dispositions applied; the successor evidence model; r84 filed

Branch `lane/predfix84`, cut from `lane/pred-rev28` at 2d6270c10; `lane/pred-rev28` NOT merged in (the rulings file
named no R-n). Design only: the six predicate documents `docs/design/predicates/{core,library,parked}{,_details}.md`,
the filed review `docs/dev/reviews/2026-11-22-r84-predspot1122.md` (+ dir, + its `NOTES.md` line), and the evidence
in `docs/dev/lanes/predfix84_evidence/`. Nothing under src/, cli/, lib/, memfn/, tests/, scripts/ touched; the record,
plan.md, decisions.md, known_issues.md and docs/dev/pred/ were not edited; no D/K ids, no plan-row edits. The task
list: the record entry "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23
rulings in hand; no owner words".

## STATE AT HANDOFF

- STATE: done.
OWED: none
- Branch tip: the commit carrying this report (WIP predecessors 59ee9a634, f96f20aca, dbf1d6df3, and the output
  commit after them).
- Rulings file `docs/dev/lanes/predfix84_rulings.md`: EMPTY at every checkpoint (before each commit, before each
  run over two minutes, before this report). Last R-n applied: none.
- `pred_doc_lint: checks passed 7270, failed 0`; `make -s test-plan-lint` clean.
- The model: `predfix84_model: 37 checks, 0 failed`; predfix84_sabotage: 43 plants, 0 not caught (each plant turned its target check FAIL, no traceback).
- Stopped on: nothing. No disposition contradicted the record's owner words or a run.

## DISPOSITIONS APPLIED

Per id, where it landed: the filed review's closing section APPLIED (same text). In short:

- Documents: A1, A2, A3, A5, A6 (1)-(5), A8, C1, C2, C6, C7, C8, D1, D3, D4, D5, D6, D7, D8 (e), G2's doc fix
  (parked/ideas/severity-table: its trigger fired), G4 (the parked piece parked/ideas/pass-through-mark).
- The successor evidence model: B1 (RENAME, a rename drill in GRID: 88 cells, moved 0), B2 (PARTPATH), B3 (ARGREF),
  B4 (UPTO), B5 (GRID and FLAGGRID arms that can fail; an UNDECIDED arm each, 4 cells, each naming its open slug in
  its piece), B7 (SWEEP and FSWEEP fail on any non-same status not declared; history and `rejected:` lines
  skipped). New checks for document fixes: LISTATOM (D3), PREFIXIN (A5, libpcre2 cross-check), CONTAINS (D5,
  libpcre2 cross-check), SPOTNAME (spot-read-name), OPENFLAGS (the three open flag slugs), PATFLAGS (A6 (4)).
- Open, no answer applied, each with its slug and each candidate's run line where the candidates part:
  option-hole-explicit (core/patterns/flags), options-reach-constants and options-position (lib/builtin/options),
  spot-read-name (core/labels/paths/closed-argument; candidate (a) is the existing line "Visible through the call").
- Not applied, as ruled: B6, D8 except (e), G1, G2's table, G3 (PLAN/NOTED); A4, A7, C3, C4's mark, C5, D2
  (OVERTAKEN, the fold lane's).
- A correction made in passing: two details lines this lane wrote first called "At a hole, only an explicit `i` or
  `-i` is inherited." "his hole-flags words"; the record shows it is part 2 of the statement put to him, which he
  answered "yes to all". The details now say so (core_details core/patterns/flags readings and rejected). The
  filed review keeps the record's own wording of the manager's ruling.

## ANSWERS CHANGED

None. Checked: SWEEP over every printed three-mode line (`PASS SWEEP: 216 printed lines now ... 212 at the
starting commit under predspot's engine; ... answers moved 0 (listed: none); gone 0; added 4`) and FSWEEP over every
flag line (`9 flag lines at the starting commit (... 9 stand, 0 changed); 16 flag lines now ...; bad 0`).
ANSWERS_CHANGED84 and F_CHANGED are empty in the model.

## WHAT MOVED

- Printed lines ADDED (each formatted by the model, DOC finds each verbatim): export-list "Through a call that
  passes its argument's labels on"; prefix-in "S's labels, through the call"; contains "The last occurrence";
  closed-argument "Candidate (b) of spot-read-name"; in-filter "Bound in a library" and "Written in the hole";
  pattern "Under another flag"; core/patterns/flags "Candidate (a)/(b) of option-hole-explicit"; options
  "Candidate (a)/(b) of options-reach-constants" (twice: a string constant, an argument literal a library body
  places) and "Candidate (a)/(b) of options-position" ((b) a compile error); binding-prefix "Counted in the text".
- A legality moved by a reading, no match: `prefix_in`'s S now takes the list (A5): `prefix_in.a` is readable.
- The evidence engine, not the documents: a binding named like a macro's parameter no longer captures it (B1);
  `[b = B(A)] & (b.p.h: ..)` is legal as `B.p.h` is (B2); `B(A & (h: "3"))` is a compile error (B3); an argument
  or macro body written before `@options` keeps the earlier options (B4).
- SUCCESSOR: predspot's model is now red on SWEEP (prefix_in's new line), FSWEEP (the candidate and `pattern($x)`
  lines its flag engine does not read) and SUCCESSOR (predcall's SCAN counts 312 spans, was 309, the three this
  lane's lines add; same 33 flagged): each declared with the digest of its FAIL line and the check that supersedes it.

## LEFT FOR THE FOLD LANE

Sentences met that the 2026-11-22-late and 2026-11-23 rulings (argument-label and its companions) will move; not
edited here:

- core.md core/labels/paths/closed-argument: "- \"Visible through the call\", settled strictly by argument-default
  (ruled): only where the body labels the spot" and "- It settles call-prefix case 2: legal, under this condition."
  (C4); core/labels/paths/argument-default "it settles call-prefix case 2 and closed-argument's \"visible through
  the call\" in ..." (C4).
- library.md lib/search/occurrences "caller's own text and stays a capture (`occurrences(/(?<n>\d+)/)`: n)" and
  lib/search/hits "Bare, the caller's own: modes: a compile error ..." (C5; capture-export moves "stays a capture").
- core.md core/holes/labels "At the top nothing is outside: the program's own text and the parts it uses alone are
  both visible to it" and core_details core/holes/labels' r83 D8 reading (D2).
- library.md lib/rx/repeat "a part label written on the argument (`rx.repeat([a = rx.digit], min = 1)`, then `a`)
  labels a template: a compile error (the manager's reading (a), ...)" (A4: legal again).
- library_details lib/convention/argument-labels "what an argument exports (the lane's reading): ..." (A7: moves into
  core/labels/export).
- core_details core/labels/paths/call-prefix reading "(3) an argument written in place is the caller's own text,
  read bare" and case 2's RULED reading (C2 marked them; C5/D2 rewrite them).
- Revision words not named by C8 and so left: core.md label-reference "It revises core/labels/export/
  flat-read-outside and hole-export ... and his example 1 ..." and one-use-read "... is revised by it" (both on
  argument-default's ground).
- Readings (a) and (b) of argument-default: NOT withdrawn here (the fold lane's, C3).

## OWNER QUESTIONS LEFT

- option-hole-explicit: is an `i` written by an option hole (`/(?${o})${w}/`, o := `"i"`) explicit? (a) explicit:
  `AB` HOLDS; (b) weak: `AB` FAILS (core/patterns/flags).
- options-reach-constants: do program options reach a string constant and an argument literal a library body
  places? (a) yes: `"ab"` under `@options(i)` HOLDS on `AB`, `atomic(/a.b/)` under `@options(s)` HOLDS on `a\nb`;
  (b) no: both FAIL (lib/builtin/options).
- options-position: may `@options` stand below a binding, appear twice, turn a flag off? (a) from the statement
  on: `/x${a}y/` with a bound above `@options(s)` FAILS on `x\ny`; (b) top only: a compile error
  (lib/builtin/options).
- spot-read-name: through a body that labels the spot, `A.d` (a, legal) or only `B.p.d` (b, `A.d` a compile error)
  (core/labels/paths/closed-argument).
- A3's consequence, to be told to the owner (the manager's ruling): a library literal's meaning is no longer
  readable off the literal alone (its file's program options condition it).

## EVIDENCE AND COMMANDS

W = /home/pcrec/projects/pcrec/worktrees/predfix84.

- `timeout 3600 python3 -I -B W/docs/dev/lanes/predfix84_evidence/predfix84_model.py` → `predfix84_model.out`;
  last line `predfix84_model: 37 checks, 0 failed`.
- `PREDFIX84_SABOTAGE=all timeout 14400 python3 -I -B .../predfix84_model.py` → `predfix84_sabotage.out`; last line
  `predfix84_sabotage: 43 plants, 0 not caught (each plant turned its target check FAIL, no traceback)`.
- `(cd W && timeout 300 python3 -I scripts/pred_doc_lint.py)` → `pred_doc_lint: checks passed 7270, failed 0`.
- `(cd W && make -s test-plan-lint)` → green (`checks failed: 0`, rc 0).
- libpcre2 (run through ctypes in the model, never read): `^(?:(?<a>ab)c|xy)(?<=^(?s:.){3})(?s:.*)$` on `abcz`
  gives a = `ab` (PREFIXIN); `^(?s:.*)(?:(?<n>\d))(?s:.*)$` on `a1b2` gives n = `2` (CONTAINS).
- Runs were single-process under `timeout`; nothing queued; no timing.
