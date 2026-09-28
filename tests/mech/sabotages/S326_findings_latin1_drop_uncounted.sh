# S326 — [FINDINGS] B5 `encode-latin1` DROPS SILENTLY (src/core/findings.c,
# `pcrec_find_derive_counts`): a code point above U+00FF is still dropped,
# but its count is no longer added to the drop total, so the listing's
# `dropped` column reads 0 — design §2.4's "larger code points are dropped,
# AND THE DETAILS LISTING SAYS HOW MANY" broken in its second half. The
# derived RATE does not move, so no stamp or digest can see it.
SAB_ID="S326-findings-latin1-drop-uncounted"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC="pcrec_find_derive_counts's encode-latin1 arm drops a code point above U+00FF without adding its count to the drop total — the rate is unchanged, the listing's dropped column reads 0"
SAB_DOC_FIGURE="findings: §12's 'via encode-latin1' derivation check and the 'dropped 12' check red; the latin1 stamp check stays green (the rate is unchanged). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S326."
# [MECH-REACH] the drop count reaches the listing: a derivation with nothing
# to drop still reports its (zero) drop count in the resolution row.
SAB_REACH='"$PCREC" --list-analysis weblog | awk -F"\t" "\$1 == \"byte-rate\" && \$2 == \"utf8\" { print \"dropped=\" \$8 }"'
SAB_REACH_EXPECT="dropped=0"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (dropped) *dropped += cps[i].count;'
SAB_AFTER='            /* SABOTAGE S326: the drop is not counted */'
