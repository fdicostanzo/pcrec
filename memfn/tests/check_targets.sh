#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (unit K0, R-36); its shape
#   is rev 0's withdrawn scripts/check_targets.sh (commit 171bdb343).
#
# memfn/tests/check_targets.sh -- THE TARGET TABLE CHECK (unit K0, request
# R-36; docs/design/memfn/target_seam_units.md §2 and §5, target_seam.md §2).
# Run by `make` (the build/targets.check stamp: a failure WARNS, R5-Q1) and
# failed on by `make strict` and `make test-memfn-targets`.
#
# The subject is memfn/src/targets.def, read through the C preprocessor (the
# same X-macro rows the kit compiles). THE CONTROL IS THE COMPILER (the lane's
# adopted choice, units.md §5): for every target of the building host's
# family that has a region, `gcc <family floor> -m<each attribute>` must
# define exactly the macros `gcc -march=<name>` defines -- the whole `-dM`
# output, never a chosen ISA list (a list would be a name-keyed filter that
# cannot see a macro nobody listed: how `sahf` was found, R2). The floor is
# THIS check's own column, not the table's (x86-64: `-march=x86-64 -mno-sse`,
# so the baseline row's `sse2` is a real comparison, not the baseline
# against itself). gcc, whatever CC is (TARGETS_GCC overrides): clang's whole
# set differs by CPU-name macros alone (clang 21.1.8's -march=x86-64 defines
# `__k8`, its -march=x86-64-v3 does not), which a macro filter could only
# paper over. A target of another family is SKIPPED and counted.
#
# Structural rules (control: the rule, stated here): at least the literal
# floors of family and target rows; target and family names distinct under
# the parser's matching rule (case-blind, `_` as `-`), so no row shadows
# another; every target's family exists; exactly ONE familyless (portable)
# target, with no region and no features; features sorted, unrepeated; a
# region's attribute list equals the features; every family's default list
# non-empty, unrepeated, each member a target of that family.
#
# THE HOST CHAIN (targets.def's MF_TARGET_HOST block, the kit's own #if) is
# held to the guard column under several preprocessor targets (gcc as is,
# -m32, -mx32; clang --target=aarch64-linux-gnu where clang exists): in each,
# the chain names the family whose guard holds, or none where none does, and
# at most one guard holds. A cell that cannot run is SKIPPED and counted.
#
# Usage: check_targets.sh [OUT]
#   prints `targets-check: ...` lines (the last `ok: ...` or the mismatches),
#   writes the same to OUT when given; exit 0 = ok, 1 = mismatch, 2 = could
#   not run (no gcc, an unreadable table).

set -u
GCC="${TARGETS_GCC:-gcc}"
here="$(cd "$(dirname "$0")" && pwd)"
def="${TARGETS_DEF:-$here/../src/targets.def}"
out="${1:-}"
FLOOR_FAMILIES=2   # the design's two family rows (target_seam.md §2)
FLOOR_TARGETS=4    # generic, x86-64, x86-64-v3, aarch64 (units.md §2, K0)

msgs=()
bad=0
say() { msgs+=("targets-check: $*"); }
mismatch() { say "MISMATCH $*"; bad=1; }
finish() {
    printf '%s\n' "${msgs[@]}"
    [ -n "$out" ] && printf '%s\n' "${msgs[@]}" > "$out"
    exit "$1"
}

command -v "$GCC" >/dev/null 2>&1 || { say "no $GCC: the check could not run"; finish 2; }
[ -r "$def" ] || { say "cannot read $def"; finish 2; }

# The rows, one per line:  F id|name|guard|defaults   T id|name|family|attr|features
rows="$(printf '%s\n' \
    '#define MF_FAMILY(id, name, guard, defaults) F id|name|guard|defaults' \
    '#define MF_TARGET(id, name, family, region, features) T id|name|family|region|features' \
    '#define MF_FAMILY_OF(id) id' '#define MF_NO_FAMILY NONE' \
    '#define MF_REGION(attr) attr' '#define MF_NO_REGION ""' \
    "#include \"$def\"" | "$GCC" -E -P -x c - 2>/dev/null | grep -E '^[FT] ')" || {
    say "could not read $def through $GCC -E"; finish 2; }

# Strip one level of C string quoting and the surrounding blanks.
unq() { local s; s="$(printf '%s' "$1" | sed 's/^ *//; s/ *$//')"; s="${s#\"}"; s="${s%\"}"; printf '%s' "${s//\\\"/\"}"; }
# The parser's matching rule (memfn.h): case-blind, `_` read as `-`.
fold() { printf '%s' "$1" | tr 'A-Z_' 'a-z-'; }
sorted_list() { printf '%s' "$1" | tr ',' '\n' | LC_ALL=C sort | paste -sd, -; }
repeats() { printf '%s\n' "$1" | tr ',' '\n' | LC_ALL=C sort | uniq -d | paste -sd, -; }

declare -A fam_name fam_guard fam_defs tgt_name tgt_fam tgt_attr tgt_feat seen_t seen_f
fams=() tgts=()
while IFS= read -r line; do
    kind="${line%% *}"; body="${line#* }"
    IFS='|' read -r a b c d e <<<"$body"
    a="$(echo "$a" | tr -d ' ')"
    if [ "$kind" = F ]; then
        fams+=("$a")
        fam_name[$a]="$(unq "$b")"; fam_guard[$a]="$(unq "$c")"; fam_defs[$a]="$(unq "$d")"
        k="$(fold "${fam_name[$a]}")"
        [ -z "${seen_f[$k]+x}" ] || mismatch "family $a: name '${fam_name[$a]}' matches ${seen_f[$k]}'s under the parser's rule"
        seen_f[$k]="$a"
    else
        tgts+=("$a")
        tgt_name[$a]="$(unq "$b")"; tgt_fam[$a]="$(echo "$c" | tr -d ' ')"
        tgt_attr[$a]="$(unq "$d")"; tgt_feat[$a]="$(unq "$e")"
        k="$(fold "${tgt_name[$a]}")"
        [ -z "${seen_t[$k]+x}" ] || mismatch "target $a: name '${tgt_name[$a]}' matches ${seen_t[$k]}'s under the parser's rule"
        seen_t[$k]="$a"
        f="${tgt_feat[$a]}"
        if [ -n "$f" ]; then
            [ "$(sorted_list "$f")" = "$f" ] || mismatch "target $a: features not sorted ('$(sorted_list "$f")')"
            [ -z "$(repeats "$f")" ] || mismatch "target $a: feature $(repeats "$f") repeats in '$f'"
        fi
        if [ -n "${tgt_attr[$a]}" ] && [ "${tgt_attr[$a]}" != "$f" ]; then
            mismatch "target $a: region attributes '${tgt_attr[$a]}' differ from features '$f'"
        fi
    fi
done <<<"$rows"

[ "${#fams[@]}" -ge "$FLOOR_FAMILIES" ] || mismatch "read ${#fams[@]} family rows (floor $FLOOR_FAMILIES)"
[ "${#tgts[@]}" -ge "$FLOOR_TARGETS" ] || mismatch "read ${#tgts[@]} target rows (floor $FLOOR_TARGETS)"

portable=0
for t in "${tgts[@]}"; do
    f="${tgt_fam[$t]}"
    if [ "$f" = NONE ]; then
        portable=$((portable + 1))
        [ -z "${tgt_attr[$t]}" ] && [ -z "${tgt_feat[$t]}" ] ||
            mismatch "target $t: the portable target has a region or features"
    elif [ -z "${fam_name[$f]+x}" ]; then
        mismatch "target $t: family $f has no family row"
    fi
done
[ "$portable" = 1 ] || mismatch "$portable targets have no family (want exactly 1, the portable target)"

for f in "${fams[@]}"; do
    l="${fam_defs[$f]}"
    [ -n "$l" ] || { mismatch "family $f: an empty default list"; continue; }
    [ -z "$(repeats "$l")" ] || mismatch "family $f: default $(repeats "$l") repeats in '$l'"
    for m in $(printf '%s' "$l" | tr ',' ' '); do
        hit=""
        for t in "${tgts[@]}"; do [ "${tgt_name[$t]}" = "$m" ] && hit="$t"; done
        if [ -z "$hit" ]; then mismatch "family $f: default '$m' is no target row"
        elif [ "${tgt_fam[$hit]}" != "$f" ]; then mismatch "family $f: default '$m' is of family ${tgt_fam[$hit]}"; fi
    done
done

# THE HOST CHAIN against the guards, per preprocessor cell.
probe="$(printf '%s\n' '#define MF_FAMILY(id, name, guard, defaults)' \
    '#define MF_TARGET(id, name, family, region, features)' '#define MF_TARGET_HOST' \
    "#include \"$def\"" 'H MF_HOST_FAMILY'
    for f in "${fams[@]}"; do printf '#if %s\nG %s\n#endif\n' "${fam_guard[$f]}" "$f"; done)"
cells=0 cskip=0 host=""
cell() {   # cell LABEL COMPILER FLAGS...
    local label="$1" cc="$2"; shift 2
    command -v "$cc" >/dev/null 2>&1 || { cskip=$((cskip + 1)); say "host cell $label SKIPPED (no $cc)"; return; }
    local o; o="$(printf '%s\n' "$probe" | "$cc" "$@" -E -P -x c - 2>/dev/null)" ||
        { cskip=$((cskip + 1)); say "host cell $label SKIPPED ($cc $* -E failed)"; return; }
    local h g; h="$(printf '%s\n' "$o" | sed -n 's/^H //p' | tr -d ' ')"
    g="$(printf '%s\n' "$o" | sed -n 's/^G //p' | tr -d ' ' | paste -sd, -)"
    cells=$((cells + 1))
    case "$g" in *,*) mismatch "host cell $label: more than one family guard holds ($g)"; return ;; esac
    if [ "$h" = MF_NFAMILY ]; then
        [ -z "$g" ] || mismatch "host cell $label: the host chain names no family, but $g's guard holds"
    else
        [ "$g" = "$h" ] || mismatch "host cell $label: the host chain names $h, the guard that holds is ${g:-none}"
    fi
    [ "$label" = gcc ] && host="$h"
}
cell gcc "$GCC"
cell gcc-m32 "$GCC" -m32
cell gcc-mx32 "$GCC" -mx32
cell clang-aarch64 clang --target=aarch64-linux-gnu
[ "$cells" -ge 1 ] || mismatch "no host cell ran"

# THE COMPILER CONTROL: the host family's region targets against -march.
declare -A floor=( [MF_FAM_X86_64]="-march=x86-64 -mno-sse" )
ran=0 skipped=0
for t in "${tgts[@]}"; do
    f="${tgt_fam[$t]}"
    [ "$f" = NONE ] && continue
    if [ "$f" != "$host" ] || [ -z "${floor[$f]+x}" ] || [ -z "${tgt_attr[$t]}" ]; then
        skipped=$((skipped + 1)); continue
    fi
    mflags="$(printf '%s' "${tgt_attr[$t]}" | sed 's/^/-m/; s/,/ -m/g')"
    # shellcheck disable=SC2086
    a="$("$GCC" ${floor[$f]} $mflags -dM -E -x c /dev/null 2>&1 | LC_ALL=C sort)" ||
        { mismatch "$t: $GCC refuses ${floor[$f]} $mflags"; continue; }
    b="$("$GCC" -march="${tgt_name[$t]}" -dM -E -x c /dev/null 2>&1 | LC_ALL=C sort)" ||
        { mismatch "$t: $GCC refuses -march=${tgt_name[$t]}"; continue; }
    if [ "$a" = "$b" ]; then ran=$((ran + 1))
    else
        d="$(diff <(echo "$a") <(echo "$b") | grep -E '^[<>]' | head -4 | tr '\n' ' ')"
        mismatch "$t: the floor plus its attributes does not define what -march=${tgt_name[$t]} does: $d"
    fi
done
case "$host" in
    ""|MF_NFAMILY) say "the host matches no family row: every target SKIPPED by the compiler control" ;;
    *) [ "$ran" -ge 1 ] || mismatch "the host family $host compared no target against $GCC -march" ;;
esac

[ "$bad" = 0 ] && say "ok: ${#fams[@]} families, ${#tgts[@]} targets, $ran compared against $GCC -march, $skipped skipped (another family or no region), host ${host:-none}, $cells host cells ($cskip skipped)"
finish "$bad"
