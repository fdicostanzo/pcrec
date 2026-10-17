# S984 — [KNOW-SRC] K3 (docs/design/measure_sets.md rev 3 §8.5 [r2 M3b],
# §9.6): THE CANONICAL WRITER DROPS `serves` DATA CONSISTENTLY. §8.5 states
# the plant as "drops every `serves … when … via` declaration"; a `serves`
# line is REQUIRED in a data block (rxt_format.md §1.10¶5), so dropping every
# one makes the canonical view refuse to load and R1 goes red too. The row's
# point — a `serves` loss `rows_digest` does not see, which R1 and R2 cannot
# catch — is kept by dropping every encoding after the first of each `when`
# list (`byte,utf8` -> `byte`): the view loads, the item digest is unmoved,
# the re-listing is a fixed point, and only R3 (analyze/'s reader, the
# deliberate twin) sees the document change.
#
# Detector: run_knowledge_tests.sh R3 on every item with a two-encoding
# `serves` list (kfixtures kline, the adversarial bundles, res_fixtures'
# byte,utf8 bundles) and the R3 serves control's premise.
SAB_ID="S984-ksrc-canonical-drops-serves-encodings"
SAB_FILE="src/parse/ks_analysis.c"
SAB_SUITES="knowledge"
SAB_DESC="the analysis kind's canonical writer keeps only the first encoding of each serves line's when-list (byte,utf8 -> byte): R1 and R2 stay green, R3 alone must catch it"
SAB_DOC_FIGURE="knowledge red on R3 for every item with a two-encoding serves list. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S984."
SAB_REACH='"$PCREC" -I "$TREE/tests/findings/adversarial" --list-analysis uniform --view=canonical | grep -q "serves byte-rate when byte,utf8 via" && echo REACH-KSRC-CANON-SERVES-LIST'
SAB_REACH_EXPECT="REACH-KSRC-CANON-SERVES-LIST"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            pcrec_sb_printf(&sb, "        serves %s when %s via %s\n",'
SAB_AFTER='            pcrec_sb_printf(&sb, "        serves %s when %.4s via %s\n",   /* SABOTAGE S984 */'
