# SIMULATE findings: crit-predspec19
## Findings

### SIMULATE-1 (CONFIRMED by reading the script; design/doc; effort small; blast: evidence claims only)
Table (B)'s binding evidence is largely tautological. In predspec19_check.py `written_at_call` builds every Ref against
`vals.operand`, and `bound()` lays it against the same `vals.operand`, so `cond_ref`'s RefError cannot fire in table (X)
(48,797 "0 differ" only re-proves rev 18 == rev 19 by shared source). B3 and B4 construct `Ref(P, ..)` and pass `P` as
operand: the two rows run identical code (`bound19(v, P, [Ref(P,..)..])`), so "B4 0 differ from direct, 1,656" compares
the code with itself. B2 likewise: `Ref(HM,..)` against `HM`. The only non-tautological rows are B1 (a hand-picked
operand) and B5 (a hand-picked mismatch). The binding rule as TEXT (resolution at the call's place) is never
implemented: no resolver exists, only the hand-supplied Ref. Draft §8 "EVIDENCE ... THE BINDING RULE (table (B))".

### SIMULATE-2 (CONFIRMED; design; small)
Operand identity is TEXT equality in the script (`ref.operand != operand`, operands are pattern strings). The draft says a
body "laying it against another operand is a compile error" (§5.4 `^` row) but never defines operand identity. Case
undecided by text: `inner(s, lo) := P2 & lex_ge2(s, lo)` called as `P1 & inner([^h, ^m], lo)` where P2 is textually
identical to P1 (e.g. both `/(?<h>\d{1,2}):(?<m>\d\d)/`, or both the same binding `HM`). Text: another operand
(a different occurrence) -> error; script: equal text -> silently answered, no error. Needs a ruling sentence
(identity by occurrence, or by binding?).

### SIMULATE-3 (CONFIRMED; doc/design; small)
Static vs dynamic refusal. The draft says B5 is a "compile error" ("828 of 828 refused"). The script raises RefError
lazily inside `bound19`, only when a condition is reached: `i >= len(s_refs) or i >= len(b) or not cond_ref(...)`
short-circuits before `cond_ref` for a wrong-length call, so a mismatched reference at a position the body never reads
(e.g. `lex_ge2([^h,^m,^x], lo)` with x resolved against another operand, entry 3 unread) is NOT refused in the script.
Text is silent on whether an unread (surplus) reference is checked. Also the text says an unknown or ambiguous label is
an error "AT THE CALL" for each listed reference, including the surplus one; the script has no unknown/ambiguous-label
emulation at all (no row exercises `lex_ge2([^nosuch, ^m], ..)` or a label in two chain operands), so those claimed
errors are untested.

### SIMULATE-4 (CONFIRMED text tension; design; small)
`&` symmetry / chain: §5.4 `^` row says a call that is an operand of `&` gets "the other side of THAT `&`", while §4.1
and the rule's gloss say the lookup is "the other operands of the chain ... the whole flattened chain" (`&` is
order- and grouping-free). These differ for `lex_ge2([^h,^m],lo) & lex_le2([^h,^m],hi) & P` (and for
`(lex_ge2(..) & lex_le2(..)) & P`): the "other side of that `&`" is the other macro (no labels), the chain's other
operands are P. Also `P & Q & call` with h in both P and Q: chain reading = ambiguity error; other-side-of-this-`&` =
Q's h. The text states both; the script only ever writes the call as the right operand next to a single pattern (its own
header: "every rev 18 population writes its call that way"), so call-on-the-left and the multi-operand chain are
untested. The strict row (`P & lex_ge2(..) & !lex_le2(..)`) relies on the census sentence "`!` makes a macro with its
operand open ... filled by the same chain", but the rule text "Written in a call that is an operand of `&`" does not
cover a call that is the operand of prefix `!`: the position rule needs the chain version stated as the rule.

### SIMULATE-5 (CONFIRMED gap; design; medium)
Positions the text leaves undecided (script silent too):
 (a) a call inside a HOLE: `/x${ lex_ge2([^h,^m], lo) }/` or `${ Q & lex_ge2(...) }`. The `^` row bans `${^h}` but says
     nothing about a call carrying references inside a hole with no `&` (operand = ? the hole's scoped text, the outer
     operand?). Only `${ Q & call }` follows from the nested-`&` rule by analogy.
 (b) a call as an ARGUMENT of another macro that lays it against something: `occurs.exactly(1, lex_ge2([^h,^m], lo))`,
     `(m: occurrences(...))`, `list_of(...)`: the call is an argument (position (1)?), not an operand of `&`; which
     operand is "where written"? The text's "no & in sight" error would refuse every such use, yet the strict-`!` use
     (SIMULATE-4) is accepted by the census, so the line between them is undrawn. Nothing about searched mode /
     `occurrences` (hit labels) either.
 (c) a reference PASSED THROUGH TWO macro levels: `wrap2(s,lo) := wrap(s,lo)` is covered by "keeps the operand it was
     written against" by induction, but a middle level that RE-SPELLS: `mk(a, b, lo) := lex_ge2([a, b], lo)` (entries
     are parameters bound to references) or `first(s) := is_late(s[1])` falls under neither `^` position (the entries
     are not `^h` written) nor §4.1's exception list (a reference parameter as an array ENTRY, passed on). Whether
     `[a, b]` is "an array of references" is not stated. Also `at(x, s, lo) := x & lex_ge2(s, lo)` called as
     `at(P, [^h,^m], lo)` (call not an operand of `&`, x = P): the position rule gives "no & in sight" though the
     operand is plainly P; text silent.
 (d) a reference inside an `&` inside a macro body whose own parameter operand `x` is bound at a LATER call: B3 covers
     `x & lex_ge2([^h,^m], lo)` only with x supplying the labels at expansion; a body `&` whose other operand is itself
     an unfilled parameter (`g(x, y, lo) := x & y & lex_ge2([^h,^m], lo)`) has a chain of two unknowns: ambiguity
     check time (definition vs expansion) unstated.

### SIMULATE-6 (CONFIRMED divergence, minor; doc; small)
(N) wrong-length: draft bodies are fixed-size; script uses `n = len(bounds)`, i.e. it runs a 3-entry body for
`lex_ge3([^h,^m],[9,0,0])` correctly, but `ge(v, ["h","m"], ["9"], 2)` models `lex_ge2([^h,^m],[9])` by n=2 with
absent `b[1]` = false entry. Matches text (absent entry, §3.2) for these three calls; flagged only because
`compare.looped`/wrong-length are described as warnings/silent false in the text without a stated diagnostic: a
silently-false wrong-length call is accepted by the script ("no refusal exists in the bodies").

## PROBED-AND-HELD
- Part (a): independently implemented (simulate/emu.py, pure `re`) the bodies from the draft text only (lex_ge/le/between
  2 and 3, strict as `ge & !le`, absent-entry false, unset label false, digits compared by value) and recomputed 9 of
  the 9 quoted worked-row groups (time range, other label order, h:m:s, versions, semver, `\d+` fields, optional minutes,
  strictly above, leading-zero bounds): 65 subject cases, every stated accept/reject reproduced, 0 divergences
  (output simulate/emu.out). Hand-checked the same rows before reading the script: same answers.
- Script header vs text: bodies identical to the text's (`bound19` is the §8 body line for line); absent index = false
  agrees with §3.2/§8; unset label fails (§4.2) agrees.
- B1 nesting answer (inner `&` reads Q's h) agrees text/script.

## Deadline note
Ran emu.py once (00:23-00:25 box clock). Did not re-run predspec19_check.py nor probe the 60 rows' searched/pinned
tables (S), (D) populations, or tables (U)/(C)/(L) beyond reading; did not read caveats (2),(5),(6) in full.
CRITIC COMPLETE
