# S191 (S-ARTSIZE1) — [ART-SIZE] THE LADDER REDUCED TO A GREEDY DESCENT, AND
# EVERY ANSWER IN THE TREE STAYS RIGHT. THE DETECTION IS A SIZE ASSERTION,
# BECAUSE ANSWER IDENTITY HOLDS BY CONSTRUCTION.
#
# `K` is the counter rung's chunking factor and nothing else: an artifact
# built at K=1 and one built at K=8 accept exactly the same language, report
# exactly the same span, and fill exactly the same capture slots. That is the
# premise the whole size term rests on (docs/design/artifact_size_term.md
# §3.2, and `make test-ksweep` is the standing census of it), and it is also
# what makes this row unreachable from every answer-checking instrument in
# the repository. A compiler that picks the WRONG K is a compiler that emits
# a larger artifact and answers every subject correctly. No `.rxt` cell, no
# oracle, no differential, no identity gate can be red for it. Only an
# assertion about the SIZE — here, about the K the artifact was built at —
# can, which is why `tests/codegen/run_size_term.sh` §3 exists and why this
# row is the one §11.3 of the note calls "the one that matters".
#
# WHAT THE EDIT DOES. `size_term_choose`'s selection is an EXHAUSTIVE
# `argmin` over the rungs' node counts (§3.3: exact, no model in it). This
# plant stops the scan at the first rung that improves on the default —
# a greedy descent, the most natural way to write the loop if you assume the
# node count falls monotonically in K. It does not: §3.1's own K-sweep table
# has interior optima, and `make test-ksweep`'s report names three corpus
# patterns whose argmin is K=2 rather than an endpoint. The ladder is
# [6,4,3,2,1], so a greedy scan takes K=6 — the first rung it sees — and the
# artifact keeps the bytes the argmin would have removed.
#
# THE DETECTOR is `run_size_term.sh` §3's last cell: the nested-N=8 subject
# is pinned at the K the term chooses for it (1), read off the artifact
# rather than off the stamp alone. §2's `size-model` cell fires too when the
# materiality bar declines the greedy K, since the verdict string then reads
# `size-model-declined`; both directions are detection and neither is
# required for the row to score.
#
# THE GREEN ARMS ARE THE POINT OF THE ROW, not a half-detection.
# `tests/size/size_term.rxt` is expected to pass every cell under this plant
# — including the block whose header says the answers "must not move ... at
# every K", which is precisely the property the plant does not break.
SAB_ID="S191-sizeterm-greedy-descent"
SAB_FILE="src/core/compile.c"
SAB_SUITES="sizeterm harness"
SAB_HARNESS_TARGET="tests/size/size_term.rxt"
SAB_DESC="the size term's argmin over the ladder becomes a greedy descent that stops at the first improving rung, so a pattern with an interior optimum is built at K=6 instead of its argmin and ships the bytes the term exists to remove. Answer-identical by construction: K is the counter rung's chunking factor, so no oracle, differential or identity gate in the tree can be red for it"
SAB_DOC_FIGURE="CANONICAL RUN 2026-08-29 (run_sabotage_matrix.sh S191 at 48e9a90): sizeterm:1fail/21pass, corpus:0fail/21pass, reach:ok(2/2), pop tests/codegen/run_size_term.sh:/^NEST8=/=1 -- DETECTED. The one red cell is run_size_term.sh section 3's last: 'the size term chose a K the artifact does not carry: 4' (required 1). THE GREEN CORPUS ARM IS THE POINT OF THE ROW, not a half-detection: tests/size/size_term.rxt passes 21/21 under the plant, including the block whose header says the answers must not move at any K. NOTE THE MEASURED K: the greedy scan stops at 4, not at the ladder's first rung 6 -- K=6 does not beat the default, so the plant lands on a rung two steps in. That is the non-monotone curve of section 3.1 showing up inside the sabotage itself, and it is why an exhaustive argmin is the rule."
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/n8.c" -- "((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}" && grep -h _UNROLL_K "$REACH_TMP/n8.c"'
SAB_REACH_EXPECT="#define RX_UNROLL_K 1
#define RX_UNROLL_K_WHY \"size-model\""
SAB_REACH_POP="tests/codegen/run_size_term.sh|^NEST8=|1"
SAB_COUNT=1
SAB_BEFORE='    int best = 0;
    for (int i = 1; i < n; i++)
        if (ok[i] && (nodes[i] < nodes[best] ||
                      (nodes[i] == nodes[best] && k[i] > k[best])))
            best = i;'
SAB_AFTER='    int best = 0;
    for (int i = 1; i < n; i++)
        if (ok[i] && (nodes[i] < nodes[best] ||
                      (nodes[i] == nodes[best] && k[i] > k[best])))
            { best = i; break; }   /* SABOTAGE S191 */'
