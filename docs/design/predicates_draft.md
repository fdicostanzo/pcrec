# The predicate language ([COND-FAMILY] #6): a preliminary specification for critical analysis

## Changelog

- **rev 6 (lane predspec6, 2026-11-15).** Folds the owner's "type picture" ruling (CF:846-878): two value kinds (rx,
  macro), a condition is a macro, "filter" is a ROLE (CF:858); one input rule, a call fills parameters and `&` fills
  the one subject slot (CF:860); the COMMA means only "next entry" and the BRACKET says how entries relate, `[ ]` any
  one, `( )` all together, `=` labels an entry, `:` constrains an existing label (CF:863); a RECORD is never a value,
  appears only in a call, a condition or the left of a binding, is the written MAP view, one-way (CF:866); a search
  returns an rx (CF:873). NEW: §5.4 is THE grammar summary for `,` `( )` `[ ]` `=` `:` (every other section points
  at it); §0.1 L43-L47; §0.2 destructuring line; O41-O47. Changed: §2.1, §2.2, §2.3, §2.6, §2.7, §3.1 (the map
  literal `(x = /foo/ | y = /bar/)` withdrawn, LEAN), §3.2, §3.5, §4.1 (the condition binding restated in record
  terms), §4.2 (example respelled), §5.1, §5.2, §7 (what a module is, O46), §8 (tuple example), §12 (all twelve
  re-checked: unchanged), §13 (C19, O30 resolved; C5, C8, C18, C25, C29, O40 restated), §14, §15.
- **rev 5 (lane predspec5, 2026-11-15).** Folds COND-FAMILY.md from the mapping ruling (CF:749) to the end: C33-C35,
  the `!` entries and the ten 2026-11-15 entries (CF:761-845; a later entry wins over the one it corrects), and fixes
  what the rev 4 audit (audpred) found in the spec. Status marks are RULED (record line) / LEAN / OPEN. NEW §0.2
  PHASE 1 SCOPE, §0.1 L41-L42, O39-O40. Changed: §2.1 and §14 (numbers one kind, LEAN; no "no number type"), §2.2
  (`!` not in rx, PARKED), §4.6 (thresholds OPEN; example without a filter called on a subject), §5.2 (sections `&`
  only; no partial application in phase 1, currying kept), §5.4, §6.1 (quote overclaim removed; next-end caveat
  restored), §8 (`count()` first, `occurs` the fallback, refusal by budget), §11 (`^`/`$` = the FILTERED SPAN's ends,
  stated once; `(?m)`), §12.5, §12.9, §13 (C6, C21, C33-C35, O23 resolved; C23 restated).
- **rev 4 (lane predspec4, 2026-11-15).** Folded the rulings after "transforms are FILTER MODIFIERS" through "Agree with
  mapping" (C1, C20, C30-C32; patterns take no arguments; the subject is never an argument; sections).
- **rev 3 (lane predspec3, 2026-11-14).** Folded the rulings from "Q1 critic framing" to "transforms are FILTER
  MODIFIERS" and the FIX-NOW dispositions of review `docs/dev/reviews/2026-11-14-r1-predspec.md` (G0 and the
  LOOK-ALIKE TABLE, pure `&`, filter modifiers, condition binding, string sets, §12.12 E-CTX).
- **rev 2 (lane predspec2, 2026-11-14).** Folded every ruling and lean after rev 0 through the counting-occurrences
  ruling and the adopted parts of `docs/dev/lanes/predx_report.md`.
- **rev 0 (lane predspec, 2026-11-14).** First consolidation of the notes through the outer-layer note.

## 0. Status, goals, standing questions

**Status: DRAFT rev 6 (lane predspec6, 2026-11-15). NOT a ruling, NOT scheduled, NO BUILD GO** (Frank 2026-11-13:
#6 not scheduled; 2026-11-15, relayed in the predspec5 brief: "the predicate work is not a go to build as we are
still in design"). Purpose (Frank 2026-11-14): "create a preliminary predicate spec doc with our latest ideas for the
purpose of critical analysis. Provide reasoning." It consolidates the dated notes in
`docs/design/plan_row_bodies/COND-FAMILY.md` ("CF"; the source of truth; the LATEST note on a topic wins, and the
owner's QUOTED words outrank a manager paraphrase beside them), the parts of `docs/dev/lanes/predx_report.md` that
the rulings adopt, and review 2026-11-14-r1-predspec. Older background, `docs/design/cond_family.md` (survey rev 0,
D193) and `docs/design/cond_family_syntax_survey.md` (lane synsurv), is cited where still live. Every rule traces to
a note, a ruling or a review finding (§15); where they are silent or disagree, §13 lists both readings.

**SYNTAX IS PLACEHOLDER THROUGHOUT.** The owner rules semantics; spelling is a later design step (D193 add. 4).
One spelling RULE is ruled (§5.1): no alphabetic operators or statement keywords; and one NAMING rule (§2.7):
a transform's name describes the subjects it accepts. Examples use the latest spellings: `/.../` rx literals (bare rx
fragments are never admitted in the expression language), `:=` define, `,` "next entry" inside `[ ]` (ARRAY, any
one entry) or `( )` (RECORD, all entries together), `=` labels an entry, `:` constrains a label that exists (THE
grammar summary is §5.4), `==` the equality section, `X[...]` positional, `&` (pure intersection) / `where` / dot for
filtering and labels, conditions `(x: S, y: T)`, transforms as FILTER MODIFIERS (`x & padded(between(1, 12))`),
operator sections `(& f)`, `@` effect statements, modules as `m := import("m")`, 1-based indexes.

Status marks (rev 6; every mark is one of three):
- **RULED (CF:n)**: the owner's own words at line n of COND-FAMILY.md (or a D-number) cover the rule; it reaches only
  as far as his quoted words, not a manager gloss beside them.
- **LEAN**: a manager's reading or proposal, this document's consequence of a ruling, an owner "perhaps", or a
  review fix (the FIX-NOW dispositions of review r1 other than Q1 and OWN-1 carry no owner ruling); the source is
  named in parentheses (review finding id, "manager", "this document").
- **OPEN**: listed in §13.

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
CF:691); G1 > G2 > G3 > G4 is the manager's draft order. At the default level
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
| L3 | `isodate & (year: S, month: 2)` vs `isodate & (year: S) & (month: 2)` | SAME | the `( )` RECORD holds its entries together; the AND comes from the record, not the comma (§4.1, §5.4) | C22, CF:866 |
| L4 | `(major: 1, minor: >=4)` vs `(major: 1 & minor: >=4)` | DIFFERENT | the second is a compile ERROR: a label inside a value (`major: (1 & minor: >=4)`) | C22 |
| L5 | `x & (a: d)` vs `(a: d)(x)` | DIFFERENT | the second is a compile ERROR: the subject is never an argument (hint: "write `x & (a: d)`"); application has one spelling (§2.3) | 2026-11-15 RULING (supersedes OWN-5's two spellings) |
| L6 | `x & (a: d)` vs `each((& (a: d)), x)` | DIFFERENT | `each` is the STRUCTURAL per-entry map (keeps entries, labels, order; the filter is mapped through the section `(& (a: d))`, §5.3); an alternative lacking `a` is dropped by `&` with `label.unset`, an ERROR naming it under `each` | OWN-5, 2026-11-15 RULING (mapping) |
| L7 | `x: /^S\w*/` vs `x: startsWith("S")` | SAME | in a filter `^` is the start of the span being filtered (§11) | CF:732, CF:761, D193 add. 3 |
| L8 | `num := /\b\d+\b/`: `/x${num}/` vs the pasted `/x\b\d+\b/` | DIFFERENT | the hole form is the EDGE-ASSERTION ERROR ("put `\b` in the pattern that places num") | Q1X-3 (iv), Q1R-3 |
| L9 | `p := /(?<=\$)\d+/`: the program `p` (searched) vs `(n = /\d+/) & (n: p)` | DIFFERENT | the condition is the EDGE-ASSERTION ERROR; the searched final pattern keeps PCRE meaning | Q1X-3 (iii), Q1X-1 |
| L10 | `\w{3} & /\w+\b/` vs `/\w{3}\b/` | DIFFERENT | the first is the EDGE-ASSERTION ERROR (no silent move foo -> bar) | Q1X-2 |
| L11 | `alts & !/^#.*/` vs `alts & !startsWith("#")` | SAME | `^` is the filtered span's start (§11) | CF:761 |
| L12 | `"5" & /(?<=\$)\d+/` in `@assert.none(...)` vs `"5" & /\d+/` | DIFFERENT | the first is the EDGE-ASSERTION ERROR (an assertion argument is a set position, §5.6) | Q1X-5 |
| L13 | `x & padded(/^5/)` vs `x & padded(startsWith("5"))` | SAME | `^` is the start of the span the modified filter reads (§11); `padded(/\b5/)` stays the EDGE-ASSERTION ERROR | CF:761 |
| L14 | `enumerate(/(?<=a)[bc]/)` vs `enumerate(/[bc]/)` | DIFFERENT | the first is the EDGE-ASSERTION ERROR | Q1R-8, Q1X-6 (b) |
| L15 | `@warn.off(/^dead\./)` vs `@warn.off(startsWith("dead."))` | SAME | `^` is the start of the name (§11) | CF:732 (LEAN extension, §11) |
| L16 | `$m ~ /^err/` vs `m: startsWith("err")` | SAME | in a search inside a value `^`/`$` are the value's ends (D193 add. 3, §2.6) | Q1R-6, RUL-1 |
| L17 | `$m ~ /^err/` vs `m: contains(/^err/)` | SAME | `^` is the value's start in both (§11); `!~` expands without a special case | CF:732 |
| L18 | a nullable final search pattern: `/\b/` vs `/a*/` | SAME | both are nullable IN CONTEXT: `empty.search` WARNING for a one-literal program, ERROR in a predicate program (§7) | Q1R-9 |
| L19 | `(?m)^\d*` searched vs the same pattern in whole-subject mode | DIFFERENT | by MODE only: `empty.search` in search mode, none when anchored (a `^` in the pattern does not exempt) | Q1R-9 |
| L20 | `/\d\d/ & padded(between(1, 12))` vs `/\d\d/ & between(1, 12)` | DIFFERENT | GAP: the second is {10, 11, 12} by the C9 ruling (string sets, canonical numerals); no warning is named for a padded target against an integer section | C9, OWN-2 |
| L21 | `!<200` vs `>=200` | DIFFERENT | on targets with non-canonical members (`0150`, `abc`: kept by `!<200`, refused by `>=200`): GAP; in where they may stand (`${>=200}` legal, `${!<200}` the unapplied-macro error): the unapplied-macro error. §13 O26 | OWN-2, RUL-2 |
| L22 | `(x: <200 \| >900)` vs top-level `x & <200 \| >900` | DIFFERENT | inside a condition `\|` binds tighter than `:` (x in either range); at top level D196 parses `(x & <200) \| >900`, a full rx that widens the program; `precedence.section` (proposed, PLAN) | C22, RUL-15 |
| L23 | `(x: <200, y: >55)` vs `[(x: <200), (y: >55)]` | DIFFERENT | AND vs OR, said by the BRACKET (`( )` all together, `[ ]` any one; §5.4); the comma means "next entry" in both, so the look-alike the review flagged (one comma, two logics) is gone; whether the bracket difference still needs a diagnostic: LEAN no (§13 O30 RESOLVED, O38) | OWN-9, CF:863 |
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
| L38 | `isodate(x).year` vs `(x & isodate).year` | DIFFERENT | the first is a compile ERROR (a pattern takes no arguments; hint "write `x & isodate`"); whether `.year` of `x & isodate` is a value or a pattern: OPEN (§13 C29) | RUL-8, 2026-11-15 RULING |
| L39 | `A & B` vs `B & A` | SAME | the same subjects are accepted; the left operand picks the REPORTED span among overlapping qualifiers (D196), so the report may differ (§2.2) | C1 ruling |
| L40 | `isodate(year: S)` vs `isodate & (year: S)` | DIFFERENT | the first is a compile ERROR: a pattern has no parameters; hint "write `isodate & (year: ...)`"; a parameterised pattern is a macro, `date_in(years) := isodate & (year: years)` (§5.2) | CF:744 |
| L41 | `/\w+/ & /^foo/` vs `/\w+/ & startsWith("foo")` | SAME | `^` in a filter is the start of the span being filtered (the `\w+` word), not of the subject (§11) | CF:761 |
| L42 | `n := count((name: S)); headers & (n: ==1)` vs `headers & occurs.exactly(1, (name: S))` | SAME | one count, two spellings; `count()` is refused only over the BUDGET, naming the `occurs` form (§8) | CF:823 (LEAN), CF:832 |
| L43 | `[x = /foo/, y = /bar/]` vs `(x = /foo/, y = /bar/)` in value position | DIFFERENT | the second is a compile ERROR: "a record is not a value; for any one of the entries write `[ ... ]`" (§3.1, §5.4); the rev 5 map literal `(x = /foo/ \| y = /bar/)` is withdrawn (§13 O42) | CF:863, CF:866 |
| L44 | `(x)` vs `x` in value position | SAME | parentheses with one unlabelled entry are GROUPING; a one-entry record exists only where a record stands (a call `f(x)`, the left of a binding), so no value is ever a one-entry record (§5.4; §13 O41) | CF:866 (LEAN) |
| L45 | `f(1, 2)` vs `f((1, 2))` | DIFFERENT | the second is a compile ERROR: a call is the macro applied to ONE record, and an inner record would be a record used as a value (§5.2) | CF:866 (LEAN) |
| L46 | `isodate & (year: 2000)` vs `c := (year: 2000)` then `isodate & c` | SAME | a condition is a MACRO, a value; binding it is L2's case; the record is its written body, never the bound thing (§2.1; §13 O45) | CF:858, CF:866 (LEAN) |
| L47 | `[x: S]` vs `[(x: S)]` | DIFFERENT | the first is a compile ERROR: `:` constrains a label of what the record is laid against, and an array entry is laid against nothing; hint "write `[(x: S)]`" (§5.4) | CF:863 (LEAN) |

**REASONING.** The owner's framing: "complex context could cause predicates to just not work and it's not clear how
the obscure rules impact it ... that's why it was so important to me that things that look like they should do the
same thing actually do." A ranked goal without a checkable table would lose every tie to G1 (review OWN-13); the
table makes G0 testable, and a D27 spec-first author writing acceptance cases from the table alone is its natural
independent control (review "D27 recommendation").

**STATUS.** G0 as the first criterion: RULED (CF:691). G0 as a goal row and the table: LEAN (review OWN-13). Rows
L1-L2: RULED (CF:722); L3-L4: RULED (CF:698); L7-L19: RULED (CF:713 as superseded in part by CF:732 and CF:761: `^`/`$`
in a filter are the filtered span's ends); L5, L38, L40: RULED (CF:744, CF:749); L39: RULED (CF:732); L41: RULED
(CF:761); L42: LEAN (CF:823 "perhaps"; the budget rule RULED, CF:832); L23's reason and L43: RULED (CF:863, CF:866);
L44-L47: LEAN (this document's readings of CF:858-866); other rows state the rule of the section cited.

### 0.2 Phase 1 scope (what the owner said is in and out of the first build)

Nothing is scheduled and there is no build go (Status above); "phase 1" is the owner's name for the first,
base-level predicate build whenever it is chartered.
- IN: THE PREDICATE PART ITSELF, the primary goal of this design (CF:795: "the primary goal of the predicate design is
  the predicate part itself"). RULED.
- IN, and the ONLY additions to the rx language: the `${}` hole and `&` (CF:795: "extra elements added to rx like ${}
  and & are necessary parts of that"). RULED. Where `&` may stand in rx text: §13 C23.
- IN: operator sections with `&` only, `(& f)` (CF:753, C33: "start with &"). Other operators' sections on need. RULED.
- IN: a macro call binds every required parameter or is an error naming the missing one (CF:753, C34; CF:804). RULED.
- OUT: `!` inside a normal rx (`/!foo/`): PARKED for a later plan item, because its scope (the whole `foo` or just
  the `f`) is unclear (CF:795). `!` in the predicate language is unaffected. RULED.
- OUT: partial application (currying). DEFERRED from phase 1 as a scope reduction, NOT dropped: the design keeps it
  (CF:804: "we can start out phase 1 without currying and revisit later"). RULED.
- OUT: the automatic `count()` -> `occurs` rewrite: a later optimization plan item, [COUNT-TO-OCCURS] (CF:840). RULED.
- OUT unless a worked example needs it: a record on the left of a binding, `(x, y) := rx ~ /.../` (CF:866 (c): "kept
  in the design, phase 1 only if an example needs it"). RULED. No §12 case needs it (rev 6 re-check), so it is out.
- Not stated by the owner: which library pieces (§8) and levels beyond the default (§6.1) phase 1 carries.

### Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** Mostly not relevant: a language spec introduces no measured quantity. The numbers cited
   (ISO date with leap Feb 29 as a plain regex: 6,848 B object, 5.9 ms compile; CF:40; class counts in §4.6) are
   compile-time sizes or arithmetic, not timings. The budgets of §4.6/§8 (O39) are measured quantities when a build
   sets them, and must name their regime then.
2. **The independent control.** Relevant to §12 and G0: expected behaviours were checked against Python's
   `datetime`, a hand-written Luhn function and libpcre2 10.49 (review r1's kit), not against pcrec. At build: the
   PCRE2+callout oracle (studies/andspike, F9), an independent Python reference evaluator, standards' own test
   vectors as `@assert.*` statements (§5.6); for G0 a D27 author working from §0.1 alone.
3. **What moves when data is regenerated.** Relevant only through `file_text`/`import` pins (§7): a changed file
   under a `sha256` pin is a loud compile error; a re-pinned file changes the emitted automaton.

## 1. Layering

**RULE.** Two layers. FOUNDATION: value kinds (§2), operators and filter modifiers (§2), views (§3), match values and
computed labels (§4), capability levels and the reporting axis (§6), the compile-time boundary, modules and
warnings (§7). LIBRARIES, built on the foundation and changeable without it: `each`, `join`, `records`,
`file_text`, standard filters and filter modifiers (`between`, `startsWith`, `length`, `padded`, `unpadded`,
`any_case`, `quoted`), `occurs`, `assert`, tuple comparisons, blessed callouts (§8). The ORGANISATIONAL layer
(interfaces, type members, UFCS, `types()`) is CUT from the first spec (§9); interfaces may return as library
packaging after a build. Namespaces stay in the foundation (what a module is: §7, §13 O46).

**TEST OF THE RANKING.** No worked example needs the cut layer: §12 checks this case by case (E-RFC uses a plain
macro on the three fields, not an interface member).

**REASONING.** Frank: the purpose is to probe the fundamental structure; unless foundational, lower priority.
predx §9: none of thirteen further programs needed interfaces, UFCS or `types()`.

**STATUS.** Layer outline: LEAN (the LAYERING note, CF:522, is the manager's outline under Frank's framing; its "no
recursion", namespaces-as-organisational and numeric-value-type items were since changed by Q12, the module-as-map
lean and C9; review RUL-14.4). The cut: RULED (CF:583, predx Q8).

## 2. Values and operators

### 2.1 Two value kinds

**RULE.** Every value is one of TWO KINDS: an **rx** (a set of strings, extensional, §11) or a **macro** (a term
awaiting input). There is no third kind: a CONDITION is a macro; a record is not a value at all (§5.4); a binding
names whatever its expression is (`isodate := join(...)` names an rx; in `isodate & (year: 2000)` the macro is the
condition, not `isodate`). Numeric and string literals are rx: `5` = {"5"}, `"a.b"` = {"a.b"} (the dot is literal,
unlike `/a.b/`); they differ only in what a comparison means (§2.4).

ONE INPUT RULE. A macro takes input two ways: a CALL fills its PARAMETERS (the call's argument list is ONE record laid
against them, §5.2); `&` fills its one SUBJECT slot with the rx on the other side. The rx is never the thing applied
(the subject is never an argument, §2.3). So: a CONDITION (`(x: <200)`, `(a: 1, b: 2)`) = a macro with a subject and
no parameters; a TRANSFORM (filter modifier, §2.7) = a macro whose parameter is a filter and whose result is a
filter; an operator SECTION `(& B)` = only the subject open; prefix `!B` = a macro with the subject open (§2.2); an
unapplied filter modifier (`padded` alone) = a macro with its parameter open.

"FILTER" IS A ROLE, NOT A TYPE: whatever stands on the filtering side of `&` (CF:858). An rx can
take the role (`<200`, `between(3, 6)`, `startsWith("S")` and `padded(between(1, 12))` mention no label, so each is
a full rx, the set that passes), and so can a macro with its subject open (a condition, `!B`, a section). Anything
naming a label it does not define is a macro awaiting the pattern that defines it.

Phase 1 has NO partial application (a macro call binds every required parameter, §5.2); the design keeps currying
for later, when a macro with some parameters bound will be a macro too (§0.2). What a MODULE is under two kinds:
§7, §13 O46. `@` statements (§5.1) are statements, not values. There is no boolean type (a test is a filter:
`"2024" & leap` is {"2024"} or empty).

NUMBERS are ONE kind for the user: a number read from the subject (text matched by `\d+` and the like, compared and
added, §2.4, §2.5) and a count of matches (`count(...)`, §8) take the same comparisons and arithmetic. Where a number
test is evaluated (compiled into the match as a set, or computed on the result) is the compiler's choice, shown with
its cost (manager's view, CF:813). Under the two kinds a number is an rx, a set of numeral strings (this document's
consequence of CF:858, LEAN; §13 O40).

**REASONING.** The closure (a predicate denotes a pattern, 2026-11-12/13) means one algebra serves patterns,
values and tests; a condition is a term with a free variable, the same kind as a macro awaiting its subject (via `&`).
The owner's criterion for the type picture: "few types and few operators that always mean the same thing wherever
they are used" (CF:846); on conditions, "It's more like a macro". Two kinds and one input rule are the smallest
picture that covers every §12 case.

**STATUS.** Two kinds (rx, macro), a condition is a macro, "filter" a role, a binding names whatever its expression
is: RULED (CF:858; the manager's proposal the owner accepted, "I'm liking your ideas", with his correction that
`isodate` is an rx, CF:855); SUPERSEDES the rev 5 LEAN (CF:362). One input rule (call = parameters, `&` = the subject
slot): RULED (CF:860). Literals as one-string sets: LEAN. Module = map: LEAN (manager, CF:619), now in tension with
"a record is not a value" (§7, §13 O46). Numbers ONE kind for the user: LEAN (CF:823, "perhaps"; the owner's ideal, CF:813); the
11-14 "no number type" is WITHDRAWN as over-reach (CF:782 (3)); what a number is: §13 O40. No boolean type: LEAN
(manager's Q6/Q9 spelling lean, CF:595). No partial application in phase 1, currying kept by the design: RULED
(CF:753, CF:804). The earlier "assertions (their own value kind)": withdrawn by the two kinds (§13 C19 RESOLVED).

### 2.2 Operators `&`, `|`, prefix `!`

**RULE.** `&` intersection, `|` union, both EXTENSIONAL over rx operands: membership depends only on the
language, so two spellings of one language behave the same under `&`, `|`, `!`. `&` is PURE INTERSECTION:
associative and commutative, so the ORDER and GROUPING of an `&` chain never change which strings it admits (a
transform is a filter modifier, §2.7, never an `&` operand with a position). Prefix `!B` is ALWAYS A MACRO with its
subject open (it takes the filter role, §2.1): `A & !B` = A minus B; `&!` is not a separate operator. A standalone `!B` where an rx
is needed (`${!B}`, `C | !B`) is the unapplied-macro error. Macros in the filter role combine pointwise by `& | !`. `!` lives in the
expression language only: inside a normal rx literal it keeps PCRE's meaning (`/!foo/` matches the text `!foo`); a
`!` operator in the rx language is PARKED for a later plan item (§0.2).

`!<200` and `>=200` are NOT interchangeable: `!<200` keeps every target string that is not a canonical numeral
below 200, so on a target with non-canonical members they differ (`/\d{4}/ & !<200` keeps `0150`, `/\d{4}/ & >=200`
does not; `"abc" & !<200` = {"abc"}, `"abc" & >=200` is empty); they agree only where every target string is a
canonical numeral. `!<200` is a macro, `>=200` a full rx (§0.1 L21; whether a label-free `!f` is a full rx: §13
O26). There is no "positive form" lint rewrite (it would change answers).

Reported span (D196, RULED for pattern-level `&`): the left operand chooses (PCRE priority: first alternative,
greedy longer, lazy shorter), the right only filters which ends are admitted; the span SET is commutative. So
`A & B` and `B & A` ACCEPT THE SAME SUBJECTS; D196's left operand picks the REPORTED span among overlapping
qualifiers, so the report may differ (§0.1 L39; C1 RESOLVED).
Precedence (D196): concatenation, then `&`, then `|`; inside a record entry `&` and `|` bind tighter than `:`
and `=`, and the comma is no operator (it ends an entry; §4.1, §5.4). In the expression language there is no concatenation operator (§2.5).

**REASONING.** Extensional `&` keeps arrays and rx "the same". `!` as a filter: a standalone complement is useless
in a search and VM-hostile, while under `&` it is bounded. A pure `&` is what the owner's look-alike criterion (G0)
asks of the most common operator: rev 2's right-associative `&` made reordering or parenthesizing a chain with a
transform in it change the answer silently (review OWN-1, RUL-11).

**STATUS.** `&` extensional, `!` a filter: RULED (CF:328, CF:376). D196: RULED (D196). `&` pure intersection, order-
and grouping-free: RULED (CF:722, OWN-1), SUPERSEDES the right-associative `&` lean. The `!<200` / `>=200` correction
and the dropped lint: LEAN (review OWN-2, RUL-2). C1: RULED (CF:732): same matches, the report may differ. No `!`
inside a normal rx: RULED (CF:795), PARKED, the spelling question NOT closed (CF:795 corrects CF:758).

### 2.3 The unapplied-macro error

**RULE.** An unapplied macro where an rx is required is a compile error naming the fix: "filter `x: digit` has
no target; write `T & (x: digit)`"; "modifier `padded` has no filter; write `padded(between(1, 12))`". THE SUBJECT IS
NEVER AN ARGUMENT: application of a FILTER has ONE spelling, `x & f` (`x & (a: digit)`, `x & padded(S)`); this is the
one input rule of §2.1 (a call fills parameters, `&` fills the subject slot; CF:860). A call
that passes the subject (`(a: digit)(x)`, `p(x)`, `padded(S)(x)`) is a compile error naming the fix ("write `x &
p`"). An alternative of x lacking the label is DROPPED (with the `label.unset` warning, §4.2), never an error.
`each(f, A)` is NOT an application spelling: it is the STRUCTURAL per-entry map (§5.3), which keeps entries, labels
and order and is an error on an entry lacking the label (§0.1 L6); a filter is mapped through an operator SECTION,
`each((& f), A)` (§5.3).

**STATUS.** The unapplied-macro error: LEAN (manager, CF:362). `each` out of the equivalence, lacking label = drop:
LEAN (review OWN-5). One application spelling, the subject never an argument (withdraws the rev 3 spellings `(a:
d)(x)`, `rx & f` = `f(rx)`, `p(x)` = `x & p`): RULED (CF:749, "Agree with mapping"); C20 RESOLVED by it.

### 2.4 Comparisons are unary sections on string sets

**RULE.** Comparisons are UNARY ONLY: `<256`, `>=lo`, `==5` denote sets, attached by `&` like everything else. A
prefix comparison takes ONE ATOM (literal, label value, binding, call, field access, parenthesized expression) and
binds tighter than `&`, `|`, `!`. The LITERAL decides the reading: `<256` = integers 0..255, `<"256"` =
lexicographic strings, `2.5` decimal, `0x100` hex. Comparisons are on the STRING SET: an integer section contains
CANONICAL numerals of VARIABLE WIDTH (the `\d+` shape: no leading zeros, sign or decimal point unless the literal
has them). Padded text is compared through the explicit `padded` modifier (§2.7): `/\d\d/ & between(1, 12)` is
{10, 11, 12} ("correct because the \d\d means two digits", CF:774) and is WRONG for months; write `/\d\d/ &
padded(between(1, 12))` or the wider pattern `/\d{1,2}/ & between(1, 12)`. There is no "compares by value" reading. `between(lo, hi)` is INCLUSIVE.
Decimal is exact decimal, never binary floating point.

**REASONING.** Every binary comparison is an intersection with a section. Literal-decides means declared types are
needed only where no literal fixes the reading (value vs value, §4.6). A comparison never silently reinterprets the
text: padding is a visible modifier on the filter.

**STATUS.** Unary: RULED (CF:250, Frank's proposal). Literals decide: RULED (CF:43). String sets, `\d+` integers, the
explicit padding modifier: RULED (CF:573, C9) and CONFIRMED (CF:774: "\d\d & between(1,12) would only match 10-12
... that is correct because the \d\d means two digits"; the "compares by value" reading is not adopted). CANONICAL
(no leading zeros) is this document's reading of "`\d+`", supported by CF:774's "to get between to ignore leading 0":
LEAN (review RUL-14.6); E-IPV4's `01.2.3.4` out depends on it. The name `padded`: RULED (CF:722; the confirmation's
own spelling, CF:774). Exact decimal: LEAN. Whether the reading belongs to the literal's quoting or to the comparison:
§13 O27.

### 2.5 No concatenation operator; arithmetic

**RULE.** The expression language has no concatenation operator: sequencing is written inside a literal
(`/${a}-${b}/`) or by `join`. `+ - * %` are arithmetic only, on numbers (§2.1): subject numbers can be added and
filtered (`($x + $y) & <50`, `$y + 1`, day differences). Value concatenation is insertion or a library name
(`concat(x, y)`).

**REASONING.** Avoids the overload trap (`"12" + "34"` = 46 or "1234"?); with no juxtaposition, a name after an
expression always starts a binding (one-token look-ahead, §5.1).

**STATUS.** No concatenation operator: LEAN (CF:69). Arithmetic on subject numbers: RULED (CF:782 (1): "\d+ numbers can
be added, filtered <256"). Arithmetic result width (`${$y + 1}` on `0099`): §13 O27.

### 2.6 Search

**RULE.** `$x ~ rx` = search inside a value (unanchored). A SEARCH RETURNS AN RX: the OCCURRENCE SET, i.e. the
search pattern narrowed to what occurs, under PCRE iteration order (non-overlapping, leftmost, continue after the
match; the C find-all iterator's order). It has the two views of every rx (§3.1): the ARRAY view is the occurrences
in order (one entry per occurrence; the view is structural, §3.4, so two equal occurrences are two entries); the MAP
view is the search pattern's labels (`d.year` = the set of the occurrences' years). `d := $m ~ /.../` binds that rx;
`(x, y) := $m ~ /.../` lays a record over the same rx's fields (by position: the search pattern's labels in group
order), so x and y each name an rx (the set of that label's strings over the occurrences); no record is bound either
way (§5.4; phase 1 only if an example needs it, §0.2). The VALUE searched is the whole
subject of that search: inside the slashes `^` and `$` are the value's start and end, and no assertion sees text
outside the value (D193 add. 3; `$x` is a one-string set, context-free, §4.1, §11). `some`, `all` are library names
over a set; `s[i]` indexes occurrences (§3.2). Every `some(s)` over the same set in one predicate denotes the SAME
occurrence (two occurrences need two names; §13 O29). `$x !~ rx` is a TEST, sugar for the condition `(x:
!contains(rx))`; `^`/`$` in `rx` are the value's ends in both. Membership is `x & a`; no `in`.

**REASONING.** Search results are values, not globals (Frank: "Even Perl had the awkward $1"). One quantifier name
(`some`, not `any`). The value-as-subject reading is D193 add. 3's ruled meaning for a predicate's regex test.

**STATUS.** Meaning (occurrence set): RULED (CF:74, Frank's proposal); a search returns an rx, its array and map
views, `(x, y) := ...` a record laid over its fields: RULED (CF:873, CF:866 (c)); one entry per occurrence (equal
occurrences stay two entries) and positional destructuring by group order: LEAN (this document); the `~` operator:
LEAN (review RUL-14.5).
`^`/`$` bound to the value: RULED (D193 add. 3; CF:732). `!~` as `x: !contains(rx)`: LEAN (review RUL-5; keep or
drop: §13 O12). `count` over an occurrence set: §8 (`count()` yields a number, LEAN, CF:823). Binding a name to a
test: allowed (§13 C6 RESOLVED).

### 2.7 Transforms are FILTER MODIFIERS

**RULE.** A TRANSFORM is a macro FILTER -> FILTER (its parameter is a filter and its result is a filter, the one
input rule of §2.1, CF:860): given a filter S it returns a NEW FILTER that accepts the subjects
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
padded(S)`, `(x: padded(S))` (the subject arrives via `&` or `label:`, never as an argument, §2.3); `&` stays pure intersection (§2.2), so a modified filter may stand
anywhere in a chain. A modifier without its filter argument where a filter is needed is the unapplied-macro error
(§2.3). `!padded(S)` is an ordinary filter (the complement of a filter). A modified filter's argument is a SET
POSITION (§11): `^`/`$` inside it are the argument's own start and end (`padded(/^5/)` = `padded(startsWith("5"))`); `\b` and edge
lookarounds are the edge-assertion error (§11). The variable-width lexicographic lint (`compare.width`) suggests `unpadded(n, ...)`.

**REASONING.** One mechanism (the pullback) collapses rev 0's transform sections, pattern -> value mappings, `jstr(p)`
and the binary forms into one closure theorem (predx S1, §8.2). Frank: "The problem is the name. Trim or unpad imply
they are doing something to the subject. But they are not. They are changing the filter to ignore elements of the
subject." A filter -> filter macro needs no operator and no position in an `&` chain, so `&` stays order- and
grouping-free (G0, review OWN-1/RUL-11), and C1/C20/C22's transform cases dissolve.

**STATUS.** RULED (CF:722, OWN-1: filter -> filter, the pullback, nesting in reading order, the naming rule, the
docs rule), SUPERSEDES the right-associative `&` pipeline (`x & unpad & between(1, 12)`), the `->` / `;` stage ideas,
and the earlier function forms `unpad(S)` / `length(<=20)` read as images. Names `padded`, `any_case`, `quoted`,
`length`, `month_numbered`: RULED (CF:722). `unpadded(n, S)` and `json.quoted`: LEAN (this document's names under the
naming rule, §13 O37).

## 3. Views

### 3.1 Array view and map view

**RULE.** An rx has two STRUCTURAL views. ARRAY view = its top-level alternatives (flat): `/a|b|c/` has 3 entries,
`/abc/` is an array of one, `/(?:a|b)|c/` has 2. MAP view = its labelled groups (a tree; nesting gives paths
`d.year`). Counts differ: `/(?<y>\d{4})-(?<m>\d\d)/` = array 1, map 2; `/(?<a>x)|(?<b>y)|z/` = array 3, map 2.
Map order = PCRE group number. A labelled alternation where each alternative is exactly one named group is the
ALIGNED case, written as an ARRAY with labelled entries: `[x = /foo/, y = /bar/]` IS the rx `(?<x>foo)|(?<y>bar)`
(`[ ]` = any one entry, `=` labels an entry, §5.4; `[1, 3, 5]` = `1|3|5`). Unlabelled entries are index-labelled.
Reverse lookup (which branch matched) is reading the accept-state label (`.index`).

THE WRITTEN FORMS OF THE TWO VIEWS. `[ ... ]` is the written form of the array view and the RECORD `( ... )` is the
written form of the map view; there is NO third view. The record is never a value (§5.4): it appears only laid
against something that has fields (a macro's parameters, a pattern's labels, a result's groups). The relation is
ONE-WAY: an rx can be viewed as a record (its groups are its fields); a record is never read as an rx. The rev 5 map
literal `(x = /foo/ | y = /bar/)` is WITHDRAWN (a `( )` in value position would be a record used as a value; the
array form above says the same thing; §0.1 L43, §13 O42). The closure "a record of rx is their sequence" was
considered and NOT adopted: it would reverse the no-concatenation lean (§2.5) and lose entry boundaries (`(1, 40)`
and `(14, 0)` would both be `140`); sequencing stays with `join` and literals.

**REASONING.** Frank: "Maps are the labeled groups. The interpretation between the two is different and can have
different counts"; arrays and maps are perspectives on an rx, not types.

**STATUS.** RULED (CF:343, two VIEWS; SUPERSEDES ONE TABLE CONSTRUCT and `{Jan: 1}` / `["US" => ...]`; value-valued
maps: §13 C7). The record as the written map view, no third view, one-way, the sequence closure not adopted: RULED
(CF:866). The labelled array as the one spelling of the aligned case and the map literal withdrawn: LEAN (this
document; CF:542's spelling was itself a lean; §13 O42). The metadata members `.index`/`.label` vs user labels of those names: §13 O31.

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

**STATUS.** `[]` positional only: RULED (CF:553). 1-based: RULED (CF:583, predx Q7). Filters over 1..n: LEAN (review
RUL-9). Multi-index `X[1, 3, 5]`: if adopted it is the array reading, any one of the positions = `X[1|3|5]`
(CF:863); whether to adopt: §13 C5.

### 3.3 Holes and groups are single entries; `|` concatenates arrays

**RULE.** Expression `|` CONCATENATES arrays (each operand contributes its top-level alternatives; appended
entries take lowest PCRE priority). An rx GROUP or a `${}` HOLE is ONE entry. With `x := /(a|b|c)/`: `x | /d/`
has 2 entries; with `x := /a|b|c/`: `x | /d/` has 4; `/${x}|d/` has 2 for either (§0.1 L24). A hole is an atom for
correctness (`/${x}d/` = `(?:a|b|c)d`). Expression parentheses are precedence only. `join` of an empty array is the
empty string.

**STATUS.** LEAN (manager, CF:385; ADD = `|`). The `array.hole` warning: LEAN (proposed by review OWN-8, PLAN).

### 3.4 Extensional vs structural operations

**RULE.** EXTENSIONAL (`& | !`, comparisons, filter modifiers) depend only on the language. STRUCTURAL (indexing,
`each`, `join`, `where`, `.label`, `enumerate`, entry counts) read the SPELLING: `/a|b/` and `/b|a/` are equal
under `&` but differ under `[1]` (and in PCRE priority). Internal rewrites (altcls, alt_normal_form) never change
user-visible structure. Field-wise narrowing that keeps other entries is structural (`each_group(&, rx, (x: d2))`),
never `&`.

**STATUS.** RULED (CF:328, CF:385). The structural effect of `&`'s distribution over entries is unstated: §13 C17.

### 3.5 Arrays of filters and filter modifiers

**RULE.** Closure one level up: an array of rx is an rx (alternation); an ARRAY OF MACROS is a macro, so an array
in the filter role filters pointwise (`t & [f, g]` = `(t & f) | (t & g)`) and an ARRAY OF FILTER MODIFIERS is a
filter modifier (`[padded, any_case](S)` = `padded(S) | any_case(S)`). The `[ ]` bracket gives "any one entry" in
every case, and the comma only separates entries (§5.4). A MIXED rx/macro array is an error (fix: write the rx entry
as a section, `(& /x/)`).
Entries must share arity. `.index` keeps the original positions when entries drop, so `ipv4 & cidrs` reports which
entry admitted the match.

**REASONING.** Frank: "an array of rx is an rx. An array of filters|macros is macro?" Classification against a
table (predx §8.3 item 1) becomes `pattern & table` with no new construct.

**STATUS.** RULED (CF:644, ARRAYS OF FILTERS); arrays of modifiers restated under OWN-1 (CF:722); "a list of
filters" as the `[ ]` any-one reading: RULED (CF:863); "filter" read as the role of a macro: CF:858.

## 4. Match values

### 4.1 `x:` constrains, `$x` reads; condition literals

**RULE.** `x: S` = the set of WHOLE MATCHES whose label x is in S (a condition, a macro awaiting the pattern that
defines x). `$x` = the VALUE captured in this match (a one-string set, context-free, §11). `x:` is ALWAYS the
constrained side; `$x` is ALWAYS a value used (operand, insertion `${$x}`, output). Capture-vs-capture is `x: <$y`
(§4.6). `$x & ...` used AS A CONDITION is an ERROR: "did you mean `x: ...`?". The left of `:` is a label PATH
(`d.year: <2000`), never an expression: a computed value is constrained through a computed label (§4.4).

CONDITIONS ARE RECORDS LAID AGAINST LABELS. A condition is written as a RECORD `( ... )` (§5.4) whose entries are
`label: S`; it is laid against the labels of the pattern it meets by `&`. The RECORD holds its entries together
(the AND comes from the record, not the comma, CF:866 (b)); the COMMA only ends an entry. An entry runs to the next
comma or the closing paren, and inside an entry `&` and `|` bind tighter than `:` (the C22 binding, restated in
record terms; every answer is unchanged, §13 O43). So:
- all of several conditions = one record: `(major: 1, minor: >=4)` = `(major: 1) & (minor: >=4)`;
- any one of several = separate records joined by `|`, or an array of them: `(major: 2) | (major: 1, minor: >=4)`
  (= `[(major: 2), (major: 1, minor: >=4)]` in the filter role, §3.5);
- a set after a label needs no parentheses: `(x: <200 | >900)`, `(month: padded(between(1, 12)))`;
- `(major: 1 & minor: >=4)` is ONE entry, `major: (1 & minor: >=4)`, a compile ERROR (a label inside a value), not a
  misreading;
- `:` outside a record has nothing to constrain: at top level `P & x: S` is an ERROR "write `P & (x: S)`", and so is
  `[x: S]` ("write `[(x: S)]`", §0.1 L47).
A condition is a MACRO (§2.1): written in value position (an argument, `occurs.exactly(1, (name: S))`; a binding,
`c := (year: 2000)`; an array entry) the record is its written body and the macro is the value; the record itself is
never bound (§0.1 L46; §13 O45).
The binding reads the same at top level and after a label (G0). In a chain `P & Q & (x: ...)`, x is looked up in
the other operands of the chain (`P & Q`; `&` is order- and grouping-free, so the whole flattened chain); a label in
both is AMBIGUOUS (error naming both); an unknown label is an error listing those available.

PATTERNS TAKE NO ARGUMENTS. A pattern has no parameters, so the call form `isodate(year: S, month: 2)` is a compile
error with the hint "write `isodate & (year: ...)`"; the one spelling is `isodate & (year: S, month: 2)`, a condition
literal with the binding above, which always NARROWS the subject (§5.2). The labelled-argument form of rev 3 (the C22
addendum's `p(a: s)` = `p & (a: s)`) is WITHDRAWN; the C22 binding rule stays, for condition literals only. A
parameterised pattern is a macro (`date_in(years) := isodate & (year: years)`, §5.2). `:` constrains a label that
exists, `=` labels an entry (in a call, the label is a parameter name: `sep = "."`); §5.4.

**REASONING.** Frank: "x: represents a fraction of the search object deconstructed": the pattern is the schema, a
match a row, labels its columns, `x:` a WHERE clause. Avoids the trap that `($x & <200) & ($y & >55)` forces x = y.
ONE condition form (`label: set`) for every condition. On the binding, Frank: `month: unpad & between(1, 12)` "is
somewhat structural because it's combined with the comma. & binds tighter" (the call form he also named is withdrawn,
CF:744; the binding reads the same in `isodate & (year: ...)`).

**STATUS.** Condition records: RULED (CF:255). One condition form, the left of `:` a path: RULED (CF:595, Q6 concept).
Binding (comma separates, `label:` up to the comma, `&`/`|` tighter than `:`): RULED (CF:698, C22), SUPERSEDES
"`name:` takes one operand term". `=` sets a parameter: RULED (CF:706). Patterns take no arguments, the call form
withdrawn: RULED (CF:744: "It can't take arguments anymore correct?", answered correct). The top-level `P & x: S` error
and the flattened chain lookup: LEAN (this document's consequences of the ruled binding). Comma records `(x: <200, y:
>55)`: RULED (CF:698). The AND from the record, the comma "next entry", `:` constrains an existing label: RULED
(CF:863, CF:866 (b)); the binding restated in record terms and the `[x: S]` error: LEAN (this document, §13 O43); a
condition written in value position denotes the macro: LEAN (§13 O45).

### 4.2 Unset labels

**RULE.** A comparison on an UNSET label is false (its `!` true); a condition naming a label that is unset for a
match fails for that match; WARN (`label.unset`) when a plain reference can be unset. This keeps extensional `&`
consistent: `[x = /\d/, y = /[a-z]/] & (x: /[0-5]/)` = `[0-5]` (the alternative lacking x drops, §2.3; rev 5
spelled the labelled alternation as the withdrawn map literal, §3.1).

**STATUS.** LEAN (CF:173); cited as "ruled" by a later note (§13 O3). That warnings have names: RULED (CF:666); the name
`label.unset`: LEAN (manager's list, review RUL-14.1). The two sentences disagree on `(x: !<5)` for an unset x, and
on zero-iteration repeated labels: §13 O28.

### 4.3 Repeated and duplicate labels

**RULE.** At the default level a repeated label follows the SEQUENCE RULE: `x: S` constrains ALL iterations; the
quantified forms are the `occurs` library (§8: `occurs.some((x: S))`, `occurs.exactly(n, (x: S))`, ...); a bare
`$x` on a repeated label is an ERROR naming the quantified forms. At `vm`, `$x` is PCRE's last iteration (what
`\k<x>` sees). Duplicate names (`(?J)`, `(?|`): plain `$x` gives the lowest-numbered set group; the static TYPE of a
duplicate label is the UNION of the definitions that can set it. Structurally, `alt.x` returns EVERY entry labelled
x as an array in group order; `alt.x[1]` (first in the PATTERN, compile time) differs from `$x` (the MATCH's value).

**REASONING.** "All iterations" is substitution into the loop body, the only pure lowering (predx §2.1, O4); the
last-iteration rule would need captures inside a loop.

**STATUS.** Sequence rule: RULED (CF:583, predx Q4), SUPERSEDES "plain `$x` = last iteration" at the default level.
`occurs` as a library: RULED (CF:682); its role as the FALLBACK to `count()`: LEAN (CF:823) with the budget rule RULED
(CF:832); the namespace name `occurs`: RULED in use (CF:782: "use 'occurs' module like occurs.at_least(3, ...)").
Duplicate labels by index: LEAN (CF:400); union type cited "ruled" (CF:350; §13 O3). A duplicate label set twice in
one match under `x: S`: §13 O35. The `occurs` condition argument is a parenthesised literal: RULED (CF:732, C31).

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

**STATUS.** Computed labels: LEAN (foundation per the LAYERING note, CF:522). Match-dependent binding as THE spelling:
LEAN (manager, CF:595; the concept RULED there), SUPERSEDES the `with` placeholder and predx's `with`. Which pattern a
binding attaches to when its labels occur in several: §13 O19.

### 4.5 Ambiguity

**RULE.** A label is AMBIGUOUS when two accepting parses give it different spans (decidable). At the default level
a condition on an ambiguous label passes if SOME parse passes (one automaton); a `label.ambiguous` WARNING shows a
witness, the two parses, which one PCRE chooses, the consequence and a fix where one exists. At `vm` the condition
uses PCRE's chosen parse. Library types are checked unambiguous at their labels. Every occurrence of the same
application denotes ONE parse (merged narrowing).

**REASONING.** The default level is a promise; only some-parse keeps it; for unambiguous labels the readings
coincide, so the difference is confined to exactly the patterns the warning flags (predx C11).

**STATUS.** RULED (CF:583, predx Q2). Resolves C11. Some-parse per condition vs merged narrowing for two conditions on
one pattern (`(a: <5) & (b: <5)` on `123`): §13 O33.

### 4.6 Value-vs-value relations, priced by class count

**RULE.** A comparison between two match values (`(b: >$a)`, `(day: padded(<=days_in($year, $month)))`,
`(wname.index: ==wd)`) is a RELATION, run the cheapest correct way. The values are passed to value macros as
parameters (`days_in($year, $month)`); a FILTER is never called with them (`leap($year)` is the subject-as-argument
error, §2.3; the leap test is `$year & leap`, inside the library's `days_in`). Its cost is the CLASS COUNT of the
earlier label(s): the number of classes the earlier labels enter the relation with (raw = |dom|; through a regular
twin = its class count). The manager's answer to "how practical" (CF:659-663; the owner has not replied, so the
tiers and numbers are LEAN and the thresholds §13 O39): SMALL (calendar 24, state/ZIP ~50, weekday-vs-date 7, check
digits 10/11) = one automaton at the default level; LARGE (times of day 1,440: borderline; dates within 15 days:
~3.65M) = a default-level ERROR printing the count and the fixes, or a linear arithmetic check under `functions`;
UNBOUNDED (`b: >$a` over arbitrary `\d+`) = not regular, `functions` only. The compiler computes the count BEFORE
building; [COST-EXPLAIN] shows it.

**REASONING.** Turns "too large" into an explainable number; predicts E-CAL (24) vs E-NEAR (3.65M). Present it as
"a relation, run the cheapest correct way", never as "always one automaton".

**STATUS.** Value-vs-value comparisons, typed and class-count priced: RULED as a concept (CF:657-659: "VALUE-VS-VALUE
comparisons: AGREED, Frank asked how practical"). The SMALL / LARGE / UNBOUNDED tiers and their numbers are the
manager's ANSWER to that question (CF:659-663), which the owner never replied to: LEAN; the thresholds are §13 O39. A
count against another label's value is such a relation: LEAN (CF:682).

## 5. Macros, bindings, statements

### 5.1 Program shape, bindings, no keywords

**RULE.** A program = bindings, expressions, calls and `@` STATEMENTS, with ONE final expression (the program's
pattern); newlines are layout (whitespace and newlines are free between expression tokens: long logic goes in `:=`
definitions, literals stay short). A binding starts `name :=`. There is ONE kind of binding: `name := expression`,
and the name names whatever its expression is, an rx or a macro (CF:858); a definition head `m(p1, p2) :=` makes a
macro (§5.2); a record on the left (`(x, y) := ...`, §2.6) is design only, out of phase 1 (§0.2). The bound kind
decides use in a hole: an rx inserts its set (a pattern a sub-pattern, a one-string value its literal text), a
macro with only its subject open (a condition, a section) is a guard (§11). A binding
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

**STATUS.** Block shape: RULED (CF:68). One kind: LEAN (CF:115). No alphabetic keywords: RULED (CF:595). `@` statements,
the unused-pattern and bare-statement errors: LEAN (manager, CF:619, on Frank's prefix suggestion). String enum values
and the closed built-in list: LEAN (review OWN-7). Define-before-use: §13 C12. Bare label names as values: §13 C13.
How a program selects `functions`/`captures`/`vm`/`eval` (§6.1): §13 O31.

### 5.2 Macros and parameters

**RULE.** `m(p1, p2) := body` makes a macro. THE SUBJECT IS NEVER AN ARGUMENT (it arrives via `&` or `label:`, §2.3).
A CALL IS THE MACRO APPLIED TO ONE RECORD (CF:866 (a)): the parentheses of `f(...)` are a record (§5.4) laid against
the macro's parameters, its positional entries by position, its labelled entries (`=`) by parameter name; a record
inside that record would be a record used as a value, an ERROR (`f((1, 2))`, §0.1 L45). An entry that is itself a
condition (`occurs.exactly(1, (name: S))`) passes a MACRO, not a record (§4.1). Every argument is a PARAMETER:
POSITIONAL arguments are the REQUIRED parameters in declared order (`between(1, 12)`,
`padded(S)`, `occurs.exactly(1, cond)`, `pair(p) := /${p},${p}/`), KEYWORD arguments are OPTIONAL SETTINGS with
defaults (`join(a, sep = ".")`), and ANY parameter may also be passed by name (`between(low = 1, high = 12)`): one
rule for every macro. A pattern is not a macro and has no parameters: calling one is a compile error ("write
`isodate & (year: ...)`", §4.1). A PARAMETERISED pattern is a macro: `date_in(years) := isodate & (year: years)`.
Every labelled pattern keeps its labels as fields, reached by a condition literal (`isodate & (year: 2000)`; fully
constrained = formatting). Operators are macros, and an operator SECTION is the macro with its left operand open:
`(& B)` is a macro with only the subject open (the subject on the left; CF:860), sections compose (`(& isodate & (year: 2024))`, `(& !B)`), and a
section is how a filter is passed where a macro is wanted (`each((& isodate), dates)`, §5.3). Sections START with
`&` only; sections of other operators come on need (C33). NO PARTIAL APPLICATION in phase 1: a macro call binds
every required parameter or is a compile error naming the missing one (`between(low = 1)` = "missing `high`"); a
section is the one way to leave a hole. The DESIGN keeps currying (a macro with some parameters bound is a macro)
for after phase 1 (C34; §0.2). Macros expand at compile time, inlined per use; cost is per USE. No lambda until an
example needs one (D77).

Typed parameters: `m(x: T)` narrows x by T (in a definition head, `:` constrains the parameter the head declares,
§5.4), and the POSITIONAL argument must lie WITHIN T; a broader or partly
overlapping argument is an error showing a dropped witness and the explicit conversion. A condition literal applied by `&`
never gets that check: it always NARROWS the subject (`isodate & (year: <2000)` silently drops `5`, which `/\d{4}/`
cannot hold). At NARROWING SITES (typed parameters, condition literals, an `&` whose operands come from definitions) an
empty intersection from pure parts is an ERROR; a dead branch WARNS (`dead.branch`); nothing when emptiness is match-
or parameter-dependent; NEVER inside an `@assert.*` argument, whose emptiness is the assertion's own subject (§5.6).
`m(p: pure)` makes a match-dependent argument an error ("pass `pattern($x)`"). Built-in `pattern($x)` = the label's
static pattern.

**STATUS.** Macro bindings: RULED (CF:124). `=` sets a parameter vs `:` filters, a condition literal narrows: RULED
(CF:706). Patterns take no arguments, a parameterised pattern is a macro: RULED (CF:744). The subject is never an
argument, positional = required parameters, keywords = optional settings, any parameter by name, operator sections,
no lambda: RULED (CF:749; C20/C30 RESOLVED). Sections start with `&` only: RULED (CF:753, C33). No partial application
in phase 1: RULED (CF:753, C34); the design keeps currying for later: RULED (CF:804, which says C34 does not supersede
CF:308). A call = the macro applied to one record: RULED (CF:866 (a)); the nested-record error and a condition
argument passing the macro: LEAN (this document; §13 O45). Typed-parameter containment: LEAN (CF:149). The empty-intersection error scoped to narrowing sites: LEAN
(review RUL-6). `pattern()`/`pure`: LEAN. Overloading: LEAN, NOT phase one (CF:163). `(x & isodate).year`: §13 C29.

### 5.3 Structural macros: `each`, `each_group`, `where`, `join`

**RULE.** Macros are passable values, FENCED: compile-time only, over finite declared arrays, structural operators
only. `each(f, A)` applies f per entry, keeps labels and order, returns an array (the structural per-entry map, not
an application spelling, §2.3). f is a MACRO whose parameters the entry fills (`each(triple, ...)`, `each(capture, a)`),
or a FILTER passed as an operator SECTION: `each((& isodate), dates)` maps the filter over the subjects, and sections
compose (`(& isodate & (year: 2024))`, ruled 2026-11-15, §5.2); over several arrays it ZIPS by position (unequal lengths = error naming both counts).
`each_group` zips BY LABEL. `join(a, sep = s)` concatenates entries in declared order; `sep` is a set; joined parts
stay navigable labels (`(c.A: <200)`, `c[1]`), free when unread. Family: in-order fixed = `join`; in-order repeated =
`list_of(X, sep = ...)`; any-order fixed = `&` of labelled parts (JSONL); candidate sugar `any_order(a, sep = ...)`.
Caller-visible captures are a library macro: `capture(x) := /(?<${x.label}>${x})/`, `join(each(capture, a), sep =
".")`, exported like any binding (§7).

**Ordinal parameter.** The iteration ORDINAL (dense, starts at `index =`, default 1), `x.index` (original position)
and `x.label` (original name) differ once an array is sliced; the ordinal is a PARAMETER the macro declares
(`capture(x, i) := /(?<f_${i}>${x})/`); `each` passes it as the second argument when the macro takes one.

**STATUS.** LEAN (CF:278 join, CF:289 compose instead of an option, CF:300 each's bindings). Mapping a filter by a
section: RULED (CF:749). Ordinal default 1: per the 1-based ruling. Per-field constraints carrying into joined labels:
§13 O5. The rev 0 `export capture(x) := ...` keyword form is superseded by `@export` (§7).

### 5.4 The marks: THE grammar summary for `,` `( )` `[ ]` `=` `:`

This is the ONE place these marks are defined; every other section points here. Inside `/.../` none of this applies:
rx text has PCRE's meaning (`\d{1,3}`, `(?<y>...)`, `[^,]`, `/${p},${p}/`).

| mark | where it may appear | what it means |
|---|---|---|
| `,` | only between ENTRIES inside `[ ]` or `( )` (a call's parentheses are a `( )`) | "next entry"; it never carries logic (no AND, no OR, no dimension) |
| `[ e1, e2, ... ]` | value position; and as the index bracket `X[...]` | ARRAY: ANY ONE entry. Of rx: an alternation; of macros: a macro (a list of filters, §3.5); mixed: error. `X[...]` selects positions, any one of those listed (`X[1, 3, 5]` = `X[1\|3\|5]`, if the multi-index is adopted, C5) |
| `( e1, e2, ... )` | ONLY laid against something with fields: (a) a CALL's argument list, against the macro's parameters (also a definition head `m(p1, p2) :=`, which declares them); (b) a CONDITION, against a pattern's labels; (c) the LEFT of `:=`, against a result's groups (design only; out of phase 1, §0.2) | RECORD: ALL entries together, positional or labelled. NEVER A VALUE: it cannot be bound, stored or returned. The written form of the MAP view (§3.1); one-way |
| `( e )` | value position, no comma, no label mark | GROUPING (precedence only); a one-entry record exists only in positions (a)-(c) (§13 O41) |
| `=` | `label = e` as an entry of `[ ]` or of a call record | gives the entry its LABEL: a group name in an array (`[year = /\d{4}/, ...]`), a parameter name in a call (`sep = "."`) |
| `:` | `label: S` as an entry of a condition record (the label may be a path, `d.year: S`); `p: T` in a definition head | CONSTRAINS a label that EXISTS (the pattern's label; the parameter the head declares). Elsewhere an error (`P & x: S`, `[x: S]`) |
| `:=` | statement start | binds a name to an rx or a macro (§5.1) |

ENTRY EXTENT: an entry runs to the next `,` or the closing bracket; inside it `&` and `|` bind tighter than `:` and
`=`, so `(x: <200 | >900)` and `[month = /\d\d/ & padded(between(1, 12)), ...]` each hold ONE entry (§4.1, C22).
A record written where a VALUE is needed is an error (`(x = /a/, y = /b/)`: "a record is not a value; for any one of
the entries write `[ ... ]`", §0.1 L43), except a record of `label: S` entries, which denotes its CONDITION, a macro
(§4.1; §13 O45). Other marks: `(& f)` is an operator section (§5.2); `==` is the equality section; `@` marks an
effect statement.

**STATUS.** The comma as "next entry", `[ ]` any one, `( )` all together, `=` labels, `:` constrains an existing label:
RULED (CF:863). The record never a value and its three positions: RULED (CF:866). Spellings: placeholders (D193 add.
4). The table's placement of definition heads under (a), the `( e )` grouping rule, the entry extent restated for
`=`, and the condition exception: LEAN (this document; §13 O41, O43, O44, O45). `@`: LEAN (manager, CF:619).
SUPERSEDES rev 5's "`,` separates conditions in a condition literal and arguments in a call" and "`=` BINDS a label
inside a map/list literal" (the map literal is withdrawn, §3.1).

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

**STATUS.** RULED as design (CF:648: "I love it. Enumerate go." = design adoption; #6 unscheduled). Codepoint order for
class members: LEAN (review OWN-10). Edge assertions refused: RULED (CF:713, CF:761 (3)). Finite-group backreferences
as a GENERAL engine rule are not #6: [BACKREF-FINITE] (§11, §14); the levels of the three same-text spellings: §13
O34.

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

**STATUS.** Concept (compile-time assertions): RULED (CF:595, Q9). Library form `assert.some` etc.: RULED (CF:608,
Frank's own `assert := import("assert")`, `assert.some("2024" & leap)`); `@` prefix: LEAN (manager, CF:619),
SUPERSEDES `check A == B` and the `assert_some(...)` built-ins. Set position: RULED (CF:713). The empty-intersection
exemption: LEAN (review RUL-6). A library SEARCH assertion (review Q1X-5): not adopted, §13 O36.

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
non-regular operand on each candidate span; the reported span follows D196 ([PRED-SPLIT]). CAVEAT (CF:63): D196's
left operand chooses the reported end, so when the verify rejects the preferred end the next end must be tried; for
that match the verify falls back to the VM.

**REASONING.** An RE2-class promise with far more expressive power (G2). Independence: a user may want
linear-time callouts without backtracking, or spans without callouts. Under the ruled string-set model (§11) no
set-position use carries context state, so G2 needs no regular-lookaround lowering for conditions (review Q1X-8).

**STATUS.** Levels: LEAN (CF:472, "Lean ADOPT"). The promise "linear, automaton code only" (automaton split and
parameter-only computations at default; `functions` = functions over captured text): RULED (CF:583, predx Q5;
resolves C14 and O9). `&` at `vm`: RULED (CF:657, "AGREED"; the note's "the spec must state it" is the manager's
text, not a quote); the next-end caveat: LEAN (CF:63, the [PRED-SPLIT] filing). Performance-trade rules: RULED
2026-11-12. `functions` presupposes DFA captures ([ENG-TDFA]): §13 O6. How a program selects a level: §13 O31.

### 6.2 What a default-level program reports

**RULE.** Three outputs, three costs: (a) the match SPAN: default, free; (b) ACCEPT-CLASS values (`.index`,
computed labels with finite class counts: weekday, region, card brand, per-group classes combined at output):
default, free (a lookup on the accept state); (c) named-group SPANS (`$year` as text): the `captures` opt-in (a
tagged DFA, [ENG-TDFA], or the VM). The default output is span + accept-class values.

**STATUS.** RULED (CF:583, predx Q11).

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
  returns a MODULE of the file's exported bindings; member access is navigation by name (`json.row`). WHAT A MODULE
  IS under the two value kinds is OPEN (§13 O46): rev 5 called it a MAP (the aligned map case), usable whole as a
  pattern when every entry is an rx; but a module holds macros, so it is not an rx, and a record (the written map
  view) is never a value (CF:866), yet `json := import("json")` binds it. Lean: a module is a compile-time NAMESPACE
  that `:=` names, not a value (never passed, stored, returned or used whole as a pattern). A library file exports with `@export(names)`: every module label whose NAME is in the rx
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
silent defaults" for data files (the CRLF trap becomes an error). Modules add no value kind (O46's lean: a
namespace, not a value); import and
export as functions over name-sets add no keyword, and one name-selection rule serves import, export and warnings.
The empty-ENTRY error rejected legitimate optional parts and missed `/\d*/`; the real hazard is a final pattern that
reports an empty find, which is a fact about the pattern in context (review Q1R-9).

**STATUS.** Bounded recursion: RULED (CF:583, predx Q12, low priority, one example), REFINES CF:58. file_text +
records: LEAN (CF:419). Tiling: RULED (CF:583, predx Q13). Import/export as functions, `@export` filter,
no-export error: LEAN (manager, CF:608, CF:619, on Frank's proposals); module = map: LEAN, put in question by
CF:858/CF:866 (§13 O46); import resolves to exactly one file, argument a set of names: RULED (CF:630). Empty-match rule: RULED (CF:666), SUPERSEDES the empty-ENTRY error and `skip_empty`;
nullability in context: RULED (CF:713); only the MODE exempts: LEAN (review Q1R-9). String option values: LEAN (review
OWN-7). Prerequisite list: LEAN (review Q1X-8). The untiled-range wording: LEAN (review Q1R-10). Cost surfacing: LEAN
(CF:41). The `trim` / `\r` trap of rev 0 is subsumed by tiling (§13 O18 RESOLVED).

### 7.1 Named warnings

**RULE.** Every warning has a STABLE NAME in dotted families (a contract, stated in the spec): `empty.search`,
`dead.branch`, `label.unset`, `compare.width`, `label.ambiguous`, `warn.unused`; proposed by review 2026-11-14-r1
and not adopted: `precedence.section`, `array.hole`, `flag.hole`. Control is by `@` effects, rest of file:
`@warn.off("compare.width")`, `@warn.off(startsWith("dead."))` (a label-free value filter is a full rx; the look-alike
`@warn.off(/^dead\./)` is the same set, `^` being the name's start, §0.1 L15), `@warn.off(/.*/)`; the reverse `@warn.error(/.*/)` (a
strict build); a per-binding form (spelling OPEN); and a compiler option for a whole build (like `-Wno-`). SELECTORS
ARE A SET OF NAMES AS AN RX, the same name-selection rule as import and export: no `*` wildcard (`"*"` is the
literal name `*`, matches nothing). Errors cannot be disabled (the edge-assertion error included). An `@warn.off`
that suppresses nothing raises `warn.unused` (itself suppressible).

**STATUS.** That warnings have names and can be disabled: RULED (CF:666: "warnings need names and the user must be able
to disable them"); selectors as an rx: RULED (CF:677: "use an rx instead of wild card purely for consistency"). The
list of names: LEAN (manager's list, review RUL-14.1). rev 2's `transform.noop` is gone: a modifier without its
filter is the unapplied-macro error (§2.3).

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
  `exactly(n, c)`, `at_least(n, c)`, `at_most(n, c)`; `c` is the usual condition, passed as a parenthesised literal
  (`occurs.exactly(1, (name: set))`; C31 RESOLVED); constant (or caller-parameter) n at default; cost = a capped
  counter (n+2 states) multiplied in, shown by [COST-EXPLAIN]; a count against another label's value is a priced
  relation (§4.6). The module NAME tells the user these are counts of matches.
- `count(...)` FIRST, `occurs` AS THE FALLBACK: `count(c)` yields the number of occurrences meeting `c`, a number used
  with the ordinary comparisons and arithmetic like a subject number (`n := count((name: any_case("Host")))`, `headers
  & (n: ==1)`; §0.1 L42). There is NO positional rule against `count()`: it is accepted wherever it is written, and
  the compiler refuses it only when building it exceeds the BUDGET (its state cost), the refusal naming the `occurs`
  form as the fix. Below the budget the compiler may RECOMMEND the `occurs` form (a named warning) as the way to reduce
  states. A later, separate plan item, [COUNT-TO-OCCURS] (not phase 1): where the compiler can PROVE the answers do not
  change, it rewrites a `count()` test into the `occurs` form itself. What `occurs` saves over `count()` for the same
  test belongs to the lowering section of a later revision; the budget: §13 O39.
- TUPLE COMPARISONS are a library macro, no syntax. The rev 5 spelling `lex_ge([major, minor, patch], [1, 4, 0])`
  passed tuples as values, which the type picture forbids: a `[ ]` is an alternation (any one entry, so its order is
  not part of the value) and a record is never a value (CF:863, CF:866). Candidate rewrite (LEAN, §13 C25): `version
  & lex_ge(1, 4, 0)`, a macro whose call record is the bound tuple and whose SUBJECT, arriving by `&`, supplies the
  other tuple as its labels in group order (map view), with a compile error when the counts differ; it needs a
  call record of variable length (§13 O47). The phase-1 spelling needs no tuple: "version at least 1.4" is `semver &
  ((major: >=2) | (major: 1, minor: >=4))`: the record holds its entries together, `|` gives any one (§4.1).
- `assert` (§5.6): `some`, `none`, `same`.
Candidate content (a follow-up initiative): network, time, identifiers, communication, checksummed numbers; each
tested against the standard's OWN vectors (as `@assert` statements), the callout oracle and the laws; each shows
its DFA column.

BLESSED CALLOUTS: emitted C text, so the artifact stays self-contained. Blessed = PURE, BOUNDED, TOTAL,
ORACLE-TESTED, and DECLARES ITS REGULAR TWIN where one exists (luhn, weekday, days_in), with its class count
(§4.6): the compiler picks automaton vs callout. First contents: numbers, dates, checksums, network, text; Unicode
normalisation deferred. The unblessed escape hatch is PCRE `(?C)`. Home: its own directory/tests/journal like
memfn/. A callout in DFA context returns a DFA-friendly verb; plain FAIL needs the VM.

**STATUS.** Standard library: RULED as a follow-up initiative (CF:38). Blessed callouts: LEAN (CF:461, "Lean ADOPT").
`when`: RULED (CF:184, "Add when"). Filter modifiers and their names: RULED (CF:722; `unpadded`, `json.quoted`: §13
O37). `occurs` family: RULED as a library (CF:682); the name: RULED in use (CF:782). `count()` first, `occurs` the
fallback: LEAN (CF:823, "perhaps the solution is both"). `count()` refused only on BUDGET, `occurs` recommended to
reduce states, no positional rule: RULED (CF:832: "i would refuse count() on budget or as a recommended way to reduce
states rather than rules"); the budget as a labelled measured quantity: LEAN (manager's note, CF:832; §13 O39). The
automatic rewrite: RULED as a LATER plan item (CF:840). Tuples as a library macro: RULED (CF:644), SUPERSEDES predx's
tuple-on-the-left-of-`:` syntax (S12); its placeholder argument spelling is replaced (CF:866; the candidate:
LEAN, C25). The comma form of the semver condition: RULED (CF:704).

## 9. Cut from the first spec

**RULE.** Not in the first spec: INTERFACES (`type(...)`, `isodate: date`), TYPE MEMBERS declared with a type,
SCOPE-LIMITED UFCS (`d.weekday` resolving to a scoped macro), `types()`. Interfaces may return after a build as
LIBRARY PACKAGING (a set of required labels with value types, checked by inclusion per field, at the module export
boundary). The NO-SEMANTIC-OVERRIDE rule (two compliant formats holding one date must agree) stays as a rule for
that return. Namespaces stay (§7, §13 O46; a definition's labels are dotted paths).

**REASONING.** predx §9: none of thirteen programs needed them; UFCS adds a third resolution rule to `.` (the
metadata members are already one: §13 O31).

**STATUS.** RULED (CF:583, predx Q8). SUPERSEDES rev 0 §9's interface, member, UFCS and `types()` rules.

## 10. Eval

**RULE.** `x & eval($fmt)` is a CONDITION known only at match time, opaque to analysis; the static matcher finds
candidates and eval filters them. DFA-only, the same automaton code as compile-time `records()`. Only as an
explicit MODULE ("requires module 'eval'" otherwise; the artifact declares the runtime dependency), with a BUDGET
(exhaustion is a distinct result) and a cache keyed by pattern string. The workhorse is the caller-PARAMETERISED
matcher (§11); self-describing files are a demonstration, not a driver.

**STATUS.** LEAN (an idea, late in #6; CF:430 runtime eval + addendum).

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
hole's set (together: FILTERS, each applied to a SPAN of the subject), and a compile-time set (an `enumerate` argument,
an `@assert` argument, a name set for `import`/`@export`/`@warn`, a computed value, a `records` entry).

THE FILTERED SPAN (stated once; CF:761). In a filter, `^` and `$` mean the START and END OF THE SPAN BEING FILTERED,
not of the subject. `/\w+/ & /^foo/` accepts the words that start with `foo`, exactly as `/\w+/ & startsWith("foo")`
(§0.1 L41); `P & (x: /^S\w*/)` constrains x's own start (L7); `alts & !/^#.*/` drops entries starting `#` (L11). The
lone program `/^foo/` is different because it is a FINAL pattern, searched in the subject: there `^` is the subject's
start (or a line start under `(?m)`). This RESTORES the 2026-11-13 understanding ("b was in the span context of a",
CF:56 "in-context stays for pattern-level &") in exactly this sense, and it SUPERSEDES the 2026-11-14 Q1 entry's
listing of `^`/`$` among the errors (CF:713-717); the foundation stays STRING SETS (CF:761 (1)). A compile-time set
has no filtered span; there `^`/`$` are the string's own ends (this document's extension, LEAN).

An assertion that would READ BEYOND THE FILTERED SPAN is a COMPILE ERROR naming the fix (CF:761 (3)): `\b` at the
span's start or end, and (LEAN, the manager's reading) a lookaround that can read outside the span, reachable at its
start through a nullable prefix or at its end through a nullable suffix; the property is decided statically on the
pattern. `^`/`$` are NOT in this class:

    "`\b` in the condition on x reads text outside x: put `\b` in the pattern that places x"

Assertions strictly INSIDE the span keep PCRE meaning (`(x: /\d+\b\.\d+/)`: the `\b` reads only x's own characters).
MULTILINE (C35, CF:753): an explicitly written `(?m)` keeps PCRE's meaning inside the span (`^`/`$` also at line
breaks within it); without it `^`/`$` are the span's ends; never does either read outside the span. VALUES (`$x`, a
one-string set), transform images (what a modified filter reads, §2.7) and compile-time sets are CONTEXT-FREE. In a
SEARCH inside a value (`$x ~ rx`, §2.6) the value is the whole subject of that search, so `^`/`$` are the value's ends
(D193 add. 3). FINAL patterns and `records` record rx are SEARCHED in their subject and keep full PCRE meaning,
context assertions included. Nullability for the empty-match rule is computed IN CONTEXT (§7). A named in-context form
(a library call, no keyword) is added only on a measured need (D77).

HOLES `${expr}`: every hole denotes a SET OF STRINGS and matches one of them: a value inserts LITERAL TEXT (never
re-parsed), a pattern inserts a sub-pattern (`${isodate & (year: 2000)}` = a sub-pattern insertion); a hole's
set is a set position (a `\b` or edge lookaround inside it is the error above; write the assertion in the literal around the
hole). In the inner direction (an API caller passing a PCRE string) a GUARD is written with an explicit `&`:
`(\d+)&${ <256 }`; a hole after an atom WITHOUT `&` is a FOLLOWING item (`(\d+)${ <256 }` = digits followed by a
numeral below 256). Generalized backreferences (`(?<y>\d{4})-${$y + 1}`); holes are order-free; holes in typed SYNTAX
POSITIONS (`\d{${n}}`, `[${a}-${b}]`) supply that position's type from a finite set; holes never change structure
seen outside. Run-time PARAMETERS (`limit := param(/\d{1,4}/)`) are read-only per match, validated against their
type, read AS LATE AS POSSIBLE; computations on parameters only are default-level (§6.1).

**REASONING.** Making PCRE text a literal gives G3 without a mode switch; free-form multi-line layout belongs to the
expression language, not to literals (C2); the strict subset applies only where a literal sits inside a larger
program (review OWN-14). The Q1 foundation: review r1 compared context-marked triples (A), value-scoped string sets
(B1) and string sets composed in context (B2); the rule set is string-set shaped, and rev 2's argument for A did not
discriminate (its cases are FINAL patterns, searched under every model; Q1R-12, Q1X-1). Under A or B2 look-alikes
fail SILENTLY (`\w{3} & /\w+\b/` moves the match; a `^` condition on a repeated label passes one header and fails
two); under B1 others do (`n: p` dead for a lookbehind `p`). With `^`/`$` bound to the filtered span (CF:761) the `^`
look-alikes agree with `startsWith`; every remaining divergence needs an assertion that reads outside the span, a
static property, and refusing exactly those leaves no silent failure and no unbuilt lowering at the default level
(G0, G2). Nullability in context is A's one real gain, adopted. The KIND of a hole decides its insertion, never the
content (no injection); a guard needs `&` so the hole rule has no exception (C4).

**STATUS.** Outer layer: LEAN (CF:564, "Lean ADOPT"). Literal leanings incl. the strict subset: RULED (CF:56, "I like your
suggestions"); the subset scoped to literals inside a larger program and the one-literal program = today's pattern:
LEAN (review OWN-14). No implicit x-mode: RULED (CF:577, C2). STRING SETS: RULED (CF:713, CF:761 (1)). In a filter
`^`/`$` = the ends of the span being filtered: RULED (CF:761 (2), SUPERSEDES the part of CF:713 that listed `^`/`$`
among the errors); its extension to the compile-time sets (no span is filtered there; `^`/`$` = the string's ends):
LEAN (this document). Assertions reading beyond the filtered span refused: RULED for `\b` (CF:761 (3)); edge
lookarounds in the same class: LEAN (manager's reading, CF:761). `(?m)` written explicitly: RULED (CF:753, C35).
Context-free values, transform images and compile-time sets, nullability in context, a named in-context form only on
measured need: RULED (CF:713). The three candidates and the restated reasoning: LEAN (review Q1R-1, Q1X-2, Q1R-12,
Q1X-1). Guard holes with `&`: RULED (CF:573, C4). Holes: RULED (CF:80, CF:81). Parameters: RULED (CF:84); the
interface rides [IFACE-PUSH]. `&` and `${}` as the only rx additions: RULED (CF:795). Finite-group backreferences as
regular: a general engine row, [BACKREF-FINITE] (RULED, CF:583, predx Q10: not #6). `&` in rx text: §13 C23.

## 12. Worked examples (acceptance cases)

Each case: the program (placeholder spelling), the capability level it needs, and expected behaviour on a few
subjects. Subjects are searched with PCRE semantics (leftmost, then the left operand's priority) unless the program
anchors. Weekdays, day differences and Luhn results were checked with Python (`datetime.date.isoweekday`, a
hand-written Luhn), not with pcrec; PCRE behaviours (E-IPV4, E-DEPTH, E-FILE, E-CTX) were checked with libpcre2 10.49
by review 2026-11-14-r1-predspec. Libraries are modules (`d := import("dates")`, §7). No §12.1-12.11 case puts an
assertion in a set position, so none of them depends on the Q1 model; §12.12 holds the cases that do.

REV 6 RE-CHECK (the type picture, CF:846-878; per-case record in `docs/dev/lanes/predspec6_report.md`): all twelve
cases are UNCHANGED token for token. Every comma in them sits in a call record, a condition record, a `[ ]` array or
rx text (§5.4); every `[ ]` is an array read as any one entry (an alternation of names or strings) or passed to a
structural macro that reads its entries in order (`join`, §3.4); every `( ... )` is a call, a condition or grouping;
no case passes a tuple or a record as a value, and none needs a record on the left of a binding (§0.2). Two open
items touch cases without changing their spelling: the module bindings (`json := import("json")`, E-JSONL, E-IPV4, E-HTTP, E-DEPTH; §13 O46)
and a condition passed as an argument (`occurs.exactly(1, (name: ...))`, `count((name: ...))`, E-HTTP; §13 O45).

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
(held under libpcre2); a boundary is the user's to write, in the final pattern around the hole: `/\b${ipv4}\b/` on
`256.1.1.1 and 10.0.0.1` finds `10.0.0.1` only (the `\b` belong to the final pattern, not to the hole's set, §11).
The assertions run at compile time and are decided on strings (§5.6).

### 12.4 E-LUHN: checksummed card numbers

    card := /\d{4}(?: ?\d{4}){3}/ & luhn & startsWith("4")
    card

`luhn` (weighted digit sum mod 10) is REGULAR (~20 states), a filter declaring its regular twin; IBAN mod 97 and
ISBN-10 mod 11 are the same class. The literal keeps its space (no implicit x-mode, §11). LEVEL: default. Expected:
`4111 1111 1111 1111` -> match; `4111 1111 1111 1112` -> no (Luhn fails); `5500 0000 0000 0004` -> no (Luhn valid,
fails `startsWith("4")`). Whether `luhn` skips the spaces: §13 O8.

### 12.5 E-CAL: calendar validity (a relation between labels)

    isodate := (as in 12.2)
    dim   := days_in($year, $month)             # computed label: 24 classes (12 months x leap)
    valid := isodate & (day: padded(<=dim))
    @assert.some("2024-02-29" & valid)
    @assert.none("2023-02-29" & valid)
    valid

A value-vs-value relation with class count 24 (§4.6): one automaton. `days_in` is a value macro whose parameters
are the two values; the leap test (`$year & leap`) sits inside it, so no filter is called with a subject (§2.3; rev 4
wrote `days_in($month, leap($year))`, which called the filter `leap` with the subject and used its result as a truth
value). LEVEL: default. Expected (whole subject):
`2024-02-29` in; `2023-02-29` out; `2024-04-31` out; `2024-13-01` out (not an isodate). The notes' `month: \d\d &
between(1,12)` is WRONG (only 10, 11, 12 pass): C9, confirmed CF:774; `padded` is the fix (§0.1 L20).

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
states: 3, 3, 2) multiplied into the loop. The condition is passed as a parenthesised literal (a required positional parameter, C31 RESOLVED 2026-11-14); the
labelled-argument spelling `occurs.exactly(1, name: ...)` is not used.
The `count()` spelling (§8) is the same test: `n_host := count((name: any_case("Host")))` and `headers & (n_host:
==1)`; at these bounds it is within any budget, so it is accepted, and the compiler may recommend the `occurs` form.
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
sets, `^`/`$` = the filtered span's ends, the edge-assertion error for `\b` and edge lookarounds; CF:761). E-CTX-1, 5
and 7 do not error; E-CTX-2, 3, 4, 6 do. The answers under the other models are review Q1X-2's table. LEVEL: none applies
(compile errors).

    P := /(?<w>\w) (?<x>\w+)/
    P & (x: /^S\w*/)                                  # E-CTX-1, subject `a Sab`
    num := /\b\d+\b/
    /a${num}/                                         # E-CTX-2, subject `a12`
    @assert.none("5" & /(?<=\$)\d+/)                  # E-CTX-3
    /\w{3}/ & /\w+\b/                                 # E-CTX-4, subject `foobar`
    x & padded(/^5/)                                  # E-CTX-5
    enumerate(/(?<=a)[bc]/)                           # E-CTX-6
    headers & (name: /^[A-Z][\w-]*/)                  # E-CTX-7 (§12.9's headers), `Host: a` / `Host: a\r\nAccept: b`

- E-CTX-1: NO error; `^` is x's start: `a Sab` -> match `a Sab`, same as `(x: startsWith("S"))`. (A/B2: silent no
  match; B1: match.)
- E-CTX-2: compile ERROR (`\b` at both edges of the hole's set). Fix: write the boundaries in the literal around the
  hole, `/a\b${/\d+/}\b/`, which says what the pasted text says: on `a12` it finds nothing (`a` and `1` are both
  word characters). (B1: match, unlike the pasted text.)
- E-CTX-3: compile ERROR (a lookbehind at the start of an assertion argument). Under A the assertion FAILED although
  the subject `5` never matches. Fix: assert on strings without the lookbehind (`@assert.some("5" & /\d+/)`); search
  behaviour is shown by an example subject, not by an assertion (§5.6, §13 O36).
- E-CTX-4: compile ERROR (`\b` at the end of an `&` operand). Fix `/\w{3}\b/`: on `foobar` it reports `bar` visibly,
  from the final pattern. (A/B2: the reported match silently moves from `foo` to `bar`.)
- E-CTX-5: NO error; `^` is the start of the modified filter's argument, same as `x & padded(startsWith("5"))`.
- E-CTX-6: compile ERROR (a lookbehind at the start of an `enumerate` argument). Fix `enumerate(/[bc]/)` = `["b",
  "c"]` and put `(?<=a)` in the final pattern.
- E-CTX-7: NO error; `^` is the start of each `name` value: both subjects -> match, same as `(name: /[A-Z][\w-]*/)` (a
  set is matched ENTIRELY). (A/B2: the one-header block matches, the two-header block silently
  fails, and adding `m` to the condition flips it; review Q1R-4.)
Agreeing look-alike (no error): an assertion strictly inside a value, `/(?<v>[\d.]+)/ & (v: /\d+\b\.\d+/)` on
`3.14` -> match (the `\b` reads only characters of v).

## 13. Open questions and contradictions

Contradictions (C) are places where two notes, or a note and a ruling, give different readings; open items (O) are
places the notes leave silent or explicitly open. Each gives both readings; none is resolved here except by a
recorded ruling, cited.

RESOLVED (one line each; the rule now stands in the section named; RULED marks cite the record):
- **C1** `&` order: RULED (CF:732), §2.2, §0.1 L39. **C2** x-mode: RULED (CF:577), §11. **C4** guard holes: RULED
  (CF:573), §11. **C11** purity vs ambiguity: RULED (CF:583, Q2), §4.5. **C14** size-cap fallback: RULED (CF:583,
  Q5), §6.1. **C20** application: RULED (CF:749), §2.3. **C22** the pipeline under `name:`: RULED (CF:698, CF:706),
  §4.1. **C24** `ci`: RULED (CF:722, `any_case`), §2.7.
- **O4** (CF:583, Q4), **O9** (Q5), **O11** (Q7, 1-based), **O18** (Q13, tiling), **O25** (CF:713, string sets): RULED,
  §4.3, §6.1, §3.2, §7, §11.
- **C6** binding a test (rev 5): the 2026-11-13 "a TEST is an error" was corrected the same day: a test IS a pattern
  and may be bound and inserted (CF:81, Frank's correction; CF:117: one kind of binding, tests sit beside patterns),
  §5.1.
- **C8** comma in records vs lists: RULED (CF:698), RESTATED by the type picture (rev 6, CF:863): the comma means
  only "next entry" in both; the BRACKET says how entries relate (`( )` all together, `[ ]` any one); answers
  unchanged, §5.4, §0.1 L23.
- **C19** the kind of an assertion (rev 6): RULED (CF:858): two value kinds; an assertion is not a value kind; `@`
  forms are statements (§2.1, §5.6). Whether one can be NAMED: C18.
- **O30** brackets and commas with opposite meanings (rev 6): RULED (CF:863): the comma has one meaning and the
  bracket carries the relation, so `(x: <200, y: >55)` vs `[(x: <200), (y: >55)]` differ by the bracket alone (L23);
  `x[[1, 3, 5]]` vs `x & [1, 3, 5]` differ by the TOOL (position vs language, §3.2), both brackets reading any one.
  The review's lean "tuples by name" is overtaken (a record is never a value, CF:866); the tuple question is C25.
- **C9** padded labels: RULED (CF:573), CONFIRMED (CF:774): string sets, `\d+`, explicit `padded`, §2.4.
- **C10** transform sections and the left of `:`: filter modifiers (RULED, CF:722) and computed values via
  match-dependent bindings (concept RULED, CF:595), §2.7, §4.4.
- **C15** in-context vs value-scoped `&`: the model RULED (CF:713, CF:761: string sets; `^`/`$` = the filtered span's
  ends; reading beyond it refused), §11. `&` inside `/.../` text: C23.
- **C21** `count` as a value (rev 5): `count(...)` yields a number used like a subject number, LEAN (CF:823,
  "perhaps"); refused only over the budget with `occurs` named, RULED (CF:832); the 11-14 "NOT a count value (no
  number type)" is withdrawn (CF:782 (3)), §8. `some`/`all` as built-ins or library names: C28.
- **C27** context-marked sets vs "matches ENTIRELY": RULED (CF:713): a set is the strings it matches entirely; `^` in
  a filter is the filtered span's start (CF:761), §11.
- **C30** what a positional argument is: RULED (CF:732, CF:749): positional = required parameters, keywords =
  optional settings, any parameter by name, §5.2.
- **C31** `occurs` conditions: RULED (CF:732): a parenthesised literal, `occurs.exactly(1, (name: any_case("Host")))`,
  §8, §12.9.
- **C32** `^`/`$` and edge assertions in a filter: RULED (CF:732), CONFIRMED and stated by the owner (CF:761): `^`/`$`
  mean the start and end of the span being filtered; `\b` that would read beyond it is refused, §11.
- **C33** operator sections (rev 5): RULED (CF:753, "start with &"): sections start with `&` only (`(& f)`, the
  subject on the left; `(& !B)` covered); other operators on need, §5.2.
- **C34** partial application (rev 5): RULED (CF:753, "start no"; CF:804): phase 1 has none (a call binds every
  required parameter or is an error naming the missing one; sections are the one way to leave a hole); the DESIGN
  keeps currying (CF:308) for after phase 1 (Reading A of rev 4 is the later design, Reading B the phase 1 build),
  §5.2, §0.2.
- **C35** `(?m)` inside a value (rev 5): RULED (CF:753, "agree"): an explicit `(?m)` keeps PCRE meaning inside the
  span (line breaks within it); without it `^`/`$` are the span's ends; never reads outside, §11.
- **O17** D196's F7 in-context lookaround: RULED for set positions (CF:713, CF:761 (3): an assertion that would read
  beyond the filtered span is refused; final patterns keep PCRE meaning; the 2026-11-13 span-context understanding,
  CF:56, is restored for `^`/`$`), §11. `\K` refused; verbs, cross-operand backrefs (finite: `enumerate`; general:
  [BACKREF-FINITE]), recursion remain as listed in rev 2.
- **O23** the `occurs` namespace name (rev 5): RULED in use (CF:782: "use 'occurs' module like occurs.at_least(3,
  ...)"; "i suggested an 'occurs' type module that would handle structural predicates").
- The call form `isodate(year: S)` and the labelled-argument addendum: WITHDRAWN, RULED (CF:744), §4.1, §5.2.
- Review RUL-4 (right-associative `&` vs the chain label lookup): dissolved by OWN-1 (pure `&`), §4.1. Review RUL-10:
  answered by CF:706 (labelled arguments always narrow), §5.2.

STILL OPEN (contradictions):
- **C3. DEFINE bindings in the inner direction.** 2026-11-13 evening: an opted-in DEFINE holds `name := ...` bindings.
  2026-11-14: DEFINE stays ONLY as PCRE syntax inside a literal; API callers keep the inner direction (`(\d+)&${ <256
  }`). Reading A: inner-direction patterns have holes but no bindings. Reading B: inner-direction DEFINE keeps `:=`.
- **C5. Multi-index comma.** 2026-11-14 00:10 (a manager lean): `A[1,3,5]` NOT adopted, comma kept for `A[i, j]`;
  the `[]` positional note lists `X[1,3,5]` as valid. Rev 6: NARROWED by CF:863, which names "a multi-index if
  adopted" under the array bracket: IF adopted, `X[1, 3, 5]` = `X[1|3|5]` (any one of those positions, result an
  array keeping the original positions), and the comma can no longer be a dimension separator (`A[i, j]` would make it
  carry logic; write `A[i][j]`, as `d[1][1]` already does). Still open: whether to adopt the multi-index at all.
  Lean: adopt (it costs no new rule; `X[[1, 3, 5]]` then reads the same).
- **C7. Value-valued maps.** 2026-11-13 `["US" => "United States"]`; 2026-11-14 views: labels are names, the value
  per branch shown is `.index`. Reading A: other values are computed labels (now bindings, §4.4) or record arrays
  (predx C7). Reading B: `=>` survives.
- **C12. Define-before-use.** 2026-11-13 BLOCK SHAPE: required; 2026-11-13 evening: forward references allowed, no
  cycles. Bounded recursion (§7) needs a self-reference at least.
- **C13. Bare label names as values.** 2026-11-13 NAME RESOLUTION: an undeclared bare name is a label; 2026-11-14
  01:00: values always `$x`. `(wname.index: ==wd)` uses a bare binding as a value while `(b: >$a)` uses `$` (§0.1
  L37). Review OWN-11's lean: computed labels follow labels, `x:` to constrain, `$x` to read (so `==$wd`).
- **C16. Precedence example.** D196 (`&` tighter than `|`) parses the 00:10 example `x & <256 | >300` (CF:251) as
  `(x & <256) | >300`, silently WIDENING the program; WITHDRAWN (LEAN, review RUL-15): write `(x: <256 | >300)`
  (§4.1); a `precedence.section` warning is PLAN (§0.1 L22).
- **C17. `&`'s structure.** `&` is extensional (§2.2) yet distributes over array entries and drops empty products
  (§3.2), a structural effect (`/a|b/ & /b|a/` gives [a, b] or [b, a] by which side is major). predx C17/S15
  proposes "left-major cross product", which would give the ORDER of an `&` chain a structural effect against the
  ruled "order- and grouping-free" (CF:722). `.index` after `&` with an array of filters (§3.5) depends on it.
- **C18. Named assertions vs the `@` rule.** Named failures via `leap_1900 := assert_none(...)` (CF:595); the `@`
  lean (CF:619): effect macros cannot drop `@`, only `@` forms are bare statements. A named assertion is then
  `leap_1900 := @assert.none(...)` (an `@` inside an expression), a binding without `@`, or not allowed. Rev 6: a
  binding names an rx or a macro (CF:858) and an assertion is neither (C19), so the binding readings are out. Lean: a
  name is a labelled entry of the assertion's call record, `@assert.none("1900" & leap, name = "leap_1900")`.
- **C23. `&` in rx text.** C4 ruling: the guard is `(\d+)&${ <256 }`, an `&` inside PCRE text; the owner lists `&`
  (with `${}`) as the rx additions the predicates need (CF:795); but a literal means EXACTLY what PCRE means (CF:577),
  where `R&D` is three literal characters (G3). Reading A: `&${` is a two-token marker, rx syntax only before a hole.
  Reading B: `&` is an operator throughout rx text in the predicate opt-in (a one-literal program then differs from
  PCRE on `R&D`). Lean: A, which keeps G3 and still gives the owner's `&` in rx.
- **C25. Tuple comparison arrays.** `lex_ge([major, minor, patch], [1, 4, 0])` (CF:648); but an array literal IS an
  alternation (§3.1), and the export discussion rejects `[leap, weekday]` for exactly this (CF:614: "names lost");
  `[1, 4, 0]` is `&`-equal to `[0, 1, 4]` (review OWN-9). Rev 6: the type picture forbids the tuple as a value (a
  record is never a value, CF:866; an array is any one entry, CF:863); what stays RULED from CF:644 is "a library
  macro, no syntax". Candidate rewrite (the manager's, CF:876): `version & lex_ge(1, 4, 0)`: the call record is the
  bound tuple, the subject (by `&`) gives the other side as its labels in group order. Lean: adopt that shape for the
  library, with a compile error when the call record's length differs from the subject's label count; it needs a
  variable-length call record (O47). No worked example or other library signature needs a tuple or record as a
  value (rev 6 check of §8 and §12); phase 1 can rely on the condition spelling of §8, which needs no tuple.
- **C26. The empty-match ERROR "opted out".** §7: in a predicate program the nullable-search case is an ERROR, with
  "no diagnostic ... when opted out"; §7.1: "Errors cannot be disabled". How a predicate program opts out of an
  error (other than `& !""` or anchoring) is not stated.
- **C28. `occurs.all` vs the sequence rule.** §4.3: `x: S` on a repeated label already means all iterations; the
  counting ruling adds `occurs.all(x: S)`. Either they are synonyms or `x: S` means something else (§0.1 L36; O28).
  Also open here: whether `some`/`all` are built-ins or library names (review RUL-13).
- **C29. `(x & isodate).year`.** `isodate(x)` is a compile error (CF:744, CF:749). What remains: whether `.year` of
  `x & isodate` is a VALUE (the cut layer's `(X & isodate).weekday`) or the map-view PATTERN of the part (§3.2).
  Reading A: `.` on any rx is structural and values are only `$`-forms (`$d.year`). Reading B: `.year` of an
  application is a value. Rev 6: the ruled search result (CF:873) reads `d.year` on an rx as an rx (the set of the
  occurrences' years), i.e. the map view gives an rx, never a third thing; lean A, with `.year` of `x & isodate` the
  set of the year strings of the narrowed pattern (one string when the narrowed set has one year).

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
- **O12.** `!~` once `!` is a filter: keep (as the sugar of §2.6, review RUL-5), or drop it (no edge-assertion
  special case remains, C32).
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
- **O24.** Export: the Q6/Q9 note's "look later: `export` as a binding attribute, imports as a compilation-unit
  setting" is overtaken by the function forms, which are LEAN (manager); the option (b) `_`-prefix convention is
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
- **O38. Look-alike rows with no diagnostic.** §0.1 marks GAP rows (L20, L21 on answers, L25, L29-L32, L35; L23
  left the list in rev 6: its difference is now the stated meaning of the bracket, CF:863):
  DIFFERENT with no named diagnostic, so G0's acceptance fails on them today. Some are open items above; L20 (a padded
  target against an integer section) and L25 (`/a|b/` vs `/b|a/` under `[]`/`.index`, by design) have no item:
  whether a documented structural difference needs a diagnostic, and which warning L20 gets, are open. Also from
  OWN-15: whether the goal order G1 > G2 should be stated as G2 > G1 at the default level (what the rules do).

Open items NEW in rev 5 (from the 2026-11-15 entries and the rev 4 audit; plain words, each with a leaning):
- **O39. The budgets: how big is too big?** Two size limits are named but never set by the owner: (a) the
  class-count tiers of a relation between two labels (§4.6: "24 classes = fine, 1,440 = borderline, 3.65M = error"
  is the manager's answer to "how practical", CF:659-663, which the owner did not reply to); (b) the budget over which
  `count()` is refused in favour of `occurs` (CF:832). Lean: ONE budget, a labelled, measured state/size quantity
  that both tests use (the standing preference for measured budgets over structural rules; D77), shown with its
  number by the cost report, with no fixed thresholds written into the spec.
- **O40. What is a number?** The owner wants numbers to be one kind (CF:813, CF:823); rev 4 treated numbers as
  numeral strings (`5` = {"5"}). Open: whether a number is still a numeral STRING SET (so `count(...)` is the set of
  its canonical spellings and can be inserted with `${...}`) or a separate value kind; and so how `count(...)` reads
  inside a hole and against a padded subject number. Lean: numeral string sets, canonical form, so no third value
  kind is added and §2.4's comparison rules cover counts unchanged; where a number test is evaluated (inside the match
  as a set, or on the result as a value) is the compiler's choice, with the cost shown (manager's view, CF:813). Rev
  6: the ruled two value kinds (CF:858) leave no room for a number kind, so the lean follows from the ruling; it stays
  listed because the owner has not said "a number is an rx" in so many words, and the hole/padding questions remain.

Open items NEW in rev 6 (the type picture, CF:846-878; items (a)-(e) are the manager's TO CHECK list, CF:876, and
the brief's; each with a lean, none decided here):
- **O41. `(x)`: grouping or a one-entry record?** (a.) Lean: GROUPING wherever a value is expected. A record is
  never a value (CF:866), so a value-position `( e )` cannot be a record and there is nothing to disambiguate; a
  one-entry record exists only in the three record positions, where the position says so: a call `f(x)` (its
  parentheses are the record), a condition `(x: S)` (the `:` says so), and the left of a binding `(x) := r` (design
  only: lays x over r's first group; out of phase 1). §5.4, §0.1 L44.
- **O42. The list form and the map literal under "comma = next entry".** (c.) `[x = /foo/, y = /bar/]` reads
  directly: an array (any one entry) whose entries carry labels (`=`), i.e. `(?<x>foo)|(?<y>bar)`; it STAYS, as the one
  spelling of the aligned case (`join`'s input is the same form). The map literal `(x = /foo/ | y = /bar/)` does not
  survive: a `( )` in value position would be a record used as a value, and its single entry `x = (/foo/ | y = /bar/)`
  puts a label inside a value. Lean: withdraw it (CF:542 was a spelling lean, not a ruling); write the array form.
  §3.1, §0.1 L43.
- **O43. The condition binding in record terms.** (d.) The C22 rule "`&`/`|` tighter than `:`, `:` tighter than `,`"
  becomes: an ENTRY runs to the next comma or the closing bracket (the comma is no operator, so it has no precedence),
  and inside an entry `&` and `|` bind tighter than `:` and `=`. Every rev 5 answer is unchanged (L3, L4, L22; the
  `(major: 1 & minor: >=4)` error). New consequences: `:` outside a record is an error (`P & x: S`, `[x: S]`). Lean:
  adopt the restatement; it is the C22 ruling, not a new rule. §4.1, §5.4.
- **O44. Every other comma in the draft.** (e.) Checked: `occurs.exactly(1, cond)`, `between(1, 12)`, `join(a, sep =
  ".")`, `each((& f), A)`, `weekday_of($y, $m, $d)`: call records (positional, then labelled), unchanged; `[f, g]`
  arrays of filters (§3.5) and `@export(["leap", /[^_].*/])`: arrays, any one entry, unchanged; `(x: <200, y: >55)`:
  a condition record, unchanged; `X[1,3,5]`: C5 (narrowed); commas inside `/.../` (`\d{1,3}`, `/${p},${p}/`,
  `[^,]`): rx text, untouched. Two things the ruling's list of record positions does not name: (1) DEFINITION HEADS
  `m(p1, p2) :=` and typed parameters `m(x: T)`; lean: a head is position (a), the call shape that declares the
  parameters, with `:` constraining the parameter it declares; (2) the library name `records(text, rx)` (§7) now
  collides with the vocabulary word "record"; lean: rename the placeholder when spellings are chosen (it returns an
  ARRAY of entries, so a name like `entries_of` says what it returns).
- **O45. A condition written where a value is expected.** The ruling says a condition is a macro (a value, CF:858)
  and that a record appears "in a condition, against a pattern's labels" (CF:866 (b)); conditions are also passed
  (`occurs.exactly(1, (name: S))`, `count((name: S))`), put in arrays (`[(x: <200), (y: >55)]`) and could be bound
  (`c := (year: 2000)`). Lean: a record whose entries are all `label: S`, written in value position, DENOTES ITS
  CONDITION (the macro with the subject open that lays the record against the subject's labels); the macro is the
  value, the record is its written body, and no record is ever bound. Any other record in value position is an
  error (L43). §4.1, §5.4, §0.1 L46.
- **O46. What a module is.** Rev 5: a module is a MAP of the file's bindings (LEAN, CF:619), usable whole as a
  pattern when every entry is an rx. Under the two kinds it is neither an rx (it holds macros) nor a record (never a
  value, CF:866), yet `json := import("json")` binds it. Reading A: a module is a compile-time NAMESPACE that `:=`
  names, not a value (no passing, storing or returning; `json.row` is name resolution). Reading B: a module is an rx
  when every export is an rx and a namespace otherwise (two meanings for one form, against G0). Lean: A; the "use a
  module whole as a pattern" sentence goes (name the entries in an array instead). Touches E-JSONL, E-IPV4, E-HTTP,
  E-DEPTH only through their `import` lines, whose spelling does not change. §7.
- **O47. A call record of variable length.** (b.) The candidate `version & lex_ge(1, 4, 0)` (C25) needs a macro that
  accepts as many positional entries as the subject has labels; §5.2's macros have a fixed parameter list. Readings:
  (A) a library-only variadic form (a declared "rest" parameter), (B) fixed-arity variants (`lex_ge3`), (C) no tuple
  macro: write the condition spelling of §8. Lean: C for phase 1 (no example needs more), A as the design's later
  shape, decided when a library needs it (D77).

FAMILIES noted by the review (PLAN; not folded): value mappings (RUL-F1); quantifiers and emptiness checks, now
incl. `count()` vs `occurs` (RUL-F2); same-text-twice (O34, RUL-F3); name-set selection (RUL-F4); the dot (O31,
RUL-F5); application spellings (C29, RUL-F6; C20/C30 resolved).

## 14. Non-goals

- Non-regular nesting (balanced parentheses, unbounded JSON) stays with PCRE recursion on the VM (`vm`) or bounded
  recursion (§7); the predicate language adds no non-regular power of its own.
- No general-purpose language: no unbounded recursion through parameterized definitions, no unbounded loops, no
  lambdas until an example needs one, no side effects beyond compile-time `@` statements, no run-time compilation of
  caller-supplied PATTERNS outside `eval`, no alphabetic keywords, no boolean type (LEAN, CF:595). Numbers are NOT a
  non-goal: they are one kind for the user (§2.1, LEAN).
- No "best match" overload ranking; no interfaces, members, UFCS or `types()` in the first spec (§9).
- No third value kind: no record, tuple, boolean or number values (two kinds, rx and macro, RULED CF:858; a record is
  a shape laid against fields, never a value, RULED CF:866; numbers: §13 O40).
- No change to plain PCRE patterns outside the opt-in; class contents `[...]` keep PCRE2's meaning (synsurv).
- No in-context reading of a pattern in a set position (refused, §11) until a measured need (D77).
- No spelling decision beyond the no-keyword rule and the modifier naming rule (placeholder throughout); no build
  (#6 not scheduled; NO BUILD GO). Not phase 1: `!` in a normal rx (PARKED), partial application (deferred),
  sections of operators other than `&`, the `count()` -> `occurs` rewrite ([COUNT-TO-OCCURS]) (§0.2).
- Not this document: DFA captures ([ENG-TDFA]), finite-group backreferences as an engine rule ([BACKREF-FINITE],
  its own unscheduled row), the Boolean IR mechanism and lookaround lowering (D196 add. 2), the standard library's
  content, a JSON database.

## 15. Provenance

COND-FAMILY.md notes by date/heading; "11-12" = the 2026-11-12 sections, etc. "predx" = `docs/dev/lanes/predx_report.md`.
"r1" = review `docs/dev/reviews/2026-11-14-r1-predspec.md` (finding ids from its critic files).

| section | notes consolidated |
|---|---|
| rev 6 (all sections touched) | the type picture, CF:846-878: CF:858 (two kinds, condition = macro, filter a role) -> §2.1, §2.2, §3.5, §14, C19, O40; CF:860 (one input rule) -> §2.1, §2.3, §2.7, §5.2; CF:863 (comma, brackets, `=`, `:`) -> §5.4, §3.1, §3.2, §4.1, L23, C5, C8, O30; CF:866 (record never a value, three positions, map view, one-way, no sequence closure) -> §5.4, §3.1, §4.1, §5.2, §0.2, §7, §8, L43-L47, C25, O41-O47; CF:873 (search returns an rx) -> §2.6, C29; CF:876 (the manager's TO CHECK list) -> O41, O42, C25, O47 |
| 0 | rev 5: §0.2 from CF:753, CF:795, CF:804, CF:840; legend per the audpred findings; 11-12 base requirements; 11-13 COST METRICS; Frank 11-13 (#6 not scheduled), 11-14 (charter); goals are the manager's draft; rev 2: Q5 (G2), C2 + empty-match (G3), Q12 + enumerate (G4); rev 3: 11-14 Q1 critic framing (G0), r1 OWN-13 (table), OWN-14 (G3), OWN-15; the table's rows from r1 Q1R/Q1X/OWN/RUL |
| 1 | 11-14 LAYERING; 11-14 predx Q8; r1 RUL-14.4 |
| 2.1-2.3 | rev 4: 11-15 RULING (subject never an argument), 11-14 RULINGS (C1); 11-14 fractional rx + addendum; 11-14 `!`; 11-14 SUPERSEDES field-wise `&`; D196 + add. 1-2; 11-14 import follow-up (module = map); 11-14 counting; rev 5: CF:753 (C34), CF:782, CF:795, CF:804, CF:813, CF:823 (numbers, `!`, currying); rev 3: 11-14 RULING OWN-1 (pure `&`); r1 OWN-2, RUL-2, OWN-5, RUL-14.2 |
| 2.4 | 11-13 LITERALS DECIDE; 11-14 00:10; 11-14 RULINGS on §13 (C9); 11-14 RULING OWN-1 (`padded`); r1 RUL-14.6 |
| 2.5-2.6 | 11-13 NO CONCATENATION OPERATOR; 11-13 SEARCH notes; 11-14 00:10; D193 add. 3; 11-14 RULING Q1; r1 RUL-1, RUL-5, Q1R-6, RUL-14.5 |
| 2.7 | 11-14 RULING OWN-1 (transforms are FILTER MODIFIERS); predx S1, §8.2 (the pullback) |
| 3 | 11-14 00:10; views; spelling vs logic; index base; `[]` positional; 11-14 predx Q7; 11-14 predx gaps (ARRAYS OF FILTERS); r1 RUL-9, OWN-8 |
| 4 | rev 5: §4.6 thresholds marked LEAN per the audit, example per CF:749; rev 4: 11-14 follow-up (patterns take no arguments); 11-14 01:00; 11-13 late; 11-13 DESTRUCTURING, AMBIGUITY notes, MAPPINGS; 11-14 predx Q2, Q4, Q6/Q9; 11-14 value-vs-value (cont.); predx S3; 11-14 counting; rev 3: 11-14 RULING C22 + addendum; r1 RUL-14.1 |
| 5 | rev 5: CF:753, CF:804 (sections, no partial application in phase 1); rev 4: 11-14 follow-ups + 11-15 RULING (parameters, sections, no lambda); 11-13 BLOCK SHAPE, NAME RESOLUTION; 11-13 evening; 11-14 join, compose, curry, marks; 11-14 Q6/Q9 (no keywords, assertions); 11-14 import/export + follow-up (`@`); 11-14 predx gaps (ENUMERATE); predx S8; rev 3: C22 addendum; 11-14 RULING Q1; r1 OWN-7, RUL-6, OWN-10, Q1X-5 |
| 6 | rev 5: CF:63 (next-end caveat restored); 11-14 capability levels; 11-12 base requirements; 11-14 predx Q5, Q11; 11-14 RULINGS cont. (`&` at `vm`); predx S9, S10, §3.9 F33; r1 Q1X-8 |
| 7, 7.1 | 11-13 RECURSION RULE NARROWED, IMPORT, COST notes; 11-14 file_text + records; 11-14 predx Q12, Q13; predx S6, S14; 11-14 import/export + follow-up + addendum; 11-14 empty-match RULING + amendment; rev 3: 11-14 RULING Q1 (nullability in context); r1 Q1R-9, Q1R-10, Q1X-8, OWN-7, RUL-14.1 |
| 8 | rev 5: CF:782, CF:823, CF:832, CF:840 (`count()`, `occurs`, budget, [COUNT-TO-OCCURS]); 11-12 STANDARD LIBRARY; 11-13 STRING OPERATIONS; 11-13 late; 11-14 blessed callouts; 11-14 counting; 11-14 predx gaps (TUPLE CONDITIONS); 11-14 Q6/Q9 + import (assert); rev 3: 11-14 RULING OWN-1, C22 (semver comma form) |
| 9 | 11-14 predx Q8; predx §9 |
| 10 | 11-14 runtime eval + addendum |
| 11 | rev 5: CF:761 (the filtered span), CF:753 (C35), CF:795 (rx additions); rev 4: 11-14 RULINGS (C32); 11-14 outer layer, ERRATUM; 11-13 literal/hole/parameter notes; 11-14 RULINGS on §13 (C4) and RULING C2; 11-14 predx Q3, Q5, Q10; rev 3: 11-14 RULING Q1 foundation (SUPERSEDES predx Q1 / C15 / S2's context-marked sets); D193 add. 3; r1 Q1R-1, Q1X-2, Q1R-12, Q1X-1, OWN-14 |
| 12 | rev 5: E-CAL per CF:749 (no filter called with a subject), E-HTTP `count()` per CF:823/832; rev 4: E-CTX-1, 5, 7 per the C32 ruling, E-HTTP per C31; rev 0 sources; rev 2 rewrites per §§2.7, 4.4, 5.6, 7; E-HTTP from 11-14 counting; E-SEP from 11-14 ENUMERATE; E-DEPTH from predx §3.9 + Q12; rev 3: renamed per OWN-1; E-SEP index per r1 OWN-10; E-FILE per r1 Q1R-10/Q1X-7; E-CTX-1..6 per r1 Q1X-9, E-CTX-7 per r1 Q1R-4 |
| 13 | rev 5: C6 (CF:81, CF:117), C21, C33-C35, O23 resolved; C23 restated (CF:795); O39-O40 from CF:659-663, CF:813-832; cross-reading of all notes, D196, D193 and the 2026-11-14/15 rulings (lanes predspec, predspec2, predspec3, predspec4); rev 3 open items O26-O38 from r1's OWNER dispositions; rev 4: 11-14 RULINGS on rev 3's contradictions (C1, C30, C31, C32), 11-14/15 follow-ups and RULING "Agree with mapping" (C20, C30), new C33-C35 |
| 14 | 11-12 scoping; 11-13 late JSONL; D196 add. 2; synsurv; 11-14 predx Q10; 11-14 RULING Q1 (named in-context form only on measured need) |

Background documents: `cond_family.md` (members, machinery M1-M12, D193 answers) is still the mechanism map;
`cond_family_syntax_survey.md`'s `&!` and `=~` spellings are superseded (`!` filter, `~`), its "opt-in, not default"
and "do not touch class contents" recommendations stand.
