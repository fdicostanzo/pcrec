#!/bin/bash
# grid1/build.sh -- build the joint timing slot's OWN arms (and every external
# arm set) under $OUT. Writes ONLY under $OUT. Never edits slot25c or spike1.
# Compiles pinned to CPUS, at most JOBS at once (light work: no clock).
#
#   OUT=... bash build.sh            # design + subjects + arms + ext arms
#   OUT=... bash build.sh --ext      # the external arm sets only (after adding one)
#
# Steps:
#   1. grid.py design + gen (arms.tsv, arms_f2.tsv, subjects.tsv, subj/, the
#      generator's planted-count self-check) unless SKIP_GEN=1; the F2 real
#      subjects are copied from spike1 (read-only);
#   2. $OUT/lib/: gdrv.c gchk.c gload.h keep.h (what an ext arm links);
#   3. art/<cell>/{new,deny}/: slot25c ALPHA's R17-b artifacts (copied), and
#      `quad` (the 4-term cover) emitted by THIS worktree's compiler;
#   4. bin/<cell>/<arm>/{art.c,art.h,art.o,run,chk,chka,cnt} per own arm:
#        walk  = ALPHA deny verbatim (today's table walk; the cell's base)
#        V1    = ALPHA new verbatim (R17-b, mask8_swar)
#        G1    = mkvar(w8,0,0): the generator's V1 (the G1 control below)
#        V2 V3 = SWAR + prologue / + keep          S1 S2 S3 = the same, SSE2 W=64
#        A1 A2 A3 = the same, AVX2 W=64 (-mavx2)   Sn An = STATELESS sse2/avx2
#      run = gdrv.c (+ -DKEEP for V3/S3/A3); chk = gchk.c; chka = gchk.c under
#      ASan+UBSan with mkvar's VS_DEBUG re-probe; cnt = gchk.c + art.c -DVS_COUNT
#      (V1's counting source is G1's; the walk has no cnt: its site counters
#      are G1's, recorded as arm `site`);
#      bin/f3-<cell> -> <cell> (F3's timing cells share the binaries);
#   5. the G1 control: G1's holding function must assemble identically to V1's
#      (the generator reproduces R17-b), and same_first marks a keep arm whose
#      holding function equals its unkept twin's (time.sh skips it in `first`);
#   6. every $OUT/ext/<name>/: `gen_subj` (if executable) then `build.sh`, both
#      with OUT and GRID (this directory) in the environment.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
WT=${WT:-$(cd "$HERE/../../../.." && pwd)}
OUT=${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid1}
ALPHA=${ALPHA:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/slot25c/alpha}
SPIKE=${SPIKE:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/spike1}
CPUS=${CPUS:-12-15}
JOBS=${JOBS:-4}
CC=${CC:-gcc}
CELLS=${CELLS:-"dig bounded dfa-hat hex-run word-eq quad"}
QUAD_PAT='[0-9A-Fa-f_]+='
# cells emitted by THIS worktree's compiler instead of copied from ALPHA: quad, plus any
# "cell=pattern" words in EMIT_CELLS (grid2 adds wcls=\w+= ; unset = grid1 exactly)
declare -A EMIT_PAT=([quad]="$QUAD_PAT")
for kv in ${EMIT_CELLS:-}; do EMIT_PAT[${kv%%=*}]=${kv#*=}; done
grep -qw avx2 /proc/cpuinfo || { echo "FATAL: this box has no AVX2"; exit 1; }
mkdir -p "$OUT/tmp" "$OUT/bin" "$OUT/lib" "$OUT/ext"
TMPDIR=$OUT/tmp; export TMPDIR

build_ext() {
  for e in "$OUT"/ext/*/; do
    [ -d "$e" ] || continue
    n=$(basename "$e")
    if [ -x "$e/gen_subj" ]; then
      echo "ext $n: gen_subj"
      (OUT=$OUT GRID=$HERE taskset -c "$CPUS" "$e/gen_subj") || { echo "EXT $n gen_subj FAILED"; return 1; }
    fi
    [ -f "$e/build.sh" ] || { echo "EXT $n: no build.sh"; return 1; }
    echo "ext $n: build.sh"
    (OUT=$OUT GRID=$HERE CPUS=$CPUS JOBS=$JOBS taskset -c "$CPUS" bash "$e/build.sh") || { echo "EXT $n build FAILED"; return 1; }
    [ -f "$e/arms.tsv" ] || { echo "EXT $n: no arms.tsv"; return 1; }
  done
  echo "ext: done"
}
if [ "${1:-}" = --ext ]; then build_ext; exit $?; fi

# ---- 1. design + subjects
python3 -I "$HERE/grid.py" design "$OUT" || exit 1
if [ "${SKIP_GEN:-0}" != 1 ]; then
  taskset -c "$CPUS" python3 -I "$HERE/grid.py" gen "$OUT" -j "$JOBS" || { echo "GEN FAILED"; exit 1; }
fi
for s in prose1m docs1m code1m prose64k docs64k code64k; do
  [ -s "$OUT/subj/$s" ] || cp "$SPIKE/subj/$s" "$OUT/subj/$s"
done

# ---- 2. the library an ext arm links
cp "$HERE/gdrv.c" "$HERE/gchk.c" "$HERE/gload.h" "$HERE/keep.h" "$OUT/lib/"

# ---- 3. artifacts
for c in $CELLS; do
  for side in new deny; do
    d=$OUT/art/$c/$side; mkdir -p "$d"
    if [ -n "${EMIT_PAT[$c]:-}" ]; then
      [ -x "$WT/build/pcrec" ] || { echo "FATAL: build pcrec in $WT first (make -j4)"; exit 1; }
      extra=""; [ "$side" = deny ] && extra=--memfn=no-pf-terms-mask
      # shellcheck disable=SC2086
      "$WT/build/pcrec" -p rx $extra -o "$d/art.c" --pattern "${EMIT_PAT[$c]}" || { echo "EMIT FAILED $c $side"; exit 1; }
    else
      cp "$ALPHA/art/$c/off/$side/art.c" "$ALPHA/art/$c/off/$side/art.h" "$d/"
    fi
  done
  cmp -s "$OUT/art/$c/new/art.c" "$OUT/art/$c/deny/art.c" && { echo "FATAL: $c new == deny (not a mover)"; exit 1; }
done

# ---- 4. arms: name width align keep (width "-" = a verbatim artifact: new|deny)
VARS="walk - deny 0
V1 - new 0
G1 w8 0 0
V2 w8 1 0
V3 w8 0 1
S1 v16 0 0
S2 v16 1 0
S3 v16 0 1
A1 v32 0 0
A2 v32 1 0
A3 v32 0 1
Sn v16n 0 0
An v32n 0 0"
jobs_file=$OUT/tmp/build.jobs; : > "$jobs_file"
L=$OUT/lib
for c in $CELLS; do
  while read -r V w a k; do
    d=$OUT/bin/$c/$V; mkdir -p "$d"
    if [ "$w" = - ]; then cp "$OUT/art/$c/$a/art.c" "$OUT/art/$c/$a/art.h" "$d/"; k=0
    else python3 -I "$HERE/mkvar.py" "$OUT/art/$c/new/art.c" "$d/art.c" "$w" "$a" "$k" || { echo "MKVAR FAILED $c $V"; exit 1; }
         cp "$OUT/art/$c/new/art.h" "$d/art.h"; fi
    av=""; case "$V" in A*) av=-mavx2 ;; esac
    kd=""; [ "$k" = 1 ] && kd=-DKEEP
    I="-I$d -I$L"
    echo "$CC -O2 $av $I -c $d/art.c -o $d/art.o && $CC -O2 $kd $I -c $L/gdrv.c -o $d/gdrv.o && $CC -o $d/run $d/gdrv.o $d/art.o && $CC -O2 $kd $I -o $d/chk $L/gchk.c $d/art.o" >> "$jobs_file"
    echo "$CC -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all $av $kd -DVS_DEBUG $I -o $d/chka $L/gchk.c $d/art.c" >> "$jobs_file"
    cntsrc=$d/art.c; [ "$V" = V1 ] && cntsrc=$OUT/bin/$c/G1/art.c
    [ "$V" != walk ] && echo "$CC -O2 $av $kd -DVS_COUNT $I -o $d/cnt $L/gchk.c $cntsrc" >> "$jobs_file"
  done <<< "$VARS"
done
echo "build jobs: $(grep -c . "$jobs_file")"
: > "$OUT/tmp/build.out"
tr '\n' '\0' < "$jobs_file" | taskset -c "$CPUS" xargs -0 -P "$JOBS" -I{} bash -c '{} 2>&1' >> "$OUT/tmp/build.out" 2>&1
grep -E 'error|warning' "$OUT/tmp/build.out" | head -20
fail=0
for c in $CELLS; do while read -r V w a k; do
  for b in run chk chka; do [ -x "$OUT/bin/$c/$V/$b" ] || { echo "MISSING $c/$V/$b"; fail=1; }; done
  [ "$V" = walk ] || [ -x "$OUT/bin/$c/$V/cnt" ] || { echo "MISSING $c/$V/cnt"; fail=1; }
done <<< "$VARS"; done
[ "$fail" = 0 ] || { echo "BUILD FAILED (see $OUT/tmp/build.out)"; exit 1; }
for c in dig hex-run word-eq quad; do ln -sfn "$c" "$OUT/bin/f3-$c"; done

# ---- 5. the G1 control and same_first
g1fail=0
for c in $CELLS; do
  dis() { objdump -d --no-show-raw-insn "$1" | awk '$2=="<rx_search>:"{p=1;next} p&&/^$/{exit} p' | sed -E 's/^ *[0-9a-f]+:\t//; s/[0-9a-f]+ <([^>+]+)(\+0x[0-9a-f]+)?>/<\1\2>/'; }
  if cmp -s <(dis "$OUT/bin/$c/V1/art.o") <(dis "$OUT/bin/$c/G1/art.o"); then echo "G1==V1  $c (rx_search assembles identically)"
  else echo "G1!=V1  $c (the generator's w8/0/0 is not R17-b's text)"; g1fail=1; fi
  for p in "V3 V1" "S3 S1" "A3 A1"; do set -- $p
    if cmp -s <(dis "$OUT/bin/$c/$1/art.o") <(dis "$OUT/bin/$c/$2/art.o"); then echo "$1==$2 $c" > "$OUT/bin/$c/$1/same_first"
    else rm -f "$OUT/bin/$c/$1/same_first"; fi
  done
done
echo "same_first: $(ls "$OUT"/bin/*/*/same_first 2>/dev/null | wc -l) keep arms equal their unkept twin in \`first\`"
[ "$g1fail" = 0 ] || { echo "G1 CONTROL FAILED"; exit 1; }

# ---- 6. external arm sets
build_ext || exit 1
echo "build: done"
