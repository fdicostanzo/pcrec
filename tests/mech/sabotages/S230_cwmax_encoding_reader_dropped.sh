# S230 ([ENCCHK-DD12A] admin row) — tests/mrl/cwmax_check.c's ENCODING
# DIRECTIVE READER stops applying the resolved encoding, so every block is
# swept as if it were `byte` however its `.rxt` file spells `encoding utf8`.
#
# WHY THIS IS THE EDIT WORTH PLANTING. `do_file`'s directive reader already
# resolves an `encoding` line through the seam's own registry
# (`pcrec_enc_by_name`) and reports an unknown name loudly — the realistic
# slip is not "the resolver breaks", it is "the resolved value never reaches
# `Block.encoding`", exactly the shape a refactor of that if/else produces
# when someone hoists the lookup and forgets the assignment.
#
# THE CHECK THIS DEFEATS IS THE ONE K49FIX ADDED, NOT THE ORIGINAL PAIR.
# tests/mrl/CLAUDE.md's own account of the 2026-09-05 repair (K49-adjacent
# unit-mismatch fix) names TWO FLOORS the encoding-aware half needs to avoid
# being dead code that passes silently: (i) the utf8 block population is
# nonzero, (ii) at least one compared span's byte width exceeds its
# character width. This row is floor (i)'s planted failing direction,
# validated by hand at the repair and NEVER BEFORE encoded as a permanent
# mech row -- which is exactly [ENCCHK-DD12A]'s charter (docs/dev/known_issues.md
# K52's sibling admin obligation): the cwmax floors get sabotage-scored
# rather than resting on a one-time manual demonstration in a CLAUDE.md
# paragraph.
#
# WHAT ACTUALLY HAPPENS, MEASURED (scratch build, same tree, whole corpus):
# every block parses under `byte` regardless of its own `encoding` line, so
# a multi-byte literal in the pattern becomes a CLASS OF BYTES rather than
# one character class and `pcrec_cwmax` is computed on the wrong language
# entirely. `n_utf8_blocks` and `n_utf8_spans` both read 0 (floor (i) fires
# by name), floor (ii) fires too (0 multibyte spans -- there is no utf8 span
# population left to have one), and CHECK 2 itself goes on to report 40 REAL
# violations of its own (byte-parsed cwmax vs. character-tier oracle spans on
# the very shapes axis01_encoded_length.rxt was built to carry, e.g.
# `[^₠-€]` and `[€]{1,2}`) -- three independent symptoms of one dropped
# assignment.
#
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS: the reach probe
# below builds and runs the SAME checker binary the `mrl` arm's §8 runs, on
# the CLEAN tree, and reads its own printed counters -- not a re-derivation
# of what "utf8 blocks" ought to mean.
SAB_ID="S230-cwmax-encoding-reader-dropped"
SAB_FILE="tests/mrl/cwmax_check.c"
SAB_SUITES="mrl"
SAB_DESC="cwmax_check.c's encoding directive reader resolves the name but never assigns it to the block, so every .rxt block is swept as byte regardless of its own directive -- the utf8-aware half of run_mrl_tests.sh section 8 goes dead silently unless its own population floors catch it"
SAB_DOC_FIGURE="tests/mrl/CLAUDE.md's 2026-09-05 repair account: 'validated in the failing direction -- disabling the encoding reader trips the first [floor]'. MEASURED here for the first time as a permanent row (whole corpus, this tree): utf8 blocks/spans 0/0 (floor (i) fires), multibyte spans 0 (floor (ii) fires too, vacuously), CHECK 2 violations 0 -> 40 (a real regression, not only a dead floor)."
SAB_REACH='"$CC" -O1 -w -I "$TREE/lib" -I "$TREE/src" -o "$REACH_TMP/cwmax_check" "$TREE/tests/mrl/cwmax_check.c" "$TREE/build/libpcrec.a" && "$REACH_TMP/cwmax_check" "$TREE/tests/utf8/axis01_encoded_length.rxt"'
SAB_REACH_EXPECT='utf8 blocks / spans      : 64 / 88'
SAB_REACH_POP='tests/utf8/axis01_encoded_length.rxt|^encoding utf8|50'
SAB_COUNT=1
SAB_BEFORE='                b.encoding = e->id;'
SAB_AFTER='                /* SABOTAGE S230: resolved but never applied */
                (void)e;'
