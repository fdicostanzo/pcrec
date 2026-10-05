#!/bin/bash
# probe.sh LABEL PATTERN CONFIGBODY BLOCKBODY [-- CLIARGS...]
#
# One cross-source composition cell (option_sets.md §2.5a). Writes a scratch
# .rxt holding `config c` (CONFIGBODY: \n-separated lines) and `target rx = p
# with c` (or a bare `target rx = p` when CONFIGBODY is empty) over the pattern
# block `p` (plus BLOCKBODY lines), compiles it with CLIARGS, and prints the
# exit code, stderr, and the stamps a composition can move.
#
# Env: PCREC (default: this tree's build/pcrec), SCRATCH (REQUIRED: a
# directory inside the lane worktree or session scratchpad; never /tmp).
set -u
here=$(cd "$(dirname "$0")" && pwd)
P=${PCREC:-$here/../../../build/pcrec}
D=${SCRATCH:?set SCRATCH to a scratch directory (never /tmp)}
label=$1; pat=$2; cfg=$3; blk=$4; shift 4; [ "${1:-}" = -- ] && shift
f=$D/$label.rxt
{
  if [ -n "$cfg" ]; then echo "config c"; printf '%b\n' "$cfg" | sed 's/^/  /'
                         echo "target rx = p with c"
  else echo "target rx = p"; fi
  echo; echo "pattern $pat"; echo "name p"
  [ -n "$blk" ] && printf '%b\n' "$blk"
} > "$f"
rm -f "$D/$label.c" "$D/$label.h"
TMPDIR=$D timeout 60 "$P" -o "$D/$label.c" "$@" "$f" > "$D/$label.out" 2> "$D/$label.err"; rc=$?
echo "=== $label  rc=$rc  cli: $*"
[ -n "$cfg" ] && printf '%b\n' "$cfg" | sed 's/^/  cfg| /'
[ -n "$blk" ] && printf '%b\n' "$blk" | sed 's/^/  blk| /'
sed -e "s|$D/||" -e 's/^/  err| /' "$D/$label.err" | head -4
if [ -f "$D/$label.c" ]; then
  grep -hE "#define RX_(TUNE|ENGINE|VM_PREFILTER|DFA_TABLE|UNROLL_K|UTF_CHECK|STARTPOS_GUARD|FINDINGS|STEP_BUDGET|REQ_WHY) |PCREC_FEATURE_MODULES" "$D/$label.c" | sed 's/^/  stamp| /'
  grep -hE "^\s+\.(flags|encoding) =" "$D/$label.c" | sed 's/^ */  info| /'
  echo "  comment-lines| $(grep -c '^ *//\|/\* ' "$D/$label.c")"
fi
