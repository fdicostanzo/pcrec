# S338 ([UCP] U2) -- T3 ACCEPTS A TWO-CHARACTER BODY.
#
# THE CLAIM (ucp_design.md §2.2, §6 U2's sabotage list): T3's `ctx-node` row
# applies only when the lookaround body's LANGUAGE is a set of single
# characters. `(?<=ab)` is width two — a context node reads ONE character on
# each side and cannot express it (§2.2's "what stays a lookaround").
#
# THE SABOTAGE drops the "exactly one element carries the character" test
# for the last element of a concatenation, so `(?<=ab)x` is recognized as
# `(?<=a)x`: "ax" matches where libpcre2 answers nomatch.
SAB_ID="S338-t3-two-character-body"
SAB_FILE="src/parse/ctxnode.c"
SAB_SUITES="ctxnode"
SAB_DESC="T3's language test lets a two-element concatenation through (keeping its first character), so (?<=ab)x becomes (?<=a)x"
SAB_DOC_FIGURE="ctxnode arm: tests/ucp/ctxnode.rxt's \`(?<=ab)x\` on \"ax\" matches (libpcre2: nomatch). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S338."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(?<=ab)x" >/dev/null 2>&1; echo $?'
SAB_REACH_EXPECT="0"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                if (one) return false;
                one = a;'
SAB_AFTER='                one = a;   /* SABOTAGE S338 */'
