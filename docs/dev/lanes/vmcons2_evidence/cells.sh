#!/usr/bin/env bash
# vmcons2: the rev 2 witness cells at the base (stock answers) beside
# libpcre2's, so every build cell's expectation is oracle-checked here.
# Usage: S=<scratch> PCREC=<lane/trailgc build/pcrec> bash cells.sh
# Needs drv.c / drvv.c / p2.c in $S/w (review r6's soundness scratch).
set -u
W=$S/w; P=$PCREC; WD=/home/pcrec/projects/pcrec/scripts/watchdog
timeout 60 gcc -O1 -o "$W/p2" "$W/p2.c" -lpcre2-8 || exit 1
cell() {   # name flags pattern p2pattern driver env subjects...
    local name=$1 flags=$2 pat=$3 p2pat=$4 drv=$5 env=$6; shift 6
    # shellcheck disable=SC2086
    "$P" -p rx $flags -o "$W/$name.c" --pattern "$pat" || { echo "$name COMPILE-FAIL"; return; }
    timeout 120 gcc -O1 -w -I"$W" -o "$W/$name" -include "$W/$name.h" "$W/$drv" "$W/$name.c" || { echo "$name BUILD-FAIL"; return; }
    echo "== $name  pattern: $pat  flags: $flags ${env:+env: $env}"
    echo "-- stock"; env $env "$WD" -s 20 -m 1g -S "vmcons2-$name" -- "$W/$name" "$@"
    echo "-- libpcre2 ($p2pat)"; "$W/p2" "$p2pat" "$@"
}
cell s1  "--features all" '^(?:(?:(a)b)*c){2}$' '^(?:(?:(a)b)*c){2}$' drv.c "" abcc ababcc abcabc cc
cell s2a "--features all" '^(a)${v}c' '^(a)(?:b)c' drvv.c "V=b" abc abd ac
cell s2b "--features all" '^(?:${v}x|by)z' '^(?:(?:a)x|by)z' drvv.c "V=a" axz byz bxz
cell s2c "--features all" '^(?:${v}x|by)z' '^(?:(?:b)x|by)z' drvv.c "V=b" bxz byz axz
cell s3a "--features all" '^x(?:a|(?<=x|yz))w' '^x(?:a|(?<=x|yz))w' drv.c "" xw xaw xxw yzw
cell s3b "--features all" '^(*napla:x(?:a|))xb' '^(*napla:x(?:a|))xb' drv.c "" xb xab
cell s5a "--features all" '^(?:[ab]+b|y)(z)' '^(?:[ab]+b|y)(z)' drv.c "" abz aabz bbz bz yz aaz
cell s5b "--features all" '^(?:.*?x|y)(z)' '^(?:.*?x|y)(z)' drv.c "" axz aaxz xz yz
cell s6  "--features all --engine=vm -fno-splice-calls" '^(x(?>a(?1)?b)y)$' '^(x(?>a(?1)?b)y)$' drv.c "" xaby xaxabyby xaxaxabybyby xay xaxaby
cell k2  "--features all --engine=vm -fno-splice-calls" '^(?:(?1)y)*(a|b)$' '^(?:(?1)y)*(a|b)$' drv.c "" a ay ayb aybyb ayayb
cell k2b "--features all --engine=vm" '^(?:(a)(b))*c$' '^(?:(a)(b))*c$' drv.c "" c abc ababc abac
