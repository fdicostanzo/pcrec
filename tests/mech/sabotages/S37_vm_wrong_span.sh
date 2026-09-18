# S37 — [M4.5b] A PLANTED WRONG SPAN. D44.1 extends the cursor rung to
# deterministic capture-bearing bodies by DERIVING each group's span from the
# cursor at loop exit instead of writing it per iteration. That derivation is
# arithmetic on offsets, which is exactly the kind of code that can be wrong by
# one forever without anything structural noticing: the artifact still has a
# cursor loop, still writes both slots, still costs O(1) frames.
#
# The sabotage makes the group's END offset equal its START offset, so every
# such group reports a zero-length span at the right place. `(ab)+` on "abab"
# goes from group 1 = [2,4) to [2,2).
SAB_ID="S37-vm-wrong-span"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="vm"
SAB_DESC="the cursor rung derives a group's END from the same offset as its START (every deterministic-body group reports a zero-length span)"
SAB_DOC_FIGURE="tests/vm/run_vm_tests.sh: the oracle sweep fails (zero-length groups on every fixed-stride repeat)"
# [ENG-BREP] TWO occurrences since 2026-08-16, not one. The cursor rung now
# has two emission paths -- the backtracking one and the possessified one --
# and each derives the group's end from the cursor the same way. The count is
# raised rather than the anchor narrowed to one of them ON PURPOSE: the defect
# this sabotage plants exists in BOTH paths, so a sabotage that planted it in
# only one would leave the other silently unmeasured, and the whole point of a
# sabotage is to ask whether the checks can see the defect wherever it lives.
#
# replace.py REFUSING when the count drifted is the tool working: this file
# came back ANOMALY rather than quietly sabotaging one of the two paths, which
# is exactly the anchor-mismatch failure mode it exists to make loud.
#
# RE-AIMED 2026-09-18 (lane w2b, [REVW.2] wave 2 stage 3). Both arms used to
# build the group's span text with `snprintf(val, sizeof val, ...)` into a
# per-arm `char val[PCREC_MAX_EMIT_NAME_LEN]` written TWICE (start, then end);
# stage 3 made `vm_rolef` arena-owned, so each write is now its own fragment
# passed straight to `vm_set` and the statement ends in `,` where it used to
# end in `);`. The anchor changes by exactly that one character.
#
# THE COUNT-2 PROPERTY IS PRESERVED DELIBERATELY AND IS WHY THE ANCHOR KEEPS
# ITS 21-SPACE PREFIX. replace.py matches a whole-file SUBSTRING, not a line,
# and the two arms sit at DIFFERENT depths (32 and 28 spaces of indent today,
# 25 and 21 before) -- so an anchor carrying the SHALLOWER indent is a suffix
# of the deeper line too and matches both, which is what makes one anchor
# plant the defect in both emission paths. An anchor re-aimed to either arm's
# own column would match ONCE and leave the other path silently unmeasured,
# the exact failure the note above says this row exists to avoid.
SAB_COUNT=2
SAB_BEFORE="                     stride - caps[i].off - caps[i].len),"
SAB_AFTER="                     stride - caps[i].off),  /* SABOTAGE S37 */"
