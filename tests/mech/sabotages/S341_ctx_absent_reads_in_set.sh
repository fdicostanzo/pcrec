# S341 ([UCP] U2) -- AN ABSENT SIDE READS AS IN THE SET.
#
# THE CLAIM (ucp_design.md §2.2): an A_CTX's truth function reads "absent"
# (the start or the end of the subject) as NOT in its set — `\b` at 0 before
# a word character is a boundary, `(?<!a)b` matches at 0. The DFA spells
# "absent" as atom 0, the empty membership vector, and the forward machine's
# `s0` is closed under it.
#
# THE SABOTAGE closes `s0` under the machine's LAST atom instead — the one
# whose vector carries the most sets — so at offset 0 the missing previous
# character reads as a member: `(?<!a)b` on "b" answers nomatch where
# libpcre2 answers (0,1).
SAB_ID="S341-ctx-absent-reads-in-set"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="ctxnode"
SAB_DESC="the DFA's no-byte-on-this-side start state s0 is closed under the last context atom instead of atom 0, so an absent side reads as in the set"
SAB_DOC_FIGURE="ctxnode arm: tests/ucp/ctxnode.rxt's \`(?<!a)b\`/\`(?<![a-c])\\d\`/\`\\b\\w\` cells at offset 0 disagree with libpcre2. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S341."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(?<![a-c])\\d" >/dev/null 2>&1 && grep -c "define RX_ENGINE \"dfa\"" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    d->s0 = make_state(cx, nfa, d, &m, &root, 1, true, true, UPC_PLAIN,'
SAB_AFTER='    d->s0 = make_state(cx, nfa, d, &m, &root, 1, true, true, m.natoms - 1,   /* SABOTAGE S341 */'
