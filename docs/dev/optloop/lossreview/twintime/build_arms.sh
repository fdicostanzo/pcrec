#!/bin/bash
# build_arms.sh: build every timing arm of the twintime slot, as the bench
# builds an artifact (gcc -O2 -fPIC -shared; the timing driver fatime links
# the .so).  Env: LR (scratch root), PCREC, BENCHCOPY.  Output tree:
#   $LR/tt/CELL/ARM/pPAD/{rx.c,rx.h,librx.so,fatime}
# ARM  base | base_b (a SECOND compile of today's artifact: the null arm) |
#      twin arms made by vm/twins/twin.py from base's rx.c.
# PAD  a layout control: PAD bytes of `.skip` are put at the very top of
#      rx.c (every function after it moves by PAD), so a delta is read at
#      four code alignments, not one.
set -e
export TMPDIR=${TMPDIR:-$LR/tmp}; mkdir -p "$TMPDIR"
HERE=$(cd "$(dirname "$0")" && pwd)
TW="$HERE/../vm/twins"
: "${LR:?}" "${PCREC:?}" "${BENCHCOPY:?}"
PADS=${PADS:-"0 16 32 48"}
# cell  set/pattern  arm=transform ...
CELLS=(
 "bak2   syntax/bak-2                   seam=static_seam noinline=static_noinline noclone=static_noinline_noclone"
 "bak1   syntax/bak-1                   seam=static_seam"
 "modj   syntax/mod-j-uc                seam=static_seam"
 "phone  capability/phone-palindrome-6  seam=static_seam"
 "bakpy  syntax/bak-py                  seam=static_seam"
 "bakgrel syntax/bak-g-rel              seam=static_seam"
)
for spec in "${CELLS[@]}"; do
  set -- $spec; cell=$1 sp=$2; shift 2
  case " ${ONLY:-$cell} " in *" $cell "*) ;; *) continue ;; esac
  set_=${sp%/*}; pat=${sp#*/}
  P="$(cat "$BENCHCOPY/bench/$set_/patterns/$pat.rx")"
  B=$LR/tt/$cell; rm -rf "$B"; mkdir -p "$B/src/base" "$B/src/base_b"
  "$PCREC" --features all -o "$B/src/base/rx.c" --pattern "$P"
  "$PCREC" --features all -o "$B/src/base_b/rx.c" --pattern "$P"
  for a in "$@"; do
    n=${a%%=*}; tr=${a#*=}; mkdir -p "$B/src/$n"
    cp "$B/src/base/rx.h" "$B/src/$n/rx.h"
    python3 "$TW/twin.py" "$B/src/base/rx.c" "$B/src/$n/rx.c" "$tr"
  done
  for d in "$B"/src/*/; do
    arm=$(basename "$d")
    for pad in $PADS; do
      O=$B/$arm/p$pad; mkdir -p "$O"
      cp "$d/rx.h" "$O/rx.h"
      { [ "$pad" -gt 0 ] && echo "__asm__(\".text\\n.skip $pad, 0x90\\n\");"; cat "$d/rx.c"; } > "$O/rx.c"
      ( cd "$O"
        gcc -O2 -fPIC -shared -o librx.so rx.c
        gcc -O2 -I. -o fatime "$TW/fatime.c" -L. -lrx -Wl,-rpath,"$O" )
    done
  done
  echo "built $cell: $(ls "$B"/src | tr '\n' ' ')"
done
