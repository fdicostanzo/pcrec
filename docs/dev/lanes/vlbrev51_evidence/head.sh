#!/bin/bash
# vlbrev51: pcrec HEAD verdict per pattern (one line each). $1 = pcrec binary, $2 = patterns file.
P=$1; out=$(mktemp -p /var/tmp/pcrec-pcrec/scratch/vlbrev51)
while IFS= read -r pat; do
  [ -z "$pat" ] && continue
  r=$(timeout 20 "$P" --features all -p rx -o "$out" --pattern "$pat" 2>&1 >/dev/null); rc=$?
  if [ $rc -eq 0 ]; then lb=$(grep -o 'rx_VALID_LB[^0-9]*[0-9]*' "$out" | head -1); echo "$pat	COMPILES $lb"
  else echo "$pat	REFUSED rc=$rc: $(echo "$r" | head -1)"; fi
done < "$2"
rm -f "$out"
