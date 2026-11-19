# CRITIC SIMULATE: predspec25 (rev 25 re-check)

## Findings

### SIMULATE-1 — the product's ORDER decides reported labels; "answer-free" holds only for the one witness run
CONFIRMED. Severity: answer (a draft reading that decides answers, unasked: G24-5). Effort: small (ask it, or add
the witness). Blast radius: every literal with two or more value holes of several members. R.1.14, line ~1265 ("THE
DRAFT'S READINGS (answer-free where run): ... the product's ORDER is the written order of the holes, the first
slowest (against the first fastest, n := [2, 3, 4], `[r = repeat(rx.digit, n, n)] & (r: length in L)` ... 0 / 0 / 0").
Repro (simulate/t4.py, my engine from the text, libpcre2 agreeing): a := [1, 2], b := [1, 2],
`/(?<x>\d{${a}})(?<y>\d{${b}})/`. First slowest = `(?|(?<x>\d{1})(?<y>\d{1})|(?<x>\d{1})(?<y>\d{2})|(?<x>\d{2})(?<y>\d{1})|...)`;
first fastest swaps the middle copies. WHOLE `123`: slowest HOLDS x = `1`, y = `23`; fastest HOLDS x = `12`, y = `3`
(libpcre2: the same two answers). Over 364 texts (`12a`, length <= 5), labels compared: 8 / 0 / 0. The draft's witness
cannot discriminate by construction: ONE binding used twice in ONE quantifier with a length test yields the same first
length in either order (the lengths tried come out 2, 3, 4 in both), so the 0 / 0 / 0 is not evidence the reading is
answer-free in general. Same fact one level down: n := [2, 4] vs n := [4, 2] in RX4's own literal gives group 1 =
`1234` vs `12` on WHOLE `123456` (the value's order is the preference order; for a count given as a PATTERN, R.1.12's
"a constant is an rx", the enumeration order of `/2|4/` vs `/[24]/` vs `/4|2/` is nowhere stated). Expected: the
order is a reading that decides labels in WHOLE and must be a slugged question (or the order of a pattern-valued
count stated).

### SIMULATE-2 — the GROUP NAME row's copies cannot be joined: PCRE refuses the branch reset the draft relies on
CONFIRMED. Severity: answer/design (a position-table row whose written-out regex is not a pattern). Effort: small to
state (a different join, or the name row's rule). Blast radius: every name-position hole with two or more members.
R.1.14 position table, line ~1258 (GROUP NAME: "one copy per combination"), with line ~1265 ("THE DRAFT'S READINGS
...: the copies share their group numbers (PCRE's branch reset, so `1` names the same group in every copy)").
Repro: the evidence prints (fwd.out, RX4) `nm := ["a", "b"]: /(?<${nm}>\d)/ -> /(?|(?<a>\d)|(?<b>\d))/` with no check;
libpcre2-8 10.46 REFUSES that text: "different names for subpatterns of the same number are not allowed" (simulate/t5.py).
Each copy alone is legal, so the "removal of illegal combinations" (per combination) never sees it; the evidence's
legality test is per copy only (header: "a combination that is not a legal pattern REMOVED (legality = libpcre2
compiles it)"), never of the joined result. So the shown expansion is not a regex, "the copies share their group
numbers" cannot hold for a name position, and the row's answers are undefined (one group under two names? two
groups, numbers no longer shared?). Expected: the name row states its join (e.g. plain `(?:..|..)` with distinct
numbers, then what `1` names) or the evidence checks the JOINED pattern compiles.

### SIMULATE-3 — removal at LITERAL granularity: two spellings of one all-removed count give different answers
CONFIRMED (by the draft's own rule as written; the evidence never runs a removal inside a larger literal). Severity:
answer. Effort: small (state the granularity, or ask). Blast radius: every literal holding a value hole beside other
alternatives. R.1.14 line ~1250 ("several holes with several members make the literal stand for the CARTESIAN PRODUCT
of the combinations, and a combination that is not a legal pattern is REMOVED"), the COUNT row ("one copy of the
literal per combination"), and RX5's "Every combination illegal (min := [5], max := [2, 3]): nothing is left, `(?!)`".
Repro (simulate/t4.py): m := [5], M := [2]. Spelling A, the hole inline: `/a|\d{${m},${M}}/` -> the one copy
`a|\d{5,2}` is illegal and REMOVED -> `(?!)`: WHOLE `a` FAILS, SEARCHED `xa` FAILS. Spelling B, the same count through
the library: `/a|${rx.repeat(rx.digit, min = m, max = M)}/` -> repeat's own body is the literal copied, so `(?!)` is
inserted in a pattern position -> `a|(?:(?!))`: WHOLE `a` HOLDS, SEARCHED `xa` `a`@1. The rx module's promise that
`repeat` is "a library definition over holes in count positions" makes these two spellings of one thing; they differ
in every mode (FIND-ALL `a`: [] vs [`a`@0]). Drill (b)'s case "a hole whose every combination is removed": the result
depends on which literal is copied. Related gap: ZERO members (`${[]}`, or an empty count set) has no row (the table's
columns are "one member" and "several members"), so `${[]}` vs `${/(?!)/}` vs an all-removed hole is unspecified.

### SIMULATE-4 — "inside rx text a backreference already reads it" is false once names are shared, and every SEQ of shared names makes them so
CONFIRMED. Severity: answer/doc. Effort: small (correct the parenthetical; state what a part's `\k<h>` reads after a
splice). Blast radius: R.1.7 THE THREE READS (b), and every composed pattern with a backreference in a part. Lines
~977-980 ("(b) THE CARRIED-CAPTURE FORM, REQUIRED ...: PCRE's capture, the value from the last time a group of the name
was SET (inside rx text a backreference already reads it)"); R.1.13 (2)-(3) (a composed pattern behaves as a literal;
across SEQ one label); §R.6's own A6 line ("`\k<x>` reads `a`, PCRE2 taking the first SET group of the name").
Repro (simulate/t6.py, libpcre2): `/(?J)(?:(?<x>a)|(?<x>b))+\k<x>/` matches `abba`, not `abbb`: the backreference
reads `a` while the last-set capture (and the label) is `b` -> the parenthetical contradicts §R.6. The splice makes it
bite: A := `/(?<h>\d)/`, B := `/(?<h>\d)\k<h>/` (B alone matches `33`, not `37`); `A SEQ B` written out is
`(?J)(?:(?<h>\d))(?:(?<h>\d)\k<h>)` (without `(?J)` libpcre2 refuses it): WHOLE `733` FAILS, `737` HOLDS, since B's
`\k<h>` now reads A's group. So a part's backreference changes meaning under composition, against "a compose and a
literal rx have the same label behavior" read naturally, and the draft states neither the written-out regex's `(?J)`
nor what a backreference reads across parts (`rx_module.md` row 24 said the group "lives in another hole's own
namespace", which label-flow's flat names no longer give).

### SIMULATE-5 — "numbers name the nearest pattern to their left" over an ALTERNATION: every reading breaks R.1.4's distribution law, and no question covers it
CONFIRMED (engine from the text; each reading run). Severity: answer (an unasked gap beside **sequence-numbers**).
Effort: small (widen sequence-numbers to every composition, or state the `|` case). Blast radius: numbered conditions
after any `|`. R.1.13 line ~1196 ("in `A & B & (1: ...)` the number names a group of B, the pattern the condition is
written on"); §R.8 (b) **sequence-numbers** (asks only after the SEQUENCE operator); R.1.4 (``&` DISTRIBUTES over a `|`
on its LEFT ... 0 / 0 / 0 of 1,365`).
Repro (simulate/t7.py): A := `/(\d)x/`, B := `/(\d)y/`, X := `(1: <5)`. The distributed form `(A & X) | (B & X)` (each
`1` names its own literal's group): WHOLE `3x` HOLDS, `3y` HOLDS; FIND-ALL `7x 3y 3x` [`3y`@3, `3x`@6]. The undistributed
`(A | B) & X` under sequence-numbers' three candidates: (a) written-out numbering, `(?:(\d)x)|(?:(\d)y)`, 1 = A's group:
`3y` FAILS (1 unset), FIND-ALL [`3x`@6]; (b) a composed pattern has no numbers: the unknown-label ERROR; (c) the nearest
literal = B: `3x` FAILS, FIND-ALL [`3y`@3]. So with a numbered condition the left-distribution law fails under every
candidate (only a branch-reset written-out numbering, which no candidate names, would keep it), and the gap is
not in the question list.

### SIMULATE-6 — a hole whose edge assertion sits at a FILTER operand's edge: hole-reading and operand-context give opposite rules; §0.1 L71's printed answer is not re-derived
SUSPECTED (text divergence; no answer to run until a rule is picked). Severity: design/doc. Effort: small (one sentence:
classify the EXPANDED operand, or exempt holes). Blast radius: every hole inside a filter (right side of `&`, a `label:`
set, an `&` inside a hole). R.1.4 line ~731 ("REV 25: a HOLE is no longer among them (hole-reading, RULED: a hole is a
PATTERN position, matched in place, and an assertion at its edge crosses the border"); R.1.4 line ~720 ("ANY PIECE
THAT MIGHT LOOK OUTSIDE THE STRETCH IS A COMPILE ERROR"); R.1.14 hole-reading (2); §0.1 L71 line 2433 (no REV 25 mark).
Drill (b), the second insertion point (inside a nested program): num := `/\b\d+\b/`, `/\d+/ & /${num}/`. Read by
hole-reading, num's `\b` crosses the hole's border and lands at the operand's edge, which is the stretch's edge;
read by operand-context the expanded operand `(?:\b\d+\b)` holds an edge `\b`, a COMPILE ERROR, exactly as
`/\d+/ & num` is. The draft states both sentences and picks neither. The same tension decides L71's printed answer:
`/x${/^a/ & /(?s).*/}/` on `xa` "matches 0-2" because "the `&` operands are filter roles over the text the hole takes";
under rev 25 the hole is "the inserted pattern as a WHOLE, ... matched where it stands", whose left operand is
then searched in place (R.1.4: "the paths of P", P not a filter), its `^` the subject's start, and the program never
matches `xa`. And `/x${num & /\d+/}/`: under L71's reading num is a filter role (its `\b` the operand-context ERROR);
under hole-reading it crosses the border (compiles, never matches). Outer chain (`wb SEQ digits SEQ wb`, `/x${num}/`)
and a binding used twice (`num SEQ "," SEQ num` matches `1,2`; `num SEQ num` matches nothing, the can-never-match
warning) are unambiguous and hold (PROBED-AND-HELD).

### SIMULATE-7 — the hit list's FAILED FIRST TRY prints hits [`00`, `12`]: the evidence judges "under 100" with int(), against §2.4's canonical numerals
CONFIRMED. Severity: answer (a shown hit list; the HOLDS verdict survives). Effort: trivial (judge with the
numeral rule, reprint). Blast radius: R.1.9's PART H line (rev 24.4 text, in scope). R.1.9 line ~1150 ("THE FAILED FIRST
TRY ... all four HOLD, with hits [`34`], [`12`, `34`], [`12`, `45`], [`00`, `12`] (the lazy gap is re-entered and
swallows the start of a long number)"); R.1's NUMERALS sentence (line ~559: "an integer comparison set contains
CANONICAL numerals ...; so `00` is outside `>= (9, 30)`").
Repro: R/tree/.../predspec244_evidence/predspec244_model.py:674 `ok = all(int(c.subject[a:b]) < 100 for a, b in hits)`:
int("00") = 0 passes. Under the draft's numeral rule `00` is not in `< 100` (its literal has no leading zero), so the
list [`00`, `12`] is rejected and the backtracking goes on: my engine from the text (simulate/t9.py,
`\A(?:.*?(?>(?<n>\d+)))*\D*\z` then the judge with canonical numerals) gives `x300 12` HOLDS with hits [`0`, `12`]. The
other three lists and every verdict of PART H reproduce (the model: `1234` FAILS, `12 34` HOLDS [`12`, `34`], `12 345`
FAILS, `x300 12` FAILS; the inside-judged form all HOLD).

### SIMULATE-8 — the evidence's header and its sabotage switch: the readings are sentences of the subject; the switch CAN fail, but two rev 25 readings have no check that could
CONFIRMED. Severity: maintenance. Effort: small. Blast radius: predspec25_model.py. Every reading the HEADER lists is a
sentence of the subject (splice and every operand one non-capturing group: R.1.14 "each one non-capturing group";
postfix > SEQ > `&` > `|`: "THE ORDER, tightest first"; longest first: "the operators are read LONGEST FIRST"; copies per
combination, first hole slowest, legality = libpcre2: "the product's ORDER is the written order of the holes, the first
slowest", hole-member-kind's "pattern legality"; the numbering by opening parenthesis, a name's number an alias:
R.1.13; the static-order control: "the label = the item last in PATTERN ORDER among those set"). The switch
(`PREDSPEC25_SABOTAGE=1`, re-run here) fails 13 of 42 checks (PS x7, RX2 x2, RX4, RX5 "two to four", RX8 x2): it can
fail. Not guarded: (a) the product ORDER, whose only comparison (RX5 "the ORDER of the product") is no check and cannot
differ by construction (SIMULATE-1); (b) the joined copies' legality, never checked (SIMULATE-2); (c) PARTS LF, NUM, E,
W, as the draft itself says. A sabotage row "first hole fastest" would pass every check today.

## PROBED-AND-HELD
My own backtracking engine (simulate/eng.py: the one label rule, PCRE order, PCRE2's global loop) and rx-module
expander (simulate/rx.py), both written from R.1.7 / R.1.14's sentences BEFORE reading the evidence's expander, then
diffed against fwd.out (re-run: byte-identical to the committed .out) and libpcre2 (pcre2h):
- PART PS: the 8 shown lines (WHOLE `3;4;7;`, `3;3;9;`, `3;7;4;`, `9;1;`, `7;`, ``; SEARCHED `3;7;`@0, `9;`@0); engine =
  libpcre2 0 / 0 / 0 of 1,365; per-pass reset vs libpcre2 3 / 15 / 27 (first `3;1;`); the sorted intent 0 of 1,365; the
  except-last intent 0 of 1,093; `c := NOT (h: >= 5)` WHOLE `3;7;` HOLDS, `7;3;` FAILS, SEARCHED `7;`@0, FIND-ALL [`7;`@0,
  `3;`@2, ``@4, `3;3;`@5, ``@9]. All held.
- PART AS: [`7`, `3`]; it [`7`, ``, `3`, ``], h [`7`, `3`]. Held.
- R.1.7 rev 24.4: the separated-list table (4 cells, labels and arrays), the conditioned item (5 lines), list(item)|item
  (4), the two-groups table (11 cells, one rule and carry columns), derivations (i), (iii) in 3 modes, (iv) x2, (v),
  (vi) x2; the rev 24.3 lazy FIND-ALL witness [``@0, `;`@0, ``@1]. All held.
- R.1.9 PART H: the model's four verdicts and lists, the inside-judged form; the first try's verdicts (one list differs:
  SIMULATE-7).
- R.1.13: (i) `A SEQ B` on `7` / `7,3` / SEARCHED / FIND-ALL; (ii) `AL SEQ BL` h = `2`; the composed list = the literal
  (label and array, 2 texts); `aa.h` WHOLE x2 / SEARCHED / FIND-ALL; NUM: the numbering of `(a)(?:b)(?<n>c)(?=d)((d)e)`,
  `/(\d)\d/ & /\d(\d)/ & (1: <2)` 4 answers, `(2: > $1)` 4 answers, numbered-duplicate (a)/(b) 8 answers,
  sequence-numbers (a)/(c) 6 answers. Held. Drill: numbers with `$` (`/\d(\d)$/`) and a lookahead (`/\d(?=(\d))\d/`) in
  the nearest operand name that operand's group on `12`, `21`, `10` (held); with `\b` at its edge the operand is the
  operand-context error, so the number never reads (consistent).
- R.1.14: RX1 (expansion, 3 modes, vs `\b\d+\b` 0 / 0 / 0 of 364 over `1x `); RX3 (0 of 364 texts match; `(?:ab)?c` vs
  `ab?c` 6 answers); RX4 (1234 vs 12); RX5 (expansion, 3 modes, WHOLE vs `\d{2,4}` 0 of 364; one-argument 0 of 364; all
  removed -> `(?!)`); RX6 (5 answers, array, plural vs `\d+` 0 / 0 / 0); RX7 (18 operator rows, my engine = libpcre2,
  `(?:\d+)??` 0, 3, 2, 1); RX8 (`ab+`, `(?:ab)+`, `x1|2` and its other order, the conditioned sequence: 14 answers);
  hole-member-kind, plus-operands, quantified-condition, label-mark L3: every shown answer recomputed by hand and
  equal to the evidence. Drills: an edge assertion at the outer chain (RX1, `/x${num}/`) and through a binding used
  twice (`num SEQ "," SEQ num` HOLDS `1,2`, 33 searched matches over `1, ` to length 5; `num SEQ num` 0 matches) held.
- §R.2 PART E: empty-search 3 modes, min-values 3 modes, `aab` re-cut (by hand); PART W five trigger rows (by
  reading). Held.
- The sabotage switch: re-run, 29 of 42 OK (it can fail; see SIMULATE-8).

CRITIC COMPLETE
