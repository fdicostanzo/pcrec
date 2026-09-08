# S-U11 ([M5.0] stage 1 by design, LANDED at stage 4; utf8_design.md §4.1.1,
# §8.2, ASK 3 RULED) -- THE STANDING 1:n FOLD CHECK IS LIVE.
#
# THE ODD ROW IN THIS TABLE, AND DELIBERATELY SO. Every other row sabotages
# the COMPILER and asks whether a check notices. This one sabotages A CHECK'S
# OWN EXPECTATION and asks whether the MATRIX notices -- because the fact it
# defends is a fact about libpcre2, which no amount of pcrec-side testing can
# reach. Its subject being the oracle is also why the design placed it at
# stage 1, four stages before the fold it defends; it landed here because
# stages 1-3 did not build it.
#
# THE CLAIM: libpcre2 10.46 implements SIMPLE case folding and no one-to-many
# folding at all -- 0 of 11 measured cells, under both `PCRE2_UTF|CASELESS`
# and `...|UCP`. The whole caseless lowering rests on it: a 1:n fold is a
# SEQUENCE, so its existence would force a caseless literal into an
# alternation and a caseless class to hold something a set cannot hold. The
# failure would be SILENT -- a future libpcre2 that gained full folding would
# simply start matching cells pcrec answers `no` to.
#
# THE SABOTAGE inverts the verdict test, so all 22 assertions demand a MATCH.
# Against a healthy oracle every one fails, which is the row scoring DETECTED.
# The floor below is 22 and not 11 on purpose: 11 would pass a check that had
# silently dropped the `PCRE2_UCP` arm, which is the arm a full-folding
# implementation is likeliest to reach first.
SAB_ID="S-U11-fold-1n-check-inverted"
SAB_FILE="tests/registry/pc4_check.c"
SAB_SUITES="registry"
SAB_DESC="the standing 1:n fold check asserts that ss-ligature cells DO match caseless, inverting the result the whole DD-1 lowering rests on"
SAB_DOC_FIGURE='MEASURED solo 2026-09-08: a clean run prints the fold block reading 22 assertions (11 cells x 2 option words), 0 matching, and PASSES; inverted, run_pc4.sh exits 1 with exactly 22 FAIL lines naming the design event.'
# THE REACH QUESTION FOR A ROW WHOSE SUBJECT IS A CHECK is whether the check
# is still WIRED, not whether the compiler can do something -- so the probe
# greps its call site. The POPULATION floor is 11 (the cells) rather than
# §8.2's 22, because the 22 is ASSERTED EXACTLY inside `check_1n_fold` itself,
# which sees a lost UCP arm that a grep for a string in this file cannot.
SAB_REACH='grep -c "check_1n_fold()" tests/registry/pc4_check.c'
SAB_REACH_EXPECT='^1$'
SAB_REACH_POP='tests/registry/pc4_check.c|^    \{ "|11'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            asserted++;
            if (rc >= 0)'
SAB_AFTER='            asserted++;
            if (rc < 0)   /* SABOTAGE S-U11: the assertion inverted */'
