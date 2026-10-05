#!/usr/bin/env bash
# [START-SET] VM-hat twin battery.  Env: PCREC, PROBE (fs_probe), CC (gcc-16), W (scratch dir)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; CC="${CC:-gcc-16}"
one() {  # one <pattern> <alphabet> <maxlen> [extra flags...]
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
  "$CC" -O1 -w -I"$W" -o "$W/drv" "$HERE/drv2.c" "$W/rx.c" "$W/tw.c" || { echo "CC-FAIL $pat"; return; }
  printf '%-36s %-10s |S|=%-3s ' "$pat" "$eng" "$(echo "$fs" | cut -f4)"
  python3 -c "
import itertools,sys
A=sys.argv[1]
for L in range(int(sys.argv[2])+1):
  for t in itertools.product(A,repeat=L): print(''.join(t))" "$alpha" "$L" | "$W/drv" | tail -1
}
one '\((?:[^()]|(?R))*\)'            '()a'    9
one '(["'"'"'])(?:(?!\1)[^\\]|\\.)*\1' '"'"'"'\a'   8
one '<(?<t>\w+)>[^<]*</\k<t>>'        '<>/a'   10
one '\b(\w+)\s+\1\b'                  'ab _'   8
# (?<=a)b(c) at auto is a hybrid: run forced below
one '\Bcat\B'                         'cat x'  7  --engine=vm
one '(?i)cat'                         'cCaAt'  6  --engine=vm
one 'x*(a)\1'                         'xa'     10
one '(?:\Ga|b)c'                      'abc'    8  --engine=vm
one 'a\Kb'                            'ab'     10 --engine=vm
one '\b(?:true|false|null)\b'         'atrue ' 7  --engine=vm
one '(a+)x\1catdog'                   'axcatdog' 6
one '(?<=a)b(c)'                      'abc'    8  --engine=vm
one '(?i)caf\x{e9}'                   'cCaf'"$(printf '\xc3\xa9\xc3\x89\x80')" 6 --engine=vm -e utf8
one '(?i)stra\x{df}e'                 'sStr'"$(printf '\xc3\x9f\xc5\xbf\x80')"'ae' 6 --engine=vm -e utf8
echo "== failing-direction CONTROLS (a twin missing one start byte MUST disagree)"
DROP=27 one '(["'"'"'])(?:(?!\1)[^\\]|\\.)*\1' '"'"'"'\a'   8
DROP=63 one '(?i)cat'                 'cCaAt'  6  --engine=vm
DROP=73 one '(?i)stra\x{df}e'         'sStr'"$(printf '\xc3\x9f\xc5\xbf\x80')"'ae' 6 --engine=vm -e utf8
