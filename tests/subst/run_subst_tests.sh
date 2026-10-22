#!/usr/bin/env bash
# tests/subst/run_subst_tests.sh -- [M4-SUBST] `make test-subst`: the subst
# artifact's checks (docs/spec/subst_api.md, replace_design.md §R3).
#
#   1. run_subst_tests.py over cells.tsv: every cell's stated answer, the
#      generic arms (sizing, NOSPACE, the k = 1 glue, the dirty iterator, the
#      foreign ncap, the LIMIT stop), and libpcre2's pcre2_substitute where it
#      can answer (its header).
#   2. the template compiler's refusals: each must exit 1 naming a template
#      offset, never emit (D26: the wording is not pinned, the offset is).
#   3. the header contract (§R3.8, §R3.11): a subst header with no rx block
#      of its abi does not compile; `-o -` is one self-contained `.c`; an rx
#      and a subst header of one prefix, and subst headers whose prefixes
#      differ only in case, share a translation unit.
#   4. the cells again with the artifacts and driver under AddressSanitizer +
#      UBSan (the glue's stack batch buffer, S1364, is an overrun ASan sees
#      on any box; a stack canary only on some). ASAN=0 skips it.
#
# Without libpcre2 the oracle arms are not run and the section says so
# (`SKIP: subst oracle`); every other arm still runs.
# env: PCREC, CC, GENCFLAGS, KEEP=1
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
if [ -z "${PCRE2_AVAILABLE:-}" ]; then
    . "$ROOT_DIR/tests/lib/resolve_pcre2.sh"
fi
export PCREC CC GENCFLAGS PCRE2_AVAILABLE PCRE2_CFLAGS="${PCRE2_CFLAGS:-}" PCRE2_LIBS="${PCRE2_LIBS:-}"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
[ "$PCRE2_AVAILABLE" = 1 ] || echo "SKIP: subst oracle (no linkable libpcre2-8): the pcre2 arms do not run"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/subst.XXXXXX")"
[ "${KEEP:-0}" = 1 ] || trap 'rm -rf "$WORK"' EXIT

pass=0 fail=0
ok()  { pass=$((pass + 1)); }
bad() { fail=$((fail + 1)); echo "FAIL: $*"; }

# ---- 1. the cells ----------------------------------------------------------
python3 -I "$SCRIPT_DIR/run_subst_tests.py" "$WORK/cells" "$SCRIPT_DIR/cells.tsv" > "$WORK/cells.log" 2>&1
rc=$?
cat "$WORK/cells.log"
p="$(sed -n 's/^checks passed: //p' "$WORK/cells.log")"
f="$(sed -n 's/^checks failed: //p' "$WORK/cells.log")"
pass=$((pass + ${p:-0})); fail=$((fail + ${f:-1}))
[ "$rc" = 0 ] || [ "${f:-1}" != 0 ] || bad "run_subst_tests.py exited $rc"

# ---- 2. refusals: TEMPLATE<TAB>OFFSET ----------------------------------------
while IFS=$'\t' read -r tmpl off; do
    case "$tmpl" in ''|'#'*) continue ;; esac
    if "$TIMEOUT_BIN" 60 "$PCREC" -p s -o "$WORK/r.c" --subst "$tmpl" > /dev/null 2> "$WORK/r.err"; then
        bad "template '$tmpl' compiled; want a refusal at offset $off"
    elif grep -q "(template offset $off)\$" "$WORK/r.err"; then ok
    else bad "template '$tmpl': $(head -1 "$WORK/r.err"), want template offset $off"
    fi
done <<'EOF'
$	0
ab$	2
$ 	0
${1	0
${1:-x}	0
${n:+y}	0
${	2
${}	2
$*MARK	0
${*MARK}	0
x$99999	1
${LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL}	0
x$LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL	1
$+	0
${&}	2
EOF
# under -e utf8 the template is UTF-checked (§2¶3) and names take \p{L}
# (§2¶1a); under byte the same name is refused
for t in "$(printf '[\xff]')" "$(printf 'ab\xc3')"; do
    if "$TIMEOUT_BIN" 60 "$PCREC" -p s -e utf8 -o "$WORK/r.c" --subst "$t" > /dev/null 2> "$WORK/r.err"; then
        bad "an ill-formed utf8 template compiled"
    elif grep -q '(template offset [12])$' "$WORK/r.err"; then ok
    else bad "ill-formed utf8 template: $(head -1 "$WORK/r.err")"
    fi
done
for t in "$(printf '[${\xc3\xa9}]')" "$(printf '[$\xc3\xa9x1]')"; do
    if "$TIMEOUT_BIN" 60 "$PCREC" -p s -e utf8 -o "$WORK/r.c" --subst "$t" > /dev/null 2> "$WORK/r.err" &&
       grep -q '"\\303\\251' "$WORK/r.c"; then ok
    else bad "utf8 template '$t' did not compile to a named row: $(head -1 "$WORK/r.err")"
    fi
    if "$TIMEOUT_BIN" 60 "$PCREC" -p s -o "$WORK/r.c" --subst "$t" > /dev/null 2>&1; then
        bad "byte template '$t' compiled (a byte >= 0x80 names nothing under byte)"
    else ok; fi
done
# the subst-block names reserve their families (cli.md §1.6¶2 row 4), on
# both compile paths
for pfx in rx_shape rx_subst rx_subst_x rx_group pcrec_subst; do
    if "$TIMEOUT_BIN" 60 "$PCREC" -p "$pfx" -o "$WORK/r.c" --subst 'x' > /dev/null 2>&1; then bad "prefix $pfx compiled a subst"; else ok; fi
    if "$TIMEOUT_BIN" 60 "$PCREC" -p "$pfx" -o "$WORK/r.c" --pattern 'a' > /dev/null 2>&1; then bad "prefix $pfx compiled an rx"; else ok; fi
done
if "$TIMEOUT_BIN" 60 "$PCREC" -p rx_shapes -o "$WORK/r.c" --subst 'x' > /dev/null 2>&1; then ok; else bad "prefix rx_shapes (no family) was refused"; fi
# every pattern-compile option is refused with --subst, never ignored (§5¶1)
for fl in -i --no-captures --engine=vm --emit-main --trace "--features all" --ucp --max-nfa-states=99999999; do
    if "$TIMEOUT_BIN" 60 "$PCREC" $fl -p s -o "$WORK/r.c" --subst 'x' > /dev/null 2>&1; then bad "--subst accepted $fl"; else ok; fi
done
if "$TIMEOUT_BIN" 60 "$PCREC" -e utf8 -p s -o "$WORK/r.c" --subst 'x' > /dev/null 2>&1; then ok; else bad "--subst refused -e utf8"; fi
if "$TIMEOUT_BIN" 60 "$PCREC" -p 'a__b' -o "$WORK/r.c" --subst 'x' > /dev/null 2>&1; then
    bad "a reserved prefix (a__b) compiled a subst"
else ok; fi
if "$TIMEOUT_BIN" 60 "$PCREC" -p s -o "$WORK/r.c" --subst 'x' --pattern 'a' > /dev/null 2>&1; then
    bad "--subst with --pattern was accepted"
else ok; fi
for u in error empty; do
    if "$TIMEOUT_BIN" 60 "$PCREC" -p s -o "$WORK/r.c" --unset=$u --pattern 'a' > /dev/null 2>&1; then
        bad "--unset=$u without --subst was accepted"
    else ok; fi
done

# ---- 3. the header contract ------------------------------------------------
"$TIMEOUT_BIN" 60 "$PCREC" -p hs -o "$WORK/hs.c" --subst '<$1>' || bad "hs did not compile"
printf '#define PCREC_RX_ABI_H 1\n#include "hs.h"\n' > "$WORK/abi.c"
if "$CC" $GENCFLAGS -fsyntax-only -I "$WORK" "$WORK/abi.c" 2> "$WORK/abi.err"; then
    bad "a subst header compiled beside an rx block of another abi"
elif grep -q 'regenerate' "$WORK/abi.err"; then ok
else bad "abi mismatch failed without the #error: $(head -2 "$WORK/abi.err")"
fi
if "$TIMEOUT_BIN" 60 "$PCREC" -p so -o - --subst '[$0]' > "$WORK/so.c" &&
   "$CC" $GENCFLAGS -c -o "$WORK/so.o" "$WORK/so.c" 2> "$WORK/so.err"; then ok
else bad "-o - is not one self-contained .c: $(head -2 "$WORK/so.err" 2>/dev/null)"
fi
for h in "$WORK/hs.h" "$WORK/hs.c"; do
    if LC_ALL=C grep -q '[^[:print:][:space:]]' "$h"; then bad "$(basename "$h") is not ASCII"; else ok; fi
done
grep -q '^#define HS_NVREFS 1$' "$WORK/hs.h" && ok || bad "hs.h carries no HS_NVREFS 1"
# an rx and a subst artifact of ONE prefix, and two subst artifacts whose
# prefixes differ only in case, in one translation unit (§1¶3)
mkdir -p "$WORK/tu"
if "$TIMEOUT_BIN" 60 "$PCREC" --features all -p pair -o "$WORK/tu/pair.c" --pattern '(a)' &&
   "$TIMEOUT_BIN" 60 "$PCREC" -p pair -o "$WORK/tu/pair_sub.c" --subst '[$1]' &&
   "$TIMEOUT_BIN" 60 "$PCREC" -p sq -o "$WORK/tu/sq.c" --subst '<$0>' &&
   "$TIMEOUT_BIN" 60 "$PCREC" -p sQ -o "$WORK/tu/sQ.c" --subst '[$0]'; then
    printf '%s\n' '#include "pair.h"' '#include "pair_sub.h"' '#include "sq.h"' '#include "sQ.h"' \
        'int main(void) { rx_subst_binding b; rx_subst_run r[PAIR_NREFS]; int bad;' \
        '    return pcrec_subst_bind(&b, &pair_info, &pair_subst_info, r, 1, 0, 0, &bad)' \
        '        || sq_subst_info.render == sQ_subst_info.render; }' > "$WORK/tu/main.c"
    if "$CC" $GENCFLAGS -I "$WORK/tu" -o "$WORK/tu/main" "$WORK/tu/main.c" "$WORK/tu/pair.c" \
           "$WORK/tu/pair_sub.c" "$WORK/tu/sq.c" "$WORK/tu/sQ.c" 2> "$WORK/tu/err" && "$WORK/tu/main"; then ok
    else bad "rx+subst of one prefix, or sq+sQ, in one TU: $(head -3 "$WORK/tu/err")"; fi
else bad "the one-TU artifacts did not compile"; fi

# ---- 4. the cells under ASan + UBSan ----------------------------------------
if [ "${ASAN:-1}" = 1 ]; then
    if printf 'int main(void){return 0;}\n' | "$CC" -fsanitize=address -x c - -o "$WORK/asanprobe" 2>/dev/null; then
        GENCFLAGS="-O1 -g -std=gnu11 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer" \
            ASAN_OPTIONS=detect_leaks=0 \
            python3 -I "$SCRIPT_DIR/run_subst_tests.py" "$WORK/asan" "$SCRIPT_DIR/cells.tsv" > "$WORK/asan.log" 2>&1
        rc=$?
        sed 's/^/asan: /' "$WORK/asan.log" | grep -v '^asan: checks '
        p="$(sed -n 's/^checks passed: //p' "$WORK/asan.log")"
        f="$(sed -n 's/^checks failed: //p' "$WORK/asan.log")"
        pass=$((pass + ${p:-0})); fail=$((fail + ${f:-1}))
        [ "$rc" = 0 ] || [ "${f:-1}" != 0 ] || bad "the ASan pass of run_subst_tests.py exited $rc"
    else
        echo "SKIP: subst asan (the compiler cannot build -fsanitize=address)"
    fi
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" = 0 ]
