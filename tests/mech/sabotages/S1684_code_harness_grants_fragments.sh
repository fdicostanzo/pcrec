# S1684 ([INLINE-C] stage 2, design 9.1 S-IC29) -- THE HARNESS PASSES THE
# OPT-IN TO FRAGMENT BLOCKS. A section's `allow-code` manifest line is meant
# for its ENTRY files only (design 5.2): code a fragment brings in through an
# `include` is reached code. With the entry test removed the harness grants
# the fragment's blocks too. Witness: tests/code/frag/frag_code.rxt, whose
# code block expects the refusal.
SAB_ID="S1684-code-harness-grants-fragments"
SAB_FILE="tests/harness/run.sh"
SAB_SUITES="code"
SAB_DESC="tests/harness/run.sh passes the manifest's --allow-code to fragment blocks as well as to entry files"
SAB_REACH='grep -c "include \"frag_code.rxt\"" "$TREE/tests/code/frag/entry.rxt"'
SAB_REACH_EXPECT='1'
SAB_COUNT=1
SAB_BEFORE='    rxt_is_entry "$rxt" || return 0'
SAB_AFTER='    true || return 0   # SABOTAGE S1684'
