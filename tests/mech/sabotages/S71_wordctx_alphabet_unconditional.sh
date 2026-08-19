# S71 — [M6.2 wave B] THE ALPHABET REFINEMENT MADE UNCONDITIONAL.
#
# assertions_design.md §3.4 requires the byte class map to be refined by the
# word set so that "the previous byte was a word character" is constant inside
# a class. The refinement is GATED on the machine actually carrying an
# N_WORDB/N_NWORDB, and the claim wave B lands with is that a `\b`-free
# pattern therefore pays nothing at all — same alphabet, same states, same
# tables, same emitted bytes.
#
# This sabotage removes the gate. Every pattern's class map is then refined by
# the word set whether or not the pattern asks a word-boundary question, so
# every artifact in the corpus gains classes and moves bytes.
#
# WHAT MAKES THIS ROW WORTH ITS RUNTIME: the sabotage is SEMANTICS-PRESERVING.
# A refined alphabet is still an alphabet — the same partition, more finely
# cut — so every emitted matcher answers identically, the whole `.rxt` corpus
# stays green, both oracles stay green, and every differential in the tree
# stays green. Only the byte-identity gate can see it. That is precisely the
# case this project's check-design lesson is about: a claim of the form "X is
# free by construction" needs a construction check, and a construction check
# needs a measured failing direction.
#
# It is also the SHAPE of the mistake that would really happen. Nobody deletes
# a gate on purpose; someone moves the refinement next to the other
# refinements in eqclasses, where every one of its neighbours is
# unconditional, and the diff looks tidier than what it replaced.
SAB_ID="S71-wordctx-alphabet-unconditional"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="wordctxidentity harness"
SAB_DESC="eqclasses refines the byte alphabet by the word set on EVERY pattern instead of only on those carrying a \\b/\\B: every artifact in the corpus gains classes and moves bytes, with every answer unchanged"
SAB_DOC_FIGURE="tests/codegen/run_wordctx_identity.sh: the \\b-free identity population goes from all-identical to nearly all-differing; the corpus stays green"
SAB_COUNT=1
SAB_BEFORE='    if (has_word) ncls = refine_by(d, ncls, pcrec_cls_word_esc);'
SAB_AFTER='    ncls = refine_by(d, ncls, pcrec_cls_word_esc);   /* SABOTAGE S71 */'

# ---------------------------------------------------------------------------
# ANNOTATED 2026-08-19 BY THE [M6.2] WAVE D LANE — SAB_DOC_FIGURE ABOVE IS
# MEASURED WRONG, AND THE REASON GENERALISES TO EVERY KNOB-BASED IDENTITY GATE.
#
# The figure claims the \b-free identity population "goes from
# all-identical to nearly all differing" under this row. It does not.
# MEASURED 2026-08-19 by applying this exact edit and running
# `tests/codegen/run_wordctx_identity.sh`: the identity sweep stays
# 1135/1135 BYTE-IDENTICAL.
#
# THE MECHANISM. That script builds its reference compiler from THE TREE'S
# OWN SOURCES with `-DPCREC_NO_WORDCTX`, i.e. from the SABOTAGED sources.
# This edit deletes the `if (has_word)` gate, so the refinement runs in the
# subject build AND in the reference build, and the difference the gate
# measures cancels. Only sabotages that live inside code the knob actually
# suppresses are visible to a knob-based reference.
#
# WHAT DOES CATCH IT TODAY, and it is incidental rather than designed: with
# the gate deleted, `has_word` becomes an unused parameter, the reference
# build emits `-Wunused-parameter`, and the script's own "the reference build
# produced warnings" check fires. So the row is scored DETECTED for a reason
# unrelated to what it claims to detect — and a future sabotage of the same
# shape that did not happen to orphan a parameter would be scored UNDETECTED
# while the gate reported a clean bill of health.
#
# This is the project's recorded check-design failure class (a control sharing
# a source with what it controls) in a new place. Wave D's own knob is
# therefore placed at the EMITTER's decision points rather than in the
# analysis — see `src/gen/emit_dfa.c`'s `PCREC_NO_GSTART` block, and
# tests/mech/sabotages/S83's own note, where the re-placement immediately
# exposed a real emitter defect the mis-placed knob had hidden. RE-PLACING
# THIS ROW'S KNOB IS NOT WAVE D'S TO DO: it changes wave B's machinery
# and wants its own slice. Recorded here rather than silently left, because a
# committed SAB_DOC_FIGURE that is false is worse than an absent one.
# ---------------------------------------------------------------------------
