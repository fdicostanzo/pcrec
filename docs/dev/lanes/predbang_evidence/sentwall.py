# 2026-11-27: the owner's three statements on sent-label-wall, put through predfix90_model's own engine and its
# separate path-rule evaluator (the model is executed whole first; its own output is discarded). Prints; asserts nothing.
import runpy, sys, io, contextlib
M = 'docs/dev/lanes/predfix90_evidence/predfix90_model.py'
buf = io.StringIO()
ns = {'__name__': '__main__', '__file__': M}
try:
    with contextlib.redirect_stdout(buf):
        exec(compile(open(M).read(), M, 'exec'), ns)
except SystemExit as e:
    print('model exit code', e.code)
print('model last line:', buf.getvalue().strip().splitlines()[-1])
B = ('_', '_')
cells = [('sent', (B,), ()),                       # R(l:, v) := /${[l = [_ = v]]}xx/   read x.h
         ('arg',  (B,), ()),                       # B(rx) := /${[_ = rx]}xx/           B([a = A]) & (a.h: <5)
         ('arg',  (('P', 'n'), B), ())]            # the caller's label under a public label and a blank
for kind, layers, steps, want, why, e, b, rx, got, err, diff in ns['g_run'](cells):
    print(f'{kind:5} | {e} | {"; ".join(b)}\n      rules say: {want} {why} | engine: {got} {err or ""} | answers against /{rx}/: {diff}')
# the reversed order: the wall above the sent label (the documents' printed line)
P, err = ns['run']('R(x:, A) & (x.h: <5)', [ns['A_H'], 'R(l:, v) := /${[_ = [l = v]]}xx/'])
q = ['3xx', '7xx', '7xx 3xx', '3xx 7xx 4xx']
print('reversed | R(l:, v) := /${[_ = [l = v]]}xx/ | engine:', 'legal' if P is not None else 'refused ' + err,
      '| answers', ns['answers'](P, q) if P is not None else '')
# a non-label parameter used as a label: R(l, v) with no mark
P, err = ns['run']('R(x, A) & (x.h: <5)', [ns['A_H'], 'R(l, v) := /${[l = v]}xx/'])
print('unmarked | R(l, v) := /${[l = v]}xx/ called R(x, A) | engine:', 'legal' if P is not None else 'refused: ' + str(err)[:200])
P, err = ns['run']('R(x, A) & (R.l.h: <5)', [ns['A_H'], 'R(l, v) := /${[l = v]}xx/'])
print('unmarked, read as the body wrote it | (R.l.h: <5) | engine:', 'legal, answers ' + str(ns['answers'](P, q)) if P is not None else 'refused: ' + str(err)[:200])
