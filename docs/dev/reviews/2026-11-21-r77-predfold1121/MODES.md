# CRITIC MODES findings: predfold1121 (r77)

(append-only: add each finding the moment you have it; never overwrite this file with Write)

## Findings

### MODES-1  CONFIRMED  answer  -- a group question written INSIDE a used definition: the array's "entire rx as composed" scope and nested-scope's "own settings only" give two answers
- Pieces: core/labels/labels-vs-captures (core.md:303-306, "The array's scope is the entire rx as composed, not one literal or one definition ... two groups of one name in a sequence give it both settings ... as they stand where it is read (composed at that point: a reading)") vs core/holes/bare-condition/nested-scope (core.md:458, ruled 2026-11-21, record "OWNER RULING -- bare-nested-scope, case 2: b": "reads only its own settings of them") and core/labels/flow's new exception (core.md:366-367). array-vs-passes (core.md:313) says the group questions read "the array of a name's settings" without saying whose settings when the question is written inside a piece another definition uses. Neither piece names the other; the array bullet still says "not one definition".
- Mode: the nested role (a group question inside a used definition). At top level the two agree (one definition holds everything).
- Witness (engine calibrated on 5 printed lines, all reproduced; modes/w/eng.py, w1.py): `A SEQ B`, A := `/(?<h>\d)/`, B := `/(?:;(?<h>\d))*/ & some((h: "7"))`.
  Composed array (labels-vs-captures): WHOLE `7;1` HOLDS, `1;7` HOLDS, `7` HOLDS / SEARCHED `x7;1;2` `7;1;2`@1 / FIND-ALL `7;1;2 1;7;2 7;1` [`7;1;2`@0, `1;7;2`@6, `7;1`@12]
  Own settings (nested-scope): WHOLE `7;1` FAILS, `1;7` HOLDS, `7` FAILS / SEARCHED `x7;1;2` FAILS / FIND-ALL `7;1;2 1;7;2 7;1` [`1;7;2`@6]
  Edge in SECOND place at min >= 2 (B's loop `{2,}`): composed WHOLE `7;1;2` HOLDS, own FAILS; both HOLD `1;7;2`.
  Sub-part (b) empties: on `7` B's own array is EMPTY, so `some` is false under own-settings and true under composed: the empty-array rule (core.md:320) answers differently by which array is meant.
- Same question for `h[k]` (`(h[1]: "7")` inside B: composed reads A's `7`, own reads B's first) and for `count`/`occurs` (count 1 vs 0 on `7;1`).
- Expected: one sentence naming the array a group question sees when it is written inside a separately defined piece (own settings, as nested-scope rules for values, or composed, as the array bullet says), and the array bullet's "not one definition" restricted to what the piece's USER reads.
- Effort: small (one bullet in each piece, two run lines). Blast radius: every group question in a library binding (lib/modifiers/length `nchars := count((ch: ..))` is the same shape when `length` is used after another `ch`-setting part).

### MODES-2  CONFIRMED  answer  -- a group question in an `&` operand inside a hole: which array (the definition's, or the chain's) is not stated; literal and hole spellings can part
- Pieces: core/labels/labels-vs-captures/array-vs-passes (core.md:313, ruled) states no place; core/values/reads (core.md:660-663) says a `$` read "in an `&` operand" resolves in "the chain's labels" but in "a value hole, every label visible in the definition"; match-so-far (core.md:547) says a hole's content belongs to the definition it is written in; the place table (core.md:167) gives an `&` operand "the stretch's own text, whole".
- Mode: nested filter role (inside a hole, inside an `&` operand), one definition (no nested-scope involved).
- Witness (modes/w/w2.py): `/(?<h>\d)${/(?:;(?<h>\d))*/ & some((h: "7"))}/`.
  The definition's array: WHOLE `7;1` HOLDS, `1;7` HOLDS, `7` HOLDS / SEARCHED `x7;1;2` `7;1;2`@1 / FIND-ALL `7;1;2 1;7;2 7;1` [`7;1;2`@0, `1;7;2`@6, `7;1`@12]
  The chain's own settings: WHOLE `7;1` FAILS, `1;7` HOLDS, `7` FAILS / SEARCHED `x7;1;2` FAILS / FIND-ALL `7;1;2 1;7;2 7;1` [`1;7;2`@6]
  The literal spelling `/(?<h>\d)(?:;(?<h>\d))*/ & some((h: "7"))` gives the first line (one array, the "Outside the loop" shape), so under the chain reading the hole spelling and the literal spelling answer differently; under the definition reading the `&` operand's group question sees a setting made OUTSIDE its stretch (not "the stretch's own text").
- Sub-part (b): on `7` the chain's array is EMPTY (some false), the definition's is [`7`].
- Library instance of MODES-1 and this one together: `/(?<ch>[a-z])/ SEQ length(==3)` (length(S) := `chars & (nchars: S)`, nchars := `count((ch: /(?s:.)/))`, library.md:97-103): composed array WHOLE `xabc` FAILS, `xab` HOLDS / SEARCHED `-xab` `xab`@1 / FIND-ALL `xab yabc` [`xab`@0, `yab`@4]; own/chain array WHOLE `xabc` HOLDS, `xab` FAILS / SEARCHED `-xab` FAILS / FIND-ALL `xab yabc` [`xab `@0, `yabc`@4]. The ruled name `length` reads a length of 4 for a 3-character stretch under the array bullet's wording.
- Expected: the array piece says which settings a group question in an `&` operand sees (the operand's own, matching reads' "the chain's labels", or the definition's), in every place.
- Effort: small. Blast radius: every library body of the shape `P & group-question` (length, hits + occurs, the "Same item" idiom inside a hole).

### MODES-3  CONFIRMED  answer  -- `0` in an `&` written in place as a sequence operand: the new definition-wide rule breaks the ruled identity `A & B` = `A & (0: B)` and parts from the hole spelling
- Pieces: core/conditions/match-so-far (core.md:538, 543, ruled 2026-11-21 zero-in-definition: "Within one definition `0` spans all its literals and operands"; core.md:541 "After a complete pattern (`A & (0: S)`) the match so far is the entire match", which names no place) vs core/filters/and (core.md:593, ruled 2026-11-17: "`A & B` holds exactly when `A & (0: B)` holds, on the same stretch") and core/holes/bare-condition (core.md:1086: "in `${A & (0: S)}` the `0` is only A").
- Mode: the nested filter role (an `&` operand that is not the program's top). At top level the definition's match so far IS the stretch, so all three agree; they part only nested.
- Witness (modes/w/w3.py): `/\d/ SEQ (/\d/ & (0: /\d/))`, one definition.
  Definition-wide `0` (match-so-far as worded): WHOLE `12` FAILS / SEARCHED `x12` FAILS / FIND-ALL `12 34 5` []
  The `&`'s stretch (filters/and's identity; and the hole spelling `/\d${/\d/ & (0: /\d/)}/`, bare-condition's "only A"): WHOLE `12` HOLDS / SEARCHED `x12` `12`@1 / FIND-ALL `12 34 5` [`12`@0, `34`@3]
  `/\d/ SEQ (/\d/ & /\d/)` HOLDS on `12` in every mode, so under the worded rule `A & B` and `A & (0: B)` give two answers. Edge in second place at min >= 2: `/\d/ SEQ (";" SEQ (/\d/ & (0: /\d/))){2,}` on `1;2;3`: definition-wide FAILS, stretch HOLDS (SEARCHED `x1;2;3` `1;2;3`@1).
- So the literal-written `&` and the hole-written `&` of one definition answer differently, though match-so-far says a hole's content "belongs to the definition it is written in" (core.md:547).
- Expected: match-so-far states that inside an `&` operand `0` is the operand's stretch (keeping filters/and and bare-condition's "only A"), or the `&` identity is restricted to top level. The ruling's question as put ("`0` is the match so far of the definition it is written in") did not show an `&` operand.
- Effort: small (one bullet + one run line). Blast radius: every `&` with a `0` condition nested in a sequence, hole-free; filters/and's ruled identity.

### MODES-4  CONFIRMED  answer  -- `0` in a FIND-ALL place (an `occurrences` argument): three readings the changed text allows, three answers
- Pieces: core/conditions/match-so-far (core.md:547, a reading added 2026-11-21: "An expression written in place (an argument, a hole's content) belongs to the definition it is written in ... the argument below is the caller's, so its `0` includes the caller's `\d`"; core.md:544 "A definition used inside it counts as its text"), core/holes/bare-condition (core.md:1086: a condition in a hole "is read in the definition the hole is written in", and occurrences' hole `${x}` is written in occurrences' body), the place table (core.md:178: an `occurrences` argument's text is "its stretch"), lib/search/occurrences (library.md:301: a condition in x "reads that hit's own labels", nothing on `0`).
- Mode: a FIND-ALL place. The printed "An argument" line (core.md:553) has no text in the macro body BEFORE the hole and no loop, so it cannot tell these apart.
- Witness (modes/w/w4.py; occurrences per its ruled body `/(?:(?s:.*?)(?<hit>${x})){${min},}(?s:.*)/`): `/x?/ SEQ occurrences(/\d/ SEQ (0: /\d/), min = n)`.
  n = 1, the caller's definition: WHOLE `a5` FAILS, `x5` FAILS, `5` HOLDS / SEARCHED `-a5` `5`@2 / FIND-ALL `a5 56` [`5 56`@1]
  n = 1, occurrences' body (the hole's definition): WHOLE `a5` FAILS, `x5` HOLDS, `5` HOLDS / SEARCHED `-a5` `5`@2 / FIND-ALL `a5 56` [`5 56`@1]
  n = 1, the hit's own text: WHOLE `a5` HOLDS, `x5` HOLDS / SEARCHED `-a5` `-a5`@0 / FIND-ALL `a5 56` [`a5 56`@0]
  Edge in SECOND place, n = 2, `56`: caller FAILS, body FAILS, hit's own HOLDS (FIND-ALL `a5 56` [] vs [`a5 56`@0]): under both definition readings the second hit's `0` contains the first hit and the gap, so a test meant per hit can never pass past the first.
- The same question stands for a `records` item and for `0` in a group question's argument (`some((0: S))`: `0` has no array of settings; whether it is a compile error is not stated).
- Expected: match-so-far names `0` in a FIND-ALL place (per hit, as the place table's "its stretch" suggests, or the caller's), with a line whose macro body has text before the hole and a second hit.
- Effort: small-medium (a reading to rule; the `0`-in-loop question zero-in-loop is a sibling and may close together). Blast radius: occurrences, hits, records, any macro looping an argument.

### MODES-5  CONFIRMED  design  -- nested-scope readings (c) "a piece looped by its user reads its own previous pass" and (d) "two uses of one piece are two pieces" make `(B SEQ ";"){2}` and its written-out form answer differently
- Piece: core/holes/bare-condition/nested-scope (core.md:474-478, the manager's readings, UNTESTED per core_details.md:1562 ff.); core/labels/one-rule's reading "A counted repeat `{n}` with n of 2 or more is a loop" (core.md:348).
- Mode/role: the nested role, with the edge in SECOND place (the second pass / the second use) at a count of 2.
- Witness (modes/w/w5.py): B := `/${NOT (c: >= 5)}(?<c>\d)/` (the printed "Pass 2" body as a separate definition).
  `(B SEQ ";"){2}`, reading (c): WHOLE `7;3;` FAILS, `3;7;` HOLDS / SEARCHED `x7;3;` FAILS / FIND-ALL `7;3; 3;7;` [`3;7;`@5]
  `B SEQ ";" SEQ B SEQ ";"`, reading (d): WHOLE `7;3;` HOLDS, `3;7;` HOLDS / SEARCHED `x7;3;` `7;3;`@1 / FIND-ALL `7;3; 3;7;` [`7;3;`@0, `3;7;`@5]
  In ONE definition both spellings (`/(?:${NOT (c: >= 5)}(?<c>\d);){2}/` and written out) give the first line.
- So the exception to compose-equals-literal (ruled, case 2) is not only "one definition vs two": for one composed piece, `X{2}` and `X X` part, which no ruled text shows and which core/patterns/quantifiers' `{n}` does not say. The owner's case-2 reason ("in a loop around the insides of the B ... the first time through it is unset") speaks about a loop only.
- Expected: either a line stating the `{2}`-vs-written-out difference (so the ruling is put with it), or reading (d) refined (a use is a written mention; a loop's passes are one use) with this line printed.
- Effort: small. Blast radius: any library piece reading a label before its group, used repeated (the "compare an item with its predecessor" idiom of pass-start-read, core.md:568).

### MODES-6  CONFIRMED (the `\k` half) / SUSPECTED (the caller half)  answer  -- "the CAPTURE ... the value from the last time a group of the name was set" is not PCRE's for a name with two groups: `\k<h>` reads the FIRST SET group in pattern order
- Piece: core/labels/labels-vs-captures (core.md:296-298, context bullet read by the changed bullets core.md:291-295: "A group written in rx text is a label and a capture", "what the caller gets is the captures", "PCRE's carried value"); core/labels/one-rule (core.md:343) allows two groups of one name.
- Probe (libpcre2-8 via ctypes, modes/w/pcre.py; anchored whole): `(?J)(?<h>\d)(?:;(?<h>\d))?\k<h>`: `77` MATCH (groups `7`, unset), `7;33` NOMATCH, `7;37` MATCH (groups `7`, `3`). PCRE's back reference to a duplicated name uses the first group, in pattern order, that is set; not the last set.
- Under the printed definition ("last time a group of the name was set"): `7;33` HOLDS, `7;37` FAILS. PCRE: `7;33` FAILS, `7;37` HOLDS. So the literal `/(?<h>\d)(?:;(?<h>\d))?\k<h>/` WHOLE answers are wrong as the piece defines a capture, in every mode (SEARCHED `x7;37` `7;37`@1 under PCRE, FAILS under the definition).
- Label vs capture with NO loop: on `7;3` the label h is `3` (last mention, one-rule), PCRE's capture for `\k<h>` is `7`; the piece says the two part "after a loop" (core.md:286) and its only line parting them is a loop (`3;;`, core.md:310). The edge here is the second group being the one set.
- SUSPECTED (would confirm: a pcre2 name-lookup probe or a pcre2-reader note): the caller's by-name capture of a duplicated name also returns the first set group, so "what the caller receives ... PCRE's carried value or the label's last-pass value" (core.md:294) has a third value that is neither.
- Expected: the capture bullet says "the first set group of the name in pattern order (PCRE's duplicate-name rule), and within one group its last setting", with the `7;37` line; the caller question names the duplicate-name case.
- Effort: small. Blast radius: every rx-text `\k` on a name written twice (pcrec allows it where PCRE needs `(?J)`), and the open caller question.

### MODES-7  CONFIRMED  answer  -- "every setting, in order": the ORDER is not defined where a lookaround sets the name (time of setting vs place in the text), so `h[k]` has two answers
- Piece: core/labels/labels-vs-captures/array-vs-passes (core.md:313, ruled: "every setting, in order"; `h[k]` "the k-th setting", core.md:317) and labels-vs-captures (core.md:299); core/patterns/lookaround (core.md:273-278: labels set in a lookahead/lookbehind are visible after it, "may lie outside the matched text").
- Drill: a label set inside a lookaround inside a pass, edge in SECOND place.
- Witness (modes/w/w7.py): `/(?:(?=\d(?<h>\d))(?<h>\d))+\d/ & (h[2]: "1")`.
  Settings in the order they are made (the lookahead's first): on `12` [`2`, `1`], on `123` [`2`, `1`, `3`, `2`]: WHOLE `12` HOLDS, `123` HOLDS / SEARCHED `x123` `123`@1 / FIND-ALL `123 12` [`123`@0, `12`@4]
  Settings in text order (by where each setting's text stands): `12` [`1`, `2`], `123` [`1`, `2`, `2`, `3`]: WHOLE `12` FAILS, `123` FAILS / SEARCHED `x123` FAILS / FIND-ALL `123 12` []
- A lookbehind gives the same split with the setting's text BEFORE an earlier setting's; `sorted`/`distinct` (library.md:1270 "every setting of the name") inherit the question.
- Expected: one clause, "in the order the settings are made along the path" (or text order), with a lookaround line. The printed lines have no lookaround, so they cannot tell.
- Effort: trivial. Blast radius: `h[k]`, and every reading that assumes the array order is the item order.

### MODES-8  SUSPECTED  answer  -- `h[k]` past the array's end (an empty array, or fewer settings than k) is not defined: absent (a test fails, NOT holds) or an error
- Piece: core/labels/labels-vs-captures/array-vs-passes (core.md:313, 317, 320: the empty-array bullet defines `some` and a count, not the index); core/conditions/two-valued / defaults (an absent label: a test fails, `NOT` holds, a default stands in).
- Sub-part (b): an EMPTY array, an UNSET label and an index past the end are three spellings of "no value"; only the first two have a stated answer.
- Witness: `/(?:(?<h>\d)?;)+/ & NOT (h[2]: "5")`. On `3;` and on `3;;` (array [`3`], the second pass sets nothing, PCRE keeps the empty-able pass): read as absent, WHOLE HOLDS, SEARCHED `x3;` `3;`@1; read as an error, no line. On `;;` (empty array) the same split. With `min >= 2` the second pass is exactly the place the index meets the optional: `3;5;` gives h[2] = `5` (FAILS), `3;;5;` gives h[2] = `5` too (the setting count skips the empty pass), so `3;;5;` and `3;5;` answer alike while the label after the loop differs (`5` both; on `3;5;;` the label is unset, h[2] still `5`).
- Would confirm: a sentence or line in array-vs-passes for k past the end; a default on an index (`(h[2] = "x": ..)`) is the same question.
- Effort: trivial. Blast radius: every `h[k]` with a loop that can run fewer than k settings.

### MODES-9  CONFIRMED  answer  -- flags in a hole vs a CONDITION's set: whether the hole's `i` reaches `(d: "x")` is not stated, and either answer breaks a ruled equivalence
- Pieces: core/holes/flags (core.md:1035, ruled: "What is inserted in a hole starts with the flags in force at the hole"); core/holes/flags/in-filter (core.md:1045, ruled; its changed bullets core.md:1053-1060: "the sides take the flags first", the warning "never where the expression reads a label of the literal (`$x`)"); core/holes/bare-condition (core.md:1090: "`/\d${(0: rx.digit)}/` is `/\d/ & (0: rx.digit)`"); core/patterns/flags (core.md:218: a program-level `&` has no surrounding rx, each side keeps its own flags). Every printed flag line has PATTERN operands only.
- Mode/role: a bare condition in a hole; a condition side of an `&` in a hole; a group question side.
- Witnesses (regex model: the condition as a lookbehind on d's text, python `re`: `(?i)(?P<d>[a-z])(?<=x)` matches `X`; `(?P<d>[a-z])(?<=x)` does not):
  1. `/(?i)(?<d>[a-z])${(d: "x")}/` on `X`: the set inherits `i` -> WHOLE HOLDS; it does not -> FAILS.
     Its ruled equal (bare-condition, "a bare condition last in an rx equals the condition on the whole") `/(?i)(?<d>[a-z])/ & (d: "x")` is a program-level `&`, the condition keeping its own flags -> FAILS. So if the hole's flags reach the condition (as "what is inserted in a hole" says), the ruled equivalence breaks; if not, core/holes/flags needs a "conditions excepted" clause.
  2. `/(?i)${/(?<d>[a-z])/ & (d: "x")}/` on `X`: "the expression alone with the flag applied to its result" HOLDS; sides-first HOLDS only if the condition side inherits. If it does not, the new warning fires on every condition side in a caseless hole (the `$x` exemption names only a label "of the literal").
  3. FIND-ALL place / group question: `/(?i)${/(?:(?<d>[a-z]),)+/ & some((d: "x"))}/` on `a,X,`: inherit HOLDS, else FAILS (SEARCHED `-a,X,` `a,X,`@1 vs FAILS).
- Expected: one sentence in core/holes/flags/in-filter (and core/holes/flags) saying whether a condition's sets take the hole's flags, with a line on `X`, and the bare-condition equivalence stated "flags aside" or kept by the choice.
- Effort: small. Blast radius: every condition in a hole under `(?i)`/`(?s)` (a `/./`-set under `s`), the new warning's firing set.

### MODES-10  CONFIRMED  answer  -- a `$` read inside a group question's condition (`some((h: $m))`): which m is read is not stated; it re-opens the pairing the joint-entry refusal closed
- Pieces: core/labels/labels-vs-captures/array-vs-passes (core.md:322-327: plain entries are each "a group question over its own array"; a JOINT entry is "a compile error for now; pairing by index or by item can be allowed later without changing an answer"); core/values/reads (core.md:653, "`$y` is the label `y` as it stands where the read is written"; core.md:655 "A read yields at most one string").
- Mode: a FIND-ALL place (a group question's argument).
- Witness (modes/w/w11.py): `/(?:(?<h>\d)(?<m>\d),)+/ & some((h: $m))`.
  `$m` as it stands where written (after the loop: the last pass's m): WHOLE `11,23,` FAILS, `12,31,` HOLDS, `12,` FAILS / SEARCHED `x11,23,` `11,`@1 / FIND-ALL `11,23, 12,31, 12,` [`11,`@0, `12,31,`@7]
  `$m` of the setting being judged (the same pass, a pairing by item): WHOLE `11,23,` HOLDS, `12,31,` FAILS / SEARCHED `x11,23,` `11,23,`@1 / FIND-ALL `11,23, 12,31, 12,` [`11,23,`@0]
  The edge is in SECOND place: on `12,31,` the reading-1 hit is h[1] against the LAST m.
- So the promise "pairing ... can be allowed later without changing an answer" holds only if `$` reads inside a group question are refused too, or are fixed now as reading 1 (then a later by-item pairing would change this line's answer). A computed label over another label (`some((h: $m + 1))`, core/values/computed-labels: "computed where it is read") is the same question.
- Expected: array-vs-passes states what a `$` read (and a computed label) inside a group question's condition reads, or refuses it with the joint entry.
- Effort: small. Blast radius: every group question whose set reads a label; the joint-in-some "without changing an answer" promise.

### MODES-11  CONFIRMED  answer  -- a group question INSIDE a loop pass: the array "as they stand where it is read" carries the earlier passes' settings, so a per-pass test is order-dependent; no piece says whether that is meant
- Pieces: core/labels/labels-vs-captures (core.md:303-306: the array holds the settings "as they stand where it is read"); array-vs-passes (core.md:313, ruled; every printed line puts the group question AFTER the outermost loop); core/conditions/in-sequence (core.md:520: "A condition written inside a loop, on the item, is a piece of every pass"); one-rule (core.md:347: an inner loop is entered anew each outer pass, which resets the LABEL, not the array: core.md:318 "a reset acts on the label only").
- Drill: a label looped at two depths, read from INSIDE the outer loop; edge in SECOND place.
- Witness (modes/w/w12.py), one definition: `((/(?:(?<h>\d),)+/ & some((h: "7"))) SEQ ";")+`.
  The array as it stands (earlier passes' settings included): WHOLE `7,;1,;` HOLDS, `1,;7,;` FAILS, `7,;` HOLDS / SEARCHED `x7,;1,;` `7,;1,;`@1 / FIND-ALL `7,;1,; 1,;7,;` [`7,;1,;`@0, `7,;`@10]
  The operand's own settings (this pass only; also MODES-2's chain reading): WHOLE `7,;1,;` FAILS, `1,;7,;` FAILS / SEARCHED `x7,;1,;` `7,;`@1 / FIND-ALL `7,;1,; 1,;7,;` [`7,;`@0, `7,;`@10]
  Under the worded rule the two group orders of the same items answer differently (`7,;1,;` HOLDS, `1,;7,;` FAILS): the "on the item" idiom ("every pass" written inside the loop, core.md:308, 520) does not give "every group has a 7" with a group question.
- Expected: array-vs-passes says what a group question written inside a loop reads (the settings so far, or the settings made inside its own operand/pass), with one line where the edge is the second pass.
- Effort: small. Blast radius: the every-pass idiom with a group question on the item; lib/counting/every-pass candidate (c) "a loop construct over a conditioned item".

### MODES-12  CONFIRMED  doc  -- every-pass: the settings form and the item form also part on a NEVER-ITERATED loop, which the piece does not name (it names only an optional label)
- Piece: lib/counting/every-pass (library.md, the changed bullet: "a pass that sets nothing is not judged, so where the label is optional it is not the item form"; its two lines use `+`, so a loop with no pass is never shown).
- Sub-part (b): a never-iterated loop and an empty array are two spellings of "no item".
- Witness (modes/w/w14.py): `/(?:(?<d>\d),)*x/ & some((d: "7")) & occurs.none(NOT (d: "7"))`: WHOLE `x` FAILS, `7,x` HOLDS / SEARCHED `-x` FAILS / FIND-ALL `x 7,x 1,x` [`7,x`@2]
  The item form `/(?:(?<d>\d)${(d: "7")},)*x/`: WHOLE `x` HOLDS, `7,x` HOLDS / SEARCHED `-x` `x`@1 / FIND-ALL `x 7,x 1,x` [`x`@0, `7,x`@2, `x`@8]
  With no optional label at all, the two forms part on zero passes (vacuous "every pass" vs `some`'s "false on an empty array"). `occurs.none(NOT c)` ALONE agrees with the item form here (true on an empty array, core.md:154).
- Expected: the bullet says "where the label is optional, or the loop can make no pass", or the candidate (b) names `occurs.none(NOT c)` without `some(c)` for the vacuous case.
- Effort: trivial. Blast radius: the every-pass-spelling question put to the owner.

## PROBED-AND-HELD

- Engine (modes/w/eng.py: PCRE path order, label reset on entering a branching, settings array, carried capture, the trailing empty pass kept) reproduces 6 printed lines exactly (Outside the loop, Outside the loop the label beside it, An empty array, the outermost view, every-pass "Every setting", pass-start-read "Pass 2"): calibration only, not re-derivation (EXAMPLES lens owns that). Minimum witness length reached: 1 character (`7`, `X`) up to 11 (`7,;1,; 1,;7,;`); every parting witness above needs 2+ settings and parts at length 3-6.
- HELD: group-truth's reading on one entry: `NOT some((d: "7"))` and `occurs.none((d: "7"))` give identical WHOLE (3 texts), SEARCHED and FIND-ALL (6 reports incl. 4 empty matches) on `/(?:(?<d>\d),?)*/`; `some(NOT c)` differs as stated (w13.py).
- HELD: nullable loop body (`/(?:(?<d>\d*);?)+/` vs `/(?:(?<d>\d+)?;?)+/`): PCRE (libpcre2 probe) keeps a trailing empty pass that SETS d to the empty string (array [`7`, ``]), but path backtracking rescues every condition tried (`(d: /\d+/)`, the every-setting form): identical answers in all three modes on 4 texts (w10.py). The empty setting shows only in a count on the FIRST path (both `(n: ==1)` and `(n: ==2)` hold on `7` by different paths), which the path model already states.
- HELD: `h[k]` with an optional label in a looped place, edge in second place: `/(?:(?<h>\d)?;)+/` on `3;;5;` and `3;5;` give h[2] = `5` alike (settings skip the empty pass), consistent with "a pass that sets nothing adds nothing".
- HELD: class-member hole lift vs hand class: `[${c}]` with c := [`9`, `0`] lifted gives `(?:10|1)`, one value `"90"` (one class, ascending) gives `(?:1|10)`, by the two ruled rules (lift-order, class-value) together; python `re` SEARCHED on `x10`: `10`@1 vs `1`@1. Defined (two spellings of one set part, but each by a ruled rule; not filed).
- HELD: flags through a binding in a hole (core/holes/flags "a binding in a hole inherits") does not conflict with nested-scope's sealing (values/names only).
- HELD: never-iterated loop: `occurs.none(NOT c)`, `NOT some(NOT c)` and the item form agree on `x` (all HOLD); only `some(c) & ...` parts (MODES-12).
- HELD (reasoned from the text, not run): `_` labels: a group question or flat read naming another binding's `_v` is the visibility error at top level, in a `count` argument and in a hole (statement 1 holds by place-free wording); `[x = A]` and `\k<x>` in one literal was already the free-name error before the label/capture split.

CRITIC COMPLETE modes 2026-11-21T23:58Z
