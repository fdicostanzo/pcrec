# S293 — [OPT-LITSCAN] S1 step 6 THE RUN PRE-CHECK'S SCAN OFFSET DROPPED
# (src/gen/emit_dfa.c, `ofs_test_run`): the pre-check's candidate test keeps
# scanning for the run's member `run[i]` but records its offset as 0, so the
# `rx_reqrun` block takes each hit of `run[i]` as the run's START instead of
# `hit - i` and compares the run there. On every run whose scanned member is
# not its first byte the compare never lines up, the block returns `n`, and
# the search entry answers NOMATCH on a subject that contains the run.
#
# THE STEP-6-SPECIFIC ARITHMETIC. Before the conversion the loop spelled the
# member's offset as `rp_c - i` at its compare; after it the offset is ONE
# field of the one derivation, `OfsTest.scan_k`, read by the block's scan
# start AND by the candidate it implies (`cand = hit - scan_k`). This plant
# zeroes that field and nothing else — the scanned byte, the run, the guards
# and the call are all intact — so it isolates exactly the offset the
# conversion moved from a compare into the candidate test.
#
# ANSWER-DETECTABLE: a lost run is a false NOMATCH on every `m` cell of a
# pattern whose run pre-check is emitted and whose scan member sits past the
# run's first byte. tests/base/k66_precheck_whole_run.rxt is the named
# harness target: under `-e byte` its whole run `eeeeeeee~#~#~#~#` is
# scanned on `~` at offset 8 (the window's), so the byte block's `m` cell
# loses its match; under utf8 the window is the run's first 8 bytes, every
# scan offset is 0, and that block is the in-file control the plant leaves
# alone. tests/codegen/run_prechecks.sh §4.1c
# (the scan offset asserted per witness) and §4.3 are the structural
# detectors.
SAB_ID="S293-reqrun-scan-offset-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks harness"
SAB_HARNESS_TARGET="tests/base/k66_precheck_whole_run.rxt"
SAB_DESC="the run pre-check's candidate test records its scan member's offset as 0, so each rx_reqrun block takes a hit of run[i] as the run's start rather than hit - i and never finds a run whose scan member is not its first byte: a false NOMATCH on every matching subject of such a pattern"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S293."
# [MECH-REACH] the probe: `a=b` (scan member `=` at 1) under
# -fno-offset-skip emits its rx_reqrun block scanning at offset 1.
SAB_REACH='"$PCREC" --features all -p rx -fno-offset-skip -o "$REACH_TMP/o.c" --pattern "a=b" && grep -qF "memchr(subject + pos + 1, 61, n - pos - 1);" "$REACH_TMP/o.c" && grep -qF "rx_reqrun(subject, subject_length, search_from)" "$REACH_TMP/o.c" && echo REACH-REQRUN-SCAN-OFFSET-EMITTED'
SAB_REACH_EXPECT="REACH-REQRUN-SCAN-OFFSET-EMITTED"
SAB_COUNT=1
SAB_BEFORE='    t->scan_k    = i;
    t->scan_byte = run[i];'
SAB_AFTER='    t->scan_k    = 0;   /* SABOTAGE S293: the scan member offset dropped */
    t->scan_byte = run[i];'
