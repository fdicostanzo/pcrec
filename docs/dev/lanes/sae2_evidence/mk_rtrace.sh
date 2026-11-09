#!/usr/bin/env bash
# mk_rtrace.sh REV OUTDIR -- span_arms unit E2's R-SPAN INSTRUMENT (§4.3, r1 F11):
# a SCRATCH build of revision REV with one stderr trace line added to the window
# statement's R span (src/gen/emit_dfa.c `pf_window_of`), under
# PCREC_RSPAN_TRACE=1:
#   RSPAN <offset> <len> <TT/KK per position>
# one line per stated R span (the parked and the reseed alternatives each). The
# patch lives only in OUTDIR (under the temp root); nothing is committed with
# it. census_e2.py reads it to count R-span movers beside run movers.
set -eu
REV=$1 OUT=$2
REPO=/home/pcrec/projects/pcrec
rm -rf "$OUT"; mkdir -p "$OUT"
git -C "$REPO" archive "$REV" | tar -x -C "$OUT"
python3 -I - "$OUT/src/gen/emit_dfa.c" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
anchor = "    *out = a;\n    return n;\n"
assert s.count(anchor) == 1, "pf_window_of anchor moved"
trace = ('    if (getenv("PCREC_RSPAN_TRACE"))\n'
         '        for (int i = 0; i < 2; i++) {\n'
         '            if (!rsp[i]) continue;\n'
         '            fprintf(stderr, "RSPAN\\t%d\\t%d\\t", w + lo, hi - lo);\n'
         '            for (int j = lo; j < hi; j++) fprintf(stderr, "%02x/%02x", r->bytes[j], r->mask[j]);\n'
         '            fprintf(stderr, "\\n");\n'
         '        }\n')
open(p, "w").write(s.replace(anchor, trace + anchor))
PY
nice make -C "$OUT" -j4 build/pcrec > "$OUT/build.log" 2>&1
echo "rtrace build of $REV: $OUT/build/pcrec"
