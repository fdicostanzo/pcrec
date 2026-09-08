# S-U1 ([M5.0] stage 4; utf8_design.md §4.3, §8.2) -- FOLD BEFORE NEGATE.
#
# THE CLAIM: the caseless fold is applied to the POSITIVE set, before the
# negation, so `[^k]` under `-i` excludes every member of k's fold class.
# D23/OS-1 made that rule for the ASCII fold and §4.3 MEASURED it holds under
# UTF including across blocks: `[^k]` caseless rejects U+212A.
#
# WHY ONLY BEHAVIOUR SEES IT, which is why this row exists at all: BOTH orders
# produce a set that is CLOSED UNDER CASE SWAPPING. Folding the complement
# instead of the set yields `{all but k} | swapcase{all but k}`, which under
# a Unicode fold is every code point -- a perfectly well-formed class that no
# invariant, no structural check and no interval-algebra assertion can tell
# from the right one. Only a cell over a fold PARTNER can.
#
# THE SABOTAGE swaps the two adjacent lines in `p_class`, the ONE constructor
# where the order lives. Stage 4 did not move them; it inserted the produced
# sets' union between the fold and the negation, so the pair being swapped is
# the same pair S08 has always aimed at, one encoding wider.
SAB_ID="S-U1-fold-after-negate"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8"
SAB_DESC="p_class negates before folding, so a negated caseless class is closed under case swapping in the wrong direction and [^k] under -i matches K and U+212A"
SAB_DOC_FIGURE="PREDICTED (§8.2): the negated caseless blocks of tests/utf8/fold.rxt and axis06_caseless_fold.rxt go red. The design's own discriminating cell is [^k] on U+212A."
SAB_REACH='"$PCREC" -i -e utf8 -p rx -o - -- "[^k]"'
SAB_REACH_EXPECT='Pattern:  */'
SAB_REACH_POP='tests/utf8/fold.rxt|^pattern \[\^|3'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (cx->mods->caseless) cls_casefold(cx, &set, cls_enc(cx)->fold);
    pcrec_cpset_add_set(&set, prod.iv, prod.n);
    if (neg) pcrec_cpset_complement(&set, cls_universe(cx));'
SAB_AFTER='    /* SABOTAGE S-U1: negate first, then fold */
    pcrec_cpset_add_set(&set, prod.iv, prod.n);
    if (neg) pcrec_cpset_complement(&set, cls_universe(cx));
    if (cx->mods->caseless) cls_casefold(cx, &set, cls_enc(cx)->fold);'
