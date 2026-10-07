#!/usr/bin/env bash
# C-1's constructed route-flip witnesses: a VM-forced possessive/atomic
# pattern whose free discharge (src/opt/atomic.c, pcrec_poss_survey) the arms
# make positive, so the DEFAULT route moves vm -> dfa, and `--engine=dfa`
# moves refused -> compiled.  PROTO = the rev-2 prototype binary.
# Usage: PROTO=... routeflip_witness.sh   (prints one row per pattern x arms)
P="${PROTO:?}"; T=$(mktemp -d "${TMPDIR:-/tmp}/rflip.XXXXXX"); trap 'rm -rf "$T"' EXIT
printf 'pattern\tarms\tdefault\tengine_dfa\n'
for pat in '\w++\b' '(?>\w+)\b' 'x(?>\w+)\b' '\d++(?![\d.])' '[a-z]++(?=@)' '(?>[a-z]+)(?=@)'; do
  for arms in off on; do
    if [ $arms = on ]; then E="PROTO_ARM_A=1 PROTO_ARM_B=1"; else E=""; fi
    env $E "$P" --features all -o "$T/r.c" --pattern "$pat" 2>/dev/null
    eng=$(sed -n 's/^#define RX_ENGINE "\([a-z]*\)".*/\1/p' "$T/r.c" | head -1)
    if env $E "$P" --features all --engine=dfa -o "$T/d.c" --pattern "$pat" 2>"$T/e"; then d=compiled
    else d="refused: $(head -1 "$T/e" | cut -c1-70)"; fi
    printf '%s\t%s\t%s\t%s\n' "$pat" "$arms" "$eng" "$d"
  done
done
