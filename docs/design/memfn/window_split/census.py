#!/usr/bin/env python3
# census.py SRC SPEC [-v] [--calls|--bodies]
#   SRC  : a directory holding the kit's memfn/src files at the tree under study.
#   SPEC : lines "NEWFILE <- SRCFILE RANGES" where RANGES are a,b line pairs ("78-151 231-278")
#          or "ent:NAME" (a whole top-level entity of SRCFILE). An entity belongs to the
#          NEWFILE whose range holds its FIRST line. Lines of a split SRCFILE no SPEC line names
#          stay in a file named "<SRCFILE>(rest)" (it must be empty for window.c).
# Prints, per new file: lines, entities; then every NAME DEFINED IN ONE NEW FILE AND NAMED IN
# CODE IN ANOTHER (comments, string literals and prototype lines blanked; member names after
# '.'/'->' skipped), grouped: statics that must lose `static` (the private header's functions
# and objects), types/macros/enumerators (the private header's types), already-public names
# (kit.h today). Then each new file's PUBLIC names: names other memfn/src files call; the name cost per
# boundary; the FILE CYCLES (--calls: edges from functions/tables/objects only, types go to the header;
# --bodies: edges from function bodies only, table initializers excluded). A CENSUS of code text:
# comments do not count (arch C-39's ceiling counts them, hence 25 there vs 16 here at its 2-file cut).
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ents import entities

src, spec = sys.argv[1], sys.argv[2]
verbose = '-v' in sys.argv
ID = re.compile(r'(?<![A-Za-z0-9_])(?<!\.)(?<!->)([A-Za-z_][A-Za-z0-9_]*)')

def ident_lines(L, a, b):
    out = {}
    for k in range(a, b+1):
        t = L[k-1]
        t = re.sub(r'->\s*[A-Za-z_]\w*', ' ', t)
        t = re.sub(r'\.\s*[A-Za-z_]\w*', ' ', t)
        for m in ID.finditer(t):
            out.setdefault(m.group(1), set()).add(k)
    return out

files = {}
def load(fn):
    if fn not in files:
        ents, L = entities(os.path.join(src, fn))
        files[fn] = (ents, L)
    return files[fn]

assign = []  # (newfile, srcfile, a, b) or (newfile, srcfile, 'ent', name)
for line in open(spec):
    line = line.split('#')[0].strip()
    if not line: continue
    lhs, rhs = line.split('<-')
    nf = lhs.strip(); parts = rhs.split(); sf = parts[0]; load(sf)
    for p in parts[1:]:
        if p.startswith('ent:'): assign.append((nf, sf, 'ent', p[4:]))
        else:
            a, b = p.split('-'); assign.append((nf, sf, int(a), int(b)))

def home(sf, ent):
    k, nm, a, b, s = ent
    for nf, f, x, y in assign:
        if f != sf: continue
        if x == 'ent':
            if y == nm: return nf
        elif x <= a <= y: return nf
    return None

# owner map
owner = {}   # name -> (newfile, kind, static, srcfile, a, b)
members = {} # newfile -> list of ents
split_srcs = sorted({f for _, f, _, _ in assign})
for sf in split_srcs:
    ents, L = files[sf]
    for e in ents:
        k, nm, a, b, s = e
        if k == 'proto' or nm in ('(anon)', '_Static_assert'): continue
        nf = home(sf, e)
        if nf is None:
            if sf == 'window.c' or any(f == sf and x != 'ent' for _, f, x, _ in assign):
                nf = sf + '(rest)'
            else:
                nf = sf   # an entity-picked source keeps the rest under its own name
        members.setdefault(nf, []).append(e)
        if k in ('fn', 'table', 'obj', 'inst', 'struct', 'typedef', 'macro', 'enumr', 'enum'):
            owner.setdefault(nm, (nf, k, s, sf, a, b))

# users
use = {}  # name -> {newfile: [srcfile:line,...]}
fuse = {} # name -> {newfile} where a FUNCTION BODY names it (a call or a read; table initializers excluded)
for sf in split_srcs:
    ents, L = files[sf]
    protos = set()
    for k, nm, a, b, s in ents:
        if k == 'proto': protos.update(range(a, b+1))
    for nf, es in members.items():
        for e in es:
            k, nm, a, b, s = e
            if e not in files[sf][0]: continue
            ids = ident_lines(L, a, b)
            for n, ls in ids.items():
                ls = {x for x in ls if x not in protos}
                if not ls or n not in owner: continue
                o = owner[n]
                if o[3] == sf and o[4] <= min(ls) and max(ls) <= o[5] and o[4] == a: continue
                if o[0] == nf: continue
                use.setdefault(n, {}).setdefault(nf, set()).update(f'{sf}:{x}' for x in ls)
                if k == 'fn': fuse.setdefault(n, set()).add(nf)

# other kit files as outside users (the public face)
others = sorted(f for f in os.listdir(src) if f.endswith('.c') and f not in split_srcs)
outside = {}
for f in others:
    L = open(os.path.join(src, f)).read()
    from ents import blank
    BL = blank(L).split('\n')
    ids = ident_lines(BL, 1, len(BL))
    for n, ls in ids.items():
        if n in owner and owner[n][1] in ('fn', 'table', 'obj'):
            outside.setdefault(n, {})[f] = len(ls)

def count_lines(nf):
    tot = 0
    for f, sf, x, y in assign:
        if f == nf and x != 'ent': tot += y - x + 1
        elif f == nf:
            for e in files[sf][0]:
                if e[1] == y and e[0] == 'fn': tot += e[3] - e[2] + 1
    return tot

print('== files')
for nf in sorted(members):
    es = members[nf]
    fns = [e for e in es if e[0] == 'fn']
    print(f'{nf}\tentity-lines={count_lines(nf)}\tfns={len(fns)}\tents={len(es)}')
FUNC = ('fn', 'table', 'obj', 'inst')
cross_static = sorted(n for n in use if owner[n][1] in FUNC and owner[n][2])
cross_type = sorted(n for n in use if owner[n][1] not in FUNC)
cross_pub = sorted(n for n in use if owner[n][1] in FUNC and not owner[n][2])
def show(title, names):
    print(f'== {title}: {len(names)}')
    for n in names:
        o = owner[n]
        us = ','.join(sorted(use[n]))
        extra = ''
        if verbose: extra = '\t' + ' '.join(sorted(sum((sorted(v) for v in use[n].values()), []))[:12])
        print(f'{n}\t{o[1]}\t{o[0]}\t-> {us}{extra}')
show('STATICS crossing (lose static; private header)', cross_static)
show('TYPES/MACROS/ENUMERATORS crossing (private header)', cross_type)
show('ALREADY PUBLIC (kit.h) crossing', cross_pub)
print('== PUBLIC per new file (named by other memfn/src files)')
for nf in sorted(members):
    pub = sorted(n for n in outside if owner[n][0] == nf and not owner[n][2])
    print(f'{nf}\t{len(pub)}\t' + ' '.join(f'{n}[{"+".join(sorted(outside[n]))}]' for n in pub))
print('== BOUNDARY name cost (definer -> user: names that must cross; statics+types, kit.h names excluded)')
pairs = {}
for n, us in use.items():
    o = owner[n]
    if o[1] in FUNC and not o[2]: continue
    for u in us:
        pairs.setdefault((o[0], u), []).append(n)
for (a, b), ns in sorted(pairs.items(), key=lambda kv: -len(kv[1])):
    print(f'{len(ns):3d}  {a} -> {b}: {" ".join(sorted(ns))}')
# file-level edges (user -> definer), every crossing name incl. kit.h ones, then the cycles (SCCs)
edges = {}
TYPES_TO_HEADER = '--calls' in sys.argv or '--bodies' in sys.argv
BODIES = '--bodies' in sys.argv
for n, us in use.items():
    if TYPES_TO_HEADER and owner[n][1] not in FUNC: continue
    if BODIES: us = fuse.get(n, set())
    for u in us:
        if u != owner[n][0]: edges.setdefault(u, set()).add(owner[n][0])
nodes = sorted(set(members) | {x for v in edges.values() for x in v})
idx = {}; low = {}; stack = []; on = set(); sccs = []; c = [0]
def sc(v):
    idx[v] = low[v] = c[0]; c[0] += 1; stack.append(v); on.add(v)
    for w in edges.get(v, ()):
        if w not in idx: sc(w); low[v] = min(low[v], low[w])
        elif w in on: low[v] = min(low[v], idx[w])
    if low[v] == idx[v]:
        comp = []
        while True:
            w = stack.pop(); on.discard(w); comp.append(w)
            if w == v: break
        sccs.append(comp)
sys.setrecursionlimit(10000)
for v in nodes:
    if v not in idx: sc(v)
print('== FILE CYCLES (strongly connected sets of >1 file; edges = a name used across)')
for comp in sccs:
    if len(comp) > 1:
        print(' '.join(sorted(comp)))
        for a in sorted(comp):
            for b in sorted(edges.get(a, ())):
                if b in comp:
                    ns = sorted(n for n, us in use.items() if a in (fuse.get(n, set()) if BODIES else us) and owner[n][0] == b and (not TYPES_TO_HEADER or owner[n][1] in FUNC))
                    print(f'   {a} -> {b}: {" ".join(ns)}')
