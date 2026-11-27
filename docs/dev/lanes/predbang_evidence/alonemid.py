# 2026-11-27: alone-as-middle, the reads around `[n = (P SEQ Q)]` through predfix90_model's engine. Prints; asserts nothing.
import io, contextlib
M = 'docs/dev/lanes/predfix90_evidence/predfix90_model.py'
buf = io.StringIO(); ns = {'__name__': '__main__', '__file__': M}
try:
    with contextlib.redirect_stdout(buf): exec(compile(open(M).read(), M, 'exec'), ns)
except SystemExit as e: pass
print('model last line:', buf.getvalue().strip().splitlines()[-1])
B = ['P := /(?<d>\\d)/', 'Q := /,(?<d>\\d)/']
q = ['7,3', '3,7', '3,7 7,3', '7,3 3,7 4,1']
def show(e, b):
    P, err = ns['run'](e, b)
    print(e, '|', '; '.join(b[2:]) or '-', '|', 'legal ' + str(ns['answers'](P, q)) if P is not None else 'refused: ' + str(err)[:230])
for rd in ['n.Q.d', 'Q.d', 'n.d', 'n.P.d', 'P.d']:
    show('[n = (P SEQ Q)] & (%s: <5)' % rd, B)
for rd in ['X.Q.d', 'X.d', 'X.n.Q.d', 'X.n.d']:
    show('X & (%s: <5)' % rd, B + ['X := [n = (P SEQ Q)]'])
show('[n = (Q SEQ Q)] & (Q.d: <5)', B)
