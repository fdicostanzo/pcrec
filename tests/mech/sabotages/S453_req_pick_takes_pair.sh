#!/usr/bin/env bash
# S453 ([OPT-LITSCAN] S4 C3, lane c3build) -- REQ_BYTE NAMES A PAIR POSITION'S T.
#
# `<PREFIX>_REQ_BYTE` is the run's scan member only where that member is an
# exact byte; at a pair position T is not a byte every match must contain, so
# the stamp is the set's pick. This plant returns `bytes[idx]` whenever a run
# shipped. ANSWER-PRESERVING (no answer reads REQ_BYTE on a run route): the
# detector is reqcube_check.py's "REQ_BYTE is a req_set member" check, and
# `(?i:select)\d+x` must read 120. (Design's provisional S452.)
# RE-ANCHORED 2026-11-11 (lane k382, R-38 K38-2; span_runs_sheet.md §5's K38-2 row): the shipped run is the
# whole run, uncut (`whole`/`whole_mask`); the same mask test is dropped (intent unchanged).
# RE-ANCHORED 2026-11-11 (lane k382fix, review r1 k382 F5/F10): `ReqRun.idx`/`len` retired, the pick
# computes its index in place; the same mask test is dropped (intent unchanged).
SAB_ID="S453-req-pick-takes-pair"
SAB_FILE="src/facts/req.c"
SAB_SUITES="codegen"
SAB_DESC="the req_byte fact returns the run's scan member whenever a run shipped, including a pair position's T, so REQ_BYTE names a byte that is not in the necessary set"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S453."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?i:select)\\d+x" && grep -q "^#define RX_REQ_BYTE \"120\"" "$REACH_TMP/o.c" && echo REACH-PAIR-PICK'
SAB_REACH_EXPECT="REACH-PAIR-PICK"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (run->whole_mask[idx] == 0xFF) return run->whole[idx];'
SAB_AFTER='        return run->whole[idx];   /* SABOTAGE S453 */'
