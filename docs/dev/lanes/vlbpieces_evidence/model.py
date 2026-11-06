#!/usr/bin/env python3
"""vlbpieces model: a tiny PCRE-subset backtracking matcher with two
lookbehind evaluators, so each can be compared against libpcre2 10.46
(probe.c, the oracle).

  range  : vlookbehind.md rev 2 §5.1 -- per branch, candidate starts farthest
           first, the WHOLE branch run forward, end-check at the cursor.
           This is the CONTROL: it must agree with libpcre2 on every cell,
           which shows the matcher itself is faithful.
  pieces : the owner's idea -- the branch flattened into a sequence of
           pieces (non-capturing groups dissolved, capture groups become
           open/close MARKERS); walked from the cursor BACKWARD, piece by
           piece. A fixed piece is reached by one jump of its width and run
           forward; a variable piece tries its lengths longest first, each
           run forward with a local end-check. Markers take the boundary the
           walk is at ("captures resolved when the loop's extent is known").

  trim   : the range loop with the branch's TRAILING fixed run hoisted out
           of it: that run is reached by one jump from the cursor and run
           forward once; the loop covers only the rest of the branch.

Usage: model.py range|pieces|trim < lines "pattern<TAB>subject"
Output: the probe's format (every non-overlapping match with groups).
Byte mode only; the subset is what the parser below accepts.
"""
import sys

WORD = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
SPACE = set(" \t\n\r\f\v")
ALL = set(chr(c) for c in range(256))


class Parser:
    def __init__(self, p):
        self.p, self.i, self.ng, self.icase = p, 0, 0, False
        if p.startswith("(?i)"):
            self.icase, self.i = True, 4

    def peek(self, k=0):
        return self.p[self.i + k] if self.i + k < len(self.p) else ""

    def alt(self):
        brs = [self.seq()]
        while self.peek() == "|":
            self.i += 1
            brs.append(self.seq())
        return brs[0] if len(brs) == 1 else ("alt", brs)

    def seq(self):
        items = []
        while self.peek() not in ("", "|", ")"):
            items.append(self.quant(self.atom()))
        return ("seq", items)

    def cls(self, chars):
        if self.icase:
            chars = set(chars) | {c.swapcase() for c in chars}
        return ("lit", frozenset(chars))

    def atom(self):
        c = self.peek()
        self.i += 1
        if c == "(":
            if self.p.startswith("?:", self.i):
                self.i += 2; n = self.alt(); kind = None
            elif self.p.startswith("?>", self.i):
                self.i += 2; n = ("atom", self.alt()); kind = 1
            elif self.p.startswith("?=", self.i):
                self.i += 2; n = ("look", False, False, True, self.alt())
            elif self.p.startswith("?!", self.i):
                self.i += 2; n = ("look", False, True, True, self.alt())
            elif self.p.startswith("?<=", self.i):
                self.i += 3; n = ("look", True, False, True, self.alt())
            elif self.p.startswith("?<!", self.i):
                self.i += 3; n = ("look", True, True, True, self.alt())
            elif self.p.startswith("?<*", self.i):
                self.i += 3; n = ("look", True, False, False, self.alt())
            else:
                self.ng += 1; g = self.ng; n = ("cap", g, self.alt())
            assert self.peek() == ")", self.p
            self.i += 1
            return n
        if c == "\\":
            d = self.peek(); self.i += 1
            if d == "b": return ("wb", False)
            if d == "B": return ("wb", True)
            if d == "w": return self.cls(WORD)
            if d == "s": return self.cls(SPACE)
            if d == "d": return self.cls(set("0123456789"))
            if d.isdigit(): return ("bref", int(d))
            return self.cls({d})
        if c == "[":
            neg = self.peek() == "^"
            if neg: self.i += 1
            s = set()
            while self.peek() != "]":
                a = self.peek(); self.i += 1
                if self.peek() == "-" and self.peek(1) != "]":
                    b = self.peek(1); self.i += 2
                    s |= {chr(x) for x in range(ord(a), ord(b) + 1)}
                else:
                    s.add(a)
            self.i += 1
            if self.icase: s |= {x.swapcase() for x in s}
            return ("lit", frozenset(ALL - s if neg else s))
        if c == ".": return ("lit", frozenset(ALL - {"\n"}))
        if c == "^": return ("bol",)
        if c == "$": return ("eol",)
        return self.cls({c})

    def quant(self, n):
        c = self.peek()
        if c not in ("?", "*", "+", "{"): return n
        if c == "{":
            j = self.p.index("}", self.i)
            body = self.p[self.i + 1:j]; self.i = j + 1
            if "," in body:
                a, b = body.split(",")
                lo, hi = int(a), (int(b) if b else None)
            else:
                lo = hi = int(body)
        else:
            self.i += 1
            lo, hi = {"?": (0, 1), "*": (0, None), "+": (1, None)}[c]
        mode = "g"
        if self.peek() == "?": self.i += 1; mode = "l"
        elif self.peek() == "+": self.i += 1; mode = "p"
        return ("rep", n, lo, hi, mode)


def width(n):
    t = n[0]
    if t == "lit": return (1, 1)
    if t in ("wb", "bol", "eol", "look", "open", "close"): return (0, 0)
    if t == "seq":
        lo = hi = 0
        for x in n[1]:
            a, b = width(x); lo += a
            hi = None if hi is None or b is None else hi + b
        return (lo, hi)
    if t == "alt":
        ws = [width(x) for x in n[1]]
        return (min(w[0] for w in ws),
                None if any(w[1] is None for w in ws) else max(w[1] for w in ws))
    if t in ("cap",): return width(n[2])
    if t == "atom": return width(n[1])
    if t == "rep":
        a, b = width(n[1])
        hi = None if (n[3] is None and b != 0) or b is None else b * (n[3] or 0)
        return (a * n[2], hi)
    raise ValueError("no width for " + t)


class M:
    def __init__(self, mode, s, ng):
        self.mode, self.s, self.ng = mode, s, ng

    def isw(self, i):
        return 0 <= i < len(self.s) and self.s[i] in WORD

    def m(self, n, i, c, k):
        s, t = self.s, n[0]
        if t == "lit":
            return k(i + 1, c) if i < len(s) and s[i] in n[1] else None
        if t == "seq":
            items = n[1]
            def go(j, pos, cc):
                if j == len(items): return k(pos, cc)
                return self.m(items[j], pos, cc, lambda p2, c2: go(j + 1, p2, c2))
            return go(0, i, c)
        if t == "alt":
            for b in n[1]:
                r = self.m(b, i, c, k)
                if r is not None: return r
            return None
        if t == "cap":
            g = n[1]
            def close(j, cc):
                cc = list(cc); cc[2 * g] = i; cc[2 * g + 1] = j
                return k(j, tuple(cc))
            return self.m(n[2], i, c, close)
        if t == "open" or t == "close":
            raise ValueError("marker outside the piece walk")
        if t == "atom":
            r = self.m(n[1], i, c, lambda j, cc: (j, cc))
            return None if r is None else k(*r)
        if t == "wb":
            at = self.isw(i - 1) != self.isw(i)
            return k(i, c) if at != n[1] else None
        if t == "bol": return k(i, c) if i == 0 else None
        if t == "eol": return k(i, c) if i == len(s) else None
        if t == "bref":
            a, b = c[2 * n[1]], c[2 * n[1] + 1]
            if a < 0: return None
            sub = s[a:b]
            return k(i + len(sub), c) if s.startswith(sub, i) else None
        if t == "rep":
            body, lo, hi, mode = n[1], n[2], n[3], n[4]
            if mode == "p":
                return self.m(("atom", ("rep", body, lo, hi, "g")), i, c, k)
            def rep(cnt, pos, cc):
                def more():
                    if hi is not None and cnt >= hi: return None
                    def nxt(j, c2):
                        if hi is None and j == pos: return k(j, c2)   # unbounded empty guard
                        return rep(cnt + 1, j, c2)
                    return self.m(body, pos, cc, nxt)
                def stop():
                    return k(pos, cc) if cnt >= lo else None
                if mode == "g":
                    r = more()
                    return r if r is not None else stop()
                r = stop()
                return r if r is not None else more()
            return rep(0, i, c)
        if t == "look":
            behind, neg, atomic, body = n[1], n[2], n[3], n[4]
            if not behind:
                r = self.m(body, i, c, lambda j, cc: cc)
                if neg: return None if r is not None else k(i, c)
                return None if r is None else k(i, r)
            brs = body[1] if body[0] == "alt" else [body]
            ev = {"range": self.range_branch, "pieces": self.piece_branch,
                  "trim": self.trim_branch}[self.mode]
            if neg:
                for b in brs:
                    if ev(b, i, c, lambda cc: cc) is not None: return None
                return k(i, c)
            if atomic:
                for b in brs:
                    r = ev(b, i, c, lambda cc: cc)
                    if r is not None: return k(i, r)
                return None
            for b in brs:
                r = ev(b, i, c, lambda cc: k(i, cc))
                if r is not None: return r
            return None
        raise ValueError(t)

    # rev 2 §5.1: candidate starts farthest first, whole branch forward
    def range_branch(self, b, cur, c, fin):
        lo, hi = width(b)
        for d in range(min(hi, cur), lo - 1, -1):
            r = self.m(b, cur - d, c, lambda j, cc: fin(cc) if j == cur else None)
            if r is not None: return r
        return None

    # the owner's piece walk
    def piece_branch(self, b, cur, c, fin):
        items = flatten(b)
        def walk(idx, e, cc):
            if idx < 0: return fin(cc)
            it = items[idx]
            if it[0] in ("open", "close"):
                cc = list(cc); cc[2 * it[1] + (1 if it[0] == "close" else 0)] = e
                return walk(idx - 1, e, tuple(cc))
            lo, hi = width(it)
            for d in range(min(hi, e), lo - 1, -1):
                r = self.m(it, e - d, cc,
                           lambda j, c2, d=d: walk(idx - 1, e - d, c2) if j == e else None)
                if r is not None: return r
            return None
        return walk(len(items) - 1, cur, c)

    # the trimmed range loop: the branch's trailing fixed run (markers
    # included) is reached by one jump and run forward ONCE; the range loop
    # then covers only the rest, with its end-check at the run's start
    def trim_branch(self, b, cur, c, fin):
        items = flatten(b)
        j = len(items)
        while j > 0 and (items[j - 1][0] in ("open", "close")
                         or width(items[j - 1])[0] == width(items[j - 1])[1]):
            j -= 1
        rest, tail = items[:j], items[j:]
        tw = sum(width(x)[0] for x in tail if x[0] not in ("open", "close"))
        if tw > cur: return None
        e = cur - tw
        lo = sum(width(x)[0] for x in rest if x[0] not in ("open", "close"))
        hi = sum(width(x)[1] for x in rest if x[0] not in ("open", "close"))
        def loop(cc):
            for d in range(min(hi, e), lo - 1, -1):
                r = self.run_items(rest, e - d, cc, lambda p, c2: fin(c2) if p == e else None)
                if r is not None: return r
            return None
        return self.run_items(tail, e, c, lambda p, cc: loop(cc) if p == cur else None)

    # a flattened item list run FORWARD; markers write the position reached
    def run_items(self, items, i, c, k):
        def go(j, pos, cc):
            if j == len(items): return k(pos, cc)
            it = items[j]
            if it[0] in ("open", "close"):
                cc = list(cc); cc[2 * it[1] + (1 if it[0] == "close" else 0)] = pos
                return go(j + 1, pos, tuple(cc))
            return self.m(it, pos, cc, lambda p2, c2: go(j + 1, p2, c2))
        return go(0, i, c)


def flatten(n):
    t = n[0]
    if t == "seq":
        out = []
        for x in n[1]: out += flatten(x)
        return out
    if t == "cap":
        return [("open", n[1])] + flatten(n[2]) + [("close", n[1])]
    return [n]


def run(mode, pat, subj):
    P = Parser(pat); root = P.alt(); ng = P.ng
    mm = M(mode, subj, ng)
    out, at, n = [], 0, len(subj)
    while at <= n:
        hit = None
        for st in range(at, n + 1):
            c0 = tuple([-1] * (2 * ng + 2))
            r = mm.m(root, st, c0, lambda j, cc, st=st: (st, j, cc))
            if r is not None: hit = r; break
        if hit is None: break
        st, en, cc = hit
        cc = list(cc); cc[0], cc[1] = st, en
        top = max(g for g in range(ng + 1) if cc[2 * g] >= 0)
        out.append("[" + ",".join("-" if cc[2 * g] < 0 else "%d-%d" % (cc[2 * g], cc[2 * g + 1])
                                  for g in range(top + 1)) + "]")
        at = en if en > st else en + 1
    return "".join(out) if out else "nomatch"


if __name__ == "__main__":
    mode = sys.argv[1]
    for line in sys.stdin:
        line = line.rstrip("\n")
        pat, subj = line.split("\t")[:2]
        print("%s\t%s\t%s" % (pat, subj, run(mode, pat, subj)))
