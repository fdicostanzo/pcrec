# S1302 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: a setter on a BOUND iterator is silently ignored instead of making the next call refuse.
# Detector: the poison arm (a setter after the first call must end the iterator with PCREC_ERR_ITER).
SAB_ID="S1302-setter-on-bound-no-poison"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='a setter on a BOUND iterator is silently ignored instead of making the next call refuse'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1302.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "         else if ((it_)->hdr != PCREC_ITER_ENDED) (it_)->hdr = 0; } while (0)\n"'
SAB_AFTER='        "         } while (0)   /* SABOTAGE S1302 */\n"'
