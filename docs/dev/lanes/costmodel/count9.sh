#!/usr/bin/env bash
# costmodel: rebuild data/counts9.txt — lane r17loss's no-clock counting pass
# (count_instrument.py + count_cnt.c, copied verbatim from lane/r17loss
# docs/dev/lanes/r17loss/{instrument.py,cnt.c}) run over all NINE subjects
# (slot25c's five + the spike's four real-text ones) instead of five.
# usage: count9.sh SLOT25C_ALPHA_DIR SPIKE_SUBJ_DIR SCRATCH_DIR > counts9.txt
# One gcc -O2 per cell into SCRATCH_DIR (never /tmp); no timing.
set -euo pipefail
A=$1; SUBJ=$2; X=$3; HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$X"
for c in dig email word-eq hex-run bounded dfa-hat vm-hat vm-hat-1; do
    python3 -I "$HERE/count_instrument.py" "$A/art/$c/off/new/art.c" "$X/$c.c"
    TMPDIR="$X" gcc -O2 -I"$A/art/$c/off/new" -o "$X/$c.bin" "$HERE/count_cnt.c" "$X/$c.c"
done
for c in dig email word-eq hex-run bounded dfa-hat vm-hat vm-hat-1; do
    for s in short prose64k digits64k prose1m mix64k docs64k docs1m code64k code1m; do
        f="$SUBJ/$s"; [ "$s" = short ] && f="$A/subj/short"
        for m in first all; do echo "$c $s $m $("$X/$c.bin" "$f" "$m")"; done
    done
done
