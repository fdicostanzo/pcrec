#!/usr/bin/env python3
"""D151 stage 1's DECIDING CENSUS (lane rincensus, 2026-10-11): how many patterns are eligible
for reverse-inner stage 1 under the RULED gates?  COMPILE-SIDE ONLY: no subject is matched, no
clock is read, gcc is never run.  Nothing under src/ is touched.

A pattern is ELIGIBLE when it is
  * on the DFA route (pcrec --emit-facts RX_ENGINE=dfa; stage 1 is the DFA hat),
  * not start-anchored (the start_anchor fact),
  * has ONE COMMON landmark L across its top-level branches (revised Q2, D151 add. 6):
    a maximal run of single-byte / caseless-pair items on each branch's flattened spine,
    the same byte-set sequence in every branch, with a NON-EMPTY P_i before it in at least
    one branch (a landmark at the start is a prefix literal, not an inner one),
  * G1: no P_i holds a backreference, call, atomic/possessive or lookaround,
  * G2: per (P_i, L) at least one of the THREE arms (D151 add. 5):
        fixed   P_i has fixed BYTE width;
        disj    NOT (bytes(L) subset alphabet(P_i));
        ffree   no string of P_i contains L as a factor AND L is border-free, both over
                L's case-fold variant set (F4), decided on P_i's NFA x a shift-and
                automaton of L (F7), never on P's DFA,
  * G3: ppm(L's rarest scan byte) <= ppm(today's scan key) / F  (F = 1, 2, 8 reported;
    2 is D149's UNMEASURED default and the headline).

The reader is lane startstudy's census.py Reader, COPIED and extended (scoped (?i:), \\Q..\\E, \\x{..},
class-range escapes, \\p / \\X as a conservative APPROXIMATE item: all bytes, variable width,
so a construct it cannot model only ever makes an arm DECLINE).  Population loaders, the
facts() reader and the byte-rate prior are IMPORTED from the artrev census (loaded by path).

Per pattern two outcomes are recorded: `pair` (the ruled text: every branch passes G2 with its
own P_i) and `union` (G2 evaluated once on P' = P_1 | ... | P_n); the model lane's
mixed-P finding (rincensus_report.md section 2) says which one the build may rely on.

Controls (K35), run by --selftest:
  C1  hand-classified patterns (positives AND negatives for each arm, caseless L, mixed P, alternation),
  C2  the arm decision procedure against rinner_model.py's INDEPENDENT implementation
      (parse_p + factor_witness on generated P texts: 0 disagreements required),
  C3  sabotage rows: with the border test blind, or the factor test blind, the selftest must FAIL.

Env: PCREC (default build/pcrec), BENCH, CORPUS, OUT.
Usage: PCREC=build/pcrec CORPUS=. BENCH=<pcrec-bench> OUT=<scratch> python3 rincensus.py [--selftest] [--workers 8]
       [--sabotage no-border|no-factor] [--catalog FILE ...]
"""
import argparse, collections, concurrent.futures as cf, csv, gzip, importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.environ
E.setdefault("PCREC", "build/pcrec"); E.setdefault("CORPUS", "."); E.setdefault("BENCH", ""); E.setdefault("OUT", "build/rc")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, *rel))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


G = _load("artgen_census", ["..", "..", "dev", "optloop", "artrev", "gen", "census.py"])
W = G.W
ALL = set(range(256))
HIGH = set(range(128, 256))
SABOTAGE = None
NFA_CAP = 60000        # NFA states
PROD_CAP = 3000000     # product states visited


class Unparsed(Exception):
    pass


class Cap(Exception):
    pass


def esc_set(ch):
    D = set(range(48, 58)); S = {9, 10, 11, 12, 13, 32}; H = {9, 32, 0xA0}; V = {10, 11, 12, 13, 0x85}
    return {"w": W, "d": D, "s": S, "h": H, "v": V, "W": ALL - W, "D": ALL - D, "S": ALL - S,
            "H": ALL - H, "V": ALL - V, "N": ALL - {10}, "R": {10, 11, 12, 13}}.get(ch)


POSIX = {"alpha": set(range(65, 91)) | set(range(97, 123)), "digit": set(range(48, 58)),
         "alnum": set(range(65, 91)) | set(range(97, 123)) | set(range(48, 58)),
         "space": {9, 10, 11, 12, 13, 32}, "upper": set(range(65, 91)), "lower": set(range(97, 123)),
         "xdigit": set(b"0123456789abcdefABCDEF"), "word": W,
         "punct": {b for b in range(33, 127) if not chr(b).isalnum()}, "print": set(range(32, 127)),
         "graph": set(range(33, 127)), "blank": {9, 32}, "cntrl": set(range(32)) | {127},
         "ascii": set(range(128))}


def expand_Q(s):
    """\\Q..\\E -> escaped literals"""
    out, i = [], 0
    while i < len(s):
        if s.startswith("\\Q", i):
            j = s.find("\\E", i + 2)
            lit = s[i + 2:] if j < 0 else s[i + 2:j]
            out.append("".join(("\\" + c) if not (c.isalnum() or ord(c) > 127 or c == "_") else c for c in lit))
            i = len(s) if j < 0 else j + 2
        elif s[i] == "\\" and i + 1 < len(s):
            out.append(s[i:i + 2]); i += 2
        else:
            out.append(s[i]); i += 1
    return "".join(out)


class Reader:
    """lane startstudy's census.py Reader, extended.  Items:
       ('set', S, w)   one character; w=(1,1) or (1,4) (multibyte / variable / approximate)
       ('zw', kind)    view | look | flag
       ('bref',) ('call',)
       ('grp', alts, atomic)   ('rep', item, m, M, mode)"""

    def __init__(self, p, icase, utf8):
        self.s = expand_Q(p.decode("latin-1")); self.i = 0; self.icase = icase; self.utf8 = utf8
        self.dotall = False; self.approx = 0
        if "(?x" in self.s or "(?|" in self.s or "(?(" in self.s or "(?-x" in self.s:
            raise Unparsed("unsupported-syntax")
        while self.s.startswith("(*", self.i):          # (*UTF) (*UCP) ... leading option verbs
            m = re.match(r"\(\*[A-Z_0-9=]+\)", self.s[self.i:])
            if not m:
                raise Unparsed("verb")
            self.i += len(m.group(0))

    def fold(self, st):
        if not self.icase:
            return st
        return st | {b ^ 32 for b in st if 65 <= b <= 90 or 97 <= b <= 122}

    def width_of(self, st):
        if self.utf8 and any(b >= 0x80 for b in st):
            return (1, 1) if len(st) == 1 else (1, 4)
        return (1, 1)

    def wide(self, st):
        """a class-ish item: under utf8 (UCP) a class is a CHARACTER class (wide, variable)."""
        if self.utf8:
            return ("set", set(st) | HIGH, (1, 4))
        return ("set", set(st), (1, 1))

    def approx_item(self):
        self.approx += 1
        return ("set", set(ALL), (1, 4))

    def escape_char(self, i):
        """in a class: parse the escape at s[i] (after the backslash) -> (set|None, value|None, next i)"""
        s = self.s
        e = esc_set(s[i])
        if e is not None:
            return (set(e) | (HIGH if self.utf8 and s[i] in "wdsWDShHvV" else set())), None, i + 1
        lo = {"n": 10, "t": 9, "r": 13, "f": 12, "v": 11, "e": 27, "a": 7, "b": 8}.get(s[i])
        if lo is not None:
            return None, lo, i + 1
        if s[i] == "x":
            m = re.match(r"\{([0-9a-fA-F]+)\}", s[i + 1:])
            if m:
                return None, int(m.group(1), 16), i + 1 + len(m.group(0))
            m = re.match(r"[0-9a-fA-F]{1,2}", s[i + 1:])
            return None, (int(m.group(0), 16) if m else 0), i + 1 + (len(m.group(0)) if m else 0)
        if s[i] in "0123456789":
            m = re.match(r"[0-7]{1,3}", s[i:])
            if not m:
                raise Unparsed("class-escape")
            return None, int(m.group(0), 8), i + len(m.group(0))
        if s[i] in "pP":
            m = re.match(r"\{[^}]*\}|[A-Za-z]", s[i + 1:])
            self.approx += 1
            return set(ALL), None, i + 1 + (len(m.group(0)) if m else 0)
        if s[i] == "c":
            return None, ord(s[i + 1]) ^ 64, i + 2
        if s[i].isalnum():
            raise Unparsed("class-escape")
        return None, ord(s[i]), i + 1

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
                    out.add(ord("[")); i += 1; continue
                nm = POSIX.get(m.group(2))
                if nm is None:
                    raise Unparsed("posix")
                out |= (ALL - nm) if m.group(1) else nm
                if self.utf8 and not m.group(1):
                    out |= HIGH
                i += len(m.group(0)); continue
            if c == "\\":
                i += 1
                if i >= len(s):
                    raise Unparsed("class")
                st, lo, i = self.escape_char(i)
                if st is not None:
                    out |= st; continue
            else:
                lo = ord(c); i += 1
            if i + 1 < len(s) and s[i] == "-" and s[i + 1] != "]":
                if s[i + 1] == "\\":
                    st2, hi, j = self.escape_char(i + 2)
                    if st2 is not None:          # [a-\d]: a literal hyphen, then the set
                        out.add(lo); out.add(ord("-")); out |= st2; i = j; continue
                    i = j
                elif s[i + 1] == "[":
                    out.add(lo); continue
                else:
                    hi = ord(s[i + 1]); i += 2
                out |= set(range(lo, min(hi, 255) + 1))
                if hi > 255:
                    out |= HIGH
            else:
                out.add(lo if lo < 256 else 0xFF)
                if lo > 255:
                    out |= HIGH
        if i >= len(s):
            raise Unparsed("class")
        self.i = i + 1
        out = self.fold(out)
        if neg:
            out = ALL - out
            return out, ((1, 4) if self.utf8 else (1, 1))
        return out, self.width_of(out)

    def flags(self, f):
        on = f.split("-")[0]
        if "x" in on:
            raise Unparsed("x-flag")
        return on

    def atom(self):
        s = self.s; c = s[self.i]
        if c == "(":
            atomic = False
            saved = (self.icase, self.dotall)
            if s.startswith("(?:", self.i):
                self.i += 3
            elif s.startswith("(?>", self.i) or s.startswith("(*atomic:", self.i):
                self.i += 3 if s.startswith("(?>", self.i) else 9; atomic = True
            elif s.startswith("(?#", self.i):
                j = s.find(")", self.i)
                if j < 0:
                    raise Unparsed("comment")
                self.i = j + 1
                return ("zw", "flag")
            elif s.startswith(("(?=", "(?!"), self.i) or s.startswith(("(?<=", "(?<!"), self.i):
                self.i += 4 if s[self.i + 2] == "<" else 3
                self.alternation()
                self.close()
                self.icase, self.dotall = saved
                return ("zw", "look")
            elif re.match(r"\(\?P?<\w+>|\(\?'\w+'", s[self.i:]):
                m = re.match(r"\(\?P?<\w+>|\(\?'\w+'", s[self.i:]); self.i += len(m.group(0))
            elif re.match(r"\(\?(\d+|[+-]\d+|R|&\w+|P>\w+)\)", s[self.i:]):
                m = re.match(r"\(\?(\d+|[+-]\d+|R|&\w+|P>\w+)\)", s[self.i:]); self.i += len(m.group(0))
                return ("call",)
            elif re.match(r"\(\?\^?[A-Za-z-]*\)", s[self.i:]):
                m = re.match(r"\(\?(\^?[A-Za-z-]*)\)", s[self.i:]); self.i += len(m.group(0))
                on = self.flags(m.group(1))
                if "i" in on:
                    self.icase = True
                if "s" in on:
                    self.dotall = True
                return ("zw", "flag")
            elif re.match(r"\(\?\^?[A-Za-z-]*:", s[self.i:]):
                m = re.match(r"\(\?(\^?[A-Za-z-]*):", s[self.i:]); self.i += len(m.group(0))
                on = self.flags(m.group(1))
                off = m.group(1).split("-")[1] if "-" in m.group(1) else ""
                if "i" in on:
                    self.icase = True
                if "i" in off:
                    self.icase = False
                if "s" in on:
                    self.dotall = True
            elif s.startswith("(*", self.i) or s.startswith("(?", self.i):
                raise Unparsed("group-kind")
            else:
                self.i += 1
            alts = self.alternation()
            self.close()
            self.icase, self.dotall = saved
            return ("grp", alts, atomic)
        if c == "[":
            st, w = self.cls(); return ("set", st, w)
        if c == ".":
            self.i += 1
            return ("set", ALL if self.dotall else ALL - {10}, (1, 4) if self.utf8 else (1, 1))
        if c in "^$":
            self.i += 1; return ("zw", "view")
        if c == "\\":
            n = s[self.i + 1] if self.i + 1 < len(s) else ""
            self.i += 2
            e = esc_set(n)
            if e is not None:
                if n == "R":
                    return ("grp", [[("set", {10, 11, 12, 13}, (1, 1))], [("set", {13}, (1, 1)), ("set", {10}, (1, 1))]], False)
                if self.utf8:
                    return ("set", set(e) | HIGH, (1, 4))
                return ("set", set(e), (1, 1))
            if n in "bBAzZG":
                return ("zw", "view")
            if n == "K":
                raise Unparsed("\\K")
            if n.isdigit() and n != "0":
                m = re.match(r"\d*", s[self.i:])
                if len(m.group(0)) + 1 <= 3 and False:
                    pass
                self.i += len(m.group(0))
                return ("bref",)
            if n == "0":
                m = re.match(r"[0-7]{0,2}", s[self.i:]); self.i += len(m.group(0))
                return ("set", {int("0" + m.group(0), 8)}, (1, 1))
            if n in "gk":
                m = re.match(r"\{[^}]*\}|<[^>]*>|'[^']*'|-?\d+", s[self.i:])
                if not m:
                    raise Unparsed("\\g")
                self.i += len(m.group(0))
                return ("call",) if n == "g" and m.group(0)[0] in "<'" else ("bref",)
            m = {"n": 10, "t": 9, "r": 13, "f": 12, "e": 27, "a": 7}.get(n)
            if m is not None:
                return ("set", {m}, (1, 1))
            if n == "x":
                mm = re.match(r"\{([0-9a-fA-F]+)\}", s[self.i:])
                if mm:
                    self.i += len(mm.group(0)); v = int(mm.group(1), 16)
                else:
                    mm = re.match(r"[0-9a-fA-F]{0,2}", s[self.i:]); self.i += len(mm.group(0)); v = int(mm.group(0) or "0", 16)
                if v < 128 or (not self.utf8 and v < 256):
                    return ("set", self.fold({v}), (1, 1))
                if self.utf8:        # a multibyte literal: its UTF-8 bytes, one item each
                    return ("grp", [[("set", {b}, (1, 1)) for b in chr(v).encode("utf8")]], False)
                return self.approx_item()
            if n in "pPXCN" or n == "o" or n == "c":
                if n in "pP":
                    mm = re.match(r"\{[^}]*\}|[A-Za-z]", s[self.i:])
                    self.i += len(mm.group(0)) if mm else 0
                elif n in "No":
                    mm = re.match(r"\{[^}]*\}", s[self.i:]); self.i += len(mm.group(0)) if mm else 0
                    if n == "N" and not mm:
                        return ("set", ALL - {10}, (1, 4) if self.utf8 else (1, 1))
                elif n == "c":
                    self.i += 1
                return self.approx_item()
            if n.isalnum() or n == "":
                raise Unparsed("escape")
            return ("set", {ord(n)}, (1, 1))
        if c in "*+?{)|":
            raise Unparsed("stray")
        self.i += 1
        return ("set", self.fold({ord(c)}), self.width_of({ord(c)}))

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


# ---- item properties (census.py's) -----------------------------------------

def props(it):
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


def flatten(items, peel=False):
    """Splice un-quantified, non-atomic, single-alternative groups (rust's flatten).  With `peel`, the FIRST
    iteration of a mandatory (m >= 1) repeat of a single-alternative group is spliced out too:
    X{m,M} = X X{m-1,M-1} (an exact rewrite of the language), which is how ipv6's ':' becomes a spine literal."""
    out = []
    for it in items:
        if it[0] == "grp" and len(it[1]) == 1 and not it[2]:
            out += flatten(it[1][0], peel)
        elif (peel and it[0] == "rep" and it[2] >= 1 and it[4] != "poss" and it[1][0] == "grp"
              and len(it[1][1]) == 1 and not it[1][2] and (it[3] is None or it[3] >= 1)):
            out += flatten(it[1][1][0], False)
            m2, M2 = it[2] - 1, (None if it[3] is None else it[3] - 1)
            if M2 != 0:
                out.append(("rep", it[1], m2, M2, it[4]))
        else:
            out.append(it)
    return out


def litset(it):
    if it[0] == "set" and it[2] == (1, 1) and (len(it[1]) == 1 or (len(it[1]) == 2 and
                                                                   len({b | 32 for b in it[1]}) == 1)):
        return frozenset(it[1])
    if it[0] == "rep" and it[2] >= 1:
        return litset(it[1])
    return None


def landmarks(spine):
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


def canon(it):
    k = it[0]
    if k == "set":
        return ("set", tuple(sorted(it[1])), it[2])
    if k == "zw":
        return it[:2]
    if k == "grp":
        return ("grp", tuple(tuple(canon(x) for x in a) for a in it[1]), it[2])
    if k == "rep":
        return ("rep", canon(it[1]), it[2], it[3], it[4])
    return it


# ---- G2's factor-free arm on P's NFA x a shift-and automaton of L's set sequence --------------

def build_nfa(items, utf8):
    eps, tr = [], []

    def new():
        if len(eps) >= NFA_CAP:
            raise Cap("nfa")
        eps.append([]); tr.append([]); return len(eps) - 1

    def item(n):
        k = n[0]
        if k == "set":
            a, b = new(), new()
            st = n[1]
            if utf8 and n[2] == (1, 4) and (set(st) & HIGH):
                lo = frozenset(st & set(range(128)))
                if lo:
                    tr[a].append((lo, b))
                cont = frozenset(range(0x80, 0xC0))
                for leads, k2 in ((frozenset(range(0xC2, 0xE0)), 1), (frozenset(range(0xE0, 0xF0)), 2),
                                  (frozenset(range(0xF0, 0xF5)), 3)):
                    q = new(); tr[a].append((leads, q))
                    for _ in range(k2 - 1):
                        q2 = new(); tr[q].append((cont, q2)); q = q2
                    tr[q].append((cont, b))
            else:
                tr[a].append((frozenset(st), b))
            return a, b
        if k == "zw":
            a, b = new(), new(); eps[a].append(b); return a, b
        if k == "grp":
            a, b = new(), new()
            for alt in n[1]:
                s2, e2 = seq(alt); eps[a].append(s2); eps[e2].append(b)
            return a, b
        if k == "rep":
            _, m, lo, hi, _mode = n
            a = b = new()
            for _ in range(lo):
                s2, e2 = item(m); eps[b].append(s2); b = e2
            if hi is None:
                s2, e2 = item(m); loop = new()
                eps[b].append(loop); eps[loop].append(s2); eps[e2].append(loop); b = loop
            else:
                end = new()
                for _ in range(hi - lo):
                    eps[b].append(end); s2, e2 = item(m); eps[b].append(s2); b = e2
                eps[b].append(end); b = end
            return a, b
        raise Cap("item " + k)

    def seq(items_):
        a = b = new()
        for m in items_:
            s2, e2 = item(m); eps[b].append(s2); b = e2
        return a, b

    s, e = seq(items)
    return eps, tr, s, e


def border_free_sets(run):
    """no two occurrences (any fold variants) can overlap: for every 0<k<n some position t<k has
    run[n-k+t] and run[t] DISJOINT."""
    n = len(run)
    for k in range(1, n):
        if all(run[n - k + t] & run[t] for t in range(k)):
            return False
    return True


def factor_free_sets(items, run, utf8):
    """True: no string of P (items) contains an L variant as a factor.  False: some does.  None: cap."""
    if SABOTAGE == "no-factor":
        return True
    try:
        eps, tr, s0, acc = build_nfa(items, utf8)
    except Cap:
        return None
    n = len(run)
    D = [0] * 256
    for t, st in enumerate(run):
        for b in st:
            D[b] |= 1 << t
    full = 1 << (n - 1)
    MATCHED = -1
    setrep = {}                       # NFA transition set -> {D-value: a representative byte}
    for q in range(len(tr)):
        for cs, _q2 in tr[q]:
            if cs not in setrep:
                reps = {}
                for b in cs:
                    reps.setdefault(D[b], b)
                setrep[cs] = list(reps.values())
    seen = {(s0, 0)}
    stack = [(s0, 0)]
    while stack:
        q, m = stack.pop()
        if q == acc and m == MATCHED:
            return False
        for q2 in eps[q]:
            if (q2, m) not in seen:
                seen.add((q2, m)); stack.append((q2, m))
        for cs, q2 in tr[q]:
            for b in setrep[cs]:
                if m == MATCHED:
                    m2 = MATCHED
                else:
                    m2 = ((m << 1) | 1) & D[b]
                    if m2 & full:
                        m2 = MATCHED
                if (q2, m2) not in seen:
                    if len(seen) > PROD_CAP:
                        return None
                    seen.add((q2, m2)); stack.append((q2, m2))
    return True


def arms_for(pitems, run, utf8, icase):
    """-> dict(g1, empty, fixed, disj, ffree, ffree_why).  `ffree` is None when the arm could not be decided."""
    lo, hi, al, fl = seq_props(pitems)
    o = dict(g1=not (fl & {"bref", "call", "atomic", "look"}), g1_why=",".join(sorted(fl & {"bref", "call", "atomic", "look"})),
             empty=(hi == 0), pmin=lo, pmax=hi)
    lbytes = set().union(*run)
    o["fixed"] = hi is not None and lo == hi and lo > 0
    o["disj"] = not lbytes <= al
    if utf8 and icase and (any(b >= 0x80 for b in lbytes) or lbytes & set(b"kKsS")):
        o["ffree"] = None; o["ffree_why"] = "utf8-fold"
        return o
    bf = True if SABOTAGE == "no-border" else border_free_sets(run)
    o["bfree"] = bf
    if not bf:
        o["ffree"] = False; o["ffree_why"] = "bordered"
        return o
    ff = factor_free_sets(pitems, run, utf8)
    o["ffree"] = ff
    o["ffree_why"] = "cap" if ff is None else ("" if ff else "P-contains-L")
    return o


def arm_names(o):
    return [a for a in ("fixed", "disj", "ffree") if o.get(a)]


# ---- the pattern-level decision -------------------------------------------

VARIANTS = ["max_peel", "max", "sub_peel", "sub"]
HEADLINE = "max_peel"
LADDER = ["no-landmark", "no-common-L", "P-empty", "G1", "G2", "G3", "ELIGIBLE"]
SUBMAX = 48      # longest run whose sub-runs are enumerated in "sub" mode


def cands_of(sp, mode):
    """{key: [(spine index where L starts, run)]}.  mode 'max': each maximal literal run is one L.
    mode 'sub': every contiguous sub-run of every maximal run (the common-L search across branches)."""
    d = {}
    for start, run in landmarks(sp):
        if mode == "max":
            d.setdefault(tuple(run), []).append((start, run))
        else:
            n = len(run)
            if n > SUBMAX:
                d.setdefault(tuple(run), []).append((start, run))
                continue
            for a in range(n):
                for b in range(a + 1, n + 1):
                    d.setdefault(tuple(run[a:b]), []).append((start + a, run[a:b]))
    return d


def decide(tree, utf8, icase, key_ppm, mode="max", peel=False):
    """-> dict with the furthest gate reached and, for the best candidate, arms/ratio.
    Evaluated for `pair` and `union` G2 forms.  F-dependence is returned as `ratio`."""
    while len(tree) == 1 and len(tree[0]) == 1 and tree[0][0][0] == "grp" and not tree[0][0][2]:
        tree = tree[0][0][1]                  # the whole pattern is one (?:...) group: its alternation IS the top level
    branches = [flatten(a, peel) for a in tree]
    per = [cands_of(sp, mode) for sp in branches]
    if not any(per):
        return dict(stage="no-landmark")
    common = set(per[0])
    for d in per[1:]:
        common &= set(d)
    if not common:
        return dict(stage="no-common-L", nbranch=len(branches))
    best = None
    for key in common:
        run = list(key)
        scan = min(ppm(r) for r in run)
        ratio = key_ppm / max(1, scan)
        bres = []
        for bi, sp in enumerate(branches):
            chosen = None
            for start, run_ in per[bi][key]:
                pit = sp[:start]
                a = arms_for(pit, run, utf8, icase)
                if a["empty"]:
                    cand = ("empty", a, pit)
                elif not a["g1"]:
                    cand = ("G1", a, pit)
                elif arm_names(a):
                    cand = ("ok", a, pit)
                else:
                    cand = ("G2", a, pit)
                rank = {"ok": 3, "empty": 2, "G2": 1, "G1": 0}[cand[0]]
                if chosen is None or rank > chosen[0]:
                    chosen = (rank, cand)
            bres.append(chosen[1])
        if all(k == "empty" for k, _, _ in bres):
            st = "P-empty"
        elif any(k == "G1" for k, _, _ in bres):
            st = "G1"
        elif any(k == "G2" for k, _, _ in bres):
            st = "G2"
        else:
            st = "ok"
        # union form: arms on P' = (P_1 | ... | P_n)
        u_ok = None
        u_arms = []
        if len(branches) > 1 and st in ("ok", "G2"):
            up = [("grp", [list(pit) for _k, _a, pit in bres], False)]
            ua = arms_for(up, run, utf8, icase)
            u_arms = arm_names(ua)
            u_ok = bool(u_arms) and ua["g1"] and not ua["empty"]
        elif len(branches) == 1:
            u_ok = (st == "ok")
            u_arms = arm_names(bres[0][1]) if st == "ok" else []
        pcanon = {tuple(canon(x) for x in pit) for _, _, pit in bres}
        # composition across branches (rincensus_report.md section 2): a "strong" arm (disj / ffree: starts(j') > j for every
        # earlier occurrence j) composes freely; a width-0 branch is trivially strong; fixed widths compose only when EQUAL
        strong = [k == "empty" or a.get("disj") or a.get("ffree") for k, a, _ in bres]
        widths = {a["pmin"] for k, a, _ in bres if k != "empty" and a.get("fixed") and not (a.get("disj") or a.get("ffree"))}
        allw = [a["pmin"] if (k != "empty" and a.get("fixed")) else (0 if k == "empty" else None) for k, a, _ in bres]
        comp = len(branches) == 1 or all(strong) or (None not in allw and len(set(allw)) == 1)
        strong_nf = [k == "empty" or a.get("disj") for k, a, _ in bres]          # strong WITHOUT the factor-free arm
        comp_nf = (len(branches) == 1 and bool(arm_names(bres[0][1]) and set(arm_names(bres[0][1])) != {"ffree"})) \
            or (len(branches) > 1 and (all(strong_nf) or (None not in allw and len(set(allw)) == 1)))
        needs_ffree = st == "ok" and comp and not comp_nf
        cand = dict(stage=st, comp_ok=(comp and st == "ok"), needs_ffree=needs_ffree, nbr=len(branches), ratio=ratio, key=key, nbranch=len(branches),
                    arms=[arm_names(a) if k == "ok" else [] for k, a, _ in bres], uniformP=(len(pcanon) == 1),
                    union_ok=u_ok, union_arms=u_arms, lhex="".join("%02x" % min(r) for r in run), single=[min(r) for r in run if len(r) == 1], L="".join(("\\x%02x" % min(r)) if not 32 <= min(r) < 127 or min(r) == 92 else chr(min(r)) for r in run),
                    ffree_why=[a.get("ffree_why", "") for _, a, _ in bres], pmin=[a["pmin"] for _, a, _ in bres],
                    pmax=[a["pmax"] for _, a, _ in bres])
        rank = {"P-empty": 0, "G1": 1, "G2": 2, "ok": 3}[st]
        if best is None or (rank, ratio) > (best[0], best[1]["ratio"]):
            best = (rank, cand)
    return best[1]


def first_arm(arms):
    """first-match order over a pattern's per-branch arms: the WEAKEST first-match arm over branches
    (the arm that admits the pattern; 'ffree' only when some branch needs it)."""
    order = ("fixed", "disj", "ffree")
    worst = 0
    for br in arms:
        if not br:
            continue
        worst = max(worst, min(order.index(a) for a in br))
    return order[worst]


def pattern_row(r):
    o = dict(pop=r["pop"], id=r["id"], enc=r["enc"], icase=int(r["icase"]))
    fd, err = G.facts(r)
    if fd is None:
        o["outcome"] = "refused"; return o
    f, d = fd
    eng = d.get("ENGINE", ""); vpf = d.get("VM_PREFILTER", "")
    o["route"] = "dfa" if eng == "dfa" else ("hybrid" if vpf == "hybrid" else "vm-only")
    o["anchor"] = f.get("start_anchor", "")
    o["dfa_scan"] = d.get("DFA_SCAN", ""); o["dfa_start"] = d.get("DFA_START", ""); o["dfa_pf"] = d.get("DFA_PREFILTER", "")
    o["handoff"] = d.get("REQ_HANDOFF", ""); o["req_run"] = d.get("REQ_RUN", "")
    S = G.bitset(f.get("start_set", ""))
    try:
        rd = Reader(r["pat"], r["icase"], r["enc"] == "utf8")
        tree = rd.parse()
        o["approx"] = rd.approx
    except (Unparsed, ValueError, IndexError, RecursionError) as e:
        o["outcome"] = "unparsed"; o["why"] = (e.args[0] if e.args else type(e).__name__); return o
    if o["anchor"] != "unanchored":
        o["outcome"] = "anchored"; return o
    # today's scan key (K1's key, census.py's rule)
    vm_start = d.get("VM_START_SCAN", ""); req_run = d.get("REQ_RUN", "")
    if o["route"] == "vm-only" and vpf == "none" and vm_start in ("", "none"):
        key = 1000000
    elif req_run not in ("", "none"):
        try:
            key = G.PRIOR.get(int(d.get("REQ_BYTE", "")), 2)
        except ValueError:
            key = sum(G.PRIOR.get(x, 2) for x in S) if S is not None else 1000000
    else:
        key = sum(G.PRIOR.get(x, 2) for x in S) if S is not None else 1000000
    o["key_ppm"] = key
    ut = r["enc"] == "utf8"
    try:
        decs = {v: decide(tree, ut, r["icase"], key, v.split("_")[0], v.endswith("_peel")) for v in VARIANTS}
    except (RecursionError, Cap) as e:
        o["outcome"] = "unparsed"; o["why"] = "decide:" + type(e).__name__; return o
    o["nbranch"] = len(tree)
    for v, d in decs.items():
        o["stage_" + v] = d["stage"]
        o["ratio_" + v] = "%.2f" % d["ratio"] if "ratio" in d else ""
        o["arm_" + v] = first_arm(d["arms"]) if d["stage"] == "ok" else ""
        o["union_" + v] = (first_arm([d["union_arms"]]) if d.get("union_ok") else "") if "union_ok" in d else ""
        o["uniform_" + v] = int(d["uniformP"]) if "uniformP" in d else ""
        o["comp_" + v] = int(d["comp_ok"]) if "comp_ok" in d else ""
        o["nff_" + v] = int(d["needs_ffree"]) if "needs_ffree" in d else ""
        o["nbr_" + v] = d.get("nbr", "")
        o["L_" + v] = d.get("L", "")
        o["lhex_" + v] = d.get("lhex", "")
        o["ffwhy_" + v] = ",".join(sorted({w for w in d.get("ffree_why", []) if w}))
        o["arms_all_" + v] = "/".join(sorted({a for br in d.get("arms", []) for a in br}))
    # C2 (K35): the landmark's bytes must be NECESSARY according to pcrec's own req_set (src/facts/req.c, no shared code),
    # checked for every candidate L the readings chose, on case-sensitive byte patterns where pcrec derived a set
    req = G.intlist(f.get("req_set", "")) if f.get("req_set", "none") not in ("none", "") else []
    if req and not r["icase"] and not ut:
        chk = viol = 0
        for v, d in decs.items():
            if d.get("lhex") and d["stage"] in ("ok", "G2", "G1"):
                lb = set(d["single"])                # case-pair positions are skipped: req_set holds one case
                chk += len(lb); viol += len(lb - set(req))
        o["c2_checked"] = chk; o["c2_viol"] = viol
    dec = decs[HEADLINE]
    o["stage"] = dec["stage"]
    if dec["stage"] in ("no-landmark", "no-common-L"):
        o["outcome"] = dec["stage"]; return o
    o["pmin"] = dec["pmin"][0]; o["pmax"] = "" if dec["pmax"][0] is None else dec["pmax"][0]
    o["outcome"] = {"ok": "G3-pending"}.get(dec["stage"], dec["stage"])
    return o


# ---- the controls ----------------------------------------------------------

SELF = [  # (pattern, icase, utf8, want stage/arm) : arm = first-match arm, or a stage name
    (rb"[0-9]{3}-x", False, False, "fixed"),
    (rb"\d+@x", False, False, "disj"),
    (rb"[a-z]+xy", False, False, "G2"),                       # P holds xy as a factor: split ambiguous
    (rb"(?:abcin|gnb|xyzg)ing", False, False, "ffree"),          # no stem holds ing; ing border-free (sfx shape)
    (rb"(?:sing|abc)ing", False, False, "G2"),                # a stem holds ing
    (rb"(?:abcin|xyzn)nin", False, False, "G2"),              # nin bordered: arm 3 declines
    (rb"(?:abcin|xyzg)ing", False, False, "ffree"),
    (rb"[a-z]+nin", False, False, "G2"),
    (rb"(?i)(?:xb*a|b)aA", False, False, "G2"),              # F4: caseless L aA: variants aa/aA/Aa/AA; P holds a(a)
    (rb"(?:xb*a|b)aa", False, False, "G2"),                  # aa is bordered
    (rb"(?:[a-f]+|[0-9]+)ing", False, False, "disj"),
    (rb"(?:\bfoo)bar", False, False, "P-empty"),
    (rb"(a+)\1x", False, False, "G1"),
    (rb"(?>a+)@x", False, False, "G1"),
    (rb"(?=a)b+@x", False, False, "G1"),
    (rb"abc", False, False, "P-empty"),
    (rb"\w+", False, False, "no-landmark"),
    (rb"(?:(?:[0-9a-f]{1,4}:){4,7}[0-9a-f]{1,4}|(?:[0-9a-f]{1,4}:){1,7}:[0-9a-f]{0,4})", False, False, "disj"),   # loglines/ipv6: peeled first iteration, equal P, common L ':'
    (rb"[0-9a-f]{1,4}:x|[0-9a-f]{1,4}:y", False, False, "no-common-L"),   # maximal runs :x / :y differ (sub-run mode would find ':')
    (rb"yab|[xy]*abc", False, False, "no-common-L"),              # F2: distinct landmarks decline
    (rb"x[a-y]*z|cq", False, False, "no-common-L"),
]


def selftest(verbose=True):
    G.PRIOR = G.prior()
    bad = 0
    for p, ic, ut, want in SELF:
        try:
            tree = Reader(p, ic, ut).parse()
            dec = decide(tree, ut, ic, 1000, "max", True)
            got = dec["stage"] if dec["stage"] != "ok" else first_arm(dec["arms"])
        except Unparsed as e:
            got = "unparsed:" + str(e)
        ok = got == want
        bad += not ok
        if verbose:
            print("%-4s %-42s want %-12s got %s" % ("ok" if ok else "FAIL", p.decode(), want, got))
    # the uniform / mixed-P flags on a two-branch pattern
    d1 = decide(Reader(rb"[ab]+:x|b:y", False, False).parse(), False, False, 1000, "sub")
    d2 = decide(Reader(rb"[0-9a-f]{1,4}:x|[0-9a-f]{1,4}:y", False, False).parse(), False, False, 1000, "sub")
    for lbl, got, want in (("mixedP not uniform", d1["uniformP"], False), ("equalP uniform", d2["uniformP"], True)):
        bad += got != want
        if verbose:
            print("%-4s %s" % ("ok" if got == want else "FAIL", lbl))
    bad += c2_cross_check(verbose)
    if verbose:
        print("selftest: %d failed" % bad)
    return bad


def c2_cross_check(verbose, n=3000, seed=11):
    """C2: the arm's FACTOR decision on item-NFAs against rinner_model.py's independent implementation
    (its own P text parser and Dijkstra over P's NFA x KMP).  0 disagreements required."""
    import random
    sys.argv_backup = sys.argv
    if "PCRE2_LIB" not in E:
        E["PCRE2_LIB"] = "/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0"
    M = _load("rinner_model", ["rinner_model.py"])
    rnd = random.Random(seed)
    dis = tot = pos = 0
    for _ in range(n):
        c = M.gen_case(rnd)
        P, L = c["P"], c["L"]
        if c["pf"]["atomic"] or c["pf"]["look"]:
            pass
        try:
            theirs = M.factor_witness(P, L) is None
            tb = M.border_free(L)
        except Exception:
            continue
        try:
            items = Reader(P.encode(), False, False).parse()
            items = [("grp", items, False)]
        except Unparsed:
            continue
        run = [frozenset({ord(ch)}) for ch in L]
        # the model's `.` is ALPH (abX), not all bytes: a P with a '.' or a negated class is out of the
        # comparison's domain (the item reader's alphabet is bytes); compare only on those without
        if "." in P or "[^" in P or "$" in P and False:
            continue
        mine = factor_free_sets(items, run, False)
        mb = border_free_sets(run)
        a = arms_for(items, run, False, False)
        tot += 1; pos += (not theirs)
        # the other two arms: fixed width (the model's pw is [lo, hi], zero width counts there) and the alphabet arm
        mfixed = c["pw"][0] == c["pw"][1] and c["pw"][0] > 0
        mdisj = not set(L) <= set(c["palph"])
        if mine is None or mine != theirs or mb != tb or a["fixed"] != mfixed or a["disj"] != mdisj:
            dis += 1
    if verbose:
        print("C2 arms (factor+border, fixed width, alphabet) vs rinner_model.py's own bookkeeping and factor_witness: %d cases (%d with a factor), %d disagreements" % (tot, pos, dis))
    return dis


# ---- weights (walk_survey's method, upper estimates) -----------------------

def weights(wsdir):
    """est ms per bench pattern id = sum over default-config cells of bench_ns * m_gap / T (K1-owned cells
    excluded), walk_survey's K12 formula applied to ANY pattern.  Control: reproduces K12's 15.786 ms."""
    res = {}
    with gzip.open(os.path.join(wsdir, "res_bench.tsv.gz"), "rt") as fh:
        for x in csv.DictReader(fh, delimiter="\t"):
            if x["config"] != "default" or x["regime"] == "match":
                continue
            try:
                mg = int(x["m_gap"])
            except (ValueError, KeyError):
                continue
            if mg > 0:
                k = (x["pid"], {"search": "search_short", "findall": "throughput"}.get(x["regime"], x["regime"]))
                res[k] = res.get(k, 0) + mg
    cells = {}
    with open(os.path.join(wsdir, "cells_bench.tsv")) as fh:
        for x in csv.DictReader(fh, delimiter="\t"):
            if x["config"] != "default":
                continue
            cells[(x["pid"], x["regime"])] = x
    out = collections.defaultdict(float); cellwts = collections.defaultdict(list)
    for (pid, reg), mg in res.items():
        x = cells.get((pid, reg))
        if not x or not x["bench_ns"] or float(x["G_K1"] or 0) > 0:
            continue
        est = float(x["bench_ns"]) * mg / max(1, int(x["T"])) / 1e6
        out[pid] += est; cellwts[pid].append((reg, est))
    return out, cellwts


def main():
    global SABOTAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sabotage", choices=["no-border", "no-factor"])
    ap.add_argument("--catalog", action="append", default=[], help="extra pattern file: one pattern per line (id=file:line)")
    a = ap.parse_args()
    SABOTAGE = a.sabotage
    G.PRIOR = G.prior()
    if a.selftest:
        sys.exit(1 if selftest() else 0)
    out = E["OUT"]; os.makedirs(out, exist_ok=True)
    pop = G.bench_pop() + G.corpus_pop()
    for cat in a.catalog:
        for i, ln in enumerate(open(cat, "rb").read().split(b"\n"), 1):
            if ln.startswith((b"# ", b"#-")) or ln == b"#":     # the file's own comment rule; "#[0-9a-f]{6}" is a pattern
                continue
            if ln and b"\x00" not in ln:
                pop.append(dict(pop="catalog", id="%s:%d" % (os.path.basename(cat), i), enc="byte", icase=False, pat=ln))
    if a.limit:
        pop = pop[:a.limit]
    with cf.ThreadPoolExecutor(a.workers) as ex:
        rows = list(ex.map(pattern_row, pop))
    keys = sorted({k for o in rows for k in o})
    with gzip.open(os.path.join(out, "rincensus_rows%s.tsv.gz" % (("_" + a.sabotage) if a.sabotage else "")), "wt") as fh:
        fh.write("\t".join(keys) + "\n")
        for o in rows:
            fh.write("\t".join(str(o.get(k, "")) for k in keys) + "\n")
    print("wrote", len(rows), "rows")


if __name__ == "__main__":
    main()
