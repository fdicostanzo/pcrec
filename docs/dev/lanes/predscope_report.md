# Lane predscope — the 2026-11-21 scope and capture rulings folded into the predicate documents

Design-document revision only ([COND-FAMILY]); nothing under src/ cli/ lib/ memfn/ tests/ scripts/ touched. Tier opus.
Branch lane/predscope, cut from lane/pred-rev28 at 36a74948f.

## STATE AT HANDOFF

- STATE: delivered. Tip: the commit carrying this report (on top of 6d2dd2a0e, the WIP fold).
- Lint: `python3 -I scripts/pred_doc_lint.py` → `pred_doc_lint: checks passed 5434, failed 0` (one soft WARN, parked.md
  over its 16 KB soft cap, as at the start).
- Rulings file `docs/dev/lanes/predscope_rulings.md`: rulings file empty (re-read before each commit and before this
  report).
- PREMISE: (1) lint at the starting tip ended `failed 0` with 5,331 passed, not the brief's 5,289 (the manager's two
  folds of today, class-value and flat-read-outside, added checks). (2) predfix61's model re-ran byte-identical (no
  diff). predasc's model DIFFERED on one line: its TAGS check asserts `[lib/builtin/enumerate/class-value] open
  class-value`, which the manager's own fold f26a28b5e turned to `ruled 2026-11-21`; every other predasc check, and its
  printed answers, are unchanged (23 of 24 ok). The brief names that fold as done, so this lane read the diff as an old
  status pin the fold made stale, not as a broken premise, and went on. predasc's files are historical, so the lane did
  not edit them; the class-value lines are re-run here instead (CLASSV).
- OWED: none

## RULINGS FOLDED

R-A, pure-label (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a
capture afterwards too; `_` labels never export; three examples of what a definition may name"), his words: "i agree
that captures are explicitly written either in literal form or using a macro like capture()." Pieces:
core/labels/export (statement 5 narrowed to CAPTURES; `[x = A]` a label and no capture), core/labels/paths (first
bullet), core/labels/labels-vs-captures (a label is not always a capture), core/labels/export/caller-ambiguous (the
question narrowed to captures), core/holes/labels (what flows is labels), lib/structural/capture (its "reach the caller
by export with no macro" bullet), lib/search/hits ("captures level": `hit` is a capture), lib/modifiers/length (`ch` is
also a capture), lib/modifiers/month-numbered (`[mname = ...]` makes no capture). His supporting words of 2026-11-17,
"setting labels is just the label using the group-label-not-capture syntax", are cited in labels-vs-captures and paths.
The REQUIREMENT ("so an add on component that converted a label into a capture is needed") and the two methods ("a
wrapper like [ d = capture(digits) ]", "afterthefact like [ d = digits ] & capture(d)", "no spelling suggested") are
the new under-construction piece lib/structural/capture/add-on and a row of core/spellings/placeholders.

R-B, the `_` labels (same entry, "as we discussed"): "1. purely predicate labels and 2. cannot become exported
captures (although they might be internal captures)". Pieces: core/labels/export (a bullet), lib/structural/capture/add-on.

R-C, zero-in-definition (record: "2026-11-21 OWNER RULING — zero-in-definition: a (`0` is the match so far of the
definition it is written in)"), his words "zero-in-definition: a". Pieces: core/conditions/match-so-far (statement:
the DEFINITION, a binding or a macro body; within one definition composed, the ruled `/\d/ SEQ (0: /7/) SEQ /\d/`
unchanged), core/holes/bare-condition (statement), core/holes/pattern (last bullet), core/holes/bare-condition/nested-scope
(the `0` line ruled, "Match so far (ruled)").

R-D, his three examples "rather than rules", folded verbatim with his verdicts into
core/holes/bare-condition/nested-scope: (1) "is legal. C can see d as a flat look into A. C cannot see rx as its a
binding variable not a label."; (2) "is incorrect."; (3) "would be correct". Example 1's "C can see d as a flat look
into A" also cited in core/holes/labels; "C cannot see rx as its a binding variable not a label" in
core/operators/bindings. The manager's rule over the three is in nested-scope marked "a reading, the manager's, not his
words".

Not folded as rules (kept as questions, placeholders or untouched, as the brief says): how a capture is asked for
(under construction); the manager's frame (finished rx, shaping and matching holes, renaming apart, three kinds of
reference) is recorded nowhere in the base; open-versus-closed as a general rule (nested-scope stays open for a label
of the definition's user); `[=year]` and `.` are spellings-table entries (`[=year]` read as `[year = year]`, a reading,
also a reading line in core/labels/paths); the label parameter stays parked (a source line added to its details);
M-2: nothing.

## MANAGER READINGS TESTED

class-value:
- (a) a caseless single character enumerates in codepoint order (`(?i)k`: `K`, `k`, U+212A): SUPPORTED as to the
  order (python `re`, str mode, IGNORECASE, over every codepoint: U+004B, U+006B, U+212A; CASELESS). UNTESTABLE that a
  caseless character is a class for `enumerate` (no ruling says so). Which members libpcre2 gives in UTF, UCP and byte
  mode is a PCRE2 fact this lane did not look up (D181): a question for a pcre2-reader.
- (b) "codepoint" in byte mode is the byte value: UNTESTABLE (it defines a word; no ruling speaks of byte mode). For
  orientation: `[A-C\xe9\x80]` in python bytes mode orders 0x41 0x42 0x43 0x80 0xe9, the Latin-1 codepoint order (BYTES).

pure-label:
- (a) the rule his three examples fit: NOT SUPPORTED as stated. It fits all three examples (EX1, EX2, EX3), but applied
  to the 17 definitions the documents print (NAMES) it refuses 7 of them. Five are bound conditions and computed
  labels that read labels of the pattern they meet: pass-start-read's `c := NOT (h: /\d/) | (n: >= $h)` (the
  piece is RULED, its example the draft's), computed-labels' `sum := $a + $b`, count's `n := count((d: "7"))`,
  length's `nchars`, month_numbered's `mnum`. The other two are nested-scope's own Condition and Read lines. With bound
  conditions and computed labels outside the rule (they are "laid against the labels of the pattern it meets",
  core/conditions/form, ruled), only nested-scope's two lines are refused. Legal under the rule: lib/control/when (its
  body names no label), lib/search/occurrences' `hit` (its body writes it), looped-compare's `late`, export's `year`,
  `capture`, `list_of`, `date_in`, length's own body, and bare-condition/labels' Composed `B := /${(c: >= 5)}(?<c>\d)/`.
  That last one is legal BY NAME because B writes a c of its own, but it reads A's VALUE. A definition closed to its
  user's labels would CHANGE that line from HOLDS to never matching: composed WHOLE `73` HOLDS, closed WHOLE `73`
  FAILS / SEARCHED `37 73` FAILS / FIND-ALL `73 37 51` [] (CLOSEDB).
- (b) it is the closed answer to bare-nested-scope for labels and reads: UNTESTABLE by the record. None of his examples
  names a label of the definition's USER (the piece's Condition and Read lines do). Example 2 is a parameter's label.
  So the examples refuse COMPOSED for a parameter's labels and say nothing about labels from above.
- (c) an after-the-fact capture names its label by the visibility rules, so a `_` label cannot be captured outside its
  binding: SUPPORTED by the record (export statement 1, "A private label is visible only inside the binding it is
  written in"; his "cannot become exported captures (although they might be internal captures)"). A refusal, not run.
- (d) `capture(name, x) := /(?<${name}>${x})/` is the wrapper method in literal form: SUPPORTED as a wrapper that makes a
  capture (python `re` groups of its lowering: `d`; CAPT). But his wrapper placeholder `[ d = capture(digits) ]` takes
  its name from the part label, which this body cannot do (the field the core lacks, already stated in the piece). The
  second half (the after-the-fact form has no body, native) is UNTESTED: no form is defined.
- (e) what the caller reads for a captured label a loop sets is not stated: SUPPORTED (no record line states it). The
  two values part on `/(?:(?<h>\d)?;)+/` on `3;;`: the label is unset, python `re`'s capture is `3` (LOOPVAL).

condition-argument: a condition passed as an argument is resolved in the caller's definition: SUPPORTED. The record's
`tagged` line is reproduced mechanically, with `when`'s body read from library.md: WHOLE `n:42` HOLDS, `n:ab` FAILS,
`w:ab` HOLDS, `w:42` HOLDS / SEARCHED `n:ab w:ab` `w:ab`@5 / FIND-ALL `n:42 n:ab w:ab n:7x` [`n:42`@0, `w:ab`@10,
`n:7`@15]. `when`'s body names no label, so resolved there `kind` would not be visible (WHEN; plant s18).

zero-in-definition:
- (a) an expression written in place belongs to the definition it is written in: SUPPORTED by the words as put ("the
  definition it is written in"). Run: `/\d/ SEQ B((0: /\d/))`, B(rx) := `/${rx}xx/`. As the caller's, WHOLE `5xx`
  HOLDS / SEARCHED `a5xx` `5xx`@1 / FIND-ALL `5xx 55xx` [`5xx`@0, `5xx`@5]. As the macro's, it never matches (ZARG).
- (b) a condition bound alone takes the `0` of the definition it is USED in: UNTESTABLE by the record, and it pulls
  against the words. The answer as put, "`0` is the match so far of the definition it is written in", read literally
  makes the binding `c := (0: rx.digit)` that definition, and its match so far at the condition is empty. Both run on
  `/\d${c}x/`: as if in place, WHOLE `7x` HOLDS; the binding's own `0` never matches (ZCBIND). Asked below as
  zero-condition-binding.
- (c) `${A & (0: S)}` unchanged: SUPPORTED by the record (operand-world, ruled; his 2026-11-19 "but not
  /${A & (0: digit)}/ where it is only the A"). Not re-run here (preddoc1 EX-bare-and).
- (d) zero-in-loop untouched: SUPPORTED (the ruling's question and answer name definitions, not passes);
  core/conditions/match-so-far/in-loop is unchanged and still open.

M-2: nothing to test.

## ANSWERS CHANGED

No printed three-mode answer moves. Every line that shows label values in parentheses ("HOLDS (a = `1`, b = `23`)")
shows LABELS and stands. What changed, and on what ground:
- core/labels/export statement 5. It was "The caller's captures are what is visible from the top-level program by these
  rules." It is now the CAPTURES visible from the top-level program (the groups in rx text and the capture forms), with
  `[x = A]` a label and no capture. FOLLOWS from R-A ("It NARROWS export statement 5").
- core/labels/paths first bullet. It was "`[x = A]` is the group form `(?<x>A)` read as a label; inside pattern text a
  named group is the same thing." It is now: `[x = A]` makes a label and no capture; a named group in pattern text is a
  label and also a capture. FOLLOWS from R-A.
- lib/structural/capture. It said "A binding's public labels reach the caller by export with no macro"; now a label
  reaches the caller only as a capture. FOLLOWS from R-A.
- core/labels/export/caller-ambiguous was about "a public label two parts both set" and is now about "a public capture
  two parts both make". A READING of R-A (a label no capture makes never reaches the caller). Its example's h is
  written in rx text, so the run is unchanged.
- core/conditions/match-so-far statement. It was "the text the rx the condition is written in has matched"; now "the
  text the definition the condition is written in (a binding or a macro body) has matched". Its bullet "The rx it is
  written in is the rx composed at the point the condition is used" is now "within one definition ... as composed".
  FOLLOWS from R-C.
- core/holes/bare-condition statement. It was "its `0` is the surrounding rx's match so far"; now "that definition's
  match so far to the hole". FOLLOWS from R-C.
- core/holes/pattern last bullet. It was "`0` in the outer rx is the outer match so far"; now the outer definition's
  `0` includes the inserted text, and an inserted definition's `0` is its own. FOLLOWS from R-C.
- core/holes/bare-condition/nested-scope. "Match so far, (a)" is now "Match so far (ruled)", and the (b) line moved to
  the details (rejected). FOLLOWS from R-C. The statement is narrowed to a label the definition's user sets. A READING:
  the `0` part is ruled and examples 1-3 decide a parameter's labels.
- core/holes/bare-condition. The binding bullet said "behaves as the bare condition does". For its `0` it now says the
  record does not settle it. This is a consequence this lane DERIVED from R-C's words (above), not a ruling.

## WHAT MOVED

Changed pieces (core.md): core/labels/labels-vs-captures (2 bullets, a run line, `see:`; date 2026-11-21);
core/labels/export (statement 5, 2 bullets; date); core/labels/export/caller-ambiguous (heading name "... shared
capture", statement, body; date); core/labels/paths (bullet 1 rewritten, a `[=year]` bullet; date);
core/conditions/match-so-far (statement, 3 bullets, the "An argument" line; date); core/values/reads (the nested-scope
pointer reworded); core/holes/pattern (last bullet; date); core/holes/labels (2 bullets; date); core/holes/bare-condition
(statement, the binding bullet, 2 run lines; date); core/holes/bare-condition/labels (the pointer and the Composed
sentence; status and date unchanged); core/holes/bare-condition/nested-scope (heading name "What a hole in a used
definition may name", statement, body restated, 3 example lines; status stays `open bare-nested-scope`, date
2026-11-21); core/operators/bindings (1 bullet; date); core/spellings/placeholders (two rows widened, one row added).
Changed pieces (library.md): lib/structural/capture (bullet replaced, 2 added; date); lib/search/hits, lib/modifiers/length,
lib/modifiers/month-numbered (one sentence each).
Added: lib/structural/capture/add-on, `under-construction 2026-11-21` (its details entry too).
Details: an entry for each piece above (rulings items cite the record titles; readings with verdicts; history with
the words before), lib/builtin/enumerate/class-value (the two readings' verdicts), parked/ideas/label-parameter (today's
source line, permitted by the brief). The slug zero-in-definition is added to match-so-far's `slugs:`.
Not re-tagged: no tag moved. Unaffected on reading, said here because the brief names it: export's bullet "A filter
operand's labels are visible like any others" (it is about labels within the program, not about what the caller gets).
Also: docs/dev/history/claude_md/docs__dev__lanes.md gains the report's index line (N-1).
How these were found: `grep -n -i "caller\|captures level\|capture" core.md library.md parked.md` and
`grep -n -i "visible in the result\|to the caller\|reach.* caller\|caller gets\|caller sees\|caller's capture"` over
the six predicate files.

## DRAFT READINGS ADDED

Each is marked "a reading" in the base:
- labels-vs-captures: what the caller receives for a captured label a loop sets is not stated.
- caller-ambiguous: a capture name two parts both make is ambiguous for the caller as for the program; a label no
  capture makes raises no such question.
- paths: `[=year]` is `[year = year]`.
- match-so-far: a program's final expression is the outermost definition. An expression written in place belongs to
  the definition it is written in.
- bare-condition: a bound condition's `0` read as if written in place is a reading the ruling does not settle.
- nested-scope: the rule over the three examples (the manager's), with bound conditions and computed labels outside it.
- bindings: an argument, a condition included, is written and resolved in the caller's definition.
- capture: `capture(name, x)` is the wrapper method in its literal form.
- add-on: after the fact, a `_` label cannot be captured outside its binding. The after-the-fact form has no body today.
- hits, length: a group written in rx text in a body is a capture as well as a label.

## OWNER QUESTIONS LEFT

1. zero-condition-binding (proposed slug). A condition bound alone, `c := (0: rx.digit)`, used in a hole: is its `0` the
   using definition's match so far, as if written in place (a), or the binding's own, empty at its point (b)? Program
   `/\d${c}x/`. (a): WHOLE `7x` HOLDS, `77x` FAILS / SEARCHED `a7x` `7x`@1 / FIND-ALL `7x 12x 8x` [`7x`@0, `2x`@4,
   `8x`@7]. (b): WHOLE `7x` FAILS, `77x` FAILS / SEARCHED `a7x` FAILS / FIND-ALL `7x 12x 8x` []. Leaning: (a). A
   condition has no rx of its own and is "laid against" the pattern it meets. Under (b) a bound `0` condition can
   never hold.
2. bare-nested-scope (the existing slug, narrowed). May a hole in a definition name a label its USER sets? (a) CLOSED:
   a compile error, as example 2 makes it for a parameter's label; (b) COMPOSED. Program `/(?<h>\d)${inner}/`,
   inner := `/x${(h: <5)}/`. (a): a compile error. (b): WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 /
   FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6]. Under (a), bare-condition/labels' Composed line (B writes its own c and reads
   A's) would also become never-matching, if the closing covers values as well as names. Proposal for the piece's
   status: it STAYS OPEN. The `0` line and his three examples are ruled, but no example of his speaks of a label from
   above, and the rule over the examples is the manager's.
3. capture-loop-value (proposed slug). For a capture whose group a loop sets, does the caller receive PCRE's carried
   value (a) or the label's last-pass value (b)? Program `/(?:(?<h>\d)?;)+/`: WHOLE `3;;` HOLDS, `3;` HOLDS / SEARCHED
   `x3;;` `3;;`@1 / FIND-ALL `3;; 7;` [`3;;`@0, `7;`@4]. The match is the same under both. On `3;;`, (a) gives h = `3`
   and (b) gives h unset; on `7;`@4 both give `7`. For a label made a capture by the add-on, the same question.

For a pcre2-reader, not the owner: which members `(?i)k` has in libpcre2 in byte, UTF and UCP mode.

## EVIDENCE AND COMMANDS

- `timeout 110 python3 -I -B docs/dev/lanes/predscope_evidence/predscope_model.py` → `predscope_model: 20 checks, 0
  failed` (committed as `predscope_model.out`; runs in about 1 s). Checks: CONTROL, FLATR, CLASSV, CAPT, EX1, EX2, EX3,
  NAMES, CLOSEDB, ZSEQ, ZNEST, ZARG, ZCBIND, LOOPVAL, CASELESS, BYTES, WHEN, RECORD, QUOTES, DOC.
- `predscope_sabotage.out`: the 21 plants (s1..s21) run one at a time with `PREDSCOPE_SABOTAGE=sN`. Each is CAUGHT by its
  target check, with no traceback.
- The model LOWERS every program from its text. The library bodies `rx.digit`, `repeat(x, min)`, `rx.digits` and
  `when` are read out of library.md. Macros are functions over rx text, and each argument is lowered in the caller.
  Controls: python `re` on independent hand regexes. Example 1 is checked against `(?:[1-9]\d?|0)xx` and `rx.digits`
  against `\d+`, on 1,365 texts over `019x`: 0 / 0 / 0 differ. Python `re` over the codepoint range is the control for
  CLASSV and CASELESS, python `re` group values for LOOPVAL, and the record's own lines and words for RECORD, QUOTES
  and WHEN. DOC: 11 formatted lines occur verbatim in the documents.
- "Today" counts: 17 definitions scanned, 7 refused by reading (a) as stated, 2 with conditions and computed labels
  outside it. Each comes from the NAMES block of the model run above.
- Premise commands: `python3 -I scripts/pred_doc_lint.py` (start: passed 5331, failed 0; end: passed 5434, failed 0);
  `timeout 100 python3 -I -B docs/dev/lanes/predfix61_evidence/predfix61_model.py | diff - .../predfix61_model.out`
  (no diff); the same for predasc (one diff, its TAGS pin, explained in STATE AT HANDOFF).
