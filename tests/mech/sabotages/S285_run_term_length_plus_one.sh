# S285 — [OPT-LITSCAN] S1 THE RUN TERM IS COMPARED ONE BYTE LONGER THAN PROVED
# (src/gen/emit_dfa.c, `ofsk_emit_verify`): the run-pinned rows' P4 compare
# reads `t->run_len + 1` bytes instead of `t->run_len`, so the emitted
# `memchr`/compare tests one byte past the window `PrefixKSets.run_pinned`
# actually proved is fixed. litscan_s1.md §7.1 row (b), the emitter-level
# mirror of S268 (`src/opt/reqbyte.c`'s analysis-level "claims a longer run
# than proven").
#
# THE EXTRA BYTE IS A REAL COMPILER READ, NOT AN OVERFLOW: `ReqRun.bytes` is
# a fixed `PCREC_MAX_REQ_RUN_EMIT`-byte array and `run_len` (5 for router's
# `/user`) sits well inside it, so `run_bytes[run_len]` is an in-bounds read
# of a byte the analysis never wrote — the arena's zero. The emitted compare
# therefore demands a literal NUL immediately after the pinned run, which no
# real match has, so the artifact refuses every candidate. ANSWER-DETECTABLE
# (lost matches on every run-pinned artifact), and — unlike row (a)'s offset
# plant or row (d)'s width plant — it never touches `OfsTest.maxk`, so it is
# invisible to ASan.
SAB_ID="S285-run-term-length-plus-one"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness offsetskip"
SAB_HARNESS_TARGET="tests/offsetskip/run_pinned.rxt"
SAB_DESC="the run-pinned prefilter rows' P4 compare tests t->run_len + 1 bytes instead of t->run_len, so the candidate test demands an extra byte (the analysis's own unwritten zero) beyond the proved run and refuses every real match start: every m cell of every run-pinned artifact reads nomatch"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S285."
# [MECH-REACH] the router takes a run row and emits the P4 run term at cand,
# comparing exactly run_len (5) bytes on the clean tree.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "/user|/users" && grep -q "^#define RX_DFA_PREFILTER \"run-pinned\"" "$REACH_TMP/o.c" && grep -qF "!memcmp(subject + cand, \"/user\", 5)" "$REACH_TMP/o.c" && echo REACH-RUN-TERM-EMITTED'
SAB_REACH_EXPECT="REACH-RUN-TERM-EMITTED"
SAB_COUNT=1
SAB_BEFORE='                               t->run_bytes, t->run_len);'
SAB_AFTER='                               t->run_bytes, t->run_len + 1);   /* SABOTAGE S285 */'
