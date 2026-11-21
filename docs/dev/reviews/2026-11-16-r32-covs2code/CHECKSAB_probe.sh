#!/usr/bin/env bash
# CHECKSAB probe: one case, one tree. probe.sh ROOT FL PAT MODE OUT [SHEX]
#  MODE verdict|facts|answer. ROOT = tree root with build/. Pattern spelled as cases.tsv (@D etc).
set -u
root="$1"; fl="$2"; pat="$3"; mode="$4"; out="$5"; shex="${6-}"
W=/home/pcrec/projects/pcrec/worktrees/crit-covs2code
. "$W/tests/kitproof/loader.sh"
kp_limits "$root/build/pcrec" || { echo "LIMITS-UNREAD $KP_ERR"; exit 1; }
a="$(kp_flags "$fl")"; p="$(kp_pat "$pat")"
rm -rf "$out"; mkdir -p "$out"
case "$mode" in
 facts)
   enc=byte; case "$fl" in *u*) enc=utf8;; esac
   nice timeout 120 "$root/build/pcrec" --features all $a --emit-facts --pattern "$p" > "$out/facts" 2> "$out/err"; echo "RC=$?"
   awk -F'\t' -v enc="$enc" '/^#section / { sec = substr($0, 10); next } sec == "cover" && $1 == enc { print $2 "|" $3 "|" $4 "|" $5 }' "$out/facts" | cut -c1-120 ;;
 verdict|answer)
   nice timeout 120 "$root/build/pcrec-harness" --harness=kit-proof --features all -p rx $a -o "$out/a.c" --pattern "$p" > "$out/err" 2>&1; rc=$?
   echo "RC=$rc"; [ $rc -eq 0 ] || { head -3 "$out/err"; exit 0; }
   echo "SCAN=$(sed -n 's/^#define RX_DFA_SCAN "\([^"]*\)".*/\1/p' "$out/a.c")"
   if [ "$mode" = answer ]; then
     nice timeout 120 gcc -O1 -std=gnu11 -include "$out/a.h" -o "$out/drv" "$W/tests/kitproof/drv.c" "$out/a.c" > "$out/gcc" 2>&1 || { echo DRV-FAIL; head -3 "$out/gcc"; exit 0; }
     echo "GOT=$(printf '%s\n' "$shex" | timeout 10 "$out/drv")"
     phex="$(printf '%s' "$p" | xxd -p | tr -d '\n')"
     echo "WANT=$(awk -F'\t' -v f="$fl" -v ph="$phex" -v s="$shex" '$1==f && $2==ph && $3==s {print $4; exit}' "$W/tests/kitproof/answers.tsv")"
   fi ;;
esac
