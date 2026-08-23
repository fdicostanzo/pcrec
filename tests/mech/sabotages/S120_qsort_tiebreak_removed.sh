# S120 (design row S-BR17) — §8.2's NUMBER TIEBREAK IS REMOVED FROM THE
# REFLECTION TABLE'S COMPARATOR.
#
# THE ONE ROW IN THIS FAMILY WHOSE DETECTOR IS STRUCTURAL RATHER THAN
# BEHAVIOURAL, and R32's re-check is why. Its first analysis concluded the row
# COULD NOT GO RED — glibc's `qsort` is a stable merge sort, so a name-only
# comparator preserves insertion order — and then the premise was corrected
# and it got WORSE: `mod_named_groups.c` PREPENDS each declaration and
# `emit_dfa.c` walks that list FROM THE HEAD, so the array reaching `qsort` is
# in DESCENDING group number. Under a stable sort a tiebreak-less comparator
# therefore emits (name asc, number DESC).
#
# THAT IS NOT A REPRODUCIBILITY NICETY, IT IS A WRONG RULE. `match_api.md`
# §6's caller algorithm — bsearch, walk BACK to the run's first row, then
# FORWARD to the first participating one — then selects the HIGHEST-numbered
# participating group, which is exactly the "last set" rule §8.3's `"xyy"`
# cell rules out. The table would encode a resolution rule the emitted matcher
# does not use.
#
# AND A BEHAVIOURAL ROW HERE WOULD NOT BE A CONTROL: whether it goes red
# depends on TWO unspecified properties agreeing (qsort's stability and the
# list's direction). So the detector reads the emitted rows' ORDER off the
# ARTIFACT — `tests/codegen`'s [M6.5-DUPNAMES] check, strictly increasing in
# (name, number) — which depends on neither.
SAB_ID="S120-qsort-tiebreak-removed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/backrefs/dupnames.rxt"
SAB_DESC="ng_cmp_name loses its number tiebreak, so rows sharing a name come out in whatever order the sort leaves them -- on glibc, DESCENDING, because the declaration list is prepended and walked from the head. The emitted table then encodes the \"last set\" resolution rule while the matcher implements \"first set\", and no MATCH-semantics test can see the disagreement"
SAB_DOC_FIGURE="PREDICTED: codegen RED on [M6.5-DUPNAMES] for the three dup-name fixtures; the corpus GREEN (the emitted matcher is unchanged). Canonical figure owed from run_sabotage_matrix.sh S120."
SAB_COUNT=1
SAB_BEFORE='    int c = strcmp((*pa)->name, (*pb)->name);
    if (c != 0) return c;
    return (*pa)->number < (*pb)->number ? -1
         : (*pa)->number > (*pb)->number ?  1 : 0;'
SAB_AFTER='    return strcmp((*pa)->name, (*pb)->name);   /* SABOTAGE S120 */'
