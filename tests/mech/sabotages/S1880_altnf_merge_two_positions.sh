# S1880 ([RUN-POS-SET] stage 1, lane altbuild; docs/design/alt_normal_form.md
# §5 stage 1 S-a) -- THE OWNER'S MERGE ACCEPTS A PAIR DIFFERING IN TWO
# POSITIONS.
#
# Rule M folds two branches equal at every position but `p`. The plant widens
# the one key predicate (`anf_in_key`, read by the hash and the equality test
# alike) to drop position `p - 1` too, so `(?i)β`'s boxes `ce 92`, `ce b2`,
# `cf 90` fold into `ce [92 b2 90]`: a superset at one position and a lost
# member at the other. Answer witness (tests/utf8/altnf_lowering.rxt block
# 1): `ΐ` (`ce 90`) must not match and `ϐ` (`cf 90`) must; libpcre2 is the
# oracle, so the sabotaged tree is wrong against a source it shares nothing
# with.
SAB_ID="S1880-altnf-merge-two-positions"
SAB_FILE="src/opt/altnf.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8/altnf_lowering.rxt"
SAB_DESC="the alternation owner's sibling merge groups branches that differ in two positions, so (?i)beta's UTF-8 boxes fold into a superset at one byte and lose a member at the other"
SAB_DOC_FIGURE="PREDICTED: tests/utf8/altnf_lowering.rxt red on block 1 (n \\xce\\x90 matches, m \\xcf\\x90 fails) and the merged-run blocks; every other file unaffected."
SAB_REACH='"$PCREC" -e utf8 --features all -p rx --engine=vm -fno-cls-kit -fno-alt-island --emit-ir --pattern "(?i)β" | grep -o "alternation entry (2 branches)"'
SAB_REACH_EXPECT='alternation entry (2 branches)'
SAB_REACH_POP='tests/utf8/altnf_lowering.rxt|^pattern \(\?i\)β|2'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return i != p;'
SAB_AFTER='    return i != p && i + 1 != p;   /* SABOTAGE S1880: two positions left out of the key */'
