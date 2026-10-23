# S283 — [OPT-LITSCAN] S1 THE TWO-BIT DENY'S SECOND HALF DROPPED
# (src/gen/emit_dfa.c, `dfa_pfs[]`, `cand_rows[]` since [START-TABLE] C3): the run rows carry
# `PCREC_NO_RUN_PREFILTER` alone, so `-fno-offset-skip` no longer removes
# them and stops keeping lib/pcrec.h's promise of the pre-[OPT-K] artifact.
# litscan_s1.md §7.1 row (k), R3-8.
#
# INVISIBLE TO `make test-axes`: every axis still denies the rows through the
# surviving bit's own flag, answers are identical, and the sweep never asks
# WHICH bit did it. The detector is the one structural row that does.
# FLIPPED TO UNDETECTED (EXPECTED) 2026-10-23 (lane s3fix600; job 600's re-aim
# run). The run rows' mask bit is no longer the only thing -fno-offset-skip
# removes them by: since D172 S2 (NEXT reads the window family's reply)
# `pf_window_of` states no run R under PCREC_NO_OFFSET_SKIP, so no reply
# carries C-pin and no run row applies, whatever its mask says. The plant
# therefore moves no artifact. MEASURED by a scratch build of this exact plant
# on c3ea619c3 (before S3) AND on the S3 tree: `/user|/users` under
# `-fno-offset-skip -fno-req-handoff` (plus --memfn=no-wf-find on S3) stays
# "memchr", byte-identical to the clean build; single-row mech on the S3 tree:
# prechecks 0fail/395pass. The bit stays (defence in depth for a future NEXT
# that reads no reply); the row records that the reply now guards it.
SAB_ID="S283-run-rows-offset-skip-bit-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_EXPECT=UNDETECTED
SAB_DESC="the run-pinned rows lose PCREC_NO_OFFSET_SKIP from their deny mask, so -fno-offset-skip leaves router on run-pinned (the offset-skip block still emitted) instead of the pre-[OPT-K] memchr artifact"
SAB_DOC_FIGURE="MEASURED 2026-10-23 (lane s3fix600, single-row mech on the S3 tree): UNDETECTED -- reach:ok(1/1), prechecks:0fail/395pass; the plant moves no artifact at c3ea619c3 either (a scratch build). What would close it: a NEXT that again reads the row mask alone. Before D172 S2: MEASURED 2026-09-25 (lane s1build, single-row mech): DETECTED -- reach:ok(1/1), prechecks:20fail/269pass (§5.10 row k, plus every §3.4b/§4.x arm that reads the run check under -fno-offset-skip). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S283."
# RE-AIMED 2026-10-11 (lane rlhbuild, [REQ-HANDOFF-L1]): as S282, the deny
# probe adds `-fno-req-handoff` (the re-entry outranks memchr otherwise).
# RE-AIMED 2026-10-23 (lane s3fix600, D172 S3 job 600): the witness is a fixed-width
# window, a `cover` artifact by default (no scan, so not this site); the probe's
# compiles take the cover row's deny --memfn=no-wf-find, the build before S3.
SAB_REACH='"$PCREC" --memfn=no-wf-find --features all -p rx -fno-offset-skip -fno-req-handoff -o "$REACH_TMP/o.c" --pattern "/user|/users" && grep -q "^#define RX_DFA_PREFILTER \"memchr\"" "$REACH_TMP/o.c" && "$PCREC" --memfn=no-wf-find --features all -p rx -o "$REACH_TMP/p.c" --pattern "/user|/users" && grep -q "^#define RX_DFA_PREFILTER \"run-pinned\"" "$REACH_TMP/p.c" && echo REACH-OFFSET-SKIP-DENIES-RUN-ROWS'
SAB_REACH_EXPECT="REACH-OFFSET-SKIP-DENIES-RUN-ROWS"
# RE-AIMED 2026-10-07 (lane stc3, [START-TABLE] C3, start_table.md §3.5):
# `dfa_pfs[]` is deleted into `cand_rows[]`, whose two run rows break the
# line after the deny mask (stc2's S283 collision guard), so the anchor spans
# the break. Intent re-verified: the plant still drops PCREC_NO_OFFSET_SKIP
# from both run rows' deny and nothing else (count 2).
SAB_COUNT=2
SAB_BEFORE='PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER,
             pf_run'
SAB_AFTER='PCREC_NO_RUN_PREFILTER /* SABOTAGE S283 */,
             pf_run'
