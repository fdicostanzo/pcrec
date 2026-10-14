#!/usr/bin/env python3
"""R-17 (lane r17s): render the hand twins as C text, one specialized
function per (cell, form), the way a kit row would render a site: every
constant literal, no descriptor read at run time.

    gen_twins.py > twins_gen.h

THE KERNEL CONTRACT (every form, every cell) is the PF FIND statement's,
`pffind.c`'s `pf_walk` read as a function:

    size_t f(const unsigned char *s, size_t lo, size_t hi)
        returns the least i in [lo, hi) with s[i] in S; else hi; and lo
        itself when lo >= hi (the walk's loop test fails first: NOP).

`hi` is `n - end_back`, so the bounded site (end_back 1) is the same kernel
at hi = n - 1. No form reads s[i] for i outside [lo, hi): every load is
in range, so there is no over-read to argue (the guard-page check proves it).

THE FORMS (which apply to a cell is the cell's set shape, below):
  table     today's emitted walk over the 256-byte membership table.
  memchr    |S| = 1: one libc memchr (pf_memchr's call).
  mcK       |S| = 2..3: a BOUNDED memchr cascade: h = memchr(m1, [lo, hi)),
            then each next member searched only over [lo, h). Exact (the
            least hit of any member), no state across calls, each byte read
            at most K times; K calls per find.
  swar      8 bytes per step on ordinary uint64 (scalar layer, Q50): an OR of
            the cell's TERMS, then a byte tail. A term is
              eq(A)        haszero(w ^ A*0x01..)
              cube(M, V)   haszero((w & M*0x01..) ^ V*0x01..)
              range(L, H)  exact per-lane (d = w -lane L; d < H-L+1)
            haszero ((t - 0x01..) & ~t & 0x80..) flags false lanes only ABOVE
            a true one, so the lowest flag of the OR is the least hit; the
            range term is exact per lane. Unaligned 8-byte loads by memcpy.
  sse2/avx2 the vrun.c-style w16/w32 compare: eq = cmpeq; cube = cmpeq(and);
            range = cmpeq(min_epu8(v - L, H - L), v - L); OR, movemask, ctz.
            Blocks ascend while i + W <= hi; then ONE overlapped final block
            ending at hi (lanes below i masked off) when hi - lo >= W; else
            the next narrower level (avx2 -> sse2 -> the swar byte tail).
            SIMD layer (MF_P_PORTABLE_ONLY off); x86 only.
D149: no constant here is tuned. W = 8/16/32 is the word or register width
(derived); the overlapped final block and the scalar tail are the only
cut-overs and both are forced by "never read outside [lo, hi)".
"""

CELLS = [
    # id, bench cell(s), site, set (sorted), swar/simd terms, extra forms
    ("adl", "utf8/alt-distinct-lead", "dfa-pf byte-class",
     [0x63, 0xD0, 0xE6], [("eq", 0x63), ("eq", 0xD0), ("eq", 0xE6)]),
    ("qdm", "capability/quoted-delim-match", "vm-hat start_set",
     [0x22, 0x27], [("eq", 0x22), ("eq", 0x27)]),
    ("alt2", "syntax/alt-two, syntax/alt-nested", "dfa-pf byte-class",
     [0x63, 0x64], [("eq", 0x63), ("eq", 0x64)]),
    ("alt2r", "syntax/alt-two (range spelling)", "dfa-pf byte-class",
     [0x63, 0x64], [("range", 0x63, 0x64)]),
    ("bkn", "syntax/bak-k-named", "vm-hat start_set",
     [0x3C], [("eq", 0x3C)]),
    ("bpr", "capability/balanced-parens-rec", "vm-hat start_set",
     [0x28], [("eq", 0x28)]),
    ("sig", "utf8/ci-sigma", "dfa-pf byte-class",
     [0xCE, 0xCF], [("cube", 0xFE, 0xCE)]),
    ("tki", "utf8/ci-turkish-i", "dfa-pf byte-class",
     [0x49, 0x69], [("cube", 0xDF, 0x49)]),
    ("kel", "utf8/ci-kelvin", "dfa-pf byte-class",
     [0x4B, 0x6B, 0xE2], [("cube", 0xDF, 0x4B), ("eq", 0xE2)]),
    ("hbr", "capability/high-byte-run", "dfa-pf byte-class",
     list(range(0x80, 0x100)), [("range", 0x80, 0xFF)]),
    ("hbrc", "capability/high-byte-run (cube spelling)", "dfa-pf byte-class",
     list(range(0x80, 0x100)), [("cube", 0x80, 0x80)]),
    ("u8l", "capability/utf8-lead-no-cont (bounded, hi = n - 1)", "dfa-pf byte-class-bounded",
     list(range(0xC2, 0xE0)), [("range", 0xC2, 0xDF)]),
    # DENSE CONTROLS: the bench's own non-losing range sites, which a row
    # serving ranges reaches too and must not regress (22 x [0-9], 12 x [a-z]).
    ("dig", "control: bench [0-9] prefilter sites (x22)", "dfa-pf byte-class",
     list(range(0x30, 0x3A)), [("range", 0x30, 0x39)]),
    ("lc", "control: bench [a-z] prefilter sites (x12)", "dfa-pf byte-class",
     list(range(0x61, 0x7B)), [("range", 0x61, 0x7A)]),
]


def rep8(b):
    return "0x%sull" % ("%02X" % b * 8)


def lane_ok(t):
    k = t[0]
    if k == "eq":
        return "(b == 0x%02X)" % t[1]
    if k == "cube":
        return "((b & 0x%02X) == 0x%02X)" % (t[1], t[2])
    return "((unsigned char)(b - 0x%02X) <= 0x%02X)" % (t[1], t[2] - t[1])


def swar_term(t):
    k = t[0]
    if k == "eq":
        x = "(w ^ %s)" % rep8(t[1])
        return "((%s - 0x0101010101010101ull) & ~%s & 0x8080808080808080ull)" % (x, x)
    if k == "cube":
        x = "((w & %s) ^ %s)" % (rep8(t[1]), rep8(t[2]))
        return "((%s - 0x0101010101010101ull) & ~%s & 0x8080808080808080ull)" % (x, x)
    # range: d = w - L per lane (no cross-lane borrow), then d < W per lane
    lo, wd = t[1], t[2] - t[1] + 1
    d = ("((((w | 0x8080808080808080ull) - %s) ^ ((w ^ ~%s) & 0x8080808080808080ull)))"
         % (rep8(lo & 0x7F), rep8(lo)))
    if wd >= 256:
        return "0x8080808080808080ull"
    if wd > 128:
        # in range iff NOT (d >= wd), and d >= wd iff (d - wd) per lane < 256 - wd
        raise SystemExit("range wider than 128 not needed by these cells")
    # d < wd (wd <= 128): lanes with d >= 128 fail; else (d & 7F) + (128 - wd) < 128
    return ("(~((((%s & 0x7F7F7F7F7F7F7F7Full) + %s) | %s)) & 0x8080808080808080ull)"
            % (d, rep8(128 - wd), d))


def simd_term(t, w):
    pre = "_mm" if w == 16 else "_mm256"
    si = "si128" if w == 16 else "si256"
    if t[0] == "eq":
        return "%s_cmpeq_epi8(v, %s_set1_epi8((char)0x%02X))" % (pre, pre, t[1])
    if t[0] == "cube":
        return ("%s_cmpeq_epi8(%s_and_%s(v, %s_set1_epi8((char)0x%02X)), %s_set1_epi8((char)0x%02X))"
                % (pre, pre, si, pre, t[1], pre, t[2]))
    return ("%s_cmpeq_epi8(%s_min_epu8(%s_sub_epi8(v, %s_set1_epi8((char)0x%02X)), %s_set1_epi8((char)0x%02X)), "
            "%s_sub_epi8(v, %s_set1_epi8((char)0x%02X)))"
            % (pre, pre, pre, pre, t[1], pre, t[2] - t[1], pre, pre, t[1]))


def or_all(xs, f):
    if len(xs) == 1:
        return xs[0]
    out = xs[0]
    for x in xs[1:]:
        out = f(out, x)
    return out


def emit_cell(cid, bench, site, S, terms, o):
    o.append("/* ---- %s: %s (%s), S = {%s}%s ---- */\n" % (
        cid, bench, site, ",".join("%02x" % b for b in S[:8]), "..." if len(S) > 8 else ""))
    # the table
    tbl = [1 if b in S else 0 for b in range(256)]
    o.append("static const unsigned char %s_T[256] = {%s};\n" % (cid, ",".join(map(str, tbl))))
    # table walk (today)
    o.append("NOINL size_t %s_table(const unsigned char *s, size_t lo, size_t hi)\n"
             "{ while (lo < hi && !%s_T[s[lo]]) lo++; return lo; }\n" % (cid, cid))
    # the scalar lane predicate (the swar tail; also the reference's own form is the TABLE)
    lane = " || ".join(lane_ok(t) for t in terms)
    o.append("static inline int %s_lane(unsigned char b) { return %s; }\n" % (cid, lane))
    forms = ["table"]
    if len(S) == 1:
        o.append("NOINL size_t %s_memchr(const unsigned char *s, size_t lo, size_t hi)\n"
                 "{\n    if (lo >= hi) return lo;\n"
                 "    const void *q = memchr(s + lo, 0x%02X, hi - lo);\n"
                 "    return q ? (size_t)((const unsigned char *)q - s) : hi;\n}\n" % (cid, S[0]))
        forms.append("memchr")
    if 2 <= len(S) <= 3:
        body = ["    if (lo >= hi) return lo;\n",
                "    size_t h = hi;\n    const void *q;\n"]
        for b in S:
            body.append("    q = h > lo ? memchr(s + lo, 0x%02X, h - lo) : 0;\n"
                        "    if (q) h = (size_t)((const unsigned char *)q - s);\n" % b)
        body.append("    return h;\n")
        o.append("NOINL size_t %s_mc%d(const unsigned char *s, size_t lo, size_t hi)\n{\n%s}\n"
                 % (cid, len(S), "".join(body)))
        forms.append("mc%d" % len(S))
    # swar
    st = or_all([swar_term(t) for t in terms], lambda a, b: "(%s | %s)" % (a, b))
    o.append("static inline size_t %s_swar_from(const unsigned char *s, size_t i, size_t hi)\n{\n"
             "    while (i + 8 <= hi) {\n"
             "        uint64_t w; memcpy(&w, s + i, 8);\n"
             "        uint64_t z = %s;\n"
             "        if (z) return i + (size_t)(__builtin_ctzll(z) >> 3);\n"
             "        i += 8;\n    }\n"
             "    while (i < hi && !%s_lane(s[i])) i++;\n"
             "    return i;\n}\n" % (cid, st, cid))
    o.append("NOINL size_t %s_swar(const unsigned char *s, size_t lo, size_t hi)\n"
             "{ if (lo >= hi) return lo; return %s_swar_from(s, lo, hi); }\n" % (cid, cid))
    forms.append("swar")
    # sse2 / avx2
    for w, isa, attr in ((16, "sse2", ""), (32, "avx2", "__attribute__((target(\"avx2\"))) ")):
        pre = "_mm" if w == 16 else "_mm256"
        si = "si128" if w == 16 else "si256"
        vt = "__m128i" if w == 16 else "__m256i"
        m = or_all([simd_term(t, w) for t in terms],
                   lambda a, b: "%s_or_%s(%s, %s)" % (pre, si, a, b))
        nxt = "%s_swar_from(s, i, hi)" % cid if w == 16 else "%s_sse2_from(s, i, hi, lo)" % cid
        o.append("#ifdef __x86_64__\n")
        o.append("%sstatic inline size_t %s_%s_from(const unsigned char *s, size_t i, size_t hi, size_t lo)\n{\n"
                 "    while (i + %d <= hi) {\n"
                 "        %s v = %s_loadu_%s((const %s *)(s + i));\n"
                 "        unsigned m = (unsigned)%s_movemask_epi8(%s);\n"
                 "        if (m) return i + (size_t)__builtin_ctz(m);\n"
                 "        i += %d;\n    }\n"
                 "    if (i < hi && hi - lo >= %d) {\n"
                 "        size_t b = hi - %d;\n"
                 "        %s v = %s_loadu_%s((const %s *)(s + b));\n"
                 "        unsigned m = (unsigned)%s_movemask_epi8(%s);\n"
                 "        m &= %s << (i - b);\n"
                 "        return m ? b + (size_t)__builtin_ctz(m) : hi;\n"
                 "    }\n"
                 "    return %s;\n}\n"
                 % (attr, cid, isa, w, vt, pre, si, vt, pre, m, w, w, w, vt, pre, si, vt, pre, m,
                    "0xFFFFu" if w == 16 else "0xFFFFFFFFu", nxt))
        o.append("%sNOINL size_t %s_%s(const unsigned char *s, size_t lo, size_t hi)\n"
                 "{ if (lo >= hi) return lo; return %s_%s_from(s, lo, hi, lo); }\n"
                 % (attr, cid, isa, cid, isa))
        o.append("#endif\n")
        forms.append(isa)
    return forms


def main():
    o = ["/* GENERATED by gen_twins.py (lane r17s, R-17). Do not edit. */\n",
         "#ifndef NOINL\n#define NOINL __attribute__((noinline))\n#endif\n"]
    table = []
    for c in CELLS:
        forms = emit_cell(*c, o)
        table.append((c[0], c[1], c[3], forms))
    o.append("typedef size_t (*find_fn)(const unsigned char *, size_t, size_t);\n")
    o.append("typedef struct { const char *cell, *form, *bench; find_fn f; int simd; "
             "const unsigned char *T; int bounded; } twin;\n")
    o.append("static const twin TWINS[] = {\n")
    for cid, bench, S, forms in table:
        for f in forms:
            simd = f in ("sse2", "avx2")
            line = "    { \"%s\", \"%s\", \"%s\", %s_%s, %d, %s_T, %d },\n" % (
                cid, f, bench, cid, f, 2 if f == "avx2" else 1 if simd else 0, cid,
                1 if cid == "u8l" else 0)
            o.append(("#ifdef __x86_64__\n" + line + "#endif\n") if simd else line)
    o.append("};\n#define NTWINS (sizeof TWINS / sizeof TWINS[0])\n")
    print("".join(o), end="")


if __name__ == "__main__":
    main()
