#!/bin/bash
# [MEMFN] isa_evaluation.md §3.3 L-2 (lane lxrun, 2026-10-05): TODAY's pcrec
# artifacts compiled at gcc -O2 (baseline x86-64) against -O2
# -march=x86-64-v3 -- gcc's own vectorization, BMI2, movbe; no memfn kernel
# -- on 12 representative bench patterns (capability + syntax sets) and the
# bench's own pinned throughput subjects. Absolute ns per subject byte,
# never a ratio as the verdict; a delta inside the launch-to-launch spread of
# either arm reads NULL.
#
#     S4A=<alpha_k82.sh's dir, already built> bash memfn_l2.sh OUTDIR
#
# Reuses alpha_k82.sh's NEW compiler ($S4A/new/build/pcrec, main's tip), its
# sha256-checked subjects ($S4A/subj/{cap,syn}) and its driver ($S4A/drv.c:
# find-all, warm-up-calibrated >= 50 ms loop, median of PASSES). Protocol as
# alpha (§6.1): taskset -c $CPU, load1 < 0.5 before each cell (waited at most
# LOADWAIT s, then logged and run anyway), LAUNCHES launches round-robin
# across the two arms, cell = median of per-launch medians. Writes only under
# OUTDIR. Last line: "MEMFN-L2 COMPLETE cells=<n> fails=<n>".
set -u
S4A=${S4A:?set S4A to alpha_k82.sh run dir}
O=${1:?usage: memfn_l2.sh OUTDIR}
CC=${CC:-gcc}
CPU=${CPU:-2}
LAUNCHES=${LAUNCHES:-5}
PASSES=${PASSES:-5}
LOADWAIT=${LOADWAIT:-600}
BENCH=${BENCH:-/home/duxevents/pcrec-bench}
PCREC=${PCREC:-$S4A/new/build/pcrec}
T=gnutimeout; command -v $T >/dev/null || T=timeout
mkdir -p "$O"; cd "$O" || exit 2
export TMPDIR=$O
[ -x "$PCREC" ] && [ -s "$S4A/drv.c" ] && [ -d "$S4A/subj/cap" ] && [ -d "$S4A/subj/syn" ] \
    || { echo "S4A not built (need new/build/pcrec, drv.c, subj/cap, subj/syn)"; exit 2; }
# name|bench pattern|subjects
CELLS=(
  "aws-key|capability/patterns/wild-secrets-aws-access-key-id.rx|cap:t-64k cap:t-1m"
  "ipv4-owasp|capability/patterns/wild-validator-ipv4-owasp.rx|cap:t-64k cap:t-1m"
  "union-select|capability/patterns/wild-waf-crs-942270-union-select.rx|cap:t-64k cap:t-1m"
  "quoted-grok|capability/patterns/wild-logparse-quotedstring-grok.rx|cap:t-64k cap:t-1m"
  "iso8601|capability/patterns/wild-datetime-moment-iso8601.rx|cap:t-64k cap:t-1m"
  "uuid-grok|capability/patterns/wild-validator-uuid-grok.rx|cap:t-64k cap:t-1m"
  "paren-rec|capability/patterns/balanced-parens-rec.rx|cap:t-64k cap:t-1m"
  "cls-w|syntax/patterns/cls-w.rx|syn:t-64k syn:t-1m"
  "cls-d|syntax/patterns/cls-d.rx|syn:t-64k syn:t-1m"
  "alt-nested|syntax/patterns/alt-nested.rx|syn:t-64k syn:t-1m"
  "bak-1|syntax/patterns/bak-1.rx|syn:t-64k syn:t-1m"
  "mod-i|syntax/patterns/mod-i.rx|syn:t-64k syn:t-1m"
)
FAILS=0
echo "# box: $(hostname) $(grep -m1 'model name' /proc/cpuinfo | sed 's/.*: //'); $($CC --version | head -1)"
echo "# pcrec: $PCREC ($("$PCREC" --version 2>/dev/null | head -1)); taskset -c $CPU; gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) boost=$(cat /sys/devices/system/cpu/cpufreq/boost 2>/dev/null); $(date -u +%Y-%m-%dT%H:%MZ)"
echo "## build: per pattern one emit, two compiles (driver + artifact, same flags)"
for cell in "${CELLS[@]}"; do
    IFS='|' read -r name pat subjects <<<"$cell"
    mkdir -p "$name"
    if ! "$PCREC" --features all -p rx -o "$name/art.c" --pattern "$(cat "$BENCH/bench/$pat")" 2>"$name/emit.err"; then
        echo "EMIT FAILED $name: $(head -1 "$name/emit.err")"; FAILS=$((FAILS + 1)); continue
    fi
    $CC -O2 -I"$name" -o "$name/run.base" "$S4A/drv.c" "$name/art.c" || { echo "CC FAILED $name base"; FAILS=$((FAILS + 1)); continue; }
    $CC -O2 -march=x86-64-v3 -I"$name" -o "$name/run.v3" "$S4A/drv.c" "$name/art.c" || { echo "CC FAILED $name v3"; FAILS=$((FAILS + 1)); continue; }
    # what -march bought in the text: ymm uses, BMI1/2 + movbe mnemonics, .text size
    ev() { objdump -d --no-show-raw-insn "$1" | awk -v s="$2" '
        /ymm/ {y++} /\t(shlx|shrx|sarx|rorx|bzhi|pdep|pext|andn|blsr|blsi|blsmsk|tzcnt|lzcnt|movbe)/ {b++}
        END {printf "ymm=%d bmi/movbe=%d", y+0, b+0}'; printf ' text=%s' "$(size -A "$1" | awk '/^\.text/{print $2}')"; }
    echo "$name: base[$(ev "$name/run.base")] v3[$(ev "$name/run.v3")]"
done
echo "## answer identity (matches= equal between arms on every subject)"
for cell in "${CELLS[@]}"; do
    IFS='|' read -r name pat subjects <<<"$cell"
    [ -x "$name/run.v3" ] || continue
    for s in $subjects; do
        f="$S4A/subj/${s%%:*}/${s#*:}.bin"
        a=$($T 300 "$name/run.base" t "$f" 1 | cut -d' ' -f1); b=$($T 300 "$name/run.v3" t "$f" 1 | cut -d' ' -f1)
        if [ -n "$a" ] && [ "$a" = "$b" ]; then echo "same $name $s $a"; else echo "ANSWER DIFF $name $s: '$a' vs '$b'"; FAILS=$((FAILS + 1)); touch "$name/.bad"; fi
    done
done
echo "## timing: ns/byte, median of $LAUNCHES launch-medians (each launch = median of $PASSES >= 50 ms loops)"
printf '%-13s %-9s %11s %11s %11s %8s %11s  %s\n' cell subject base v3 v3-base pct floor verdict
n=0
for cell in "${CELLS[@]}"; do
    IFS='|' read -r name pat subjects <<<"$cell"
    [ -x "$name/run.v3" ] && [ ! -e "$name/.bad" ] || continue
    for s in $subjects; do
        f="$S4A/subj/${s%%:*}/${s#*:}.bin"
        w=0; while :; do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{exit !($l < 0.5)}" && break
            [ $w -ge "$LOADWAIT" ] && { echo "# load1=$l after ${w}s wait, running $name $s anyway"; break; }; sleep 20; w=$((w + 20)); done
        mb=""; mv=""
        for i in $(seq 1 "$LAUNCHES"); do
            mb="$mb $($T 600 taskset -c "$CPU" "$name/run.base" t "$f" "$PASSES" | sed -n 's/.*median=\([0-9.]*\).*/\1/p')"
            mv="$mv $($T 600 taskset -c "$CPU" "$name/run.v3" t "$f" "$PASSES" | sed -n 's/.*median=\([0-9.]*\).*/\1/p')"
        done
        # median, and spread (max - min) of the launch medians
        st() { tr ' ' '\n' <<<"$1" | grep . | sort -g | awk '{a[NR]=$1} END{printf "%s %.6f", a[int((NR+1)/2)], a[NR]-a[1]}'; }
        read -r b sb <<<"$(st "$mb")"; read -r v sv <<<"$(st "$mv")"
        if [ -z "$b" ] || [ -z "$v" ]; then echo "NO TIMING $name $s"; FAILS=$((FAILS + 1)); continue; fi
        awk -v c="$name" -v s="$s" -v b="$b" -v v="$v" -v sb="$sb" -v sv="$sv" 'BEGIN{
            d=v-b; fl=(sb>sv?sb:sv); a=(d<0?-d:d)
            printf "%-13s %-9s %11.6f %11.6f %+11.6f %+7.1f%% %11.6f  %s\n", c, s, b, v, d, (b>0?100*d/b:0), fl, (a<=fl?"NULL":(d<0?"V3-WIN":"V3-LOSS"))}'
        n=$((n + 1))
    done
done
echo "MEMFN-L2 COMPLETE cells=$n fails=$FAILS"
