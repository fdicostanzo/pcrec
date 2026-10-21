#!/usr/bin/env bash
# tests/codegen/run_residual_twins.sh -- [FINDALL-NEXT] I1, IC1: the RESIDUAL
# TWINS (findall_iter.md §2.4). Every exported residual entry
# (`<prefix>_next_pos`, `_valid_upto`, `_var_valid`, ...) is a one-line
# forwarder to a static twin `<prefix>__<name>`, and every call inside the
# artifact goes to the twin, so a -fPIC build (a shared library) reaches its
# own residuals directly rather than through the PLT, where they are
# interposable and cost a call through a stub.
#
# THE CHECK READS THE OBJECT, not the text: each artifact is compiled -O2
# -fPIC -c and its relocations listed (objdump -dr). A residual is a symbol
# the object exports that has a static twin (nm: a global T `<p>_X` and a
# local t `<p>__X`); a PLT32 relocation against one is a call that missed its
# twin. Two controls: a PLANT (one twin call in the text respelled to the
# exported name) must turn the same reading red, and a POPULATION floor of
# (artifact, residual) pairs whose twin is called keeps it from going green
# on artifacts that call none.
# env: PCREC, CC, MIN_PAIRS (default 8)
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
MIN_PAIRS="${MIN_PAIRS:-8}"
W="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-twins.XXXXXX")"
trap 'rm -rf "$W"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# PATTERN<TAB>FLAGS: the iterator (next_pos), the subject check (valid_upto),
# variables (var_valid), both engines, and a compound shell
CASES='x*|y
(a)|b*	--engine=vm
x*|.	-e utf8 -futf-check
(a|b)*c	-e utf8 -futf-check --engine=vm
a${v}|b
^\s*|\s*$
.	-e utf8 -fstartpos-guard=align'

# misses OBJ: the PLT32 relocations against residuals that have a twin
misses() {
    local o="$1" res
    res="$(nm "$o" | awk '$2 == "T" { g[$3] = 1 } $2 == "t" { t[$3] = 1 }
                       END { for (s in g) { n = s; sub(/_/, "__", n); if (n in t) printf "%s ", s } }')"
    [ -n "$res" ] || return 0
    objdump -dr "$o" | awk -v list="$res" '
        BEGIN { n = split(list, a, " "); for (i = 1; i <= n; i++) r[a[i]] = 1 }
        /R_X86_64_PLT32|R_X86_64_PC32/ { s = $3; sub(/[-+].*$/, "", s); if (s in r) print s }'
}

npairs=0; i=0
while IFS=$'\t' read -r pat flags; do
    i=$((i + 1)); d="$W/c$i"; mkdir -p "$d"
    # shellcheck disable=SC2086
    if ! pcrec_run "$PCREC" --features all -p rx $flags -o "$d/rx.c" --pattern "$pat" 2> "$d/err"; then
        bad "[twins] '$pat' $flags does not compile: $(head -1 "$d/err")"; continue
    fi
    if ! gen_cc "twins:$pat" "$CC" -O2 -fPIC -std=gnu11 -c "$d/rx.c" -o "$d/rx.o" 2> "$d/cc.err"; then
        bad "[twins] '$pat' $flags: -fPIC build failed: $(head -2 "$d/cc.err" | tr '\n' ' ')"; continue
    fi
    m="$(misses "$d/rx.o")"
    if [ -n "$m" ]; then bad "[twins] '$pat' $flags calls its exported residual(s) through the PLT: $(echo $m)"
    else ok "[twins] '$pat' $flags: every residual call is a direct call to its twin"; fi
    # the population: twins this artifact's text calls
    for tw in $(grep -o 'rx__[a-z_]*(' "$d/rx.c" | sort -u | tr -d '('); do
        nm "$d/rx.o" | grep -q " T ${tw/rx__/rx_}\$" && npairs=$((npairs + 1))
    done
done <<< "$CASES"

# the plant: respell the first twin call of a twin-calling artifact
p="$W/c3"; cp "$p/rx.c" "$p/plant.c"   # beside its rx.h
tw="$(grep -o 'rx__valid_upto(subject' "$p/plant.c" | head -1)"
if [ -z "$tw" ]; then
    bad "[twins-plant] the plant site (a call of rx__valid_upto) is absent: the control measures nothing"
else
    # the first occurrence only, portably (no GNU `sed 0,/re/`)
    awk '!d && sub(/rx__valid_upto\(subject/, "rx_valid_upto(subject") { d = 1 } 1' \
        "$p/plant.c" > "$p/plant.tmp" && mv "$p/plant.tmp" "$p/plant.c"
    if gen_cc "twins:plant" "$CC" -O2 -fPIC -std=gnu11 -c "$p/plant.c" -o "$p/plant.o" 2> "$p/plant.err" &&
       [ -n "$(misses "$p/plant.o")" ]; then
        ok "[twins-plant] a call respelled to the exported name is read as a PLT call"
    else
        bad "[twins-plant] the planted PLT call was not seen: the reading is blind"
    fi
fi
[ "$npairs" -ge "$MIN_PAIRS" ] && ok "[twins-population] $npairs (artifact, residual) pairs call their twin (floor $MIN_PAIRS)" \
    || bad "[twins-population] $npairs (artifact, residual) pairs call their twin, floor $MIN_PAIRS"
echo "residual twins: $pass passed, $fail failed"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
