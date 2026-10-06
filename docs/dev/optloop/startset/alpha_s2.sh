#!/usr/bin/env bash
# [START-SET] stage 2 -- THE LINUX ALPHA BLOCK for lane ssbuild2's VM HAT
# (docs/design/startset.md §7; docs/dev/lanes/ssbuild2_report.md; D144 item 1
# and addenda 1 and 3), alpha_k82h.sh's protocol with the VM hat's arms:
#
#   BASE = main before the hat (abi 61), NEW = the VM hat (abi 62),
#   DENY = NEW with -fno-start-set (bit 47, the start-set rows' deny).
#
# THE CELLS have two kinds. `W`: a VM-hat mover under the cell's flags: NEW
# carries `RX_VM_START_SCAN "first-class"` and differs from BASE, and DENY ==
# BASE apart from the abi digits and DENY's `RX_VM_START_SCAN "none"` line,
# so |DENY - BASE| is the floor. `C`: not a mover -- the null band at auto
# (the census shows them DFA-route) -- NEW == BASE == DENY under the same
# normalization. The NULL BAND IS PER CONFIGURATION (cost-F6): the same
# patterns under --engine=vm are W cells (guards), listed separately.
#
# §7's cell list, each with its expected sign:
#   IMPROVE (VM, auto): quoted-delim, balanced-parens-rec, bak-k-named, each on
#     capability/syntax t-1m AND a MATCH-DENSE synthetic subject (cost-F3),
#     plus a SHORT-CALL cell (per call, absolute ns against the floor, K88);
#   IMPROVE (VM, --engine=vm, the pcrec-vm testee): mod-i, mod-r,
#     cls-fold-pair, cls-pair-ctl, ci-strasse, aws (forced);
#   DO-NOT-REGRESS: the auto null band (floor-byte, high-byte-run,
#     uuid-near-miss, union-select, ci-ascii-control) -- C cells; the same
#     under --engine=vm -- W guard cells; the dense-S guards doubled-word and
#     bak-1 (|S| = 63, sign 0); `a(\w)\1` at d = 33% and 80% on match-dense
#     subjects (cost-F1: the table form measured x0.9 there on the Mac, sign
#     0 or -); `e(\w)\1` on prose (d 8.5%); a |S| = 255 `.`-led cell; an
#     S == REQ_BYTE hit-dense cell (cost-F4: the pre-check and the seek read
#     the same byte -- the trigger of the filed VM-hat dominance/handoff row);
#     nested-comment-rec (pre-check-dominated: null expected).
# ABSOLUTE deltas beside the floor, never a ratio; inside the floor reads
# NULL. Any loss past the floor is an issue row (D144 item 3); any wrong
# answer is a disaster.
#
# EVERY READING RECORDS THE LIBC (cost-F7): the time step's header prints
# `ldd --version`'s first line. BOTH [MEMFN] LAYERS (D147): the kit's SIMD
# layer is not built at this pin (no -fmemfn-simd axis), so the scalar layer
# is the only one; set EXTRA_NEW_FLAGS=-fmemfn-simd to re-read the cells when
# it is.
set -u
S2A=${S2A:-/tmp/s2alpha_startset}
PCREC_REPO=${PCREC_REPO:-/home/duxevents/pcrec}
BENCH=${BENCH:-/home/duxevents/pcrec-bench}
BASE_REV=${BASE_REV:?set BASE_REV to main before the VM hat (abi 61)}
NEW_REV=${NEW_REV:?set NEW_REV to the VM hat commit (lane/ssbuild2 tip, abi 62)}
EXTRA_NEW_FLAGS=${EXTRA_NEW_FLAGS:-}
CC=${CC:-gcc}
CPU=${CPU:-2}
LAUNCHES=${LAUNCHES:-5}
PASSES=${PASSES:-5}
STEP=${1:-all}
mkdir -p "$S2A"
cd "$S2A" || exit 2

CAP="cap:t-64k cap:t-1m"
SYN="syn:t-64k syn:t-1m"
U8="u8:t-64k u8:t-1m"
# name|kind (W mover / C control)|pattern (bench path, or lit:<regex>)|flags|subjects
CELLS=(
  "quoted-delim|W|capability/patterns/quoted-delim-match.rx||$CAP dense:quoted"
  "balanced-parens|W|capability/patterns/balanced-parens-rec.rx||$CAP dense:paren"
  "bak-k-named|W|syntax/patterns/bak-k-named.rx||$SYN dense:tag"
  "nested-comment|W|capability/patterns/nested-comment-rec.rx||$CAP"
  "doubled-word|W|capability/patterns/doubled-word.rx||$CAP"
  "bak-1|W|syntax/patterns/bak-1.rx||$SYN"
  "mod-i-vm|W|syntax/patterns/mod-i.rx|--engine=vm|$SYN"
  "mod-r-vm|W|syntax/patterns/mod-r.rx|--engine=vm|$SYN"
  "cls-fold-pair-vm|W|syntax/patterns/cls-fold-pair.rx|--engine=vm|$SYN"
  "cls-pair-ctl-vm|W|syntax/patterns/cls-pair-ctl.rx|--engine=vm|$SYN"
  "ci-strasse-vm|W|utf8/patterns/ci-strasse.rx|-e utf8 --engine=vm|$U8"
  "aws-vm|W|capability/patterns/wild-secrets-aws-access-key-id.rx|--engine=vm|$CAP"
  "floor-byte|C|capability/patterns/floor-byte.rx||$CAP"
  "high-byte-run|C|capability/patterns/high-byte-run.rx||$CAP"
  "uuid-near-miss|C|capability/patterns/uuid-near-miss.rx||$CAP"
  "union-select|C|capability/patterns/wild-waf-crs-942270-union-select.rx||$CAP"
  "ci-ascii-ctl|C|utf8/patterns/ci-ascii-control.rx|-e utf8|$U8"
  "floor-byte-vm|W|capability/patterns/floor-byte.rx|--engine=vm|$CAP"
  "union-select-vm|W|capability/patterns/wild-waf-crs-942270-union-select.rx|--engine=vm|$CAP"
  "ci-ascii-ctl-vm|W|utf8/patterns/ci-ascii-control.rx|-e utf8 --engine=vm|$U8"
  "a-w-1-d33|W|lit:a(\\w)\\1||dense:a33"
  "a-w-1-d80|W|lit:a(\\w)\\1||dense:a80"
  "e-w-1-prose|W|lit:e(\\w)\\1||cap:t-1m"
  "dot-led-255|W|lit:.(a)\\1||cap:t-64k"
  "s-eq-reqbyte|W|lit:(q)\\1q||dense:qhit"
)
# the per-call cells: quoted-delim-match's own search_short subjects, under
# the hat and a control (the seek adds one table walk per call)
PERCALLS=(
  "quoted-srch|W|capability/patterns/quoted-delim-match.rx||short"
  "union-srch|C|capability/patterns/wild-waf-crs-942270-union-select.rx||short"
)

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
for tag, setname in (("cap", "capability"), ("syn", "syntax"), ("u8", "utf8")):
    d = os.path.join(out, tag); os.makedirs(d, exist_ok=True)
    g = load(setname, "gen_throughput_subjects")
    with contextlib.redirect_stdout(io.StringIO()):
        g.OUT, g.MANIFEST = d, os.path.join(d, "manifest_throughput.tsv")
        g.main()
    man = committed(setname, "manifest_throughput.tsv")
    for sid, sha in man.items():
        p = os.path.join(d, sid + ".bin")
        ok = os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == sha
        print("%s:%s %s" % (tag, sid, "OK" if ok else "SHA-MISMATCH")); bad += not ok
# the per-call subjects: capability's short subjects named for quoted-delim-match
g = load("capability", "gen_subjects")
man = committed("capability", "manifest.tsv")
want = {ln.split("\t")[1] for ln in open(os.path.join(bench, "bench/capability/expectations.tsv"))
        if ln.startswith("quoted-delim-match\t") and "\tsearch_short\t" in ln}
d = os.path.join(out, "short"); os.makedirs(d, exist_ok=True)
for sid, _desc, body in g.build():
    if sid in want:
        ok = man.get(sid) == hashlib.sha256(body).hexdigest()
        open(os.path.join(d, sid + ".bin"), "wb").write(body)
        print("short:%s %s" % (sid, "OK" if ok else "SHA-MISMATCH")); bad += not ok
# MATCH-DENSE synthetic subjects (cost-F3), 64 KiB each, seeded: written
# here, hashed into the run's header by the time step (no bench manifest).
d = os.path.join(out, "dense"); os.makedirs(d, exist_ok=True)
def fill(unit):
    return (unit * (65536 // len(unit) + 1))[:65536]
open(os.path.join(d, "quoted.bin"), "wb").write(fill(b'{"key":"value","n":"x\'y"} '))
open(os.path.join(d, "paren.bin"), "wb").write(fill(b"(a(b)c) f(x) (()) "))
open(os.path.join(d, "tag.bin"), "wb").write(fill(b"<a>x</a> <bb>yy</bb> <c>"))
for name, dens in (("a33", 0.33), ("a80", 0.80)):
    r = random.Random(0x5527 + int(dens * 100))
    other = b"bcdefgh"
    open(os.path.join(d, name + ".bin"), "wb").write(bytes(
        ord("a") if r.random() < dens else r.choice(other) for _ in range(65536)))
open(os.path.join(d, "qhit.bin"), "wb").write(fill(b"qa qb qqx q "))
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

  for cell in "${CELLS[@]}" "${PERCALLS[@]}"; do
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

# no \b: BSD sed silently no-ops it, and this runs on both boxes. NEW's
# `RX_VM_START_SCAN "none"` line is on every artifact (D148 Q-R6) and BASE
# has none, so it goes too; a mover's "first-class" stays, so a mover still
# differs from BASE.
norm() { sed -E -e 's/\(abi (61|62)\)/(abi N)/g; s/(PCREC_RX_ABI_H[^0-9]*)(61|62)/\1N/g; s/(\.abi = )(61|62),/\1N,/' -e '/^#define RX_VM_START_SCAN "none"$/d' "$1"; }

check() {
  # (1) a W cell's NEW carries RX_VM_START_SCAN "first-class" and differs from
  #     BASE, and DENY == BASE (modulo the digits and DENY's "none" line: bit
  #     47 is in strategy_denials); (2) a C cell's three artifacts are equal
  #     under the same normalization; (3) base, new and deny answer
  #     identically on every subject.
  local rc=0
  for cell in "${CELLS[@]}" "${PERCALLS[@]}"; do
    IFS='|' read -r name kind pat flags subjects <<<"$cell"
    for side in base new deny; do
      [ -s "art/$name/$side/art.c" ] && [ -x "art/$name/$side/run" ] \
        || { echo "NOT BUILT: art/$name/$side (run 'build' first)"; return 1; }
    done
    same() { cmp -s <(norm "art/$name/$1/art.c") <(norm "art/$name/$2/art.c"); }
    case "$kind" in
      W) { grep -qE '^#define RX_VM_START_SCAN "first-class"$' "art/$name/new/art.c" && ! same base new && same base deny; } \
           || { echo "W-CELL WRONG $name: want NEW on the VM hat and != BASE, DENY == BASE"; rc=1; } ;;
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
  echo "# libc: $(ldd --version 2>&1 | head -1) | layers: scalar${EXTRA_NEW_FLAGS:+ + $EXTRA_NEW_FLAGS} | dense subjects: $(cat subj/dense/*.bin | sha256sum 2>/dev/null | cut -c1-16)"
  echo "# $(date -u) $(uname -n) load1=$( [ "${DARWIN:-0}" = 1 ] && sysctl -n vm.loadavg | cut -d' ' -f2 || cut -d' ' -f1 /proc/loadavg) gov=$(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null) boost=$(cat /sys/devices/system/cpu/cpufreq/boost 2>/dev/null)"
  printf '%-15s %-22s %-6s %10s %10s %10s  %10s %10s  %s\n' cell subject unit base new deny new-base floor verdict
  for cell in "${CELLS[@]}" "${PERCALLS[@]}"; do
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
