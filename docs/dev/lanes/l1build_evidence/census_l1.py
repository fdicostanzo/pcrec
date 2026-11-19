#!/usr/bin/env python3
"""span_arms unit L1's CENSUS (docs/design/span_arms.md rev 3.2 §14.4 L1
"Census (first)", common (1), RULING-4): the MODEL's predicted movers at the
unit's base, over every `.rxt` pattern under tests/ and the bench file
docs/dev/lanes/sae1_evidence/bench_patterns.txt. The STOP rule reads the
model's predicted population (RULING-4); the two-sided observed-vs-model
compare runs at the feature's gate, not here.

THE MODEL reads no compiler code. It is an exact-set model over the BYTE
spelling (encoding `byte`, the model's only alphabet; a pattern whose text it
cannot read as bytes is abstained):

  * the scanner is census_e1.py's (`alts`, `seq_items`, `skip_class`), the
    item classes census_e2.py's (`look-ahead-pos`, `look-behind-pos`, ...);
  * each consumed one-position item (a literal, a class, an escape) is its
    exact byte set; a set of more than 128 members (PCREC_MAX_REQ_RUN_POS_SET,
    the run's domain) is a GAP: consumed, but no guard meets it or crosses it;
  * a positive lookaround's ITEM is the body's per-offset sets at signed
    offsets from its cursor (a lookahead's left-aligned from 0, a lookbehind's
    right-aligned at -1, -2, ...; an alternation body unites per offset where
    every branch reaches; a nested positive lookaround's own terms are kept
    at their own offsets); the GUARD is the item's terms outward from the
    cursor up to the first absent or out-of-domain term;
  * the guard MEETS the consumed positions at equal subject offsets, crossing
    only exact-width neighbours (a zero-width item is crossed; anything of
    variable width, a GAP, a backreference, an alternation group is a WALL
    where the guard stops); a term that passes the sequence's edge with only
    exact items crossed is an edge LEFTOVER, met with every other leftover at
    the same offset (guard against guard, the stacking case);
  * an empty meet anywhere is NEVER, propagated by D-9's never rows (CAT any
    item; ALT every arm; REP m >= 1 the body; positive LOOK the body; negative
    LOOK never not; the empty class leaf always);
  * reach 0 (TOP has no rows at L1): guards are DROPPED at the root; only
    the narrowed consumed positions remain.

Where the model narrows a consumed position, the narrowed pattern is SPELLED
(the item's text replaced by its narrowed set, `\\xHH` or `[\\xHH...]`) and
the predicted run, `req_set`, `req_byte` and `req_set_maxoff` are the
REFERENCE compiler's facts of that spelling (encoding byte), with the TOP SET
STEP applied on top: every exact one-byte position of the predicted run joins
the original `req_set` (the predicted set is the union). The narrowing and
the never bit are the model's; the run choice over the narrowed text is the
reference's own (E1/E2's method: the model's part is the spelling).

Abstained (listed): `(?x)`, `(?i)` (the spelling of a case-folded byte is
not the byte), callouts, verbs, conditionals, recursion and calls, and any
narrowing that falls on an item the spelling cannot rewrite in place (a
quantified `{n}` copy). Under-approximations, COUNTED (never predicted as a
move): guard terms dropped at a repeat's edge, at an alternation group's
edge, or at a non-cube hull (the model meets exact sets, see the report).

usage: census_l1.py PCREC TREE BENCH_FILE OUT_DIR [--model-only] [--jobs N]
  PCREC  the unit's BASE build (lists the corpus; with no --model-only it
         also compiles the spellings and the lookaround items alone)
"""
import concurrent.futures as cf
import importlib.util
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


E1 = _load("census_e1", "../sae1_evidence/census_e1.py")
E2 = _load("census_e2", "../sae2_evidence/census_e2.py")
Abstain = E1.Abstain
ABSTAINS = (E1.Abstain, E2.Abstain, E2.E1.Abstain)   # census_e2 loads its own copy of census_e1
TIMEOUT = 60
POS_SET = 128          # PCREC_MAX_REQ_RUN_POS_SET, the run's position domain
MAX_REP = 32           # PCREC_MAX_REQ_RUN_SCAN: an exact {n} copied at most this many times
ALL = frozenset(range(256))


# ---------------------------------------------------------------- byte sets

WORD = frozenset(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")
DIGIT = frozenset(b"0123456789")
SPACE = frozenset(b" \t\n\x0b\x0c\r")
HSPACE = frozenset(b" \t\xa0")
VSPACE = frozenset(b"\n\x0b\x0c\r\x85")
POSIX = {
    b"alpha": frozenset(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"),
    b"digit": DIGIT, b"alnum": frozenset(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"),
    b"upper": frozenset(b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"), b"lower": frozenset(b"abcdefghijklmnopqrstuvwxyz"),
    b"space": SPACE, b"blank": frozenset(b" \t"), b"word": WORD,
    b"xdigit": frozenset(b"0123456789abcdefABCDEF"),
    b"punct": frozenset(c for c in range(33, 127) if not chr(c).isalnum()),
    b"cntrl": frozenset(list(range(32)) + [127]), b"print": frozenset(range(32, 127)),
    b"graph": frozenset(range(33, 127)), b"ascii": frozenset(range(128)),
}
SIMPLE = {ord('n'): 10, ord('t'): 9, ord('r'): 13, ord('f'): 12, ord('e'): 27, ord('a'): 7}
CLS_ESC = {ord('d'): DIGIT, ord('w'): WORD, ord('s'): SPACE, ord('h'): HSPACE, ord('v'): VSPACE}


def esc_byte(p, i):
    """p[i] == '\\': (end, byteset) for a one-position escape, or raise Abstain."""
    n = p[i + 1] if i + 1 < len(p) else None
    if n is None:
        raise Abstain("trailing backslash")
    if n in SIMPLE:
        return i + 2, frozenset([SIMPLE[n]])
    if n in CLS_ESC:
        return i + 2, CLS_ESC[n]
    if chr(n) in "DWSHV":
        return i + 2, ALL - CLS_ESC[n + 32]
    if n == ord('x'):
        if p[i + 2:i + 3] == b"{":
            k = p.find(b"}", i + 3)
            v = int(p[i + 3:k] or b"0", 16)
            if v > 255:
                raise Abstain("\\x{} above a byte")
            return k + 1, frozenset([v])
        j = i + 2
        while j < len(p) and j < i + 4 and chr(p[j]) in "0123456789abcdefABCDEF":
            j += 1
        return j, frozenset([int(p[i + 2:j] or b"0", 16)])
    if n == ord('0'):
        j = i + 2
        while j < len(p) and j < i + 4 and chr(p[j]) in "01234567":
            j += 1
        return j, frozenset([int(p[i + 1:j], 8) & 255])
    if n == ord('o') and p[i + 2:i + 3] == b"{":
        k = p.find(b"}", i + 3)
        v = int(p[i + 3:k], 8)
        if v > 255:
            raise Abstain("\\o{} above a byte")
        return k + 1, frozenset([v])
    if n == ord('c'):
        if i + 2 >= len(p):
            raise Abstain("\\c")
        return i + 3, frozenset([p[i + 2] ^ 0x40])
    if n == ord('N') and p[i + 2:i + 3] != b"{":
        return i + 2, ALL - {10}
    if chr(n).isalnum():
        raise Abstain("escape \\" + chr(n))       # \p \X \R \N{} \Q... and backrefs: not one position here
    return i + 2, frozenset([n])                  # an escaped punctuation byte


def class_set(p, i):
    """p[i] == '[': (end, byteset)."""
    j = i + 1; neg = False
    if p[j:j + 1] == b"^":
        neg = True; j += 1
    s = set(); first = True; prev = None
    while j < len(p):
        c = p[j]
        if c == ord(']') and not first:
            j += 1; break
        first = False
        if c == ord('[') and p[j + 1:j + 2] == b":":
            k = p.find(b":]", j + 2)
            name = p[j + 2:k]; pneg = name.startswith(b"^")
            if pneg:
                name = name[1:]
            if name not in POSIX:
                raise Abstain("posix class")
            s |= (ALL - POSIX[name]) if pneg else POSIX[name]
            j = k + 2; prev = None; continue
        if c == ord('\\') and p[j + 1:j + 2] == b"b":
            lo = 8; j += 2
        elif c == ord('\\'):
            e, bs = esc_byte(p, j)
            if len(bs) == 1:
                lo = next(iter(bs))
            else:
                s |= bs; j = e; prev = None; continue
            j = e
        else:
            lo = c; j += 1
        if p[j:j + 1] == b"-" and p[j + 1:j + 2] not in (b"]", b""):
            j += 1
            if p[j] == ord('\\'):
                e, bs = esc_byte(p, j)
                if len(bs) != 1:
                    raise Abstain("class range to a class")
                hi = next(iter(bs)); j = e
            else:
                hi = p[j]; j += 1
            s |= set(range(lo, hi + 1))
        else:
            s.add(lo)
    else:
        raise Abstain("unterminated class")
    return j, frozenset(ALL - s if neg else s)


def leaf_set(p, s, ae):
    """The byte set of a one-position item text p[s:ae], or None if it is not one."""
    c = p[s]
    if c == ord('['):
        e, bs = class_set(p, s)
        return bs if e == ae else None
    if c == ord('\\'):
        e, bs = esc_byte(p, s)
        return bs if e == ae else None
    if c == ord('.'):
        return ALL - {10}
    if ae == s + 1 and chr(c) not in "()|*+?{^$":
        return frozenset([c])
    return None


# ---------------------------------------------------------------- the model

class Pos:
    """One consumed position: its byte set, the text span spelling it, and
    whether that span may be rewritten in place."""
    __slots__ = ("set", "span", "spellable", "narrow")

    def __init__(self, bs, span, spellable):
        self.set = bs; self.span = span; self.spellable = spellable; self.narrow = bs


class Look:
    __slots__ = ("terms",)          # {signed offset from the cursor: byteset}

    def __init__(self, terms):
        self.terms = terms


WALL = "wall"; ZERO = "zero"


class Res:
    def __init__(self):
        self.never = False
        self.limits = []        # under-approximations met (counted)
        self.positions = []     # every Pos the model built (consumed, outside lookaround bodies)
        self.looks = 0          # positive lookarounds seen (consumed context)


def flatten(p, a, b, res, consumed, depth=0):
    """p[a:b] (no top-level '|') -> (slots, never). Slots: Pos, Look, ZERO, WALL.
    `consumed` is False inside a lookaround body (its positions are the item,
    never spelled)."""
    slots = []; never = False
    for (s, ae, e, kind, rmin, rmax) in E1.seq_items(p, a, b):
        if rmax == 0:
            continue                                     # {0}: the unit (never not)
        quant = e > ae
        if kind == "zero":
            k = E2.item_kind(p, s, ae)
            if k in ("look-ahead-pos", "look-behind-pos"):
                ga, gb = s + (3 if k == "look-ahead-pos" else 4), ae - 1
                terms, bnever = look_item(p, ga, gb, k == "look-ahead-pos", res)
                if consumed:
                    res.looks += 1
                if bnever and rmin >= 1:
                    never = True
                if quant:
                    res.limits.append("quantified lookaround")
                    slots.append(ZERO)
                else:
                    slots.append(Look(terms))
            else:
                slots.append(ZERO)                       # negative lookaround, anchors, \b: the unit, never not
            continue
        if kind == "quote":
            body = p[s + 2:ae - 2] if p[ae - 2:ae] == b"\\E" else p[s + 2:ae]
            for k, ch in enumerate(body):
                slots.append(Pos(frozenset([ch]), None, False) if not quant else WALL)
            if consumed:
                res.limits.append("\\Q..\\E (not spelled)")
            continue
        if isinstance(kind, tuple):
            ia, ib, cap = kind[1], kind[2], kind[3]
            br = E1.alts(p, ia, ib)
            if len(br) == 1 and not quant:
                sub, nv = flatten(p, ia, ib, res, consumed, depth + 1)
                slots += sub; never = never or nv
                continue
            # alternation or quantified group: model inside, a WALL outside
            nvs = []
            for sa, sb in br:
                sub, nv = flatten(p, sa, sb, res, consumed, depth + 1)
                nv = meet_seq(sub, res) or nv
                nvs.append(nv)
            bnever = all(nvs)
            if bnever and rmin >= 1:
                never = True
            if len(br) > 1:
                res.limits.append("alternation group edge")
            if quant:
                res.limits.append("repeat edge")
            slots.append(WALL)
            continue
        # a one-position leaf, or something the model does not read
        if p[s:s + 1] == b"\\" and p[s + 1:s + 2] in (b"g", b"k") or re.match(rb"\\[1-9]", p[s:ae]):
            slots.append(WALL); continue
        try:
            bs = leaf_set(p, s, ae)
        except ABSTAINS:
            bs = None
        if bs is None:
            slots.append(WALL); continue
        if not bs and rmin >= 1:
            never = True                                  # the empty class leaf (D-9)
        if quant:
            if rmin == rmax and rmin <= MAX_REP:
                for _ in range(rmin):
                    q = Pos(bs, (s, ae), False)
                    slots.append(q)
                    if consumed:
                        res.positions.append(q)
            else:
                slots.append(WALL)
            continue
        q = Pos(bs, (s, ae), True)
        slots.append(q)
        if consumed:
            res.positions.append(q)
    return slots, never


def is_pos(x):
    return isinstance(x, Pos)


def in_domain(bs):
    return 0 < len(bs) <= POS_SET


def meet_seq(slots, res):
    """Meet every Look's guard with the consumed positions of `slots` (CAT-R,
    CAT-L), and the edge leftovers with each other (CAT-EDGE). Returns the
    never bit of the meets."""
    never = False
    left = {}; right = {}             # leftovers past the left/right edge: offset -> set
    for ci, sl in enumerate(slots):
        if not isinstance(sl, Look):
            continue
        for direction in (1, -1):
            d = 0 if direction == 1 else -1
            j = ci                    # cursor between slots[ci-1] and slots[ci+1]
            idx = ci + 1 if direction == 1 else ci - 1
            while d in sl.terms:
                g = sl.terms[d]
                if not in_domain(g):
                    break
                while 0 <= idx < len(slots) and (slots[idx] == ZERO or isinstance(slots[idx], Look)):
                    idx += direction
                if idx < 0 or idx >= len(slots):
                    # past the edge with only exact items crossed: a leftover
                    off = d - (count_exact(slots, ci, direction))
                    side = right if direction == 1 else left
                    prev = side.get(off)
                    side[off] = g if prev is None else (prev & g)
                    if prev is not None and not side[off]:
                        never = True
                    d += direction
                    continue
                t = slots[idx]
                if not is_pos(t) or not in_domain(t.set):
                    break             # WALL or GAP: the guard stops
                m = t.narrow & g
                if not m:
                    never = True      # EMPTY-MEET: the position keeps its value, the bit is set
                else:
                    t.narrow = m
                idx += direction; d += direction
    return never


def count_exact(slots, ci, direction):
    """The number of consumed positions between the cursor at slot ci and the
    edge in `direction` (all exact by construction when this is called)."""
    n = 0; idx = ci + direction
    while 0 <= idx < len(slots):
        if is_pos(slots[idx]):
            n += 1
        idx += direction
    return n if direction == 1 else -n


def look_item(p, a, b, ahead, res):
    """The ITEM of a positive lookaround body p[a:b]: ({offset: set}, never)."""
    br = E1.alts(p, a, b)
    per = []; nvs = []
    for sa, sb in br:
        sub, nv = flatten(p, sa, sb, res, False)
        nv = meet_seq(sub, res) or nv
        nvs.append(nv)
        terms = {}
        poss = [x for x in sub if x != ZERO and not isinstance(x, Look)]
        exact = all(is_pos(x) for x in poss)
        w = len(poss)
        # the body's own positions, from the cursor outward until a wall
        seq = poss if ahead else list(reversed(poss))
        for k, x in enumerate(seq):
            if not is_pos(x):
                break
            terms[k if ahead else -1 - k] = x.narrow
        if len(br) == 1:
            # nested items at their own offsets (relative to the body start / end)
            for ci, sl in enumerate(sub):
                if not isinstance(sl, Look):
                    continue
                before = sub[:ci]
                if not all(is_pos(x) or x == ZERO or isinstance(x, Look) for x in (before if ahead else sub[ci + 1:])):
                    continue
                if ahead:
                    base = sum(1 for x in before if is_pos(x))
                else:
                    base = -sum(1 for x in sub[ci + 1:] if is_pos(x))
                for off, g in sl.terms.items():
                    o = base + off
                    if ahead and o >= w and not exact:
                        continue
                    if (not ahead) and o < -w and not exact:
                        continue
                    if o in terms:
                        m = terms[o] & g
                        if not m:
                            nv = True; nvs[-1] = True
                        terms[o] = m
                    else:
                        terms[o] = g
        per.append(terms)
    never = all(nvs)
    if len(per) == 1:
        return per[0], never
    # alternation body: unite per offset where every branch reaches
    out = {}
    for off in per[0]:
        if all(off in t for t in per[1:]):
            out[off] = frozenset().union(*(t[off] for t in per))
    # keep only the contiguous run outward from the cursor
    res_terms = {}
    d = 0 if ahead else -1
    while d in out:
        res_terms[d] = out[d]; d += 1 if ahead else -1
    return res_terms, never


def model(p):
    """-> dict(never, narrowed [(span, old, new)], unspellable, limits, looks)."""
    if b"(?x" in p or b"(?i" in p or re.search(rb"\(\?[a-zA-Z-]*i[a-zA-Z-]*[:)]", p):
        raise Abstain("(?x) or (?i)")
    E2.scan(p)          # raises on callouts, verbs, conditionals, recursion, calls
    res = Res()
    nvs = []
    for sa, sb in E1.alts(p, 0, len(p)):
        sub, nv = flatten(p, sa, sb, res, True)
        nv = meet_seq(sub, res) or nv
        nvs.append(nv)
    root_never = all(nvs)
    narrowed = []; unspell = 0
    for q in res.positions:
        if q.narrow != q.set:
            if q.spellable:
                narrowed.append((q.span, q.set, q.narrow))
            else:
                unspell += 1
    return {"never": root_never, "narrowed": narrowed, "unspellable": unspell,
            "limits": sorted(set(res.limits)), "looks": res.looks}


def spell_set(bs):
    bs = sorted(bs)
    if len(bs) == 1:
        return b"\\x%02x" % bs[0]
    return b"[" + b"".join(b"\\x%02x" % c for c in bs) + b"]"


def spelling(p, narrowed):
    q = p
    for (s, e), _, new in sorted(narrowed, key=lambda x: -x[0][0]):
        q = q[:s] + spell_set(new) + q[e:]
    return q


# ---------------------------------------------------------------- population

def population(pcrec, tree, bench_file):
    pats = []
    for d, _, fs in os.walk(os.path.join(tree, "tests")):
        for f in sorted(fs):
            if not f.endswith(".rxt"):
                continue
            path = os.path.join(d, f)
            r = subprocess.run([pcrec, "--list-source", path], capture_output=True, timeout=TIMEOUT)
            if r.returncode != 0:
                continue
            for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
                x = line.split("\t")
                if len(x) >= 5 and x[0] in ("pattern", "pattern-esc"):
                    pats.append(("corpus:" + os.path.relpath(path, tree), E1.decode_escape(x[4])))
    with open(bench_file, "rb") as h:
        for n, line in enumerate(h.read().split(b"\n")):
            if not line or line.startswith(b"#"):
                continue
            pats.append(("bench:%d" % (n + 1), E1.decode_escape(line.decode("utf-8", "surrogateescape"))))
    return pats


def has_pos_look(p):
    return b"(?=" in p or b"(?<=" in p


# ---------------------------------------------------------------- observation (reference compiler)

FACTS = ("req_whole_run", "req_set", "req_set_maxoff", "req_byte")


def facts(pcrec, pat):
    try:
        r = subprocess.run([pcrec, "-p", "rx", "--features", "all", "--emit-facts=byte",
                            "--pattern", pat], capture_output=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    rows = {}; sec = None
    for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
        if line.startswith("#section "):
            sec = line.split()[1]; continue
        if line.startswith("#") or sec != "facts":
            continue
        x = line.split("\t")
        rows[(x[0], x[1])] = x
    return rows


def fval(rows, f):
    if rows is None:
        return None
    return rows.get(("byte", f), [None] * 7)[6]


def run_singles(run):
    """The exact one-byte positions of a `req_whole_run` value (listing form:
    hex bytes, `[lo-hi...]` sets, optional `/mask`)."""
    if not run or run == "none":
        return set()
    text = run.split("/")[0]
    mask = run.split("/")[1] if "/" in run else None
    out = set(); i = 0; k = 0
    while i < len(text):
        if text[i] == "[":
            j = text.index("]", i); i = j + 1; k += 1; continue
        b = int(text[i:i + 2], 16)
        if mask is None or mask[2 * k:2 * k + 2] == "ff":
            out.add(b)
        i += 2; k += 1
    return out


def set_members(v):
    if not v or v == "none":
        return set()
    return {int(x) for x in v.split(",") if x.strip().isdigit()}


def one(args):
    ref, src, pat, compile_ = args
    rec = {"src": src, "pat": pat}
    try:
        m = model(pat)
    except ABSTAINS as e:
        rec["abstain"] = str(e)
        return rec
    except Exception as e:      # a scanner failure is an abstention, listed
        rec["abstain"] = "scanner: %s" % type(e).__name__
        return rec
    rec.update(m)
    rec["model_mover"] = bool(m["never"] or m["narrowed"])
    if compile_ and rec["model_mover"]:
        r0 = facts(ref, pat)
        rec["compiled"] = r0 is not None
        if r0 is not None:
            rec["today"] = {f: fval(r0, f) for f in FACTS}
            if m["narrowed"]:
                q = spelling(pat, m["narrowed"])
                rec["spelled"] = q
                rs = facts(ref, q)
                if rs is None:
                    rec["spell_fail"] = True
                else:
                    pr = {f: fval(rs, f) for f in FACTS}
                    # THE TOP SET STEP: an exact one-byte consumed position of the
                    # chosen run joins the set; the walk applies it BEFORE the run
                    # floor (READYL1-7), so a below-floor run (`a` alone, never
                    # listed as req_whole_run) still joins: read as the narrowed
                    # one-byte positions the spelling's own set keeps, plus the
                    # listed run's exact positions.
                    tset = set_members(rec["today"]["req_set"])
                    narrow1 = {next(iter(n)) for _, _, n in m["narrowed"] if len(n) == 1}
                    step = (run_singles(pr["req_whole_run"]) | (narrow1 & set_members(pr["req_set"])))
                    pr["req_set_step"] = ",".join(str(x) for x in sorted(tset | step)) if step - tset else rec["today"]["req_set"]
                    rec["pred"] = pr
            moved = []
            if m["never"]:
                moved.append("dead")
            if rec.get("pred"):
                if rec["pred"]["req_whole_run"] != rec["today"]["req_whole_run"]:
                    moved.append("req_whole_run")
                if set_members(rec["pred"]["req_set_step"]) != set_members(rec["today"]["req_set"]):
                    moved.append("req_set")
                if rec["pred"]["req_byte"] != rec["today"]["req_byte"]:
                    moved.append("req_byte")
                if rec["pred"]["req_set_maxoff"] != rec["today"]["req_set_maxoff"]:
                    moved.append("req_set_maxoff")
            rec["moved"] = moved
        if pat_item_lowering_needed(rec):
            rec["lowerings"] = item_lowerings(ref, pat)
    return rec


def pat_item_lowering_needed(rec):
    return bool(rec.get("moved"))


def item_lowerings(ref, pat):
    try:
        its = E2.scan(pat)
    except ABSTAINS:
        return []
    out = []
    for s, e, k, text in its:
        if k in ("look-ahead-pos", "look-behind-pos"):
            out.append("%s:%s" % (k, E2.lowering(ref, text)))
    return sorted(set(out))


# ---------------------------------------------------------------- expectations (§14.2, §14.4 L1)

EXPECT = [
    # pattern, expected: set of moved facts (model's names), or set() for a non-mover.
    # req_set_maxoff is ADDED to §14.4's list on every req_set mover: a byte
    # that joins the set joins its offset table (`req_set_maxoff`, one row per
    # member), so the two move together (l1build_report.md, Census, finding 1).
    (b"xy(?=bc)[bc]c", {"req_whole_run", "req_set", "req_set_maxoff"}),
    (b"a(?=b)[bc]", {"req_whole_run", "req_set", "req_byte", "req_set_maxoff"}),
    (b"ab[xy][xy](?=(?<=xx)y)[xy]", {"req_whole_run", "req_set", "req_byte", "req_set_maxoff"}),
    (b"[ac][ac]cc(?<=acc)(?<=cc)d", {"req_whole_run", "req_set", "req_set_maxoff"}),
    (b"x(?=qr)[pq]r", {"req_whole_run", "req_set", "req_byte", "req_set_maxoff"}),
    (b"foo(?=bar)baz", {"dead"}),
    (b"(?<=ab)(?<=cb)c", {"dead"}),
    (b"xyz(?<=yz)abc", set()),
    (b"xy[ac]b(?:(?<=ab)b|c)", set()),
    (b"x(?=ab|ac)a.", set()),
    # §14.2's other L1 "same" rows
    (b"(?<=foo)bar", set()), (b"bar(?=baz)", set()), (b"(?<=ab|b)c", set()),
    (b"(?<=fo{1,3})bar", set()), (b"(?<=ab)ab[a-z]*q", set()), (b"(?<=qz)ab", set()),
    (b"(?<=e{10})eeeeeqzx", set()), (b"[a-z]?[a-z]a(?=bc)", set()),
    (b"y*(?:ab(?<=xab)c)", set()), (b"foo(?!x)bar", set()), (b"x(?!ab)ac", set()),
    (b"(?<=foo)bar(?=baz)", set()),
    # §5.2 (g) dead family and W-D8
    (b"x(?:foo(?=bar)baz)?y", set()), (b"(?:foo(?=bar)baz|q)", set()),
    (b"(?:foo(?=bar)baz){0}x", set()), (b"x[^\\x00-\\xff]y", {"dead"}),
]


def check_expect(ref, compile_):
    lines = []; bad = 0
    for pat, exp in EXPECT:
        r = one((ref, "expect", pat, compile_))
        if "abstain" in r:
            lines.append("  EXPECT %-34s ABSTAIN (%s)" % (pat.decode(), r["abstain"])); bad += 1; continue
        got = set(r.get("moved", [])) if compile_ else ({"dead"} if r["never"] else set()) | ({"narrowed"} if r["narrowed"] else set())
        if compile_:
            ok = got == exp
        else:
            ok = (bool(got) == bool(exp)) and (("dead" in got) == ("dead" in exp))
        bad += not ok
        detail = ""
        if r.get("pred"):
            detail = " pred run=%s set=%s byte=%s maxoff=%s; today run=%s set=%s byte=%s" % (
                r["pred"]["req_whole_run"], r["pred"]["req_set_step"], r["pred"]["req_byte"], r["pred"]["req_set_maxoff"],
                r["today"]["req_whole_run"], r["today"]["req_set"], r["today"]["req_byte"])
        lines.append("  EXPECT %-34s %s expected=%s model=%s%s" % (
            pat.decode(), "ok  " if ok else "DIFF", ",".join(sorted(exp)) or "-", ",".join(sorted(got)) or "-", detail))
    return lines, bad


def esc(b):
    return b.decode("latin-1").encode("unicode_escape").decode()


def main():
    a = sys.argv[1:]
    jobs = 8; compile_ = True
    if "--jobs" in a:
        k = a.index("--jobs"); jobs = int(a[k + 1]); del a[k:k + 2]
    if "--model-only" in a:
        a.remove("--model-only"); compile_ = False
    ref, tree, bench_file, out = a
    t0 = time.time()
    os.makedirs(out, exist_ok=True)
    pop = population(ref, tree, bench_file)
    seen = {}
    for src, pat in pop:
        seen.setdefault(pat, src)
    cands = [(ref, src, pat, compile_) for pat, src in seen.items() if has_pos_look(pat)]
    with cf.ThreadPoolExecutor(jobs) as ex:
        recs = list(ex.map(one, cands))
    absn = [r for r in recs if "abstain" in r]
    read = [r for r in recs if "abstain" not in r]
    mm = [r for r in read if r["model_mover"]]
    if compile_:
        movers = [r for r in mm if r.get("moved")]
    else:
        movers = mm
    def cnt(rs, pred):
        return "%d (corpus %d, bench %d)" % (sum(1 for r in rs if pred(r)),
            sum(1 for r in rs if pred(r) and r["src"].startswith("corpus:")),
            sum(1 for r in rs if pred(r) and r["src"].startswith("bench:")))
    with open(os.path.join(out, "census.tsv"), "w") as h:
        h.write("#src\tpattern\tnever\tnarrowed\tmoved\tlowerings\ttoday(run;set;byte;maxoff)\tpredicted(run;set+step;byte;maxoff)\tspelled\tlimits\tabstain\n")
        for r in sorted(recs, key=lambda r: r["src"]):
            if not (r.get("model_mover") or r.get("abstain") or r.get("limits")):
                continue
            t = r.get("today") or {}; pr = r.get("pred") or {}
            h.write("\t".join([r["src"], esc(r["pat"]), str(r.get("never", "")),
                               ";".join("%d:%s->%s" % (s[0], esc(spell_set(o)), esc(spell_set(n))) for s, o, n in r.get("narrowed", [])),
                               ",".join(r.get("moved", [])), ",".join(r.get("lowerings", [])),
                               ";".join(str(t.get(f)) for f in FACTS) if t else "",
                               ";".join(str(pr.get(f)) for f in ("req_whole_run", "req_set_step", "req_byte", "req_set_maxoff")) if pr else "",
                               esc(r.get("spelled", b"")), ",".join(r.get("limits", [])), r.get("abstain", "")]) + "\n")
    lines = [
        "population: %d rows (%d corpus, %d bench), %d distinct texts; with a positive lookaround: %d"
        % (len(pop), sum(1 for s, _ in pop if s.startswith("corpus:")), sum(1 for s, _ in pop if s.startswith("bench:")),
           len(seen), len(cands)),
        "abstained: %s" % cnt(absn, lambda r: True),
        "read by the model: %s" % cnt(read, lambda r: True),
        "model narrows a consumed position or proves never: %s" % cnt(mm, lambda r: True),
        "  of them never (dead): %s" % cnt(mm, lambda r: r["never"]),
        "  of them narrowing: %s (unspellable narrowings, not predicted: %d texts)" % (
            cnt(mm, lambda r: bool(r["narrowed"])), sum(1 for r in read if r["unspellable"])),
    ]
    if compile_:
        lines.append("PREDICTED MOVERS (a fact moves, or dead): %s" % cnt(movers, lambda r: True))
        for f in ("dead", "req_whole_run", "req_set", "req_byte", "req_set_maxoff"):
            lines.append("  %-16s %s" % (f, cnt(movers, lambda r, f=f: f in r["moved"])))
        lines.append("  model movers the base compiler REFUSES (not a pattern pcrec compiles): %s"
                     % cnt(mm, lambda r: not r.get("compiled")))
        lines.append("  narrowed but no fact moves (the narrowed position is not in the chosen run): %s"
                     % cnt(mm, lambda r: r.get("compiled") and not r.get("moved")))
        for r in sorted(mm, key=lambda r: r["src"]):
            if not r.get("moved"):
                lines.append("  NOT-MOVED %s %s compiled=%s" % (r["src"], esc(r["pat"]), r.get("compiled")))
        lines.append("  item lowerings among movers: " + ", ".join(
            "%s %d" % (k, sum(1 for r in movers if k in r.get("lowerings", [])))
            for k in sorted({k for r in movers for k in r.get("lowerings", [])})))
    lim = {}
    for r in read:
        for l in r["limits"]:
            lim[l] = lim.get(l, 0) + 1
    lines.append("model limits met (under-approximation, texts): " + ", ".join("%s %d" % kv for kv in sorted(lim.items())))
    ab = {}
    for r in absn:
        ab[r["abstain"]] = ab.get(r["abstain"], 0) + 1
    lines.append("abstentions by reason: " + ", ".join("%s %d" % kv for kv in sorted(ab.items())))
    for r in sorted(movers, key=lambda r: r["src"]):
        lines.append("  MOVER %s %s moved=%s" % (r["src"], esc(r["pat"]), ",".join(r.get("moved", ["model"]))))
    el, bad = check_expect(ref, compile_)
    lines.append("§14.4 expected movers / non-movers (%d rows, %d disagreements):" % (len(EXPECT), bad))
    lines += el
    lines.append("== census COMPLETE: %d predicted movers (%s), %d expectation disagreements, %.0f s"
                 % (len(movers), "model+reference" if compile_ else "model only", bad, time.time() - t0))
    with open(os.path.join(out, "summary.txt"), "w") as h:
        h.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
