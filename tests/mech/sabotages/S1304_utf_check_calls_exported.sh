# S1304 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: the -futf-check prologue calls the EXPORTED <prefix>_valid_upto rather than its static twin.
# Detector: the -fPIC object carries a PLT relocation against rx_valid_upto.
SAB_ID="S1304-utf-check-calls-exported"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="twins"
SAB_DESC='the -futf-check prologue calls the EXPORTED <prefix>_valid_upto rather than its static twin'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1304.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_enc_twin_mark(c);   /* the static twin, [FINDALL-NEXT] */'
SAB_AFTER='    /* SABOTAGE S1304 */'
