# S123 ([M6.6.2] wave B+C, design §9.3 S-LA2) — THE CURSOR IS RESTORED.
#
# THE CLAIM, and it is the definition of the construct rather than a detail: a
# lookaround keeps the VERDICT and throws the POSITION away. `vm_look` records
# `scan_position` into `SLOT_LOOK_POS<n>` at the assertion's entry and puts it
# back at `L_ok`; drop that one line and every lookahead becomes
# WIDTH-CONSUMING — `(?=ab)abc` on "abc" would need "ababc".
#
# COARSE, AND KEPT FOR THE REASON DESIGN §9.3 GIVES: its absence would be
# worse. Nearly every cell in the corpus goes red, which is exactly what a
# claim this central should look like when it is broken.
#
# THE `(void)` LINES IN THE AFTER TEXT ARE NOT DECORATION: `b` and `sl` have no
# other use in this block, and a sabotage that fails to BUILD scores as a
# harness error rather than as a detection.
SAB_ID="S123-look-no-cursor-restore"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC="vm_look's positive arm stops restoring scan_position from SLOT_LOOK_POS, so the assertion CONSUMES its body's bytes — a zero-width construct that is not zero-width"
SAB_DOC_FIGURE="PREDICTED: most of tests/lookaround/ goes red; (?=ab)abc no longer matches \"abc\". Canonical figure owed from run_sabotage_matrix.sh S123."
SAB_COUNT=1
SAB_BEFORE='            sb_printf(b, "    scan_position = (size_t)slot_values[%s];\n", sl);'
SAB_AFTER='            /* SABOTAGE S123: the cursor is NOT restored */
            (void)b; (void)sl;'
