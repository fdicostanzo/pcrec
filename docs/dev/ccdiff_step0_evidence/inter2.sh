set -u
S=/tmp/claude-1001/-home-duxevents-pcrec/dcce9a31-e3ae-41e3-8913-a4a918af3f32/scratchpad/ccdiff
BB=/home/duxevents/pcrec-bench/bench/bounded
cell(){ name=$1; sub=$2; reg=$3; it=$4; shift 4; vars="$*"
  : > $S/.rows2
  for r in $(seq 1 11); do row=""
    for v in $vars; do x=$($S/mb $S/cells/$name/$v.so "$sub" $reg $it | cut -f1); row="$row $x"; done
    echo "$row" >> $S/.rows2; done
  python3 - "$name" "$vars" <<'PY'
import sys,statistics
name=sys.argv[1]; vars=sys.argv[2].split()
rows=[[float(x) for x in l.split()] for l in open('/tmp/claude-1001/-home-duxevents-pcrec/dcce9a31-e3ae-41e3-8913-a4a918af3f32/scratchpad/ccdiff/.rows2')]
for i,v in enumerate(vars):
    rat=[r[i]/r[0] for r in rows]
    print("%-22s %-12s median_ns=%9.1f  ratio=%.3f  [%.3f-%.3f]"%(name,v,statistics.median([r[i] for r in rows]),statistics.median(rat),min(rat),max(rat)))
PY
}
echo "LOAD: $(cut -d' ' -f1-3 /proc/loadavg)"
cell dig-upto-16-thr-vm $BB/throughput/t-digits-016k.bin  findall 200 art-gcc nossp-gcc twinW-gcc twinV-gcc art-clang
cell floor-thr-vm       $BB/throughput/t-letters-016k.bin findall 200 art-gcc nossp-gcc twinW-gcc twinV-gcc art-clang
echo "LOAD: $(cut -d' ' -f1-3 /proc/loadavg)"
