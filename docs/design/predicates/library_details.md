# The predicate language: details (library)

One entry per tag of `library.md`, in the same order (fields as in `core_details.md`). The record
is `docs/design/plan_row_bodies/COND-FAMILY.md`; a skeleton entry's source is `predicates_draft.md` revision 29.1.

## lib/builtin/enumerate — Enumerate
was: core/arrays/enumerate (2026-11-19, a call-form name: the owner, "all macros "x()" should be in the library document"; the manager's ruling R-1 of lane preddoc4)
slugs:
rulings:
- 2026-11-14 "I love it. Enumerate go." (record: "2026-11-14 RULINGS on the predx gaps"); design adoption, with its rules: the budget, PCRE priority order, a built-in
rejected:
- widest first (one more copy first everywhere) as the order — by review r52 D (TABLES-4): it parts from PCRE priority on `(?:a|ab){1,2}` (SEARCHED `aba` `aba`@0 against `a`@0); preddoc3b sabotage s8 caught.
- codepoint order for a class's members in a lift — by owner ruling — class-order (core/arrays/class-order).
readings:
- the enumerator's ORDER equals PCRE's own pattern on re-joining — SUPPORTED (preddoc3b EXenum: 0 / 0 / 0 of 63 texts; PART PR of predspec281 on libpcre2).
- an interior lookaround or a backreference in the argument: NOT STATED (PART PR of predspec281).
evidence: preddoc3b EXenum.
history:
- 2026-11-14: "Enumerate go"; the draft §5.5. 2026-11-18: construction-line made it the line of single-value functions. 2026-11-19: class-order replaced the codepoint lean for lifts.
- 2026-11-19 (lane preddoc3b): converted from `?`.
- 2026-11-19 (lane preddoc4): moved to the library, section `lib/builtin` (the owner's direction of 2026-11-19, R-1).

## lib/builtin/enumerate/class-index — The order of a class in enumerate
was: core/arrays/class-index (2026-11-19, a call-form name: the owner, "all macros "x()" should be in the library document"; the manager's ruling R-1 of lane preddoc4)
slugs: class-index
rulings:
rejected:
readings:
- (a) is the draft's reading (rev 29's narrowing of the codepoint lean, not the ruling's words) — the record says the lean "is replaced", with no carve-out; (a) vs (b) 0 / 250 / 570 of 3,906; (a) vs (c) 0 / 0 / 0 (PART CO of predspec291).
evidence: preddoc3b EXclassindex; PART CO of predspec291 (P29-10).
history:
- 2026-11-19: new with class-order; re-worded by review r54 P29-10.
- 2026-11-19 (lane preddoc4): moved to the library, section `lib/builtin` (the owner's direction of 2026-11-19, R-1).

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
evidence: docs/dev/lanes/preddoc4_evidence/ PART PT.
history:
- 2026-11-19 (lane preddoc4): a new piece: a name on the closed built-in list with no piece (review r59 COMPB-3).

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
evidence: preddoc3c PARTS CA, CAneg; the draft's rev 28 PART AC, rev 28.1 PART FF, rev 29 PART AC, rev 29.1 PART AC.
history:
- 2026-11-15: a primitive for now, the basis a follow-up ([PRED-REREAD], the draft §13 O70).
- 2026-11-18 (rev 28): flags-propagate re-ran the candidate body; rev 28.1: the `(?-i)` difference; rev 29: T-c, equal for plain and positive filter-role arguments; rev 29.1: the negated operand differs; any-case-body named as a gap, not asked.
- 2026-11-19 (lane preddoc3c): converted, `open any-case-body`.

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
- caveats (the draft's): two helper bindings beside the body; `count`'s budget applies to `nchars`; the label `ch` visible.
evidence: preddoc3c PART LE; review r16 `bodies_check.out`.
history:
- 2026-11-14: named in OWN-1; 2026-11-15 (rev 15): a body (review r16 FIXIND-3).
- 2026-11-18: his `length($y)` (an image) is written `strlen($y)` (the draft's A26), so this filter keeps its name.
- 2026-11-19 (lane preddoc3c): a new piece (a provided name the library lacked: census row `length`).
- 2026-11-19 (lane preddoc4): `needs:` the computed-label piece and lib/counting/count, the two names its body uses (review r59 READ-8).

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

## lib/control/peek — peek
was: core/conditional/peek (2026-11-19, the owner: core document macros are defined in the library unless primitive)
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
was: core/conditional/when (2026-11-19, the owner: core document macros are defined in the library unless primitive)
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
was: core/conditional/test (2026-11-19, the owner: core document macros are defined in the library unless primitive)
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
slugs: hit-carry hit-carry-depth min-values nullable-meaning
rulings:
- 2026-11-15 "1. if I understand this question, it's asking if the search rx follows non-pcre matching behavior? If that's the question, then the answer is it should always follow it if for no other reason than that's what's expected." (record: "2026-11-14 RULINGS on rev 3's contradictions")
- 2026-11-15 "1 occurances." (record: "2026-11-15 RULING — the provided transform `search` is renamed `occurrences`")
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "Agree with all three." (record: "2026-11-17 OWNER RULING — the three remaining error-or-warning candidates")
- 2026-11-18 "hit-carry: occurrences is a simple regex rewrite ? So what the user provides gets inserted into a template hole like usual? If this is so, then the user is creating this scenario themselves. They can simply put the condition after the label to get the normal behavior. In cases where the user puts the condition before the label, they are expecting carries behavior" (record: "2026-11-18 OWNER RULING — hit-carry: it carries, because `occurrences` is a rewrite")
- 2026-11-18 "hit-carry: warning on nullable" (record: "2026-11-18 OWNER RULING — nullable argument: a warning")
- 2026-11-15 "occurrences(x, label = \"foo\")" (record: "2026-11-15 RULINGS — a per-call hit name; no count warning; the hole is the scope an `&` in it anchors to")
rejected:
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
evidence: preddoc3c PART OC; the draft R.1.9, rev 26 PART H, rev 26.1 PART R47.
history:
- 2026-11-14: the `contains` family; 2026-11-15: PCRE's parse, `min` (0 or 1), no `max`; renamed from `search` (rev 13).
- 2026-11-17: regex-settles (his one-pattern lazy-gap model, "It's essentially /(.*(${rx}))*.*/ So not global"); min-values.
- 2026-11-18: hit-carry; the nullable argument a warning; the hits of a nullable argument corrected twice by the manager.
- 2026-11-19 (lane preddoc3c): converted.
- 2026-11-19 (lane preddoc4): the whole-text idiom `J & C & occurrences(M)` moved here from core/model/modes, whose ruling (whole-text, "adopt it if it's legal") stays cited there (review r59 PLACE-2 (b)).
- 2026-11-19 (lane preddoc4): the ruled per-call hit name added to the base (review r59 COMPB-8); its spelling stays a placeholder.
- 2026-11-19 (lane preddoc5): the slug nullable-meaning moved here from core/conditions/defaults, which named it this piece's fact (review r59 COMPA-13).

## lib/search/hits — hits
slugs: hits-committed hits-text hits-pass hit-list
rulings:
- 2026-11-17 "hits-text: yes but spelling to be reviewed with all other spellings." (record: "2026-11-17 OWNER RULING — the hit list: atomic and anchored")
rejected:
- each hit atomic but not the loop, `\A(?:.*?(?>(?<n>\d+)))*\D*\z` with the list judged after it — by run — the lazy gap is re-entered and swallows a number's start: "every hit under 100" HOLDS on all four texts with hits [`34`], [`12`, `34`], [`12`, `45`], [`0`, `12`] (the draft R.1.9; preddoc3c PART HI reproduces the four lists; sabotage s11 caught).
- the stretch reading (SEARCHED `x300 12` gives `x30`@0 with [`30`]) — by owner ruling — hits-text: standing alone the list is the whole subject's.
readings:
- the body (an atomic group around the whole loop, anchored at both ends) gives the printed lists and verdicts: `1234` FAILS [`1234`], `12 34` HOLDS, `12 345` FAILS, `x300 12` FAILS; with an optional label `axa` FAILS (the last hit's own g unset), `aax` HOLDS — SUPPORTED (preddoc3c PART HI).
- hits-pass and some-own: a bare condition after it reads the last hit's own labels (closed by entailment, the draft §R.8) — SUPPORTED for the optional-label rows (PART HI).
- `module: ?`; the spelling `hits` is a placeholder, his `all_matches(rx)`.
evidence: preddoc3c PART HI; the draft R.1.9, rev 24.4 PART H.
history:
- 2026-11-17: "OWNER on what `hits` is" (questions), then the ruling: atomic and anchored (hits-committed, hits-text).
- 2026-11-19 (lane preddoc3c): converted.
- 2026-11-19 (lane preddoc5): the slug hit-list moved here from core/model/table, whose reading named this piece as the one deciding it (review r59 PLACE-4).

## lib/search/contains — contains
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
evidence: preddoc3c PART SW.
history:
- 2026-11-14/15: the `contains` family; the record's body (11-15); the draft kept `occurrences(x, min = 1)` (lib/search/contains/by-occurrences).
- 2026-11-19 (lane preddoc3c): converted; the draft's spelling split into its own piece (one piece, one status).

## lib/search/contains/by-occurrences — contains as occurrences
slugs:
rulings:
rejected:
readings:
- `contains(x) := occurrences(x, min = 1)` (the draft's LEAN, §2.6, §8: chosen so x's labels read as the leftmost hit) — the same set as the ruled gap body, 0 / 0 / 0 of 121 texts (`ab` over `abx`, length <= 4) in all three modes — SUPPORTED (preddoc3c PART SWocc).
- it also equals `occurrences(x) & some((hit: /(?s).*/))` (the draft) — UNTESTED here.
evidence: preddoc3c PART SWocc.
history:
- 2026-11-15 (rev 9-12): the draft kept this spelling against the record's text, "the same sets".
- 2026-11-19 (lane preddoc3c): split from `contains` (a new sub-piece).

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
slugs:
rulings:
- 2026-11-15 "Ok I agree." (record: "2026-11-14 RULINGS on rev 3's contradictions")
rejected:
readings:
- the record's body `/.*${rx}/` with the gap crossing line breaks: on `ab123` with `(?<n>\d+)`, n = `3` (greedy) — SUPPORTED as the record's text (preddoc3c PART SW).
evidence: preddoc3c PART SW.
history:
- 2026-11-15: the plain gap body (rev 12); the draft kept a lazy gap (lib/search/ends-with/lazy-gap).
- 2026-11-19 (lane preddoc3c): converted; the lazy gap split into its own piece.

## lib/search/ends-with/lazy-gap — endsWith with a lazy gap
slugs:
rulings:
rejected:
readings:
- the lazy gap (the draft's LEAN since rev 9, kept against the record's text): n = `123` on `ab123`; rev 8's greedy `.*` gave `3` (libpcre2) — SUPPORTED (preddoc3c PART SW).
- "as SETS nothing changes" — SUPPORTED (a gap is a gap); the searched stretch differs (`x12 34`: `x12`@0 against `x12 34`@0).
evidence: preddoc3c PART SW.
history:
- rev 9-10 (2026-11-15): the lazy gap chosen for how the argument's labels read; rev 12 kept it against the record's `/.*${rx}/`.
- 2026-11-19 (lane preddoc3c): split from `endsWith`.

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
- 2026-11-15 "3. could you use some() to get some hits?" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING — SEARCH IS A TRANSFORM"
- 2026-11-15 "Do it" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING — SEARCH IS A TRANSFORM"
- 2026-11-16 "all-question: retire" (record: "2026-11-16 OWNER RULING — all-question: retire")
- 2026-11-17 "after-loop-read: ok I see it. Last pass own label makes sense" (record: "2026-11-17 OWNER RULING — after-loop-read: the last pass's own label")
rejected:
- `all` as a group question — by owner ruling — all-question: retire.
- `occurs.some` — by the draft (rev 7's, removed, not aliased) — `some(c)` is the one spelling.
readings:
- false on zero passes, each pass judged with its own labels (the draft §4.3's group-questions table) — the draft's reading; SUPPORTED for its example (preddoc4 PART SO; sabotage s8, "every pass", caught).
- `some` is native to the language: it walks a pass table no body can reach (review r59 PLACE-3) — the lane's reading under R-1 (`defined: native`).
evidence: docs/dev/lanes/preddoc4_evidence/ PART SO; the draft §4.3, R.4.
history:
- 2026-11-19 (lane preddoc4): a new piece: ruled pieces used `some` with no piece (review r59 PRIMITIVES-MISSING, READ-6).
- 2026-11-19 (lane preddoc5): the slug some-own (the draft's, closed by entailment) moved here from lib/search/hits; there was no `some` piece when it was homed (review r59 PLACE-4).

## lib/counting/count — count
slugs: count-budget
rulings:
- 2026-11-15 "counts: perhaps the solution is both. you can use count() until you can't then you can use 'occurs' as a fallback" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING (lean) — counts: `count()` first, `occurs` as the fallback"
- 2026-11-15 "i would refuse count() on budget or as a recommended way to reduce states rather than rules" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING — when `count()` gives way to `occurs`: by BUDGET, not by rule"
- 2026-11-15 "4. agree. Allows "even()" or other checks for count." (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULINGS — the five open items"
- 2026-11-15 "Predicate count/occurs issue: it would be a later optimization plan item that if pcrec could show no change in semantics that it convert count() into occurs" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 OWNER NOTE — `count()` -> `occurs` as a LATER OPTIMIZATION"
rejected:
- `count()` refused in a set position by rule (the manager's "until you can't" reading) — by owner ruling — "by BUDGET, not by rule" (the reading WITHDRAWN in the record).
readings:
- `n := count((d: "7"))`, `/(?:(?<d>\d),)+/ & (n: ==2)`: WHOLE `7,1,7,` HOLDS, `7,1,` FAILS / SEARCHED `7,7,7,` `7,7,`@0 / FIND-ALL [`7,7,`@0, `1,7,7,`@7] — SUPPORTED (preddoc4 PART CO; sabotage s9, every pass counted, caught).
- the budget is one measured quantity, named with the "too many classes" budget (the five open items, (3)); no number stated.
evidence: docs/dev/lanes/preddoc4_evidence/ PART CO; plan row [COUNT-TO-OCCURS].
history:
- 2026-11-19 (lane preddoc4): a new piece: `count(c)` was the body helper of `length` with no piece (review r59 PRIMITIVES-MISSING, READ-6). The slug count-budget is the lane's name for the budget ruling.
- 2026-11-19 (lane preddoc6, review r60 COLD-2): the base's "`even()` on a count" (his word, "Allows "even()" or other checks for count", quoted above) written as the set it names, `/\d*[02468]/`: no piece provides `even`.

## lib/counting/occurs — occurs.exactly, .at_least, .at_most, .none
slugs:
rulings:
- 2026-11-14 "more obscure but valuable" (record: "2026-11-14 RULING — counting occurrences")
rejected:
- `occurs.some` and `occurs.all` — by the draft (rev 7's, removed, not aliased; LEAN) — `some(c)` is the one spelling; `all` was retired (all-question).
- a namespace `label` (`label.exactly(1, ...)`) — by the record — it clashes with element metadata `x.label`.
readings:
- the family is RULED as a library (2026-11-14); the name `occurs` ruled in use (the draft §8 STATUS).
- `NOT some(c)` = `occurs.none(c)`; the every-pass form `some(c) & occurs.none(NOT c)` equals `REP & c` on 364 texts (the draft R.4's W1-W9 table) — the draft's runs, not re-run here.
- `count(c)` first, `occurs` the fallback (LEAN); `count()` refused only on budget (RULED) — the core's group questions, which have no core piece yet.
evidence: the draft §8, §4.3, R.4.
history:
- 2026-11-14: agreed as a library family (all, some, none, exactly, at_least, at_most); 2026-11-15 (rev 8): counts only.
- 2026-11-19 (lane preddoc3c): converted; the heading drops `.some` (withdrawn).

## lib/counting/every-pass — Every pass, named
slugs: every-pass-spelling
rulings:
- 2026-11-17 "last-pass-default: regex. I want to have the method of achieving the alternative meanings defined and tested so we don't lose that functionality." (record: "2026-11-17 OWNER RULING — last-pass-default: regex"); the standing instruction: every meaning the draft could express before (every pass with and without at-least-one, not-every, some / count / occurs, ...) has its spelling DEFINED and TESTED
rejected:
readings:
- OPEN in the draft (§R.8, row every-pass-home: "the conditioned item inside `repeat` is the item form"; the draft R.4's W1a, W1b); the owner, the evening of 2026-11-16 as the draft quotes him: "assign the condition inside the loop to get the all behavior" — the item form, today's way; whether a name exists is not asked.
- `some(c) & occurs.none(NOT c)` equals `REP & c` on 364 texts (the draft R.4's W1-W9 table) — the draft's runs, not re-run here.
evidence: the draft R.4, §R.8.
history:
- 2026-11-19 (lane preddoc4): a new open piece: the slug every-pass-spelling had no home (review r59 PRIMITIVES-MISSING).

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
- its kin `right` and `mid`: the owner's question "What about string operators like left, right, mid?" (record bullet STRING OPERATIONS, 2026-11-13) and the draft R.1.16 T9's "and kin" name them; neither is defined; their FILTER names are rejected under lib/sets/prefix-in — named, not defined (no piece of their own: they would be pieces of this kind once one is wanted).
evidence: preddoc3c PART LF; the draft R.1.16 T9.
history:
- 2026-11-18: match-is-rx; construction-line.
- 2026-11-19 (lane preddoc3c): converted.

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
was: core/patterns/repeat (2026-11-19, a library definition over count holes: the core holds primitives only)
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

## lib/structural/capture — capture
slugs:
rulings:
rejected:
- the keyword form `export capture(x) := ...` (rev 0) — by the draft — superseded by `@export`.
readings:
- `capture(x) := /(?<${x.label}>${x})/` (the draft §5.3, LEAN) names the group by its argument's label — SUPPORTED as a lowering (preddoc3c PART CP); superseded in part by export-rule (rev 26); what the caller gets for a public label two parts both set is caller-ambiguous.
- what `capture(x)` returns for a looped x is not stated (the draft R.11 row 32).
evidence: preddoc3c PART CP.
history:
- 2026-11-19 (lane preddoc2): found as a body with no library piece; (lane preddoc3c): a new piece and section.

## lib/structural/each — each, each_group, where_group
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

## lib/structural/sort — sort, unique
slugs:
rulings:
rejected:
readings:
- SORT IS SEMANTICS: the record's lean ("`sort(alts, by: length, desc)` exists only as the deliberate leftmost-longest choice. `unique` keeps the first occurrence", record: "2026-11-14 — literals from a file"); the draft §7 — a lean, UNTESTED.
evidence:
history:
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
