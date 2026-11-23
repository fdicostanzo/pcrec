# predfix77 — review r77's ruled fixes applied to the predicate documents

Lane predfix77 (opus), branch lane/predfix77 cut from lane/pred-rev28 at dbf93362f; lane/pred-rev28 merged in once
(R-1), bringing the owner's array-in-piece ruling and his bound-condition position. Design only; no build go.

## STATE AT HANDOFF

OWED: none

- Commits: 9225a8dfe (dispositions applied, evidence model), 1ee7e8681 (merge of lane/pred-rev28, alone, R-1),
  fda5b12a6 (array-in-piece RULED (b) folded; bound-condition kept open, his position stated), and the final commit
  (R-3 marks, the filed review, evidence outputs, this report, history line).
- `scripts/pred_doc_lint.py`: failed 0 at every commit (5752 passed at fda5b12a6). `make -s test-plan-lint`: clean.
- Evidence: docs/dev/lanes/predfix77_evidence/predfix77_model.py, 20 checks, 0 failed (predfix77_model.out); 20
  plants s1..s20, each caught by its target check, no traceback (predfix77_sabotage.out).
- Review filed: docs/dev/reviews/2026-11-21-r77-predfold1121.md (STATUS: FILED, RULED + APPLIED per id) and its
  directory (critic texts, verify.md, verify_brief.md, process.md, the verifier's byname.py); index line in
  docs/dev/reviews/NOTES.md after r61's.
- Not touched (not mine): plan.md, decisions.md, known_issues.md, the record, docs/dev/pred/*, other lanes' evidence.

## DISPOSITIONS APPLIED

Where each landed, by tag (the filed review's table "RULED and applied" carries the same with the ruled text).

| id | state | where |
|---|---|---|
| A1 | applied (owner ruled (b) during the lane) | core/labels/labels-vs-captures, .../array-vs-passes, core/holes/bare-condition/nested-scope (VALUES), lib/counting/some, count, occurs |
| A2 | applied as a reading (the manager's (d)) | core/labels/labels-vs-captures/array-vs-passes |
| A3 | applied, kept OPEN (R-3) | core/holes/bare-condition/bound-condition (open); the seven readers; five definitions marked "(depends on the open bound-condition)" |
| A4 | applied | core/holes/bare-condition, core/holes/bare-condition/labels |
| A5 | applied | core/conditions/match-so-far |
| A6 | verified by a run; base reading PLAN | details of core/conditions/match-so-far and lib/search/occurrences; lines below |
| A7 | applied | lib/modifiers/any-case |
| A8 | applied | core/labels/labels-vs-captures, core/labels/export/caller-ambiguous, core/values/reads |
| A9 | applied | core/conditions/form, core/values/tuples, core/conditions/form/record-in-some (open), array-vs-passes |
| A10 | noted (PLAN, rides "only i is inherited") | core/holes/flags/in-filter details |
| A11 | applied | core/labels/labels-vs-captures/array-vs-passes |
| A12 | applied | core/holes/bare-condition/nested-scope; (c) to `rejected:` |
| D1 | applied | bare-condition/labels and nested-scope details |
| D2 | applied; "sealed definitions" principle PLAN | composed-at-point, flow, bare-condition/labels; re-dates |
| D3 | applied | core/holes/flags/in-filter, core/model/places, nested-scope |
| D4 | applied; helper-captures queued | lib/modifiers/length, lib/search/occurrences, lib/search/hits |
| D5 | applied | core/conditions/match-so-far; nested-scope details |
| D6 | applied | core/holes/bare-condition, core/model/table/group-truth |
| D7 | applied | lib/counting/some, core/holes/flags/in-filter |
| D8 | applied (spellings, RULING-10); RULING-9 noted for the manager | lib/builtin/enumerate/class-value, core/labels/flow |
| D9 | applied | predfix77_evidence/; citations re-pointed (bare-condition/labels, nested-scope, holes/class/lift-order); red re-runs below |
| D10 | applied | nested-scope run lines, core/operators/bindings details |
| D11 | the four DISAGREE items applied; the rest PLAN | lib/counting/some, core/arrays/class-order, lib/builtin/enumerate, class-value, in-filter, core/holes/labels |
| D12 | applied | core/model/table details, match-so-far/in-loop, parked/ideas/field-count, parked/ideas/label-only-group, lib/builtin/pattern, core/diagnostics/errors, bare-condition/labels, lib/counting/every-pass |
| D13 | PLAN (trigger: `within` built); not applied | — |
| GENERAL-4 | noted, stated once as a deliberate difference (a reading) | core/values/reads |

## MANAGER READINGS TESTED

The brief's five:
1. `0` as a sequence operand is the operand's match so far — SUPPORTED (SEQZERO: against `\d\d`, 0 / 0 / 0 of 121
   texts; the definition-wide rival prints a different line, below).
2. A loop inside a piece reads the piece's own previous pass (case-2 (d)) — SUPPORTED (LOOPPIECE: loop against the
   written-out form 0 / 0 / 0 of 364); the withdrawn (c) prints the different line below.
3. A sealed piece names only labels it holds — SUPPORTED as run (SEALED: case 1 and example 2 refused).
4. `chars` with a part label answers as before and makes no capture — SUPPORTED (CHARS).
5. A6, three readings of `0` inside `occurrences` — VERIFIED: three different lines (OCCZERO), below.

array-in-piece (R-1), each (a reading):
- (a) replaced by his "or A SEQ /B definition/" (R-2): the in-place SEQ form reads A's settings — the line "Written
  in place" equals the record's pasted `entire` line (ARRPIECE).
- (b) "what can be seen" includes the public labels of the parts the piece uses — SUPPORTED (ARRREAD).
- (c) the ruling covers `some`, `count`, `occurs`, `h[k]` — SUPPORTED for `some` and `h[k]` (ARRREAD); `count`,
  `occurs` by the same array, not run.
- (d) (= review A2) a group question in an `&` operand inside one definition reads that definition's settings —
  SUPPORTED as a run (ARRREAD, the line "In an `&` operand, one definition (a reading)"); the rival:
```
The operand's own stretch only (not the reading): WHOLE `7` FAILS, `7;1` FAILS, `1;7` HOLDS, `1;2` FAILS / SEARCHED `x7;1 1;7` `1;7`@5 / FIND-ALL `7;1 1;7 3;4 7 2;7;5` [`1;7`@4, `2;7;5`@14] (the same program)
```
- (e) the path form and the user's own read unchanged — UNTESTED (no line moves).

A6's three lines (OCCZERO), and SEQZERO's rival:
```
The caller's definition (the reading today): WHOLE `a5` FAILS, `x5` FAILS, `5` HOLDS / SEARCHED `-x5` `5`@2 / FIND-ALL `a5 x5` [`5 x5`@1] (`/x?/ SEQ occurrences(/\d/ SEQ (0: /\d/), min = 1)`)
The body of `occurrences`: WHOLE `a5` FAILS, `x5` HOLDS, `5` HOLDS / SEARCHED `-x5` `x5`@1 / FIND-ALL `a5 x5` [`5 x5`@1] (`/x?/ SEQ occurrences(/\d/ SEQ (0: /\d/), min = 1)`)
The hit's own text: WHOLE `a5` HOLDS, `x5` HOLDS, `5` HOLDS / SEARCHED `-x5` `-x5`@0 / FIND-ALL `a5 x5` [`a5 x5`@0] (`/x?/ SEQ occurrences(/\d/ SEQ (0: /\d/), min = 1)`)
Definition-wide `0` (not the reading): WHOLE `12` FAILS / SEARCHED `x12` FAILS / FIND-ALL `12 34 5` [] (the same program)
```
The withdrawn loop reading (LOOPPIECE), and ZEROARG's line read in B's definition (`/\d/ SEQ B((0: /\d/))`, B(rx) :=
`/${rx}xx/`), not the reading:
```
A user's loop under the withdrawn reading: WHOLE `7;3;` FAILS, `3;7;` HOLDS / SEARCHED `x7;3;` FAILS / FIND-ALL `7;3; 3;7;` [`3;7;`@5]
WHOLE `5xx` FAILS, `xx` FAILS / SEARCHED `a5xx` FAILS / FIND-ALL `5xx 55xx` []
```

## ANSWERS CHANGED

- A group question inside a BOUND piece: before, the composed array (A's settings included); now (ruled) the
  piece's own — "Bound first" WHOLE `7` FAILS where it held.
- A capture of two groups of one name under `(?J)`: PCRE's FIRST set group, not the last (DUPNAME, libpcre2-8).
- `some` on an empty array: false, now marked a reading; a record inside `some`: product of its entries (a reading).
- bare-condition: `0` in an argument is its caller's definition's (a reading), stated alike in both pieces.
- `chars`: no capture any more (part label); answers unchanged.
- every-pass: "or the loop can make no pass" — the no-pass case HOLDS in the item form (EVERYNONE).
- The bound-condition readers: no longer "read where it is used"; each is open (R-3).

## WHAT MOVED

- Removed: the lane's own draft piece core/labels/labels-vs-captures/array-in-piece (never delivered); its slug now
  on core/labels/labels-vs-captures.
- New open pieces: core/conditions/form/record-in-some, core/holes/bare-condition/bound-condition.
- Readings moved to `rejected:`: case-2 (c) (withdrawn), the SHARED and "open nested-scope" readings of
  bare-condition/labels, nested-scope residue (b), the manager's bound-condition leaning (a) (withdrawn).
- Re-dated ruled pieces: 2026-11-21 for the r77 rulings; 2026-11-22 for labels-vs-captures, array-vs-passes,
  some, count, occurs (array-in-piece).

## DRAFT READINGS ADDED

All marked "(a reading)" in the base: array order is the order made (a lookahead first); `h[k]` past the end is
absent; a `$` read inside a group question reads the last pass; a definition is a binding or a macro body; the
`&`-operand array holds both sides' settings with a plain read still ambiguous (R-2); `0` in an argument is the
caller's; `some` false on an empty array.

## OWNER QUESTIONS LEFT

- bound-condition: his position (b) awaits his confirmation after the manager's response; the five definitions
  depend on it.
- record-in-some: a record and its joint form inside a group question part.
- count-several: `count`/`occurs` of several entries.
- helper-captures: library bodies that make captures (`hit`).
- capture-loop-value; his lean "only i is inherited" (A10); the "sealed definitions" principle (D2, PLAN);
  group-truth; zero-in-loop with the A6 reading.

## EVIDENCE AND COMMANDS

- `timeout 300 python3 -I -B docs/dev/lanes/predfix77_evidence/predfix77_model.py` -> "predfix77_model: 20 checks, 0
  failed" (predfix77_model.out).
- Sabotage: `PREDFIX77_SABOTAGE=sN` for N in 1..20, each alone (predfix77_sabotage.out).
- Lint: `(cd worktrees/predfix77 && timeout 300 python3 -I scripts/pred_doc_lint.py | tail -1)`.
- Old scripts re-run on this branch (D9; red, cited checks re-pointed to predfix77's):
  - predscope_model.py: "20 checks, 2 failed (CLOSEDB, DOC)" — CLOSEDB prints the composed reading the ruling
    refuses; DOC misses 3 nested-scope lines and 1 bare-condition line.
  - predfix61_model.py: "15 checks, 1 failed (DOC)" — 7 lines missing (1 bare-condition/labels, 4 bare-nested-scope, 2
    class-hole-order).
  - predasc_model.py: "24 checks, 1 failed: TAGS" — "class-order slugs ['class-order', 'class-positions',
    'quantified-order'] ; class-value still open: True".
  - predarr_model.py: stops with `AssertionError: `chars := (/.*?/)`` — the library's `chars` body was re-spelled
    (D4); its length lines are now checked by predfix77 CHARS.
- libpcre2-8 10.46 through docs/dev/lanes/rxmodel_evidence/pcre2h.py (library only, D181).
