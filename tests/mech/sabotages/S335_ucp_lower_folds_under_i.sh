# S335 ([UCP] U1) -- UCP `[:lower:]` FOLDS UNDER `(?i)`.
#
# THE CLAIM (ucp_design.md §1.3 rule 1, [O]): under UCP, `[:lower:]` and
# `[:upper:]` are FOLD-INERT — `(?i)[[:lower:]]` is exactly `[[:lower:]]` and
# does not match `A`, while `(?i)\p{Ll}` DOES fold. No spelling can carry
# that, which is why the definition is a set with a marker (DEFK_SET's
# `fold_inert`, T2's `inert` row).
#
# THE SABOTAGE clears the marker on the lower set, so T2 falls through to the
# fold row the encoding selects (Latin-1 under byte UCP) and `(*UCP)(?i)
# [[:lower:]]` gains `A-Z` and `À-Þ`. Every UCP answer without `(?i)` is
# unchanged, and `[:lower:]` under utf8 is wide and refused anyway — the byte
# tier is where the rule is observable at U1 (tests/ucp/byte.rxt).
SAB_ID="S335-ucp-lower-folds-under-i"
SAB_FILE="src/parse/mod_ucp.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/ucp/byte.rxt"
SAB_DESC="the UCP [:lower:] set loses its fold-inert marker, so (*UCP)(?i)[[:lower:]] matches A and \\xc9 under byte"
SAB_DOC_FIGURE="harness over tests/ucp/byte.rxt: (*UCP)(?i)[[:lower:]] and its [^...]/[...x] siblings flip on the uppercase subjects (red). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S335."
SAB_REACH='"$PCREC" --features classes,modifiers,ucp -p rx -o "$REACH_TMP/o0.c" --pattern "(*UCP)(?i)[[:lower:]]" >/dev/null 2>&1; echo $?'
SAB_REACH_EXPECT="0"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='SETDEF(pcrec_ucp_set_lower,    "ucp-lower",    false, true,  t_ll);'
SAB_AFTER='SETDEF(pcrec_ucp_set_lower,    "ucp-lower",    false, false, t_ll); /* SABOTAGE S335 */'
