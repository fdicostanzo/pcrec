# S85 — [M6.2 WAVE E] THE `\K` ARTIFACT TAKES `caps[0][0]` FROM THE
# PREFILTER'S SPAN.
#
# THIS IS R30 C3's OWN REQUEST, WORD FOR WORD: "make the emitted `\K` artifact
# write `caps[0][0]` from the prefilter's span; the structural check must go
# red. Without this it is the only module check with no measured failing
# direction." The panel asked for the row before the check existed; this is it.
#
# THE CLAIM IT IS THE FAILING DIRECTION OF is assertions_design.md §6.3 rule 1:
# on a `\K` pattern `caps[0][0]` comes from the VM ALONE, and the prefilter's
# start is used only to bound the search, never written out. Under the default
# (hybrid) engine that prefilter start is `win[0][0]` — the REVERSE PASS's
# answer — which is the PRE-`\K` start by construction, because src/ir/nfa.c
# lowers `\K` to an epsilon so the prefilter is literally the machine the
# `\K`-free pattern builds.
#
# THE SABOTAGE forces `<prefix>_caps_out`'s pre-wave arm on every artifact, so
# a `\K` pattern reports where matching BEGAN instead of where the winning
# path last crossed a `\K`. Nothing else changes: the trailed write is still
# emitted, the slot is still filled, the capacities are still sized for it —
# the artifact simply stops reading it. That is deliberately the SHARPEST
# version of the defect rather than the loudest, because a sabotage that
# deleted the write too would fail on shapes a wrong-provenance bug does not.
#
# WHAT IT IS MEASURED TO MOVE, and the spread is the point:
#
#     tests/codegen/run_codegen_tests.sh   [M6.2-KRESET rule 1] goes RED, by
#                                          name: "caps_out does not read the
#                                          trailed \K slot at all". Rules 1b, 3
#                                          and 3b stay GREEN, which is right —
#                                          the \K-free artifact, the VM's entry
#                                          shape and the DFA's entry are all
#                                          genuinely untouched, and that
#                                          disjointness is what makes this row
#                                          and S86 two rows instead of one.
#     tests/assertions/kreset.rxt          RED, 198 of 581 cases.
#     run_kreset_diff.sh                   RED in §1 and §2.
#
# MEASURED 2026-08-19 (scratch tree, applied through tests/mech/lib/replace.py,
# never committed): codegen 1 fail / 55 pass; kreset.rxt 198 fail / 383 pass.
#
# BOTH the structural check and the corpus fire, and that is worth stating
# rather than treating as redundancy: a `\K` whose reported start is the
# prefilter's is WRONG IN ANSWERS as well as in provenance, so this is one of
# the rare rows where the structural check is not the only instrument. The
# ones where it IS the only instrument are the byte-identity gates
# (S69/S71/S76/S83), and wave E deliberately ships no such gate — its
# byte-identity claim rests on ONE emitter predicate, checked as rule 1b and
# measured once against the genuine pre-wave compiler.
SAB_ID="S85-kreset-caps-from-prefilter"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness kresetdiff"
SAB_HARNESS_TARGET="tests/assertions/kreset.rxt"
SAB_DESC="the emitted <prefix>_caps_out always takes caps[0][0] from its \`start\` argument -- which under the hybrid IS the prefilter's (i.e. the reverse pass's) span start -- instead of from the trailed \\K slot. Every \\K artifact then reports where matching BEGAN: 'a\\Kb' on \"ab\" answers (0,2) where PCRE2 answers (1,2)"
SAB_DOC_FIGURE="codegen 1 fail / 55 pass ([M6.2-KRESET rule 1], by name); tests/assertions/kreset.rxt 198 fail / 383 pass"
SAB_COUNT=1
SAB_BEFORE='        v.nkreset > 0
          ? "    /* \\K: the reported start is where the winning path last\n"'
SAB_AFTER='        0   /* SABOTAGE S85 */
          ? "    /* \\K: the reported start is where the winning path last\n"'
