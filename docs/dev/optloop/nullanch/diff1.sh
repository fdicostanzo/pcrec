#!/bin/bash
# [NULLABLE-ANCH] BUILD answer differential (lane nullanch1): REF default vs
# NEW default, every subject to MAXLEN over ALPHA, every start offset.
# ALPHA is printf %b text; keep a `\n` away from its END (command
# substitution strips a trailing newline).
# usage: diff1.sh REF_PCREC NEW_PCREC SCRATCH_DIR     (single core, light)
set -u
HERE=$(cd "$(dirname "$0")" && pwd); REF=$1; NEW=$2; S=$3; mkdir -p "$S"; S=$(cd "$S" && pwd); cd "$S" || exit 2
while IFS=$'\t' read -r pat alpha maxlen; do
  [ -z "$pat" ] && continue
  alpha=$(printf '%b' "$alpha")
  "$REF" -p da --features all -o da.c --pattern "$pat" || { echo "REFUSED-ref $pat"; continue; }
  "$NEW" -p db --features all -o db.c --pattern "$pat" || { echo "REFUSED-new $pat"; continue; }
  nc=$(grep -m1 -E '^#define DA_NCAPS ' da.h | awk '{print $3}')
  sa=$(grep -m1 -E '^#define DA_ENGINE_SEL ' da.c | awk '{print $3}')
  sb=$(grep -m1 -E '^#define DB_ENGINE_SEL ' db.c | awk '{print $3}')
  pb=$(grep -m1 -E '^#define DB_VM_PREFILTER ' db.c | awk '{print $3}')
  gcc -O1 -DNCAPS="$nc" -DALPHA="\"$(printf '%s' "$alpha" | sed 's/\\/\\\\/g; s/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')\"" -DMAXLEN="$maxlen" -o dd "$HERE/diff1_driver.c" da.c db.c 2>&1 | head -3
  printf '%s\t[%s]\tref=%s\tnew=%s/%s\t' "$pat" "$(printf '%s' "$alpha" | sed ':a;N;$!ba;s/\n/\\n/g')" "$sa" "$sb" "$pb"
  gnutimeout 1800 ./dd | tail -1
done <<'LIST'
^(([a-z]+)*)+$	a\n!	11
^(\s+)*$	 \nx	12
^(a{2,4})?$	a\nb	12
^(a?)(?1)*$	a\nb	12
^(?:(?<g>a?)){0}(?&g)*+$	a\nb	12
^(a*)*$	a\nb	11
\A(a*)*\z	a\nb	11
^(a*)*	a\nb	11
(a*)*$	a\nb	11
(?m)^(a*)*$	a\nb	11
LIST
