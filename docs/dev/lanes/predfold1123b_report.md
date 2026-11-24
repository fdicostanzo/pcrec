# Lane predfold1123b — the 2026-11-23 rulings after zero-open, folded

Branch `lane/predfold1123b`, cut from `lane/pred-rev28` at 89d26b6b3. Design only: the six predicate documents,
the successor evidence model, this report. Nothing under src/, cli/, lib/, memfn/, tests/; no record, plan,
decisions or reviews file touched.

## STATE AT HANDOFF

OWED: none

- The rulings file `docs/dev/lanes/predfold1123b_rulings.md` stayed EMPTY (read before each commit, before each
  long run and before this report): no R-n applied.
- Lint: `python3 -I scripts/pred_doc_lint.py`: `pred_doc_lint: checks passed 8502, failed 0`.
- `make -s test-plan-lint`: `checks passed: 2`, `checks failed: 0`.
- Model: `predfold1123b_model: 18 checks, 0 failed` (the committed `predfold1123b_model.out`).
- Sabotage: `predfold1123b_sabotage: 25 plants, 0 not caught` (the committed `predfold1123b_sabotage.out`).
- Nothing stopped the lane: no ruling contradicts an unreversed ruling (binding-as-label names its own reversals),
  and no run contradicted a ruling's stated consequence. Two consequences of a manager's reading are OWNER
  QUESTIONS below, not stops.

## RULINGS FOLDED

Each with its record entry (cited whole on a `rulings:` item) and where it lands.

- count-unspecified ("I agree the count semantics should work that way and that solves this issue. ...") —
  core/holes/count (one bullet, the line "Both bounds unspecified", the libpcre2 fact on `a{,}` run through ctypes);
  core/operators/bindings/unspecified (its count position).
- unspecified-rule ("unspecified-rule: yes and elegant", on the sentence put to him, quoted whole) — a NEW ruled
  piece core/operators/bindings/unspecified: the three positions with a ruled line (a label, an option, a count
  bound), a compile error elsewhere (a pattern, a set, a whole count, a comparison bound), the play-out's two
  withdrawn lines as `rejected:`.
- call-forms ("call-forms: yes.", on the four lines, quoted whole) — core/operators/bindings/call-forms CLOSES,
  renamed "One head per name", ruled; candidate (a) to `rejected:` by owner ruling; core/operators/bindings'
  positional/keyword sentence restated as line 2; lib/rx/repeat and lib/modifiers/padded lose their several bodies.
- repeat-head ("repeat-head: agree with your lean") — lib/rx/repeat's one head `repeat(x, min = _, max = min) :=
  /(?:${[(=) = x]}){${min},${max}}/`, its table run (no count, one count exact, `3, _`, `_, 5`, a range, a written
  0); a NEW parked piece parked/ideas/compile-time-conditional with the trigger "the first default or body that
  cannot be written without it" and the `?` `:` / `?:` spelling note.
- label-hole-full — already folded by predfix86; CHECKED: its record title is a `rulings:` item in
  core/labels/label-only-group and core/holes/name.
- closing-own-label — predfix86's history-only cites are now `rulings:` items (with his words whole) in
  core/labels/export, core/labels/export/arguments, core/labels/paths/closed-argument. Export statement 7 already
  carried his wording ("you can't go through A to get inside"; "there may be other doors"); unchanged.
- binding-as-label ("binding-as-label: yes", the four conditions quoted whole) — core/labels/rule line 3,
  core/labels/paths/argument-default (REVERSED), closed-argument, call-prefix case 2, export/arguments,
  binding-prefix and one-use-read (KEPT, a pointer each), nested-scope example 1, holes/labels, the errors and names
  tables, and the library (convention, peek, atomic, when, hits, occurrences). spot-read-name ANSWERED (candidate
  (b)): its open bullet replaced.
- label-doors ("label-doors: agree. Yes", the five lines quoted whole with the glosses as told to him) — ONE new
  ruled piece core/labels/rule at the head of the labels section, and ONE table, core/labels/ownership, under it
  (rows: the reading definition's own text / an argument's binding / the body / the caller inside an argument / a
  sent or forwarded label; columns: alone / labelled / listed / closed / stacked / forwarded; 26 cells run). The
  pieces that say parts of it keep their tags and point at it. Nothing else moved or re-tagged.
- The manager's reading (a) of label-parameter-omitted ("`[l = B]` with `_` is `[_ = B]`") is WITHDRAWN as the
  record says: core/operators/bindings/label-omitted now says an unspecified label on a part is the part with NO
  label; the consequence "a body that reads its label parameter cannot be called with the blank label" STANDS; his
  two-label body `A(l:, P) := [l = [_x = P]] & (_x: 5)` is printed with its two runs as the way round it.
- NOT RULED, kept so: the play-out's level 1 items 7-8 and level 2 (one parked piece for the group,
  parked/ideas/call-head-forms, with triggers and the interleaving beyond line 2); `?` for optional parameters
  (parked/ideas/optional-arguments, `max?` = `max = _` noted as the manager's suggestion); r86's open slugs and
  r84's flags slugs untouched. "A value left of `:`" appears in the range only as an optional-label edge that
  STANDS (record line 9745, r86's A1 disposition, already folded by predfix86); no new ruling, nothing applied.
  "The count-prefixed list / length(0:)": NOT FOUND in lines 9402-10135 (searched `length(0`, `count-prefixed`);
  nothing done.

Record differs from the brief: none found. The brief's "unspecified-rule ... positions with a ruled line: a label,
an option, a count bound" matches the ruling entry ("the option hole's `""`").

## MANAGER READINGS TESTED

Every "manager's reading" / "(marked)" sentence of the range (after zero-open), with its verdict.

| entry | reading | verdict | ground |
|---|---|---|---|
| play-out | the whole (a PROPOSAL) | n/a | ruled parts folded by their rulings; the rest parked |
| call-forms comments | `repeat(A)` is `A*` under `min = _, max = min` | SUPPORTED | REPEAT, CONTROL (`{0,}` against python `re`) |
| call-forms comments | unset and `_` differ only where the default is not `_` | SUPPORTED | REPEAT: `min = 3` exact, `min = 3, max = _` 3 or more |
| repeat sketch | his sketch is head (i)'s table but for a written 0 | SUPPORTED | REPEAT reproduces head (i); the record's run |
| repeat sketch | `${min|0}` makes copies, not a fallback | UNTESTABLE as a run | the engine runs no binding of several numbers; the rule sentence of core/holes/count quoted |
| repeat sketch | a compile-time conditional is a new component | applied | parked/ideas/compile-time-conditional |
| `?:` remark | the conditional's marks meet `?:` | applied | the parked piece's note |
| `{,}` objection | text only if `_` is the empty text | SUPPORTED | COUNT: libpcre2 `a{,}` WHOLE holds on `a{,}` only (s16); UNSPEC's `_` by meaning, not text (s5) |
| count-unspecified | the mark has one rule; two play-out lines withdrawn | SUPPORTED | UNSPEC: pattern and set refused (s6) |
| unspecified-rule (a) | withdrawn lines are compile errors | SUPPORTED | UNSPEC |
| unspecified-rule (b) | `_` to ANY parameter, judged per position | SUPPORTED | the line "Laid into two positions" |
| unspecified-rule (c) | not "use the default" | SUPPORTED | REPEAT (s7) |
| call-forms (a) | filled twice / unknown name: compile error | SUPPORTED | CALLFORMS |
| call-forms (b) | a default under every rule of a body | UNTESTED beyond `max = min` | CALLFORMS |
| call-forms (c) | the binding-list head is a framing, not ruled | applied | parked/ideas/call-head-forms |
| closing-own-label | the four-line restatement | superseded | by label-doors (ruled) |
| spot-read-name working (r1, three conditions) | the body labels the spot: `A.d` LEGAL | NOT SUPPORTED, not written | SHORTHAND: condition 4 (ruled) refuses it |
| spot-read-name working (r1) | the body closes the spot: `A.d` LEGAL | NOT SUPPORTED, not written | SHORTHAND, TABLE: refused |
| spot-read-name working (r1) | the body uses it alone: `A.d` LEGAL | SUPPORTED | `3xx` HOLDS, `7xx` FAILS, as the record's run |
| fourth condition | alone legal; labelled error, read `B.p.d`; closed error; caller-labelled `a.d` legal, `A.d` error | SUPPORTED | SHORTHAND, TABLE; the record's answers reproduced |
| binding-as-label (a) | "already made" by anyone, the body included | SUPPORTED | SHORTHAND |
| binding-as-label (b) | a list on the spot is a label made: `A.d` error, read `B.d` | SUPPORTED as run of the reading | SHORTHAND; consequences an OWNER QUESTION |
| binding-as-label (c) | placed twice alone: the same-label-twice rules | SUPPORTED | "Used twice alone, the last mention" |
| binding-as-label (c) | never placed: the never-pass warning | UNTESTABLE | the engine refuses the sugar and its expansion alike; no warning modelled |
| binding-as-label (d) | the canonical form written as his statement | applied | core/labels/rule line 2 |
| consequence (predfix86) | a body reading its label parameter refuses `_` | SUPPORTED (stands) | the line, unchanged in SWEEP |
| two-label clarification | agreed; `A(n:, /\d/)` and `A(_:, /\d/)` agree in every mode | SUPPORTED | OWNERBODY; the record's answers reproduced (s24) |
| two-label clarification | unspecified label = no label, not the blank mark | SUPPORTED | NOLABEL (s12) |
| nesting order | the values agree in either order | SUPPORTED | STACK (s13) |
| label-doors (a) | stacked = nested directly; anything between makes two spots | SUPPORTED | "Something between the two labels" refused |
| label-doors (b) | `n.d` passes a private `_x` stacked on the spot | SUPPORTED | STACK |
| label-doors (c) | `[l = [_ = P]]` opens through `l` | SUPPORTED | "A blank label in the stack" (s14) |

## ANSWERS CHANGED

Each with his earlier words, where it stood, what it is now.

- argument-default: his "argument-default: for me this is an error." `B(A) & (A.d: <5)`, B(rx) := `/${rx}xx/`: a
  compile error, now LEGAL (WHOLE `3xx` HOLDS, `7xx` FAILS). The statement of core/labels/paths/argument-default
  reversed; "The caller's own read" line now "The caller's read through the shorthand"; the same in
  core/labels/export/arguments ("His ruled error stands" bullet and the line "The body using its argument alone").
- argument-default "Both uses" (`/${[p = rx]}-${rx}/`): `7-3` FAILS, `3-7` HOLDS (the labelled spot) → `7-3` HOLDS,
  `3-7` FAILS (the alone spot; condition 4; a reading, see OWNER QUESTIONS).
- closed-argument: his "closed-arguments: a" on "`A.d` is legal in the caller exactly where `d` is visible through
  the call". "Visible through the call" (labelled spot, legal) → a compile error, the read `B.p.d` (the old
  "Candidate (b)" line, now "Through the body's path"); "Used alone by the body" (error) → LEGAL; the closed cases
  unchanged (errors).
- call-prefix case 2: his "i'd say A.d is legal there". "A's own d, the body using the argument alone (case 2)":
  error → LEGAL; "A's own d, the body labelling the spot (case 2)": legal → error; "Used twice alone"
  (`pair(A) & (A.d: <5)`, `/${p},${p}/`): error → LEGAL, the last mention (`7,3` HOLDS, `3,7` FAILS).
- nested-scope example 1, his "is legal. C can see d as a flat look into A": a compile error under argument-default
  → LEGAL (WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS). core/holes/labels' sentence likewise.
- label-omitted (reading (a) withdrawn): "Closed by `_`", `W(_:, A) & (A.h: <5)`: a compile error → LEGAL ("The
  unspecified label on a spot": `<3>` HOLDS, `<7>` FAILS).
- the library: `when(A, (A.h: ..))` legal (a reading) → a compile error; `peek(A) & (A.d: ..)`, `atomic(A)`,
  `hits(A)`, `occurrences(A)`, `identity(A)` with `A.d`: legal under closed-argument's "passes the labels on" → a
  compile error, read through the call (`peek.d`, `hits.hit.d`, ...).
- the tables: the errors table's two `A.d` rows merged into one (labelled, listed, closed, or A referenced twice);
  call-forms and unspecified errors added; the names table's argument row restated.
- rx.repeat: `rx.repeat(x, min = 1)` meant at least one (the third body) → exactly one; every documented use that
  meant "at least" re-spelled `min = 1, max = _` (rx.digits and the three repeat lines; the same answers).

## WHAT MOVED

- New ruled pieces: core/labels/rule, core/labels/ownership (at the head of the labels section),
  core/operators/bindings/unspecified (after call-forms).
- New reading piece: lib/modifiers/padded-to (`padded_to(rx, n)`, the manager's placeholder name per the record),
  taking padded's width-form body, bullets and line; lib/modifiers/padded keeps its one head.
- Renamed (tag kept): core/operators/bindings/call-forms "Several bodies for one name" → "One head per name".
- Status changes: call-forms open → ruled 2026-11-23; lib/rx/repeat ruled 2026-11-22 → 2026-11-23;
  argument-default ruled 2026-11-22 → 2026-11-23; core/holes/count ruled 2026-11-19 → 2026-11-23.
- New parked pieces: parked/ideas/compile-time-conditional, parked/ideas/call-head-forms. Bullets added to
  parked/ideas/empty-argument and parked/ideas/optional-arguments.
- Lines GONE (declared in SWEEP's MOVEDB): the two call-forms lines by the old bodies; padded's width line (now
  padded_to's); the three `min = 1` repeat lines (re-spelled); "A read in then"'s tail; the `B(A) & (A.d: <5)`
  lines whose answers moved.
- lib/search/occurrences: its `A.d` refusal is RUN but not printed (the piece is at 40 lines); the sentence points
  at the table.

## DRAFT READINGS ADDED

- The blank mark over the reading definition's own literal: `[_ = /(?<h>\d)/] SEQ /xx/ & (h: <5)` LEGAL, its owner
  reads it (the table's first-row closed cell), from line 4's gloss as told to him ("its owner always reads it").
  The loaded engine closed it; the model adds OWNREAD (s25).
- A default naming a LATER parameter is a compile error at the definition (the reading of "never a later one").
- `_` in an option position: `(?${o}:` becomes `(?:` (the option hole's `""`).
- The forwarded column is n/a for every row but the sent label.
- The provided bodies are under the shorthand like a user's: a list or `hit` on the spot is a label made.

## OWNER QUESTIONS LEFT

- list-is-label (reading (b) of binding-as-label): a body that LISTS its spot has made a label, so `A.d` through
  it is a compile error. Consequences: `when(A, (A.h: ..))`, `peek(A) & (A.d: ..)`, `atomic(A)`, `hits(A)`,
  `occurrences(A)`, `identity(A)` all refuse the argument's name; the reads are `when.h`, `peek.d`, `hits.hit.d`.
  The alternative: a list is NOT a label made, `A.d` legal there (as before). Leaning: keep (b) (one name per spot).
- both-uses: a body using its argument alone and labelled (`/${[p = rx]}-${rx}/`): `A.d` now reads the ALONE spot
  (the second digit), where the documents said the labelled spot's. Reply either way.
- pair-twice-alone: `/${p},${p}/` with `A.d` is legal by the last mention (reading (c)); the documents had a
  compile error. Reply either way.
- padded-to-name: the width form's name `padded_to` is a placeholder.
- owner-reads-blank: `[_ = /(?<h>\d)/]` in the definition's own text: `h` still read bare there (line 4's gloss);
  export statement 7's table row "not accessible locally to the binding" is for a binding A.
- the open slugs carried as they were: capture-in-set, optional-entry-edges, optional-label-general, r84's three
  flags slugs.

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/predfold1123b_evidence/predfold1123b_model.py` (successor of predfix86's; own CLAUDE.md there).
  `timeout 7200 python3 -I -B docs/dev/lanes/predfold1123b_evidence/predfold1123b_model.py` → the committed
  `predfold1123b_model.out`, last line `predfold1123b_model: 18 checks, 0 failed`.
- `PREDFOLD1123B_SABOTAGE=all` → the committed `predfold1123b_sabotage.out`, last line `predfold1123b_sabotage: 25
  plants, 0 not caught`. Its first run caught 22 of 25. s12 and s15 were MASKED: the stack rule made the planted
  form and the right one agree. NOLABEL now also checks the lowering itself (`[l = v]` with `_` gives `(v)`), and
  s15 now plants a wrong expansion. s13 crashed in STACK's message (an unguarded read of a refused program); it is
  guarded now. All three are caught by their own check.
- SWEEP: 295 printed lines now, 274 at 89d26b6b3 under predfix86's engine; every moved or gone answer declared
  (MOVEDB, 7 programs); undeclared 0.
- SUCCESSOR: the thirteen earlier models re-run; each now stops at load on its reader of `rx.digits := rx.repeat(
  rx.digit, min = 1)` (digest b024bdc4e170; predarr and predscope keep the tracebacks predfix86 declared,
  ce43d48c7e37, 17ab1e47c179); every one declared.
- The expansion drill (EXPAND): 12 sugar forms against their written-out expansions (the shorthand, both uses,
  `_:` on a spot, his body with `_:`, a label parameter, an unset parameter, `_` for one bound and for both, named
  entries, `_` for an option, stacked labels either order, `?:`), legality and every mode over 21 texts.
- libpcre2 RUN through ctypes (never read): `a{,}` WHOLE on ``, `aaa`, `a{,}`: False, False, True.
- `python3 -I scripts/pred_doc_lint.py`: failed 0. `make -s test-plan-lint`: failed 0.
