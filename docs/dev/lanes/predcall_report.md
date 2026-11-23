# predcall — call-prefix case 1 folded; closed-argument ruled (a); the c.A statement, the second hits example

Lane predcall (opus), branch lane/predcall cut from lane/pred-rev28 at e10799e53. Design only; docs only; no build
go. A small follow-up to lane predref; no restructuring, no re-sweep.

## STATE AT HANDOFF

OWED: none

- Commits: 72d488b0c (WIP: the brief's fold, the evidence), the merge of lane/pred-rev28 for R-1's record entry,
  and the final commit (R-1 folded, this report).
- Rulings file `docs/dev/lanes/predcall_rulings.md`: last entry applied **R-1** (closed-argument RULED (a)), read
  at every checkpoint (before the WIP commit, after the fold, before this report). R-1 replaces the brief's item 2:
  the piece written open is now `ruled 2026-11-22`.
- Premise test (all held): (a) `python3 -I scripts/pred_doc_lint.py` at the worktree root printed "pred_doc_lint:
  checks passed 6205, failed 0"; (b) `timeout 120 python3 -I docs/dev/lanes/predref_evidence/predref_model.py |
  tail -1` printed "predref_model: 8 checks, 0 failed"; (c) the record's last entry title began "2026-11-22 OWNER,
  on closed-argument".
- Final tree: the lint prints "pred_doc_lint: checks passed 6289, failed 0"; the model prints "predcall_model: 14
  checks, 0 failed"; `make -s test-plan-lint` is clean.
- predref's model on the folded documents: "predref_model: 8 checks, 1 failed (MARKS)". Its MARKS looks for
  "[core/labels/paths/call-prefix]   open call-prefix 2026-11-22", which the ruling moved. My MARKS looks for the
  piece ruled, and my PREDREF check runs predref's model and expects exactly that one red check. Its other seven
  checks stay green (its DOC included: the lines predref printed are kept).
- predbound's model is unchanged at "predbound_model: 21 checks, 1 failed (DOC)", the red that predref's report
  already names. Its PREFIXRD still refuses `B(A) & (B.d: <100)`: that is a model of reading (e), which the ruling
  rejects. It is historical evidence and was not edited.
- Not touched: plan.md, decisions.md, known_issues.md, the record, docs/dev/pred/*, reviews, skills, other lanes'
  evidence.

## RULINGS FOLDED

- call-prefix case 1, from the record entry "2026-11-22 OWNER RULING — call-prefix, case 1: the macro's name
  qualifies a label of its body; case 2: "i'd say A.d is legal there", with a doubt he is working through". His
  words: "call-prefix. case 1. yes use the macro name as shown to qualify the label. 2. i'd say A.d is legal there.
  i'm trying to figure out if B(A) would ever remove the d. its possible it changes the answer to go through [ c =
  B(A) ] as B may defined d".
  - core/labels/paths/call-prefix moved from open to `ruled 2026-11-22`. Its statement now reads: a macro's name
    qualifies the labels its call surfaces, under a binding prefix's two rules (called once, a plain read is
    legal; called more than once, a plain read is the compile error and a group question reads every call).
  - A labelled call stays legal. No program written that way was re-spelled. The library's two pieces gained one
    sentence each for the name spelling (`occurrences(/\d+/) & (occurrences.hit: <5)`, `hits(/\d+/) & (hits.hit:
    <5)`, each run). The printed lines were not touched.
  - binding-prefix's reading "(e) a MACRO's name is not a prefix for now" now reads "a MACRO's name is a prefix
    too, under the same two rules". (e) moved to `rejected:` in the details. label-reference's "Not stated" bullet
    was rewritten.
- closed-argument (R-1), from the record entry "2026-11-22 OWNER RULING — closed-argument: a (where a macro closes
  its argument's labels, the caller's `A.d` is a compile error)". His words: "closed-arguments: a".
  - The new piece core/labels/paths/closed-argument is `ruled 2026-11-22`. Its statement: for an argument that is a
    binding, the caller's `A.d` is legal exactly where `d` is visible through the call; where the macro closes the
    argument's labels it is a compile error. It is a sub-piece in all but its tag: a fifth tag word is not in the
    format, so the tag is a sibling under core/labels/paths.
  - His reason ("what would A.d mean if d no longer was visible?") is quoted with its own record title. The
    manager's (b) is under `rejected:`. Readings (a)-(c) are each marked as readings.
  - The piece prints one run line, "Visible through the call", and one line "Closed by the macro: modes: a compile
    error".
  - The compile-error index (core/diagnostics/errors) gained a row for it.
  - call-prefix case 2 is ruled through it: the bullet "NOT RULED; the owner's lean" is gone, and the line label
    "(case 2, a reading)" is now "(case 2)".
- His statement "[ c = B(A) ] does not allow c.A" (record "2026-11-22 OWNER, on closed-argument: ...") is in
  core/labels/paths. It is quoted as his words (class STATEMENT in the details), with its ground marked as a
  reading: inside B the argument is the parameter, "a binding variable not a label".
- His second hits example (record "2026-11-22 OWNER, on the helper-captures validation: "right", and a second
  example with a test inside the argument") is in lib/search/hits. That piece now has the record's two run lines,
  "inner test" and "every number", and the sentence "a test inside the argument chooses the hits; a test after
  the atomic `hits` judges them" (a reading, run). predref's lines for his first example are kept.
- His remark "nice. critical is the @assert macros to test that it does what was intended" is quoted in one bullet
  in lib/assert/assert, with no meaning folded. The bullet names the two gaps as a reading: what a search reports,
  and a label's value on a subject. The piece keeps its date 2026-11-14, since no rule changed.
- The manager's call on lib/planned/standard: the three computed uses are KEPT as quoted uses of the frozen draft's
  worked examples, with the line "written before bound-condition (2026-11-22), which refuses a computed value bound
  alone; restated when the standard library is designed". The piece is re-dated to 2026-11-22, because the base
  line carries that date and the lint allows only the status date.
- Macro types: the head's bare `year` now has the reading "under label-reference the body would name it through the
  parameter, `d.year`". The bullet adds that his example was written an hour before that ruling, and that the
  question was not asked.

## MANAGER READINGS TESTED

- (a) binding-prefix's two rules carried to a macro's name: SUPPORTED as a run of the reading.
  - TWICE: `occurrences(/\d/) SEQ ";" SEQ occurrences(/\d/) & (occurrences.hit: "9")` is refused with "label the
    part". The group question `some((occurrences.hit: "9"))` was compared against the direct "a `;` and a 9
    anywhere": 0 of 121 texts differ. `9;1` HOLDS, so the first call is read.
  - CASE1: his `hits(/\d+/) & (hits.hit: 3)` is legal and equals the labelled call (0 / 0 / 0 of 341 texts). WHOLE
    against the direct "the last number is 3" differs on 0 texts. The four printed library lines give the same
    answers when the call is read by the macro's name.
  - The model counts the call as a use of the name in its definition, as a binding's use counts.
- (b) both run lines of the call-prefix record entry, from the program text: SUPPORTED (RECORD).
  - `B(A) & (A.d: <5)` and `[c = B(A)] & (c.d: <5)` reproduce the pasted lines, with A := `/(?<d>\d)/` and B(rx)
    := `/${rx}-(?<d>\d)/`.
  - WHOLE against the direct "first digit" / "second digit under 5": 0 and 0 of 40 texts differ.
  - `(?<d>...)` in a USER macro body is fine under helper-captures. That ruling is for provided bodies; the brief's
    answer is stated as a reading, and the model reads labels only, so it is untested as to capture.
- (c) `B.d` equals `c.d` for a single call: SUPPORTED (BDOT). The two differ on 0 / 0 / 0 of 121 texts, and the
  `B.d` line equals the record's c.d line.
- (d) an argument the body uses twice (`pair(A) & (A.d: <5)`, pair(p) := `/${p},${p}/`): SUPPORTED as a run of the
  reading (PAIR). One run line, every mode, is in call-prefix: it reads the last mention.
  - WHOLE against the direct "the second digit under 5": 0 of 40 texts differ. It equals `[c = pair(A)] & (c.d:
    <5)`.
  - The reading needs "used more than once" counted in the caller's TEXT (A is written once). Counted per lowering
    of the parameter, the same program is the compile error "A is used 2 times here". This is a choice the reading
    makes, and I state it in the details.
- (e) both pasted lines of his second hits example: SUPPORTED (HITS2). They reproduce with their hit lists. WHOLE
  against the direct hits (inside: every digit 0-4; after: every number) differs on 0 and 0 of 781 texts.
- The ground of "c.A" (the argument is the parameter): SUPPORTED as a run of the reading (CA). `[c = B(A)] & (c.A.d:
  <5)` is refused: `c` passes no label `A.d`.
- R-1, the ruling as run: SUPPORTED (CLOSED).
  - Where B closes its argument (`[_ = rx]`), `A.d` and `c.d` are refused. The call itself matches as `\dxx` (0 /
    0 / 0 of 31 texts).
  - Through an open B, `A.d` is legal and its line is the record's A.d line.
  - R-1's reading (a) is SUPPORTED for `[_ = rx]`. It is UNTESTED for a `_x` part label: the loaded model keeps a
    `_x` part's groups visible by their own names.
  - Reading (b) is SUPPORTED (PAIR).
  - Reading (c) is UNTESTED: the error names the missing label, not the macro.

Not supported: none.

## ANSWERS CHANGED

None. No printed program changed its answers. The new lines are new programs, and the printed lines are unchanged:
DOC finds all 10 formatted lines verbatim, and predref's DOC stays green over its own lines.

## WHAT MOVED

- core.md:
  - core/labels/paths/call-prefix: open to ruled; statement, bullets and run lines rewritten.
  - core/labels/paths/closed-argument: new, ruled.
  - core/labels/paths: two bullets.
  - core/labels/paths/binding-prefix: the macro reading.
  - core/labels/paths/label-reference: one bullet.
  - core/operators/bindings/macro-types: the `d.year` reading.
  - core/diagnostics/errors: one row.
- library.md:
  - lib/search/occurrences: one bullet, the name spelling.
  - lib/search/hits: two bullets and two lines.
  - lib/assert/assert: one bullet.
  - lib/planned/standard: one bullet; date 2026-11-19 to 2026-11-22.
- Details:
  - Every touched piece gained a history line naming its old words verbatim where words changed.
  - call-prefix's entry: rewritten (rulings, rejected, readings, history).
  - closed-argument: a new entry.
- New lines, each run by the model:
  - call-prefix: "By the macro's name, his example", "Labelled", "Called twice, a group question reads every
    call", "A's own d, through the argument (case 2)", "d as the call surfaces it, the last mention (B's)", "By the
    macro's name", "An argument used twice by the body".
  - closed-argument: "Visible through the call".
  - lib/search/hits: "His second example, a test inside the argument", "Every number tested after the call".
  - Compile-error lines: "Called twice, a plain read" and "Closed by the macro".

## DRAFT READINGS ADDED

Each is marked "(a reading)" in the base:
- the macro's name also reaches its arguments' labels ("as the call surfaces it");
- binding-prefix's two rules applied to a macro's name;
- a group in a user macro's body is a capture, because helper-captures covers provided bodies only;
- an argument the body uses twice reads its last mention, counted once in the caller's text;
- the ground of "c.A";
- R-1's readings (a)-(c);
- the two `@assert` gaps;
- `d.year` for macro types;
- one call read by the macro's name gives the labelled call's answers (library).

## OWNER QUESTIONS LEFT

- Not ruled and not applied: zero-condition-binding, `(?<:x>...)` as a final spelling, macro variables / types (the
  `d.year` reading not asked), count-several, capture-loop-value, zero-in-loop.
- R-1's reading (c): the error message (it names the macro that closes the label). The message is the manager's
  call; nothing is asked of the owner.
- For the manager (reply either way): R-1's reading (a) covers a `_x` part label in the body. The loaded model
  cannot show that closure: predfix77's lowerer keeps a `_x` part's groups visible by their own names, against
  export statement 6. A later model should fix that before the reading is marked supported for `_x`.

## EVIDENCE AND COMMANDS

- `(cd worktrees/predcall && timeout 300 python3 -I -B docs/dev/lanes/predcall_evidence/predcall_model.py)` prints
  "predcall_model: 14 checks, 0 failed" (`predcall_model.out`). Its checks are CONTROL, CASE1, TWICE, RECORD, BDOT,
  CA, PAIR, HITS2, CLOSED, QUOTES, MARKS, SCAN, PREDREF and DOC.
- Sabotage: `PREDCALL_SABOTAGE=sN` for N in 1..13, each run alone (`predcall_sabotage.out`). Each plant is caught by
  its target check, with no traceback.
- The model loads predref's definitions unchanged (exec up to its "the checks" line), which loads predbound's.
  - Its controls are python `re` (CONTROL; the closed call as `\dxx`), direct predicates written from the meaning
    (CASE1, TWICE, RECORD, PAIR, HITS2), and the record's pasted lines, read from the record (RECORD, HITS2).
  - SCAN is predref's textual checker with its LEFT list unchanged: 221 spans are checked and 29 are left, the same
    29.
- Lint: `(cd worktrees/predcall && timeout 300 python3 -I scripts/pred_doc_lint.py | tail -1)` prints "checks
  passed 6289, failed 0". `make -s test-plan-lint` is clean.
- predref's model: `timeout 300 python3 -I -B docs/dev/lanes/predref_evidence/predref_model.py | tail -1` prints
  "predref_model: 8 checks, 1 failed (MARKS)". The red is the expected one, covered by my MARKS and PREDREF.
