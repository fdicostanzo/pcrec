#!/usr/bin/env bash
# S461 ([K82], lane k82fix) -- PICK'S NONE ANSWER IGNORES THE CANDIDATES' SIZES.
#
# [K82] (C): under NONE the PICK primitive prices a candidate by MASS's own
# NONE answer, its member count, so a run scans an exact position before a
# two-member pair. This plant prices every cube as one member, which is the
# abi-59 answer ("rightmost, whatever the candidates' sizes"): alt-shared
# (`日本|日曜|日付`, -e utf8) scans the UTF-8 lead-byte pair {E4, E6} again.
# Answer-invisible (every run position is necessary). Detector:
# run_prechecks.sh §5.11's (C) rows (REQ_RUN @3 / @5 where @2 / @0).
#
# [k382mech, 2026-11-12, R-38 K38-2] RE-AIMED: the detector and the probe.
# Since K38-2 `REQ_RUN`'s `@` is the kit's search position, so the (C) REQ_RUN
# rows no longer read PICK (mech 607 shard 1: 0 failed / 395 passed,
# UNEXPECTED). PICK's surviving reader is the `req_byte` fact
# (src/facts/req.c `pcrec_req_pick`: the run's picked position where exact,
# else the set's pick). `x(?i:elect)\d+z` -e utf8: NONE picks the one exact
# position x (REQ_BYTE 120); the plant prices the five pairs as one member,
# picks the rightmost pair, and REQ_BYTE falls to the set's rightmost z (122).
# Measured on a scratch build with the plant (findings.o relinked): 120 clean,
# 122 planted. Detector: run_prechecks.sh §5.11's (C) REQ_BYTE row
# (`[5.11c]`), added for this row.
#
# [s2tri h4, 2026-11-13] RE-AIMED + RE-ANCHORED (lane s2tri, [RUN-POS-SET]
# flip 2 -> 128). Two moves, one cause. (1) The probe's witness
# `x(?i:elect)\d+z` now carries `\d` as the run position [30-39], so its
# RX_REQ_RUN is the set spelling `78[4565][4c6c][4565][4363][5474][30-39]@0`
# and the cube-form grep read UNREACHED; the detector [5.11c] was already
# re-aimed to `x(?i:elect).+z` (3d70b9997), whose run keeps the cube form,
# so the probe now reads that witness (tip: RX_REQ_BYTE "120", RX_REQ_RUN
# "78454c454354@0/ffdfdfdfdfdf"). (2) The OLD plant (`cube_mass`'s NONE
# answer) became an equivalent mutant: since rps3 the run scan index asks
# `pcrec_find_pos_pick` / `pcrec_find_pos_mass` (one member SET per
# position), and every remaining `pcrec_find_pick` caller passes care = NULL,
# so `cube_mass` only ever prices one-byte cubes, where 1 << popcount(0) == 1
# makes the plant a no-op. PICK's NONE cardinality answer now lives in
# `pcrec_find_pos_mass`, so the anchor moves there (same fault: every
# position priced as one member). Measured on scratch builds (findings.o
# relinked into a copy of libpcrec.a), witness `x(?i:elect).+z` -e utf8:
# clean 120; old plant 120 (invisible); new plant 122 (the [5.11c] red).
SAB_ID="S461-pick-none-ignores-size"
SAB_FILE="src/core/findings.c"
SAB_SUITES="prechecks"
SAB_DESC="the PICK primitive's NONE answer prices every run position (a member set) as one member, so pcrec's own pick over a NONE run takes its rightmost position even where it is a two-member pair beside an exact byte (the abi-59 answer, K82 cause C), and REQ_BYTE falls to the set's pick"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S461."
SAB_REACH='"$PCREC" --features all --memfn=no-window-search -fno-landmark-walk -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern "x(?i:elect).+z" && grep -q "^#define RX_REQ_BYTE \"120\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_RUN \"78454c454354@0/ffdfdfdfdfdf\"" "$REACH_TMP/o.c" && echo REACH-PICK-NONE-MASS'
SAB_REACH_EXPECT="REACH-PICK-NONE-MASS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return rate ? (uint32_t)m : uniform_mass(k);'
SAB_AFTER='    return rate ? (uint32_t)m : uniform_mass(1);   /* SABOTAGE S461 */'
