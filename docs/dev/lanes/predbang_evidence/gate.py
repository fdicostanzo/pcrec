# 2026-11-27: alone-as-middle, the reads around `[n = (P SEQ Q)]` through predfix90_model's engine. Prints; asserts nothing.
import io, contextlib
M = 'docs/dev/lanes/predfix90_evidence/predfix90_model.py'
buf = io.StringIO(); ns = {'__name__': '__main__', '__file__': M}
try:
    with contextlib.redirect_stdout(buf): exec(compile(open(M).read(), M, 'exec'), ns)
except SystemExit as e: pass
print('model last line:', buf.getvalue().strip().splitlines()[-1])
B = ['P := /(?<d>\\d)/', 'Q := /,(?<d>\\d)/']
q = ['7,3', '3,7', '1,2', '8,9', '8,9 3,7 1,2', '7,3 3,7 4,1 9,9']
def show(e, b):
    P, err = ns['run'](e, b)
    print(e, '|', '; '.join(b[2:]) or '-', '|', 'legal ' + str(ns['answers'](P, q)) if P is not None else 'refused: ' + str(err)[:230])
for e in ['[n = ([a = P] SEQ [b = Q])] & (n.d: <5)',
          '[n = ([a = P] SEQ [b = Q])] & some((n.d: <5))',
          '[n = ([a = P] SEQ [b = Q])] & all((n.d: <5))',
          '[n = (P SEQ Q)] & some((n.d: <5))',
          '[n = (P SEQ Q)] & all((n.d: <5))',
          '[n = (P SEQ Q)] & (P.d: <5) & (Q.d: <5)']:
    show(e, B)
