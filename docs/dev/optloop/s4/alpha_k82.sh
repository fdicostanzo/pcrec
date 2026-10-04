#!/usr/bin/env bash
# [K82] (A)+(C) -- THE LINUX ALPHA BLOCK for lane k82fix's fix
# (docs/dev/lanes/k82fix_report.md; D144 item 1 and addendum 1), alpha_c3.sh's
# protocol with K82's arms:
#
#   BASE = abi 59 (main 940fa06e, C3 default-on), NEW = the K82 fix (abi 60),
#   DENY = NEW with -fno-req-set-lead (bit 45, the set-leads row's deny).
#
# THE CELLS have three kinds. `A`: a set-leads mover (k82diag_report.md §4.3
# row 4, confirmed by k82_movers.log): NEW != BASE, and DENY == BASE apart
# from the abi digits, so |DENY - BASE| is the floor. `P`: the PICK NONE mover
# (alt-shared): bit 45 does not reach it, so DENY == NEW and the floor is
# |DENY - NEW|. `C`: unchanged by both halves -- C3's customers (union-select,
# ci-ascii-ctl), cause (B)'s movers that this fix deliberately leaves
# (mod-i, cls-fold-pair, ci-strasse: [FINDINGS.B4]'s later design), and
# byte-identical controls -- NEW == BASE == DENY. union-srch is the per-CALL
# cell (union-select's short search subjects), a control. ABSOLUTE deltas
# beside the floor, never a ratio; inside the floor reads NULL.
set -u
S4A=${S4A:-/tmp/s4alpha_k82}
PCREC_REPO=${PCREC_REPO:-/home/duxevents/pcrec}
BENCH=${BENCH:-/home/duxevents/pcrec-bench}
BASE_REV=${BASE_REV:?set BASE_REV to the abi-59 commit (main 940fa06e)}
NEW_REV=${NEW_REV:?set NEW_REV to the K82 fix commit (lane/k82fix tip)}
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
  "userpass|A|capability/patterns/wild-secrets-username-password-pair.rx||$CAP"
  "stack-frame|A|loglines/patterns/stack-frame.rx||$LOG"
  "cls-h|A|syntax/patterns/cls-h.rx||$SYN"
  "cls-n-uc|A|syntax/patterns/cls-n-uc.rx||$SYN"
  "cls-s-lc|A|syntax/patterns/cls-s-lc.rx||$SYN"
  "cls-v|A|syntax/patterns/cls-v.rx||$SYN"
  "mod-s|A|syntax/patterns/mod-s.rx||$SYN"
  "alt-shared|P|utf8/patterns/alt-shared-char.rx|-e utf8|$U8"
  "union-nocaps|C|capability/patterns/wild-waf-crs-942270-union-select.rx|--no-captures|$CAP"
  "union-caps|C|capability/patterns/wild-waf-crs-942270-union-select.rx||$CAP"
  "ci-ascii-ctl|C|utf8/patterns/ci-ascii-control.rx|-e utf8|$U8"
  "mod-i|C|syntax/patterns/mod-i.rx||$SYN"
  "cls-fold-pair|C|syntax/patterns/cls-fold-pair.rx||$SYN"
  "ci-strasse|C|utf8/patterns/ci-strasse.rx|-e utf8|$U8"
  "kvquoted-ctl|C|loglines/patterns/kv-quoted.rx||$LOG"
  "levelctx-ctl|C|loglines/patterns/level-context.rx||$LOG"
)
# the per-call cell: union-select's own search_short subjects
PERCALL="union-srch|C|capability/patterns/wild-waf-crs-942270-union-select.rx||short"

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
      [ "$side" = deny ] && extra=-fno-req-set-lead
      mkdir -p "art/$name/$side"
      # shellcheck disable=SC2086
      "$S4A/$bin/build/pcrec" --features all -p rx $flags $extra \
        -o "art/$name/$side/art.c" --pattern "$(cat "$BENCH/bench/$pat")" || { echo "EMIT FAILED $name $side"; exit 1; }
      "$CC" -O2 -I"art/$name/$side" -o "art/$name/$side/run" drv.c "art/$name/$side/art.c"
    done
  done
}

# no \b: BSD sed silently no-ops it, and this runs on both boxes
norm() { sed -E -e 's/\(abi (59|60)\)/(abi N)/g; s/(PCREC_RX_ABI_H[^0-9]*)(59|60)/\1N/g; s/(\.abi = )(59|60),/\1N,/' "$1"; }

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
    same() { cmp -s <(norm "art/$name/$1/art.c") <(norm "art/$name/$2/art.c"); }
    case "$kind" in
      A) { ! same base new && same base deny; } \
           || { echo "A-CELL WRONG $name: want NEW != BASE, DENY == BASE"; rc=1; } ;;
      P) { ! same base new && same new deny; } \
           || { echo "P-CELL WRONG $name: want NEW != BASE, DENY == NEW"; rc=1; } ;;
      C) { same base new && same base deny; } \
           || { echo "CONTROL MOVED $name"; rc=1; } ;;
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
  # DARWIN=1: the Mac's DIRECTIONAL run (D144 addendum 1: never a verdict) --
  # no taskset, no load wait, load1 from sysctl.
  local pin="taskset -c $CPU"
  if [ "${DARWIN:-0}" = 1 ]; then pin=""; fi
  echo "# $(date -u) $(uname -n) load1=$( [ "${DARWIN:-0}" = 1 ] && sysctl -n vm.loadavg | cut -d' ' -f2 || cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) boost=$(cat /sys/devices/system/cpu/cpufreq/boost 2>/dev/null)"
  printf '%-15s %-22s %-6s %10s %10s %10s  %10s %10s  %s\n' cell subject unit base new deny new-base floor verdict
  for cell in "${CELLS[@]}" "$PERCALL"; do
    IFS='|' read -r name kind pat flags subjects <<<"$cell"
    mode=t; unit=ns/B
    if [ "$name" = union-srch ]; then mode=c; unit=ns/call; subjects=$(cd subj/short && ls *.bin | sed 's/\.bin$//; s/^/short:/'); fi
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
      ref=$b; [ "$kind" = P ] && ref=$n   # P: bit 45 does not reach it, DENY == NEW
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
