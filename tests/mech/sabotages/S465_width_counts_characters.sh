#!/usr/bin/env bash
# S465 ([K82] (B), lane k82hbuild) -- THE OFFSET COUNTS CHARACTERS, NOT BYTES.
#
# Detector: run_prechecks.sh §5.12a's HAND K pin table (its `.{3}cat` and
# `.{1,3}:` utf8 rows, K = 12, derived by hand, never by the walk; ci-strasse's
# pattern until 2026-11-13) and handoff.rxt's multibyte rows.
#
# RE-AIMED 2026-11-13 (lane s2tri, [RUN-POS-SET] flip 2 -> 128): with set
# positions up to 128 members the run of (?i)straße begins AT (?i)s's last
# byte, the set {S, s, 0xBF} (run [5373bf][5474]...@3, K 1, re-pinned in
# run_prechecks 3d70b9997), so the wide class is no longer wholly before the
# run and the plant's one-byte count gives the SAME K 1 there (measured on a
# planted build: run 545241@2/dfdfdf, REQ_HANDOFF "1"): straße no longer
# tells the plant apart. The witness is now §5.12a's `.{3}cat` -e utf8 row,
# where the wide class `.` sits wholly before the run and outside it: K 12 on
# the tip, 3 under the plant (planted build, 2026-11-13; `.{1,3}:` likewise
# 12 -> 3), so the detector table turns red. Probe and population follow it.
SAB_ID="S465-width-counts-characters"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/litscan/handoff.rxt"
SAB_DESC='the necessary-run walk counts a wide (code-point) class as ONE byte -- pcrec_cwmax'\''s character count, the mistake the design names H2 -- so .{3}cat under utf8 reads K = 3 where three characters of up to four bytes make it 12, and lo lands inside the match'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S465.'
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern '\''.{3}cat'\'' && grep -q '\''^#define RX_REQ_HANDOFF "12"'\'' "$REACH_TMP/o.c" && echo REACH-WIDE-DOT-K12'
SAB_REACH_EXPECT='REACH-WIDE-DOT-K12'
SAB_REACH_POP='tests/codegen/run_prechecks.sh|^[.][{]3[}]cat%-e utf8%12%12%|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        case A_CAP:
        case A_ATOMIC:
        /* [CLS-TREE] S3: TRANSPARENT to its byte child, which is exactly
         * what sat in this slot before the kind existed, so the walk
         * continues as it did then. */
        case A_WCLASS:
            /* Transparent:'
SAB_AFTER='        case A_WCLASS:
            acc->runs = rr_cat(w, rr_none(1), acc->runs);  /* SABOTAGE S465 */
            return;
        case A_CAP:
        case A_ATOMIC:
            /* Transparent:'
