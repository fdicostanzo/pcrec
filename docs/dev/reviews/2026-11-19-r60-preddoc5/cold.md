# CRITIC COLD: r60 preddoc5

## Findings


## PASS 1 (cold read of core.md then library.md, whole, without r59)

Method: read R/tree/docs/design/predicates/core.md (1,268 lines) and library.md (629 lines) top to bottom in chunks;
every printed example re-derived by hand from the piece's text (69 example lines in core, 34 in library); the 51
examples that reduce to a plain regex run with `python3 -I` `re` (script: cold/run.py, longest witness `7,7,7, 1,7,7,`
13 chars / `abcdefghij-10` by hand; output reproduced every printed WHOLE/SEARCHED/FIND-ALL answer).

### COLD-1  CONFIRMED   severity: doc   effort: S
where: core.md core/operators/statements (line 1042-1045) vs library.md (whole file)
what: The core says the built-ins include "the effects `@warn`, `@export`, `@options` ... Every provided name written
as a call has its piece in the library (`library.md`), these included." The library has NO piece for `@export(...)`,
`@warn.off(...)`, `@warn.error(...)`, `@options.strict(...)` (lib/builtin holds enumerate, import, import/filter,
pattern, eval; lib/records holds param, file_text, records). `@export` is described only in core/modules/export,
`@warn.*`/`@options.strict` only in core/diagnostics/warnings - i.e. call-form names live in the core, against the
core's own sentence and the doc_format rule "EVERY CALL-FORM NAME IS A LIBRARY PIECE".
evidence: `grep -n "@export\|@warn\|@options" library.md` -> only line 55 ("as `@export`'s is") and the @each lines;
no heading. core.md:1045 "these included".
proposed fix: add library pieces lib/builtin/export (`defined: native (a compile-time effect on the file's map)`),
lib/builtin/warn (`@warn.off`, `@warn.error`), lib/builtin/options (`@options.strict`), each pointing back at the
core pieces that hold the meaning; or reword core 1045 to exempt `@` effects (less consistent).

### COLD-2  CONFIRMED   severity: doc   effort: S
where: library.md lib/counting/count (line 394), lib/builtin/import/filter (line 64); core.md core/modules/naming (1150)
what: Call-form names used with no library piece: `even()` ("`even()` on a count") and `search(string)` (inside the
import filter). `search` is moreover a name the core REJECTS by rule: core/modules/naming "never `unpad`, `trim` or
`search`" ... "`search` acts on the text". A reader meets a forbidden name used as if provided.
evidence: grep above: library.md:394, :64; core.md:1150-1154. No heading for even/search in library.md.
proposed fix: `even` -> a lib/sets piece (`even := /\d*[02468]/`, defined: language) or replace by an existing set
(`count(...) & between(..)`); write the import filter with a non-call placeholder (`import("f1"|"f2", names = /.../)`)
or a piece-backed name, never `search`.

### COLD-3  CONFIRMED   severity: answer   effort: S
where: core.md core/holes/bare-condition (958, 959, 962 example), core/spellings/placeholders (1253),
core/spellings/condition-parentheses (1267)
what: The printed example program `/\d${(0: digit)}x/` uses a bare name `digit` on the value side of a condition.
By core/conditions/form "on the value side a bare name is a binding"; no binding `digit` is given in the example,
none is provided by the library (the provided part is `rx.digit`, module `rx`, not in the default set:
core/modules/default-set holds only `peek`), and core/operators/statements makes "an undeclared name that is not a
label" a compile error. Built mechanically, the example is a COMPILE ERROR, not the printed WHOLE `7x` HOLDS ...
evidence: library.md:546 `rx.digit := /\d/` is the only definition; lib/control/peek is the only `default: yes`.
proposed fix: write the example with its binding (`digit := /\d/`) as other examples do (`wb := ...`), or use
`/\d/` inline: `/\d${(0: /\d/)}x/`.

### COLD-4  CONFIRMED   severity: doc   effort: S
where: core.md core/diagnostics/errors (line 1179); no other mention except core/holes/flags 913 ("its recursion")
what: Term used without a definition: the error index lists "a recursion through a parameterised definition other
than one integer literal parameter strictly decreasing to a literal base case | (a reading; no piece)". Nothing in
the base files says a binding or macro may refer to itself at all (core/operators/bindings: "Macros expand at
compile time, inlined per use" - which, read literally, never terminates for any recursion). A new session cannot
learn from the base whether recursion exists, what "one integer literal parameter" means, or why the base case
must be literal. An error row with "no piece" is also the only row of the index without a home.
proposed fix: a core piece core/operators/recursion (status reading) stating the allowed shape with a run example
(e.g. `pow2(n) := when(...)` or whatever the draft held), or drop the row until the piece exists.

### COLD-5  CONFIRMED   severity: doc   effort: M
where: core.md core/diagnostics/errors (1160-1184)
what: The piece says "Each error below is ruled or read in its own piece; this piece is the index", but at least 12
compile errors stated in the base files have no row:
  (1) an ambiguous reference across `&` (core/labels/flow 313, core/labels/export 327, core/labels/paths 354);
  (2) a binding's name used as a path, `A.h` (core/labels/flow 315);
  (3) a backreference/number to a name the rx does not define, the "free-name" error (core/labels/export 335,
      core/labels/backreferences 367, core/holes/labels 933) - the row at 1172 covers only the two-groups case;
  (4) `P & x: S` and `[x: S]` (core/conditions/form 413);
  (5) a default of several strings (core/conditions/defaults 487);
  (6) a user label named `index` or `label` (core/values/metadata 658);
  (7) a `:` in a definition head (core/operators/bindings 1026);
  (8) `\K`, `(*ACCEPT)`, `\G`, verbs, callouts inside a larger program (core/patterns/literals 200, "refused");
  (9) `when` without `then` (lib/control/when 187);
  (10) `pattern($x)` on a group that is "not self-contained" (lib/builtin/pattern 77);
  (11) an imported element above the requested level (lib/builtin/import 57);
  (12) a failed `@assert.*` (lib/assert/assert 473).
A new session using the index to learn "what is refused" gets a partial list presented as complete.
evidence: `grep -nE "compile error|is an error|are errors|is the error" core.md library.md` (78 hits) compared row by
row with the 14 index rows.
proposed fix: add the rows (or state that the index covers core errors only and add (1)-(8)); a lint check "every
'compile error' sentence's piece is named in the index" would keep it whole.

### COLD-6  CONFIRMED   severity: doc   effort: S
where: core.md core/values/functions (680 statement vs 686 clause 1) and lib/builtin/enumerate (18)
what: Contradiction inside one piece. Statement: "A single-value function accepts an rx exactly where `enumerate`
accepts it ...; ANY OTHER rx is under construction." Clause 1: an rx with an assertion looking outside the operand is
"`enumerate`'s compile error" - an rx enumerate does not accept, yet a compile error, not under construction.
Clause 2 then makes "infinite or over-budget" under construction, while lib/builtin/enumerate makes the same rx a
COMPILE ERROR for enumerate - so "exactly where enumerate accepts it" is not the line either.
proposed fix: statement: "... applied to each enumerated string; an outward-looking assertion is enumerate's compile
error, an infinite or over-budget rx is under construction" (the clauses as the rule), or say the statement
summarises clause 3 only.

### COLD-7  CONFIRMED   severity: doc   effort: M
where: core.md and library.md, 50 lines (list: `grep -nE "draft|\bhis\b|\bHis\b|owner|manager|the record|\btold\b|\blean\b|was cut|retired|revision|wrote"`, principle headings excluded)
what: History / provenance / process talk in the base files beyond what doc_format permits (a principle piece quoting
him; the manager's names on principles). Examples outside core/principles:
  core 555 "On a condition the record also wrote `!`; the documents write `NOT` there";
  core 617-618 "`<"256"` strings, `2.5` ... are the draft's readings, not ruled";
  core 821 "(a reading: the manager's call)"; core 921/926 "The reading today (the draft's)", "the draft's run";
  core 924 "His remark: ... (on this question; not asked as a ruling)";
  core 967/969 "The manager's reading ... the rival"; core 1108 "his lean"; core 1124 "the owner's";
  core 1146 "(a lean, its own plan row)"; core 1187, 1197 "the manager's call"; core 1244-1258 "his `€`, `¥`",
  "his `A :: B`", "his `@x`", "his `(?<:x>foo)`";
  core 95 "a mismatch with his words is told the same turn" (a process rule, not language);
  core 10 / 12 (header) "reading (the draft's or the manager's)", "predicates_draft.md, which stays the source";
  lib 78 "(the draft's reading)"; lib 127 "by the owner's ruling"; lib 136 "the owner wants"; lib 140-141 "His uses",
  "his words"; lib 178 "(the owner's lean)"; lib 194 "the owner's `null`"; lib 250, 268, 371, 442, 446, 455, 603
  ("his ..."); lib 307 "as the owner wrote it"; lib 383 "`all` is retired" (revision talk); lib 411 "no example of
  the draft is printed"; lib 421 "the draft's runs"; lib 536 "Its use in the record"; lib 611 "as the draft's JSONL
  example uses them"; lib 618 "the decoding filter was cut" (revision talk); lib 629 "is the lean".
Also record-slug/process words a reader cannot resolve in the warnings table's `ground` column (core 1203-1218:
"polarity-rule", "empty-search-error", "the accepted list", "accepted", "default-unused", "anchor-warn-scope",
"plus-operands", "name resolution").
L6 does not catch these (its word list is revision marks), so the lint is clean.
proposed fix: in the base, state the rule and its status word only ("a reading", "open"); move who-said/who-leans,
"the draft's", "retired", "was cut", "his spelling" to the details entries; replace the `ground` column by the
status word plus the piece tag (the slugs belong in details).

### COLD-8  CONFIRMED   severity: answer   effort: S
where: library.md lib/structural/capture (575, 581) vs core.md core/values/metadata (653-659), core/labels/flow (315)
what: The body `capture(x) := /(?<${x.label}>${x})/` with the example x := `[d = /\d+/]` cannot be built from the core.
`.label` is defined only as a field of "a part label over an ARRAY" ("that member's name"); here the argument is a
part-labelled pattern, and `x` inside the body is a parameter/binding - core/labels/flow: "A binding's name is not a
path (`A.h` is an error where a label is referenced)". Read by the core's rules, `x.label` is either the path error or
the name of the (unnamed) array member, not `d`. Even granting `x.label` = `d`, the literal substitution is
`/(?<d>(?:(?<d>\d+)))/`-shaped (the part label `[d = A]` is itself the group `(?<d>A)`, core/labels/paths 352), two
nested groups of one name, which the example does not mention (the printed `(12)` happens to agree).
evidence: core.md:653 "A part label over an array carries two fields"; :315; :352; python run of the mechanical
form with the inner group renamed: WHOLE `12` HOLDS, SEARCHED `x12` `12`@1, FIND-ALL [`1`@0, `23`@2] (the matching
agrees; the definition does not stand).
proposed fix: define a field of a part label giving its own name (e.g. `.name`, on any part label) in
core/values/metadata, or write capture with an explicit name parameter, `capture(name, x) := /(?<${name}>${x})/`.

### COLD-9  CONFIRMED   severity: design   effort: M
where: library.md lib/rx/repeat (559-561), lib/modifiers/padded (91, 96-97) vs core.md core/operators/bindings (1018-1026)
what: Two library names are defined by SEVERAL bodies selected by call form - `repeat(x, n)`, `repeat(x, min, max)`,
`repeat(x, min)`; `padded(rx)`, `padded(rx, n)` - but the core's macro rule has one head per name: positional
arguments are the REQUIRED parameters in declared order, optional ones are keyword settings with defaults. Nothing
in the core defines overloading, and the bodies collide: `rx.repeat(rx.digit, 3)` fits both `repeat(x, n)` (exactly
3) and `repeat(x, min)` (3 or more); `padded`'s width is an optional parameter passed positionally, which the core
does not allow. A new session cannot tell which body a call takes.
proposed fix (GENERAL FORM + UNLOCK): one head per name with keyword settings - `repeat(x, min = 0, max = ...)`,
`padded(rx, width = ...)` - which needs one missing core fact: a way to say "no maximum" / "no width" as a value or
an absent setting (an `unset` default, or the count hole accepting an empty value as `{min,}`). Trigger: the first
library name with an optional setting that changes the body's SHAPE; it is already here twice. Or, minimal: a core
sentence admitting several bodies per name, chosen by the set of parameters passed, with `repeat(x, n)` renamed
`repeat(x, exactly = n)`.

### COLD-10  CONFIRMED   severity: design   effort: S
where: library.md lib/search/ends-with (303, ruled) vs lib/search/ends-with/lazy-gap (312, reading);
lib/search/contains (272, ruled) vs lib/search/contains/by-occurrences (282, reading)
what: Two names each have two definitions in the base, both stated in the present tense: "`endsWith(s)` is the plain
gap body `/(?s:.*)(?:${s})/`" and "`endsWith(s)` is written with a LAZY gap, `/(?s:.*?)(?:${s})/`"; likewise
`contains(s)` = the gap body and `contains(x)` "is written `occurrences(x, min = 1)`". The pieces themselves say the
answers differ: endsWith(/(?<n>\d+)/) on `ab123` n = `3` vs `123`; SEARCHED `x12 34` `x12 34`@0 vs `x12`@0 (python
confirms both). A new session cannot tell which body the name has; the sub-piece's status `reading` beside a `ruled`
parent reads as a pending replacement but nothing says so (no `open` slug).
evidence: cold/run.py rows lib/search/ends-with and lib/search/ends-with/lazy-gap.
proposed fix: make each sub-piece an `open <slug>` ("which body defines endsWith: greedy (ruled) or lazy?") with
the ruled body stated as current, or move the alternative bodies to the details entry as candidates.

### COLD-11  CONFIRMED   severity: doc   effort: S
where: core.md examples core/patterns/atomic (263 `atomic(B | A)`), core/values/functions (693 `left(...)`),
core/holes/negated-class (823 `join(c)`), core/holes/count (788 `rx.repeat(rx.digit, ...)`); every library example
(`when(...)`, `occurrences(...)`, `quoted(...)`, `between(...)`, ...); core/modules/default-set (1104-1108)
what: How a provided name with `module: ?` is reached is never stated. The base's only rule: a default-set name is
written bare (only `peek` carries `default: yes`); everything else comes through `import` (core/modules, "A module
is reached by `import`"); an undeclared name is a compile error (core/operators/statements). Built mechanically,
the core examples above and nearly every library example are compile errors (no import line, no binding), and
`rx.repeat` needs `rx` bound. 46 of the 53 library pieces have `module: ?` (`grep -c "^module: ?" library.md`), so a reader cannot write a working
program that calls `when` or `between`.
evidence: example census (grep of example lines for `name(`): core calls atomic, join, left, peek, rx.repeat; only
peek is reachable bare.
proposed fix: one sentence in core/modules/default-set (or the library header): "Examples call every provided name
bare, as if imported; how a `module: ?` name is reached is open (core/modules/default-set/members)." That makes the
assumption explicit without deciding the open question.

### COLD-12  CONFIRMED   severity: doc   effort: S
where: core.md core/conditions/two-valued (423-428)
what: "`NOT (h: <5)`, `(h: !<5)` and `P & !(P & (h: <5))` are three meanings", but the printed table shows the first
and third rows identical on all three texts (HOLDS / FAILS / HOLDS). The table proves two meanings; the third
differs only where P has several paths, which no column shows. A new reader concludes NOT and the complement form
are the same.
evidence: hand derivation of a pattern that parts them: P = `/(?<h>\d)?\d?x/` on `3x`: `NOT (h: <5)` - first path h=3
rejected, next path (h absent, \d=3) holds -> HOLDS; `P & !(P & (h: <5))` - `P & (h: <5)` matches `3x`, so the
complement fails -> FAILS.
proposed fix: add a fourth column on such a P (`3x` on `/(?<h>\d)?\d?x/`: HOLDS / FAILS / FAILS).

### COLD-13  CONFIRMED   severity: doc   effort: S
where: core.md core/patterns/literals (200-201) vs core/labels/labels-vs-captures (284-285), core/modules/standard-library (1145)
what: Contradiction on callouts: literals says inside a larger program "callouts are refused until their predicate
meaning is defined"; labels-vs-captures lists "a callout" among the places that read the capture inside rx text (as
if legal), and standard-library has members that are "emitted C code ... the compiler choosing the automaton or the
callout". The same literals bullet also contradicts its own first bullet's "no strict subset" unless one notices
"inside a larger program".
proposed fix: labels-vs-captures: drop "a callout" or add "(where callouts are allowed: a one-literal program)";
standard-library: say the blessed callout is compiler-emitted, not a callout written in rx text.

### COLD-14  CONFIRMED   severity: doc   effort: S
where: core.md core/diagnostics/warnings (1191-1218) vs core/labels/one-rule (304), core/diagnostics/warnings (1199)
what: (a) core/labels/one-rule: "A label no match can set draws a warning, not an error (core/diagnostics/warnings)" -
the warnings table has no row for it (`pcrec.label.unset` is "can be absent where it is read", a different trigger;
`pcrec.dead.branch` is about alternatives). (b) The statement says every warning "has one stable name", yet five rows
are nameless `(hide)`, `(arithmetic)`, `(nullable hit)`, `(consuming test)`, `(join)`, while the others carry
placeholder names; the reader cannot tell why. (c) The selector bullet names the unused-suppression warning
`warn.unused`; the table names it `pcrec.warn.unused`, and the bullet before says the compiler's names carry
`pcrec.`.
proposed fix: add the row (`pcrec.label.never`, a label no match can set); give the five rows placeholder names like
the rest; write `pcrec.warn.unused` in the bullet.

### COLD-15  CONFIRMED   severity: doc   effort: S
where: library.md lib/modifiers/month-numbered (159); core.md core/labels/export example (338)
what: Two printed examples are not mechanically buildable from their text: (a) the month_numbered body is written
with an ellipsis, `[mname = [/Jan(?:uary)?/, ..., /Dec(?:ember)?/]]`; the `.index` the example depends on (Jun = 6)
requires the elided order. (b) core/labels/export's example program is a bare binding,
`year := /(?<_v>\d{4})/ & (_v: >= 2000)`, which by core/operators/statements is not a program (no final
expression) - the WHOLE/SEARCHED/FIND-ALL answers belong to `year` used as the final expression.
proposed fix: (a) write the twelve members (one line) or say "the twelve English month names in calendar order,
each with its three-letter prefix"; (b) append `; year` (or "(`year`, year := ...)") as other examples do.

### COLD-16  CONFIRMED   severity: design   effort: M   (SIBLING OF A FAMILY)
where: core/filters/operand-context (512), core/holes/in-filter (975), core/values/functions clause 1 (686),
lib/builtin/enumerate (26), lib/assert/assert (472), core/modules/export (1135); core/model/places (159-176)
what: One rule is stated six times separately: "a position that judges a set as its whole world refuses an assertion
that looks outside it" - a filter operand, a hole inside a filter operand, a single-value function's operand,
`enumerate`'s argument ("a compile-time set position"), an assertion's argument ("a compile-time set position"),
`@export`'s names. The place table, which is meant to list every place with its kind, has rows for the filter
operand and the `label:` set but none for the compile-time SET positions (enumerate / assert / @export / import
names / a single-value function's operand), so the family has no home and its members can drift (they already
differ: functions say "enumerate's compile error", enumerate says "the edge-assertion error", assert says "the
edge-assertion error", operand-context says "any piece that might look outside" - which also covers lookarounds, while
the edge-assertion wording does not; enumerate leaves "an interior lookaround or a backreference: not stated").
GENERAL FORM: a place-table column "may look outside: no" and one row "a compile-time set position (the argument of
enumerate, an assertion, @export, import; a single-value function's operand)"; core/filters/operand-context states
the rule once for every place with "no" in that column. UNLOCK: the open interior-lookaround question for enumerate
is then answered by the same rule as for filter operands. Trigger: already met (six statements, two wordings).

### COLD-17  SUSPECTED   severity: maintenance   effort: S   (GENERAL FORM + UNLOCKS)
where: library.md lib/search/{contains, starts-with, ends-with, ends-with/lazy-gap, occurrences, hits}, lib/sets/anything, lib/sets/prefix-in
what: The "any text" gap is written in three spellings across sibling bodies: `(?s:.*)` (contains, startsWith,
endsWith, occurrences, prefix_in), `[\s\S]*` (hits, anything), `(?s:.)` per char (length's chars, padded). They are
equal today, but core/principles/rx-owns-flags + core/holes/flags make a hole's flags inherited for `s`; `(?s:...)`
pins it, `[\s\S]` is flag-proof. The library already provides `anything` "for any text ... no flag changes it".
GENERAL FORM: `contains(s) := anything SEQ s SEQ anything`, `startsWith(s) := s SEQ anything`, the lazy gap a
provided `anything_lazy` (or `anything` under `*?`), so the gap is defined once. UNLOCK: a future change to what
"any text" means (an encoding mode, bytes vs characters - lib/strings/left leaves it open) is made in one piece.
Trigger: the first gap whose spelling differs in meaning (none today; hence SUSPECTED).

### COLD-18  CONFIRMED   severity: doc   effort: S
where: core.md 1205 ("narrowing site"), 903 ("asked with the construction line"), 1246 ("the skip-past verb"),
637/1126 ("first/rest walk/binding"); library.md 57 ("the level the user asked for (automaton code only, by
default)"), 268 ("the captures level"), 547 ("the program's UCP setting"), 369 ("the encoding mode")
what: Terms used without a definition anywhere in the base files (grep counts: each appears once or twice and
nowhere defined). "Level" in particular is a whole concept (an engine/capability level the user selects, with a
default) that a new session meets only in passing (also core/patterns/literals 193 "no level beyond today's engine
choice"). "first/rest" points at a parked idea but is used in core as if known.
proposed fix: one defining clause each where first used, or a pointer tag (a parked or a core piece) on the line;
"level" deserves a core piece or a see: to wherever the capability levels are defined.

### COLD-19  CONFIRMED   severity: doc   effort: S
where: core.md core/modules/standard-library (1143); library.md header (8-10), lib/search/within (334),
lib/planned/standard (623, 629), lib/json (611), lib/records/file-literals (536)
what: The base files lean on "the worked examples" ("names the worked examples call", "the worked example names it",
"the draft's JSONL example", "Its use in the record") as if the reader had them; no base file holds or points at them
(no tag, no path). A new session cannot see the uses that justify `within`, `days`, `json.row`, `file_literals`.
Also one name drifts inside the same piece: lib/planned/standard calls `weekday_of(...)` (627) and then speaks of the
REGULAR TWIN "for `luhn`, `weekday` and `days_in`" (629); core 1070 renames `weekday` in an import example.
proposed fix: either quote the one-line use in each piece (most already do) and drop "the worked example(s)" /
"the draft's" / "the record" wording, or give the worked examples a home tag (parked or a core appendix) and cite it;
write `weekday_of` consistently.

### COLD-20  CONFIRMED   severity: doc   effort: S
where: core.md core/model/table/group-truth (146-152); library.md lib/counting/some (385)
what: The open question's candidates are not alternatives. The question: do `NOT some(c)` and `occurs.none(c)` agree
with `occurs.none(NOT c)`? Candidate (a) "`NOT some(c)` = `occurs.none(c)`"; candidate (b) "`occurs.none(NOT c)` is a
different question". Both can be true at once (and the text says (a) agrees on every run and (b) parts from (a) on a
pass lacking the label), so a reader cannot tell what the owner is being asked to choose. Meanwhile lib/counting/some
(ruled) states candidate (a) as settled fact: "`NOT some(c)` and `occurs.none(c)` are the same question".
proposed fix: phrase the open question as the actual choice (e.g. "on a pass lacking the label, does `occurs.none(NOT
c)` count the pass? (a) no - it differs from NOT some(c); (b) yes - ..."), and mark lib/counting/some's sentence as
the agreed half.

### COLD-21  CONFIRMED   severity: doc   effort: S
where: core.md core/operators/statements (1042-1043) vs library.md lib/builtin/eval (81-86)
what: `eval` is listed among "The BUILT-INS ... a closed list, reserved in CALL position": `import`, `enumerate`,
`pattern`, `param`, `file_text`, `records`, `eval`. Its library piece says it is an idea "that only a named module would
provide", `module: eval`, "only as the explicit module `eval` ... never by default". A built-in reserved name and a
member of a module reached only by import are two different statuses; also a closed reserved list containing an
under-construction idea is odd.
proposed fix: drop `eval` from the built-in list (it is `eval.eval(...)` / a module member) or say the reservation
holds the name for the module.

## PASS 2: against r59

(Opened only R/tree/docs/dev/reviews/2026-11-19-r59-preddoc3/readwhole.md, after pass 1 was written.)

My findings:
- COLD-1  RECURS (partial) READ-11 / PLACE-3: `@options` now in the effect list and `pattern`/`eval` have pieces,
  but the new sentence "Every provided name written as a call has its piece in the library, these included" is
  false for `@export`, `@warn.*`, `@options.strict`.
- COLD-2  NEW (`even()`, `search(...)`; the PLACE-8 G1 "called name without a piece" class, new members).
- COLD-3  RECURS READ-6 / PLACE-3 (`digit` bare, `(0: digit)` example) - named in r59, not fixed.
- COLD-4  RECURS PLACE-4 (9) (the recursion error row "no piece"; r59 proposed a core/operators/bindings/recursion sub-piece) - not fixed.
- COLD-5  NEW (errors index incomplete; PLACE-8 G4 "derived indexes" is the general fix r59 proposed).
- COLD-6  NEW (core/values/functions statement vs clause 1 vs enumerate).
- COLD-7  RECURS READ-13 (provenance words; the warnings `ground` column of slugs / "the accepted list" named in r59, still present; "the draft's" phrases still present; unpadded/json-quoted pieces are gone - that part fixed).
- COLD-8  RECURS (partial) READ-6 / PLACE-3 (`.label`): `.index`/`.label` now defined, but only for a part label over an ARRAY; capture's use on a non-array part label through a binding is still undefined.
- COLD-9  RECURS PLACE-3 (macro overloading by arity, rx.repeat's three bodies) - not fixed; `padded`'s two heads join it.
- COLD-10 NEW (two present-tense bodies for endsWith and for contains).
- COLD-11 NEW (how a `module: ?` name is reached; generalises READ-6's "state the example's import" for `digit`).
- COLD-12 NEW (two-valued table shows two meanings, claims three).
- COLD-13 NEW (callouts refused vs listed as capture readers).
- COLD-14 NEW (warnings table: missing "label no match can set" row; nameless rows; `warn.unused` vs `pcrec.warn.unused`). READ-10's trigger conflict is fixed.
- COLD-15 NEW (month_numbered body elided with `...`; READ-5's `join` defect is fixed; export example is a bare binding).
- COLD-16 NEW (SIBLING: the outward-assertion refusal stated in six places).
- COLD-17 NEW (GENERAL FORM: one gap; SUSPECTED).
- COLD-18 RECURS READ-6 ("the captures level") and PLACE-4 (11) ("a narrowing site" defined nowhere); new members: "the construction line", "level", "first/rest", "UCP setting", "encoding mode".
- COLD-19 NEW (the "worked examples" cited, never present; `weekday` vs `weekday_of`).
- COLD-20 NEW (group-truth's candidates are not alternatives; lib/counting/some states (a) as fact).
- COLD-21 NEW (`eval` both a reserved built-in and a module-only member).

r59 items I did NOT re-find (no re-check needed):
- READ-1 not re-found (core/values/comparisons now exists).
- READ-2 not re-found (core/filters/negation; `not` gone; NOT carve-out stated).
- READ-3 not re-found (`0` decided in core/conditions/match-so-far only).
- READ-4 not re-found (padded's counts are count holes).
- READ-5 not re-found as stated (array, `.index` defined); see COLD-15 for the ellipsis.
- READ-6 re-found in part (COLD-3, COLD-8, COLD-18); `some`/`count`/`pattern`/`eval`/computed label now have pieces.
- READ-7 not re-found (scope of `$` reads stated in core/values/reads).
- READ-8 not re-found (core/values/computed-labels).
- READ-9 not re-found (flags-in-filter is an open piece; other-positions sub-piece).
- READ-10 not re-found.
- READ-11 re-found in part (COLD-1, COLD-21).
- READ-12 not re-found (the TYPE bullet is gone).
- READ-13 re-found (COLD-7).
- READ-14 not re-found (statement now says "Outside a binding").
- READ-15 not re-found (core/values/tuples).
- READ-16 not re-found (both expansions now `(?|`).
- READ-17 not re-found as a finding: I noticed `:=` in examples from core/patterns/sequence on with no pointer to core/operators/bindings, and judged it readable (each example names its bindings); not rechecked by census.
- READ-18 not re-found in pass 1 (I did not measure size); fact for the coordinator: `wc -c` core.md 100,972 B (r59: 93,687), library.md 41,675 B (r59: 28,209), both further over L7's soft caps (64 KB / 24 KB).
- PLACE-1 replaced by the rule change (not checked).
- PLACE-2 not re-found (atomic is lib/control/atomic; the `occurrences` idiom points at the library).
- PLACE-3 re-found in part (COLD-3, COLD-8, COLD-9).
- PLACE-4 re-found in part ((9) = COLD-4, (11) = COLD-18/COLD-7); others not checked (details-side).
- PLACE-5 not re-found (I read consuming-test's "keyed on the form" and held it).
- PLACE-6 not re-found (core/modules/positional is now open; tuple-apart a parked pointer).
- PLACE-7, PLACE-8 not re-checked (parked.md out of my read; G1's lint would catch COLD-2/3/11, G4 would fix COLD-5/14).

## PROBED-AND-HELD

- Every printed example in the two base files re-derived by the core's own rules: 69 example lines in core.md, 34 in
  library.md (`grep -c "^WHOLE\|^A part label used twice" ...`). All answers held except where the program cannot be
  built (COLD-3 `digit`, COLD-8 `x.label`, COLD-15 ellipsis / bare binding, COLD-11 reachability).
- 51 of them reduce to a plain regex and were run with `python3 -I` `re` (cold/run.py; output: every WHOLE /
  SEARCHED / FIND-ALL matched the print, incl. enumerate's `(?:aa|aab|a|aba|abab|ab)`, when's mechanical
  `NOT peek(peek(..))` expansion, both endsWith bodies, rx.repeat's mechanical `(?:(?:\d)){2,2}|...`). Longest
  witness run: `id-blah ID-BLAH Id-blah` (23 chars). Label-dependent examples (outermost-view `3;, 3;;, 4;,`,
  pass-start-read `3;7;4; 9;1;` incl. the empty finds at 6 and 11, reads `3-3;-3; 7-7;`, number-domain, arithmetic
  negative result, strlen `abcdefghij-10`, count `7,7,7, 1,7,7,`, some, hits `aax`/`axa`, padded width form) derived by
  hand: all held.
- Library bodies built mechanically (substitute holes literally): padded (both), quoted, any_case candidate, length,
  peek, when, when-test, atomic, occurrences, hits, contains (both), startsWith, endsWith (both), anchored, anything,
  between, prefix_in, list_of, rx.digits, rx.repeat, enumerate: 23 bodies produce their own printed examples.
- Statement/body contradictions checked in every core section; only COLD-6, COLD-12, COLD-13, COLD-20, COLD-21 found.
- `defined:` lines: 53 library pieces, every one carries `defined:`; `?` only on open/under-construction pieces
  (checked by eye against status).
- Lint run on the copy: 4,844 checks, 0 failed (L10 skipped).

CRITIC COMPLETE
