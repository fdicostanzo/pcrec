#!/usr/bin/env python3
# assemble.py ROOT OUT [--pure] : the CUT ASSEMBLER of window_split.md rev 2 (r95 lesson 1).
#   ROOT : a pcrec tree at the design's T (reads ROOT/memfn/src and ROOT/memfn/include only).
#   OUT  : a scratch directory (never memfn/src): OUT/memfn/src and OUT/memfn/include are
#          written there as the tree would read AT THE UNIT'S TIP, window.c removed.
# Reads, beside this file: cut.spec (which lines go where), files.spec (each new file's title,
# provenance line and window.h's head comment), window_h.in (the private header as
# written, with its @TYPES@ and @DECLS@ slots) and edits.spec (renames and FROM/TO edits: the
# accessors, H3's names, O3's predicates, U2b's re-spellings, the kit.h lines that move).
# Rules it applies (window_split.md §3-§5, stated there; nothing here is a choice of its own):
#   R1 every window.c line goes to exactly one file (a `window.h <-` item wins over a file
#      range; any other overlap, or a line no item names, is an error);
#   R2 an `ent:NAME` item takes the entity WITH the comment block ending on the line above it;
#   R3 an `export` name loses `static` at its definition and gets `#define N MF_NS(N)` plus a
#      declaration in window.h's @DECLS@ (a function's head up to its body, an object's
#      declarator up to its initializer, `extern`), grouped by defining file; `export N = TEXT`
#      gives the declaration text explicitly (an object whose bound a `sizeof` reader needs);
#      `@new FILE NAME = TEXT` declares an accessor the edits write in FILE (not in window.c);
#   R4 a static forward declaration of an exported name is deleted; of a non-exported name it
#      goes to its definition's file (kept in place if it already lands there, else right after
#      that file's prologue); a forward declaration naming nothing defined is an error;
#   R5 each new .c gets a prologue (SPDX, Provenance, its title line, window.c's includes,
#      `window.h` for family files); window.h gets the family comment (cut.spec `head`);
#   R6 `rename OLD NEW` renames OLD as a CODE token (comments and strings untouched, member
#      names after `.`/`->` untouched) in every file the assembler writes or edits;
#   R7 each FROM of edits.spec must occur EXACTLY ONCE in its file, after R1-R6.
# Prints one line per written file (lines, exports) and exits 1 on any rule violation.
import os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ents import entities, blank

PURE = '--pure' in sys.argv     # the cut alone: no edits.spec, no @new (tables.py's T end, W36)
argv = [a for a in sys.argv[1:] if a != '--pure']
root, out = argv[0], argv[1]
SRC = os.path.join(root, 'memfn/src')
errs = []
def err(m): errs.append(m)

def read_lines(p): return open(p).read().split('\n')
SRCS = {}            # every source file cut.spec names: (lines, entities)
for raw in open(os.path.join(HERE, 'cut.spec')):
    l = raw.split('#')[0]
    if '<-' in l:
        sf = l.split('<-')[1].split()[0]
        if sf not in SRCS:
            SRCS[sf] = (read_lines(os.path.join(SRC, sf)), entities(os.path.join(SRC, sf))[0])
W, WENTS = SRCS['window.c']

def ent_span(sf, name):
    L, E = SRCS[sf]
    for k, nm, a, b, s in E:
        if nm == name and k != 'proto':
            # R2: the comment block that ends on the line above
            t = a - 1
            if t >= 1 and L[t-1].rstrip().endswith('*/'):
                while t >= 1 and '/*' not in L[t-1]: t -= 1
                return t, b
            return a, b
    err(f'ent:{name}: no entity in {sf}'); return None

# ---- cut.spec
items = []          # (newfile, srcfile, a, b)
titles, provs, heads = {}, {}, {}
order = []
for raw in open(os.path.join(HERE, 'files.spec')).readlines() + open(os.path.join(HERE, 'cut.spec')).readlines():
    line = raw.rstrip('\n')
    if not line.strip() or line.lstrip().startswith('#'): continue
    if line.startswith('title '):
        _, nf, txt = line.split(None, 2); titles[nf] = txt; continue
    if line.startswith('prov '):
        _, nf, txt = line.split(None, 2); provs[nf] = txt; continue
    if line.startswith('head '):
        _, nf, sf, rg = line.split(); a, b = map(int, rg.split('-')); heads[nf] = (sf, a, b); continue
    lhs, rhs = line.split('<-')
    nf = lhs.strip(); parts = rhs.split('#')[0].split(); sf = parts[0]
    if nf not in order: order.append(nf)
    for p in parts[1:]:
        if p.startswith('ent:'):
            sp = ent_span(sf, p[4:])
            if sp: items.append((nf, sf, sp[0], sp[1]))
        else:
            a, b = map(int, p.split('-')); items.append((nf, sf, a, b))

# R1: per source line, its file
home = {}
for sf in SRCS:
    L = SRCS[sf][0]
    n = len(L) - (1 if L and L[-1] == '' else 0)
    hl = {}
    for nf, f, a, b in items:
        if f != sf: continue
        for k in range(a, b+1):
            if k > n: err(f'{nf}: {sf}:{k} beyond EOF'); break
            if nf == 'window.h':
                if hl.get(k, 'window.h') != 'window.h': err(f'{sf}:{k} twice in window.h')
                hl[k] = 'window.h'
    fl = {}
    for nf, f, a, b in items:
        if f != sf or nf == 'window.h': continue
        for k in range(a, b+1):
            if k in hl: continue
            if k in fl: err(f'{sf}:{k} in {fl[k]} and {nf}')
            fl[k] = nf
    for k in range(1, n+1):
        h = hl.get(k) or fl.get(k)
        if h is None:
            if sf == 'window.c': err(f'window.c:{k} homed nowhere')
            else: h = sf
        home[(sf, k)] = h
    for k in range(1, n+1):
        pass
for nf, (sf, a, b) in heads.items():
    for k in range(a, b+1):
        if home.get((sf, k)) != nf: err(f'head {nf}: {sf}:{k} is homed in {home.get((sf,k))}')

# ---- window_h.in: exports
exports, explicit = [], {}
hdr_text = open(os.path.join(HERE, 'window_h.in')).read()
for m in re.finditer(r'^@export\s+(\w+)(?:\s*=\s*(.+))?$', hdr_text, re.M):
    exports.append(m.group(1))
    if m.group(2): explicit[m.group(1)] = m.group(2).strip()
news = re.findall(r'^@new\s+(\S+)\s+(\w+)\s*=\s*(.+)$', hdr_text, re.M)
hdr_text = re.sub(r'^@(export|new)\b.*\n', '', hdr_text, flags=re.M)

def defn(name):
    for sf, (L, E) in SRCS.items():
        for k, nm, a, b, s in E:
            if nm == name and k in ('fn', 'table', 'obj', 'inst'): return sf, k, a, b
    return None

edit_lines = {}     # (sf, line) -> replacement text (static stripped)
decls = {}          # defining newfile -> [decl text]
for nm in exports:
    d = defn(nm)
    if not d: err(f'export {nm}: no definition'); continue
    sf, kind, a, b = d
    L = SRCS[sf][0]
    first = L[a-1]
    if not first.startswith('static '): err(f'export {nm}: {sf}:{a} is not static'); continue
    edit_lines[(sf, a)] = first[len('static '):]
    nf = home[(sf, a)]
    if nm in explicit: dt = explicit[nm]
    else:
        text = '\n'.join(L[a-1:b]); bl = blank(text)
        if kind == 'fn':
            depth = 0; cut = None
            for i, c in enumerate(bl):
                if c == '(': depth += 1
                elif c == ')': depth -= 1
                elif c == '{' and depth == 0: cut = i; break
            dt = text[:cut].rstrip()[len('static '):] + ';'
        else:
            depth = 0; cut = None
            for i, c in enumerate(bl):
                if c in '([': depth += 1
                elif c in ')]': depth -= 1
                elif c == '=' and depth == 0: cut = i; break
            if cut is None: err(f'export {nm}: no initializer'); continue
            dt = 'extern ' + text[:cut].rstrip()[len('static '):] + ';'
    decls.setdefault(nf, []).append((nm, dt))

for nf, nm, dt in ([] if PURE else news):          # an accessor edits.spec writes (no window.c definition)
    decls.setdefault(nf, []).append((nm, dt.strip())); exports.append(nm)

# R4: static forward declarations
proto_moves = {}    # newfile -> [text]
drop = set()
for k, nm, a, b, s in WENTS:
    if k != 'proto' or nm == '_Static_assert': continue
    text = '\n'.join(W[a-1:b])
    names = re.findall(r'\b(\w+)\s*(?:\(|,|;)', blank(text).split('(')[0] + ';') if '(' not in blank(text) else [nm]
    if '(' not in blank(text):     # an object forward declaration: every declarator
        body = re.sub(r'^\s*static\s+const\s+\w+\s+', '', blank(text)).rstrip(' ;\n')
        names = [x.strip() for x in body.split(',')]
    ex = [x for x in names if x in exports]
    if ex:
        if len(ex) != len(names): err(f'proto {names}: mixed exported and not')
        for k2 in range(a, b+1): drop.add(('window.c', k2))
        continue
    d = defn(nm)
    if not d: err(f'proto {nm}: nothing defined'); continue
    dfile = home[(d[0], d[2])]
    if home[('window.c', a)] == dfile: continue
    for k2 in range(a, b+1): drop.add(('window.c', k2))
    proto_moves.setdefault(dfile, []).append(text)

# ---- assemble each file's body (source order of its lines)
bodies = {}
for sf in SRCS:
    L = SRCS[sf][0]
    n = len(L) - (1 if L and L[-1] == '' else 0)
    for k in range(1, n+1):
        h = home[(sf, k)]
        if (sf, k) in drop: continue
        if h in heads and heads[h][0] == sf and heads[h][1] <= k <= heads[h][2]: continue
        bodies.setdefault(h, []).append(edit_lines.get((sf, k), L[k-1]))

INCL = ['#include <stddef.h>', '#include <stdio.h>', '#include <stdlib.h>', '#include <string.h>', '']
def prologue(nf):
    pv = provs.get(nf, 'original pcrec-memory-functions text (memfn/PROVENANCE.md).')
    t = titles.get(nf, '')
    lines = ['/* SPDX-License-Identifier: 0BSD', ' * Provenance: ' + pv, ' *',
             f' * memfn/src/{nf} — {t}', ' */'] + INCL + ['#include "kit.h"']
    if nf.startswith('window_'): lines.append('#include "window.h"')
    lines.append('')
    for p in proto_moves.get(nf, []): lines.append(p)
    if proto_moves.get(nf): lines.append('')
    return lines

files = {}
for nf in order:
    if nf in ('window.h', '-') or nf in SRCS: continue
    files[nf] = '\n'.join(prologue(nf) + bodies.get(nf, [])).rstrip('\n') + '\n'
for sf in SRCS:                  # a cut source's rest keeps its name (window.c's must be empty)
    if sf != 'window.c': files[sf] = '\n'.join(bodies[sf]).rstrip('\n') + '\n'
if bodies.get('window.c'): err('window.c keeps lines')

# window.h
hb = bodies.get('window.h', [])
dl = []
for nf in order:
    if nf not in decls: continue
    dl.append(f'/* {nf} */')
    for nm, dt in decls[nf]:
        dl.append(f'#define {nm} MF_NS({nm})')
    for nm, dt in decls[nf]: dl.append(dt)
    dl.append('')
hs, ha, hb2 = heads.get('window.h', ('window.c', 1, 0))
headtxt = '\n'.join(W[ha-1:hb2]) if hb2 else ''
hdr = hdr_text.replace('@HEAD@', headtxt).replace('@TYPES@', '\n'.join(hb).strip('\n')) \
              .replace('@DECLS@', '\n'.join(dl).rstrip('\n'))
files['window.h'] = hdr

# ---- edits.spec: renames (R6) then FROM/TO edits (R7)
others = {}
def get(fn):
    if fn in files: return files[fn]
    if fn not in others:
        p = os.path.join(SRC, fn) if not fn.startswith('include/') else os.path.join(root, 'memfn', fn)
        others[fn] = open(p).read()
    return others[fn]
def put(fn, t):
    if fn in files: files[fn] = t
    else: others[fn] = t

spec = '' if PURE else open(os.path.join(HERE, 'edits.spec')).read()
renames = re.findall(r'^rename\s+(\w+)\s+(\w+)\s+in\s+(.+)$', spec, re.M)
def rename_code(t, old, new):
    bl = blank(t); outp = []; last = 0
    for m in re.finditer(r'(?<![\w.])' + re.escape(old) + r'(?!\w)', bl):
        pre = bl[max(0, m.start()-3):m.start()].rstrip()
        if pre.endswith('->') or pre.endswith('.'): continue
        outp.append(t[last:m.start()]); outp.append(new); last = m.end()
    outp.append(t[last:]); return ''.join(outp)
for old, new, where in renames:
    fl = where.split()
    if fl == ['family']: fl = [f for f in files if f.startswith('window') or f.startswith('kit_')]
    for fn in fl: put(fn, rename_code(get(fn), old, new))

blocks = re.findall(r'^@@ (\S+)[^\n]*\n<<<\n(.*?)\n===\n(.*?)\n?>>>$', spec, re.M | re.S)
for fn, frm, to in blocks:
    t = get(fn); c = t.count(frm)
    if c != 1: err(f'edit in {fn}: FROM found {c} times: {frm.splitlines()[0][:70]!r}'); continue
    put(fn, t.replace(frm, to))

# ---- write
if errs:
    for e in errs: print('ERROR', e)
    sys.exit(1)
osrc = os.path.join(out, 'memfn/src'); oinc = os.path.join(out, 'memfn/include')
if os.path.realpath(osrc).startswith(os.path.realpath(SRC)): sys.exit('refusing to write into memfn/src')
shutil.rmtree(os.path.join(out, 'memfn'), ignore_errors=True)
shutil.copytree(SRC, osrc); shutil.copytree(os.path.join(root, 'memfn/include'), oinc)
os.remove(os.path.join(osrc, 'window.c'))
for fn, t in list(files.items()) + list(others.items()):
    p = os.path.join(out, 'memfn', fn) if fn.startswith('include/') else os.path.join(osrc, fn)
    open(p, 'w').write(t)
for fn in sorted(files):
    ex = [nm for nm, _ in decls.get(fn, [])]
    print(f'{fn}\tlines={files[fn].count(chr(10))}\texports={len(ex)}\t{" ".join(ex)}')
for fn in sorted(others): print(f'{fn}\tedited')
