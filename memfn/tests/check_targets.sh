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
# The subject is memfn/src/targets.def (the FACTS) and targets_c.def (the C
# emitter's family spellings and the host chain), read through the C
# preprocessor (the same X-macro rows the kit compiles). THE CONTROL IS THE
# COMPILER (the lane's adopted choice, units.md §5): for every target of the
# building host's family that has needs, `gcc <family floor> -m<each need>` must
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
# floors of family and target rows; ONE token space for the whole table (the
# owner's ruling 2026-11-07: a `-fmemfn-simd` list mixes family and target
# tokens): every family and target name distinct from every other under the
# parser's matching rule (ASCII-case-blind, otherwise exact), so no token is
# both a family and a target and no row shadows another; every target's family exists; exactly ONE familyless (portable)
# target, with no needs and no features; needs and features sorted,
# unrepeated, needs a subset of features; every family's default list
# non-empty, unrepeated, each member a target of that family.
#
# FACTS CARRY NO SPELLING (the owner's ruling 2026-11-07, emitters for C or
# Rust): every field of a facts row is a list of tokens (`[a-z0-9][a-z0-9.-]*`,
# comma-separated, or empty), which no C (or Rust) text is -- a `(`, `#`,
# `_`, quote, `=` or blank fails it -- except the one `doc` column; targets.def holds no preprocessor
# directive; and targets_c.def has exactly one spelling row per family.
#
# LEVEL ADMISSION (unit U2): the kit admits a level (levels.def) at a target
# iff the level's family token is the target's family's and every one of the
# level's `needs` is among the target's `features`. For every target of the
# building host's family and every level of that family, the table's answer
# is held to THE COMPILER's: a need is supplied at the target iff
# `gcc -march=<target> -m<need>` defines exactly what `gcc -march=<target>`
# does (the whole -dM set again), so a feature the table forgets (how
# x86-64-v3 first lacked sse2 and dropped w16) and one it invents both fail.
# Every level's family token names a family, and its test_march is a target
# token whose row admits it. LEVELS_DEF points at another levels table.
#
# THE NEEDS SUFFICE ([XARCH-NEEDSOK]): each level's RENDERED helpers (G2's
# SIMD generator, at the widest level's test_march) must compile at the floor
# plus -m<each need> alone, so a level that under-declares its needs (avx for
# avx2: S726) is red. Needs build/libpcrec.a (LIBPCREC overrides); SKIPPED,
# counted, where it is absent.
#
# THE HOST CHAIN (targets_c.def's MF_TARGET_HOST block, the kit's own #if) is
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
cdef="${TARGETS_C_DEF:-$here/../src/targets_c.def}"
ldef="${LEVELS_DEF:-$here/../src/levels.def}"
idef="${INCLUDES_C_DEF:-$here/../src/includes_c.def}"
out="${1:-}"
FLOOR_FAMILIES=2   # the design's two family rows (target_seam.md §2)
FLOOR_TARGETS=4    # generic, x86-64, x86-64-v3, armv8-a (units.md §2, K0)

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
[ -r "$def" ] && [ -r "$cdef" ] && [ -r "$ldef" ] && [ -r "$idef" ] ||
    { say "cannot read $def, $cdef, $ldef or $idef"; finish 2; }

# The rows, one per line:  F id|name|defaults   T id|name|family|needs|features
#                          C id|guard (targets_c.def)
rows="$(printf '%s\n' \
    '#define MF_FAMILY(id, name, defaults, doc) F id|name|defaults|doc' \
    '#define MF_TARGET(id, name, family, needs, features, doc) T id|name|family|needs|features|doc' \
    '#define MF_FAMILY_OF(id) id' '#define MF_NO_FAMILY NONE' \
    '#define MF_NEEDS(list) list' '#define MF_NO_NEEDS ""' \
    '#define MF_FAMILY_C(id, guard) C id|guard' \
    '#define MF_LEVEL(id, family, needs, inc, vw, test_march, forbid, stamp) L id|family|needs|test_march|stamp|inc|vw' \
    '#define MF_INCLUDE_C(bit, line) I bit|line' \
    "#include \"$def\"" "#include \"$cdef\"" "#include \"$ldef\"" "#include \"$idef\"" |
    "$GCC" -E -P -x c - 2>/dev/null | grep -E '^[FTCLI] ')" || {
    say "could not read $def, $cdef, $ldef and $idef through $GCC -E"; finish 2; }
directives="$(grep -nE '^[[:space:]]*#' "$def" | head -3 | tr '\n' ' ')"
[ -z "$directives" ] || mismatch "targets.def (the facts) holds a preprocessor directive: $directives"

# Strip one level of C string quoting and the surrounding blanks.
unq() { local s; s="$(printf '%s' "$1" | sed 's/^ *//; s/ *$//')"; s="${s#\"}"; s="${s%\"}"; printf '%s' "${s//\\\"/\"}"; }
# The parser's matching rule (memfn.h): ASCII-case-blind, otherwise exact.
fold() { printf '%s' "$1" | tr 'A-Z' 'a-z'; }
# The one prose column: a plain-English line, never C (no `#`, `_`, brace,
# semicolon, backslash, quote or `|`), non-empty, at most 100 bytes.
docline() { [ -n "$2" ] && [ "${#2}" -le 100 ] && ! printf '%s' "$2" | grep -q '[#_{};\\"|]' ||
    mismatch "$1: '$2' is not a plain-English line (empty, over 100 bytes, or C text)"; }
sorted_list() { printf '%s' "$1" | tr ',' '\n' | LC_ALL=C sort | paste -sd, -; }
repeats() { printf '%s\n' "$1" | tr ',' '\n' | LC_ALL=C sort | uniq -d | paste -sd, -; }

# A facts field: tokens, comma-separated, or empty -- never emitter text.
tokens() { [ -z "$2" ] || printf '%s' "$2" | grep -qxE '[a-z0-9][a-z0-9.-]*(,[a-z0-9][a-z0-9.-]*)*' ||
    mismatch "$1: '$2' is not a token list (emitter text in a facts row?)"; }

declare -A fam_name fam_guard fam_defs tgt_name tgt_fam tgt_attr tgt_feat seen_tok
declare -A lvl_fam lvl_needs lvl_march lvl_stamp lvl_inc lvl_vw inc_line
fams=() tgts=() lvls=()
while IFS= read -r line; do
    kind="${line%% *}"; body="${line#* }"
    IFS='|' read -r a b c d e f g <<<"$body"
    a="$(echo "$a" | tr -d ' ')"
    if [ "$kind" = L ]; then
        lvls+=("$a")
        lvl_fam[$a]="$(unq "$b")"; lvl_needs[$a]="$(unq "$c")"
        lvl_march[$a]="$(unq "$d")"; lvl_stamp[$a]="$(unq "$e")"
        lvl_inc[$a]="$(echo "$f" | tr -d ' ')"; lvl_vw[$a]="$(echo "$g" | tr -d ' ')"
        tokens "level $a needs" "${lvl_needs[$a]}"
    elif [ "$kind" = I ]; then
        [ -z "${inc_line[$a]+x}" ] || mismatch "include bit $a: more than one spelling row"
        inc_line[$a]="$(unq "$b")"
    elif [ "$kind" = C ]; then
        [ -z "${fam_guard[$a]+x}" ] || mismatch "family $a: more than one C spelling row"
        fam_guard[$a]="$(unq "$b")"
    elif [ "$kind" = F ]; then
        fams+=("$a")
        fam_name[$a]="$(unq "$b")"; fam_defs[$a]="$(unq "$c")"
        docline "family $a doc" "$(unq "$d")"
        tokens "family $a name" "${fam_name[$a]}"; tokens "family $a defaults" "${fam_defs[$a]}"
        k="$(fold "${fam_name[$a]}")"
        [ -z "${seen_tok[$k]+x}" ] || mismatch "family $a: token '${fam_name[$a]}' is also ${seen_tok[$k]}'s (one token space for families and targets)"
        seen_tok[$k]="family $a"
    else
        tgts+=("$a")
        tgt_name[$a]="$(unq "$b")"; tgt_fam[$a]="$(echo "$c" | tr -d ' ')"
        tgt_attr[$a]="$(unq "$d")"; tgt_feat[$a]="$(unq "$e")"
        docline "target $a doc" "$(unq "$f")"
        tokens "target $a name" "${tgt_name[$a]}"; tokens "target $a needs" "${tgt_attr[$a]}"
        tokens "target $a features" "${tgt_feat[$a]}"
        k="$(fold "${tgt_name[$a]}")"
        [ -z "${seen_tok[$k]+x}" ] || mismatch "target $a: token '${tgt_name[$a]}' is also ${seen_tok[$k]}'s (one token space for families and targets)"
        seen_tok[$k]="target $a"
        f="${tgt_feat[$a]}"
        if [ -n "$f" ]; then
            [ "$(sorted_list "$f")" = "$f" ] || mismatch "target $a: features not sorted ('$(sorted_list "$f")')"
            [ -z "$(repeats "$f")" ] || mismatch "target $a: feature $(repeats "$f") repeats in '$f'"
        fi
        n="${tgt_attr[$a]}"
        if [ -n "$n" ]; then
            [ "$(sorted_list "$n")" = "$n" ] || mismatch "target $a: needs not sorted ('$(sorted_list "$n")')"
            for m in $(printf '%s' "$n" | tr ',' ' '); do
                case ",$f," in *",$m,"*) ;; *) mismatch "target $a: need '$m' is not among its features '$f'" ;; esac
            done
        fi
    fi
done <<<"$rows"

# A FAMILY token equal to a TARGET token once `_` reads as `-` (x86_64 vs
# x86-64) is one typo from a different valid meaning: refused.
for f in "${fams[@]}"; do for t in "${tgts[@]}"; do
    [ "$(printf '%s' "${fam_name[$f]}" | tr 'A-Z_' 'a-z-')" != "$(printf '%s' "${tgt_name[$t]}" | tr 'A-Z_' 'a-z-')" ] ||
        mismatch "family $f: token '${fam_name[$f]}' equals target $t's '${tgt_name[$t]}' once _ reads as - (a typo would change its meaning)"
done; done

[ "${#fams[@]}" -ge "$FLOOR_FAMILIES" ] || mismatch "read ${#fams[@]} family rows (floor $FLOOR_FAMILIES)"
[ "${#tgts[@]}" -ge "$FLOOR_TARGETS" ] || mismatch "read ${#tgts[@]} target rows (floor $FLOOR_TARGETS)"

portable=0
for t in "${tgts[@]}"; do
    f="${tgt_fam[$t]}"
    if [ "$f" = NONE ]; then
        portable=$((portable + 1))
        [ -z "${tgt_attr[$t]}" ] && [ -z "${tgt_feat[$t]}" ] ||
            mismatch "target $t: the portable target has needs or features"
    elif [ -z "${fam_name[$f]+x}" ]; then
        mismatch "target $t: family $f has no family row"
    fi
done
[ "$portable" = 1 ] || mismatch "$portable targets have no family (want exactly 1, the portable target)"

for f in "${!fam_guard[@]}"; do
    [ -n "${fam_name[$f]+x}" ] || mismatch "targets_c.def spells family $f, which has no facts row"
done
for f in "${fams[@]}"; do
    [ -n "${fam_guard[$f]+x}" ] || mismatch "family $f: no C spelling row in targets_c.def"
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
probe="$(printf '%s\n' '#define MF_FAMILY_C(id, guard)' '#define MF_TARGET_HOST' \
    "#include \"$cdef\"" 'H MF_HOST_FAMILY'
    for f in "${fams[@]}"; do [ -n "${fam_guard[$f]:-}" ] && printf '#if %s\nG %s\n#endif\n' "${fam_guard[$f]}" "$f"; done)"
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

in_list() { case ",$2," in *",$1,"*) return 0 ;; esac; return 1; }
# THE FEATURES COLUMN IS COMPLETE (the kit manager's ruling, unit U2): over
# THIS check's feature vocabulary (token -> the macro gcc defines when the
# feature is enabled; a column of the check, sharing no source with the
# table), every token a host-family target lists is in the vocabulary and
# its macro is defined at `gcc -march=<name>`, and every vocabulary token
# whose macro is defined there is listed. Not in the vocabulary: features no
# kit level or target row names (crc32 among them, whose macro gcc 14 added).
declare -A vocab=(
    [MF_FAM_X86_64:fxsr]=__FXSR__ [MF_FAM_X86_64:mmx]=__MMX__ [MF_FAM_X86_64:sse]=__SSE__
    [MF_FAM_X86_64:sse2]=__SSE2__ [MF_FAM_X86_64:sse3]=__SSE3__ [MF_FAM_X86_64:ssse3]=__SSSE3__
    [MF_FAM_X86_64:sse4.1]=__SSE4_1__ [MF_FAM_X86_64:sse4.2]=__SSE4_2__ [MF_FAM_X86_64:popcnt]=__POPCNT__
    [MF_FAM_X86_64:sahf]=__LAHF_SAHF__ [MF_FAM_X86_64:cx16]=__GCC_HAVE_SYNC_COMPARE_AND_SWAP_16
    [MF_FAM_X86_64:avx]=__AVX__ [MF_FAM_X86_64:avx2]=__AVX2__ [MF_FAM_X86_64:bmi]=__BMI__
    [MF_FAM_X86_64:bmi2]=__BMI2__ [MF_FAM_X86_64:f16c]=__F16C__ [MF_FAM_X86_64:fma]=__FMA__
    [MF_FAM_X86_64:lzcnt]=__LZCNT__ [MF_FAM_X86_64:movbe]=__MOVBE__ [MF_FAM_X86_64:xsave]=__XSAVE__
)
FLOOR_VOCAB=20     # the x86-64 vocabulary's tokens, above
nv=0; for k in "${!vocab[@]}"; do [ "${k%%:*}" = "$host" ] && nv=$((nv + 1)); done
case "$host" in MF_FAM_X86_64) [ "$nv" -ge "$FLOOR_VOCAB" ] || mismatch "feature vocabulary $nv < floor $FLOOR_VOCAB" ;; esac
fcomp=0
for t in "${tgts[@]}"; do
    f="${tgt_fam[$t]}"
    [ "$f" != NONE ] && [ "$f" = "$host" ] && [ "$nv" -ge 1 ] || continue
    m="$("$GCC" -march="${tgt_name[$t]}" -dM -E -x c /dev/null 2>/dev/null)" ||
        { mismatch "$t: $GCC refuses -march=${tgt_name[$t]}"; continue; }
    for x in ${tgt_feat[$t]//,/ }; do
        if [ -z "${vocab[$f:$x]+x}" ]; then mismatch "$t: feature '$x' is not in the check's vocabulary"
        elif ! printf '%s\n' "$m" | grep -q "^#define ${vocab[$f:$x]} "; then
            mismatch "$t: lists '$x', but $GCC -march=${tgt_name[$t]} does not define ${vocab[$f:$x]}"
        fi
    done
    for k in "${!vocab[@]}"; do
        [ "${k%%:*}" = "$f" ] || continue
        x="${k#*:}"
        printf '%s\n' "$m" | grep -q "^#define ${vocab[$k]} " || continue
        in_list "$x" "${tgt_feat[$t]}" ||
            mismatch "$t: $GCC -march=${tgt_name[$t]} enables '$x' (${vocab[$k]}), which its features do not list"
    done
    fcomp=$((fcomp + 1))
done
case "$host" in
    ""|MF_NFAMILY) ;;
    *) [ "$fcomp" -ge 1 ] || mismatch "the features control compared no target" ;;
esac

# LEVEL ADMISSION: the table's answer against the compiler's.
FLOOR_LEVELS=2     # w16, w32 (R-13)
[ "${#inc_line[@]}" -ge 3 ] || mismatch "${#inc_line[@]} include spelling rows < floor 3 (string.h, w16, w32)"
[ "${#lvls[@]}" -ge "$FLOOR_LEVELS" ] || mismatch "${#lvls[@]} level rows < floor $FLOOR_LEVELS"
table_admits() {   # table_admits TARGET LEVEL
    local n f="${tgt_fam[$1]}"
    [ "$f" != NONE ] && [ "${fam_name[$f]}" = "${lvl_fam[$2]}" ] || return 1
    for n in ${lvl_needs[$2]//,/ }; do in_list "$n" "${tgt_feat[$1]}" || return 1; done
}
admitted=0 refused=0
for l in "${lvls[@]}"; do
    lf="" mt=""
    for f in "${fams[@]}"; do [ "${fam_name[$f]}" = "${lvl_fam[$l]}" ] && lf="$f"; done
    [ -n "$lf" ] || mismatch "level $l: family token '${lvl_fam[$l]}' names no family"
    for t in "${tgts[@]}"; do [ "${tgt_name[$t]}" = "${lvl_march[$l]}" ] && mt="$t"; done
    if [ -z "$mt" ]; then mismatch "level $l: test_march '${lvl_march[$l]}' is no target token"
    elif ! table_admits "$mt" "$l"; then mismatch "level $l: its test_march ${lvl_march[$l]} does not admit it"
    fi
    # its header is a FACT with one C spelling (review 2026-11-08 r5 X-1)
    i="${lvl_inc[$l]}"
    if [ -z "${inc_line[$i]+x}" ]; then mismatch "level $l: include bit '$i' has no spelling row in includes_c.def"
    elif ! printf '%s' "${inc_line[$i]}" | grep -qxE '#include <[A-Za-z0-9_./]+>\\n'; then
        mismatch "level $l: include bit $i's spelling '${inc_line[$i]}' is not one #include line"
    fi
    for k in "${lvls[@]}"; do
        [ "$k" = "$l" ] || [ "${lvl_inc[$k]}" != "$i" ] || mismatch "levels $l and $k share include bit $i (one bit per level)"
    done
    [ -n "$lf" ] && [ "$lf" = "$host" ] && [ -n "${floor[$lf]+x}" ] || continue
    for t in "${tgts[@]}"; do
        [ "${tgt_fam[$t]}" = "$lf" ] || continue
        base="$("$GCC" -march="${tgt_name[$t]}" -dM -E -x c /dev/null 2>&1 | LC_ALL=C sort)" ||
            { mismatch "$t: $GCC refuses -march=${tgt_name[$t]}"; continue; }
        truth=1
        for n in ${lvl_needs[$l]//,/ }; do
            w="$("$GCC" -march="${tgt_name[$t]}" -m"$n" -dM -E -x c /dev/null 2>&1 | LC_ALL=C sort)" ||
                { mismatch "level $l at $t: $GCC refuses -m$n"; truth=x; break; }
            [ "$w" = "$base" ] || truth=0
        done
        [ "$truth" = x ] && continue
        if table_admits "$t" "$l"; then got=1; else got=0; fi
        if [ "$got" != "$truth" ]; then
            mismatch "level $l at ${tgt_name[$t]}: the table $([ "$got" = 1 ] && echo admits || echo refuses) it, $GCC -march=${tgt_name[$t]} $([ "$truth" = 1 ] && echo supplies || echo lacks) its needs (${lvl_needs[$l]}): a feature is $([ "$got" = 1 ] && echo invented || echo missing)"
        elif [ "$got" = 1 ]; then admitted=$((admitted + 1))
        else refused=$((refused + 1)); fi
    done
done
case "$host" in
    ""|MF_NFAMILY) ;;
    *) [ "$admitted" -ge 1 ] && [ "$refused" -ge 1 ] ||
           mismatch "level admission compared $admitted admitted and $refused refused (both must be >= 1)" ;;
esac

# THE NEEDS SUFFICE (review 2026-11-08 r5 checks-7, [XARCH-NEEDSOK]; the S726
# closer): admission above proves the table agrees with the compiler about
# which targets SUPPLY a level's needs; it cannot see a level whose needs are
# too weak for its own intrinsics (avx declared for avx2 text), because every
# target that carries the one carries the other. So the level's RENDERED
# helpers are compiled at this check's floor plus -m<each need> and nothing
# else (the floor of the controls above; the control is the compiler): they
# must compile. The text is the kit's, rendered by G2's SIMD generator
# (memfn/tests/g2/g2_simd_gen.c) at the last level's test_march (the widest
# level, whose target admits every level), with G2's host region left out.
# A level's compile keeps the helpers of its stamp and of every level of its
# family of lesser width (a w32 helper falls through to w16) and the shared
# bodies and loaders, never the selector or wrapper (host text calling the
# higher levels). Needs libpcrec.a (LIBPCREC overrides); a missing library
# or a host family without a floor SKIPS the cell, counted.
#
# A CATCH IS A CHECK FAILURE, NEVER A COMPILER ERROR ON THIS CHECK'S OUTPUT
# (lane xarchfix, 2026-11-12): each compile's output stays in its own file in
# the cell's scratch directory (kept, and named, when the cell fails), and the
# mismatch line carries the first diagnostic's SUMMARY in words, never the
# compiler's own error line; a level the kit rendered no helper for is found
# by the extraction itself and never compiled. A mech arm reads a compiler
# error in its log as a plant that does not compile ([MECH-NOCOMPILE]).
NEEDS_FLOOR=2      # level cells compiled when the cell runs: w16 and w32
needsok=0 needsskip=0 needskeep=0
# The first diagnostic of a compiler log, in words (first match wins).
diag_summary() {
    local d fn
    d="$(grep -m1 -E '(error|warning): ' "$1")"
    [ -n "$d" ] || { printf 'no diagnostic line (exit status only)'; return; }
    fn="$(printf '%s' "$d" | sed -n "s/.*inlining failed in call to .always_inline. .\([A-Za-z0-9_]*\).: target specific option mismatch.*/\1/p")"
    if [ -n "$fn" ]; then
        printf 'the intrinsic %s needs an ISA feature these flags do not enable (always_inline target mismatch)' "$fn"
    else
        printf 'the compiler refused the text: %s' "$(printf '%s' "$d" | sed -E 's/^.*(error|warning): //; s/(error|warning):/\1 -/g' | head -c 160)"
    fi
}
if [ -n "${floor[$host]+x}" ]; then
    lib="${LIBPCREC:-$here/../../build/libpcrec.a}"
    inc="$here/../include"; g2d="$here/g2"
    if [ ! -r "$lib" ] || [ ! -r "$g2d/g2_simd_gen.c" ]; then
        needsskip=1; say "needs-suffice cell SKIPPED (cannot read $lib)"
    else
        nd="$(mktemp -d "${TMPDIR:-/var/tmp}/targets-needs.XXXXXX")" || { say "no scratch directory"; finish 2; }
        top="${lvl_march[${lvls[${#lvls[@]}-1]}]}"
        if ! "$GCC" -O0 -I "$inc" -o "$nd/gen" "$g2d/g2_simd_gen.c" "$lib" >"$nd/gen.log" 2>&1 ||
           ! "$nd/gen" 1 24 "$nd" "$top" >>"$nd/gen.log" 2>&1; then
            needskeep=1
            mismatch "needs-suffice: the G2 SIMD generator did not build or run at $top: $(diag_summary "$nd/gen.log") (output: $nd/gen.log)"
        else
            sites="$nd/g2v_sites.c"
            head -n "$(( $(grep -n '^#if defined(__clang__)' "$sites" | head -1 | cut -d: -f1) - 1 ))" "$sites" > "$nd/head.c"
            for l in "${lvls[@]}"; do
                allowed=""
                for k in "${lvls[@]}"; do
                    [ "${lvl_fam[$k]}" = "${lvl_fam[$l]}" ] && [ "${lvl_vw[$k]}" -le "${lvl_vw[$l]}" ] && allowed="$allowed,${lvl_stamp[$k]}"
                done
                { cat "$nd/head.c"
                  awk -v allowed="${allowed#,}" -v own="${lvl_stamp[$l]}" -v miss="$nd/lv_$l.nohelper" '
                    BEGIN { n = split(allowed, a, ","); for (i = 1; i <= n; i++) ok[a[i]] = 1; ok["body"] = 1 }
                    /^\/\* G2V KIT TEXT BEGIN/ { on = 1; next }
                    /^\/\* G2V KIT TEXT END/ { on = 0 }
                    !on { next }
                    { if (!d) { if ($0 !~ /^static/) next; d = 1; buf = ""; nm = ""
                          if (match($0, /[A-Za-z0-9_]+\(/)) nm = substr($0, RSTART, RLENGTH - 1)
                          one = ($0 ~ /\{.*\}[ \t]*$/) }
                      buf = buf $0 "\n"
                      if (one || $0 ~ /^}/) { d = 0; keep = 1
                          if (nm ~ /__[a-z0-9]+$/) { s = nm; sub(/.*__/, "", s); keep = (s in ok); if (s == own) own_n++ }
                          else if (nm ~ /^g2v_[fc][0-9]+$/) keep = 0
                          if (keep) printf "%s", buf } }
                    END { if (!own_n) print own > miss }' "$sites"
                } > "$nd/lv_$l.c"
                if [ -e "$nd/lv_$l.nohelper" ]; then
                    needskeep=1
                    mismatch "level $l (stamp ${lvl_stamp[$l]}, needs '${lvl_needs[$l]}'): the kit rendered no helper of stamp ${lvl_stamp[$l]} at $top, so the level cannot be compiled (the kit refuses it at the widest level's target?)"
                    continue
                fi
                mflags="$(printf '%s' "${lvl_needs[$l]}" | sed 's/^/-m/; s/,/ -m/g')"
                # shellcheck disable=SC2086
                if "$GCC" -I "$g2d" -O2 -fkeep-inline-functions -fkeep-static-functions -Wno-unused-function \
                        ${floor[$host]} $mflags -c -o /dev/null "$nd/lv_$l.c" >"$nd/lv_$l.log" 2>&1; then needsok=$((needsok + 1))
                else
                    needskeep=1
                    mismatch "level $l (stamp ${lvl_stamp[$l]}, needs '${lvl_needs[$l]}'): its rendered helpers do not compile at ${floor[$host]} $mflags, so the needs are too weak for its intrinsics: $(diag_summary "$nd/lv_$l.log") (compiler output: $nd/lv_$l.log)"
                fi
            done
        fi
        if [ "$needskeep" = 1 ]; then rm -f "$nd/gen"; say "needs-suffice scratch kept: $nd"; else rm -rf "$nd"; fi
        [ "$needsok" -ge "$NEEDS_FLOOR" ] || mismatch "the needs-suffice control compiled $needsok levels (floor $NEEDS_FLOOR)"
    fi
fi

[ "$bad" = 0 ] && say "ok: ${#fams[@]} families, ${#tgts[@]} targets, $ran compared against $GCC -march, $skipped skipped (another family or no needs), host ${host:-none}, $cells host cells ($cskip skipped), level admission $admitted admitted + $refused refused against $GCC, features complete at $fcomp targets over $nv vocabulary tokens, needs suffice at $needsok levels ($needsskip skipped)"
finish "$bad"
