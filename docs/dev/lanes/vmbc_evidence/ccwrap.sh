#!/bin/bash
# ccwrap.sh ARGS... : gcc, but every generated matcher .c is first rewritten by vmopt (mode $VMOPT_MODE, default BC)
V=/var/tmp/pcrec-pcrec/scratch/vmbc; args=()
for a in "$@"; do
  if [[ "$a" == *.c ]] && [ -f "$a" ] && command grep -q '_match_anchored(const' "$a"; then
    python3 -I $V/tools/vmopt.py -m "${VMOPT_MODE:-BC}" "$a" "$a.vmbc.c" 2>>"${VMOPT_LOG:-$V/vmopt_corpus.log}"
    args+=("$a.vmbc.c")
  else args+=("$a"); fi
done
exec gcc "${args[@]}"
