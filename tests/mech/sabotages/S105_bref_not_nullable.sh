# S105 (design row S-BR3) — `vm_nullable` RETURNS FALSE FOR `A_BREF`.
#
# THE ONE ROW IN THIS FAMILY WHOSE FAILURE IS A HANG rather than a wrong
# answer, which is why its detector is the harness's derived TIMEOUT and not a
# span comparison.
#
# A referenced group can publish an EMPTY capture, and the reference then
# consumes nothing: `^(x?)y\1z$` on "yz" is (0,2) with group 1 = (0,0), and
# `^(a?)\1{3}$` matches "" at (0,0). So a quantifier over a backreference has
# a NULLABLE body and needs the empty-iteration guard (§3.3 of engine_m4). Say
# otherwise and `(\1)*` loops forever on a zero-width iteration.
#
# The guard is also what `mrl.c`'s `pcrec_minw(A_BREF) == 0` says from the
# other side: the two are ONE property read by two passes, and getting either
# wrong is unsound in a different direction.
SAB_ID="S105-bref-not-nullable"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness brefdiff"
SAB_HARNESS_TARGET="tests/backrefs/numeric.rxt"
SAB_DESC="vm_nullable answers FALSE for A_BREF, so a quantifier whose body is a backreference loses its empty-iteration guard. A group that captured the empty string makes the body consume nothing and the loop never terminates -- the failure is a HANG, caught by the harness's derived timeout rather than by a wrong span"
SAB_DOC_FIGURE="PREDICTED: the corpus TIMES OUT or fails on numeric.rxt's quantified block (^(a?)\\1{3}\$ on \"\"). Canonical figure owed from run_sabotage_matrix.sh S105."
SAB_COUNT=1
SAB_BEFORE='        case A_BREF: return true;'
SAB_AFTER='        case A_BREF: return false;   /* SABOTAGE S105 */'
