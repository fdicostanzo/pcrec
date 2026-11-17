# CRITIC changetable: predspec23

## Findings

### CHANGETABLE-1 (CONFIRMED, doc, effort small, blast radius: reader trust in the "every site" claim)
§R intro (rev23:371-373) and §R.9 (rev23:826-829) say the table lists EVERY rev 22 site for a term the rulings touch. Repro: a python scan of rev 22 for the term set (`x?:`, `h?`, `all(`, DOM, value set, domain-scope, match-context, mark-narrows, zero-pass, one-witness, default-reaches, optional mark, never-absent, the mark, $a), minus the 118 table cites and the 40 UNAFFECTED sites, leaves 26 hit lines uncovered. Substantive ones (affected, no row, cite does not reach them):
- rev22:372-376 (status header: "Rev 21 reads the mark's domain from the PROGRAM ... Rev 22 folds not-is-complement ... one-witness"; no site covers 359-399). Handled in rev23:1033-1039 but has no row.
- rev22:650 (S021 cites 651 only), 1921 (S073 cites 1920; "narrow each other's DOMs"), 2265 (§4.2 (e2) "$a ... manager's derivation", between S092 and S093), 2602 (S112 cites 2587, 2606-2607; "`all` reads DOM"), 3243 (never-absent mark warning family; S123 is 3205-3218), 3406 (S126 is 3409-3419; "absent label FAILS unless the author marks it"), 5472 and 5481 (S154 is 5470-5471, S155 5484-5489; "$a outside the condition", "DOM non-regular").
Each IS handled in the rev 23 body (checked rev23:1316-1325, 1721-1723, 2268, 2833, 3477, 3648, 5746-5757); the defect is the missing or short cites, so the table is not complete as stated.
Uncovered hits classified UNAFFECTED: rev22:543,544,552,553,566,5315,5411 (other-side sigil "mark"), 712,725,728 (unrelated `$a`, L50, L53), 1158 (generic "mark"), 2908 (heading of S116's table), 3886/4132 (`&` mark under ON), 4463,4527 ($a path), 4612 (metadata mark).
Fix: add rows or widen cites for the 9 ranges above.

### CHANGETABLE-2 (CONFIRMED, doc, small)
§13 "OPEN ITEMS NEW IN REV 20" bullets rev23:5704-5737 (zero-pass-empty, match-context, domain-scope, mark-narrows, mark-under-not, one-witness, "NEW in rev 22 ... (i) WHAT COUNTS AS A CONDITION for the `!` error", default-reaches-dollar, (e3), "IF IT IS POSSIBLE" tier 5745-5748) still read live: "F1 is the mark's one meaning", `(h?: <$a, k: 3)` FAILS, "a default fills it, a mark reads it existentially", "`!` takes a pattern or a set, never a condition". No inline [REV 23] note; retirement is only in the trailing block rev23:5761-5780 (bullets 5750 and 5756 do have inline notes, so treatment is inconsistent). The "dated history (a CLOSED item)" wording at rev23:379 allows it, so doc severity only.

### Part (b) result
Live scan of rev23:1020-5853: "source row", "result row", "per subject" have 0 hits. About 200 hits for `x?:`, `h?`, `all(`, DOM, value set, `!`-error are each a dated REV 20-22 paragraph, ruling-table row, "(rev 22: ...)" clause, [REV 23: ...] note, or a rev 23 sentence saying the thing is out. Only survivors: CHANGETABLE-2. `!` on a condition is not called an error anywhere live (rev23:2609 says removed; 4849 is dated, REV 23 paragraph follows).

## PROBED-AND-HELD
- Table integrity: 118 rows = 35 AFFECTED-UNCOVERED + 83 COVERED (+40 UNAFFECTED = 158 in sites.tsv); all 118 ids exist, none UNAFFECTED, 0 missing; every row's cite equals sites.tsv's rev 22 lines (0 mismatches).
- 444 rev 22 term hits re-derived; 418 inside a row cite or an UNAFFECTED site; the 26 others classified above.
- rev 23 live scan: source/result row, per subject 0 hits; mark/all/DOM/`!`-error survivors only as CHANGETABLE-2.

CRITIC COMPLETE
