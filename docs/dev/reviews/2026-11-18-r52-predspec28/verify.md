# VERIFY predspec28 (review r52): inline by the coordinator

Every CONFIRMED finding was a quote claim or a one-call oracle repro, so the coordinator checked inline (skill §6.2)
instead of launching a verifier agent. Calls: `.coord/v/v1.py` (libpcre2 10.46 via pcre2h, python `re`) and
greps of R/subject (joined lines where the draft wraps). Freeze drift: none (main 482a5044 unchanged; lane/pred-rev28
moved only by a journal/wake commit after 5cb89b91).

| id(s) | check | verdict |
|---|---|---|
| TABLES-3, GENFORM-6 | body `(?:\d{2}|\d{2,3})` vs `\d{2,3}`: SEARCHED `x123` (1,3) vs (1,4); FIND-ALL `123 12345` [(0,2),(4,6),(6,8)] vs [(0,3),(4,7),(7,9)]; `0012|00123` vs `00123|0012` SEARCHED `00123` (0,4) vs (0,5) | HOLDS |
| TABLES-4 | `(?:a|ab){1,2}` SEARCHED `aba` (0,1), FIND-ALL [(0,1),(2,3)]; the model's order alternation (0,3) [(0,3)]; PCRE priority order alternation = the rx | HOLDS |
| TABLES-8 | `(?i:(?:(?-i)ho))` WHOLE `HO` FAILS (the primitive accepts) | HOLDS |
| TABLES-9 | the printed literal without `(?J)` REJECTED "two named subpatterns have the same name"; draft text at §R.7 lacks `(?J)` (grep) | HOLDS (the `(?J)` answer itself: pcre2h's name lookup raises on a duplicate; T20's witness was reproduced by the RULING and TABLES critics) |
| FIXIND-3, MODECLOSURE-3/4 | `(?x)a(?:b#c)d` REJECTED "missing closing parenthesis"; `(?x)a(?:#b\n)c` WHOLE `ac` HOLDS; §11 "NO implicit extended mode" sentence has no REV 28 mark (grep) | HOLDS |
| FIXIND-4, MODECLOSURE-5 | `(?n)(?:(a)\1)` REJECTED "reference to non-existent subpattern"; `(?U)x(?:a+)` SEARCHED `xaaa` (0,2) | HOLDS |
| MODECLOSURE-2, FIXIND-6 | `(?J)(?'h'a)-(?:(?'h'b)\k<h>)` WHOLE `a-ba` HOLDS, `a-bb` FAILS (the outer group bound) | HOLDS |
| MODECLOSURE-6 | `(?:a(?i)b|c)` WHOLE `C` HOLDS, `Ab` FAILS | HOLDS |
| MODECLOSURE-1, GENFORM-1 | operands as own literals on `HO`: `ho`&`h.` FAILS, inherited HOLDS; §11 sentence "An `&` operand ... are not holes" quoted | HOLDS (the counts 4/336/336 and 3/258/258 not re-run) |
| MODECLOSURE-7 | `(?<y>\d+)-(?<=\k<y>-)x` REJECTED "length of lookbehind assertion is not limited" | HOLDS (as a gap: no sentence states the case) |
| TABLES-1, FIXIND-1 | T8 cell holds both "an assertion looking outside): UNDER CONSTRUCTION" and "cannot FILTER ... COMPILE ERROR"; T4 "UNDER CONSTRUCTION needs a DEFINED meaning" (grep) | HOLDS |
| TABLES-2, FIXIND-8 | "UNDER CONSTRUCTION beyond constants, OPEN on a user array" in §2.5 and §5.4's `+` row, no REV 28 mark | HOLDS |
| TABLES-5 | the printed `0 10 007` [`10`@2, `7`@7] for `\d+ + 1` (rev 27.1's PART I) | HOLDS (quote) |
| RULING-1 | record: "(m2) **lift-order** is answered by consequence" among THE MANAGER'S READINGS; the only MANAGER'S CALL is under-construction-class; draft §R.8 lists lift-order under THE MANAGER'S CALLS | HOLDS |
| RULING-3 | record: "`m`, `s`, `x` under the same sentence is a reading"; draft R.1.15: "the same holds for `m`, `s` and `x` (each run ...)" | HOLDS |
| RULING-4, FIXIND-18 | "asked as an idea, **array-in-hole**", "AN UNSET LABEL: UNRULED, asked", "is NOT a body (re-tested", "width and unset still open" present, unmarked (grep) | HOLDS |
| RULING-5 | 26 headings from the hole-reads-capture discussion to the record's end; §R.11 rows 125-148 | HOLDS |
| RULING-6, RULING-8, RULING-12 | "UNTESTABLE beyond that statement"; "class is for the manager" (grep); no §R.8 list names the `${@y}` class | HOLDS |
| FIXIND-5 | §2.7 `length(S) := chars & (nchars: S)` and T9's `length($y)` image | HOLDS (quotes) |
| FIXIND-15, FIXIND-19 | quotes ("needs a default or an EMPTY reading") | HOLDS |
| FIXIND-10..14 (evidence arms) | not re-run (critic's own mutation script `fixind/s/mut.py`); maintenance only, no design answer rests on them | not verified (maintenance) |
| RULING-9, TABLES-7 | two critics independently: `- 1` 3 of 9,999; `% 7` 9,990; `* 0` 9,990; differ = narrower count in every row | HOLDS (two independent runs agree) |

VERIFY COMPLETE
