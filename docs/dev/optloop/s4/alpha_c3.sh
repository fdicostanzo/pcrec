#!/bin/bash
# docs/dev/optloop/s4/alpha_c3.sh -- [OPT-LITSCAN] S4 C3's ALPHA BLOCK, the
# caseless necessary run (litscan_s4.md §6.1-§6.2's C3 table; D144 item 1 and
# addendum 1), for the manager to run on the Linux box (ubuntubudu, Ryzen,
# gcc 15.2) through the executor channel. NOT for the Mac: no darwin clock is
# citable. Nothing here writes inside either repo: the bench's subject
# generators are imported with their output paths pointed under $S4A, and
# every regenerated subject is sha256-checked against the bench's COMMITTED
# manifest (a mismatch means off-pin: STOP).
#
#   PCREC_REPO=/home/duxevents/pcrec  BENCH=/home/duxevents/pcrec-bench \
#   BASE_REV=<abi-58 commit>  NEW_REV=<C3 commit>  bash alpha_c3.sh [build|check|time|all]
#
# BASE is the commit before C3 (lane/r1land's tip, abi 58); NEW is C3 (abi 59);
# DENY is NEW with -fno-req-run-fold. C3's deny is FACT-LEVEL and masked out of
# rx_info.flags, so DENY's artifact must equal BASE's apart from the abi digit
# alone -- checked by `check` before anything is timed -- which makes BASE/DENY
# the noise floor of each cell (the same program twice).
#
# THE CELLS: the one measured customer (union-select, nocaps and caps), the
# census's bench movers (litscan_s4.md §2.3.7: 11 on the auto route), the
# class-C movers the single ranking adds (slack, http-5xx), byte-identical
# controls of both census classes (A0: no run before or after; B: the same
# exact run), and union-select's per-CALL cell on its short search subjects
# (the F1/F6 per-call-constant risk). Per D144 addendum 1 every TIMED LOOP is
# calibrated to >= 50 ms (the find-all, or the per-call search, repeated R
# times), and the report is ABSOLUTE deltas beside the floor |DENY - BASE|,
# ns per subject byte for throughput cells and ns per CALL for per-call cells,
# never a ratio; a delta inside the floor reads NULL.
set -u
S4A=${S4A:-/tmp/s4alpha_c3}
PCREC_REPO=${PCREC_REPO:-/home/duxevents/pcrec}
BENCH=${BENCH:-/home/duxevents/pcrec-bench}
BASE_REV=${BASE_REV:?set BASE_REV to the abi-58 commit (lane/r1land tip)}
NEW_REV=${NEW_REV:?set NEW_REV to the C3 commit}
CC=${CC:-gcc}
CPU=${CPU:-2}
LAUNCHES=${LAUNCHES:-5}
PASSES=${PASSES:-5}
STEP=${1:-all}
mkdir -p "$S4A"
cd "$S4A" || exit 2

CAP="cap:t-64k cap:t-256k cap:t-1m"
SYN="syn:t-64k syn:t-256k syn:t-1m"
U8="u8:t-64k u8:t-256k u8:t-1m"
LOG="log:t-064k-fail log:t-256k-fail log:t-1024k-fail log:t-1024k-hit"
# name|kind (W witness / C control)|bench pattern|flags|subjects
CELLS=(
  "union-nocaps|W|capability/patterns/wild-waf-crs-942270-union-select.rx|--no-captures|$CAP"
  "union-caps|W|capability/patterns/wild-waf-crs-942270-union-select.rx||$CAP"
  "slack-nocaps|W|capability/patterns/wild-secrets-slack-webhook-url.rx|--no-captures|$CAP"
  "slack-caps|W|capability/patterns/wild-secrets-slack-webhook-url.rx||$CAP"
  "userpass|W|capability/patterns/wild-secrets-username-password-pair.rx||$CAP"
  "http-5xx|W|loglines/patterns/http-5xx.rx||$LOG"
  "mod-i|W|syntax/patterns/mod-i.rx||$SYN"
  "mod-r|W|syntax/patterns/mod-r.rx||$SYN"
  "cls-fold-pair|W|syntax/patterns/cls-fold-pair.rx||$SYN"
  "cls-pair-ctl|W|syntax/patterns/cls-pair-ctl.rx||$SYN"
  "ci-ascii-ctl|W|utf8/patterns/ci-ascii-control.rx|-e utf8|$U8"
  "ci-strasse|W|utf8/patterns/ci-strasse.rx|-e utf8|$U8"
  "alt-shared|W|utf8/patterns/alt-shared-char.rx|-e utf8|$U8"
  "sleep-ctl|C|capability/patterns/wild-waf-crs-942160-sleep-benchmark.rx||$CAP"
  "dbnames-ctl|C|capability/patterns/wild-waf-crs-942140-dbnames.rx||$CAP"
  "concat-ctl|C|capability/patterns/wild-waf-crs-942360-concat-sqli.rx||$CAP"
  "stackframe-ctl|C|loglines/patterns/stack-frame.rx||$LOG"
  "kvquoted-ctl|C|loglines/patterns/kv-quoted.rx||$LOG"
)
# the per-call cell: union-select's own search_short subjects
PERCALL="union-srch|W|capability/patterns/wild-waf-crs-942270-union-select.rx||short"

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
  python3 - "$BENCH" "$S4A/subj" <<'PY'
import sys, os, hashlib, importlib.util, io, contextlib
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
for tag, setname in (("cap", "capability"), ("syn", "syntax"), ("u8", "utf8"), ("log", "loglines")):
    d = os.path.join(out, tag); os.makedirs(d, exist_ok=True)
    g = load(setname, "gen_throughput_subjects")
    with contextlib.redirect_stdout(io.StringIO()):
        if setname == "loglines":
            g.main(["--out", d])
        else:
            g.OUT, g.MANIFEST = d, os.path.join(d, "manifest_throughput.tsv")
            g.main()
    man = committed(setname, "manifest_throughput.tsv")
    for sid, sha in man.items():
        p = os.path.join(d, sid + ".bin")
        ok = os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == sha
        print("%s:%s %s" % (tag, sid, "OK" if ok else "SHA-MISMATCH")); bad += not ok
# the per-call subjects: capability's short subjects named for union-select
g = load("capability", "gen_subjects")
man = committed("capability", "manifest.tsv")
want = {ln.split("\t")[1] for ln in open(os.path.join(bench, "bench/capability/expectations.tsv"))
        if ln.startswith("wild-waf-crs-942270-union-select\t") and "\tsearch_short\t" in ln}
d = os.path.join(out, "short"); os.makedirs(d, exist_ok=True)
for sid, _desc, body in g.build():
    if sid in want:
        ok = man.get(sid) == hashlib.sha256(body).hexdigest()
        open(os.path.join(d, sid + ".bin"), "wb").write(body)
        print("short:%s %s" % (sid, "OK" if ok else "SHA-MISMATCH")); bad += not ok
sys.exit(1 if bad else 0)
PY
  [ $? -eq 0 ] || { echo "SUBJECT SHA MISMATCH: off-pin, STOP"; exit 1; }
  # D144 addendum 1: a timed loop runs >= 50 ms (R repetitions calibrated
  # from a warm-up pass). Mode `t` is the find-all in ns per subject byte;
  # mode `c` is one search per call in ns per CALL.
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
  for cell in "${CELLS[@]}" "$PERCALL"; do
    IFS='|' read -r name kind pat flags subjects <<<"$cell"
    [ -s "$BENCH/bench/$pat" ] || { echo "NO SUCH PATTERN FILE: $pat"; exit 1; }
    for side in base new deny; do
      bin=base; extra=""
      [ "$side" != base ] && bin=new
      [ "$side" = deny ] && extra=-fno-req-run-fold
      mkdir -p "art/$name/$side"
      # shellcheck disable=SC2086
      "$S4A/$bin/build/pcrec" --features all -p rx $flags $extra \
        -o "art/$name/$side/art.c" --pattern "$(cat "$BENCH/bench/$pat")" || { echo "EMIT FAILED $name $side"; exit 1; }
      "$CC" -O2 -I"art/$name/$side" -o "art/$name/$side/run" drv.c "art/$name/$side/art.c"
    done
  done
}

# no \b: BSD sed silently no-ops it, and this runs on both boxes
norm() { sed -E -e 's/\(abi 5[89]\)/(abi N)/g; s/(PCREC_RX_ABI_H[^0-9]*)5[89]/\1N/g; s/(\.abi = )5[89],/\1N,/' "$1"; }

check() {
  # (1) DENY == BASE modulo the abi digit ALONE (the fact deny restores the
  #     abi-58 program and stamps); (2) a witness's NEW artifact carries a
  #     masked REQ_RUN and differs from BASE, a control's equals BASE modulo
  #     the digit; (3) base, new and deny answer identically on every subject.
  local rc=0
  for cell in "${CELLS[@]}" "$PERCALL"; do
    IFS='|' read -r name kind pat flags subjects <<<"$cell"
    for side in base new deny; do
      [ -s "art/$name/$side/art.c" ] && [ -x "art/$name/$side/run" ] \
        || { echo "NOT BUILT: art/$name/$side (run 'build' first)"; return 1; }
    done
    if cmp -s <(norm "art/$name/base/art.c") <(norm "art/$name/deny/art.c"); then
      echo "DENY==BASE  $name"; else echo "DENY!=BASE  $name  (the floor is not the same program: STOP)"; rc=1; fi
    run=$(sed -n 's/^#define RX_REQ_RUN "\(.*\)"$/\1/p' "art/$name/new/art.c")
    same=0; cmp -s <(norm "art/$name/base/art.c") <(norm "art/$name/new/art.c") && same=1
    case "$kind" in
      C) { [ $same = 1 ] && [ "${run#*/}" = "$run" ]; } || { echo "CONTROL MOVED $name REQ_RUN=$run"; rc=1; } ;;
      *) { [ $same = 0 ] && [ "${run#*/}" != "$run" ]; } || { echo "WITNESS NOT REACHED $name REQ_RUN=$run"; rc=1; } ;;
    esac
    if [ "$name" = union-srch ]; then subjects=$(cd subj/short && ls *.bin | sed 's/\.bin$//; s/^/short:/'); fi
    for s in $subjects; do
      f="subj/${s%%:*}/${s#*:}.bin"; mode=t; [ "$name" = union-srch ] && mode=c
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
  echo "# $(date -u) $(uname -n) load1=$(cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) boost=$(cat /sys/devices/system/cpu/cpufreq/boost 2>/dev/null)"
  printf '%-15s %-22s %-6s %10s %10s %10s  %10s %10s  %s\n' cell subject unit base new deny new-base floor verdict
  for cell in "${CELLS[@]}" "$PERCALL"; do
    IFS='|' read -r name kind pat flags subjects <<<"$cell"
    mode=t; unit=ns/B
    if [ "$name" = union-srch ]; then mode=c; unit=ns/call; subjects=$(cd subj/short && ls *.bin | sed 's/\.bin$//; s/^/short:/'); fi
    for s in $subjects; do
      f="subj/${s%%:*}/${s#*:}.bin"
      while :; do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{exit !($l < 0.5)}" && break; sleep 20; done
      declare -A M=()
      for i in $(seq 1 "$LAUNCHES"); do
        for side in base new deny; do
          v=$(taskset -c "$CPU" "art/$name/$side/run" $mode "$f" "$PASSES" | sed -n 's/.*median=\([0-9.]*\).*/\1/p')
          M[$side]="${M[$side]:-} $v"
        done
      done
      med() { tr ' ' '\n' <<<"$1" | grep . | sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}'; }
      b=$(med "${M[base]}"); n=$(med "${M[new]}"); d=$(med "${M[deny]}")
      dl=$(awk "BEGIN{printf \"%+.5f\", $n-$b}"); fl=$(awk "BEGIN{x=$d-$b; printf \"%.5f\", x<0?-x:x}")
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
