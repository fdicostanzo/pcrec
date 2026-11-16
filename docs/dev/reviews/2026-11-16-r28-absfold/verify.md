# verify.md — round absfold (inline by the coordinator; every CONFIRMED finding is a quote claim, a count from a
# committed .out, or a one-line derivation; skill §6.2 inline option)

## SIMULATE-1 / SIMULATE-4 (`?` as a loop for the pairing rule)
HOLDS (text). COND-FAMILY.md:1599 owner "Even /x?/ is a loop from 0 to 1." sits in the 13:29 entry whose RULED part (1) (line 1600) says "the pairing loop is the DEEPEST loop that encloses any named label ... otherwise the sibling-loop error"; the note never says whether an upper-bound-1 quantifier is a loop. The split follows from the wording by hand. Engine counts not re-run.
## SIMULATE-2 / CRITERIA-2 / RULING-2 / FIXIND-1(domain) / FIXIND-2(domain) — ONE item (contradicting directions on the domain)
HOLDS on both sides. (a) SIMULATE-2: the lookbehind in `(?:;(?<h>\d)(?<=[0-4]))*` sits OUTSIDE h's group, so a syntactic "strings of h's group" is `\d` in one spelling and `[0-4]` in the other: the split is real for a syntactic group domain. (b) CRITERIA-2: `!R` is the complement over all k-tuples of strings (note item 4A.4, cited by FIXIND-2), so under ANY text `m = "x"` puts every tuple into `!office`: `((h, m?): !office)` HOLDS on `10`. (c) RULING-2: draft :1941-1943 quoted by the critic: empty intersection from pure parts = error, dead branch = warning, match-dependent = nothing; (c)'s rationale covers only the first. Neither domain as worded passes every drill.
## SIMULATE-3 / SIMULATE-5 / RULING-3 / FIXIND-8 (A2m vs vacuous `all`)
HOLDS. absfold_check.py:689 `al0 = {s: (True if not l else ...)}` (vacuous over an empty list) feeds `.out`:190 "(LI) all((n: <0)) vs (n?: <0) [the empty-set corner] differ 1 of 1111 (all HOLDS, n? FAILS)", which §4G.6 (6) quotes as A2m; §4G.6 (1) defines A2m as "c with every label marked".
## FIXIND-1 / RULING-1 ((AR) record cell = F2)
HOLDS. joint_condition.md:1759 record cell "h's part satisfied, k still tested"; :1765-1768 F1 for every shape; `.out` (ZE) C1 F1 vs F2 differ 1 ('0-3').
## FIXIND-6 ((UP) witness)
HOLDS. absfold_check.out:165 "'3;' AR FAILS k? HOLDS today FAILS": AR = today on `3;`.
## FIXIND-7 / RULING-9 (55-67 vs 55-68)
HOLDS. joint_condition.md:1824 "rows 55-67 new"; :2189 "rows 55-68 NEW".
## CHANGETAB-1 / CHANGETAB-2
HOLDS. predicates_draft.md:1256-1257 ("a plain condition true over zero allowed hits ... RULED BY ACCEPTANCE"); :2395 "`all(c)` (= the plain condition, rarely written)"; :3664 "Zero iterations: both hold (rev 9, §4.2)".
## CRITERIA-1 (`occurs.none(((h, m?): !R))`)
HOLDS by hand derivation on the three witnesses: `''` none of zero passes HOLDS; `3,` the pass lacks m, some m (`45`) puts (3, m) in `!R` -> counted -> FAILS; `3:15,` (3, 15) in R -> not counted -> HOLDS. Unmarked, the m-less pass is not counted and `3,` HOLDS (wrong). The 0 of 259 count not re-run.
## Not verified (design arguments, not claims of fact)
CRITERIA-3 (proposal), CRITERIA-4 (SUSPECTED unlock; its own confirmation recipe), CRITERIA-5, RULING-4..8 (quote-level; spot-checked RULING-8's LEAVES text at CF:1678-1680), CHANGETAB-3..8 (cite-level).
VERIFY COMPLETE
