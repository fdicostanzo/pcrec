# S122 ([M6.6.2] wave B+C, design §9.3 S-LA1) — THE POSITIVE LOOKAHEAD CUTS.
#
# THE CLAIM. `(?=X)` is ATOMIC: it commits to the body's FIRST success and does
# not reconsider. That is not a property of "lookahead" in general — PCRE2 has
# a NON-atomic positive lookahead too, `(?*X)`, and the two differ in exactly
# the line this row deletes. Design §2.2 fixes the distinction with four
# measured cells on "abab":
#
#     (?=(a|ab))\1$        NOMATCH    keeps its first success ("a")
#     (?*(a|ab))\1$        (2,4)      retries, finds "ab"
#     (*napla:(a|ab))\1$   (2,4)      the verb spelling of (?*
#     (*pla:(a|ab))\1$     NOMATCH    the verb spelling of (?=
#
# WITHOUT THE CUT the atomic form answers the non-atomic one's (2,4).
#
# THE DETECTOR BODY IS CHOSEN, NOT CONVENIENT (R33 C2-13). `possessify.c` has
# three `A_ATOMIC` sites, and if it possessified the body's alternation the
# choice points the cut removes would never have existed and this row would go
# GREEN ON A BROKEN COMPILER. MEASURED against the LANDED possessify at this
# wave: `(?=(a|ab))\1$` stamps `RX_VM_STRATS 0x0u` — no possessification at
# all — and `pss_walk` does not enter a lookaround body in the first place.
# The cell needs `backrefs` as well as `lookaround`, and `lookahead.rxt` names
# both; under the default `std1` it would be refused and the row would go
# green by REFUSAL, which is S108's masking shape (R33 V-10).
SAB_ID="S122-look-positive-no-cut"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround/lookahead.rxt"
SAB_DESC="vm_look's positive arm stops cutting, so a positive lookahead keeps every choice point its body created and a later failure can re-enter it — turning the ATOMIC (?= into the NON-ATOMIC (?*"
SAB_DOC_FIGURE="PREDICTED: the atomicity discriminator goes red — (?=(a|ab))\\1\$ on \"abab\" answers (2,4) where libpcre2 says NOMATCH. The lookaround arm's §2 additionally reports the two spellings agreeing where they must disagree. Canonical figure owed from run_sabotage_matrix.sh S122."
SAB_COUNT=1
SAB_BEFORE='        if (atomic)
            vm_cut(v, mslot, "cut: the assertion is committed; every choice "
                             "point the body created is discarded, dead or not");'
SAB_AFTER='        /* SABOTAGE S122: the cut deleted — (?= behaves as (?* */
        (void)mslot;'
