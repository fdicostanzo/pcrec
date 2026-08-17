#!/usr/bin/env bash
# ARCHIVED INSTRUMENT (K24 fix lane, 2026-08-17) -- provenance and reruns, the
# same posture as probe.sh next to it. It works out of a SCRATCH directory
# (variants, 8 MB subjects, built binaries); override with
#   K24_SCRATCH=/some/dir bash <this script>
# The session scratchpad it originally ran in is the default only so the
# recorded invocation is reproducible verbatim.
# K24 lever head-to-head. Build line and pinning are compare.sh's, verbatim
# (gcc -O2 -std=gnu11 -Wall -Wextra -Werror + eng_pcrec.c, taskset -c 2), so
# the numbers are commensurable with case (c)'s floors.tsv reference.
set -u
S="${K24_SCRATCH:-/tmp/claude-1001/-home-duxevents-pcrec/383cccce-a795-474b-afc3-b70de52a4808/scratchpad/k24fix}"
REPO="${K24_REPO:-/home/duxevents/pcrec}"
SUBJECT="$S/c_alt_absent.bin"
DRIVER="$REPO/tests/bench/compare/eng_pcrec.c"
BENCH_CPU="${BENCH_CPU:-2}"
TRIALS="${TRIALS:-10}"
TARGET_SECS=0.3
LOAD_MAX=2.0
OUT="${OUT:-$S/headtohead.tsv}"

PIN=""
if command -v taskset >/dev/null 2>&1 && taskset -c "$BENCH_CPU" true 2>/dev/null; then
    PIN="taskset -c $BENCH_CPU"
fi

read -r L1 L5 _ < /proc/loadavg
echo "load1=$L1 load5=$L5 pin='$PIN' trials=$TRIALS"
if awk -v l="$L5" -v m="$LOAD_MAX" 'BEGIN{exit !(l+0>m+0)}'; then
    echo "LOAD TOO HIGH ($L5 > $LOAD_MAX) -- refusing to measure" >&2; exit 1
fi

printf 'variant\tload1\tload5\tsplit\tmedian_mbps\tmin\tmax\ttrials\n' > "$OUT"

extract() { local text="$1" key="$2"; [[ "$text" =~ (^|[[:space:]])$key=([^[:space:]]+) ]] && printf '%s' "${BASH_REMATCH[2]}"; }

for d in "$@"; do
    name="$(basename "$d")"; name="${name#v_}"
    extra="$(cat "$d/CFLAGS" 2>/dev/null || echo)"
    berr="$(timeout 180 gcc -O2 -std=gnu11 -Wall -Wextra -Werror $extra \
        -I"$d" -o "$d/eng_pcrec" "$DRIVER" "$d/gen.c" 2>&1)"
    if [ $? -ne 0 ]; then
        echo "$name: BUILD FAILED: $berr"
        printf '%s\t%s\t%s\tBUILDFAIL\t\t\t\t\n' "$name" "$L1" "$L5" >> "$OUT"
        continue
    fi
    split="$(nm "$d/eng_pcrec" | grep -c 'rx_search\.\(part\|constprop\|isra\)' || true)"
    if [ "$split" -gt 0 ]; then splitlbl="SPLIT"; else splitlbl="mono"; fi

    b="$(timeout 120 $PIN "$d/eng_pcrec" "$SUBJECT" 1 2>&1)"
    if [ "$(extract "$b" status)" != "ok" ]; then echo "$name: baseline run failed: $b"; continue; fi
    if [ "$(extract "$b" match)" != "0" ]; then echo "$name: CORRECTNESS -- expected nomatch, got match=$(extract "$b" match)"; continue; fi
    s1="$(extract "$b" secs)"
    iters=$(awk -v s="$s1" -v t="$TARGET_SECS" 'BEGIN{if(s<1e-6)s=1e-6; v=(t/s)*1.2; if(v<1)v=1; printf "%d", v}')

    vals=()
    for ((t=0;t<TRIALS;t++)); do
        o="$(timeout 120 $PIN "$d/eng_pcrec" "$SUBJECT" "$iters" 2>&1)"
        [ "$(extract "$o" status)" != "ok" ] && { echo "$name: trial $t failed: $o"; break; }
        vals+=("$(extract "$o" mbps)")
    done
    med="$(printf '%s\n' "${vals[@]}" | sort -g | awk '{v[NR]=$0} END{print v[int((NR+1)/2)]}')"
    mn="$(printf '%s\n' "${vals[@]}" | sort -g | head -1)"
    mx="$(printf '%s\n' "${vals[@]}" | sort -g | tail -1)"
    joined="$(printf '%s,' "${vals[@]}")"
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$L1" "$L5" "$splitlbl" "$med" "$mn" "$mx" "$joined" >> "$OUT"
    echo "$name: median=$med [$mn..$mx] $splitlbl iters=$iters"
done
echo "DONE -> $OUT"
