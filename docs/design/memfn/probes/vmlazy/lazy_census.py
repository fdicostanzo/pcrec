#!/usr/bin/env python3
"""docs/design/memfn/probes/vmlazy/lazy_census.py -- R-12 VMLAZY NORMALIZE's G1
CENSUS (docs/dev/lanes/r12scope_report.md §1.5, §5.3;
docs/dev/lanes/vmlazy_report.md).

The NORMALIZE step re-spells the VM cursor rung's LAZY rmin prefix. The parent
(abi 70) wrote a counted loop that fails inside the loop:

        rx_span_cursor = scan_position;
        {
            unsigned long it_ = 0;
            while (it_ < KUL) {
                if (!(rx_span_cursor + W <= subject_length<TEST>)) goto rx_fail;
                rx_span_cursor += W; it_++;
            }
        }

and the normalized tree writes the kit's capped ADVANCE layout plus the rung's
reach test:

        {
            unsigned long it_ = 0;
            rx_span_cursor = scan_position;
            while ((rx_span_cursor + W <= subject_length) && it_ < KULL<TEST>) {
                rx_span_cursor += W;
                it_++;
            }
        }
        if ((ptrdiff_t)rx_span_cursor < slot_values[L] + K*W) goto rx_fail;

<TEST> is ` && (m0) && (m1) ...`, the same string in both (the member texts).
This census checks that claim from pcrec's side:

1. MOVERS BY ID. Per artifact, a class:
     identical  the bytes did not move;
     abi        only the abi number moved (--abi OLD:NEW) and the PARENT holds
                no lazy prefix;
     lazy       the UN-DONE text (every new block rewritten back to the old
                form, `RX_VM_PROGRAM_BYTES` read back by the measured block
                delta) equals the parent, the blocks un-done number exactly
                the prefixes the PARENT text holds (the independent control,
                read off the parent by the OLD form's own regex), and each
                reach test's offset is K*W;
     shape      as `lazy`, but `RX_VM_ENTRY_SHAPE` also moved (the entry-shape
                knee reads the program's length): listed by id, never a
                failure on its own, the un-done comparison then skips the
                entry functions (reported with its first hunk);
     OTHER      anything else; printed with its first hunk; the run fails.
2. ASSEMBLY (--asm). Every lazy/shape mover of the argv streams is written
   parent/new under ONE basename and compiled `-S` at each --recipe; the two
   `.s` are compared after renumbering gcc's local labels (routing_census's
   normalizer). Non-identical movers are listed (--nonid-out) for the timing
   step; they are not a failure of the census (the object code is EXPECTED to
   move: a loop-carried test becomes a post-loop test).

K35: the lazy population must be non-empty in every .c stream, and the lazy
total at least --floor.

Usage:
  python3 docs/design/memfn/probes/vmlazy/lazy_census.py --ref PARENT \\
      --abi 70:72 [--every N] [--asm] [--jobs N] [--nonid-out FILE]
The working side is this tree's build/pcrec; scratch goes under
build-emitsweep/ (gitignored), as emit_sweep's does.
"""
import argparse
import concurrent.futures
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
sys.path.insert(0, os.path.join(HERE, '..', 'r4e0b'))
import emit_sweep as es  # noqa: E402
import routing_census as rc  # noqa: E402  (norm_asm, asm_of, emit_pair, digit_only)

OLD = re.compile(rb'    rx_span_cursor = scan_position;\n    \{\n        unsigned long it_ = 0;\n'
                 rb'        while \(it_ < (\d+)UL\) \{\n'
                 rb'            if \(!\(rx_span_cursor \+ (\d+) <= subject_length(.*)\)\) goto rx_fail;\n'
                 rb'            rx_span_cursor \+= (\d+); it_\+\+;\n'
                 rb'        \}\n    \}\n')
NEW = re.compile(rb'    \{\n        unsigned long it_ = 0;\n        rx_span_cursor = scan_position;\n'
                 rb'        while \(\(rx_span_cursor \+ (\d+) <= subject_length\) && it_ < (\d+)ULL(.*)\) \{\n'
                 rb'            rx_span_cursor \+= (\d+);\n            it_\+\+;\n        \}\n    \}\n'
                 rb'    if \(\(ptrdiff_t\)rx_span_cursor < slot_values\[(\d+)\] \+ (\d+)\) goto rx_fail;\n')
PROG = re.compile(rb'^(#define RX_VM_PROGRAM_BYTES )(\d+)ULL$', re.M)
SHAPE = re.compile(rb'^#define RX_VM_ENTRY_SHAPE "(\w+)"$', re.M)


def undo(new):
    """(text, nblocks, delta) with every new-form block rewritten to the old
    form, or (None, why, 0)."""
    out, at, n, delta = bytearray(), 0, 0, 0
    for m in NEW.finditer(new):
        w, k, test, step, _low, off = m.groups()
        if step != w:
            return None, 'block steps %s at stride %s' % (step.decode(), w.decode()), 0
        if int(off) != int(k) * int(w):
            return None, 'reach test offset %s is not K*W = %d' % (off.decode(), int(k) * int(w)), 0
        old = (b'    rx_span_cursor = scan_position;\n    {\n        unsigned long it_ = 0;\n'
               b'        while (it_ < ' + k + b'UL) {\n'
               b'            if (!(rx_span_cursor + ' + w + b' <= subject_length' + test + b')) goto rx_fail;\n'
               b'            rx_span_cursor += ' + w + b'; it_++;\n        }\n    }\n')
        out += new[at:m.start()] + old
        at = m.end()
        n += 1
        delta += (m.end() - m.start()) - len(old)
    out += new[at:]
    return bytes(out), n, delta


def prog_bytes(text):
    m = PROG.search(text)
    return int(m.group(2)) if m else None


def classify(old, new, abi):
    """(class, why, nblocks)"""
    parent_n = len(OLD.findall(old))
    if old == new or rc.digit_only(old, new, abi):
        if parent_n:
            return 'OTHER', 'the parent holds %d lazy prefix(es) that did not move' % parent_n, 0
        return ('identical' if old == new else 'abi'), None, 0
    text, n, delta = undo(new)
    if text is None:
        return 'OTHER', n, 0
    if n != parent_n:
        return 'OTHER', 'parent holds %d lazy prefix(es), %d un-done' % (parent_n, n), n
    pa, pb = prog_bytes(old), prog_bytes(text)
    if pa is not None and pb is not None:
        if pb - pa != delta:
            return 'OTHER', 'RX_VM_PROGRAM_BYTES moved %d, blocks moved %d' % (pb - pa, delta), n
        text = PROG.sub(lambda m: m.group(1) + str(pa).encode() + b'ULL', text)
    if text == old or rc.digit_only(old, text, abi):
        return 'lazy', None, n
    sa, sb = SHAPE.search(old), SHAPE.search(new)
    if sa and sb and sa.group(1) != sb.group(1):
        return 'shape', '%s -> %s; %s' % (sa.group(1).decode(), sb.group(1).decode(),
                                         es.first_diff_hunk(old, text)), n
    return 'OTHER', es.first_diff_hunk(old, text), n


def controls(ref_bin, tree_bin, abi, timeout):
    """The census's failing direction: planted edits of one real mover that
    must each read OTHER (and the unplanted pair must read lazy)."""
    pat = '(a)(?:ab){2,}?ab'
    _, old, _ = es.compile_stream_c(ref_bin, pat, timeout, engine='vm')
    _, new, _ = es.compile_stream_c(tree_bin, pat, timeout, engine='vm')
    m = NEW.search(new)
    plants = [
        ('unplanted', new, 'lazy'),
        ('reach offset +1', new[:m.start(6)] + str(int(m.group(6)) + 1).encode() + new[m.end(6):], 'OTHER'),
        ('a member byte edited', new.replace(b'== 98)) {', b'== 99)) {', 1), 'OTHER'),
        ('the prefix left in the old form', old.replace(b'(abi 70)', b'(abi 72)'), 'OTHER'),
        ('a byte outside the prefix', new.replace(b'goto rx_L6;', b'goto rx_L6; ', 1), 'OTHER'),
        ('PROGRAM_BYTES off by one', PROG.sub(lambda x: x.group(1) + str(int(x.group(2)) + 1).encode() + b'ULL',
                                              new), 'OTHER'),
    ]
    bad = 0
    for name, text, want in plants:
        got = classify(old, text, abi)[0]
        print('control %-34s want %-6s got %s' % (name, want, got))
        bad += got != want
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', required=True, help='the parent revision')
    ap.add_argument('--abi', help='OLD:NEW')
    ap.add_argument('--every', type=int, default=1, help='every Nth corpus row')
    ap.add_argument('--asm', action='store_true')
    ap.add_argument('--recipe', action='append', default=None,
                    help='an -S recipe (default: "-O2" and "-O2 -march=x86-64-v3")')
    ap.add_argument('--floor', type=int, default=1)
    ap.add_argument('--nonid-out', help='write the non-identical assembly movers here (TSV)')
    ap.add_argument('--movers-out', help='write every lazy/shape mover here (TSV)')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--timeout', type=int, default=60)
    a = ap.parse_args()
    recipes = a.recipe or ['-O2', '-O2 -march=x86-64-v3']
    abi = tuple(x.encode() for x in a.abi.split(':')) if a.abi else None

    out = os.path.join(TREE, 'build-emitsweep')
    os.makedirs(out, exist_ok=True)
    cc = es.resolve_cc(TREE)
    ref_bin, _ = es.build_from_rev(TREE, a.ref, out, cc, 'vmlazy_ref')
    tree_bin = os.path.join(TREE, 'build', 'pcrec')
    nbad = controls(ref_bin, tree_bin, abi, a.timeout)
    if nbad:
        print('FAIL: %d planted control(s) did not read as planted' % nbad)
        return 1
    patterns = es.enumerate_corpus(tree_bin, TREE, 30)[::a.every]
    print('== R-12 VMLAZY census: ref %s vs %s; %d pattern rows (every %d); cc %s =='
          % (a.ref, tree_bin, len(patterns), a.every, cc), flush=True)

    table, others, movers, shapes = {}, [], [], []
    blocks = {}

    streams = [
        ('c-default', [], lambda b, p: es.compile_stream_c(b, p, a.timeout)),
        ('c-vm', ['--engine=vm'], lambda b, p: es.compile_stream_c(b, p, a.timeout, engine='vm')),
        ('c-utf8', ['-e', 'utf8'], lambda b, p: es.compile_stream_c(b, p, a.timeout, extra=('-e', 'utf8'))),
        ('c-utf8-vm', ['-e', 'utf8', '--engine=vm'],
         lambda b, p: es.compile_stream_c(b, p, a.timeout, engine='vm', extra=('-e', 'utf8'))),
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
                row = table.setdefault(name, {})
                if not ok_a and not ok_b:
                    row['both-refuse'] = row.get('both-refuse', 0) + 1
                    continue
                if ok_a != ok_b:
                    row['ASYMMETRIC'] = row.get('ASYMMETRIC', 0) + 1
                    others.append((name, key, 'one side refused'))
                    continue
                cls, why, n = classify(c_a, c_b, abi)
                row[cls] = row.get(cls, 0) + 1
                if cls == 'OTHER':
                    others.append((name, key, why))
                if cls == 'shape':
                    shapes.append((name, key, why))
                if cls in ('lazy', 'shape'):
                    blocks[name] = blocks.get(name, 0) + n
                    if argv_extra is not None:
                        movers.append((name, key, item[2], argv_extra))
        print('  %s done' % name, flush=True)

    cols = ['identical', 'abi', 'lazy', 'shape', 'OTHER', 'ASYMMETRIC', 'both-refuse']
    print('\n| stream | ' + ' | '.join(cols) + ' | prefixes |')
    print('|---|' + '---|' * (len(cols) + 1))
    for s in sorted(table):
        print('| %s | %s | %d |' % (s, ' | '.join(str(table[s].get(c, 0)) for c in cols), blocks.get(s, 0)))
    for s, key, why in shapes:
        print('SHAPE: %s %s: %s' % (s, key, why))

    bad = list(others)
    total = sum(t.get('lazy', 0) + t.get('shape', 0) for t in table.values())
    for s in ('c-default', 'c-vm', 'c-utf8-vm', 'c-comments'):
        if not (table.get(s, {}).get('lazy', 0) + table.get(s, {}).get('shape', 0)):
            bad.append((s, '-', 'no lazy mover: the population is empty (K35)'))
    moved_ir = sum(v for k, v in table.get('emit-ir-vm', {}).items() if k not in ('identical', 'abi', 'both-refuse'))
    if moved_ir:
        bad.append(('emit-ir-vm', '-', '%d listing(s) moved' % moved_ir))
    if total < a.floor:
        bad.append(('*', '-', 'lazy total %d below the floor %d' % (total, a.floor)))

    if a.movers_out:
        with open(a.movers_out, 'w') as fh:
            fh.write('# stream\tkey\tpattern (escape-encoded)\targv\n')
            for stream, key, pat, argv_extra in movers:
                fh.write('%s\t%s\t%s\t%s\n' % (stream, key, es.encode_escape(
                    pat.encode('utf-8', 'surrogateescape') if isinstance(pat, str) else pat),
                    ' '.join(argv_extra)))

    if a.asm:
        root = os.path.join(out, 'vmlazycensus-asm')
        shutil.rmtree(root, ignore_errors=True)
        jobs = [m for m in movers if m[0] != 'c-comments']
        print('\n== assembly: %d movers, recipes %s ==' % (len(jobs), recipes), flush=True)
        asm_tab = {r: {} for r in recipes}
        nonid = []

        def asm_job(job):
            i, (stream, key, pat, argv_extra) = job
            dirs = rc.emit_pair(ref_bin, tree_bin, pat, argv_extra, root, 'm%d' % i, a.timeout, abi)
            res = {}
            if dirs is None:
                return stream, key, None, pat, argv_extra
            for r in recipes:
                sa, ea = rc.asm_of(cc, dirs[0], r, 300)
                sb, eb = rc.asm_of(cc, dirs[1], r, 300)
                if sa is None or sb is None:
                    res[r] = ('ERROR', (ea or eb or b'').decode(errors='replace'))
                    continue
                na, nb = rc.norm_asm(sa, []), rc.norm_asm(sb, [])
                if na == nb:
                    res[r] = ('identical', None)
                else:
                    ia = [l for l in na.split(b'\n') if l.startswith(b'\t')]
                    ib = [l for l in nb.split(b'\n') if l.startswith(b'\t')]
                    res[r] = ('DIFFERENT', '%d vs %d instruction lines' % (len(ia), len(ib)))
            shutil.rmtree(os.path.join(root, 'm%d' % i), ignore_errors=True)
            return stream, key, res, pat, argv_extra

        with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
            for stream, key, res, pat, argv_extra in ex.map(asm_job, list(enumerate(jobs))):
                if res is None:
                    bad.append(('asm', key, 'could not re-emit the pair'))
                    continue
                for r, (v, why) in res.items():
                    asm_tab[r][v] = asm_tab[r].get(v, 0) + 1
                    if v == 'ERROR':
                        bad.append(('asm ' + r, key, why))
                    elif v != 'identical':
                        nonid.append((stream, r, why, pat, argv_extra))
        shutil.rmtree(root, ignore_errors=True)
        print('| recipe | identical | DIFFERENT | ERROR |')
        print('|---|---|---|---|')
        for r in recipes:
            t = asm_tab[r]
            print('| `%s` | %d | %d | %d |' % (r, t.get('identical', 0), t.get('DIFFERENT', 0), t.get('ERROR', 0)))
        if a.nonid_out:
            with open(a.nonid_out, 'w') as fh:
                fh.write('# stream\trecipe\tinstructions\tpattern (escape-encoded)\targv\n')
                for stream, r, why, pat, argv_extra in nonid:
                    fh.write('%s\t%s\t%s\t%s\t%s\n' % (stream, r, why, es.encode_escape(
                        pat.encode('utf-8', 'surrogateescape') if isinstance(pat, str) else pat),
                        ' '.join(argv_extra)))

    for stream, key, why in bad[:40]:
        print('FAIL: %s %s: %s' % (stream, key, why))
    print('census: %s (lazy movers %d)' % ('CLEAN' if not bad else '%d FAIL' % len(bad), total))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
