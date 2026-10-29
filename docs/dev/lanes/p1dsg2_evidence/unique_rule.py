#!/usr/bin/env python3
"""Lane p1dsg2 (2026-10-29): review r1 A1, the UNIQUE rule restated over (state, class) pairs,
shown on the design's own witnesses three independent ways.

THE RULE (rev 1, admission row `excl-cand`): W = rev(P.L) is UNIQUE iff for no reachable state s
and byte class c with accepts(s, c) does step(s, c) reach a state s' that has ANY accepting pair
(s', c'), where c' ranges over the byte classes AND `none` (the plain accept at the subject's
start, i.e. the floor/positional accept).  An accept and the step that continues read the SAME
byte subject[p-1], so a by-class accept whose class differs from the looping class is terminal.

Three columns per witness:
  pcrec   the rule run on pcrec's OWN emitted reverse tables of P.L (`-p rw`, RECOVER shortcuts
          denied so the reverse-pass machine is emitted; the machine W would be); "no reverse
          machine" where pcrec routes P.L off the reverse pass (pcrec_nfa_has_bot: ^ \\A \\G).
  model   the same rule on an INDEPENDENT reverse DFA built here from P.L (a small Thompson NFA
          + subset construction over the witness's own bytes, assertions evaluated on the
          (left byte, right byte) pair; ^ \\A \\G hold only at `none`, the walk's floor at 0).
          Shares no code with pcrec.
  truth   libpcre2 10.46: find-all of R = P.L.S, against the per-hit CAND tactic (each hit j of
          L ascending from the floor, starts(j) = every s >= floor where P matches exactly
          [s, j) in context with L next, ONE anchored attempt of R at min starts(j)), exhaustive
          over every subject up to a length over the witness's alphabet. `wrong` = subjects whose
          span+capture lists differ; `max|starts|` = the largest starts(j) seen.
A witness is CONSISTENT when rule=UNIQUE implies 0 wrong, and rule=NOT is shown load-bearing by
max|starts| >= 2 (and, for the review's named witnesses, wrong >= 1).
Usage: PCREC=build/pcrec python3 -I unique_rule.py [--maxlen 6]   (about 13 pcrec compiles)"""
import argparse, ctypes, itertools, os, re, subprocess, sys, tempfile

# ---------------------------------------------------------------- libpcre2 (truth)
LIB = ctypes.CDLL(os.environ.get("PCRE2_LIB", "/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0"))
SZ = ctypes.c_size_t
LIB.pcre2_compile_8.restype = ctypes.c_void_p
LIB.pcre2_compile_8.argtypes = [ctypes.c_char_p, SZ, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(SZ), ctypes.c_void_p]
LIB.pcre2_match_data_create_8.restype = ctypes.c_void_p
LIB.pcre2_match_data_create_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
LIB.pcre2_match_8.restype = ctypes.c_int
LIB.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, SZ, SZ, ctypes.c_uint32, ctypes.c_void_p,
                              ctypes.c_void_p]
LIB.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(SZ)
LIB.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
ANCHORED = 0x80000000
MD = LIB.pcre2_match_data_create_8(64, None)
_cc = {}


def comp(pat):
    if pat not in _cc:
        e, o = ctypes.c_int(), SZ()
        c = LIB.pcre2_compile_8(pat.encode(), len(pat.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        if not c:
            raise ValueError("pcre2 compile %r" % pat)
        _cc[pat] = c
    return _cc[pat]


def m(pat, subj, start, opts=0):
    rc = LIB.pcre2_match_8(comp(pat), subj, len(subj), start, opts, MD, None)
    if rc < 0:
        if rc == -1:
            return None
        raise RuntimeError("pcre2 rc %d" % rc)
    ov = LIB.pcre2_get_ovector_pointer_8(MD)
    return tuple(ov[i] for i in range(2 * rc))


def at_floor(pat, pos):
    # \G holds at the search's start (the walk's floor), never elsewhere
    return pat.replace(r"\G", r"(?<=\A[\s\S]{%d})" % pos)


def truth(R, subj):
    out, pos = [], 0
    while pos <= len(subj):
        r = m(at_floor(R, pos), subj, pos)
        if r is None:
            break
        out.append(r)
        pos = r[1] if r[1] > r[0] else r[1] + 1
    return out


def starts(P, L, subj, j, pos):
    pat = r"(?:%s)(?<=\A[\s\S]{%d})(?=\Q%s\E)" % (at_floor(P, pos), j, L)
    return [s for s in range(pos, j + 1) if m(pat, subj, s, ANCHORED) is not None]


def per_hit(P, L, S, subj, stat):
    R = P + L + S
    out, pos = [], 0
    j = subj.find(L.encode(), pos)
    while j >= 0:
        st = starts(P, L, subj, j, pos)
        stat[0] = max(stat[0], len(st))
        r = m(at_floor(R, pos), subj, min(st), ANCHORED) if st else None
        if r is not None:
            out.append(r)
            pos = r[1]
            j = subj.find(L.encode(), max(pos, j + 1))
        else:
            j = subj.find(L.encode(), j + 1)
    return out


# ---------------------------------------------------------------- the rule on a reverse machine
def rule(states0, classes, step, acc, plain):
    """states0: seed; step(s,c) -> s' or None; acc(s,c) -> bool; plain(s) -> bool (c = none).
    Returns (UNIQUE?, witness pair)."""
    seen, todo = set(), [states0]
    while todo:
        s = todo.pop()
        if s in seen:
            continue
        seen.add(s)
        for c in classes:
            t = step(s, c)
            if t is not None:
                todo.append(t)
    def has_acc(s):
        return plain(s) or any(acc(s, c) for c in classes)
    for s in seen:
        for c in classes:
            if not acc(s, c):
                continue
            t = step(s, c)
            if t is None:
                continue
            reach, todo = set(), [t]
            while todo:
                u = todo.pop()
                if u in reach:
                    continue
                reach.add(u)
                if has_acc(u):
                    return False, (s, c, u)
                todo += [v for v in (step(u, d) for d in classes) if v is not None]
    return True, None


def rule_r0(states0, classes, step, acc, plain):
    """The ORIGINAL design's state-level wording (p1dsg rev 0): NOT unique if an accepting state
    (any accepting pair) reaches an accepting state in one or more steps on ANY class."""
    def has_acc(s):
        return plain(s) or any(acc(s, c) for c in classes)
    seen, todo = set(), [states0]
    while todo:
        s = todo.pop()
        if s in seen:
            continue
        seen.add(s)
        todo += [t for t in (step(s, c) for c in classes) if t is not None]
    for s in seen:
        if not has_acc(s):
            continue
        reach, todo = set(), [t for t in (step(s, c) for c in classes) if t is not None]
        while todo:
            u = todo.pop()
            if u in reach:
                continue
            reach.add(u)
            if has_acc(u):
                return False
            todo += [v for v in (step(u, d) for d in classes) if v is not None]
    return True


def pcrec_rule(pcrec, PL):
    NOREC = ["-fno-start-pinned", "-fno-start-width", "-fno-start-landing", "-fno-rev-end"]
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as d:
        out = os.path.join(d, "w.c")
        subprocess.run([pcrec, "-p", "rw", "--features", "all"] + NOREC + ["-o", out, "--pattern", PL],
                       check=True, capture_output=True, timeout=60)
        src = open(out).read()
    start = re.search(r'#define RW_DFA_START "([^"]*)"', src)
    if "rw_reverse_next_state" not in src:
        return "no reverse machine (RW_DFA_START %s)" % (start.group(1) if start else "?")
    def tab(name):
        body = re.search(r"rw_reverse_%s\[\d+\] = \{(.*?)\};" % name, src, re.S).group(1)
        return [int(x) for x in body.replace("\n", " ").split(",") if x.strip()]
    nxt, pa = tab("next_state"), tab("is_accepting")
    ncls = max(tab("byte_class")) + 1
    # no by-class table: the machine's accepts read no left context, so every class accepts as
    # the plain accept does
    pc = tab("is_accepting_by_class") if "rw_reverse_is_accepting_by_class" in src else \
        [pa[s - s % ncls] for s in range(len(nxt))]
    args = (0, range(ncls), lambda s, c: None if nxt[s + c] == 65535 else nxt[s + c],
            lambda s, c: pc[s + c] == 1, lambda s: pa[s] == 1)
    u, w = rule(*args)
    r0 = "r0 says %s" % ("UNIQUE" if rule_r0(*args) else "NOT")
    return ("UNIQUE" if u else "NOT (accept (%d,%d) steps to accepting %d)" % (w[0] // ncls, w[1], w[2] // ncls)) + "; " + r0


# ---------------------------------------------------------------- the independent model
WORD = set(b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz")


class NFA:
    def __init__(self):
        self.edges = []   # (u, kind, arg, v): kind 'e' eps, 'b' byte set, 'a' assertion

    def new(self):
        self.edges.append(None)
        return len(self.edges) - 1

    def add(self, u, kind, arg, v):
        self.edges.append((u, kind, arg, v))


def parse(pat):
    """Tiny regex subset: literals, \\w \\d \\b \\A \\G ^, [...], (?:..), (..), |, * + ? {m,n}."""
    i = 0
    def atom_set(ch):
        if ch == "w": return frozenset(WORD)
        if ch == "d": return frozenset(b"0123456789")
        return frozenset(ord(ch).to_bytes(1, "big"))
    def alt():
        nonlocal i
        branches = [seq()]
        while i < len(pat) and pat[i] == "|":
            i += 1
            branches.append(seq())
        return ("alt", branches)
    def seq():
        nonlocal i
        items = []
        while i < len(pat) and pat[i] not in "|)":
            a = atom()
            if i < len(pat) and pat[i] in "*+?{":
                q = pat[i]; i += 1
                if q == "*": lo, hi = 0, None
                elif q == "+": lo, hi = 1, None
                elif q == "?": lo, hi = 0, 1
                else:
                    k = pat.index("}", i); lo, _, hi = pat[i:k].partition(","); i = k + 1
                    lo = int(lo); hi = None if _ and not hi else int(hi or lo)
                a = ("rep", a, lo, hi)
            items.append(a)
        return ("seq", items)
    def atom():
        nonlocal i
        ch = pat[i]; i += 1
        if ch == "(":
            if pat.startswith("?:", i): i += 2
            a = alt(); assert pat[i] == ")"; i += 1
            return a
        if ch == "[":
            neg = pat[i] == "^"
            if neg: i += 1
            s = set()
            while pat[i] != "]":
                if pat[i] == "\\":
                    s |= atom_set(pat[i + 1]); i += 2
                elif pat[i + 1] == "-" and pat[i + 2] != "]":
                    s |= set(range(ord(pat[i]), ord(pat[i + 2]) + 1)); i += 3
                else:
                    s.add(ord(pat[i])); i += 1
            i += 1
            return ("set", frozenset(set(range(256)) - s) if neg else frozenset(s))
        if ch == "\\":
            e = pat[i]; i += 1
            if e in "bAG": return ("assert", e)
            return ("set", atom_set(e))
        if ch == "^": return ("assert", "A")   # non-multiline ^ is \A
        if ch == ".": return ("set", frozenset(set(range(256)) - {10}))
        return ("set", atom_set(ch))
    t = alt(); assert i == len(pat), pat
    return t


def build(nfa, t, u, v):
    k = t[0]
    if k == "set": nfa.add(u, "b", t[1], v)
    elif k == "assert": nfa.add(u, "a", t[1], v)
    elif k == "alt":
        for b in t[1]: build(nfa, b, u, v)
    elif k == "seq":
        cur = u
        for x in t[1]:
            nx = nfa.new(); build(nfa, x, cur, nx); cur = nx
        nfa.add(cur, "e", None, v)
    elif k == "rep":
        _, a, lo, hi = t
        cur = u
        for _ in range(lo):
            nx = nfa.new(); build(nfa, a, cur, nx); cur = nx
        if hi is None:
            loop = nfa.new(); nfa.add(cur, "e", None, loop); build(nfa, a, loop, loop); nfa.add(loop, "e", None, v)
        else:
            for _ in range(hi - lo):
                nx = nfa.new(); nfa.add(cur, "e", None, v); build(nfa, a, cur, nx); cur = nx
            nfa.add(cur, "e", None, v)


def holds(kind, left, right):
    if kind == "b":
        return (left is not None and left in WORD) != (right is not None and right in WORD)
    return left is None          # \A ^ \G: only at the walk's floor at 0 (c = none)


def model_rule(PL, alphabet):
    nfa = NFA(); s0 = nfa.new(); f = nfa.new(); build(nfa, parse(PL), s0, f)
    E = [e for e in nfa.edges if e]
    def close(S, left, right):
        S, todo = set(S), list(S)
        while todo:
            x = todo.pop()
            for (a, kind, arg, b) in E:
                if b == x and (kind == "e" or (kind == "a" and holds(arg, left, right))) and a not in S:
                    S.add(a); todo.append(a)
        return frozenset(S)
    def step(st, c):
        S, right = st
        if c is None: return None
        T = close(S, c, right)
        N = frozenset(a for (a, kind, arg, b) in E if kind == "b" and b in T and c in arg)
        return (N, c) if N else None
    def acc(st, c):
        return s0 in close(st[0], c, st[1])
    u, w = rule((frozenset({f}), None), list(alphabet), step, acc, lambda st: acc(st, None))
    return "UNIQUE" if u else "NOT (accept on %r steps to an accepting state)" % chr(w[1])


# ---------------------------------------------------------------- witnesses
W = [  # name, P, L, S, alphabet, named subject (or None), role
    ("dup-param (L = '=')", r"\b(\w+)", "=", r"[^&]*&(?:[^&]*&)*\1=", "ab=&", None, "the stage-2 UNIQUE mover"),
    ("SIM-1 nullable \\b", r"\b(\w*)", "=x", r"\1", "ab=x ", "ab=x", "review A1 witness"),
    ("SIM-1 \\b at P's end", r"(\w+)\b", "=x", r"\1", "ab=x ", "ab=xb", "simulate's second form"),
    ("SIM-2 positional ^", r"(?:^|-)([\w-]+)", "=", r"\1\b", "ab-=", "ab-cd=cd", "review A1 witness"),
    ("SIM-2 positional \\A", r"(?:\A|-)([\w-]+)", "=", r"\1\b", "ab-=", "ab-cd=cd", "review A1 witness"),
    ("SIM-2 positional \\G", r"(?:\G|-)([\w-]+)", "=", r"\1\b", "ab-=", "ab-cd=cd", "review A1 witness"),
    ("dup-param (L = '&')", r"\b(\w+)=[^&]*", "&", r"(?:[^&]*&)*\1=", "ab=& ", "a=1 b=2&b=", "S1: the landmark choice"),
    ("LF-E1 (a+)X\\1", r"(a+)", "X", r"\1", "aX", "aaXa", "locate_finish LF-E1"),
    ("fixed width", r"(\w\w)", "=", r"\1", "ab=", None, "fixed width implies UNIQUE"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maxlen", type=int, default=6)
    a = ap.parse_args()
    pcrec = os.environ.get("PCREC", "build/pcrec")
    bad = 0
    print("# p1dsg2 unique_rule.py: libpcre2 10.46 (truth), pcrec %s (pcrec column), maxlen %d" % (pcrec, a.maxlen))
    print("# witness | P | L | S | pcrec rule on rev(P.L) (+ rev 0's state-level wording, r0) | model rule | named subject: truth vs per-hit | "
          "exhaustive: subjects, wrong, max|starts|")
    for name, P, L, S, alpha, named, role in W:
        pr = pcrec_rule(pcrec, P + L)
        mr = model_rule(P + L, set(alpha.encode()) | {ord("a"), ord(" ")})
        nm = ""
        if named:
            t, st = truth(P + L + S, named.encode()), [0]
            h = per_hit(P, L, S, named.encode(), st)
            nm = "%r: libpcre2 %s, per-hit %s" % (named, t, h)
        n = wrong = 0; st = [0]
        for ln in range(1, a.maxlen + 1):
            for tup in itertools.product(alpha, repeat=ln):
                subj = "".join(tup).encode()
                n += 1
                if truth(P + L + S, subj) != per_hit(P, L, S, subj, st):
                    wrong += 1
        uniq_m = mr.startswith("UNIQUE")
        ok = (wrong == 0) if uniq_m else (st[0] >= 2)
        if pr.startswith("UNIQUE") != uniq_m and not pr.startswith("no reverse"):
            ok = False
        bad += not ok
        print("%s | %s | %s | %s | %s | %s | %s | %d subjects, %d wrong, max|starts| %d | %s (%s)" % (
            name, P, L, S, pr, mr, nm or "-", n, wrong, st[0], "CONSISTENT" if ok else "INCONSISTENT", role))
    print("# verdict: %s" % ("PASS (rule agrees with truth on every witness)" if not bad else "FAIL %d" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
