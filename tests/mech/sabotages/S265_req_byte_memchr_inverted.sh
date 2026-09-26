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
# [OPT-PRECHECK-ADMIT] RE-POINTED THE WITNESS (lane s265reach, 2026-09-26):
# `a=b` no longer reaches this text. Its whole necessary run ("a=b") now
# gets a `run-pinned` DFA candidate scan that VERIFIES the run
# (`ofs_test_verifies_run`), so G1's dominance rule (`req_byte_dominated_by`,
# src/gen/emit_dfa.c) takes the run-pinned identity branch and `a=b` stamps
# `RX_REQ_WHY "dominated"` instead of `"emitted"` -- `pcrec_emit_req_byte_check`
# returns before printing anything (`req_admit(cx) != REQ_ADMIT_EMITTED`).
# [OPT-FREQPICK]/[OPT-LITSCAN] S1 landed the run-pinned form and the
# dominance rule after this row was authored; the mechanism this row
# sabotages did not move, only the population of witnesses that still
# reach it (the [MECH-REACH] shape this file's own header names).
#
# THE REACH WITNESS IS NOW `a.?b`, chosen for what it is NOT rather than for
# a stamp alone: `a` and `b` are both in the pattern's necessary-byte SET, the
# picked byte is `b` (98, argmin of the byte-frequency prior over {97,98}),
# and there is NO required RUN (`.?` is optional, so nothing is contiguous) --
# `RX_REQ_RUN "none"`. `pcrec_emit_req_byte_check` therefore takes the
# ONE-BYTE branch (its `req_run.len >= 2` early return does not fire), and G1
# does not dominate it: the artifact's own DFA candidate scan is a plain
# `memchr` on byte 97 ('a', NOT `b`, so the identity conjunct fails), and
# under `-e byte` `pcrec_byte_freq_ppm(97) > pcrec_byte_freq_ppm(98)` (a common
# letter must be STRICTLY rarer than the required byte to dominate it, and 'a'
# is not rarer than 'b') -- so `req_byte_dominated_by` returns false and
# `req_admit` answers EMITTED. The probe asserts `RX_REQ_WHY "emitted"` AND
# the emitted `!memchr` line together, so a later change that keeps the stamp
# and moves the emission -- or that makes THIS witness dominated too -- is
# caught as UNREACHED rather than read as a clean row.
#
# WHAT IT ALSO CERTIFIES, and the reason the plant is a one-character edit
# rather than a deletion: the `subject_length <= search_from` arm above the
# `memchr` is LEFT INTACT. A plant that removed the whole pre-check would be
# invisible (the sound direction), and a plant that removed only the empty
# window arm would be a NULL-dereference rather than a wrong answer. This one
# isolates the SENSE, which is the half tests/codegen/run_prechecks.sh §3.1c
# asserts separately from the byte's own value (on ITS OWN still-live
# witnesses `\w+@\w+`, `a{2,4}b`, `(a)\1?b` -- three of the eight §3.1 rows
# whose `wantrun` is `none`; the other five -- `<[a-z]+>`, `(ab|cd)e`,
# `[^x]c`, `(?:ab)*c`, `q` -- now read `dominated` under [OPT-PRECHECK-ADMIT]
# and so no longer reach §3.1c, though §3.1/§3.1b/§3.1w still pass on them).
SAB_ID="S265-req-byte-memchr-inverted"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness prechecks"
SAB_DESC="the required-byte whole-window pre-check emits 'memchr(...)' where it should emit '!memchr(...)', so both engines' search entries answer NOMATCH exactly when the byte every match must contain IS present and fall through to the attempt loop when it is absent — an inversion that turns every matching subject of every required-byte pattern into a no-match, unlike its two batch siblings whose sound-direction plants have no answer-level detector at all"
SAB_DOC_FIGURE="tests/harness/run.sh over the full .rxt corpus is the primary detector: every 'm' case of every pattern carrying a required byte reports nomatch, so 'cases failed' moves from 0 to a large count. tests/codegen/run_prechecks.sh §3.1c is the structural detector and names the sense directly ('the pre-check's sense is not !memchr(...) — it may be inverted') on the §3.1 witnesses that still read RX_REQ_WHY 'emitted' with no run (three of eight after [OPT-PRECHECK-ADMIT] narrowed the population — see the header above). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S265. RE-POINTED 2026-09-26 (lane s265reach): SAB_REACH's witness moved from 'a=b' (reads RX_REQ_WHY 'dominated' on main as of 5803051b, so the row scored UNREACHED) to 'a.?b' (reads 'emitted'); solo run owed to the manager."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree
# `a.?b` stamps RX_REQ_WHY "emitted" (not "dominated" -- see the header
# above) and emits the negated memchr this row inverts, on byte 98 ('b').
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "a.?b" && grep -q "^#define RX_REQ_WHY \"emitted\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_BYTE \"98\"" "$REACH_TMP/o.c" && grep -q "!memchr(subject + search_from, 98, subject_length - search_from)" "$REACH_TMP/o.c" && echo REACH-REQ-BYTE-PRECHECK-EMITTED'
SAB_REACH_EXPECT="REACH-REQ-BYTE-PRECHECK-EMITTED"
SAB_COUNT=1
SAB_BEFORE='        "%sif (%s <= %s ||\n"
        "%s    !memchr(%s + %s, %d, %s - %s))\n"'
SAB_AFTER='        "%sif (%s <= %s ||\n"
        "%s    memchr(%s + %s, %d, %s - %s))\n"   /* SABOTAGE S265: the sense inverted */'
