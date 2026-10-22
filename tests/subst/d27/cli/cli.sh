#!/bin/bash
# substd27 CLI + header-composition cases (subst_api.md §1, §5, §6¶6, §7¶5).
# usage: cli/cli.sh [PCREC]     prints PASS/FAIL per case and a total
set -u
# substfix (adoption): paths, the timeout binary and the compiler from the
# environment ($OUT is required).
D=$(cd "$(dirname "$0")" && pwd)
P=${1:-${PCREC:-$D/../../../../build/pcrec}}
O=${OUT:?OUT must name a scratch directory}
rm -rf "$O"; mkdir -p "$O"
T="${TIMEOUT_BIN:-timeout} 60"
gcc() { command "${CC:-gcc}" "$@"; }
np=0; nf=0
ok()  { np=$((np+1)); echo "PASS $1"; }
bad() { nf=$((nf+1)); echo "FAIL $1: $2"; }
# expect_rc ID WANT(0|nz) cmd...   (stderr kept in $O/ID.err)
expect_rc() {
  id=$1; want=$2; shift 2
  "$@" > "$O/$id.out" 2> "$O/$id.err"; rc=$?
  if [ "$want" = 0 ] && [ $rc -eq 0 ]; then ok "$id";
  elif [ "$want" = nz ] && [ $rc -ne 0 ] && [ $rc -lt 124 ] && [ -s "$O/$id.err" ]; then ok "$id";
  else bad "$id" "exit $rc, stderr: $(head -c 300 "$O/$id.err")"; fi
}

# ---- §5¶1 mode exclusivity
printf '$1' > "$O/t.tpl"
expect_rc both.subst.and.file nz $T "$P" -o "$O/x.c" --subst '$1' --subst-file "$O/t.tpl"
expect_rc subst.and.pattern   nz $T "$P" -o "$O/x.c" --subst '$1' --pattern 'a'
expect_rc substfile.and.pattern nz $T "$P" -o "$O/x.c" --subst-file "$O/t.tpl" --pattern 'a'
printf 'pattern a\n' > "$O/f.rxt"
expect_rc subst.and.fileop    nz $T "$P" -o "$O/x.c" --subst '$1' "$O/f.rxt"
expect_rc subst.and.listsyntax nz $T "$P" --subst '$1' --list-syntax
expect_rc subst.and.emitir    nz $T "$P" --subst '$1' --emit-ir
expect_rc subst.and.countgroups nz $T "$P" --subst '$1' --count-groups
expect_rc subst.twice         nz $T "$P" -o "$O/x.c" --subst '$1' --subst '$2'
expect_rc unset.without.subst nz $T "$P" -o "$O/x.c" --unset=error --pattern 'a'
expect_rc unset.bogus         nz $T "$P" -o "$O/x.c" --unset=bogus --subst '$1'
expect_rc unset.empty.value   nz $T "$P" -o "$O/x.c" --unset= --subst '$1'
expect_rc unset.EMPTY.case    nz $T "$P" -o "$O/x.c" --unset=EMPTY --subst '$1'
expect_rc substfile.missing   nz $T "$P" -o "$O/x.c" --subst-file "$O/nope.tpl"
expect_rc substfile.dir       nz $T "$P" -o "$O/x.c" --subst-file "$O"
expect_rc subst.no.o          nz $T "$P" --subst '$1'
expect_rc subst.no.value      nz $T "$P" -o "$O/x.c" --subst
# -p rules (cli.md §1.6)
expect_rc prefix.dash         nz $T "$P" -p a-b -o "$O/x.c" --subst '$1'
expect_rc prefix.digit        nz $T "$P" -p 1x -o "$O/x.c" --subst '$1'
expect_rc prefix.empty        nz $T "$P" -p '' -o "$O/x.c" --subst '$1'
expect_rc prefix.dunder       nz $T "$P" -p a__b -o "$O/x.c" --subst '$1'
expect_rc prefix.61           nz $T "$P" -p "$(printf 'a%.0s' $(seq 61))" -o "$O/x.c" --subst '$1'
expect_rc prefix.60           0  $T "$P" -p "$(printf 'a%.0s' $(seq 60))" -o "$O/p60.c" --subst '$1'
# compile flags that mean nothing to a template: refused, or ignored? (§5¶1 is silent)
for fl in "-e utf8" "-i" "--no-captures" "--engine=vm" "--emit-main" "--features all" "--trace"; do
  id="flag.$(echo "$fl" | tr -c 'a-z0-9\n' '_')"
  $T "$P" $fl -p fx -o "$O/fx.c" --subst '$1' > /dev/null 2> "$O/$id.err"; rc=$?
  echo "INFO $id exit $rc: $(head -c 160 "$O/$id.err")"
done

# ---- §2¶3 refusals: exit nonzero, a template offset in the diagnostic
for t in '$' 'ab$' '${' 'x${1' '${}' '${1a}' '$*MARK' '${*MARK}' '${1:-w}' '${1:+w}' '${n-w}' '$65536' 'ab$-'; do
  id="refuse.$(printf '%s' "$t" | od -An -tx1 | tr -d ' \n')"
  "$P" -o "$O/x.c" --subst "$t" > /dev/null 2> "$O/$id.err"; rc=$?
  if [ $rc -ne 0 ] && grep -q 'template offset [0-9]' "$O/$id.err"; then ok "$id ($t)"; else bad "$id ($t)" "exit $rc: $(cat "$O/$id.err")"; fi
done
# the offset points at the offending '$' (wording is not contract; the offset is)
"$P" -o "$O/x.c" --subst 'abc$' 2> "$O/off.err"; grep -q 'template offset 3' "$O/off.err" && ok refuse.offset.end || bad refuse.offset.end "$(cat "$O/off.err")"
"$P" -o "$O/x.c" --subst 'ab${1' 2> "$O/off2.err"; grep -qE 'template offset (2|5)' "$O/off2.err" && ok refuse.offset.brace || bad refuse.offset.brace "$(cat "$O/off2.err")"
# no artifact is left behind by a refused template
rm -f "$O/ref.c" "$O/ref.h"; "$P" -o "$O/ref.c" --subst 'x$' 2>/dev/null
[ ! -e "$O/ref.c" ] && [ ! -e "$O/ref.h" ] && ok refuse.no.output || bad refuse.no.output "a refused template left $(ls "$O"/ref.*)"

# ---- §1¶1 files, §5¶2 stamps
$T "$P" -p dmy -o "$O/dmy.c" --subst '[$1|${name}|$$]' 2>/dev/null
[ -s "$O/dmy.c" ] && [ -s "$O/dmy.h" ] && ok files.c.and.h || bad files.c.and.h "missing"
grep -q '^#define DMY_SUBST_UNSET "empty"' "$O/dmy.c" && ok stamp.unset.empty || bad stamp.unset.empty "$(grep SUBST_UNSET "$O/dmy.c")"
grep -q '^#define DMY_SUBST_MODULES "subst"' "$O/dmy.c" && ok stamp.modules.subst || bad stamp.modules.subst "$(grep MODULES "$O/dmy.c")"
grep -q 'DMY_SUBST_UNSET\|DMY_SUBST_MODULES' "$O/dmy.h" && bad stamp.c.only "the .h carries a .c-only stamp" || ok stamp.c.only
grep -q '^#define DMY_NREFS  *1' "$O/dmy.h" && grep -q '^#define DMY_NSEGS  *1' "$O/dmy.h" && grep -q '^#define DMY_MAXNUM  *1' "$O/dmy.h" \
  && ok stamp.h.constants || bad stamp.h.constants "$(grep -E 'DMY_(NREFS|NSEGS|MAXNUM)' "$O/dmy.h")"
$T "$P" -p dme --unset=error -o "$O/dme.c" --subst '${!v}$1' 2>/dev/null
grep -q '^#define DME_SUBST_UNSET "error"' "$O/dme.c" && ok stamp.unset.error || bad stamp.unset.error "$(grep SUBST_UNSET "$O/dme.c")"
grep -q '^#define DME_SUBST_MODULES "subst,subst-pcrec"' "$O/dme.c" && ok stamp.modules.pcrec || bad stamp.modules.pcrec "$(grep MODULES "$O/dme.c")"
# the declared order inside the .h: shared block, subst block, declarations
a=$(grep -n 'define PCREC_RX_ABI_H' "$O/dmy.h" | head -1 | cut -d: -f1); b=$(grep -n 'define PCREC_SUBST_H' "$O/dmy.h" | cut -d: -f1); c=$(grep -n 'extern const struct rx_subst_info dmy_subst_info' "$O/dmy.h" | cut -d: -f1)
[ -n "$a" ] && [ -n "$b" ] && [ -n "$c" ] && [ "$a" -lt "$b" ] && [ "$b" -lt "$c" ] && ok header.order || bad header.order "$a $b $c"
# --subst-file is byte for byte: NUL, CR, quotes, newline, high bytes
printf 'a"\x27\r\n\x00\xff$1\\' > "$O/raw.tpl"
$T "$P" -p raw -o "$O/raw.c" --subst-file "$O/raw.tpl" 2> "$O/raw.err" && ok substfile.raw.compiles || bad substfile.raw.compiles "$(cat "$O/raw.err")"
# empty template, empty file
$T "$P" -p emp -o "$O/emp.c" --subst '' 2> "$O/emp.err" && ok subst.empty || bad subst.empty "$(cat "$O/emp.err")"
: > "$O/empty.tpl"
$T "$P" -p empf -o "$O/empf.c" --subst-file "$O/empty.tpl" 2> "$O/empf.err" && ok substfile.empty || bad substfile.empty "$(cat "$O/empf.err")"
# a big template
head -c 200000 /dev/zero | tr '\0' 'x' > "$O/big.tpl"; printf '$1' >> "$O/big.tpl"
$T "$P" -p bigt -o "$O/bigt.c" --subst-file "$O/big.tpl" 2> "$O/bigt.err"; echo "INFO substfile.200k exit $?: $(head -c 200 "$O/bigt.err")"
# many references
python3 -c "print(''.join('\$%d' % (i % 9 + 1) for i in range(20000)), end='')" > "$O/many.tpl"
$T "$P" -p many -o "$O/many.c" --subst-file "$O/many.tpl" 2> "$O/many.err"; echo "INFO substfile.20000refs exit $?: $(head -c 200 "$O/many.err")"

# ---- §1¶5 self-contained -o -
( cd "$O" && $T "$P" -p sc -o - --subst '<$1>' > "$O/sc_stdout.c" 2> "$O/sc.err" ); rc=$?
[ $rc -eq 0 ] && [ ! -e "$O/sc.h" ] && [ ! -e "$O/-.h" ] && ok selfcontained.noheader || bad selfcontained.noheader "exit $rc"
grep -q 'define PCREC_RX_ABI_H' "$O/sc_stdout.c" && grep -q 'define PCREC_SUBST_H' "$O/sc_stdout.c" && ok selfcontained.blocks || bad selfcontained.blocks "missing a block"
$T "$P" --features all -p sr -o - --pattern '(a)(b)?' > "$O/sr_stdout.c" 2>/dev/null
cat > "$O/sc_main.c" <<'EOF'
#include "sr_stdout.c"
#include "sc_stdout.c"
#include <stdio.h>
int main(void) {
    rx_subst_binding b; rx_subst_run r[1]; int bad; size_t L, K; unsigned char o[64];
    if (pcrec_subst_bind(&b, &sr_info, &sc_subst_info, r, 1, NULL, 0, &bad)) return 2;
    rx_iter it = RX_ITER_INIT((const unsigned char *)"xab", 3);
    int rc = pcrec_subst(&b, &it, SIZE_MAX, o, 64, &L, &K);
    return !(rc == 0 && L == 4 && !memcmp(o, "x<a>", 4));
}
EOF
gcc -std=gnu11 -fsanitize=address,undefined -o "$O/sc_main" "$O/sc_main.c" 2> "$O/sc_main.err" && "$O/sc_main" && ok selfcontained.two.in.one.tu || bad selfcontained.two.in.one.tu "$(head -c 400 "$O/sc_main.err")"

# ---- §1¶3 include order and multiplicity; §1¶4 abi #error; §6¶6 PCREC_SUBST_PAIRS; §7¶5 example
$T "$P" --features all -p rx -o "$O/rx.c" --pattern '(a)(b)?' 2>/dev/null
$T "$P" --features all -p ra -o "$O/ra.c" --pattern '(x)(y)?' 2>/dev/null
$T "$P" -p s1 -o "$O/s1.c" --subst '[$1]' 2>/dev/null
$T "$P" -p s2 -o "$O/s2.c" --subst '<$0>' 2>/dev/null
SAN="-std=gnu11 -fsanitize=address,undefined -fno-sanitize-recover=undefined -g -I $O"
for f in rx ra s1 s2; do gcc $SAN -c -o "$O/$f.o" "$O/$f.c" || bad "cc.$f" "compile"; done
for order in "s1 rx" "rx s1" "s1 s2 rx ra" "s2 s1 s1 rx rx" "ra s2"; do
  id="include.$(echo $order | tr ' ' _)"
  { for h in $order; do echo "#include \"$h.h\""; done; cat "$D/inc_body.c"; } > "$O/$id.c"
  gcc $SAN -DHAVE_RX=$(echo " $order " | grep -q ' rx ' && echo 1 || echo 0) -o "$O/$id" "$O/$id.c" "$O"/rx.o "$O"/ra.o "$O"/s1.o "$O"/s2.o 2> "$O/$id.err" \
    && "$O/$id" > "$O/$id.out" 2>&1 && ok "$id" || bad "$id" "$(head -c 400 "$O/$id.err") $(cat "$O/$id.out" 2>/dev/null)"
done
printf '#define PCREC_RX_ABI_H 83\n#include "s1.h"\nint main(void){return 0;}\n' > "$O/abi_old.c"
if gcc $SAN -c -o /dev/null "$O/abi_old.c" 2> "$O/abi_old.err"; then bad abi.mismatch.error "compiled"; else grep -q '#error' "$O/abi_old.err" && grep -q 'abi' "$O/abi_old.err" && ok abi.mismatch.error || bad abi.mismatch.error "$(head -c 300 "$O/abi_old.err")"; fi
printf '#include "rx.h"\n#undef PCREC_RX_ABI_H\n#define PCREC_RX_ABI_H 85\n#include "s1.h"\nint main(void){return 0;}\n' > "$O/abi_new.c"
if gcc $SAN -c -o /dev/null "$O/abi_new.c" 2> "$O/abi_new.err"; then bad abi.mismatch.newer "compiled"; else ok abi.mismatch.newer; fi
for pairs in 1 2 3 4 64 256 100000; do
  id="pairs.$pairs"
  { echo "#define PCREC_SUBST_PAIRS $pairs"; echo '#include "rx.h"'; echo '#include "s1.h"'; cat "$D/inc_body.c"; } > "$O/$id.c"
  gcc $SAN -DHAVE_RX=1 -o "$O/$id" "$O/$id.c" "$O"/rx.o "$O"/ra.o "$O"/s1.o "$O"/s2.o 2> "$O/$id.err" && "$O/$id" > "$O/$id.out" 2>&1 \
    && ok "$id" || bad "$id" "$(head -c 400 "$O/$id.err") $(cat "$O/$id.out" 2>/dev/null)"
done
# §7¶5's custom-glue example, verbatim inside a function (prefix rx, subst dmy)
$T "$P" -p dmy -o "$O/dmy.c" --subst '[$1]' 2>/dev/null; gcc $SAN -c -o "$O/dmy.o" "$O/dmy.c"
cat > "$O/doc_example.c" <<'EOF'
#include "rx.h"
#include "dmy.h"
#include <stdio.h>
int main(void) {
    rx_subst_binding b; rx_subst_run runs[DMY_NREFS]; int bad;
    if (pcrec_subst_bind(&b, &rx_info, &dmy_subst_info, runs, DMY_NREFS, NULL, 0, &bad)) return 3;
    unsigned char out[64]; size_t cap = sizeof out;
    rx_iter it = RX_ITER_INIT((const unsigned char *)"zabza", 5);
    rx_ctx ctx; rx_var vres[1]; rx_subst_cur cur = { 0, 0, 1 };
    ptrdiff_t caps[RX_NCAPS][2];
    rx_subst_ctx_init(&ctx, &it, &b, vres);
    while (rx_next(&it, caps))
        if (dmy_subst_info.render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 1,
                                  RX_SUBST_GAPS, out, cap, &cur) < 0) break;
    rx_subst_put(&cur, out, cap, ctx.subject + cur.prev, ctx.len - cur.prev);
    return !(cur.w == 8 && !memcmp(out, "z[a]z[a]", 8));
}
EOF
gcc $SAN -o "$O/doc_example" "$O/doc_example.c" "$O/rx.o" "$O/dmy.o" 2> "$O/doc_example.err" && "$O/doc_example" && ok doc.example.7p5 || bad doc.example.7p5 "$(head -c 400 "$O/doc_example.err")"
# §6¶3's retry example, verbatim
cat > "$O/doc_retry.c" <<'EOF'
#include "rx.h"
#include "dmy.h"
#include <stdlib.h>
int main(void) {
    rx_subst_binding b; rx_subst_run runs[DMY_NREFS]; int bad;
    if (pcrec_subst_bind(&b, &rx_info, &dmy_subst_info, runs, DMY_NREFS, NULL, 0, &bad)) return 3;
    const unsigned char *s = (const unsigned char *)"zabza"; size_t n = 5;
    unsigned char out[2]; size_t cap = sizeof out;
    rx_iter it0 = RX_ITER_INIT(s, n), it = it0;     /* keep a FRESH copy */
    size_t len, k;
    int rc = pcrec_subst(&b, &it, SIZE_MAX, out, cap, &len, &k);
    unsigned char *big = NULL;
    if (rc == PCREC_SUBST_NOSPACE && len != SIZE_MAX) {
        big = malloc(len ? len : 1);
        it = it0;
        rc = pcrec_subst(&b, &it, SIZE_MAX, big, len, &len, &k);
    }
    int ok = rc == 0 && len == 8 && k == 2 && !memcmp(big, "z[a]z[a]", 8);
    free(big);
    return !ok;
}
EOF
gcc $SAN -o "$O/doc_retry" "$O/doc_retry.c" "$O/rx.o" "$O/dmy.o" 2> "$O/doc_retry.err" && "$O/doc_retry" && ok doc.example.6p3 || bad doc.example.6p3 "$(head -c 400 "$O/doc_retry.err")"
# §1¶1's sample declarations: the element signature in the .h matches the typedef
printf '#include "dmy.h"\nrx_substfn *f = dmy_render;\nint main(void){return f == 0;}\n' > "$O/sig.c"
gcc $SAN -Werror -o "$O/sig" "$O/sig.c" "$O/dmy.o" 2> "$O/sig.err" && ok element.signature || bad element.signature "$(head -c 300 "$O/sig.err")"
# strict compile of every emitted header/source under -Wall -Wextra -pedantic (C99 per §6¶6)
for std in c99 gnu99 c11 c17; do
  gcc -std=$std -Wall -Wextra -Werror -I "$O" -c -o /dev/null "$O/s1.c" 2> "$O/w.$std.err" && ok "warnings.subst.$std" || bad "warnings.subst.$std" "$(head -c 300 "$O/w.$std.err")"
done
g++ -x c++ -I "$O" -fsyntax-only "$O/s1.h" 2> "$O/cxx.err"; echo "INFO header.as.cxx exit $?: $(head -c 200 "$O/cxx.err")"
# §1¶3 under prefixes that differ only in case (both legal per cli.md §1.6¶1)
$T "$P" -p sq -o "$O/sq.c" --subst '<$0>' 2>/dev/null; $T "$P" -p sQ -o "$O/sQ.c" --subst '[$0]' 2>/dev/null
printf '#include "sq.h"\n#include "sQ.h"\nint main(void){ return sq_subst_info.abi != sQ_subst_info.abi; }\n' > "$O/case.c"
gcc $SAN -c -o /dev/null "$O/case.c" 2> "$O/case.err" && ok include.case.prefixes || bad include.case.prefixes "$(grep -m1 error "$O/case.err") (guard: $(sed -n 2p "$O/sq.h") vs $(sed -n 2p "$O/sQ.h"))"

# §1¶3 with an rx and a subst artifact under ONE prefix (one pattern, its template; no symbol clashes)
mkdir -p "$O/same"
$T "$P" --features all -p pair -o "$O/same/pair.c" --pattern '(a)' 2>/dev/null
$T "$P" -p pair -o "$O/same/pair_sub.c" --subst '[$1]' 2>/dev/null
printf '#include "pair.h"\n#include "pair_sub.h"\nint main(void){ rx_subst_binding b; rx_subst_run r[1]; int bad;\n return pcrec_subst_bind(&b, &pair_info, &pair_subst_info, r, 1, 0, 0, &bad); }\n' > "$O/same/main.c"
gcc $SAN -I "$O/same" -o "$O/same/main" "$O/same/main.c" "$O/same/pair.c" "$O/same/pair_sub.c" 2> "$O/same/err" && "$O/same/main" \
  && ok include.same.prefix.rx.and.subst || bad include.same.prefix.rx.and.subst "$(grep -m1 error "$O/same/err") (both headers guard on $(sed -n 2p "$O/same/pair.h" | cut -d' ' -f2))"
for pairs in 0; do
  id="pairs.$pairs"
  { echo "#define PCREC_SUBST_PAIRS $pairs"; echo '#include "rx.h"'; echo '#include "s1.h"'; cat "$D/inc_body.c"; } > "$O/$id.c"
  gcc $SAN -DHAVE_RX=1 -o "$O/$id" "$O/$id.c" "$O"/rx.o "$O"/ra.o "$O"/s1.o "$O"/s2.o 2> "$O/$id.err" && "$O/$id" > "$O/$id.out" 2>&1 \
    && ok "$id" || bad "$id" "$(head -c 400 "$O/$id.err") $(cat "$O/$id.out" 2>/dev/null)"
done

echo "TOTAL pass=$np fail=$nf"
