# S-U5 ([M5.0] stage 2; utf8_design.md §8.2) -- THE UTF8 BACK-STEP IS BYTE
# ARITHMETIC.
#
# THE CLAIM: the utf8 backend's `$_back_step` walks CHARACTERS (§5.2), so a
# lookbehind under `--encoding=utf8` steps over whole characters. The
# sabotage replaces its body with the BYTE backend's `pos - k` -- the exact
# residual the seam exists to keep out of shared code, arriving through the
# one door it is allowed to live behind.
#
# WHAT GOES WRONG: `(?<=α)x` on `CE B1 78` back-steps from 2 to 1 --
# MID-CHARACTER -- and the body's forward run from 1 reads `B1`, which is not
# a character start, so the automaton has no path and the assertion FAILS: a
# LOST MATCH. Identical under `byte` (there `pos - k` IS the walk), which is
# why no byte-axis instrument can see this row and the utf8 corpus owns it.
SAB_ID="S-U5-back-step-byte-arithmetic"
SAB_FILE="src/gen/enc/enc_utf8.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8"
SAB_DESC="the utf8 backend's back_step body becomes the byte backend's pos - k, so a lookbehind under --encoding=utf8 lands mid-character and loses every match behind a multi-byte character"
SAB_DOC_FIGURE="PREDICTED (§8.2): every tests/utf8 lookbehind cell behind a multi-byte character goes red (lost match); ASCII-only lookbehind cells are unmoved. DEMONSTRATED at stage 2 pre-corpus: (?<=\x{3b1})x on CE B1 78 answers match(2,3) clean and nomatch sabotaged."
SAB_REACH='"$PCREC" --features lookaround -e utf8 -p rx -o - -- "(?<=\x{3b1})x"'
SAB_REACH_EXPECT='Pattern: (?<=\x{3b1})x'
# RE-POINTED 2026-09-05: the stage-2 lane wrote this population against a
# GUESSED corpus filename; the promoted D27 corpus (merge 698eea61) landed
# with the axis naming, so the pop line named a file that does not exist and
# the first full mech run read the row UNREACHED-UNEXPECTED. Floor unchanged
# where it still holds (K35: rounded down); measured count in parens.
SAB_REACH_POP='tests/utf8/axis08_lookbehind_varwidth.rxt|^pattern .*\(\?<|18'  # measured 24
SAB_COUNT=1
SAB_BEFORE='"    (void)n;                 /* reads only below pos, as the contract says */\n"
"    while (k--) {\n"'
SAB_AFTER='"    (void)n; (void)s;\n"
"    return k > pos ? $_BACK_STEP_NONE : pos - k;  /* SABOTAGE S-U5 */\n"
"    while (k--) {\n"'
