#!/usr/bin/env python3
"""tests/memfn/stamp_mover_census.py -- the R4a' MOVER CENSUS: every artifact
moves by EXACTLY the two kit stamp lines (and, after the bump, the abi
digit), checked rather than eyeballed ([MEMFN] R4a'; memfn/docs/requests.md
R-3 part 2; docs/dev/lanes/memfnstamp_report.md).

It drives scripts/emit_sweep.py's own machinery (the reference build from
`git archive REF`, the corpus enumeration, the argv/composition/IR streams)
and replaces its identical-or-mover verdict with a CLASSIFIER, per artifact:

  identical   the bytes did not move (expected for the --emit-ir listings and
              for composition headers, which carry no stamps; never for a .c)
  abi         no stamp line, and only the abi digit moved (--abi OLD:NEW;
              a header or listing at the bump step; never for a .c)
  stamps      the new text, with its `#define <UP>_MEMFN_FORMS "..."` and
              `#define <UP>_MEMFN_LIBC "..."` lines removed, equals the old
              text byte for byte, and those two lines are exactly two,
              adjacent, in that order, directly after the `<UP>_RUN_WORDS`
              line
  stamps+abi  the same, after which every remaining differing line becomes
              the old line when the new abi number is read as the old one
              (--abi OLD:NEW; the bump step's reading)
  OTHER       anything else: printed with its first hunk, and the run fails

Usage:
  python3 tests/memfn/stamp_mover_census.py --ref BASE [--abi OLD:NEW] [--jobs N]
The working side is this tree's build/pcrec; scratch goes under
build-emitsweep/ (gitignored), as emit_sweep's does.
"""
import argparse
import concurrent.futures
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
import emit_sweep as es  # noqa: E402

STAMP = re.compile(rb'^#define (\w+)_MEMFN_(FORMS|LIBC) "[^"\n]*"$')
RUN_WORDS = re.compile(rb'^#define \w+_RUN_WORDS ')


def digit_only(ol, nl, abi):
    """True iff the two line lists differ only where reading the new abi
    number as the old one makes them equal."""
    if not abi or len(ol) != len(nl):
        return False
    o, n = abi
    pat = re.compile(rb'(?<![0-9])' + n + rb'(?![0-9])')
    return all(pat.sub(o, b) == a for a, b in zip(ol, nl) if a != b)


def classify(old, new, abi):
    if old == new:
        return 'identical', None
    nl = new.split(b'\n')
    at = [i for i, l in enumerate(nl) if STAMP.match(l)]
    if not at and digit_only(old.split(b'\n'), nl, abi):
        return 'abi', None
    if len(at) != 2 or at[1] != at[0] + 1:
        return 'OTHER', '%d stamp lines, not 2 adjacent' % len(at)
    kinds = [STAMP.match(nl[i]).group(2) for i in at]
    if kinds != [b'FORMS', b'LIBC'] or at[0] == 0 or not RUN_WORDS.match(nl[at[0] - 1]):
        return 'OTHER', 'stamp lines not FORMS, LIBC directly after RUN_WORDS'
    rest = nl[:at[0]] + nl[at[1] + 1:]
    ol = old.split(b'\n')
    if rest == ol:
        return 'stamps', None
    if digit_only(ol, rest, abi):
        return 'stamps+abi', None
    return 'OTHER', es.first_diff_hunk(old, b'\n'.join(rest))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', required=True)
    ap.add_argument('--abi', help='OLD:NEW, the bump step')
    ap.add_argument('--jobs', type=int, default=min(8, os.cpu_count() or 4))
    ap.add_argument('--timeout', type=int, default=60)
    a = ap.parse_args()
    abi = tuple(x.encode() for x in a.abi.split(':')) if a.abi else None

    out = os.path.join(TREE, 'build-emitsweep')
    os.makedirs(out, exist_ok=True)
    ref_bin, _ = es.build_from_rev(TREE, a.ref, out, es.resolve_cc(TREE), 'ref')
    tree_bin = os.path.join(TREE, 'build', 'pcrec')
    patterns = es.enumerate_corpus(tree_bin, TREE, 30)
    files = es.find_files(TREE, ('.rxt', '.rxtin'))
    print('== R4a\' mover census: ref %s vs %s; %d pattern rows, %d composition files =='
          % (a.ref, tree_bin, len(patterns), len(files)))

    table = {}
    others = []

    def tally(stream, key, ok_a, ok_b, c_a, c_b):
        row = table.setdefault(stream, {})
        if not ok_a and not ok_b:
            row['both-refuse'] = row.get('both-refuse', 0) + 1
            return
        if ok_a != ok_b:
            row['ASYMMETRIC'] = row.get('ASYMMETRIC', 0) + 1
            others.append((stream, key, 'one side refused'))
            return
        cls, why = classify(c_a, c_b, abi)
        row[cls] = row.get(cls, 0) + 1
        if cls == 'OTHER':
            others.append((stream, key, why))

    streams = [
        ('c-default', lambda b, p: es.compile_stream_c(b, p, a.timeout)),
        ('c-vm', lambda b, p: es.compile_stream_c(b, p, a.timeout, engine='vm')),
        ('emit-ir-vm', lambda b, p: es.compile_stream_ir(b, p, a.timeout)),
    ]
    for name, fn in streams:
        def one(item, fn=fn):
            f, kind, pat = item
            ok_a, c_a, _ = fn(ref_bin, pat)
            ok_b, c_b, _ = fn(tree_bin, pat)
            return '%s:%s:%r' % (f, kind, pat[:60]), ok_a, ok_b, c_a, c_b
        with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
            for key, ok_a, ok_b, c_a, c_b in ex.map(one, patterns):
                tally(name, key, ok_a, ok_b, c_a, c_b)
        print('  %s done' % name, flush=True)

    comp_root = os.path.join(out, 'stampcensus-comp')
    os.makedirs(comp_root, exist_ok=True)

    def comp(job):
        i, path = job
        rc_a, arts_a, _ = es.run_composition(ref_bin, path, comp_root, 'a%d' % i, 3 * a.timeout)
        rc_b, arts_b, _ = es.run_composition(tree_bin, path, comp_root, 'b%d' % i, 3 * a.timeout)
        return os.path.relpath(path, TREE), arts_a, arts_b

    with concurrent.futures.ThreadPoolExecutor(min(a.jobs, 6)) as ex:
        for rel, arts_a, arts_b in ex.map(comp, list(enumerate(files))):
            for fn in sorted(set(arts_a) | set(arts_b)):
                stream = 'comp-' + fn.rsplit('.', 1)[-1]
                tally(stream, '%s:%s' % (rel, fn), fn in arts_a, fn in arts_b,
                      arts_a.get(fn), arts_b.get(fn))
    es.run(['rm', '-rf', comp_root], 60)

    cols = ['identical', 'abi', 'stamps', 'stamps+abi', 'OTHER', 'ASYMMETRIC', 'both-refuse']
    print('\n| stream | ' + ' | '.join(cols) + ' |')
    print('|---|' + '---|' * len(cols))
    for s in sorted(table):
        print('| %s | %s |' % (s, ' | '.join(str(table[s].get(c, 0)) for c in cols)))
    bad = list(others)
    for s in ('c-default', 'c-vm', 'comp-c'):
        still = table.get(s, {}).get('identical', 0) + table.get(s, {}).get('abi', 0)
        if still:
            bad.append((s, '-', '%d .c artifact(s) without the two lines: a stamp-less artifact'
                        % still))
    for s in ('emit-ir-vm', 'comp-h'):
        moved = sum(v for k, v in table.get(s, {}).items()
                    if k not in ('identical', 'abi', 'both-refuse'))
        if moved:
            bad.append((s, '-', '%d listing/header(s) moved' % moved))
    for stream, key, why in bad[:30]:
        print('FAIL: %s %s: %s' % (stream, key, why))
    print('census: %s' % ('CLEAN' if not bad else '%d FAIL' % len(bad)))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
