#!/bin/bash
# Sourced by chain.sh (copied from worktrees/memfn-slot/b3aheavy, lane b3achain2): score one mech row's log by its DECLARED SAB_EXPECT.
# Matrix semantics (tests/mech/run_sabotage_matrix.sh): the trailer counts "unexpected" for any row whose
# verdict contradicts its declared expectation (lines ~3349-3362: an expected UNDETECTED/UNREACHED row is
# rendered "(EXPECTED ...)" and is NOT unexpected), but the separate undetected/unreached counters still count
# those expected rows (vcount greps the verdict column for UNDETECTED / UNREACHED|NOW REACHED). So:
#   DETECTED (default)      : unexpected 0, undetected 0, unreached 0, anomalies 0
#   UNREACHED               : unexpected 0, undetected 0, unreached 1, anomalies 0
#   UNDETECTED              : unexpected 0, undetected 1, unreached 0, anomalies 0
#   BUILD-REFUSED           : a refused build is scored DETECTED by the matrix (line ~1534): all four counters 0
# $1 = row id (no suffix), $2 = its log, $3 = worktree holding tests/mech/sabotages.
# Prints "OK|BAD <id> expect=<E> :: <trailer>" and returns 0 for OK.
mech_score() {
  local id=$1 lg=$2 wt=$3 f exp tr want_u=0 want_r=0
  f=$(ls "$wt"/tests/mech/sabotages/${id}_*.sh 2>/dev/null | head -1)
  if [ -z "$f" ]; then echo "BAD $id expect=? :: NO SABOTAGE FILE"; return 1; fi
  exp=$(command grep -m1 -E '^SAB_EXPECT=' "$f" | sed -E 's/^SAB_EXPECT=//; s/["'"'"']//g; s/[[:space:]#].*$//')
  [ -z "$exp" ] && exp=DETECTED
  case "$exp" in
    DETECTED|BUILD-REFUSED) ;;
    UNREACHED) want_r=1 ;;
    UNDETECTED) want_u=1 ;;
    *) echo "BAD $id expect=$exp :: UNKNOWN SAB_EXPECT"; return 1 ;;
  esac
  tr=$(command grep -E '^== mech run COMPLETE' "$lg" 2>/dev/null | tail -1)
  if [ -n "$tr" ] && echo "$tr" | command grep -q 'unexpected: 0,' && echo "$tr" | command grep -q "undetected: $want_u," \
     && echo "$tr" | command grep -q "unreached: $want_r," && echo "$tr" | command grep -q 'anomalies: 0[,)]'; then
    echo "OK $id expect=$exp :: $tr"; return 0
  fi
  echo "BAD $id expect=$exp :: ${tr:-NO COMPLETE TRAILER}"; return 1
}
