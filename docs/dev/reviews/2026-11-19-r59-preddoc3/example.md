# Critic example findings (round r59 preddoc3)

## Findings


### EXAMPLE-1  CONFIRMED  severity: doc  effort: S
where: core.md lines 270, 281, 297, 437, 574, 762, 808, 818; library.md lines 165, 187, 197, 206, 214, 234, 272, 297 (tags core/patterns/atomic, core/patterns/lookaround, core/labels/labels-vs-captures, core/conditions/two-valued, core/values/number-domain, core/holes/class, core/holes/empty, lib/search/occurrences, contains, contains-by-occurrences, starts-with, ends-with, anchored, lib/sets/prefix-in, lib/strings/join)
what: the FIND-ALL witness cannot separate FIND-ALL from SEARCHED: its report list has ONE item, and the first match of the same subject is that item (or the gap-body programs `.*`-swallow the whole subject, so SEARCHED and FIND-ALL both report the one stretch). An implementation whose FIND-ALL stopped after the first match prints identical answers on these lines. Also WHOLE witnesses with only HOLDS (no FAILS): core 325(2 texts, ok), 590, 607, 637, 648, 661, 662, 674, 675, 784, 846, 952; lib 30, 214, 222, 252, 315, 341, 405 (a WHOLE that ignored whole-ness passes); WHOLE with only FAILS: core 546, 574.
evidence: script /var/tmp/pcrec-pcrec/scratch/crit-preddoc3/example/ (inline python in the session): for every 3-mode line (65 core, 27 library) count items in the FIND-ALL list -> 8 core + 9 library lists with <=1 item (library 178 has 0 items and S also FAILS, a legitimate all-fail row). Reproduce: python3 -I regex over `' / FIND-ALL '` lines, count backticked `@n` items.
proposed fix: for the lines above choose a FIND-ALL subject with a second non-overlapping match (e.g. `ax ab ab` for a[^xy], `25 13 14` for atomic, `err1 err2` under a NON-gap program), or say in the line that the mode is the same as SEARCHED for a gap body. Low priority: the answers are right.

### EXAMPLE-2  CONFIRMED  severity: doc  effort: S
where: parked.md pieces parked/ideas/default-set (item 3), default-range (item 11), macro-warning (item 12), zero-loop-default (item 7), field-count (item 8); future list items 3, 7, 8, 11, 12 ("SUPERSEDED IN PART 2026-11-17", future.md lines 43, 172 etc.)
what: the SUPERSEDED-IN-PART notes of the future list are carried only into parked_details.md (lines 61, 124, 174, 237, 262), not into the base piece. The base file a session reads whole still states: default-set "A default written `some(...)` / `all(...)`" (`all` RETIRED, all-question 23:18); default-range's idea ("restrict a default to the values the label could hold") was ANSWERED by default-value (21:49, any text, warning only on a never-used default); macro-warning's Trigger still says "beside the mark-in-none one" (mark-in-none retired with the mark).
evidence: parked.md lines 25-26, 75-77, 81-83 vs future.md lines 43-52, 172, and parked_details.md lines 61, 237, 262.
proposed fix: add one clause to each of the five base pieces ("partly superseded 2026-11-17: `all` and the mark are retired; see details") so the base reader is not misled about a retired name.

### EXAMPLE-3  CONFIRMED  severity: maintenance  effort: S
where: parked.md parked/ideas/place-table-skeleton (item 22), parked/ideas/label-parameter (item 26), parked/ideas/rx-module (item 21)
what: three triggers are paraphrased, not copied. Item 22: future "the owner's answers to rev 24.1's §R.8 questions (the table's open cells), or the next full revision of §R" -> parked "the owner's answers to the place table's open cells, or the next full revision of the nested-place sections" (the revision named changes from §R to "the nested-place sections"). Item 26: future "the first revision of the draft after rev 25 that takes up reusable conditions. NOT in lane predspec25's scope" -> parked "the first revision of the definition that takes up reusable conditions" (the "after rev 25" bound dropped). Item 21: future has NO trigger line (its NEXT is "a design note (lane rxlib), then the owner"), parked agrees ("none recorded") but also says "taken up as core/patterns/sequence and lib/rx", a status the future list does not record (an item leaves the list only by owner decision, future.md line 4).
evidence: future.md 394, 582, 364-380; parked.md 150-153, 177-180, 143-147.
proposed fix: copy the two triggers' wording (or mark the paraphrase), and say for item 21 whether the owner took it up (cite the record) or drop "taken up".

## APPENDIX A: example sample (EXAMPLE sub-part 1)
Method: scripts /var/tmp/pcrec-pcrec/scratch/crit-preddoc3/example/eng.py (a small path-enumerating engine: seq, alt, opt, star with the "branching resets labels" rule, grp, cond, lookahead, read, backref; modes WHOLE = some path spans the text, SEARCHED = first path at the leftmost start, FIND-ALL = PCRE global loop with the retry-non-empty-then-step rule) and run.py (92 cases). Run: `timeout 120 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc3/example/run.py` -> "TOTAL 92 DIFF 0". Sabotage check: run_sab.py edits two expected FIND-ALL lists and run.py's harness reports exactly those two as DIFF (the harness is live). Regex-shaped values (no condition) use python `re` fullmatch / search / finditer directly; programs with conditions were hand-translated to the engine (the engine implements the PIECES' stated model, so it checks the printed answers against the piece's own rules, not an independent oracle) or to an equivalent plain regex stated in each case's note. Holes were expanded by hand to the regex the piece itself prints.
Every case is run in all three modes (WHOLE with every printed text; SEARCHED one text; FIND-ALL one text) = 92 programs, 92 x 3 mode lines, longest witness `abcdefghij-10` / `99945999 999450999 9997999` (26 chars).
Tags (file:line  piece): core 124 model/match; 140 model/modes; 150 model/table; 192 places/outermost-view; 210 literals; 221 flags; 233 sequence; 243 alternation; 260 quantifiers; 270 atomic; 281 lookaround; 297 labels-vs-captures; 313 one-rule; 325 flow; 343 export; 352 caller-ambiguous(open); 363, 364 paths; 378 backreferences; 396 numbers; 404 numbers/in-loop(open); 421 form; 437 two-valued (+ the 3x3 table lines 430-434); 446 in-sequence; 461 match-so-far; 469 pass-start-read; 479 defaults; 496 and; 513 complement; 528 kinds; 546 reads; 563 one-type; 574 number-domain; 590, 591 arithmetic; 607 functions; 623 lift; 637 enumerate; 648 class-order; 661 class-positions(open, C1 only partly reconstructed); 711 holes; 727 count; 733 name; 749, 762 class; 772 range-end; 784 flag (both o="i" and o=""); 803, 818 empty; 836 or; 846 flags; 856, 897, 902 in-filter; 871 same-name; 882, 889 bare-condition; 907 no-hole; 932 and 952 holes. library 29, 30 padded; 49 quoted; 61 any_case(open, candidate body); 84 length; 92 month_numbered; 109 peek; 123 when; 136 when-test; 165 occurrences; 178 hits; 187 contains; 197 contains-by-occurrences; 206 startsWith; 214 endsWith; 222 endsWith lazy; 234 anchored; 252 anything; 262 between; 272 prefix_in; 297 join; 307 left; 315 strlen; 341 list_of; 369 rx classes; 384 rx.repeat; 405 capture. = 68 piece-example lines (core 50 across all sections: model, patterns, labels, conditions, filters, values, arrays, holes; library 22 across modifiers, control, search, sets, strings, records, rx, structural) plus the 3x3 table, ruling-lines counted once each.
Result for (i): printed answer equals my run on all of them. (Two checks beyond answers: endsWith greedy n=`3` and lazy n=`123` on `ab123` confirmed with python groups; `enumerate(/(?:a|ab){1,2}/)` priority list equals the printed alternation.)

## APPENDIX B: against the frozen draft (sub-part 1 (ii))
Method: grep -F of each subject string in predicates_draft.md, then read the matched line. Draft lines whose printed answers equal the piece's: 1080 (243), 1005 (496/140: `a12 1` -> `1`@1), 1114 (281), 1141 (437), 1253 (469 `3;7;4;` FAILS, SEARCHED `3;7;`@0), 1344 (297), 1358 (313), 1419-1421 (192; the draft prints other FIND-ALL subjects, SEARCHED `3;,,` matched at `3;,`@0 equal), 1675 (325), 1685 (363), 1746/1789 (343), 1824/1833 (546, PCRE capture vs label told apart), 1924 (396), 1944 (233), 1963 (711), 2074 (727), 2105 (260), 2107 (932), 2444 (836), 2522 (607), 2550 (574), 3017 (648: the draft itself says CLASS ORDER moved `x10` `1`@1 -> `10`@1 and FIND-ALL [`10`@0, ...]; the piece prints the moved answer), 3394 (404 label reading), 3415/5550 (padded width form: `0129`@1, [`0129`@0, `0000`@5]), 2587 (strlen: the draft prints it as `length($y)`, same answers; renamed strlen by r52 K), 6942 (endsWith lazy n=`123`). 871 same-name: the piece prints another subject (`/(?<h>a)-${q}\k<h>/`, q := `/(?<h>b)/`) than the draft's rev 28.1 row A30 (`a-bb` HOLDS, reversed); the piece follows the record "same-name-count: scoped" (record 4642-4667, its MANAGER CORRECTION), consistent with draft line 2215/2236 (WHOLE `a-ba` HOLDS). Differences found: none. Not printed in the draft (so only (i) applies): 61, 84(`abcdefg`), 92, 109, 123 table row printed at draft 1549 (equal), 165, 178, 187, 197, 206, 222, 234, 252, 262, 272, 297, 307, 341, 369, 384, 405, 590/591, 623, 637, 648 FIND-ALL, 749-818, 846, 856-907.
No record entry from 4834 onward was needed to excuse a difference.

## APPENDIX C: parked coverage (sub-part 2)
Method: python -I script extracting `TRIGGER` lines of each `## n.` item of predicates_future.md and the `Trigger` line of the n-th `### ` piece of parked.md (pieces appear in item order; 39 pieces: 38 + never-constant).
| item | piece tag | trigger present | agrees |
|---|---|---|---|
| 1 | first-rest | yes | yes (verbatim) |
| 2 | partial-transforms | yes | yes |
| 3 | default-set | yes | yes (base stale on `all`, EXAMPLE-2) |
| 4 | tuple-apart | yes | yes |
| 5 | unset-member | yes | yes |
| 6 | empty-value | yes | yes |
| 7 | zero-loop-default | yes | yes |
| 8 | field-count | yes | yes |
| 9 | label-twice | yes | yes |
| 10 | explainer | yes | yes |
| 11 | default-range | yes | yes (base stale: ANSWERED by default-value, EXAMPLE-2) |
| 12 | macro-warning | yes | yes (mark-in-none retired, EXAMPLE-2) |
| 13 | nested-relation | yes (3 triggers) | yes |
| 14 | match-then-judge | yes (3) | yes |
| 15 | spelling-check | yes | yes |
| 16 | place-table | yes (3) | yes |
| 17 | ordered-table | yes (3) | yes |
| 18 | kleene-completion | yes | yes |
| 19 | atomic | yes | yes |
| 20 | capability-optins | yes | yes |
| 21 | rx-module | none recorded (future has none) | yes, but "taken up" claim (EXAMPLE-3) |
| 22 | place-table-skeleton | yes | paraphrased, drifted (EXAMPLE-3) |
| 23 | severity-table | yes | yes |
| 24 | user-doc-traps | yes | yes |
| 25 | label-hygiene | yes | yes |
| 26 | label-parameter | yes | paraphrased, bound dropped (EXAMPLE-3) |
| 27 | cartesian | yes | yes |
| 28 | count-filter | yes | yes |
| 29 | assert | yes | yes |
| 30 | string-level-rx | yes | yes |
| 31 | match-is-rx-unlocks | yes (U1-U6, 6 triggers) | yes, all six present |
| 32 | label-only-group | yes | yes |
| 33 | array-in-hole | yes | yes |
| 34 | restricted-parameter | yes | yes |
| 35 | class-base | yes | yes |
| 36 | limited | yes | yes |
| 37 | known-nothing | yes | yes |
| 38 | warning-rows | yes | yes |
All 38 items have a piece; 37 carry a trigger (item 21 has none in the source either); 35 verbatim, 2 paraphrased with drift (22, 26). The 39th piece (never-constant, trigger none) is from the record, not the future list.

## PROBED-AND-HELD
- 92 example programs (68 piece lines + 3 table lines + repeats of modes), core 50 pieces across all 8 sections and library 22 across 7 sections: printed WHOLE/SEARCHED/FIND-ALL answers all equal my runs (0 differ); 3x3 two-valued table equal.
- Draft comparison: about 30 draft-printed subjects checked, 0 differences (the class-order move at draft 3017 is in the piece).
- Parked: 38 of 38 items have a piece; 37 of 38 triggers present and 35 verbatim; item 31's six unlock triggers all present.
- Harness sabotage: 2 edited expectations caught (2 of 2).

CRITIC COMPLETE
