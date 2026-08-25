# S180 (S-FB2) — [DD-14.FB] THE TWO CAPACITIES ARE BOUND TO EACH OTHER'"'"'S ARRAY.
#
# `<prefix>_run_state_bind` takes four arguments in two pairs and the pairs have
# the same shape, so transposing the two counts is a one-character-class typo
# that compiles, runs, and is right whenever the two numbers happen to be equal.
#
# THIS IS WHY `tests/recursion/framebuffer.rxt`'"'"'S CAPACITIES ARE ASYMMETRIC.
# The obvious cell to write is `frames-buffer=8192` — one number, both arrays —
# and it CANNOT SEE THIS ROW, ever, because under it the sabotage is a no-op.
# The block instead hands over 1024 frames and 8192 trail entries for a subject
# that needs 686 and 3,081: sufficient as written, insufficient transposed (1,024
# trail entries against 3,081 needed). Design §4'"'"'s measured 4.49 trail entries
# per frame is what makes an asymmetric pair the natural one to write, and this
# row is what makes writing it obligatory.
#
# The three `_in` entries share the wording, so all three are sabotaged: an
# artifact where only `<prefix>_search_in` transposed would be a stranger bug
# and a weaker row.
SAB_ID="S180-buffers-capacities-swapped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness framebuffer"
SAB_HARNESS_TARGET="tests/recursion/framebuffer.rxt"
SAB_DESC="all three emitted <prefix>_*_in entries pass buffers->ntrail as the RESUME capacity and buffers->nframes as the TRAIL capacity. A no-op whenever a caller supplies equal capacities, which is why the corpus cell that detects it uses deliberately unequal ones"
SAB_DOC_FIGURE="PREDICTED: framebuffer.rxt RED on the 1024,8192 cell (the trail capacity becomes 1024 against 3,081 needed, so a match becomes a give-up); the equal-capacity and NULL cells GREEN. Canonical figure owed from run_sabotage_matrix.sh S180."
SAB_COUNT=3
SAB_BEFORE='        "    %s_run_state_bind(&run, buffers->frames, buffers->nframes,\n"
        "                            buffers->trail,  buffers->ntrail);\n"'
SAB_AFTER='        "    %s_run_state_bind(&run, buffers->frames, buffers->ntrail,\n"
        "                            buffers->trail,  buffers->nframes);   /* SABOTAGE S180 */\n"'
