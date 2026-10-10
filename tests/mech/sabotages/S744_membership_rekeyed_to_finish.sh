#!/usr/bin/env bash
# S744 ([OPT-REVEND] L0, lane lfl0; docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md) -- a membership reader re-keyed to the FINISH selection (LR-S1, the shape revision 2 would have built): `dfa_table_name` takes the anchored machine from `dfa_match_is_unwrapped` instead of the path's members. It runs on VM hybrids (`pcrec_emit_dfa_scan_stamps`), where the finisher is the VM and FINISH has no row.
# Detector: tests/codegen/run_cand_oracle.sh: every hybrid witness aborts `no-row FINISH` (MEASURED by plant at landing: 27 checks fail); in the default build every forward+reverse hybrid compile crashes (`(a+)b` exits 139).
SAB_ID='S744-membership-rekeyed-to-finish'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle codegen'
SAB_DESC='dfa_table_name reads the anchored member off the FINISH selection: every forward+reverse hybrid hits a no-row FINISH selection'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S744.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a+)b" && grep -qF "#define RX_VM_PREFILTER \"hybrid\"" "$REACH_TMP/o.c" && echo REACH-HYBRID'
SAB_REACH_EXPECT='REACH-HYBRID'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-10 (lane revbuild, [OPT-REVEND] L2): the membership folds read dfa_member_machines; the plant still ORs the anchored member off the FINISH selection. Intent
# unchanged.
SAB_BEFORE='static int dfa_member_machines(Ctx *cx, const Dfa *out[3])
{
    unsigned m = cand_path_members(cx);'
SAB_AFTER='static int dfa_member_machines(Ctx *cx, const Dfa *out[3])
{
    unsigned m = cand_path_members(cx) | (dfa_match_is_unwrapped(cx) ? CAND_MA : 0);   /* SABOTAGE S744 */'
