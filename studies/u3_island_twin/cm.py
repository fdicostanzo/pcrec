"""cm.py -- the CHARACTER-STEPPED MACHINE (the island form of
docs/design/ucp_design.md s3.1) and its C emitter.

A CM is one direction of one search machine, expressed over CHARACTERS:

  * ASCII bytes are stepped exactly as today: a byte-class table and a
    state x class transition table (the "ordinary cells").
  * every non-ASCII byte maps to ONE class, NA.  A state's NA cell is either
    an ordinary cell (self-loop fold, s3.3, or dead) or an ISLAND TOKEN in
    the reserved top range (ISL + state); the walk catches tokens and the
    dead sentinel with ONE unsigned compare, so the ASCII path gains no
    compare.
  * the island decodes the character (`P_decode`, the stage-4 body), takes
    its membership vector v (atom index, or BOT for an ill-formed byte, one
    byte long, in no set), and resumes at tgt[q][v].

Two accept modes (s3.8 H7): SCALAR -- accept is a property of the state
reached (the loop-top test the DFA has today) -- and BYCLASS -- accept
depends on the NEXT character, answered from a class-indexed table for ASCII
and from acc_isl[q][v] inside the island for non-ASCII (the mechanism
`\\b` uses today for ASCII).  The membership predicate `P_in(cp)` is
supplied separately (providers.py) so the same machine is timed against
each vector producer.
"""

ISL = 0x4000          # first island token; every ordinary state number is below
FLOOR = 0x4000        # (unsigned)st >= FLOOR  <=>  island token or dead(-1)


class CM:
    def __init__(self, name, nst, cls256, nasc, nxt, tgt, acc=None,
                 accn=None, aend=None, acc_isl=None, byclass=False,
                 can_begin=None, seed=None, natoms=2, req_byte=None):
        self.name = name
        self.nst = nst
        self.cls = cls256          # 256 entries; bytes >= 0x80 == nasc (NA)
        self.nasc = nasc           # number of ASCII classes; NA == nasc
        self.nxt = nxt             # nxt[q][c], c in 0..nasc ; NA col: 'I' -> island
        self.tgt = tgt             # tgt[q] = [target per v] (v: atoms..., BOT), or None
        self.acc = acc or [0] * nst
        self.byclass = byclass
        self.accn = accn           # accn[q][c] for ASCII classes (byclass)
        self.aend = aend or [0] * nst
        self.acc_isl = acc_isl     # acc_isl[q][v] (byclass)
        self.can_begin = can_begin
        self.req_byte = req_byte   # whole-window necessary byte (pcrec's REQ_BYTE pre-check), forward only
        self.seed = seed           # forward only: dict(abs=, asc=[per ascii class], isl=[per v])
        self.natoms = natoms
        self.nv = natoms + 1       # + BOT

    # cell classification for the NA column ---------------------------------
    def na_cell(self, q):
        t = self.tgt[q]
        if t is None:
            return -1
        if all(x == -1 for x in t):
            return -1                     # dead: no thread survives the character
        if (all(x == q for x in t) and not self.acc[q]
                and not (self.byclass and any(self.acc_isl[q]))):
            return q                      # self-loop fold (s3.3): never an ACCEPTING state,
                                          # whose mid-character bytes would record an accept
        return ISL + q


def _arr(name, ctype, vals, per=16):
    body = []
    for i in range(0, len(vals), per):
        body.append("    " + ", ".join(str(v) for v in vals[i:i + per]) + ",")
    return "static const %s %s[%d] = {\n%s\n};\n" % (ctype, name, len(vals), "\n".join(body))


DECODE = r"""
/* the stage-4 decoder body (enc_utf8.c u8_defs_bref_ci), verbatim: length in
 * bytes, or 0 when truncated or ill-formed */
static inline size_t P_decode(const unsigned char *s, size_t end, size_t p, unsigned *cp)
{
    unsigned char b = s[p];
    size_t len, i;
    unsigned v, floor;
    if (b < 0x80u)               { *cp = b; return 1; }
    else if ((b & 0xE0u) == 0xC0u) { len = 2; v = b & 0x1Fu; floor = 0x80u; }
    else if ((b & 0xF0u) == 0xE0u) { len = 3; v = b & 0x0Fu; floor = 0x800u; }
    else if ((b & 0xF8u) == 0xF0u) { len = 4; v = b & 0x07u; floor = 0x10000u; }
    else return 0;
    if (p + len > end) return 0;
    for (i = 1; i < len; i++) {
        if ((s[p + i] & 0xC0u) != 0x80u) return 0;
        v = (v << 6) | (unsigned)(s[p + i] & 0x3Fu);
    }
    if (v < floor || v > 0x10FFFFu || (v >= 0xD800u && v <= 0xDFFFu)) return 0;
    *cp = v;
    return len;
}

/* the REPAIRED back_step (utf8_design.md 5.2.1, ucp_design.md 3.5): walk back
 * over at most three continuation bytes to a lead byte that DECLARES exactly
 * the run walked, else one byte of BOT.  Returns the character's length and
 * sets *cp (0xFFFFFFFF == BOT). */
static inline size_t P_back(const unsigned char *s, size_t e, unsigned *cp)
{
    size_t q = e - 1, len;
    int k = 0;
    while (q > 0 && k < 3 && (s[q] & 0xC0u) == 0x80u) { q--; k++; }
    len = P_decode(s, e, q, cp);
    if (len && q + len == e) return len;
    *cp = 0xFFFFFFFFu;
    return 1;
}
"""


def _vec(nv_atoms):
    # the vector of one decoded character: atom 0 = out, atom 1 = in (one
    # set), BOT for an ill-formed byte.  Multi-set machines are not built here.
    assert nv_atoms == 2
    return "(len ? (unsigned)(P_in(cp) ? 1 : 0) : 2u)"


def emit(prefix, fwd, rev, guard=True):
    """C source of `int P_search(...)`.  P_in(cp) is declared, not defined."""
    P = prefix
    out = []
    out.append("/* island twin (hand-twin, studies/u3_island_twin): %s */" % prefix)
    out.append("#include <stddef.h>\n#include <stdint.h>\n#include <string.h>\n")
    out.append("#ifdef U3_COUNT\nunsigned long P_cnt[4]; /* 0 fwd island, 1 fwd BOT, 2 rev island, 3 rev BOT */\n#define U3C(i) (P_cnt[i]++)\n#else\n#define U3C(i) ((void)0)\n#endif\n".replace("P_", P + "_"))
    out.append(DECODE.replace("P_", P + "_"))
    NC_F = fwd.nasc + 1
    NC_R = rev.nasc + 1

    def tables(tag, m, NC):
        s = []
        s.append(_arr("%s_%s_cls" % (P, tag), "unsigned char", m.cls, 16))
        flat = []
        for q in range(m.nst):
            row = list(m.nxt[q])
            row[m.nasc] = m.na_cell(q)
            assert len(row) == NC
            flat += row
        s.append(_arr("%s_%s_nxt" % (P, tag), "short", flat))
        if m.byclass:
            fl = []
            for q in range(m.nst):
                fl += list(m.accn[q]) + [0]
            s.append(_arr("%s_%s_accn" % (P, tag), "unsigned char", fl))
            s.append(_arr("%s_%s_aend" % (P, tag), "unsigned char", m.aend))
            fl = []
            for q in range(m.nst):
                fl += list(m.acc_isl[q])
            s.append(_arr("%s_%s_acci" % (P, tag), "unsigned char", fl))
        if not m.byclass or any(m.acc):
            s.append(_arr("%s_%s_acc" % (P, tag), "unsigned char", m.acc))
        fl = []
        for q in range(m.nst):
            fl += list(m.tgt[q]) if m.tgt[q] is not None else [-1] * m.nv
        s.append(_arr("%s_%s_tgt" % (P, tag), "short", fl))
        return "\n".join(s)

    out.append(tables("f", fwd, NC_F))
    out.append(tables("r", rev, NC_R))
    if fwd.can_begin is not None:
        out.append(_arr("%s_can_begin" % P, "unsigned char", fwd.can_begin, 16))
    if fwd.seed is not None:
        out.append(_arr("%s_seed_asc" % P, "short", fwd.seed["asc"]))
        out.append(_arr("%s_seed_isl" % P, "short", fwd.seed["isl"]))
    out.append("static inline int %s_in(unsigned cp);\n" % P)
    # ------------------------------------------------------------------ fwd
    NVf, NVr = fwd.nv, rev.nv
    vec = "(len ? (unsigned)(%s_in(cp) ? 1 : 0) : %du)" % (P, fwd.natoms)
    f = []
    f.append("int %s_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2])\n{" % P)
    if guard:
        f.append("    if (!(from == 0 || from >= n || (s[from] & 0xC0) != 0x80)) return -7;")
    f.append("    size_t pos = from, last = (size_t)-1;")
    f.append("    unsigned cp = 0; size_t len; unsigned v; (void)v;")
    if fwd.seed is not None:
        f.append("    int st = %d;" % fwd.seed["abs"])
        f.append("    if (from > 0 && from <= n) {")
        f.append("        unsigned char pb = s[from - 1];")
        f.append("        if (pb < 0x80) st = %s_seed_asc[%s_f_cls[pb]];" % (P, P))
        f.append("        else { len = %s_back(s, from, &cp); v = %s; st = %s_seed_isl[v]; }" % (P, vec, P))
        f.append("    }")
    else:
        f.append("    int st = 0;")
    f.append("    if (from > n) return 0;")
    if fwd.req_byte is not None:
        f.append("    if (!memchr(s + from, %d, n - from)) return 0;   /* the necessary-byte whole-window pre-check pcrec emits today (RX_REQ_BYTE) */" % fwd.req_byte)
    f.append("    for (;;) {")
    if not fwd.byclass:
        f.append("        if (%s_f_acc[st]) last = pos;" % P)
        if fwd.can_begin is not None:
            f.append("        if (st == 0 && last == (size_t)-1) {")
            f.append("            while (pos < n && !%s_can_begin[s[pos]]) pos++;" % P)
            f.append("            if (pos >= n) return 0;")
            f.append("        }")
        f.append("        if (pos >= n) break;")
        f.append("        st = %s_f_nxt[st * %d + %s_f_cls[s[pos++]]];" % (P, NC_F, P))
        f.append("        if ((unsigned)st < %du) continue;" % FLOOR)
        f.append("        if (st < 0) break;")
        f.append("        { int q = st - %d; size_t p = pos - 1;" % ISL)
        f.append("          len = %s_decode(s, n, p, &cp); v = %s; U3C(0); if (!len) { len = 1; U3C(1); }" % (P, vec))
        f.append("          st = %s_f_tgt[q * %d + v]; pos = p + len; if (st < 0) break; }" % (P, NVf))
    else:
        f.append("        if (%s_f_acc[st]) last = pos;" % P if any(fwd.acc) else "")
        f.append("        if (pos >= n) { if (%s_f_aend[st]) last = pos; break; }" % P)
        f.append("        { unsigned c = %s_f_cls[s[pos]];" % P)
        f.append("          if (%s_f_accn[st * %d + c]) last = pos;" % (P, NC_F))
        f.append("          st = %s_f_nxt[st * %d + c]; pos++; }" % (P, NC_F))
        f.append("        if ((unsigned)st < %du) continue;" % FLOOR)
        f.append("        if (st < 0) break;")
        f.append("        { int q = st - %d; size_t p = pos - 1;" % ISL)
        f.append("          len = %s_decode(s, n, p, &cp); v = %s; U3C(0); if (!len) { len = 1; U3C(1); }" % (P, vec))
        f.append("          if (%s_f_acci[q * %d + v]) last = p;" % (P, NVf))
        f.append("          st = %s_f_tgt[q * %d + v]; pos = p + len; if (st < 0) break; }" % (P, NVf))
    f.append("    }")
    f.append("    if (last == (size_t)-1) return 0;")
    # ------------------------------------------------------------------ rev
    vecr = "(len ? (unsigned)(%s_in(cp) ? 1 : 0) : %du)" % (P, rev.natoms)
    f.append("    {")
    f.append("        size_t end = last, start = (size_t)-1, rp = end; int rs = 0;")
    f.append("        for (;;) {")
    if not rev.byclass:
        f.append("            if (%s_r_acc[rs]) start = rp;" % P)
        f.append("            if (rp <= from) break;")
        f.append("            rs = %s_r_nxt[rs * %d + %s_r_cls[s[--rp]]];" % (P, NC_R, P))
        f.append("            if ((unsigned)rs < %du) continue;" % FLOOR)
        f.append("            if (rs < 0) break;")
        f.append("            { int q = rs - %d; size_t e = rp + 1;" % ISL)
        f.append("              len = %s_back(s, e, &cp); v = %s; U3C(2); if (cp == 0xFFFFFFFFu) U3C(3);" % (P, vecr))
        f.append("              rp = e - len; rs = %s_r_tgt[q * %d + v]; if (rs < 0) break; }" % (P, NVr))
    else:
        f.append("            if (rp == 0) { if (%s_r_aend[rs]) start = rp; break; }" % P)
        f.append("            { size_t e = rp; unsigned char b = s[e - 1];")
        f.append("              if (b < 0x80) {")
        f.append("                  unsigned c = %s_r_cls[b];" % P)
        f.append("                  if (%s_r_accn[rs * %d + c]) start = rp;" % (P, NC_R))
        f.append("                  if (rp <= from) break;")
        f.append("                  rs = %s_r_nxt[rs * %d + c]; rp--; if (rs < 0) break; continue;" % (P, NC_R))
        f.append("              }")
        f.append("              len = %s_back(s, e, &cp); v = %s; U3C(2); if (cp == 0xFFFFFFFFu) U3C(3);" % (P, vecr))
        f.append("              if (%s_r_acci[rs * %d + v]) start = rp;" % (P, NVr))
        f.append("              if (rp <= from) break;")
        f.append("              rs = %s_r_tgt[rs * %d + v]; rp = e - len; if (rs < 0) break; }" % (P, NVr))
    f.append("        }")
    f.append("        if (start == (size_t)-1) return 0;")
    f.append("        if (caps) { caps[0][0] = (ptrdiff_t)start; caps[0][1] = (ptrdiff_t)end; }")
    f.append("        return 1;")
    f.append("    }")
    f.append("}")
    out.append("\n".join(x for x in f if x != ""))
    src = "\n".join(out)
    return src
