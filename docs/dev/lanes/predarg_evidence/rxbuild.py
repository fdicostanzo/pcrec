# predarg: a python `re` regex built MECHANICALLY from a program's text and its bindings' bodies, every group and
# every written label made a uniquely named group (g0, g1, ...) so a READING can name which one a read targets.
# The language's labels carry no extra matching meaning in these programs (no loops, no `&` between patterns), so
# the regex with the target's single-digit content narrowed by the condition gives the program's three modes.
# Design evidence only; asserts nothing. Uses the model's scanners (TR11, split111, split_top_commas, _is_cond).
import re

import load

NS = load.NS
TR11 = NS["TR11"]


class Build:
    def __init__(self, expr, binds):
        self.defs = {}
        for b in binds:
            m = re.match(r"\s*([A-Za-z_][\w.]*)(\(([^)]*)\))?\s*:=\s*(.*)$", b, re.S)
            ps = None if m.group(3) is None else [p.split("=")[0].strip() for p in m.group(3).split(",")]
            self.defs[m.group(1)] = (ps, m.group(4).strip())
        for nm, (ps, body) in NS["LIBMACROS"].items():
            self.defs.setdefault(nm, ([p for p, _ in ps], body))
        self.groups = []                                     # (gK, name, owner, kind)
        parts = NS["split111"](expr, 0, len(expr), "&")
        gq = re.compile(r"(some|every|count|none|all|occurs[.\w]*)\(\s*@")
        isc = [(expr[x:y].startswith("(") and NS["_is_cond"](expr[x:y])) or bool(gq.match(expr[x:y])) for x, y in parts]
        pat = [expr[x:y] for (x, y), c in zip(parts, isc) if not c]
        self.conds = [expr[x:y] for x, y in parts if expr[x:y].startswith("(") and NS["_is_cond"](expr[x:y])]
        assert len(pat) == 1, "one pattern part only"
        self.rx = self.low(pat[0], {}, "P")

    def new(self, name, owner, kind):
        g = "g%d" % len(self.groups)
        self.groups.append((g, name, owner, kind))
        return g

    def low(self, s, env, owner):
        s = s.strip()
        sp = NS["split111"]
        ps = sp(s, 0, len(s), "|")
        if len(ps) > 1:
            return "(?:%s)" % "|".join(self.low(s[x:y], env, owner) for x, y in ps)
        ps = sp(s, 0, len(s), "SEQ")
        if len(ps) > 1:
            return "".join(self.low(s[x:y], env, owner) for x, y in ps)
        return self.atom(s, env, owner)

    def atom(self, s, env, owner):
        if s.startswith("^"):
            return "(?=%s)" % self.atom(s[1:], env, owner)
        if s[0] == "(" and TR11._group_end(s, 0) == len(s):
            return "(?:%s)" % self.low(s[1:-1], env, owner)
        if s[0] == "[" and TR11._group_end(s, 0) == len(s):
            m = re.match(r"\[\s*(\([^)]*\)|_?\w*)\s*=\s*(.*)\]$", s, re.S)
            nm = m.group(1)
            inner = self.low(m.group(2), env, owner)
            if nm.startswith("("):
                return "(?:%s)" % inner
            if nm in env and env[nm][0] == "label":
                nm = env[nm][1]                              # a label parameter: the sent name
                if nm == "_":
                    return "(?:%s)" % inner
            return "(?P<%s>%s)" % (self.new(nm, owner, "label"), inner)
        if s[0] == "/" and TR11._rx_end(s, 0) == len(s):
            return self.rxt(s[1:-1], env, owner)
        if s[0] in "\"'":
            return re.escape(TR11._unstring(s))
        m = re.match(r"([A-Za-z_][\w.]*)$", s)
        if m:
            nm = m.group(1)
            if nm in env:
                _, text, cenv, cown = env[nm]                # built afresh at each placement: own group names
                return "(?:%s)" % self.low(text, cenv, cown)
            ps, body = self.defs[nm]
            assert ps is None, nm
            return "(?:%s)" % self.low(body, {}, nm)
        m = re.match(r"([A-Za-z_][\w.]*)\((.*)\)$", s, re.S)
        if m:
            ps, body = self.defs[m.group(1)]
            a = m.group(2)
            args = [a[x:y] for x, y in NS["split_top_commas"](a, 0, len(a))]
            env2 = {}
            for p, x in zip(ps, args):
                x = x.strip()
                kw = re.match(r"(\w+)\s*=\s*(.*)$", x, re.S)
                if kw and kw.group(1) in ps and not x.startswith("["):
                    p, x = kw.group(1), kw.group(2)
                if p.endswith(":") or x.endswith(":"):
                    env2[p.rstrip(":")] = ("label", x.rstrip(":"))
                else:
                    env2[p] = ("arg", x, env, owner)
            return "(?:%s)" % self.low(body, env2, m.group(1))
        raise ValueError("atom " + s[:40])

    def rxt(self, t, env, owner):
        out, i = [], 0
        while i < len(t):
            if t.startswith("${", i):
                j = TR11._brace_end(t, i + 1)
                out.append("(?:%s)" % self.low(t[i + 2:j - 1], env, owner))
                i = j
                continue
            if t[i] == "\\":
                out.append(t[i:i + 2])
                i += 2
                continue
            m = re.match(r"\(\?<:?\$\{(\w+)\}>", t[i:])
            if m:
                lab = env[m.group(1)][1]
                out.append("(?:" if lab == "_" else "(?P<%s>" % self.new(lab, owner, "sent"))
                i += m.end()
                continue
            m = re.match(r"\(\?<:?(_?[A-Za-z]\w*)>", t[i:])
            if m:
                out.append("(?P<%s>" % self.new(m.group(1), owner, "group"))
                i += m.end()
                continue
            out.append(t[i])
            i += 1
        return "".join(out)

    def pick(self, name, k=1, owner=None):
        """the k-th group or label of that name (and owner), in written order of the expansion."""
        c = [g for g, n, o, _ in self.groups if n == name and (owner is None or o == owner)]
        return c[k - 1]

    def regex(self, target, cond):
        """the regex with the target group's `\\d` narrowed by the condition (`<5`, `"3"`, `3`)."""
        m = re.match(r"\s*(<|>=)\s*(\d)\s*$", cond)
        if m:
            lo, hi = (0, int(m.group(2)) - 1) if m.group(1) == "<" else (int(m.group(2)), 9)
            cls = "[%d-%d]" % (lo, hi)
        else:
            cls = re.escape(TR11._unstring(cond.strip()) if cond.strip()[0] in "\"'" else cond.strip())
        pre = "(?P<%s>" % target
        a = self.rx.index(pre) + len(pre)
        if self.rx.startswith("\\d)", a):
            return self.rx[:a] + cls + self.rx[a + 2:]
        return self.rx[:a] + "(?=%s)" % cls + self.rx[a:]    # a label over one character: its text narrowed


def modes(rx, target, whole, search, findall):
    """the three modes, the model's conventions (RePg: a match counts only where the target is set)."""
    c = re.compile(rx)

    def ok(m):
        return m is not None and m.group(target) is not None

    def srch(t):
        for i in range(len(t) + 1):
            m = c.match(t, i)
            if ok(m):
                return "`%s`@%d" % (m.group(0), i)
        return "FAILS"

    def fa(t):
        out, i = [], 0
        while i <= len(t):
            m = c.match(t, i)
            if ok(m):
                out.append("`%s`@%d" % (m.group(0), i))
                i = m.end() if m.end() > i else i + 1
                continue
            i += 1
        return "[%s]" % ", ".join(out)
    w = ", ".join("`%s` %s" % (x, "HOLDS" if ok(c.fullmatch(x)) else "FAILS") for x in whole)
    return "WHOLE %s / SEARCHED `%s` %s / FIND-ALL `%s` %s" % (w, search, srch(search), findall, fa(findall))
