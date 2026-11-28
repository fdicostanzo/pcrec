# Lane predfold1128: five owner rulings folded; the strong lean no-path-through-argument applied and marked (DESIGN)

Branch lane/predfold1128, cut from lane/pred-rev28 at 8e7cca4a9. Design only: nothing under src/, cli/, lib/, memfn/,
tests/ or scripts/ was edited. The rulings are the record entries of 2026-11-27 in
docs/design/plan_row_bodies/COND-FAMILY.md (not edited by this lane): "OWNER RULING — gate-beside-direct: "legal"",
"OWNER RULING — carve-out-reading: "agree with lean"", "OWNER RULING — caller-label-export: "agree first read. If
they didn't want to export use _a label."", "OWNER RULING — named-list-use: "agree use it."; ...", "OWNER RULING —
param-reference: "yes all four"; ...", "OWNER, a STRONG LEAN on no-path-through-argument" and "OWNER, a DIRECTION:
"Let's stop questions for tonight. Fold now"". The study it rests on is docs/dev/lanes/predarg_report.md.

## STATE AT HANDOFF

- OWED: none.
- The rulings file `docs/dev/lanes/predfold1128_rulings.md` was re-read before each commit, before each run over two
  minutes and before this report. It stayed empty: no entry was applied (last entry applied: none).
- Branch tip: the commit carrying this report.
- pred_doc_lint: `@@LINT@@`. `make -s test-plan-lint`: green.
- Model: `@@MODEL@@` (full, SUCCESSOR128 included); sabotage: `@@PLANTS@@` (one plant per check).
- Premise, before any edit: predfix112 full at 8e7cca4a9: `predfix112_model: 11 checks, 0 failed`.
- Printed lines moved: 10 (8 three-mode lines to compile errors, 1 compile error to legal, 1 error message). Marker
  sites: 38 (core.md 35, library.md 3; MARK128 counts them).

## RULINGS FOLDED

- **gate-beside-direct** ("legal"). core/labels/rule/one-path: the line "A direct target beside a gate" (`[n = (P
  SEQ /,(?<d>\d)/)] & (n.d: <5)`, n's own `d`) and the bullet "Nothing skipped" lose their reading mark; the
  details entry's reading marked RULED, a rulings item. Answers unchanged (RULE128, SWEEP128).
- **carve-out-reading** ("agree with lean": the door). New ruled piece core/labels/rule/argument-door, the statement
  as asked: "a body's export list opens a door through the argument's place. A path may pass it, and one-path and
  body-own-name apply to what is reached as they do anywhere else." Lines: "One argument sets it" (`W.h`), "The
  body's own beside the list" (`Bo.d`, the body's own `d`), "His remedy" (his observation, the same `Bo` with
  `[(=, _ = d) = rx]`, the same answers: READINGS128), "Under the body's label" (`B2.p.h`). The kinds table's place
  row: "passed only through a list on it".
- **caller-label-export** ("agree first read. If they didn't want to export use _a label."). New ruled piece
  core/labels/rule/caller-label: `Y.a.h` legal (`3xx!` HOLDS), `Y.c.a.h` a compile error, `[_a = A]` keeps the
  label in (a compile error from outside). The kinds table's caller-label row's outside and exported cells.
- **named-list-use** ("agree use it."). New ruled piece core/labels/export/named-list: a named list requires the
  argument to have the label; missing is an error at the CALL; set twice is legal and reads the last; through a
  forwarding macro the error names the forwarding place; a definition that can never be satisfied is an error where
  it is written; each message names the label and the list. "A named list on a spot" moves from a definition error
  to legal (below). core/labels/export/arguments' table row points at it.
- **param-reference** ("yes all four"). New ruled pieces core/operators/bindings/reference (lines 1, 2, 4: declared,
  enforced in the body, nothing inferred) and core/operators/bindings/reference-call (line 3, at the call). His
  weekday example: legal as a filter after both pieces (`wdname SEQ " " SEQ mdy & day_named(wdname, mdy)`), and
  the error "a read before the match" at the weekday's own spot; python's `datetime` is SAID to be a stand-in for the
  planned `weekday_of`. Each error of line 3 is a `modes: a compile error` line (a pattern written in place, a
  missing label, a name used twice, a read before the match). "Whether the CALL also carries a mark" is listed as
  not decided. label-kinds is revised for users (the reference kind by a declared list in the head);
  bound-condition and macro-types say what this settles (a declared reference names its target in the head;
  meaning (ii)'s declared form) and close nothing further.
- **The strong lean no-path-through-argument**, applied and MARKED at every site with "(the owner's strong lean,
  entailed by carve-out-reading and caller-label-export; to be confirmed)". Its one home piece is
  core/labels/rule/argument-place (open under its slug). The withdrawn clause is printed nowhere (STALE128 searches
  all six files).
- **The manager's call hits-through-hit**: the provided bodies of `hits` and `occurrences` carry the list under
  `hit` (`(?<:hit>${[(=) = r]})`, `(?<:hit>${[(=) = x]})`), so `hits.hit.g` and `occurrences.hit.n` stay legal with
  their answers (READINGS128 runs the old and new bodies). Recorded as the manager's call in
  lib/convention/argument-labels, lib/search/hits and lib/search/occurrences, and their details entries.

## MANAGER READINGS TESTED

Each RUN (READINGS128 and RULE128; output in predfold1128_model.out):
- stacked-chain: `X.c.h` re-spelled by Y labelling the argument, `X.a.h`, the same answers: SUPPORTED.
- shorthand-outside "the contrast stands": NOT SUPPORTED as written. `[pub = B([A = A])] & (pub.A.h: <5)` is an error
  by caller-label-export's asked words ("only the path through the call's own label"). It holds in a moved form:
  from a binding that uses the caller, `X & (X.A.h: <5)` with X := `[pub = B([A = A])] SEQ "!"` is legal and the
  shorthand `[pub = B(A)]` is refused. Printed that way in core/labels/paths/shorthand-outside.
- carve-out-reading's remedy: `[(=, _ = d) = rx]` gives the same answers as `[(=) = rx]` for `Bo.d`: SUPPORTED (the
  door reads the body's own anyway; the remedy makes it explicit).
- hits-through-hit: the list under `hit` keeps `hits.hit.g` legal with its old answers; without it the read is
  refused: SUPPORTED.
- param-reference "at the point of the call": the filter over the whole legal, the call at the weekday's own spot
  "a read before the match": SUPPORTED.
- param-reference example 3 (`checked(B) := B & (B.year: < 2100)`): NOT FOLDED (OWNER QUESTIONS LEFT).

## ANSWERS CHANGED

Each old line is quoted from 8e7cca4a9; each new one is RUN (SWEEP128 declares the seven gone keys, ERRSWEEP128 and
SPECLINES128 run the new lines). All in core.md.
1. core/labels/rule/paths, "Through a call, the middle label skipped" (`B(A) & (B.h: <5)`): old WHOLE `3xx` HOLDS,
   `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8]; new: a compile error (read
   `A.h`, the same answers, core/labels/rule/argument-place). Marked.
2. core/labels/rule/stacked-chain, `X & (X.c.h: <5)`: old WHOLE `3xx!;` HOLDS, `7xx!;` FAILS / ... [`3xx!;`@0,
   `4xx!;`@12]; new: a compile error; added `X & (X.a.h: <5)` with Y := `[c = B([a = A])] SEQ "!"`, the old answers.
3. core/labels/rule/alone-as-middle, `[n = (P SEQ B(Q))] & (n.B.p.d: <5)`: old WHOLE `7,3xx` HOLDS, `3,7xx` FAILS /
   ... [`7,3xx`@0, `4,1xx`@12]; new: a compile error; added `(Q.d: <5)`, the old answers.
4. core/labels/rule/alone-as-middle, "A macro call used alone, skipped" (`n.d`): the message only, old "write `n.B.d`
   or `n.P.d`", new "write `n.P.d`, or `Q.d` for Q's".
5. core/labels/export/named-list (moved from core/labels/export/arguments), "A named list on a spot" (`N(A) & (N.h:
   <5)`): old a compile error ("a parameter exports nothing the definition can see"); new WHOLE `3` HOLDS, `7` FAILS
   / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4].
6. core/labels/paths/closed-argument, "Through the body's path" (`B(A) & (B.p.d: <5)`): old WHOLE `7-3` FAILS, `3-7`
   HOLDS, `3-3` HOLDS / ... [`3-7`@4, `1-2`@8]; new: a compile error naming `A.d`. Marked.
7. core/labels/paths/argument-default, "From outside, written out" (`[pub = B([A = A])] & (pub.A.h: <5)`): old WHOLE
   `3xx` HOLDS / ... [`3xx`@0, `4xx`@8]; new: a compile error. Marked.
8. core/labels/paths/argument-default, "Through a part label in the body" (`B(A) & (B.dd.d: <100)`): old WHOLE
   `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / ... [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17]; new: a compile error
   (read `A.d`). Marked.
9. core/labels/paths/shorthand-outside, "From outside, written out" (the same `pub.A.h`): as 7; two lines added
   (`X.A.h` written legal, the shorthand refused). Marked.
10. core/holes/bare-condition/nested-scope, "Example 1, the spot labelled" (`C := B(A) & (B.dd.d: <100)`): as 8; a
   tenth moved line the study's census missed (its key carries `C :=`). Marked.
- Lines 1-3 and 6-10 are the eight three-mode lines moved to compile errors; the study's nine were these less
  nested-scope's, plus `hits.hit.g` and `occurrences.hit.n`, which the manager's call keeps legal.
- Marker sites: 38 (core.md 35, library.md 3, parked.md 0).

## WHAT MOVED

- New pieces (9): core/labels/rule/argument-place (open no-path-through-argument), argument-door (ruled),
  caller-label (ruled), list-over-label (open), forwarded-place (open), sent-over-body-label (open);
  core/labels/export/named-list (ruled); core/operators/bindings/reference and reference-call (ruled). Each has
  a details entry in order (L3).
- Edited pieces: core/labels/rule/paths, one-path, stacked-chain, alone-as-middle, kinds (the place row, the
  shorthand row corrected (study problem 11), the caller-label row, a bullet); core/labels/ownership (two cells, a
  bullet); core/labels/export (statement 3); export/arguments; paths/call-prefix, closed-argument, argument-default,
  shorthand-outside; core/holes/labels, bare-condition/nested-scope, bound-condition;
  core/operators/bindings/label-kinds, macro-types; lib/convention/argument-labels, lib/search/occurrences,
  lib/search/hits. Each details entry has a rulings item and a history line with the old text verbatim.
- The walker's refusal message names the rule and the ways in (study problem 10): "the path passes B's argument
  place, which no list opens: read `A.h`, label the argument, or list it in the body" (MSG128; the wording a
  reading).
- The withdrawn clause was removed from a details rulings item and a rejected item (both re-worded).

## DRAFT READINGS ADDED

Each printed as a MARKED reading under the study's lean, both readings RUN (OPEN128):
- **sent-over-body-label** (lean legal): `Rs(x:, A) & (x.h: <5)`, Rs(l:, v) := `/${[l = [p = v]]}xx/`: WHOLE `3xx`
  HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8]; the other reading
  (the path from `x` passes the body's `p` and the place) a compile error.
- **forwarded-place** (lean legal): `Mx(A) & (Mx.h: <5)`, Mx(r) := `/<${[(=) = L2(r)]}>/`, L2(x) := `/${[(=) = x]}/`:
  WHOLE `<3>` HOLDS, `<7>` FAILS / SEARCHED `<7> <3>` `<3>`@4 / FIND-ALL `<3> <7> <4>` [`<3>`@0, `<4>`@8]; the other
  reading (only Mx's own list on its own place counts) a compile error.
- **list-over-label** (lean error): `B1(A) & (B1.h: <5)`, B1(rx) := `/${[(=) = [p = rx]]}xx/`: a compile error; the
  other reading (any list above the place opens it) legal, WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx`
  `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8]; `B1.p` legal under both.

## OWNER QUESTIONS LEFT

- **no-path-through-argument**: confirm or lift the strong lean. It is applied at 38 marked sites, and its home is
  core/labels/rule/argument-place.
- **sent-over-body-label**, **forwarded-place**, **list-over-label**: as above, each printed under the lean and
  marked.
- **reference-example-checked** (STOP RULE): the manager's param-reference example 3, `checked(B) := B & (B.year: <
  2100)`, places a plain parameter and reads its label through the parameter's name. Line 4's asked words ("A
  plain parameter that the body places and then reads stays legal, as today") read it as legal; core/labels/paths
  ("a parameter's label inside the body is not nameable") makes it an error "as today". Both readings RUN: the model
  refuses it ("checked names a label it does not hold"); the reading "legal" answers as `isodate & (isodate.year: <
  2100)`, WHOLE `2024-02-29` HOLDS, `2150-01-01` FAILS (READINGS128 prints both). Not folded.
- **call-mark** (listed as not decided, his words "yes all four" leave it open): whether the CALL of a reference
  parameter also carries a mark.

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/predfold1128_evidence/` (its CLAUDE.md): `predfold1128_model.py`, `predfold1128_model.out`,
  `predfold1128_sabotage.out`, `predfold1128_succ_decl.tsv`.
- Full: `(cd worktrees/predfold1128 && PREDFOLD1128_SUCCDIR=$PCREC_TMPDIR/scratch/predfold1128/<empty dir> timeout
  6000 python3 -I -B docs/dev/lanes/predfold1128_evidence/predfold1128_model.py)`.
- Sabotage: the same with `PREDFOLD1128_SABOTAGE=all PREDFOLD1128_READDUMP=1` (each plant in a LIGHT subprocess).
- SUCCESSOR128: @@SUCC@@
- Lint: `python3 scripts/pred_doc_lint.py`; `make -s test-plan-lint`.
- Only python3 `-I` with `re` and `datetime` (the weekday stand-in), one process per model, every run under
  `timeout`. No make but `make -s test-plan-lint`, no box queue, no suite, no timing.
