# S3601 -- [ARENA-SCOPES] R1/F1, design sabotage (8) (lane arenabuild,
# 2026-11-25): `pcrec_sb_adopt` accepts arena storage (design D-6).
#
# Adopt moves HEAP storage and frees the destination's old buffer: arena
# storage on either side would be handed to `free`. The plant drops the
# refusal. Net: scope_check's D-6 checks (core), which require the refusal.
SAB_ID="S3601-adopt-takes-arena-storage"
SAB_FILE="src/core/sb.c"
SAB_SUITES="core"
SAB_DESC="pcrec_sb_adopt no longer refuses a StrBuf with arena storage (.ar): scope_check's D-6 checks read no refusal"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3601."
SAB_REACH_POP="tests/core/scope_check.c|D-6: pcrec_sb_adopt|2"
SAB_COUNT=1
SAB_BEFORE='    if (dst->ar || src->ar) {'
SAB_AFTER='    if (0) {   /* SABOTAGE S3601: arena storage is adopted */'
