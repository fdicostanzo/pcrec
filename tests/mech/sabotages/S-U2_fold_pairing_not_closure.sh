# S-U2 ([M5.0] stage 4; utf8_design.md §4.2a, §8.2) -- THE FOLD IS A CLOSURE.
#
# THE CLAIM: a fold class may have MORE THAN TWO members, so the constructor
# must close the set under the fold relation rather than "add the other case".
# MEASURED: `k` <-> `K` <-> U+212A are one class of three, `s` <-> `S` <->
# U+017F another, and 27 classes in the vendored data have three or four
# members. A partner map gets every one of them wrong.
#
# WHY IT IS INVISIBLE WITHOUT A THIRD-MEMBER CELL: `k`/`K` still works under
# the sabotage -- every two-member class is unaffected, which is 1,427 of the
# 1,454 -- so a corpus of ASCII fold pairs passes completely.
#
# THE SABOTAGE walks ONE step of the cycle instead of all of it. Under the
# cyclic-next representation (`src/core/fold_tables.inc`) that is not even the
# "add the partner" a naive implementer would write: from `k` it adds U+212A
# and LOSES `K`, because the cycle's next member from `k` is the Kelvin sign.
# Either failure is the row's claim -- the point is that one round of a
# relation whose classes are larger than two is not a closure.
SAB_ID="S-U2-fold-pairing-not-closure"
SAB_FILE="src/core/fold.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8"
SAB_DESC="ucd_partners adds one cycle step instead of closing the class, so a three-member fold class loses a member and (?i)k stops matching K"
SAB_DOC_FIGURE="MEASURED solo 2026-09-08 at the stage-4 landing: 211 passed / 26 FAILED over tests/utf8/fold.rxt + axis06_caseless_fold.rxt (237/0 clean); two-member classes untouched."
SAB_REACH='"$PCREC" -i -e utf8 -p rx -o - -- "k"'
SAB_REACH_EXPECT='Pattern:  */'
SAB_REACH_POP='tests/utf8/fold.rxt|^pattern|12'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        for (m = pcrec_ucd_fold_links[i].next;
             m != cp && guard < PCREC_FOLD_MAX_ORBIT;
             m = ucd_fold_next(m), guard++)
            pcrec_cpset_add(out, m, m);'
SAB_AFTER='        /* SABOTAGE S-U2: one round, not a closure */
        (void)guard;
        m = pcrec_ucd_fold_links[i].next;
        pcrec_cpset_add(out, m, m);'
