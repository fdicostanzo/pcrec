# Lane preddef — default-export folded (a part used alone is protected); export-list folded (R-1, R-2)

Branch `lane/preddef`, cut from `lane/pred-rev28` at 0050e019a; `lane/pred-rev28` merged in once (for R-1/R-2's record
entries). Design only: documents `docs/design/predicates/{core,library}{,_details}.md` and the evidence in
`docs/dev/lanes/preddef_evidence/`. Nothing under src/, cli/, lib/, memfn/, tests/, scripts/ touched; the record
was not edited.

## STATE AT HANDOFF

- Branch tip: the commit carrying this report (its WIP predecessors 9f9ebd437, ed37dc43a).
- Rulings file `docs/dev/lanes/preddef_rulings.md`: last entry applied **R-2** (re-read before each commit and
  before this report; no R-3).
- Lint: `timeout 120 python3 -I scripts/pred_doc_lint.py` → `checks passed 6628, failed 0`; `make -s
  test-plan-lint` clean.
- Model: `timeout 900 python3 -I -B docs/dev/lanes/preddef_evidence/preddef_model.py` → `preddef_model: 22 checks,
  0 failed`; 22 plants each caught by their target check, none by traceback (`preddef_sabotage.out`).
- Nothing in flight; nothing owed.

## RULINGS FOLDED

- **default-export: protected** (record "2026-11-22 OWNER RULING — default-export: protected (a part used alone is
  available inside the binding and is not exported)"), his words whole: "default-export: protected". Folded into:
  core/labels/export (statement, statements 2, 3, 5 marked, the four-row analogy table, two new lines),
  core/labels/export/flat-read-outside (statement; his example "A := <label a> B := A & A   C := B & (B.a: 9) here
  B.a is always an error." with lines), core/labels/flow, core/labels/paths, binding-prefix, label-reference,
  call-prefix, closed-argument, two-sources, core/holes/labels, nested-scope, core/patterns/atomic, the errors
  table; library: length, peek, hits, occurrences, endsWith, list_of, rx.repeat. Each touched piece's details entry
  gains a rulings item and a history line quoting the old text.
- **export-list: yes** (R-1; record "2026-11-22 OWNER RULING — export-list: yes (...)"), with his question and
  proposal quoted whole: a new ruled piece core/labels/export/export-list (the forms table, readings (a)-(f) marked,
  three printed lines); its row in the analogy table; "some labels but not others" answered in core/labels/export;
  the one-form-two-targets sentence stated once in core/modules/binding-list; a placeholders row.
- **His caveat** (R-2; record "2026-11-22 OWNER, on the two name spaces: "Agree caveat bindings used to scope
  labels (A.a: 8)""): quoted beside the agreement in core/modules/binding-list, and in core/conditions/form's
  "Left of `:`" bullet, both "(a reading)".
- Two new OPEN pieces (not ruled; neither answer applied): core/labels/paths/argument-default and
  core/labels/export/capture-export, each with both candidates and run lines.

## MANAGER READINGS TESTED

| reading | verdict | evidence (check in preddef_model.py) |
|---|---|---|
| (a) used alone = a sequence operand, hole or `&` operand without part label, as `[_A = A]` | SUPPORTED | PROTECT, ANALOGY |
| (b) a binding exports its own text's labels and, through a public part label, that part's exports (`pub.a.h`) | SUPPORTED; lane addition (a reading): by name too, `pub.h`, for a labelled part | PROTECT |
| (c) an outside read of a label only a part used alone holds is a compile error | SUPPORTED | PROTECT, SCAN, SWEEP plant s16 |
| (d) `[=A]` (read `[A = A]`) exports a part under its own name | SUPPORTED as run with `[A = A]` (the model does not parse `[=A]`) | ANALOGY |
| (e) a call exports what its body writes; an argument used alone is not exported (`B.d`, `c.d`); example 3 passes it on | SUPPORTED | MACRO, ATOMIC |
| (f) array-in-piece unchanged | SUPPORTED | ARRAY |
| (g) his `B.a` "always an error", plain and group question, at C and at the top | SUPPORTED | EXAMPLE |
| (h) `length` exports no `ch` | SUPPORTED | LIBRARY |
| R-1 (a) one form, two targets | UNTESTED (wording) | — |
| R-1 (b) forms carry over | SUPPORTED for one, renamed, all, all but one; several UNTESTED | LIST |
| R-1 (c) alias, no new capture | UNTESTED (captures not modelled) | — |
| R-1 (d) listed name also written: same label | UNTESTED | — |
| R-1 (e) no path name for the part | SUPPORTED | LIST |
| R-1 (f) only an exported label can be listed | SUPPORTED (plant s6) | LIST |

Not supported: none.

## ANSWERS CHANGED

None. SWEEP: 229 printed three-mode lines of the six documents, old engine (predfix82's) against the rule under
argument-default's candidate (local): lines the old engine reproduced and the rule does not: 0; ANSWERS_CHANGED 0.
Two lines reproduced by the rule only (core.md, the export-list lines; the old engine has no list form).

## WHAT MOVED

| tag | old binding and reference | new |
|---|---|---|
| core/patterns/atomic | `[ab = atomic(B \| A)] & (ab.l: <20)` | re-spelled `atomic([ab = B \| A]) & (ab.l: <20)`, answers unchanged; awaits argument-default |
| core/labels/export | prose "`/${A}!/` ... shows `h`" (`pub.h`, pub := `/${A}!/`) | now a compile error (line "Used alone, from outside") |
| core/labels/export/flat-read-outside | his `C := B & (B.a: 9)`; `some((B.a: 9))` was legal | now a compile error, both (line "His example"); `B.x.a`, `B.y.a` under `[x = A] & [y = A]` added |
| core/labels/paths/binding-prefix | prose `X.D.h`, X := `D SEQ "!"` legal | now a compile error (line "X's use, used alone in X"); `X.d.h` under `X := [d = D] SEQ "!"` added |
| core/labels/paths/call-prefix | prose `B.d`/`c.d` "as the call surfaces it" with any body | `/${rx}xx/`: now a compile error (line "By the macro's name, the body writing no `d`"); line "d as the call surfaces it, the last mention (B's)" renamed "d as the call exports it, the body's own", program unchanged |
| core/labels/paths/call-prefix | `B(A) & (A.d: <5)`; `pair(A) & (A.d: <5)` | unchanged; awaits argument-default |
| core/labels/paths/closed-argument | `B(A) & (A.d: <5)` | unchanged; awaits argument-default |
| core/labels/paths/two-sources | `B([x = /(?<d>\d)/]) & (x.d: <5)` | unchanged; awaits argument-default |
| core/holes/bare-condition/nested-scope | `C := B(A) & (A.d: <100)` | unchanged; awaits argument-default |
| lib/modifiers/length | prose "`ch` is visible in the result" | `length.ch`, `length.chars.ch` now compile errors |
| lib/control/peek, lib/search/hits, lib/search/ends-with, lib/records/list-of | `peek(/(?<d>\d)/) SEQ /\d\d/`, `hits(/a(?<g>x)?/) & (g: "x")`, `endsWith(/(?<n>\d+)/)`, `list_of(/(?<h>\d)/, sep = ",")` | unchanged; awaits argument-default |

Counts: re-spelled 1; turned into a compile error 5 (export, flat-read-outside, binding-prefix, call-prefix,
length); left marked "awaits argument-default" 10 printed lines (AWAITS: `grep -c 'awaits argument-default'
core.md library.md` → 13 and 7, the rest bullets and the open piece). Under (error) each of the 7 marked lines
that reads the argument's label is refused (AWAITS); the other 3 (peek, endsWith, list_of) carry the label only as
an annotation, and their library bodies are not modelled by either engine (REFUSED in both; their answers are the
earlier lanes', not re-run here).

## DRAFT READINGS ADDED

- statement 3 keeps passing a labelled part's labels by name (`pub.h`) as well as by path: the ruling reverses it
  "for an unlabelled part" only.
- a pattern macro's call written alone in a body is a use alone, as a bound name is.
- an argument written in place belongs to argument-default with an argument that is a binding.
- `atomic(X)` uses X alone, so a label on the call reaches none of X's labels.
- the two-sources first shape now depends on argument-default; the top-level shape is unchanged.
- a hole's definition exports none of the inserted pattern's labels; labelling the insert passes them on.
- `chars` exports `ch` (its own part label); `length` does not.
- the export-list forms table and readings R-1 (a)-(f), each "(a reading)".

## OWNER QUESTIONS LEFT

- **argument-default**: where a macro's body uses an argument alone, is the caller's `A.d` (or a group written in
  place) its own local read, legal, or a compile error? Lines kept and marked; core/labels/paths/argument-default.
- **capture-export**: does a capture in rx text inside a part used alone still reach the caller (as PCRE), or follow
  its label? Statement 5 marked; core/labels/export/capture-export.
- Untouched, as briefed: two-sources (its piece now says what default-export changes), idiom-confirm,
  zero-condition-binding, macro variables/types, count-several, capture-loop-value, zero-in-loop.

## EVIDENCE AND COMMANDS

- `timeout 900 python3 -I -B docs/dev/lanes/preddef_evidence/preddef_model.py` → `preddef_model: 22 checks, 0
  failed` (`preddef_model.out`). Checks: CONTROL, PROTECT, EXAMPLE, ANALOGY, MACRO, AWAITS, UNMARKED, ARRAY,
  NESTED2, LIBRARY, VISIBLE, SETAND, LIST, CAPTEXP, ATOMIC, SCAN, NULLABLE, SUCCESSOR, SWEEP, QUOTES, MARKS, DOC.
- Sabotage: `PREDDEF_SABOTAGE=sN` for s1..s22, each alone → each target check FAIL, traceback 0
  (`preddef_sabotage.out`, 22 lines). The required plant (a printed program re-spelled to read an unexported label)
  is s16, caught by SWEEP; s20 plants the same read for the textual SCAN.
- SUCCESSOR: predfix82, predbound, predref, predcall, predfix77, predarr, predscope re-run, last lines read; reds
  declared: predfix82 MARKS (ANS-1's wording left the reflowed call-prefix bullet; the pointer stands) and
  SUCCESSOR (its re-run of predref/predcall meets their new DOC reds); predref DOC (the atomic line re-spelled:
  ATOMIC, SWEEP); predcall DOC (the renamed line: MACRO); the rest as predfix82 declared them.
- Engine fix outside the rule: SETAND (the loaded set test read `A & A` as a set).
- Known limit (EVID-4): a nullable loop body past the minimum is not modelled; NULLABLE: 320 programs, 0 with one.
- Lint: `timeout 120 python3 -I scripts/pred_doc_lint.py` → failed 0; `make -s test-plan-lint` clean.
