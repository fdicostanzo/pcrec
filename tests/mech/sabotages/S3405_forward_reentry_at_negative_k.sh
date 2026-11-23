# S3405 (lane l3feat2, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3 and §5.7) --
# W-L17 (R-1): the forward scan's `handoff` re-entry is no longer declined at K < 0. At a restart in the
# DFA start state a match begun before the scan position can be in flight, its lookbehind run further
# back; the re-ask from the scan position misses it: `(?<=foobar)\d*x` on "foobar12x" answers NOMATCH
# (oracle (6,9)) and on "xfoobar9xfoobarx" (15,16) (oracle (7,9)).
# Detector: tests/litscan/spanarms.rxt (the L3 blocks, both routes).
# RE-AIMED 2026-11-20 (lane l3r65, review r65 A and C): under the pick rule no default-route compile states
# `(?<=foobar)\d*x`'s BACK run (its consumed extent is empty), and with the decline removed every forward
# scan that would re-enter at K < 0 reaches the loud internal error review r65 C put in its kept-hit init, so
# the compile is REFUSED: `(?<=xyz)a+xyz` (BACK `xyza` at -3 over an unbounded consumed `xyz`, the start-byte
# row by default) refuses, red in tests/codegen/run_prechecks.sh [5.12a] (its hand row refused). Measured on the planted tree (l3r65 report).
SAB_ID="S3405-forward-reentry-at-negative-k"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC='the forward scan re-enters the handoff at K < 0 (the decline removed), so a match begun before the scan position, in flight in the start state, is skipped; since review r65 C the compile refuses there (the K < 0 kept-hit init is an internal error)'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3feat_report.md), re-aimed by lane l3r65 (docs/dev/lanes/l3r65_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3405."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?<=xyz)a+xyz'\'' && grep -q '\''^#define RX_DFA_PREFILTER "memchr"$'\'' "$REACH_TMP/o.c" && grep -q '\''^#define RX_REQ_HANDOFF "-3"$'\'' "$REACH_TMP/o.c" && echo REACH-WL17'
SAB_REACH_EXPECT='REACH-WL17'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!req_k_reentry_sound(k)) return false;'
SAB_AFTER='    (void)req_k_reentry_sound;   /* SABOTAGE S3405: the K < 0 decline removed */'
