#!/bin/bash
# grid1/checklib.sh -- the check legs as functions, sourced by check.sh and
# plants.sh (so a plant runs EXACTLY the legs the gate runs). Needs OUT, T.
# The leg definitions are in check.sh's header.
RES=${RES:-$OUT/res}; export RES
safe() { tr '/@' '__' <<<"$1"; }
ans() {    # the answer line of a run, without the fixed-mode tail
  sed -E 's/ (passes|cycle|cycleexp|ns\/pass)=[^ ]*//g'
}
group() {  # cell subjtoken mode arms
  c=$1; tok=$2; m=$3; IFS=, read -r -a A <<<"$4"
  s=${tok%@*}; off=0; [ "$tok" != "$s" ] && off=${tok#*@}
  r=$RES/g.$(safe "$c.$tok.$m"); : > "$r"
  b=${A[0]}; bd=$OUT/bin/$c/$b; sp=$OUT/subj/$s
  key="$c $tok $m"
  bl=$(GRID_OFF=$off GRID_FIXED=0 "$T" 600 "$bd/run" "$sp" "$m" 2>&1 | ans); brc=$?
  # leg O
  o=$(awk -F'\t' -v c="$c" -v s="$s" -v m="$m" '$1==c&&$2==s&&$3==m{print $4}' "$OUT/oracle.tsv")
  if [ -n "$o" ]; then
    [ "$o" = "$bl" ] && echo "$c $b O $key OK" >> "$r" || echo "$c $b O $key FAIL base='$bl' oracle='$o'" >> "$r"
  fi
  # base chk (leg L reference)
  bc=""; if [ -x "$bd/chk" ]; then bc=$OUT/tmp/L.$(safe "$c.$tok.$m.$b")
    if [ -d "$sp" ]; then GRID_OFF=$off "$T" 900 "$bd/chk" "$sp" list "$m" > "$bc" 2>/dev/null
    else "$T" 900 "$bd/chk" "$sp" list "$m" "$off" > "$bc" 2>/dev/null; fi || echo "$c $b L $key FAIL base chk rc=$?" >> "$r"
  fi
  nb=1; [ -d "$sp" ] && nb=$(ls "$sp" | grep -vc '^\.')
  for a in "${A[@]}"; do
    d=$OUT/bin/$c/$a
    if [ "$a" != "$b" ]; then
      l=$(GRID_OFF=$off GRID_FIXED=0 "$T" 600 "$d/run" "$sp" "$m" 2>&1 | ans)
      [ -n "$l" ] && [ "$l" = "$bl" ] && echo "$c $a R $key OK" >> "$r" || echo "$c $a R $key FAIL got='$l' base='$bl'" >> "$r"
      if [ -n "$bc" ] && [ -x "$d/chk" ]; then
        lo=$OUT/tmp/L.$(safe "$c.$tok.$m.$a")
        if [ -d "$sp" ]; then GRID_OFF=$off "$T" 900 "$d/chk" "$sp" list "$m" > "$lo" 2>/dev/null
        else "$T" 900 "$d/chk" "$sp" list "$m" "$off" > "$lo" 2>/dev/null; fi
        rc=$?; [ "$rc" = 0 ] && cmp -s "$lo" "$bc" && echo "$c $a L $key OK" >> "$r" || echo "$c $a L $key FAIL rc=$rc" >> "$r"
        rm -f "$lo"
      fi
    fi
    if [ "$nb" -gt 1 ]; then
      cl=$(GRID_OFF=$off GRID_FIXED=$nb "$T" 600 "$d/run" "$sp" "$m" 2>&1)
      h=$(sed -n 's/.* cycleexp=\([0-9a-f]*\).*/\1/p' <<<"$cl"); ch=$(sed -n 's/.* cycle=\([0-9a-f]*\).*/\1/p' <<<"$cl")
      [ -n "$h" ] && [ "$h" = "$ch" ] && echo "$c $a C $key OK" >> "$r" || echo "$c $a C $key FAIL '$cl'" >> "$r"
    fi
  done
  [ -n "$bc" ] && rm -f "$bc"
}

# ---- the deep legs (own generated arms; the walk and V1 for reference)
DEEP_ARMS="V1 G1 V2 V3 S1 S2 S3 A1 A2 A3 Sn An"
deep_subj() {
  case "$1" in
    dig) echo "g1-dig-n48-ginf-Lnone g1-dig-n63-ginf-Lnone g1-dig-n64-ginf-Lnone g1-dig-n65-ginf-Lnone g1-dig-n128-ginf-Lnone g1-dig-n48-g8-L32-u g1-dig-n65-g8-L32-u g1-dig-n128-g8-L32-u g1-dig-n64k-g2-L32 g1-dig-n64k-g8-L1k-burst g1-dig-n64k-ginf-L64k" ;;
    dfa-hat) echo "g1-dfa-hat-n64k-g2-L32 g1-dfa-hat-n64k-g8-L8-u g1-dfa-hat-n64k-ginf-L64k prose64k" ;;
    bounded) echo "g1-bounded-n64k-g2-L8 g1-bounded-n64k-g32-L1k-u g1-bounded-n64k-ginf-L64k prose64k" ;;
    hex-run|word-eq|quad) echo "g1-f3-$1-n64k-ginf-Lnone code64k" ;;
  esac
}
fuzz_subj() {
  case "$1" in
    dig) echo "g1-dig-n64k-g2-L32 g1-dig-n64k-g8-L1k-burst" ;;
    dfa-hat) echo "g1-dfa-hat-n64k-g8-L8-u" ;;
    bounded) echo "g1-bounded-n64k-g2-L8" ;;
    *) echo "code64k" ;;
  esac
}
COMBOS="0,0 1,1 13,29 31,7"
export COMBOS
deep_ref() {   # the walk's reference outputs for one cell
  c=$1; b=$OUT/bin/$c/walk; a=$OUT/ans/$c; mkdir -p "$a"; r=$RES/d.$c.walk; : > "$r"
  for s in $(deep_subj "$c"); do
    for m in first all; do
      "$T" 600 "$b/chk" "$OUT/subj/$s" list $m > "$a/$s.$m" || echo "$c walk D $s $m RC=$?" >> "$r"
      for cc in $COMBOS; do cut=${cc#*,}; [ "$cut" = 0 ] && continue
        "$T" 600 "$b/chk" "$OUT/subj/$s" list $m 0 "$cut" > "$a/$s.$m.cut$cut" || echo "$c walk D $s $m cut$cut RC=$?" >> "$r"; done
    done
    "$T" 600 "$b/chk" "$OUT/subj/$s" every > "$a/$s.every" || echo "$c walk E $s RC=$?" >> "$r"
    "$T" 600 "$b/chk" "$OUT/subj/$s" rand > "$a/$s.rand" || echo "$c walk N $s RC=$?" >> "$r"
  done
  for s in $(fuzz_subj "$c"); do "$T" 900 "$b/chk" "$OUT/subj/$s" fuzz > "$a/$s.fuzz" || echo "$c walk F $s RC=$?" >> "$r"; done
}
deep_one() {   # cell arm [resfile-tag]
  c=$1; V=$2; tag=${3:-$V}; d=$OUT/bin/$c/$V; a=$OUT/ans/$c; r=$RES/d.$c.$tag; : > "$r"
  cc_() { leg=$1; ref=$2; shift 2
    "$T" 900 "$@" > "$OUT/tmp/$c.$tag.out" 2> "$OUT/tmp/$c.$tag.err"; rc=$?
    if [ "$rc" = 0 ] && cmp -s "$OUT/tmp/$c.$tag.out" "$ref"; then echo "$c $V $leg OK" >> "$r"
    else echo "$c $V $leg FAIL rc=$rc $(head -c 300 "$OUT/tmp/$c.$tag.err" | tr '\n' ' ')" >> "$r"; fi; }
  for s in $(deep_subj "$c"); do
    sp=$OUT/subj/$s
    cc_ "E $s" "$a/$s.every" "$d/chk" "$sp" every
    cc_ "N $s" "$a/$s.rand" "$d/chk" "$sp" rand
    for x in $COMBOS; do off=${x%,*}; cut=${x#*,}; suf=""; [ "$cut" != 0 ] && suf=.cut$cut
      for m in first all; do cc_ "A $s $m off$off cut$cut" "$a/$s.$m$suf" "$d/chka" "$sp" list $m "$off" "$cut"; done; done
    cc_ "A $s rand" "$a/$s.rand" "$d/chka" "$sp" rand
  done
  for s in $(fuzz_subj "$c"); do cc_ "F $s" "$a/$s.fuzz" "$d/chk" "$OUT/subj/$s" fuzz; done
  rm -f "$OUT/tmp/$c.$tag.out" "$OUT/tmp/$c.$tag.err"
}
export -f group ans safe deep_subj fuzz_subj deep_ref deep_one
