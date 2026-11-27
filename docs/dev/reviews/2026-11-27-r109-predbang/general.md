# CRITIC general: predbang (r109)

## Findings

Runs: my own lowerings, written from the documents' sentences (none imported from the evidence), in
`general/gen_runs.py` (+ `.out`) and `general/gen_array.py` (+ `.out`), each `timeout 120 python3 -I`. Modes as
core/model/modes defines them: "WHOLE (some surviving path spans the whole text), SEARCHED (the first surviving
path at the leftmost start) or FIND-ALL (PCRE2's global loop over it)"; python `fullmatch` / `search` /
`finditer`. Every equivalence printed has its control pair in the same script.

### GENERAL-1 (CONFIRMED; design; effort small; blast: V-A line 6, every `&!` with a condition operand)
Candidate line 6 writes "the condition fails" as `A &! (h: <5)`, but line 3 defines `&!` only for a pattern
operand: "`A &! B`: the difference (A's stretch is not a B whole); the shorthand of `A & (0 :! B)`". A condition
is zero width (core/conditions/in-sequence), so read by line 3 it never matches a non-empty stretch whole and
`A &! c` holds on every path of A; read as intended it is "c fails after A", which needs a sentence naming the
operand's kind. Goal 1's check (lines 14-15) asks that such a sentence be stated as a rule; the candidate states
none. Run R1, A := `/(?<h>\d)?x/`:
- intended `!(h: <5)` after A: WHOLE 'x' HOLDS '3x' FAILS '7x' HOLDS | SEARCHED '3x 7x x' -> ('x', 1) | FIND-ALL [('x', 1), ('7x', 3), ('x', 6)]
- line 3 read literally: WHOLE 'x' HOLDS '3x' HOLDS '7x' HOLDS | SEARCHED -> ('3x', 0) | FIND-ALL [('3x', 0), ('7x', 3), ('x', 6)]
- 56 of 341 differ; control (`(h :! <5)` after A against the intended): 185 of 341 differ. Witness length 4.
Fix shape: under V-A, state the rule ("`&!` with a condition operand is that condition negated, absent
included") or make `A &! c` a compile error naming the negation's spelling; under V-B..V-D `A &! c` is a
compile error naming `A & !(c)` (one spelling per meaning).

### GENERAL-2 (CONFIRMED by the documents' sentences + R4; design; effort small; blast: V-B as stated, lib/control/when)
V-B ("`!(cond)` stays ... line 6 leaves") cannot drop `^!(cond)` without breaking candidate line 5. The body
`when(T, B, C) := T SEQ B | ^!T SEQ C` receives a condition as T (the documents' else-only form
`when(NOT (h: <5), z)`, lib/control/when; `when(!(h: <5), z)`, drop-not line 3), so `^!` on a condition is
legal inside the provided body; and lib/control/peek already reads "A condition given as A is zero width already:
`peek(c)` tests c where it stands", which `^A` inherits as `peek`'s replacement (line 4). So under V-B either
(a) `^!(c)` stays legal for users too: ONE meaning ("c fails here") with TWO spellings, `!(c)` and `^!(c)`, chosen
by nothing but taste; or (b) `^!(c)` is refused outside bodies: a special case, against
core/principles/general-rules ("a consistent, general rule ... and not something specific"); or (c) `when`'s
body dispatches on its test's kind, which lib/control/when-test says a body cannot ("the body cannot see that an
argument is bare"). V-C (`T SEQ B | !^T SEQ C`) and V-D (`T SEQ B | !T SEQ C`) each give ONE body spelling for
every kind of test. R4 (V-D's body, T := `(h: <5)` after `/(?<h>\d)/`, B := a, C := b, `!T` lowered `(?!T)`):
WHOLE '3a' HOLDS '7b' HOLDS '3b' FAILS | SEARCHED '3b 3a 7a 7b' -> ('3a', 3) | FIND-ALL [('3a', 3), ('7b', 9)];
against its meaning `[0-4]a|[5-9]b`: 0 of 341 differ; control (then/else swapped): 212 of 341 differ. Witness
length 4. For a consuming or `^` test the V-D body is the text of today's body (`(?!T)` = `NOT peek(T)`), and
`(?!(?=A))` = `(?!A)` is the evidence's caret run.

### GENERAL-3 (CONFIRMED; design; effort small; blast: V-D (and any variant with a prefix `!` on patterns) beside `~!`)
One spelling, two meanings: `~!A`. As the candidate's ONE token it is the negative lookbehind `(?<!A)`; in any
variant where `!A` is itself a pattern (V-D), `~` applied to `!A` composes to `(?<=(?!A))`, which is `(?!A)`:
a test AHEAD. `^!A` has no such trap (`^(!A)` = `(?!A)` = the token's meaning). Run R2, A := `\d`, then `x`:
- `~!A SEQ x` as the token `(?<!\d)x`: WHOLE 'x' HOLDS '1x' FAILS | SEARCHED '1x x 1x1 x1' -> ('x', 3) | FIND-ALL [('x', 3), ('x', 9)]
- `~(!A) SEQ x` composed `(?<=(?!\d))x`: WHOLE 'x' HOLDS '1x' FAILS | SEARCHED -> ('x', 1) | FIND-ALL [('x', 1), ('x', 3), ('x', 6), ('x', 9)]
- token vs composed: 132 of 364 differ; V-C's `!~A` `(?!(?<=\d))x` vs the token: 0 of 364; `^!A` token vs
  `^(!A)`: 0 of 364; control `^!A` vs `~!A`: 176 of 364. Witness length 5. (python `re` accepts the zero-width
  lookbehind; PCRE2 facts out of scope.)
The general fact under it: a lookaround on a zero-width operand Z is Z (`^Z` = `~Z` = Z; peek's own "a
condition given as A is zero width already"). So in V-D, `~!` must not be a token (the spacing/parenthesis would
silently change direction: the same hazard the record cites for the one-token `:!`, "the silent reading could
not be taken back", record line 11789); the negative behind is `!~A` (as V-C), and `^`/`~` on a zero-width operand
is a compile error for now (it means its operand; relax later with no answer moving).

### GENERAL-4 (CONFIRMED by R1/R2/R5 and the documents; design; the GENERAL FORM; blast: all variants)
Every negative form of the subject is a member of ONE family: a TEST at a point asking whether a stated TEXT is
in an rx's language, the mark `!` flipping the question's answer while keeping the text's presence. As a declared
table (the manager's operators as rows; columns the facts each row must state):
| operator | the text it asks about | the question | can the text be absent? | negative |
|---|---|---|---|---|
| `x:` / `x ?:` | label x's text as it stands (outermost view) | the text is in S | yes | `:!` / `?:!` |
| `&` (= `0:` after a complete pattern, core/filters/and) | the stretch | the stretch is in B, whole | no | `&!` |
| `^` | the text ahead of the point | some start of it is in A | no | `^!` (V-A/B) or `!^` (V-C) |
| `~` | the text behind the point | some end of it is in A | no | `~!` (V-A/B) or `!~` (V-C) |
| `some(c)` (group question) | each setting of c's label | some setting meets c | no (a setting is a value) | `occurs.none(c)` (by NAME, today) |
Two consequences, each run:
1. The owner's "both logical not and set complement depending on context" (record line 11846) is a real
   difference at exactly ONE row: a label that can be absent. There `(x :! S)` (present and outside) and `!(x: S)`
   (fails, absent included) part (R5 outermost control: 735 of 1093 differ, witness length 6; also bang_entry).
   On every row whose text cannot be absent the mark and the prefix are one meaning: `&!` = `& !(0: B)`,
   `^!A` = `!^A` (R2: 0 of 364), and inside a group question `occurs.none(!(d: "7"))` = `occurs.none((d :! "7"))`
   (R5: 0 of 1093, alphabet '71,', P := `/(?:(?<d>\d)?,)+/`; WHOLE ',' HOLDS '7,' HOLDS '1,' FAILS '7,,' HOLDS |
   SEARCHED '1,7,' -> (',7,', 1) | FIND-ALL '7,7, 1,7,' [('7,7,', 0), (',7,', 6)] for both).
2. The prefix negation, in the variants that have it, is PCRE's own `(?!X)`: "X cannot match from here". On a
   zero-width X (a condition, `^A`, `~A`) that IS the logical not of X (R2, R4). So V-B, V-C and V-D state the
   same prefix meaning on different domains: V-B on conditions, V-C on zero-width tests, V-D on every pattern.
Fewest rules meeting Goal 1: V-D. One sentence, "`!X` holds at a point where X cannot match from that point; it
consumes nothing and passes no labels", plus ONE kind rule every prefix variant needs and none states: "the
negation of a condition is a condition" (so `A & !(c)` is a test after A's operands, core/filters/and's "A
condition written in an `&` chain stands after every pattern operand"; were `!c` a zero-width pattern, it would
be a filter operand matched against the stretch whole, the wrong answers of R1's literal row). V-C is V-D plus
one conservative error (a consuming operand), relaxable to V-D with no answer moving
(core/principles/conservative-first). V-B is NOT on that chain: it keeps `^!`/`~!` as tokens and adds a second
spelling of the point test for conditions (GENERAL-2). V-A has no prefix but needs line 6's three spellings, two
with unstated rules (GENERAL-1, and `^!(c)` relying on peek's condition reading).
Goal 1 for the marks: the table's columns make `!` one sentence ("the text is there and the row's question
fails"), `?` one sentence ("or the text is absent"), with no reference to the operand's kind; `?` is legal only on
a row whose text can be absent (elsewhere `pcrec.default.unused`'s kind of warning, as `?:` on `0` today).

### GENERAL-5 (CONFIRMED by the documents; design/maintenance; sibling of a family; blast: core/conditions/form, lib/counting)
The set `:`/`:!`, `?:`/`?:!`, `&`/`&!`, `^`/`^!`, `~`/`~!` is a family of (operator x polarity [x absent
policy]) and should be the declared table of GENERAL-4 (memory rule: decisions as first-match tables), not five
paragraphs. Members already in the documents that the candidate does not list:
- `some` / `occurs.none`: the same family's group-question row, its negative spelled by NAME in another module;
  `NOT some(c)` and `occurs.none(c)` are "one question by definition" (core/model/table/group-truth) — an
  existing one-meaning-two-spellings the documents accept.
- `0:` is `&`'s row (core/filters/and "`A & B` holds exactly when `A & (0: B)` holds"); the candidate's line 3
  says so for `&!`; the table makes `(0 :! B)` and `&! B` one cell.
- `(0: endsWith(A))` / `(0: startsWith(..))` / `contains` (lib/search) ask the same question of the match so far
  that `~A` asks of the text behind, bounded at the definition's start (core/conditions/match-so-far: `0` is the
  text "from its start to the condition's point"): a near-sibling whose negative is already writable,
  `(0 :! endsWith(A))`. Hand-derived, not run: they part where the lookbehind reaches before the definition's start.
- rx text's `[^...]` and the negated class hole (core/holes/negated-class) are a third, rx-text-only complement
  (one character's set); rx text keeps PCRE's meaning, so it is outside the table, and should be named there as
  outside so the census of `!` does not count it.
Missing column the table forces: the group-question row has no absent cell, so the cross-identity of the
subject's line 66, `(a ?:! S)` = `!(a: S)`, is place-dependent: inside a group question `!(a: S)` = `(a :! S)`
(R5) and `?:!` is refused there (core/conditions/form/optional-entry: "Inside a group question: modes: a compile
error for now"). A replacement map for the owner's question 3 must carry this row.

### GENERAL-6 (CONFIRMED by reading; doc/design; Goal 4; blast: every variant)
Goal 4 (line 21-22: "every form states YES / NEVER / MAYBE with a weight") is not met by the subject for ANY
form: lines 39-67 state no DFA category and no weight. The record's categories for the forms are not runs: `^`
/`^!` "classed YES 2026-11-25" on the closure argument ("each has a DFA in principle", record lines 10719-10725, with
"pcrec today ... every lookaround form is VM"); `~`/`~!` "YES by the same closure, the manager's estimate,
nothing run" (record lines 11827-11828). No weight is given for any lookaround form, while the group questions carry
"maybe, about 0.8". Estimates that read as YES: (a) V-D's `!A` on an unbounded consuming A (a negative
lookahead over `\d+`-like A: regular, but a product/complement whose state cost is unmeasured: MAYBE with a
weight is the honest class); (b) `~A`/`~!A` on a variable-width A (python `re` refuses variable-width lookbehind;
whether PCRE2 accepts it is out of scope and not guessed); (c) the entry negatives `:!`/`?:!` are as the entry
(record 11497) — that one is a fair inheritance. Fix: one DFA column in the GENERAL-4 table, each cell
YES/NEVER/MAYBE + weight, marked estimate or run.

### GENERAL-7 (CONFIRMED by R7; design; effort trivial; blast: the owner's `|!`, record line 11735)
`|!` is not a member of the family: `|` asks no membership question, so it has no negative cell. The two
readings it invites part: "union with B's complement" (the consistency reading beside `&!`) needs the
complement object every variant removes (Goal 3), and under V-D `A | !B` composes to an alternation with a
zero-width branch. R7, A := `\d`, B := `x`: composed `\d|(?!x)`: WHOLE '' HOLDS 'x' FAILS 'y' FAILS '1' HOLDS |
SEARCHED 'x1y' -> ('1', 1) | FIND-ALL [('1', 1), ('', 2), ('', 3)]; the union-with-complement reading holds WHOLE
on 'y' and 'xy' (composed: both FAIL). Witness length 2 (a single-case contrast, not a sweep). Leaning: `|!` a
compile error, reserved; under V-D `A | !B` legal by composition with the existing searched-empty warning
(core/model/modes).

## ANSWERS AND SUGGESTION INPUT

(The `## ANSWERS AND SUGGESTION INPUT` heading was dropped by my first insert of GENERAL-2..7 and restored here;
no other text was removed.)

### The owner's question 2: "if !(cond) is ok, is there another place ! would also work?"
For each place: does `!` keep the ONE meaning "logical not of a zero-width test at a point"; does it collide
with `^!`, `~!`, `:!`, `?:!`, `&!`; what it unlocks; the trigger to add it later (until then: a compile error
naming the spelling to use, which relaxes with no answer moving).
1. `!^A` / `!~A` (V-C). Keeps the one meaning (`^A`, `~A` are zero-width tests; R2: `!~A` = `(?<!A)`, 0 of 364
   vs the token). Collides with `^!` / `~!`: the same meanings, a second spelling each; keep ONE pair. If `!`
   works on tests, `^!` and `~!` are not needed as tokens (`^!A` would be `^(!A)` and that equals `(?!A)` only
   in V-D; `~(!A)` is a test AHEAD, GENERAL-3). Unlocks: one `when` body for every kind (GENERAL-2) and the
   behind pair with no new token. Trigger: adopt now if `!(cond)` is adopted (it is the same rule on the same
   domain, zero-width tests); this is my lens's answer.
2. `!` on a consuming pattern, `!A` = `(?!A)` (V-D). Keeps the meaning in the extended sense "A cannot match from
   here" (on a zero-width operand it is the logical not). Collides: `^!A` becomes a second spelling; `A & !B`
   (weeks of documents) becomes a lookahead as a filter operand, the existing compile error, its message naming
   `&!` (record line 11789's stance). Unlocks: PCRE's `(?!A)` with no `^` (Goal 2, "pcre has the (?!A) form and
   we are avoiding it"), `when(!x, z)` as the owner expected on 2026-11-25, and drop-not's hole row (b) deleted
   with its answers kept by plain composition (R3: `(?=${!A})` = `(?!A)`, `(?!${!A})` = `(?=A)`, 0 of 364 each,
   control 301 of 364, witness length 5). Trigger: a user writing `!^A` where `!A` would do, or the owner's
   Goal 2 ruled as binding here.
3. `!` on a group question, `!some(c)`. Keeps the meaning (a group question is a zero-width test over the
   array). No collision with the marks; it duplicates `occurs.none(c)` (one question by definition,
   core/model/table/group-truth) — an accepted second spelling today (`NOT some(c)` is printed). Inside, `!c` as
   the argument (`occurs.none(!(d: "7"))`, printed as `occurs.none(NOT (d: "7"))` in lib/counting/every-pass)
   keeps the meaning and EQUALS `(d :! "7")` there (R5, 0 of 1093), while `?:!` is refused there. Legal now in
   V-B..V-D if the group question counts as a condition: state it. Unlock: none new.
4. `!` as a `when` test, `when(!t, z)`. Keeps the meaning on any test; the else-only form. In V-B only for a
   condition; V-C for any zero-width test (`when(!^x, z)`); V-D also `when(!x, z)`. No collision. Trigger: V-D's.
5. `|!`. No: `|` asks no membership question, so there is no negative cell (GENERAL-7). A compile error,
   reserved; trigger: a ruled meaning, which would need the complement object (Goal 3) or be `A | !B` by
   composition.
6. `!!X`. Keeps the meaning (double negation); answers equal X's (R8: `!!A` vs `^A`, 0 of 121, witness length
   4) but passes NO labels (`!!A` d=None, `^A` d='1' on '1'), so it is never a spelling of `^A` under
   core/principles/meaning-not-spelling's "set their labels the same way". No collision. Leaning: legal by
   composition, a structural warning ("a double negation; `^X` passes X's labels"). No trigger needed.
7. `!` in a hole of a lookaround group, `(?=${!A})` (drop-not reading (b), record line 10863). Under V-A/V-B/V-C
   there is no `!A` object, so the hole row goes and `^!A` replaces `peek(!A)`. Under V-D it needs NO row: plain
   composition gives reading (b)'s answers (R3). Trigger: V-D.
8. `!` on a `records` item or an `occurrences` argument. `records` items are "can match, condition-free"
   (core/model/places): `!c` is excluded with conditions; `!A` (V-D) is a zero-width item, a compile-time find-all
   of empty matches: no use. `occurrences(!A)`: a nullable argument (warning; its hits are empty and the first
   ends the loop, lib/search/occurrences). Inside an argument, `occurrences(/\d+/ &! /7/)` keeps today's answers of
   the complement-inside line. Leaning: a compile error at both places for now; trigger: a program that needs a
   zero-width hit list.
9. `!` on a whole bound name used as a test, `!X` with `X := ...`. A condition cannot be bound alone
   (core/holes/bare-condition/bound-condition), so in V-B `!X` is never a condition: a compile error. V-C: legal
   only if X is zero width (e.g. `X := ^A`). V-D: `(?!X)` for any X; the use reads nothing of X's labels
   (core/principles/binding-fixed holds: X's own reads are its own). Unlock: a named negative test
   (`no_digit := !rx.digit`), the "named complement" the record says is lost (record 2026-11-27, first entry),
   back as a named negative lookahead. Trigger: V-D.

### Which variant states the general form with the fewest rules (my lens only)
V-D, with three amendments: (1) "the negation of a condition is a condition" stated as the one kind rule
(GENERAL-4); (2) `~!` is not a token, the negative behind is `!~A`, and `^`/`~` on a zero-width operand a compile
error for now (GENERAL-3); (3) the marks `:!`, `?:!`, `&!` kept as the table's negative cells (GENERAL-4/5),
because on the label row they mean something the prefix does not (present and outside), and `?:!`'s only
shorter twin, `!(x: S)`, is a different cell inside a group question (GENERAL-5). If the owner prefers to build
conservatively, V-C is V-D with one compile error (a consuming operand) that relaxes to V-D with no answer
moving. V-B is not recommended by this lens: it is not on the V-C -> V-D relaxation chain and needs either a
second spelling (`^!(c)`) or a special-case error (GENERAL-2). V-A needs a stated rule for `&!` on a condition
(GENERAL-1) and spells "c fails" three ways.
Goal 4 is unmet in every variant (GENERAL-6): the table of GENERAL-4 should carry the DFA column.

## PROBED-AND-HELD
- `^!A` as one token against `^` on a prefix `!A` (V-D composition): 0 of 364 differ (alphabet '1x ', length 0..5;
  control `^!A` vs `~!A` 176 of 364). The `^!` spelling keeps its answers in V-A, V-B and V-D.
- V-C's `!~A` against the candidate's `~!A` token: 0 of 364 differ (same alphabet; control above).
- drop-not reading (b) by plain composition under V-D: `(?=${!A})` = `(?!A)`, `(?!${!A})` = `(?=A)`: 0 of 364 each
  (alphabet 'y1 ', length 0..5; control `(?!A)` vs `(?=A)` 301 of 364).
- V-D's one `when` body on a condition test: 0 of 341 against its meaning (control 212 of 341), R4.
- `!!A` against `^A`: answers 0 of 121 differ (length 0..4); labels differ (none vs d), R8.
- Inside a group question `!(c)` = `(x :! S)`: 0 of 1093 (alphabet '71,', length 0..6); outermost control 735 of
  1093 (gen_array.py).
- Goal 3 ("no object that cannot be used where its operand could"): every variant's negative point test is a
  zero-width pattern or a condition, usable where its operand is except as a filter operand, the same refusal
  `^A` meets (core/filters/operand-context); held for V-A..V-D.
- I ran none of the evidence scripts; my models are my own (gen_runs.py, gen_array.py), and agree with the
  evidence where they overlap (the `(?!(?=A))` = `(?!A)` guard; the entry cells on `/(?<h>\d)?x/`).

CRITIC COMPLETE general 2026-11-27T19:34Z
