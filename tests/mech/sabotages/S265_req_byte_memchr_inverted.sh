# S265 — [OPT-REQBYTE] THE REQUIRED-BYTE PRE-CHECK'S MEMCHR SENSE IS INVERTED
# (src/gen/emit_dfa.c, `pcrec_emit_req_byte_check`): the emitted test reads
# `memchr(...)` where it should read `!memchr(...)`, so a search returns
# NOMATCH exactly when the necessary byte IS PRESENT and runs the attempt
# loop exactly when it is not.
#
# THIS IS THE ONE OF THE THREE BATCH-1 MECHANISMS WHOSE NATURAL CORRUPTION IS
# NOT IN THE SOUND DIRECTION, which is why it is the only one of the three
# with an ordinary answer-level detector on the CORPUS arm. [OPT-ANCHOR-VM]
# (S263) and the sound-direction half of this mechanism remove only work that
# would have failed; a flipped sense removes work that would have SUCCEEDED,
# so every corpus pattern carrying a required byte stops matching every
# subject that contains one.
#
# THE REACH WITNESS IS THE STAMP, not a hand-picked pattern shape: any
# artifact whose `<PREFIX>_REQ_BYTE` is not `"none"` emits this text, and the
# probe below asserts the stamp AND the emitted `!memchr` line together so a
# later change that keeps the stamp and moves the emission is caught as
# UNREACHED rather than read as a clean row.
#
# WHAT IT ALSO CERTIFIES, and the reason the plant is a one-character edit
# rather than a deletion: the `subject_length <= search_from` arm above the
# `memchr` is LEFT INTACT. A plant that removed the whole pre-check would be
# invisible (the sound direction), and a plant that removed only the empty
# window arm would be a NULL-dereference rather than a wrong answer. This one
# isolates the SENSE, which is the half tests/codegen/run_prechecks.sh §3.1c
# asserts separately from the byte's own value.
SAB_ID="S265-req-byte-memchr-inverted"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness prechecks"
SAB_DESC="the required-byte whole-window pre-check emits 'memchr(...)' where it should emit '!memchr(...)', so both engines' search entries answer NOMATCH exactly when the byte every match must contain IS present and fall through to the attempt loop when it is absent — an inversion that turns every matching subject of every required-byte pattern into a no-match, unlike its two batch siblings whose sound-direction plants have no answer-level detector at all"
SAB_DOC_FIGURE="tests/harness/run.sh over the full .rxt corpus is the primary detector: every 'm' case of every pattern carrying a required byte reports nomatch, so 'cases failed' moves from 0 to a large count. tests/codegen/run_prechecks.sh §3.1c is the structural detector and names the sense directly ('the pre-check's sense is not !memchr(...) — it may be inverted') on each of the twelve §3.1 witnesses that carry a byte. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S265."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree `a=b`
# stamps the byte 98 and emits the negated memchr this row inverts.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "a=b" && grep -q "^#define RX_REQ_BYTE \"98\"" "$REACH_TMP/o.c" && grep -q "!memchr(subject + search_from, 98, subject_length - search_from)" "$REACH_TMP/o.c" && echo REACH-REQ-BYTE-PRECHECK-EMITTED'
SAB_REACH_EXPECT="REACH-REQ-BYTE-PRECHECK-EMITTED"
SAB_COUNT=1
SAB_BEFORE='        "%sif (%s <= %s ||\n"
        "%s    !memchr(%s + %s, %d, %s - %s))\n"'
SAB_AFTER='        "%sif (%s <= %s ||\n"
        "%s    memchr(%s + %s, %d, %s - %s))\n"   /* SABOTAGE S265: the sense inverted */'
