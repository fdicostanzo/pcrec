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
SAB_DOC_FIGURE="tests/codegen/run_mlinectx_identity.sh: the (?m)-free identity population goes from all-identical to 1117 of 1201 DIFFERING; the corpus stays green. TRUE ONLY SINCE THE [M6.2] REPAIR SLICE MOVED THIS ROW'S REFERENCE KNOB (2026-08-19) -- before that the sweep stayed all-identical and the row was scored DETECTED through an orphaned-parameter warning; see the annotation below. CANONICAL MATRIX RUN 2026-08-19: mlinectxid:1fail/3pass, corpus:0fail/20533pass -- DETECTED"
# MEASURED before this row shipped, the same way every wave C row was: 1032 of
# 1161 corpus artifacts change under this edit, and not one answer does. The
# margin is enormous because almost no pattern's alphabet already separates
# LF — which is exactly why the gate on it has to be a byte comparison and not
# a behaviour test.
SAB_COUNT=1
SAB_BEFORE='    if (has_nl)   ncls = refine_by(d, ncls, pcrec_cls_newline);'
SAB_AFTER='    ncls = refine_by(d, ncls, pcrec_cls_newline);   /* SABOTAGE S76 */'

# ---------------------------------------------------------------------------
# ANNOTATED 2026-08-19 BY THE [M6.2] WAVE D LANE, THEN RESOLVED THE SAME DAY BY
# THE [M6.2] REPAIR SLICE. Both halves are kept: the annotation is the finding,
# the resolution is what it cost to fix, and the second is not what the first
# predicted.
#
# WHAT WAVE D FOUND. The pre-slice SAB_DOC_FIGURE claimed the (?m)-free
# identity population "goes from all-identical to largely differing" under this
# row. It did not. MEASURED 2026-08-19 by applying this exact edit and running
# `tests/codegen/run_mlinectx_identity.sh`: the identity sweep stayed BYTE-IDENTICAL.
#
# THE MECHANISM. That script builds its reference compiler from THE TREE'S OWN
# SOURCES with `-DPCREC_NO_MLINECTX`, i.e. from the SABOTAGED sources. This edit deletes
# the `if (...)` gate, so with the knob PINNING THE FLAG the refinement ran in
# the subject build AND in the reference build and the difference CANCELLED.
# Only sabotages living inside the region the knob actually suppresses are
# visible to a knob-based reference. What caught it instead was INCIDENTAL:
# the deleted gate orphaned a parameter, the reference build emitted
# `-Wunused-parameter`, and the script's own "the reference build produced
# warnings" check fired. The row was scored DETECTED for a reason unrelated to
# what it claims to detect.
#
# WHAT THE REPAIR SLICE DID, AND THE PART THAT SURPRISED IT. Wave D prescribed
# its own cure — move the knob to the EMITTER's decision points. MEASURED
# FIRST: that is NOT sufficient here. `\G` refines no alphabet and interns no
# state the emitter cannot neutralize, but this row's construct refines the
# ALPHABET, and no emitter branch can un-refine a partition — so the reference
# build goes on emitting the sabotaged class table. With an emitter-only knob
# the sweep stays byte-identical. That emitter-only figure was measured on
# S71's population (1186/1186 identical) rather than on this one; the two
# rows share a mechanism exactly, differing only in which byte set the
# refinement uses.
#
# THE KNOB IS NOW AROUND THE ACTION. `src/ir/dfa.c`'s `eqclasses` carries a
# `#ifndef PCREC_NO_MLINECTX` around the refinement LINE this row edits, so the
# reference build excludes the action entirely no matter what an edit does to
# its gate; a second pin sits in front of the flag's other consumers, and
# `src/gen/emit_dfa.c` carries an emitter half for the sites the emitter
# really decides. The `(void)` cast under the knob also removes the orphaned
# parameter, so the incidental detection path is GONE and this row must now be
# caught by BYTES or not at all. MEASURED AFTER, on THIS row's own
# population: 1117 of 1201 multiline-anchor-free artifacts DIFFER (S71's
# figure on its own population is 1178 of 1186).
#
# THE DURABLE RULE, recorded in tests/mech/CLAUDE.md: wrap the ACTION a
# construct performs, never the FLAG that decides whether to perform it. A
# sabotage that deletes the flag's consumer is the realistic edit, and it
# cancels a flag pin exactly.
# ---------------------------------------------------------------------------
