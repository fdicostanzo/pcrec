# fixA findings

## Findings

### FIXA-1 (CONFIRMED; design; effort S) `search` as a "transform" breaks the ruled NAMING RULE, or gives "transform" a second meaning
Rev 8 made search "a LIBRARY TRANSFORM" (§2.6 L554, §0 L122, §1 L358); rev 7's glossary (§0.3 L313) says
"**transform** (= **filter modifier**) | a macro filter -> filter (§2.7)", and §2.7 L718-720 (RULED CF:727-728, his
words) says "a modifier's name describes the SUBJECTS IT ACCEPTS (an adjective or phrase ...), never a verb acting on the
subject". `search` is a verb, and `search(x)` (min 0) accepts EVERY string, so its name describes nothing it accepts.
Nor is it §2.7's mechanism: "the pullback of S under the modifier's READING t" (L706) does not produce an rx "in which
the hit group REPEATS" (L555). Either (a) search is a filter modifier and its name breaks a RULED rule (and §0 L88's
"one NAMING rule ... a transform's name describes the subjects it accepts"), or (b) "transform" now names two things
(the pullback modifiers and a label-adding library macro), against §0.3's "one word per thing" and G0b. The owner's
own word is "transform" (CF:903, CF:929), so the fix is a sentence saying which: e.g. §0.3 splits "transform" (any
macro filter -> filter, search included) from "filter modifier" (the pullback, the naming rule), or the naming rule
is stated as covering modifiers only. Blast radius: §0 L88, §0.3 L313, §2.6, §2.7, §8 L1529.

### FIXA-2 (CONFIRMED; design; effort M) `[n]` after a label path has two meanings: static entry (rev 7 `$` path rule) vs iteration (rev 8)
§3.2 tool 1 L786-793: `X[...]` = "POSITION in the ARRAY interface only" (an rx's top-level alternatives), "Indexing reads
a SPELLED array at compile time"; §4.3 L951-952: "`alt.x[1]` (first in the PATTERN, compile time) differs from `$x`".
Rev 7's `$` rule (§5.4 L1281, P6-6): "`$a.b.c` = `$(a.b.c)`", the captured string of the WHOLE path. Rev 8 then gives the
same bracket after a label the ITERATION meaning: `$x[2]` "the captured string of iteration 2", `$m.hit[2].g`,
`(x[2]: S)` a test on iteration 2 (§4.3 L989-995, §13 O56 (2), §2.6 L660-661). Applied literally to
`P := /(?:(?<x>a|b),)*/`: by §3.2/§4.3 `P.x[2]` is the second ENTRY of x's pattern (`b`), so `$x[2]` = `$(x[2])` = the
captured string of the `b` branch; by rev 8 it is the text of iteration 2 (`a` on `a,a,`). `(x[2]: "a")` on `a,a,`:
iteration reading holds; static reading constrains a path whose pattern is `b` (empty / dead branch). Neither rev 7's
§5.4 `[ ]` row nor rev 8's §3.4 SPELLED-vs-ITERATIONS paragraph says which wins after a label that both repeats and has
alternatives. G0b ("one meaning each") fails for `[ ]` as the index bracket. Fix: state that after a REPEATED label `[n]`
indexes iterations (and `alt.x[1]`'s static reading needs another spelling), or the reverse. Blast: §3.2, §4.3, §5.4
`$`/`[ ]` rows, O56, §2.6 owner's example.

### FIXA-3 (CONFIRMED; design; effort S) `$m.hit` (no index) on a repeated label: "every iteration, positions kept" (rev 8) vs "a one-string set" / "PCRE's last iteration"
Rev 8 added `$m.hit & (g: "x")` = "iterations 1 and 3, positions kept" (§2.6 L662, §4.3 L990-991, C17 L2103-2105).
Elsewhere `$x` is "the CAPTURED STRING of this match (a one-string set, context-free, §11)" (§4.1 L869, §0.3 L307), "a
bare `$x` on a repeated label is an ERROR" at the default level, and "At `vm`, `$x` is PCRE's last iteration (what
`\k<x>` sees)" (§4.3 L947-948). Applied to the owner's value `abx aby abx`: under the vm rule `$m.hit` = {`abx`} (hit 3),
so `$m.hit & (g: "x")` keeps one string, not "iterations 1 and 3"; under §4.1 a one-string set has no "positions". The
captures-level reading of unindexed `$` on a repeated label is stated nowhere, so `$` gets a second meaning only in this
example. Fix: spell the selection without bare `$` on the repeated label (e.g. a structural tool over iterations, which
§3.4 L838-840 currently forbids, or `$m.hit[...]` with a filter index), or state the captures-level meaning of `$x` on a
repeated label and reconcile it with the vm rule. Blast: §2.6 owner's example, §4.3, C17, O50 (a).

### FIXA-4 (CONFIRMED; design, design-only form; effort S) L50/O54's lean (a positional record over a search's groups pairs x with a, y with b) is broken by rev 8's own `hit` group
Rev 8 L50 (L225) and O54 (L2405-2407): `(x, y) := $m & search(/(?<a>\d)(?<b>\d)/)` is "laid against the map interface
(groups); x and y are then REPEATED labels, one iteration per hit". §3.1 L751: "Map order = PCRE group number"; O41
L2270: `(x) := r` "lays x over r's first group". Rev 8's body (kept in rev 9, §2.6 L563) puts `(?<hit>${x})` around the
argument, so the rx's map interface in group order is hit, a, b (python3 `re`: groupindex {'hit': 1, 'a': 2, 'b': 3}).
A positional record laid by that order binds x = hit (`12`-style two-digit hits) and y = a, not x = a, y = b as the lean
intends. Fix: say the record is laid against the ARGUMENT's groups (excluding the library's `hit`), or by name. Ties
to O55 (the hit label). Blast: L50, O54, O41's "first group" rule.

### FIXA-5 (CONFIRMED; doc/G0b; effort S) Rev 7's mark-table `[ ]` row names `count` as a STRUCTURAL tool over entries; rev 8 made `count(c)` the group question over ITERATIONS
§5.4 L1259 (`[ e1, e2, ... ]` row, rev 7): "Under structural tools (indexing, `each`, `join`, `count` of entries, §3.4)".
Rev 8 defines `count(c)` = "the NUMBER of iterations meeting the condition c" (§4.3 L967, §8 L1547), a group question
that is NOT a structural tool (§3.4 L838-840: structural tools never read iterations; §4.3 L996). No structural
`count` over spelled entries is defined anywhere (§3.4 L826 says only "entry counts"). So the code-font name `count`
carries two meanings (entries of a spelled rx vs iterations meeting c), against G0b. Fix: say "the entry count" in the
row (no name), or define one `count` and say how it reads a spelled array. Blast: §5.4 `[ ]` row only.

### FIXA-6 (CONFIRMED; doc, status mark; effort S) TWO-WAY CENSUS marks `count(...)` RULED; §8, L42 and C21 mark it LEAN
§12 census L1771 (rev 7): "`count(...)` | none in code | RULED as the first spelling (CF:823, CF:832)". CF:823 is headed
"RULING (lean)" and his words are "perhaps the solution is both"; §8 STATUS L1577-1578: "`count()` first, `occurs` the
fallback: LEAN (CF:823, "perhaps the solution is both")"; §0.1 STATUS L247: "L42: LEAN (CF:823 "perhaps"; the budget
rule RULED, CF:832)"; C21 L2016: "LEAN (CF:823, "perhaps")". CF:832 rules only WHEN count gives way (by budget), not that
count is the first spelling. One construct, two status marks; the census overclaims. Fix: "LEAN (CF:823); its budget
refusal RULED (CF:832)". Same census, L1782 (rev 7): "`*`, `%` | RULED in kind (arithmetic, CF:782 (1))": CF:782's
words are "\d+ numbers can be added, filtered <256" (addition only); `*`/`%` rest on the manager's reading (LEAN).

### FIXA-7 (CONFIRMED; doc, stale; effort S) Rev 8's "What remains open is only the [metadata] collision (§13 O31)" vs rev 9's decision and O31's remaining question
§3.2 tool 4 L801-802 (rev 8): "What remains open is only the collision of a metadata name with a user label of that
name (§13 O31)". Rev 9 decides it: §5.4 `.` row L1280 "A user label named `index` or `label` is an ERROR naming the
reserved field (rev 9: the manager's call, LEAN)"; §13 DECIDED BY THE MANAGER (2) L2473; and O31 L2211-2213 says what is
"STILL OPEN" is "how a program selects `functions`/`captures`/`vm`/`eval`". So §3.2 and O31 name two different
remainders. Also still routing the collision to O31 as open: §3.1 STATUS L780-781, §5.4 STATUS L1294 ("the metadata
collision: §13 O31"). Fix: §3.2 says "the collision is an ERROR (manager's call, LEAN, O31)".

### FIXA-8 (CONFIRMED; doc, dangling quote; effort S) O31 quotes §9 as "a third resolution rule to `.`"; rev 8 rewrote §9 to "a second resolution rule"
O31 L2202-2203 (rev 7 widening): "§9 cut UFCS for being "a third resolution rule to `.`"; the same argument applies
here." §9 REASONING L1601-1602 (rev 8): "UFCS would add a second resolution rule to `.`, whose ONE meaning is now ruled".
Rev 7's §9 said "third" (c5e1931e1 line 1205); rev 8 changed §9 but not the quote. The quoted text no longer exists.

### FIXA-9 (CONFIRMED; doc, status mark; effort S) §0.1 STATUS gives L53's refusal two owners: rev 8's "this document's LEAN" and rev 9's "the manager's call"
§0.1 STATUS L252-253 (rev 8 sentence, kept): "L53's refusal and L51's error class are this document's LEAN"; L256 (rev
9): "L53's refusal is the manager's call (LEAN)"; L53's own source cell (L228): "the refusal: LEAN (manager, rev 9)";
O53 L2398: "(A) is the MANAGER'S CALL". The rev 8 clause went stale when rev 9 re-attributed it. Same paragraph, rev 7
clause L249-250: "L48-L51 (rev 7): BY DESIGN rows state the rule of the section cited, OPEN/GAP rows their §13 item"
names no ERROR class, yet L49 and L51 are now ERROR rows (rev 8). Fix: drop "L53's refusal and" from the rev 8 clause.

### FIXA-10 (CONFIRMED; doc, mis-cite; effort S) §4.3 cites the group questions' "n+2 states" to CF:62; CF:62 is the nth-countdown note, the n+2 counter is CF:685
§4.3 L986 (rev 8): "GROUP QUESTIONS ... compile to states (a capped counter per question, n+2 states, CF:62's cost
rule)". CF:62 (s.nth(i) with a bounded i) says "a COUNTDOWN carried by the DFA, ~k states for i <= k" and nothing about
n+2. The "capped counter (n+2 states)" is the 2026-11-14 counting ruling, CF:685 (§8 L1543 states it without a cite).
Fix: cite CF:685 for n+2 (CF:62 stays right for O56 (2)'s literal-index test).

### FIXA-11 (CONFIRMED; doc/maintenance; effort S) Smaller stale sentences and case lists from rev 7/8 additions
(a) §11 L1652 (rev 7): "`contains(/^err/)` = `startsWith("err")` although `contains`'s body puts the argument in a hole
after `.*`": rev 9's body is `search(x, min = 1)`, the hole sits after the lazy `(?:.*?` inside the loop (§2.6 L563-564).
(b) O50 (c) L2361 (rev 8): "A search IS a filter (`(m: search(r))`), which never rejects": true only for the default
`min = 0`; `search(r, min = 1)` rejects (§2.6 L624, rev 9).
(c) L48 L223 (rev 7): "`x \| /d/` has 4 (`\|` concatenates arrays)": rev 8 says nothing is an array value (§3.1, §3.4
L840-841); §3.3 says `|` concatenates ENTRIES.
(d) Kind table L427 (rev 7): computed label needed by "E-HTTP (`count`)": E-HTTP's code has no `count` (the census
L1771: "none in code (E-HTTP's prose only)"; §12.9 L1921 prose).
(e) Mark table (rev 7) case lists: the `[ ]` row L1259 lists join inputs in E-WEEKDAY, E-IPV4, E-RFC, E-NEAR, E-SEP but
not E-HTTP (`join([name = token, value = fvalue], ...)`, L1912; the census counts "six cases" for `join`); the `:` row
L1265 omits E-FILE (`rows & (w: >100)`, L1896).
(f) §0.3 L308 (rev 7): "constraint set | the rx after `:` (`x: S`, `m(x: T)`)": `m(x: T)` is an ERROR in phase 1 (rev 8,
§5.2, L49); fine as design text but unmarked.

## PROBED-AND-HELD
- Method: rev 6 (22ec6bf73), rev 7 (c5e1931e1), rev 8 (1d6ba00d2) texts extracted and grepped for each candidate's origin; rev 9 read in full (2539 lines).
- §0.1 rev 7/8 rows L16, L17, L31, L36, L48-L54 (11 rows): every § and O/C cross-reference resolves in rev 9; L52's example (`abx aby abx`, all-hits rejects, some accepts) still holds under the one reading; L53's Python count re-run (`re.findall("a*","baa")` = ['', 'aa', ''], 3); L54/L31/L36 reasons match §4.3. Defects only L48 wording (FIXA-11c) and L50 (FIXA-4).
- CF cites carried by rev 7/8 additions, checked against COND-FAMILY_freeze.md: CF:849, 851-855, 860, 863, 866, 869-870, 873-874, 881-883, 889-892, 895-899, 903-926 (rulings tables, L-rows, §2.6, §3.1, §4.3, §5.4, §7), CF:113 (§7 `(?&name)`), CF:548 (§8 join takes an ordinary array), CF:553, CF:74 (non-overlapping leftmost), CF:180 (rev 8 §15 row): 30+ cites hold; mismatches: CF:62 (FIXA-10), CF:823/CF:782 overclaimed (FIXA-6).
- §0.3 glossary: 21 rev 7/8 rows traced through rev 9; one meaning each except "transform" (FIXA-1) and the `m(x: T)` example (FIXA-11f).
- §2.1 KIND TABLE (9 rows): kinds/status consistent with §2.1 STATUS, §7, O46; one case-list slip (FIXA-11d).
- §5.4 MARK TABLE (7 bracket rows + 12 other marks): one-meaning claims hold except `[ ]` row's `count` (FIXA-5) and the index bracket after a repeated label (FIXA-2); case lists checked against §12 code lines: 2 omissions (FIXA-11e).
- Rev 7 §3.4 SPELLED vs rev 8 ITERATIONS paragraph, §3.2 tool 1 (no `X[0]`), §5.3 `c[1]` is c, §2.1 `(& M)` = M, §2.3/§5.1 macro-in-a-hole (P6-1), §7 records item rx wording, §11 ONE SPAN PER FILTER ROLE vs §2.7 argument span: consistent in rev 9.
- §13 rev 7/8 items O48-O56, C28, O12, O29, C36: RESOLVED/OPEN status consistent with §0.2, §4.3, §5.2; O53 manager's-call relabel consistent except the §0.1 STATUS clause (FIXA-9).
- §12 TWO-WAY CENSUS (16 rows): usage counts agree with §12 code (no `search(`, `some(`, `X[` in code); one status overclaim (FIXA-6).
- §12 examples vs rev 7/8 rules: E-JSONL `contains` under the search body still needs no label read (no `hit` condition); no §12 case violates a rev 7/8 addition.
