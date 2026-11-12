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
            if atom[0] in ("bos", "eos", "eosnl"):
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
            if c == 0x3a:
                self.i += 1
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
                    raise Unsupported("duplicate name")
                self.names[name] = cap
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
        return ("cap", cap, body) if cap else body


def parse(pat, flags="", utf8=False):
    pr = Parser(pat, flags, utf8)
    ast = pr.parse()
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
    ASSERT [ASSERT, kind, out]           kind: 'bos' | 'eos' | 'eosnl'
    MATCH  [MATCH]
    """

    def __init__(self, ast, ncap, anchored=False, opts=None):
        self.n = []
        self.ncap = ncap
        self.ntags = 2 * (ncap + 1)
        self.nloops = 0
        self.opts = opts or {}
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
        if k in ("bos", "eos", "eosnl"):
            return self.add([ASSERT, k, nxt])
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


def closure(nfa, seeds, at_bos):
    """seeds: ordered list of ('node', i, payload) or ('direct', key, payload).
    Returns ordered list of (key, payload, written) where key is a CHAR node id
    or ('M', cond); `written` is the set of tags crossed on the path. Stops at
    the first unconditional accept (lower-priority threads are pruned).
    Priority DFS; visited keyed by (node, loops-entered-in-this-closure): the
    empty-iteration rule (an iteration that consumed nothing ends its loop,
    PCRE's KETRMAX check) makes the path's context part of the node's future."""
    N = nfa.n
    out = []
    claimed = set()
    visited = set()
    for kind, x, payload in seeds:
        if kind == "direct":
            if x not in claimed:
                claimed.add(x)
                out.append((x, payload, frozenset()))
            continue
        stack = [(x, frozenset(), frozenset(), None)]
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
                if a == "bos":
                    if at_bos:
                        stack.append((nd[2], ctx, wr, cond))
                else:
                    stack.append((nd[2], ctx, wr, cond_and(cond, "z" if a == "eos" else "Z")))
    return out


# --------------------------------------------------------------------------
# Pike VM over the TNFA (reference semantics; per-thread tag dicts)
# --------------------------------------------------------------------------
def result_from_tags(nfa, tags):
    g = []
    for k in range(nfa.ncap + 1):
        s, e = tags.get(2 * k, -1), tags.get(2 * k + 1, -1)
        g.append(None if s < 0 or e < 0 else (s, e))
    return g


def pike(nfa, subj):
    def step_closure(seeds, pos):
        res = closure(nfa, seeds, pos == 0)
        th = []
        for key, tags, wr in res:
            if wr:
                tags = dict(tags)
                for t in wr:
                    tags[t] = pos
            th.append((key, tags))
        return th

    threads = step_closure([("node", nfa.start, {})], 0)
    best = None

    def accept(th):
        for key, tags in th:
            if key == ("M", None):
                return tags
        return None

    best = accept(threads) or best
    for i, b in enumerate(subj):
        seeds = []
        for key, tags in threads:
            if isinstance(key, tuple):
                if key[1] == "Z" and b == 10:
                    seeds.append(("direct", ("M", "z"), tags))
                continue
            nd = nfa.n[key]
            if b in nd[1]:
                seeds.append(("node", nd[2], tags))
        if not seeds:
            threads = []
            break
        threads = step_closure(seeds, i + 1)
        a = accept(threads)
        if a is not None:
            best = a
    for key, tags in threads:  # EOF: first accepting thread in priority order
        if isinstance(key, tuple):
            best = tags
            break
    return None if best is None else result_from_tags(nfa, best)


# --------------------------------------------------------------------------
# Tagged DFA
# --------------------------------------------------------------------------
class TooBig(Exception):
    pass


def byte_classes(nfa):
    """Partition 0..255 by the CHAR sets of the NFA (plus \\n alone when any
    $-assertion exists)."""
    sets = [nd[1] for nd in nfa.n if nd[0] == CHAR]
    if any(nd[0] == ASSERT and nd[1] == "eosnl" for nd in nfa.n):
        sets.append(frozenset([10]))
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
    'P' (the current position) or a register. tagged=False builds the
    untagged DFA over the same NFA (same thread lists, no tag identity)."""

    def __init__(self, nfa, tagged=True, max_states=4000):
        self.nfa = nfa
        self.tagged = tagged
        self.classes, self.cmap = byte_classes(nfa)
        self.states = []
        self.index = {}
        self.trans = {}  # (state, symbol class) -> (dest, ops)
        self.max_states = max_states
        self.nregs = 0
        # initial state
        seeds = [("node", nfa.start, {t: "U" for t in range(nfa.ntags)})]
        res = closure(nfa, seeds, True)
        self.init, self.init_ops = self.intern(res, {})
        self.build()

    def livetags(self, key):
        if isinstance(key, tuple):
            return range(self.nfa.ntags)
        return sorted(self.nfa.live[key])

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
                if v != "P" and v[1] not in used:
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
        ops = {}
        for c, v in enumerate(srcs):
            dst = regmap[c]
            src = "P" if v == "P" else v[1]
            if src != dst and not ("nocopy" in SABOTAGE and src != "P"):
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
        rep = self.classes[sym][0]
        seeds = []
        for ti, key in enumerate(keys):
            vals = self.thread_vals(sid, ti) if self.tagged else {}
            if isinstance(key, tuple):
                if key[1] == "Z" and rep == 10:
                    seeds.append(("direct", ("M", "z"), vals))
                continue
            nd = self.nfa.n[key]
            if rep in nd[1]:
                seeds.append(("node", nd[2], vals))
        res = closure(self.nfa, seeds, False)
        r = self.intern(res, regmap)
        self.trans[k] = r
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
    def out_of(self, sid, ti, regs, pos_known=None):
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
                regs[d] = pos if s == "P" else old[s]

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
        keys = self.states[s][0][0]
        for ti, key in enumerate(keys):
            if isinstance(key, tuple):
                return self.out_of(s, ti, regs)
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
            ns = sum(1 for v in ops.values() if v == "P")
            nc = len(ops) - ns
            sets += ns
            copies += nc
            copy_tr += nc > 0
            maxops = max(maxops, len(ops))
            # a copy whose source is also a destination needs a temporary in C
            if any(v != "P" and v in ops for v in ops.values()):
                cyc += 1
        live_states = sum(1 for st in self.states if st[0][0])
        return dict(states=live_states, regs=self.nregs, trans=ntr, sets=sets, copies=copies,
                    copy_trans=copy_tr, maxops=maxops, tmp_trans=cyc,
                    init_ops=len(self.init_ops), classes=len(self.classes))


def compile_pattern(pat, flags="", utf8=False, anchored=False):
    ast, ncap = parse(pat, flags, utf8)
    return TNFA(ast, ncap, anchored=anchored)
