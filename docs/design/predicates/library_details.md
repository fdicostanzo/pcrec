# The predicate language: details (library)

One entry per tag of `library.md`, in the same order (fields as in `core_details.md`). The record
is `docs/design/plan_row_bodies/COND-FAMILY.md`; a skeleton entry's source is `predicates_draft.md` revision 29.1.

## lib/builtin/enumerate — Enumerate
was: core/arrays/enumerate (2026-11-19, a call-form name: the owner, "all macros "x()" should be in the library document"; the manager's ruling R-1 of lane preddoc4)
was: lib/builtin/enumerate/class-index (2026-11-19, merged: the owner's ruling class-positions answered class-index, "descending class value order"; lane predloop)
was: core/arrays/class-index (2026-11-19, merged with lib/builtin/enumerate/class-index, its later tag: the owner, "all macros "x()" should be in the library document"; the manager's ruling R-1 of lane preddoc4)
slugs: class-index
rulings:
- 2026-11-19 "quantified-order: keep pcre priority order and classes change to lowest to highest unless pcre priority order disagrees." (record: "2026-11-19 OWNER RULING — quantified-order: PCRE's priority order; and classes lowest to highest; sorting only when asked"); a class's members, in the array and in every lift, lowest to highest; PCRE's priority order kept inside a quantified operand
- 2026-11-19 "class-positions: nested loops, classes descending" (record: "2026-11-19 OWNER RULING — class-positions: nested loops, classes descending"); it answers class-index: a class's members in the array are in the one class order, descending then, lowest to highest since quantified-order
- 2026-11-19 "Enumerate() will output in written or for classes descending class value order." (record: "2026-11-19 OWNER, discussing class-positions: the nested-loop rule, as if against `fn()`; a `lengthSorted()` transform"); "in written or" read as "in written ORDER, or" (phone); the proposal the ruling adopted; its "descending" replaced by quantified-order
- 2026-11-14 "I love it. Enumerate go." (record: "2026-11-14 RULINGS on the predx gaps"); design adoption, with its rules: the budget, PCRE priority order, a built-in
rejected:
- widest first (one more copy first everywhere) as the order — by review r52 D (TABLES-4): it parts from PCRE priority on `(?:a|ab){1,2}` (SEARCHED `aba` `aba`@0 against `a`@0); preddoc3b sabotage s8 caught; predloop sabotage s10 caught.
- descending class value order, for the array and every lift (`enumerate(/\d/)` [`9`, `8`, .., `0`]; class-positions as ruled earlier the same evening) — by owner ruling — quantified-order, his reason: "It was to help the arithmetic common choice but if it doesn't completely then it shouldn't at all."; run: `/${enumerate(/\d/) + 1}/` SEARCHED `x10` `1`@1 ascending against `10`@1 descending, 0 / 250 / 570 of 3,906 (predasc EXenumclass, OLD; sabotage s11 caught).
- class-index (c), the longer result first, ties by codepoint — by owner ruling — class-positions: nothing is sorted by length.
readings:
- the enumerator's ORDER equals PCRE's own pattern on re-joining — SUPPORTED (preddoc3b EXenum: 0 / 0 / 0 of 63 texts; PART PR of predspec281 on libpcre2); re-run with classes ascending, the ruled example has no class and is unchanged (predasc EXenum: 0 / 0 / 0 of 63 texts, sabotage s10 caught).
- an interior lookaround or a backreference in the argument: NOT STATED (PART PR of predspec281).
- (the manager's (e) of class-positions, re-run under quantified-order) a class inside a larger rx enumerates as nested positions in text order, each class ascending: `enumerate(/[ab]\d/)` is [`a0`, .., `a9`, `b0`, .., `b9`] — SUPPORTED as rule-as-code (predasc EXpos, sabotage s12 caught); the letters' order rests on class-value.
- `enumerate(/\d/) + 1` = `\d + 1`, the array and the lift one order (follows from the ruling) — SUPPORTED (predasc EXenumclass: both `(?:1|2|3|4|5|6|7|8|9|10)`; EXwplus 0 / 0 / 0); class-index's candidate (b) ("the array's ascending codepoint order everywhere", its line SEARCHED `x10` `1`@1) and (a) (ascending for the array) now coincide with the ruled order for digits (a reading).
evidence: preddoc3b EXenum, EXclassindex; PART CO of predspec291 (P29-10); predloop (superseded by predasc: predloop's model asserts the retired descending order and is red at the tip by design) EXenum, EXenumclass, EXpos; predasc EXenum, EXenumclass, EXpos, OLD.
history:
- 2026-11-14: "Enumerate go"; the draft §5.5. 2026-11-18: construction-line made it the line of single-value functions. 2026-11-19: class-order replaced the codepoint lean for lifts.
- 2026-11-19 (lane preddoc3b): converted from `?`.
- 2026-11-19 (lane preddoc4): moved to the library, section `lib/builtin` (the owner's direction of 2026-11-19, R-1).
- 2026-11-19 (lane preddoc6, review r60 FIXVER-7): `see: lib/builtin/enumerate/class-index core/arrays/class-order` added: the body depends on the forward piece class-index, and the pointer was lost in the move from the core (r59 READ-17's eleventh pair).
- 2026-11-19 (lane predloop): class-positions. Status date 2026-11-14 to 2026-11-19; statement before: "`enumerate(rx)` lists a finite rx's strings one per entry, in PCRE's priority order; an edge assertion in it, or an infinite or over-budget rx, is a compile error." The bullet "A class's members have no PCRE order; for a lift see core/arrays/class-order, for the entries' own order lib/builtin/enumerate/class-index." replaced by the descending order; class-index merged here; `needs:` gains core/arrays/class-order, `see:` names class-value.
- the piece lib/builtin/enumerate/class-index (open class-index; merged here by lane predloop), its history: new with class-order; re-worded by review r54 P29-10; moved to the library by lane preddoc4. Its statement: "The order of a class's members in `enumerate`'s array (`.index`, `each`, a lift of `enumerate(X)`) is a question for the owner." Its candidates: (a) codepoint order for the ARRAY, the class order for a lift; (b) the array's codepoint order everywhere; (c) the longer result first, ties by codepoint. Its readings line: "(a) is the draft's reading (rev 29's narrowing of the codepoint lean, not the ruling's words) — the record says the lean "is replaced", with no carve-out; (a) vs (b) 0 / 250 / 570 of 3,906; (a) vs (c) 0 / 0 / 0 (PART CO of predspec291)." Its printed lines: (a) `/${enumerate(/\d/) + 1}/` WHOLE `10` HOLDS / SEARCHED `x10` `10`@1 / FIND-ALL `10 3 11` [`10`@0, `3`@3, `1`@5, `1`@6] (kept, now the ruled answer); (b) SEARCHED `x10` `1`@1, FIND-ALL [`1`@0, `3`@3, `1`@5, `1`@6] (rejected).
- 2026-11-19 (lane predasc): quantified-order. Statement before: "`enumerate(rx)` lists a finite rx's strings one per entry, in PCRE's priority order, a class descending; an edge assertion in it, or an infinite or over-budget rx, is a compile error." Bullets before: "A class gives its members in "descending class value order", in the array and in a lift alike: `enumerate(/\d/)` is [`9`, `8`, .., `0`], so `.index` counts from the top and `enumerate(/\d/) + 1` is `\d + 1` (core/arrays/class-order). The value of a class that is not digits: lib/builtin/enumerate/class-value."; "Positions nest in text order, each class descending: `enumerate(/[ab]\d/)` is [`b9`, `b8`, .., `b0`, `a9`, .., `a0`] (a reading, run; the letters' order is class-value's)." The example line before: `/${enumerate(/\d/) + 1}/` WHOLE `10` HOLDS / SEARCHED `x10` `10`@1 / FIND-ALL `10 3 11` [`10`@0, `3`@3, `1`@5, `1`@6]. Rejected items it moves out of `rejected:` (each rejected by class-positions' "descending", which quantified-order replaced), verbatim: "codepoint (ascending) order for a class's members in a lift — by owner ruling — class-order, then class-positions (descending) (core/arrays/class-order)."; "class-index (a), codepoint ascending for the ARRAY and the class order for a lift (`enumerate(/[-\/.]/)` [`-`, `.`, `/`]) — by owner ruling — class-positions: one order, descending, for the array and every lift."; "class-index (b), the array's ascending codepoint order everywhere (`/${enumerate(/\d/) + 1}/` SEARCHED `x10` `1`@1) — by owner ruling — class-positions; run: the loop gives `10`@1 (predloop EXenumclass, sabotage s11 caught).". Readings before, verbatim: "(the manager's (e) of class-positions) a class inside a larger rx enumerates as nested positions in text order, each class descending: `enumerate(/[ab]\d/)` is [`b9`, .., `b0`, `a9`, .., `a0`] — SUPPORTED as rule-as-code (predloop EXpos, sabotage s12 caught); the letters' order rests on class-value."; "`enumerate(/\d/) + 1` = `\d + 1`, the array and the lift one order (follows from the ruling) — SUPPORTED (predloop EXenumclass: 0 / 0 / 0 by RB)."
- 2026-11-22 (lane predfix77, review r77 D2 (FIXIND-14), D11 (GENERAL-10); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): status date 2026-11-19 to 2026-11-21 (class-value, class-hole-order); "Every class is in ascending codepoint order" became "Every written class ...; a class holding a hole is an alternation of classes (core/holes/class)".

## lib/builtin/enumerate/class-value — The value of a class's members
slugs: class-value
rulings:
- 2026-11-21 "ascending codepoints everywhere makes sesne." (record: "2026-11-21 OWNER RULING — class-value: ascending codepoints everywhere"); "sesne" read as "sense"; answer (a) of the question as asked; with it, not asked as a ruling: "it is more natural to enumerate classes lowest to highest. alternation order should be decided by transform anyway for consistency."
- 2026-11-19 "class-positions: nested loops, classes descending" (record: "2026-11-19 OWNER RULING — class-positions: nested loops, classes descending"); NOT ANSWERED by it: what "class value" is for a class that is not digits (asked in the same turn, left open)
- 2026-11-19 "classes change to lowest to highest unless pcre priority order disagrees" (record: "2026-11-19 OWNER RULING — quantified-order: PCRE's priority order; and classes lowest to highest; sorting only when asked"); NOT ANSWERED by it either: what "lowest to highest" is for a class that is not digits
- 2026-11-19 (class: DISCUSSION) "if i allowed letters, the + would define the order as digits followed by letters as per normal." (record: "2026-11-19 OWNER, discussing the base idea: numbers are strings over an ordered set of symbols"); with "a" + "b" meaningful "when those types are defined as part of an ordered set of symbols (ie. not as written)"; candidate (b)'s ground; not a ruling
rejected:
- (b) the order of a declared ordered symbol set ("digits followed by letters as per normal"), as `enumerate`'s order for a class — by owner ruling — class-value ("ascending codepoints everywhere"); the idea itself stays parked (parked/ideas/class-base); run under the ruled order: `enumerate(/[\dA-Fa-f]/)` is `0123456789ABCDEFabcdef` (classvalue.py, the manager's scratch run, not a lane's evidence).
readings:
- (the manager's (a) of class-value) a caseless single character is a class for this rule, `(?i)k` enumerating `K`, `k`, U+212A — SUPPORTED as to the ORDER: python `re` (str mode, IGNORECASE) over every codepoint gives U+004B, U+006B, U+212A, ascending (predscope_model.py CASELESS; sabotage s14 caught); UNTESTED that a caseless single character is a class for `enumerate` (no ruling says so), and which members libpcre2 gives in each mode (UTF, UCP, byte) is a PCRE2 fact this lane does not look up (D181; a question for a pcre2-reader).
- (the manager's (b) of class-value) "codepoint" in a byte-mode program is the byte value — UNTESTED (untestable: it defines a word; no ruling speaks of byte mode). Run for orientation: python `re` bytes mode, `[A-C\xe9\x80]` by byte value is 0x41, 0x42, 0x43, 0x80, 0xe9, the same as the Latin-1 codepoint order (predscope_model.py BYTES; sabotage s15 caught).
- (the manager's (b) of quantified-order) ascending codepoint, so `enumerate(/[abc]/)` is [`a`, `b`, `c`] and `.index` counts from the bottom — RULED 2026-11-21 (class-value), no longer a reading; the enumerator under that reading prints [`a`, `b`, `c`] (predasc EXpos, sabotage s12 caught).
- no match shows the order (one-character members never compete; no defined function on letters gives competing results) — a reading, UNTESTED beyond `\w + 1` = `\d + 1` (predasc EXwplus: the letters give nothing; earlier predloop EXwplus).
evidence: predloop (superseded by predasc: predloop's model asserts the retired descending order and is red at the tip by design) EXpos, EXwplus; predasc EXpos, EXwplus, PCREORD.
history:
- 2026-11-21 (the manager, one ruling): class-value RULED. Status `open class-value 2026-11-19` to `ruled 2026-11-21`; `defined: ?` to native. Statement before: "What "lowest to highest" means for a one-character set position that is not digits (`[abc]`, `\w`, `.`, a caseless `(?i)k`) in `enumerate`'s order is a question for the owner." Its candidates before: "(a) ascending codepoint (the manager's reading today, not ruled): `enumerate(/[abc]/)` is [`a`, `b`, `c`] and `.index` counts from the bottom (`a` is 1); (b) the order of a declared ordered symbol set, as in the owner's discussion of numbers over symbols". The bullet "PCRE orders no position that takes one character from a set" dropped with the question.
- 2026-11-19 (lane predloop): a new open sub-piece, the question the ruling left open.
- 2026-11-19 (lane predfix61, review r61 F-K: RULING-8, REACH-7, GENERAL-7): the statement until then: "What "lowest to highest" means for a class that is not digits (`[abc]`, `\w`, `.`) in `enumerate`'s order is a question for the owner." Its bullet until then: "The reading today (the manager's, not ruled): ascending codepoint, so `enumerate(/[abc]/)` is [`a`, `b`, `c`] and `.index` counts from the bottom (`a` is 1). The other candidate: an order the owner names." Now: his earlier discussion quoted, parked/ideas/class-base pointed at, the ordered symbol set named as candidate (b), and the caseless single character in the question (predfix61 FK: `(?i)k` takes `K`, `k`, U+212A; `(?i)[\da-f]` by codepoint `0..9A..Fa..f`).
- 2026-11-19 (lane predasc): quantified-order turned the class order to lowest to highest; the question stays open, restated. Statement before: "What "class value" orders a class that is not digits (`[abc]`, `\w`, `.`) in `enumerate`'s descending order is a question for the owner." Bullet before: "The reading today (the manager's, not ruled): descending codepoint, so `enumerate(/[abc]/)` is [`c`, `b`, `a`] and `.index` counts from the top (`c` is 1). The other candidate: an order the owner names." Reading before, verbatim: "(the manager's (a) of class-positions) the codepoint, so `enumerate(/[abc]/)` is [`c`, `b`, `a`] and `.index` counts from the top — UNTESTED as a rule (an owner question); the enumerator under that reading prints [`c`, `b`, `a`] (predloop EXpos)."
- 2026-11-21 (lane predscope): the manager's two readings tested (above); the printed lines re-run: `[\dA-Fa-f]` 0123456789ABCDEFabcdef (A 11, a 17), `[a-cB]` B a b c (predscope_model.py CLASSV, python `re` over the codepoint range; sabotage s16 caught). The piece unchanged.
- 2026-11-22 (lane predfix77, review r77 D8 (RULING-10), D11 (GENERAL-10); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): statement until then, verbatim: "A class's members are enumerated in ascending codepoint order, every class alike: "ascending codepoints everywhere makes sense"." His word is "sesne" (read as "sense"), now quoted as he wrote it; "every class" became "every written class". The sort bullet marks his sentence an observation and cites the ruled "Only solution is sorting output when needed." (core/arrays/class-order) instead.

## lib/builtin/import — import
was: core/modules/import (2026-11-19, a call-form name: the owner, "all macros "x()" should be in the library document"; the manager's ruling R-1 of lane preddoc4)
was: parked/import-symbols/import (2026-11-19, ruled by the owner: it is in the language)
slugs: import-several
rulings:
- 2026-11-19 "import-several: yes. if you can bind multiple arguments simultaneously, thent this is more expressive. before you could only bind one so what did multiple files mean? although, good point, if the binding is just 1 symbol, then its a map of all the values of the files combined." (record: "2026-11-19 OWNER RULING — import-several: an import may name several files; one name bound to it is the combined map")
- 2026-11-17 "So if I use a li library element that causes non-dfa behavior then it should error out" (record: "2026-11-17 OWNER — a library element beyond the user's level is an ERROR"); RULED for libraries (the record): a library element that needs more than the level the user asked for is a compile error, never a silent lift; his "good ideas" on scope and a host cap are not ruled
rejected:
- it must resolve to EXACTLY ONE file; several matches a compile error (the 2026-11-14 addendum; the draft §7) — by owner ruling — import-several ("before you could only bind one so what did multiple files mean?").
- `import weekday as wd` for a clash (the manager's 2026-11-14 lean) — by owner ruling — no alphabetic keywords; the rename is now `(wd = weekday) := ...` (core/modules/binding-list).
readings:
- zero files matched stays a compile error (the manager's reading of import-several) — UNTESTED (a refusal).
- the argument is a set of names, an rx over file names, consistent with export: the 2026-11-14 addendum as the record paraphrases it ("Addendum (Frank)", record: "2026-11-14 — import/export as functions"), not his verbatim words; its "exactly one file" half reversed by import-several — SUPPORTED by import-several's ruling, which keeps the set of names.
- compile time only, pinned by `sha256`, configured directories only (the manager's 2026-11-13 design; the draft §7, LEAN) — UNTESTED.
evidence:
history:
- 2026-11-13: `d := import("isodate")`; 2026-11-14: import/export as functions, its follow-up and addendum; 2026-11-19: several modules in one import, then import-several.
- 2026-11-19 (lane preddoc3b): the parked placeholder parked/import-symbols/import is retired into this section (the owner ruled import-symbols); its slug `import-symbols` is on core/modules/binding-list.
- 2026-11-19 (lane preddoc4): moved to the library, section `lib/builtin` (the owner's direction of 2026-11-19, R-1).
- 2026-11-19 (lane preddoc5): the level bullet added with its ruling (review r59 COMPA-8); the 2026-11-14 addendum item ("import(...)'s argument is a set of names ...", the record's paraphrase, not his words) moved from `rulings:` to the readings (review r59 RULING-4).

## lib/builtin/import/filter — A filter inside the import
was: core/modules/import-filter (2026-11-19, a call-form name: the owner, "all macros "x()" should be in the library document"; the manager's ruling R-1 of lane preddoc4)
slugs:
rulings:
- 2026-11-19 "one could filter but it would have to be inside the import("file1"|"file2", search(string))" (record: "2026-11-19 OWNER RULING — import-several: an import may name several files; one name bound to it is the combined map"); an IDEA in the ruling's answer
rejected:
readings:
- NOT STATED: the filter before or after the conflict check.
evidence:
history:
- 2026-11-19: his first instinct already filtered inside the import (`import("blah", /left|right/)`); the idea in import-several.
- 2026-11-19 (lane preddoc4): moved to the library, section `lib/builtin` (the owner's direction of 2026-11-19, R-1).
- 2026-11-19 (lane preddoc6, review r60 COLD-2): his `search(string)` marked a placeholder in the base: `search` is the name the owner renamed `occurrences` (core/modules/naming); the statement before quoted it as the form.

## lib/builtin/export — export
slugs: export-choice
rulings:
rejected:
- `export([leap])`, an array of names (`[leap, weekday]` is `leap | weekday`, names lost) — by the manager's 2026-11-14 analysis, (3) (record: "2026-11-14 — import/export as functions").
- `export(leap, weekday)` receiving names (a macro seeing argument expressions) — by the manager's 2026-11-14 analysis ("a meta feature; avoid").
readings:
- the record: "Export choice PENDING Frank" (record "2026-11-14 — import/export as functions", the options (a) `export([leap = leap, ...])`, (b) every top-level binding exported unless its name starts with `_`, (c) `export(leap, weekday)`; the manager's lean (b)); never answered, so the piece is `open` under the slug export-choice (the manager's name for the pending choice, given by lane preddoc6 at the predicate manager's ruling of 2026-11-19).
- `@export(names)`, the names a set of strings (`export(["leap", /[^_].*/])`, `export(/[^_].*/)`), and the no-export error ("library exports nothing"; no silent default): the manager's lean in the follow-up to his `export(["leap", !startsWith("_")])` (the same record entry; the draft §7, LEAN) — UNTESTED (no matching involved).
- `@` marks a compile-time EFFECT macro (his "a prefix designating side-effect macros"; the manager's lean (3) in the follow-up) — UNTESTED.
- the `_` rule, candidate (b)'s ground, is RULED for what `.` reaches (export-rule; import-symbols statement 3: core/labels/export, core/modules/map); whether it is the whole of export is what export-choice asks — the manager's reading.
evidence:
history:
- 2026-11-14: import/export as functions (options (a)-(c), lean (b)), its follow-up (lean `@export(names)`).
- 2026-11-19 (lane preddoc6, review r60 EFFECTS / COLD-1 / FIXVER-6 / RECOUNT-3 / RULING-7): a new piece. The core sentence "Every provided name written as a call has its piece in the library, these included" (core/operators/statements) named `@export`, `@warn`, `@options` with no library piece; the predicate manager ruled (2026-11-19) the `@` effects call-form names, so each has its library piece, `defined: native`, status by the record. `@export(names)` was defined in core/modules/export, which keeps the meaning (what a file exports is chosen among its public names).

## lib/builtin/pattern — pattern
slugs:
rulings:
rejected:
- a coercion inside a macro body (`pattern(arg)` turning a caller's `$x` into the group's shape) — by the record (the manager's leaning, "no silent conversions") — a parameter kind `pure` marks the need instead (parked with typed parameters).
readings:
- the built-in `pattern($x)`, the group's static pattern, PURE although it mentions a label; union of duplicate definitions; flags as compiled in place; inner named groups as fields; "not self-contained" an error — the manager's leaning in the record's 2026-11-14 00:10 notes (his question: how to get the group's PATTERN without its match); LEAN in the draft (§13 O48), OUT of phase 1 (the draft's census, CF:889).
- `/(?<x>\d+),${pattern($x)}/` is `(?<x>\d+),(?:\d+)`: WHOLE `12,345` HOLDS / SEARCHED `1,2`@1 / FIND-ALL [`1,22`@0, `3,4`@5] — SUPPORTED (preddoc4 PART PT; sabotage s12, the backreference, caught).
- for a part label `[x = A]` (no group in rx text) `pattern($x)` is A's pattern (review r77 FIXIND-8) — UNTESTED (a reading).
evidence: docs/dev/lanes/preddoc4_evidence/ PART PT.
history:
- 2026-11-19 (lane preddoc4): a new piece: a name on the closed built-in list with no piece (review r59 COMPB-3).
- 2026-11-22 (lane predfix77, review r77 D12 (FIXIND-8); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): a bullet for a part label (pure-label: `[x = A]` is no longer "the group form").

## lib/builtin/eval — eval
slugs:
rulings:
rejected:
readings:
- the record's "2026-11-14 — runtime eval (Frank: with the dynamic automaton and pcrec as a library, `x := eval(...)` for a dynamic rx; restriction DFA; opaque; effectively a callout)": an IDEA; only as an explicit MODULE ("requires module 'eval'" otherwise) with a BUDGET; the same automaton code as compile-time `records()` — named, not defined: `under-construction`.
evidence:
history:
- 2026-11-19 (lane preddoc4): a new piece: a name on the closed built-in list with no piece (review r59 COMPB-3).

## lib/builtin/warn — @warn.off, @warn.error
slugs:
rulings:
- 2026-11-14 "I agree but warnings need names and the user must be able to disable them (wildcard?)" (record: "2026-11-14 RULING — the empty-match hazard"); control via `@` effects, `@warn.off(...)` and its reverse `@warn.error(...)` (the record)
- 2026-11-14 "use an rx instead of wild card purely for consistency" (record: "2026-11-14 RULING — the empty-match hazard"); its amendment: a selector is a set of names as an rx, no `*` wildcard
- 2026-11-17 "The suppression could be @config.warn.off(/compare\.width\..*/)" (record: "2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path"); suppression selects by a pattern over the names (his spellings placeholders)
rejected:
- a `*` wildcard in a selector — by owner ruling — the amendment: `"*"` is the literal name and draws `warn.unused`.
readings:
- the reach "rest of file", a per-binding form (spelling open) and a whole-build compiler option ("like -Wno-"): the manager's proposal inside the ruling entry — UNTESTED (no matching involved).
- `@warn` an EFFECT built-in, reserved after `@` only (the draft §5.1, review r10 CENSUS-7; LEAN) — UNTESTED.
evidence:
history:
- 2026-11-14: the empty-match hazard ruling and its amendment; 2026-11-17: the names, the library path, the `pcrec.` prefix (core/diagnostics/warnings).
- 2026-11-19 (lane preddoc6, review r60 EFFECTS): a new piece; the selector rule stays stated in core/diagnostics/warnings, this piece is the name.

## lib/builtin/options — @options.strict
slugs:
rulings:
- 2026-11-17 "polarity-rule: warning for both. Warnings are errors given some strictness setting eg @config.strict()" (record: "2026-11-17 OWNER RULING — polarity-rule"); (2) warnings become errors under a strictness setting declared in the source
- 2026-11-17 ""One reading of mine: the setting covers...": @options.strict(/no-fail/)" (record: "2026-11-17 OWNER RULING — polarity-rule"); the ADDENDUM, same evening: strictness is SELECTIVE, a pattern over warning names; it corrects the manager's reading "the setting covers every warning"
rejected:
- the strictness setting covering every warning by default (the manager's reading) — by owner ruling — the polarity-rule addendum (`@options.strict(/no-fail/)`).
readings:
- `@options` as the family of the capability opt-ins (record "2026-11-17 OWNER IDEA — options written in the language", an IDEA, not a ruling: "Perhaps there should be an @options() in the language") — parked (parked/ideas/capability-optins).
- `@config.strict()` and `@options.strict(...)` are one setting under two placeholder spellings (D193 add. 4) — the manager's reading.
evidence:
history:
- 2026-11-17: polarity-rule and its addendum.
- 2026-11-19 (lane preddoc6, review r60 EFFECTS): a new piece; `@options.strict` was stated only in core/diagnostics/warnings.

## lib/modifiers/padded — padded
was: lib/modifiers/unpadded (2026-11-19, a piece that only said the name is not provided; its content is a rejected line here (review r59 READ-13))
slugs: padded-width padded-order padded-lazy-sparse cut-unpadded
rulings:
- 2026-11-15 "padded(rx) := /0*${rx}/" (record: "2026-11-15 RULING — `padded` is the plain macro `padded(rx) := /0*${rx}/`")
- 2026-11-18 "padded-width: minimum" (record: "2026-11-18 OWNER RULING — padded-width: minimum")
- 2026-11-19 "i agree with your lean" (record: "2026-11-19 OWNER RULING — padded-order")
- 2026-11-19 "padded-lazy-sparse: stated behavior." (record: "2026-11-19 OWNER RULING — padded-lazy-sparse; with remarks on `padded`'s width, a `limited` macro, and a direction on macros")
- 2026-11-15 "cut-unpadded: agree" (record: "2026-11-15 RULING — `unpadded` is cut from the first spec")
rejected:
- exact width (a value longer than n is nothing) — by owner ruling — padded-width; the run: `9999-10000` FAILS under it (preddoc3c PART PW, sabotage s3 caught).
- the exact-width branch first, `(/0*${rx}/ & /(?s:.){${n}}/) | (rx & /(?s:.){${n},}/)` — by owner ruling — padded-order (the lean taken: any-length first); it differs SEARCHED on `x0129` (`012`@1) (PART PW, sabotage s1 caught).
- the argument's own order (each member zero-filled to at least n, in enumerate's order) as the definition — by owner ruling — padded-order replaced it by the body's order; no single body keeps it for an infinite argument (the draft's rev 28.1 PART PO).
- an error for a lazy or shortest-first argument — by owner ruling — padded-lazy-sparse.
- a modifier's argument as a filter matched whole of its own (the draft's old row L13: `padded(/^5/)` = `padded("5")`) — by owner ruling — the plain macro: the argument is spliced into a hole, so `^` forbids the zeros (PART PA).
- `0?` for the zeros arm — by run — `2025-002026` would fail (the draft's rev 28.1 PART PW; preddoc3c PART PW, sabotage s2 caught).
- `unpadded` as a provided name (it read the subject as if zero-padded, `9:00` tested as `09:00`: text the subject does not contain, so no body in the language says it) — by owner ruling — cut-unpadded; a time range is written with split fields and number conditions, `/(?<h>\d{1,2}):(?<m>\d\d)/ & (h: padded(between(9, 10)))` with the minute condition its end needs.
- rev 2's `pad(n)` (the filter reads a subject as if zero-padded to width n) — by the draft (it became `unpadded(n, S)`, then cut-unpadded) — its zeros are not in the text; it was the draft's addition, not his ruling (the draft §9).
readings:
- the two-argument body `padded(rx, n) := (rx & /(?s:.){${n},}/) | (/0*${rx}/ & /(?s:.){${n}}/)` reproduces every printed answer of the width form: five argument orders (`(?:\d\d)+?` n = 3, `\d{2,3}`, `1|0123`, `\d|\d\d\d|\d\d`, `\d+?` n = 2) and the two value-hole programs — SUPPORTED (preddoc3c PART PW; sabotages s1, s2, s3 caught).
- the one-argument body reproduces `5`, `05`, `005`; `padded(/^5/)` only `5`; `/1|2/` on `02`; `padded(between(0, 255))` on `000`; `padded(between(1, 12))` rejects `00` — SUPPORTED (PART PA; sabotage s4, the raw paste without the hole's group, caught).
- "a macro whose body is one filter or one sequence keeps the argument's order; an alternation of filtered copies imposes its own" (the manager's reading in the padded-lazy-sparse entry) — UNTESTED here as a general law; it is what PART PW shows for `padded`.
- his remark "i suspect it will always be broken for some use case and 0* will be default" is an OBSERVATION: the default (no width) is `0*`, as ruled; nothing reversed — the base says so.
- his bounding observations ("restrict it to the rightmost 4", "<=9999") are compositions over the minimum form, not rules (the draft §2.7, rev 28's PART PW).
evidence: preddoc3c PARTS PA, PW; the draft's rev 28 PART PW, rev 28.1 PART PO, rev 29 PART PO, rev 29.1 PART PO (predspec291); `$PCREC_TMPDIR/scratch/pred/padlazy.py` (the record).
history:
- 2026-11-15: the plain macro; "Give or take details" (the group around the splice the spec writer's).
- 2026-11-18: the width form, minimum (rev 28); the exact-first body as the draft's reading.
- 2026-11-19: padded-order (any length first); padded-lazy-sparse (stated behaviour); `limited` proposed the same day (lib/modifiers/limited, parked/ideas/limited).
- 2026-11-19 (lane preddoc3c): the skeleton converted in full.
- 2026-11-19 (lane preddoc4): the body's counts written as holes, `{${n},}` and `{${n}}` (record: "2026-11-19 MANAGER — the withdrawal above is itself CORRECTED: taking a tuple apart is OPEN (tuple-parts), not confirmed; and a slip in the padded body", item 2); built from its text the old body never matches (`{n,}` is literal text): preddoc4 PART PD, sabotage s1. `by: core/principles/stated-behaviour` dropped (review r59 RULING-1: the principle was coined from this piece).
- (from lib/modifiers/unpadded) his reason: "The issue is numbers compare right aligned and strings left." The natural-order range he filed instead (digit runs compared as numbers, a way of comparing chosen where the range is written) is a later item with its trigger in the same entry ("a real example where splitting fields is too clumsy"); not an ideas-file item.
- (from lib/modifiers/unpadded) 2026-11-15: cut (rev 14); the time-range example rewritten with split fields.
- (from lib/modifiers/unpadded) 2026-11-19 (lane preddoc3c): the `?` piece written as "not provided".
- 2026-11-19 (lane preddoc4): the piece `lib/modifiers/unpadded` deleted, its content moved here (review r59 READ-13).
- 2026-11-19 (lane preddoc6, review r60 COLD-9): a bullet points at the open question core/operators/bindings/call-forms: the two bodies are chosen by the call form, which the core's macro rule does not provide for.

## lib/modifiers/quoted — quoted
was: lib/modifiers/json-quoted (2026-11-19, a piece that only said the name is not provided; its content is a rejected line here (review r59 READ-13))
slugs: cut-json-quoted
rulings:
- 2026-11-14 "The problem is the name. Trim or unpad imply they are doing something to the subject. But they are not. They are changing the filter to ignore elements of the subject." (record: "2026-11-14 RULING — OWN-1, transforms are FILTER MODIFIERS")
- 2026-11-15 "cut-json-quoted: agree. It would necessitate a callout or similar? We have unrelated plans for dfa compatible callouts and that could be one" (record: "2026-11-15 RULING — `json.quoted` is cut from the first spec")
rejected:
- the plain splice `quoted(S) := /"(?:${S})"/` — by run — its `^` reads the stretch before the quote, so `quoted(/^a\w*/)` never matches (0 of 121 texts over `"ab`; preddoc3c PART QU, sabotage s13 caught).
- `json.quoted` as a provided name (it tested S against the DECODED string, `\u0041` read as `A`, which is not in the text) — by owner ruling — cut-json-quoted; the `json` module keeps `json.string`, the literal's rx.
- rev 2's `jstr(p)` (a JSON string literal read as its decoded text) — by the draft (it became `json.quoted`, then cut-json-quoted) — the decoded string is not in the text (the draft §9).
readings:
- the body `/"${S & /[^"]*/}"/` while the quoted text holds no escape (the draft's LEAN, §2.7 bodies table) — SUPPORTED for its one printed claim (PART QU).
- the names `padded`, `any_case`, `quoted`, `length`, `month_numbered` are ruled (OWN-1's list); the bodies are the draft's.
evidence: preddoc3c PART QU.
history:
- 2026-11-14: named in OWN-1; 2026-11-15 (rev 14): the body with `&` inside the hole (the draft).
- 2026-11-19 (lane preddoc3c): converted.
- (from lib/modifiers/json-quoted) a DFA-compatible callout (his pointer) or a finite-state decoding rewrite could bring it back (the manager's answer in the entry); a follow-up with `any_case`'s basis.
- (from lib/modifiers/json-quoted) 2026-11-15: cut (rev 16).
- (from lib/modifiers/json-quoted) 2026-11-19 (lane preddoc3c): the `?` piece written as "not provided"; `module: json` from the draft ("the `json` module keeps `json.string`").
- 2026-11-19 (lane preddoc4): the piece `lib/modifiers/json-quoted` deleted, its content moved here (review r59 READ-13).

## lib/modifiers/any-case — any_case
slugs: any-case-body primitive-transforms
rulings:
- 2026-11-15 "primitive-transforms: I understand why any_case is currently a primitive. I'd like to look for more fundamental ways of reducing that like some option setting primitive that any_case is built on or something else. I am ok with that being a followup." (record: "2026-11-15 RULINGS — tuple compare in the first library; `any_case` stays a primitive for now, a more fundamental basis is a FOLLOW-UP")
rejected:
- one "reading primitive" for `any_case` and `json.quoted` ("S matched whole on what the transform reads") — by owner ruling — not adopted (the same entry).
- `any_case(S) := each(folded, enumerate(S))` over a spelled lowers/uppers table — not taken as the definition (the draft §13; it needs a finite S).
readings:
- the candidate body `/(?i:${rx})/` equals the primitive for an argument writing no case flag: `/ho/` 0 / 0 / 0 of 781 texts (`hHoO1`, length <= 4) — SUPPORTED (preddoc3c PART CA; sabotage s17 caught).
- it differs for an argument writing `(?-i)`: `any_case(/(?-i)ho/)` 3 / 246 / 249 of 781 (the draft's printed counts) — SUPPORTED, reproduced (PART CA).
- it differs for a NEGATED filter operand: `any_case(/[abAB]{2}/ & !/ab/)` 4 / 168 / 216 of 781 (`aAbB `), the primitive WHOLE `aB` HOLDS / SEARCHED `x aB ab` `aB`@2 / FIND-ALL `ab aB AB` [`ab`@0, `aB`@3, `AB`@6], the body (the `(?i)` reaching `!/ab/`) FAILS / FAILS / [] — SUPPORTED, reproduced (PART CAneg).
- the primitive's argument is a whole-match role on the CASE-FOLDED reading of the stretch (the manager's LEAN, §2.7) — UNTESTED (no row rests on it).
- status: held `open any-case-body` by the manager (the brief of lane preddoc3c); the question was never put to the owner.
- a third parting: `any_case(/[a-z]x/ & /[A-Z]x/)` (the sides take the flag first, core/holes/flags/in-filter) — SUPPORTED by a run (predfix77 ANYCASE: over the 820 texts on `aAbBxXzZ7` to length 3 the body holds WHOLE on 16, as python `re` with each side under re.I does, the native definition on none, the argument having no member; sabotage s12 caught; the review's anycase.py found the same 16).
- the `pcrec.flags.filter` warning fires inside the body on that argument, the warning the caller's to read (review r77 A7) — UNTESTED (a reading).
evidence: preddoc3c PARTS CA, CAneg; the draft's rev 28 PART AC, rev 28.1 PART FF, rev 29 PART AC, rev 29.1 PART AC. predfix77_model.py ANYCASE.
history:
- 2026-11-15: a primitive for now, the basis a follow-up ([PRED-REREAD], the draft §13 O70).
- 2026-11-18 (rev 28): flags-propagate re-ran the candidate body; rev 28.1: the `(?-i)` difference; rev 29: T-c, equal for plain and positive filter-role arguments; rev 29.1: the negated operand differs; any-case-body named as a gap, not asked.
- 2026-11-19 (lane preddoc3c): converted, `open any-case-body`.
- 2026-11-22 (lane predfix77, review r77 A7; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): the standing reading's "every mode except two" was false since flags-in-filter (sides first); the third exception, the warning's behaviour and two lines added; the candidates read "those three".

## lib/modifiers/limited — limited
slugs:
rulings:
rejected:
readings:
- `limited(rx, n)` modelled as the filter `rx & /(?s:.){0,n}/` ("at most n", the manager's reading of "limited"): `limited(padded(digits), 5)` covers `00000` through `99999` AND every shorter digit string; with `digits := /\d+/`, `padded(digits)` is the same set as `digits`; "exactly n" gives other answers — the record's run, not settled (the record's INCONSISTENCY 1 and 2, told to him).
evidence: the record's `$PCREC_TMPDIR/scratch/pred/limited.py` run (the padded-lazy-sparse entry).
history:
- 2026-11-19: his words: "we need a limited(rx, 5) macro so limited(padded(digits), 5) which would cover all digits 00000 through 99999 which i think the way it would work mostly in the field. ... you could also say padded(limited(digits,5)) and the padding could be infinite." (record: "2026-11-19 OWNER RULING — padded-lazy-sparse; with remarks on `padded`'s width, a `limited` macro, and a direction on macros"); classed there an IDEA / PROPOSAL; his direction the same day: no deep dive into one macro.
- 2026-11-19 (lane preddoc3c): a new piece, `under-construction` (the manager's brief: a direction acknowledged, not defined); the ideas-file item 36 stays parked/ideas/limited.

## lib/modifiers/length — length
slugs:
rulings:
- 2026-11-14 "The problem is the name. Trim or unpad imply they are doing something to the subject. But they are not. They are changing the filter to ignore elements of the subject." (record: "2026-11-14 RULING — OWN-1, transforms are FILTER MODIFIERS")
rejected:
- `length(<=20)` read as an IMAGE function — by owner ruling — OWN-1 superseded the image forms (`unpad(S)`, `length(<=20)`).
readings:
- the body `chars & (nchars: S)` gives the length (S in ==0, ==3, ==20, ==21, <=20, even; the empty text, a newline, 20 and 21 characters) — SUPPORTED (preddoc3c PART LE; sabotage s21 caught); the draft's review r16 emulation, 27 cases, 0 differ.
- under array-vs-passes `nchars := count((ch: /(?s:.)/))` counts the SETTINGS of `ch`, one per character: the printed line is the same under both readings — SUPPORTED (predarr CHANGED, the helpers read from library.md).
- caveats (the draft's): two helper bindings beside the body; `count`'s budget applies to `nchars`; the label `ch` visible.
- `chars` re-spelled with a part label, `([ch = /(?s:.)/])*`, leaves every printed `length` line unchanged (review r77 D4; the brief's reading 4) — SUPPORTED by a run (predfix77 CHARS: the one printed line rebuilt from the old body and from the new, both equal to the printed text; the old body makes the capture `ch`, the new none; sabotage s11 caught).
- `nchars` is a computed count bound alone, so it rests on the open core/holes/bare-condition/bound-condition (under his position (b) it would be refused) — UNTESTED.
evidence: preddoc3c PART LE; review r16 `bodies_check.out`. predfix77_model.py CHARS.
history:
- 2026-11-14: named in OWN-1; 2026-11-15 (rev 15): a body (review r16 FIXIND-3).
- 2026-11-18: his `length($y)` (an image) is written `strlen($y)` (the draft's A26), so this filter keeps its name.
- 2026-11-19 (lane preddoc3c): a new piece (a provided name the library lacked: census row `length`).
- 2026-11-19 (lane preddoc4): `needs:` the computed-label piece and lib/counting/count, the two names its body uses (review r59 READ-8).
- 2026-11-21 (lane predscope, pure-label folded): one sentence added, `ch`, written as a group in rx text, is also a capture (a reading of the ruling, predscope_model.py CAPT for the two kinds); no answer moves.
- 2026-11-21 (lane predarr, array-vs-passes ruled): the statement's "one loop pass per character, its count tested by S" became "one setting of `ch` per character, their count tested by S". No answer moves.
- 2026-11-22 (lane predfix77, review r77 D4, A3; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): the helper until then, verbatim: "`chars := /(?:(?<ch>(?s:.)))*/`", and the bullet "The label `ch` is visible in the result; written as a group in rx text it is also a capture (a reading of pure-label)." A part label makes no capture, so `length` hands the caller none (his reason for the add-on: "isodate and all the other libraries don't want to presume everyone is interested in every label being a capture."); `length(==3) & length(<5)` no longer reaches caller-ambiguous for a capture.
## lib/modifiers/month-numbered — month_numbered
slugs:
rulings:
- 2026-11-14 "The problem is the name. Trim or unpad imply they are doing something to the subject. But they are not. They are changing the filter to ignore elements of the subject." (record: "2026-11-14 RULING — OWN-1, transforms are FILTER MODIFIERS")
rejected:
readings:
- the body `months & (mnum: S)`, `mnum := $mname.index` (1-based) accepts `Jan` .. `Jun` for `between(1, 6)` — SUPPORTED (preddoc3c PART MN; sabotage s20, 0-based, caught); review r16's emulation, 170 cases, 0 differ, rests on the emulated `.index`.
evidence: preddoc3c PART MN.
history:
- 2026-11-14: named in OWN-1; 2026-11-15 (rev 15): a body.
- 2026-11-19 (lane preddoc3c): a new piece (not in the census's 61 rows; a provided name of the draft §2.7).
- 2026-11-19 (lane preddoc4): `join([...])` removed from `months` (join is one string, the members joined; an array is already the alternation); `needs:` the computed-label and metadata pieces; answers unchanged: preddoc3c PART MN built the body as the alternation (review r59 READ-5).
- 2026-11-19 (lane preddoc6, review r60 COLD-15): the body's `...` written out as the twelve names in calendar order (the `.index` the example reads depends on the order); answers unchanged (preddoc6 PART MN).
- 2026-11-21 (lane predscope, pure-label folded): one sentence added, `[mname = ...]` makes no capture (a reading of the ruling, predscope_model.py CAPT for the two kinds); no answer moves.
- 2026-11-22 (lane predfix77, review r77 A3; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): `mnum` points at the open core/holes/bare-condition/bound-condition.

## lib/control/peek — peek
was: core/conditional/peek (2026-11-19, the owner: core document macros are defined in the library unless primitive; since refined the same day: every call-form name is a library piece, the "primitive" designation withdrawn)
slugs: when-peek
rulings:
- 2026-11-18 "When: I agree peek A. Automatic or enforced? peek() transform" (record: "2026-11-18 OWNER RULING — when-test: A is a peek; and his question, automatic or enforced")
- 2026-11-18 "When peek: warn. A test pattern does consume and warns that it is." (record: "2026-11-18 OWNER RULING — when-peek: a bare pattern as the test CONSUMES, with a warning; `peek()` makes it a peek")
rejected:
- the test peeked automatically (a bare pattern silently a peek) — by owner ruling — when-peek: a bare pattern consumes; the user writes `peek()`.
readings:
- the body `peek(A) := /(?=${A})/` reproduces every ruled example that uses `peek` (the when-test table's peek column, lookahead-labels on `37`, R.1.10's peek rows and `when(NOT peek(x), z)`) — SUPPORTED (preddoc2 PARTS PE, W1, WT, WD, WN; each with its sabotage caught).
- `NOT peek(A)` is the negative lookahead (the draft's reading, R.1.10 (8)) — SUPPORTED as a lowering (preddoc2 PART WN against the draft's printed answers and the semantic model).
- `default: yes` (in the default-imported set) — the owner's LEAN, not a ruling ("there can be a special imported by default set which includes peek()"); the rest of the set is NOT stated (owner question default-set).
- `module: ?`: no module is stated; `sys` in his `sys.peek()` is his example, not a ruling.
evidence: preddoc2 PARTS PE, W1, WT, WD, WN; the draft R.1.10 (3), (4); rev 26.1's PART COND (the draft's own runs).
history:
- 2026-11-18: `peek()` is his placeholder for the transform (when-test), made THE way to test without consuming by when-peek.
- 2026-11-19: the owner, after reading the pilot: "there is nothing particular about peek() other than its a useful transform"; "there can be a special imported by default set which includes peek()" (record: "2026-11-19 OWNER, after reading the pilot documents (doc-shape)"). Moved to the library with a body (lane preddoc2).
- 2026-11-19: his aside on importing symbols so a call is not `sys.peek()` (`(left,right) := import("blah", /left|right/)`) is an IDEA to discuss, owner question import-symbols; carried then by the parked piece `parked/import-symbols/import`, deleted the same day by the manager's brief (lane preddoc3c); no piece carries it now.

## lib/control/when — when
was: core/conditional/when (2026-11-19, the owner: core document macros are defined in the library unless primitive; since refined the same day: every call-form name is a library piece, the "primitive" designation withdrawn)
slugs: when-meaning when-default when-alone
rulings:
- 2026-11-17 "when-meaning: agree" (record: "2026-11-17 OWNER RULING — when-meaning")
- 2026-11-18 "When: yes guarded form." (record: "2026-11-18 OWNER RULING — the conditional is the guarded form; and his question on its test")
- 2026-11-18 "When default: yes first example. Also, a when operator should be considered" (record: "2026-11-18 OWNER RULING — when-default: the missing else requires nothing; and a `when` operator to be considered")
- 2026-11-18 "when-alone: that wasn't my ruling but my interpretation. If it's wrong let's go with what's right." (record: "2026-11-18 OWNER on when-alone: his sentence was an interpretation; go with what is right")
- 2026-11-18 "When: regardless, single arg has no value and should be an error. Ideally an @assert of some sort." (record: "2026-11-18 OWNER RULING — a `when` with a single argument is an error")
- 2026-11-18 "When: start with required then. Use NOT to get else behavior" (record: "2026-11-18 OWNER RULING — `then` is required; NOT gives the else-only behaviour")
rejected:
- the naive form `(A|B|fail)|C`, falling through to C when A holds and B does not — by run — whole `1` holds through C where an if-then-else must fail (the record, "2026-11-18 OWNER, a question on the conditional form").
- the missing else FAILS (`when(A, B)` = `A then B`) — by owner ruling — when-default.
- "the when(x) form is the same as x" — by owner ruling — withdrawn by him as an interpretation (when-alone), then `when(x)` made an error.
- `then` optional, `when(x, else = z)` legal (his spelling lean) — by owner ruling — `then` is required.
- the definition `x & (NOT c | p)` as THE definition — by owner ruling — it is the guarded form's special case for a condition test and condition branches (the draft R.1.10 (6)).
readings:
- the body `when(test, then, else = //) := (test SEQ then) | (NOT peek(test) SEQ else)` reproduces every ruled example, in the peek form and the consumed form, with a condition test and with NOT — SUPPORTED (preddoc2 PARTS W1, WT, WD, WN, WC, WV, W8; each against the draft's printed answers, the semantic model and a sabotage).
- the signature makes `then` required and refuses `when(x)` and `when(x, else = z)` "syntactically" — SUPPORTED as RULE-AS-CODE (preddoc2 PART WS; sabotage s6 caught); passing parameters BY NAME is the draft's reading (the ONE INPUT RULE).
- `//` (his `null`) is "nothing required", not a new value — the manager's reading, UNTESTED (a reading of words).
- the test is evaluated once per branch in principle (a cost statement) — NOT RUNNABLE.
- the spelling (`when`, `then`, `else`, an operator form) is open: conditional-spelling.
evidence: preddoc2 PARTS W1, WD, WN, WC, WS, WV, W8; the draft R.1.10 and rev 26.1's PART COND; PART C V13-V15 of the rev 24 lanes (the special case).
history:
- 2026-11-17: `when(c, p)` := `x & (NOT c | p)`, "a LIBRARY DEFINITION, no primitive" (when-meaning).
- 2026-11-18: the guarded form; when-default; when-alone; a single argument an error; `then` required (the draft R.1.10 (1), (2), (8)).
- 2026-11-19: moved from the core to the library with its body (lane preddoc2; the owner's recommendation 1).
- 2026-11-19 (lane preddoc4): `needs: core/filters/negation` (the body's `NOT peek(test)` is legal by that piece) and `see: lib/control/when-test` (review r59 NEGATION, READ-17).

## lib/control/when-test — The test of `when`
was: core/conditional/test (2026-11-19, the owner: core document macros are defined in the library unless primitive; since refined the same day: every call-form name is a library piece, the "primitive" designation withdrawn)
slugs: when-test
rulings:
- 2026-11-18 "When: I agree peek A. Automatic or enforced? peek() transform" (record: "2026-11-18 OWNER RULING — when-test: A is a peek; and his question, automatic or enforced")
- 2026-11-18 "When peek: warn. A test pattern does consume and warns that it is." (record: "2026-11-18 OWNER RULING — when-peek: a bare pattern as the test CONSUMES, with a warning; `peek()` makes it a peek")
- 2026-11-18 "we have since ruled that $y is a regex of a single enumeration at runtime, so the when forms would work on it." (record: "2026-11-18 OWNER RULING — value-test: the `if` was illustrative; the `when` forms work on `$y`")
rejected:
- the test always a peek, a bare pattern included (the manager's lean at when-test) — by owner ruling — when-peek: a bare pattern consumes.
- a value read as the test as its own case (holds when non-empty) — by owner ruling — value-test (one rule, no special case).
readings:
- the three kinds are when's ONE body read per kind (a condition and a peek are zero width; a bare pattern is consumed by `test SEQ then`) — SUPPORTED (preddoc2 PARTS WT, WC, WV).
- labels the test sets are visible in then; unset in else (the draft R.1.10 (5)(b)) — SUPPORTED for a peek (PART PE); the else side as run by rev 26.1's PART COND.
- a filter-only rx as the test — NOT STATED by any ruling.
evidence: preddoc2 PARTS WT, WC, WV; the draft R.1.0's TEST row and R.1.10 (3)-(5).
history:
- 2026-11-18: when-test, when-peek; 2026-11-18 evening value-test.
- 2026-11-19: moved to the library with `when` (lane preddoc2); the warning stays a core diagnostic, core/diagnostics/consuming-test.

## lib/control/when-test/not — NOT on a bare pattern test
slugs: not-test
rulings:
rejected:
readings:
- (the draft R.8, rev 26.1's PART COND, x := `\d`, z := `\w`) NEGATIVE PEEK `(?!\d)\w|(?=\d)`: WHOLE `x` HOLDS / SEARCHED `1x` ``@0 / FIND-ALL `x1 y 12` [`x`@0, ``@1, `y`@3, ``@5, ``@6] (= PCRE2's `(?(?!\d)\w|)`, 0 / 0 / 0 of 364); COMPLEMENT: a compile error — candidates, RUN.
evidence: rev 26.1's PART COND (the draft R.8 not-test row); preddoc2 PART WN (the clear form `when(NOT peek(x), z)`).
history:
- 2026-11-18: the manager's note in the record ("`then` is required; NOT gives the else-only behaviour"): complement-place and when-peek's reading collide here; asked as not-test.
- 2026-11-19 (lane preddoc2): split from the test piece (one piece, one status: the test is ruled, this is open).

## lib/control/atomic — atomic
slugs:
rulings:
- 2026-11-17 "Atomic as used by say atomic() would provide pcre behavior." (record: "2026-11-17 OWNER on atomic-search")
rejected:
readings:
- the body `atomic(X) := /(?>${X})/` reproduces its example: `atomic(/a|ab/) SEQ "c"` WHOLE `ac` HOLDS, `abc` FAILS / SEARCHED `xabc ac` `ac`@5 / FIND-ALL `ac abc ac` [`ac`@0, `ac`@7] — SUPPORTED (preddoc4 PART AT, built from the body's text; sabotage: the group not atomic).
- `atomic(...)` was the core's placeholder spelling for its atomic part (core/patterns/atomic); a name that is a body over a hole is a library piece (doc_format's rule; review r59 PLACE-2 (a)).
evidence: docs/dev/lanes/preddoc4_evidence/ PART AT.
history:
- 2026-11-17: atomic-search; `atomic(...)` the core's spelling of an atomic part.
- 2026-11-19 (lane preddoc4): a new piece: the name moved out of core/patterns/atomic, which keeps the rule (review r59 PLACE-2 (a)).

## lib/search/occurrences — occurrences
formerly: ?.search (2026-11-15, the owner renamed `search` to `occurrences` under his naming rule)
slugs: hit-carry hit-carry-depth min-values nullable-meaning helper-captures
rulings:
- 2026-11-15 "1. if I understand this question, it's asking if the search rx follows non-pcre matching behavior? If that's the question, then the answer is it should always follow it if for no other reason than that's what's expected." (record: "2026-11-14 RULINGS on rev 3's contradictions")
- 2026-11-15 "1 occurances." (record: "2026-11-15 RULING — the provided transform `search` is renamed `occurrences`")
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "Agree with all three." (record: "2026-11-17 OWNER RULING — the three remaining error-or-warning candidates")
- 2026-11-18 "hit-carry: occurrences is a simple regex rewrite ? So what the user provides gets inserted into a template hole like usual? If this is so, then the user is creating this scenario themselves. They can simply put the condition after the label to get the normal behavior. In cases where the user puts the condition before the label, they are expecting carries behavior" (record: "2026-11-18 OWNER RULING — hit-carry: it carries, because `occurrences` is a rewrite")
- 2026-11-18 "hit-carry: warning on nullable" (record: "2026-11-18 OWNER RULING — nullable argument: a warning")
- 2026-11-15 "occurrences(x, label = \"foo\")" (record: "2026-11-15 RULINGS — a per-call hit name; no count warning; the hole is the scope an `&` in it anchors to")
rejected:
- "its hits are those of a plain search" (R.1.9, unqualified) — by owner ruling — hit-carry NARROWED it to an argument with no condition before its group (the draft R.9 row 41).
- the name `search` (a verb acting on the subject) — by owner ruling — renamed `occurrences`.
- `min` 0 or 1 only, another value a compile error naming `occurs.at_least` — by owner ruling — min-values: any n, at least n hits.
- a nullable argument a compile error — by owner ruling — a warning.
- an argument with a backreference or conditional that can run while its group is unset refused — by owner ruling — hit-carry: the carry is the rewrite's own behaviour.
- "at most one hit, the first" for a nullable argument (the record's manager correction of 2026-11-18 afternoon) — by run — `occurrences(/\d*/)` on `1a` gives two hits [`1`@0, ``@1] (the draft's rev 26.1 PART R47 A1, libpcre2; preddoc3c PART OC, sabotage s9 caught).
- "the program keeps PCRE's meaning for the empty hit, as the empty search does" — by run — NOT SUPPORTED: PCRE's find-all of `/\d*/` on `a1b` gives four hits, the loop fewer (the draft R.1.9, PART H H4, H5).
readings:
- the body reproduces R.1.9's printed hits (`/\d*/` on `1a` and `12a3`; `min = 2` on the empty text, two empty hits; `min = 3` on `ab`, three) and `occurrences(/(?<n>\d+)/ & (n: <100))` on `1234` HOLDS with [`12`, `34`] — SUPPORTED (preddoc3c PART OC; sabotages s9, s10 caught).
- the loop's priority equals python's own reading of the body text `(?:(?s:.*?)(?<hit>${x})){${min},}(?s:.*)` with x := `\d+` and min 0, 1, 2: 0 / 0 / 0 of 31 texts over `1a` — SUPPORTED (PART OC).
- the hits of a nullable argument: up to and including the first empty hit (the manager's second correction, review r47 V1) — the told reading, SUPPORTED as the draft printed it (PART OC).
- hit-carry's witness `occurrences(/${c}(?<h>\d)/, min = 2)`, c := NOT (h: >= 5) (WHOLE `73` FAILS, SEARCHED `73` FAILS, FIND-ALL `3x73` [`3x73`@0 h = `7`]) — UNTESTED here (a condition before its group reads the previous hit: it needs the label engine; the draft's rev 26 PART H ran it on libpcre2).
- hit-carry-depth (how deep the carry reaches) — asked in the draft's open table, not answered; not a library question.
- the label `hit` (written as a group in rx text) is a capture the caller receives, here and in lib/search/hits (a reading of pure-label; review r77 D4, RULING-6, GENERAL-7, FIXIND-16) — UNTESTED as meant: it sits against his reason for the add-on, "isodate and all the other libraries don't want to presume everyone is interested in every label being a capture." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name"); the re-spelling with a part label needs the expression form around the atomic group (hits). An owner question, helper-captures (queued, the manager's to ask).
- `0` inside the argument (review r77 A6): three candidates part — see core/conditions/match-so-far (VERIFIED by predfix77 OCCZERO; PLAN).
evidence: preddoc3c PART OC; the draft R.1.9, rev 26 PART H, rev 26.1 PART R47.
history:
- 2026-11-14: the `contains` family; 2026-11-15: PCRE's parse, `min` (0 or 1), no `max`; renamed from `search` (rev 13).
- 2026-11-17: regex-settles (his one-pattern lazy-gap model, "It's essentially /(.*(${rx}))*.*/ So not global"); min-values.
- 2026-11-18: hit-carry; the nullable argument a warning; the hits of a nullable argument corrected twice by the manager.
- 2026-11-19 (lane preddoc3c): converted.
- 2026-11-19 (lane preddoc4): the whole-text idiom `J & C & occurrences(M)` moved here from core/model/modes, whose ruling (whole-text, "adopt it if it's legal") stays cited there (review r59 PLACE-2 (b)).
- 2026-11-19 (lane preddoc4): the ruled per-call hit name added to the base (review r59 COMPB-8); its spelling stays a placeholder.
- 2026-11-19 (lane preddoc5): the slug nullable-meaning moved here from core/conditions/defaults, which named it this piece's fact (review r59 COMPA-13).
- 2026-11-19 (lane preddoc6, review r60 RECOUNT-6): the draft R.9 candidate for this piece, PARTIAL at r59 and left unchanged by preddoc5, now has its own `rejected:` line.
- 2026-11-22 (lane predfix77, review r77 D4; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): a bullet states the `hit` capture as a reading with the tension named; status date 2026-11-18 to 2026-11-21 (pure-label changed what `hit` is).

## lib/search/hits — hits
slugs: hits-committed hits-text hits-pass hit-list
rulings:
- 2026-11-17 "hits-text: yes but spelling to be reviewed with all other spellings." (record: "2026-11-17 OWNER RULING — the hit list: atomic and anchored")
rejected:
- each hit atomic but not the loop, `\A(?:.*?(?>(?<n>\d+)))*\D*\z` with the list judged after it — by run — the lazy gap is re-entered and swallows a number's start: "every hit under 100" HOLDS on all four texts with hits [`34`], [`12`, `34`], [`12`, `45`], [`0`, `12`] (the draft R.1.9; preddoc3c PART HI reproduces the four lists; sabotage s11 caught).
- the stretch reading (SEARCHED `x300 12` gives `x30`@0 with [`30`]) — by owner ruling — hits-text: standing alone the list is the whole subject's.
readings:
- the body (an atomic group around the whole loop, anchored at both ends) gives the printed lists and verdicts: `1234` FAILS [`1234`], `12 34` HOLDS, `12 345` FAILS, `x300 12` FAILS; with an optional label `axa` FAILS (the last hit's own g unset), `aax` HOLDS — SUPPORTED (preddoc3c PART HI).
- "every hit under 100" written as `hits(/\d+/) & occurs.none((hit: >= 100))`, a group question on the array of `hit` (one setting per hit) — the lane's reading of the unwritten program; WHOLE `1234` FAILS, `12 34` HOLDS, `12 345` FAILS, `x300 12` FAILS under the settings and the pass readings alike — SUPPORTED (predarr HITS: the body read from library.md, against python `re` 0 / 0 / 0 of 1,365 texts; sabotage s13, the atomic group re-entered, caught).
- hits-pass and some-own: a bare condition after it reads the last hit's own labels (closed by entailment, the draft §R.8) — SUPPORTED for the optional-label rows (PART HI).
- `module: ?`; the spelling `hits` is a placeholder, his `all_matches(rx)`.
evidence: preddoc3c PART HI; the draft R.1.9, rev 24.4 PART H.
history:
- 2026-11-17: "OWNER on what `hits` is" (questions), then the ruling: atomic and anchored (hits-committed, hits-text).
- 2026-11-19 (lane preddoc3c): converted.
- 2026-11-19 (lane preddoc5): the slug hit-list moved here from core/model/table, whose reading named this piece as the one deciding it (review r59 PLACE-4).
- 2026-11-21 (lane predscope, pure-label folded): one sentence added, the `hit` group written in rx text is a capture as well as a label (a reading of the ruling, predscope_model.py CAPT for the two kinds); no answer moves.
- 2026-11-21 (lane predarr, array-vs-passes ruled): the "every hit under 100" bullet names its program, a group question on the array of `hit` (a reading). No answer moves.
- 2026-11-22 (lane predfix77, review r77 D4; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): the capture bullet points at the tension and the question helper-captures (lib/search/occurrences).
## lib/search/contains — contains
was: lib/search/contains/by-occurrences (2026-11-19, merged: a second present-tense definition of `contains` in the base; its body is a reading line here (review r60 COLD-10))
slugs:
rulings:
- 2026-11-15 "Your examples make me agree. /\d\d/ & between(1, 12) Without anchoring it would match "31"" (record: "2026-11-14 RULINGS on rev 3's contradictions")
- 2026-11-15 "Ok I agree." (record: "2026-11-14 RULINGS on rev 3's contradictions")
rejected:
- regex filters unanchored by default — by owner ruling — his `/\d\d/ & between(1, 12)` would match `31`.
- an explicit anchor switching off the implicit ones — by owner ruling — the same entry, (4).
readings:
- the record's body `/.*${rx}.*/` with the gaps crossing line breaks is `/(?s:.*)(?:${s})(?s:.*)/`, and `contains(/^err/)` equals `startsWith("err")` WHOLE (0 of 1,365 texts over `erx` and a newline, length <= 5) — SUPPORTED (preddoc3c PART SW).
- `contains(/err$/)` also accepts a value ending `err` and a newline (PCRE's `$`; `\z` for the exact end) — SUPPORTED (PART SW).
- a CANDIDATE body, not the definition: `contains(x) := occurrences(x, min = 1)` (the draft's LEAN, §2.6, §8: chosen so x's labels read as the leftmost hit) — the same set as the ruled gap body, 0 / 0 / 0 of 121 texts (`ab` over `abx`, length <= 4) in all three modes; only the labels differ (the hit, and which occurrence x's labels read) — SUPPORTED (preddoc3c PART SWocc). Its printed run: `occurrences("ab", min = 1)` WHOLE `xabx` HOLDS, `ba` FAILS / SEARCHED `x ab` `x ab`@0 / FIND-ALL `ab ab` [`ab ab`@0].
- the same candidate also equals `occurrences(x) & some((hit: /(?s).*/))` (the draft) — UNTESTED here.
evidence: preddoc3c PART SW, PART SWocc.
history:
- 2026-11-14/15: the `contains` family; the record's body (11-15); the draft kept `occurrences(x, min = 1)` (its reading above).
- 2026-11-19 (lane preddoc3c): converted; the draft's spelling split into its own piece (one piece, one status).
- 2026-11-15 (rev 9-12): the draft kept the occurrences spelling against the record's text, "the same sets".
- 2026-11-19 (lane preddoc6, review r60 COLD-10): the sub-piece "contains as occurrences" (`reading`, "`contains(x)` is written `occurrences(x, min = 1)`: the same set, and x's labels read leftmost, as a hit") merged back here as a candidate reading: the base had two present-tense definitions of one name.

## lib/search/starts-with — startsWith
slugs:
rulings:
- 2026-11-15 "Ok I agree." (record: "2026-11-14 RULINGS on rev 3's contradictions")
rejected:
- his first sketch `startsWith(rx) := /^${rx}/` — by owner ruling (the advice he agreed to) — in filter position it means exactly rx: `/^5/` rejects `57` (preddoc3c PART SW, sabotage s7 caught).
- folding `startsWith`/`endsWith` into `occurrences` with an anchored argument (the manager's lean) — by owner ruling — withdrawn in the same entry.
readings:
- the body `/(?:${s})(?s:.*)/` accepts `57` for `startsWith("5")`, and its gap crosses a line break (`a`, newline, `b`) — SUPPORTED (PART SW; sabotage s8, unscoped gaps, caught).
evidence: preddoc3c PART SW.
history:
- 2026-11-15: the plain gap bodies (rev 12).
- 2026-11-19 (lane preddoc3c): converted.

## lib/search/ends-with — endsWith
was: lib/search/ends-with/lazy-gap (2026-11-19, merged: a second present-tense definition of `endsWith` in the base; its body is a reading line here (review r60 COLD-10))
slugs:
rulings:
- 2026-11-15 "Ok I agree." (record: "2026-11-14 RULINGS on rev 3's contradictions")
rejected:
readings:
- the record's body `/.*${rx}/` with the gap crossing line breaks: on `ab123` with `(?<n>\d+)`, n = `3` (greedy) — SUPPORTED as the record's text (preddoc3c PART SW).
- a CANDIDATE body, not the definition: the LAZY gap `/(?s:.*?)(?:${s})/` (the draft's LEAN since rev 9, kept against the record's text), so the argument starts as far LEFT as it can: n = `123` on `ab123`; rev 8's greedy `.*` gave `3` (libpcre2). As SETS nothing changes; the labels and the searched stretch differ: `(?s:.*?)(?:(?<n>\d+))` WHOLE `ab123` HOLDS (123) / SEARCHED `x12 34` `x12`@0 (the ruled body: `x12 34`@0) / FIND-ALL `a1 b2` [`a1`@0, ` b2`@2] — SUPPORTED (preddoc3c PART SW).
evidence: preddoc3c PART SW.
history:
- 2026-11-15: the plain gap body (rev 12); the draft kept a lazy gap (its reading above).
- 2026-11-19 (lane preddoc3c): converted; the lazy gap split into its own piece.
- rev 9-10 (2026-11-15): the lazy gap chosen for how the argument's labels read; rev 12 kept it against the record's `/.*${rx}/`.
- 2026-11-19 (lane preddoc6, review r60 COLD-10): the sub-piece "endsWith with a lazy gap" (`reading`, "`endsWith(s)` is written with a LAZY gap, `/(?s:.*?)(?:${s})/`, so its argument starts as far LEFT as it can") merged back here as a candidate reading: the base had two present-tense definitions of one name; the ruled body is the definition.

## lib/search/anchored — anchored
slugs: anchored-in-hole
rulings:
- 2026-11-15 "Ok I agree." (record: "2026-11-14 RULINGS on rev 3's contradictions")
- 2026-11-15 "Anchored def: agree." (record: "2026-11-15 RULINGS — `anchored` has exact ends; which `&` is the operator in rx text"); CORRECTED by the 21:20 entry (the item below): it answered the earlier `\A`/`\z` lean
- 2026-11-15 "anchored-in-hole: agree" (record: "2026-11-15 RULINGS — no anchored-specific error in a hole; the anchor warning covers every whole-match place")
- 2026-11-15 "The anchored comment was to a previous statement. What does new anchored suggestion mean." (record: "2026-11-15 CORRECTION and RULING"); part (a): his "Anchored def: agree" answered the manager's EARLIER statement (the `\A`/`\z` lean): RULED = `anchored` has EXACT ends; defining `anchored(P)` as "P in filter role on the enclosing scope" is NOT ruled
rejected:
- his placeholder `anchored(rx) := /^${rx}$/` — by owner ruling — exact ends: its `$` also holds before a final newline (preddoc3c PART AC, sabotage s6 caught).
- an error specific to `anchored` in a hole — by owner ruling — anchored-in-hole.
- defining `anchored(P)` as "P in filter role on the enclosing scope" — not ruled (the correction entry); it differs in a hole.
readings:
- the body reproduces the nine printed rows (`anchored(/a|b/)` on `ab`; `/a|ab/`; `/foo/` on `foo` and on `foo` with a newline; `/foo$/`; `(?m)^a$`; `/x${anchored(/a/)}/`; `/${anchored(/a/)}b/`; `/\w+/ & anchored(/foo/)` on `xfoo` 1-4) — SUPPORTED (preddoc3c PART AC).
- "no rule or table of the language depends on `anchored`" (the manager's consequence, told) — UNTESTED.
evidence: preddoc3c PART AC; the draft §8, `predspec13_anchor.out`, `predspec14_anchor.out`, `predspec15_anchor.out`.
history:
- 2026-11-15: added (the one anchoring rule); exact ends (rev 13); anchored-in-hole and anchor-warn-scope (rev 14); the tie with `&` (rev 15, warn-in-macro-body).
- 2026-11-19 (lane preddoc3c): converted.

## lib/search/within — within
slugs:
rulings:
rejected:
readings:
- `within(15, of = ...)` appears only in the worked example E-NEAR (the draft §12.7) and §5.1's list of library names; no body, no definition — the conversion's reading: `under-construction`.
evidence: the draft §12.7.
history:
- 2026-11-19 (lane preddoc3c): converted.

## lib/sets/anything — anything
slugs: anything-text
rulings:
- 2026-11-19 "anthing-text: agree anything := [\s\S]*." (record: "2026-11-19 OWNER RULING — anything-text; and a standing instruction on his regex")
rejected:
- his 2026-11-18 example `any := /.*/` — by owner ruling — anything-text: it fails on a multi-line value (preddoc3c PART AN, sabotage s5 caught).
readings:
- `[\s\S]*` holds WHOLE on the empty text, `12`, `a` newline `b`, `A b` newline, alone and under `(?s)`, `(?i)`, `(?m)`, `(?x)` — SUPPORTED (preddoc3c PART AN; the record's own run).
- nullable, a whole-value tool (the draft's R.1.0 PROGRAM row) — the record's note, unchanged and not asked.
evidence: preddoc3c PART AN.
history:
- 2026-11-19: anything-text ("anthing-text" read as the slug); the skeleton converted in full (lane preddoc3c).
- 2026-11-19 (lane preddoc4): `anything & NOT X` written `anything & !X` (the complement is `!`; review r59 NEGATION).

## lib/sets/between — between
slugs:
rulings:
- 2026-11-15 "for numbers there was a critic complaining that \d\d & between(1,12) would only match 10-12 and i said yes, that is correct because the \d\d means two digits." (record: "2026-11-14 RULINGS on rev 3's contradictions")
rejected:
- a "compares by value" reading (`/\d\d/ & between(1, 12)` accepting `05`) — by owner ruling — the string-set reading stands.
readings:
- the body `>= lo & <= hi` (the conversion's spelling of the draft's "`between(lo, hi)` is INCLUSIVE"; no body is printed in the draft) gives {`10`, `11`, `12`} on two-digit texts and, under `padded`, `05`, `5`, `12` — SUPPORTED (preddoc3c PART BE; sabotage s12, exclusive bounds, caught).
- tuple bounds (`between((9, 0), (10, 0))`, dictionary order, at most 2k - 1 products) — the joint condition's sets (the draft §2.4, §8 (5)); UNTESTED here.
evidence: preddoc3c PART BE.
history:
- 2026-11-14: a standard library set; 2026-11-15: the string-set confirmation; rev 20: tuple atoms.
- 2026-11-19 (lane preddoc3c): converted.

## lib/sets/prefix-in — prefix_in, suffix_in, slice_in
slugs:
rulings:
rejected:
- the names `left(n, S)`, `right(n, S)`, `mid(i, n, S)` for this filter — by review r48 E (the manager's spelling call) — they collided with his `left(rx, n)`, a different function (the image).
readings:
- the body `/${S & /(?s:.){${n}}/}(?s:.*)/` (the draft's LEAN, rev 15): `prefix_in(2, /abc|xy/)` holds on `xyz`, not on `abc`; `prefix_in(2, "Columbus")` never holds — SUPPORTED (preddoc3c PART PI; sabotage s19, the image in its place, caught).
- out of range: the draft §13 O14, open; characters per the encoding mode.
evidence: preddoc3c PART PI.
history:
- 2026-11-15 (rev 15): `left/right/mid` with a body; 2026-11-18 (rev 27.1): renamed.
- 2026-11-19 (lane preddoc3c): converted.

## lib/counting/some — some
slugs: all-question some-own
rulings:
- 2026-11-21 "they chose to use the same labels and therefore that has to have a meaning. for simplicity, and due to the fact that the other interpretations can be otherwise spelled, i think option "a"" (record: "2026-11-21 OWNER RULING — array-vs-passes: a"); `some` reads the ARRAY OF SETTINGS of the name, the one outside the loop included; it REVISES this piece's "at least one pass of a loop meets the condition c" (2026-11-15)
- 2026-11-21 "join-in-some: agree and elegant. that said, no one would know to write it." (record: "2026-11-21 OWNER RULING — joint-in-some: agree"); a joint entry inside `some` is refused for now; "same item" is the on-item label, then `some` on that label
- 2026-11-15 "3. could you use some() to get some hits?" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING — SEARCH IS A TRANSFORM"
- 2026-11-15 "Do it" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING — SEARCH IS A TRANSFORM"
- 2026-11-16 "all-question: retire" (record: "2026-11-16 OWNER RULING — all-question: retire")
- 2026-11-17 "after-loop-read: ok I see it. Last pass own label makes sense" (record: "2026-11-17 OWNER RULING — after-loop-read: the last pass's own label")
- 2026-11-22 "array-in-piece: if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is bound first, its internal references refer only to what can be seen at that point." (record: "2026-11-22 OWNER RULING — array-in-piece: b (a group question inside a bound piece reads only what that piece can see)")
rejected:
- `all` as a group question — by owner ruling — all-question: retire.
- `occurs.some` — by the draft (rev 7's, removed, not aliased) — `some(c)` is the one spelling.
readings:
- false on zero passes, each pass judged with its own labels (the draft §4.3's group-questions table) — the draft's reading; SUPPORTED for its example (preddoc4 PART SO; sabotage s8, "every pass", caught); REPLACED by array-vs-passes (a): false on an EMPTY array (a reading of the ruling; predarr EMPTY).
- the printed line under the settings reading — the SAME answers as under the passes (one setting per pass, none outside the loop): `WHOLE `1,7,` HOLDS, `1,2,` FAILS / SEARCHED `1,2, 7,` `7,`@5 / FIND-ALL `7,1, 2, 3,7,` [`7,1,`@0, `3,7,`@8] (`/(?:(?<d>\d),)+/ & some((d: "7"))`)` — SUPPORTED (predarr CHANGED; sabotage s12, the last setting only, caught).
- `some` is native to the language: it walks a pass table no body can reach (review r59 PLACE-3) — the lane's reading under R-1 (`defined: native`); since array-vs-passes it walks a name's array of settings, still native.
evidence: docs/dev/lanes/preddoc4_evidence/ PART SO (its "every pass" wording superseded by array-vs-passes; the line's answers stand); docs/dev/lanes/predarr_evidence/ CHANGED, EMPTY; the draft §4.3, R.4.
history:
- 2026-11-19 (lane preddoc4): a new piece: ruled pieces used `some` with no piece (review r59 PRIMITIVES-MISSING, READ-6).
- 2026-11-19 (lane preddoc5): the slug some-own (the draft's, closed by entailment) moved here from lib/search/hits; there was no `some` piece when it was homed (review r59 PLACE-4).
- 2026-11-19 (lane preddoc6, review r60 COLD-20): "`NOT some(c)` and `occurs.none(c)` are the same question" marked as the reading of the open question core/model/table/group-truth (it is that question's candidate (a)); before, a ruled piece stated it as settled.
- 2026-11-21 (lane predarr, array-vs-passes and joint-in-some ruled): the statement until then, verbatim: "`some(c)` holds when at least one pass of a loop meets the condition c, each pass judged with its own labels; it is false where the loop made no pass."; `defined: native (a question over a loop's passes; no expression of the language walks the passes)`; the bullet "`some` is the one spelling of "at least one pass"" lost "pass"; "`NOT some(c)` and `occurs.none(c)` are the same question under the reading of the open question core/model/table/group-truth (a reading)" became "the same question over the array". Bullets added: the array, the joint entry refused and the on-item idiom. Status date 2026-11-15 to 2026-11-21. The printed line does not move.
- 2026-11-22 (lane predfix77, review r77 D7 (RULING-4), D11 (GENERAL-8); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): statement until then, verbatim: "`some(c)` holds when at least one setting in the array of c's label meets c; it is false on an empty array." The empty-array clause is marked a reading in the statement; the `NOT some(c)` = `occurs.none(c)` bullet restricted "for a condition of one entry", group-truth owning it (under the product reading of several entries extended to `occurs` it fails on `5:1,`: hand-worked, review r77 GENERAL-8).
- 2026-11-22 (lane predfix77, R-1): array-in-piece folded where the piece states the array (those visible in the definition the question is written in, a bound piece's own); status date 2026-11-21 to 2026-11-22.
## lib/counting/count — count
slugs: count-budget
rulings:
- 2026-11-21 "they chose to use the same labels and therefore that has to have a meaning. for simplicity, and due to the fact that the other interpretations can be otherwise spelled, i think option "a"" (record: "2026-11-21 OWNER RULING — array-vs-passes: a"); `count` reads the ARRAY OF SETTINGS; it REVISES "the number of passes of a loop that meet c"
- 2026-11-15 "counts: perhaps the solution is both. you can use count() until you can't then you can use 'occurs' as a fallback" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING (lean) — counts: `count()` first, `occurs` as the fallback"
- 2026-11-15 "i would refuse count() on budget or as a recommended way to reduce states rather than rules" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING — when `count()` gives way to `occurs`: by BUDGET, not by rule"
- 2026-11-15 "4. agree. Allows "even()" or other checks for count." (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULINGS — the five open items"
- 2026-11-15 "Predicate count/occurs issue: it would be a later optimization plan item that if pcrec could show no change in semantics that it convert count() into occurs" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 OWNER NOTE — `count()` -> `occurs` as a LATER OPTIMIZATION"
- 2026-11-22 "array-in-piece: if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is bound first, its internal references refer only to what can be seen at that point." (record: "2026-11-22 OWNER RULING — array-in-piece: b (a group question inside a bound piece reads only what that piece can see)")
rejected:
- `count()` refused in a set position by rule (the manager's "until you can't" reading) — by owner ruling — "by BUDGET, not by rule" (the reading WITHDRAWN in the record).
readings:
- `n := count((d: "7"))`, `/(?:(?<d>\d),)+/ & (n: ==2)`: WHOLE `7,1,7,` HOLDS, `7,1,` FAILS / SEARCHED `7,7,7,` `7,7,`@0 / FIND-ALL [`7,7,`@0, `1,7,7,`@7] — SUPPORTED (preddoc4 PART CO; sabotage s9, every pass counted, caught).
- the printed line under the settings reading — the SAME answers (one setting per pass): SUPPORTED (predarr CHANGED). On an empty array the count is zero (a reading; predarr EMPTY: `count(NOT (d: "7"))` on `,` is 0 on the array, 1 on the passes). On a condition of several entries what is counted is not stated (the manager's reading (b); an owner question, count-several, proposed).
- the budget is one measured quantity, named with the "too many classes" budget (the five open items, (3)); no number stated.
evidence: docs/dev/lanes/preddoc4_evidence/ PART CO; plan row [COUNT-TO-OCCURS].
history:
- 2026-11-19 (lane preddoc4): a new piece: `count(c)` was the body helper of `length` with no piece (review r59 PRIMITIVES-MISSING, READ-6). The slug count-budget is the lane's name for the budget ruling.
- 2026-11-19 (lane preddoc6, review r60 COLD-2): the base's "`even()` on a count" (his word, "Allows "even()" or other checks for count", quoted above) written as the set it names, `/\d*[02468]/`: no piece provides `even`.
- 2026-11-21 (lane predarr, array-vs-passes ruled): the statement until then, verbatim: "`count(c)` is the number of passes of a loop that meet c, a canonical numeral used with the ordinary comparisons; it is refused only over the budget, the refusal naming `occurs`."; `defined: native (a count over a loop's passes; no expression of the language counts passes)`. A bullet added (settings, zero, several entries). Status date 2026-11-15 to 2026-11-21. The printed line does not move.
- 2026-11-22 (lane predfix77, review r77 A3; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): `n` points at the open core/holes/bare-condition/bound-condition.
- 2026-11-22 (lane predfix77, R-1): array-in-piece folded where the piece states the array (those visible in the definition the question is written in, a bound piece's own); status date 2026-11-21 to 2026-11-22.
## lib/counting/occurs — occurs.exactly, .at_least, .at_most, .none
slugs:
rulings:
- 2026-11-21 "they chose to use the same labels and therefore that has to have a meaning. for simplicity, and due to the fact that the other interpretations can be otherwise spelled, i think option "a"" (record: "2026-11-21 OWNER RULING — array-vs-passes: a"); `occurs` reads the ARRAY OF SETTINGS (the record entry names lib/counting/occurs among the revised pieces)
- 2026-11-14 "more obscure but valuable" (record: "2026-11-14 RULING — counting occurrences")
- 2026-11-22 "array-in-piece: if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is bound first, its internal references refer only to what can be seen at that point." (record: "2026-11-22 OWNER RULING — array-in-piece: b (a group question inside a bound piece reads only what that piece can see)")
rejected:
- `occurs.some` and `occurs.all` — by the draft (rev 7's, removed, not aliased; LEAN) — `some(c)` is the one spelling; `all` was retired (all-question).
- a namespace `label` (`label.exactly(1, ...)`) — by the record — it clashes with element metadata `x.label`.
readings:
- the family is RULED as a library (2026-11-14); the name `occurs` ruled in use (the draft §8 STATUS).
- over the array, `NOT some(c)` = `occurs.none(c)` by definition and `occurs.none(NOT c)` is "every setting meets c" — SUPPORTED (predarr TRUTH); the every-pass form over the array is not the item form where the label is optional (predarr EVERYPASS; lib/counting/every-pass).
- `NOT some(c)` = `occurs.none(c)`; the every-pass form `some(c) & occurs.none(NOT c)` equals `REP & c` on 364 texts (the draft R.4's W1-W9 table) — the draft's runs, not re-run here.
- `count(c)` first, `occurs` the fallback (LEAN); `count()` refused only on budget (RULED) — the core's group questions, which have no core piece yet.
evidence: the draft §8, §4.3, R.4.
history:
- 2026-11-14: agreed as a library family (all, some, none, exactly, at_least, at_most); 2026-11-15 (rev 8): counts only.
- 2026-11-19 (lane preddoc3c): converted; the heading drops `.some` (withdrawn).
- 2026-11-21 (lane predarr, array-vs-passes ruled): the statement until then, verbatim: "The `occurs` module counts a repeated label's passes meeting a condition: `exactly(n, c)`, `at_least(n, c)`, `at_most(n, c)`, `none(c)`."; `defined: native (a count over the passes of a loop, a capped counter; no expression of the language counts passes)`; the bullet's "one record is one pass" became "judged on each setting of its label"; the `modes:` line's "a count over a loop's pass table; no example of the draft is printed in the three modes" re-pointed at the runs. `needs:` the array piece. Status date 2026-11-14 to 2026-11-21.
- 2026-11-22 (lane predfix77, R-1): array-in-piece folded where the piece states the array (those visible in the definition the question is written in, a bound piece's own); status date 2026-11-21 to 2026-11-22.
## lib/counting/every-pass — Every pass, named
slugs: every-pass-spelling
rulings:
- 2026-11-17 "last-pass-default: regex. I want to have the method of achieving the alternative meanings defined and tested so we don't lose that functionality." (record: "2026-11-17 OWNER RULING — last-pass-default: regex"); the standing instruction: every meaning the draft could express before (every pass with and without at-least-one, not-every, some / count / occurs, ...) has its spelling DEFINED and TESTED
rejected:
readings:
- OPEN in the draft (§R.8, row every-pass-home: "the conditioned item inside `repeat` is the item form"; the draft R.4's W1a, W1b); the owner, the evening of 2026-11-16 as the draft quotes him: "assign the condition inside the loop to get the all behavior" — the item form, today's way; whether a name exists is not asked.
- `some(c) & occurs.none(NOT c)` equals `REP & c` on 364 texts (the draft R.4's W1-W9 table) — the draft's runs, under the PASS reading; NOT SUPPORTED over the array where the label is optional: on `7,,` every setting is `7` and the form HOLDS while the item form FAILS (predarr EVERYPASS; sabotage s11 caught). The pass-reading line, verbatim as run: `Passes: WHOLE `7,7,` HOLDS, `7,,` FAILS, `7,1,` FAILS / SEARCHED `7,, 7,7,` `7,`@0 / FIND-ALL `7,, 7,1, 7,7,` [`7,`@0, `7,`@4, `7,7,`@9] (`/(?:(?<d>\d)?,)+/ & some((d: "7")) & occurs.none(NOT (d: "7"))`)`.
- the settings form and the item form part on a loop that can make no pass as well (review r77 MODES-12) — SUPPORTED by a run (predfix77 EVERYNONE: on `x` the settings form FAILS, `some` false on an empty array, the item form HOLDS; sabotage s14 caught).
evidence: the draft R.4, §R.8; docs/dev/lanes/predarr_evidence/ EVERYPASS. predfix77_model.py EVERYNONE.
history:
- 2026-11-19 (lane preddoc4): a new open piece: the slug every-pass-spelling had no home (review r59 PRIMITIVES-MISSING).
- 2026-11-21 (lane predarr, array-vs-passes ruled): the statement until then, verbatim: "Is there a named group question for "every pass meets c", equal to `some(c) & occurs.none(NOT c)`, or is every pass written only with the condition on the item?"; candidate (b) until then "a named group question equal to `some(c) & occurs.none(NOT c)`"; the `modes:` line "modes: n/a (a question; the draft's runs are cited in the details entry)" replaced by two run lines. Over the array the form says every SETTING, not every pass; the question stays open. Status date 2026-11-19 to 2026-11-21.
- 2026-11-22 (lane predfix77, review r77 D12 (MODES-12); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): "where the label is optional it is not the item form" became "where the label is optional, or the loop can make no pass, ..."; the two lines "No pass, every setting", "No pass, the item form" added.
## lib/strings/join — join
slugs:
rulings:
- 2026-11-19 "negated-class-hole: [^${join(c)}]" (record: "2026-11-19 OWNER RULING — negated-class-hole")
rejected:
- one class built from all the values of `[^${c}]` (the manager's leaning at negated-class-hole) — by owner ruling — the user writes `join`.
readings:
- `[^${join(c)}]`, c := [x, y], is `[^xy]`: WHOLE `ax` FAILS, `ab` HOLDS / `ab`@3 / [`ab`@6] (the record's run) — SUPPORTED (preddoc3c PART JO; sabotage s14, `[^${c}]` with no join read as the alternation of negated classes, caught).
- "a function from an array to one string, its members in order" — the manager's reading, told to him; `sep` is the draft's §5.3 (LEAN); `join` over a spelled array of PATTERNS is the n-ary sequence (the rx-module note).
- for a NON-negated class `[${join(c)}]` equals `[${c}]`; a value with several characters is a class member each; `[^${c}]` with two or more values warns, pointing at `join` — the manager's readings (the negated-class-hole entry), UNTESTED here.
evidence: preddoc3c PART JO.
history:
- 2026-11-12/13: `join([name = rx, ...], sep = ...)` in the draft (§5.3); 2026-11-19: his `join(c)` in a negated class.
- 2026-11-19 (lane preddoc3c): converted.

## lib/strings/left — left
slugs:
rulings:
- 2026-11-18 "left(2) is the leftmost two digits of an rx." (record: "2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match"")
rejected:
readings:
- built for an rx `enumerate` accepts, under construction otherwise (construction-line, core/values/functions): `left(/foobar|bazqux/, 2)` = `fo|ba` — SUPPORTED (preddoc3c PART LF).
- string-level manipulation of any rx (`left(/\d+/, 2)`) is parked/ideas/string-level-rx.
- its order is enumerate's, a class ascending, nothing sorted by length: `left(/\d{1,2}?/, 2)` equals `\d{1,2}?` itself (lane predloop's reading of class-positions, re-run under quantified-order) — SUPPORTED (predasc EXleft: 0 / 0 / 0 of 3,906 against `\d{1,2}?`; its results sorted longest first differ, 0 / 3,104 / 3,616; the line unchanged; sabotage s14 caught).
- its kin `right` and `mid`: the owner's question "What about string operators like left, right, mid?" (record bullet STRING OPERATIONS, 2026-11-13) and the draft R.1.16 T9's "and kin" name them; neither is defined; their FILTER names are rejected under lib/sets/prefix-in — named, not defined (no piece of their own: they would be pieces of this kind once one is wanted).
evidence: preddoc3c PART LF; the draft R.1.16 T9; predloop (superseded by predasc: predloop's model asserts the retired descending order and is red at the tip by design) EXleft; predasc EXleft.
history:
- 2026-11-18: match-is-rx; construction-line.
- 2026-11-19 (lane preddoc3c): converted.
- 2026-11-19 (lane predloop): the order bullet and its example added (class-positions).
- 2026-11-19 (lane predasc): quantified-order. Bullet before: "Its order is enumerate's, a class descending, nothing sorted by length: `left(/\d{1,2}?/, 2)` keeps `\d{1,2}?`'s own answers (a reading, run)." Reading before, verbatim: "its order is enumerate's, a class descending, nothing sorted by length: `left(/\d{1,2}?/, 2)` equals `\d{1,2}?` itself (this lane's reading of class-positions) — SUPPORTED (predloop EXleft: 0 / 0 / 0 of 3,906 against `\d{1,2}?`; its results sorted longest first differ, 0 / 3,104 / 3,616; sabotage s14 caught)."

## lib/strings/strlen — strlen
slugs:
rulings:
- 2026-11-18 "illustrative: length($y) returns the length of the match." (record: "2026-11-18 OWNER, what "under construction" was about")
rejected:
readings:
- `/(?<y>\w+)-${strlen($y)}/`: WHOLE `abc-3` HOLDS / `abc-3`@5 / [`a-1`@0, `abcdefghij-10`@9] (the draft's rev 28 PART CN) — SUPPORTED (preddoc3c PART SL; sabotage s16 caught).
- the spelling `strlen` is the manager's call 6 (his own word in the padded sketch, "strlen($y-1)"), so the filter `length(S)` keeps its name.
evidence: preddoc3c PART SL.
history:
- 2026-11-18: his `length($y)`; rev 28.1: written `strlen($y)` (the draft's A26).
- 2026-11-19 (lane preddoc3c): converted.

## lib/strings/upper-start — upperStart
slugs:
rulings:
rejected:
readings:
- three mentions in the draft (R.1.16 T9, the spellings list), no definition — the conversion's reading: `under-construction`.
evidence:
history:
- 2026-11-18: his placeholder beside `left(rx, n)` (match-is-rx).
- 2026-11-19 (lane preddoc3c): converted.

## lib/assert/assert — assert.some, assert.none, assert.same
slugs:
rulings:
- 2026-11-14 "I agree with both excepting the spelling ... no alpha operators ... with, check, in ... check is not `x := ...` ... don't want to go into new grammar lightly" (record: "2026-11-14 RULINGS on docs/dev/lanes/predx_report.md §11")
- 2026-11-15 "If someone is writing ambiguous rx they need to think about what that means and validate it with @check()" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULINGS — ONE reading everywhere (PCRE's); ambiguity is the author's to validate; no `max` on search for now"
rejected:
- `check` as a keyword or statement form, `x := check ...` — by owner ruling — "no alpha operators", "check is not `x := ...`" (Q9).
- the `assert_some(...)` built-ins and `check A == B` — by owner ruling — the assertion library form (`assert := import("assert")`, `assert.some(...)`; the draft §5.6 STATUS: "SUPERSEDES `check A == B` and the `assert_some(...)` built-ins").
- a library assertion on the searched mode (a critic's "search assertion", `@assert.finds(p, "256.1.1.1", ...)`-shaped) — by review (Q1X-5, NOTED) — not adopted (the draft §13 O36).
readings:
- the CONCEPT (compile-time assertions) is agreed (Q6 + Q9); the spelling `@assert.some/none/same`, a module's effect calls, is the manager's lean after his `assert := import("assert")`, `assert.some("2024" & leap)` (record "2026-11-14 — import/export as functions") and the draft §5.6 (LEAN) — a placeholder spelling.
- the set position and the edge-assertion error in its argument: the draft §5.6 — not run here.
evidence: the draft §5.6.
history:
- 2026-11-19 (lane preddoc4): a new piece and section: the ruled assert module had no piece (review r59 COMPB-2).
- 2026-11-21 (lane predarr, array-vs-passes ruled): the last bullet's "that one asks about a loop's passes in a match" became "about a label's settings in a match".
## lib/assert/each — assert.each
slugs:
rulings:
rejected:
readings:
- the per-entry assertion spelling is OPEN in the draft (§13 O22, "the `@each(...)` per-entry assertion spelling (both OPEN by ruling)"); the lean `@assert.each(...)` is review r10 CENSUS-16's (the draft §5.5) — UNTESTED; no new question is opened here.
evidence:
history:
- 2026-11-19 (lane preddoc5): a new piece (review r59 COMPB-2, COMPB-8); the owner's direction of 2026-11-19 puts every call-form name in the library, marked defined or not.

## lib/records/records — records
slugs:
rulings:
rejected:
readings:
- the draft §7 (file_text and records; the names placeholders colliding with RECORD, §13 O44) — the draft's text, not run.
evidence: the draft §7, §12.8 (E-FILE).
history:
- 2026-11-19 (lane preddoc3c): converted.

## lib/records/list-of — list_of
slugs:
rulings:
rejected:
- form (b), the two-copy definition `(?:X(?:S X)*)?` of the rx-module note — by the draft's proposal (R.1.7) — under the one label rule its one-item label is unset (preddoc3c PART LO, sabotage s15 caught).
readings:
- form (a), `(?:X S)*X` (THE DRAFT'S PROPOSAL, the manager's lean, not ruled): the label `7` on `7` and `5` on `7,3,5`, the empty text FAILS — SUPPORTED (PART LO).
evidence: preddoc3c PART LO.
history:
- 2026-11-17 (rev 24.4): defined as form (a), a proposal; separator-label dissolved.
- 2026-11-19 (lane preddoc3c): converted.

## lib/records/param — param
slugs:
rulings:
rejected:
readings:
- a run-time input (the draft §0.3, §11; E-NEAR (b)); what it is: OPEN (the draft §13 O46, no owner slug) — the draft's.
evidence: the draft §0.3, §12.7.
history:
- 2026-11-19 (lane preddoc3c): converted.

## lib/records/file-text — file_text
slugs:
rulings:
rejected:
readings:
- the draft §7: a pinned compile-time file; what moves when the file changes is the `sha256` pin (the draft's standing question 3).
evidence: the draft §7, §12.8.
history:
- 2026-11-19 (lane preddoc3c): converted.

## lib/records/any-order — any_order
slugs:
rulings:
rejected:
readings:
- "candidate sugar" in the draft (§5.3) and in the record's join entry ("candidate sugar `any_order(a, sep:)`", record: "2026-11-14 — join"); graded in the draft's own provided-macro audit (§13 O61) — a lean, UNTESTED.
evidence:
history:
- 2026-11-19 (lane preddoc5): a new piece (review r59 COMPB-8); the owner's direction of 2026-11-19 puts every call-form name in the library, marked defined or not.

## lib/records/file-literals — file_literals
slugs:
rulings:
rejected:
readings:
- the record's lean ("2026-11-14 — literals from a file", the owner asked for `alts := file_literals("...")`), then "`file_literals` becomes library sugar `records(file_text(p), lines)` where `lines` is a NAMED record rx" (record: "2026-11-14 — file_text + records"); the draft §7 keeps it — a lean, UNTESTED; `defined: ?` because no body names its item rx.
evidence:
history:
- 2026-11-19 (lane preddoc5): a new piece (review r59 COMPB-10); the owner's direction of 2026-11-19 puts every call-form name in the library, marked defined or not.

## lib/rx/classes — Character parts: rx.digit, rx.digits, rx.letter, rx.any_of, rx.range, rx.none_of, ...
slugs:
rulings:
- 2026-11-17 "i agree with repeat. i agree with plurals, why not. can i name the item inside the repeat with [ a = rx.digit ]" (record: "2026-11-17 OWNER — the rx module: one repeat construct; plurals as conveniences")
rejected:
- one construct per plural with its own count arguments (`rx.digits(min, max)`, the rx-module note's row 3) — by owner ruling — one `repeat` does all counting; plurals are one-line definitions over it.
readings:
- the bodies are the rx-module note's construct list (rows 2-8), "definable today"; `rx.letter`'s class follows the program's UCP setting (row 4: "a question of meaning, minor") — the note's, not run.
- `rx.digits := rx.repeat(rx.digit, min = 1)` equals `\d+`: 0 / 0 / 0 of 63 texts (`1a`, length <= 5) — SUPPORTED (preddoc3c PART RC; the draft's PART RX6 on 364).
- `rx.alnum` is one of the singular character parts the draft names (R.1.14, "`rx.digit`, `rx.alnum`, ..."), written "..." in the heading; its body, `[[:alnum:]]` beside `rx.letter`'s `[[:alpha:]]`, is the lane's reading — UNTESTED.
evidence: preddoc3c PART RC; `docs/design/rx_module.md` §2 (the note is SUPERSEDED by the draft R.1.14 for what is ruled).
history:
- 2026-11-17: the rx module proposed (his), the one repeat construct agreed.
- 2026-11-19 (lane preddoc3c): converted.

## lib/rx/repeat — rx.repeat
was: core/patterns/repeat (2026-11-19, a library definition over count holes; the "core holds primitives only" rule of that morning was withdrawn the same day: every call-form name is a library piece)
was: lib/rx/optional-loop (2026-11-19, a piece that only said the name is not provided; its content is a rejected line here (review r59 READ-13))
slugs: count-argument
rulings:
- 2026-11-17 "i agree with the count proposal. i'm curious how the repeat functionality would work however. is it a primative?" (record: "2026-11-17 OWNER RULING — the count proposal")
- 2026-11-17 "i agree with repeat. i agree with plurals, why not. can i name the item inside the repeat with [ a = rx.digit ]" (record: "2026-11-17 OWNER — the rx module: one repeat construct; plurals as conveniences")
- 2026-11-17 "so the two argument form of + is addition, and the single postfix version is 1 or more. if we're going there, lets just do it. + +? * *? ? ??" (record: "2026-11-17 OWNER RULING — quantifier operators")
rejected:
- `repeat` as a primitive — by the two-kinds entry — "`repeat` is therefore a library definition" (the draft R.1.14).
- one binding of an array for every mention (`n` the same member in both places) — by run — `repeat(digit, n, n + 1)`, n := [2, 5], WHOLE `1234` HOLDS only through the cross copy (2,6) (rev 26.1's PART R47 B2; preddoc2 PART RB, sabotage s9 caught).
- `rx.optional` and `rx.loop` as provided names — by owner ruling — the quantifier operators (`x?`, `x??`, `x?+`, `x*`, `x+` and their lazy and possessive forms are the core's operators; counts are `rx.repeat`; a separated list is `list_of`).
readings:
- the three bodies, one per call form, reproduce every ruled example: RX5 (min = n, max = n), the one-argument exact count, every copy illegal, AL2 (`n + 1`), B2 (per mention), RX6 (a labelled item, a condition after it and inside it), the plural `digits` — SUPPORTED (preddoc2 PARTS RX, RB, R6; WHOLE against python's `\d{2,4}`, `\d{2}|\d{4}`, `\d+` on 63 texts, 0 differing).
- "no maximum" written as a second body with the bound left out (the draft's reading; answer-free) — SUPPORTED as a lowering (PART R6, sabotage s11 caught).
- the structural warning when a combination is removed, the can-never-match warning when all are (the manager's proposals) — NOT RUNNABLE.
evidence: PARTS RX4-RX6 of predspec25; rev 26's PART AL; preddoc2 PARTS RX, RB, R6.
history:
- 2026-11-17: the count proposal and the one repeat construct (the draft R.1.14, COUNTS, ONE REPEAT CONSTRUCT).
- 2026-11-19 (lane preddoc2): the core piece `core/patterns/repeat` (a skeleton) and this `?` piece made one, converted in full in the library; `module: rx` from the record's "the rx module".
- (from lib/rx/optional-loop) the note's `rx.loop` with `sep` is `list_of`; `every-pass-spelling` (his loop construct over a conditioned item) stays OPEN in the draft §R.8.
- (from lib/rx/optional-loop) 2026-11-17: proposed in the rx-module note; the quantifier operators ruled the same evening.
- (from lib/rx/optional-loop) 2026-11-19 (lane preddoc3c): written as "not provided".
- 2026-11-19 (lane preddoc4): the piece `lib/rx/optional-loop` deleted, its content moved here (review r59 READ-13).
- 2026-11-19 (lane preddoc6, review r60 COLD-9): "The bodies, one per call form" marked a reading and pointed at the open question core/operators/bindings/call-forms (`rx.repeat(rx.digit, 3)` fits two bodies with different answers).
- 2026-11-19 (lane preddoc6, review r60 RULING-9): the first `was:` line's reason read "the core holds primitives only" as a standing rule; rewritten: it was the rule of that morning, and the owner withdrew the designation the same day ("my "primitive" designation doesn't work", record "2026-11-19 OWNER, refining where provided names live: every `x()` in the library, marked defined in the language or not"); the reason today: every call-form name is a library piece.
- 2026-11-19 (lane predfix61, review r61 F-M, GENERAL-4): "first hole slowest" points at the lift's loop (core/arrays/lift); no answer moves. Status date 2026-11-17 to 2026-11-19.

## lib/structural/capture — capture
slugs:
rulings:
- 2026-11-21 "i agree that captures are explicitly written either in literal form or using a macro like capture()." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name")
rejected:
- the keyword form `export capture(x) := ...` (rev 0) — by the draft — superseded by `@export`.
readings:
- `capture(name, x) := /(?<${name}>${x})/`, the name passed (lane preddoc6, review r60 COLD-8) — SUPPORTED (preddoc6 PART CP).
- `capture(x) := /(?<${x.label}>${x})/` (the draft §5.3, LEAN; the owner's sketch `group(x) := /(?<${x.label}>${x})/`, "lots of hand waving", record "2026-11-14 — compose instead of an option") names the group by its argument's label — SUPPORTED as a lowering (preddoc3c PART CP), but NOT BUILDABLE from the core as written (no field gives a part label's own name); superseded in part by export-rule (rev 26); what the caller gets for a public label two parts both set is caller-ambiguous.
- what `capture(x)` returns for a looped x is not stated (the draft R.11 row 32).
- (the manager's (d) of pure-label) `capture(name, x) := /(?<${name}>${x})/` is the wrapper method in its literal form — SUPPORTED as a wrapper that makes a capture (python `re` groups of its lowering: `d`; predscope_model.py CAPT); his wrapper placeholder `[ d = capture(digits) ]` names the capture from the part label, which this body cannot (the missing field above).
evidence: preddoc3c PART CP.
history:
- 2026-11-19 (lane preddoc2): found as a body with no library piece; (lane preddoc3c): a new piece and section.
- 2026-11-19 (lane preddoc6, review r60 COLD-8): the body could not be built from the core: `.label` is defined only for a part label over an array ("that member's name", core/values/metadata), and inside the body `x` is a parameter, not a path (core/labels/flow: "A binding's name is not a path"). The piece now states `capture(name, x) := /(?<${name}>${x})/` (the name passed as a string to the group-name hole) and keeps the draft's one-parameter sketch as a bullet naming the missing field; the example `capture(x)`, x := `[d = /\d+/]` became `capture("d", /\d+/)`, same answers (preddoc6 PART CP).
- 2026-11-21 (lane predscope, pure-label folded): the bullet until then: "A binding's public labels reach the caller by export with no macro; `capture` stays a way to NAME a capture." (wrong after pure-label: a label reaches the caller only as a capture). Two bullets added (the wrapper reading; the add-on pointer). Status date 2026-11-19 to 2026-11-21.

## lib/structural/capture/add-on — Making a label a capture
slugs: none
rulings:
- 2026-11-21 (class: REQUIREMENT) "so an add on component that converted a label into a capture is needed." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name"); his reason: "the reason for the second one is that someone may use a library form like isodate."
- 2026-11-21 (class: DISCUSSION, nothing ruled) "what i don't know is precisely what that looks like. two methods are to specify it like a wrapper like [ d = capture(digits) ] etc or specify it afterthefact like [ d = digits ] & capture(d) or something. no spelling suggested." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name")
- 2026-11-21 (class: STATEMENT, marked agreed) "1. purely predicate labels and 2. cannot become exported captures (although they might be internal captures)" (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name"); of the `_t` labels
rejected:
readings:
- (the manager's (c) of pure-label) the after-the-fact capture names its label by the visibility rules a condition does, so a `_` label cannot be named, hence cannot be captured, outside its binding — SUPPORTED by the record (statement 1 of core/labels/export, "A private label is visible only inside the binding it is written in"; his "cannot become exported captures (although they might be internal captures)"); untestable by run (a refusal).
- the after-the-fact form has no body in the language (native) (the manager's (d), second half) — UNTESTED (no form is defined).
evidence: predscope_model.py CAPT (what is a capture today).
history:
- 2026-11-21 (lane predscope): a new under-construction piece for his requirement of pure-label; both spellings are placeholders (core/spellings/placeholders).

## lib/structural/each — each, each_group, where, where_group
slugs:
rulings:
- 2026-11-15 "Agree with mapping" (record: "2026-11-14 RULINGS on rev 3's contradictions")
rejected:
- the ordinal as "the second argument when the macro takes one" (rev 9) — by review r10 CENSUS-15 — a two-parameter macro's slot 2 had two claimants.
readings:
- §5.3's rules (the draft's LEAN; mapping a filter by a section RULED): fenced compile-time tools over spelled arrays — not run (no subject).
evidence: the draft §5.3.
history:
- 2026-11-19 (lane preddoc3c): a new piece (census rows `each`, `each_group`, `where`).
- 2026-11-19 (lane preddoc6, review r60 RECOUNT-2): `where(p, X)` added to the heading and body: the history line above claimed it (census row `where`) and the piece did not carry it. The draft §5.3: "`where(p, X)` = SELECT entries by a compile-time STRUCTURAL property (the selecting twin of `each`; not the filter role, §0.3)"; its name table: "`where`, `where_group`, `each_group` | none | LEAN (§3.2, §5.3); candidate cut" — a reading, as the piece.

## lib/structural/sort — sort, unique
slugs:
rulings:
- 2026-11-19 (class: IDEA) "Perhaps then we need a lengthSorted() transform." (record: "2026-11-19 OWNER, discussing class-positions: the nested-loop rule, as if against `fn()`; a `lengthSorted()` transform"); his "Perhaps", an IDEA, not ruled (the ruling's entry lists it under NOT RULED)
- 2026-11-19 (class: PRINCIPLE) "Only solution is sorting output when needed." (record: "2026-11-19 OWNER RULING — quantified-order: PCRE's priority order; and classes lowest to highest; sorting only when asked"); for a lift's order: no built-in length order; the user sorts
- 2026-11-19 (class: REQUEST) "Need a terser sort function for common use." (record: "2026-11-19 OWNER RULING — quantified-order: PCRE's priority order; and classes lowest to highest; sorting only when asked"); a provided name shorter than this piece's `sort` call; its name is a spelling, the manager's to propose; nothing named or defined here
- 2026-11-19 (class: LEAN and REQUEST) "the existing sort function is lean: good as the general purpose sort. Helpful: a shorthand for sorting by longest so all those options don't have to be written out." (record: "2026-11-19 OWNER, on the sort function: the existing one is the general sort; a shorthand for longest first would help"); the name `longest_first` is the manager's placeholder, not his words
rejected:
readings:
- SORT IS SEMANTICS: the record's lean ("`sort(alts, by: length, desc)` exists only as the deliberate leftmost-longest choice. `unique` keeps the first occurrence", record: "2026-11-14 — literals from a file"); the draft §7 — a lean, UNTESTED.
- his `lengthSorted()` is this piece's `sort(alts, by = "length", order = "desc")` under another placeholder name (the record's note under his proposal) — UNTESTED (an idea: nothing is defined).
evidence:
history:
- 2026-11-19 (lane predfix61, review r61 F-L: GENERAL-8, RULING-9): the statement until then: "`sort(alts, by = "length", order = "desc")` reorders an array's alternatives, only as the deliberate leftmost-longest choice; `unique` keeps each entry's first occurrence." ("only as" stood against his "good as the general purpose sort"; the record's 2026-11-14 lean stays above as a reading.) The reading "entries of equal length keeping their order" (the manager's, a stable sort) dropped: two different strings of one length never tie at one position, so it is not observable (review r61 RULING-9). `longest_first` and `lengthSorted()` added to core/spellings/placeholders.
- 2026-11-19 (the manager, after lane predasc): the request bullet restated with his second sentence and the placeholder name `longest_first(X)`; before: "The owner's request, nothing named or defined: \"Need a terser sort function for common use.\" (a provided name shorter than this piece's call; its name is open)."
- 2026-11-19 (lane predloop): his idea `lengthSorted()` noted on the piece (class-positions); nothing defined.
- 2026-11-19 (lane predasc): quantified-order: his principle "Only solution is sorting output when needed." and his request for a terser sort function added as two bullets; nothing named or defined; status unchanged.
- 2026-11-19 (lane preddoc5): a new piece (review r59 COMPB-8); the owner's direction of 2026-11-19 puts every call-form name in the library, marked defined or not.

## lib/structural/sorted — sorted, distinct
slugs:
rulings:
rejected:
readings:
- "`sorted` and `distinct` take the array form" is the MANAGER's text in the pass-list-read entry ("MINE, to be checked", record: "2026-11-17 OWNER RULING — pass-list-read"), carried by the draft (R.1.7) — UNTESTED; the array as its own type is the owner's point (3), cited on core/values/reads.
evidence:
history:
- 2026-11-19 (lane preddoc5): a new piece (review r59 COMPB-8); the owner's direction of 2026-11-19 puts every call-form name in the library, marked defined or not.
- 2026-11-21 (lane predarr, array-vs-passes ruled): the statement's "(the other passes, his `@x`)" became "(every setting of the name, his `@x`)": the array is the settings, not the passes.
## lib/json/members — json.row, json.string
slugs:
rulings:
rejected:
readings:
- `json.row` is a module member reached by the one `.` (the draft §3.2 tool 4, §7) and E-JSONL's (the draft §12.1); `json.string` stays in the `json` module after `json.quoted`'s cut (the draft §9, "the `json` module keeps `json.string`, the literal's rx") — UNTESTED; no body is written in the draft.
evidence:
history:
- 2026-11-19 (lane preddoc5): a new piece (review r59 COMPB-8); the owner's direction of 2026-11-19 puts every call-form name in the library, marked defined or not.

## lib/planned/standard — days, weekday_of, days_in, luhn
slugs:
rulings:
rejected:
readings:
- called, never bound with `:=`, in the draft (§4.4, §4.6 "the library's `days_in`", §5.1's library-name list, §6.1, §12) — the lane's reading: planned standard-library content (core/modules/standard-library).
- the regular twin: the record's lean ("2026-11-14 — a standard library of blessed callouts (Frank)", lean ADOPT, plan row [BLESSED-CALLOUTS]) — a lean, UNTESTED.
evidence:
history:
- 2026-11-19 (lane preddoc5): a new piece (review r59 COMPB-9); the owner's direction of 2026-11-19 puts every call-form name in the library, marked defined or not.
- 2026-11-19 (lane preddoc6, review r60 COLD-19): `weekday` in the regular-twin bullet written `weekday_of`, as the piece calls it; the library header gives "the worked examples" their home (the frozen draft §12, the acceptance cases).
