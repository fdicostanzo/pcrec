# S91 — [M6.4.2] THE FREE DISCHARGE FIRES UNCONDITIONALLY.
#
# `src/parse/registry.c`'s own row comment has carried this trap since before
# there was a producer: *"naive determinization implements the NON-atomic
# semantics ... this row must never be lowered by simply ignoring the
# atomicity."* This row is that sentence made executable — the discharge
# deletes every `A_ATOMIC`, verdict or no verdict, which is exactly "ignore the
# atomicity" arrived at through the pass that is ALLOWED to delete some of them.
#
# WHY THE PASS THAT MAY DELETE SOME IS THE DANGEROUS ONE. `pcrec_discharge_atomic`
# is licensed by possessify's §2.2 verdict, whose whole content is "no retreat
# into this loop can produce a match the preferred path does not" — i.e. "the
# cut deletes nothing". Drop the condition and the pass is still
# semantics-preserving on every DEAD cut (which is most of the idiom family:
# `a*+b`, `[^"]*+"`), so the artifacts that most users compile stay correct and
# only the cells where the cut BITES move. A corpus without biting cells would
# be green.
#
# THAT IS WHY tests/atomic_groups/run_atomic_diff.sh ASSERTS A NON-VACUITY
# FLOOR measured against each pattern's two-byte UNCUT TWIN: 16 of its 26 cut
# patterns have a subject where the atomic answer and the uncut answer differ.
# This row is what that floor exists for.
SAB_ID="S91-discharge-unconditional"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="codegen harness atomicdiff registry"
SAB_HARNESS_TARGET="tests/atomic_groups/atomic_basic.rxt"
SAB_DESC="pcrec_discharge_atomic deletes EVERY A_ATOMIC(A_REP) rather than only those possessify's §2.2 verdict proves dead, so a cut that changes the language is silently dropped. '(?:a|ab)*+c' on \"abc\" then matches (0,3) where PCRE2 gives NO MATCH -- registry.c's own row comment names this exact trap"
SAB_DOC_FIGURE="PREDICTED: the whole atomic corpus RED on the biting cells, atomicdiff RED, and registry's check_engine_capability RED (a pattern whose cut bites would compile under --engine=dfa instead of refusing). Canonical figure owed from run_sabotage_matrix.sh S91."
SAB_COUNT=1
SAB_BEFORE='        if (ds_has(d, a) && a->l->k == A_REP) return a->l;'
SAB_AFTER='        if (a->l->k == A_REP) return a->l;   /* SABOTAGE S91 */'
