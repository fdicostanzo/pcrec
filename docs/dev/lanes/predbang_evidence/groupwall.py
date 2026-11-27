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
for e, b in [('/(?<_g>(?<d>\\d))x/ & (d: <5)', []),
             ('X & (X.d: <5)', ['X := /(?<_g>(?<d>\\d))x/']),
             ('[n = /(?<_g>(?<d>\\d))x/] & (n.d: <5)', []),
             ('[_g = /(?<d>\\d)/] SEQ /x/ & (d: <5)', []),
             ('[_g = /(?<d>\\d)/] SEQ /x/ & (_g.d: <5)', []),
             ('X & (X.d: <5)', ['X := [_g = /(?<d>\\d)/] SEQ /x/']),
             ('[n = ([_g = /(?<d>\\d)/] SEQ /x/)] & (n.d: <5)', [])]:
    print('; '.join(b) or '-', '||', end=' '); show(e, B + b)
