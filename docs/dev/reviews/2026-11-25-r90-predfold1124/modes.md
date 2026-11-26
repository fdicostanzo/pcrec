# CRITIC MODES: r90 predfold1124

## Findings

### MODES-1 (CONFIRMED; doc; effort: one cell; blast radius: one table row) A sibling site of exact-count-unspecified still says "open"
- Where: core.md [core/holes/insert], the table row "a count (a quantifier bound)", last cell: "a whole count `{${n}}` a
  compile error for now (a reading; open exact-count-unspecified)".
- The fold ruled exact-count-unspecified ("agree error"; core_details.md entry "2026-11-23 (lane predfold1124 ...
  exact-count-unspecified ...)"; core/operators/bindings/unspecified now says "his ruling"), and re-wrote the
  printed line "An exact count" (fold_printed_lines line 32: "his ruling, exact-count-unspecified"). This row was
  not touched: it still calls the error "for now", "a reading", and the question "open". Repro: `grep -n 'open
  exact-count-unspecified' R/subject/*.md` gives only core.md:1592.
- The compile-error line 32 and line 48 ("The width unspecified") cite the ruling correctly; the evidence engine's
  refusal text names "unspecified-rule" (no form without the part), not the owner's ruling: an engine-wording
  matter only.
- Fix: "a whole count `{${n}}` a compile error (exact-count-unspecified: his ruling)".

### MODES-2 (CONFIRMED on the evidence engine; design; effort: one owner question or one ruled sentence; blast radius: every body that labels or lists its spot, read from outside) The outside read parts the shorthand from its written-out form on a manager's reading only, and the printed witness of the parting is the one body where the evidence shows no parting
- Where: core.md [core/labels/paths/argument-default], the bullet "The shorthand label is protected ... so the expansion
  is the same READ, not the same export (the manager's reading; the line "From outside"; that the written-out
  `[pub = B([A = A])]` exports `pub.A.h` is hand-worked, not run)", and its line "From outside" (fold line 30).
- The ruled sentence is his "shorthand-is-callers: yes thats it exactly" on "`B(A)` read through `A.d` means
  `B([A = A])`, whatever B's body does with the spot". Nothing ruled says the two forms part for a read from
  outside; the parting rests on the manager's reading (b) alone (analogy to statement 2's protected label).
- Repro (probe.py, A := `/(?<d>\d)/`): `[pub = B(A)] & (pub.A.d: <5)` vs `[pub = B([A = A])] & (pub.A.d: <5)`:
  - B(rx) := `/${[p = rx]}xx/`: REFUSED vs LEGAL. Same split for `/${[(=) = rx]}xx/`, `/${[n = [m = rx]]}xx/`,
    `/${[(=) = rx]}-${[(=) = rx]}/`, `/${rx}-${[p = rx]}/` ("Alone first"), `/${[p = rx]}-${rx}/`, `identity`, and
    `/${[n = [_x = rx]]}xx/` (but see MODES-3: that last LEGAL is itself a rule-2 hole).
  - B(rx) := `/${rx}xx/` (THE line's own body): REFUSED vs REFUSED. Also `[pub = B([a = A])] & (pub.a.d: <5)` and
    `hide([a = A]) & (hide.a.d: <5)`: REFUSED ("not visible through"). So the document's hand-worked claim that
    the written-out form exports `pub.A.h` for this body is denied by the evidence, and the line "From outside"
    shows no difference from the expansion at all on the engine. Rule 6 ("A part used alone inside a binding is
    crossed from outside as an underscore label is") read on the body's alone spot supports the engine; the
    reading "a label the caller writes in an argument ... [is a start] in the CALLER's binding, whatever the body
    stacks" supports the document. The documents do not say which.
- Smallest witness: `[pub = B(A)] & (pub.A.d: <5)` / `[pub = B([A = A])] & (pub.A.d: <5)`, B(rx) := `/${[p = rx]}xx/`
  (legality differs; no mode needed). In-binding reads agree in all three modes for every body (PROBED-AND-HELD).
- Fix shape: either the owner rules whether "means `B([A = A])`" covers the outside read (then the pair agrees by
  construction), or the line "From outside" is re-witnessed on a body where the written-out form IS legal
  (`/${[p = rx]}xx/`), its written-out half run, and the alone-body claim corrected or argued from rule 6.

### MODES-3 (CONFIRMED on the evidence engine; evidence + doc gap; effort: a PATH9 arm and one printed line; blast radius: reads through a call to the caller's own label under a body's private stack) A path from outside crosses the body's `_x` to reach the caller's label
- Where: the engine (PATH9, predfold1124_model.py) against core.md [core/labels/rule/paths] rule 2; no document line
  covers it ([core/labels/ownership]'s caller row reads only `a.h`; [core/labels/export/arguments]'s table prints
  `identity.a.h` for a list body only).
- Repro (A := `/(?<d>\d)/`, B(rx) := `/${[n = [_x = rx]]}xx/`): `B([a = A]) & (B.a.d: <5)` and `(B.n.a.d: <5)`: LEGAL,
  WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8];
  `[pub = B([a = A])] & (pub.a.d: <5)` LEGAL. Yet `B([a = A]) & (B._x.a.d: <5)` REFUSED (rule 2), `B(A) & (B.n.h: <5)`
  REFUSED (the printed line "Through a call, a private label in the body"), and with B(rx) := `/${[_ = rx]}xx/` or
  `/${[_p = rx]}xx/` or `/${[_x = rx]}xx/` the same `B.a.d` / `c.a.d` reads are REFUSED.
- Expected by rule 2 ("the path may not contain any underscore labels full or prefix unless the underscore prefix
  label is the start") and rule 5 (from outside the start is the macro's name or the label on the use): the path
  B -> n -> _x -> a -> d contains `_x`, not its start: a compile error. The reading that the caller's label is a
  START "whatever the body stacks" licenses `a.d`, not a path that starts at `B`/`pub` and crosses `_x`.
- Smallest witness: `B([a = A]) & (B.a.d: <5)` with the stacked body (legality; 3 labels deep).
- This also makes MODES-2's stacked-`_x` LEGAL written-out half unreliable.

### MODES-4 (CONFIRMED; doc; effort: one clause; blast radius: one line) "Inside a union" names the intersection as its "alike"
- Where: library.md [lib/structural/capture/in-set], the line "Inside a union: modes: a compile error (`/(?<h>\d)?x/ &
  (h: "3" | capture("h"))`: his ruling; `(h: <5 & capture("h"))` alike)" (fold line 53).
- `(h: <5 & capture("h"))` is an intersection and is the very program of the next line "Inside an intersection"
  (fold line 54). The union line's second witness should be a union (e.g. `(h: capture("h") | "3")`). Answers and
  refusals are right: both programs REFUSED on the probe; the cited ground "capture-in-set: error." covers both.

## PROBED-AND-HELD

- (a) THE 59 LINES. 36 legal lines: each meaning written directly as a python `re` regex (labels folded into the
  regex as constrained groups; last mention / array by the documents' rules) and run in WHOLE, SEARCHED and
  FIND-ALL on the line's own texts: 36 of 36 identical to the printed answer (oracle59.py, oracle59.out by rerun).
  The probe (second source) agrees with every engine-runnable legal line (probe59.out; option-hole lines 1, 2 are
  not runnable on the probe and rest on the regex alone: `(?i:ab)`, `a.b`). 18 compile-error lines (4, 7, 8, 9 two
  programs, 12 two, 20, 25 two, 30, 32, 48, 53 two, 54): all refused; each printed reason matches the cited
  sentence (rule 2, rule 6, condition 4, exact-count-unspecified "agree error", capture-in-set "error."), except
  line 30's ground (MODES-2) and line 53's misplaced "alike" (MODES-4). The 9 bullet lines (36-42, 56-59) are
  history ("until then") entries, not ruled lines: not run as answers.
- (a) THE OWNERSHIP TABLE: 5 rows x 5 columns, 62 reads with the table's own texts (table.sh / table.out): every
  legal cell gives WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `3xx`@4 / FIND-ALL [`3xx`@0, `4xx`@8] as the piece
  says; every cell's compile error refused (row 1 stacked `n.h`, row 2 closed/stacked `B.h`/`B.n.h`, row 3, row 4
  `A.h`). The RULED worked lines of rule, rule/paths, stacked-chain, closed-argument, argument-default checked
  against their cells: no disagreement (the lines for public stacks, two spots and `_p` sit in no column, as the
  table's bullet says).
- (a) CAPTURE-STATE drill ("set at every spot", the manager's reading), shorthand vs written-out vs a meaning regex,
  three modes each: optional spot `/(?:${rx})?xx/`; optional second spot `/${rx}(?:-${rx})?/` (WHOLE `3` FAILS: the
  last mention is the unset second spot, as flow's "not always the last match" rules); loop `/(?:${rx},)+/`
  (SEARCHED backtracks to `3,`@0); loop min 2 `/(?:${rx}){2,}/` and `rx.repeat(A, 2, _)` with the edge in second
  place (`73` HOLDS, `37` FAILS, `3` FAILS); two depths `/${rx}(?:,${rx})+/`; FIND-ALL places `some((A.d: "7"))` over
  a loop, two spots and an optional second spot (the array holds every spot's setting: `7` HOLDS where the plain
  read FAILS), `count((A.d: "7")): ==2` over a loop and two spots: 10 bodies, all three forms identical. Smallest
  texts reached: one character (`3`, `7`).
- (b) EXPANSION drill: 46 bodies/calls (expand.py, expand.out): alone, labelled, listed, closed, `_p`, stacked
  `_x`, stacked public, twice alone/list/closed, alone first, labelled first, closed first, alone then closed,
  peek, atomic, identity, hide, hits, occurrences, padded, padded_to, contains, startsWith, endsWith, anchored,
  rx.repeat (min 1, min 2), list_of (with `sep`): `B(A) & (A.d: <5)` vs `B([A = A]) & (A.d: <5)` identical in
  legality and all three modes everywhere; meaning regex agrees where written (28 bodies); the caller's explicit
  `a.d` gives the same answers and `A.d` is refused under it everywhere. Only the outside read parts (MODES-2).
  Not runnable on the engine, hand-worked to agree: `when(A, /x/)` (`[0-4]x`; the guard's `NOT peek` spot sets
  nothing visible), `quoted` (undeclared on the probe), a body passing its argument on to another macro (all four
  shapes "not modelled"; by "whatever B's body does with the spot" both forms legal, `[0-4]xx`), never placed
  (engine refuses both forms alike; the documents' never-pass warning is "a reading, not run", printing no answer).
- Engine-wording note, no finding: under `B([a = A])` the engine refuses `A.d` by condition 4 for user macros,
  padded_to and rx.repeat, but as "`A` is neither written nor a binding used" for peek, atomic, hits, occurrences,
  padded, contains, startsWith, endsWith, anchored: same legality, a different stated ground.
- The model, LIGHT run in this lens dir: `predfold1124_model: 20 checks, 0 failed`; its EXPAND (10 bodies) checks
  in-binding reads only, so the outside half of MODES-2 is outside every check.

CRITIC COMPLETE
