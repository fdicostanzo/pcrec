#!/bin/bash
# split_size.sh PCREC BENCH_REPO WORKDIR — [OPT-ATTEMPT-SPLIT]'s size, compile-only, no clock.
# Compiles wild-waf-crs-942360-concat-sqli (the full pattern), the exact twin's two halves
# (dfa/twins/mk_split.py: u = the four ^-free arms unanchored, a = the ^ arm) and reports
# .c bytes, .o bytes (gcc -O2 -c; text+data) and the route stamps. The row's construction
# is original + u (ONE attempt of the original at search_from, then ENG_UNANCH without the
# ^ arms); the twin's is a + u.
set -e
H=$(dirname "$0"); PC=$1; BR=$2; W=$3; mkdir -p "$W"
P=$BR/bench/capability/patterns/wild-waf-crs-942360-concat-sqli.rx
python3 -I $H/../dfa/twins/mk_split.py $P $W
for n in full u a; do
  case $n in full) f=$P;; u) f=$W/u.rx;; a) f=$W/a.rx;; esac
  gnutimeout 300 $PC -p rx --features all -o $W/$n.c --pattern-esc --pattern "$(python3 -I $H/esc.py $f)"
  gcc -O2 -c -I$W $W/$n.c -o $W/$n.o
  echo "== $n  .c=$(wc -c < $W/$n.c)  $(size $W/$n.o | tail -1 | awk '{printf ".text=%s .data=%s .o_total=%s",$1,$2,$4}')"
  grep -E "define RX_(ENGINE|DFA_SCAN|DFA_PREFILTER|DFA_TABLE|DFA_SCAN_EDGE) " $W/$n.c | tr '\n' ' '; (grep -m1 'start_max' $W/$n.c || echo)
done
python3 -I - $W <<'P'
import os, subprocess, sys
W = sys.argv[1]
def sz(n): return int(subprocess.check_output("size %s/%s.o | tail -1 | awk '{print $4}'" % (W, n), shell=True))
def cb(n): return os.path.getsize("%s/%s.c" % (W, n))
f, u, a = sz("full"), sz("u"), sz("a")
print(".o  row construction (original + u): %d = %.3fx of original %d" % (f + u, (f + u) / f, f))
print(".o  exact twin (a + u):              %d = %.3fx of original" % (a + u, (a + u) / f))
f, u, a = cb("full"), cb("u"), cb("a")
print(".c  row construction (original + u): %d = %.3fx of original %d" % (f + u, (f + u) / f, f))
print(".c  exact twin (a + u):              %d = %.3fx of original" % (a + u, (a + u) / f))
P
