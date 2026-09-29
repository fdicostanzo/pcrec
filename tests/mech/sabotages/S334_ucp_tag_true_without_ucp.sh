# S334 ([UCP] U1) -- A `DEF_UCP` TAG ANSWERS TRUE WITHOUT UCP.
#
# THE CLAIM (ucp_design.md §1.2/§1.4, D130 Q1): UCP is OPT-IN. `\d` means
# `[0-9]` under `-e utf8` unless `(*UCP)`/`--ucp` says otherwise — PCRE2_UTF's
# own default, and D26 makes the answer the exact tier: a UCP-free artifact
# must be byte-identical to the pre-UCP compiler's.
#
# THE SABOTAGE drops the `ucp` conjunct from DEF_UCP_D's predicate, so every
# `\d`/`\D` in every compile resolves to its UCP definition. Under `byte` the
# UCP digit set clamps to `[0-9]` and nothing moves there — which is why the
# witness is utf8: tests/ucp/sets_utf8.rxt's no-UCP `\d` control on U+0660
# (ARABIC-INDIC DIGIT ZERO) flips nomatch -> match, and knobs.rxt's `(?aD)`
# no-UCP control stays right while the `(*UCP)(?aD)` cells stay right too —
# only the controls can see it.
SAB_ID="S334-ucp-tag-true-without-ucp"
SAB_FILE="src/parse/definitions.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/ucp"
SAB_DESC="DEF_UCP_D answers true whenever aD is unset, UCP or not, so every utf8 \\d becomes \\p{Nd}"
SAB_DOC_FIGURE="harness over tests/ucp: the no-UCP \\d control blocks read U+0660 (and the other Nd subjects) as matches (red). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S334."
SAB_REACH='"$PCREC" -e utf8 -p rx -o "$REACH_TMP/o0.c" --pattern "\\d" >/dev/null 2>&1; echo $?'
SAB_REACH_EXPECT="0"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        return cx->mods->ucp && !(cx->mods->arestrict & PARSE_ARESTRICT_D);'
SAB_AFTER='        return !(cx->mods->arestrict & PARSE_ARESTRICT_D); /* SABOTAGE S334 */'
