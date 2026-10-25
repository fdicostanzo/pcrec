#!/usr/bin/env bash
# tests/subst/run_subst_tests.sh -- [M4-SUBST] `make test-subst`: the subst
# artifact's checks (docs/spec/subst_api.md, replace_design.md §R4).
#
#   1. run_subst_tests.py over cells.tsv, then over module subst-extended's
#      tests/subst-extended/cells.tsv: every cell's stated answer through
#      the spec's recipes and replace-all, the generic arms (its header), and
#      libpcre2's pcre2_substitute where it can answer.
#   2. the template compiler's refusals: each must exit 1 naming a template
#      offset, never emit (D26: the wording is not pinned, the offset is);
#      the reserved prefixes and the refused options; under `--features
#      subst-extended`, the module's own refusals (§2¶8-¶12).
#   3. the header contract (§1¶3, §10): a subst header with no rx block of
#      its abi does not compile; `-o -` is one self-contained `.c`; an rx and
#      a subst header of one prefix share a translation unit, and two subst
#      headers whose prefixes differ only in case do not (the #error).
#   4. the support unit (`--emit-support`, §10¶2, cli.md §1.20): needs no
#      argument, refuses any, writes identical bytes twice, is ASCII, and
#      builds both ways (PCREC_SUPPORT_IMPLEMENTATION in one TU beside a
#      declarations-only TU; PCREC_SUPPORT_STATIC alone).
#   5. the cells again with the artifacts and driver under AddressSanitizer +
#      UBSan (replace-all's stack batch and exact-capacity buffers are
#      overruns ASan sees on any box). ASAN=0 skips it.
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
EXT_CELLS="$ROOT_DIR/tests/subst-extended/cells.tsv"
for cells in "$SCRIPT_DIR/cells.tsv" "$EXT_CELLS"; do
    tag="$(basename "$(dirname "$cells")")"
    python3 -I "$SCRIPT_DIR/run_subst_tests.py" "$WORK/$tag" "$cells" > "$WORK/$tag.log" 2>&1
    rc=$?
    sed "s/^/$tag: /" "$WORK/$tag.log" | grep -v "^$tag: checks "
    p="$(sed -n 's/^checks passed: //p' "$WORK/$tag.log")"
    f="$(sed -n 's/^checks failed: //p' "$WORK/$tag.log")"
    pass=$((pass + ${p:-0})); fail=$((fail + ${f:-1}))
    [ "$rc" = 0 ] || [ "${f:-1}" != 0 ] || bad "run_subst_tests.py over $tag exited $rc"
done

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
# module subst-extended's refusals, each at its offset (§2¶8-¶12): a
# backslash + two digits, an escape not in the table, a trailing backslash,
# a \Q left open in conditional text, the operators that are not
# conditionals, malformed escapes, nesting past PCREC_MAX_TEMPLATE_NESTING
nest11="$(printf '${1:+%.0s' 1 2 3 4 5 6 7 8 9 10 11)x}}}}}}}}}}}"
while IFS=$'\t' read -r enc tmpl off; do
    case "$enc" in ''|'#'*) continue ;; esac
    [ "$tmpl" = NEST11 ] && tmpl="$nest11"
    if "$TIMEOUT_BIN" 60 "$PCREC" -p s -e "$enc" --features subst-extended -o "$WORK/r.c" --subst "$tmpl" > /dev/null 2> "$WORK/r.err"; then
        bad "extended template '$tmpl' ($enc) compiled; want a refusal at offset $off"
    elif grep -q "(template offset $off)\$" "$WORK/r.err"; then ok
    else bad "extended template '$tmpl' ($enc): $(head -1 "$WORK/r.err"), want template offset $off"
    fi
done <<'EOF'
byte	\10	0
byte	a\101	1
byte	\81	0
byte	\q	0
byte	\d	0
byte	ab\	2
byte	${1:-\Qa}	5
byte	${1:-x	6
byte	${1:=x}	0
byte	${1:?x}	0
byte	${1:}	0
byte	${1:x}	0
byte	${1-x}	0
byte	${1+x}	0
byte	${!v:-x}	0
byte	\x{100}	0
byte	\N{U+41}	0
byte	\o{}	0
byte	\o{18}	0
byte	\o	0
byte	\x{}	0
byte	\x{41	0
byte	\xg	0
byte	\c	0
byte	x\N	1
utf8	\x{110000}	0
utf8	\x{d800}	0
utf8	\N{U+}	0
utf8	\N{41}	0
utf8	\N{u+41}	0
byte	NEST11	50
EOF
# a 10-deep nest compiles; `--features subst-extended` is the only module
# --subst takes (§5¶1), and the module's forms refuse without it (§2¶4)
nest10="$(printf '${1:+%.0s' 1 2 3 4 5 6 7 8 9 10)x}}}}}}}}}}"
if "$TIMEOUT_BIN" 60 "$PCREC" -p s --features subst-extended -o "$WORK/r.c" --subst "$nest10" > /dev/null 2>&1; then ok
else bad "a 10-deep conditional was refused"; fi
for fl in "--features all" "--features subst-extended,vars" "--features std1"; do
    if "$TIMEOUT_BIN" 60 "$PCREC" $fl -p s -o "$WORK/r.c" --subst 'x' > /dev/null 2>&1; then bad "--subst accepted $fl"; else ok; fi
done
for t in '${1:+a}' '${1:-a}'; do
    if "$TIMEOUT_BIN" 60 "$PCREC" -p s -o "$WORK/r.c" --subst "$t" > /dev/null 2> "$WORK/r.err"; then
        bad "'$t' compiled without module subst-extended"
    elif grep -q "requires module 'subst-extended'" "$WORK/r.err"; then ok
    else bad "'$t' without the module: $(head -1 "$WORK/r.err")"; fi
done
"$TIMEOUT_BIN" 60 "$PCREC" -p sx --features subst-extended -o "$WORK/sx.c" --subst '\U$1' &&
    grep -q '^#define SX_SUBST_MODULES "subst,subst-extended"$' "$WORK/sx.c" && ok ||
    bad "an extended artifact does not stamp SX_SUBST_MODULES subst,subst-extended"
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
# ONE group-name grammar (pcrec_group_name_cp): under utf8 a name the pattern
# side declares is a name the template can reference, and one it refuses the
# template refuses too; each row's answer is libpcre2 10.46's for (?<NAME>x)
# (U+0663 is Nd, never first; U+2170 is Nl, never a name)
while IFS='	' read -r nm want; do
    nm="$(printf "$nm")"
    "$TIMEOUT_BIN" 60 "$PCREC" -e utf8 --features named-groups -p r -o "$WORK/r.c" --pattern "(?<$nm>x)" > /dev/null 2>&1
    a=$?
    "$TIMEOUT_BIN" 60 "$PCREC" -e utf8 -p s -o "$WORK/r.c" --subst "\${$nm}" > /dev/null 2>&1
    b=$?
    if [ "$a" = "$want" ] && [ "$b" = "$want" ]; then ok
    else bad "group name '$nm': pattern side rc $a, template side rc $b, want $want on both"; fi
done <<'NAMES'
\xc3\xa9	0
a\xd9\xa3	0
\xd9\xa3	1
_	0
a_1	0
1a	1
\xe2\x85\xb0	1
NAMES
# the subst-block and support-unit names reserve their families (cli.md
# §1.6¶2 row 4), on both compile paths
for pfx in pcrec PCREC pcrec_subst Pcrec_Subst_x pcrec_support pcrec_subst_support_id; do
    if "$TIMEOUT_BIN" 60 "$PCREC" -p "$pfx" -o "$WORK/r.c" --subst 'x' > /dev/null 2>&1; then bad "prefix $pfx compiled a subst"; else ok; fi
    if "$TIMEOUT_BIN" 60 "$PCREC" -p "$pfx" -o "$WORK/r.c" --pattern 'a' > /dev/null 2>&1; then bad "prefix $pfx compiled an rx"; else ok; fi
done
for pfx in rx_shape pcrec_supports pcrecx pcrec_x rx_subst rx_group; do     # no family
    if "$TIMEOUT_BIN" 60 "$PCREC" -p $pfx -o "$WORK/r.c" --subst 'x' > /dev/null 2>&1; then ok; else bad "prefix $pfx (no family) was refused"; fi
done
# every documented option is refused with --subst and with --emit-support by
# its PRESENCE, a default value included (§5¶1, §10¶2); the population is
# --help's and --list-axes' own (cli_option_census.py)
"$TIMEOUT_BIN" 900 python3 -I "$SCRIPT_DIR/cli_option_census.py" "$PCREC" "$WORK/census" > "$WORK/census.log" 2>&1
crc=$?
grep -v '^checks ' "$WORK/census.log"
p="$(sed -n 's/^checks passed: //p' "$WORK/census.log")"
f="$(sed -n 's/^checks failed: //p' "$WORK/census.log")"
pass=$((pass + ${p:-0})); fail=$((fail + ${f:-1}))
[ "$crc" = 0 ] || [ "${f:-1}" != 0 ] || bad "cli_option_census.py exited $crc"
if "$TIMEOUT_BIN" 60 "$PCREC" -p 'a__b' -o "$WORK/r.c" --subst 'x' > /dev/null 2>&1; then
    bad "a reserved prefix (a__b) compiled a subst"
else ok; fi
if "$TIMEOUT_BIN" 60 "$PCREC" -p s -o "$WORK/r.c" --subst 'x' --pattern 'a' > /dev/null 2>&1; then
    bad "--subst with --pattern was accepted"
else ok; fi
# unset handling is a flag of the call (PCREC_SUBST_STRICT), not an option:
# --unset= is unknown on every path (cli.md §1.19¶1)
for u in error empty; do
    for mode in "--pattern a" "--subst x"; do
        if "$TIMEOUT_BIN" 60 "$PCREC" -p s -o "$WORK/r.c" --unset=$u $mode > /dev/null 2>&1; then
            bad "--unset=$u with $mode was accepted"
        else ok; fi
    done
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
# a case region over every item kind, both encodings: ASCII, and clean under
# -Wshadow too (its locals and voids follow what its items read)
i=0
for t in '\Ux' '\U$1' '\U${1:+a:b}' '\U$0' '\U${!v}' '\U$_' '\U$`' "\\U\$'" '\U${0:+a:b}' 'a\u$1\E${!v}' '\L${n}' '${1:+\Ua:b}'; do
    i=$((i + 1))
    for e in byte utf8; do
        if "$TIMEOUT_BIN" 60 "$PCREC" -e $e --features subst-extended -p cr$i -o "$WORK/cr$i$e.c" --subst "$t" 2> "$WORK/cr.err" &&
           "$CC" $GENCFLAGS -Wshadow -c -I "$WORK" -o "$WORK/cr.o" "$WORK/cr$i$e.c" 2> "$WORK/cr.err"; then ok
        else bad "case region '$t' ($e): $(head -2 "$WORK/cr.err")"; fi
        if LC_ALL=C grep -q '[^[:print:][:space:]]' "$WORK/cr$i$e.c"; then bad "case region '$t' ($e) is not ASCII"; else ok; fi
    done
done
# an rx and a subst artifact of ONE prefix, and two subst artifacts of
# different prefixes, in one translation unit, the numbered-reference
# assert of §3¶3 included; two whose prefixes differ only in case are the
# #error (§1¶3)
mkdir -p "$WORK/tu"
if "$TIMEOUT_BIN" 60 "$PCREC" --features all -p pair -o "$WORK/tu/pair.c" --pattern '(a)' &&
   "$TIMEOUT_BIN" 60 "$PCREC" -p pair -o "$WORK/tu/pair_sub.c" --subst '[$1]' &&
   "$TIMEOUT_BIN" 60 "$PCREC" -p sq -o "$WORK/tu/sq.c" --subst '<$0>' &&
   "$TIMEOUT_BIN" 60 "$PCREC" -p sQ -o "$WORK/tu/sQ.c" --subst '[$0]' &&
   "$TIMEOUT_BIN" 60 "$PCREC" -p sr -o "$WORK/tu/sr.c" --subst '[$0]'; then
    printf '%s\n' '#include "pair.h"' '#include "pair_sub.h"' '#include "sq.h"' '#include "sr.h"' \
        '_Static_assert(PAIR_MAXNUM < PAIR_NCAPS, "a numbered reference past the pattern");' \
        'int main(void) { rx_ctx ctx; rx_var vres[PAIR_NVREFS]; int bad;' \
        '    rx_iter it = RX_ITER_INIT((const unsigned char *)"a", 1);' \
        '    return pcrec_subst_ctx_init(&ctx, &it, &pair_info, &pair_subst_info, NULL, vres, 0, &bad)' \
        '        || sq_subst_info.render == sr_subst_info.render; }' > "$WORK/tu/main.c"
    # the guard probe compiles whatever the guards are, so a colliding guard
    # (the subst header dropped behind the rx header's) is caught by this
    # cell and not by the next one's compile error
    printf '%s\n' '#include "pair.h"' '#include "pair_sub.h"' \
        'int main(void) {' '#ifdef PCREC_SUBST_GEN_pair_H' '    return 0;' '#else' '    return 1;' '#endif' '}' > "$WORK/tu/guard.c"
    if "$CC" -I "$WORK/tu" -o "$WORK/tu/guard" "$WORK/tu/guard.c" 2> "$WORK/tu/guard.err" && "$WORK/tu/guard"; then ok
    else bad "pair.h + pair_sub.h in one TU: the subst header was dropped (its guard is not its own)"; guard_bad=1; fi
    if "$CC" $GENCFLAGS -I "$WORK/tu" -o "$WORK/tu/main" "$WORK/tu/main.c" "$WORK/tu/pair.c" \
           "$WORK/tu/pair_sub.c" "$WORK/tu/sq.c" "$WORK/tu/sr.c" 2> "$WORK/tu/err" && "$WORK/tu/main"; then ok
    elif [ "${guard_bad:-0}" = 1 ]; then bad "rx+subst of one prefix, or sq+sr, in one TU (see the guard cell)"
    else bad "rx+subst of one prefix, or sq+sr, in one TU: $(head -3 "$WORK/tu/err")"; fi
    printf '%s\n' '#include "sq.h"' '#include "sQ.h"' > "$WORK/tu/case.c"
    if "$CC" $GENCFLAGS -fsyntax-only -I "$WORK/tu" "$WORK/tu/case.c" 2> "$WORK/tu/case.err"; then
        bad "sq.h and sQ.h shared a translation unit"
    elif grep -q 'differ only in case' "$WORK/tu/case.err"; then ok
    else bad "sq.h + sQ.h failed without the #error: $(head -2 "$WORK/tu/case.err")"; fi
else bad "the one-TU artifacts did not compile"; fi

# ---- 4. the support unit ---------------------------------------------------
mkdir -p "$WORK/sup"
if "$TIMEOUT_BIN" 60 "$PCREC" --emit-support > "$WORK/sup/a.h" &&
   "$TIMEOUT_BIN" 60 "$PCREC" --emit-support -o "$WORK/sup/b.h" &&
   "$TIMEOUT_BIN" 60 "$PCREC" --emit-support -o - > "$WORK/sup/c.h"; then
    if cmp -s "$WORK/sup/a.h" "$WORK/sup/b.h" && cmp -s "$WORK/sup/a.h" "$WORK/sup/c.h"; then ok
    else bad "--emit-support wrote different bytes on stdout, -o FILE and -o -"; fi
    if LC_ALL=C grep -q '[^[:print:][:space:]]' "$WORK/sup/a.h"; then bad "the support unit is not ASCII"; else ok; fi
    grep -q 'pcrec_subst_support_id = 0x[0-9a-f]\{16\}ull;' "$WORK/sup/a.h" && ok || bad "the support unit defines no 64-bit content id"
else bad "--emit-support failed"; fi
for extra in "-p x" "--pattern a" "--subst x" "-e utf8" "--features all" "-i" "--emit-main"; do
    if "$TIMEOUT_BIN" 60 "$PCREC" --emit-support $extra -o "$WORK/sup/r.h" > /dev/null 2>&1; then
        bad "--emit-support accepted $extra"
    else ok; fi
done
printf '%s\n' '#define PCREC_SUPPORT_IMPLEMENTATION' '#include "a.h"' > "$WORK/sup/impl.c"
printf '%s\n' '#include "a.h"' '#include "pair_sub.h"' \
    'int main(void) { pcrec_subst_piece p[2] = { { (const unsigned char *)"ab", 2 }, { (const unsigned char *)"c", 1 } };' \
    '    unsigned char b[4]; return pcrec_subst_flatten(p, 2, b, sizeof b) != 3 || memcmp(b, "abc", 3); }' > "$WORK/sup/use.c"
printf '%s\n' '#define PCREC_SUPPORT_STATIC' '#include "a.h"' \
    'int main(void) { return pcrec_subst_flatten((const pcrec_subst_piece *)0, 0, (unsigned char *)0, 0) != 0; }' > "$WORK/sup/st.c"
if "$CC" $GENCFLAGS -I "$WORK/sup" -I "$WORK/tu" -o "$WORK/sup/use" "$WORK/sup/use.c" "$WORK/sup/impl.c" \
       "$WORK/tu/pair_sub.c" 2> "$WORK/sup/err" && "$WORK/sup/use"; then ok
else bad "the support unit as an implementation TU + a user TU: $(head -3 "$WORK/sup/err")"; fi
if "$CC" $GENCFLAGS -I "$WORK/sup" -o "$WORK/sup/st" "$WORK/sup/st.c" 2> "$WORK/sup/err" && "$WORK/sup/st"; then ok
else bad "the support unit under PCREC_SUPPORT_STATIC: $(head -3 "$WORK/sup/err")"; fi

# ---- 5. the cells under ASan + UBSan ----------------------------------------
if [ "${ASAN:-1}" = 1 ]; then
    if printf 'int main(void){return 0;}\n' | "$CC" -fsanitize=address -x c - -o "$WORK/asanprobe" 2>/dev/null; then
        GENCFLAGS="-O1 -g -std=gnu11 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer" \
            ASAN_OPTIONS=detect_leaks=0 \
            python3 -I "$SCRIPT_DIR/run_subst_tests.py" "$WORK/asan" "$SCRIPT_DIR/cells.tsv" > "$WORK/asan.log" 2>&1
        rc=$?
        GENCFLAGS="-O1 -g -std=gnu11 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer" \
            ASAN_OPTIONS=detect_leaks=0 \
            python3 -I "$SCRIPT_DIR/run_subst_tests.py" "$WORK/asanx" "$EXT_CELLS" > "$WORK/asanx.log" 2>&1
        rcx=$?
        for lg in asan asanx; do
            sed "s/^/$lg: /" "$WORK/$lg.log" | grep -v "^$lg: checks "
            p="$(sed -n 's/^checks passed: //p' "$WORK/$lg.log")"
            f="$(sed -n 's/^checks failed: //p' "$WORK/$lg.log")"
            pass=$((pass + ${p:-0})); fail=$((fail + ${f:-1}))
            r=$rc; [ "$lg" = asanx ] && r=$rcx
            [ "$r" = 0 ] || [ "${f:-1}" != 0 ] || bad "the ASan pass of run_subst_tests.py ($lg) exited $r"
        done
    else
        echo "SKIP: subst asan (the compiler cannot build -fsanitize=address)"
    fi
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" = 0 ]
