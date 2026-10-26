# S1620 -- [EMIT-BIDI] THE COMMENT FRAME PASSES BYTES >= 0x80 RAW.
#
# The pre-fix state of the `-fcomments` map comment: a pattern holding U+200F
# (tests/modifiers/xmode_utf8.rxt:32,38) put a raw bidi control into a C
# comment, gcc's -Wbidi-chars warned and the harness's -Werror lost both cases
# on the -fcomments axis (job 624). The shared escaper's comment frame now
# numbers every non-printable-ASCII byte; this row lets the comment frame
# print a byte >= 0x80 as itself again (the string frame is untouched, so
# `.pattern` still round-trips and only the comment echoes go raw).
SAB_ID="S1620-ctext-comment-passes-high-bytes"
SAB_FILE="src/core/sb.c"
SAB_SUITES="codegen"
SAB_DESC="pcrec_sb_ctext's comment frame prints a byte >= 0x80 raw, so a pattern holding U+200E/U+200F puts a raw bidi control into the provenance line and the orientation block; tests/codegen/run_ctext_ascii.sh must go RED on its no-raw-bidi-byte and -Wbidi-chars arms"
SAB_DOC_FIGURE="PREDICTED: run_ctext_ascii.sh RED on the ascii + compile arms of every label (OWED: run_sabotage_matrix.sh S1620 in the day slot, lane emitbidi's job)."
SAB_COUNT=1
SAB_BEFORE='        else if (c >= 32 && c < 127) pcrec_sb_putc(sb, (char)c);'
SAB_AFTER='        else if (c >= 32 && (c < 127 || ctx != PCREC_CTEXT_STRING)) pcrec_sb_putc(sb, (char)c);   /* SABOTAGE S1620 */'
