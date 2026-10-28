#!/usr/bin/env bash
# d27/run.sh — D27 spec-first tests for [INLINE-C] stage 2 (embedded C).
#
#   PCREC=build/pcrec CC=gcc bash tests/code/d27/run.sh
#
# Every expectation is derived from docs/spec (match_api.md §11.9-§11.10,
# cli.md §1.1.1/§1.10/§1.17/§1.22, rxt_format.md §1.1, pattern_language.md
# §7.12); each case carries its citation. Prints `PASS name` /
# `FAIL name: expected X got Y` per case and a final `d27: N passed, M failed`.
# Writes only under $D27_OUT (default ${TMPDIR:-build}/d27run). The cases name
# their file operands as `d27/rxt/...` (the author's cell layout, and the
# `#line` expectations quote them), so the run works in a scratch root whose
# `d27` is a copy of this directory with the fixtures' `.rxtin` renamed
# `.rxt`: stored as `.rxt` they would be walked by every `.rxt` corpus run.
set -u

D27=$(cd "$(dirname "$0")" && pwd)
OUT=${D27_OUT:-${TMPDIR:-$D27/../../../build}/d27run}
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
CELL=$OUT/cell
rm -rf -- "$CELL"
mkdir -p "$CELL"
mkdir -p "$CELL/d27/rxt"
ln -s "$D27/hdr" "$CELL/d27/hdr"
for f in "$D27"/rxt/*.rxtin; do cp "$f" "$CELL/d27/rxt/$(basename "$f" in)"; done
: "${PCREC:?set PCREC=<path to pcrec>}"
CC=${CC:-gcc}
case $PCREC in /*) ;; *) PCREC=$PWD/$PCREC ;; esac
W=$OUT/work
rm -rf -- "$W"
mkdir -p "$W/cli" "$W/m" "$W/fb" "$W/misc"
T="timeout 30"
# match_api.md §6 (the ASCII rule): every artifact compiles clean under
# -Wall -Wextra -Werror -Wbidi-chars, a code segment's own bytes excepted
GCCF=(-std=gnu11 -O1 -Wall -Wextra -Werror -Wbidi-chars=any)

npass=0
nfail=0
pass() { echo "PASS $1"; npass=$((npass + 1)); }
fail() { echo "FAIL $1: $2"; nfail=$((nfail + 1)); }
# tally the PASS/FAIL lines a driver printed
tally() {
    local f=$1 l
    while IFS= read -r l; do
        case $l in
            PASS\ *) echo "$l"; npass=$((npass + 1)) ;;
            FAIL\ *) echo "$l"; nfail=$((nfail + 1)) ;;
        esac
    done <"$f"
}
oneline() { tr '\n' ' ' <"$1" | cut -c1-240; }

# ------------------------------------------------------------------
# 1. CLI cases (cli_cases.tsv): exit code, diagnostic, written or not
# ------------------------------------------------------------------
while IFS=$'\t' read -r name cite args pat want_exit ere written; do
    case $name in '' | \#*) continue ;; esac
    out=$W/cli/$name.c
    cmd=("$PCREC")
    if [ "$args" != "-" ]; then
        eval "extra=($args)"
        cmd+=("${extra[@]}")
    fi
    [ "$written" != none ] && cmd+=(-o "$out")
    [ "$pat" != "-" ] && cmd+=(--pattern-esc --pattern "\"$pat\"")
    (cd "$W/cli" && $T "${cmd[@]}" >"$W/cli/$name.stdout" 2>"$W/cli/$name.stderr")
    got=$?
    why=""
    [ "$got" = "$want_exit" ] || why="exit: expected $want_exit got $got (stderr: $(oneline "$W/cli/$name.stderr"))"
    if [ -z "$why" ] && [ "$ere" != "-" ] && ! grep -Eqi -- "$ere" "$W/cli/$name.stderr"; then
        why="stderr: expected /$ere/ got: $(oneline "$W/cli/$name.stderr")"
    fi
    if [ -z "$why" ]; then
        case $written in
            yes) [ -s "$out" ] || why="expected $out written, it is not" ;;
            no) { [ -e "$out" ] || [ -e "${out%.c}.h" ]; } && why="refused compile left $out or its .h written" ;;
            none) grep -q 'static ptrdiff_t' "$W/cli/$name.stdout" && why="describe mode wrote C to stdout" ;;
        esac
    fi
    if [ -z "$why" ]; then pass "cli.$name"; else fail "cli.$name [$cite]" "$why"; fi
done <"$D27/cli_cases.tsv"

# A diagnostic never passes a non-ASCII byte of a refused value through
# (match_api.md §11.9¶3's reason: a bidi control must not reach a terminal).
rawcheck() { # name stderr-file
    if LC_ALL=C grep -q $'[\x80-\xff]' "$2"; then fail "$1 [§11.9¶3 reason]" "raw non-ASCII byte on stderr: $(oneline "$2" | od -c | head -3 | tr '\n' ' ')"
    else pass "$1"; fi
}
rawcheck cli.hdr_bidi_refused_no_raw_bytes "$W/cli/hdr_bidi_refused.stderr"
rawcheck cli.hdr_nonascii_refused_no_raw_bytes "$W/cli/hdr_nonascii_refused.stderr"

# ------------------------------------------------------------------
# 2. compile-and-run cases (match_cases.tsv), driver_match.c
# ------------------------------------------------------------------
while IFS=$'\t' read -r name cite args pat subj want; do
    case $name in '' | \#*) continue ;; esac
    gen=$W/m/$name.c
    cmd=("$PCREC" --allow-code=c --features all)
    if [ "$args" != "-" ]; then
        eval "extra=($args)"
        cmd+=("${extra[@]}")
    fi
    cmd+=(-o - --pattern-esc --pattern "\"$pat\"")
    if ! $T "${cmd[@]}" >"$gen" 2>"$W/m/$name.pcrec.err"; then
        fail "run.$name [$cite]" "expected $want got pcrec refusal: $(oneline "$W/m/$name.pcrec.err")"
        continue
    fi
    if ! $T "$CC" "${GCCF[@]}" -DGEN_C="\"$gen\"" -o "$W/m/$name.bin" "$D27/driver_match.c" 2>"$W/m/$name.cc.err"; then
        fail "run.$name [$cite]" "expected $want got C compile error: $(oneline "$W/m/$name.cc.err")"
        continue
    fi
    printf '%b' "$subj" >"$W/m/$name.subj"
    $T "$W/m/$name.bin" "$W/m/$name.subj" >"$W/m/$name.out" 2>/dev/null
    rc=$?
    if [ $rc -ge 128 ] && [ $rc -ne 124 ]; then
        got=TRAP
    elif [ $rc -ne 0 ]; then
        got="EXIT $rc"
    else
        got=$(cat "$W/m/$name.out")
    fi
    # expected "M s e" is a token prefix of the driver's line
    case "$got " in
        "$want "*) pass "run.$name" ;;
        *) fail "run.$name [$cite]" "expected '$want' got '$got'" ;;
    esac
done <"$D27/match_cases.tsv"

# match_api.md §6 (the ASCII rule, the paragraph before §6.1): every byte of
# the artifact is ASCII "except the bytes of an embedded code segment and of a
# code-header line". Every non-ASCII line of these artifacts must be a line of
# the segment's text (after the first #line).
for name in passthrough_byte_compiles bidi_literal_outside_code nonascii_comment_in_code; do
    gen=$W/m/$name.c
    [ -s "$gen" ] || { fail "ascii.$name [§6 ASCII rule]" "no artifact (see run.$name)"; continue; }
    fl=$(grep -n '^#line' "$gen" | head -1 | cut -d: -f1)
    bad=$(LC_ALL=C grep -n $'[\x80-\xff]' "$gen" | cut -d: -f1 | awk -v fl="${fl:-0}" '$1 <= fl' | tr '\n' ' ')
    if [ -z "$bad" ]; then pass "ascii.$name"; else fail "ascii.$name [§6 ASCII rule]" "non-ASCII bytes outside the segment on lines: $bad"; fi
done

# ------------------------------------------------------------------
# 3. span helpers called directly (§11.10), driver_helpers.c
# ------------------------------------------------------------------
gen=$W/misc/helpers_gen.c
if $T "$PCREC" --allow-code=c -o - --pattern '(?C`c: return RX_PASS;`)a' >"$gen" 2>"$W/misc/helpers.err" &&
    $T "$CC" "${GCCF[@]}" -DGEN_C="\"$gen\"" -o "$W/misc/helpers.bin" "$D27/driver_helpers.c" 2>>"$W/misc/helpers.err"; then
    $T "$W/misc/helpers.bin" >"$W/misc/helpers.out" 2>&1
    tally "$W/misc/helpers.out"
else
    fail "helpers.build [§11.10¶1]" "could not build: $(oneline "$W/misc/helpers.err")"
fi
# the same helpers from a HAND-WRITTEN-binding artifact (§11.10¶1 "alike")
gen=$W/misc/helpers_named.c
if $T "$PCREC" -o - --features callouts --pattern '(?C"d27x")a' >"$gen" 2>"$W/misc/helpers_named.err" &&
    $T "$CC" "${GCCF[@]}" -DGEN_C="\"$gen\"" -c -o "$W/misc/helpers_named.o" "$D27/driver_helpers.c" 2>>"$W/misc/helpers_named.err"; then
    pass "helpers.named_binding_artifact_carries_helpers"
else
    fail "helpers.named_binding_artifact_carries_helpers [§11.10¶1]" "$(oneline "$W/misc/helpers_named.err")"
fi

# ------------------------------------------------------------------
# 4. stamps in the split form's .h (§6.3.1¶1, §6.3.2, §11.2¶3, §11.9¶8)
# ------------------------------------------------------------------
stamp_case() { # name cite prefix pattern pcrec-args... -- cc-defines...
    local name=$1 cite=$2 pfx=$3 pat=$4
    shift 4
    local pa=() da=()
    while [ $# -gt 0 ] && [ "$1" != -- ]; do pa+=("$1"); shift; done
    [ $# -gt 0 ] && shift
    da=("$@")
    local dir=$W/misc/st_$name
    mkdir -p "$dir"
    if ! $T "$PCREC" "${pa[@]}" -p "$pfx" -o "$dir/a.c" --pattern "$pat" 2>"$dir/err"; then
        fail "stamps.$name [$cite]" "pcrec refused: $(oneline "$dir/err")"
        return
    fi
    local up
    up=$(printf '%s' "$pfx" | tr a-z A-Z)
    if ! $T "$CC" "${GCCF[@]}" -DGEN_H="\"$dir/a.h\"" -DCASE="\"stamps.$name\"" -DP_="$up" "${da[@]}" \
        -o "$dir/bin" "$D27/driver_stamps.c" 2>"$dir/cc.err"; then
        fail "stamps.$name [$cite]" "driver did not compile against the .h: $(oneline "$dir/cc.err")"
        return
    fi
    $T "$dir/bin" >"$dir/out" 2>&1
    tally "$dir/out"
}
stamp_case code_only "§6.3.2;§11.9¶8" rx 'a(?C`c: return RX_PASS;`)b' --allow-code=c -- \
    -DWANT_CALLOUTS=1 -DWANT_BINDINGS='""' -DWANT_LANGS='"c"' -DWANT_SPAN=1
stamp_case two_segments "§11.2¶3" rx '(?C`c: return RX_PASS;`)a(?C`c: return RX_PASS;`)' --allow-code=c -- \
    -DWANT_CALLOUTS=2 -DWANT_BINDINGS='""' -DWANT_LANGS='"c"' -DWANT_SPAN=1
stamp_case mixed "§6.3.2 _CALLOUT_BINDINGS sorted, distinct; code not listed" rx '(?C"octet")(?C1)a(?C`c: return RX_PASS;`)(?C"octet")' --allow-code=c --features callouts -- \
    -DWANT_CALLOUTS=4 -DWANT_BINDINGS='"rx_callout_1,rx_callout_octet"' -DWANT_LANGS='"c"' -DWANT_SPAN=1
stamp_case unreachable_counted "§11.2¶3 'a site no match can reach ... is counted'" rx '(?:(?C`c: return RX_PASS;`)){0}a' --allow-code=c -- \
    -DWANT_CALLOUTS=1 -DWANT_BINDINGS='""' -DWANT_LANGS='"c"' -DWANT_SPAN=1
stamp_case binding_named_c "§11.9¶1 '(?C\"c,consume\") names the binding c'" rx '(?C"c,consume")a' --features callouts -- \
    -DWANT_CALLOUTS=1 -DWANT_BINDINGS='"rx_callout_c"' -DWANT_NO_LANGS=1 -DWANT_SPAN=1
stamp_case no_callout "§1¶6b 'An artifact with no callout site emits none of it'" rx 'abc' -- \
    -DWANT_NO_LANGS=1 -DWANT_NO_CALLOUTS=1 -DWANT_SPAN=0
stamp_case prefixed "§1¶2 <PREFIX>_ family" foo 'a(?C`c: return RX_PASS;`)b' --allow-code=c -- \
    -DWANT_CALLOUTS=1 -DWANT_BINDINGS='""' -DWANT_LANGS='"c"' -DWANT_SPAN=1

# PCREC_FEATURE_MODULES under --features all never lists code-c (cli §1.17¶3, match_api §6.3.11¶1)
dir=$W/misc/st_features_all
mkdir -p "$dir"
if $T "$PCREC" --features all --allow-code=c -o - --pattern 'a(?C`c: return RX_PASS;`)b' >"$dir/a.c" 2>"$dir/err"; then
    if grep -E '^#define PCREC_FEATURE_MODULES ' "$dir/a.c" | grep -q 'code-c'; then
        fail "stamps.feature_modules_all_excludes_code [cli§1.17¶3]" "$(grep -E '^#define PCREC_FEATURE_MODULES ' "$dir/a.c")"
    else
        pass "stamps.feature_modules_all_excludes_code"
    fi
else
    fail "stamps.feature_modules_all_excludes_code [cli§1.17¶3]" "pcrec refused: $(oneline "$dir/err")"
fi

# ------------------------------------------------------------------
# 5. names, bindings, macro hygiene (§11.2¶1a, §11.9¶4-¶5), driver_names.c
# ------------------------------------------------------------------
gen=$W/misc/names_gen.c
names_pat='"(?C`c: return RX_PASS;`)a(?C`c:\n#define D27_FROM_CODE 1\nreturn RX_FAIL; /* D27_LAST_MARK */\n`)|b(?<nm>z)?"'
if $T "$PCREC" --allow-code=c --features all -p foo -o - --pattern-esc --pattern "$names_pat" >"$gen" 2>"$W/misc/names.err" &&
    $T "$CC" "${GCCF[@]}" -DGEN_C="\"$gen\"" -o "$W/misc/names.bin" "$D27/driver_names.c" 2>>"$W/misc/names.err"; then
    $T "$W/misc/names.bin" >"$W/misc/names.out" 2>&1
    tally "$W/misc/names.out"
else
    fail "names.build [§11.2¶1a;§11.9¶4]" "$(oneline "$W/misc/names.err")"
fi
# §11.9¶4: "its definition comes LAST in the .c, after everything else the
# artifact writes" -- after the last segment's text only the segment's closing,
# #undef lines (and blank lines) may follow.
if [ -s "$gen" ]; then
    # skip the rest of the last segment's function (up to its closing brace
    # in column 0), then only #undef and blank lines may remain
    lm=$(grep -n 'D27_LAST_MARK' "$gen" | tail -1 | cut -d: -f1)
    tailtxt=$(awk -v lm="$lm" 'f == 2 {print} f == 1 && /^}/ {f = 2} NR == lm {f = 1}' "$gen" | grep -Ev '^[[:space:]]*$|^#undef ' || true)
    if [ -z "$tailtxt" ]; then pass "names.definition_last"; else
        fail "names.definition_last [§11.9¶4]" "after the last segment: $(printf '%s' "$tailtxt" | tr '\n' ' ' | cut -c1-200)"
    fi
    # §11.9¶4: the macro set comes before the first #line
    ms=$(grep -n '^#define RX_SUBJ' "$gen" | head -1 | cut -d: -f1)
    fl=$(grep -n '^#line' "$gen" | head -1 | cut -d: -f1)
    if [ -n "$ms" ] && [ -n "$fl" ] && [ "$ms" -lt "$fl" ]; then pass "names.macro_set_before_first_line"; else
        fail "names.macro_set_before_first_line [§11.9¶4]" "RX_SUBJ define at line '${ms:-none}', first #line at '${fl:-none}'"
    fi
    # §11.9¶4: `--pattern` text is named <command line>
    if grep -q '^#line [0-9][0-9]* "<command line>"' "$gen"; then pass "names.line_command_line"; else
        fail "names.line_command_line [§11.9¶4]" "no '#line N \"<command line>\"' in the .c"
    fi
    # §11.9¶4: under --pattern-esc every decoded line carries its own #line naming the opener's line
    nl=$(grep -c '^#line 1 "<command line>"' "$gen")
    if [ "$nl" -ge 4 ]; then pass "names.pattern_esc_line_per_decoded_line"; else
        fail "names.pattern_esc_line_per_decoded_line [§11.9¶4]" "expected >=4 '#line 1 \"<command line>\"' (segment 1 + segment 2's 3 non-empty decoded lines), got $nl"
    fi
fi

# two code artifacts in one translation unit (§1¶5-¶6b, §11.9¶4)
ga=$W/misc/two_a.c gb=$W/misc/two_b.c
if $T "$PCREC" --allow-code=c -p pa -o - --pattern 'x(?C`c: return RX_POS == 1 ? RX_PASS : RX_FAIL;`)a' >"$ga" 2>"$W/misc/two.err" &&
    $T "$PCREC" --allow-code=c -p pb -o - --pattern 'x(?C`c: return RX_POS == 1 ? RX_PASS : RX_FAIL;`)b' >"$gb" 2>>"$W/misc/two.err" &&
    $T "$CC" "${GCCF[@]}" -DGEN_A="\"$ga\"" -DGEN_B="\"$gb\"" -o "$W/misc/two.bin" "$D27/driver_two.c" 2>>"$W/misc/two.err"; then
    $T "$W/misc/two.bin" >"$W/misc/two.out" 2>&1
    tally "$W/misc/two.out"
else
    fail "two.one_translation_unit [§1¶6a;§11.9¶4]" "$(oneline "$W/misc/two.err")"
fi

# ------------------------------------------------------------------
# 6. #line reaches gcc's diagnostics (§11.9¶4)
# ------------------------------------------------------------------
diag_case() { # name cite expect-ERE gen-producing pcrec args...
    local name=$1 cite=$2 ere=$3
    shift 3
    local dir=$W/misc/diag_$name
    mkdir -p "$dir"
    if ! (cd "$CELL" && $T "$PCREC" "$@" >"$dir/a.c" 2>"$dir/err"); then
        fail "diag.$name [$cite]" "pcrec refused: $(oneline "$dir/err")"
        return
    fi
    if $T "$CC" -std=gnu11 -c -o "$dir/a.o" "$dir/a.c" 2>"$dir/cc.err"; then
        fail "diag.$name [$cite]" "expected a gcc error in the user's code, compile succeeded"
        return
    fi
    if grep -Eq -- "$ere" "$dir/cc.err"; then pass "diag.$name"; else
        fail "diag.$name [$cite]" "expected gcc diagnostic /$ere/ got: $(grep -m2 -E 'error' "$dir/cc.err" | tr '\n' ' ' | cut -c1-200)"
    fi
}
# 'd' of d27_undeclared is pattern byte 16 (0-based): column 17
diag_case cmdline_col "§11.9¶4 '<command line>', padded to its column" \
    '^<command line>:1:17: error: .d27_undeclared' \
    --allow-code=c -o - --pattern 'ab(?C`c: return d27_undeclared;`)'
# file operand as typed, line 4; "pattern " is 8 bytes, so column 8+17 = 25
diag_case file_line_col "§11.9¶4 'a FILE operand as typed' + line + column" \
    '^d27/rxt/line\.rxt:4:25: error: .d27_undeclared' \
    --allow-code=c -o - d27/rxt/line.rxt
diag_case file_as_typed_dotdot "§11.9¶4 'a FILE operand as typed'" \
    '^\./d27/rxt/\.\./rxt/line\.rxt:4:' \
    --allow-code=c -o - ./d27/rxt/../rxt/line.rxt
diag_case file_esc_opener_line "§11.9¶4 'every decoded line carries its own #line naming the opener's line'" \
    '^d27/rxt/line_esc\.rxt:4(:[0-9]+)?: error: .d27_undeclared2' \
    --allow-code=c -o - d27/rxt/line_esc.rxt
diag_case cmdline_esc_line1 "§11.9¶4 (--pattern-esc: every decoded line names the opener's line)" \
    '^<command line>:1(:[0-9]+)?: error: .d27_undeclared3' \
    --allow-code=c -o - --pattern-esc --pattern '"ab(?C`c:\nint q = 1;\n\nreturn d27_undeclared3 + q;`)"'

# ------------------------------------------------------------------
# 7. --code-header placement and build (§11.9¶7, cli §1.22¶2)
# ------------------------------------------------------------------
dir=$W/misc/hdr_cli
mkdir -p "$dir"
if $T "$PCREC" --allow-code=c --code-header c:d27a.h --code-header 'c:"d27b.h"' --code-header c:d27a.h \
    '--code-header=c:<stdint.h>' -o "$dir/a.c" \
    --pattern 'a(?C`c: return (d27_a() == 7 && d27_b() == 8) ? RX_PASS : RX_FAIL;`)b' 2>"$dir/err"; then
    n_a=$(grep -c '^#include "d27a.h"' "$dir/a.c")
    [ "$n_a" = 1 ] && pass "hdr.cli_repeated_once" || fail "hdr.cli_repeated_once [cli§1.22¶2]" "expected 1 '#include \"d27a.h\"' got $n_a"
    grep -q '^#include "d27a.h"' "$dir/a.c" && pass "hdr.cli_bare_name_quoted" || fail "hdr.cli_bare_name_quoted [cli§1.22¶2 'a bare name (written as \"name\")']" "no '#include \"d27a.h\"'"
    la=$(grep -n '^#include "d27a.h"' "$dir/a.c" | head -1 | cut -d: -f1)
    lb=$(grep -n '^#include "d27b.h"' "$dir/a.c" | head -1 | cut -d: -f1)
    ls_=$(grep -n '^#include <stdint.h>' "$dir/a.c" | tail -1 | cut -d: -f1)
    ms=$(grep -n '^#define RX_SUBJ' "$dir/a.c" | head -1 | cut -d: -f1)
    seg=$(grep -n 'd27_a() == 7' "$dir/a.c" | grep -v Pattern | grep -v '\.pattern' | tail -1 | cut -d: -f1)
    if [ -n "$la" ] && [ -n "$lb" ] && [ -n "$ls_" ] && [ -n "$ms" ] && [ -n "$seg" ] &&
        [ "$ms" -lt "$la" ] && [ "$la" -lt "$lb" ] && [ "$lb" -lt "$ls_" ] && [ "$ls_" -lt "$seg" ]; then
        pass "hdr.cli_order_after_macro_set_before_segment"
    else
        fail "hdr.cli_order_after_macro_set_before_segment [§11.9¶4;§11.9¶7]" "lines: RX_SUBJ=$ms d27a=$la d27b=$lb stdint=$ls_ segment=$seg"
    fi
    if grep -Eq '^#include "d27' "$dir/a.h"; then
        fail "hdr.cli_only_in_c [§11.9¶7 'only in the .c']" "the .h #includes a code-header"
    else
        pass "hdr.cli_only_in_c"
    fi
    if $T "$CC" "${GCCF[@]}" -I "$D27/hdr" -DGEN_C="\"$dir/a.c\"" -o "$dir/bin" "$D27/driver_match.c" 2>"$dir/cc.err"; then
        # driver_match includes the .c; the .c includes a.h by name, found beside it
        printf 'ab' >"$dir/subj"
        if [ "$($T "$dir/bin" "$dir/subj")" = "M 0 2" ]; then pass "hdr.cli_build_runs"; else
            fail "hdr.cli_build_runs [§11.9¶7]" "expected 'M 0 2' got '$($T "$dir/bin" "$dir/subj")'"
        fi
    else
        fail "hdr.cli_build_runs [§11.9¶7]" "C compile failed: $(oneline "$dir/cc.err")"
    fi
else
    fail "hdr.cli [cli§1.22¶2]" "pcrec refused: $(oneline "$dir/err")"
fi
# a code-header with the grant and no segment is still emitted (cli §1.22¶2 "Each is emitted")
dir=$W/misc/hdr_noseg
mkdir -p "$dir"
if $T "$PCREC" --allow-code=c --code-header c:d27a.h -o - --pattern 'abc' >"$dir/a.c" 2>"$dir/err"; then
    grep -q '^#include "d27a.h"' "$dir/a.c" && pass "hdr.no_segment_still_emitted" ||
        fail "hdr.no_segment_still_emitted [cli§1.22¶2]" "no '#include \"d27a.h\"' in a granted no-segment artifact"
else
    fail "hdr.no_segment_still_emitted [cli§1.22¶2]" "pcrec refused: $(oneline "$dir/err")"
fi

# ------------------------------------------------------------------
# 8. file operands (cli §1.1.1¶4, §1.22, rxt_format §1.1)
# ------------------------------------------------------------------
fb() { # name cite want-exit stderr-ERE written(yes|no) files-expected(list or -) pcrec-args...
    local name=$1 cite=$2 want=$3 ere=$4 wr=$5 files=$6
    shift 6
    local dir=$W/fb/$name
    mkdir -p "$dir/out"
    (cd "$CELL" && $T "$PCREC" "$@" -o "$dir/out" >"$dir/stdout" 2>"$dir/stderr")
    local got=$? why=""
    [ "$got" = "$want" ] || why="exit: expected $want got $got (stderr: $(oneline "$dir/stderr"))"
    if [ -z "$why" ] && [ "$ere" != - ] && ! grep -Eqi -- "$ere" "$dir/stderr"; then
        why="stderr: expected /$ere/ got: $(oneline "$dir/stderr")"
    fi
    if [ -z "$why" ]; then
        local have
        have=$(cd "$dir/out" && ls | tr '\n' ' ' | sed 's/ $//')
        if [ "$wr" = no ] && [ -n "$have" ]; then why="refused build left files: $have"; fi
        if [ "$wr" = yes ] && [ "$have" != "$files" ]; then why="expected files '$files' got '$have'"; fi
    fi
    if [ -z "$why" ]; then pass "file.$name"; else fail "file.$name [$cite]" "$why"; fi
}
fb no_grant_writes_nothing "cli§1.1.1¶4 'leaves no file of any target written'" 1 'code-c' no - d27/rxt/two_targets.rxt
fb grant_every_target "cli§1.22¶1 'The grant applies to every compile in the invocation'" 0 - yes 'coded.c coded.h plain.c plain.h' --allow-code=c d27/rxt/two_targets.rxt
fb code_header_needs_grant "rxt§1.1 code-header 'segment or no segment'" 1 - no - d27/rxt/hdr_only.rxt
fb code_header_granted "rxt§1.1 code-header" 0 - yes 'plain.c plain.h' --allow-code=c d27/rxt/hdr_only.rxt
fb config_allow_code_refused "rxt§1.1¶2 (refused at parse)" 1 - no - d27/rxt/config_allow.rxt
fb config_allow_code_refused_granted "rxt§1.1¶2;§11.9¶8 (a file cannot grant; refused at parse)" 1 - no - --allow-code=c d27/rxt/config_allow.rxt
fb config_code_header_refused "rxt§1.1¶2 (--code-header refused at parse)" 1 - no - --allow-code=c d27/rxt/config_hdr.rxt
fb features_code_c_refused "§11.9¶8 'a features text naming it is refused wherever it arrives from'" 1 'code-c' no - --allow-code=c d27/rxt/features_code.rxt
fb lib_code_refused "§11.9¶8;cli§1.22¶1 'Code in a definition read from another .rxt file (lib ...) is refused even with the grant'" 1 'embedded code' no - --allow-code=c d27/rxt/lib_user.rxt
fb lib_code_refused_delivering "§11.9¶8 (lib definition through a delivering call)" 1 'embedded code' no - --allow-code=c d27/rxt/deliver_lib.rxt
# the same definition LOCAL is still refused, by §11.1¶1 (a delivering call is a call)
fb local_def_delivering_refused "§11.1¶1 (a site in a group a call reaches; 'a lib definition')" 1 'subroutine call' no - --allow-code=c d27/rxt/deliver_local.rxt
# An included fragment's block is not a definition a target can name (pcrec
# answers "no definition"), so this refusal holds for a reason other than the
# code rule; REPORT.md lists the include clause as untestable from the CLI.
fb include_code_refused "§11.9¶8;cli§1.22¶1 '(... include) is refused even with the grant'" 1 - no - --allow-code=c d27/rxt/inc_entry.rxt
fb cli_code_header_with_file "cli§1.22¶2 'It does not combine with a file operand'" 1 - no - --allow-code=c --code-header c:d27a.h d27/rxt/two_targets.rxt
fb hdr_unknown_lang_refused "rxt§1.1 code-header '<lang> a code language (c)'" 1 - no - --allow-code=c d27/rxt/hdr_unknown_lang.rxt
fb hdr_nonascii_refused "rxt§1.1 code-header 'printable ASCII'" 1 - no - --allow-code=c d27/rxt/hdr_nonascii.rxt
fb hdr_backslash_refused "rxt§1.1 code-header 'no backslash'" 1 - no - --allow-code=c d27/rxt/hdr_backslash.rxt
fb refused_char_in_file "§11.9¶3 (file operand)" 1 'U\+200B' no - --allow-code=c d27/rxt/ref_in_file.rxt
rawcheck file.hdr_nonascii_refused_no_raw_bytes "$W/fb/hdr_nonascii_refused/stderr"
# -o - with a refused target: nothing on stdout (§11.9¶8 'no artifact is written')
dir=$W/fb/stdout_refused
mkdir -p "$dir"
(cd "$CELL" && $T "$PCREC" --target coded -o - d27/rxt/two_targets.rxt >"$dir/stdout" 2>"$dir/stderr")
r=$?
if [ "$r" = 1 ] && [ ! -s "$dir/stdout" ]; then pass "file.stdout_refused_writes_nothing"; else
    fail "file.stdout_refused_writes_nothing [§11.9¶8;cli§1.1.1¶4]" "exit $r, stdout $(wc -c <"$dir/stdout") bytes"
fi
fb hdr_code_file_ok "rxt§1.1 code-header" 0 - yes 'rx.c rx.h' --allow-code=c d27/rxt/hdr_code.rxt
dir=$W/fb/hdr_code_file_ok/out
if [ -s "$dir/rx.c" ]; then
    n_a=$(grep -c '^#include "d27a.h"' "$dir/rx.c")
    [ "$n_a" = 1 ] && pass "file.hdr_repeated_once" || fail "file.hdr_repeated_once [rxt§1.1 'a repeated text once']" "expected 1 got $n_a"
    la=$(grep -n '^#include "d27a.h"' "$dir/rx.c" | head -1 | cut -d: -f1)
    lb=$(grep -n '^#include "d27b.h"' "$dir/rx.c" | head -1 | cut -d: -f1)
    if [ -n "$la" ] && [ -n "$lb" ] && [ "$la" -lt "$lb" ]; then pass "file.hdr_in_order"; else
        fail "file.hdr_in_order [rxt§1.1 'in the order written']" "d27a=$la d27b=$lb"
    fi
    if grep -Eq '^#include "d27' "$dir/rx.h"; then fail "file.hdr_only_in_c [§11.9¶7]" "the .h #includes a code-header"; else pass "file.hdr_only_in_c"; fi
    if $T "$CC" "${GCCF[@]}" -I "$D27/hdr" -DGEN_C="\"$dir/rx.c\"" -o "$dir/../bin" "$D27/driver_match.c" 2>"$dir/../cc.err"; then
        printf 'ab' >"$dir/../subj"
        r=$($T "$dir/../bin" "$dir/../subj")
        [ "$r" = "M 0 2" ] && pass "file.hdr_build_runs" || fail "file.hdr_build_runs [§11.9¶7]" "expected 'M 0 2' got '$r'"
    else
        fail "file.hdr_build_runs [§11.9¶7]" "$(oneline "$dir/../cc.err")"
    fi
    if grep -q '^#line [0-9][0-9]* "d27/rxt/hdr_code.rxt"' "$dir/rx.c"; then pass "file.line_names_operand"; else
        fail "file.line_names_operand [§11.9¶4]" "no '#line N \"d27/rxt/hdr_code.rxt\"'"
    fi
fi

# ------------------------------------------------------------------
# 9. --emit-main with code builds and runs (cli §1.10¶1-¶2)
# ------------------------------------------------------------------
dir=$W/misc/emit_main
mkdir -p "$dir"
if $T "$PCREC" --allow-code=c --emit-main -o "$dir/em.c" --pattern 'a(?C`c: return RX_POS == 1 ? RX_PASS : RX_FAIL;`)b' 2>"$dir/err" &&
    $T "$CC" -std=gnu11 -O1 -o "$dir/em" "$dir/em.c" 2>>"$dir/err"; then
    $T "$dir/em" ab >/dev/null 2>&1
    r1=$?
    $T "$dir/em" ac >/dev/null 2>&1
    r2=$?
    [ "$r1" = 0 ] && pass "emit_main.match_exit_0" || fail "emit_main.match_exit_0 [cli§1.10¶1]" "expected 0 got $r1"
    [ "$r2" = 1 ] && pass "emit_main.nomatch_exit_1" || fail "emit_main.nomatch_exit_1 [cli§1.10¶1]" "expected 1 got $r2"
else
    fail "emit_main.build [cli§1.10¶2]" "$(oneline "$dir/err")"
fi

# ------------------------------------------------------------------
# 10. a site no match can reach builds under -Werror in the SPLIT form too
#     (§11.2¶1a), with the .c compiled on its own
# ------------------------------------------------------------------
dir=$W/misc/unreach_split
mkdir -p "$dir"
if $T "$PCREC" --allow-code=c -o "$dir/a.c" --pattern '(?:(?C`c: return RX_PASS;`)){0}a' 2>"$dir/err" &&
    $T "$CC" "${GCCF[@]}" -c -o "$dir/a.o" "$dir/a.c" 2>>"$dir/err"; then
    pass "werror.unreachable_split_form"
else
    fail "werror.unreachable_split_form [§11.2¶1a]" "$(oneline "$dir/err")"
fi

echo "d27: $npass passed, $nfail failed"
