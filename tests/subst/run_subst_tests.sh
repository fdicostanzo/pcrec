#!/usr/bin/env bash
# tests/subst/run_subst_tests.sh -- [M4-SUBST] `make test-subst`: the subst
# artifact's checks (docs/spec/subst.md, replace_design.md §R3).
#
#   1. run_subst_tests.py over cells.tsv: every cell's stated answer, the
#      generic arms (sizing, NOSPACE, the k = 1 glue, the dirty iterator, the
#      foreign ncap, the LIMIT stop), and libpcre2's pcre2_substitute where it
#      can answer (its header).
#   2. the template compiler's refusals: each must exit 1 naming a template
#      offset, never emit (D26: the wording is not pinned, the offset is).
#   3. the header contract (§R3.8, §R3.11): a subst header with no rx block
#      of its abi does not compile; `-o -` is one self-contained `.c`.
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
    if "$PCREC" -p s -o "$WORK/r.c" --subst "$tmpl" > /dev/null 2> "$WORK/r.err"; then
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
EOF
if "$PCREC" -p 'a__b' -o "$WORK/r.c" --subst 'x' > /dev/null 2>&1; then
    bad "a reserved prefix (a__b) compiled a subst"
else ok; fi
if "$PCREC" -p s -o "$WORK/r.c" --subst 'x' --pattern 'a' > /dev/null 2>&1; then
    bad "--subst with --pattern was accepted"
else ok; fi
if "$PCREC" -p s -o "$WORK/r.c" --unset=error --pattern 'a' > /dev/null 2>&1; then
    bad "--unset= without --subst was accepted"
else ok; fi

# ---- 3. the header contract ------------------------------------------------
"$PCREC" -p hs -o "$WORK/hs.c" --subst '<$1>' || bad "hs did not compile"
printf '#define PCREC_RX_ABI_H 1\n#include "hs.h"\n' > "$WORK/abi.c"
if "$CC" $GENCFLAGS -fsyntax-only -I "$WORK" "$WORK/abi.c" 2> "$WORK/abi.err"; then
    bad "a subst header compiled beside an rx block of another abi"
elif grep -q 'regenerate' "$WORK/abi.err"; then ok
else bad "abi mismatch failed without the #error: $(head -2 "$WORK/abi.err")"
fi
if "$PCREC" -p so -o - --subst '[$0]' > "$WORK/so.c" &&
   "$CC" $GENCFLAGS -c -o "$WORK/so.o" "$WORK/so.c" 2> "$WORK/so.err"; then ok
else bad "-o - is not one self-contained .c: $(head -2 "$WORK/so.err" 2>/dev/null)"
fi
for h in "$WORK/hs.h" "$WORK/hs.c"; do
    if LC_ALL=C grep -q '[^[:print:][:space:]]' "$h"; then bad "$(basename "$h") is not ASCII"; else ok; fi
done

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" = 0 ]
