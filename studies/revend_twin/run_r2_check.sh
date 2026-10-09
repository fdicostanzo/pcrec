#!/bin/bash
# [OPT-REVEND] revision 2 (lane revrev): answer identity of forms C (walk), A
# (exact) and B (lower), all with the walk at the HEAD (X7) and the dead-seed
# check (X1), against the artifact AND libpcre2 10.46, over patterns.tsv (43),
# r2_patterns.tsv (18) and q1_patterns.tsv (13, byte); then the controls.
#   PCREC=build/pcrec ./run_r2_check.sh      (STUDY; output results/r2_*.txt)
# Twins are built from the -fno-end-window artifact (the rev-end row precedes
# W1, so W1's clamp never runs ahead of the walk); the reference `o` is the
# default artifact. Generated files go to work/r2/ (gitignored).
set -u
HERE=$(cd "$(dirname "$0")" && pwd); : "${PCREC:?}"
W=$HERE/work/r2; S=$HERE/work/subj; R=$HERE/results; mkdir -p "$W" "$R"
[ -f "$S/pool_byte.hex" ] || python3 -I "$HERE/mksubj.py" "$(git -C "$HERE" rev-parse --show-toplevel)" "$S" >/dev/null
# name enc eol pattern, one list
{ grep -v '^#' "$HERE/patterns.tsv"; grep -v '^#' "$HERE/r2_patterns.tsv"
  grep -v '^#' "$HERE/q1_patterns.tsv" | awk -F'\t' 'NF{print $1"\tbyte\t"$2"\t"$3}'; } | grep -v '^$' > "$W/all.tsv"
one() {   # FORM SAB SAN name enc eol pat -> one summary line per pool (also in $d/result.txt)
    local form=$1 sab=$2 san=$3 name=$4 enc=$5 eol=$6 pat=$7 xf=""
    # form walkNA: form C on a -fno-anchored-dfa artifact (no anchored machine:
    # a tie hands s* to the body)
    [ "$form" = walkNA ] && { xf=-fno-anchored-dfa; }
    local d=$W/$form${sab:+-$sab}/$name; mkdir -p "$d"
    one_body "$@" > "$d/result.txt" 2>&1; cat "$d/result.txt"
}
one_body() {
    local form=$1 sab=$2 san=$3 name=$4 enc=$5 eol=$6 pat=$7 xf=""
    [ "$form" = walkNA ] && { xf=-fno-anchored-dfa; form=walk; }
    local d=$W/$1${sab:+-$sab}/$name
    "$PCREC" --features all -e "$enc" -p o $xf -o "$d/o.c" --pattern "$pat" 2>"$d/o.err" || { echo "$form $name REFUSED"; return; }
    "$PCREC" --features all -e "$enc" -p t -fno-end-window $xf -o "$d/t.c" --pattern "$pat" 2>"$d/t.err"
    TWIN_FORM=$form TWIN_SABOTAGE=$sab python3 -I "$HERE/mktwin.py" "$d/t.c" "$d/t.c.twin" t "$eol" 2>"$d/twin.err" \
        || { echo "$form $name NOT-TWINNABLE $(grep -E '^#define O_(ENGINE|DFA_START) ' "$d/o.c" | awk '{printf "%s=%s ",$2,$3}'): $(cat "$d/twin.err")"; return; }
    mv "$d/t.c.twin" "$d/t.c"
    local cf="-O2 -w"; [ -n "$san" ] && cf="-O1 -g -w -fsanitize=address -fno-omit-frame-pointer"
    gcc $cf -I"$d" -o "$d/check" "$HERE/check.c" "$d/o.c" "$d/t.c" -lpcre2-8 || { echo "$form $name CCFAIL"; return; }
    local pools="$S/pool_$enc.hex"; [ "$enc" = byte ] && pools="$pools $S/long.hex"
    for pool in $pools; do
        printf '%-6s%-9s %-24s %-9s ' "$1" "${sab:+[$sab]}" "$name" "$(basename "$pool" .hex)"
        ASAN_OPTIONS=detect_leaks=0 gnutimeout 900 "$d/check" "$pat" "$enc" "$pool" 2>"$d/asan.$(basename "$pool")" | tr -d '\n'
        rc=${PIPESTATUS[0]}
        if grep -q 'AddressSanitizer' "$d/asan.$(basename "$pool")"; then printf ' ASAN:%s' "$(grep -m1 -oE 'AddressSanitizer: [A-Za-z-]+' "$d/asan.$(basename "$pool")")"; fi
        echo " rc=$rc"
    done
}
job() { local line; line=$(sed -n "$1p" "$W/jobs.tsv"); IFS=$'\t' read -r a n e l pat <<< "$line"; one "$a" "" "" "$n" "$e" "$l" "$pat"; }
export -f one one_body job; export W S HERE PCREC
for form in walk exact lower; do awk -F'\t' -v f=$form '{print f"\t"$0}' "$W/all.tsv"; done > "$W/jobs.tsv"
grep -E '^(tie-|x1-)' "$W/all.tsv" | grep -v utf8 | awk '{print "walkNA\t"$0}' >> "$W/jobs.tsv"
seq 1 "$(wc -l < "$W/jobs.tsv")" | xargs -P "${P:-6}" -I{} bash -c 'job {} > /dev/null'
: > "$W/identity.raw"
while IFS=$'\t' read -r a n rest; do cat "$W/$a/$n/result.txt" >> "$W/identity.raw"; done < "$W/jobs.tsv"
cp "$W/identity.raw" "$R/r2_identity.txt"
# CONTROLS: each must show twin_diff > 0 (or an ASan report for nodead)
: > "$W/controls.raw"
for sab in noeol firstseed tien tien1 nodead; do
    san=""; [ $sab = nodead ] && san=asan
    grep -v '^#' "$HERE/controls_r2.tsv" | while IFS=$'\t' read -r name enc eol pat; do
        one walk "$sab" "$san" "$name" "$enc" "$eol" "$pat"
    done >> "$W/controls.raw" 2>&1
done
cp "$W/controls.raw" "$R/r2_controls.txt"
echo "== run_r2_check COMPLETE $(date -Is)" >> "$R/r2_controls.txt"
