#!/usr/bin/env python3
"""D164 hand twin: the END_MARK on the two engine paths it changes, as a
priority NFA simulation (a Pike VM is exactly the subset construction pcrec's
DFA determinizes, so a state here is a DFA state there), with every subject
byte load COUNTED and every answer checked against libpcre2.

Part A (forward, `X(?=Y)` with bounded Y): the unanchored leftmost-first scan
over the LOWERED NFA, where every thread past the mark carries its distance d
since the mark and the first ACCEPT in priority order reports end = pos - d
(D3's accept-pruning, unchanged).  Checked at every start position.

Part B (reverse, `X$`): today's rev-end (two seeds n and n-1, tie -> one
anchored forward run) against the mark's one walk from n over
rev(X MARK \\n? \\z), three ways:
  M1  tagged walk: each reverse thread carries the distance at which it
      crossed the mark (0 or 1); at s* one distance is the end, two are a
      tie resolved by the static fact `mark_prio` or else a forward run;
  M0  untagged walk: one walk, then a forward run whenever s[n-1] == '\\n'
      and `nl_last` (the fact rev-end already computes);
  T   today: two walks, a forward run on a tie.
Loads are subject bytes read.  Usage: python3 -I twin.py [--k N]
"""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcre2
TP = os.environ.get('TWIN_PLANT', '')   # a deliberately wrong variant (controls)
from diff_lowering import L, C, A, R, G, LA, text, lower

# ---- an ordered NFA from the mini AST ---------------------------------------
# node: ('chr', set, next) ('split', [targets]) ('mark', next) ('end', next)
#       ('acc',)  -- built forward or REVERSED

ESC = {'\\s': set(b' \t\n\r\x0b\x0c'), '\\d': set(b'0123456789'),
       '\\w': set(b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'),
       '\\n': {10}, '\\.': {46}, '.': set(range(256)) - {10}}


def lit_sets(t):
    """a literal token of the mini AST -> list of byte sets (one per char)."""
    if t in ESC:
        return [ESC[t]]
    if t.startswith('[') and t.endswith(']'):
        body = t[1:-1]
        out, i = set(), 0
        while i < len(body):
            if body[i] == '\\':
                out |= ESC['\\' + body[i + 1]]; i += 2
            elif i + 2 < len(body) and body[i + 1] == '-':
                out |= set(range(ord(body[i]), ord(body[i + 2]) + 1)); i += 3
            else:
                out.add(ord(body[i])); i += 1
        return [out]
    out, i = [], 0
    while i < len(t):
        if t[i] == '\\':
            out.append(ESC[t[i:i + 2]]); i += 2
        elif t[i] == '.':
            out.append(ESC['.']); i += 1
        else:
            out.append({ord(t[i])}); i += 1
    return out


class NFA:
    def __init__(self):
        self.n = []

    def add(self, x):
        self.n.append(list(x)); return len(self.n) - 1


def build(nfa, a, nxt, rev):
    """Thompson construction with priority order; returns the entry state.
    `rev` builds the REVERSED language (concatenation order flipped)."""
    k = a[0]
    if k == 'lit':
        sets = lit_sets(a[1])
        if rev:
            sets = sets[::-1]
        for s in reversed(sets):
            nxt = nfa.add(('chr', frozenset(s), nxt))
        return nxt
    if k == 'cat':
        xs = a[1][::-1] if rev else a[1]
        for x in reversed(xs):
            nxt = build(nfa, x, nxt, rev)
        return nxt
    if k == 'alt':
        return nfa.add(('split', [build(nfa, x, nxt, rev) for x in a[1]]))
    if k in ('cap', 'ncg'):
        return build(nfa, a[1], nxt, rev)
    if k == 'rep':
        _, x, lo, hi, mode = a
        assert mode in ('g', 'l')
        # optional tail (hi - lo copies) or a star loop, then lo copies.
        if hi is None:
            sp = nfa.add(('split', []))
            body = build(nfa, x, sp, rev)
            nfa.n[sp][1] = [body, nxt] if mode == 'g' else [nxt, body]
            tail = sp
        else:
            tail = nxt
            for _ in range(hi - lo):
                body = build(nfa, x, tail, rev)
                tail = nfa.add(('split', [body, nxt] if mode == 'g' else [nxt, body]))
        cur = tail
        for _ in range(lo):
            cur = build(nfa, x, cur, rev)
        return cur
    if k == 'mark':
        return nfa.add(('mark', nxt))
    if k == 'anch':
        assert a[1] == 'z'
        return nfa.add(('end', nxt))
    raise ValueError(k)


def compile_nfa(ast, rev=False):
    nfa = NFA()
    acc = nfa.add(('acc',))
    start = build(nfa, ast, acc, rev)
    return nfa, start


# ---- forward Pike VM with mark distances (part A) ---------------------------

class Count:
    def __init__(self): self.loads = 0


def closure(nfa, items, pos, n, out, seen):
    """items: list of (state, d, start) in priority order. Appends the closed
    threads (chr / acc) to `out` in priority order; d None = before the mark."""
    stack = list(reversed(items))
    while stack:
        st, d, s0 = stack.pop()
        key = (st, d)
        if key in seen:
            continue
        seen.add(key)
        node = nfa.n[st]
        t = node[0]
        if t == 'split':
            for tg in reversed(node[1]):
                stack.append((tg, d, s0))
        elif t == 'mark':
            stack.append((node[1], 0 if d is None else d, s0))
        elif t == 'end':
            if pos == n:
                stack.append((node[1], d, s0))
        else:
            out.append((st, d, s0))


def search_fwd(nfa, start, subj, sp, cnt):
    """Leftmost-first unanchored search from sp; returns (start, end) of the
    REPORTED match (end = accept position - mark distance) or None."""
    n = len(subj)
    clist, best = [], None
    for pos in range(sp, n + 1):
        items = [(st, d, s0) for st, d, s0 in clist]
        if best is None:
            items.append((start, None, pos))          # a new, lowest-priority start
        threads, seen = [], set()
        closure(nfa, items, pos, n, threads, seen)
        nl = []
        for st, d, s0 in threads:
            if nfa.n[st][0] == 'acc':
                best = (s0, pos - (0 if TP == 'fwd-consumed-end' else (d or 0)))
                break                                   # D3: prune lower priority
            nl.append((st, d, s0))
        if pos == n:
            break
        if not nl:
            if best is not None:
                break
            clist = []
            continue
        cnt.loads += 1
        c = subj[pos]
        clist = []
        for st, d, s0 in nl:
            node = nfa.n[st]
            if c in node[1]:
                clist.append((node[2], None if d is None else d + 1, s0))
        if not clist and best is not None:
            break
    return best


def part_a():
    cases = [('dpx', C(R(L('\\d'), 1, None), LA(L('px')))),
             ('greedy-var', C(R(L('a'), 1, None), LA(C(R(L('a'), 0, 1), L('b'))))),
             ('lazy-var', C(R(L('a'), 1, None, 'l'), LA(C(R(L('a'), 0, 1), L('b'))))),
             ('alt-mixed', A(C(L('a'), LA(L('bc'))), L('ab'), C(R(L('[ab]'), 1, None), LA(L('c'))))),
             ('foo-bar', C(L('foo'), LA(A(L('bar'), L('ba'))))),
             ('empty-look', LA(L('ab'))),
             ('dollar', C(R(L('[ab]'), 0, None), ('anch', '$'))),
             ('lazy-dollar', C(R(L('[ab\\n]'), 0, None, 'l'), ('anch', '$')))]
    alpha = [b'a', b'b', b'c', b'\n', b'1', b'p', b'x', b'f', b'o', b'r']
    rnd = random.Random(164)
    subs = [b''.join(rnd.choice(alpha) for _ in range(rnd.randrange(0, 9))) for _ in range(3000)]
    subs += [b'12px', b'foobar', b'aab', b'aaab', b'abc', b'ab\n', b'\n']
    tot = bad = 0
    for name, ast in cases:
        low = lower(ast)
        nfa, st = compile_nfa(low)
        code = pcre2.Code(text(ast)[0])
        for s in subs:
            for sp in range(len(s) + 1):
                tot += 1
                m = code.match(s, sp)
                want = None if m is None else m[0]
                got = search_fwd(nfa, st, s, sp, Count())
                if want != got:
                    bad += 1
                    if bad <= 5:
                        print('  A-DIFF', name, s, sp, want, got)
    print('A forward, lowered NFA + accept-distance, vs libpcre2: %d cells, %d differences' % (tot, bad))
    return bad


# ---- reverse walks (part B) --------------------------------------------------

def rev_walk(nfa, start, subj, seed, floor, tagged, cnt):
    """One reverse subset walk seeded at `seed`, reading subj[seed-1], ...
    Threads carry the mark distance (seed - mark position) when tagged.
    Returns (smallest accepting position, its tag set) or (None, None)."""
    n = len(subj)
    items = [(start, None, 0)]
    pos = seed
    best, best_tags = None, None
    while True:
        threads, seen = [], set()
        # reverse closure: 'end' (\z) holds where pos == n; mark records seed - pos
        stack = list(reversed(items)); out = []
        while stack:
            st, d, _ = stack.pop()
            key = (st, d if tagged else None)
            if key in seen:
                continue
            seen.add(key)
            node = nfa.n[st]
            t = node[0]
            if t == 'split':
                for tg in reversed(node[1]):
                    stack.append((tg, d, 0))
            elif t == 'mark':
                stack.append((node[1], seed - pos, 0))
            elif t == 'end':
                if pos == n:
                    stack.append((node[1], d, 0))
            else:
                out.append((st, d if tagged else None, 0))
        accs = {d for st, d, _ in out if nfa.n[st][0] == 'acc'}
        if accs:
            best, best_tags = pos, accs
        live = [x for x in out if nfa.n[x[0]][0] == 'chr']
        if not live or pos <= floor:
            break
        cnt.loads += 1
        c = subj[pos - 1]
        items = [(nfa.n[st][2], d, 0) for st, d, _ in live if c in nfa.n[st][1]]
        if not items:
            break
        pos -= 1
    return best, best_tags


def fwd_anchored_end(nfa, start, subj, at, cnt):
    """The anchored leftmost-first run from `at` (rev-end's tie arm): returns
    the reported end, counting loads."""
    r = search_fwd_anchored(nfa, start, subj, at, cnt)
    return r


def search_fwd_anchored(nfa, start, subj, at, cnt):
    n = len(subj)
    clist, best = [(start, None, at)], None
    for pos in range(at, n + 1):
        threads, seen = [], set()
        closure(nfa, clist, pos, n, threads, seen)
        nl = []
        for st, d, s0 in threads:
            if nfa.n[st][0] == 'acc':
                best = pos - (d or 0)
                break
            nl.append((st, d, s0))
        if pos == n or not nl:
            break
        cnt.loads += 1
        c = subj[pos]
        clist = [(nfa.n[st][2], None if d is None else d + 1, s0) for st, d, s0 in nl if c in nfa.n[st][1]]
        if not clist:
            break
    return best


def mark_prio(nfa, start, alphabet, cap=20000):
    """The static tie fact: over every reachable anchored forward state (an
    ordered thread list WITHOUT pruning, mark distances carried), at the
    subject end: when two or more distances accept, which one is first in
    priority order?  Returns ('const', d), ('none',) or ('state-dependent',)."""
    seen_states, frontier, winners = set(), [], set()
    init = ((start, None),)
    frontier.append(init)
    while frontier:
        state = frontier.pop()
        if state in seen_states:
            continue
        seen_states.add(state)
        if len(seen_states) > cap:
            return ('state-dependent', 'cap')
        # at the end: close with \z true, list accepting distances in order
        out, seen = [], set()
        closure(nfa, [(s, d, 0) for s, d in state], 1, 1, out, seen)
        accd = [d for st, d, _ in out if nfa.n[st][0] == 'acc']
        if len(set(accd)) >= 2:
            winners.add(accd[0])
        # successors (closure with \z false, then one byte)
        out, seen = [], set()
        closure(nfa, [(s, d, 0) for s, d in state], 0, 1, out, seen)
        for c in alphabet:
            nxt = tuple((nfa.n[st][2], None if d is None else d + 1)
                        for st, d, _ in out if nfa.n[st][0] == 'chr' and c in nfa.n[st][1])
            if nxt:
                frontier.append(nxt)
    if not winners:
        return ('none',)
    if len(winners) == 1:
        return ('const', winners.pop())
    return ('state-dependent',)


def nl_last(rnfa, rstart):
    """rev-end's fact on the UNLOWERED reverse machine of X: can a match end
    by consuming the final newline (does the walk seeded at n step on '\\n')?"""
    out, seen = [], set()
    closure(rnfa, [(rstart, None, 0)], 1, 1, out, seen)
    return any(rnfa.n[st][0] == 'chr' and 10 in rnfa.n[st][1] for st, _, _ in out)


def strategies(X, subj, facts, cnt_t, cnt_m1, cnt_m0):
    """Return the three strategies' answers for X$ searched from 0."""
    n = len(subj)
    xr_nfa, xr_start, low_rnfa, low_rstart, fwd_nfa, fwd_start, prio, nll = facts
    # --- T: today's two seeds over rev(X), tie -> anchored forward run
    starts = {}
    for seed in ([n, n - 1] if n and subj[n - 1] == 10 else [n]):
        p, _ = rev_walk(xr_nfa, xr_start, subj, seed, 0, False, cnt_t)
        if p is not None:
            starts[seed] = p
    t = None
    if starts:
        sstar = min(starts.values())
        ends = [e for e, p in starts.items() if p == sstar]
        if len(ends) == 1:
            t = (sstar, ends[0])
        else:
            t = (sstar, search_fwd_anchored(fwd_nfa, fwd_start, subj, sstar, cnt_t))
    # --- M1: one tagged walk over rev(X MARK \n? \z)
    p, tags = rev_walk(low_rnfa, low_rstart, subj, n, 0, True, cnt_m1)
    m1 = None
    if p is not None:
        if TP == 'm1-no-tags':
            m1 = (p, n)
        elif len(tags) == 1:
            m1 = (p, n - next(iter(tags)))
        elif prio[0] == 'const':
            m1 = (p, n - (1 - prio[1] if TP == 'm1-prio-flipped' else prio[1]))
        else:
            m1 = (p, search_fwd_anchored(fwd_nfa, fwd_start, subj, p, cnt_m1))
    # --- M0: one untagged walk, forward run when a tie is possible
    p, _ = rev_walk(low_rnfa, low_rstart, subj, n, 0, False, cnt_m0)
    m0 = None
    if p is not None:
        if n and subj[n - 1] == 10 and nll and TP != 'm0-skip-finish':
            m0 = (p, search_fwd_anchored(fwd_nfa, fwd_start, subj, p, cnt_m0))
        elif n and subj[n - 1] == 10 and p <= n - 1:
            m0 = (p, n - 1)
        else:
            m0 = (p, n)
    return t, m1, m0


def make_facts(X):
    xr_nfa, xr_start = compile_nfa(X, rev=True)
    low = lower(C(X, ('anch', '$')))
    low_rnfa, low_rstart = compile_nfa(low, rev=True)
    fwd_nfa, fwd_start = compile_nfa(low)
    alphabet = sorted({b for node in fwd_nfa.n if node[0] == 'chr' for b in node[1]} | {0x51})
    alphabet = [b for b in alphabet if b < 128]
    prio = mark_prio(fwd_nfa, fwd_start, alphabet)
    nll = nl_last(xr_nfa, xr_start)
    return (xr_nfa, xr_start, low_rnfa, low_rstart, fwd_nfa, fwd_start, prio, nll)


B_CASES = [
    ('ws-greedy', R(L('\\s'), 1, None)),
    ('ws-lazy', R(L('\\s'), 0, None, 'l')),
    ('digits', R(L('\\d'), 1, None)),
    ('txt', C(R(L('[a-z]'), 1, None), L('.txt'))),
    ('alt-a-anl', A(L('a'), L('a\\n'))),
    ('alt-anl-a', A(L('a\\n'), L('a'))),
    ('mixed-prio', A(R(L('\\s'), 1, None), C(L('x'), R(L('\\s'), 0, None, 'l')))),
    ('any-greedy', R(L('[\\s\\w]'), 0, None)),
    ('nl-only-lazy', C(L('a'), R(L('\\n'), 0, 2, 'l'))),
    ('nl-only-greedy', C(L('a'), R(L('\\n'), 0, 2))),
]


def part_b(k):
    print('B reverse from the end, X$ (k = %d for the cost cells)' % k)
    rnd = random.Random(1640)
    alpha = [b' ', b'\t', b'\n', b'a', b'x', b'Q', b'1', b'.', b't']
    subs = [b''.join(rnd.choice(alpha) for _ in range(rnd.randrange(0, 10))) for _ in range(4000)]
    subs += [b'\n', b' \n', b'a\n', b'a\n\n', b'x \n']
    bad = 0
    print('  %-14s %-22s %-6s %s' % ('X', 'mark_prio', 'nl_last', 'answers vs libpcre2 (T / M1 / M0)'))
    for name, X in B_CASES:
        facts = make_facts(X)
        code = pcre2.Code(text(C(X, ('anch', '$')))[0])
        dt = d1 = d0 = 0
        for s in subs:
            m = code.match(s, 0)
            want = None if m is None else m[0]
            t, m1, m0 = strategies(X, s, facts, Count(), Count(), Count())
            dt += t != want; d1 += m1 != want; d0 += m0 != want
            if (t != want or m1 != want or m0 != want) and bad < 6:
                bad += 1
                print('   B-DIFF', name, s, want, t, m1, m0)
        print('  %-14s %-22s %-6s %d / %d / %d wrong of %d' % (name, str(facts[6]), facts[7], dt, d1, d0, len(subs)))
    # the cost cells: compound.md B.5's shapes
    print('  cost cells (subject-byte loads, search from 0; ratio = strategy / one pass of k):')
    cells = [('ws-greedy', b'Q' + b'\t' * k + b'\n'),
             ('ws-lazy', b'q' + b' ' * k + b'\n'),
             ('ws-greedy', b'Q' + b'\t' * k),
             ('digits', b'x' * 10 + b'1' * k + b'\n'),
             ('mixed-prio', b'Q' + b'x' + b' ' * k + b'\n'),
             ('txt', b'Q ' + b'a' * k + b'.txt\n')]
    rows = []
    for name, s in cells:
        X = dict(B_CASES)[name]
        facts = make_facts(X)
        code = pcre2.Code(text(C(X, ('anch', '$')))[0])
        ct, c1, c0 = Count(), Count(), Count()
        t, m1, m0 = strategies(X, s, facts, ct, c1, c0)
        m = code.match(s, 0)
        want = None if m is None else m[0]
        ok = (t == want and m1 == want and m0 == want)
        rows.append((name, len(s), ct.loads, c1.loads, c0.loads, ok, facts[6][0]))
        print('   %-11s n=%-6d T=%-6d (%.2fx)  M1=%-6d (%.2fx)  M0=%-6d (%.2fx)  prio=%-15s answers=%s'
              % (name, len(s), ct.loads, ct.loads / k, c1.loads, c1.loads / k, c0.loads, c0.loads / k,
                 facts[6][0], 'ok' if ok else 'WRONG'))
    return bad


def rev_states(nfa, start, tagged, n_is_end=True, cap=50000):
    """Reachable reverse subset states (the walk's DFA), seeded at the
    subject end; threads keep their mark distance when tagged."""
    alphabet = sorted({b for node in nfa.n if node[0] == 'chr' for b in node[1]})
    classes = {}
    for b in range(256):
        sig = tuple(b in node[1] for node in nfa.n if node[0] == 'chr')
        classes.setdefault(sig, b)
    reps = list(classes.values())

    def close(items, at_end, depth):
        out, seen, stack = [], set(), list(reversed(items))
        while stack:
            st, d = stack.pop()
            key = (st, d if tagged else None)
            if key in seen:
                continue
            seen.add(key)
            node = nfa.n[st]
            if node[0] == 'split':
                for tg in reversed(node[1]):
                    stack.append((tg, d))
            elif node[0] == 'mark':
                stack.append((node[1], depth))
            elif node[0] == 'end':
                if at_end:
                    stack.append((node[1], d))
            else:
                out.append((st, d if tagged else None))
        return tuple(out)
    init = close([(start, None)], True, 0)
    seen, frontier = {init}, [(init, 0)]
    while frontier:
        state, depth = frontier.pop()
        if len(seen) > cap:
            return -1
        for c in reps:
            nxt = [(nfa.n[st][2], d) for st, d in state if nfa.n[st][0] == 'chr' and c in nfa.n[st][1]]
            if not nxt:
                continue
            ns = close(nxt, False, min(depth + 1, 2))
            if ns not in seen:
                seen.add(ns)
                frontier.append((ns, min(depth + 1, 2)))
    return len(seen)


def part_c():
    print('C reverse machine size (reachable subset states; tags = mark distance carried)')
    print('  %-14s %8s %14s %12s' % ('X', 'rev(X)', 'mark untagged', 'mark tagged'))
    extra = [('word', R(L('\\w'), 1, None)), ('num-dot', C(R(L('\\d'), 1, None), L('\\.'), R(L('\\d'), 1, 3))),
             ('kv', C(R(L('[a-z]'), 1, None), L('='), R(L('[^\\n]'), 0, None)))]
    for name, X in B_CASES + extra:
        try:
            xr, xs = compile_nfa(X, rev=True)
            lr, ls = compile_nfa(lower(C(X, ('anch', '$'))), rev=True)
        except Exception as e:
            print('  %-14s skipped (%s)' % (name, e)); continue
        print('  %-14s %8d %14d %12d' % (name, rev_states(xr, xs, False), rev_states(lr, ls, False),
                                          rev_states(lr, ls, True)))


if __name__ == '__main__':
    k = 16000
    if '--k' in sys.argv:
        k = int(sys.argv[sys.argv.index('--k') + 1])
    print('# libpcre2', pcre2.version())
    a = part_a()
    b = part_b(k)
    part_c()
    print('# TOTAL A-diffs=%d B-diff-samples=%d' % (a, b))
