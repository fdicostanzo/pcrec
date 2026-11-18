#!/usr/bin/env python3
# Lane predspec244 (2026-11-17): the evidence engine of docs/design/predicates_draft.md REVISION 24.4 (the owner's
# rulings of the evening of 2026-11-17 after rev 24.3: ONE label rule, "branchings reset the labels inside them";
# an unqualified `$x` reads the label; the hit list atomic and anchored; the filter sentence; join order; zero-place).
# DESIGN EVIDENCE ONLY; rules nothing.
#
# HOW: a NEW, small path enumerator (not a patch of the earlier engines): a regex subset parsed here (literals, `.`,
# classes, `\d \D \w \s`, `(?:..)`, `(?<n>..)`, `(?>..)`, `|`, `* + ? {m,n}` greedy and lazy, `\A \z ^ $`) whose
# paths come out in PCRE's preference order; a CONDITION is a callout node `(?C"name")` (the same spelling as the
# libpcre2 models) that reads the LABELS under the rule in force. Three label rules (switch PREDSPEC244_RULES):
#   244   (rev 24.4, THE ONE RULE): entering ANY BRANCHING (an alternation of two or more branches; any quantifier
#         other than {1}: an optional, a loop, a counted repeat) resets every label NAME whose group lies inside it;
#         a group's close sets its name; in a sequence the last mention wins. Nothing else ever resets a label.
#   243   (rev 24.3's rules, the switch back): a LOOP (a quantifier with upper bound > 1) resets the names inside it on
#         entry and at the START OF EVERY PASS (a pass has its own labels); alternations and optionals reset nothing;
#         a group that took no part is unset because nothing set it.
#   carry PCRE's capture state (rev 24.1's carry): nothing resets.
# Rule 244 has NO per-pass reset: a pass's own labels come out of it only through branchings inside the body.
# The pass forms (`some`, `occurs.none`, `h[k]`) read the OUTERMOST loop's pass table: the labels at the end of
# each of its passes. FIND-ALL is PCRE2's global loop (retry NOTEMPTY_ATSTART | ANCHORED after an empty match). A
# loop iteration that matches the empty string past the minimum is kept as the last pass (rev 24.3 A1).
#
# CONTROL: libpcre2-8 (the installed library, run through ../rxmodel_evidence/pcre2h.py, never read: D181).
#   CAPTURES: plain PCRE2 (the capture IS rule `carry`).
#   LABELS under rule 244: THE MARKER MODEL (no construction shared with the engine): every label group renamed
#   (h1, h2, ...) and an empty capture `(?<eK>)` written just before every branching that contains a group of the
#   name; PCRE2 restores captures on backtracking, so at the final callout each marker holds where its branching
#   was LAST ENTERED on the path and each copy holds where it was LAST SET. The label = the copy set last (largest
#   end), unless a marker of the name was entered at or after that end (then unset). Positional: exact when every
#   label group consumes a character (an empty group ties with its marker: a stated limit, no such row here).
#
# SWITCHES (W = the worktree; run from $PCREC_TMPDIR/scratch/predspec244; one process, well under a minute):
#   timeout 1800 python3 -I -B W/docs/dev/lanes/predspec244_evidence/predspec244_model.py > fwd.out
#   PREDSPEC244_RULES=243      the engine's DEFAULT rule becomes rev 24.3's (the switch back: PART A's printed
#                              lines must come out as rev 24.3 printed them, and PART N's new answers move)
#   PREDSPEC244_SABOTAGE=1     rule 244 resets only at LOOP entry (not at an alternation or an optional): the
#                              checks against the marker model and the printed lines must fail
import os, sys, re, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rxmodel_evidence"))
import pcre2h as P                                                     # noqa: E402

DEFAULT = os.environ.get("PREDSPEC244_RULES", "244")
SAB = os.environ.get("PREDSPEC244_SABOTAGE") == "1"
assert DEFAULT in ("244", "243", "carry")

# ------------------------------------------------------------------------------------------------------- parser
DIG = set("0123456789")
def cls_of(esc):
    return {"d": lambda c: c in DIG, "D": lambda c: c not in DIG, "w": lambda c: c.isalnum() or c == "_",
            "s": lambda c: c in " \t\n\r\f\v", "S": lambda c: c not in " \t\n\r\f\v"}[esc]

class Parser:
    def __init__(self, src): self.s, self.i, self.n = src, 0, 0
    def peek(self): return self.s[self.i] if self.i < len(self.s) else None
    def parse(self):
        node = self.alt()
        assert self.i == len(self.s), ("trailing", self.s, self.i)
        return node
    def alt(self):
        br = [self.seq()]
        while self.peek() == "|": self.i += 1; br.append(self.seq())
        return br[0] if len(br) == 1 else ("alt", br)
    def seq(self):
        items = []
        while self.peek() not in (None, "|", ")"):
            items.append(self.quant(self.atom()))
        return ("seq", items)
    def quant(self, a):
        c = self.peek()
        if c in ("*", "+", "?") or (c == "{" and re.match(r"\{\d+(,\d*)?\}", self.s[self.i:])):
            if c == "{":
                m = re.match(r"\{(\d+)(,(\d*))?\}", self.s[self.i:]); self.i += m.end()
                lo = int(m.group(1)); hi = lo if m.group(2) is None else (int(m.group(3)) if m.group(3) else 10 ** 9)
            else:
                self.i += 1; lo, hi = {"*": (0, 10 ** 9), "+": (1, 10 ** 9), "?": (0, 1)}[c]
            greedy = True
            if self.peek() == "?": self.i += 1; greedy = False
            self.n += 1
            return self.quant(("rep", a, lo, hi, greedy, self.n))
        return a
    def atom(self):
        c = self.s[self.i]; self.i += 1
        if c == "(":
            if self.s.startswith('?C"', self.i):
                j = self.s.index('"', self.i + 3); nm = self.s[self.i + 3:j]; self.i = j + 2
                return ("call", nm)
            if self.s.startswith("?J)", self.i): self.i += 3; return ("seq", [])
            name, kind = None, "grp"
            if self.s.startswith("?:", self.i): self.i += 2; kind = "nc"
            elif self.s.startswith("?>", self.i): self.i += 2; kind = "atomic"
            elif self.s.startswith("?<=", self.i) or self.s.startswith("?<!", self.i):
                neg = self.s[self.i + 2] == "!"; self.i += 3; inner = self.alt(); assert self.s[self.i] == ")"; self.i += 1
                return ("lookb", neg, inner)
            elif self.s.startswith("?=", self.i) or self.s.startswith("?!", self.i):
                neg = self.s[self.i + 1] == "!"; self.i += 2; inner = self.alt(); assert self.s[self.i] == ")"; self.i += 1
                return ("look", neg, inner)
            else:
                m = re.match(r"\?P?<([A-Za-z_]\w*)>", self.s[self.i:]); assert m, self.s
                self.i += m.end(); name = m.group(1)
            inner = self.alt(); assert self.s[self.i] == ")"; self.i += 1
            if kind == "nc": return inner
            if kind == "atomic": return ("atomic", inner)
            return ("grp", name, inner)
        if c == "[":
            neg = self.peek() == "^"
            if neg: self.i += 1
            fs = []
            while self.s[self.i] != "]":
                ch = self.s[self.i]
                if ch == "\\":
                    fs.append(cls_of(self.s[self.i + 1])); self.i += 2; continue
                if self.s[self.i + 1] == "-" and self.s[self.i + 2] != "]":
                    a, b = ch, self.s[self.i + 2]; fs.append(lambda x, a=a, b=b: a <= x <= b); self.i += 3; continue
                fs.append(lambda x, ch=ch: x == ch); self.i += 1
            self.i += 1
            return ("chr", (lambda x, fs=fs, neg=neg: any(f(x) for f in fs) != neg))
        if c == "\\":
            e = self.s[self.i]; self.i += 1
            if e in "dDwsS": return ("chr", cls_of(e))
            if e == "A": return ("bos",)
            if e == "z": return ("eos",)
            if e == "Z": return ("eosnl",)
            if e in "bB": return ("wb", e == "B")
            return ("chr", lambda x, e=e: x == e)
        if c == ".": return ("chr", lambda x: x != "\n")
        if c == "^": return ("bos",)
        if c == "$": return ("eos",)
        return ("chr", lambda x, c=c: x == c)

def names_in(node, acc=None):
    acc = set() if acc is None else acc
    t = node[0]
    if t == "grp": acc.add(node[1]); names_in(node[2], acc)
    elif t in ("seq",): [names_in(x, acc) for x in node[1]]
    elif t == "alt": [names_in(x, acc) for x in node[1]]
    elif t == "rep": names_in(node[1], acc)
    elif t in ("atomic",): names_in(node[1], acc)
    elif t in ("look", "lookb"): names_in(node[2], acc)
    return acc

def loops_of(node, outer=None, acc=None):
    """name -> id of the OUTERMOST loop (upper bound > 1) enclosing a group of that name."""
    acc = {} if acc is None else acc
    t = node[0]
    if t == "grp":
        if outer is not None: acc.setdefault(node[1], outer)
        loops_of(node[2], outer, acc)
    elif t in ("seq", "alt"): [loops_of(x, outer, acc) for x in node[1]]
    elif t == "rep": loops_of(node[1], outer if outer is not None or node[3] <= 1 else node[5], acc)
    elif t == "atomic": loops_of(node[1], outer, acc)
    elif t == "look": loops_of(node[2], outer, acc)
    return acc

# ------------------------------------------------------------------------------------------------------- engine
class St:
    __slots__ = ("labs", "caps", "log", "ptab")
    def __init__(self, labs, caps, log, ptab): self.labs, self.caps, self.log, self.ptab = labs, caps, log, ptab
    def reset(self, names):
        if not names: return self
        labs = dict(self.labs)
        for n in names: labs[n] = None
        return St(labs, self.caps, self.log + tuple(("reset", n) for n in sorted(names)), self.ptab)

class View:
    def __init__(self, prog, s, start, pos, st): self.prog, self.s, self.start, self.pos, self.st = prog, s, start, pos, st
    def lab(self, n): return (self.st.caps if self.prog.rule == "carry" else self.st.labs).get(n)
    def cap(self, n): return self.st.caps.get(n)
    def passes(self, n):
        lid = self.prog.outer.get(n)
        return None if lid is None else list(self.st.ptab.get(lid, ()))
    def array(self, n, slots=False):
        """every setting of the name in order (the array form); with slots=True a reset after a setting leaves None"""
        out = []
        for ev in self.st.log:
            if ev[0] == "set" and ev[1] == n: out.append(ev[2])
            elif slots and ev[0] == "reset" and ev[1] == n and out and out[-1] is not None: out.append(None)
        return out

class Prog:
    def __init__(self, src, conds=None, rule=None, sab=None):
        self.src, self.conds = src, dict(conds or {})
        self.rule = rule or DEFAULT
        self.sab = SAB if sab is None else sab
        self.root = Parser(src).parse()
        self.outer = loops_of(self.root)
        self.names = sorted(names_in(self.root))
        self._ni = {}
    def ni(self, node):
        k = id(node)
        if k not in self._ni: self._ni[k] = frozenset(names_in(node))
        return self._ni[k]
    def m(self, node, s, pos, st, start):
        t = node[0]
        if t == "chr":
            if pos < len(s) and node[1](s[pos]): yield pos + 1, st
        elif t == "seq":
            yield from self.seqm(node[1], 0, s, pos, st, start)
        elif t == "alt":
            if self.rule == "244" and not self.sab: st = st.reset(self.ni(node))
            for b in node[1]: yield from self.m(b, s, pos, st, start)
        elif t == "grp":
            for p2, st2 in self.m(node[2], s, pos, st, start):
                v = s[pos:p2]; labs = dict(st2.labs); caps = dict(st2.caps); labs[node[1]] = v; caps[node[1]] = v
                yield p2, St(labs, caps, st2.log + (("set", node[1], v),), st2.ptab)
        elif t == "rep":
            _, body, lo, hi, greedy, rid = node
            names = self.ni(body)
            if self.rule == "244" and (lo, hi) != (1, 1) and (not self.sab or hi > 1): st = st.reset(names)
            if self.rule == "243" and hi > 1: st = st.reset(names)
            ptab = dict(st.ptab); ptab[rid] = (); st = St(st.labs, st.caps, st.log, ptab)
            yield from self.repm(body, lo, hi, greedy, rid, names, 0, s, pos, st, start)
        elif t == "call":
            if self.conds[node[1]](View(self, s, start, pos, st)): yield pos, st
        elif t == "bos":
            if pos == 0: yield pos, st
        elif t == "eos":
            if pos == len(s): yield pos, st
        elif t == "eosnl":
            if pos == len(s) or (pos == len(s) - 1 and s[-1] == "\n"): yield pos, st
        elif t == "wb":
            w = lambda i: 0 <= i < len(s) and (s[i].isalnum() or s[i] == "_")
            if (w(pos - 1) != w(pos)) != node[1]: yield pos, st
        elif t == "lookb":
            got = None
            for k in range(pos, -1, -1):
                got = next((r for r in self.m(node[2], s, k, st, start) if r[0] == pos), None)
                if got is not None: break
            if node[1]:
                if got is None: yield pos, st
            elif got is not None: yield pos, got[1]
        elif t == "atomic":
            for r in self.m(node[1], s, pos, st, start): yield r; break
        elif t == "look":
            got = next(self.m(node[2], s, pos, st, start), None)
            if node[1]:
                if got is None: yield pos, st
            elif got is not None: yield pos, got[1]
    def seqm(self, items, i, s, pos, st, start):
        if i == len(items): yield pos, st; return
        for p2, st2 in self.m(items[i], s, pos, st, start):
            yield from self.seqm(items, i + 1, s, p2, st2, start)
    def repm(self, body, lo, hi, greedy, rid, names, count, s, pos, st, start):
        def more():
            if count < hi:
                st1 = st.reset(names) if (self.rule == "243" and hi > 1) else st
                for p2, st2 in self.m(body, s, pos, st1, start):
                    ptab = dict(st2.ptab); ptab[rid] = ptab.get(rid, ()) + (dict(st2.labs),)
                    st3 = St(st2.labs, st2.caps, st2.log, ptab)
                    if p2 == pos and count >= lo:      # an empty iteration past the minimum: kept, the loop ends
                        yield p2, st3; continue
                    yield from self.repm(body, lo, hi, greedy, rid, names, count + 1, s, p2, st3, start)
        if greedy:
            yield from more()
            if count >= lo: yield pos, st
        else:
            if count >= lo: yield pos, st
            yield from more()
    def paths(self, s, pos):
        st = St({n: None for n in self.names}, {n: None for n in self.names}, (), {})
        for p2, st2 in self.m(self.root, s, pos, st, pos): yield p2, st2
    def labels(self, st): return dict(st.caps) if self.rule == "carry" else dict(st.labs)
    # modes
    def whole(self, s):
        for p2, st in self.paths(s, 0):
            if p2 == len(s): return (True, self.labels(st), st)
        return (False, None, None)
    def search(self, s, pos=0, notempty_anchored=False):
        for st_ in range(pos, len(s) + 1):
            for p2, st in self.paths(s, st_):
                if notempty_anchored and p2 == st_: continue
                return (st_, p2, self.labels(st), st)
            if notempty_anchored: return None
        return None
    def findall(self, s):
        out, pos, ne = [], 0, False
        while pos <= len(s):
            r = self.search(s, pos, ne)
            if r is None:
                if ne: pos += 1; ne = False; continue
                break
            out.append(r[:3]); ne = r[1] == r[0]; pos = r[1]
        return out

# ------------------------------------------------------------------------------------------------------- helpers
def strings(alpha, n):
    out, cur = [""], [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
def lists(items, n):
    out, cur = [""], [""]
    for _ in range(n):
        cur = [c + it for c in cur for it in items]; out += cur
    return out
def num(v): return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None
def lt(n): return lambda v: num(v) and int(v) < n

def fl(labs, keys):
    if labs is None or not keys: return ""
    return " " + ", ".join("%s = %s" % (k, "`%s`" % labs[k] if labs.get(k) is not None else "unset") for k in keys)
def W_(p, s, keys=()):
    ok, labs, _ = p.whole(s)
    return ("HOLDS" + fl(labs, keys)) if ok else "FAILS"
def S_(p, s, keys=()):
    r = p.search(s)
    return "FAILS" if r is None else "`%s`@%d%s" % (s[r[0]:r[1]], r[0], fl(r[2], keys))
def F_(p, s, keys=()):
    return "[" + ", ".join("`%s`@%d%s" % (s[a:b], a, fl(l, keys)) for a, b, l in p.findall(s)) + "]"

def row(p, s, mode, keys):
    if mode == "W":
        ok, labs, _ = p.whole(s); return (ok, tuple(sorted((labs or {}).items())) if keys else None)
    if mode == "S":
        r = p.search(s); return None if r is None else (r[0], r[1], tuple(sorted(r[2].items())) if keys else None)
    return tuple((a, b, tuple(sorted(l.items())) if keys else None) for a, b, l in p.findall(s))
def diff3(p1, p2, pool, keys=True):
    """texts whose reported row differs (holds, stretch, labels compared) per mode WHOLE / SEARCHED / FIND-ALL"""
    out, first = [], None
    for mode in "WSF":
        n = 0
        for s in pool:
            if row(p1, s, mode, keys) != row(p2, s, mode, keys):
                n += 1
                if first is None: first = (mode, s)
        out.append(n)
    return out, first
def fmt3(d): return "%d / %d / %d of %d%s" % (d[0][0], d[0][1], d[0][2], d[2], "" if d[1] is None else " (first %s `%s`)" % d[1])
def D3(p1, p2, pool, keys=True):
    d, f = diff3(p1, p2, pool, keys); return (d, f, len(pool))

CHECKS = []
def check(name, ok): CHECKS.append((name, bool(ok))); return "OK" if ok else "FAILED"

def mk(src, conds=None, rule=None, **kw): return Prog(src, conds, rule, **kw)
RULES = ("244", "243", "carry")

print("predspec244 engine: default rule %s%s; libpcre2-8 %s" % (DEFAULT, " (SABOTAGE: rule 244 resets only at loop entry)" if SAB else "", P.version()))
print()

# ======================================================================================================== PART A
print("== PART A: rev 24.3's printed label lines, under the one rule (244) AND the switch back (243); each line: the")
print("   answer under 244 ; under 243 ; the text rev 24.3 printed ; whether 244 equals the printed text")
NA, NA_DIFF = 0, []
def pa(tag, prog_src, conds, texts_modes, keys, printed):
    """texts_modes: list of (mode, text); printed: list of strings, one per (mode, text)"""
    global NA
    got = {}
    for rule in ("244", "243"):
        p = mk(prog_src, conds, rule)
        got[rule] = [{"W": W_, "S": S_, "F": F_}[m](p, t, keys) for m, t in texts_modes]
    for (m, t), a, b, pr in zip(texts_modes, got["244"], got["243"], printed):
        NA += 1
        same = a == pr and b == pr
        if a != pr: NA_DIFF.append((tag, m, t, a, pr))
        print("A %-7s %s %-22s 244 %s ; 243 %s ; printed %s ; %s" % (tag, {"W": "WHOLE   ", "S": "SEARCHED", "F": "FIND-ALL"}[m], "`%s`" % t, a, b, pr, check("A %s %s %s" % (tag, m, t), same)))

h5 = {"c": lambda v: lt(5)(v.lab("h"))}
nh5 = {"c": lambda v: not lt(5)(v.lab("h"))}
S1 = r"(?:(?<a>\d)|(?<b>[a-z]))*xx(?C\"c\")".replace('\\"', '"')
pa("S1", S1, {"c": lambda v: lt(5)(v.lab("a"))},
   [("W", "3qxx"), ("W", "q3xx"), ("W", "7q3xx"), ("S", "3qxx"), ("F", "3qxx q3xx 7q3xx")], (),
   ["FAILS", "HOLDS", "HOLDS", "FAILS", "[`q3xx`@5, `7q3xx`@10]"])
pa("S1a", S1, {"c": lambda v: lt(5)(v.lab("a"))}, [("W", "q3xx"), ("W", "7q3xx")], ("a",), ["HOLDS a = `3`", "HOLDS a = `3`"])
CLOSE = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*"
def jeq(v, d=None):
    h, m = v.lab("h"), v.lab("m")
    if m is None and d is not None: m = d
    return h is not None and m is not None and (h, m) == ("10", "45")
PO = ("9:45,10,", "10,9:45,", "10:45,10,")
pa("S2", CLOSE + '(?C"c")', {"c": lambda v: jeq(v)}, [("W", t) for t in PO], (), ["FAILS"] * 3)
pa("S3", CLOSE + '(?C"c")', {"c": lambda v: jeq(v, "00")}, [("W", t) for t in PO], (), ["FAILS"] * 3)
def hour(v):
    h, m = v.lab("h"), v.lab("m")
    m = "00" if m is None else m
    return (h, m) == ("10", "00")
pa("S4", CLOSE + '(?C"c")', {"c": hour}, [("W", t) for t in PO], (), ["HOLDS", "FAILS", "HOLDS"])
pa("S2s", CLOSE + '(?C"c")', {"c": lambda v: jeq(v)}, [("S", "10,9:45, 10:45,"), ("F", "9:45,10, 10:45, 10,9:45,")], (),
   ["`10:45,`@9", "[`10:45,`@9]"])
def late(h, m): return num(h) and num(m) and (int(h), int(m)) >= (9, 30)
LATE = r'(?:(?<h>\d{1,2})(?::(?<m>\d\d))?,(?C"c"))*'
lc = {"c": lambda v: late(v.lab("h"), v.lab("m"))}
pa("S5", LATE, lc, [("W", "10:00,9:00,11:00,"), ("S", "10:00,9:00,11:00,"), ("W", "10:15,9:00,11:15,"), ("S", "10:15,9:00,11:15,"),
                    ("W", "9:45,10:15,"), ("W", "9:45,10,")], (),
   ["FAILS", "``@0", "FAILS", "`10:15,`@0", "HOLDS", "FAILS"])
pa("S5f", LATE, lc, [("F", "10:15,9:00,11:15,")], (), ["[`10:15,`@0, ``@6, ``@7, ``@8, ``@9, ``@10, `11:15,`@11, ``@17]"])
NEST = r"(?:(?:(?<h>\d)?;)*,)*"
pa("N", NEST + '(?C"c")', h5, [("W", "3;,,"), ("W", "3;;,"), ("W", "3;,7;,"), ("W", "7;,3;,"), ("S", "3;,, 7;,"), ("F", "3;,, 3;;, 3;,7;,")], ("h",),
   ["FAILS", "FAILS", "FAILS", "HOLDS h = `3`", "`3;,`@0 h = `3`", "[`3;,`@0 h = `3`, `3;,`@10 h = `3`]"])
ITEM = r'(?<h>\d)?;(?C"c")'
pa("Ni", r"(?:(?:" + ITEM + r")*,)*", h5, [("W", "3;,,"), ("W", "3;;,"), ("W", "3;,7;,"), ("W", "7;,3;,"), ("S", "3;,, 7;,")], (),
   ["HOLDS", "FAILS", "FAILS", "FAILS", "`3;,,`@0"])
pa("Nii", r'(?:(?:(?<h>\d)?;)*(?C"c"),)*', h5, [("W", "3;,,"), ("W", "3;;,"), ("W", "3;,7;,"), ("W", "7;,3;,"), ("S", "3;,, 7;,")], ("h",),
   ["FAILS", "FAILS", "FAILS", "FAILS", "`3;,`@0 h = `3`"])
def occ_none(pred, name):
    def f(v):
        ps = v.passes(name)
        return not any(pred(p.get(name)) for p in ps)
    return f
pa("X2", NEST + '(?C"c")', {"c": occ_none(lambda x: not lt(5)(x), "h")}, [("W", ","), ("W", "3;7;,"), ("W", "7;3;,")], (), ["FAILS", "FAILS", "HOLDS"])
def idx(name, k, pred):
    def f(v):
        ps = v.passes(name)
        return len(ps) >= k and pred(ps[k - 1].get(name))
    return f
pa("X2b", NEST + '(?C"c")', {"c": idx("h", 2, lt(5))}, [("W", ",3;,")], ("h",), ["HOLDS h = `3`"])
def some_j(v):
    return any(p.get("h") is not None and p.get("k") is not None and int(p["h"]) > int(p["k"]) for p in v.passes("h"))
pa("X3", r'(?:(?<k>\d)(?:(?<h>\d);)*,)*(?C"c")', {"c": some_j}, [("W", "37;,51;,")], (), ["HOLDS"])
pa("X3s", r'(?:(?<k>\d);)*(?:(?<h>\d),)*(?C"c")', {"c": lambda v: v.lab("h") is not None and v.lab("k") is not None and int(v.lab("h")) > int(v.lab("k"))},
   [("W", "3;7,")], ("h", "k"), ["HOLDS h = `7`, k = `3`"])
pa("X1", r'(?:(?<h>\d)?)*(?C"c")', nh5, [("W", "3"), ("S", "3"), ("F", "3")], ("h",), ["HOLDS h = unset", "`3`@0 h = unset", "[`3`@0 h = unset, ``@1 h = unset]"])
pa("X1p", r'(?:(?<h>\d)?)*(?C"c")', h5, [("W", "3")], ("h",), ["HOLDS h = `3`"])
pa("X1e", r'(?:a|(?<e>))*', {}, [("W", "a")], ("e",), ["HOLDS e = ``"])
pa("L1", r'(?:(?<h>\d);)*(?C"c")', h5, [("W", "7;3;"), ("S", "7;3;"), ("F", "7;3; 3;7;")], ("h",),
   ["HOLDS h = `3`", "`7;3;`@0 h = `3`", "[`7;3;`@0 h = `3`, `3;`@5 h = `3`]"])
REP = r"(?:(?<h>\d)?;)*"
pa("R13;;", REP + '(?C"c")', h5, [("W", "3;;"), ("S", "3;;")], ("h",), ["FAILS", "`3;`@0 h = `3`"])
pa("R23;;", REP + '(?C"c")', nh5, [("W", "3;;"), ("S", "3;;"), ("F", "3;7; 7;; 3;")], ("h",),
   ["HOLDS h = unset", "`3;;`@0 h = unset", "[`3;7;`@0 h = `7`, ``@4 h = unset, `7;;`@5 h = unset, ``@8 h = unset, ``@9 h = unset, `;`@10 h = unset, ``@11 h = unset]"])
pa("R37;;", REP + '(?C"c")', {"c": lambda v: v.lab("h") is not None and not lt(5)(v.lab("h"))}, [("W", "7;;"), ("S", "7;;"), ("F", "3;7; 7;; 3;")], (),
   ["FAILS", "`7;`@0", "[`3;7;`@0, `7;`@5]"])
pa("Ib", r"(?:" + ITEM + r")+", h5, [("W", "3;;")], (), ["FAILS"])
pa("VP", r'(?:(?<h>\d);(?C"c"))+', h5, [("W", "3;"), ("S", "3;7;"), ("F", "3;1; 7;")], (), ["HOLDS", "`3;`@0", "[`3;1;`@0]"])
pa("SO", REP + '(?C"c")', {"c": lambda v: any(lt(5)(p.get("h")) for p in v.passes("h"))}, [("W", "3;;"), ("S", "7;3;;"), ("F", "7;; 3;;")], (),
   ["HOLDS", "`7;3;;`@0", "[`3;;`@4]"])
pa("SO2", CLOSE + '(?C"c")', {"c": lambda v: any((p.get("h"), p.get("m") or "00") == ("10", "00") for p in v.passes("h"))}, [("W", "9:45,10,")], (), ["HOLDS"])
keq = {"c": lambda v: v.lab("k") is not None and v.lab("k") == v.lab("h")}
pa("PL", r'(?:(?<h>\d);)*(?<k>\d)(?C"c")', keq, [("W", "3;7;7"), ("W", "3;7;3"), ("F", "3;7;7 7;3;3")], (),
   ["HOLDS", "FAILS", "[`3;7;7`@0, `7;3;3`@6]"])
pa("PLo", r'(?:(?<h>\d)?;)*(?<k>\d)(?C"c")', keq, [("W", "7;;7"), ("S", "7;;7"), ("F", "7;;7 3;3")], (), ["FAILS", "FAILS", "[`3;3`@5]"])
pa("U1", r'(?<b>\d+)(?<a>\d)?(?C"c")', {"c": lambda v: lt(5)(v.lab("a"))}, [("W", "12"), ("S", "12"), ("F", "12 1 19 3")], ("a", "b"),
   ["HOLDS a = `2`, b = `1`", "`12`@0 a = `2`, b = `1`", "[`12`@0 a = `2`, b = `1`]"])
pa("Z", r'(?:(?<x>a)|(?<x>b))+', {}, [("W", "abb")], ("x",), ["HOLDS x = `b`"])
OCC = r'(?:[\s\S]*?(?<x>(?<g>a)?b))+[\s\S]*'
pa("OCC", OCC + '(?C"c")', {"c": lambda v: v.lab("g") == "a"}, [("W", "abb")], ("x", "g"), ["HOLDS x = `ab`, g = `a`"])
print("A SUMMARY: %d printed lines (each a mode of a text); 244 differs from the printed text on %d%s" % (
    NA, len(NA_DIFF), "".join("\nA   DIFFERS %s %s `%s`: 244 %s ; printed %s" % d for d in NA_DIFF)))
print()

# ======================================================================================================== PART B
print("== PART B: rule 244 vs rule 243 over the pools (reported row, labels compared; WHOLE / SEARCHED / FIND-ALL), and the")
print("   carry-vs-rule counts rev 24.3 printed, recomputed by THIS engine under 243 and 244 (a check of the engine itself)")
POOLS = {"A37": strings("37qx", 5), "RG3": strings("37;", 5), "NP": strings("37;,", 5), "LP3": lists(["10:00,", "9:00,", "11:00,", "9:45,", "10,"], 3),
         "JP": lists(["9:45,", "10,", "10:45,", "9,"], 3), "TM": lists(["9,", "10,", "9:15,", "9:45,", "10:15,"], 3)}
def pb(tag, src, conds, pool, printed_carry=None):
    p4, p3, pc = (mk(src, conds, r) for r in ("244", "243", "carry"))
    d43 = D3(p4, p3, POOLS[pool])
    line = "B %-6s %s on %s: 244 vs 243 %s" % (tag, src, pool, fmt3(d43))
    ok = d43[0] == [0, 0, 0]
    if printed_carry:
        dc4 = D3(pc, p4, POOLS[pool]); dc3 = D3(pc, p3, POOLS[pool])
        line += " ; carry vs 244 %s ; carry vs 243 %s ; rev 24.3 printed %s" % (fmt3(dc4), fmt3(dc3), printed_carry)
        ok = ok and "%d / %d / %d" % tuple(dc3[0]) == printed_carry and dc4[0] == dc3[0]
    print(line + " ; " + check("B %s" % tag, ok))
pb("S1", S1, {"c": lambda v: lt(5)(v.lab("a"))}, "A37", "28 / 40 / 40")
pb("REP", REP + '(?C"c")', h5, "RG3", "8 / 33 / 33")
pb("ITEM", r"(?:" + ITEM + r")+", h5, "RG3", "5 / 34 / 34")
pb("LATE", LATE, lc, "LP3", "4 / 7 / 11")
pb("NEST", NEST + '(?C"c")', h5, "NP", "10 / 20 / 20")
pb("Ni", r"(?:(?:" + ITEM + r")*,)*", h5, "NP")
pb("Nii", r'(?:(?:(?<h>\d)?;)*(?C"c"),)*', h5, "NP")
pb("CLOSE", CLOSE + '(?C"c")', {"c": lambda v: jeq(v)}, "JP")
pb("CLOSE0", CLOSE + '(?C"c")', {"c": hour}, "JP")
pb("REPnot", REP + '(?C"c")', nh5, "RG3")
pb("X2", NEST + '(?C"c")', {"c": occ_none(lambda x: not lt(5)(x), "h")}, "NP")
pb("X2b", NEST + '(?C"c")', {"c": idx("h", 2, lt(5))}, "NP")
pb("SO", REP + '(?C"c")', {"c": lambda v: any(lt(5)(p.get("h")) for p in v.passes("h"))}, "RG3")
pb("PLo", r'(?:(?<h>\d)?;)*(?<k>\d)(?C"c")', keq, "RG3")
pb("ALT", r'(?:(?<a>\d)|(?<b>[a-z]))*(?C"c")', {"c": lambda v: lt(5)(v.lab("a"))}, "A37")
pb("TML", r'(?:(?<h>\d{1,2})(?::(?<m>\d\d))?,)*(?C"c")', {"c": lambda v: late(v.lab("h"), v.lab("m"))}, "TM")
print()

# ======================================================================================================== PART C
print("== PART C: where 244 and 243 PART: a condition in a pass placed BEFORE its label's group (no branching inside the body")
print("   around the group). 244: the loop resets once, on entry; a pass sees the previous pass's value until its own group")
print("   closes. 243: every pass starts with its labels unset.")
PS = r'(?:(?C"c")(?<h>\d);)*'
ng5 = {"c": lambda v: not (num(v.lab("h")) and int(v.lab("h")) >= 5)}
for rule in ("244", "243", "carry"):
    p = mk(PS, ng5, rule)
    print("C %-5s `/(?:${c}(?<h>\\d);)*/`, c := NOT (h: >= 5) at the pass start: WHOLE `3;7;` %s ; `7;3;` %s ; `3;3;` %s ; SEARCHED `7;3;` %s ; FIND-ALL `7;3; 3;3;` %s" % (
        rule, W_(p, "3;7;"), W_(p, "7;3;"), W_(p, "3;3;"), S_(p, "7;3;"), F_(p, "7;3; 3;3;")))
d = D3(mk(PS, ng5, "244"), mk(PS, ng5, "243"), POOLS["RG3"])
print("C 244 vs 243 on that program: %s ; %s" % (fmt3(d), check("C pass-start differs (expected NONZERO: a new answer)", d[0] != [0, 0, 0])))
PS2 = r'(?:(?C"c")(?<h>\d)?;)*'
d2 = D3(mk(PS2, ng5, "244"), mk(PS2, ng5, "243"), POOLS["RG3"])
print("C with the group OPTIONAL, `/(?:${c}(?<h>\\d)?;)*/`: 244 vs 243 %s (the optional resets h only when it is entered, AFTER c)" % fmt3(d2))
PS3 = r'(?:(?:(?C"c")(?<h>\d);|x))*'
d3 = D3(mk(PS3, ng5, "244"), mk(PS3, ng5, "243"), strings("37;x", 5))
print("C inside an alternation in the body, `/(?:(?:${c}(?<h>\\d);|x))*/`: 244 vs 243 %s (the alternation resets on entry, before c)" % fmt3(d3))
print("C %s" % check("C alternation-in-body agrees", d3[0] == [0, 0, 0]))
print()

# ======================================================================================================== PART N
print("== PART N: NEW answers of the one rule (WHOLE; SEARCHED / FIND-ALL where named); each beside rev 24.3's rule (243),")
print("   PCRE's capture (carry) and libpcre2 itself under (?J) (duplicate names allowed; the capture PCRE2 reads)")
import ctypes
P.L.pcre2_substring_get_byname_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(P.SIZE)]
def pcre_dup(pat, s, name):
    """libpcre2 under (?J): the value PCRE2 gives for the NAME (pcre2_substring_get_byname) and each group's capture"""
    pb = ("(?J)" + pat).encode(); err, off = ctypes.c_int(0), P.SIZE(0)
    code = P.L.pcre2_compile_8(pb, len(pb), P.BASE_OPTS, ctypes.byref(err), ctypes.byref(off), None)
    md = P.L.pcre2_match_data_create_from_pattern_8(code, None)
    sb = s.encode()
    rc = P.L.pcre2_match_8(code, sb, len(sb), 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED, md, None)
    if rc < 0: return "no match"
    ov = P.L.pcre2_get_ovector_pointer_8(md)
    groups = ["`%s`" % s[ov[2 * g]:ov[2 * g + 1]] if g < rc and ov[2 * g] != P.UNSET else "unset" for g in range(1, pat.count("(?<") + 1)]
    buf, ln = ctypes.c_void_p(), P.SIZE(0)
    r2 = P.L.pcre2_substring_get_byname_8(md, name.encode(), ctypes.byref(buf), ctypes.byref(ln))
    byname = ("`%s`" % ctypes.string_at(buf, ln.value).decode()) if r2 == 0 else "unset"
    return "by name h = %s (groups %s)" % (byname, ", ".join(groups))
def pcre_nodup(pat):
    try: P.Pcre(pat); return "compiles"
    except ValueError as e: return "COMPILE ERROR: %s" % str(e).split(": ", 1)[-1]
NEW = [("N1", r"(?<h>\d)?;(?<h>\d)?", ["3;", "3;4", ";4"]),
       ("N2", r"(?<h>\d)?(?:;(?<h>\d)?)*", ["3;", "7;3;", "7;3", "3"]),
       ("N3", r"(?<h>\d)(?:,(?<h>\d))*", ["7", "7,3", "7,3,5"]),
       ("N4", r"(?<h>\d);(?:(?<h>\d)|x)", ["3;x", "3;4"]),
       ("N5", r"(?<h>\d);(?:x|(?<h>\d))", ["3;x", "3;4"])]
EXPECT = {("N1", "3;"): "unset", ("N2", "3;"): "unset", ("N2", "7;3;"): "unset", ("N2", "7;3"): "`3`", ("N2", "3"): "unset",
          ("N3", "7"): "unset", ("N3", "7,3"): "`3`", ("N4", "3;x"): "unset", ("N5", "3;x"): "unset"}
for tag, pat, texts in NEW:
    print("N %s `/%s/`: without (?J) libpcre2: %s" % (tag, pat, pcre_nodup(pat)))
    for t in texts:
        res = {r: W_(mk(pat, {}, r), t, ("h",)) for r in RULES}
        e = EXPECT.get((tag, t))
        ok = "" if e is None else " ; " + check("N %s %s" % (tag, t), res["244"] == "HOLDS h = %s" % e)
        print("N %s   on `%s`: 244 %s ; 243 %s ; carry %s ; libpcre2 (?J) %s%s" % (tag, t, res["244"], res["243"], res["carry"], pcre_dup(pat, t, "h"), ok))
p = mk(r'(?<h>\d)(?:,(?<h>\d))*(?C"c")', {"c": lambda v: v.lab("h") is not None})
print("N N3 with `& (h: present)`, the items-then-last form against the two-copy list: two-copy `7` %s / SEARCHED `7 7,3` %s / FIND-ALL `7 7,3` %s" % (
    W_(p, "7"), S_(p, "7 7,3", ("h",)), F_(p, "7 7,3", ("h",))))
q = mk(r'(?:(?<h>\d),)*(?<h>\d)(?C"c")', {"c": lambda v: v.lab("h") is not None})
print("N N3' items-then-last `/(?:(?<h>\\d),)*(?<h>\\d)/` (the last item outside the loop): `7` %s ; `7,3` %s ; SEARCHED `7 7,3` %s" % (W_(q, "7", ("h",)), W_(q, "7,3", ("h",)), S_(q, "7 7,3", ("h",))))
print("N array form on N2 `7;;3;`: settings in order %s ; with a slot for each reset after a setting %s (the open question **array-slot**)" % (
    mk(r"(?<h>\d)?(?:;(?<h>\d)?)*").whole("7;;3;")[2] and View(None, "", 0, 0, mk(r"(?<h>\d)?(?:;(?<h>\d)?)*").whole("7;;3;")[2]).array("h"),
    View(None, "", 0, 0, mk(r"(?<h>\d)?(?:;(?<h>\d)?)*").whole("7;;3;")[2]).array("h", True)))
st = mk(r"(?<h>\d)?(?:;(?<h>\d)?)*").whole("7;3;")[2]
print("N array form on N2 `7;3;`: %s (label: unset) ; on REP `3;;7;`: %s (label: `7`)" % (
    View(None, "", 0, 0, st).array("h"), View(None, "", 0, 0, mk(REP).whole("3;;7;")[2]).array("h")))
print()

# ======================================================================================================== PART L
print("== PART L: THE SEPARATED LIST (rulings file R1, R2: the worked example of the label rule), each form on `7`, `7,3,5`")
print("   and `7,3,` (no last item), WHOLE: the label after the pattern and the ARRAY form (every setting of the name, in")
print("   order); then with a CONDITIONED item (item := (?<h>\\d) & (h: <5), the condition inside the item, every item)")
LFORMS = [("(a) items-then-last", r"(?:(?<h>\d),)*(?<h>\d)"), ("(b) first-then-rest", r"(?<h>\d)(?:,(?<h>\d))*"),
          ("(c1) his sketch over (a): list | item", r"(?:(?:(?<h>\d),)*(?<h>\d)|(?<h>\d))"),
          ("(c2) his sketch over (b): list | item", r"(?:(?<h>\d)(?:,(?<h>\d))*|(?<h>\d))"),
          ("(c3) his sketch, list of two or more | item", r"(?:(?<h>\d)(?:,(?<h>\d))+|(?<h>\d))")]
LEXP = {("(a) items-then-last", "7"): ("`7`", ["7"]), ("(a) items-then-last", "7,3,5"): ("`5`", ["7", "3", "5"]),
        ("(b) first-then-rest", "7"): ("unset", ["7"]), ("(b) first-then-rest", "7,3,5"): ("`5`", ["7", "3", "5"])}
for nm, pat in LFORMS:
    for rule in ("244", "243"):
        p = mk(pat, {}, rule); cells = []
        for t in ("7", "7,3,5", "7,3,"):
            ok, labs, st = p.whole(t)
            if not ok: cells.append("`%s` FAILS" % t); continue
            lab = "`%s`" % labs["h"] if labs["h"] is not None else "unset"; arr = View(p, t, 0, len(t), st).array("h")
            e = LEXP.get((nm, t)) if rule == "244" else None
            cells.append("`%s` label %s, array %s%s" % (t, lab, arr, "" if e is None else " " + check("L %s %s" % (nm, t), (lab, arr) == e)))
        print("L %-44s %s `/%s/`: %s" % (nm, rule, pat, " ; ".join(cells)))
for nm, pat in LFORMS[:2]:
    cpat = pat.replace(r"(?<h>\d)", r'(?<h>\d)(?C"c")')
    p = mk(cpat, h5)
    cells = []
    for t in ("3", "3,1,4", "3,7,1", "7"):
        ok, labs, st = p.whole(t)
        cells.append("`%s` %s" % (t, ("HOLDS label %s, array %s" % ("`%s`" % labs["h"] if labs["h"] is not None else "unset", View(p, t, 0, len(t), st).array("h"))) if ok else "FAILS"))
    print("L %s, conditioned item (every item < 5): %s ; SEARCHED `7,3,1` %s ; FIND-ALL `3,7,1 2` %s" % (nm, " ; ".join(cells), S_(p, "7,3,1", ("h",)), F_(p, "3,7,1 2", ("h",))))
print()

# ======================================================================================================== PART M
print("== PART M: the MARKER MODEL on libpcre2 (labels under the one rule) vs the engine's rule 244, reported row with labels;")
print("   and the ORDER CHECK: the same pattern with NO markers (PCRE's capture) must DIFFER where a branching resets")
def label_from(ctx, copies, markers):
    best = None
    for c in copies:
        sp = ctx.span(c)
        if sp is not None and (best is None or sp[1] > best[1][1]): best = (c, sp)
    if best is None: return None
    for mm in markers:
        sp = ctx.span(mm)
        if sp is not None and sp[0] >= best[1][1]: return None
    return ctx.subject[best[1][0]:best[1][1]]
class MRx:
    """a libpcre2 pattern whose label(s) are computed at the final callout from copies and markers"""
    def __init__(self, pat, spec, test, use_markers=True):
        self.spec, self.test, self.use = spec, test, use_markers
        self.last = None
        self.rx = P.Pcre(pat, {"t": self._t})
    def _t(self, ctx):
        labs = {n: label_from(ctx, cp, mk_ if self.use else ()) for n, (cp, mk_) in self.spec.items()}
        if self.test(labs): self.last = labs; return True
        return False
    def match(self, s, pos, opts=0):
        self.last = None
        r = self.rx.match(s, pos, opts)
        return None if r is None else (r[0], r[1], dict(self.last))
def mrow(mr, s, mode):
    if mode == "W":
        r = mr.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
        return (r is not None, tuple(sorted(r[2].items())) if r else ())
    if mode == "S":
        r = mr.match(s, 0); return None if r is None else (r[0], r[1], tuple(sorted(r[2].items())))
    out, pos, ne = [], 0, False
    while pos <= len(s):
        r = mr.match(s, pos, (0x00000008 | P.PCRE2_ANCHORED) if ne else 0)
        if r is None:
            if ne: pos += 1; ne = False; continue
            break
        out.append((r[0], r[1], tuple(sorted(r[2].items())))); ne = r[1] == r[0]; pos = r[1]
    return tuple(out)
def erow(p, s, mode):
    r = row(p, s, mode, True)
    if mode == "W": return (r[0], r[1] if r[0] else ())
    return r
def mcmp(tag, epat, conds, mpat, spec, test, pool, expect_order_diff):
    pe = mk(epat, conds, "244")
    m1, m0 = MRx(mpat, spec, test, True), MRx(mpat, spec, test, False)
    out, out0 = [], []
    for mode in "WSF":
        n = n0 = 0
        for s in POOLS[pool] if isinstance(pool, str) else pool:
            e = erow(pe, s, mode)
            n += mrow(m1, s, mode) != e
            n0 += mrow(m0, s, mode) != e
        out.append(n); out0.append(n0)
    N = len(POOLS[pool] if isinstance(pool, str) else pool)
    ok = out == [0, 0, 0] and ((sum(out0) > 0) == expect_order_diff)
    print("M %-5s model `%s` vs engine 244: %d / %d / %d of %d ; without markers (the capture) %d / %d / %d (expected %s) ; %s" % (
        tag, mpat, out[0], out[1], out[2], N, out0[0], out0[1], out0[2], "to differ" if expect_order_diff else "equal", check("M %s" % tag, ok)))
T = lambda f: f
mcmp("S1", S1, {"c": lambda v: lt(5)(v.lab("a"))},
     r'(?<e1>)(?:(?<e2>)(?:(?<a1>\d)|(?<b1>[a-z])))*xx(?C"t")', {"a": (("a1",), ("e1", "e2")), "b": (("b1",), ("e1", "e2"))},
     lambda L: lt(5)(L["a"]), "A37", True)
mcmp("REP", REP + '(?C"c")', h5, r'(?<e1>)(?:(?<e2>)(?<h1>\d)?;)*(?C"t")', {"h": (("h1",), ("e1", "e2"))}, lambda L: lt(5)(L["h"]), "RG3", True)
mcmp("NEST", NEST + '(?C"c")', h5, r'(?<e1>)(?:(?<e2>)(?:(?<e3>)(?<h1>\d)?;)*,)*(?C"t")', {"h": (("h1",), ("e1", "e2", "e3"))},
     lambda L: lt(5)(L["h"]), "NP", True)
mcmp("CLOSE", CLOSE + '(?C"c")', {"c": lambda v: jeq(v)}, r'(?<e1>)(?:(?<h1>\d+)(?<e2>)(?::(?<m1>\d\d))?,)*(?C"t")',
     {"h": (("h1",), ("e1",)), "m": (("m1",), ("e1", "e2"))}, lambda L: (L["h"], L["m"]) == ("10", "45"), "JP", True)
mcmp("N2", r'(?<h>\d)?(?:;(?<h>\d)?)*(?C"c")', {"c": lambda v: lt(5)(v.lab("h"))},
     r'(?<e1>)(?<h1>\d)?(?<e2>)(?:;(?<e3>)(?<h2>\d)?)*(?C"t")', {"h": (("h1", "h2"), ("e1", "e2", "e3"))}, lambda L: lt(5)(L["h"]), "RG3", True)
mcmp("N1", r'(?<h>\d)?;(?<h>\d)?(?C"c")', {"c": lambda v: lt(5)(v.lab("h"))},
     r'(?<e1>)(?<h1>\d)?;(?<e2>)(?<h2>\d)?(?C"t")', {"h": (("h1", "h2"), ("e1", "e2"))}, lambda L: lt(5)(L["h"]), "RG3", True)
mcmp("N3", r'(?<h>\d)(?:,(?<h>\d))*(?C"c")', {"c": lambda v: v.lab("h") is not None},
     r'(?<h1>\d)(?<e1>)(?:,(?<h2>\d))*(?C"t")', {"h": (("h1", "h2"), ("e1",))}, lambda L: L["h"] is not None, strings("37,", 5), True)
mcmp("N4", r'(?<h>\d);(?:(?<h>\d)|x)(?C"c")', {"c": lambda v: True},
     r'(?<h1>\d);(?<e1>)(?:(?<h2>\d)|x)(?C"t")', {"h": (("h1", "h2"), ("e1",))}, lambda L: True, strings("37;x", 4), True)
mcmp("N5", r'(?<h>\d);(?:x|(?<h>\d))(?C"c")', {"c": lambda v: True},
     r'(?<h1>\d);(?<e1>)(?:x|(?<h2>\d))(?C"t")', {"h": (("h1", "h2"), ("e1",))}, lambda L: True, strings("37;x", 4), True)
mcmp("U1", r'(?<b>\d+)(?<a>\d)?(?C"c")', {"c": lambda v: lt(5)(v.lab("a"))},
     r'(?<b1>\d+)(?<e1>)(?<a1>\d)?(?C"t")', {"a": (("a1",), ("e1",)), "b": (("b1",), ())}, lambda L: lt(5)(L["a"]), strings("129 ", 4), False)
cap_eq = 0
for s in POOLS["RG3"]:
    for mode in "WSF":
        cap_eq += erow(mk(REP + '(?C"c")', h5, "carry"), s, mode) != mrow(MRx(r'(?:(?<h1>\d)?;)*(?C"t")', {"h": (("h1",), ())}, lambda L: lt(5)(L["h"]), False), s, mode)
print("M CAPTURES: rule carry vs plain libpcre2 on REP & (h: <5), 364 texts x 3 modes: %d differ ; %s" % (cap_eq, check("M carry = libpcre2", cap_eq == 0)))
print()

# ======================================================================================================== PART H
print("== PART H: the HIT LIST on libpcre2 10.46 (the manager's run of the evening, re-run): whole values; 'every number")
print("   under 100'. The hits are recorded by a callout as a stack (an entry is dropped when the match backs up past it)")
def hitrun(pat, s):
    hits = []
    def rec(c):
        sp = c.span("n")
        while hits and hits[-1][0] >= sp[0]: hits.pop()
        hits.append(sp); return True
    judged = {}
    def judge(c):
        ok = all(int(c.subject[a:b]) < 100 for a, b in hits)
        judged["h"] = [c.subject[a:b] for a, b in hits]; return ok
    def inside(c):
        sp = c.span("n"); return int(c.subject[sp[0]:sp[1]]) < 100
    r = P.Pcre(pat, {"rec": rec, "judge": judge, "in": inside})
    m = r.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
    if m is None: return "FAILS%s" % (" (last list judged %s)" % judged["h"] if "h" in judged else "")
    return "HOLDS%s" % (" hits %s" % judged["h"] if "h" in judged else " (n = `%s`)" % m[2]["n"])
HT = ("1234", "12 34", "12 345", "x300 12")
EXPH = {r'\A(?>(?:.*?(?<n>\d+)(?C"rec"))*\D*)\z(?C"judge")': ["FAILS", "HOLDS", "FAILS", "FAILS"]}
for nm, pat in (("judged inside (the search as part of the pattern)", r'\A(?:.*?(?<n>\d+)(?C"in"))*\D*\z'),
                ("FIRST TRY: each hit atomic, the list judged after", r'\A(?:.*?(?>(?<n>\d+))(?C"rec"))*\D*\z(?C"judge")'),
                ("THE MODEL: the whole loop atomic, anchored at both ends, the list judged after", r'\A(?>(?:.*?(?<n>\d+)(?C"rec"))*\D*)\z(?C"judge")'),
                ("the model with the general tail `[\\s\\S]*`", r'\A(?>(?:[\s\S]*?(?<n>\d+)(?C"rec"))*[\s\S]*)\z(?C"judge")')):
    res = [hitrun(pat, t) for t in HT]
    e = EXPH.get(pat)
    print("H %s `%s`: %s%s" % (nm, pat, " ; ".join("`%s` %s" % (t, r) for t, r in zip(HT, res)),
                                "" if e is None else " ; " + check("H model", [r.split()[0] for r in res] == e)))
HAT = r'\A(?>(?:[\s\S]*?(?<n>\d+))*[\s\S]*)\z(?C"c")'
hc = {"c": lambda v: all(lt(100)(p.get("n")) for p in v.passes("n"))}
ph = mk(HAT, hc)
print("H the engine (rule 244, the atomic group and the pass table): %s ; SEARCHED `x300 12` %s (standing alone it reads the whole subject) ; FIND-ALL `12 34` %s" % (
    " ; ".join("`%s` %s" % (t, W_(ph, t)) for t in HT), S_(ph, "x300 12"), F_(ph, "12 34")))
print("H %s" % check("H engine = libpcre2 model", [W_(ph, t) for t in HT] == ["FAILS", "HOLDS", "FAILS", "FAILS"]))
HG = r'\A(?>(?:[\s\S]*?a(?<g>x)?)*[\s\S]*)\z(?C"c")'
pg = mk(HG, {"c": lambda v: v.lab("g") == "x"})
print("H `hits(/a(?<g>x)?/) & (g: \"x\")` (the last hit's own g): `axa` %s ; `aax` %s ; SEARCHED `axa` %s (rev 24.3 printed `ax`@0: the hits of the stretch)" % (
    W_(pg, "axa", ("g",)), W_(pg, "aax", ("g",)), S_(pg, "axa", ("g",))))
print()

# ======================================================================================================== PART F
print("== PART F: the FILTER SENTENCE ('the filter is matched against the stretch as if the stretch were the whole text')")
print("   and THE DRAFT'S READING of 'any piece that might look outside' (refused at compile time): `\\b`/`\\B` that can")
print("   sit at an edge of the operand, a lookbehind that can reach before its start, a lookahead that can reach past its")
print("   end, `\\G`, `\\K`. Anchors `^ $ \\A \\z \\Z` are ALLOWED (they are the stretch's ends). A classifier over the operand:")
def classify(op):
    toks = re.findall(r"\\[bBGK]|\(\?<[=!]|\(\?[=!]|\\[Az Z]|[\^$]", op)
    # edge analysis by min lengths around each token (a small, conservative reading for these operands)
    def minlen(x):
        x = re.sub(r"\\[bBGKAzZ]|[\^$]", "", x)
        x = re.sub(r"\(\?<?[=!][^)]*\)", "", x)
        if x == "": return 0
        try: return min(len(m) for m in ("1", "11") if re.fullmatch(x, m) or False) if False else (0 if re.fullmatch(x, "") else 1)
        except re.error: return 1
    for m in re.finditer(r"\\[GK]", op): return "REFUSED (`%s`: speaks about the search, not the string)" % m.group(0)
    for m in re.finditer(r"\\[bB]", op):
        before, after = op[:m.start()], op[m.end():]
        if minlen(before) == 0 or minlen(after) == 0: return "REFUSED (`%s` can sit at an edge of the operand)" % m.group(0)
    for m in re.finditer(r"\(\?<[=!]([^)]*)\)", op):
        if minlen(op[:m.start()]) == 0: return "REFUSED (a lookbehind that can reach before the operand's start)"
    for m in re.finditer(r"\(\?[=!]([^)]*)\)", op):
        if minlen(op[m.end():]) == 0: return "REFUSED (a lookahead that can reach past the operand's end)"
    return "ALLOWED"
def amp(left, right_src, s, mode):
    """`left & right`: left's paths, kept when right matches the stretch WHOLE as its own text (the filter sentence)"""
    rp = mk(right_src)
    lp = mk(left + '(?C"amp")', {"amp": lambda v: rp.whole(v.s[v.start:v.pos])[0]})
    return {"W": W_, "S": S_, "F": F_}[mode](lp, s)
for op in (r"^\d$", r"\A\d\z", r"\d+$", r"^1", r"\b\d+", r"\d+\b", r"\B\d+", r"1\b2", r"(?<=a)\d+", r"\d(?<=1)\d", r"\d+(?![a-z])", r"\d(?=2)\d", r"\G\d+", r"\d\K\d*"):
    c = classify(op)
    extra = ""
    if c == "ALLOWED" and "\\Z" not in op:
        extra = " ; `/\\d+/ & /%s/`: WHOLE `12` %s, SEARCHED `a12 1` %s, FIND-ALL `12 1 21` %s" % (op, amp(r"\d+", op, "12", "W"), amp(r"\d+", op, "a12 1", "S"), amp(r"\d+", op, "12 1 21", "F"))
    print("F `%s`: %s%s" % (op, c, extra))
print("F %s" % check("F refusals", [classify(o).split()[0] for o in (r"\b\d+", r"\B\d+", r"(?<=a)\d+", r"\d+(?![a-z])", r"\G\d+", r"\d\K\d*", r"^\d$", r"1\b2", r"\d(?<=1)\d", r"\d(?=2)\d")] ==
                                   ["REFUSED"] * 6 + ["ALLOWED"] * 4))
print()

# ======================================================================================================== PART J
print("== PART J: join order (left side decides) and zero-place (numbers are the pattern's own groups), re-run")
G_, L_ = r"(?<a>\d+)", r"(?<c>\d+?)"
def amp2(lsrc, rsrc, s, mode):
    rp = mk(rsrc)
    lp = mk(lsrc + '(?C"amp")', {"amp": lambda v: rp.whole(v.s[v.start:v.pos])[0]})
    return {"W": W_, "S": S_, "F": F_}[mode](lp, s)
print("J `G & L` (left decides): SEARCHED `11` %s ; `L & G`: %s (rev 24.3 printed `11`@0 vs `1`@0) ; %s" % (
    amp2(G_, L_, "11", "S"), amp2(L_, G_, "11", "S"), check("J join order", (amp2(G_, L_, "11", "S"), amp2(L_, G_, "11", "S")) == ("`11`@0", "`1`@0"))))
print("J zero-place: in `/\\d+/ & (0: /1\\d*/)` the `0` of the right side is the stretch (its world): SEARCHED ` 1` %s ; FIND-ALL ` 1 12 21` %s" % (
    amp2(r"\d+", r"1\d*", " 1", "S"), amp2(r"\d+", r"1\d*", " 1 12 21", "F")))
print()

# ======================================================================================================== PART S
print("== PART S: shared-label re-examined: a label named in BOTH operands of `&`, read by a condition after the chain.")
print("   Candidates: ERROR (the draft, §4.1); LEFT (the left operand's setting stands); LAST MENTION in the reporting order")
print("   (left then right: the right operand's setting, which is unset when the right operand's own branching reset it)")
def shared(lsrc, rsrc, cand, test):
    rp = mk(rsrc)
    def amp_(v):
        ok, rl, _ = rp.whole(v.s[v.start:v.pos])
        if not ok: return False
        lab = v.lab("h") if cand == "LEFT" else rl["h"]
        return test(lab)
    return mk(lsrc + '(?C"amp")', {"amp": amp_})
for lsrc, rsrc in ((r"(?<h>\d)\d", r"\d(?<h>\d)"), (r"(?<h>\d)\d", r"\d(?<h>[a-z])?\d")):
    cells = []
    for cand in ("LEFT", "LAST"):
        q = shared(lsrc, rsrc, cand, lt(2))
        cells.append("%s: WHOLE `12` %s, `21` %s ; SEARCHED `21 12` %s ; FIND-ALL `12 21 10` %s" % (cand, W_(q, "12"), W_(q, "21"), S_(q, "21 12"), F_(q, "12 21 10")))
    print("S `/%s/ & /%s/ & (h: <2)`: ERROR: REJECTED ; %s" % (lsrc, rsrc, " ; ".join(cells)))
d = D3(shared(r"(?<h>\d)\d", r"\d(?<h>\d)", "LEFT", lt(2)), shared(r"(?<h>\d)\d", r"\d(?<h>\d)", "LAST", lt(2)), strings("012 ", 4), keys=False)
print("S LEFT vs LAST on the first pair, holds and stretch: %s" % fmt3(d))
print()

# ======================================================================================================== PART D
print("== PART D: the review drills, under 244 (and 243 beside it)")
def both(tag, src, conds, texts, keys=()):
    for rule in ("244", "243"):
        p = mk(src, conds, rule)
        print("D %-28s %s: %s" % (tag, rule, " ; ".join("%s `%s` %s" % (m, t, {"W": W_, "S": S_, "F": F_}[m](p, t, keys)) for m, t in texts)))
both("optional label, looped place", REP + '(?C"c")', h5, [("W", "3;;"), ("W", "3;;7;"), ("S", "7;;3;"), ("F", "3;; 3;")], ("h",))
both("a label at two loop depths", NEST + '(?C"c")', h5, [("W", "3;,,"), ("W", "7;,3;,"), ("S", "3;,, 7;,")], ("h",))
both("a place inside a place (ii)", r'(?:(?:(?<h>\d)?;)*(?C"c"),)*', h5, [("W", "3;,,"), ("W", "3;,"), ("S", "3;,, 7;,")], ("h",))
both("a nullable loop body", r'(?:(?<h>\d)?)*(?C"c")', nh5, [("W", "3"), ("W", ""), ("S", "3"), ("F", "3")], ("h",))
both("duplicate name across a loop", r'(?<h>\d)?(?:;(?<h>\d)?)*(?C"c")', {"c": lambda v: v.lab("h") is None}, [("W", "3"), ("W", "3;"), ("W", "3;4")], ("h",))
print("D anchored / \\b / lookahead operand: PART F (refused or allowed, by THE DRAFT'S READING)")
print()

# ======================================================================================================== CHECKS
ok = sum(1 for _, v in CHECKS if v)
print("== CHECKS: %d of %d OK%s" % (ok, len(CHECKS), "" if ok == len(CHECKS) else " ; FAILED: " + ", ".join(n for n, v in CHECKS if not v)))
