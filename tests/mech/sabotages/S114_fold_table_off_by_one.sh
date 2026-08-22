# S114 (design row S-BR11) — THE RESIDUAL ENTRY'S FOLD DIVERGES FROM
# `cls_casefold` BY ONE BYTE.
#
# R32 E8's shape, as a row. A caseless backreference CANNOT fold at parse time
# — its operand is subject text nobody has seen — so pcrec's ASCII fold exists
# TWICE: once as the class widener `cls_casefold` applies (D23), and once as
# arithmetic inside the encoding residual `$_bref_match_caseless`. Two
# spellings of one fact is the shape this project keeps cataloguing, and the
# first design's answer ("reuse the same table as `\b`") was not available:
# `cls_casefold` is a bitmap WIDENER, not a byte-to-byte map, and nothing in
# `src/gen/enc/` can call a `static` function in `src/parse/`.
#
# SO THE FOLD BECAME AN OBJECT (`pcrec_ascii_fold`, src/core/fold.c) that
# `cls_casefold` DERIVES from, and the agreement is asserted by a MECHANISM
# rather than a comment: `tests/backrefs/fold_agreement_check.c` walks all
# 65,536 byte pairs comparing the SHIPPED residual entry — compiled out of an
# artifact pcrec actually emitted — against that table.
#
# THIS MOVES ONE BYTE ('z' stops folding), which is the smallest divergence
# the check must still see. A caseless corpus that happened to use no `z` would
# not.
SAB_ID="S114-fold-table-off-by-one"
SAB_FILE="src/gen/enc/enc_byte.c"
SAB_SUITES="brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/caseless.rxt"
SAB_DESC="The caseless residual entry's fold covers A-Y instead of A-Z, so a caseless backreference stops folding 'Z'/'z' while pcrec's class fold still does. Two spellings of one fact drifting by ONE BYTE is what the 65,536-pair agreement check exists to see; a corpus that used no 'z' would not"
SAB_DOC_FIGURE="PREDICTED: the fold-agreement check RED on the 'Z'/'z' pair; brefdiff RED if a caseless cell uses it. Canonical figure owed from run_sabotage_matrix.sh S114."
SAB_COUNT=1
SAB_BEFORE="\"        if (x >= 'A' && x <= 'Z') x = (unsigned char)(x + 32);\\n\""
SAB_AFTER="\"        if (x >= 'A' && x <= 'Y') x = (unsigned char)(x + 32);\\n\"   /* SABOTAGE S114 */"
