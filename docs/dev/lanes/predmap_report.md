# predmap: how the map accessor `m[key]` would be used (study)

STATE: done. A study; it rules nothing and edits nothing under docs/design/. Proposal under study: the owner's map creator
(record "2026-11-25 OWNER, on maps" and the entry after it, slug map-creator, his lean "yes", NOT ruled). Every run line
below is pasted from `docs/dev/lanes/predmap_evidence/predmap_runs.out` by case id (`[ID]`). Each lowers the form mechanically:
a map is the alternation of its elements in written order, each under its label; a selection is the alternation in the
KEY's order; a join is the sequence. The study's own choices are marked CANDIDATE; what I reasoned by hand is marked hand-worked.
Placeholder spelling for the literal: `{a = A, b = B}` (the manager's, not his). DFA categories are my ESTIMATES in his three
words: yes / never / maybe (weight 0..1, and what it depends on).

## STATE AT HANDOFF
OWED: none.
Rulings file docs/dev/lanes/predmap_rulings.md: empty at the last read (before writing the report). Premise test: pred_doc_lint
"failed 0"; core/modules/map "ruled 2026-11-15". Script last line: see EVIDENCE. Stopped: nothing. No premise failed.
One contradiction in the documents to know first (hand-worked): core/modules/map says "A map interface is not a created value:
no map value is passed around" while the proposal creates a map. The owner's entry reads the proposal as an exception ("the
interface concept is true excepting"); the study treats a created map as an ARRAY whose elements are all labelled, and a
module as a map interface only.

## WHAT THE DOCUMENTS SAY TODAY
Quotes (code = Q#, used by the grid). Tags are the piece names; "early note" = manager's text around a short owner quote, not a ruling.

- Q1 [core/operators/precedence] "| 1 | `.` field, call `f(..)`, index `X[..]` | postfix after an OPERAND, left | a reading |"
- Q2 [core/operators/precedence] "A `(` or `[` is a call or an index only after an operand; after an operator it begins an operand (a reading)."
- Q3 [core/operators/precedence] "`[a = A | b = B]` is two labelled entries" and "`,` also separates entries there, loosest: `[a, b, c]` is `a | b | c`" (a labelled array is writable today; the labelling is not enforced).
- Q4 [core/labels/labels-vs-captures/array-vs-passes, ruled 2026-11-22] "`h[k]` is the k-th setting (the line "Two depths")." and "`h[k]` past the array's end is an absent value: a test on it fails and NOT of it holds (a reading; "Past the end")."
- Q5 [core/labels/paths] "In a value position `alt.x[1]` stays legal (a reading)."
- Q6 [core/values/metadata] "A part label over an array carries two fields: `.index`, the 1-based position in the array of the member that matched, and `.label`, that member's name." / "1-based everywhere, as PCRE's group numbers are; `[0]` is the whole rx." / "A user label named `index` or `label` would hide them: a compile error (a reading)."
- Q7 [core/labels/numbers, ruled 2026-11-22] "A number names a group of the condition's pattern only when that pattern is ONE written literal ...; elsewhere (a sequence, an inserted pattern, an alternation of patterns, a repeat's operand, a chain of several patterns) it is the compile error "name the group"." / "A group's name and its number are two names of one label (naming both is the label-twice error)." / "`$1` reads label 1 as `$x` reads a name." / "`0` is never refused and names the match so far".
- Q7w [core/labels/numbers] "The numbered-label warning fires where a condition or a `$` reads a label by number on a pattern NOT written at that place (a bound name, an imported element ...)".
- Q8 [core/modules/map, ruled 2026-11-15] "`.` has one meaning: a field of the map interface of the thing on its left (a label, a module member, metadata)." and "A map interface is not a created value: no map value is passed around."
- Q9 [core/modules/positional, open tuple-parts] "The same question covers a positional list against a MAP (a module, an import), which has no order."
- Q10 [core/arrays/lift, ruled 2026-11-19] "An array is an alternation; an operation on operands of many strings is the nested loop over each operand's `enumerate`, the first outermost, each result the next alternative." / "A repeated result is harmless: as alternatives the first occurrence wins (a reading, run)." / "The rule is about arrays the user writes and the rxs `enumerate` accepts, not about the match-time array of a label's settings, which is its own type (a reading)."
- Q11 [core/modules/names] table row: "label | a group number, a second name of one label; `0` the match so far | `(1: ..)`, `(0: ..)`".
- Q12 [lib/builtin/import, ruled 2026-11-19] "`m := import("isodate")` binds a module to a name; members are `m.year`." and "it may resolve to several files, and bound to one name its value is their combined map."
- Q13 [core/modules/binding-list] "`(l = left, =right) := X` binds `l` to `X.left` and `right` to `X.right`, on any map; `=left` is `left = left`." [core/modules/all-symbols] "`(=) := X` binds every member `.` reaches on X under its own name".
- Q14 [lib/builtin/warn] "a set of names written as an rx, matched whole." [lib/builtin/export, open] "`@export(names)` exports every binding whose name is in the rx `names`".
- Q15 [lib/builtin/enumerate] "an infinite or over-budget rx is a compile error giving the count".
- Q16 [lib/strings/join] "`join(a, sep = s)` is one value: the members of a finite array in their order, s between them" and "Joined parts stay reachable by their labels (`c.A`): stale beside ... unless join is ruled an exception; no printed line uses it."
- Q17 [lib/modifiers/month-numbered] "`month_numbered(S) := months & (months.mname.index: S)`".
- Q18 [core/modules/conflicts] "A member name carried by two files of one `(=) := import(...)` is a compile error".
- Q19 [lib/records/any-order, under construction] "`any_order(a, sep = ...)` is candidate sugar for a fixed set of parts written in any order; nothing defines it." [lib/records/list-of] "`list_of(X, sep = S)` is the separated list `/(?:${[(=) = X]}${[(=) = S]})*${[(=) = X]}/`: its label is the last item, its array every item."
- Q20 [core/filters/and, ruled 2026-11-17] "P's paths are tried first, the left side deciding" and "`&` ... P's first path with every path of Q, then P's next".
- Q21 [core/diagnostics/warnings] `pcrec.label.hidden`: "a label written in the definition against a binding of the same name".
- Q22 record 2026-11-25 (ruled, not folded): the group questions take the array form, `some(@d, "7")`; PARKED by the manager: "a selection of an array's settings by position" (overlaps `h[k]`). `x{a,b}` is a postfix count (brace-counts, ruled): the owner first thought of braces as "an accessor for maps" and dropped it for PCRE familiarity.
- Q23 early notes (record line 67, 2026-11-14 notes; manager's, NOT rulings): "an array is a map with keys 1..k"; "Access: a NUMBER indexes the array view (`rx[1]`), a NAME navigates the map view (`rx.y`, `rx["y"]`): no ambiguity rule"; "a pattern key = lookup by matching"; "lookup BOTH WAYS ... backward value -> key needs non-overlapping values".
- Q24 the statement put back to him (slug map-creator, NOT ruled): (4) "in `m[key]` a numeral is a position and any other string is a name; a key of several strings gives the selected elements as an array, in the key's order, labels kept".

Every existing meaning, by form:
| form | meaning today | source |
|---|---|---|
| `X[..]` | an index, postfix after an operand, level 1 | Q1, Q2 |
| `h[k]`, `A.h[2]`, `alt.x[1]` | the k-th SETTING of a label (an array of settings, match time; absent past the end) | Q4, Q5 |
| `[0]` | the whole rx | Q6 |
| `[a, b]`, `[a = A | b = B]` | an array literal (an alternation); labelled entries unenforced | Q3 |
| a number | a group number (one literal only; `0` the match so far), `(1: ..)`, `$1` | Q7, Q11 |
| `.index`, `.label` | position and name of the member that matched, on a part label over an array | Q6 |
| `.name` | a field of the map interface: a label, a module member, metadata | Q8 |
| a labelled array entry | `[a = A]` makes a label and no capture; `.label` is "that member's name" | Q3, Q6 |
Not stated anywhere: an index with a name or a set inside `[ ]`; `[k]` on a module; `[k]` on an unlabelled array (beyond `[0]`).

## USES OF THE ACCESSOR
Under the proposal (rule set A, below). "Today" = what the documents let one write now. Programs are a binding plus the final expression.

| id | program | today | DFA (estimate) |
|---|---|---|---|
| U1 | `tok := {num = /\d+/, id = /[a-z]+/, op = /[-+*\/]/}` ; `tok` | writable, unenforced: `[num = /\d+/, id = ..., op = ...]` (Q3) | yes 1.0 (an alternation) |
| U2 | `tok.num SEQ "+" SEQ tok.num` | not writable: `tok.num` today is the label's text, not the element (see clash 1 below) | yes 1.0 |
| U3 | `tok2["id"\|"num"]` (key order beats map order) | not writable | yes 1.0 |
| U4 | `tok[2]` (the second element, by position) | not writable | yes 1.0 |
| U5 | `(?<t>int\|word):${kv[$t]}` (key read at match time) | not writable (a backreference made regular only by hand) | maybe 0.7: finite expansion exists; depends on the key count and on no key text being a prefix of another |
| U6 | `cc := {US = "United States", DE = "Germany"}`; `(?<c>US\|DE)=${cc[$c]}` | not writable | maybe 0.7 (as U5) |
| U7 | `join(iso["day"\|"month"\|"year"], sep = ".")` | reorder by hand: `day SEQ "." SEQ month ...` | yes 1.0 |
| U8 | `(=year, =day) := iso` then `year SEQ "/" SEQ day` | same, with `iso` a module today (Q13) | yes 1.0 |
| U9 | `tok[/num\|id/]` (names by a pattern) | not writable | yes 1.0 (selection is compile time over a finite name list) |
| U10 | `months[1\|2\|3\|4\|5\|6]` | `months & (months.mname.index: between(1, 6))` (Q17) | yes 0.9 (the test form maybe 0.8: which alternative matched) |

`[M0]` WHOLE `ab` HOLDS, `a` HOLDS, `b` FAILS / SEARCHED `ab a b ab` `ab`@0:a / FIND-ALL `ab a b ab` [`ab`@0:a, `a`@3:b, `ab`@7:a] :: (`(?:(?P<a>(?:ab))|(?P<b>(?:a)))`)
`[M0.a]` WHOLE `ab` HOLDS, `a` FAILS, `b` FAILS / SEARCHED `ab a b ab` `ab`@0:a / FIND-ALL `ab a b ab` [`ab`@0:a, `ab`@7:a] :: (`(?:(?P<a>(?:ab)))`)
`[U1]` WHOLE `22` HOLDS, `x` HOLDS, `+` HOLDS, `1+` FAILS / SEARCHED `x1+22*y` `x`@0:id / FIND-ALL `x1+22*y` [`x`@0:id, `1`@1:num, `+`@2:op, `22`@3:num, `*`@5:op, `y`@6:id] :: (`(?:(?P<num>(?:\d+))|(?P<id>(?:[a-z]+))|(?P<op>(?:[-+*/])))`)
`[U2]` WHOLE `1+22` HOLDS, `1+x` FAILS / SEARCHED `1+22 3+x 4+5` `1+22`@0 / FIND-ALL `1+22 3+x 4+5` [`1+22`@0, `4+5`@9] :: (`(?:\d+)\+(?:\d+)`)
`[U3.map]` WHOLE `12ab` HOLDS, `12` HOLDS / SEARCHED `12ab 7` `12`@0:num / FIND-ALL `12ab 7` [`12`@0:num, `ab`@2:id, `7`@5:num] :: (`(?:(?P<num>(?:\d+))|(?P<id>(?:[a-z0-9]+)))`)
`[U3.sel]` WHOLE `12ab` HOLDS, `12` HOLDS / SEARCHED `12ab 7` `12ab`@0:id / FIND-ALL `12ab 7` [`12ab`@0:id, `7`@5:id] :: (`(?:(?P<id>(?:[a-z0-9]+))|(?P<num>(?:\d+)))`)
`[U4]` WHOLE `22` FAILS, `x` HOLDS, `+` FAILS, `1+` FAILS / SEARCHED `x1+22*y` `x`@0:id / FIND-ALL `x1+22*y` [`x`@0:id, `y`@6:id] :: (`(?:(?P<id>(?:[a-z]+)))`)
`[U5]` WHOLE `int:12` HOLDS, `int:x` FAILS / SEARCHED `int:12 word:ab int:x word:7 int:3` `int:12`@0 / FIND-ALL `int:12 word:ab int:x word:7 int:3` [`int:12`@0, `word:ab`@7, `int:3`@28] :: (`(?:int:(?:\d+)|word:(?:[a-z]+))`)
`[U5 ref]` the reading reference (key read, element chosen, matched after the separator) gives `int:12`@0, `word:ab`@7, `int:3`@28
`[U6]` WHOLE `US=Germany` FAILS, `DE=Germany` HOLDS / SEARCHED `US=United States DE=Germany US=Germany DE=United States` `US=United States`@0 / FIND-ALL `US=United States DE=Germany US=Germany DE=United States` [`US=United States`@0, `DE=Germany`@17] :: (`(?:US=(?:United States)|DE=(?:Germany))`)
`[U6 ref]` the reading reference (key read, element chosen, matched after the separator) gives `US=United States`@0, `DE=Germany`@17
`[U5.pos]` WHOLE `1:12` HOLDS, `2:12` FAILS / SEARCHED `1:12 2:ab 1:x int:3 word:q` `1:12`@0 / FIND-ALL `1:12 2:ab 1:x int:3 word:q` [`1:12`@0, `2:ab`@5, `int:3`@14, `word:q`@20] :: (`(?:1:(?:\d+)|2:(?:[a-z]+)|int:(?:\d+)|word:(?:[a-z]+))`)
`[U7.dmy]` WHOLE `2025-01-02` FAILS, `2025` FAILS, `01` FAILS / SEARCHED `2025-01-02 31.12.1999` `31.12.1999`@11:year / FIND-ALL `2025-01-02 31.12.1999` [`31.12.1999`@11:year] :: (`(?P<day>(?:\d\d))\.(?P<month>(?:\d\d))\.(?P<year>(?:\d{4}))`)
`[U8]` WHOLE `2025/02` HOLDS, `25/02` FAILS / SEARCHED `2025/02 25/02 1999/31` `2025/02`@0 / FIND-ALL `2025/02 25/02 1999/31` [`2025/02`@0, `1999/31`@14] :: (`(?:\d{4})/(?:\d\d)`)

Findings from the runs: the same two elements in the other order are a different pattern (`M0[b|1]` vs `M0`: `a`@0 against `ab`@0): the key's order is the alternation's priority. `U3.map` against `U3.sel`: `12ab` is one token `id` under the key's order and two tokens under the map's. The expansion of a key read at match time answers identically to a reference that reads the key (U5, U6: the `ref` lines). A numeral READ at match time is a position under rule 4 (U5.pos: `1:12` selects element 1, `int:3` still selects by name).

Clash 1 (not in the owner's list; hand-worked from Q8 and Q11): for a created map `m`, `m.a` can mean the ELEMENT `a` (a pattern, compile time) or the LABEL `a` (the text matched, match time; the names table puts `.` between the two kinds). Position decides today (left of `:` the last step is a label); the documents do not say what `m.a` is in a pattern position. UNDECIDED; in the lowering both match the same texts (L1 below).

## THE CLASH GRID
Rows: what stands left of `[`. Columns: the key. Each cell: meaning under the proposal [deciding sentence] and `*` where two readings COMPETE. U = UNDECIDED (printed, with the reason). Rows R2, column C1/C2/C4/C7 rest on Q24, the manager's statement, not on a ruling.

| left of `[` | C1 numeral `[1]` | C2 name string `["a"]` | C3 bare name `[a]` | C4 set `["a"\|"b"]` | C5 pattern `[/a.*/]` | C6 read `[$k]` | C7 mix `["a"\|1]` |
|---|---|---|---|---|---|---|---|
| R1 unlabelled array `days := [mon, tue]` | U: only `[0]` is stated (Q6); position is the natural reading | U: edge 3 of the statement; candidate: compile error | U | U (Q10's lift would give an array) | U | U | U |
| R2 created map `m` | position [Q24] ; `m[0]` is the whole rx [Q6] * (0 as position?) | name [Q24] | U * (the name `a`, or the value of binding `a`: run B1) | the selected elements, key order, labels kept [Q24, Q10] | U (edge 2; precedent Q14; runs P1-P4) | U (edge 1; runs U5, U6) | `m["a"]\|m[1]` [Q24, Q10]; the same element twice is harmless [Q10] |
| R3 binding of ONE literal with groups `t := /(\d\d?):(\d\d)/` | U * three readings: group number 1 [Q7, `$1`], position 1 of a one-member array, setting index [Q4]. `t & (1: <13)` today draws the numbered-label warning [Q7w] | U * a group's name (`t.h`, Q8) or an element name | U | U | U | U | U |
| R4 binding of a composed pattern `u := A SEQ B` | U: a number is the compile error "name the group" on it [Q7] | U: its labels are reached by `.` [Q8]; no elements | U | U | U | U | U |
| R5 a label `h` (its array of settings) | k-th setting [Q4] (ruled) | U: settings have no names | U | U * `h[1\|2]`: lift [Q10] says arrays the user writes, "not ... the match-time array of a label's settings" | U | U * `h[$k]`: match-time index; parked selection by position [Q22] | U |
| R6 part label over an array `[w = [/Mon/, /Tue/]]` | U * the k-th SETTING of the label `w` (Q4) or the k-th MEMBER of the array it labels (Q6): run N3b parts them | U: `.label` names the matched member [Q6] | U | U | U | U | U |
| R7 module `m := import("isodate")` | U: "a MAP ... which has no order" [Q9] | U: `m.year` is the ruled form [Q12, Q8]; `m["year"]` would duplicate it | U | U: a set of members | U: `import`'s argument is an rx over file names [Q12], `@export`'s a set of names [Q14] | U | U |

Count: 49 cells; 4 rest on the manager's statement (R2: C1, C2, C4, C7), 1 is ruled (R5-C1), 44 are UNDECIDED. Competition (`*`): R2-C1 (zero), R2-C3, R3-C1, R3-C2, R5-C4, R5-C6, R6-C1. Run for the two that are about the proposal's own row: `m[a]` with a := "b" (`[B1.name]` WHOLE `ab` HOLDS, `a` FAILS, `b` FAILS / SEARCHED `ab a b ab` `ab`@0:a / FIND-ALL `ab a b ab` [`ab`@0:a, `ab`@7:a] :: (`(?:(?P<a>(?:ab)))`) against `[B1.value]` WHOLE `ab` FAILS, `a` HOLDS, `b` FAILS / SEARCHED `ab a b ab` `a`@0:b / FIND-ALL `ab a b ab` [`a`@0:b, `a`@3:b, `a`@7:b] :: (`(?:(?P<b>(?:a)))`)).

## NUMBERS AND GROUP NUMBERS
His "consider we can't use numbers to refer to group numbers". Three number spaces share the numeral: a GROUP number (left of `:` or `$1`; Q7, Q11), a POSITION in an array (the proposal's `m[1]`; Q6's `[0]`), a SETTING index (`h[k]`; Q4). They are told apart by the slot, not the numeral: a group number stands left of `:` or after `$` and is refused on anything but ONE written literal; `[k]` stands after an operand.

`[N1]` map {a=/(\d)-(\d)/, b=/(x)/} lowered: label -> group number {'a': 1, 'b': 4}; positions are a=1, b=2
`[N1b]` on `x` the lowered alternation's group 1 is None, group 3 is None, group 4 is 'x'; the element b alone `(x)` has group 1 `x`
`[N2]` (core/labels/numbers) a group number against a map (an alternation of its elements): compile error "name the group"

- Position is not group number (run N1): a map element's group number shifts with the groups inside the elements before it (b is position 2, group 4). In the language `[x = A]` "makes a label and no capture" (core/labels/paths), so a part-label map has no group numbers at all; a position survives any inner groups.
- What numbers refuses today: a number against a sequence, an inserted pattern or an alternation of patterns (Q7). A map is an alternation of patterns, so `(1: ..)` against `m` is already the compile error "name the group" (N2 map row); `m[1]` is a different slot, so nothing is refused or reinterpreted.
- Renumbering: a selection is a new array with its own positions (N3): `m["b"|"a"][1]` is element b while `m[1]` is a.
`[N3b]` part label w over [/Mon/, /Tue/] in a loop on `TueMon`: the settings of w are `Tue`, `Mon` (w[1] as a setting = `Tue`, member 2); the array's member 1 is /Mon/: the two readings of w[1] part
- Does any existing program change meaning? Hand-worked: every `X[..]` printed in the documents has a label on its left (Q4, Q5: `h[2]`, `A.h[2]`, `alt.x[1]`), and no map can be created today, so none. The one new clash is a NAME held by both a label and a created map (`h[2]`): the existing hide rule `pcrec.label.hidden` (Q21) fires on a label against a binding of the same name, so the case is a warning today, not a new rule; which one `h[2]` reads is UNDECIDED.
- A group-number-looking key: `m[1]` is not group 1 under any candidate; a user wanting group 1 of one literal writes `(1: ..)` as today.

## SELECTING NAMES BY A PATTERN
`m[/a.*/]`. Precedents: `@warn.off(sel)` takes "a set of names written as an rx, matched whole" (Q14); `@export(names)` and `import(names)` select by an rx over names (Q14, Q12), no order stated. `enumerate` refuses an infinite rx (Q15).
Map PN = {ab = /x/, a = /xy/, abc = /xyz/, b = /q/} (elements overlap: `x` is a prefix of the others).
`[P1.map]` WHOLE `xyz` HOLDS, `xy` HOLDS, `x` HOLDS / SEARCHED `xyz xy x q` `x`@0:ab / FIND-ALL `xyz xy x q` [`x`@0:ab, `x`@4:ab, `x`@7:ab] :: (`(?:(?P<ab>(?:x))|(?P<a>(?:xy))|(?P<abc>(?:xyz)))`)
`[P1.key]` WHOLE `xyz` HOLDS, `xy` HOLDS, `x` HOLDS / SEARCHED `xyz xy x q` `xyz`@0:abc / FIND-ALL `xyz xy x q` [`xyz`@0:abc, `x`@4:ab, `x`@7:ab] :: (`(?:(?P<abc>(?:xyz))|(?P<ab>(?:x))|(?P<a>(?:xy)))`)
`[P1.mapof]` WHOLE `xyz` HOLDS, `xy` HOLDS, `x` HOLDS / SEARCHED `xyz xy x q` `x`@0:ab / FIND-ALL `xyz xy x q` [`x`@0:ab, `x`@4:ab, `x`@7:ab] :: (`(?:(?P<ab>(?:x))|(?P<a>(?:xy))|(?P<abc>(?:xyz)))`)
`[P2]` modes: a compile error (m[/a.*/] by the key's enumeration): key 'a.*' is infinite: enumerate refuses it
`[P2b]` by the map's own names the same key is finite: m[/a.*/] selects ['ab', 'a', 'abc']
`[P4]` whole match: m[/a/] selects ['a'] (not ab, abc); m[/a|b/] selects ['a', 'b']
`[P3.empty]` WHOLE `xyz` FAILS, `xy` FAILS, `x` FAILS / SEARCHED `xyz xy x q` FAILS / FIND-ALL `xyz xy x q` [] :: (`(?!)`)
- The order parts: by the map's own order `m[/a.*/]` is `ab|a|abc` and finds `x`@0; by the key's enumeration (`abc|ab|a`) it is `abc|ab|a` and finds `xyz`@0 (P1.map against P1.key; "differ" line). The same three names selected by a key that lists them in another order but taken in the map's order are identical to P1.map ("same" line).
- Finite against infinite: the key's own enumeration is refused when the key is infinite (P2, Q15), but selecting AMONG THE MAP'S NAMES is always finite (P2b). So a pattern key is usable only as a filter over the names (map order), or only for finite keys (key order). Which one is his decision.
- Whole match: `m[/a/]` selects the name `a` only, not `ab` or `abc` (P4; the selector precedent "matched whole").
- Empty selection: no name matches. It is the empty array, `(?!)`, never matching in any mode (P3.empty) or a compile error as for a literal key no element has (P3.lit in the next section). A selector that selects nothing draws a warning in `@warn.off` (`pcrec.warn.unused`, lib/builtin/warn): precedent for a warning, not an error.
- DFA: yes 1.0 for a compile-time selection (a finite name list); not applicable to match time.

## NAMES AND NUMBERS COMBINED
`[M0[a|1]]` WHOLE `ab` HOLDS, `a` FAILS, `b` FAILS / SEARCHED `ab a b ab` `ab`@0:a / FIND-ALL `ab a b ab` [`ab`@0:a, `ab`@7:a] :: (`(?:(?P<a>(?:ab))|(?:ab))`)
`[M0[1|b]]` WHOLE `ab` HOLDS, `a` HOLDS, `b` FAILS / SEARCHED `ab a b ab` `ab`@0:a / FIND-ALL `ab a b ab` [`ab`@0:a, `a`@3:b, `ab`@7:a] :: (`(?:(?P<a>(?:ab))|(?P<b>(?:a)))`)
`[M0[b|1]]` WHOLE `ab` HOLDS, `a` HOLDS, `b` FAILS / SEARCHED `ab a b ab` `a`@0:b / FIND-ALL `ab a b ab` [`a`@0:b, `a`@3:b, `a`@7:b] :: (`(?:(?P<b>(?:a))|(?P<a>(?:ab)))`)
`[M0[2|1]]` WHOLE `ab` HOLDS, `a` HOLDS, `b` FAILS / SEARCHED `ab a b ab` `a`@0:b / FIND-ALL `ab a b ab` [`a`@0:b, `a`@3:b, `a`@7:b] :: (`(?:(?P<b>(?:a))|(?P<a>(?:ab)))`)
`[K1]` modes: a compile error (m["zz"|"yy"]): no element named 'zz'
`[K2]` modes: a compile error (m[3] on a map of two): no element at position 3 (the map has 2)
`[K3.err]` modes: a compile error (m["b"|"zz"], one atom absent (CANDIDATE: any absent atom is the error)): no element named 'zz'
`[K3.drop]` WHOLE `ab` FAILS, `a` HOLDS, `b` FAILS / SEARCHED `ab a b ab` `a`@0:b / FIND-ALL `ab a b ab` [`a`@0:b, `a`@3:b, `a`@7:b] :: (`(?:(?P<b>(?:a)))`)
`[K4.zero]` WHOLE `ab` HOLDS, `a` HOLDS, `b` FAILS / SEARCHED `ab a b ab` `ab`@0:a / FIND-ALL `ab a b ab` [`ab`@0:a, `a`@3:b, `ab`@7:a] :: (`(?:(?P<a>(?:ab))|(?P<b>(?:a)))`)
`[K5]` modes: a compile error (a map with the label "1" (CANDIDATE: refused)): label '1' is a numeral: unreachable by name
`[K5b]` with numeral names allowed, NM["1"] is ('1', 'x') and NM[1] is ('1', 'x'): the same text names two elements
`[K5c]` a label "01" or "1a" is not a canonical numeral: is_numeral -> False, False
- `m["a"|1]` (a is position 1) is the same element twice: the copy is harmless, "the first occurrence wins" (Q10); answers equal `m.a` (the "same" lines under USES). `m[1|"b"]` equals `m["a"|"b"]`; `m["b"|1]` equals `m[2|1]` and differs from the map's order.
- A numeral-looking name: a label `"1"` makes `m["1"]` (a position under rule 4) and the element named `"1"` collide (K5b). CANDIDATE: refuse a numeral as a map label (K5); `"01"` and `"1a"` are not canonical numerals and stay names (K5c). A read that yields `1` at match time is a position (U5.pos).
- A key that selects nothing: a literal key no element has is a compile error (statement line 5; K1, K2). A set with one absent atom: error for the whole key (K3.err, the statement's reading) or dropped silently (K3.drop): CANDIDATE choice, the statement does not say.
- `m[0]` is the whole rx on the documents' sentence (Q6), answers equal the bare map (K4.zero): position 0 does not exist. UNDECIDED whether `m[0|1]` is allowed.
- Order: Q10's lift puts the first key atom outermost: `m["a"|1]` and `m[1|"a"]` give the same elements in a different order only when two different elements are named.

## TABLES OF PATTERNS
Today (Q17): `months := [mname = [/Jan(?:uary)?/, ...]]`, `month_numbered(S) := months & (months.mname.index: S)`: the NUMBER is the position of the member matched, read as a value; the match text is still the month name. A map gives each month a NAME (`jan` ... `dec`) beside the position.
`[T1.first6]` WHOLE `Jun` HOLDS, `Jul` FAILS / SEARCHED `Dec Feb` `Feb`@4:feb / FIND-ALL `Mar Oct Apr` [`Mar`@0:mar, `Apr`@8:apr] :: (`(?:(?P<jan>(?:Jan(?:uary)?))|(?P<feb>(?:Feb(?:ruary)?))|(?P<mar>(?:Mar(?:ch)?))|(?P<apr>(?:Apr(?:il)?))|(?P<may>(?:May))|(?P<jun>(?:June?)))`)
`[T2.name]` WHOLE `Mar` HOLDS, `March` HOLDS / SEARCHED `Mar Oct March` `Mar`@0:mar / FIND-ALL `Mar Oct March` [`Mar`@0:mar, `March`@8:mar] :: (`(?:(?P<mar>(?:Mar(?:ch)?)))`)
- The first line reproduces the documents' month_numbered(between(1, 6)) answers (WHOLE `Jun` HOLDS, `Jul` FAILS / SEARCHED `Feb`@4 / FIND-ALL `Mar`@0, `Apr`@8): selection by position equals the `.index` test on this table (checked in the script). Tests by position and selection agree in general because `&` keeps the paths through the chosen alternative (Q20, hand-worked); they would part only if `&` stopped trying P's next path.
- What a map adds: lookup by NAME (`months["mar"]`, T2) in the source, and the name comes out at match time as `.label` (the `:mar` tag on each match line), where today only `.index` is read.
`[T3.cc]` WHOLE `Germany` HOLDS, `Germany!` FAILS / SEARCHED `Peru Germany` `Germany`@5:DE / FIND-ALL `United States Germany` [`United States`@0:US, `Germany`@14:DE] :: (`(?P<US>(?:United States))|(?P<DE>(?:Germany))`)
`[T3b]` backward, value to key: the label that matched is the key: `United States` -> US
`[T4.overlap]` WHOLE `color` HOLDS / SEARCHED `color` `color`@0:en / FIND-ALL `color color` [`color`@0:en, `color`@6:en] :: (`(?:(?P<en>(?:color))|(?P<us>(?:color)))`)
- Country code to name, forward: `cc[$c]` with the code read earlier (U6: only consistent pairs match). Backward, value to key: the label of the alternative that matched is the key (T3b). Q23's early note says backward lookup "needs non-overlapping values": with two keys of one value (T4) only the first key is ever reported, `us` never.
- Stays out of reach: a table that REWRITES text (month name to the text `3`): a match is an rx and nothing is replaced (core/values/one-type); the number is read as a value (`.index`), not produced as text. A key that is itself a pattern with a reverse lookup of an overlapping value is the "lookup by matching" of Q23, unbuilt. DFA: forward yes 1.0 (const key); read key maybe 0.7; backward `.label` maybe 0.8 (needs the alternative that matched; yes when values are disjoint, as months; weaker with overlap).

## LIBRARY NAMESPACES
A module is a map interface (Q8); a created map is an array whose elements are labelled. Both have `.`; the brackets are new only on the second.
`[L1.dot]` WHOLE `2025` HOLDS, `99` FAILS / SEARCHED `x 2025 y` `2025`@2:year / FIND-ALL `2025 1999 x` [`2025`@0:year, `1999`@5:year] :: (`(?:(?P<year>(?:\d{4})))`)
`[L1.br]` WHOLE `2025` HOLDS, `99` FAILS / SEARCHED `x 2025 y` `2025`@2:year / FIND-ALL `2025 1999 x` [`2025`@0:year, `1999`@5:year] :: (`(?:(?P<year>(?:\d{4})))`)
`[L1b]` the label: m.year as a bare element carries it in the lowering year; the one-element array m["year"] keeps the label: year
`[L2]` modes: a compile error (import("a"|"b") with a shared member `year`): member ['year'] carried by two files (core/modules/conflicts)
`[L2b]` without the clash the combined map is ['year', 'tz', 'hour']
`[L3.all]` WHOLE `2025/02` HOLDS, `25/02` FAILS / SEARCHED `2025/02 25/02 1999/31` `2025/02`@0 / FIND-ALL `2025/02 25/02 1999/31` [`2025/02`@0, `1999/31`@14] :: (`(?:\d{4})/(?:\d\d)`)
- `m["year"]` on a module: nothing in the documents (grid R7). If allowed it would DUPLICATE `m.year` (the same text, L1 lines); the proposal's own answer for a created map is that `["year"]` is a one-element ARRAY keeping the label while `.year` is the element; for a module that distinction has no support (Q8 "no map value is passed around"). Candidate: bracket access on a module is a compile error until a use appears; candidate: it equals `.`.
- Collision with the module interface: a created map named like a module member (`m := import("x")` and a local `{year = ..}`) are two bindings; nothing collides until `(=) := aMap` or an import shares a name: `(=) := aMap` binds every element under its own name, by the same rule as for a module (Q13), and the hide-label warning and Q18's shared-name error apply per name; `(=) := {a = A, b = B}` then reads `a`, `b` as the elements (L3: `year SEQ "/" SEQ month` equals `iso.year "/" iso.month`).
- Can a map be exported? Hand-worked: a binding `pub := {..}` is exported by the `_` rule like any binding (core/labels/export) and reached `lib.pub.a`; the reading `lib.pub["a"]` follows the map row, not a module row. `import("a"|"b")` is "their combined map" (Q12): a shared member is the compile error (Q18, L2), so a combined module is a map with unique names and `["year"]` behaves as on any map if rule A is extended to modules.
- The reserved names: `index` and `label` are metadata fields of a part label over an array (Q6), and "a user label named `index` or `label` would hide them: a compile error". An element so named would also clash with the field when the map is under a part label; candidate: the same compile error on a map label.
- Overlap of namespaces is the real cost: a map's names are labels (Q8's `.` reaches labels, members, metadata), so a map with elements, labels written inside the elements, and metadata share one `.` namespace. Not decided anywhere.

## A MAP UNDER JOIN AND ITS SIBLINGS
His question to the manager: a sequence map. The manager's thought (record, not ruled): one map, the combiner chosen by the function applied.
`[J0.alt]` WHOLE `2025-01-02` FAILS, `2025` HOLDS, `01` HOLDS / SEARCHED `2025-01-02 31.12.1999` `2025`@0:year / FIND-ALL `2025-01-02` [`2025`@0:year, `01`@5:month, `02`@8:month] :: (`(?:(?P<year>(?:\d{4}))|(?P<month>(?:\d\d))|(?P<day>(?:\d\d)))`)
`[J1.join]` WHOLE `2025-01-02` HOLDS, `2025` FAILS, `01` FAILS / SEARCHED `2025-01-02 31.12.1999` `2025-01-02`@0:day / FIND-ALL `2025-01-02 31.12.1999` [`2025-01-02`@0:day] :: (`(?P<year>(?:\d{4}))-(?P<month>(?:\d\d))-(?P<day>(?:\d\d))`)
`[J2.dmy]` WHOLE `31.12.1999` HOLDS, `2025-01-02` FAILS / SEARCHED `2025-01-02 31.12.1999` `31.12.1999`@11:year / FIND-ALL `2025-01-02 31.12.1999` [`31.12.1999`@11:year] :: (`(?P<day>(?:\d\d))\.(?P<month>(?:\d\d))\.(?P<year>(?:\d{4}))`)
`[J2.sub]` WHOLE `2025-02` HOLDS, `2025-01-02` FAILS / SEARCHED `2025-02 1999-31` `2025-02`@0:day / FIND-ALL `2025-02 1999-31` [`2025-02`@0:day, `1999-31`@8:day] :: (`(?P<year>(?:\d{4}))-(?P<day>(?:\d\d))`)
`[J3.any]` WHOLE `2025-01-02` HOLDS, `01-2025-02` HOLDS, `01-02-2025` HOLDS, `2025-2025-01` FAILS / SEARCHED `x 01-2025-02` `01-2025-02`@2 / FIND-ALL `2025-01-02 01-02-2025 7` [`2025-01-02`@0, `01-02-2025`@11] :: (`(?:(?:\d{4})-(?:\d\d)-(?:\d\d)|(?:\d{4})-(?:\d\d)-(?:\d\d)|(?:\d\d)-(?:\d{4})-(?:\d\d)|(?:\d\d)-(?:\d\d)-(?:\d{4})|(?:\d\d)-(?:\d{4})-(?:\d\d)|(?:\d\d)-(?:\d\d)-(?:\d{4}))`)
`[J3]` any_order of 3 parts lowered: 6 branches (n!), labels not carried by `re` (two groups of one name per branch are the language's union, hand-worked); 4 parts: 24 branches
`[J4.list]` WHOLE `x,1,22` HOLDS, `x,,1` FAILS / SEARCHED `q x,1,22 y` `q`@0:id / FIND-ALL `x,1,22 y,7` [`x,1,22`@0:id, `y,7`@7:id] :: (`(?:(?:(?:[a-z0-9]+)|(?:\d+)),)*(?:(?P<id>(?:[a-z0-9]+))|(?P<num>(?:\d+)))`)
`[J1b]` labels in the sequence lowering: ['day', 'month', 'year'] (the lowering keeps them; lib/strings/join marks its own line on joined parts labels stale)
- One element list feeds all four (J5 in the output): bare = alternation (J0: `day` never reported, `month` has the same text and comes first); `join(m, sep = "-")` = sequence (J1: `2025-01-02` in one match, three labels); `any_order` = the permutation alternation (J3: 6 branches for 3 parts, 24 for 4, an n! table in the lowering; DFA maybe 0.7: yes in principle, states grow with the parts); `list_of` = `(?:X,)*X` (J4: label is the last item, Q19).
- With the accessor, `join(iso["day"|"month"|"year"], sep = ".")` REORDERS (J2.dmy: the key's order is the sequence order) and `iso["year"|"day"]` joins a subset (J2.sub). For join the key's order matters most; for the bare alternation it is only priority.
- Labels in each: the lowering keeps every label in the alternation and the sequence (J1b); in `list_of` the label is the last item (Q19); in `any_order` each branch carries the same labels in another order (hand-worked: `re` cannot show it; two groups of one name are the language's union). Q16's line on joined parts' labels is marked stale by its own piece: what a join over a map does with the labels is the point to state. The runs show the lowering keeps them.
- So a "sequence map" is a FUNCTION over the one map (a different combiner), not a second kind of map; nothing in the runs needed two kinds. A cost: `join` takes "a finite array" (Q16) and the map is an array whose members are labelled; accepting it is a decision (labels kept or dropped).
- DFA: bare, join, list_of yes 1.0; any_order maybe 0.7.

## CANDIDATE RULES AND THEIR EDGES
No pick. Three rule sets for `m[key]` on a created map.
**A. As put (Q24).** Numeral = position (`0` the whole rx), other string = name, a set is the lift in the key's order, labels kept, a key no element has is a compile error at compile time. Edges unruled: read keys, pattern keys, names on plain arrays.
 Easy: positions and names in one slot; reordering by key (U3, U7). Refuses: nothing about the edges; a numeral-looking label must be refused. Parts: `m["a"|1]` is legal (same element twice, M0[a|1]).
**B. A plus finite selectors and read keys.** A, with: a pattern key selects the names it matches WHOLE, in the MAP's order (finite always; no key enumeration), an empty selection is a warning and the empty array; a key read at match time is the finite expansion (numerals read as positions) and an unknown value at match time simply fails to match.
 Easy: `tok[/num|id/]` (U9), table lookups (U5, U6). Refuses: key-order for a pattern key. Parts from A: `m[/x/]` is a pattern, not a compile error; U5/U6 are legal. DFA: A's rows yes; reads maybe 0.7.
**C. Names only in brackets.** `m[ ]` takes name strings and sets of names (and a pattern, as B); a numeral is a compile error on a map; positions come from `.index`, `each`, or nothing.
 Easy: no clash with group numbers, setting indices (`h[k]`) or `[0]`; `m["a"|1]` is refused (R-C.1), the question dissolves; numeral-looking labels are not a problem. Refuses: `tok[2]`, `months[1|..|6]` (rewritten as a name set or by `.index` as today, Q17). Parts from A: `m["a"|1]` and `m[2|1]` are compile errors.
Parting examples (run above): `m["a"|1]` A/B legal = `m.a`, C error. `m[/a.*/]`: A under construction, B map order `x`@0, key-order variant `xyz`@0 (P1). `m[$k]`: A under construction, B legal, C legal for names. `m[0]`: A/B whole rx, C error. DFA of each rule set: yes except read keys (maybe 0.7) and any_order (maybe 0.7).

## OWNER QUESTIONS
Slugs, candidates, runs (the three modes are in each pasted line). All unruled.
1. **numeral-key** (do numerals in `[ ]` pick a position): A/B yes, C no. Run, the question he asked: `[M0[a|1]]` WHOLE `ab` HOLDS, `a` FAILS, `b` FAILS / SEARCHED `ab a b ab` `ab`@0:a / FIND-ALL `ab a b ab` [`ab`@0:a, `ab`@7:a] :: (`(?:(?P<a>(?:ab))|(?:ab))`) and C: `[R-C.1]` modes: a compile error (candidate C on m["a"|1]): candidate C: a numeral in m[ ] is refused (names only).
2. **key-order** (a set of keys: the key's order or the map's order): key's order (A as put) `[M0[b|1]]` WHOLE `ab` HOLDS, `a` HOLDS, `b` FAILS / SEARCHED `ab a b ab` `a`@0:b / FIND-ALL `ab a b ab` [`a`@0:b, `a`@3:b, `a`@7:b] :: (`(?:(?P<b>(?:a))|(?P<a>(?:ab)))`) against map order, which would give `[M0[a|b]]` WHOLE `ab` HOLDS, `a` HOLDS, `b` FAILS / SEARCHED `ab a b ab` `ab`@0:a / FIND-ALL `ab a b ab` [`ab`@0:a, `a`@3:b, `ab`@7:a] :: (`(?:(?P<a>(?:ab))|(?P<b>(?:a)))`).
3. **read-key** (`m[$k]` at match time: allowed or under construction): allowed `[U5]` WHOLE `int:12` HOLDS, `int:x` FAILS / SEARCHED `int:12 word:ab int:x word:7 int:3` `int:12`@0 / FIND-ALL `int:12 word:ab int:x word:7 int:3` [`int:12`@0, `word:ab`@7, `int:3`@28] :: (`(?:int:(?:\d+)|word:(?:[a-z]+))`); under construction means the table is written by hand, as today.
4. **pattern-key** (names by pattern: the map's order over the names, the key's enumeration order, or not yet; and an empty selection: error, warning, or empty): `[P1.map]` WHOLE `xyz` HOLDS, `xy` HOLDS, `x` HOLDS / SEARCHED `xyz xy x q` `x`@0:ab / FIND-ALL `xyz xy x q` [`x`@0:ab, `x`@4:ab, `x`@7:ab] :: (`(?:(?P<ab>(?:x))|(?P<a>(?:xy))|(?P<abc>(?:xyz)))`) against `[P1.key]` WHOLE `xyz` HOLDS, `xy` HOLDS, `x` HOLDS / SEARCHED `xyz xy x q` `xyz`@0:abc / FIND-ALL `xyz xy x q` [`xyz`@0:abc, `x`@4:ab, `x`@7:ab] :: (`(?:(?P<abc>(?:xyz))|(?P<ab>(?:x))|(?P<a>(?:xy)))`); empty `[P3.empty]` WHOLE `xyz` FAILS, `xy` FAILS, `x` FAILS / SEARCHED `xyz xy x q` FAILS / FIND-ALL `xyz xy x q` [] :: (`(?!)`) against an error.
5. **bare-name-key** (`m[a]`: the name `a`, the value of binding `a`, or an error): `[B1.name]` WHOLE `ab` HOLDS, `a` FAILS, `b` FAILS / SEARCHED `ab a b ab` `ab`@0:a / FIND-ALL `ab a b ab` [`ab`@0:a, `ab`@7:a] :: (`(?:(?P<a>(?:ab)))`) against `[B1.value]` WHOLE `ab` FAILS, `a` HOLDS, `b` FAILS / SEARCHED `ab a b ab` `a`@0:b / FIND-ALL `ab a b ab` [`a`@0:b, `a`@3:b, `a`@7:b] :: (`(?:(?P<b>(?:a)))`) (a := "b").
6. **numeral-labels** (may a map label be a numeral): refuse (K5), or allow and reach it only by `.`: `[K5b]` with numeral names allowed, NM["1"] is ('1', 'x') and NM[1] is ('1', 'x'): the same text names two elements.
7. **zero-and-part-label** (`m[0]` the whole rx; `w[1]` on a part label over an array: setting or member): see K4.zero and N3b above; candidate for `w[1]`: refuse until a use appears.
8. **module-bracket** (`m["year"]` on a module): the same as `.year` (L1), or a compile error: `[L1.br]` WHOLE `2025` HOLDS, `99` FAILS / SEARCHED `x 2025 y` `2025`@2:year / FIND-ALL `2025 1999 x` [`2025`@0:year, `1999`@5:year] :: (`(?:(?P<year>(?:\d{4})))`).
9. **element-label** (does `m.a` carry the label `a` and does `join` keep labels): `[J1.join]` WHOLE `2025-01-02` HOLDS, `2025` FAILS, `01` FAILS / SEARCHED `2025-01-02 31.12.1999` `2025-01-02`@0:day / FIND-ALL `2025-01-02 31.12.1999` [`2025-01-02`@0:day] :: (`(?P<year>(?:\d{4}))-(?P<month>(?:\d\d))-(?P<day>(?:\d\d))`) keeps them in the lowering; whether it must is his.
10. **plain-array-name** (a name on an unlabelled array, edge 3): compile error (candidate) since an unlabelled array has no names; by the statement `[a, b][...]` stays positions only.

## EVIDENCE AND COMMANDS
- `python3 -I docs/dev/lanes/predmap_evidence/predmap_runs.py` (seconds); output committed as `predmap_runs.out`; last line: `predmap_runs: 54 cases, 0 failed`.
- Run in order of the sections; each `[ID]` line is the lowered regex's answer in WHOLE / SEARCHED / FIND-ALL, labels after `:`. Python `re`; the only models of mine: the lowering, the selection in the key's order, finite expansion of read keys (checked against a reading reference), the filter-equals-selection reasoning (hand-worked, Q20), the permutation alternation for any_order (labels not shown by `re`).
- Hand-worked claims: the contradiction with Q8, clash 1, "no existing program changes", `&` keeping paths (Q20), export of a map, DFA estimates.
- Premise: `python3 -I scripts/pred_doc_lint.py` -> `pred_doc_lint: checks passed 9173, failed 0`.
