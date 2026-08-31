# S209 (D90/[LIM-1]) — A BARE NUMERIC #define IS RE-INTRODUCED OUTSIDE THE
# TABLE, DELINKING IT FROM THE ROW IT USED TO SHARE A NUMBER WITH.
#
# WHAT IT BREAKS. `src/gen/emit_vm.c`'s `VM_MAX_BODY_CAPS` — the cursor
# rung's own bound on capture groups a body may hold ([ENG-BREP]) — was a
# BARE `enum { VM_MAX_BODY_CAPS = 64 };` before this lane, independently
# spelled from `src/core/limits.h`'s `PCREC_MAX_REVDET_BODY_GROUPS`
# (`src/opt/revdet.c`'s own bound, ALSO 64), even though limits.h's own
# comment on that constant already said "Same number and same reason as the
# cursor rung's own VM_MAX_BODY_CAPS" — two homes for one fact, coincidentally
# still equal. [LIM-1] fixed it to `#define VM_MAX_BODY_CAPS
# PCREC_MAX_REVDET_BODY_GROUPS`, a bare alias with no number of its own. This
# plant PUTS THE LITERAL BACK — the exact two-homes shape the survey found
# and D90's own charter names by name ("a sabotage row catches a bare
# numeric #define outside the table").
#
# WHY NOTHING BEHAVIOURAL CAN SEE IT. The plant does not change the VALUE —
# 64 is 64 either way, so the cursor rung's own bound is completely
# unmoved, no artifact's bytes change, and the corpus/identity gates/
# differentials all stay green. This is the SAME shape [LIM-1]'s own
# find-vs-fix demonstrates: the drift is a PROVENANCE regression (two
# sources for one fact, silently re-diverging the day one of them is edited
# alone), not an answer regression, and only a source-level sweep for a
# bare policy-shaped literal outside src/core/limits.def can see it —
# `tests/registry/limits_check.sh` part 3.
#
# WHY THIS IS THE SHARPEST WITNESS FOR PART 3 RATHER THAN A FRESH INVENTED
# NAME. Inventing a brand-new bare constant (`#define FOO_MAX 99`) would
# also trip the check, but would prove only that the REGEX matches a name
# shape — this plant proves the check catches a REAL regression the survey
# actually found and fixed, on the constant most likely to be "simplified"
# back to a literal by a future edit that does not know the alias is load-
# bearing provenance rather than decoration.
SAB_ID="S209-vm-max-body-caps-delinked"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="limits vmidentity harness"
SAB_HARNESS_TARGET="tests/base/bounded_repeats.rxt"
SAB_DESC="src/gen/emit_vm.c's VM_MAX_BODY_CAPS -- a bare alias of PCREC_MAX_REVDET_BODY_GROUPS since [LIM-1] -- is put back as an independently-spelled literal 64, the exact two-homes-for-one-number shape the survey found and fixed; the VALUE is unchanged so no answer or artifact byte moves, and only a source-level sweep for a bare policy-shaped #define outside limits.def can see it"
SAB_DOC_FIGURE="PREDICTED: limits:1fail (part 3: 'enum { VM_MAX_BODY_CAPS = 64 }; -- VM_MAX_BODY_CAPS is neither a limits.def row nor on the cited allowlist'). harness and vmidentity expected 0fail -- the value is unchanged, so every answer and every emitted byte is identical. Canonical figure owed from run_sabotage_matrix.sh S209."
SAB_COUNT=1
SAB_BEFORE='#define VM_MAX_BODY_CAPS PCREC_MAX_REVDET_BODY_GROUPS'
SAB_AFTER='enum { VM_MAX_BODY_CAPS = 64 };   /* SABOTAGE S209: delinked from the table */'
