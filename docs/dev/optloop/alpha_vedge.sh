#!/bin/bash
# docs/dev/optloop/alpha_vedge.sh -- [OPT-VEDGE]'s ALPHA BLOCK (D144 item 1 +
# addendum 1), for the Linux box (ubuntubudu, gcc 15.2). NOT for the Mac. The
# commands are vedge_report.md §5/§7's, as one script. Nothing is written
# inside either repo: everything lands under $S4A.
#
#   PCREC_REPO=<repo with both revs>  BENCH=/home/duxevents/pcrec-bench \
#   BASE_REV=74017b71 NEW_REV=8562ff3a  bash alpha_vedge.sh [build|check|time|all]
#
# BASE is the commit BEFORE [OPT-VEDGE] (74017b71, abi 56: 14e78104 already
# carries the feature). NEW is the tip. DENY is NEW with every later deny flag
# (-fno-view-edge, and -fno-run-overlap -fno-req-run-fold for the abi-58/59
# rows landed since), so DENY's program equals BASE's apart from the abi
# digits (`check` verifies, per cell, before anything is timed); BASE/DENY is
# each cell's noise floor (the same program twice). Per D144 addendum 1:
# every timed loop >= 50 ms (calibrated), ABSOLUTE ns/call deltas beside the
# floor |DENY-BASE|, never a ratio; a delta inside the floor is NULL.
set -u
S4A=${S4A:-$PWD/vedge_alpha}
PCREC_REPO=${PCREC_REPO:-/home/duxevents/pcrec}
BENCH=${BENCH:-/home/duxevents/pcrec-bench}
BASE_REV=${BASE_REV:?set BASE_REV (the commit before OPT-VEDGE, 74017b71)}
NEW_REV=${NEW_REV:?set NEW_REV}
DENYFLAGS=${DENYFLAGS:--fno-view-edge -fno-run-overlap -fno-req-run-fold}
CC=${CC:-gcc}
CPU=${CPU:-2}
LAUNCHES=${LAUNCHES:-5}
STEP=${1:-all}
mkdir -p "$S4A"
cd "$S4A" || exit 2
SUBJ="short l4k prose64k dig40 mix4k hex4k"
# name|bench pattern file|flags|wrap (1 = "(?:P)\z")
CELLS=()
for n in 4 16 64 256 1024 2048 4096; do CELLS+=("upto-$n|bounded/patterns/cls-upto-$n.rx||1"); done
CELLS+=("cls-w|syntax/patterns/cls-w.rx||1" "dig-exact-16|bounded/patterns/dig-exact-16.rx||1"
        "year4|bounded/patterns/year4.rx||1" "hex32|bounded/patterns/hex32.rx||1"
        "floor|bounded/patterns/floor.rx||1"
        "base10num-grok|capability/patterns/wild-logparse-base10num-grok.rx||1"
        "qnt-dot-bounded|utf8/patterns/qnt-dot-bounded.rx|-e utf8|1")

build() {
  for side in base new; do
    rev=$BASE_REV; [ "$side" = new ] && rev=$NEW_REV
    if [ ! -x "$side/build/pcrec" ]; then
      rm -rf "$side"; mkdir -p "$side"
      git -C "$PCREC_REPO" archive "$rev" | tar -x -C "$side"
      make -C "$side" -j4 >"$side.build.log" 2>&1 || { echo "BUILD FAILED: $side"; exit 1; }
    fi
  done
  # fixed-seed subjects (vedge_report.md §5: short = 40 random lowercase,
  # l4k = 4096 letters, prose64k = 2-9-letter words, dig40, mix4k over
  # `ab:12 \n`, hex4k)
  mkdir -p subj
  python3 - "$S4A/subj" <<'PY'
import random, string, sys, os
out = sys.argv[1]; r = random.Random(0x5EED)
def put(n, b): open(os.path.join(out, n), "wb").write(b)
L = string.ascii_lowercase
put("short", "".join(r.choice(L) for _ in range(40)).encode())
put("l4k", "".join(r.choice(L) for _ in range(4096)).encode())
w, tot = [], 0
while tot < 65536:
    x = "".join(r.choice(L) for _ in range(r.randint(2, 9))); w.append(x); tot += len(x) + 1
put("prose64k", " ".join(w).encode()[:65536])
put("dig40", "".join(r.choice(string.digits) for _ in range(40)).encode())
put("mix4k", "".join(r.choice("ab:12 \n") for _ in range(4096)).encode())
put("hex4k", "".join(r.choice("0123456789abcdef") for _ in range(4096)).encode())
PY
  # D144 addendum 1: the timed loop is >= 50 ms (iterations doubled until a
  # round takes >= 50 ms), 7 rounds, median ns/call.
  cat > percall50.c <<'CEOF'
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>
extern int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
static uint64_t now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (uint64_t)t.tv_sec*1000000000ull+t.tv_nsec;}
static int cmp(const void*a,const void*b){double x=*(double*)a,y=*(double*)b;return x<y?-1:x>y;}
int main(int c,char**v){FILE*f=fopen(v[1],"rb");fseek(f,0,2);long n=ftell(f);fseek(f,0,0);unsigned char*b=malloc(n+1);
 if(fread(b,1,n,f)!=(size_t)n) return 2;
 ptrdiff_t cp[64][2]; int r=rx_search(b,n,0,cp); long it=1; uint64_t t0;
 do{it*=2;t0=now();for(long i=0;i<it;i++)rx_search(b,n,0,cp);}while(now()-t0<50000000);
 double t[7];for(int k=0;k<7;k++){t0=now();for(long i=0;i<it;i++)rx_search(b,n,0,cp);t[k]=(double)(now()-t0)/it;}
 qsort(t,7,sizeof t[0],cmp);printf("r=%d span=%td,%td ns/call=%.2f\n",r,r==1?cp[0][0]:-1,r==1?cp[0][1]:-1,t[3]);return 0;}
CEOF
  for cell in "${CELLS[@]}"; do
    IFS='|' read -r name pat flags wrap <<<"$cell"
    [ -s "$BENCH/bench/$pat" ] || { echo "NO SUCH PATTERN FILE: $pat"; exit 1; }
    p=$(cat "$BENCH/bench/$pat"); [ "$wrap" = 1 ] && p="(?:$p)\\z"
    for side in base new deny; do
      bin=base; extra=""
      [ "$side" != base ] && bin=new
      [ "$side" = deny ] && extra=$DENYFLAGS
      mkdir -p "art/$name/$side"
      # shellcheck disable=SC2086
      "$S4A/$bin/build/pcrec" --features all -p rx $flags $extra \
        -o "art/$name/$side/art.c" --pattern "$p" || { echo "EMIT FAILED $name $side"; exit 1; }
      "$CC" -O2 -I"art/$name/$side" -o "art/$name/$side/run" percall50.c "art/$name/$side/art.c" || { echo "CC FAILED $name $side"; exit 1; }
    done
  done
}

norm() { sed -E -e 's/abi 5[5-9]/abi N/g; s/(PCREC_RX_ABI_H[^0-9]*)5[5-9]/\1N/g; s/(\.abi = )5[5-9]/\1N/; /^#define RX_RUN_WORDS /d' "$1"; }

check() {
  # DENY == BASE modulo the abi digits (reported, not fatal: a cell where it
  # differs has no valid floor and is flagged), and every arm answers (r and
  # span) identically on every subject.
  local rc=0
  for cell in "${CELLS[@]}"; do
    IFS='|' read -r name pat flags wrap <<<"$cell"
    for side in base new deny; do
      [ -x "art/$name/$side/run" ] || { echo "NOT BUILT: art/$name/$side"; return 1; }
    done
    if cmp -s <(norm "art/$name/base/art.c") <(norm "art/$name/deny/art.c"); then echo "DENY==BASE  $name"
    else echo "DENY!=BASE  $name  (no valid floor: flagged)"; fi
    cmp -s <(norm "art/$name/base/art.c") <(norm "art/$name/new/art.c") && echo "NEW==BASE   $name (unmoved)"
    for s in $SUBJ; do
      a=$(art/$name/base/run "subj/$s" | sed 's/ ns\/call.*//')
      for side in new deny; do
        b=$(art/$name/$side/run "subj/$s" | sed 's/ ns\/call.*//')
        [ "$a" = "$b" ] || { echo "ANSWER DIFF $name $side $s: $a vs $b"; rc=1; }
      done
    done
  done
  echo "check: rc=$rc"; return $rc
}

time_cells() {
  echo "# $(date -u) $(uname -n) load1=$(cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) cpu=$CPU"
  printf '%-16s %-9s %10s %10s %10s  %10s %10s  %s\n' cell subject base_ns new_ns deny_ns new-base floor verdict
  for cell in "${CELLS[@]}"; do
    IFS='|' read -r name pat flags wrap <<<"$cell"
    for s in $SUBJ; do
      for t in $(seq 1 30); do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{exit !($l < 0.5)}" && break; sleep 20; done
      declare -A M=()
      for i in $(seq 1 "$LAUNCHES"); do
        for side in base new deny; do
          v=$(taskset -c "$CPU" "art/$name/$side/run" "subj/$s" | sed -n 's/.*ns\/call=\([0-9.]*\).*/\1/p')
          M[$side]="${M[$side]:-} $v"
        done
      done
      med() { tr ' ' '\n' <<<"$1" | grep . | sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}'; }
      b=$(med "${M[base]}"); n=$(med "${M[new]}"); d=$(med "${M[deny]}")
      dl=$(awk "BEGIN{printf \"%+.2f\", $n-$b}"); fl=$(awk "BEGIN{x=$d-$b; printf \"%.2f\", x<0?-x:x}")
      v=$(awk "BEGIN{x=$n-$b; a=x<0?-x:x; print (a<=$fl)?\"NULL\":(x<0?\"WIN\":\"REGRESSION\")}")
      printf '%-16s %-9s %10s %10s %10s  %10s %10s  %s\n' "$name" "$s" "$b" "$n" "$d" "$dl" "$fl" "$v"
      unset M
    done
  done
}

case "$STEP" in
  build) build ;;
  check) check ;;
  time)  time_cells ;;
  all)   build && check && time_cells ;;
  *) echo "usage: $0 [build|check|time|all]"; exit 2 ;;
esac
