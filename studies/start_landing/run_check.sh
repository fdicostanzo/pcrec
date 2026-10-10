#!/bin/bash
# [START-LANDING] hand-twin answer identity over a run list (STUDY).
#   PCREC=build/pcrec POOLDIR=<dir with pool_byte.hex pool_utf8.hex> MODE=assert|replace \
#     [CONTROL=noguard|wplus1|forcelanding] ./run_check.sh RUNLIST.tsv OUTDIR
# RUNLIST.tsv: name enc icase cfg pattern_hex row W [subjects,comma,separated]
#   (runlist.py writes it from census.py's output). Per row: emit the
# artifact twice (-p o, -p t) with the bench's flags, twin the t copy
# (mktwin.py, FORM from the row), build check.c against libpcre2-8 and sweep:
# the machine-derived exhaustive pool (mksubj.py), the corpus/edge pool for
# the encoding, and the row's own (bench) subjects. CONTROL is a planted
# fault: the sweep must then FAIL (controls.tsv names the expected rows).
# One summary line per (row, pool); exit 1 if any row disagreed.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
: "${PCREC:?}" "${POOLDIR:?}"; MODE=${MODE:-assert}; CONTROL=${CONTROL:-}
RL=$1; OUT=$2; mkdir -p "$OUT"
bad=0
while IFS=$'\t' read -r name enc icase cfg phex row W subs; do
    case "$name" in ''|'#'*|name) continue ;; esac
    d=$OUT/$(printf '%s' "$name.$cfg" | tr '/:' '__'); mkdir -p "$d"
    args=(--features all); [ "$enc" = utf8 ] && args+=(-e utf8); [ "$icase" = 1 ] && args+=(-i)
    [ "$cfg" = nocaps ] && args+=(--no-captures)
    pat=$(python3 -c 'import sys;b=bytes.fromhex(sys.argv[1]);print(""+"".join("\\\\" if c==0x5c else "\\\"" if c==0x22 else chr(c) if 0x20<=c<0x7f else "\\x%02x"%c for c in b)+"")' "$phex")
    for p in o t; do
        "$PCREC" "${args[@]}" -p $p -o "$d/$p.c" --pattern-esc --pattern "\"$pat\"" 2>"$d/$p.err" \
            || { echo "$name $cfg REFUSED"; continue 2; }
    done
    case "$row" in
        end-minus-width) form="width:$W"; [ "$CONTROL" = wplus1 ] && form="width:$((W+1))" ;;
        landing|forcelanding) form=landing; [ "$enc" = utf8 ] && form=landing-u8 ;;
        *) echo "$name $cfg SKIP row=$row"; continue ;;
    esac
    xa=(); [ "$CONTROL" = noguard ] && xa=(--no-guard)
    if ! python3 "$HERE/mktwin.py" "$d/t.c" "$d/t.c.tw" t "$form" "$MODE" "${xa[@]}" 2>"$d/tw.err"; then
        echo "$name $cfg NOT-TWINNABLE: $(cat "$d/tw.err")"; bad=1; continue
    fi
    mv "$d/t.c.tw" "$d/t.c"
    gcc -O1 -w -I"$d" -o "$d/check" "$HERE/check.c" "$d/o.c" "$d/t.c" -lpcre2-8 2>"$d/cc.err" \
        || { echo "$name $cfg CCFAIL $(head -c 300 "$d/cc.err")"; bad=1; continue; }
    python3 "$HERE/mksubj.py" "$d/o.c" o "$enc" "$d/ex.hex" >/dev/null
    pools=("$d/ex.hex" "$POOLDIR/pool_$enc.hex")
    if [ -n "${subs:-}" ]; then
        python3 -c 'import sys
for p in sys.argv[2].split(","):
    if p: sys.stdout.write(open(p,"rb").read().hex()+"\n")' x "$subs" > "$d/own.hex"
        pools+=("$d/own.hex")
    fi
    for pool in "${pools[@]}"; do
        printf '%-44s %-7s %-16s %-6s ' "$name" "$cfg" "$form" "$(basename "$pool" .hex)"
        gnutimeout 900 "$d/check" "$phex" "$enc" "$icase" "$pool" || bad=1
    done
    rm -f "$d/check" "$d/own.hex"
done < "$RL"
exit $bad
