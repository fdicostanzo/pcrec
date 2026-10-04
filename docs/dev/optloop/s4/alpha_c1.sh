#!/bin/bash
# docs/dev/optloop/s4/alpha_c1.sh -- [OPT-LITSCAN] S4 C1's ALPHA BLOCK
# (litscan_s4.md §6.1-§6.2; D144 item 1), for the manager to run on the Linux
# box (ubuntubudu, Ryzen, gcc 15.2) through the executor channel. NOT for the
# Mac: no darwin clock is citable. Nothing here writes inside either repo:
# everything lands under $S4A (default /tmp/s4alpha, the cycle-1 precedent on
# that box).
#
#   PCREC_REPO=/home/duxevents/pcrec  BENCH=/home/duxevents/pcrec-bench \
#   BASE_REV=<C0 commit>  NEW_REV=<C1 commit>  bash alpha_c1.sh [step0|build|check|time|all]
#
# BASE is the commit before C1 (C0, byte-identical to main by its zero-mover
# sweep); NEW is C1. On the lane/r1land stack (C1 landed at abi 58 on top of
# [OPT-VEDGE]'s abi 57) BASE is the [OPT-VEDGE] renumber commit and NEW the
# stack tip — r1land_report.md names both shas; DENY is NEW with -fno-run-overlap. DENY's program must
# equal BASE's apart from the abi digit and the RX_RUN_WORDS line, checked by
# `check` before anything is timed, so BASE/DENY is the noise floor of each
# cell (the same program twice) and a NEW/BASE ratio inside it is a NULL.
#
# Q3 (manager's ruling): the `overlap` row ships only if its alpha shows a
# win beyond that floor on its witnesses; otherwise the manager flips it to
# denied-by-default at merge. The `|` (fused) twins are Q10's alpha twin.
set -u
S4A=${S4A:-/tmp/s4alpha}
PCREC_REPO=${PCREC_REPO:-/home/duxevents/pcrec}
BENCH=${BENCH:-/home/duxevents/pcrec-bench}
BASE_REV=${BASE_REV:?set BASE_REV to the C0 commit}
NEW_REV=${NEW_REV:?set NEW_REV to the C1 commit}
# DENY's flags. NEW here may be a later tip than C1's own commit (r1alpha ran
# it at 8562ff3a, abi 59, which also carries C3), so DENY switches off C3's
# -fno-req-run-fold as well: then DENY == BASE and BASE/DENY is still the
# same program twice. (For NEW = the abi-58 C1 tip, DENYFLAGS=-fno-run-overlap.)
DENYFLAGS=${DENYFLAGS:--fno-run-overlap -fno-req-run-fold}
CC=${CC:-gcc}
CPU=${CPU:-2}
LAUNCHES=${LAUNCHES:-5}
PASSES=${PASSES:-5}
STEP=${1:-all}
mkdir -p "$S4A"
cd "$S4A" || exit 2

# The witness cells (§6.2, C1). name|bench path|flags|subjects
CELLS=(
  "slack-nocaps|capability/patterns/wild-secrets-slack-webhook-url.rx|--no-captures|t-1m t-256k t-64k"
  "router|capability/patterns/router-prefix-order.rx||t-1m t-256k t-64k"
  "keyword-ctl|capability/patterns/keyword-prefix-order.rx||t-1m t-256k t-64k"
)
for L in 3 7 10; do
  CELLS+=("lit-l$L-vm|litrun/patterns/lit-l$L.rx|--engine=vm|mat-l$L fbf-l$L lbf-l$L")
done
for L in 2 4 8 16 31 40; do                     # byte-identical controls
  CELLS+=("lit-l$L-vm-ctl|litrun/patterns/lit-l$L.rx|--engine=vm|mat-l$L fbf-l$L lbf-l$L")
done
TWINS=("slack-nocaps" "lit-l7-vm")              # the fused `|` spelling (Q10)

step0() {
  # [WORD-FOLD]'s owed gcc-15/x86 instruction arm: branch count, constant
  # folding and ASan checks per function (litscan_s4.md §1.4-§1.5, §5.2).
  local d=$PCREC_REPO/docs/dev/optloop/s4
  mkdir -p step0 && cd step0 || return 1
  "$CC" --version | head -1
  for o in -O1 -O2 -Os; do
    "$CC" "$o" -S -o "spell$o.s" "$d/spell.c"
    echo "== spell.c $o: per function, conditional branches and immediates"
    awk '/^[a-z_0-9]+:$/{f=$1} /^\tj[a-z]+ /&&!/jmp/{br[f]++} /\$0x[0-9a-f]{6,}|movabs/{imm[f]++}
         END{for(k in br) printf "  %-28s jcc=%d wide-imm=%d\n", k, br[k], imm[k]}' "spell$o.s" | sort
  done
  for f in one two; do
    "$CC" -O2 -fsanitize=address -S -o "$f.asan.s" "$d/$f.c"
    echo "== $f.c -O2 -fsanitize=address: __asan_report calls $(grep -c '__asan_report' "$f.asan.s")"
  done
  cd "$S4A"
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
  # the subjects, regenerated here and sha256-checked against the bench's
  # committed manifests (a mismatch means off-pin: STOP)
  mkdir -p subj
  python3 - "$BENCH" "$S4A/subj" <<'PY'
import sys, os, hashlib, importlib.util
bench, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, bench)
sys.path.insert(0, os.path.join(bench, "bench/capability"))
import captext as ct
man = {}
for mf in ("bench/capability/manifest_throughput.tsv", "bench/litrun/manifest_throughput.tsv"):
    for ln in open(os.path.join(bench, mf)):
        f = ln.rstrip("\n").split("\t")
        if len(f) >= 3 and f[0] != "id":
            man[f[0]] = f[2]
def put(sid, b):
    open(os.path.join(out, sid + ".bin"), "wb").write(b)
    ok = man.get(sid) == hashlib.sha256(b).hexdigest()
    print(sid, len(b), "OK" if ok else "SHA-MISMATCH")
    if not ok: sys.exit(1)
for sid, n, seed in (("t-64k", 65536, 0xC0FFEE1), ("t-256k", 262144, 0xC0FFEE2), ("t-1m", 1048576, 0xC0FFEE3)):
    put(sid, ct.text(n, seed))
spec = importlib.util.spec_from_file_location("gts", os.path.join(bench, "bench/litrun/gen_throughput_subjects.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)   # defines, writes nothing
for L in g.littext.L_SWEEP:
    for kind, fn, _ in g.KINDS:
        put("%s-l%d" % (kind, L), g.build_one(L, kind, fn))
PY
  [ $? -eq 0 ] || exit 1
  # D144 addendum 1: each TIMED LOOP runs >= ~60 ms (the find-all repeated
  # R times, R calibrated from a warm-up pass), never a single ~30 us pass.
  cat > findall_med.c <<'EOF'
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
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"rb"); fseek(f,0,SEEK_END); long n=ftell(f); rewind(f);
  unsigned char*b=malloc(n); if(fread(b,1,n,f)!=(size_t)n) return 2; fclose(f);
  int passes=argc>2?atoi(argv[2]):5; double t[64]; long count=0;
  double t0=now(); count=findall(b,n); double one=now()-t0;
  long reps=(long)(0.060/(one>1e-9?one:1e-9))+1;
  for(int it=0; it<passes&&it<64; it++){
    t0=now(); for(long r=0;r<reps;r++) count=findall(b,n); t[it]=now()-t0; }
  qsort(t,passes,sizeof t[0],cmpd);
  printf("matches=%ld median=%.6f ns/byte reps=%ld loop=%.1f ms\n", count,
         t[passes/2]*1e9/((double)n*reps), reps, t[passes/2]*1e3);
  return 0; }
EOF
  for cell in "${CELLS[@]}"; do
    IFS='|' read -r name pat flags subjects <<<"$cell"
    mkdir -p "art/$name"
    for side in base new deny; do
      bin=base; extra=""
      [ "$side" != base ] && bin=new
      [ "$side" = deny ] && extra=$DENYFLAGS
      mkdir -p "art/$name/$side"
      # shellcheck disable=SC2086
      "$S4A/$bin/build/pcrec" --features all -p rx $flags $extra \
        -o "art/$name/$side/art.c" --pattern "$(cat "$BENCH/bench/$pat")" || { echo "EMIT FAILED $name $side"; exit 1; }
      "$CC" -O2 -I"art/$name/$side" -o "art/$name/$side/run" findall_med.c "art/$name/$side/art.c"
    done
  done
  for name in "${TWINS[@]}"; do
    mkdir -p "art/$name/fused"
    cp "art/$name/new/art.h" "art/$name/fused/art.h"
    # the fused spelling, one substitution: `A == B && C == D` over one run
    # compare's two words becomes `!((A ^ B) | (C ^ D))` (litscan_s4.md §1.5)
    perl -pe 's/(rx_w([248])\([^()]*\)) == (rx_w\2\("(?:[^"\\]|\\.)*"\)) && (rx_w\2\([^()]*\)) == (rx_w\2\("(?:[^"\\]|\\.)*"\))/!(($1 ^ $3) | ($4 ^ $5))/g' \
      "art/$name/new/art.c" > "art/$name/fused/art.c"
    n=$(grep -c ' ^ ' "art/$name/fused/art.c"); echo "twin $name: $n fused compare line(s)"
    [ "$n" -gt 0 ] || { echo "TWIN NOT APPLIED: $name"; exit 1; }
    "$CC" -O2 -I"art/$name/fused" -o "art/$name/fused/run" findall_med.c "art/$name/fused/art.c"
  done
}

check() {
  # (1) DENY == BASE modulo the abi digit and RX_RUN_WORDS: the noise floor
  #     is the same program twice; (2) NEW writes word compares exactly on the
  #     overlap witnesses and none on the controls; (3) every arm (and every
  #     twin, through waf/check.sh) answers identically on every subject.
  local rc=0
  for cell in "${CELLS[@]}"; do
    IFS='|' read -r name pat flags subjects <<<"$cell"
    for side in base new deny; do
      [ -s "art/$name/$side/art.c" ] && [ -x "art/$name/$side/run" ] \
        || { echo "NOT BUILT: art/$name/$side (run 'build' first)"; return 1; }
    done
    norm() { sed -E -e 's/abi 5[5-9]/abi N/g; s/(PCREC_RX_ABI_H[^0-9]*)5[5-9]/\1N/g; s/(\.abi = )5[5-9]/\1N/; /^#define RX_RUN_WORDS /d' "$1"; }
    if cmp -s <(norm "art/$name/base/art.c") <(norm "art/$name/deny/art.c"); then
      echo "DENY==BASE  $name"; else echo "DENY!=BASE  $name  (the floor is not the same program: STOP)"; rc=1; fi
    w=$(sed -n 's/^#define RX_RUN_WORDS //p' "art/$name/new/art.c")
    case "$name" in *-ctl) [ "$w" = 0 ] || { echo "CONTROL MOVED $name RUN_WORDS=$w"; rc=1; } ;;
                    *) [ "$w" -gt 0 ] || { echo "WITNESS NOT REACHED $name RUN_WORDS=$w"; rc=1; } ;; esac
    for s in $subjects; do
      a=$(art/$name/base/run "subj/$s.bin" 1 | cut -d' ' -f1)
      for side in new deny fused; do
        [ -x "art/$name/$side/run" ] || continue
        b=$(art/$name/$side/run "subj/$s.bin" 1 | cut -d' ' -f1)
        [ "$a" = "$b" ] || { echo "ANSWER DIFF $name $side $s: $a vs $b"; rc=1; }
      done
    done
  done
  for name in "${TWINS[@]}"; do
    for cell in "${CELLS[@]}"; do
      IFS='|' read -r n2 pat flags subjects <<<"$cell"; [ "$n2" = "$name" ] || continue
      ss=""; for s in $subjects; do ss="$ss subj/$s.bin"; done
      # shellcheck disable=SC2086
      sh "$PCREC_REPO/docs/dev/optloop/waf/check.sh" "art/$name/new/art.c" "art/$name/fused/art.c" $ss || rc=1
    done
  done
  echo "check: rc=$rc"; return $rc
}

time_cells() {
  # protocol §6.1: taskset -c $CPU, load1 < 0.5 before each cell, LAUNCHES
  # launches round-robin across the arms, PASSES timed loops each; a cell is
  # the median of the per-launch medians, ns per subject byte.
  echo "# $(date -u) $(uname -n) load1=$(cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) boost=$(cat /sys/devices/system/cpu/cpufreq/boost 2>/dev/null)"
  # D144 addendum 1: ABSOLUTE deltas (ns per subject byte) beside the floor
  # |DENY - BASE| (the same program twice), never a ratio; a delta inside the
  # floor is NULL.
  printf '%-18s %-7s %9s %9s %9s %9s  %9s %9s %9s  %s\n' cell subject base new deny fused new-base floor fused-new verdict
  for cell in "${CELLS[@]}"; do
    IFS='|' read -r name pat flags subjects <<<"$cell"
    for s in $subjects; do
      while :; do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{exit !($l < 0.5)}" && break; sleep 20; done
      declare -A M=(); arms="base new deny"; [ -x "art/$name/fused/run" ] && arms="$arms fused"
      for i in $(seq 1 "$LAUNCHES"); do
        for side in $arms; do
          v=$(taskset -c "$CPU" "art/$name/$side/run" "subj/$s.bin" "$PASSES" | sed -n 's/.*median=\([0-9.]*\).*/\1/p')
          M[$side]="${M[$side]:-} $v"
        done
      done
      med() { tr ' ' '\n' <<<"$1" | grep . | sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}'; }
      b=$(med "${M[base]}"); n=$(med "${M[new]}"); d=$(med "${M[deny]}"); f=$(med "${M[fused]:-}")
      dl=$(awk "BEGIN{printf \"%+.5f\", $n-$b}"); fl=$(awk "BEGIN{x=$d-$b; printf \"%.5f\", x<0?-x:x}")
      fd=-; [ -n "$f" ] && fd=$(awk "BEGIN{printf \"%+.5f\", $f-$n}")
      v=$(awk "BEGIN{x=$n-$b; a=x<0?-x:x; print (a<=$fl)?\"NULL\":(x<0?\"WIN\":\"REGRESSION\")}")
      printf '%-18s %-7s %9s %9s %9s %9s  %9s %9s %9s  %s\n' "$name" "$s" "$b" "$n" "$d" "${f:--}" "$dl" "$fl" "$fd" "$v"
      unset M
    done
  done
}

case "$STEP" in
  step0) step0 ;;
  build) build ;;
  check) check ;;
  time)  time_cells ;;
  all)   step0 && build && check && time_cells ;;
  *) echo "usage: $0 [step0|build|check|time|all]"; exit 2 ;;
esac
