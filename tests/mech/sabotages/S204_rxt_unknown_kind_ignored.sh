# S204 (S-C2's family, and the row the four-kinds gap earns) —
# [DD-13b.W1.1] the python oracle treats a line kind it does not know as
# a COMMENT instead of refusing it, so a whole class of expectation
# silently stops being verified.
#
# THIS IS THE FAILURE THE STEP ACTUALLY HIT, planted. `parse_rxt` knew 10
# of the corpus's 14 line kinds; `gu` (23 lines), `frames-buffer=` (9),
# `engine` (5) and `budget` (3) each raised "unrecognized line". That was
# LOUD, and being loud is why W1.1 found it the moment the oracle was
# pointed at the corpus rather than at tests/base. The dangerous version
# is the quiet one: an unknown kind swallowed as a comment verifies
# nothing, reports nothing, and subtracts from a total nobody compares.
#
# CAUGHT TWICE, and the two detectors fail differently:
#   `rxtsource` C1 leg B == leg C — run.sh's parser still reads the line
#       and emits a case row for it; this one no longer does, so the two
#       dumps differ by exactly the swallowed kinds. This is the detector
#       that names WHICH kind went missing.
#   `rxtsource` C3's pinned totals — the `giveup` skip count drops from
#       23 to 0 and the verified count moves. This is the detector that
#       works even if both dumps were changed together.
#
# A row for the SHAPE, not for one kind: the plant is in the parser's
# fallthrough, so it covers every kind the grammar may gain later, which
# is the direction this file will actually be edited in.
#
# AND IT NEEDED A WITNESS, for a reason with a sting in it: once W1.1
# taught this parser the four kinds it was missing, NO corpus line
# reaches the unknown-kind branch any more. FIXING THE GAP IS WHAT
# EMPTIED THE POPULATION OF THE ROW THAT GUARDS IT, and the row duly
# scored UNDETECTED on its first run.
# tests/rxtsource/fixtures/unknown_kind.rxtin is the witness: `tag` is a
# real keyword of a later wave, which all three parsers must REFUSE
# rather than swallow.
SAB_ID="S204-rxt-unknown-kind-ignored"
SAB_FILE="tests/harness/verify_rxt.py"
SAB_SUITES="rxtsource"
SAB_DESC="verify_rxt.py's parser swallows an unrecognised .rxt line kind as a comment instead of refusing it, so every expectation of that kind is silently unverified and uncounted"
SAB_REACH_POP="tests/rxtsource/fixtures/unknown_kind.rxtin|^tag |1"
SAB_COUNT=1
SAB_BEFORE='        else:
            raise ValueError(f"{path}:{lineno}: unrecognized line: {line!r}")'
SAB_AFTER='        else:
            continue   # SABOTAGE S204: unknown kind swallowed as a comment'
