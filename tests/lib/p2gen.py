#!/usr/bin/env python3
"""tests/lib/p2gen.py SPEC.gen.py > FILE.rxt -- writes `.rxt` blocks whose
expectations come from libpcre2 (tests/lib/p2probe.c), never from pcrec.

Lane langfix2 wrote K122-K127's corpora with it; lane langfix3 moved it here
from the lane's gitignored scratch so they can be re-derived. Each corpus's
SPEC sits beside it as `<name>.gen.py`; regenerating one reproduces the
committed file byte for byte against libpcre2 10.46, the reference oracle on
the Linux dev box (docs/testing.md "The boxes").

SPEC defines HEAD (the file's leading comment) and BLOCKS, a list of
dict(c=comment, p=pattern, f=features, fl=flags, e=encoding, eng=engine,
po=1 for `# pcre2-only`, s=[subjects] or 'perr'). A subject is a str/bytes,
or (startpos, subject). A `perr` block asserts libpcre2 refuses it too
(`ok=1`: libpcre2 accepts it, for pcrec's documented capability refusals).

The probe is built on demand into build/p2gen/ (gitignored) with plain `gcc`
and `-lpcre2-8`; the headers it compiles against are the oracle's version."""
import os
import runpy
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'tests', 'lib', 'p2probe.c')
PROBE = os.path.join(ROOT, 'build', 'p2gen', 'p2probe')


def probe():
    if not os.path.exists(PROBE) or os.path.getmtime(PROBE) < os.path.getmtime(SRC):
        os.makedirs(os.path.dirname(PROBE), exist_ok=True)
        subprocess.run(['gcc', '-O1', '-o', PROBE, SRC, '-lpcre2-8'], check=True)
    return PROBE


def esc(b):
    o = ''
    for x in b:
        c = chr(x)
        if 0x20 <= x < 0x7f and c not in '"\\':
            o += c
        else:
            o += '\\x%02x' % x
    return o


def main():
    spec = runpy.run_path(sys.argv[1])
    exe = probe()
    out = [spec.get('HEAD', '')]
    for b in spec['BLOCKS']:
        enc = b.get('e')
        fl = b.get('fl', '')
        opts = ('u' if enc == 'utf8' else '') + ('i' if 'i' in fl else '')
        pb = b['p'].encode()
        if b['c']:
            out.append('\n'.join('# ' + l if l else '#' for l in b['c'].split('\n')))
        if b.get('po'):
            out.append('# pcre2-only')
        out.append('pattern ' + b['p'])
        if b.get('f'):
            out.append('features ' + b['f'])
        if enc:
            out.append('encoding ' + enc)
        if fl:
            out.append('flags ' + fl)
        if b.get('eng'):
            out.append('engine ' + b['eng'])
        subs = b['s']
        args = []
        sl = []
        if subs != 'perr':
            for s in subs:
                sp = 0
                if isinstance(s, tuple):
                    sp, s = s
                sb = s.encode() if isinstance(s, str) else s
                sl.append((sp, sb))
                args.append('%d:%s' % (sp, sb.hex()))
        r = subprocess.run([exe, opts, pb.hex()] + args,
                           capture_output=True, text=True).stdout.split('\n')
        if subs == 'perr':
            assert r[0].startswith('OK' if b.get('ok') else 'ERR'), (b['p'], r[0])
            out.append('perr')
            out.append('')
            continue
        assert r[0].startswith('OK'), (b['p'], r[0])
        ncap = int(r[0].split()[1])
        for (sp, sb), line in zip(sl, r[1:]):
            t = line.split()
            if t[0] == 'N':
                out.append(('n "%s"' % esc(sb)) if sp == 0
                           else ('ns %d "%s"' % (sp, esc(sb))))
            elif t[0] == 'M':
                v = list(map(int, t[1:]))
                out.append(('m "%s" %d %d' % (esc(sb), v[0], v[1])) if sp == 0
                           else ('ms %d "%s" %d %d' % (sp, esc(sb), v[0], v[1])))
                for g in range(1, ncap + 1):
                    out.append('g %d %d %d' % (g, v[2 * g], v[2 * g + 1]))
            else:
                raise SystemExit('give-up %s %s' % (b['p'], line))
        out.append('')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
