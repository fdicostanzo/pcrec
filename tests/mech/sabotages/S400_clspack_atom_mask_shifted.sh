# S400 ([OPT-CLSPACK], lane clspack) -- A TABLE-READ CLASS IS TESTED WITH
# ANOTHER CLASS'S ATOM MASK.
#
# THE CLAIM (docs/spec/tuning.md §2.34): the shared atom table answers exactly
# what each class's own 32-byte bitmap answers. The plant hands every matcher
# the mask of the class before it in the table's order (the first keeps its
# own), so the atom route answers a different class at ten of eleven
# positions. ANSWER-MOVING: tests/base/clspack_atoms.rxt's atom blocks and
# run_clspack.sh's differential against -fno-cls-pack both see it; the
# structural PART 1/2 arms stay green (the table, the matchers and the stamp
# are all still there), which is the row's point -- only the answers moved.
SAB_ID="S400-clspack-atom-mask-shifted"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="clspack harness"
SAB_HARNESS_TARGET="tests/base/clspack_atoms.rxt"
SAB_DESC="the atom-table emission passes each class the atom mask of the class before it, so the shared-table route tests the wrong set"
SAB_DOC_FIGURE="MEASURED solo 2026-09-30 at the clspack tip: clspack:4fail/20pass (the three differentials + population), corpus:16fail/63pass (tests/base/clspack_atoms.rxt's atom blocks; site-10 and atom-65 green) DETECTED."
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ][02468]"'
SAB_REACH_EXPECT='#define RX_VM_CLS_ATOMS 12'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                                           tab, &v->clstab.atoms, v->clsatom[i]);'
SAB_AFTER='                                           tab, &v->clstab.atoms, v->clsatom[i] ? v->clsatom[i] - 1 : 0);'
