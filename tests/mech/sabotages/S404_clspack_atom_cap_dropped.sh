# S404 ([OPT-CLSPACK], lane clspack) -- THE 64-ATOM CAP IS NOT ENFORCED.
#
# A class's membership is one 64-bit mask shifted by the byte's atom number,
# so a partition of 65 atoms cannot be tested that way. The plant drops the
# cap from pcrec_clskit_atoms, so the 65-atom witness takes the atom row
# (its stamp reads 65 where it must read 0) with a mask that cannot represent
# its 65th atom.
SAB_ID="S404-clspack-atom-cap-dropped"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="clspack"
SAB_DESC="pcrec_clskit_atoms no longer refuses a partition of more than 64 atoms, so the atom row fires past the mask's width"
SAB_DOC_FIGURE="RE-MEASURED solo 2026-09-30 at the land4 tip (run_clspack.sh gained [deny-kit], 24 -> 25 checks): clspack:1fail/24pass -- [atom-65] (RX_VM_CLS_ATOMS 65 where 0 is due) DETECTED."
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ][02468]"'
SAB_REACH_EXPECT='#define RX_VM_CLS_ATOMS 12'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (out->natoms > PLACE.atom_max) return false;'
SAB_AFTER='    (void)0;'
