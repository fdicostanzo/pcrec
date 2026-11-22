#!/usr/bin/env bash
# S3526 ([MEMFN] R-47 unit U4, lane bsu4g, 2026-11-22) -- plant (b) of docs/design/memfn/block_span.md §10.2's sabotage table (job 708's `past`): the vector span's final block starts one byte later, so it reads S[C + LO + K], one byte past the stretch. Caught by G2-V whole's END guard page on a WALK whose stretch ends at the pattern end ([0-9]{25}, R7w, k 24: a match flush against the subject's end puts that byte on the PROT_NONE page; on D-hors the byte past the stretch is the probe, in bounds, so the OVER-READ is harmless there). The plant is also an ANSWER bug wherever K % B == 0 (the shifted final block leaves byte K - B of the stretch untested: `[0-9a-f]{17}` on `Z0000000000000000` reads `match 0 17`, libpcre2 none), so G2-V whole reds on HORS answers too, and G2-V unit reds by its kit_tail text pin (it reads the shifted `p + (K - B + 1)` as a disagreement and drives no window), not by its high guard. The row is therefore an answer-and-guard plant, not a guard-only witness; the guard pages' own proof is G2-V's start-up self-witness (GUARD-LOW-LIVE / GUARD-HIGH-LIVE, r78 G2V-1, PLANTSB-2).
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
