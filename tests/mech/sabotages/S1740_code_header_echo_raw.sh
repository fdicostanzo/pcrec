# S1740 ([INLINE-C] stage 2, lane ic2d27land, D27 finding F1) -- A REFUSED
# `--code-header` VALUE IS ECHOED THROUGH THE FRAME-ONLY ESCAPE again:
# control bytes go out by number but a Bidi_Control byte run reaches the
# terminal raw, in pcrec's own diagnostic (the match_api.md §11.9¶3 reason).
# Witness: tests/code/d27 (arm 12): hdr_bidi_refused's stderr must hold the
# escaped bytes and no raw byte.
SAB_ID="S1740-code-header-echo-raw"
SAB_FILE="cli/main.c"
SAB_SUITES="code"
SAB_DESC="the --code-header refusal echoes the value through pcrec_sb_text, so a non-ASCII byte (a bidi control) reaches stderr raw"
SAB_REACH='"$PCREC" --allow-code=c $'\''--code-header=c:"a\xe2\x80\xaeb.h"'\'' -o "$REACH_TMP/o.c" --pattern '\''a(?C`c: return RX_PASS;`)b'\'' 2>&1 | grep -c "got .c:"'
SAB_REACH_EXPECT='1'
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_ctext(&b, (const unsigned char *)v, strlen(v), PCREC_CTEXT_COMMENT);
    cli_err("--code-header: %s'
SAB_AFTER='    pcrec_sb_text(&b, v);   /* SABOTAGE S1740 */
    cli_err("--code-header: %s'
