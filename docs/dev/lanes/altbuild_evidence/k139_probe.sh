#!/usr/bin/env bash
# probe.sh BIN OUT: accept/refuse with and without the island over three families
BIN=$1; OUT=$2; S=$(dirname "$0"); : > "$OUT"
cb() { gnutimeout 300 "$BIN" -p rx --engine=vm "$@" --warn-emit-bytes=1 -o $S/p.c 2>&1 >/dev/null | sed -n 's/.*: \([0-9]*\) bytes of emitted code.*/R\1/p; s/.*(\([0-9]*\) of code).*/A\1/p' | head -1; }
for spec in "ladder 200 240 260 280 300 320 340 360 400" "dense 600 800 1000 1200 1400 1600 1800 2000 2400 2800" "rand 400 600 800 1000 1200 1400 1600 2000 2400"; do
  set -- $spec; fam=$1; shift
  for n in "$@"; do p=$(python3 -I $S/fam.py $fam $n)
    for fl in "" "-fno-altcls-factor -fno-altcls-merge"; do
      on=$(cb $fl --pattern "$p"); off=$(cb $fl -fno-alt-island --pattern "$p")
      printf '%s\t%s\t%s\t%s\t%s\n' $fam $n "${fl:-default}" "$on" "$off" >> "$OUT"
    done; done; done
