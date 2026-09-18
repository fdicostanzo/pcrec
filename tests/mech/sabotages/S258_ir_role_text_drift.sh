# S258 — [REVW.1] wave 1 stage 0's irsb BYTE-NEUTRALITY ARM
# (tests/codegen/run_ir_listing.sh, docs/dev/w1stage0_evidence/CLAUDE.md).
#
# The arm pins the --emit-ir listing's bytes against a committed per-pattern
# baseline (tests/codegen/manifests/ir_listing_baseline/) so a future wave's
# emitter-interior moves are checkable against a real prior state. This
# sabotage is the arm's own failing-direction proof: it moves ONE role-text
# word in vm_alt's alternation-entry comment, which reaches `irsb` (the
# listing) but NOT any byte the four standing `.c`-artifact identity gates
# compare — those gates would stay green under this exact edit, which is
# the whole reason emitvm_second_pass.md S1/S5 (EP2) flags `irsb` as a
# stream with no other comparator.
#
# WHY THIS ROLE STRING SPECIFICALLY: `vm_alt` is reached by
# run_ir_listing.sh's own PATTERNS population (docs/dev/w1stage0_evidence/
# listing_reach_census.py's PRIMARY census: 3 of 3 vm_alt sites reached),
# so the sabotage is exercised on the FIRST pattern in that array
# (`a(b|c)+d`) and needs no corpus change.
SAB_ID="S258-ir-role-text-drift"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="irlisting"
SAB_DESC="vm_alt's alternation-entry role text is reworded, moving the --emit-ir listing's bytes with no .c-artifact byte moving at all"
SAB_DOC_FIGURE="tests/codegen/run_ir_listing.sh: the BYTE-NEUTRALITY check fails for a(b|c)+d"
SAB_COUNT=1
SAB_BEFORE="               ? vm_rolef(v, \"alternation entry (%d branches)\", nbr)"
SAB_AFTER="               ? vm_rolef(v, \"alternation ENTRY (%d branches)\", nbr)  /* SABOTAGE S258 */"
