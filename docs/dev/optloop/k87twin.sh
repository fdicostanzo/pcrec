#!/usr/bin/env bash
# [K87] pcrec-side Linux TWIN of the scan-edge range spelling, with an
# ALIGNMENT CONTROL (lane k87twin; docs/dev/optloop/k87twin_report.md).
#
#   NEW = main's emission:  (unsigned)(b - lo) <= spanu
#   OLD = the twin:         (unsigned char)(b - lo) <= span   (sed over the emitted C;
#                           `build` verifies the diff is exactly the range-test sites)
#   Each spelling is compiled at PADS code offsets (a `.skip K` prepended to the
#   artifact shifts every function and loop by K bytes) -- the alignment control.
#   NEW at pad 0 is compiled TWICE (new0, new0b): |new0 - new0b| is the
#   base-vs-base floor.  CCs: gcc and clang, -O2.
# usage: k87twin.sh build | time CC | all
set -u
W=${W:-/home/duxevents/pcrec/scratch_lx/k87twin}
PCREC=${PCREC:-$W/main/build/pcrec}
CPU=${CPU:-2}; LAUNCHES=${LAUNCHES:-5}; PASSES=${PASSES:-5}
PADS=${PADS:-"0 16 32 48 64 80 96 112"}
cd "$W" || exit 2
mkdir -p "$W/tmp"; export TMPDIR="$W/tmp"
PATS=("cls|[a-z]{0,1024}" "nest|(?:[a-z]{1,6}){1,6}")
# cell: pattern|mode|subject
CELLS=(
  "cls|t|t-letters-004k" "cls|t|t-letters-016k" "cls|t|t-letters-064k"
  "nest|t|t-letters-004k" "nest|t|t-letters-016k" "nest|t|t-letters-064k"
  "cls|c|f-pw-8" "cls|c|f-hex-32" "cls|c|f-csv-4" "cls|c|d-00031"
  "nest|c|f-pw-8" "nest|c|f-hex-32" "nest|c|f-csv-4" "nest|c|d-00031"
)
variants() { for p in $PADS; do echo "new$p"; echo "old$p"; done; echo new0b; }

build() {
  mkdir -p gen bin
  for pp in "${PATS[@]}"; do
    n=${pp%%|*}; pat=${pp#*|}
    mkdir -p gen/$n
    "$PCREC" --features all -p rx -o gen/$n/art.c --pattern "$pat" || { echo "EMIT FAILED $n"; exit 1; }
    cp gen/$n/base.h gen/$n/art.h 2>/dev/null; ls gen/$n >/dev/null
    # the twin: ONLY the range-test spelling
    perl -pe 's/\(unsigned\)\(([^()]*?(?:\[[^\]]*\])?) - (\d+)\) <= (\d+)u/(unsigned char)($1 - $2) <= $3/g' \
      gen/$n/art.c > gen/$n/art_old.c
    echo "== $n: diff old vs new (changed lines)";     diff gen/$n/art.c gen/$n/art_old.c > gen/$n/old_new.diff
    # every differing line must differ only by the spelling
    python3 - gen/$n/art.c gen/$n/art_old.c <<'PY' || { echo "TWIN DIFF NOT SPELLING-ONLY"; exit 1; }
import sys,re
a=open(sys.argv[1]).read().split("\n"); b=open(sys.argv[2]).read().split("\n")
assert len(a)==len(b); k=0
PAT=1
for x,y in zip(a,b):
    if x!=y:
        k+=1
        nx=re.sub(r"\(unsigned\)\((.*?) - (\d+)\) <= (\d+)u", r"R(\1,\2,\3)", x)
        ny=re.sub(r"\(unsigned char\)\((.*?) - (\d+)\) <= (\d+)", r"R(\1,\2,\3)", y)
        assert nx==ny, (x,y)
print("spelling-only lines: %d" % k)
PY
  done
  cat > drv.c <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "art.h"
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}
static int cmpd(const void*a,const void*b){double x=*(const double*)a,y=*(const double*)b;return x<y?-1:x>y;}
static long findall(const unsigned char*b,long n){
  ptrdiff_t caps[RX_NCAPS][2]; size_t pos=0; long count=0;
  for(;;){ int r=rx_search(b,(size_t)n,pos,caps); if(r==0) break;
           if(r<0){ printf("giveup %d\n", r); exit(3); }
           size_t s=(size_t)caps[0][0], e=(size_t)caps[0][1];
           count++; pos=(e>s)?e:s+1; if(pos>(size_t)n) break; }
  return count; }
static long onecall(const unsigned char*b,long n){
  ptrdiff_t caps[RX_NCAPS][2]; int r=rx_search(b,(size_t)n,0,caps);
  if(r<0){ printf("giveup %d\n", r); exit(3); } return r; }
int main(int argc,char**argv){
  int percall=argv[1][0]=='c';
  FILE*f=fopen(argv[2],"rb"); fseek(f,0,SEEK_END); long n=ftell(f); rewind(f);
  unsigned char*b=malloc(n?n:1); if(n&&fread(b,1,n,f)!=(size_t)n) return 2; fclose(f);
  int passes=argc>3?atoi(argv[3]):5; double t[64]; long count=0;
  long (*fn)(const unsigned char*,long)=percall?onecall:findall;
  double t0=now(); count=fn(b,n); double one=now()-t0;
  long reps=(long)(0.050/(one>1e-9?one:1e-9))+1;
  for(int it=0; it<passes&&it<64; it++){
    t0=now(); for(long r=0;r<reps;r++) count=fn(b,n); t[it]=now()-t0; }
  qsort(t,passes,sizeof t[0],cmpd);
  if(percall) printf("result=%ld median=%.3f ns/call reps=%ld loop=%.1f ms\n", count,
                     t[passes/2]*1e9/(double)reps, reps, t[passes/2]*1e3);
  else printf("matches=%ld median=%.6f ns/byte reps=%ld loop=%.1f ms\n", count,
              t[passes/2]*1e9/((double)n*reps), reps, t[passes/2]*1e3);
  return 0; }
EOF
  for cc in gcc clang; do
    command -v $cc >/dev/null || continue
    for pp in "${PATS[@]}"; do
      n=${pp%%|*}
      for v in $(variants); do
        sp=${v%%[0-9]*}; pad=${v#$sp}; pad=${pad%b}
        src=gen/$n/art.c; [ "$sp" = old ] && src=gen/$n/art_old.c
        d=bin/$cc/$n/$v; mkdir -p $d
        { printf '__asm__(".text\\n.skip %d,0x90\\n");\n' "$pad"; cat $src; } > $d/art.c
        cp gen/$n/art.h $d/art.h
        $cc -O2 -I$d -o $d/run drv.c $d/art.c || { echo "CC FAILED $cc $n $v"; exit 1; }
      done
    done
  done
  echo build done
}

time_cells() {
  cc=$1; pin="taskset -c $CPU"
  echo "# $(date -u) $(uname -n) cc=$cc load1=$(cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor) boost=$(cat /sys/devices/system/cpu/cpufreq/boost)"
  echo "# cc cell mode subject launch variant value"
  for cell in "${CELLS[@]}"; do
    IFS='|' read -r n mode s <<<"$cell"
    f=subj/$s.bin
    # answer identity first (one pass each)
    ref=$(bin/$cc/$n/new0/run $mode $f 1 | cut -d' ' -f1)
    for v in $(variants); do
      a=$(bin/$cc/$n/$v/run $mode $f 1 | cut -d' ' -f1); [ "$a" = "$ref" ] || echo "ANSWER DIFF $cc $n $v $s"
    done
    for i in $(seq 1 "$LAUNCHES"); do
      while :; do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{exit !($l < 0.5)}" && break; sleep 20; done
      for v in $(variants); do
        val=$($pin bin/$cc/$n/$v/run $mode $f "$PASSES" | sed -n 's/.*median=\([0-9.]*\).*/\1/p')
        echo "$cc $n $mode $s $i $v $val"
      done
    done
  done
}
case "${1:-all}" in
  build) build ;;
  time) time_cells "${2:-gcc}" ;;
  all) build && for cc in gcc clang; do command -v $cc >/dev/null && time_cells $cc; done ;;
esac
