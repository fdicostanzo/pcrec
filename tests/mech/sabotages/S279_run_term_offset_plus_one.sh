# S279 — [OPT-LITSCAN] S1 THE RUN TERM IS COMPARED ONE BYTE LATE
# (src/gen/emit_dfa.c, `ofsk_emit_verify`): the run-pinned rows' P4 compare
# reads the run at `cand + run_o + 1` instead of `cand + run_o`, so every
# candidate whose run sits at its proved pin fails the verify and the skip
# walks past every real match. litscan_s1.md §7.1 row (a).
#
# ANSWER-DETECTABLE: the run rows are the prefilter, so a refused true start
# is a lost match on every run-pinned artifact. tests/offsetskip/
# run_pinned.rxt is the corpus detector; tests/codegen/run_offset_skip.sh §2
# is the structural one, naming the compare's offset verbatim.
SAB_ID="S279-run-term-offset-plus-one"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness offsetskip"
SAB_HARNESS_TARGET="tests/offsetskip/run_pinned.rxt"
SAB_DESC="the run-pinned prefilter rows compare the pinned run one byte past its proved offset (cand + run_o + 1), so the candidate test refuses every real match start and the skip returns n: every m cell of every run-pinned artifact reads nomatch"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (lane s1build, single-row mech): DETECTED -- reach:ok(1/1), corpus:27fail/28pass (tests/offsetskip/run_pinned.rxt, before the C0 block was added), offsetskip:3fail/25pass (run_offset_skip.sh §2 names the router/foo-b/ab-user run terms missing). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S279."
# [MECH-REACH] the router takes a run row and emits the P4 run term at cand.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "/user|/users" && grep -q "^#define RX_DFA_PREFILTER \"run-pinned\"" "$REACH_TMP/o.c" && grep -qF "!memcmp(subject + cand, \"/user\", 5)" "$REACH_TMP/o.c" && echo REACH-RUN-TERM-EMITTED'
SAB_REACH_EXPECT="REACH-RUN-TERM-EMITTED"
# [OPT-LITSCAN] S1 step 6 re-anchor (lane s1step6, 2026-09-26): the verify
# chain lost its `DfaForm` (litscan_s1.md §1.3's narrowing), so `f->cx` reads
# `cx`; plant and intent unchanged. The run pre-check's `rx_reqrun` blocks
# are now written by this same chain (their run term is at offset 0), so the
# plant ALSO shifts every run pre-check's compare one byte late, turning each
# into a false NOMATCH: the row deletes more and isolates the same site.
SAB_COUNT=1
SAB_BEFORE='            emit_exact_compare(c, t->run_o == 0
                                  ? "subject + cand"
                                  : dfa_fragf(cx, "subject + cand + %d", t->run_o),'
SAB_AFTER='            emit_exact_compare(c, dfa_fragf(cx, "subject + cand + %d", t->run_o + 1),   /* SABOTAGE S279 */'
