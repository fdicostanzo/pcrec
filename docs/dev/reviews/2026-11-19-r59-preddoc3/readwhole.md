# Critic readwhole findings (round r59 preddoc3)

## Findings


## PASS 1 (READ-WHOLE, blind: core.md then library.md, no details/draft/record opened)

### READ-1  CONFIRMED   severity: design   effort: M
where: core.md (no piece) + library.md lib/sets/between; uses at core/principles/no-absence, core/conditions/form, core/filters/and example, core/holes/and-in-hole, core/operators/precedence level 3, core/values/number-domain; library length (`==3`), between (`>= lo & <= hi`)
what: The COMPARISON SETS `< <= > >= ==` (the language's most-used value form: `(h: >= 10, m: <30)`, `<100`, `!<5`) are defined NOWHERE as a piece. core says only "the comparisons" are in the number domain (line 568) and gives their precedence (line 918); library's `between` is "the comparison set `>= lo & <= hi`" and leans on them. A newcomer cannot learn what `<30` is (a set of canonical numerals? an rx? can it match, is it finite/infinite, can it stand in a pattern hole as in `${/\d+/ & <100}`?), nor what `==3` means (equality to a numeral? to a string?).
evidence: `grep -n comparison core.md library.md` -> only core 568, 912 and library 255; no `###` heading names a comparison. First use `<100` at core line 39 (a quote), first piece use core line 421.
proposed fix: a core piece `core/values/comparisons` (primitive: a comparison is a set over the number domain, `<n` = the canonical numerals below n, infinite for `>`/`>=` so it can filter but cannot be enumerated; `==n` the one-numeral set; tuples by dictionary order if that is ruled) placed in Values right after number-domain, and every early use gets `see:` or a `needs:` to it. Trigger: now (it is a primitive every condition uses).

### READ-2  CONFIRMED   severity: doc   effort: S
where: core/filters/kinds example (core.md 528) vs core/operators/bindings ("No alphabetic operators or statement keywords: a word is always a NAME", core.md 947) vs core/conditions/two-valued (`NOT c`) vs library lib/sets/anything (`anything & NOT X`) and lib/control/when body (`NOT peek(test)`)
what: Three spellings of negation appear and the rules contradict. (1) The kinds example writes `not /7\d*/ & not /8\d*/`; `not` is defined nowhere, and by the bindings rule a word is a NAME, so `not` is an undeclared name (a compile error by core/operators/statements). (2) `NOT` is itself an alphabetic operator, against "No alphabetic operators". (3) core defines `NOT c` only on a CONDITION (two-valued: "`NOT c` is legal on a condition") and `!B` as the complement on a pattern, but the library applies `NOT` to PATTERNS: `anything & NOT X` and the ruled `when` body `NOT peek(test)` (peek(test) is a lookahead pattern, not a condition); lib/control/peek says "`NOT peek(A)` is the negative peek (a reading, run)". A newcomer cannot tell whether `NOT P` on a pattern is a complement, a negative lookahead, or an error - which is exactly the open question lib/control/when-test/not asks for bare patterns, while the ruled `when` body already uses it on `peek(...)`.
evidence: core.md 416 "`NOT c` is legal on a condition"; 426 "`NOT c` is regex's negative lookahead around the test"; 947 "No alphabetic operators ... a word is always a NAME"; 528 `neither := not /7\d*/ & not /8\d*/`; library 112, 251.
proposed fix: kinds example -> `!/7\d*/ & !/8\d*/`; anything bullet -> `anything & !X`; core/conditions/two-valued (or a new core piece) states what `NOT` applies to (a condition, and a zero-width pattern such as a lookahead: the negative lookahead) so the ruled `when` body is legal by a stated rule; core/operators/bindings carves out `NOT` (a placeholder spelling: "no alphabetic operator except the placeholder `NOT`").

### READ-3  CONFIRMED   severity: design   effort: S
where: core/labels/numbers (core.md 381, 390) vs core/conditions/match-so-far (core.md 453, 459)
what: Contradictory definitions of `0`. numbers' STATEMENT: "`0` is always the entire match of the rx however it is composed"; its bullet: "Inside a part, `0` written in that part's own condition is that part's own match (inside a loop body, the pass's)". match-so-far: "In a condition standing as a sequence operand, `0` names the match so far ... Inside a loop the match so far starts at the rx's start, not the pass's (a reading)". So for `(/\d/ SEQ (0: S))+` a newcomer gets three answers: the entire match (numbers statement), the pass's match (numbers bullet: a loop body is a part), the text from the rx's start (match-so-far). "a part" is also not defined so as to decide whether a loop body is one.
evidence: the three quoted lines.
proposed fix: numbers' statement drops "always ... the entire match" and points at the one rule: "`0` names the match so far at the condition's point (core/conditions/match-so-far); written after a complete pattern that is its entire match"; settle (or open) loop body = part vs rx start in ONE place and delete the other bullet. Move numbers after match-so-far, or give numbers `see: core/conditions/match-so-far` for its definition of 0 (it has the see:, but the statement contradicts what it points at).

### READ-4  CONFIRMED   severity: answer   effort: S
where: library.md lib/modifiers/padded, body line 18
what: The ruled width body `padded(rx, n) := (rx & /(?s:.){n,}/) | (/0*${rx}/ & /(?s:.){n}/)` writes the parameter `n` inside rx text WITHOUT a hole. By core/patterns/literals an rx literal "is full PCRE and means exactly what PCRE means", and the only crossing from the expression language into rx text is `${...}` (core.md 201-202); PCRE reads `{n,}` and `{n}` with a non-digit inside as LITERAL text. As written, the body matches only texts ending in the characters `{n,}` / `{n}`, so the printed example (`padded(/(?:\d\d)+?/, 3)` SEARCHED `x0129` `0129`@1) cannot come from this body. Compare lib/sets/prefix-in, which writes the count correctly as `{${n}}`.
evidence: `grep -nE '[^$]\{[a-z][a-z_]*[,}]' core.md library.md` -> library.md:18 is the only body hit (core 307 is prose about `{n}`).
proposed fix: `padded(rx, n) := (rx & /(?s:.){${n},}/) | (/0*${rx}/ & /(?s:.){${n}}/)` (count holes); check the details entry and the draft carry the same fix.

### READ-5  CONFIRMED   severity: answer   effort: S
where: library.md lib/modifiers/month-numbered (line 90) vs lib/strings/join (line 290)
what: `months := join([mname = [/Jan(?:uary)?/, ..., /Dec(?:ember)?/]])` uses `join` to build an ALTERNATION of month names, but join is defined as "one value: the members of a finite array in their order, s between them; with no `sep`, nothing between" - a CONCATENATION (`[^${join(c)}]`, c := [x, y], is `[^xy]`). Read by its definition, `months` is the one text `JanFeb...Dec` (or a sequence of the twelve patterns), and `month_numbered(between(1, 6))` could never hold on `Jun`. Join is also defined on strings ("one value"); its members here are patterns. And `$mname.index`: `.index` is defined nowhere (core/arrays/enumerate mentions "which alternative matched (`.index`)" as a use only).
evidence: library 290 "`join(a, sep = s)` is one value: the members ... s between them"; 297 `[^${join(c)}]` is `a[^xy]`.
proposed fix: `months := [mname = [/Jan(?:uary)?/, ..., /Dec(?:ember)?/]]` (an array IS an alternation, core/arrays/lift); define `.index` in core (a field of a part label over an array: the 1-based position of the member that matched) or mark it `?`/under-construction with its home.

### READ-6  CONFIRMED   severity: doc   effort: M
where: names used bare in core.md and library.md with no piece and no import: `some` / `every` (core 153, 158, 191, 294), `count(c)` (library 81, 283), `digit` bare (core 877-882, 1164; library 379), `.index` (core 636, 665; library 90), `x.label` (library 400), `json.string` (library 67), `pattern`, `eval` built-ins (core 960), "the captures level" (library 177), "a blessed callout" (library 242), "the predicate opt-in" (core 213), "a computed label" (core 965 only)
what: A newcomer reading the two base files whole meets these as if defined. `some`/`every` carry ruled weight (labels-vs-captures: the array form is "compared with a single value only through some or every"; the open group-truth question is ABOUT `some`), yet neither file has a piece; parked has only `some(^h)` over a field reference. `count(c)` is the body helper of `length` and the "other form" of occurs, no piece. `digit` is used bare where only `rx.digit` is provided. Built-ins `pattern` and `eval` are reserved in call position with no definition anywhere. By core/operators/statements "an undeclared name that is not a label is a compile error", so several printed examples (bare-condition's `(0: digit)`, rx.repeat's `repeat(digit, n, n + 1)`) are compile errors as written.
evidence: `grep -n '\bsome\b' core.md library.md` (uses at 153/158/191/294, no heading); `grep -n 'count(' library.md` (81, 283, no piece); headings list (no `some`, `count`, `digit`, `pattern`, `eval`).
proposed fix: each gets a home: `some`/`every`/`count` -> a library piece each under lib/counting beside occurs (or core if primitive: they range over the pass table, which no core body walks, so likely primitive -> core, see PLACE pass); `digit` -> write `rx.digit` or state the example's `(=) := import("rx")`; `pattern`, `eval` -> a `?` piece each (the built-in list must not name things with no piece); `.index`, `.label` -> core/modules/map's "metadata" fields listed; "computed label" -> its own core piece (it is what `length`/`month_numbered` bodies rely on, READ-8).

### READ-7  CONFIRMED   severity: design   effort: M
where: core/values/reads (core.md 543), core/holes/labels bullet 1 (core.md 852-853) vs core/holes/value, core/values/reads statement, and the examples of core/values/one-type (563), core/values/number-domain (574), core/holes/value (836)
what: Two core rules make the core's own examples compile errors, read literally. (a) core/values/reads: "A read of a name the rx it is written in does not define is a compile error (a reading)" - but one-type's example `/(?<x>\d+)/ & ($x & <5)` writes `$x` in the right operand, an rx (a read IS an rx) that defines no x. (b) core/holes/labels: "A reference written INSIDE the inserted pattern resolves in its own namespace; a name it does not define there is a compile error" - but `${$y + 1}`, `${$y | "x"}` and `${strlen($y)}` are references written inside a hole to a y only the outer literal defines, and core/values/reads says "`$y` reads the label, everywhere, holes included". The distinction the writer evidently intends (a VALUE hole's expression vs an inserted PATTERN; a `$` read vs a `\k<>` backreference) is never stated, and core/holes/bare-condition/labels is open on exactly the neighbouring question for conditions. A newcomer cannot tell which `$y` uses are legal.
evidence: the quoted lines; examples at core.md 563, 574, 836, library 315.
proposed fix: state the scope rule once, in core/values/reads: "a `$` read resolves in the namespace at the point it is written: in a value hole, the surrounding rx's labels as they stand at the hole; the free-name error applies to rx TEXT (`\k<y>`, numbers) inside an inserted pattern". Re-word the reads bullet ("the rx it is written in" -> "the program at that point") and holes/labels bullet 1 ("a backreference or group number written inside the inserted pattern"). If that is a new reading, mark it so and tie it to the open bare-condition-labels question (same family, SIBLING below).

### READ-8  CONFIRMED   severity: design   effort: M
where: library.md lib/modifiers/length (`nchars := count(...)`, `(nchars: S)`), lib/modifiers/month-numbered (`mnum := $mname.index`, `(mnum: S)`) vs core/conditions/form ("An entry is `p: S`, p a label path, never an expression"; "Left of `:` names are labels") and core/operators/statements ("A binding that mentions a match label is match-dependent (a computed label)")
what: Two library bodies put a BINDING (a match-dependent expression) left of `:` in a condition. core allows only label paths there and defines "computed label" in a single parenthesis with no rule saying a computed label may stand where a label does, what its value is per path, or whether a condition entry may target it. A newcomer cannot verify these bodies are legal programs.
evidence: library 78, 81, 87, 90; core 411, 414, 965.
proposed fix: a core piece for the computed label (what it is, where it may be read: left of `:`, `$`; when it is evaluated; its value when an input label is unset), placed in Labels or Values, with `needs:` from the two library pieces; or, if that is not ruled, mark the two bodies `reading` with the dependency named and an open slug.

### READ-9  CONFIRMED   severity: doc   effort: S
where: core/holes intro (core.md 680) and core/holes/value last bullet (835) vs core/holes/flags (845) vs core/labels/labels-vs-captures (292)
what: The Holes section says "The pieces of this section are complete.", yet (a) core/holes/value ends "A read in a count, class or option position: the draft's reading (`predicates_draft.md`) until converted" - a base file pointing a newcomer at the frozen draft for the current rule, inside a section declared complete; (b) core/holes/flags carries an OPEN question in a bullet ("open, flags-in-filter (the draft's reading: yes)") with no `open flags-in-filter` piece anywhere (grep of all base files: no such status); (c) labels-vs-captures says "(spelling open)" for the carried-capture form, a third status-in-prose. Open questions are supposed to be findable by `--state open`; these two are not.
evidence: `grep -n 'open [a-z-]* 2026' core.md library.md parked.md` lists 9 open pieces, none flags-in-filter.
proposed fix: drop "complete" from the section intro (or make it true); split core/holes/value's last bullet into sub-pieces (count/class/option read) with their status (`?` or reading), stating the reading; make flags-in-filter an `open` sub-piece core/holes/flags/in-filter; the carried-capture spelling is already covered by core/spellings/placeholders, so drop "(spelling open)".

### READ-10  CONFIRMED   severity: doc   effort: S
where: core/labels/numbers ("A number in a condition draws the numbered-label warning", core.md 393) vs core/diagnostics/warnings row `pcrec.label.numbered` ("a condition or `$` reading a label by number on a pattern not written there (`0` exempt)", 1122)
what: Two different triggers for one warning: every number in a condition (numbers) vs only a number on a pattern not written at the condition (warnings), with `0` exempt only in the table. Under numbers' own rule a number is legal only on ONE written literal, so the table's trigger ("a pattern not written there") reads as either never firing or as covering bound literals (`p := /(\d)/; p & (1: ..)`), which numbers does not say is legal.
evidence: the two lines.
proposed fix: one trigger, stated in core/labels/numbers (the deciding piece), the warnings table row pointing at it; say whether a bound single literal counts as "one written literal".

### READ-11  CONFIRMED   severity: doc   effort: S
where: core/operators/statements (core.md 960-962) vs core/diagnostics/warnings (1111) and library lib/records/param, lib/records/file-text, lib/records/records
what: (a) The built-ins and effects are "a closed list": `import, enumerate, pattern, param, file_text, records, eval`; "the effects `@warn` and `@export` after `@` only" - but warnings uses a third effect `@options.strict(...)`, not in the closed list. (b) "Every other name is a library name" implies the built-ins are NOT library names, yet `param`, `file_text`, `records` are library pieces (`module: ?`), and `pattern`, `eval` have no piece in any file.
evidence: the quoted lines; library headings 325, 343, 350.
proposed fix: add `@options` to the effect list (or spell strictness as `@warn.error`, which the selector bullet already has); move the built-ins to core (they are primitive, PLACE pass) or drop them from the reserved list; give `pattern` and `eval` a `?` piece.

### READ-12  CONFIRMED   severity: doc   effort: S
where: core/modules/map (core.md 980: "Members of a TYPE travel with the type (`d.weekday` works...)") vs core/values/one-type (552: "ONE type for values, the rx") and core/operators/bindings (945: "Typed parameters are not in the first build")
what: map speaks of a value's TYPE carrying members while one-type rules there is one type. A newcomer cannot tell what "a type" is for `d` (a part label of a date pattern? a module-bound pattern?). The bullet is marked "a lean of the owner's, not ruled" inside a `ruled` piece.
evidence: the quoted lines.
proposed fix: re-word as "members of a pattern's module travel with a value bound to it" if that is the meaning, or move the bullet to a parked/open sub-piece (it is a lean, not a rule) and keep one-type's statement unqualified.

### READ-13  CONFIRMED   severity: maintenance   effort: S
where: library.md lib/modifiers/unpadded (33), lib/modifiers/json-quoted (64), lib/structural intro (397), lib/modifiers/quoted (45), length (82), month-numbered (91), between (261), occurs modes line (285), rx.repeat (376), occurrences (161); core.md core/diagnostics/errors (1074, 1093), core/diagnostics/under-construction (1098), core/holes/same-name (868), core/holes/class (742), core/diagnostics/warnings ground column (1114-1126)
what: History and provenance survive in the base files in words L6 does not list. Worst: two library PIECES exist only to say a name was removed ("`unpadded` is not a provided name: the owner cut it from the first spec"; json.quoted the same) - a withdrawn name is history/rejection, the format puts it in a details `rejected:` line (or parked), and a newcomer reading the library whole meets two non-names as pieces. Also: "(a new section: no section held them)", "the manager's list from the draft", "Four candidates whose only ground was ... are warnings", "told to the owner", "asked and ruled on", "the copy reading differs", "the body is the draft's" (x4), "a reading of the ruled premise, told". The warnings table's "ground" column cites question slugs and "the accepted list", which a base-only reader cannot resolve (no piece defines "the accepted list"; `polarity-rule`, `empty-search-error`, `plus-operands` are slugs, i.e. details-file vocabulary).
evidence: `grep -nE "first spec|cut it|the draft|told|asked and|new section|from the draft|candidates whose|differs\)|accepted list|polarity-rule|empty-search-error|plus-operands" core.md library.md` -> 25 lines (table in appendix A).
proposed fix: delete the unpadded and json.quoted pieces from the base (their `was:`-free tags retire into a details `rejected:` line on the nearest live piece: lib/modifiers/padded and a json module piece, or parked); replace "the body is the draft's" by the status word alone (`reading` already says it); drop the provenance parentheses; turn the warnings "ground" column into a "decided in" column naming the deciding PIECE (status shows ruled/reading). Extend L6's word list with `the draft`, `cut`, `told`, `first spec` (maintenance trigger: the next lint round).

### READ-14  SUSPECTED   severity: doc   effort: S
where: core/holes/labels/hole-export (core.md 859) vs core/labels/flow (316-325) and core/labels/export rule 3 (334)
what: The open question's statement says "Today they part: the hole does [re-export], the sequence part does not", but flow's statement and example show labels DO surface across the sequence operator (`A SEQ B` reads h at top level). The difference only exists OUTSIDE A BINDING (export rule 3: "the public labels written in its own literals and its public part labels"), and hole-export never says "outside a binding". A newcomer reading the statement alone concludes the hole and flow contradict each other.
evidence: core 318 "Across the sequence operator a name both parts surface is one label"; 859 statement.
proposed fix: statement -> "Outside a binding, does a hole re-export the inserted pattern's public labels where an unlabelled sequence part does not?" with `needs: core/labels/export` (rule 3 is the premise).

### READ-15  CONFIRMED   severity: doc   effort: S
where: core.md / library.md: tuples (core/conditions/form 411-412 `(h, m): R`, `(A, B)`; core/modules/positional 1052 `lo := (9, 0)`; lib/sets/between 260 "Its bounds may be tuples (dictionary order)") vs core/operators/bindings 948 "A RECORD (the parentheses of a call or a condition) is never a value"
what: TUPLE is a value form with no piece: what `(9, 0)` is, how a tuple set `(A, B)` is the product, what dictionary order means for a comparison. Its spelling (parentheses with commas) is the record's spelling, which bindings says is "never a value"; `lo := (9, 0)` then reads as binding a record. A newcomer cannot tell a tuple from a record.
evidence: quoted lines; no heading contains "tuple" except parked/ideas/tuple-apart.
proposed fix: a core piece core/values/tuples (or in Arrays): the tuple value, the tuple set as product, its order, how it parses apart from a record; bindings' record bullet points at it.

### READ-16  CONFIRMED   severity: doc   effort: S
where: core/holes/count example (core.md 727) vs lib/rx/repeat example (library 384)
what: The SAME program (`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4]) is shown expanding to `(?|\d{2,2}|\d{2,4}|\d{4,4})` in core and `(?:\d{2,2}|\d{2,4}|\d{4,4})` in the library. `(?|` (branch reset) and `(?:` differ for any copy holding a capture (group numbering), which is what a newcomer would take the choice to mean.
evidence: the two example lines.
proposed fix: one expansion in both (count-hole copies are an alternation of copies; say which group kind the copies sit in, in core/holes/count, since numbering through copies is a number-rule question).

### READ-17  CONFIRMED   severity: doc   effort: M
where: core.md read order (whole file); predicates/CLAUDE.md "a file uses only what is before it, except `see:` pointers"
what: core.md does NOT read front to back. (1) The first non-principle section, The model, uses `&`, conditions `(a: "1")`, part labels, complements, holes, bindings and library names (`occurrences`, `some`, `occurs`) with `needs:` only on core/model/match; core/model/places is a table of 15 places of which 13 are defined later. (2) `:=` bindings appear in examples from core/patterns/sequence (line 233) on; the binding form is defined at core/operators/bindings (line 934), 700 lines later, never pointed at. (3) Holes `${}` are used from line 469 (pass-start-read's example binds a CONDITION and inserts it in a hole - legal only by core/holes/bare-condition, line 873, no pointer). (4) 56 tag references in piece bodies/needs point FORWARD without a `see:`; the ones where the piece's meaning depends on the later piece (not an index row): model/table -> patterns/atomic; model/table/group-truth -> conditions/pass-start-read; conditions/form -> conditions/two-valued; conditions/in-sequence -> conditions/pass-start-read; values/reads -> values/one-type; values/one-type -> arrays/lift; arrays/enumerate -> arrays/class-order, class-index; labels/export -> labels/backreferences; holes/flags -> holes/same-name; lib/control/when -> lib/control/when-test. (5) core/labels/one-rule's "Repeated means set in a loop by its operand regex" defines a term whose user (`occurs`, "a repeated label") is in the library. The lint's L5 checks `needs:` order only, so none of this is caught.
evidence: census script `readwhole/fwd.py` (appendix B; 126 core + 47 library pieces; 56 forward refs listed); first-use grep (appendix B).
proposed fix (general form, with triggers): (a) NOW: a short notation piece at the head of core (after principles), `core/model/notation`, `reading`, listing the surface every example uses - a literal `/../`, `name := X`, `P & Q`, a condition `(l: S)`, a comparison set, `${X}`, `$x` - each with `see:` to its defining piece; examples may then use those forms freely. (b) NOW: reorder so that the forms the model section relies on come first - Patterns, Labels, Conditions, Filters, then The model (table, places, outermost-view) as the synthesis; places table moves to the END of core (it is an index of every place) or becomes `see:`-declared. (c) NOW: every body forward reference that the meaning depends on becomes a `see:` (11 above), or the pieces swap order (form/two-valued; reads/one-type/lift: put one-type first in Values). (d) LINT TRIGGER: when (a)-(c) land, L5 grows a check "a bare tag in a body that names a LATER piece must also be on the piece's `see:` line" (index pieces whose body is a table exempt by a `modes: n/a (the table ...)` line), so the CLAUDE.md claim becomes checked.

### READ-18  CONFIRMED   severity: maintenance   effort: L
where: core.md 93,687 bytes vs L7's soft cap 64 KB (library.md 28,209 vs 24 KB)
what: Over cap by 46%. Measured composition (method: appendix B script 2): Holes 17.7 KB (the biggest section), Labels 10.3 KB, model 7.3, principles 7.1, values 6.8, patterns 6.8, modules 6.4, diagnostics 6.3; the five INDEX pieces (errors 2.4 KB, warnings 2.6, spellings 2.7, places 2.0, insert 0.8) = 10.5 KB, all restating rows whose meaning is in other pieces; the 9 open pieces 5.9 KB; example lines 10.0 KB (required); 63 inline "(a reading)" marks.
proposed fix, the GENERAL FORM: the base file is ONE file per SECTION, the tag's path already naming it. `core/holes/class` lives in `core/holes.md` (and `core/holes_details.md`); the read order is the section order in a short `core.md` index (one line per section: tag, one-sentence scope, needs). This needs no tag change (the path already is file/section/piece), keeps every section well under 20 KB, and lets a session read only the sections a question touches. Steps and triggers: (1) NOW, cheap, no format change: move the principles' "His words in full" quotes and long candidate runs of open pieces to details (about -4 KB); delete the two non-name library pieces (READ-13). (2) NOW: generate, not hand-keep, the four derived indexes (errors, warnings' "fires on" column, spellings, insert): each deciding piece carries one field line (`fires: error <name>` / `spells: <thing>`), and `scripts/entry --index errors|warnings|spellings` prints the table; the base keeps the hub statement only (-8 KB, and kills the stale-index class: READ-10, READ-11, PLACE-6). (3) TRIGGER core.md still > 64 KB after (1)-(2), or any one section > 16 KB: the per-section split above (the lint's file/section rule changes from "path equals file" to "path's first two words equal file"; L3/L5 keep working on the concatenation in index order). (4) TRIGGER: a second hub family like zero-values (one table split into status sub-pieces): allow a table piece with a status column, so a split by status costs one row, not one piece.

## PASS 2 (PLACEMENT; details files read, record grepped)

Rule applied: doc_format.md line 29 "CORE HOLDS PRIMITIVES ONLY: a piece whose definition is a body in the core language is a LIBRARY piece", line 25 (core holds "every provided name that is primitive"), and the owner (record 5265, "2026-11-19 OWNER, after reading the pilot documents (doc-shape)"): "i recommend that core document macros be defined in the library unless they are primitive". On comparisons the record (line 35) has his "the < types must be primitive because the generator is primitive".

### PLACE-1  CONFIRMED   severity: design   effort: M
where: (ii) library pieces that say of themselves they are PRIMITIVE: lib/counting/occurs ("Primitive: a count over the passes of a loop; no body in the core language writes it"), lib/strings/join ("Primitive ... the core language has no body that walks an array"), lib/strings/left ("Primitive: a string function; the core language has no slicing"), lib/strings/strlen ("Primitive"), lib/records/records, lib/records/param, lib/records/file-text ("Primitive"), lib/structural/each ("Primitive: compile-time structural tools"), lib/modifiers/any-case (body line: "Today (ruled): `any_case` is a PRIMITIVE for now"); also primitive by content: lib/strings/upper-start (a string function "of the `left` kind"), lib/search/within (needs "a computed label or a blessed callout").
what: 11 library pieces are not bodies in the core language; by the format and the owner's words they are CORE pieces (primitive provided names). Three of them (`records`, `param`, `file_text`) are also on core's closed built-in list (core/operators/statements), which says "Every other name is a library name" - i.e. the core already calls them not-library.
evidence: `grep -n 'Primitive' library.md` -> lines 279, 293, 303, 313, 329, 346, 353, 411 (self-declared) + any-case line 55 ("a PRIMITIVE for now").
proposed fix: a core section `core/primitives` (or the existing Values/Arrays sections) homing each as a core piece with `was: lib/... (2026-11-19, primitive: core holds primitives)`: occurs (+ the missing `count`, `some`, `every`, PLACE-3) under a core "pass questions" piece beside core/model/table; `join`, `left`, `strlen`, `upperStart` under core/values/functions (which already states their rule); `records`, `param`, `file_text`, `each` beside `enumerate` (compile-time built-ins); `any_case` stays in library ONLY under candidate (a) of its own open question - while open, it is a core primitive with the body as the library candidate. Pending the owner's any-case-body answer, the piece's home is decided by that answer (say so in the piece).

### PLACE-2  CONFIRMED   severity: design   effort: M
where: (i) core pieces whose definition is (or the core itself says is) a body in the core language
what: (a) core/patterns/atomic: the NAME `atomic(...)` is the body `atomic(X) := /(?>${X})/` (a PCRE atomic group around a pattern hole); the primitive is PCRE's atomic group with a condition inside it (the core rule), the provided name belongs in the library beside peek (`lib/control/atomic`), as peek is "a lookahead around a pattern hole". (b) core/model/modes's bullet "A check of the whole text is written ... `J & C & occurrences(M)`" is a library idiom, not a primitive: belongs to lib/search/occurrences (or hits). (c) core/holes/negated-class defines `join` ("a function from an array to one string, its members in order") - the definition of a provided name inside a core piece, duplicating lib/strings/join. (d) core/holes/pattern bullet "`anchored` in a hole has no error of its own" states a fact about a library macro, duplicated in lib/search/anchored. (e) OPERATORS defined by bodies: core itself says "A sequence and a hole in a pattern position are one reading" (`A SEQ B` = `/${A}${B}/`), a postfix quantifier is "the regex quantifier ... on the operand as a whole" (`X+` = `/(?:${X})+/`), and `NOT c` "is regex's negative lookahead around the test" (`/(?!${c})/`). These are syntax, not names, so the owner's macro rule does not move them; but the pieces should STATE the body (the operator is sugar for it), which makes the hole the one composition primitive and settles what `NOT` means on a zero-width pattern (READ-2) by the same body.
evidence: core.md 229, 249, 426, 704, 757, 136-138, 267.
proposed fix: (a) new lib/control/atomic (body + `see:` from core/patterns/atomic, which keeps the condition rule); (b) move the bullet to lib/search/occurrences, core keeps "a check of the whole text is a WHOLE match" with `see:`; (c) negated-class keeps only `see: lib/strings/join` (or the core piece of PLACE-1); (d) drop the core bullet, keep `see: lib/search/anchored`; (e) each operator piece gains one line "it is the body `...`" (reading where not ruled).

### PLACE-3  CONFIRMED   severity: design   effort: M
where: (iii) provided names the core (and library) use that have NEITHER a core nor a library piece
what: `some`, `every` (core 153, 158, 191, 294; the record 2026-11-13 "some() any() all() as primitives? ... YES as the ONE spelling"), `count(c)` (library 81, 283), the comparisons `< <= > >= ==` (READ-1; record line 35: the generator is primitive), `.index` (core 636, 665; library 90), `.label` (library 400), `digit` bare (core 877-882, library 379), `not` (core 528), `pattern`, `eval` (built-ins, core 960), `@options` (core 1111), `json.string` (library 67), tuples (READ-15), the computed label (READ-8), macro overloading by arity (lib/rx/repeat's three bodies `repeat(x, n)`, `repeat(x, min, max)`, `repeat(x, min)`: core/operators/bindings defines one head per name, with required positional and optional keyword parameters; three bodies for one name is a mechanism core never states).
evidence: heading census (appendix C): no `###` heading in core.md, library.md or parked.md names any of these.
proposed fix: primitives (comparisons, `some`/`every`/`count`, `.index`/`.label` metadata fields, tuples, computed labels, `pattern`, `eval`) get core pieces (status `?`/reading where nothing is ruled); `digit`/`not` are fixed in the examples (READ-2, READ-6); `@options` joins the effect list or is replaced; overloading: either rx.repeat is rewritten as ONE head (`repeat(x, min = 0, max = "")` with "no maximum" spelled by a value) or core/operators/bindings states arity overloading (then it is a core mechanism the library relies on, flagged `reading`).

### PLACE-4  CONFIRMED   severity: doc   effort: S
where: (iii) rules and slugs homed on pieces that do not decide them
what: (1) core/spellings/placeholders: "the ARRAY FORM of a read (his `@x`), its index `h[k]` and the pass index" -> core/labels/one-rule, and "the EVERY-PASS shorthand" -> core/labels/one-rule; one-rule says neither; the array form is decided in core/labels/labels-vs-captures (and core/values/reads), "every pass" in labels-vs-captures + core/conditions/in-sequence. (2) slug `array-slot` ("only what was set", record 2026-11-17) sits on core/labels/one-rule, but the rule it decided ("a reset contributes nothing") is stated in labels-vs-captures. (3) slug `filter-captures` sits on core/filters/kinds, but its details say it is "closed by export-rule: visibility goes by export" and the rule is stated in core/labels/export. (4) slug `hit-list` sits on core/model/table; its details say "UNTESTED here (lib/search/hits)": decided by lib/search/hits. (5) slug `rx-module` sits on core/patterns/sequence while parked/ideas/rx-module and the lib/rx pieces carry the note. (6) slug `some-own` sits on lib/search/hits (there is no `some` piece). (7) the `other-holes` ruling (record "2026-11-19 OWNER RULING — other-holes") decides core/holes/class, core/holes/range-end and core/holes/option (all three cite it in `rulings:`), but the slug is listed only on class; range-end and option have empty `slugs:` - `scripts/entry other-holes` finds one of three deciding pieces. L9 has the `shared:` line for exactly this. (8) core/diagnostics/errors homes the current compile error "`${@y}`, not defined" on parked/ideas/array-in-hole; the deciding piece is core/holes/value ("written today it is a compile error"). (9) core/diagnostics/errors row "a recursion through a parameterised definition other than one integer literal parameter strictly decreasing to a literal base case | (a reading; no piece)": a rule with no home; its decider is core/operators/bindings (macros expand at compile time, per use). (10) core/modules/map: "Only what `.` reaches is reachable from outside: the public names (core/labels/export decides)" vs core/modules/export: "`@export` selects among them" - two deciders for a module member's visibility, and labels/export decides LABELS, not binding names. (11) core/diagnostics/warnings rows `pcrec.dead.branch`, `pcrec.label.unset`, `pcrec.default.unused`, `pcrec.label.ambiguous`, `pcrec.anchor.whole`, `pcrec.warn.unused` have ground "the accepted list" and no deciding piece ("a narrowing site" is defined nowhere).
evidence: slugs census (appendix C, awk over `slugs:` lines); details lines core_details 462/466 (array-slot), 499/726 (filter-captures), 301 (hit-list), library_details 246 (some-own); range-end/option rulings items cite "2026-11-19 OWNER RULING — other-holes".
proposed fix: (1) repoint to core/labels/labels-vs-captures, core/conditions/in-sequence; (2)-(4) move the slugs to the deciding pieces; (5) rx-module to parked/ideas/rx-module (or `shared:`); (6) to the new `some` piece; (7) a `shared: other-holes` head line or list the slug on all three; (8) row -> core/holes/value; (9) a sub-piece core/operators/bindings/recursion (reading); (10) one decider: modules/export decides members (`_` prefix as the default selector if that is the reading), map points at it; (11) each row names its deciding piece or carries `?` status in a sub-piece.

### PLACE-5  CONFIRMED   severity: design   effort: S
where: core/diagnostics/consuming-test, core/diagnostics/nullable-hit vs parked/ideas/macro-warning and core/principles/structural-warnings
what: Both are COMPILER warnings about the ARGUMENTS of LIBRARY macros (`when`'s test; `occurrences`/`hits`'s argument). consuming-test says itself "keyed on the form ..., which no macro body can see". A compiler that warns on `when`'s first argument knows the library name `when` - a special case for one library macro - while "a warning a macro raises about its own arguments" is PARKED (parked/ideas/macro-warning). As homed, core depends on either a special case (against "nothing in it is particular to peek", and the general-mechanisms rule) or on a parked mechanism; a newcomer cannot tell which.
evidence: core.md 1137-1146; parked.md 81-86.
proposed fix: state the mechanism in core: a library body may mark a parameter (`test: consuming-warned`, a placeholder) and the compiler's structural check reads the mark - then the two warnings are library-defined (structural-warnings: "structural or definable by a library option") and live with `when`/`occurrences`; or say plainly "a reading: the compiler knows these two names" and open it. Trigger for the general form: parked macro-warning's own trigger ("a second library-macro diagnostic") is ALREADY met by these two.

### PLACE-6  CONFIRMED   severity: design   effort: S
where: core/modules/positional (ruled 2026-11-16) vs parked/ideas/tuple-apart (parked)
what: CROSS-FILE CONTRADICTION. core rules "A positional list on the left of a binding takes a TUPLE apart: after `lo := (9, 0)`, `(a, b) := lo` binds `a` and `b`" (details: record "2026-11-16 OWNER CONFIRMATION — a tuple on the left of a binding takes it apart", his "Yes"), and the same idea is in parked.md as "Taking one tuple apart in a binding ... modes: n/a (parked: not in the language)" with trigger "item 1 taken up, or an example that needs one part of a tuple value". A session reading the base files whole learns both that it is in the language and that it is not. core/modules/positional even points at it (`see: parked/ideas/tuple-apart`).
evidence: core.md 1051-1059; parked.md 32-36; core_details positional rulings; parked_details tuple-apart history (the ideas-file item 4, "STATUS: OPEN ... the manager's note, 2026-11-16; not an owner ruling").
proposed fix: retire parked/ideas/tuple-apart (its text into core/modules/positional's details `history:`, `was:` line) or narrow it to what is still not in the language (taking apart a SET of tuples, already "NOT STATED" in the core piece), renamed accordingly.

### PLACE-7  CONFIRMED   severity: maintenance   effort: S
where: SIBLING-OF-A-FAMILY, pieces of one family split across files (each line: the family; its pieces; the defect)
what:
 1. LIMITED: lib/modifiers/limited (under-construction) + parked/ideas/limited (parked) - one name in two files with two statuses; a provided-but-undefined name and a parked idea at once.
 2. ATOMIC: core/patterns/atomic (ruled) + parked/ideas/atomic ("Atomic: not backtracked into once matched, and its spelling") + the `atomic(...)` name with no library piece (PLACE-2a).
 3. OPTIONS: core/diagnostics/warnings uses `@options.strict(...)` as live; parked/ideas/capability-optins parks `@options(...)`; core/operators/statements' closed effect list omits it (READ-11).
 4. RX MODULE: parked/ideas/rx-module says it was "taken up as core/patterns/sequence and lib/rx" - a parked piece for an adopted idea.
 5. NEGATION: `NOT` (core/conditions/two-valued), `!` (core/filters/complement), `NOT peek` (lib/control/peek, lib/control/when), the open not-test (lib/control/when-test/not), `not` (core/filters/kinds example) - five homes, no single rule (READ-2).
 6. NAME RESOLUTION ("namespace at reference"): core/labels/export, core/labels/backreferences, core/values/reads, core/holes/labels, core/holes/same-name, and three OPEN pieces (caller-ambiguous, hole-export, bare-condition-labels) - one principle, eight pieces, two contradictory sentences (READ-7).
 7. ZERO (`0`): core/labels/numbers, core/conditions/match-so-far, core/holes/bare-condition, core/filters/and - contradictory (READ-3).
 8. PASS QUESTIONS: array form / `h[k]` (labels-vs-captures), `some`/`every` (no piece), `occurs.*` (library, primitive), `count` (no piece), outermost-view, group-truth (open) - the family's core is missing (PLACE-3).
 9. HIT LIST: core/model/modes (the whole-text idiom), core/model/places row, lib/search/{occurrences, hits, contains/by-occurrences}, lib/counting/occurs, core/diagnostics/nullable-hit.
 10. IMAGE vs PREIMAGE string functions: core/values/functions + lib/strings/{left, strlen, upper-start, join} + lib/sets/prefix-in + lib/modifiers/length: one distinction (image vs filter), three library sections.
 11. NON-NAMES: lib/modifiers/unpadded, lib/modifiers/json-quoted, lib/rx/optional-loop - "not a provided name" pieces in the library (READ-13).
evidence: headings census (appendix C).
proposed fix: one home per family: 1 keep the library piece, retire the parked one into its details (or vice versa, by status: under-construction means "a direction acknowledged" = in the language); 2 core rule + library name + parked keeps only the verbs/`A :: B`; 3 decide live or parked; 4 retire; 5, 6, 7 one hub piece each with the cases as rows; 8 a core hub "questions over the pass table"; 9 a library section intro naming the family; 10 one section `lib/strings` with image and preimage subsections; 11 move to details `rejected:`.

### PLACE-8  SUSPECTED   severity: design   effort: M
where: GENERAL FORM + UNLOCKS (with triggers)
what / proposed fix:
 G1. A DECLARED KERNEL: one core hub piece listing every primitive (rx literal, hole, `&`, condition, complement, comparison generator, enumerate, pass questions, string image functions, compile-time file/records/param, import/export, metadata fields) - each a core piece. RULE: every library body uses only kernel names and EARLIER library names. UNLOCK: a lint check (L13) "every called name in a library body or a core example has a piece or is bound in the example" - it would have caught READ-2 (`not`), READ-6 (`some`, `count`, `digit`, `.index`, `.label`), READ-4 (a parameter in rx text outside a hole: a name inside `/../` braces). TRIGGER: now (six undefined names found by hand).
 G2. OPERATORS AS BODIES: sequence, quantifiers, `NOT`, atomic stated as bodies over the hole. UNLOCK: the hole is the single composition primitive; `NOT P` on any zero-width P has its meaning by the body (`/(?!${P})/`), so not-test's candidate (b) costs no rule while (a) needs one - a fact to put in front of the owner with that question. TRIGGER: the not-test ruling or the spellings review.
 G3. ONE RESOLUTION TABLE: name resolution as one table, reference kind (`$x`, `x:`, `\k<x>`, a number, `x.h`) x place (program, `&` operand, sequence part, pattern hole, value hole, bare condition in a hole, binding outside, caller) -> the namespace read. UNLOCK: caller-ambiguous, hole-export and bare-condition-labels become three empty cells of one table, each asked as a cell; READ-7's contradiction cannot recur. TRIGGER: the next ruling on any of the three open pieces.
 G4. DERIVED INDEXES generated from per-piece fields (errors, warnings, spellings, insert, places). UNLOCK: stale index rows impossible (READ-10, READ-11, PLACE-4 (1), (8), (11) are all index rows that drifted). TRIGGER: now (core size) - see READ-18.
 G5. HOLE COMBINATION as one rule: "several values in a hole are an alternation at the smallest enclosing construct where an alternation is legal (pattern: the group; class: the class; count: the quantified atom?) - else an error (name, option)". The owner ruled count copies the WHOLE literal, so G5 is not the count rule; but it predicts class, negated class, range end, pattern and zero values with one sentence. UNLOCK: a future position (a Unicode property name hole, a callout argument) gets its meaning by the rule. TRIGGER: the first new hole position proposed; positions-own-rules stays the owner's principle, so this is a reading offered to him, not a rewrite.

## APPENDIX A: history-like phrases in base files (READ-13)
Method: grep -nE "first spec|cut it|the draft|told|asked and|used to|no longer|new section|from the draft|candidates whose|differs\)|accepted list|polarity-rule|empty-search-error|plus-operands|his lean|owner's lean|until converted" core.md library.md
```
core.md:10:slug ruling; its details name the record's class), `reading` (the draft's or the manager's, not ruled), `open <slug>` (a
core.md:102:A regex in his example or ruling is run before it is recorded; a mismatch with his words is told the same turn.
core.md:392:- A number on a group whose name is shared inside one literal is refused too (a reading).
core.md:742:  the pattern (a reading, run: the copy reading differs).
core.md:835:- A read in a count, class or option position: the draft's reading (`predicates_draft.md`) until converted.
core.md:845:- Whether the two sides of an `&` written inside a hole inherit: open, flags-in-filter (the draft's reading: yes).
core.md:868:- The outer literal's `\k<h>` reads the outer group (asked and ruled on `\k<h>`).
core.md:1036:- That the set exists and holds `peek`: his lean. Library pieces in it carry `default: yes`.
core.md:1074:- Each error below is ruled or read in its own piece; this piece is the index (the manager's list from the draft).
core.md:1093:- Four candidates whose only ground was "probably a mistake" are warnings: an empty search, a test that can never
core.md:1098:The under-construction error keeps its own class, worded as under construction (the manager's call, told to the owner).
core.md:1114:| `pcrec.test.never`, `pcrec.test.always` | a test that can never pass; one that can never fail; at any polarity | polarity-rul
core.md:1115:| `pcrec.empty.search` | a searched final pattern that can report an empty find | empty-search-error |
core.md:1116:| `pcrec.dead.branch` | an alternative of a narrowing site that can never match | the accepted list |
core.md:1117:| `pcrec.label.unset` | a label a condition names can be absent where it is read, with no default | the accepted list |
core.md:1118:| `pcrec.default.unused` | a default that can never be used | the accepted list |
core.md:1119:| `pcrec.label.ambiguous` | an ambiguous label in the author's own pattern text | the accepted list |
core.md:1120:| `pcrec.anchor.whole` | an explicit anchor that provably sits at the edge of a filter role's stretch | the accepted list |
core.md:1121:| `pcrec.warn.unused` | an `@warn.off` that suppresses nothing | the accepted list |
core.md:1126:| (arithmetic) | an arithmetic result known at compile time to be nothing, whatever the cause; a member list only when every me
library.md:6:`docs/design/predicates_draft.md`, which stays its source. Worked-example bindings of the draft (`isodate`, `weekday_of`,
library.md:33:`unpadded` is not a provided name: the owner cut it from the first spec.
library.md:45:- The name is ruled (a filter modifier named for what it reads); the body is the draft's.
library.md:64:`json.quoted` is not a provided name: the owner cut it from the first spec.
library.md:82:- The name is ruled; the body is the draft's. The label `ch` is visible in the result.
library.md:91:- The name is ruled; the body is the draft's. The label `mname` is visible in the result.
library.md:108:- `default: yes`: in the default-imported set, so written bare, not `module.peek` (the owner's lean).
library.md:161:- A nullable argument draws a warning. Its hits (a reading of the ruled premise, told): the plain search's hits up
library.md:261:- `between` as `>= lo & <= hi` is the draft's body; "inclusive" and the two-digit example are the owner's.
library.md:285:modes: n/a (a count over a loop's pass table; no example of the draft is printed in the three modes)
library.md:376:  /(?:${x}){${min},${max}}/`; `repeat(x, min) := /(?:${x}){${min},}/` (how a body writes "no maximum": the draft's
library.md:397:The compile-time tools over spelled arrays and the macro that names a capture (a new section: no section held them).
```

## APPENDIX B: forward-reference census (READ-17)
Method: timeout 60 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc3/readwhole/fwd.py (parses ### headings, needs:/see: lines and bare tags in bodies; a FORWARD ref = a tag in body or needs: of a piece that is later in core-then-library order and not on its see: line; sub-pieces of the piece itself excluded). Population: 126 core + 47 library pieces (incl. section headings as pieces).
```
pieces core 126 lib 47
FORWARD (undeclared by see:): 56
  core/model/modes core/model/places body
  core/model/table core/patterns/atomic body
  core/model/table/group-truth core/conditions/pass-start-read body
  core/model/places core/conditions/form body
  core/model/places core/conditions/in-sequence body
  core/model/places core/filters/and body
  core/model/places core/filters/complement body
  core/model/places core/holes/pattern body
  core/model/places core/labels/export body
  core/model/places core/labels/one-rule body
  core/model/places core/labels/paths body
  core/model/places core/patterns/atomic body
  core/model/places core/patterns/lookaround body
  core/model/places core/patterns/sequence body
  core/model/places lib/control/when-test body
  core/model/places lib/records/records body
  core/model/places lib/search/occurrences body
  core/labels/export core/labels/backreferences body
  core/conditions/form core/conditions/two-valued body
  core/conditions/in-sequence core/conditions/pass-start-read body
  core/values/reads core/spellings/placeholders body
  core/values/reads core/values/one-type body
  core/values/one-type core/arrays/lift body
  core/values/functions lib/sets/prefix-in body
  core/arrays/enumerate core/arrays/class-index body
  core/arrays/enumerate core/arrays/class-order body
  core/arrays/class-order core/arrays/class-positions body
  core/holes/insert core/holes/class body
  core/holes/insert core/holes/count body
  core/holes/insert core/holes/name body
  core/holes/insert core/holes/negated-class body
  core/holes/insert core/holes/no-hole body
  core/holes/insert core/holes/option body
  core/holes/insert core/holes/pattern body
  core/holes/insert core/holes/range-end body
  core/holes/insert core/holes/value body
  core/holes/range-end core/holes/zero-values/class body
  core/holes/flags core/holes/same-name body
  core/modules core/spellings/placeholders body
  core/modules/default-set/members lib/control/peek body
  core/diagnostics/errors core/diagnostics/under-construction body
  core/diagnostics/errors core/diagnostics/warnings body
  core/diagnostics/warnings core/diagnostics/consuming-test body
  core/diagnostics/warnings core/diagnostics/dollar-form body
  core/diagnostics/warnings core/diagnostics/nullable-hit body
  core/spellings/placeholders core/spellings/condition-parentheses body
  core/spellings/placeholders lib/control/peek body
  core/spellings/placeholders lib/control/when body
  core/spellings/placeholders lib/modifiers/padded body
  core/spellings/placeholders lib/rx/classes body
  core/spellings/placeholders lib/rx/repeat body
  core/spellings/placeholders lib/search/hits body
  core/spellings/placeholders lib/sets/anything body
  core/spellings/placeholders lib/strings/join body
  lib/control/when lib/control/when-test body
  lib/sets/prefix-in lib/strings/left body
UNDEFINED tag refs: []
```
First-use lines of constructs (for READ-17): `:=` first in an example at core.md 233 (core/patterns/sequence), defined 934; `${}` first in an example 469, holes section 677; condition in a hole 469, defined 873; `not /` 528 (never defined); `some(` 153 (never defined); `.index` 636 (never defined).

## APPENDIX C: placement censuses (PASS 2)
Slugs per tag: awk '/^## /{t=$2} /^slugs:/{print t": "substr($0,8)}' core_details.md library_details.md (126+47 entries; 'shared:' head lines: grep -n '^shared:' *_details.md -> core_details.md:10 shared: when-peek only).
Self-declared primitives in library: grep -n 'Primitive' library.md -> 279 293 303 313 329 346 353 411 (+ any_case line 55).
Undefined-name check: for each of some, every, count, comparison, index, label, digit, not, pattern, eval, options, tuple, computed: grep -n '^### .*NAME' core.md library.md parked.md -> no heading (parked has only 'count / some over a field reference' and 'Taking one tuple apart').
Size by section: awk over '## ' headings of core.md (READ-18 figures); piece categories by a python pass over '### ' heads (examples 9,952 B; open pieces 5,919 B; principles 4,585 B in pieces + section intro; index pieces errors 2,405, warnings 2,631, spellings 2,692, places 2,018, insert 830).

## PROBED-AND-HELD

- PASS 1 population: core.md read whole (1,179 lines, 113 pieces incl. 22 principles) then library.md whole (415 lines, 47 pieces), blind (no details, draft or record opened during the pass; doc_format.md read only after pass 1's findings READ-1..6 were written).
- Examples hand-checked against their stated expansions (no runs; this lens does not run): core/arrays/enumerate (`(?:a|ab){1,2}` priority order aa, aab, a, aba, abab, ab - correct), core/arrays/class-order (`\d + 1` FIND-ALL on `10 3 11` - consistent), core/holes/count / lib/rx/repeat (copy (4,2) removed, the remaining three copies; answers held, only the group kind differs, READ-16), lib/search/hits (FIND-ALL [] on `aax axa`, consistent with the anchored atomic body), lib/control/when and when-test expansions (consistent with the body), core/conditions/two-valued's three-meanings table (consistent with the definitions of NOT, `!<5`, complement), core/values/arithmetic examples (member `x` gives nothing; negative result nothing - consistent). 7 checked, 0 inconsistent beyond READ-4 (padded's body cannot produce its own example) and READ-5 (month_numbered's body by join's definition).
- Held, NOT findings: index pieces (places, insert, zero-values, errors, warnings, spellings) pointing forward is the nature of an index; reported only as part of the read-order fix (READ-17) and the generation proposal (G4), not as defects of their own. core/labels/one-rule vs core/conditions/pass-start-read vs labels-vs-captures (a pass that skips its group): consistent once "entering an optional/alternation resets" is applied - no contradiction. core/labels/flow (`&` sides unordered) vs core/labels/paths: consistent. core/filters/and "a condition in an `&` chain stands after every pattern operand" vs core/conditions/in-sequence: consistent (different operators). core/modules/default-set as "an ordinary implicit `(=) := import(...)` line": a program-shape rule, not a provided name - correctly core. core/arrays/enumerate in core: the owner called it a primitive (record line 1209) - correctly core. lib/control/peek, when, when-test, contains, startsWith, endsWith, anchored, anything, quoted, padded, list_of, between, prefix_in, rx.classes, rx.repeat, capture, hits, occurrences: bodies in the core language - correctly library (subject to the undefined names they call, PLACE-3).
- Principles section: 22 pieces, each with a quote and a manager-marked name; their placement first is the format's rule; no history words found in it.
- Slug homing: 98 tags with slugs checked by name against their piece's statement; 7 mis-homed (PLACE-4 (2)-(7)); the rest decide what they carry (sampled by the details text for 11 suspicious slugs).
- warn.unused vs pcrec.warn.unused (core 1110 vs 1121): a naming slip inside a placeholder table, folded into G4 rather than filed.
- Not checked (other lenses): owner quotes word for word (RULING lens); example runs (EXAMPLE lens); record-vs-draft timing overrides after record line 4834 (COMPLETENESS lenses).

CRITIC COMPLETE
