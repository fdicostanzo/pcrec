#!/usr/bin/env bash
# confirm_prep.sh -- [ARTREV] S4 confirmer prep: rebuild the four pilot artifact roots from the pin and
# import the reviewers' FINAL sealed twins as arms, ready for `identity` and `time`.
#
#   confirm_prep.sh PCREC ROOT
#
# PCREC  a pcrec binary that regenerates the pin's artifacts BYTE-IDENTICALLY (checked below against
#        docs/dev/optloop/artrev/pilot_pins.tsv; main's build/pcrec at abi 62 does).
# ROOT   becomes ARTREV_ROOT: ROOT/<artifact name>/{artifact.c,arms/orig,arms/orig2,arms/<twin arms>}.
# Arms: A01 -> L1..L4; A07 -> a_L1..a_L6 (rvA07a) and b_L1..b_L6 (rvA07b, L4 = its r2); A09 -> L1..L6
# (L1 = r2, L4 = r3).  The highest revision of each lead wins.  Twins are imported with --control
# (uncounted: the confirmer's ledger is fresh and A07 carries 12 leads).  Controls (ctl*) and null.* are
# NOT imported; `null` is made with `twin NAME null --null`.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
TREE=$(cd "$HERE/../.." && pwd)
PCREC=$1; ROOT=$2
D=$TREE/docs/dev/optloop/artrev
export ARTREV_CC=${ARTREV_CC:-gcc-16} ARTREV_ROOT=$ROOT
A="python3 -B $HERE/artrev.py"
mkdir -p "$ROOT"
declare -a LOG
gen_one() {  # NAME PATTERN_HEX FLAGS PREFIX WANT_SHA
  local name=$1 phex=$2 flags=$3 prefix=$4 want=$5
  python3 -c "import sys,binascii;sys.stdout.buffer.write(binascii.unhexlify('$phex'))" > "$ROOT/.pat_$name"
  $A gen "$name" --pcrec "$PCREC" --pattern-file "$ROOT/.pat_$name" --flags="$flags" --prefix "$prefix" --pin "$(awk -F'\t' -v n="$name" '$3==n{print $8; exit}' "$D/pilot_pins.tsv")" --force >/dev/null
  got=$(python3 -c "import json;print(json.load(open('$ROOT/$name/meta.json'))['artifact_sha256'])")
  [ "$got" = "$want" ] || { echo "PIN MISMATCH for $name: regenerated $got, pin has $want -- this pcrec does not reproduce the pilot artifact; twins would not apply" >&2; exit 3; }
  echo "$name: regenerated, sha256 $got matches the pin"
  $A twin "$name" null --null >/dev/null
}
import_twins() {  # NAME PREFIX_FOR_ARM DIR[,DIR]
  local name=$1 pre=$2 dirs=$3
  for lead in $(ls ${dirs//,/ } 2>/dev/null | sed -n 's/^\(L[0-9]*\)\.r[0-9]*\.patch$/\1/p' | sort -u); do
    best=""; bestr=0
    for d in ${dirs//,/ }; do for p in "$d/$lead".r*.patch; do [ -f "$p" ] || continue
      r=${p##*.r}; r=${r%.patch}; [ "$r" -gt "$bestr" ] && { bestr=$r; best=$p; }
    done; done
    $A twin "$name" "${pre}${lead}" --patch "$best" --control >/dev/null
    echo "$name: arm ${pre}${lead} <- $(basename "$best")"
  done
}
tab=$(printf '\t')
while IFS="$tab" read -r id cell name phex flags prefix sha pin abi eng ncaps havein ccv; do
  [ "$id" = id ] && continue
  case "$cell" in rvA07b) continue;; esac           # A07 is one artifact: rvA07a's row builds it, both reviewers' twins import into it
  gen_one "$name" "$phex" "$flags" "$prefix" "$sha"
  case "$id" in
    A01) import_twins "$name" "" "$D/A01/twins";;
    A07) import_twins "$name" "a_" "$D/A07a"; import_twins "$name" "b_" "$D/A07b";;
    A09) import_twins "$name" "" "$D/A09/twins";;
  esac
done < "$D/pilot_pins.tsv"
echo "confirm_prep: roots under $ROOT"
