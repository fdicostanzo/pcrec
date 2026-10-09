#!/usr/bin/env python3
"""docs/design/memfn/probes/r4e0b/routing_census.py -- R4e'.0b's G1 CENSUS
(integration.md §R4.9.2.6; memfn/docs/requests.md R-11; D155 item 6;
docs/dev/lanes/r4e0b_report.md).

The routing moves every offset-skip/pre-check function's loop, byte for
byte, under `<fn>__body` and makes `<fn>` one call to it. This census checks
that claim on pcrec's artifacts, from pcrec's side (never the kit's `moved`):

1. MOVERS BY ID. Per artifact, a class:
     identical  the bytes did not move;
     abi        only the abi number moved (--abi OLD:NEW), and the PARENT
                artifact holds no function;
     routed     the UN-DONE text (every `<fn>(...) { return <fn>__body(...); }`
                selector removed, every `<fn>__body(` head renamed back to
                `<fn>(`) equals the parent byte for byte (the abi number
                read back), and the selectors removed number exactly the
                functions the PARENT text defines;
     OTHER      anything else; printed with its first hunk; the run fails.
   The control is independent of the routing: the parent's own function
   count, read off the PARENT text by its head (`static inline size_t
   <name>_{reqrun,reqrun_whole,ofsskip}(const unsigned char *subject, ...`).
   A parent artifact holding a function that did not route, or one holding
   none that moved beyond the abi digit, is a failure.
2. THE BYTES. Per routed function, the delta 121 + 2 x len(name) plus each
   table parameter declared once more and passed once (+139 for
   `rx_reqrun`), checked against the measured delta of the whole artifact.
3. ASSEMBLY (--asm). Every routed mover of the argv streams is written
   parent/routed into two directories under ONE basename (rx.c/rx.h: the -o
   basename trap) and compiled `-S` at each --recipe; the two `.s` are
   compared after renumbering gcc's local labels (.LFB/.LFE/.L<n>/.LC<n>, by
   first appearance) and reading `<fn>__body` as `<fn>`. Each non-identical
   mover is listed with its first hunk. -Os and -O0 may be added as
   reported-only recipes (--report-recipe), which never fail the run.

K35: every stream's routed population and every customer (reqrun,
reqrun_whole, ofsskip) must be non-empty, and the routed total at least
--floor.

Usage:
  python3 docs/design/memfn/probes/r4e0b/routing_census.py --ref PARENT \\
      --abi 68:70 [--every N] [--asm] [--jobs N] [--out DIR]
The working side is this tree's build/pcrec; scratch goes under
build-emitsweep/ (gitignored), as emit_sweep's does.
"""
import argparse
import concurrent.futures
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
import emit_sweep as es  # noqa: E402

CUSTOMERS = (b'reqrun_whole', b'reqrun', b'ofsskip')
# the PARENT's function head: the independent control (never the selector)
FN_HEAD = re.compile(rb'^static inline size_t (\w+_(?:reqrun_whole|reqrun|ofsskip))'
                     rb'\(const unsigned char \*subject, size_t n, size_t pos((?:, const unsigned char \*\w+)*)\)$',
                     re.M)
# the routed selector, written whole by the seam (ofsskip.c fn_selector)
SELECTOR = re.compile(rb'static inline size_t (\w+)\(const unsigned char \*subject, size_t n, size_t pos'
                      rb'((?:, const unsigned char \*\w+)*)\)\n\{\n'
                      rb'    return (\w+)\(subject, n, pos((?:, \w+)*)\);\n\}\n\n')


def digit_only(old, new, abi):
    """True iff the two texts differ only on lines where reading the new abi
    number as the old one makes them equal (line by line, so a table byte
    that happens to spell the number elsewhere is never rewritten)."""
    ol, nl = old.split(b'\n'), new.split(b'\n')
    if not abi or len(ol) != len(nl):
        return False
    o, n = abi
    pat = re.compile(rb'(?<![0-9])' + n + rb'(?![0-9])')
    return all(pat.sub(o, b) == a for a, b in zip(ol, nl) if a != b)


def undo(new):
    """(text, [(name, tables)]) with every routed selector removed and every
    helper head renamed back, or (None, why)."""
    found = []
    out = bytearray()
    at = 0
    for m in SELECTOR.finditer(new):
        name, tparams, callee, targs = m.group(1), m.group(2), m.group(3), m.group(4)
        if callee != name + b'__body':
            return None, 'selector %s calls %s' % (name.decode(), callee.decode())
        tnames = re.findall(rb'\*(\w+)', tparams)
        if [b', ' + t for t in tnames] != re.findall(rb', \w+', targs):
            return None, 'selector %s does not forward its tables in order' % name.decode()
        head = (b'static inline size_t ' + name + b'__body(const unsigned char *subject, size_t n, size_t pos'
                + tparams + b')\n{\n')
        # the helper must sit directly above its selector (the seam's order)
        h = new.rfind(head, at, m.start())
        if h < 0 or new.find(b'\n}\n\n', h, m.start()) < 0:
            return None, 'selector %s has no helper above it' % name.decode()
        out += new[at:m.start()]
        at = m.end()
        found.append((name, tnames))
    out += new[at:]
    text = bytes(out)
    for name, _ in found:
        text = text.replace(b'static inline size_t ' + name + b'__body(',
                            b'static inline size_t ' + name + b'(', 1)
    if b'__body' in text:
        return None, 'a `__body` survives the un-doing'
    return text, found


def predicted_delta(found):
    d = 0
    for name, tables in found:
        d += 121 + 2 * len(name)
        for t in tables:
            d += len(b', const unsigned char *' + t) + len(b', ' + t)
    return d


def customer(name):
    for c in CUSTOMERS:
        if name.endswith(b'_' + c):
            return c.decode()
    return '?'


def classify(old, new, abi):
    """(class, why, found)"""
    parent_fns = FN_HEAD.findall(old)
    unrouted = 'OTHER', '%d function(s) in the parent did not route' % len(parent_fns), []
    if old == new or digit_only(old, new, abi):
        if parent_fns:
            return unrouted
        return ('identical' if old == new else 'abi'), None, []
    text, found = undo(new)
    if text is None:
        return 'OTHER', found, []
    if text != old and not digit_only(old, text, abi):
        return 'OTHER', es.first_diff_hunk(old, text), found
    if sorted(n for n, _ in parent_fns) != sorted(n for n, _ in found):
        return 'OTHER', 'parent defines %s, %d selector(s) removed' % (
            [n.decode() for n, _ in parent_fns], len(found)), found
    if len(new) - len(old) != predicted_delta(found):
        return 'OTHER', 'delta %d, predicted %d' % (len(new) - len(old), predicted_delta(found)), found
    return 'routed', None, found


# ---- assembly --------------------------------------------------------------

LABEL = re.compile(rb'\.(LFB|LFE|LVL|LBB|LBE|LC|L)(\d+)\b')


def norm_asm(s, names):
    for n in names:
        s = s.replace(n + b'__body', n)
    seen = {}

    def sub(m):
        k = (m.group(1), m.group(2))
        if k not in seen:
            seen[k] = sum(1 for kk in seen if kk[0] == m.group(1))
        return b'.' + m.group(1) + str(seen[k]).encode()
    return LABEL.sub(sub, s)


def asm_of(cc, d, recipe, timeout):
    rc, out, err = es.run([cc] + recipe.split() + ['-S', 'rx.c', '-o', 'rx.s'], timeout, cwd=d)
    if rc != 0:
        return None, err[-400:]
    with open(os.path.join(d, 'rx.s'), 'rb') as fh:
        return fh.read(), None


def emit_pair(ref_bin, tree_bin, pat, argv_extra, root, tag, timeout, abi=None):
    dirs = []
    for side, b in (('a', ref_bin), ('b', tree_bin)):
        d = os.path.join(root, tag, side)
        os.makedirs(d, exist_ok=True)
        argv = [b, '-p', 'rx', '--features', 'all'] + argv_extra + ['-o', os.path.join(d, 'rx.c')]
        argv += es._pattern_argv(b, pat)
        rc, _, err = es.run(argv, timeout)
        if rc != 0:
            return None
        dirs.append(d)
    if abi:
        # the abi number is DATA in the object (rx_info.abi): read the
        # parent's as the new one on its abi-spelling lines only, so the
        # assembly comparison is about code
        o, n = abi
        pat = re.compile(rb'(?<![0-9])' + o + rb'(?![0-9])')
        for fn in ('rx.c', 'rx.h'):
            path = os.path.join(dirs[0], fn)
            with open(path, 'rb') as fh:
                lines = fh.read().split(b'\n')
            lines = [pat.sub(n, l) if re.search(rb'abi|ABI', l) else l for l in lines]
            with open(path, 'wb') as fh:
                fh.write(b'\n'.join(lines))
    return dirs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', required=True, help='the parent revision')
    ap.add_argument('--abi', help='OLD:NEW')
    ap.add_argument('--every', type=int, default=1, help='every Nth corpus row')
    ap.add_argument('--no-comp', action='store_true', help='skip the composition stream')
    ap.add_argument('--asm', action='store_true')
    ap.add_argument('--recipe', action='append', default=None,
                    help='a gating -S recipe (default: "-O2" and "-O2 -march=x86-64-v3")')
    ap.add_argument('--report-recipe', action='append', default=[],
                    help='a reported-only -S recipe ("-Os", "-O0")')
    ap.add_argument('--asm-every', type=int, default=1, help='every Nth routed mover')
    ap.add_argument('--floor', type=int, default=1)
    ap.add_argument('--nonid-out', help='write the non-identical assembly movers here (TSV)')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--timeout', type=int, default=60)
    a = ap.parse_args()
    recipes = a.recipe or ['-O2', '-O2 -march=x86-64-v3']
    abi = tuple(x.encode() for x in a.abi.split(':')) if a.abi else None

    out = os.path.join(TREE, 'build-emitsweep')
    os.makedirs(out, exist_ok=True)
    cc = es.resolve_cc(TREE)
    ref_bin, _ = es.build_from_rev(TREE, a.ref, out, cc, 'routing_ref')
    tree_bin = os.path.join(TREE, 'build', 'pcrec')
    patterns = es.enumerate_corpus(tree_bin, TREE, 30)[::a.every]
    files = [] if a.no_comp else es.find_files(TREE, ('.rxt', '.rxtin'))[::a.every]
    print("== R4e'.0b routing census: ref %s vs %s; %d pattern rows (every %d), %d composition files; cc %s =="
          % (a.ref, tree_bin, len(patterns), a.every, len(files), cc), flush=True)

    table, others, movers = {}, [], []
    by_customer, deltas = {}, {}

    def tally(stream, key, ok_a, ok_b, c_a, c_b, item=None):
        row = table.setdefault(stream, {})
        if not ok_a and not ok_b:
            row['both-refuse'] = row.get('both-refuse', 0) + 1
            return
        if ok_a != ok_b:
            row['ASYMMETRIC'] = row.get('ASYMMETRIC', 0) + 1
            others.append((stream, key, 'one side refused'))
            return
        cls, why, found = classify(c_a, c_b, abi)
        row[cls] = row.get(cls, 0) + 1
        if cls == 'OTHER':
            others.append((stream, key, why))
        if cls == 'routed':
            for name, tables in found:
                c = customer(name)
                by_customer.setdefault(stream, {})[c] = by_customer.setdefault(stream, {}).get(c, 0) + 1
                d = 121 + 2 * len(name) + sum(len(b', const unsigned char *' + t) + len(b', ' + t) for t in tables)
                deltas[(c, d)] = deltas.get((c, d), 0) + 1
            if item is not None:
                movers.append((stream, key, item, [n for n, _ in found]))

    streams = [
        ('c-default', [], lambda b, p: es.compile_stream_c(b, p, a.timeout)),
        ('c-vm', ['--engine=vm'], lambda b, p: es.compile_stream_c(b, p, a.timeout, engine='vm')),
        ('c-utf8', ['-e', 'utf8'], lambda b, p: es.compile_stream_c(b, p, a.timeout, extra=('-e', 'utf8'))),
        ('c-comments', ['-fcomments'], lambda b, p: es.compile_stream_c(b, p, a.timeout, extra=('-fcomments',))),
        ('emit-ir-vm', None, lambda b, p: es.compile_stream_ir(b, p, a.timeout)),
    ]
    for name, argv_extra, fn in streams:
        def one(item, fn=fn):
            f, kind, pat = item
            ok_a, c_a, _ = fn(ref_bin, pat)
            ok_b, c_b, _ = fn(tree_bin, pat)
            return item, '%s:%s:%r' % (f, kind, pat[:60]), ok_a, ok_b, c_a, c_b
        with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
            for item, key, ok_a, ok_b, c_a, c_b in ex.map(one, patterns):
                # c-comments' code is c-default's (comments compile to nothing),
                # so its movers are not re-assembled
                tally(name, key, ok_a, ok_b, c_a, c_b,
                      (item[2], argv_extra) if argv_extra is not None and name != 'c-comments' else None)
        print('  %s done' % name, flush=True)

    if files:
        comp_root = os.path.join(out, 'routingcensus-comp')
        os.makedirs(comp_root, exist_ok=True)

        def comp(job):
            i, path = job
            _, arts_a, _ = es.run_composition(ref_bin, path, comp_root, 'a%d' % i, 3 * a.timeout)
            _, arts_b, _ = es.run_composition(tree_bin, path, comp_root, 'b%d' % i, 3 * a.timeout)
            return os.path.relpath(path, TREE), arts_a, arts_b

        with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
            for rel, arts_a, arts_b in ex.map(comp, list(enumerate(files))):
                for fname in sorted(set(arts_a) | set(arts_b)):
                    stream = 'comp-' + fname.rsplit('.', 1)[-1]
                    tally(stream, '%s:%s' % (rel, fname), fname in arts_a, fname in arts_b,
                          arts_a.get(fname), arts_b.get(fname))
        shutil.rmtree(comp_root, ignore_errors=True)

    cols = ['identical', 'abi', 'routed', 'OTHER', 'ASYMMETRIC', 'both-refuse']
    print('\n| stream | ' + ' | '.join(cols) + ' |')
    print('|---|' + '---|' * len(cols))
    for s in sorted(table):
        print('| %s | %s |' % (s, ' | '.join(str(table[s].get(c, 0)) for c in cols)))
    print('\nrouted functions by customer:')
    for s in sorted(by_customer):
        print('  %s: %s' % (s, ', '.join('%s %d' % kv for kv in sorted(by_customer[s].items()))))
    print('per-function delta (customer, bytes): count')
    for (c, d), n in sorted(deltas.items()):
        print('  %s +%d: %d' % (c, d, n))

    bad = list(others)
    total = sum(t.get('routed', 0) for t in table.values())
    for s in ('c-default', 'c-vm', 'c-utf8', 'c-comments'):
        if not table.get(s, {}).get('routed'):
            bad.append((s, '-', 'no routed mover: the population is empty (K35)'))
    for c in ('reqrun', 'reqrun_whole', 'ofsskip'):
        if not any(c in v for v in by_customer.values()):
            bad.append(('*', c, 'no routed function of this customer (K35)'))
    for s in ('emit-ir-vm', 'comp-h'):
        moved = sum(v for k, v in table.get(s, {}).items() if k not in ('identical', 'abi', 'both-refuse'))
        if moved:
            bad.append((s, '-', '%d listing/header(s) moved beyond the abi digit' % moved))
    if total < a.floor:
        bad.append(('*', '-', 'routed total %d below the floor %d' % (total, a.floor)))

    if a.asm:
        root = os.path.join(out, 'routingcensus-asm')
        shutil.rmtree(root, ignore_errors=True)
        jobs = movers[::a.asm_every]
        print('\n== assembly: %d routed movers (every %d), recipes %s, reported-only %s =='
              % (len(jobs), a.asm_every, recipes, a.report_recipe), flush=True)
        asm_tab = {r: {} for r in recipes + a.report_recipe}
        asm_bad = []
        nonid = []

        def asm_job(job):
            i, (stream, key, (pat, argv_extra), names) = job
            dirs = emit_pair(ref_bin, tree_bin, pat, argv_extra, root, 'm%d' % i, a.timeout, abi)
            res = {}
            if dirs is None:
                return stream, key, None, None
            for r in recipes + a.report_recipe:
                sa, ea = asm_of(cc, dirs[0], r, 300)
                sb, eb = asm_of(cc, dirs[1], r, 300)
                if sa is None or sb is None:
                    res[r] = ('ERROR', (ea or eb or b'').decode(errors='replace'))
                    continue
                na, nb = norm_asm(sa, []), norm_asm(sb, names)
                if na == nb:
                    res[r] = ('identical', None)
                else:
                    # the same instructions in another order (gcc's block
                    # layout or scheduling), or other instructions: compare
                    # the instruction lines with every label read as one
                    ia = sorted(LABEL.sub(b'.L', l) for l in na.split(b'\n') if l.startswith(b'\t'))
                    ib = sorted(LABEL.sub(b'.L', l) for l in nb.split(b'\n') if l.startswith(b'\t'))
                    res[r] = ('DIFFERENT', '%s; %s' % (
                        'same instruction multiset (layout/order only)' if ia == ib else
                        'instructions differ: %d vs %d instruction lines' % (len(ia), len(ib)),
                        es.first_diff_hunk(na, nb)))
            shutil.rmtree(os.path.join(root, 'm%d' % i), ignore_errors=True)
            return stream, key, res, (pat, argv_extra)

        with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
            for stream, key, res, src in ex.map(asm_job, list(enumerate(jobs))):
                if res is None:
                    asm_bad.append(('*', stream, key, 'could not re-emit the pair'))
                    continue
                for r, (v, why) in res.items():
                    asm_tab[r][v] = asm_tab[r].get(v, 0) + 1
                    if v != 'identical':
                        asm_bad.append((r, stream, key, why))
                        nonid.append((stream, r, why.split(';')[0] if why else v, src))
        shutil.rmtree(root, ignore_errors=True)
        print('| recipe | identical | DIFFERENT | ERROR | gates |')
        print('|---|---|---|---|---|')
        for r in recipes + a.report_recipe:
            t = asm_tab[r]
            print('| `%s` | %d | %d | %d | %s |' % (r, t.get('identical', 0), t.get('DIFFERENT', 0),
                                                  t.get('ERROR', 0), 'yes' if r in recipes else 'reported'))
        for r, stream, key, why in asm_bad:
            print('ASM %s: %s %s %s: %s' % ('FAIL' if r in recipes or r == '*' else 'note', r, stream, key, why))
            if r in recipes or r == '*':
                bad.append(('asm ' + r, key, 'non-identical assembly'))
        if a.nonid_out:
            with open(a.nonid_out, 'w') as fh:
                fh.write('# stream\trecipe\tclass\tpattern (escape-encoded)\targv\n')
                for stream, r, cls, (pat, argv_extra) in nonid:
                    fh.write('%s\t%s\t%s\t%s\t%s\n' % (stream, r, cls, es.encode_escape(
                        pat.encode('utf-8', 'surrogateescape') if isinstance(pat, str) else pat),
                        ' '.join(argv_extra)))
        for r in recipes + a.report_recipe:
            mult = sum(1 for rr, _, _, w in asm_bad if rr == r and w.startswith('same instruction'))
            print('%s: of the DIFFERENT, %d have the same instruction multiset (layout/order only)'
                  % (r, mult))

    for stream, key, why in bad[:40]:
        print('FAIL: %s %s: %s' % (stream, key, why))
    print('census: %s (routed %d)' % ('CLEAN' if not bad else '%d FAIL' % len(bad), total))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
