#!/usr/bin/env python3
"""docs/design/memfn/probes/vmlazy/vocab_resweep.py -- R-12 Q-R12-5's
VOCABULARY RE-SWEEP: every emitted-text literal under src/gen/ and src/enc/
that is NEW since the search vocabulary was born (R4a, the manifest's first
commit), listed with the loop/scan shapes it carries and whether any
tests/memfn/search_vocab.tsv line already sees it.

C17's static half can only see a search form some vocabulary line
recognises (integration.md §R4.3.4's stated limit). VMLAZY (found by M6's
scoping) and `$_valid_upto`'s ASCII skip (found by R-12's) were both found by
accident; this lists the population a third one would hide in, so a reader
classifies it once instead of waiting for the next accident.

A literal is a CANDIDATE when it holds a loop or a word-at-a-time load
(`while (`, `for (`, `do {`, `memcpy`, a 0x8080.. mask); every candidate is
printed with its file, definition, line, the vocabulary lines that match it
(none = unseen), and its first 160 characters. The classification (search
site or not) is the reader's and is recorded in the lane report.

Usage: python3 vocab_resweep.py BASE_REV [ROOT]
       python3 vocab_resweep.py --all [ROOT]   (every literal, no base: the
       population the manifest's birth census also read)
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(TREE, 'tests', 'memfn'))
import c17_lex  # noqa: E402

CAND = re.compile(r'while \(|for \(|do \{|memcpy|0x8080')


def vocab(root):
    out = []
    for ln in open(os.path.join(root, 'tests', 'memfn', 'search_vocab.tsv'), encoding='utf-8'):
        if ln.startswith('#') or not ln.strip():
            continue
        f = ln.rstrip('\n').split('\t')
        out.append((f[1], re.compile(f[2])))
    return out


def files(root):
    for d in ('src/gen', 'src/enc'):
        for fn in sorted(os.listdir(os.path.join(root, d))):
            if fn.endswith('.c'):
                yield os.path.join(d, fn)


def literals_at(rev, rel, scratch):
    r = subprocess.run(['git', '-C', TREE, 'show', '%s:%s' % (rev, rel)], capture_output=True)
    if r.returncode:
        return set()
    p = os.path.join(scratch, 'base_' + rel.replace('/', '_'))
    with open(p, 'wb') as fh:
        fh.write(r.stdout)
    return {t for _, _, t in c17_lex.literals_by_function(p)}


def main():
    base = sys.argv[1]
    root = sys.argv[2] if len(sys.argv) > 2 else TREE
    every = base == '--all'
    scratch = os.environ.get('TMPDIR') or os.path.join(TREE, 'build-emitsweep')
    os.makedirs(scratch, exist_ok=True)
    voc = vocab(root)
    n_new = n_cand = n_unseen = 0
    for rel in files(root):
        old = set() if every else literals_at(base, rel, scratch)
        for name, line, text in c17_lex.literals_by_function(os.path.join(root, rel)):
            if text in old:
                continue
            n_new += 1
            if not CAND.search(text):
                continue
            n_cand += 1
            seen = [lid for lid, rx in voc if rx.search(text)]
            n_unseen += not seen
            print('%s:%d\t%s\t%s\t%s' % (rel, line, name, ','.join(seen) or 'UNSEEN',
                                         text[:160].replace('\t', ' ')))
    print('# new literals %d, candidates %d, unseen by any vocabulary line %d (base %s)'
          % (n_new, n_cand, n_unseen, base))


if __name__ == '__main__':
    main()
