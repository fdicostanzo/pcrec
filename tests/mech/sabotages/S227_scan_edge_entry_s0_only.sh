# S227 ([OPT-EDGE] STEP 1.1) — THE SCAN LOOP'S ONE PER-SEARCH ENTRY DISPATCH
# GOES BACK TO ASKING "IS THE STATE EXACTLY s0" INSTEAD OF "IS IT A HEAD".
#
# WHAT IT BREAKS. `src/opt/scanedge.c` DELETES a scan chain's interior states
# and KILLS the head's own class cell, on one claim about the emitted loop:
# when the ordinary step runs, the state variable never holds a head together
# with a byte of that head's scan class. The state variable is written in
# three places -- the entry seed, the step, and the offset-set prefilter's
# reseed -- and the entry seed is the one this plant is about. Axis D's
# `seeded` form initialises it to
# `seed_state[byte_class[subject[search_from - 1]]]`, i.e. to ANY member of
# the seed family, so a search whose preceding byte seeds straight onto a head
# must reach the edge body without the generic path. Since STEP 1.1 the entry
# asks the loop's own question, `is_stop(s) && !is_dead(s)`. This plant
# restores the STEP 1 spelling, an equality against `cell_of(s0)`.
#
# WHY THAT SPELLING WAS EVER EXACT, AND WHY IT IS NOT NOW. At STEP 1 it was
# exact because precondition (8) refused every seed target but `s0` as a head
# -- so the entry test's correctness was a fact about the PASS, recorded
# nowhere in the tree except inside a comment about something else. STEP 1.1
# narrowed (8) to the reseed hazard it is actually for, which is what makes
# the general entry test load-bearing rather than tidier.
#
# THE FAILURE MODE IS A LOST MATCH, NOT AN OBSERVABILITY GAP, which is what
# separates this row from S224-S226 one construct over. The seeded head goes
# down the generic path, no stay skip fires at a head (`pick_skip_states`
# declines them), the prefilter's guard is `state == cell_of(s0)` and is
# false, and the step then reads `tr[head][C]` -- the cell the pass killed --
# so the walk dies where it should have scanned.
#
# THE WITNESS IS `foo\B` AND IT IS NOT THE OBVIOUS ONE. On the `\b\w+\b`
# family the forward seed DOES land on the head and the answer STILL does not
# move, because the only searches that reach it start mid-word and no match of
# `\b\w+\b` begins mid-word -- the wrong answer and the right one coincide.
# MEASURED at the landing: `foo\B` on "xfoofoox" answers [] under this plant
# against [(1,4) (4,7)] on the clean tree. Its edge is on the REVERSE machine,
# whose seed table is { 0, 12, 12, 12 } against a stop floor of 12 -- three of
# four seed classes land exactly on the head -- so the match START is never
# recovered and both matches vanish.
SAB_ID="S227-scan-edge-entry-s0-only"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="scanedge corpus"
SAB_DESC="emit_scan_loop's one-per-search entry dispatch tests 'state == cell_of(s0)' instead of the loop's own 'is_stop && !is_dead'. Axis D's seeded initialiser installs any member of the seed family, so a search that seeds straight onto a scan-edge head takes the GENERIC path and the step reads tr[head][C] -- the transition cell src/opt/scanedge.c killed. A LOST MATCH, not an observability gap: foo\\B on \"xfoofoox\" answers [] against [(1,4) (4,7)]"
SAB_DOC_FIGURE="MEASURED 2026-09-04 (lane edge2, scratch build of this exact plant, branch lane/edge2 at 13105657): DETECTED. tests/codegen/run_scan_edge_census.sh goes 11fail/2pass -- every manifest row whose machine has both a seed table and a scan edge reports 'the loop entry is not the general head test'. The ANSWER witness is separate and was run by hand: foo\\B on \"xfoofoox\" [] vs [(1,4) (4,7)] through the spec section3.1 find-all loop. OWED: the corpus arm's own figure, which needs a battery run"
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree an
# artifact exists whose machine carries BOTH a seed table and a scan edge and
# whose loop entry is therefore the general head test. Without such an
# artifact this plant would edit a line nothing emits, and the row would score
# "not detected" for the wrong reason.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" -- "foo\\B" && grep -q "rx_reverse_seed_state" "$REACH_TMP/o.c" && grep -q "if (rx_reverse_is_stop(reverse_state) && !rx_reverse_is_dead(reverse_state)) goto rx_reverse_scan_edge;" "$REACH_TMP/o.c" && echo REACH-SEEDED-HEAD-ENTRY-PRESENT'
SAB_REACH_EXPECT="REACH-SEEDED-HEAD-ENTRY-PRESENT"
SAB_COUNT=1
SAB_BEFORE='            sb_printf(c, "%sif (%s_%s_is_stop(%s) && !%s_%s_is_dead(%s))"
                         " goto %s;   // seeded straight onto a scan-edge head\n",
                      ind, f->p, f->dir->c.name, f->dir->statev,
                      f->p, f->dir->c.name, f->dir->statev, le);'
SAB_AFTER='            sb_printf(c, "%sif (%s == %d) goto %s;   /* SABOTAGE S227 */\n",
                      ind, f->dir->statev,
                      f->repr->cell_of(f->d->s0, f->d), le);'
