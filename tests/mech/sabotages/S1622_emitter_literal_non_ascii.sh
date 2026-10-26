# S1622 -- [EMIT-BIDI] AN EMITTER'S STRING LITERAL CARRIES A NON-ASCII BYTE.
#
# The house rule is "emitted text is ASCII-only, comments included"
# (src/gen/CLAUDE.md). The emitters' own comment prose once carried em dashes
# and section signs that reached every `-fcomments` artifact. This row plants an
# em dash in one emitted literal (the rx_abi block's working-storage comment,
# present in every header); run_ctext_ascii.sh must go RED on the artifact
# ASCII arm AND on the string-literal scan of the emitter files.
SAB_ID="S1622-emitter-literal-non-ascii"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="an emitter string literal holds a raw em dash (U+2014); tests/codegen/run_ctext_ascii.sh must go RED on every label's pure-ASCII arm and on its [litscan] arm"
SAB_DOC_FIGURE="PREDICTED: run_ctext_ascii.sh RED on the ascii arm of every label and on the litscan arm (OWED: run_sabotage_matrix.sh S1622)."
SAB_COUNT=1
SAB_BEFORE='The caller-provided working storage (spec section 10).'
SAB_AFTER='The caller-provided working storage — (spec section 10).'
