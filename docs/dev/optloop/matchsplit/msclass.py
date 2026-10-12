#!/usr/bin/env python3
"""[MATCH-SPLIT] STEP-0: the path-class analysis of docs/design/
match_split_requirements.md section 2.2, over msprobe's RAW-parse AST dump.

A class is a property of PATHS through the pattern, not of the syntax.  Each
live path carries
    sp   start pins   S  (^ \\A, absolute 0)   G  (\\G, search_from)
                      LS ((?m)^ at the path's LEADING position)
    ep   end pins     E  ($ \\Z, n or n-1)     EZ (\\z, n)
                      LE ((?m)$ at the path's TRAILING position)
    z    what the path consumes: Z nothing, NL only newline bytes, N other
    lu   the path's first consuming atom sits in an unbounded repeat
and a summary of a node is the SET of such elements over its paths.

  * an ABSOLUTE start pin (S, G) on a path that already consumed a byte is
    dead; an absolute end pin (E needs Z|NL after it, EZ needs Z) followed
    by more consumption is dead;
  * a LINE pin ((?m)^ / (?m)$) away from the path's edge is a landmark, not a
    pin: it is dropped (and counted in flags.ml_landmark), the path is FREE;
  * anchors inside lookarounds do not classify; they are counted (look_pin).

Also here: the structural redundancy check (a pinned path whose pin-erased
atom sequence equals a free path's: `(?:^)?ab`) and the sub-language texts
(FREE = paths with no pin; END = paths with an end pin) the survey compiles
on their own.  The texts are an UNPARSE of the raw tree; survey.py checks the
unparse of the WHOLE tree against the original's stamps (control C-RT).
"""
import itertools

PLANT = set()   # C4's deliberate defects: 'ml_edge', 'look_end' (survey.py --plant)

Z, NL, N = 0, 1, 2
S, G, LS = 1, 2, 4
E, EZ, LE = 1, 2, 4


class Flags:
    def __init__(self):
        self.dead = 0          # a combination discarded because an absolute pin was unsatisfiable
        self.ml_landmark = 0   # a (?m) pin dropped to a landmark (not at the path's edge)
        self.look_pin = set()  # kinds of lookaround whose body carries a pin
        self.ref = set()       # bref / var / call present
        self.ctx = 0
        self.kreset = 0


def join_z(a, b):
    return max(a, b)


def cat2(A, B, fl):
    out = set()
    for (asp, aep, az, alu) in A:
        for (bsp, bep, bz, blu) in B:
            sp = asp
            bs = bsp
            if bs and az != Z:
                if bs & (S | G):
                    fl.dead += 1
                    continue
                if bs & LS and "ml_edge" not in PLANT:
                    fl.ml_landmark += 1
                    bs &= ~LS
            sp |= bs
            ep = bep
            ae = aep
            if ae:
                ok = True
                if ae & E and bz == N:
                    fl.dead += 1
                    ok = False
                elif ae & EZ and bz != Z:
                    fl.dead += 1
                    ok = False
                if not ok:
                    continue
                if ae & LE and bz != Z:
                    fl.ml_landmark += 1
                    ae &= ~LE
            ep |= ae
            z = join_z(az, bz)
            lu = alu if az != Z else blu
            out.add((sp, ep, z, lu))
    return out


def summ(n, fl):
    k = n[0]
    if k == "cat":
        acc = {(0, 0, Z, 0)}
        for c in n[1:]:
            acc = cat2(acc, summ(c, fl), fl)
        return acc
    if k == "alt":
        out = set()
        for c in n[1:]:
            out |= summ(c, fl)
        return out
    if k == "c":
        z = NL if n[1] == [[10, 10]] else N
        return {(0, 0, z, 0)}
    if k == "cbig":
        return {(0, 0, N, 0)}
    if k == "e":
        return {(0, 0, Z, 0)}
    if k == "k":
        fl.kreset += 1       # \\K moves the REPORTED start, not the attempt start the classes talk about
        return {(0, 0, Z, 0)}
    if k == "ctx":
        fl.ctx += 1
        return {(0, 0, Z, 0)}
    if k == "bol":
        return {(LS if n[1] else S, 0, Z, 0)}
    if k == "eol":
        return {(0, LE if n[1] else E, Z, 0)}
    if k == "end":
        return {(0, EZ, Z, 0)}
    if k == "g":
        return {(G, 0, Z, 0)}
    if k in ("cap", "atom", "wc"):
        return summ(n[-1], fl)
    if k in ("bref", "var", "call"):
        fl.ref.add(k)
        return {(0, 0, Z, 0), (0, 0, N, 0)}
    if k == "look":
        sub = Flags()
        body = summ(n[4], sub)
        fl.ref |= sub.ref
        if any(sp or ep for (sp, ep, z, lu) in body):
            fl.look_pin.add(("behind" if n[1] else "ahead") + ("-neg" if n[2] else "-pos"))
            if "look_end" in PLANT:
                return {(sp, ep, Z, 0) for (sp, ep, z, lu) in body}
        return {(0, 0, Z, 0)}
    if k == "rep":
        rmin, rmax, body = n[1], n[2], n[5]
        B = summ(body, fl)
        res = set()
        if rmin == 0:
            res.add((0, 0, Z, 0))
        if rmax == 0:
            return res
        lo = max(rmin, 1)
        hi = rmax if rmax >= 0 else 10 ** 9
        if lo > 4:
            ks = [4]
        else:
            ks = [x for x in range(1, 5) if lo <= x <= hi]
        P = None
        for kk in range(1, max(ks) + 1 if ks else 1):
            P = B if P is None else cat2(P, B, fl)
            if kk in ks:
                res |= P
        if rmax < 0:
            # an unbounded repeat LEADS a path that consumed anything inside it
            res = {(sp, ep, z, 1) if z != Z else (sp, ep, z, lu) for (sp, ep, z, lu) in res}
        return res
    raise ValueError("unknown node " + k)


def classes(elems):
    """Per-path class: start pin first, then end pin, else F."""
    out = []
    for (sp, ep, z, lu) in elems:
        if sp & S:
            c = "S"
        elif sp & G:
            c = "G"
        elif sp & LS:
            c = "LS"
        elif ep & (E | EZ):
            c = "E"
        elif ep & LE:
            c = "LE"
        else:
            c = "F"
        out.append(c)
    return out


# ---- structural redundancy ---------------------------------------------------

def canon(n):
    """Pin-erased canonical text of a subtree, for atom signatures."""
    k = n[0]
    if k in ("bol", "eol", "end", "g", "e"):
        return ""
    if k == "cat":
        return "".join(canon(c) for c in n[1:])
    if k == "alt":
        return "(" + "|".join(canon(c) for c in n[1:]) + ")"
    if k == "c":
        return "C" + repr(n[1])
    if k in ("cap", "atom", "wc"):
        return canon(n[-1])
    if k == "rep":
        return "R%d,%d,%d,%d(%s)" % (n[1], n[2], n[3], n[4], canon(n[5]))
    if k == "look":
        return "L%d%d%d(%s)" % (n[1], n[2], n[3], canon(n[4]))
    if k == "ctx":
        return "X%d,%d,%s" % (n[1], n[2], repr(n[3]) if len(n) > 3 else "")
    return k


class PathCap(Exception):
    pass


CAP_PATHS = 256


def has_pin(n):
    k = n[0]
    if k in ("bol", "eol", "end", "g"):
        return True
    if k in ("cat", "alt"):
        return any(has_pin(c) for c in n[1:])
    if k in ("cap", "atom", "wc"):
        return has_pin(n[-1])
    if k == "rep":
        return has_pin(n[5])
    return False


def paths(n):
    """[(sp, ep, atoms, bad)] -- bad: a pin not at its edge of the path."""
    k = n[0]
    if k == "cat":
        acc = [(0, 0, (), False)]
        for c in n[1:]:
            P = paths(c)
            nxt = []
            for (asp, aep, aat, abad) in acc:
                for (bsp, bep, bat, bbad) in P:
                    bad = abad or bbad
                    if bsp and aat:
                        bad = True
                    if aep and bat:
                        bad = True
                    nxt.append((asp | (0 if aat else bsp), bep | (0 if bat else aep),
                                aat + bat, bad))
            if len(nxt) > CAP_PATHS:
                raise PathCap()
            acc = nxt
        return acc
    if k == "alt":
        out = []
        for c in n[1:]:
            out += paths(c)
        if len(out) > CAP_PATHS:
            raise PathCap()
        return out
    if k == "bol":
        return [(LS if n[1] else S, 0, (), False)]
    if k == "eol":
        return [(0, LE if n[1] else E, (), False)]
    if k == "end":
        return [(0, EZ, (), False)]
    if k == "g":
        return [(G, 0, (), False)]
    if k in ("e", "k"):
        return [(0, 0, (), False)]
    if k in ("cap", "atom", "wc"):
        return paths(n[-1])
    if k == "rep":
        body = n[5]
        if not has_pin(body):
            return [(0, 0, ("R%d,%d,%d,%d(%s)" % (n[1], n[2], n[3], n[4], canon(body)),), False)]
        out = []
        if n[1] == 0:
            out.append((0, 0, (), False))
        if n[2] != 0:
            out += paths(body)
        return out
    return [(0, 0, (canon(n),), False)]


def redundancy(root):
    """For each start/end pin kind: do all live pinned paths erase to a free path?
    Returns dict kind -> ('all'|'some'|'none'|'n/a', n_pinned) or None when capped."""
    try:
        P = paths(root)
    except PathCap:
        return None
    free = {p[2] for p in P if not p[0] and not p[1] and not p[3]}
    res = {}
    for kind, sel in (("S", lambda sp, ep: sp & S), ("G", lambda sp, ep: sp & G),
                      ("LS", lambda sp, ep: sp & LS), ("E", lambda sp, ep: ep & (E | EZ)),
                      ("LE", lambda sp, ep: ep & LE)):
        pinned = [p for p in P if sel(p[0], p[1]) and not p[3]]
        if not pinned:
            continue
        red = [p for p in pinned if p[2] in free]
        res[kind] = ("all" if len(red) == len(pinned) else "some" if red else "none", len(pinned))
    return res


# ---- unparse -----------------------------------------------------------------

class Unsupported(Exception):
    pass


def hx(v):
    return "\\x{%x}" % v


def set_text(iv, neg=False):
    if not iv:
        return "(?!)"
    return "[" + "".join(hx(lo) if lo == hi else hx(lo) + "-" + hx(hi) for lo, hi in iv) + "]"


def wrap(t, need):
    """t is (text, prec); prec 0 alt, 1 cat, 2 atom.  Return text safe at `need`."""
    s, p = t
    return s if p >= need else "(?:" + s + ")"


def always_z(n, cache={}):
    fl = Flags()
    return all(z == Z for (_, _, z, _) in summ(n, fl))


class Texts:
    """Sub-language texts of a node: A (all), NP (no pin), NE (no end pin),
    E (has an end pin).  Each None (empty language) or (text, prec)."""

    def __init__(self, A, NP, NE, E):
        self.A, self.NP, self.NE, self.E = A, NP, NE, E


def t_alt(items):
    items = [t for t in items if t is not None]
    if not items:
        return None
    if len(items) == 1:
        return items[0]
    return ("|".join(wrap(t, 0) for t in items), 0)


def t_cat(items):
    if any(t is None for t in items):
        return None
    if len(items) == 1:
        return items[0]
    return ("".join(wrap(t, 1) for t in items), 1)


def quant(rmin, rmax, greedy, poss):
    q = "{%d,%d}" % (rmin, rmax) if rmax >= 0 else "{%d,}" % rmin
    if poss:
        q += "+"
    elif not greedy:
        q += "?"
    return q


def texts(n, lead, trail, approx):
    k = n[0]
    if k == "cat":
        ch = n[1:]
        az = [always_z(c) for c in ch]
        T = []
        for i, c in enumerate(ch):
            ld = lead and all(az[:i])
            tr = trail and all(az[i + 1:])
            T.append(texts(c, ld, tr, approx))
        A = t_cat([t.A for t in T])
        NP = t_cat([t.NP for t in T])
        NE = t_cat([t.NE for t in T])
        Eparts = []
        for i in range(len(T)):
            if T[i].E is None:
                continue
            Eparts.append(t_cat([t.NE for t in T[:i]] + [T[i].E] + [t.A for t in T[i + 1:]]))
        return Texts(A, NP, NE, t_alt(Eparts))
    if k == "alt":
        T = [texts(c, lead, trail, approx) for c in n[1:]]
        return Texts(t_alt([t.A for t in T]), t_alt([t.NP for t in T]),
                     t_alt([t.NE for t in T]), t_alt([t.E for t in T]))
    if k == "c":
        t = (set_text(n[1]), 2)
        return Texts(t, t, t, None)
    if k == "cbig":
        raise Unsupported("cbig")
    if k == "e":
        t = ("", 1)
        return Texts(t, t, t, None)
    if k == "k":
        t = ("\\K", 2)
        return Texts(t, t, t, None)
    if k == "ctx":
        anchor, fn, iv = n[1], n[2], n[3]
        if anchor:
            if fn == 6:
                t = ("\\b", 2)
            elif fn == 9:
                t = ("\\B", 2)
            else:
                raise Unsupported("ctx-fn")
        else:
            pre = {10: "(?=", 5: "(?!", 12: "(?<=", 3: "(?<!"}.get(fn)
            if pre is None:
                raise Unsupported("ctx-fn")
            t = (pre + set_text(iv) + ")", 2)
        return Texts(t, t, t, None)
    if k in ("bol", "eol", "end", "g"):
        if k == "bol":
            txt = "(?m:^)" if n[1] else "\\A"
        elif k == "eol":
            txt = "(?m:$)" if n[1] else "\\Z"
        elif k == "end":
            txt = "\\z"
        else:
            txt = "\\G"
        t = (txt, 2)
        if k == "g" or (k == "bol" and not n[1]):
            return Texts(t, None, t, None)
        if k == "bol":               # (?m)^
            return Texts(t, None if lead else t, t, None)
        if k in ("end",) or (k == "eol" and not n[1]):
            return Texts(t, None, None, t)
        # (?m)$
        return Texts(t, None if trail else t, None if trail else t, t if trail else None)
    if k == "cap":
        T = texts(n[2], lead, trail, approx)

        def cp(x):
            return None if x is None else ("(" + x[0] + ")", 2)
        return Texts(cp(T.A), cp(T.NP), cp(T.NE), cp(T.E))
    if k == "atom":
        T = texts(n[1], lead, trail, approx)

        def at(x):
            return None if x is None else ("(?>" + x[0] + ")", 2)
        return Texts(at(T.A), at(T.NP), at(T.NE), at(T.E))
    if k == "wc":
        return texts(n[1], lead, trail, approx)
    if k == "bref" and n[2] == 1:
        t = ("\\g{%d}" % n[3][0], 2)
        if n[1]:
            t = ("(?i:" + t[0] + ")", 2)
        return Texts(t, t, t, None)
    if k == "call":
        t = ("(?R)" if n[1] == 0 else "(?%d)" % n[1], 2)
        return Texts(t, t, t, None)
    if k in ("bref", "var"):
        raise Unsupported(k)
    if k == "look":
        behind, neg, atomic = n[1], n[2], n[3]
        body = texts(n[4], False, False, approx).A
        if atomic:
            pre = "(?<" if behind else "(?"
            pre += "!" if neg else "="
        else:       # the non-atomic positive lookarounds, (*napla: and (*naplb:
            if neg:
                raise Unsupported("look-nonatomic-neg")
            pre = "(*naplb:" if behind else "(*napla:"
        t = (pre + (body[0] if body else "(?!)") + ")", 2)
        return Texts(t, t, t, None)
    if k == "rep":
        rmin, rmax, gr, po, body = n[1], n[2], n[3], n[4], n[5]
        T = texts(body, lead, trail, approx)
        q = quant(rmin, rmax, gr, po)

        def rp(x, zero_ok):
            if x is None:
                return ("(?:)", 2) if rmin == 0 else None
            return (wrap(x, 2) + q, 1)     # a quantified atom is not itself repeatable: prec 1
        A = rp(T.A, True)
        NP = rp(T.NP, True)
        NE = rp(T.NE, True)
        E_ = None
        if T.E is not None:
            approx.append("rep-end")
            if rmin <= 1:
                nea = wrap(T.NE, 2) + "*" if T.NE else ""
                aa = wrap(T.A, 2) + "*" if T.A else ""
                E_ = ("(?:" + nea + wrap(T.E, 2) + aa + ")", 2) if True else None
        return Texts(A, NP, NE, E_)
    raise ValueError(k)


def classify(root):
    """-> dict with elems, per-class sets, flags, redundancy, texts."""
    fl = Flags()
    el = summ(root, fl)
    cl = classes(el)
    d = dict(elems=sorted(el), classes=cl, dead=fl.dead, ml_landmark=fl.ml_landmark,
             look_pin=sorted(fl.look_pin), ref=sorted(fl.ref), ctx=fl.ctx, kreset=fl.kreset)
    d["red"] = redundancy(root)
    return d


def sublang_texts(root):
    approx = []
    try:
        T = texts(root, True, True, approx)
    except Unsupported as e:
        return dict(unsupported=str(e))
    pick = lambda t: None if t is None else t[0]
    return dict(A=pick(T.A), NP=pick(T.NP), E=pick(T.E), approx=sorted(set(approx)))
