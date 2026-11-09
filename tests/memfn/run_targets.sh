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
#   4. PCREC'S ARTIFACTS at a target ([XARCH-DEV] U3): part 3's cells on real
#      `pcrec -fmemfn-simd=TARGET` artifacts (answers vs a naive finder, a ymm
#      census, a region-stripped control, the guard's refusals), and the
#      CONSUMER-TU cells: a gcc translation unit that #includes an artifact and
#      then uses the same facility (SSE intrinsics, a second artifact, a
#      fortified memcpy) must compile (review 2026-11-08-r5-xarch X-1, X-2).
# THE RAN FLOORS: on an x86-64 host every gcc cell of parts 3 and 4 must run
# (GCC_CELLS, ART_GCC_CELLS, CONSUMER_CELLS); a clang cell is SKIPPED, counted
# and printed, only where clang is absent; on another host the x86 cells are
# SKIPPED and counted. A missing build/pcrec on an x86-64 host is a FAIL.
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
ART_GCC_CELLS=12   # part 4: 4 gcc cells x 3 targets (the v3 four run only on an AVX2 CPU)
CONSUMER_CELLS=4   # part 4's consumer-TU cells
ROW_FLOOR=63   # targets_check.c's PASS lines, measured at K0 (lane k0; one host row on every host); +16 at U2 (four admission rows of four checks each, every host); +5 at u2rev (each admission row's includes, review r5 X-1; the kernel's bracket refusal, SEAM-5)

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
    # A -march=x86-64-v4 object may carry AVX-512 code (CI's runner lacks it:
    # SIGILL, run 42530231132): such a cell is compiled and linked everywhere
    # but RUN only where the host has avx512f; the skip is counted.
    case " $* " in *" -march=x86-64-v4 "*)
        if ! grep -qw avx512f /proc/cpuinfo 2>/dev/null; then
            skip "cell $name ($cc $*): compiled and linked, not run (host lacks avx512f)"; return
        fi ;;
    esac
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
    want="$GCC_CELLS"; grep -qw avx512f /proc/cpuinfo 2>/dev/null || want=$((GCC_CELLS - 1))   # gcc-v4 not run without avx512f
    [ "$ran" -ge "$want" ] || bad "RAN floor: $ran cells ran, want at least the $want gcc cells"

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

echo "== 4. pcrec's artifacts at a target (U3) =="
# The cells of part 3 on REAL artifacts: pcrec states the target to the kit
# and places its guard and region (match_api.md §6.3.10¶14-¶15). A vrun-shaped
# pattern at each SIMD target and at the portable one, compiled at each cell,
# its first match held to a naive caseless finder over every (length, position)
# of a sweep. Controls: the v3 artifact's object carries ymm registers; with
# the region's pragmas stripped it no longer compiles at the default -march
# (the region, not the consumer's flags, supplies the ISA); its guard refuses
# a -m32 gcc and an aarch64 clang compile. Then the consumer-TU cells.
PCREC_BIN="${PCREC_BIN:-$ROOT_DIR/build/pcrec}"
if [ "$host" = x86_64 ] && [ -x "$PCREC_BIN" ]; then
    aran=0
    cat > "$WORKDIR/drv.c" <<'C'
#include <stdio.h>
#include <stddef.h>
#include <string.h>
#include <ctype.h>
#include "a.h"
static long naive(const unsigned char *s, size_t n) {
    for (size_t i = 0; i + 3 <= n; i++)
        if (tolower(s[i]) == 'c' && tolower(s[i + 1]) == 'a' && tolower(s[i + 2]) == 't') return (long)i;
    return -1;
}
int main(void) {
    unsigned char b[200]; long bad = 0, n_checks = 0;
    for (size_t n = 0; n <= 150; n++) for (size_t at = 0; at <= n; at++) {
        memset(b, 'x', n); if (at + 3 <= n) memcpy(b + at, "cAt", 3);
        if (n > 6) b[n / 2] = 'c';   /* a near miss */
        ptrdiff_t sp[1][2]; int rc = rx_search(b, n, 0, sp);
        long got = rc > 0 ? (long)sp[0][0] : -1;
        n_checks++; if (got != naive(b, n)) bad++;
    }
    printf("%ld %ld\n", n_checks, bad); return bad != 0;
}
C
    have_clang=0; command -v clang >/dev/null 2>&1 && have_clang=1
    host_avx2=0; gcc -march=native -dM -E -x c /dev/null 2>/dev/null | grep -q '__AVX2__' && host_avx2=1
    acell() {   # acell TARGET NAME CC FLAGS..
        local tg="$1" name="$2"; shift 2; local d="$WORKDIR/a_${tg}_$name"; mkdir -p "$d"
        if [ "$tg" = portable ]; then simd=-fno-memfn-simd; else simd="-fmemfn-simd=$tg"; fi
        if ! "$TIMEOUT_BIN" 60 "$PCREC_BIN" -p rx "$simd" -o "$d/a.c" --pattern '(?i)cat' 2> "$d/pc.err"; then
            bad "artifact $tg: pcrec refused: $(head -c 200 "$d/pc.err")"; return; fi
        cp "$WORKDIR/drv.c" "$d/drv.c"
        if ! "$TIMEOUT_BIN" 120 "$@" -O2 -I"$d" -o "$d/run" "$d/a.c" "$d/drv.c" 2> "$d/cc.err"; then
            bad "artifact $tg cell $name ($*): did not build: $(head -c 300 "$d/cc.err")"; return; fi
        if [ "$tg" = x86-64-v3 ] && [ "$host_avx2" != 1 ]; then
            skip "artifact $tg cell $name: built; not run (this CPU lacks AVX2)"; return; fi
        ran=$((ran + 1)); aran=$((aran + 1))
        if out="$("$TIMEOUT_BIN" 60 "$d/run")"; then ok "artifact $tg cell $name ($*): answers equal the naive finder ($out)"
        else bad "artifact $tg cell $name ($*): answers differ (checks, wrong: $out)"; fi
    }
    for tg in portable x86-64 x86-64-v3; do
        acell "$tg" gcc gcc
        acell "$tg" native gcc -march=native
        acell "$tg" v2 gcc -march=x86-64-v2
        acell "$tg" nosse2 gcc -mno-sse2
        if [ "$have_clang" = 1 ]; then acell "$tg" clang clang; else skip "artifact $tg cell clang: no clang"; fi
    done
    want="$ART_GCC_CELLS"; [ "$host_avx2" = 1 ] || want=$((ART_GCC_CELLS - 4))
    clang_cells=0; [ "$have_clang" = 1 ] && clang_cells=3; [ "$have_clang" = 1 ] && [ "$host_avx2" != 1 ] && clang_cells=2
    [ "$aran" -ge $((want + clang_cells)) ] || bad "RAN floor (artifacts): $aran cells ran, want $((want + clang_cells))"
    # the levels each target renders, read off the artifact's own stamp: the
    # portable target none, each SIMD target some (else the answer cells above
    # would pass with no SIMD at all)
    forms() { sed -n 's/^#define RX_MEMFN_FORMS //p' "$WORKDIR/a_$1_gcc/a.c"; }
    if [ "$(forms portable)" = '"none"' ] && [ -n "$(forms x86-64)" ] && [ "$(forms x86-64)" != '"none"' ] \
       && [ -n "$(forms x86-64-v3)" ] && [ "$(forms x86-64-v3)" != '"none"' ]; then
        ok "forms: the portable artifact renders no SIMD form, x86-64 $(forms x86-64), x86-64-v3 $(forms x86-64-v3)"
    else bad "forms: portable $(forms portable) (want \"none\"), x86-64 $(forms x86-64), x86-64-v3 $(forms x86-64-v3) (want SIMD forms)"; fi
    v3="$WORKDIR/a_x86-64-v3_gcc/a.c"
    if [ -f "$v3" ] && command -v objdump >/dev/null 2>&1; then
        gcc -O2 -c -I"$(dirname "$v3")" -o "$WORKDIR/v3.o" "$v3"
        y="$(objdump -d --no-show-raw-insn "$WORKDIR/v3.o" | grep -c '%ymm')"
        if [ "$y" -gt 0 ]; then ok "census: the x86-64-v3 artifact's object carries $y ymm uses at the default -march"
        else bad "census: the x86-64-v3 artifact's object carries no ymm register (the region did not apply?)"; fi
        sed -E '/#pragma (clang attribute (push|pop)|GCC (push_options|pop_options|target))/d' "$v3" > "$WORKDIR/v3_noregion.c"
        if gcc -O2 -c -I"$(dirname "$v3")" -o "$WORKDIR/v3n.o" "$WORKDIR/v3_noregion.c" 2> "$WORKDIR/v3n.err"; then
            bad "control: the x86-64-v3 artifact without its region still compiled at the default -march"
        elif grep -q 'target specific option mismatch' "$WORKDIR/v3n.err"; then
            ok "control: the x86-64-v3 artifact without its region refuses to compile at the default -march (an ISA mismatch)"
        else bad "control: the region-stripped artifact failed, but not for its ISA: $(head -c 200 "$WORKDIR/v3n.err")"; fi
        if gcc -m32 -fsyntax-only -I"$(dirname "$v3")" "$v3" 2> "$WORKDIR/v3g.err"; then bad "artifact guard gcc -m32: compiled"
        elif grep -q 'generated for another CPU family' "$WORKDIR/v3g.err"; then ok "artifact guard gcc -m32: refused with its own message"
        else bad "artifact guard gcc -m32: failed, but not at the guard: $(head -c 200 "$WORKDIR/v3g.err")"; fi
        if [ "$have_clang" = 1 ]; then
            if clang --target=aarch64-linux-gnu -fsyntax-only -I"$(dirname "$v3")" "$v3" 2> "$WORKDIR/v3c.err"; then bad "artifact guard clang aarch64: compiled"
            elif grep -q 'generated for another CPU family' "$WORKDIR/v3c.err"; then ok "artifact guard clang aarch64: refused with its own message"
            else bad "artifact guard clang aarch64: failed, but not at the guard: $(head -c 200 "$WORKDIR/v3c.err")"; fi
        else skip "artifact guard clang aarch64: no clang"; fi
    else skip "artifact census and controls: no v3 artifact or no objdump"; fi

    echo "== 4b. consumer translation units (gcc) =="
    # An artifact compiled ALONE builds under every flag set; these are the
    # uses that #include it and then use the same facility in the same TU.
    # gcc gives a header's inline functions the target in force where it is
    # FIRST included, so a header first read inside an artifact's region
    # breaks every later use of it outside. Each cell must compile.
    cdir="$WORKDIR/consumer"; mkdir -p "$cdir"
    gen() { "$TIMEOUT_BIN" 60 "$PCREC_BIN" "$@" 2>> "$cdir/pc.err"; }
    gen -p ra -fmemfn-simd=x86-64-v3 -o "$cdir/a.c" --pattern '(?i)hello' &&
    gen -p rb -fmemfn-simd=x86-64 -o "$cdir/b.c" --pattern '(?i)world' &&
    gen -p rc -fmemfn-simd=x86-64-v3 -o "$cdir/c.c" --pattern '^\s+|\s+$' ||
        bad "consumer cells: pcrec refused an artifact: $(head -c 200 "$cdir/pc.err")"
    if grep -q '^#define RC_COMPOUND "none"' "$cdir/c.c"; then
        bad "consumer cells: the compound control is no compound (RC_COMPOUND none); re-aim its pattern"; fi
    # F1 (lane u3d27, D27 region suite; match_api.md §6.3.10¶15): the region
    # holds no #include, a compound part's own and --emit-main's included, and
    # each header is included once; a part's count stays 0 (its held lines'
    # marks leave with them) and the --emit-main compound's count is the
    # target's text alone (the prologue already has its headers), as on a
    # plain artifact with no form.
    gen -p rd -fmemfn-simd=x86-64-v3 --emit-main -o "$cdir/d.c" --pattern '^\s+|\s+$' &&
    gen -p re -fmemfn-simd=x86-64-v3 --emit-main -o "$cdir/e.c" --pattern 'abc' ||
        bad "consumer cells: pcrec refused an F1 control: $(head -c 200 "$cdir/pc.err")"
    for f in c.c d.c; do
        nreg=$(grep -c '^#pragma GCC push_options' "$cdir/$f")
        inreg=$(awk '/^#pragma GCC push_options/{r=1} /^#pragma GCC pop_options/{r=0} r && /^#include/' "$cdir/$f" | wc -l)
        dup=$(grep '^#include <' "$cdir/$f" | sort | uniq -d | tr '\n' ' ')
        parts=$(grep -E '^#define R[CD]__\w+_SIMD_GUARDED_BYTES ' "$cdir/$f" | grep -vc ' 0x0000000000000000ULL$')
        if [ "$nreg" = 1 ] && [ "$inreg" = 0 ] && [ -z "$dup" ] && [ "$parts" = 0 ]; then
            ok "F1 $f (compound, v3): no #include inside the region, none twice, every part's count 0"
        else bad "F1 $f: regions=$nreg includes-inside=$inreg twice=[${dup}] nonzero-part-counts=$parts"; fi
    done
    gd=$(sed -n 's/^#define RD_SIMD_GUARDED_BYTES //p' "$cdir/d.c")
    ge=$(sed -n 's/^#define RE_SIMD_GUARDED_BYTES //p' "$cdir/e.c")
    if [ -n "$gd" ] && [ "$gd" = "$ge" ]; then
        ok "F1 d.c: the --emit-main compound's count is the plain control's ($gd)"
    else bad "F1 d.c: SIMD_GUARDED_BYTES $gd, the plain --emit-main control's $ge"; fi
    printf '%s\n' '#include "a.c"' '#include <emmintrin.h>' \
        'int sse_use(const char *p) { __m128i v = _mm_loadu_si128((const __m128i *)p);' \
        '    return _mm_movemask_epi8(_mm_cmpeq_epi8(v, _mm_set1_epi8(97))); }' > "$cdir/intrin.c"
    printf '%s\n' '#include "a.c"' '#include "b.c"' > "$cdir/two.c"
    printf '%s\n' '#include "c.c"' '#include <string.h>' \
        'void cpy(char *d, const char *s, size_t n) { memcpy(d, s, n); }' > "$cdir/fortify.c"
    ccell() {   # ccell NAME FILE FLAGS..
        local name="$1" f="$2"; shift 2
        if "$TIMEOUT_BIN" 120 gcc "$@" -c -I"$cdir" -o "$cdir/$name.o" "$cdir/$f" 2> "$cdir/$name.err"; then
            cran=$((cran + 1)); ok "consumer $name (gcc $*): compiles"
        else cran=$((cran + 1)); bad "consumer $name (gcc $*): $(grep -m1 'error' "$cdir/$name.err" | head -c 300)"; fi
    }
    cran=0
    ccell intrin intrin.c -O2                       # a v3 artifact, then the consumer's SSE intrinsics
    ccell two-O2 two.c -O2                          # a v3 artifact, then an x86-64 one
    ccell two-O0 two.c -O0
    ccell fortify fortify.c -O2 -D_FORTIFY_SOURCE=2 # a v3 compound, then a fortified memcpy
    [ "$cran" -ge "$CONSUMER_CELLS" ] || bad "RAN floor (consumer): $cran cells ran, want $CONSUMER_CELLS"
elif [ "$host" = x86_64 ]; then
    bad "pcrec artifact cells: no $PCREC_BIN on an x86-64 host (build it: make)"
else
    skip "pcrec artifact cells: host is $host, not x86_64 (counted: $((ART_GCC_CELLS + CONSUMER_CELLS + 6)))"
fi

[ $((pass + fail)) -gt 2 ] || bad "the section checked nothing past its first two parts"
echo "targets: $ran cells ran, $skipped skipped"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
