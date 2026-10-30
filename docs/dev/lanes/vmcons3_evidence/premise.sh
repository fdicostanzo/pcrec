#!/bin/bash
# PREMISE TEST (brief): r8 SOUND-6's twin reproduces under rev 2's rule as
# written. A conditional fail typed FAIL passes rev 2's signature, and the
# slot-flow rounds then delete group 1's live SETs.
# usage: PCREC=<merged build/pcrec> S=<scratch dir> premise.sh
set -u
E=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$S"
"$PCREC" -p rx --features all -o "$S/mt.c" --pattern '^(a)b+c' || exit 1
grep -n 'goto rx_fail;' "$S/mt.c" | grep -E 'span_cursor <|PRUNE_TOO_SHORT' | while IFS= read -r l; do
    t=${l#*:}
    for k in FAIL BRANCH_FAIL; do python3 -I "$E/sig_rev2.py" rx $k "$t"; done
done
# The twin: what V3 does once both conditional fails end every path (FAIL:
# "path ends"): group 1's two SETs have no read after them, so both go.
grep -v 'RX_SET(RX_SLOT_GROUP1_' "$S/mt.c" > "$S/mt_twin.c"
diff "$S/mt.c" "$S/mt_twin.c"
for n in mt mt_twin; do echo "== $n"; "$E/run.sh" "$S" $n "$S/$n.c" abbc abc ac; done
gcc -O1 -w -o "$S/p2" "$E/p2.c" -lpcre2-8 && { echo "== libpcre2"; "$S/p2" '^(a)b+c' '' abbc abc ac; }
