#!/usr/bin/env bash
# compare.sh BEFORE NEW: every plant of the 4 runners applied by the OLD per-runner
# heredoc (BEFORE tree's runner text, extracted to old_*.py) and by NEW's
# tests/lib/plants.py, each to a fresh copy; the two resulting trees and exit codes compared.
set -u
B=$1; N=$2; E=$(cd "$(dirname "$0")" && pwd); T=$E/t; M=$N/tests/lib/plants.py
fn() { awk '/^plant_spec\(\) \{/{f=1} f{print} f&&/^}$/{exit}' "$1"; }
same=0; diff=0
cmpdirs() {  # tag id rcold rcnew
    if [ "$3" = "$4" ] && diff -r "$T/a" "$T/b" >/dev/null; then same=$((same + 1)); echo "SAME $1 $2 rc=$3"
    else diff=$((diff + 1)); echo "DIFF $1 $2 rc old=$3 new=$4"; fi
}
for r in win:memfn/tests/run_g2_win.sh proof:tests/memfn/run_proof.sh; do
    tag=${r%%:*}; f=$B/${r#*:}
    eval "$(fn "$f")"
    for id in $(sed -n 's/^PLANTS="\(.*\)"$/\1/p' "$f"); do
        spec="$(plant_spec "$id")"
        file="${spec%%@@*}"; rest="${spec#*@@}"; from="${rest%%@@*}"; to="${rest#*@@}"
        rm -rf "$T"; mkdir -p "$T"; cp -r "$B/memfn/src" "$T/a"; cp -r "$B/memfn/src" "$T/b"
        python3 -I "$E/old_$tag.py" "$T/a/$file" "$from" "$to" 2>/dev/null; o=$?
        python3 -I "$M" apply win "$T/b" -- "$spec" 2>/dev/null; n=$?
        cmpdirs $tag $id $o $n
    done
done
f=$B/memfn/tests/run_g2_pres.sh; eval "$(fn "$f")"
for id in $(sed -n 's/^PLANTS="\(.*\)"$/\1/p' "$f"); do
    specs="$(plant_spec "$id")"
    rm -rf "$T"; mkdir -p "$T"; cp -r "$B/memfn/src" "$T/a"; cp -r "$B/memfn/src" "$T/b"
    mkdir -p "$T/a/c0" "$T/b/c0"; cp "$B/docs/design/memfn/span_pick/census0.py" "$T/a/c0/"; cp "$B/docs/design/memfn/span_pick/census0.py" "$T/b/c0/"
    o=0
    while IFS= read -r spec; do
        file="${spec%%@@*}"; rest="${spec#*@@}"; from="${rest%%@@*}"; to="${rest#*@@}"
        case "$file" in @c0/*) path="$T/a/c0/${file#@c0/}" ;; *) path="$T/a/$file" ;; esac
        python3 -I "$E/old_pres.py" "$path" "$from" "$to" 2>/dev/null || { o=1; break; }
    done <<< "$specs"
    ed=(); while IFS= read -r l; do ed+=("$l"); done <<< "$specs"
    python3 -I "$M" apply pres "$T/b" "$T/b/c0" -- "${ed[@]}" 2>/dev/null; n=$?
    cmpdirs pres $id $o $n
done
f=$B/tests/memfn/run_wreply.sh; eval "$(fn "$f")"
eval "$(awk '/^PERTS=\(/{f=1} f{print} f&&/^\)$/{exit}' "$f")"
for id in $(sed -n 's/^PLANTS="\(.*\)"$/\1/p' "$f"); do
    spec="$(plant_spec "$id")"
    if [ "$id" = S1414 ]; then seq=("$spec"); else seq=("${PERTS[@]}" "$spec"); fi
    rm -rf "$T"; mkdir -p "$T/a" "$T/b"; cp -r "$B/src" "$T/a/src"; cp -r "$B/src" "$T/b/src"
    o=0; for s in "${seq[@]}"; do python3 -I "$E/old_wreply.py" "$T/a" "$s" 2>/dev/null || { o=1; break; }; done
    python3 -I "$M" apply wreply "$T/b" -- "${seq[@]}" 2>/dev/null; n=$?
    cmpdirs wreply $id $o $n
done
# PERTS alone (the wreply main path's perturbed copy)
rm -rf "$T"; mkdir -p "$T/a" "$T/b"; cp -r "$B/src" "$T/a/src"; cp -r "$B/src" "$T/b/src"
o=0; for s in "${PERTS[@]}"; do python3 -I "$E/old_wreply.py" "$T/a" "$s" 2>/dev/null || { o=1; break; }; done
python3 -I "$M" apply wreply "$T/b" -- "${PERTS[@]}" 2>/dev/null; n=$?
cmpdirs wreply PERTS $o $n
rm -rf "$T"
echo "compare: same=$same diff=$diff"
[ "$diff" -eq 0 ]
