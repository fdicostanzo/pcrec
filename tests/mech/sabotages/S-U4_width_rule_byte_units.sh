# S-U4 ([M5.0] stage 2; utf8_design.md §8.2, RE-AIMED AS BUILT) -- THE WIDTH
# RULE FALLS BACK TO A BYTE-DENOMINATED ANSWER.
#
# THE DESIGN'S FORM OF THIS ROW IS INEXPRESSIBLE AS BUILT, AND THAT IS A
# FINDING RATHER THAN A GAP. §8.2 asks for "point the PARSE HOOK back at a
# byte-width walk, leaving postresolve on the character pair", detecting a
# divergence between the two timings. As built there is nothing to point at
# and nowhere to point it from: the two timings share ONE la_widths
# (mod_lookaround.c -- §5.6.4's "the move is to the RULE" landed as the rule
# having one home), and the byte-unit pcrec_maxw RETIRED with the re-aim
# (§5.6.2), so no byte-width function survives for a small edit to reach.
# The hazard the row defends is narrowed to its one surviving spelling:
# someone re-introduces byte thinking INSIDE the character pair.
#
# THE SABOTAGE IS THE [M5.0] CROSS-NOTE'S OWN PRESCRIBED CURE -- "the A_CLASS
# arm must become the encoding's maximum code-unit length" -- which §5.6
# refuted as breaking every lookbehind, and which is exactly the edit a
# well-meaning reader of that (uncorrected) row text would make. Applied,
# every class branch reads cwmin 1 != cwmax 4 and REFUSES: `(?<=a)x`, a
# pure-ASCII lookbehind that ships today, stops compiling.
SAB_ID="S-U4-width-rule-byte-units"
SAB_FILE="src/opt/mrl.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC="pcrec_cwmax's A_CLASS arm answers the encoding's maximum code-unit length (the [M5.0] cross-note's refuted cure) instead of the definitional 1 character; every lookbehind whose branch contains any class reads cwmin != cwmax and refuses, (?<=a)x included"
SAB_DOC_FIGURE="PREDICTED: every lookbehind block in tests/lookaround/ that has a class (or literal, which parses to a class) in a branch goes red as a pattern-compile failure; lookahead blocks are unmoved (no width rule). MEASURED at stage 2: lookbehind.rxt and lookbehind_widths.rxt red wholesale, refused.rxt's perr blocks still red-for-the-right-reason where the refusal text changed."
SAB_COUNT=1
SAB_BEFORE='            /* One CHARACTER, exactly and by definition — see the header. */
            return mrl_sat_add(acc, 1);'
SAB_AFTER='            /* SABOTAGE S-U4: the cross-note cure — max code-unit length. */
            return mrl_sat_add(acc, 4);'
