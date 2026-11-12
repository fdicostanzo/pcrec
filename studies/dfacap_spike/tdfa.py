"""tdfa.py -- the capspike reference construction (study code, never product).

A leftmost-first (PCRE priority) tagged DFA over a named pattern subset:

  parse()      pattern bytes -> AST (raises Unsupported(reason) outside the subset)
  TNFA         AST -> tagged NFA with priority-ordered epsilon edges, tags on
               capture open/close, ENTER/BACK loop markers for PCRE's
               empty-iteration rule, and end-assertions folded into
               CONDITIONAL accepts
  pike()       Pike-VM simulation of the TNFA (per-thread tag values): the
               semantics the TDFA must reproduce, checked separately
  TDFA         subset construction over priority-ordered thread lists, each
               thread carrying a tag -> value-class map; classes are bound to
               registers per state; transitions carry register ops
               (set-to-position / copy); final ops at accept

Subset: literals, escapes, classes (POSIX names included), `.`, concatenation,
alternation, capturing / non-capturing / named groups, ? * + {m} {m,} {m,n}
({,n}) greedy and lazy, scoped and global flags i s x, anchors ^ \\A $ \\Z \\z
(not under m), byte encoding (utf8 only when the pattern is ASCII and has no
construct that matches a non-ASCII code point).

Semantics of a tag: the position where the winning path LAST crossed it.
Group k = (tag 2k, tag 2k+1); group 0 = tags 0, 1 (unanchored search is a
lazy any-byte prefix loop before tag 0, so the match start is a tag too).
"""
import os
import sys

sys.setrecursionlimit(20000)
# Sabotage switches (the controls: each must turn cases.py red):
#   noempty  -- drop the empty-iteration rule (BACK always may loop)
#   nocopy   -- drop register copies from the TDFA's transition ops
#   noctx    -- noempty AND visited keyed by node only (the textbook Pike VM)
#   fifo     -- dedupe endpoints last-wins instead of first-wins (priority off)
SABOTAGE = set(os.environ.get("CAPSPIKE_SABOTAGE", "").split(","))


class Unsupported(Exception):
    pass


# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------
ALL = frozenset(range(256))
DIGIT = frozenset(range(48, 58))
WORD = frozenset(list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123)) + [95])
SPACE = frozenset([9, 10, 11, 12, 13, 32])
HSPACE = frozenset([9, 32, 0xa0])
VSPACE = frozenset([10, 11, 12, 13, 0x85])
POSIX = {
    b"alpha": frozenset(list(range(65, 91)) + list(range(97, 123))),
    b"digit": DIGIT,
    b"alnum": frozenset(list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123))),
    b"space": SPACE,
    b"upper": frozenset(range(65, 91)),
    b"lower": frozenset(range(97, 123)),
    b"punct": frozenset(c for c in range(33, 127) if not (48 <= c <= 57 or 65 <= c <= 90 or 97 <= c <= 122)),
    b"xdigit": frozenset(list(range(48, 58)) + list(range(65, 71)) + list(range(97, 103))),
    b"word": WORD,
    b"blank": frozenset([9, 32]),
    b"cntrl": frozenset(list(range(0, 32)) + [127]),
    b"graph": frozenset(range(33, 127)),
    b"print": frozenset(range(32, 127)),
    b"ascii": frozenset(range(0, 128)),
}


def fold(s):
    out = set(s)
    for c in s:
        if 65 <= c <= 90:
            out.add(c + 32)
        elif 97 <= c <= 122:
            out.add(c - 32)
    return frozenset(out)


class Parser:
    """Recursive descent over pattern bytes. AST nodes:
    ('set', frozenset) ('cat', [n]) ('alt', [n]) ('cap', k, n)
    ('rep', n, lo, hi|None, greedy) ('bos',) ('eos',) ('eosnl',) ('empty',)"""

    def __init__(self, pat, flags="", utf8=False):
        self.p = pat
        self.i = 0
        self.ncap = 0
        self.utf8 = utf8
        self.names = {}
        self.groups = {}
        self.dupnames = False
        self.f = {"i": "i" in flags, "s": "s" in flags, "x": "x" in flags, "m": "m" in flags}

    def peek(self, k=0):
        j = self.i + k
        return self.p[j] if j < len(self.p) else None

    def parse(self):
        n = self.alt()
        if self.i != len(self.p):
            raise Unsupported("unbalanced ) at %d" % self.i)
        return n

    def alt(self):
        arms = [self.cat()]
        while self.peek() == 0x7c:  # |
            self.i += 1
            arms.append(self.cat())
        return arms[0] if len(arms) == 1 else ("alt", arms)

    def skip_x(self):
        while self.f["x"] and self.i < len(self.p):
            c = self.p[self.i]
            if c in (32, 9, 10, 11, 12, 13):
                self.i += 1
            elif c == 0x23:  # '#'
                while self.i < len(self.p) and self.p[self.i] != 10:
                    self.i += 1
            else:
                break

    def cat(self):
        items = []
        while True:
            self.skip_x()
            c = self.peek()
            if c is None or c in (0x7c, 0x29):
                break
            atom = self.atom()
            if atom is None:
                continue
            atom = self.quant(atom)
            items.append(atom)
        if not items:
            return ("empty",)
        return items[0] if len(items) == 1 else ("cat", items)

    def quant(self, atom):
        while True:
            self.skip_x()
            c = self.peek()
            lo = hi = None
            if c == 0x3f:
                lo, hi = 0, 1; self.i += 1
            elif c == 0x2a:
                lo, hi = 0, None; self.i += 1
            elif c == 0x2b:
                lo, hi = 1, None; self.i += 1
            elif c == 0x7b:
                r = self.brace()
                if r is None:
                    return atom
                lo, hi = r
            else:
                return atom
            if atom[0] in ("bos", "eos", "eosnl", "wb", "nwb", "la", "lb"):
                raise Unsupported("quantified assertion")
            greedy = True
            if self.peek() == 0x3f:
                greedy = False; self.i += 1
            elif self.peek() == 0x2b:
                raise Unsupported("possessive quantifier")
            if hi is not None and hi < lo:
                raise Unsupported("bad range")
            atom = ("rep", atom, lo, hi, greedy)

    def brace(self):
        j = self.i + 1
        p = self.p
        def num(j):
            k = j
            while k < len(p) and 48 <= p[k] <= 57:
                k += 1
            return (int(p[j:k]) if k > j else None), k
        a, j = num(j)
        if j < len(p) and p[j] == 0x7d:
            if a is None:
                return None
            self.i = j + 1
            return a, a
        if j < len(p) and p[j] == 0x2c:
            b, k = num(j + 1)
            if k < len(p) and p[k] == 0x7d and (a is not None or b is not None):
                self.i = k + 1
                return (a or 0), b
        return None

    def cls(self, s):
        if self.f["i"]:
            s = fold(s)
        return ("set", frozenset(s))

    def lit(self, c):
        if self.utf8 and c >= 0x80:
            raise Unsupported("utf8 non-ASCII literal")
        return self.cls({c})

    def atom(self):
        c = self.p[self.i]
        if c == 0x28:
            return self.group()
        if c == 0x5b:
            return self.bracket()
        if c == 0x2e:
            self.i += 1
            if self.utf8:
                raise Unsupported("utf8 dot")
            return ("set", ALL if self.f["s"] else ALL - {10})
        if c == 0x5e:
            self.i += 1
            if self.f["m"]:
                raise Unsupported("multiline ^")
            return ("bos",)
        if c == 0x24:
            self.i += 1
            if self.f["m"]:
                raise Unsupported("multiline $")
            return ("eosnl",)
        if c == 0x5c:
            return self.escape()
        if c in (0x2a, 0x2b, 0x3f):
            raise Unsupported("quantifier without atom")
        self.i += 1
        return self.lit(c)

    def escape(self, in_class=False):
        p = self.p
        self.i += 1
        if self.i >= len(p):
            raise Unsupported("trailing backslash")
        c = p[self.i]
        self.i += 1
        simple = {0x6e: 10, 0x74: 9, 0x72: 13, 0x66: 12, 0x65: 27, 0x61: 7}
        if c in simple:
            return self.lit(simple[c]) if not in_class else simple[c]
        neg = {0x64: (DIGIT, False), 0x44: (DIGIT, True), 0x77: (WORD, False), 0x57: (WORD, True),
               0x73: (SPACE, False), 0x53: (SPACE, True), 0x68: (HSPACE, False), 0x48: (HSPACE, True),
               0x76: (VSPACE, False), 0x56: (VSPACE, True)}
        if c in neg:
            s, n = neg[c]
            if self.utf8 and (n or c in (0x68, 0x76)):
                raise Unsupported("utf8 negated/h/v class escape")
            s = (ALL - s) if n else s
            return ("set", s) if not in_class else s
        if c == 0x4e and not in_class:
            if self.utf8:
                raise Unsupported("utf8 \\N")
            return ("set", ALL - {10})
        if c == 0x78:  # \x
            if self.i < len(p) and p[self.i] == 0x7b:
                j = p.index(b"}", self.i)
                v = int(p[self.i + 1:j], 16)
                self.i = j + 1
            else:
                k = self.i
                while k < len(p) and k < self.i + 2 and chr(p[k]) in "0123456789abcdefABCDEF":
                    k += 1
                v = int(p[self.i:k], 16) if k > self.i else 0
                self.i = k
            if v > 255 or (self.utf8 and v >= 0x80):
                raise Unsupported("code point > 0x7f")
            return self.lit(v) if not in_class else v
        if c == 0x30:  # \0 octal
            k = self.i
            while k < len(p) and k < self.i + 2 and 48 <= p[k] <= 55:
                k += 1
            v = int(p[self.i - 1:k], 8)
            self.i = k
            return self.lit(v) if not in_class else v
        if c == 0x63:  # \cX
            v = p[self.i] ^ 0x40 if p[self.i] < 97 else (p[self.i] - 32) ^ 0x40
            self.i += 1
            return self.lit(v) if not in_class else v
        if not in_class:
            if c == 0x41:
                return ("bos",)
            if c == 0x7a:
                return ("eos",)
            if c == 0x5a:
                return ("eosnl",)
            if c == 0x51:  # \Q..\E
                j = p.find(b"\\E", self.i)
                j = len(p) if j < 0 else j
                lits = [self.lit(b) for b in p[self.i:j]]
                self.i = min(len(p), j + 2)
                if not lits:
                    return None
                return lits[0] if len(lits) == 1 else ("cat", lits)
            if c == 0x45:
                return None
            if c == 0x67 and self.i < len(p) and p[self.i] in (0x3c, 0x27):  # \g<n> \g'n' calls
                close = 0x3e if p[self.i] == 0x3c else 0x27
                j = p.index(bytes([close]), self.i + 1)
                ref = p[self.i + 1:j]
                self.i = j + 1
                try:
                    return ("call", self.relref(ref.decode()))
                except ValueError:
                    return ("call", ref)
            if c == 0x62:
                return ("wb",)
            if c == 0x42:
                return ("nwb",)
        else:
            if c == 0x62:
                return 8
        if (48 <= c <= 57) or (65 <= c <= 90) or (97 <= c <= 122):
            raise Unsupported("escape \\%s" % chr(c))
        return self.lit(c) if not in_class else c

    def bracket(self):
        p = self.p
        self.i += 1
        neg = False
        if self.peek() == 0x5e:
            neg = True; self.i += 1
        s = set()
        first = True
        while True:
            if self.i >= len(p):
                raise Unsupported("unterminated class")
            c = p[self.i]
            if c == 0x5d and not first:
                self.i += 1
                break
            first = False
            if c == 0x5b and self.peek(1) == 0x3a:
                j = p.find(b":]", self.i + 2)
                if j < 0:
                    raise Unsupported("bad posix")
                name = p[self.i + 2:j]
                pn = False
                if name.startswith(b"^"):
                    pn, name = True, name[1:]
                if name not in POSIX:
                    raise Unsupported("posix class %r" % name)
                ps = POSIX[name]
                if pn:
                    if self.utf8:
                        raise Unsupported("utf8 negated posix")
                    ps = ALL - ps
                s |= ps
                self.i = j + 2
                continue
            if c == 0x5c:
                v = self.escape(in_class=True)
            else:
                self.i += 1
                v = c
                if self.utf8 and v >= 0x80:
                    raise Unsupported("utf8 non-ASCII in class")
            if isinstance(v, frozenset):
                s |= v
                continue
            if v is None:
                continue
            if self.peek() == 0x2d and self.peek(1) not in (0x5d, None):
                self.i += 1
                if p[self.i] == 0x5c:
                    hi = self.escape(in_class=True)
                    if isinstance(hi, frozenset):
                        raise Unsupported("class range to class")
                else:
                    hi = p[self.i]; self.i += 1
                if hi < v:
                    raise Unsupported("bad class range")
                s |= set(range(v, hi + 1))
            else:
                s.add(v)
        if self.f["i"]:
            s = set(fold(s))
        if neg:
            if self.utf8:
                raise Unsupported("utf8 negated class")
            s = ALL - s
        return ("set", frozenset(s))

    def group(self):
        p = self.p
        self.i += 1
        save = dict(self.f)
        cap = None
        if self.peek() == 0x2a:
            raise Unsupported("verb (*...)")
        if self.peek() == 0x3f:
            self.i += 1
            c = self.peek()
            if c in (0x3d, 0x21) or (c == 0x3c and self.peek(1) in (0x3d, 0x21)):
                behind = c == 0x3c
                if behind:
                    self.i += 1
                neg = p[self.i] == 0x21
                self.i += 1
                ncap0 = self.ncap
                body = self.alt()
                if self.peek() != 0x29:
                    raise Unsupported("missing )")
                self.i += 1
                self.f = save
                if self.ncap != ncap0:
                    raise Unsupported("capture inside lookaround")
                arms = body[1] if body[0] == "alt" else [body]
                if not all(x[0] == "set" for x in arms):
                    raise Unsupported("lookaround body wider than one character")
                u = frozenset().union(*[x[1] for x in arms])
                return ("lb" if behind else "la", u, neg)
            if c == 0x3a:
                self.i += 1
            elif (c is not None and 48 <= c <= 57) or (c in (0x2b, 0x2d) and self.peek(1) is not None
                                                      and 48 <= self.peek(1) <= 57):
                j = p.index(b")", self.i)
                ref = p[self.i:j].decode()
                self.i = j + 1
                return ("call", self.relref(ref))
            elif c == 0x26 or (c == 0x50 and self.peek(1) == 0x3e):  # (?&name) (?P>name)
                self.i += 1 if c == 0x26 else 2
                j = p.index(b")", self.i)
                name = p[self.i:j]
                self.i = j + 1
                return ("call", name)
            elif c == 0x52:
                raise Unsupported("recursion (?R)")
            elif c == 0x23:  # comment
                j = p.index(b")", self.i)
                self.i = j + 1
                return None
            elif c in (0x3c, 0x27) and self.peek(1) not in (0x3d, 0x21) or (c == 0x50 and self.peek(1) == 0x3c):
                if c == 0x50:
                    self.i += 1
                close = 0x3e if p[self.i] == 0x3c else 0x27
                j = p.index(bytes([close]), self.i + 1)
                name = p[self.i + 1:j]
                self.i = j + 1
                self.ncap += 1
                cap = self.ncap
                if name in self.names:
                    self.dupnames = True
                self.names.setdefault(name, cap)
            else:
                # flag setting (?imsx-imsx) or (?flags:...)
                on = True
                j = self.i
                newf = dict(self.f)
                while j < len(p) and p[j] not in (0x29, 0x3a):
                    ch = chr(p[j])
                    if ch == "-":
                        on = False
                    elif ch == "^":
                        newf = {k: False for k in newf}
                    elif ch in "isxm":
                        newf[ch] = on
                    elif ch == "J":
                        pass  # duplicate names allowed: numbering only
                    else:
                        raise Unsupported("group (?%s" % chr(p[self.i]))
                    j += 1
                if j >= len(p):
                    raise Unsupported("bad group")
                if p[j] == 0x29:  # (?i) applies to the rest of the enclosing group
                    self.i = j + 1
                    self.f.update(newf)
                    return None
                self.i = j + 1
                self.f.update(newf)
        else:
            self.ncap += 1
            cap = self.ncap
        body = self.alt()
        if self.peek() != 0x29:
            raise Unsupported("missing )")
        self.i += 1
        self.f = save
        if cap:
            self.groups[cap] = body
            return ("cap", cap, body)
        return body

    def relref(self, ref):
        if ref[0] in "+-":
            n = int(ref[1:])
            return self.ncap + n if ref[0] == "+" else self.ncap - n + 1
        return int(ref)

    def resolve(self, a, stack=()):
        """Splice subroutine calls: the called group's body with its capture
        nodes stripped (PCRE2: captures set inside a call revert when it
        returns). A call reaching a group already being expanded is recursion."""
        k = a[0]
        if k == "call":
            ref = a[1]
            num = self.names.get(ref) if isinstance(ref, bytes) else ref
            if num is None or num not in self.groups:
                raise Unsupported("unresolved call")
            if num in stack:
                raise Unsupported("recursive call")
            return self.resolve(strip_caps(self.groups[num]), stack + (num,))
        if k in ("cat", "alt"):
            return (k, [self.resolve(x, stack) for x in a[1]])
        if k == "cap":
            return ("cap", a[1], self.resolve(a[2], stack + (a[1],)))
        if k == "rep":
            return ("rep", self.resolve(a[1], stack)) + a[2:]
        return a


def strip_caps(a):
    k = a[0]
    if k == "cap":
        return strip_caps(a[2])
    if k in ("cat", "alt"):
        return (k, [strip_caps(x) for x in a[1]])
    if k == "rep":
        return ("rep", strip_caps(a[1])) + a[2:]
    return a


def parse(pat, flags="", utf8=False):
    pr = Parser(pat, flags, utf8)
    try:
        ast = pr.parse()
    except (ValueError, IndexError) as e:
        raise Unsupported("spike parser: %s" % e)
    ast = pr.resolve(ast)
    return ast, pr.ncap


# --------------------------------------------------------------------------
# Tagged NFA
# --------------------------------------------------------------------------
CHAR, SPLIT, TAG, ENTER, BACK, ASSERT, MATCH = range(7)


class TNFA:
    """Nodes are lists: [kind, ...].
    CHAR   [CHAR, set, out]
    SPLIT  [SPLIT, [outs in priority order]]
    TAG    [TAG, t, out]
    ENTER  [ENTER, loop, out]            an iteration of `loop` starts here
    BACK   [BACK, loop, enter, exit, greedy]  end of an iteration
    ASSERT [ASSERT, kind, out, ...]      kind: 'bos' | 'eos' | 'eosnl' | 'wb' | 'nwb'
                                         | 'la' (+ set, negated) | 'lb' (+ prevsets index, negated)
    MATCH  [MATCH]
    """

    def __init__(self, ast, ncap, anchored=False, opts=None):
        self.n = []
        self.ncap = ncap
        self.ntags = 2 * (ncap + 1)
        self.nloops = 0
        self.opts = opts or {}
        self.prevsets = [WORD]
        self.match = self.add([MATCH])
        body = self.comp(ast, self.add([TAG, 1, self.match]))
        main = self.add([TAG, 0, body])
        if anchored:
            self.start = main
        else:
            pre = self.add([SPLIT, None])
            anyc = self.add([CHAR, ALL, pre])
            self.n[pre][1] = [main, anyc]  # lazy: try the match first
            self.start = pre
        self.check_end_asserts()
        self.liveness()

    def add(self, node):
        self.n.append(node)
        return len(self.n) - 1

    def comp(self, a, nxt):
        k = a[0]
        if k == "set":
            return self.add([CHAR, a[1], nxt])
        if k == "empty":
            return nxt
        if k == "cat":
            for x in reversed(a[1]):
                nxt = self.comp(x, nxt)
            return nxt
        if k == "alt":
            return self.add([SPLIT, [self.comp(x, nxt) for x in a[1]]])
        if k == "cap":
            close = self.add([TAG, 2 * a[1] + 1, nxt])
            return self.add([TAG, 2 * a[1], self.comp(a[2], close)])
        if k in ("bos", "eos", "eosnl", "wb", "nwb"):
            return self.add([ASSERT, k, nxt])
        if k == "la":
            return self.add([ASSERT, "la", nxt, a[1], a[2]])
        if k == "lb":
            if a[1] not in self.prevsets:
                self.prevsets.append(a[1])
            return self.add([ASSERT, "lb", nxt, self.prevsets.index(a[1]), a[2]])
        if k == "rep":
            _, sub, lo, hi, greedy = a
            if hi is None:
                # lo-1 fixed copies, then a `+` loop (PCRE2: X{n,} = X{n-1}X+);
                # lo == 0: a `*` (optional entry to the + loop)
                tail = self.loop(sub, nxt, greedy, optional=(lo == 0))
                for _ in range(max(lo - 1, 0)):
                    tail = self.comp(sub, tail)
                return tail
            # (hi - lo) nested optionals (X(X(X)?)?)?, then lo fixed copies
            tail = nxt
            for _ in range(hi - lo):
                body = self.comp(sub, tail)
                tail = self.add([SPLIT, [body, nxt] if greedy else [nxt, body]])
            for _ in range(lo):
                tail = self.comp(sub, tail)
            return tail
        raise AssertionError(k)

    def loop(self, sub, nxt, greedy, optional):
        L = self.nloops
        self.nloops += 1
        back = self.add([BACK, L, None, nxt, greedy])
        enter = self.add([ENTER, L, None])
        self.n[enter][2] = self.comp(sub, back)
        self.n[back][2] = enter
        if not optional:
            return enter
        return self.add([SPLIT, [enter, nxt] if greedy else [nxt, enter]])

    def succ(self, i):
        nd = self.n[i]
        k = nd[0]
        if k == CHAR or k == TAG or k == ENTER or k == ASSERT:
            return [nd[2]]
        if k == SPLIT:
            return nd[1]
        if k == BACK:
            return [nd[2], nd[3]]
        return []

    def check_end_asserts(self):
        # after an end assertion only epsilon paths may follow (else: out of subset)
        for i, nd in enumerate(self.n):
            if nd[0] == ASSERT and nd[1] in ("eos", "eosnl"):
                seen, st = set(), [nd[2]]
                while st:
                    j = st.pop()
                    if j in seen:
                        continue
                    seen.add(j)
                    if self.n[j][0] == CHAR:
                        raise Unsupported("consuming after end assertion")
                    st.extend(self.succ(j))

    def liveness(self):
        T = self.ntags
        full = frozenset(range(T))
        live = [frozenset() for _ in self.n]
        live[self.match] = full
        changed = True
        while changed:
            changed = False
            for i, nd in enumerate(self.n):
                if nd[0] == MATCH:
                    continue
                s = set()
                for j in self.succ(i):
                    s |= live[j]
                if nd[0] == TAG:
                    s.discard(nd[1])
                s = frozenset(s)
                if s != live[i]:
                    live[i] = s
                    changed = True
        self.live = live
        # dead tags can be stripped from MATCH-conditional endpoints too: all live
        self.live_match = full


# --------------------------------------------------------------------------
# The closure (shared by the Pike VM and the TDFA)
# --------------------------------------------------------------------------
UNCOND = None  # accept condition: None = unconditional, 'z' = EOF next, 'Z' = EOF or "\n" EOF next


def cond_and(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return "z" if "z" in (a, b) else "Z"


def sigof(nfa, b):
    """What the closure may ask about the PREVIOUS byte: membership in each of
    nfa.prevsets (index 0 is \\w). None = start of subject."""
    return None if b is None else tuple(b in s for s in nfa.prevsets)


def closure(nfa, seeds, sig, nxt):
    """seeds: ordered ('node', i, payload, ctx, cond) or ('direct', key, payload).
    sig: the previous byte's signature (None at the subject start). nxt: the
    NEXT input -- None (unknown: the normal closure), a byte, or 'EOF' (the
    delayed closure of a pending assertion, run once the next input is known).
    Returns ordered (key, payload, written): key is a CHAR node id, ('M', cond),
    or ('A', node, ctx, sig, cond) -- an assertion on the next byte, pending.
    Stops at the first unconditional accept (lower priorities are pruned).
    Priority DFS; visited keyed by (node, loops-entered-in-this-closure, cond):
    the empty-iteration rule (an iteration that consumed nothing ends its
    loop, PCRE's KETRMAX check) makes that context part of the node's future."""
    N = nfa.n
    out = []
    claimed = set()
    visited = set()
    for sd in seeds:
        if sd[0] == "direct":
            _, x, payload = sd
            if x not in claimed:
                claimed.add(x)
                out.append((x, payload, frozenset()))
                if x == ("M", None):
                    return out
            continue
        _, x, payload, ctx0, cond0 = sd
        stack = [(x, ctx0, frozenset(), cond0)]
        while stack:
            i, ctx, wr, cond = stack.pop()
            vk = (i, cond) if "noctx" in SABOTAGE else (i, ctx, cond)
            if vk in visited:
                continue
            visited.add(vk)
            nd = N[i]
            k = nd[0]
            if k == CHAR:
                if cond is not None:
                    continue
                if "fifo" in SABOTAGE and i in claimed:
                    out[:] = [o for o in out if o[0] != i]
                    claimed.discard(i)
                if i not in claimed:
                    claimed.add(i)
                    out.append((i, payload, wr))
            elif k == MATCH:
                key = ("M", cond)
                if key not in claimed:
                    claimed.add(key)
                    out.append((key, payload, wr))
                    if cond is None:
                        return out
            elif k == TAG:
                stack.append((nd[2], ctx, wr | {nd[1]}, cond))
            elif k == SPLIT:
                for j in reversed(nd[1]):
                    stack.append((j, ctx, wr, cond))
            elif k == ENTER:
                stack.append((nd[2], ctx | {nd[1]}, wr, cond))
            elif k == BACK:
                L, enter, ex, greedy = nd[1], nd[2], nd[3], nd[4]
                if L in ctx and "noempty" not in SABOTAGE:  # this iteration matched empty: leave the loop
                    stack.append((ex, ctx, wr, cond))
                elif greedy:
                    stack.append((ex, ctx, wr, cond))
                    stack.append((enter, ctx, wr, cond))
                else:
                    stack.append((enter, ctx, wr, cond))
                    stack.append((ex, ctx, wr, cond))
            elif k == ASSERT:
                a = nd[1]
                ok = None  # True / False / 'pending' / a new cond
                if a == "bos":
                    ok = sig is None
                elif a == "lb":
                    ok = (sig is not None and sig[nd[3]]) != nd[4]
                elif a in ("eos", "eosnl"):
                    if nxt is None:
                        stack.append((nd[2], ctx, wr, cond_and(cond, "z" if a == "eos" else "Z")))
                        continue
                    if nxt == "EOF":
                        ok = True
                    elif a == "eosnl" and nxt == 10:
                        stack.append((nd[2], ctx, wr, cond_and(cond, "z")))
                        continue
                    else:
                        ok = False
                else:  # wb, nwb, la: need the next byte
                    if nxt is None:
                        key = ("A", i, ctx, sig, cond)
                        if key not in claimed:
                            claimed.add(key)
                            out.append((key, payload, wr))
                        continue
                    nw = nxt != "EOF" and nxt in WORD
                    if a in ("wb", "nwb"):
                        pw = sig is not None and sig[0]
                        ok = (pw != nw) == (a == "wb")
                    else:  # la
                        ok = (nxt != "EOF" and nxt in nd[3]) != nd[4]
                if ok:
                    stack.append((nd[2], ctx, wr, cond))
    return out


def delayed(nfa, key, payload, nxt):
    """Resume a pending assertion thread now that the next input is known."""
    _, node, ctx, sig, cond = key
    return closure(nfa, [("node", node, payload, ctx, cond)], sig, nxt)


# --------------------------------------------------------------------------
# Pike VM over the TNFA (reference semantics; per-thread tag dicts)
# --------------------------------------------------------------------------
def result_from_tags(nfa, tags):
    g = []
    for k in range(nfa.ncap + 1):
        s, e = tags.get(2 * k, -1), tags.get(2 * k + 1, -1)
        g.append(None if s < 0 or e < 0 else (s, e))
    return g


def _write(tags, wr, v):
    if not wr:
        return tags
    tags = dict(tags)
    for t in wr:
        tags[t] = v
    return tags


def pike(nfa, subj):
    def accept(th):
        for key, tags in th:
            if key == ("M", None):
                return tags
        return None

    res = closure(nfa, [("node", nfa.start, {}, frozenset(), None)], None, None)
    threads = [(k, _write(t, wr, 0)) for k, t, wr in res]
    best = accept(threads)
    for i, b in enumerate(subj):
        items = []
        for key, tags in threads:
            if isinstance(key, int):
                nd = nfa.n[key]
                if b in nd[1]:
                    items.append(("node", nd[2], tags, frozenset(), None))
            elif key[0] == "M":
                if key[1] == "Z" and b == 10:
                    items.append(("direct", ("M", "z"), tags))
            else:  # pending assertion: resume at position i with next = b
                for k2, t2, wr in delayed(nfa, key, tags, b):
                    t2 = _write(t2, wr, i)
                    if isinstance(k2, int):
                        if b in nfa.n[k2][1]:
                            items.append(("node", nfa.n[k2][2], t2, frozenset(), None))
                    else:
                        items.append(("direct", k2, t2))
        if not items:
            threads = []
            break
        res = closure(nfa, items, sigof(nfa, b), None)
        threads = [(k, _write(t, wr, i + 1)) for k, t, wr in res]
        a = accept(threads)
        if a is not None:
            best = a
    n = len(subj)
    for key, tags in threads:  # EOF: first accepting thread in priority order
        if isinstance(key, int):
            continue
        if key[0] == "M":
            best = tags
            break
        hit = [(k2, _write(t2, wr, n)) for k2, t2, wr in delayed(nfa, key, tags, "EOF") if not isinstance(k2, int)]
        if hit:
            best = hit[0][1]
            break
    return None if best is None else result_from_tags(nfa, best)


# --------------------------------------------------------------------------
# Tagged DFA
# --------------------------------------------------------------------------
class TooBig(Exception):
    pass


def byte_classes(nfa):
    """Partition 0..255 by every byte predicate the closure or a step asks:
    CHAR sets, \\n (for $), \\w, lookahead and lookbehind sets."""
    sets = [nd[1] for nd in nfa.n if nd[0] == CHAR]
    sets += list(nfa.prevsets[1:])
    if any(nd[0] == ASSERT and nd[1] in ("wb", "nwb") for nd in nfa.n):
        sets.append(WORD)
    for nd in nfa.n:
        if nd[0] == ASSERT:
            if nd[1] == "eosnl":
                sets.append(frozenset([10]))
            elif nd[1] == "la":
                sets.append(nd[3])
    sig = {}
    for b in range(256):
        key = tuple(b in s for s in sets)
        sig.setdefault(key, []).append(b)
    classes = list(sig.values())
    cmap = [0] * 256
    for ci, bs in enumerate(classes):
        for b in bs:
            cmap[b] = ci
    return classes, cmap


class TDFA:
    """States are (keys, classvecs): keys = ordered thread endpoints, classvecs
    = per thread, per LIVE tag (ascending tag order), a value class: 'U'
    (unset, a compile-time constant) or an int (canonical, numbered by first
    appearance). Each state binds its classes to registers (regmap). A
    transition = (dest, ops) with ops a parallel assignment {dst: src}, src
    'P' (the current position), 'Q' (the position before this byte: tags a
    resumed pending assertion crossed) or a register. tagged=False builds
    the untagged DFA over the same NFA (same thread lists, no tag identity)."""

    def __init__(self, nfa, tagged=True, max_states=4000):
        self.nfa = nfa
        self.tagged = tagged
        self.classes, self.cmap = byte_classes(nfa)
        self.states = []
        self.index = {}
        self.trans = {}  # (state, symbol class) -> (dest, ops)
        self.feeds = {}  # (state, symbol class) -> per dest class: ('P',) | ('Q',) | ('c', source class)
        self.eofs = {}
        self.max_states = max_states
        self.nregs = 0
        seeds = [("node", nfa.start, {t: "U" for t in range(nfa.ntags)}, frozenset(), None)]
        res = closure(nfa, seeds, None, None)
        self.init, self.init_ops = self.intern(res, [])
        self.build()

    def livetags(self, key):
        if isinstance(key, int):
            return sorted(self.nfa.live[key])
        if key[0] == "M":
            return range(self.nfa.ntags)
        return sorted(self.nfa.live[key[1]])

    def intern(self, res, srcmap):
        """res: closure output (key, vals, written) with vals {tag: 'U' | ('r', reg)}.
        Returns (state id, ops)."""
        keys = []
        vecs = []
        canon = {}
        srcs = []  # class id -> source value ('P' or ('r', reg))
        for key, vals, wr in res:
            keys.append(key)
            vec = []
            if self.tagged:
                for t in self.livetags(key):
                    v = "P" if t in wr else vals[t]
                    if v == "U":
                        vec.append("U")
                        continue
                    if v not in canon:
                        canon[v] = len(srcs)
                        srcs.append(v)
                    vec.append(canon[v])
            vecs.append(tuple(vec))
        sk = (tuple(keys), tuple(vecs))
        sid = self.index.get(sk)
        if sid is None:
            if len(self.states) >= self.max_states:
                raise TooBig()
            # bind classes to registers: keep an inherited register when free,
            # else the lowest free register
            regmap = [None] * len(srcs)
            used = set()
            for c, v in enumerate(srcs):
                if v not in ("P", "Q") and v[1] not in used:
                    regmap[c] = v[1]
                    used.add(v[1])
            for c, v in enumerate(srcs):
                if regmap[c] is None:
                    r = 0
                    while r in used:
                        r += 1
                    regmap[c] = r
                    used.add(r)
            self.nregs = max([self.nregs] + [r + 1 for r in regmap])
            sid = len(self.states)
            self.states.append((sk, regmap))
            self.index[sk] = sid
        regmap = self.states[sid][1]
        inv = {r: c for c, r in enumerate(srcmap)} if srcmap else {}
        self.last_feeds = [(v,) if v in ("P", "Q") else ("c", inv[v[1]]) for v in srcs]
        ops = {}
        for c, v in enumerate(srcs):
            dst = regmap[c]
            src = v if v in ("P", "Q") else v[1]
            if src != dst and not ("nocopy" in SABOTAGE and src not in ("P", "Q")):
                ops[dst] = src
        return sid, ops

    def thread_vals(self, sid, ti):
        (keys, vecs), regmap = self.states[sid]
        key = keys[ti]
        vals = {}
        if self.tagged:
            for t, c in zip(self.livetags(key), vecs[ti]):
                vals[t] = "U" if c == "U" else ("r", regmap[c])
        return vals

    def step(self, sid, sym):
        k = (sid, sym)
        if k in self.trans:
            return self.trans[k]
        (keys, vecs), regmap = self.states[sid]
        b = self.classes[sym][0]
        items = []
        for ti, key in enumerate(keys):
            vals = self.thread_vals(sid, ti) if self.tagged else {}
            if isinstance(key, int):
                nd = self.nfa.n[key]
                if b in nd[1]:
                    items.append(("node", nd[2], vals, frozenset(), None))
            elif key[0] == "M":
                if key[1] == "Z" and b == 10:
                    items.append(("direct", ("M", "z"), vals))
            else:
                for k2, v2, wr in delayed(self.nfa, key, vals, b):
                    v2 = _write(v2, wr, "Q")
                    if isinstance(k2, int):
                        if b in self.nfa.n[k2][1]:
                            items.append(("node", self.nfa.n[k2][2], v2, frozenset(), None))
                    else:
                        items.append(("direct", k2, v2))
        res = closure(self.nfa, items, sigof(self.nfa, b), None)
        r = self.intern(res, regmap)
        self.trans[k] = r
        self.feeds[k] = self.last_feeds
        return r

    def eof(self, sid):
        """Final ops at end of input: (vals) of the first thread that accepts."""
        if sid in self.eofs:
            return self.eofs[sid]
        keys = self.states[sid][0][0]
        r = None
        for ti, key in enumerate(keys):
            if isinstance(key, int):
                continue
            vals = self.thread_vals(sid, ti)
            if key[0] == "M":
                r = vals
                break
            hit = [_write(v2, wr, "P") for k2, v2, wr in delayed(self.nfa, key, vals, "EOF")
                   if not isinstance(k2, int)]
            if hit:
                r = hit[0]
                break
        self.eofs[sid] = r
        return r

    def build(self):
        todo = [self.init]
        seen = {self.init}
        while todo:
            s = todo.pop()
            for sym in range(len(self.classes)):
                d, _ = self.step(s, sym)
                if d not in seen:
                    seen.add(d)
                    todo.append(d)

    # ---- running -------------------------------------------------------
    def out_of(self, sid, ti, regs):
        (keys, vecs), regmap = self.states[sid]
        tags = {}
        for t, c in zip(self.livetags(keys[ti]), vecs[ti]):
            tags[t] = -1 if c == "U" else regs[regmap[c]]
        return result_from_tags(self.nfa, tags)

    def run(self, subj):
        regs = [-1] * max(self.nregs, 1)

        def apply(ops, pos):
            old = list(regs)
            for d, s in ops.items():
                regs[d] = pos if s == "P" else pos - 1 if s == "Q" else old[s]

        def uncond(sid):
            keys = self.states[sid][0][0]
            if keys and keys[-1] == ("M", None):
                return len(keys) - 1
            return None

        s = self.init
        apply(self.init_ops, 0)
        best = None
        a = uncond(s)
        if a is not None:
            best = self.out_of(s, a, regs)
        for i, b in enumerate(subj):
            s, ops = self.step(s, self.cmap[b])
            if not self.states[s][0][0]:
                return best
            apply(ops, i + 1)
            a = uncond(s)
            if a is not None:
                best = self.out_of(s, a, regs)
        vals = self.eof(s)
        if vals is not None:
            n = len(subj)
            tags = {t: (-1 if v == "U" else n if v == "P" else regs[v[1]]) for t, v in vals.items()}
            return result_from_tags(self.nfa, tags)
        return best

    # ---- costs ---------------------------------------------------------
    def stats(self):
        ntr = sets = copies = 0
        copy_tr = 0
        maxops = 0
        cyc = 0
        for (s, sym), (d, ops) in self.trans.items():
            if not self.states[d][0][0]:
                continue
            ntr += 1
            ns = sum(1 for v in ops.values() if v in ("P", "Q"))
            nc = len(ops) - ns
            sets += ns
            copies += nc
            copy_tr += nc > 0
            maxops = max(maxops, len(ops))
            # a copy whose source is also a destination needs a temporary in C
            if any(v not in ("P", "Q") and v in ops for v in ops.values()):
                cyc += 1
        live_states = sum(1 for st in self.states if st[0][0])
        return dict(states=live_states, regs=self.nregs, trans=ntr, sets=sets, copies=copies,
                    copy_trans=copy_tr, maxops=maxops, tmp_trans=cyc,
                    init_ops=len(self.init_ops), classes=len(self.classes))


def analyze(dfa):
    """Allocation-independent facts about the register program.
    copyfree: is there ANY class->register assignment under which no
      transition needs a copy?  Union every dest class with the source class
      that feeds it; copy-free iff no union set holds two classes of one state.
    conflicts: the number of states with such a clash (a lower bound on the
      states that need copies on some incoming transition).
    fixed: classes whose value is a compile-time constant offset from the
      current position (pos - k on every path) or from the match start
      (anchored machines: start + k), so need no register at all."""
    states = dfa.states
    ncls = [len(st[1]) for st in states]
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for (s, sym), (d, ops) in dfa.trans.items():
        for c, f in enumerate(dfa.feeds[(s, sym)]):
            if f[0] == "c":
                parent[find((d, c))] = find((s, f[1]))
    conflicts = 0
    for sid, n in enumerate(ncls):
        roots = [find((sid, c)) for c in range(n)]
        if len(set(roots)) != len(roots):
            conflicts += 1
    # depth of each state from the start (pos - start), if unique
    TOP = "TOP"
    depth = {dfa.init: 0}
    changed = True
    while changed:
        changed = False
        for (s, sym), (d, ops) in dfa.trans.items():
            if s not in depth or not states[d][0][0]:
                continue
            nd = TOP if depth[s] == TOP else depth[s] + 1
            if d not in depth:
                depth[d] = nd; changed = True
            elif depth[d] != TOP and depth[d] != nd:
                depth[d] = TOP; changed = True
    # value lattices per (state, class): offp (value = pos - k), offs (value = start + k)
    offp, offs = {}, {}
    for c in range(ncls[dfa.init]):
        offp[(dfa.init, c)] = 0
        offs[(dfa.init, c)] = 0

    def meet(tab, key, v):
        if key not in tab:
            tab[key] = v
            return True
        if tab[key] != TOP and tab[key] != v:
            tab[key] = TOP
            return True
        return False
    changed = True
    while changed:
        changed = False
        for (s, sym), (d, ops) in dfa.trans.items():
            if not states[d][0][0]:
                continue
            for c, f in enumerate(dfa.feeds[(s, sym)]):
                if f[0] in ("P", "Q"):
                    q = 1 if f[0] == "Q" else 0
                    vp = q
                    vs = depth.get(d, TOP)
                    vs = TOP if vs == TOP else vs - q
                else:
                    src = (s, f[1])
                    if src not in offp:
                        continue
                    vp = TOP if offp[src] == TOP else offp[src] + 1
                    vs = offs[src]
                changed |= meet(offp, (d, c), vp)
                changed |= meet(offs, (d, c), vs)
    live = [sid for sid in range(len(states)) if states[sid][0][0]]
    isfixed = lambda k: offp.get(k, TOP) != TOP or offs.get(k, TOP) != TOP
    # copy-freedom once fixed classes need no register (a non-fixed class fed
    # from a fixed one is a set "r = pos - k" / "r = start + k", not a copy)
    parent = {}
    for (s, sym), (d, ops) in dfa.trans.items():
        for c, f in enumerate(dfa.feeds[(s, sym)]):
            if f[0] == "c" and not isfixed((d, c)) and not isfixed((s, f[1])):
                parent[find((d, c))] = find((s, f[1]))
    conflicts_nf = 0
    for sid in live:
        roots = [find((sid, c)) for c in range(ncls[sid]) if not isfixed((sid, c))]
        if len(set(roots)) != len(roots):
            conflicts_nf += 1
    fixed = sum(1 for sid in live for c in range(ncls[sid]) if isfixed((sid, c)))
    total = sum(ncls[sid] for sid in live)
    need = max([0] + [sum(1 for c in range(ncls[sid]) if not isfixed((sid, c))) for sid in live])
    return dict(copyfree=conflicts == 0, conflicts=conflicts, copyfree_nf=conflicts_nf == 0,
                conflicts_nf=conflicts_nf, fixed=fixed, classes=total,
                allfixed=(fixed >= total), regs_after_fixed=need)


def compile_pattern(pat, flags="", utf8=False, anchored=False):
    ast, ncap = parse(pat, flags, utf8)
    return TNFA(ast, ncap, anchored=anchored)
