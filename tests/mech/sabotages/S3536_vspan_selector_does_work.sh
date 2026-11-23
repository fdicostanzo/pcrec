#!/usr/bin/env bash
# S3536 -- C18 control (4) (block_span.md §10.2, R-47 unit U4): the vector span's selector does work (its one call line gains a comparison). Answer-identical. Rejected by the routing leg (C18 (d), tests/memfn/routing_shape.py): a selector's whole body is one call forwarding its parameters.
SAB_ID='S3536-vspan-selector-does-work'
SAB_FILE='memfn/src/window.c'
SAB_SUITES='simdfloor'
SAB_DESC='the vector span'\''s selector body is a call plus a comparison, so the routing leg must red'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3536. docs/dev/lanes/bsu4p_report.md carries the lane run.'
SAB_REACH='"$PCREC" --features all -fmemfn-simd=x86-64-v3 -p rx -o - --pattern "[0-9a-f]{17}"'
SAB_REACH_EXPECT='    return rx_mf1_vs0__w32(rx_mf1_s, rx_mf1_c);'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kit_out(o, "    return %s(%s, %s);\n", callee, rc->S, rc->C);'
SAB_AFTER='    kit_out(o, "    return %s(%s, %s) != 0;\n", callee, rc->S, rc->C);   /* SABOTAGE S3536 */'
