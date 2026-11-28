# Lane predfix113: review r113 applied to the predicate documents (DESIGN)

Branch lane/predfix113, cut from lane/pred-rev28 at 8fa0108f9. This is design only: nothing under src/, cli/, lib/,
memfn/, tests/ or scripts/ was edited. The findings are review r113 of the fold predfold1128, as RULED by the
predicate manager. The review is filed at docs/dev/reviews/2026-11-27-r113-predfold1128.md, with the critics' files
and the dispositions beside it. No owner ruling is folded here. Nothing in NOT RULED was applied as ruled:
no-path-through-argument, sent-over-body-label, forwarded-place, list-over-label, reference-example-checked and the
call mark for a reference all stay as the record leaves them.

## STATE AT HANDOFF

- OWED: none.
- The rulings file `docs/dev/lanes/predfix113_rulings.md` was re-read before each commit, before each run over two
  minutes and before this report. It stayed empty, so no entry was applied (last entry applied: none).
- Branch tip: the commit carrying this report. The document fixes are in dd4292798; the model, the declarations and
  the filed review are in 162735d9c; the committed runs and this report are in the tip.
- pred_doc_lint: `pred_doc_lint: checks passed 10603, failed 0`. `make -s test-plan-lint`: green.
- Model: `predfix113_model: 11 checks, 0 failed` (full, SUCCESSOR113 included: 22 models read, 91 reds, all as declared). Sabotage: `PASS PLANTS113: 14 plants, caught 14` (one or more per check; that run's last line `predfix113_model: 12 checks, 0 failed`).
- Premise, at 8fa0108f9 before any edit: `pred_doc_lint: checks passed 10528, failed 0`, and predfold1128 in full
  gave `predfold1128_model: 16 checks, 0 failed` (SUCCESSOR128: 21 models, 88 reds, all as declared). Its PASS/FAIL
  lines were identical to the committed model.out.
- Strong-lean marker sites: 40 (core.md 37, library.md 3). The start had 38. RULING-4 dropped 2 and added 4. The
  phrase is unchanged, "(the owner's strong lean, entailed by carve-out-reading and caller-label-export; to be
  confirmed)".
- Owner questions open: 7, listed under OWNER QUESTIONS LEFT. Two of them are new: label-above-call (EXAMPLES-1) and
  the two named-list cells that go with reference-example-checked.

## FINDINGS APPLIED

Each finding below is applied as ruled in `dispositions.md`. The document commit is dd4292798, and the check that
verifies each one is named.

- **RULING-1** (FIX-NOW): "own" is restored in param-reference line 3, so it reads "by the caller's own path rules".
  This is fixed in the quote in core/operators/bindings/reference-call and in that piece's statement. In
  core/operators/bindings/reference, the quote of lines 1, 2 and 4 is now closed after line 2 and reopened at line 4
  (`..."; line 4: "4. **Nothing inferred.** ..."`). Checked by QUOTES113 (each quote is a verbatim substring of the
  record at 8fa0108f9) and STALE113.
- **RULING-2** (FIX-NOW): the withdrawn meaning is re-worded to the door at two sites. In core/labels/export/named-list:
  "The list is the door on the place (core/labels/rule/argument-door), not labels of the body's own: it passes the
  named label through the call, an alias of the argument's". In lib/convention/argument-labels: "the list on it ...
  is the door ...: it passes every label the argument exports through the call". export-list gains one sentence: its
  "same label, the last mention" bullet is "for a part. On a parameter's place the list is the door
  (core/labels/rule/argument-door), not labels of the body's own." Checked by TEXT113 and STALE113.
- **RULING-3** (FIX-NOW, the document half): the core bullet "Places and then reads, as today" is marked "a marked
  reading, the fold's, pending the owner question reference-example-checked". The example the owner was shown is
  named and today's rules refuse it. Both readings are RUN and printed:
  - The fold's reading is the line "Placed, then read by the parameter's name", a compile error.
  - The other reading, a NEW rule, gives `checked(isodate)` WHOLE `2024-02-29` HOLDS, `2150-01-01` FAILS / SEARCHED
    `x 2150-01-01 1999-12-31` `1999-12-31`@13 / FIND-ALL `2024-02-29 2150-01-01 1999-12-31` [`2024-02-29`@0,
    `1999-12-31`@22].

  The macro-types reading `d.year` is marked "replaced by param-reference line 2". The base files use "replaced"
  because lint L6 bars the word "superseded" there. Checked by OPEN113 (CHECKED113 both ways), TEXT113 and STALE113.
- **RULING-4** (FIX-NOW): the marker is dropped at "Two binding levels, the sender's label" (`X.a.h`) and at "Through a
  call, the sender's name" (`A.h`).
  - The marker is added at four sites: the caller-label bullet "In the sender's own text ..." (also marked "a
    reading, the fold's"), the kinds table's shorthand-row skippable cell, the caller-label row's outside cell (where
    `B.a.h` is now "a reading"), and the new EXAMPLES-1 line.
  - "Through the call's label" is re-worded: "read `Y.a.h` (ruled, caller-label-export; its ground the strong lean, to
    be confirmed); `Y.c.h` alike" followed by the marker. `Y.c.h` is unruled and depends on the lean, so it keeps the
    mark.
  - The count is 38 - 2 + 4 = 40. MARK113 derives the expected number from the start commit's count and the ruled
    site lists, and checks each site.
- **RULING-5** (FIX-NOW): three marks.
  - The nested-scope statement now ends "a parameter's labels are not its to name, but a reference's listed ones"
    (exactly 200 characters, the cap). The siblings in core/labels/paths and core/labels/paths/call-prefix carry the
    same exception.
  - label-kinds' `rejected:` item is marked "REVISED by param-reference" in core_details.md.
  - parked/ideas/reference-kind is narrowed to the label-mark form `A(a:, B) := B & (a: 5)`, with a new trigger.
    Checked by TEXT113 and STALE113.
- **RULING-6** (FIX-NOW + ASKED + open cells): three "Lacking it" lines are printed in core/labels/export/named-list:
  behind an underscore label `[_w = ..]`, behind an underscore group `(?<_g>(?<h>\d))`, and a part used alone
  `As := A SEQ "!"`. Each is the use error naming `h` and `(=h)`. Rows 1 and 8 are printed as MARKED readings with
  both readings RUN (OWNER QUESTIONS LEFT). The remaining rows are listed in the details entries as open cells, each
  with its trigger:
  - core/operators/bindings/reference: a reference beside a label parameter, a looped label, a group question, the
    wildcard head forms, an export from a reference call.
  - core/labels/export/named-list: the renamed list's use error, a reference argument's gate or wall, and a plain
    parameter with `(=)`.

  Checked by ERRSWEEP113, OPEN113 (ROWS113) and TEXT113.
- **RULING-7** (PLAN): a new parked piece, parked/ideas/label-interface "A declared label interface". It lists the
  members, the lean restated as "an undeclared interface is empty", and the unlocks, each with its trigger. Its
  details entry files it as a unification candidate. No rule changes. Checked by TEXT113.
- **RULING-8** (FIX-NOW): two statements are marked as the manager's call under transform-export: occurrences' (its
  body "(its list the manager's call, transform-export)") and hits' body bullet. Two reading lines are printed, both
  RUN:
  - "Through the door, `hit` skipped" (`hits(/a(?<g>x)?/) & (hits.g: "x")`).
  - "The argument's group, through the door" (`occurrences(/(?<n>\d+)/) & (occurrences.n: "3")`).

  Their answers equal the printed `.hit.g` and `.hit.n` lines at 8fa0108f9 (HAND113). To keep the occurrences piece
  within its 40-line cap, its `min = n` bullet was joined to the bullet before it.
- **EXAMPLES-1** (FIX-NOW + ASKED): `k.a.h` over `[k = [c = B([a = A])]]` is printed as the marked line "A label above
  the call's label", a compile error. The lean read literally says the path passes `c` and the place. The other
  reading is RUN in the bullet: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx`
  [`3xx`@0, `4xx`@8]. The model follows the literal reading, which is LIT113. CANARY113 shows predfold1128's boundary
  reads it legal, while `Y.a.h` and `X.a.h` stay legal both ways.
- **EXAMPLES-2** (FIX-NOW): "His remedy" is replaced by the separating witness, and its error twin is printed:
  - "Without his remedy": `Bo(rx) := /${[q = /(?<d>\d)/]}-${[(=) = rx]}/`, a compile error naming `Bo.q.d`.
  - "His remedy": `[(=, _ = d) = rx]`, legal: WHOLE `3-7` HOLDS, `7-3` FAILS, `3-3` HOLDS, `7-7` FAILS.

  The piece's bullet says where the remedy separates. Checked by the SWEEP113 declaration (GONE113), HAND113 and
  ERRSWEEP113.
- **EXAMPLES-3** (FIX-NOW): four refusals now name the way in. `X.c.h` names "Y labels the argument and X reads
  `X.a.h`, the next line". `Y.c.a.h` names "read `Y.a.h`". "A list above the body's label" names
  `[p = [(=) = rx]]`. "At the weekday's own spot" names "write the call as a filter over the whole". Checked by
  TEXT113.
- **EXAMPLES-4** (FIX-NOW): one sentence in reference-call. Line 1's head `weekday_of((=year, =month, =day))` is the
  owner's placeholder example of a declared reference, and the native is planned over three values
  (lib/planned/standard), which is the shape the program calls. Checked by TEXT113.
- **EXAMPLES-5** (FIX-NOW): argument-place's "What moved" list now names nested-scope's line "Example 1, the spot
  labelled". It also says `X.c.h` is a different program (Y labels its argument), not a re-spelling. Checked by
  TEXT113.
- **FREEZE DRIFT** (accepted as mapped): no document sentence prints the withdrawn `pub.A.h`-written-out contrast as
  legal. Every `pub.A.h` site was grepped: the written-out form is printed only as a compile error, and the
  `pub := [=A]` sites have no call.

## MANAGER READINGS TESTED

- The ruled model behaviour for EXAMPLES-1, "the lean read literally (the path goes through the place: an error)",
  is SUPPORTED as run: LIT113 refuses `k.a.h` and keeps `Y.a.h` and `X.a.h` (caller-label-export) legal (CANARY113).
  SWEEP113 shows that no printed line moved with it.
- The record's finding that the manager's telling was false is SUPPORTED again. `checked(B) := B & (B.year: < 2100)`
  is refused by the model ("names a label it does not hold"), as predfold1128 found. Line 4's other reading is RUN
  (OPEN113).
- RULING-8's implied reads, that `hits.g` and `occurrences.n` are legal under the door and one-path and read the last
  hit's label, are SUPPORTED as run. Their answers equal the printed `.hit` lines (HAND113).
- EXAMPLES-2's claim that the witness separates is SUPPORTED. Without the remedy, `Bo.d` sees two `d`; with it, the
  read is legal and gives the body's `d` (a hand regex, `[0-4]-\d`).
- The record's "38 MARKED sites" is SUPPORTED: MARK113 counts 38 at 8fa0108f9.
- RULING-6's underscore-group cell ("each the use error, `(?<_h>..)` too (export 3)") is SUPPORTED only after a model
  fix. predfold1128's `_exports128` ignores an underscore group, so `N(Au)` ran LEGAL there. EXP113 fixes the model,
  and predfold1128's ERRSWEEP128 red is declared.

## ANSWERS CHANGED

- No printed line's answers changed. SWEEP113 compared every three-mode line against the start commit's lines under
  the control and found 0 moved and 0 gone. The one declared key is "His remedy"'s old program, replaced with the
  same answers.
- Two model answers changed. Neither was ever printed before this lane:
  - `[k = [c = B([a = A])]] & (k.a.h: <5)`: legal under predfold1128, a compile error under LIT113 (EXAMPLES-1, a
    marked reading).
  - `N(Au) & (N.h: <5)` with Au := `/(?<_g>(?<h>\d))/`: legal under predfold1128, the use error under EXP113
    (export statement 3).

## WHAT MOVED

- There are 17 new printed lines (SPECLINES113: 5 three-mode, 12 compile-error, all run). Four bullets carry a
  reading's answers, each an OPEN113 run printed verbatim.
  - Added: "A label above the call's label", "Without his remedy", "His remedy" (re-written), the three "Lacking it"
    lines, "The body reads the named label", "Two labelled parts", "Placed, then read by the parameter's name",
    "Through the door, `hit` skipped" and "The argument's group, through the door".
  - Re-worded (the marker or the message only): "Two binding levels, through the call's label", "Two binding levels,
    the sender's label", "Through a call, the sender's name", "Through the call's label", "A list above the body's
    label" and "At the weekday's own spot".
- The statements re-written are nested-scope, reference-call, occurrences and parked/ideas/reference-kind (now named
  "A reference by the label mark, for users"). Each old text is kept verbatim in its details entry's history.
- There is one new parked piece, parked/ideas/label-interface.
- Every touched piece's details entry carries a history line naming the finding.
- predfold1128 now has three declared reds (ERRSWEEP128, SPECLINES128, SUCCESSOR128). 19 older keys moved, all because
  of this lane's added lines: older engines predate the rules those lines print. Each is declared in
  `predfix113_succ_decl.tsv` with its own FAIL line text. No older red turned green and none is a traceback.

## DRAFT READINGS ADDED

These are marked in the documents and are not owner rulings:

- The caller-label bullet "In the sender's own text the call's label and the macro's name are paths through the place
  alike" (`pub.A.h` written out, `B.a.h`) is now marked "a reading, the fold's". It was printed unmarked inside a
  ruled piece.
- EXAMPLES-1's printed reading: a label above the call's label in the sender's own text is a compile error.
- RULING-6 row 1's printed reading: the body reading its named list's label bare is a compile error by nested-scope.
- RULING-6 row 8's printed reading: two labelled parts holding `h` give one-path's use error, naming both `a.h` and
  `b.h`.
- RULING-8's two reading lines (`hits.g`, `occurrences.n`).
- The open cells' proposed readings (UNTESTED, each with its trigger) in the reference and named-list details entries.
- The refusal wordings added under EXAMPLES-3 are the manager's (D26).

## OWNER QUESTIONS LEFT

Every question now open:

1. **reference-example-checked** (new in the record; not yet asked). Does param-reference line 4's second sentence
   stand as a NEW rule (a body may read the labels of a parameter it places, by the parameter's name), or fall?
   - Program: `checked(B) := B & (B.year: < 2100)`, `checked(isodate)`.
   - Both readings are printed in core/operators/bindings/reference: the bullet "Places and then reads, as today"
     (the other reading's answers) and the line "Placed, then read by the parameter's name".
   - Asked with it, RULING-6 row 1, **named-list-body-read**: `N2(rx) := /${[(=h) = rx]}/ & (h: <5)`, `N2(A)`. Both
     readings are in core/labels/export/named-list: the bullet "Two cells" and the line "The body reads the named
     label".
   - Asked with it, RULING-6 row 8, **named-list-two-parts**: `N([a = P] SEQ [b = Q]) & (N.h: <5)`, P :=
     `/(?<h>\d)/`, Q := `/,(?<h>\d)/`. Both readings are in the same bullet and the line "Two labelled parts".
2. **label-above-call** (EXAMPLES-1, to be asked with the strong lean's confirmation): `[k = [c = B([a = A])]] &
   (k.a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`. Both readings are in core/labels/rule/caller-label:
   the bullet "A label above the call's label ..." and the line "A label above the call's label".
3. **no-path-through-argument** (the strong lean, still marked, never asked as a ruling). Its home is
   core/labels/rule/argument-place, and it is marked at 40 sites.
4. **list-over-label**: `B1(A) & (B1.h: <5)`, B1(rx) := `/${[(=) = [p = rx]]}xx/`. Both readings are in
   core/labels/rule/list-over-label (unchanged by this lane except its message).
5. **forwarded-place**: `Mx(A) & (Mx.h: <5)`. Both readings are in core/labels/rule/forwarded-place (unchanged).
6. **sent-over-body-label**: `Rs(x:, A) & (x.h: <5)`. Both readings are in core/labels/rule/sent-over-body-label
   (unchanged).
7. **The call mark for a reference** (left for later, told to the owner; not a question yet): no program; recorded in
   core/operators/bindings/reference.

## EVIDENCE AND COMMANDS

- Evidence: `docs/dev/lanes/predfix113_evidence/` (CLAUDE.md, `predfix113_model.py`, `predfix113_model.out`,
  `predfix113_sabotage.out`, `predfix113_succ_decl.tsv`).
- Run from the worktree root, with an existing EMPTY scratch directory:
  `PREDFIX113_SUCCDIR=DIR timeout 6000 python3 -I -B docs/dev/lanes/predfix113_evidence/predfix113_model.py`.
  The committed `predfix113_model.out` is that run at the delivered documents.
- Sabotage: `PREDFIX113_SABOTAGE=all PREDFIX113_LIGHT=1 PREDFIX113_READDUMP=1 PREDFIX113_SUCCDIR=DIR timeout 6000
  python3 -I -B docs/dev/lanes/predfix113_evidence/predfix113_model.py`. This is one LIGHT subprocess per plant; s14
  reads DIR. The output is `predfix113_sabotage.out`.
- The model uses python3 `-I` `re` only (and `datetime` through the loaded weekday stand-in), in a single process
  except for the successor and plant subprocesses. It reads git only by the pinned commit 8fa0108f9. The one older
  model that reads a branch by name, predfold1123 (`lane/pred-rev28:`), is noted in CLAUDE.md.
- Lint: `(cd <worktree> && timeout 300 python3 -I scripts/pred_doc_lint.py | tail -1)`, and `make -s test-plan-lint`.
- No box queue, suite or timing was used.
