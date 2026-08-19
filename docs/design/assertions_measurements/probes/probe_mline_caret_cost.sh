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
    int rep = argc > 4 ? atoi(argv[4]) : 1;   /* inner repeats: a memchr arm is
                                                 below timer resolution at one
                                                 search, which reports 0.000000
                                                 and makes every ratio a lie */
    unsigned char *s = malloc(n ? n : 1);
    for (size_t i = 0; i < n; i++)
        s[i] = ((i + 1) % (size_t)line == 0) ? '\n' : 'a';  /* no 'b' */
    ptrdiff_t caps[8][2];
    double best = 1e9;
    /* volatile SINK: without it gcc -O2 deletes all but the last iteration of
     * the repeat loop (the return value is otherwise dead), and a fast arm
     * reports 0.000000 over 200 searches -- which this probe did on its first
     * run of the non-crossing arm. */
    static volatile int sink;
    int r = 0;
    for (int t = 0; t < trials; t++) {
        struct timespec a, b;
        clock_gettime(CLOCK_MONOTONIC, &a);
        for (int k = 0; k < rep; k++) { r = rx_search(s, n, 0, caps); sink = r; }
        clock_gettime(CLOCK_MONOTONIC, &b);
        double el = ((b.tv_sec-a.tv_sec)+1e-9*(b.tv_nsec-a.tv_nsec)) / rep;
        if (el < best) best = el;
    }
    printf("%.8f %d\n", best, r);
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
printf '%-8s %-14s %-14s %-14s %-10s %s\n' \
    "n" "A (?m)^shape" "B anchored" "C unanch" "A/B" "A growth per doubling"
prev=""
for n in 4000 8000 16000 32000 64000; do
    ta=$("$D/A" $n $LINE 5 | cut -d' ' -f1)
    tb=$("$D/B" $n $LINE 5 | cut -d' ' -f1)
    tc=$("$D/C" $n $LINE 5 | cut -d' ' -f1)
    rat=$(python3 -c "print('%.0fx' % ($ta/$tb) if $tb>0 else 'n/a')")
    g=""
    [ -n "$prev" ] && g=$(python3 -c "print('%.2fx' % ($ta/$prev) if $prev>0 else '')")
    printf '%-8s %-14s %-14s %-14s %-10s %s\n' "$n" "$ta" "$tb" "$tc" "$rat" "$g"
    prev=$ta
done
echo
echo "A growing ~4x per doubling is the O(n^2) signature: ~n/$LINE enterable"
echo "attempts, each scanning O(n). B is flat (start_max = 0, ONE attempt)."
echo "C is flat and fastest: memchr + skip loops, neither of which ENG_ATTEMPT"
echo "emits at all."

# ---------------------------------------------------------------------------
# THE NON-CROSSING ARM (R30 N3). The quadratic above needs a body that can run
# PAST a newline. Most real `(?m)^` patterns do not: `(?m)^ERROR` matches within
# one line, so every attempt dies within a few bytes and the shape is LINEAR.
#
# That arm is the one the memchr('\n') candidate-start mitigation actually
# helps, and the first draft of the design justified the mitigation on the
# QUADRATIC arm instead — where a prefilter helps far less, because the cost
# there is the scanning each attempt does, not the number of attempts.
#
#   D  `^ERROR|\nERROR`  — the (?m)^ERROR shape: ENG_ATTEMPT, n+1 attempts,
#                          each dying in a byte or two. Linear, big constant.
#   E  `ERROR`           — the ENG_UNANCH control: one memchr over the whole
#                          subject. Linear, tiny constant.
#
# The D/E ratio is what a memchr('\n') candidate-start prefilter would close:
# it turns D's "visit every start" into "visit every line start", which is the
# same jump E already gets on its own first byte.
echo
echo "=== NON-CROSSING arm: the case the memchr(newline) mitigation is FOR ==="
build D '^ERROR|\nERROR'
build E 'ERROR'
echo
printf '%-8s %-14s %-14s %s\n' "n" "D (?m)^ERROR" "E unanch" "D/E ratio"
for n in 8000 32000 128000; do
    td=$("$D/D" $n $LINE 5 200 | cut -d' ' -f1)
    te=$("$D/E" $n $LINE 5 200 | cut -d' ' -f1)
    rat=$(python3 -c "print('%.0fx' % ($td/$te) if $te>0 else 'n/a')")
    printf '%-8s %-14s %-14s %s\n' "$n" "$td" "$te" "$rat"
done
echo
echo "D and E are BOTH linear -- the ratio is a constant factor, not a curve."
echo "That constant is the mitigation's target: a newline candidate-start"
echo "prefilter would let D skip line-start to line-start instead of visiting"
echo "every offset. Both arms are timed over 200 inner repeats, because a"
echo "single memchr over 8 KB is below this clock's resolution."

# ---------------------------------------------------------------------------
# [M6.2 WAVE C] THE SAME MEASUREMENT ON THE REAL CONSTRUCT.
#
# Everything above measures `(?m)^` through STAND-INS, because [M6.1] ran on a
# compiler that refused the `m` letter. Wave C built it, so the arms below are
# the patterns themselves — and they are not the same artifacts as their
# stand-ins, which is the point:
#
#   F  `(?m)^ERROR`   — the real non-crossing pattern. Its interior start
#                       state is live ONLY for a newline predecessor, so D63's
#                       candidate-start prefilter applies: one memchr('\n')
#                       between attempts instead of visiting every offset.
#   G  `(?m)^[^b]*b`  — the real crossing pattern, D63's accepted residue.
#                       The prefilter removes attempts, not scanning, and this
#                       shape's cost IS the scanning, so the O(n^2) stands.
#
# The stand-ins get NO prefilter and could not: `\nERROR`'s branch says
# nothing about the byte BEFORE the start, so every predecessor byte seeds a
# live state and the candidate set is all 256. That is why D above is the
# honest "before" number for F rather than a second spelling of it.
echo
echo "=== [M6.2 wave C] THE REAL CONSTRUCT, with D63's prefilter ==="
buildm() {   # $1=tag $2=pattern — same as build(), with the modules enabled
    "$PCREC" --features assertions,modifiers -p rx --no-captures -o "$D/m.c" -- "$2"
    gcc -O2 -I"$D" -o "$D/$1" "$D/drv.c" "$D/m.c"
    eng="ENG_UNANCH (memchr + skips)"
    grep -q 'start_max' "$D/m.c" && eng="ENG_ATTEMPT"
    grep -q 'memchr' "$D/m.c" && eng="$eng + D63 candidate prefilter"
    sm=$(grep -o 'const size_t start_max = [^;]*' "$D/m.c" | head -1 | sed 's/.*= //')
    printf '  %-4s %-22s %-46s %s\n' "$1" "$2" "$eng" "${sm:+start_max=$sm}"
}
buildm F '(?m)^ERROR'
buildm G '(?m)^[^b]*b'

echo
echo "--- NON-CROSSING: F (real, prefiltered) against D (stand-in) and E ---"
printf '%-8s %-14s %-14s %-14s %-10s %s\n' \
    "n" "F (?m)^ERROR" "D stand-in" "E unanch" "D/F" "F/E"
for n in 8000 32000 128000; do
    tf=$("$D/F" $n $LINE 5 200 | cut -d' ' -f1)
    td=$("$D/D" $n $LINE 5 200 | cut -d' ' -f1)
    te=$("$D/E" $n $LINE 5 200 | cut -d' ' -f1)
    r1=$(python3 -c "print('%.0fx' % ($td/$tf) if $tf>0 else 'n/a')")
    r2=$(python3 -c "print('%.0fx' % ($tf/$te) if $te>0 else 'n/a')")
    printf '%-8s %-14s %-14s %-14s %-10s %s\n' "$n" "$tf" "$td" "$te" "$r1" "$r2"
done
echo
echo "D/F is the prefilter's measured effect on the arm it is FOR; F/E is what"
echo "is left against a plain unanchored memchr. The [M6.1] design predicted"
echo "the D/E gap (85-185x) as the mitigation's target."

echo
echo "--- CROSSING: G (real) against A (stand-in). NOT rescued, per D63 ---"
printf '%-8s %-14s %-14s %-10s %s\n' "n" "G (?m)^[^b]*b" "A stand-in" "A/G" "G growth per doubling"
prev=""
for n in 4000 8000 16000 32000 64000; do
    tg=$("$D/G" $n $LINE 5 | cut -d' ' -f1)
    ta=$("$D/A" $n $LINE 5 | cut -d' ' -f1)
    rat=$(python3 -c "print('%.2fx' % ($ta/$tg) if $tg>0 else 'n/a')")
    g=""
    [ -n "$prev" ] && g=$(python3 -c "print('%.2fx' % ($tg/$prev) if $prev>0 else '')")
    printf '%-8s %-14s %-14s %-10s %s\n' "$n" "$tg" "$ta" "$rat" "$g"
    prev=$tg
done
echo
echo "G still grows ~4x per doubling. D63 accepts that explicitly and queues"
echo "DD-7's reverse BOT variant as the sequenced fix; the prefilter removes"
echo "attempts, and this shape's cost is the scanning each surviving attempt"
echo "does. A shipped number, not a discovered one."
