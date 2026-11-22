# predbound — bound-condition and count-in-set folded into the predicate documents (with R-1..R-3)

Lane predbound (opus), branch lane/predbound cut from lane/pred-rev28 at 1e0384941; lane/pred-rev28 merged in
twice, alone (5e01f6527 for R-1/R-2, 6e21606b2 for R-3). Design only; docs only; no build go.

## STATE AT HANDOFF

OWED: none

- Commits: 5893e9575 (bound-condition and count-in-set folded, evidence model), 5e01f6527 (merge, R-1/R-2),
  400edd840 (R-1 binding-prefix ruled, R-2 joint values, the open label-reference), 6e21606b2 (merge, R-3), and
  the final commit (R-3 folded, report, history line).
- Rulings file: last entry applied R-3 (label-reference ruled "required"); R-1 and R-2 applied before it.
- `python3 -I scripts/pred_doc_lint.py` (subshell at the worktree root): "pred_doc_lint: checks passed 6080,
  failed 0" on the final tree (5779 passed at the start, premise (a)). `make -s test-plan-lint`: "checks passed:
  2, checks failed: 0".
- Evidence: docs/dev/lanes/predbound_evidence/predbound_model.py, "predbound_model: 21 checks, 0 failed"
  (predbound_model.out); 20 plants s1..s20, each caught by its target check, no traceback (predbound_sabotage.out).
- Premise test: (a) 5779 passed, failed 0; (b) "predfix77_model: 20 checks, 0 failed"; (c) the record's last
  entry began "2026-11-22 OWNER RULING — count-in-set: b". All three held.
- predfix77_model.py after the fold: as committed it stops at load (`AssertionError: `chars := (.*?)`, `nchars`):
  its library reader looks for the `nchars` helper, now gone. Run in scratch with the two old helper bodies given
  as constants: "predfix77_model: 20 checks, 2 failed (CHARS, MARKS)". CHARS reads the printed `length` line in
  the `nchars` spelling (covered by predbound FIVE, length row, and LABELREF); MARKS reads bound-condition as open
  and array-vs-passes's pointer (covered by predbound MARKS and REFUSE). Its DOC stays green.
- Not touched (not mine): plan.md, decisions.md, known_issues.md, the record, docs/dev/pred/*, reviews, skills.

## RULINGS FOLDED

- bound-condition (b), record "2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left
  open", with his position, correction and "illegal meaning a compiler error": core/holes/bare-condition/bound-condition
  now `ruled`. A condition or computed value bound alone that names a label no pattern in its binding holds is a
  compile error at the binding. The five refused definitions are rewritten in place (below). `c := (0: 5)` left
  open: new open piece core/holes/bare-condition/zero-binding (slug zero-condition-binding), both candidates run,
  neither applied. His two alternatives are under construction: core/operators/bindings/label-variables and
  core/operators/bindings/macro-types (both meanings (i), (ii) of the restriction stated, neither chosen).
- count-in-set (b), record "2026-11-22 OWNER RULING — count-in-set: b ...": new ruled piece
  core/conditions/form/value-left; core/conditions/form's "p a label path, never an expression" revised.
- R-1, binding-prefix, record "2026-11-22 OWNER RULING — binding-prefix: 1 yes ...": new ruled piece
  core/labels/paths/binding-prefix. His example reproduces the record's pasted `all` line in every mode, and the
  rejected last-use reading reproduces its `last` line. core/labels/flow's "A binding's name is not a path"
  revised. The parked piece the brief asked for is not made (R-1).
- R-2: reading (d) changed: the components of a joint entry may be values. And an open label-reference piece,
  which R-3 then made ruled.
- R-3, label-reference "required", record "2026-11-22 OWNER RULING — label-reference: required ...": new ruled
  piece core/labels/paths/label-reference. Every program this lane wrote uses the required form: `length(S) :=
  chars & (count((chars.ch: /(?s:.)/)): S)` and `months & (months.mname.index: S)`. The second spelling is the
  form the model supports, because the part label `mname` is reached through the binding `months`. Pointer
  sentences were added in flat-read-outside, export statement 3 and nested-scope example 1. Their statements and
  lines are left for the next lane's sweep, as R-3 says. His idea is in a parked piece:
  parked/ideas/unqualified-after-definition.
- Also parked: parked/ideas/declared-labels (his "aside").

## MANAGER READINGS TESTED

bound-condition and count-in-set (the brief):
- (a) a condition written in place, an argument included, is unchanged: SUPPORTED for `inner((h: <5))` and `B((0:
  /\d/))` (INPLACE). `when`'s test was UNTESTED here, because the model has no `when` lowering.
- (b) a set bound alone is unchanged: SUPPORTED (SETBOUND). It gives the record's pasted `[6-9]` line, 0 / 0 / 0
  of 85 texts.
- (c) the five definitions in place: SUPPORTED (FIVE). All six printed lines rebuilt from the new program text
  have the same answers as at 1e0384941, and each WHOLE matches a direct rule (0 differ). `(a: <(10 - $b))` was
  re-run: 0 of 100 digit pairs differ, 55 hold (SUMALT). For `n` the in-place form is `(count((d: "7")): ==2)`,
  not the list's `occurs.exactly`, because count-in-set (b) came after the list.
- (d) left part: bare name/path = label, else value: the manager's call, run as the model's parse (META, FIVE).
  - Single value only: UNTESTABLE as a rule; the model refuses several strings (SEVERAL).
  - A value that yields nothing fails the entry and `NOT` holds on it: SUPPORTED (NOTHING).
  - `($h: S)` and `(h: S)` answer alike: SUPPORTED, 18 programs, 0 / 0 / 0 (SAMEREAD).
  - Joint entry (R-2 changed this): components may be values, SUPPORTED, 0 of 300 differ (JOINTV).
  - A default stays a label form: UNTESTED.
- (e) the error is reported at the binding, used or not: run (ATBINDING). The class (an ordinary compile error)
  is his words. The place is a reading.
- (f) computed-labels restated as a value in an entry, `count`'s binding form withdrawn: done (MARKS).
- (g) a binding whose body uses a pattern that holds the label is legal: SUPPORTED (LEGAL: `length`, `year`).
- (h) sweep: at 1e0384941 the refused bindings in the base files were exactly:
  - the five definitions: `c`, `sum`, `n` twice in print, `nchars`, `mnum`;
  - `length` through `nchars`;
  - `lt5`;
  - two already printed as refused: `inner` and example 2's `B`.
  None was found beyond the five. Now every refused binding in the base files is printed as refused (SWEEP).
  Details lines that the sweep finds are as-run records (`rejected:`/history, an ideas-file source text):
  core/labels/labels-vs-captures/array-vs-passes's rejected "Passes" line, parked field-count's source, and
  label-parameter's history. I re-worded one live reading, group-truth's "c := `(d: "7")`" notation. The
  readings of computed-labels, length, month_numbered and count were rewritten, with the old text verbatim in
  history.

binding-prefix entry (R-1), each "(a reading)":
- (a) one use answers as `[aa = A]`: SUPPORTED. The line "One use" equals the printed `[aa = ...]` line (PREFIX).
- (b) uses are counted per definition: SUPPORTED as run (PREFIXRD).
- (c) an explicit part label twice is unchanged: SUPPORTED (PREFIXRD).
- (d) nothing private is reachable: SUPPORTED as run (PREFIXRD). Making such a reference a compile error is the
  model's choice; it is not stated.
- (e) a macro's name is not a prefix: SUPPORTED as run (PREFIXRD).
- (f) a label and a binding of one name: UNTESTED.
- (g) the error can be relaxed later: UNTESTABLE.

label-reference entry (R-3):
- (a) and (b): the model's rule, run (LABELREF, META). `B(A) & (A.d: <100)` is legal; `(d: ..)` is refused.
- (c) the rule covers `$` reads too: applied by the model.
- (d) where a label comes from a macro call, an argument or a typed parameter: NOT STATED, to be asked.
- (e) no answer changes, only spellings: SUPPORTED for this lane's programs. The required form against the bare
  form read as before gives 0 / 0 / 0 of 63 texts (LABELREF). The other programs are the next lane's.

Not supported: none.

## ANSWERS CHANGED

No printed answer moved. Each change is a spelling or a status, and each follows a ruling unless marked:
- pass-start-read: was `${c}`, c := `NOT (h: /\d/) | (n: >= $h)`. Now the test is written in its hole. The
  same line.
- computed-labels: was "named left of `:` like a label", with `sum := $a + $b`. Now `(($a + $b): <10)`. The
  same line. Still a reading.
- array-vs-passes "A count of zero" and lib/counting/count: `n := count(..)` became `(count(..): ==N)`. The same
  lines.
- length: was `chars & (nchars: S)`. Now `chars & (count((chars.ch: /(?s:.)/)): S)`. The same line.
- month_numbered: was `months & (mnum: S)`, `mnum := $mname.index`. Now `months & (months.mname.index: S)`. The
  same line.
- core/conditions/form: was "never an expression". Now a value may stand left of `:`.
- core/labels/flow: was "A binding's name is not a path". Now a binding's name is a prefix.
- The macro line `lt5(S) := (h: S)` under (a): now a compile error (a reading). The line moved to `rejected:`.

## WHAT MOVED

- New pieces:
  - ruled: core/conditions/form/value-left, core/labels/paths/binding-prefix, core/labels/paths/label-reference;
  - open: core/holes/bare-condition/zero-binding;
  - under construction: core/operators/bindings/label-variables, core/operators/bindings/macro-types;
  - parked: parked/ideas/declared-labels, parked/ideas/unqualified-after-definition.
- Open to ruled: core/holes/bare-condition/bound-condition.
- Re-dated 2026-11-22: form, pass-start-read, reads, bare-condition, nested-scope, flow, paths. Reading re-dated:
  computed-labels (renamed "A computed value in an entry"), length, month_numbered.
- Two error rows added to core/diagnostics/errors: the bound-alone binding, and a plain read through a twice-used
  prefix; plus the reading row for several strings left of `:`.
- Lines moved: bound-condition's (a)/(b) and his two examples went to zero-binding. "A macro returning a
  condition" and "The last use only" went to `rejected:`. "Bare, read as before the ruling" went to
  label-reference's `rejected:`.
- The brief's parked/ideas/binding-prefix was drafted in 5893e9575 and removed in 400edd840. It was never
  delivered, so it has no `was:` line.

## DRAFT READINGS ADDED

All are marked "(a reading)" in the base:
- the left-part parse rule;
- a value is single;
- nothing fails the entry and `NOT` holds;
- `$h` on the left;
- values in a joint entry;
- the error is placed at the binding;
- a macro whose body is a condition is the same form;
- the macro-types target reading;
- the binding-prefix readings (a)..(g) and the label-reference readings (a)..(e);
- in the model only: a path to a label the prefix does not pass is a compile error.

## OWNER QUESTIONS LEFT

- zero-condition-binding: a condition on `0` bound alone, `c := (0: 5)`.
- macro variables and macro types: spellings, and the meaning of the restriction ((i) or (ii)).
- label-reference (d): the source of a label that comes from a macro call's body, from an argument, or from a
  typed parameter.
- binding-prefix (f): a label and a binding with one name.
- For the manager:
  - the statements of flat-read-outside and of export statement 3 still say "read flat". This lane added
    pointers only, per R-3. doc_format.md asks that a ruling rewrite the statements of the pieces it changes. I
    leave this to the sweep lane: reply either way.
  - `when`'s test as an argument was not run.
- Untouched, as the brief says: record-in-some, count-several, helper-captures, capture-loop-value, zero-in-loop.

## EVIDENCE AND COMMANDS

- `(cd worktrees/predbound && timeout 300 python3 -I -B docs/dev/lanes/predbound_evidence/predbound_model.py)`
  prints "predbound_model: 21 checks, 0 failed" (predbound_model.out). It runs CONTROL, REFUSE, SETBOUND,
  ATBINDING, INPLACE, LEGAL, FIVE, SUMALT, NOTHING, SAMEREAD, SEVERAL, ZERO, META, SWEEP, PREFIX, PREFIXRD, JOINTV,
  LABELREF, QUOTES, MARKS and DOC.
- Sabotage: `PREDBOUND_SABOTAGE=sN` for N in 1..20, each run alone (predbound_sabotage.out). Each plant is caught
  by its target check, no traceback.
- Lint: `(cd worktrees/predbound && timeout 300 python3 -I scripts/pred_doc_lint.py | tail -1)` prints "checks
  passed 6080, failed 0". `make -s test-plan-lint` is clean.
- predfix77 re-run: `timeout 120 python3 -I docs/dev/lanes/predfix77_evidence/predfix77_model.py` stops at load
  (above). A scratch copy with the two helper bodies as constants
  ($PCREC_TMPDIR/scratch/predbound/p77_patched.py) prints "20 checks, 2 failed (CHARS, MARKS)".
- The model copies predfix77's lowerer and matcher unchanged. It reads the old printed lines from 1e0384941 by
  `git show`. The library bodies are read from library.md. Controls: python `re` on hand regexes, direct counts,
  the record's pasted lines (`[6-9]`, `all`, `last`) and the record's words (QUOTES, 13 passages).
