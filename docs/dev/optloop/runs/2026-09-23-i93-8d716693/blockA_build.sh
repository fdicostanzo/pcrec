#!/bin/bash
set -e
PCREC=/tmp/optloop2/pcrec/build/pcrec
PATTERNS_DIR=/home/duxevents/pcrec-bench/bench/capability/patterns
WORK=/tmp/optloop3/blockA/work
mkdir -p "$WORK"
cp /tmp/optloop3/blockA/findall.c "$WORK/findall.c"

declare -A PAT
PAT[router-prefix-order]="$(cat $PATTERNS_DIR/router-prefix-order.rx)"
PAT[uuid-near-miss]="$(cat $PATTERNS_DIR/uuid-near-miss.rx)"
PAT[ipv4-near-miss]="$(cat $PATTERNS_DIR/ipv4-near-miss.rx)"
PAT[wild-codegrammar-json-array-begin]="$(cat $PATTERNS_DIR/wild-codegrammar-json-array-begin.rx)"

# variant name -> extra pcrec flags
declare -A VARIANT
VARIANT[default]=""
VARIANT[noreqbyte]="-fno-req-byte"
VARIANT[noendwin]="-fno-end-window"
VARIANT[noboth]="-fno-req-byte -fno-end-window"

for pat in "${!PAT[@]}"; do
  text="${PAT[$pat]}"
  extra_flags=""
  if [ "$pat" = "router-prefix-order" ]; then
    extra_flags="--no-captures"
  fi
  for variant in default noreqbyte noendwin noboth; do
    vflags="${VARIANT[$variant]}"
    dir="$WORK/$pat/$variant"
    mkdir -p "$dir"
    artc="$dir/art.c"
    echo "=== $pat / $variant ==="
    "$PCREC" -p rx $extra_flags $vflags -o "$artc" --pattern "$text" 2>"$dir/pcrec.err" \
      && echo "compiled" || { echo "FAILED"; cat "$dir/pcrec.err"; exit 1; }
    binname="$WORK/${pat}__${variant}"
    gcc -O2 -I"$dir" -o "$binname" "$WORK/findall.c" "$artc" 2>"$dir/gcc.err" \
      && echo "linked -> $binname" || { echo "GCC FAILED"; cat "$dir/gcc.err"; exit 1; }
  done
done
echo "ALL BUILT"
