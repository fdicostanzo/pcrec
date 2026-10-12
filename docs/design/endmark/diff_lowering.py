#!/usr/bin/env python3
"""D164's LOWERING, checked against libpcre2 (the semantic oracle, D26).

For each generated pattern P carrying a path-final positive lookahead (or a
path-final `$`, `\\Z`, `(?m)$`), build the LOWERED pattern P' in PCRE2 syntax:
the lookahead `(?=Y)` at a path's end becomes `()Y`, where the EMPTY CAPTURE
GROUP `()` stands in for END_MARK (its offset is where the mark records group
0's end). `$`/`\\Z` become `()\\n?\\z`, `(?m)$` becomes `()(?:\\n|\\z)`; `\\z`
is left alone (its Y consumes nothing). Inside the region after a mark a
path-final lookahead lowers to its body with no second mark (`plain`).

Then, at EVERY start position of every subject over an exhaustive alphabet:
  - P matches iff P' matches;
  - same group-0 start;
  - P's group-0 end == the offset of the mark group P' set (or P''s group-0
    end where no mark was crossed on the winning path);
  - every capture of P equals its counterpart in P', where a capture that
    ENCLOSES a mark is read with its end replaced by the set mark's offset
    (the report-time close-at-mark rule, endmark.md §1.4);
  - find-all under pcrec's protocol (docs/spec/match_api.md §3.1.3, over the
    REPORTED spans) gives the same sequence.

Usage: python3 -I diff_lowering.py [--len N] [--jobs J] [--set NAME] > out.txt
"""
import itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcre2

# ---- a tiny pattern AST ------------------------------------------------------
# ('lit', text) ('cat', [..]) ('alt', [..]) ('rep', n, lo, hi|None, mode g/l/p)
# ('cap', n) ('atom', n) ('look', n, '='|'*'|'!') ('anch', '$'|'Z'|'z'|'m$')
# ('kreset',) ('mark',) ('ncg', n)  -- ncg: non-capturing group (?:...)

def L(t): return ('lit', t)
def C(*xs): return ('cat', list(xs))
def A(*xs): return ('alt', list(xs))
def R(n, lo, hi, mode='g'): return ('rep', n, lo, hi, mode)
def G(n): return ('cap', n)
def AT(n): return ('atom', n)
def LA(n, k='='): return ('look', n, k)


def render(n, out, groups, enclosing, marks):
    """Render to PCRE2 text; number capture groups in opening order. `groups`
    collects, per capture/mark in opening order, (kind, id(node), enclosing
    mark-ancestor flag placeholder)."""
    k = n[0]
    if k == 'lit':
        out.append(n[1])
    elif k == 'cat':
        for x in n[1]:
            wrap = x[0] == 'alt'
            if wrap: out.append('(?:')
            render(x, out, groups, enclosing, marks)
            if wrap: out.append(')')
    elif k == 'alt':
        for i, x in enumerate(n[1]):
            if i: out.append('|')
            render(x, out, groups, enclosing, marks)
    elif k == 'rep':
        _, x, lo, hi, mode = n
        atomic = x[0] == 'lit' and len(x[1]) == 1 or x[0] in ('cap', 'atom', 'ncg')
        if x[0] == 'lit' and x[1].startswith('[') and x[1].endswith(']') and x[1].count('[') == 1:
            atomic = True
        if x[0] == 'lit' and x[1] in ('\\n', '\\s', '\\d', '\\w', '.'):
            atomic = True
        if not atomic: out.append('(?:')
        render(x, out, groups, enclosing, marks)
        if not atomic: out.append(')')
        q = {(0, None): '*', (1, None): '+', (0, 1): '?'}.get((lo, hi))
        if q is None:
            q = '{%d,%s}' % (lo, '' if hi is None else hi) if lo != hi else '{%d}' % lo
        out.append(q + {'g': '', 'l': '?', 'p': '+'}[mode])
    elif k == 'cap':
        groups.append(['cap', id(n), list(enclosing)])
        me = len(groups) - 1
        out.append('(')
        enclosing.append(me)
        render(n[1], out, groups, enclosing, marks)
        enclosing.pop()
        out.append(')')
    elif k == 'ncg':
        out.append('(?:'); render(n[1], out, groups, enclosing, marks); out.append(')')
    elif k == 'atom':
        out.append('(?>'); render(n[1], out, groups, enclosing, marks); out.append(')')
    elif k == 'look':
        out.append('(?' + n[2]); render(n[1], out, groups, enclosing, marks); out.append(')')
    elif k == 'anch':
        out.append({'$': '$', 'Z': '\\Z', 'z': '\\z', 'm$': '$'}[n[1]])
    elif k == 'kreset':
        out.append('\\K')
    elif k == 'mark':
        groups.append(['mark', id(n), list(enclosing)])
        marks.append(len(groups) - 1)
        out.append('()')
    else:
        raise ValueError(k)


def text(n):
    out, groups, marks = [], [], []
    render(n, out, groups, [], marks)
    return ''.join(out), groups, marks


TAIL_NL = C(R(L('\\n'), 0, 1), ('anch', 'z'))
TAIL_ML = ('ncg', A(L('\\n'), ('anch', 'z')))


PLANT = os.environ.get('PLANT', '')


def lower(n, plain=False):
    """D164: the lowering of path-final positive lookaheads. `plain` is the
    region after a mark, where a path-final lookahead becomes its body.
    PLANT=<name> applies one deliberately WRONG variant (the controls)."""
    k = n[0]
    if k == 'cat':
        if PLANT == 'lower-nontail':
            return ('cat', [lower(x, plain) for x in n[1]])
        return ('cat', n[1][:-1] + [lower(n[1][-1], plain)])
    if k == 'alt':
        return ('alt', [lower(x, plain) for x in n[1]])
    if k in ('cap', 'atom', 'ncg'):
        return (k, lower(n[1], plain))
    if k == 'rep' and (n[3] == 1 or PLANT == 'through-rep'):
        return ('rep', lower(n[1], plain), n[2], n[3], n[4])
    if k == 'look' and (n[2] in ('=', '*') or PLANT == 'lower-negative'):
        body = lower(n[1], True)
        return body if plain else C(('mark',), ('ncg', body))
    if k == 'anch' and n[1] in ('$', 'Z', 'm$'):
        body = TAIL_ML if n[1] == 'm$' else TAIL_NL
        return body if plain else C(('mark',), body)
    return n


def caps_of(groups):
    return [i for i, g in enumerate(groups) if g[0] == 'cap']


# ---- the comparison ------------------------------------------------------------

def reported(m, groups_l, marks_l):
    """(start, end) of the lowered match as the mark reports it."""
    s, e = m[0]
    if PLANT == 'consumed-end':
        return s, e, None
    for gi in marks_l:
        a, b = m[gi + 1]
        if a >= 0:
            return s, a, gi
    return s, e, None


def next_pos_utf(subj, p, utf):
    p += 1
    if utf:
        while p < len(subj) and (subj[p] & 0xC0) == 0x80:
            p += 1
    return p


def findall(fn, subj, utf):
    out, p, n = [], 0, len(subj)
    while p <= n:
        r = fn(p)
        if r is None:
            break
        s, e = r
        out.append((s, e))
        p = next_pos_utf(subj, e - 1, utf) if e > s else next_pos_utf(subj, s, utf)
    return out


def check(orig, low, subjects, utf, extra):
    t0, g0, _ = text(orig)
    t1, g1, m1 = text(low)
    O = pcre2.Code(t0, utf, extra)
    Lc = pcre2.Code(t1, utf, extra)
    # capture correspondence: the i-th 'cap' of the original is the i-th 'cap'
    # of the lowered tree (the lowering never adds or reorders captures).
    co, cl = caps_of(g0), caps_of(g1)
    assert len(co) == len(cl), (t0, t1)
    mark_set = set(m1)
    enclosing = [any(mi in mark_set and gi in g1[mi][2] for mi in m1) for gi in cl]
    bad = []
    cells = 0
    for subj in subjects:
        starts = range(len(subj) + 1)
        if utf:
            starts = [p for p in starts if p == len(subj) or (subj[p] & 0xC0) != 0x80]
        for p in starts:
            cells += 1
            a = O.match(subj, p)
            b = Lc.match(subj, p)
            if (a is None) != (b is None):
                bad.append((subj, p, 'exists', a, b)); continue
            if a is None:
                continue
            s, e, mg = reported(b, g1, m1)
            if (s, e) != a[0]:
                bad.append((subj, p, 'group0', a[0], (s, e))); continue
            for i, (go, gl) in enumerate(zip(co, cl)):
                want = a[go + 1]
                got = b[gl + 1]
                if PLANT != 'no-close-at-mark' and enclosing[i] and mg is not None and got[0] >= 0 and gl in g1[mg][2]:
                    got = (got[0], s if False else b[mg + 1][0])
                if want != got:
                    bad.append((subj, p, 'cap%d' % (i + 1), want, got)); break
        fo = findall(lambda q: (lambda m: None if m is None else m[0])(O.match(subj, q)), subj, utf)
        if PLANT == 'findall-consumed':
            fl = findall(lambda q: (lambda m: None if m is None else m[0])(Lc.match(subj, q)), subj, utf)
            fl = [(s0, e0) for s0, e0 in fl]
            fr = []
            p = 0
            while p <= len(subj):
                m = Lc.match(subj, p)
                if m is None: break
                rs, re_, _ = reported(m, g1, m1)
                fr.append((rs, re_))
                p = next_pos_utf(subj, m[0][1] - 1, utf) if m[0][1] > rs else next_pos_utf(subj, rs, utf)
            fl = fr
        else:
            fl = findall(lambda q: (lambda m: None if m is None else reported(m, g1, m1)[:2])(Lc.match(subj, q)), subj, utf)
        if fo != fl:
            bad.append((subj, -1, 'findall', fo, fl))
    return t0, t1, cells, bad


# ---- the generated families ----------------------------------------------------

XS = [L(''), L('a'), R(L('a'), 1, None), R(L('a'), 1, None, 'l'), R(L('a'), 1, None, 'p'),
      AT(R(L('a'), 1, None)), R(L('a'), 0, None), R(L('a'), 0, None, 'l'),
      A(L('ab'), L('a')), A(L('a'), L('ab')), R(G(L('a')), 1, None),
      R(L('a'), 1, 3), R(L('[ab]'), 0, None), R(C(L('a'), R(G(L('b')), 0, 1)), 1, None),
      R(L('[abc]'), 0, None, 'l'), R(L('\\s'), 1, None), R(L('\\s'), 0, None, 'l')]
YS = [L('b'), L('bc'), A(L('b'), L('bc')), A(L('bc'), L('b')), G(L('b')),
      C(G(L('b')), R(G(L('c')), 0, 1)), C(R(L('b'), 0, None), L('c')), R(L('[bc]'), 1, 2),
      L('a'), L('ab'), C(L('b'), LA(L('c'))), C(L('b'), LA(L('c'), '!')),
      C(L('b'), ('anch', '$')), A(L('b'), C(R(L('\\n'), 0, 1), ('anch', 'z'))),
      C(G(R(L('a'), 0, None)), L('b')), R(L('\\n'), 1, 2)]


def wrappers(X, Y):
    la = LA(Y)
    yield 'X(?=Y)', C(X, la)
    yield 'X(?*Y)', C(X, LA(Y, '*'))
    yield '(X(?=Y))', G(C(X, la))
    yield '(?:X(?=Y))?', R(('ncg', C(X, la)), 0, 1)
    yield '(?:X(?=Y))??', R(('ncg', C(X, la)), 0, 1, 'l')
    yield 'X(?=Y)|ab', A(C(X, la), L('ab'))
    yield 'b|X(?=Y)', A(L('b'), C(X, la))
    yield '(X(?=Y)|a)c?', (G(A(C(X, la), L('a'))), 'c?')   # NOT path-final: must stay
    yield '(X(?=Y)|c)', G(A(C(X, la), L('c')))
    yield '(?>X(?=Y))', AT(C(X, la))
    yield '(?:a\\K)?X(?=Y)', C(R(('ncg', C(L('a'), ('kreset',))), 0, 1), X, la)
    yield 'c?(X)(?=Y)', C(R(L('c'), 0, 1), G(X), la)


def anchor_family():
    for X in XS:
        for a in ('$', 'Z', 'm$', 'z'):
            yield ('anch-' + a, C(X, ('anch', a)), a == 'm$')
            yield ('anch-cap-' + a, G(C(X, ('anch', a))), a == 'm$')
            yield ('anch-alt-' + a, A(C(X, ('anch', a)), L('ab')), a == 'm$')
        yield ('mix', A(C(X, ('anch', '$')), C(L('b'), ('anch', 'z'))), False)
        yield ('look-then-$', C(X, LA(C(L('b'), ('anch', '$')))), False)


CURATED = [
    # find-all: consumed context past the reported end must not move next_pos
    ('fa-aa', C(L('a'), LA(L('aa')))),
    ('fa-empty', LA(L('ab'))),
    ('fa-empty2', LA(R(L('a'), 1, 2))),
    ('kreset-mark', C(L('a'), ('kreset',), L('b'), LA(L('c')))),
    ('nested-tail', C(L('a'), LA(C(L('b'), LA(L('c')))))),
    ('nested-mid', C(L('a'), LA(C(LA(L('bc')), L('b'))))),
    ('cap-in-look-alt', C(L('a'), LA(A(G(L('b')), G(L('bc')))))),
    ('cap-enclose-alt', G(A(C(L('a'), LA(L('bc'))), C(L('ab'), LA(L('c')))))),
    ('cap-nest2', G(C(L('a'), G(C(R(L('b'), 0, None), LA(L('c'))))))),
    ('greedy-var', C(R(L('a'), 1, None), LA(C(R(L('a'), 0, 1), L('b'))))),
    ('lazy-var', C(R(L('a'), 1, None, 'l'), LA(C(R(L('a'), 0, 1), L('b'))))),
    ('poss-q', R(('ncg', C(L('a'), LA(L('b')))), 0, 1, 'p')),
    ('neg-tail', C(L('a'), LA(L('b'), '!'))),          # control: does NOT lower
    ('look-only-ws', C(R(L('\\s'), 1, None), ('anch', '$'))),
    ('lazy-ws', C(R(L('\\s'), 0, None, 'l'), ('anch', '$'))),
    ('tie', A(L('q'), C(L('a'), ('anch', '$')), C(L('a\\n'), ('anch', '$')))),
    # NOT path-final (the lowering must leave them alone; the plants must not)
    ('nontail-b', C(L('a'), LA(L('b')), L('b'))),
    ('nontail-c', C(G(A(C(L('a'), LA(L('b'))), L('a'))), R(L('c'), 0, 1))),
    ('loop-plus', R(('ncg', C(L('a'), LA(L('a')))), 1, None)),
    ('loop-02', R(('ncg', C(L('a'), LA(L('ab')))), 0, 2)),
    ('dollar-mid', C(L('a'), ('anch', '$'), R(L('\\n'), 0, 1))),
]


def run_one(args):
    name, orig, utf, extra, subjects = args
    low = lower(orig)
    t0, t1, cells, bad = check(orig, low, subjects, utf, extra)
    return name, t0, t1, cells, bad


def subjects_over(alpha, maxlen):
    out = []
    for n in range(maxlen + 1):
        for t in itertools.product(alpha, repeat=n):
            out.append(b''.join(t))
    return out


def main():
    import argparse, multiprocessing as mp
    ap = argparse.ArgumentParser()
    ap.add_argument('--len', type=int, default=5)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--set', default='all')
    a = ap.parse_args()
    byte_subj = subjects_over([b'a', b'b', b'c', b'\n'], a.len)
    utf_subj = subjects_over([b'a', 'é'.encode(), b'b', b'\n'], max(3, a.len - 1))
    jobs = []
    if a.set in ('all', 'gen'):
        for xi, X in enumerate(XS):
            for yi, Y in enumerate(YS):
                for wn, w in wrappers(X, Y):
                    if isinstance(w, tuple) and len(w) == 2 and isinstance(w[1], str):
                        w = C(w[0], R(L('c'), 0, 1))
                    jobs.append(('gen x%d y%d %s' % (xi, yi, wn), w, False, 0, byte_subj))
    if a.set in ('all', 'anch'):
        for nm, p, ml in anchor_family():
            jobs.append((nm, p, False, pcre2.MULTILINE if ml else 0, byte_subj))
    if a.set in ('all', 'cur'):
        for nm, p in CURATED:
            jobs.append(('cur ' + nm, p, False, 0, subjects_over([b'a', b'b', b'c', b'\n', b'q', b' '], 5)))
    if a.set in ('all', 'utf'):
        for nm, p in [('utf-look', C(R(L('[aé]'), 1, None), LA(L('é')))),
                      ('utf-look2', C(L('a'), LA(C(L('é'), R(L('b'), 0, 1))))),
                      ('utf-dollar', C(R(L('[aé]'), 0, None), ('anch', '$'))),
                      ('utf-lazy-dollar', C(R(L('.'), 0, None, 'l'), ('anch', '$')))]:
            jobs.append(('utf ' + nm, p, True, 0, utf_subj))
    print('# libpcre2 %s; byte subjects %d (len<=%d), utf subjects %d; patterns %d'
          % (pcre2.version(), len(byte_subj), a.len, len(utf_subj), len(jobs)))
    tot_cells = tot_bad = 0
    with mp.Pool(a.jobs) as pool:
        for name, t0, t1, cells, bad in pool.imap(run_one, jobs, chunksize=4):
            tot_cells += cells
            tot_bad += len(bad)
            print('%s\t%s\t%s\tcells=%d\tdiff=%d' % (name, t0, t1, cells, len(bad)))
            for b in bad[:3]:
                print('   DIFF', b)
    print('# TOTAL patterns=%d cells=%d differences=%d' % (len(jobs), tot_cells, tot_bad))


if __name__ == '__main__':
    main()
