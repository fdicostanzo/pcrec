#!/usr/bin/env bash
# S3526 ([MEMFN] R-47 unit U4, lane bsu4g, 2026-11-22) -- plant (b) of docs/design/memfn/block_span.md §10.2's sabotage table (job 708's `past`): the vector span's final block starts one byte later, so it reads S[C + LO + K], one byte past the stretch. Caught by G2-V whole's END guard page on a WALK whose stretch ends at the pattern end ([0-9]{25}, R7w, k 24: a match flush against the subject's end puts that byte on the PROT_NONE page; on D-hors the byte past the stretch is the probe, in bounds, so the plant is benign there), and by G2-V unit's high guard on every rendering (its window is exactly the stretch).
SAB_ID='S3526-vspan-final-block-reads-past'
SAB_FILE='memfn/src/window.c'
SAB_SUITES='g2v'
SAB_DESC='the vector span final block reads one byte past the stretch'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3526. docs/dev/lanes/bsu4g_report.md carries the lane run.'
# REACH: the design's witness, a WALK whose stretch ends at the pattern end (k 24, B 16); its
# final block's line as the clean tree writes it.
SAB_REACH='"$PCREC" --features all -fmemfn-simd=x86-64-v3 -p rx -o - --pattern "[0-9]{25}"'
SAB_REACH_EXPECT='    return rx_mf1_vs0__w32_b(p + (24 - 16));'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kit_out(o, "    return %s(p + (%u - %u));\n}\n\n", blk, k, b);'
SAB_AFTER='    kit_out(o, "    return %s(p + (%u - %u + 1));\n}\n\n", blk, k, b);   /* SABOTAGE S3526 */'
