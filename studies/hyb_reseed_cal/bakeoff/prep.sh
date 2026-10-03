#!/bin/bash
# prep.sh NEW_PCREC BASE_PCREC BENCH_DIR OUT — builds the A2 bake-off PACK
# (Mac side; writes OUT/ and OUT.tgz, nothing else).
#
#   NEW_PCREC   the lane's compiler (its adaptive artifacts are the forms'
#               source, its -fno-hyb-reseed artifacts the deny)
#   BASE_PCREC  main's compiler at the branch point: only the A1 cell's `a`
#   BENCH_DIR   a pcrec-bench checkout, READ ONLY (subjects are regenerated
#               from its generators and sha256-verified against its
#               manifests; nothing is written into it)
#
# The pack is self-contained: the artifacts (`src/`), the subjects, sdrv.c,
# cells.tsv, bakeoff.sh and a MANIFEST naming both compilers' commits and
# every subject's sha256. bakeoff.sh needs only a C compiler pair and python3.
#
# The pack carries COPIES of the kit's scripts, so a pack built from an
# uncommitted kit runs code no commit holds: round 1's pack shipped a
# bakeoff.sh one line older than the committed one, and that line killed the
# run half-way (lane a2build). prep.sh therefore refuses a kit with
# uncommitted changes (ALLOW_DIRTY=1 overrides, and the MANIFEST says so) and
# records each copied script's sha256.
set -euo pipefail
NEW=$1 BASE=$2 BENCH=$3 OUT=$4
HERE=$(cd "$(dirname "$0")" && pwd)
KITDIRTY=$(git -C "$HERE" status --porcelain -- . ../shape | head -1)
if [ -n "$KITDIRTY" ] && [ "${ALLOW_DIRTY:-0}" != 1 ]; then
    echo "prep: the kit has uncommitted changes ($KITDIRTY ...); commit them or set ALLOW_DIRTY=1" >&2; exit 1
fi
export PYTHONDONTWRITEBYTECODE=1
rm -rf "$OUT"; mkdir -p "$OUT/src" "$OUT/cal"
python3 "$HERE/../shape/regen_bench_subjects.py" "$BENCH/bench/syntax" "$OUT"
python3 "$HERE/regen_cap_subjects.py" "$BENCH/bench/capability" "$OUT"
calgen=$(mktemp -d "$OUT/.calgen.XXXX")
(cd "$HERE/.." && python3 subjects.py "$calgen" >/dev/null)
for f in synth-dense synth-1m synth-64k-asc gap64 bursty; do mv "$calgen/$f.bin" "$OUT/cal/"; done
rm -rf "$calgen"
cp "$HERE/../shape/sdrv.c" "$HERE/cells.tsv" "$HERE/bakeoff.sh" "$HERE/table.py" "$OUT/"

stamp() { sed -n 's/^#define RX_VM_RESEED "\([a-z-]*\)"$/\1/p' "$1"; }
grep -v '^#' "$HERE/cells.tsv" | cut -f1-4 | sort -u | while IFS=$'\t' read -r id pat flags role; do
    fl=(); [ "$flags" != - ] && read -r -a fl <<<"$flags"
    if [ "$role" = a1 ]; then
        "$BASE" -p rx --features all ${fl[@]+"${fl[@]}"} -o "$OUT/src/$id.a.c" --pattern "$pat"
        "$NEW" -p rx --features all ${fl[@]+"${fl[@]}"} -o "$OUT/src/$id.d.c" --pattern "$pat"
        [ "$(stamp "$OUT/src/$id.a.c")" = adaptive-dense ] && [ "$(stamp "$OUT/src/$id.d.c")" = anchored ] \
            || { echo "prep: $id: expected base adaptive-dense / new anchored" >&2; exit 1; }
        continue
    fi
    "$NEW" -p rx --features all ${fl[@]+"${fl[@]}"} -o "$OUT/src/$id.a.c" --pattern "$pat"
    "$NEW" -p rx --features all ${fl[@]+"${fl[@]}"} -fno-hyb-reseed -o "$OUT/src/$id.d.c" --pattern "$pat"
    case "$(stamp "$OUT/src/$id.a.c")" in adaptive*) ;; *) echo "prep: $id: '$pat' is not adaptive" >&2; exit 1 ;; esac
    python3 "$HERE/mkforms.py" "$OUT/src/$id.a.c" "$OUT/src" "$id"
done

{
    echo "pack built $(date -u +%Y-%m-%dT%H:%MZ) on $(uname -sm)"
    echo "new  $("$NEW" --version 2>&1 | head -1)  tree $(git -C "$HERE" rev-parse --short HEAD)"
    echo "base $("$BASE" --version 2>&1 | head -1)"
    echo "kit  $([ -n "$KITDIRTY" ] && echo "DIRTY (ALLOW_DIRTY=1)" || echo clean) at $(git -C "$HERE" rev-parse --short HEAD)"
    (cd "$OUT" && shasum -a 256 bakeoff.sh table.py cells.tsv sdrv.c 2>/dev/null || sha256sum bakeoff.sh table.py cells.tsv sdrv.c)
    (cd "$OUT" && shasum -a 256 subj/* thr/* cal/* cap/* 2>/dev/null || sha256sum subj/* thr/* cal/* cap/*)
} > "$OUT/MANIFEST"
tar -C "$(dirname "$OUT")" -czf "$OUT.tgz" "$(basename "$OUT")"
echo "pack: $OUT.tgz ($(du -h "$OUT.tgz" | cut -f1))"
