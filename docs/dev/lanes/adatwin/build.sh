#!/bin/bash
# adatwin/build.sh OUT -- builds the adatwin slot (compile only, no clock; writes ONLY under OUT). flat/build.sh's
# shape, arms changed: walk (base), V1, M64 (flat's mkarms.py), OBS, ADAPT, ADAPTC, ADAPT1C (adatwin/mkarms.py, hand
# edits of V1's text; the walk's start table copied in for walk mode). Every arm is compiled here from its art.c with
# the same flags (-O2), so the arms differ only in the candidate producer. Per cell also: OUT/bat/<cell>/<arm> (the
# battery, abat.c), <arm>.san (ASan+UBSan), the plants ADAPT.sw / ADAPT.wlo / ADAPTC.sw, and the count builds
# <arm>.cnt (battery) and OUT/bin/<cell>/<arm>/cnt (timed driver) of ADAPT/ADAPTC/ADAPT1C with -DADAPT_COUNT.
set -u
OUT=${1:?usage: build.sh OUT}
HERE=$(cd "$(dirname "$0")" && pwd)
FLAT=$(cd "$HERE/../flat" && pwd)
G1=$(cd "$HERE/../grid1" && pwd)
E8=${E8:-/home/pcrec/projects/pcrec/worktrees/e8min/build/e8slot_r2}
GRID2=${GRID2:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2}
CPUS=${CPUS:-12-15}; JOBS=${JOBS:-4}; CC=${CC:-gcc}
mkdir -p "$OUT/tmp" "$OUT/subj" "$OUT/lib" "$OUT/bin" "$OUT/bat" "$OUT/ext/adatwin" "$OUT/res" "$OUT/ans" "$OUT/time"
TMPDIR=$OUT/tmp; export TMPDIR
L=$OUT/lib
cp "$G1/gdrv.c" "$G1/gload.h" "$G1/keep.h" "$L/"; cp "$HERE/abat.c" "$L/"
printf '# no own cells: flat is an ext arm set\n' > "$OUT/arms.tsv"; cp "$OUT/arms.tsv" "$OUT/arms_f2.tsv"
printf 'name\tfamily\tn\tg\tL\tshape\treuse\tnbuf\tplanted_matches\tplanted_landings\n' > "$OUT/subj_facts.tsv"
: > "$OUT/oracle.tsv"
{ echo "# adatwin build provenance $(date -u)"; echo "e8_slot=$E8"; echo "grid2=$GRID2"; echo "gcc=$($CC --version | head -1)"
  echo "adatwin_commit=$(git -C "$HERE" rev-parse HEAD 2>/dev/null)"; } > "$OUT/provenance.txt"

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
: > "$OUT/ext/adatwin/arms.tsv"; echo "# adatwin's ext arm table: cell arm role subjects modes" >> "$OUT/ext/adatwin/arms.tsv"
for c in $CELLS; do
  ss=$(subj_of "$c"); [ -n "$ss" ] || { echo "build: no subjects for $c"; exit 1; }
  for s in $ss; do ln -sfn "$(readlink -f "$E8/subj/$s" 2>/dev/null || echo "$GRID2/subj/$s")" "$OUT/subj/$s"; done
  list=$(echo $ss | tr ' ' ,)
  for a in walk V1 M64 OBS ADAPT ADAPTC ADAPT1C; do
    r=arm; [ "$a" = walk ] && r=base
    printf '%s\t%s\t%s\t%s\tall\n' "$c" "$a" "$r" "$list" >> "$OUT/ext/adatwin/arms.tsv"
  done
done

build_cell() {   # CELL: write every arm's art.c, link run + battery binaries
  c=$1; src=$(src_of "$c"); d=$OUT/bin/$c; bd=$OUT/bat/$c; mkdir -p "$bd"
  for a in walk V1 M64 OBS ADAPT ADAPTC ADAPT1C ADAPT.sw ADAPT.wlo ADAPTC.sw; do
    ad=$d/$a; mkdir -p "$ad"; cp "$src/V1/art.h" "$ad/art.h"
    case "$a" in
      walk) cp "$src/walk/art.c" "$ad/art.c"; cp "$src/walk/art.h" "$ad/art.h" ;;
      V1) cp "$src/V1/art.c" "$ad/art.c" ;;
      M64) python3 -I "$FLAT/mkarms.py" "$src/V1/art.c" M64 > "$ad/art.c" || return 1 ;;
      *.*) python3 -I "$HERE/mkarms.py" "$src/V1/art.c" "$src/walk/art.c" "${a%%.*}" "${a#*.}" > "$ad/art.c" || return 1 ;;
      *) python3 -I "$HERE/mkarms.py" "$src/V1/art.c" "$src/walk/art.c" "$a" > "$ad/art.c" || return 1 ;;
    esac
    $CC -O2 -I"$ad" -I"$L" -c "$ad/art.c" -o "$ad/art.o" || { echo "COMPILE FAILED $c $a"; return 1; }
    case "$a" in *.*) ;; *)
      $CC -O2 -I"$ad" -I"$L" -c "$L/gdrv.c" -o "$ad/gdrv.o" && $CC -o "$ad/run" "$ad/gdrv.o" "$ad/art.o" \
        || { echo "LINK FAILED $c $a"; return 1; }
      $CC -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all -I"$ad" -o "$bd/$a.san" "$L/abat.c" "$ad/art.c" \
        || { echo "SAN FAILED $c $a"; return 1; }
      case "$a" in ADAPT*)
        $CC -O2 -DADAPT_COUNT -I"$ad" -I"$L" -c "$ad/art.c" -o "$ad/art.cnt.o" && $CC -O2 -o "$bd/$a.cnt" "$L/abat.c" "$ad/art.cnt.o" \
          && $CC -o "$ad/cnt" "$ad/gdrv.o" "$ad/art.cnt.o" || { echo "CNT FAILED $c $a"; return 1; } ;;
      esac ;;
    esac
    $CC -O2 -o "$bd/$a" "$L/abat.c" "$ad/art.o" || { echo "BAT FAILED $c $a"; return 1; }
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
export -f build_cell src_of subj_of; export OUT L CC HERE FLAT E8 GRID2
printf '%s\n' $CELLS | taskset -c "$CPUS" xargs -P "$JOBS" -I{} bash -c 'build_cell {} || echo FAIL {}' > "$OUT/tmp/build.log" 2>&1
grep -E 'FAIL|FAILED|SAME' "$OUT/tmp/build.log" && { echo "build: FAILED (see $OUT/tmp/build.log)"; exit 1; }
python3 -I "$G1/arms.py" "$OUT" validate all > "$OUT/tmp/validate.out" 2>&1 || { cat "$OUT/tmp/validate.out"; echo "build: arm tables invalid"; exit 1; }
tail -1 "$OUT/tmp/validate.out"
echo "build: done cells=$(echo $CELLS | wc -w) groups=$(python3 -I "$G1/arms.py" "$OUT" groups timed | wc -l)"
