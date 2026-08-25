#!/usr/bin/env bash
# tests/cli/run_cli_tests.sh — CLI surface + library-API regression tests.
#
# Part of `make test` since M2. Covers the CLI surface beyond the plain `-p rx -o tmp/gen.c`
# path the .rxt harness exercises: -o -, --emit-main, prefix boundary
# validation, subdirectory output, `--` end-of-options, missing-value and
# unknown-option diagnostics, and a direct library-API (pcrec_compile /
# pcrec_output_free) NULL-argument / double-free smoke test.
#
# docs/dev/reviews/2026-08-09-m1.md P-M1; plan M2.4.
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
# D45: one shared generated-code compile budget (docs/dev/decisions.md). The
# library-API smoke case is deliberately NOT wrapped: it links libpcrec.a, so
# it is compiler-axis code, not a generated matcher.
#
# EXECUTION of the emitted --emit-main/driver binaries below is bounded too
# (gen_run, same file): a handful of runs per case, not an inner loop.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="cli"
# [SR-11] table_contract.md's one implementation (tests/lib/table.sh): case10
# below resolves the dump's field count from its OWN header rather than a
# hardcoded literal — see that case's comment.
. "$ROOT_DIR/tests/lib/table.sh"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
LIBA="${LIBA:-$ROOT_DIR/build/libpcrec.a}"
LIBDIR="${LIBDIR:-$ROOT_DIR/lib}"
KEEP="${KEEP:-0}"
# SAN-1: this is a compile site for GENERATED matcher code (gen.c, several
# cases below) as well as this file's own small test drivers, in the same
# invocation — so it honors GENCFLAGS like tests/harness and tests/codegen
# do, rather than a hardcoded string, which was a gap the sanitizer battery
# found (docs/testing.md, "Sanitizer + lint battery").
CFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
if [ "${LINTGEN:-0}" = "1" ]; then CFLAGS="$CFLAGS -fanalyzer"; fi

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
    out="$(pcrec_run "$PCREC" -o - -- 'abc' 2>"$d/stderr.txt" 1>"$d/gen.c")"
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
/* [M4.4] D44.2: the caps-array search signature, its FINAL shape — no
 * rx_span/out-struct declared here at all, since the parameter type needs
 * no name of its own. */
int rx_search(const unsigned char *s, size_t n, size_t startpos, ptrdiff_t (*caps)[2]);
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    ptrdiff_t caps[1][2];
    if (rx_search((const unsigned char *)argv[1], strlen(argv[1]), 0, caps)) {
        printf("match %td %td\n", caps[0][0], caps[0][1]);
    } else {
        printf("nomatch\n");
    }
    return 0;
}
EOF
    local build_log build_rc
    gen_cc "${FUNCNAME[0]}" "$CC" $CFLAGS -o "$d/t" "$d/gen.c" "$d/mymain.c"
    build_rc=$?; build_log="$GEN_CC_LOG"
    if [ "$build_rc" -eq 0 ]; then
        pass "case1: gcc compiles the -o - output standalone with an appended main"
    else
        fail "case1: gcc compiles the -o - output standalone with an appended main" "$build_log"
        return
    fi
    local runout
    runout="$(gen_run "${FUNCNAME[0]} match" "$d/t" xxabcxx)"
    assert_eq "case1: standalone binary matches 'abc' in 'xxabcxx'" "match 2 5" "$runout"
    runout="$(gen_run "${FUNCNAME[0]} nomatch" "$d/t" zzz)"
    assert_eq "case1: standalone binary reports nomatch for 'zzz'" "nomatch" "$runout"
}

# ---------------------------------------------------------------------------
# 2. --emit-main produces a runnable binary with match/nomatch output.
# ---------------------------------------------------------------------------
case2() {
    local d="$WORKDIR/case2"
    mkdir -p "$d"
    local rc
    pcrec_run "$PCREC" --emit-main -o - -- 'abc' > "$d/gen.c" 2>"$d/stderr.txt"
    rc=$?
    assert_eq "case2: --emit-main -o - exits 0" "0" "$rc" "stderr: $(cat "$d/stderr.txt")"

    local build_log build_rc
    gen_cc "${FUNCNAME[0]}" "$CC" $CFLAGS -o "$d/t" "$d/gen.c"
    build_rc=$?; build_log="$GEN_CC_LOG"
    if [ "$build_rc" -eq 0 ]; then
        pass "case2: --emit-main output compiles into a runnable binary"
    else
        fail "case2: --emit-main output compiles into a runnable binary" "$build_log"
        return
    fi

    local runout runrc
    runout="$(gen_run "${FUNCNAME[0]} match" "$d/t" xxabcxx)"; runrc=$?
    assert_eq "case2: emitted main prints 'match START END' for a match" "match 2 5" "$runout"
    assert_eq "case2: emitted main exits 0 on match" "0" "$runrc"

    runout="$(gen_run "${FUNCNAME[0]} nomatch" "$d/t" zzz)"; runrc=$?
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
    pcrec_run "$PCREC" -p "$p60" --emit-main -o - -- 'a' >"$d/g60.c" 2>"$d/e1.txt"
    rc=$?
    assert_eq "case3: 60-char prefix accepted (pcrec exit 0)" "0" "$rc" "stderr: $(cat "$d/e1.txt")"
    gen_cc "${FUNCNAME[0]}" "$CC" $CFLAGS -o "$d/t60" "$d/g60.c"
    build_rc=$?; build_log="$GEN_CC_LOG"
    if [ "$build_rc" -eq 0 ]; then
        pass "case3: 60-char-prefix generated code compiles"
    else
        fail "case3: 60-char-prefix generated code compiles" "$build_log"
    fi

    pcrec_run "$PCREC" -p "$p61" -o "$d/g61.c" -- 'a' 2>"$d/e2.txt"
    rc=$?
    assert_eq "case3: 61-char prefix rejected exit 1" "1" "$rc"
    assert_contains "case3: 61-char prefix rejection has a diagnostic" \
        "$(cat "$d/e2.txt")" "prefix"

    pcrec_run "$PCREC" -p "1abc" -o "$d/glead.c" -- 'a' 2>"$d/e3.txt"
    rc=$?
    assert_eq "case3: leading-digit prefix rejected exit 1" "1" "$rc"
    assert_contains "case3: leading-digit prefix rejection has a diagnostic" \
        "$(cat "$d/e3.txt")" "prefix"

    pcrec_run "$PCREC" -p "" -o "$d/gempty.c" -- 'a' 2>"$d/e4.txt"
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
    pcrec_run "$PCREC" -o "$sub/gen.c" -- 'abc' 2>"$d/stderr.txt"
    rc=$?
    assert_eq "case4: -o subdir/gen.c exits 0" "0" "$rc" "stderr: $(cat "$d/stderr.txt")"

    if [ -f "$sub/gen.c" ] && [ -f "$sub/gen.h" ]; then
        pass "case4: both gen.c and gen.h written in subdir"
    else
        fail "case4: both gen.c and gen.h written in subdir" \
            "ls $sub: $(ls "$sub" 2>&1)"
        return
    fi

    local build_log build_rc
    gen_cc "${FUNCNAME[0]}" "$CC" $CFLAGS -I"$sub" -o "$d/t" "$ROOT_DIR/tests/harness/driver.c" "$sub/gen.c"
    build_rc=$?; build_log="$GEN_CC_LOG"
    if [ "$build_rc" -eq 0 ]; then
        pass "case4: subdir output compiles with -I subdir"
    else
        fail "case4: subdir output compiles with -I subdir" "$build_log"
        return
    fi
    local runout
    runout="$(gen_run "${FUNCNAME[0]}" "$d/t" 'xxabcxx')"
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

    pcrec_run "$PCREC" --emit-main -o - -- '-foo' > "$d/gen.c" 2>"$d/stderr.txt"
    rc=$?
    assert_eq "case5: -- allows a pattern starting with '-' (exit 0)" "0" "$rc" \
        "stderr: $(cat "$d/stderr.txt")"
    local build_log build_rc
    gen_cc "${FUNCNAME[0]}" "$CC" $CFLAGS -o "$d/t" "$d/gen.c"
    build_rc=$?; build_log="$GEN_CC_LOG"
    if [ "$build_rc" -eq 0 ]; then
        pass "case5: '-foo' pattern generated code compiles"
        local runout
        runout="$(gen_run "${FUNCNAME[0]}" "$d/t" 'xx-fooxx')"
        assert_eq "case5: '-foo' literal matches its own text" "match 2 6" "$runout"
    else
        fail "case5: '-foo' pattern generated code compiles" "$build_log"
    fi

    pcrec_run "$PCREC" -o 2>"$d/e_o.txt"; rc=$?
    assert_eq "case5: missing -o value exits 1" "1" "$rc"
    assert_contains "case5: missing -o value diagnoses 'missing value'" \
        "$(cat "$d/e_o.txt")" "missing value"

    pcrec_run "$PCREC" -p 2>"$d/e_p.txt"; rc=$?
    assert_eq "case5: missing -p value exits 1" "1" "$rc"
    assert_contains "case5: missing -p value diagnoses 'missing value'" \
        "$(cat "$d/e_p.txt")" "missing value"

    pcrec_run "$PCREC" -e 2>"$d/e_e.txt"; rc=$?
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

    pcrec_run "$PCREC" -o "$d/x.c" 2>"$d/e_nopat.txt"; rc=$?
    assert_eq "case6: no pattern exits 1" "1" "$rc"
    assert_contains "case6: no pattern gives a diagnostic on stderr" \
        "$(cat "$d/e_nopat.txt")" "pattern"

    pcrec_run "$PCREC" -o "$d/y.c" -- 'a' 'b' 2>"$d/e_twopat.txt"; rc=$?
    assert_eq "case6: two patterns exits 1" "1" "$rc"
    assert_contains "case6: two patterns gives a diagnostic on stderr" \
        "$(cat "$d/e_twopat.txt")" "one pattern"

    pcrec_run "$PCREC" -z -o "$d/z.c" -- 'a' 2>"$d/e_unk.txt"; rc=$?
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
    local build_log build_rc
    build_log="$("$CC" $CFLAGS -I"$LIBDIR" -o "$d/smoke" "$d/smoke.c" "$LIBA" 2>&1)"
    if [ $? -eq 0 ]; then
        pass "case7: library-API smoke test compiles against pcrec.h + libpcrec.a"
    else
        fail "case7: library-API smoke test compiles against pcrec.h + libpcrec.a" "$build_log"
        return
    fi

    local runout runrc
    runout="$("$TIMEOUT_BIN" 10 "$d/smoke" 2>"$d/smoke_stderr.txt")"
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
#    accepted, reaches pcrec_options.flags (PCREC_CASELESS, [M4.4] D43.2/D44.8:
#    was pcrec_options.caseless), composes with `--` and
#    --emit-main, and does not leak into a build that did not ask for it.
# ---------------------------------------------------------------------------
case9() {
    local d="$WORKDIR/case9"
    mkdir -p "$d"
    local rc build_log runout

    pcrec_run "$PCREC" -i --emit-main -o - -- 'aBc' > "$d/gen.c" 2>"$d/stderr.txt"
    rc=$?
    assert_eq "case9: -i exits 0" "0" "$rc" "stderr: $(cat "$d/stderr.txt")"

    gen_cc "${FUNCNAME[0]}" "$CC" $CFLAGS -o "$d/t" "$d/gen.c"
    build_rc=$?; build_log="$GEN_CC_LOG"
    if [ "$build_rc" -ne 0 ]; then
        fail "case9: -i output compiles" "$build_log"
        return
    fi
    pass "case9: -i output compiles warning-clean"

    runout="$(gen_run "${FUNCNAME[0]} -i match ABC" "$d/t" xxABCxx)"
    assert_eq "case9: -i 'aBc' matches 'ABC'" "match 2 5" "$runout"
    runout="$(gen_run "${FUNCNAME[0]} -i match abc" "$d/t" xxabcxx)"
    assert_eq "case9: -i 'aBc' still matches 'abc'" "match 2 5" "$runout"

    # ...and the same pattern WITHOUT -i must not: a compile option must not
    # leak into builds that did not request it
    pcrec_run "$PCREC" --emit-main -o - -- 'aBc' > "$d/gens.c" 2>/dev/null
    if gen_cc "${FUNCNAME[0]} (gens.c)" "$CC" $CFLAGS -o "$d/ts" "$d/gens.c"; then
        runout="$(gen_run "${FUNCNAME[0]} case-sensitive control" "$d/ts" xxABCxx)"
        assert_eq "case9: without -i, 'aBc' does NOT match 'ABC'" "nomatch" "$runout"
    else
        fail "case9: case-sensitive control build" "compile failed"
    fi

    # -i is listed in --help (an undiscoverable flag is a half-shipped one)
    assert_contains "case9: --help documents -i" "$(pcrec_run "$PCREC" --help)" "-i "

    # a pattern starting with '-' after `--` still parses as a pattern, not a flag
    pcrec_run "$PCREC" -i -o "$d/dash.c" -- '-i' 2>"$d/e_dash.txt"; rc=$?
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

    out="$(pcrec_run "$PCREC" --list-syntax 2>"$d/e.txt")"; rc=$?
    assert_eq "case10: --list-syntax exits 0" "0" "$rc" "stderr: $(cat "$d/e.txt")"
    assert_contains "case10: --list-syntax emits the column header" "$out" \
        "#kind	selector	syntax"

    # [SR-11] HEADER TRUTHFULNESS (docs/spec/table_contract.md, "The
    # checks"): every data row's field count equals the header's OWN
    # declared count — table_check_truthfulness, tests/lib/table.sh. This
    # is the durable form of the old `NF != 16` literal (12 until MOD-0.1
    # appended `roadmap`, `quantifiable`, `class_expect`, 2026-08-11; 16
    # since D65 appended `built`, 2026-08-21 —
    # docs/design/registry_built_status_memo.md): a literal count broke
    # the moment D65 landed, and this check compares against the header
    # instead, so the next appended column changes nothing here.
    printf '%s\n' "$out" > "$d/dump.tsv"
    nrows=$(grep -vc '^#' "$d/dump.tsv")
    if table_check_truthfulness "$d/dump.tsv" 2>"$d/truthfulness.err"; then
        nbad=0
    else
        nbad=$(grep -c '^table: .*:.* has ' "$d/truthfulness.err")
    fi
    assert_eq "case10: every dump row's field count matches the header's declared count (no tab leaked into one)" \
        "0" "$nbad" "rows: $nrows; $(cat "$d/truthfulness.err")"
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
    pcrec_run "$PCREC" --list-syntax --flavour pcre2 >"$d/o4.txt" 2>&1; rc=$?
    assert_eq "case10: --flavour pcre2 exits 0" "0" "$rc"
    assert_eq "case10: --flavour pcre2 selects every row" \
        "$nrows" "$(grep -vc '^#' "$d/o4.txt")"
    pcrec_run "$PCREC" --list-syntax --flavour python-re >"$d/o5.txt" 2>"$d/e5.txt"; rc=$?
    assert_eq "case10: an unknown flavour exits 1" "1" "$rc"
    assert_contains "case10: an unknown flavour is named in the error" \
        "$(cat "$d/e5.txt")" "unknown flavour 'python-re'"

    # a query compiles nothing, so mixing it with a compile is an error rather
    # than a silently-ignored half of the command line
    pcrec_run "$PCREC" --list-syntax -o - -- 'abc' >/dev/null 2>"$d/e6.txt"; rc=$?
    assert_eq "case10: --list-syntax with -o and a pattern exits 1" "1" "$rc"
    assert_contains "case10: ...and says which flag conflicts" \
        "$(cat "$d/e6.txt")" "takes no pattern and no -o"
    pcrec_run "$PCREC" --list-syntax --explain '\v' >/dev/null 2>"$d/e7.txt"; rc=$?
    assert_eq "case10: --list-syntax with --explain exits 1" "1" "$rc"
    pcrec_run "$PCREC" --flavour pcre2 -o - -- 'abc' >/dev/null 2>"$d/e8.txt"; rc=$?
    assert_eq "case10: --flavour without a query exits 1" "1" "$rc"
    pcrec_run "$PCREC" --explain >/dev/null 2>"$d/e9.txt"; rc=$?
    assert_eq "case10: --explain with no value exits 1" "1" "$rc"
    assert_contains "case10: ...with a missing-value diagnostic" \
        "$(cat "$d/e9.txt")" "missing value for --explain"

    # --list-verbs (Q1). A separate dump because the fifty verb NAMES are not
    # RegRows and --list-syntax's format is frozen by SR-4's generated doc
    # section. Four columns, and the row count is asserted as a FLOOR with a
    # named row required: a count alone would be satisfied by any fifty rows.
    out="$(pcrec_run "$PCREC" --list-verbs 2>"$d/ev.txt")"; rc=$?
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
    pcrec_run "$PCREC" --list-verbs --list-syntax >/dev/null 2>"$d/ev2.txt"; rc=$?
    assert_eq "case10: --list-verbs with --list-syntax exits 1" "1" "$rc"
    pcrec_run "$PCREC" --list-verbs -o - -- 'abc' >/dev/null 2>"$d/ev3.txt"; rc=$?
    assert_eq "case10: --list-verbs with -o and a pattern exits 1" "1" "$rc"

    # --list-families ([M6.6.2] wave F, D71 item 3). A THIRD dump, and it is a
    # dump rather than a change to --list-syntax for --list-verbs' reason one
    # level over: --list-syntax is PER-ROW and its consumers depend on that
    # (tests/reject/ probes every non-base row's own `syntax`), so the INDEX
    # layer's grouping gets its own view instead of collapsing theirs.
    out="$(pcrec_run "$PCREC" --list-families 2>"$d/ef.txt")"; rc=$?
    assert_eq "case10: --list-families exits 0" "0" "$rc" "stderr: $(cat "$d/ef.txt")"
    assert_contains "case10: --list-families emits the column header" "$out" \
        "#syntax	module	engines	status	built	nmembers	members"
    nfam="$(printf '%s\n' "$out" | grep -vc '^#')"
    nsyn="$(pcrec_run "$PCREC" --list-syntax | grep -vc '^#')"
    # THE TWO COUNTS MUST DIFFER, and the direction is the assertion: the
    # family view is the row view with multi-spelling constructs COLLAPSED, so
    # it must be SMALLER. Equal counts would mean the grouping had silently
    # stopped grouping — a view that prints one line per row while claiming to
    # print one per family is exactly as wrong as one that dropped rows, and
    # far quieter. A floor alone could not see it.
    if [ "$nfam" -lt 60 ] || [ "$nfam" -ge "$nsyn" ]; then
        fail "case10: --list-families printed $nfam lines against --list-syntax's $nsyn rows — a family view must be SMALLER than the row view (floor 60)"
    else
        pass "case10: --list-families printed $nfam family lines, collapsing $nsyn rows (floor 60, and strictly fewer than the rows)"
    fi
    # A MULTI-MEMBER FAMILY BY NAME, with its spellings. `(?=...)` is the one
    # this wave created and the one a regression would silently un-group.
    assert_contains "case10: --list-families groups the alpha spellings under their primary" "$out" \
        "(?=...)	lookaround	vm	module	built	3	(?=...) (*pla:a) (*positive_lookahead:a)"
    # Every line has exactly 7 tab-separated fields — the format is an
    # interface, same rule as the two dumps above.
    badfields="$(printf '%s\n' "$out" | grep -v '^#' | awk -F'\t' 'NF != 7' | head -3)"
    if [ -n "$badfields" ]; then
        fail "case10: --list-families rows without exactly 7 fields" "$badfields"
    else
        pass "case10: every --list-families row has exactly 7 tab-separated fields"
    fi
    pcrec_run "$PCREC" --list-families --list-syntax >/dev/null 2>"$d/ef2.txt"; rc=$?
    assert_eq "case10: --list-families with --list-syntax exits 1" "1" "$rc"
    pcrec_run "$PCREC" --list-families -o - -- 'abc' >/dev/null 2>"$d/ef3.txt"; rc=$?
    assert_eq "case10: --list-families with -o and a pattern exits 1" "1" "$rc"
    # No flavour axis, and for a reason of its own rather than by inheritance:
    # a family is a grouping OF rows, so filtering members would print families
    # whose membership depends on the filter and whose ANDed `built` would then
    # mean something different per invocation.
    pcrec_run "$PCREC" --list-families --flavour pcre2 >/dev/null 2>"$d/ef4.txt"; rc=$?
    assert_eq "case10: --list-families with --flavour exits 1" "1" "$rc"
    assert_contains "case10: ...and says where --flavour does apply" \
        "$(cat "$d/ef4.txt")" "--flavour applies to --list-syntax and --explain only"

    # [M6.6.2 wave F] A FORM ERROR IS THE DOORWAY'S ANSWER, NOT THE NAME'S
    # MODULE'S — and `--probe-ask` is the only channel that can see it.
    #
    # `(*pla)` is a real lower-table name in a form PCRE2 does not accept, and
    # PCRE2 decides that BEFORE it decides anything about modules. Wave F gave
    # the name `pla` a registry row of its own (module `lookaround`), and
    # mod_verbs.c does that lookup AFTER the form check so this stays true.
    #
    # THE REJECT TABLE CANNOT PIN IT, which is why the pin is here. That
    # table's row is message-only, and the form refusal's TEXT comes from the
    # VerbName table (`t->unknown_msg`) rather than from the elected row — so
    # it is byte-identical whichever side of the form check the lookup sits
    # on. MEASURED on a control build with the lookup moved: the message did
    # not move and this field did, `verdict` -> `result` under
    # `--features lookaround`. `answered_at == result` is D33's "the gate was
    # OPEN and the port had nothing to say" signal (and what D65 classifies
    # `built` on), so the control has a form error reporting itself as an
    # answer given with the module's gate open: wave F's own misattribution,
    # one level down.
    assert_eq "case10: a verb FORM error answers at VERDICT with its name's module DISABLED" \
        "verdict" "$(pcrec_run "$PCREC" --features none --probe-ask result -- '(*pla)' | cut -f3)"
    assert_eq "case10: ...and STILL at verdict with module lookaround ENABLED — the form check runs before the name's row is looked up" \
        "verdict" "$(pcrec_run "$PCREC" --features lookaround --probe-ask result -- '(*pla)' | cut -f3)"
    # The CONTRAST that makes the pair a measurement: the same name in a form
    # PCRE2 DOES accept reaches the name's row, so it answers at `result` with
    # the module enabled and at `verdict` with it disabled.
    assert_eq "case10: the same name in an ACCEPTED form answers at VERDICT with the module disabled" \
        "verdict" "$(pcrec_run "$PCREC" --features none --probe-ask result -- '(*pla:a)' | cut -f3)"
    assert_eq "case10: ...and at RESULT with module lookaround enabled — the second gate really is the NAME's row" \
        "result" "$(pcrec_run "$PCREC" --features lookaround --probe-ask result -- '(*pla:a)' | cut -f3)"

    # --count-groups (MOD-0.1, §18.1): the running capture count's external
    # channel — the surface tests/spec_mod0/check02 compares against libpcre2.
    # Expectations oracle-verified: python re agrees on every cell, and a
    # 300-pattern generated sweep at landing found zero disagreements.
    out="$(pcrec_run "$PCREC" --count-groups -- '(a)(b)(c)' 2>"$d/ec1.txt")"; rc=$?
    assert_eq "case10: --count-groups counts sibling groups" "0" "$rc" \
        "stderr: $(cat "$d/ec1.txt")"
    assert_eq "case10: ...and prints 3 for (a)(b)(c)" "3" "$out"
    assert_eq "case10: --count-groups counts nested groups" \
        "2" "$(pcrec_run "$PCREC" --count-groups -- '(a(b))')"
    assert_eq "case10: --count-groups does not count (?:...)" \
        "0" "$(pcrec_run "$PCREC" --count-groups -- '(?:a)')"
    assert_eq "case10: --count-groups on a groupless pattern is 0" \
        "0" "$(pcrec_run "$PCREC" --count-groups -- 'a|b')"
    # a refused construct refuses here too, with the compile diagnostic —
    # leftmost refusal, no count for a pattern pcrec does not fully know
    pcrec_run "$PCREC" --count-groups -- '(?<n>a)' >/dev/null 2>"$d/ec2.txt"; rc=$?
    assert_eq "case10: --count-groups refuses what pcrec refuses" "1" "$rc"
    assert_contains "case10: ...with the construct's own diagnostic" \
        "$(cat "$d/ec2.txt")" "requires module 'named-groups'"
    pcrec_run "$PCREC" --count-groups -o - -- 'a' >/dev/null 2>"$d/ec3.txt"; rc=$?
    assert_eq "case10: --count-groups with -o exits 1" "1" "$rc"
    pcrec_run "$PCREC" --count-groups >/dev/null 2>"$d/ec4.txt"; rc=$?
    assert_eq "case10: --count-groups without a pattern exits 1" "1" "$rc"

    # --probe-ask (MOD-0.1, §18.2): the cursor-rule channel — one doorway call
    # at a chosen want level, real cursor reported before and after. The
    # comparison over every row belongs to tests/spec_mod0's check06 (a D27
    # author); what is pinned HERE is the surface: the exact line for one
    # known cell, the field count, the gate demotion being visible, and the
    # in-repo cursor sweep with a FLOORED population (an empty sweep prints
    # the same silence as a passing one, so the count is asserted).
    out="$(pcrec_run "$PCREC" --probe-ask verdict -- '\d' 2>"$d/ep1.txt")"; rc=$?
    assert_eq "case10: --probe-ask verdict runs" "0" "$rc" \
        "stderr: $(cat "$d/ep1.txt")"
    assert_eq "case10: ...and reports the escape doorway cell exactly" \
        "escape	verdict	verdict	2	2	refusal	0	0	0	\\d requires module 'classes'" \
        "$out"
    assert_eq "case10: --probe-ask line has 10 fields" \
        "10" "$(printf '%s\n' "$out" | awk -F'\t' '{print NF}')"
    # the §5.4 gate, observable: a `result` ask is ANSWERED at `verdict`
    # while no module is enabled — the day one is, this cell changes and
    # this assertion must be revisited alongside check07.
    # [STD1b] (D37, 2026-08-13): that day arrived for the BARE invocation
    # too (`classes` is default-on now), so this cell now needs
    # `--features none` to keep exercising "no module enabled" — the bare
    # cell itself is exercised by case14's byte-identity-with-std1 pin.
    assert_eq "case10: --probe-ask result is answered at verdict (the gate)" \
        "verdict" "$(pcrec_run "$PCREC" --features none --probe-ask result -- '\d' | cut -f3)"
    # ...and that day arrived (MOD-0.3c): with module classes ENABLED the
    # same ask reaches `result` and the outcome word is the PRODUCING
    # vocabulary — both cells were false the day before the producers wired
    # in (D33 §9.3), and the doorway still must not move the cursor even
    # when producing (fields 4/5 equal; the CALLER moves at result).
    # [M6.5.2] THE `end` FIELD (the ninth) MOVED 0 -> 2, and it is a fix
    # rather than a drift. `ExtResult.end` is "one past the construct", the
    # value the CALLER advances to at RESULT — and this branch (the escape
    # doorway's own SET port) left it at the zero-initialiser while `esc_atom`
    # compensated by assuming every atom producer's construct is exactly the
    # two-byte escape. Module `backrefs` has atom constructs that are longer
    # (`\k<name>`, `\g{-1}`, an octal re-read), so `esc_atom` now advances to
    # whatever the producer reports, and a producer that reports 0 would rewind
    # the cursor to the start of the pattern. The cursor fields (4 and 5) are
    # UNCHANGED at 2 and 2, which is the property this cell exists for: the
    # doorway still does not move `cx->pos` even when producing.
    assert_eq "case10: --features classes --probe-ask result produces a node" \
        "escape	result	result	2	2	node	0	0	2	" \
        "$(pcrec_run "$PCREC" --features classes --probe-ask result -- '\d')"
    assert_eq "case10: ...and the posix class produces members, cursor unmoved" \
        "class-bracket	result	result	1	1	members	1	0	10	" \
        "$(pcrec_run "$PCREC" --features classes --probe-ask result -- '[[:alpha:]]')"
    # full-text coordinates for a prefixed construct (the ten (?-N) rows)
    assert_eq "case10: --probe-ask reports full-text cursor coordinates" \
        "4	4" "$(pcrec_run "$PCREC" --probe-ask verdict -- '(a)(?-1)' | cut -f4,5)"
    # THE CURSOR SWEEP: every registry row's syntax, claim and verdict, and
    # the cursor must not move (§18.2's hard rule; WANT_RESULT is the only
    # level allowed to move it — and the producing ports that exist since
    # MOD-0.3/MOD-0.5 (classes, modifiers) return it unmoved too, carrying
    # `end` for the CALLER to advance, check06's rule — so this sweep's
    # claim/verdict limit is caution, not a live dependency). (?:...)
    # is the one deliberate non-route: the base grammar answers it before
    # any doorway, so there is no call to probe.
    #
    # [M6.4.2] THE NON-ROUTING SET GREW BY FOUR, and for a DIFFERENT reason
    # than `(?:...)`'s, which is why it is now asserted as a SET rather than a
    # count: `(?:` reaches a doorway's byte and the base grammar answers FIRST,
    # while the four possessive-suffix rows (kind `quant-suffix`) reach NO
    # DOORWAY AT ALL — the possessive `+` is a quantifier suffix recognised
    # inside `p_rep`, and src/parse/registry.c's header records why giving it a
    # doorway would cost the base tier a lookup on every quantifier. A count
    # alone would be satisfied by the WRONG four rows dropping out.
    local swept=0 moved=0 noroute=0
    local noroute_set="" noroute_expect
    # Space-joined on ONE line: assert_eq reports a mismatch as two values and
    # a multi-line value makes the report unreadable at exactly the moment it
    # matters.
    #
    # `LC_ALL=C` ON BOTH SIDES, AND IT IS NOT DEFENSIVE PADDING. Under the
    # default locale `sort` collates by dictionary rules that treat punctuation
    # as ignorable, so `a?+` and `a++` compare EQUAL and `sort -u` SILENTLY
    # DROPS ONE — measured here: the set came back four-membered with a`?`+
    # missing while the count beside it correctly read 10. A set assertion that
    # can lose a member is worse than the count it replaced.
    noroute_expect="$(printf '%s\n' '(?:...)' 'a*+' 'a++' 'a?+' 'a{1,2}+' | LC_ALL=C sort | tr '\n' ' ')"
    while IFS= read -r syn; do
        for w in claim verdict; do
            if line="$(pcrec_run "$PCREC" --probe-ask "$w" -- "$syn" 2>/dev/null)"; then
                swept=$((swept + 1))
                [ "$(printf '%s\n' "$line" | cut -f4)" = \
                  "$(printf '%s\n' "$line" | cut -f5)" ] || {
                    moved=$((moved + 1))
                    fail "case10: cursor moved under $w" "$syn: $line"
                }
            else
                noroute=$((noroute + 1))
                noroute_set="$noroute_set$syn
"
            fi
        done
    done < <(grep -v '^#' "$d/dump.tsv" | cut -f3)
    if [ "$swept" -ge 198 ] && [ "$moved" -eq 0 ]; then
        pass "case10: cursor unchanged below WANT_RESULT over $swept probes (floor 198)"
    else
        fail "case10: cursor sweep" "swept=$swept (floor 198) moved=$moved"
    fi
    assert_eq "case10: exactly the named rows reach no doorway" \
        "$noroute_expect" \
        "$(printf '%s' "$noroute_set" | grep . | LC_ALL=C sort -u | tr '\n' ' ')"
    # TWO probes per row (claim and verdict), so the count is 2x the set.
    assert_eq "case10: ...and each of them was probed at both want levels" \
        "10" "$noroute"
    # channel-cannot-run is exit 1 and distinct from a measured refusal
    pcrec_run "$PCREC" --probe-ask verdict -- 'abc' >/dev/null 2>"$d/ep2.txt"; rc=$?
    assert_eq "case10: --probe-ask on non-doorway text exits 1" "1" "$rc"
    assert_contains "case10: ...and explains the (?: exclusion" \
        "$(cat "$d/ep2.txt")" "base grammar answers"
    pcrec_run "$PCREC" --probe-ask sideways -- '\d' >/dev/null 2>&1; rc=$?
    assert_eq "case10: an unknown want level exits 1" "1" "$rc"
    pcrec_run "$PCREC" --probe-ask verdict -o - -- '\d' >/dev/null 2>&1; rc=$?
    assert_eq "case10: --probe-ask with -o exits 1" "1" "$rc"
    pcrec_run "$PCREC" --probe-ask verdict >/dev/null 2>&1; rc=$?
    assert_eq "case10: --probe-ask without a construct exits 1" "1" "$rc"
    pcrec_run "$PCREC" --probe-ask verdict --list-syntax >/dev/null 2>&1; rc=$?
    assert_eq "case10: --probe-ask with --list-syntax exits 1" "1" "$rc"

    # --features (MOD-0.1, slice 9): the enabled set. No module has ports yet,
    # so the ONLY observable today is the gate's state through --probe-ask's
    # answered_at — result stays result where the row's module is enabled,
    # demotes to verdict where it is not — and verdicts must not move at all
    # (check07's subject; one spot pin here).
    assert_eq "case10: --features all opens the gate (answered_at result)" \
        "result" "$(pcrec_run "$PCREC" --features all --probe-ask result -- '\d' | cut -f3)"
    assert_eq "case10: --features is per-module, not a blanket switch" \
        "verdict" "$(pcrec_run "$PCREC" --features backrefs --probe-ask result -- '\d' | cut -f3)"
    assert_eq "case10: an open gate does not move the cursor either" \
        "2	2" "$(pcrec_run "$PCREC" --features all --probe-ask result -- '\d' | cut -f4,5)"
    # The MOD-0.1-era pin that stood here — "an open gate changes no verdict
    # text" — EXPIRED the day the first producer landed (MOD-0.3c), exactly
    # as its neighbour comment predicted ("the day one is, this cell changes
    # and this assertion must be revisited alongside check07"). Successor:
    # the open gate now changes the OUTCOME for a producing row, in exactly
    # one way — refusal -> produced node, diagnostic emptied — while the
    # closed gate keeps the refusal text verbatim.
    assert_eq "case10: an open gate now PRODUCES where the closed one refuses" \
        "node	" \
        "$(pcrec_run "$PCREC" --features all --probe-ask result -- '\d' | cut -f6,10)"
    # [STD1b]: `\d`'s own module (`classes`) is open by DEFAULT now, so a
    # bare probe would produce too — `--features none` is what still shows
    # the closed-gate refusal verbatim (bare's own "produces, same as
    # std1" fact is case14's job).
    assert_eq "case10: ...and the closed gate keeps the refusal verbatim" \
        "refusal	\d requires module 'classes'" \
        "$(pcrec_run "$PCREC" --features none --probe-ask result -- '\d' | cut -f6,10)"
    pcrec_run "$PCREC" --features nosuchmodule --probe-ask result -- '\d' \
        >/dev/null 2>"$d/ef1.txt"; rc=$?
    assert_eq "case10: an unknown module name in --features exits 1" "1" "$rc"
    assert_contains "case10: ...and is refused BY NAME" \
        "$(cat "$d/ef1.txt")" "unknown module 'nosuchmodule'"
    # a BASE-TIER compile under --features all emits byte-identical MATCHER
    # code to one without: the gate exists for module rows only and must
    # never perturb a base pattern's compile path (this pin's original "no
    # ports exist" rationale expired at MOD-0.3c; the base-tier half is the
    # part that must stay true forever).
    # SAME BASENAME in different directories — the emitted C embeds the
    # output basename in its #include (the journal's twice-paid lesson)
    #
    # [STD1] phase A (D37) makes the file's OWN FIRST LINES differ on
    # purpose: the artifact stamp reports the REQUESTED set, by design,
    # regardless of whether this particular base-tier pattern's matcher
    # uses any of it — that is what makes the stamp trustworthy as a
    # reproduction recipe (a "none"-stamped artifact must mean the compile
    # really asked for none). So the comparison below skips exactly the
    # stamp block (pattern comment + feature comment + the two feature
    # macros — 4 lines) and asserts identity on everything after it, which
    # is the part this pin has always been about: the MATCHER.
    # [STD1b]: `fa` used to be generated BARE to get the "none" stamp — bare
    # now stamps 'std1' instead (D37's whole point: the stamp reports the
    # REQUESTED set honestly, and the request itself changed). `--features
    # none` is what still requests, and stamps, 'none'; the MATCHER-identity
    # claim below is unaffected either way, since a base-tier pattern like
    # 'a(b|c)+d' never engages the gate regardless of which set is named.
    mkdir -p "$d/fa" "$d/fb"
    pcrec_run "$PCREC" --features none -o "$d/fa/feat.c" -- 'a(b|c)+d' 2>/dev/null
    pcrec_run "$PCREC" --features all -o "$d/fb/feat.c" -- 'a(b|c)+d' 2>/dev/null
    if cmp -s <(tail -n +5 "$d/fa/feat.c") <(tail -n +5 "$d/fb/feat.c"); then
        pass "case10: --features all compiles byte-identical MATCHER code (stamp lines 1-4 differ on purpose, D37)"
    else
        fail "case10: --features all changed emitted MATCHER code with no ports built"
    fi
    if grep -q '^/\* Feature set: none' "$d/fa/feat.c" \
       && grep -q '^/\* Feature set: all' "$d/fb/feat.c"; then
        pass "case10: ...and the stamp itself DOES differ, honestly reporting what was requested"
    else
        fail "case10: the stamp did not report the two different requested sets" \
            "$(head -2 "$d/fa/feat.c") / $(head -2 "$d/fb/feat.c")"
    fi

    # an undiscoverable flag is a half-shipped one (case9's rule, applied here)
    out="$(pcrec_run "$PCREC" --help)"
    assert_contains "case10: --help documents --list-syntax" "$out" "--list-syntax"
    assert_contains "case10: --help documents --list-verbs" "$out" "--list-verbs"
    assert_contains "case10: --help documents --explain" "$out" "--explain"
    assert_contains "case10: --help documents --count-groups" "$out" "--count-groups"
    assert_contains "case10: --help documents --probe-ask" "$out" "--probe-ask"
    assert_contains "case10: --help documents --features" "$out" "--features"

    # `--` still ends options: a pattern that looks like a query is a pattern
    pcrec_run "$PCREC" -o "$d/dash.c" -- '--list-syntax' 2>"$d/e10.txt"; rc=$?
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
#     WHAT THIS CASE CANNOT REACH (docs/design/design_notes_mod07.md section 9.4 —
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
    # [STD1b] (D37, 2026-08-13): `modifiers` is default-on now, so a genuinely
    # bare `--explain '(?i-m:'` no longer stops at "requires module
    # 'modifiers'" — it reaches the module's OWN parse of the (malformed,
    # truncated) run and answers "missing closing ) for group" instead, a
    # different worked example entirely. `--features none` is what still
    # walks through D29's original example step by step.
    out="$(pcrec_run "$PCREC" --features none --explain '(?i-m:' 2>"$d/e1.txt")"; rc=$?
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
    out="$(pcrec_run "$PCREC" --explain '(?<')"
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

    out="$(pcrec_run "$PCREC" --explain '\N{U+0041}')"
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

    # --- [M4-CALLOUTS] step 1 (D36, flipped 2026-08-14): (?C1) is now a
    # PLANNED module row, not ROADMAP_NEVER. This block used to pin the
    # ROADMAP_NEVER shape (K14, MOD-0.7a); it now pins the post-flip shape —
    # a module row like any other, promising 'callouts'. The `agree` clause
    # still cannot independently verify attribution (both its sides read the
    # row), so this hand-written pin is still the only net.
    out="$(pcrec_run "$PCREC" --explain '(?C1)')"
    assert_field "case11: (?C1) carries roadmap planned" "$out" "(?C1)" \
        "roadmap" "planned"
    assert_field "case11: (?C1)'s status promises module callouts" "$out" \
        "(?C1)" "status" \
        "known, unimplemented — requires module 'callouts'"
    assert_field "case11: ...the row records its module" \
        "$out" "(?C1)" "module" "callouts"
    assert_field "case11: ...the live answer promises it" "$out" "(?C1)" \
        "own names" "callouts"
    assert_field "case11: ...and that is agreement, not a dissent" "$out" \
        "(?C1)" "agree" "ok"

    # --- the class-bracket doorway, and a DECLARED class expectation --------
    out="$(pcrec_run "$PCREC" --explain '[[:alpha:]]')"
    assert_field "case11: [[:alpha:]] is module classes" "$out" "[[:alpha:]]" \
        "module" "classes"
    assert_field "case11: ...blamed at pcrec's own offset" "$out" "[[:alpha:]]" \
        "own at" "1"
    out="$(pcrec_run "$PCREC" --explain '\d')"
    assert_field "case11: \d's class expectation is DECLARED from the row" \
        "$out" '\d' "class" "set 10"
    assert_field "case11: \d carries the PCRE2 semantics note" "$out" '\d' \
        "note" "any decimal digit"
    out="$(pcrec_run "$PCREC" --explain '\v')"
    assert_field "case11: \v is module classes" "$out" '\v' "module" "classes"
    assert_field "case11: \v's note is the measured PCRE2 semantics" "$out" '\v' \
        "note" \
        "any vertical whitespace character (NOT vertical tab; python re disagrees)"

    # --- QUERY CELLS whose live answer differs from the row's declaration ---
    # Five measured cells where that is CORRECT. Pinned as correct so a future
    # reader does not "fix" them into agreement.
    out="$(pcrec_run "$PCREC" --explain '\p{Foo}')"
    assert_field "case11: \p{Foo} gets mod_uprops' refined refusal" "$out" \
        "@header" "live" "\p requires module 'unicode-props'"
    # K16: this offset is PCREC'S OWN behaviour (stability, not oracle
    # agreement) — 164 of 256 body bytes are libpcre2 err-146 AT THE BYTE while
    # pcrec's scanner reads past them. The K16 fix lands with the first
    # unicode-props producer and MOVES this number; it is pinned so the move is
    # deliberate rather than silent.
    assert_field "case11: ...at pcrec's own scan-completion offset (K16)" \
        "$out" "@header" "live at" "7"
    out="$(pcrec_run "$PCREC" --explain '(*NOTAVERB)')"
    assert_field "case11: an unknown verb NAME promises no module" "$out" \
        "@header" "live" "(*VERB) not recognized or malformed"
    assert_field "case11: ...even though the one verb ROW declares one" "$out" \
        "(*ACCEPT)" "module" "verbs"
    assert_field "case11: ...and the name table says it is not known" "$out" \
        "verb name NOTAVERB" "known" "no"
    assert_field "case11: ...naming the table PCRE2 would have consulted" \
        "$out" "verb name NOTAVERB" "table" "upper"
    out="$(pcrec_run "$PCREC" --explain '(*ACCEPT)')"
    assert_field "case11: a known verb name reports its measured forms" "$out" \
        "verb name ACCEPT" "forms" "(*N)|(*N:a)|(*N:)"
    assert_field "case11: ...and where its roadmap came from" "$out" \
        "verb name ACCEPT" "roadmap src" "inherited from the (* row"
    out="$(pcrec_run "$PCREC" --explain '[[:foo:]]')"
    assert_field "case11: an unknown POSIX name promises no module" "$out" \
        "@header" "live" "unknown POSIX class name"
    assert_field "case11: ...while its row is still module classes" "$out" \
        "[[:alpha:]]" "module" "classes"
    out="$(pcrec_run "$PCREC" --explain '[[:<:]]')"
    assert_field "case11: a whole-class-only name names ANOTHER module" "$out" \
        "@header" "live names" "assertions"
    out="$(pcrec_run "$PCREC" --explain '(?iZ)')"
    assert_field "case11: a malformed option RUN promises no module" "$out" \
        "@header" "live" "unrecognized character after (? or (?-"
    # ...and the elected row is still the option row: `elected` is the row the
    # doorway DISPATCHED on, not the row that wrote the message
    assert_field "case11: ...but the (?i) row was still the one elected" "$out" \
        "@header" "live elected" "(?i)"

    # --- the gate axis: --features changes what the doorway DOES ------------
    out="$(pcrec_run "$PCREC" --features classes --explain '\d')"
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
    #
    # [M6.3] (2026-08-18) split what was ONE shared cell into two, and this
    # is the deliberate half, not a weakening of it: `(?J)`'s per-letter
    # answer used to name module 'named-groups' honestly (the module did
    # not exist yet, so "requires module 'named-groups'" was true). Once
    # named-groups actually SHIPPED without (?J)/DUPNAMES — a ruled scope
    # exclusion, docs/dev/plan.md's [M6.3] row — that same sentence would
    # have started being a LIE the moment the module landed, so
    # mod_modifiers.c's 'J' case moved to K14's ROADMAP_NEVER wording (no
    # module promised) instead. `(?m)` is untouched: `assertions` has not
    # shipped, so its per-letter promise is still true and still pinned the
    # original way. The comment this replaces said the point was "the fix
    # must not become dropping the interesting field" — that principle
    # still holds; what changed is which answer IS the honest one for `J`.
    out="$(pcrec_run "$PCREC" --features modifiers --explain '(?m)' 2>"$d/e3.txt")"; rc=$?
    assert_eq "case11: an open gate does not make (?m) dissent" "0" "$rc" \
        "stderr: $(cat "$d/e3.txt")"
    assert_field "case11: ...(?m)'s row agrees" "$out" "(?m)" "agree" "ok"
    assert_field "case11: ...and the header counts no dissent for (?m)" \
        "$out" "@header" "dissents" "0"
    # the per-LETTER module is still SHOWN. This is the pin that stops the
    # fix being "make the two sides agree by dropping the interesting
    # one": the displayed answer must keep naming the letter's module.
    assert_field "case11: ...while (?m)'s own answer still names the letter's module" \
        "$out" "(?m)" "own names" "assertions"
    assert_field "case11: ...and the row still declares its own" \
        "$out" "(?m)" "module" "modifiers"

    out="$(pcrec_run "$PCREC" --features modifiers --explain '(?J)' 2>"$d/e3.txt")"; rc=$?
    assert_eq "case11: an open gate does not make (?J) dissent" "0" "$rc" \
        "stderr: $(cat "$d/e3.txt")"
    assert_field "case11: ...(?J)'s row agrees" "$out" "(?J)" "agree" "ok"
    assert_field "case11: ...and the header counts no dissent for (?J)" \
        "$out" "@header" "dissents" "0"
    # [M6.3], THIRD WORDING (manager ruling, citing the ratified D38
    # PCRE2_DUPNAMES row and docs/pcre2_compliance.md's own REJECTED/
    # planned status for (?J) — not OUT-OF-SCOPE): the letter's own answer
    # names its TRUE owning module, `named-groups` (duplicate NAMES are
    # named-group semantics, same dispatch logic 'm' already uses for
    # 'assertions'), without the false "requires" framing — "requires
    # module 'named-groups'" would read as "enabling it fixes this", which
    # is false since named-groups ships without dupnames support.
    #
    # [M6.5.2] FOURTH AND — because the letter is now BUILT — LAST: the owner
    # is `backrefs` (ASK-1, ruled with R32). Wording 3 was right about the
    # DECLARING half and silent about the RESOLVING one, and it is the
    # resolution rule for a reference to a duplicated name that makes the
    # letter mean anything at all. The split the compliance page records:
    # declaring a duplicate name is `named-groups`; resolving a reference to
    # one, and this letter, are `backrefs`. The "requires" framing comes
    # BACK with it and is now true — enabling `backrefs` does fix this — which
    # is the property wording 1 lacked and the reason it had to go.
    assert_field "case11: ...while (?J)'s own answer names its true owning module" \
        "$out" "(?J)" "own names" "backrefs"
    assert_field "case11: ...and the row still declares its own" \
        "$out" "(?J)" "module" "modifiers"

    # --- THE NULL CONTRACT (R20/MOD07-4+5): NULL <=> answered without a row -
    # `ExtResult.row` named three no-row cases and was WRONG about two of
    # them. Both doorways stamp the elected row at the point of LOOKUP, and
    # both then have a later path that answers without consulting it: the `(?`
    # doorway's c2 < 0 branch (R17's end-of-pattern fix — c2 == -1 aliases
    # REG_SEL_ANY, so the catch-all is stamped and then walked past), and the
    # class-bracket delimiter-scan decline (stamped before the scan runs). So
    # "NULL => no row" held and the converse did not, and the display asserted
    # elections that never happened. Written failing first; the verbatim block
    # is in the slice's commit message.
    out="$(pcrec_run "$PCREC" --explain '(?')"
    assert_field "case11: '(?' at end of pattern elected NO row" "$out" \
        "@header" "live elected" "none"
    # ...and MOD07-5 falls out of the same fix: `fallback` means "the
    # arbitration actually elected the catch-all here", so tagging it on a
    # query the catch-all never won asserted a reachability nothing exercised.
    # The row is still SHOWN — the prefix rule finds it, which is what
    # `listed` says.
    assert_field "case11: ...so the catch-all is 'listed', not an election" \
        "$out" "(?q)" "select" "listed"
    # 45 -> 50 at [DD-14] wave F: the five byte-keyed `(?` INDEX rows
    # (`(?10)`, `(?01)`, `(?00)`, `(?+2)(a)(b)`, `(a)x10(?-10)`), which the
    # `(?` prefix rule finds exactly as it finds every other row in the
    # bucket. They are SHOWN and never ELECTED — see the exempt split below.
    assert_eq "case11: ...and the row set is unchanged by the retagging" "50" \
        "$(explain_field "$out" "@header" "rows")"
    out="$(pcrec_run "$PCREC" --explain '[[:alpha]')"
    assert_field "case11: an unclosed delimiter pair DECLINES" "$out" \
        "@header" "live" "declines — no construct at this doorway"
    assert_field "case11: ...having elected no row either" "$out" \
        "@header" "live elected" "none"

    # --- the base-grammar row: an honest non-answer, not a fabricated one ---
    out="$(pcrec_run "$PCREC" --explain '(?:')"; rc=$?
    assert_eq "case11: --explain '(?:' exits 0" "0" "$rc"
    assert_field "case11: (?: has no doorway call to report" "$out" "@header" \
        "route" \
        "none — the base grammar answers this text before any doorway is consulted"
    assert_field "case11: ...and its row says so rather than passing silently" \
        "$out" "(?:...)" "agree" "ok  (base grammar; no doorway call to compare)"
    assert_field "case11: ...it is a prefix match, not a bucket candidate" \
        "$out" "(?:...)" "select" "listed"

    # --- `rows 0`: a ROUTED query that selects nothing (R20/MOD07-6) --------
    # The design note called this branch "impossible today; every routed query
    # yields at least the elected row". Measured: 87 of the 127 `\<byte>`
    # queries display it, because an unknown escape elects no row and no row's
    # `syntax` shares a prefix with it. The branch had ZERO assertions until
    # now — which is how a live, common output shape stayed described as
    # unreachable.
    out="$(pcrec_run "$PCREC" --explain '\q' 2>"$d/e5.txt")"; rc=$?
    assert_eq "case11: a routed query that selects no rows still exits 0" "0" "$rc" \
        "stderr: $(cat "$d/e5.txt")"
    assert_field "case11: ...reporting rows 0" "$out" "@header" "rows" "0"
    assert_field "case11: ...with the live block still answered" "$out" \
        "@header" "live" "unknown escape \q"
    assert_field "case11: ...electing no row" "$out" "@header" "live elected" "none"
    assert_field "case11: ...and no dissent, there being nothing to dissent" \
        "$out" "@header" "dissents" "0"

    # --- CONTROL BYTES IN THE ECHO (R20/MOD07-8) ---------------------------
    # The format grammar had no escaping, so a query containing a newline
    # injected a synthetic header line that `explain_field` — the helper right
    # above, parsing this same format — read as real. Measured before the fix:
    # this query reported `rows 99`. No attacker involved; it is the
    # operator's own text, so the cure is a visible rendering (`\xHH` for
    # bytes below 0x20 and 0x7f), not a quoting scheme.
    out="$(pcrec_run "$PCREC" --explain "$(printf '\\\nrows           99\n')" 2>/dev/null)"
    assert_field "case11: an injected header line does not become a field" \
        "$out" "@header" "rows" "0"
    # (command substitution strips the trailing newline, so the query is
    # `\` + LF + `rows           99` — the leading `\` is the query's own,
    # deliberately NOT doubled: only control bytes are escaped)
    assert_field "case11: ...the newline is rendered visibly in the echo" \
        "$out" "@header" "query" '\\x0arows           99'
    # ...and the same bytes reaching the ANSWER text are escaped too: the
    # refusal renders the selector byte into its own sentence, so escaping
    # only the echo would leave the injection reachable one line down.
    assert_field "case11: ...and in the live answer that embeds the byte" \
        "$out" "@header" "live" 'unknown escape \\x0a'
    out="$(pcrec_run "$PCREC" --explain "$(printf '(?\t)')" 2>/dev/null)"
    assert_field "case11: a control byte in the SELECTOR echo is escaped" \
        "$out" "@header" "route" "after '(?'  selector '\\x09'"

    # --- the unanswerable query keeps its exit 1 and its message ------------
    pcrec_run "$PCREC" --explain 'a' >"$d/o2.txt" 2>"$d/e2.txt"; rc=$?
    assert_eq "case11: --explain on base syntax exits 1" "1" "$rc"
    assert_contains "case11: ...and says why" "$(cat "$d/e2.txt")" \
        "no construct matches"

    # --- THE FLOORED SWEEPS -------------------------------------------------
    # An empty sweep prints the same silence as a passing one, so the
    # populations are asserted. Every displayed row must win its OWN syntax and
    # agree; the ONE exception is the single RS_BASE row, whose syntax reaches
    # no doorway.
    local blocks=0 selfel=0 agreed=0 exempt=0 idxel=0 answered=0 q
    local queries=('\v' '\d' '\N{U+0041}' '(?<' '(?P' '(?i-m:' '(?iZ)' '(?C1)'
                   '(?(1)' '(?-1)' '[[:alpha:]]' '[[.a.]]' '[[:foo:]]'
                   '(*ACCEPT)' '(*NOTAVERB)' '\p{Foo}' '(?' '(?:' '\Q')
    for q in "${queries[@]}"; do
        out="$(pcrec_run "$PCREC" --explain "$q" 2>/dev/null)" || continue
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
                  # [DD-14 wave F] THREE buckets, not two. A block that
                  # elects neither `self` nor `—` is a byte-keyed INDEX row
                  # electing its PRIMARY, which is what an index row is for
                  # (D71 item 3) and is a DIFFERENT fact from the RS_BASE
                  # row's "reaches no doorway at all". Folding them together
                  # would let either population grow behind the other's
                  # number.
                  if [ "$v" = "self" ]; then selfel=$((selfel + 1))
                  elif [ "$v" = "—" ]; then exempt=$((exempt + 1))
                  else idxel=$((idxel + 1)); fi ;;
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
    # THE EXEMPT COUNT, ASSERTED EXACTLY (R20/MOD07-7). The conjunct that
    # stood here was `selfel == blocks - exempt`, which is a TAUTOLOGY: the
    # loop above increments exactly one of the two per block, so their sum is
    # `blocks` by construction and the test could not fail. Beside it sat
    # `exempt <= 3` with no explanation of the 3.
    #
    # SELF-ELECTION IS NOT UNASSERTED AS A RESULT — it is asserted by the
    # agreement sweep this loop duplicates: clause 1 DISSENTS when a row's own
    # syntax does not elect that row, and the sweep above requires every block
    # to agree. What was left genuinely unchecked is the size of the EXCEPTION
    # set, so that is what this now pins, exactly rather than as a tolerance.
    #
    # WHY 2: exactly one registry row (`(?:...)`, the single RS_BASE row)
    # reaches no doorway, and it appears in two of the 19 queries — `(?` finds
    # it by prefix, `(?:` by both rules. A third exempt block would mean a row
    # stopped electing itself while still reporting agreement, which is the
    # one combination the two sweeps cannot produce together.
    #
    # [DD-14 wave F] AND WHY 5 INDEX-ELECTED, counted SEPARATELY. Module
    # `recursion`'s five byte-keyed `(?` index rows appear in the `(?` prefix
    # query and each elects its PRIMARY — `(?10)` elects `(?1)`, `(?01)`
    # elects `(?0)` (the family and the dispatch differ, which is the whole
    # point of the split). They are not "exempt": their election is ASSERTED,
    # by `put_agreement`'s own index-row clause, which requires a real row of
    # the SAME MODULE. What is pinned here is the SIZE of that population, so
    # a sixth byte-keyed index row cannot arrive unremarked and neither can
    # one that quietly stopped being shown.
    if [ "$exempt" -eq 2 ] && [ "$idxel" -eq 5 ] &&
       [ "$selfel" -eq $((blocks - 7)) ]; then
        pass "case11: exactly $exempt blocks are base-grammar exempt and $idxel are index rows electing their primary ($selfel/$blocks elected their own row)"
    else
        fail "case11: election sweep" \
             "exempt=$exempt (want exactly 2: the RS_BASE row in 2 queries)" \
             "idxel=$idxel (want exactly 5: the byte-keyed (? index rows)" \
             "self=$selfel blocks=$blocks"
    fi
    # and no query on the shipped table may exit 3
    local dissenting=0
    for q in "${queries[@]}"; do
        pcrec_run "$PCREC" --explain "$q" >/dev/null 2>&1
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
    out="$(pcrec_run "$PCREC" --explain '\v')"
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
    pcrec_run "$PCREC" --features modifiers --explain '(?i:[)' \
        >"$d/o1.txt" 2>"$d/e1.txt"; rc=$?
    assert_clean_failure \
        "case12: --explain survives a port that ctx_fails" "$rc" "$d/e1.txt"
    pcrec_run "$PCREC" --features all --probe-ask result -- '(?i:[)' \
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
    # [STD1b]: `modifiers` is default-on now, so a bare invocation of this
    # same text reaches the SAME crashing-port path the two cells above
    # already exercise (with `--features modifiers`/`all` explicitly) —
    # `--features none` is what still demonstrates the CLOSED-gate case
    # this section is actually about.
    out="$(pcrec_run "$PCREC" --features none --explain '(?i:[)' 2>"$d/e3.txt")"; rc=$?
    assert_eq "case12: closed-gate --explain of the same text exits 0" "0" "$rc" \
        "stderr: $(cat "$d/e3.txt")"
    assert_field "case12: ...and answers with the module refusal" "$out" \
        "@header" "live" "(?i...) requires module 'modifiers'"
    out="$(pcrec_run "$PCREC" --features none --probe-ask result -- '(?i:[)' 2>"$d/e4.txt")"; rc=$?
    assert_eq "case12: closed-gate --probe-ask of the same text exits 0" "0" "$rc" \
        "stderr: $(cat "$d/e4.txt")"
    assert_eq "case12: ...reporting a refusal, not an error" "refusal" \
        "$(cut -f6 <<<"$out")"

    # --- the OPEN gate, WELL-FORMED body: production is untouched ---------
    # The positive control for the guard itself: a setjmp that swallowed
    # every open-gate answer would pass both crash pins above.
    out="$(pcrec_run "$PCREC" --features modifiers --explain '(?i:a)' 2>"$d/e5.txt")"; rc=$?
    assert_eq "case12: an open gate still answers a well-formed body" "0" "$rc" \
        "stderr: $(cat "$d/e5.txt")"
    assert_field "case12: ...by PRODUCING" "$out" "@header" "live" \
        "produces an AST node"
    assert_field "case12: ...answered at result" "$out" "@header" \
        "live answered" "result"
    out="$(pcrec_run "$PCREC" --features all --probe-ask result -- '(?i:a)' 2>"$d/e6.txt")"; rc=$?
    assert_eq "case12: --probe-ask likewise" "0" "$rc" \
        "stderr: $(cat "$d/e6.txt")"
    assert_eq "case12: ...reporting the produced node" "node" \
        "$(cut -f6 <<<"$out")"
}

# ---------------------------------------------------------------------------
# 13. THE ENCODING GATE (-e), which nothing in this repository covered until
#     MOD-0.8c slice 3 — `grep -rn '\-e utf8' tests/` found nothing at all, so
#     the one gate the CLI has besides --features was entirely unpinned.
#
#     The finding it closes is K14's shape on that gate (R20, the D27 blinded
#     writer's divergence 5): pcrec answered "encoding 'utf8' requires module
#     'utf8'", and the module namespace has no 'utf8' — `--features utf8` says
#     so itself. The one actionable noun in the diagnostic pointed at a name
#     the only surface that consumes module names rejects.
#
#     WHAT IS PINNED, and it is not the sentence. D26 tiers the WORDING of a
#     refusal for something pcrec does not implement out of the exact tier, so
#     these assert the two things that are not wording: the diagnostic must not
#     name a module (a NEGATIVE pin — the substring "module 'utf8'"), and it
#     must point at the milestone that actually delivers the feature. The
#     cross-check is the one that makes it stick: whatever name the diagnostic
#     offers, `--features` must accept it, and here the assertion is that no
#     name is offered at all.
# ---------------------------------------------------------------------------
case13() {
    local d="$WORKDIR/case13"
    mkdir -p "$d"
    local rc out err

    # [M5-SEAM] (D58) `byte` is the encoding's name, in BOTH spellings.
    pcrec_run "$PCREC" -e byte -o "$d/ok.c" 'ab' 2>"$d/e0.txt"; rc=$?
    assert_eq "case13: -e byte compiles" "0" "$rc" "stderr: $(cat "$d/e0.txt")"
    pcrec_run "$PCREC" --encoding=byte -o "$d/ok2.c" 'ab' 2>"$d/e0b.txt"; rc=$?
    assert_eq "case13: --encoding=byte compiles" "0" "$rc" "stderr: $(cat "$d/e0b.txt")"

    # ABSENT means byte: the default artifact must be byte-identical to the
    # explicitly-byte one, which is a stronger statement than "it compiles" —
    # it says the default and the explicit request are the SAME request, not
    # merely two that happen to work. Compared through `-o -` (self-contained),
    # the idiom case9/case10 established for exactly this: two artifacts
    # written to different BASENAMES differ in their emitted #include line.
    pcrec_run "$PCREC" -o - 'ab' > "$d/def.c" 2>"$d/e0c.txt"; rc=$?
    assert_eq "case13: no -e at all compiles" "0" "$rc" "stderr: $(cat "$d/e0c.txt")"
    pcrec_run "$PCREC" -e byte -o - 'ab' > "$d/expl.c" 2>/dev/null
    if cmp -s "$d/def.c" "$d/expl.c"; then
        pass "case13: the DEFAULT encoding is byte (default and -e byte artifacts are byte-identical)"
    else
        fail "case13: the default encoding is not byte" \
             "$(diff "$d/def.c" "$d/expl.c" | head -4)"
    fi
    # ...and the artifact says so about itself (rx_info.encoding, PCREC_ENC_BYTE == 0).
    if grep -q '^    \.encoding = 0,$' "$d/def.c"; then
        pass "case13: the artifact stamps .encoding = 0 (PCREC_ENC_BYTE)"
    else
        fail "case13: the artifact does not stamp PCREC_ENC_BYTE" \
             "$(grep -n 'encoding' "$d/def.c" | head -3)"
    fi

    # [M5-SEAM] `ascii` was this encoding's name before D58 and is NOT an
    # alias: one namespace member, one spelling ([SR-10]). The diagnostic
    # offers the menu the registry actually holds.
    pcrec_run "$PCREC" -e ascii -o "$d/no0.c" 'ab' >"$d/o0.txt" 2>"$d/eold.txt"; rc=$?
    assert_eq "case13: -e ascii is no longer a known encoding (D58 renamed it 'byte')" "1" "$rc"
    assert_contains "case13: ...and the refusal offers the real menu" \
        "$(cat "$d/eold.txt")" "want byte, utf8"

    # -e utf8 is refused, cleanly, with no C written.
    pcrec_run "$PCREC" -e utf8 -o "$d/no.c" 'ab' >"$d/o1.txt" 2>"$d/e1.txt"; rc=$?
    err="$(cat "$d/e1.txt")"
    assert_eq "case13: -e utf8 is refused" "1" "$rc" "stderr: $err"
    if [ -s "$d/no.c" ]; then
        fail "case13: a refused encoding writes no C" "wrote $(wc -c <"$d/no.c") bytes"
    else
        pass "case13: a refused encoding writes no C"
    fi

    # THE FIX: it must not promise a module that does not exist.
    if printf '%s' "$err" | grep -q "module 'utf8'"; then
        fail "case13: -e utf8 must not promise a module the namespace lacks" \
             "stderr: $err" \
             "K14's shape: --features utf8 answers 'unknown module'"
    else
        pass "case13: -e utf8 does not promise a module the namespace lacks"
    fi
    assert_contains "case13: ...it names the milestone that delivers UTF-8" \
        "$err" "milestone M5"

    # AND THE CROSS-CHECK, which is what stops the fix being a reword: the
    # module namespace really has no 'utf8', so any diagnostic naming one is
    # over-promising. If a future M5 registers the name, this flips and the
    # pin above must be revisited deliberately rather than deleted.
    out="$(pcrec_run "$PCREC" --features utf8 -o - 'a' 2>&1)"; rc=$?
    assert_eq "case13: --features utf8 is still refused by name" "1" "$rc"
    assert_contains "case13: ...as an unknown module" "$out" "unknown module 'utf8'"

    # [M5-SEAM] the LONG spelling refuses identically. Both spellings reach
    # one lookup and one refusal, so they cannot drift into two answers.
    out="$(pcrec_run "$PCREC" --encoding=utf8 -o "$d/no2.c" 'ab' 2>&1)"; rc=$?
    assert_eq "case13: --encoding=utf8 is refused too" "1" "$rc"
    assert_contains "case13: ...with the same milestone diagnostic" "$out" "milestone M5"

    # [M5-SEAM] (D58/DD-12 (8)) encoding is PER-PATTERN, so two artifacts with
    # different prefixes compiled by SEPARATE invocations must compose in one
    # TU. That is the property "mixed encodings in one compilation unit are
    # supported by construction" rests on, and it is checkable today with one
    # encoding: nothing about the residual embed may be file- or
    # process-scoped.
    pcrec_run "$PCREC" -p e1 --encoding=byte -o "$d/e1.c" -- 'a(b|c)+d' >/dev/null 2>&1
    pcrec_run "$PCREC" -p e2 -e byte -o "$d/e2.c" -- 'x+y' >/dev/null 2>&1
    cat > "$d/mix.c" <<'MIXEOF'
#include "e1.h"
#include "e2.h"
int main(void)
{
    return (int)(e1_next_pos((const unsigned char *)"", 0, 0)
               + e2_next_pos((const unsigned char *)"", 0, 0)) - 2;
}
MIXEOF
    if gen_cc "case13 mixed-artifact TU" "$CC" $CFLAGS -I"$d" -o "$d/mix" \
              "$d/mix.c" "$d/e1.c" "$d/e2.c"; then
        if "$d/mix"; then
            pass "case13: two separately-compiled artifacts, each carrying its own residual block, link and run in one TU"
        else
            fail "case13: the two-artifact TU built but its residual entries answered wrongly"
        fi
    else
        fail "case13: two artifacts with their own residual blocks failed to compile into one TU" \
             "$(printf '%s' "$GEN_CC_LOG" | head -3)"
    fi
}

# ---------------------------------------------------------------------------
# 14. [STD1] phase A (docs/dev/decisions.md D37): the frozen named set
#     `std1` = {classes, modifiers}, artifact stamping, and the bare-default
#     mapping point. Phase A does NOT flip the bare default — it stays
#     "none" (the pre-existing behaviour); only the plumbing lands here.
#
#     `classes` and `modifiers` both carry real PRODUCERS since MOD-0.3c/
#     MOD-0.5c (src/parse/CLAUDE.md), so `--features std1` genuinely changes
#     what a pattern compiles TO, not just the probe channel's answered_at
#     — case10/case11 pinned that axis while the gate had no name for it.
#     Match assertions below are oracle-verified against python3 `re`
#     (docs/testing.md).
# ---------------------------------------------------------------------------
case14() {
    local d="$WORKDIR/case14"
    mkdir -p "$d"
    local rc out

    if ! command -v python3 >/dev/null 2>&1; then
        echo "case14: SKIP oracle-verified match cells (needs python3)" >&2
    fi

    # --- [STD1b] (D37, 2026-08-13): the bare default IS std1 now. Phase A
    #     (above, historically) pinned that the bare default still refused
    #     \d while --features std1 explicitly accepted it; this phase
    #     flips the bare default itself, so the interesting facts are now
    #     that BARE accepts \d and is byte-IDENTICAL to --features std1
    #     (not just equivalent modulo the stamp's set name, as the old
    #     std1-vs-explicit-classes,modifiers comparison below still is),
    #     and that the PRE-flip behaviour survives, verbatim, as
    #     `--features none` — the literal old-default spec. -----------
    pcrec_run "$PCREC" -o "$d/bare.c" -- '\d' >/dev/null 2>"$d/e_bare.txt"; rc=$?
    assert_eq "case14: bare default now accepts \\d ([STD1b]: the flip)" \
        "0" "$rc" "stderr: $(cat "$d/e_bare.txt")"

    pcrec_run "$PCREC" --features none -o "$d/none.c" -- '\d' >/dev/null 2>"$d/e_none.txt"; rc=$?
    assert_eq "case14: --features none still refuses \\d (the pre-flip bare behaviour, kept explicit)" \
        "1" "$rc"
    assert_contains "case14: ...with the classes-module refusal" \
        "$(cat "$d/e_none.txt")" "requires module 'classes'"

    pcrec_run "$PCREC" --features std1 -o "$d/std1.c" -- '\d' 2>"$d/e_std1.txt"; rc=$?
    assert_eq "case14: --features std1 accepts \\d" \
        "0" "$rc" "stderr: $(cat "$d/e_std1.txt")"

    # -o - (self-contained, no #include) for the comparison below: two
    # different output BASENAMES would otherwise embed two different
    # #include lines and differ for a reason unrelated to the stamp — the
    # same trap run_trie_identity.sh and case9's -i comparison both avoid.
    pcrec_run "$PCREC" -o - -- '\d' > "$d/bare_stamp.c" 2>/dev/null
    pcrec_run "$PCREC" --features std1 -o - -- '\d' > "$d/std1_bare.c" 2>/dev/null
    if diff -q "$d/bare_stamp.c" "$d/std1_bare.c" >/dev/null; then
        pass "case14: bare invocation == --features std1, byte-for-byte, stamp included (no set-name difference at all — a bare invocation IS std1 now, not merely equivalent to it)"
    else
        fail "case14: bare invocation vs --features std1 diverged" \
            "$(diff "$d/bare_stamp.c" "$d/std1_bare.c")"
    fi

    pcrec_run "$PCREC" --features classes,modifiers -o - -- '\d' > "$d/expl_bare.c" 2>/dev/null
    # byte-identical except the stamp's own SET NAME (std1 vs explicit) —
    # everything a matcher's behaviour depends on, including the stamped
    # MODULE LIST, is unchanged.
    local ndiff
    ndiff="$(diff "$d/std1_bare.c" "$d/expl_bare.c" | grep -cE '^[<>]')"
    if [ "$ndiff" -eq 4 ] \
       && grep -q '/\* Feature set: std1 (modules: classes,modifiers) \*/' "$d/std1_bare.c" \
       && grep -q '/\* Feature set: explicit (modules: classes,modifiers) \*/' "$d/expl_bare.c"; then
        pass "case14: --features std1 == --features classes,modifiers except the stamp's set name"
    else
        fail "case14: std1 vs explicit spelling diverged beyond the stamp" \
            "$(diff "$d/std1_bare.c" "$d/expl_bare.c")"
    fi

    # --- MATCH BEHAVIOUR, oracle-verified: std1 engages BOTH classes'
    #     (\d) and modifiers' ((?i)) producers in one pattern ------------
    if command -v python3 >/dev/null 2>&1; then
        pcrec_run "$PCREC" --features std1 --emit-main -o - -- '(?i)cat\d+' \
            > "$d/m.c" 2>"$d/e_m.txt"
        if gen_cc "${FUNCNAME[0]} (m.c)" "$CC" $CFLAGS -o "$d/m" "$d/m.c"; then
            pass "case14: --features std1 '(?i)cat\\d+' compiles"
            local py rx got
            for subj in 'xxCAT123xx' 'xxcatxx'; do
                py="$(python3 -c "
import re
m = re.search(r'(?i)cat\d+', '$subj')
print('match %d %d' % (m.start(), m.end()) if m else 'nomatch')
")"
                got="$(gen_run "${FUNCNAME[0]} '$subj'" "$d/m" "$subj")"
                assert_eq "case14: '(?i)cat\\d+' vs python re on '$subj'" \
                    "$py" "$got"
            done
        else
            fail "case14: --features std1 '(?i)cat\\d+' compiles" \
                "$(cat "$d/build_m.txt")"
        fi
    fi

    # --- unknown named-set-shaped spec: a clean, by-name error ----------
    pcrec_run "$PCREC" --features std2 -o "$d/bad.c" -- 'a' >/dev/null 2>"$d/e_bad.txt"; rc=$?
    assert_eq "case14: an unknown named-set name exits 1" "1" "$rc"
    assert_contains "case14: ...refused BY NAME" "$(cat "$d/e_bad.txt")" "'std2'"
    assert_contains "case14: ...and the message names the real vocabulary (std1)" \
        "$(cat "$d/e_bad.txt")" "std1"
    if [ -s "$d/bad.c" ]; then
        fail "case14: a refused --features writes no C" "wrote $(wc -c <"$d/bad.c") bytes"
    else
        pass "case14: a refused --features writes no C"
    fi

    # --- ARTIFACT STAMPING: header comment + macros, every invocation ---
    # [STD1b]: the DEFAULT constant flipped from "none" to "std1", so the
    # bare invocation's stamp flips with it — that is the entire mechanism
    # D37 promised (an artifact reproduces itself forever regardless of
    # what "default" means the year it was built, because it stamps the
    # EXPANDED answer, not the word "default"). `--features none` is what
    # now stamps 'none': the escape hatch, unaffected by the flip.
    out="$(pcrec_run "$PCREC" -o - -- 'a')"
    assert_contains "case14: bare invocation stamps 'std1' ([STD1b]: the new default constant)" \
        "$out" '/* Feature set: std1 (modules: classes,modifiers) */'
    assert_contains "case14: ...and PCREC_FEATURE_SET macro" \
        "$out" '#define PCREC_FEATURE_SET "std1"'
    assert_contains "case14: ...and the expanded PCREC_FEATURE_MODULES" \
        "$out" '#define PCREC_FEATURE_MODULES "classes,modifiers"'

    out="$(pcrec_run "$PCREC" --features none -o - -- 'a')"
    assert_contains "case14: --features none stamps 'none' (the escape hatch, unaffected by the flip)" \
        "$out" '/* Feature set: none (modules: none) */'
    assert_contains "case14: ...and PCREC_FEATURE_SET macro" \
        "$out" '#define PCREC_FEATURE_SET "none"'
    assert_contains "case14: ...and an empty PCREC_FEATURE_MODULES" \
        "$out" '#define PCREC_FEATURE_MODULES ""'

    out="$(pcrec_run "$PCREC" --features std1 -o - -- 'a')"
    assert_contains "case14: --features std1 stamps its own name" \
        "$out" '/* Feature set: std1 (modules: classes,modifiers) */'
    assert_contains "case14: ...and the expanded module list in the macro" \
        "$out" '#define PCREC_FEATURE_MODULES "classes,modifiers"'

    out="$(pcrec_run "$PCREC" --features all -o - -- 'a')"
    assert_contains "case14: --features all stamps 'all' plus its own full expansion" \
        "$out" '/* Feature set: all (modules: '

    # the paired .c/.h form: the HEADER carries the comment (matching the
    # existing pattern-comment convention) but not the macros, so a .c that
    # #includes its own .h never sees PCREC_FEATURE_SET defined twice.
    pcrec_run "$PCREC" --features std1 -o "$d/pair.c" -- 'a' >/dev/null 2>"$d/e_pair.txt"
    assert_contains "case14: the paired .h also carries the stamp comment" \
        "$(cat "$d/pair.h" 2>/dev/null)" \
        '/* Feature set: std1 (modules: classes,modifiers) */'
    if grep -q 'PCREC_FEATURE_SET' "$d/pair.h" 2>/dev/null; then
        fail "case14: the paired .h must not carry the macros too" \
            "$(cat "$d/pair.h")"
    else
        pass "case14: the paired .h carries the comment only, not the macros"
    fi
    if [ "$(grep -c 'define PCREC_FEATURE_SET' "$d/pair.c")" -eq 1 ]; then
        pass "case14: the .c defines PCREC_FEATURE_SET exactly once (no redefinition via its own #include)"
    else
        fail "case14: PCREC_FEATURE_SET macro count in the .c" \
            "$(grep -c 'define PCREC_FEATURE_SET' "$d/pair.c") occurrences"
    fi
}

# ---------------------------------------------------------------------------
# 15. K21 (docs/dev/known_issues.md) — --emit-main's three-way contract on a
#     VM artifact that GIVES UP. `<prefix>_search` is three-valued (1 match,
#     0 no-match, negative PCREC_ERR_STEPS/PCREC_ERR_FRAMES give-up on a VM
#     artifact's budget exhaustion; DFA artifacts never return the
#     sentinels). The pre-fix `pcrec_emit_main` tested the result as a bool,
#     so C truthiness took the MATCH branch on a negative return and printed
#     `caps`, which the give-up path never wrote — confidently-reported
#     uninitialized stack bytes ("match 0 0"). Case2 already covers match/
#     nomatch; this case is the third leg, driven the same way §4/§4.5 of
#     tests/vm/run_vm_tests.sh drive the two bounds to their own limit (a
#     tiny --step-budget / --backtrack-frames on a shape that burns it in a
#     handful of resumptions), rather than the R23 fuzzer witness, which is
#     harder to reproduce reliably.
# ---------------------------------------------------------------------------
case15() {
    local d="$WORKDIR/case15"
    mkdir -p "$d"

    # (a) the step budget. `(a*)*b`'s O(n^2) resumption count burns a
    # --step-budget=50 well inside 20 bytes of 'a' with no 'b' to end it.
    local rc build_log build_rc
    pcrec_run "$PCREC" --emit-main --engine=vm --step-budget=50 -o "$d/steps.c" \
        -- '(a*)*b' >/dev/null 2>"$d/steps.err"
    rc=$?
    assert_eq "case15: steps witness compiles pcrec-side" "0" "$rc" \
        "stderr: $(cat "$d/steps.err")"
    gen_cc "${FUNCNAME[0]}-steps" "$CC" $CFLAGS -o "$d/steps" "$d/steps.c"
    build_rc=$?; build_log="$GEN_CC_LOG"
    if [ "$build_rc" -eq 0 ]; then
        pass "case15: steps witness's --emit-main output compiles"
    else
        fail "case15: steps witness's --emit-main output compiles" "$build_log"
        return
    fi
    local out rc2
    out="$(gen_run "${FUNCNAME[0]}-steps" "$d/steps" 'aaaaaaaaaaaaaaaaaaaa')"; rc2=$?
    assert_eq "case15: step-budget exhaustion prints the honest give-up line, not a fabricated match" \
        "steps" "$out"
    assert_eq "case15: step-budget exhaustion exits 3 (distinct from match=0, nomatch=1, usage=2)" \
        "3" "$rc2"

    # (b) the frame capacity. `((a)|b)*c` overflows a --backtrack-frames=4
    # array in a handful of choice points.
    pcrec_run "$PCREC" --emit-main --engine=vm --backtrack-frames=4 -o "$d/frames.c" \
        -- '((a)|b)*c' >/dev/null 2>"$d/frames.err"
    rc=$?
    assert_eq "case15: frames witness compiles pcrec-side" "0" "$rc" \
        "stderr: $(cat "$d/frames.err")"
    gen_cc "${FUNCNAME[0]}-frames" "$CC" $CFLAGS -o "$d/frames" "$d/frames.c"
    build_rc=$?; build_log="$GEN_CC_LOG"
    if [ "$build_rc" -eq 0 ]; then
        pass "case15: frames witness's --emit-main output compiles"
    else
        fail "case15: frames witness's --emit-main output compiles" "$build_log"
        return
    fi
    out="$(gen_run "${FUNCNAME[0]}-frames" "$d/frames" 'aaaaaaaaaaaaaaaaaaaa')"; rc2=$?
    assert_eq "case15: frame-capacity exhaustion prints the honest give-up line, not a fabricated match" \
        "frames" "$out"
    assert_eq "case15: frame-capacity exhaustion exits 3 (distinct from match=0, nomatch=1, usage=2)" \
        "3" "$rc2"

    # (c) the non-firing controls: the SAME two patterns under an ample
    # budget/capacity must still match honestly — a give-up path that always
    # fired would trivially "pass" (a) and (b) above without proving anything.
    pcrec_run "$PCREC" --emit-main --engine=vm --step-budget=1000000 -o "$d/steps_ok.c" \
        -- '(a*)*b' >/dev/null 2>"$d/steps_ok.err"
    gen_cc "${FUNCNAME[0]}-steps-ok" "$CC" $CFLAGS -o "$d/steps_ok" "$d/steps_ok.c" \
        && out="$(gen_run "${FUNCNAME[0]}-steps-ok" "$d/steps_ok" 'aaaaaaaaaaaaaaaaaaaab')" \
        && assert_eq "case15 CONTRAST: an ample step budget on the same shape still matches honestly" \
            "match 0 21" "$out" \
        || fail "case15 CONTRAST: could not build/run the ample-step-budget control" "$GEN_CC_LOG"

    pcrec_run "$PCREC" --emit-main --engine=vm --backtrack-frames=4096 -o "$d/frames_ok.c" \
        -- '((a)|b)*c' >/dev/null 2>"$d/frames_ok.err"
    gen_cc "${FUNCNAME[0]}-frames-ok" "$CC" $CFLAGS -o "$d/frames_ok" "$d/frames_ok.c" \
        && out="$(gen_run "${FUNCNAME[0]}-frames-ok" "$d/frames_ok" 'aaaaaaaaaaaaaaaaaaaac')" \
        && assert_eq "case15 CONTRAST: an ample frame capacity on the same shape still matches honestly" \
            "match 0 21" "$out" \
        || fail "case15 CONTRAST: could not build/run the ample-frame-capacity control" "$GEN_CC_LOG"
}

# ---------------------------------------------------------------------------
# 16. [M4.7c] K9's API half: rx_info.pattern_len makes the NUL-truncation
# silent-wrong-compile DETECTABLE (docs/dev/known_issues.md K9).
#
# pcrec_compile() takes a NUL-terminated pattern and no length, so a pattern
# containing an embedded NUL is silently truncated at it: "a\0b" (3 bytes)
# compiles as "a" (1 byte) and reports SUCCESS for a different pattern than
# the caller passed. K9 itself is not reachable through argv (a shell/exec
# NUL always ends the string before pcrec sees it) or through a line-based
# .rxt corpus, which is why case7's shape — a direct library-API C probe
# linking libpcrec.a — is the only surface that can express it.
#
# This case PINS the current truncation behavior (it is DD-3's job, not
# this one, to change it) and asserts the new detectability it landed with:
# a caller who independently knows the intended pattern length can compare
# it against rx_info.pattern_len and catch exactly this silent-wrong-compile.
# ---------------------------------------------------------------------------
case16() {
    local d="$WORKDIR/case16"
    mkdir -p "$d"

    if [ ! -f "$LIBA" ]; then
        fail "case16: libpcrec.a exists at $LIBA" "build it first (e.g. 'make')"
        return
    fi
    if [ ! -f "$LIBDIR/pcrec.h" ]; then
        fail "case16: pcrec.h exists at $LIBDIR/pcrec.h"
        return
    fi

    cat > "$d/k9.c" <<'EOF'
#include <stdio.h>
#include <string.h>
#include "pcrec.h"

int main(void) {
    pcrec_options opt;
    pcrec_default_options(&opt);
    pcrec_output out;
    pcrec_error err;
    memset(&out, 0, sizeof(out));

    /* "a\0b": 3 bytes, an embedded NUL after the first. Cannot be spelled
     * as a C string literal (it would itself end at the NUL) — built byte
     * by byte so the buffer's true 3-byte extent is unambiguous here even
     * though pcrec_compile() cannot see past byte 1. */
    char pat[3];
    pat[0] = 'a';
    pat[1] = '\0';
    pat[2] = 'b';

    int rc = pcrec_compile(pat, &opt, &out, &err);
    if (rc != 0) {
        fprintf(stderr, "FAIL: embedded-NUL pattern did not compile (rc=%d, %s)\n",
                rc, err.msg);
        return 1;
    }
    if (!out.c_src) {
        fprintf(stderr, "FAIL: embedded-NUL pattern compiled but produced NULL c_src\n");
        return 1;
    }
    /* K9's claim, pinned: the compile SUCCEEDS for a pattern different from
     * the one the caller passed (the artifact is for "a", not "a\0b"). What
     * this field adds is that the artifact now says so honestly. */
    if (!strstr(out.c_src, ".pattern_len = 1,")) {
        fprintf(stderr,
                "FAIL: rx_info.pattern_len does not report 1 for the truncated compile\n");
        pcrec_output_free(&out);
        return 1;
    }

    pcrec_output_free(&out);
    printf("k9 OK\n");
    return 0;
}
EOF
    local build_log
    build_log="$("$CC" $CFLAGS -I"$LIBDIR" -o "$d/k9" "$d/k9.c" "$LIBA" 2>&1)"
    if [ $? -eq 0 ]; then
        pass "case16: K9 embedded-NUL probe compiles against pcrec.h + libpcrec.a"
    else
        fail "case16: K9 embedded-NUL probe compiles against pcrec.h + libpcrec.a" "$build_log"
        return
    fi

    local runout runrc
    runout="$("$TIMEOUT_BIN" 10 "$d/k9" 2>"$d/k9_stderr.txt")"
    runrc=$?
    if [ $runrc -ge 124 ]; then
        fail "case16: K9 embedded-NUL probe does not crash or hang" \
            "exit code: $runrc (>=124 = timeout/crash)" "stderr: $(cat "$d/k9_stderr.txt")"
    else
        assert_eq "case16: K9 embedded-NUL probe exits 0" "0" "$runrc" \
            "stderr: $(cat "$d/k9_stderr.txt")"
        assert_eq "case16: rx_info.pattern_len (1) makes the truncated compile detectable" \
            "k9 OK" "$runout"
    fi
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
case13
case14
case15
case16

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
