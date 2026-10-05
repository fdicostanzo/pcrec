#!/usr/bin/env bash
HH=/Users/fdicostanzo/pcrec/docs/dev/reviews/2026-10-05-r4-startset/ssc-sound-harness   # this directory (drv2e.c/drv3e.c)
# critic copy of run_dfatwin.sh's one(), narrowing to T = S & E via dfatwin.py
HERE=/Users/fdicostanzo/pcrec/docs/design/startset/twin; CC=gcc-16
one() {
  local pat="$1" alpha="$2" L="$3"; shift 3
  rm -f "$W"/rx.* "$W"/tw.* "$W"/rs.*
  for p in rx tw rs; do "$PCREC" --features all "$@" -p $p -o "$W/$p.c" --pattern "$pat" >/dev/null 2>"$W/err" || { echo "REFUSED $pat $(head -1 $W/err)"; return; }; done
  local eng; eng=$(grep -h '#define RX_ENGINE \|#define RX_VM_PREFILTER \|#define RX_DFA_PREFILTER \|#define RX_VM_PREFILTER_LANG ' "$W/rx.c" | awk '{print $3}' | tr -d '"' | paste -sd/ -)
  local penc=(); case " $* " in *" -e utf8 "*) penc=(-e utf8);; esac
  local fs; fs=$(printf 'x\t%s\n' "$(printf '%s' "$pat" | xxd -p | tr -d '\n')" | "$PROBE" "${penc[@]}" | tail -1)
  local sz; sz=$(python3 "$HERE/dfatwin.py" "$W/tw.c" "$W/rs.c" "$(echo "$fs" | cut -f5)" 2>&1) || { echo "NOT-IN-REACH $pat ($eng): $(echo "$sz" | tail -1)"; return; }
  "$CC" -O1 -w -I"$W" -o "$W/drv" "$HH/drv3e.c" "$W/rx.c" "$W/tw.c" "$W/rs.c" || { echo "CC-FAIL $pat"; return; }
  printf '%-30s %-34s %-12s ' "$pat" "$eng" "$sz"
  python3 -c "
import itertools,sys
A=[bytes.fromhex(x) for x in sys.argv[1].split(',')]
for L in range(int(sys.argv[2])+1):
  for t in itertools.product(A,repeat=L): print(''.join(chr(c) if 32<=c<127 and c!=92 else chr(92)+'x%02x'%c for c in b''.join(t)))" "$alpha" "$L" | "$W/drv" | tail -4
}
