#!/usr/bin/env bash
# S718 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the derived reach one short ([r9 C-1]): every use of R moves together, so the shortest accepted span reads one byte past n. Seen as a FAULT on G2's end guard page (and by ASan's poisoning).
SAB_ID='S718-vrun-reach-short'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the vrun reach R = VW + T is one short, so the vector body reads one byte past n'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S718. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    unsigned vw = lv->vw, tt = vrun_t(x->p), r = vw + tt;'
SAB_AFTER='    unsigned vw = lv->vw, tt = vrun_t(x->p), r = vw + tt - 1;   /* SABOTAGE S718 */'
