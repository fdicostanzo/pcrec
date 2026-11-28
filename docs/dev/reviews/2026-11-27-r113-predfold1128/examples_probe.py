# Load the predfold1128 model up to its CHECKS128 marker (read-only; no file of the model is changed) and probe.
import sys, os
M = os.path.abspath('docs/dev/lanes/predfold1128_evidence/predfold1128_model.py')
src = open(M, encoding='utf-8').read()
cut = src.index('# ==== CHECKS128')
g = {'__file__': M, '__name__': 'probe128'}
exec(compile(src[:cut], M, 'exec'), g)
AH = "A := /(?<h>\\d)/"; BP = "B(rx) := /${[p = rx]}xx/"
P = [
 ('stacked over call label, from outside Y3.a.h', 'Y3 & (Y3.a.h: <5)', [AH, BP, 'Y3 := [k = [c = B([a = A])]] SEQ "!"']),
 ('stacked over call label, from outside Y3.k.a.h', 'Y3 & (Y3.k.a.h: <5)', [AH, BP, 'Y3 := [k = [c = B([a = A])]] SEQ "!"']),
 ('stacked over call label, own text k.a.h', '[k = [c = B([a = A])]] & (k.a.h: <5)', [AH, BP]),
 ('own text c.a.h', '[c = B([a = A])] & (c.a.h: <5)', [AH, BP]),
 ('group around call, own text g.a.h', '[k = (B([a = A]) SEQ "!")] & (k.a.h: <5)', [AH, BP]),
 ('from outside, group k: Y4.k.a.h', 'Y4 & (Y4.k.a.h: <5)', [AH, BP, 'Y4 := [k = (B([a = A]) SEQ "!")] SEQ ";"']),
 ('Bo with labelled body d, no remedy', 'Bo(Ad) & (Bo.d: <5)', ["Ad := /(?<d>\\d)/", "Bo(rx) := /${[q = /(?<d>\\d)/]}-${[(=) = rx]}/"]),
 ('Bo with labelled body d, remedy', 'Bo(Ad) & (Bo.d: <5)', ["Ad := /(?<d>\\d)/", "Bo(rx) := /${[q = /(?<d>\\d)/]}-${[(=, _ = d) = rx]}/"]),
]
for nm, e, b in P:
    try:
        Pg, err = g['run11'](e, b)
    except Exception as x:
        Pg, err = None, 'EXC %r' % x
    if Pg is None:
        print('%-50s REFUSED %s' % (nm, (err or '')[:200]))
    else:
        texts = ['3xx!', '7xx!'] if 'Y' in e else (['3xx', '7xx'] if 'k' in e or 'c.' in e else ['3-7', '7-3', '3-3'])
        try: a = g['ans11'](Pg, texts)
        except Exception as x: a = 'EXC %r' % x
        print('%-50s LEGAL %s' % (nm, a))
