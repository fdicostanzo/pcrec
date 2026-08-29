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
SAB_DOC_FIGURE="CANONICAL RUN 2026-08-29 (run_sabotage_matrix.sh S193 at 48e9a90): resource:7fail/19pass, sizeterm:17fail/3pass, corpus:21fail/0pass, reach:ok(1/1), both pops =1 -- DETECTED, and LOUD BY CONSTRUCTION as this header says. The resource arm is the one to read: all SIX section-1b cells flip in both directions -- the three shapes are ACCEPTED where a refusal is required (a{0,25000} at 1,103,367 B, [a-z]{0,30000} at 1,323,371 B, (a|b){0,30000} at 1,333,109 B), and each is then REFUSED at --max-emit-bytes=9000000 where the raised override must re-accept it, because under the inversion a larger limit refuses more. The seventh red is section 1s own a{65535} auto cell (SEL-1s fallback), refused at 18,155 bytes against a 1,000,000 limit -- the same inversion seen from the small side. Nothing else in the tree expresses that DIRECTION: the 21 red corpus cells and the 17 red sizeterm cells all say only that a pattern stopped compiling."
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/big.c" -- "a{0,25000}"'
SAB_REACH_EXPECT="bytes of emitted C source"
SAB_REACH_POP="tests/resource/run_resource_tests.sh|size_moved=|1
tests/resource/run_resource_tests.sh|bytes of emitted C source|1"
SAB_COUNT=1
SAB_BEFORE='        if (emit_tot > cap_tot)'
SAB_AFTER='        if (emit_tot < cap_tot)   /* SABOTAGE S193 */'
