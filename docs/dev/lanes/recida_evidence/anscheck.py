#!/usr/bin/env python3
"""anscheck.py PATFILE OUTDIR [pcrec args...]   (lane recida, [RECID-A] answer check)

For each pattern in PATFILE: build THIS tree's matcher (build/pcrec, with the extra args), run every
(subject, startpos) cell over a pattern-derived subject set and compare with libpcre2 through
tests/backrefs/bref_oracle.answer (the project's ctypes oracle: span AND every group span). On a
difference it also builds the pre-module reference matcher ($RECIDA_REF, a pcrec built from ac4917d)
and says whether THAT build agrees with libpcre2 on the same cells (REF-AGREES-WITH-ORACLE is the
regression shape; ref-also-differs is a pre-existing divergence).

Env: RECIDA_REF=/path/to/pcrec_ref (optional).  Exit 1 if any DIFF / MAIN-NOBUILD / LENGTH-MISMATCH.
Subjects: all strings of length <= 4 (<= 3 when the alphabet has 5 symbols) over up to 3 literal
letters taken from the pattern plus the symbols its escapes and anchors need (space, a digit, a
newline) plus one letter absent from the pattern; every startpos of every subject."""
import itertools, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
REF = os.environ.get('RECIDA_REF', '')
sys.path.insert(0, W + '/tests/backrefs')
import bref_oracle as BO
P = BO.P
patfile, outdir = sys.argv[1], sys.argv[2]
extra = sys.argv[3:]
os.makedirs(outdir, exist_ok=True)
pats = [l for l in open(patfile, encoding='utf-8', errors='surrogateescape').read().split('\n') if l]

def alphabet(p):
    q = re.sub(r'\\.', '', p)
    q = re.sub(r'\(\?<[A-Za-z_]\w*>|\(\?P?[<=!>:]|\(\?[\w^-]+[):]|\\k<\w+>', '', q)
    letters = []
    for c in q:
        if c.isalnum() and c.isascii() and c not in letters:
            letters.append(c)
    a = letters[:3]
    if 'a' not in a and len(a) < 3: a.append('a')
    if re.search(r'\(\?[a-z]*m|\\n|\$|\^', p): a.append('\n')
    if re.search(r'\\[sSwWbB]', p): a.append(' ')
    if re.search(r'\\[dD]', p): a.append('7')
    a.append('z' if 'z' not in a else 'q')
    return a

def subjects(a):
    out = ['']
    for n in range(1, (4 if len(a) <= 4 else 3) + 1):
        out += [''.join(t) for t in itertools.product(a, repeat=n)]
    return out

def build(pat, d, ref=False):
    os.makedirs(d, exist_ok=True)
    pb = pat.encode('utf-8', 'surrogateescape')
    if ref:
        cmd = [REF, '--features', 'all', '-p', 'rx', '-o', d + '/gen.c', '--', pb]
    else:
        cmd = [W + '/build/pcrec', '--features', 'all', '-p', 'rx'] + extra + ['-o', d + '/gen.c', '--pattern', pb]
    if subprocess.run(cmd, capture_output=True).returncode != 0: return None
    hdr = open(d + '/gen.h', encoding='utf-8', errors='replace').read()
    ncaps = int(re.search(r'#define RX_NCAPS\s+(\d+)', hdr).group(1))
    r = subprocess.run(['gcc', '-O0', '-w', '-I' + d, '-o', d + '/t', W + '/tests/backrefs/bref_batch.c', d + '/gen.c'], capture_output=True)
    return None if r.returncode != 0 else ncaps - 1

def run(d, cells):
    inp = ''.join('%s\t%d\n' % c for c in cells).encode()
    return subprocess.run([d + '/t'], input=inp, capture_output=True, timeout=300).stdout.decode().split('\n')[:-1]

tot = bad = compiles = skipped = 0
for idx, p in enumerate(pats):
    d = '%s/p%04d' % (outdir, idx)
    a = alphabet(p); subs = subjects(a)
    sd = d + '/subj'; os.makedirs(sd, exist_ok=True)
    cells = []
    for i, s in enumerate(subs):
        fn = '%s/s%04d' % (sd, i)
        open(fn, 'wb').write(s.encode('latin-1'))
        cells += [(fn, sp) for sp in range(len(s) + 1)]
    try:
        rx = P.Compiled(p)
    except Exception:
        print('ORACLE-REFUSES\t%s' % p); skipped += 1; continue
    ng = build(p, d); compiles += 1
    if ng is None:
        print('MAIN-NOBUILD\t%s' % p); bad += 1; continue
    mine = run(d, cells)
    theirs = [BO.answer(rx, s, sp, ng) for s in subs for sp in range(len(s) + 1)]
    if len(mine) != len(theirs):
        print('LENGTH-MISMATCH\t%s' % p); bad += 1; continue
    tot += len(cells)
    diffs = [(c, m, t) for c, m, t in zip(cells, mine, theirs) if m != t]
    if not diffs:
        print('OK\t%s\tcells=%d\talphabet=%r' % (p, len(cells), ''.join(a))); continue
    refstat = 'ref-unavailable'
    if REF:
        ng2 = build(p, d + '/ref', ref=True); compiles += 1
        refstat = 'ref-noaccept'
        if ng2 is not None:
            rd = sum(1 for r_, t in zip(run(d + '/ref', cells), theirs) if r_ != t)
            refstat = 'ref-also-differs(%d)' % rd if rd else 'REF-AGREES-WITH-ORACLE'
    c, m, t = diffs[0]
    print('DIFF\t%s\tcells=%d/%d\t%s\tfirst: subj=%r sp=%d mine=%r oracle=%r' % (
        p, len(diffs), len(cells), refstat, open(c[0], 'rb').read().decode('latin-1'), c[1], m, t))
    bad += 1
print('SUMMARY patterns=%d diff=%d oracle-refused=%d cells=%d gcc-compiles=%d' % (len(pats), bad, skipped, tot, compiles))
sys.exit(1 if bad else 0)
