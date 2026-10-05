#!/usr/bin/env bash
# S469 ([K82] (B), lane k82hbuild) -- THE VM'S \G ANCHOR MOVES WITH THE HANDOFF.
#
# No census hybrid mover carries a \G start family (litscan_k82h.md §3.1a),
# so the witness is constructed: (?:\Gab|x)(cat)(?=dog), a VM hybrid with an
# exact prefilter and K = 2 whose lookahead erases the prefilter-window
# ceiling (so the (d') decline does not apply). On "zzabcatdog" from 0 the
# answer is NOMATCH; with the \G anchor at the handoff (2) it is (2,7).
# Detector: handoff.rxt's \G-hybrid row and run_prechecks.sh §5.12g.
SAB_ID="S469-vm-gstart-moved"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/litscan/handoff.rxt"
SAB_DESC='the VM hybrid passes the handoff'\''s start into the VM'\''s own \G anchor (match_anchored'\''s search_from) instead of the caller'\''s startpos, so \Gab is tested at the moved start'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S469.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:\Gab|x)(cat)(?=dog)'\'' && grep -q '\''^#define RX_REQ_HANDOFF "2"'\'' "$REACH_TMP/o.c" && echo REACH-GSTART-HYBRID'
SAB_REACH_EXPECT='REACH-GSTART-HYBRID'
SAB_REACH_POP='tests/litscan/handoff.rxt|^pattern \(\?:\\Gab\|x\)\(cat\)\(\?=dog\)$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        v->ngst > 0 ? ", search_from" : "",'
SAB_AFTER='        v->ngst > 0 ? pcrec_sb_fragf(&v->cx->arena, ", %s", first) : "", /* SABOTAGE S469 */'
