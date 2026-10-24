#!/bin/bash
# substd27 CLI + header-composition cases (subst_api.md §1, §5, §6, §10).
# usage: cli/cli.sh [PCREC]     prints PASS/FAIL per case and a total
# substb2: the R4 interface -- `--unset=` is gone (an unknown option: unset is
# the run-time RX_SUBST_STRICT, §4¶23), the support unit is `--emit-support`
# (§10), the drivers are the §6 recipes (the setup, the per-match loop, the
# flatten), and the R3 stamps (`_SUBST_UNSET`, `_NSEGS`) and `PCREC_SUBST_PAIRS`
# are retired with the promises behind them.
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
# substb2: --unset= is no option at all now (§4¶23, §5¶1: unset is a flag of the call): every spelling is refused
expect_rc unset.without.subst nz $T "$P" -o "$O/x.c" --unset=error --pattern 'a'
expect_rc unset.bogus         nz $T "$P" -o "$O/x.c" --unset=bogus --subst '$1'
expect_rc unset.empty.value   nz $T "$P" -o "$O/x.c" --unset= --subst '$1'
expect_rc unset.EMPTY.case    nz $T "$P" -o "$O/x.c" --unset=EMPTY --subst '$1'
expect_rc unset.error.with.subst nz $T "$P" -o "$O/x.c" --unset=error --subst '$1'
expect_rc unset.empty.with.subst nz $T "$P" -o "$O/x.c" --unset=empty --subst '$1'
$T "$P" -o "$O/x.c" --unset=error --subst '$1' > /dev/null 2> "$O/unset.msg"
grep -q "unknown option" "$O/unset.msg" && ok unset.unknown.option || bad unset.unknown.option "$(head -c 200 "$O/unset.msg")"
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
# compile flags that mean nothing to a template (§5¶1: every other option is REFUSED, never ignored; -e is the template's encoding)
expect_rc flag.e.utf8 0 $T "$P" -e utf8 -p fx -o "$O/fx.c" --subst '$1'
for fl in "-i" "--no-captures" "--engine=vm" "--emit-main" "--features all" "--trace"; do
  id="flag.$(echo "$fl" | tr -c 'a-z0-9\n' '_')"
  expect_rc "$id" nz $T "$P" $fl -p fx -o "$O/fx.c" --subst '$1'
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
grep -q '^#define DMY_SUBST_MODULES "subst"' "$O/dmy.c" && ok stamp.modules.subst || bad stamp.modules.subst "$(grep MODULES "$O/dmy.c")"
grep -q 'DMY_SUBST_MODULES' "$O/dmy.h" && bad stamp.c.only "the .h carries a .c-only stamp" || ok stamp.c.only
# §1¶1, §5¶2: NREFS = max(1, references) (here $1 and ${name}: 2), PIECES = gap + [ + $1 + | + name + |$] (6), MAXNUM, NVREFS = max(1, 0)
grep -q '^#define DMY_NREFS  *2' "$O/dmy.h" && grep -q '^#define DMY_PIECES  *6' "$O/dmy.h" && grep -q '^#define DMY_MAXNUM  *1' "$O/dmy.h" \
  && grep -q '^#define DMY_NVREFS  *1' "$O/dmy.h" && ok stamp.h.constants || bad stamp.h.constants "$(grep -E 'DMY_(NREFS|PIECES|MAXNUM|NVREFS)' "$O/dmy.h")"
grep -q 'DMY_NSEGS\|SUBST_UNSET "' "$O/dmy.h" "$O/dmy.c" && bad stamp.r3.retired "an R3 stamp (_NSEGS, _SUBST_UNSET) is still emitted" || ok stamp.r3.retired
$T "$P" -p dme -o "$O/dme.c" --subst '${!v}$1' 2>/dev/null
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
/* §1¶5: a template without case forcing needs nothing but the two files: the setup and the per-match recipe (§6¶2) */
int main(void) {
    rx_iter it = RX_ITER_INIT((const unsigned char *)"xab", 3);
    rx_var vres[1]; rx_ctx ctx; int bad;
    if (rx_subst_ctx_init(&ctx, &it, &sr_info, &sc_subst_info, NULL, vres, 0, &bad) < 0) return 2;
    ptrdiff_t caps[SR_NCAPS][2]; rx_subst_piece pc[SC_PIECES]; rx_subst_out o = { .pc = pc, .cap = SC_PIECES };
    unsigned char out[64]; size_t w = 0;
    while (sr_next(&it, caps)) {
        o.n = 0;
        if (sc_render(&ctx, NULL, caps, 1, RX_SUBST_GAPS, &o) < 0) return 3;
        for (size_t i = 0; i < o.n; i++) { memcpy(out + w, pc[i].p, pc[i].len); w += pc[i].len; }
    }
    memcpy(out + w, ctx.subject + o.prev, ctx.len - o.prev); w += ctx.len - o.prev;
    return !(w == 4 && !memcmp(out, "x<a>", 4));
}
EOF
gcc -std=gnu11 -fsanitize=address,undefined -o "$O/sc_main" "$O/sc_main.c" 2> "$O/sc_main.err" && "$O/sc_main" && ok selfcontained.two.in.one.tu || bad selfcontained.two.in.one.tu "$(head -c 400 "$O/sc_main.err")"

# ---- §1¶3 include order and multiplicity; §1¶4 abi #error; §6¶2 and §6¶8 examples (substb2: PCREC_SUBST_PAIRS is retired)
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
# substland2: RX_FOREACH_PAIRS was dropped with RX_FOREACH (D175), so the three foreachpairs.* cases became batchpairs.*.
# RX_SUBST_BATCH_PAIRS, the support unit's one overridable bound (§10¶6a), set by the defining TU: replace-all answers what the
# per-match loop answers (rx is (a)(b)?, 3 pairs a match); a bound below one match's pairs is MISMATCH (§10¶7)
$T "$P" --emit-support -o "$O/support_bp.h" 2>/dev/null
cat > "$O/batch_body.c" <<'EOF'
#include "rx.h"
#include "s1.h"
#define PCREC_SUPPORT_IMPLEMENTATION
#include "support_bp.h"
#include <stdio.h>
int main(void)
{
    static unsigned char s[3000], out[6000];
    for (int i = 0; i < 3000; i++) s[i] = "abxya"[i % 5];
    rx_iter it = RX_ITER_INIT(s, sizeof s);
    rx_var vres[1];
    rx_ctx ctx;
    ptrdiff_t caps[RX_NCAPS][2];
    rx_subst_piece pc[64 * S1_PIECES];
    rx_subst_out o = { .pc = pc, .cap = 64 * S1_PIECES };
    size_t k = 0, w = 0, len;
    int bad, rc = rx_subst_ctx_init(&ctx, &it, &rx_info, &s1_subst_info, NULL, vres, 0, &bad);
    if (rc < 0) { printf("setup %d\n", rc); return 2; }
    while (rx_next(&it, caps)) {
        o.n = 0; o.sn = 0;
        if ((rc = s1_render(&ctx, NULL, caps, 1, RX_SUBST_GAPS, &o)) < 0) { printf("rc %d\n", rc); return 3; }
        for (size_t i = 0; i < o.n; i++) w += pc[i].len;
        k++;
    }
    if (it.rc < 0) return 5;
    w += sizeof s - o.prev;                                   /* the tail */
    it = RX_ITER_INIT(s, sizeof s);
    rx_subst_ctx_init(&ctx, &it, &rx_info, &s1_subst_info, NULL, vres, 0, &bad);
    rc = rx_subst_replace_all(rx_next_n, &it, &s1_subst_info, &ctx, NULL, 0, &o, out, sizeof out, &len);
    if (RX_SUBST_BATCH_PAIRS < RX_NCAPS) return rc != PCREC_SUBST_MISMATCH ? (printf("rc %d, want MISMATCH\n", rc), 6) : 0;
    if (rc < 0 || (size_t)rc != k || len != w) { printf("rc %d len %zu vs %zu %zu\n", rc, len, k, w); return 4; }
    return 0;
}
EOF
for pairs in 2 3 1024; do
  id="batchpairs.$pairs"
  { echo "#define RX_SUBST_BATCH_PAIRS $pairs"; cat "$O/batch_body.c"; } > "$O/$id.c"
  gcc $SAN -o "$O/$id" "$O/$id.c" "$O"/rx.o "$O"/s1.o 2> "$O/$id.err" && "$O/$id" > "$O/$id.out" 2>&1 \
    && ok "$id" || bad "$id" "$(head -c 400 "$O/$id.err") $(cat "$O/$id.out" 2>/dev/null)"
done
# §6¶2's per-match recipe (prefix rx, subst dmy), the stream replaced by a buffer
$T "$P" -p dmy -o "$O/dmy.c" --subst '[$1]' 2>/dev/null; gcc $SAN -c -o "$O/dmy.o" "$O/dmy.c"
cat > "$O/doc_example.c" <<'EOF'
#include "rx.h"
#include "dmy.h"
#include <stdio.h>
int main(void) {
    const unsigned char *s = (const unsigned char *)"zabza"; size_t n = 5;
    unsigned char out[64]; size_t w = 0;
    rx_iter it = RX_ITER_INIT(s, n);
    const rx_subst_map *map = NULL;
    unsigned flags = 0;
    rx_var vres[DMY_NVREFS];
    rx_ctx ctx;
    int bad, rc = rx_subst_ctx_init(&ctx, &it, &rx_info, &dmy_subst_info, map, vres, flags, &bad);
    if (rc < 0) return 3;
    ptrdiff_t caps[RX_NCAPS][2];
    rx_subst_piece pc[DMY_PIECES];
    rx_subst_out o = { .pc = pc, .cap = DMY_PIECES };
    while (rx_next(&it, caps)) {
        o.n = 0; o.sn = 0;
        rc = dmy_render(&ctx, map, caps, 1, flags | RX_SUBST_GAPS, &o);
        if (rc < 0) return 4;
        for (size_t i = 0; i < o.n; i++) { memcpy(out + w, pc[i].p, pc[i].len); w += pc[i].len; }
    }
    if (it.rc < 0) return 5;
    if (n > o.prev) { memcpy(out + w, s + o.prev, n - o.prev); w += n - o.prev; }
    return !(w == 8 && !memcmp(out, "z[a]z[a]", 8));
}
EOF
gcc $SAN -o "$O/doc_example" "$O/doc_example.c" "$O/rx.o" "$O/dmy.o" 2> "$O/doc_example.err" && "$O/doc_example" && ok doc.example.6p2 || bad doc.example.6p2 "$(head -c 400 "$O/doc_example.err")"
# §6¶8/§6¶9: the support unit emitted by the CLI, the setup wrapper and the replace-all call, the NOSPACE retry on a FRESH iterator
$T "$P" --emit-support -o "$O/support.h" 2> "$O/support.err" && ok support.emit || bad support.emit "$(head -c 300 "$O/support.err")"
cat > "$O/doc_all.c" <<'EOF'
#include "rx.h"
#include "dmy.h"
#define PCREC_SUPPORT_IMPLEMENTATION
#include "support.h"
#include <stdlib.h>
static int sub_all(const struct rx_info *rx, const struct rx_subst_info *t,
                   const rx_subst_map *map, unsigned flags,
                   const unsigned char *s, size_t n,
                   unsigned char *out, size_t cap, size_t *len)
{
    rx_iter it = RX_ITER_INIT(s, n);
    rx_var vres[t->nvrefs > 0 ? t->nvrefs : 1];
    rx_subst_piece pc[64 * (size_t)t->npieces];
    rx_subst_out o = { .pc = pc, .cap = 64 * (size_t)t->npieces };
    rx_ctx ctx;
    int bad, rc = rx_subst_ctx_init(&ctx, &it, rx, t, map, vres, flags, &bad);
    if (rc < 0) return rc;
    return rx_subst_replace_all(rx->next_n, &it, t, &ctx, map, flags, &o, out, cap, len);
}
int main(void) {
    const unsigned char *s = (const unsigned char *)"zabza"; size_t n = 5;
    unsigned char out[2]; size_t cap = sizeof out, len;
    int rc = sub_all(&rx_info, &dmy_subst_info, NULL, 0, s, n, out, cap, &len);
    unsigned char *big = NULL;
    if (rc == PCREC_SUBST_NOSPACE && len != SIZE_MAX) {      /* buf was too small: len bytes suffice; a FRESH iterator */
        big = malloc(len ? len : 1);
        rc = sub_all(&rx_info, &dmy_subst_info, NULL, 0, s, n, big, len, &len);
    }
    size_t sz;
    int rs = sub_all(&rx_info, &dmy_subst_info, NULL, 0, s, n, NULL, 0, &sz);   /* sizes only (§6¶9a) */
    int ok = rc == 2 && len == 8 && !memcmp(big, "z[a]z[a]", 8) && rs == 2 && sz == 8;
    free(big);
    return !ok;
}
EOF
gcc $SAN -o "$O/doc_all" "$O/doc_all.c" "$O/rx.o" "$O/dmy.o" 2> "$O/doc_all.err" && "$O/doc_all" && ok doc.example.6p8 || bad doc.example.6p8 "$(head -c 400 "$O/doc_all.err")"
# §10¶2: the support unit is deterministic, to stdout or to a file; it refuses every other argument; PCREC_SUPPORT_STATIC
$T "$P" --emit-support -o "$O/support2.h" 2>/dev/null; cmp -s "$O/support.h" "$O/support2.h" && ok support.deterministic || bad support.deterministic "two runs differ"
$T "$P" --emit-support > "$O/support3.h" 2>/dev/null; cmp -s "$O/support.h" "$O/support3.h" && ok support.stdout || bad support.stdout "stdout differs from -o"
expect_rc support.refuses.pattern nz $T "$P" --emit-support --pattern a -o "$O/x.h"
expect_rc support.refuses.subst nz $T "$P" --emit-support --subst '$1' -o "$O/x.h"
expect_rc support.refuses.prefix nz $T "$P" --emit-support -p x -o "$O/x.h"
grep -q 'defined(PCREC_SUPPORT_IMPLEMENTATION)' "$O/support.h" && ok support.guarded.impl || bad support.guarded.impl "definitions not under PCREC_SUPPORT_IMPLEMENTATION"
# a program with no implementation in any TU does not link (the names carry the abi, §10¶3); with it in one TU it does (doc_all above)
printf '#include "rx.h"\n#include "dmy.h"\n#include "support.h"\nint main(void){ unsigned char o[1]; rx_subst_piece p = { o, 0 }; return (int)rx_subst_flatten(&p, 1, o, 1); }\n' > "$O/nolink.c"
gcc $SAN -o "$O/nolink" "$O/nolink.c" "$O/rx.o" "$O/dmy.o" 2> "$O/nolink.err" && bad support.needs.impl "linked without the implementation" || { grep -q "rx_subst_flatten_v" "$O/nolink.err" && ok support.needs.impl || bad support.needs.impl "$(head -c 300 "$O/nolink.err")"; }
printf '#define PCREC_SUPPORT_STATIC\n#include "support.h"\n#include "rx.h"\n#include "dmy.h"\nint main(void){ unsigned char o[4]; rx_subst_piece p = { (const unsigned char *)"ab", 2 }; return !(rx_subst_flatten(&p, 1, o, 4) == 2 && !memcmp(o, "ab", 2)); }\n' > "$O/static.c"
gcc $SAN -o "$O/static" "$O/static.c" "$O/rx.o" "$O/dmy.o" 2> "$O/static.err" && "$O/static" && ok support.static || bad support.static "$(head -c 400 "$O/static.err")"
# §1¶1's sample declarations: the element signature in the .h matches the typedef
printf '#include "dmy.h"\nrx_substfn *f = dmy_render;\nint main(void){return f == 0;}\n' > "$O/sig.c"
gcc $SAN -Werror -o "$O/sig" "$O/sig.c" "$O/dmy.o" 2> "$O/sig.err" && ok element.signature || bad element.signature "$(head -c 300 "$O/sig.err")"
# strict compile of every emitted header/source under -Wall -Wextra -pedantic (C99 per §6¶6)
for std in c99 gnu99 c11 c17; do
  gcc -std=$std -Wall -Wextra -Werror -I "$O" -c -o /dev/null "$O/s1.c" 2> "$O/w.$std.err" && ok "warnings.subst.$std" || bad "warnings.subst.$std" "$(head -c 300 "$O/w.$std.err")"
done
g++ -x c++ -I "$O" -fsyntax-only "$O/s1.h" 2> "$O/cxx.err"; echo "INFO header.as.cxx exit $?: $(head -c 200 "$O/cxx.err")"
# §1¶3 under prefixes that differ only in case (both legal per cli.md §1.6¶1).
# substb2, ruling R14 (docs/dev/lanes/subst_rulings.md): the R4c #error for two
# subst headers whose prefixes differ only in case is a CLEAN REFUSAL, not a
# miscompile (subst_api.md §1¶3); the case now expects that refusal.
$T "$P" -p sq -o "$O/sq.c" --subst '<$0>' 2>/dev/null; $T "$P" -p sQ -o "$O/sQ.c" --subst '[$0]' 2>/dev/null
printf '#include "sq.h"\n#include "sQ.h"\nint main(void){ return sq_subst_info.abi != sQ_subst_info.abi; }\n' > "$O/case.c"
if gcc $SAN -c -o /dev/null "$O/case.c" 2> "$O/case.err"; then bad include.case.prefixes "sq.h and sQ.h shared a translation unit (want the §1¶3 #error)"
elif grep -q 'differ only in case' "$O/case.err"; then ok include.case.prefixes
else bad include.case.prefixes "$(grep -m1 error "$O/case.err") (want the §1¶3 #error)"; fi

# §1¶3 with an rx and a subst artifact under ONE prefix (one pattern, its template; no symbol clashes)
mkdir -p "$O/same"
$T "$P" --features all -p pair -o "$O/same/pair.c" --pattern '(a)' 2>/dev/null
$T "$P" -p pair -o "$O/same/pair_sub.c" --subst '[$1]' 2>/dev/null
printf '#include "pair.h"\n#include "pair_sub.h"\nint main(void){ int bad;\n return pcrec_subst_check(&pair_subst_info, 0, &pair_info, 0, &bad); }\n' > "$O/same/main.c"
gcc $SAN -I "$O/same" -o "$O/same/main" "$O/same/main.c" "$O/same/pair.c" "$O/same/pair_sub.c" 2> "$O/same/err" && "$O/same/main" \
  && ok include.same.prefix.rx.and.subst || bad include.same.prefix.rx.and.subst "$(grep -m1 error "$O/same/err") (both headers guard on $(sed -n 2p "$O/same/pair.h" | cut -d' ' -f2))"
echo "TOTAL pass=$np fail=$nf"
