# S1393 — the D65 built-status probe asks only the default encoding again,
# so `(*UTF)a`/`(*UTF8)a` read `unbuilt` (speclang finding 9). The registry
# check's population pin (142 = 114 + 12 + 16) catches it. Lane langfix.
SAB_ID="S1393-built-status-byte-only"
SAB_FILE="src/dump/syntax_dump.c"
SAB_SUITES="registry"
SAB_DESC="pcrec_construct_built_status: only PCREC_ENC_BYTE is probed"
SAB_DOC_FIGURE="PREDICTED: the registry arm's built-status POPULATION MOVED line (112 + 14 against 114 + 12). Canonical figure owed from run_sabotage_matrix.sh S1393."
SAB_COUNT=1
SAB_BEFORE="    for (int enc = PCREC_ENC_BYTE; pcrec_enc_by_id(enc); enc++)"
SAB_AFTER="    for (int enc = PCREC_ENC_BYTE; enc == PCREC_ENC_BYTE; enc++)"
