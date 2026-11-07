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
# RE-AIMED 2026-11-06 (lane vlbbuild, [VLOOKBEHIND] stage 1): the stated
# detector (class-bearing lookbehinds refuse) is gone -- a varying branch now
# compiles, and its extra candidates fail the end-check, so short answers stay
# green. Re-aimed on (?<=ab)x (`--emit-ir`: "fixed width 2", under the plant
# "width 2..8") at gate 3's classification control. `(?<=a)x` never carried
# it: a one-character body is a T3 context node built before any width rule.
# The paragraphs above are the original record.
SAB_ID="S-U4-width-rule-byte-units"
SAB_FILE="src/opt/mrl.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC='pcrec_cwmax'\''s A_CLASS arm answers the encoding'\''s maximum code-unit length (the [M5.0] cross-note'\''s refuted cure) instead of the definitional 1 character; since [VLOOKBEHIND] stage 1 a class-bearing lookbehind branch of two characters or more becomes a VARYING branch (2..8 for (?<=ab)x) instead of refusing, a one-character body is a T3 context node the width rule never sees'
SAB_DOC_FIGURE='PREDICTED (re-aimed, vlookbehind.md §7 S-U4, r2-1106 F5): run_lookaround_diff.sh §6 (gate 3, vlb_accept.py) red on its classification control -- (?<=ab)x and every multi-character fixed body judged `width K..4K` where libpcre2 at max_varlookbehind 0 accepts; probably also the cap/ceiling boundary cells where x4 crosses 255 or 65535 (W9/W9b in lookbehind_variable_witness.rxt). Answers on short bodies stay green (the extra candidates fail the end-check). Run at build: owed (report).'
# RE-ANCHORED at [PATFACTS] step 3.6 (R3, 2026-09-28, lane pf36):
# `pcrec_mrl_sat_add` retired into the shared `pcrec_sat_add(a, b, cap)`
# (src/opt/mrl.c); the disambiguating comment line above the call is
# unchanged and still what makes this anchor unique to `pcrec_cwmax`'s
# A_CLASS arm.
SAB_COUNT=1
SAB_BEFORE='            /* One CHARACTER, exactly and by definition — see the header. */
            return pcrec_sat_add(acc, 1, MRL_MINW_MAX);'
SAB_AFTER='            /* SABOTAGE S-U4: the cross-note cure — max code-unit length. */
            return pcrec_sat_add(acc, 4, MRL_MINW_MAX);'
