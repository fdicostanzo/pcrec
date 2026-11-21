# verify

## Verdicts

Oracle: `verify/o.py` (ctypes libpcre2-8 public API, ANCHORED|ENDANCHORED = 0x80000000|0x20000000) and python3 -I `re`. Scripts: s.py, http.py. Loop body = §2.6 L563 spliced: `(?s)(?:.*?(?<hit>X)){N,}.*`.

### SIM-1: HOLDS
`loop('(?:(?<c>a)|b)c(?(<c>)a|d)','acabcd')` -> ovector [(0,6),(0,3),(0,1)]: hit (group 1) = (0,3) only, one hit `aca`. Find-all by `re.finditer` = [(0,3),(3,6)]; anchored match from 0 -> (0,3), from 3 -> (3,6) (unrolled/find-all = TWO hits). Second repro `(?:(?<c>a)|b)\k<c>?c` on `acbac`: loop last hit (2,5)=`bac`; fresh-start matches at 0 -> (0,2), at 3 -> (3,5); at 2 -> None (so `bac` exists only through the carried c). Text claim at L596-600/628-633 (equal "for an argument that cannot match empty") is thus false for backref/conditional on own group.

### SIM-2: HOLDS
`loop('(?<g>a)?b','abb')` -> [(0,3),(2,3),(0,1)]: last hit hit=(2,3) `b`, g=(0,1) (outside the hit, from hit 1). Under per-iteration reading g would be unset in hit 2. Draft L1531-1532 "the argument's labels inside it" does not say which. 

### SIM-3: HOLDS (doc severity; note the draft DOES state hole semantics at L569-570)
Quoted L563 body, L1516 `startsWith(s) := /${s}(?s:.*)/`, `endsWith(s) := /(?s).*?${s}/`. Spliced runs: `(?s)(?:.*?(?<hit>a.b)){1,}.*` on `a\nb` -> match (0,3); scoped `(?-s:a.b)` -> None. endsWith spliced `(?s).*?a.b` on `xa\nb` -> (0,4); scoped `(?s:.*?)a.b` -> None. startsWith `a|b(?s:.*)` on `ax` -> None; `(?:a|b)(?s:.*)` -> (0,2). endsWith `(?s).*?a|b` on `xb` -> None; grouped -> (0,2). `(.)\1` as argument spliced min 1 on `xaay` -> None (find-all has `aa`). `(?<hit>a)` argument -> COMPILE-ERR. All as claimed. Caveat: if holes are atoms with own flags/numbering (§3.3, §11, stated L569-570) the bodies are right; the finding is about spliced reproduction.

### SIM-4: HOLDS
L588-589 quoted: "as SETS both are the values with a substring in x". `loop('^err','x err',1)` -> None (rejected) while `re.search('err','x err')` True. L612-616 says `contains(/^err/)` = startsWith. Contradiction with the "values with a substring in x" sentence for anchored x as claimed.

### SIM-5: HOLDS
`loop('err$','err\n',1)` -> [(0,4),(0,3)]: accepts, hit (0,3). `m('err$','err\n',AE)` -> None (whole-span filter rejects; endsWith("err") = `(?s).*?err` ANCHORED|ENDANCHORED also rejects `err\n`). The draft's §11/L612-616 text ("ends of the span") does not say `$` is span-end exactly vs PCRE `$`.

### SIM-6: HOLDS
Text: L1718-1719 "Subjects are searched ... unless the program anchors"; E-HTTP program (L1907-1915) has no anchor and no whole-subject mode; D196 (decisions.md:10203-10206): "leftmost start, then the left operand's first-preferred end the right operand accepts exactly". http.py (headers language `tok:[^\r\n]*` list sep CRLF, ends longest-first, counts checked per span): `'Host: a\r\nhost: b'` -> (0,7,'Host: a'); `'Host: a\r\nTransfer-Encoding: chunked'` -> (0,7,'Host: a'). Draft expects "two host: lines -> no". Both shorter-span escapes confirmed.

### FIXB-1: HOLDS
Text: §2.2 L461-462 "both EXTENSIONAL over rx operands: membership depends only on the language, so two spellings of one language behave the same under `&`, `|`, `!`"; §3.4 L825 "EXTENSIONAL (`& | !`, comparisons, filter modifiers) depend only on the language"; L25 (L200) "SAME under `& | !`". §4.5 L1043-1047: a condition reads PCRE's own parse of the value. Run (f.py): `(?<a>\d+)(?<b>\d+)` on `123` ANCHORED|ENDANCHORED -> a=(0,2); `(?<a>\d+?)(?<b>\d+)` -> a=(0,1) (python re same: (0,2) vs (0,1)); the two are one language and one label relation, so `P1 & (a:"1")` rejects, `P2 & (a:"1")` accepts. Union order: `(?|(?<l>a)a|(?<l>aa))` on `aa` -> l=(0,1); swapped `(?|(?<l>aa)|(?<l>a)a)` -> l=(0,2). The text states no consequence for conditions.

### FIXB-2: HOLDS
Quoted §4.2 L924-933: REPEATED = "its group can be set more than once (a group under `*`, `+`, ...)"; "A REPEATED label with ZERO iterations is NOT unset ... a plain condition HOLDS over none ... `*` admits zero iterations, `+` does not." Hand execution on value `x`, condition `(n:<5)`: `/x|(?<n>\d)/` n set once, unset -> FAILS; `/x|(?<n>\d)+/` group under `+` -> REPEATED, zero iterations -> HOLDS (though `+` "does not" admit zero); `/(?:(?<n>\d)+)?x/`, `/(?:(?<n>\d)+)*x/` same HOLDS; `/(?<n>\d)?x/` FAILS. libpcre2 on `x` for all five patterns: n = None (unset) in every one (f.py B2), so PCRE draws no distinction; the HOLD is a layer the text does not call out.

### FIXB-3: HOLDS
Text L590-591: `(m: contains(/ab(?<g>[xy])/) & (g: "x"))` "means 'every hit has g = x'". libpcre2 on `abx aby`: rev 8 body `(?s).*ab(?<g>[xy]).*` -> g=(6,7) `y` (an existing parse with g=x is what rev 8's some-parse admitted); rev 9 loop body hits: first hit abx (g=x) and last hit (4,7)=aby (g=y) -> every-hit condition rejects; argument-side `(?s)(?:.*?(?<hit>ab(?<g>x))){1,}.*` -> matches (0,7), hit (0,3) (accepts). So the operand-side vs argument-side pair differs and rev 9 vs rev 8 answer moves; L58 (L233) says only "accepted the same values" (not re-quoted here; critic's quote taken from fixB, L58 cited at L586-593 which I read).

### FIXB-6: HOLDS (text only)
O57 L2441-2442: "the ambiguous population is counted twice, by the ambiguity check and by a libpcre2 differential that finds a witness with two accepting parses (K35)"; §0 L345-347: "an independent... libpcre2 differential that finds a witness string whose PCRE parse differs from another accepting parse". Neither names where the second accepting parse comes from (grep 'second parse|another accepting parse|two accepting parses' finds only L347, L1748, L2442; none names a source). It also forbids the rejecting callout in L2436 for the answers ("never a rejecting callout"), so a callout route for counting is neither allowed nor stated.

### FIXB-7(d): HOLDS
§4.5 L1050: "THE CONDITION FILTERS THE PARSE; IT NEVER STEERS IT"; L1397-1399: "when the verify rejects the preferred end the next end must be tried". Runs: `(?<a>\d+)(?<b>\d+)` on `123` ANCHORED|ENDANCHORED -> a=(0,2) (`P & (a:"1")` rejects the span `123`); on the span `12` -> [(0,2),(0,1),(1,2)] a=`1` (python re.fullmatch a=(0,1)) accepts. A search of subject `123` under D196 next-end therefore reports `12`, a span plain PCRE would not report for that pattern: the condition steers the SPAN (not the parse). Draft states "per value" only. 

### FIXA-2 + CENSUS-10 (`[n]` after a label path): PARTLY
Text, two meanings of `[n]` after a label: §3.2 L786-793 "`X[...]` = POSITION in the array interface only ... Indexing reads a SPELLED array at compile time (§3.4); on a repeated label's iterations (`$m.hit[2]`) it reads ONE iteration"; §4.3 L951-952 "`alt.x[1]` (first in the PATTERN, compile time) differs from `$x`"; §4.3 L989-995 `$x[2]` = iteration 2, `(x[2]: S)` = test on one iteration. So the draft states both and ties them to the two spellings (`alt.x[..]` structural vs `$`/condition iteration), but never states the deciding rule, and `$m.hit[2]` is itself a path through a binding m, so "path through a binding = groups" does not decide. Oracle on the critic's repro: `(?J)(?:(?<x>a)|(?<x>b))+` on `ba` ANCHORED|ENDANCHORED -> [(0,2),(1,2),(0,1)]: group 1 (the `a`-branch, first x in the pattern) = `a`; iteration 1 of x = `b` (group 2 = (0,1)). So `alt & (x[1]:"a")` is true under "group", false under "iteration"; confirmed that the readings differ, and the text decides it only implicitly (by prefix). FIXA-2's `P.x[2]` rev-7-vs-rev-8 clash is therefore real in wording, partly settled by context.

### FIXA-3 + CENSUS-1 (`$` on a repeated label): HOLDS
Quoted: §5.4 L1281 `$` = "the CAPTURED STRING of the whole path"; §4.1 L869 `$x` = "the CAPTURED STRING of this match (a one-string set, context-free)"; §4.3 L947-948 "a bare `$x` on a repeated label is an ERROR ... At `vm`, `$x` is PCRE's last iteration"; vs §2.6 L662 / §4.3 L990-991 `$m.hit & (g: "x")` "keeps iterations 1 and 3 with their positions" at the `captures` level. `hit` is a repeated label (L563), so `$m.hit` unindexed is exactly L947's bare case; the only statement of a captures-level meaning of unindexed `$` is the example itself (grep of 'captures level' lines 660-661, 792, 991, 1281, 1776, 2104, 2355, 2422: all indexed uses or this example). Levels are separate switches, so vm gives `abx` (last iteration) against "iterations 1 and 3".

### FIXA-4: HOLDS
Text: L50 (L225) and O54 (L2405-2407) "laid against the search pattern's GROUPS (the map interface), x and y REPEATED labels"; §3.1 L751 "Map order = PCRE group number"; body L563 puts `(?<hit>${x})` around the argument. `re.compile(r'(?s)(?:.*?(?P<hit>(?P<a>\d)(?P<b>\d)))*.*').groupindex` -> {'hit': 1, 'a': 2, 'b': 3}. Group order is hit, a, b, so a positional record over the search pattern's groups binds x = hit, y = a unless the argument's groups are named (the text says "the search pattern's GROUPS", not the argument's).

### CENSUS-2: HOLDS
Text: §5.4 L1251-1252 "Inside `/.../` none of this applies: rx text has PCRE's meaning (`\d{1,3}`, `(?<y>...)`, `[^,]`, `/${p},${p}/`)"; the last is a hole. G3 (L1618-1620 and §0) "a one-literal program IS EXACTLY TODAY'S PCRE PATTERN". libpcre2 `pcre2_compile_8('x${num}')` -> compiles (no COMPILE-ERR; matches nothing on `x`, so `$` anchor then literal `{num}`); `(\d+)&${ <256 }` also compiles. So `${` is valid PCRE text with PCRE meaning and also a hole opener. C23 L2111-2115 weighs only `&`.

### CENSUS-3: PARTLY
Text: §5.4 L1282 `${ }` = "a HOLE: inserts an rx's set as one entry (§3.3, §11)". Typed positions: the table row omits them, but §11 L1684-1685 states "holes in typed SYNTAX POSITIONS (`\d{${n}}`, `[${a}-${b}]`) supply that position's type from a finite set" (so meaning 2 is defined, in §11, and `{${min},}` at L563 is that case). Name splice: `capture(x) := /(?<${x.label}>${x})/` (L1236) and `(?<f_${i}>${x})` (L1241) paste into a group NAME; §11 L1685 states "holes never change structure seen outside" and no section defines a hole in a name. Meaning 3 confirmed undefined; meaning 2 only misplaced from the table.

### CENSUS-4: HOLDS
`search(x, min = 0) := ...` at L563/L1529. §5.4 `=` row (L1264) "`name = e` as an entry of `[ ]` or of a call record"; §5.2 L1197-1199 "In phase 1 a definition head declares NAMES only (`m(p1, p2) :=`)"; L1181-1183 says keyword arguments are "OPTIONAL SETTINGS with defaults" but no text says where a default is written. The head `min = 0` is neither a name nor a call record entry.

### CENSUS-5: HOLDS
L1939-1940 `value_depth(0) := json.scalar` / `value_depth(k) := ...`; §5.4 `(` row (a) "a definition head `m(p1, p2) :=`, which declares them"; §5.2 L1198 "names only"; L1219 "Overloading: LEAN, NOT phase one (CF:163)"; §5.1 L1181 "ONE kind of binding: `name := expression`"; O21 L2165 admits the several-definitions form. `value_depth(k: 0)` would be a `:` in a head = the L49 error (L1199). The literal-argument head is outside the stated head rules.

### CENSUS-15: HOLDS
Text: §5.3 L1229 "over several arrays it ZIPS by position"; L1239-1241 "the ordinal is a PARAMETER the macro declares (`capture(x, i) := ...`); `each` passes it as the second argument when the macro takes one." For `pair(x, y)` with `each(pair, A, B)`: zip rule fills (A[k], B[k]); ordinal rule ("passes it as the second argument when the macro takes one") also claims slot 2 (pair takes two). No sentence orders the two rules (§5.2's positional rule covers only caller arguments, L1181-1183). Text-only confirmation.

VERIFY COMPLETE
