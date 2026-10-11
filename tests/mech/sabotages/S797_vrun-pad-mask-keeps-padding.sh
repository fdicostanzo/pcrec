#!/usr/bin/env bash
# S797 ([MEMFN] R-14 follow-up, lane r14p, 2026-10-11) -- the padded verify's mask does not zero the bytes past the run's end: they are compared against the zero padding. G2's SIMD family (answers and its padded-verify rule) and the cli case for (?i)cat.
SAB_ID='S797-vrun-pad-mask-keeps-padding'
SAB_FILE='memfn/src/runcmp.c'
SAB_SUITES='cli g2simd'
SAB_DESC='the padded word masks the bytes past the run with 0xDF, not 0x00: a hit whose next bytes are not 0x00/0x20 is missed'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S797. docs/dev/lanes/r14p_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        k[i] = in ? r->k ? r->k[i] : 0xFF : 0x00;'
SAB_AFTER='        k[i] = in ? r->k ? r->k[i] : 0xFF : i < r->len ? 0x00 : 0xDF;   /* SABOTAGE S797 */'
