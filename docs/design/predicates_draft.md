# The predicate language ([COND-FAMILY] #6): a preliminary specification for critical analysis

## 0. Status, goals, standing questions

**Status: DRAFT rev 0 (lane predspec, 2026-11-14). NOT a ruling, NOT scheduled** (Frank 2026-11-13: #6 not
scheduled, discussion continues). Purpose (Frank 2026-11-14): "create a preliminary predicate spec doc with our
latest ideas for the purpose of critical analysis. Provide reasoning." It consolidates the dated notes in
`docs/design/plan_row_bodies/COND-FAMILY.md` (the source of truth; the LATEST note on a topic wins). Older
background, `docs/design/cond_family.md` (survey rev 0, D193) and `docs/design/cond_family_syntax_survey.md`
(lane synsurv), is cited where still live; where it disagrees with the notes, the notes win and the section says
so. No rule here is new: every rule traces to a note (§15); where the notes are silent or disagree, §13 lists both
readings. Contradictions are listed, never resolved.

**SYNTAX IS PLACEHOLDER THROUGHOUT.** The owner rules semantics; spelling is a later design step (D193 add. 4:
owner examples are not syntax). Examples use the latest spellings in the notes: `/.../` rx literals (2026-11-14
ERRATUM: bare rx fragments are never admitted in the expression language), `:=` define, `=` bind, `:` constrain,
`==` the equality section, `[]` positional, `&` / `where` / dot for filtering and labels, 1-based indexes.

Status marks used below: **RULED** (a D-number or Frank's explicit acceptance), **AGREED** (Frank proposed or
accepted in discussion, no D-number), **LEAN** (manager's leaning, not yet answered), **OPEN** (§13).

### Goals (MANAGER DRAFT, not yet seen by the owner; ranked, highest wins a conflict)

| # | goal | who benefits | checkable form |
|---|---|---|---|
| G1 | EXPRESSIVENESS over the string: conditions PCRE cannot state (cross-label arithmetic, checksums, calendar validity, key-order independence, computed properties) are short programs | users writing validators, filters, log/JSONL searches | every §12 acceptance case is written in at most ~6 definitions with no construct outside §§2-8 |
| G2 | PURE-DFA GUARANTEE BY DEFAULT: a program that compiles at the default level runs as one automaton (linear time, no backtracking, hostile-input safe, self-contained output) | anyone matching untrusted input; embedders | every default-level §12 case compiles to the DFA engine (`RX_ENGINE` stamp); anything else is a compile error naming the construct and the opt-in, never a silent route change |
| G3 | PCRE COMPATIBILITY: every PCRE pattern is a valid one-literal program with PCRE's meaning | existing PCRE users; the corpus | the whole `.rxt` corpus, each pattern wrapped as `/.../`, answers identically to today (see §13 Q1: x-mode currently breaks this) |
| G4 | STRUCTURE IS COMPILE-TIME ONLY, TOTAL, TERMINATING: every structural evaluation (each, join, records, indexing, imports) is finite and ends | the compiler's users (no hang at build), the security story | no recursion through parameterized definitions (checked acyclic); every structural operator ranges over finite declared things; a fuzzer over programs never hangs the compiler (watchdog) |

Non-goals: §14. Priority G1 > G2 > G3 > G4 is the manager's draft order; G2 vs G1 conflicts (a condition that
is expressible but not regular) resolve by the capability levels (§6), not by dropping G1.

### Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** Mostly not relevant: a language spec introduces no measured quantity. The one
   number cited (ISO date with leap Feb 29 as a plain regex: 6,848 B object, 5.9 ms compile, all 4-digit years;
   6,376 B for 2000-2099; COND-FAMILY 2026-11-13 "COST METRICS") is a compile-time size on the Linux dev box;
   any cost table a build produces must name its regime then.
2. **The independent control.** Relevant to §12: expected behaviours were checked against Python's `datetime`
   (weekdays, day differences) and a hand-written Luhn function in this lane, not against pcrec. At build the
   notes name the controls: the PCRE2+callout oracle (studies/andspike, F9), an independent Python reference
   evaluator (2026-11-12 base decisions), standards' own test vectors for library entries (2026-11-12 STANDARD
   LIBRARY).
3. **What moves when data is regenerated.** Relevant only through `file_text`/`import` pins (§7): a changed
   file under a `sha256` pin is a loud compile error; a re-pinned file changes the emitted automaton. No table
   or stamp is introduced by this document.

## 1. Layering

**RULE.** Three layers. FOUNDATION: value kinds (§2), operators (§2), views (§3), match values (§4),
capability levels (§6), the compile-time boundary (§7). LIBRARIES, built on the foundation and changeable
without it: `each`, `join`, `records`, `file_text`, standard filters (`between`, `startsWith`, `length`), blessed
callouts (§8). ORGANISATIONAL, on which nothing below depends: interfaces, type members, namespaces, dot
resolution / UFCS, `types()` (§9). Value types and computed labels go with the core; interfaces wait for after a
first build.

**TEST OF THE RANKING.** No worked example needs the organisational layer: Luhn, calendar, JSONL, IPv4 need
foundation + library filters; date distance needs the `functions` level; RFC weekday needs computed labels only.
§12 checks this case by case (it holds for E-RFC only when `weekday` is called as a plain macro on the three
fields, not as an interface member: §12.6).

**REASONING.** Frank: the purpose is to probe the fundamental structure; unless foundational, lower priority. A
layer that no acceptance case needs can be cut or postponed without rewriting the base.

**STATUS.** AGREED outline, 2026-11-14 LAYERING note ("the outline #6's design document starts from").

## 2. Values and operators

### 2.1 Two value kinds

**RULE.** Every value is either an **rx** (a set of strings, extensional) or a **macro** (a term awaiting
arguments, curried by keywords). Numeric and string literals are rx: `5` = {"5"}, `"a.b"` = {"a.b"} (the dot is
literal, unlike `/a.b/`); they differ only in what a comparison means (§2.4). Conditions (`(x: <200)`), prefix
`!B`, unapplied filters and partially applied macros are macros. A value filter mentioning NO label (`<200`,
`between(3, 6)`, `startsWith("S")`) is a full rx (the set that passes); anything naming a label it does not define
is a macro awaiting the pattern that defines it.

**REASONING.** The closure (a predicate denotes a pattern, 2026-11-12/13) means one algebra serves patterns,
values and tests; the 2026-11-14 "fractional rx" note found that a condition is not a partial rx but a term with
a free variable, the same kind as a curried macro, so two kinds suffice.

**STATUS.** LEAN (2026-11-14 fractional rx; layering item 1). Literals as one-string sets: LEAN (2026-11-14
00:10).

### 2.2 Operators `&`, `|`, prefix `!`

**RULE.** `&` intersection, `|` union, both EXTENSIONAL: membership depends only on the language, so two
spellings of one language behave the same under `&`, `|`, `!`. Prefix `!` is ALWAYS A FILTER (a macro awaiting
a target): `A & !B` = `(!B)(A)` = A minus B; `&!` is not a separate operator. A standalone `!B` where an rx is
needed (`${!B}`, `C | !B`) is the unapplied-macro error. Filters combine pointwise by `& | !`. `!<200` is a
filter; `>=200` is a full rx; they agree on every target. De Morgan and double negation are ordinary rewrites.

Reported span (from D196, RULED for pattern-level `&`): the left operand chooses (PCRE priority: first
alternative, greedy longer, lazy shorter), the right only filters which ends are admitted; the span SET is
commutative. Precedence (D196): concatenation, then `&`, then `|`. In the expression language there is no
concatenation operator (§2.5).

**REASONING.** Extensional `&` keeps arrays and rx "the same" (Frank: he would rather say `(a: ...)` is not a map
or an rx than give up that consistency). `!` as a filter: a standalone complement is useless in a search (`!abc`
matches nearly every string) and VM-hostile, while under `&` it is bounded. One `!` in both languages replaces
the earlier `&!`-only family (Frank: "consistency... a hobgoblin to good design").

**STATUS.** `&` extensional: AGREED 2026-11-14 (SUPERSEDES field-wise `&`). `!`: AGREED 2026-11-14 (SUPERSEDES
"shared operators `&`, `&!`, `|`" and the 2026-11-13 "negation relative to the type" note). D196: RULED. Tension
between extensional `&` and D196's asymmetric reported end, and the 2026-11-14 remark "`&` commutes, so order is
readability only": §13 C1. The synsurv survey's `&!` recommendation (its item 7) is superseded.

### 2.3 The unapplied-macro error

**RULE.** An unapplied macro where an rx is required is a compile error naming the fix: "filter `x: digit` has
no target; write `T & (x: digit)`"; the same error for an unapplied `capture(prefix = ...)`. Application has three
equivalent spellings: `x & (a: digit)`, `(a: digit)(x)`, `each((a: digit), A)` (an alternative lacking label `a`
is an error naming it). `rx & f` = `f(rx)`; `p(x)` = `x & p` for a parameterless `p`.

**REASONING.** Makes the kind boundary visible at compile time rather than producing an empty or universal set.

**STATUS.** LEAN 2026-11-14 (fractional rx + addendum).

### 2.4 Comparisons are unary sections; literals decide

**RULE.** Comparisons are UNARY ONLY: `<256`, `>=lo`, `==5` denote sets, attached by `&` like everything else. A
prefix comparison takes ONE ATOM (literal, label value, call, field access, parenthesized expression) and binds
tighter than `&`, `|`, `!`; a compound operand needs parentheses (`<($end - 1)`). The LITERAL decides the
reading: `<256` = canonical integers 0..255 (int generator), `<"256"` = lexicographic strings, `2.5` decimal,
`0x100` hex. Comparison sets contain CANONICAL numerals only (no leading zeros, sign or decimal point unless the
literal has them); `unpad` is the explicit transform for padded text (`unpad` keeps one digit, "000" -> "0").
`between(lo, hi)` is INCLUSIVE. Decimal is exact decimal, never binary floating point.

**REASONING.** Every binary comparison is an intersection with a section, including capture-vs-capture
(`start: <$end`) and arithmetic; the precedence rule "comparisons bind between concatenation and `&`" disappears.
Literal-decides means declared types are needed only where no literal fixes the reading (value vs value). Exact
decimal keeps generator, evaluator and oracle in agreement by construction.

**STATUS.** Unary: AGREED 2026-11-14 00:10. Literals decide: AGREED 2026-11-13 (REFINES the declared-type
overloading note). Canonical rule, `unpad`: LEAN 2026-11-14 00:10. Exact decimal: LEAN 2026-11-12. Spellings of
transform sections disagree across notes (`unpad() == 5`, `length() < 6`, `length(<=20)`): §13 C10.

### 2.5 No concatenation operator; arithmetic

**RULE.** The expression language has no concatenation operator: sequencing is written inside a literal
(`/${a}-${b}/`) or by `join`. `+ - * %` are arithmetic only. Value concatenation is insertion or a library name
(`concat(x, y)`).

**REASONING.** Keeps layers clean and avoids the overload trap (`"12" + "34"` = 46 or "1234"?); with no
juxtaposition, a name after an expression always starts a binding (one-token look-ahead, §5.1).

**STATUS.** LEAN 2026-11-13 (NO CONCATENATION OPERATOR).

### 2.6 Search

**RULE.** `$x ~ rx` = search inside a value (unanchored): its value is the OCCURRENCE SET under PCRE iteration
order (non-overlapping, leftmost, continue after the match; the C find-all iterator's order). `some`, `all`,
`count` are library names over a set; `s[i]` indexes occurrences (§3.2). `$x !~ rx` is a TEST (no occurrence):
`$x & !contains(rx)`; binding a name to a test was an error (2026-11-13; contradicted, §13 C6). Every `some(s)`
over the same set in one predicate denotes the SAME occurrence (two occurrences need two names). `some` over a
static array is the array (redundant); `all` is the intersection of its branches. Membership is `x & a`; no `in`.

**REASONING.** Search results are values, not globals (Frank: "Even Perl had the awkward $1"). `~` is free
because complement is `!`; awk/PostgreSQL precedent. One quantifier name (`some`, not `any`: "any" means some or
all by context).

**STATUS.** AGREED 2026-11-13 (SEARCH OPERATOR REVISED; SET FUNCTIONS REPLACE PROJECTIONS, SUPERSEDING `.some`/`.all`
projections and the separate binder).

## 3. Views

### 3.1 Array view and map view

**RULE.** An rx has two STRUCTURAL views. ARRAY view = its top-level alternatives (flat): `/a|b|c/` has 3 entries,
`/abc/` is an array of one, `/(?:a|b)|c/` has 2. MAP view = its labelled groups (a tree; nesting gives paths
`d.year`). Counts differ: `/(?<y>\d{4})-(?<m>\d\d)/` = array 1, map 2; `/(?<a>x)|(?<b>y)|z/` = array 3, map 2.
Map order = PCRE group number. A labelled alternation where each alternative is exactly one named group is the
ALIGNED case (both views count alike); a map literal `(x = /foo/ | y = /bar/)` IS the rx `(?<x>foo)|(?<y>bar)`,
and the list form `[x = /foo/, y = /bar/]` is the same value (`[1,3,5]` = `1|3|5`). Unlabelled entries are
index-labelled. Map/array keyed by index carries a label per branch = an accept-state label (the classification
machinery), so reverse lookup (which branch matched) is reading that label (`.index`).

**REASONING.** Frank: "Maps are the labeled groups. The interpretation between the two is different and can have
different counts"; arrays and maps are perspectives on an rx, not types. One object, two decompositions, avoids
a separate table/tuple type (`join` takes an ordinary array).

**STATUS.** AGREED 2026-11-14 (arrays vs maps are two VIEWS; SUPERSEDES the 2026-11-13 ONE TABLE CONSTRUCT and the
00:10 "array IS a labelled alternation" spellings `{Jan: 1}` / `["US" => ...]`; value-valued maps: §13 C7).

### 3.2 The four tools

**RULE.**
1. `X[...]` = POSITION in the array view only: integers, integer sets, numeric filters (`X[1]`, `X[1,3,5]`,
   `X[<4]`); the result is always an array, keeping the ORIGINAL positions (renumbering is an explicit
   function); a string or non-numeric filter inside is a compile error suggesting the right tool. Indexing
   descends: `d := /(a|b|c)|d/` gives `d[1]` = `(a|b|c)`, `d[1][1]` = `/a/`, `d[2]` = `/d/`. `[0]` = the whole rx
   (PCRE group 0). Out of range = entry absent: tests on it are false.
2. `X & f` = filter by LANGUAGE; `&` distributes over entries and empty products drop:
   `alts & !startsWith("#")` keeps passing literals; `rows & (w: >100)` keeps matching rows.
3. `where(p, X)` = filter by a compile-time STRUCTURAL property (the filtering twin of `each`); `where_group(p, X)`
   for the map view: `where(has_member(weekday), types(isodate))`, `where_group(label: startsWith("S"), A)`.
4. `X.name` = LABEL navigation in the map view (`A.Saturday`, `alt.repeated[1]`); `.name` is never digits
   (`A.4` reads as a decimal; write `A[4]`).

**REASONING.** The output of `[]` is always an array, so `[]` uses the array view; a type-dependent `[]` breaks on
`[1, 2, "fire", startsWith("S")]`. `&` on types arrays would intersect languages (wrong), hence `where`.

**STATUS.** AGREED 2026-11-14 (`[]` positional only; SUPERSEDES `A["Saturday"]`, `A[startsWith("S")]`,
`file_literals(...)[!startsWith("#")]`, `rows[r.w: >100]`, `types(isodate)[has_member(weekday)]`). 1-based: LEAN
2026-11-14 (index base; SUPERSEDES `/a|b|c/[1]` = `/b/` and the `each` ordinal default 0). `X[1,3,5]` contradicts
the 00:10 note keeping the comma for `A[i, j]`: §13 C5.

### 3.3 Holes and groups are single entries; `|` concatenates arrays

**RULE.** Expression `|` CONCATENATES arrays (each operand contributes its top-level alternatives; appended
entries take lowest PCRE priority). An rx GROUP or a `${}` HOLE is ONE entry. With `x := /(a|b|c)/`: `x | /d/`
has 2 entries; with `x := /a|b|c/`: `x | /d/` has 4 (= `/a|b|c|d/`); `/${x}|d/` has 2 for either. A hole is an
atom for correctness (`/${x}d/` = `(?:a|b|c)d`). Expression parentheses are precedence only, never structure
(`(x) | /d/` is still 4). `join` of an empty array is the empty string (not the empty set).

**REASONING.** The two crossings give both choices: merge entries in the expression language, nest as one entry
by crossing into rx text. Append-at-end = lowest priority makes position and meaning agree.

**STATUS.** LEAN 2026-11-14 (spelling vs logic in the array view; ADD = `|`).

### 3.4 Extensional vs structural operations

**RULE.** EXTENSIONAL (`& | !`, comparisons) depend only on the language. STRUCTURAL (indexing, `each`, `join`,
`where`, `.label`, `count` of entries) read the SPELLING: `/a|b/` and `/b|a/` are equal under `&` but differ under
`[1]` (and in PCRE priority). Internal rewrites (altcls, alt_normal_form) never change user-visible structure.
Field-wise narrowing that keeps other entries is structural (`each_group(&, rx, (x: d2))`), never `&`.

**REASONING.** Without the split, an optimizer rewrite could change a program's answer through indexing.

**STATUS.** AGREED 2026-11-14.

## 4. Match values

### 4.1 `x:` constrains, `$x` reads

**RULE.** `x: S` = the set of WHOLE MATCHES whose label x is in S (a condition, a macro awaiting the pattern that
defines x). `$x` = the VALUE captured in this match (a one-string set, so every operator applies). `x:` is ALWAYS
the constrained side; `$x` is ALWAYS a value used (operand, insertion `${$x}`, output). Capture-vs-capture is
`x: <$y`. `$x & ...` used AS A CONDITION (top-level whole-match `&`, a guard hole) is an ERROR: "did you mean
`x: ...`?". The left of `:` may be a PATH (`d.year: <2000`). `name:` takes one operand term, tighter than `&`;
bigger sets need parentheses (`x: (<200 | >900)`). In a chain `P & Q & x: ...`, x is looked up in `P & Q`; a
label in both is AMBIGUOUS (error naming both); an unknown label is an error listing those available. Call-site
label arguments are sugar: `p(a: s, b: t)` = `p & (a: s) & (b: t)`.

Conditions over several labels combine with ordinary operators:
`/(?<x>\d+),(?<y>\d+)/ & (x: <200 & y: >55 | x: <100 & y: >20)`.

**REASONING.** Frank: "x: represents a fraction of the search object deconstructed": the pattern is the schema, a
match a row, labels its columns, `x:` a WHERE clause. Avoids the trap that `($x & <200) & ($y & >55)` intersects x's
value with y's (forcing x = y). The `$x` vs `x:` threshold (Frank: "a cognitive threshold") is lowered by RULE:
the trap cannot be written. Each `x: S` with constant S is a static constraint on its group, so the whole
condition is one automaton (a union of products), no VM, no callout: only genuine capture-vs-capture is
match-dependent.

**STATUS.** AGREED 2026-11-14 01:00 (atoms SUPERSEDE comma records as the main form; records "remain as
shorthand", §13 C8). Dot = which part, colon = constrain: AGREED (jq-style juxtaposition not adopted). Purity
claim holds only for unambiguous labels: §13 C11.

### 4.2 Unset labels

**RULE.** A comparison on an UNSET label is false (its `!` true); `some` over no occurrences is false, `all` true;
a record/condition naming a label that is unset for a match fails for that match; WARN when a plain reference can
be unset. This keeps extensional `&` consistent: `(x = /\d/ | y = /[a-z]/) & (x: /[0-5]/)` = `[0-5]`, the same as
the language intersection.

**STATUS.** LEAN 2026-11-13 late; cited as "ruled" by the 2026-11-14 SUPERSEDES note (status discrepancy, §13 O3).

### 4.3 Repeated and duplicate labels

**RULE.** Plain `$x` follows PCRE exactly (what `\k<x>` sees): a repeated group gives its LAST iteration;
duplicate names (`(?J)`, `(?|`) give the lowest-numbered set group. `some($x)`, `all($x)`, `count($x)`, `$x[i]`
range over EVERY occurrence (each iteration of each participating definition, match order). WARN when plain `$x`
can hold more than one occurrence. The static TYPE of a duplicate label is the UNION of the definitions that can
set it (`(?<a>\d)|(?<a>[a-z])`: `\d|[a-z]`). Structurally, `alt.x` returns EVERY entry labelled x as an array in
group order (a unique label gives an array of one = the rx itself); `alt.x[1]` (first in the PATTERN, compile
time) differs from `$x` (the MATCH's value) when the first did not participate.

**STATUS.** LEAN 2026-11-13 late; duplicate labels by index LEAN 2026-11-14; union type cited "ruled" 2026-11-14.

### 4.4 Value types and computed labels

**RULE.** A label may carry a VALUE TYPE (number via the canonical numeral; "07" complies with `number` via
canonical `unpad`). A COMPUTED LABEL is a field that is not a substring: a pattern -> value mapping of the match
(an accept-state label). `textdate := join([...]) with month = mname.index`: the 1-based array index of the
matched month name IS the month number. Values pull back to patterns (`month(x) < 3` = `/Jan(uary)?|Feb(ruary)?/`);
a mapping must be a FUNCTION (one value per text: the per-label ambiguity check), many-to-one allowed, total on its
pattern. Tabulated mappings report a constant from the accept state; numerals by digit conversion.

**REASONING.** Lets non-numeric layouts (month names) comply with numeric fields; a weekday or Luhn check digit is
a property without a capture group (2026-11-13 late: day of week as a computed property).

**STATUS.** Value types + computed labels: LEAN, foundation per the LAYERING note. Mapping rules: LEAN 2026-11-13
(PATTERN -> VALUE MAPPINGS). The `with` keyword is a placeholder (from the interfaces note); whether value types
change what `between(1,12)` means on a `\d\d` label: §13 C9.

### 4.5 Ambiguity

**RULE.** A label is AMBIGUOUS when two accepting parses give it different spans (decidable). Narrowing gives "SOME
parse passes"; capture-then-test gives "the parse PCRE CHOOSES passes" (VM). Library types are checked unambiguous
at their labels (fast path always); an ambiguous user label takes PCRE's chosen parse, reported. Every occurrence
of the same application denotes ONE parse (merged narrowing). A warning SHOWS a witness, the two parses, which one
PCRE chooses, the consequence and a fix where one exists; the explain listing can say why an expected-ambiguous
label is not ambiguous.

**STATUS.** LEAN 2026-11-13 (DESTRUCTURING, AMBIGUITY EXPLAINED, AMBIGUITY WARNINGS MUST BE HELPFUL). Interaction
with the pure-DFA default: §13 C11.

## 5. Macros

### 5.1 Program shape and bindings

**RULE.** A program (or block) = bindings + ONE final expression; several conditions combine with `&`. A binding
starts `name :=`; newlines are layout. There is ONE kind of binding: `name := expression`; its inferred type
decides use in a hole (pattern -> sub-pattern, value -> text, test -> guard). A binding mentioning a match label is
MATCH-DEPENDENT (evaluated per match); otherwise PURE (compile time); the cost report shows which. No `:=` inside
holes. Symbols come only from the pattern (labels) or from `:=` (bindings); built-ins (`some`, `all`, `count`,
`import`, `pattern`, `types`) are reserved in CALL position only; `$&` and `$_` are reserved scope-supplied labels;
an undeclared name that is not a label is an error with a suggestion; a binding hiding a label WARNS (`$x` still
reaches the label).

**STATUS.** Block shape: AGREED 2026-11-13. One kind: LEAN 2026-11-13 evening. NAME RESOLUTION: Frank's rules
2026-11-13 (SUPERSEDE the $-sigil note's "any value" meaning). Define-before-use vs forward references: §13 C12.
Bare label names as values after the `x:`/`$x` split: §13 C13.

### 5.2 Macros, parameters, currying

**RULE.** `m(p1, p2) := body` makes a macro; positional parameters CONSTRUCT (`between(lo, hi) := >=lo & <=hi`,
`pair(p) := /${p},${p}/`), keyword `name =` arguments CONFIGURE (`join(a, sep = ".")`), `name:` arguments FILTER
(`isodate(year: 2000)` = `isodate & (year: 2000)`). Every labelled pattern is a macro whose label parameters are its
labels (FORWARD `isodate(x)`: text -> fields; REVERSE `isodate(year: 2000)`: a pattern; fully constrained =
formatting). Keywords CURRY: an application is a value until every required parameter is bound; keywords bind in
any order across partial applications; rebinding one is an error (`capture(prefix = "f_")` awaits its subject;
`<200`, `between(3, 6)` are such partial applications). Operators are macros (`&` as a value is two-argument
intersection; `(& B)` a curried filter). Macros expand at compile time, inlined per use; cost is per USE. No lambda
until an example needs one (named macros + currying cover every example so far).

Typed parameters: `m(x: T)` narrows x by T, and the argument must lie WITHIN T (the type removes nothing); a
broader or partly overlapping argument is an error showing a dropped witness and the explicit conversion to write
(`right(year, 2)`, `j & /\d\d/`); an empty intersection from pure parts is an ERROR; a dead branch WARNS; nothing
when emptiness is match- or parameter-dependent or a part has no exact automaton. Shape types (`/\d\d/`) differ from
value types (`<100`); the diagnostic notices "values fit, shape does not". `m(p: pure)` makes a match-dependent
argument an error ("pass `pattern($x)`"). Built-in `pattern($x)` = the label's static pattern (pure; inner groups as
fields; a group referring outside itself is "not self-contained").

**REASONING.** Application and typing are both intersection (Frank: `m(x: d2) := x & d2 & m` read as a DEFINITION
OF MEANING). Contract over silent filter (Frank: "We could just say the type must equal"; manager's adjustment
"within", since strict equality rejects natural narrower arguments and no conversion can widen).

**STATUS.** Macro bindings AGREED 2026-11-13 evening; currying AGREED 2026-11-14 ("Keywords to macros basically
curry the rx function"); `=` configure vs `:` filter: SPELLING LEAN 2026-11-14 (binding vs constraining marks,
SUPERSEDES `sep: "."`); typed-parameter containment: LEAN 2026-11-13; `pattern()`/`pure`: LEAN 2026-11-14 00:10.
Overloading (disjoint types, per-string dispatch): LEAN, NOT phase one (2026-11-13 evening; SUPERSEDES the
2026-11-12 resolve-by-declared-type note).

### 5.3 Structural macros: `each`, `each_group`, `where`, `join`

**RULE.** Macros are passable values, FENCED: compile-time only, over finite declared arrays, structural operators
only (each, join, maybe a fold), no recursion. `each(f, A)` applies f per entry, keeps labels and order, returns an
array; over several arrays it ZIPS by position (unequal lengths = error naming both counts). `each_group` zips BY
LABEL (a label in only one input = error; `unmatched = keep` only on a real example). `where`/`where_group`: §3.2.
`join(a, sep = s)` concatenates entries in declared order; `sep` is a set (a literal string auto-escaped, or a
pattern); joined parts stay navigable labels (`c.A: <200`, `c[1]`), free when unread. Family: in-order fixed =
`join`; in-order repeated = `list_of(X, sep = ...)`; any-order fixed = `&` of labelled parts (JSONL); candidate
sugar `any_order(a, sep = ...)`. No `prefix`/`suffix` keywords. Exporting caller-visible captures is a library
function, not an option: `export capture(x) := /(?<${x.label}>${x})/`, `join(each(capture, a), sep = ".")`;
`${x.label}` in a group-name position is a compile-time splice that must yield a valid PCRE name.

**Ordinal parameter.** Three values differ once an array is sliced: the iteration ORDINAL (dense, starts at
`index =`, default 1), `x.index` (original position) and `x.label` (original name). Element facts stay on the
element; the ordinal is a PARAMETER the macro declares (`capture(x, i) := /(?<f_${i}>${x})/`); `each` passes it as
the second argument when the macro takes one; the function argument must be one argument short (two with the
ordinal), checked at compile time. A numeral spliced into a name is canonical.

**STATUS.** LEAN 2026-11-14 (join; compose instead of an option, DROPPING `group:`; each's bindings; piecewise via
each). Ordinal default 1: SUPERSEDED from 0 by the index-base note. Whether a map's per-field value constraints carry
into joined labels: OPEN, asked Frank (§13 O5).

### 5.4 The marks

**RULE.** `:=` defines a name; `=` BINDS (a label inside a map/list literal: `year = /\d{4}/`; a keyword argument:
`sep = "."`); `:` CONSTRAINS (typed parameters `x: date`, `type(year: number)`, conditions `year: <2000`, sugar
`isodate(year: 2000)`); `==` is the equality section.

**REASONING.** `name: value` was doing three jobs (label definition, condition, keyword argument), making
`(x: /foo/ | y: /bar/)` ambiguous (labelled alternation vs two OR-ed conditions). Reading payoff: `f(sep = ".")`
configures, `isodate(year: 2000)` filters.

**STATUS.** SPELLING LEAN 2026-11-14, syntax not ruled (SUPERSEDES `sep:`, `index:`, `skip_empty:`, `trim:`,
`sha256:`, `of:` keyword spellings in earlier notes; this document rewrites them with `=`).

## 6. Capability levels

**RULE.** Inside the predicate opt-in, the DEFAULT level is PURE AUTOMATON: linear time, no backtracking,
hostile-input safe, self-contained output. Anything beyond it is a compile error naming the construct and the
option that allows it ("`days($b) - days($a)` needs match-time functions: add `functions`, or make the anchor a
constant"), the "requires module 'X'" contract shape. Opt-ins are INDEPENDENT switches, not a ladder:
- `functions`: blessed callouts on DFA captures (still linear, self-contained);
- `vm`: full PCRE semantics (backrefs, recursion, non-DFA lookbehind);
- `eval`: runtime patterns (budgeted; links a runtime).
`functions` does not imply `vm`. At the default level a REGULAR TWIN (luhn, weekday, days_in) MUST take its
automaton form; too large = compile error with the size, suggesting `functions` (never a silent switch). Plain PCRE
patterns are unchanged. The cost tool's first output is the level a program needed and why.

**REASONING.** An RE2-class promise with far more expressive power (G2); every language item carries a declared
DFA-capable column and "I'd want to know if a feature dropped this requirement" (Frank 2026-11-12 base
requirement 2). Independence: a user may want linear-time callouts without backtracking.

**STATUS.** LEAN ADOPT 2026-11-14 (capability levels; Frank's idea "a predicate version, perhaps the default, that is
PURE DFA"). Base requirement "DFA capable" + notification: AGREED 2026-11-12. Performance-trade rules (never trade
correctness; zero cost when unused; a slower route only where no proved faster one exists, visible and filed):
RULED 2026-11-12 ("Agree with deliberate definition"). `functions` presupposes DFA captures ([ENG-TDFA], a SEPARATE
initiative per 2026-11-12 scoping): §13 O6. Conflict with the earlier stamped size-cap fallback and [PRED-SPLIT]'s
automatic demotion: §13 C14.

## 7. The compile-time boundary

**RULE.**
- Structural evaluation is TOTAL over finite things and TERMINATES: no cycle through a PARAMETERIZED definition
  (checked acyclic at load; the error names the cycle); parameterless pattern bindings may recurse as in PCRE
  (`balanced := /\((?:[^()]|(?&balanced))*\)/`, matched at run time, needs `vm` as non-regular); labels inside
  recursion refused at first.
- `file_text(path, sha256 = ...)` = the whole file as one compile-time string; `records(text, rx)` = each
  compile-time match of rx over a compile-time string is an entry; named groups make entries maps.
  `file_literals(p)` is library sugar `records(file_text(p), lines)` where `lines` is a NAMED record rx (no hidden
  default: blank lines and `\r` are decided by the chosen rx). Record rx restricted to the DFA-able subset;
  `records` needs an IN-COMPILER matcher (pcrec has none today) built on [AUTOMATON-KIT].
- Imports and file reads are COMPILE TIME ONLY (artifact self-contained), PINNED by `sha256` (a changed file is a
  loud error), resolved only from CONFIGURED library directories (a pattern from an untrusted source must not read
  files); the name -> file map and its pin live in configuration (the .rxt `include`/`lib` machinery,
  `docs/spec/rxt_format.md` §1.1.1, and [LIB]).
- TRAPS ARE LOUD (no silent defaults): an EMPTY entry (the alternation would match everywhere) is a compile error
  unless filtered or `skip_empty = true`; `\r`/trailing spaces are errors unless `trim = true`.
- SORT IS SEMANTICS: alternation order = PCRE priority (`ab|abc` vs `abc|ab` on `abcd`); the compiler already
  builds priority-preserving tries, so users never sort for speed; `sort(alts, by = length, desc)` exists only as
  the deliberate leftmost-longest choice; `unique` keeps the first occurrence.
- Compile cost is first-order: every kernel row and prelude macro reports compile time, table size and match speed
  beside its DFA column; marginal cost per predicate; warnings only on a route change, a cap, or an interaction
  blow-up ([COST-EXPLAIN]). Prerequisites named before any build: [DFA-MIN-FAST], an in-construction budget,
  [PRED-SPLIT].

**REASONING.** G4; compile-time expansion must terminate; trust: a pattern names a library entry, never an
arbitrary path. Sort-as-semantics: a user who sorts for a trie changes answers.

**STATUS.** Recursion rule: AGREED 2026-11-13 (RECURSION RULE NARROWED, replacing restriction (1)). file_text +
records: LEAN 2026-11-14 (SUPERSEDES the standalone `file_literals` primitive; its filter spelling superseded by
`&`). Import: LEAN 2026-11-13. Cost surfacing: LEAN 2026-11-13. Construction-size risks (complement determinizes
its right operand, quadratic minimizer, many predicates multiply): 2026-11-13 CONSTRUCTION SIZE.

## 8. Libraries

**RULE.** Standard library = prelude text (typed macros, type declarations) on the foundation; it grows without
compiler changes. Standard filters: `between` (inclusive), `startsWith(s) := /${s}.*/`, `endsWith`,
`contains(s) := /.*${s}.*/`, `length`, `when(c, p)` (`x & when(c, p)` = `(x & c & p) | (x & !c)`), `unpad`, string
positions `left/right/mid` with literal positions (units = characters per the encoding mode; out-of-range CLAMP
leaning). Candidate content (a follow-up initiative): network, time, identifiers, communication, checksummed
numbers; each tested against the standard's OWN vectors, the callout oracle and the laws; each shows its DFA
column.

BLESSED CALLOUTS: emitted C text (like kit search code), so the artifact stays self-contained. Blessed =
guarantees the compiler relies on: PURE (reorder, skip, run only on DFA-validated candidates), BOUNDED (linear,
stated limit), TOTAL (bad input = filter false, never a match-time error), ORACLE-TESTED (python datetime /
ipaddress etc.), and DECLARES ITS REGULAR TWIN where one exists (luhn, weekday, days_in): the compiler picks
automaton vs callout. First contents: numbers, dates (days, weekday, days_in, leap), checksums (luhn, mod97,
isbn10/13), network (ipv4_int, in_cidr, ipv6 normalise), text (code-point length); Unicode normalisation deferred
(official UCD data and tests only). The unblessed escape hatch is PCRE `(?C)` with a caller C function, no compiler
assumptions. Home: its own directory/tests/journal like memfn/ (pcrec describes the need, the library returns C
text). A callout in DFA context returns a DFA-friendly verb ((*SKIP), (*PRUNE), (*COMMIT)); plain FAIL needs the VM;
an automatic split may use a verb only where proved answer-identical.

**STATUS.** Standard library: AGREED as a follow-up initiative 2026-11-12. Blessed callouts: LEAN ADOPT 2026-11-14,
"a #6 component after the static pieces". `when`: Frank's request 2026-11-13. Verbs: LEAN 2026-11-13 late.

## 9. Organisational layer

**RULE.**
- INTERFACES: `date := type(year: number, month: number & between(1, 12), day: number & between(1, 31))`;
  `isodate: date := ...` is checked at compile time (narrower OK); a union of compliant forms complies.
- COMPUTED LABELS for compliance (§4.4): `textdate: date := join([...]) with month = mname.index`.
- NO SEMANTIC OVERRIDE: a member is a function of the values; two compliant formats holding one date must agree;
  an override could only be a different IMPLEMENTATION (the compiler's choice); a different meaning (Julian) is a
  different TYPE. Extra information in a format becomes a CONSTRAINT (E-RFC).
- MEMBERS DECLARED WITH THE TYPE (`export date := type(...) { weekday(d) := ...; leap(d) := ... }`), never "any
  macro whose first parameter is date"; members travel with the type, not into the importer's namespace.
- NAMESPACES: a definition is a namespace; dot projects at every level (definition -> pattern `isodate.year`,
  application -> value, search -> occurrences); parts must be self-contained; a part is AS WRITTEN, without
  cross-field context; doc term "namespace" ("module" is pcrec's word for feature modules).
- SCOPE-LIMITED UFCS: `d.name` resolves (1) a label, (2) a type member, (3) a macro in the importer's scope whose
  first parameter accepts the value's type; more than one = compile error naming both; no dot lookup into
  libraries not imported; `import ... as` resolves clashes.
- `types(isodate)` = `[isodate, date]` (the rx first, then declared interfaces in order), an ordinary array; no
  type-of-type tower.

**REASONING.** Rust traits / Go methods for explicit membership; D/Nim UFCS limited to scope so an unrelated
import cannot change `d.foo`.

**STATUS.** LEAN 2026-11-14 (interfaces; namespaces for type members + addendum; polymorphism and the types
array). Namespaces: AGREED 2026-11-13 (DEFINITIONS ARE NAMESPACES). Interfaces wait for after a first build
(LAYERING).

## 10. Eval

**RULE.** `x & eval($fmt)` is a CONDITION known only at match time, opaque to analysis; the static matcher finds
candidates (the hull ignores eval) and eval filters them. DFA-only (linear, no inner captures), the same automaton
code as compile-time `records()`. Only as an explicit MODULE ("requires module 'eval'" otherwise; the artifact
declares the runtime dependency), with a BUDGET (lazy DFA, bounded state cache; exhaustion is a distinct result,
never a silent no-match) and a cache keyed by pattern string. Self-declared LITERALS in files (MIME boundary,
heredoc) are backreferences, not eval; self-declared PATTERNS are eval's real capability and its worst trust case.
The workhorse is the caller-PARAMETERISED matcher (static skeleton + run-time value holes, §11); self-describing
files are a demonstration, not a driver.

**STATUS.** IDEA, late in #6 (2026-11-14 runtime eval + addendum). Needs an owner ruling on the module/dependency
line when reached.

## 11. The outer layer

**RULE.** The expression language is the OUTER layer: an rx is a LITERAL inside it, so a program that is just
`/(a|b)+c/` is valid and every PCRE pattern is a one-literal program (no separate PCRE mode). Top-level `:=`
replaces DEFINE for new code; DEFINE stays only as PCRE syntax inside a literal with PCRE's meaning. The predicate
opt-in selects WHICH LANGUAGE a file or API call is in, not a flag inside a regex. Library files are
expression-language files with `export`. The `.rxt` format is unchanged (a program is a pattern entry's content;
detail settled at build). Crossings: rx -> expression only by `${...}`; expression -> rx only by `/.../`.

Literals: full PCRE inside, `\/` escapes; a literal is its OWN SCOPE (numbered groups do not leak; named groups are
fields of its value); NO INHERITED FLAGS; VALUE-SCOPED (`^`/`$` = the value's ends, lookarounds see only the value);
the STRICT PURE SUBSET first (refuse `\K`, `(*ACCEPT)`, `\G`, backtracking verbs, callouts/inline code, each
admitted later once its meaning is defined). A pattern used as a SET means the strings it matches ENTIRELY: `/^S/`
is {"S"}; keys starting with S are `/S.*/`. Extended mode (x, not xx) is the default for every literal in an
opted-in unit (`(?-x)` turns it off locally).

HOLES `${expr}` (API callers passing a plain PCRE string keep the inner direction: `(\d+)${ <256 }`): every hole
denotes a SET OF STRINGS and matches one of them: a value inserts LITERAL TEXT (never re-parsed: no injection), a
pattern inserts a sub-pattern (`${isodate(year: 2000)}` = a parameterized subroutine call; `(?&isodate)` =
`${isodate}`), a test NARROWS (a guard). Generalized backreferences (`(?<y>\d{4})-${$y + 1}`); holes are
order-free; holes in typed SYNTAX POSITIONS (`\d{${n}}`, `(?i=${ci})`, `[${a}-${b}]`, `\p{${p}}`) supply that
position's type from a finite set; holes never change structure seen outside (group names/numbers). Run-time
PARAMETERS (`limit := param(/\d{1,4}/)`) are read-only per match, validated against their declared type, and read
AS LATE AS POSSIBLE (guarded transitions resolved once at match start; switches compound only where they meet).

**REASONING.** The JSONL example showed the expression language can stand alone; making PCRE text a literal gives
G3 without a mode switch. Value-scoped literals keep a named type meaning the same everywhere. The TYPE of a hole
decides its insertion, never the content, which closes the interpolation-injection hole Perl has.

**STATUS.** Outer layer: LEAN ADOPT 2026-11-14 (newest note). Literal leanings incl. value-scoped and strict
subset: RULED by Frank 2026-11-13 ("I like your suggestions"). Extended mode: Frank 2026-11-13 evening. Holes:
AGREED 2026-11-13 (THE HOLE, GENERALIZED + CORRECTION: tests in holes are guards). Parameters: AGREED/LEAN 2026-11-13
(RUN-TIME PARAMETERS, READ AS LATE AS POSSIBLE, SWITCHES COMPOUND ONLY WHERE THEY MEET); the interface rides
[IFACE-PUSH]. DEFINE-as-binding-block notes (2026-11-13 evening: bindings in DEFINE, classic groups beside
bindings) are overtaken by the outer-layer note for new code; their status for the inner direction is §13 C3. The
x-mode default breaks "every PCRE pattern is a literal": §13 C2. `(\d+)${ <256 }`'s meaning: §13 C4.
In-context vs value-scoped `&` once all `&` is expression-level: §13 C15.

## 12. Worked examples (acceptance cases)

Each case: the program (placeholder spelling), the capability level it needs, and expected behaviour on a few
subjects. Subjects are searched with PCRE semantics (leftmost, then the left operand's priority) unless the
program anchors. Weekdays, day differences and Luhn results were checked in this lane with Python
(`datetime.date.isoweekday`, a hand-written Luhn), not with pcrec. Library names (`dates`, `json`) are imports
(`d := import("dates")`, §7).

### 12.1 E-JSONL: flat JSONL, date range + string match (key-order independence)

    json  := import("json")    # ws, jchar, jstr_any, num, value, member_any, jstr(p), member(k, v), row(k, v)
    dates := import("dates")
    q := json.row("ts",    json.jstr(dates.isodate & between("2024-01-01", "2024-03-31")))
       & json.row("level", json.jstr("error"))
       & json.row("msg",   json.jstr(contains("timeout")))
    /^${q}$/m

`row(k, v)` aligns one member to the member grid; `&` of three rows accepts the members in any order (concatenation
could not). `jstr(p)` = the JSON string literals whose DECODED text is in p (a mapping pulled back to a pattern).
Quoted literals compare as strings; fixed-width ISO dates order correctly that way. LEVEL: default (pure DFA; every
binding is pure; cost = the product of the `row` automata). Expected:
- `{"ts":"2024-02-10","level":"error","msg":"db timeout"}` -> match;
- `{"msg":"timeout","level":"error","ts":"2024-02-10"}` -> match (order independent);
- `{"ts":"2024-05-01","level":"error","msg":"timeout"}` -> no match (date out of range);
- `{"ts":"2024-02-10","level":"error","msg":"timeout"}` -> match (escape-exact `jstr`; weakens the
  required-literal skip; `jstr_plain` restores it, a visible library choice).
Duplicate keys: `row` holds if ANY member with that key matches. Nesting: VM recursion or depth-bounded unrolling.

### 12.2 E-WEEKDAY: ISO date + weekday as a computed property

    isodate := join([year = /\d{4}/, month = /\d\d/ & unpad(between(1, 12)),
                     day = /\d\d/ & unpad(between(1, 31))], sep = "-")
               with weekday = weekday_of($year, $month, $day)      # library macro, regular (400-year cycle)
    isodate & (weekday: 6)                                         # ISO numbering assumed: Monday = 1

LEVEL: default (regular: ~14 year states after the 4th digit, month as an offset mod 7, day in 7 classes; estimated
on the order of a hundred minimal states, unmeasured). Expected: `2026-11-14` -> match (Saturday); `2026-11-13` ->
no (Friday); `2024-02-29` -> no (Thursday). Weekday numbering/value type is not fixed by the notes (`weekday == "Sat"`
and `weekday: 6` both appear): §13 O7.

### 12.3 E-IPV4: real octet ranges

    octet := /\d{1,3}/ & between(0, 255)       # canonical numerals only: "01" excluded
    ipv4  := join([octet, octet, octet, octet], sep = ".")
    ipv4

LEVEL: default. Expected (whole-subject test, `$x & ipv4`): `192.168.1.17` in; `256.1.1.1` out; `01.2.3.4` out
(canonical rule). As a SEARCH program, `256.1.1.1` yields `56.1.1.1` (PCRE search semantics); a boundary or anchor
is the user's to write. Whether leading-zero octets should pass is a library choice (`unpad`), stated, not silent.

### 12.4 E-LUHN: checksummed card numbers

    card := /\d{4}(?:[ ]?\d{4}){3}/ & luhn & startsWith("4")
    card

`luhn` (weighted digit sum mod 10) is REGULAR (~20 states), a computed-property filter declaring its regular twin;
IBAN mod 97 and ISBN-10 mod 11 are the same class. LEVEL: default (twin MUST be the automaton). Expected:
`4111 1111 1111 1111` -> match; `4111 1111 1111 1112` -> no (Luhn fails); `5500 0000 0000 0004` -> no (Luhn valid,
fails `startsWith("4")`). The note's spelling `( ?\d{4})` is rewritten `(?:[ ]?\d{4})` because x-mode is the
literal default (§11): a literal space would be ignored. Whether `luhn` skips the spaces is not stated: §13 O8.

### 12.5 E-CAL: calendar validity (a label's constraint depends on another label)

    isodate := join([year = /\d{4}/, month = /\d\d/ & unpad(between(1, 12)),
                     day = /\d\d/ & unpad(between(1, 31))], sep = "-")
    valid := isodate & (day: unpad(<=days_in($month, leap($year))))
    valid

Finite and enumerable (leap = mod 4/100/400, regular): one automaton. LEVEL: default. Expected (whole subject):
`2024-02-29` in; `2023-02-29` out; `2024-04-31` out; `2024-13-01` out (not an isodate). The notes' own form
`month: \d\d & between(1,12)` is EMPTY for 01..09 under the canonical-numeral rule (only 10, 11, 12 pass, silently):
§13 C9. `$month` inside a constraint on `day` is capture-vs-capture over finite domains (a product, still regular).

### 12.6 E-RFC: weekday consistency

    month_abbrevs   := ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    weekday_abbrevs := ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    textdate := join([day = /\d{1,2}/, mname = month_abbrevs, year = /\d{4}/], sep = " ")
                with month = mname.index
    rfcdate  := join([wname = weekday_abbrevs, rest = textdate], sep = ", ")
                & (wname.index: ==weekday_of($rest.year, $rest.month, $rest.day))
    rfcdate

LEVEL: default (weekday regular, so a weekday-consistent date validator is one pure-DFA automaton). Expected:
`Sat, 14 Nov 2026` -> match; `Fri, 14 Nov 2026` -> no. The note writes `weekday(rest)` with `rest` typed `date` (an
interface member, organisational layer); the layering test (§1) holds only in the plain-macro form above. The
note's `(wname.index: = weekday(rest))` predates the `==` section and the `$` value rule.

### 12.7 E-NEAR: date within 15 days of another (three anchor cases)

    near_const := isodate & within(15, of = "2026-11-14")            # (a) compile-time constant
    anchor     := param(isodate)                                      # (b) caller-supplied at run time
    near_param := isodate & within(15, of = anchor)
    pair       := join([a = isodate, b = isodate], sep = /\s*,\s*/)   # (c) both dates in the subject
    close      := pair & ((days($b) - days($a)): between(-15, 15))

(a) a 31-literal set (2026-10-30 .. 2026-11-29), tiny trie; LEVEL default. `2026-11-29` in, `2026-11-30` out.
(b) a computed set or arithmetic on a parameterised matcher, no eval; LEVEL not fixed by the notes (start-state
choice over ~3.65M anchor values is far past any cap; relax + verify is [PRED-SPLIT]'s shape): §13 O9.
(c) regular in principle but the automaton would remember ~3.65M day values, so a MATCH-TIME check: an inline
callout on DFA-validated candidates using DFA captures; LEVEL `functions`; at the default level a compile error
naming `functions`. `2026-11-01, 2026-11-14` -> match (13 days); `2026-11-01, 2026-12-01` -> no (30 days). The
compiler, not the spelling, picks set-expansion vs match-time check. An expression on the LEFT of `:` (not a label
path) contradicts §4.1's path rule: §13 C10.

### 12.8 E-FILE: file literals and CSV records

    lines := /^[^\r\n]*$/m                                        # named record rx; no hidden default
    alts  := records(file_text("w.txt", sha256 = "<pin>"), lines)
             & !startsWith("#") & length(<=20) & !""                # empty entries filtered explicitly
    rows  := records(file_text("w.csv", sha256 = "<pin>"), /^(?<word>[^,]+),(?<w>\d+)$/m)
    word_of(r) := r.word
    heavy := each(word_of, rows & (w: >100))
    alts | heavy

LEVEL: default; nothing happens at match time (all structure is compile-time). Expected, with `w.txt` = `# words`,
`foo`, `foobar` and `w.csv` = `apple,150`, `pear,90`: `alts` = `foo|foobar` (file order), `heavy` = `apple`.
Searching `foobarbaz` reports `foo` (alternation order is PCRE priority: sort is semantics). Removing `& !""` with a
trailing newline in `w.txt` is a compile error (empty entry), not an everywhere-matching program. A changed
`w.txt` under its pin is a compile error. `& !""` as the empty-entry filter and `r.word` on a record entry are this
document's rewrites of the notes' `skip_empty` and lambda forms. With this `lines`, a CRLF line (`foo\r`)
produces NO record (`$` does not match before `\r`): the `\r` trap moves into the record rx choice and drops the
line silently, against "no silent defaults" (§13 O18).

## 13. Open questions and contradictions

Contradictions (C) are places where two notes, or a note and a ruling, give different readings; open items (O) are
places the notes leave silent or explicitly open. Each gives both readings; none is resolved here.

- **C1. `&` order.** D196 (RULED): the left operand chooses the reported end, "order of operands is meaningful".
  2026-11-14 fractional-rx addendum: "`&` commutes, so order is readability only"; 2026-11-14 SUPERSEDES note: `&` is
  extensional, two spellings of one language behave the same. Reading A: extensional = MEMBERSHIP only, reported
  span still left-chooses (spelling-dependent). Reading B: the expression language's `&` is purely a set operation and
  D196 governs only the reported end of a search, which then depends on the left operand's spelling.
- **C2. x-mode vs "every PCRE pattern is a literal".** 2026-11-13 evening: the opt-in turns on extended mode for
  every literal. 2026-11-14 outer layer: `/(a|b)+c/` is a valid program with PCRE's meaning, no separate PCRE mode.
  `/a b/` or `/a#b/` means something different under x. Reading A: x is the literal default and G3 holds only for
  x-safe patterns (a wrapper `(?-x)` restores PCRE). Reading B: a whole-program literal keeps PCRE's flags and x
  applies only to literals inside a larger program. The notes' own `( ?\d{4})` (E-LUHN) breaks under A.
- **C3. DEFINE bindings in the inner direction.** 2026-11-13 evening: an opted-in DEFINE holds `name := ...` bindings
  (then: classic groups beside them). 2026-11-14: DEFINE stays ONLY as PCRE syntax inside a literal. API callers
  keep the inner direction (`(\d+)${ <256 }`). Reading A: inner-direction patterns have holes but no bindings (bindings
  only at top level). Reading B: inner-direction DEFINE keeps `:=` bindings.
- **C4. The target of a guard hole.** `(\d+)${ <256 }` (2026-11-14 outer layer) and `\d{3}&${<256}` (01:00) read as
  guards on the preceding text. But `<256` mentions no label, so by the fractional-rx rule it is a FULL rx (the set of
  numerals 0..255), and a hole matches one string of its set: the pattern would be `(\d+)` FOLLOWED BY a numeral
  below 256. Reading A: a hole whose expression is a value filter guards the preceding atom/group (the old `##`
  scope rule, "innermost enclosing group"). Reading B: holes are uniform sets; guarding needs `&` or a label
  condition. Also `\d{3}&${...}` uses `&` inside rx text, which C15 questions.
- **C5. Multi-index comma.** 2026-11-14 00:10: `A[1,3,5]` NOT adopted, comma kept for a later `A[i, j]`; the
  multi-index is `A[[1,3,5]]` / `A[B]`. 2026-11-14 `[]` positional note lists `X[1,3,5]` as valid.
- **C6. Binding a test.** 2026-11-13 (`!~` IS A TEST): binding a name to a test is a compile error. 2026-11-13 evening
  (one kind of binding): tests (`ok := leap($d.year)`) sit beside patterns. The later note's closure argument (a test
  is a pattern) suggests the earlier rule is superseded, but neither says so.
- **C7. Value-valued maps.** 2026-11-13 ONE TABLE CONSTRUCT: `["US" => "United States"]`, `/Jan(uary)?/ => 1`
  (key -> arbitrary value). 2026-11-14 views: a map is labelled groups, labels are names; the only value per branch
  shown is `.index`. Reading A: values beyond names/indices are computed labels (`with`). Reading B: `=>` mappings
  survive as a separate construct. No 2026-11-14 note spells `"US" -> "United States"`.
- **C8. Comma in records vs lists.** List literal `[x = /foo/, y = /bar/]` = `|` (alternation). Condition record
  `(x: <200, y: >55)` = AND (2026-11-14 01:00, "records remain as shorthand"). Same comma, opposite connectives;
  the marks note resolved `=` vs `:` but not the comma.
- **C9. Comparisons on padded labels.** The canonical-numeral rule (00:10) makes `/\d\d/ & between(1, 12)` = {10,
  11, 12}. The E-CAL note writes exactly that for months; the interfaces note says "07" complies with `number` via
  canonical unpad; LAYERING foundation (4) lists label value types. Reading A: comparisons are always on the string
  set, `unpad` explicit (E-CAL as written silently drops 01..09). Reading B: a label with a value type compares by
  value. This document's examples use explicit `unpad`.
- **C10. Spelling of transform sections and the left of `:`.** `unpad() == 5`, `length() < 6`, `left(1) == "S"`
  (00:10, binary forms), `length(<=20)` (2026-11-14 file literals), unary-only comparisons (00:10). The left of `:`
  is a label PATH (01:00); E-NEAR writes an arithmetic expression there (`days($b) - days($a): between(-15, 15)`)
  and E-RFC a computed field (`wname.index:`).
- **C11. Purity of `x:` vs ambiguity.** 01:00: every constant `x: S` is pure, one automaton. 2026-11-13 ambiguity
  rule: narrowing = "some parse", PCRE's chosen parse needs the VM for an ambiguous label. Reading A: `x:` on an
  ambiguous label means some-parse (pure, differs from PCRE's `$x`). Reading B: it means PCRE's parse, which needs
  `vm` and is a compile error at the default level.
- **C12. Define-before-use.** 2026-11-13 BLOCK SHAPE: define-before-use REQUIRED for readability. 2026-11-13 evening
  (one kind of binding): forward references allowed, no cycles.
- **C13. Bare label names as values.** 2026-11-13 NAME RESOLUTION: an undeclared bare name is a label. 2026-11-14
  01:00: `x:` constrains, `$x` is ALWAYS the value. Reading A: bare `x` in a value position still means the label's
  value. Reading B: bare `x` is only the constrained side or a binding; values always need `$`.
- **C14. Size-cap fallback.** 2026-11-12 MACROS ON MACROS: expansions over the budget stay as VM evaluation, stamped;
  2026-11-13 [PRED-SPLIT]: the planner automatically demotes a blowing operand to a verify step. 2026-11-14
  capability levels: at the default level, too large = compile error suggesting `functions`, never a silent switch.
  Reading A: the default level forbids both fallbacks (they require `vm`/`functions`). Reading B: [PRED-SPLIT] verify
  is allowed at the default level when the verify is itself an automaton.
- **C15. In-context vs value-scoped `&`.** 2026-11-13 (ruled leanings): in-context lookaround for PATTERN-level `&`,
  value-scoped for predicate literals. 2026-11-14 outer layer: every `&` is expression-level between literals, and
  ERRATUM: `&` is a value operator, not rx syntax. Reading A: there is no pattern-level `&` any more, so all literals
  are value-scoped (a lookahead in an `&` operand cannot see past its span). Reading B: `&` inside `/.../` remains
  D196's pattern-level operator with in-context lookaround (which then also breaks G3 for literal `&`, e.g. `R&D`).
- **C16. Precedence example.** D196: `&` binds tighter than `|`. 2026-11-14 00:10: `x & <256 | >300` reads as
  `x & ((<256) | (>300))`, which requires `|` tighter than `&` (under D196 it is `(x & <256) | >300`). The 01:00
  example `x: <200 & y: >55 | x: <100 & y: >20` follows D196.

Open items:
- **O1.** The meaning of a program's final expression against the subject (search with PCRE semantics, as this
  document assumes, vs whole-subject test); value-scoped literals and "a pattern as a set matches entirely" make
  the two readings differ for every top-level literal.
- **O2.** Precedence among `!`, `:`, `.`, prefix comparisons and arithmetic is stated only pairwise.
- **O3.** Notes call several leanings "ruled" (unset label false, union type of duplicates, filtering by indexing)
  where the original note is a leaning; their status needs confirming.
- **O4.** `x:` on a repeated group (last iteration, every iteration, or refused) is not stated.
- **O5.** Do a map's per-field value constraints carry into joined labels (asked Frank 2026-11-14; lean yes).
- **O6.** The `functions` level presupposes DFA captures ([ENG-TDFA]), a separate initiative; without them a
  callout pays a VM re-run per candidate.
- **O7.** Weekday value type and numbering (`weekday == "Sat"` vs `weekday: 6`).
- **O8.** Checksum filters over separated digits (does `luhn` skip spaces?).
- **O9.** Capability level of a run-time parameter whose variant set is too large (E-NEAR (b)).
- **O10.** Resume after a rejecting callout for unanchored search (open in 2026-11-13 late; verbs proposed).
- **O11.** Index base was "TBD" (Frank 2026-11-13: "we could +1 if needed"); 2026-11-14 leans 1-based; no ruling.
- **O12.** The `!~` operator's place once `!` is a filter (`$x !~ rx` = `$x & !contains(rx)`): keep, or drop as sugar.
- **O13.** Library files: bindings + `export` with no final expression, vs the one-final-expression block rule.
- **O14.** String position out of range: CLAMP (leaning) vs strict false.
- **O15.** Mid-sequence placement for joined maps (`before`/`after` keywords on `|`): deferred to a real example.
- **O16.** Group 0 find-all resume rule (`\K`-style vs lookbehind-style), open in cond_family.md §7 (D193 add. 5).
- **O17.** D196's remaining F7 recommendations (in-context lookaround, `\K` refused, verbs, cross-operand backrefs,
  recursion) were sent to "the [COND-FAMILY] spec section"; only the strict pure subset (§11) has an answer.
- **O18.** With `records` + a user-chosen record rx, lines the rx does not match are dropped without a diagnostic
  (CRLF under `/^[^\r\n]*$/m`); whether `records` must account for every byte of the text is not stated.

## 14. Non-goals

- Non-regular nesting (balanced parentheses, nested JSON) stays with PCRE recursion on the VM (`vm` level) or a
  depth-bounded unrolling; the predicate language adds no non-regular power of its own.
- No general-purpose language: no recursion through parameterized definitions, no unbounded loops, no lambdas until
  an example needs one, no side effects (purity), no run-time compilation of caller-supplied PATTERNS outside `eval`.
- No "best match" overload ranking; no semantic override of type members; no type-of-type tower.
- No change to plain PCRE patterns outside the opt-in; class contents `[...]` keep PCRE2's meaning (synsurv).
- No spelling decision (placeholder throughout); no build (#6 not scheduled; NO BUILD GO).
- Not this document: DFA captures ([ENG-TDFA], separate initiative), the Boolean IR mechanism and lookaround
  lowering (D196 add. 2: mechanism first, syntax untethered; cond_family.md §5 first piece), the standard library's
  content, a JSON database (a consumer, not a pcrec scope change).

## 15. Provenance

COND-FAMILY.md notes by date/heading; "11-12" = the 2026-11-12 sections, etc.

| section | notes consolidated |
|---|---|
| 0 | 11-12 base requirements; 11-13 COST METRICS; Frank 11-13 (#6 not scheduled), 11-14 (this charter); goals are the manager's draft (lane brief) |
| 1 | 11-14 LAYERING |
| 2.1-2.3 | 11-14 fractional rx + addendum; 11-14 `!`; 11-14 SUPERSEDES field-wise `&`; D196 + add. 1-2 |
| 2.4 | 11-13 LITERALS DECIDE, COMPARISONS AND DECIMALS; 11-14 00:10 (unary only, paren-free sections, literals as sets, canonical numerals, unpad); 11-13 late (`between` inclusive) |
| 2.5 | 11-13 NO CONCATENATION OPERATOR |
| 2.6 | 11-13 SEARCH RESULTS ARE VALUES, SEARCH OPERATOR REVISED, `!~` IS A TEST, SET FUNCTIONS REPLACE PROJECTIONS, SET FUNCTIONS BEYOND SEARCH; 11-14 00:10 (`some(a)` = a, no `in`) |
| 3 | 11-14 00:10; 11-14 SUPERSEDES field-wise `&`; arrays vs maps VIEWS; spelling vs logic; index base; duplicate labels by index; `[]` positional only; 11-13 ONE TABLE CONSTRUCT, ARRAYS |
| 4 | 11-14 01:00 (all bullets); 11-13 late (label reference, duplicates, unset); 11-13 DESTRUCTURING, AMBIGUITY EXPLAINED, AMBIGUITY WARNINGS, PATTERN -> VALUE MAPPINGS; 11-13 late weekday property; 11-14 interfaces (computed labels) |
| 5 | 11-13 BLOCK SHAPE, NAME RESOLUTION, TWO SOURCES OF SYMBOLS; 11-13 evening (one kind of binding, macro bindings, `m(x: d2)`, empty intersection, equality checks, overloading); 11-13 BOTH DIRECTIONS; 11-14 join, compose, each's bindings, keywords curry, piecewise via each, binding vs constraining marks; 11-14 00:10 `pattern()` / `pure` |
| 6 | 11-14 capability levels; 11-12 base requirements, performance trades (agreed) |
| 7 | 11-13 RECURSION RULE NARROWED, MACROS ON MACROS, IMPORT, COST METRICS, SURFACING COSTS, CONSTRUCTION SIZE; 11-14 literals from a file, file_text + records |
| 8 | 11-12 STANDARD LIBRARY; 11-13 STRING OPERATIONS; 11-13 late (`when`, callout verbs); 11-14 blessed callouts |
| 9 | 11-13 DEFINITIONS ARE NAMESPACES; 11-14 interfaces, namespaces for type members + addendum, polymorphism and the types array |
| 10 | 11-14 runtime eval + addendum |
| 11 | 11-14 outer layer, ERRATUM; 11-13 LITERAL PATTERNS + "I like your suggestions", REFERENCES FROM A LITERAL, THE HOLE GENERALIZED + CORRECTION, ${y + 1}, RUN-TIME PARAMETERS, PARAMETERS AS CONTROLLED VARIATION, HOLES IN SYNTAX POSITIONS, READ A PARAMETER LATE, SWITCHES COMPOUND; 11-13 evening (extended mode, DEFINE notes) |
| 12 | 11-13 late JSONL; 11-13 late weekday; 11-12 STANDARD LIBRARY (IPv4); 11-14 EXAMPLES (E-LUHN, E-CAL, E-NEAR); 11-14 interfaces (E-RFC); 11-14 file literals, file_text + records |
| 13 | cross-reading of all notes and D196 (this lane) |
| 14 | 11-12 scoping; 11-13 late JSONL (nesting, database); D196 add. 2; synsurv recommendation 2 |

Background documents: `cond_family.md` (the member inventory, machinery M1-M12, the checker product C3, D193
answers) is still the mechanism map the predicate language rides on (its X4 where-clause `rx ## P` and X8 typed
predicates are the predecessors of §§4-5; its `##` spelling and the `_`/`$_` scope rule are superseded by holes and
`x:` conditions). `cond_family_syntax_survey.md` predates the 2026-11-13/14 notes: its operand-extent fix for `=~` is
adopted (`/.../` primaries), its `&!` and `=~` spellings are superseded (`!` filter, `~`), its "opt-in, not default"
and "do not touch class contents" recommendations stand (the outer layer is the opt-in).
