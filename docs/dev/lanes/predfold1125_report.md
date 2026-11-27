# Lane predfold1125: seven owner rulings and R-1..R-6 folded into the predicate documents

Branch `lane/predfold1125`, cut from `lane/pred-rev28` at 212e234e6.

- Rulings folded: drop-not, array-argument, brace-counts, map-creator, string-literals, bang-split, and-not.
- Review r109: F5, F7, F13 and F14 only.
- The rulings file: R-1 sent-label-wall, R-2 label-needs-mark, R-3 skip-past-wall, R-4 equivalence-inside,
  R-5 alone-as-middle, R-6 shorthand-outside.

This is design only. Nothing under src/, cli/, lib/, memfn/, tests/ or scripts/ changed. The record
`docs/design/plan_row_bodies/COND-FAMILY.md` was not edited.

## STATE AT HANDOFF

- Tip: the commit that carries this report, the history line and the committed `.out` files. The evidence ran at
  4750e025b (the tip adds only the `.out` files, this report and the history line).
- Rulings file `docs/dev/lanes/predfold1125_rulings.md`: six entries, R-1..R-6, all folded. Re-read before every
  commit, before each long run and before this report.
- Lint and gates:
  - `python3 -I scripts/pred_doc_lint.py`: `pred_doc_lint: checks passed 9770, failed 0`.
  - `make -s test-plan-lint`: green (checks passed: 2, checks failed: 0).
- The model's last line: `predfold1125_model: 15 checks, 0 failed`.
- Sabotage: `PASS PLANTS11: 15 plants, caught 15`.
- Nothing stopped. No STOP RULE conflict arose.
- Attribution: the brief's commit trailer named Claude Fable 5.2. The commits carry "Co-Authored-By: Claude Opus
  5.5", the model that ran this lane, following the session's attribution instruction.

OWED:
- A rulings item for each of R-1..R-6 at the merge. Their record entries ("2026-11-27 OWNER RULING —
  sent-label-wall" and its five siblings) are on lane/pred-rev28 after this lane's start commit. No
  `(record: ...)` item on this branch can cite them, so lint L4 would refuse one. Each details entry cites the
  rulings file's R-n instead and says the item is owed at the merge.

## RULINGS FOLDED

- **bang-split** (the core ruling):
  - `!` is the logical not of a test; `~` is the complement of a set or pattern; `^A` looks ahead and `!^A` is its
    negative. Lookbehind gets no operator for now.
  - Every printed `NOT` was re-spelled. Every printed `!` outside rx text and strings was classed by its operand:
    415 operators, 0 wrong (CENSUS11, r109 F14).
  - New pieces: core/patterns/lookaround/ahead and core/filters/family (r109 F13: the family table, with a DFA
    column marked as told, not ruled).
  - Rewritten pieces: complement, negation, kinds, two-valued, precedence, bindings and the conditions pieces.
  - The record has "agree drop &!".
- **drop-not**: `NOT` is no spelling. The `!peek(A)` error is gone: it is `!^A` (lib/control/peek, the line "Its
  not").
- **array-argument**:
  - Group questions take `q(@d, S)`. A condition as the argument is a compile error naming the array form.
  - `every` is named and ruled: lib/counting/every, was lib/counting/every-pass.
  - group-truth and record-in-some close. The record reading is now a reading, dissolved.
  - The occurs counters are re-spelled.
- **brace-counts**: new core/patterns/quantifiers/braces. `x{a,b}`, `{a}`, `{a,}`, `{,b}`, lazy and possessive;
  white space is layout; `x{}` and `x{,}` are compile errors naming `x*`.
- **string-literals**: new core/patterns/strings. A string has no pattern operators. Escapes are `\\`, both quotes,
  `\n`, `\r`, `\t` and `\x{..}`; `""` is the empty text; adjacent strings are an error naming `SEQ`.
- **map-creator**: core/modules/map was restated, and core/modules/map/access is new. `m.a` must exist; `m[key]` is
  a search in the key's order; nothing found is the never-matching rx. A missing label or a numeral label is a
  compile error.
- **and-not**: `A & ~B` replaces `A & !B` everywhere printed.
- **r109 F5**: every refusal names the form to write (ERRSWEEP11's MSG11 rows, 17 forms, over 76 compile-error lines).
- **r109 F7**: core/filters/negation/effects names `!` and `~`.
- **R-1 sent-label-wall**: RULED candidate (a), the compile error. Candidate (b) goes to the details as rejected.
  His words are quoted from R-1, and his side note was not applied, as told.
- **R-2 label-needs-mark**: core/operators/bindings/label-variables gains a bullet and two compile-error lines,
  `R(x, A)` and the group-name form `A(x)`. Each line names the missing mark.
- **R-3 skip-past-wall**: RULED (a). The first three lines are kept. Candidate (b)'s three lines and the middle road
  go to the details as rejected. core/labels/rule/paths' Readings bullet now says "His ruling" for that clause.
- **R-4 equivalence-inside**: RULED (a). His sentence stays in core/labels/rule/paths as the picture from outside.
  Candidate (b) goes to the details as rejected.
- **R-5 alone-as-middle**: RULED with the statement as re-asked. Inside its binding a part used alone is a label
  of its own name: a start or a middle step (`n.Q.d`), never skipped.
  - The line "A part used alone as a middle, inside" is now legal, with `Q.d`'s answers (RUN, and the new line "Its
    own start, alike").
  - The line "Through the part used alone, skipped" is now a compile error naming `n.Q.d` (the message names
    `n.P.d` or `n.Q.d`, both routes).
  - Two lines added: used twice, not a step; and `X.Q.d` from outside, rule 6.
  - core/labels/rule/paths' reading "an implicit label is never a middle" is replaced by his ruling.
  - core/labels/export statement 2 gains the middle step and "never skipped". Rule 6's wording (his) was checked
    and stands.
  - Every printed program that skipped through a part used alone was found by SWEEP11 under the patched walker.
    Besides the piece's own line there are three: core/patterns/alternation, core/patterns/atomic and
    core/operators/precedence, `[ab = (B | A)] & (ab.l: <20)` and kin. Each is re-spelled with written labels
    (`[ab = ([b = B] | [a = A])]`), which rule 4 still skips. Their answers are unchanged (RESPELL11).
  - The model: predfix90's path walker, its message and the grid evaluator are patched as DECLARED text
    replacements (R5PATCH11), under X11 only, so the control still runs the starting rules. GRID's 16 undecided
    alone-as-middle cells are now decided "refused". All 3050 cells agree with the evaluator; sabotage q15 is
    caught.
- **R-6 shorthand-outside**: RULED (a). Text and lines are as they read. "The manager's reading (b)" there and in
  core/labels/paths/argument-default becomes his ruling. Candidate (b) goes to the details as rejected.
- The principle piece core/principles/all-dfa records his stated goal and his request for a DFA category. It is
  STATED, NOT RULED.

## MANAGER READINGS TESTED

READINGS11 tested 49 readings: 35 SUPPORTED, 0 NOT SUPPORTED, 14 UNTESTABLE, each with its reason in the `.out`.
The ones that matter:

- `!(h: S)` equals `(h ?: ~S)`, and `!(h ?: S)` equals `(h: ~S)`: 0 of 11 states differ. The control parts on the
  absent state.
- A record stays a product of sets: `!(a: S, b: T)` = `(a ?: ~S) | (b ?: ~T)`. 0 of 121 states differ, against a
  direct python reference, because the engine cannot run a `|` of conditions.
- `~A & B` is `(~A) & B`. `~B & ~C` is `~(B | C)` as filters. `not_seven := ~seven` carries over. All agree on
  every text.
- One `when` body serves a bare test and a lookahead test, checked against `\d\d\d|(?!\d)\w` and
  `(?=\d)\d\d|(?!\d)\w`. `when(!x, z)` on a bare pattern is an error naming `!^`.
- array-argument (c): the set may read a label as it stands. 0 differences against a direct reading: the last pass's
  m compared against every h.
- Group answers, GROUP11: `!some` = `occurs.none`, and `every` = `occurs.none(@d, ~S)`. Each agrees with a direct
  reading over 364 texts.
- Answer readings, each against python `re`: brace counts (BRACES), strings (STRINGS), map selection in the key's
  order (MAP11), and the empty selection as the never-matching rx.
- A limit, by construction: the readings that a form is a compile error are implemented by TR11 itself. Some
  examples: `\x41`, a raw line end in a string, `_` inside braces, braces on a condition, `@0`, label-needs-mark.
  Those runs show that the front end and the printed lines agree. They do not show the reading independently. Only
  the answer readings above have an independent oracle.
- UNTESTABLE, each for a stated reason: the spelling placeholders, a match-time count `x{$n}`, the accessor on a
  non-map pattern, `.index` on a selection, position 0, the string encoding question, the weak `i`, and a string as
  a name.
- Dropped as untestable rather than claimed: the `~~B` claim. The engine does not parse `~~`.
- R-5's check, as asked: the predfix90 engine answers `X.Q.d` from OUTSIDE as legal for X := `[n = (P SEQ Q)]`.
  This is a MODEL DEFECT, confirmed by run (READINGS11: legal under the starting rules). Its cause: predfix90's
  walker raised "undecided" on any step naming a part used alone, and handed the read to the loaded older engine,
  which answered it. core/labels/export statement 3 says such a part exports nothing. The patched walker refuses
  the read by rule 6, and `X.n.Q.d` alike. Kept as before: a step naming a part that is directly a label's whole
  content is still handed off as undecided (the labelled case, unchanged).

## ANSWERS CHANGED

- `!peek(A)`: before, a compile error; now legal, it is `!^A` (drop-not and bang-split).
- `R(x, A)` with R(l, v) := `/${[l = v]}xx/`: before, legal, writing a label literally named `l` (`R.l.h` legal);
  now a compile error at the definition (R-2). The same holds for the group-name form `(?<:${l}>...)` with an
  unmarked `l`. No other printed program is refused by the new rule (SWEEP11). `A2(l = _:)` is a marked parameter
  and still runs.
- `when(!x, z)` on a bare pattern: before, open (not-test); now a compile error naming `!^x` (bang-split line 4).
- `[n = (P SEQ Q)] & (n.d: <5)`: before, legal, Q's `d`; now a compile error naming `n.Q.d` (R-5).
  `[n = (P SEQ Q)] & (n.Q.d: <5)`: before, a compile error; now legal, with `Q.d`'s answers (R-5).
  `X.Q.d` from outside: before, legal in the model (the defect above); now a compile error (rule 6).
- Every `!` on a set or pattern and every `NOT` is now a compile error naming its form. The answers under the new
  spelling are unchanged.
- No printed answer moved otherwise. SWEEP11 ran the starting commit's 336 keys under predfix90's engine against
  today's 396 lines, matched by the translated program:
  - moved 0, gone 0;
  - 11 re-spellings declared, each with equal printed answers;
  - 3 lines dropped by a ruling, declared (two by R-3, one by R-5, which is now a compile-error line);
  - 36 added;
  - 61 non-same lines inherited from the control with the same key and status, plus 2 details records in the
    spelling of their run.

## WHAT MOVED

- `was: lib/counting/every-pass` (2026-11-27): now lib/counting/every, named `every` by array-argument.
- Closed by a ruling:
  - core/model/table/group-truth;
  - core/labels/rule/sent-label-wall, skip-past-wall, equivalence-inside and alone-as-middle;
  - core/labels/paths/shorthand-outside;
  - lib/control/when-test/not (now `` `!` on a bare pattern test ``).
- core/conditions/form/record-in-some: an open piece becomes a reading.
- lib/control/peek: ruled becomes `open peek-name`, because no ruled text needs the name now.
- New in core.md: core/principles/all-dfa, core/patterns/strings, core/patterns/quantifiers/braces,
  core/patterns/lookaround/ahead, core/filters/family, core/modules/map/access.
- New parked pieces: parked/ideas/export-two-labels, select-by-position, triple-quote, non-atomic-ahead and
  in-place-complement.
- Restated: the pieces listed under RULINGS FOLDED. Each changed piece's date is now 2026-11-25 or 2026-11-27.

## DRAFT READINGS ADDED

All of these are marked "the manager's reading" in their pieces, for the next critic round (r111):

- `^A` as an `&` operand is operand-context's compile error. `^A` passes A's labels on, and `!^A` passes none.
- `^A` is atomic, as PCRE's lookahead is.
- `!^A` cannot be written `^~A`.
- `!c`'s DFA category is "as c"; `^A`'s is "yes".
- The map accessor:
  - it works on any pattern with labels;
  - a bare name in the brackets is a binding's value;
  - a one-name result is not renumbered;
  - `m[0]` is the whole rx;
  - a name on an unlabelled array finds nothing;
  - the same result twice matches as once;
  - an empty result draws the warning.
- Strings: `\x{..}` gives a code point. Whether that is a character or a byte is the encoding question.
- `_` inside braces is a compile error for now.
- peek, candidate (a): keep `peek` as the named form, by the `rx.repeat` parallel. This is the lean.
- R-2's second sentence: the group-name form is the same error.

## OWNER QUESTIONS LEFT

There are 10 open pieces. Before the fold there were 18 in core.md and library.md: nine closed and one opened.

- lib/builtin/export (export-choice).
- lib/modifiers/any-case (any-case-body).
- lib/control/peek (peek-name): keep `peek(A)` beside `^A`, or keep `^A` alone. This is new, and it carries the
  question of which peek forms the library provides.
- core/labels/rule/group-node.
- core/labels/numbers/in-loop.
- core/conditions/form/optional-edges, optional-general.
- core/conditions/quantified/group.
- core/modules/default-set/members.
- core/modules/positional.

Not pieces, but raised in the text:

- Whether `!A` on a pattern may later mean `(?!A)`. Today it is an error naming `~` and `!^`.
- A lookbehind spelling ("no operator for now").
- The map's open edges: a key read at match time, brackets on a module, labels under a join, and the two `.index`
  edges.

A PCRE2 source fact was not needed. `^A`'s atomicity is a draft reading resting on PCRE's documented lookahead
behaviour. No run tests it.

Noted for the manager: `core/holes/insert` has no lookaround row in the current text.

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/predfold1125_evidence/`:
  - `predfold1125_model.py`, with its CLAUDE.md;
  - `predfold1125_model.out`, the full run at the tip, SUCCESSOR11 included;
  - `predfold1125_sabotage.out`;
  - `predfold1125_succ_decl.tsv`: 61 declared reds over 17 models, each by predfix90's line-number-free key. Each
    reason is in the file: either carried from predfix90 with the key unchanged, or the key moved with this fold's
    re-spelling and with R-5/R-6. There are no tracebacks.
- The front end TR11 and the lowering RX11 are inlined in the model. The model builds every regex mechanically from
  the body text and from the `when` body read from library.md.
- Every new printed line, 43 of them, came from a RUN: SPECLINES produced each line and DOC11 found it verbatim in
  its piece.
- Commands:
  - `timeout 5400 python3 -I -B docs/dev/lanes/predfold1125_evidence/predfold1125_model.py`, the full run, about
    75 s on this box, SUCCESSOR11 71 s of it.
  - `PREDFOLD1125_LIGHT=1 ...` skips SUCCESSOR11.
  - `PREDFOLD1125_SUCCDUMP=DIR PREDFOLD1125_SABOTAGE=all PREDFOLD1125_LIGHT=1 ...` runs the 15 plants. q12 reads
    the dumped successor runs.
  - `(cd worktrees/predfold1125 && python3 -I scripts/pred_doc_lint.py)`.
  - `make -s test-plan-lint`.
  - `scripts/lanecheck predfold1125`.
- Scratch helpers (not evidence) are under `/var/tmp/pcrec-pcrec/scratch/predfold1125/`:
  - `gen.py`, `gen11.py` and `specs.txt` wrote the printed lines;
  - `respell.py` did the code-span re-spelling;
  - `details.py` did the details entries.
