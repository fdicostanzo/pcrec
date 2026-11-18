#!/usr/bin/env python3
# Lane predspec25 (2026-11-17): the evidence engine of docs/design/predicates_draft.md REVISION 25 (the owner's rulings
# of the evening of 2026-11-17 from COND-FAMILY's entry "OWNER RULING — pass-start-read" to the end of the file: the
# label rulings, the warnings set, numbers naming groups, and the rx module). DESIGN EVIDENCE ONLY; rules nothing.
#
# HOW: lane predspec244's engine (docs/dev/lanes/predspec244_evidence/predspec244_model.py, never edited) is LOADED IN
# MEMORY: its text up to its first print (the parser, the path enumerator with the ONE LABEL RULE "244", rev 24.3's
# rule "243" and PCRE's capture "carry", the mode helpers) is executed here unpatched. On top of it:
#   - an EXPANDER for the rx-module surface (placeholder marks: `SEQ` for the sequence operator, the nine postfix
#     quantifier operators, `&` with a condition `@c`, `|`, `[n = E]` for a labelled part, parentheses), written from
#     the ruled sentences: postfix tightest, then SEQ, then `&`, then `|`; SEQ a splice; every operand one
#     non-capturing group; operators read longest first;
#   - an INSTANTIATOR for holes in value positions (a count, a group name): the literal is copied once per
#     combination of members (the cartesian product, first hole slowest), a combination that is not a legal pattern
#     REMOVED (legality = libpcre2 compiles it);
#   - a NUMBERING step for the label-number trial: plain capturing groups get the names _1, _2, ... by their opening
#     parenthesis (named groups keep their name; their number is an alias).
# CONTROLS (no construction shared with what they check):
#   - libpcre2-8 (installed; run through ../rxmodel_evidence/pcre2h.py, never read: D181) on HAND-WRITTEN regex text,
#     written from the draft's rule sentences, against the expander's output and the engine;
#   - Python `re` as an intent oracle where a program has no labels (string sets);
#   - THE STATIC-ORDER MODEL for labels in loop-free patterns: each label group renamed (h1, h2, ...) and an empty
#     capture before each branching that contains the name; plain libpcre2 captures; the label = the item LAST IN
#     PATTERN ORDER among those set (a marker = unset). Unlike predspec244's marker model it compares pattern order,
#     not text positions, so it is exact where a lookahead sets a label at a later text position (loop-free only).
#
# Run (W = the worktree; from $PCREC_TMPDIR/scratch/predspec25; one process, well under a minute):
#   timeout 1800 python3 -I -B W/docs/dev/lanes/predspec25_evidence/predspec25_model.py > fwd.out
#   PREDSPEC25_SABOTAGE=1   deliberately wrong rules: the sequence operator LOOSER than `|` and a postfix operator
#                           binding the whole sequence chain before it; two count arguments read as the UNION of their
#                           members (the note's C1) instead of the product; a hole in a count position read as an
#                           inner alternation; a condition in a loop body reads labels under rev 24.3's per-pass reset.
#                           The checks must fail.
import os, sys, re, itertools, ctypes

HERE = os.path.dirname(os.path.abspath(__file__))
SRC244 = os.path.join(os.path.dirname(HERE), "predspec244_evidence", "predspec244_model.py")
SAB = os.environ.get("PREDSPEC25_SABOTAGE") == "1"
os.environ["PREDSPEC244_RULES"] = "244"
os.environ.pop("PREDSPEC244_SABOTAGE", None)
_src = open(SRC244).read()
_cut = _src.index('print("predspec244 engine')
E = {"__file__": SRC244, "__name__": "predspec244_defs"}
exec(compile(_src[:_cut], SRC244, "exec"), E)
P, mk, W_, S_, F_, D3, fmt3, strings, num, lt, View, row = (E[k] for k in
    ("P", "mk", "W_", "S_", "F_", "D3", "fmt3", "strings", "num", "lt", "View", "row"))

CHECKS = []
def check(name, ok): CHECKS.append((name, bool(ok))); return "OK" if ok else "FAILED"
PRULE = "243" if SAB else "244"          # the rule a condition in a loop body reads under (sabotage: rev 24.3's)

# ------------------------------------------------------------------------------------------------ libpcre2 helpers
NOTEMPTY_ATSTART = 0x00000008
def fl(labs, keys):
    if not keys: return ""
    return " " + ", ".join("%s = %s" % (k, "`%s`" % labs.get(k) if labs.get(k) is not None else "unset") for k in keys)
class LRx:
    """a libpcre2 pattern; `labels` computes the reported labels at a final callout (or plain captures)"""
    def __init__(self, pat, conds=None, labfn=None):
        self.labfn, self.last = labfn, None
        cs = dict(conds or {})
        if labfn is not None: cs["fin"] = self._fin; pat = pat + '(?C"fin")'
        self.rx = P.Pcre(pat, cs)
    def _fin(self, ctx): self.last = self.labfn(ctx); return True
    def match(self, s, pos, opts=0):
        self.last = None
        r = self.rx.match(s, pos, opts)
        if r is None: return None
        return (r[0], r[1], dict(self.last) if self.labfn is not None else r[2])
def pW(lr, s, keys=()):
    r = lr.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
    return "FAILS" if r is None else "HOLDS" + fl(r[2], keys)
def pS(lr, s, keys=()):
    r = lr.match(s, 0)
    return "FAILS" if r is None else "`%s`@%d%s" % (s[r[0]:r[1]], r[0], fl(r[2], keys))
def pFl(lr, s):
    out, pos, ne = [], 0, False                       # PCRE2's global loop (R.1.2)
    while pos <= len(s):
        r = lr.match(s, pos, (NOTEMPTY_ATSTART | P.PCRE2_ANCHORED) if ne else 0)
        if r is None:
            if ne: pos += 1; ne = False; continue
            break
        out.append(r); ne = r[1] == r[0]; pos = r[1]
    return out
def pF(lr, s, keys=()):
    return "[" + ", ".join("`%s`@%d%s" % (s[a:b], a, fl(l, keys)) for a, b, l in pFl(lr, s)) + "]"
def prow(lr, s, mode, keys):
    if mode == "W":
        r = lr.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
        return (r is not None, tuple((k, r[2].get(k)) for k in keys) if r else ())
    if mode == "S":
        r = lr.match(s, 0); return None if r is None else (r[0], r[1], tuple((k, r[2].get(k)) for k in keys))
    return tuple((a, b, tuple((k, l.get(k)) for k in keys)) for a, b, l in pFl(lr, s))
def pD3(a, b, pool, keys=()):
    """two libpcre2 patterns: texts whose reported row differs per mode"""
    out, first = [], None
    for mode in "WSF":
        n = 0
        for s in pool:
            if prow(a, s, mode, keys) != prow(b, s, mode, keys):
                n += 1; first = first or (mode, s)
        out.append(n)
    return (out, first, len(pool))
def erow(p, s, mode, keys):
    r = row(p, s, mode, True)
    pick = lambda labs: tuple((k, dict(labs).get(k)) for k in keys)
    if mode == "W": return (r[0], pick(r[1]) if r[0] else ())
    if mode == "S": return None if r is None else (r[0], r[1], pick(r[2]))
    return tuple((a, b, pick(l)) for a, b, l in r)
def epD3(p, lr, pool, keys=()):
    """the engine against a libpcre2 pattern"""
    out, first = [], None
    for mode in "WSF":
        n = 0
        for s in pool:
            if erow(p, s, mode, keys) != prow(lr, s, mode, keys):
                n += 1; first = first or (mode, s)
        out.append(n)
    return (out, first, len(pool))
def compiles(pat):
    try: P.Pcre(pat); return None
    except ValueError as e: return str(e).split(": ", 1)[-1]
P.L.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(P.SIZE)
def groups_of(pat, s):
    """libpcre2: every numbered group's text on a WHOLE match (plain PCRE numbering)"""
    pb = pat.encode(); err, off = ctypes.c_int(0), P.SIZE(0)
    code = P.L.pcre2_compile_8(pb, len(pb), P.BASE_OPTS, ctypes.byref(err), ctypes.byref(off), None)
    md = P.L.pcre2_match_data_create_from_pattern_8(code, None)
    sb = s.encode()
    rc = P.L.pcre2_match_8(code, sb, len(sb), 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED, md, None)
    if rc < 0: return None
    ov = P.L.pcre2_get_ovector_pointer_8(md)
    cnt = ctypes.c_uint32(0); P.L.pcre2_pattern_info_8(code, 4, ctypes.byref(cnt))    # PCRE2_INFO_CAPTURECOUNT
    return [None if ov[2 * g] == P.UNSET else s[ov[2 * g]:ov[2 * g + 1]] for g in range(cnt.value + 1)]

# ------------------------------------------------------------------------------------------- the rx-module expander
TOK = re.compile(r'\s*("(?:[^"\\]|\\.)*"|\+\+|\+\?|\*\+|\*\?|\?\+|\?\?|[+*?]|SEQ\b|@\w+|[A-Za-z_][\w.]*|[\[\]=()|&])')
POSTFIX = ("++", "+?", "*+", "*?", "?+", "??", "+", "*", "?")
def tokens(src):
    out, i = [], 0
    while i < len(src.rstrip()):
        m = TOK.match(src, i); assert m, (src, i); out.append(m.group(1)); i = m.end()
    return out
def lit(s):
    return "".join("\\" + c if c in "\\.^$|?*+()[]{}" else c for c in s)
def starts_operand(t): return t is not None and (t[0] == '"' or t in ("[", "(") or re.match(r"[A-Za-z_]", t) and t != "SEQ")
class TypeErr(Exception): pass
class Exp:
    """placeholder rx-module surface -> regex text (the RULED order unless sab)"""
    def __init__(self, env, sab=False): self.env, self.sab = env, sab
    def __call__(self, src):
        self.t, self.i = tokens(src), 0
        r = self.amp_s() if self.sab else self.alt()
        assert self.i == len(self.t), ("trailing", src, self.t[self.i:])
        return r
    def peek(self): return self.t[self.i] if self.i < len(self.t) else None
    def eat(self, x=None):
        t = self.peek(); assert x is None or t == x, (x, t); self.i += 1; return t
    # the ruled order: postfix, SEQ, &, |
    def alt(self):
        br = [self.amp()]
        while self.peek() == "|": self.eat(); br.append(self.amp())
        return br[0] if len(br) == 1 else "(?:" + "|".join(br) + ")"
    def amp(self):
        x = self.seq()
        while self.peek() == "&":
            self.eat(); c = self.eat(); assert c.startswith("@"); x = "(?:%s)(?C\"%s\")" % (x, c[1:])
        return x
    def seq(self):
        parts = [self.post()]
        while self.peek() == "SEQ": self.eat(); parts.append(self.post())
        return parts[0] if len(parts) == 1 else "".join("(?:%s)" % p for p in parts)
    def post(self):
        x = self.prim()
        while self.peek() in POSTFIX:
            op = self.eat()
            if op in ("+", "*") and starts_operand(self.peek()):
                raise TypeErr("binary `%s` on patterns: arithmetic, not a quantifier" % op)
            x = "(?:%s)%s" % (x, op)
        return x
    def prim(self):
        t = self.eat()
        if t[0] == '"': return lit(t[1:-1])
        if t == "(":
            x = self.amp_s() if self.sab else self.alt(); self.eat(")"); return x
        if t == "[":
            n = self.eat(); self.eat("="); x = self.amp_s() if self.sab else self.alt(); self.eat("]")
            return "(?<%s>%s)" % (n, x)
        return "(?:%s)" % self.env[t]
    # SABOTAGE order: `|` tighter than SEQ, and a postfix binds the whole SEQ chain before it
    def amp_s(self):
        x = self.seq_s()
        while self.peek() == "&":
            self.eat(); c = self.eat(); x = "(?:%s)(?C\"%s\")" % (x, c[1:])
        return x
    def seq_s(self):
        parts = [self.alt_s()]
        chain = lambda ps: ps[0] if len(ps) == 1 else "".join("(?:%s)" % p for p in ps)
        while True:
            if self.peek() in POSTFIX: parts = ["(?:%s)%s" % (chain(parts), self.eat())]
            elif self.peek() == "SEQ": self.eat(); parts.append(self.alt_s())
            else: return chain(parts)
    def alt_s(self):
        br = [self.prim()]
        while self.peek() == "|": self.eat(); br.append(self.prim())
        return br[0] if len(br) == 1 else "(?:" + "|".join(br) + ")"

# --------------------------------------------------------------------------------- holes in value positions
def instantiate(template, holes, union=False, inner=False):
    """template with {0}, {1}...; holes = list of member lists. RULED: one copy of the literal per combination
    (cartesian product, first hole slowest), illegal combinations removed. Sabotage: union / inner alternation."""
    if inner:   # one copy, each hole an inner alternation of its members (not the ruled reading)
        return template.format(*["(?:%s)" % "|".join(m) for m in holes]), []
    combos = [tuple(m[k] for m in holes) for k in range(len(holes[0]))] if union else list(itertools.product(*holes))
    keep, gone = [], []
    for c in combos:
        txt = template.format(*c)
        bad = compiles(txt)
        (gone if bad else keep).append((c, txt, bad))
    if not keep: return "(?!)", gone
    return ("(?|" if len(keep) > 1 else "(?:") + "|".join(t for _, t, _ in keep) + ")", gone

# ------------------------------------------------------------------------------------------ numbering (the trial)
def number_groups(pat):
    """plain capturing groups -> (?<_k>...) by opening parenthesis; returns (pattern, {number: name})"""
    out, k, i, alias = [], 0, 0, {}
    while i < len(pat):
        c = pat[i]
        if c == "\\": out.append(pat[i:i + 2]); i += 2; continue
        if c == "(":
            m = re.match(r"\(\?P?<([A-Za-z_]\w*)>", pat[i:])
            if m: k += 1; alias[k] = m.group(1); out.append(m.group(0)); i += m.end(); continue
            if pat.startswith("(?", i): out.append("(?"); i += 2; continue
            k += 1; alias[k] = "_%d" % k; out.append("(?<_%d>" % k); i += 1; continue
        out.append(c); i += 1
    return "".join(out), alias

# --------------------------------------------------------------------------------- the static-order label model
def static_labels(pat_renamed, order):
    """order: list of (group name, kind, label) in PATTERN ORDER; kind 'set' (a copy) or 'mark' (a branching entry)"""
    def f(ctx):
        out = {}
        for g, kind, lab in order:
            if ctx.get(g) is not None: out[lab] = ctx.get(g) if kind == "set" else None
        return out
    return f

print("predspec25 engine over predspec244's (loaded in memory, rule 244); libpcre2-8 %s%s" % (
    P.version(), " ; SABOTAGE" if SAB else ""))
print()

# ======================================================================================================== PART PS
print("== PART PS: pass-start-read (RULED: 'pass-start-read: yes keep it'). A condition in a loop body reads the labels")
print("   AT THE POINT WHERE IT IS WRITTEN: before its label's group the previous pass's value. The sorted list shown to")
print("   the owner (COND-FAMILY), re-run: `/(?:(?=(?<n>\\d))(?C)(?<h>\\d);)*/`, the callout 'h unset, or n >= h'")
def ge_or_unset(get):
    h, n = get("h"), get("n")
    return h is None or (num(n) and num(h) and int(n) >= int(h))
SORTED = r'(?:(?=(?<n>\d))(?C"c")(?<h>\d);)*'
ls = LRx(SORTED, {"c": lambda x: ge_or_unset(x.get)})
es = mk(SORTED, {"c": lambda v: ge_or_unset(v.lab)}, PRULE)
e243 = mk(SORTED, {"c": lambda v: ge_or_unset(v.lab)}, "243")
SHOWN_PS = [("W", "3;4;7;", "HOLDS"), ("W", "3;3;9;", "HOLDS"), ("W", "3;7;4;", "FAILS"), ("S", "3;7;4;", "`3;7;`@0"),
            ("W", "9;1;", "FAILS"), ("S", "9;1;", "`9;`@0"), ("W", "7;", "HOLDS"), ("W", "", "HOLDS")]
for m, t, shown in SHOWN_PS:
    a = {"W": pW, "S": pS}[m](ls, t); b = {"W": W_, "S": S_}[m](es, t); c = {"W": W_, "S": S_}[m](e243, t)
    print("PS %s `%s`: shown %s ; libpcre2 %s ; engine (the one rule) %s ; rev 24.3's per-pass reset %s ; %s" % (
        m, t, shown, a, b, c, check("PS shown %s %s" % (m, t), a == shown and b == shown)))
POOL_PS = strings("139;", 5)
d = epD3(es, ls, POOL_PS, ("h", "n"))
print("PS engine vs libpcre2 over %d texts (alphabet `139;`, length <= 5), reported row, labels h and n: %s ; %s" % (
    len(POOL_PS), fmt3(d), check("PS engine = libpcre2", d[0] == [0, 0, 0])))
d = epD3(e243, ls, POOL_PS, ("h", "n"))
print("PS ORDER CHECK: rev 24.3's per-pass reset vs libpcre2: %s (must differ)" % fmt3(d))
check("PS order check differs", d[0] != [0, 0, 0])
# the manager's spelling in the draft's forms: c := when((h: /\d/), (n: >= $h)) = NOT (h: /\d/) | (n: >= $h)
WHENF = r'(?:(?=(?<n>\d))(?:(?C"noth")|(?C"ge"))(?<h>\d);)*'
ew = mk(WHENF, {"noth": lambda v: not (v.lab("h") is not None and re.fullmatch(r"\d", v.lab("h"))),
                "ge": lambda v: num(v.lab("n")) and num(v.lab("h")) and int(v.lab("n")) >= int(v.lab("h"))}, PRULE)
d = D3(ew, es, POOL_PS)
print("PS the manager's spelling `when((h: /\\d/), (n: >= $h))` = `NOT (h: /\\d/) | (n: >= $h)` (the record: 'not run through")
print("   the model'), run as an alternation of two tests at the condition's place: vs the single callout %s ; %s" % (
    fmt3(d), check("PS when-spelling = callout", d[0] == [0, 0, 0])))
# intent oracles (Python re, no shared construction): sorted; and 'every item except the LAST is under 5'
def items(t): return [x for x in t.split(";")[:-1]] if re.fullmatch(r"(?:\d;)*", t) else None
bad = sum(1 for t in POOL_PS if es.whole(t)[0] != (items(t) is not None and all(a <= b for a, b in zip(items(t), items(t)[1:]))))
print("PS WHOLE vs the intent 'the items are in non-decreasing order' (Python): %d of %d differ ; %s" % (bad, len(POOL_PS), check("PS sorted oracle", bad == 0)))
NG5 = r'(?:(?C"c")(?<h>\d);)*'
en = mk(NG5, {"c": lambda v: not (num(v.lab("h")) and int(v.lab("h")) >= 5)}, PRULE)
POOL37 = strings("37;", 6)
bad = sum(1 for t in POOL37 if en.whole(t)[0] != (items(t) is not None and all(int(x) < 5 for x in items(t)[:-1])))
print("PS `/(?:${c}(?<h>\\d);)*/`, c := NOT (h: >= 5), WHOLE vs 'every item except the LAST is under 5' (the manager's")
print("   corrected restatement, Python): %d of %d differ ; %s" % (bad, len(POOL37), check("PS except-last oracle", bad == 0)))
print("PS the record's other line, WHOLE `7;3;` %s (the second pass reads the first pass's 7) ; SEARCHED `7;3;` %s" % (W_(en, "7;3;"), S_(en, "7;3;")))
print()

# ======================================================================================================== PART AS
print("== PART AS: array-slot (RULED: 'only what was set'): the array is the name's SETTINGS in order; a reset adds nothing")
st = mk(r"(?<h>\d)?(?:;(?<h>\d)?)*").whole("7;;3;")[2]
arr = View(None, "", 0, 0, st).array("h")
print("AS `/(?<h>\\d)?(?:;(?<h>\\d)?)*/` on `7;;3;`: array %s (the shown row: [`7`, `3`] against [`7`, -, `3`, -]) ; %s" % (arr, check("AS array", arr == ["7", "3"])))
st = mk(r"(?<it>(?<h>\d)?)(?:;(?<it>(?<h>\d)?))*").whole("7;;3;")[2]
arr2 = View(None, "", 0, 0, st).array("it")
print("AS the manager's lean, run: label the WHOLE item (always set, possibly empty), `/(?<it>(?<h>\\d)?)(?:;(?<it>(?<h>\\d)?))*/`")
print("   on `7;;3;`: array of it %s (positions kept), array of h %s ; %s" % (arr2, View(None, "", 0, 0, st).array("h"), check("AS item array", arr2 == ["7", "", "3", ""])))
print()

# ======================================================================================================== PART LF
print("== PART LF: label-flow (RULED): a composed pattern surfaces labels as a literal does; across SEQ one label, the LAST")
print("   MENTION; across `&` a name both sides surface is an ambiguous reference (an error where referenced); a part's")
print("   own label through a label on the part (`[aa = A]`, `aa.h`). Control: the STATIC-ORDER model on libpcre2.")
ENV = {"rx.digit": r"\d", "digits": r"\d+", "wb": r"\b", "A": r"(?<h>\d)", "B": r"(?:,(?<h>\d))?",
       "AL": r"\d(?=,\d,(?<h>\d))", "BL": r",(?<h>\d)", "item": r"(?<h>\d)"}
X = Exp(ENV, sab=SAB)
seq1 = X("A SEQ B")
e1 = mk(seq1)
s1 = LRx(r"(?:(?<h1>\d))(?<e2>)(?:(?:,(?<h2>\d))?)", labfn=static_labels(None, [("h1", "set", "h"), ("e2", "mark", "h"), ("h2", "set", "h")]))
print("LF A := `/(?<h>\\d)/`, B := `/(?:,(?<h>\\d))?/`; `A SEQ B` expands to `/%s/`" % seq1)
print("LF   WHOLE `7`: engine %s ; static-order %s (item 24 entry 15: h UNSET) ; %s" % (W_(e1, "7", ("h",)), pW(s1, "7", ("h",)),
      check("LF A SEQ B on 7", W_(e1, "7", ("h",)) == "HOLDS h = unset" == pW(s1, "7", ("h",)))))
print("LF   WHOLE `7,3`: engine %s ; SEARCHED `x7 7,3`: %s ; FIND-ALL `7 7,3`: %s" % (W_(e1, "7,3", ("h",)), S_(e1, "x7 7,3", ("h",)), F_(e1, "7 7,3", ("h",))))
d = epD3(e1, s1, strings("37,", 5), ("h",))
print("LF   engine vs static-order over %d texts, labels compared: %s ; %s" % (d[2], fmt3(d), check("LF static = engine", d[0] == [0, 0, 0])))
seq2 = X("AL SEQ BL")
e2 = mk(seq2)
s2 = LRx(r"(?:\d(?=,\d,(?<h1>\d)))(?:,(?<h2>\d))", labfn=static_labels(None, [("h1", "set", "h"), ("h2", "set", "h")]))
print("LF (ii) a lookahead makes A's h name LATER text than B's: AL := `/\\d(?=,\\d,(?<h>\\d))/`, BL := `/,(?<h>\\d)/`, `AL SEQ BL`:")
print("LF   SEARCHED `1,2,3`: engine %s ; static-order %s (B's, the last mention, though A's `3` lies later in the text) ; %s" % (
    S_(e2, "1,2,3", ("h",)), pS(s2, "1,2,3", ("h",)), check("LF lookahead last mention", S_(e2, "1,2,3", ("h",)) == "`1,2`@0 h = `2`" == pS(s2, "1,2,3", ("h",)))))
lst = X('(item SEQ ",")* SEQ item')
d = D3(mk(lst), mk(r"(?:(?<h>\d),)*(?<h>\d)"), strings("37,", 5))
el = mk(lst); st7 = el.whole("7")[2]; st735 = el.whole("7,3,5")[2]
print("LF the composed list `(item SEQ \",\")* SEQ item` -> `/%s/` vs the literal items-then-last `/(?:(?<h>\\d),)*(?<h>\\d)/`:" % lst)
print("LF   %s ; on `7` label %s array %s ; on `7,3,5` label %s array %s ; %s" % (fmt3(d), el.whole("7")[1]["h"], View(None, "", 0, 0, st7).array("h"),
      el.whole("7,3,5")[1]["h"], View(None, "", 0, 0, st735).array("h"), check("LF composed list = literal", d[0] == [0, 0, 0])))
def amp_left(lsrc, rsrc, test):
    """`[aa = L] & R & (aa.h: test)`: R matched WHOLE on the stretch; the test reads the LEFT part's own h"""
    rp = mk(rsrc)
    return mk("(?<aa>" + lsrc + ')(?C"amp")', {"amp": lambda v: rp.whole(v.s[v.start:v.pos])[0] and test(v.lab("h"))})
q = amp_left(r"(?<h>\d)\d", r"\d(?<h>\d)", lt(2))
res = (W_(q, "12"), W_(q, "21"), S_(q, "21 12"), F_(q, "12 21 10"))
print("LF `[aa = /(?<h>\\d)\\d/] & /\\d(?<h>\\d)/ & (aa.h: <2)`: WHOLE `12` %s, `21` %s ; SEARCHED `21 12` %s ; FIND-ALL `12 21 10` %s" % res)
print("LF   = rev 24.4's PART S line LEFT, shown to the owner with shared-label ; `(h: <2)` there: the AMBIGUOUS-REFERENCE error ; %s" % (
    check("LF aa.h = LEFT", res == ("HOLDS", "FAILS", "`12`@3", "[`12`@0, `10`@6]"))))
print()

# ======================================================================================================== PART NUM
print("== PART NUM: label numbers, TRIED (not ruled): a number is another name of a group's label, read by the one rule;")
print("   only capturing groups are numbered, by opening parenthesis; local to each pattern literal")
g = groups_of(r"(a)(?:b)(?<n>c)(?=d)((d)e)", "abcde")
print("NUM `(a)(?:b)(?<n>c)(?=d)((d)e)` on `abcde`, libpcre2 groups 0..4: %s (the manager's answer: 1 = a, 2 = c (n), 3 = de, 4 = d) ; %s" % (
    g, check("NUM numbering", g == ["abcde", "a", "c", "de", "d"])))
pn, al = number_groups(r"(a)(?:b)(?<n>c)(?=d)((d)e)")
print("NUM the trial's numbering of the same literal: `%s`, aliases %s (2 is n: `(n: .., 2: ..)` names one label twice: the label-twice error)" % (pn, al))
pu, _ = number_groups(r"(?:(\d)?;)*")
c1 = mk(pu + '(?C"c")', {"c": lambda v: lt(5)(v.lab("_1"))})
c2 = mk(r'(?:(?<h>\d)?;)*(?C"c")', {"c": lambda v: lt(5)(v.lab("h"))})
d = D3(c1, c2, strings("37;", 5), keys=False)
print("NUM `/(?:(\\d)?;)*/ & (1: <5)` vs REP `& (h: <5)` (an unnamed group read by number = a named one): %s ; %s ; WHOLE `3;;` %s" % (
    fmt3(d), check("NUM number = name", d[0] == [0, 0, 0]), W_(c1, "3;;")))
# two groups of one name, each with its own number: does `1` name the label h (alias) or group 1's own setting?
DUP = r"(?<h>\d)(?:,(?<h>\d))*"
alias_p = mk(DUP + '(?C"c")', {"c": lambda v: lt(5)(v.lab("h"))})
own_p = mk(r'(?<_1>\d)(?:,(?<_2>\d))*(?C"c")', {"c": lambda v: lt(5)(v.lab("_1"))})
for nm, p in (("(a) ALIAS (1 names the label h)", alias_p), ("(b) OWN (1 names group 1's own label)", own_p)):
    print("NUM `/%s/ & (1: <5)` %s: WHOLE `3,7` %s, `7,3` %s ; SEARCHED `7,3` %s ; FIND-ALL `3,7 7,3` %s" % (
        DUP, nm, W_(p, "3,7"), W_(p, "7,3"), S_(p, "7,3"), F_(p, "3,7 7,3")))
d = D3(alias_p, own_p, strings("37,", 5), keys=False)
print("NUM   (a) vs (b), holds and stretch: %s ; libpcre2 under (?J): group 1 on `3,7` = %s (PCRE's `$1` is group 1's capture)" % (
    fmt3(d), groups_of("(?J)" + DUP, "3,7")[1]))
check("NUM alias vs own differ", d[0] != [0, 0, 0])
# A & B & (1: ..): the number names a group of the NEAREST pattern to its left (B)
rp = mk(r"\d(?<_1>\d)")
qn = mk(r'(?<_1>\d)\d(?C"amp")', {"amp": lambda v: rp.whole(v.s[v.start:v.pos])[0] and lt(2)(rp.whole(v.s[v.start:v.pos])[1]["_1"])})
res = (W_(qn, "12"), W_(qn, "21"), S_(qn, "21 12"), F_(qn, "12 21 10"))
print("NUM `/(\\d)\\d/ & /\\d(\\d)/ & (1: <2)` (1 = B's group): WHOLE `12` %s, `21` %s ; SEARCHED `21 12` %s ; FIND-ALL `12 21 10` %s ; %s" % (
    res + (check("NUM nearest pattern", res == ("FAILS", "HOLDS", "`21`@0", "[`21`@3, `10`@6]")),)))
# sequence-numbers: A SEQ B & (1: ..), A := /(\d)/, B := /,(\d)/
wo = mk(r'(?:(?<_1>\d))(?:,(?<_2>\d))(?C"c")', {"c": lambda v: lt(5)(v.lab("_1"))})       # (a) written-out numbering
nb = mk(r'(?:(?<a_1>\d))(?:,(?<_1>\d))(?C"c")', {"c": lambda v: lt(5)(v.lab("_1"))})      # (c) the nearest literal, B
for nm, p in (("(a) WRITTEN-OUT (1 = A's group)", wo), ("(c) NEAREST LITERAL (1 = B's group)", nb)):
    print("NUM `A SEQ B & (1: <5)`, A := `/(\\d)/`, B := `/,(\\d)/`, %s: WHOLE `3,7` %s, `7,3` %s ; SEARCHED `7,3 3,7` %s ; FIND-ALL `7,3 3,7` %s" % (
        nm, W_(p, "3,7"), W_(p, "7,3"), S_(p, "7,3 3,7"), F_(p, "7,3 3,7")))
d = D3(wo, nb, strings("37,", 4), keys=False)
print("NUM   (a) vs (c): %s ; (b) a composed pattern has no numbers of its own: `1` is the unknown-label error" % fmt3(d))
dl = mk(r'(?<_1>\d):(?<_2>\d)(?C"c")', {"c": lambda v: int(v.lab("_2")) > int(v.lab("_1"))})
print("NUM `$1` tried as a value: `/(\\d):(\\d)/ & (2: > $1)`: WHOLE `3:5` %s, `5:3` %s ; SEARCHED `5:3 3:5` %s ; FIND-ALL `5:3 3:5 4:9` %s" % (
    W_(dl, "3:5"), W_(dl, "5:3"), S_(dl, "5:3 3:5"), F_(dl, "5:3 3:5 4:9")))
print()

# ======================================================================================================== PART RX
print("== PART RX: the rx module's forms (RULED), expanded by code and run against HAND-WRITTEN regex on libpcre2")
def show3(lr, w, s_, f_):
    return "WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (w, pW(lr, w), s_, pS(lr, s_), f_, pF(lr, f_))
# (1) sequence-reading: splice
t = X("wb SEQ digits SEQ wb")
a, b = LRx(t), LRx(r"\b\d+\b")
d = pD3(a, b, strings("1x ", 5))
print("RX1 `wb SEQ digits SEQ wb` -> `/%s/`: %s" % (t, show3(a, "12", "x12 34", "12 x34 56")))
print("RX1   the note's answers: WHOLE `12` HOLDS ; SEARCHED `x12 34` `34`@4 ; FIND-ALL `12 x34 56` `12`@0, `56`@7 ; vs hand `\\b\\d+\\b` %s ; %s" % (
    fmt3(d), check("RX1 splice", d[0] == [0, 0, 0] and pS(a, "x12 34") == "`34`@4" and pF(a, "12 x34 56") == "[`12`@0, `56`@7]")))
# (2) precedence
t = X('"x" SEQ "1" | "2"')
a, b = LRx(t), LRx(r"x1|2")
d = pD3(a, b, strings("x12 y", 4))
print("RX2 `\"x\" SEQ \"1\" | \"2\"` -> `/%s/`: %s ; vs hand `x1|2` %s ; %s" % (t, show3(a, "2", "y2", "x1 2 x2"), fmt3(d),
      check("RX2 precedence", d[0] == [0, 0, 0] and pF(a, "x1 2 x2") == "[`x1`@0, `2`@3, `2`@6]")))
print("RX2   the other order (`|` tighter, the note's P3) `x(?:1|2)`: %s" % show3(LRx(r"x(?:1|2)"), "2", "y2", "x1 2 x2"))
t = X('[h = rx.digit] SEQ (";" SEQ [m = rx.digit])? & @c')
h5 = {"c": lambda v: lt(5)(v.lab("h"))}
pe, ph = mk(t, h5), mk(r'(?<h>\d)(?:;(?<m>\d))?(?C"c")', h5)
d = D3(pe, ph, strings("37;", 5))
print("RX2 `[h = rx.digit] SEQ (\";\" SEQ [m = rx.digit])? & (h: <5)` -> `/%s/` (the condition on the WHOLE sequence):" % t)
print("RX2   WHOLE `7;3` %s, `3;7` %s ; SEARCHED `7;3` %s ; vs hand `(?<h>\\d)(?:;(?<m>\\d))?` then c: %s ; %s" % (
    W_(pe, "7;3", ("h", "m")), W_(pe, "3;7", ("h", "m")), S_(pe, "7;3", ("h", "m")), fmt3(d), check("RX2 amp binds after SEQ", d[0] == [0, 0, 0])))
# (3) hole-reading
hole = "x(?:%s)" % r"\b\d+\b"
lr = LRx(hole); pool = strings("x1 ", 5)
hits = sum(1 for s in pool if lr.match(s, 0) is not None)
print("RX3 hole-reading: `/x${num}/`, num := `/\\b\\d+\\b/`, is `/%s/` (the assertion crosses the border): texts with a match %d of %d ; %s (can-never-match: the warning)" % (
    hole, hits, len(pool), check("RX3 dead assertion", hits == 0)))
a, b = LRx(r"(?:ab)?c"), LRx(r"ab?c")
print("RX3 `/${/ab/}?c/` = `/(?:ab)?c/`: %s ; a STRING insert `ab?c`: %s ; %s" % (
    show3(a, "ac", "bc", "c abc ac"), show3(b, "ac", "bc", "c abc ac"), check("RX3 whole insert", pW(a, "ac") == "FAILS" and pW(b, "ac") == "HOLDS")))
# (4) the insert's kind per position: a count position, the literal copied per member
rul, _ = instantiate(r"(\d+?)\d{{{0}}}", [["2", "4"]], inner=False)
inn = r"(\d+?)(?:\d{2}|\d{4})"      # one copy, the hole an inner alternation of its members
if SAB: rul = inn
ga, gb = groups_of(rul, "123456"), groups_of(inn, "123456")
print("RX4 a count position, n := [2, 4]: `/(\\d+?)\\d{${n}}/` copied per member -> `/%s/`: WHOLE `123456` group 1 = %s ;" % (rul, ga[1]))
print("RX4   one copy with an inner alternation `/%s/` (NOT the ruling: 'the literal is instantiated per member'): group 1 = %s ; %s" % (
    inn, gb[1], check("RX4 per-member copies", ga[1] == "1234" and gb[1] == "12")))
gn, _ = instantiate(r"(?<{0}>\d)", [["a", "b"]])
print("RX4 a group-name position, nm := [\"a\", \"b\"]: `/(?<${nm}>\\d)/` -> `/%s/` (one copy per member)" % gn)
# (5) counts: distribute per mention; the cartesian product; illegal combinations removed
two, gone = instantiate(r"\d{{{0},{1}}}", [["2", "4"], ["2", "4"]], union=SAB)
one, _ = instantiate(r"\d{{{0}}}", [["2", "4"]])
print("RX5 `rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4]: the product (2,2) (2,4) (4,2) (4,4); removed: %s ; -> `/%s/`" % (
    ", ".join("%s (libpcre2: %s)" % (t_, why) for _, t_, why in gone), two))
a = LRx(two); b = LRx(one)
print("RX5   %s" % show3(a, "123", "12345", "12345 6"))
print("RX5   the one-argument exact count `rx.repeat(rx.digit, n)` -> `/%s/`: %s" % (one, show3(b, "123", "12345", "12345 6")))
pool = strings("12x", 5)
bad = sum(1 for s in pool if (a.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED) is not None) != bool(re.fullmatch(r"\d{2,4}", s)))
print("RX5   WHOLE vs Python `\\d{2,4}` (two to four digits, item 24 entry 16): %d of %d differ ; %s" % (bad, len(pool), check("RX5 two to four", bad == 0)))
bad1 = sum(1 for s in pool if (b.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED) is not None) != bool(re.fullmatch(r"\d{2}|\d{4}", s)))
print("RX5   one-argument vs Python `\\d{2}|\\d{4}`: %d of %d differ ; %s" % (bad1, len(pool), check("RX5 one-argument", bad1 == 0)))
none_, gone2 = instantiate(r"\d{{{0},{1}}}", [["5"], ["2", "3"]])
print("RX5 every combination illegal (min := [5], max := [2, 3]): removed %d of 2 -> `/%s/`: matches nothing (the can-never-match warning)" % (len(gone2), none_))
kk, gk = instantiate(r"\d{{{0}}}", [["2", "x"]])
print("RXK a member of the wrong kind in a count position, n := [\"2\", \"x\"]: by libpcre2 legality `\\d{x}` is a LEGAL pattern (literal")
print("    braces), removed: %d -> `/%s/`: %s ; with the member refused by the position's kind -> `/(?:\\d{2})/`: %s" % (
    len(gk), kk, show3(LRx(kk), "1{x}", "a1{x}", "12 3{x}"), show3(LRx(r"(?:\d{2})"), "1{x}", "a1{x}", "12 3{x}")))
o3s, _ = instantiate(r"(?<r>\d{{{0},{1}}})", [["2", "3", "4"], ["2", "3", "4"]])
fast = list(itertools.product(["2", "3", "4"], repeat=2)); fast = [(x, y) for y, x in fast]
o3f = "(?|" + "|".join(r"(?<r>\d{%s,%s})" % c for c in fast if int(c[0]) <= int(c[1])) + ")"
tot = [0, 0, 0]
for L in (set(z) for k in range(1, 4) for z in itertools.combinations((2, 3, 4), k)):
    cs = {"c": lambda x, L=L: x.get("r") is not None and len(x.get("r")) in L}
    dd = pD3(LRx(o3s + '(?C"c")', cs), LRx(o3f + '(?C"c")', cs), strings("12x", 5), ("r",))
    tot = [u + v for u, v in zip(tot, dd[0])]
print("RX5 the ORDER of the product (THE DRAFT'S READING: first hole slowest) against first hole fastest, n := [2, 3, 4],")
print("   `[r = repeat(rx.digit, n, n)] & (r: length in L)` for all 7 sets L, reported row with r: %d / %d / %d texts summed (%d texts each) (answer-free here)" % (tuple(tot) + (len(strings("12x", 5)),)))
# (6) the one repeat construct and labels
t = X("([a = rx.digit] & @c)+")
pa = mk(t, {"c": lambda v: lt(5)(v.lab("a"))})
st = pa.whole("341")[2]
print("RX6 `rx.repeat([a = rx.digit] & (a: <5), min = 1)` -> `/%s/`: WHOLE `3417` %s, `341` %s (array %s) ; SEARCHED `3417` %s ; FIND-ALL `3417 82` %s" % (
    t, W_(pa, "3417"), W_(pa, "341", ("a",)), View(None, "", 0, 0, st).array("a"), S_(pa, "3417", ("a",)), F_(pa, "3417 82", ("a",))))
pb = mk(X("[a = rx.digit]+ & @c"), {"c": lambda v: lt(5)(v.lab("a"))})
print("RX6 bare after the repeat, `rx.repeat([a = rx.digit], min = 1) & (a: <5)`: WHOLE `73` %s, `37` %s (the last item) ; %s" % (
    W_(pb, "73", ("a",)), W_(pb, "37", ("a",)), check("RX6 labels", W_(pa, "3417") == "FAILS" and W_(pb, "73", ("a",)) == "HOLDS a = `3`" and W_(pb, "37") == "FAILS")))
pr = mk(X("[run = rx.digit+]"))
print("RX6 labelling the repeat, `[run = rx.repeat(rx.digit, min = 1)]` -> `/%s/`: on `341` run = %s" % (X("[run = rx.digit+]"), pr.whole("341")[1]["run"]))
d = pD3(LRx(X("rx.digit+")), LRx(r"\d+"), strings("1x ", 5))
print("RX6 the plural `digits := rx.repeat(rx.digit, min = 1)` -> `/%s/` vs `\\d+`: %s ; %s" % (X("rx.digit+"), fmt3(d), check("RX6 plural", d[0] == [0, 0, 0])))
# (7) the nine postfix operators: each regex's own on the operand as a whole
def ends_l(pat, s):
    seen = []
    def rec(x): seen.append(x.pos); return False
    P.Pcre(pat + '(?C"e")', {"e": rec}).match(s, 0, P.PCRE2_ANCHORED); return seen
def ends_e(pat, s): return [p for p, _ in mk(pat).paths(s, 0)]
okc = 0
for xs in (r"\d", r"\d+"):
    cells = []
    for op in POSTFIX:
        ex = Exp({"x": xs}, SAB)("x" + op)
        base = op[0]                    # the possessive form's plain quantifier
        epat = "(?>(?:(?:%s))%s)" % (xs, base) if op in ("++", "*+", "?+") else ex
        a_, b_ = ends_l(ex, "123"), ends_e(epat, "123")
        okc += a_ == b_
        cells.append("%s %s" % (op, ",".join(map(str, a_)) + ("" if a_ == b_ else " (engine %s)" % b_)))
    print("RX7 X := `%s`, the ends `X op` tries on `123` at 0 (libpcre2; the engine, possessive as atomic): %s" % (xs, " ; ".join(cells)))
print("RX7 18 operator rows, libpcre2 = the engine: %d ; %s ; `(?:\\d+)??` 0,3,2,1 against `\\d*?` %s (regex behaving as regex)" % (
    okc, check("RX7 nine operators", okc == 18), ",".join(map(str, ends_l(r"\d*?", "123")))))
for src, hand in (('"a" SEQ "b"+', r"ab+"), ('("a" SEQ "b")+', r"(?:ab)+"), ("rx.digit+", r"\d+")):
    t = X(src); d = pD3(LRx(t), LRx(hand), strings("ab1", 5))
    print("RX8 `%s` -> `/%s/`: %s ; vs hand `%s` %s ; %s" % (src, t, show3(LRx(t), "abb", "abbab", "abbab"), hand, fmt3(d), check("RX8 %s" % src, d[0] == [0, 0, 0])))
try: t = X('"a" SEQ "1"+ & @c | "2"')
except AssertionError as e: t = "PARSE FAILED %s" % (e,)
print("RX8 the whole order, `\"a\" SEQ \"1\"+ & c | \"2\"` -> `/%s/` ; %s" % (t, check("RX8 order text", t == '(?:(?:(?:a)(?:(?:1)+))(?C"c")|2)')))
for src in ("x++", "x+?", "x*+", "x??", "x+ | y", "x + y", "x * y"):
    try: r_ = Exp({"x": "a", "y": "b"}, SAB)(src)
    except TypeErr as e: r_ = "TYPE ERROR (%s)" % e
    except AssertionError as e: r_ = "PARSE FAILED %s" % (e,)
    print("RX9 tokens `%s` -> %s -> %s" % (src, tokens(src), r_))
# (8) a quantifier on a condition: regex's meaning (the manager's 'type error' is not in the owner's words)
for op, name in (("?", "optional"), ("+", "one or more"), ("*", "any number")):
    lrq = LRx(r'(?<h>\d)(?:(?C"c"))%s' % op, {"c": lambda x: lt(5)(x.get("h"))})
    erq = mk(r'(?<h>\d)(?:(?C"c"))%s' % ("{1,2}" if op == "+" else "?" if op == "?" else "{0,2}"), {"c": lambda v: lt(5)(v.lab("h"))})
    print("RXQ `[h = rx.digit] SEQ (h: <5)%s` as regex (`(?<h>\\d)(?:(?C))%s`, %s): libpcre2 WHOLE `7` %s, `3` %s ; SEARCHED `73` %s ; FIND-ALL `7 3` %s" % (
        op, op, name, pW(lrq, "7"), pW(lrq, "3"), pS(lrq, "73"), pF(lrq, "7 3")))
# (9) arithmetic beside patterns: a count from `n + 1` with n := [2, 4]
p1, _ = instantiate(r"\d{{{0}}}", [["3", "5"]])
print("RXA `rx.repeat(rx.digit, n + 1)`, n := [2, 4], read as distribution per mention (3 | 5): `/%s/`: %s ; read as 'adding patterns is a type error': REJECTED" % (
    p1, show3(LRx(p1), "123", "123456", "12345 678")))
print()

# ======================================================================================================== PART E
print("== PART E: the error-or-warning rulings, their shown rows re-run (empty-search-error: warning; min-values: at least n)")
pe = mk(r'(?<h>\d*)(?C"c")', {"c": lambda v: not lt(5)(v.lab("h"))})
res = (W_(pe, "", ("h",)), S_(pe, "a7"), F_(pe, "7a3"))
print("E `/(?<h>\\d*)/ & NOT (h: <5)` (PCRE's empty matches, with the warning `pcrec.empty.search`): WHOLE `` %s ; SEARCHED `a7` %s ; FIND-ALL `7a3` %s ; %s" % (
    res + (check("E empty-search shown", res == ("HOLDS h = ``", "``@0", "[`7`@0, ``@1, ``@2, ``@3]")),)))
lre = LRx(r'(?<h>\d*)(?C"c")', {"c": lambda x: not lt(5)(x.get("h"))})
d = epD3(pe, lre, strings("7a3", 4), ("h",))
print("E   engine vs libpcre2 (global loop): %s ; %s" % (fmt3(d), check("E empty-search libpcre2", d[0] == [0, 0, 0])))
om = mk(r"(?:[\s\S]*?(?<x>\d)){2,}[\s\S]*")
st = om.whole("1a2")[2]
r_ = om.search("1 a2 3"); fa = om.findall("12 3 45")
print("E `occurrences(/\\d/, min = 2)` (the one-pattern model with `{2,}`): WHOLE `1a2` %s hits %s ; SEARCHED `1 a2 3` %s ; FIND-ALL `12 3 45` %d match(es), hits %s ; %s" % (
    W_(om, "1a2"), View(None, "", 0, 0, st).array("x"), S_(om, "1 a2 3"), len(fa), View(None, "", 0, 0, om.whole("12 3 45")[2]).array("x"),
    check("E min-values shown", W_(om, "1a2") == "HOLDS" and S_(om, "1 a2 3") == "`1 a2 3`@0" and len(fa) == 1)))
# which "at least n": the quantifier {n,} (re-cuts the hits) or the count over the hits (occurs.at_least)?
qc = mk(r"(?:[\s\S]*?(?<x>aab|a)){2,}[\s\S]*")
qb = mk(r'(?:[\s\S]*?(?<x>aab|a))*[\s\S]*(?C"c")', {"c": lambda v: sum(1 for ps in (v.passes("x") or []) if ps.get("x") is not None) >= 2})
qa = mk(r'(?>(?:[\s\S]*?(?<x>aab|a))*[\s\S]*)(?C"c")', {"c": lambda v: sum(1 for ps in (v.passes("x") or []) if ps.get("x") is not None) >= 2})
for nm, p_ in (("(C) the quantifier `{2,}`", qc), ("(B) `occurrences(x) & occurs.at_least(2, ..)`, the condition re-entering", qb), ("(B') over the atomic hit list, `hits(x) & occurs.at_least(2, ..)`", qa)):
    w = p_.whole("aab")
    print("E min = 2 on x := `/aab|a/`, %s: WHOLE `aab` %s%s ; SEARCHED `xaab` %s ; FIND-ALL `aab a` %s" % (
        nm, W_(p_, "aab"), (" hits %s" % View(None, "", 0, 0, w[2]).array("x")) if w[0] else "", S_(p_, "xaab"), F_(p_, "aab a")))
d1 = D3(qc, qb, strings("ab ", 5), keys=False); d2 = D3(qc, qa, strings("ab ", 5), keys=False)
print("E   (C) vs (B) %s ; (C) vs (B') %s (holds and stretch)" % (fmt3(d1), fmt3(d2)))
print()

# ======================================================================================================== PART W
print("== PART W: the manager's reading 'the withdrawn looped-warning is the existing label.unset under the one rule'.")
print("   looped-warning's trigger: a bare condition after the pattern reads a label whose group is inside a loop;")
print("   label.unset's: the label CAN BE UNSET where the condition reads it (here: some path reaching it, over the pool)")
def can_unset(src, pool):
    seen = []
    p = mk(src + '(?C"r")', {"r": lambda v: seen.append(v.lab("h") is None) or False})
    for s in pool:
        for st_ in range(len(s) + 1): list(p.paths(s, st_))
        if any(seen): return True
    return False
for src, looped in ((r"(?:(?<h>\d);)*", True), (r"(?:(?<h>\d);)+", True), (r"(?:(?<h>\d)?;)+", True), (r"(?<h>\d)?;", False), (r"(?<h>\d);", False)):
    u = can_unset(src, strings("3;", 4))
    print("W `/%s/ & (h: <5)`: looped-warning %s ; label.unset %s%s" % (src, "fires" if looped else "silent", "fires" if u else "silent", "" if u == looped else "   <- they differ"))
print()

# ======================================================================================================== CHECKS
ok = sum(1 for _, v in CHECKS if v)
print("== CHECKS: %d of %d OK%s" % (ok, len(CHECKS), "" if ok == len(CHECKS) else " ; FAILED: " + ", ".join(n for n, v in CHECKS if not v)))
