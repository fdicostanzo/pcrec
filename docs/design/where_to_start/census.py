#!/usr/bin/env python3
"""where_to_start.md §D: WHERE IS THE BEST NECESSARY LANDMARK? (K35: counted, with controls)

COMPILE-SIDE ONLY: no subject is matched, no clock is read, gcc is never run.

Population: the [ARTREV] generalizer's (docs/dev/optloop/artrev/gen/census.py,
imported, not copied): every pcrec-bench bench/<set>/patterns/*.rx (READ-ONLY,
--features all, -e utf8 on set `utf8`) and every `pattern`/`pattern-esc` block of
tests/**/*.rxt (deduplicated on pattern bytes, encoding, icase).

Per pattern, two independent readings:

  pcrec's   `--emit-facts`: the route (RX_ENGINE / RX_VM_PREFILTER), start_anchor,
            start_set, req_set, req_run(+maxoff), kset_walk, RX_VM_START_SCAN,
            RX_DFA_PREFILTER, RX_REQ_HANDOFF.
  ours      a small PCRE reader (this file) that flattens the pattern's TOP-LEVEL
            concatenation (un-quantified groups are spliced in, as rust's
            reverse_inner.rs `flatten` does) and lists every LANDMARK on it: a
            maximal run of single-byte (or caseless two-byte) items. For each it
            records the PREFIX P before it: byte width [min, max] (max None =
            unbounded), P's consumable alphabet, and whether P holds a
            backreference, an atomic/possessive, a lookaround or a call.

The best landmark is the one with the rarest scan byte under the shipped prior
(tests/findings/default_ppm.tsv, the same table K1 reads). It is classified by
POSITION and MAPPING STRENGTH:

  start      P has width [0,0] (only zero-width items before it)
  fixed      P has width [k,k], k > 0: hit - k is the one candidate (offset-k)
  bounded    P has width [a,b], b finite: a window [hit-b, hit-a]; also a lower
             bound hit-b for the forward scan (the K82 handoff's form)
  exact-rev  P unbounded, but the reverse walk is EXACT: P backref/atomic/
             lookaround/call-free and P cannot consume every distinct byte of L
             (rust's has_no_earlier_match, single-literal arm)
  presence   P unbounded and the gate fails: the landmark says NO only

`gain2x`: the best landmark's ppm is >= 2x rarer than what the artifact scans on
today (K1's key: the run member when a run shipped, else the start set's summed
mass; on a prefilter-less VM with no start-set hat, 1,000,000 = scans nothing).
The 2x is an UNMEASURED DEFAULT (D149), reported beside 1x and 8x.

CONTROLS (run by --selftest, transcript committed as selftest.txt):
  C1  reader positives/negatives: fixed patterns with hand-known classes.
  C2  NECESSITY, against pcrec: every byte our reader calls necessary on a
      case-sensitive byte pattern must be in pcrec's req_set where pcrec derived
      one (req_set comes from src/facts/req.c's walk, not from this reader).
      Disagreements are COUNTED in the summary, never asserted away.
  C3  FIXED OFFSET, against pcrec: where we call a landmark `fixed` at offset k
      and pcrec's kset_walk reaches offset k with a single byte, it must be our
      byte. Counted the same way.

Env: PCREC (default build/pcrec), BENCH, CORPUS, OUT. Usage:
  PCREC=build/pcrec CORPUS=. OUT=<scratch> python3 docs/design/where_to_start/census.py [--selftest] [--workers 4]
"""
import argparse, collections, concurrent.futures as cf, gzip, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location(
    "artgen_census", os.path.join(HERE, "..", "..", "dev", "optloop", "artrev", "gen", "census.py"))
G = importlib.util.module_from_spec(_spec)   # the artgen census: population, facts(), prior()
_spec.loader.exec_module(G)

E = os.environ
OUT = E.get("OUT", "build-wts")
W = G.W
ALL = set(range(256))


class Unparsed(Exception):
    pass


def esc_set(ch):
    D = set(range(48, 58)); S = {9, 10, 11, 12, 13, 32}; H = {9, 32, 0xA0}; V = {10, 11, 12, 13, 0x85}
    return {"w": W, "d": D, "s": S, "h": H, "v": V, "W": ALL - W, "D": ALL - D, "S": ALL - S,
            "H": ALL - H, "V": ALL - V, "N": ALL - {10}, "R": {10, 11, 12, 13}}.get(ch)


class Reader:
    """PCRE pattern bytes -> list of top alternatives, each a list of items:
       ('set', S, w)   one character; w = (1,1) or (1,4) for a multibyte utf8 class
       ('zw', kind)    zero-width: view (^ $ \\b ...), look (lookaround), flag
       ('bref',)       backreference (width unknown)
       ('call',)       subroutine call
       ('grp', alts, atomic)
       ('rep', item, m, M, mode)"""

    def __init__(self, p, icase, utf8):
        self.s = p.decode("latin-1"); self.i = 0; self.icase = icase; self.utf8 = utf8
        if "(?x" in self.s or "\\Q" in self.s or "(?#" in self.s or "(?|" in self.s or "(?(" in self.s:
            raise Unparsed("unsupported-syntax")

    def fold(self, st):
        if not self.icase:
            return st
        return st | {b ^ 32 for b in st if 65 <= b <= 90 or 97 <= b <= 122}

    def width_of(self, st):
        if self.utf8 and any(b >= 0x80 for b in st):
            return (1, 4)
        return (1, 1)

    def cls(self):
        s = self.s; i = self.i + 1; neg = False; out = set()
        if i < len(s) and s[i] == "^":
            neg = True; i += 1
        first = True
        while i < len(s) and (s[i] != "]" or first):
            first = False
            c = s[i]
            if c == "[":
                m = re.match(r"\[:(\^?)(\w+):\]", s[i:])
                if not m:
                    raise Unparsed("class")
                nm = {"alpha": set(range(65, 91)) | set(range(97, 123)), "digit": set(range(48, 58)),
                      "alnum": set(range(65, 91)) | set(range(97, 123)) | set(range(48, 58)),
                      "space": {9, 10, 11, 12, 13, 32}, "upper": set(range(65, 91)),
                      "lower": set(range(97, 123)), "xdigit": set(b"0123456789abcdefABCDEF"),
                      "word": W, "punct": {b for b in range(33, 127) if not chr(b).isalnum()},
                      "print": set(range(32, 127)), "graph": set(range(33, 127)), "blank": {9, 32},
                      "cntrl": set(range(32)) | {127}}.get(m.group(2))
                if nm is None:
                    raise Unparsed("posix")
                out |= (ALL - nm) if m.group(1) else nm
                i += len(m.group(0)); continue
            if c == "\\":
                i += 1
                if i >= len(s):
                    raise Unparsed("class")
                e = esc_set(s[i])
                if e is not None:
                    out |= e; i += 1; continue
                lo = {"n": 10, "t": 9, "r": 13, "f": 12, "v": 11, "e": 27, "a": 7}.get(s[i])
                if lo is None:
                    if s[i] == "x" and re.match(r"[0-9a-fA-F]{2}", s[i + 1:i + 3]):
                        lo = int(s[i + 1:i + 3], 16); i += 2
                    elif s[i].isalnum():
                        raise Unparsed("class-escape")
                    else:
                        lo = ord(s[i])
                i += 1
            else:
                lo = ord(c); i += 1
            if i + 1 < len(s) and s[i] == "-" and s[i + 1] != "]":
                hi = s[i + 1]
                if hi in "\\[":
                    raise Unparsed("class-range")
                out |= set(range(lo, ord(hi) + 1)); i += 2
            else:
                out.add(lo)
        if i >= len(s):
            raise Unparsed("class")
        self.i = i + 1
        out = self.fold(out)
        if neg:
            out = ALL - out
            return out, ((1, 4) if self.utf8 else (1, 1))
        return out, self.width_of(out)

    def atom(self):
        s = self.s; c = s[self.i]
        if c == "(":
            atomic = False
            if s.startswith("(?:", self.i):
                self.i += 3
            elif s.startswith("(?>", self.i):
                self.i += 3; atomic = True
            elif s.startswith(("(?=", "(?!"), self.i) or s.startswith(("(?<=", "(?<!"), self.i):
                self.i += 4 if s[self.i + 2] == "<" else 3
                self.alternation()
                self.close()
                return ("zw", "look")
            elif re.match(r"\(\?P?<\w+>|\(\?'\w+'", s[self.i:]):
                m = re.match(r"\(\?P?<\w+>|\(\?'\w+'", s[self.i:]); self.i += len(m.group(0))
            elif re.match(r"\(\?(\d+|[+-]\d+|R|&\w+|P>\w+)\)", s[self.i:]):
                m = re.match(r"\(\?(\d+|[+-]\d+|R|&\w+|P>\w+)\)", s[self.i:]); self.i += len(m.group(0))
                return ("call",)
            elif re.match(r"\(\?[imsxn-]+\)", s[self.i:]):
                m = re.match(r"\(\?([imsxn-]+)\)", s[self.i:]); self.i += len(m.group(0))
                f = m.group(1)
                if "x" in f.split("-")[0]:
                    raise Unparsed("x-flag")
                if "i" in f.split("-")[0]:
                    self.icase = True
                return ("zw", "flag")
            elif re.match(r"\(\?[imsxn-]+:", s[self.i:]):
                m = re.match(r"\(\?([imsxn-]+):", s[self.i:])
                if "i" in m.group(1).split("-")[0] or "x" in m.group(1):
                    raise Unparsed("scoped-flag")
                self.i += len(m.group(0))
            elif s.startswith("(*", self.i) or s.startswith("(?", self.i):
                raise Unparsed("group-kind")
            else:
                self.i += 1
            alts = self.alternation()
            self.close()
            return ("grp", alts, atomic)
        if c == "[":
            st, w = self.cls(); return ("set", st, w)
        if c == ".":
            self.i += 1; return ("set", ALL - {10}, (1, 4) if self.utf8 else (1, 1))
        if c in "^$":
            self.i += 1; return ("zw", "view")
        if c == "\\":
            n = s[self.i + 1] if self.i + 1 < len(s) else ""
            self.i += 2
            e = esc_set(n)
            if e is not None:
                return ("set", e, (1, 4) if self.utf8 and any(b >= 0x80 for b in e) else (1, 1))
            if n in "bBAzZG":
                return ("zw", "view")
            if n == "K":
                raise Unparsed("\\K")
            if n.isdigit() and n != "0":
                while self.i < len(s) and s[self.i].isdigit():
                    self.i += 1
                return ("bref",)
            if n in "gk":
                m = re.match(r"\{[^}]*\}|<[^>]*>|'[^']*'|-?\d+", s[self.i:])
                if not m:
                    raise Unparsed("\\g")
                self.i += len(m.group(0))
                return ("call",) if n == "g" and m.group(0)[0] in "<'" else ("bref",)
            m = {"n": 10, "t": 9, "r": 13, "f": 12, "e": 27, "a": 7}.get(n)
            if m is not None:
                return ("set", {m}, (1, 1))
            if n == "x" and re.match(r"[0-9a-fA-F]{2}", s[self.i:self.i + 2]):
                v = int(s[self.i:self.i + 2], 16); self.i += 2
                return ("set", self.fold({v}), (1, 1))
            if n.isalnum() or n == "":
                raise Unparsed("escape")
            return ("set", {ord(n)}, (1, 1))
        if c in "*+?{)|":
            raise Unparsed("stray")
        self.i += 1
        return ("set", self.fold({ord(c)}), (1, 1))

    def close(self):
        if self.i >= len(self.s) or self.s[self.i] != ")":
            raise Unparsed("paren")
        self.i += 1

    def quant(self, it):
        s = self.s
        while self.i < len(s):
            c = s[self.i]
            if c in "*+?":
                m, M = {"*": (0, None), "+": (1, None), "?": (0, 1)}[c]; self.i += 1
            elif c == "{":
                mm = re.match(r"\{(\d+)(,(\d*))?\}", s[self.i:])
                if not mm:
                    return it
                m = int(mm.group(1)); M = m if mm.group(2) is None else (int(mm.group(3)) if mm.group(3) else None)
                self.i += len(mm.group(0))
            else:
                return it
            mode = "greedy"
            if self.i < len(s) and s[self.i] in "?+":
                mode = "lazy" if s[self.i] == "?" else "poss"; self.i += 1
            it = ("rep", it, m, M, mode)
        return it

    def seq(self):
        items = []
        while self.i < len(self.s) and self.s[self.i] not in "|)":
            items.append(self.quant(self.atom()))
        return items

    def alternation(self):
        alts = [self.seq()]
        while self.i < len(self.s) and self.s[self.i] == "|":
            self.i += 1; alts.append(self.seq())
        return alts

    def parse(self):
        t = self.alternation()
        if self.i != len(self.s):
            raise Unparsed("trailing")
        return t


# ---- item properties -------------------------------------------------------

def props(it):
    """(minw, maxw|None, alphabet, flags) of an item. flags: bref, atomic, look, call."""
    k = it[0]
    if k == "set":
        return it[2][0], it[2][1], set(it[1]), set()
    if k == "zw":
        return 0, 0, set(), ({"look"} if it[1] == "look" else set())
    if k == "bref":
        return 0, None, set(ALL), {"bref"}
    if k == "call":
        return 0, None, set(ALL), {"call"}
    if k == "grp":
        lo, hi, al, fl = None, 0, set(), ({"atomic"} if it[2] else set())
        for a in it[1]:
            l2, h2, a2, f2 = seq_props(a)
            lo = l2 if lo is None else min(lo, l2)
            hi = None if hi is None or h2 is None else max(hi, h2)
            al |= a2; fl |= f2
        return lo or 0, hi, al, fl
    if k == "rep":
        l, h, a, f = props(it[1])
        f = set(f) | ({"atomic"} if it[4] == "poss" else set())
        if it[3] is None:
            hi = 0 if h == 0 else None
        else:
            hi = None if h is None else h * it[3]
        return l * it[2], hi, (a if it[3] != 0 else set()), f
    raise ValueError(k)


def seq_props(items):
    lo, hi, al, fl = 0, 0, set(), set()
    for it in items:
        l, h, a, f = props(it)
        lo += l; hi = None if hi is None or h is None else hi + h; al |= a; fl |= f
    return lo, hi, al, fl


def flatten(items):
    """Splice un-quantified, non-atomic, single-alternative groups (rust's flatten)."""
    out = []
    for it in items:
        if it[0] == "grp" and len(it[1]) == 1 and not it[2]:
            out += flatten(it[1][0])
        else:
            out.append(it)
    return out


def litset(it):
    """The byte set of a one-character item if it is a LANDMARK member: a single
    byte, or a caseless letter pair; else None."""
    if it[0] == "set" and it[2] == (1, 1) and (len(it[1]) == 1 or (len(it[1]) == 2 and
                                                                   len({b | 32 for b in it[1]}) == 1)):
        return frozenset(it[1])
    if it[0] == "rep" and it[2] >= 1:
        return litset(it[1])   # x+ / x{2,}: its first x is necessary where the repeat begins
    return None


def landmarks(spine):
    """[(index, [bytesets])] — maximal runs of landmark members on the spine. A
    repeat member ends its run (its later copies float)."""
    out, run, start = [], [], None
    for i, it in enumerate(spine):
        ls = litset(it)
        if ls is not None:
            if not run:
                start = i
            run.append(ls)
            if it[0] == "rep":
                out.append((start, run)); run = []
        else:
            if run:
                out.append((start, run)); run = []
    if run:
        out.append((start, run))
    return out


def ppm(bs):
    return sum(G.PRIOR.get(b, 2) for b in bs)


def classify(tree):
    """-> dict(kind, landmark, ...) or dict(kind='top-alternation'|'no-landmark')."""
    if len(tree) != 1:
        return dict(cls="top-alternation")
    spine = flatten(tree[0])
    lms = landmarks(spine)
    if not lms:
        return dict(cls="no-landmark")
    cands = []
    for start, run in lms:
        lo, hi, al, fl = seq_props(spine[:start])
        # the run's scan member: its rarest position
        k = min(range(len(run)), key=lambda q: (ppm(run[q]), q))
        Lbytes = set().union(*run)
        cands.append(dict(start=start, run=run, scan=k, ppm=ppm(run[k]), pmin=lo, pmax=hi,
                          palph=al, pflags=fl, lbytes=Lbytes))
    best = min(cands, key=lambda c: (c["ppm"], c["start"]))
    first = cands[0]
    return dict(cls="spine", best=best, first=first, ncands=len(cands))


def strength(c):
    if c["pmax"] == 0:
        return "start"
    if c["pmax"] is not None and c["pmin"] == c["pmax"]:
        return "fixed"
    if c["pmax"] is not None:
        return "bounded"
    if c["pflags"] & {"bref", "call", "atomic", "look"}:
        return "presence"
    if not (c["lbytes"] <= c["palph"]):
        return "exact-rev"
    return "presence"


def kset_list(v):
    """kset_walk value -> list of (byte or None for a multi-member set)."""
    if not v or v == "none":
        return []
    out = []
    for f in v.split(","):
        out.append(None if f.startswith("[") else int(f))
    return out


def census_row(r):
    o = dict(pop=r["pop"], id=r["id"], enc=r["enc"], icase=int(r["icase"]))
    fd, err = G.facts(r)
    if fd is None:
        o["refused"] = err; return o
    f, d = fd
    eng = d.get("ENGINE", ""); vpf = d.get("VM_PREFILTER", "")
    o["route"] = "dfa" if eng == "dfa" else ("hybrid" if vpf == "hybrid" else "vm-only")
    o["anchor"] = f.get("start_anchor", "")
    o["vm_start"] = d.get("VM_START_SCAN", ""); o["dfa_pf"] = d.get("DFA_PREFILTER", "")
    o["handoff"] = d.get("REQ_HANDOFF", ""); o["req_run"] = d.get("REQ_RUN", "")
    S = G.bitset(f.get("start_set", ""))
    req = G.intlist(f.get("req_set", "")) if f.get("req_set", "none") not in ("none", "") else []
    try:
        tree = Reader(r["pat"], r["icase"], r["enc"] == "utf8").parse()
    except (Unparsed, ValueError, IndexError) as e:
        o["parsed"] = 0; o["why_unparsed"] = (e.args[0] if e.args else type(e).__name__)
        return o
    o["parsed"] = 1
    c = classify(tree)
    o["cls"] = c["cls"]
    if c["cls"] != "spine":
        return o
    b = c["best"]
    o["strength"] = strength(b)
    o["best_ppm"] = b["ppm"]; o["best_len"] = len(b["run"])
    o["best_kind"] = "byte" if len(b["run"]) == 1 else "run"
    o["best_is_first"] = int(b is c["first"])
    # today's scan key (K1's key, extended to the VM route)
    if o["route"] == "vm-only" and vpf == "none" and o["vm_start"] in ("", "none"):
        key = 1000000
    elif o["req_run"] not in ("", "none"):
        try:
            key = G.PRIOR.get(int(d.get("REQ_BYTE", "")), 2)
        except ValueError:
            key = sum(G.PRIOR.get(x, 2) for x in S) if S is not None else 1000000
    else:
        key = sum(G.PRIOR.get(x, 2) for x in S) if S is not None else 1000000
    o["key_ppm"] = key
    ratio = key / max(1, b["ppm"])
    o["gain"] = 8 if ratio >= 8 else 2 if ratio >= 2 else 1 if ratio > 1 else 0
    # C2: necessity control, case-sensitive byte patterns only
    if not r["icase"] and r["enc"] == "byte" and req:
        mine = {x for cc in [c["best"]] for st in cc["run"] for x in st if len(st) == 1}
        o["c2_checked"] = len(mine)
        o["c2_viol"] = len(mine - set(req))
    # C3: fixed-offset control
    if o["strength"] == "fixed" and len(b["run"][0]) == 1:
        ks = kset_list(f.get("kset_walk", ""))
        k = b["pmin"]
        if k < len(ks) and ks[k] is not None:
            o["c3"] = "agree" if ks[k] == next(iter(b["run"][0])) else "disagree"
        else:
            o["c3"] = "unreached"
    return o


# ---- the selftest (C1) ------------------------------------------------------

SELF = [  # (pattern, icase, expected strength of the best landmark, or a cls)
    (b"abc", False, "start"),
    (b"\\d{3}-\\d{4}", False, "fixed"),
    (b"[a-z]{2,5}@x", False, "bounded"),
    (b"\\w+@\\w+\\.com", False, "exact-rev"),        # @ is rarest; \w cannot consume @
    (b"[a-z]+zq", False, "presence"),                # [a-z] consumes z and q: split ambiguous
    (b"(a+)\\1@", False, "presence"),                # backref in P
    (b"(?>a+)@", False, "presence"),                 # atomic in P
    (b"a|b", False, "top-alternation"),
    (b"\\w+", False, "no-landmark"),
    (b"(?:\\bat [A-Za-z0-9_$.]+)\\(", False, "exact-rev"),   # A01's shape
    (b"[^)]*\\)", False, "exact-rev"),               # [^)] cannot consume the landmark
]


def selftest():
    G.PRIOR = G.prior()
    bad = 0
    for p, ic, want in SELF:
        try:
            c = classify(Reader(p, ic, False).parse())
            got = c["cls"] if c["cls"] != "spine" else strength(c["best"])
        except Unparsed as e:
            got = "unparsed:" + str(e)
        ok = got == want
        bad += not ok
        print("%-4s %-34s want %-16s got %s" % ("ok" if ok else "FAIL", p.decode(), want, got))
    print("selftest: %d controls, %d failed" % (len(SELF), bad))
    return bad


def summarize(rows):
    L = []
    for pop in ("bench", "corpus"):
        R = [o for o in rows if o["pop"] == pop]
        ok = [o for o in R if "refused" not in o]
        parsed = [o for o in ok if o.get("parsed")]
        unanch = [o for o in parsed if o["anchor"] == "unanchored"]
        L.append("## %s: %d patterns, %d compiled, parsed %d (%.0f%%); unanchored+parsed %d"
                 % (pop, len(R), len(ok), len(parsed), 100.0 * len(parsed) / max(1, len(ok)), len(unanch)))
        why = collections.Counter(o.get("why_unparsed") for o in ok if not o.get("parsed"))
        L.append("   unparsed by reason: " + ", ".join("%s %d" % kv for kv in why.most_common()))
        L.append("   compiled by route: " + ", ".join("%s %d" % kv for kv in
                                                    sorted(collections.Counter(o["route"] for o in ok).items())))
        L.append("   parsed by route:   " + ", ".join("%s %d" % kv for kv in
                                                    sorted(collections.Counter(o["route"] for o in parsed).items())))
        for route in ("dfa", "hybrid", "vm-only"):
            U = [o for o in unanch if o["route"] == route]
            cls = collections.Counter(o["cls"] for o in U)
            sp = [o for o in U if o["cls"] == "spine"]
            st = collections.Counter(o["strength"] for o in sp)
            notstart = [o for o in sp if o["strength"] != "start"]
            g2 = [o for o in notstart if o["gain"] >= 2]
            g8 = [o for o in notstart if o["gain"] >= 8]
            L.append("   [%s] unanchored %d: %s" % (route, len(U), ", ".join("%s %d" % kv for kv in sorted(cls.items()))))
            L.append("      best landmark by strength: " + ", ".join("%s %d" % (k, st[k]) for k in
                                                                    ("start", "fixed", "bounded", "exact-rev", "presence")))
            L.append("      best NOT at start: %d (byte %d / run %d); of these >=2x rarer than today's key %d, >=8x %d"
                     % (len(notstart), sum(o["best_kind"] == "byte" for o in notstart),
                        sum(o["best_kind"] == "run" for o in notstart), len(g2), len(g8)))
            L.append("      >=2x by strength: " + ", ".join("%s %d" % (k, sum(o["strength"] == k for o in g2))
                                                           for k in ("fixed", "bounded", "exact-rev", "presence")))
            served = [o for o in g2 if o["strength"] in ("fixed", "bounded") and
                      (o["dfa_pf"].startswith(("offset-set", "run-pinned")) or o["handoff"] not in ("", "none"))]
            L.append("      of >=2x fixed/bounded, already on an offset-set/run-pinned row or the K82 handoff: %d of %d"
                     % (len(served), sum(o["strength"] in ("fixed", "bounded") for o in g2)))
            if pop == "bench":
                for k in ("exact-rev", "presence"):
                    ids = sorted(o["id"] for o in g2 if o["strength"] == k)
                    if ids:
                        L.append("      %s >=2x: %s" % (k, ", ".join(ids)))
            if route == "vm-only":
                nopf = [o for o in sp if o["vm_start"] in ("", "none")]
                usable = [o for o in nopf if o["strength"] in ("start", "fixed", "bounded", "exact-rev")]
                L.append("      VM-only with NO candidate scan today (VM_START_SCAN none): %d spine; a usable"
                         " landmark (start/fixed/bounded/exact-rev): %d (start %d, non-start %d)"
                         % (len(nopf), len(usable), sum(o["strength"] == "start" for o in usable),
                            sum(o["strength"] != "start" for o in usable)))
                hat = [o for o in sp if o["vm_start"] not in ("", "none")]
                hn = [o for o in hat if o["strength"] in ("fixed", "bounded", "exact-rev") and o["gain"] >= 2]
                L.append("      VM-only WITH the start-set hat: %d spine; a non-start usable landmark >=2x rarer"
                         " than the hat's set: %d" % (len(hat), len(hn)))
        c2 = [o for o in parsed if "c2_checked" in o]
        L.append("   C2 necessity vs pcrec req_set: %d patterns checked, %d bytes, %d violations"
                 % (len(c2), sum(o["c2_checked"] for o in c2), sum(o["c2_viol"] for o in c2)))
        c3 = collections.Counter(o["c3"] for o in parsed if "c3" in o)
        L.append("   C3 fixed offset vs pcrec kset_walk: " + ", ".join("%s %d" % kv for kv in sorted(c3.items())))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    G.PRIOR = G.prior()
    if a.selftest:
        sys.exit(1 if selftest() else 0)
    os.makedirs(OUT, exist_ok=True)
    pop = G.bench_pop() + G.corpus_pop()
    if a.limit:
        pop = pop[:a.limit]
    with cf.ThreadPoolExecutor(a.workers) as ex:
        rows = list(ex.map(census_row, pop))
    keys = sorted({k for o in rows for k in o})
    with gzip.open(os.path.join(OUT, "rows.tsv.gz"), "wt") as fh:
        fh.write("\t".join(keys) + "\n")
        for o in rows:
            fh.write("\t".join(str(o.get(k, "")) for k in keys) + "\n")
    s = summarize(rows)
    open(os.path.join(OUT, "summary.txt"), "w").write(s + "\n")
    print(s)


if __name__ == "__main__":
    main()
