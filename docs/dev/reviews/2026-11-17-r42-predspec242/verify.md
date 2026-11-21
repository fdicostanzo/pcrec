# VERIFY — round predspec242

## V1

Scripts: verify/w/v1.py (output v1.out). The engine loader verify/w/eng.py is modeclosure's work/eng.py copied
unchanged. The libpcre2 control is mine: a `(?<ps>)` capture at the start of the loop body, and a callout that reads h
only when h starts at or after ps. The body has no lookaround, so the position test gives the same answer as a time
test here.

- libpcre2 fact, HOLDS. `/(?:(?C"s")(?<p>)(?<h>\d)?)*(?C"e")/` WHOLE on `3`: the body-start callout fires at pos 0 and
  again at pos 1. At the end p = (1,1) and h = (0,1), and the match is (0,1). So PCRE2 ran a second, EMPTY iteration
  and kept it. `/(?:a|(?<e>))*/` WHOLE on `a` ends with e = (1,1): the empty iteration even SETS a group.
- Engine lines, HOLD (read). pathimpact_model.py l.154 has `if p2 == pos and count >= lo: continue  # an empty pass past
  the minimum ends the loop`, which drops that path and keeps the state from before the pass. predspec241_model.py
  l.148 (`Rep.walk`) has `if e == pos: continue  # an empty pass ends the loop (PCRE)`. `OccS.walk` (l.182-186) KEEPS an
  empty hit as the last hit ("an empty hit ends the loop", then `yield from tail(e, h)`). So the three loop kinds do
  not agree with each other.
- Witness `/(?:(?<h>\d)?)*/ & NOT (h: <5)` on `3`:
  - Engine: WHOLE FAILS; SEARCHED ``@0 with h unset; FIND-ALL [``@0, ``@1].
  - libpcre2: WHOLE HOLDS with h unset; SEARCHED `3`@0 with h unset; FIND-ALL [`3`@0, ``@1].
  - The rule's text gives the libpcre2 answer by R.1.7 (2)-(3), if the empty iteration is a pass: the last pass set no
    h, so `(h: <5)` fails and NOT holds.
  - On `37` and `7` the answers agree but the reported label differs: engine h = `7`, libpcre2 h unset.
  - The positive `(h: <5)` agrees on all three texts. Its callout fails on the empty-pass path, and PCRE backtracks to
    the path without that pass.
- MODECLOSURE-1 count, HOLDS. I re-ran engine vs my own control on alphabet `37;`, length <= 4: WHOLE 30, SEARCHED 80,
  FIND-ALL 116 of 121, first text `3`. This is exactly the critic's figure, from a control that shares no code with
  model U. The positive form differs on 0 / 0 / 0.
- Does the subject say whether the empty iteration is a pass? NO sentence does for a pattern loop:
  - R.1.7 (2)-(4) (l.702-711) speak of "the LAST pass" and "a group that took no part in a pass" without defining a
    pass.
  - The only sentences on PCRE's empty iteration are about `occurrences` (§2.6 l.2388-2390: "PCRE ends a loop whose
    iteration matched the empty string ... at most ONE hit (the first, possibly empty)"; §0.1 L53 l.1639). They count
    the empty iteration as a hit, which matches OccS and goes against the pattern loops.
  - §R.6 has no row on it; its only nullable mention (via l.1555) is about the empty stretch and defaults.
- Do the §R pools contain a nullable loop body? NO. I read every loop pattern in predspec241_model.py and
  predspec242b_model.py (REP, REP1, CLOSE, TML, KH, ALT, NEST/INNER, PL, the helper-group C2 models, EAT, ANY, the hole
  items ITEM1/ITEMO/ITEMC). Each body consumes at least one character (`;`, `,`, `\d`, `[a-z]`, `[\s\S]`). So no §R
  count can see the difference. C2's "16 of 16" and PART N's 0-of-1,365 are silent on it, not evidence against it.

VERDICT: HOLDS. SIMULATE-2 and MODECLOSURE-1 are confirmed as one item: the libpcre2 fact, the engine lines, the witness
in all three modes, the 30/80/116 count, the text gap, and the absence from every pool.

## V2

I read §2.2 (l.2138-2209) and §2.4 (l.2233-2278) in full.
- §2.2 states no numeral-domain rule. Its only canonical mention is the `!<200` / `>=200` contrast (l.2181-2185). This
  confirms SIMULATE-5: the §R citations "§2.2" point at the wrong section.
- §2.4 decides the question in its RULE paragraph, l.2236-2240: "The LITERAL decides the reading ... an integer
  comparison set contains CANONICAL numerals of VARIABLE WIDTH (the `\d+` shape: no leading zeros, sign or decimal
  point UNLESS THE LITERAL HAS THEM)".
- DICT-DOMAIN (l.2248-2250) applies that per component: "must lie in its literal's DOMAIN (canonical numerals for an
  integer literal)". Its examples `(9, 0)` and `(9, 30)` are literals WITHOUT leading zeros. That is why `9:00` and
  `10:00` are rejected there, and why the STOP line (l.732-735) still holds.
- The literal `00` HAS a leading zero. By l.2239-2240 its component's domain admits leading zeros, so `00` lies inside
  `== (10, 00)`'s second component.
- The default `m = 00` supplies the TEXT `00`. l.2853 says "the DEFAULT `h = v`, per test, any text", and l.847 says
  `default.unused` fires on "a default whose text is outside every set it meets". The default's text `00` therefore
  meets a component whose literal admits it.

Under the document's own rule:
- R.1.7 S4 (l.726-727) HOLDS / FAILS / HOLDS on `9:45,10,` / `10,9:45,` / `10:45,10,`, exactly as published. The last
  pass sets h = `10` and m is unset, so the default stands in.
- §R.8 some-own (l.1105) is likewise as published.

The engine does compare STRINGS there, HOLDS (read):
- predspec241_model.py l.1175 has `lambda h, m: (h, m) == ("10", "00")`, and predspec242b_model.py l.613 has the same.
  `jeq` at l.1068 is also a string compare. The numeral tests go through `num()` (lastpass_model.py l.276).
- This compare EQUALS the l.2240 reading on every CLOSE text. h is `\d+` against the literal `10` without leading zeros:
  a string compare rejects `010`, as the canonical rule does. m is `\d\d` (or the default `00`) against the literal
  `00`. So no CLOSE answer can move.
- PART S's CHECKS line (out l.521) does list S1, S2, S3 and S5 only. S4 is printed (out l.213-215, NOW = SHOWN) without
  a model control.

Left over:
- "unless the literal has them" is a rule of §2.4, not of DICT-DOMAIN's parenthetical. The text never says what an
  integer set written `00` contains beyond admitting leading zeros (only `00`? every padded zero?).
- The §R preamble's "Numerals are canonical (§2.2: `0|[1-9]\d*`)" (l.481) states the rule without its exception. That
  is a doc item (cite §2.4 and its "unless the literal has them"), not an answer item.

VERDICT: PARTLY.
- The engine's string comparison and the missing S4 check: HOLD.
- SIMULATE-1's consequence (S4 and some-own become FAILS / FAILS / FAILS by DICT-DOMAIN): REFUTED. §2.4 l.2239-2240,
  "no leading zeros ... unless the literal has them", puts `00` inside a component whose literal is written `00`. I ran
  no call: this is a text derivation, and the published answers stand.

## V3

Script: verify/w/v3.py, mine. Names are spelled `(?P<x>` so pcre2h's unique-name lookup is bypassed.

The label by the text: x = `b` on `abb`.
- §4.3 l.2972-2975: "A duplicate label INSIDE A LOOP is a REPEATED label first: its iterations in match order, each
  iteration's value from whichever of the duplicate groups THAT iteration set".
- R.1.7 (2) (l.702-704): the bare condition reads the LAST pass's own. The last pass of `abb` is `b`, set through
  group 2.

The capture on libpcre2 10.46 is `a`:
- `/(?J)(?:(?P<x>a)|(?P<x>b))+\k<x>/` WHOLE matches `abba` (groups 1 = `a`, 2 = `b`) and does NOT match `abbb`.
- So `\k<x>` reads `a`: PCRE checks the groups of a duplicated name in pattern order and uses the first SET one. Group
  1 is still carried from pass 1.
- The same split shows on `aba`: it matches WHOLE as loop `ab` plus `\k` = `a`, where the label after loop `ab` would
  be `b`. `baa` matches with `\k` = `a`.

So the label (`b`) and the capture (`a`) differ although the last pass DID set x. That falls outside §R.6's row
(l.986: "a label set inside a loop, read after the pattern or inside a later pass that did not set it"). x is mandatory
in every pass, so §R.8 pass-list-read's "last: with a mandatory h it equals libpcre2's backreference `\k<h>`"
(l.1110) is false for a duplicate name.

Mitigation, not a refutation: at the default level a bare `$x` on a repeated label is an error (§4.3 l.2968-2970,
2976-2977). So only a CONDITION or a `vm`-level read meets it, and §R.8's sentence is about `$h`. But R.1.7 (2) makes
the condition read the last pass's own, and the row's wording covers conditions.

VERDICT: HOLDS (doc). SIMULATE-3's fact and its consequence for l.986 and l.1110's wording reproduce.

## V4

Script: verify/w/v4.py (output v4.out). It uses the same engine loader as V1. It compares the literal NEST
`/(?:(?:(?<h>\d)?;)*,)*/` with the hole spelling `/(?:${inner},)*/`, inner := `/(?:(?<h>\d)?;)*/`. The pool is
alphabet `37;,`, length <= 5 (1,365 texts), labels compared.

Counts (all reproduce the critic's figures):

| condition | WHOLE / SEARCHED / FIND-ALL of 1,365 |
|---|---|
| bare `(h: <5)` (control) | 0 / 0 / 0, as §R prints |
| `some((h: <5))` | 6 / 11 / 11 |
| `occurs.none(NOT (h: <5))` | 13 / 353 / 973 |
| `(h[2]: <5)` | 7 / 17 / 17 |

The first `h[2]` text by length is `,3;,`:
- the literal FAILS: its flattened inner passes are only `3`;
- the holes HOLD h = `3`: the second OUTER pass.

The critic's `7;3;,` also differs: the literal HOLDS by reading the second inner pass, and the holes FAIL.

Witnesses, WHOLE:
- `some((h: <5))` on `3;7;,`: the literal HOLDS (reported h = `7`); the holes FAIL. The holes read one outer pass, at
  its outermost view h = `7`.
- `occurs.none(NOT (h: <5))` on `,`: the literal HOLDS (no inner pass at all); the holes FAIL (one outer pass with h
  unset).
- `some` on `3;;,7;,`: the literal HOLDS; the holes FAIL.

Do the two spellings denote one pattern? They should:
- §3.3 / §2.6 l.2327-2328: "The hole `${x}` is one atom with its OWN flags and its OWN group numbering ... a reader who
  splices the text by hand must write `(?:x)`".
- §2.7 l.2601-2602: "a hole is ONE entry (§3.3: `/${x}d/` = `(?:a|b|c)d`)".
- Spliced as `(?:x)`, the hole spelling of NEST is NEST itself, so the engine answers ONE pattern two ways.

Does any subject sentence state whose passes the pass forms range over? NONE does:
- R.1.7 (4) (l.707-711) rules the outermost view for "a bare condition" only.
- NESTED LOOPS (l.755-763) measures literal = holes for the bare condition only.
- The §R.6 rows (l.970 "the PASS TABLE of a loop ... every pass's values"; l.1008 "the PASS FORMS (every pass's values)")
  do not say which loop's passes when two loops enclose the label.
- §R.8 some-own (l.1105) asks only whether each pass's OWN labels are read, and its witnesses are single loops (REP,
  CLOSE).
- My scan of l.450-1247 for "pass table", "innermost", "outer pass", "enclosing loop" and "two loops" finds no other
  sentence.

The engine's cause (critic's reading): the literal keys its pass table on the innermost loop (flattened), and the hole
loop keys it on the outer loop. My numbers are consistent with that; I did not re-read lastpass's `rx_of`.

VERDICT: HOLDS. MODECLOSURE-2's counts reproduce exactly, and RULING-13 is CONFIRMED: no sentence states it. RULING-13's
own example `some((h: <5))` on `3;;,7;,` is one of the moving texts (the literal HOLDS, the holes FAIL). Severity: an
answer moves between two spellings that §3.3's splice rule makes the same pattern.

## V5

Script: verify/w/v5.py, mine. It runs three things:
- the engine;
- the helper-group construction exactly as §R.10 l.1185-1187 describes it: "an empty group `(?<ps>)` at the start of
  each pass ..., a callout reading a label as the pass's own only when its capture starts at or after every helper";
- my own order-based control: the loop unrolled so that only the last pass's copy of the body names h. PCRE2's
  path-exact capture then IS the last pass's own label, with no position test.

Results, `& (h: <5)`, WHOLE:

| case | text | engine | helper | unrolled |
|---|---|---|---|---|
| LOOKBEHIND `/(?:\d\|(?<=(?<h>\d))[a-z])*/` | `3a` | HOLDS, h = `3` | FAILS | HOLDS |
| LOOKAHEAD `/(?:(?=.(?<h>\d))[a-z]\|\d)*/` | `a3` | FAILS | HOLDS | FAILS |
| LOOKAHEAD | `a3a3` | FAILS | HOLDS | FAILS |

- Lookbehind: the last pass `a` SETS h = `3` through its lookbehind, but h's capture starts at 0, before the helper at
  1.
- Lookahead: pass 1 (`a`) sets h = `3` at 1-2; the last pass `3` (starting at 1) sets none.
- Every other text of the two sets agrees. Engine = unrolled on every text I ran (9).

By R.1.7 (2)-(3) (l.702-707: "the value the LAST pass itself set ... a group that took no part in a pass is unset in
it") the answer is about WHEN the group was set. The engine and the unrolled control follow that rule; the helper
construction tests WHERE the text lies and gets both cases wrong.

The text calls the helper construction the per-pass label's regex model with no restriction:
- §R.6 l.999-1000: "Its regex model is the helper-group callout model (PART C2: 16 of 16 equal)";
- §R.10 l.1185-1187;
- G24-3 (l.497), which rests on PART C.

None of C2's pools has a group inside a lookaround inside a loop (the loop patterns I listed in V1), so the check
cannot fail on this class. I did not re-run the critic's 9 / 33 / 33 counts; the witnesses suffice for the claim.

VERDICT: HOLDS (doc/evidence). No printed answer moves; the stated "regex model" is valid only for groups whose text
lies inside their own pass.

## V6

Script: verify/w/v6.py (engine). J := `((h, k): h > k)`, with numerals tested through `num()`.

Engine results:
- Two depths, `/(?:(?<k>\d)(?:(?<h>\d);)*,)*/`: the bare `& J` on `37;,` HOLDS h = `7`, k = `3` in all three modes. On
  `73;,` it FAILS; on `37;,51;,` WHOLE FAILS and SEARCHED gives `37;,`@0.
- Siblings, `/(?:(?<k>\d);)*(?:(?<h>\d),)*/`: the bare `& J` on `3;7,` HOLDS h = `7`, k = `3` in all three modes. On
  `7;3,` and `3;9;7,` it FAILS.
- `& some(J)` and `& occurs.none(NOT J)` raise `ValueError: group question over ('h', 'k')` on every text and mode, in
  both shapes.
- Source: lastpass_model.py l.153-155, `_passes_for`: `if len(lps) != 1: raise ValueError(...)`. It rejects whenever
  the labels' innermost loops differ. A single-loop `some(J)` runs: some-own's CLOSE row is printed. So the rejection is
  the engine's, not a ruled compile error.

What R.1.7 A JOINT says (l.764-767):
- "a bare joint reads the last pass's own tuple";
- "a per-pass joint is written on the item, `/(?:${item})*/` with the joint in the item (every pass), or with `some(J)`
  (some pass)";
- "a bare joint pairs within the last pass".

Two depths: "within the last pass" can be read as the last OUTER pass, which holds k and, at the outermost view (R.1.7
(4)), its last inner pass's h. The engine's HOLDS fits that reading.

Siblings: there is no single "last pass". k's last pass belongs to loop 1 and h's to loop 2. The engine pairs two
different loops' last passes, a tuple no single pass holds. "the last pass's own tuple" and "pairs within the last
pass" do not describe this. The per-label rule (2) (l.702-704) does give each component.

For `some(J)` the text names it as the per-pass spelling without restricting it to one loop. Neither "some pass of
which loop" nor an error is stated anywhere in §R; W4d (l.897) pairs a looped h with a SET-ONCE k only.

VERDICT: HOLDS.
- The engine facts reproduce.
- The text gap is real: siblings' "tuple", and `some(J)` / `occurs.none(NOT J)` across loops, are unstated.
- One nuance: at two depths the bare joint IS covered by "pairs within the last pass", read as the last outer pass.

## V7

Script: verify/w/v7.py, mine. The control is the V1-style helper callout; REP has no lookaround, so it is exact here.
"PCRE2's global loop" is pcre2demo's: after an empty match, retry at the same offset with NOTEMPTY_ATSTART|ANCHORED,
and on failure advance one. Pool: 364 texts (alphabet `37;`, length <= 5). Stretches are compared; the critic compared
labels as well.

| program | step-one vs PCRE2 loop | engine vs PCRE2 loop | engine vs step-one |
|---|---|---|---|
| greedy REP `& (h: <5)` | 0 | 0 | 0 |
| greedy REP `& NOT (h: <5)` | 0 | 0 | 0 |
| lazy `/(?:(?<h>\d)?;)*?/ & (h: <5)` | 0 | 0 | 0 |
| lazy `& NOT (h: <5)` | 301 of 364 | 301 | 0 |

The first lazy NOT text is `;`:
- step-one and the engine give [``@0, ``@1];
- PCRE2's loop gives [``@0, `;`@0, ``@1]. The retry at 0 takes one pass `;`, whose own h is unset, so NOT holds.

The two definitions:
- R.1.2 l.573-576 DEFINES the report: "FIND-ALL: the first surviving path at each start, again from the reported end, an
  empty report stepping one character, as the engine and the libpcre2 harness both do (review r40 C3: PCRE's own
  empty-match retry is not modelled; no answer here depends on it)".
- §R.6 l.991, row "FIND-ALL after an empty match": "PCRE2 retries at the same place, then advances | ... | the language
  follows PCRE2 (regex, the default); the evidence's simplification decides no answer here".

So R.1.2 states step-one as the definition and §R.6 states PCRE2's loop as the language's. They disagree on the lazy NOT
program. "no answer here depends on it" holds for the printed programs I re-ran (greedy REP both ways, lazy positive),
not for FIND-ALL in general.

VERDICT: HOLDS. MODECLOSURE-6's 301 of 364 and its first text `;` reproduce on an independent control, and the two
definitions conflict as stated.

## V8

Script: verify/w/v8.py, mine, on libpcre2 10.46. The pattern is a time `(?<h>HOUR)(?::(?<m>\d\d))?`, then the verb, then
a callout "not late". late = both components are canonical numerals and (h, m) >= (9, 30); predspec242b_model.py
l.221 defines it the same way. FIND-ALL uses the step-one harness.

| hour | verb | `9:30` | `9:30 8:15` | `8:15 9:30 7:00` |
|---|---|---|---|---|
| `\d{1,2}` (the subject's T2V, out l.505-509) | plain | [`9`, `30`] | [`9`, `30`, `8:15`] | [`8:15`, `9`, `30`, `7:00`] |
| `\d{1,2}` | atomic and (*PRUNE) | [`30`@2] | [`30`@2, `8:15`@5] | [`8:15`, `30`, `7:00`] |
| `\d{1,2}` | (*SKIP) | [] | [`8:15`@5] | [`8:15`@0, `7:00`@10] |
| `\d{1,2}` | (*COMMIT) | [] | [] | [`8:15`@0] |
| `\d` | plain | [`9`, `3`, `0`] | [`9`, `3`, `0`, `8:15`] | [`8:15`, `9`, `3`, `0`, `7:00`] |
| `\d` | atomic and (*PRUNE) | [`3`@2, `0`@3] | [`3`, `0`, `8:15`] | [`8:15`, `3`, `0`, `7:00`] |
| `\d` | (*SKIP) and (*COMMIT) | as for `\d{1,2}` | as for `\d{1,2}` | as for `\d{1,2}` |
| `\d+` | every verb | as for `\d{1,2}` | as for `\d{1,2}` | as for `\d{1,2}` |

With `\d{1,2}` every line of R.1.4 l.664-665 reproduces exactly.

Which pattern reproduces which line:
- R.1.4 l.664-665's figures reproduce under the subject's `\d{1,2}` hour, and also under `\d+`.
- The record's PLAIN line (COND-FAMILY l.2521-2522, "plain `9:30` -> `9`, `3`, `0`") reproduces only under a one-digit
  hour `\d`.
- The record's "the atomic group and (*PRUNE) both -> `0`" reproduces under NONE of the three: `\d` gives `3`, `0`, and
  the others give `30`.
- The record's (*SKIP) and (*COMMIT) lines (l.2523-2525) reproduce under all three.

The subject calls its figures "the manager's run in that entry; re-run here" (l.665) without saying that the plain and
atomic/PRUNE figures differ from the record's. The conclusion is unaffected: (*SKIP), not (*PRUNE), gives "returns
nothing" with later matches found.

VERDICT: HOLDS (doc). SIMULATE-4 reproduces exactly.

## V9

### RULING-6

- §7.1's selector rule, l.3792-3795: "the look-alike `@warn.off(/^dead\./)` is NOT the same set: a name set holds whole
  strings, so it is the one name `dead.`". l.3796-3797: "SELECTORS ARE A SET OF NAMES AS AN RX".
- R.2 l.840 and the warning table l.3815-3816 name the warnings `test.never` and `test.always`. No name in §7.1's table
  is `no-fail`.
- R.2 l.845 presents his `@options.strict(/no-fail/)` as "a pattern over warning names (§7.1's selector rule)". Read
  by that rule, `/no-fail/` is the one whole name `no-fail`, so it selects nothing among the draft's names.
- Mitigation: R.2 calls the spelling "a placeholder spelling". The record (COND-FAMILY l.2541-2543) says his example
  "selects a warning named `no-fail`".
- §R.8 has no warning-names row: R.2 says "names not ruled" (l.841).

VERDICT: HOLDS (design/doc).

### RULING-12

- §2.6 l.2412-2416 keeps, under the mark "[REV 24.2: the RULE in substance ... where this paragraph and R.1.7 differ,
  R.1.7 wins]", this example: "`(m: occurrences(/(?<g>a)?b/) & (g: "a"))` on `abb` REJECTS (hit 2's g is unset,
  `label.unset`)".
- Under rev 24.2 (R.1.7 EXPORTED LABELS l.752-754; R.1.9 the last hit's own) the path with hits [`ab`, `b`] fails, and
  PCRE backs off to hits [`ab`] with `b` as gap. That path HOLDS g = `a`.
- I checked this two ways (verify/w/v9.py):
  - the engine: `occurrences(/(?<g>a)?b/)` (min 0 and min 1) `& (g: "a")` on `abb`: WHOLE HOLDS g = `a`; SEARCHED
    `abb`@0; FIND-ALL [`abb`@0];
  - libpcre2 10.46, the one-pattern model `(?:[\s\S]*?(?<ps>)(?<g>a)?b)*[\s\S]*` with an own-g callout: WHOLE matches
    (0,3) with the last hit's ps = (0,0) and g = `a`.
- This is R.1.7 l.753-754's own shape (`occurrences(/(?<x>(?<g>a)?b)/, min = 1) & (g: "a")` on `abb` HOLDS x = `ab`).
- So the kept example's "REJECTS" contradicts §R, and the mark calls the paragraph the rule without flagging it. The
  mark's "R.1.7 wins" makes the answer recoverable.

VERDICT: HOLDS (an answer in a kept example).

### RULING-2

- The record's MINE (COND-FAMILY l.2403-2405, "MINE, to be worked out by lane predspec241 ...: where a label takes its
  value from the capture (the end of each pass)") says "the end of each pass". The subject never mentions that
  parenthetical: a grep for "end of each pass" finds nothing.
- after-loop-read RECORD (1) (COND-FAMILY l.2461-2462): "a condition written INSIDE a loop, on the item, is judged in
  every pass: that is how "all" is written". HIS WORDS on `late := time & ((h, m): >= (9, 30))`, `/(?:${late},)*/`
  (l.2454-2456): "Then the rx is "a loop of (times after 9:30)"".
- §R.8 value-point (l.1102) states the cost of "pass end" itself: "an item condition could read no label of its own pass
  (every §R.4 item spelling FAILS)". Its witness `/(?:${item})+/` FAILS on `3;` under pass end.
- Under pass end, `late`'s condition (before the pass's `,`) reads an unset h and m and fails in every pass. The program
  would then match only the empty loop, not "a loop of (times after 9:30)".

So "pass end" contradicts the meaning he accepted for the RECORD (1) example, and "group close" is the one consistent
candidate. No ruling names value-point explicitly, so "excluded" is by entailment from his accepted example, not by a
sentence. The draft's row says "Touches nothing ruled" (l.1102), which is wrong for that reason.

VERDICT: HOLDS. Pass end is excluded by entailment from RECORD (1)'s accepted example, not by an explicit ruling. The
"(the end of each pass)" MINE goes unmentioned.

### RULING-11

grep `REV 24.2` / "rev 24.2" after §R (l.1247) finds these marks:

| line | where | in §R.9's list? |
|---|---|---|
| 1250 | the §0 status line | no |
| 2412 | §2.6 | yes |
| 2932 | §4.2 | yes |
| 3059 | §4.3 THE PAIRING RULE | yes |
| 3386 | §5.2 "[REV 24.2: a WARNING, `test.never`, ...]" | no |
| 3810, 3815-3816 | §7.1 "THE WARNING TABLE (rev 24.2, rulings R6 ...)" | no |

- §R.9 l.1172-1173 lists rev 24.2's marks as "§2.6 ...; §4.2 ...; §4.3 THE PAIRING RULE".
- R.11 row 40 (l.1244) itself cites "§R.2, §5.2, §7.1".
- §7.1's is a "(rev 24.2 ...)" label rather than a bracketed "[REV 24.2]" mark, so its omission is arguable. §5.2's is a
  true bracketed mark and is missing.

VERDICT: HOLDS (doc).

## V10

The printed line:
- 738 is NOT printed in predspec242b_model.out. It is predspec241_model.out l.557: "Q zero-place   THE LAW's twin
  `occurrences(/\d+/ & /1\d*/, min = 1)` (the reference: `&` on the hit's stretch) vs `0` = PCRE's group 0 (the
  program's match start to here): WHOLE 738 (first ` 1`: HOLDS #hits=[1] vs FAILS); SEARCHED 738 ...; FIND-ALL 738 ...
  of 1365 (labels compared)".
- predspec242b_model.out l.502 prints only the innermost candidate, rev 24.1 vs NOW, 0 / 0 / 0, UNCHANGED.

What it compares (predspec241_model.py l.1124-1135):
- The reference `OCC(AND(\d+, 1\d*), 1)` against `OccG0`, an `OccS` whose hit is admitted only when `/1\d*/` matches
  WHOLE on the text from the PROGRAM's match start to the hit's end.
- Pool DSP = `strings("129 ", 5)` (l.373), 1,365 texts, all three modes.
- The key (`candf`/`labkey`, l.815-827) is the WHOLE holds / SEARCHED stretch / FIND-ALL stretches, plus the label
  `#hits` (the hit list). So "labels compared" there means "hit lists compared", as R.1.4 l.635 says.

Re-run: verify/w/v10.py (output v10.out). It uses the same engine as V1 and my own copy of `OccG0` and `labkey` as
defined at l.1125-1130 and l.815. Rules 24.2 and 24 give identical figures.

| metric | WHOLE / SEARCHED / FIND-ALL of 1,365 (first ` 1`) |
|---|---|
| holds/stretch + hit lists | 738 / 738 / 738 |
| holds/stretch WITHOUT hit lists | 660 / 660 / 660 |
| holds only | 660 / 0 / 0 |

The innermost candidate vs the reference is 0 under every metric.

So 660 is the same comparison on the same pool, with the hit lists left out of the key. On 78 texts the two candidates
report the same holds and stretch but different hit lists. predspec241_model.out l.558's libpcre2 control of the
group-0 candidate is also "holding and stretch" (0 / 0 / 0). That is the 660 metric, so the 738 figure has no libpcre2
control on its hit-list part.

VERDICT: HOLDS for R.1.4's printed 738 (it reproduces under "hit lists compared"). 660 vs 738 is a METRIC difference
(hit lists in or out of the key), not a changed answer. A doc nit: R.1.4 cites the figure with no PART/tag, and it lives
only in predspec241_model.out, not in the rev 24.2 answer file predspec242b_model.out (I did not check whether §R's
preamble promises otherwise).

VERIFY COMPLETE

