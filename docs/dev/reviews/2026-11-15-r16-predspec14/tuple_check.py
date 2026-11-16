# FIXIND: exhaustive check of the O69 tuple-compare sketch (2 and 3 fields) vs lexicographic integer order.
# Field values are read by libpcre2 (whole match, named groups) and python re; each condition (l: padded(cmp)) is
# evaluated as libpcre2/re whole match of /0*(?:SET)/ on the label's text, SET = canonical numerals satisfying cmp.
import sys, re
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec14/evidence")
import predspec14_anchor as E

def canon_set(pred, top=120):
    vs = [str(v) for v in range(top) if pred(v)]
    return "(?:" + "|".join(vs) + ")" if vs else "(?!)"

def whole(p, t):
    a = E.pcre(p, t, 0, E.ANCH | E.ENDANCH) is not None
    b = re.fullmatch(E.py(p), t) is not None
    assert a == b, (p, t)
    return a

def padded(pred): return "0*(?:%s)" % canon_set(pred)
def plain(pred):  return canon_set(pred)

def fields(TP, names, s):
    if E.pcre(TP, s, 0, E.ANCH | E.ENDANCH) is None:
        return None
    out = []
    for n in names:
        a = E.whole_groups(TP, s, n)
        out.append(s[a[0]:a[1]])
    return out

# 2 fields, as written in O69 (1)
def tuple2(s, lo, hi):
    f = fields(r"(?<t1>\d{1,2}):(?<t2>\d\d)", ["t1", "t2"], s)
    if f is None:
        return False
    t1, t2 = f
    lo1, lo2 = lo; hi1, hi2 = hi
    ge = whole(padded(lambda v: v > lo1), t1) or (whole(padded(lambda v: v == lo1), t1) and whole(padded(lambda v: v >= lo2), t2))
    le = whole(padded(lambda v: v < hi1), t1) or (whole(padded(lambda v: v == hi1), t1) and whole(padded(lambda v: v <= hi2), t2))
    return ge and le

# 3 fields: LITERAL = the text's entry (t1: ==lo1, t2: ==lo2, t3: padded(>=lo3)) (equalities NOT padded),
# the strict entries before it in the same style; ALL PADDED = every comparison padded.
def tuple3(s, lo, hi, eqwrap):
    t = fields(r"(?<t1>\d{1,2}):(?<t2>\d\d):(?<t3>\d\d)", ["t1", "t2", "t3"], s)
    if t is None:
        return False
    def lex(b, strict, last):
        ents = [[(0, padded(lambda v: strict(v, b[0])))],
                [(0, eqwrap(lambda v: v == b[0])), (1, padded(lambda v: strict(v, b[1])))],
                [(0, eqwrap(lambda v: v == b[0])), (1, eqwrap(lambda v: v == b[1])), (2, padded(lambda v: last(v, b[2])))]]
        return any(all(whole(rx, t[i]) for i, rx in e) for e in ents)
    return lex(lo, lambda a, b: a > b, lambda a, b: a >= b) and lex(hi, lambda a, b: a < b, lambda a, b: a <= b)

def truth(s, lo, hi):
    return lo <= tuple(int(x) for x in s.split(":")) <= hi

bad2 = n2 = 0
subs2 = ["%s:%s" % (a, b) for a in [str(i) for i in range(0, 13)] + ["%02d" % i for i in range(0, 10)]
         for b in ["%02d" % j for j in (0, 1, 29, 30, 31, 59)]]
for lo in [(9, 0), (9, 30), (0, 0), (5, 1)]:
    for hi in [(10, 0), (9, 30), (12, 59), (5, 1)]:
        for s in subs2:
            n2 += 1
            if tuple2(s, lo, hi) != truth(s, lo, hi):
                bad2 += 1; print("2F DIFF", s, lo, hi)
print("2 fields: %d cases, %d differ from lexicographic order" % (n2, bad2))

subs3 = ["%s:%s:%s" % (a, b, c) for a in ["9", "09", "10", "8", "08", "0", "00"] for b in ["29", "30", "31", "00"]
         for c in ["00", "05", "06", "59"]]
for name, wrap in (("LITERAL (==lo unpadded)", plain), ("ALL PADDED", padded)):
    bad = n = 0; ex = []
    for lo in [(9, 30, 5), (0, 0, 0)]:
        for hi in [(10, 0, 0), (9, 30, 5)]:
            for s in subs3:
                n += 1
                got = tuple3(s, lo, hi, wrap)
                if got != truth(s, lo, hi):
                    bad += 1; ex.append((s, lo, hi, "accept" if got else "reject"))
    print("3 fields %s: %d cases, %d differ; e.g. %s" % (name, n, bad, ex[:4]))
