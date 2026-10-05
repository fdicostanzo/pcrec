#!/usr/bin/env bash
HH=/Users/fdicostanzo/pcrec/docs/dev/reviews/2026-10-05-r4-startset/ssc-sound-harness   # this directory (drv2e.c/drv3e.c)
# sourced copy of run_vmtwin.sh's one() for critic probes
HERE=/Users/fdicostanzo/pcrec/docs/design/startset/twin; CC=gcc-16
one() {
  local pat="$1" alpha="$2" L="$3"; shift 3
  rm -f "$W"/rx.* "$W"/tw.*
  "$PCREC" --features all "$@" -p rx -o "$W/rx.c" --pattern "$pat" >/dev/null 2>"$W/err" || { echo "REFUSED $pat: $(head -1 "$W/err")"; return; }
  "$PCREC" --features all "$@" -p tw -o "$W/tw.c" --pattern "$pat" >/dev/null 2>&1
  local eng; eng=$(grep -h '#define RX_ENGINE \|#define RX_VM_PREFILTER ' "$W/rx.c" | awk '{print $3}' | tr -d '"' | paste -sd/ -)
  local penc=(); case " $* " in *" -e utf8 "*) penc=(-e utf8);; esac
  local fs; fs=$(printf 'x\t%s\n' "$(printf '%s' "$pat" | xxd -p | tr -d '\n')" | "$PROBE" "${penc[@]}" | tail -1)
  local nul set; nul=$(echo "$fs" | cut -f3); set=$(echo "$fs" | cut -f5)
  if [ "$nul" != 0 ]; then echo "SKIP(nullable) $pat"; return; fi
  python3 "$HERE/vmtwin.py" "$W/tw.c" tw "$set" || { echo "PATCH-FAIL $pat"; return; }
  "$CC" -O1 -w -I"$W" -o "$W/drv" "$HH/drv2e.c" "$W/rx.c" "$W/tw.c" || { echo "CC-FAIL $pat"; return; }
  printf '%-36s %-10s |S|=%-3s ' "$pat" "$eng" "$(echo "$fs" | cut -f4)"
  python3 -c "
import itertools,sys
A=[bytes.fromhex(x) for x in sys.argv[1].split(',')]
for L in range(int(sys.argv[2])+1):
  for t in itertools.product(A,repeat=L): print(''.join(chr(c) if 32<=c<127 and c!=92 else chr(92)+'x%02x'%c for c in b''.join(t)))" "$alpha" "$L" | "$W/drv" | tail -3
}
