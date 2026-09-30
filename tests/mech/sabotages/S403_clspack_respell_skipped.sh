# S403 ([OPT-CLSPACK], lane clspack) -- THE PROGRAM IS NOT RE-SPELLED.
#
# The atom row fires and the table emission writes the shared table and the
# matchers, but the program keeps reading the per-class bitmaps the table
# emission no longer writes: the artifact names arrays it lacks and fails to
# compile. run_clspack.sh sees it twice (a bitmap read left in the atom
# artifact; the two-artifact driver does not build) and the corpus arm sees
# every atom block fail to build.
SAB_ID="S403-clspack-respell-skipped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="clspack harness"
SAB_HARNESS_TARGET="tests/base/clspack_atoms.rxt"
SAB_DESC="vm_cls_tables chooses the atom table (or, at --tune -2/-1, a kit matcher) but never re-spells the program's bitmap reads"
# RE-ANCHORED 2026-09-30 (lane clss2, [CLS-TREE] S2): the re-spell is now taken whenever any read is not the bitmap it was written as (the atom table, or a kit matcher at the size-leaning positions); the plant still skips it, intent unchanged.
SAB_DOC_FIGURE="RE-MEASURED solo 2026-09-30 at the land4 tip (run_clspack.sh gained [deny-kit], 24 -> 25 checks): clspack:10fail/15pass, corpus:46fail/33pass -- every atom artifact reads a bitmap it lacks and fails to build DETECTED."
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ][02468]"'
SAB_REACH_EXPECT='#define RX_VM_CLS_ATOMS 12'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (respell) vm_cls_respell(v);'
SAB_AFTER='    if (respell) (void)vm_cls_respell;'
