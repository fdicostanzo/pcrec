# S441 ([OPT-LITSCAN] S4 C1, lane s4build) -- THE LAST WORD OVER-READS.
#
# The run compare's `overlap` row loads natural-width words and moves the
# last one back so it ends exactly at L (offset L - W): every word lies
# inside the run, which is what lets the caller's `pos + L <= n` guard bound
# the read. The plant puts the last word at L - W + 1, one byte past the run
# -- an over-read of the subject on a match ending at the subject's end, and
# a constant that reads one byte past the run's own bytes. The cheap detector
# is run_codegen_tests.sh's [OPT-LITSCAN S4] word-offset check (every word
# o + W <= L, the last at exactly L - W); the harness sees it too, through the
# L-sweep cells (tests/litscan/litrun.rxt) whose expected answers the shifted
# constant no longer gives. (litscan_s4.md §5.5's S442: there the plant is
# answer-preserving behind a 0x00 mask byte; the masked rows are C3's, so on
# an exact run the plant moves answers as well.)
SAB_ID="S441-run-word-overreads"
SAB_FILE="src/gen/runcmp.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/litscan/litrun.rxt"
SAB_DESC="the run compare's last word sits at L - W + 1, one byte past the run, so it reads past the bounds the caller's guard covers and compares a constant that reaches past the run's bytes"
SAB_DOC_FIGURE="Read the current figure from a run (predicted: codegen's [OPT-LITSCAN S4] word-offset check red on every overlap witness; harness red on the L-sweep m cells)."
SAB_REACH='"$PCREC" --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "xyz(a|ab)c" && grep -qF "rx_w2(subject + scan_position + 1) == rx_w2(\"yz\")" "$REACH_TMP/o.c" && echo REACH-OVERLAP-ROW-EMITTED'
SAB_REACH_EXPECT="REACH-OVERLAP-ROW-EMITTED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        int at = o + w <= r->len ? o : r->len - w;   /* the last word ends at L */'
SAB_AFTER='        int at = o + w <= r->len ? o : r->len - w + 1;   /* SABOTAGE S441 */'
