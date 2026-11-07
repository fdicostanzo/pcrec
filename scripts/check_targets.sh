#!/usr/bin/env bash
# scripts/check_targets.sh -- THE TARGET TABLE CHECK ([XARCH-DEV] U1;
# docs/design/memfn/target_seam.md §2, target_seam_units.md §4). Run by
# `make` (the `targets-check` stamp) and failed on by `make strict` and
# `make test-memfn-targets`.
#
# The subject is src/gen/targets.def, read through the C preprocessor (the
# same X-macro rows the library compiles). The CONTROL is the compiler: for
# every target of the building host's family, `CC -march=<family floor>
# -m<each attr>` must define exactly the macros `CC -march=<name>` defines
# (the whole `-dM` output, not a chosen ISA list). The floor belongs to THIS
# check, not to the table (x86-64: `-march=x86-64 -mno-sse`, so the baseline
# row `sse2` is a real comparison and not the baseline against itself).
# Structural assertions: every family's baseline is a target of that family;
# every target's family exists; a non-empty attr is sorted and equals the
# features column; the host family's guard holds on the host. A target of
# another family is SKIPPED and counted, never silently passed.
#
# The control compiler is gcc (TARGETS_GCC, default `gcc`), whatever CC the
# build uses: §2 names gcc's `-march` as the control, and clang's whole `-dM`
# set differs by CPU-name macros alone (measured, clang 21.1.8: its
# `-march=x86-64` defines `__k8`, `-march=x86-64-v3` does not), which a
# macro-name filter could only paper over. No gcc = exit 2 (could not run).
#
# Usage: scripts/check_targets.sh [OUT]
#   prints `targets-check: ok ...` or `targets-check: MISMATCH ...` lines;
#   writes the same to OUT when given; exit 0 = ok, 1 = mismatch, 2 = could
#   not run. `make` warns on 1 and 2 and does not stop (R5-Q1: a newer gcc's
#   own -march definition must not break a stranger's build).

set -u
CC="${TARGETS_GCC:-gcc}"
root="$(cd "$(dirname "$0")/.." && pwd)"
def="$root/src/gen/targets.def"
out="${1:-}"

msgs=()
bad=0
say() { msgs+=("targets-check: $*"); }
mismatch() { say "MISMATCH $*"; bad=1; }

# The rows, one per line: F name|guard|baseline|list  /  T id|name|family|attr|features
rows="$(printf '%s\n' \
    '#define PCREC_FAMILY(id, name, guard, baseline, simd_list) F id|name|guard|#baseline|simd_list' \
    '#define PCREC_TARGET(id, name, family, attr, features) T #id|name|#family|attr|features' \
    "#include \"$def\"" | "$CC" -E -P -x c - 2>/dev/null | grep -E '^[FT] ')" || {
    say "could not read $def through $CC -E"; printf '%s\n' "${msgs[@]}"
    [ -n "$out" ] && printf '%s\n' "${msgs[@]}" > "$out"; exit 2; }

# Strip one level of C string quoting (the rows hold string literals).
unq() { local s="$1"; s="${s#\"}"; s="${s%\"}"; printf '%s' "${s//\\\"/\"}"; }

declare -A fam_of_tgt name_of_tgt attr_of_tgt fam_name fam_guard fam_base
fams=() tgts=()
while IFS= read -r line; do
    kind="${line%% *}"; body="${line#* }"
    IFS='|' read -r a b c d e <<<"$body"
    a="$(echo "$a" | tr -d ' ')"
    if [ "$kind" = F ]; then
        fams+=("$a"); fam_name[$a]="$(unq "$(echo "$b" | sed 's/^ *//; s/ *$//')")"
        fam_guard[$a]="$(unq "$(echo "$c" | sed 's/^ *//; s/ *$//')")"
        fam_base[$a]="$(unq "$(echo "$d" | tr -d ' ')")"
    else
        a="$(unq "$a")"; tgts+=("$a")
        name_of_tgt[$a]="$(unq "$(echo "$b" | tr -d ' ')")"
        fam_of_tgt[$a]="$(unq "$(echo "$c" | tr -d ' ')")"
        attr_of_tgt[$a]="$(unq "$(echo "$d" | tr -d ' ')")"
        f="$(unq "$(echo "$e" | tr -d ' ')")"
        if [ -n "${attr_of_tgt[$a]}" ]; then
            [ "${attr_of_tgt[$a]}" = "$f" ] || mismatch "$a: features '$f' differ from attr '${attr_of_tgt[$a]}'"
            sorted="$(echo "${attr_of_tgt[$a]}" | tr ',' '\n' | LC_ALL=C sort | paste -sd, -)"
            [ "$sorted" = "${attr_of_tgt[$a]}" ] || mismatch "$a: attr is not sorted ('$sorted')"
        fi
    fi
done <<<"$rows"

[ "${#fams[@]}" -gt 0 ] && [ "${#tgts[@]}" -gt 0 ] || {
    mismatch "read ${#fams[@]} family rows and ${#tgts[@]} target rows (want >= 1 each)"; }

for t in "${tgts[@]}"; do
    f="${fam_of_tgt[$t]}"
    [ "$f" = PCREC_FAM_NONE ] && continue
    [ -n "${fam_name[$f]+x}" ] || mismatch "$t: family $f has no family row"
done
for f in "${fams[@]}"; do
    b="${fam_base[$f]}"
    if [ -z "${fam_of_tgt[$b]+x}" ]; then mismatch "$f: baseline $b is not a target row"
    elif [ "${fam_of_tgt[$b]}" != "$f" ]; then mismatch "$f: baseline $b is of family ${fam_of_tgt[$b]}"; fi
done

# The host family: the one whose guard holds under CC's own target.
host=""
for f in "${fams[@]}"; do
    r="$(printf '#if %s\nHOLDS\n#endif\n' "${fam_guard[$f]}" | "$CC" -E -P -x c - 2>/dev/null | grep -c HOLDS)"
    [ "$r" = 1 ] && host="$f"
done

# The family floors: the CHECK's own column (see the header).
declare -A floor=( [PCREC_FAM_X86_64]="-march=x86-64 -mno-sse" )

ran=0 skipped=0
for t in "${tgts[@]}"; do
    f="${fam_of_tgt[$t]}"
    [ "$f" = PCREC_FAM_NONE ] && continue
    if [ "$f" != "$host" ] || [ -z "${floor[$f]+x}" ]; then skipped=$((skipped + 1)); continue; fi
    mflags=""
    [ -n "${attr_of_tgt[$t]}" ] && mflags="$(echo "${attr_of_tgt[$t]}" | sed 's/^/-m/; s/,/ -m/g')"
    # shellcheck disable=SC2086
    a="$("$CC" ${floor[$f]} $mflags -dM -E -x c /dev/null 2>&1 | LC_ALL=C sort)" || {
        mismatch "$t: $CC refuses ${floor[$f]} $mflags"; continue; }
    b="$("$CC" -march="${name_of_tgt[$t]}" -dM -E -x c /dev/null 2>&1 | LC_ALL=C sort)" || {
        mismatch "$t: $CC refuses -march=${name_of_tgt[$t]}"; continue; }
    if [ "$a" = "$b" ]; then ran=$((ran + 1))
    else
        d="$(diff <(echo "$a") <(echo "$b") | grep -E '^[<>]' | head -4 | tr '\n' ' ')"
        mismatch "$t: floor + attr does not define what -march=${name_of_tgt[$t]} does: $d"
    fi
done
[ -n "$host" ] || say "the host matches no family row (every target SKIPPED)"
[ -n "$host" ] && [ "$ran" -eq 0 ] && mismatch "the host family $host compared no target"

[ "$bad" = 0 ] && say "ok: ${#fams[@]} families, ${#tgts[@]} targets, $ran compared against $CC -march, $skipped skipped (another family), host ${host:-none}"
printf '%s\n' "${msgs[@]}"
[ -n "$out" ] && printf '%s\n' "${msgs[@]}" > "$out"
exit "$bad"
