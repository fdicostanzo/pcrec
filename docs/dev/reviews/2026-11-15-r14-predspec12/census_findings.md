# CENSUS findings: predspec12

## Findings

### CENSUS-1 (CONFIRMED; doc; effort S; blast: §0.1 prose only)
§0.1 draft:375-386, the paragraph "SAME ROWS RE-APPLIED UNDER THE ANCHORING RULING (rev 11 ...)", still states the
pre-rev-12 meanings in the present tense, unmarked: "`contains`/`search` remove that" (draft:377), "a filter that no
LOOSENING transform wraps" (draft:378), and "L17 and L63 ... HOLD (`contains(/err$/)` and `endsWith("err")` both
reject `err\n`)" (draft:380-381). Row L63 (draft:318) and the very next paragraph (draft:387-391) say L63 MOVED to
DIFFERENT and `contains(/err$/)` ACCEPTS `err\n` (oracle: `whole '(?s:.*?)(?:err$)(?s:.*)' 'err\n'` -> [(0, 4)];
with `\z` -> None). Rule: CF:1011-1019 (no transform removes/loosens; `$` plain PCRE). Same stale vocabulary, but
historical-tagged, at draft:2283 (§12 REV 11 paragraph: "no loosening transform wraps") and draft:202 / draft:2650
(old ruling rows, each followed by a REV 12 gloss, so those two HOLD). Fix: mark draft:375-386 "superseded by the
next paragraph" or strike its L63 clause; respell "loosening" as rev 11's term.

### CENSUS-2 (CONFIRMED; doc (G0b words); effort S; blast: §0.3, §11, §0.1, §2.6, Changelog)
"whole value" / "the value as the subject": §0.3 (draft:453) defines **value** = "anything of a kind (an rx or a
macro)", NOT used for "the filtered text (that is the SPAN; the owner's "the value being filtered", CF:994, is kept
in quotes)". Rev 12 uses "value" for the filtered span UNQUOTED in the draft's own voice, on 18 lines: draft:8, 9, 213,
214 ("final newline of the value"), 272, 318 (x2), 324, 387, 721, 2089 ("MUST MATCH THE WHOLE VALUE"), 2095 ("PLAIN
PCRE WITH THE VALUE AS THE SUBJECT"), 2105, 2115, 2136, 2193, 2203, plus §0.3's own "scoped match" row glossing it as
the span. So one word carries two meanings (a kind's member; the filtered text) inside THE ONE ANCHORING RULE itself.
The record's wording (CF:1011, 1013) is the source; §0.3 says a quoted ruling keeps its words "glossed where they
differ", so the fix is either to write "span" in the draft's voice (keep "value" only in quotes) or to change §0.3's
value row. Related: **subject** (§0.3 draft:450: "the run-time TEXT being matched") is ALSO used for the span in
"PCRE with the value as the subject" and in §2.7/§8 ("accepts the subjects S would accept", "the subject's length
read", draft:1910-1911: `length` reads the SPAN's length, not the run-time text's); the naming rule's "never an action
on the subject" relies on that second sense.

### CENSUS-3 (CONFIRMED; doc; effort S; blast: §0.1 verdict classes vs §2.6/§8/§0.3 library vocabulary)
"GAP" has two meanings, the second NEW in rev 12. (1) The §0.1 verdict class "GAP = no diagnostic yet (an open
defect against G0)" (draft:250-251; used on L20, L21, L22, L24, L29, L30, L32, L33, L35, L66, L67 and in O38,
draft:2830-2836). (2) Rev 12's "GAP TRANSFORMS" / "GAP bodies" / "plain GAPS" = the `(?s:.*)` gaps (draft:11, 216, 462,
1880, 2179, 2302-2303 "a gap body"). Uppercase `GAP`/`GAPS`: 34 occurrences; all spellings of gap(s): 99,
two meanings. Both stand in §0.1 rows side by side (L17 "plain gaps", L66 "DIFFERENT: GAP"), and O38 now discusses
"a `$` inside `contains`/`search` that a gap can follow" as a candidate for a GAP-class row. Fix: one of them renamed
(e.g. the library family "gap-bodied" in lower case only, or the verdict class "UNDIAGNOSED").

### CENSUS-4 (CONFIRMED; doc; effort S; blast: 3 sentences)
`$` described as the span's EXACT end where rev 12 makes it PCRE's. THE ONE ANCHORING RULE (§11, draft:2096) says
`$` is "the span's end or just before a final newline of the span; the exact end is `\z`". The MULTILINE sentence
in the same section, draft:2145, "without it [`(?m)`] `^`/`$` are the span's ends; never does either read outside the
span", and its copy in §13, draft:2597, give `$` exactly the span's end as its NON-multiline meaning, i.e. rev 10-11's
exact-end `$`, the reading rev 12 withdrew (oracle: `whole '(?s:.*?)(?:err$)(?s:.*)' 'err\n'` -> [(0, 4)], so `$`
held at 3, not at the span end 4). Looser "`^`/`$` = the (filtered) span's ends" phrasings at draft:334, 976, 2125,
2192, 2510 are compatible if "end" means PCRE's `$`-end and HOLD; 2145/2597 are the ones that contrast it with `(?m)`
and so state the exact end. Fix: "without it `^` is the span's start and `$` its end or before a final newline".

### CENSUS-5 (CONFIRMED; design/doc; effort S; blast: the one rule's trigger word "filter")
"filter" has two extents in §11, and THE ONE ANCHORING RULE keys on it. STRING SETS (draft:2078-2082): set positions
are an `&` operand, a label condition, a filter body, "a hole's set (together: FILTERS, the first three each applied
to a SPAN ..., the last a part of the filter it sits in)": a hole's set IS a FILTER there. THE ONE ANCHORING RULE
(draft:2087-2093): "A FILTER ... MUST MATCH THE WHOLE VALUE", and "an rx in a HOLE is part of the rx around it and
has no anchoring of its own" under EVERYWHERE ELSE. Read literally the first makes every hole (incl. `contains`'s
argument) whole-matched, the pre-rev-12 "the argument is anchored, the transform removes it" picture; the second is
the ruled one (CF:1011-1014: the filter side of `&` and a `label:` condition). The rule's own enumeration
(draft:2087-2088) excludes holes, so the ANSWERS follow the ruled meaning; the defect is the word. Fix: in STRING SETS
call the four "SET POSITIONS" only and reserve FILTER for the first three, matching §0.3's "filter role".

### CENSUS-6 (CONFIRMED; design (owner question framing); effort S; blast: §2.7 rule text, §13 O61 lean)
The naming rule is stated with a WIDER scope than CF:1020-1022. The ruling: named "for how it changes the FILTER /
which values the changed filter accepts (`padded`, `anchored`), never for an action on the subject". §2.7 draft:965-
967 adds a third ground: "which values the changed filter accepts OR WHAT IT READS (... `length`, ...)". O61's lean
(a) `occurrences(x)` rests on exactly that added clause: "a noun for what the changed filter reads, exactly as
`length(S)` names the value's length" (draft:3182-3183), and `length`, `left/right/mid` pass only through it. The
precedent is real (`length` is an owner-RULED name, CF:722), but the draft presents "or what it reads" as part of the
CF:1020-1022 rule rather than as this document's reading. Fix: mark "or what it reads" LEAN (derived from CF:722's
`length`), and say in O61 that (a) passes only under that reading. Other scope statements HOLD: §0.3 draft:462-463
("widens it to every provided transform"), §2.7 STATUS draft:993-995, §8 draft:1981 all give "every provided
transform"; no surviving "modifiers only" statement in the present tense (rev 10-11's is quoted as history). Minor
companion: the §2.7 HEADING "Transforms are FILTER MODIFIERS" (draft:946) still equates the two, against §0.3's
"`search`, `contains` (transforms, not modifiers)" (draft:463).

### CENSUS-7 (SUSPECTED for `capture`, CONFIRMED for the coverage gap; design/doc; effort S; blast: §2.7, §5.3, §8, O61)
NAMING CENSUS of every provided macro whose input and output are rx/filters (§0.3 draft:462: a transform is "ANY
macro filter -> filter"). Graded against CF:1020-1022:
PASS, graded by the draft: `padded`, `unpadded(n,S)` (accepts the unpadded spellings; LEAN O37), `any_case`, `quoted`,
`json.quoted`, `month_numbered`, `anchored`, `contains`, `startsWith`, `endsWith`, `length` (only via the added
"what it reads" clause, CENSUS-6). FAIL, marked OPEN: `search` (O61) -- correctly. No name is marked OPEN that passes.
PROVIDED BUT NEVER GRADED (O61, draft:3192-3194, asserts "No other provided transform fails the rule" and excludes
only `count`, `sort`/`unique`/`join`/`each`):
 - `capture(x) := /(?<${x.label}>${x})/` (§5.3 draft:1569, "a library macro"): rx -> rx, same accepted set, named by a
   VERB for an action on the subject's text (capturing it). Fails the rule if it is a transform; if it is a
   "structural tool" like `join`, O61's exclusion list should say so. SUSPECTED: confirm by ruling which it is.
 - `when(c, p)` (§8 draft:1907), `some(c)`, `all(c)`, `occurs.exactly/at_least/at_most/none` (§8), `list_of(X,
   sep)`, `any_order(a, sep)` (§5.3), `left/right/mid` (§8): all filter -> filter by §0.3's definition; all PASS on
   my grading (quantifiers / predicates / descriptions of accepted values; `left/right/mid` via "what it reads"),
   but none is listed in §2.7's rule examples or O61's audit sentence. `enumerate` is a built-in (not "provided"
   by the library) and acts on the rx, not the subject: HOLDS.
Fix: O61's sentence names the full list (or the report's audit is cited for it and includes these), and `capture`
is classed (structural tool vs transform).

### CENSUS-8 (CONFIRMED; doc; effort XS; blast: 3 sentences)
"search" (the noun) still names the SEARCHED MODE in three places, against §0.3 draft:464 ("**search** /
**searched**: `search(x)`, the library TRANSFORM / the MODE ...; not used for each other"): draft:647 ("a standalone
complement is useless in a search"), draft:2501 (E-DEPTH: "search finds an inner `[[[1]]]`", a final pattern), and
draft:2766 (O-item: "the "useless in a search" worry"). With `search` itself up for renaming (O61), these would
silently stay. Fix: "searched" / "a searched program". (draft:2131 "the same as a search for `/^err/`" is rev 6
history: HOLDS.)

## PROBED-AND-HELD
- (a) Anchoring vocabulary, occurrences / meanings (rev 12 copy): `\A` 26 / 1 and `\z` 34 / 1 (the scoped match's
  exact ends; every code use in a FINAL pattern: E-HTTP, L68, O62); `\Z` 0; `^` 178 and `$` in code spans: every
  filter-position code use (L7, L11, L13, L41, L69, E-CTX-1/5/7, `contains(/^err/)`, `contains(/err$/)`) read as plain
  PCRE with the span as subject, consistent with oracle; the exception is prose CENSUS-4. "scoped match" 14 / 1
  (§0.3's). "anchored(" 23 / 1 (the transform); "anchored"/"anchoring" (148 case-insens.) / 2 senses that agree (the
  implicit whole-match of a filter; a final pattern written with `\A...\z`), plus pre-rev-12 "remove that anchoring"
  only in CENSUS-1's places. "unanchored" 8 / 1 (PCRE's, outside filters; draft:2090 is the owner's quoted "31"
  reason). "searched" 49 / 1 (the mode). "whole" (100): "whole value" = CENSUS-2; "whole subject"/"whole span"/"whole
  string" one meaning each. "loosen" 3: draft:378, 2283 (CENSUS-1), draft:462 (quoted as rev 11's, HOLDS). "remov*"
  19: anchoring sense only at draft:10, 202, 377, 721, 829-831, 2650-2653: all but 377 negate it ("removes no
  anchoring") or are glossed REV 12. "exact end"/"exact-end" 22: every one names `\z` or the WITHDRAWN rev 10-11
  reading; none asserts it as current except CENSUS-4's implicit 2145/2597. "span" (165): the filtered text; a
  secondary sense "the reported match range" (draft:352-353, E-WEEKDAY "output = span") does not touch anchoring.
- No occurrence of an explicit anchor switching an implicit one off except as REJECTED (draft:2100-2101, L69).
- `anchored`'s `$` before a final newline is surfaced as OPEN (O62), not hidden; E-HTTP keeps `\A...\z` consistently.
- (b) Naming-rule scope statements: draft:462, 463, 965, 995, 1981, 3178: all "every provided transform"; no
  present-tense "modifiers only".
- Oracle calls: 2 (`whole` on `err\n` with `$` and with `\z`).
