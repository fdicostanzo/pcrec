#!/usr/bin/env bash
# docs/design/prior_cost_unify/meter_sites.sh -- PROTOTYPE of rev 2 §3.5's
# independent control ([r3 S2/F1]): the meter class an axis's row DECLARES is
# checked against the meter class DERIVED from the emitted charge sites with
# the axis on and denied. Static site counts per artifact, four counters:
#   steps  `RX_PUSH(`          (each resume point pays one step at the fail label)
#   work   `RX_CHARGE_WORK(`   (D49's forward-work charge)
#   frames `RX_PUSH(`          (capacity: same site, a different budget)
#   trail  `RX_TRAIL(`+`RX_SET(` (capacity)
# Per (pattern, axis): delta = on - denied per counter, then
#   all <= 0 and some < 0 -> DELETES; some > 0 and some < 0 -> SUBSTITUTES;
#   some > 0, none < 0 -> ADDS; all 0 -> NONE (the axis did not move the meter
#   here). A SITE count is a proxy for the dynamic charge; the dynamic arm is
#   [GIVEUP-DIFF]'s budget ladder. Light: a handful of compiles.
# Usage: meter_sites.sh PCREC OUTDIR  (writes only under OUTDIR)
set -u
P=$1; O=$2; mkdir -p "$O"
count() { grep -c "$2" "$1" 2>/dev/null || true; }
row() { # pat axisflag
  local pat=$1 ax=$2 a b
  a="$O/on.c"; b="$O/off.c"
  gnutimeout 20 "$P" -p rx --engine=vm --features all -o "$a" --pattern "$pat" >/dev/null 2>&1 || { printf "%s\t%s\tREFUSED-ON\n" "$ax" "$pat"; return; }
  gnutimeout 20 "$P" -p rx --engine=vm --features all "$ax" -o "$b" --pattern "$pat" >/dev/null 2>&1 || { printf "%s\t%s\tREFUSED-OFF\n" "$ax" "$pat"; return; }
  local cls="" pos=0 neg=0 d out=""
  for spec in 'push:RX_PUSH(' 'work:RX_CHARGE_WORK(' 'trail:RX_TRAIL(\|RX_SET('; do
    local n=${spec%%:*} re=${spec#*:}
    d=$(( $(count "$a" "$re") - $(count "$b" "$re") ))
    out="$out\t$n=$d"; [ $d -gt 0 ] && pos=1; [ $d -lt 0 ] && neg=1
  done
  if [ $pos = 1 ] && [ $neg = 1 ]; then cls=SUBSTITUTES
  elif [ $pos = 1 ]; then cls=ADDS
  elif [ $neg = 1 ]; then cls=DELETES
  else cls=NONE; fi
  printf "%s\t%s%b\t%s\n" "$ax" "$pat" "$out" "$cls"
}
while IFS=$'\t' read -r ax pat; do
  [ -z "$ax" ] && continue; row "$pat" "$ax"
done <<'ROWS'
-fno-possessify	\b(\w+)\b\s+\1\b
-fno-possessify	(a+)b
-fno-possessify	([a-z]+)\d
-fno-poss-bref-first	\b(\w+)\b\s+\1\b
-fno-poss-ctx-follow	\b(\w+)\b\s+\1\b
-fno-lit-run	(abcdef|x)y
-fno-alt-island	(foo|bar|baz)q
-fno-counter	(a|bc){0,40}d
-fno-revdet	(a|b)+c
-fno-hyb-reseed	(?<=a)x(\d)
-fno-start-set	(\w)\1
ROWS
