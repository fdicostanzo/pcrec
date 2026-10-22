# S1453 — the octal escape's ceiling is \377 under every encoding again, so
# `\400` refuses under utf8 (K125). Lane langfix2.
SAB_ID="S1453-octal-ceiling-byte-only"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8/octal_wide.rxt"
SAB_DESC="pcrec_clsport_octal: the ceiling test is val > 0xff instead of the encoding's universe"
SAB_DOC_FIGURE="PREDICTED: every utf8 block of tests/utf8/octal_wide.rxt with a value above \\377 fails as a pattern-compile failure; the \\1000 control and the two byte perr controls stay green. Canonical figure owed from run_sabotage_matrix.sh S1453."
SAB_COUNT=1
SAB_BEFORE="    if ((unsigned)val > cls_universe(cx)) {"
SAB_AFTER="    if (val > 0xff) {   /* SABOTAGE S1453 */"
