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

    # --explain's CONTENT assertions moved to case11 at MOD-0.7 and were
    # rewritten per FIELD. They are not here any more because R10/C4-1
    # demonstrated — and MOD-0.7a re-measured at 26b9660 — that all eight of
    # them stayed GREEN under a module-attribution swap between two rows of
    # `--explain '(?<'`: assert_contains tests the whole output blob, and the
    # "all four rows" count is satisfied by any four rows. Keeping them here
    # beside case11's field-level versions would leave assertions the project
    # has measured as unable to dissent sitting in the suite as if they were
    # coverage. What stays in case10 is the flag PLUMBING below, which is
    # about argument handling and not about what --explain knows.

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

# ---------------------------------------------------------------------------
# 11. `--explain` (MOD-0.7): the CROSS-SOURCE query surface.
#
#     THIS CASE EXISTS BECAUSE case10's --explain assertions COULD NOT DISSENT.
#     R10/C4-1 demonstrated it and MOD-0.7a re-measured it at 26b9660: swap the
#     module attributions of two rows in registry.c and all eight of case10's
#     --explain content assertions stay green, because assert_contains tests the
#     whole output blob and the row count is satisfied by any four rows. Those
#     assertions MOVED here and were rewritten per FIELD. case10 keeps only the
#     flag-plumbing ones (conflicts, missing value, --help).
#
#     THE RULE FOR THIS CASE, and it is the reason it exists:
#       NO assert_contains AGAINST A WHOLE --explain OUTPUT. Every assertion
#       names a ROW (or the header) and a KEY, through explain_field.
#     A future assertion that reaches for assert_contains "$out" is re-creating
#     the defect this case was written to remove.
#
#     WHAT THIS CASE CANNOT REACH (docs/design_notes_mod07.md section 9.4 —
#     recorded here because the sweep-template lesson has recurred four times
#     and this is the signpost):
#       - THE QUERY SET IS HAND-LISTED. The generated query space (every byte
#         after each doorway opener, at depth) is NOT swept here; a routing or
#         selection bug that affects only a byte outside the list below is
#         invisible to this case.
#       - the row set comes from --list-syntax, the same table --explain prints,
#         so a DELETED row disappears from both (check_required_rows' hand-written
#         manifest is what sees that);
#       - the attribution clause CANNOT dissent on a module-name swap (measured:
#         ext.c renders the promise from the same r->module --explain prints), so
#         the module PINS below, not the `agree` field, are the C4-1 net;
#       - class-position answers are DECLARED (the `class` column), never live.
# ---------------------------------------------------------------------------

# explain_field <output> <row-syntax|@header> <key>  ->  the value, or ""
#
# The format is a strict grammar so that a test can dissent per field: header
# lines are unindented `key<2+ spaces>value` and end at the first blank line;
# each row block then starts with the row's `syntax` unindented and continues
# with `  key<2+ spaces>value`. Keys never contain two consecutive spaces,
# which is what makes the split unambiguous.
explain_field() {
    # row/key go through the ENVIRONMENT, never `awk -v`: -v processes escape
    # sequences in its value, so a row named `\v` would arrive as a vertical
    # tab and match nothing. Half this case's rows are backslash escapes.
    EF_ROW="$2" EF_KEY="$3" awk '
        BEGIN { hdr = 1; row = ENVIRON["EF_ROW"]; key = ENVIRON["EF_KEY"] }
        /^$/   { hdr = 0; head = ""; next }
        /^[^ ]/ {
            if (hdr) {
                if (row == "@header" && match($0, /  +/)) {
                    k = substr($0, 1, RSTART - 1)
                    if (k == key) { print substr($0, RSTART + RLENGTH); exit }
                }
            } else head = $0
            next
        }
        {
            if (row == "@header" || head != row) next
            line = substr($0, 3)
            if (match(line, /  +/)) {
                k = substr(line, 1, RSTART - 1)
                if (k == key) { print substr(line, RSTART + RLENGTH); exit }
            }
        }
    ' <<<"$1"
}

# assert_field <case-name> <output> <row> <key> <expected>
assert_field() {
    local name="$1" out="$2" row="$3" key="$4" want="$5"
    assert_eq "$name" "$want" "$(explain_field "$out" "$row" "$key")" \
        "row: $row  key: $key"
}

case11() {
    local d="$WORKDIR/case11"
    mkdir -p "$d"
    local rc out

    # --- D29's worked example, the headline: it did not run before MOD-0.7 ---
    out="$("$PCREC" --explain '(?i-m:' 2>"$d/e1.txt")"; rc=$?
    assert_eq "case11: --explain '(?i-m:' exits 0" "0" "$rc" \
        "stderr: $(cat "$d/e1.txt")"
    assert_field "case11: ...echoes the query" "$out" "@header" "query" "(?i-m:"
    assert_field "case11: ...routes to the (? doorway with selector i" "$out" \
        "@header" "route" "after '(?'  selector 'i'"
    assert_field "case11: ...and the LIVE doorway answers it" "$out" "@header" \
        "live" "(?i...) requires module 'modifiers'"
    assert_field "case11: ...at pcrec's own blame offset" "$out" "@header" "live at" "0"
    assert_field "case11: ...electing the (?i) row" "$out" "@header" "live elected" "(?i)"
    assert_field "case11: ...answered at verdict (the gate is shut)" "$out" \
        "@header" "live answered" "verdict"
    assert_field "case11: ...promising module modifiers" "$out" "@header" \
        "live names" "modifiers"
    assert_field "case11: ...with one row shown" "$out" "@header" "rows" "1"
    assert_field "case11: ...and no dissent" "$out" "@header" "dissents" "0"
    # the row is a CANDIDATE (it competed), which the prefix rule cannot say:
    # today's prefix match finds NOTHING for this query
    assert_field "case11: '(?i-m:' selects (?i) as a candidate" "$out" "(?i)" \
        "select" "candidate"

    # --- THE C4-1 NET: hand-written module pins, per row, per field ---------
    # These are the assertions a module-attribution swap must fail. NOT the
    # `agree` field: that reads r->module through ext.c's own snprintf and
    # agrees with itself (measured, design note section 0). tests/reject is the
    # primary home of module-name truth (470 pins); these six are the subset
    # R10's C4-1 and C4-1b actually used, plus one row per doorway.
    out="$("$PCREC" --explain '(?<')"
    assert_field "case11: (?<=...) is module lookaround" "$out" "(?<=...)" \
        "module" "lookaround"
    assert_field "case11: (?<name>a) is module named-groups" "$out" "(?<name>a)" \
        "module" "named-groups"
    assert_field "case11: (?<=...) wins its own syntax" "$out" "(?<=...)" \
        "own elected" "self"
    assert_field "case11: ...and its live answer promises its own module" "$out" \
        "(?<=...)" "own names" "lookaround"
    assert_field "case11: (?<=...) agrees" "$out" "(?<=...)" "agree" "ok"
    assert_field "case11: (?<name>a) agrees" "$out" "(?<name>a)" "agree" "ok"
    # the four rows of the '<' bucket, all candidates — case10 counted them,
    # this names them
    assert_eq "case11: --explain '(?<' shows the whole bucket" "4" \
        "$(explain_field "$out" "@header" "rows")"
    assert_field "case11: the lookbehind rows are candidates" "$out" "(?<!...)" \
        "select" "candidate"
    # and the QUERY's own live answer elects the bare row, not a lookbehind
    assert_field "case11: '(?<' truncated elects the bare named-group row" \
        "$out" "@header" "live elected" "(?<name>a)"

    out="$("$PCREC" --explain '\N{U+0041}')"
    assert_field "case11: \N{U+0041} is module unicode-props" "$out" '\N{U+0041}' \
        "module" "unicode-props"
    assert_field "case11: \N is module classes" "$out" '\N' "module" "classes"
    # R10/C1-1: the bucket has THREE rows and the prefix rule sees two. The
    # third is a candidate here, which is the selection rule's whole point.
    assert_eq "case11: the \N bucket shows all three rows" "3" \
        "$(explain_field "$out" "@header" "rows")"
    assert_field "case11: \N{name} is a CANDIDATE the prefix rule misses" "$out" \
        '\N{name}' "select" "candidate"
    assert_field "case11: \N{name} is a rejected row promising nothing" "$out" \
        '\N{name}' "own names" "—"
    assert_field "case11: ...and that agrees" "$out" '\N{name}' "agree" "ok"

    # --- THE ROADMAP_NEVER ROW: the defect MOD-0.7a found (note section 1) ---
    # --explain promised module 'callouts' for a construct the compiler
    # refuses with "no module will implement it". K14's over-promise, fixed in
    # ext.c at MOD-0.1, still live on the query surface because syntax_dump.c
    # never read `roadmap`. These three assertions were written BEFORE the fix
    # and watched failing (the FIX-3 pattern; the recorded failure is in this
    # slice's commit message) — the `agree` clause cannot see this defect,
    # because both of its sides read the row.
    out="$("$PCREC" --explain '(?C1)')"
    assert_field "case11: (?C1) carries roadmap never" "$out" "(?C1)" \
        "roadmap" "never"
    assert_field "case11: (?C1)'s status does NOT promise a module" "$out" \
        "(?C1)" "status" \
        "known, outside pcrec's scope — no module will implement it"
    assert_field "case11: ...the row still records whose module it would be" \
        "$out" "(?C1)" "module" "callouts"
    assert_field "case11: ...the live answer promises nothing" "$out" "(?C1)" \
        "own names" "—"
    assert_field "case11: ...and that is agreement, not a dissent" "$out" \
        "(?C1)" "agree" "ok"

    # --- the class-bracket doorway, and a DECLARED class expectation --------
    out="$("$PCREC" --explain '[[:alpha:]]')"
    assert_field "case11: [[:alpha:]] is module classes" "$out" "[[:alpha:]]" \
        "module" "classes"
    assert_field "case11: ...blamed at pcrec's own offset" "$out" "[[:alpha:]]" \
        "own at" "1"
    out="$("$PCREC" --explain '\d')"
    assert_field "case11: \d's class expectation is DECLARED from the row" \
        "$out" '\d' "class" "set 10"
    assert_field "case11: \d carries the PCRE2 semantics note" "$out" '\d' \
        "note" "any decimal digit"
    out="$("$PCREC" --explain '\v')"
    assert_field "case11: \v is module classes" "$out" '\v' "module" "classes"
    assert_field "case11: \v's note is the measured PCRE2 semantics" "$out" '\v' \
        "note" \
        "any vertical whitespace character (NOT vertical tab; python re disagrees)"

    # --- QUERY CELLS whose live answer differs from the row's declaration ---
    # Five measured cells where that is CORRECT. Pinned as correct so a future
    # reader does not "fix" them into agreement.
    out="$("$PCREC" --explain '\p{Foo}')"
    assert_field "case11: \p{Foo} gets mod_uprops' refined refusal" "$out" \
        "@header" "live" "\p requires module 'unicode-props'"
    # K16: this offset is PCREC'S OWN behaviour (stability, not oracle
    # agreement) — 164 of 256 body bytes are libpcre2 err-146 AT THE BYTE while
    # pcrec's scanner reads past them. The K16 fix lands with the first
    # unicode-props producer and MOVES this number; it is pinned so the move is
    # deliberate rather than silent.
    assert_field "case11: ...at pcrec's own scan-completion offset (K16)" \
        "$out" "@header" "live at" "7"
    out="$("$PCREC" --explain '(*NOTAVERB)')"
    assert_field "case11: an unknown verb NAME promises no module" "$out" \
        "@header" "live" "(*VERB) not recognized or malformed"
    assert_field "case11: ...even though the one verb ROW declares one" "$out" \
        "(*ACCEPT)" "module" "verbs"
    assert_field "case11: ...and the name table says it is not known" "$out" \
        "verb name NOTAVERB" "known" "no"
    assert_field "case11: ...naming the table PCRE2 would have consulted" \
        "$out" "verb name NOTAVERB" "table" "upper"
    out="$("$PCREC" --explain '(*ACCEPT)')"
    assert_field "case11: a known verb name reports its measured forms" "$out" \
        "verb name ACCEPT" "forms" "(*N)|(*N:a)|(*N:)"
    assert_field "case11: ...and where its roadmap came from" "$out" \
        "verb name ACCEPT" "roadmap src" "inherited from the (* row"
    out="$("$PCREC" --explain '[[:foo:]]')"
    assert_field "case11: an unknown POSIX name promises no module" "$out" \
        "@header" "live" "unknown POSIX class name"
    assert_field "case11: ...while its row is still module classes" "$out" \
        "[[:alpha:]]" "module" "classes"
    out="$("$PCREC" --explain '[[:<:]]')"
    assert_field "case11: a whole-class-only name names ANOTHER module" "$out" \
        "@header" "live names" "assertions"
    out="$("$PCREC" --explain '(?iZ)')"
    assert_field "case11: a malformed option RUN promises no module" "$out" \
        "@header" "live" "unrecognized character after (? or (?-"
    # ...and the elected row is still the option row: `elected` is the row the
    # doorway DISPATCHED on, not the row that wrote the message
    assert_field "case11: ...but the (?i) row was still the one elected" "$out" \
        "@header" "live elected" "(?i)"

    # --- the gate axis: --features changes what the doorway DOES ------------
    out="$("$PCREC" --features classes --explain '\d')"
    assert_field "case11: an open gate PRODUCES instead of refusing" "$out" \
        "@header" "live" "produces an AST node"
    assert_field "case11: ...answered at result, the gate observable" "$out" \
        "@header" "live answered" "result"
    # WHAT THIS CELL ASSERTS CHANGED AT R20/MOD07-3, and the annotation has to
    # say so because the string alone does not. It used to read "ok (produces;
    # this row's module is enabled)" and that was the WHOLE of the row's
    # agreement at an open gate: `put_agreement` short-circuited on any
    # non-refusal, so promise and attribution were never evaluated and opening
    # a gate SHRANK the coverage of the rows it turned on. Now three clauses
    # run against the row's CLOSED-GATE answer (which is where the predicate
    # was censused) and a fourth — `gate` — runs against this open-gate one:
    # a row that produces must have its declared module in the enabled set.
    # So this cell is now four assertions wearing one string, and the
    # parenthetical names which gate each half was judged at.
    assert_field "case11: ...and producing is agreement for a module row" \
        "$out" '\d' "agree" \
        "ok  (clauses at the closed gate; at this one the row produces and its module is enabled)"
    # the DISPLAYED answer is still the requested gate's — the clause scope
    # moved, the data did not
    assert_field "case11: ...with the open gate's own answer still displayed" \
        "$out" '\d' "own" "produces an AST node"

    # --- THE CLAUSE SCOPE: clauses judge the CLOSED gate (R20/MOD07-2) -----
    # `(?J)` and `(?m)` DISSENTED the moment `--features modifiers` opened the
    # gate — exit 3, stderr calling it "a pcrec defect", about a tree
    # tests/reject:663-664 pins as CORRECT. An enabled option-run port refuses
    # per LETTER and a letter's module is not the option ROW's, so comparing
    # them fired on right data. §5.2's census was taken entirely at the closed
    # gate; the enabled set is the axis the design never varied. Written
    # failing first — both exited 3 with
    #   agree  DISSENT: attribution: declared 'modifiers', live names 'named-groups'
    # — and the verbatim blocks are in the slice's commit message.
    local letter_mod
    for q in '(?J)' '(?m)'; do
        [ "$q" = '(?J)' ] && letter_mod="named-groups" || letter_mod="assertions"
        out="$("$PCREC" --features modifiers --explain "$q" 2>"$d/e3.txt")"; rc=$?
        assert_eq "case11: an open gate does not make $q dissent" "0" "$rc" \
            "stderr: $(cat "$d/e3.txt")"
        assert_field "case11: ...$q's row agrees" "$out" "$q" "agree" "ok"
        assert_field "case11: ...and the header counts no dissent for $q" \
            "$out" "@header" "dissents" "0"
        # the per-LETTER module is still SHOWN. This is the pin that stops the
        # fix being "make the two sides agree by dropping the interesting
        # one": the displayed answer must keep naming the letter's module.
        assert_field "case11: ...while $q's own answer still names the letter's module" \
            "$out" "$q" "own names" "$letter_mod"
        assert_field "case11: ...and the row still declares its own" \
            "$out" "$q" "module" "modifiers"
    done

    # --- the base-grammar row: an honest non-answer, not a fabricated one ---
    out="$("$PCREC" --explain '(?:')"; rc=$?
    assert_eq "case11: --explain '(?:' exits 0" "0" "$rc"
    assert_field "case11: (?: has no doorway call to report" "$out" "@header" \
        "route" \
        "none — the base grammar answers this text before any doorway is consulted"
    assert_field "case11: ...and its row says so rather than passing silently" \
        "$out" "(?:...)" "agree" "ok  (base grammar; no doorway call to compare)"
    assert_field "case11: ...it is a prefix match, not a bucket candidate" \
        "$out" "(?:...)" "select" "listed"

    # --- the unanswerable query keeps its exit 1 and its message ------------
    "$PCREC" --explain 'a' >"$d/o2.txt" 2>"$d/e2.txt"; rc=$?
    assert_eq "case11: --explain on base syntax exits 1" "1" "$rc"
    assert_contains "case11: ...and says why" "$(cat "$d/e2.txt")" \
        "no construct matches"

    # --- THE FLOORED SWEEPS -------------------------------------------------
    # An empty sweep prints the same silence as a passing one, so the
    # populations are asserted. Every displayed row must win its OWN syntax and
    # agree; the ONE exception is the single RS_BASE row, whose syntax reaches
    # no doorway.
    local blocks=0 selfel=0 agreed=0 exempt=0 answered=0 q
    local queries=('\v' '\d' '\N{U+0041}' '(?<' '(?P' '(?i-m:' '(?iZ)' '(?C1)'
                   '(?(1)' '(?-1)' '[[:alpha:]]' '[[.a.]]' '[[:foo:]]'
                   '(*ACCEPT)' '(*NOTAVERB)' '\p{Foo}' '(?' '(?:' '\Q')
    for q in "${queries[@]}"; do
        out="$("$PCREC" --explain "$q" 2>/dev/null)" || continue
        answered=$((answered + 1))
        while IFS= read -r line; do
            # match on the KEY and trim the value, never on a fixed column:
            # the first version of this loop pinned the padding and reported
            # 81 dissents the moment a key got one space wider
            local v
            case "$line" in
              "  own elected"*)
                  v="${line#*elected}"; v="${v#"${v%%[! ]*}"}"
                  blocks=$((blocks + 1))
                  if [ "$v" = "self" ]; then selfel=$((selfel + 1))
                  else exempt=$((exempt + 1)); fi ;;
            esac
            case "$line" in
              "  agree"*)
                  v="${line#*agree}"; v="${v#"${v%%[! ]*}"}"
                  case "$v" in
                    ok*) agreed=$((agreed + 1)) ;;
                    *)   fail "case11: a row DISSENTS on the shipped table" \
                              "query: $q" "$line" ;;
                  esac ;;
            esac
        done < <(printf '%s\n' "$out")
    done
    # FLOORS, measured at landing: 19 queries answered, 81 row blocks. A floor
    # catches shrinkage (a row deleted, a selection rule narrowed); adding a
    # registry row raises the count and is fine.
    if [ "$answered" -ge 19 ] && [ "$blocks" -ge 81 ] && [ "$agreed" -eq "$blocks" ]; then
        pass "case11: $blocks row blocks over $answered queries, all agree (floors 81/19)"
    else
        fail "case11: agreement sweep" \
             "answered=$answered (floor 19) blocks=$blocks (floor 81) agreed=$agreed"
    fi
    # every block but the RS_BASE row's elected ITSELF
    if [ "$selfel" -eq $((blocks - exempt)) ] && [ "$exempt" -le 3 ]; then
        pass "case11: $selfel/$blocks blocks elected their own row ($exempt base-grammar exempt)"
    else
        fail "case11: election sweep" "self=$selfel blocks=$blocks exempt=$exempt"
    fi
    # and no query on the shipped table may exit 3
    local dissenting=0
    for q in "${queries[@]}"; do
        "$PCREC" --explain "$q" >/dev/null 2>&1
        [ $? -eq 3 ] && dissenting=$((dissenting + 1))
    done
    assert_eq "case11: no query dissents on the shipped table (exit 3 count)" \
        "0" "$dissenting"

    # --- the dissent contract, in the direction that can be tested here -----
    # Exit 3's FIRING direction needs a sabotaged table and this case must
    # never ship asserting against one (manager ruling 6), so it is measured at
    # landing as V1-V7 and recorded in the commit message. What is pinned here
    # is that the surface distinguishes the two failure modes at all: exit 1
    # for an unanswerable query (above) and exit 0 with `dissents 0` for a
    # clean one.
    out="$("$PCREC" --explain '\v')"
    assert_field "case11: a clean query reports zero dissents" "$out" \
        "@header" "dissents" "0"
}

# ---------------------------------------------------------------------------
# 12. A PRODUCING PORT THAT FAILS, ON THE QUERY SURFACES (R20/MOD07-1, tier 1).
#
#     Both query surfaces hand a doorway a Ctx they `memset` and never
#     `setjmp`. That was safe exactly while every doorway RETURNED its answer
#     — and the extracted `doorway_call` still CARRIES the comment saying so,
#     naming "the first enabled, result-producing module port" as the event
#     that must revisit it. That port landed at MOD-0.3c/0.5c, two milestones
#     before `--explain` was rewritten around the same Ctx, and nothing
#     revisited: `--features modifiers --explain '(?i:['` SIGSEGVed (139),
#     because mod_modifiers' port recurses into `pcrec_parse_body`, the
#     unterminated class raises `ctx_fail`, and the longjmp lands in an
#     uninitialized `jmp_buf`.
#
#     WHAT IS PINNED IS THE SHAPE, NOT THE WORDING (D26 tier 3): a status
#     that is nonzero (the surface could not answer) and BELOW 128 (bash
#     reports 128+N for a signal, so this is what separates "diagnosed" from
#     "died"), plus a non-empty diagnostic on the stream that surface already
#     uses for errors. Both surfaces, because both had the defect.
#
#     THE GATE IS THE AXIS, so both of its states are here: closed, the same
#     text is an ordinary refusal at exit 0 and must stay one; open, a
#     WELL-FORMED body must still produce. A guard that turned every open-gate
#     query into an error would satisfy the two crash pins alone.
# ---------------------------------------------------------------------------

# assert_clean_failure <case-name> <rc> <stderr-file>
# Nonzero (it failed) and < 128 (it was not killed by a signal) and it said
# something. 139 = 128 + SIGSEGV is exactly what this rejects.
assert_clean_failure() {
    local name="$1" rc="$2" ef="$3"
    if [ "$rc" -ne 0 ] && [ "$rc" -lt 128 ] && [ -s "$ef" ]; then
        pass "$name (exit $rc, diagnosed)"
    else
        fail "$name" "exit: $rc (want nonzero and < 128)" \
             "stderr: $(cat "$ef")"
    fi
}

case12() {
    local d="$WORKDIR/case12"
    mkdir -p "$d"
    local rc out

    # --- the two crashing cells (139 before the fix) ---------------------
    "$PCREC" --features modifiers --explain '(?i:[)' \
        >"$d/o1.txt" 2>"$d/e1.txt"; rc=$?
    assert_clean_failure \
        "case12: --explain survives a port that ctx_fails" "$rc" "$d/e1.txt"
    "$PCREC" --features all --probe-ask result -- '(?i:[)' \
        >"$d/o2.txt" 2>"$d/e2.txt"; rc=$?
    assert_clean_failure \
        "case12: --probe-ask survives a port that ctx_fails" "$rc" "$d/e2.txt"

    # ...and the port's own diagnostic is what the operator is told, rather
    # than a generic "could not answer". The TEXT is tier 3 and free; that it
    # is the CLASS ERROR and not the misuse sentence is not.
    assert_contains "case12: ...naming the error the port actually raised" \
        "$(cat "$d/e1.txt")" "character class"
    assert_contains "case12: ...on --probe-ask too" \
        "$(cat "$d/e2.txt")" "character class"
    # the misuse sentence must NOT be what a failing port prints: before this
    # fix the only nonzero --probe-ask path was "WANT must be claim, verdict
    # or result", and reusing it here would tell the operator to fix their
    # command line for a defect in the pattern.
    if grep -q "WANT must be" "$d/e2.txt"; then
        fail "case12: a failing port must not print the misuse sentence" \
             "stderr: $(cat "$d/e2.txt")"
    else
        pass "case12: a failing port does not print --probe-ask's misuse sentence"
    fi

    # --- the CLOSED gate: the same text, an ordinary answer ---------------
    out="$("$PCREC" --explain '(?i:[)' 2>"$d/e3.txt")"; rc=$?
    assert_eq "case12: closed-gate --explain of the same text exits 0" "0" "$rc" \
        "stderr: $(cat "$d/e3.txt")"
    assert_field "case12: ...and answers with the module refusal" "$out" \
        "@header" "live" "(?i...) requires module 'modifiers'"
    out="$("$PCREC" --probe-ask result -- '(?i:[)' 2>"$d/e4.txt")"; rc=$?
    assert_eq "case12: closed-gate --probe-ask of the same text exits 0" "0" "$rc" \
        "stderr: $(cat "$d/e4.txt")"
    assert_eq "case12: ...reporting a refusal, not an error" "refusal" \
        "$(cut -f6 <<<"$out")"

    # --- the OPEN gate, WELL-FORMED body: production is untouched ---------
    # The positive control for the guard itself: a setjmp that swallowed
    # every open-gate answer would pass both crash pins above.
    out="$("$PCREC" --features modifiers --explain '(?i:a)' 2>"$d/e5.txt")"; rc=$?
    assert_eq "case12: an open gate still answers a well-formed body" "0" "$rc" \
        "stderr: $(cat "$d/e5.txt")"
    assert_field "case12: ...by PRODUCING" "$out" "@header" "live" \
        "produces an AST node"
    assert_field "case12: ...answered at result" "$out" "@header" \
        "live answered" "result"
    out="$("$PCREC" --features all --probe-ask result -- '(?i:a)' 2>"$d/e6.txt")"; rc=$?
    assert_eq "case12: --probe-ask likewise" "0" "$rc" \
        "stderr: $(cat "$d/e6.txt")"
    assert_eq "case12: ...reporting the produced node" "node" \
        "$(cut -f6 <<<"$out")"
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
case11
case12

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
