# S107 (design row S-BR3) — `vm_nullable` RETURNS FALSE FOR `A_BREF`.
#
# THE FAILURE IS A LOUD GIVE-UP, NOT A HANG -- CORRECTED 2026-08-22 after this
# row scored UNDETECTED in the 118-row matrix on 5edba64. Both halves of what
# this header used to say were wrong, and they were wrong in the two ways that
# together made the row unfalsifiable:
#
#   1. "ITS DETECTOR IS THE HARNESS'S DERIVED TIMEOUT." It is not. MEASURED on
#      the sabotaged build: `^(a?)\1*b$` on "b" returns PCREC_ERR_FRAMES in
#      0.10s -- the zero-width iterations exhaust the frame stack and the
#      artifact gives up LOUDLY (D45) instead of spinning. So this is an
#      ORDINARY wrong-answer row and the corpus catches it as one.
#
#   2. "THE CORPUS ALREADY HAS THE CELL." It did not. The corpus had the
#      SHAPE (`^(a*)\1*$`, numeric.rxt) and none of its live population:
#      every subject made group 1 non-empty ("aaa" -> (0,3)), so the reference
#      consumed bytes on every iteration and the guard never ended the loop.
#      And the cell this row's own DOC_FIGURE named, `^(a?)\1{3}$`, is a
#      BOUNDED repeat -- it never reaches the unbounded star rung that carries
#      the guard, so it emits no guard even on a CLEAN build (measured:
#      "empty-iteration guard" occurs 0 times in that artifact).
#
# The gap was corpus-side, not a wrong claim about the code: the module is
# correct and the sabotage IS observable. tests/backrefs/gen_corpus.py gained
# the "EMPTY CAPTURE UNDER AN UNBOUNDED QUANTIFIER" block, whose whole subject
# set is chosen so the referenced group publishes an EMPTY capture. MEASURED
# with that block in place: numeric.rxt 88/0 clean, 79/9 sabotaged.
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
SAB_ID="S107-bref-not-nullable"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness brefdiff"
SAB_HARNESS_TARGET="tests/backrefs/numeric.rxt"
SAB_DESC="vm_nullable answers FALSE for A_BREF, so a quantifier whose body is a backreference loses its empty-iteration guard. A group that captured the EMPTY string makes the body consume nothing, the loop re-enters at zero width, and the frame stack is exhausted -- the artifact gives up LOUDLY with PCREC_ERR_FRAMES (0.10s, measured), which the corpus catches as an ordinary wrong answer. Its live population is an UNBOUNDED quantifier over a reference to a group that captured empty; a bounded repeat never reaches the rung that carries the guard"
SAB_DOC_FIGURE="MEASURED 2026-08-22 (single-row run, after the corpus gained the empty-capture block): harness numeric.rxt 79 pass / 9 fail, every failure a PCREC_ERR_FRAMES give-up on a cell whose referenced group captured EMPTY (^(a*)\\1*\$ on \"\", ^(a?)\\1*b\$ on \"b\", ^(a?)\\1{2,}\$ on \"\" and \"aa\", ^()\\1+\$ on \"\"). Clean: 88/0."
SAB_COUNT=1
SAB_BEFORE='        case A_BREF: return true;'
SAB_AFTER='        case A_BREF: return false;   /* SABOTAGE S107 */'
