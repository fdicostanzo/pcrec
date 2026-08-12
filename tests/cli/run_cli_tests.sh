#!/usr/bin/env bash
# tests/cli/run_cli_tests.sh — CLI surface + library-API regression tests.
#
# Part of `make test` since M2. Covers the CLI surface beyond the plain `-p rx -o tmp/gen.c`
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

# ---------------------------------------------------------------------------
# 8. Compiling must not need a big C stack (R3 critic finding F3).
#
# pcrec is a LIBRARY, so a caller's thread stack is not ours to assume: musl's
# default pthread stack is 128 KB and embedders routinely use 256-512 KB. The
# M2.8 trie regressed this badly and silently — trie_build recursed once per
# duplicate branch, so `a|a|...|a` with 9000 branches needed >1 MB, where the
# pre-trie construction handled the same pattern in 128 KB because ITS deep
# recursion sat in tail position and gcc turned it into a jump. Nothing in the
# suite noticed: stack depth is invisible to every correctness test.
#
# The assertion is 512 KB rather than the default 8 MB, because the point is to
# fail on a REGRESSION; a limit only just above today's requirement would flake.
# ---------------------------------------------------------------------------
case8() {
    local pat out rc
    if ! command -v python3 >/dev/null 2>&1; then
        echo "case8: SKIP (needs python3 to build the pattern)" >&2
        return 0
    fi
    pat="$(python3 -c 'print("|".join(["a"]*9000))')"
    out="$(bash -c "ulimit -s 512; exec \"$PCREC\" -p rx -o \"$WORKDIR/deep.c\" -- \"$pat\"" 2>&1)"
    rc=$?
    if [ $rc -ge 128 ]; then
        fail "case8: 9000-branch alternation within a 512 KB stack" \
             "pcrec died with signal $((rc - 128)) (trie_build recursion depth regression?)"
    elif [ $rc -ne 0 ]; then
        fail "case8: 9000-branch alternation within a 512 KB stack" \
             "pcrec exited $rc" "output: $out"
    else
        pass "case8: 9000-branch alternation compiles within a 512 KB stack"
    fi
}

# ---------------------------------------------------------------------------
# 9. -i (ASCII case-insensitive, OS-1/D23) end to end through the CLI, and the
#    library field behind it. The .rxt corpus covers the matching semantics;
#    what is CLI surface, and therefore this file's job, is that the flag is
#    accepted, reaches pcrec_options.caseless, composes with `--` and
#    --emit-main, and does not leak into a build that did not ask for it.
# ---------------------------------------------------------------------------
case9() {
    local d="$WORKDIR/case9"
    mkdir -p "$d"
    local rc build_log runout

    "$PCREC" -i --emit-main -o - -- 'aBc' > "$d/gen.c" 2>"$d/stderr.txt"
    rc=$?
    assert_eq "case9: -i exits 0" "0" "$rc" "stderr: $(cat "$d/stderr.txt")"

    build_log="$("$CC" $CFLAGS -o "$d/t" "$d/gen.c" 2>&1)"
    if [ $? -ne 0 ]; then
        fail "case9: -i output compiles" "$build_log"
        return
    fi
    pass "case9: -i output compiles warning-clean"

    runout="$("$d/t" xxABCxx)"
    assert_eq "case9: -i 'aBc' matches 'ABC'" "match 2 5" "$runout"
    runout="$("$d/t" xxabcxx)"
    assert_eq "case9: -i 'aBc' still matches 'abc'" "match 2 5" "$runout"

    # ...and the same pattern WITHOUT -i must not: a compile option must not
    # leak into builds that did not request it
    "$PCREC" --emit-main -o - -- 'aBc' > "$d/gens.c" 2>/dev/null
    if "$CC" $CFLAGS -o "$d/ts" "$d/gens.c" 2>/dev/null; then
        runout="$("$d/ts" xxABCxx)"
        assert_eq "case9: without -i, 'aBc' does NOT match 'ABC'" "nomatch" "$runout"
    else
        fail "case9: case-sensitive control build" "compile failed"
    fi

    # -i is listed in --help (an undiscoverable flag is a half-shipped one)
    assert_contains "case9: --help documents -i" "$("$PCREC" --help)" "-i "

    # a pattern starting with '-' after `--` still parses as a pattern, not a flag
    "$PCREC" -i -o "$d/dash.c" -- '-i' 2>"$d/e_dash.txt"; rc=$?
    assert_eq "case9: -i composes with -- and a '-i'-looking pattern" "0" "$rc" \
        "stderr: $(cat "$d/e_dash.txt")"
}

# ---------------------------------------------------------------------------
# 10. The syntax queries (SR-3): --list-syntax, --explain, --flavour.
#
#     These are not a convenience feature — SR-4 makes tests/reject/ iterate
#     this dump and renders docs/pcre2_compliance.md from it, so the FORMAT is
#     an interface with consumers. The load-bearing assertion here is the field
#     count: the dump forbids tabs and newlines inside a field rather than
#     escaping them, and a note that acquired one would silently hand every
#     consumer a shifted column. Nothing else would notice.
# ---------------------------------------------------------------------------
case10() {
    local d="$WORKDIR/case10"
    mkdir -p "$d"
    local rc out nrows nbad

    out="$("$PCREC" --list-syntax 2>"$d/e.txt")"; rc=$?
    assert_eq "case10: --list-syntax exits 0" "0" "$rc" "stderr: $(cat "$d/e.txt")"
    assert_contains "case10: --list-syntax emits the column header" "$out" \
        "#kind	selector	syntax"

    # every non-comment row has exactly 15 tab-separated fields (12 until
    # MOD-0.1 appended `roadmap`, `quantifiable` and then `class_expect`,
    # 2026-08-11)
    printf '%s\n' "$out" > "$d/dump.tsv"
    nrows=$(grep -vc '^#' "$d/dump.tsv")
    nbad=$(awk -F'\t' '!/^#/ && NF != 15' "$d/dump.tsv" | wc -l)
    assert_eq "case10: every dump row has 15 fields (no tab leaked into one)" \
        "0" "$nbad" "rows: $nrows"
    if [ "$nrows" -ge 60 ]; then
        pass "case10: dump carries the registry's rows ($nrows)"
    else
        fail "case10: dump carries the registry's rows" "only $nrows rows"
    fi
    # a blank line would end the table early for a naive reader
    assert_eq "case10: dump has no blank lines" "0" "$(grep -c '^$' "$d/dump.tsv")"

    # --explain answers for one construct, and names the module it needs
    out="$("$PCREC" --explain '\v' 2>"$d/e2.txt")"; rc=$?
    assert_eq "case10: --explain exits 0" "0" "$rc" "stderr: $(cat "$d/e2.txt")"
    assert_contains "case10: --explain names the owning module" "$out" \
        "requires module 'classes'"
    assert_contains "case10: --explain carries the PCRE2 semantics" "$out" \
        "vertical whitespace"

    # One selector byte, two MODULES: both must be reported. This asserted the
    # compound module string "lookaround/named-groups" until Q2/SR-9 retired it —
    # `(?<` is now four rows (the `=` `!` `*` lookbehind tails and the named
    # group), so the byte's answer is exact per construct instead of a compound
    # name. The test's intent is unchanged and better served: ask for both
    # modules rather than for one string that happened to contain both.
    out="$("$PCREC" --explain '(?<')"
    assert_contains "case10: --explain reports (?< as lookaround" "$out" "'lookaround'"
    assert_contains "case10: --explain reports (?< as named-groups" "$out" "'named-groups'"
    # ...and the tails really are distinct rows, not one row printed twice
    assert_eq "case10: --explain '(?<' reports all four rows" "4" \
        "$(printf '%s\n' "$out" | grep -c "^  doorway")"

    # a base-tier construct has no row, and saying so is the correct answer
    "$PCREC" --explain 'a' >"$d/o3.txt" 2>"$d/e3.txt"; rc=$?
    assert_eq "case10: --explain on base syntax exits 1" "1" "$rc"
    assert_contains "case10: --explain on base syntax says why" \
        "$(cat "$d/e3.txt")" "no construct matches"

    # --flavour: exactly one exists, and a typo must not silently dump the lot
    "$PCREC" --list-syntax --flavour pcre2 >"$d/o4.txt" 2>&1; rc=$?
    assert_eq "case10: --flavour pcre2 exits 0" "0" "$rc"
    assert_eq "case10: --flavour pcre2 selects every row" \
        "$nrows" "$(grep -vc '^#' "$d/o4.txt")"
    "$PCREC" --list-syntax --flavour python-re >"$d/o5.txt" 2>"$d/e5.txt"; rc=$?
    assert_eq "case10: an unknown flavour exits 1" "1" "$rc"
    assert_contains "case10: an unknown flavour is named in the error" \
        "$(cat "$d/e5.txt")" "unknown flavour 'python-re'"

    # a query compiles nothing, so mixing it with a compile is an error rather
    # than a silently-ignored half of the command line
    "$PCREC" --list-syntax -o - -- 'abc' >/dev/null 2>"$d/e6.txt"; rc=$?
    assert_eq "case10: --list-syntax with -o and a pattern exits 1" "1" "$rc"
    assert_contains "case10: ...and says which flag conflicts" \
        "$(cat "$d/e6.txt")" "takes no pattern and no -o"
    "$PCREC" --list-syntax --explain '\v' >/dev/null 2>"$d/e7.txt"; rc=$?
    assert_eq "case10: --list-syntax with --explain exits 1" "1" "$rc"
    "$PCREC" --flavour pcre2 -o - -- 'abc' >/dev/null 2>"$d/e8.txt"; rc=$?
    assert_eq "case10: --flavour without a query exits 1" "1" "$rc"
    "$PCREC" --explain >/dev/null 2>"$d/e9.txt"; rc=$?
    assert_eq "case10: --explain with no value exits 1" "1" "$rc"
    assert_contains "case10: ...with a missing-value diagnostic" \
        "$(cat "$d/e9.txt")" "missing value for --explain"

    # --list-verbs (Q1). A separate dump because the fifty verb NAMES are not
    # RegRows and --list-syntax's format is frozen by SR-4's generated doc
    # section. Four columns, and the row count is asserted as a FLOOR with a
    # named row required: a count alone would be satisfied by any fifty rows.
    out="$("$PCREC" --list-verbs 2>"$d/ev.txt")"; rc=$?
    assert_eq "case10: --list-verbs exits 0" "0" "$rc" "stderr: $(cat "$d/ev.txt")"
    assert_contains "case10: --list-verbs emits the column header" "$out" \
        "#table	name	forms	unknown"
    nverbs="$(printf '%s\n' "$out" | grep -vc '^#')"
    if [ "$nverbs" -lt 40 ]; then
        fail "case10: --list-verbs printed $nverbs rows, floor 40 — the verb tables have shrunk"
    else
        pass "case10: --list-verbs printed $nverbs verb names (floor 40)"
    fi
    # Both tables must be present. A dump of one is how the case distinction
    # would silently disappear.
    assert_contains "case10: --list-verbs carries the upper table" "$out" \
        "upper	ACCEPT	"
    assert_contains "case10: --list-verbs carries the lower table" "$out" \
        "lower	script_run	"
    assert_contains "case10: --list-verbs records the start-of-pattern rule" "$out" \
        "start-of-pattern-only"
    # Every line must have exactly 6 tab-separated fields (4 until MOD-0.1
    # appended `roadmap` and then `quantifiable`): the format is an interface,
    # and a field containing a tab would corrupt it (case10's rule for
    # --list-syntax, applied to the second dump).
    badfields="$(printf '%s\n' "$out" | grep -v '^#' | awk -F'\t' 'NF != 6' | head -3)"
    if [ -n "$badfields" ]; then
        fail "case10: --list-verbs rows without exactly 6 fields" "$badfields"
    else
        pass "case10: every --list-verbs row has exactly 6 tab-separated fields"
    fi
    "$PCREC" --list-verbs --list-syntax >/dev/null 2>"$d/ev2.txt"; rc=$?
    assert_eq "case10: --list-verbs with --list-syntax exits 1" "1" "$rc"
    "$PCREC" --list-verbs -o - -- 'abc' >/dev/null 2>"$d/ev3.txt"; rc=$?
    assert_eq "case10: --list-verbs with -o and a pattern exits 1" "1" "$rc"

    # --count-groups (MOD-0.1, §18.1): the running capture count's external
    # channel — the surface tests/spec_mod0/check02 compares against libpcre2.
    # Expectations oracle-verified: python re agrees on every cell, and a
    # 300-pattern generated sweep at landing found zero disagreements.
    out="$("$PCREC" --count-groups -- '(a)(b)(c)' 2>"$d/ec1.txt")"; rc=$?
    assert_eq "case10: --count-groups counts sibling groups" "0" "$rc" \
        "stderr: $(cat "$d/ec1.txt")"
    assert_eq "case10: ...and prints 3 for (a)(b)(c)" "3" "$out"
    assert_eq "case10: --count-groups counts nested groups" \
        "2" "$("$PCREC" --count-groups -- '(a(b))')"
    assert_eq "case10: --count-groups does not count (?:...)" \
        "0" "$("$PCREC" --count-groups -- '(?:a)')"
    assert_eq "case10: --count-groups on a groupless pattern is 0" \
        "0" "$("$PCREC" --count-groups -- 'a|b')"
    # a refused construct refuses here too, with the compile diagnostic —
    # leftmost refusal, no count for a pattern pcrec does not fully know
    "$PCREC" --count-groups -- '(?<n>a)' >/dev/null 2>"$d/ec2.txt"; rc=$?
    assert_eq "case10: --count-groups refuses what pcrec refuses" "1" "$rc"
    assert_contains "case10: ...with the construct's own diagnostic" \
        "$(cat "$d/ec2.txt")" "requires module 'named-groups'"
    "$PCREC" --count-groups -o - -- 'a' >/dev/null 2>"$d/ec3.txt"; rc=$?
    assert_eq "case10: --count-groups with -o exits 1" "1" "$rc"
    "$PCREC" --count-groups >/dev/null 2>"$d/ec4.txt"; rc=$?
    assert_eq "case10: --count-groups without a pattern exits 1" "1" "$rc"

    # --probe-ask (MOD-0.1, §18.2): the cursor-rule channel — one doorway call
    # at a chosen want level, real cursor reported before and after. The
    # comparison over every row belongs to tests/spec_mod0's check06 (a D27
    # author); what is pinned HERE is the surface: the exact line for one
    # known cell, the field count, the gate demotion being visible, and the
    # in-repo cursor sweep with a FLOORED population (an empty sweep prints
    # the same silence as a passing one, so the count is asserted).
    out="$("$PCREC" --probe-ask verdict -- '\d' 2>"$d/ep1.txt")"; rc=$?
    assert_eq "case10: --probe-ask verdict runs" "0" "$rc" \
        "stderr: $(cat "$d/ep1.txt")"
    assert_eq "case10: ...and reports the escape doorway cell exactly" \
        "escape	verdict	verdict	2	2	refusal	0	0	0	\\d requires module 'classes'" \
        "$out"
    assert_eq "case10: --probe-ask line has 10 fields" \
        "10" "$(printf '%s\n' "$out" | awk -F'\t' '{print NF}')"
    # the §5.4 gate, observable: a `result` ask is ANSWERED at `verdict`
    # while no module is enabled — the day one is, this cell changes and
    # this assertion must be revisited alongside check07
    assert_eq "case10: --probe-ask result is answered at verdict (the gate)" \
        "verdict" "$("$PCREC" --probe-ask result -- '\d' | cut -f3)"
    # ...and that day arrived (MOD-0.3c): with module classes ENABLED the
    # same ask reaches `result` and the outcome word is the PRODUCING
    # vocabulary — both cells were false the day before the producers wired
    # in (D33 §9.3), and the doorway still must not move the cursor even
    # when producing (fields 4/5 equal; the CALLER moves at result).
    assert_eq "case10: --features classes --probe-ask result produces a node" \
        "escape	result	result	2	2	node	0	0	0	" \
        "$("$PCREC" --features classes --probe-ask result -- '\d')"
    assert_eq "case10: ...and the posix class produces members, cursor unmoved" \
        "class-bracket	result	result	1	1	members	1	0	10	" \
        "$("$PCREC" --features classes --probe-ask result -- '[[:alpha:]]')"
    # full-text coordinates for a prefixed construct (the ten (?-N) rows)
    assert_eq "case10: --probe-ask reports full-text cursor coordinates" \
        "4	4" "$("$PCREC" --probe-ask verdict -- '(a)(?-1)' | cut -f4,5)"
    # THE CURSOR SWEEP: every registry row's syntax, claim and verdict, and
    # the cursor must not move (§18.2's hard rule; WANT_RESULT is the only
    # level allowed to move it — and the producing ports that exist since
    # MOD-0.3/MOD-0.5 (classes, modifiers) return it unmoved too, carrying
    # `end` for the CALLER to advance, check06's rule — so this sweep's
    # claim/verdict limit is caution, not a live dependency). (?:...)
    # is the one deliberate non-route: the base grammar answers it before
    # any doorway, so there is no call to probe.
    local swept=0 moved=0 noroute=0
    while IFS= read -r syn; do
        for w in claim verdict; do
            if line="$("$PCREC" --probe-ask "$w" -- "$syn" 2>/dev/null)"; then
                swept=$((swept + 1))
                [ "$(printf '%s\n' "$line" | cut -f4)" = \
                  "$(printf '%s\n' "$line" | cut -f5)" ] || {
                    moved=$((moved + 1))
                    fail "case10: cursor moved under $w" "$syn: $line"
                }
            else
                noroute=$((noroute + 1))
                [ "$syn" = '(?:...)' ] || \
                    fail "case10: a row's syntax no longer routes" "$syn ($w)"
            fi
        done
    done < <(grep -v '^#' "$d/dump.tsv" | cut -f3)
    if [ "$swept" -ge 198 ] && [ "$moved" -eq 0 ]; then
        pass "case10: cursor unchanged below WANT_RESULT over $swept probes (floor 198)"
    else
        fail "case10: cursor sweep" "swept=$swept (floor 198) moved=$moved"
    fi
    assert_eq "case10: exactly one row is base-answered before the doorway" \
        "2" "$noroute"
    # channel-cannot-run is exit 1 and distinct from a measured refusal
    "$PCREC" --probe-ask verdict -- 'abc' >/dev/null 2>"$d/ep2.txt"; rc=$?
    assert_eq "case10: --probe-ask on non-doorway text exits 1" "1" "$rc"
    assert_contains "case10: ...and explains the (?: exclusion" \
        "$(cat "$d/ep2.txt")" "base grammar answers"
    "$PCREC" --probe-ask sideways -- '\d' >/dev/null 2>&1; rc=$?
    assert_eq "case10: an unknown want level exits 1" "1" "$rc"
    "$PCREC" --probe-ask verdict -o - -- '\d' >/dev/null 2>&1; rc=$?
    assert_eq "case10: --probe-ask with -o exits 1" "1" "$rc"
    "$PCREC" --probe-ask verdict >/dev/null 2>&1; rc=$?
    assert_eq "case10: --probe-ask without a construct exits 1" "1" "$rc"
    "$PCREC" --probe-ask verdict --list-syntax >/dev/null 2>&1; rc=$?
    assert_eq "case10: --probe-ask with --list-syntax exits 1" "1" "$rc"

    # --features (MOD-0.1, slice 9): the enabled set. No module has ports yet,
    # so the ONLY observable today is the gate's state through --probe-ask's
    # answered_at — result stays result where the row's module is enabled,
    # demotes to verdict where it is not — and verdicts must not move at all
    # (check07's subject; one spot pin here).
    assert_eq "case10: --features all opens the gate (answered_at result)" \
        "result" "$("$PCREC" --features all --probe-ask result -- '\d' | cut -f3)"
    assert_eq "case10: --features is per-module, not a blanket switch" \
        "verdict" "$("$PCREC" --features backrefs --probe-ask result -- '\d' | cut -f3)"
    assert_eq "case10: an open gate does not move the cursor either" \
        "2	2" "$("$PCREC" --features all --probe-ask result -- '\d' | cut -f4,5)"
    # The MOD-0.1-era pin that stood here — "an open gate changes no verdict
    # text" — EXPIRED the day the first producer landed (MOD-0.3c), exactly
    # as its neighbour comment predicted ("the day one is, this cell changes
    # and this assertion must be revisited alongside check07"). Successor:
    # the open gate now changes the OUTCOME for a producing row, in exactly
    # one way — refusal -> produced node, diagnostic emptied — while the
    # closed gate keeps the refusal text verbatim.
    assert_eq "case10: an open gate now PRODUCES where the closed one refuses" \
        "node	" \
        "$("$PCREC" --features all --probe-ask result -- '\d' | cut -f6,10)"
    assert_eq "case10: ...and the closed gate keeps the refusal verbatim" \
        "refusal	\d requires module 'classes'" \
        "$("$PCREC" --probe-ask result -- '\d' | cut -f6,10)"
    "$PCREC" --features nosuchmodule --probe-ask result -- '\d' \
        >/dev/null 2>"$d/ef1.txt"; rc=$?
    assert_eq "case10: an unknown module name in --features exits 1" "1" "$rc"
    assert_contains "case10: ...and is refused BY NAME" \
        "$(cat "$d/ef1.txt")" "unknown module 'nosuchmodule'"
    # a BASE-TIER compile under --features all emits byte-identical code to
    # one without: the gate exists for module rows only and must never
    # perturb a base pattern's compile path (this pin's original "no ports
    # exist" rationale expired at MOD-0.3c; the base-tier half is the part
    # that must stay true forever).
    # SAME BASENAME in different directories — the emitted C embeds the
    # output basename in its #include (the journal's twice-paid lesson)
    mkdir -p "$d/fa" "$d/fb"
    "$PCREC" -o "$d/fa/feat.c" -- 'a(b|c)+d' 2>/dev/null
    "$PCREC" --features all -o "$d/fb/feat.c" -- 'a(b|c)+d' 2>/dev/null
    if cmp -s "$d/fa/feat.c" "$d/fb/feat.c"; then
        pass "case10: --features all compiles byte-identical output today"
    else
        fail "case10: --features all changed emitted code with no ports built"
    fi

    # an undiscoverable flag is a half-shipped one (case9's rule, applied here)
    out="$("$PCREC" --help)"
    assert_contains "case10: --help documents --list-syntax" "$out" "--list-syntax"
    assert_contains "case10: --help documents --list-verbs" "$out" "--list-verbs"
    assert_contains "case10: --help documents --explain" "$out" "--explain"
    assert_contains "case10: --help documents --count-groups" "$out" "--count-groups"
    assert_contains "case10: --help documents --probe-ask" "$out" "--probe-ask"
    assert_contains "case10: --help documents --features" "$out" "--features"

    # `--` still ends options: a pattern that looks like a query is a pattern
    "$PCREC" -o "$d/dash.c" -- '--list-syntax' 2>"$d/e10.txt"; rc=$?
    assert_eq "case10: -- protects a '--list-syntax'-looking pattern" "0" "$rc" \
        "stderr: $(cat "$d/e10.txt")"
}

case1
case2
case3
case4
case5
case6
case7
case8
case9
case10

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
