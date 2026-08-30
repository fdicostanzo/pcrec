# S201 (S-C10) — [DD-13b.W1.1] `--list-source` reports every pattern row's
# `line` one LATER than it is.
#
# THIS IS THE SEAM'S ONE NUMBER. run.sh gains no head arms at all; for a
# head-bearing file it is TOLD where the body starts, by the `line` column
# of the first `pattern` row. Getting it wrong is the failure mode the
# whole seam design trades for having one head parser instead of two, so it
# gets its own row.
#
# THREE CASES, THREE DIFFERENT DETECTORS, and W1.1 is where the third stops
# being silent:
#   too EARLY                  -> the loop starts on a head line, no arm
#                                 matches, run.sh's catch-all hard-errors
#   too LATE, one block        -> the `pattern` line is skipped,
#                                 blocks_in_file stays 0, the P-C2 floor fires
#   too LATE, several blocks   -> the first block's cases push with
#                                 have_block=0 and the next `pattern` line's
#                                 reset discards them. BEFORE W1.1's guard
#                                 this was SILENT; it is now a hard error.
#
# AND THE WITNESS HAD TO BE BUILT. 0 of the corpus's 179 files are
# head-bearing, so all three detectors have an EMPTY population on the
# corpus and this row would have scored UNDETECTED while the code was
# perfectly broken. tests/rxtsource/fixtures/head_basic.rxtin is the
# witness; the check compares pcrec's reported line against an INDEPENDENT
# grep over the raw bytes, never against pcrec's own opinion.
SAB_ID="S201-rxt-body-line-late"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="rxtsource"
SAB_DESC="--list-source reports each pattern block one line later than it is, so run.sh starts its body loop past the first pattern line of a head-bearing file"
SAB_REACH_POP="tests/rxtsource/fixtures/head_basic.rxtin|^pattern |2"
SAB_COUNT=1
SAB_BEFORE='            block = row_push(&p, src, RXT_DECL_PATTERN, line);'
SAB_AFTER='            block = row_push(&p, src, RXT_DECL_PATTERN, line + 1);   /* SABOTAGE S201 */'
