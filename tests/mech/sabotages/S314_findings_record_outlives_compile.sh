# S314 — [FINDINGS] B2 F-9: THE CONSUMPTION RECORD OUTLIVES ITS COMPILE
# (src/core/findings.c, `pcrec_find_stamp`): whether a query was ASKED is
# remembered past the compile (and past the ATTEMPT) that asked it, so a
# later compile — a second target in the same invocation, or a retry
# attempt — stamps a query it never asked (design §6.4: the record belongs to
# the FINAL attempt, reset per attempt like every `Job` field).
#
# WHY THE DETECTOR IS A SECOND TARGET AND NOT A RETRY. The design names a
# `[SEL-1]` fixture; its population is EMPTY today, and structurally so:
# a carried record is visible only when an EARLIER attempt asked and the
# FINAL did not. MEASURED (lane findb2, instrumented build, 2026-09-27): the
# [SEL-1] rung's first attempt overflows in the DFA BUILD, before any reader
# asks (`[ab]*a[ab]{20}c`, `x[ab]*a[ab]{18}` under -fno-req-byte
# -fno-prefilter ask in neither attempt); the size rungs keep a DFA scan
# ([K53]/[K59] keep the DFA engine, and [OPT-4]'s collapse preserves
# nullability, so it never drops a prefilter attempt 1 had), and the final
# attempt re-asks. So the per-ATTEMPT half has no witness, and this row's
# plant is the general defect (the record is process state, not attempt
# state), whose per-COMPILE half does: run_findings_tests.sh §6 #22 compiles
# two targets in one invocation, the second asking nothing, and requires "".
#
# RE-AIMED 2026-10-17 (lane rpunion, [WINDOW-E1] D167 addendum 3, abi 79):
# the stamp is now the UNION over the compile's attempts (and a compound's
# parts), so carrying an ask from a discarded attempt to the shipped one is
# the RULE, not this defect, and the per-attempt half above is retired (F-5
# found its witness, and the fix made it correct). The defect left is the
# per-COMPILE half: the union outlives its compile. `pcrec_find_stamp` now
# takes the consulted set; the plant keeps it in a static, so the second
# target inherits the first's ask. Same detector, same arm.
SAB_ID="S314-findings-record-outlives-compile"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC="whether byte-rate was asked is remembered past the compile that asked it, so a later compile in the same process (a second target) stamps a query none of its attempts asked — the consulted set is no longer the compile's own (design §6.4, D167 add. 3)"
SAB_DOC_FIGURE="findings red on §6 [#22] (t_quiet stamps byte-rate=none where \"\" is expected). The per-attempt half is retired by the union-over-attempts rule (see this row's header). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S314."
SAB_REACH='python3 "$TREE/tests/findings/res_fixtures.py" "$REACH_TMP/r" && mkdir -p "$REACH_TMP/o" && "$PCREC" -o "$REACH_TMP/o" "$REACH_TMP/r/multi.rxt" && grep -q "_FINDINGS \"byte-rate=default:" "$REACH_TMP/o/t_asks.c" && grep -q "_FINDINGS \"\"" "$REACH_TMP/o/t_quiet.c" && echo REACH-FINDINGS-RECORD-PER-COMPILE'
SAB_REACH_EXPECT="REACH-FINDINGS-RECORD-PER-COMPILE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!(consulted & PCREC_FQ_BIT(PCREC_FQ_BYTE_RATE))) return "";'
SAB_AFTER='    static unsigned leaked;   /* SABOTAGE S314: the consulted set outlives its compile */
    consulted |= leaked;
    leaked = consulted;
    if (!(consulted & PCREC_FQ_BIT(PCREC_FQ_BYTE_RATE))) return "";'
