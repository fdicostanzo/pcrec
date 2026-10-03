#!/usr/bin/env bash
# tests/codegen/run_prefix_invariance.sh — K79: no SELECTION reads the prefix.
#
# The compiler emits every artifact under a fixed two-byte placeholder prefix
# and writes the caller's `-p` spelling onto the finished text
# (`pcrec_sb_render_prefix`, src/core/sb.c; the contract is
# docs/spec/limits.md "Size limits and the prefix"). Every size-predicated
# selection — the VM entry shape, the size term's trigger and ladder, the
# emitted-size caps — therefore sees the text at one canonical prefix length,
# and the same pattern gets the same artifact under every prefix, spelled
# differently. Before abi 54 it did not: `(foo|bar)[0-9]{2,5}(x)` took entry
# shape `inline` at `-p rx` and `plain` under a 60-character prefix (K79).
#
# WHAT THIS DEEMS SELECTION: EVERYTHING. The check does not pick stamps. Each
# artifact at a long prefix, with its prefix spellings mapped back to
# `rx`/`RX`, must equal the `-p rx` artifact BYTE FOR BYTE (.c and .h). So
# every stamp, form, table and label is compared, and the only bytes allowed
# to differ are the prefix's own spelling. No stamp is exempt: the one stamp
# that counts emitted bytes, `<PREFIX>_VM_PROGRAM_BYTES`, counts them at the
# canonical length since abi 54 and is compared like the rest.
#
#   PART 1  full-text identity over the population below at three long
#           prefixes (3, 23 and 60 characters — 60 is PCREC_MAX_PREFIX_LEN),
#           spelled from letters no emitted text uses in that order, so the
#           back-mapping is exact (see "the back-map" below). A refusal's
#           diagnostic is compared the same way.
#   PART 2  a ONE-character prefix, whose spelling cannot be back-mapped
#           (`q` is in every comment), compared on its VALUE STAMPS: every
#           `#define <P>_<NAME> <value>` line, prefix stripped at its known
#           position, must equal the `-p rx` list.
#   PART 3  the reach: the witnesses below are the ones that FLIPPED entry
#           shape on the pre-fix compiler (measured on lane k7980 against
#           the branch point, docs/dev/lanes/k7980_report.md), each asserted
#           to take the same shape at every prefix; plus a population floor.
#
# THE BACK-MAP. The long prefixes are built from `kpz` + digits (upper
# `KPZ` + digits). `kpz` occurs in no fixed emitted text, a pattern would
# have to spell it, and the population below drops any that does; so
# replacing every occurrence is exact, not a heuristic. If it ever
# stopped being exact the failure is loud (a spurious diff), never silent.
#
# FAILING DIRECTION: sabotage S437 feeds the emitters the caller's prefix
# instead of the placeholder — the pre-fix behaviour — and PART 3's
# witnesses go red (so does PART 1 on every artifact whose program length
# is prefix-dependent).
#
# Output: PASS:/FAIL: lines and the `checks passed:`/`checks failed:` trailer.
# Usage: bash tests/codegen/run_prefix_invariance.sh

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"

pass=0; fail=0
ok()  { echo "PASS: $*"; pass=$((pass+1)); }
bad() { echo "FAIL: $*" >&2; fail=$((fail+1)); }

TMP="$(mktemp -d "${TMPDIR:-/tmp}/pfxinv.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

# The PART 3 witnesses: each flipped VM_ENTRY_SHAPE between `-p rx` and a
# 60-character prefix on the pre-fix compiler (inline -> plain, or
# forward -> shared), on the route named.
WITNESSES=(
    'auto|(foo|bar)[0-9]{2,5}(x)'
    'auto|(cat|DOG)s?'
    'auto|(x?)(y?)(z?)'
    'auto|^(a)(b)\g-1$'
    'auto|x(?!a)(?!b)(?!c)(?!d)(?!e)(?!f)(?!g)(?!h)(?!i)(?!j)(?!k)(?!l)(?!m)(?!n)(?!o)(?!p)(?!q)'
    'vm|cat|car|cap|dog'
)

# PART 1's population: the witnesses plus a deterministic slice of the
# corpus's distinct `pattern` lines (every STRIDE-th, sorted), on the default
# route and on the forced VM — the VM is where the entry shape lives.
STRIDE="${PFXINV_STRIDE:-40}"
POP="$TMP/pop.txt"
for w in "${WITNESSES[@]}"; do printf '%s\n' "$w"; done > "$POP"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' 2>/dev/null \
    | sed 's/^pattern //' | LC_ALL=C sort -u \
    | awk -v s="$STRIDE" 'NR % s == 0' \
    | grep -vi 'kpz' \
    | while IFS= read -r p; do printf 'auto|%s\nvm|%s\n' "$p" "$p"; done >> "$POP"
npop="$(wc -l < "$POP" | tr -d ' ')"

PX3='kpz'
PX23='kpz90123456789012345678'
PX60='kpz901234567890123456789012345678901234567890123456789012345'
up() { printf '%s' "$1" | tr '[:lower:]' '[:upper:]'; }

# compile ROUTE PATTERN PREFIX DIR -> DIR/a.c, DIR/a.h (same basename at
# every prefix, so the header's #include line is identical); rc in $?.
compile() {
    local route="$1" pat="$2" px="$3" dir="$4" eng=()
    [ "$route" = vm ] && eng=(--engine=vm)
    rm -rf "$dir"; mkdir -p "$dir"
    "$TIMEOUT_BIN" 60 "$PCREC" --features all "${eng[@]}" -p "$px" \
        -o "$dir/a.c" --pattern "$pat" > "$dir/err" 2>&1
}
backmap() {  # FILE PREFIX -> stdout, the prefix spellings mapped to rx/RX
    local u; u="$(up "$2")"
    sed -e "s/$2/rx/g" -e "s/$u/RX/g" "$1"
}
stamps() {  # FILE UPPER-PREFIX -> the value-stamp list, prefix stripped
    sed -n "s/^#define $2_\([A-Za-z0-9_]*\) \(.*\)\$/\1 \2/p" "$1"
}
shape() { sed -n "s/^#define $2_VM_ENTRY_SHAPE \(.*\)\$/\1/p" "$1"; }

echo "== PART 1: full-text identity at three long prefixes ($npop compiles each) =="
p1_same=0; p1_diff=0; p1_refused=0; p1_first=""
p2_same=0; p2_diff=0; p2_first=""
i=0
while IFS= read -r line; do
    i=$((i+1))
    route="${line%%|*}"; pat="${line#*|}"
    compile "$route" "$pat" rx "$TMP/rx"; rc_rx=$?
    # PART 2 rides the same loop: the one-character prefix's value stamps.
    compile "$route" "$pat" q "$TMP/q"; rc_q=$?
    if [ "$rc_rx" -ne "$rc_q" ]; then
        p2_diff=$((p2_diff+1)); [ -n "$p2_first" ] || p2_first="$line (rc $rc_rx vs $rc_q)"
    elif [ "$rc_rx" -eq 0 ]; then
        if [ "$(stamps "$TMP/rx/a.c" RX)" = "$(stamps "$TMP/q/a.c" Q)" ]; then
            p2_same=$((p2_same+1))
        else
            p2_diff=$((p2_diff+1)); [ -n "$p2_first" ] || p2_first="$line"
        fi
    fi
    for px in "$PX3" "$PX23" "$PX60"; do
        compile "$route" "$pat" "$px" "$TMP/px"; rc=$?
        if [ "$rc" -ne "$rc_rx" ]; then
            p1_diff=$((p1_diff+1)); [ -n "$p1_first" ] || p1_first="$line at -p $px (rc $rc_rx vs $rc)"
            continue
        fi
        if [ "$rc" -ne 0 ]; then
            # a refusal: the diagnostic must not depend on the prefix either
            if [ "$(backmap "$TMP/px/err" "$px")" = "$(cat "$TMP/rx/err")" ]; then
                p1_refused=$((p1_refused+1))
            else
                p1_diff=$((p1_diff+1)); [ -n "$p1_first" ] || p1_first="$line at -p $px (diagnostic)"
            fi
            continue
        fi
        if [ "$(backmap "$TMP/px/a.c" "$px")" = "$(cat "$TMP/rx/a.c")" ] \
           && [ "$(backmap "$TMP/px/a.h" "$px")" = "$(cat "$TMP/rx/a.h")" ]; then
            p1_same=$((p1_same+1))
        else
            p1_diff=$((p1_diff+1)); [ -n "$p1_first" ] || p1_first="$line at -p $px"
        fi
    done
done < "$POP"

if [ "$p1_diff" -eq 0 ] && [ "$p1_same" -gt 0 ]; then
    ok "PART 1: $p1_same artifacts at -p kpz/23/60 chars are byte-identical to -p rx up to the prefix's spelling ($p1_refused refusals identical too)"
else
    bad "PART 1: $p1_diff of $((p1_same + p1_diff + p1_refused)) long-prefix compiles differ from -p rx beyond the prefix's spelling; first: $p1_first"
fi
if [ "$p2_diff" -eq 0 ] && [ "$p2_same" -gt 0 ]; then
    ok "PART 2: $p2_same artifacts at -p q carry the -p rx value-stamp list exactly"
else
    bad "PART 2: $p2_diff artifacts at -p q carry a different value-stamp list from -p rx; first: $p2_first"
fi

echo "== PART 3: the reach =="
# POPULATION FLOOR (K35): a slice that silently emptied would pass PART 1.
# Counted over compiles that were COMPARED (identical or not), so a red
# PART 1 does not also read as a shrunken population.
p1_cmp=$((p1_same + p1_diff))
if [ "$npop" -ge 100 ] && [ "$p1_cmp" -ge 250 ]; then
    ok "PART 3: population $npop route x pattern pairs, $p1_cmp long-prefix compiles compared (floors 100 / 250)"
else
    bad "PART 3: population $npop pairs / $p1_cmp compared compiles is under its floor (100 / 250) — the corpus slice shrank or most of it stopped compiling"
fi
for w in "${WITNESSES[@]}"; do
    route="${w%%|*}"; pat="${w#*|}"
    compile "$route" "$pat" rx "$TMP/w"; want="$(shape "$TMP/w/a.c" RX)"
    if [ -z "$want" ]; then
        bad "PART 3: witness [$route] $pat no longer reaches the VM entry-shape decision (no RX_VM_ENTRY_SHAPE) — re-derive the witness list"
        continue
    fi
    got=""
    for px in q "$PX3" "$PX23" "$PX60"; do
        compile "$route" "$pat" "$px" "$TMP/w"
        s="$(shape "$TMP/w/a.c" "$(up "$px")")"
        [ "$s" = "$want" ] || got="$got -p ${#px}ch:$s"
    done
    if [ -z "$got" ]; then
        ok "PART 3: witness [$route] $pat takes entry shape $want at every prefix length (1..60)"
    else
        bad "PART 3: witness [$route] $pat takes $want at -p rx but$got — a selection reads the prefix (K79)"
    fi
done

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
