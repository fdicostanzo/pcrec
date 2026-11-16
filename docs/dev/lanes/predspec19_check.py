# predspec19: evidence for predicates_draft.md rev 19 (the other-side sigil). A COPY of predspec18_check.py (the
# original is not edited): every rev 18 population re-run with the tuple bodies RE-EXPRESSED over FIELD REFERENCES,
#     lex_ge2(s, lo) := [(s[1]: padded(>lo[1])), (s[1]: padded(==lo[1]), s[2]: padded(>=lo[2]))]
# where s is an array of field references written at the call site (`[^h, ^m]`), plus the populations for the
# reference's BINDING rule (table (B)). What changes in the emulation is WHERE the compared label comes from:
#   - a reference `^h` is a pair (operand it was resolved against, label), fixed WHERE IT IS WRITTEN: the operand a
#     condition written in place of the call would read (§4.1's lookup at the call's place);
#   - the body's condition `(s[k]: S)` is laid against the BODY'S operand; a reference resolved against a different
#     operand is a COMPILE ERROR (raised as RefError and counted, never answered);
#   - an index past the end of the reference array is an ABSENT entry: its condition is false (§3.2 tool 1).
# Every call of the re-expressed body is ALSO answered by rev 18's label-name form (`bound18`, verbatim) and the two
# are compared (XCHK: 0 differ expected). The expectations stay INTEGER ORDER from the subject's digits.
#
# rev 18's header, kept for the populations:
# predspec18: evidence for predicates_draft.md rev 18 (review r17-predspec17 fixes). A COPY of predspec17_check.py
# (engine helpers verbatim; the original is not edited) extended with the populations review r17 found missing.
# Every regex verdict is computed by libpcre2-8 (public API, ctypes) AND Python `re`; every call asserts the two
# engines agree (0 disagreements expected). The expectations are INTEGER ORDER computed in Python from the subject's
# digits (`truth`, `cmp_prefix`), never from the bodies under test.
#
# THE BODIES, emulated as the draft writes them (§8 TUPLE COMPARISONS): one bound = `[ ]` of n entries (any one);
# entry k = s[1](padded(==b1)) & ... & s[k](padded(OP bk)); a condition `(lab: padded(S))` HOLDS iff the label was
# reached (§4.2) and EVERY iteration's text (one for a set-once label; §4.3 sequence rule for a repeated one; vacuous
# over zero iterations of a reached loop) is matched whole by `0*(?:SET)`; an UNSET label fails every condition on it.
# An index past an array's end is an ABSENT entry and a condition on it is false (§3.2 tool 1, as rev 17 reads it):
# the wrong-length call is RUN, never refused by this script (review r17 F6: rev 17's refusal was the script's raise).
#
# (D)  rev 17's populations (always-set digit labels), as before: 25,848 cases expected, 0 differ.
# (R)  rev 16's bundled bodies vs the decomposed form: 7,528 cases, 0 differ.
# (U)  OPTIONAL and NON-DIGIT compared labels (F1, F2): the halves and between against the DECIDED-PREFIX order
#      (fields compared first to last; a field that is unset or not digits, reached before the order is decided,
#      makes the match INCOMPARABLE); the strict forms in both spellings (rev 17's `P & !lex_le` and rev 18's
#      `lex_ge & !lex_le`) and equality.
# (Z)  BOUND LITERALS with leading zeros (F3): `[09, 00]` under the two readings of §2.4's clause (the literal's
#      width vs the integer's value); and BOUNDS FROM THE SAME MATCH `[$a1, $a2]` with zero-padded captured text.
# (L)  REPEATED compared labels (F4): a label repeated in the PROJECTION (`[(h:), (h:)]`), and LOOPED labels under
#      the sequence rule, against "every tuple in range" and against the in-item spelling (the call inside the loop).
# (N)  WRONG-LENGTH calls (F6): what the bodies give by §3.2's absent-entry rule.
# (S)  the worked example PROGRAMS SEARCHED (F5): some span matched whole by the program; the pinned forms.
# (C)  a COMPUTED label as a compared field (rulings R-2): a month name's index beside a year.
# (W)  the worked rows of §8 rev 18 (rev 17's 35 rows, the restored `\d+`-fields row, the new rows).
import ctypes, itertools, json, re

L = ctypes.CDLL("libpcre2-8.so.0")
L.pcre2_compile_8.restype = ctypes.c_void_p
L.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                              ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32,
                            ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_data_free_8.argtypes = [ctypes.c_void_p]
ANCH, ENDANCH = 0x80000000, 0x20000000
_cache = {}
DISAGREE = [0]
L.pcre2_config_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
_vb = ctypes.create_string_buffer(64)
L.pcre2_config_8(11, _vb)                       # PCRE2_CONFIG_VERSION
print("libpcre2-8", _vb.value.decode(), "| Python", __import__("sys").version.split()[0])


def _code(p):
    if p not in _cache:
        e, o = ctypes.c_int(), ctypes.c_size_t()
        c = L.pcre2_compile_8(p.encode(), len(p.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        assert c, (p, e.value)
        _cache[p] = c
    return _cache[p]


def py(p):
    p = p.replace(r"\z", r"\Z").replace("(?<", "(?P<").replace("(?P<=", "(?<=").replace("(?P<!", "(?<!")
    return re.sub(r"^\(\?([a-z]+)\)(.*)$", r"(?\1:\2)", p, flags=re.S)


def whole(p, t):
    """p matches all of t (a filter role on the stretch t), both engines."""
    c = _code(p)
    md = L.pcre2_match_data_create_from_pattern_8(c, None)
    rc = L.pcre2_match_8(c, t.encode(), len(t.encode()), 0, ANCH | ENDANCH, md, None)
    L.pcre2_match_data_free_8(md)
    a = rc >= 0
    b = re.fullmatch(py(p), t) is not None
    if a != b:
        DISAGREE[0] += 1
        print("  ENGINE DISAGREEMENT", repr(p), repr(t), a, b)
    return a


def yn(b):
    return "accept" if b else "reject"


def canon(pred, top=130):
    vs = [str(v) for v in range(top) if pred(v)]
    return "(?:" + "|".join(vs) + ")" if vs else "(?!)"


OPS = {">": lambda a, b: a > b, ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
       "==": lambda a, b: a == b}


def comparison_set(op, atom, reading):
    """the comparison set `OP atom`. reading "value": the atom's integer value, canonical numerals (rev 18).
    reading "width": a numeral atom WITH a leading zero keeps its width: exactly len(atom) digits, zero-filled
    (the other reading of §2.4's "unless the literal has them"). A non-digit atom: the empty set."""
    if not re.fullmatch(r"\d+", atom):
        return "(?!)"
    v = int(atom)
    if reading == "width" and len(atom) > 1 and atom[0] == "0":
        w = len(atom)
        vs = ["%0*d" % (w, x) for x in range(10 ** w) if OPS[op](x, v)]
        return "(?:" + "|".join(vs) + ")" if vs else "(?!)"
    return canon(lambda x: OPS[op](x, v), top=max(130, 2 * v + 2))   # every numeral up to twice the bound


def padded(op, atom, reading="value"):
    return "0*(?:%s)" % comparison_set(op, atom, reading)


class Vals(dict):
    """a match's labels, remembering the OPERAND (the author's pattern) they were read from"""
    operand = None


class Ref:
    """a field reference `^lab`, resolved where it is WRITTEN against `operand` (the pattern text)"""
    def __init__(self, operand, lab):
        self.operand, self.lab = operand, lab

    def __repr__(self):
        return "^" + self.lab


class RefError(Exception):
    pass


XCHK = [0, 0]          # [calls answered by both forms, calls where rev 19's form differs from rev 18's]


def labels(P, s, item=None):
    """the author's pattern matched WHOLE on s: {label: None (unset) | [iteration texts]} or None (no match).
    item: for a pattern that is one loop `(?:ITEM,)*`, the iterations are the ITEM matches in order (§4.3)."""
    if not whole(P, s):
        return None
    if item is not None:
        its = list(re.finditer(py(item), s))
        names = re.compile(py(item)).groupindex
        r = Vals({n: [m.group(n) for m in its] for n in names})
        r.operand = P
        return r
    m = re.fullmatch(py(P), s)
    r = Vals({k: (None if v is None else [v]) for k, v in m.groupdict().items()})
    r.operand = P
    return r


def cond(vals, lab, rx):
    """(lab: rx): unset fails (§4.2); every iteration in rx (§4.3), vacuous over zero iterations of a reached loop"""
    v = vals.get(lab)
    return v is not None and all(whole(rx, t) for t in v)


def bound18(vals, proj, b, n, strict, last, reading="value"):
    """rev 18's form, VERBATIM: proj is a list of label names (the accessors / sections)"""

    for k in range(n):
        ok = True
        for i in range(k + 1):
            op = "==" if i < k else (last if k == n - 1 else strict)
            if i >= len(proj) or i >= len(b) or not cond(vals, proj[i], padded(op, b[i], reading)):
                ok = False
                break
        if ok:
            return True
    return False




def cond_ref(vals, operand, ref, rx):
    """the body's `(s[k]: rx)`: the parameter is bound to a field reference (the one ruled-in change, §4.1); the
    condition is laid against the body's operand; a reference resolved elsewhere is a compile error"""
    if ref.operand != operand:
        raise RefError("%r names a label of %s; this condition reads %s" % (ref, ref.operand, operand))
    return cond(vals, ref.lab, rx)


def bound19(vals, operand, s_refs, b, n, strict, last, reading="value"):
    """rev 19's body: [ (s[1]: padded(strict b1)), (s[1]: padded(==b1), s[2]: padded(strict b2)), ...,
    (... s[n]: padded(last bn)) ]; s[k] past the end of the reference array (or b[k] past the bounds) is ABSENT"""
    for k in range(n):
        ok = True
        for i in range(k + 1):
            op = "==" if i < k else (last if k == n - 1 else strict)
            if i >= len(s_refs) or i >= len(b) or not cond_ref(vals, operand, s_refs[i], padded(op, b[i], reading)):
                ok = False
                break
        if ok:
            return True
    return False


def written_at_call(vals, proj):
    """the references a call WRITTEN DIRECTLY as an operand of `&` with the author's pattern gets: `[^h, ^m]` for
    proj ["h", "m"], each resolved against that pattern (every rev 18 population writes its call that way)"""
    return [p if isinstance(p, Ref) else Ref(vals.operand, p) for p in proj]


def bound(vals, proj, b, n, strict, last, reading="value", operand=None):
    refs = written_at_call(vals, proj)
    got = bound19(vals, operand if operand is not None else vals.operand, refs, b, n, strict, last, reading)
    if all(isinstance(p, str) for p in proj):
        XCHK[0] += 1
        XCHK[1] += got != bound18(vals, proj, b, n, strict, last, reading)
    return got


def ge(v, proj, lo, n=None, reading="value", operand=None):
    return bound(v, proj, lo, n or len(lo), ">", ">=", reading, operand)


def le(v, proj, hi, n=None, reading="value", operand=None):
    return bound(v, proj, hi, n or len(hi), "<", "<=", reading, operand)


def S(t):
    return [str(x) for x in t]


def cmp_prefix(vals, proj, b):
    """the expectation: integer order field by field, first to last; '<', '=', '>' when decided, None when a field
    reached before the order is decided is unset, repeated or not digits (INCOMPARABLE)"""
    for lab, x in zip(proj, b):
        t = vals.get(lab)
        if t is None or len(t) != 1 or not re.fullmatch(r"\d+", t[0]):
            return None
        a = int(t[0])
        if a != int(x):
            return "<" if a < int(x) else ">"
    return "="


tot = {}


def tally(table, key, got, want):
    d = tot.setdefault(table, {})
    n, bad = d.get(key, (0, 0))
    d[key] = (n + 1, bad + (got != want))


def report(table):
    d = tot[table]
    for k in sorted(d):
        print("  %-58s %5d cases, %d differ" % (k, d[k][0], d[k][1]))
    print("  total: %d cases, %d differ" % (sum(n for n, _ in d.values()), sum(b for _, b in d.values())))


HM = r"(?<h>\d{1,2}):(?<m>\d\d)"
HMS = r"(?<h>\d{1,2}):(?<m>\d\d):(?<sec>\d\d)"
PAST = r"(?<m>\d\d) past (?<h>\d{1,2})"
VERS = r"(?<major>0|[1-9]\d*)\.(?<minor>0|[1-9]\d*)"
SEMVER = r"(?<major>0|[1-9]\d*)\.(?<minor>0|[1-9]\d*)\.(?<patch>0|[1-9]\d*)"
HOURS = [str(i) for i in range(13)] + ["%02d" % i for i in range(10)]
MINS = ["%02d" % j for j in (0, 1, 29, 30, 31, 59)]
subs2 = ["%s:%s" % (a, b) for a in HOURS for b in MINS]
subsp = ["%s past %s" % (b, a) for a in HOURS for b in MINS]
subs3 = ["%s:%s:%s" % (a, b, c) for a in ["9", "09", "10", "8", "08", "0", "00", "11"] for b in ["29", "30", "31", "00"]
         for c in ["00", "04", "05", "06", "59"]]
subsv = ["%d.%d" % (a, b) for a in range(0, 4) for b in range(0, 13)]
B2 = [(9, 0), (9, 30), (0, 0), (5, 1), (10, 0), (12, 59)]
B3 = [(9, 30, 5), (0, 0, 0), (10, 0, 0), (9, 30, 6)]


def family(table, tag, P, proj, subs, bounds, strict_rows):
    """the halves, between, equality and the strict forms against cmp_prefix"""
    for s in subs:
        v = labels(P, s)
        for lo in bounds:
            c = None if v is None else cmp_prefix(v, proj, lo)
            g = v is not None and ge(v, proj, S(lo))
            l = v is not None and le(v, proj, S(lo))
            tally(table, tag + "  lex_ge", g, c in (">", "="))
            tally(table, tag + "  lex_le", l, c in ("<", "="))
            tally(table, tag + "  equal = lex_between(lo, lo)", g and l, c == "=")
            if "17" in strict_rows:
                tally(table, tag + "  above, rev 17: P & !lex_le", v is not None and not l, c == ">")
                tally(table, tag + "  below, rev 17: P & !lex_ge", v is not None and not g, c == "<")
            if "18" in strict_rows:
                tally(table, tag + "  above, rev 18: lex_ge & !lex_le", g and not l, c == ">")
                tally(table, tag + "  below, rev 18: lex_le & !lex_ge", l and not g, c == "<")
            for hi in bounds:
                ch = None if v is None else cmp_prefix(v, proj, hi)
                tally(table, tag + "  lex_between", g and v is not None and le(v, proj, S(hi)),
                      c in (">", "=") and ch in ("<", "="))


# ---------------------------------------------------------------------------------------------------- table (D)
print()
print("(D) rev 17's populations (every compared label set, digits) vs integer lexicographic order; rev 17's rows")
family("D", "2 h:m      [h, m]", HM, ["h", "m"], subs2, B2, "17")
family("D", "2 m past h [h, m]", PAST, ["h", "m"], subsp, B2, "17")
family("D", "3 h:m:s    [h, m, sec]", HMS, ["h", "m", "sec"], subs3, B3, "17")
family("D", "2 versions [major, minor]", VERS, ["major", "minor"], subsv, [(1, 4), (0, 9), (1, 10), (2, 0)], "17")
report("D")
print("(D') the same populations, rev 18's strict spelling (lex_ge & !lex_le, lex_le & !lex_ge)")
family("D'", "2 h:m      [h, m]", HM, ["h", "m"], subs2, B2, "18")
family("D'", "3 h:m:s    [h, m, sec]", HMS, ["h", "m", "sec"], subs3, B3, "18")
tot["D'"] = {k: v for k, v in tot["D'"].items() if "rev 18" in k}
report("D'")

# ---------------------------------------------------------------------------------------------------- table (R)
print()
print("(R) rev 16's bundled body vs the decomposed form (author pattern = the same field patterns and separator)")
n = bad = 0
for pats, sep, subs, bounds, P, proj in [
        ([r"\d{1,2}", r"\d\d"], ":", subs2, B2, HM, ["h", "m"]),
        ([r"\d{1,2}", r"\d\d", r"\d\d"], ":", subs3, B3, HMS, ["h", "m", "sec"])]:
    p16 = re.escape(sep).join("(?<t%d>(?:%s))" % (i + 1, a) for i, a in enumerate(pats))
    proj16 = ["t%d" % (i + 1) for i in range(len(pats))]
    for s in subs:
        v, v16 = labels(P, s), labels(p16, s)
        for lo in bounds:
            for hi in bounds:
                n += 1
                a = v is not None and ge(v, proj, S(lo)) and le(v, proj, S(hi))
                b = v16 is not None and ge(v16, proj16, S(lo)) and le(v16, proj16, S(hi))
                bad += a != b
print("  %d cases, %d differ" % (n, bad))

# ---------------------------------------------------------------------------------------------------- table (U)
print()
print("(U) OPTIONAL and NON-DIGIT compared labels vs the decided-prefix order (incomparable = every form rejects)")
OPT = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
subso = [a + b for a in HOURS for b in [""] + [":" + m for m in MINS]]
NOND = r"(?<h>\w{1,2}):(?<m>\w\w)"
subsn = ["%s:%s" % (a, b) for a in ["9", "09", "10", "8", "ab", "x", "1a"] for b in ["00", "30", "59", "ab", "3x"]]
OPT3 = r"(?<h>\d{1,2}):(?<m>\d\d)(?::(?<sec>\d\d))?"
subso3 = [a + ":" + b + c for a in ["9", "09", "10", "8", "11"] for b in ["29", "30", "31", "00"]
          for c in ["", ":00", ":05", ":06", ":59"]]
family("U", "opt  h(:m)?        [h, m]", OPT, ["h", "m"], subso, B2, "17,18")
family("U", "nond \\w h:\\w m      [h, m]", NOND, ["h", "m"], subsn, B2, "17,18")
family("U", "opt3 h:m(:sec)?    [h, m, sec]", OPT3, ["h", "m", "sec"], subso3, B3, "17,18")
report("U")
v = labels(OPT, "9")
print("  witness '9' (m unset), bound [9, 30]: lex_ge2 %s, lex_le2 %s; rev 17 above %s and below %s at once; "
      "rev 18 above %s, below %s" % (ge(v, ["h", "m"], ["9", "30"]), le(v, ["h", "m"], ["9", "30"]),
                                     not le(v, ["h", "m"], ["9", "30"]), not ge(v, ["h", "m"], ["9", "30"]),
                                     ge(v, ["h", "m"], ["9", "30"]) and not le(v, ["h", "m"], ["9", "30"]),
                                     le(v, ["h", "m"], ["9", "30"]) and not ge(v, ["h", "m"], ["9", "30"])))
v = labels(OPT, "10")
print("  witness '10' (m unset): lex_between2([^h, ^m], [9, 30], [11, 0]) -> %s (decided by h; m never read)"
      % yn(ge(v, ["h", "m"], ["9", "30"]) and le(v, ["h", "m"], ["11", "0"])))
v = labels(NOND, "ab:00")
print("  witness 'ab:00' (\\w field), bound [9, 0]: rev 17 above %s, rev 18 above %s"
      % (not le(v, ["h", "m"], ["9", "0"]), ge(v, ["h", "m"], ["9", "0"]) and not le(v, ["h", "m"], ["9", "0"])))

# ---------------------------------------------------------------------------------------------------- table (Z)
print()
print("(Z) bound literals with LEADING ZEROS, and bounds from the same match, under the two readings of an atom")
for reading in ("width", "value"):
    for lo, hi in [(("09", "00"), ("10", "00")), (("9", "0"), ("10", "0")), (("09", "30"), ("09", "59"))]:
        for s in subs2:
            v = labels(HM, s)
            t = cmp_prefix(v, ["h", "m"], lo), cmp_prefix(v, ["h", "m"], hi)
            tally("Z", "reading=%s  [%s]..[%s]" % (reading, ", ".join(lo), ", ".join(hi)),
                  ge(v, ["h", "m"], list(lo), reading=reading) and le(v, ["h", "m"], list(hi), reading=reading),
                  t[0] in (">", "=") and t[1] in ("<", "="))
CAP = r"(?<a1>\d\d):(?<a2>\d\d)-(?<b1>\d{1,2}):(?<b2>\d\d)"
subsc = ["%s:%s-%s:%s" % (a1, a2, b1, b2) for a1 in ("08", "09", "10") for a2 in ("00", "05", "30")
         for b1 in ("8", "9", "09", "10") for b2 in ("00", "05", "30", "59")]
for reading in ("width", "value"):
    for s in subsc:
        v = labels(CAP, s)
        lo = [v["a1"][0], v["a2"][0]]                    # [$a1, $a2]: the captured TEXT, zero-padded by \d\d
        tally("Z", "reading=%s  lex_ge2([^b1, ^b2], [$a1, $a2])" % reading,
              ge(v, ["b1", "b2"], lo, reading=reading), cmp_prefix(v, ["b1", "b2"], lo) in (">", "="))
report("Z")
v = labels(HM, "9:30")
print("  witness '9:30' in [09, 00]..[10, 00]: width reading %s, value reading %s"
      % (yn(ge(v, ["h", "m"], ["09", "00"], reading="width") and le(v, ["h", "m"], ["10", "00"], reading="width")),
         yn(ge(v, ["h", "m"], ["09", "00"]) and le(v, ["h", "m"], ["10", "00"]))))

# ---------------------------------------------------------------------------------------------------- table (L)
print()
print("(L) REPEATED compared labels")
print("  (L1) a label twice in the projection: /(?<h>\\d{1,2}):(?<m>\\d\\d)/ & lex_ge2([^h, ^h], lo)")
for lo in [(9, 30), (9, 5), (9, 0)]:
    acc = [s for s in subs2 if ge(labels(HM, s), ["h", "h"], S(lo))]
    h_gt = [s for s in subs2 if int(s.split(":")[0]) > lo[0]]
    h_ge = [s for s in subs2 if int(s.split(":")[0]) >= lo[0]]
    meant = [s for s in subs2 if cmp_prefix(labels(HM, s), ["h", "m"], lo) in (">", "=")]
    empty2 = not any(OPS["=="](x, lo[0]) and OPS[">="](x, lo[1]) for x in range(130))
    print("    lo %-8s accepts %3d of %d; = 'h > %d': %s; = 'h >= %d': %s; = the meant [h, m] compare: %s; "
          "entry 2 (h == %d & h >= %d) empty (dead.branch fires): %s"
          % (list(lo), len(acc), len(subs2), lo[0], acc == h_gt, lo[0], acc == h_ge, acc == meant, lo[0], lo[1], empty2))
print("    '9:45' with lo [9, 30]: %s (the meant [^h, ^m] compare: %s)"
      % (yn(ge(labels(HM, "9:45"), ["h", "h"], ["9", "30"])), yn(ge(labels(HM, "9:45"), ["h", "m"], ["9", "30"]))))
LOOP = r"(?:(?<h>\d{1,2}):(?<m>\d\d),)*"
ITEM = r"(?<h>\d{1,2}):(?<m>\d\d),"
TUP = ["8:00,", "8:59,", "9:00,", "9:15,", "9:30,", "10:00,", "11:00,"]
subsl = [""] + TUP + [a + b for a in TUP for b in TUP]
print("  (L2) a LOOPED label: %s & lex_ge2([^h, ^m], lo), the sequence rule (§4.3, RULED CF:583)" % LOOP.replace("\\", "\\"))
for lo in [(9, 0), (9, 30)]:
    for s in subsl:
        v = labels(LOOP, s, item=ITEM)
        tups = [(int(a), int(b)) for a, b in zip(v["h"], v["m"])]
        body = ge(v, ["h", "m"], S(lo))
        in_item = all(ge(labels(HM, t.rstrip(",")), ["h", "m"], S(lo)) for t in re.findall(r"\d{1,2}:\d\d,", s))
        tally("L", "the body vs 'EVERY tuple >= lo'", body, all(t >= lo for t in tups))
        tally("L", "the body vs 'SOME tuple >= lo'", body, any(t >= lo for t in tups))
        tally("L", "in-item list_of(P & lex_ge2(...)) vs 'EVERY tuple >= lo'", in_item, all(t >= lo for t in tups))
report("L")
for s in ["", "10:00,9:30,", "9:30,10:00,", "10:00,11:00,"]:
    v = labels(LOOP, s, item=ITEM)
    print("    %-16r body (lex_ge2 [9, 0]) -> %s" % (s, yn(ge(v, ["h", "m"], ["9", "0"]))))

# ---------------------------------------------------------------------------------------------------- table (N)
print()
print("(N) WRONG-LENGTH calls, run by §3.2's absent-entry rule (no refusal exists in the bodies)")
for s in subs2:
    v = labels(HM, s)
    tally("N", "lex_ge3([^h, ^m], [9, 0, 0]) vs 'strictly above 9:00'", ge(v, ["h", "m"], ["9", "0", "0"], 3),
          cmp_prefix(v, ["h", "m"], (9, 0)) == ">")
    tally("N", "lex_ge2([^h, ^m], [9]) vs 'h > 9'", ge(v, ["h", "m"], ["9"], 2),
          cmp_prefix(v, ["h"], (9,)) == ">")
for s in subs3:
    v = labels(HMS, s)
    tally("N", "lex_ge2([^h, ^m, ^sec], [9, 30]) vs '[h, m] >= 9:30'", ge(v, ["h", "m", "sec"], ["9", "30"], 2),
          cmp_prefix(v, ["h", "m"], (9, 30)) in (">", "="))
report("N")

# ---------------------------------------------------------------------------------------------------- table (S)
print()
print("(S) the example PROGRAMS SEARCHED (some span matched whole by the program, §2.2); pinned by author boundaries")


def searched(P, proj, lo, hi, s, pin="", n=None):
    """some span s[i:j] matched whole by P with the compare holding on that span's reading; pin: the author's
    boundaries `(?<![PIN])P(?![PIN])` for the characters PIN of a field or separator (`\\d:` for times, `\\d.` for
    versions), i.e. neither neighbour of the span is one of them (evaluated as that test)"""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if pin and ((i > 0 and (s[i - 1].isdigit() or s[i - 1] in pin)) or
                        (j < len(s) and (s[j].isdigit() or s[j] in pin))):
                continue
            v = labels(P, s[i:j])
            if v is not None and ge(v, proj, lo, n) and (hi is None or le(v, proj, hi, n)):
                return s[i:j]
    return None


SROWS = [("time 9:00..10:00", HM, ["h", "m"], ["9", "0"], ["10", "0"], ":",
          ["19:30", "10:001", "9:30", "at 9:30 ok", "10:00:01"]),
         ("h:m:s 9:30:05..10:00:00", HMS, ["h", "m", "sec"], ["9", "30", "5"], ["10", "0", "0"], ":", ["19:30:05"]),
         ("versions 1.4..1.10", VERS, ["major", "minor"], ["1", "4"], ["1", "10"], ".",
          ["1.40", "11.4", "1.100", "v1.9"]),
         ("semver >= 1.4.0", SEMVER, ["major", "minor", "patch"], ["1", "4", "0"], None, ".", ["0.1.4.0", "v1.4.0"])]
for title, P, proj, lo, hi, pin, subj in SROWS:
    for s in subj:
        a = searched(P, proj, lo, hi, s)
        b = searched(P, proj, lo, hi, s, pin=pin)
        print("  %-24s %-12r searched -> %-6s (span %-9r) | pinned -> %s" % (title, s, yn(a is not None), a,
                                                                          yn(b is not None)))
n = bad = 0
for title, P, proj, lo, hi, pin, subs in [("time", HM, ["h", "m"], ["9", "0"], ["10", "0"], ":", subs2),
                                          ("versions", VERS, ["major", "minor"], ["1", "4"], ["1", "10"], ".", subsv)]:
    for s in subs:
        v = labels(P, s)
        n += 1
        bad += (searched(P, proj, lo, hi, s, pin=pin) is not None) != (v is not None and ge(v, proj, lo) and
                                                                          le(v, proj, hi))
print("  pinned searched vs whole-value answer on (D)'s time and version subjects: %d cases, %d differ" % (n, bad))

# ---------------------------------------------------------------------------------------------------- table (C)
print()
print("(C) a COMPUTED label as a compared field (rulings R-2): ym & lex_between2([^year, ^mnum], lo, hi),")
print("    mnum := $mname.index (the month name's 1-based position, §4.4), emulated as a label holding that numeral")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
YM = r"(?<year>\d{4})-(?<mname>%s)" % "|".join(MONTHS)


def ym_labels(s):
    v = labels(YM, s)
    if v is not None:
        v["mnum"] = [str(MONTHS.index(v["mname"][0]) + 1)]       # the computed label: a canonical numeral
    return v


subsy = ["%d-%s" % (y, m) for y in (2023, 2024, 2025, 2026) for m in MONTHS] + ["2024-Foo", "24-Mar"]
for lo, hi in [((2024, 3), (2025, 2)), ((2024, 12), (2025, 1)), ((2023, 1), (2023, 1))]:
    for s in subsy:
        v = ym_labels(s)
        c = None if v is None else (cmp_prefix(v, ["year", "mnum"], lo), cmp_prefix(v, ["year", "mnum"], hi))
        tally("C", "[%d, %d]..[%d, %d] vs (year, month number) order" % (lo + hi),
              v is not None and ge(v, ["year", "mnum"], S(lo)) and le(v, ["year", "mnum"], S(hi)),
              c is not None and c[0] in (">", "=") and c[1] in ("<", "="))
        tally("C", "the month NAME compared directly, [^year, ^mname] (non-digit: never read past year)",
              v is not None and ge(v, ["year", "mname"], S(lo)) and le(v, ["year", "mname"], S(hi)),
              c is not None and v is not None and int(v["year"][0]) > lo[0] and int(v["year"][0]) < hi[0])
report("C")

# ---------------------------------------------------------------------------------------------------- table (W)
print()
print("(W) the worked rows of §8 (rev 18, and rev 19's looped rows), each subject matched WHOLE by the filter")


def ex(title, f, rows):
    print("  " + title)
    b = 0
    for s, want in rows:
        got = f(s)
        b += got != want
        print("    %-14r -> %-6s %s" % (s, yn(got), "" if got == want else "  UNEXPECTED (stated %s)" % yn(want)))
    return b


def betw(P, proj, lo, hi, reading="value"):
    def f(s):
        v = labels(P, s)
        return v is not None and ge(v, proj, lo, reading=reading) and le(v, proj, hi, reading=reading)
    return f


bad = rows = 0
W = [
    ('/(?<h>\\d{1,2}):(?<m>\\d\\d)/ & lex_between2([^h, ^m], [9, 0], [10, 0])',
     betw(HM, ["h", "m"], ["9", "0"], ["10", "0"]),
     [("9:00", True), ("09:30", True), ("9:59", True), ("10:00", True),
      ("10:01", False), ("8:59", False), ("11:00", False), ("9:5", False)]),
    ('/(?<m>\\d\\d) past (?<h>\\d{1,2})/ & lex_between2([^h, ^m], [9, 0], [10, 0])  (labels in the other order)',
     betw(PAST, ["h", "m"], ["9", "0"], ["10", "0"]),
     [("30 past 9", True), ("00 past 10", True), ("01 past 10", False), ("59 past 8", False)]),
    ('/(?<h>\\d{1,2}):(?<m>\\d\\d):(?<sec>\\d\\d)/ & lex_between3([^h, ^m, ^sec], [9, 30, 5], [10, 0, 0])',
     betw(HMS, ["h", "m", "sec"], ["9", "30", "5"], ["10", "0", "0"]),
     [("9:30:05", True), ("09:30:05", True), ("9:59:59", True), ("10:00:00", True),
      ("9:30:04", False), ("10:00:01", False), ("8:59:59", False), ("9:30", False)]),
    ('/(?<major>0|[1-9]\\d*)\\.(?<minor>0|[1-9]\\d*)/ & lex_between2([^major, ^minor], [1, 4], [1, 10])',
     betw(VERS, ["major", "minor"], ["1", "4"], ["1", "10"]),
     [("1.4", True), ("1.9", True), ("1.10", True),
      ("1.3", False), ("1.11", False), ("2.0", False), ("0.9", False), ("1.04", False), ("1x4", False)]),
    ('semver & lex_ge3([^major, ^minor, ^patch], [1, 4, 0])  (the 2026-11-14 record\'s shape)',
     lambda s: labels(SEMVER, s) is not None and ge(labels(SEMVER, s), ["major", "minor", "patch"], ["1", "4", "0"]),
     [("1.4.0", True), ("1.10.2", True), ("2.0.0", True), ("1.3.99", False), ("0.9.9", False), ("1.04.0", False)]),
    ('/(?<major>\\d+)\\.(?<minor>\\d+)/ & lex_between2([^major, ^minor], [1, 4], [1, 10])  (rev 16 row, restored)',
     betw(r"(?<major>\d+)\.(?<minor>\d+)", ["major", "minor"], ["1", "4"], ["1", "10"]),
     [("1.04", True), ("01.10", True), ("1.010", True), ("1.011", False)]),
    ('/(?<h>\\d{1,2})(?::(?<m>\\d\\d))?/ & lex_between2([^h, ^m], [9, 30], [11, 0])  (m OPTIONAL; rev 18)',
     betw(OPT, ["h", "m"], ["9", "30"], ["11", "0"]),
     [("10", True), ("9:45", True), ("9", False), ("11", False), ("11:00", True)]),
    ('strictly above 9:30: P & lex_ge2(s, [9, 30]) & !lex_le2(s, [9, 30]), P = the optional-minutes pattern (rev 18)',
     lambda s: (lambda v: v is not None and ge(v, ["h", "m"], ["9", "30"]) and not le(v, ["h", "m"], ["9", "30"]))(
         labels(OPT, s)),
     [("9:31", True), ("10", True), ("9:30", False), ("9", False), ("8", False)]),
    ('/(?<h>\\d{1,2}):(?<m>\\d\\d)/ & lex_between2([^h, ^m], [09, 00], [10, 00])  (leading-zero bounds; rev 18)',
     betw(HM, ["h", "m"], ["09", "00"], ["10", "00"]),
     [("9:30", True), ("09:30", True), ("9:00", True), ("10:01", False)]),
]
W += [
    ('/(?:(?<h>\\d{1,2}):(?<m>\\d\\d),)*/ & lex_ge2([^h, ^m], [9, 0])  (looped: per label; compare.looped WARNS; rev 19)',
     lambda s: ge(labels(LOOP, s, item=ITEM), ["h", "m"], ["9", "0"]),
     [("10:00,9:30,", False), ("", True), ("10:00,11:00,", True), ("9:30,10:00,", False)]),
    ('the fix compare.looped names: the compare inside the loop item, list_of(P & lex_ge2([^h, ^m], [9, 0]))-shaped',
     lambda s: all(ge(labels(HM, t.rstrip(",")), ["h", "m"], ["9", "0"]) for t in re.findall(r"\d{1,2}:\d\d,", s)),
     [("10:00,9:30,", True), ("", True), ("8:59,10:00,", False)]),
]
for title, f, rws in W:
    rows += len(rws)
    bad += ex(title, f, rws)
print("  %d worked rows, %d not as stated" % (rows, bad))

# ---------------------------------------------------------------------------------------------------- table (B)
print()
print("(B) THE BINDING RULE: a reference names a label of the operand a condition written in place of its call would")
print("    read (fixed where WRITTEN); passed into a body it keeps that operand; laid against another, a compile error")


def truth_hm(t, lo):
    """integer order of an 'h:m' text against lo, from the digits (independent of the bodies)"""
    a, b = t.split(":")
    return (int(a), int(b)) >= tuple(lo)


# (B1) a NESTED `&`: the reference is written inside a condition's set, at the inner `&`.
OUT = r"(?<h>\d{1,2})\.(?<m>\d\d)@(?<t>\d{1,2}:\d\d)"
subsb = ["%s.%s@%s" % (a, b, c) for a in ("8", "9", "10") for b in ("00", "45") for c in ("8:59", "9:00", "9:30", "10:00")]
n_b1 = diff_wrong = 0
for lo in [(9, 0), (9, 30)]:
    for s in subsb:
        v = labels(OUT, s)
        t = v["t"][0]
        inner = labels(HM, t)                                   # (t: HM & lex_ge2([^h, ^m], lo)): t's text, HM's parse
        refs = [Ref(HM, "h"), Ref(HM, "m")]                     # written at the INNER `&`: HM's h and m
        got = whole(HM, t) and bound19(inner, HM, refs, S(lo), 2, ">", ">=")
        tally("B", "B1 nested: P & (t: Q & lex_ge2([^h, ^m], lo)) vs Q's fields in t", got, truth_hm(t, lo))
        wrong = bound19(v, OUT, [Ref(OUT, "h"), Ref(OUT, "m")], S(lo), 2, ">", ">=")   # the OUTER fields instead
        diff_wrong += wrong != got
        n_b1 += 1
print("  B1: reading the OUTER operand's h, m instead would answer differently in %d of %d cases (the rule decides)"
      % (diff_wrong, n_b1))

# (B2) written at the CALL SITE and passed through a library body that applies it to the SAME operand:
#      wrap(s, lo) := lex_ge2(s, lo);  HM & wrap([^h, ^m], lo)  vs  HM & lex_ge2([^h, ^m], lo)
# (B3) written INSIDE a library body: at_least(x, lo) := x & lex_ge2([^h, ^m], lo); at_least(HM, lo), PAST alike
# (B4) a BOUND call: late := lex_ge2([^h, ^m], [9, 30]); HM & late, PAST & late (the reference is resolved where the
#      bound macro's operand is filled; under the strictly visible-`&` reading this is REFUSED instead)
for lo in B2:
    for P, subs in [(HM, subs2), (PAST, subsp)]:
        for s in subs:
            v = labels(P, s)
            direct = ge(v, ["h", "m"], S(lo))
            truth = cmp_prefix(v, ["h", "m"], lo) in (">", "=")
            if P == HM:
                tally("B", "B2 HM & wrap([^h, ^m], lo) vs integer order", bound19(v, HM, [Ref(HM, "h"), Ref(HM, "m")],
                                                                        S(lo), 2, ">", ">="), truth)
            body_refs = [Ref(P, "h"), Ref(P, "m")]              # the body's own `&`: x, filled by P at expansion
            tally("B", "B3 at_least(P, lo), refs in the body (P = HM, PAST)", bound19(v, P, body_refs, S(lo), 2,
                                                                                   ">", ">="), truth)
            tally("B", "B4 P & late (bound call; P = HM, PAST) vs direct", bound19(v, P, [Ref(P, "h"), Ref(P, "m")],
                                                                              S(lo), 2, ">", ">="), direct)

# (B5) passed into a body that lays it against ANOTHER operand: inner(s, lo) := PAST & lex_ge2(s, lo);
#      HM & inner([^h, ^m], lo). The references name HM's h, m; the conditions read PAST: refused, never answered.
refused = silent = n5 = 0
for lo in B2:
    for s in subs2:
        n5 += 1
        try:
            bound19(labels(PAST, "%s past %s" % (s.split(":")[1], s.split(":")[0])), PAST,
                    [Ref(HM, "h"), Ref(HM, "m")], S(lo), 2, ">", ">=")
        except RefError:
            refused += 1
print("  B5: HM & inner([^h, ^m], lo), inner's compare at another operand (PAST): %d of %d calls refused at compile"
      " time" % (refused, n5))
try:
    bound19(labels(PAST, "30 past 9"), PAST, [Ref(HM, "h"), Ref(HM, "m")], ["9", "0"], 2, ">", ">=")
except RefError as e:
    print("    the error: %s" % e)
report("B")
print()
print("(X) rev 19's re-expressed body vs rev 18's label-name body, every call of every population above: %d calls, "
      "%d differ" % tuple(XCHK))
print()
print("engine disagreements: %d" % DISAGREE[0])
