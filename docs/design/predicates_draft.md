# The predicate language ([COND-FAMILY] #6): a preliminary specification for critical analysis

## Changelog

- **rev 3 (lane predspec3, 2026-11-14).** Folds the owner rulings recorded in COND-FAMILY.md from "Q1 critic framing"
  to "transforms are FILTER MODIFIERS", and applies the FIX-NOW dispositions of review
  `docs/dev/reviews/2026-11-14-r1-predspec.md` (critic round crit-predspec on rev 2). Superseded text is REPLACED.
  Changed: §0 NEW goal G0 LOOK-ALIKE CONSISTENCY ranked first, with the LOOK-ALIKE TABLE (§0.1); G3 restated (one-literal
  program = today's PCRE pattern); §2.2 `&` pure intersection again (right associativity WITHDRAWN), `!<200` vs
  `>=200` corrected; §2.3 `each` out of the equivalence list; §2.6 `$x ~ rx` binds `^`/`$` to the value (D193 add. 3),
  `!~` = `x: !contains(rx)`; §2.7 REWRITTEN: transforms are FILTER MODIFIERS (`padded`, `any_case`, `quoted`,
  `length`, `month_numbered`, `json.quoted`, `unpadded`), every example renamed; §3.2 numeric filters range over 1..n;
  §4.1 condition binding (C22: comma separates, `label:` takes up to the comma); §5.1 closed reserved list, string
  enum values; §5.2 labelled arguments narrow, the empty-intersection error scoped to narrowing sites; §5.5 class
  members in codepoint order; §5.6 assertions are set positions; §7 in-context nullability (only the MODE exempts),
  `gaps = "allow"`, prerequisites; §7.1 `transform.noop` gone, marks corrected; §11 REWRITTEN: STRING SETS with the
  EDGE-ASSERTION ERROR (Q1 RULED), context-marked sets withdrawn, D193 add. 3 folded, reasoning restated; §12 examples
  rewritten, E-SEP index fixed, E-FILE text fixed, NEW §12.12 E-CTX-1..7 (the deciding cases); §13 resolved items
  marked, new contradictions (C29-C32) and the review's unruled OWNER items as open items (O26-O38); §15 rows.
- **rev 2 (lane predspec2, 2026-11-14).** Folded every ruling and lean after rev 0 through the counting-occurrences
  ruling and the adopted parts of `docs/dev/lanes/predx_report.md`.
- **rev 0 (lane predspec, 2026-11-14).** First consolidation of the notes through the outer-layer note.

## 0. Status, goals, standing questions

**Status: DRAFT rev 3 (lane predspec3, 2026-11-14). NOT a ruling, NOT scheduled** (Frank 2026-11-13: #6 not
scheduled, discussion continues; "Enumerate go." 2026-11-14 is a DESIGN adoption, not a build go). Purpose (Frank
2026-11-14): "create a preliminary predicate spec doc with our latest ideas for the purpose of critical analysis.
Provide reasoning." It consolidates the dated notes in `docs/design/plan_row_bodies/COND-FAMILY.md` (the source of
truth; the LATEST note on a topic wins), the parts of `docs/dev/lanes/predx_report.md` (exploration, S1-S20,
Q1-Q14) that the 2026-11-14 rulings adopt, and the FIX-NOW dispositions of review 2026-11-14-r1-predspec. Older
background, `docs/design/cond_family.md` (survey rev 0, D193) and `docs/design/cond_family_syntax_survey.md` (lane
synsurv), is cited where still live. Every rule traces to a note, a ruling or a review finding (§15); where they are
silent or disagree, §13 lists both readings. Contradictions are listed, never resolved.

**SYNTAX IS PLACEHOLDER THROUGHOUT.** The owner rules semantics; spelling is a later design step (D193 add. 4).
One spelling RULE is ruled (§5.1): no alphabetic operators or statement keywords; and one NAMING rule (§2.7):
a transform's name describes the subjects it accepts. Examples use the latest spellings: `/.../` rx literals (bare rx
fragments are never admitted in the expression language), `:=` define, `=` bind or set a parameter, `:` constrain,
`==` the equality section, `[]` positional, `&` (pure intersection) / `where` / dot for filtering and labels,
condition literals `(x: S, y: T)`, transforms as FILTER MODIFIERS (`x & padded(between(1, 12))`), `@` effect
statements, modules as `m := import("m")`, 1-based indexes.

Status marks: **RULED** (a D-number or Frank's explicit ruling before rev 0), **AGREED** (Frank proposed or
accepted in discussion before rev 0), **LEAN** (manager's leaning before rev 0), and for items folded since:
**OWNER RULED 2026-11-14** (Frank's ruling or agreement) or **MANAGER LEAN** (the manager's lean recorded on the
note, not yet answered); **REVIEW FIX** (rev 3: a correction applied from a FIX-NOW disposition of review
2026-11-14-r1-predspec, by finding id; not an owner ruling); **OPEN** (§13).

### Goals (MANAGER DRAFT; G0 is the owner's standing criterion; ranked, highest wins a conflict)

| # | goal | who benefits | checkable form |
|---|---|---|---|
| G0 | LOOK-ALIKE CONSISTENCY / INTUITIVE BEHAVIOUR: forms that look like they should do the same thing DO the same thing; where they cannot, the compiler SAYS so for the program at hand. A rule whose effect a user cannot predict (context silently making a predicate fail) is a defect even when formally sound | every user (Frank: "Rx is already hieroglyphics"); reviewers of predicate programs | the LOOK-ALIKE TABLE (§0.1): every pair of forms that look alike is marked SAME, or DIFFERENT + the named diagnostic the compiler emits when they differ; acceptance = no DIFFERENT row without a diagnostic (rows marked GAP are open, §13 O38) |
| G1 | EXPRESSIVENESS over the string: conditions PCRE cannot state (cross-label arithmetic, checksums, calendar validity, key-order independence, computed properties, occurrence counts) are short programs | users writing validators, filters, log/JSONL searches | every §12 acceptance case is written with no construct outside §§2-8 (the cases are chosen by the rules' own author: a control sharing its source, review OWN-15) |
| G2 | LINEAR, AUTOMATON-CODE-ONLY BY DEFAULT: a program that compiles at the default level runs as automaton code (one pass or an automaton relax-then-verify split; linear time, no backtracking, hostile-input safe, self-contained output) | anyone matching untrusted input; embedders | at design: every §12 case names its level; at build: every default-level §12 case compiles to automaton code only (`RX_ENGINE` stamp); anything else is a compile error naming the construct and the opt-in, never a silent route change |
| G3 | PCRE COMPATIBILITY: a one-literal program IS today's PCRE pattern, with PCRE's meaning (no subset, no level beyond today's engine choice) | existing PCRE users; the corpus | the whole `.rxt` corpus, each pattern wrapped as `/.../` (with `/` escaped as `\/` and the case's flags transferred to the literal), answers identically to today (a nullable one-literal program gets the `empty.search` WARNING only, §7) |
| G4 | STRUCTURE IS COMPILE-TIME ONLY, TOTAL, TERMINATING: every structural evaluation (each, join, records, indexing, imports, enumerate) is finite and ends | the compiler's users (no hang at build), the security story | recursion through parameterized definitions only by a strictly decreasing literal parameter (§7); every structural operator ranges over finite declared things, `enumerate` under a budget; a fuzzer over programs never hangs the compiler (watchdog) |

Constraints on every goal (ruled RULES, not ranked goals): no alphabetic operators or keywords (§5.1); `&`, `|`,
`!` extensional (§2.2). Non-goals: §14. G0 is the owner's ("STANDING CRITERION ... ranked first for this design",
COND-FAMILY 2026-11-14 "Q1 critic framing"); G1 > G2 > G3 > G4 is the manager's draft order. At the default level
every G1/G2 conflict resolves toward G2 (a compile error naming the opt-in; the capability levels, §6, and the
class-count cost, §4.6), so G1 is regained by an opt-in, never by a silent route change (review OWN-15: the order
G1 > G2 decides only the design of a new rule).

### 0.1 The LOOK-ALIKE TABLE

Each row is a pair (or set) of forms a reader would expect to agree. SAME = one answer on every subject. DIFFERENT
= the named diagnostic the compiler emits when they differ for the program at hand. GAP = DIFFERENT with no
diagnostic yet (an open defect against G0, §13 O38). "(proposed)" = a named diagnostic recommended by the review and
not yet adopted. Sources: review 2026-11-14-r1-predspec finding ids.

| # | forms | verdict | diagnostic / reason | source |
|---|---|---|---|---|
| L1 | `a & b & c` in any order or grouping, incl. transforms: `alts & !startsWith("#") & length(<=20)` vs `alts & length(<=20) & !startsWith("#")`; `(x & padded(S)) & T` vs `x & (padded(S) & T)` | SAME | `&` is pure intersection (§2.2, OWN-1 ruling) | OWN-1, RUL-11 |
| L2 | a binding vs its expansion: `m := /\d\d/ & padded(between(1, 12)); m & T` vs `/\d\d/ & padded(between(1, 12)) & T` | SAME | | OWN-1 (c) |
| L3 | `isodate(year: S, month: 2)` vs `isodate & (year: S, month: 2)` vs `isodate & (year: S) & (month: 2)` | SAME | labelled arguments = condition literal (§4.1, §5.2) | C22 addendum |
| L4 | `(major: 1, minor: >=4)` vs `(major: 1 & minor: >=4)` | DIFFERENT | the second is a compile ERROR: a label inside a value (`major: (1 & minor: >=4)`) | C22 |
| L5 | `x & (a: d)` vs `(a: d)(x)` | SAME | one extensional application (§2.3) | OWN-5 |
| L6 | `x & (a: d)` vs `each((a: d), x)` | DIFFERENT | `each` is the STRUCTURAL per-entry map (keeps entries, labels, order); an alternative lacking `a` is dropped by `&` with `label.unset`, an ERROR naming it under `each` | OWN-5 |
| L7 | `x: /^S\w*/` vs `x: startsWith("S")` | DIFFERENT | the first is the EDGE-ASSERTION ERROR naming the second (§11) | Q1R-2, Q1X-3 (i) |
| L8 | `num := /\b\d+\b/`: `/x${num}/` vs the pasted `/x\b\d+\b/` | DIFFERENT | the hole form is the EDGE-ASSERTION ERROR ("put `\b` in the pattern that places num") | Q1X-3 (iv), Q1R-3 |
| L9 | `p := /(?<=\$)\d+/`: the program `p` (searched) vs `(n = /\d+/) & (n: p)` | DIFFERENT | the condition is the EDGE-ASSERTION ERROR; the searched final pattern keeps PCRE meaning | Q1X-3 (iii), Q1X-1 |
| L10 | `\w{3} & /\w+\b/` vs `/\w{3}\b/` | DIFFERENT | the first is the EDGE-ASSERTION ERROR (no silent move foo -> bar) | Q1X-2 |
| L11 | `alts & !/^#.*/` vs `alts & !startsWith("#")` | DIFFERENT | the first is the EDGE-ASSERTION ERROR (no silent acceptance) | Q1R-5 |
| L12 | `"5" & /(?<=\$)\d+/` in `@assert.none(...)` vs `"5" & /\d+/` | DIFFERENT | the first is the EDGE-ASSERTION ERROR (an assertion argument is a set position, §5.6) | Q1X-5 |
| L13 | `x & padded(/^5/)` vs `x & padded(startsWith("5"))` | DIFFERENT | the first is the EDGE-ASSERTION ERROR (a modified filter's body is a set position) | Q1R-7, Q1X-6 (c) |
| L14 | `enumerate(/(?<=a)[bc]/)` vs `enumerate(/[bc]/)` | DIFFERENT | the first is the EDGE-ASSERTION ERROR | Q1R-8, Q1X-6 (b) |
| L15 | `@warn.off(/^dead\./)` vs `@warn.off(startsWith("dead."))` | DIFFERENT | the first is the EDGE-ASSERTION ERROR (a name set is a compile-time set) | Q1R-8 |
| L16 | `$m ~ /^err/` vs `m: startsWith("err")` | SAME | in a search inside a value `^`/`$` are the value's ends (D193 add. 3, §2.6) | Q1R-6, RUL-1 |
| L17 | `$m ~ /^err/` vs `m: contains(/^err/)` | DIFFERENT | the second is the EDGE-ASSERTION ERROR (`^` reachable through `contains`'s nullable `.*`); its fix text names `startsWith("err")`. Consequence for `!~`: §13 C32 | lane (from Q1R-6, RUL-5) |
| L18 | a nullable final search pattern: `/\b/` vs `/a*/` | SAME | both are nullable IN CONTEXT: `empty.search` WARNING for a one-literal program, ERROR in a predicate program (§7) | Q1R-9 |
| L19 | `(?m)^\d*` searched vs the same pattern in whole-subject mode | DIFFERENT | by MODE only: `empty.search` in search mode, none when anchored (a `^` in the pattern does not exempt) | Q1R-9 |
| L20 | `/\d\d/ & padded(between(1, 12))` vs `/\d\d/ & between(1, 12)` | DIFFERENT | GAP: the second is {10, 11, 12} by the C9 ruling (string sets, canonical numerals); no warning is named for a padded target against an integer section | C9, OWN-2 |
| L21 | `!<200` vs `>=200` | DIFFERENT | on targets with non-canonical members (`0150`, `abc`: kept by `!<200`, refused by `>=200`): GAP; in where they may stand (`${>=200}` legal, `${!<200}` the unapplied-macro error): the unapplied-macro error. §13 O26 | OWN-2, RUL-2 |
| L22 | `(x: <200 \| >900)` vs top-level `x & <200 \| >900` | DIFFERENT | inside a condition `\|` binds tighter than `:` (x in either range); at top level D196 parses `(x & <200) \| >900`, a full rx that widens the program; `precedence.section` (proposed, PLAN) | C22, RUL-15 |
| L23 | `(x: <200, y: >55)` vs `[(x: <200), (y: >55)]` | DIFFERENT | AND vs OR (an array of filters, §3.5); GAP (§13 O30) | OWN-9 |
| L24 | `x := /a\|b\|c/`: `/${x}\|d/` vs `x \| /d/` vs `/a\|b\|c\|d/` | DIFFERENT | one language, different entries: `[2]` and the default-level `.index` differ; `array.hole` (proposed, PLAN) | OWN-8 |
| L25 | `/a\|b/` vs `/b\|a/` | DIFFERENT | SAME under `& \| !`; differ under `[]`, `.index` and PCRE priority (§3.4, by design); GAP (no diagnostic; §13 O38) | §3.4 |
| L26 | `enumerate(/[-\/.]/)` vs `enumerate(/[.\/-]/)` | SAME | class members in codepoint order (§5.5) | OWN-10 |
| L27 | `X[<4]` vs `X[1\|2\|3]` | SAME | numeric filters range over positions 1..n (§3.2) | RUL-9 |
| L28 | `$x & S` as a condition vs `(x: S)` | DIFFERENT | the first is an ERROR "did you mean `x: ...`?" (§4.1) | §4.1 |
| L29 | `a := 256` vs `b := "256"` under `<a` / `<b` | DIFFERENT | GAP; OPEN (§13 O27) | OWN-3 |
| L30 | `!(x: S)` vs `(x: !S)` on a repeated, optional or zero-iteration label | DIFFERENT | GAP; OPEN (§13 O28) | OWN-4 |
| L31 | two `occurs.some(...)` filters vs two conditions on one `some(s)` | DIFFERENT | GAP; OPEN (§13 O29) | OWN-6 |
| L32 | `/${q}/m` vs the inlined text of `q` | DIFFERENT | GAP; `flag.hole` (proposed); OPEN (§13 O32) | Q1R-11 |
| L33 | `\k<s>` vs `${$s}` vs `each(..., enumerate(...))` on a finite label | DIFFERENT | different levels today; OPEN (§13 O34) | RUL-7 |
| L34 | `(a: <5) & (b: <5)` on an ambiguous two-label parse: default level vs `vm` | DIFFERENT | `label.ambiguous` WARNING (per label); multi-label reading OPEN (§13 O33) | RUL-3 |
| L35 | `(?J)` duplicate label vs a repeated label, under `x: S` | DIFFERENT | GAP; OPEN (§13 O35) | RUL-16 |
| L36 | `(x: S)` vs `occurs.all(x: S)` on a repeated label | OPEN | §13 C28 | OWN-4, C28 |
| L37 | `(wname.index: ==wd)` vs `(b: >$a)` | OPEN | a computed value read bare vs with `$` (§13 C13) | OWN-11 |
| L38 | `isodate(x).year` vs `(x & isodate).year` | OPEN | value vs pattern (§13 C29) | RUL-8 |

**REASONING.** The owner's framing: "complex context could cause predicates to just not work and it's not clear how
the obscure rules impact it ... that's why it was so important to me that things that look like they should do the
same thing actually do." A ranked goal without a checkable table would lose every tie to G1 (review OWN-13); the
table makes G0 testable, and a D27 spec-first author writing acceptance cases from the table alone is its natural
independent control (review "D27 recommendation").

**STATUS.** G0 as the first criterion: OWNER RULED 2026-11-14 ("Q1 critic framing"). G0 as a goal row and the
table: REVIEW FIX (OWN-13). Rows L1-L4: OWNER RULED 2026-11-14 (OWN-1, C22 and addendum); L7-L19: OWNER RULED
2026-11-14 (Q1); other rows state the rule of the section cited.

### Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** Mostly not relevant: a language spec introduces no measured quantity. The numbers cited
   (ISO date with leap Feb 29 as a plain regex: 6,848 B object, 5.9 ms compile, all 4-digit years; 6,376 B for
   2000-2099; COND-FAMILY 2026-11-13 "COST METRICS"; class counts in §4.6; review Q1X-8's DFA state counts) are
   compile-time sizes or arithmetic, not timings; any cost table a build produces must name its regime then.
2. **The independent control.** Relevant to §12 and G0: expected behaviours were checked against Python's
   `datetime` (weekdays, day differences), a hand-written Luhn function and libpcre2 10.49 (the review's kit), not
   against pcrec. At build the notes name the controls: the PCRE2+callout oracle (studies/andspike, F9), an
   independent Python reference evaluator (2026-11-12 base decisions), standards' own test vectors for library
   entries (2026-11-12 STANDARD LIBRARY), which `@assert.*` statements (§5.6) can carry inside the library file; for
   G0 a D27 author working from §0.1 alone.
3. **What moves when data is regenerated.** Relevant only through `file_text`/`import` pins (§7): a changed file
   under a `sha256` pin is a loud compile error; a re-pinned file changes the emitted automaton. No table or stamp
   is introduced by this document.

## 1. Layering

**RULE.** Two layers. FOUNDATION: value kinds (§2), operators and filter modifiers (§2), views (§3), match values and
computed labels (§4), capability levels and the reporting axis (§6), the compile-time boundary, modules and
warnings (§7). LIBRARIES, built on the foundation and changeable without it: `each`, `join`, `records`,
`file_text`, standard filters and filter modifiers (`between`, `startsWith`, `length`, `padded`, `unpadded`,
`any_case`, `quoted`), `occurs`, `assert`, tuple comparisons, blessed callouts (§8). The ORGANISATIONAL layer
(interfaces, type members, UFCS, `types()`) is CUT from the first spec (§9); interfaces may return as library
packaging after a build. Namespaces stay in the foundation (a module is a map, §7).

**TEST OF THE RANKING.** No worked example needs the cut layer: §12 checks this case by case (E-RFC uses a plain
macro on the three fields, not an interface member).

**REASONING.** Frank: the purpose is to probe the fundamental structure; unless foundational, lower priority.
predx §9: none of thirteen further programs needed interfaces, UFCS or `types()`.

**STATUS.** Layer outline: LEAN, as amended by later rulings (the LAYERING note is the manager's outline under
Frank's framing; its "no recursion", namespaces-as-organisational and numeric-value-type items were since changed
by Q12, the module-as-map lean and C9; REVIEW FIX RUL-14.4). The cut: OWNER RULED 2026-11-14 (predx Q8).

## 2. Values and operators

### 2.1 Two value kinds

**RULE.** Every value is either an **rx** (a set of strings, extensional, §11) or a **macro** (a term awaiting
arguments, curried by keywords). Numeric and string literals are rx: `5` = {"5"}, `"a.b"` = {"a.b"} (the dot is
literal, unlike `/a.b/`); they differ only in what a comparison means (§2.4). Conditions (`(x: <200)`), prefix `!B`,
unapplied filters, unapplied filter modifiers and partially applied macros are macros. A value filter mentioning NO
label (`<200`, `between(3, 6)`, `startsWith("S")`, `padded(between(1, 12))`) is a full rx (the set that passes);
anything naming a label it does not define is a macro awaiting the pattern that defines it. A MODULE is a map (§7),
not a third kind. `@` statements (§5.1) are statements, not values. There is no boolean type; there is no number
type (arithmetic operates on numeral strings, §2.5).

**REASONING.** The closure (a predicate denotes a pattern, 2026-11-12/13) means one algebra serves patterns,
values and tests; a condition is a term with a free variable, the same kind as a curried macro.

**STATUS.** LEAN (2026-11-14 fractional rx; layering item 1). Literals as one-string sets: LEAN. Module = map, not
a third kind: MANAGER LEAN 2026-11-14 (import follow-up, SUPERSEDES the namespace-as-third-kind lean). No number
type: OWNER RULED 2026-11-14 for COUNTS (counting: "filters, NOT a count value"); the language-wide reading (no
number type anywhere, arithmetic on numeral strings) is this document's, LEAN (REVIEW FIX RUL-14.2; arithmetic
result width: §13 O27). The earlier "assertions (their own value kind)": §13 C19.

### 2.2 Operators `&`, `|`, prefix `!`

**RULE.** `&` intersection, `|` union, both EXTENSIONAL over rx operands: membership depends only on the
language, so two spellings of one language behave the same under `&`, `|`, `!`. `&` is PURE INTERSECTION:
associative and commutative, so the ORDER and GROUPING of an `&` chain never change which strings it admits (a
transform is a filter modifier, §2.7, never an `&` operand with a position). Prefix `!` is ALWAYS A FILTER (a macro
awaiting a target): `A & !B` = `(!B)(A)` = A minus B; `&!` is not a separate operator. A standalone `!B` where an rx
is needed (`${!B}`, `C | !B`) is the unapplied-macro error. Filters combine pointwise by `& | !`.

`!<200` and `>=200` are NOT interchangeable: `!<200` keeps every target string that is not a canonical numeral
below 200, so on a target with non-canonical members they differ (`/\d{4}/ & !<200` keeps `0150`, `/\d{4}/ & >=200`
does not; `"abc" & !<200` = {"abc"}, `"abc" & >=200` is empty); they agree only where every target string is a
canonical numeral. `!<200` is a filter, `>=200` a full rx (§0.1 L21; whether a label-free `!f` is a full rx: §13
O26). There is no "positive form" lint rewrite (it would change answers).

Reported span (D196, RULED for pattern-level `&`): the left operand chooses (PCRE priority: first alternative,
greedy longer, lazy shorter), the right only filters which ends are admitted; the span SET is commutative.
Precedence (D196): concatenation, then `&`, then `|`; inside a condition literal `&` and `|` bind tighter than `:`
(§4.1). In the expression language there is no concatenation operator (§2.5).

**REASONING.** Extensional `&` keeps arrays and rx "the same". `!` as a filter: a standalone complement is useless
in a search and VM-hostile, while under `&` it is bounded. A pure `&` is what the owner's look-alike criterion (G0)
asks of the most common operator: rev 2's right-associative `&` made reordering or parenthesizing a chain with a
transform in it change the answer silently (review OWN-1, RUL-11).

**STATUS.** `&` extensional, `!` filter: AGREED 2026-11-14. D196: RULED. `&` pure intersection, order- and
grouping-free: OWNER RULED 2026-11-14 (OWN-1, "transforms are FILTER MODIFIERS"), SUPERSEDES the right-associative
`&` lean. The `!<200` / `>=200` correction and the dropped lint: REVIEW FIX (OWN-2, RUL-2). C1 (extensional set vs
D196's left-chooses), sharpened by "order-free": OPEN, §13.

### 2.3 The unapplied-macro error

**RULE.** An unapplied macro where an rx is required is a compile error naming the fix: "filter `x: digit` has
no target; write `T & (x: digit)`"; "modifier `padded` has no filter; write `padded(between(1, 12))`". Application
of a FILTER has two equivalent spellings: `x & (a: digit)` and `(a: digit)(x)`; `rx & f` = `f(rx)`; `p(x)` = `x &
p` for a parameterless filter `p` (a modified filter such as `padded(S)` is one). An alternative of x lacking the
label is DROPPED (with the `label.unset` warning, §4.2), never an error, in both spellings. `each(f, A)` is NOT an
application spelling: it is the STRUCTURAL per-entry map (§5.3), which keeps entries, labels and order and is an
error on an entry lacking the label (§0.1 L6).

**STATUS.** LEAN 2026-11-14 (fractional rx + addendum). `each` out of the equivalence, lacking label = drop:
REVIEW FIX (OWN-5). Transforms as filter modifiers make `p(x)` = `x & p` hold for them too (rev 2 C20 RESOLVED by the
OWN-1 ruling).

### 2.4 Comparisons are unary sections on string sets

**RULE.** Comparisons are UNARY ONLY: `<256`, `>=lo`, `==5` denote sets, attached by `&` like everything else. A
prefix comparison takes ONE ATOM (literal, label value, binding, call, field access, parenthesized expression) and
binds tighter than `&`, `|`, `!`. The LITERAL decides the reading: `<256` = integers 0..255, `<"256"` =
lexicographic strings, `2.5` decimal, `0x100` hex. Comparisons are on the STRING SET: an integer section contains
CANONICAL numerals of VARIABLE WIDTH (the `\d+` shape: no leading zeros, sign or decimal point unless the literal
has them). Padded text is compared through the explicit `padded` modifier (§2.7): `/\d\d/ & between(1, 12)` is
{10, 11, 12} and is WRONG for months; write `/\d\d/ & padded(between(1, 12))`. `between(lo, hi)` is INCLUSIVE.
Decimal is exact decimal, never binary floating point.

**REASONING.** Every binary comparison is an intersection with a section. Literal-decides means declared types are
needed only where no literal fixes the reading (value vs value, §4.6). A comparison never silently reinterprets the
text: padding is a visible modifier on the filter.

**STATUS.** Unary: AGREED 2026-11-14 00:10. Literals decide: AGREED 2026-11-13. String sets, `\d+` integers,
explicit padding modifier: OWNER RULED 2026-11-14 (C9, Reading A: "Integers should be \d+ to be variable width.
Unpad would be the right approach"); CANONICAL (no leading zeros) is the reading this document takes of "`\d+`"
(which as a regex admits `007`), supported by "Unpad would be the right approach"; E-IPV4's `01.2.3.4` out depends on
it (REVIEW FIX RUL-14.6). The modifier's name `padded`: OWNER RULED 2026-11-14 (OWN-1 naming rule). Exact decimal:
LEAN 2026-11-12. Whether the reading belongs to the literal's quoting or to the comparison: §13 O27.

### 2.5 No concatenation operator; arithmetic

**RULE.** The expression language has no concatenation operator: sequencing is written inside a literal
(`/${a}-${b}/`) or by `join`. `+ - * %` are arithmetic only, on numeral strings (no number type, §2.1). Value
concatenation is insertion or a library name (`concat(x, y)`).

**REASONING.** Avoids the overload trap (`"12" + "34"` = 46 or "1234"?); with no juxtaposition, a name after an
expression always starts a binding (one-token look-ahead, §5.1).

**STATUS.** LEAN 2026-11-13 (NO CONCATENATION OPERATOR). Arithmetic result width (`${$y + 1}` on `0099`): §13 O27.

### 2.6 Search

**RULE.** `$x ~ rx` = search inside a value (unanchored): its value is the OCCURRENCE SET under PCRE iteration
order (non-overlapping, leftmost, continue after the match; the C find-all iterator's order). The VALUE is the whole
subject of that search: inside the slashes `^` and `$` are the value's start and end, and no assertion sees text
outside the value (D193 add. 3; `$x` is a one-string set, context-free, §4.1, §11). `some`, `all` are library names
over a set; `s[i]` indexes occurrences (§3.2). Every `some(s)` over the same set in one predicate denotes the SAME
occurrence (two occurrences need two names; §13 O29). `$x !~ rx` is a TEST, sugar for the condition `(x:
!contains(rx))` (consequence for an rx with an edge assertion: §13 C32). Membership is `x & a`; no `in`.

**REASONING.** Search results are values, not globals (Frank: "Even Perl had the awkward $1"). One quantifier name
(`some`, not `any`). The value-as-subject reading is D193 add. 3's ruled meaning for a predicate's regex test.

**STATUS.** Meaning (occurrence set): AGREED 2026-11-13 (SET FUNCTIONS REPLACE PROJECTIONS); the `~` operator:
LEAN ("Spellings remain leanings until the owner rules", REVIEW FIX RUL-14.5). `^`/`$` bound to the value: RULED
(D193 add. 3, Frank 2026-11-10; stands under the Q1 ruling; REVIEW FIX RUL-1, Q1R-6). `!~` as `x: !contains(rx)`:
REVIEW FIX (RUL-5; keep or drop: §13 O12). `count` over a search's occurrence set: §13 C21. Binding a name to a
test: §13 C6.

### 2.7 Transforms are FILTER MODIFIERS

**RULE.** A TRANSFORM is a macro FILTER -> FILTER: given a filter S it returns a NEW FILTER that accepts the subjects
S would accept once parts of them are ignored or reinterpreted. THE TRANSFORM TRANSFORMS THE FILTER, NOT THE
SUBJECT: the subject is never modified; the modified filter reads it differently. Mechanically the modified filter
is the pullback of S under a finite transducer or a finite table t (the strings whose t-image lies in S): one
construction, regular in, regular out (inverse image under a rational relation); a non-finite t needs `functions`.

    month & padded(between(1, 12))                 # accepts "05", "5", "12": leading zeros ignored by the filter
    t & unpadded(5, between("09:00", "10:00"))      # accepts "9:00": the filter reads it as if zero-padded to width 5
    (msg: quoted(contains("timeout")))              # the filter reads only the text inside the quotes
    (host: any_case("example.com"))                 # the filter ignores letter case
    alts & !startsWith("#") & length(<=20)          # the filter reads the subject's length
    mname & month_numbered(between(1, 6))           # month names whose number is 1..6: "Jan" .. "Jun"
    quoted(any_case("host"))                        # modifiers nest, in reading order

NAMING RULE: a modifier's name describes the SUBJECTS IT ACCEPTS (an adjective or phrase: `padded`, `unpadded`,
`any_case`, `quoted`, `length`, `month_numbered`), never a verb acting on the subject (`unpad`, `trim`,
`lowercase`). A modifier is applied to a filter by a call and the result is used like any filter: `x &
padded(S)`, `(x: padded(S))`, `padded(S)(x)`; `&` stays pure intersection (§2.2), so a modified filter may stand
anywhere in a chain. A modifier without its filter argument where a filter is needed is the unapplied-macro error
(§2.3). `!padded(S)` is an ordinary filter (the complement of a filter). A modified filter's argument is a SET
POSITION (§11): an edge assertion inside it is the edge-assertion error (`padded(/^5/)`; write
`padded(startsWith("5"))`). The variable-width lexicographic lint (`compare.width`) suggests `unpadded(n, ...)`.

**REASONING.** One mechanism (the pullback) collapses rev 0's transform sections, pattern -> value mappings, `jstr(p)`
and the binary forms into one closure theorem (predx S1, §8.2). Frank: "The problem is the name. Trim or unpad imply
they are doing something to the subject. But they are not. They are changing the filter to ignore elements of the
subject." A filter -> filter macro needs no operator and no position in an `&` chain, so `&` stays order- and
grouping-free (G0, review OWN-1/RUL-11), and C1/C20/C22's transform cases dissolve.

**STATUS.** OWNER RULED 2026-11-14 (OWN-1, "transforms are FILTER MODIFIERS": filter -> filter, the pullback,
nesting in reading order, the naming rule, the docs rule), SUPERSEDES the right-associative `&` pipeline (`x & unpad
& between(1, 12)`), the `->` / `;` stage ideas, and the earlier function forms `unpad(S)` / `length(<=20)` read as
images. Names `padded`, `any_case`, `quoted`, `length`, `month_numbered`: the ruling's. `unpadded(n, S)` (rev 2's
`pad(n)`) and `json.quoted` (rev 2's `jstr`): this document's names under the naming rule, placeholder (§13 O37).

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
value-valued maps: §13 C7). The metadata members `.index`/`.label` vs user labels of those names: §13 O31.

### 3.2 The four tools

**RULE.**
1. `X[...]` = POSITION in the array view only: integers, integer sets, numeric filters (`X[1]`, `X[<4]`); the
   result is always an array, keeping the ORIGINAL positions; a string or non-numeric filter inside is a compile
   error suggesting the right tool. Indexing descends (`d[1][1]`). Integer sets and numeric filters select among
   positions 1..n only (`X[<4]` = `X[1|2|3]`); the integer literal `[0]` alone = the whole rx (PCRE group 0). Out of
   range = entry absent: tests on it are false. 1-based.
2. `X & f` = filter by LANGUAGE; `&` distributes over entries and empty products drop:
   `alts & !startsWith("#")` keeps passing literals; `rows & (w: >100)` keeps matching rows.
3. `where(p, X)` = filter by a compile-time STRUCTURAL property (the filtering twin of `each`); `where_group(p, X)`
   for the map view.
4. `X.name` = LABEL navigation in the map view (`A.Saturday`, `alt.repeated[1]`, module members `json.row`);
   `.name` is never digits.

**REASONING.** The output of `[]` is always an array, so `[]` uses the array view. `&` on structural properties
would intersect languages (wrong), hence `where`.

**STATUS.** AGREED 2026-11-14 (`[]` positional only). 1-based: OWNER RULED 2026-11-14 (predx Q7). Filters over
1..n: REVIEW FIX (RUL-9). Multi-index comma `X[1,3,5]`: §13 C5.

### 3.3 Holes and groups are single entries; `|` concatenates arrays

**RULE.** Expression `|` CONCATENATES arrays (each operand contributes its top-level alternatives; appended
entries take lowest PCRE priority). An rx GROUP or a `${}` HOLE is ONE entry. With `x := /(a|b|c)/`: `x | /d/`
has 2 entries; with `x := /a|b|c/`: `x | /d/` has 4; `/${x}|d/` has 2 for either (§0.1 L24). A hole is an atom for
correctness (`/${x}d/` = `(?:a|b|c)d`). Expression parentheses are precedence only. `join` of an empty array is the
empty string.

**STATUS.** LEAN 2026-11-14 (spelling vs logic in the array view; ADD = `|`). The `array.hole` warning: proposed
(review OWN-8, PLAN).

### 3.4 Extensional vs structural operations

**RULE.** EXTENSIONAL (`& | !`, comparisons, filter modifiers) depend only on the language. STRUCTURAL (indexing,
`each`, `join`, `where`, `.label`, `enumerate`, entry counts) read the SPELLING: `/a|b/` and `/b|a/` are equal
under `&` but differ under `[1]` (and in PCRE priority). Internal rewrites (altcls, alt_normal_form) never change
user-visible structure. Field-wise narrowing that keeps other entries is structural (`each_group(&, rx, (x: d2))`),
never `&`.

**STATUS.** AGREED 2026-11-14. The structural effect of `&`'s distribution over entries is unstated: §13 C17.

### 3.5 Arrays of filters and filter modifiers

**RULE.** Closure one level up: an array of rx is an rx (alternation); an ARRAY OF FILTERS is a filter (pointwise:
`[f, g](t)` = `f(t) | g(t)`); an ARRAY OF FILTER MODIFIERS is a filter modifier (`[padded, any_case](S)` =
`padded(S) | any_case(S)`). A MIXED rx/filter array is an error (fix: write the rx entry as a filter, `(& /x/)`).
Entries must share arity. `.index` keeps the original positions when entries drop, so `ipv4 & cidrs` reports which
entry admitted the match.

**REASONING.** Frank: "an array of rx is an rx. An array of filters|macros is macro?" Classification against a
table (predx §8.3 item 1) becomes `pattern & table` with no new construct.

**STATUS.** OWNER RULED 2026-11-14 (predx gaps: ARRAYS OF FILTERS); arrays of modifiers restated under the OWN-1
ruling.

## 4. Match values

### 4.1 `x:` constrains, `$x` reads; condition literals

**RULE.** `x: S` = the set of WHOLE MATCHES whose label x is in S (a condition, a macro awaiting the pattern that
defines x). `$x` = the VALUE captured in this match (a one-string set, context-free, §11). `x:` is ALWAYS the
constrained side; `$x` is ALWAYS a value used (operand, insertion `${$x}`, output). Capture-vs-capture is `x: <$y`
(§4.6). `$x & ...` used AS A CONDITION is an ERROR: "did you mean `x: ...`?". The left of `:` is a label PATH
(`d.year: <2000`), never an expression: a computed value is constrained through a computed label (§4.4).

CONDITION LITERALS AND BINDING. A condition is written in a CONDITION LITERAL `( ... )`. Inside it the COMMA
separates conditions, and each `label:` takes the whole expression up to the next comma or the closing paren:
`&` and `|` bind tighter than `:`, and `:` binds tighter than `,`. So:
- conjunction of conditions = comma: `(major: 1, minor: >=4)` = `(major: 1) & (minor: >=4)`;
- disjunction = separate literals: `(major: 2) | (major: 1, minor: >=4)`;
- a set after a label needs no parentheses: `(x: <200 | >900)`, `(month: padded(between(1, 12)))`;
- `(major: 1 & minor: >=4)` = `major: (1 & minor: >=4)` = a compile ERROR (a label inside a value), not a misreading;
- at top level `P & x: S` reads as `(P & x): S`, whose left is not a label path: an ERROR "write `P & (x: S)`".
The binding reads the same at top level and after a label (G0). In a chain `P & Q & (x: ...)`, x is looked up in
the other operands of the chain (`P & Q`; `&` is order- and grouping-free, so the whole flattened chain); a label in
both is AMBIGUOUS (error naming both); an unknown label is an error listing those available.

LABELLED ARGUMENTS are the same form with the same binding: `p(a: s, b: t)` = `p & (a: s, b: t)`, and
`isodate(year: S, month: 2)` = `isodate & (year: S, month: 2)` (currying: the positional argument is the subject).
`:` constrains, `=` sets a parameter (`sep = "."`). A labelled argument always NARROWS the subject (§5.2).

**REASONING.** Frank: "x: represents a fraction of the search object deconstructed": the pattern is the schema, a
match a row, labels its columns, `x:` a WHERE clause. Avoids the trap that `($x & <200) & ($y & >55)` forces x = y.
ONE condition form (`label: set`) for every condition. On the binding, Frank: `month: unpad & between(1, 12)` "is
somewhat structural because it's combined with the comma. & binds tighter"; "Also isodate(year: unpad & etc) looks
the same" (the labelled argument).

**STATUS.** AGREED 2026-11-14 01:00. One condition form, the left of `:` a path: OWNER RULED 2026-11-14 (predx Q6,
concept). Binding (comma separates, `label:` up to the comma, `&`/`|` tighter than `:`): OWNER RULED 2026-11-14
(C22), SUPERSEDES "`name:` takes one operand term, tighter than `&`". Labelled arguments = condition literal, `=`
sets a parameter, labelled arguments narrow: OWNER RULED 2026-11-14 (C22 addendum; answers review RUL-10). The
top-level `P & x: S` error and the flattened chain lookup: this document's consequences of the ruled binding (rev 2's
right-associative tension, review RUL-4, dissolves with pure `&`). Comma records `(x: <200, y: >55)`: kept by C22
(rev 2 C8 RESOLVED).

### 4.2 Unset labels

**RULE.** A comparison on an UNSET label is false (its `!` true); a condition naming a label that is unset for a
match fails for that match; WARN (`label.unset`) when a plain reference can be unset. This keeps extensional `&`
consistent: `(x = /\d/ | y = /[a-z]/) & (x: /[0-5]/)` = `[0-5]` (the alternative lacking x drops, §2.3).

**STATUS.** LEAN 2026-11-13 late; cited as "ruled" by a later note (§13 O3). That warnings have names: OWNER RULED
2026-11-14; the name `label.unset`: MANAGER LEAN (the manager's list, REVIEW FIX RUL-14.1). The two sentences
disagree on `(x: !<5)` for an unset x, and on zero-iteration repeated labels: §13 O28.

### 4.3 Repeated and duplicate labels

**RULE.** At the default level a repeated label follows the SEQUENCE RULE: `x: S` constrains ALL iterations; the
quantified forms are the `occurs` library (§8: `occurs.some((x: S))`, `occurs.exactly(n, (x: S))`, ...); a bare
`$x` on a repeated label is an ERROR naming the quantified forms. At `vm`, `$x` is PCRE's last iteration (what
`\k<x>` sees). Duplicate names (`(?J)`, `(?|`): plain `$x` gives the lowest-numbered set group; the static TYPE of a
duplicate label is the UNION of the definitions that can set it. Structurally, `alt.x` returns EVERY entry labelled
x as an array in group order; `alt.x[1]` (first in the PATTERN, compile time) differs from `$x` (the MATCH's value).

**REASONING.** "All iterations" is substitution into the loop body, the only pure lowering (predx §2.1, O4); the
last-iteration rule would need captures inside a loop.

**STATUS.** Sequence rule: OWNER RULED 2026-11-14 (predx Q4), SUPERSEDES "plain `$x` = last iteration" at the
default level. `occurs`: OWNER RULED 2026-11-14 (counting; namespace name MANAGER LEAN). Duplicate labels by index
LEAN 2026-11-14; union type cited "ruled" 2026-11-14 (§13 O3). A duplicate label set twice in one match under `x:
S`: §13 O35. The spelling of an `occurs` condition argument: §13 C31.

### 4.4 Computed labels are match-dependent bindings

**RULE.** A COMPUTED LABEL is a value of the match that is not a substring. It is written as a MATCH-DEPENDENT
BINDING: a binding that reads match labels IS a computed label of the pattern whose labels it reads:

    d  := days($b) - days($a)                 # a computed label of the pattern defining a and b
    close := pair & (d: between(-15, 15))
    wd := weekday_of($rest.year, $rest.month, $rest.day)
    rfc & (wname.index: ==wd)

A mapping must be a FUNCTION (one value per text: the per-label ambiguity check), many-to-one allowed, total on its
pattern. Tabulated mappings report a constant from the accept state (§6.2); numerals by digit conversion. A computed
value is context-free (§11). Through a filter modifier a value condition becomes a pattern: `month_numbered(<3)` =
`/Jan(uary)?|Feb(ruary)?/` (§2.7).

**REASONING.** Lets non-numeric layouts (month names) comply with numeric fields; a weekday or a Luhn check is a
property without a capture group. A binding instead of a keyword keeps the grammar keyword-free (§5.1).

**STATUS.** Computed labels: LEAN, foundation per the LAYERING note. Match-dependent binding as THE spelling:
MANAGER LEAN 2026-11-14 (Q6/Q9 spelling; concept OWNER RULED), SUPERSEDES the `with` placeholder (`with month =
mname.index`) and predx's `with`. Which pattern a binding attaches to when its labels occur in several: §13 O19.
Forward value calls (`days($b)`) beside filter modifiers (the value-mapping family): §13, families note.

### 4.5 Ambiguity

**RULE.** A label is AMBIGUOUS when two accepting parses give it different spans (decidable). At the default level
a condition on an ambiguous label passes if SOME parse passes (one automaton); a `label.ambiguous` WARNING shows a
witness, the two parses, which one PCRE chooses, the consequence and a fix where one exists. At `vm` the condition
uses PCRE's chosen parse. Library types are checked unambiguous at their labels. Every occurrence of the same
application denotes ONE parse (merged narrowing).

**REASONING.** The default level is a promise; only some-parse keeps it; for unambiguous labels the readings
coincide, so the difference is confined to exactly the patterns the warning flags (predx C11).

**STATUS.** OWNER RULED 2026-11-14 (predx Q2). Resolves C11. Some-parse per condition vs merged narrowing for two
conditions on one pattern (`(a: <5) & (b: <5)` on `123`): §13 O33.

### 4.6 Value-vs-value relations, priced by class count

**RULE.** A comparison between two match values (`(b: >$a)`, `(day: padded(<=days_in($month, leap($year))))`,
`(wname.index: ==wd)`) is a RELATION, run the cheapest correct way. Its cost is the CLASS COUNT of the earlier
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
library calls (§5.6), computed values are bindings (§4.4). Enumerated option values are STRINGS, not bare words
(`gaps = "allow"`, `order = "desc"`).

BARE STATEMENTS: only `@` forms (compile-time EFFECT macros, §5.6, §7.1) may stand alone; a bare rx anywhere but
the final expression is an error ("unused pattern: bind it or make it the result"); a bare statement without `@` is
an error (it catches the unbound pattern). Pure macros cannot take `@`; effect macros cannot drop it (purity
visible and checked syntactically). `@` exists only in the expression language.

Names: symbols come only from the pattern (labels), from `:=` (bindings) or from a module (member access). The
BUILT-INS are a CLOSED list, reserved in CALL position only: `import`, `enumerate`, `pattern`, `param`,
`file_text`, `records`, `eval`. Every other name in the examples (`between`, `startsWith`, `contains`, `padded`,
`days`, `weekday_of`, `within`, `list_of`, `join`, `each`, ...) is a library name; whether `some`/`all` are
built-ins or library names: §13 C21/C28 (review RUL-13). `$&` and `$_` are reserved scope-supplied labels; an
undeclared name that is not a label is an error with a suggestion; a binding hiding a label WARNS (`$x` still
reaches the label).

**REASONING.** Frank: "no alpha operators ... with, check, in ... don't want to go into new grammar lightly". The
grammar shrinks to bindings, expressions, calls and `@` statements; the `@` mark makes compile-time effects visible.
A bare enum word (`allow`, `desc`) would be a keyword in argument position (review OWN-7).

**STATUS.** Block shape: AGREED 2026-11-13. One kind: LEAN 2026-11-13 evening. No alphabetic keywords: OWNER RULED
2026-11-14 (Q6/Q9). `@` statements, the unused-pattern and bare-statement errors: MANAGER LEAN 2026-11-14 (import
follow-up (3), on Frank's prefix suggestion). String enum values and the closed built-in list: REVIEW FIX (OWN-7;
the list is this document's reading of the built-ins it names). Define-before-use: §13 C12. Bare label names as
values: §13 C13. How a program selects `functions`/`captures`/`vm`/`eval` (§6.1): §13 O31.

### 5.2 Macros, parameters, currying

**RULE.** `m(p1, p2) := body` makes a macro; positional parameters CONSTRUCT (`between(lo, hi) := >=lo & <=hi`,
`pair(p) := /${p},${p}/`), keyword `name =` arguments CONFIGURE (`join(a, sep = ".")`), `name:` arguments FILTER
(`isodate(year: 2000)` = `isodate & (year: 2000)`, §4.1). Every labelled pattern is a macro whose label parameters
are its labels (FORWARD `isodate(x)`: text -> fields; REVERSE `isodate(year: 2000)`: a pattern; fully constrained =
formatting). Keywords CURRY: an application is a value until every required parameter is bound; rebinding one is an
error. Operators are macros (`(& B)` a curried filter). Macros expand at compile time, inlined per use; cost is per
USE. No lambda until an example needs one.

Typed parameters: `m(x: T)` narrows x by T, and the POSITIONAL argument must lie WITHIN T; a broader or partly
overlapping argument is an error showing a dropped witness and the explicit conversion. A LABELLED argument never
gets that check: it always NARROWS the subject (`isodate(year: <2000)` silently drops `5`, which `/\d{4}/` cannot
hold). At NARROWING SITES (typed parameters, labelled arguments, an `&` whose operands come from definitions) an
empty intersection from pure parts is an ERROR; a dead branch WARNS (`dead.branch`); nothing when emptiness is match-
or parameter-dependent; NEVER inside an `@assert.*` argument, whose emptiness is the assertion's own subject (§5.6).
`m(p: pure)` makes a match-dependent argument an error ("pass `pattern($x)`"). Built-in `pattern($x)` = the label's
static pattern.

**STATUS.** Macro bindings AGREED 2026-11-13 evening; currying AGREED 2026-11-14; `=` sets a parameter vs `:`
filters: OWNER RULED 2026-11-14 (C22 addendum); labelled arguments narrow: OWNER RULED 2026-11-14 (C22 addendum,
answers review RUL-10); typed-parameter containment: LEAN 2026-11-13; the empty-intersection error scoped to
narrowing sites: REVIEW FIX (RUL-6); `pattern()`/`pure`: LEAN 2026-11-14 00:10. Overloading: LEAN, NOT phase one.
`isodate(x).year` vs `(x & isodate).year`: §13 C29.

### 5.3 Structural macros: `each`, `each_group`, `where`, `join`

**RULE.** Macros are passable values, FENCED: compile-time only, over finite declared arrays, structural operators
only. `each(f, A)` applies f per entry, keeps labels and order, returns an array (the structural per-entry map, not
an application spelling, §2.3); over several arrays it ZIPS by position (unequal lengths = error naming both counts).
`each_group` zips BY LABEL. `join(a, sep = s)` concatenates entries in declared order; `sep` is a set; joined parts
stay navigable labels (`(c.A: <200)`, `c[1]`), free when unread. Family: in-order fixed = `join`; in-order repeated =
`list_of(X, sep = ...)`; any-order fixed = `&` of labelled parts (JSONL); candidate sugar `any_order(a, sep = ...)`.
Caller-visible captures are a library macro: `capture(x) := /(?<${x.label}>${x})/`, `join(each(capture, a), sep =
".")`, exported like any binding (§7).

**Ordinal parameter.** The iteration ORDINAL (dense, starts at `index =`, default 1), `x.index` (original position)
and `x.label` (original name) differ once an array is sliced; the ordinal is a PARAMETER the macro declares
(`capture(x, i) := /(?<f_${i}>${x})/`); `each` passes it as the second argument when the macro takes one.

**STATUS.** LEAN 2026-11-14 (join; compose instead of an option; each's bindings). Ordinal default 1: per the
1-based ruling. Per-field constraints carrying into joined labels: §13 O5. The rev 0 `export capture(x) := ...`
keyword form is superseded by `@export` (§7).

### 5.4 The marks

**RULE.** `:=` defines a name; `=` BINDS a label inside a map/list literal (`year = /\d{4}/`) and SETS a parameter
(`sep = "."`); `:` CONSTRAINS (typed parameters `x: date`, conditions `(year: <2000)`, labelled arguments
`isodate(year: 2000)`); `,` separates conditions in a condition literal and arguments in a call (§4.1); `==` is the
equality section; `@` marks an effect statement.

**STATUS.** SPELLING LEAN 2026-11-14, syntax not ruled; `:` vs `=` and the comma: OWNER RULED 2026-11-14 (C22 and
addendum). `@`: MANAGER LEAN 2026-11-14.

### 5.5 `enumerate`

**RULE.** `enumerate(rx)` = the ARRAY of a FINITE rx's strings, in PCRE PRIORITY ORDER (leftmost alternative,
greedy before lazy); the members of a CLASS, which has no priority among them, come in CODEPOINT ORDER (so
`enumerate(/[-\/.]/)` = `enumerate(/[.\/-]/)` = `["-", ".", "/"]`); so re-joining preserves which match is reported
(hence a built-in, not a library). Its argument is a compile-time SET POSITION: an edge assertion in it is the
edge-assertion error (§11; `enumerate(/(?<=a)[bc]/)`). A BUDGET bounds it: an infinite or over-budget rx is a
compile error giving the count. Uses: finite backreferences made regular (`each(date_sep, enumerate(/[-\/.]/))`,
`!contains(each(triple, enumerate(/[\x21-\x7E]/)))`), matched delimiters (`each(q, enumerate(/["']/))`), which option
matched via `.index` at the default level, per-entry library assertions (spelling of `@each(...)` OPEN).

**REASONING.** A class is ONE alternative, so no array tool reached its members; finiteness plus a budget keeps G4.
Codepoint order is extensional: two spellings of one class give one array (G0).

**STATUS.** OWNER RULED 2026-11-14 ("I love it. Enumerate go." = design adoption; #6 unscheduled). Codepoint order
for class members: REVIEW FIX (OWN-10). Edge assertions refused: OWNER RULED 2026-11-14 (Q1). Finite-group
backreferences as a GENERAL engine rule are not #6: [BACKREF-FINITE] (§11, §14); the levels of the three same-text
spellings: §13 O34.

### 5.6 Assertions (compile-time checks)

**RULE.** Compile-time assertions are LIBRARY effect calls over rx, written as `@` statements; no boolean type, no
keyword. Membership is `&` (`"2024" & leap` is {"2024"} or empty); inclusion is `A & !B` empty:

    assert := import("assert")
    @assert.some("2024" & leap)
    @assert.none("1900" & leap)
    @assert.none(octet & !/\d{1,3}/)          # every octet has 1-3 digits
    @assert.same(old, new)                     # library: both differences empty
    @assert.some(slow_errors)                  # not dead

An assertion's argument is a compile-time SET POSITION: it is decided on strings, and an edge assertion in it is
the edge-assertion error (§11; `@assert.none("5" & /(?<=\$)\d+/)` is refused, not existential over contexts). No
assertion states SEARCH behaviour (that `256.1.1.1` is searched as `56.1.1.1`, §12.3). The implicit
empty-intersection error never applies inside an assertion's argument (§5.2). Anonymous assertions report line +
text; NAMED assertions give named failures (§13 C18 for their spelling). An assertion the compiler cannot decide
reports "can't prove: not regular" beyond the default level. Libraries carry their standard's test vectors as
assertions run at import.

**REASONING.** Language equality and inclusion are decidable (D196 add. 2's never-match/XOR fact), so the library
test rule ("tested against the standard's own vectors") becomes executable (predx S8, §8.3 item 3).

**STATUS.** Concept (compile-time assertions): OWNER RULED 2026-11-14 (Q9). Library form `assert.some` etc.: Frank
2026-11-14 (`assert := import("assert")`, `assert.some("2024" & leap)`); `@` prefix: MANAGER LEAN 2026-11-14,
SUPERSEDES `check A == B` and the `assert_some(...)` built-ins. Set position: OWNER RULED 2026-11-14 (Q1). The
empty-intersection exemption: REVIEW FIX (RUL-6). A library SEARCH assertion (review Q1X-5, `@assert.finds`-shaped):
not adopted, recorded in §13 O36.

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
speed); it may NOT change level silently. A one-literal program is today's PCRE pattern on today's engines (G3,
§11). The cost tool's first output is the level a program needed and why.

**`&` AT `vm` WITH A NON-REGULAR OPERAND.** The regular operands build the CANDIDATE automaton; the VM verifies the
non-regular operand on each candidate span; the reported span follows D196 ([PRED-SPLIT]).

**REASONING.** An RE2-class promise with far more expressive power (G2). Independence: a user may want
linear-time callouts without backtracking, or spans without callouts. Under the ruled string-set model (§11) no
set-position use carries context state, so G2 needs no regular-lookaround lowering for conditions (review Q1X-8).

**STATUS.** Levels: LEAN ADOPT 2026-11-14. The promise "linear, automaton code only" (automaton split and
parameter-only computations at default; `functions` = functions over captured text): OWNER RULED 2026-11-14 (predx
Q5; resolves C14 and O9). `&` at `vm`: OWNER RULED 2026-11-14 ("the spec must state it"). Performance-trade rules:
RULED 2026-11-12. `functions` presupposes DFA captures ([ENG-TDFA]): §13 O6. How a program selects a level: §13 O31.

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
  compile-time match of rx over a compile-time string is an entry; named groups make entries maps. The record rx is
  SEARCHED in the text (in context, like a final pattern: its `^`/`$` read the file text); each ENTRY is a plain
  string (context-free, §11). The record rx's matches must TILE the text (every byte in a record or a declared gap),
  else a compile error naming the untiled byte range ("bytes 0-4 (`foo\r\n`) belong to no record");
  `records(text, rx, gaps = "allow")` opts out. How a record rx declares its separator bytes: §13 O20 (until it is
  settled, a multi-line file fails tiling on its `\n` terminators). `file_literals(p)` is library sugar over
  `records` with a NAMED record rx (no hidden default). Record rx restricted to the DFA-able subset; `records` needs
  an IN-COMPILER matcher (pcrec has none today) built on [AUTOMATON-KIT].
- MODULES. `m := import(names, sha256 = ...)` is a built-in FUNCTION; `names` is a CONSTANT set of names (an rx
  over file names, e.g. `"json"`); it must resolve to EXACTLY ONE file in the CONFIGURED library directories (zero
  or several = compile error listing the candidates; a pattern from an untrusted source must not read files). It
  returns a MODULE, which is a MAP (the aligned map case) of the file's exported bindings; member access is label
  navigation (`json.row`); using a module whole as a pattern is legal only if every entry is an rx (else the
  unapplied-macro error). A library file exports with `@export(names)`: every module label whose NAME is in the rx
  `names` (`@export("leap")`, `@export(["leap", /[^_].*/])`, `@export(/[^_].*/)`); the filter must be a set of
  strings, not a target-less filter in an alternation. A name set is a compile-time set: an edge assertion in it is
  the edge-assertion error (§11). A library file with no export is an error ("library exports nothing"). Imports and
  file reads are COMPILE TIME ONLY (artifact self-contained), PINNED by `sha256`; the name -> file map and its pin
  live in configuration (the .rxt `include`/`lib` machinery, `docs/spec/rxt_format.md` §1.1.1, and [LIB]).
- THE EMPTY-MATCH HAZARD. When the program's FINAL pattern is NULLABLE and used in SEARCH mode: an ERROR in a
  predicate program, a WARNING (`empty.search`) for a program that is one plain PCRE literal (`/a*/` is legal
  PCRE). NULLABILITY IS COMPUTED IN CONTEXT: a pattern is nullable when it can report an empty find in some subject,
  so `/\b/`, `/(?=a)/` and `(?m)^\d*` are nullable although as string sets `/\b/` and `/(?=a)/` are empty. Only the
  caller's anchored/whole-string MODE exempts (validation); an anchor or assertion IN the pattern does not (`(?m)^\d*`
  yields an empty find on every line without digits). No diagnostic either when the empty string is excluded (`&
  !""`) or when opted out. The message names the empty source and the fixes. Empty ENTRIES are legal (`["", "M"]`
  is an optional part). File blank lines are covered by `records` tiling.
- SORT IS SEMANTICS: alternation order = PCRE priority (`ab|abc` vs `abc|ab` on `abcd`); `sort(alts, by =
  "length", order = "desc")` exists only as the deliberate leftmost-longest choice; `unique` keeps the first
  occurrence.
- Compile cost is first-order: every kernel row and prelude macro reports compile time, table size and match speed
  beside its DFA column; relation costs as class counts (§4.6); warnings only on a route change, a cap, or an
  interaction blow-up ([COST-EXPLAIN]). Prerequisites named before any build: [DFA-MIN-FAST], an
  in-construction budget, [PRED-SPLIT], and the static EDGE-ASSERTION check (nullable-prefix/suffix reachability of
  an assertion node, §11). NOT a prerequisite: D196 add. 2's regular-lookaround lowering for conditions (the ruled
  model refuses edge lookarounds in set positions; context-free uses cost the same under every model, review
  Q1X-8). A context assertion in a FINAL pattern (a lookahead, a multi-character lookbehind) keeps today's engine
  choice and its level (§6.1).

**REASONING.** G4; compile-time expansion must terminate, and a strictly decreasing literal parameter is a
syntactic termination check that admits the one legitimate default-level recursion (bounded nesting). Tiling is "no
silent defaults" for data files (the CRLF trap becomes an error). Modules as maps add no value kind; import and
export as functions over name-sets add no keyword, and one name-selection rule serves import, export and warnings.
The empty-ENTRY error rejected legitimate optional parts and missed `/\d*/`; the real hazard is a final pattern that
reports an empty find, which is a fact about the pattern in context (review Q1R-9).

**STATUS.** Bounded recursion: OWNER RULED 2026-11-14 (predx Q12, low priority, one example), REFINES the 2026-11-13
RECURSION RULE NARROWED. file_text + records: LEAN 2026-11-14. Tiling: OWNER RULED 2026-11-14 (predx Q13).
Import/export as functions, module = map, `@export` filter, no-export error: MANAGER LEAN 2026-11-14 (on Frank's
proposals); import resolves to exactly one file, argument a set of names: OWNER RULED 2026-11-14 (addendum,
Frank). Empty-match rule: OWNER RULED 2026-11-14, SUPERSEDES the empty-ENTRY error and `skip_empty`; nullability in
context: OWNER RULED 2026-11-14 (Q1); only the MODE exempts: REVIEW FIX (Q1R-9). String option values: REVIEW FIX
(OWN-7). Prerequisite list: REVIEW FIX (Q1X-8). The untiled-range wording: REVIEW FIX (Q1R-10). Cost surfacing: LEAN
2026-11-13. The `trim` / `\r` trap of rev 0 is subsumed by tiling (§13 O18 RESOLVED).

### 7.1 Named warnings

**RULE.** Every warning has a STABLE NAME in dotted families (a contract, stated in the spec): `empty.search`,
`dead.branch`, `label.unset`, `compare.width`, `label.ambiguous`, `warn.unused`; proposed by review 2026-11-14-r1
and not adopted: `precedence.section`, `array.hole`, `flag.hole`. Control is by `@` effects, rest of file:
`@warn.off("compare.width")`, `@warn.off(startsWith("dead."))` (a label-free value filter is a full rx; the look-alike
`@warn.off(/^dead\./)` is the edge-assertion error, §0.1 L15), `@warn.off(/.*/)`; the reverse `@warn.error(/.*/)` (a
strict build); a per-binding form (spelling OPEN); and a compiler option for a whole build (like `-Wno-`). SELECTORS
ARE A SET OF NAMES AS AN RX, the same name-selection rule as import and export: no `*` wildcard (`"*"` is the
literal name `*`, matches nothing). Errors cannot be disabled (the edge-assertion error included). An `@warn.off`
that suppresses nothing raises `warn.unused` (itself suppressible).

**STATUS.** That warnings have names and can be disabled, selectors as an rx: OWNER RULED 2026-11-14 (empty-match
ruling: "warnings need names and the user must be able to disable them"; amendment: "use an rx instead of wild card
purely for consistency"). The list of names: MANAGER LEAN (the manager's, recorded on the ruling; REVIEW FIX
RUL-14.1). rev 2's `transform.noop` is gone: a modifier without its filter is the unapplied-macro error (§2.3).

## 8. Libraries

**RULE.** Standard library = prelude text (typed macros) on the foundation; it grows without compiler changes.
Standard filters: `between` (inclusive), `startsWith(s) := /${s}.*/`, `endsWith`, `contains(s) := /.*${s}.*/`,
`when(c, p)` (`x & when(c, p)` = `(x & c & p) | (x & !c)`). Standard FILTER MODIFIERS (§2.7; each transforms the
filter, never the subject): `padded(S)` (leading zeros ignored), `unpadded(n, S)` (read as if zero-padded to width
n), `any_case(S)` (letter case ignored), `quoted(S)` (only the text inside the quotes read), `length(S)` (the
subject's length read), `month_numbered(S)` (a month name read as its number), string positions `left/right/mid`
with literal positions (units = characters per the encoding mode; out-of-range: §13 O14); `json.quoted(S)` (a JSON
string literal read as its decoded text) lives in the `json` module.
- `occurs` (`occurs := import("occurs")`): filters over a repeated label's occurrences: `all`, `some`, `none`,
  `exactly(n, c)`, `at_least(n, c)`, `at_most(n, c)`; `c` is the usual condition (`(label: set)`; its spelling as an
  argument: §13 C31); FILTERS, NOT a count value (no number type); constant (or caller-parameter) n at default; cost
  = a capped counter (n+2 states) multiplied in, shown by [COST-EXPLAIN]; a count against another label's value is a
  priced relation (§4.6). Value comparisons (`between`, `<=`) stay purely about values.
- TUPLE COMPARISONS are a library macro, no syntax: `lex_ge([major, minor, patch], [1, 4, 0])` (the array spelling:
  §13 C25). Written out with condition literals, "version at least 1.4" is
  `semver & ((major: >=2) | (major: 1, minor: >=4))`: the comma conjoins, separate literals disjoin (§4.1).
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
2026-11-14. `when`: Frank's request 2026-11-13. Filter modifiers and their names: OWNER RULED 2026-11-14 (OWN-1;
`unpadded`, `json.quoted`: §13 O37). `occurs` family: OWNER RULED 2026-11-14 (counting, as a LIBRARY); the namespace
name `occurs`: MANAGER LEAN (name open to Frank; not `label`, which clashes with `x.label`). Tuples as a library
macro: OWNER RULED 2026-11-14, SUPERSEDES predx's tuple-on-the-left-of-`:` syntax (S12). The comma form of the
semver condition: OWNER RULED 2026-11-14 (C22: "the semver example needs the comma form").

## 9. Cut from the first spec

**RULE.** Not in the first spec: INTERFACES (`type(...)`, `isodate: date`), TYPE MEMBERS declared with a type,
SCOPE-LIMITED UFCS (`d.weekday` resolving to a scoped macro), `types()`. Interfaces may return after a build as
LIBRARY PACKAGING (a set of required labels with value types, checked by inclusion per field, at the module export
boundary). The NO-SEMANTIC-OVERRIDE rule (two compliant formats holding one date must agree) stays as a rule for
that return. Namespaces stay (§7, a module is a map; a definition's labels are dotted paths).

**REASONING.** predx §9: none of thirteen programs needed them; UFCS adds a third resolution rule to `.` (the
metadata members are already one: §13 O31).

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
`/(a|b)+c/` is valid and every PCRE pattern is a one-literal program (no separate PCRE mode). A ONE-LITERAL PROGRAM
IS EXACTLY TODAY'S PCRE PATTERN: no strict subset, no level beyond today's engine choice, no set position (G3).
Top-level `:=` replaces DEFINE for new code; DEFINE stays only as PCRE syntax inside a literal with PCRE's meaning.
The predicate opt-in selects WHICH LANGUAGE a file or API call is in. Library files are expression-language files
with `@export`. The `.rxt` format is unchanged. Crossings: rx -> expression only by `${...}`; expression -> rx only
by `/.../`.

Literals: full PCRE inside, `\/` escapes; a literal means EXACTLY what PCRE means: NO implicit extended mode
(`/foo bar/` keeps its space, `#` is literal); extended mode is per literal (`/.../x` or a leading `(?x)`). A literal
is its OWN SCOPE (numbered groups do not leak; named groups are fields of its value); NO INHERITED FLAGS (a hole's
pattern keeps its own flags: §13 O32). Inside a LARGER program, literals start from the STRICT PURE SUBSET (refuse
`\K`, `(*ACCEPT)`, `\G`, backtracking verbs, callouts/inline code, each admitted later once its predicate meaning is
defined; unbounded backreferences need `vm`).

STRING SETS. A pattern used as a SET denotes the strings it matches ENTIRELY (keys starting with S are `/S.*/`).
SET POSITIONS are: an `&` operand, a label condition, a filter body (incl. a modified filter's argument, §2.7), a
hole's set, and a compile-time set (an `enumerate` argument, an `@assert` argument, a name set for
`import`/`@export`/`@warn`, a computed value, a `records` entry). In a set position an EDGE ASSERTION is a COMPILE
ERROR naming the fix: an edge assertion is one that can read text OUTSIDE the value (`^`, `$`, `\b`, or a lookaround
reachable at the value's start through a nullable prefix or at its end through a nullable suffix; the property is
decided statically on the pattern):

    "`^` in the condition on x reads text outside x: write `startsWith("S")`, or put `^` in the pattern that places x"

Assertions strictly INSIDE a value keep PCRE meaning (`(x: /\d+\b\.\d+/)`: the `\b` reads only x's own characters).
VALUES (`$x`, a one-string set), transform images (what a modified filter reads, §2.7) and compile-time sets are
CONTEXT-FREE. In a SEARCH inside a value (`$x ~ rx`, §2.6) the value is the whole subject, so `^`/`$` are the
value's ends (D193 add. 3). FINAL patterns and `records` record rx are SEARCHED in their subject and keep full PCRE
meaning, context assertions included. Nullability for the empty-match rule is computed IN CONTEXT (§7). A named
in-context form (a library call, no keyword) is added only on a measured need (D77).

HOLES `${expr}`: every hole denotes a SET OF STRINGS and matches one of them: a value inserts LITERAL TEXT (never
re-parsed), a pattern inserts a sub-pattern (`${isodate(year: 2000)}` = a parameterized subroutine call); a hole's
set is a set position (an edge assertion inside it is the error above; write the assertion in the literal around the
hole). In the inner direction (an API caller passing a PCRE string) a GUARD is written with an explicit `&`:
`(\d+)&${ <256 }`; a hole after an atom WITHOUT `&` is a FOLLOWING item (`(\d+)${ <256 }` = digits followed by a
numeral below 256). Generalized backreferences (`(?<y>\d{4})-${$y + 1}`); holes are order-free; holes in typed SYNTAX
POSITIONS (`\d{${n}}`, `[${a}-${b}]`) supply that position's type from a finite set; holes never change structure
seen outside. Run-time PARAMETERS (`limit := param(/\d{1,4}/)`) are read-only per match, validated against their
type, read AS LATE AS POSSIBLE; computations on parameters only are default-level (§6.1).

**REASONING.** Making PCRE text a literal gives G3 without a mode switch; with long patterns decomposed into
bindings, free-form multi-line layout belongs to the expression language, not to literals (C2). G3 is kept by
making a one-literal program exactly today's pattern, with the strict subset only where a literal sits inside a
larger program (review OWN-14). The Q1 foundation: the review compared THREE candidates, context-marked triples (A),
value-scoped string sets (B1) and string sets plus a context kind composed in context (B2); A equals B2 at every
match-time `&`, condition and hole and is underdetermined wherever no subject exists (transform images, computed
values, `enumerate`, assertions, `records` entries, name sets); the rule set (§2.1, §2.4, §2.7, §3.4, §4.1, §5.5,
§7) is string-set shaped. rev 2's argument for A (G3 for `/(?<=\$)\d+/` and E-JSONL's `/^${q}$/m`) did not
discriminate: both are FINAL patterns, searched in the subject under every model (review Q1R-12, Q1X-1). The real
argument for A was "a name means the same everywhere"; but under A or B2 look-alikes fail SILENTLY (`x: /^S\w*/`
never matches after text, `\w{3} & /\w+\b/` moves the match, a `^` condition on a repeated label passes one header
and fails two, `!/^#.*/` keeps comment lines), and under B1 others do (`n: p` dead for a lookbehind `p`). Every
divergence needs an assertion that can read outside the value, a static property; refusing exactly those makes
look-alikes either agree or be refused, with no silent failure, no outer-pattern dependence and no unbuilt lowering
at the default level (G0, G2), and keeps D193 add. 3. Nullability in context is A's one real gain, adopted. The KIND
of a hole decides its insertion, never the content (no injection); a guard needs `&` so the hole rule has no
exception (C4).

**STATUS.** Outer layer: LEAN ADOPT 2026-11-14. Literal leanings incl. the strict subset: RULED 2026-11-13; the
subset scoped to literals inside a larger program and the one-literal program = today's pattern: REVIEW FIX
(OWN-14). No implicit x-mode: OWNER RULED 2026-11-14 (C2). STRING SETS with the EDGE-ASSERTION ERROR, context-free
values, transform images and compile-time sets, nullability in context, a named in-context form only on measured
need: OWNER RULED 2026-11-14 (Q1, "1. agree", on the review's proposed answer), SUPERSEDES the tentative
context-marked sets (rev 2) and rev 2's hole-as-in-context reading; D193 add. 3 stands. The three candidates and
the restated reasoning: REVIEW FIX (Q1R-1, Q1X-2, Q1R-12, Q1X-1). Guard holes with `&`: OWNER RULED 2026-11-14 (C4).
Holes: AGREED 2026-11-13. Parameters: AGREED/LEAN 2026-11-13; the interface rides [IFACE-PUSH]. Finite-group
backreferences as regular: a general engine row, [BACKREF-FINITE] (OWNER RULED 2026-11-14, predx Q10: not #6). `&` in
inner-direction rx text: §13 C15, C23.

## 12. Worked examples (acceptance cases)

Each case: the program (placeholder spelling), the capability level it needs, and expected behaviour on a few
subjects. Subjects are searched with PCRE semantics (leftmost, then the left operand's priority) unless the program
anchors. Weekdays, day differences and Luhn results were checked with Python (`datetime.date.isoweekday`, a
hand-written Luhn), not with pcrec; PCRE behaviours (E-IPV4, E-DEPTH, E-FILE, E-CTX) were checked with libpcre2 10.49
by review 2026-11-14-r1-predspec. Libraries are modules (`d := import("dates")`, §7). No §12.1-12.11 case puts an
assertion in a set position, so none of them depends on the Q1 model; §12.12 holds the cases that do.

### 12.1 E-JSONL: flat JSONL, date range + string match (key-order independence)

    json  := import("json")    # ws, jchar, quoted, num, value, member_any, member(k, v), row(k, v)
    dates := import("dates")
    q := json.row("ts",    json.quoted(dates.isodate & between("2024-01-01", "2024-03-31")))
       & json.row("level", json.quoted("error"))
       & json.row("msg",   json.quoted(contains("timeout")))
    /^${q}$/m

`row(k, v)` aligns one member to the member grid; `&` of three rows accepts the members in any order. `json.quoted`
is the JSON-string filter modifier (§2.7): `json.quoted(p)` is the filter p changed to read a JSON string literal as
its decoded text (rev 2's `json.jstr & p` pipeline is superseded). Quoted literals compare as strings; fixed-width
ISO dates order correctly that way. `^`/`$` sit in the FINAL pattern and read the subject's lines (§11); `q` holds no
assertion. LEVEL: default (every binding is pure; cost = the product of the `row` automata). Expected:
- `{"ts":"2024-02-10","level":"error","msg":"db timeout"}` -> match;
- `{"msg":"timeout","level":"error","ts":"2024-02-10"}` -> match (order independent);
- `{"ts":"2024-05-01","level":"error","msg":"timeout"}` -> no match (date out of range).
Duplicate keys: `row` holds if ANY member with that key matches. Nesting: §12.11 or `vm`.

### 12.2 E-WEEKDAY: ISO date + weekday as a computed label

    isodate := join([year  = /\d{4}/,
                     month = /\d\d/ & padded(between(1, 12)),
                     day   = /\d\d/ & padded(between(1, 31))], sep = "-")
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
`padded(between(0, 255))` admits it, a stated library choice). As a SEARCH program, `256.1.1.1` yields `56.1.1.1`
(held under libpcre2); a boundary is the user's to write, in the final pattern (`/\b${ipv4}\b/` would put `\b` in a
hole's literal, not in the hole: the boundary reads the subject; on `256.1.1.1 and 10.0.0.1` it finds `10.0.0.1`
only). The assertions run at compile time and are decided on strings (§5.6).

### 12.4 E-LUHN: checksummed card numbers

    card := /\d{4}(?: ?\d{4}){3}/ & luhn & startsWith("4")
    card

`luhn` (weighted digit sum mod 10) is REGULAR (~20 states), a filter declaring its regular twin; IBAN mod 97 and
ISBN-10 mod 11 are the same class. The literal keeps its space (no implicit x-mode, §11). LEVEL: default. Expected:
`4111 1111 1111 1111` -> match; `4111 1111 1111 1112` -> no (Luhn fails); `5500 0000 0000 0004` -> no (Luhn valid,
fails `startsWith("4")`). Whether `luhn` skips the spaces: §13 O8.

### 12.5 E-CAL: calendar validity (a relation between labels)

    isodate := (as in 12.2)
    dim   := days_in($month, leap($year))       # computed label: 24 classes (12 months x leap)
    valid := isodate & (day: padded(<=dim))
    @assert.some("2024-02-29" & valid)
    @assert.none("2023-02-29" & valid)
    valid

A value-vs-value relation with class count 24 (§4.6): one automaton. LEVEL: default. Expected (whole subject):
`2024-02-29` in; `2023-02-29` out; `2024-04-31` out; `2024-13-01` out (not an isodate). The notes' `month: \d\d &
between(1,12)` is WRONG (only 10, 11, 12 pass): C9 ruling, `padded` is the fix (§0.1 L20).

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
rewrite. `month := $mname.index` is this document's rewrite of rev 0's `with month = mname.index` under §4.4 (the
same mapping as the `month_numbered` modifier, §2.7; family note, §13). `==wd` vs `==$wd`: §13 C13.

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
             & !startsWith("#") & !"" & length(<=20)              # any order: & is pure intersection
    rows  := records(file_text("w.csv", sha256 = "<pin>"), /^(?<word>[^,]+),(?<w>\d+)$/m)
    word_of(r) := r.word
    heavy := each(word_of, rows & (w: >100))
    alts | heavy

LEVEL: default; nothing happens at match time. Expected, with `w.txt` = `# words`, `foo`, `foobar` and `w.csv` =
`apple,150`, `pear,90`: `alts` = `foo|foobar` (file order), `heavy` = `apple`. Searching `foobarbaz` reports `foo`
(sort is semantics). The record rx is searched in the file text (its `^`/`$` read the file); the entries are plain
strings. A BLANK LINE inside `w.txt` gives an empty entry (without `& !""` the final pattern is nullable and the
search program is an error, the `empty.search` hazard, §7); a TRAILING newline gives none (PCRE2's multiline `^`
does not match after a final newline; Python's `re` differs). A CRLF line `foo\r\n` is not matched at all by `lines`,
so the tiling error names the whole range `foo\r\n`, not just the `\r`. NOT YET A VALID ACCEPTANCE CASE: the `\n`
terminators belong to no record, so under the tiling rule as written E-FILE is itself a tiling error until O20
says how a record rx declares its separators (§13 O20). A changed `w.txt` under its pin is a compile error.

### 12.9 E-HTTP: header block with occurrence counts

    occurs := import("occurs")
    header := join([name = token, value = fvalue], sep = ":")    # token, fvalue as in predx §3.8
    headers := list_of(header, sep = /\r\n/)
    headers & occurs.exactly(1, (name: any_case("Host")))
            & occurs.at_most(1, (name: any_case("Content-Length")))
            & occurs.none((name: any_case("Transfer-Encoding")))

`name` is a repeated label: a bare `$name` would be an error (§4.3). Each `occurs` filter is a capped counter (n+2
states: 3, 3, 2) multiplied into the loop. The condition is passed as a condition literal (positional): the
labelled-argument spelling `occurs.exactly(1, name: ...)` would NARROW the subject under the C22 addendum (§13 C31).
LEVEL: default. Expected: a block with one `Host:` line and no `Transfer-Encoding` -> match; two `host:` lines -> no
(`any_case`).

### 12.10 E-SEP: the same separator twice (a finite backreference, regular)

    date_sep(s) := join([year = /\d{4}/, month = /\d\d/, day = /\d\d/], sep = s)
    dates := each(date_sep, enumerate(/[-\/.]/))      # 3 entries, class members in codepoint order: - . /
    dates

LEVEL: default (PCRE's `\d{4}([-\/.])\d\d\1\d\d` needs `vm` in the strict subset; §13 O34). Expected: `2026-11-14`
-> match, `.index` 1; `2026.11.14` -> match, `.index` 2; `2026/11/14` -> match, `.index` 3; `2026-11/14` -> no. Over
budget (`enumerate(/\w+/)`) is a compile error giving the count.

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

### 12.12 E-CTX: assertions in set positions (the cases that decide Q1)

Each case puts an assertion where the three candidate models (§11) disagree; the answer is the RULED one (string
sets + the edge-assertion error). The answers under the other models are review Q1X-2's table. LEVEL: none applies
(compile errors).

    P := /(?<w>\w) (?<x>\w+)/
    P & (x: /^S\w*/)                                  # E-CTX-1, subject `a Sab`
    num := /\b\d+\b/
    /a${num}/                                         # E-CTX-2, subject `a12`
    @assert.none("5" & /(?<=\$)\d+/)                  # E-CTX-3
    /\w{3}/ & /\w+\b/                                 # E-CTX-4, subject `foobar`
    x & padded(/^5/)                                  # E-CTX-5
    enumerate(/(?<=a)[bc]/)                           # E-CTX-6
    headers & (name: /^[A-Z][\w-]*/)                  # E-CTX-7 (E-HTTP's headers), subjects `Host: a`, `Host: a\r\nAccept: b`

- E-CTX-1: compile ERROR (`^` at the start of the condition on x). Fix `(x: startsWith("S"))`: `a Sab` -> match
  `a Sab`. (A/B2: silent no match; B1: match.)
- E-CTX-2: compile ERROR (`\b` at both edges of the hole's set). Fix: write the boundaries in the literal around the
  hole (`/a\b${digits}\b/`, which on `a12` finds nothing: `a` and `1` are both word characters). (B1: match.)
- E-CTX-3: compile ERROR (a lookbehind at the start of an assertion argument). Under A the assertion FAILED although
  the subject `5` never matches. Fix: decide on strings (`@assert.none("5" & /\d+/ & !/\d+/)`-shaped tests), or test
  search behaviour by an example subject outside assertions (§5.6).
- E-CTX-4: compile ERROR (`\b` at the end of an `&` operand). Fix `/\w{3}\b/`: on `foobar` it reports `bar` visibly,
  from the final pattern. (A/B2: the reported match silently moves from `foo` to `bar`.)
- E-CTX-5: compile ERROR (`^` at the start of a modified filter's argument). Fix `x & padded(startsWith("5"))`.
- E-CTX-6: compile ERROR (a lookbehind at the start of an `enumerate` argument). Fix `enumerate(/[bc]/)` = `["b",
  "c"]` and put `(?<=a)` in the final pattern.
- E-CTX-7: compile ERROR (`^` at the start of the condition on a repeated label). Fix `(name: /[A-Z][\w-]*/)` (a set
  is matched ENTIRELY): both subjects -> match. (A/B2: the one-header block matches, the two-header block silently
  fails, and adding `m` to the condition flips it; review Q1R-4.)
Agreeing look-alike (no error): an assertion strictly inside a value, `/(?<v>[\d.]+)/ & (v: /\d+\b\.\d+/)` on
`3.14` -> match (the `\b` reads only characters of v).

## 13. Open questions and contradictions

Contradictions (C) are places where two notes, or a note and a ruling, give different readings; open items (O) are
places the notes leave silent or explicitly open. Each gives both readings; none is resolved here except by a
recorded ruling, cited.

RESOLVED in rev 2 (one line each; the rule now stands in the section named):
- **C2** x-mode: RESOLVED, OWNER RULED 2026-11-14 (no implicit x-mode; per-literal `(?x)`), §11.
- **C4** guard holes: RESOLVED, OWNER RULED 2026-11-14 (`(\d+)&${ <256 }`; without `&` a following item), §11.
- **C9** padded labels: RESOLVED, OWNER RULED 2026-11-14 (Reading A: string sets, `\d+`, explicit padding
  modifier), §2.4.
- **C10** transform sections and the left of `:`: RESOLVED, transforms (now filter modifiers, OWN-1) and computed
  values via match-dependent bindings (concept OWNER RULED 2026-11-14, Q6), §2.7, §4.4.
- **C11** purity vs ambiguity: RESOLVED, OWNER RULED 2026-11-14 (Q2: some parse at default, PCRE's at `vm`), §4.5.
- **C14** size-cap fallback: RESOLVED, OWNER RULED 2026-11-14 (Q5), §6.1.
- **O4** `x:` on a repeated group: RESOLVED, OWNER RULED 2026-11-14 (Q4, sequence rule), §4.3.
- **O9** large run-time parameter variant set: RESOLVED, OWNER RULED 2026-11-14 (Q5), §6.1, §12.7 (b).
- **O11** index base: RESOLVED, OWNER RULED 2026-11-14 (Q7, 1-based), §3.2.
- **O18** `records` dropping unmatched lines: RESOLVED, OWNER RULED 2026-11-14 (Q13, tiling, `gaps = "allow"`), §7.

RESOLVED in rev 3:
- **C8** comma in records vs lists: RESOLVED, OWNER RULED 2026-11-14 (C22: in a condition literal the comma
  conjoins conditions); the comma in a list literal still separates alternatives, a DIFFERENT look-alike (§0.1 L23,
  O30). predx C8's and review OWN-9's "drop the comma record" lean is overtaken by the ruling.
- **C15** in-context vs value-scoped `&`: the model part RESOLVED, OWNER RULED 2026-11-14 (Q1: string sets + the
  edge-assertion error), §11. Still open: whether `&` inside `/.../` text is rx syntax (C23).
- **C20** application equivalence for transforms: RESOLVED, OWNER RULED 2026-11-14 (OWN-1): a modified filter is a
  filter, so `padded(S)(x)` = `x & padded(S)`, §2.3, §2.7.
- **C22** the pipeline under `name:`: RESOLVED, OWNER RULED 2026-11-14 (C22 binding + addendum), §4.1.
- **C24** `ci` as a function vs a transform: RESOLVED, OWNER RULED 2026-11-14 (OWN-1): `any_case("Host")` is the
  modifier applied to the set `"Host"`, §2.7, §12.9.
- **C27** context-marked sets vs "matches ENTIRELY": RESOLVED, OWNER RULED 2026-11-14 (Q1): a set is the strings it
  matches entirely; `(x: /^S/)` is the edge-assertion error, §11.
- **O17** D196's F7 in-context lookaround: RESOLVED for set positions, OWNER RULED 2026-11-14 (Q1: refused; final
  patterns keep PCRE meaning), §11; `\K` refused, verbs, cross-operand backrefs (finite: `enumerate`; general:
  [BACKREF-FINITE]), recursion remain as listed in rev 2.
- **O25** Q1 context-marked sets TENTATIVE: RESOLVED, OWNER RULED 2026-11-14 (Q1 foundation = STRING SETS), §11.
- Review RUL-4 (right-associative `&` vs the chain label lookup): dissolved by OWN-1 (pure `&`), §4.1.
- Review RUL-10 (label arguments filter vs typed parameters check): answered by the C22 addendum (labelled
  arguments always narrow), §5.2.

STILL OPEN from rev 0:
- **C1. `&` order.** D196 (RULED): the left operand chooses the reported end. 2026-11-14: "`&` commutes, so order is
  readability only"; OWN-1 ruling (2026-11-14): "`&` is pure intersection again (order- and grouping-free)". Reading
  A: order-free = MEMBERSHIP only, the reported span still left-chooses (D196 stands for the span). Reading B: the
  expression language's `&` is order-free for the reported span too, and D196 governs only pattern-level `&` inside
  PCRE text. predx C1 proposes A's wording (not ruled). rev 3: the OWN-1 wording makes this a contradiction between
  two rulings (OWN-1 and D196), listed, not resolved.
- **C3. DEFINE bindings in the inner direction.** 2026-11-13 evening: an opted-in DEFINE holds `name := ...` bindings.
  2026-11-14: DEFINE stays ONLY as PCRE syntax inside a literal; API callers keep the inner direction (`(\d+)&${ <256
  }`). Reading A: inner-direction patterns have holes but no bindings. Reading B: inner-direction DEFINE keeps `:=`.
- **C5. Multi-index comma.** 2026-11-14 00:10: `A[1,3,5]` NOT adopted, comma kept for `A[i, j]`; the `[]` positional
  note lists `X[1,3,5]` as valid. (Review OWN-9 adds `x[[1, 3, 5]]` vs `x & [1, 3, 5]`, O30.)
- **C6. Binding a test.** 2026-11-13: binding a name to a test is an error; 2026-11-13 evening: tests sit beside
  patterns as bindings; the Q6/Q9 lean binds computed values and filters freely. Not stated as superseded.
- **C7. Value-valued maps.** 2026-11-13 `["US" => "United States"]`; 2026-11-14 views: labels are names, the value
  per branch shown is `.index`. Reading A: other values are computed labels (now bindings, §4.4) or record arrays
  (predx C7). Reading B: `=>` survives.
- **C12. Define-before-use.** 2026-11-13 BLOCK SHAPE: required; 2026-11-13 evening: forward references allowed, no
  cycles. Bounded recursion (§7) needs a self-reference at least.
- **C13. Bare label names as values.** 2026-11-13 NAME RESOLUTION: an undeclared bare name is a label; 2026-11-14
  01:00: values always `$x`. The Q6/Q9 rule ("a word is always a NAME: function, label, binding") does not say
  which in a value position; `(wname.index: ==wd)` uses a bare binding as a value while `(b: >$a)` uses `$` (§0.1
  L37). Review OWN-11's lean: computed labels follow labels, `x:` to constrain, `$x` to read (so `==$wd`).
- **C16. Precedence example.** D196: `&` tighter than `|`; the 00:10 example `x & <256 | >300` therefore parses
  `(x & <256) | >300`, and since `>300` is a label-free filter (a full rx) the program silently WIDENS to every
  canonical numeral above 300 anywhere. The example is WITHDRAWN (REVIEW FIX RUL-15): the intended reading is
  `x & (<256 | >300)` or, as a condition, `(x: <256 | >300)` (§4.1). A `precedence.section` warning (a label-free
  comparison as a top-level `|` operand beside an `&`-applied one) is PLAN (§0.1 L22).

STILL OPEN from rev 2:
- **C17. `&`'s structure.** `&` is extensional (§2.2) yet distributes over array entries and drops empty products
  (§3.2), a structural effect (`/a|b/ & /b|a/` gives [a, b] or [b, a] by which side is major). predx C17/S15
  proposes "left-major cross product"; not ruled. `.index` after `&` with an array of filters (§3.5) depends on it.
  rev 3: a "left-major" structure gives the ORDER of an `&` chain a structural effect, against the OWN-1 ruling's
  "order- and grouping-free" (listed with C1, not resolved).
- **C18. Named assertions vs the `@` rule.** Q6/Q9 lean: named failures via `leap_1900 := assert_none(...)`; import
  lean (2): "named assertions (`leap_1900 := assert.none(...)`) remain"; import lean (3): effect macros cannot drop
  `@`, only `@` forms are bare statements. A named assertion is then either `leap_1900 := @assert.none(...)` (an
  `@` inside an expression), a binding without `@` (against (3)), or not allowed.
- **C19. The kind of an assertion.** Import lean (2): assertions are "their own value kind"; §2.1: two kinds (rx,
  macro), modules not a third kind, "no boolean type". Whether an `@` effect yields a value at all is not stated.
- **C21. `count` as a value.** §2.6 / rev 0 §4.3: `count` is a library name over a set, `count($x)` a value. The
  counting ruling: occurrence filters, "NOT a count value (no number type)". Whether `count` over a search's
  occurrence set (`$x ~ rx`) survives as a value is not stated. Review RUL-13 adds: `some`/`all` are listed as
  built-ins (rev 2 §5.1), library names (§2.6) and `occurs.some`/`occurs.all` (§8); rev 3's closed built-in list
  leaves them out pending this row and C28.
- **C23. `&` in inner-direction rx text.** C4 ruling: the guard is `(\d+)&${ <256 }`, an `&` inside PCRE text. ERRATUM
  (2026-11-14): `&` is a value operator, not rx syntax; G3 needs `R&D` literal. Reading A: `&${` is a two-token
  marker of the inner direction only. Reading B: `&` is rx syntax in inner-direction strings.
- **C25. Tuple comparison arrays.** Tuples are a library macro `lex_ge([major, minor, patch], [1, 4, 0])`; but an
  array literal IS an alternation (§3.1), and the import/export discussion rejects `export([leap])` for exactly this
  ("`[leap, weekday]` = `leap | weekday`, names lost"). `[major, minor, patch]` of labels has the same problem, and
  `[1, 4, 0]` is `&`-equal to `[0, 1, 4]` (review OWN-9). The condition-literal spelling of §8 needs no tuple.
- **C26. The empty-match ERROR "opted out".** §7: in a predicate program the nullable-search case is an ERROR, with
  "no diagnostic ... when opted out"; §7.1: "Errors cannot be disabled" and `empty.search` is a WARNING name. How a
  predicate program opts out of an error (other than `& !""` or anchoring) is not stated.
- **C28. `occurs.all` vs the sequence rule.** §4.3: `x: S` on a repeated label already means all iterations; the
  counting ruling adds `occurs.all(x: S)`. Either they are synonyms or `x: S` on a repeated label means something
  else; not stated (§0.1 L36; review OWN-4 proposes one rule for all label shapes, O28).

NEW in rev 3 (contradictions; listed, not resolved):
- **C29. `isodate(x).year` vs `(x & isodate).year`.** §5.2: FORWARD `isodate(x)` is text -> fields, and the cut
  layer's note (11-14) reads `(X & isodate).weekday` as a value; §3.2: `.name` on an rx is map-view navigation
  yielding the part's PATTERN. Reading A: `.` on any rx is structural and values are only `$`-forms (`$d.year`);
  "forward `isodate(x)`" as a value form is dropped. Reading B: `p(x)` is not `x & p` for labelled patterns, and
  `.year` of an application is a value. (Review RUL-8; the draft never declared the two equal, V25.)
- **C30. What a positional argument is.** C22 addendum: "currying: the positional argument is the subject"
  (`isodate(year: S)`); OWN-1 ruling: a modifier's positional argument is the FILTER it modifies (`padded(S)`);
  §5.2: positional parameters CONSTRUCT (`between(lo, hi)`). Reading A: the addendum's sentence is about labelled
  pattern macros only. Reading B: it is general, and modifiers and constructors are exceptions to state. (Review
  RUL-F6, the application family.)
- **C31. `occurs` conditions as labelled arguments.** Counting ruling: `occurs.exactly(n, c)` with `c` "the usual
  `label: set` condition", spelled `occurs.exactly(1, name: ci("Host"))`. C22 addendum: a labelled argument in a call
  ALWAYS NARROWS the subject (`f(a: s)` = `f & (a: s)`), which would make that call `occurs.exactly(1) & (name: ...)`,
  i.e. every name in the set and a count with no condition. Reading A: pass the condition as a positional condition
  literal (`occurs.exactly(1, (name: ...))`, the spelling §12.9 uses because it holds under both rulings). Reading B:
  library filters whose parameter IS a condition take it in labelled form, an exception to the addendum.
- **C32. `!~` with an edge assertion.** RUL-5 (REVIEW FIX): `$x !~ rx` = `(x: !contains(rx))`. D193 add. 3 (stands):
  in `$x ~ rx` the value is the whole subject, so `$x ~ /^err/` = "x starts with err". Q1 ruling: in `(x:
  contains(/^err/))` the `^` is reachable through `contains`'s nullable `.*` prefix, so it is the edge-assertion
  error (§0.1 L17). So for an rx with an edge assertion the sugar's expansion is refused while the search it abbreviates
  is legal. Reading A: `!~` (and the test reading of `~`) expands to a set that reads the value as the whole subject
  (a context-free set: the strings in which a search for rx succeeds), not to `contains`. Reading B: `!~` is refused
  for an rx with an edge assertion (fix text: `startsWith`/`endsWith`). Bears on O12 (keep or drop `!~`).

Open items (rev 0, still open):
- **O1.** The meaning of a program's final expression against the subject (search vs whole-subject test). The
  empty-match rule presupposes a SEARCH MODE chosen by the caller (predx O1 lean: the caller picks); not ruled.
- **O2.** Precedence among `!`, `:`, `.`, prefix comparisons, arithmetic and `@` is stated only pairwise (C16,
  §4.1's binding).
- **O3.** Notes call several leanings "ruled" (unset label false, union type of duplicates, filtering by indexing).
- **O5.** Do a map's per-field value constraints carry into joined labels (asked Frank 2026-11-14; lean yes; predx:
  yes by construction).
- **O6.** `functions` presupposes DFA captures ([ENG-TDFA]); Q11 moves span REPORTING to `captures`; whether
  `functions` without TDFA pays a VM re-run per candidate is not ruled.
- **O7.** Weekday value type and numbering (`weekday == "Sat"` vs `weekday: 6`).
- **O8.** Checksum filters over separated digits (does `luhn` skip spaces?).
- **O10.** Resume after a rejecting callout for unanchored search (predx: the next DFA candidate; not ruled).
- **O12.** `!~` once `!` is a filter: keep (as the sugar of §2.6, REVIEW FIX RUL-5), or drop it; C32 adds the
  edge-assertion case.
- **O13.** Library files: bindings + `@export`; whether a library has a final expression (the "one final
  expression" and "unused pattern" rules, §5.1) is not stated.
- **O14.** String position out of range: CLAMP (rev 0 leaning) vs strict false (predx lean).
- **O15.** Mid-sequence placement for joined maps (`before`/`after`): deferred to a real example.
- **O16.** Group 0 find-all resume rule (`\K`-style vs lookbehind-style), cond_family.md §7 (D193 add. 5).

Open items (rev 2, still open):
- **O19.** A match-dependent binding is "a computed label of the pattern whose labels it reads": which pattern, when
  the labels it reads occur in several bindings (`$mname` in `textdate`, reached again through `rfcdate.rest`).
- **O20.** `records` tiling: how a record rx declares its separator/gap bytes (line terminators) so that tiling
  holds without `gaps = "allow"`. CONSEQUENCE (review Q1R-10): until it is settled, E-FILE fails its own tiling rule
  on every `\n` (§12.8); the review suggests a declared separator (`records(text, rx, sep = /\n/)`-shaped).
- **O21.** Bounded recursion's base case: several definitions of one name by literal argument (`value_depth(0) :=`)
  is predx's spelling; not stated as a general feature.
- **O22.** The per-binding `@warn.off` spelling; the `@each(...)` per-entry assertion spelling (both OPEN by ruling).
- **O23.** The `occurs` namespace name (MANAGER LEAN, open to Frank).
- **O24.** Export: the Q6/Q9 note's "look later: `export` as a binding attribute, imports as a compilation-unit
  setting" is overtaken by the function forms, which are MANAGER LEAN; the option (b) `_`-prefix convention is
  expressible as `@export(/[^_].*/)` but not a default (a library with no export is an error).

Open items NEW in rev 3 (review 2026-11-14-r1-predspec items dispositioned OWNER that no ruling covers; each with the
review's proposed lean, in plain words, NOT resolved):
- **O26. Is a negated filter with no label a full pattern?** (OWN-2, RUL-2.) `>=200` may stand alone (`${>=200}`,
  `@warn.off(startsWith("dead."))`) but `!<200` and `!startsWith("dead.")` may not (prefix `!` is always a filter),
  although both are well-defined regular sets. Lean: yes, a label-free `!f` is a full pattern exactly like a
  label-free `f` (the "useless in a search" worry is what the empty-match rule already catches); plus a warning when a
  negated numeric comparison meets a target with non-canonical members (`0150`, `abc`).
- **O27. Does quoting a constant decide how it compares?** (OWN-3.) `a := 256` and `b := "256"` are the same set, yet
  `x & <a` compares numbers and `x & <b` compares text (`1000` out vs in), and `@assert.same(a, b)` passes. The same
  question covers arithmetic results (does `${$y + 1}` on `0099` insert `100` or `0100`?) and leading-zero bounds
  (does `between(01, 12)` admit `1`, `05`?). Lean: make numeric vs text a property of the comparison you write, not
  of how the constant is quoted; arithmetic yields canonical numerals; width is set with the padding modifier.
- **O28. One rule for conditions on optional, repeated and never-entered labels?** (OWN-4.) On `1,7,` with a
  repeated n, "not all below 5" (`!(n: <5)`) matches while "each not below 5" (`(n: !<5)`) does not; on an optional
  label that is unset the two sentences of §4.2 disagree; `?` vs `*` around the same group flips `(n: <5)` on `end`.
  Lean: a condition holds when EVERY occurrence is in the set AND there is at least one (zero iterations = unset =
  fail); `!(x: S)` is its plain complement; `(x: !S)` = every occurrence outside S; a warning with a witness when the
  two differ for the pattern at hand; `occurs.all` an alias or removed (C28).
- **O29. Does each `some` pick its own occurrence?** (OWN-6.) Two `occurs.some` filters may use different
  iterations (filters combine independently), but §2.6 says every `some(s)` over one search set is the SAME
  occurrence. Lean: each `some(...)` picks its own witness; to make one occurrence satisfy two tests, write one `some`
  with both tests conjoined. This deletes the "two occurrences need two names" rule.
- **O30. Brackets and commas with opposite meanings.** (OWN-9, C5, C25.) `[(x: <200), (y: >55)]` is OR while `(x:
  <200, y: >55)` is AND (now ruled, C8); `x[[1, 3, 5]]` selects positions while `x & [1, 3, 5]` selects the strings
  `1`, `3`, `5`; a tuple `[1, 4, 0]` is an alternation, so its order is not part of the value. Lean (as amended by the
  C22 ruling, which keeps the comma record): tuples by name (`lex_ge(major = 1, minor = 4, patch = 0)`-shaped) so
  `[...]` means alternation everywhere.
- **O31. Metadata members and level selection.** (OWN-7, RUL-12.) `.index` and `.label` share the dot with user
  labels: for `/(?<index>\d+),(?<label>\w+)/`, `r.index` is the label or the position? Lean: a non-alphabetic
  metadata mark, or metadata as call-position built-ins (`index(x)`, `label_of(x)`), or an error for user labels
  named like a metadata member. Also unstated: how a program selects `functions`/`captures`/`vm`/`eval` (as strings
  or API options, not bare words).
- **O32. Flags of a pattern inserted in a hole.** (Q1R-11.) With no inherited flags, `q := /^\{.*\}$/` inserted in
  `/${q}/m` keeps single-line `^`/`$` and finds nothing on `{a}\n{b}`, while the same text inlined in the `m`
  literal finds both lines. Lean: a `flag.hole` warning naming the fix (`q := /.../m`), or state the flags of a
  binding explicitly.
- **O33. Two conditions on an ambiguous pattern.** (RUL-3.) `/(?<a>\d+)(?<b>\d+)/ & (a: <5) & (b: <5)` on `123`:
  each condition passes on SOME parse (true per condition, the extensional reading), no single parse passes both
  (merged narrowing: false), PCRE's chosen parse gives false. Lean: per-condition some-parse (the extensional
  reading), with the `label.ambiguous` text saying that two conditions may be met by different parses.
- **O34. Same text twice: one level for every spelling?** (RUL-7.) `\k<s>` on a 3-valued finite group needs `vm`,
  the value hole `${$s}` on the same label is default-level, and `each(..., enumerate(...))` is a third spelling.
  Lean: one rule keyed by whether the referenced language is finite, for all three spellings (links
  [BACKREF-FINITE]; if Q10 keeps the engine rule out of #6, the predicate front end must still lower `\k` on a finite
  label as it lowers `${$x}`, or refuse both).
- **O35. A label set twice in one match.** (RUL-16.) `(?J)(?<x>\d)-(?<x>\d)` is not "repeated", so `(x: <5)` is
  unspecified and `$x` silently picks the lowest-numbered group, while the look-alike repeat `(?:(?<x>\d)-?){2}` is
  under the sequence rule. Lean: the sequence rule for every label with more than one static occurrence per match.
- **O36. A search assertion.** (Q1X-5, NOTED.) No assertion can state search behaviour (E-IPV4's `256.1.1.1` ->
  `56.1.1.1`). The critic's suggestion: a library search assertion (`@assert.finds(p, "256.1.1.1", ...)`-shaped, a
  name, not a keyword). Not dispositioned by the review; recorded.
- **O37. Two modifier names this document chose.** `unpadded(n, S)` (rev 2's `pad(n)`: the filter reads a subject
  as if zero-padded to width n) and `json.quoted(S)` (rev 2's `jstr`) are placeholders under the naming rule; the
  ruling named `padded`, `any_case`, `quoted`, `length`, `month_numbered` only.
- **O38. Look-alike rows with no diagnostic.** §0.1 marks GAP rows (L20, L21 on answers, L23, L25, L29-L32, L35):
  DIFFERENT with no named diagnostic, so G0's acceptance fails on them today. Some are open items above; L20 (a padded
  target against an integer section) and L25 (`/a|b/` vs `/b|a/` under `[]`/`.index`, by design) have no item:
  whether a documented structural difference needs a diagnostic, and which warning L20 gets, are open. Also from
  OWN-15: whether the goal order G1 > G2 should be stated as G2 > G1 at the default level (what the rules do).

FAMILIES noted by the review (PLAN; not folded): value mappings (filter modifiers, computed-label bindings,
`.index`, forward value calls `days($b)`: one transducer object, RUL-F1); quantifiers and emptiness checks
(`some`/`all`, `occurs.*`, the sequence rule, `count`, `@assert.*`, the implicit checks: one `Q(source, cond)`
form, RUL-F2); same-text-twice (O34, RUL-F3); name-set selection (`import`, `@export`, `@warn.*`, `where_group` by
name, RUL-F4); the dot (O31, RUL-F5); application spellings (C29, C30, RUL-F6).

## 14. Non-goals

- Non-regular nesting (balanced parentheses, unbounded JSON) stays with PCRE recursion on the VM (`vm`) or bounded
  recursion (§7); the predicate language adds no non-regular power of its own.
- No general-purpose language: no unbounded recursion through parameterized definitions, no unbounded loops, no
  lambdas until an example needs one, no side effects beyond compile-time `@` statements, no run-time compilation of
  caller-supplied PATTERNS outside `eval`, no alphabetic keywords, no boolean or number type.
- No "best match" overload ranking; no interfaces, members, UFCS or `types()` in the first spec (§9).
- No change to plain PCRE patterns outside the opt-in; class contents `[...]` keep PCRE2's meaning (synsurv).
- No in-context reading of a pattern in a set position (refused, §11) until a measured need (D77).
- No spelling decision beyond the no-keyword rule and the modifier naming rule (placeholder throughout); no build
  (#6 not scheduled; NO BUILD GO).
- Not this document: DFA captures ([ENG-TDFA]), finite-group backreferences as an engine rule ([BACKREF-FINITE],
  its own unscheduled row), the Boolean IR mechanism and lookaround lowering (D196 add. 2), the standard library's
  content, a JSON database.

## 15. Provenance

COND-FAMILY.md notes by date/heading; "11-12" = the 2026-11-12 sections, etc. "predx" = `docs/dev/lanes/predx_report.md`.
"r1" = review `docs/dev/reviews/2026-11-14-r1-predspec.md` (finding ids from its critic files).

| section | notes consolidated |
|---|---|
| 0 | 11-12 base requirements; 11-13 COST METRICS; Frank 11-13 (#6 not scheduled), 11-14 (charter); goals are the manager's draft; rev 2: Q5 (G2), C2 + empty-match (G3), Q12 + enumerate (G4); rev 3: 11-14 Q1 critic framing (G0), r1 OWN-13 (table), OWN-14 (G3), OWN-15; the table's rows from r1 Q1R/Q1X/OWN/RUL |
| 1 | 11-14 LAYERING; 11-14 predx Q8; r1 RUL-14.4 |
| 2.1-2.3 | 11-14 fractional rx + addendum; 11-14 `!`; 11-14 SUPERSEDES field-wise `&`; D196 + add. 1-2; 11-14 import follow-up (module = map); 11-14 counting (no number type); rev 3: 11-14 RULING OWN-1 (pure `&`); r1 OWN-2, RUL-2, OWN-5, RUL-14.2 |
| 2.4 | 11-13 LITERALS DECIDE; 11-14 00:10; 11-14 RULINGS on §13 (C9); 11-14 RULING OWN-1 (`padded`); r1 RUL-14.6 |
| 2.5-2.6 | 11-13 NO CONCATENATION OPERATOR; 11-13 SEARCH notes; 11-14 00:10; D193 add. 3; 11-14 RULING Q1; r1 RUL-1, RUL-5, Q1R-6, RUL-14.5 |
| 2.7 | 11-14 RULING OWN-1 (transforms are FILTER MODIFIERS); predx S1, §8.2 (the pullback) |
| 3 | 11-14 00:10; views; spelling vs logic; index base; `[]` positional; 11-14 predx Q7; 11-14 predx gaps (ARRAYS OF FILTERS); r1 RUL-9, OWN-8 |
| 4 | 11-14 01:00; 11-13 late; 11-13 DESTRUCTURING, AMBIGUITY notes, MAPPINGS; 11-14 predx Q2, Q4, Q6/Q9; 11-14 value-vs-value (cont.); predx S3; 11-14 counting; rev 3: 11-14 RULING C22 + addendum; r1 RUL-14.1 |
| 5 | 11-13 BLOCK SHAPE, NAME RESOLUTION; 11-13 evening; 11-14 join, compose, curry, marks; 11-14 Q6/Q9 (no keywords, assertions); 11-14 import/export + follow-up (`@`); 11-14 predx gaps (ENUMERATE); predx S8; rev 3: C22 addendum; 11-14 RULING Q1; r1 OWN-7, RUL-6, OWN-10, Q1X-5 |
| 6 | 11-14 capability levels; 11-12 base requirements; 11-14 predx Q5, Q11; 11-14 RULINGS cont. (`&` at `vm`); predx S9, S10, §3.9 F33; r1 Q1X-8 |
| 7, 7.1 | 11-13 RECURSION RULE NARROWED, IMPORT, COST notes; 11-14 file_text + records; 11-14 predx Q12, Q13; predx S6, S14; 11-14 import/export + follow-up + addendum; 11-14 empty-match RULING + amendment; rev 3: 11-14 RULING Q1 (nullability in context); r1 Q1R-9, Q1R-10, Q1X-8, OWN-7, RUL-14.1 |
| 8 | 11-12 STANDARD LIBRARY; 11-13 STRING OPERATIONS; 11-13 late; 11-14 blessed callouts; 11-14 counting; 11-14 predx gaps (TUPLE CONDITIONS); 11-14 Q6/Q9 + import (assert); rev 3: 11-14 RULING OWN-1, C22 (semver comma form) |
| 9 | 11-14 predx Q8; predx §9 |
| 10 | 11-14 runtime eval + addendum |
| 11 | 11-14 outer layer, ERRATUM; 11-13 literal/hole/parameter notes; 11-14 RULINGS on §13 (C4) and RULING C2; 11-14 predx Q3, Q5, Q10; rev 3: 11-14 RULING Q1 foundation (SUPERSEDES predx Q1 / C15 / S2's context-marked sets); D193 add. 3; r1 Q1R-1, Q1X-2, Q1R-12, Q1X-1, OWN-14 |
| 12 | rev 0 sources; rev 2 rewrites per §§2.7, 4.4, 5.6, 7; E-HTTP from 11-14 counting; E-SEP from 11-14 ENUMERATE; E-DEPTH from predx §3.9 + Q12; rev 3: renamed per OWN-1; E-SEP index per r1 OWN-10; E-FILE per r1 Q1R-10/Q1X-7; E-CTX-1..6 per r1 Q1X-9, E-CTX-7 per r1 Q1R-4 |
| 13 | cross-reading of all notes, D196, D193 and the 2026-11-14 rulings (lanes predspec, predspec2, predspec3); rev 3 open items O26-O38 from r1's OWNER dispositions |
| 14 | 11-12 scoping; 11-13 late JSONL; D196 add. 2; synsurv; 11-14 predx Q10; 11-14 RULING Q1 (named in-context form only on measured need) |

Background documents: `cond_family.md` (the member inventory, machinery M1-M12, the checker product C3, D193
answers) is still the mechanism map the predicate language rides on. `cond_family_syntax_survey.md` predates the
2026-11-13/14 notes: its `&!` and `=~` spellings are superseded (`!` filter, `~`), its "opt-in, not default" and "do
not touch class contents" recommendations stand. Prior-art details the predx report left unverified (Pomsky,
Hyperscan) are answered in its scratch note (predx Q14); this document cites neither.
