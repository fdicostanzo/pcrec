# CENSUS findings

## Findings

### CENSUS-1 (CONFIRMED; doc/design; effort small; blast: §0.3, §7.1, §11 STRING SETS, §11 rule bullet 1 vs §11 warning table, §2.7)
The list of FILTER ROLES (= where `anchor.whole` fires and what opens a scoped match) disagrees with itself. The §11
warning table (rev14 l.2440) and §2.7 (l.1134-1135) and O67 (l.3605) put a FOURTH place in it: "the argument of
`any_case`, `length`, `month_numbered`, `json.quoted`: fires yes (LEAN), matched whole on the transform's reading".
The four canonical lists omit it: §0.3 filter role row (l.559: "either side of `&`, a `label:` condition, a
compile-time set"), §7.1 (l.2014-2016: "a side of `&`, a `label:` condition, a compile-time set, a parameter a body
puts in one of these"), §11 STRING SETS (l.2262-2263: four set positions, "The first three are FILTER ROLES"), §11
rule bullet 1 (l.2285-2290). §0.3 scoped-match row (l.555) and l.2297 say "exactly two things OPEN one" (program,
filter role over "its stretch"), but the pullback argument is matched whole on READING text that is no stretch of the
subject, and l.2361 calls "what a modified filter reads" CONTEXT-FREE. Count: 3 of 7 statements include the place,
4 of 7 omit it (and §7.1, the contract list of the warning, is among the omitters). Repro: read the seven lines cited.
Fix: either add "(LEAN, until O67) the argument of a reading transform" to §0.3/§7.1/STRING SETS, or point all of
them at ONE list (see CENSUS-7).

### CENSUS-2 (CONFIRMED; doc, with a design edge; effort small; blast: §0.3 filter modifier row, §2.7 heading and RULE, §3.5, §8, ~20 own-voice sites)
"filter modifier" and "pullback" each carry TWO meanings in the document's own voice after rev 14. (a) §0.3 l.564:
filter modifier = "the PULLBACK kind of transform"; §2.7 heading l.1060 "Filter modifiers: the pullback kind";
l.1066-1067 "Mechanically the modified filter is the pullback of S"; l.1138 "One mechanism (the pullback)". (b) Rev 14
l.1070-1072: `padded` is a plain hole macro and "the pullback proper is needed only by the transforms whose reading
yields text the subject does not contain" (the four of O67; l.1123-1133, l.3601, l.3647 use "pullback" in this
narrow sense, 9 sites). Yet `padded`, `quoted`, `left`/`right`/`mid` (all plain-body, no pullback, §2.7 table) are
still called filter modifiers: l.645 ("an unapplied filter modifier (`padded` alone)"), 761, 786, 793, 796,
1093-1096, 1269 (`[padded, any_case]` "an ARRAY OF FILTER MODIFIERS"), 2081 ("Standard FILTER MODIFIERS"), 2338,
3096, 3585. Census: "modifier"/"modified"/"filter modifier" 61 own-voice-or-history occurrences after the changelog;
the 13 own-voice live sites listed (l.645-3585) name a plain-body transform as a "modifier"/"pullback kind". Fix:
either §0.3 says "filter modifier = a transform that changes what the filter reads (§2.7 list), whether by body or by
the pullback" and "pullback" is kept for the primitive, or `padded`/`quoted`/`left` move to "transform".

### CENSUS-3 (CONFIRMED; doc/design; effort small; blast: §2.1 kind table, §2.3, §2.7 RULE, §0.3 transform row)
STALE "a transform's PARAMETER IS A FILTER". Rev 14 withdrew "a modifier's argument is itself a filter" (changelog) and
§11 l.2271 reserves "filter" for things in a filter role, with `padded`/`contains`/`startsWith`/`endsWith`/`anchored`/
`occurrences` putting the parameter in a HOLE (l.2269, not a filter role). Still live: l.1062 "A TRANSFORM is a macro
FILTER -> FILTER (its parameter is a filter and its result is a filter)"; l.644 "a macro whose parameter is a filter
and whose result is a filter"; l.725 "a macro called on a filter"; l.761 diagnostic text "modifier `padded` has no
filter"; l.1095 "A modifier without its filter argument". 6 own-voice sites (5 lines; l.563/1141/1144 carry the
owner's CF:903 "filter -> filter" word, kept). §0.3 l.559 "a filter = a thing in that role" makes `padded(/^5/)`'s
argument NOT a filter while l.1062 says it is. Fix: "a macro rx -> rx whose result is used in a filter role"; the
argument "lands where the body puts it" (already l.1096-1099).

### CENSUS-4 (CONFIRMED; doc; effort small; blast: ~13 sites in §0, §0.1, §2.6, §5.6, §11, §13)
STALE "search" in the document's own voice, against §0.3 l.565 ("'search' alone is used only in quotations and
history"). Census of `\bsearch(es|ing)?\b` after the changelog: 108 matches; 7 are the warning name `empty.search`
(kept by §0.3); the rest are quotations, rename notes or history EXCEPT these 13 live uses: l.305 G4 "a search's hits"
(the transform); l.342 L16 reason "The search filters nothing" (the transform); l.344 L18 "a nullable final search
pattern" (the mode: "searched"); l.1030 "Search results stay values-not-globals"; l.1033 STATUS "Search as a library
transform of the `contains` family"; l.1035 "Search a transform but not a filter modifier"; l.1846 "No assertion
states SEARCH behaviour" (mode); l.2363 §11 "A SEARCH inside a span (`(m: occurrences(rx))`" (transform, rule
text); l.2402 §11 ampersand table row (i) "the stretch ... the search tries" (mode; rev 13 text); l.3145, 3146, 3148
O36 "A search assertion ... state search behaviour ... what a search finds" (open item, own voice, 4 uses on 3 lines).
Borderline (6): l.302 "log/JSONL searches" (users' activity), l.928 "as the owner expects of a search", l.1875
"library SEARCH assertion (review Q1X-5)", l.2344 (rev 6 narrative), l.2768 "Searching `foobarbaz`" (mode, verb),
l.3065 O10 "unanchored search" (PCRE mode, see CENSUS-5). Fix: respell to `occurrences`/"searched"/"the search mode".

### CENSUS-5 (CONFIRMED; doc; effort trivial; blast: §0.3 row l.556 vs 5 own-voice sites)
"anchored" has a THIRD meaning in the document's own voice that §0.3 l.556 forbids ("'anchored' names ONLY the macro
`anchored(...)` ... and the real assertions"): the PCRE/API whole-subject MATCH MODE (PCRE2_ANCHORED-like). l.345 L19
"`empty.search` in searched mode, none when anchored"; l.1977 "the caller's anchored/whole-string MODE exempts";
l.3065 O10 "unanchored search"; l.3400 "libpcre2's own anchored match"; l.466 (rev 12 history: "unanchored as in
PCRE") and l.255 (record column) are history/record. So 4 live of 6. The rev 14 census
(`evidence/predspec14_census.py`) files these as "other: PCRE/API mode" (6 before, 6 after) and so never reports them
as a violation of the new row. Fix: "whole-subject mode" at the 4 live sites, or a §0.3 gloss admitting the API
mode as the third named use. Also the row's list of "real assertions" differs by site: §0.3 l.556 and §11 l.2283
`\A \z \Z ^ $`; changelog l.8 and §13 l.3483 `\A \z ^ $` (no `\Z`); rulings table l.284 `\A`/`\z` (the owner's words,
CF:1088). 4 lists, 3 memberships; only `\A`/`\z` is RULED, the rest is this document's extension, yet l.556 labels
the whole row RULED.

### CENSUS-6 (CONFIRMED; doc, with one rule-text clash; effort small; blast: §8 anchored, §11, §13 O64; §0.3 has no "scope" row)
"scope" is used bare as a short form of §0.3's "scoped match" AND in three other own-voice meanings, and two of them
contradict each other in the anchor text. Census of `\b(un)?scop(e|ed|es)\b` after the changelog: 68 matches; 24
are "scoped match"; of the rest, bare "scope" = the scoped match (the anchor sense) at l.394, 556 (the §0.3 row
itself: "pins its argument to the ends of its scope"), 2064, 2066 (x2), 2404, 2409, 2413, 2437, 2439, 2456, 3570,
3574 (13); "SCOPE" = the group/flag namespace of a literal at l.2215 ("A literal is its OWN SCOPE (numbered groups do
not leak ...)"); = an operand's extent at l.2251 ("SCOPE OF AN rx-TEXT `&`") and l.2502 ("the guard's stated
scope"); "scoped" = a flag-scoped group `(?s:...)` at l.844, 1044, 1055, 2051, 2151, 2576 (6); plus project scope
(l.498, 511, 513). THE CLASH: l.2066 "In a HOLE no scope is opened" (and l.2413, 2439, 2456 "the hole opens no
scope") vs l.2215 "A literal is its OWN SCOPE" — a literal written in a hole (`/x${/^a/}/`) both is and opens no
scope; and l.2051 ("The gaps are SCOPED `(?s:...)`") sits 13 lines above l.2064 ("the ends of its scope") in the same
§8 paragraph about anchoring. The owner's own word is "scoped match" (CF:1005) and his rulings use "scope" in the
anchor sense (CF:1087), so the fix is to spell the anchor sense "scoped match" everywhere (13 sites) and respell
l.2215/2251/2502 ("group namespace", "extent").

### CENSUS-7 (CONFIRMED; doc; effort small; blast: §0.3 span row, §11 throughout)
TWO WORDS FOR ONE THING: "stretch" (rev 14, 56 matches after the changelog, 48 lines) and "span" (186 matches) both
name the text a filter role matches whole, in the same sentences' own voice. §0.3 l.554 "span = the text a set
position filters: an `&` operand's text, a label's text ..." and l.556/559 "a filter role MATCHES ITS STRETCH WHOLE"
never say the two are one; §0.3's G0b lean is "one word per thing" (l.545). Side by side: l.2391 "each matches the
WHOLE span the `&` is applied to" vs l.2400 "the stretch both sides match whole"; l.2264 "open a scoped match over a
stretch of the subject" vs l.2332 "The span is fixed where the FILTER ROLE is"; l.555 "(its span, matched WHOLE)" vs
l.2298 "every FILTER ROLE ... (its stretch)". The owner ruled only the PHRASE "matches its stretch whole"
(CF:1083-1088); the free noun "stretch" (l.1070 "SELECTS a stretch of the subject", l.1112 "the body's stretch",
l.2393 "one stretch of the subject from end to end") is this document's. Fix: one §0.3 line, "stretch: the ruled
phrase's word for the span (same thing)", or keep "stretch" only inside the ruled phrase (18 of the 56 are in a "... stretch whole" form;
38 are free-noun uses).

### CENSUS-8 (CONFIRMED; doc; effort trivial; blast: §5.4 MARK TABLE `${ }` row)
§5.4 MARK TABLE disagrees with §12: the `${ }` row (l.1782) cites "E-HTTP (`/\A${block}\z/`)" as a case using the
hole, but rev 13 respelled E-HTTP's final pattern to `anchored(block)` (l.2785, l.2610 "CODE LINES: one changes");
E-HTTP's code (l.2779-2785) holds no `${`. Re-run (`census/marks12.py`, every §12 code block, comments stripped):
`${` occurs in E-JSONL, E-DEPTH, E-CTX only: 3, the row claims 4. Every other §12-case column of the MARK TABLE
re-runs: `&` all but E-SEP/E-DEPTH; `|` E-FILE/E-DEPTH; `,` all but E-LUHN/E-DEPTH/E-CTX; `/.../` all but E-CAL;
`#` 10 of 12; `"..."` all but E-SEP; `@` E-IPV4/E-CAL/E-CTX; `$` E-WEEKDAY/E-CAL/E-RFC/E-NEAR; `!` E-FILE. Fix: drop
E-HTTP from the row (or cite `anchored`'s body, §8, as prose).

### CENSUS-9 (CONFIRMED; maintenance (the evidence, not the spec); effort trivial; blast: the census the changelog cites, l.9 "respelled by census")
`evidence/predspec14_census.py` misfiles; its "after" counts (run: `python3 -I ../evidence/predspec14_census.py
rev12 rev14` from census/: whole-match/& tie 62, real assertion 92, macro 119, warning 45, PCRE/API 6, E-NEAR 5,
changelog 26; total 355) are not a classification of meaning. Misfiles found by reading its per-line dump
(`census/census_dump.py`): (a) "whole-match / & tie" (the class the respelling was meant to drain) holds at least 13
that are NOT the tie: the macro at l.2787, 2795 ("ANCHORED", "the anchored block" = `anchored(block)`), l.270
("Anchored def"), and the owner's tag "anchored-in-hole" at l.285, 2059, 2458, 3566 (its macro test needs a backtick
before or `(` after); a real assertion at l.2568 ("E-JSONL (anchored by its own `/^${q}$/m`"); meta-mentions of the
word itself at l.284, 556 (x2), 2283, 2508, 3483. (b) "real assertion (noun)" holds the owner's tag
"anchor-warn-scope" (4: l.286, 333, 2420, 3580). (c) "other: PCRE/API mode" holds l.1888 "make the anchor a
constant", which is E-NEAR's date (see CENSUS-10). (d) the script never flags the API-mode class as a §0.3 violation
(CENSUS-5). Net: the script's 62 "whole-match" residue overstates live misuse; reading it, I find 0 own-voice LIVE uses
of "anchored"/"anchoring" for the tie or the whole-match requirement outside history/quotes (held, below) and 4
API-mode uses (CENSUS-5).

### CENSUS-10 (CONFIRMED; doc; effort trivial; blast: §12.7 E-NEAR, §7 diagnostic text l.1888, §13 l.3234)
"anchor" (noun) has two meanings in the document's own voice: the real assertion (the §0.3 l.556 sense; `anchor.whole`
"an anchor in a side") and E-NEAR's REFERENCE DATE: l.2741 heading "three anchor cases", l.2744 binding `anchor :=
param(isodate)`, l.2745 `of = anchor`, l.2751 "anchor +- 15 days", l.1888 diagnostic text "make the anchor a
constant", l.3234 "`anchor := param(isodate)`". 6 of the ~95 "anchor"/"anchors" noun uses. Harmless before rev 14;
now that §0.3 polices the anchor words and the warning's own text says "an anchor ... adds nothing", a worked example
named `anchor` reads as one. Fix: rename E-NEAR's run-time input `ref`/`pivot` (a placeholder spelling, D193 add. 4).

### CENSUS-11 (SUSPECTED as a design gap, CONFIRMED as drift by CENSUS-1; maintenance/design; effort medium; blast: §0.3, §5.4 `&` row, §7.1, §11)
SIBLING OF A FAMILY. Rev 14's role-keyed warning is the THIRD role-keyed fact the document states with its own
list of positions: (1) the edge-assertion ERROR, keyed on SET POSITIONS (4: `&` side, `label:`, compile-time set,
hole's set; l.2262-2266, l.2373); (2) "opens a scoped match" / matched whole, keyed on FILTER ROLES (l.555, 559,
2285-2290, 2297); (3) `anchor.whole`, keyed on filter roles after expansion (l.2014-2016, l.2309, table l.2430-2440),
plus the derived "where a provided transform's parameter lands" list (l.2269, l.2436, §2.7 table l.1115-1127). The
position list is restated at 7 sites (§0.3 x2, §5.4 `&` row, §7.1, STRING SETS, rule bullet 1, warning table) and
already drifted (CENSUS-1: the pullback argument in 3, absent from 4). GENERAL FORM: ONE declared role table, a row
per position after expansion (side of `&`; `label:`; compile-time set; hole; final pattern; `records` item rx;
reading-transform argument), columns: set position? / opens a scoped match over what / anchors read / edge-assertion
error / `anchor.whole` / empty-match rule; every other site points at it (the §11 warning table is two columns of it
already; the house first-match-table form). UNLOCKS: the primitive-transforms ruling (whichever way) edits ONE row;
O66's "can never match" warning and any later position (a tuple compare's fields, O69) become rows, not new
paragraphs. TRIGGER: the primitive-transforms ruling itself (the next edit to the position list), or the next
review finding of list drift. Effort: one table + 6 pointer edits.

## PROBED-AND-HELD

- `anchor.operand` (16 occurrences after the changelog): every one is history, a "(rev 13: ...)" gloss, or a
  rev-13 re-applied paragraph (l.477-491, 2613) or a §13 decision/O65 head (l.3465, 3579). 0 stale live uses.
  `anchor.whole` agrees across §7.1, §5.4 `&` row, §11 warning section, §0.1 rows L7/L11/L15/L41/L70/L71 and
  §12 E-CTX-1/7 (class columns re-read: L7, L11, L15, L41, L70, L71 = DIFFERENT: WARNING; L13 BY DESIGN; L69 SAME,
  as the rev 14 §0.1 paragraph l.487-495 says).
- "anchored"/"anchoring"/"unanchored" for the `&` tie or the whole-match requirement: read every hit of the census
  script's whole-match class (62) and the KWIC list (184 non-macro-call hits): 0 own-voice LIVE uses; the rest are
  quotations, rulings-table record columns, history paragraphs (l.426-472, 2581, 2595, 2973-2976, §15) or
  meta-mentions of the word. The rev 14 respelling holds for that sense (exceptions: API mode, CENSUS-5).
- `occurrences` (renamed from `search`): every code span naming the transform uses `occurrences`; `search` in code
  spans appears only as "spelled `search` through rev 12", rule-history, or the owner's sketch (l.840, 215).
- `&`, `\&`, `[&]` under the rx-& switch: 14 hits after the changelog; §5.4 `&` row, §5.4 STATUS, §11 l.2204/2245,
  STATUS l.2501, §0.2 l.508 and O60 l.3527-3528 all say "`\&` or `[&]`", RULED CF:1041-1046; l.243, 3450, 3518-3519 are
  rev 11 history ("[&]" alone) and say so. Consistent.
- "hole": one meaning throughout (`${ }` insertion; a parameter spliced by a body is the same thing, §2.7 l.1112).
  §0.3 has no "hole" row; the §5.4 `${ }` row is its definition. Held (row absent but no second meaning).
- "plain macro": one meaning (a macro whose meaning is its body's text, no special case) at every own-voice use
  (§2.7, §8 l.2058, §11 l.2305, O67); "NOT EXPRESSIBLE" consistently = no body over the subject text.
- "filter role" as defined by §0.3 l.559 is used in that sense at every own-voice use I read in §2.7, §8, §11;
  the defects are the LIST (CENSUS-1) and "filter" as a parameter type (CENSUS-3), not the phrase.
- Self-quoted counts that RE-RUN: "three sentences" (§11 rule: 3 bullets); "eight positions" (ampersand table rows
  i-viii: 8); "four set positions ... first three FILTER ROLES" (l.2262-2263); "five ... NOT plain macros ... four
  remain" (§2.7 table: 5 NOT EXPRESSIBLE rows incl. CUT `unpadded`); l.2269's six hole-landing names = the §2.7 table's
  hole rows; §5.4 "`( )` has four rows" (4); "exactly TWO stated exceptions" inside `/.../` (`${`, `&`); MARK TABLE
  §12-case columns: all re-run except `${ }` (CENSUS-8), by `census/marks12.py`. Not re-run: "165 of 7,057 corpus
  pattern lines" (l.3518; a corpus count, outside this lens and the document).
- Provenance §15 rows l.3681-3682 cite "§11 THE ONE ANCHORING RULE" (the old heading); they record what rev 12/13
  wrote, and l.2484 glosses the rename, so held as history.
- STANDING (2) GENERAL FORM + UNLOCKS, held: the whole-match rule is already in its general form (a role opens a
  scoped match over the text it takes; anchors read the innermost; l.2296-2299). The role-keyed warning's general form
  is "a diagnostic is a predicate on (role after expansion, construct)", whose unlock is the role table of CENSUS-11
  (O66's never-match warning would be one more column; trigger: a measured user report of a never-matching program,
  as O66 says). The plain-macro bodies' general form is "the library is bodies over a small primitive set (splice,
  `&`, `label:`, the pullback)", which is the open owner question primitive-transforms: not raised.
