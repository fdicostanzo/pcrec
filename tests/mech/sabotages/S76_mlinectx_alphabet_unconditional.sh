# S76 — [M6.2 wave C] THE NEWLINE ALPHABET REFINEMENT MADE UNCONDITIONAL.
#
# assertions_design.md §3.7 puts `(?m)$`'s operand on the CLASS axis, which
# requires the byte class map to be refined by the newline set so that "the
# byte about to be consumed is a newline" is constant inside a class. The
# refinement is GATED on the machine actually carrying an N_BOT_M/N_EOL_M, and
# the claim wave C lands with is that a `(?m)`-free pattern therefore pays
# nothing at all — same alphabet, same states, same tables, same emitted
# bytes.
#
# This sabotage removes the gate. Every pattern's class map is then refined by
# the newline set whether or not the pattern asks a multiline question, so
# every artifact whose alphabet did not already separate LF gains a class and
# moves bytes.
#
# WHAT MAKES THIS ROW WORTH ITS RUNTIME: the sabotage is SEMANTICS-PRESERVING,
# exactly as S71's is on the word half. A refined alphabet is still an
# alphabet — the same partition, more finely cut — so every emitted matcher
# answers identically, the whole `.rxt` corpus stays green, both oracles stay
# green, and every differential in the tree stays green. Only the byte-identity
# gate can see it.
#
# It is also the SHAPE of the mistake that would really happen, and wave C
# makes it likelier than wave B did: the two refinements now sit on ADJACENT
# LINES, one gated on `has_word` and one on `has_nl`, next to the ungated
# per-N_CLASS loop above them. Deleting one condition to "make the block
# uniform" is a tidier-looking diff than what it replaces.
SAB_ID="S76-mlinectx-alphabet-unconditional"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="mlinectxidentity harness"
SAB_DESC="eqclasses refines the byte alphabet by the newline set on EVERY pattern instead of only on those carrying a (?m)^/(?m)\$: every artifact whose alphabet did not already separate LF gains a class and moves bytes, with every answer unchanged"
SAB_DOC_FIGURE="tests/codegen/run_mlinectx_identity.sh: the (?m)-free identity population goes from all-identical to largely differing; the corpus stays green"
# MEASURED before this row shipped, the same way every wave C row was: 1032 of
# 1161 corpus artifacts change under this edit, and not one answer does. The
# margin is enormous because almost no pattern's alphabet already separates
# LF — which is exactly why the gate on it has to be a byte comparison and not
# a behaviour test.
SAB_COUNT=1
SAB_BEFORE='    if (has_nl)   ncls = refine_by(d, ncls, pcrec_cls_newline);'
SAB_AFTER='    ncls = refine_by(d, ncls, pcrec_cls_newline);   /* SABOTAGE S76 */'

# ---------------------------------------------------------------------------
# ANNOTATED 2026-08-19 BY THE [M6.2] WAVE D LANE — SAB_DOC_FIGURE ABOVE IS
# MEASURED WRONG, AND THE REASON GENERALISES TO EVERY KNOB-BASED IDENTITY GATE.
#
# The figure claims the (?m)-free identity population "goes from
# all-identical to largely differing" under this row. It does not.
# MEASURED 2026-08-19 by applying this exact edit and running
# `tests/codegen/run_mlinectx_identity.sh`: the identity sweep stays
# all BYTE-IDENTICAL.
#
# THE MECHANISM. That script builds its reference compiler from THE TREE'S
# OWN SOURCES with `-DPCREC_NO_MLINECTX`, i.e. from the SABOTAGED sources.
# This edit deletes the `if (has_nl)` gate, so the refinement runs in the
# subject build AND in the reference build, and the difference the gate
# measures cancels. Only sabotages that live inside code the knob actually
# suppresses are visible to a knob-based reference.
#
# WHAT DOES CATCH IT TODAY, and it is incidental rather than designed: with
# the gate deleted, `has_nl` becomes an unused parameter, the reference
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
# THIS ROW'S KNOB IS NOT WAVE D'S TO DO: it changes wave C's machinery
# and wants its own slice. Recorded here rather than silently left, because a
# committed SAB_DOC_FIGURE that is false is worse than an absent one.
# ---------------------------------------------------------------------------
