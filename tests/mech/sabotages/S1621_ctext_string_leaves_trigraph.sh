# S1621 -- [EMIT-BIDI] THE STRING FRAME STOPS ESCAPING `?`.
#
# `?` is backslash-escaped in the string frame so no pair it writes can begin
# a trigraph (`-Wtrigraphs` is part of -Wall, so -Werror makes an unescaped
# `??(` in `.pattern` a compile failure). This row deletes the `?` row from
# the escaper's declared table; the check's pattern holds `??(`.
SAB_ID="S1621-ctext-string-leaves-trigraph"
SAB_FILE="src/core/sb.c"
SAB_SUITES="codegen"
SAB_DESC="pcrec_sb_ctext's string frame no longer escapes '?', so a pattern holding '??(' puts a trigraph into rx_info.pattern; run_ctext_ascii.sh must go RED on its compile arm"
SAB_DOC_FIGURE="PREDICTED: run_ctext_ascii.sh RED on the compile arm of every label (OWED: run_sabotage_matrix.sh S1621 in the day slot)."
SAB_COUNT=1
SAB_BEFORE='    { CTX_BIT(PCREC_CTEXT_STRING),          -1,  '"'"'?'"'"',  "\\?"  },'
SAB_AFTER='    /* SABOTAGE S1621: the ? row removed */'
