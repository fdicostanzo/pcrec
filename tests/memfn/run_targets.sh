#!/usr/bin/env bash
# tests/memfn/run_targets.sh -- [XARCH-DEV] unit K0 (request R-36): `make
# test-memfn-targets`, the kit's CPU target table (memfn/src/targets.def;
# docs/design/memfn/target_seam_units.md §2, §5; target_seam.md §2, §6.1, §8).
# Rev 0's withdrawn U1 harness (commit 171bdb343), its table now the kit's.
#
# Three parts:
#   1. THE TABLE CHECK's verdict (memfn/tests/check_targets.sh; control: gcc's
#      own -march and the guard column under several preprocessor targets).
#      `make` only warns on it; this section fails on it.
#   2. THE ENTRIES (targets_check.c; control: the design's rows spelled as
#      literals there, and `uname -m` for the host's default list).
#   3. THE COMPILE CELLS (G1's measurable form, §6.1's matrix): a kit-shaped
#      `#if`-free fixture in the kit's own region and guard texts, compiled,
#      linked and run at each cell, its answers held to a naive finder over
#      every (length, position) of a sweep; the v3 part's object must carry
#      ymm registers and the baseline part's xmm ones (objdump: a region that
#      silently failed to apply), and the family guard must REFUSE a `-m32`
#      gcc and an aarch64 clang compile with its own message.
# THE RAN FLOOR: on an x86-64 host every gcc cell must run (GCC_CELLS); a
# clang cell is SKIPPED, counted and printed, only where clang is absent; on
# another host the x86 cells are SKIPPED and counted.
#
# Usage: bash tests/memfn/run_targets.sh     Env: CC (the unit build), KEEP=1
# Prints `checks passed: N` / `checks failed: M`; exit 0 iff M is 0.

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/unit_cc.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
KEEP="${KEEP:-0}"
WORKDIR="$(mktemp -d)"
cleanup() { if [ "$KEEP" = 1 ]; then echo "targets: KEEP=1, $WORKDIR" >&2; else rm -rf "$WORKDIR"; fi; }
trap cleanup EXIT

pass=0; fail=0; ran=0; skipped=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1"; fail=$((fail + 1)); }
skip() { echo "SKIP: $1"; skipped=$((skipped + 1)); }
GCC_CELLS=6
ROW_FLOOR=58   # targets_check.c's PASS lines, measured at K0 (lane k0; one host row on every host); +16 at U2 (four admission rows of four checks each, every host)

echo "== 1. the kit's target table check =="
if out="$(bash "$ROOT_DIR/memfn/tests/check_targets.sh")"; then ok "$out"; else bad "$out"; fi

echo "== 2. the entries =="
BIN="$WORKDIR/targets_check"
if ! unit_build "$BIN" "$SCRIPT_DIR/targets_check.c" -I"$ROOT_DIR/memfn/include"; then
    bad "targets_check.c did not build"; echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
host="$(uname -m)"
"$BIN" "$host" > "$WORKDIR/rows.out"; rc=$?
cat "$WORKDIR/rows.out"
nrow="$(grep -c '^PASS' "$WORKDIR/rows.out")"
if [ "$rc" -eq 0 ] && [ "$nrow" -ge "$ROW_FLOOR" ]; then ok "targets_check: $nrow entry checks green (floor $ROW_FLOOR)"
else bad "targets_check: rc=$rc, $nrow passing (floor $ROW_FLOOR)"; fi

echo "== 3. the compile cells =="
"$BIN" --fixture > "$WORKDIR/fixture.c"
cat > "$WORKDIR/main.c" <<'EOF'
#include <stdio.h>
#include <string.h>
size_t fx_generic(const unsigned char *, size_t, unsigned char);
size_t fx_w16(const unsigned char *, size_t, unsigned char);
size_t fx_w32(const unsigned char *, size_t, unsigned char);
/* The control: a naive finder written here, not the fixture's generic. */
static size_t naive(const unsigned char *s, size_t n, unsigned char b)
{ size_t i = 0; while (i < n && s[i] != b) i++; return i; }
int main(void)
{
    static unsigned char buf[200];
    long checks = 0, bad = 0;
    int v3 = __builtin_cpu_supports("avx2") && __builtin_cpu_supports("bmi2");
    for (size_t n = 0; n <= sizeof buf; n++)
        for (size_t at = 0; at <= n; at++) {
            memset(buf, 'a', sizeof buf);
            if (at < n) buf[at] = 'Z';
            size_t want = naive(buf, n, 'Z');
            bad += fx_w16(buf, n, 'Z') != want; checks++;
            if (v3) { bad += fx_w32(buf, n, 'Z') != want; checks++; }
        }
    printf("checks %ld bad %ld v3 %d\n", checks, bad, v3);
    return bad != 0;
}
EOF

have_clang=0; command -v clang >/dev/null 2>&1 && have_clang=1

# cell NAME COMPILER FLAGS...: compile + link + run; answers vs the naive finder.
cell() {
    local name="$1" cc="$2"; shift 2
    local exe="$WORKDIR/cell_$name"
    if ! "$TIMEOUT_BIN" 120 "$cc" -O2 -Wall -Wextra -Werror "$@" -o "$exe" \
            "$WORKDIR/fixture.c" "$WORKDIR/main.c" 2> "$WORKDIR/cell_$name.err"; then
        bad "cell $name ($cc $*): did not compile: $(head -c 300 "$WORKDIR/cell_$name.err")"; return
    fi
    local r; r="$("$TIMEOUT_BIN" 60 "$exe")"
    if [ $? -eq 0 ]; then ok "cell $name ($cc $*): $r"; ran=$((ran + 1))
    else bad "cell $name ($cc $*): wrong answers: $r"; fi
}

if [ "$host" = x86_64 ]; then
    cell gcc-default  gcc
    cell gcc-native   gcc -march=native
    cell gcc-v4       gcc -march=x86-64-v4
    cell gcc-nosse2   gcc -mno-sse2
    cell gcc-noregs   gcc -mgeneral-regs-only
    cell gcc-v2       gcc -march=x86-64-v2
    if [ "$have_clang" = 1 ]; then
        cell clang-default clang
        cell clang-native  clang -march=native
        cell clang-v4      clang -march=x86-64-v4
    else skip "clang cells: no clang on this box (3 cells)"; fi
    [ "$ran" -ge "$GCC_CELLS" ] || bad "RAN floor: $ran cells ran, want at least the $GCC_CELLS gcc cells"

    echo "== 3b. the target code census (objdump) =="
    if command -v objdump >/dev/null 2>&1; then
        gcc -O2 -c -o "$WORKDIR/fx.o" "$WORKDIR/fixture.c"
        dis() { objdump -d --no-show-raw-insn "$WORKDIR/fx.o" | awk -v f="<$1>:" '$2==f{p=1;next} /^$/{p=0} p'; }
        y32="$(dis fx_w32 | grep -c '%ymm')"; x16="$(dis fx_w16 | grep -c '%xmm')"; yg="$(dis fx_generic | grep -c '%ymm')"
        if [ "$y32" -gt 0 ] && [ "$x16" -gt 0 ] && [ "$yg" -eq 0 ]; then
            ok "census at default -march: fx_w32 $y32 ymm, fx_w16 $x16 xmm, fx_generic 0 ymm"
        else bad "census at default -march: fx_w32 $y32 ymm (want > 0), fx_w16 $x16 xmm (want > 0), fx_generic $yg ymm (want 0)"; fi
    else skip "census: no objdump"; fi

    echo "== 3c. the family guard refuses another family =="
    msg='generated for another CPU family'
    guard() {
        local name="$1"; shift
        if "$TIMEOUT_BIN" 60 "$@" -fsyntax-only "$WORKDIR/fixture.c" 2> "$WORKDIR/g_$name.err"; then
            bad "guard $name ($*): compiled; the #error did not fire"
        elif grep -q "$msg" "$WORKDIR/g_$name.err"; then ok "guard $name ($*): refused with its own message"
        else bad "guard $name ($*): failed, but not with the guard's message: $(head -c 200 "$WORKDIR/g_$name.err")"; fi
    }
    guard gcc-m32 gcc -m32
    if [ "$have_clang" = 1 ]; then guard clang-aarch64 clang --target=aarch64-linux-gnu
    else skip "guard clang-aarch64: no clang"; fi
else
    skip "x86-64 compile cells, census and guard: host is $host (counted: $((GCC_CELLS + 6)))"
fi

[ $((pass + fail)) -gt 2 ] || bad "the section checked nothing past its first two parts"
echo "targets: $ran cells ran, $skipped skipped"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
