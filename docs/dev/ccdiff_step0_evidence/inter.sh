set -u
S=/tmp/claude-1001/-home-duxevents-pcrec/dcce9a31-e3ae-41e3-8913-a4a918af3f32/scratchpad/ccdiff
BB=/home/duxevents/pcrec-bench/bench/bounded; BL=/home/duxevents/pcrec-bench/bench/loglines
# INTERLEAVED A/B: within one round every variant runs back to back, so a load
# excursion hits them together; the statistic is the median of the PER-ROUND
# ratios, not a ratio of medians. 11 rounds.
cell(){ name=$1; sub=$2; reg=$3; it=$4; shift 4; vars="$*"
  : > $S/.rows
  for r in $(seq 1 11); do
    row=""
    for v in $vars; do
      x=$($S/mb $S/cells/$name/$v.so "$sub" $reg $it | cut -f1); row="$row $x"
    done
    echo "$row" >> $S/.rows
  done
  python3 - "$name" "$vars" <<'PY'
import sys,statistics
name=sys.argv[1]; vars=sys.argv[2].split()
rows=[[float(x) for x in l.split()] for l in open('/tmp/claude-1001/-home-duxevents-pcrec/dcce9a31-e3ae-41e3-8913-a4a918af3f32/scratchpad/ccdiff/.rows')]
for i,v in enumerate(vars):
    rat=[r[i]/r[0] for r in rows]
    abs_=[r[i] for r in rows]
    print("%-24s %-11s median_ns=%10.1f   ratio_vs_gcc=%.3f  [%.3f-%.3f]"%(
        name,v,statistics.median(abs_),statistics.median(rat),min(rat),max(rat)))
PY
}
echo "LOAD AT START: $(cut -d' ' -f1-3 /proc/loadavg)"
cell cls-upto-4-thr-auto     $BB/throughput/t-letters-016k.bin findall 200 art-gcc art-clang twinA-gcc twinC-gcc twinAC-gcc
cell dig-upto-16-thr-vm      $BB/throughput/t-digits-016k.bin  findall 200 art-gcc art-clang twinV-gcc
cell floor-thr-vm            $BB/throughput/t-letters-016k.bin findall 200 art-gcc art-clang twinV-gcc
cell nest3-16-thr-vm         $BB/throughput/t-digits-016k.bin  findall  50 art-gcc art-clang twinV-gcc
cell stack-frame-srch-vm     $BL/subjects/s-000.bin            search 20000 art-gcc art-clang twinV-gcc
cell level-context-srch-auto $BL/subjects/s-000.bin            search 20000 art-gcc art-clang twinV-gcc
echo "LOAD AT END: $(cut -d' ' -f1-3 /proc/loadavg)"
