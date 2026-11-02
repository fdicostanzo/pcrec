# S105 (design row S-BR1) — THE UNSET TEST BECOMES `ref_end > ref_start`.
#
# The plausible implementation, and it is wrong in one direction only: it
# turns every EMPTY CAPTURE into a failure. A group that captured the empty
# string is SET — `^(x?)y\1z$` on "yz" is (0,2) with group 1 = (0,0) — and the
# reference matches vacuously, consuming nothing.
#
# EVERY NON-EMPTY CELL STILL PASSES, which is what makes it a row rather than
# a smoke test: the whole numeric corpus agrees except `numeric.rxt`'s E
# block, whose cells exist for exactly this.
#
# It is also the mirror of S107's mistake one level down: "is the pair set"
# and "does the pair have length" are one `if` apart, and PCRE2 distinguishes
# them (§3.3 fails an UNSET reference; §3.4 succeeds an EMPTY one).
# RE-AIMED 2026-10-30 (lane vmrec, [VMREC] (a): the VM body as typed records):
# the bref compare block is VK_BREF's renderer (vm_r_bref), text unchanged. Same detector, same arm.
SAB_ID="S105-unset-test-is-length"
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES="brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/numeric.rxt"
SAB_DESC="The emitted chain tests slot_values[START] != slot_values[END] instead of != PCREC_UNSET, so a published EMPTY capture reads as unset and the reference FAILS. ^(x?)y\\1z\$ on \"yz\" answers nomatch where PCRE2 gives (0,2) with group 1 = (0,0); every non-empty cell still passes"
SAB_DOC_FIGURE="PREDICTED: the corpus RED on numeric.rxt's EMPTY block; brefdiff RED. Canonical figure owed from run_sabotage_matrix.sh S105."
SAB_COUNT=1
# FIXED 2026-10-31 (lane vmrecg): the first re-aim added a `%s` to the format without an
# argument, shifting the rest of the printf's arguments (`slot_values[\n]`, "expected expression
# before ']'"). The AFTER now rewrites the format AND its argument list together.
SAB_BEFORE='            "        %sif (slot_values[%s] != PCREC_UNSET) {\n"
            "            ref_start = slot_values[%s];\n"
            "            ref_end   = slot_values[%s];\n"
            "        }%s",
            i ? "else " : "", ns, ns, ne,'
SAB_AFTER='            "        %sif (slot_values[%s] != slot_values[%s]) {   /* SABOTAGE S105 */\n"
            "            ref_start = slot_values[%s];\n"
            "            ref_end   = slot_values[%s];\n"
            "        }%s",
            i ? "else " : "", ns, ne, ns, ne,'
