#!/usr/bin/env bash
# [START-SET] stage 3 -- THE LINUX ALPHA BLOCK for lane ssbuild3's DFA HAT
# (docs/design/startset.md §4.4, §7; docs/dev/lanes/ssbuild3_report.md; D144
# item 1 and addenda 1 and 3), alpha_s2.sh's protocol with the DFA hat's arms:
#
#   BASE = main before the DFA hat (abi 62/63), NEW = the DFA hat (abi 64),
#   DENY = NEW with -fno-start-set (bit 47, the start-set rows' deny).
#
# THE CELLS have two kinds. `W`: a DFA-hat mover: NEW stamps a `first-*`
# RX_DFA_PREFILTER and differs from BASE, and DENY == BASE apart from the abi
# digits, so |DENY - BASE| is the floor. `C`: not a mover -- NEW == BASE ==
# DENY under the same normalization.
#
# §7's DFA cells, each with its expected sign (cost-F5):
#   IMPROVE: capability aws thr (E 63 -> T 1, d 0.17%, the memchr form);
#     json-constant (63 -> 3, d 7.9%); dbnames (63 -> 14, d 22%; may read
#     null); loglines bignum (63 -> 10, d 12%; may read null), hex32-id
#     (63 -> 16, d 32%; may read null); level-context and the ctx-* hybrids
#     (63 -> 3).
#   F3 -- THE RE-SEED'S COST WHERE IT IS LEAST AMORTIZED (§4.4, cost-F5): the
#     DENSE movers kv-quoted (d 57%), wb-256 and wb-512 (d 56%), hex32-id
#     (d 32%): sign 0 (flat); a loss up to the floor is possible, past it is
#     an issue row.
#   NULL CELLS (one-byte narrowings, expected ~0, a re-seed fixed cost with a
#     deny floor): quotedstring-grok (4 -> 3), float-literal-bound (11 -> 10).
#   DO-NOT-REGRESS controls (C): floor-byte, high-byte-run, uuid-near-miss,
#     union-select.
#   OWED TO THE BENCH (never reverse-engineered here, memory pcrec-ask-bench-
#   dev): the litrun aws cell's subject id and the CTX cells' short-call
#   subjects -- named in the report as questions to relay.
# ABSOLUTE deltas beside the floor, never a ratio; inside the floor reads
# NULL. Any loss past the floor is an issue row (D144 item 3); any wrong
# answer is a disaster.
#
# EVERY READING RECORDS THE LIBC (cost-F7). BOTH [MEMFN] LAYERS (D147): set
# EXTRA_NEW_FLAGS=-fmemfn-simd to re-read the cells on the SIMD layer once it
# exists.
set -u
S2A=${S2A:-/tmp/s3alpha_startset}
PCREC_REPO=${PCREC_REPO:-/home/duxevents/pcrec}
BENCH=${BENCH:-/home/duxevents/pcrec-bench}
BASE_REV=${BASE_REV:?set BASE_REV to main before the DFA hat (abi 62 or 63)}
NEW_REV=${NEW_REV:?set NEW_REV to the DFA hat commit (lane/ssbuild3 tip, abi 64)}
EXTRA_NEW_FLAGS=${EXTRA_NEW_FLAGS:-}
CC=${CC:-gcc}
CPU=${CPU:-2}
LAUNCHES=${LAUNCHES:-5}
PASSES=${PASSES:-5}
STEP=${1:-all}
mkdir -p "$S2A"
cd "$S2A" || exit 2

CAP="cap:t-64k cap:t-1m"
LOG="log:t-064k-syslog log:t-1024k-syslog"
BND="bnd:t-letters-064k"
ALT="alt:t-128k-sparse alt:t-128k-dense"
# name|kind (W mover / C control)|pattern (bench path, or lit:<regex>)|flags|subjects
CELLS=(
  "aws|W|capability/patterns/wild-secrets-aws-access-key-id.rx||$CAP"
  "json-constant|W|capability/patterns/wild-codegrammar-json-constant.rx||$CAP"
  "dbnames|W|capability/patterns/wild-waf-crs-942140-dbnames.rx||$CAP"
  "bignum|W|loglines/patterns/bignum.rx||$LOG"
  "hex32-id|W|loglines/patterns/hex32-id.rx||$LOG"
  "level-context|W|loglines/patterns/level-context.rx||$LOG"
  "ctx-lazy-64|W|bounded/patterns/ctx-lazy-64.rx||$BND"
  "ctx-lazy-256|W|bounded/patterns/ctx-lazy-256.rx||$BND"
  "ctx-lazy-1024|W|bounded/patterns/ctx-lazy-1024.rx||$BND"
  "ctx-greedy-256|W|bounded/patterns/ctx-greedy-256.rx||$BND"
  "kv-quoted|W|loglines/patterns/kv-quoted.rx||$LOG"
  "wb-256|W|altwide/patterns/wb-256.rx||$ALT"
  "wb-512|W|altwide/patterns/wb-512.rx||$ALT"
  "grok|W|capability/patterns/wild-logparse-quotedstring-grok.rx||$CAP"
  "float-literal|W|capability/patterns/float-literal-bound.rx||$CAP"
  "floor-byte|C|capability/patterns/floor-byte.rx||$CAP"
  "high-byte-run|C|capability/patterns/high-byte-run.rx||$CAP"
  "uuid-near-miss|C|capability/patterns/uuid-near-miss.rx||$CAP"
  "union-select|C|capability/patterns/wild-waf-crs-942270-union-select.rx||$CAP"
)
PERCALLS=()

pattern_of() {  # pattern_of <field>: a bench path's text, or the literal after lit:
  case "$1" in lit:*) printf '%s' "${1#lit:}" ;; *) cat "$BENCH/bench/$1" ;; esac
}

build() {
  for side in base new; do
    rev=$BASE_REV; [ "$side" = new ] && rev=$NEW_REV
    if [ ! -x "$side/build/pcrec" ]; then
      rm -rf "$side"; mkdir -p "$side"
      git -C "$PCREC_REPO" archive "$rev" | tar -x -C "$side"
      make -C "$side" -j4 >"$side.build.log" 2>&1 || { echo "BUILD FAILED: $side"; exit 1; }
    fi
  done
  mkdir -p subj
  python3 - "$BENCH" "$S2A/subj" <<'PY'
import sys, os, hashlib, importlib.util, io, contextlib, random
bench, out = sys.argv[1], sys.argv[2]
def load(setname, mod):
    d = os.path.join(bench, "bench", setname)
    sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location(setname + "_" + mod, os.path.join(d, mod + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
def committed(setname, mf):
    man = {}
    for ln in open(os.path.join(bench, "bench", setname, mf)):
        f = ln.rstrip("\n").split("\t")
        if len(f) >= 3 and f[0] != "id":
            man[f[0]] = f[2]
    return man
bad = 0
import inspect
for tag, setname in (("cap", "capability"), ("log", "loglines"), ("bnd", "bounded"), ("alt", "altwide")):
    d = os.path.join(out, tag); os.makedirs(d, exist_ok=True)
    g = load(setname, "gen_throughput_subjects")
    with contextlib.redirect_stdout(io.StringIO()):
        g.OUT, g.MANIFEST = d, os.path.join(d, "manifest_throughput.tsv")
        g.main([]) if inspect.signature(g.main).parameters else g.main()
    man = committed(setname, "manifest_throughput.tsv")
    for sid, sha in man.items():
        p = os.path.join(d, sid + ".bin")
        ok = os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == sha
        print("%s:%s %s" % (tag, sid, "OK" if ok else "SHA-MISMATCH")); bad += not ok
sys.exit(1 if bad else 0)
PY
  [ $? -eq 0 ] || { echo "SUBJECT SHA MISMATCH: off-pin, STOP"; exit 1; }
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

  for cell in "${CELLS[@]}" ${PERCALLS[@]+"${PERCALLS[@]}"}; do
    IFS='|' read -r name kind pat flags subjects <<<"$cell"
    case "$pat" in lit:*) ;; *) [ -s "$BENCH/bench/$pat" ] || { echo "NO SUCH PATTERN FILE: $pat"; exit 1; } ;; esac
    for side in base new deny; do
      bin=base; extra=""
      [ "$side" != base ] && bin=new && extra="$EXTRA_NEW_FLAGS"
      [ "$side" = deny ] && extra="$EXTRA_NEW_FLAGS -fno-start-set"
      mkdir -p "art/$name/$side"
      # shellcheck disable=SC2086
      "$S2A/$bin/build/pcrec" --features all -p rx $flags $extra \
        -o "art/$name/$side/art.c" --pattern "$(pattern_of "$pat")" || { echo "EMIT FAILED $name $side"; exit 1; }
      "$CC" -O2 -I"art/$name/$side" -o "art/$name/$side/run" drv.c "art/$name/$side/art.c"
    done
  done
}

# no \b: BSD sed silently no-ops it, and this runs on both boxes. Only the
# abi digits differ between BASE and DENY (stage 3 adds no every-artifact
# line); a mover's `first-*` RX_DFA_PREFILTER stays, so it differs from BASE.
norm() { sed -E -e 's/\(abi (62|63|64)\)/(abi N)/g; s/(PCREC_RX_ABI_H[^0-9]*)(62|63|64)/\1N/g; s/(\.abi = )(62|63|64),/\1N,/' "$1"; }

check() {
  # (1) a W cell's NEW carries a `first-*` RX_DFA_PREFILTER and differs from
  #     BASE, and DENY == BASE (modulo the digits: bit 47 is in
  #     strategy_denials); (2) a C cell's three artifacts are equal
  #     under the same normalization; (3) base, new and deny answer
  #     identically on every subject.
  local rc=0
  for cell in "${CELLS[@]}" ${PERCALLS[@]+"${PERCALLS[@]}"}; do
    IFS='|' read -r name kind pat flags subjects <<<"$cell"
    for side in base new deny; do
      [ -s "art/$name/$side/art.c" ] && [ -x "art/$name/$side/run" ] \
        || { echo "NOT BUILT: art/$name/$side (run 'build' first)"; return 1; }
    done
    same() { cmp -s <(norm "art/$name/$1/art.c") <(norm "art/$name/$2/art.c"); }
    case "$kind" in
      W) { grep -qE '^#define RX_DFA_PREFILTER "first-(memchr|class)-bounded"$' "art/$name/new/art.c" && ! same base new && same base deny; } \
           || { echo "W-CELL WRONG $name: want NEW on the DFA hat and != BASE, DENY == BASE"; rc=1; } ;;
      C) { same base new && same base deny; } \
           || { echo "CONTROL MOVED $name"; rc=1; } ;;
    esac
    if [ "$subjects" = short ]; then subjects=$(cd subj/short && ls *.bin | sed 's/\.bin$//; s/^/short:/'); fi
    for s in $subjects; do
      f="subj/${s%%:*}/${s#*:}.bin"; mode=t; case "$name" in *-srch) mode=c ;; esac
      a=$(art/$name/base/run $mode "$f" 1 | cut -d' ' -f1)
      for side in new deny; do
        b=$(art/$name/$side/run $mode "$f" 1 | cut -d' ' -f1)
        [ "$a" = "$b" ] || { echo "ANSWER DIFF $name $side $s: $a vs $b"; rc=1; }
      done
    done
  done
  echo "check: rc=$rc"; return $rc
}

time_cells() {
  # protocol §6.1: taskset -c $CPU, load1 < 0.5 before each cell, LAUNCHES
  # launches round-robin across the three arms, PASSES timed loops each; a
  # cell is the median of the per-launch medians.
  # DARWIN=1: the Mac's DIRECTIONAL run (D144 addendum 1: never a verdict) --
  # no taskset, no load wait, load1 from sysctl.
  local pin="taskset -c $CPU"
  if [ "${DARWIN:-0}" = 1 ]; then pin=""; fi
  echo "# libc: $(ldd --version 2>&1 | head -1) | layers: scalar${EXTRA_NEW_FLAGS:+ + $EXTRA_NEW_FLAGS}"
  echo "# $(date -u) $(uname -n) load1=$( [ "${DARWIN:-0}" = 1 ] && sysctl -n vm.loadavg | cut -d' ' -f2 || cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) boost=$(cat /sys/devices/system/cpu/cpufreq/boost 2>/dev/null)"
  printf '%-15s %-22s %-6s %10s %10s %10s  %10s %10s  %s\n' cell subject unit base new deny new-base floor verdict
  for cell in "${CELLS[@]}" ${PERCALLS[@]+"${PERCALLS[@]}"}; do
    IFS='|' read -r name kind pat flags subjects <<<"$cell"
    mode=t; unit=ns/B
    if [ "$subjects" = short ]; then mode=c; unit=ns/call; subjects=$(cd subj/short && ls *.bin | sed 's/\.bin$//; s/^/short:/'); fi
    for s in $subjects; do
      f="subj/${s%%:*}/${s#*:}.bin"
      while [ "${DARWIN:-0}" != 1 ]; do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{exit !($l < 0.5)}" && break; sleep 20; done
      declare -A M=()
      for i in $(seq 1 "$LAUNCHES"); do
        for side in base new deny; do
          # shellcheck disable=SC2086  # $pin is empty or a word list on purpose
          v=$($pin "art/$name/$side/run" $mode "$f" "$PASSES" | sed -n 's/.*median=\([0-9.]*\).*/\1/p')
          M[$side]="${M[$side]:-} $v"
        done
      done
      med() { tr ' ' '\n' <<<"$1" | grep . | sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}'; }
      b=$(med "${M[base]}"); n=$(med "${M[new]}"); d=$(med "${M[deny]}")
      ref=$b   # W and C alike: DENY == BASE in program text
      dl=$(awk "BEGIN{printf \"%+.5f\", $n-$b}"); fl=$(awk "BEGIN{x=$d-$ref; printf \"%.5f\", (x<0?-x:x)}")   # parenthesized: BSD awk refuses a bare ?: argument
      v=$(awk "BEGIN{x=$n-$b; a=x<0?-x:x; print (a<=$fl)?\"NULL\":(x<0?\"WIN\":\"REGRESSION\")}")
      printf '%-15s %-22s %-6s %10s %10s %10s  %10s %10s  %s\n' "$name" "$s" "$unit" "$b" "$n" "$d" "$dl" "$fl" "$v"
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
