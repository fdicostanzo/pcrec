#!/bin/bash
# e8min/e8build.sh OUT -- builds E8's slot directory (compile only, no clock; writes ONLY under OUT).
#
# The slot is grid1's ext-arm-set shape (docs/dev/lanes/grid1/README.md): OUT/ext/e8/arms.tsv declares the cells,
# OUT/bin/<cell>/<arm>/run is the timed driver (grid1/gdrv.c linked with the arm's artifact), OUT/subj/<name> the
# subjects. Two kinds of cell (e8design.py plan):
#   j1-<qid>  a census mover. walk = the kit compiler under --memfn=no-pf-terms-mask (main's walk, shown equal by
#             b4prep/walkcmp), V1 = the same compiler's default compile (V1 at every set site). The pattern and its
#             extra argv come from j1_patterns.tsv; both texts must differ (a mover whose V1 text equals the walk's
#             is a census/compiler disagreement: FATAL).
#   an-<fam>  grid2's own anchor and positive-control cells: grid2's built bin/<fam>/{walk,V1}/run copied as they
#             are (same binaries, same subjects, symlinked read-only from the grid2 slot).
# PCREC = the kit-branch compiler grid2 used (lane/memfn-r17, abi 77: V1 everywhere, knows no-pf-terms-mask).
set -u
OUT=${1:?usage: e8build.sh OUT}
HERE=$(cd "$(dirname "$0")" && pwd)
G1=$(cd "$HERE/../../../../dev/lanes/grid1" && pwd)
PCREC=${PCREC:-/home/pcrec/projects/pcrec/worktrees/memfn-r17/build/pcrec}
GRID2=${GRID2:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2}
CPUS=${CPUS:-12-15}; JOBS=${JOBS:-4}; CC=${CC:-gcc}
[ -x "$PCREC" ] || { echo "FATAL: no compiler at $PCREC"; exit 1; }
"$PCREC" --list-axes 2>/dev/null | grep -q pf-terms-mask || { echo "FATAL: $PCREC lacks --memfn=no-pf-terms-mask"; exit 1; }
mkdir -p "$OUT/tmp" "$OUT/subj" "$OUT/lib" "$OUT/bin" "$OUT/ext/e8" "$OUT/res" "$OUT/ans"
TMPDIR=$OUT/tmp; export TMPDIR OUT PCREC CC HERE
L=$OUT/lib
cp "$G1/gdrv.c" "$G1/gload.h" "$G1/keep.h" "$L/"
# grid1's check.sh/time.sh expect these files; E8 has no own cells, no python oracle, no F2 table
printf '# no own cells: E8 is an ext arm set\n' > "$OUT/arms.tsv"; cp "$OUT/arms.tsv" "$OUT/arms_f2.tsv"
printf 'name\tfamily\tn\tg\tL\tshape\treuse\tnbuf\tplanted_matches\tplanted_landings\n' > "$OUT/subj_facts.tsv"
: > "$OUT/oracle.tsv"
{ echo "# e8 build provenance $(date -u)"; echo "pcrec=$PCREC"; "$PCREC" --version 2>&1 | head -1
  echo "pcrec_sha256=$(sha256sum "$PCREC" | cut -d' ' -f1)"; echo "gcc=$($CC --version | head -1)"
  echo "e8min_commit=$(git -C "$HERE" rev-parse HEAD 2>/dev/null)"; } > "$OUT/provenance.txt"

python3 -I "$HERE/e8design.py" plan > "$OUT/tmp/plan.tsv" || exit 1
python3 -I "$HERE/e8design.py" arms > "$OUT/ext/e8/arms.tsv" || exit 1
# subjects: corpus files are COPIED (f2perf sizes a subject with a plain stat, which on a symlink reads the link's
# length and picks K = 1024 passes: minutes per 40 MiB loser); grid2's streamed directories are symlinked read-only
while IFS=$'\t' read -r kind cell name src q; do
    case "$kind" in J1) [ "$(stat -Lc %s "$OUT/subj/$name" 2>/dev/null)" = "$(stat -c %s "$src")" ] && [ ! -L "$OUT/subj/$name" ] \
                            || { rm -f "$OUT/subj/$name"; cp "$src" "$OUT/subj/$name"; } ;; AN) ln -sfn "$GRID2/subj/$name" "$OUT/subj/$name" ;; esac
done < "$OUT/tmp/plan.tsv"

build_j1() {   # QID: emit both texts, link both drivers
    q=$1
    IFS=$'\t' read -r _ extra pat < <(awk -F'\t' -v q="$q" '$1==q' "$HERE/j1_patterns.tsv")
    [ "$extra" = - ] && extra=; read -ra ex <<< "$extra"
    for a in walk V1; do
        d=$OUT/bin/j1-$q/$a; mkdir -p "$d"; mf=(); [ "$a" = walk ] && mf=(--memfn=no-pf-terms-mask)
        "$PCREC" -p rx --features all "${ex[@]}" "${mf[@]}" -o "$d/art.c" --pattern "$pat" > "$d/emit.out" 2>&1 \
            || { echo "EMIT FAILED j1-$q $a: $(head -1 "$d/emit.out")"; return 1; }
        $CC -O2 -I"$d" -I"$L" -c "$d/art.c" -o "$d/art.o" && $CC -O2 -I"$d" -I"$L" -c "$L/gdrv.c" -o "$d/gdrv.o" \
            && $CC -o "$d/run" "$d/gdrv.o" "$d/art.o" || { echo "COMPILE FAILED j1-$q $a"; return 1; }
    done
    cmp -s "$OUT/bin/j1-$q/walk/art.c" "$OUT/bin/j1-$q/V1/art.c" && { echo "SAME TEXT j1-$q (walk == V1: not a mover for this compiler)"; return 1; }
    return 0
}
export -f build_j1; export L
awk -F'\t' '$1=="J1"{print $5}' "$OUT/tmp/plan.tsv" | sort -u | taskset -c "$CPUS" xargs -P "$JOBS" -I{} bash -c 'build_j1 {} || echo FAIL {}' > "$OUT/tmp/j1.build" 2>&1
grep -E '^(FAIL|EMIT|COMPILE|SAME)' "$OUT/tmp/j1.build" && { echo "e8build: J1 build FAILED"; exit 1; }
for fam in $(awk -F'\t' '$1=="AN"{print $5}' "$OUT/tmp/plan.tsv" | sort -u); do
    for a in walk V1; do
        mkdir -p "$OUT/bin/an-$fam/$a"; cp -L "$GRID2/bin/$fam/$a/run" "$OUT/bin/an-$fam/$a/run" || { echo "e8build: no anchor $fam/$a"; exit 1; }
    done
done
python3 -I "$G1/arms.py" "$OUT" validate all > "$OUT/tmp/validate.out" 2>&1 || { cat "$OUT/tmp/validate.out"; echo "e8build: arm tables invalid"; exit 1; }
tail -1 "$OUT/tmp/validate.out"
echo "e8build: done j1=$(awk -F'\t' '$1=="J1"' "$OUT/tmp/plan.tsv" | wc -l) an=$(awk -F'\t' '$1=="AN"' "$OUT/tmp/plan.tsv" | wc -l) cells"
