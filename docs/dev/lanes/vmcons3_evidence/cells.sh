#!/bin/bash
# Rev 3's new witness cells: base answers and libpcre2 10.46, plus the
# structural facts each cell must reach (a SPAN block, an island root shape).
# usage: PCREC=<merged build/pcrec> S=<scratch dir> cells.sh
set -u
E=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$S"
gcc -O1 -w -o "$S/p2" "$E/p2.c" -lpcre2-8 || exit 1
cell() {  # cell NAME 'PATTERN' 'FLAGS' subj...
    local n=$1 pat=$2 fl=$3; shift 3
    echo "=== $n  $pat  [$fl]"
    "$PCREC" -p rx $fl -o "$S/$n.c" --pattern "$pat" || return
    echo "engine: $(sed -n 's/^#define RX_ENGINE "\(.*\)"/\1/p' "$S/$n.c")" \
         "islands: $(sed -n 's/^#define RX_VM_ALT_ISLANDS \(.*\)/\1/p' "$S/$n.c")" \
         "span-blocks: $(grep -c 'rx_span_cursor = scan_position;' "$S/$n.c")" \
         "kit-loops: $(grep -c 'while ((rx_span_cursor' "$S/$n.c")" \
         "switch: $(grep -c 'switch (subject\[scan_position' "$S/$n.c")"
    "$E/run.sh" "$S" "$n" "$S/$n.c" "$@" | sed 's/^/  base     /'
    "$S/p2" "$pat" '' "$@" | sed 's/^/  libpcre2 /'
}
cell C5b '^(?:.*?x|y)(z)'        '--features all' axz aaxz xz yz
cell C5c '^(?:[ab]{2,}?b|y)(z)'  '--features all' abbz aabz abz ababz yz
cell C7a '^(?:\d+y|(?:ab|abc|abcd|abcde))(z)' '--features all -fno-altcls-factor' abz abcz abcdez 12yz
cell C7b '^(?:\d+y|(?:ab|abc|cd|cde))(z)' '--features all' abz abcz cdz cdez 12yz xz
cell C6  '^(x(?>a(?1)?b)y)$'     '--features all --engine=vm -fno-splice-calls' xaby xaxabyby xaxaxabybyby xay xaxaby
cell C8  '^(a)b+c'               '--features all' abbc abc ac
