# S112 (design row S-BR8) — RULE 3's COUNT USES THE WHOLE PATTERN INSTEAD OF
# "SO FAR".
#
# §5's ASYMMETRY, and the reason it is a row is stated in the design: "a design
# that implements one count for both is wrong in one direction or the other,
# AND NO TEST THAT ONLY USES GROUPS-BEFORE WILL NOTICE."
#
# MEASURED: `\1`..`\9` see the WHOLE pattern (`\1(a)` compiles, the group is
# AFTER the escape), while `\10`+ see only what PRECEDES them (`\10(a)..(j)`
# is the OCTAL byte 0x08, not a reference to group 10). This sabotage gives
# rule 3 the whole-pattern count, which turns that octal byte into a
# backreference — a SILENT MIS-PARSE, not an error.
#
# EXACTLY ONE FAMILY OF CELLS SEES IT: `octal.rxt`'s `\10(a)..(j)` block.
# Every groups-before cell in the file still passes, which is what makes this
# a discriminating row rather than a smoke test.
SAB_ID="S112-rule3-whole-pattern"
SAB_FILE="src/parse/mod_backrefs.c"
SAB_SUITES="harness brefdiff"
SAB_HARNESS_TARGET="tests/backrefs/octal.rxt"
SAB_DESC="Rule 3's multi-digit backref-vs-octal decision consults the FINAL group count instead of the count SO FAR, so \\10(a)..(j) becomes a reference to group 10 where PCRE2 reads the octal byte 0x08. Deferring that decision is exactly what lets a later group retroactively turn an octal literal into a reference"
SAB_DOC_FIGURE="PREDICTED: the corpus RED on octal.rxt's rule-3 block only. Canonical figure owed from run_sabotage_matrix.sh S112."
SAB_COUNT=1
SAB_BEFORE='        if (v >= 1 && v <= (long)cx->ncap) {'
SAB_AFTER='        if (v >= 1) {   /* SABOTAGE S112: no "so far" bound at all */'
