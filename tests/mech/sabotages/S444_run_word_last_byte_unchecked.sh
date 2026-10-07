# S444 ([OPT-LITSCAN] S4 C1, lane s4build) -- THE LAST WORD STOPS ONE BYTE
# SHORT, SO THE RUN'S LAST BYTE IS NEVER COMPARED.
#
# The `overlap` row's two words must COVER the run: the first starts at 0 and
# the last ends at L. The plant moves the last word back one byte too far
# (offset L - W - 1), so the run's final byte is in no word and a subject
# that differs only there MATCHES -- a false match, the direction an answer
# check sees. Detectors: the harness, through the L-sweep's last-byte-flip
# cells (tests/litscan/litrun.rxt flips every position of every run once),
# and run_codegen_tests.sh's [OPT-LITSCAN S4] check that the last word sits
# at exactly L - W.
SAB_ID="S444-run-word-last-byte-unchecked"
# RE-AIMED 2026-10-07 ([MEMFN] M1b REPLACE, lane m1b): src/gen/runcmp.c moved into the kit (memfn/src/runcmp.c, transcribed); the words writer's anchor line is verbatim. Intent unchanged.
SAB_FILE="memfn/src/runcmp.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/litscan/litrun.rxt"
SAB_DESC="the run compare's last word sits at L - W - 1, so the run's last byte is compared by no word and a subject differing only there matches"
SAB_DOC_FIGURE="Read the current figure from a run (predicted: harness red on every L-sweep last-byte-flip n cell at an overlap length; codegen's last-word-offset check red)."
SAB_REACH='"$PCREC" --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "xyz(a|ab)c" && grep -qF "rx_w2(subject + scan_position + 1) == rx_w2(\"yz\")" "$REACH_TMP/o.c" && echo REACH-OVERLAP-ROW-EMITTED'
SAB_REACH_EXPECT="REACH-OVERLAP-ROW-EMITTED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        int at = o + w <= r->len ? o : r->len - w;   /* the last word ends at L */'
SAB_AFTER='        int at = o + w <= r->len ? o : r->len - w - 1;   /* SABOTAGE S444 */'
