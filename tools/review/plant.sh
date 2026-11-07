#!/usr/bin/env bash
# tools/review/plant.sh ROW OUTDIR [REV] -- build a PLANTED compiler for one
# sabotage row, without make and without touching the tree, into
# OUTDIR/tree/build/pcrec. A critic's tool (adopted from code round
# 2026-11-06-r4-vlookbehind-code, whose coordinator wrote it; RULING "process
# change adopted"): a lens re-derives a row's plant against the emitted text it
# claims to break, instead of trusting the row's prose (that round's lesson 1).
#
#   ROW     a row id (`S1963`, resolved under tests/mech/sabotages/ of the tree
#           this script sits in), or the PATH of a row-shaped file of your own
#           (SAB_FILE/SAB_BEFORE/SAB_AFTER[/SAB_COUNT], optional *2 pair).
#   OUTDIR  scratch, under the temp root ($PCREC_TMPDIR/scratch/<lane>/...),
#           never /tmp and never the tree. OUTDIR/tree is replaced.
#   REV     the commit to plant into (default HEAD). The tree's build/obj must
#           have been built from REV: only the planted file is recompiled, the
#           rest of the objects are copied. With the default HEAD and a dirty
#           src/ the copy and the objects disagree; build a clean tree first.
#
# The row is applied with tests/mech/lib/replace.py, the matrix's own applier,
# so SAB_COUNT and the whole-file substring rule are the matrix's. Only
# compiler plants (src/ lib/ cli/ shared/ memfn/) build here; a test-file plant
# prints its SAB_FILE and exits 3: apply it to a COPY of that test file.
# Run a planted compiler with PCREC=OUTDIR/tree/build/pcrec in front of the
# harness or a differential; compare against the clean build/pcrec.
set -euo pipefail
[ $# -ge 2 ] || { sed -n '2,23p' "$0" >&2; exit 2; }
ROW=$1 OUT=$2 REV=${3:-HEAD}
TREE=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
case "$OUT" in /tmp|/tmp/*) echo "plant.sh: /tmp is not used; put OUTDIR under the temp root" >&2; exit 2;; esac
if [ -f "$ROW" ]; then f=$ROW; else f=$(ls "$TREE"/tests/mech/sabotages/"${ROW}"_*.sh 2>/dev/null | head -1); fi
[ -n "$f" ] || { echo "plant.sh: no row $ROW" >&2; exit 2; }
[ -d "$TREE/build/obj" ] || { echo "plant.sh: $TREE/build/obj missing (run make at $REV first)" >&2; exit 2; }
SAB_FILE= SAB_FILE2= SAB_COUNT=1 SAB_COUNT2=1 SAB_BEFORE2= SAB_AFTER2=
# shellcheck disable=SC1090
. "$f"
T=$OUT/tree
rm -rf "$T"; mkdir -p "$T/build"
git -C "$TREE" archive "$REV" src lib cli shared memfn | tar -x -C "$T"
cp -r "$TREE/build/obj" "$T/build/"
apply() { # file before after count
    printf '%s' "$2" > "$OUT/.b"; printf '%s' "$3" > "$OUT/.a"
    python3 -I "$TREE/tests/mech/lib/replace.py" "$T/$1" "$OUT/.b" "$OUT/.a" "$4"; }
rebuilt=()
for pair in 1 2; do
    if [ $pair = 1 ]; then F=$SAB_FILE B=$SAB_BEFORE A=$SAB_AFTER C=${SAB_COUNT:-1}
    else F=$SAB_FILE2 B=$SAB_BEFORE2 A=$SAB_AFTER2 C=${SAB_COUNT2:-1}; fi
    [ -n "$F" ] || continue
    case "$F" in src/*|lib/*|cli/*|shared/*|memfn/*) ;;
        *) echo "TEST-FILE PLANT: $F (not a compiler plant)"; exit 3;; esac
    apply "$F" "$B" "$A" "$C"
    rebuilt+=("$F")
done
(
    cd "$T"
    for F in "${rebuilt[@]}"; do
        case "$F" in
            src/*.c) o=build/obj/${F#src/}; o=${o%.c}.o
                nice gcc -O2 -g -Wall -Wextra -std=gnu11 -Ilib -Isrc -c -o "$o" "$F";;
            *)  echo "note: $F is not a src/*.c file; rebuilding every src object"
                for c in $(find src -name '*.c'); do o=build/obj/${c#src/}; o=${o%.c}.o
                    [ -f "$o" ] && nice gcc -O2 -g -std=gnu11 -Ilib -Isrc -c -o "$o" "$c"; done;;
        esac
    done
    ar rcs build/libpcrec.a $(find build/obj -name '*.o' | sort)
    nice gcc -O2 -g -std=gnu11 -Ilib -Isrc -o build/pcrec cli/main.c build/libpcrec.a
)
echo "PLANTED $(basename "$f") -> $T/build/pcrec"
