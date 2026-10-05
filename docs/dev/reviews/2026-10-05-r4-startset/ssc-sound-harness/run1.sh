#!/bin/bash
# run1.sh PATTERN MODE(byte|utf8|utf8ucp) [pcrec flags...]  ; subjects on stdin
S=${W:?set W to a scratch dir}; HH=/Users/fdicostanzo/pcrec/docs/dev/reviews/2026-10-05-r4-startset/ssc-sound-harness; pat="$1"; mode="$2"; shift 2
case $mode in byte) ef="-e byte";; byteucp) ef="-e byte --ucp";; utf8) ef="-e utf8";; utf8ucp) ef="-e utf8 --ucp";; esac
/Users/fdicostanzo/pcrec/build/pcrec --features all $ef "$@" -p rx -o $S/rx.c --pattern "$pat" || exit 1
grep -h '#define RX_ENGINE \|#define RX_VM_PREFILTER \|#define RX_DFA_PREFILTER \|#define RX_DFA_SCAN ' $S/rx.c | awk '{printf "%s=%s ",$2,$3}'; echo
gcc-16 -O1 -w -I$S -I/opt/homebrew/include -o $S/odrv $HH/odrv.c $S/rx.c -L/opt/homebrew/lib -lpcre2-8 || exit 1
$S/odrv "$pat" $mode
