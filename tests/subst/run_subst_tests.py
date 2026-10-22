#!/usr/bin/env python3
"""tests/subst/run_subst_tests.py -- [M4-SUBST] the subst artifact's checks
(docs/spec/subst_api.md; replace_design.md §R3): every cell of cells.tsv compiled
and run through subst_drv.c, held to its stated answer AND to libpcre2's
pcre2_substitute, the independent oracle, where pcre2 can answer.

Usage: run_subst_tests.py WORKDIR [CELLS.tsv]
Env: PCREC (default build/pcrec), CC (default cc), GENCFLAGS, PCRE2_AVAILABLE,
PCRE2_CFLAGS, PCRE2_LIBS (tests/lib/resolve_pcre2.sh, read by the .sh
wrapper).

A cell is one TAB-separated line (`#` lines are comments):

  ID FLAGS PATTERN TEMPLATE UNSET LIMIT SUBJECT VARS EXPECT P2 LABEL REACH

  FLAGS     pcrec's rx flags beyond `--features all` (`-` none): `-e utf8`,
            `-i`, `--no-captures`; `-e utf8` and `-i` also set the oracle's
  PATTERN   as written; `rep:N:TEXT` is TEXT repeated N times
  TEMPLATE  as written, compiled through --subst-file; `esc:T` decodes T's
            \\xNN \\n \\t \\\\ first; `arg:T` compiles through --subst;
            a leading `utf8:` compiles it with `-e utf8` (subst_api.md §2¶5)
  UNSET     empty | error (`--unset=`)
  LIMIT     a count, or `all`; `@START` after it starts the iterator (and
            the oracle) at START
  SUBJECT   in the escape vocabulary above; `rep:N:TEXT` repeats
  VARS      `-`, or `name=value,...` (`name` alone: passed with p == NULL)
  EXPECT    out:TEXT:N (the output and the substitution count) |
            rc:NAME (the glue's code) | bind:NAME:ROW (bind's code, *bad_ref)
  P2        same (pcre2 answers EXPECT's out exactly) | out:TEXT:N |
            rc:NUMBER (pcre2's own answer, a stated difference) | na
  LABEL     `-` when P2 is same or na, else the difference's name
            (replace_design.md §R3.10's row)
  REACH     `-`, or comma-separated tokens; every token of REACH_NEED must
            be carried by at least one PASSING cell (K35)

Per `out` cell the generic arms hold too: out == NULL sizes the same; cap ==
the length fits exactly; cap == length - 1 is NOSPACE with the full length
and count (S1353); the k = 1 custom glue answers the same; a 0xA5-dirty
iterator answers the same (S1352); the element refuses a foreign ncap
(S1351); a LIMIT stop leaves the iterator where exactly LIMIT <rx>_next calls
leave it (S1349); the glue refuses a BOUND and an ENDED iterator with
PCREC_ERR_ITER; the element refuses an unknown flag; bind refuses one run too
few and an rx with no slot; for `${!name}` templates the element refuses a
ctx with no variables or one too few, and under --unset=error renders an
unset one as PCREC_ERR_UNSET_VAR; where pcre2 answers the same, the element
without RX_SUBST_GAPS answers what pcre2's SUBSTITUTE_REPLACEMENT_ONLY does,
and pcre2 at outlength == the length is NOMEMORY asking for length + 1 (its
NUL, §R3.10 row 1).
"""

import os
import re
import subprocess
import sys

CODES = {
    'NOSPACE': -11, 'BADSPAN': -12, 'RENDER': -13, 'UNSET': -14,
    'MISMATCH': -15, 'MISSING_REF': -16, 'UNSET_VAR': -8, 'ITER': -10,
    'STEPS': -2,
}
PCRE2_NOMEMORY = -48
REACH_NEED = ['S1346', 'S1347', 'S1348', 'S1349', 'S1350', 'S1351', 'S1352',
              'S1353', 'S1354', 'S1355', 'nogroupceiling', 'batch64', 'illformed',
              'badspancorner', 'nul', 'vars', 'abi', 'giveup',
              'subject', 'before', 'after', 'amp', 'start', 'agree', 'utf8tmpl', 'encbind',
              'fresh', 'unk', 'bmis', 'vmis', 'vuerr', 'nogap']


def decode(t):
    """The escape vocabulary to bytes; `rep:N:TEXT` repeats."""
    m = re.match(r'rep:(\d+):(.*)$', t, re.S)
    if m:
        return decode(m.group(2)) * int(m.group(1))
    out = bytearray()
    i = 0
    while i < len(t):
        c = t[i]
        if c == '\\' and i + 1 < len(t):
            n = t[i + 1]
            if n == 'x':
                out.append(int(t[i + 2:i + 4], 16))
                i += 4
                continue
            out += {'n': b'\n', 't': b'\t', '\\': b'\\'}.get(n, b'\\' + n.encode())
            i += 2
            continue
        out += c.encode('latin-1')
        i += 1
    return bytes(out)


def raw(t):
    m = re.match(r'rep:(\d+):(.*)$', t, re.S)
    return (m.group(2) * int(m.group(1))).encode('latin-1') if m else t.encode('latin-1')


def main():
    work = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    cells_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, 'cells.tsv')
    root = os.path.dirname(os.path.dirname(here))
    pcrec = os.environ.get('PCREC', os.path.join(root, 'build', 'pcrec'))
    cc = os.environ.get('CC', 'cc')
    gencflags = os.environ.get('GENCFLAGS', '-O1 -std=gnu11 -Wall -Wextra -Werror').split()
    have_p2 = os.environ.get('PCRE2_AVAILABLE') == '1'
    os.makedirs(work, exist_ok=True)

    passed = failed = 0

    def check(ok, what):
        nonlocal passed, failed
        if ok:
            passed += 1
        else:
            failed += 1
            print('FAIL: ' + what)
        return ok

    cells = []
    with open(cells_path, encoding='latin-1') as f:
        for ln, line in enumerate(f, 1):
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            col = line.split('\t')
            if not check(len(col) == 12, '%s:%d: %d columns, want 12' % (cells_path, ln, len(col))):
                continue
            cells.append(col)

    rxs, sbs = {}, {}
    for c in cells:
        rxs.setdefault((c[1], c[2]), len(rxs))
        sbs.setdefault((c[3], c[4]), len(sbs))

    # ---- compile every rx and subst artifact, one pcrec each -------------
    srcs = []
    for (flags, pat), i in rxs.items():
        args = [pcrec, '--features', 'all', '-p', 'r%d' % i, '-o', os.path.join(work, 'r%d.c' % i)]
        args += [] if flags == '-' else flags.split()
        r = subprocess.run(args + ['--pattern', raw(pat)], capture_output=True)
        if not check(r.returncode == 0, 'rx %d (%s) refused: %s' % (i, pat, r.stderr.decode('latin-1').strip())):
            return finish(passed, failed)
        srcs.append('r%d.c' % i)
    for (tmpl, unset), i in sbs.items():
        args = [pcrec, '-p', 's%d' % i, '--unset=' + unset, '-o', os.path.join(work, 's%d.c' % i)]
        if tmpl.startswith('utf8:'):
            args += ['-e', 'utf8']
            tmpl = tmpl[5:]
        if tmpl.startswith('arg:'):
            args += ['--subst', tmpl[4:].encode('latin-1')]
        else:
            tb = decode(tmpl[4:]) if tmpl.startswith('esc:') else raw(tmpl)
            tf = os.path.join(work, 's%d.tmpl' % i)
            with open(tf, 'wb') as f:
                f.write(tb)
            args += ['--subst-file', tf]
        r = subprocess.run(args, capture_output=True)
        if not check(r.returncode == 0, 'subst %d (%s) refused: %s' % (i, tmpl, r.stderr.decode('latin-1').strip())):
            return finish(passed, failed)
        srcs.append('s%d.c' % i)

    # ---- the table: headers in both orders (subst first, then rx first) --
    with open(os.path.join(work, 'subst_tab.h'), 'w') as f:
        f.write('#include "s0.h"\n'
                'extern const struct rx_info *const subst_rx[];\n'
                'extern const struct rx_subst_info *const subst_sb[];\n')
    with open(os.path.join(work, 'tab.c'), 'w') as f:
        n = max(len(rxs), len(sbs))
        for i in range(n):
            pair = (['s%d.h' % i] if i < len(sbs) else []) + (['r%d.h' % i] if i < len(rxs) else [])
            for h in (pair if i % 2 == 0 else reversed(pair)):
                f.write('#include "%s"\n' % h)
        f.write('const struct rx_info *const subst_rx[] = {\n%s};\n'
                % ''.join('    &r%d_info,\n' % i for i in range(len(rxs))))
        f.write('const struct rx_subst_info *const subst_sb[] = {\n%s};\n'
                % ''.join('    &s%d_subst_info,\n' % i for i in range(len(sbs))))
    drv = os.path.join(work, 'drv')
    p2 = (['-DSUBST_PCRE2'] + os.environ.get('PCRE2_CFLAGS', '').split()) if have_p2 else []
    p2libs = os.environ.get('PCRE2_LIBS', '').split() if have_p2 else []
    r = subprocess.run([cc] + gencflags + p2 + ['-I', work, '-o', drv,
                       os.path.join(here, 'subst_drv.c'), os.path.join(work, 'tab.c')]
                       + [os.path.join(work, s) for s in srcs] + p2libs, capture_output=True)
    if not check(r.returncode == 0, 'driver build: ' + r.stderr.decode('latin-1')[-2000:]):
        return finish(passed, failed)

    # ---- run -------------------------------------------------------------
    lines = []
    for c in cells:
        p2opts = (1 if '-e utf8' in c[1] else 0) | (2 if re.search(r'(^| )-i( |$)', c[1]) else 0)
        if c[7] == '-':
            v = '-'
        else:
            vs = []
            for item in c[7].split(','):
                if '=' in item:
                    k, val = item.split('=', 1)
                    vs.append(raw(k).hex() + '=' + decode(val).hex())
                else:
                    vs.append(raw(item).hex())
            v = ','.join(vs)
        lines.append('\t'.join([c[0], str(rxs[(c[1], c[2])]), str(sbs[(c[3], c[4])]),
                                raw(c[2]).hex() or '-', str(p2opts), c[5],
                                decode(c[6]).hex() or '-', v]))
    r = subprocess.run([drv], input='\n'.join(lines) + '\n', capture_output=True, text=True)
    if not check(r.returncode == 0, 'driver exited %d: %s' % (r.returncode, r.stderr[-2000:])):
        return finish(passed, failed)
    out = r.stdout.splitlines()
    check(out and out[0] == 'unit\tput=1,0', 'unit: rx_subst_put does not saturate at SIZE_MAX (S1350): %r' % (out[:1],))
    reached = {'S1350'} if out and out[0] == 'unit\tput=1,0' else set()
    got = {}
    for ln in out[1:]:
        f = ln.split('\t')
        got[f[0]] = dict(x.split('=', 1) for x in f[1:])

    p2_compared = 0
    for c in cells:
        cid, expect, p2want, label, reach = c[0], c[8], c[9], c[10], c[11]
        g = got.get(cid)
        if not check(g is not None, '%s: no driver line' % cid):
            continue
        before = failed
        kind, _, rest = expect.partition(':')
        bind = g['bind'].split(',')
        if check(g.get('babi') == str(CODES['MISMATCH']), '%s: a record of another abi bound: %s' % (cid, g.get('babi'))):
            reached.add('abi')
        if kind == 'bind':
            name, row = rest.rsplit(':', 1)
            check(bind == [str(CODES[name]), row], '%s: bind %s, want %s,%s' % (cid, g['bind'], CODES[name], row))
        elif check(bind == ['0', '-1'], '%s: bind refused: %s' % (cid, g['bind'])):
            main_ = g['main'].split(',')
            if kind == 'out':
                text, n = rest.rsplit(':', 1)
                want = decode(text)
                L = len(want)
                check(main_ == ['0', str(L), n, want.hex() or '-'],
                      '%s: main %s, want 0,%d,%s,%r' % (cid, g['main'], L, n, want))
                check(g['size'] == '0,%d,%s' % (L, n), '%s: size-only %s' % (cid, g['size']))
                check(g.get('exact') == '0,%d,%s' % (L, n), '%s: exact cap %s' % (cid, g.get('exact')))
                if L:
                    if check(g.get('short') == '%d,%d,%s' % (CODES['NOSPACE'], L, n),
                             '%s: cap = len - 1 gives %s, want NOSPACE,%d,%s (S1353)' % (cid, g.get('short'), L, n)):
                        reached.add('S1353')
                check(g['k1'] == '0,%d,%s' % (L, want.hex() or '-'), '%s: k=1 glue %s' % (cid, g['k1']))
                if check(g['dirty'] == '0,%d,%s' % (L, want.hex() or '-'), '%s: dirty iterator %s' % (cid, g['dirty'])) \
                        and '${!' in c[3] and c[7] == '-':
                    reached.add('S1352')
            else:
                code = CODES[rest]
                check(main_ == [str(code), '0', '0', '-'], '%s: main %s, want %d,0,0' % (cid, g['main'], code))
                check(g['size'].split(',')[0] == str(code), '%s: size-only %s' % (cid, g['size']))
                check(g['k1'].split(',')[0] == str(code), '%s: k=1 glue %s' % (cid, g['k1']))
                check(g['dirty'].split(',')[0] == str(code), '%s: dirty iterator %s' % (cid, g['dirty']))
            if check(g['mis'] == str(CODES['MISMATCH']), '%s: element took a foreign ncap: %s (S1351)' % (cid, g['mis'])):
                reached.add('S1351')
            mm = str(CODES['MISMATCH'])
            if check(g.get('unk') == mm, '%s: element took an unknown flag: %s' % (cid, g.get('unk'))):
                reached.add('unk')
            it_ = str(CODES['ITER'])
            if check(g.get('stale') == '%s,%s' % (it_, it_),
                     '%s: the glue over a BOUND, ENDED iterator gave %s, want PCREC_ERR_ITER twice' % (cid, g.get('stale'))):
                reached.add('fresh')
            bm = g.get('bmis', '').split(',')
            if check(len(bm) == 2 and bm[0] in ('na', mm) and bm[1] == mm,
                     '%s: bind took one run too few or an rx with no slot: %s' % (cid, g.get('bmis'))) and bm[0] == mm:
                reached.add('bmis')
            if '${!' in c[3]:
                if check(g.get('vmis') == '%s,%s' % (mm, mm),
                         '%s: element took a ctx with no / too few variables: %s' % (cid, g.get('vmis'))):
                    reached.add('vmis')
                if c[4] == 'error' and check(g.get('vuerr') == str(CODES['UNSET_VAR']),
                                             '%s: element rendered an unset variable under --unset=error: %s'
                                             % (cid, g.get('vuerr'))):
                    reached.add('vuerr')
            if 'lim' in g:
                a, b = g['lim'].split(',')
                if check(a == b, '%s: the glue stopped at LIMIT with the iterator at %s, %s after exactly LIMIT calls (S1349)'
                         % (cid, a, b)):
                    reached.add('S1349')
        # the oracle
        if p2want != 'na' and have_p2:
            p2 = g.get('p2', 'na')
            if p2want == 'same':
                text, n = rest.rsplit(':', 1)
                want = decode(text)
                ok = check(p2 == '%s,%s' % (n, want.hex() or '-'), '%s: pcre2 %s, want the same %s,%r' % (cid, p2, n, want))
                ng, ro = g.get('nogap', ''), g.get('p2ro', '')
                if 'nogap' in g and check(ro.startswith(n + ',') and ng.split(',', 2)[0] == '0'
                                          and ng.split(',', 2)[2] == ro.split(',', 1)[1],
                                          '%s: the element without GAPS gave %s, pcre2 REPLACEMENT_ONLY %s'
                                          % (cid, ng, ro)):
                    reached.add('nogap')
                check(g.get('p2short') == '%d,%d' % (PCRE2_NOMEMORY, len(want) + 1),
                      '%s: pcre2 at outlength %d: %s, want NOMEMORY asking %d (its NUL)' % (cid, len(want), g.get('p2short'), len(want) + 1))
            elif p2want.startswith('out:'):
                text, n = p2want[4:].rsplit(':', 1)
                ok = check(p2 == '%s,%s' % (n, decode(text).hex() or '-'), '%s: pcre2 %s, want the stated difference %s' % (cid, p2, p2want))
            else:
                ok = check(p2.split(',')[0] == p2want[3:], '%s: pcre2 %s, want the stated %s' % (cid, p2, p2want))
            check(p2want == 'same' or label != '-', '%s: a pcre2 difference with no LABEL' % cid)
            p2_compared += 1
        if failed == before and reach != '-':
            reached.update(reach.split(','))

    for t in REACH_NEED:
        check(t in reached, 'reach token %s carried by no passing cell (K35)' % t)
    if have_p2:
        check(p2_compared >= 30, 'only %d cells compared with pcre2 (floor 30)' % p2_compared)
    print('cells: %d, rx artifacts: %d, subst artifacts: %d, pcre2-compared: %d, reached: %s'
          % (len(cells), len(rxs), len(sbs), p2_compared, ' '.join(sorted(reached))))
    return finish(passed, failed)


def finish(passed, failed):
    print('checks passed: %d' % passed)
    print('checks failed: %d' % failed)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
