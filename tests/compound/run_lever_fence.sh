#!/usr/bin/env bash
# tests/compound/run_lever_fence.sh -- [COMPOUND] G7, THE HARNESS LEVER'S
# FENCE (docs/design/compound.md §A.11, §E.3 G7; sabotage row CMP-17).
#
# The lever (`--harness=no-compound`, build/pcrec-harness only) force-declines
# the compound family. Hidden visibility does not fence the shipped static
# archive, so these three checks are the fence:
#   (a) `nm -g --defined-only build/libpcrec.a` lists EXACTLY ONE global
#       beginning with the reserved prefix (`pcrec_harness_`): the lever's
#       entry, and nothing else under it;
#   (b) no header under lib/ declares a name beginning with it;
#   (c) neither the option spelling (`--harness=`) nor the prefix appears in
#       docs/spec/, docs/guide/, README.md, examples/, lib/, tests/, scripts/
#       or cli/, outside the allowlist of the harness's own uses below.
# Each check runs on the shipped inputs AND on a planted input that must
# FAIL it: a second global under the prefix, a lib/ declaration of it, and the
# lever's object removed (zero globals -- the lever demonstrably exists).
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LIB="$ROOT/build/libpcrec.a"
CC="${CC:-gcc}"
W="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-fence.XXXXXX")"
trap 'rm -rf "$W"' EXIT
PFX=pcrec_harness_
fails=0
pass() { echo "ok   $*"; }
fail() { echo "FAIL $*"; fails=$((fails + 1)); }

# (a) the globals of ARCHIVE under the prefix, one per line.
globals() { nm -g --defined-only "$1" 2>/dev/null | awk -v p="$PFX" '$2 ~ /^[A-Z]$/ && index($3, p) == 1 { print $3 }' | LC_ALL=C sort -u; }
# (b) the declarations of the prefix in the headers under DIR.
decls() { grep -rn "$PFX" "$1" --include='*.h' 2>/dev/null; }
# (c) the mentions under ROOT outside the allowlist: path:line text. The
# allowlist: the harness's own build and CLI arm, this directory, the axes
# arm, emit_sweep's harness pairing, the two sabotage rows that plant the
# fence's own faults (S907, S909), and the memfn kit's arm-entry counter check
# (R-MS6, R17-b' B2: `--harness=arm-reach` and the counter's reserved name),
# and cli/CLAUDE.md's record of the harness build (its options listed since
# R17-b' B1: a red on lane/memfn-fd @ 285590dc6, found by lane fdb2).
ALLOW='^(cli/main\.c|cli/CLAUDE\.md|Makefile|tests/compound/|tests/axes/run_axes\.sh|scripts/emit_sweep\.py|tests/mech/sabotages/S90[79]_|tests/memfn/run_arm_reach\.sh)'
mentions() {
    (cd "$1" && grep -rnI -e '--harness=' -e "$PFX" docs/spec docs/guide README.md examples lib tests scripts cli 2>/dev/null) |
        grep -Ev "$ALLOW"
}

[ -f "$LIB" ] || { echo "FAIL: $LIB is missing (run make)"; exit 1; }

g="$(globals "$LIB")"
n="$(printf '%s' "$g" | grep -c . || true)"
[ "$n" -eq 1 ] && pass "(a) exactly one global under $PFX: $g" ||
    fail "(a) $n globals under $PFX in libpcrec.a: $(echo $g)"
d="$(decls "$ROOT/lib")"
[ -z "$d" ] && pass "(b) no lib/ header declares $PFX" || fail "(b) lib/ declares it: $d"
m="$(mentions "$ROOT")"
[ -z "$m" ] && pass "(c) no mention of the lever outside its allowlist" ||
    fail "(c) the lever is mentioned outside its allowlist: $(echo "$m" | head -5)"

# controls: each planted input must fail its check
cp "$LIB" "$W/two.a"
printf 'int %sextra(void) { return 0; }\n' "$PFX" > "$W/extra.c"
"$CC" -c -o "$W/extra.o" "$W/extra.c" && ar rs "$W/two.a" "$W/extra.o" 2>/dev/null
[ "$(globals "$W/two.a" | grep -c .)" -eq 2 ] && pass "(a) control: a planted second global is seen" ||
    fail "(a) control: a planted second global under $PFX was not seen"
cp "$LIB" "$W/none.a"
member="$(ar t "$LIB" | while read -r o; do ar p "$LIB" "$o" > "$W/m.o"; nm -g --defined-only "$W/m.o" | grep -q " $PFX" && echo "$o"; done | head -1)"
if [ -n "$member" ]; then
    ar d "$W/none.a" "$member"
    [ "$(globals "$W/none.a" | grep -c . || true)" -eq 0 ] && pass "(a) control: the lever removed reads 0 globals (member $member)" ||
        fail "(a) control: the lever's member removed and a global remains"
else
    fail "(a) control: no archive member defines the lever"
fi
mkdir -p "$W/lib" && cp "$ROOT"/lib/*.h "$W/lib/" && printf 'int %scompile(void);\n' "$PFX" >> "$W/lib/pcrec.h"
[ -n "$(decls "$W/lib")" ] && pass "(b) control: a planted lib/ declaration is seen" ||
    fail "(b) control: a planted lib/ declaration was not seen"
mkdir -p "$W/tree/docs/spec" && printf 'run pcrec --harness=no-compound\n' > "$W/tree/docs/spec/x.md"
[ -n "$(mentions "$W/tree")" ] && pass "(c) control: a planted spec mention is seen" ||
    fail "(c) control: a planted spec mention was not seen"

[ "$fails" -eq 0 ] && echo "PASS: G7 lever fence (3 checks, 4 controls)" || echo "FAIL: G7 lever fence: $fails failures"
[ "$fails" -eq 0 ]
