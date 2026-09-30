# S340 ([UCP] U2) -- THE BYTE-EXPRESSIBILITY PRECONDITION SKIPPED FOR A
# NON-ASCII SET UNDER UTF-8.
#
# THE CLAIM (ucp_design.md §2.3): the all-byte DFA (and the VM's one-byte
# test) implements a context set exactly iff every member is ONE byte of the
# encoding — any set under `-e byte`, an ASCII-only set under `-e utf8`.
# `pcrec_enc_set_bytes` is that precondition, asked by every site that turns
# a context set into bytes; a set that fails it keeps its lookaround.
#
# THE SABOTAGE makes the precondition CLAMP instead of refuse: the set's
# members up to 0xFF become bytes and the rest are dropped. `(?<=[^a])a`
# under utf8 then reads the stray continuation byte 0x80 as "in [^a]" and
# answers (1,2) on `80 61` — §2.3's measured hazard — where libpcre2
# (UTF|MATCH_INVALID_UTF) answers nomatch. It must be caught by the hazard
# cell, not by an answer on an ASCII subject.
SAB_ID="S340-ctx-precondition-clamps"
SAB_FILE="src/enc/enc.c"
SAB_SUITES="ctxnode"
SAB_DESC="pcrec_enc_set_bytes clamps a context set to its one-byte members instead of refusing it, so a non-ASCII set under utf8 becomes a (sampled) byte context"
SAB_DOC_FIGURE="ctxnode arm: tests/utf8/axis13_ctx_illformed.rxt's \`(?<=[^a])a\` on \"\\x80a\" matches (1,2) (libpcre2 MIU: nomatch). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S340."
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o "$REACH_TMP/o0.c" --pattern "(?<=[^a])a" >/dev/null 2>&1; echo $?'
SAB_REACH_EXPECT="0"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (iv[i].hi > e->onebyte_max) return false;
        for (unsigned c = iv[i].lo; c <= iv[i].hi; c++)'
SAB_AFTER='        if (iv[i].lo > 0xFFu) continue;   /* SABOTAGE S340 */
        for (unsigned c = iv[i].lo; c <= (iv[i].hi > 0xFFu ? 0xFFu : iv[i].hi); c++)'
