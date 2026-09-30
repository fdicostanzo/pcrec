# S412 — [UTF-VALID] THE LB STEP-BACK STEPS ONE BYTE PER CHARACTER
# (src/enc/enc_utf8.c, `$_valid_upto`): the skip back over continuation
# bytes is dropped, so each of LB characters is one byte. That is the
# naive walk utf_valid_design.md §1.3 (critic r2 F3) measured PCRE2 does NOT
# take: PCRE2 steps one byte and then over EVERY continuation byte. On a
# well-formed multi-byte character before startpos the walk now lands INSIDE
# it and reports its continuation byte as ill-formed.
#
# WHAT SEES IT: tests/utfcheck's §1.3 pinned rows (`(?<=a)b` on
# `\x80\x80\x80b` from 3: libpcre2 -22 at 0, the one-byte walk reports 2)
# and the `align`/`random` rows with a multi-byte character before a
# lookbehind's startpos.
SAB_ID="S412-utf-stepback-one-byte"
SAB_FILE="src/enc/enc_utf8.c"
SAB_SUITES="utfcheck"
SAB_DESC="valid_upto's LB step-back moves one byte per character instead of PCRE2's raw walk (one byte, then back over every continuation byte), so the checked range starts inside a character and the refusal set and offsets move"
SAB_DOC_FIGURE="docs/design/utf_valid_design.md §1.3 (the raw walk, measured). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S412"
SAB_REACH='"$PCREC" -p rx -e utf8 -futf-check --features all -o "$REACH_TMP/o.c" --pattern "(?<=a)b" && grep -qF "#define rx_VALID_LB 1" "$REACH_TMP/o.c" && echo REACH-STEPBACK'
SAB_REACH_EXPECT="REACH-STEPBACK"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        while (p > 0 && (s[p] & 0xC0u) == 0x80u) p--;\n"'
SAB_AFTER='"        /* SABOTAGE S412 */\n"'
