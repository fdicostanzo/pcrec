#!/usr/bin/env python3
"""predmap_runs.py -- lane predmap: runs for the study of a map accessor m[key].

Run:  python3 -I docs/dev/lanes/predmap_evidence/predmap_runs.py   (seconds)
Last line: `predmap_runs: N cases, K failed`; exit 1 iff K > 0.

WHAT IT IS.  A MECHANICAL LOWERING of each proposed form to the python `re`
regex it would be, then the three modes on a several-match subject:
  a map            -> the alternation of its elements in written order, each
                      element under its label, (?P<label>(?:rx))
  a selection      -> the alternation of the chosen elements IN THE KEY'S ORDER
                      (an element chosen twice: its second copy unlabelled)
  join / list_of / any_order -> the sequence / the separated list / the
                      permutation alternation of the same elements
  a key read at match time -> the finite expansion, checked against a
                      reference that reads the key (a differential)
WHAT IT IS NOT.  Nothing here is the language: the lowering is the study's
model of the owner's proposal and of the manager's statement (not ruled).
Where a rule is modelled from a quoted sentence the sentence is named at the
model.  Candidate choices (what a numeral-like name does, what an empty
selection does) are the study's candidates, flagged CANDIDATE.
EXPECTATIONS: `case(..., x=[...])` declares the three-mode answer; `same`,
`differ`, `raises` declare relations.  A mismatch counts as failed.
"""
import re
import re._parser as _sp
import sys

N = 0
FAILED = []
OUT = []


def emit(s):
    OUT.append(s)
    print(s)


def check(ok, what):
    global N
    N += 1
    if not ok:
        FAILED.append(what)
        emit("FAILED: " + what)


class CompileError(Exception):
    pass


NUMERAL = re.compile(r"(0|[1-9][0-9]*)\Z")


def is_numeral(s):
    return isinstance(s, int) or NUMERAL.match(s) is not None


# ---------------------------------------------------------------- the map model
class MapM:
    """A created map: an ordered list of (label, rx text).  CANDIDATE: a
    label that is a canonical numeral is refused (else m["1"] is a position)."""

    def __init__(self, items, allow_numeral_names=False):
        self.items = list(items)
        seen = set()
        for lab, _ in self.items:
            if not lab:
                raise CompileError("a map element without a label (syntax error)")
            if is_numeral(lab) and not allow_numeral_names:
                raise CompileError("label %r is a numeral: unreachable by name" % lab)
            if lab in seen:
                raise CompileError("duplicate label %r" % lab)
            seen.add(lab)

    @property
    def names(self):
        return [l for l, _ in self.items]

    def by_name(self, name):
        for l, r in self.items:
            if l == name:
                return (l, r)
        raise CompileError("no element named %r" % (name,))

    def by_pos(self, p):
        if 1 <= p <= len(self.items):
            return self.items[p - 1]
        raise CompileError("no element at position %d (the map has %d)" % (p, len(self.items)))


def lower(items):
    """alternation of (label, rx), in the order given; a repeated label's
    later copy is unlabelled (re refuses two groups of one name)."""
    if not items:
        return "(?!)"
    seen, parts = set(), []
    for lab, rx in items:
        if lab in seen:
            parts.append("(?:%s)" % rx)
        else:
            seen.add(lab)
            parts.append("(?P<%s>(?:%s))" % (lab, rx))
    return "(?:" + "|".join(parts) + ")"


def pick(m, atom):
    if isinstance(atom, int) or NUMERAL.match(atom):
        p = int(atom)
        if p == 0:
            return list(m.items)  # `[0]` is the whole rx (core/values/metadata)
        return [m.by_pos(p)]
    return [m.by_name(atom)]


def select(m, key, drop_absent=False):
    """m[key], key a list of atoms in the key's order (the lift of `|`)."""
    out = []
    for a in key:
        try:
            out += pick(m, a)
        except CompileError:
            if not drop_absent:
                raise
    return out


def key_enum(keyrx):
    """enumerate(key) for the tiny keys used here: a finite literal
    alternation in written order; an unbounded repeat is refused (lib/builtin/
    enumerate: "an infinite or over-budget rx is a compile error")."""
    lo, hi = _sp.parse(keyrx).getwidth()
    if hi >= _sp.MAXREPEAT:
        raise CompileError("key %r is infinite: enumerate refuses it" % keyrx)
    if re.search(r"[\\\[\](){}?*+.^$]", keyrx.replace("|", "")):
        raise CompileError("key %r: this model enumerates literal alternations only" % keyrx)
    return keyrx.split("|")


def select_pattern(m, keyrx, order="map"):
    """m[/keyrx/]: the names the key matches WHOLE (the selector precedent:
    lib/builtin/warn "matched whole").  order = "map" (map's own order) or
    "key" (the key's enumeration order; refused if the key is infinite)."""
    if order == "map":
        return [it for it in m.items if re.fullmatch(keyrx, it[0])]
    out = []
    for s in key_enum(keyrx):
        out += [it for it in m.items if it[0] == s]
    return out


def group_numbers(m):
    """the group NUMBER each label would get in the lowered alternation."""
    return re.compile(lower(m.items)).groupindex


# ---------------------------------------------------------------- the runner
def fmt(s):
    return "`%s`" % s


def run(rx, whole, search, findall):
    c = re.compile(rx)
    w = [(s, c.fullmatch(s) is not None) for s in whole]
    sm = c.search(search)
    s = (sm.group(), sm.start(), sm.lastgroup) if sm else None
    f = [(x.group(), x.start(), x.lastgroup) for x in c.finditer(findall)]
    return {"whole": w, "search": s, "all": f}


def line(r, search, findall):
    w = ", ".join("%s %s" % (fmt(s), "HOLDS" if ok else "FAILS") for s, ok in r["whole"])
    if r["search"]:
        t, p, l = r["search"]
        s = "%s %s@%d%s" % (fmt(search), fmt(t), p, ":" + l if l else "")
    else:
        s = "%s FAILS" % fmt(search)
    f = ", ".join("%s@%d%s" % (fmt(t), p, ":" + l if l else "") for t, p, l in r["all"])
    return "WHOLE %s / SEARCHED %s / FIND-ALL %s [%s]" % (w, s, fmt(findall), f)


RES = {}


def case(cid, rx, whole, search, findall, x=None, x_rx=None):
    """one lowered program in the three modes.  x = declared FIND-ALL answer
    as [(text, pos, label)]; x_rx = declared lowered regex."""
    r = run(rx, whole, search, findall)
    RES[cid] = r
    emit("[%s] %s :: (`%s`)" % (cid, line(r, search, findall), rx))
    if x is not None:
        check(r["all"] == x, "%s find-all %r != declared %r" % (cid, r["all"], x))
    if x_rx is not None:
        check(rx == x_rx, "%s regex %r != declared %r" % (cid, rx, x_rx))
    return r


def same(a, b, what):
    ra, rb = RES[a], RES[b]
    strip = lambda r: ([w for w in r["whole"]], r["search"] and r["search"][:2], [t[:2] for t in r["all"]])
    check(strip(ra) == strip(rb), "%s: %s and %s differ in an answer" % (what, a, b))
    emit("[same %s = %s] answers identical in all three modes (labels not compared)" % (a, b))


def differ(a, b, what):
    ra, rb = RES[a], RES[b]
    d = ra["whole"] != rb["whole"] or ra["search"] != rb["search"] or ra["all"] != rb["all"]
    check(d, "%s: %s and %s should differ" % (what, a, b))
    emit("[differ %s <> %s] some answer differs" % (a, b))


def raises(cid, thunk, text):
    try:
        thunk()
    except CompileError as e:
        emit("[%s] modes: a compile error (%s): %s" % (cid, text, e))
        check(True, cid)
        return
    emit("[%s] DID NOT RAISE (%s)" % (cid, text))
    check(False, cid + " should raise")


# ---------------------------------------------------------------- data
M0 = MapM([("a", "ab"), ("b", "a")])
S0 = "ab a b ab"
W0 = ["ab", "a", "b"]


def c0(cid, items, x=None, x_rx=None):
    return case(cid, lower(items), W0, S0, S0, x, x_rx)


TOK = MapM([("num", r"\d+"), ("id", r"[a-z]+"), ("op", r"[-+*/]")])
ST = "x1+22*y"
WT = ["22", "x", "+", "1+"]
TOK2 = MapM([("num", r"\d+"), ("id", r"[a-z0-9]+")])
ISO = MapM([("year", r"\d{4}"), ("month", r"\d\d"), ("day", r"\d\d")])
SI = "2025-01-02 31.12.1999"
WI = ["2025-01-02", "2025", "01"]

# ================================================================ SECTION 2
emit("== 2. uses of the accessor")
c0("M0", M0.items, x=[("ab", 0, "a"), ("a", 3, "b"), ("ab", 7, "a")])
c0("M0.a", pick(M0, "a"))
c0("M0[b|1]", select(M0, ["b", 1]), x=[("a", 0, "b"), ("a", 3, "b"), ("a", 7, "b")])
c0("M0[b]", select(M0, ["b"]))
c0("M0[a|1]", select(M0, ["a", 1]))
c0("M0[1|b]", select(M0, [1, "b"]))
c0("M0[a|b]", select(M0, ["a", "b"]))
c0("M0[1|2]", select(M0, [1, 2]))
c0("M0[2|1]", select(M0, [2, 1]))
same("M0[a|1]", "M0.a", "m[\"a\"|1] selects element a twice: the answers are m.a's")
same("M0[1|b]", "M0[a|b]", "a numeral and the name of the same element")
same("M0[b|1]", "M0[2|1]", "positions and names of the same elements")

case("U1", lower(TOK.items), WT, ST, ST,
     x=[("x", 0, "id"), ("1", 1, "num"), ("+", 2, "op"), ("22", 3, "num"), ("*", 5, "op"), ("y", 6, "id")])
case("U2", r"(?:\d+)\+(?:\d+)", ["1+22", "1+x"], "1+22 3+x 4+5", "1+22 3+x 4+5",
     x=[("1+22", 0, None), ("4+5", 9, None)])
case("U3.map", lower(TOK2.items), ["12ab", "12"], "12ab 7", "12ab 7",
     x=[("12", 0, "num"), ("ab", 2, "id"), ("7", 5, "num")])
case("U3.sel", lower(select(TOK2, ["id", "num"])), ["12ab", "12"], "12ab 7", "12ab 7",
     x=[("12ab", 0, "id"), ("7", 5, "id")])
case("U4", lower(select(TOK, [2])), WT, ST, ST, x=[("x", 0, "id"), ("y", 6, "id")])
case("U9", lower(select(TOK, ["num", "id"])), WT, ST, ST)

# U5/U6: a key read at match time -> finite expansion, differential vs a reading reference
def table_case(cid, m, keytexts, sep, subject, whole):
    """pattern  (?P<k>KEYS) sep ${m[$k]}  : expanded per key text; each key text is
    classified like a literal key (numeral = position, else name)."""
    alts = []
    for kt in keytexts:
        _, rx = pick(m, kt)[0]
        alts.append("%s%s(?:%s)" % (re.escape(kt), re.escape(sep), rx))
    rx = "(?:" + "|".join(alts) + ")"
    r = case(cid, rx, whole, subject, subject)
    # reference: read the key, select, match the element right after the separator
    ref, i = [], 0
    while i < len(subject):
        hit = None
        for kt in keytexts:
            if subject.startswith(kt + sep, i):
                _, erx = pick(m, kt)[0]
                mm = re.compile(erx).match(subject, i + len(kt) + len(sep))
                if mm:
                    hit = (subject[i:mm.end()], i)
                    break
        if hit:
            ref.append(hit)
            i += len(hit[0])
        else:
            i += 1
    check([t[:2] for t in r["all"]] == ref, "%s: expansion differs from the reading reference %r" % (cid, ref))
    emit("[%s ref] the reading reference (key read, element chosen, matched after the separator) gives %s"
         % (cid, ", ".join("%s@%d" % (fmt(t), p) for t, p in ref)))


KV = MapM([("int", r"\d+"), ("word", r"[a-z]+")])
table_case("U5", KV, ["int", "word"], ":", "int:12 word:ab int:x word:7 int:3", ["int:12", "int:x"])
CC = MapM([("US", "United States"), ("DE", "Germany")])
table_case("U6", CC, ["US", "DE"], "=", "US=United States DE=Germany US=Germany DE=United States",
           ["US=Germany", "DE=Germany"])
# numerals read at match time are positions (rule 4 applied to a read)
table_case("U5.pos", KV, ["1", "2", "int", "word"], ":", "1:12 2:ab 1:x int:3 word:q", ["1:12", "2:12"])

case("U7.seq", r"(?P<year>(?:\d{4}))-(?P<month>(?:\d\d))-(?P<day>(?:\d\d))", WI, SI, SI,
     x=[("2025-01-02", 0, "day")])
case("U7.dmy", r"(?P<day>(?:\d\d))\.(?P<month>(?:\d\d))\.(?P<year>(?:\d{4}))", WI, SI, SI,
     x=[("31.12.1999", 11, "year")])
case("U8", r"(?:\d{4})/(?:\d\d)", ["2025/02", "25/02"], "2025/02 25/02 1999/31", "2025/02 25/02 1999/31",
     x=[("2025/02", 0, None), ("1999/31", 14, None)])

# ================================================================ SECTION 4
emit("== 4. numbers and group numbers")
GM = MapM([("a", r"(\d)-(\d)"), ("b", r"(x)")])
gi = group_numbers(GM)
emit("[N1] map {a=/(\\d)-(\\d)/, b=/(x)/} lowered: label -> group number %s; positions are a=1, b=2" % dict(gi))
check(gi["b"] == 4 and gi["a"] == 1, "N1 group numbers shift with inner groups")
mm = re.compile(lower(GM.items)).fullmatch("x")
emit("[N1b] on `x` the lowered alternation's group 1 is %r, group 3 is %r, group 4 is %r; the element b alone `(x)` has group 1 `x`"
     % (mm.group(1), mm.group(3), mm.group(4)))
check(mm.group(1) is None and mm.group(3) is None and mm.group(4) == "x", "N1b")

NUMBER_OK = {"one written literal": True, "a sequence": False, "an inserted pattern": False,
             "an alternation of patterns": False, "a map (an alternation of its elements)": False}
for k, v in NUMBER_OK.items():
    emit("[N2] (core/labels/numbers) a group number against %s: %s" % (k, "allowed" if v else 'compile error "name the group"'))
# the model of the quoted rule is the table above; the map row is the study's application of "an alternation of patterns"

sel = select(M0, ["b", "a"])
case("N3.sel", lower(sel), W0, S0, S0)
emit("[N3] m[\"b\"|\"a\"] is an array of two: its position 1 is `b` (m's own position 2): m[\"b\"|\"a\"][1] = %s, m[1] = %s"
     % (sel[0][0], M0.by_pos(1)[0]))
check(sel[0][0] == "b" and M0.by_pos(1)[0] == "a", "N3")
case("N3.w", r"(?:(?P<w>Mon|Tue))+", ["Tue", "TueMon"], "x", "TueMon Mon",
     x=[("TueMon", 0, "w"), ("Mon", 7, "w")])
emit("[N3b] part label w over [/Mon/, /Tue/] in a loop on `TueMon`: the settings of w are `Tue`, `Mon` (w[1] as a setting = `Tue`, member 2); "
     "the array's member 1 is /Mon/: the two readings of w[1] part")
RES2 = [m.group("w") for m in re.finditer(r"(?P<w>Mon|Tue)", "TueMon")]
check(RES2 == ["Tue", "Mon"] and "Mon|Tue".split("|")[0] == "Mon", "N3b")

# ================================================================ SECTION 5
emit("== 5. selecting names by a pattern")
PN = MapM([("ab", "x"), ("a", "xy"), ("abc", "xyz"), ("b", "q")])
SP = "xyz xy x q"
WP = ["xyz", "xy", "x"]
case("P1.map", lower(select_pattern(PN, "a.*", "map")), WP, SP, SP,
     x=[("x", 0, "ab"), ("x", 4, "ab"), ("x", 7, "ab")])
case("P1.key", lower(select_pattern(PN, "abc|ab|a", "key")), WP, SP, SP,
     x=[("xyz", 0, "abc"), ("x", 4, "ab"), ("x", 7, "ab")])
case("P1.mapof", lower(select_pattern(PN, "abc|ab|a", "map")), WP, SP, SP)
same("P1.mapof", "P1.map", "the same three names, the map's order")
differ("P1.map", "P1.key", "map order against key order")
raises("P2", lambda: select_pattern(PN, "a.*", "key"), "m[/a.*/] by the key's enumeration")
emit("[P2b] by the map's own names the same key is finite: m[/a.*/] selects %s" % [l for l, _ in select_pattern(PN, "a.*", "map")])
emit("[P4] whole match: m[/a/] selects %s (not ab, abc); m[/a|b/] selects %s" %
     ([l for l, _ in select_pattern(PN, "a")], [l for l, _ in select_pattern(PN, "a|b")]))
check([l for l, _ in select_pattern(PN, "a")] == ["a"], "P4")
e = select_pattern(PN, "zz.*", "map")
case("P3.empty", lower(e), WP, SP, SP, x=[], x_rx="(?!)")
raises("P3.lit", lambda: select(PN, ["zz"]), 'm["zz"], a literal key no element has')

# ================================================================ SECTION 6
emit("== 6. names and numbers combined")
raises("K1", lambda: select(M0, ["zz", "yy"]), 'm["zz"|"yy"]')
raises("K2", lambda: select(M0, [3]), "m[3] on a map of two")
case("K3.drop", lower(select(M0, ["b", "zz"], drop_absent=True)), W0, S0, S0)
raises("K3.err", lambda: select(M0, ["b", "zz"]), 'm["b"|"zz"], one atom absent (CANDIDATE: any absent atom is the error)')
case("K4.zero", lower(select(M0, [0])), W0, S0, S0)
same("K4.zero", "M0", "m[0] is the whole rx (core/values/metadata)")
raises("K5", lambda: MapM([("1", "x"), ("b", "y")]), 'a map with the label "1" (CANDIDATE: refused)')
NM = MapM([("1", "x"), ("b", "y")], allow_numeral_names=True)
emit('[K5b] with numeral names allowed, NM["1"] is %s and NM[1] is %s: the same text names two elements' %
     (pick(NM, "1")[0], pick(NM, 1)[0]))
check(pick(NM, "1") == pick(NM, 1), 'K5b: "1" is classed as a position, so NM["1"] is element 1')
emit("[K5c] a label \"01\" or \"1a\" is not a canonical numeral: is_numeral -> %s, %s" % (is_numeral("01"), is_numeral("1a")))
check(not is_numeral("01") and not is_numeral("1a"), "K5c")

# ================================================================ SECTION 7
emit("== 7. tables of patterns")
MONTHS = MapM([(n, r) for n, r in [
    ("jan", "Jan(?:uary)?"), ("feb", "Feb(?:ruary)?"), ("mar", "Mar(?:ch)?"), ("apr", "Apr(?:il)?"),
    ("may", "May"), ("jun", "June?"), ("jul", "July?"), ("aug", "Aug(?:ust)?"), ("sep", "Sep(?:tember)?"),
    ("oct", "Oct(?:ober)?"), ("nov", "Nov(?:ember)?"), ("dec", "Dec(?:ember)?")]])
# the documents' line for month_numbered(between(1, 6)): WHOLE `Jun` HOLDS, `Jul` FAILS / SEARCHED `Dec Feb` `Feb`@4 /
# FIND-ALL `Mar Oct Apr` [`Mar`@0, `Apr`@8]
case("T1.first6", lower(select(MONTHS, [1, 2, 3, 4, 5, 6])), ["Jun", "Jul"], "Dec Feb", "Mar Oct Apr",
     x=[("Mar", 0, "mar"), ("Apr", 8, "apr")])
check(RES["T1.first6"]["whole"] == [("Jun", True), ("Jul", False)] and RES["T1.first6"]["search"][:2] == ("Feb", 4),
      "T1 reproduces the documents' month_numbered line")
case("T2.name", lower(select(MONTHS, ["mar"])), ["Mar", "March"], "Mar Oct March", "Mar Oct March")
case("T3.cc", "(?P<US>(?:United States))|(?P<DE>(?:Germany))", ["Germany", "Germany!"], "Peru Germany", "United States Germany")
emit("[T3b] backward, value to key: the label that matched is the key: `United States` -> %s"
     % re.compile(lower(CC.items)).search("United States").lastgroup)
OV = MapM([("en", "color"), ("us", "color")])
case("T4.overlap", lower(OV.items), ["color"], "color", "color color",
     x=[("color", 0, "en"), ("color", 6, "en")])
emit("[T4] two keys with one value: the backward lookup reports `en` both times; `us` is never reported (first occurrence wins)")
case("T5.filter", lower(select(TOK2, [2])), ["12ab", "12"], "12ab 7", "12ab 7", x=[("12ab", 0, "id"), ("7", 5, "id")])
emit("[T5] a test on the position of the matched alternative, `&`-kept paths in order (core/filters/and: \"P's first path with every path of Q, then P's next\"), keeps the paths through alternative 2: the answers of the selection TOK2[2] (hand-worked)")

# ================================================================ SECTION 8
emit("== 8. library namespaces")
case("L1.dot", lower(pick(ISO, "year")), ["2025", "99"], "x 2025 y", "2025 1999 x")
case("L1.br", lower(select(ISO, ["year"])), ["2025", "99"], "x 2025 y", "2025 1999 x")
same("L1.dot", "L1.br", "m.year and m[\"year\"] select the same text")
emit("[L1b] the label: m.year as a bare element carries it in the lowering %s; the one-element array m[\"year\"] keeps the label: %s"
     % (RES["L1.dot"]["all"][0][2], RES["L1.br"]["all"][0][2]))
A2 = MapM([("year", r"\d{4}"), ("tz", "Z")])
B2 = MapM([("year", r"\d\d"), ("hour", r"\d\d")])


def combine(*maps):
    names = [n for m in maps for n in m.names]
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        raise CompileError("member %s carried by two files (core/modules/conflicts)" % dup)
    return MapM([it for m in maps for it in m.items])


raises("L2", lambda: combine(A2, B2), 'import("a"|"b") with a shared member `year`')
emit("[L2b] without the clash the combined map is %s" % combine(A2, MapM([("hour", r"\d\d")])).names)
case("L3.all", r"(?:\d{4})/(?:\d\d)", ["2025/02", "25/02"], "2025/02 25/02 1999/31", "2025/02 25/02 1999/31")
same("L3.all", "U8", "(=) := iso binds year, month, day: `year \"/\" month` is `iso.year \"/\" iso.month`")

# ================================================================ SECTION 9
emit("== 9. a map under join and its siblings")
case("J0.alt", lower(ISO.items), WI, SI, "2025-01-02",
     x=[("2025", 0, "year"), ("01", 5, "month"), ("02", 8, "month")])
emit("[J0] the bare map is the alternation: on 2025-01-02, `day` is never reported (month, same text, is first)")


def join(items, sep):
    return sep.join("(?P<%s>(?:%s))" % (l, r) for l, r in items)


case("J1.join", join(ISO.items, "-"), WI, SI, SI, x=[("2025-01-02", 0, "day")])
case("J2.dmy", join(select(ISO, ["day", "month", "year"]), r"\."), ["31.12.1999", "2025-01-02"], SI, SI,
     x=[("31.12.1999", 11, "year")])
case("J2.sub", join(select(ISO, ["year", "day"]), "-"), ["2025-02", "2025-01-02"], "2025-02 1999-31", "2025-02 1999-31")
import itertools
PERM = "(?:" + "|".join(join(p, "-") if False else "-".join("(?:%s)" % r for _, r in p)
                        for p in itertools.permutations(ISO.items)) + ")"
case("J3.any", PERM, ["2025-01-02", "01-2025-02", "01-02-2025", "2025-2025-01"], "x 01-2025-02", "2025-01-02 01-02-2025 7",
     x=[("2025-01-02", 0, None), ("01-02-2025", 11, None)])
emit("[J3] any_order of 3 parts lowered: %d branches (n!), labels not carried by `re` (two groups of one name per branch are the language's union, hand-worked); 4 parts: %d branches"
     % (len(list(itertools.permutations(ISO.items))), len(list(itertools.permutations(range(4))))))
LI = select(TOK2, ["id", "num"])
case("J4.list", "(?:(?:" + "|".join("(?:%s)" % r for _, r in LI) + "),)*" + lower(LI), ["x,1,22", "x,,1"],
     "q x,1,22 y", "x,1,22 y,7",
     x=[("x,1,22", 0, "id"), ("y,7", 7, "id")])
check(len({"join": 1}) == 1, "J-sibling table is one element list: see J1-J4 built from ISO.items")
emit("[J5] one table, four combiners: the same ISO.items list feeds J0 (alternation), J1 (sequence), J3 (any order), J4's list: no second kind of map is needed to run them")
check(re.compile(J := join(ISO.items, "-")).groupindex.keys() == {"year", "month", "day"}, "J1 labels kept in the sequence lowering")
emit("[J1b] labels in the sequence lowering: %s (the lowering keeps them; lib/strings/join marks its own line on joined parts labels stale)"
     % sorted(re.compile(J).groupindex))

# ================================================================ SECTION 10
emit("== 10. candidate rules on the parting examples")
emit("[R-A] statement as put: numeral = position, other string = name, set = lift in key order, compile-time keys; m[\"a\"|1] = m0[a|1] -> see M0[a|1]")
emit("[R-C] names only in brackets (numerals refused): m[\"a\"|1] is a compile error; m[\"a\"|\"b\"] is the same as in A")


def names_only(m, key):
    for a in key:
        if is_numeral(a):
            raise CompileError("candidate C: a numeral in m[ ] is refused (names only)")
    return select(m, key)


raises("R-C.1", lambda: names_only(M0, ["a", 1]), 'candidate C on m["a"|1]')
check(names_only(M0, ["b", "a"]) == select(M0, ["b", "a"]), "R-C agrees with A on names")

# bare name key: value of a binding or the element's name
a_binding = "b"
c0("B1.name", select(M0, ["a"]))
c0("B1.value", select(M0, [a_binding]))
differ("B1.name", "B1.value", "m[a] with a := \"b\": the name a, or the binding a's value")

# ================================================================ end
emit("predmap_runs: %d cases, %d failed" % (N, len(FAILED)))
sys.exit(1 if FAILED else 0)
