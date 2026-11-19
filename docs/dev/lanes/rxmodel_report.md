# Lane rxmodel — a regex model for each open predicate choice, run on libpcre2 (2026-11-17)

DESIGN EVIDENCE ONLY. Nothing here rules; `docs/design/predicates_draft.md` is not edited. "The model equals
candidate X" is a finding about what PCRE2 does, not a choice. Every number is printed by
`rxmodel_evidence/rxmodel.py` (output `rxmodel_evidence/rxmodel.out`); tags like `[b3]` name its lines.

## STATE AT HANDOFF

- OWED: none
- Rulings file `rxmodel_rulings.md`: last entry applied R4 (R1/R2: the owner's own model of `occurrences`, the lazy
  gap `(?:.*?(rx))*.*`, run in EACH CHOICE f; R3/R4: WHERE NO REGEX MODEL EXISTS is written as noted exceptions with
  the regex default, the value an explicit request would ask for, and whether the tests on it are regular).
- Premise test: PASS. (1) `pathimpact_model.py` re-ran byte-identical to its committed `.out` (about 2 minutes).
  (2) libpcre2-8 10.46 reached through `rxmodel_evidence/pcre2h.py`; `(?:(?<g1>\d\d)|(?<g2>\d)\d)(?C)` on `25` with
  the callout failing when g1 = 25 reports g2 = 2, the second branch [P1]. The harness's option values and the
  callout-as-condition form are checked by behaviour [P0].
- Validation: 141 comparisons; 62 are exact (0 texts differ in every mode). `RXMODEL_SABOTAGE=1` (every callout
  answers the opposite way) leaves 14 exact: 13 are callout-free pure-regex models (immune by construction; their
  control is the engine, an independent implementation) and one coincidence ([i4] vs Kleene OR; its twin comparison
  breaks); 158 output lines move.

## THE METHOD

- THE BASE MODEL (the owner 2026-11-13; the manager's note there): a condition is a PCRE2 CALLOUT `(?C"name")` placed
  where the condition is written, returning "fail here" when its test is not TRUE (FALSE or an absent label), so PCRE
  backtracks to its next choice. It reproduces the branch-scope ruling exactly: `(B | A) & (l: <20)` as
  `(?|(?<l>\d\d)|(?<l>\d)\d)(?C"l<20")` HOLDS `25` with l = 2, find-all on `25 13` [`25`, `13`]; L60 HOLDS `aa`;
  `P & (a: "1")` HOLDS `123` with a = 1, b = 23; each 0 texts differ from pathimpact's rule engine over its sets [B1-B3].
- Where a choice needs more, the model uses PCRE2's own constructs: conditional groups `(?(<g>)yes|no)`, a callout
  as a condition (written inside a lookahead, `(?(?=(?C"t"))yes|no)`; written bare it backtracks instead of taking
  `no` [P0]), negative lookahead, atomic groups, possessive repeats, verbs, and PCRE2 10.45's NON-ATOMIC lookahead
  `(*napla:...)`. TWO PATTERNS ON ONE STRETCH (the predicate `&` and `!`) has no plain-regex construct; the model
  ties them with `(*napla:X(?<T>[\s\S]*+))` (X's paths, backtrackable, with the rest of the text captured) and
  `\k<T>\z` at the other side's end, which holds only at X's end. A callout may read the subject (two models do:
  `when`'s pass test reads its stretch's passes, route (ii) reads the whole subject; both stated where used).
- Each model is run on a WHOLE value (`PCRE2_ANCHORED|PCRE2_ENDANCHORED`), a SEARCHED text and a FIND-ALL text (the
  engines' loop: again from the end, an empty match steps one), and compared with pathimpact's engine running each
  candidate on the same lines and on a text set: DIG4-type sets {1, 2, 9, space} to length 5 (1,365), {3, 7, ;} (364),
  time texts {9, 0, 5, :, space} to length 5 (3,906), KH texts (1,110), {1, 2, space, x} to length 4 (341).
  Compile options NO_AUTO_POSSESS and NO_START_OPTIMIZE keep every path visible to callouts [P0]. Python `re` is not
  used for any model; PCRE2 is RUN, never read (D181).
- Standing questions: measurement regime NOT RELEVANT (no timing). Independent control RELEVANT: every model is
  checked against pathimpact's engine (a separate implementation, a path enumerator over Python's parse) and the
  sabotage switch shows the comparisons can fail. Data regeneration NOT RELEVANT (no table or pin).

## ONE TABLE

| choice (slug) | regex model in a few words | the candidate it supports | faithful? | contradicts a ruling? |
|---|---|---|---|---|
| the rule itself (branch-scope) | a callout after the pattern; PCRE backtracks on "fail here" | the ruled reading (ii) | exact | no; it is the ruling |
| unknown-backtracks | a test on an unset group (callout, conditional group, or backreference) simply fails | U1: rejects and backtracks like FALSE (U2 needs an explicit `(*PRUNE)(*FAIL)`) | exact | no |
| condition-not | NOT = a negative lookahead around the test | two-valued NOT: an absent label PASSES the NOT | exact | YES: "absence never matches, negated or not" (11-16); the ruled meaning needs an explicit guard in regex |
| loop-condition | inside the loop body: judged each pass; after the loop: only the last pass's value | a condition written after the loop = the LAST pass (neither L1 nor L2); written in the body = L2 | exact | tension: the all-question ruling was shown "the plain condition fails on the empty list" (every pass) |
| pass-table | every pass tested in the body, plus "at least one pass" | the draft's pass table (Kleene AND) has an exact regex spelling, but not where the condition is written | exact | no |
| pass-and | both candidates spelled with a flag group; regex's own NOT after the loop reads the last pass | neither; regex does not decide | exact per candidate | no |
| complement-paths | negative lookahead tied to the same stretch | C1: no surviving path of B at all (C2 needs an atomic group inside) | exact (needs the non-atomic lookahead) | no |
| complement-place | a lone `!q` in a whole value = "not q, whole" | legal in a whole-value place; a searched lone `!q` has no model | exact / none | no |
| nested-complement | a lookahead inside the stretch holding the tied complement | C1 (by composition; not run on its own) | close | no |
| lookahead-reentry | PCRE's lookahead is atomic; PCRE2 also offers a non-atomic one | LA1 by default; LA2 only as an explicit opt-in | exact | no |
| negative lookahead with a condition | the negative lookahead tries every inner path | NA1 (NA2 needs an atomic group inside) | exact | no |
| lookahead-labels | PCRE keeps a positive lookahead's captures | the draft's reading (its first surviving path's labels) | exact | no |
| hits-reentry | a global search commits each hit; ONE regex (the owner's lazy-gap model) re-enters | H1 if `occurrences` is a search, H2 if it is one pattern; the first path of the owner's model has exactly the search's hits | exact | no |
| hit-list | the condition inside the searched pattern, then find-all | the draft's hit list (own rows, leftmost, non-overlapping) | exact | no |
| join-order | regex has no `&`; the side put in a non-atomic lookahead is the outer one | neither; the usual idiom `(?=X)Y` reads left-outer but is atomic (a third answer) | close | no |
| `A & B` vs `A & (0: B)` | B consumed in the subject reads the text around it; `(0: B)` is a second match on the stretch alone | regex's `&` is IN CONTEXT; `(0: B)` is the SPAN meaning | exact | YES: the 11-15 ruling (string sets; `^`/`$` = the span's ends) is the SPAN meaning, which regex's in-context `&` is not |
| record-under-not | NOT around the record's tests or the joint test | two-valued: equal to none of the three candidates | exact | YES, the same root as condition-not |
| group-truth | "some pass" as a flag group | two-valued EXISTS (today's reading) | exact | no |
| condition-or | NOT around an alternation of tests | two-valued OR (rev 22), not Kleene OR | exact | YES, the same root as condition-not |
| when-meaning | PCRE's conditional group: if c then p | the FILTER form (the body is a plain alternation, also exact) | exact | no |
| repeated-means | a group inside a repeat is repeated, by syntax alone | the manager's ruling (the operand regex decides) | trivial | no |
| whole-text | route (i) = a negative lookahead; route (ii) = a gate over the whole subject | both modelled; route (ii) in find-all has no plain-regex spelling (no unbounded lookbehind) | exact / callout only | no |
| polarity-rule | none (regex has no compile-time polarity rule) | none | none | no |
| atomic (E7) | PCRE's atomic group | the labelled extra, on every line and set | exact | no |

## EACH CHOICE

### a. unknown-backtracks (E6): a test on an absent label

- The choice: when a condition reads a label the path did not set (UNKNOWN), does the pattern backtrack to its next
  path (U1) or stop trying at that start (U2)?
- Line: `/(?<b>\d+)(?<a>\d)?/ & (a: <5)`; first path b = 12, a absent.
- Models: [a1] callout `(?<b>\d+)(?<a>\d)?(?C"a<5")` (absent = fail here); [a2] pure regex
  `(?<b>\d+)(?<a>\d)?(?(<a>)(?<=[0-4])|(*FAIL))`; [a3] a BACKREFERENCE to the unset group, `(a: = z)` as
  `(?<b>\d+)(?<a>\d)?;(?=\k<a>)(?<z>\d)`.
- PCRE2: WHOLE `12` HOLDS a = 2, b = 1; SEARCHED `12`@0; find-all on `12 1 19 3` [`12`]. [a3] on `12;2` HOLDS a = 2.
- Equals U1: 0 differ in every mode over 1,365 texts (a1, a2), 0 over 364 (a3). Against U2: 240 WHOLE / 1,038
  SEARCHED / 1,038 FIND-ALL (first `11`). U2 is reachable only by writing a verb: `(?(<a>)...|(*PRUNE)(*FAIL))` [a4]
  equals U2 (0 / 0 / 0).
- Faithful: exact. Claim CONFIRMED: an unset-group test fails like any piece; PCRE2's default for a backreference to
  an unset group is to fail (with the option MATCH_UNSET_BACKREF it matches empty instead [b5]).

### b. condition-not: NOT on a test of an absent label

- The choice (ruled 2026-11-16 23:48): NOT is the where-clause's three-valued NOT; "absence never matches, negated or
  not".
- Line: `/(?<b>\d+)(?<a>\d)?/ & NOT (a: <5)` on `1` (a absent); find-all `1 12 19 3`.
- Models: [b1] `(?<b>\d+)(?<a>\d)?(?!(?C"a<5"))`; [b2] `(?!(?(<a>)(?<=[0-4])|(*FAIL)))`; [b4] a negative lookahead
  around a backreference to the unset group, `(?<b>\d+)(?<a>\d)?;(?!\k<a>)(?<z>\d)`.
- PCRE2: [b1] WHOLE `1` HOLDS (a absent); find-all [`1`, `12`, `19`, `3`], every one with a absent. [b4] on `1;2`
  HOLDS: the backreference to the unset a fails, so its negative lookahead SUCCEEDS.
- Equals the two-valued NOT ("not TRUE"): 0 / 0 / 0 of 1,365 (b1, b2), 0 of 364 (b4). Against the RULED three-valued
  NOT: 243 WHOLE / 1,359 SEARCHED / 1,359 FIND-ALL (first `1`); b4 16 / 128 / 128.
- The ruled meaning IS writable in regex, with an explicit guard: `(?(<a>)(?!(?<=[0-4]))|(*FAIL))` [b3] equals it
  (0 / 0 / 0). With the option MATCH_UNSET_BACKREF the backreference form flips: `(?!\k<a>)` fails on an absent a,
  but then the POSITIVE test `(?=\k<a>)` succeeds on it [b5] (absence matches positively).
- Faithful: exact. CONTRADICTS the ruling (claim CONFIRMED): the natural regex NOT is two-valued. See WHERE REGEX
  CONTRADICTS A RULING.

### c. loop-condition (E2), pass-table, pass-and

- The choice: a condition on a label set inside a loop: judged after the loop over all passes (L1, the draft's pass
  table, Kleene AND), or a piece inside each pass (L2)?
- Lines: `/(?:(?<h>\d);)*/ & (h: <5)` and `/(?:(?<h>\d)?;)*/ & (h: <5)` on `7;3;`, find-all `3;;7;;3;`.
- Models, by WHERE the callout is written:
  - [c1] in the body right after h's group, `(?:(?<h>\d)(?C"h<5");)*`: equals L2 (0 / 0 / 0 of 364, both loops).
    `7;3;` FAILS whole; SEARCHED reports the empty match at 0.
  - [c2] after the loop, `(?:(?<h>\d);)*(?C"h<5")`: reads only the LAST pass (PCRE keeps the last iteration's
    capture; a pass that does not set h keeps the earlier value): `7;3;` HOLDS h = 3. Equals pathimpact's "no pass
    table: PCRE's last capture" candidate (0 / 0 / 0); against L1 1 / 7 / 7 and 16 / 54 / 54; against L2 2 / 324 / 364 and 10 / 306 / 364.
  - [c3] the draft's pass table as regex: every pass tested in the body, a pass lacking h fails, at least one pass:
    `(?:(?<h>\d)(?C"h<5");)*(?(<h>)|(*FAIL))` and `(?:(?<h>\d)(?C"h<5");)+`: equal L1 (0 / 0 / 0, both loops).
- pass-and, `NOT (h: <5)` on `/(?:(?<h>\d)?;)*/`, line `7;;`: regex's own NOT after the loop [c4] reads the last
  pass, two-valued, and equals neither candidate (10 / 306 / 364 vs Kleene AND; 22 / 339 / 364 vs the alternative).
  Each candidate has an exact spelling with a flag group: Kleene AND [c5]
  `(?:(?:(?<h>\d)(?(?=(?C"h<5"))|(?<bad>)))?;)*(?(<bad>)|(*FAIL))` (0 / 0 / 0); "a pass lacking h makes it UNKNOWN"
  [c6] the same with the optional removed (0 / 0 / 0); they differ 18 / 50 / 50 (first `7;;`).
- Faithful: exact for every candidate. Claim PARTLY REFUTED: "all passes" HAS a regex model (in the body plus a
  guard; equal to L1 on every text), but it is not where the predicate writes the condition; the regex model of
  the condition AS WRITTEN (after the loop) is the last pass only. Regex does not choose between L1 and L2 or between
  the pass-and candidates; it says a condition after a loop sees one value. See WHERE NO REGEX MODEL EXISTS (1).

### d. complement-paths (E3), complement-place, nested-complement, polarity-rule

- The choice: `!B` keeps a stretch when B has NO surviving path over it (C1) or when B's one parse is rejected (C2).
- Line: `P & !(P & (a: "1"))`, P = `/(?<a>\d+)(?<b>\d+)/`, on `123`; find-all `123 9 113`.
- Model [d1]: `(*napla:(?<a>\d+)(?<b>\d+)(?<T>[\s\S]*+))(?!(?<a2>\d+)(?<b2>\d+)(?C"a2=1")\k<T>\z)` then consume to
  the end. PCRE2: WHOLE `123` FAILS; SEARCHED `23`@1; find-all [`23`]. Equals C1: 0 / 0 / 0 of 1,365; against C2
  117 / 270 / 270 (first `111`). C2 is writable only with an atomic group around B's first parse [d2] (0 / 0 / 0).
- The tie matters: the untied `(?!B)` asks "no B from this start, any end" [d3]; it equals C1 on this program by
  coincidence, but on `/\d+/ & !/1/` the tied model equals the engine (0) [d5] and the untied `(?!1)\d+` differs
  120 / 357 / 417 (first `11`) [d6].
- complement-place: a lone `!q` in a WHOLE place ("the value is not a late time") = `(?!q\z)[\s\S]*` [d4]: `9:30`
  FAILS, `9` HOLDS, `10:45` FAILS; 0 of 3,906 differ from "not a whole q". A SEARCHED lone `!q` has no model (no
  pattern gives the stretch or its preference). nested-complement: `contains(t2 & !q)` is a lookahead bounded to the
  stretch holding [d1]'s tied complement, so C1; not run on its own (pathimpact found C1 and C2 equal there).
  polarity-rule: no model (below).
- Faithful: exact (with PCRE2 10.45's non-atomic lookahead). Claim CONFIRMED with the tie made explicit.

### e. lookahead-reentry (E4, E4'), lookahead-labels

- The choice: does a condition outside a positive lookahead re-enter it (LA2) or not (LA1)? Does a condition inside a
  negative lookahead backtrack inside (NA1) or judge the first inner path (NA2)?
- Lines: `/(?=(?<x>\d+))\d/ & (x: "1")` on `12`, find-all `112 12 1`; `/(?![\s\S]*${q})${t2}/` on `9:15 10:45`.
- [e1] `(?=(?<x>\d+))\d(?C"x=1")`: SEARCHED `12` FAILS; find-all [`1`@7]; equals LA1 (0 / 0 / 0 of 1,365); against
  LA2 0 / 660 / 693. [e2] the same with `(*napla:...)`: `1`@0; equals LA2 (0 / 0 / 0). PCRE2 offers both; the plain
  lookahead is LA1.
- [e3] `(?![\s\S]*?T2'(?C"late2"))T2`: SEARCHED `0:45`@6; equals NA1 (0 / 0 / 0 of 3,906); against NA2 6 / 6 / 6
  (first `09:50`). NA2 needs an atomic group around the inner path [e4] (0 / 0 / 0).
- lookahead-labels [e5]: `(?=[\s\S]*?\d\d:(?<lm>\d\d)(?C"lm>=30"))T2(?C"lm=50")` on `9:15 10:45 11:50`: `0:45`@6 with
  lm = 50 (the outer row carries the lookahead's capture), equal to LA1 on the lines and over 3,906 texts; with
  `(*napla:)` [e6] `9:15`@0, equal to LA2. (That text set does not separate LA1 and LA2: both 0; the lines do.)
- Faithful: exact. Claims CONFIRMED (LA1 atomic; NA1).

### f. hits-reentry (E5), hit-list, and the owner's model of occurrences (rulings R1, R2)

- The choice: `occurrences(/\d+/)` with `(hit: <100)`: are the hits fixed and then judged (H1), or does the
  condition re-enter the body (H2)?
- GLOBAL SEARCH (each hit committed before the next search): [f1] `\A(?:\D*+(?<hit>\d++)(?C"hit<100"))++\D*+\z`
  (possessive: hits committed) equals H1 (0 of 341 WHOLE); [f3] two steps, PCRE2's find-all of `\d+` then every hit
  judged, equals H1 (0). `1234`, `x300 12`, `5 123` all FAIL.
- ONE REGEX, the owner's model (R1, R2: the LAZY gap is his), `(?:.*?(rx))*.*` with `.` matching everything:
  - no condition [fR1]: the reported path's hits are exactly the global search's hits (0 of 341 differ): `12 34`
    [12, 34], `1234` [1234], `x300 12` [300, 12].
  - comparison line, greedy gap [fR2]: the first pass takes the rightmost shortest hit: `12 34` [4]; differs from the
    global search on 212 of 341 (first `11`: [1] vs [11]).
  - `(hit: <100)` written INSIDE the body after the hit group [fR4, with `{1,}`]: equals H2 (0 of 341); `1234` HOLDS
    with hits [12, 34], `x300 12` [30, 0, 12]: the condition re-enters and re-splits. With `*` (zero passes allowed)
    [fR3] `x` holds too (H2 rejects zero hits): 31 differ from H2.
  - `(hit: <100)` written AFTER the loop [fR5]: reads only the last pass's capture; equal to H2 on holds (0: a
    re-entered body can always hide a large hit in a gap), but the hit lists show it: `1234` [123, 4].
  - `min = 2` as `{2,}` [fR6]: `1234` HOLDS (the loop splits one number into two hits); against the global search's
    count >= 2: 124 of 341 differ (first `11`).
  - empty hits, rx = `\d*` [fR7]: the loop ends on an empty pass (`1 2` gives [1, '']); a global search steps on
    (`1 2` gives [1, '', 2, '']).
- The owner's "not global, correct?": correct. One regex re-enters (H2) and re-splits; only its FIRST path's hits
  equal the global search's. 56 of 341 texts differ between H1 and H2.
- hit-list [f4]: the callout inside the searched pattern, then find-all, `(?<n>\d+)(?C"n<100")`: on `1234` [`12`,
  `34`]; equals the draft's hit list (R.1.9) 0 / 0 / 0 of 1,365.
- Faithful: exact both ways. Claim CONFIRMED; the model supports H1 if `occurrences` is a search over the place,
  H2 if it is one pattern (the owner's model).

### g. join-order (E1) and the same-stretch `&`

- The choice: in `X & Y`, whose paths are outer (which labels the reported row carries)?
- Line: `(P & Q) & ((a: "1") | (c: "1"))`, Q = `/(?<c>\d+)(?<d>\d+)/`, on `123`.
- Regex has no `&`. With the tie, the side in the non-atomic lookahead is outer: [g1] P in `(*napla:)` reports
  a = 12, c = 1, equal to left-outer (0 / 0 / 0 of 1,365); [g2] Q in it reports a = 1, c = 12, equal to right-outer
  (0); the two differ 0 / 414 / 414. The usual idiom `(?=X)Y` writes the left operand first in an ORDINARY (atomic)
  lookahead [g3, g4]: it equals left-outer on this line, but with `(a: "1")` alone it FAILS `123` (P keeps only its
  first parse, a = 12), 117 / 414 / 414 against either order: a third reading (left side atomic).
- Faithful: close. No plain-regex spelling of same-stretch `&` exists without PCRE2 10.45's non-atomic lookahead;
  regex does not choose the order. Claim CONFIRMED (no deciding model).

### h. `A & B` against `A & (0: B)`: does B, as a filter, see the text around the stretch?

- [h1-h4] regex's `&`: `(*napla:\d+(?<T>[\s\S]*+))B(?=\k<T>\z)`: B is matched inside the subject, so `^`, `$`, `\b`
  and lookarounds read the text around the stretch. It equals pathimpact's IN-CONTEXT `&` (0 / 0 / 0 for `^\d+`,
  `\b\d+`, `\d+$`, `(?<= )\d+`).
- [h1z-h4z] `(0: B)`: a callout that matches B WHOLE against the stretch alone; equals the SPAN `&` and pathimpact's
  `& (0: B)` (0 / 0 / 0 each).
- They part on `^`, `$` and lookbehind: `/\d+/ & /^\d+/` on ` 1`: regex FAILS, `(0: B)` `1`@1 (336 SEARCHED / 822
  FIND-ALL of 1,365); `$` and `(?<= )` 822 / 822. (`\b\d+` happens to agree on this set.)
- Faithful: exact. The owner's 2026-11-15 ruling ("consider 'a' to instead be the set of strings again", `^`/`$` the
  ends of the filtered span, contextual assertions like `\b` disallowed in a filter) is the SPAN meaning = `(0: B)`.
  Regex's own spelling of `&` is the in-context meaning that ruling reversed. See WHERE REGEX CONTRADICTS A RULING.

### i. the other open slugs

- record-under-not [i1, i2]: NOT around the record `(?!(?C"h<9")(?C"m<30"))` or around the joint test: both two-valued
  and identical. On `10` they HOLD (equal to completion and to the record), but over 3,906 time texts they equal none
  of the three candidates: first `0` (h = 0, m absent) HOLDS, where the record (Kleene) and completion FAIL (918
  SEARCHED) and today's joint FAILS (3,546). Faithful: exact. Contradicts the absence ruling (same root as b).
- group-truth [i3]: "some pass has h < 5" as a flag group `(?(?=(?C"h<5"))(?<hit>)|)` set inside the pass, `NOT some`
  as `(?(<hit>)(*FAIL)|)`: equals two-valued EXISTS (today) 0 / 0 / 0 of 364; three-valued `some` differs 17 / 135 /
  245. A three-valued `some` would need a second flag for "a pass lacked h". Supports EXISTS. Faithful: exact.
- condition-or [i4]: `(?!(?C"h<5")|(?C"k<5"))` on `b7` HOLDS: equals the two-valued OR (rev 22) 0 / 0 / 0 of 156;
  against the told Kleene OR 3 / 89 / 89. Contradicts the absence ruling (same root as b).
- when-meaning [i5, i6]: PCRE's CONDITIONAL GROUP is "if c then p": `(?<k>\d)(?:;(?<h>\d))*(?(?=(?C"c"))(?C"p")|)`
  equals the FILTER form `x & when(c, p)` 0 / 0 / 0 of 1,110 (on `3;0;5 5;1;9` [`3;0;5`, `5;1;9`]); the library body
  as a regex alternation (its complement tied) equals the body 0 / 0 / 0 ([`3;0`, `5`, `5;1`, `9`]); the two differ
  0 / 125 / 125. Supports the filter form as the natural construct; both are exact. (The `c` callout reads its
  stretch's passes, as pathimpact's engine does.)
- repeated-means [i7, i8]: PCRE has no notion of "repeated" beyond syntax (a group inside a repeat keeps its last
  value); both spellings answer alike on `3;`, `7;3;`, `3;7;3;`. Supports the manager's ruling trivially.
- whole-text: route (i) is the negative lookahead of e (NA1, exact). Route (ii) `t2 & text.none(q)` is exact as a
  callout reading the whole subject [i9] (0 / 0 / 0 of 3,906; against today's `t2 & !q` 6 / 90 / 90). In plain
  regex only the start gate `\A(?![\s\S]*q)` + `\K` [i10] exists: SEARCHED exact (0), but `\A` stops find-all after
  one match, and "no q behind this start" cannot be written: PCRE2 refuses an unbounded lookbehind [i11] ("length of
  lookbehind assertion is not limited").
- pass-table, pass-and: under c. polarity-rule, complement-place, nested-complement: under d and below.

### j. E7 atomic

- PCRE's atomic group equals pathimpact's labelled extra on all its lines and sets (0 / 0 / 0 each): [j1] `t2 & q` on
  `9:30` HOLDS `9:30`; [j2] `t2 & !q` (item 14) on `9:30` reports `30`@2; [j3] `(B | A) & (l: <20)` on `25` FAILS,
  find-all on `25 13` [`13`] (item 19's hand answer); [j4] `P & (a: "1")` on `123` FAILS; [j5] with the condition
  INSIDE the atomic group, `(?>(?<a>\d+)(?<b>\d+)(?C"a=1"))`, `123` HOLDS a = 1: the group backtracks inside before
  committing. So "atomic = take the first row before filtering" holds for conditions outside the atomic group only
  (as pathimpact P8 (b) found). Faithful: exact.

## WHERE REGEX CONTRADICTS A RULING

1. condition-not (2026-11-16 23:48, his words "condition-not : yes allow not", the record: "a condition on an absent
   label is unknown, its NOT is unknown, the row is dropped (absence never matches, negated or not)"). Regex's NOT is
   a negative lookahead; around a test of an unset group (callout, conditional, backreference) it SUCCEEDS: `/(?<b>\d+)
   (?<a>\d)?/ & NOT (a: <5)` HOLDS on `1`; differs from the ruling on 243 WHOLE / 1,359 SEARCHED of 1,365 [b1, b2,
   b4]. Regex can say the ruled thing only with an explicit guard, `(?(<a>)(?!test)|(*FAIL))` [b3]. The same root
   decides record-under-not [i1, i2] and condition-or [i4]: regex makes both two-valued (condition-or then equals
   rev 22's two-valued OR; record-under-not equals none of the three candidates). THE QUESTION for the owner:
   regex says an absent label passes a NOT; the ruled sentence says it never matches. Which wins?
2. `&` and the text around the stretch (2026-11-15, his words: "it was decided to drop this interpretation and
   consider 'a' to instead be the set of strings again ... the rulling was to say again that ^...$ meant the start and
   end of the filtered condition and to disallow certain contextual rx like \b in a filter rx"). Regex can put two
   patterns on one stretch only by matching both in the subject, which is the in-context meaning that ruling
   reversed: `/\d+/ & /^\d+/` on ` 1` FAILS in regex, `1`@1 under the ruling [h1, h1z]. The ruled meaning equals
   `A & (0: B)` exactly. THE QUESTION: none needed if the ruling stands; it is recorded that regex here is the
   reversed alternative.
3. A tension, not a contradiction of his words: the all-question ruling (2026-11-16 23:18, "all-question: retire")
   was shown "the plain condition fails on the empty list", i.e. a plain condition on a looped label means every
   pass. Regex's model of a condition written after the loop reads the LAST pass only [c2] (`7;3;` HOLDS h = 3).

## WHERE NO REGEX MODEL EXISTS

Each is a NOTED EXCEPTION the language keeps (R3); never a reason to remove the feature. For each (R4): what regex
alone gives (the default if regex behaviour ruled), the value an explicit request would ask for (no spelling;
`all_matches(rx)` is the owner's placeholder), whether the tests on it are regular, and the question regex cannot
answer, with its candidates run.

1. EVERY PASS OF A LOOP, judged where the condition is written (after the loop): pass-table, pass-and, group-truth.
   - Gives: a condition over all of a label's values in the loop. Regex alone: the LAST pass's value [c2].
   - Default under regex behaviour: `(h: <5)` after the loop reads the last pass; an explicit request would ask for
     "the list of h's values, one per pass, in order".
   - Regular? `all`, `some`, `count >= N` / `= N` for a constant N, `occurs.*`, with a regular test on each value, are
     regular: written in the body they are a product (each pass restricted [c3]), a flag [i3, c5], or a counter up to
     N. Reading one pass's VALUE out, or comparing values across passes (sorted, all distinct, a sum), needs stored
     values: the captures level, as the 2026-11-15 ruling (1) already put "reading ONE hit" (CF:972-980).
   - The question regex cannot answer: how a condition on the list interacts with backtracking. Candidates run: L1
     (judged after the loop) vs L2 (a piece in each pass): differ 1 / 324 / 364 (`/(?:(?<h>\d);)*/`) and 18 / 338 /
     364 (`(?<h>\d)?`), only on zero passes and empty passes; pass-and's two candidates differ 18 / 50 / 50.
2. ALL HITS OF A SEARCH: hits-reentry, hit-list.
   - Gives: the list of every hit of a search inside the place. Regex alone: one search yields one match; the owner's
     one-regex model yields the last pass's capture [fR5].
   - Default under regex behaviour: one match; an explicit request would ask for "every hit of a global search,
     leftmost, non-overlapping, in order".
   - Regular? `all` / `some` / `count` over the hits of `\d+` is regular for this witness ([f1], the possessive form,
     equals H1 on 341 texts); for an arbitrary rx it needs PCRE's leftmost-first segmentation, which is UNPROVEN here
     beyond the witness. Reading a hit's value needs captures (CF:972-980, ruling (1)).
   - The question: committed hits (H1) or a re-entered body (H2): 56 of 341 differ; `min = 2` as a loop count
     re-splits `1234` (124 of 341 differ from the search's count) [fR6].
3. A WHOLE-SUBJECT GATE IN FIND-ALL (whole-text route (ii)).
   - Gives: "the subject contains no q" applied to every hit. Regex alone: route (i)'s positional "no q from here on"
     [e3], or the `\A` gate, which reports one match only [i10]; PCRE2 refuses the unbounded lookbehind that would
     say "no q behind here" [i11].
   - Default under regex behaviour: route (i); an explicit request would ask for "a yes/no over the whole subject".
   - Regular? Yes: "no q anywhere" is the complement of `.*q.*`, a regular set, needing no stored values; only
     PCRE2's syntax lacks it (a callout gate models it exactly [i9]).
   - The question (whole-text, PARKED by the owner): routes (i) and (ii) differ 0 / 90 / 90 of 3,906 [i9].
4. A SEARCHED LONE COMPLEMENT `!q` (complement-place): no pattern gives its stretch or its preference order. Regex
   default: none (today a compile ERROR). In a WHOLE place it has an exact model [d4]. Regular as a set of whole
   values (a complement); no stored values.
5. polarity-rule: a compile-time rule; regex has none (its NOT is two-valued, so a constant-never or constant-always
   condition is just a pattern that never or always matches). Default under regex behaviour: no error, no warning.
   Nothing to make regular.
6. join-order: regex has no `&`; both orders are writable [g1, g2] and the usual idiom gives a third (atomic) answer
   [g3, g4]. Default under regex behaviour: none stated. Regular: holding is order-free (0 differ WHOLE); only the
   reported labels depend on it (414 of 1,365).
7. nested-complement: modelled by composition only, not run on its own.

## COMMANDS

W = /home/pcrec/projects/pcrec/worktrees/rxmodel; run from a scratch dir, e.g. `/var/tmp/pcrec-pcrec/scratch/rxmodel`.
Python 3.14 standard library and the installed libpcre2-8 (10.46).

    timeout 900 python3 -I W/docs/dev/lanes/pathimpact_evidence/pathimpact_model.py > pi_fwd.out    # premise (1), ~2 min
    diff pi_fwd.out W/docs/dev/lanes/pathimpact_evidence/pathimpact_model.out                        # prints nothing
    timeout 900 python3 -I W/docs/dev/lanes/rxmodel_evidence/rxmodel.py > rx.out                    # ~30 s
    diff rx.out W/docs/dev/lanes/rxmodel_evidence/rxmodel.out                                        # prints nothing
    grep -c 'over the set: WHOLE 0; SEARCHED 0; FIND-ALL 0' rx.out                                   # 62
    RXMODEL_SABOTAGE=1 timeout 900 python3 -I W/docs/dev/lanes/rxmodel_evidence/rxmodel.py > sab.out
    grep -c 'over the set: WHOLE 0; SEARCHED 0; FIND-ALL 0' sab.out                                  # 14
    diff rx.out sab.out | grep -c '^<'                                                               # 158
