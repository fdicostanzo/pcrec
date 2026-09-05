# S-U9 ([M5.0] stage 2; utf8_design.md §8.2, §5.2.1 / r54 E4) -- THE
# BACK-STEP'S DECLARED-LENGTH TEST IS DELETED.
#
# THE CLAIM: `$_back_step` validates that every character run it steps over
# is DECLARED by its lead byte (§5.2.1's repair — "the line the first design
# draft did not have"). Without it the walk and the forward parse can
# disagree about where a character starts, and the lookbehind end-check —
# whose redundancy proof assumes they agree — FIRES.
#
# INVISIBLE ON EVERY WELL-FORMED SUBJECT, AND THE FAILURE IS AN ABORT, NOT A
# WRONG ANSWER: on `C2 80 80` (one continuation byte too many), the clean
# artifact's `(?<!.)x` back-step answers NONE at the ill-formed run, the
# assertion holds, and the match is found; the sabotaged one back-steps to 0,
# the body consumes the well-formed `C2 80` prefix, ends one byte short of
# the entry, and the NEGATIVE arm's end-check returns RX_R_INTERNAL — below
# PCREC_ERR_FLOOR, a composed site's __builtin_trap(). Reachable on a
# WELL-FORMED subject too through a mid-character startpos (§2.6.1.1), which
# is why P-9's instrument sweeps both.
SAB_ID="S-U9-back-step-length-test-deleted"
SAB_FILE="src/gen/enc/enc_utf8.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8"
SAB_DESC="the utf8 back_step's want != end - pos declared-length test is deleted; on an ill-formed continuation run (or a mid-character startpos) the walk and the forward parse disagree, the negative lookbehind's end-check fires RX_R_INTERNAL, and a composed call site traps on a subject the ruling promises will merely not match"
SAB_DOC_FIGURE="PREDICTED (§8.2): tests/utf8/invalid.rxt's (?<! cells over C2 80 80-shaped subjects red as ERROR returns rather than spans. DEMONSTRATED at stage 2 pre-corpus: (?<!.)x on C2 80 80 78 answers match(3,4) clean; sabotaged, rx_search returns the internal-error code."
SAB_REACH='"$PCREC" --features lookaround -e utf8 -p rx -o - -- "(?<!.)x"'
SAB_REACH_EXPECT='Pattern: (?<!.)x'
SAB_REACH_POP='tests/utf8/invalid.rxt|^pattern .*\(\?<!|6'
SAB_COUNT=1
SAB_BEFORE='"        if (want != end - pos) return $_BACK_STEP_NONE;\n"'
SAB_AFTER='"        (void)want; (void)end;  /* SABOTAGE S-U9: length test deleted */\n"'
