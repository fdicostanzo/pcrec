#!/usr/bin/env bash
# docs/design/findall_iter/twin/run_twin.sh — lane iterdes, [FINDALL-NEXT] HAND TWIN runner.
# ANSWERS AND SIZES ONLY: no clock is read anywhere in this script.
#
# For each case (prefix, pcrec flags, pattern, mode): emit the artifact with the
# tree's build/pcrec, transform it with mktwin.py, compile the twin + drv.c at
# -O2 -Wall -Wextra -Werror, run the case's subjects through it and compare:
#   plain mode: I == L == N (the iterator equals today's loop, span for span)
#   retry mode: I == N == G, G = libpcre2 10.46's global loop (semprobe.c), the
#               independent oracle; L is printed beside it for the record.
# Then the codegen facts: `size` of the plain artifact's object vs the twin's,
# the per-symbol sizes of _search/_next/_next_n, and whether the twin's exported
# _search has the SAME instruction bytes as the plain artifact's (objdump).
#
# usage: [TWIN_SHARED=1] run_twin.sh TREE OUTDIR   (TWIN_SHARED: one noinline body, the size alternative)
set -u
TREE=$(cd "$1" && pwd); OUT=$2
TW=$TREE/docs/design/findall_iter/twin
PCREC=$TREE/build/pcrec
SEMPROBE=$OUT/semprobe
mkdir -p "$OUT"
gcc -O1 -o "$SEMPROBE" "$TREE/docs/design/findall_iter/sem/semprobe.c" -lpcre2-8 || exit 2
CF="-O2 -Wall -Wextra -Werror"
fail=0

# case table, TAB-separated: prefix, pcrec flags ('-' = none), pattern, mode, subjects
# (escaped, '|'-separated; <empty> is the empty subject)
cases() {
cat <<'EOF'
ra	-	a	plain	aaaa|a|b|<empty>|xaxax|aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
rw	-	\w+	plain	the quick brown fox|  a b  |x|wordwordword|a\x00b c
rv	-	a(b|c)+d	plain	abd acd xabcbd|abbbbd|ad|abcd abcd abcd
rn	-	[0-9]+x	plain	12x 3x 45y 6x|x|0000000000x
rl	-	a*	plain	bbb|aaa|aab|<empty>
rq	-	(?:ab|a)	plain	aab|ababab|b
ru	-e utf8	.	plain	a\xce\xb1b|\xce\xb1\xce\xb2|a\x80a|\x80\x80b
rk	-e utf8	a	plain	a\x80a|\xce\xb1a\xce\xb1|aaa
rg	--features all	\G\w+	plain	ab ab ab|abc|<empty>
re	--engine=vm	|a	retry	aaa|ab|b|<empty>
rz	--engine=vm	a*?	retry	aaa|baab|<empty>
rx	--engine=vm	x*|y	retry	y|xyy|yxy
rr	--engine=vm	a??b?	retry	ab|aab|ba
rt	--engine=vm --features all	(?<=a)|b	retry	abab|bb|<empty>
rf	--engine=vm --features all	(?=b)|b	retry	ab|bbb
rc	--engine=vm	(?:^|,)([^,]*)	retry	,|, |a,b,,c|,,
rj	--engine=vm --features all	ab\K	retry	ababab|abab|<empty>
EOF
}

while IFS=$'\t' read -r pfx flags pat mode subs; do
    [ -n "$pfx" ] || continue
    [ "$flags" = - ] && flags=""
    d=$OUT/$pfx; mkdir -p "$d"
    # shellcheck disable=SC2086
    if ! (cd "$d" && "$PCREC" -p "$pfx" $flags -o "$pfx.c" --pattern "$pat") 2> "$d/pcrec.err"; then
        echo "CASE $pfx: pcrec refused: $(head -1 "$d/pcrec.err")"; fail=1; continue
    fi
    rflag=""; [ "$mode" = retry ] && rflag="--retry"
    [ -n "${TWIN_SHARED:-}" ] && rflag="$rflag --shared"
    python3 -I "$TW/mktwin.py" "$pfx" "$d/$pfx.c" "$d/twin.c" $rflag || { echo "CASE $pfx: mktwin failed"; fail=1; continue; }
    cp "$TW/iter_abi.h" "$d/"
    PU=$(echo "$pfx" | tr a-z A-Z)
    gcc $CF -c -o "$d/plain.o" "$d/$pfx.c" -I"$d" || { echo "CASE $pfx: plain compile failed"; fail=1; continue; }
    gcc $CF -c -o "$d/twin.o" "$d/twin.c" -I"$d" || { echo "CASE $pfx: twin compile failed"; fail=1; continue; }
    gcc $CF -o "$d/drv" "$TW/drv.c" "$d/twin.o" -I"$d" -DPFX="$pfx" -DPFXU="$PU" -DHDR="\"$pfx.h\"" \
        || { echo "CASE $pfx: driver build failed"; fail=1; continue; }
    : > "$d/subjects"; : > "$d/pairs"
    IFS='|' read -ra S <<< "$subs"
    for x in "${S[@]}"; do [ "$x" = "<empty>" ] && x=""; printf '%s\n' "$x" >> "$d/subjects"; printf '%s\t%s\n' "$pat" "$x" >> "$d/pairs"; done
    "$d/drv" < "$d/subjects" > "$d/drv.out"
    utf=""; case " $flags " in *" -e utf8 "*) utf=1;; esac
    if [ -n "$utf" ]; then sed 's/^/U\t/' "$d/pairs" | "$SEMPROBE" > "$d/sem.out" 2>/dev/null
    else "$SEMPROBE" < "$d/pairs" > "$d/sem.out" 2>/dev/null; fi
    paste "$d/drv.out" <(cut -f6,7 "$d/sem.out") > "$d/joined"
    while IFS=$'\t' read -r L I rc Z B N PL PG; do
        I=${I#I=}; L=${L#L=}; N=${N#N=}; PL=${PL#L=}; PG=${PG#G=}; Z=${Z#Z=}; B=${B#B=}
        nI=$(printf '%s' "$I" | grep -o '(' | wc -l)
        ok=1
        [ "$I" = "$N" ] || ok=0
        [ "$Z" = "$nI" ] || ok=0
        [ "$B" = "-10" ] || ok=0
        case "$rc" in rc=0) ;; *) ok=0;; esac
        if [ "$mode" = plain ]; then [ "$I" = "$L" ] || ok=0; [ "$L" = "$PL" ] || ok=0
        else [ "$I" = "$PG" ] || ok=0; fi
        st=OK; [ $ok = 1 ] || { st=MISMATCH; fail=1; }
        printf 'CASE %-3s %-6s %-8s %-5s I=%s | L=%s | G=%s | N=%s Z=%s B=%s %s\n' \
            "$pfx" "$mode" "$st" "${rc#rc=}" "$I" "$L" "$PG" "$N" "$Z" "$B" "$pat"
    done < "$d/joined"
    # codegen facts
    ps=$(size "$d/plain.o" | awk 'NR==2{print $1}'); ts=$(size "$d/twin.o" | awk 'NR==2{print $1}')
    sym() { nm -S --size-sort "$1" | awk -v s="$2" '$4==s{print $2}' | { read -r h && printf '%d' "$((16#$h))"; }; }
    srch_p=$(sym "$d/plain.o" "${pfx}_search"); srch_t=$(sym "$d/twin.o" "${pfx}_search")
    objdump -d --no-show-raw-insn "$d/plain.o" | awk -v f="<${pfx}_search>:" '$2==f{p=1;next} p&&/^$/{exit} p' | sed 's/^ *[0-9a-f]*://; s/#.*//; s/[0-9a-f]* </</g' > "$d/search_plain.s"
    objdump -d --no-show-raw-insn "$d/twin.o"  | awk -v f="<${pfx}_search>:" '$2==f{p=1;next} p&&/^$/{exit} p' | sed 's/^ *[0-9a-f]*://; s/#.*//; s/[0-9a-f]* </</g' > "$d/search_twin.s"
    same=different; cmp -s "$d/search_plain.s" "$d/search_twin.s" && same=identical
    link=$(grep -o 'body linkage: [^-]*' "$d/twin.c" | head -1)
    printf 'SIZE %-3s text plain=%s twin=%s (+%s) | _search plain=%s twin=%s (%s insns) | _next=%s _next_n=%s __find=%s | %s\n' \
        "$pfx" "$ps" "$ts" "$((ts - ps))" "$srch_p" "$srch_t" "$same" \
        "$(sym "$d/twin.o" "${pfx}_next")" "$(sym "$d/twin.o" "${pfx}_next_n")" "$(sym "$d/twin.o" "${pfx}__find")" "$link"
done < <(cases)
echo "run_twin: $([ $fail = 0 ] && echo ALL OK || echo FAILURES)"
exit $fail
