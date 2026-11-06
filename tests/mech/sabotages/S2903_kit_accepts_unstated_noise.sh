# S2903 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (d);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (d) the kit accepts a row whose noise state is UNSTATED (or unknown).
# Detector: G2's api block (memfn/tests/g2/g2_gen.c, run under --gate-only by run_g2_gate.sh) hands mf_art_begin a zero-initialized mf_measure and a state 3, each expected refused: api_fail 2.
SAB_ID="S2903-kit-accepts-unstated-noise"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="g2gate"
SAB_DESC='(d) the kit accepts a row whose noise state is UNSTATED (or unknown)'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2903.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            return "a row whose noise state is UNSTATED or unknown (MF_SITE_ABI 24: "'
SAB_AFTER='            if (0) return "a row whose noise state is UNSTATED or unknown (MF_SITE_ABI 24: "   /* SABOTAGE S2903 */'
