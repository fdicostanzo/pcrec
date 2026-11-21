# CRITIC MODECLOSURE: predspec28 (review r52)

Scratch and runs: `modeclosure/probe1.py`..`probe6.py` (libpcre2 through pcre2h, python `re` as the second control
where it can express the case). Callout model as rev 28's (lazy `(?<v>[\s\S]*?)` + callout; label = predspec261's
`(?<ps>)` marker model).

## Findings

### MODECLOSURE-1  CONFIRMED   severity: design   effort: M
- where: R.1.15 header [REV 28] vs §11 Literals [REV 28] (and R.1.16 A19, §2.7 `any_case` row); place: an `&` written INSIDE a hole (R.1.14 (4): "an `&` written INSIDE a hole keeps both operands filter roles over the text the hole takes")
- claim: R.1.15 says "ONE rule for everything in a hole: what is inserted STARTS with the flags in force at the hole"; §11 says "An `&` operand, a condition's set and a macro argument in a filter role are not holes: the ruling does not speak of them, and this section's ROLE TABLE keeps them as their own literals". When the hole HOLDS an `&` expression, both operands are "own literals", so the flags in force at the hole reach NOTHING: exactly the outcome the owner's flags-propagate argument rejects ("if they don't propagate down, they effectively do not take effect at the hole", CF record 2026-11-18 discussing flags-propagate). Consequence: adding a filter that admits everything changes the answer, so `${X & total}` != `${X}` inside a `(?i)` hole.
- repro: (a) `/(?i)(?<y>[ab])-${$y & /./}/` (draft's reading: `$y` an `&` operand with nothing written, `/./` caseful) against `/(?i)(?<y>[ab])-${$y}/`: 4 / 336 / 336 of 3,906 texts (`aAbB-`, length <= 5); WHOLE `a-A`: `${$y}` HOLDS, `${$y & /./}` FAILS; SEARCHED `x a-A` `a-A`@2 vs FAILS; FIND-ALL `a-a a-A` [`a-a`@0, `a-A`@4] vs [`a-a`@0]. `${$y}` equals libpcre2 `(?i)(?<y>[ab])-\k<y>` 0 / 0 / 0. (b) a pattern operand: `/(?i)x${/ab/ & /a./}/` vs `/(?i)x${/ab/}/`: 3 / 258 / 258 of 3,906 (`xaAbB`, length <= 5), first WHOLE `xaB`. With propagation reaching the operands both are 0 / 0 / 0. Minimum witness length 3.
- blast radius: R.1.15 (12)'s `${$y & <5}` (harmless on digits, not on letters); §2.7 `any_case` body (A19's "filter-role argument still differs" is this same split); §R.8 any-case-body; R.1.14 (4); §0.1 L32 ("SAME where q writes no flags" fails when q is an `&` expression); every macro body whose hole receives an `&`-built argument (`quoted`, `left`/`right`/`mid`).

### MODECLOSURE-2  CONFIRMED   severity: design   effort: S
- where: R.1.16 T20 [REV 28] ("a COMPILE ERROR at the backreference unless the literal says `(?J)`"), A25; against R.1.15 [REV 28] ("what is inserted STARTS with the flags in force at the hole")
- claim: `J` is a flag a literal can carry. Under flags-propagate a literal inserted at a hole where `(?J)` is in force STARTS with `J`; T20's error keys on "the literal SAYS `(?J)`". Which wins is not stated: q := `/(?:(?<h>a)|(?<h>b))\k<h>/` is a compile error alone, and at `/(?J)${q}/` either still an error (T20's words) or legal (R.1.15's words). Also the draft's "as text" reading of a hole goes wrong under `J` with names: the outer group and the inserted group share a name in the text, and PCRE's first-set rule binds the INSERTED `\k<h>` to the OUTER group, against "its own group numbering" / "inside X, X's own namespace".
- repro (libpcre2): `(?:(?'h'a)|(?'h'b))\k<h>` REJECTED ("two named subpatterns have the same name (PCRE2_DUPNAMES not set)"); `(?J)(?:(?:(?'h'a)|(?'h'b))\k<h>)` COMPILES (WHOLE `aa` HOLDS, `bb` HOLDS, `ba` FAILS). Text reading of `/(?J)(?<h>a)-${/(?<h>b)\k<h>/}/`: `(?J)(?'h'a)-(?:(?'h'b)\k<h>)` WHOLE `a-ba` HOLDS, `a-bb` FAILS (the own-namespace reading gives the reverse); without the outer `(?J)` the same text is REJECTED (duplicate name). Also: `(?'h'a)(?:(?J)(?'h'b))` COMPILES, so a `(?J)` the INSERTED rx writes reaches a name the OUTER literal carries in libpcre2.
- blast radius: T20, A25, §R.8 same-name-twice; the record's row 147 m1 (a group arriving through a hole or a part: NOT STATED) is the same gap from the other side; R.1.14 HOLE-READING's "`(?:foo)` is that reading as text".

### MODECLOSURE-3  CONFIRMED   severity: design   effort: S
- where: §11 Literals (UNMARKED sentence rev 28 left standing: "a literal means EXACTLY what PCRE means: NO implicit extended mode (`/foo bar/` keeps its space, `#` is literal); extended mode is per literal (`/.../x` or a leading `(?x)`)"); R.1.15 [REV 28] ("a read is the case with nothing written"; "So the compile-time one-string rx `q := /a/` ... now gives the read's answer"; "the same holds for `m`, `s` and `x`"); R.1.15 (1) ("it is never re-read as regex syntax")
- claim: under propagation `x` in force at a hole reaches an inserted literal, so `/foo bar/` LOSES its space and `#` starts a comment there: §11's sentence is false inside an `(?x)` hole and was not marked. And the "one rule" unification of a read with a one-string literal holds for `i` only: a read is a string set (never re-read as syntax, R.1.15 (1)), so `x` does nothing to it, while it rewrites the literal's set. The PART J equality (literal q = read) does not survive `x`.
- repro: at an `(?x)` hole after `(?<y>a\ b)-`: q := `/a b/` inserted (`(?:a b)`) vs the read `${$y}` (literal text) vs libpcre2 `\k<y>`: on `a b-a b` FAILS / HOLDS / HOLDS; on `a b-ab` HOLDS / FAILS / FAILS (python `re`: `(?x)(?P<y>a\ b)-(?:a b)` on `a b-a b` no match, `(?P=y)` match). Minimum witness length 6.
- blast radius: §11, R.1.15 header and (1), (10)(b) ("as a literal written there would be"), §5.4 `${ }` row, A18, §0.1 L32, §13 O32.

### MODECLOSURE-4  CONFIRMED   severity: doc   effort: S
- where: R.1.14 HOLE-READING (1) [REV 28] ("`(?:foo)` is that reading as text: `/(?i)xxx${/foo/}yyy/` = `/(?i)xxx(?:foo)yyy/`"); §0.1 L32 [REV 28] ("SAME where `q` writes no flags of its own")
- claim: with `x` in force the "as text" spelling is not the reading: an inserted literal containing `#` makes its comment run past the wrapper's `)`. Both stated equalities fail.
- repro: q := `/a#b/` at `/(?x)${q}c/`: the hole reading (comment ends at the hole) matches `ac`; the stated text `(?x)(?:a#b)c` is REJECTED by libpcre2 ("missing closing parenthesis") and python `re` ("missing ), unterminated subpattern"); the inlined text `(?x)a#bc` matches `a` only (the comment eats `bc`). A text spelling that does hold needs a newline before the `)`: `(?x)a(?:#b<newline>)c` WHOLE `ac` HOLDS. Length 2.
- blast radius: R.1.14 (1), §0.1 L32, §13 O32's resolution, any emitter that builds the hole by pasting text.

### MODECLOSURE-5  CONFIRMED   severity: design   effort: S
- where: R.1.15 [REV 28] ("the same holds for `m`, `s` and `x`"); the record's flags-propagate m1 ("the rule covers every flag a literal can carry ... `m`, `s`, `x` under the same sentence is a reading")
- claim: the SET of propagating flags is stated only by the four run. PCRE literals also carry `n`, `U`, `J` (MODECLOSURE-2) and `xx`. `n` in force at a hole turns a LEGAL inserted literal into a compile error; `U` moves the inserted rx's path order (so its labels' values); neither is stated.
- repro (libpcre2): `(a)\1` COMPILES; `(?n)(?:(a)\1)` and `(?n)x(?:(a)\1)` REJECTED ("reference to non-existent subpattern"). `(?U)x(?:a+)` SEARCHED `xaaa` -> `xa`@0 (q := `/a+/` written greedy). `(?xx)(?:[a b])` compiles (the class loses its space).
- blast radius: R.1.15 header, §11, §5.4 `${ }`, R.1.16 T20 (J), §2.7 bodies holding `${rx}` (any macro whose body sets `n` or `U`).

### MODECLOSURE-6  CONFIRMED   severity: doc   effort: S
- where: R.1.15 [REV 28] / §11 [REV 28] "the flags in force at the hole" (the mode list in the brief: `(?i)` after the hole, scoped `(?i:..)`)
- claim: "in force" is PCRE's positional rule, which includes PCRE's carry of an unscoped setting into LATER BRANCHES of the same group: in `/(?:a(?i)b|${q})/` the hole is caseless though no `(?i)` precedes it on its own branch. A `(?i)` after the hole in the same branch does not reach it; a scoped `(?i:..${q}..)` does. The draft states none of these; a reader of "at the hole" can read it lexically per branch.
- repro (libpcre2): `(?:a(?i)b|c)` WHOLE `C` HOLDS, `aB` HOLDS, `Ab` FAILS. python `re` cannot serve as control (no mid-pattern global flags).
- blast radius: R.1.15, §11, §5.4 `${ }`.

### MODECLOSURE-7  SUSPECTED   severity: design   effort: S
- where: R.1.0 THE PLACE TABLE, the POSITIVE LOOKAHEAD / LOOKBEHIND row ("as the rx it is written in"); R.1.15 (rules 2 and 3 in a lookbehind)
- claim: a value hole (`${$y}`) inside a LOOKBEHIND has no stated meaning: its length is known only at run time; the draft's PCRE control `\k<y>` is refused there for an unbounded group, and the callout model cannot be placed there either. The unset rule in a negative lookbehind (`(?<!${$y})`, the never-matching rx: always true) follows only if a read is legal there at all.
- repro: libpcre2 `(?<y>\d+)-(?<=\k<y>-)x` REJECTED ("length of lookbehind assertion is not limited"); `(?<y>\d)-(?<=\k<y>-)x` COMPILES; `(?<=(?<v>[\s\S]*?)-)` REJECTED. Confirm by a sentence in R.1.15 or the place table saying legal (and how), error, or UNDER CONSTRUCTION.
- blast radius: R.1.0's lookbehind row, R.1.15, R.1.16 T12.

## PROBED-AND-HELD
- Rule (2), unset = never-matching, two spellings of one empty set, TOP in every mode: `/(?<y>\d)?-${($y & <5) | "x"};/` (unset read AND a set-but-filtered read in one literal) equals libpcre2 `(?<y>\d)?-(?:(?(<y>)(?:(?=[0-4])\k<y>)|(?!))|x);` and `(?:(?=[0-4])\k<y>|x);` on 0 / 0 / 0 of 19,531 texts (`37x-;`, length <= 6).
- Rule (2) in an `occurrences` ARGUMENT, read after its group (the hit's own): hit lists of the same literal equal the PCRE `(?!)` spelling on 0 of 78,125 texts of length 7 (`37x-;`), the edge case SECOND (`3-3;-x;`: [`3-3;`@0, `-x;`@4] both); min = 2 by hit count 0 of 19,531 (length <= 6).
- Rule (2) + (3), a label set at two loop depths read from outside: `/(?:(?:(?<y>\d);)*,)*=${$y | "x"}/` vs `\k<y>|x`: 1 / 1 / 1 of 19,531 (`3;,=x`, length <= 6), WHOLE `3;,,=3` (label FAILS, capture HOLDS), `3;,,=x` both HOLD: the alternative beside the unset read survives, as R.1.15 (3) states; the split is (8)'s label/capture split, already counted there.
- A NULLABLE loop body: `/(?:(?<y>a)?)*-${$y}/` vs `/(?:(?<y>a))*-${$y}/`: 0 / 0 / 0 of 1,093 (`ab-`, length <= 6); the empty last pass DOES run in libpcre2 (marker at 1, label unset) and PCRE backtracks to the path without it, so the unset rule does not split the two spellings; `\k<y>` HOLDS on `a-a` for both.
- Rule (1) for `i` through a read: `/(?i)(?<y>[ab])-${$y}/` = libpcre2 `\k<y>` 0 / 0 / 0 of 3,906 (`aAbB-`, length <= 5); `/(?i)x${/ab/}/` with propagation into the hole = plain `(?i)x(?:ab)` 0 / 0 / 0 of 3,906.
- `${[]}` in a PATTERN position is `(?!)` (R.1.0 ZERO values row), the same as the unset read; in COUNT/CLASS/OPTION positions reads are UNDER CONSTRUCTION / NOT STATED (T13, T15, T16), so no second spelling exists there to disagree. Not run beyond the table.
- Rule (4) is a compile-time property, so mode-independent and place-independent within one written literal; libpcre2 agrees (`(?'h'\d)(?'h'\d)-\k<h>` REJECTED without `(?J)`). Its gaps are MODECLOSURE-2.
- Hole inside a hole for flags: transitive under the stated rule (each insert starts with the flags at its own hole); no counter-example found beyond MODECLOSURE-1/-4/-5.
CRITIC COMPLETE
