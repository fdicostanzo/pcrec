# Lane predfold1123 — the 2026-11-22 late and 2026-11-23 rulings folded into the predicate documents

Branch `lane/predfold1123`, cut from `lane/pred-rev28` at e420369c5; `lane/pred-rev28` NOT merged in. Design only:
the six predicate documents `docs/design/predicates/{core,library,parked}{,_details}.md` and the evidence in
`docs/dev/lanes/predfold1123_evidence/`. Nothing under src/, cli/, lib/, memfn/, tests/, scripts/ touched; the record,
docs/dev/pred/, plan.md, decisions.md, known_issues.md and docs/dev/reviews/ were not edited. Task: fold every RULING
of the record from its 2026-11-22 late entries through "binding-fixed"; R1 added zero-open.

## STATE AT HANDOFF

- STATE: done.
OWED: none
- Branch tip: the commit carrying this report (WIP predecessors from 69322b46a on).
- Rulings file `docs/dev/lanes/predfold1123_rulings.md`: R1 only (zero-open), applied; re-read before each commit,
  each run over two minutes and this report.
- `pred_doc_lint: checks passed 7841, failed 0`; `make -s test-plan-lint` clean (`checks failed: 0`).
- The model: `predfold1123_model: 18 checks, 0 failed`; `predfold1123_sabotage: 24 plants, 0 not caught (each plant turned its target check FAIL, no traceback)`.
- FOR THE MERGE: zero-open's two entries exist only on `lane/pred-rev28` (after this lane's cut). They are cited in
  `history:` lines only (L4 needs a title present in this worktree's record), and quoted against that branch's
  record by QUOTES. Once the record carries them, the four pieces they touch (core/conditions/match-so-far,
  core/values/reads, core/diagnostics/warnings, lib/structural/capture) can take them as `rulings:` items.
  core/values/reads keeps its 2026-11-22 date for the same reason.

## RULINGS FOLDED

Each with its piece (tag) and the record title cited in `rulings:`:
- capture-export (1 no, 2 yes) — core/labels/export/capture-export, ruled 2026-11-22.
- capture-twice (a) — closes core/labels/export/caller-ambiguous (ruled 2026-11-23) and lib/structural/capture.
- zero-condition-binding: an error, reconsider later — core/holes/bare-condition/zero-binding, ruled 2026-11-22;
  lines (a), (c) to `rejected:`.
- argument-label: yes; argument-export (the reading taken, "this aligns") — new core/labels/export/arguments;
  argument-default narrowed, its readings (a) and (b) WITHDRAWN; two-sources ruled (first shape re-settled; second
  shape closed on label-reference); call-prefix, closed-argument, holes/labels, atomic, rx.repeat, hits re-said.
- approach 1 ("tentatively"), label-parameter-omitted, -default, label-kinds, label-in-argument, label-forward —
  core/operators/bindings/label-variables (still under construction) and five new siblings: label-omitted,
  label-default, label-kinds, label-in-argument, label-forward. `:` in a head now marks a label parameter.
- optional-label: yes; optional-place (before the colon; `?:` his lean) — new core/conditions/form/optional-entry;
  the capture request's shape (by the statement he answered) — lib/structural/capture ruled 2026-11-23.
- capture-name (a), array-capture: yes (capture-as-pcre dropped; capture-loop-value the label) —
  lib/structural/capture, lib/structural/capture/add-on (array request ruled, unbuilt: under construction).
- capture-negated, broadened — new core/filters/negation/effects.
- zero-in-loop (b) — core/conditions/match-so-far/in-loop ruled; line (a) to `rejected:`.
- binding-fixed: yes — new principle core/principles/binding-fixed; nested-scope's "(to be confirmed)" closed.
- zero-open (R1): `0` read open; never absent (`pcrec.default.unused`); no settings (group question, index:
  compile errors); `$0` legal; a request only on a complete `0` — core/conditions/match-so-far, core/values/reads,
  core/diagnostics/warnings and errors, lib/structural/capture, lib/counting/some.
- review r84 items handed to this lane: A4, A7 (the argument-labels sentence moved to core/labels/export/arguments),
  C3, C4, C5, C8 (label-reference, one-use-read), D2 — each in its piece's `history:`.

## MANAGER READINGS TESTED

R1's readings:
- (a) "complete" is the `&` case and a condition written last in its definition — SUPPORTED (ZEROOPEN: a request
  on `0` written last legal, on an open `0` refused; as modelled).
- (b) the warning is `pcrec.default.unused` — SUPPORTED (ZEROOPEN: `(0 ?: ..)` draws it; the name is the
  manager's call).
- (c) `$0` in a value hole follows the value-hole rules — SUPPORTED (ZEROOPEN: `/\w+${$0}/` equals python `re`
  `(\w+)\1` in every mode over 8 texts).
The range's readings run by READINGS (17, all agree with the record's statement): two-sources second shape (b);
label-parameter-twice (plain read, group question, index; across `&` ambiguous); label-omitted (a); label-kinds
(a), (b); label-in-argument (c); argument-export; optional-label `NOT (h ?: S)` = `(h: !S)`; optional-place (b);
value-left (d) ("Frank"); label-forward across `|`; label-forward q1, q2; JSON picture q1; the string `"3"` and
number `3` alike; capture-twice; zero-in-loop — all SUPPORTED.
Others: effect-in-guard (a request in `when`'s test refused through the body read from library.md) — SUPPORTED;
the label set tighter than `|` — SUPPORTED as modelled (ARGSHAPES: the two spellings answer differently);
optional-entry (a) joint/value — SUPPORTED; (d) a default with `?:` warns — SUPPORTED; (b) `h+`/`h*` not forms and
(e) `?:` one token — UNTESTABLE (spellings); zero-binding (a) and in-place — SUPPORTED, as an argument UNTESTED;
capture-name (a)-(c), array-capture (a), (b) — UNTESTED / UNTESTABLE (not modelled, a build point).
No reading was refuted; none was dropped for that reason.

## ANSWERS CHANGED

- `/(?<h>\d)/ SEQ A & (h: <5)`: WHOLE `1,7` FAILS → HOLDS, `7,1` HOLDS → FAILS (two-sources: the bare `h` is the
  one written here; the old line (a) is in `rejected:`).
- Legal now, compile errors before: `B([a = A]) & (a.d: <100)`, `B(/(?<d>\d)/) & (d: <5)`,
  `rx.repeat([a = rx.digit], min = 1)` then `a`, `hits(/a(?<g>x)?/) & (g: "x")`, `atomic([ab = (B | A)])` then
  `ab.l` (argument-label).
- `/\d${c}x/`, c := `(0: rx.digit)`: both candidate lines gone; `c := (0: 5)` is a compile error at `c`.
- `capture("d", /\d+/)`: the two-argument wrapper's line to `rejected:`; the request replaces it.
- Re-said, no printed answer moved: peek and occurrences (a group written in the argument in place is the
  caller's own, read bare; a caller capture only on request); `capture` left lib/convention/argument-labels'
  covered list (the request places no argument).
- `[ab = B | A]` re-spelled `[ab = (B | A)]` (alternation, paths, atomic): no answer moved; the old spelling's
  (different) answers are printed at core/operators/precedence as the reading's witness.
- SWEEP declares each of these (MOVEDF), plus two lines predfix84's engine could not run that this model runs as
  printed (no printed answer moved).

## WHAT MOVED

- No tag renamed or moved. New tags: core/principles/binding-fixed, core/labels/export/arguments,
  core/conditions/form/optional-entry, core/filters/negation/effects, core/operators/bindings/{label-omitted,
  label-default, label-kinds, label-in-argument, label-forward}, parked/ideas/{empty-argument, reference-kind,
  label-symbol, optional-arguments}.
- The sentence "What an argument exports" moved from lib/convention/argument-labels to
  core/labels/export/arguments (a pointer left; review r84 A7).
- Status moves: two-sources open → ruled; zero-binding open → ruled; in-loop open → ruled; caller-ambiguous,
  capture-export → ruled; match-so-far ruled 2026-11-21 → 2026-11-23; capture reading → ruled; add-on and
  json/members stay under construction (dates 2026-11-23); label-variables stays under construction.

## DRAFT READINGS ADDED

Marked in the documents as readings (none ruled):
- the label set binds looser than `&`, tighter than `|`; `[a, b, c]` is `a | b | c` (core/operators/precedence);
- effect-in-guard (core/filters/negation/effects, lib/control/when);
- a request inside a group question a compile error for now (the manager's proposal);
- a label parameter passed `_` by a body that places and reads it reads its own placement (the lane's);
- the default of a label parameter is the author's, in the head (label-default);
- a value with no label is fixed at compile time and warns (value-left);
- a request with no name: whether it gives the last step is not stated;
- the JSON sketch's bodies, its several-keys rule (last fitting member) — the manager's.

## OWNER QUESTIONS LEFT

- label-set-precedence: is `[a = A | b = B]` two labelled entries (the label set tighter than `|`)?
- optional-label-general: his flag stays open (`?:` read as "special, not a quantifier").
- question-request: a capture request inside a group question — an error for now?
- effect-in-guard: a request in `when`'s test refused through the guard — he may object.
- array-request-spelling: the array request under the request's shape.
- label-parameter-dollar: may a body read its label parameter with `$`?
- empty-argument, reference-kind, label-symbol, optional-arguments: parked with triggers.
- zero-in-loop's clause "or it's unusable": the reading told to him stands until he says otherwise.

## EVIDENCE AND COMMANDS

W = /home/pcrec/projects/pcrec/worktrees/predfold1123.

- `timeout 5400 python3 -I -B W/docs/dev/lanes/predfold1123_evidence/predfold1123_model.py` →
  `predfold1123_model.out`; last line `predfold1123_model: 18 checks, 0 failed`.
- `PREDFOLD_SABOTAGE=all timeout 14400 python3 -I -B .../predfold1123_model.py` → `predfold1123_sabotage.out`;
  last line `predfold1123_sabotage: 24 plants, 0 not caught (each plant turned its target check FAIL, no traceback)`.
- `(cd W && timeout 300 python3 -I scripts/pred_doc_lint.py)` → `pred_doc_lint: checks passed 7841, failed 0`.
- `(cd W && make -s test-plan-lint)` → `checks failed: 0`, rc 0.
- SUCCESSOR re-runs the 11 earlier models; each red is declared with its own FAIL line's digest (SUPERSEDEDF):
  reds predfix84 already declared keep its reason, the rest (predfix84's own, and digests the fold moved) name
  the check here that covers them. No older red is undeclared.
- One plant (s4) first ended in a traceback in READINGS (a refused JSON program read as an object); READINGS
  now judges each row through a guard, and the clean run is unchanged.
- Runs were single-process under `timeout`; nothing queued; no timing.
