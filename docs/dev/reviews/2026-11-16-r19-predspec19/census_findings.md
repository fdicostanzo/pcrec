# CENSUS findings: crit-predspec19
## Findings

### CENSUS-1 (CONFIRMED; doc; effort small; blast radius §8 THE FIELD REFERENCE census only)
§8 THE FIELD REFERENCE, THE CENSUS (rev19 l.2712-2713): "run over every `^` this document writes outside rx text (rev 19,
by hand; the occurrences are this section's rows, caveats, table (B)'s programs and §0.1 L72-L81)". Both halves are
false as written. (i) "every `^` ... outside rx text": the draft has 141 backticked bare `` `^` `` mentions outside rx
text, ~123 of them the ANCHOR (§11's "`^`/`$`", l.770-771, 2917-3008, 3159-3177, 4009-4014, ...), ~18 the sigil
("§5.4 `^` row", l.9, 777, 1506, 1529, 1533, 2018, 2035, 2048, 2445, 2514, 2679, 2701, 2712, 2715, 4277, 4521, 4644);
plus `^pattern` in a shell grep ERE (l.476). The census covers sigil occurrences only. (ii) the population list
omits sigil occurrences in §0 rulings table (l.457-459), §0.2 (l.753), §0.3 (l.777), §2.7 (l.1358), §3.5 (l.1506-1507),
§4.1 (l.1530-1537), §5.4 (l.2035), §8 TUPLE COMPARISONS (2445-2640), §12 table (3361), §13 O71/O75/O76/(16)/(17).
Most are shapes the rows do cover, but four SHAPES are in no census row (CENSUS-2). Fix: say "every SIGIL
occurrence" and list the sections, or add the rows.

### CENSUS-2 (CONFIRMED; doc/design; effort small; blast radius §5.4 `^` row, §8 census, O75)
Four sigil SHAPES the draft writes are covered by no row of §8 THE CENSUS (and two by no clause of the §5.4 `^` row):
(a) `^d.year` (l.8, 458, 1531, 1535, 2035, 2680): a dotted path, defined in every summary, used in NO program; the
census has no row for a reference whose path has more than one step, and the `.` row of §5.4 (l.2033) lists "a `$`
path" among `.`'s instances but not a `^` path. (b) `^h[2]` (l.2737, 4558: "an iteration index is written in the path at
the call (`^h[2]`)"): the O75 resolution DEPENDS on this spelling, yet the §5.4 `^` row says nothing about `[...]` inside
a `^` path (the `$` row states it at length: `$m.hit[2]`, `$m.hit[(g: "x")]`), the census has no row, and the 00:09
warning's trigger as worded ("whenever a compared field can hold more than one occurrence (a reference to a REPEATED
label, §4.2's boundary)", §8 caveat (6)) reads two ways on `^h[2]`: h is a REPEATED label (warn) / the field `h[2]` holds
one occurrence (no warn). (c) `(s: S)` with `s` bound to the WHOLE array `[^h, ^m]` (§3.5 l.1507, §8 l.2461, L74):
"`(h: S) | (m: S)`" -- a third reading of a reference parameter on the left of `:`, distinct from the census's last row
(`(s[k]: S)`). Under §4.1's ONE EXCEPTION it is legal only if an array of references counts as "a PARAMETER BOUND TO A
FIELD REFERENCE" (§3.5 says it is one) -- stated nowhere in §4.1. (d) the error shapes `(s[1].year: S)` (§4.1
l.1535) and `lex_ge2([^h], [9])` alone (§8 NO `&` IN SIGHT, l.2701) are missing from the census's error row (l.2728).
Fix: four rows (or clauses) and one sentence in the `^` row on indices/iterations in a `^` path.

### CENSUS-3 (CONFIRMED; design (status); effort small; blast radius §4.1, §5.4 `:` row, §8 STATUS, O75)
The ONE EXCEPTION is attributed whole to the manager's consequence, but the consequence (CF:1311-1313: "in a macro
body a parameter bound to a field reference may stand on the left of `:`") does NOT include the indexed form, and
the indexed form is the one O75 holds OPEN as an owner question. §4.1 RULE (l.1528-1530): "THE ONE EXCEPTION (rev 19; the
manager's consequence of the sigil ruling, CF:1311-1313 on main, checked here): in a MACRO BODY, a PARAMETER BOUND TO A
FIELD REFERENCE ..., or a literal-index entry of a parameter bound to a spelled array of them (`s[1]`, §3.2 tool 1,
O75), may stand on the left of `:`". §4.1 STATUS (l.1575-1577): "the manager's consequence ..., adopted with it; its
limits (what stays forbidden): LEAN" -- the PERMITTED `s[1]` widening gets no tag; §5.4's `:` row (l.2018) illustrates
the exception with exactly the open form, "(`(s[1]: S)`, rev 19, §4.1's one exception, `^` row)"; §8 STATUS (l.2768)
"the field-reference parameter on the left of `:`: the manager's consequence, adopted". Meanwhile O75 (l.4555-4558) and
the census's last row say `[k]` there READS ITERATIONS under the rules as written and needs a new stated exception.
So the rule text adopts what the open item asks. The draft's own §0 table (l.459) sees it ("One consequence is
INCOMPLETE as worded: the bodies also index an array of references") but §4.1/§5.4 do not carry that. Fix: in §4.1
split the clause: the unindexed parameter = the manager's consequence; the literal-index entry = OPEN (O75), and the
`:` row's example `(s: S)` or tagged OPEN.

### CENSUS-4 (CONFIRMED; doc (provenance); effort small; blast radius §3.5)
§3.5 RULE (l.1505-1506): "The same closure, rev 19 (the owner's general path, rulings R-1: "an array of something is
that something"): an ARRAY OF FIELD REFERENCES (§5.4 `^` row) is a field reference, "any one of these fields"". The
owner's words (CF:1321-1322) were about MACROS ("what otherwise is an array of macros?"); the application to references
is the MANAGER'S NOTE, not ruled (CF:1325-1327: "The manager's notes (not ruled): the SAME test applies to the sigil
route's own array, `[^h, ^m]`: by the general path an array of field references is a field reference"). §3.5 STATUS
(l.1514-1515) is unchanged from rev 18 and lists only RULED items, so this rev 19 sentence sits under a RULED-only
status with no LEAN tag. (§8 l.2459-2461 and L74 say "THE OWNER'S TEST APPLIED", which is honest; §3.5 is the one place
that reads as ruled.) Arguably it follows from the ruled general path (CF:644/1323) -- then say "consequence of the
ruled general path (the manager's note CF:1325), LEAN" in §3.5 STATUS.

### CENSUS-5 (CONFIRMED; doc (evidence); effort trivial; blast radius changelog, §5.4 `^` row, §8, L80)
"828 of 828 cross-operand calls refused" (changelog l.26-27; §5.4 `^` row "§8 table (B): 828 of 828 refused"; §8 l.2695,
2541; L80) is the evidence script's own refusal: predspec19_check.py l.135/186 `raise RefError(...)`, counted at
l.626-636. It is the exact shape rev 18 condemned (caveat (2), l.2580-2581: "Rev 17's "a COMPILE ERROR ... table (W)
shows the refusal" had no mechanism: the refusal was the evidence script's own `raise`"); here a mechanism IS stated
(§5.4's binding rule), so the count is not false, but it is a control sharing its source with what it controls: it
shows the model implements the rule, not that the rule refuses. Fix: say "refused by the model of the stated rule (the
script's RefError); not independent evidence" or drop the count. (B1's "22 of 48 would differ" IS informative.)
Arithmetic checked: B1 48 + B2 828 + B3 1,656 + B4 1,656 = 4,188 = the .out total (l.209); (X) 48,797 matches l.211.

### CENSUS-6 (CONFIRMED as a look-alike; doc (spelling-step input); effort trivial; blast radius §0.1, D193 spelling step)
The commonest sigil shape, `[^h, ^m]` (~45 of the ~187 sigil occurrences are inside such a spelled array), is
character-for-character a PCRE NEGATED CLASS ("one char not in {h, ',', ' ', '^', m}"), and the draft's own §5.4 intro
(l.2001) cites `[^,]` as the canonical rx-text example; `[ ]` "WRITES AN RX entry by entry" (§5.4 `[ ]` row) and an
array of rx IS an rx, so the two languages' `[` sit in adjacent positions. No program in the draft has two readings
(the sigil is expression-language only, and the census of rx spans found no `[^` ... `]` in expression position that
is not a reference array), but §0.1 (the LOOK-ALIKE TABLE, L72-L81 added this revision) has no row for it, and
neither does §5.4's `^` row ("its symbol is the spelling step's"). Fix: one look-alike row (`lex_ge2([^h, ^m], lo)` vs
`/[^h, ^m]/`), flagged for the spelling step, so the placeholder's worst collision is on record when the symbol is
chosen. (Rev 18's `^.h` had the same issue: `[^.h, ^.m]`, l.575, 4597.)

### CENSUS-7 (CONFIRMED; doc; effort trivial; blast radius §8 ANY NUMBER OF FIELDS, §4.1)
§4.1's exception admits "a literal-index entry" and forbids "arithmetic or a computed index (`s[n - 1]`, until O69
(3)'s trigger)". §8's recursive general form has THREE indexed left-of-`:` occurrences: `(s[n]: padded(>=lo[n]))`
(l.2624, base case) and `(s[n-j+1]: ...)` twice (l.2625). The draft's rev 19 note (l.2632-2634: "on the left of `:`
that index is also outside §4.1's one exception, which admits a LITERAL index only") names only `s[n-j+1]`. `s[n]`
(a PARAMETER bound to a literal, no arithmetic) is neither "a literal-index" nor "arithmetic" as worded: unclassified.
Fix: say whether an index that is a parameter bound to a literal counts as literal (the any-n trigger needs it either way).
Census of `[n]` on the left of `:` (all code spans, grep `name[idx](.field)?:`): 41 occurrences --
ITERATION index `x[1]`/`x[2]` 9 (L64, §3.2, §4.3, §13 O-items: one meaning, the position rule); ENTRY pick on a
reference parameter `s[1]` 16, `s[2]` 7, `s[3]` 1, `s[k]` 3 (the O75 collision, stated by the draft); recursive
`s[n]` 1, `s[n-j+1]` 2 (this finding); `s[1].year` 1 (stated error); `f[2]` 1 (the draft's own two-reading example,
l.2734). Reference arrays carrying an index: `^h[2]` 2 (CENSUS-2 (b)); no `[^h, ^m][k]` written anywhere.

### CENSUS-8 (CONFIRMED; design (owner's idea narrowed); effort small; blast radius §8 THE PROJECTION (iv), §5.4 `^` row errors)
§8 THE PROJECTION (iv) (l.2665-2667): "his idea at CF:1295-1302 reshaped rev 18's mark plus `.`, `^.h`, into a sigil, so
the other side is never a thing in its own right and the question of the mark standing alone does not arise". The
owner's words: 23:44 "what about a symbol that represents the other side of the intersection" (CF:1270-1271) and
23:56 "IF the otherside mark can't be used alone, it could just be a scoping sigil like ^h" (CF:1297) -- a CONDITIONAL
whose premise was the manager's "would START as field access only". "Given up: the other side as a thing in its own
right" (CF:1302) sits inside "The manager's notes (not ruled)". The 00:06 ruling picks "the sigil mark" over the
SECTION; it rules nothing about a standalone other side. The draft turns the manager's "Given up" into part of the
owner's idea and makes every standalone use an ERROR (`P & ^h`, `r := ^h`, §5.4 `^` row) with no record that his
original form (a symbol for the other side itself) is DEFERRED rather than refused. Fix: attribute "never a thing in
its own right" to the manager's note CF:1302, and record the standalone other side as a not-adopted-now item with a
trigger (see CENSUS-10 unlock U1), not as a question that "does not arise".

### CENSUS-9 (SUSPECTED; doc (provenance); effort trivial; blast radius §0 rulings table l.457, §8 l.2705, §15 l.4644)
"(a pointer, LOW WEIGHT: the owner does not recall asking)" (l.457) and "LOW WEIGHT, he does not recall asking"
(l.2705) characterise the owner, but CF:1284-1293 says nothing of the kind (grep "recall"/"low weight" in
COND-FAMILY.md: 0 hits); the record's own qualifier is "(the manager's READING, to confirm)". If the source is the
lane's rulings file it must be cited; otherwise it is an unsourced statement about the owner. Confirm by the
lane's brief/rulings file (not in this round's copies).

### CENSUS-10 (design; the two standing questions; effort: record only; blast radius §5.4, §4.1, §13)
SIBLING. Yes: `^` is a sibling of `$` (both a sigil before a label PATH; the owner's own frame "scoping sigil like
^h", the manager's "same grammatical shape as `$`", CF:1299) and the reference is a third face of the one field that
`:` and `.` already address. The draft TREATS it as `$`'s sibling in the summary ("three spellings with one role
each", l.2684-2685; L76) but NOT in the mark table's mechanics: (i) the `$` row states path-wholeness, iterations
`$m.hit[2]` and selections `$m.hit[(g: "x")]`; the `^` row states none of these (O75 nevertheless leans on `^h[2]`);
(ii) the `.` row (l.2033) lists "a `$` path" among `.`'s instances, not a `^` path, though `^d.year` is the `^` row's
own example; (iii) the `:` row's "FIELD PATH of the operand's map interface" and the `^` reference are the same
object (a field path resolved against the other side) yet §4.1 frames the reference on the left of `:` as an
EXCEPTION rather than as the general case.
GENERAL FORM (lens: fewer, more general). A field reference is "a field PATH of an operand, resolved where written".
`h:` in a condition already IS that (the condition reads the other side, §4.1's lookup); the draft's own error text
for `(^h: S)` says so ("a condition already reads the other side, so the reference adds nothing there"). So the
general form is: the left of `:` is ALWAYS a field reference; `h:` in a written condition is its implicit spelling,
`s:` through a parameter its passed spelling. Stated that way §4.1 has NO exception (one rule: "the left of `:` is a
field reference"), `(^h: S)` is the explicit spelling of `(h: S)` (an equivalence, not an error, or kept an error as a
one-spelling choice), and `$h` is "the value of the reference ^h" -- one primitive (the reference) with `:` and `$` as
its two uses. The manager raised exactly this at 23:44 ("whether `(h: S)` is then readable as a condition on `^.h`
(fewer, more general primitives)", CF:1281-1282); the draft answers only the spelling half (an error) and never
records the unification. Not proposed for adoption here; recorded as the general form.
UNLOCKS, each with its trigger: U1 the STANDALONE other side (`^` alone = the operand's map; `^.h` = `^h`), giving the
owner's 23:10 "a macro that takes a map and produces an array given labels" literally (THE PROJECTION (ii)) -- trigger:
a library body that must enumerate the operand's labels (§13 C25 reading (B), "all of v's labels"). U2 other
FIELD-TAKING library families over the same mechanism (relations between labels: E-CAL `valid_date([^y, ^m, ^d])`,
E-NEAR's distance, `all_distinct`, §4.6's capture-vs-capture `x: <$y` as `lt(^x, ^y)`) -- trigger: a second §12 case or
library family wanting to be a call over fields rather than inline conditions. U3 the ANY-n compare (§8 `lg`) once
the index rule covers parameter/arithmetic indices -- trigger: O69 (3) (already filed; CENSUS-7 widens it). U4 field
references as OUTPUT selectors (`captures` naming which spans to report, §6.2) -- trigger: the reporting-axis design
needing a named-span list. U5 the `compare.repeated` warning (L75) becomes a generic "two references to one field in
one spelled array" lint for any field-taking family -- trigger: U2's second family.

## PROBED-AND-HELD
- (a) CENSUS COUNTS, every backticked span and every indented code line of rev 19 (scripts census/caret.py,
  count.py; classification by position inside `/.../`, then hand-checked; counts approximate to +-3 where a span's
  backtick pairing is ambiguous): ANCHOR inside rx text ~167 (incl. `(?m)^`, holes' nested `/^a/`, l.476's shell
  ERE `^pattern` 2 = "other"); CLASS NEGATION `[^...]` 13 (`[^,]`, `[^"]*`, `[^\r\n]`, `[^,]+`); SIGIL ~187 (`^h` ~150,
  `^m` ~110 as array partners, `^major`/`^minor`/`^patch`/`^sec`/`^year`/`^mnum`/`^a1`/`^a2`/`^b1`/`^b2`/`^x`,
  `^d.year` 6, `^h[2]` 2); OLD MARK `^.h`/`^.m` 7 (all in history, L77, O71/(13): superseded, error row); `${^h}` 2
  (error row); BARE `` `^` `` mentions 141 (~123 anchor, ~18 the sigil/`^` row). 
- Every sigil in a PROGRAM shape stands in one of the two stated positions (argument; entry of an argument array) or
  is listed as an error with its fix: 0 references written outside the positions. Checked: worked block l.2480-2487
  (8 lines, 16 refs), caveats, table (B) programs B1-B5, L72-L81, O75/O76, (16)/(17).
- No sigil occurrence has two readings in the expression language (CENSUS-6 is a reader look-alike, not a parse
  ambiguity); `${^h}` vs `/x${/^a/}/`: hole content is expression language, so `^` there is the sigil (an error) and
  inside a nested `/.../` the anchor: consistent with §5.4's "exactly TWO stated exceptions" (the sigil is not a third).
- Table (B) arithmetic and (X) count against the .out (CENSUS-5). L79's "22 of 48" = .out l.202. Census rows' "names"
  column agrees with §5.4's binding text in all 13 rows (B4 correctly marked lean-dependent).
- (b) Ruling fidelity held for: the sigil RULED, symbol a placeholder (CF:1308-1310) -- §5.4 STATUS, §8 (iv), O71;
  positions/binding/errors/bound-call tagged LEAN (§5.4 STATUS l.2050-2052); the three-spellings framing attributed
  to the manager's note (l.458, 2685); section not adopted with his reason AND his open door verbatim (§8 (iv),
  l.2668-2671); bare reference RULED out with both reasons (L72, l.2474); macro-arguments NO (O73, with the manager's
  withdrawal correctly marked overtaken); looped-compare warn, meaning kept, not an error, fix named (caveat (6), O74)
  -- CF:1332-1334 matches; tuple names/order rulings cited correctly; the "manager's consequences" (1)-(3) marked as
  his (l.459) except CENSUS-3's indexed widening. Mild stretch, held: §5.4 STATUS cites the owner's "it wouldn't be
  clear where it was coming from" (said of a BARE reference) as "the owner's stated value" behind binding-where-
  written; it is tagged LEAN and the manager's lexical lean (CF:1280) is cited beside it.
- O76's lean (a) (resolve at fill site) is in tension with the owner's visibility reason; the draft states both sides
  and leaves it to him: held.

## Deadline note
All probes above ran before 00:45 (last script ~00:25). Not run: predspec19_check.py (the coordinator's 00:20 re-run
was taken as given); no independent check of B5 beyond reading the script. Census counts are by script + hand,
approximate where noted.

CRITIC COMPLETE
