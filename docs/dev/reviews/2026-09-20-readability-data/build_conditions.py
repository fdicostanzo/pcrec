#!/usr/bin/env python3
"""Rebuild the naming experiment's evidence conditions from the CURRENT tree.

usage: build_conditions.py SRC_C NAMES_TSV OUTDIR [VM_STRUCT_END_MARKER]
  SRC_C      the commented source (e.g. src/gen/emit_vm.c)
  NAMES_TSV  kind<TAB>name rows (field = Vm.xxx, func, local)
  OUTDIR     writes cond_A.md (identifier + declaration/signature line) and
             cond_B.md (A + the declaration's comment / the function's header)
Method recorded in ../2026-09-20-readability-experiments.md §1. A guesser
(haiku) answers from the condition file ALONE; a grader (sonnet) scores
correct/partial/wrong/vacuous against the truth column of graded_all.tsv."""
import sys, re
src_path, names_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
marker = sys.argv[4] if len(sys.argv) > 4 else '} Vm;'
src = open(src_path, encoding='utf-8').read().split('\n')
names = [l.rstrip('\n').split('\t')[:2] for l in open(names_path) if l.strip()]
e = next(i for i, l in enumerate(src) if l.startswith(marker)) + 1
b = max(i for i in range(e) if src[i].startswith('typedef struct')) + 1
ev_b = max(i for i in range(b - 1) if 'typedef struct' in src[i])
def sc(s): return re.sub(r'/\*.*?\*/', '', s).strip()
decls = {}
for l in src[b - 1:e]:
    code = sc(l)
    if not code or code.startswith(('typedef', '}')): continue
    for m in re.finditer(r'\**([A-Za-z_][A-Za-z0-9_]*)\s*(\[[^\]]*\])*\s*(?=[;,])', code):
        decls.setdefault(m.group(1), (code, (re.findall(r'/\*.*?\*/', l) or [''])[0]))
def func_sig(name):
    for i, l in enumerate(src):
        if re.match(r'^static [^;]*\b' + re.escape(name) + r'\(', l) and not l.rstrip().endswith(';'):
            j, sig = i, l
            while not sig.rstrip().endswith(')') and j < i + 4:
                j += 1; sig = sig.rstrip() + ' ' + src[j].strip()
            return i, sc(sig.replace('{', ''))
    return None, None
def header_above(i):
    j = i - 1
    while j >= 0 and src[j].strip() == '': j -= 1
    if j >= 0 and src[j].strip().endswith('*/'):
        k = j
        while k >= 0 and '/*' not in src[k]: k -= 1
        return '\n'.join(src[k:j + 1])
    return ''
A, B = [], []
for kind, name in names:
    if kind == 'field':
        fn = name.split('.', 1)[1]
        if fn in decls: code, cm = decls[fn]
        else:
            code, cm = '(declaration not located)', ''
            for l in src[ev_b:b]:
                if re.search(r'\b' + re.escape(fn) + r'\b\s*[;,]', sc(l)):
                    code, cm = sc(l), (re.findall(r'/\*.*?\*/', l) or [''])[0]; break
        A.append((kind, name, code)); B.append((kind, name, code + ('  ' + cm if cm else '')))
    elif kind == 'func':
        i, sig = func_sig(name)
        A.append((kind, name, sig or '(signature not located)'))
        B.append((kind, name, (sig or '') + '\n' + (header_above(i) if i is not None else '')))
    else:
        m = None
        for l in src:
            c = sc(l)
            if re.search(r'[A-Za-z_\]\*] +\**' + re.escape(name) + r'\b\s*(=|,|;|\))', c) and ('(' in c or ';' in c) and not c.startswith('return'):
                m = c; break
        A.append((kind, name, m or '(no declaration line located)')); B.append((kind, name, m or ''))
for cond, rows in (('A', A), ('B', B)):
    with open(f'{out}/cond_{cond}.md', 'w') as f:
        f.write(f"# Condition {cond}: guess what each name means from ONLY the text on its row.\n\n")
        for kind, name, txt in rows: f.write(f"## {kind}\t{name}\n```c\n{txt}\n```\n\n")
print("wrote", out, "rows", len(names))
