# verify: predspec10

## Verdicts

### SIMULATE-1: HOLDS
Draft:1893-1894 says a filter applied directly is anchored at both ends (`m & /^err$/` = `m & /err/`); 1904 sets `^`/`$` as the string's own ends; no sentence leaves the right end open for `^` alone. Ran `whole '^foo' foobar` -> None; `whole '(?:foo)(?s:.*)' foobar` -> [(0,6)]; `whole '^5' 57` -> None vs startsWith form [(0,2)]; `whole '^dead\.' dead.x` -> None vs startsWith [(0,6)]; `whole '^S\w*' S-1` -> None vs `(?:S)(?s:.*)` [(0,3)]. Draft:1898 and L41 (draft:250), L13, L15 say SAME/"words that start with foo". Contradiction confirmed.

### SIMULATE-2: HOLDS
Draft:711-712 refuses "a pattern whose backreference or conditional names a group of the SAME hit", which covers `(.)\1`. Ran `whole '(?:(?s:.*?)(?<hit>(.)\2)){0,}(?s:.*)' aabbcd` -> hit (2,4); `all '(.)\1' aabbcd` -> (0,2),(2,4): last hit equal. E-SEP's `\d{4}([-\/.])\d\d\1\d\d`: loop last hit (28,38), find-all last (28,38). The refusal is broader than the stated reason (earlier-iteration visibility); draft:651 does list `/(.)\1/` as a raw-splice case, as stated.

### SIMULATE-3: HOLDS
Draft:752-753 says no row has a top-level `|`; row at draft:763 is `/aab\|a/`. Ran `whole '(?:(?s:.*?)(?<hit>aab|a)){0,}(?s:.*)' aab` -> hit (0,3); `{2,}` -> hit (1,2): answers stand, the stated reason is wrong for that row.

### CENSUS-1: PARTLY
Quoted draft:369, 495, 781-790, 1006, 1140-1142, 1484, 1930-1932: all say captured string = one-string set, context-free; 788 says "`.g` a label inside that entry" and 1141 "`$` covers the whole path". No sentence says a `$` entry of a repeated label carries labels or positions; the draft's 1648-1650 gives only an ITEM precedent. So the unstated carrying and the two parses are real. But "label-free" is not stated either ("context-free" is not "label-free"), so a contradiction is overstated; it is an unstated structural effect.

### CENSUS-2: HOLDS
Draft:1861-1863 and 1453-1455 say "exactly two"; draft:1853-1854 and 1642-1644 give `(?&name)` as a crossing. Ran `search '\((?:[^()]|(?&balanced))*\)' '(a(b))'` -> compile error "reference to non-existent subpattern"; with a named group -> [(0,6),(0,6)].

### CENSUS-3: HOLDS
Counts rerun: `grep -rhE '^pattern .*&' ...| wc -l` = 165; `'^pattern .*\(\?&'` = 154. Ran `search '(?<a>x)(?\&a)' xx` -> compile error "unrecognized character after (? or (?-"; `search '[a\&b]' '&'` -> [(0,1)]. Draft:1874-1878, 187 say "everywhere" and no position-dependent reading; O60 (B) draft:2853 does not name `(?&`. (The 11 non-`(?&` lines include class and callout-C-code `&`, not only 11 literal ampersands.)

### CENSUS-4: HOLDS
Draft:1864-1868 "So the exception takes no matchable PCRE meaning away", "in every position (... a class ...)". Ran `search '[${]x' '{x'` -> [(0,2)]; `search '\Q${\E' 'a${'` -> [(1,3)]. Pattern positions: `x${num}` vs `x{num}` -> None; `x${0}y`, `x${0,1}y`, `x${,2}y`, `x${2}` all compile errors.

### CENSUS-5: HOLDS
Draft:573-575, 1943-1945 describe `(\d+)&${ <256 }` as a guard on an atom ("a hole after an atom WITHOUT `&` is a FOLLOWING item"); draft:1874-1875 and 555 give `&` D196 precedence "concatenation, then `&`, then `|`". Applying the rule, `/port=(\d+)&${<256}/` = `/port=(\d+)/ & <256` (empty), not an atom-scoped guard; no sentence scopes the guard to the atom, and O60 (B) draft:2853 says "works as written". Rule application only (no oracle, `&` is not PCRE).

### CENSUS-6: PARTLY
(a) REFUTED: the quoted sentence ("REV 8: the owner chose (C) ... In the DESIGN the item stays OPEN with no reading chosen: (A) and (B)...") is at draft:2655-2656 inside O48's body (O48 opens at draft:2647), where it is correct; draft:2583-2588 is the end of O40 (which says "RESOLVED in rev 10 ... as its lean said") and the start of O41 (`sed -n 2583,2590p`). (b) HOLDS: O50 (a) draft:2672-2675 still says "the MANAGER'S LEAN, CF:924-926; LEAN" beside the "RULED in rev 10" at 2689-2690. (c) HOLDS: C23 is in the RESOLVED list (draft:2367) and sits under "STILL OPEN (contradictions):" (draft:2391, 2430-2431, "RESOLVED in rev 10"). (d) HOLDS: O39 RESOLVED (no fixed thresholds) vs E-NEAR (c) draft:2171-2172 "at the default level a compile error printing the count" and draft:2212 "within any budget"; only §4.6 (draft:1298, 1311) marks its tiers LEAN/illustrative, not the §12 expectations.

### CENSUS-7: HOLDS
Recounted over the 4-space code lines of §12.1-12.12 (own script, `verify/c.py`, rx literals and strings stripped). `${` holes: E-JSONL 1, E-DEPTH 2, E-HTTP 1, E-CTX 1 (row draft:1485 names E-JSONL, E-DEPTH, E-IPV4 only). `@`: E-IPV4, E-CAL, E-CTX (row 1487 omits E-CTX). `/.../`: E-CAL none (draft:2130 `# isodate as in 12.2`). `,` outside rx/strings: none in E-LUHN, E-DEPTH, E-CTX. Strings/numerals: none in E-SEP. `+`: absent in every block, not in the TWO-WAY CENSUS rows (draft:2052-2069), draft:1481 lists only `-`, `*`, `%`.

### CENSUS-8: HOLDS
CF:972-973 item (1) reads "reading ONE hit needs captures"; draft:784-786 marks all three last lines (`$m.hit[2]`, `$m.hit[2].g`, `$m.hit & (g: "x")`) "RULED BY ACCEPTANCE, CF:972-973" and draft:1484 puts `$m.hit` inside the RULED parenthesis, while only "one meaning at every level" is marked LEAN. Over-reach for every-iteration `$` and for selection is as stated; the draft already marks bare `$x` LEAN at draft:1166.

### CENSUS-9: HOLDS
Draft:299-300 reads "L55, L56 and L36's zero-iteration clause LEAN RULED BY ACCEPTANCE (CF:997-1000 ...)" and "L65 RULED with them (review r10 picks, this document)"; draft:265 still says "unset fails: LEAN, CF:173" and draft:1079 opens "LEAN (CF:173)" while draft:1084-1085 says RULED BY ACCEPTANCE; CF:997-1000 ("Agree with lean") is the never-reached rule.

### CENSUS-10: HOLDS
Draft:375-376 make `search`/`contains` transforms that are not modifiers; draft:455 and 537 still say "a transform is a filter modifier"; draft:377 says search/searched are "not used for each other" while draft:228, 1231, 1673, 2113, 2189, 2458 say "search mode" / "SEARCH program" for the mode.

### CENSUS-11: HOLDS
Draft:1484 and 369 define `$` as captured strings; draft:1484 itself reads `$mname.index` (11 for `Nov`) and draft:1190-1191 says read computed labels "with `$` like any label" (`$d`, `$wd`); draft:381 calls `.index` metadata. Neither is captured text.

### CENSUS-12: HOLDS
Draft:1094-1099 gives two rules for `$x` (every iteration for a repeated label; lowest-numbered set group for duplicates); draft:273 L64 uses a label that is both. Ran `whole '(?J)(?:(?<x>a)|(?<x>b))+' ba` -> [(0,2),(1,2),(0,1)]: group 1 `a`@1, group 2 `b`@0.

VERIFY COMPLETE
