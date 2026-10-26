#!/usr/bin/env bash
# tests/core/kindrow_check.sh ROOT [WORKDIR] — [INLINE-C] stage 1a THE
# PER-KIND ATTRIBUTE ROW IS COMPLETE (src/core/kindrow.def;
# docs/design/inline_c.md §1.8): every `AKind` has exactly one row, in enum
# order, and a kind without a row FAILS TO COMPILE.
#
# The promise is a COMPILER property (internal.h builds `pcrec_kind_row`'s
# switch from the table with -Wswitch raised to an error, and asserts each
# row's position), so the check is a compile, run against plants:
#   (1) the census, read as TEXT, independent of the compiler's view: the
#       AKind enumerators in internal.h and the KIND_ROW rows in kindrow.def
#       are the same names in the same order, at least 16 of them (K35);
#   (2) control: a translation unit including core/internal.h and calling
#       `pcrec_kind_row` compiles clean on the live tree;
#   (3) a NEW KIND appended to AKind with no row: the compile fails, naming
#       the kind in the -Werror=switch diagnostic;
#   (4) a ROW DELETED from kindrow.def: the compile fails;
#   (5) two rows SWAPPED: the compile fails on the position assertion;
#   (6) a row DUPLICATED: the compile fails.
# Every plant must fail AND its control (2) must pass; a plant that compiles
# is the finding. One gcc -fsyntax-only per arm, on a copy of src/ and lib/.
set -u
export LC_ALL=C
ROOT="$1"
W="${2:-$(mktemp -d)}"
CC="${CC:-gcc}"
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1"; fail=$((fail + 1)); }

HDR="$ROOT/src/core/internal.h"
DEF="$ROOT/src/core/kindrow.def"

# (1) the census, as text: the enumerators between `typedef enum {` and
# `} AKind;`, and the rows in file order.
enum_names="$(awk '/^typedef enum \{/ { buf = ""; inside = 1; next }
                   inside && /^\} AKind;/ { print buf; exit }
                   inside && /^\} [A-Za-z_]+;/ { inside = 0; next }
                   inside && /^    A_[A-Z]+,?[[:space:]]*($|\/\*)/ {
                       n = $1; sub(/,$/, "", n); buf = buf n "\n" }' "$HDR" |
              grep -v '^$')"
row_names="$(sed -n 's/^KIND_ROW(\(A_[A-Z]*\),.*/\1/p' "$DEF")"
nenum="$(printf '%s\n' "$enum_names" | grep -c '^A_')"
nrow="$(printf '%s\n' "$row_names" | grep -c '^A_')"
if [ "$nenum" -lt 16 ] || [ "$nrow" -lt 16 ]; then
    bad "kindrow census: read $nenum AKind enumerators and $nrow rows, fewer than 16 — the scan has stopped matching (K35)"
elif [ "$enum_names" != "$row_names" ]; then
    bad "kindrow census: the rows are not the enumerators in enum order: $(diff <(printf '%s\n' "$enum_names") <(printf '%s\n' "$row_names") | tr '\n' ' ')"
else
    ok "kindrow census: $nenum AKind enumerators, $nrow rows, same names in the same order"
fi

# A pristine copy of the two include roots, restored before each plant.
mkdir -p "$W/pristine" "$W/tree"
cp -R "$ROOT/src" "$ROOT/lib" "$W/pristine/"
reset_tree() { rm -rf "$W/tree"; cp -R "$W/pristine" "$W/tree"; }
cat > "$W/probe.c" <<'EOF'
#include "core/internal.h"
int kindrow_probe(void) { return (int)pcrec_kind_row(A_CLASS).text; }
EOF
# Compiles the probe against include root $1; output to $2; returns gcc's rc.
compile_probe() {
    "$CC" -std=gnu11 -I"$1/lib" -I"$1/src" -fsyntax-only "$W/probe.c" > "$2" 2>&1
}

# (2) control on the live tree.
if compile_probe "$ROOT" "$W/control.log"; then
    ok "kindrow control: a TU calling pcrec_kind_row compiles clean on the live tree"
else
    bad "kindrow control: the live tree does not compile the probe: $(head -3 "$W/control.log" | tr '\n' ' ')"
fi

# plant NAME DESC EXPECT-ERE PYTHON-EDIT — applies the edit to the copy, then
# demands a failed compile whose diagnostics match EXPECT-ERE.
plant() {
    local name="$1" desc="$2" expect="$3" edit="$4"
    reset_tree
    if ! python3 -I -c "$edit" "$W/tree/src/core/internal.h" "$W/tree/src/core/kindrow.def"; then
        bad "kindrow plant ($name): the plant did not apply — re-derive it from the live files"
        return
    fi
    if compile_probe "$W/tree" "$W/$name.log"; then
        bad "kindrow plant ($name): $desc COMPILED — the table's completeness is no longer enforced"
    elif grep -qE "$expect" "$W/$name.log"; then
        ok "kindrow plant ($name): $desc fails to compile ($(grep -m1 -oE "$expect" "$W/$name.log"))"
    else
        bad "kindrow plant ($name): $desc failed for another reason: $(grep -m1 'error' "$W/$name.log")"
    fi
}

# (3) a kind with no row, appended after the last enumerator.
plant newkind "a new AKind with no row" \
    "enumeration value .A_KINDROW_PROBE. not handled in switch" '
import sys
p = sys.argv[1]; s = open(p).read()
i = s.index("} AKind;")
j = s.rindex("\n", 0, i)
assert s[j - len("A_WCLASS"):j] == "A_WCLASS", "the last enumerator moved"
s = s[:j] + ",\n    A_KINDROW_PROBE" + s[j:]
open(p, "w").write(s)'

# (4) a row deleted (the variable's).
plant delrow "kindrow.def with the A_VAR row deleted" \
    "enumeration value .A_VAR. not handled in switch|KIND_ROW_AT_A_VAR" '
import sys, re
p = sys.argv[2]; s = open(p).read()
s2 = re.sub(r"^KIND_ROW\(A_VAR,.*\n", "", s, count=1, flags=re.M)
assert s2 != s
open(p, "w").write(s2)'

# (5) two rows swapped (the empty string and the end-of-line anchor).
plant swaprows "kindrow.def with the A_EMPTY and A_EOL rows swapped" \
    "is not at its AKind position" '
import sys, re
p = sys.argv[2]; s = open(p).read()
a = re.search(r"^KIND_ROW\(A_EMPTY,.*$", s, re.M).group(0)
b = re.search(r"^KIND_ROW\(A_EOL,.*$", s, re.M).group(0)
s = s.replace(a, "@@A@@").replace(b, a).replace("@@A@@", b)
open(p, "w").write(s)'

# (6) a row duplicated (the lookaround'"'"'s).
plant duprow "kindrow.def with the A_LOOK row duplicated" \
    "duplicate case value|redeclaration of enumerator" '
import sys, re
p = sys.argv[2]; s = open(p).read()
m = re.search(r"^KIND_ROW\(A_LOOK,.*\n", s, re.M)
s = s[:m.end()] + m.group(0) + s[m.end():]
open(p, "w").write(s)'

echo "kindrow checks passed: $pass"
echo "kindrow checks failed: $fail"
[ "$fail" -eq 0 ]
