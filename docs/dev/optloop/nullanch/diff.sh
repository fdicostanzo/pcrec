#!/bin/bash
# [NULLABLE-ANCH] STEP 0 answer differential: default vs -fprefilter twin.
# usage: diff.sh PCREC_BIN SCRATCH_DIR     (single core, light)
set -u
HERE=$(cd "$(dirname "$0")" && pwd); PCREC=$1; S=$2; mkdir -p "$S"; S=$(cd "$S" && pwd); cd "$S" || exit 2
# pattern ; alphabet ; maxlen ; ncaps(RX_NCAPS of the default compile)
while IFS=$'\t' read -r pat alpha maxlen; do
  [ -z "$pat" ] && continue
  "$PCREC" -p da --features all -o da.c --pattern "$pat" || { echo "REFUSED $pat"; continue; }
  "$PCREC" -p db --features all -fprefilter -o db.c --pattern "$pat" || { echo "REFUSED-fprefilter $pat"; continue; }
  nc=$(grep -m1 -E '^#define DA_NCAPS ' da.h | awk '{print $3}')
  eng=$(grep -m1 -E '^#define DB_VM_PREFILTER ' db.c | awk '{print $3}')
  sel=$(grep -m1 -E '^#define DA_ENGINE_SEL ' da.c | awk '{print $3}')
  gcc -O1 -DNCAPS="$nc" -DALPHA="\"$alpha\"" -DMAXLEN="$maxlen" -o dd "$HERE/diff_driver.c" da.c db.c 2>&1 | head -3
  printf '%s\t[%s]\tda_sel=%s\tdb_prefilter=%s\t' "$pat" "$alpha" "$sel" "$eng"
  gnutimeout 300 ./dd | tail -1
done <<'LIST'
^(([a-z]+)*)+$	ab!	10
^(\s+)*$	 x	12
^(a|b*)*$	abc	9
^(\s*\w*)*$	 a!	9
^(a?)(?1)*$	ab	12
^(a{2,4})?$	ab	12
^(?:(?<g>a?)){0}(?&g)*+$	ab	12
^(a*)*$	ab	12
^(a*)+$	ab	12
^(x?)*$	x	8
^((a)|b*)*$	ab	10
\A(a*)*\z	ab	12
^(a*)*$	a\n	12
^(\s+)*$	 \nx	10
^(a|\n)*$	a\nb	10
LIST
