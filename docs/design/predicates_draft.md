# The predicate language ([COND-FAMILY] #6): a preliminary specification for critical analysis

## Changelog

- **rev 2 (lane predspec2, 2026-11-14).** Folds every ruling and lean recorded in COND-FAMILY.md after rev 0 (from
  "2026-11-14 RULINGS on predicates_draft.md §13" to the counting-occurrences ruling) and the content they adopt
  from `docs/dev/lanes/predx_report.md`. Superseded text is REPLACED, not kept beside the new. Changed: §0 goals and
  marks; §1 (organisational layer cut); §2.2 (`&` right-associative); §2.4 (C9: string sets, `\d+` integers,
  explicit `unpad`); NEW §2.7 transforms as pullbacks spelled as a pipeline (S1); §3.5 NEW arrays of filters and
  transforms; §4.3 repeated labels by the sequence rule (Q4) and `occurs`; §4.4 computed labels as match-dependent
  bindings (Q6, `with` gone); §4.5 some-parse (Q2); NEW §4.6 value-vs-value relations priced by class count (S3);
  §5.1 program shape: no alphabetic keywords, `@` statements, unused-pattern error; NEW §5.5 `enumerate`; NEW §5.6
  assertions; §6 capability levels: the default promise (Q5), `captures` and the reporting axis (S9, Q11), `&` at
  `vm` ([PRED-SPLIT]); §7: bounded recursion (S6, Q12), `records` tiling (S14, Q13), modules as maps with
  `import`/`@export` as functions, the empty-match rule; NEW §7.1 named warnings; §8: `occurs`, tuple comparisons,
  `assert`; §9 reduced to the cut list (Q8); §11: no implicit x-mode (C2), context-marked sets (S2, Q1 TENTATIVE),
  guard holes need `&` (C4); §12 examples rewritten to the newest spellings, three added (E-HTTP, E-SEP, E-DEPTH);
  §13 resolved items marked, contradictions among the new rulings added (C17-C28, O19-O25); §15 rows added.
- **rev 0 (lane predspec, 2026-11-14).** First consolidation of the notes through the outer-layer note.

## 0. Status, goals, standing questions

**Status: DRAFT rev 2 (lane predspec2, 2026-11-14). NOT a ruling, NOT scheduled** (Frank 2026-11-13: #6 not
scheduled, discussion continues; "Enumerate go." 2026-11-14 is a DESIGN adoption, not a build go). Purpose (Frank
2026-11-14): "create a preliminary predicate spec doc with our latest ideas for the purpose of critical analysis.
Provide reasoning." It consolidates the dated notes in `docs/design/plan_row_bodies/COND-FAMILY.md` (the source of
truth; the LATEST note on a topic wins) and the parts of `docs/dev/lanes/predx_report.md` (exploration, S1-S20,
Q1-Q14) that the 2026-11-14 rulings adopt. Older background, `docs/design/cond_family.md` (survey rev 0, D193) and
`docs/design/cond_family_syntax_survey.md` (lane synsurv), is cited where still live. No rule here is new: every
rule traces to a note (§15); where the notes are silent or disagree, §13 lists both readings. Contradictions are
listed, never resolved.

**SYNTAX IS PLACEHOLDER THROUGHOUT.** The owner rules semantics; spelling is a later design step (D193 add. 4).
One spelling RULE is ruled (§5.1): no alphabetic operators or statement keywords. Examples use the latest
spellings: `/.../` rx literals (bare rx fragments are never admitted in the expression language), `:=` define, `=`
bind, `:` constrain, `==` the equality section, `[]` positional, `&` (right-associative) / `where` / dot for
filtering and labels, transforms as pipeline stages (`x & unpad & between(1, 12)`), `@` effect statements,
modules as `m := import("m")`, 1-based indexes.

Status marks: **RULED** (a D-number or Frank's explicit ruling before rev 0), **AGREED** (Frank proposed or
accepted in discussion before rev 0), **LEAN** (manager's leaning before rev 0), and for items folded in rev 2
exactly as the note says: **OWNER RULED 2026-11-14** (Frank's ruling or agreement) or **MANAGER LEAN** (the
manager's lean recorded on the note, not yet answered); **OPEN** (§13).

### Goals (MANAGER DRAFT, not yet seen by the owner; ranked, highest wins a conflict)

| # | goal | who benefits | checkable form |
|---|---|---|---|
| G1 | EXPRESSIVENESS over the string: conditions PCRE cannot state (cross-label arithmetic, checksums, calendar validity, key-order independence, computed properties, occurrence counts) are short programs | users writing validators, filters, log/JSONL searches | every §12 acceptance case is written in at most ~6 definitions with no construct outside §§2-8 |
| G2 | LINEAR, AUTOMATON-CODE-ONLY BY DEFAULT: a program that compiles at the default level runs as automaton code (one pass or an automaton relax-then-verify split; linear time, no backtracking, hostile-input safe, self-contained output) | anyone matching untrusted input; embedders | every default-level §12 case compiles to automaton code only (`RX_ENGINE` stamp); anything else is a compile error naming the construct and the opt-in, never a silent route change |
| G3 | PCRE COMPATIBILITY: every PCRE pattern is a valid one-literal program with PCRE's meaning | existing PCRE users; the corpus | the whole `.rxt` corpus, each pattern wrapped as `/.../`, answers identically to today (a nullable one-literal program gets the `empty.search` WARNING only, §7) |
| G4 | STRUCTURE IS COMPILE-TIME ONLY, TOTAL, TERMINATING: every structural evaluation (each, join, records, indexing, imports, enumerate) is finite and ends | the compiler's users (no hang at build), the security story | recursion through parameterized definitions only by a strictly decreasing literal parameter (§7); every structural operator ranges over finite declared things, `enumerate` under a budget; a fuzzer over programs never hangs the compiler (watchdog) |

Non-goals: §14. Priority G1 > G2 > G3 > G4 is the manager's draft order; G2 vs G1 conflicts (a condition that
is expressible but not regular, or regular but too large) resolve by the capability levels (§6) and the
class-count cost (§4.6), not by dropping G1.

### Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** Mostly not relevant: a language spec introduces no measured quantity. The numbers cited
   (ISO date with leap Feb 29 as a plain regex: 6,848 B object, 5.9 ms compile, all 4-digit years; 6,376 B for
   2000-2099; COND-FAMILY 2026-11-13 "COST METRICS"; class counts in §4.6) are compile-time sizes or arithmetic,
   not timings; any cost table a build produces must name its regime then.
2. **The independent control.** Relevant to §12: expected behaviours were checked against Python's `datetime`
   (weekdays, day differences) and a hand-written Luhn function, not against pcrec. At build the notes name the
   controls: the PCRE2+callout oracle (studies/andspike, F9), an independent Python reference evaluator
   (2026-11-12 base decisions), standards' own test vectors for library entries (2026-11-12 STANDARD LIBRARY),
   which `@assert.*` statements (§5.6) can carry inside the library file.
3. **What moves when data is regenerated.** Relevant only through `file_text`/`import` pins (§7): a changed file
   under a `sha256` pin is a loud compile error; a re-pinned file changes the emitted automaton. No table or stamp
   is introduced by this document.

## 1. Layering

**RULE.** Two layers. FOUNDATION: value kinds (§2), operators and transforms (§2), views (§3), match values and
computed labels (§4), capability levels and the reporting axis (§6), the compile-time boundary, modules and
warnings (§7). LIBRARIES, built on the foundation and changeable without it: `each`, `join`, `records`,
`file_text`, standard filters and transforms (`between`, `startsWith`, `length`, `unpad`, `pad`, `ci`), `occurs`,
`assert`, tuple comparisons, blessed callouts (§8). The ORGANISATIONAL layer (interfaces, type members, UFCS,
`types()`) is CUT from the first spec (§9); interfaces may return as library packaging after a build. Namespaces
stay in the foundation (a module is a map, §7).

**TEST OF THE RANKING.** No worked example needs the cut layer: §12 checks this case by case (E-RFC uses a plain
macro on the three fields, not an interface member).

**REASONING.** Frank: the purpose is to probe the fundamental structure; unless foundational, lower priority.
predx §9: none of thirteen further programs needed interfaces, UFCS or `types()`.

**STATUS.** Layer outline AGREED 2026-11-14 (LAYERING note). The cut: OWNER RULED 2026-11-14 (predx Q8).

## 2. Values and operators

### 2.1 Two value kinds

**RULE.** Every value is either an **rx** (a set of strings, extensional; with context, §11) or a **macro** (a term
awaiting arguments, curried by keywords). Numeric and string literals are rx: `5` = {"5"}, `"a.b"` = {"a.b"} (the
dot is literal, unlike `/a.b/`); they differ only in what a comparison means (§2.4). Conditions (`(x: <200)`),
prefix `!B`, unapplied filters, transforms and partially applied macros are macros. A value filter mentioning NO
label (`<200`, `between(3, 6)`, `startsWith("S")`) is a full rx (the set that passes); anything naming a label it
does not define is a macro awaiting the pattern that defines it. A MODULE is a map (§7), not a third kind. `@`
statements (§5.1) are statements, not values. There is no boolean type and no number type.

**REASONING.** The closure (a predicate denotes a pattern, 2026-11-12/13) means one algebra serves patterns,
values and tests; a condition is a term with a free variable, the same kind as a curried macro.

**STATUS.** LEAN (2026-11-14 fractional rx; layering item 1). Literals as one-string sets: LEAN. Module = map, not
a third kind: MANAGER LEAN 2026-11-14 (import follow-up, SUPERSEDES the namespace-as-third-kind lean). No number
type: OWNER RULED 2026-11-14 (counting: "filters, NOT a count value"). The earlier "assertions (their own value
kind)": §13 C19.

### 2.2 Operators `&`, `|`, prefix `!`

**RULE.** `&` intersection, `|` union, both EXTENSIONAL over rx operands: membership depends only on the
language, so two spellings of one language behave the same under `&`, `|`, `!`. `&` is RIGHT-ASSOCIATIVE (`a & b &
c` = `a & (b & c)`; no change for pure rx, intersection is associative; it matters only for transforms, §2.7).
Prefix `!` is ALWAYS A FILTER (a macro awaiting a target): `A & !B` = `(!B)(A)` = A minus B; `&!` is not a
separate operator. A standalone `!B` where an rx is needed (`${!B}`, `C | !B`) is the unapplied-macro error.
Filters combine pointwise by `& | !`. `!<200` is a filter; `>=200` is a full rx; they agree on every target. `!` of
a transform is an error.

Reported span (D196, RULED for pattern-level `&`): the left operand chooses (PCRE priority: first alternative,
greedy longer, lazy shorter), the right only filters which ends are admitted; the span SET is commutative.
Precedence (D196): concatenation, then `&`, then `|`. In the expression language there is no concatenation
operator (§2.5).

**REASONING.** Extensional `&` keeps arrays and rx "the same". `!` as a filter: a standalone complement is useless
in a search and VM-hostile, while under `&` it is bounded. Right associativity lets a transform on the left of `&`
scope the rest of its chain (Frank: "why not make & right associative?").

**STATUS.** `&` extensional, `!` filter: AGREED 2026-11-14. D196: RULED. Right associativity: MANAGER LEAN
2026-11-14 (pullback as pipeline). C1 (extensional set vs D196's left-chooses): OPEN, §13.

### 2.3 The unapplied-macro error

**RULE.** An unapplied macro where an rx is required is a compile error naming the fix: "filter `x: digit` has
no target; write `T & (x: digit)`". Application has three equivalent spellings for FILTERS: `x & (a: digit)`,
`(a: digit)(x)`, `each((a: digit), A)` (an alternative lacking label `a` is an error naming it). `rx & f` = `f(rx)`;
`p(x)` = `x & p` for a parameterless filter `p`. Transforms are applied only as pipeline stages (§2.7).

**STATUS.** LEAN 2026-11-14 (fractional rx + addendum). Whether `p(x)` = `x & p` survives for transforms: §13 C20.

### 2.4 Comparisons are unary sections on string sets

**RULE.** Comparisons are UNARY ONLY: `<256`, `>=lo`, `==5` denote sets, attached by `&` like everything else. A
prefix comparison takes ONE ATOM (literal, label value, binding, call, field access, parenthesized expression) and
binds tighter than `&`, `|`, `!`. The LITERAL decides the reading: `<256` = integers 0..255, `<"256"` =
lexicographic strings, `2.5` decimal, `0x100` hex. Comparisons are on the STRING SET: an integer section contains
CANONICAL numerals of VARIABLE WIDTH (the `\d+` shape: no leading zeros, sign or decimal point unless the literal
has them). Padded text is compared through the explicit `unpad` transform (§2.7; `unpad` keeps one digit, "000" ->
"0"): `/\d\d/ & between(1, 12)` is {10, 11, 12} and is WRONG for months; write `/\d\d/ & unpad & between(1, 12)`.
`between(lo, hi)` is INCLUSIVE. Decimal is exact decimal, never binary floating point.

**REASONING.** Every binary comparison is an intersection with a section. Literal-decides means declared types are
needed only where no literal fixes the reading (value vs value, §4.6). A comparison never silently reinterprets the
text: padding is a visible stage.

**STATUS.** Unary: AGREED 2026-11-14 00:10. Literals decide: AGREED 2026-11-13. String sets, `\d+` integers,
explicit `unpad`: OWNER RULED 2026-11-14 (C9, Reading A: "Integers should be \d+ to be variable width. Unpad would
be the right approach"). Exact decimal: LEAN 2026-11-12. The binary transform forms (`unpad() == 5`, `length() <
6`): superseded by §2.7.

### 2.5 No concatenation operator; arithmetic

**RULE.** The expression language has no concatenation operator: sequencing is written inside a literal
(`/${a}-${b}/`) or by `join`. `+ - * %` are arithmetic only. Value concatenation is insertion or a library name
(`concat(x, y)`).

**REASONING.** Avoids the overload trap (`"12" + "34"` = 46 or "1234"?); with no juxtaposition, a name after an
expression always starts a binding (one-token look-ahead, §5.1).

**STATUS.** LEAN 2026-11-13 (NO CONCATENATION OPERATOR).

### 2.6 Search

**RULE.** `$x ~ rx` = search inside a value (unanchored): its value is the OCCURRENCE SET under PCRE iteration
order (non-overlapping, leftmost, continue after the match; the C find-all iterator's order). `some`, `all` are
library names over a set; `s[i]` indexes occurrences (§3.2). `$x !~ rx` is a TEST: `$x & !contains(rx)`. Every
`some(s)` over the same set in one predicate denotes the SAME occurrence (two occurrences need two names).
Membership is `x & a`; no `in`.

**REASONING.** Search results are values, not globals (Frank: "Even Perl had the awkward $1"). One quantifier name
(`some`, not `any`).

**STATUS.** AGREED 2026-11-13 (SEARCH OPERATOR REVISED; SET FUNCTIONS REPLACE PROJECTIONS). `count` over a search's
occurrence set, after the counting ruling made counts filters: §13 C21. Binding a name to a test: §13 C6.

### 2.7 Transforms: pullbacks spelled as a pipeline

**RULE.** A TRANSFORM t is a finite transducer or a finite table (`unpad`, `pad(n)`, `ci`, `unquoted`, `length`,
month-name -> number, `jstr`). It PULLS A SET BACK: the strings whose t-image lies in S. One construction, regular
in, regular out (inverse image under a rational relation); a non-finite transform needs `functions`. Spelling: a
TRANSFORM ON THE LEFT OF `&` is the pullback of the rest of its chain (the mirror of "a filter on the right applies
to the target on the left"):

    x & unpad & between(1, 12)                      # x's strings whose unpadded value is 1..12
    t & pad(5) & between("09:00", "10:00")          # fixes 9:00 > 10:00 for a lexicographic compare
    msg: unquoted & contains("timeout")
    alts & !startsWith("#") & length & <=20         # raw-text tests BEFORE the transform

A transform SCOPES THE REST OF ITS CHAIN (a pipe stage); raw-text tests go before it; parentheses end its scope.
A trailing transform (`x & unpad`) is a no-op WARNING (`transform.noop`); `!transform` is an error. The
variable-width lexicographic lint suggests `pad(n)`.

**REASONING.** One mechanism collapses rev 0's transform sections, pattern -> value mappings, `jstr(p)` and the
binary forms into one closure theorem (predx S1, §8.2). The pipeline reads left to right (Frank: `unpad(between(1,
12))` is pure but reads inside out).

**STATUS.** Pullback as the mechanism: MANAGER LEAN 2026-11-14 (ADOPT; predx S1). Pipeline spelling and right
associativity: MANAGER LEAN 2026-11-14, SUPERSEDES the function forms `unpad(S)` / `length(<=20)` and the dot-view
alternative (`month.unpad: S`). The pipeline under `name:` (`month: unpad & between(1, 12)`) vs §4.1's "`name:`
takes one operand term": §13 C22.

## 3. Views

### 3.1 Array view and map view

**RULE.** An rx has two STRUCTURAL views. ARRAY view = its top-level alternatives (flat): `/a|b|c/` has 3 entries,
`/abc/` is an array of one, `/(?:a|b)|c/` has 2. MAP view = its labelled groups (a tree; nesting gives paths
`d.year`). Counts differ: `/(?<y>\d{4})-(?<m>\d\d)/` = array 1, map 2; `/(?<a>x)|(?<b>y)|z/` = array 3, map 2.
Map order = PCRE group number. A labelled alternation where each alternative is exactly one named group is the
ALIGNED case; a map literal `(x = /foo/ | y = /bar/)` IS the rx `(?<x>foo)|(?<y>bar)`, and the list form `[x =
/foo/, y = /bar/]` is the same value (`[1,3,5]` = `1|3|5`). Unlabelled entries are index-labelled. Reverse lookup
(which branch matched) is reading the accept-state label (`.index`).

**REASONING.** Frank: "Maps are the labeled groups. The interpretation between the two is different and can have
different counts"; arrays and maps are perspectives on an rx, not types.

**STATUS.** AGREED 2026-11-14 (two VIEWS; SUPERSEDES ONE TABLE CONSTRUCT and `{Jan: 1}` / `["US" => ...]`;
value-valued maps: §13 C7).

### 3.2 The four tools

**RULE.**
1. `X[...]` = POSITION in the array view only: integers, integer sets, numeric filters (`X[1]`, `X[<4]`); the
   result is always an array, keeping the ORIGINAL positions; a string or non-numeric filter inside is a compile
   error suggesting the right tool. Indexing descends (`d[1][1]`). `[0]` = the whole rx (PCRE group 0). Out of
   range = entry absent: tests on it are false. 1-based.
2. `X & f` = filter by LANGUAGE; `&` distributes over entries and empty products drop:
   `alts & !startsWith("#")` keeps passing literals; `rows & (w: >100)` keeps matching rows.
3. `where(p, X)` = filter by a compile-time STRUCTURAL property (the filtering twin of `each`); `where_group(p, X)`
   for the map view.
4. `X.name` = LABEL navigation in the map view (`A.Saturday`, `alt.repeated[1]`, module members `json.row`);
   `.name` is never digits.

**REASONING.** The output of `[]` is always an array, so `[]` uses the array view. `&` on structural properties
would intersect languages (wrong), hence `where`.

**STATUS.** AGREED 2026-11-14 (`[]` positional only). 1-based: OWNER RULED 2026-11-14 (predx Q7). Multi-index
comma `X[1,3,5]`: §13 C5.

### 3.3 Holes and groups are single entries; `|` concatenates arrays

**RULE.** Expression `|` CONCATENATES arrays (each operand contributes its top-level alternatives; appended
entries take lowest PCRE priority). An rx GROUP or a `${}` HOLE is ONE entry. With `x := /(a|b|c)/`: `x | /d/`
has 2 entries; with `x := /a|b|c/`: `x | /d/` has 4; `/${x}|d/` has 2 for either. A hole is an atom for
correctness (`/${x}d/` = `(?:a|b|c)d`). Expression parentheses are precedence only. `join` of an empty array is the
empty string.

**STATUS.** LEAN 2026-11-14 (spelling vs logic in the array view; ADD = `|`).

### 3.4 Extensional vs structural operations

**RULE.** EXTENSIONAL (`& | !`, comparisons, pullbacks) depend only on the language. STRUCTURAL (indexing, `each`,
`join`, `where`, `.label`, `enumerate`, entry counts) read the SPELLING: `/a|b/` and `/b|a/` are equal under `&` but
differ under `[1]` (and in PCRE priority). Internal rewrites (altcls, alt_normal_form) never change user-visible
structure. Field-wise narrowing that keeps other entries is structural (`each_group(&, rx, (x: d2))`), never `&`.

**STATUS.** AGREED 2026-11-14. The structural effect of `&`'s distribution over entries is unstated: §13 C17.

### 3.5 Arrays of filters and transforms

**RULE.** Closure one level up: an array of rx is an rx (alternation); an ARRAY OF FILTERS is a filter (pointwise:
`[f, g](t)` = `f(t) | g(t)`); an ARRAY OF TRANSFORMS is a transform (the union of the pullbacks). A MIXED rx/filter
array is an error (fix: write the rx entry as a filter, `(& /x/)`). Entries must share arity. `.index` keeps the
original positions when entries drop, so `ipv4 & cidrs` reports which entry admitted the match.

**REASONING.** Frank: "an array of rx is an rx. An array of filters|macros is macro?" Classification against a
table (predx §8.3 item 1) becomes `pattern & table` with no new construct.

**STATUS.** OWNER RULED 2026-11-14 (predx gaps: ARRAYS OF FILTERS).

## 4. Match values

### 4.1 `x:` constrains, `$x` reads

**RULE.** `x: S` = the set of WHOLE MATCHES whose label x is in S (a condition, a macro awaiting the pattern that
defines x). `$x` = the VALUE captured in this match (a one-string set). `x:` is ALWAYS the constrained side; `$x`
is ALWAYS a value used (operand, insertion `${$x}`, output). Capture-vs-capture is `x: <$y` (§4.6). `$x & ...`
used AS A CONDITION is an ERROR: "did you mean `x: ...`?". The left of `:` is a label PATH (`d.year: <2000`), never
an expression: a computed value is constrained through a computed label (§4.4). `name:` takes one operand term,
tighter than `&`; bigger sets need parentheses (`x: (<200 | >900)`). In a chain `P & Q & x: ...`, x is looked up in
`P & Q`; a label in both is AMBIGUOUS (error naming both); an unknown label is an error listing those available.
Call-site label arguments are sugar: `p(a: s, b: t)` = `p & (a: s) & (b: t)`.

**REASONING.** Frank: "x: represents a fraction of the search object deconstructed": the pattern is the schema, a
match a row, labels its columns, `x:` a WHERE clause. Avoids the trap that `($x & <200) & ($y & >55)` forces x = y.
ONE condition form (`label: set`) for every condition.

**STATUS.** AGREED 2026-11-14 01:00. One condition form, the left of `:` a path: OWNER RULED 2026-11-14 (predx Q6,
concept). Comma records `(x: <200, y: >55)`: §13 C8.

### 4.2 Unset labels

**RULE.** A comparison on an UNSET label is false (its `!` true); a condition naming a label that is unset for a
match fails for that match; WARN (`label.unset`) when a plain reference can be unset. This keeps extensional `&`
consistent: `(x = /\d/ | y = /[a-z]/) & (x: /[0-5]/)` = `[0-5]`.

**STATUS.** LEAN 2026-11-13 late; cited as "ruled" by a later note (§13 O3). Warning name: OWNER RULED 2026-11-14
(named warnings).

### 4.3 Repeated and duplicate labels

**RULE.** At the default level a repeated label follows the SEQUENCE RULE: `x: S` constrains ALL iterations; the
quantified forms are the `occurs` library (§8: `occurs.some(x: S)`, `occurs.exactly(n, x: S)`, ...); a bare `$x` on
a repeated label is an ERROR naming the quantified forms. At `vm`, `$x` is PCRE's last iteration (what `\k<x>`
sees). Duplicate names (`(?J)`, `(?|`): plain `$x` gives the lowest-numbered set group; the static TYPE of a
duplicate label is the UNION of the definitions that can set it. Structurally, `alt.x` returns EVERY entry labelled
x as an array in group order; `alt.x[1]` (first in the PATTERN, compile time) differs from `$x` (the MATCH's value).

**REASONING.** "All iterations" is substitution into the loop body, the only pure lowering (predx §2.1, O4); the
last-iteration rule would need captures inside a loop.

**STATUS.** Sequence rule: OWNER RULED 2026-11-14 (predx Q4), SUPERSEDES "plain `$x` = last iteration" at the
default level. `occurs`: OWNER RULED 2026-11-14 (counting; namespace name MANAGER LEAN). Duplicate labels by index
LEAN 2026-11-14; union type cited "ruled" 2026-11-14 (§13 O3).

### 4.4 Computed labels are match-dependent bindings

**RULE.** A COMPUTED LABEL is a value of the match that is not a substring. It is written as a MATCH-DEPENDENT
BINDING: a binding that reads match labels IS a computed label of the pattern whose labels it reads:

    d  := days($b) - days($a)                 # a computed label of the pattern defining a and b
    close := pair & (d: between(-15, 15))
    wd := weekday_of($rest.year, $rest.month, $rest.day)
    rfc & (wname.index: ==wd)

A mapping must be a FUNCTION (one value per text: the per-label ambiguity check), many-to-one allowed, total on its
pattern. Tabulated mappings report a constant from the accept state (§6.2); numerals by digit conversion. Values
pull back to patterns (`month(x) < 3` = `/Jan(uary)?|Feb(ruary)?/`, §2.7).

**REASONING.** Lets non-numeric layouts (month names) comply with numeric fields; a weekday or a Luhn check is a
property without a capture group. A binding instead of a keyword keeps the grammar keyword-free (§5.1).

**STATUS.** Computed labels: LEAN, foundation per the LAYERING note. Match-dependent binding as THE spelling:
MANAGER LEAN 2026-11-14 (Q6/Q9 spelling; concept OWNER RULED), SUPERSEDES the `with` placeholder (`with month =
mname.index`) and predx's `with`. Which pattern a binding attaches to when its labels occur in several: §13 O19.

### 4.5 Ambiguity

**RULE.** A label is AMBIGUOUS when two accepting parses give it different spans (decidable). At the default level
a condition on an ambiguous label passes if SOME parse passes (one automaton); a `label.ambiguous` WARNING shows a
witness, the two parses, which one PCRE chooses, the consequence and a fix where one exists. At `vm` the condition
uses PCRE's chosen parse. Library types are checked unambiguous at their labels. Every occurrence of the same
application denotes ONE parse (merged narrowing).

**REASONING.** The default level is a promise; only some-parse keeps it; for unambiguous labels the readings
coincide, so the difference is confined to exactly the patterns the warning flags (predx C11).

**STATUS.** OWNER RULED 2026-11-14 (predx Q2). Resolves C11.

### 4.6 Value-vs-value relations, priced by class count

**RULE.** A comparison between two match values (`b: >$a`, `day: (unpad & <=days_in($month, leap($year)))`,
`wname.index: ==wd`) is a RELATION, run the cheapest correct way. Its cost is the CLASS COUNT of the earlier
label(s): the number of classes the earlier labels enter the relation with (raw = |dom|; through a regular twin =
its class count). SMALL (calendar 24, state/ZIP ~50, weekday-vs-date 7, check digits 10/11) = one automaton at the
default level. LARGE (times of day 1,440: borderline; dates within 15 days: ~3.65M) = a default-level ERROR printing
the count and the fixes, or a linear arithmetic check under `functions`. UNBOUNDED (`b: >$a` over arbitrary `\d+`)
= not regular, `functions` only. The compiler computes the count BEFORE building; [COST-EXPLAIN] shows it.

**REASONING.** Turns "too large" into an explainable number; predicts E-CAL (24) vs E-NEAR (3.65M). Present it as
"a relation, run the cheapest correct way", never as "always one automaton".

**STATUS.** OWNER RULED 2026-11-14 (value-vs-value comparisons, AGREED with the class-count answer; predx S3). A
count against another label's value is such a relation (counting ruling).

## 5. Macros, bindings, statements

### 5.1 Program shape, bindings, no keywords

**RULE.** A program = bindings, expressions, calls and `@` STATEMENTS, with ONE final expression (the program's
pattern); newlines are layout (whitespace and newlines are free between expression tokens: long logic goes in `:=`
definitions, literals stay short). A binding starts `name :=`. There is ONE kind of binding: `name := expression`;
its inferred kind decides use in a hole (pattern -> sub-pattern, value -> text, filter -> guard). A binding
mentioning a match label is MATCH-DEPENDENT (a computed label, §4.4); otherwise PURE (compile time); the cost report
shows which.

NO ALPHABETIC OPERATORS OR STATEMENT KEYWORDS: a word is always a NAME (function, label, binding). There is no
`with`, `check`, `in`, `export`, `import ... as`: imports and exports are function calls (§7), assertions are
library calls (§5.6), computed values are bindings (§4.4).

BARE STATEMENTS: only `@` forms (compile-time EFFECT macros, §5.6, §7.1) may stand alone; a bare rx anywhere but
the final expression is an error ("unused pattern: bind it or make it the result"); a bare statement without `@` is
an error (it catches the unbound pattern). Pure macros cannot take `@`; effect macros cannot drop it (purity
visible and checked syntactically). `@` exists only in the expression language.

Names: symbols come only from the pattern (labels), from `:=` (bindings) or from a module (member access);
built-ins (`import`, `enumerate`, `pattern`, `some`, `all`) are reserved in CALL position only; `$&` and `$_` are
reserved scope-supplied labels; an undeclared name that is not a label is an error with a suggestion; a binding
hiding a label WARNS (`$x` still reaches the label).

**REASONING.** Frank: "no alpha operators ... with, check, in ... don't want to go into new grammar lightly". The
grammar shrinks to bindings, expressions, calls and `@` statements; the `@` mark makes compile-time effects visible.

**STATUS.** Block shape: AGREED 2026-11-13. One kind: LEAN 2026-11-13 evening. No alphabetic keywords: OWNER RULED
2026-11-14 (Q6/Q9). `@` statements, the unused-pattern and bare-statement errors: MANAGER LEAN 2026-11-14 (import
follow-up (3), on Frank's prefix suggestion). Define-before-use: §13 C12. Bare label names as values: §13 C13.

### 5.2 Macros, parameters, currying

**RULE.** `m(p1, p2) := body` makes a macro; positional parameters CONSTRUCT (`between(lo, hi) := >=lo & <=hi`,
`pair(p) := /${p},${p}/`), keyword `name =` arguments CONFIGURE (`join(a, sep = ".")`), `name:` arguments FILTER
(`isodate(year: 2000)` = `isodate & (year: 2000)`). Every labelled pattern is a macro whose label parameters are its
labels (FORWARD `isodate(x)`: text -> fields; REVERSE `isodate(year: 2000)`: a pattern; fully constrained =
formatting). Keywords CURRY: an application is a value until every required parameter is bound; rebinding one is an
error. Operators are macros (`(& B)` a curried filter). Macros expand at compile time, inlined per use; cost is per
USE. No lambda until an example needs one.

Typed parameters: `m(x: T)` narrows x by T, and the argument must lie WITHIN T; a broader or partly overlapping
argument is an error showing a dropped witness and the explicit conversion; an empty intersection from pure parts is
an ERROR; a dead branch WARNS (`dead.branch`); nothing when emptiness is match- or parameter-dependent. `m(p: pure)`
makes a match-dependent argument an error ("pass `pattern($x)`"). Built-in `pattern($x)` = the label's static
pattern.

**STATUS.** Macro bindings AGREED 2026-11-13 evening; currying AGREED 2026-11-14; `=` configure vs `:` filter:
SPELLING LEAN 2026-11-14; typed-parameter containment: LEAN 2026-11-13; `pattern()`/`pure`: LEAN 2026-11-14 00:10.
Overloading: LEAN, NOT phase one.

### 5.3 Structural macros: `each`, `each_group`, `where`, `join`

**RULE.** Macros are passable values, FENCED: compile-time only, over finite declared arrays, structural operators
only. `each(f, A)` applies f per entry, keeps labels and order, returns an array; over several arrays it ZIPS by
position (unequal lengths = error naming both counts). `each_group` zips BY LABEL. `join(a, sep = s)` concatenates
entries in declared order; `sep` is a set; joined parts stay navigable labels (`c.A: <200`, `c[1]`), free when
unread. Family: in-order fixed = `join`; in-order repeated = `list_of(X, sep = ...)`; any-order fixed = `&` of
labelled parts (JSONL); candidate sugar `any_order(a, sep = ...)`. Caller-visible captures are a library macro:
`capture(x) := /(?<${x.label}>${x})/`, `join(each(capture, a), sep = ".")`, exported like any binding (§7).

**Ordinal parameter.** The iteration ORDINAL (dense, starts at `index =`, default 1), `x.index` (original position)
and `x.label` (original name) differ once an array is sliced; the ordinal is a PARAMETER the macro declares
(`capture(x, i) := /(?<f_${i}>${x})/`); `each` passes it as the second argument when the macro takes one.

**STATUS.** LEAN 2026-11-14 (join; compose instead of an option; each's bindings). Ordinal default 1: per the
1-based ruling. Per-field constraints carrying into joined labels: §13 O5. The rev 0 `export capture(x) := ...`
keyword form is superseded by `@export` (§7).

### 5.4 The marks

**RULE.** `:=` defines a name; `=` BINDS (a label inside a map/list literal: `year = /\d{4}/`; a keyword argument:
`sep = "."`); `:` CONSTRAINS (typed parameters `x: date`, conditions `year: <2000`, sugar `isodate(year: 2000)`);
`==` is the equality section; `@` marks an effect statement.

**STATUS.** SPELLING LEAN 2026-11-14, syntax not ruled. `@`: MANAGER LEAN 2026-11-14.

### 5.5 `enumerate`

**RULE.** `enumerate(rx)` = the ARRAY of a FINITE rx's strings, in PCRE PRIORITY ORDER (leftmost alternative,
greedy before lazy), so re-joining preserves which match is reported (hence a built-in, not a library). A BUDGET
bounds it: an infinite or over-budget rx is a compile error giving the count. Uses: finite backreferences made
regular (`each(date_sep, enumerate(/[-\/.]/))`, `!contains(each(triple, enumerate(/[\x21-\x7E]/)))`), matched
delimiters (`each(q, enumerate(/["']/))`), which option matched via `.index` at the default level, per-entry
library assertions (spelling of `@each(...)` OPEN).

**REASONING.** A class is ONE alternative, so no array tool reached its members; finiteness plus a budget keeps G4.

**STATUS.** OWNER RULED 2026-11-14 ("I love it. Enumerate go." = design adoption; #6 unscheduled). Finite-group
backreferences as a GENERAL engine rule are not #6: [BACKREF-FINITE] (§11, §14).

### 5.6 Assertions (compile-time checks)

**RULE.** Compile-time assertions are LIBRARY effect calls over rx, written as `@` statements; no boolean type, no
keyword. Membership is `&` (`"2024" & leap` is {"2024"} or empty); inclusion is `A & !B` empty:

    assert := import("assert")
    @assert.some("2024" & leap)
    @assert.none("1900" & leap)
    @assert.none(octet & !/\d{1,3}/)          # every octet has 1-3 digits
    @assert.same(old, new)                     # library: both differences empty
    @assert.some(slow_errors)                  # not dead

Anonymous assertions report line + text; NAMED assertions give named failures (§13 C18 for their spelling). An
assertion the compiler cannot decide reports "can't prove: not regular" beyond the default level. Libraries carry
their standard's test vectors as assertions run at import.

**REASONING.** Language equality and inclusion are decidable (D196 add. 2's never-match/XOR fact), so the library
test rule ("tested against the standard's own vectors") becomes executable (predx S8, §8.3 item 3).

**STATUS.** Concept (compile-time assertions): OWNER RULED 2026-11-14 (Q9). Library form `assert.some` etc.: Frank
2026-11-14 (`assert := import("assert")`, `assert.some("2024" & leap)`); `@` prefix: MANAGER LEAN 2026-11-14,
SUPERSEDES `check A == B` and the `assert_some(...)` built-ins.

## 6. Capability levels and the reporting axis

### 6.1 Levels

**RULE.** Inside the predicate opt-in, the DEFAULT level promises "LINEAR, AUTOMATON CODE ONLY": linear time, no
backtracking, hostile-input safe, self-contained output. It does NOT promise one DFA pass: a relax-then-verify split
whose verify is itself an automaton over the candidate span ([PRED-SPLIT]) is inside it, and so are computations on
run-time PARAMETERS only (once per match, over a fixed-size value; comparisons against parameters compile to
parametric automata). Anything beyond is a compile error naming the construct and the option that allows it ("the
relation `d` has ~3.65M classes: add `functions`, or make the anchor a constant"), the "requires module 'X'" shape.
Opt-ins are INDEPENDENT switches, not a ladder:
- `functions`: blessed callouts on CAPTURED text (still linear, self-contained);
- `captures`: named-group SPANS in the output (§6.2);
- `vm`: full PCRE semantics (backrefs, recursion, non-DFA lookbehind);
- `eval`: runtime patterns (budgeted; links a runtime).
At the default level a REGULAR TWIN (luhn, weekday, days_in) MUST take its automaton form; too large = compile error
with the size (§4.6), never a silent switch. The planner may choose an automaton split silently (it changes only
speed); it may NOT change level silently. Plain PCRE patterns are unchanged. The cost tool's first output is the
level a program needed and why.

**`&` AT `vm` WITH A NON-REGULAR OPERAND.** The regular operands build the CANDIDATE automaton; the VM verifies the
non-regular operand on each candidate span; the reported span follows D196 ([PRED-SPLIT]).

**REASONING.** An RE2-class promise with far more expressive power (G2). Independence: a user may want
linear-time callouts without backtracking, or spans without callouts.

**STATUS.** Levels: LEAN ADOPT 2026-11-14. The promise "linear, automaton code only" (automaton split and
parameter-only computations at default; `functions` = functions over captured text): OWNER RULED 2026-11-14 (predx
Q5; resolves C14 and O9). `&` at `vm`: OWNER RULED 2026-11-14 ("the spec must state it"). Performance-trade rules:
RULED 2026-11-12. `functions` presupposes DFA captures ([ENG-TDFA]): §13 O6.

### 6.2 What a default-level program reports

**RULE.** Three outputs, three costs: (a) the match SPAN: default, free; (b) ACCEPT-CLASS values (`.index`,
computed labels with finite class counts: weekday, region, card brand, per-group classes combined at output):
default, free (a lookup on the accept state); (c) named-group SPANS (`$year` as text): the `captures` opt-in (a
tagged DFA, [ENG-TDFA], or the VM). The default output is span + accept-class values.

**STATUS.** OWNER RULED 2026-11-14 (predx Q11, S9).

## 7. The compile-time boundary, modules, traps

**RULE.**
- Structural evaluation is TOTAL over finite things and TERMINATES. Recursion through a PARAMETERIZED definition
  is admitted only when ONE integer parameter is a literal at every call after expansion and STRICTLY DECREASES at
  every recursive call, with a literal base case (`value_depth(0) := json.scalar`, §12.11); any other cycle is
  refused at load (the error names the cycle). Parameterless pattern bindings may recurse as in PCRE (`balanced :=
  /\((?:[^()]|(?&balanced))*\)/`, matched at run time, needs `vm`); labels inside recursion refused at first.
- `file_text(path, sha256 = ...)` = the whole file as one compile-time string; `records(text, rx)` = each
  compile-time match of rx over a compile-time string is an entry; named groups make entries maps. The record rx's
  matches must TILE the text (every byte in a record or a declared gap), else a compile error ("bytes 12-14
  (`\r\n`) belong to no record"); `records(text, rx, gaps = allow)` opts out. `file_literals(p)` is library sugar
  over `records` with a NAMED record rx (no hidden default). Record rx restricted to the DFA-able subset; `records`
  needs an IN-COMPILER matcher (pcrec has none today) built on [AUTOMATON-KIT].
- MODULES. `m := import(names, sha256 = ...)` is a built-in FUNCTION; `names` is a CONSTANT set of names (an rx
  over file names, e.g. `"json"`); it must resolve to EXACTLY ONE file in the CONFIGURED library directories (zero
  or several = compile error listing the candidates; a pattern from an untrusted source must not read files). It
  returns a MODULE, which is a MAP (the aligned map case) of the file's exported bindings; member access is label
  navigation (`json.row`); using a module whole as a pattern is legal only if every entry is an rx (else the
  unapplied-macro error). A library file exports with `@export(names)`: every module label whose NAME is in the rx
  `names` (`@export("leap")`, `@export(["leap", /[^_].*/])`, `@export(/[^_].*/)`); the filter must be a set of
  strings, not a target-less filter in an alternation. A library file with no export is an error ("library
  exports nothing"). Imports and file reads are COMPILE TIME ONLY (artifact self-contained), PINNED by `sha256`;
  the name -> file map and its pin live in configuration (the .rxt `include`/`lib` machinery,
  `docs/spec/rxt_format.md` §1.1.1, and [LIB]).
- THE EMPTY-MATCH HAZARD. When the program's FINAL pattern is NULLABLE and used in SEARCH mode: an ERROR in a
  predicate program, a WARNING (`empty.search`) for a program that is one plain PCRE literal (`/a*/` is legal
  PCRE). No diagnostic when anchored/whole-string (validation), when the empty string is excluded (`& !""`), or
  when opted out. The message names the empty source and the fixes. Empty ENTRIES are legal (`["", "M"]` is an
  optional part). File blank lines are covered by `records` tiling.
- SORT IS SEMANTICS: alternation order = PCRE priority (`ab|abc` vs `abc|ab` on `abcd`); `sort(alts, by = length,
  desc)` exists only as the deliberate leftmost-longest choice; `unique` keeps the first occurrence.
- Compile cost is first-order: every kernel row and prelude macro reports compile time, table size and match speed
  beside its DFA column; relation costs as class counts (§4.6); warnings only on a route change, a cap, or an
  interaction blow-up ([COST-EXPLAIN]). Prerequisites named before any build: [DFA-MIN-FAST], an
  in-construction budget, [PRED-SPLIT].

**REASONING.** G4; compile-time expansion must terminate, and a strictly decreasing literal parameter is a
syntactic termination check that admits the one legitimate default-level recursion (bounded nesting). Tiling is "no
silent defaults" for data files (the CRLF trap becomes an error). Modules as maps add no value kind; import and
export as functions over name-sets add no keyword, and one name-selection rule serves import, export and warnings.
The empty-ENTRY error rejected legitimate optional parts and missed `/\d*/`; the real hazard is a final pattern that
matches everywhere.

**STATUS.** Bounded recursion: OWNER RULED 2026-11-14 (predx Q12, low priority, one example), REFINES the 2026-11-13
RECURSION RULE NARROWED. file_text + records: LEAN 2026-11-14. Tiling: OWNER RULED 2026-11-14 (predx Q13).
Import/export as functions, module = map, `@export` filter, no-export error: MANAGER LEAN 2026-11-14 (on Frank's
proposals); import resolves to exactly one file, argument a set of names: OWNER RULED 2026-11-14 (addendum,
Frank). Empty-match rule: OWNER RULED 2026-11-14, SUPERSEDES the empty-ENTRY error and `skip_empty`. Cost
surfacing: LEAN 2026-11-13. The `trim` / `\r` trap of rev 0 is subsumed by tiling (§13 O18 RESOLVED).

### 7.1 Named warnings

**RULE.** Every warning has a STABLE NAME in dotted families (a contract, stated in the spec): `empty.search`,
`dead.branch`, `label.unset`, `transform.noop`, `compare.width`, `label.ambiguous`, `warn.unused`. Control is by
`@` effects, rest of file: `@warn.off("compare.width")`, `@warn.off(startsWith("dead."))` (a label-free value
filter is a full rx), `@warn.off(/.*/)`; the reverse `@warn.error(/.*/)` (a strict build); a per-binding form
(spelling OPEN); and a compiler option for a whole build (like `-Wno-`). SELECTORS ARE A SET OF NAMES AS AN RX, the
same name-selection rule as import and export: no `*` wildcard (`"*"` is the literal name `*`, matches nothing).
Errors cannot be disabled. An `@warn.off` that suppresses nothing raises `warn.unused` (itself suppressible).

**STATUS.** OWNER RULED 2026-11-14 (empty-match ruling: "warnings need names and the user must be able to disable
them"; amendment: "use an rx instead of wild card purely for consistency"). The list of names: manager's, recorded
on the ruling.

## 8. Libraries

**RULE.** Standard library = prelude text (typed macros) on the foundation; it grows without compiler changes.
Standard filters: `between` (inclusive), `startsWith(s) := /${s}.*/`, `endsWith`, `contains(s) := /.*${s}.*/`,
`when(c, p)` (`x & when(c, p)` = `(x & c & p) | (x & !c)`). Standard transforms (§2.7): `unpad`, `pad(n)`, `ci`,
`unquoted`, `length`, string positions `left/right/mid` with literal positions (units = characters per the
encoding mode; out-of-range: §13 O14).
- `occurs` (`occurs := import("occurs")`): filters over a repeated label's occurrences: `all`, `some`, `none`,
  `exactly(n, c)`, `at_least(n, c)`, `at_most(n, c)`; `c` is the usual `label: set` condition; FILTERS, NOT a count
  value (no number type); constant (or caller-parameter) n at default; cost = a capped counter (n+2 states)
  multiplied in, shown by [COST-EXPLAIN]; a count against another label's value is a priced relation (§4.6). Value
  comparisons (`between`, `<=`) stay purely about values.
- TUPLE COMPARISONS are a library macro, no syntax: `lex_ge([major, minor, patch], [1, 4, 0])`.
- `assert` (§5.6): `some`, `none`, `same`.
Candidate content (a follow-up initiative): network, time, identifiers, communication, checksummed numbers; each
tested against the standard's OWN vectors (as `@assert` statements), the callout oracle and the laws; each shows
its DFA column.

BLESSED CALLOUTS: emitted C text, so the artifact stays self-contained. Blessed = PURE, BOUNDED, TOTAL,
ORACLE-TESTED, and DECLARES ITS REGULAR TWIN where one exists (luhn, weekday, days_in), with its class count
(§4.6): the compiler picks automaton vs callout. First contents: numbers, dates, checksums, network, text; Unicode
normalisation deferred. The unblessed escape hatch is PCRE `(?C)`. Home: its own directory/tests/journal like
memfn/. A callout in DFA context returns a DFA-friendly verb; plain FAIL needs the VM.

**STATUS.** Standard library: AGREED as a follow-up initiative 2026-11-12. Blessed callouts: LEAN ADOPT
2026-11-14. `when`: Frank's request 2026-11-13. `occurs` family: OWNER RULED 2026-11-14 (counting, as a LIBRARY);
the namespace name `occurs`: MANAGER LEAN (name open to Frank; not `label`, which clashes with `x.label`).
Tuples as a library macro: OWNER RULED 2026-11-14, SUPERSEDES predx's tuple-on-the-left-of-`:` syntax (S12).

## 9. Cut from the first spec

**RULE.** Not in the first spec: INTERFACES (`type(...)`, `isodate: date`), TYPE MEMBERS declared with a type,
SCOPE-LIMITED UFCS (`d.weekday` resolving to a scoped macro), `types()`. Interfaces may return after a build as
LIBRARY PACKAGING (a set of required labels with value types, checked by inclusion per field, at the module export
boundary). The NO-SEMANTIC-OVERRIDE rule (two compliant formats holding one date must agree) stays as a rule for
that return. Namespaces stay (§7, a module is a map; a definition's labels are dotted paths).

**REASONING.** predx §9: none of thirteen programs needed them; UFCS adds a third resolution rule to `.`.

**STATUS.** OWNER RULED 2026-11-14 (predx Q8). SUPERSEDES rev 0 §9's interface, member, UFCS and `types()` rules.

## 10. Eval

**RULE.** `x & eval($fmt)` is a CONDITION known only at match time, opaque to analysis; the static matcher finds
candidates and eval filters them. DFA-only, the same automaton code as compile-time `records()`. Only as an
explicit MODULE ("requires module 'eval'" otherwise; the artifact declares the runtime dependency), with a BUDGET
(exhaustion is a distinct result) and a cache keyed by pattern string. The workhorse is the caller-PARAMETERISED
matcher (§11); self-describing files are a demonstration, not a driver.

**STATUS.** IDEA, late in #6 (2026-11-14 runtime eval + addendum).

## 11. The outer layer

**RULE.** The expression language is the OUTER layer: an rx is a LITERAL inside it, so a program that is just
`/(a|b)+c/` is valid and every PCRE pattern is a one-literal program (no separate PCRE mode). Top-level `:=`
replaces DEFINE for new code; DEFINE stays only as PCRE syntax inside a literal with PCRE's meaning. The predicate
opt-in selects WHICH LANGUAGE a file or API call is in. Library files are expression-language files with
`@export`. The `.rxt` format is unchanged. Crossings: rx -> expression only by `${...}`; expression -> rx only by
`/.../`.

Literals: full PCRE inside, `\/` escapes; a literal means EXACTLY what PCRE means: NO implicit extended mode
(`/foo bar/` keeps its space, `#` is literal); extended mode is per literal (`/.../x` or a leading `(?x)`). A literal
is its OWN SCOPE (numbered groups do not leak; named groups are fields of its value); NO INHERITED FLAGS; the STRICT
PURE SUBSET first (refuse `\K`, `(*ACCEPT)`, `\G`, backtracking verbs, callouts/inline code; unbounded
backreferences need `vm`). CONTEXT-MARKED SETS: a pattern denotes a set of (left context, span, right context)
triples; plain patterns ignore the contexts; `^`, `$`, `\b`, regular lookarounds constrain them; `&` intersects
triples; a label condition's value is the label's span WITH its context inside the match, so a lookbehind in a
condition's set sees the text before the label. The span of a pattern used as a SET is the strings it matches
ENTIRELY: keys starting with S are `/S.*/`.

HOLES `${expr}`: every hole denotes a SET OF STRINGS and matches one of them: a value inserts LITERAL TEXT (never
re-parsed), a pattern inserts a sub-pattern (`${isodate(year: 2000)}` = a parameterized subroutine call). In the
inner direction (an API caller passing a PCRE string) a GUARD is written with an explicit `&`: `(\d+)&${ <256 }`; a
hole after an atom WITHOUT `&` is a FOLLOWING item (`(\d+)${ <256 }` = digits followed by a numeral below 256).
Generalized backreferences (`(?<y>\d{4})-${$y + 1}`); holes are order-free; holes in typed SYNTAX POSITIONS
(`\d{${n}}`, `[${a}-${b}]`) supply that position's type from a finite set; holes never change structure seen
outside. Run-time PARAMETERS (`limit := param(/\d{1,4}/)`) are read-only per match, validated against their type,
read AS LATE AS POSSIBLE; computations on parameters only are default-level (§6.1).

**REASONING.** Making PCRE text a literal gives G3 without a mode switch; with long patterns decomposed into
bindings, free-form multi-line layout belongs to the expression language, not to literals (C2). Context-marked sets
keep G3 for lone-literal programs with lookbehind (`/(?<=\$)\d+/`) and E-JSONL's `/^${q}$/m`, and make "a name means
the same everywhere" true (predx C15/S2). The KIND of a hole decides its insertion, never the content (no
injection); a guard needs `&` so the hole rule has no exception (C4).

**STATUS.** Outer layer: LEAN ADOPT 2026-11-14. Literal leanings incl. strict subset: RULED 2026-11-13. No implicit
x-mode: OWNER RULED 2026-11-14 (C2; SUPERSEDES "the predicate opt-in implies x-mode"). Context-marked sets: OWNER
RULED 2026-11-14, TENTATIVE (predx Q1: the first target of a critic round), SUPERSEDES "value-scoped literals".
Guard holes with `&`: OWNER RULED 2026-11-14 (C4). Holes: AGREED 2026-11-13. Parameters: AGREED/LEAN 2026-11-13;
the interface rides [IFACE-PUSH]. Finite-group backreferences as regular: a general engine row, [BACKREF-FINITE]
(OWNER RULED 2026-11-14, predx Q10: not #6). `&` in inner-direction rx text: §13 C15, C23.

## 12. Worked examples (acceptance cases)

Each case: the program (placeholder spelling), the capability level it needs, and expected behaviour on a few
subjects. Subjects are searched with PCRE semantics (leftmost, then the left operand's priority) unless the program
anchors. Weekdays, day differences and Luhn results were checked with Python (`datetime.date.isoweekday`, a
hand-written Luhn), not with pcrec. Libraries are modules (`d := import("dates")`, §7). Where a field condition
holds a pipeline, the examples parenthesize it (`month: (unpad & between(1, 12))`) pending §13 C22.

### 12.1 E-JSONL: flat JSONL, date range + string match (key-order independence)

    json  := import("json")    # ws, jchar, jstr, num, value, member_any, member(k, v), row(k, v)
    dates := import("dates")
    q := json.row("ts",    json.jstr & dates.isodate & between("2024-01-01", "2024-03-31"))
       & json.row("level", json.jstr & "error")
       & json.row("msg",   json.jstr & contains("timeout"))
    /^${q}$/m

`row(k, v)` aligns one member to the member grid; `&` of three rows accepts the members in any order. `jstr` is the
JSON-string DECODING transform (§2.7): `json.jstr & p` = the JSON string literals whose decoded text is in p
(rev 0's function form `jstr(p)` is superseded). Quoted literals compare as strings; fixed-width ISO dates order
correctly that way. `^`/`$` constrain the subject's line context (§11). LEVEL: default (every binding is pure; cost
= the product of the `row` automata). Expected:
- `{"ts":"2024-02-10","level":"error","msg":"db timeout"}` -> match;
- `{"msg":"timeout","level":"error","ts":"2024-02-10"}` -> match (order independent);
- `{"ts":"2024-05-01","level":"error","msg":"timeout"}` -> no match (date out of range).
Duplicate keys: `row` holds if ANY member with that key matches. Nesting: §12.11 or `vm`.

### 12.2 E-WEEKDAY: ISO date + weekday as a computed label

    isodate := join([year  = /\d{4}/,
                     month = /\d\d/ & unpad & between(1, 12),
                     day   = /\d\d/ & unpad & between(1, 31)], sep = "-")
    weekday := weekday_of($year, $month, $day)     # match-dependent binding: a computed label of isodate
    isodate & (weekday: 6)                         # ISO numbering assumed: Monday = 1

LEVEL: default (regular: ~14 year states after the 4th digit, month as an offset mod 7, day in 7 classes; on the
order of a hundred minimal states, unmeasured); output = span + the weekday class (§6.2). Expected: `2026-11-14` ->
match (Saturday); `2026-11-13` -> no (Friday); `2024-02-29` -> no (Thursday). Weekday value type: §13 O7.

### 12.3 E-IPV4: real octet ranges

    octet := /\d{1,3}/ & between(0, 255)       # canonical numerals only: "01" excluded
    ipv4  := join([octet, octet, octet, octet], sep = ".")
    assert := import("assert")
    @assert.some("192.168.1.17" & ipv4)
    @assert.none("01.2.3.4" & ipv4)
    ipv4

LEVEL: default. Expected (whole-subject test): `192.168.1.17` in; `256.1.1.1` out; `01.2.3.4` out (canonical rule;
`unpad` admits it, a stated library choice). As a SEARCH program, `256.1.1.1` yields `56.1.1.1`; a boundary is the
user's to write. The assertions run at compile time.

### 12.4 E-LUHN: checksummed card numbers

    card := /\d{4}(?: ?\d{4}){3}/ & luhn & startsWith("4")
    card

`luhn` (weighted digit sum mod 10) is REGULAR (~20 states), a filter declaring its regular twin; IBAN mod 97 and
ISBN-10 mod 11 are the same class. The literal keeps its space (no implicit x-mode, §11; rev 0's `[ ]` rewrite is
undone). LEVEL: default. Expected: `4111 1111 1111 1111` -> match; `4111 1111 1111 1112` -> no (Luhn fails);
`5500 0000 0000 0004` -> no (Luhn valid, fails `startsWith("4")`). Whether `luhn` skips the spaces: §13 O8.

### 12.5 E-CAL: calendar validity (a relation between labels)

    isodate := (as in 12.2)
    dim   := days_in($month, leap($year))       # computed label: 24 classes (12 months x leap)
    valid := isodate & (day: (unpad & <=dim))
    @assert.some("2024-02-29" & valid)
    @assert.none("2023-02-29" & valid)
    valid

A value-vs-value relation with class count 24 (§4.6): one automaton. LEVEL: default. Expected (whole subject):
`2024-02-29` in; `2023-02-29` out; `2024-04-31` out; `2024-13-01` out (not an isodate). The notes' `month: \d\d &
between(1,12)` is WRONG (only 10, 11, 12 pass): C9 ruling, `unpad` is the fix.

### 12.6 E-RFC: weekday consistency

    month_abbrevs   := ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    weekday_abbrevs := ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    textdate := join([day = /\d{1,2}/, mname = month_abbrevs, year = /\d{4}/], sep = " ")
    month    := $mname.index                    # computed label of textdate (1-based index = month number)
    rfcdate  := join([wname = weekday_abbrevs, rest = textdate], sep = ", ")
    wd       := weekday_of($rest.year, $rest.month, $rest.day)
    rfcdate & (wname.index: ==wd)

LEVEL: default (a 7-class relation). Expected: `Sat, 14 Nov 2026` -> match; `Fri, 14 Nov 2026` -> no. The note's
`wd := weekday(rest)` assumes a member on a `date` type (cut, §9); the plain macro on the fields is this document's
rewrite. `month := $mname.index` is this document's rewrite of rev 0's `with month = mname.index` under §4.4.

### 12.7 E-NEAR: date within 15 days of another (three anchor cases)

    near_const := isodate & within(15, of = "2026-11-14")            # (a) compile-time constant
    anchor     := param(isodate)                                      # (b) caller-supplied at run time
    near_param := isodate & within(15, of = anchor)
    pair       := join([a = isodate, b = isodate], sep = /\s*,\s*/)   # (c) both dates in the subject
    d          := days($b) - days($a)
    close      := pair & (d: between(-15, 15))

(a) a 31-literal set (2026-10-30 .. 2026-11-29); LEVEL default. `2026-11-29` in, `2026-11-30` out. (b) a
computation on a parameter only (anchor +- 15 days, once per match) and a parametric comparison: LEVEL default
(§6.1). (c) a relation with ~3.65M classes (§4.6): at the default level a compile error printing the count and
naming `functions`; under `functions` a linear arithmetic check on DFA-validated candidates. `2026-11-01,
2026-11-14` -> match (13 days); `2026-11-01, 2026-12-01` -> no (30 days).

### 12.8 E-FILE: file literals and CSV records

    lines := /^[^\r\n]*$/m                                        # named record rx; no hidden default
    alts  := records(file_text("w.txt", sha256 = "<pin>"), lines)
             & !startsWith("#") & !"" & length & <=20             # raw-text tests before the transform
    rows  := records(file_text("w.csv", sha256 = "<pin>"), /^(?<word>[^,]+),(?<w>\d+)$/m)
    word_of(r) := r.word
    heavy := each(word_of, rows & (w: >100))
    alts | heavy

LEVEL: default; nothing happens at match time. Expected, with `w.txt` = `# words`, `foo`, `foobar` and `w.csv` =
`apple,150`, `pear,90`: `alts` = `foo|foobar` (file order), `heavy` = `apple`. Searching `foobarbaz` reports `foo`
(sort is semantics). Without `& !""`, a trailing newline in `w.txt` gives an empty entry, the final pattern is
nullable, and the search program is an error (`empty.search` hazard, §7). A CRLF line (`foo\r`) is now a tiling
error naming the `\r` byte, not a silently dropped line. How the `\n` terminators count as declared gaps rather than
untiled bytes: §13 O20. A changed `w.txt` under its pin is a compile error.

### 12.9 E-HTTP: header block with occurrence counts

    occurs := import("occurs")
    header := join([name = token, value = fvalue], sep = ":")    # token, fvalue as in predx §3.8
    headers := list_of(header, sep = /\r\n/)
    headers & occurs.exactly(1, name: ci("Host"))
            & occurs.at_most(1, name: ci("Content-Length"))
            & occurs.none(name: ci("Transfer-Encoding"))

`name` is a repeated label: a bare `$name` would be an error (§4.3). Each `occurs` filter is a capped counter (n+2
states: 3, 3, 2) multiplied into the loop. LEVEL: default. Expected: a block with one `Host:` line and no
`Transfer-Encoding` -> match; two `host:` lines -> no (`ci`). Spelled as the ruling spells it; `ci` as a function here vs a
pipeline transform in §2.7: §13 C24.

### 12.10 E-SEP: the same separator twice (a finite backreference, regular)

    date_sep(s) := join([year = /\d{4}/, month = /\d\d/, day = /\d\d/], sep = s)
    dates := each(date_sep, enumerate(/[-\/.]/))      # 3 entries, in PCRE priority order
    dates

LEVEL: default (PCRE's `\d{4}([-\/.])\d\d\1\d\d` needs `vm` in the strict subset). Expected: `2026-11-14` ->
match, `.index` 1; `2026/11/14` -> match, `.index` 2; `2026-11/14` -> no. Over budget (`enumerate(/\w+/)`) is a
compile error giving the count.

### 12.11 E-DEPTH: bounded recursion (JSON nested at most k deep)

    json := import("json")
    value_depth(0) := json.scalar
    value_depth(k) := json.scalar | /\[(?:${value_depth(k - 1)}(?:,${value_depth(k - 1)})*)?\]/
    value_depth(3)

`k` is a literal at every call and strictly decreases, with a literal base case (§7); objects elided. LEVEL:
default (a few hundred states for k = 3, unmeasured). `json.value` itself (unbounded recursion) needs `vm`.
Expected: `[[1]]` -> match; `[[[[1]]]]` -> the whole subject is not a `value_depth(3)` (search finds an inner
`[[[1]]]`). Defining one name by several literal-argument cases is how predx spells the base case; whether that
form is admitted generally is not stated (§13 O21).

## 13. Open questions and contradictions

Contradictions (C) are places where two notes, or a note and a ruling, give different readings; open items (O) are
places the notes leave silent or explicitly open. Each gives both readings; none is resolved here except by a
recorded ruling, cited.

RESOLVED in rev 2 (one line each; the rule now stands in the section named):
- **C2** x-mode: RESOLVED, OWNER RULED 2026-11-14 (no implicit x-mode; per-literal `(?x)`), §11.
- **C4** guard holes: RESOLVED, OWNER RULED 2026-11-14 (`(\d+)&${ <256 }`; without `&` a following item), §11.
- **C9** padded labels: RESOLVED, OWNER RULED 2026-11-14 (Reading A: string sets, `\d+`, explicit `unpad`), §2.4.
- **C10** transform sections and the left of `:`: RESOLVED, transforms as pipeline pullbacks (MANAGER LEAN
  2026-11-14) and computed values via match-dependent bindings (concept OWNER RULED 2026-11-14, Q6), §2.7, §4.4.
- **C11** purity vs ambiguity: RESOLVED, OWNER RULED 2026-11-14 (Q2: some parse at default, PCRE's at `vm`), §4.5.
- **C14** size-cap fallback: RESOLVED, OWNER RULED 2026-11-14 (Q5: an automaton verify split is default-level;
  callouts on captured text need `functions`; no silent level change), §6.1.
- **O4** `x:` on a repeated group: RESOLVED, OWNER RULED 2026-11-14 (Q4, sequence rule), §4.3.
- **O9** large run-time parameter variant set: RESOLVED, OWNER RULED 2026-11-14 (Q5: parameter-only computations
  are default-level), §6.1, §12.7 (b).
- **O11** index base: RESOLVED, OWNER RULED 2026-11-14 (Q7, 1-based), §3.2.
- **O18** `records` dropping unmatched lines: RESOLVED, OWNER RULED 2026-11-14 (Q13, tiling, `gaps = allow`), §7.

STILL OPEN from rev 0:
- **C1. `&` order.** D196 (RULED): the left operand chooses the reported end. 2026-11-14: "`&` commutes, so order is
  readability only"; `&` is extensional. Reading A: extensional = MEMBERSHIP only, reported span still left-chooses.
  Reading B: the expression language's `&` is purely a set operation and D196 governs only the reported end of a
  search. predx C1 proposes A's wording (not ruled). Right associativity (§2.2) adds: a transform operand is never
  commutable.
- **C3. DEFINE bindings in the inner direction.** 2026-11-13 evening: an opted-in DEFINE holds `name := ...` bindings.
  2026-11-14: DEFINE stays ONLY as PCRE syntax inside a literal; API callers keep the inner direction (`(\d+)&${ <256
  }`). Reading A: inner-direction patterns have holes but no bindings. Reading B: inner-direction DEFINE keeps `:=`.
- **C5. Multi-index comma.** 2026-11-14 00:10: `A[1,3,5]` NOT adopted, comma kept for `A[i, j]`; the `[]` positional
  note lists `X[1,3,5]` as valid.
- **C6. Binding a test.** 2026-11-13: binding a name to a test is an error; 2026-11-13 evening: tests sit beside
  patterns as bindings; the Q6/Q9 lean binds computed values and filters freely. Not stated as superseded.
- **C7. Value-valued maps.** 2026-11-13 `["US" => "United States"]`; 2026-11-14 views: labels are names, the value
  per branch shown is `.index`. Reading A: other values are computed labels (now bindings, §4.4) or record arrays
  (predx C7). Reading B: `=>` survives.
- **C8. Comma in records vs lists.** `[x = /foo/, y = /bar/]` = alternation; `(x: <200, y: >55)` = AND ("records remain
  as shorthand"). Same comma, opposite connectives. predx C8 proposes dropping the free-standing record (not ruled).
- **C12. Define-before-use.** 2026-11-13 BLOCK SHAPE: required; 2026-11-13 evening: forward references allowed, no
  cycles. Bounded recursion (§7) needs a self-reference at least.
- **C13. Bare label names as values.** 2026-11-13 NAME RESOLUTION: an undeclared bare name is a label; 2026-11-14
  01:00: values always `$x`. The Q6/Q9 rule ("a word is always a NAME: function, label, binding") does not say
  which in a value position; `wname.index: ==wd` uses a bare binding as a value.
- **C15. In-context vs value-scoped `&`.** PARTLY RESOLVED: context-marked sets (OWNER RULED 2026-11-14, TENTATIVE)
  replace value scoping, §11. Still open: whether `&` inside `/.../` text is rx syntax (D196's pattern-level
  operator, breaking G3 for `R&D`) or never (ERRATUM: `&` is a value operator); see C23.
- **C16. Precedence example.** D196: `&` tighter than `|`; the 00:10 example `x & <256 | >300` read as `x & ((<256)
  | (>300))`. The pullback lean restates D196 ("Fits D196 precedence"); the example is not withdrawn by a note.

NEW in rev 2 (contradictions among the 2026-11-14 rulings and leans; listed, not resolved):
- **C17. `&`'s structure.** `&` is extensional (§2.2) yet distributes over array entries and drops empty products
  (§3.2), a structural effect (`/a|b/ & /b|a/` gives [a, b] or [b, a] by which side is major). predx C17/S15
  proposes "left-major cross product"; not ruled. `.index` after `&` with an array of filters (§3.5) depends on it.
- **C18. Named assertions vs the `@` rule.** Q6/Q9 lean: named failures via `leap_1900 := assert_none(...)`; import
  lean (2): "named assertions (`leap_1900 := assert.none(...)`) remain"; import lean (3): effect macros cannot drop
  `@`, only `@` forms are bare statements. A named assertion is then either `leap_1900 := @assert.none(...)` (an
  `@` inside an expression), a binding without `@` (against (3)), or not allowed.
- **C19. The kind of an assertion.** Import lean (2): assertions are "their own value kind"; §2.1: two kinds (rx,
  macro), modules not a third kind, "no boolean type". Whether an `@` effect yields a value at all is not stated.
- **C20. Application equivalence for transforms.** §2.3: `p(x)` = `x & p` for a parameterless `p`. §2.7: `x & unpad`
  (a trailing transform) is a no-op warning, and the function form `unpad(S)` is superseded. So for a transform,
  `unpad(x)` is either an error, the image, or the pullback, and `x & unpad` is not `unpad(x)`.
- **C21. `count` as a value.** §2.6 / rev 0 §4.3: `count` is a library name over a set, `count($x)` a value. The
  counting ruling: occurrence filters, "NOT a count value (no number type)". Whether `count` over a search's
  occurrence set (`$x ~ rx`) survives as a value is not stated.
- **C22. The pipeline under `name:`.** §4.1 (01:00): `name:` takes one operand term, tighter than `&`. The pullback
  lean writes `month: unpad & between(1, 12)` and `msg: unquoted & contains("timeout")` unparenthesized, which §4.1
  parses as `(month: unpad) & between(1, 12)` (a trailing transform, then an unrelated filter).
- **C23. `&` in inner-direction rx text.** C4 ruling: the guard is `(\d+)&${ <256 }`, an `&` inside PCRE text. ERRATUM
  (2026-11-14): `&` is a value operator, not rx syntax; G3 needs `R&D` literal. Reading A: `&${` is a two-token
  marker of the inner direction only. Reading B: `&` is rx syntax in inner-direction strings.
- **C24. `ci` as a function vs a transform.** The counting ruling writes `name: ci("Host")` (a function returning a
  set); the pullback lean lists `ci` among TRANSFORMS (`& ci & ...` pipeline stages). Both cannot be the one
  spelling unless `ci(s)` is a library filter defined as `ci & s`.
- **C25. Tuple comparison arrays.** Tuples are a library macro `lex_ge([major, minor, patch], [1, 4, 0])`; but an
  array literal IS an alternation (§3.1), and the import/export discussion rejects `export([leap])` for exactly this
  ("`[leap, weekday]` = `leap | weekday`, names lost"). `[major, minor, patch]` of labels has the same problem.
- **C26. The empty-match ERROR "opted out".** §7: in a predicate program the nullable-search case is an ERROR, with
  "no diagnostic ... when opted out"; §7.1: "Errors cannot be disabled" and `empty.search` is a WARNING name. How a
  predicate program opts out of an error (other than `& !""` or anchoring) is not stated.
- **C27. Context-marked sets vs "matches ENTIRELY".** rev 0's rule `/^S/` = {"S"} (value-scoped) and S2's triples
  (`^` constrains the left context, so `x: /^S/` requires x to start a line or the subject) give different answers
  for a label condition containing an anchor. Rev 2 keeps "entirely" for the span only; the notes do not restate it.
- **C28. `occurs.all` vs the sequence rule.** §4.3: `x: S` on a repeated label already means all iterations; the
  counting ruling adds `occurs.all(x: S)`. Either they are synonyms or `x: S` on a repeated label means something
  else; not stated.

Open items (rev 0, still open):
- **O1.** The meaning of a program's final expression against the subject (search vs whole-subject test). The
  empty-match rule presupposes a SEARCH MODE chosen by the caller (predx O1 lean: the caller picks); not ruled.
- **O2.** Precedence among `!`, `:`, `.`, prefix comparisons, arithmetic and `@` is stated only pairwise (C16, C22).
- **O3.** Notes call several leanings "ruled" (unset label false, union type of duplicates, filtering by indexing).
- **O5.** Do a map's per-field value constraints carry into joined labels (asked Frank 2026-11-14; lean yes; predx:
  yes by construction).
- **O6.** `functions` presupposes DFA captures ([ENG-TDFA]); Q11 moves span REPORTING to `captures`; whether
  `functions` without TDFA pays a VM re-run per candidate is not ruled.
- **O7.** Weekday value type and numbering (`weekday == "Sat"` vs `weekday: 6`).
- **O8.** Checksum filters over separated digits (does `luhn` skip spaces?).
- **O10.** Resume after a rejecting callout for unanchored search (predx: the next DFA candidate; not ruled).
- **O12.** `!~` once `!` is a filter: keep, or drop as sugar.
- **O13.** Library files: bindings + `@export`; whether a library has a final expression (the "one final
  expression" and "unused pattern" rules, §5.1) is not stated.
- **O14.** String position out of range: CLAMP (rev 0 leaning) vs strict false (predx lean).
- **O15.** Mid-sequence placement for joined maps (`before`/`after`): deferred to a real example.
- **O16.** Group 0 find-all resume rule (`\K`-style vs lookbehind-style), cond_family.md §7 (D193 add. 5).
- **O17.** D196's remaining F7 recommendations: in-context lookaround is answered TENTATIVELY by context-marked sets;
  `\K` refused, verbs, cross-operand backrefs (finite: `enumerate`; general: [BACKREF-FINITE]), recursion remain.

Open items NEW in rev 2:
- **O19.** A match-dependent binding is "a computed label of the pattern whose labels it reads": which pattern, when
  the labels it reads occur in several bindings (`$mname` in `textdate`, reached again through `rfcdate.rest`).
- **O20.** `records` tiling: how a record rx declares its separator/gap bytes (line terminators) so that tiling
  holds without `gaps = allow`.
- **O21.** Bounded recursion's base case: several definitions of one name by literal argument (`value_depth(0) :=`)
  is predx's spelling; not stated as a general feature.
- **O22.** The per-binding `@warn.off` spelling; the `@each(...)` per-entry assertion spelling (both OPEN by ruling).
- **O23.** The `occurs` namespace name (MANAGER LEAN, open to Frank).
- **O24.** Export: the Q6/Q9 note's "look later: `export` as a binding attribute, imports as a compilation-unit
  setting" is overtaken by the function forms, which are MANAGER LEAN; the option (b) `_`-prefix convention is
  expressible as `@export(/[^_].*/)` but not a default (a library with no export is an error).
- **O25.** Q1 context-marked sets are TENTATIVE: the first target of a critic round.

## 14. Non-goals

- Non-regular nesting (balanced parentheses, unbounded JSON) stays with PCRE recursion on the VM (`vm`) or bounded
  recursion (§7); the predicate language adds no non-regular power of its own.
- No general-purpose language: no unbounded recursion through parameterized definitions, no unbounded loops, no
  lambdas until an example needs one, no side effects beyond compile-time `@` statements, no run-time compilation of
  caller-supplied PATTERNS outside `eval`, no alphabetic keywords, no boolean or number type.
- No "best match" overload ranking; no interfaces, members, UFCS or `types()` in the first spec (§9).
- No change to plain PCRE patterns outside the opt-in; class contents `[...]` keep PCRE2's meaning (synsurv).
- No spelling decision beyond the no-keyword rule (placeholder throughout); no build (#6 not scheduled; NO BUILD GO).
- Not this document: DFA captures ([ENG-TDFA]), finite-group backreferences as an engine rule ([BACKREF-FINITE],
  its own unscheduled row), the Boolean IR mechanism and lookaround lowering (D196 add. 2), the standard library's
  content, a JSON database.

## 15. Provenance

COND-FAMILY.md notes by date/heading; "11-12" = the 2026-11-12 sections, etc. "predx" = `docs/dev/lanes/predx_report.md`.

| section | notes consolidated |
|---|---|
| 0 | 11-12 base requirements; 11-13 COST METRICS; Frank 11-13 (#6 not scheduled), 11-14 (charter); goals are the manager's draft; rev 2: Q5 (G2), C2 + empty-match (G3), Q12 + enumerate (G4) |
| 1 | 11-14 LAYERING; 11-14 predx Q8 |
| 2.1-2.3 | 11-14 fractional rx + addendum; 11-14 `!`; 11-14 SUPERSEDES field-wise `&`; D196 + add. 1-2; 11-14 import follow-up (module = map); 11-14 counting (no number type); 11-14 pullback (right-assoc) |
| 2.4 | 11-13 LITERALS DECIDE; 11-14 00:10; 11-14 RULINGS on §13 (C9) |
| 2.5-2.6 | 11-13 NO CONCATENATION OPERATOR; 11-13 SEARCH notes; 11-14 00:10 |
| 2.7 | 11-14 PULLBACK spelled as a pipeline; predx S1, §8.2 |
| 3 | 11-14 00:10; views; spelling vs logic; index base; `[]` positional; 11-14 predx Q7; 11-14 predx gaps (ARRAYS OF FILTERS) |
| 4 | 11-14 01:00; 11-13 late; 11-13 DESTRUCTURING, AMBIGUITY notes, MAPPINGS; 11-14 predx Q2, Q4, Q6/Q9; 11-14 value-vs-value (cont.); predx S3; 11-14 counting |
| 5 | 11-13 BLOCK SHAPE, NAME RESOLUTION; 11-13 evening; 11-14 join, compose, curry, marks; 11-14 Q6/Q9 (no keywords, assertions); 11-14 import/export + follow-up (`@`); 11-14 predx gaps (ENUMERATE); predx S8 |
| 6 | 11-14 capability levels; 11-12 base requirements; 11-14 predx Q5, Q11; 11-14 RULINGS cont. (`&` at `vm`); predx S9, S10, §3.9 F33 |
| 7, 7.1 | 11-13 RECURSION RULE NARROWED, IMPORT, COST notes; 11-14 file_text + records; 11-14 predx Q12, Q13; predx S6, S14; 11-14 import/export + follow-up + addendum; 11-14 empty-match RULING + amendment |
| 8 | 11-12 STANDARD LIBRARY; 11-13 STRING OPERATIONS; 11-13 late; 11-14 blessed callouts; 11-14 counting; 11-14 predx gaps (TUPLE CONDITIONS); 11-14 Q6/Q9 + import (assert) |
| 9 | 11-14 predx Q8; predx §9 |
| 10 | 11-14 runtime eval + addendum |
| 11 | 11-14 outer layer, ERRATUM; 11-13 literal/hole/parameter notes; 11-14 RULINGS on §13 (C4) and RULING C2; 11-14 predx Q1, Q3, Q5, Q10; predx C15, S2 |
| 12 | rev 0 sources; rev 2 rewrites per §§2.7, 4.4, 5.6, 7; E-HTTP from 11-14 counting; E-SEP from 11-14 ENUMERATE; E-DEPTH from predx §3.9 + Q12 |
| 13 | cross-reading of all notes, D196 and the 2026-11-14 rulings (lanes predspec, predspec2) |
| 14 | 11-12 scoping; 11-13 late JSONL; D196 add. 2; synsurv; 11-14 predx Q10 |

Background documents: `cond_family.md` (the member inventory, machinery M1-M12, the checker product C3, D193
answers) is still the mechanism map the predicate language rides on. `cond_family_syntax_survey.md` predates the
2026-11-13/14 notes: its `&!` and `=~` spellings are superseded (`!` filter, `~`), its "opt-in, not default" and "do
not touch class contents" recommendations stand. Prior-art details the predx report left unverified (Pomsky,
Hyperscan) are answered in its scratch note (predx Q14); this document cites neither.
