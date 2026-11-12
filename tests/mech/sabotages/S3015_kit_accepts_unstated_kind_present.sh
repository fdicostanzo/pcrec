# S3015 — kit close-out (lane kclose; r8 review of S2a, SEAM-2).
#
# Plant: the kit accepts a kind whose `present` is UNSTATED (or unknown) at mf_art_begin.
# Detector: G2's api block (memfn/tests/g2/g2_gen.c, run under --gate-only by run_g2_gate.sh) hands mf_art_begin an analysis object whose kind is zero-initialized and one with state 3, each expected refused: api_fail 2.
SAB_ID="S3015-kit-accepts-unstated-kind-present"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="g2gate"
SAB_DESC='the kit accepts an analysis kind whose presence is UNSTATED (or unknown)'
SAB_DOC_FIGURE='PREDICTED: G2 gate api_fail 2; exact re-run: bash tests/mech/run_sabotage_matrix.sh S3015.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            return "a kind whose presence is UNSTATED or unknown (every kind "'
SAB_AFTER='            if (0) return "a kind whose presence is UNSTATED or unknown (every kind "   /* SABOTAGE S3015 */'
