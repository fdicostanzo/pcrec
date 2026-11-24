#!/usr/bin/env python3
# binders.py ROOT ASM [RUNNERS_ROOT] : window_split.md rev 2 §7's re-aim table, over an assemble.py
# tree. For every file-keyed binder whose text lives in a file the unit changes, at T (ROOT):
#   mech   every tests/mech/sabotages row (SAB_FILE/SAB_BEFORE and its second site), its fields
#          read by SOURCING the row in bash as scripts/m6read_check_sab_anchors.py does;
#   g2     every runner plant keyed <file>.c@@FROM@@TO in run_g2_win.sh, run_g2_pres.sh,
#          run_proof.sh (read from RUNNERS_ROOT, default ROOT: pass a checkout of
#          lane/memfn-plantcheck to count its re-aimed plants), decoded by each runner's dialect;
#   purity every tests/memfn/purity_rows.tsv row's `old` text;
#   census every tests/memfn/decider_census.tsv row keyed window.c / presence.c / compose.c
#          (its NAME's definition, found by ents.py);
# it prints where the text is found in ASM's memfn/src: `OK file` (found exactly the row's
# count, in exactly one file: the binder's new key), or STALE (nowhere) / AMBIGUOUS (twice, or
# in two files). Then, with --compile, the W26 probe: each mech SAB_AFTER and each g2 TO applied
# to a copy of its NEW file and `gcc-16 -fsyntax-only`-ed there (the kit's flags), PASS/FAIL.
# Last line per population: `binders: <pop> N rows, K OK, B bad`. Exit 1 iff any bad.
import os, re, subprocess, sys, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ents import entities

args = [a for a in sys.argv[1:] if not a.startswith('--')]
root, asm = args[0], args[1]
rroot = args[2] if len(args) > 2 else root
COMPILE = '--compile' in sys.argv
CC = os.environ.get('CC', 'gcc-16')
A = os.path.join(asm, 'memfn/src')
CHANGED = {'window.c', 'presence.c', 'compose.c', 'finder.c', 'ofsskip.c', 'precheck.c',
           'pffind.c', 'generic.c'}
texts = {f: open(os.path.join(A, f)).read() for f in os.listdir(A) if f.endswith(('.c', '.h'))}
FAMILY = sorted(f for f in texts if f.startswith(('window', 'kit_pos', 'kit_pick', 'kit_kb'))
                or f in CHANGED)

# THE RE-SPELL TABLE: the unit's own text changes (edits.spec) a binder's text must follow, so a
# binder quoting a re-spelled line is re-aimed to the NEW spelling in the commit that re-spells it
# (H3's renames; A1/O3's TIE reads; A2's A-model read). Applied as code-token renames, then
# literal replacements; a row found only after it reads `OK*` (re-spelled, then found).
RENAMES = [('in_set', 'kit_pos_in'), ('count', 'kit_pos_count'), ('shape', 'kit_pos_shape'),
           ('two', 'kit_pos_two'), ('full', 'kit_pos_full')]
LITERAL = [('wf_ties[T_MARGIN].to == TIE_RESEED', 'kit_tie_reseeds(T_MARGIN)'),
           ('wf_ties[T_CMODEL].to == TIE_EXCHANGE', 'kit_tie_exchanges(T_CMODEL)'),
           ('wf_arows[d->a[rs].arow].ct != &ct_a_model', '!wf_a_is_model(d->a[rs].arow)')]
def respell(s):
    for o, n in RENAMES: s = re.sub(r'(?<![\w.>])' + o + r'(?=\s*\()', n, s)
    for o, n in LITERAL: s = s.replace(o, n)
    return s

def where(t, count=1, pool=None, orig=None):
    st, nf = where1(t, count, pool, orig)
    if st != 'OK' and respell(t) != t:
        st2, nf2 = where1(respell(t), count, pool, orig)
        if st2 == 'OK': return 'OK*', nf2
    return st, nf

def where1(t, count=1, pool=None, orig=None):
    if orig in texts and orig not in ('window.c',) and texts[orig].count(t) == count:
        return 'OK', orig      # its file is not split: the binder keeps its key
    hits = {f: texts[f].count(t) for f in (pool or texts) if t and texts[f].count(t)}
    if not hits: return 'STALE', None
    if len(hits) > 1 or list(hits.values())[0] != count: return 'AMBIGUOUS', ','.join(f'{f}:{n}' for f, n in sorted(hits.items()))
    return 'OK', list(hits)[0]

FLAGS = ['-O2', '-Wall', '-Wextra', '-std=gnu11', '-fsyntax-only']
def fam(nf): return nf.startswith(('window_', 'kit_'))
def probe(nf, frm, to, more=()):
    """the planted NEW file alone (with the row's other edits in that file, `more`), in a
    scratch dir, its includes resolved in ASM (-I); a TO/AFTER in a family file follows the
    re-spell table (it calls the new names)"""
    if nf.endswith('.h'): return 'SKIP(header)'
    d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
    try:
        p = os.path.join(d, nf)
        s = texts[nf]
        for f_, t_ in ((frm, to),) + tuple(more):
            s = s.replace(f_, respell(t_) if fam(nf) else t_, 1)
        open(p, 'w').write(s)
        r = subprocess.run([CC] + FLAGS + ['-I', A, '-I', os.path.join(asm, 'memfn/include'), p],
                           capture_output=True, text=True)
        return 'PASS' if r.returncode == 0 else 'FAIL ' + (r.stderr.strip().splitlines() or [''])[0][:90]
    finally:
        shutil.rmtree(d)

bad_total = 0
def report(pop, rows):
    global bad_total
    ok = sum(1 for r in rows if r[2] in ('OK', 'OK*') and not r[-1].startswith('FAIL'))
    for r in rows: print(pop + '\t' + '\t'.join(str(x) for x in r))
    b = len(rows) - ok; bad_total += b
    print(f'binders: {pop} {len(rows)} rows, {ok} OK, {b} bad')

# ---- mech
rows = []
sab = os.path.join(root, 'tests/mech/sabotages')
for fn in sorted(f for f in os.listdir(sab) if f.endswith('.sh')):
    out = subprocess.run(['bash', '-c',
        'set -a; SAB_FILE=; SAB_BEFORE=; SAB_AFTER=; SAB_COUNT=; SAB_FILE2=; SAB_BEFORE2=; '
        'SAB_AFTER2=; SAB_COUNT2=; . "%s"; printf "%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00%%s\\x00" '
        '"$SAB_FILE" "$SAB_BEFORE" "$SAB_AFTER" "${SAB_COUNT:-1}" "$SAB_FILE2" "$SAB_BEFORE2" '
        '"$SAB_AFTER2" "${SAB_COUNT2:-1}"' % os.path.join(sab, fn)], capture_output=True, text=True)
    v = out.stdout.split('\x00')
    for k in (0, 4):
        if len(v) < k + 4: continue
        f, b, a, c = v[k:k+4]
        if not f.startswith('memfn/src/') or os.path.basename(f) not in CHANGED or not b: continue
        st, nf = where(b, int(c or 1), orig=os.path.basename(f))
        b2, a2 = (respell(b), respell(a)) if st == 'OK*' else (b, a)
        o = 4 - k                         # the row's other site, applied with it in one file
        more = ()
        if len(v) >= o + 4 and v[o] == f and v[o+1]:
            more = ((respell(v[o+1]) if st == 'OK*' else v[o+1], v[o+2]),)
        pr = probe(nf, b2, a2, more) if COMPILE and st.startswith('OK') and a else '-'
        rows.append((fn[:-3], 'site%d' % (k // 4 + 1), st, nf or '', os.path.basename(f), pr))
report('mech', rows)

# ---- g2 plants (each runner's dialect: win/proof `\n`->newline then `\&`->&; pres keeps `\\n`)
def un_win(s): return s.replace('\\n', '\n').replace('\\&', '&')
def un_pres(s): return s.replace('\\\\n', '\x00').replace('\\n', '\n').replace('\x00', '\\n').replace('\\&', '&')
rows = []
for rf, dec in (('memfn/tests/run_g2_win.sh', un_win), ('memfn/tests/run_g2_pres.sh', un_pres),
                ('tests/memfn/run_proof.sh', un_win)):
    label = '?'
    for i, l in enumerate(open(os.path.join(rroot, rf)).read().split('\n'), 1):
        m = re.match(r"\s*([A-Za-z0-9_|-]+)\)", l)
        if m: label = m.group(1)
        m = re.search(r"echo '([A-Za-z0-9_]+\.c)@@(.*)'", l)
        if not m or m.group(1) not in CHANGED: continue
        spec = m.group(2).replace("'\"'\"'", "'")
        frm, _, to = spec.partition('@@')
        frm, to = dec(frm), dec(to)
        st, nf = where(frm, orig=m.group(1))
        f2 = respell(frm) if st == 'OK*' else frm
        rows.append([label, f'{rf}:{i}', st, nf or '', m.group(1), (f2, to)])
# a plant of several edits (one label) is probed once, its edits in the runner's order
done = {}
for r in rows:
    if not (COMPILE and r[2].startswith('OK')): continue
    key = (r[0], r[3])
    if key not in done:
        eds = [x[5] for x in rows if x[0] == r[0] and x[3] == r[3] and isinstance(x[5], tuple)]
        done[key] = probe(r[3], eds[0][0], eds[0][1], tuple(eds[1:]))
for r in rows:
    r[5] = done.get((r[0], r[3]), '-') if COMPILE and r[2].startswith('OK') else '-'
report('g2', rows)

# ---- purity rows (`old` exactly once across the family list)
rows = []
for l in open(os.path.join(root, 'tests/memfn/purity_rows.tsv')):
    if l.startswith('#') or not l.strip(): continue
    c = l.rstrip('\n').split('\t')
    if c[1] == '-': continue          # an UNREACHED row plants nothing
    st, nf = where(c[1].replace('\\n', '\n'), 1, FAMILY)
    rows.append((c[0], '-', st, nf or '', 'window.c', '-'))
report('purity', rows)

# ---- decider census rows (keyed by file and NAME's definition)
defs = {}
for f in texts:
    if not f.endswith('.c'): continue
    for k, nm, a, b, s in entities(os.path.join(A, f))[0]:
        if k != 'proto': defs.setdefault(nm, set()).add(f)
for h in ('window.h', 'kit.h'):
    if h not in texts: continue
    for k, nm, a, b, s in entities(os.path.join(A, h))[0]:
        if k not in ('proto', 'macro'): defs.setdefault(nm, set()).add(h)
rows = []
for l in open(os.path.join(root, 'tests/memfn/decider_census.tsv')):
    if l.startswith('#') or not l.strip(): continue
    c = l.rstrip('\n').split('\t')
    if c[0] not in ('window.c', 'presence.c', 'compose.c'): continue
    hs = sorted(defs.get(c[1].split(':')[0], ()))
    st = 'OK' if len(hs) == 1 else 'STALE' if not hs else 'AMBIGUOUS'
    rows.append((c[1], c[2], st, ','.join(hs), c[0], '-'))
report('census', rows)
sys.exit(1 if bad_total else 0)
