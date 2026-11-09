# CRITIC simulate: spanarms
## Findings

### SIM-1 CONFIRMED (model + build tree): T2 row 2 shadows row 3 for X{0} / X{0,0}
Severity speed (missed run, not wrong); effort trivial (order rows or add `n = 0` to row 1); blast radius only `{0}` repeats; note §6 T2, §2 row "REP X{0,n}".
Row 2 (`m = 0` -> gap) is matched before row 3 for m = n = 0, so `X{0}` stays a gap although it is exactly the empty string. Model: `xy(?:ab){0}zw` rule best = 2 positions (`zw`), the spelling `xyzw` has 4. Build tree today: `xy(?:ab){0}zw` -> whole_run 7a77 (2 bytes); `xyzw` -> 78797a77 (4). Same for every one of 298 non-empty bodies in the grid (X{0,0}). Note's row 2 text "`X{0,n}` admits epsilon" is true but at n=0 it is ONLY epsilon.

### SIM-2 CONFIRMED (model; the model agrees with the build tree on the unrolled copies): W-R5 as written is an equivalent mutant
Severity doc/test (a witness that cannot fail); effort trivial; blast radius one mech row; note §3.6 W-R5, §3.1 point 3.
`(?:abc){20}` stores 32 positions from 11 copies on (build tree, spelled `(?:abc)` x k: k=9 -> 27 bytes, 10 -> 30, 11 -> 32, 12 -> 32, 13 -> 32). The note's rule gives c = ceil(32/3)+1 = 12; "saturation at one copy fewer" = 11 copies = 32 positions = the CORRECT run, not "29". 29 is not reproduced by any copy count (27, 30, 32 only). To differ the sabotage must drop 2 copies (10 copies -> 30).
### SIM-3 CONFIRMED (model sweep w = 1..40): "ceil(32/w)+1" is a safe upper bound, not the saturation point
Severity doc (harmless extra copy); effort trivial. Note §3.1 point 3 says the copy "after which no stored field can change". Re-sweep (power(X,c) fields head/tail/best/all/trunc stable from c0): c0 = ceil(32/w) when w does not divide 32 (w=3 -> 11, 5 -> 7, 6 -> 6, 7 -> 5, 9..10 -> 4, 11..15 -> 3, 17..31 -> 2, 33+ -> 1), c0 = 32/w + 1 only when w | 32 (w = 1,2,4,8,16,32). The claim never undershoots (soundness safe, 40 widths), overshoots by 1 at every other w. Non-`all` bodies: stable by 2 copies in all 122 non-all bodies of the grid (97 stable at 1, 25 at 2): that claim HOLDS.

### SIM-4 SUSPECTED (low; confirmed only that the tie exists): W-R4 and W-R3 "correct run" is a tie
`ab(?:c?){2}de` correct best = `ab` or `de` (2 positions each, model and build tree: whole_run 6465 = `de`); W-R4's sabotage (`abde`, 4) is detected either way, so no defect, but "correct = de" holds only by the build's tie-break. Doc only.

## PROBED-AND-HELD
- T2 + 3.1 pts 1-3 + Offsets, python3 -I model (model.py, grid.py in this dir) written from the note text before reading any lane script: 299 bodies (empty, c?, width 1-3 literals/classes over {a,b,c} incl. cube [ac][bc] and non-cube [ab], equal-width 2-member alternations) x m 0..4 x n m..5 and unbounded x 2 contexts (bare; xy..zw) = 14842 patterns (54 skipped, language > 40000 words). Necessity of head, tail, best, all, width on EVERY word of the language (language-by-construction): 0 violations.
- Oracle: 149 random patterns `^BODY{m,n}$` x 1093 subjects (all strings over abc, len 0..6) through p2probe = 162857 checks: language equals my enumeration (0 disagreements), rule fields hold on every libpcre2 match (0 unsound).
- Rule vs spelling (model of best-of-both spellings X^m(X)? / (X)?X^m): equal at every grid point except X{0,0} (SIM-1; rule weaker) and width-0 bodies (rule stronger and correct, spelling gaps).
- Model vs build tree, 450 sampled grid points (663 compiles, spelled, xy..zw flanks, -e byte): model best length == measured for all non-alternation bodies; 19 differences all in two-position alternations such as `ab|cc` where my product-of-sets ALT model is stronger than pcrec's (an ALT-model calibration gap, not a REP-rule issue).
- Non-all bodies saturate within 2 copies (122 bodies); rule output == fully unrolled CAT (660 cases, w 1..11, m up to 70) incl. all=false when c<m.
- Part (b): reproduced every quoted number in section 3.4 (A{4}=4, ab{3}c=5, 8, 8 cube, 12, 6, 4, 6, 10, 32, 4, unchanged min-0), section 4.4 (8 for the E-1/E-2/E-4 rows, abx/xcd tie 3 for ab(?:x\b)+cd, 6, 3 via the unit join), and W-R1 (4 vs 6), W-R2 (4 vs 10), W-R3 (2 vs 4), W-R4 (2 vs 4). NOT reproduced: W-R5's 29 (SIM-2).
