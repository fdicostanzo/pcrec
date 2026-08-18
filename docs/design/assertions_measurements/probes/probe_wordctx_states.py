#!/usr/bin/env python3
"""[M6.1]/DD-6 -- what does carrying `\\b`'s word context in the DFA cost?

A PROTOTYPE, and it says so. pcrec cannot compile `\\b` today, so the state
count of a context-carrying DFA cannot be read off an artifact. This builds the
automaton the design proposes -- DFA state = (NFA pre-set, previous byte was a
word character), assertion closure parameterised by (prev_is_word,
next_is_word) exactly as `src/ir/dfa.c:640-641` parameterises its closure by
`eol_ok` -- and counts its states.

THE NUMBER THAT MATTERS IS THE RATIO, not the absolute count. Both arms of
every comparison come out of THIS constructor, so whatever this prototype does
differently from `src/ir/dfa.c` cancels. The absolute counts are separately
calibrated against pcrec's own `<prefix>_facc[]` length on the assertion-free
arm (--calibrate), and the residual disagreement is reported rather than
hidden.

Minimisation is Moore's algorithm, because pcrec minimises too
(`src/core/compile.c:224`) and an unminimised count would overstate the cost:
the whole question is how many context-split states SURVIVE being distinguished.

Usage: probe_wordctx_states.py PATTERN_FILE [--calibrate PCREC_BIN]
"""
import re as _re
import subprocess
import sys

WORD = set(range(0x30, 0x3A)) | set(range(0x41, 0x5B)) | {0x5F} | set(range(0x61, 0x7B))
ALL = frozenset(range(256))

# ---------------------------------------------------------------- parser ----
# The subset the corpora actually use: literals, \d \w \s and negations, `.`,
# classes with ranges and negation, (...) and (?:...), |, * + ? {m,n}, \b \B.

CLS = {'d': frozenset(range(0x30, 0x3A)),
       'w': frozenset(WORD),
       's': frozenset({0x20, 0x09, 0x0A, 0x0B, 0x0C, 0x0D})}
for k in list(CLS):
    CLS[k.upper()] = ALL - CLS[k]
ESC = {'n': 0x0A, 't': 0x09, 'r': 0x0D, 'f': 0x0C, 'v': 0x0B, '0': 0x00}


class P:
    def __init__(self, s):
        self.s, self.i = s, 0

    def eof(self):
        return self.i >= len(self.s)

    def peek(self):
        return self.s[self.i] if not self.eof() else ''

    def take(self):
        c = self.s[self.i]
        self.i += 1
        return c


def p_alt(p):
    out = [p_cat(p)]
    while p.peek() == '|':
        p.take()
        out.append(p_cat(p))
    return out[0] if len(out) == 1 else ('alt', out)


def p_cat(p):
    out = []
    while not p.eof() and p.peek() not in '|)':
        out.append(p_rep(p))
    return ('cat', out)


def p_rep(p):
    a = p_atom(p)
    while p.peek() and p.peek() in '*+?{':
        if p.peek() == '{':
            m = _re.match(r'\{(\d+)(,(\d*))?\}', p.s[p.i:])
            if not m:
                break
            p.i += m.end()
            lo = int(m.group(1))
            hi = lo if not m.group(2) else (None if m.group(3) == ''
                                            else int(m.group(3)))
        else:
            c = p.take()
            lo, hi = {'*': (0, None), '+': (1, None), '?': (0, 1)}[c]
        if p.peek() == '?' or p.peek() == '+':
            p.take()                      # laziness/possessiveness: no effect
        a = ('rep', a, lo, hi)             # on the LANGUAGE, hence on states
    return a


def p_class(p):
    neg = False
    if p.peek() == '^':
        p.take()
        neg = True
    acc, first = set(), True
    while not p.eof() and (p.peek() != ']' or first):
        first = False
        c = p.take()
        if c == '\\':
            e = p.take()
            if e in CLS:
                acc |= CLS[e]
                continue
            lo = ESC.get(e, ord(e))
        else:
            lo = ord(c)
        if p.peek() == '-' and p.i + 1 < len(p.s) and p.s[p.i + 1] != ']':
            p.take()
            c2 = p.take()
            hi = ESC.get(p.take(), None) if c2 == '\\' else ord(c2)
            if hi is None:
                hi = lo
            acc |= set(range(lo, hi + 1))
        else:
            acc.add(lo)
    p.take()                                                       # the ']'
    s = frozenset(acc)
    return ('cls', ALL - s if neg else s)


def p_atom(p):
    c = p.take()
    if c == '(':
        if p.s[p.i:p.i + 2] == '?:':
            p.i += 2
        a = p_alt(p)
        p.take()                                                   # the ')'
        return a
    if c == '[':
        return p_class(p)
    if c == '.':
        return ('cls', ALL - {0x0A})
    if c == '\\':
        e = p.take()
        if e in ('b', 'B'):
            return ('assert', e)
        if e in CLS:
            return ('cls', CLS[e])
        return ('cls', frozenset({ESC.get(e, ord(e))}))
    if c in '^$':
        return ('anchor', c)
    return ('cls', frozenset({ord(c)}))


# ------------------------------------------------------------------ NFA ----
# Nodes: ('cls', byteset, next) | ('split', a, b) | ('assert', kind, next)
#      | ('match',). `next` is a node id; -1 is a patch hole.

class N:
    def __init__(self):
        self.n = []

    def add(self, t):
        self.n.append(list(t))
        return len(self.n) - 1


def build(nfa, a, nxt):
    """Emit `a` so that finishing it jumps to node `nxt`; return the entry."""
    k = a[0]
    if k == 'cls':
        return nfa.add(('cls', a[1], nxt))
    if k == 'assert':
        return nfa.add(('assert', a[1], nxt))
    if k == 'anchor':
        return nfa.add(('assert', a[1], nxt))
    if k == 'cat':
        for item in reversed(a[1]):
            nxt = build(nfa, item, nxt)
        return nxt
    if k == 'alt':
        e = [build(nfa, b, nxt) for b in a[1]]
        cur = e[-1]
        for x in reversed(e[:-1]):
            cur = nfa.add(('split', x, cur))
        return cur
    if k == 'rep':
        _, body, lo, hi = a
        if hi is None:
            sp = nfa.add(('split', -1, nxt))
            nfa.n[sp][1] = build(nfa, body, sp)
            cur = sp
            for _ in range(lo):                      # {lo,} = lo copies + star
                cur = build(nfa, body, cur)
            return cur
        cur = nxt
        for _ in range(hi - lo):                     # the optional tail
            sp = nfa.add(('split', build(nfa, body, cur), nxt))
            cur = sp
        for _ in range(lo):
            cur = build(nfa, body, cur)
        return cur
    raise AssertionError(k)


def compile_nfa(pat, unanchored=True):
    ast = p_alt(P(pat))
    nfa = N()
    m = nfa.add(('match',))
    start = build(nfa, ast, m)
    if unanchored:
        # nfa_wrap_unanchored's self-loop (src/ir/nfa.c:590): a state-0 loop on
        # every byte, which is how pcrec makes ENG_UNANCH unanchored.
        sp = nfa.add(('split', start, -1))
        loop = nfa.add(('cls', ALL, sp))
        nfa.n[sp][2] = loop
        start = sp
    return nfa, start


# ------------------------------------------------- subset construction ------

def closure(nfa, pre, prev_w, next_w, live_asserts):
    """Nodes that can CONSUME, plus whether MATCH is reachable, under the
    assertion context (prev_w, next_w) -- pcrec's closure(.., bot_ok, eol_ok)
    with one more bit (src/ir/dfa.c:517)."""
    seen, stack, out, acc = set(), list(pre), set(), False
    while stack:
        i = stack.pop()
        if i in seen:
            continue
        seen.add(i)
        nd = nfa.n[i]
        if nd[0] == 'cls':
            out.add(i)
        elif nd[0] == 'match':
            acc = True
        elif nd[0] == 'split':
            stack += [nd[1], nd[2]]
        else:                                                    # 'assert'
            if live_asserts and not assert_true(nd[1], prev_w, next_w):
                continue
            stack.append(nd[2])
    return frozenset(out), acc


def assert_true(kind, prev_w, next_w):
    if kind == 'b':
        return prev_w != next_w
    if kind == 'B':
        return prev_w == next_w
    return True          # ^/$ are not what this probe measures; treat as free


def subset(nfa, start, ctx, live_asserts):
    """ctx: carry the prev-is-word bit in the state identity. Returns
    (nstates, ncls, nstates_min)."""
    # Byte equivalence classes: partition by membership across every 'cls'
    # node, REFINED by the word set when the context bit is live (next_w must
    # be constant inside a class).
    sets = [nd[1] for nd in nfa.n if nd[0] == 'cls']
    key = {}
    for b in range(256):
        k = tuple(b in s for s in sets) + ((b in WORD,) if ctx else ())
        key.setdefault(k, []).append(b)
    classes = list(key.values())
    rep = [c[0] for c in classes]
    ncls = len(classes)

    s0 = (frozenset([start]), False)
    ids, order, work = {s0: 0}, [s0], [s0]
    trans = {}
    while work:
        st = work.pop()
        pre, pw = st
        row = []
        for c in range(ncls):
            b = rep[c]
            nw = (b in WORD) if ctx else False
            live, _ = closure(nfa, pre, pw, nw, live_asserts)
            npre = frozenset(nfa.n[i][2] for i in live if b in nfa.n[i][1])
            if not npre:
                row.append(-1)
                continue
            tgt = (npre, (b in WORD) if ctx else False)
            if tgt not in ids:
                ids[tgt] = len(order)
                order.append(tgt)
                work.append(tgt)
            row.append(ids[tgt])
        trans[ids[st]] = row

    # Accept SIGNATURE: with a next-byte-sensitive assertion the accept bit is
    # a function of (state, next class), which is the design's states x ncls
    # accept table. Moore's output function is that whole vector.
    def sig(st):
        pre, pw = st
        v = []
        for c in range(ncls):
            nw = (rep[c] in WORD) if ctx else False
            v.append(closure(nfa, pre, pw, nw, live_asserts)[1])
        v.append(closure(nfa, pre, pw, False, live_asserts)[1])   # end of input
        return tuple(v)

    n = len(order)
    part = {}
    for i, st in enumerate(order):
        part.setdefault(sig(st), []).append(i)
    cls_of = {}
    for gi, (_, mem) in enumerate(sorted(part.items())):
        for i in mem:
            cls_of[i] = gi
    while True:                                                     # Moore
        new = {}
        for i in range(n):
            k = (cls_of[i],) + tuple(cls_of.get(t, -1) if t >= 0 else -1
                                     for t in trans[i])
            new.setdefault(k, []).append(i)
        if len(new) == len(set(cls_of.values())):
            break
        cls_of = {i: gi for gi, (_, mem) in enumerate(sorted(new.items()))
                  for i in mem}
    return n, ncls, len(set(cls_of.values()))


NFA_CAP = 400        # this prototype is O(states * ncls) closures per pass and
                     # is not the shipped constructor; a bounded repeat that
                     # replicates into thousands of NFA nodes is reported as
                     # too-big rather than silently costing an hour.


def measure(pat):
    """(baseline, with-\\b) minimised state counts for `\\b<pat>\\b`."""
    nfa0, s0 = compile_nfa(pat)
    if len(nfa0.n) > NFA_CAP:
        raise MemoryError("NFA %d nodes > cap %d" % (len(nfa0.n), NFA_CAP))
    base = subset(nfa0, s0, ctx=False, live_asserts=False)
    nfa1, s1 = compile_nfa(r'\b' + pat + r'\b')
    wb = subset(nfa1, s1, ctx=True, live_asserts=True)
    return base, wb


def calibrate(pcrec, pat, mine):
    r = subprocess.run([pcrec, "-p", "rx", "--no-captures", "-o", "-", "--", pat],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None
    m = _re.search(r"static const unsigned char rx_facc\[(\d+)\]", r.stdout)
    return int(m.group(1)) if m else None


def main():
    pats = [l.strip() for l in open(sys.argv[1])
            if l.strip() and not l.startswith("#")]
    pcrec = sys.argv[3] if len(sys.argv) > 3 else None

    print("%-38s %7s %7s %6s %6s %6s" %
          ("pattern (measured as \\bPAT\\b)", "base", "wordctx", "ratio",
           "ncls0", "ncls1"))
    ratios, rows, cal_ok, cal_bad = [], 0, 0, []
    for pat in pats:
        try:
            (b_n, b_cls, b_min), (w_n, w_cls, w_min) = measure(pat)
        except Exception as e:                       # unsupported syntax
            print("%-38s  SKIP (%s)" % (pat[:38], type(e).__name__))
            continue
        rows += 1
        ratios.append(w_min / b_min)
        print("%-38s %7d %7d %5.2fx %6d %6d" %
              (pat[:38], b_min, w_min, w_min / b_min, b_cls, w_cls))
        if pcrec:
            got = calibrate(pcrec, pat, b_min)
            if got is None:
                pass
            elif got == b_min:
                cal_ok += 1
            else:
                cal_bad.append((pat, b_min, got))

    ratios.sort()
    print("\nn = %d patterns" % rows)
    print("state ratio (minimised, \\bPAT\\b vs PAT) "
          "min/median/max = %.2fx / %.2fx / %.2fx" %
          (ratios[0], ratios[len(ratios) // 2], ratios[-1]))
    print("patterns at ratio <= 1.00x: %d ; > 2.00x: %d" %
          (sum(1 for r in ratios if r <= 1.0), sum(1 for r in ratios if r > 2.0)))
    if pcrec:
        print("\nCALIBRATION against pcrec's own rx_facc[] on the "
              "assertion-free arm: %d agree, %d disagree" %
              (cal_ok, len(cal_bad)))
        for pat, mine, got in cal_bad[:12]:
            print("   %-34s prototype %4d  pcrec %4d" % (pat[:34], mine, got))


main()
