# The `rx` module: building patterns without rx literals (design note, rev 0)

**STATUS: PROPOSED, rev 0 (lane rxlib, 2026-11-17). Material for a discussion with the owner. It proposes; it rules
nothing.** Every choice that decides what a program means is laid out in section 7 as a question with candidates and
worked examples; none is chosen. Source: the owner's proposal of 2026-11-17 (`plan_row_bodies/COND-FAMILY.md`, the
entry "OWNER PROPOSAL — building patterns without rx literals"; `predicates_future.md` item 21), the manager's
rulings file for this lane (R1, R2), and the draft `predicates_draft.md` rev 23.2 read through the 2026-11-17 rulings
that post-date it (branch-scope reading (ii), regex-settles, absent-under-not, when-meaning, last-pass-default).

HIS WORDS: "this discussion is showing me that we need to support building rx without rx literals. Propose: an "rx"
module that has "digits", "loop", and other constructs. Further, a concatenation operator so that A € B means A
followed by B". And (rulings R2): "Rx module: ? Operator could mean regex ?. So /\d+/ ? Becomes /(?:\d+)?/ Then /\d*/
Effectively".

SPELLINGS ARE PLACEHOLDERS (D193 add. 4). `€` is the owner's own placeholder for the sequence operator and is kept
so that no spelling is implied. Member names (`rx.digit`, `rx.loop`, ...), setting names (`min =`, `sep =`,
`mode =`) and the postfix quantifier marks of section 3a are placeholders too. Existing draft spellings (`[ ]`, `=`
inside `[ ]`, `&`, `|`, `(label: S)`, `${ }`) are used with the draft's meaning.

EVIDENCE: `docs/dev/lanes/rxlib_evidence/rxlib_check.py` (output `rxlib_check.out`; PART n below). It runs on the
installed libpcre2-8 10.46 through lane rxmodel's harness (a condition is a callout where it is written, PCRE
backtracks when it says "fail here": the branch-scope ruling's own model) and on Python 3.14's `re` for plain
constructs. Commands: `docs/dev/lanes/rxlib_report.md`.

## Goals

Ranked; the higher wins a conflict.

- **G1. The regex model stays the meaning.** Every construct is DEFINED as regex text (a body over literals and
  holes), so what it does is what that text does under PCRE (the owner's 2026-11-17 direction: decide by a regex
  model where one exists). Who benefits: the owner and every reader, who can check a construct by reading its text.
  Measurable: the literal-free spelling of each section-1 example and its literal spelling differ on 0 texts in each
  of WHOLE, SEARCHED and FIND-ALL (target 0; measured 0 on 364 / 3,906 / 341 texts, PART B).
- **G2. No new primitive unless one is unavoidable.** Measurable: of the constructs in section 2, the count with no
  body in today's language; each such row says what is missing (target: every missing piece named; section 6 lists
  them).
- **G3. A condition can be written where it means.** The 2026-11-17 rulings make the PLACE of a condition decide its
  meaning (a piece of the pattern; last pass after a loop; every pass on the conditioned item). Who benefits: authors
  who today need a literal with a hole to put a condition inside a loop. Measurable: every row of lane lastpass's
  table "what the named request must cover" has a literal-free spelling or is named as still needing one (section 5).
- **G4. The level of each construct is visible.** The 2026-11-17 ruling makes a library element beyond the user's
  level a compile error, so the module's listing must say each export's level. Measurable: every row of section 2
  states its level, checked on the built compiler where it says "checked".

NON-GOALS: a final spelling; a build (no build go); any change to `/.../` literals or to what a one-literal program
means; regex grammar inside the predicate language (the owner's objection to `(?>...)` there, item 19); deciding the
open items of rev 24 (another lane rewrites the draft today).

## Standing questions (docs/design/CLAUDE.md)

1. MEASUREMENT REGIME: NOT RELEVANT. No timing; every number is a count of texts on which two spellings answer
   differently.
2. INDEPENDENT CONTROL: RELEVANT. The "before" spellings are written BY HAND as their regex models from the draft's
   hole rule; the "after" spellings are EXPANDED BY CODE from section 2's definitions (`rxlib_check.py`, class `Rx`);
   both run on libpcre2; both are compared with an INTENT ORACLE, a plain regex with no labels and no callouts run on
   Python's `re`, which shares no code with libpcre2 or with the expander, with the reported labels computed in
   Python from the matched text. The populations are enumerated by the script (every text over a small alphabet up
   to a length; the count is printed). Sabotage: `RXLIB_SABOTAGE=1` moves a loop's item conditions after the loop
   and makes `optional` lazy; PART B then differs on B1 (2 / 324 / 364 texts) and B2 (0 / 480 / 704), the summary
   count moves 0 -> 3,748. B3 uses neither construct and does not move (its control is the oracle alone).
3. WHAT MOVES WHEN DATA IS REGENERATED: NOT RELEVANT. No table, stamp or generated file.

## 0. What the draft already has (the premise test)

The draft has NO sequence operator, and more than holes and arrays:

- **§2.5 "No concatenation operator" is an explicit LEAN (CF:69).** On 2026-11-13 the owner offered both forms ("put
  it into an rx /(?&year)(?&mon)(?&day)/ or we have a concatenation operator"); THE LEAN WAS THE MANAGER'S (rulings
  R1), for three reasons: the layers stay clean (patterns sequence inside literals, the expression language only
  combines and tests); the `+` overload trap (`"12" + "34"`: 46 or `1234`?); with no juxtaposition, a name after an
  expression always starts a binding (one-token look-ahead, §5.1). §3.1 also records "a record of rx is their
  sequence" considered and NOT adopted, for the same lean and because it loses entry boundaries (`(1, 40)` and
  `(14, 0)` would both be `140`). So `€` reopens a recorded lean; section 7 asks it as **sequence-operator**.
- **An n-ary sequence tool exists: `join([...], sep = s)`** (§5.3, LEAN, CF:278): it concatenates the entries of a
  spelled array in written order, `sep` between them; its labelled parts stay navigable (`[year = /\d{4}/, ...]`).
  E-WEEKDAY, E-IPV4, E-RFC, E-NEAR, E-SEP and E-HTTP use it (§12).
- **A separated loop exists: `list_of(X, sep = ...)`** (§5.3, "in-order repeated"; E-HTTP's `headers`). No body is
  written for it, and whether it admits zero items is OPEN (§13).
- **A label without a literal exists:** a one-entry labelled array `[x = R]` IS the rx `(?<x>R)` (§3.1); and
  `capture(x) := /(?<${x.label}>${x})/` (§5.3) puts a hole in a group-name position.
- **Alternation exists:** `A | B` (PCRE's one parse; since 2026-11-17 a condition backtracks into it, branch-scope
  (ii)) and `[A, B]` ("an array of rx is an rx", §3.5).
- **Transforms with bodies exist** (§2.7, §8): `padded`, `anchored`, `startsWith`, `endsWith`, `occurrences`,
  `contains`, `quoted`, `left`/`right`/`mid`, `length`, `month_numbered`; `any_case` is a PRIMITIVE (RULED, rev 16).
  `when(c, p)` is a library definition (when-meaning, 2026-11-17).
- **The hole rule** (§3.3, §11, §5.4's `${ }` row): a hole inserts an rx's STRING SET as ONE atom (`/${x}d/` =
  `(?:a|b|c)d`), with its OWN flags and its OWN group numbering; in a typed syntax position (a quantifier bound, a
  class range end, a group name, an option's value) it supplies that position's value from a finite compile-time
  set; a `\b` or a lookaround at a hole's edge is the EDGE-ASSERTION ERROR (§0.1 L8: a hole is a string set, it has
  no neighbours). A hole may hold a program with conditions, each condition reading its label within the hole's text
  (§R.4.1).

What a literal-free author CANNOT write today: a character class (digit, letter), an optional part, a counted loop
without a separator, the lazy and possessive forms, anchors and boundaries, lookaround, atomic. Each needs a literal
(`/\d/`, `/(?:${x})?/`, ...). That is the gap the module fills.

## 1. The need: three before/after examples

Each pair is run on libpcre2 and against the intent oracle (PART B): BEFORE vs AFTER differ on 0 texts, AFTER vs
INTENT on 0, in WHOLE, SEARCHED and FIND-ALL. The regex models are printed as the script prints them.

**B1. Every item of a list under 5** (the 2026-11-17 last-pass-default ruling's own case: "every pass" is written by
conditioning the item and looping over the conditioned item).

    BEFORE (today):  item := /(?<h>\d)/ & (h: <5)
                     /(?:${item};)*/
    AFTER:           item := [h = rx.digit] & (h: <5)
                     rx.loop(item € ";")

Regex model, both: `(?:(?:(?<h>\d)(?C"c"));)*` with c = "h is a canonical numeral below 5"; the plain twin is
`(?:[0-4];)*`. On `3;3;` WHOLE HOLDS; on `3;7;` WHOLE FAILS and SEARCHED reports `3;`@0 (h = `3`); on `7;3;` SEARCHED
reports the EMPTY row @0 (the loop may run zero times, and the leftmost start wins), and FIND-ALL reports ``@0,
``@1, `3;`@2, ``@4. Over the 364 texts over {3, 7, ;} to length 5: 0 / 0 / 0 differ. The contrast the ruling draws:
the BARE label after the loop, `rx.loop([h = rx.digit] € ";") & (h: <5)`, reads the LAST pass and HOLDS on `7;3;`
(lane lastpass, `/(?:(?<h>\d);)*/ & (h: <5)`, checked against libpcre2 there).

**B2. A time of day with labelled parts and a condition on one part** (the draft's `t2`, §R.4).

    BEFORE (today):  t2 := /(?<h>\d{1,2})(?::(?<m>\d\d))?/
                     t2 & (h: <13)
    AFTER:           t2 := [h = rx.digits(1, 2)] € rx.optional(":" € [m = rx.digits(2, 2)])
                     t2 & (h: <13)

Regex model, before `(?<h>\d{1,2})(?::(?<m>\d\d))?(?C"c")`; after (expanded)
`(?:(?<h>\d{1,2}))(?:(?:(?:\:)(?:(?<m>\d{2,2})))?)(?C"c")`. On `9:30` WHOLE HOLDS (h `9`, m `30`); on `14:30` WHOLE
FAILS, SEARCHED reports `1`@0 (h = `14` is rejected, PCRE backtracks to h = `1`, and the optional minutes cannot
follow), FIND-ALL `1`@0 then `4:30`@1; on `9:30 14:00` FIND-ALL `9:30`@0, `1`@5, `4:00`@6. Intent oracle
`(?:1[0-2]|\d)(?::\d\d)?`. Over 3,906 texts over {1, 4, 9, 0, :}: 0 / 0 / 0 differ. (The `1`@5 is regex behaviour
under branch-scope (ii), not a construct's doing: a boundary is the author's to write, section 2 row 15.)

**B3. An alternation** (the draft's branch-scope example; §R.1.4, COND-FAMILY 2026-11-17 11:35).

    BEFORE (today):  A := /(?<l>\d)\d/        B := /(?<l>\d\d)/
                     (B | A) & (l: <20)
    AFTER:           A := [l = rx.digit] € rx.digit        B := [l = rx.digits(2, 2)]
                     (B | A) & (l: <20)

Regex model `(?|(?<l>\d\d)|(?<l>\d)\d)(?C"c")` (a label in both branches needs PCRE's branch reset `(?|...)`; the
expander emits it when branches share a label). On `25` WHOLE HOLDS through A with l = `2`; on `15` l = `15`; on `05`
l = `0` (`05` is not a canonical numeral, B's row is rejected); FIND-ALL on `25 13`: `25`@0 (l `2`), `13`@3 (l
`13`). Over 341 texts over {1, 2, 5, space}: 0 / 0 / 0 differ. The alternation itself needed no new construct; the
gain is that A and B are written without literals.

What the pairs show: the meaning does not move (G1); what moves is that no `/.../` is needed, and in B1 the condition
sits visibly on the item that the loop repeats.

## 2. The construct list

Columns: the construct (placeholder name); its arguments; its DEFINITION AS REGEX TEXT (the regex model: the
construct means exactly this text, a hole being one atom with its own flags); whether it is DEFINABLE TODAY as a
library body over literals and holes (the body, or what is missing); its LEVEL by draft §6.1 (default = automaton
code only). "Checked" = run on the built compiler (`build/pcrec -p rx --features all --engine=dfa|vm`, 2026-11-17):
`a(?:b|c)*?d`, `a{2,}?`, `^a$`, `\Aa\z`, `\bfoo\b`, `x(?=\d)`, `x(?!\d)`, `(?<=a)b`, `a++b`, `(?>\d+)x` compile under
`--engine=dfa`; `a*+a`, `(?>ab|a)c`, `(?<=a|bc)d`, `(\d)\1` are refused there ("requires the VM engine"); `(?(...)`
is refused under both ("module 'conditionals' is enabled but (?(...) is not implemented yet").

| # | construct | arguments | definition as regex text | definable today? | level |
|---|---|---|---|---|---|
| 1 | literal text | a string | the string, every character literal (`"a.b"` = `a\.b`) | YES, it IS the string literal (`"9:"`; §2.1: a quoted literal is a one-string rx); no construct needed | default |
| 2 | `rx.digit` | none | `\d` | YES: `digit := /\d/` | default |
| 3 | `rx.digits` | `min = 1`, `max` (unbounded by default) | `\d{min,max}` | YES with a bounded max: `digits(min, max) := /\d{${min},${max}}/` (a hole in a quantifier bound, a typed position). An UNBOUNDED default needs a second body `/\d{${min},}/`: today's typed-position rule names no "no bound" value | default |
| 4 | `rx.letter` | none | `[[:alpha:]]` (PCRE's: ASCII unless UCP) or `\p{L}` | YES either way; WHICH is a question of meaning (minor, not listed in section 7: the class follows the program's UCP setting exactly as in a literal) | default |
| 5 | `rx.word_char`, `rx.space`, `rx.any`, `rx.any_but_newline` | none | `\w`, `\s`, `(?s:.)`, `.` | YES: one-line bodies | default |
| 6 | `rx.any_of` | a set of one-character strings, or a string | `[abc]` | AN ARRAY: YES, it is the array itself (`["a", "b", "c"]` = `a\|b\|c`, the same strings and order). A STRING: NO, splitting a string into its characters is not in the language (`chars(w)`, §13's `folded(w)` row) | default |
| 7 | `rx.range` | two one-character strings | `[a-b]` | YES: `range(a, b) := /[${a}-${b}]/` (class range ends are a typed position) | default |
| 8 | `rx.none_of` | a set of one-character strings | `[^abc]` | YES: `rx.any & !S` (pattern difference after `&`, §R.1.4) | default |
| 9 | sequence `A € B` | two patterns | `(?:A)(?:B)` (the hole rule: `/${A}${B}/`) | YES as a macro, `seq(a, b) := /${a}${b}/`, and n-ary as `join([a, b, c])`. The OPERATOR is a spelling (section 3); its READING (hole or text splice) is section 7's first question | default |
| 10 | alternation `A \| B`, `[A, B]` | patterns | `(?:A\|B)`; with a label in more than one branch `(?\|A\|B)` (branch reset; B3) | EXISTS | default |
| 11 | `rx.optional` | a pattern; `mode` = greedy, lazy, possessive | `(?:X)?`, `(?:X)??`, `(?:X)?+` | YES as three bodies (`/(?:${x})?/`, ...). As ONE construct with a `mode =` setting: NO, a quantifier's greedy/lazy/possessive mark is not a typed hole position today | greedy, lazy: default. Possessive: default only where pcrec discharges it (checked: `a++b` yes, `a*+a` no), else `vm` |
| 12 | `rx.loop` | a pattern; `min = 0`, `max` (unbounded), `sep` (none), `mode` | no `sep`: `(?:X){min,max}`; with `sep`: `(?:X)(?:(?:S)(?:X)){min-1,max-1}`, wrapped `(?:...)?` when min = 0 (PART C: 0 of 1,093 texts differ from a split oracle, six (min, max) pairs) | YES without `sep` (holes in both bounds); with `sep` YES as the TWO-COPY body above, but X is written twice, which changes what a label inside X reads (section 5, **separator-label**). The ONE-COPY form `(?:(?(<s>)S)X(?<s>)){min,max}` (PART C: 0 differ) uses PCRE's conditional group, NOT BUILT in pcrec | default for the two-copy form; the one-copy form: PCRE's spelling is `vm`-only, though "a separator before every pass but the first" is a one-bit flag an automaton can carry |
| 13 | greedy / lazy / possessive | a `mode` setting on 11, 12 | `?` `*` `+` `{m,n}` then nothing, `?` or `+` | as for row 11 | as for row 11 |
| 14 | anchors | none | `\A`, `\z`, `\Z`; `^`, `$` (line forms under `m`) | YES: `text_start := /\A/`; and `anchored(x)` exists. BUT see row 15's caveat | default (checked `^a$`, `\Aa\z`) |
| 15 | word boundary | none | `\b`, `\B` | A BODY YES (`/\b/`); USABLE IN A SEQUENCE: NO under the hole reading, since `rx.word_boundary € x` puts `\b` alone in a hole and a `\b` at a hole's edge is the edge-assertion error (§0.1 L8). The same holds for rows 14, 16, 17 placed as operands of `€`. Section 7, **sequence-reading** | default (checked `\bfoo\b`) |
| 16 | lookahead, negative lookahead | a pattern | `(?=X)`, `(?!X)` | A BODY YES (`/(?=${x})/`); in a sequence, as row 15. Conditions inside: the regex model is settled (regex-settles (3): an outer condition never re-enters a lookahead) | default (checked `x(?=\d)`, `x(?!\d)`) |
| 17 | lookbehind, negative lookbehind | a pattern | `(?<=X)`, `(?<!X)` | as row 16 | default for fixed length (checked `(?<=a)b`); `vm` for branches of different lengths (checked `(?<=a\|bc)d`) |
| 18 | a labelled part | a name, a pattern | `(?<name>X)` | EXISTS: `[name = X]`; also `capture`-style `/(?<${n}>${x})/`. Section 4 | default for the label as a TEST; reading its text out: `captures` (§6.2) |
| 19 | atomic | a pattern | `(?>X)` | A BODY YES (`atomic(x) := /(?>${x})/`), and a library name is not regex grammar in the predicate language, so it is one of the owner's own candidates (`atomic()` transform, item 19); its SPELLING stays item 19's | `vm` unless pcrec discharges the cut (checked `(?>\d+)x` yes, `(?>ab\|a)c` no) |
| 20 | possessive loop | as row 12 | `(?:X){m,n}+` | as row 11 | as row 11 |
| 21 | any text (a gap) | `mode` | `(?s:.*)`, `(?s:.*?)` | YES (`startsWith`/`endsWith` already use both) | default |
| 22 | empty, never | none | the empty string `""`; `(?!)` | `""` EXISTS; never: a body `/(?!)/`, used as an operand of `€` it is row 15's case | default |
| 23 | case-insensitive | a pattern | `(?i:X)` | NO. A hole keeps its own flags (§11, NO INHERITED FLAGS), so `/(?i:${x})/` is x itself; this is exactly why `any_case` is a primitive (§2.7, RULED rev 16). The module would re-export `any_case`, not define it | default (as `any_case`) |
| 24 | backreference to a part | a label | `\k<name>` | NO: the group lives in another hole's own namespace, and `\k<${n}>` is not a typed position. The finite form exists: E-SEP's `each(date_sep, enumerate(...))` | `vm` (checked `(\d)\1`); the finite form default |
| 25 | separated list | as row 12 with `sep` | as row 12 | EXISTS as `list_of(X, sep = ...)` (no body written; its minimum OPEN) | as row 12 |

COUNT: 25 rows. DEFINABLE TODAY (one or more bodies over literals and holes, or already in the language): 16 (rows
1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 18, 19, 20, 21, 25; rows 11, 13 and 20 only as one body per mode, NOT as one
construct with a `mode =` setting, for want of a typed position for the mark). PARTLY: 7 (row 6: the array form
yes, from a string no, no `chars`; row 12: the two-copy separator form only, with its label consequence, the
one-copy form needing PCRE's conditional group, not built; rows 14, 15, 16, 17 and 22's `never`: definable, but
UNUSABLE as operands of `€` under the hole reading). NOT DEFINABLE: 2 (row 23, `any_case` stays the primitive; row
24, no cross-part backreference).

## 3. The sequence operator

**What `A € B` means as regex text.** `A € B` := `/${A}${B}/` = `(?:A)(?:B)`: A's text, then B's, each one atom. So
`€` needs no new meaning: today's `seq(a, b) := /${a}${b}/` and `join([a, b])` already say it. B1-B3's expansions are
this definition, run (PART B).

**What it needs that holes do not already give.** In MEANING, nothing, under the hole reading. What it adds is a
SPELLING without a literal (`A € B` instead of `/${A}${B}/`), an infix chain instead of an array (`A € B € C` instead
of `join([A, B, C])`), and a precedence. Two limits of the hole reading then become visible, because every operand of
`€` is a hole: an assertion as an operand is the edge-assertion error (row 15), and an operand never sees its
neighbour's flags (row 23). Reading `€` as a TEXT SPLICE removes the first limit (the assertion sees its neighbours,
as in PCRE text) and is asked as **sequence-reading**. The 11-13 reasons beside today's (rulings R1):

| 11-13 reason (the manager's lean, CF:69) | today |
|---|---|
| layers stay clean: patterns sequence inside literals, predicates combine and test | the expression language already writes patterns: `[ ]` writes an alternation, `[x = R]` a group, `join` a sequence, the transforms' bodies a hole each; the line was crossed by `join` |
| the `+` overload trap | `€` is a distinct mark; the trap returns only if the chosen spelling is `+` or juxtaposition (section 3a) |
| one-token look-ahead: no juxtaposition, so a name after an expression starts a binding | holds for any infix mark; FAILS for juxtaposition as the spelling |
| (new, 2026-11-17) | the place of a condition decides its meaning; `€` lets a conditioned part stand in a sequence without a literal (B1, B2) |

**Precedence.** Three candidates against `&` and `|` (`&` before `|` is D196's and stays):
- P1: `€` tighter than `&`, `&` tighter than `|`. This is D196's own order for rx text ("concatenation, then `&`,
  then `|`").
- P2: `&` tighter than `€`, `€` tighter than `|`.
- P3: `|` tighter than `€` (`€` loosest of the three).

`A € B & (h: <5)` with A := `[h = rx.digit]`, B := `rx.optional(";" € [m = rx.digit])`: under P1 it is `(A € B) & (h:
<5)`, legal; under P2 it is `A € (B & (h: <5))`, and B defines no `h`: the unknown-label error (§4.1's lookup).
`"x" € "1" | "2"`: under P1 and P2 it is `("x" € "1") | "2"`, under P3 `"x" € ("1" | "2")` (PART G): WHOLE on `2`
HOLDS under P1, FAILS under P3; SEARCHED on `y2` reports `2`@1 under P1, nothing under P3; FIND-ALL on `x1 2 x2`:
P1 `x1`@0, `2`@3, `2`@6; P3 `x1`@0, `x2`@5.

**Associativity.** In regex text, a non-capturing group changes no path and no order, so `(A € B) € C` and `A € (B €
C)` are the same text up to grouping: the same strings, the same preference order, the same labels (a fact of
regex, not run here). `€` can then be read n-ary with no rule.

**When A or B carries conditions.** By the day's rule a condition is a piece of the pattern at the position where it
is written. With A := `[h = rx.digit]`, B := `rx.optional(";" € [m = rx.digit])` (PART D; 364 texts over {3, 7, ;}):
- `(A & (h: <5)) € B` is `(?<h>\d)(?C"c")(?:;(?<m>\d))?`; `(A € B) & (h: <5)` is `(?<h>\d)(?:;(?<m>\d))?(?C"c")`.
  They differ on 0 texts in each mode. On `3;7` both HOLD (h `3`, m `7`); on `7;3` both FAIL WHOLE and both report
  `3`@2. A condition that reads only labels already set where it stands judges the same paths in the same order at
  either place: the place changes WHEN the test runs (cost), not the answer.
- `(A & (m: <5)) € B` against `(A € B) & (m: <5)`: here the place decides. At A's place m is not set: the hole
  reading makes it the unknown-label error (A defines no m); the callout model makes it a test on an absent label,
  which fails (regex-settles (1)), so it never holds. They differ on 2 / 66 / 66 texts; on `3;3` the early form FAILS
  WHOLE, the late one HOLDS (m `3`).
- A label set in BOTH A and B: section 4, **label-twice**.

**n-ary form and arrays.** "An array of rx is an rx" is an ALTERNATION (§3.5, RULED CF:644; `[ ]` = any one entry,
CF:863), so "an array is a sequence" would reverse a ruling; the n-ary sequence is `join([...])` or a `€` chain. They
do not collide as long as `[ ]` keeps its one reading.

## 3a. Quantifier operators beside the named constructs (rulings R2)

The owner's idea: a POSTFIX QUANTIFIER on a pattern value, meaning the regex quantifier applied to the grouped
pattern. Definitions as regex text: `X ?` := `/(?:${X})?/`; `X *` := `/(?:${X})*/`; `X +` := `/(?:${X})+/`; a count
`X {m,n}` := `/(?:${X}){m,n}/`; lazy `X ??`, `X *?`, ...; possessive `X ?+`, `X *+`, ... They are the named
constructs of rows 11-13 and 20 with another spelling: `X ?` = `rx.optional(X)`, `X *` = `rx.loop(X)`, `X +` =
`rx.loop(X, min = 1)`.

`(?:\d+)?` AGAINST `\d*` (PART F; a callout after the quantified part records each end PCRE tries on `123`, anchored
at 0): `(?:\d+)?` tries 3, 2, 1, 0; `\d*` tries 3, 2, 1, 0. The same strings (checked over {1, x} to length 4 with
Python `re`) and the same preference order, so the owner's "Then /\d*/ Effectively" holds for the GREEDY forms. It
FAILS for the lazy ones: `(?:\d+)??` tries 0, 3, 2, 1 while `\d*?` tries 0, 1, 2, 3 (and `(?:\d+?)??` tries 0, 1, 2,
3). Possessive: `(?:\d+)?+` and `\d*+` both try 3 only. `(?:\d+)*` has the same strings as `\d*` but MORE PATHS (it
tries 3, 3, 2, 3, 3, 2, 1, 0: one stretch is reached by several splittings into passes), which matters for a
labelled part inside it (its last pass differs by path).

Operators and named constructs can coexist: the operator is a spelling of the named construct. The GRAMMAR QUESTIONS
the operators open, each with an example that reads two ways (asked as **quantifier-grammar**):
- POSTFIX `+` AND `*` AGAINST ARITHMETIC. The draft adds and multiplies numbers (`$y + 1` in a hole, §2.5; E-NEAR's
  day differences). If the sequence were spelled by juxtaposition, `"1" + "2"` reads as `1+2` (one or more `1`, then
  `2`) or as the number 3 (PART G): WHOLE on `112` HOLDS / FAILS; SEARCHED on `x1112` reports `1112`@1 / (on `x3`)
  `3`@1; FIND-ALL on `12 112 3`: `12`@0, `112`@3 / `3`@7. With an infix `€` the parser can tell (`"1" + € "2"` vs
  `"1" + "2"`), the reader may not: the 11-13 overload trap in a new place.
- `?` AGAINST A CONDITIONAL SPELLING. The owner noted the same day that `?` has a regex meaning and the conditional's
  spelling is open: `c ? p` reads "if c then p" (`when(c, p)`) or "c, optional, then p" (with juxtaposition).
- A COUNT IN BRACES AGAINST RECORDS OR HOLES. `X {2, 3}` outside rx text is new (braces appear only in `${ }` inside a
  literal): unambiguous, but `X(2, 3)` is a call and `(2, 3)` a tuple value, one character away; inside a literal
  `${x}{2,3}` is already PCRE's count after a hole, and a count from a binding is `{${n}}` there but `{n}` outside.
- WHICH QUANTIFIER A LAZY OR POSSESSIVE MARK BINDS. `X ? ?` (lazy optional of X) is not `X` made lazy inside (the
  orders above). An operator chain must say whether `[a = rx.digits] ??` is lazy outside or inside, and the
  difference is observable: with `& (b: <30)` after `[b = rx.digits(0)] € "x"`, the lazy-outside form reports a =
  `12`, b = `3` on `123x`, the plain twin `(?<a>\d*?)` reports a = `1`, b = `23` (PART G).
- A QUANTIFIER ON A LABELLED PART INSIDE A LOOP. `([h = rx.digit] € ";") *  & (h: <5)` reads the LAST pass (the
  ruling): HOLDS on `7;3;`; `(([h = rx.digit] & (h: <5)) € ";") *` tests every pass: FAILS WHOLE on `7;3;` (B1).
  The operator form and the named form agree; what the reader must see is which parentheses the condition is in.
- WHERE A SEPARATOR GOES. An operator has no place for one: `(X € ",") *` is a TERMINATED list (`a,b,`), and `X €
  ("," € X) *` writes X twice (section 5's separator-label consequence). Only the named loop has a `sep` argument.

## 4. Labels without literals

**How a part gets its label.** Candidates:
- L1. The existing one-entry labelled array: `[h = rx.digit]` IS `(?<h>\d)` (§3.1). No new construct.
- L2. A construct taking a name: `rx.label("h", X)` := `/(?<${n}>${x})/`, `capture`'s body (§5.3).
- L3. A binding's own name becomes the label: `year := rx.digits(4, 4)` then `year € "-" € month` has labels year,
  month. Its cost: every binding used in a pattern sets a label, and a binding used twice (`octet € "." € octet`) sets
  one label twice (below).
- L4. A mark of its own (spelling open; not `:`, which narrows, and not a word, since the draft has no alphabetic
  operators, §5.1).

**How parts' labels flow into the whole.** A literal has its OWN group namespace (§11); its named groups are fields
of its value; a hole may hold a program with labels, each condition inside reading its own (§R.4.1); `join`'s parts
"stay navigable by their labels" and E-WEEKDAY reads `$year` of `isodate` directly; the 11-13 note "definitions are
namespaces" reads `isodate.year`. Two candidates for a `€` chain:
- F1 FLAT: every label of a part is a label of the whole (as `join` and B2: `t2 & (h: <13)` reads A's h).
- F2 NESTED: a part's labels are reached under the part's binding name (`t.h`), as `isodate.year`.
Asked as **label-flow**.

**The same label twice.** `[h = rx.digit] € rx.optional(";" € [h = rx.digit])` is the regex
`(?J)(?<h>\d)(?:;(?<h>\d))?`. PCRE's reading of a duplicate name is the LOWEST-NUMBERED SET GROUP, i.e. the FIRST
written (PART E: `(?J)(?'h'\d)(?:;(?'h'\d))?=\k<h>` HOLDS on `3;7=3`, FAILS on `3;7=7`). The draft already gives a
set-once duplicate label that reading (§4.3, "plain `$x` gives the lowest-numbered set group"), and leaves a label set
twice in one match outside a loop OPEN (§13 O35). Asked as **label-twice**.

**A label inside a loop.** Last pass by default (last-pass-default, 2026-11-17): `rx.loop([h = rx.digit] € ";") & (h:
<5)` reads the last pass that set h. The loop construct keeps that, with ONE exception that the construct itself
creates: the separator form written as two copies (section 5).

## 5. Loops

`rx.loop(X, min = 0, max = unbounded, sep = none, mode = greedy)`; definitions in section 2 row 12. How it carries
the 2026-11-17 meanings:
- EVERY PASS: the conditioned item, `rx.loop(X & c)` (B1). At least one pass: `min = 1`.
- LAST PASS: a bare label after the loop, `rx.loop(X) & c` (the ruling; lane lastpass checked it against libpcre2).
- THE NAMED "ALL PASSES" REQUEST (the owner: "I want to have the method of achieving the alternative meanings defined
  and tested"). The loop construct is a natural owner: it is where the passes are written. AS A QUESTION ONLY
  (**every-pass-home**): does the request attach to the loop construct (a setting or a companion construct), stay with
  the group questions (`some(c)`, `occurs.none(NOT c)`, which already spell "some" and "every pass, possibly none"),
  or is the conditioned item enough? Lane lastpass's "what the named request must cover", row by row:

| what must stay writable | literal-free spelling with the module | regular? |
|---|---|---|
| every pass, at least one | `rx.loop(X & c, min = 1)` | yes (`(?:[0-4];)+`, lastpass PART F) |
| every pass, possibly none | `rx.loop(X & c)` | yes (B1, PART B) |
| zero passes fine, a pass lacking the label not | `occurs.none(...)` as today (a group question) | yes |
| a joint or record per pass | the condition on the item that holds both labels: `rx.loop(X & ((h, m): R))` | yes |
| not every pass; every pass in `!S`; the difference over every pass | `L & !rx.loop(X & c)` with L the plain loop (pattern difference); `rx.loop(X & (h: !S))` | yes |
| some / count / occurs.* | the group questions as today | yes (capped counters) |
| one pass by literal index, `(x[2]: S)` | unrolled: `X € (X & c) € rx.loop(X)` (the second pass written on its own) | yes; no new construct |
| reading a pass's value (`$x[2]`, the list) | not the module's business; `captures` as today | no (stored values) |
| the committed hit list | `occurrences` as today | as today |

- SEPARATORS. The two-copy definition `(?:X)(?:(?:S)(?:X)){0,}` writes X twice. If X holds a label, PCRE's
  duplicate-name rule makes a bare label after the loop read the FIRST item, not the last pass (PART E:
  `(?J)(?'h'\d)(?:;(?'h'\d))*=\k<h>` HOLDS on `1;2;3=1`, FAILS on `1;2;3=3`), against the last-pass ruling. The
  one-copy definition `(?:(?(<s>)S)X(?<s>))*` keeps one group and reads the last pass (PART E: `1;2;3=3` HOLDS) and
  accepts the same texts (PART C: 0 of 1,093 for six (min, max) pairs), but uses PCRE's conditional group (not built
  in pcrec; `vm` in PCRE's terms) and its flag group `s` would leak across an ENCLOSING loop's passes (a caveat, not
  run). Asked as **separator-label**. The existing `list_of` has the same question.
- COUNTS AS ARGUMENTS. `min` and `max` are holes in a typed position, "a finite compile-time set". The 2026-11-17
  ruling "a constant is an rx where the count of the enumeration is 1" makes a count argument an rx; a ONE-member
  count is `{n}`; a several-member count (`n := [2, 4]`) needs a meaning, asked as **count-argument**. A run-time
  count (`param(...)`) is a countdown an automaton can carry for a bounded value (the 11-13 `nth(i)` note), else
  `functions`.
- MODES. Lazy changes which row is REPORTED (SEARCHED, FIND-ALL) and which path's labels a row carries; not which
  whole values hold. Possessive is `vm` unless pcrec discharges it.

## 6. What it does not change

- Literals stay; a one-literal program is today's PCRE pattern (§11); every construct has a LITERAL TWIN with the same
  meaning, its definition (section 2).
- `[ ]`, `|`, `&`, holes, `join`, `list_of`, `capture` and the transforms keep their meaning; the module re-exports
  `any_case`, it does not redefine it.
- NOTHING HERE IS A NEW PRIMITIVE IN MEANING. What section 2 shows cannot be written as a body today, and what it
  would take:
  1. a construct with a `mode =` setting (rows 11, 13, 20): a typed hole position for the quantifier mark, or one
     name per mode;
  2. `rx.any_of("abc")` from a string (row 6): a `chars` function (the array form needs nothing);
  3. the one-copy separator loop (row 12): PCRE's conditional group, not built in pcrec;
  4. a case-insensitive construct (row 23): `any_case` stays the primitive (RULED rev 16);
  5. a backreference to another part (row 24): a cross-namespace `\k`; the finite `each`/`enumerate` form exists;
  6. an assertion as an operand of `€` (rows 14-17, 22): under the hole reading, an exception to the edge-assertion
     error or the text-splice reading of `€` (**sequence-reading**). This is the one place the module may need a
     rule rather than a body.

## Context: such libraries elsewhere

FROM THE AUTHOR'S OWN KNOWLEDGE, NOT RESEARCH (no browsing). Parser-combinator libraries (Parsec and its kin) build
patterns from small functions with a sequence operator, an alternation operator with ordered choice, `many`,
`optional` and `sepBy`; their `try` and committed choice are close to atomic. "Verbal expression" builders chain
method calls (`startOfLine().then("x").maybe("y")`) and emit regex text, which is this note's model (a construct IS
its regex text). Raku's rules make whitespace-separated atoms a sequence and offer `:`, `::`, `:::` as backtracking
stops (the owner's reference for atomic) and `%` for a separator on a quantifier (`\d+ % ','`), a quantifier-attached
separator worth knowing for section 3a's last bullet. Emacs's `rx` is an s-expression form whose `seq`, `or`,
`opt`, `zero-or-more`, `group` and `any` compile to regex strings, with the same grouping-as-meaning rule.

## 7. Questions for the owner

Ordered by how much else depends on them. Each wants a reply either way. "WHOLE / SEARCHED / FIND-ALL" are the three
modes (a whole value; the first match in a text; every match left to right). Runs: PART G unless said.

1. **sequence-reading** — what `A € B` means: the hole rule, or a text splice.
   STATE: the draft's only sequencing (holes, `join`) follows the hole rule: each part a string set, one atom, its own
   flags, no neighbours, so a `\b` or lookaround at a part's edge is an error (§0.1 L8). CANDIDATES: (a) the hole rule;
   (b) a text splice: A's regex text then B's, assertions see their neighbours as in a literal (flags still the
   part's own); (c) the hole rule plus a stated exception for assertion constructs. EXAMPLE `wb € rx.digits € wb`,
   wb := `\b`: under (a) a compile error; under (b) and (c) it is `\b\d+\b`: WHOLE on `12` HOLDS; SEARCHED on `x12
   34` reports `34`@4; FIND-ALL on `12 x34 56`: `12`@0, `56`@7. COST: (a) nothing new, but rows 14-17 and 22 cannot
   be sequenced (anchors and boundaries stay in literals or `anchored`); (b) a second reading of a part beside the
   hole's, so `/${A}${B}/` and `A € B` could differ when A or B ends in an assertion; (c) one listed exception.
2. **sequence-operator** — whether to have the operator at all.
   STATE: §2.5's LEAN against it was the manager's (11-13; the owner had offered either); `join` exists. CANDIDATES:
   (a) adopt an infix sequence operator (spelling open); (b) keep `join` and literals only; (c) both, the operator
   being `join` of two. EXAMPLE: B2's `t2` written `[h = rx.digits(1, 2)] € rx.optional(":" € [m = ...])`, as
   `join([h = ..., rx.optional(join([":", m = ...]))])`, or as today's literal: the same regex text, so the
   candidates DO NOT DIFFER in any answer (B2: 0 of 3,906 texts in all three modes). COST: (a) a new mark and a
   precedence (question 3); the 11-13 reasons (the table in section 3) are met by an infix mark and broken by
   juxtaposition; (b) none, but every sequence needs an array or a literal; (c) two spellings of one thing.
3. **sequence-precedence** — where `€` binds against `&` and `|`.
   STATE: D196 orders rx text as concatenation, then `&`, then `|`. CANDIDATES: P1 (D196's order), P2 (`&` tighter
   than `€`), P3 (`€` loosest). EXAMPLE `"x" € "1" | "2"`: WHOLE on `2` HOLDS (P1, P2) / FAILS (P3); SEARCHED on `y2`
   `2`@1 / nothing; FIND-ALL on `x1 2 x2` `x1`@0, `2`@3, `2`@6 / `x1`@0, `x2`@5. And `A € B & (h: <5)` (A sets h, B
   does not): legal under P1, the unknown-label error under P2. COST: P1 matches literal text (a pasted pattern and
   its `€` spelling group alike); P2 lets a condition attach to the last part without parentheses but makes `A € B &
   c` read B alone; P3 matches no existing order.
4. **label-flow** — how a part's labels reach the whole.
   STATE: a literal has its own namespace; `join` parts stay navigable; E-WEEKDAY reads `$year` flat; the 11-13 note
   reads `isodate.year` nested. CANDIDATES: F1 flat; F2 nested under the part's binding name; (c) flat with nesting
   available (`t.h` and `h` both). EXAMPLE `stamp := "T" € t2` (B2's `t2`): under F1 `stamp & (h: <13)` is legal:
   WHOLE on `T14:30` FAILS, SEARCHED reports `T1`@0 (h `1`), FIND-ALL on `T9:30 T14:00` `T9:30`@0, `T1`@6; under F2
   it is the unknown-label error, and `stamp & (t2.h: <13)` gives those same answers. The candidates differ in which
   programs are LEGAL, not in the answers of a legal program. COST: F1 makes every inner label a label of every enclosing pattern
   (collisions become label-twice cases); F2 lengthens every condition; (c) two names for one label.
5. **label-mark** — how a part is given its label without a literal.
   STATE: `[name = X]` exists (L1). CANDIDATES: L1; L2 a construct taking a name; L3 the binding's name; L4 a new
   mark. EXAMPLE `octet := rx.digits(1, 3)`, `ip2 := octet € "." € octet`, then `ip2 & (octet: <10)`: under L1 and L2
   the unknown-label error (nothing is labelled); under L3 octet is set twice and question 6 decides: with PCRE's
   rule (the first octet) WHOLE on `5.200` HOLDS, SEARCHED on `250.3` reports `0.3`@2 (the first octet `250`, then
   `50` at the next start, rejected), FIND-ALL on `5.1 50.2` `5.1`@0, `0.2`@5. COST: L1
   none; L2 one more name for L1; L3 labels nobody asked for, and every repeated binding becomes a label-twice case;
   L4 a new mark.
6. **label-twice** — a label set by two parts of one sequence.
   STATE: OPEN in the draft (§13 O35; R.1.2 makes a name set inside and outside a loop an error). CANDIDATES: (D1) a
   compile error; (D2) PCRE's rule, the lowest-numbered set group, i.e. the first written (PART E); (D3) the last
   set (no plain-regex spelling found here: a noted exception if chosen); (D4) both values, read by a named request.
   EXAMPLE `[h = rx.digit] € rx.optional(";" € [h = rx.digit]) & (h: <5)`: D2 WHOLE on `3;7` HOLDS (h `3`), SEARCHED
   `3;7`@0, FIND-ALL on `3;7 8;2` `3;7`@0, `2`@6; D3 WHOLE on `3;7` FAILS (h `7`), SEARCHED `3`@0, FIND-ALL `3`@0,
   `8;2`@4; D1 refuses the program. COST: D1 forbids L3's repeated bindings and the two-copy separator form; D2 is
   regex but reads the FIRST, against the last-pass intuition of the loop ruling; D3 needs a rule regex does not
   have; D4 needs the named request (question 11's kind).
7. **separator-label** — what a label inside a separated loop reads after it.
   STATE: last pass by the ruling; the two-copy definition reads the FIRST item (PART E); `list_of` has the same
   question. CANDIDATES: (a) define the construct by the two-copy text and accept PCRE's reading (or forbid labels
   in a separated item); (b) define it by the one-copy text (conditional group: last pass, same strings, PART C);
   (c) define the MEANING as "last pass" and leave the text to the compiler (the flag is one bit, regular). EXAMPLE
   `rx.loop([h = rx.digit], sep = ",") & (h: <5)`: (a) WHOLE on `7,3` FAILS (h `7`), SEARCHED `3`@2, FIND-ALL on `7,3
   1,9` `3`@2, `1,9`@4; (b)/(c) WHOLE on `7,3` HOLDS (h `3`), SEARCHED `7,3`@0, FIND-ALL `7,3`@0, `1`@4. COST: (a)
   a loop whose label means something different with and without `sep`; (b) PCRE's conditional group, VM-only in
   PCRE's spelling and not built in pcrec; (c) a construct whose regex text is not its first definition.
8. **count-argument** — a count argument whose rx has several members.
   STATE: a typed hole takes "a finite compile-time set"; "a constant is an rx whose enumeration has one member".
   CANDIDATES: (C1) the union over members, in enumeration order (`\d{2}|\d{4}` for n := `[2, 4]`); (C2) a compile
   error unless one member; (C3) the hull (`\d{2,4}`). EXAMPLE `rx.digits(n, n)`, n := `[2, 4]`: C1 WHOLE on `1234`
   HOLDS, on `123` FAILS; SEARCHED on `12345` `12`@0; FIND-ALL `12`@0, `34`@2. C3 WHOLE on `123` HOLDS; SEARCHED
   `1234`@0; FIND-ALL `1234`@0. COST: C1 regular, size grows with the count of members, and the order of the
   enumeration becomes the preference order; C2 none, less reach; C3 changes the strings (3 digits admitted).
9. **quantifier-operators** — postfix quantifier operators beside the named constructs (rulings R2).
   STATE: an idea, filed in rulings R2. CANDIDATES: (a) named constructs only; (b) operators only; (c) both, the
   operator a spelling of the named construct. Answers do not differ between the candidates; inside (b) and (c) the
   LAZY MARK's binding does. EXAMPLE `[a = rx.digits] ??` (lazy outside) then `[b = rx.digits(0)] € "x"` with `(b:
   <30)`, against the plain twin `\d*?`: WHOLE on `123x` both HOLD, labels a `12`, b `3` / a `1`, b `23`; SEARCHED
   the same rows @0; FIND-ALL on `123x 45x` (a `12`, b `3`), (a `4`, b `5`) / (a `1`, b `23`), (a `4`, b `5`). The
   GREEDY forms agree with their plain twins in strings and order (`(?:\d+)?` and `\d*` both try 3, 2, 1, 0, PART F).
   COST: (b), (c): question 10's grammar; (a) longer text for the commonest constructs.
10. **quantifier-grammar** — the parse questions operators open (section 3a lists five).
    STATE: no operator exists. CANDIDATES per sub-question: postfix `+`/`*` share the arithmetic marks, or get other
    marks; `?` is the optional, or is kept for a conditional; counts in braces outside literals, or as arguments
    only; a lazy mark binds outside or inside. EXAMPLE (the one that reads two ways as a whole program): if the
    sequence were juxtaposition, `"1" + "2"` as quantifier-then-sequence: WHOLE on `112` HOLDS, SEARCHED on `x1112`
    `1112`@1, FIND-ALL on `12 112 3` `12`@0, `112`@3; as arithmetic (the rx `3`): WHOLE on `112` FAILS, SEARCHED on
    `x3` `3`@1, FIND-ALL `3`@7. COST: shared marks bring back the 11-13 overload trap; separate marks add marks.
11. **every-pass-home** — where the named all-passes request lives.
    STATE: required by last-pass-default ("defined and tested"); not designed. CANDIDATES: (a) a setting or
    companion of the loop construct; (b) the group questions only (`occurs.none(NOT c)`, `some`); (c) the conditioned
    item only (section 5's table). EXAMPLE "every pass under 5, at least one" on `/(?:(?<h>\d);)*/`'s texts:
    `rx.loop([h = rx.digit] & (h: <5) € ";", min = 1)` and `L & some((h: <5)) & occurs.none(NOT (h: <5))` answer
    alike (lane lastpass PART E: 0 / 0 of 364 in WHOLE and SEARCHED; e.g. WHOLE on `3;3;` HOLDS, on `3;7;` and on the
    empty text FAILS): the candidates DO NOT DIFFER in answers. COST: (a) a second way to say what (c) says, but one
    that keeps the pattern unchanged when the request is added; (b) none new, written away from the loop; (c) the
    pattern itself is rewritten to ask.

These questions are independent of revision 24's open items except label-twice (§13 O35) and every-pass-home (the
named request the last-pass ruling requires).
