# S193 (S-ARTSIZE3) — [ART-SIZE] THE EMITTED-SIZE CAP'S COMPARISON INVERTED:
# THE REFUSAL TAKES THE COMPLEMENT OF THE POPULATION IT EXISTS FOR.
#
# D84's total cap is a REFUSAL, and a refusal is a contract (the [SEL-1]
# lesson, docs/dev/wake.md: nine tests that asserted one broke when a fallback
# quietly made it unreachable). This plant flips the one comparison that
# decides it, so every artifact BELOW the megabyte limit is refused and the
# three shapes the limit was written for are accepted at 1.1-1.3 MB.
#
# THIS ROW IS LOUD BY CONSTRUCTION, AND THAT IS STATED RATHER THAN DISCOVERED.
# The cap site is on the path of EVERY successful compile in the project, so
# an inverted comparison turns essentially every cell in the tree red. What it
# proves is therefore a REACH fact — the site is live on every compile — and
# NOT a coverage discovery. Do not read a wide red row here as evidence that
# the cap is well covered; S191 and S192 are the rows that carry information
# about coverage, and both are answer-identical with green corpus arms.
#
# THE ONE ASYMMETRY WORTH READING OFF THIS ROW. Only `tests/resource/
# run_resource_tests.sh` §1b asserts the cap's TRUE side: three shapes pinned
# with the byte counts they used to emit, each required to draw the "bytes of
# emitted C source" refusal, each required to be RE-ACCEPTED when
# `--max-emit-bytes` is raised past it. Under this plant both cells of all
# three flip — accepted where a refusal is required, then refused where the
# raised override must re-accept — and no other instrument in the tree
# expresses that direction at all. Every other red cell here says only "this
# pattern stopped compiling".
#
# THE TOTAL CAP IS THE ONE INVERTED, AND THE CHOICE IS THE FINDING. The CODE
# cap (`PCREC_MAX_VM_EMIT_CODE_BYTES`, 500,000) has NO natural witness
# anywhere in this repository: §1b's three shapes are all TABLE-dominated
# (their code is tens of KB), so it is the total cap that refuses them, and
# the code cap is reachable only through the lowered-cap reference compiler
# `run_size_term.sh` §5 builds. A second row inverting it would score against
# an empty population, which is the shape this directory refuses to encode.
SAB_ID="S193-sizecap-comparison-inverted"
SAB_FILE="src/core/compile.c"
SAB_SUITES="resource sizeterm harness"
SAB_HARNESS_TARGET="tests/size/size_term.rxt"
SAB_DESC="the total emitted-size cap's refusal comparison is inverted, so every artifact under the megabyte limit is refused as 'too large' and the three oversize shapes tests/resource §1b pins are accepted at 1.1-1.3 MB. The resource arm is the only one in the tree that expresses that DIRECTION; every other red cell says only that a pattern stopped compiling"
SAB_DOC_FIGURE="PLACEHOLDER -- written 2026-08-29 (lane artsize3), CANONICAL RUN OWED (bash tests/mech/run_sabotage_matrix.sh S193). PREDICTED: resource:>=6fail (both cells of all three §1b shapes), sizeterm:many-fail, corpus:all-fail on tests/size/size_term.rxt -- DETECTED loudly, and the row's content is the REACH fact plus §1b's asymmetry, not a coverage discovery. Replace this line with the measured row and the arm figures."
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/big.c" -- "a{0,25000}"'
SAB_REACH_EXPECT="bytes of emitted C source"
SAB_REACH_POP="tests/resource/run_resource_tests.sh|size_moved=|1
tests/resource/run_resource_tests.sh|bytes of emitted C source|1"
SAB_COUNT=1
SAB_BEFORE='        if (emit_tot > cap_tot)'
SAB_AFTER='        if (emit_tot < cap_tot)   /* SABOTAGE S193 */'
