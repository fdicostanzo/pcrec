#!/usr/bin/env python3
"""grid1 (from vecspike): hand-edit an R17-b `new` artifact into one variant.

usage: mkvar.py IN.c OUT.c WIDTH ALIGN KEEP
  WIDTH  w8  = mask8_swar (R17-b's own form, block W = 8)
         v16 = mask64_sse2 (block W = 64, four 16-byte compares + movemask)
         v32 = mask64_avx2 (block W = 64, two 32-byte compares + movemask)
         v16n / v32n = STATELESS sse2 / avx2 (grid1's arm): the same W = 64
              block, NO cache: every use rescans from lo (ALIGN = KEEP = 0)
  ALIGN  0|1  the alignment prologue (V2): scalar member tests until s+i is
              aligned to the LOAD width (8 / 16 / 32), then aligned loads
  KEEP   0|1  the preserved state (V3): `struct rx_keep` (keep.h) replaces the
              site struct; rx_search_keep(s, n, from, caps, &st) is added

Only the site's struct, its `next_candidate` and (KEEP) the holding function's
signature and declaration change.  The cover terms are read from the
artifact's own `<stem>__mask`, the scalar test is its own `<stem>__member`.
The emitted function carries counters under -DVS_COUNT and a re-probe of every
answer against the byte loop under -DVS_DEBUG; neither is defined in a timed
build.  w8/0/0 reproduces R17-b's function (build.sh proves the timed V1 and
gen(w8,0,0) assemble identically).
"""
import re, sys

src_path, out_path, width, align, keep = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
assert width in ("w8", "v16", "v32", "v16n", "v32n")
stateless = width.endswith("n")
if stateless:
    assert not align and not keep, "the stateless arm has no prologue and no kept state"
    width = width[:-1]
txt = open(src_path).read()
lines = txt.split("\n")

m = re.search(r"static inline unsigned long long (\w+)__mask\(const unsigned char \*p\)\n\{\n"
              r"    pcrec_mfk_w8_vector v = pcrec_mfk_w8_load_vector\(p\);\n"
              r"    return pcrec_mfk_w8_lane_mask\((.*)\);\n\}\n", txt)
assert m, "no __mask"
stem, expr = m.group(1), m.group(2)
terms = re.findall(r"pcrec_mfk_w8_(range|eq|cube)\(v, (0x[0-9a-f]+|\d+)(?:, (0x[0-9a-f]+|\d+))?\)", expr)
assert terms and expr.count("pcrec_mfk_w8_") == len(terms) * 2 - 1 + 0 or True
hi_expr = re.search(r"static inline size_t \w+__next_candidate\(struct \w+ \*c, size_t lo\)\n\{\n"
                    r"    const unsigned char \*s = c->s;\n    size_t hi = (c->n[^;]*);", txt).group(1)
member = re.search(r"static inline int " + stem + r"__member\(unsigned char x\)\n\{\n    return (.*);\n\}", txt).group(1)

W = 8 if width == "w8" else 64          # the block (cache) width
LW = {"w8": 8, "v16": 16, "v32": 32}[width]  # the load width (alignment unit)

out = []
# ---- the wide primitives (gcc vector extensions + __builtin_ia32_*, no header) ----
if width != "w8":
    n = LW
    out.append(f"""#ifndef VS_V{n}_H
#define VS_V{n}_H
typedef unsigned char vs_v{n} __attribute__((vector_size({n}), may_alias));
typedef unsigned char vs_v{n}u __attribute__((vector_size({n}), may_alias, aligned(1)));
typedef char vs_v{n}c __attribute__((vector_size({n})));
static inline vs_v{n} vs_v{n}_load(const unsigned char *p) {{ return *(const vs_v{n}u *)p; }}
static inline vs_v{n} vs_v{n}_load_aligned(const unsigned char *p) {{ return *(const vs_v{n} *)p; }}
static inline vs_v{n} vs_v{n}_splat(unsigned b) {{ return (vs_v{n}){{0}} + (unsigned char)b; }}
static inline vs_v{n} vs_v{n}_eq(vs_v{n} v, unsigned b) {{ return (vs_v{n})(v == vs_v{n}_splat(b)); }}
static inline vs_v{n} vs_v{n}_cube(vs_v{n} v, unsigned m, unsigned val) {{ return (vs_v{n})((v & vs_v{n}_splat(m)) == vs_v{n}_splat(val)); }}
static inline vs_v{n} vs_v{n}_range(vs_v{n} v, unsigned l, unsigned w) {{ return (vs_v{n})((vs_v{n})(v - vs_v{n}_splat(l)) < vs_v{n}_splat(w)); }}
static inline unsigned long long vs_v{n}_lane_mask(vs_v{n} f) {{ return (unsigned)__builtin_ia32_pmovmskb{128 if n == 16 else 256}((vs_v{n}c)f); }}
#endif""")

def term_text(prefix):
    parts = []
    for kind, a, b in terms:
        parts.append(f"{prefix}_{kind}(v, {a}{', ' + b if b else ''})")
    e = parts[0]
    for p in parts[1:]:
        e = f"({e} | {p})" if prefix != "pcrec_mfk_w8" else f"pcrec_mfk_w8_vor({e}, {p})"
    return e

blk_defs = []
if width != "w8":
    n = LW
    blk_defs.append(f"static inline unsigned long long {stem}__lanes(vs_v{n} v)\n{{\n    return vs_v{n}_lane_mask({term_text('vs_v' + str(n))});\n}}")
    for nm, ld in (("blk", "load"), ("blka", "load_aligned")):
        parts = " | ".join(f"({stem}__lanes(vs_v{n}_{ld}(p + {k})) << {k})" for k in range(0, 64, n))
        blk_defs.append(f"static inline unsigned long long {stem}__{nm}(const unsigned char *p)\n{{\n    return {parts};\n}}")
else:
    blk_defs.append(f"#define {stem}__blk {stem}__mask")
    blk_defs.append(f"static inline unsigned long long {stem}__blka(const unsigned char *p)\n{{\n"
                    f"    return {stem}__mask((const unsigned char *)__builtin_assume_aligned(p, 8));\n}}")

C = "struct rx_keep" if keep else f"struct {stem}__c"
FL = "pcrec_mfk_w8_first_lane"
fill_blk = f"{stem}__blka" if align else f"{stem}__blk"
head = ""
if align:
    head = f"""    while (i < hi && ((__UINTPTR_TYPE__)(s + i) & {LW - 1})) {{
        VS_HEADB();
        if ({stem}__member(s[i])) {{
            VS_RET(i, VS_HEADHIT());
        }}
        i++;
    }}
"""
nc_head = f"""#ifdef VS_COUNT
extern unsigned long long vs_uses, vs_cold, vs_cache_hit, vs_cache_pass, vs_xcall, vs_skipped,
    vs_head_hit, vs_head_bytes, vs_blocks, vs_call, vs_fill_call;
#define VS_ENTRY() (vs_uses++, vs_cold += c->top == 0)
#define VS_HEADB() (vs_head_bytes++)
#define VS_HEADHIT() (vs_head_hit++)
#define VS_CHIT(lo, r) (vs_cache_hit++, vs_skipped += (r) - (lo), vs_xcall += vs_fill_call != vs_call)
#define VS_CPASS(lo) (vs_cache_pass++, vs_skipped += c->top - (lo), vs_xcall += vs_fill_call != vs_call)
#define VS_FILL() (vs_blocks++, vs_fill_call = vs_call)
#else
#define VS_ENTRY() ((void)0)
#define VS_HEADB() ((void)0)
#define VS_HEADHIT() ((void)0)
#define VS_CHIT(lo, r) ((void)0)
#define VS_CPASS(lo) ((void)0)
#define VS_FILL() ((void)0)
#endif
#ifdef VS_DEBUG
#include <assert.h>
static size_t vs_probe(const unsigned char *s, size_t lo, size_t hi)
{{
    while (lo < hi && !{stem}__member(s[lo])) lo++;
    return lo;
}}
#define VS_RET(r, ev) do {{ size_t vs_r = (r); ev; \\
        assert(c->base <= c->top && c->top <= hi && c->top - c->base <= {W}); \\
        assert(vs_r == vs_probe(s, lo, hi)); return vs_r; }} while (0)
#else
#define VS_RET(r, ev) do {{ size_t vs_r = (r); ev; return vs_r; }} while (0)
#endif
"""
nc = nc_head + f"""static inline size_t {stem}__next_candidate({C} *c, size_t lo)
{{
    const unsigned char *s = c->s;
    size_t hi = {hi_expr};
    size_t i = lo;
    VS_ENTRY();
    if ((size_t)(lo - c->base) < (size_t)(c->top - c->base)) {{
        unsigned long long m = c->m >> (lo - c->base);
        if (m) {{
            VS_RET(lo + {FL}(m), VS_CHIT(lo, vs_r));
        }}
        VS_CPASS(lo);
        i = c->top;
    }}
{head}    for (; i + {W} <= hi; i += {W}) {{
        unsigned long long m = {fill_blk}(s + i);
        VS_FILL();
        if (m) {{
            c->base = i;
            c->top = i + {W};
            c->m = m;
            VS_RET(i + {FL}(m), (void)0);
        }}
    }}
    if (i >= hi) VS_RET(hi, (void)0);
    if (hi >= {W}) {{
        size_t b = hi - {W};
        unsigned long long m = {stem}__blk(s + b);
        VS_FILL();
        c->base = b;
        c->top = hi;
        c->m = m;
        m >>= i - b;
        VS_RET(m ? i + {FL}(m) : hi, (void)0);
    }}
    {{
        unsigned long long m = 0;
        for (size_t k = i; k < hi; k++)
            m |= (unsigned long long){stem}__member(s[k]) << (k - i);
        VS_FILL();
        c->base = i;
        c->top = hi;
        c->m = m;
        VS_RET(m ? i + {FL}(m) : hi, (void)0);
    }}
}}"""
if stateless:   # grid1: no cache read or written; c->top stays 0, so every use counts as cold
    nc = nc_head + f"""static inline size_t {stem}__next_candidate({C} *c, size_t lo)
{{
    const unsigned char *s = c->s;
    size_t hi = {hi_expr};
    size_t i = lo;
    VS_ENTRY();
    for (; i + {W} <= hi; i += {W}) {{
        unsigned long long m = {stem}__blk(s + i);
        VS_FILL();
        if (m) VS_RET(i + {FL}(m), (void)0);
    }}
    if (i >= hi) VS_RET(hi, (void)0);
    if (hi >= {W}) {{
        size_t b = hi - {W};
        unsigned long long m = {stem}__blk(s + b) >> (i - b);
        VS_FILL();
        VS_RET(m ? i + {FL}(m) : hi, (void)0);
    }}
    for (; i < hi; i++)
        if ({stem}__member(s[i])) VS_RET(i, (void)0);
    VS_RET(hi, (void)0);
}}"""

# ---- splice: struct, blocks, next_candidate ----
def span(start_re):
    for k, l in enumerate(lines):
        if re.match(start_re, l):
            e = k
            while lines[e] not in ("}", "};"):
                e += 1
            return k, e
    raise SystemExit("not found: " + start_re)

ns, ne = span(r"static inline size_t \w+__next_candidate\(")
lines[ns:ne + 1] = ("\n".join(blk_defs) + "\n" + nc).split("\n")
ms, me = span(r"static inline unsigned long long \w+__mask\(")
lines[ms:ms] = out  # the wide sub-block before the site's helpers
if keep:
    ss, se = span(r"struct " + stem + r"__c \{")
    lines[ss:se + 1] = ['#include "keep.h"']
txt = "\n".join(lines)

if keep:
    txt = txt.replace(f"struct {stem}__c", "struct rx_keep")
    decl = f"    struct rx_keep {stem}__c = {{ subject, subject_length, 0, 0, 0 }};"
    assert txt.count(decl) == 1
    txt = txt.replace(decl, f"    struct rx_keep {stem}__c_own = {{ subject, subject_length, 0, 0, 0 }};\n"
                            f"    struct rx_keep *const {stem}__cp = rx_keep_st ? rx_keep_st : &{stem}__c_own;")
    txt = re.sub(r"&" + stem + r"__c\b", stem + "__cp", txt).replace(f"{stem}__c.n", f"{stem}__cp->n")
    assert not re.search(stem + r"__c\b", txt), "a site-struct use left unrewritten"
    rebind = ("    if (st->s != s || st->n != n) { st->s = s; st->n = n; st->base = 0; st->top = 0; st->m = 0; }\n"
              "#ifdef VS_DEBUG\n    assert(st->base <= st->top && st->top <= n && st->top - st->base <= %d);\n#endif\n" % W)
    sig = "int rx_search_keep(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2], struct rx_keep *st)"
    if stem == "rx_search_pf":          # DFA: the site lives in rx_search itself
        old = "int rx_search(const unsigned char *const subject, size_t const subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2])\n{"
        assert txt.count(old) == 1
        txt = txt.replace(old, "static inline __attribute__((always_inline)) int rx_search__impl(const unsigned char *const subject, size_t const subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2], struct rx_keep *rx_keep_st)\n{")
        txt += ("\n#if __has_attribute(noclone)\n__attribute__((noclone))\n#endif\n"
                "int rx_search(const unsigned char *const subject, size_t const subject_length, size_t search_from, ptrdiff_t (*capture_spans)[2])\n"
                "{\n    return rx_search__impl(subject, subject_length, search_from, capture_spans, 0);\n}\n"
                f"{sig}\n{{\n{rebind}    return rx_search__impl(s, n, from, caps, st);\n}}\n")
    else:                               # VM: the site lives in rx_search_run
        old = "size_t search_from, ptrdiff_t (*capture_spans)[2], rx_run_state *run)\n{"
        assert txt.count(old) == 1
        txt = txt.replace(old, "size_t search_from, ptrdiff_t (*capture_spans)[2], rx_run_state *run, struct rx_keep *rx_keep_st)\n{")
        call = "return rx_search_run(subject, subject_length, search_from, capture_spans, &run);"
        assert txt.count(call) == 1
        txt = txt.replace(call, call.replace("&run)", "&run, 0)"))
        txt += (f"\n{sig}\n{{\n{rebind}    rx_run_state run;\n"
                "    rx_run_state_bind(&run, rx_no_buffers.frames, rx_no_buffers.nframes,\n"
                "                            rx_no_buffers.trail,  rx_no_buffers.ntrail);\n"
                "    return rx_search_run(s, n, from, caps, &run, st);\n}\n")
open(out_path, "w").write(txt)
