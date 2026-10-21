#!/bin/bash
# flat/build.sh OUT -- builds the flat slot (compile only, no clock; writes ONLY under OUT).
#
# grid1's ext-arm-set shape, as e8min/e8build.sh: OUT/ext/flat/arms.tsv declares the cells, OUT/bin/<cell>/<arm>/run
# is the timed driver (grid1/gdrv.c linked with the arm's art.c), OUT/subj/<name> the subjects (read-only symlinks to
# the e8 slot's copies and to grid2's streamed directories). Arms per cell: walk (base), V1, F8, F64, M64. walk and
# V1 are the e8 slot's own emitted texts (the kit compiler at worktrees/memfn-r17, walk = --memfn=no-pf-terms-mask);
# F8/F64/M64 are mkarms.py's hand edits of V1's text. Anchors take grid2's own walk/V1 texts. Every arm is compiled
# here from its art.c with the same flags (-O2), so the five arms differ only in the candidate producer.
# Also builds, per cell: OUT/bat/<cell>/<arm> (the battery, fbat.c, -O2), <arm>.san (ASan+UBSan), and the two
# plants F8.stale / F64.tail / F64.stale; OUT/bat/<cell>/members (the walk's start-byte set as hex) and corpus (a real subject).
set -u
OUT=${1:?usage: build.sh OUT}
HERE=$(cd "$(dirname "$0")" && pwd)
G1=$(cd "$HERE/../grid1" && pwd)
E8=${E8:-/home/pcrec/projects/pcrec/worktrees/e8min/build/e8slot_r2}
GRID2=${GRID2:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2}
CPUS=${CPUS:-12-15}; JOBS=${JOBS:-4}; CC=${CC:-gcc}
mkdir -p "$OUT/tmp" "$OUT/subj" "$OUT/lib" "$OUT/bin" "$OUT/bat" "$OUT/ext/flat" "$OUT/res" "$OUT/ans" "$OUT/time"
TMPDIR=$OUT/tmp; export TMPDIR
L=$OUT/lib
cp "$G1/gdrv.c" "$G1/gload.h" "$G1/keep.h" "$L/"; cp "$HERE/fbat.c" "$L/"
printf '# no own cells: flat is an ext arm set\n' > "$OUT/arms.tsv"; cp "$OUT/arms.tsv" "$OUT/arms_f2.tsv"
printf 'name\tfamily\tn\tg\tL\tshape\treuse\tnbuf\tplanted_matches\tplanted_landings\n' > "$OUT/subj_facts.tsv"
: > "$OUT/oracle.tsv"
{ echo "# flat build provenance $(date -u)"; echo "e8_slot=$E8"; echo "grid2=$GRID2"; echo "gcc=$($CC --version | head -1)"
  echo "flat_commit=$(git -C "$HERE" rev-parse HEAD 2>/dev/null)"; } > "$OUT/provenance.txt"

# cell -> (source dir of walk/V1 art.c, subjects)
CELLS="j1-L10 j1-P14 j1-C16 j1-N08 j1-N10 j1-B10 j1-P05 j1-P12 an-dig an-dfa-hat"
src_of() { case "$1" in an-*) echo "$GRID2/bin/${1#an-}" ;; *) echo "$E8/bin/$1" ;; esac; }
subj_of() {
  case "$1" in
    an-dig) echo g2-dig-n64k-g8-L1k-reg-S ;;
    an-dfa-hat) echo g2-dfa-hat-n64k-ginf-L32-S ;;
    *) awk -F'\t' -v c="$1" '$1==c && $2=="walk" {print $4}' "$E8/ext/e8/arms.tsv" | tr , ' ' ;;
  esac
}
: > "$OUT/ext/flat/arms.tsv"; echo "# flat's ext arm table: cell arm role subjects modes" >> "$OUT/ext/flat/arms.tsv"
for c in $CELLS; do
  ss=$(subj_of "$c"); [ -n "$ss" ] || { echo "build: no subjects for $c"; exit 1; }
  for s in $ss; do ln -sfn "$(readlink -f "$E8/subj/$s" 2>/dev/null || echo "$GRID2/subj/$s")" "$OUT/subj/$s"; done
  list=$(echo $ss | tr ' ' ,)
  for a in walk V1 F8 F64 M64; do
    r=arm; [ "$a" = walk ] && r=base
    printf '%s\t%s\t%s\t%s\tall\n' "$c" "$a" "$r" "$list" >> "$OUT/ext/flat/arms.tsv"
  done
done

build_cell() {   # CELL: write every arm's art.c, link run + battery binaries
  c=$1; src=$(src_of "$c"); d=$OUT/bin/$c; bd=$OUT/bat/$c; mkdir -p "$bd"
  for a in walk V1 F8 F64 M64 F8.stale F64.tail F64.stale; do
    ad=$d/$a; mkdir -p "$ad"; cp "$src/V1/art.h" "$ad/art.h"
    case "$a" in
      walk) cp "$src/walk/art.c" "$ad/art.c"; cp "$src/walk/art.h" "$ad/art.h" ;;
      V1) cp "$src/V1/art.c" "$ad/art.c" ;;
      F8.stale) python3 -I "$HERE/mkarms.py" "$src/V1/art.c" F8 stale > "$ad/art.c" || return 1 ;;
      F64.tail) python3 -I "$HERE/mkarms.py" "$src/V1/art.c" F64 tail > "$ad/art.c" || return 1 ;;
      F64.stale) python3 -I "$HERE/mkarms.py" "$src/V1/art.c" F64 stale > "$ad/art.c" || return 1 ;;
      *) python3 -I "$HERE/mkarms.py" "$src/V1/art.c" "$a" > "$ad/art.c" || return 1 ;;
    esac
    $CC -O2 -I"$ad" -I"$L" -c "$ad/art.c" -o "$ad/art.o" || { echo "COMPILE FAILED $c $a"; return 1; }
    case "$a" in *.*) ;; *)
      $CC -O2 -I"$ad" -I"$L" -c "$L/gdrv.c" -o "$ad/gdrv.o" && $CC -o "$ad/run" "$ad/gdrv.o" "$ad/art.o" \
        || { echo "LINK FAILED $c $a"; return 1; }
      $CC -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all -I"$ad" -o "$bd/$a.san" "$L/fbat.c" "$ad/art.c" \
        || { echo "SAN FAILED $c $a"; return 1; } ;;
    esac
    $CC -O2 -o "$bd/$a" "$L/fbat.c" "$ad/art.o" || { echo "BAT FAILED $c $a"; return 1; }
  done
  # the walk's skip table (the one its skip loop reads) as a 256-bit hex set; a real subject for the battery's slices
  python3 -I - "$d/walk/art.c" > "$bd/members" <<'PY' || return 1
import re, sys
t = open(sys.argv[1]).read()
tab = re.findall(r"!(\w+)\[subject\[scan_position\]\]\) scan_position\+\+;", t)
assert len(tab) == 1, tab
m = re.search(r"%s\[256\] = \{(.*?)\};" % tab[0], t, re.S)
v = [int(x) for x in m.group(1).replace("\n", " ").split(",") if x.strip()]
assert len(v) == 256
print("".join("%x" % sum(v[4 * i + k] << k for k in range(4)) for i in range(64)))
PY
  s=$(subj_of "$c" | awk '{print $1}'); p=$OUT/subj/$s; [ -d "$p" ] && p=$p/b00000
  ln -sfn "$(readlink -f "$p")" "$bd/corpus"
  cmp -s "$d/walk/art.c" "$d/V1/art.c" && { echo "SAME TEXT $c"; return 1; }
  return 0
}
export -f build_cell src_of subj_of; export OUT L CC HERE E8 GRID2
printf '%s\n' $CELLS | taskset -c "$CPUS" xargs -P "$JOBS" -I{} bash -c 'build_cell {} || echo FAIL {}' > "$OUT/tmp/build.log" 2>&1
grep -E 'FAIL|FAILED|SAME' "$OUT/tmp/build.log" && { echo "build: FAILED (see $OUT/tmp/build.log)"; exit 1; }
python3 -I "$G1/arms.py" "$OUT" validate all > "$OUT/tmp/validate.out" 2>&1 || { cat "$OUT/tmp/validate.out"; echo "build: arm tables invalid"; exit 1; }
tail -1 "$OUT/tmp/validate.out"
echo "build: done cells=$(echo $CELLS | wc -w) groups=$(python3 -I "$G1/arms.py" "$OUT" groups timed | wc -l)"
