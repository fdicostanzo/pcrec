# CRITIC FAMILIES: k147fix (review r64)

## Findings

### FAMILIES-1  CONFIRMED  severity: maintenance  effort: S  blast: tests/thread/run_compile_stack.sh DEPTH_FAMILIES only
where: run_compile_stack.sh DEPTH_FAMILIES (rows brefrep/brefsrep/litrep)   what: K147 lists variants `?`, named groups with `\k<x0>`, `*+`, `*?` as also dying at 250; no row covers any of them. Only `*` is a row. Most share a path with `brefrep` (identical hw 257,552), so they need no row; but `*+` is a distinct path: hw 293,552 (SUBJECT) vs 257,552, and K149's `(abc|abd..abe)*+` is 293,552 too. It is a different arm (possessive/atomic wrap) that the rows never reach, so a regression confined to the `pss_atomic`/possessive arm of the new frame split would not turn this script red. `\k` named has a `named` row but with core `a`, no `\k` row (named+`\k<x0>` at SUBJECT = 257,552, same as `\1`, low value).
repro: stack.sh on nest('(a|b','\1',')*+',250) -> BASE DIED exit=139, SUBJECT rc=0 hw=293552 (below worst 344176, no budget risk today). Same for `\\%d` core. A one-row addition (`brefpos;;(a|b;\1;)*+;;all;0`) would cover it. `?`, `*?`, `\k`: same hw as `*`, no row needed.

### FAMILIES-2  CONFIRMED  severity: maintenance  effort: S  blast: none today
where: nest() `case "$2" in *%*)`   what: any core containing a literal `%` is now run through printf once per level; a future row wanting a literal percent changes meaning. No old row had a `%` in a core (checked). The header comment documents it, so a documented trap, not a defect.

### FAMILIES-3  CONFIRMED  severity: doc  effort: S  blast: none
where: DEPTH rows   what: the depth-251 half of every new row is vacuous as a guard for this fix (BASE also prints "too deeply nested" at 251, hw 122,152 identical: the parser refuses before possessify). Only the @250 half carries the guard. True of old rows too; logic correct. Noted because "refused at 251" is not evidence of the fix.

## Answer to THE ONE QUESTION
(a) YES, each new guard row goes RED on BASE: brefrep, brefsrep, litrep @250 -> BASE `DIED exit=139` (stack.sh, 442368), SUBJECT rc=0 hw 257552/257552/317504; @251 refused by name on both trees. ncaltrep is not a K147/K149 guard (BASE=SUBJECT=344176 rc=0; a measured-worst record row, the K147 Fix text is true). `\\%d` yields `\1\2...\250` exactly (250 backrefs, no double backslash, ends `\249\250)`). features all / engine 0 reach the fold (BASE dies). Engine 1 is refused by name (`\1` needs VM / captures), engine 2 passes at the same hw.
(b) Old rows: every pre-existing DEPTH row and the u1/u2 UNBUILT patterns at 250 and 251 are byte-identical BASE vs SUBJECT nest() (diff -r of the pattern dirs shows only the 8 new files). WIDTH/CONTROL use no `%` core. The script reads no headroom/worst/margin constant; the largest new record (344,176 = 77.8% of 442,368) is under budget.


## PROBED-AND-HELD
- 4 new rows x {250,251} x {BASE,SUBJECT} = 16 stack.sh runs; old-row pattern diff 20 rows + 2 unbuilt x {250,251}, 0 changes.
- Variants at depth 250 BASE vs SUBJECT, 22 runs: `?`, `*?`, `*+`, `\1..\N` with `?`/`*+`, named `\k<x0>`, K149 `?`/`*+`/`*?`, `+` (SUBJECT refuses by name, "nested bounded repeats would replicate a body": rc=-1, not a crash), unquantified. All BASE dies except K149 `*+` (ok 353512) and unquantified; all SUBJECT compile <=317504 except the `+` refusal.
- engines 1/2 on the four rows at 250, SUBJECT: 8 runs. Total ~54 runs; depth 250 only for compiles.
CRITIC COMPLETE families 17:17
