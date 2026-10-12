#!/bin/bash
# t5_build.sh: T5's artifacts.  For every utf8 bench pattern (76) compile TODAY
# (arm `base`) and the SCRATCH D160 prior in the `fo` shape (arm `fo20`:
# `--analysis fo20 -I $LR/prior`, gen_d160f.py mode o, 20% non-ASCII mass) as
# the bench's pcrec-auto-caps testee does (misc/mk.py), prefix rx, at PADS
# layouts, linked with the multi-subject timing driver.  Prints MOVERS: the
# patterns whose emitted C differs between the arms (everything else is the
# same artifact and is not timed).  Env: LR PCREC BENCHCOPY, JOBS.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
MISC=$HERE/../misc
: "${LR:?}" "${PCREC:?}" "${BENCHCOPY:?}"
export TMPDIR=${TMPDIR:-$LR/tmp}; mkdir -p "$TMPDIR"
PADS=${PADS:-"0 16 32 48"}; JOBS=${JOBS:-8}
ROOT=$(cd "$HERE/../../../../.." && pwd)
P=$LR/prior; mkdir -p "$P"
python3 -I "$MISC/gen_d160f.py" "$ROOT/src/findings/default.rxt" "$P" fo20 o 20
T=$LR/t5; rm -rf "$T"; mkdir -p "$T"
gcc -O2 -shared -fPIC -o "$LR/memcount.so" "$HERE/memcount.c" -ldl
one() {
  pat=$1
  for arm in base base_b fo20; do
    D=$T/$pat/$arm; mkdir -p "$D"
    extra=""; [ $arm = fo20 ] && extra="--analysis fo20 -I $P"
    python3 -I "$MISC/mk.py" "$PCREC" "$BENCHCOPY" utf8 "$pat" "$D" -- $extra >/dev/null 2>"$D/mk.err" || { echo "BUILDFAIL $pat $arm"; return; }
  done
  # the arms differ only if the emitted C does (stamps naming the analysis are part of that)
  if cmp -s "$T/$pat/base/rx.c" "$T/$pat/fo20/rx.c"; then echo "SAME $pat"; else echo "MOVER $pat"; fi
  for arm in base base_b fo20; do for pad in $PADS; do
    O=$T/$pat/$arm/p$pad; mkdir -p "$O"; cp "$T/$pat/$arm/rx.h" "$O/rx.h"
    { [ "$pad" -gt 0 ] && echo "__asm__(\".text\\n.skip $pad, 0x90\\n\");"; cat "$T/$pat/$arm/rx.c"; } > "$O/rx.c"
    ( cd "$O" && gcc -O2 -fPIC -shared -o librx.so rx.c && gcc -O2 -I. -o fatime "$HERE/../vm/twins/fatime.c" -L. -lrx -Wl,-rpath,"$O" )
  done; done
}
export -f one; export T P MISC PCREC BENCHCOPY HERE PADS TMPDIR
ls "$BENCHCOPY/bench/utf8/patterns/" | sed 's/\.rx$//' | xargs -P "$JOBS" -I{} bash -c 'one {}' | sort > "$T/status.txt"
grep -c MOVER "$T/status.txt" | sed 's/^/MOVERS /'; grep -c SAME "$T/status.txt" | sed 's/^/SAME /'; grep BUILDFAIL "$T/status.txt" || true
