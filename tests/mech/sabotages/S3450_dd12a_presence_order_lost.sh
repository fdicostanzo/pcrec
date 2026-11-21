#!/usr/bin/env bash
# S3450 (lane l3tri, 2026-11-20; span_arms L3) -- DD12a(i)'s PRESENCE ORDER is
# lost: the check no longer compares a run-stating pair's presence members as a
# multiset or removes the statements, so the byte-rate-keyed PRES order (byte:
# the one-byte gate before the run's gate; utf8: the rq_set loop after it)
# reads as an encoding conditional again.
#
# Detector: the region's own floor (PRESENCE_ORDER >= 1, reached by the
# explicit DD12a(ii) witness `(?<=a)(b)\1x`, K -1) and the strict-identity
# comparison on that witness.
SAB_ID="S3450-dd12a-presence-order-lost"
SAB_FILE="tests/codegen/run_encoding_checks.sh"
# RE-AIMED 2026-11-20 (lane l3r65, review r65 A): the explicit witness is `ab(c)\1x` (K 1); after the pick
# rule `(?<=a)(b)\1x` states a run under byte only (`6162` at -1; utf8 none), so it no longer has a run on
# both sides (reason restated 2026-11-21, lane l3r66, review r66 CHECK-2).
SAB_SUITES="encoding"
SAB_DESC='DD12a(i) never takes the presence-order arm, so a run-stating pair whose presence tests differ only in byte-rate-keyed order and form is reported as an encoding conditional in the hot path'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/l3tri_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3450.'
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern '\''ab(c)\1x'\'' && grep -q '\''static const unsigned char rq_set\[\] = { 120 };'\'' "$REACH_TMP/o.c" && grep -q '\''#define RX_REQ_RUN "616263@2"'\'' "$REACH_TMP/o.c" && echo REACH-PRES-ORDER'
SAB_REACH_EXPECT='REACH-PRES-ORDER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                if seqb != sequ:'
SAB_AFTER='                if False and seqb != sequ:  # SABOTAGE S3450'
