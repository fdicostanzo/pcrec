# Lane predfix82 report: review r82's ruled fixes applied to the predicate documents

Lane predfix82 (opus), branch lane/predfix82, cut from lane/pred-rev28 at 0f6a556bc. It applies the dispositions of
the record entry "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record
entries (no owner words)" to docs/design/predicates/{core,library,parked}{,_details}.md, writes one evidence model,
and files the review. Design only; no build, no suite, no timing.

## STATE AT HANDOFF

OWED: none

- Last record entry applied: "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections
  of record entries (no owner words)". No later record entry, and no merge of lane/pred-rev28 during the lane.
- Rulings file docs/dev/lanes/predfix82_rulings.md: empty at every checkpoint (before each commit, before the
  sabotage runs, before this report). No R-n applied.
- pred_doc_lint: checks passed 6428, failed 0 (WARN L7 soft caps on core.md, library.md and parked.md, as before).
- Premise checks at the start all passed: the lint at failed 0, the record's last entry the ruling entry, and the six
  earlier models' reds as the review describes them (EVID-1).
- Stop rule: no contradiction found between the record, the brief and the dispositions.

## DISPOSITIONS APPLIED

Each id below is applied, planned or noted. The tags are where it landed. The filed review also carries an APPLIED
note per id.

| id | state | landed |
|---|---|---|
| ANS-1 | applied | core/labels/paths/call-prefix ("A's own `d`" marked a reading on the run lines he was shown); core/labels/paths/closed-argument; new open piece core/labels/paths/two-sources (open two-sources, four run lines); model TWOSRC |
| ANS-2 (a) | applied | core/labels/paths/binding-prefix, core/labels/flow (marked a reading); new open piece core/labels/paths/one-use-read (open idiom-confirm, his label-flow point 4 words and today's words) |
| ANS-2 (b) | applied | core/labels/paths ("for one use") |
| ANS-2 (c) | applied | core/labels/paths/binding-prefix (a reading, run: the line "A use inside another used binding"); model NESTED |
| ANS-2 (d) | applied | core/labels/paths/binding-prefix (a reading, run: the line "Counted in the text"); model TEXTUSES |
| ANS-3 | applied | core/conditions/form/value-left ("outside a group question"; a reading; the line "Inside a group question"); core/diagnostics/errors row; model VALUEGQ |
| ANS-4 | applied | core/labels/paths (the rule as a reading with its ground; `c.A.d` names it); core/labels/paths/closed-argument (`c.d`); core/diagnostics/errors row; model PATHS, CLOSEDX |
| ANS-5 | applied | core/labels/export statement 3 (the lines "Statement 3, a path", "Statement 6"); core/labels/export/flat-read-outside (`pair.b.x`, its line); model PATHS |
| ANS-6 | applied | core/labels/paths/binding-prefix (the line "The index through sequenced uses"); core/diagnostics/errors row; lib/search/occurrences; model INDEX |
| EVID-1 | applied | model SUCCESSOR (six earlier models re-run, last line read, each red named superseded); the new model exits non-zero on a failed check |
| EVID-2 | applied | engine CLOSE fix; model CLOSEDX; core/labels/paths/closed-argument (the line "Closed by a `_` part label") |
| EVID-3 | applied | engine AND and AMBIG fixes; model SECOND, AMBIG; the lines "One use, the second operand" and "Across `&`" |
| EVID-4 | applied (limit stated) + planned (engine fix) | the new model's header and its CLAUDE.md; model NULLABLE. Not in the EARLIER models' headers: those are lane files, historical, and not mine to edit |
| EVID-5 | applied | the contrast pair in core/labels/paths/binding-prefix; model CONTRAST; quantifier-order plant s1 (ORDER) |
| DES-1 | applied + planned (target table) | core/holes/bare-condition/bound-condition (sentence and line); core/values/computed-labels; errors row; model BOUNDSET |
| DES-2 | applied | core/patterns/literals (re-dated 2026-11-22) |
| DES-3 | applied | core/conditions/form; errors row; model GAPS |
| DES-4 | planned | no change |
| DES-5 | planned | no change |
| DES-6 | applied | core/labels/paths/call-prefix (the line "A part label named like the macro"); core/labels/paths/binding-prefix; model HIDE |
| RULING-3 | applied | core/labels/paths/label-reference |
| RULING-4 | applied | core/holes/bare-condition/zero-binding (re-lettered (a), (b), (c)) |
| RULING-5 | applied | core/conditions/form (the record note is CORRECTION 2) |
| RULING-8 | applied | (a) the macro-types reading in core_details.md and core/operators/bindings/macro-types; (b), (c) core/labels/label-only-group; (d) core/conditions/form/value-left |
| RULING-9 | applied (as the owner question) | core/labels/paths/label-reference; core/labels/paths/one-use-read |
| GENERAL-5 | applied | core/holes/bare-condition/nested-scope |
| GENERAL-7 / EXAMPLES-4 | applied | lib/search/occurrences |
| GENERAL-8 | applied | core/values/computed-labels reduced to its in-a-set fact (not merged: no restructuring); three `needs:` retargeted (lib/modifiers/length, lib/modifiers/month-numbered, core/values/metadata); the details reading |
| GENERAL-11 / FIXIND-8 | applied | parked/ideas/label-parameter, parked/ideas/restricted-parameter (superseded, stated), parked/ideas/label-hygiene (partly overtaken) |
| FIXIND-1 | applied | parked/ideas/user-doc-traps (items 13, 15, 21, 25, 30) |
| FIXIND-2 | applied | lib/search/occurrences (to `rejected:`) |
| FIXIND-3 | applied | lib/search/occurrences, lib/search/hits, core/values/tuples, parked/ideas/empty-value, parked/ideas/kleene-completion (details readings marked as printed before, today's spelling named) |
| FIXIND-4 | applied | core/labels/export, core/labels/export/flat-read-outside (details) |
| FIXIND-5 | applied | core/holes/bare-condition (details) |
| FIXIND-6 | applied | lib/strings/join (marked stale unless ruled an exception) |
| FIXIND-7 | applied | core/labels/labels-vs-captures |
| FIXIND-9 | applied | core/operators/statements, lib/search/within |
| EXAMPLES-2 | applied | core/diagnostics/errors |
| library.md size | planned | noted |
| the three lessons | noted | for main, as proposed skill edits (skills are not this lane's to edit) |

Every changed piece has a history line in its details entry naming the review id and the ruling entry. The pieces
re-dated to 2026-11-22: core/patterns/literals, core/operators/statements, core/diagnostics/errors,
lib/search/within, lib/strings/join, and the three parked pieces.

## MANAGER READINGS TESTED

| reading | verdict | check (plant) |
|---|---|---|
| ANS-2c: the prefix reaches only the uses written in the referencing definition | supported | NESTED (s6) |
| ANS-2d: uses counted in the text, before macros expand | supported | TEXTUSES (s5) |
| ANS-3: a value entry inside a group question is a compile error | supported (the two forms part there: on `7;1;`, `some((h: "7"))` HOLDS and `($h: "7")` FAILS) | VALUEGQ (s10) |
| ANS-4: a label not visible through its source is a compile error, a typo'd path too | supported as run | PATHS, CLOSEDX (s8, s2) |
| ANS-5: a source is a path of names | supported (`pub.a.h`, `pair.b.x`, `days.w.index`, `X.D.h`) | PATHS (s8) |
| ANS-6: the index through `&`-joined uses is an error; through sequenced uses it is in text order | supported | INDEX (s9) |
| DES-1: a set that reads a label, bound alone, is an error | supported | BOUNDSET (s12) |
| DES-3: the three gaps are compile errors | supported | GAPS (s19) |
| DES-6: the part label wins, with the warning | supported | HIDE (s11) |

All nine readings are supported, so no reading is unsupported or untestable. Each verdict is from the fixed engine,
which builds every regex mechanically from the program text. The controls are direct predicates on the texts and
python `re`.

## ANSWERS CHANGED

- No printed three-mode line changed its answer. SWEEP ran all 220 printed lines under the old engine and the fixed
  one. The fixed engine reproduces every line the old one did, and 8 more: the new lines and lines the old engine
  refused.
- Two readings are new and print no answer line: a value entry inside a group question is a compile error (before,
  the text said nothing and the old model crashed), and a set reading a label, bound alone, is a compile error.
- One line was re-lettered, with its answer unchanged: zero-binding's sealed candidate went from (b) to (c).

## WHAT MOVED

- Statements changed: core/values/computed-labels (reduced to its in-a-set fact; the old statement is quoted in its
  history) and core/holes/bare-condition/zero-binding (three candidates).
- Two pieces are new: core/labels/paths/two-sources and core/labels/paths/one-use-read, both open.
- One details reading moved to `rejected:`, in lib/search/occurrences.
- Nothing was moved between files.

## DRAFT READINGS ADDED

These are marked readings, not rulings:
- core/labels/paths: the visibility rule (ANS-4).
- core/labels/export: the path rule (ANS-5).
- core/labels/paths/binding-prefix: text counting, the reach of a prefix, the index, and the part label that wins.
- core/conditions/form: the three gaps, and `$h` with `h` named twice.
- core/conditions/form/value-left: the group-question error.
- core/holes/bare-condition/bound-condition: the target rule.
- lib/search/occurrences: a group question across `&` reads every call. This one is not run separately: the bare-name
  form is run, in the line "Across `&`".

## OWNER QUESTIONS LEFT

- two-sources (core/labels/paths/two-sources): when a name has two sources, does the read reach the last mention or
  the source written here? Both shapes are printed with the run lines for `7-3` and `1,7` under each candidate.
- idiom-confirm (core/labels/paths/one-use-read): is the one-use plain read `A.h` legal, and with it
  `isodate & (isodate.year: < 2100)`?
- Still unruled and not touched here: zero-condition-binding; `(?<:x>...)` as a final spelling; macro variables and
  macro types; count-several; capture-loop-value; zero-in-loop.
- FIXIND-6 leaves a question for the manager: is join an exception to "[ c = B(A) ] does not allow c.A"?

## EVIDENCE AND COMMANDS

- Model: docs/dev/lanes/predfix82_evidence/predfix82_model.py. It loads predcall's model unchanged and replaces the
  named engine parts listed in its header. Run: `timeout 600 python3 -I -B
  docs/dev/lanes/predfix82_evidence/predfix82_model.py`. It takes about 10 s and exits 1 on a failed check.
- The clean run is `predfix82_model.out`, which ends "predfix82_model: 22 checks, 0 failed".
- Plants: `PREDFIX82_SABOTAGE=s1` .. `s21`, each run alone. Each is caught by its target check, with no traceback, in
  `predfix82_sabotage.out`.
- SUCCESSOR names these earlier-model reds as superseded:
  - predbound: DOC.
  - predref: SCAN and MARKS.
  - predcall: SCAN and PREDREF.
  - predfix77 and predarr: a traceback, from the `chars` body reader.
  - predscope: NAMES, CLOSEDB and DOC.
- The nullable-body limit is stated in the model header and in the evidence CLAUDE.md. It was verified by
  `grep -n 'KNOWN LIMIT (EVID-4' docs/dev/lanes/predfix82_evidence/{predfix82_model.py,CLAUDE.md}` (both files hit).
- Lint: `timeout 120 python3 -I scripts/pred_doc_lint.py` gives failed 0. Then `make -s test-plan-lint` and
  `scripts/lanecheck` (below).
- Review filed: docs/dev/reviews/2026-11-22-r82-predfold1122.md with its directory (the critic texts, verify.md,
  coordinator_evidence_rerun.md, process.md) and its index line in docs/dev/reviews/NOTES.md.
