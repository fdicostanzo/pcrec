# 2026-11-27: alone-as-middle, the reads around `[n = (P SEQ Q)]` through predfix90_model's engine. Prints; asserts nothing.
import io, contextlib
M = 'docs/dev/lanes/predfix90_evidence/predfix90_model.py'
buf = io.StringIO(); ns = {'__name__': '__main__', '__file__': M}
try:
    with contextlib.redirect_stdout(buf): exec(compile(open(M).read(), M, 'exec'), ns)
except SystemExit as e: pass
print('model last line:', buf.getvalue().strip().splitlines()[-1])
B = ['A := /(?<h>\\d)/', 'A2 := /(?<h>\\d)/']
q = ['3x', '7x', '7x 3x', '3x 7x 4x']
def show(e, b=B):
    P, err = ns['run'](e, b)
    print(e, '|', 'legal ' + str(ns['answers'](P, q)) if P is not None else 'refused: ' + str(err)[:230])
for e in ['/(?<g>(?<d>\\d))x/ & (g.d: <5)', '/(?<g>(?<d>\\d))x/ & (d: <5)', '/(?<g>(?<d>\\d))x/ & (g: <5)',
          '/(?<g>${A})x/ & (g.h: <5)', '/(?<g>${A})x/ & (A.h: <5)', '/(?<g>${A})x/ & (h: <5)', '/(?<g>${A})x/ & (g: <5)',
          '/(?<g>${[a = A]})x/ & (g.a.h: <5)', '/(?<g>${[a = A]})x/ & (a.h: <5)',
          '[g = A] SEQ /x/ & (g.h: <5)',
          'X & (X.g.h: <5)', 'X & (X.h: <5)']:
    show(e, B + ['X := /(?<g>${[a = A]})x/'])
