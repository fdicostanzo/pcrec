# S1451 — the lookbehind branch split peels every A_ALT down the spine
# instead of exactly nbr - 1, so a first-branch group of alternatives is read
# as spine and the split runs past its array (K123). Lane langfix2.
SAB_ID="S1451-lookbehind-split-reads-group-as-spine"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_group_alt.rxt"
SAB_DESC="pcrec_lookbehind_branches: the loop also continues while the leftover node is an A_ALT, so (?<=(?:ab|cd))x is split as two branches against a count of one"
SAB_DOC_FIGURE="PREDICTED: tests/lookaround/lookbehind_group_alt.rxt's accepted blocks whose FIRST top-level branch is a group of alternatives fail (internal error, or a wrong split); blocks whose group is a later branch stay green. Canonical figure owed from run_sabotage_matrix.sh S1451."
SAB_COUNT=1
SAB_BEFORE="    out[0] = a;
}"
SAB_AFTER="    while (a->k == A_ALT && nbr == 1) { out[0] = a->r; a = a->l; }   /* SABOTAGE S1451 */
    out[0] = a;
}"
