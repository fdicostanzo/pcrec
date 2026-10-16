#!/usr/bin/env python3
"""grid2: the three NEW variant generators (r17b_prime.md §5.4 prep). grid1's mkvar.py
is untouched and still builds the W8/SSE2/AVX2 arms; this file adds

  mkvar2.py disp  NEW.c DENY.c OUT.c FORM [A1.c]
        the DISPATCH TWIN. NEW.c is the cell's R17-b artifact (V1, W8), DENY.c the same
        pattern with the table walk, A1.c (FORM 2 only) mkvar.py's v32 output for the
        cell. OUT.c is r17b_prime.md §2.2's scaffold with the form byte `f` FORCED to
        FORM (0 WALK, 1 V1, 2 W64 = A1): (a) WALK + V1 for FORM 0/1, (b) WALK + V1 + W64
        for FORM 2. The struct gains `f`, the file the walk helper (over the DENY
        artifact's own table), `__form`, `__next` (and the `__w32` function for (b));
        the storage point initializes `f` from `__form(n, start)` and the use calls
        `__next`. `__form` is OPAQUE: it returns FORM for every span < 2^62 through one
        runtime compare on `n - lo`, so gcc cannot fold the dispatch away (a constant
        `f` would be SROA'd into the single form and the twin would measure nothing).
        That compare stands for the real rows' span compare (§2.2's `span < 36`).
  mkvar2.py scaf DENY.c OUT.c
        the WALK-ONLY SCAFFOLD (M18: walk-in-helper vs walk-inline). DENY.c's inline walk
        moves into a helper reached through a {s, n} struct, nothing else changes.
  mkvar2.py ob    ART.c OUT.c VARIANT BYTE [HDR.c]
        the one-byte cells (items 3, 4): ART.c is the compiler's own artifact of a
        one-byte consumer (its FIND is `memchr(P, BYTE, LEN)`); VARIANT is
          libc  the artifact verbatim (copy)
          walk  the FIND as a table walk at |S| = 1 (a 256-entry table, pcrec's walk)
          loop  the FIND as the generic byte loop (compare to BYTE)
          v1    the FIND as ONE-TERM SWAR, V1's W8 block over `pcrec_mfk_w8_eq` (HDR.c
                supplies the kit's W8 block: the text of an artifact that carries it);
                STATELESS here: V1's cache needs a declaration point a libc site lacks
          none  the use's FIND statement DELETED: the guard block holding it goes and
                the consumer walks (r17b_prime §1.3 F0)
        Every variant but `none` replaces only the memchr CALL by a call of an inline
        helper with memchr's signature, so the consumer's text is untouched.
"""
import re, sys


def die(m):
    raise SystemExit("mkvar2: " + m)


def balanced(txt, start):
    """index just past the ')' closing the '(' at txt[start]"""
    d = 0
    for i in range(start, len(txt)):
        if txt[i] == "(": d += 1
        elif txt[i] == ")":
            d -= 1
            if d == 0: return i + 1
    die("unbalanced parentheses")


def stem_of(txt):
    m = re.search(r"struct (\w+)__c \{", txt)
    if not m: die("no site struct (not an R17-b `new` artifact)")
    return m.group(1)


def walk_parts(deny):
    """(table name, table initializer text, K) from the DENY artifact's walk"""
    m = re.search(r"while \(scan_position(?: \+ (\d))? < subject_length && !(\w+)\[subject\[scan_position\]\]\) scan_position\+\+;", deny)
    if not m: die("no table walk in the deny artifact")
    k, name = int(m.group(1) or 0), m.group(2)
    t = re.search(r"static const unsigned char " + name + r"\[256\] = \{(.*?)\n\s*\};", deny, re.S)
    if not t: die("table %s not found" % name)
    return name, t.group(1), k, m.group(0)


def insert_before(txt, pat, add):
    m = re.search(pat, txt, re.M)
    if not m: die("no anchor for " + pat)
    return txt[:m.start()] + add + txt[m.start():]


def opaque_form(stem, form):
    return (f"static inline unsigned char {stem}__form(size_t n, size_t lo)\n{{\n"
            f"    unsigned char f = {form};\n"
            f"    if ((n - lo) >> 62) f = {1 if form == 0 else 0};   /* stands for the rows' span compare; {form} for every real span */\n"
            f"    return f;\n}}\n")


def disp(new_p, deny_p, out_p, form, a1_p=None):
    txt, deny = open(new_p).read(), open(deny_p).read()
    stem = stem_of(txt)
    tab, init, K, _ = walk_parts(deny)
    # struct: the form byte
    txt, n = re.subn(r"(struct %s__c \{[^}]*?unsigned long long m;\n)(\};)" % stem, r"\1    unsigned char f;\n\2", txt, count=1)
    if n != 1: die("struct field")
    helpers = (f"static const unsigned char {stem}__tab[256] = {{{init}\n}};\n"
               f"static inline size_t {stem}__walk(const struct {stem}__c *c, size_t lo)\n{{\n"
               f"    while (lo + {K} < c->n && !{stem}__tab[c->s[lo]]) lo++;\n    return lo;\n}}\n")
    nxt_pat = r"^static inline size_t %s__next_candidate\(" % stem
    w32 = ""
    if form == 2:
        if not a1_p: die("FORM 2 needs A1.c")
        a1 = open(a1_p).read()
        v32 = re.search(r"#ifndef VS_V32_H.*?\n#endif\n", a1, re.S)
        rest = re.search(r"static inline unsigned long long %s__lanes\(.*?^static inline size_t %s__next_candidate\(.*?^\}\n" % (stem, stem), a1, re.S | re.M)
        if not v32 or not rest: die("cannot extract the W64 function from A1.c")
        w32 = v32.group(0) + rest.group(0).replace(f"{stem}__next_candidate(", f"{stem}__next_candidate__w32(")
    txt = insert_before(txt, nxt_pat, w32 + helpers)
    sel = opaque_form(stem, form)
    third = (f"    if (c->f == 2) return {stem}__next_candidate__w32(c, lo);\n" if form == 2 else "")
    sel += (f"static inline size_t {stem}__next(struct {stem}__c *c, size_t lo)\n{{\n"
            f"    if (c->f == 0) return {stem}__walk(c, lo);\n{third}"
            f"    return {stem}__next_candidate(c, lo);\n}}\n")
    # after next_candidate's closing brace: the selector functions
    m = re.search(nxt_pat, txt, re.M)
    end = re.compile(r"^\}\n", re.M).search(txt, m.end())
    txt = txt[:end.end()] + sel + txt[end.end():]
    # storage point and use
    txt, n = re.subn(r"(struct %s__c %s__c = \{ subject, subject_length, 0, 0, 0)( \};)" % (stem, stem),
                     r"\1, %s__form(subject_length, search_from)\2" % stem, txt)
    if n != 1: die("storage point")
    txt, n = re.subn(r"%s__next_candidate\(&%s__c, " % (stem, stem), f"{stem}__next(&{stem}__c, ", txt)
    if n < 1: die("use")
    open(out_p, "w").write(txt)


def scaf(deny_p, out_p):
    deny = open(deny_p).read()
    tab, init, K, loop = walk_parts(deny)
    stem = "rx_search_pf"
    helpers = (f"struct {stem}__c {{\n    const unsigned char *s;\n    size_t n;\n}};\n"
               f"static const unsigned char {stem}__tab[256] = {{{init}\n}};\n"
               f"static inline size_t {stem}__walk(const struct {stem}__c *c, size_t lo)\n{{\n"
               f"    while (lo + {K} < c->n && !{stem}__tab[c->s[lo]]) lo++;\n    return lo;\n}}\n")
    txt = insert_before(deny, r"^int rx_search\(const unsigned char", helpers)
    txt, n = re.subn(re.escape(loop), f"scan_position = {stem}__walk(&{stem}__c, scan_position);", txt)
    if n != 1: die("walk statement")
    txt = insert_before(txt, r"^\s*size_t scan_position = ", f"    struct {stem}__c {stem}__c = {{ subject, subject_length }};\n")
    open(out_p, "w").write(txt)


TICK = """#ifdef G2_COUNT
#include <stdio.h>
static unsigned long long g2_calls, g2_bytes;
__attribute__((destructor)) static void g2_report(void) { fprintf(stderr, "g2_find calls=%llu bytes=%llu\\n", g2_calls, g2_bytes); }
#define G2_TICK(len) (g2_calls++, g2_bytes += (len))
#else
#define G2_TICK(len) ((void)0)
#endif
"""
V1_HELPER = TICK + """static inline const void *g2_find(const void *vp, int b, size_t len)
{
    G2_TICK(len);
    const unsigned char *p = (const unsigned char *)vp;
    size_t i = 0;
    for (; i + 8 <= len; i += 8) {
        unsigned long long m = pcrec_mfk_w8_lane_mask(pcrec_mfk_w8_eq(pcrec_mfk_w8_load_vector(p + i), (unsigned)b));
        if (m) return p + i + pcrec_mfk_w8_first_lane(m);
    }
    if (i >= len) return 0;
    if (len >= 8) {
        size_t t = len - 8;
        unsigned long long m = pcrec_mfk_w8_lane_mask(pcrec_mfk_w8_eq(pcrec_mfk_w8_load_vector(p + t), (unsigned)b)) >> (i - t);
        return m ? p + i + pcrec_mfk_w8_first_lane(m) : 0;
    }
    for (; i < len; i++) if (p[i] == (unsigned char)b) return p + i;
    return 0;
}
"""
LOOP_HELPER = TICK + """static inline const void *g2_find(const void *vp, int b, size_t len)
{
    G2_TICK(len);
    const unsigned char *p = (const unsigned char *)vp;
    for (size_t i = 0; i < len; i++) if (p[i] == (unsigned char)b) return p + i;
    return 0;
}
"""
WALK_HELPER = TICK + """static const unsigned char g2_tab[256] = { [%d] = 1 };
static inline const void *g2_find(const void *vp, int b, size_t len)
{
    G2_TICK(len);
    const unsigned char *p = (const unsigned char *)vp;
    size_t i = 0;
    (void)b;
    while (i < len && !g2_tab[p[i]]) i++;
    return i < len ? p + i : 0;
}
"""


def ob(art_p, out_p, variant, byte, hdr_p=None):
    txt = open(art_p).read()
    if variant == "libc":
        open(out_p, "w").write(txt); return
    if variant == "none":
        lines = txt.split("\n")
        hit = None
        for k, l in enumerate(lines):
            if re.search(r"memchr\(\s*[^,]+,\s*%d\s*," % byte, l): hit = k; break
        if hit is None: die("no memchr of byte %d" % byte)
        guard = re.compile(r"^(\s*)if \((forward_state == 0 && last_accept_position == \(size_t\)-1|start > 0 && subject\[start - 1\] != 10)\) \{$")
        g = None
        for k in range(hit, -1, -1):
            m = guard.match(lines[k])
            if m: g = (k, m.group(1)); break
        if g is None: die("no guard block above the FIND")
        k, ind = g
        e = k + 1
        while lines[e] != ind + "}": e += 1
        if not (k < hit < e): die("guard does not contain the FIND")
        del lines[k:e + 1]
        open(out_p, "w").write("\n".join(lines)); return
    helper = {"loop": LOOP_HELPER, "walk": WALK_HELPER.replace("%d", str(byte)), "v1": V1_HELPER}[variant]
    if variant == "v1":
        if not hdr_p: die("v1 needs HDR.c")
        h = re.search(r"#ifndef PCREC_MFK_W8_H.*?\n#endif\n", open(hdr_p).read(), re.S)
        if not h: die("no W8 block in HDR.c")
        helper = h.group(0) + helper
    n = 0
    out = []
    pos = 0
    for m in re.finditer(r"\bmemchr\(", txt):
        end = balanced(txt, m.end() - 1)
        args = txt[m.end():end - 1]
        parts = [a.strip() for a in re.split(r",(?![^()]*\))", args)]
        if len(parts) == 3 and parts[1] == str(byte):
            out.append(txt[pos:m.start()]); out.append(f"g2_find({parts[0]}, {byte}, {parts[2]})")
            pos = end; n += 1
    out.append(txt[pos:])
    if n < 1: die("no memchr of byte %d to replace" % byte)
    txt = "".join(out)
    txt, k = re.subn(r"(#include <string\.h>\n)", lambda m: m.group(1) + helper, txt, count=1)
    if k != 1: die("no #include <string.h> anchor")
    open(out_p, "w").write(txt)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: die(__doc__)
    if a[0] == "disp": disp(a[1], a[2], a[3], int(a[4]), a[5] if len(a) > 5 else None)
    elif a[0] == "scaf": scaf(a[1], a[2])
    elif a[0] == "ob": ob(a[1], a[2], a[3], int(a[4]), a[5] if len(a) > 5 else None)
    else: die(__doc__)
