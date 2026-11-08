#!/bin/bash
# usage: or.sh OPTS PATTERN start:subject ...   (text args; hex-encodes for p2probe)
S=${P2PROBE_DIR:-/var/tmp/pcrec-pcrec/scratch/spanarms2}
h(){ printf '%s' "$1" | od -An -tx1 | tr -d ' \n'; }
o=$1; p=$2; shift 2; a=()
for s in "$@"; do a+=("${s%%:*}:$(h "${s#*:}")"); done
printf '%s\t%s\t' "$p" "$*"; $S/p2probe "${o:--}" "$(h "$p")" "${a[@]}" | tr '\n' ' '; echo
