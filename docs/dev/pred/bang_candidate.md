# The `!` candidate: a rule set under discussion (2026-11-27)

STATUS: PROPOSED, NOT RULED. Written by the predicate manager as the SUBJECT of review r109 (predbang), at the
owner's request: "please have a critic lane look over these rules and provide feedback and a suggestion on !".
The record of his words is `docs/design/plan_row_bodies/COND-FAMILY.md`, the entries dated 2026-11-27 (from
"an IDEA ("half baked") on `!`" to the end); the record wins over this file. Spellings are placeholders (D193
addendum 4). The predicate language is DESIGN ONLY: no code exists and none is proposed here.

## Goals (the owner's, in his words where quoted; the order is the manager's reading)

1. Each symbol means one thing where it is written. His words: "we split off ! because in different places the
   negation/complement idea was different semantics"; "the trouble is that its both logical not and set
   complement depending on context. !(cond) and !A mean different things."
   Checkable: for every legal form holding `!`, one sentence gives its meaning with no reference to the kind of
   its operand, or the sentence that does refer to it is stated as a rule.
2. Regex behaviour is the default ("Plain rx in particular should work like pcre when we can"); PCRE's `(?!A)`
   exists and the design should not pretend otherwise ("one thing bothers me is that pcre has the (?!A) form and
   we are avoiding it").
3. No object that cannot be used where its operand could ("what is !B as an object? you can't seq it or use it
   where you can B").
4. All DFA unless the user specifies ("goal is all dfa unless specified by user. I don't want "when" to force
   vm"): every form states YES / NEVER / MAYBE with a weight.
5. Conservative now, relax later: an error may be relaxed without changing an answer.
Non-goals: final spellings; the non-atomic lookarounds; any build.

## Today (the documents at this commit, with drop-not of 2026-11-25 ruled and not folded)

- `!B` on a pattern or a set is the complement, an rx that can filter and cannot match
  (core/filters/complement, core/filters/kinds): legal as an `&` operand, after `label:`, bound, passed.
- `!` (the documents print `NOT`) on a condition: "holds exactly when c fails, a negative lookahead at its
  point" (core/filters/negation, core/conditions/two-valued).
- The negative peek is `peek(!A)`; `!peek(A)` and `when(!x, z)` on a bare pattern are compile errors (the record,
  "2026-11-25 OWNER RULING — drop-not").
- The entry operators are `:` (present and in the set) and `?:` (absent, or in the set)
  (core/conditions/form/optional-entry).
- `when(test, then, else = //) := ([(=) = test] SEQ [(=) = then]) | (NOT peek(test) SEQ [(=) = else])`
  (lib/control/when); a bare pattern test consumes (lib/control/when-test).

## The candidate (statement put to the owner as slug bang-split; NOT answered)

1. No `!` by itself: the complement object leaves. `X := !B`, `(a: !<v)` and `A & !B` are compile errors naming
   the operator to use. (His later words: not ruled out forever; so RESERVED, under construction.)
2. Entry operators, each ONE token: `:` present and in; `?:` absent or in; `:!` present and outside; `?:!`
   absent or outside.
3. `A &! B`: the difference (A's stretch is not a B whole); the shorthand of `A & (0 :! B)`.
4. Four prefix lookaround operators, zero width, each an ordinary pattern usable wherever a pattern is: `^A`
   (A matches ahead), `^!A` (cannot), `~A` (A matches behind), `~!A` (cannot). `^A` replaces `peek(A)` and passes
   A's labels on; the negatives pass none.
5. `when(T, B, C) := T SEQ B | ^!T SEQ C`: a bare test consumes as today; `when(^A, B, C)` does not;
   `when(^!A, B, C)` is the negative.
6. (The manager's reading, DISLIKED by the owner: "i don't like ^!(cond) because it looks like abuse".)
   Negating a condition is written `^!(h: <5)` in a sequence, `A &! (h: <5)` beside a pattern, `(h ?:! <5)` for
   one entry.

## Variants on the table

- V-A: the candidate as written (no bare `!` at all; line 6).
- V-B (the owner's, 2026-11-27: "perhaps that is the one form and ! mean logical not"): as V-A, but `!(cond)`
  stays, the ONE bare use of `!`, meaning "the condition does not hold here"; line 6 leaves.
- V-C (the manager's, earlier the same day, then set aside): `!` is the logical not of any zero-width TEST: a
  condition, `^A`, `~A`; so the negatives are `!^A`, `!~A`, and `^!`, `~!` are not operators.
- V-D (the owner's question of the same day, the manager judged it "not a mistake once the complement object is
  gone"): prefix `!A` on a pattern IS PCRE's `(?!A)`, on a condition "does not hold here": one prefix operator;
  `^A` or `peek(A)` for the positive.
- In every variant: whether `:!`, `?:!` and `&!` are still wanted beside `!(cond)`, since (the manager's
  hand derivation, with the runs in the evidence) `(a :! S)` = `!(a ?: S)`, `(a ?:! S)` = `!(a: S)` and
  `A &! B` = `A & !(0: B)`.

## The owner's questions to the round (his words)

1. "what is the difference between (a:! 5) and !(a: 5) ? perhaps its in the compound forms."
2. "if !(cond) is ok, is there another place ! would also work?"
3. "would it make sense to replace :! et al if we went with !(cond) or do they mean different things"
4. "provide feedback and a suggestion on !"

## Evidence

`docs/dev/lanes/predbang_evidence/` (python `re` runs with committed outputs; they print, they assert nothing).
Modes: every claim about answers is to be shown WHOLE, SEARCHED and FIND-ALL.

## Standing questions (docs/design/CLAUDE.md)

Measurement regime: not relevant (no measured quantity). Independent control: the runs compare a form against
PCRE's own lookaround or against a second spelling through python `re`; the models of `&!` and of the entries
are the manager's own lowering (a shared source with the claim: a critic should build its own). Regenerated
data: none.
