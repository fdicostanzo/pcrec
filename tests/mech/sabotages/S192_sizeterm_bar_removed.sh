# S192 (S-ARTSIZE2) — [ART-SIZE] THE MATERIALITY BAR REMOVED, AND THE ONLY
# INSTRUMENT IN THE TREE THAT CAN SEE IT IS A REFERENCE COMPILER BUILT WITH A
# LOWERED CAP.
#
# The size term's selection has two steps and the bar sits between them
# (docs/design/artifact_size_term.md §3.3): the argmin picks a rung, and the
# rung is KEPT only if it saves at least 25 % of the default's bytes. The bar
# gates a THROUGHPUT preference — K=1 costs 1-3 % on single-level large
# counts (§3.4), so a 3 % size win is not worth taking — and removing it makes
# the term take every improvement however small.
#
# RE-ANCHORED 2026-09-17 ([OPT-DIAL], lane dialimpl): the 75 that used to sit
# as a literal in the `if` below is now `SIZE_TERM_BAR_DEFAULT` (still 75,
# still beside `size_term_choose`, `src/core/compile.c`) and the function
# reads a `bar` PARAMETER instead of the literal, because `--tune=N` moves
# the bar (`docs/spec/tuning.md` §5.4: 95 at `-2`, 85 at `-1`, 75 -- the same
# default, unmoved -- at `0`). The row's INTENT is unchanged: the plant still
# removes the bar entirely, so the argmin rung is taken however small the
# saving, regardless of which value `bar` was resolved to. Nothing about
# WHERE the plant is visible moves either -- the reach probe below compiles
# at the dial's OWN default position (`balanced`, `bar` resolving to the
# same `SIZE_TERM_BAR_DEFAULT` 75 the pre-dial build always used), so
# [OPT-DIAL] changes no cited figure in this row.
#
# WHERE THE PLANT IS VISIBLE, AND WHY THAT IS EXACTLY ONE PLACE. The bar can
# only be observed where it DECLINES, and a decline is invisible from the
# outside: the artifact is simply the one the caller's own options produce.
# The single exception is `cap-rescue` — the path where the bar declines a
# rung and a CAP takes it anyway — because that path stamps its own name into
# the artifact (`RX_UNROLL_K_WHY "cap-rescue"`, D81/§4.5). With the bar gone
# the rescue never happens: step 1 keeps the argmin, the argmin already fits,
# and the artifact stamps `size-model`. So `run_size_term.sh` §5's cell reads
# `size-model` where it requires `cap-rescue`, and that is the detection.
#
# THAT CELL RUNS AGAINST A COMPILER THIS PROJECT BUILDS ON PURPOSE. The
# natural cap-rescue population is ZERO (§6 of the same script pins it, and
# §4.2b of the note derives the empty band), and the CLI overrides are
# RAISE-ONLY by ruling (D84 ruling 1), so the branch cannot be forced from
# outside a build. §5 therefore compiles a second pcrec with
# `-DPCREC_SIZE_TERM_THRESHOLD=20000 -DPCREC_MAX_VM_EMIT_CODE_BYTES=30000`
# ([ENG-ABS]'s precedent) and drives the witness through that. THIS ROW IS
# THE RECORD THAT THE BAR HAS NO OTHER WITNESS: if that reference build were
# ever dropped from the script, nothing anywhere in this repository would go
# red for a size term that ignores its own materiality bar. The
# `SAB_REACH_POP` floors below are what make that dependence checkable rather
# than stated.
#
# THE GREEN ARMS ARE THE POINT OF THE ROW. Answers cannot move (K is
# answer-identical by construction, S191's header), and neither can the
# corpus's artifacts: the one corpus pattern the ladder fires on takes a rung
# the bar ACCEPTS by a wide margin, so removing the bar leaves its K where it
# was. `tests/size/size_term.rxt` is expected 0fail; the nested-N=8 subject's
# stamped K in §3 is expected UNCHANGED.
SAB_ID="S192-sizeterm-bar-removed"
SAB_FILE="src/core/compile.c"
SAB_SUITES="sizeterm harness"
SAB_HARNESS_TARGET="tests/size/size_term.rxt"
SAB_DESC="the size term's 25% materiality bar is removed, so the argmin rung is taken however small the saving and a declined-then-cap-rescued K becomes an ordinary size-model choice. Detectable ONLY through the lowered-cap reference compiler in run_size_term.sh §5: cap-rescue has a natural population of zero and the overrides are raise-only, so the bar's decline has no other witness in the tree"
SAB_DOC_FIGURE="CANONICAL RUN 2026-08-29 (run_sabotage_matrix.sh S192 at 48e9a90): sizeterm:1fail/21pass, corpus:0fail/21pass, reach:ok(1/1), both pops (RESCUE= and DPCREC_SIZE_TERM_THRESHOLD=20000) =1 -- DETECTED. The one red cell is run_size_term.sh section 5: '_UNROLL_K_WHY expected cap-rescue under the lowered cap, got size-model'. THAT IS THE WHOLE INSTRUMENT: the cell runs against a compiler built with -DPCREC_SIZE_TERM_THRESHOLD=20000 -DPCREC_MAX_VM_EMIT_CODE_BYTES=30000, and it is the ONLY place in the repository where the materiality bar is observed DECLINING. Note it cannot be reproduced by pointing a sabotaged binary at a clean tree -- section 5 builds its reference compiler from the tree under test, so the plant has to be in the SOURCE. THE GREEN CORPUS ARM IS THE POINT OF THE ROW: 21/21 on tests/size/size_term.rxt, and section 3's stamped K on the nested-N=8 subject is UNMOVED, because the bar accepts that rung by a wide margin.

RE-ANCHORED 2026-09-17 ([OPT-DIAL], lane dialimpl) after src/core/compile.c's
literal 75 became a 'bar' parameter (SIZE_TERM_BAR_DEFAULT, same value, moved
beside size_term_choose so the dial's own table -- src/core/tune.c -- has
somewhere to reach into). RE-RUN SOLO, tree a32bb6a35422835ae8349e566df241ba3fa81174 (bash tests/mech/run_sabotage_matrix.sh S192):
sizeterm:3fail/28pass, corpus:0fail/21pass, reach:ok(1/1), both pops
(RESCUE= and DPCREC_SIZE_TERM_THRESHOLD=20000) =1 -- DETECTED, unexpected: 0.
The suite's own pass/fail denominators grew since the 2026-08-29 figure
(21->28 passed, the sizeterm arm gained cells; 1->3 failed) but the ROW's
verdict and its one-instrument claim are unchanged: this is still the ONLY
cell in the tree that watches the materiality bar decline, run against the
same -DPCREC_SIZE_TERM_THRESHOLD=20000 -DPCREC_MAX_VM_EMIT_CODE_BYTES=30000
reference compiler. THE SECOND-WITNESS QUESTION, asked and answered by this
re-anchor rather than left implicit: now that the bar is a DIAL CELL reaching
95 at --tune=-2 and 85 at -1, does the bar's DECLINE gain a second, non-
reference-compiler witness anywhere in the tree? NO, for two independent
reasons. (1) DIRECTION: 'sel = best' fires when 'total[best]*100 <=
total[0]*bar', so a HIGHER bar is a WEAKER gate -- it accepts the argmin on a
SMALLER required saving, moving every dial position AWAY from a decline and
toward S192's own limit (bar->100 degenerates toward 'always keep the
argmin', the sabotage's own unconditional form) rather than toward it. Both
non-default positions (85, 95) can only shrink the population of patterns
whose bar DECLINES, never grow it. (2) MECHANISM: cap-rescue -- the only path
on which a decline is OBSERVABLE at all (see this row's header above) --
additionally requires the argmin to be declined AND THEN a fixed EMIT-SIZE
CAP (PCREC_MAX_EMIT_BYTES / PCREC_MAX_VM_EMIT_CODE_BYTES) to force a smaller
K anyway. Those caps are NOT DIAL CELLS (docs/spec/tuning.md §5.4: 'emitted-
size caps -- NOT A RUNG -- raise-only refusal boundaries; a dial that lowered
one would manufacture refusals'), so no --tune position ever narrows the gap
between 'the ladder is in scope' (the threshold cell, which -2/-1 DO lower)
and 'the artifact is over a cap' (unchanged at every position) -- the two
halves cap-rescue needs stay exactly as far apart as they are today. §6.1b's
own 81-new-pattern population (the -2 threshold's 40,000-byte reach) is
therefore not a population where cap-rescue becomes newly observable either:
those patterns enter the LADDER's scope, not the CAPS' range, which §6.2a
measured at 999,925 B against a 1,000,000 B cap -- two orders of magnitude
past anything the threshold alone moves. Verification OWED going forward
only in the sense every SAB_REACH is: re-run this row (or the mech tripwire)
whenever §5.4's ladder or cap rows next move by a ruled diff."
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/n8.c" -- "((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}" && grep -h _UNROLL_K "$REACH_TMP/n8.c"'
SAB_REACH_EXPECT="#define RX_UNROLL_K_WHY \"size-model\""
SAB_REACH_POP="tests/codegen/run_size_term.sh|RESCUE=|1
tests/codegen/run_size_term.sh|DPCREC_SIZE_TERM_THRESHOLD=20000|1"
SAB_COUNT=1
SAB_BEFORE='    if (best != 0 && total[best] * 100 <= total[0] * (size_t)bar) sel = best;'
SAB_AFTER='    if (best != 0) sel = best;   /* SABOTAGE S192 */'
