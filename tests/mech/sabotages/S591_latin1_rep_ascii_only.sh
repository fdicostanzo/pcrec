# S591 ([K94]) — THE LATIN-1 FOLD REPRESENTATIVE STOPS AT ASCII.
#
# `pcrec_fold_latin1_rep` (src/core/fold.c) is what the seam's generated UCP
# caseless table is built from. THIS ROW LETS ONLY ASCII MEMBERS BE
# REPRESENTATIVES, so the generated table folds a-z and nothing in
# 0xC0..0xFE: the match-time fold silently disagrees with the `--ucp` class
# fold about every accented pair. The agreement check against
# `pcrec_fold_latin1` (tests/backrefs/fold_agreement_ucp_check.c, brefdiff
# section 9c) is the only control with two independent sources here.
SAB_ID="S591-latin1-rep-ascii-only"
SAB_FILE="src/core/fold.c"
SAB_SUITES="brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/caseless_ucp.rxt"
SAB_DESC="pcrec_fold_latin1_rep only lets ASCII members represent a fold class, so a --ucp byte artifact's caseless table covers the 26 ASCII pairs and none of the 30 Latin-1 ones, while the --ucp classes still fold all 56. The match-time fold and the class fold drift apart over exactly the non-ASCII pairs"
SAB_DOC_FIGURE="PREDICTED: fold_agreement_ucp_check RED on 0xC0..0xFE pairs (brefdiff 9c); caseless_ucp.rxt Latin-1 cells RED. Canonical figure owed from run_sabotage_matrix.sh S591."
SAB_COUNT=1
SAB_BEFORE="        if (m <= 0xFFu && m < rep) rep = m;"
SAB_AFTER="        if (m < 0x80u && m < rep) rep = m;   /* SABOTAGE S591 */"
