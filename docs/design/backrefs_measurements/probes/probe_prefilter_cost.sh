#!/bin/sh
# [M6.5.1] charter (f) -- WHAT VM-ONLY SEARCH COSTS, MEASURED IN-PCREC.
#
# The design rules that an UNEXPANDED backreference pattern searches on the
# VM with NO DFA prefilter, because a backref-erased approximation is a
# SUPERSET language and engine_m4.md 6.1's hybrid needs an EXACT anchored
# window, not an over-approximating one. That ruling has a price, and this
# probe is the price.
#
# WHY IT IS AN EXACT MEASUREMENT AND NOT A PROXY. pcrec cannot compile a
# backreference, so the obvious probe -- time a backref pattern with and
# without a prefilter -- cannot be written. But the prefilter is a SEPARATE
# axis from the construct: `--engine=vm` stamps `RX_VM_PREFILTER "none"`
# while the default `auto` stamps `"hybrid"` for the SAME capture-bearing
# pattern (src/opt/select_engine.c's prefilter block). So both arms compile
# the IDENTICAL pattern text with the IDENTICAL engine, and the only
# difference is the prefilter -- which is exactly the difference the ruling
# makes. The patterns are real backref idioms with the backreference
# ERASED, so the automaton being searched is the one a backref pattern's
# body actually has.
#
# WHAT IT DOES NOT MEASURE, said plainly: the VM work the backref COMPARE
# itself adds. That work is proportional to the captured length and is
# present in both worlds; the prefilter axis is the one the ruling moves.
#
# THE SUBJECT IS A NO-MATCH SUBJECT ON PURPOSE. A prefilter's whole value
# is answering `nomatch` at DFA speed without the VM ever running
# (engine_m4.md 4.7). A subject that matches early measures neither arm's
# scanning. Both a NO-MATCH and a LATE-MATCH subject are run, because the
# two answer different questions and reporting only the first would
# overstate the loss.
#
# Usage: probe_prefilter_cost.sh PCREC_BIN WORKDIR [SUBJECT_KB]
set -e
PCREC=$1; D=$2; KB=${3:-256}
mkdir -p "$D"

cat > "$D/drv.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "m.h"
/* argv: n  mode(0=nomatch,1=latematch)  trials  reps */
int main(int argc, char **argv) {
    (void)argc;
    size_t n = (size_t)atol(argv[1]);
    int mode = atoi(argv[2]), trials = atoi(argv[3]), rep = atoi(argv[4]);
    unsigned char *s = malloc(n + 64);
    /* Filler: 7-letter words separated by spaces, and ADJACENT WORDS
     * DIFFER -- no quote, no tag, no digit run, no repeated word. So the
     * TRUE backref patterns have no match here, which is what makes mode 0
     * a genuine nomatch subject. (A first version used all-'a' words; that
     * subject contains the same word twice in a row, so the dupword idiom's
     * own TRUE pattern matched at offset 0 and the "nomatch" arm was not
     * one.) */
    for (size_t i = 0; i < n; i++)
        s[i] = ((i % 8) == 7) ? ' ' : (unsigned char)('a' + (i / 8) % 20);
    size_t len = n;
    if (mode == 1) {                 /* plant a match at the very end */
        const char *tail = "\"zz\" <b>q</b> 42-42 ww ";
        size_t tl = strlen(tail);
        memcpy(s + n, tail, tl);
        len = n + tl;
    }
    ptrdiff_t caps[16][2];
    static volatile int sink;
    double best = 1e9; int r = 0;
    for (int t = 0; t < trials; t++) {
        struct timespec a, b;
        clock_gettime(CLOCK_MONOTONIC, &a);
        for (int k = 0; k < rep; k++) { r = rx_search(s, len, 0, caps); sink = r; }
        clock_gettime(CLOCK_MONOTONIC, &b);
        double el = ((b.tv_sec-a.tv_sec)+1e-9*(b.tv_nsec-a.tv_nsec)) / rep;
        if (el < best) best = el;
    }
    printf("%.8f %d\n", best, r);
    return 0;
}
EOF

N=$((KB * 1024))
TRIALS=5
REPS=3

# THE POPULATION, written out in full rather than derived by an edit.
#
# Each row is  tag | THE REAL BACKREF PATTERN | THE ERASED PATTERN | note.
# The erased pattern is the backreference replaced by a CAPTURE-ERASED COPY
# OF THE REFERENCED SUB-PATTERN, which is APPROACH 2's own stated
# over-approximation and is a genuine SUPERSET (the captured text is always
# in the group's language). It is written down, not produced by a sed on
# the pattern, because this probe's own first run derived it with
# `sed 's/\\1//'` -- which erases the backref to EPSILON, a different and
# unsound approximation, and additionally lost every `\b` to a `read`
# without -r. Both defects printed a full table of confident ratios.
IDIOMS='quote|(["\x27])[^"\x27]*\1|(["\x27])[^"\x27]*["\x27]|a quoted string, the commonest real backref
tag|<([a-z]+)>[^<]*</\1>|<([a-z]+)>[^<]*</[a-z]+>|an XML/HTML tag pair
dupword|\b([a-z]+)\s+\1\b|\b([a-z]+)\s+[a-z]+\b|the duplicated-word idiom
digits|([0-9]+)-\1|([0-9]+)-[0-9]+|a repeated number
letter|(\w)\1|(\w)\w|the smallest possible backref'

printf '%-9s %-26s %-9s %-13s %-13s %-8s %s\n' \
    tag "erased pattern" subject "hybrid (s)" "vm-only (s)" ratio note
printf -- '-%.0s' $(seq 1 118); printf '\n'

nrows=0
printf '%s\n' "$IDIOMS" | while IFS='|' read -r tag pat erased note; do
    [ -n "$tag" ] || continue
    for mode in 0 1; do
        [ "$mode" = 0 ] && subj=nomatch || subj=latematch
        # --features assertions,classes: the dupword idiom carries `\b`, which is a
        # `\s`, both module constructs. Both arms get the identical flag set.
        "$PCREC" -p rx --features assertions,classes -o "$D/m.c" -- "$erased" >/dev/null
        gcc -O2 -I"$D" -o "$D/hy" "$D/drv.c" "$D/m.c"
        pf_h=$(grep -o 'RX_VM_PREFILTER "[a-z]*"' "$D/m.c" | head -1)
        "$PCREC" -p rx --features assertions,classes --engine=vm -o "$D/m.c" -- "$erased" >/dev/null
        gcc -O2 -I"$D" -o "$D/vo" "$D/drv.c" "$D/m.c"
        pf_v=$(grep -o 'RX_VM_PREFILTER "[a-z]*"' "$D/m.c" | head -1)
        # THE POSITIVE CONTROL: if the two arms stamp the SAME prefilter,
        # this row is comparing an artifact with itself and its ratio is
        # meaningless. Say so rather than printing 1.00x.
        if [ "$pf_h" = "$pf_v" ]; then
            printf '%-9s %-26s %-9s %s\n' "$tag" "$erased" "$subj" \
                "SKIPPED: both arms stamp $pf_h -- no prefilter axis here"
            continue
        fi
        h=$("$D/hy" "$N" "$mode" "$TRIALS" "$REPS")
        v=$("$D/vo" "$N" "$mode" "$TRIALS" "$REPS")
        ht=${h%% *}; hr=${h##* }
        vt=${v%% *}; vr=${v##* }
        if [ "$hr" != "$vr" ]; then
            agree="*** ANSWERS DIFFER ($hr vs $vr) ***"
        else
            agree="$note"
        fi
        # BELOW-RESOLUTION GUARD, this probe's own equivalent of
        # probe_mline_caret_cost.sh's all-'a' finding: a pattern that
        # matches at offset 0 never scans, so both arms report a few tens
        # of nanoseconds and their ratio is noise. Say that instead of
        # printing a number a reader would take for a measurement.
        ratio=$(awk -v a="$vt" -v b="$ht" 'BEGIN{
            if (a < 1e-7 || b < 1e-7) { print "NOISE"; exit }
            if (b>0) printf "%.1fx", a/b; else print "n/a" }')
        # A NOISE row is not a failed measurement -- it is a RESULT: the
        # ERASED pattern matches at offset 0 on a subject the TRUE backref
        # pattern does not match at all, so this idiom's over-approximation
        # filters nothing and a hybrid built on it would buy nothing even
        # if it were sound. probe_erasure_hazard.py measures that half.
        [ "$ratio" = "NOISE" ] && agree="erasure matches at offset 0: filters NOTHING (see probe_erasure_hazard.py)"
        printf '%-9s %-26s %-9s %-13s %-13s %-8s %s\n' \
            "$tag" "$erased" "$subj" "$ht" "$vt" "$ratio" "$agree"
        nrows=$((nrows + 1))
    done
done

echo
echo "subject: ${KB} KB of filler (7-letter words, ADJACENT WORDS DIFFER, no"
echo "quote/tag/digit -- so the TRUE backref patterns have no match); latematch"
echo "appends a"
echo "24-byte tail every idiom matches. trials=$TRIALS reps=$REPS, best-of."
echo "ratio = vm-only / hybrid: how much SLOWER search is with no prefilter."
echo
echo "The backref patterns these erasures come from, for the record:"
printf '%s\n' "$IDIOMS" | while IFS='|' read -r tag pat erased note; do
    [ -n "$tag" ] && printf '  %-9s %-24s -> %s\n' "$tag" "$pat" "$erased"
done
