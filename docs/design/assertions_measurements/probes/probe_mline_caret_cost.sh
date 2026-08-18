#!/bin/sh
# [M6.1]/R30 E2 — what routing `(?m)^` to ENG_ATTEMPT actually costs.
#
# The design's first draft said `(?m)^` "inherits D8's known-slow shape and
# nothing else changes". R30 refuted that twice over, and this reproduces the
# refutation on the shipped compiler rather than taking it on report.
#
# WHY THESE PATTERNS. pcrec cannot compile `(?m)^` yet, so the cost is measured
# on the ENGINE SHAPE `(?m)^` would produce, spelled in syntax pcrec compiles
# today:
#   A  `^[^b]*b|\n[^b]*b`  — the (?m)^ shape: `^` on SOME branch, so the
#                            interior start state s1 is LIVE and `start_max`
#                            is `n` (src/gen/emit_dfa.c:1105-1108). ENG_ATTEMPT
#                            with n+1 attempts and, because that engine emits
#                            neither a prefilter nor skip loops, zero scan
#                            avoidance.
#   B  `^[^b]*b`           — the ANCHORED twin: fully `^`-anchored, so
#                            `d->s1 < 0` and `start_max` is the literal 0
#                            (M2.1's fast path). This is what plain `^` gets
#                            and what the struck sentence assumed `(?m)^`
#                            would.
#   C  `[^b]*b`            — the ENG_UNANCH control: same language shape, no
#                            anchor, so it keeps memchr + skip loops.
#
# WHY THE SUBJECT HAS NEWLINES, and this is the probe's own first finding. An
# all-'a' subject measures NOTHING: with no '\n' present, every interior
# attempt of A dies on its first byte, so A is O(n) and looks fine. The
# quadratic needs the interior branch to be ENTERABLE — one '\n' per line —
# which is exactly the subject a real `(?m)^` pattern runs on. A first draft of
# this probe used all-'a' and measured a flat line; that draft would have
# reported the design's struck sentence as CORRECT.
#
# Subject: lines of 'a' separated by '\n', NO 'b' anywhere, so every attempt
# that can start does start and runs to the end of the subject.
#
# Usage: probe_mline_caret_cost.sh PCREC_BIN WORKDIR [LINELEN]
set -e
PCREC=$1; D=$2; LINE=${3:-16}
mkdir -p "$D"

cat > "$D/drv.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "m.h"
int main(int argc, char **argv) {
    size_t n = (size_t)atol(argv[1]);
    int line = atoi(argv[2]), trials = atoi(argv[3]);
    unsigned char *s = malloc(n ? n : 1);
    for (size_t i = 0; i < n; i++)
        s[i] = ((i + 1) % (size_t)line == 0) ? '\n' : 'a';  /* no 'b' */
    ptrdiff_t caps[8][2];
    double best = 1e9;
    int r = 0;
    for (int t = 0; t < trials; t++) {
        struct timespec a, b;
        clock_gettime(CLOCK_MONOTONIC, &a);
        r = rx_search(s, n, 0, caps);
        clock_gettime(CLOCK_MONOTONIC, &b);
        double el = (b.tv_sec-a.tv_sec)+1e-9*(b.tv_nsec-a.tv_nsec);
        if (el < best) best = el;
    }
    printf("%.6f %d\n", best, r);
    return 0;
}
EOF

build() {   # $1=tag $2=pattern
    "$PCREC" -p rx --no-captures -o "$D/m.c" -- "$2"
    gcc -O2 -I"$D" -o "$D/$1" "$D/drv.c" "$D/m.c"
    eng="ENG_UNANCH (memchr + skips)"
    grep -q 'start_max' "$D/m.c" && eng="ENG_ATTEMPT (no prefilter, no skips)"
    sm=$(grep -o 'const size_t start_max = [^;]*' "$D/m.c" | head -1 | sed 's/.*= //')
    printf '  %-4s %-22s %-34s %s\n' "$1" "$2" "$eng" "${sm:+start_max=$sm}"
}

echo "=== the three shapes, and what the emitter did with each ==="
build A '^[^b]*b|\n[^b]*b'
build B '^[^b]*b'
build C '[^b]*b'

echo
echo "=== best-of-5 time (s) for ONE search; subject = lines of 'a' (len $LINE), no 'b' ==="
printf '%-8s %-13s %-13s %-13s %-10s %s\n' \
    "n" "A (?m)^shape" "B anchored" "C unanch" "A/B" "A growth per doubling"
prev=""
for n in 4000 8000 16000 32000 64000; do
    ta=$("$D/A" $n $LINE 5 | cut -d' ' -f1)
    tb=$("$D/B" $n $LINE 5 | cut -d' ' -f1)
    tc=$("$D/C" $n $LINE 5 | cut -d' ' -f1)
    rat=$(python3 -c "print('%.0fx' % ($ta/$tb) if $tb>0 else 'n/a')")
    g=""
    [ -n "$prev" ] && g=$(python3 -c "print('%.2fx' % ($ta/$prev) if $prev>0 else '')")
    printf '%-8s %-13s %-13s %-13s %-10s %s\n' "$n" "$ta" "$tb" "$tc" "$rat" "$g"
    prev=$ta
done
echo
echo "A growing ~4x per doubling is the O(n^2) signature: ~n/$LINE enterable"
echo "attempts, each scanning O(n). B is flat (start_max = 0, ONE attempt)."
echo "C is flat and fastest: memchr + skip loops, neither of which ENG_ATTEMPT"
echo "emits at all."
