# S961 — [KNOW-SRC] K3 (docs/design/measure_sets.md rev 3 §8.5, §9.6), mapped
# to the ANALYSIS kind: THE CANONICAL WRITER OMITS DATA THE ITEM DIGEST DOES
# NOT COVER. §8.5 wrote this row for the measures kind's `cells` section; the
# analysis kind's analogue is the bundle's own `description` (a section of the
# document that `rows_digest`, the ITEM digest, does not fold), dropped
# CONSISTENTLY: the canonical view loads, its re-listing omits it again, so
# R1 (the digest) and R2 (the fixed point) both stay green. Only R3 — the
# canonical file and the original read as DOCUMENTS by analyze/'s
# independent reader — can see it.
#
# Detector: run_knowledge_tests.sh R3 on every item with a description
# (shipped default, kfixtures kfull/kline) and the R3 control.
SAB_ID="S961-ksrc-canonical-drops-description"
SAB_FILE="src/parse/ks_analysis.c"
SAB_SUITES="knowledge"
SAB_DESC="the analysis kind's canonical writer omits the bundle's description: R1 and R2 stay green (rows_digest does not cover it, and the re-listing omits it again), R3 alone must catch it"
SAB_DOC_FIGURE="MEASURED 2026-10-17 at 66c51d710: knowledge:14fail/198pass, every failure R3 (shipped default, kfixtures kfull/kline, the 11 adversarial bundles; R1 and R2 green on all). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S961."
SAB_REACH='"$PCREC" --list-analysis default --view=canonical | grep -q "^    description " && echo REACH-KSRC-CANON-DESCRIPTION'
SAB_REACH_EXPECT="REACH-KSRC-CANON-DESCRIPTION"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        canon_line(&sb, 4, "description", row->description, true);'
SAB_AFTER='        (void)0;   /* SABOTAGE S961: the description is not written */'
