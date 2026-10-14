#!/usr/bin/env python3
"""R-17 revision 2 (lane r17r5): the follow-up measurement's twins.
WRITTEN, NOT RUN (the box was held; every run is owed, setfind.md §13).

    python3 -I gen_twins_r2.py > twins_r2_gen.h

It renders everything gen_twins.py renders (the cells and their STATELESS
forms: table, memchr, mcK, swar, sse2, avx2), loaded BY PATH: under
`python3 -I` the script's directory is not on sys.path. It adds:

  * synthetic cells syn4/syn5/syn6/syn8 (k members pairwise at Hamming
    distance >= 2 and numeric distance >= 2, so no two members form a cube or
    a range: EXACTLY k terms, C2-4), and x80 (a range crossing 0x80, C1-10);
  * the STATEFUL forms of setfind.md §8, one per (cell, form), all sharing
    the state type `sstate` (setfind.md §4.3's struct, every form's fields in
    one type so the timer and the check treat them alike):
      mask8_swar    cache = one 8-byte word's exact mask (W = 8)
      mask64_swar   cache = a 64-byte block's exact mask (W = 64), SWAR
      mask64i_swar  the same, the refill NOT inlined (the composable-pieces
                    shape: pop in the body, refill a call; D155 add. 3)
      mask64_sse2   W = 64 from four 16-byte compares
      mask64_avx2   W = 64 from two 32-byte compares
      ring_swar     a ring of member offsets filled from RING bytes (SWAR)
      ring_avx2     the same filled by AVX2 masks
      adapt_swar    stateless swar <-> pcrec's table walk (setfind.md §9.1)
      adapt_avx2    stateless avx2 <-> the table walk
      adapt_mask    mask64_swar <-> the table walk
    Every stateful form answers F(lo) (setfind.md §8.2): the least i in
    [lo, hi) with s[i] in S, else hi; lo itself, and NO state write, when
    lo >= hi.

THE SPELLINGS are the design's: every SWAR word load is normalized by the
constant-folded ternary of setfind.md §6 (no #if in the find text); the
stateful forms use EXACT lane renderings only (§3.4); the mask is packed by
((z >> 7) * 0x0102040810204080) >> 56.

D149 labels (each also a -D override, so the run can sweep them):
  W = 8 / 64             DERIVED: the SWAR word / the 64-bit mask word
  RING = 256             UNMEASURED DEFAULT
  ADAPT_GAP = 8          UNMEASURED DEFAULT (one SWAR word)
  ADAPT_BLOCK0 = 16      UNMEASURED DEFAULT
  ADAPT_CAP = 1024       UNMEASURED DEFAULT

PLANT_STALE (a -D define, the check's planted control, S829/S841's twin):
the mask forms' cache test loses its lower bound, and the ring form loses its
hint reset; check_r2.c must then catch EVERY twin that has a cache.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("gen_twins", os.path.join(HERE, "gen_twins.py"))
gt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gt)


def _distinct_terms(members):
    for i, a in enumerate(members):
        for b in members[i + 1:]:
            if bin(a ^ b).count("1") < 2 or abs(a - b) < 2:
                raise SystemExit("synthetic cell members %02x/%02x merge into one term" % (a, b))


SYN = [0x21, 0x2A, 0x3C, 0x47, 0x5E, 0x6B, 0x70, 0x13]
SYN_CELLS = []
for k in (4, 5, 6, 8):
    m = sorted(SYN[:k])
    _distinct_terms(m)
    SYN_CELLS.append(("syn%d" % k, "synthetic: %d one-byte terms" % k, "synthetic",
                      m, [("eq", b) for b in m]))
SYN_CELLS.append(("x80", "synthetic: one range crossing 0x80", "synthetic",
                  list(range(0x78, 0x88)), [("range", 0x78, 0x87)]))

CELLS = list(gt.CELLS) + SYN_CELLS
FULL = "0xFFFFFFFFFFFFFFFFull"
H80 = "0x8080808080808080ull"
L7F = "0x7F7F7F7F7F7F7F7Full"


def swar_exact(t):
    """EXACT per-lane flag (bit 7 of each lane) for one term over `w`."""
    if t[0] == "eq":
        x = "(w ^ %s)" % gt.rep8(t[1])
    elif t[0] == "cube":
        x = "((w & %s) ^ %s)" % (gt.rep8(t[1]), gt.rep8(t[2]))
    else:
        return gt.swar_term(t)          # r17s's range spelling is exact per lane
    return "(~(((%s & %s) + %s) | %s) & %s)" % (x, L7F, L7F, x, H80)


def emit_stateful(cid, terms, o):
    ex = gt.or_all([swar_exact(t) for t in terms], lambda a, b: "(%s | %s)" % (a, b))
    o.append("/* ---- %s: the stateful forms ---- */\n" % cid)
    # the normalized word's exact flags, one word -> 8 mask bits, the tail
    o.append("static inline unsigned long long %s_xz(unsigned long long w) { return %s; }\n" % (cid, ex))
    o.append("static inline unsigned long long %s_w8(const unsigned char *p)\n"
             "{\n    unsigned long long w;\n    memcpy(&w, p, 8);\n    w = R17_LDN(w);\n"
             "    return R17_PACK(%s_xz(w));\n}\n" % (cid, cid))
    o.append("static inline unsigned long long %s_m64_swar(const unsigned char *p)\n"
             "{\n    unsigned long long r = 0;\n"
             "    for (int k = 0; k < 8; k++) r |= %s_w8(p + 8 * k) << (8 * k);\n"
             "    return r;\n}\n" % (cid, cid))
    o.append("static inline unsigned long long %s_mtail(const unsigned char *s, size_t i, size_t hi)\n"
             "{   /* exact mask of [i, hi), hi - i < 64 */\n"
             "    unsigned long long r = 0;\n    size_t j = 0;\n"
             "    while (i + j + 8 <= hi) { r |= %s_w8(s + i + j) << j; j += 8; }\n"
             "    while (i + j < hi) { if (%s_lane(s[i + j])) r |= 1ull << j; j++; }\n"
             "    return r;\n}\n" % (cid, cid, cid))
    # SIMD 64-byte masks
    t16 = gt.or_all([gt.simd_term(t, 16) for t in terms], lambda a, b: "_mm_or_si128(%s, %s)" % (a, b))
    t32 = gt.or_all([gt.simd_term(t, 32) for t in terms], lambda a, b: "_mm256_or_si256(%s, %s)" % (a, b))
    o.append("#ifdef __x86_64__\n"
             "static inline unsigned %s_vm16(__m128i v) { return (unsigned)_mm_movemask_epi8(%s); }\n"
             "static inline unsigned long long %s_m64_sse2(const unsigned char *p)\n"
             "{\n    return (unsigned long long)%s_vm16(_mm_loadu_si128((const __m128i *)p))\n"
             "         | (unsigned long long)%s_vm16(_mm_loadu_si128((const __m128i *)(p + 16))) << 16\n"
             "         | (unsigned long long)%s_vm16(_mm_loadu_si128((const __m128i *)(p + 32))) << 32\n"
             "         | (unsigned long long)%s_vm16(_mm_loadu_si128((const __m128i *)(p + 48))) << 48;\n}\n"
             "R17_AVX2 static inline unsigned %s_vm32(__m256i v) { return (unsigned)_mm256_movemask_epi8(%s); }\n"
             "R17_AVX2 static inline unsigned long long %s_m64_avx2(const unsigned char *p)\n"
             "{\n    return (unsigned long long)%s_vm32(_mm256_loadu_si256((const __m256i *)p))\n"
             "         | (unsigned long long)%s_vm32(_mm256_loadu_si256((const __m256i *)(p + 32))) << 32;\n}\n"
             "#endif\n" % (cid, t16, cid, cid, cid, cid, cid, cid, t32, cid, cid, cid))
    forms = []

    def mask_form(name, W, MW, attr="", simd=0, inline_refill=True):
        guard = simd != 0
        pre = "#ifdef __x86_64__\n" if guard else ""
        post = "#endif\n" if guard else ""
        refill = ("    while (i + %d <= hi) {\n"
                  "        unsigned long long m = %s(s + i);\n"
                  "        if (m) { c->base = i; c->top = i + %d; c->m = m;\n"
                  "                 return i + (size_t)__builtin_ctzll(m); }\n"
                  "        i += %d;\n    }\n"
                  "    if (i >= hi) return hi;\n"
                  "    if (hi >= %d) {\n"
                  "        size_t b = hi - %d;\n"
                  "        unsigned long long m = %s(s + b);\n"
                  "        c->base = b; c->top = hi; c->m = m;\n"
                  "        m >>= i - b;\n"
                  "        return m ? i + (size_t)__builtin_ctzll(m) : hi;\n    }\n"
                  "    {\n        unsigned long long m = %s_mtail(s, i, hi);\n"
                  "        c->base = i; c->top = hi; c->m = m;\n"
                  "        return m ? i + (size_t)__builtin_ctzll(m) : hi;\n    }\n"
                  % (W, MW, W, W, W, W, MW, cid))
        head = ("    size_t i = lo;\n"
                "    if (R17_INCACHE(c, lo)) {\n"
                "        unsigned long long m = c->m >> R17_SHIFT(c, lo);\n"
                "        if (m) return lo + (size_t)__builtin_ctzll(m);\n"
                "        i = c->top;\n    }\n")
        o.append(pre)
        if inline_refill:
            o.append("%sstatic inline size_t %s_%s_find(sstate *c, const unsigned char *s, size_t lo, size_t hi)\n"
                     "{\n%s%s}\n" % (attr, cid, name, head, refill))
        else:
            o.append("%sstatic NOINL size_t %s_%s_refill(sstate *c, const unsigned char *s, size_t i, size_t hi)\n"
                     "{\n%s}\n" % (attr, cid, name, refill))
            o.append("%sstatic inline size_t %s_%s_find(sstate *c, const unsigned char *s, size_t lo, size_t hi)\n"
                     "{\n%s    return %s_%s_refill(c, s, i, hi);\n}\n" % (attr, cid, name, head, cid, name))
        o.append("%sNOINL size_t %s_%s(sstate *c, const unsigned char *s, size_t lo, size_t hi)\n"
                 "{ if (lo >= hi) return lo; return %s_%s_find(c, s, lo, hi); }\n" % (attr, cid, name, cid, name))
        o.append(post)
        forms.append((name, simd))

    def ring_form(name, MW, attr="", simd=0):
        guard = simd != 0
        o.append("#ifdef __x86_64__\n" if guard else "")
        o.append("%sNOINL size_t %s_%s(sstate *c, const unsigned char *s, size_t lo, size_t hi)\n"
                 "{\n    if (lo >= hi) return lo;\n    size_t i = lo;\n"
                 "    if (R17_INCACHE(c, lo)) {\n"
                 "        unsigned off = (unsigned)(lo - c->base), k = c->rh;\n"
                 "        R17_RING_RESET(c, k, off);\n"
                 "        while (k < c->rt && c->pos[k] < off) k++;\n"
                 "        c->rh = k;\n"
                 "        if (k < c->rt) return c->base + c->pos[k];\n"
                 "        i = c->top;\n    }\n"
                 "    while (i < hi) {\n"
                 "        size_t end = hi - i >= RING ? i + RING : hi, j = i;\n"
                 "        unsigned n = 0;\n"
                 "        while (j + 64 <= end) {\n"
                 "            unsigned long long m = %s(s + j);\n"
                 "            while (m) { c->pos[n++] = (unsigned short)(j - i + (size_t)__builtin_ctzll(m)); m &= m - 1; }\n"
                 "            j += 64;\n        }\n"
                 "        if (j < end) {\n"
                 "            unsigned long long m = %s_mtail(s, j, end);\n"
                 "            while (m) { c->pos[n++] = (unsigned short)(j - i + (size_t)__builtin_ctzll(m)); m &= m - 1; }\n"
                 "        }\n"
                 "        c->base = i; c->top = end; c->rt = n; c->rh = 0;\n"
                 "        if (n) return i + c->pos[0];\n"
                 "        i = end;\n    }\n"
                 "    return hi;\n}\n" % (attr, cid, name, MW, cid))
        o.append("#endif\n" if guard else "")
        forms.append((name, simd))

    def adapt_form(name, fast, attr="", simd=0):
        guard = simd != 0
        o.append("#ifdef __x86_64__\n" if guard else "")
        o.append("%sNOINL size_t %s_%s(sstate *c, const unsigned char *s, size_t lo, size_t hi)\n"
                 "{\n    if (lo >= hi) return lo;\n"
                 "    if (c->steps) {                       /* walk mode: pcrec's table */\n"
                 "        c->steps--;\n"
                 "        while (lo < hi && !%s_T[s[lo]]) lo++;\n"
                 "        return lo;\n    }\n"
                 "    size_t a = %s;\n"
                 "    if (a - lo >= ADAPT_GAP)  c->block = 0;\n"
                 "    else if (!c->block)       c->block = ADAPT_BLOCK0;\n"
                 "    else { c->steps = c->block; if (c->block < ADAPT_CAP) c->block *= 2; }\n"
                 "    return a;\n}\n" % (attr, cid, name, cid, fast))
        o.append("#endif\n" if guard else "")
        forms.append((name, simd))

    mask_form("mask8_swar", 8, "%s_w8" % cid)
    mask_form("mask64_swar", 64, "%s_m64_swar" % cid)
    mask_form("mask64i_swar", 64, "%s_m64_swar" % cid, inline_refill=False)
    mask_form("mask64_sse2", 64, "%s_m64_sse2" % cid, simd=1)
    mask_form("mask64_avx2", 64, "%s_m64_avx2" % cid, attr="R17_AVX2 ", simd=2)
    ring_form("ring_swar", "%s_m64_swar" % cid)
    ring_form("ring_avx2", "%s_m64_avx2" % cid, attr="R17_AVX2 ", simd=2)
    adapt_form("adapt_swar", "%s_swar_from(s, lo, hi)" % cid)
    adapt_form("adapt_avx2", "%s_avx2_from(s, lo, hi, lo)" % cid, attr="R17_AVX2 ", simd=2)
    adapt_form("adapt_mask", "%s_mask64_swar_find(c, s, lo, hi)" % cid)
    return forms


PRELUDE = r"""/* GENERATED by gen_twins_r2.py (lane r17r5, R-17 rev 2). Do not edit. */
#ifndef NOINL
#define NOINL __attribute__((noinline))
#endif
#define R17_AVX2 __attribute__((target("avx2")))
#ifndef RING
#define RING 256            /* UNMEASURED DEFAULT */
#endif
#ifndef ADAPT_GAP
#define ADAPT_GAP 8         /* UNMEASURED DEFAULT */
#endif
#ifndef ADAPT_BLOCK0
#define ADAPT_BLOCK0 16     /* UNMEASURED DEFAULT */
#endif
#ifndef ADAPT_CAP
#define ADAPT_CAP 1024      /* UNMEASURED DEFAULT */
#endif
_Static_assert(__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__ ||
               __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__, "r17r2: unsupported byte order");
/* setfind.md §6: the ONE endianness spelling, at the load */
#define R17_LDN(w) (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__ ? __builtin_bswap64(w) : (w))
/* lane i's exact flag (bit 8i+7) to mask bit i */
#define R17_PACK(z) ((((z) >> 7) * 0x0102040810204080ull) >> 56)
/* the per-site state (setfind.md §4.3), every form's fields in one type */
typedef struct {
    size_t base, top;               /* the cached block [base, top)       */
    unsigned long long m;           /* mask forms: exact membership bits  */
    unsigned steps, block;          /* adaptive forms: the mode counters  */
    unsigned rh, rt;                /* ring forms: hint, count            */
    unsigned short pos[RING];       /* ring forms: member offsets         */
} sstate;
/* the scalar fields only: an aggregate initializer would zero pos[] too
 * (512 bytes per call; setfind.md §7.3) */
static inline void sreset(sstate *c)
{
    c->base = c->top = 0; c->m = 0; c->steps = c->block = 0; c->rh = c->rt = 0;
}
#ifndef PLANT_STALE
/* base <= lo < top, one unsigned compare (setfind.md §8.2 step 1) */
#define R17_INCACHE(c, lo) ((size_t)((lo) - (c)->base) < (size_t)((c)->top - (c)->base))
#define R17_SHIFT(c, lo)   ((lo) - (c)->base)
#define R17_RING_RESET(c, k, off) do { if ((k) > 0 && (c)->pos[(k) - 1] >= (off)) (k) = 0; } while (0)
#else
/* the planted defects: no lower bound (S829's twin); no hint reset (S841's) */
#define R17_INCACHE(c, lo) ((lo) < (c)->top)
#define R17_SHIFT(c, lo)   ((lo) >= (c)->base ? (lo) - (c)->base : 0)
#define R17_RING_RESET(c, k, off) do { (void)(off); } while (0)
#endif
"""


def main():
    o = [PRELUDE]
    table = []
    for c in CELLS:
        cid, bench, site, S, terms = c
        sless = gt.emit_cell(cid, bench, site, S, terms, o)
        sful = emit_stateful(cid, terms, o)
        table.append((cid, bench, sless, sful))
    o.append("typedef size_t (*find_fn)(const unsigned char *, size_t, size_t);\n"
             "typedef size_t (*sfind_fn)(sstate *, const unsigned char *, size_t, size_t);\n"
             "typedef struct { const char *cell, *form, *bench; find_fn f; sfind_fn sf;\n"
             "                 int simd; int cache; const unsigned char *T; int bounded; } twin2;\n"
             "static const twin2 TW2[] = {\n")
    for cid, bench, sless, sful in table:
        bounded = 1 if cid == "u8l" else 0
        for f in sless:
            simd = 2 if f == "avx2" else 1 if f == "sse2" else 0
            line = ("    { \"%s\", \"%s\", \"%s\", %s_%s, 0, %d, 0, %s_T, %d },\n"
                    % (cid, f, bench, cid, f, simd, cid, bounded))
            o.append(("#ifdef __x86_64__\n" + line + "#endif\n") if simd else line)
        for f, simd in sful:
            cache = 0 if f in ("adapt_swar", "adapt_avx2") else 1
            line = ("    { \"%s\", \"%s\", \"%s\", 0, %s_%s, %d, %d, %s_T, %d },\n"
                    % (cid, f, bench, cid, f, simd, cache, cid, bounded))
            o.append(("#ifdef __x86_64__\n" + line + "#endif\n") if simd else line)
    o.append("};\n#define NTW2 (sizeof TW2 / sizeof TW2[0])\n")
    sys.stdout.write("".join(o))


if __name__ == "__main__":
    main()
