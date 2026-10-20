#!/usr/bin/env bash
# S1151 ([DD-11.5] P2c, lane ctxbuild; S341's former plant, kept) -- THE NO-BYTE
# START STATE READS AS IN THE SET. The forward machine's `s0` (no byte on the
# left at all) is closed under the machine's LAST context atom instead of atom 0,
# so a missing previous character reads as a member: `(?<!a)b` on "b" answers
# nomatch where libpcre2 answers (0,1). This was S341's plant until [DD-11.5]
# re-aimed S341 at the absent-index gate (R1); the property it guards (a
# four-cell row reads "absent" as out) is still live, so the plant moved here
# rather than retiring.
SAB_ID="S1151-ctx-s0-last-atom"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="ctxnode"
SAB_DESC="the DFA's no-byte-on-this-side start state s0 is closed under the last context atom instead of atom 0, so an absent side reads as in the set"
SAB_DOC_FIGURE='ctxnode arm: tests/ucp/ctxnode.rxt'"'"'s `(?<!a)b`/`(?<![a-c])\d`/`\b\w` cells at offset 0 disagree with libpcre2 (S341'"'"'s measured figure before its re-aim). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1151.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(?<![a-c])\\d" >/dev/null 2>&1 && grep -c "define RX_ENGINE \"dfa\"" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    d->s0 = make_state(cx, nfa, d, &m, &root, 1, true, true, UPC_PLAIN,'
SAB_AFTER='    d->s0 = make_state(cx, nfa, d, &m, &root, 1, true, true, m.natoms - 1,   /* SABOTAGE S1151 */'
