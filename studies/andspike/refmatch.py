"""refmatch.py -- a tiny backtracking reference matcher, independent of PCRE2.

Subset: literals, `.` (any char, DOTALL), `[...]` sets of literals, `(...)`,
`(?:...)`, `|`, and the quantifiers * + ? {m} {m,} {m,n}, each greedy or lazy
(`?` suffix). No anchors, lookarounds, backreferences, possessives.

`ends(node, s, i)` yields (end, caps) in backtracking PREFERENCE order, the
order a PCRE-style matcher tries them; unlimited repeats stop iterating after
an iteration that consumed nothing (the PCRE empty-iteration rule).
Also: `gen_pattern(rng, ...)` -- the random pattern generator for the sweeps.
"""


class Parser:
    def __init__(self, src):
        self.s, self.k, self.ncap = src, 0, 0

    def peek(self):
        return self.s[self.k] if self.k < len(self.s) else None

    def parse(self):
        n = self.alt()
        if self.k != len(self.s):
            raise ValueError("trailing input at %d in %r" % (self.k, self.s))
        return n

    def alt(self):
        arms = [self.seq()]
        while self.peek() == "|":
            self.k += 1
            arms.append(self.seq())
        return ("alt", arms) if len(arms) > 1 else arms[0]

    def seq(self):
        items = []
        while self.peek() not in (None, "|", ")"):
            items.append(self.quant(self.atom()))
        return ("seq", items)

    def atom(self):
        c = self.peek()
        if c == "(":
            if self.s.startswith("(?:", self.k):
                self.k += 3
                n, cap = self.alt(), None
            else:
                self.k += 1
                self.ncap += 1
                cap = self.ncap
                n = self.alt()
            if self.peek() != ")":
                raise ValueError("missing ) in %r" % self.s)
            self.k += 1
            return ("group", cap, n)
        if c == "[":
            e = self.s.index("]", self.k)
            chars = set(self.s[self.k + 1:e])
            self.k = e + 1
            return ("set", frozenset(chars))
        if c == ".":
            self.k += 1
            return ("any",)
        if c == "\\":
            self.k += 2
            return ("lit", self.s[self.k - 1])
        self.k += 1
        return ("lit", c)

    def quant(self, a):
        c = self.peek()
        if c in ("*", "+", "?"):
            self.k += 1
            lo, hi = {"*": (0, None), "+": (1, None), "?": (0, 1)}[c]
        elif c == "{":
            e = self.s.index("}", self.k)
            body = self.s[self.k + 1:e]
            self.k = e + 1
            if "," in body:
                a_, b_ = body.split(",")
                lo, hi = int(a_), (int(b_) if b_ else None)
            else:
                lo = hi = int(body)
        else:
            return a
        lazy = False
        if self.peek() == "?":
            self.k += 1
            lazy = True
        return ("rep", a, lo, hi, lazy)


def parse(src):
    pr = Parser(src)
    return pr.parse(), pr.ncap


def m(n, s, i, caps):
    t = n[0]
    if t == "lit":
        if i < len(s) and s[i] == n[1]:
            yield i + 1, caps
    elif t == "any":
        if i < len(s):
            yield i + 1, caps
    elif t == "set":
        if i < len(s) and s[i] in n[1]:
            yield i + 1, caps
    elif t == "seq":
        yield from _seq(n[1], 0, s, i, caps)
    elif t == "alt":
        for a in n[1]:
            yield from m(a, s, i, caps)
    elif t == "group":
        for e, c2 in m(n[2], s, i, caps):
            if n[1] is not None:
                c2 = c2[:n[1] - 1] + ((i, e),) + c2[n[1]:]
            yield e, c2
    elif t == "rep":
        yield from _rep(n[1], n[2], n[3], n[4], s, i, caps, 0)
    else:
        raise ValueError(t)


def _seq(items, k, s, i, caps):
    if k == len(items):
        yield i, caps
        return
    for e, c2 in m(items[k], s, i, caps):
        yield from _seq(items, k + 1, s, e, c2)


def _rep(a, lo, hi, lazy, s, i, caps, count):
    if count < lo:
        for e, c2 in m(a, s, i, caps):
            yield from _rep(a, lo, hi, lazy, s, e, c2, count + 1)
        return
    can_more = hi is None or count < hi

    def more():
        for e, c2 in m(a, s, i, caps):
            if e == i and hi is None:
                yield e, c2  # empty iteration of an unlimited repeat: stop looping
            else:
                yield from _rep(a, lo, hi, lazy, s, e, c2, count + 1)

    if lazy:
        yield i, caps
        if can_more:
            yield from more()
    else:
        if can_more:
            yield from more()
        yield i, caps


def ends(src, s, i):
    """Distinct ends of pattern `src` from i, in first-occurrence order."""
    node, ncap = parse(src)
    seen, out = set(), []
    for e, _ in m(node, s, i, (None,) * ncap):
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out


def matches(src, s, i):
    """Every (end, caps) path in order (duplicates kept): the predicate reference."""
    node, ncap = parse(src)
    return m(node, s, i, (None,) * ncap)


# -- random patterns --------------------------------------------------------
QUANTS = ["*", "+", "?", "{0,2}", "{1,2}", "{2}", "*?", "+?", "??", "{0,2}?"]


def gen_pattern(rng, alphabet="ab", depth=3, caps=False):
    def atom(d):
        r = rng.random()
        if d <= 0 or r < 0.45:
            return rng.choice(list(alphabet) + ["."] + ["[%s]" % alphabet])
        inner = alt(d - 1)
        return ("(" if caps and rng.random() < 0.5 else "(?:") + inner + ")"

    def item(d):
        a = atom(d)
        if rng.random() < 0.35:
            a += rng.choice(QUANTS)
        return a

    def seq(d):
        return "".join(item(d) for _ in range(rng.randint(1, 3)))

    def alt(d):
        k = 1 if rng.random() < 0.6 else rng.randint(2, 3)
        return "|".join(seq(d) for _ in range(k))

    return alt(depth)
