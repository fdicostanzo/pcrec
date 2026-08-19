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
SAB_DOC_FIGURE="tests/codegen/run_wordctx_identity.sh: the \\b-free identity population goes from all-identical to 1178 of 1186 DIFFERING; the corpus stays green. TRUE ONLY SINCE THE [M6.2] REPAIR SLICE MOVED THIS ROW'S REFERENCE KNOB (2026-08-19) -- before that the sweep stayed 1135/1135 identical and the row was scored DETECTED through an orphaned-parameter warning; see the annotation below. CANONICAL MATRIX RUN 2026-08-19: wordctxid:1fail/2pass, corpus:0fail/20533pass -- DETECTED"
SAB_COUNT=1
SAB_BEFORE='    if (has_word) ncls = refine_by(d, ncls, pcrec_cls_word_esc);'
SAB_AFTER='    ncls = refine_by(d, ncls, pcrec_cls_word_esc);   /* SABOTAGE S71 */'

# ---------------------------------------------------------------------------
# ANNOTATED 2026-08-19 BY THE [M6.2] WAVE D LANE, THEN RESOLVED THE SAME DAY BY
# THE [M6.2] REPAIR SLICE. Both halves are kept: the annotation is the finding,
# the resolution is what it cost to fix, and the second is not what the first
# predicted.
#
# WHAT WAVE D FOUND. The pre-slice SAB_DOC_FIGURE claimed the \b-free
# identity population "goes from all-identical to largely differing" under this
# row. It did not. MEASURED 2026-08-19 by applying this exact edit and running
# `tests/codegen/run_wordctx_identity.sh`: the identity sweep stayed BYTE-IDENTICAL.
#
# THE MECHANISM. That script builds its reference compiler from THE TREE'S OWN
# SOURCES with `-DPCREC_NO_WORDCTX`, i.e. from the SABOTAGED sources. This edit deletes
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
# the sweep stays byte-identical (1186/1186 measured on S71's population).
#
# THE KNOB IS NOW AROUND THE ACTION. `src/ir/dfa.c`'s `eqclasses` carries a
# `#ifndef PCREC_NO_WORDCTX` around the refinement LINE this row edits, so the
# reference build excludes the action entirely no matter what an edit does to
# its gate; a second pin sits in front of the flag's other consumers, and
# `src/gen/emit_dfa.c` carries an emitter half for the sites the emitter
# really decides. The `(void)` cast under the knob also removes the orphaned
# parameter, so the incidental detection path is GONE and this row must now be
# caught by BYTES or not at all. MEASURED AFTER, on S71: 1178 of 1186
# \b-free artifacts DIFFER.
#
# THE DURABLE RULE, recorded in tests/mech/CLAUDE.md: wrap the ACTION a
# construct performs, never the FLAG that decides whether to perform it. A
# sabotage that deletes the flag's consumer is the realistic edit, and it
# cancels a flag pin exactly.
# ---------------------------------------------------------------------------
