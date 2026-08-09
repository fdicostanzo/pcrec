#!/usr/bin/env bash
# tests/cli/run_cli_tests.sh — CLI surface + library-API regression tests.
#
# Standalone (not wired into the Makefile — the main build integrates it
# separately). Covers the CLI surface beyond the plain `-p rx -o tmp/gen.c`
# path the .rxt harness exercises: -o -, --emit-main, prefix boundary
# validation, subdirectory output, `--` end-of-options, missing-value and
# unknown-option diagnostics, and a direct library-API (pcrec_compile /
# pcrec_output_free) NULL-argument / double-free smoke test.
#
# docs/reviews/2026-08-09-m1.md P-M1; plan M2.4.
#
# Usage: bash tests/cli/run_cli_tests.sh
#
# Env vars:
#   PCREC   path to the pcrec binary    (default: <repo-root>/build/pcrec)
#   CC      C compiler                  (default: gcc)
#   LIBA    path to libpcrec.a          (default: <repo-root>/build/libpcrec.a)
#   LIBDIR  dir containing pcrec.h      (default: <repo-root>/lib)
#   KEEP=1  keep the temp working directory instead of deleting it on exit

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
LIBA="${LIBA:-$ROOT_DIR/build/libpcrec.a}"
LIBDIR="${LIBDIR:-$ROOT_DIR/lib}"
KEEP="${KEEP:-0}"
CFLAGS="-O1 -std=gnu11 -Wall -Wextra -Werror"

if [ ! -x "$PCREC" ]; then
    echo "run_cli_tests.sh: pcrec binary not found or not executable: $PCREC" >&2
    echo "run_cli_tests.sh: build it first (e.g. 'make') or set \$PCREC" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then
        echo "run_cli_tests.sh: KEEP=1, temp dir preserved: $WORKDIR" >&2
    else
        rm -rf "$WORKDIR"
    fi
}
trap cleanup EXIT

total_pass=0
total_fail=0

pass() {
    total_pass=$((total_pass + 1))
    echo "PASS: $1"
}

fail() {
    total_fail=$((total_fail + 1))
    echo "FAIL: $1" >&2
    shift
    for detail in "$@"; do
        echo "      $detail" >&2
    done
}

# assert_eq <case-name> <expected> <actual> [extra-detail...]
assert_eq() {
    local name="$1" expected="$2" actual="$3"
    shift 3
    if [ "$expected" = "$actual" ]; then
        pass "$name"
    else
        fail "$name" "expected: $expected" "actual:   $actual" "$@"
    fi
}

# assert_contains <case-name> <haystack> <needle> [extra-detail...]
assert_contains() {
    local name="$1" haystack="$2" needle="$3"
    shift 3
    case "$haystack" in
        *"$needle"*) pass "$name" ;;
        *) fail "$name" "expected output to contain: $needle" "actual output: $haystack" "$@" ;;
    esac
}

# ---------------------------------------------------------------------------
# 1. -o - prints self-contained C that compiles standalone (no header file).
# ---------------------------------------------------------------------------
case1() {
    local d="$WORKDIR/case1"
    mkdir -p "$d"
    local out rc
    out="$("$PCREC" -o - -- 'abc' 2>"$d/stderr.txt" 1>"$d/gen.c")"
    rc=$?
    assert_eq "case1: -o - exits 0" "0" "$rc" "stderr: $(cat "$d/stderr.txt")"
    if [ -s "$d/gen.c" ] && ! grep -q '#include "' "$d/gen.c"; then
        pass "case1: -o - produces no header #include (self-contained)"
    else
        fail "case1: -o - produces no header #include (self-contained)" \
            "gen.c: $(head -c 200 "$d/gen.c" 2>/dev/null)"
    fi

    cat > "$d/mymain.c" <<'EOF'
#include <stddef.h>
#include <stdio.h>
#include <string.h>
typedef struct { size_t start, end; } rx_span;
int rx_search(const unsigned char *s, size_t n, size_t startpos, rx_span *m);
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    rx_span m;
    if (rx_search((const unsigned char *)argv[1], strlen(argv[1]), 0, &m)) {
        printf("match %zu %zu\n", m.start, m.end);
    } else {
        printf("nomatch\n");
    }
    return 0;
}
EOF
    local build_log
    build_log="$("$CC" $CFLAGS -o "$d/t" "$d/gen.c" "$d/mymain.c" 2>&1)"
    if [ $? -eq 0 ]; then
        pass "case1: gcc compiles the -o - output standalone with an appended main"
    else
        fail "case1: gcc compiles the -o - output standalone with an appended main" "$build_log"
        return
    fi
    local runout
    runout="$("$d/t" xxabcxx)"
    assert_eq "case1: standalone binary matches 'abc' in 'xxabcxx'" "match 2 5" "$runout"
    runout="$("$d/t" zzz)"
    assert_eq "case1: standalone binary reports nomatch for 'zzz'" "nomatch" "$runout"
}

# ---------------------------------------------------------------------------
# 2. --emit-main produces a runnable binary with match/nomatch output.
# ---------------------------------------------------------------------------
case2() {
    local d="$WORKDIR/case2"
    mkdir -p "$d"
    local rc
    "$PCREC" --emit-main -o - -- 'abc' > "$d/gen.c" 2>"$d/stderr.txt"
    rc=$?
    assert_eq "case2: --emit-main -o - exits 0" "0" "$rc" "stderr: $(cat "$d/stderr.txt")"

    local build_log
    build_log="$("$CC" $CFLAGS -o "$d/t" "$d/gen.c" 2>&1)"
    if [ $? -eq 0 ]; then
        pass "case2: --emit-main output compiles into a runnable binary"
    else
        fail "case2: --emit-main output compiles into a runnable binary" "$build_log"
        return
    fi

    local runout runrc
    runout="$("$d/t" xxabcxx)"; runrc=$?
    assert_eq "case2: emitted main prints 'match START END' for a match" "match 2 5" "$runout"
    assert_eq "case2: emitted main exits 0 on match" "0" "$runrc"

    runout="$("$d/t" zzz)"; runrc=$?
    assert_eq "case2: emitted main prints 'nomatch' for no match" "nomatch" "$runout"
    assert_eq "case2: emitted main exits 1 on no match" "1" "$runrc"
}

# ---------------------------------------------------------------------------
# 3. Prefix boundary validation (60/61 chars, leading digit, empty).
# ---------------------------------------------------------------------------
case3() {
    local d="$WORKDIR/case3"
    mkdir -p "$d"
    local p60 p61
    p60="$(printf 'a%.0s' $(seq 1 60))"
    p61="$(printf 'a%.0s' $(seq 1 61))"

    local rc build_log
    "$PCREC" -p "$p60" --emit-main -o - -- 'a' >"$d/g60.c" 2>"$d/e1.txt"
    rc=$?
    assert_eq "case3: 60-char prefix accepted (pcrec exit 0)" "0" "$rc" "stderr: $(cat "$d/e1.txt")"
    build_log="$("$CC" $CFLAGS -o "$d/t60" "$d/g60.c" 2>&1)"
    if [ $? -eq 0 ]; then
        pass "case3: 60-char-prefix generated code compiles"
    else
        fail "case3: 60-char-prefix generated code compiles" "$build_log"
    fi

    "$PCREC" -p "$p61" -o "$d/g61.c" -- 'a' 2>"$d/e2.txt"
    rc=$?
    assert_eq "case3: 61-char prefix rejected exit 1" "1" "$rc"
    assert_contains "case3: 61-char prefix rejection has a diagnostic" \
        "$(cat "$d/e2.txt")" "prefix"

    "$PCREC" -p "1abc" -o "$d/glead.c" -- 'a' 2>"$d/e3.txt"
    rc=$?
    assert_eq "case3: leading-digit prefix rejected exit 1" "1" "$rc"
    assert_contains "case3: leading-digit prefix rejection has a diagnostic" \
        "$(cat "$d/e3.txt")" "prefix"

    "$PCREC" -p "" -o "$d/gempty.c" -- 'a' 2>"$d/e4.txt"
    rc=$?
    assert_eq "case3: empty prefix rejected exit 1" "1" "$rc"
    assert_contains "case3: empty prefix rejection has a diagnostic" \
        "$(cat "$d/e4.txt")" "prefix"
}

# ---------------------------------------------------------------------------
# 4. -o subdir/out.c writes both files in subdir and they compile with
#    -I subdir (reusing the shared harness driver, which assumes the
#    default "rx" prefix and includes "gen.h").
# ---------------------------------------------------------------------------
case4() {
    local d="$WORKDIR/case4"
    local sub="$d/subdir"
    mkdir -p "$sub"
    local rc
    "$PCREC" -o "$sub/gen.c" -- 'abc' 2>"$d/stderr.txt"
    rc=$?
    assert_eq "case4: -o subdir/gen.c exits 0" "0" "$rc" "stderr: $(cat "$d/stderr.txt")"

    if [ -f "$sub/gen.c" ] && [ -f "$sub/gen.h" ]; then
        pass "case4: both gen.c and gen.h written in subdir"
    else
        fail "case4: both gen.c and gen.h written in subdir" \
            "ls $sub: $(ls "$sub" 2>&1)"
        return
    fi

    local build_log
    build_log="$("$CC" $CFLAGS -I"$sub" -o "$d/t" "$ROOT_DIR/tests/harness/driver.c" "$sub/gen.c" 2>&1)"
    if [ $? -eq 0 ]; then
        pass "case4: subdir output compiles with -I subdir"
    else
        fail "case4: subdir output compiles with -I subdir" "$build_log"
        return
    fi
    local runout
    runout="$("$d/t" 'xxabcxx')"
    assert_eq "case4: subdir-built binary matches correctly" "match 2 5" "$runout"
}

# ---------------------------------------------------------------------------
# 5. `--` allows a pattern starting with '-'; missing -o/-p/-e values give
#    "missing value" errors, exit 1.
# ---------------------------------------------------------------------------
case5() {
    local d="$WORKDIR/case5"
    mkdir -p "$d"
    local rc

    "$PCREC" --emit-main -o - -- '-foo' > "$d/gen.c" 2>"$d/stderr.txt"
    rc=$?
    assert_eq "case5: -- allows a pattern starting with '-' (exit 0)" "0" "$rc" \
        "stderr: $(cat "$d/stderr.txt")"
    local build_log
    build_log="$("$CC" $CFLAGS -o "$d/t" "$d/gen.c" 2>&1)"
    if [ $? -eq 0 ]; then
        pass "case5: '-foo' pattern generated code compiles"
        local runout
        runout="$("$d/t" 'xx-fooxx')"
        assert_eq "case5: '-foo' literal matches its own text" "match 2 6" "$runout"
    else
        fail "case5: '-foo' pattern generated code compiles" "$build_log"
    fi

    "$PCREC" -o 2>"$d/e_o.txt"; rc=$?
    assert_eq "case5: missing -o value exits 1" "1" "$rc"
    assert_contains "case5: missing -o value diagnoses 'missing value'" \
        "$(cat "$d/e_o.txt")" "missing value"

    "$PCREC" -p 2>"$d/e_p.txt"; rc=$?
    assert_eq "case5: missing -p value exits 1" "1" "$rc"
    assert_contains "case5: missing -p value diagnoses 'missing value'" \
        "$(cat "$d/e_p.txt")" "missing value"

    "$PCREC" -e 2>"$d/e_e.txt"; rc=$?
    assert_eq "case5: missing -e value exits 1" "1" "$rc"
    assert_contains "case5: missing -e value diagnoses 'missing value'" \
        "$(cat "$d/e_e.txt")" "missing value"
}

# ---------------------------------------------------------------------------
# 6. Error cases: no pattern, two patterns, unknown option -> exit 1 with a
#    usage/diagnostic message on stderr.
# ---------------------------------------------------------------------------
case6() {
    local d="$WORKDIR/case6"
    mkdir -p "$d"
    local rc

    "$PCREC" -o "$d/x.c" 2>"$d/e_nopat.txt"; rc=$?
    assert_eq "case6: no pattern exits 1" "1" "$rc"
    assert_contains "case6: no pattern gives a diagnostic on stderr" \
        "$(cat "$d/e_nopat.txt")" "pattern"

    "$PCREC" -o "$d/y.c" -- 'a' 'b' 2>"$d/e_twopat.txt"; rc=$?
    assert_eq "case6: two patterns exits 1" "1" "$rc"
    assert_contains "case6: two patterns gives a diagnostic on stderr" \
        "$(cat "$d/e_twopat.txt")" "one pattern"

    "$PCREC" -z -o "$d/z.c" -- 'a' 2>"$d/e_unk.txt"; rc=$?
    assert_eq "case6: unknown option exits 1" "1" "$rc"
    assert_contains "case6: unknown option gives a diagnostic on stderr" \
        "$(cat "$d/e_unk.txt")" "unknown option"
}

# ---------------------------------------------------------------------------
# 7. Library API smoke test: NULL pattern, NULL out, valid pattern + NULL
#    err, then pcrec_output_free called twice — must not crash, correct
#    return codes.
# ---------------------------------------------------------------------------
case7() {
    local d="$WORKDIR/case7"
    mkdir -p "$d"

    if [ ! -f "$LIBA" ]; then
        fail "case7: libpcrec.a exists at $LIBA" "build it first (e.g. 'make')"
        return
    fi
    if [ ! -f "$LIBDIR/pcrec.h" ]; then
        fail "case7: pcrec.h exists at $LIBDIR/pcrec.h"
        return
    fi

    cat > "$d/smoke.c" <<'EOF'
#include <stdio.h>
#include <string.h>
#include "pcrec.h"

int main(void) {
    pcrec_options opt;
    pcrec_default_options(&opt);
    pcrec_output out;
    pcrec_error err;

    /* NULL pattern must fail cleanly, not crash. */
    memset(&out, 0, sizeof(out));
    int rc1 = pcrec_compile(NULL, &opt, &out, &err);
    if (rc1 == 0) { fprintf(stderr, "FAIL: NULL pattern returned 0\n"); return 1; }

    /* NULL out must fail cleanly. */
    int rc2 = pcrec_compile("abc", &opt, NULL, &err);
    if (rc2 == 0) { fprintf(stderr, "FAIL: NULL out returned 0\n"); return 1; }

    /* Valid pattern with NULL err must succeed. */
    memset(&out, 0, sizeof(out));
    int rc3 = pcrec_compile("abc", &opt, &out, NULL);
    if (rc3 != 0) { fprintf(stderr, "FAIL: valid pattern with NULL err failed (rc=%d)\n", rc3); return 1; }
    if (!out.c_src) { fprintf(stderr, "FAIL: valid compile produced NULL c_src\n"); return 1; }

    /* Double-free must not crash. */
    pcrec_output_free(&out);
    pcrec_output_free(&out);

    printf("smoke OK\n");
    return 0;
}
EOF
    local build_log
    build_log="$("$CC" $CFLAGS -I"$LIBDIR" -o "$d/smoke" "$d/smoke.c" "$LIBA" 2>&1)"
    if [ $? -eq 0 ]; then
        pass "case7: library-API smoke test compiles against pcrec.h + libpcrec.a"
    else
        fail "case7: library-API smoke test compiles against pcrec.h + libpcrec.a" "$build_log"
        return
    fi

    local runout runrc
    runout="$(timeout 10 "$d/smoke" 2>"$d/smoke_stderr.txt")"
    runrc=$?
    if [ $runrc -ge 124 ]; then
        fail "case7: library-API smoke test does not crash or hang" \
            "exit code: $runrc (>=124 = timeout/crash)" "stderr: $(cat "$d/smoke_stderr.txt")"
    else
        assert_eq "case7: library-API smoke test exits 0" "0" "$runrc" \
            "stderr: $(cat "$d/smoke_stderr.txt")"
        assert_eq "case7: library-API smoke test prints 'smoke OK'" "smoke OK" "$runout"
    fi
}

# ---------------------------------------------------------------------------

case1
case2
case3
case4
case5
case6
case7

echo
echo "== Summary =="
echo "cases passed: $total_pass"
echo "cases failed: $total_fail"

if [ $((total_pass + total_fail)) -eq 0 ]; then
    echo "run_cli_tests.sh: NO CASES RUN" >&2
    exit 1
fi
[ "$total_fail" -eq 0 ] && exit 0
exit 1
