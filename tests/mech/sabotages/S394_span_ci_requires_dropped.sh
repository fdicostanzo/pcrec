# S394 ([CLS-TREE] S4, lane s4build) -- THE CASELESS SPAN COMPARE STOPS
# REQUIRING THE DECODER.
#
# utf8's `$_span_match_caseless` calls `$_decode` since S4 retired its private
# copy, and PcrecEncEntry.requires is what puts the decoder in the artifact
# when no wide class did. The plant clears that column: a caseless
# backreference artifact under utf8 with no wide class calls an undefined
# static function and does not build.
SAB_ID="S394-span-ci-requires-dropped"
SAB_FILE="src/enc/enc_utf8.c"
SAB_SUITES="wclass"
SAB_DESC="the utf8 SPAN_CASELESS entry's requires column is cleared, so an artifact whose only caller of \$_decode is the caseless span compare omits the decoder"
SAB_DOC_FIGURE="PREDICTED: wclass [K6] red."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      u8_defs_bref_ci_doc,    u8_defs_bref_ci,
      PCREC_ENCE_DECODE, false },'
SAB_AFTER='      u8_defs_bref_ci_doc,    u8_defs_bref_ci,
      0, false },'
