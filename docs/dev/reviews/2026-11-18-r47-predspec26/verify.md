# VERIFY: predspec26 (review r47, 2026-11-18)

## V1

HOLDS. The subject's "at most one hit, the first, possibly empty" (line 2283; R.1.9 lines 1279-1280 "the one-pattern
LOOP ... gives ONE, the empty hit at 0"; §2.6 line 3846 "at most one hit, the first, possibly empty") is FALSE under the
loop rewrite whenever the first hit is non-empty, and the min counts hold on digit-free text by repeated empty hits.
Own drill `verify/v1.py` (libpcre2 via pcre2h; WHOLE = ANCHORED|ENDANCHORED; a callout after the hit group records
every visit, all accepted so no backtracked visits), the rewrite template the engine uses (model lines 243/266):
- `'\A(?:[\s\S]*?(?<hit>\d*)(?C"r"))*[\s\S]*\z'` on `1a`: HOLDS, hits [`1`@(0,1), ``@(1,1)] (TWO hits, the first
  non-empty); on `12a3`: [`12`@(0,2), ``@(2,2)] (the `3` is never a hit); on `1`: [`1`, ``]; on `a1b`: [``@0] (the
  subject's witness: one hit only because the FIRST hit is empty). Same with `{1,}`.
- `'\A(?:[\s\S]*?(?<hit>\d*)(?C"r")){2,}[\s\S]*\z'` on ``, `ab`, `xyz`: HOLDS with two empty hits at 0; `{3,}` three,
  `{5,}` five: `min = 2` / `min = 3` hold on every digit-free text tried.
Correct meaning, one sentence: a nullable argument's hits are the plain search's hits up to and INCLUDING the first
empty hit, which ends the loop, except that the first `min` hits are always taken and may all be empty (so
`min = k` holds on any text, e.g. by k empty hits at 0).

## V2

HOLDS. Under the PATTERN HOLE row's `0` cell (line 752: "the entire match of the composed rx (the outer rx's `0`)"),
and the SEQUENCE OPERAND row's (line 745: "the entire match of the composed rx"), a `0` written in a condition inside
the part X breaks the zero-place LAW; "the part's own match" keeps it. Own drill `verify/v2.py`, X := `/\d+/ & (0: /3\d*/)`
in `/x${X}y/`, condition a callout after X's group, pool alphabet `x37y` length <= 6 (5,461 texts), compared (labels p)
with the LAW's program `'x(?<p>(?=3)\d+)y'` (itself checked against python `re` `'x3\d*y'`: 0 WHOLE differences):
- `'x(?<p>\d+)(?C"t")y'`, t = `3\d*` fullmatch on X's own match (group p): 0 / 0 / 0 differ (WHOLE / SEARCHED / FIND-ALL).
- same, t on PCRE's group 0 so far (subject[start:pos], `x..`): 15 / 470 / 470 differ, first `x3y` (LAW HOLDS p = `3`,
  this reading FAILS); the program never matches at all.
- `'x(?<p>\d+)y(?C"t")'`, t on the outer rx's entire final match: 15 / 470 / 470, first `x3y`, likewise never matches.
Note: the same condition also sits in an `&` chain (X's own), whose row (line 744) gives "the one stretch every operand
holds on", which agrees with the part's own match: the two rows give different answers for this one `0`, so the table
is at best ambiguous here and the hole/sequence rows' wording is the breaking one.

## V3

HOLDS. Model lines 209-212: both N3 programs are `A_ + '(?C"t")'` with A_ = `'(?<z>\d+(?:,\d)?)'`; n3a tests
`c.get("z").startswith("3")`, n3b tests `c.stretch().startswith("3")`, both with the identical B test on `c.stretch()`.
Group z opens at the match start and the callout sits right after it closes, so z and the stretch are the same span on
every call. Own drill `verify/v3.py`: the same pattern with a callout counting calls where `c.get("z")` differs from
`subject[start:pos]` or from `c.stretch()`, run WHOLE + SEARCHED + FIND-ALL over the engine's pool (alphabet `37,`,
length <= 5, 364 texts): 1,250 callout calls, 0 differ. N3's 0 / 0 / 0 is true by construction and cannot fail; it is
no evidence for THE MANAGER'S READING (1) that line 744 cites ("supported: 0 / 0 / 0 of 364, PART N N3"). (B is never
matched as its own operand on its own stretch in either program.)

## V4

HOLDS. Rule applied, R.1.7 lines 1007-1008: "(2) ONE RULE FOR EVERY BRANCHING (an alternation; an optional; a loop,
which is a branching over its number of passes): ENTERING it resets every label whose group lies inside it; the branch
taken then sets what it sets." Own drill `verify/v4.py`: PCRE runs the plain patterns; the LABEL model replaces
`\k<h>` by a lazy capture + callout equal to the label, where h counts only if its group's span starts at or after an
empty marker group `(?<ps>)` at the start of the (outermost) pass (control, no optional `'(?:(?<h>\d)-\k<h>;)*'`:
label model vs `\k` 0 / 0 / 0 of 5,461).
- `'(?:(?<h>\d)?-\k<h>;)*'` WHOLE `3-3;-3;`: PCRE HOLDS (0,7) h = `3` (the second pass skips the optional; PCRE's
  capture keeps `3`); LABEL FAILS (entering the optional resets h, unset). SEARCHED: PCRE (0,7), label (0,4). Pool
  `37-;` length <= 7 (21,845): 2 / 2 / 2 differ, first `3-3;-3;`.
- `'(?:(?:(?<h>\d);)*,)*=\k<h>'` WHOLE `3;,,=3`: PCRE HOLDS h = `3`; LABEL FAILS (the second outer pass enters the
  inner loop, resetting h; the last outer pass sets nothing). Pool `3;,=` length <= 6 (5,461): 1 / 1 / 1 differ.
So with ONE group name the label rule and PCRE's capture part on plain PCRE patterns; the subject's gap statements
(line 1135 "where a literal has two groups of one name"; lines 1466-1467 "two groups of one name INSIDE ONE literal")
are narrower than the real gap.

## V5

HOLDS (as a gap in the MODEL and its control; the subject's own words point the caseless way). Own drill
`verify/v5.py`, pool `aAbB-` length <= 5 (3,906 texts):
- `'(?i)(?<y>[a-b])-\k<y>'` WHOLE `a-A`: HOLDS y = `a`; the exact-equality callout model
  `'(?i)(?<y>[a-b])-(?<v>[\s\S]*?)(?C"eq")'` (eq: v == y, the engine's `vh` shape): FAILS. Over the pool: 4 / 336 / 336
  differ (WHOLE / SEARCHED / FIND-ALL, label y), first `a-A`.
- R.1.15 (1) (line ~1785): "the value's TEXT, inserted as LITERAL TEXT, never re-read as regex syntax (THE DRAFT'S
  READING; it is the backreference's own behaviour, which `${$y}` must equal)". Taken at its word, a literal inside
  `(?i)` matches caselessly: python `re` with the value `re.escape`d into the `(?i)` pattern agrees with `\k<y>` on all
  3,906 WHOLE (0 differ). So the sentence implies caseless, the engine's model (and its VH0 control on alphabet `12-`,
  no cased pair) is exact, and R.1.15 never states the option dependence.

## V6

HOLDS. Own drill `verify/v6.py`, `(occurrences(/${c}(?<h>\d)/, min = 1) SEQ ",")*`, c := NOT (h: >= 5) as a callout
before the group. REWRITE (PCRE's capture state, h carried): `'(?:(?:[^,]*?(?:(?C"c")(?<h>\d))){1,}[^,]*,)*'`; ONE RULE:
the same with an empty marker `(?<ps>)` at each outer pass start and c counting h only if its span starts at or after
ps (entering the occurrences resets h, R.1.7 lines 1007-1008).
- WHOLE `7,3,`: rewrite FAILS (pass 2's first hit reads pass 1's h = `7`); one rule HOLDS h = `3`. SEARCHED `7,3,`:
  rewrite `7,`@0 (0,2), one rule (0,4).
- Pool `37x,` length <= 6 (5,461), label h: 86 / 238 / 270 differ with gaps `[^,]`; 66 / 150 / 206 with gaps `[^,\d]`
  (the critic's gap; same counts as theirs). Control at ONE depth (no outer loop): 0 / 0 / 0 over `37x` <= 5.
So the regex rewrite carries h across outer passes where the one rule resets it; the R.1.0 cells (line 748 "a hit is
a pass: a condition AFTER its group reads its own hit, BEFORE it the previous hit's (hit-carry, RULED)") state no
depth, and the two premises part at depth two.

## V7

HOLDS. Subject line 739 (THE PROGRAM row, KIND): "MATCH: a lone complement is the compile error here in every mode
(lone-complement-match); write `anything & not_seven`". Own drill `verify/v7.py`: `'[\s\S]*(?C"t")'`, t = the stretch
(subject[start:pos]) is NOT `7` WHOLE (python `re.fullmatch('7', ..)`; my not_seven is "not exactly `7`", the critic's
was "not `7\d*`"):
- `7`: WHOLE FAILS; SEARCHED HOLDS ``@0 (greedy anything backs off to the empty stretch, which is not `7`); FIND-ALL
  [``@0, ``@1]. `77`: SEARCHED `77`@0. ``: holds in all modes.
- Pool `7a\n` length <= 5 (364 texts): WHOLE holds on 363 (fails only on `7`; agrees with python `text != "7"` on all
  364); SEARCHED holds on 364 of 364; FIND-ALL gives a non-empty list on 364 of 364.
So the advised spelling is a working validator only WHOLE; SEARCHED / FIND-ALL it is vacuous (nullable), while the cell
offers it for "every mode".

## V8

HOLDS. Subject line 1610: "on 0 / 0 / 0 of 364 (P3; labels x, y): THE MANAGER'S READING "first slowest is the order
regex itself gives a sequence of alternations", SUPPORTED" (witness: adjacent holes only). Own drill `verify/v8.py`,
a, b := [1, 2] in `/\d{${a}}(?<m>\d*?)\d{${b}}/`:
- copies, first slowest: `'(?|\d{1}(?<m>\d*?)\d{1}|\d{1}(?<m>\d*?)\d{2}|\d{2}(?<m>\d*?)\d{1}|\d{2}(?<m>\d*?)\d{2})'`
  WHOLE `111`: HOLDS m = `1`; sequence of alternations `'(?:\d{1}|\d{2})(?<m>\d*?)(?:\d{1}|\d{2})'` WHOLE `111`:
  HOLDS m = `` (empty). python `re` agrees (copies m = `1`, sequence m = ``).
- Pool `123` length <= 5 (364): 351 / 0 / 0 differ (WHOLE / SEARCHED / FIND-ALL, label m); with a greedy middle
  `(?<m>\d*)` 0 / 0 / 0. So the reading holds only for adjacent holes (or shapes where it happens to agree), not as a
  general equivalence.

## V9

HOLDS. Subject sentence (R.1.4, lines 843-846): "WHICH pieces "might look outside" is THE DRAFT'S READING (the
manager's conservative reading in the record, not his words): `\b` and `\B` where the position can be an edge of the
operand; a lookbehind that can reach before the operand's start; a lookahead that can reach past its end; `\G` and
`\K`" (same list at line 2037). Own drill `verify/v9.py`: the engine's `outward()` alone (extracted by `ast` from
predspec26_model.py, nothing else of the model run); libpcre2 runs B on the stretch's own text (WHOLE) and in the
subject from the stretch start with its end tied by a callout (`B + '(?C"e")'`, e: pos == stretch end, ANCHORED):
- `'(?=\d\d\d)\d+'`: outward False -> engine ACCEPTED; stretch `12` of `123`: own text FAILS, in subject HOLDS (a
  lookahead reaching past the end: the sentence refuses it).
- `'(?:\d+\b)[a-z]*'` (the filled hole d := `/\d+\b/` in `/${d}[a-z]*/`): outward False -> ACCEPTED; stretch `12` of
  `12a`: own text HOLDS, in subject FAILS (`\b` at the edge through the nullable `[a-z]*`).
- control `'\b\d+\b'`: outward True -> FILTER ERROR (the edge-atom shape the engine's witnesses use).
Both shapes read outside on libpcre2 yet the classifier accepts them; it only reads the first and last atom.

## V10

HOLDS (both parts).
- CS3: predspec26_model.py line 523 `last_seq = P.Pcre(r'(?<a>\d)(?<h>\d)(?C"t")', {"t": lt5})` and line 524
  `last_and = P.Pcre(r'(?<a>\d)(?<h>\d)(?C"t")', {"t": lt5})`. With the variable name masked, the two lines have the same
  md5 (`sed -n 523p | sed 's/last_seq/X/' | md5sum` = `sed -n 524p | sed 's/last_and/X/' | md5sum` =
  2a250650d7794a884a7e3672279da482): byte-identical pattern and callout, so line 525's `diff3(...) == [0, 0, 0]`
  cannot fail; `grep CS3 predspec26_sabotage_each.out` finds nothing (no sabotage reaches it). The subject (line 1749,
  "written LAST, the sequenced condition and `&` are one model (CS3)") cites it as a run.
- hole_ok: lines 321-329, the last line `return None  # class, option, backreference: OPEN` (any position other than
  count / name / pattern returns None = OPEN; the engine's CLAUDE.md line 39 repeats "class/option/backreference =
  OPEN"), while R.1.0's HOLE POSITIONS row (line ~768) says "a BACKREFERENCE's name or number (`\k<${n}>`) | none: THE
  DRAFT'S READING (rev 25.1), a compile error". No P6 row exercises the backreference position. An engine reading with
  no sentence in the subject (it contradicts the subject's).

## V11

HOLDS (both). Subject line 1643: "a construct given an ALTERNATION where it expects one value DISTRIBUTES over it, once
per mention". Own drill `verify/v11.py`, n := [2, 5]:
- `repeat(digit, n, n + 1)`: n + 1 lifted = [3, 6]; two mentions -> product (first slowest) (2,3), (2,6), (5,3), (5,6);
  libpcre2 refuses `'\d{5,3}'` ("numbers out of order in {} quantifier"), so removal leaves
  `'(?|\d{2,3}|\d{2,6}|\d{5,6})'`. WHOLE `1234` HOLDS (only through the cross copy (2,6)); the per-member reading
  `'(?|\d{2,3}|\d{5,6})'` FAILS on `1234`; lengths 1 and 7 fail and 2, 3, 5, 6 hold under both. `n - n` lifted =
  [0, -3, 3, 0] (not 0).
- `'\d{-1}'`: COMPILES as literal text (WHOLE `1{-1}` HOLDS, `1` FAILS). `'\d{70000}'`: COMPILE ERROR "number too big
  in {} quantifier". So a lifted -1 is not a count (the kind error's case; the engine's `hole_ok("count")` =
  `all(isinstance(v, int) ...)`, line 323, accepts it), while 70000 is a count whose copy is illegal (removal's case);
  the subject states neither split.

## V12

HOLDS. Own drill `verify/v12.py`, t = h < 5 as a callout: `'(?<h>\d)(?:(?C"t"))?'` WHOLE `7` HOLDS (the test vanishes),
`3` HOLDS; `'(?<h>\d)(?:(?C"t")(?C"t"))*'` WHOLE `7` HOLDS; `'(?<h>\d)(?:(?C"t"))+'` WHOLE `7` FAILS; the bare
`'(?<h>\d)(?C"t")'` WHOLE `7` FAILS. Subject's scope sentence, lines 1755-1758: "THE MANAGER'S READINGS (RULE-AS-CODE,
PART CS CS4; a statement of scope, not runnable against a control): it covers all nine postfix operators, a condition in
sequence and a condition in rx text as a hole alike (`${c}?`); a quantifier on a GROUP holding a condition together
with pattern text quantifies a pattern and is not this case." A group holding ONLY conditions (`((h: <5))?`,
`(c1 SEQ c2)*`) is in neither clause: not named as covered, and not the excluded "together with pattern text" case.
`${c}?` is covered only when the hole's value is a condition written directly. So the sentence does not cover it, and
regex's meaning there is exactly the "`?` never fails" reading the punt exists to keep out.

## V13

HOLDS. Own drill `verify/v13.py`, `/(?:(\d)?;)*/ & (1: <5)` (group 1 named g for the wrapper; condition a callout at
the end): REGEX's capture `'(?:(?<g>\d)?;)*(?C"t")'` (t on PCRE's g) WHOLE `3;;` HOLDS g = `3` (checked against python
`re` `group(1)` of `'(?:(\d)?;)*'`: 0 of 364 WHOLE differ); the LABEL (one rule, last pass's own: a `(?<ps>)` marker
at each pass start, g counts only if set at or after it) `'(?:(?<ps>)(?<g>\d)?;)*(?C"t")'` WHOLE `3;;` FAILS. Pool
`37;` length <= 5 (364): 8 / 33 / 33 differ, first `3;;`.
Subject: R.1.13 line 1486 "There it means exactly what regex means" (the number allowed on one written literal); line
1537 "(1) a number read by the one rule behaves as a name: `/(?:(\d)?;)*/ & (1: <5)` equals REP `& (h: <5)` on 0 / 0 /
0 of 364 (WHOLE `3;;` FAILS)"; §R.7 lines 2100-2101 "KEPT: one literal (`/(\d):(\d)/ & (2: > $1)`,
`/(?:(\d)?;)*/ & (1: <5)`, ...)". The KEPT example gets the label's answer (FAILS) where regex's meaning HOLDS, so
"exactly what regex means" is false for it; and the two readings differ there, which is the ambiguity test the draft
used to refuse the shared-name number.

## V14

HOLDS. Own drill `verify/v14.py`, c := [x, y] in `/(\w*)[${c}]/` (group 1 named g; copies as a branch reset):
- SEARCHED `xy`: "more characters" `'(?<g>\w*)[xy]'` -> `xy`@0 (0,2) g = `x`; copies `'(?|(?<g>\w*)x|(?<g>\w*)y)'` ->
  `x`@0 (0,1) g = `` (empty). python `re` agrees: `(\w*)[xy]` span (0,2) group `x`; `(?:(\w*)x|(\w*)y)` span (0,1)
  group 1 ``.
- Pool `xya` length <= 4 (121 texts), group g: 0 / 32 / 32 differ (WHOLE / SEARCHED / FIND-ALL), first `xy`.
So §R.8 **other-holes** (line 2292) "members: none (the readings agree)", resting on the class-only literal `/[${c}x]/`
(OQ1, 0 / 0 / 0 of 259), is too narrow: once the literal has other parts the two class readings decide answers for
members too.

VERIFY COMPLETE

