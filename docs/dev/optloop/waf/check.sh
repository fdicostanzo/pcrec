#!/bin/sh
# check.sh BASE.c TWIN.c SUBJECT... -- answer identity of a wafread twin
# against its base artifact (span for span, every subject). Prints one
# line per subject and exits 1 on any difference. No timing.
set -e
BASE=$1; TWIN=$2; shift 2
D=$(mktemp -d); HERE=$(cd "$(dirname "$0")" && pwd)
H=${BASE%.c}.h
cp "$H" "$D/art.h"
CC=${CC:-gcc}
$CC -O2 -I"$D" -I"$(dirname "$BASE")" -o "$D/base" "$HERE/spans.c" "$BASE"
$CC -O2 -I"$D" -I"$(dirname "$BASE")" -o "$D/twin" "$HERE/spans.c" "$TWIN"
rc=0
for S in "$@"; do
  "$D/base" "$S" > "$D/b.out"; "$D/twin" "$S" > "$D/t.out"
  if cmp -s "$D/b.out" "$D/t.out"; then echo "SAME $(tail -1 "$D/b.out") $S"
  else echo "DIFF base $(tail -1 "$D/b.out") twin $(tail -1 "$D/t.out") $S"; rc=1; fi
done
rm -rf "$D"; exit $rc
