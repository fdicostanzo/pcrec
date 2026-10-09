#!/bin/sh
# walk_survey: INSTRUMENT VALIDATION (before any population number is read).
#   PCREC=build/pcrec ./validate.sh > results/validation.txt
# 1 a KNOWN GRATUITOUS walk: \d+$ on 1 MiB (today: forward whole subject +
#   reverse over the match) -- must read ~n bytes against a 6-byte answer;
# 2 its [OPT-REVEND] form-C hand-twin (studies/revend_twin/mktwin.py): the
#   same answer from ~the match alone -- the instrument must SEE the drop;
# 3 KNOWN TIGHT walks: ^abc (start-anchored) must read ~3 bytes of 1 MiB;
#   abc with its one match at the end reads ~n (the forward lower bound);
# 4 PLANTED CONTROLS (the failing direction): ^abc's artifact with one extra
#   forward pass over [search_from, n) planted at the head of rx_search, and
#   one with the reverse block run twice -- each must show the extra bytes;
# 6 THE CLASS MEASURES RESPOND: K4's land_rev on \w+ (artifact vs the
#   landtwin.py twin, which must read 0) and K5's A_pre on (?i)cat over
#   lowercase text (the folded gate vs -fno-req-run-fold, which must read 0);
# 5 AN INDEPENDENT COUNT: gcc --coverage (gcov) line counts of \d+$'s
#   forward-step and reverse-step lines, against the instrument's T_fwd and
#   T_rev on the same subject (one subject byte per step).
set -e
cd "$(dirname "$0")"
H=$PWD; W=$H/work/val; rm -rf "$W"; mkdir -p "$W"
P=${PCREC:?}; P=$(cd "$(dirname "$P")" && pwd)/$(basename "$P")
python3 - "$W" <<'PY'
import sys
w = sys.argv[1]
body = (b"the quick brown fox jumps over the lazy dog, " * 30000)[:1 << 20]
open(w + "/end_digits", "wb").write(body[:-6] + b" 12345")
open(w + "/abc_end", "wb").write(body[:-4] + b" abc")
open(w + "/abc_start", "wb").write(b"abc" + body[3:])
PY
show() {  # dir subject mode
    "$1/bin" "$1/map" "$3" 0 "$W/$2" | python3 -c '
import sys
h, v = [l.rstrip("\n").split("\t") for l in sys.stdin][:2]
d = dict(zip(h, v))
ph = ["pre", "skip", "fwd", "rev", "anc", "vm", "endw", "misc", "unk"]
print("  %-10s n=%s rc=%s span=[%s,%s) T=%s U=%s T_scan=%s ahead=%s | %s" % (d["subject"], d["n"], d["rc"], d["s"], d["e"],
      d["T"], d["U"], d["T_scan"], d["ahead"], " ".join("%s=%s/%s" % (p, d["T_" + p], d["U_" + p]) for p in ph if d["T_" + p] != "0")))'
}
echo "== 1 known gratuitous: \\d+\$ (today's artifact)"
python3 wsbuild.py "$P" "$W/end" --pattern '\d+$' >/dev/null
show "$W/end" end_digits search
echo "== 2 the same pattern, [OPT-REVEND] form-C twin (walk only)"
TWIN_FORM=walk python3 ../revend_twin/mktwin.py "$W/end/rx.c" "$W/twin.c" rx 1
WS_SRC="$W/twin.c" WS_HDR="$W/end/rx.h" python3 wsbuild.py "$P" "$W/twin" >/dev/null
show "$W/twin" end_digits search
echo "== 3 known tight: ^abc on abc_start / abc_end; abc on abc_end"
python3 wsbuild.py "$P" "$W/anc" --pattern '^abc' >/dev/null
show "$W/anc" abc_start search
show "$W/anc" abc_end search
python3 wsbuild.py "$P" "$W/lit" --pattern 'abc' >/dev/null
show "$W/lit" abc_end search
echo "== 4 planted controls on ^abc (must each show ~n extra bytes)"
python3 - "$W" <<'PY'
import re, sys
w = sys.argv[1]
src = open(w + "/anc/rx.c").read()
head = re.search(r"\nint rx_search\(.*?\)\n\{\n", src, re.S)
assert head, "rx_search head not found"
plant = ("    { volatile unsigned char rx_planted = 0; size_t rx_i;\n"
         "      for (rx_i = search_from; rx_i < subject_length; rx_i++) rx_planted ^= subject[rx_i]; }\n")
open(w + "/plant1.c", "w").write(src[:head.end()] + plant + src[head.end():])
# control 2: the same planted pass written as a REVERSE walk from the end
plant2 = ("    { volatile unsigned char rx_planted = 0; size_t rx_i;\n"
          "      for (rx_i = subject_length; rx_i > search_from; rx_i--) rx_planted ^= subject[rx_i - 1]; }\n")
open(w + "/plant2.c", "w").write(src[:head.end()] + plant2 + src[head.end():])
PY
for k in 1 2; do
  WS_SRC="$W/plant$k.c" WS_HDR="$W/anc/rx.h" python3 wsbuild.py "$P" "$W/plant$k" >/dev/null
  show "$W/plant$k" abc_start search
done
echo "== 6 class measures respond (K4 land_rev, K5 A_pre): artifact vs the twin/arm that removes the walk"
"$P" -p rx -o "$W/w.c" --pattern '\w+' && python3 landtwin.py "$W/w.c" "$W/wtwin.c"
python3 wsbuild.py "$P" "$W/wo" --pattern '\w+' >/dev/null
sed 's/#include "w.h"/#include "rx.h"/' "$W/wtwin.c" > "$W/wtwin2.c"
WS_SRC="$W/wtwin2.c" WS_HDR="$W/wo/rx.h" python3 wsbuild.py "$P" "$W/wt" >/dev/null
python3 - "$W" <<'PY'
import sys
w = sys.argv[1]
open(w + "/words", "wb").write((b"alpha beta, gamma delta. epsilon zeta eta theta " * 1400)[:65536])
open(w + "/catlow", "wb").write((b"the cat sat on a mat. " * 3000)[:65536])
PY
for d in wo wt; do "$W/$d/bin" "$W/$d/map" findall 0 "$W/words" | python3 -c '
import sys
h, v = [l.rstrip("\n").split("\t") for l in sys.stdin][:2]; d = dict(zip(h, v))
print("  %-3s \\w+ findall words n=%s nmatch=%s T=%s T_rev=%s land_rev=%s land_calls=%s" % (sys.argv[1], d["n"], d["nmatch"], d["T"], d["T_rev"], d["land_rev"], d["land_calls"]))' $d; done
python3 wsbuild.py "$P" "$W/fold" --pattern '(?i)cat' >/dev/null
python3 wsbuild.py "$P" "$W/nofold" -fno-req-run-fold --pattern '(?i)cat' >/dev/null
for d in fold nofold; do "$W/$d/bin" "$W/$d/map" findall 0 "$W/catlow" | python3 -c '
import sys
h, v = [l.rstrip("\n").split("\t") for l in sys.stdin][:2]; d = dict(zip(h, v))
print("  %-6s (?i)cat findall catlow n=%s nmatch=%s T=%s T_pre=%s A_pre=%s" % (sys.argv[1], d["n"], d["nmatch"], d["T"], d["T_pre"], d["A_pre"]))' $d; done
echo "== 5 independent count: gcov line counts vs the instrument (\\d+\$, end_digits)"
mkdir -p "$W/gcov" && cp "$W/end/rx.c" "$W/end/rx.h" "$W/gcov/"
( cd "$W/gcov" && gcc -O0 --coverage -c rx.c -o rx.o && gcc -O0 --coverage -I. "$H/fatime.c" rx.o -o fat \
  && ./fat "$W/end_digits" search 1 >/dev/null && gcov rx.c >/dev/null )
f=$(ls "$W"/gcov/*rx.c.gcov | head -1)
fw=$(grep -E 'forward_step\(rx_forward_next_state.*subject\[scan_position\+\+\]' "$f" | awk -F: '{gsub(/ /,"",$1); s+=$1} END{print s+0}')
sk=$(grep -E 'rx_can_begin_match\[subject\[scan_position\]\]' "$f" | awk -F: '{gsub(/ /,"",$1); s+=$1} END{print s+0}')
rv=$(grep -E 'reverse_step\(.*subject\[--rewind_position\]' "$f" | awk -F: '{gsub(/ /,"",$1); s+=$1} END{print s+0}')
echo "  gcov: forward-step line executions=$fw  skip-loop line executions=$sk  reverse-step line executions=$rv"
echo "  (a skip-loop line execution is one loop test: one subject load per test that reaches the load)"
