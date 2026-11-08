#!/bin/bash
# usage: probe.sh ENC < patterns ; prints pattern | req_whole_run | req_run | req_pieces | span_facts | kset_walk
P=${PCREC:-build/pcrec}
enc=${1:-byte}
while IFS= read -r pat; do
  [ -z "$pat" ] && continue
  out=$(timeout 20 $P --features all -e $enc --emit-facts --pattern "$pat" 2>&1)
  if ! grep -q '^#section facts' <<<"$out"; then printf '%s\tERR %s\n' "$pat" "$(head -1 <<<"$out")"; continue; fi
  g(){ awk -F'\t' -v f="$1" '$2==f{print $7; exit}' <<<"$out"; }
  printf '%s\twhole=%s\trun=%s\tpieces=%s\tspan=%s\tkset=%s\tengine=%s\n' "$pat" "$(g req_whole_run)" "$(g req_run)" "$(g req_pieces)" "$(g span_facts)" "$(g kset_walk)" "$(awk -F'\t' '$2=="RX_ENGINE"{print $3}' <<<"$out")"
done
