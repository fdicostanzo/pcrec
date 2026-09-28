# S309 — [FINDINGS] B2 F-3: A PROVENANCE FIELD REACHES WHAT A COMPILE
# CONSUMES (src/parse/rxt_find.c, `link_from_source`): the copied counts
# absorb the block's `retrieved` date, so editing provenance — which the
# design rules moves NOTHING (R20, D123-2: "provenance edits move nothing") —
# moves the byte-rate, its digest and the stamp. The plant models every way
# provenance could leak into the consumed bytes (design §7's digest rule:
# "the digest covers exactly the bytes whose change could change what a
# reader sees").
#
# Detector: run_findings_tests.sh §6 #14 compiles one bundle under two
# `retrieved` dates and requires byte-identical artifacts.
SAB_ID="S309-findings-digest-reads-provenance"
SAB_FILE="src/parse/rxt_find.c"
SAB_SUITES="findings"
SAB_DESC="a data block's provenance (its retrieved date) is folded into the counts a chain link carries, so a provenance-only edit moves the byte-rate, the digest and every artifact built under the bundle — R20's 'provenance edits move nothing' broken"
SAB_DOC_FIGURE="findings red on §6 [#14] (a provenance-only edit MOVED the artifact); the one-row-edit half stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S309."
SAB_REACH='python3 "$TREE/tests/findings/res_fixtures.py" "$REACH_TMP/r" && "$PCREC" -p rx -I "$REACH_TMP/r/P1" --analysis prov -o "$REACH_TMP/a.c" --pattern "abc" && grep -q "^#define RX_FINDINGS \"byte-rate=prov:" "$REACH_TMP/a.c" && echo REACH-FINDINGS-S2-LINK-COPIED'
SAB_REACH_EXPECT="REACH-FINDINGS-S2-LINK-COPIED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        memcpy(c, fb->counts, 256 * sizeof *c);'
SAB_AFTER='        memcpy(c, fb->counts, 256 * sizeof *c);
        /* SABOTAGE S309: provenance leaks into the consumed values */
        if (src->nprovs && src->provs[0].retrieved && src->provs[0].retrieved[0])
            c[0x20] += (unsigned char)src->provs[0].retrieved[strlen(src->provs[0].retrieved) - 1];'
