# CRITIC simulate: absfold

## Findings



### SIMULATE-1 — CONFIRMED (own engine) — design — two spellings of one pattern: sibling-loop ERROR vs an answer, because "loop" is undefined for `?` / `{0,1}`
WHERE: J7 / item 5 (the pairing loop "the DEEPEST loop ... otherwise the sibling-loop error", part (1) RULED 13:29,
CF:1599-1602, in the same entry as the owner's "Even /x?/ is a loop from 0 to 1"); §4G.1 (AR) lists "an optional
skipped" and "a loop run zero times" as one absence; §4G.6 does not mention it. No sentence of the note says whether
a quantifier with upper bound 1 is a LOOP for the pairing/sibling rule.
REPRO (R/simulate/drill_sib.py, own engine; Python `re` cross-checks every match): pattern A
`/(?<k>\d)?-(?<h>\d)?/` vs pattern B `/(?:(?<k>\d)|)-(?:(?<h>\d)|)/` (the owner's own equation `x?` = `(?:x|)`, CF
13:38), condition `(h: <5, k?: 3..7)`; and `/(?:(?<k>\d)-)?(?:;(?<h>\d))*/` vs `/(?:(?<k>\d)-|)(?:;(?<h>\d))*/`.
If `?` IS a loop (the owner's remark): A's record and joint `((h, k?): ...)` are the SIBLING-LOOP COMPILE ERROR (k's
loop and h's loop do not nest), B gives answers (`-1` HOLDS, `3-` FAILS), and `(h: <5) & (k?: 3..7)` gives B's
answers on BOTH spellings: drill (1) and drill (3) (record = `&`) both split, on every subject of both populations (6 + 4 distinct subjects; R/simulate/drill_sib.py output). If `?` is NOT a
loop: 0 differ in all three forms. With ONE kind of absence the answers never need `?` to be a loop; only the
sibling rule reads it.
FIX (one sentence for rev 20): "a quantifier with upper bound 1 (`?`, `{0,1}`, `{1}`) is not a loop for the pairing
rule: its group is set at most once per pass of the enclosing loop" (or: the sibling error looks only at loops whose
upper bound is 2 or more). EFFORT: one sentence + a (AR)-adjacent example. BLAST: every record/joint over two
optional fields (dates without day AND without month, `(?:...)?` sections); also the `label.unset` text.

### SIMULATE-2 — CONFIRMED — design (answer) — (AR)'s "SOME string of h's group" splits two spellings of one pattern; the manager's (c) "ANY text" does not, and the two texts disagree
WHERE: §4G.1 table (AR), mark column ("one label `(h?: S)`: holds when SOME string of h's group is in S") and the
F1 paragraph ("some value of the group would do"); vs §4G.4 corner 2 / §4G.6 (3) ("THE DOMAIN ... STILL OPEN") and
the manager's reading (c) (CF 14:50: "'Some value' ranges over ANY text, not only the texts the label's group can
match"). The note's declared RULE TABLE fixes the domain that its own corner list calls open and that (c) then sets the
other way.
REPRO (R/simulate/dom.py; Python `re`): `/(?<k>\d)(?:;(?<h>\d)(?<=[0-4]))*/` and `/(?<k>\d)(?:;(?<h>[0-4]))*/` give the
same match and the same captures on all 1,110 subjects of (RZ)'s population (0 differ). Condition
`(h?: 5..9, k: 3..7)`: under (AR)'s group domain, on the zero-pass subjects `3`..`7` the first spelling HOLDS (5 of 10:
some `\d` is in 5..9) and the second FAILS (0 of 10: no `[0-4]` is); under (c)'s ANY-text domain both HOLD (0 differ).
Same for record and joint forms. (A context-aware "texts h can take in a match" also avoids it but is not what (AR)
says and is not computable by `part()` from the group alone.)
RESULT for the 14:50 readings: (c) keeps drill (1) at 0 here; (AR)'s wording does not. Rev 20 should state the
mark's domain once (c) and strike "of h's group" from (AR) and 4G.1's F1 sentence (and say the narrowing-site error,
`predicates_draft.md:1941-1942`, is what still rejects a constant set disjoint from the group — that error has the
same context question). EFFORT: two cell edits. BLAST: every marked label whose set reaches outside its group.

### SIMULATE-3 — CONFIRMED (text vs text; own engine) — doc/answer — §4G.6 (6) gives A2m an answer its own definition in (1) does not give
WHERE: §4G.6 (1) defines "A2m: `all(c)` is c with every label marked"; §4G.6 (6) then says "Under A2m `all((x: S))` =
`(x?: S)` except when no value of x's group is in S (F1: `(n?: <0)` FAILS, `all((n: <0))` HOLDS on `''`; 1 of 1,111)".
By (1)'s definition `all((n: <0))` IS `(n?: <0)`, so under F1 (the manager's (b)) it FAILS on `''` and the two agree on
all 1,111; the quoted HOLDS (and the "1 of 1,111") belong to a different `all`: vacuous truth over no values ("every,
possibly none", the manager's 14:31 words), which is not A2m. The manager's (a) (CF 14:50) chooses "A2m" AND
"`all(...)` over no values holds for EVERY absence alike" — two definitions that part exactly on an empty S.
REPRO (R/simulate/eng.py `single(ctx,'n',None,None,lt(0),mode='A2m')`, `/(?:(?<n>\d),)*/`-shaped zero pass and
`/(?<n>\d)?x/` on `x`): A2m-as-defined FAILS; the note's (6) says HOLDS.
WHICH KEEPS THE DRILLS AT 0 (R/simulate/drill23.py, nested `(c, h, k)` 124 subjects and (ZE) 336 subjects, every
control on every label, record vs `&` vs joint-of-product and three spellings of an empty coordinate): A2m-as-defined
with F1: drill (2) 0 of 27,776 + 32,256, drill (3) 0 of the same, `$a`-empty (ZE) 0 of 672. The vacuous "holds over
none" on an EMPTY S cannot be written for a record without dropping the outside label's test (that is A2v, which
breaks record = `&`, 5 of 1,110, the note's own count) — so rev 20 must say: `all(c)` = c with every label marked,
and therefore `all((n: <0))` FAILS on the empty list (the empty-set compile error usually catches the constant case).
Strike or correct (6)'s parenthesis and the (LI) "1 of 1,111" under A2m; re-word (a) to drop "holds over no values"
as a definition. EFFORT: one sentence each in §4G.6 (6) and the 14:50 record. BLAST: L36 ("DIFFERENT: BY DESIGN") is
exactly the cases (x has no value, S non-empty) — unchanged; only the empty-S corner moves.

### SIMULATE-4 — CONFIRMED (own engine vs the script) — design — §4G.6 (5)'s "one-word fix under A2v/A2z" (side B of (1)) holds only if a skipped `(?:...)?` is NOT a zero-pass loop, which the script assumes and the text does not say
WHERE: §4G.6 (5) ("`all((h: <10, m: <30))` gives it on 0 of 259 under A2v and A2z, on 11 under A2m. So the shape's
one-word fix exists exactly under the `all` readings (1) puts against one kind of absence"), §4G.6 (1) side B, §4G.2
(OP) row, §9 row 66, CF 14:50 (a)/(f). Script: absfold_check.py (OP) builds a pass with no minutes as `(h, P)` ("missing
in a pass"), never `Z`, so `a2("A2z")`/`a2("A2v")` treat it as a plain absence.
REPRO (R/simulate/op_loop.py, own engine, the script's 259 lists, the script's domains): with `(?::(?<m>\d\d))?` read
as a loop of 0..1 passes (the owner, CF 13:29: "Even /x?/ is a loop from 0 to 1"; m's deepest loop is then the `?`,
which becomes the pairing loop and runs ZERO passes on `3,`): today vs `all(...)` A2v 36 of 259 (`3,` and even `12,`
HOLD: the outside h is no longer tested), A2z 11 of 259 (`3,`), A2m 11 — no reading of `all` gives the wanted
answers. With `?` read as NOT a loop: A2v 0, A2z 0, A2m 11 (the note's numbers, reproduced). Same mechanism splits
`/(?<n>\d)?x/` from `/(?:(?<n>\d)|)x/` under A2v/A2z (R/simulate/drill1.py: 7 condition keys each, `x` HOLDS vs FAILS)
— i.e. A2v/A2z need "`?` is not a loop" to be defined at all, and then still split `x*` from `(?:x+|)` under A2z
(drill1: 1-2 keys, `x`).
CONSEQUENCE: side B of (1) is weaker than stated — it rests on the undefined point of SIMULATE-1, and under the
owner's own remark it vanishes (the shape has no one-word fix under ANY `all` reading), which supports the manager's
(a) (A2m) and makes (f) "no one-mark fix" true without the "except under A2v/A2z" qualifier. Rev 20 should state
(5)/(f) conditionally or settle SIMULATE-1 first. EFFORT: rewrite two sentences + §9 row 66. BLAST: the (OP)
row of 4G.2 and row 66 only.

### SIMULATE-5 — CONFIRMED (script vs text) — doc — the (LI) "empty-set corner" row computes a vacuous `all`, not the script's own A2m
WHERE: absfold_check.py (L36) block: `al0 = {s: (True if not l else plain(AR, l, lambda x: False, D)) ...}` — `all` is
"HOLDS when the list is empty", whereas `a2("A2m", ...)` (same script, used for (RZ), (OP), TL) marks every label and
under F1 FAILS an empty S. `.out` line 190 "(LI) all((n: <0)) vs (n?: <0) [the empty-set corner] differ 1 of 1111" is
therefore the vacuous reading vs the mark, and §4G.6 (6) quotes it as A2m. Own engine (R/simulate/recompute.py, (LI)
1,111 lists): A2m-as-defined vs `(n?: <0)` 0 of 1,111; vacuous/A2v vs `(n?: <0)` 1 of 1,111 (`''`) — the script's
number reproduces only under the vacuous reading. Same root as SIMULATE-3 (fix there); listed separately because the
brief counts every text/script divergence. Also: the row "(LI) all((n: <5)) vs (n?: <5) 0 of 1111" uses the same
vacuous `al`, which coincides with A2m only because <5 is non-empty.

## PROBED-AND-HELD

Own engine (R/simulate/eng.py, written from §4G.1/(AR)/J6/J7/J9 BEFORE opening absfold_check.py): a backtracking
matcher with per-pass capture frames (Python `re` cross-checks every match), pairing loop = deepest enclosing loop,
zero passes / never reached / missing in a pass = one ABSENT; mark = existential over a domain (GROUP or ANY text);
default read on every absence; record = joint over the product; `&` = each single-label condition per its own loop.
- Drill (1), same pattern two spellings (R/simulate/drill1.py): `x?`/`(?:x|)`/`x{0,1}`/`x??`/`(?:|x)` (2,304
  comparisons), `x*`/`(?:x+)?`/`(?:x+|)`/`x*?`/`(?:x+?)??` (23,040), (RZ) pattern `*`/`(?:+)?`/`(?:+|)`/`*?` over 1,110
  subjects (1,704,960 comparisons), every control (nothing, `h?`, `h = 0`, `h = 9`) on every label, sets <5, <0, "x",
  plain + A2m + A2v + A2z, F1/F2, GROUP/ANY: plain and A2m 0 differ everywhere; ALL differences are A2v/A2z (the note's
  own (1)). x? vs x* on shared subjects: 0 of 576.
- Drills (2)+(3) (R/simulate/drill23.py): nested `(c, h, k)` 124 subjects and (ZE) 336, every control on every label
  ((None, mark, =0, =9)^k), plain + A2m: record vs `&` vs joint-of-product 0 of 27,776 + 32,256 under F1 and F2;
  empty coordinate in three spellings (constant `<0`, never-true, joint empty) 0 under F1, 20 + 96 under F2; set empty
  through `$a` (ZE a=0, 672) 0 under F1, 3 under F2. => of the 14:50 readings, (a) A2m + (b) F1 + (c) ANY + (e) per
  pass keep drills (1)-(3) at 0 (bar SIMULATE-1's `?`-as-loop sibling split, which no reading of (a)-(f) touches).
- Recomputed from the rule (R/simulate/recompute.py, own engine on the script's populations), REPRODUCED: TM2 92/90/2
  (`9`, `09`) and the 5 rows; TM2-L all 5 forms x 5 lists; (RZ) 5, 0, 0, 0 (h?), h=9 5 / 0, h=0 0, A2v rec vs & 5,
  A2m 0, `9` answers; (Z1) 10; (ZN) 69, 0 per pass, 48 pooled; (NL) 19, 9, 1 (`''`), 0; (ZJ) 0 of 10 unmarked each set,
  the `("x",3)|(0,5)` domain corner (`3`: \d FAILS, ANY HOLDS); (ZJ-E) F1 F/F/F, F2 H/F/F (the note's F2 "HOLDS, HOLDS,
  FAILS" counts the record AND the product-joint spelling as F2; mine reads the joint spelling by the joint sentence
  — a wording point, not a count); (ZE) 0, 0, 0, 0, 1 (`0-3`); (ZD b) agree under each default; (ZD c) 1 / 0; (OP) 1,
  0 per pass, 8 pooled, 11/11/12, A2m 11 (A2v/A2z 0 only with `?` not a loop: SIMULATE-4); (UP) 15, 0, 0; (DL) 1 / 0;
  (LI) 1 (plain vs all), n=0 1, n=9 0; (D1) 11,000 / 11,110 (the third, `m = 00`, reproduces only with the script's
  canonical-numeral `<30`; my first set ignored `canon`, my error, not a finding).
- Not re-run: the L36 "5 of 11 groups" (absent's SP rows; my own ?/* families show the same A2v/A2z-only split), (OG)
  885 of 5,461 (DERIVED in the note; superseded by the manager's (d) compile error anyway), (U)/(S) OLD-OUT rows.
CRITIC COMPLETE
