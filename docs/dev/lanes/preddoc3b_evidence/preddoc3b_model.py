#!/usr/bin/env -S python3 -I
# Lane preddoc3b (2026-11-19): the evidence for the conversion of the core sections values, arrays, operators,
# diagnostics and spellings of docs/design/predicates/core.md, and the new section core/modules. Every example line
# of those sections is RUN here in WHOLE, SEARCHED and FIND-ALL and must occur verbatim in core.md; the manager's
# readings 1-3 of the brief are checked on the documents themselves. DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD (as lane preddoc2's): each example is (1) LOWERED to a python `re` pattern by the rule the piece states
# (rule-as-code) and run in the three modes; (2) compared with the DRAFT'S PRINTED ANSWERS, typed in here by hand from
# docs/design/predicates_draft.md revision 29.1 (the control: earlier lanes ran them on libpcre2), where the draft
# prints them; (3) where it does not, or as a second control, a DIRECT SEMANTIC MODEL written from the ruled words
# (a brute-force search over start and end positions, with its own find-all loop) must agree with the run; (4) the
# rejected candidate the piece names is run too and must DIFFER (a rival that agreed would not be a witness).
#
# Run (W = the worktree; any cwd):  timeout 300 python3 -I -B W/docs/dev/lanes/preddoc3b_evidence/preddoc3b_model.py
# PREDDOC3B_SABOTAGE=sN (one at a time): a deliberately wrong rule or document fact; its check must FAIL.
#   s1  an unset read reads the CAPTURE (PCRE's last value), not the label          -> EXreads
#   s2  the `&` chain does not re-enter `\d+` (the greedy stretch judged only)       -> EXonetype
#   s3  `+` reads any digit string (`0099` as 99)                                   -> EXdomain
#   s4  a negative result is a signed numeral                                       -> EXedges
#   s5  `+` joins strings ("7" + 1 is `71`)                                         -> EXplus
#   s6  `left` takes the rightmost characters                                       -> EXleft
#   s7  arrays combine pairwise                                                     -> EXlift
#   s8  enumerate lists widest first instead of PCRE priority order                -> EXenum
#   s9  a class's lifted results in codepoint order                                -> EXclassorder
#   s10 class-positions: C2 computed as C1 (the candidates not told apart)          -> EXclasspos
#   s11 class-index: (b) computed as (a)                                           -> EXclassindex
#   s12 `|` binds tighter than the sequence operator                               -> EXprec
#   s13 a pattern hole read as a backreference to the first mention               -> EXpair
#   s14 a ruled piece's rulings item dropped (in memory)                           -> M1
#   s15 a `needs:` into a later core section planted (in memory)                   -> M2
#   s16 a slug dropped from its details entry (in memory)                          -> SL
#   s17 a `skeleton: yes` line planted in a converted section (in memory)          -> NOQ
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
RECORD = os.path.join(W, "docs", "design", "plan_row_bodies", "COND-FAMILY.md")
SAB = set(x for x in os.environ.get("PREDDOC3B_SABOTAGE", "").split(",") if x)
FAILED, CHECKS = [], []
MY_SECTIONS = ["core/values", "core/arrays", "core/operators", "core/modules", "core/diagnostics", "core/spellings"]


def sab(n):
    return n in SAB


def check(name, ok, detail=""):
    CHECKS.append(name)
    print("%-13s %s %s" % (name, "ok  " if ok else "FAIL", detail))
    if not ok:
        FAILED.append(name)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


CORE = read(os.path.join(PRED, "core.md"))
DETAILS = read(os.path.join(PRED, "core_details.md"))


# ------------------------------------------------------------------ the three modes
def modes_rx(rx, whole, srch, fa):
    c = re.compile(rx)
    wv = [(t, c.fullmatch(t) is not None) for t in whole]
    m = c.search(srch)
    sv = (srch, (m.group(0), m.start()) if m else None)
    fv = (fa, [(x.group(0), x.start()) for x in c.finditer(fa)])
    return wv, sv, fv


def modes_sem(f, whole, srch, fa):
    """f(s, i) -> end or None: the first match starting at i (a direct model). Find-all resumes at the end (one past
    it after an empty match), as PCRE's global loop does."""
    wv = [(t, f(t, 0) == len(t) or whole_sem(f, t)) for t in whole]
    sv = (srch, None)
    for i in range(len(srch) + 1):
        e = f(srch, i)
        if e is not None:
            sv = (srch, (srch[i:e], i))
            break
    out, i = [], 0
    while i <= len(fa):
        e = f(fa, i)
        if e is None:
            i += 1
            continue
        out.append((fa[i:e], i))
        i = e if e > i else i + 1
    return wv, sv, (fa, out)


WHOLE_F = {}


def whole_sem(f, t):
    g = WHOLE_F.get(f)
    return g(t) if g else False


def fmt(res, prog):
    wv, sv, fv = res
    w = ", ".join("`%s` %s" % (t, "HOLDS" if ok else "FAILS") for t, ok in wv)
    s = "`%s` %s" % (sv[0], ("`%s`@%d" % sv[1]) if sv[1] else "FAILS")
    f = "`%s` [%s]" % (fv[0], ", ".join("`%s`@%d" % x for x in fv[1]))
    return "WHOLE %s / SEARCHED %s / FIND-ALL %s (%s)" % (w, s, f, prog)


def same(a, b):
    return a == b


def in_core(line):
    return line in CORE


def printed(whole, srch, fa):
    """The draft's printed answers as a result triple: whole = [(text, bool)], srch = (text, (str, at) or None)."""
    return whole, srch, fa


def alt(strings):
    return "(?:%s)" % "|".join(re.escape(s) for s in strings) if strings else "(?!)"


CANON = re.compile(r"0|[1-9][0-9]*")


def num(s):
    """The number domain: a canonical decimal numeral, else None (core/values/number-domain)."""
    if sab("s3"):
        return int(s) if s.isdigit() else None
    return int(s) if CANON.fullmatch(s) else None


def canon(n):
    """An arithmetic result: the canonical numeral; a negative result is outside the domain (number-edges)."""
    if n is None:
        return None
    if n < 0 and not sab("s4"):
        return None
    return str(n)


# ------------------------------------------------------------------ EXreads (core/values/reads)
def ex_reads():
    # the label: a pass that skips the optional group leaves y unset in that pass; an unset read is the
    # never-matching rx, so only the branch that sets y survives
    label_rx = r"(?:(\d)-\1;)*"
    capture_rx = r"(?:(\d)?-\1;)*"          # PCRE's capture: the last value set, kept across passes
    rx = capture_rx if sab("s1") else label_rx
    res = modes_rx(rx, ["3-3;-3;"], "3-3;-3;", "3-3;-3; 7-7;")
    want = printed([("3-3;-3;", False)], ("3-3;-3;", ("3-3;", 0)),
                   ("3-3;-3; 7-7;", [("3-3;", 0), ("", 4), ("", 5), ("", 6), ("", 7), ("7-7;", 8), ("", 12)]))
    rival = modes_rx(capture_rx, ["3-3;-3;"], "3-3;-3;", "3-3;-3; 7-7;")
    rival_want = printed([("3-3;-3;", True)], ("3-3;-3;", ("3-3;-3;", 0)),
                         ("3-3;-3; 7-7;", [("3-3;-3;", 0), ("", 7), ("7-7;", 8), ("", 12)]))
    line = fmt(res, "`/(?:(?<y>\\d)?-${$y};)*/`")
    ok = same(res, want) and same(rival, rival_want) and res != rival and in_core(line)
    check("EXreads", ok, line + " | rival (capture) = the draft's `\\k<y>` answers: %s" % same(rival, rival_want))


# ------------------------------------------------------------------ EXonetype (core/values/one-type)
def ex_onetype():
    # `/(?<x>\d+)/ & ($x & <5)`: the read x filtered by <5 (a one-string rx); the `&` chain re-enters `\d+`
    def f(s, i):
        ends = [e for e in range(len(s), i, -1) if re.fullmatch(r"\d+", s[i:e])]
        if sab("s2"):
            ends = ends[:1]
        for e in ends:
            n = num(s[i:e])
            if n is not None and n < 5:
                return e
        return None

    WHOLE_F[f] = lambda t: any(re.fullmatch(r"\d+", t) and num(t) is not None and num(t) < 5 for _ in [0])
    res = modes_sem(f, ["3", "37"], "x7 3", "3 7 33 4")
    want = printed([("3", True), ("37", False)], ("x7 3", ("3", 3)),
                   ("3 7 33 4", [("3", 0), ("3", 4), ("3", 5), ("4", 7)]))
    cond = modes_rx(r"[0-4]", ["3", "37"], "x7 3", "3 7 33 4")   # `(x: <5)` on a digit run, its own lowering
    line = fmt(res, "`/(?<x>\\d+)/ & ($x & <5)`, equal to `(x: <5)` here")
    check("EXonetype", same(res, want) and same(res, cond) and in_core(line), line)


# ------------------------------------------------------------------ EXdomain (core/values/number-domain)
def read_hole(y_rx, sep, fn):
    """`/(?<y>Y)SEP${fn($y)}/` by direct search: y's ends tried greedy first (Y is a single greedy run here)."""
    def f(s, i):
        for e in range(len(s), i, -1):
            y = s[i:e]
            if not re.fullmatch(y_rx, y) or not s.startswith(sep, e):
                continue
            v = fn(y)
            if v is not None and s.startswith(v, e + len(sep)):
                return e + len(sep) + len(v)
        return None

    def whole(t):
        for e in range(len(t), 0, -1):
            y = t[:e]
            if re.fullmatch(y_rx, y) and t.startswith(sep, e):
                v = fn(y)
                if v is not None and t[e + len(sep):] == v:
                    return True
        return False
    WHOLE_F[f] = whole
    return f


def ex_domain():
    f = read_hole(r"\d{4}", "-", lambda y: canon(num(y) + 1) if num(y) is not None else None)
    res = modes_sem(f, ["0099-100"], "0099-100 2025-2026", "0099-100 2025-2026 0100-101")
    want = printed([("0099-100", False)], ("0099-100 2025-2026", ("2025-2026", 9)),
                   ("0099-100 2025-2026 0100-101", [("2025-2026", 9)]))
    # the copies lowering over every value y can take (10,000 copies; a value outside the domain gives no copy)
    copies = []
    for k in range(10000):
        y = "%04d" % k
        n = num(y)
        if n is not None:
            copies.append(re.escape(y) + "-" + re.escape(canon(n + 1)))
    low = modes_rx("(?:%s)" % "|".join(copies), ["0099-100"], "0099-100 2025-2026", "0099-100 2025-2026 0100-101")
    line = fmt(res, "`/(?<y>\\d{4})-${$y + 1}/`")
    check("EXdomain", same(res, want) and same(res, low) and in_core(line), line)


# ------------------------------------------------------------------ EXedges, EXplus (core/values/arithmetic)
def ex_edges():
    f = read_hole(r"\d+", "-", lambda y: canon(num(y) - 10) if num(y) is not None else None)
    res = modes_sem(f, ["15-5", "5--5"], "5--5 15-5", "15-5 5--5 10-0")
    want = printed([("15-5", True), ("5--5", False)], ("5--5 15-5", ("15-5", 5)),
                   ("15-5 5--5 10-0", [("15-5", 0), ("10-0", 10)]))
    g = read_hole(r"\d+", "-", lambda y: None)               # `$y % 0`: nothing, everywhere
    zero = modes_sem(g, ["5-0", "5-5"], "x5-0 5-5", "5-0 7-7 0-0")
    zero_ok = zero == ([("5-0", False), ("5-5", False)], ("x5-0 5-5", None), ("5-0 7-7 0-0", []))
    line = fmt(res, "`/(?<y>\\d+)-${$y - 10}/`: a negative result is nothing")
    check("EXedges", same(res, want) and zero_ok and in_core(line), line + " | `%% 0` never holds: %s" % zero_ok)


def plus(a, b):
    if sab("s5"):
        return a + b                                      # joining: the rejected reading
    na, nb = num(a), num(b)
    return canon(na + nb) if na is not None and nb is not None else None


def ex_plus():
    members = [plus(m, "1") for m in ["7", "x", "41"]]
    vals = [m for m in members if m is not None]
    res = modes_rx(alt(vals), ["8"], "x42 8", "8 x 42")
    want = printed([("8", True)], ("x42 8", ("42", 1)), ("8 x 42", [("8", 0), ("42", 4)]))
    line = fmt(res, "`/${[\"7\", \"x\", \"41\"] + 1}/` is `(?:8|42)`: the member `x` gives nothing")
    check("EXplus", same(res, want) and vals == (["8", "42"] if not sab("s5") else vals) and in_core(line), line)


# ------------------------------------------------------------------ EXleft (core/values/functions)
def enum_alt(strings):
    return list(strings)


def left(s, n):
    return s[-n:] if sab("s6") else s[:n]


def ex_left():
    vals = []
    for s in enum_alt(["foobar", "bazqux"]):                 # enumerate(/foobar|bazqux/), priority order
        v = left(s, 2)
        if v not in vals:
            vals.append(v)
    res = modes_rx(alt(vals), ["fo"], "xba fo", "fo ba fofo")
    want = printed([("fo", True)], ("xba fo", ("ba", 1)), ("fo ba fofo", [("fo", 0), ("ba", 3), ("fo", 6), ("fo", 8)]))
    line = fmt(res, "`/${left(/foobar|bazqux/, 2)}/` is `(?:fo|ba)`")
    check("EXleft", same(res, want) and in_core(line), line)


# ------------------------------------------------------------------ EXlift (core/arrays/lift)
def lift(op, a, b):
    if sab("s7"):
        return [op(x, y) for x, y in zip(a, b)]
    return [op(x, y) for x in a for y in b]                  # every combination, the first operand slowest


def ex_lift():
    vals = lift(plus, ["2", "4"], ["1", "10"])
    al1 = vals == ["3", "12", "5", "14"]                     # the draft's printed AL1 (array-lift, as shown to him)
    res = modes_rx(alt(vals), ["12", "4"], "x14", "3 12 5 14")
    sem = modes_sem(lambda s, i: next((i + len(v) for v in vals if s.startswith(v, i)), None),
                    ["12", "4"], "x14", "3 12 5 14")
    line = fmt(res, "`/${[2, 4] + [1, 10]}/` is `(?:3|12|5|14)`")
    pair = modes_rx(alt(["3", "14"]), ["12", "4"], "x14", "3 12 5 14")
    check("EXlift", al1 and res[0] == [("12", True), ("4", False)] and res != pair and in_core(line),
          line + " | AL1 printed [3, 12, 5, 14]: %s; the pairwise rival differs: %s" % (al1, res != pair))
    del sem


# ------------------------------------------------------------------ EXenum (core/arrays/enumerate)
def enum(node):
    """PCRE priority order of a finite rx's strings: alternatives left first; a greedy repeat one more copy first."""
    kind = node[0]
    if kind == "lit":
        yield node[1]
    elif kind == "alt":
        for n in node[1]:
            yield from enum(n)
    elif kind == "seq":
        def go(parts):
            if not parts:
                yield ""
                return
            for a in enum(parts[0]):
                for b in go(parts[1:]):
                    yield a + b
        yield from go(node[1])
    elif kind == "rep":
        _, sub, mn, mx = node

        def go(k):
            for a in enum(sub):
                if k + 1 < mx:
                    for b in go(k + 1):
                        yield a + b
                if k + 1 >= mn:
                    yield a
        if mn == 0:
            raise ValueError("not used here")
        yield from go(0)


def ex_enum():
    node = ("rep", ("alt", [("lit", "a"), ("lit", "ab")]), 1, 2)
    lst = []
    for s in enum(node):
        if s not in lst:
            lst.append(s)
    if sab("s8"):
        lst = sorted(lst, key=lambda s: -len(s[:2]) if False else 0)
        lst = ["aa", "aab", "aba", "abab", "a", "ab"]
    printed_ok = lst == ["aa", "aab", "a", "aba", "abab", "ab"]
    joined = alt(lst)
    res = modes_rx(joined, ["aba"], "aba", "aab aba")
    own = modes_rx(r"(?:a|ab){1,2}", ["aba"], "aba", "aab aba")
    texts = [""] + ["".join(p) for n in range(1, 6) for p in __import__("itertools").product("ab", repeat=n)]
    differ = [0, 0, 0]
    for t in texts:
        a, b = re.compile(joined), re.compile(r"(?:a|ab){1,2}")
        differ[0] += (a.fullmatch(t) is None) != (b.fullmatch(t) is None)
        ma, mb = a.search(t), b.search(t)
        differ[1] += (ma and (ma.span())) != (mb and (mb.span()))
        differ[2] += [m.span() for m in a.finditer(t)] != [m.span() for m in b.finditer(t)]
    line = fmt(res, "`/${enumerate(/(?:a|ab){1,2}/)}/` is `(?:aa|aab|a|aba|abab|ab)`")
    check("EXenum", printed_ok and same(res, own) and differ == [0, 0, 0] and in_core(line),
          line + " | priority list printed by the draft: %s; against `(?:a|ab){1,2}` itself %d / %d / %d of %d texts"
          % (printed_ok, differ[0], differ[1], differ[2], len(texts)))


# ------------------------------------------------------------------ class order (core/arrays/class-*)
DIGITS = [str(d) for d in range(10)]


def class_lift(results_per_member):
    """class-order: one class position's results, the longer first; equal strings one result."""
    out = []
    for r in results_per_member:
        if r is not None and r not in out:
            out.append(r)
    if sab("s9"):
        return sorted(out, key=lambda r: (int(r)))            # codepoint-of-member order, ascending values
    return sorted(out, key=lambda r: -len(r))                # stable: ties keep the member order (unobservable)


def ex_classorder():
    vals = class_lift([plus(d, "1") for d in DIGITS])
    res = modes_rx(alt(vals), ["10"], "x10", "10 3 11")
    want = printed([("10", True)], ("x10", ("10", 1)), ("10 3 11", [("10", 0), ("3", 3), ("1", 5), ("1", 6)]))
    code = modes_rx(alt([plus(d, "1") for d in DIGITS]), ["10"], "x10", "10 3 11")
    line = fmt(res, "`/${\\d + 1}/` is `(?:10|1|2|3|4|5|6|7|8|9)`")
    check("EXclassorder", same(res, want) and code != res and in_core(line),
          line + " | the codepoint rival SEARCHED %s" % (code[1][1],))


def ex_classpos():
    # C1: the lift as one position, its results longest first
    allr = []
    for a in DIGITS:
        for b in DIGITS:
            r = plus(a, b)
            if r not in allr:
                allr.append(r)
    c1 = sorted(allr, key=lambda r: -len(r))
    # C2: the first class slowest, ascending; within each, the second's results longest first
    c2 = []
    for a in DIGITS:
        for r in sorted([plus(a, b) for b in DIGITS], key=lambda r: -len(r)):
            if r not in c2:
                c2.append(r)
    if sab("s10"):
        c2 = c1
    r1 = modes_rx(alt(c1), ["13"], "x13", "13 4 18")
    r2 = modes_rx(alt(c2), ["13"], "x13", "13 4 18")
    w1 = printed([("13", True)], ("x13", ("13", 1)), ("13 4 18", [("13", 0), ("4", 3), ("18", 5)]))
    w2 = printed([("13", True)], ("x13", ("1", 1)), ("13 4 18", [("1", 0), ("3", 1), ("4", 3), ("1", 5), ("8", 6)]))
    l1 = fmt(r1, "C1, `/${\\d + \\d}/`: the lift's results longest first")
    l2 = fmt(r2, "C2: the first class slowest, ascending")
    check("EXclasspos", same(r1, w1) and same(r2, w2) and in_core(l1) and in_core(l2), l1 + " || " + l2)


def ex_classindex():
    a_vals = class_lift([plus(d, "1") for d in DIGITS])      # (a) a lift of enumerate(X) lifts the class
    b_vals = [plus(d, "1") for d in DIGITS]                  # (b) the array's codepoint order, lifted as given
    if sab("s11"):
        b_vals = a_vals
    ra = modes_rx(alt(a_vals), ["10"], "x10", "10 3 11")
    rb = modes_rx(alt(b_vals), ["10"], "x10", "10 3 11")
    wa = printed([("10", True)], ("x10", ("10", 1)), ("10 3 11", [("10", 0), ("3", 3), ("1", 5), ("1", 6)]))
    wb = printed([("10", True)], ("x10", ("1", 1)), ("10 3 11", [("1", 0), ("3", 3), ("1", 5), ("1", 6)]))
    la = fmt(ra, "(a), `/${enumerate(/\\d/) + 1}/` as the class")
    lb = fmt(rb, "(b): the array's codepoint order")
    check("EXclassindex", same(ra, wa) and same(rb, wb) and in_core(la) and in_core(lb), la + " || " + lb)


# ------------------------------------------------------------------ EXprec (core/operators/precedence)
def ex_prec():
    rx = r"x(?:1|2)" if sab("s12") else r"(?:x1)|2"          # SEQ tighter than `|`: (x then 1) or 2
    res = modes_rx(rx, ["2", "x2"], "x2", "x1 2 x2")
    rival = modes_rx(r"x(?:1|2)", ["2", "x2"], "x2", "x1 2 x2")
    line = fmt(res, "`\"x\" SEQ \"1\" | \"2\"` is `(?:x1)|2`")
    check("EXprec", res[0] == [("2", True), ("x2", False)] and res != rival and in_core(line),
          line + " | the rival `x(?:1|2)` differs: %s" % (res != rival))


# ------------------------------------------------------------------ EXpair (core/operators/bindings)
def ex_pair():
    rx = r"(\d),\1" if sab("s13") else r"(?:\d),(?:\d)"     # each mention is the inserted pattern, not a backreference
    res = modes_rx(rx, ["1,2"], "x1,2", "1,2 3,3")
    rival = modes_rx(r"(\d),\1", ["1,2"], "x1,2", "1,2 3,3")
    line = fmt(res, "`pair(p) := /${p},${p}/`, `pair(/\\d/)` is `(?:\\d),(?:\\d)`")
    check("EXpair", res[0] == [("1,2", True)] and res != rival and in_core(line), line)


# ------------------------------------------------------------------ the documents (readings 1, 2; acceptance)
def pieces(text):
    """[(tag, status, body lines)] of a base file, in order."""
    out, cur = [], None
    for ln in text.split("\n"):
        m = re.match(r"### .*?\[(\S+)\]\s+(.*?)\s+(\d{4}-\d\d-\d\d)\s*$", ln)
        if m:
            cur = [m.group(1), m.group(2), []]
            out.append(cur)
            continue
        if ln.startswith("## "):
            cur = None
            continue
        if cur is not None:
            cur[2].append(ln)
    return out


def entries(text):
    out, cur = {}, None
    for ln in text.split("\n"):
        m = re.match(r"## (\S+) — ", ln)
        if m:
            cur = m.group(1)
            out[cur] = []
            continue
        if cur:
            out[cur].append(ln)
    return out


def record_titles():
    rec = read(RECORD).split("\n")
    titles, i = [], 0
    while i < len(rec):
        ln = rec[i]
        if ln.startswith("## ") or ln.startswith("### "):
            titles.append(ln.split(" ", 1)[1].strip())
        elif ln.startswith("**20") and (i == 0 or rec[i - 1].strip() == "" or rec[i - 1].startswith("#")):
            buf = ln[2:]
            j = i
            while "**" not in buf and j + 1 < len(rec):
                j += 1
                buf += " " + rec[j]
            titles.append(re.sub(r"\s+", " ", buf.split("**")[0]).strip().rstrip("."))
        i += 1
    return titles


def mine(tag):
    return any(tag.startswith(s + "/") for s in MY_SECTIONS)


def m1():
    titles = record_titles()
    ps, es = pieces(CORE), entries(DETAILS)
    bad, n = [], 0
    for tag, status, _ in ps:
        if not mine(tag) or status != "ruled":
            continue
        n += 1
        body = "\n".join(es.get(tag, []))
        items = re.findall(r'\(record: "(.*?)"\)', body, re.S)
        if sab("s14") and tag == "core/values/number-domain":
            items = []
        cited = [re.sub(r"\s+", " ", t) for t in items]
        okitems = [t for t in cited if any(t == T or T.startswith(t + " (") or T == t for T in titles)]
        if not items or len(okitems) != len(cited):
            bad.append(tag)
    check("M1", not bad, "%d ruled pieces in my sections, each with >= 1 rulings item citing a record title; bad: %s"
          % (n, bad or "none"))


def m2():
    ps = pieces(CORE)
    order = [p[0] for p in ps]
    secs = []
    for t in order:
        s = "/".join(t.split("/")[:2])
        if s not in secs:
            secs.append(s)
    bad = []
    for tag, _, body in ps:
        if not mine(tag):
            continue
        needs = []
        for ln in body:
            if ln.startswith("needs:"):
                needs += re.split(r"[ ,]+", ln.split(":", 1)[1].strip())
        if sab("s15") and tag == "core/values/reads":
            needs.append("core/holes/value")
        for nd in needs:
            if not nd:
                continue
            ns, ts = "/".join(nd.split("/")[:2]), "/".join(tag.split("/")[:2])
            if nd.startswith("core/") and (ns not in secs or secs.index(ns) > secs.index(ts)):
                bad.append("%s -> %s" % (tag, nd))
    check("M2", not bad, "needs: from my sections into a LATER core section: %s" % (bad or "none"))


EXPECTED_SLUGS = ["value-filter", "match-is-rx", "read-is-constant", "value-is-pattern", "number-domain",
                  "domain-components", "numeral-width", "plus-operands", "number-edges", "construction-line",
                  "array-lift", "lift-order", "class-order", "class-positions", "class-index",
                  "under-construction-class", "dollar-diagnostic", "dollar-warning", "atomic-spelling",
                  "options-spelling", "conditional-spelling", "every-pass-spelling", "import-symbols",
                  "import-several", "default-set"]


def sl():
    es = entries(DETAILS)
    have = {}
    for tag, lines in es.items():
        if not mine(tag):
            continue
        for ln in lines:
            if ln.startswith("slugs:"):
                for s in re.split(r"[ ,]+", ln.split(":", 1)[1].strip()):
                    if s:
                        have[s] = tag
    if sab("s16"):
        have.pop("number-edges", None)
    missing = [s for s in EXPECTED_SLUGS if s not in have]
    check("SL", not missing, "%d of %d slugs homed in my sections; missing: %s"
          % (len(EXPECTED_SLUGS) - len(missing), len(EXPECTED_SLUGS), missing or "none"))


def noq():
    bad = []
    for tag, status, body in pieces(CORE):
        if not mine(tag):
            continue
        sk = any(ln.strip() == "skeleton: yes" for ln in body)
        if sab("s17") and tag == "core/arrays/lift":
            sk = True
        if status == "?" or sk:
            bad.append(tag)
    n = sum(1 for p in pieces(CORE) if mine(p[0]))
    check("NOQ", not bad, "%d pieces in my sections; `?` or skeleton: %s" % (n, bad or "none"))


for fn in [ex_reads, ex_onetype, ex_domain, ex_edges, ex_plus, ex_left, ex_lift, ex_enum, ex_classorder,
           ex_classpos, ex_classindex, ex_prec, ex_pair, m1, m2, sl, noq]:
    fn()
print("preddoc3b_model: %d checks, %d failed%s" % (len(CHECKS), len(FAILED), (": " + " ".join(FAILED)) if FAILED else ""))
sys.exit(1 if FAILED else 0)
