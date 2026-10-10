#!/usr/bin/env bash
# studies/start_landing/guard_timing/run.sh -- [START-LANDING] Q2 (4): the
# landing guard's cost on WELL-FORMED text. For each pattern: compile the
# default artifact (the post-loop skip) and a copy with the guard block deleted
# (the no-guard arm), link both to driver.c, and time find-alls over a
# well-formed UTF-8 subject, the two arms INTERLEAVED per round. Prints
# pattern, matches, guard ns, no-guard ns, ratio. Scratch tier (one box, no
# pinning); the answer counts must agree. Usage: run.sh [OUTDIR]
set -eu
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PCREC="${PCREC:-$ROOT/build/pcrec}"
OUT="${1:-$ROOT/build/scratch/guard_timing}"
mkdir -p "$OUT"
python3 - "$OUT/subject.txt" <<'PY'
import sys, random
random.seed(7)
words = ["alpha", "Ärger", "señor", "naïve", "東京", "Москва", "café", "x", "été", "ζωή", "über", "data"]
out = []
size = 0
while size < 1 << 20:
    w = random.choice(words) + random.choice([" ", ", ", ". ", "\n"])
    out.append(w); size += len(w.encode())
open(sys.argv[1], "wb").write("".join(out).encode())
PY
for pat in '.' '\p{L}+' '[a-zé]+'; do
    rm -rf "$OUT/g" "$OUT/n"; mkdir -p "$OUT/g" "$OUT/n"
    "$PCREC" -e utf8 -p on -o "$OUT/g/on.c" --pattern "$pat"
    grep -q '^#define ON_DFA_START "landing"' "$OUT/g/on.c" || { echo "SKIP $pat: not landing"; continue; }
    cp "$OUT/g/on.h" "$OUT/n/on.h"
    python3 - "$OUT/g/on.c" "$OUT/n/on.c" <<'PY'
import sys
s = open(sys.argv[1]).read()
a = s.index("    {\n        unsigned landing_cp;")
b = s.index("\n    }\n", s.index("                   !", a)) + len("\n    }\n")
assert "landing_cp" in s[a:b]
open(sys.argv[2], "w").write(s[:a] + s[b:])
PY
    for arm in g n; do
        gcc -O2 -I"$OUT/$arm" -o "$OUT/drv_$arm" "$ROOT/studies/start_landing/guard_timing/driver.c" "$OUT/$arm/on.c"
    done
    gs=""; ns=""; gc=""; nc=""
    for r in 1 2 3 4 5; do
        set -- $("$OUT/drv_g" "$OUT/subject.txt" 3 3); gc=$1; gs="$gs $2"
        set -- $("$OUT/drv_n" "$OUT/subject.txt" 3 3); nc=$1; ns="$ns $2"
    done
    [ "$gc" = "$nc" ] || { echo "ANSWER MISMATCH $pat: $gc vs $nc"; exit 1; }
    python3 - "$pat" "$gc" "$gs" "$ns" <<'PY'
import sys, statistics as st
p, c, g, n = sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[3].split()], [float(x) for x in sys.argv[4].split()]
gm, nm = st.median(g), st.median(n)
print(f"{p}\tmatches={c}\tguard_ns={gm:.0f}\tnoguard_ns={nm:.0f}\tratio={gm/nm:.4f}\tspread_g={min(g):.0f}-{max(g):.0f}\tspread_n={min(n):.0f}-{max(n):.0f}")
PY
done
