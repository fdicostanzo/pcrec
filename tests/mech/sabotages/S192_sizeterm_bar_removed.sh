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
SAB_DOC_FIGURE="PLACEHOLDER -- written 2026-08-29 (lane artsize3), CANONICAL RUN OWED (bash tests/mech/run_sabotage_matrix.sh S192). PREDICTED: sizeterm:1fail (§5's cap-rescue cell reads _UNROLL_K_WHY 'size-model' where it requires 'cap-rescue'; the sibling 'different K' cell still passes), corpus:0fail on tests/size/size_term.rxt. Replace this line with the measured row and the arm figures."
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/n8.c" -- "((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}" && grep -h _UNROLL_K "$REACH_TMP/n8.c"'
SAB_REACH_EXPECT="#define RX_UNROLL_K_WHY \"size-model\""
SAB_REACH_POP="tests/codegen/run_size_term.sh|RESCUE=|1
tests/codegen/run_size_term.sh|DPCREC_SIZE_TERM_THRESHOLD=20000|1"
SAB_COUNT=1
SAB_BEFORE='    if (best != 0 && total[best] * 100 <= total[0] * 75) sel = best;'
SAB_AFTER='    if (best != 0) sel = best;   /* SABOTAGE S192 */'
