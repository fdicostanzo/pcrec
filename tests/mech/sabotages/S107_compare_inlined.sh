# S107 (design row S-BR5) — THE COMPARE IS INLINED INSTEAD OF ROUTED THROUGH
# THE SEAM.
#
# THE S68 SHAPE, one construct over: IT CHANGES NO ANSWER. Under the byte
# backend an inlined `s[at+i] != s[ref_start+i]` loop is exactly what
# `$_bref_match` does, so every oracle in this tree stays green while the
# artifact has acquired encoding-sensitive byte arithmetic in SHARED EMITTER
# CODE — the residue class D58 scope item 3 enumerates by name ("caseless
# backref comparison when M6 lands") and the thing the seam exists to prevent.
#
# A UTF-8 backend would then answer differently WITHOUT ANY EMITTER CHANGE
# BEING POSSIBLE: one captured character can fold to two, so the consumed
# LENGTH stops equalling `ref_end - ref_start`, and an emitter that computes
# the length itself cannot be corrected from `src/gen/enc/`.
#
# WHAT CATCHES IT is the codegen check's fixture-DECLARED per-site count —
# the artifact must call `rx_bref_match` exactly as many times as the fixture
# says, and an inlined compare calls it zero times. Nothing behavioural can.
SAB_ID="S107-compare-inlined"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/backrefs/numeric.rxt"
SAB_DESC="The A_BREF emission writes an inline byte-compare loop instead of calling the encoding residual entry. Under the byte backend the ANSWERS ARE IDENTICAL, so every corpus and every differential stays green; what moves is that the compare stopped being replaceable by another encoding's backend"
SAB_DOC_FIGURE="PREDICTED: codegen RED on the per-site count for the residbref1/residbref3/residbrefci/residbrefboth fixtures; the corpus and brefdiff GREEN. Canonical figure owed from run_sabotage_matrix.sh S107."
SAB_COUNT=1
SAB_BEFORE='            "        took = %s(subject, subject_length,\n"
            "                  (size_t)ref_start, (size_t)ref_end,\n"
            "                  scan_position);\n",'
SAB_AFTER='            "        { size_t i_; took = (ptrdiff_t)(ref_end - ref_start);\n"
            "          for (i_ = 0; i_ < (size_t)(ref_end - ref_start); i_++)\n"
            "              if (scan_position + i_ >= subject_length ||\n"
            "                  subject[scan_position + i_] != subject[ref_start + i_])\n"
            "                  { took = -(ptrdiff_t)i_ - 1; break; } }\n"
            "        (void)0;   /* SABOTAGE S107: %.0s */\n",'
