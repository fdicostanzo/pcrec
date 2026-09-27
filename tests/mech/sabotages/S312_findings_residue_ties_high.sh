# S312 — [FINDINGS] B2 F-6: THE NORMALIZATION'S RESIDUE GOES TO THE WRONG
# ENTRY (src/core/findings.c, `pcrec_find_normalize`): among equally large
# entries the residue lands on the HIGHEST byte instead of the lowest (design
# §2.5 step 4, "ties going to the lowest byte"). The table still sums to
# 1,000,000 and every entry keeps its floor, so the postcondition asserts
# pass — only the spec's own test vectors, computed by an independent
# implementation, can see which entry took the residue.
#
# Detector: run_findings_tests.sh §1's §2.5 vectors against findings_ref.py
# (the all-equal vector puts its residue of 64 on byte 0x00, not 0xff).
SAB_ID="S312-findings-residue-ties-high"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC="the normalization's residue goes to the highest of the tied largest entries instead of the lowest, so a table of equal counts puts its rounding residue on 0xff — every sum and floor still holds and only the independent test vectors can see it"
SAB_DOC_FIGURE="findings red on §1 (the §2.5 test vectors disagree with findings_ref.py) and on every §6 fixture whose bundle has tied maxima. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S312."
SAB_REACH='"$PCREC" -p rx -I "$TREE/tests/findings/adversarial" --analysis uniform -o "$REACH_TMP/a.c" --pattern "abc" && grep -q "^#define RX_FINDINGS \"byte-rate=uniform:" "$REACH_TMP/a.c" && echo REACH-FINDINGS-NORMALIZE-TIES'
SAB_REACH_EXPECT="REACH-FINDINGS-NORMALIZE-TIES"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (ppm[b] > ppm[big]) big = b;'
SAB_AFTER='        if (ppm[b] >= ppm[big]) big = b;   /* SABOTAGE S312: residue ties to the highest byte */'
