# S338 ([UCP] U2) -- T3 ACCEPTS A TWO-CHARACTER BODY.
#
# THE CLAIM (ucp_design.md §2.2, §6 U2's sabotage list): T3's `ctx-node` row
# applies only when the lookaround body's LANGUAGE is a set of single
# characters. `(?<=ab)` is width two — a context node reads ONE character on
# each side and cannot express it (§2.2's "what stays a lookaround").
#
# THE SABOTAGE makes a concatenation read as its leading element instead of
# declining, so `(?<=ab)x` is recognized as `(?<=a)x`: "ax" matches where
# libpcre2 answers nomatch. (Re-aimed by [FLAG-SPELL], lane flagfix,
# 2026-10-24: the CAT arm's empty-skipping loop it used to plant into is gone,
# since p_cat drops such empties; the arm now declines every concatenation,
# and the intent -- a two-character body let through, keeping its first
# character -- is unchanged.)
SAB_ID="S338-t3-two-character-body"
SAB_FILE="src/parse/ctxnode.c"
SAB_SUITES="ctxnode"
SAB_DESC="T3's language test reads a concatenation as its first element, so (?<=ab)x becomes (?<=a)x"
SAB_DOC_FIGURE="ctxnode arm: tests/ucp/ctxnode.rxt's \`(?<=ab)x\` on \"ax\" matches (libpcre2: nomatch). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S338."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(?<=ab)x" >/dev/null 2>&1; echo $?'
SAB_REACH_EXPECT="0"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        case A_CAT:
            return false;'
SAB_AFTER='        case A_CAT:
            a = a->l; continue;   /* SABOTAGE S338 */'
