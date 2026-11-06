# S1886 ([RUN-POS-SET] stage 2p, lane altbuild; docs/design/alt_normal_form.md
# §5 stage 2p S-p) -- THE DESCRIPTION'S CAT PRODUCT KEEPS ONLY THE SHORTEST
# GROUP.
#
# `pcrec_pd_cat` forms every left group before every right group and merges
# equal total widths. The plant keeps the product's shortest group alone, so
# `(?i)москва` (four pieces, widths 12-15) lists one group and declines
# `one-group`, and `(?i)abcdKefgh` loses its 11-byte Kelvin piece. A FACT
# witness: the piece set is inert, no answer can move (lesson 1, stated);
# [facts-pieces] holds the fact to an independent model's value
# (docs/dev/lanes/altbuild_evidence/p2_model.py), the answer witness ships
# with the piece set's first consumer.
SAB_ID="S1886-pieces-cat-shortest-group"
SAB_FILE="src/facts/desc.c"
SAB_SUITES="facts"
SAB_DESC="the piece description's concatenation keeps only its shortest width group, so (?i)москва lists one piece where the model has four"
SAB_DOC_FIGURE="PREDICTED: facts:1fail -- [facts-pieces] (ci-moskva, the Kelvin fold class and a(?:bc|d)e read one-group)."
SAB_REACH='"$PCREC" -e utf8 --emit-facts=utf8 --pattern "(?i)москва" | grep -c "15:\["'
SAB_REACH_EXPECT='1'
SAB_REACH_POP='tests/codegen/run_facts_checks.sh|\(\?i\)москва|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return pd_norm(cx, c, g, k);'
SAB_AFTER='    PdDesc o = pd_norm(cx, c, g, k);
    if (o.ng > 1) o.ng = 1;   /* SABOTAGE S1886: the shortest group alone */
    return o;'
