#!/bin/bash
# grid1/plants.sh -- the gate's failing direction. Each plant is a one-line
# sabotage (of a generated arm, of a base walk, of the driver, of the
# generator, of an ext arm set); check.sh's OWN legs (checklib.sh) must
# report it. Builds and writes only under $OUT/plants/; a planted binary is
# linked into bin/<cell>/plant-<name>/ for the duration of its legs and
# removed after. Run after a green check.sh (the deep legs read $OUT/ans).
#
#   OUT=... bash plants.sh      -> $OUT/plants.log, "plants: ALL DETECTED"
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid1}
CPUS=${CPUS:-12-15}
JOBS=${JOBS:-4}
T=gnutimeout
export OUT T HERE
export ASAN_OPTIONS=detect_leaks=1 UBSAN_OPTIONS=print_stacktrace=1
P=$OUT/plants; rm -rf "$P"; mkdir -p "$P"
RES=$P/res; mkdir -p "$RES"; export RES
TMPDIR=$OUT/tmp; export TMPDIR
. "$HERE/checklib.sh"
L=$OUT/lib
fails=0

# name | cell | arm | file (art|drv) | old => new | what it breaks
ART_PLANTS=(
"lowerbound|hex-run|V3|art|if ((size_t)(lo - c->base) < (size_t)(c->top - c->base)) {=>if (lo < c->top) {|the cache test without its lower bound: a backward lo reads the cache"
"overread|dig|V3|art|size_t b = hi - 8;=>size_t b = hi - 7;|the overlapped tail block one byte late: reads s[n]"
"headoff|dfa-hat|V2|art|VS_RET(i, VS_HEADHIT());=>VS_RET(i + 1, VS_HEADHIT());|the prologue answers one past its hit"
"lanes16|hex-run|S1|art|<< 16)=><< 15)|SSE2 lane mask of the second load shifted wrong"
"lanes32|dig|A3|art|<< 32)=><< 31)|AVX2 lane mask of the second load shifted wrong (kept form)"
"noaligntest|word-eq|A2|art|& 31)) {=>& 0)) {|the AVX2 prologue skipped: the 'aligned' load is unaligned"
"sntail|bounded|Sn|art|>> (i - b);=>>> (i - b + 1);|the stateless tail block's shift one lane off"
"anlanes|dfa-hat|An|art|<< 32)=><< 31)|the stateless AVX2 lane mask shifted wrong"
"drvcycle|dig|V1|drv|if (++cur == gnbuf) cur = 0;=>cur = 0;|the streamed timed loop re-times buffer 0 forever (answers unchanged)"
)
plant_art() {   # src-file dst-file old new
  python3 -I - "$1" "$2" "$3" "$4" <<'EOF'
import sys
t = open(sys.argv[1]).read(); o, n = sys.argv[3], sys.argv[4]
assert t.count(o) >= 1, "anchor not found: " + o
open(sys.argv[2], "w").write(t.replace(o, n, 1))
EOF
}
score() {   # name what -> DETECTED/UNDETECTED line from $RES/*plant-name*
  local name=$1 why=$2 nf nok v
  nf=$(cat "$RES"/*"$name"* 2>/dev/null | grep -c ' FAIL\| RC=')
  nok=$(cat "$RES"/*"$name"* 2>/dev/null | grep -c ' OK$')
  [ "$nf" -gt 0 ] && v=DETECTED || { v=UNDETECTED; fails=1; }
  echo "PLANT $name: $v  legs FAIL=$nf OK=$nok  first: $(cat "$RES"/*"$name"* 2>/dev/null | grep -m1 ' FAIL\| RC=' | cut -c1-150)  -- $why"
}
for p in "${ART_PLANTS[@]}"; do
  IFS='|' read -r name cell V kind repl why <<<"$p"
  old=${repl%%=>*}; new=${repl#*=>}
  d=$P/$name; mkdir -p "$d"; src=$OUT/bin/$cell/$V
  cp "$src/art.h" "$d/"
  av=""; case "$V" in A*) av=-mavx2 ;; esac
  kd=""; case "$V" in V3|S3|A3) kd=-DKEEP ;; esac
  if [ "$kind" = drv ]; then
    cp "$src/art.c" "$d/art.c"
    plant_art "$L/gdrv.c" "$d/gdrv.c" "$old" "$new" || { echo "PLANT $name: anchor not found"; fails=1; continue; }
    drv=$d/gdrv.c
  else
    plant_art "$src/art.c" "$d/art.c" "$old" "$new" || { echo "PLANT $name: anchor not found"; fails=1; continue; }
    drv=$L/gdrv.c
  fi
  I="-I$d -I$L"
  taskset -c "$CPUS" gcc -O2 $av $kd $I -o "$d/run" "$drv" "$d/art.c" &&
  taskset -c "$CPUS" gcc -O2 $av $kd $I -o "$d/chk" "$L/gchk.c" "$d/art.c" &&
  taskset -c "$CPUS" gcc -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all $av $kd -DVS_DEBUG $I -o "$d/chka" "$L/gchk.c" "$d/art.c" ||
    { echo "PLANT $name: build failed"; fails=1; continue; }
  b=$OUT/bin/$cell/plant-$name; mkdir -p "$b"; ln -sf "$d/run" "$b/run"; ln -sf "$d/chk" "$b/chk"; ln -sf "$d/chka" "$b/chka"
  # the group legs over every group of the cell (the arm in place of the base's partner), then the deep legs
  python3 -I "$HERE/arms.py" "$OUT" groups all | awk -F'\t' -v c="$cell" '$1==c{print $1"\t"$2"\t"$3"\twalk,plant-'"$name"'"}' |
    sort -u > "$P/$name.groups"
  RES=$RES/$name; mkdir -p "$RES"; export RES
  taskset -c "$CPUS" xargs -P "$JOBS" -L1 -a "$P/$name.groups" bash -c 'group "$0" "$1" "$2" "$3"' 2>> "$P/$name.stderr"
  [ "$kind" = art ] && taskset -c "$CPUS" bash -c "deep_one $cell plant-$name" 2>> "$P/$name.stderr"
  RES=$P/res; export RES
  rm -rf "$b"
  # keep only the plant arm's own legs (the walk's lines in a group file are not the plant's)
  cat "$RES/$name"/* | grep " plant-$name " > "$RES/plant-$name.legs"; rm -rf "$RES/$name"
  score "plant-$name" "$why"
done

# the BASE walk: a planted walk must fail leg O (the oracle), not merely disagree with its arms
name=walktable; d=$P/$name; mkdir -p "$d"; cp "$OUT/bin/dig/walk/art.h" "$d/"
python3 -I - "$OUT/bin/dig/walk/art.c" "$d/art.c" <<'EOF'
import re, sys
t = open(sys.argv[1]).read()
i = t.index("rx_can_begin_match[256] = {")
j = t.index("};", i)
body = t[i:j]
# zero the entry for '7' (0x37): the 56th number in the table
nums = list(re.finditer(r"\b[01]\b", body))
assert len(nums) == 256, len(nums)
m = nums[0x37]; assert m.group() == "1"
body = body[:m.start()] + "0" + body[m.end():]
open(sys.argv[2], "w").write(t[:i] + body + t[j:])
EOF
taskset -c "$CPUS" gcc -O2 -I"$d" -I"$L" -o "$d/run" "$L/gdrv.c" "$d/art.c" || { echo "PLANT $name: build failed"; fails=1; }
b=$OUT/bin/dig/plant-$name; mkdir -p "$b"; ln -sf "$d/run" "$b/run"
python3 -I "$HERE/arms.py" "$OUT" groups all | awk -F'\t' '$1=="dig"{print $1"\t"$2"\t"$3"\tplant-walktable"}' | sort -u > "$P/$name.groups"
RES=$RES/$name; mkdir -p "$RES"; export RES
taskset -c "$CPUS" xargs -P "$JOBS" -L1 -a "$P/$name.groups" bash -c 'group "$0" "$1" "$2" "$3"'
RES=$P/res; export RES; rm -rf "$b"
cat "$RES/$name"/* | grep " O " > "$RES/plant-$name.legs"; rm -rf "$RES/$name"
score "plant-$name" "the base walk's start table drops '7': leg O (python re) must see it"

# an EXT arm set whose arm answers wrong: check's group legs must exclude it
name=extwrong; e=$P/ext_$name; mkdir -p "$e"
printf 'dig\tplant-%s\tarm\t%s\tall\n' "$name" "g1-dig-n64k-g8-L1k-u,g1-dig-n64k-g2-L32" > "$e/arms.tsv"
b=$OUT/bin/dig/plant-$name; mkdir -p "$b"; ln -sf "$P/lanes32/run" "$b/run"      # ext arms carry only `run`
grep -v '^#' "$e/arms.tsv" | while IFS=$'\t' read -r c a r s m; do for x in ${s//,/ }; do printf '%s\t%s\t%s\twalk,%s\n' "$c" "$x" "$m" "$a"; done; done > "$P/$name.groups"
RES=$RES/$name; mkdir -p "$RES"; export RES
taskset -c "$CPUS" xargs -P "$JOBS" -L1 -a "$P/$name.groups" bash -c 'group "$0" "$1" "$2" "$3"'
RES=$P/res; export RES; rm -rf "$b"
cat "$RES/$name"/* | grep " plant-$name " > "$RES/plant-$name.legs"; rm -rf "$RES/$name"
score "plant-$name" "an ext arm (run only, no chk) answering wrong: leg R"

# the GENERATOR: a match token that does not match must trip the planted-count self-check
name=gentoken
if python3 -I - "$HERE/grid.py" "$P/gen" <<'EOF' > "$P/$name.out" 2>&1
import importlib.util, os, sys
s = importlib.util.spec_from_file_location("grid", sys.argv[1]); g = importlib.util.module_from_spec(s); s.loader.exec_module(g)
c = list(g.CELLS["dig"]); c[3] = [b"%dy"]; g.CELLS["dig"] = tuple(c)     # "5y" is not a match of [0-9]+x
os.makedirs(os.path.join(sys.argv[2], "subj"), exist_ok=True)
g.gen_one((sys.argv[2], "g1-dig-n64k-g8-L1k-u", "dig", 65536, 8, 1024, "u", "rep"))
EOF
then echo "PLANT plant-$name: UNDETECTED -- the generator accepted a token that does not match"; fails=1
else echo "PLANT plant-$name: DETECTED  $(grep -m1 'SELF-CHECK' "$P/$name.out" | cut -c1-150)  -- a non-matching match token: gen's planted-count self-check"; fi

# REACH: a no-member subject WITHOUT the required byte must read uses=0 and be listed by leg U's predicate
name=reachgate
python3 -I - "$P/$name.subj" <<'EOF'
import sys, random
r = random.Random(7); f = b"abcdefghijklmnopqrstuvwyz .,;-"
open(sys.argv[1], "wb").write(bytes(r.choice(f) for _ in range(65536)))
EOF
line=$("$OUT/bin/dig/G1/cnt" "$P/$name.subj" list first 2>&1 >/dev/null | tail -1)
if printf 'dig\tsite(G1)\tx\tfirst\t%s\n' "$line" | awk -F'\t' '$2=="site(G1)" && $5 ~ /(^| )uses=0 /' | grep -q .; then
  echo "PLANT plant-$name: DETECTED  ($line)  -- a member-free subject lacking 'x': the pre-check answers, leg U lists it"
else echo "PLANT plant-$name: UNDETECTED ($line)"; fails=1; fi

# LANDING FIDELITY: dfa-hat landings inside a LETTER filler are walked by the DFA, not
# landed by the hat (the defect leg G found in grid1's own first design): leg G must flag it
name=letterfill
python3 -I - "$HERE/grid.py" "$P/$name" <<'EOF2' > "$P/$name.facts"
import importlib.util, os, sys
s = importlib.util.spec_from_file_location("grid", sys.argv[1]); g = importlib.util.module_from_spec(s); s.loader.exec_module(g)
c = list(g.CELLS["dfa-hat"]); c[1] = b"abcdeghijklmopqrsuvwxyz"; g.CELLS["dfa-hat"] = tuple(c)
os.makedirs(os.path.join(sys.argv[2], "subj"), exist_ok=True)
print(g.gen_one((sys.argv[2], "g1-dfa-hat-n64k-g8-L1k-u", "dfa-hat", 65536, 8, 1024, "u", "rep")))
EOF2
line=$("$OUT/bin/dfa-hat/G1/cnt" "$P/$name/subj/g1-dfa-hat-n64k-g8-L1k-u" list all 2>&1 >/dev/null | tail -1)
uses=$(sed -n 's/^uses=\([0-9]*\).*/\1/p' <<<"$line"); want=$(awk -F'\t' '{print $9 + $10}' "$P/$name.facts")
if awk -v u="$uses" -v w="$want" 'BEGIN{exit !(u < w - 0.10 * w - 1)}'; then
  echo "PLANT plant-$name: DETECTED  (site uses=$uses, planted landings+matches=$want)  -- landings the DFA walks, not the hat: leg G"
else echo "PLANT plant-$name: UNDETECTED (uses=$uses want=$want)"; fails=1; fi

echo "plants: $([ $fails = 0 ] && echo ALL DETECTED || echo SOME UNDETECTED)"
[ $fails = 0 ]
