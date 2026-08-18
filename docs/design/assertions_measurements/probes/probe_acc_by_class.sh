#!/bin/sh
# [M6.1] What does a NEXT-BYTE-SENSITIVE accept flag cost the hot loop?
#
# `\b` and `(?m)$` are true or false depending on the byte at `pos`, so the
# forward loop's `if (<p>_facc[st]) last = pos;` (src/gen/emit_dfa.c:961) has to
# become a states x ncls lookup indexed by the class of that byte. This measures
# the difference, and it measures it on an ANSWER-PRESERVING variant: every row
# of the wider table is that state's old bit, so the two artifacts report the
# same matches and any difference in time is the lookup and nothing else.
#
# The pattern is `[01]*1[01]{8}` because D11 measured the shipped loop on it and
# because it has a real skip loop -- the ordering hazard D11 rule 2 records.
#
# Usage: probe_acc_by_class.sh PCREC_BIN WORKDIR [TRIALS]
set -e
PCREC=$1; D=$2; T=${3:-5}
mkdir -p "$D"
PAT='[01]*1[01]{8}'
"$PCREC" -p rx --no-captures -o "$D/hp.c" -- "$PAT"

python3 - "$D" <<'EOF'
import re, sys
d = sys.argv[1]
src = open(d + '/hp.c').read()
m = re.search(r"static const unsigned char rx_facc\[(\d+)\] = \{(.*?)\};", src, re.S)
n = int(m.group(1)); vals = [int(x) for x in re.findall(r"\d+", m.group(2))]
assert len(vals) == n
ncls = int(re.search(r"rx_ftr\[(\d+)\]", src).group(1)) // n
tbl = ", ".join(str(vals[i]) for i in range(n) for _ in range(ncls))
b = src.replace(m.group(0), m.group(0) +
    "\n    static const unsigned char rx_facc2[%d] = { %s };\n" % (n * ncls, tbl))
old = "        if (rx_facc[st]) last = pos;\n"
new = ("        if (rx_facc2[st * %d + (pos < n ? rx_fcls[s[pos]] : 0)]) "
       "last = pos;\n" % ncls)
assert old in b
open(d + '/hp_b.c', 'w').write(b.replace(old, new, 1))
print("ncls=%d states=%d" % (ncls, n))
EOF

cat > "$D/drv.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "hp.h"
int main(int argc, char **argv) {
    size_t n = 8u << 20;
    unsigned char *s = malloc(n);
    unsigned seed = 12345;
    for (size_t i = 0; i < n; i++) { seed = seed*1103515245u+12345u; s[i] = "01x"[(seed>>16)%3]; }
    int trials = atoi(argv[1]);
    double best = 1e9;
    long cnt0 = -1;
    for (int t = 0; t < trials; t++) {
        struct timespec a,b; clock_gettime(CLOCK_MONOTONIC,&a);
        size_t p = 0; long cnt = 0; ptrdiff_t caps[8][2];
        while (p <= n) { if (rx_search(s,n,p,caps)!=1) break; cnt++;
            p = caps[0][1] > caps[0][0] ? (size_t)caps[0][1]
                                        : rx_next_pos(s,n,(size_t)caps[0][0]); }
        clock_gettime(CLOCK_MONOTONIC,&b);
        double el = (b.tv_sec-a.tv_sec)+1e-9*(b.tv_nsec-a.tv_nsec);
        if (el < best) best = el;
        cnt0 = cnt;
    }
    printf("%.4f s  %.1f MB/s  matches=%ld\n", best, (n/1048576.0)/best, cnt0);
    return 0;
}
EOF
cp "$D/hp.h" "$D/hp_b.h"
sed 's/hp\.h/hp_b.h/' "$D/drv.c" > "$D/drv_b.c"
gcc -O2 -I"$D" -o "$D/a" "$D/drv.c"   "$D/hp.c"
gcc -O2 -I"$D" -o "$D/b" "$D/drv_b.c" "$D/hp_b.c"
echo "pattern: $PAT   (best of $T, three repetitions of the pair)"
i=0
while [ $i -lt 3 ]; do
    printf 'A facc[st]              '; "$D/a" "$T"
    printf 'B facc2[st*ncls+cls]    '; "$D/b" "$T"
    i=$((i+1))
done
