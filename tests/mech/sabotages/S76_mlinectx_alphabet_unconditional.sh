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
SAB_COUNT=1
SAB_BEFORE='    if (has_nl)   ncls = refine_by(d, ncls, pcrec_cls_newline);'
SAB_AFTER='    ncls = refine_by(d, ncls, pcrec_cls_newline);   /* SABOTAGE S76 */'
