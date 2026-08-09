#!/usr/bin/env bash
# tests/harness/run.sh — .rxt test runner for pcrec.
#
# Usage: bash tests/harness/run.sh [file-or-dir ...]
#   With no arguments, runs every *.rxt under <repo-root>/tests/.
#   Arguments may be individual .rxt files or directories (searched
#   recursively for *.rxt).
#
# Env vars:
#   PCREC      path to the pcrec binary   (default: <repo-root>/build/pcrec)
#   CC         C compiler                 (default: gcc)
#   GENCFLAGS  flags for compiling generated code
#              (default: -O1 -std=gnu11 -Wall -Wextra -Werror)
#   KEEP=1     keep the temp working directory instead of deleting it
#   VERBOSE=1  print a line for every passing case, not just failures
#
# See docs/testing.md for the .rxt format and driver protocol.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
KEEP="${KEEP:-0}"
VERBOSE="${VERBOSE:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then
        echo "run.sh: KEEP=1, temp dir preserved: $WORKDIR" >&2
    else
        rm -rf "$WORKDIR"
    fi
}
trap cleanup EXIT

# ---- collect .rxt files -------------------------------------------------

files=()
if [ $# -eq 0 ]; then
    while IFS= read -r f; do files+=("$f"); done \
        < <(find "$ROOT_DIR/tests" -name '*.rxt' | sort)
else
    for arg in "$@"; do
        if [ -d "$arg" ]; then
            while IFS= read -r f; do files+=("$f"); done \
                < <(find "$arg" -name '*.rxt' | sort)
        else
            files+=("$arg")
        fi
    done
fi

# ---- result tracking ------------------------------------------------------

total_pass=0
total_fail=0
declare -A file_fail_count=()
compile_fail_set=()   # distinct "file:line" pattern-compile failures
block_counter=0

contains_fail() {
    local needle="$1" x
    for x in "${compile_fail_set[@]}"; do
        [ "$x" = "$needle" ] && return 0
    done
    return 1
}

record_fail() {
    # record_fail <file> <line> <message...>
    local f="$1" ln="$2"
    shift 2
    echo "$f:$ln: $*" >&2
    file_fail_count["$f"]=$(( ${file_fail_count["$f"]:-0} + 1 ))
    total_fail=$(( total_fail + 1 ))
}

record_pass() {
    total_pass=$(( total_pass + 1 ))
}

# Compile and run the current pattern block (globals cur_file, cur_pattern,
# cur_pattern_line, cur_is_perr) against its accumulated cases (parallel
# arrays case_kind/case_line/case_subject/case_start/case_end).
flush_block() {
    block_counter=$((block_counter + 1))
    local bdir="$WORKDIR/b$block_counter"
    mkdir -p "$bdir"

    local pcrec_err
    pcrec_err="$(timeout 60 "$PCREC" -p rx -o "$bdir/gen.c" -- "$cur_pattern" 2>&1 >/dev/null)"
    local pcrec_rc=$?

    if [ "$cur_is_perr" = "1" ]; then
        # exit 1 = clean rejection with a diagnostic; anything else (0 =
        # accepted, >=124 = timeout, 139 = crash, ...) is a failure — a crash
        # must never satisfy a perr expectation (R1 review P-C1)
        if [ $pcrec_rc -eq 1 ]; then
            [ "$VERBOSE" = "1" ] && echo "PASS $cur_file:$cur_pattern_line: perr '$cur_pattern'"
            record_pass
        elif [ $pcrec_rc -eq 0 ]; then
            record_fail "$cur_file" "$cur_pattern_line" \
                "expected pattern to fail to compile (perr) but pcrec succeeded: '$cur_pattern'"
        else
            record_fail "$cur_file" "$cur_pattern_line" \
                "pcrec CRASHED or timed out (exit $pcrec_rc) instead of cleanly rejecting: '$cur_pattern'"
        fi
        return 0
    fi

    if [ $pcrec_rc -ne 0 ]; then
        if [ $pcrec_rc -ge 124 ]; then
            echo "$cur_file:$cur_pattern_line: HARNESS FAILURE: pcrec crashed or timed out (exit $pcrec_rc) on pattern '$cur_pattern'" >&2
        fi
        local key="$cur_file:$cur_pattern_line"
        contains_fail "$key" || compile_fail_set+=("$key")
        local i
        for i in "${!case_kind[@]}"; do
            record_fail "$cur_file" "${case_line[$i]}" \
                "pattern '$cur_pattern' failed to compile: $pcrec_err"
        done
        return 0
    fi

    if [ ! -f "$bdir/gen.c" ] || [ ! -f "$bdir/gen.h" ]; then
        local i
        for i in "${!case_kind[@]}"; do
            record_fail "$cur_file" "${case_line[$i]}" \
                "pcrec exited 0 but did not produce gen.c/gen.h for pattern '$cur_pattern'"
        done
        return 0
    fi

    local build_log
    build_log="$(timeout 120 "$CC" $GENCFLAGS -I"$bdir" -o "$bdir/t" "$SCRIPT_DIR/driver.c" "$bdir/gen.c" 2>&1)"
    if [ $? -ne 0 ]; then
        echo "$cur_file:$cur_pattern_line: HARNESS FAILURE: $CC failed to compile generated code for pattern '$cur_pattern'" >&2
        echo "$build_log" >&2
        local i
        for i in "${!case_kind[@]}"; do
            record_fail "$cur_file" "${case_line[$i]}" "compile failure (see above)"
        done
        return 0
    fi

    local i
    for i in "${!case_kind[@]}"; do
        local kind="${case_kind[$i]}" line="${case_line[$i]}" subj="${case_subject[$i]}"
        local out expect trc
        out="$(timeout 10 "$bdir/t" "$subj")"
        trc=$?
        if [ $trc -eq 124 ]; then
            record_fail "$cur_file" "$line" \
                "test binary TIMED OUT (>10s) for pattern '$cur_pattern' subject \"$subj\""
            continue
        elif [ $trc -ge 126 ]; then
            record_fail "$cur_file" "$line" \
                "test binary crashed (exit $trc) for pattern '$cur_pattern' subject \"$subj\""
            continue
        fi
        if [ "$kind" = "m" ]; then
            expect="match ${case_start[$i]} ${case_end[$i]}"
        else
            expect="nomatch"
        fi
        if [ "$out" = "$expect" ]; then
            [ "$VERBOSE" = "1" ] && echo "PASS $cur_file:$line: '$cur_pattern' subject=\"$subj\""
            record_pass
        else
            record_fail "$cur_file" "$line" \
                "expected '$expect' got '$out' for pattern '$cur_pattern' subject \"$subj\""
        fi
    done
}

# ---- parse and run each file ----------------------------------------------

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "run.sh: file not found: $file" >&2
        continue
    fi
    cur_file="$file"
    cur_pattern=""
    cur_pattern_line=0
    cur_is_perr=0
    case_kind=(); case_line=(); case_subject=(); case_start=(); case_end=()
    have_block=0
    blocks_in_file=0

    lineno=0
    while IFS= read -r line || [ -n "$line" ]; do
        lineno=$((lineno + 1))
        [[ "$line" =~ ^[[:space:]]*$ ]] && continue
        [[ "$line" =~ ^# ]] && continue

        if [[ "$line" =~ ^pattern\ (.*)$ ]]; then
            [ "$have_block" = "1" ] && flush_block
            blocks_in_file=$((blocks_in_file + 1))
            cur_pattern="${BASH_REMATCH[1]}"
            cur_pattern_line=$lineno
            cur_is_perr=0
            case_kind=(); case_line=(); case_subject=(); case_start=(); case_end=()
            have_block=1
        elif [[ "$line" =~ ^perr[[:space:]]*$ ]]; then
            cur_is_perr=1
        elif [[ "$line" =~ ^m[[:space:]]+\"(.*)\"[[:space:]]+([0-9]+)[[:space:]]+([0-9]+)[[:space:]]*$ ]]; then
            case_kind+=("m")
            case_line+=("$lineno")
            case_subject+=("${BASH_REMATCH[1]}")
            case_start+=("${BASH_REMATCH[2]}")
            case_end+=("${BASH_REMATCH[3]}")
        elif [[ "$line" =~ ^n[[:space:]]+\"(.*)\"[[:space:]]*$ ]]; then
            case_kind+=("n")
            case_line+=("$lineno")
            case_subject+=("${BASH_REMATCH[1]}")
            case_start+=("")
            case_end+=("")
        else
            # unparseable non-blank/non-comment lines are hard errors: a
            # corrupted corpus must not silently degrade to zero coverage
            # (R1 review P-C2)
            record_fail "$file" "$lineno" "unparseable .rxt line (hard error): $line"
        fi
    done < "$file"

    [ "$have_block" = "1" ] && flush_block
    if [ "$blocks_in_file" -eq 0 ]; then
        record_fail "$file" 0 "no pattern blocks parsed from file (P-C2 floor)"
    fi
done

# ---- summary ----------------------------------------------------------

echo
echo "== Summary =="
echo "cases passed: $total_pass"
echo "cases failed: $total_fail"
if [ ${#file_fail_count[@]} -gt 0 ]; then
    echo "failures by file:"
    for f in "${!file_fail_count[@]}"; do
        echo "  $f: ${file_fail_count[$f]}"
    done | sort
fi
echo "pattern-compile failures (distinct): ${#compile_fail_set[@]}"

if [ $((total_pass + total_fail)) -eq 0 ]; then
    echo "run.sh: NO CASES RUN — corpus missing or fully unparseable" >&2
    exit 1
fi
[ "$total_fail" -eq 0 ] && exit 0
exit 1
