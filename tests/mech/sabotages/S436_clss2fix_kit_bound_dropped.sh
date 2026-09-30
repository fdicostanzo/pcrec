# S436 ([CLS-TREE] S2 review fixes, lane clss2fix, D139 item 1) -- THE KIT
# DROPS A BOUND THAT IS NOT DEAD.
#
# A MISCOMPILE AT --tune=-2/-1: a byte kit's global bound is omitted only
# where it is always false — the set spans 0 through the largest byte. The
# plant omits it wherever the set reaches 0xFF, so a set starting ABOVE 0
# (`[a\x80-\x8f\xf0-\xff]`) runs its first section's leaf on a byte below
# its base, where the base-relative offset wraps. The detector is
# run_clspack.sh PART 4's `hi255` witness (kit vs -fno-cls-kit).
SAB_ID="S436-clss2fix-kit-bound-dropped"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="clspack"
SAB_DESC="emit_bound omits the kit matcher's global bound for every set reaching cp_max, not only one that also starts at 0, so a byte kit over [a\\x80-\\xff...] tests bytes below its base with a wrapped offset"
SAB_DOC_FIGURE="Read the current figure from a run (lane clss2fix measured it solo at landing; see docs/dev/lanes/clss2_report.md, Review fixes)."
SAB_REACH='"$PCREC" --engine=vm --tune=-2 -p rx -o - --pattern "([a\\x80-\\x8f\\xf0-\\xff]+)z"'
SAB_REACH_EXPECT='if ((unsigned)(cp - 97u) > 158u) return 0;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (lo == 0 && hi >= cp_max) return;'
SAB_AFTER='    if (hi >= cp_max) return;'
