#!/usr/bin/env bash
# R-4 compile-time witnesses (note §8.7): wall seconds of `pcrec --engine=vm
# -o FILE` under four builds -- denied (PROTO, no arm), rev 2's prototype
# (PROTO2, arms), rev 2.1 with both memos off (PROTO_NOMEMO=1), rev 2.1.
# Families: Bsame n refs to one group; Bdist n groups each referenced once
# (\g{N}, so no reference reads as octal); Bcycle an n-group reference
# cycle; A1alt n `a+` branches then n `(?:\b|)`; A1lb n branches then n
# distinct lookbehind classes.  Env: PROTO, PROTO2, NS, TMPDIR.
AB="PROTO_ARM_A=1 PROTO_ARM_B=1"
T=${TMPDIR:-/tmp}
tm(){ s=$(python3 -c 'import time;print(time.time())'); env $2 ${TIMEOUT:-timeout} 900 $1 -p rx --engine=vm --features all -o $T/q.c --pattern "$3" >/dev/null 2>$T/q.err; rc=$?; python3 -c "import time;print('rc=$rc\t%.2f'%(time.time()-$s))"; }
gen(){ python3 - "$1" "$2" <<'PY'
import sys
w, n = sys.argv[1], int(sys.argv[2])
if w == "Bsame":  print("(a)" + "x+\\1" * n)
if w == "Bdist":  print("".join("(a)x+\\g{%d}" % (i + 1) for i in range(n)))
if w == "Bcycle": print("".join("(a\\g{%d})" % (i + 2) for i in range(n - 1)) + "(a\\g{1})" + "x+\\g{1}")
if w == "A1alt":  print("(?:" + "|".join("a+" for _ in range(n)) + ")" + "(?:\\b|)" * n)
if w == "A1lb":   print("(?:" + "|".join("a+" for _ in range(n)) + ")" + "(?:" + "|".join("(?<=[\\x%02x])" % (0x21 + (i % 90)) for i in range(n)) + "|)")
PY
}
for w in Bsame Bdist Bcycle A1alt A1lb; do for n in ${NS:-1600 6400 12800}; do pat=$(gen $w $n)
  # Linux caps ONE argv string at 128 KiB (MAX_ARG_STRLEN): the exec fails
  # in ~0.02 s and reads as a fast compile.  Skip, loudly.
  if [ ${#pat} -ge 131072 ]; then printf '%s\t%s\tSKIPPED\tpattern %d bytes >= MAX_ARG_STRLEN\n' "$w" "$n" ${#pat}; continue; fi
  for cfg in "$PROTO|" "$PROTO2|$AB" "$PROTO|$AB PROTO_NOMEMO=1" "$PROTO|$AB"; do b=${cfg%%|*}; e=${cfg#*|}
    printf '%s\t%s\t%s\t%s\t%s\n' "$w" "$n" "$([ "$b" = "$PROTO2" ] && echo rev2 || echo rev21)" "${e:-denied}" "$(tm $b "$e" "$pat")"; done; done; done
