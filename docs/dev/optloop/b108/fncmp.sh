#!/bin/bash
# b108 reading (lane o64read): per-function identity of two x86_64 gcc-15 -O2 -fPIC
# assemblies of one artifact, default vs -fno-lit-run. Labels (.L*, LFB/LFE, .LC*)
# are normalized so only instruction text is compared. Usage: fncmp.sh DIR NAME...
# expects DIR/NAME.off.s and DIR/NAME.on.s (gcc -O2 -fPIC -S output).
d=$1; shift
fn(){ awk -v f="$2" '$0==f":"{p=1} p{print} p&&/\.size/{exit}' "$1" \
  | grep -v "^\s*\.\(cfi\|loc\)" \
  | sed -E 's/\.L[0-9]+/.LX/g; s/LFB[0-9]+/LFB/; s/LFE[0-9]+/LFE/; s/\.LC[0-9]+/.LC/g; s/rx_targets_[0-9.]+/TGT/g'; }
for n in "$@"; do
  echo "#### $n order off: $(grep -E '^[a-z_]+:$' $d/$n.off.s | grep -v rx_info | tr '\n' ' ')"
  echo "#### $n order on:  $(grep -E '^[a-z_]+:$' $d/$n.on.s | grep -v rx_info | tr '\n' ' ')"
  for f in $(grep -E '^[a-z_]+:$' $d/$n.on.s | tr -d : | grep -v rx_info); do
    a=$(fn $d/$n.off.s $f | cksum); b=$(fn $d/$n.on.s $f | cksum)
    printf '  %-18s off=%4d on=%4d identical=%s\n' $f $(fn $d/$n.off.s $f | wc -l) $(fn $d/$n.on.s $f | wc -l) $([ "$a" = "$b" ] && echo Y || echo N)
  done
done
