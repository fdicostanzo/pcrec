#!/usr/bin/env bash
# [START-SET] DFA-hat twin battery: narrowing without the re-seed must LOSE
# matches somewhere in the battery (the failing-direction control, firstset
# §4.6), narrowing with it must agree everywhere.  Env: PCREC, PROBE, CC, W.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CC="${CC:-gcc-16}"
one() {
  local pat="$1" alpha="$2" L="$3"; shift 3
  rm -f "$W"/rx.* "$W"/tw.* "$W"/rs.*
  for p in rx tw rs; do "$PCREC" --features all "$@" -p $p -o "$W/$p.c" --pattern "$pat" >/dev/null 2>"$W/err" || { echo "REFUSED $pat"; return; }; done
  local eng; eng=$(grep -h '#define RX_ENGINE \|#define RX_VM_PREFILTER \|#define RX_DFA_PREFILTER ' "$W/rx.c" | awk '{print $3}' | tr -d '"' | paste -sd/ -)
  local penc=(); case " $* " in *" -e utf8 "*) penc=(-e utf8);; esac
  local fs; fs=$(printf 'x\t%s\n' "$(printf '%s' "$pat" | xxd -p | tr -d '\n')" | "$PROBE" "${penc[@]}" | tail -1)
  local sz; sz=$(python3 "$HERE/dfatwin.py" "$W/tw.c" "$W/rs.c" "$(echo "$fs" | cut -f5)" 2>&1) || { echo "NOT-IN-REACH $pat ($eng): $(echo "$sz" | tail -1)"; return; }
  "$CC" -O1 -w -I"$W" -o "$W/drv" "$HERE/drv3.c" "$W/rx.c" "$W/tw.c" "$W/rs.c" || { echo "CC-FAIL $pat"; return; }
  printf '%-30s %-34s %-12s ' "$pat" "$eng" "$sz"
  python3 -c "
import itertools,sys
A=sys.argv[1]
for L in range(int(sys.argv[2])+1):
  for t in itertools.product(A,repeat=L): print(''.join(t))" "$alpha" "$L" | "$W/drv" | tail -1
}
one '\b(?:ab|cd)\b'           'abcdx '  8 --no-captures
one '\b(?:ab|cd)\b'           'abcdx '  8
one '\Bcat\B'                 'catx '   8 --no-captures
one '\b[0-9]{2,3}\b'          '01a '    8 --no-captures
one '(?m)^ab'                 'ab\nx'   9 --no-captures
one '\b(?:true|false|null)\b' 'atrue '  8 --no-captures
one '(?i)\bdb_name'           'dbDB_nam' 7 --no-captures
one '\bcat\b'                 'catx '   8 --no-captures -e utf8
