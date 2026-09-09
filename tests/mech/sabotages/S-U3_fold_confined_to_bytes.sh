# S-U3 ([M5.0] stage 4; utf8_design.md §4.2c, §8.2) -- THE FOLD HAPPENS ON
# CODE POINTS, BEFORE THE BYTE LOWERING.
#
# THE CLAIM, and it is the sharpest cell in §4: `[a-z]` caseless matches
# U+212A (3 bytes) and U+017F (2 bytes). By the time the set is byte ranges
# neither is adjacent to anything in `[a-z]`, so a fold applied as a post-pass
# over those ranges cannot reach them. That is `[DD-12] (5)`'s prediction
# confirmed and the ordering constraint the implementation must not get wrong.
#
# WHY THE SABOTAGE IS A CLAMP AND NOT THE DESIGN'S OWN EDIT. §8.2 writes the
# sabotage as "move it after the byte lowering", which is not expressible as a
# text substitution: the lowering is a separate pass (`src/opt/lower_enc.c`)
# running after the parser has already published the node, so "moving" the
# fold there is a rewrite rather than a hunk. What the row DEFENDS is an
# OBSERVABLE -- can the fold reach a partner outside the byte range -- and a
# fold running after the lowering has exactly one reach: the byte range. The
# clamp below produces that reach exactly, and produces the design's own
# stated symptom ("`[a-z]` still folds to `[A-Z]`; only U+212A/U+017F are
# lost") rather than an approximation of it.
#
# WHY THE ORDINARY CORPUS CANNOT SEE IT: every ASCII fold pair is inside the
# clamp, so the whole `byte` corpus and every ASCII cell of the utf8 corpus
# stay green. Only a cell whose partner encodes to more than one byte fires.
SAB_ID="S-U3-fold-confined-to-bytes"
SAB_FILE="src/core/fold.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8"
SAB_DESC="ucd_partners drops every fold partner above 0xFF, the exact reach a fold applied after the byte lowering would have, so [a-z] under -i loses U+212A and U+017F while still folding to [A-Z]"
SAB_DOC_FIGURE="MEASURED solo 2026-09-08 at the stage-4 landing: 207 passed / 30 FAILED over tests/utf8/fold.rxt + axis06_caseless_fold.rxt (237/0 clean); every ASCII cell stays green."
SAB_REACH='"$PCREC" -i -e utf8 -p rx -o - -- "[a-z]"'
# [mechreach fix, 2026-09-09] same defect as S-U1/S-U2: 'Pattern:  */' names
# an empty pattern, which emit_pattern_comment never produces -- this
# construct's real header reads 'Pattern: [a-z] */'. Never reachable since
# authoring (a3ba7de7); see S-U1's note for the trace.
SAB_REACH_EXPECT='Pattern: [a-z] */'
SAB_REACH_POP='tests/utf8/fold.rxt|^pattern \[a-z\]|3'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            pcrec_cpset_add(out, m, m);'
SAB_AFTER='            if (m <= 0xFFu)   /* SABOTAGE S-U3: byte-confined reach */
                pcrec_cpset_add(out, m, m);'
