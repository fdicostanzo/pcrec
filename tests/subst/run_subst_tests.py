#!/usr/bin/env python3
"""tests/subst/run_subst_tests.py -- [M4-SUBST] the subst artifact's checks
(docs/spec/subst_api.md; replace_design.md §R4): every cell of cells.tsv compiled
and run through subst_drv.c, held to its stated answer AND to libpcre2's
pcre2_substitute, the independent oracle, where pcre2 can answer.

Usage: run_subst_tests.py WORKDIR [CELLS.tsv]
Env: PCREC (default build/pcrec), CC (default cc), GENCFLAGS, PCRE2_AVAILABLE,
PCRE2_CFLAGS, PCRE2_LIBS (tests/lib/resolve_pcre2.sh, read by the .sh
wrapper).

A cell is one TAB-separated line (`#` lines are comments):

  ID FLAGS PATTERN TEMPLATE STRICT LIMIT SUBJECT VARS EXPECT P2 LABEL REACH

  FLAGS     pcrec's rx flags beyond `--features all` (`-` none): `-e utf8`,
            `-i`, `--no-captures`; `-e utf8` and `-i` also set the oracle's
  PATTERN   as written; `rep:N:TEXT` is TEXT repeated N times
  TEMPLATE  as written, compiled through --subst-file; `esc:T` decodes T's
            \\xNN \\n \\t \\\\ first; `arg:T` compiles through --subst;
            a leading `utf8:` compiles it with `-e utf8` (subst_api.md §2¶5)
  STRICT    blank | strict (RX_SUBST_STRICT at run time, §4¶23)
  LIMIT     a count, or `all`; `@START` after it starts the iterator (and
            the oracle) at START
  SUBJECT   in the escape vocabulary above; `rep:N:TEXT` repeats
  VARS      `-`, or `name=value,...` (`name` alone: passed with p == NULL)
  EXPECT    out:TEXT:N (the output and the substitution count) |
            rc:NAME (the recipe's code, or the setup's) |
            check:NAME:ROW (the check's code over the by-name helper's map,
            *bad_ref)
  P2        same (pcre2 answers EXPECT's out exactly) | out:TEXT:N |
            rc:NUMBER (pcre2's own answer, a stated difference) | na
  LABEL     `-` when P2 is same or na, else the difference's name
            (subst_api.md §9's row)
  REACH     `-`, or comma-separated tokens; every token of REACH_NEED must
            be carried by at least one PASSING cell (K35)

Per cell the generic arms hold too (subst_drv.c's header names each): with
LIMIT all, §6¶4's batch recipe, §6¶5's RX_FOREACH recipe, replace-all into
a buffer that fits (the count), sized only, at exact capacity, one byte
short (NOSPACE with the full length), and over a 0xA5-dirty iterator answer
what §6¶2's per-match recipe answers; replace-all refuses an ENDED iterator;
with a LIMIT the recipe leaves the iterator where exactly LIMIT <rx>_next
calls leave it; a template without names answers the same with no map and
with a hand-filled map; the element refuses a piece array one short with
NOSPACE before writing, a map slot past ncaps (as the check does), an
unknown flag, a match end past ctx->len; the check refuses a map one entry
short and an rx with no slot; a map of NOGROUP entries under STRICT renders
every reference as unset; for `${!name}` templates the element refuses a ctx
with no variables or one too few, and under STRICT an unset one is
PCREC_ERR_UNSET_VAR; where pcre2 answers the same, the element without
RX_SUBST_GAPS answers what pcre2's SUBSTITUTE_REPLACEMENT_ONLY does, and
pcre2 at outlength == the length is NOMEMORY asking for length + 1 (its
NUL, §9 row 6).
"""

import os
import re
import subprocess
import sys

CODES = {
    'NOSPACE': -11, 'BADSPAN': -12, 'UNSET': -14,
    'MISMATCH': -15, 'MISSING_REF': -16, 'UNSET_VAR': -8, 'ITER': -10,
    'STEPS': -2,
}
PCRE2_NOMEMORY = -48
RX_FOREACH_PAIRS = 256      # match_api.md §3.8.2's default
REACH_NEED = ['S1346', 'S1347', 'S1348', 'S1352', 'S1354', 'S1355',
              'nogroupceiling', 'batch64', 'illformed', 'badspancorner', 'nul',
              'vars', 'abi', 'giveup', 'subject', 'before', 'after', 'amp', 'start',
              'agree', 'utf8tmpl', 'encbind', 'unk', 'bmis', 'vmis', 'vuerr', 'nogap',
              'blen', 'negnum', 'flatsat', 'absent', 'lim', 'short', 'exact', 'size',
              'count', 'batch', 'foreach', 'dirty', 'stale', 'nomap', 'hand', 'room',
              'mis', 'nog', 'pairs']


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


# The `unit` line's answer (subst_drv.c's unit()): flatten's total saturates
# at SIZE_MAX and a short buffer is left untouched, its total still 4
# (§10¶4); the helper refuses a numbered reference -3 as MISSING_REF
# (§3¶13); under RX_SUBST_MAP_ABSENT a name and a number the rx lacks are
# both NOGROUP, counted 2, *bad_ref the first (§3¶15).
UNIT_WANT = 'unit\tflat=1,1,4\tneg=-16\tabsent=0,2,0,-1'


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
            if not check(col[4] in ('blank', 'strict'), '%s:%d: STRICT %r' % (cells_path, ln, col[4])):
                continue
            cells.append(col)

    rxs, sbs = {}, {}
    for c in cells:
        rxs.setdefault((c[1], c[2]), len(rxs))
        sbs.setdefault(c[3], len(sbs))

    # ---- compile every rx and subst artifact, and the support unit --------
    srcs = []
    for (flags, pat), i in rxs.items():
        args = [pcrec, '--features', 'all', '-p', 'r%d' % i, '-o', os.path.join(work, 'r%d.c' % i)]
        args += [] if flags == '-' else flags.split()
        r = subprocess.run(args + ['--pattern', raw(pat)], capture_output=True)
        if not check(r.returncode == 0, 'rx %d (%s) refused: %s' % (i, pat, r.stderr.decode('latin-1').strip())):
            return finish(passed, failed)
        srcs.append('r%d.c' % i)
    for tmpl, i in sbs.items():
        args = [pcrec, '-p', 's%d' % i, '-o', os.path.join(work, 's%d.c' % i)]
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
    r = subprocess.run([pcrec, '--emit-support', '-o', os.path.join(work, 'support.h')], capture_output=True)
    if not check(r.returncode == 0, '--emit-support: ' + r.stderr.decode('latin-1').strip()):
        return finish(passed, failed)

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
        lines.append('\t'.join([c[0], str(rxs[(c[1], c[2])]), str(sbs[c[3]]),
                                raw(c[2]).hex() or '-', str(p2opts), '1' if c[4] == 'strict' else '0',
                                c[5], decode(c[6]).hex() or '-', v]))
    r = subprocess.run([drv], input='\n'.join(lines) + '\n', capture_output=True, text=True)
    if not check(r.returncode == 0, 'driver exited %d: %s' % (r.returncode, r.stderr[-2000:])):
        return finish(passed, failed)
    out = r.stdout.splitlines()
    reached = set()
    if check(out and out[0] == UNIT_WANT, 'unit: %r, want %r' % (out[:1], UNIT_WANT)):
        reached.update(['flatsat', 'negnum', 'absent'])
    got = {}
    for ln in out[1:]:
        f = ln.split('\t')
        got[f[0]] = dict(x.split('=', 1) for x in f[1:])

    mm, ns = str(CODES['MISMATCH']), str(CODES['NOSPACE'])
    p2_compared = 0
    for c in cells:
        cid, expect, p2want, label, reach = c[0], c[8], c[9], c[10], c[11]
        g = got.get(cid)
        if not check(g is not None, '%s: no driver line' % cid):
            continue
        before = failed
        kind, _, rest = expect.partition(':')
        chk = g['check'].split(',')
        all_ = c[5].split('@')[0] == 'all'
        if check(g.get('babi') == mm, '%s: the check took a record of another abi: %s' % (cid, g.get('babi'))):
            reached.add('abi')
        if kind == 'check':
            name, row = rest.rsplit(':', 1)
            check(chk == [str(CODES[name]), row], '%s: check %s, want %s,%s' % (cid, g['check'], CODES[name], row))
        elif kind == 'rc' and chk[0] != '0':
            # a code the setup itself gives (an unset variable under STRICT)
            check(chk[0] == str(CODES[rest]), '%s: setup %s, want %d' % (cid, g['check'], CODES[rest]))
        elif check(chk == ['0', '-1'], '%s: check refused: %s' % (cid, g['check'])):
            main_ = g['main'].split(',')
            if kind == 'out':
                text, n = rest.rsplit(':', 1)
                want = decode(text)
                L, hx = len(want), want.hex() or '-'
                same = '0,%d,%s' % (L, hx)
                check(main_ == ['0', str(L), n, hx], '%s: main %s, want 0,%d,%s,%r' % (cid, g['main'], L, n, want))
                arms = [('nomap', 'nomap', same), ('hand', 'hand', same)]
                if all_ and int(g['nc']) > RX_FOREACH_PAIRS:
                    # more pairs per match than the stack array: RX_FOREACH and
                    # replace-all refuse (match_api.md §3.8.2¶5, subst_api.md §10¶7)
                    arms += [('batch', 'batch', same), ('fe', 'pairs', '%d,0,-' % CODES['ITER']),
                             ('ra', 'pairs', '%s,0,-' % mm), ('size', 'pairs', '%s,0' % mm)]
                elif all_:
                    arms += [('batch', 'batch', same), ('fe', 'foreach', same),
                             ('ra', 'count', '%s,%d,%s' % (n, L, hx)), ('size', 'size', '%s,%d' % (n, L)),
                             ('exact', 'exact', '%s,%d' % (n, L)), ('dirty', 'dirty', '%s,%d,%s' % (n, L, hx))]
                    if L:
                        arms.append(('short', 'short', '%s,%d' % (ns, L)))
                for a, tok, w in arms:
                    if a in ('nomap', 'hand') and a not in g:
                        continue
                    if check(g.get(a) == w, '%s: %s %s, want %s' % (cid, a, g.get(a), w)):
                        reached.add(tok)
            else:
                code = str(CODES[rest])
                check(main_[0] == code, '%s: main %s, want %s' % (cid, g['main'], code))
                for a in (['batch', 'fe', 'ra', 'size', 'dirty'] if all_ else []) + ['nomap', 'hand']:
                    if a in g:
                        check(g[a].split(',')[0] == code, '%s: %s %s, want %s' % (cid, a, g[a], code))
            if all_ and check(g.get('stale') == str(CODES['ITER']),
                              '%s: replace-all over an ENDED iterator gave %s, want PCREC_ERR_ITER' % (cid, g.get('stale'))):
                reached.add('stale')
            rm = g.get('room', '').split(',')
            if check(len(rm) == 3 and rm[0] == ns and rm[2] == '1',
                     '%s: the element one piece short gave %s, want NOSPACE untouched' % (cid, g.get('room'))):
                reached.add('room')
            if 'mis' in g and check(g['mis'] == '%d,%s' % (CODES['MISSING_REF'], mm),
                                    '%s: a map slot at ncaps: check,element %s, want MISSING_REF,MISMATCH' % (cid, g['mis'])):
                reached.add('mis')
            if 'blen' in g and check(g['blen'] == str(CODES['BADSPAN']),
                                     '%s: element took a match end past ctx->len: %s' % (cid, g['blen'])):
                reached.add('blen')
            if check(g.get('unk') == '%s,%s' % (mm, mm), '%s: an unknown flag: element,replace-all %s' % (cid, g.get('unk'))):
                reached.add('unk')
            bm = g.get('bmis', '').split(',')
            if check(len(bm) == 2 and bm[0] in ('na', mm) and bm[1] == mm,
                     '%s: the check took one map entry too few or an rx with no slot: %s' % (cid, g.get('bmis'))) \
                    and bm[0] == mm:
                reached.add('bmis')
            if kind == 'out' and main_[2] != '0' and re.search(r'\$\{?[1-9A-Za-z]', c[3]) \
                    and '${!' not in c[3]:
                # an intended NOGROUP renders empty, RX_SUBST_STRICT included (§3¶6, §9 row 20)
                if check(g.get('nog', '').split(',')[0] == '0' and int(g['nog'].split(',')[1]) < L,
                         '%s: a NOGROUP map under STRICT gave %s, want 0 and shorter than %d' % (cid, g.get('nog'), L)):
                    reached.add('nog')
            if '${!' in c[3]:
                if check(g.get('vmis') == '%s,%s' % (mm, mm),
                         '%s: element took a ctx with no / too few variables: %s' % (cid, g.get('vmis'))):
                    reached.add('vmis')
                if c[4] == 'strict' and check(g.get('vuerr') == str(CODES['UNSET_VAR']),
                                              '%s: element rendered an unset variable under STRICT: %s'
                                              % (cid, g.get('vuerr'))):
                    reached.add('vuerr')
            if 'lim' in g:
                a, b = g['lim'].split(',')
                if check(a == b, '%s: the recipe stopped at LIMIT with the iterator at %s, %s after exactly LIMIT calls'
                         % (cid, a, b)):
                    reached.add('lim')
        # the oracle
        if p2want != 'na' and have_p2:
            p2 = g.get('p2', 'na')
            if p2want == 'same':
                text, n = rest.rsplit(':', 1)
                want = decode(text)
                check(p2 == '%s,%s' % (n, want.hex() or '-'), '%s: pcre2 %s, want the same %s,%r' % (cid, p2, n, want))
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
                check(p2 == '%s,%s' % (n, decode(text).hex() or '-'), '%s: pcre2 %s, want the stated difference %s' % (cid, p2, p2want))
            else:
                check(p2.split(',')[0] == p2want[3:], '%s: pcre2 %s, want the stated %s' % (cid, p2, p2want))
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
