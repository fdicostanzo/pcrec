# S187 (S-OPTK3) — [OPT-K] THE SELECTION NEVER FIRES, AND EVERY ANSWER IN THE
# TREE STAYS RIGHT.
#
# This is the row for the failure mode the whole [OPT-K] check apparatus
# exists for, and it is the one no answer comparison anywhere can reach. The
# offset-k skip is ANSWER-IDENTITY-PRESERVING BY CONSTRUCTION — every test it
# adds is a NECESSARY condition of a match beginning at that position — so a
# compiler that simply stopped selecting it answers every subject in this
# repository correctly, passes both oracles, passes `make test-axes` (whose
# whole claim is that the denied build and the default one agree), and loses
# the row's MEASURED 4.5x-17.1x without a single red cell.
#
# `tests/codegen/run_offset_skip.sh` §2 is the detector: it names four
# patterns and requires the form on each. §4 fires too, and for a reason worth
# stating — with the selection gone, the `-fno-offset-skip` build and the
# default build become indistinguishable, so the axis's own control is
# comparing a build against itself, which is this project's most-recorded
# check-design failure arriving through the check that was built to prevent
# it.
#
# `tests/offsetskip/offset_skip.rxt` stays 75/75 GREEN under this plant, and
# that is not a gap in it — the file's own header says so. It checks the
# emitted skip's ARITHMETIC, and there is no arithmetic to check when there is
# no skip.
SAB_ID="S187-ofsk-selection-never-fires"
SAB_FILE="src/opt/prefix_k.c"
SAB_SUITES="harness offsetskip"
SAB_HARNESS_TARGET="tests/offsetskip/offset_skip.rxt"
SAB_DESC="pcrec_prefix_ksets never publishes a selection, so no artifact takes the offset-k form. Every answer in the tree stays correct and the row's measured 4.5x-17.1x is gone — detectable ONLY by a check that counts the population"
SAB_DOC_FIGURE="PRE-VALIDATED (2026-08-28, lane optk): DETECTED against a clean 19pass/0fail + 80pass/0fail baseline -- offsetskip:5fail/14pass, corpus:0fail/80pass. THE GREEN CORPUS ARM IS THE POINT OF THE ROW, not a half-detection: every answer in the tree stays right and make test-axes stays green, because with the selection gone the denied build and the default build are the same build."
SAB_COUNT=1
SAB_BEFORE='    if (best_scan < 0) return;'
SAB_AFTER='    if (1 || best_scan < 0) return;   /* SABOTAGE S187 */'
