# VERIFY r99 memfn-winsplit3

## CLOSURE-1
Verdict: HOLDS.
- r98 RULING (top of r98 file), word for word: "R1/R2: rule adopted. Every gate arm's BASE run must be GREEN on the box it is listed for before it is used." No Mac qualifier.
- Rev 2.1 §8.2 (line 741-743): "a gate arm is used only on a box where its BASE run is GREEN; §8.4 records each Mac arm's command and last line at the base." §8.4 (line 850) title and table are Mac-only; no Linux base run is recorded.
- WHEN: rev 2.1 never states when a Linux arm's base run is taken relative to the first commit (C0b). The only timing text is line 847-848: "The Linux arms are OWED by the build lane at the tip, not run by this design lane", and G5 (line 818): "at the tip, Linux". `grep -n "first commit\|before C0b"` finds no Linux-base precondition. Line 820-821 ("an arm with no base run on a box is not listed for it") is applied to Mac G5 only; Linux G5 is "REQUIRED at the tip" (line 844) with no base run.
- Linux-listed arms with no Linux base run: make strict, test-memfn-finder, test-memfn-stamps, test-memfn-g2/run_g2.sh, plain run_g2_win.sh, run_g2_pres.sh (+ --plants), g2_vspan, g2v/simdfloor mech rows, G5 (table lines 840-845).
- S3012: §8.2 line 804-805: "run_g2_pres.sh plain and --plants, which EXECUTES its 7 re-aimed plants (S3012 stop; S3047, ...)"; §8.3 G3 Linux cell (line 841): "run_g2_pres.sh + --plants (its 7 plants)". So §8 relies on run_g2_pres.sh --plants executing S3012 on Linux (the only arm that does: binders rows show S3012 at run_g2_pres.sh:228). Its Linux base run is untaken.

## CLOSURE-2
Verdict: HOLDS (doc, small).
- Diff rev2->rev2.1 line 798: removed `| G5 | `make test` yes; mech yes | yes |`; line 804 added `| G5 | not listed (no base run: ~100 min) | REQUIRED at the tip |`.
- §8.2 lines 818-821: "G5, at the tip, Linux: REACH_ONLY mech over the re-pointed rows, then `make test` ... G5 is NOT a Mac gate in this unit: `make test` measures ~100-105 minutes ..., so its base run is not taken here". The reason names only `make test`; REACH_ONLY mech has no Mac base row in §8.4 and no stated reason.
- grep "G5\|REACH_ONLY" over the doc: G5 only at 808, 818-819, 844; none inside §R2.1 (lines 34-60), so no §R2.1 row. Caveat: "G5 is NOT a Mac gate" does drop the whole gate by assertion; only the mech half's reason is missing.

## CLOSURE-3
Verdict: HOLDS.
- §8.2 G3 Mac bullet (line 789-790): "33 re-aimed plants S1400-S1428, S1543, S2986-S2991, S3040, S3041, S3084-S3096, S3116-S3118".
- Independent count from closure/bind_tip.txt (binders output; g2 rows with new key != old, detector run_g2_win.sh): 33 rows: S1400-S1407, S1409, S1410, S1422, S1423, S1425-S1428, S1543, S2986, S2987, S2989, S2991, S3040, S3041, S3084, S3089-S3093, S3096, S3116-S3118. Count 33 matches; the spelled ranges cover ids not in it (S1408, S1411-S1421, S1424, S2988 [a `rows` edit1 row, bind_tip.txt:386], S2990, S3085-S3088, S3094, S3095). pres 7 (S3012, S3047, S3106, S3110, S3112, S3125, S3126) and proof 1 (S1419) also match. Caveat: I reused the closure critic's bind_tip.txt rather than re-running binders.py.

## CLOSURE-4
Verdict: HOLDS.
- files.spec:6: `title kit_pos.c ... the mass of a position multiset (kit_mass, from presence.c) and the run member pick (kit_run_member).` No kit_run_set / kit_run_at.
- Assembled kit_pos.c (asm/memfn/src, the round's assemble output) lines 4: header repeats exactly that title; kit_run_set at :130, kit_run_at at :139; kit_wspan_at stays in presence.c:80.
- cut.spec:16 `kit_pos.c <- presence.c 56-91 112-118` and cut.spec:1 still reads "window_split.md rev 2 §3: the cut at T a0f13ad83".


VERIFY COMPLETE
