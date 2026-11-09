# check — crit-sar1
## Findings
CHECK-1 CONFIRMED (maintenance, small, blast: one lever row). The `rep` restore arm of T2 row 3 (`{ rb_rep_any, RB_REP_SPLIT, PCREC_WALK_ARM(REP) }`, req.c:810) has no detector. S1921 plants row 2 only; every `h rep` cell in [facts-rep] (run_facts_checks.sh ~L690-705) is an exact repeat or `(?:a|bc){2}`. Under restore=rep, `xy(?:ab){1,2}zw` reads req_whole_run 6162 (default 61627a77), so a cell could separate them; none exists. A plant dropping the arm from row 3 leaves [facts-rep] green, and the axes `rep` arm cannot see it (answer-identity only, both forms sound). Fix: add `h rep xy(?:ab){1,2}zw req_whole_run 6162 harness:rep` plus a row S1922.

CHECK-2 CONFIRMED (maintenance, small). The re-aimed entry-only witness `(ab)c?userpass` (run_handoff_reach.sh) is checked structurally only (grep of entry=1,re=0), and its corpus (handoff_vm.rxt L847-870, match 18..28) does not move under the S463 plant: starts 0,5,10,15,17,18 under --engine=vm are SAME. Only `abcuserpass` at 0 goes DIFF (N vs M 0 11), and that subject is not in the corpus. The former entry witness `x{2,5}(?i:cat)` was answer-sensitive (S463 plant, --engine=vm, 0:xxxxxCaT gives M 1 8 against M 0 8) but is now classed `re`. S463 itself still fails via handoff.rxt (hosted by the vm twin), so no row is lost, but the entry-only class no longer has an answer-sensitive witness.

CHECK-3 CONFIRMED (low, small). S1919's SAB_REACH probes only the VM witness (`(a.){10}xyz`, K 20). The DFA twin `(?:a.){10}.?xyz` (K 21 on S, 5 under the plant) has no REACH or POP line, so its decay would not read UNREACHED.

CHECK-4 SUSPECTED (low). rr_pow_count's non-`all` saturation (`!b->all ? 2`) and `o.all && c == m` have no row or listing cell. A plant of `1` in place of `2` gives a sound, shorter run, and nothing in [facts-rep] asserts the run of a non-all exact repeat. `c == m` looks equivalent in effect, since truncation hides it. Confirm with a plant on `(?:a.){3}xyz` run text.


## PROBED-AND-HELD
- Hosting: S1915/16/17/19 -> `harness` arm (runs tests/harness/run.sh over every .rxt, which includes tests/litscan/spanarms.rxt); S1918/20/21 -> `facts` arm (run_facts_checks.sh). Both words are in the vocabulary. 7/7 held.
- REACH on SUBJECT: 7/7 print their expect (REACH-WR1-RUN, WR2-RUN, WR3-RUN, WR5-RUN32, WR6-K20, PIECES-W41, REP-RESTORES).
- Plants (PLANT_STATUS occurrences=1, build rc=0 on all 8). The witness is the oracle with the same subjects as spanarms.rxt, all three engines. All SILENT-MOVE (rc 0, answer wrong): S1915 `xyababzw` N vs M 0 8; S1916 `xyabzw` and `xyababzw` both N; S1917 `abef` N vs M 0 4; S1919 VM `(a.){10}xyz` N vs M 0 23, DFA twin N vs M 0 23. S1918 gives 30 positions vs 32. S1920 gives width 33 vs 41. S1921 restore=rep gives 7879616261627a77 vs 6162. 0 LOUD, 0 SAME.
- Range: W-R1..W-R6 map to S1915, S1916, S1917, W-R4 -> S1906 (E1, hosted there, not R1), S1918 (W-R5), S1919 (W-R6); S1920 covers the pieces, S1921 the lever. No missing id.
- Anchors: `m6read_check_sab_anchors.py` is read-only, root derived from the file. 1209 rows (1252 sites), all anchors resolve.
- S463: reach on SUBJECT prints K 3 (`xxCAT`); BASE reads K 5 (`CAT`). The plant fails on the witness (`(?m)^x{2,5}(?i:cat)` 0:xxxxxCaT N vs M 0 8, all 3 engines; plain pattern under --engine=vm M 1 8 vs M 0 8). The old VM witness `x{2,5}(?i:cat)` on S is entry=1,re=1 (K 3), so its old `entry` class would now fail; the move is real and accounted for. `(ab)c?userpass` is entry-only, K 3, on both BASE and S.
- [facts-rep]: nrw is counted and 0 fails; a missing binary fails; REFUSED or empty values mismatch every non-empty want; 9 cells.
- Lever fence: the mention scan on SUBJECT is empty (S1921_ allowlisted, no other file names the lever). The axes `rep` arm is answer-identity over the corpus, which includes spanarms.rxt.
- Counts: about 75 compiles/probes.
