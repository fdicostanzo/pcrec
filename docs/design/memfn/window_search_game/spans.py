#!/usr/bin/env python3
"""spans.py -- derive D161's SPAN LIST for a PCRE pattern (lane wingame).

D161 (Frank, 2026-10-11): for "search for the window" pcrec hands the kit
(1) a list of SPANS, each an array of CLASSES (one byte set per position)
with a MOVE-BACK (span beginning -> window beginning) and an OVERSHOOT (how
far that move-back may overshoot the match beginning), and (2) a frequency
table. This module produces (1) for one pattern.

WHY AN INDEPENDENT EXTRACTOR AND NOT pcrec's FACTS. `--emit-facts` prints the
k-set walk's offsets as `[N]` (a byte COUNT, not the bytes) and the req
facts as single bytes/one run, so no listing today carries a span's classes.
This walks Python's own parse tree (`re._parser`) after a small PCRE->Python
spelling pass, in BYTE mode with ASCII classes (pcrec's non-UCP `byte`
encoding). It is checked against pcrec's own k-set walk (run_game.py's
`kset_agree` column): every fixed prefix position's class SIZE must equal the
walk's offset size. That is the control; it shares no code with pcrec.

THE MODEL. A pattern flattens to a sequence of ITEMS:
    ('pos', mask)          one consumed byte, mask = 256-bit int of its set
    ('gap', lo, hi)        a variable-width stretch (hi None = unbounded)
A SPAN is a maximal run of consecutive 'pos' items. Its start offset from the
match start is the interval [omin, omax] summed over everything before it, so

    move_back = omax          (None = unbounded: NOT expressible in D161)
    overshoot = omax - omin   (None = unbounded)

Every span is NECESSARY: on every path through the pattern every match
carries those bytes at that position relative to the span's own start.

WHAT IS LOST (each counted in `notes`, never silent):
  alt-dropped   an alternation whose branches differ: only the common head /
                tail (position-wise class hull, pcrec's cube hull) survives;
                spans required on SOME paths only are dropped.
  rep-right     `C{lo,hi}` (lo<hi): the lo copies attach to the LEFT span
                only; the right neighbour does not get them.
  lookaround    a lookaround body is ignored (zero-width).
  anchor-start  `^`/`\\A` at the head: the window search is moot (one start).
  backref/recursion/kreset/gstart/verb: read as an unbounded gap or ignored.
"""
import re
import re._parser as P
import re._constants as C

ALL = (1 << 256) - 1


def m_of(*bs):
    m = 0
    for b in bs:
        m |= 1 << b
    return m


def m_range(lo, hi):
    return ((1 << (hi + 1)) - 1) ^ ((1 << lo) - 1)


DIGIT = m_range(0x30, 0x39)
WORD = DIGIT | m_range(0x41, 0x5A) | m_range(0x61, 0x7A) | m_of(0x5F)
SPACE = m_of(9, 10, 11, 12, 13, 32)
CATS = {
    C.CATEGORY_DIGIT: DIGIT, C.CATEGORY_NOT_DIGIT: ALL ^ DIGIT,
    C.CATEGORY_WORD: WORD, C.CATEGORY_NOT_WORD: ALL ^ WORD,
    C.CATEGORY_SPACE: SPACE, C.CATEGORY_NOT_SPACE: ALL ^ SPACE,
    C.CATEGORY_LINEBREAK: m_of(10), C.CATEGORY_NOT_LINEBREAK: ALL ^ m_of(10),
}


def fold(m):
    """ASCII case closure (pcrec's byte encoding, default tables)."""
    up = (m >> 0x61 & ((1 << 26) - 1)) << 0x41
    lo = (m >> 0x41 & ((1 << 26) - 1)) << 0x61
    return m | up | lo


def popc(m):
    return bin(m).count("1")


def bytes_of(m):
    return [b for b in range(256) if m >> b & 1]


# ---- PCRE -> Python spelling ----------------------------------------------
GAPRE = r"(?:[\x00-\xff]*)"   # an unbounded gap: a superset is always sound


def _hexesc(n):
    return "\\x%02x" % n if n < 256 else None


def pcre_to_py(pat):
    """Returns (python_pattern_str, notes) or raises ValueError."""
    notes = set()
    s = pat

    def qrep(mo):
        return re.escape(mo.group(1))
    if "\\Q" in s:
        s = re.sub(r"\\Q(.*?)(?:\\E|$)", qrep, s, flags=re.S)
    s2 = re.sub(r"\(\*[A-Za-z_]+(?::[^)]*)?\)", "", s)
    if s2 != s:
        notes.add("verb")
        s = s2
    s = re.sub(r"\(\?C[0-9]*\)", "", s)
    s = re.sub(r"\(\?\|", "(?:", s)
    if re.search(r"\(\?(R|[+-]?\d+|&\w+|P>\w+)\)|\\g<[^>]+>|\\g'[^']+'", s):
        notes.add("recursion")
        s = re.sub(r"\(\?(R|[+-]?\d+|&\w+|P>\w+)\)", lambda mo: GAPRE, s)
        s = re.sub(r"\\g<[^>]+>|\\g'[^']+'", lambda mo: GAPRE, s)
    if re.search(r"\\k[<{'][^>}']+[>}']|\\g\{?-?\d+\}?|\(\?P=\w+\)|\\[1-9]", s):
        notes.add("backref")
        s = re.sub(r"\\k[<{'][^>}']+[>}']|\\g\{?-?\d+\}?|\(\?P=\w+\)|\\[1-9]\d*",
                   lambda mo: GAPRE, s)
    s = re.sub(r"\(\?<([A-Za-z_]\w*)>", r"(?P<\1>", s)
    s = re.sub(r"\(\?'([A-Za-z_]\w*)'", r"(?P<\1>", s)
    s = re.sub(r"\\x\{([0-9a-fA-F]+)\}",
               lambda mo: _hexesc(int(mo.group(1), 16)) or "\x00BAD", s)
    s = re.sub(r"\\o\{([0-7]+)\}",
               lambda mo: _hexesc(int(mo.group(1), 8)) or "\x00BAD", s)
    s = re.sub(r"\\c(.)", lambda mo: "\\x%02x" % (ord(mo.group(1).upper()) ^ 0x40), s)
    if re.search(r"\(\*(UCP|UTF|UTF8)\)", s):
        raise ValueError("ucp/utf verb (not modelled)")
    s = class_aware_escapes(s)
    if "\\K" in s:
        notes.add("kreset")
        s = s.replace("\\K", "")
    if "\\G" in s:
        notes.add("gstart")
        s = s.replace("\\G", "\\A")
    s = s.replace("\\z", "\\Z")
    if "\x00BAD" in s or re.search(r"\\[pPX]", s):
        raise ValueError("unicode-escape")
    return s, notes


# PCRE escapes Python spells differently, by context (inside a [...] class
# the replacement must not open a nested class).
_ESC_OUT = {"h": r"[\t \xa0]", "H": r"[^\t \xa0]", "v": r"[\n\x0b\x0c\r\x85]",
            "V": r"[^\n\x0b\x0c\r\x85]", "N": r"[^\n]", "C": r"[\x00-\xff]",
            "R": r"(?:\r\n|[\n\x0b\x0c\r\x85])", "e": r"\x1b"}
_ESC_IN = {"h": r"\t \xa0", "v": r"\n\x0b\x0c\r\x85", "e": r"\x1b"}
_POSIX = {"alpha": "a-zA-Z", "digit": "0-9", "alnum": "a-zA-Z0-9", "upper": "A-Z",
          "lower": "a-z", "space": r"\t\n\x0b\x0c\r ", "blank": r" \t",
          "xdigit": "0-9A-Fa-f", "word": r"\w", "cntrl": r"\x00-\x1f\x7f",
          "print": r"\x20-\x7e", "graph": r"\x21-\x7e",
          "punct": r"!-/:-@\[-`{-~", "ascii": r"\x00-\x7f"}


def class_aware_escapes(s):
    out = []
    i, n = 0, len(s)
    in_cls = False
    while i < n:
        c = s[i]
        if c == "\\" and i + 1 < n:
            d = s[i + 1]
            tab = _ESC_IN if in_cls else _ESC_OUT
            if d in tab:
                out.append(tab[d])
            elif in_cls and d in "HVNCR":
                raise ValueError("negated/structural escape in class")
            else:
                out.append(s[i:i + 2])
            i += 2
            continue
        if in_cls:
            if c == "[" and s.startswith("[:", i):
                j = s.find(":]", i + 2)
                name = s[i + 2:j] if j > 0 else ""
                if name not in _POSIX:
                    raise ValueError("posix class %r" % name)
                out.append(_POSIX[name])
                i = j + 2
                continue
            if c == "]" and not (out and out[-1] in ("[", "[^")):
                in_cls = False
            out.append(c)
            i += 1
            continue
        if c == "[":
            in_cls = True
            if s.startswith("[^", i):
                out.append("[^")
                i += 2
            else:
                out.append("[")
                i += 1
            if i < n and s[i] == "]":
                out.append("\\]")
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


# ---- flattening -----------------------------------------------------------
class Flat:
    def __init__(self):
        self.notes = set()
        self.anch_start = False


def _set_mask(items, icase):
    m = 0
    neg = False
    for op, av in items:
        if op is C.NEGATE:
            neg = True
        elif op is C.LITERAL:
            m |= 1 << av
        elif op is C.RANGE:
            m |= m_range(av[0], min(av[1], 255))
        elif op is C.CATEGORY:
            m |= CATS[av]
        else:
            raise ValueError("set-op %s" % op)
    if icase:
        m = fold(m)
    return (ALL ^ m) if neg else m


def widths(items):
    lo = hi = 0
    for it in items:
        if it[0] == "pos":
            lo += 1
            if hi is not None:
                hi += 1
        else:
            lo += it[1]
            hi = None if (hi is None or it[2] is None) else hi + it[2]
    return lo, hi


def is_pure(items):
    return all(it[0] == "pos" for it in items)


def lead(items):
    n = 0
    for it in items:
        if it[0] != "pos":
            break
        n += 1
    return n


CAP = 64   # positions expanded per repeat before the rest reads as a gap


def flatten(sub, flags, F, at_head):
    out = []
    for op, av in sub:
        icase = bool(flags & C.SRE_FLAG_IGNORECASE)
        if op is C.LITERAL:
            out.append(("pos", fold(1 << av) if icase else 1 << av))
        elif op is C.NOT_LITERAL:
            out.append(("pos", ALL ^ (fold(1 << av) if icase else 1 << av)))
        elif op is C.IN:
            out.append(("pos", _set_mask(av, icase)))
        elif op is C.ANY:
            out.append(("pos", ALL if flags & C.SRE_FLAG_DOTALL else ALL ^ m_of(10)))
        elif op in (C.MAX_REPEAT, C.MIN_REPEAT, C.POSSESSIVE_REPEAT):
            lo, hi, body = av
            hi = None if hi == C.MAXREPEAT else hi
            b = flatten(body, flags, F, at_head and not out)
            bl, bh = widths(b)
            if lo > 0:
                copies = lo
                if is_pure(b) and bl * lo > CAP:
                    copies = max(1, CAP // max(bl, 1))
                elif not is_pure(b) and lo > 4:
                    copies = 1
                for _ in range(copies):
                    out.extend(b)
                if copies < lo:
                    k = lo - copies
                    out.append(("gap", bl * k, None if bh is None else bh * k))
            if hi is None or hi > lo:
                if hi is not None and lo < hi:
                    F.notes.add("rep-right") if lo > 0 else None
                ghi = None if (hi is None or bh is None) else bh * (hi - lo)
                if hi is None and bh == 0:
                    ghi = 0
                if not (ghi == 0):
                    out.append(("gap", 0, ghi))
        elif op is C.SUBPATTERN:
            gid, addf, delf, body = av
            f2 = (flags | addf) & ~delf
            out.extend(flatten(body, f2, F, at_head and not out))
        elif op is C.ATOMIC_GROUP:
            out.extend(flatten(av, flags, F, at_head and not out))
        elif op is C.BRANCH:
            alts = [flatten(a, flags, F, at_head and not out) for a in av[1]]
            out.extend(merge_alts(alts, F))
        elif op is C.AT:
            if av in (C.AT_BEGINNING, C.AT_BEGINNING_STRING) and at_head and not out:
                if av is C.AT_BEGINNING_STRING or not flags & C.SRE_FLAG_MULTILINE:
                    F.anch_start = True
                else:
                    F.notes.add("anchor-line")
            else:
                F.notes.add("assertion")
        elif op in (C.ASSERT, C.ASSERT_NOT):
            F.notes.add("lookaround")
        elif op is C.GROUPREF:
            F.notes.add("backref")
            out.append(("gap", 0, None))
        elif op is C.GROUPREF_EXISTS:
            F.notes.add("conditional")
            a = flatten(av[1], flags, F, False)
            b = flatten(av[2], flags, F, False) if av[2] else []
            out.extend(merge_alts([a, b], F))
        else:
            raise ValueError("op %s" % op)
    return out


def merge_alts(alts, F):
    """Common head and tail of the branches (position-wise class hull), the
    middle a gap. Everything else in the branches is dropped (noted)."""
    if len(alts) == 1:
        return alts[0]
    ws = [widths(a) for a in alts]
    if all(is_pure(a) for a in alts) and len({len(a) for a in alts}) == 1:
        return [("pos", _or(a[i][1] for a in alts)) for i in range(len(alts[0]))]
    minw = min(w[0] for w in ws)
    k = min(lead(a) for a in alts)
    t = min(lead(list(reversed(a))) for a in alts)
    k = min(k, minw)
    t = min(t, minw - k)
    head = [("pos", _or(a[i][1] for a in alts)) for i in range(k)]
    tail = [("pos", _or(a[len(a) - t + i][1] for a in alts)) for i in range(t)]
    mlo = minw - k - t
    mhi = None if any(w[1] is None for w in ws) else max(w[1] for w in ws) - k - t
    mid_items_dropped = any(
        any(it[0] == "pos" for it in a[k:len(a) - t]) for a in alts)
    if mid_items_dropped:
        F.notes.add("alt-dropped")
    mid = [] if (mlo == 0 and mhi == 0) else [("gap", mlo, mhi)]
    return head + mid + tail


def _or(it):
    m = 0
    for x in it:
        m |= x
    return m


def spans_of(items):
    """[(classes, omin, omax)] -- omax None = unbounded."""
    res = []
    omin, omax = 0, 0
    cur = None
    for it in items:
        if it[0] == "pos":
            if cur is None:
                cur = ([], omin, omax)
                res.append(cur)
            cur[0].append(it[1])
            omin += 1
            omax = None if omax is None else omax + 1
        else:
            cur = None
            omin += it[1]
            omax = None if (omax is None or it[2] is None) else omax + it[2]
    return res


def extract(pat_bytes):
    """-> dict(status, spans=[{classes, move_back, overshoot}], notes, ...)"""
    try:
        s = pat_bytes.decode("latin-1")
        py, notes = pcre_to_py(s)
        tree = P.parse(py, 0)
        F = Flat()
        F.notes |= notes
        gflags = tree.state.flags
        items = flatten(list(tree), gflags, F, True)
    except (ValueError, re.error, KeyError, TypeError, RecursionError, OverflowError) as e:
        return {"status": "unparsed", "why": str(e)[:60], "spans": [], "notes": set()}
    sp = []
    for cls, omin, omax in spans_of(items):
        sp.append({"classes": cls, "omin": omin, "omax": omax,
                   "move_back": omax,
                   "overshoot": None if omax is None else omax - omin})
    w = widths(items)
    return {"status": "ok", "spans": sp, "notes": F.notes,
            "anch_start": F.anch_start, "minw": w[0], "maxw": w[1],
            "items": items}


def fmt_class(m):
    n = popc(m)
    if n == 1:
        b = bytes_of(m)[0]
        return chr(b) if 0x21 <= b < 0x7F and chr(b) not in "[]|." else "\\x%02x" % b
    if n == 256:
        return "[any]"
    if m == ALL ^ m_of(10):
        return "."
    for nm, v in (("\\d", DIGIT), ("\\w", WORD), ("\\s", SPACE), ("\\D", ALL ^ DIGIT),
                  ("\\W", ALL ^ WORD), ("\\S", ALL ^ SPACE)):
        if m == v:
            return nm
    return "[%d]" % n


def fmt_span(sp):
    mb = "inf" if sp["move_back"] is None else sp["move_back"]
    ov = "inf" if sp["overshoot"] is None else sp["overshoot"]
    return "%s@mb=%s,ov=%s" % ("".join(fmt_class(c) for c in sp["classes"]), mb, ov)


if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        r = extract(a.encode("latin-1"))
        print(a, r["status"], sorted(r["notes"]), r.get("anch_start"),
              [fmt_span(s) for s in r["spans"]])
